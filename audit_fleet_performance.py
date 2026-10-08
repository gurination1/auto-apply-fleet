#!/usr/bin/env python3
"""
Autonomous Cloud Fleet Performance Auditor
Determines actual run performance through verified submissions and Gmail IMAP receipts.
Generates GitHub Actions Step Summary markdown.
"""

import os
import sqlite3

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, 'verified_job_applications.db')

def audit_performance():
    if not os.path.exists(DB_PATH):
        print("[-] Database not found.")
        return

    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    tot = c.execute('SELECT count(*) FROM verified_applications').fetchone()[0]
    jobs = c.execute("SELECT count(*) FROM verified_applications WHERE application_type='JOB'").fetchone()[0]
    interns = c.execute("SELECT count(*) FROM verified_applications WHERE application_type='INTERNSHIP'").fetchone()[0]
    emails = c.execute('SELECT count(*) FROM verified_applications WHERE email_verified=1').fetchone()[0]
    recent = c.execute('SELECT company, role, application_type, applied_at, email_verified FROM verified_applications ORDER BY id DESC LIMIT 10').fetchall()
    conn.close()

    print("\n" + "="*60)
    print("📈 CLOUD FLEET PERFORMANCE AUDIT REPORT")
    print("="*60)
    print(f"Total Verified Confirmed: {tot} / 2,000 ({tot/20:.1f}%)")
    print(f"  Remote Tech Jobs:       {jobs} / 1,000 ({jobs/10:.1f}%)")
    print(f"  Paid Tech Internships:  {interns} / 1,000 ({interns/10:.1f}%)")
    print(f"Verified IMAP Receipts:   {emails} ({emails/tot*100:.1f}% delivery proof)")
    print("="*60)

    summary_file = os.environ.get('GITHUB_STEP_SUMMARY')
    if summary_file:
        try:
            with open(summary_file, 'a') as f:
                f.write('## 📊 Cloud Fleet Performance Audit\n\n')
                f.write('| Fleet Metric | Count | 2,000 Milestone | Status |\n')
                f.write('| :--- | :---: | :---: | :---: |\n')
                f.write(f'| **Total Confirmed** | **{tot}** | 2,000 | **{tot/20:.1f}%** |\n')
                f.write(f'| **Remote Tech Jobs** | **{jobs}** | 1,000 | **{jobs/10:.1f}%** |\n')
                f.write(f'| **Paid Internships** | **{interns}** | 1,000 | **{interns/10:.1f}%** |\n')
                f.write(f'| **IMAP Verified Receipts** | **{emails}** | - | **{emails/tot*100:.1f}%** Verified Delivery |\n\n')
                f.write('### 🎯 Latest 10 Submissions:\n\n')
                f.write('| Company | Role | Type | Applied At | Email Receipt |\n')
                f.write('| :--- | :--- | :---: | :--- | :---: |\n')
                for r in recent:
                    verified_icon = '✅ Confirmed' if r[4] else '⏳ Pending / Delivered'
                    f.write(f'| **{r[0]}** | {r[1]} | `{r[2]}` | {r[3]} | {verified_icon} |\n')
            print("[+] Successfully wrote GitHub Actions step summary.")
        except Exception as e:
            print(f"[-] Could not write step summary: {e}")

if __name__ == '__main__':
    audit_performance()
