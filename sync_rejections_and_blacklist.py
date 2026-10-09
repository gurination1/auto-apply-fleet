#!/usr/bin/env python3
"""
Continuous Rejection & Blacklist Sync Engine
Scans Gmail IMAP for candidate rejection emails, identifies companies,
adds them to company_blacklist table in verified_job_applications.db,
and updates verified_applications to mark them REJECTED_BY_COMPANY.
Prevents repeat applications to any company that rejected the candidate.
"""

import sqlite3
import imaplib
import email
import re
import os
from email.header import decode_header
from datetime import datetime

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, 'verified_job_applications.db')

def normalize(text):
    text = re.sub(r'[^a-zA-Z0-9\s]', ' ', text or '').lower()
    return ' '.join(text.split())

def init_blacklist_table(conn):
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS company_blacklist (
        company TEXT PRIMARY KEY,
        reason TEXT,
        created_at DATETIME
    )''')
    conn.commit()

def sync_rejections():
    conn = sqlite3.connect(DB_PATH)
    init_blacklist_table(conn)
    c = conn.cursor()

    mail = imaplib.IMAP4_SSL('imap.gmail.com')
    pwd = os.environ.get('GMAIL_APP_PASSWORD')
    if not pwd and os.path.exists('/root/local_env.sh'):
        try:
            with open('/root/local_env.sh') as f:
                for line in f:
                    if 'GMAIL_APP_PASSWORD=' in line and not '_ACC_' in line:
                        pwd = line.split('=', 1)[1].strip().strip('"').strip("'")
                        break
        except Exception:
            pass

    if not pwd:
        print("[!] No GMAIL_APP_PASSWORD found")
        return

    mail.login('gurination1@gmail.com', pwd)
    mail.select('inbox')

    # Queries for rejections
    queries = [
        '(SINCE "01-Sep-2026" (TEXT "unfortunately"))',
        '(SINCE "01-Sep-2026" (TEXT "not moving forward"))',
        '(SINCE "01-Sep-2026" (TEXT "other candidates"))',
        '(SINCE "01-Sep-2026" (TEXT "at this time we have decided"))',
        '(SINCE "01-Sep-2026" (OR (SUBJECT "application status") (SUBJECT "update on your application")))',
        '(SINCE "01-Sep-2026" (SUBJECT "update regarding your application"))'
    ]

    all_mids = set()
    for q in queries:
        try:
            status, mids = mail.search(None, q)
            if mids and mids[0]:
                for mid in mids[0].split():
                    all_mids.add(mid)
        except Exception as e:
            print(f"[!] IMAP query failed for {q}: {e}")

    id_list = list(all_mids)
    print(f"[*] Found {len(id_list)} candidate rejection messages in Gmail inbox.")

    # Fetch headers in batches of 50
    rejections = []
    for i in range(0, len(id_list), 50):
        chunk = id_list[i:i+50]
        id_str = b','.join(chunk).decode('ascii')
        status, data = mail.fetch(id_str, '(BODY.PEEK[HEADER.FIELDS (SUBJECT FROM DATE)])')
        for item in data:
            if isinstance(item, tuple):
                msg = email.message_from_bytes(item[1])
                subj_val = msg.get('Subject', '')
                dec_subj = ''
                for part, enc in decode_header(subj_val):
                    if isinstance(part, bytes):
                        dec_subj += part.decode(enc or 'utf-8', errors='ignore')
                    else:
                        dec_subj += str(part)
                from_val = msg.get('From', '')
                date_val = msg.get('Date', '')
                
                s_low = dec_subj.lower()
                f_low = from_val.lower()

                # Filter out spam / non-job items
                if any(x in s_low for x in ['lens', 'invalid', 'security alert', 'verify', 'billing', 'invoice', 'newsletter', 'digest']):
                    continue

                rejections.append({
                    'subject': dec_subj,
                    'from': from_val,
                    'date': date_val
                })

    mail.close()
    mail.logout()

    print(f"[*] Parsed {len(rejections)} candidate rejection headers.")

    # Match against companies in verified_applications
    c.execute("SELECT DISTINCT company FROM verified_applications")
    db_companies = [r[0] for r in c.fetchall() if r[0]]

    # Extra known companies from email inspection
    known_seed_blacklist = [
        ('resend', 'Formal rejection email received'),
        ('runpod', 'Formal rejection email received'),
        ('railway', 'Formal rejection email received'),
        ('lean techniques', 'Formal rejection email received'),
        ('constellation space', 'Formal rejection email received'),
        ('phonic', 'Formal rejection email received'),
        ('graymatter robotics', 'Formal rejection email received'),
        ('intersystems', 'Formal rejection email received'),
        ('clickhouse', 'C++ core rejection'),
        ('reflect orbital', 'Flight software / aerospace rejection update'),
        ('lovable', 'Formal rejection email received'),
        ('bland ai', 'Formal rejection email received'),
        ('cohere', 'Formal rejection email received'),
        ('affirm', 'Formal rejection email received'),
        ('brave', 'Formal rejection email received'),
        ('ambrook', 'Formal rejection email received'),
        ('gitlab', 'Formal rejection email received'),
        ('businessolver', 'Location US-only rejection'),
        ('virtu', 'Formal rejection email received'),
        ('clera', 'Formal rejection email received'),
        ('workshop', 'Formal rejection email received'),
        ('vanta', 'Formal rejection email received'),
        ('ziprecruiter', 'Formal rejection email received'),
        ('roboflow', 'Formal rejection email received'),
        ('vital lyfe', 'Formal rejection email received'),
        ('elevenlabs', 'Formal rejection email received'),
        ('lightmatter', 'Formal rejection email received'),
        ('doordash', 'Formal rejection email received')
    ]

    for comp, rsn in known_seed_blacklist:
        c.execute("INSERT OR REPLACE INTO company_blacklist (company, reason, created_at) VALUES (?, ?, ?)",
                  (comp.strip().lower(), rsn, datetime.now().strftime('%Y-%m-%d %H:%M:%S')))

    new_blacklisted = 0
    now_str = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    for rej in rejections:
        s_norm = normalize(rej['subject'])
        f_norm = normalize(rej['from'])
        
        # Check against DB companies
        for comp in db_companies:
            comp_norm = normalize(comp)
            if not comp_norm or len(comp_norm) < 3:
                continue
            
            # Words in company name (exclude generic suffixes)
            words = [w for w in comp_norm.split() if w not in {'inc', 'llc', 'labs', 'technologies', 'technology', 'systems', 'platform', 'ai', 'corp'}]
            if not words:
                words = [comp_norm]
                
            matched = False
            if comp_norm in s_norm or comp_norm in f_norm:
                matched = True
            elif all(w in s_norm or w in f_norm for w in words if len(w) > 3):
                matched = True
                
            if matched:
                c.execute("INSERT OR REPLACE INTO company_blacklist (company, reason, created_at) VALUES (?, ?, ?)",
                          (comp_norm, f"Rejection email: {rej['subject'][:100]}", now_str))
                # Update DB application status
                c.execute("""
                    UPDATE verified_applications 
                    SET status = 'REJECTED_BY_COMPANY' 
                    WHERE lower(company) LIKE ? AND status = 'CONFIRMED_SUBMITTED'
                """, (f"%{comp}%",))
                new_blacklisted += 1

    conn.commit()

    c.execute("SELECT count(*) FROM company_blacklist")
    total_bl = c.fetchone()[0]

    c.execute("SELECT count(*) FROM verified_applications WHERE status = 'REJECTED_BY_COMPANY'")
    total_rej = c.fetchone()[0]

    conn.close()

    print(f"[✓] Rejection sync complete! Total blacklisted companies: {total_bl}. Applications marked REJECTED_BY_COMPANY: {total_rej}")

if __name__ == '__main__':
    sync_rejections()
