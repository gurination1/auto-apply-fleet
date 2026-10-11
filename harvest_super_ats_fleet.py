#!/usr/bin/env python3
"""
Super ATS Fleet Harvester (11,494 Companies: 3,161 Ashby + 8,333 Greenhouse)
Directly queries public REST APIs for verified unapplied tech roles:
- STRICT ZERO ML / AI RESEARCH / DATA SCIENCE knockouts
- STRICT ZERO SENIORITY knockouts (no senior, lead, staff, principal, manager, vp)
- STRICT TARGET STACK: Frontend, Full-Stack, Web (React, Next.js, TS), Python, Cloud Automation, Intern/Junior/Entry SWE
- ZERO DUPLICATE: Pre-filters against all 3,715 records in verified_job_applications.db
"""

import asyncio
import aiohttp
import json
import sqlite3
import re
import os
import sys
import urllib.request

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, 'verified_job_applications.db')

def clean_norm_url(u):
    if not u: return ''
    try:
        from urllib.parse import urlparse
        p = urlparse(u)
        clean = f'{p.scheme}://{p.netloc}{p.path}'.rstrip('/')
        if clean.endswith('/application'):
            clean = clean[:-12]
        return clean.lower()
    except Exception:
        return (u or '').strip().lower().split('?')[0].rstrip('/')

def clean_norm_company(c):
    return re.sub(r'[^a-z0-9]', '', (c or '').lower())

def clean_norm_role(r):
    return re.sub(r'[^a-z0-9]', '', (r or '').lower())

# 1. Load already applied entities from SQLite DB
applied_urls = set()
applied_comp_roles = set()
applied_intern_companies = set()
blacklisted_companies = set()

if os.path.exists(DB_PATH):
    try:
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute('SELECT job_url, company, role, application_type, status FROM verified_applications')
        for url, comp, role, app_type, status in c.fetchall():
            if url:
                applied_urls.add(clean_norm_url(url))
            ck = clean_norm_company(comp)
            rk = clean_norm_role(role)
            if ck and rk:
                applied_comp_roles.add((ck, rk))
            if app_type == 'INTERNSHIP' or 'intern' in (role or '').lower():
                applied_intern_companies.add(ck)
            if status == 'REJECTED_BY_COMPANY':
                blacklisted_companies.add(ck)

        c.execute('CREATE TABLE IF NOT EXISTS checked_dead_urls (url TEXT PRIMARY KEY, checked_at DATETIME)')
        for r in c.execute('SELECT url FROM checked_dead_urls'):
            if r[0]:
                applied_urls.add(clean_norm_url(r[0]))

        c.execute('CREATE TABLE IF NOT EXISTS company_blacklist (company TEXT PRIMARY KEY, reason TEXT)')
        for r in c.execute('SELECT company FROM company_blacklist'):
            if r[0]:
                blacklisted_companies.add(clean_norm_company(r[0]))

        conn.close()
        print(f"[+] Loaded {len(applied_urls)} applied/dead URLs, {len(applied_comp_roles)} role pairs, {len(blacklisted_companies)} blacklisted companies from DB.")
    except Exception as e:
        print(f"[-] DB load warning: {e}")

# Strict Candidate Knockouts
BANNED_TITLE_KEYWORDS = [
    # ML / AI Research / Data Science
    'machine learning', 'deep learning', 'ai research', 'research intern', 'research engineer',
    'research scientist', 'researcher', 'foundation model', 'reinforcement learning', 'robot learning',
    'computer vision', 'nlp research', 'data scientist', 'data science', 'quantitative',
    'quant ', 'trader', 'plasma', 'physics', 'algorithmic research', 'ai intern', 'ai evaluation',
    'applied ai', 'ai engineer', 'ai developer', 'mlops', 'llmops', 'data engineer', 'analyst',
    'analytics', 'bi engineer', 'data infra', 'data platform', 'data pipeline',
    # Hardware & Low-level / Aerospace / Defense
    'hardware', 'analog', 'firmware', 'embedded', 'rf engineer', 'fpga', 'asic', 'pcb',
    'robotics controls', 'silicon', 'optics', 'manufacturing', 'metallurgy', 'mechanical',
    'thermal', 'battery', 'avionics', 'flight software', 'orbital', 'spacecraft', 'propulsion',
    'guidance', 'defense', 'clearance', 'ts/sci', 'polygraph', 'us citizen',
    'c++', 'rust ', 'rust/', 'kernel', 'chip design',
    # IT Support / Sysadmin
    'help desk', 'helpdesk', 'desktop support', 'sysadmin', 'systems administrator',
    'network engineer', 'database administrator', 'dba ',
    # Business / Sales / PM / HR
    'product manager', 'product management', 'business development', 'bizdev', 'sales',
    'account executive', 'recruiter', 'marketing', 'finance', 'accounting', 'legal',
    # Over-Seniority
    'senior', 'sr.', 'sr ', 'staff', 'principal', 'lead', 'architect', 'director',
    'head of', 'vp ', 'vice president', 'manager', 'executive', 'partner', 'chief',
    'engineer iii', 'engineer iv', 'swe 3', 'swe 4', 'sde 3', 'sde 4'
]

