#!/usr/bin/env python3
"""
Zero-Loss SQLite Database Merger and Sync Engine
Merges local SQLite application entries and IMAP email receipts cleanly
into the latest upstream database without binary overwrites or race condition data loss.
"""

import os
import sys
import shutil
import sqlite3
import subprocess

DB_PATH = "verified_job_applications.db"
BACKUP_PATH = "/tmp/worker_local_backup.db"

def backup_local_db():
    if os.path.exists(DB_PATH):
        shutil.copy2(DB_PATH, BACKUP_PATH)
        print(f"[+] Backed up local database to {BACKUP_PATH}")

def merge_local_into_current():
    if not os.path.exists(BACKUP_PATH):
        print("[-] No backup database found at", BACKUP_PATH)
        return

    if not os.path.exists(DB_PATH):
        shutil.copy2(BACKUP_PATH, DB_PATH)
        print(f"[+] Restored database from {BACKUP_PATH}")
        return

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Ensure target table exists
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS verified_applications (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            company TEXT NOT NULL,
            role TEXT NOT NULL,
            portal_type TEXT NOT NULL,
            job_url TEXT NOT NULL UNIQUE,
            salary TEXT,
            status TEXT NOT NULL,
            proof_screenshot TEXT,
            notes TEXT,
            applied_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            application_type TEXT DEFAULT 'JOB',
            stipend_usd REAL DEFAULT 0,
            email_verified INTEGER DEFAULT 0,
            email_subject TEXT,
            email_sender TEXT,
            email_received_at TIMESTAMP,
            compatibility_score INTEGER DEFAULT 80,
            critique_analysis TEXT
        )
    """)
    conn.commit()

    # Attach backup
    cursor.execute(f"ATTACH DATABASE '{BACKUP_PATH}' AS backup_db")

    # 1. Insert new applications from backup not yet in current DB
    cursor.execute("""
        INSERT OR IGNORE INTO verified_applications 
        (company, role, portal_type, job_url, salary, status, proof_screenshot, notes, applied_at, application_type, stipend_usd, email_verified, email_subject, email_sender, email_received_at, compatibility_score, critique_analysis)
        SELECT company, role, portal_type, job_url, salary, status, proof_screenshot, notes, applied_at, application_type, stipend_usd, email_verified, email_subject, email_sender, email_received_at, compatibility_score, critique_analysis
        FROM backup_db.verified_applications
        WHERE job_url NOT IN (SELECT job_url FROM verified_applications)
    """)
    inserted_apps = cursor.rowcount

    # 2. Update email verification receipts from backup where current is unverified
    cursor.execute("""
        UPDATE verified_applications
        SET email_verified = 1,
            email_subject = (SELECT b.email_subject FROM backup_db.verified_applications b WHERE b.job_url = verified_applications.job_url),
            email_sender = (SELECT b.email_sender FROM backup_db.verified_applications b WHERE b.job_url = verified_applications.job_url),
            email_received_at = (SELECT b.email_received_at FROM backup_db.verified_applications b WHERE b.job_url = verified_applications.job_url)
        WHERE email_verified = 0 
          AND job_url IN (SELECT b.job_url FROM backup_db.verified_applications b WHERE b.email_verified = 1)
    """)
    updated_receipts = cursor.rowcount

    conn.commit()

    # 3. Post-merge deduplication and blacklist enforcement
    try:
        from run_unified_verified_engine import clean_norm_url, clean_norm_company, clean_norm_role, get_role_tokens
        # Enforce blacklist
        cursor.execute("SELECT company FROM company_blacklist")
        bl_set = {clean_norm_company(r[0]) for r in cursor.fetchall()}
        cursor.execute("SELECT company FROM verified_applications WHERE status='REJECTED_BY_COMPANY'")
        for r in cursor.fetchall():
            bl_set.add(clean_norm_company(r[0]))
        
        cursor.execute("SELECT id, company, role, job_url, status FROM verified_applications ORDER BY id ASC")
        all_apps = cursor.fetchall()
        
        seen_urls = {}
        seen_cr = {}
        seen_int = {}
        seen_jb = {}

        for rid, comp, role, url, status in all_apps:
            ck = clean_norm_company(comp)
            rk = clean_norm_role(role)
            nu = clean_norm_url(url)
            is_intern = 'intern' in rk or 'coop' in rk or 'placement' in rk

            if status != 'CONFIRMED_SUBMITTED':
                if nu and 'job_app' not in nu and len(nu.split('/')) > 4 and nu not in seen_urls: seen_urls[nu] = rid
                if ck and rk and (ck, rk) not in seen_cr: seen_cr[(ck, rk)] = rid
                if is_intern and ck and ck not in seen_int: seen_int[ck] = rid
                elif not is_intern and ck:
                    if ck not in seen_jb: seen_jb[ck] = []
                    seen_jb[ck].append((rid, get_role_tokens(role)))
                continue

            # Active CONFIRMED_SUBMITTED checks
            if ck in bl_set or any(b == ck for b in bl_set):
                cursor.execute("UPDATE verified_applications SET status='REJECTED_BY_COMPANY', notes='Company on rejection blacklist' WHERE id=?", (rid,))
                continue

            if nu and 'job_app' not in nu and len(nu.split('/')) > 4 and nu in seen_urls:
                cursor.execute("UPDATE verified_applications SET status='DUPLICATE_PURGED', notes='Normalized URL duplicate' WHERE id=?", (rid,))
                continue
            elif nu:
                seen_urls[nu] = rid

            if ck and rk and (ck, rk) in seen_cr:
                cursor.execute("UPDATE verified_applications SET status='DUPLICATE_PURGED', notes='Normalized (company, role) duplicate' WHERE id=?", (rid,))
                continue
            elif ck and rk:
                seen_cr[(ck, rk)] = rid

            if is_intern and ck:
                if ck in seen_int:
                    cursor.execute("UPDATE verified_applications SET status='DUPLICATE_PURGED', notes='Repeat internship at same company' WHERE id=?", (rid,))
                    continue
                else:
                    seen_int[ck] = rid

            if not is_intern and ck:
                rt = get_role_tokens(role)
                is_fuzzy = False
                if ck in seen_jb:
                    for prev_id, prev_tokens in seen_jb[ck]:
                        if rt and prev_tokens:
                            overlap = len(rt.intersection(prev_tokens))
                            denom = max(len(rt), len(prev_tokens))
                            if rt == prev_tokens or (denom > 0 and overlap / denom >= 0.75):
                                cursor.execute("UPDATE verified_applications SET status='DUPLICATE_PURGED', notes='Fuzzy role duplicate at same company' WHERE id=?", (rid,))
                                is_fuzzy = True
                                break
                if is_fuzzy:
                    continue
                if ck not in seen_jb: seen_jb[ck] = []
                seen_jb[ck].append((rid, rt))

        conn.commit()
    except Exception as e:
        print("[-] Post-merge dedup check skipped:", e)

    conn.close()

    print(f"[+] Merged SQLite delta: {inserted_apps} new applications inserted, {updated_receipts} email receipts updated.")

if __name__ == "__main__":
    action = sys.argv[1] if len(sys.argv) > 1 else "merge"
    if action == "backup":
        backup_local_db()
    elif action == "merge":
        merge_local_into_current()
    else:
        print(f"Unknown action: {action}")
