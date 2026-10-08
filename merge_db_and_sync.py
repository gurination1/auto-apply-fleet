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