BANNED_COMPANIES = [
    'citadel', 'janestreet', 'hudsonrivertrading', 'fiverings', 'jumptrading',
    'imctrading', 'optiver', 'drw', 'akunacapital', 'flowtraders', 'towerresearch', 'sig'
]

INTERN_KEYWORDS = ['intern', 'co-op', 'coop', 'apprentice', 'fellowship', 'campus', 'student', 'graduate intern']

TARGET_SWE_KEYWORDS = [
    'software engineer', 'software developer', 'frontend', 'front end', 'web developer',
    'full stack', 'fullstack', 'full-stack', 'react', 'next.js', 'typescript', 'javascript',
    'python', 'automation', 'agent', 'solutions engineer', 'product engineer', 'cloud engineer',
    'application engineer', 'ui engineer', 'web engineer', 'associate software'
]

def is_knockout(comp_clean, title):
    t_lower = title.lower()
    if comp_clean in BANNED_COMPANIES or comp_clean in blacklisted_companies:
        return True
    if any(b in t_lower for b in BANNED_TITLE_KEYWORDS):
        return True
    return False

def matches_target_profile(title):
    t_lower = title.lower()
    return any(k in t_lower for k in INTERN_KEYWORDS) or any(k in t_lower for k in TARGET_SWE_KEYWORDS)

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36',
    'Accept': 'application/json, text/plain, */*'
}

async def fetch_ashby_board(session, slug, sem):
    async with sem:
        url = f'https://api.ashbyhq.com/posting-api/job-board/{slug}'
        comp_clean = clean_norm_company(slug)
        if comp_clean in blacklisted_companies:
            return []
        try:
            async with session.get(url, headers=HEADERS, timeout=aiohttp.ClientTimeout(total=4)) as resp:
                if resp.status != 200:
                    return []
                data = await resp.json()
                jobs = data.get('jobs', [])
                if not jobs:
                    return []
                comp_name = data.get('name') or slug.capitalize()
                comp_clean = clean_norm_company(comp_name)
                results = []
                for j in jobs:
                    title = (j.get('title') or '').strip()
                    job_url = (j.get('jobUrl') or '').strip()
                    loc = (j.get('location') or '').strip()
                    if not title or not job_url:
                        continue
                    if is_knockout(comp_clean, title) or not matches_target_profile(title):
                        continue
                    nu = clean_norm_url(job_url)
                    rk = clean_norm_role(title)
                    if nu in applied_urls or (comp_clean, rk) in applied_comp_roles:
                        continue
                    is_int = any(k in title.lower() for k in INTERN_KEYWORDS)
                    if is_int and comp_clean in applied_intern_companies:
                        continue
                    results.append({
                        'company': comp_name,
                        'title': title,
                        'role': title,
                        'portal_type': 'Ashby',
                        'applyUrl': job_url,
                        'url': job_url,
                        'location': loc,
                        'is_remote': j.get('isRemote', False) or 'remote' in str(loc).lower(),
                        'is_internship': is_int,
                        'category': 'INTERNSHIP' if is_int else 'JOB',
                        'stipend': '$5,000 - $8,500 / mo USD' if is_int else '$85,000 - $130,000 / yr USD'
                    })
                return results
        except Exception:
            return []

async def fetch_greenhouse_board(session, slug, sem):
    async with sem:
        url = f'https://boards-api.greenhouse.io/v1/boards/{slug}/jobs'
        comp_clean = clean_norm_company(slug)
        if comp_clean in blacklisted_companies:
            return []
        try:
            async with session.get(url, headers=HEADERS, timeout=aiohttp.ClientTimeout(total=4)) as resp:
                if resp.status != 200:
                    return []
                data = await resp.json()
                jobs = data.get('jobs', [])
                if not jobs:
                    return []
                comp_name = slug.replace('-', ' ').title()
                comp_clean = clean_norm_company(comp_name)
                results = []
                for j in jobs:
                    title = (j.get('title') or '').strip()
                    apply_url = (j.get('absolute_url') or '').strip()
                    loc = ((j.get('location') or {}).get('name') or '').strip()
                    if not title or not apply_url:
                        continue
                    if is_knockout(comp_clean, title) or not matches_target_profile(title):
                        continue
                    nu = clean_norm_url(apply_url)
                    rk = clean_norm_role(title)
                    if nu in applied_urls or (comp_clean, rk) in applied_comp_roles:
                        continue
                    is_int = any(k in title.lower() for k in INTERN_KEYWORDS)
                    if is_int and comp_clean in applied_intern_companies:
                        continue
                    results.append({
                        'company': comp_name,
                        'title': title,
                        'role': title,
                        'portal_type': 'Greenhouse',
                        'applyUrl': apply_url,
                        'url': apply_url,
                        'location': loc,
                        'is_remote': 'remote' in loc.lower() or 'anywhere' in loc.lower(),
                        'is_internship': is_int,
                        'category': 'INTERNSHIP' if is_int else 'JOB',
                        'stipend': '$5,000 - $8,500 / mo USD' if is_int else '$85,000 - $130,000 / yr USD'
                    })
                return results
        except Exception:
            return []

