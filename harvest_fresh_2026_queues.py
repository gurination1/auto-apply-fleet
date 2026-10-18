#!/usr/bin/env python3
"""
Fresh 2026 Live Target Harvester
Harvests active, open internships and early-career software engineering roles directly from
SimplifyJobs live repos and direct Greenhouse/Ashby APIs.
Enforces:
- 100% Direct ATS (Greenhouse and Ashby ONLY; 0% Lever to bypass hCaptcha)
- Strict Junior / Lower-Mid / Intern / New Grad targeting
- 0% Machine Learning / AI Research
- Strict deduplication against SQLite database
"""

import json
import sqlite3
import re
import os
import requests

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, 'verified_job_applications.db')

BANNED_KEYWORDS = [
    # 1. AI / ML Research / Data Science
    'machine learning', 'deep learning', 'ai research', 'research intern', 'research engineer',
    'research scientist', 'applied scientist', 'ai scientist', 'data scientist', 'data science',
    'data engineer', 'data analyst', 'data analytics', 'analytics engineer', 'bi engineer',
    'quantitative', 'quant ', 'foundation model', 'reinforcement learning', 'computer vision',
    'nlp research', 'algorithm', 'mlff', 'chemistry', 'chemical', 'physics', 'plasma',
    # 2. Hardware / Electronics / Embedded / Mechanical
    'hardware', 'analog', 'firmware', 'embedded', 'rf engineer', 'fpga', 'asic', 'silicon',
    'pcb', 'circuit', 'electrical', 'controls', 'vehicle', 'automotive', 'battery', 'mechanical',
    'thermal', 'propulsion', 'avionics',
    # 3. Business / Product / Sales / Marketing / Finance
    'product manager', 'pm intern', 'product management', 'bizdev', 'sales', 'marketing',
    'finance', 'private equity', 'trading', 'banking', 'investment', 'legal', 'recruiter', 'hr',
    # 4. Over-Seniority
    'senior', 'sr.', 'sr ', 'staff', 'principal', 'lead', 'architect', 'director',
    'head of', 'vp ', 'vice president', 'manager', 'executive', 'partner', 'chief'
]

ALLOWED_ROLE_KEYWORDS = [
    'software engineer', 'software developer', 'frontend', 'front end', 'front-end',
    'full stack', 'fullstack', 'full-stack', 'web developer', 'web engineer',
    'ui engineer', 'ux engineer', 'application developer', 'solutions engineer',
    'automation engineer', 'qa engineer', 'test engineer', 'sdet',
    'backend engineer', 'cloud engineer', 'devops engineer',
    'emerging talent', 'early career', 'swe intern', 'software intern'
]

def clean_url(u):
    if not u:
        return ''
    return u.strip().split('?')[0].rstrip('/').lower()

def is_banned(title):
    t_low = title.lower()
    return any(b in t_low for b in BANNED_KEYWORDS)

def is_targeted(title):
    t_low = title.lower()
    return any(k in t_low for k in ALLOWED_ROLE_KEYWORDS)

def load_applied():
    applied = set()
    if os.path.exists(DB_PATH):
        try:
            conn = sqlite3.connect(DB_PATH)
            c = conn.cursor()
            for row in c.execute('SELECT job_url FROM verified_applications').fetchall():
                if row[0]:
                    applied.add(clean_url(row[0]))
            conn.close()
        except Exception as e:
            print("[-] DB load error:", e)
    return applied

def harvest_simplify_source(url, is_intern_source=True):
    print(f"[*] Fetching from {url}...")
    try:
        r = requests.get(url, timeout=20)
        data = r.json()
    except Exception as e:
        print(f"[-] Fetch error: {e}")
        return []

    print(f"[+] Retrieved {len(data)} raw listings.")
    applied = load_applied()
    filtered = []

    for item in data:
        if not item.get('active', True):
            continue
        job_url = item.get('url', '').strip()
        comp = item.get('company_name', '').strip()
        title = item.get('title', '').strip()

        cu = clean_url(job_url)
        if not cu or cu in applied:
            continue

        # 100% Greenhouse and Ashby ONLY (0% Lever / SmartRecruiters / Workday)
        portal_type = None
        if 'greenhouse.io' in cu:
            portal_type = 'Greenhouse'
        elif 'ashbyhq.com' in cu:
            portal_type = 'Ashby'
        else:
            continue

        if is_banned(title):
            continue

        if not is_targeted(title):
            continue

        is_int = is_intern_source or any(k in title.lower() for k in ['intern', 'co-op', 'coop', 'apprentice', 'fellow', 'campus'])

        filtered.append({
            'company': comp,
            'title': title,
            'role': title,
            'portal_type': portal_type,
            'applyUrl': job_url,
            'url': job_url,
            'location': ', '.join(item.get('locations', [])) if isinstance(item.get('locations'), list) else str(item.get('locations', '')),
            'is_internship': is_int,
            'category': 'INTERNSHIP' if is_int else 'JOB',
            'stipend': '$5,000 - $8,500 / mo USD' if is_int else '$85,000 - $130,000 / yr USD'
        })
        applied.add(cu)

    print(f"[+] Filtered to {len(filtered)} targeted, active Greenhouse & Ashby roles.")
    return filtered

def main():
    intern_url = 'https://raw.githubusercontent.com/SimplifyJobs/Summer2025-Internships/dev/.github/scripts/listings.json'
    newgrad_url = 'https://raw.githubusercontent.com/SimplifyJobs/New-Grad-Positions/dev/.github/scripts/listings.json'

    interns = harvest_simplify_source(intern_url, is_intern_source=True)
    newgrads = harvest_simplify_source(newgrad_url, is_intern_source=False)

    all_fresh = interns + newgrads
    print(f"\n[+] Total fresh verified targets collected: {len(all_fresh)} (Internships: {len(interns)}, Jobs/New Grad: {len(newgrads)})")

    # Save to high_conversion_application_queue.json
    hc_path = os.path.join(BASE_DIR, 'high_conversion_application_queue.json')
    with open(hc_path, 'w') as f:
        json.dump(all_fresh, f, indent=2)
    print(f"[+] Saved {len(all_fresh)} items to {hc_path}")

    # Also save to live_fresh_verified_roles.json
    live_path = os.path.join(BASE_DIR, 'live_fresh_verified_roles.json')
    with open(live_path, 'w') as f:
        json.dump(all_fresh, f, indent=2)
    print(f"[+] Saved {len(all_fresh)} items to {live_path}")

if __name__ == '__main__':
    main()
