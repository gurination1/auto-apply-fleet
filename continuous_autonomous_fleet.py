#!/usr/bin/env python3
"""
Continuous Autonomous Fleet Supervisor
Runs continuous submission batches, syncs receipts, and regenerates live dashboards
until reaching the target milestone (1,000 paid internships + 1,000 remote jobs).
"""

import time
import subprocess
import sqlite3
import os
import sys
import asyncio

DB_PATH = '/root/gurdharam_resume/verified_job_applications.db'

def get_stats():
    try:
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        tot = c.execute("SELECT count(*) FROM verified_applications").fetchone()[0]
        jobs = c.execute("SELECT count(*) FROM verified_applications WHERE application_type='JOB'").fetchone()[0]
        interns = c.execute("SELECT count(*) FROM verified_applications WHERE application_type='INTERNSHIP'").fetchone()[0]
        receipts = c.execute("SELECT count(*) FROM verified_applications WHERE email_verified=1").fetchone()[0]
        conn.close()
        return tot, jobs, interns, receipts
    except Exception as e:
        return 0, 0, 0, 0

def is_runner_running():
    try:
        res = subprocess.run("pgrep -f 'python3.*[r]un_unified_verified_engine.py'", shell=True, capture_output=True, text=True)
        return bool(res.stdout.strip())
    except Exception:
        return False

def main():
    print("=== CONTINUOUS AUTONOMOUS FLEET SUPERVISOR STARTED ===")
    
    # Wait for any active single batch runner to complete first
    while is_runner_running():
        tot, jobs, interns, receipts = get_stats()
        print(f"[*] Active runner detected. Current DB: {tot} (Jobs: {jobs}, Interns: {interns}, Receipts: {receipts}). Waiting 15s...")
        time.sleep(15)

    batch_num = 1
    while True:
        tot, jobs, interns, receipts = get_stats()
        print(f"\n========================================================")
        print(f"[*] LAUNCHING BATCH #{batch_num} | DB Total: {tot} (Jobs: {jobs}, Internships: {interns}, Receipts: {receipts})")
        print(f"========================================================")

        if jobs >= 1000 and interns >= 1000:
            print(f"🎉 2,000 GRAND MILESTONE REACHED! (1,000 Jobs + 1,000 Internships)")
            break

        # Run unified verified engine for 60 items per batch across all roles (jobs + internships)
        mode = 'all'

        cmd = f"python3 -u /root/gurdharam_resume/run_unified_verified_engine.py --mode {mode} --limit 60 >> /root/gurdharam_resume/continuous_fleet.log 2>&1"
        subprocess.run(cmd, shell=True)

        # Sync receipts & dashboard
        print(f"[*] Batch #{batch_num} completed. Syncing Gmail receipts & regenerating dashboard...")
        try:
            subprocess.run("python3 /root/gurdharam_resume/sync_all_receipts.py", shell=True)
            subprocess.run("python3 /root/gurdharam_resume/generate_dashboard.py", shell=True)
        except Exception as e:
            print(f"[-] Error syncing: {e}")

        tot_after, jobs_after, interns_after, receipts_after = get_stats()
        print(f"[+] Updated DB Total: {tot_after} (Jobs: {jobs_after}, Interns: {interns_after}, Receipts: {receipts_after})")
        batch_num += 1
        time.sleep(5)

if __name__ == '__main__':
    main()
