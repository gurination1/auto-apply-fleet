#!/usr/bin/env python3
"""
Continuous Live Email Receipt Sync Engine
Scans Gmail IMAP for confirmation receipts and links them to verified_applications in SQLite.
"""

import sqlite3
import imaplib
import email
import re
from email.header import decode_header

import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, 'verified_job_applications.db')

def normalize(text):
    text = re.sub(r'[^a-zA-Z0-9\s]', ' ', text or '').lower()
    return ' '.join(text.split())

def sync_receipts():
    try:
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
        mail.login('gurination1@gmail.com', pwd or '')
        mail.select('inbox')

        status, m1 = mail.search(None, '(SINCE "01-Oct-2026" (OR (FROM "ashbyhq.com") (FROM "greenhouse-mail.io")))')
        status, m2 = mail.search(None, '(SINCE "01-Oct-2026" (OR (SUBJECT "application") (SUBJECT "applying")))')
        status, m3 = mail.search(None, '(SINCE "01-Oct-2026" (OR (SUBJECT "thank you") (SUBJECT "thanks")))')

        all_mids = set((m1[0] or b'').split() + (m2[0] or b'').split() + (m3[0] or b'').split())
        id_list = list(all_mids)

        receipts = []
        for i in range(0, len(id_list), 50):
            chunk = id_list[i:i+50]
            id_str = b','.join(chunk).decode('ascii')
            status, data = mail.fetch(id_str, '(BODY.PEEK[HEADER.FIELDS (SUBJECT FROM DATE)])')
            for item in data:
                if isinstance(item, tuple):
                    msg = email.message_from_bytes(item[1])
                    subj_val = msg.get('Subject', '')
                    decoded_subj = ''
                    for part, enc in decode_header(subj_val):
                        if isinstance(part, bytes):
                            decoded_subj += part.decode(enc or 'utf-8', errors='ignore')
                        else:
                            decoded_subj += str(part)
                    from_val = msg.get('From', '')
                    date_val = msg.get('Date', '')
                    s_low = decoded_subj.lower()
                    if 'security code' not in s_low and 'withdrawn' not in s_low and 'explained' not in s_low and 'admissions' not in s_low:
                        if any(k in s_low for k in ['thank', 'thanks', 'applying', 'application', 'received', 'submission']) or any(k in from_val.lower() for k in ['ashbyhq', 'greenhouse', 'lever.co', 'haizelabs']):
                            receipts.append({
                                'subject': decoded_subj,
                                'from': from_val,
                                'date': date_val
                            })

        mail.close()
        mail.logout()

        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute("SELECT id, company, role, status, email_verified, application_type FROM verified_applications WHERE status = 'CONFIRMED_SUBMITTED'")
        apps = c.fetchall()

        c.execute("SELECT id FROM verified_applications WHERE email_verified = 1")
        assigned_app_ids = set(r[0] for r in c.fetchall())
        matched_new = 0

        for r in receipts:
            subj = r['subject']
            s_norm = normalize(subj)
            f_norm = normalize(r['from'])
            
            candidate_app_id = None
            for app_id, company, role, status, email_verified, app_type in apps:
                if app_id in assigned_app_ids:
                    continue
                c_norm = normalize(company)
                generic_terms = {
                    'the', 'inc', 'labs', 'company', 'technologies', 'technology', 'intelligence', 
                    'physical', 'systems', 'platform', 'group', 'services', 'software', 'engineering',
                    'solutions', 'robotics', 'capital', 'global', 'analytics', 'digital', 'media',
                    'interactive', 'studio', 'studios', 'foundation', 'enterprises', 'ai', 'llc', 'corp'
                }
                c_words = [w for w in c_norm.split() if len(w) > 3 and w not in generic_terms]
                
                matches_comp = False
                if c_norm in s_norm or c_norm in f_norm:
                    matches_comp = True
                elif c_words and any(w in s_norm or w in f_norm for w in c_words):
                    matches_comp = True
                    
                if matches_comp:
                    candidate_app_id = app_id
                    r_words = [w for w in normalize(role).split() if len(w) > 3 and w not in ['engineer', 'developer', 'software', 'senior', 'intern']]
                    if any(w in s_norm for w in r_words):
                        break
                        
            if candidate_app_id:
                assigned_app_ids.add(candidate_app_id)
                c.execute('''
                    UPDATE verified_applications
                    SET email_verified = 1, email_subject = ?, email_sender = ?, email_received_at = ?
                    WHERE id = ?
                ''', (r['subject'], r['from'], r['date'], candidate_app_id))
                matched_new += 1

        conn.commit()
        c.execute("SELECT COUNT(*) FROM verified_applications WHERE email_verified = 1")
        ev_total = c.fetchone()[0]
        conn.close()
        print(f"[+] Receipt sync complete: {matched_new} newly mapped, total verified receipts in DB: {ev_total}")
        return ev_total
    except Exception as e:
        print(f"[-] Receipt sync notice: {e}")
        return 0

if __name__ == '__main__':
    sync_receipts()