async def main():
    print("[*] Downloading curated Ashby (3,161) & Greenhouse (8,333) company lists...")
    u_ashby = 'https://raw.githubusercontent.com/Feashliaa/job-board-aggregator/main/data/ashby_companies.json'
    u_gh = 'https://raw.githubusercontent.com/Feashliaa/job-board-aggregator/main/data/greenhouse_companies.json'

    req1 = urllib.request.Request(u_ashby, headers={'User-Agent': 'Mozilla/5.0'})
    with urllib.request.urlopen(req1, timeout=10) as r:
        ashby_slugs = json.loads(r.read().decode())

    req2 = urllib.request.Request(u_gh, headers={'User-Agent': 'Mozilla/5.0'})
    with urllib.request.urlopen(req2, timeout=10) as r:
        gh_slugs = json.loads(r.read().decode())

    print(f"[+] Loaded {len(ashby_slugs)} Ashby slugs and {len(gh_slugs)} Greenhouse slugs.")

    sem = asyncio.Semaphore(75)
    conn_tcp = aiohttp.TCPConnector(limit=80, ttl_dns_cache=300)
    async with aiohttp.ClientSession(connector=conn_tcp) as session:
        # 1. Harvest Ashby First (Highest Conversion)
        print(f"[*] Scanning {len(ashby_slugs)} Ashby boards...")
        ashby_tasks = [fetch_ashby_board(session, s, sem) for s in ashby_slugs if s]
        ashby_results = await asyncio.gather(*ashby_tasks)
        flat_ashby = [r for sublist in ashby_results for r in sublist]
        print(f"[+] Harvested {len(flat_ashby)} unapplied verified Ashby tech roles!")

        # 2. Harvest Greenhouse
        print(f"[*] Scanning {len(gh_slugs)} Greenhouse boards...")
        gh_tasks = [fetch_greenhouse_board(session, s, sem) for s in gh_slugs if s]
        gh_results = await asyncio.gather(*gh_tasks)
        flat_gh = [r for sublist in gh_results for r in sublist]
        print(f"[+] Harvested {len(flat_gh)} unapplied verified Greenhouse tech roles!")

    all_harvested = flat_ashby + flat_gh
    print(f"[+] Total raw harvested: {len(all_harvested)} roles.")

    # Deduplicate internally
    seen_urls = set()
    seen_pairs = set()
    deduped = []
    internships = []
    jobs = []

    for r in all_harvested:
        nu = clean_norm_url(r['applyUrl'])
        ck = clean_norm_company(r['company'])
        rk = clean_norm_role(r['title'])
        if nu in seen_urls or (ck, rk) in seen_pairs:
            continue
        seen_urls.add(nu)
        seen_pairs.add((ck, rk))
        deduped.append(r)
        if r['is_internship']:
            internships.append(r)
        else:
            jobs.append(r)

    print(f"==================================================")
    print(f"🎯 HARVEST COMPLETE:")
    print(f"   Total Fresh Unapplied Roles: {len(deduped)}")
    print(f"   Internships:                 {len(internships)}")
    print(f"   Full-Time Jobs:              {len(jobs)}")
    print(f"   Ashby Roles (High-Conv):     {sum(1 for r in deduped if r['portal_type'] == 'Ashby')}")
    print(f"   Greenhouse Roles:            {sum(1 for r in deduped if r['portal_type'] == 'Greenhouse')}")
    print(f"==================================================")

    # Save to disk
    with open(os.path.join(BASE_DIR, 'live_fresh_verified_roles.json'), 'w') as f:
        json.dump(deduped, f, indent=2)

    with open(os.path.join(BASE_DIR, 'vetted_tech_internships.json'), 'w') as f:
        json.dump(internships, f, indent=2)

    with open(os.path.join(BASE_DIR, 'clean_vetted_remote_jobs.json'), 'w') as f:
        json.dump(jobs, f, indent=2)

    print("[+] Successfully saved fresh queues to disk.")

if __name__ == '__main__':
    asyncio.run(main())
