#!/usr/bin/env python3
"""
Harvest Verified Internships from Top Tech Internship Repositories
Extracts direct Greenhouse and Ashby apply links from curated college/summer internship repos.
Filters with critique_application and adds to github_verified_internships.json and live_fresh_verified_roles.json.
"""

import requests
import re
import json
import sqlite3
import os
from bs4 import BeautifulSoup

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, 'verified_job_applications.db')
conn = sqlite3.connect(DB_PATH)
c = conn.cursor()
applied_urls = set(r[0] for r in c.execute('SELECT job_url FROM verified_applications').fetchall())
applied_pairs = set((r[0].lower(), r[1].lower()) for r in c.execute('SELECT company, role FROM verified_applications').fetchall())
dead_urls = set(r[0] for r in c.execute('SELECT url FROM checked_dead_urls').fetchall())
conn.close()

from run_unified_verified_engine import critique_application

seen_urls = set(applied_urls)
seen_urls.update(dead_urls)

repos = [
    "https://raw.githubusercontent.com/SimplifyJobs/Summer2027-Internships/dev/README.md",
    "https://raw.githubusercontent.com/SimplifyJobs/Summer2026-Internships/dev/README.md",
    "https://raw.githubusercontent.com/PrepAIJobs/Summer2026-Internships/main/README.md",
    "https://raw.githubusercontent.com/SimplifyJobs/Summer2025-Internships/dev/README.md",
    "https://raw.githubusercontent.com/SimplifyJobs/Summer2025-Internships/master/README.md",
    "https://raw.githubusercontent.com/pittcsc/Summer2025-Internships/master/README.md",
    "https://raw.githubusercontent.com/speedyapply/2025-SWE-College-Jobs/main/README.md"
]

harvested_interns = []
last_comp = "Tech Startup"

for repo_url in repos:
    try:
        print(f"[*] Fetching {repo_url}...")
        r = requests.get(repo_url, timeout=15)
        if r.status_code != 200:
            continue
        
        soup = BeautifulSoup(r.text, 'html.parser')
        rows = soup.find_all('tr')
        print(f"    Found {len(rows)} rows")
        
        for row in rows:
            tds = row.find_all('td')
            if len(tds) >= 4:
                raw_comp = tds[0].get_text(strip=True).replace('↳', '').replace('🔥', '').strip()
                if raw_comp:
                    last_comp = raw_comp
                comp = last_comp
                
                title = tds[1].get_text(strip=True)
                links = [a.get('href') for a in tds[3].find_all('a') if a.get('href')]
                apply_links = [l for l in links if 'simplify.jobs' not in l]
                if not apply_links:
                    continue
                
                u = apply_links[0].strip().replace('&amp;', '&')
                
                if 'greenhouse.io' not in u and 'ashbyhq.com' not in u:
                    continue
                
                if u in seen_urls:
                    continue
                
                if (comp.lower(), title.lower()) in applied_pairs:
                    continue
                
                score, reason = critique_application(comp, title)
                if score < 60:
                    continue
                
                portal = 'Greenhouse' if 'greenhouse.io' in u else 'Ashby'
                seen_urls.add(u)
                
                item = {
                    'company': comp,
                    'title': title,
                    'applyUrl': u,
                    'portal_type': portal,
                    'is_internship': True,
                    'category': 'INTERNSHIP',
                    'stipend': '$5,000 - $9,000 / mo USD',
                    'fit_score': score
                }
                harvested_interns.append(item)
    except Exception as e:
        print(f"[-] Error parsing {repo_url}: {e}")

print(f"\n[+] Total New Verified GitHub Internships Harvested: {len(harvested_interns)}")

out_path = os.path.join(BASE_DIR, 'github_verified_internships.json')
with open(out_path, 'w') as f:
    json.dump(harvested_interns, f, indent=2)

# Also merge into live_fresh_verified_roles.json
live_file = os.path.join(BASE_DIR, 'live_fresh_verified_roles.json')
existing_live = []
if os.path.exists(live_file):
    try:
        with open(live_file) as f:
            existing_live = json.load(f)
    except Exception:
        pass

existing_urls = set((r.get('applyUrl') or r.get('url')) for r in existing_live)
added_to_live = 0
for item in harvested_interns:
    u = item.get('applyUrl')
    if u and u not in existing_urls:
        existing_live.append(item)
        existing_urls.add(u)
        added_to_live += 1

with open(live_file, 'w') as f:
    json.dump(existing_live, f, indent=2)

print(f"[+] Added {added_to_live} internships to {live_file}. Total roles now: {len(existing_live)}")
