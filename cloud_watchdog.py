#!/usr/bin/env python3
"""
Autonomous GHA Cloud Fleet Watchdog Daemon
Ensures the 24-worker GitHub Actions application fleet never stalls or stops.
Survives terminal/chat exits by running detached in the background.
Monitors run health, auto-dispatches if idle > 15m, and syncs upstream DB changes.
"""

import os
import sys
import time
import json
import subprocess
from datetime import datetime, timezone

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
LOG_FILE = os.path.join(BASE_DIR, "cloud_watchdog.log")
PID_FILE = os.path.join(BASE_DIR, "cloud_watchdog.pid")
REPO = "gurination1/auto-apply-fleet"

def log(msg):
    ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    formatted = f"[{ts}] {msg}"
    print(formatted, flush=True)
    try:
        with open(LOG_FILE, "a") as f:
            f.write(formatted + "\n")
    except Exception:
        pass

def is_already_running():
    if os.path.exists(PID_FILE):
        try:
            with open(PID_FILE, "r") as f:
                pid = int(f.read().strip())
            # Check if process is alive
            os.kill(pid, 0)
            return True
        except (OSError, ValueError):
            return False
    return False

def write_pid():
    with open(PID_FILE, "w") as f:
        f.write(str(os.getpid()))

def get_latest_runs():
    try:
        res = subprocess.run(
            ["gh", "run", "list", "--repo", REPO, "--limit", "3", "--json", "databaseId,status,conclusion,createdAt,updatedAt"],
            capture_output=True,
            text=True,
            timeout=25,
            cwd=BASE_DIR
        )
        if res.returncode == 0:
            return json.loads(res.stdout)
    except Exception as e:
        log(f"[-] Error querying gh runs: {e}")
    return []

def trigger_workflow(limit=10):
    log("[*] Dispatching fresh 24-worker autonomous application fleet on GHA...")
    try:
        res = subprocess.run(
            ["gh", "workflow", "run", "auto_apply.yml", "--repo", REPO, "-f", "mode=all", "-f", f"limit={limit}"],
            capture_output=True,
            text=True,
            timeout=30,
            cwd=BASE_DIR
        )
        if res.returncode == 0:
            log("[+] Successfully triggered auto_apply.yml workflow!")
            return True
        else:
            log(f"[-] gh workflow run failed: {res.stderr}")
    except Exception as e:
        log(f"[-] Exception triggering workflow: {e}")
    return False

def sync_git():
    try:
        subprocess.run(["git", "fetch", "origin", "main"], cwd=BASE_DIR, capture_output=True, timeout=30)
        # Check if remote main is ahead
        res = subprocess.run(["git", "rev-parse", "HEAD", "FETCH_HEAD"], cwd=BASE_DIR, capture_output=True, text=True)
        lines = res.stdout.strip().split()
        if len(lines) == 2 and lines[0] != lines[1]:
            log(f"[*] Upstream commits detected. Merging database updates...")
            subprocess.run(["python3", "merge_db_and_sync.py", "backup"], cwd=BASE_DIR, capture_output=True)
            subprocess.run(["git", "reset", "--hard", "FETCH_HEAD"], cwd=BASE_DIR, capture_output=True)
            subprocess.run(["python3", "merge_db_and_sync.py", "merge"], cwd=BASE_DIR, capture_output=True)
            log("[+] Local DB cleanly synced with latest cloud commits.")
    except Exception as e:
        log(f"[-] Git sync note: {e}")

def main():
    write_pid()
    log("[+] Perpetual GHA Cloud Watchdog Daemon started. Monitoring 24/7...")

    while True:
        try:
            sync_git()
            runs = get_latest_runs()
            
            if not runs:
                log("[-] No run status retrieved. Retrying in 60s...")
                time.sleep(60)
                continue

            active_run = None
            for r in runs:
                if r.get("status") in ["in_progress", "queued"]:
                    active_run = r
                    break

            if active_run:
                log(f"[+] Active GHA run in flight: ID={active_run.get('databaseId')} status={active_run.get('status')}")
            else:
                latest = runs[0]
                updated_at_str = latest.get("updatedAt", latest.get("createdAt", ""))
                idle_seconds = 99999
                if updated_at_str:
                    try:
                        # Parse ISO UTC timestamp
                        dt = datetime.fromisoformat(updated_at_str.replace("Z", "+00:00"))
                        now = datetime.now(timezone.utc)
                        idle_seconds = (now - dt).total_seconds()
                    except Exception:
                        pass
                
                log(f"[*] Fleet idle. Last run finished {int(idle_seconds)}s ago.")
                if idle_seconds > 90:  # If idle for more than 90 seconds after completion
                    log("[*] Idle threshold met. Discharging next cycle immediately...")
                    trigger_workflow(limit=10)
                    time.sleep(180)  # Wait for run to queue
                    continue

        except Exception as e:
            log(f"[-] Watchdog loop error: {e}")

        # Sleep between checks
        time.sleep(120)

if __name__ == "__main__":
    if is_already_running():
        print("[-] Cloud watchdog already running.")
        sys.exit(0)
    main()
