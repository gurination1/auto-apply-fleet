#!/usr/bin/env python3
"""
Unified Autonomous Cloud Harvester
Harvests both Paid Tech Internships and Early-Career/Junior Software Engineer Jobs
from top high-velocity GitHub repositories (SimplifyJobs, vanshb03, PrepAIJobs, zshah101).
Strictly applies critique_application (Zero ML, Software/Frontend/Full-Stack/Cloud only).
Supports both HTML table rows and Markdown pipe tables across all link columns.
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
c.execute('''CREATE TABLE IF NOT EXISTS checked_dead_urls (
    url TEXT PRIMARY KEY,
    checked_at DATETIME DEFAULT CURRENT_TIMESTAMP
)''')
applied_urls = set(r[0] for r in c.execute('SELECT job_url FROM verified_applications').fetchall() if r[0])
applied_pairs = set((r[0].lower(), r[1].lower()) for r in c.execute('SELECT company, role FROM verified_applications').fetchall() if r[0] and r[1])
dead_urls = set(r[0] for r in c.execute('SELECT url FROM checked_dead_urls').fetchall() if r[0])
conn.close()

from run_unified_verified_engine import critique_application

def is_ashby_active(url):
    try:
        r = requests.get(url, headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}, timeout=4)
        if 'window.__appData' in r.text:
            m = re.search(r'window\.__appData\s*=\s*(\{.*?\});', r.text)
            if m:
                data = json.loads(m.group(1))
                return data.get('posting') is not None
        return True
    except Exception:
        return True

seen_urls = set()
for u in applied_urls:
    seen_urls.add(u.lower().rstrip('/'))
    seen_urls.add(u.split('?')[0].lower().rstrip('/'))
for u in dead_urls:
    seen_urls.add(u.lower().rstrip('/'))
    seen_urls.add(u.split('?')[0].lower().rstrip('/'))

TARGET_SOURCES = [
    # --- INTERNSHIPS ---
    {
        "url": "https://raw.githubusercontent.com/SimplifyJobs/Summer2027-Internships/dev/README.md",
        "is_internship": True,
        "default_stipend": "$5,000 - $9,000 / mo USD"
    },
    {
        "url": "https://raw.githubusercontent.com/SimplifyJobs/Summer2026-Internships/dev/README.md",
        "is_internship": True,
        "default_stipend": "$5,000 - $8,500 / mo USD"
    },
    {
        "url": "https://raw.githubusercontent.com/zshah101/Automated-List-Of-Summer-2027-and-Fall-2026-Tech-Internships/main/README.md",
        "is_internship": True,
        "default_stipend": "$5,000 - $8,000 / mo USD"
    },
    {
        "url": "https://raw.githubusercontent.com/PrepAIJobs/Summer2026-Internships/main/README.md",
        "is_internship": True,
        "default_stipend": "$4,500 - $8,000 / mo USD"
    },
    {
        "url": "https://raw.githubusercontent.com/SimplifyJobs/Summer2026-Internships/dev/README-Off-Season.md",
        "is_internship": True,
        "default_stipend": "$5,000 - $8,500 / mo USD"
    },
    {
        "url": "https://raw.githubusercontent.com/SimplifyJobs/Summer2025-Internships/dev/README.md",
        "is_internship": True,
        "default_stipend": "$5,000 - $8,500 / mo USD"
    },
    {
        "url": "https://raw.githubusercontent.com/pittcsc/Summer2025-Internships/master/README.md",
        "is_internship": True,
        "default_stipend": "$5,000 - $8,000 / mo USD"
    },
    # --- FULL-TIME TECH JOBS (NEW GRAD & EARLY-CAREER SWE) ---
    {
        "url": "https://raw.githubusercontent.com/speedyapply/2026-SWE-College-Jobs/main/README.md",
        "is_internship": False,
        "default_stipend": "$85,000 - $130,000 USD / year"
    },
    {
        "url": "https://raw.githubusercontent.com/SimplifyJobs/New-Grad-Positions/dev/README.md",
        "is_internship": False,
        "default_stipend": "$80,000 - $130,000 USD / year"
    },
    {
        "url": "https://raw.githubusercontent.com/vanshb03/New-Grad-2026/main/README.md",
        "is_internship": False,
        "default_stipend": "$85,000 - $125,000 USD / year"
    },
    {
        "url": "https://raw.githubusercontent.com/vanshb03/New-Grad-2027/main/README.md",
        "is_internship": False,
        "default_stipend": "$85,000 - $125,000 USD / year"
    },
    {
        "url": "https://raw.githubusercontent.com/vanshb03/New-Grad-2025/main/README.md",
        "is_internship": False,
        "default_stipend": "$85,000 - $125,000 USD / year"
    },
    {
        "url": "https://raw.githubusercontent.com/PrepAIJobs/New-Grad-2026/main/README.md",
        "is_internship": False,
        "default_stipend": "$80,000 - $120,000 USD / year"
    }
]

harvested_interns = []
harvested_jobs = []

print("=== STARTING UNIFIED AUTONOMOUS CLOUD HARVEST ===")
for src in TARGET_SOURCES:
    src_url = src["url"]
    is_intern = src["is_internship"]
    stipend = src["default_stipend"]
    try:
        print(f"[*] Ingesting: {src_url} ...")
        resp = requests.get(src_url, timeout=18)
        if resp.status_code != 200:
            print(f"    [-] HTTP {resp.status_code}, skipping.")
            continue
        
        raw_text = resp.text
        valid_in_source = 0
        last_comp = "Tech Startup"
        
        # 1. Parse HTML <tr> rows if present
        soup = BeautifulSoup(raw_text, 'html.parser')
        rows = soup.find_all('tr')
        if len(rows) > 5:
            for row in rows:
                tds = row.find_all('td')
                if len(tds) >= 3:
                    raw_comp = tds[0].get_text(strip=True).replace('↳', '').replace('🔥', '').replace('✓', '').strip()
                    if raw_comp:
                        last_comp = raw_comp
                    comp = last_comp
                    title = tds[1].get_text(strip=True).replace('🆕', '').strip()
                    
                    # Search all remaining tds for links
                    links = []
                    for td in tds[2:]:
                        for a in td.find_all('a'):
                            h = a.get('href')
                            if h and 'simplify.jobs' not in h:
                                links.append(h)
                    
                    matching_links = [l for l in links if ('greenhouse.io' in l or 'ashbyhq.com' in l or 'lever.co' in l) and 'simplify.jobs' not in l]
                    if not matching_links:
                        continue
                    
                    u = matching_links[0].strip().replace('&amp;', '&')
                    u_norm = u.lower().rstrip('/')
                    u_base = u.split('?')[0].lower().rstrip('/')
                    if u_norm in seen_urls or u_base in seen_urls:
                        continue
                    
                    clean_c = re.sub(r'<[^>]+>', '', comp).strip().lower()
                    clean_t = re.sub(r'<[^>]+>', '', title).strip().lower()
                    if (clean_c, clean_t) in applied_pairs:
                        continue
                    
                    if 'lever.co' in u:
                        continue

                    score, reason = critique_application(comp, title)
                    if score < 80:
                        continue
                    
                    portal = 'Greenhouse' if 'greenhouse.io' in u else 'Ashby'
                    if portal == 'Ashby' and not is_ashby_active(u):
                        seen_urls.add(u_norm)
                        seen_urls.add(u_base)
                        continue
                    
                    seen_urls.add(u_norm)
                    seen_urls.add(u_base)
                    
                    item = {
                        'company': comp,
                        'title': title,
                        'applyUrl': u,
                        'portal_type': portal,
                        'is_internship': is_intern,
                        'category': 'INTERNSHIP' if is_intern else 'JOB',
                        'stipend': stipend,
                        'fit_score': score,
                        'critique_reason': reason
                    }
                    if is_intern:
                        harvested_interns.append(item)
                    else:
                        harvested_jobs.append(item)
                    valid_in_source += 1

        # 2. Parse Markdown pipe tables if present
        for line in raw_text.split('\n'):
            line_s = line.strip()
            if line_s.startswith('|') and not line_s.startswith('| ---') and not line_s.startswith('| Company'):
                parts = [p.strip() for p in line_s.split('|')[1:-1]]
                if len(parts) >= 3:
                    raw_comp = parts[0].replace('**', '').replace('✓', '').replace('🔥', '').strip()
                    raw_comp = re.sub(r'<[^>]+>', '', raw_comp)
                    raw_comp = re.sub(r'\[([^\]]+)\]\([^\)]+\)', r'\1', raw_comp).strip()
                    if raw_comp:
                        last_comp = raw_comp
                    comp = last_comp
                    raw_title = parts[1].replace('**', '').replace('🆕', '').strip()
                    raw_title = re.sub(r'<[^>]+>', '', raw_title)
                    title = re.sub(r'\[([^\]]+)\]\([^\)]+\)', r'\1', raw_title).strip()
                    
                    all_text = ' '.join(parts[2:])
                    links = re.findall(r'href=[\"\']([^\"\']+)[\"\']', all_text) + re.findall(r'\[.*?\]\((https?://[^\)]+)\)', all_text)
                    matching_links = [l for l in links if ('greenhouse.io' in l or 'ashbyhq.com' in l or 'lever.co' in l) and 'simplify.jobs' not in l]
                    if not matching_links:
                        continue
                    
                    u = matching_links[0].strip().replace('&amp;', '&')
                    u_norm = u.lower().rstrip('/')
                    u_base = u.split('?')[0].lower().rstrip('/')
                    if u_norm in seen_urls or u_base in seen_urls:
                        continue
                    
                    clean_c = re.sub(r'<[^>]+>', '', comp).strip().lower()
                    clean_t = re.sub(r'<[^>]+>', '', title).strip().lower()
                    if (clean_c, clean_t) in applied_pairs:
                        continue
                    
                    if 'lever.co' in u:
                        continue

                    score, reason = critique_application(comp, title)
                    if score < 80:
                        continue
                    
                    portal = 'Greenhouse' if 'greenhouse.io' in u else 'Ashby'
                    if portal == 'Ashby' and not is_ashby_active(u):
                        seen_urls.add(u_norm)
                        seen_urls.add(u_base)
                        continue
                    
                    seen_urls.add(u_norm)
                    seen_urls.add(u_base)
                    
                    item = {
                        'company': comp,
                        'title': title,
                        'applyUrl': u,
                        'portal_type': portal,
                        'is_internship': is_intern,
                        'category': 'INTERNSHIP' if is_intern else 'JOB',
                        'stipend': stipend,
                        'fit_score': score,
                        'critique_reason': reason
                    }
                    if is_intern:
                        harvested_interns.append(item)
                    else:
                        harvested_jobs.append(item)
                    valid_in_source += 1

        print(f"    [+] Extracted {valid_in_source} verified roles from source.")
    except Exception as e:
        print(f"[-] Error processing {src_url}: {e}")

# --- 3. DIRECT ATS API HARVESTING (GREENHOUSE & ASHBY PUBLIC APIS) ---
print("\n=== STARTING DIRECT ATS API HARVEST (GREENHOUSE & ASHBY) ===")
from concurrent.futures import ThreadPoolExecutor

gh_slugs = set()
ashby_slugs = set()
try:
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    for url, comp in c.execute('SELECT job_url, company FROM verified_applications'):
        if not url: continue
        m_gh = re.search(r'boards\.greenhouse\.io/([^/?#]+)', url) or re.search(r'greenhouse\.io/embed/job_board\?for=([^&]+)', url) or re.search(r'job-boards\.greenhouse\.io/([^/?#]+)', url)
        if m_gh: gh_slugs.add(m_gh.group(1).lower())
        m_ash = re.search(r'jobs\.ashbyhq\.com/([^/?#]+)', url)
        if m_ash: ashby_slugs.add(m_ash.group(1).lower())
    conn.close()
except Exception:
    pass

gh_slugs.update([
    'figma', 'stripe', 'scale', 'retool', 'affirm', 'postman', 'cloudflare', 'gitlab', 'databricks',
    'brex', 'ramp', 'notion', 'airbyte', 'benchling', 'andurilindustries', 'gusto', 'instacart',
    'coinbase', 'roblox', 'snapchat', 'pinterest', 'box', 'dropbox', 'github', 'reddit', 'mongodb',
    'elastic', 'datadog', 'pagerduty', 'twilio', 'hashicorp', 'splunk', 'okta', 'hubspot', 'toast',
    'duolingo', 'coursera', 'asana', 'airtable', 'spacex', 'tesla', 'plaid', 'wealthfront',
    'robinhood', 'samsara', 'checkr', 'blend', 'lattice', 'ironclad', 'gusto', 'ripple'
])

ashby_slugs.update([
    'linear', 'sentry', 'supabase', 'vercel', 'modal', 'neon', 'temporal', 'togetherai', 'elevenlabs',
    'perplexity', 'resend', 'clerk', 'posthog', 'raycast', 'calcom', 'dub', 'prisma', 'triggerdotdev',
    'inngest', 'langchain', 'llamaindex', 'qdrant', 'weaviate', 'pinecone', 'deepgram', 'assemblyai',
    'cursor', 'anysphere', 'codeium', 'replit', 'midjourney', 'runpod', 'flyio', 'baseten', 'replicate',
    'retool', 'writer', 'tavily', 'brave', 'synthesia', 'groq', 'modal-labs'
])

print(f"[*] Querying {len(gh_slugs)} Greenhouse boards and {len(ashby_slugs)} Ashby boards...")

def fetch_gh(slug):
    try:
        r = requests.get(f'https://boards-api.greenhouse.io/v1/boards/{slug}/jobs', timeout=4)
        if r.status_code == 200:
            for j in r.json().get('jobs', []):
                t = j.get('title', '')
                u = j.get('absolute_url', '')
                if not u: continue
                u_norm = u.lower().rstrip('/')
                u_base = u.split('?')[0].lower().rstrip('/')
                if u_norm in seen_urls or u_base in seen_urls: continue
                c_name = slug.capitalize()
                clean_c = re.sub(r'<[^>]+>', '', c_name).strip().lower()
                clean_t = re.sub(r'<[^>]+>', '', t).strip().lower()
                if (clean_c, clean_t) in applied_pairs: continue

                score, reason = critique_application(c_name, t)
                if score < 80: continue

                is_intern = bool(re.search(r'\b(intern|internship|co-op|coop|apprentice)\b', t.lower()))
                seen_urls.add(u_norm)
                seen_urls.add(u_base)
                item = {
                    'company': c_name,
                    'title': t,
                    'applyUrl': u,
                    'portal_type': 'Greenhouse',
                    'is_internship': is_intern,
                    'category': 'INTERNSHIP' if is_intern else 'JOB',
                    'stipend': '$5,000 - $9,000 / mo USD' if is_intern else '$85,000 - $130,000 USD / year',
                    'fit_score': score,
                    'critique_reason': reason
                }
                if is_intern:
                    harvested_interns.append(item)
                else:
                    harvested_jobs.append(item)
    except Exception:
        pass

def fetch_ash(slug):
    query = '''
    query ApiJobBoardWithTeams($organizationHostedJobsPageName: String!) {
      jobBoard: jobBoardWithTeams(organizationHostedJobsPageName: $organizationHostedJobsPageName) {
        jobPostings { id title locationName }
      }
    }'''
    try:
        r = requests.post(
            'https://jobs.ashbyhq.com/api/non-user-graphql?op=ApiJobBoardWithTeams',
            json={'operationName': 'ApiJobBoardWithTeams', 'variables': {'organizationHostedJobsPageName': slug}, 'query': query},
            headers={'Content-Type': 'application/json', 'User-Agent': 'Mozilla/5.0'},
            timeout=4
        )
        if r.status_code == 200:
            for p in r.json().get('data', {}).get('jobBoard', {}).get('jobPostings', []):
                t = p.get('title', '')
                j_id = p.get('id', '')
                u = f'https://jobs.ashbyhq.com/{slug}/{j_id}'
                if not u: continue
                u_norm = u.lower().rstrip('/')
                u_base = u.split('?')[0].lower().rstrip('/')
                if u_norm in seen_urls or u_base in seen_urls: continue
                c_name = slug.capitalize()
                clean_c = re.sub(r'<[^>]+>', '', c_name).strip().lower()
                clean_t = re.sub(r'<[^>]+>', '', t).strip().lower()
                if (clean_c, clean_t) in applied_pairs: continue

                score, reason = critique_application(c_name, t)
                if score < 80: continue

                is_intern = bool(re.search(r'\b(intern|internship|co-op|coop|apprentice)\b', t.lower()))
                seen_urls.add(u_norm)
                seen_urls.add(u_base)
                item = {
                    'company': c_name,
                    'title': t,
                    'applyUrl': u,
                    'portal_type': 'Ashby',
                    'is_internship': is_intern,
                    'category': 'INTERNSHIP' if is_intern else 'JOB',
                    'stipend': '$5,000 - $9,000 / mo USD' if is_intern else '$85,000 - $130,000 USD / year',
                    'fit_score': score,
                    'critique_reason': reason
                }
                if is_intern:
                    harvested_interns.append(item)
                else:
                    harvested_jobs.append(item)
    except Exception:
        pass

with ThreadPoolExecutor(max_workers=25) as ex:
    ex.map(fetch_gh, list(gh_slugs))
    ex.map(fetch_ash, list(ashby_slugs))

print(f"\n[+] Total New Harvested: {len(harvested_interns)} Internships, {len(harvested_jobs)} Jobs.")

# 1. Save specific queues
with open(os.path.join(BASE_DIR, 'github_verified_internships.json'), 'w') as f:
    json.dump(harvested_interns, f, indent=2)

with open(os.path.join(BASE_DIR, 'github_verified_jobs.json'), 'w') as f:
    json.dump(harvested_jobs, f, indent=2)

# 2. Merge into live_fresh_verified_roles.json
live_file = os.path.join(BASE_DIR, 'live_fresh_verified_roles.json')
existing_live = []
if os.path.exists(live_file):
    try:
        with open(live_file) as f:
            existing_live = json.load(f)
    except Exception:
        pass

existing_urls = set((r.get('applyUrl') or r.get('url') or '').lower().rstrip('/') for r in existing_live)
new_added = 0
for item in (harvested_interns + harvested_jobs):
    u = (item.get('applyUrl') or item.get('url') or '').lower().rstrip('/')
    if u and u not in existing_urls:
        existing_live.append(item)
        existing_urls.add(u)
        new_added += 1

with open(live_file, 'w') as f:
    json.dump(existing_live, f, indent=2)

print(f"[+] Total live pool now at {len(existing_live)} roles ({new_added} newly added).")
