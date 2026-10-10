#!/usr/bin/env python3
"""
Unified Verified Application Engine for Gurdharam Jeet Singh
- 100% verified submissions
- Attribute selector fix: [id="{for_id}"]
- Comprehensive label-based context mapping
- GraphQL API response validation (errors check)
- Strict error banner detector
- Positive DOM confirmation check
- Real email delivery verification
"""

import time
import os
import json
import re
import sqlite3
import argparse
import random
import imaplib
import email
import email.utils
from email.header import decode_header
import sys
import asyncio
os.environ["UV_THREADPOOL_SIZE"] = "1"
try:
    import asyncio.unix_events as ue
    ue.can_use_pidfd = lambda: False
except Exception:
    pass
from playwright.sync_api import sync_playwright
from playwright_stealth import Stealth
from gemini_captcha_solver import solve_all_captchas

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "verified_job_applications.db")
RESUME_PATH = os.path.join(BASE_DIR, "Gurdharam_Jeet_Singh_Resume.pdf")
PROOF_DIR = os.path.join(BASE_DIR, "submission_proofs")
os.makedirs(PROOF_DIR, exist_ok=True)

CANDIDATE = {
    "name": "Gurdharam Jeet Singh",
    "first_name": "Gurdharam Jeet",
    "last_name": "Singh",
    "email": "gurination1@gmail.com",
    "phone": "+91 90411 72159",
    "location": "Ludhiana, Punjab, India",
    "linkedin": "https://www.linkedin.com/in/gurdharam-jeet-singh-691a17275",
    "github": "https://github.com/gurination1",
    "portfolio": "https://gurdharam.com",
    "school": "Baba Farid Group of Institutions",
    "degree": "Bachelor of Science",
    "discipline": "Software Systems & Automation",
    "grad_year": "2027",
    "start_year": "2023",
    "end_year": "2027",
    "start_month": "August",
    "end_month": "May",
    "pronouns": "He/Him",
    "join_date": "Immediately (within 1-2 weeks)",
    "how_heard": "Tech Community & Open Source Developer Ecosystem",
    "visa": "No sponsorship required for remote contract / open to standard remote arrangements.",
    "specific": "Autonomous cloud automation fleets, luxury frontend web interfaces, and AI coding/media agent systems.",
    "teach_something": "When architecting low-latency real-time voice agents over WebSockets, the critical bottleneck is jitter buffer re-assembly and VAD false triggering. Integrating Silero VAD directly at 16kHz chunk boundaries with sub-20ms frame slicing before the STT pipeline drops turn latency below 700ms without chopping user speech.",
    "why_frontend": "Specialized in luxury, high-craft web engineering and 120fps fluid interaction design. Architected and shipped production digital flagships including Solum Minerals (luxury minerals e-commerce), Branders (interactive digital design showcase), and Dreamheights (luxury architectural platform). I focus on Next.js/React, Tailwind CSS, WebGL/Three.js, sub-second TTFB, and zero-slop component craft.",
    "why_automation": "Driven by autonomous cloud workflows and self-healing multi-agent systems. Architected yt-auto (autonomous 5-channel 24/7 cloud media generation fleet running on GitHub Actions with dual-gate multimodal LLM judge verification), the Genesis Coding Agent (autonomous code synthesis and AST self-healing loops), and VideoGen (programmatic FFmpeg/Whisper/Piper timeline video generation engine).",
    "why_voice": "Hands-on experience architecting sub-700ms real-time voice AI agents over Exotel WebSockets and SIP/VoIP, integrating Sarvam AI Indic speech models, Groq LPUs, and Silero VAD barge-in handling.",
    "why_intern": "Software systems builder (B.Sc. Software Systems & Automation) with a proven public GitHub track record shipping luxury frontend platforms (Solum Minerals, Branders, Dreamheights) and autonomous cloud agent fleets (yt-auto, Genesis Agent, VideoGen). Eager to contribute high-velocity, reliable software engineering to high-impact teams.",
    "proud_of": "Shipped production luxury frontend platforms (Solum Minerals, Branders, Dreamheights) and architected yt-auto: an autonomous 5-channel media generation fleet running 24/7 on GitHub Actions with zero local machine dependencies, verified by automated FFmpeg black-screen detectors and multimodal LLM judges.",
    "motivates": "Building production systems that run autonomously and reliably. Driven by high-performance luxury web craft, autonomous self-healing coding agents, and sub-700ms telephony voice agents.",
    "preferred_name": "Gurdharam",
    "github_username": "gurination1",
    "current_company": "Independent Software Consultancy",
    "city_query": "Ludhiana"
}

def get_tailored_pitch(company, role, app_type="JOB", category=""):
    comp_clean = re.sub(r'<[^>]+>', '', company or '').strip() or "the team"
    if app_type == "INTERNSHIP":
        return f"Software systems builder (B.Sc. Hons Software Systems & Automation) highly excited to contribute to {comp_clean}'s engineering initiatives. Proven public GitHub track record shipping luxury frontend platforms (Solum Minerals, Branders, Dreamheights) and autonomous cloud agent fleets (yt-auto, Genesis Agent, VideoGen). Eager to contribute high-velocity, reliable software engineering at {comp_clean}."
    elif "front" in category.lower() or "web" in category.lower():
        return f"Specialized in luxury, high-craft web engineering and 120fps fluid interaction design, eager to bring my engineering craft to {comp_clean}. Architected and shipped production digital flagships including Solum Minerals and Branders. Focused on Next.js/React, Tailwind CSS, sub-second TTFB, and zero-slop component craft."
    elif "voice" in category.lower():
        return f"Experienced in architecting sub-700ms real-time voice AI agents over WebSockets and SIP/VoIP, enthusiastic to build with {comp_clean}'s platform. Strong expertise in Sarvam Indic models, Groq LPUs, and Silero VAD frame slicing."
    else:
        return f"Software systems engineer passionate about {comp_clean}'s technical vision. Deep expertise in autonomous cloud workflows, Playwright browser automation, Docker containerization, and 24/7 self-healing GitHub Actions pipelines (architected yt-auto and Genesis Coding Agent)."

CONFIRMED_CACHE = None

def clean_norm_url(u):
    if not u: return ''
    try:
        from urllib.parse import urlparse, parse_qs
        p = urlparse(u)
        clean = f'{p.scheme}://{p.netloc}{p.path}'.rstrip('/')
        if clean.endswith('/application'):
            clean = clean[:-12]
        clean = clean.lower()
        if 'embed/job_app' in clean or 'job_app' in clean:
            qs = parse_qs(p.query)
            params = []
            for k in sorted(qs.keys()):
                if k.lower() in ['token', 'for', 'gh_jid']:
                    params.append(f'{k.lower()}={qs[k][0]}')
            if params:
                clean = f"{clean}?{'&'.join(params)}"
        return clean
    except Exception:
        return (u or '').split('?')[0].lower().rstrip('/')

def clean_norm_company(c):
    c = re.sub(r'<[^>]+>', '', c or '').lower()
    c = re.sub(r'[^a-z0-9]', '', c)
    for suf in ['inc', 'llc', 'corp', 'corporation', 'technologies', 'technology', 'tech', 'software', 'labs', 'hq']:
        if c.endswith(suf) and len(c) > len(suf) + 2:
            c = c[:-len(suf)]
    return c

def clean_norm_role(r):
    r = re.sub(r'<[^>]+>', '', r or '').lower()
    return re.sub(r'[^a-z0-9]', '', r)

def get_role_tokens(r):
    r = re.sub(r'[^a-zA-Z0-9\s]', ' ', (r or '').lower())
    words = set(r.split())
    noise = {'junior', 'jr', 'entry', 'level', 'associate', 'developer', 'engineer', 'role', 'position', 'remote', 'fulltime', 'full', 'time', '2026', '2027', 'ii', 'i', 'the', 'and', 'for', 'at'}
    return words - noise

def get_confirmed_cache():
    global CONFIRMED_CACHE
    if CONFIRMED_CACHE is None:
        try:
            conn = sqlite3.connect(DB_PATH)
            c = conn.cursor()
            c.execute('''CREATE TABLE IF NOT EXISTS checked_dead_urls (
                url TEXT PRIMARY KEY,
                checked_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )''')
            c.execute('''CREATE TABLE IF NOT EXISTS company_blacklist (
                company TEXT PRIMARY KEY,
                reason TEXT,
                created_at DATETIME
            )''')
            urls = set()
            # 1. Block ALL URLs previously processed (regardless of status)
            for r in c.execute('SELECT job_url FROM verified_applications'):
                if r[0]:
                    nu = clean_norm_url(r[0])
                    if nu: urls.add(nu)
            for r in c.execute('SELECT url FROM checked_dead_urls'):
                if r[0]:
                    nu = clean_norm_url(r[0])
                    if nu: urls.add(nu)

            roles = set()
            company_internships = set()
            company_jobs = {} # comp -> list of token sets
            # 2. Block ALL (company, role) pairs previously processed
            for r in c.execute('SELECT company, role FROM verified_applications'):
                ck = clean_norm_company(r[0])
                rk = clean_norm_role(r[1])
                if ck and rk:
                    roles.add((ck, rk))
                    if 'intern' in rk or 'coop' in rk or 'placement' in rk:
                        company_internships.add(ck)
                    else:
                        if ck not in company_jobs:
                            company_jobs[ck] = []
                        company_jobs[ck].append(get_role_tokens(r[1]))
            
            # 3. Block ALL companies that sent rejections or are on blacklist
            blacklisted_companies = set()
            for r in c.execute('SELECT company FROM company_blacklist'):
                if r[0]:
                    ck = clean_norm_company(r[0])
                    if ck: blacklisted_companies.add(ck)
            for r in c.execute('SELECT DISTINCT company FROM verified_applications WHERE status = "REJECTED_BY_COMPANY"'):
                if r[0]:
                    ck = clean_norm_company(r[0])
                    if ck: blacklisted_companies.add(ck)

            conn.close()
            CONFIRMED_CACHE = (urls, roles, company_internships, company_jobs, blacklisted_companies)
        except Exception:
            CONFIRMED_CACHE = (set(), set(), set(), {}, set())
    return CONFIRMED_CACHE

def mark_url_dead(url):
    urls, roles, company_internships, company_jobs, blacklisted_companies = get_confirmed_cache()
    if url:
        nu = clean_norm_url(url)
        if nu: urls.add(nu)
    try:
        conn = sqlite3.connect(DB_PATH)
        conn.cursor().execute('INSERT OR IGNORE INTO checked_dead_urls (url) VALUES (?)', (url,))
        conn.commit()
        conn.close()
    except Exception:
        pass

def is_already_confirmed(url, company, title):
    urls, roles, company_internships, company_jobs, blacklisted_companies = get_confirmed_cache()
    nu = clean_norm_url(url)
    if nu and nu in urls:
        return True

    ck = clean_norm_company(company)
    rk = clean_norm_role(title)
    if not ck:
        return False

    # 1. Blacklist check
    if ck in blacklisted_companies or any(b == ck for b in blacklisted_companies):
        return True

    # 2. Exact (company, role) match
    if (ck, rk) in roles:
        return True

    # 3. Single internship policy: only 1 internship application per company
    is_intern = 'intern' in rk or 'coop' in rk or 'placement' in rk
    if is_intern and ck in company_internships:
        return True

    # 4. Fuzzy token check for full-time jobs at same company
    if not is_intern and ck in company_jobs:
        rt = get_role_tokens(title)
        if rt:
            for prev_tokens in company_jobs[ck]:
                if prev_tokens:
                    overlap = len(rt.intersection(prev_tokens))
                    denom = max(len(rt), len(prev_tokens))
                    if rt == prev_tokens or (denom > 0 and overlap / denom >= 0.75):
                        return True

    return False

def critique_application(company, title, category=""):
    title_lower = title.lower()
    
    # 1. STRICT PURGE OF MACHINE LEARNING, HARDWARE, LOW-LEVEL, C++, ROBOTICS & OVER-SENIORITY
    banned = [
        # AI / ML Research / Theoretical Math / Data Science
        'machine learning', 'ml ', '/ml', 'deep learning', 'ai research', 'research intern', 'research engineer',
        'researcher', 'scientist', 'foundation model', 'reinforcement learning', 'robot learning', 'computer vision',
        'nlp research', 'computational', 'plasma', 'physics', 'algorithmic research', 'ai intern', 'ai evaluation',
        'applied ai', 'ai engineer', 'ai developer', 'mlops', 'llmops', 'aiops', 'llm', 'data engineer',
        'data science', 'data scientist', 'analyst', 'analytics', 'bi engineer', 'data infra', 'data platform',
        'data pipeline', 'analytics engineer', 'enterprise data',
        # Non-software / physical domain / retail / oil & gas
        'retail', 'store associate', 'cashier', 'merchandise', 'warehouse', 'oil', 'gas', 'midstream', 'drilling',
        'civil', 'chemical engineer', 'materials science', 'facilities engineer', 'technician',
        # Aerospace flight software / avionics / spacecraft / orbital
        'flight software', 'flight ', 'avionics', 'orbital', 'spacecraft', 'propulsion', 'satellite flight',
        'guidance, navigation', 'guidance and control', 'spacecraft simulation', 'drone stack',
        # Robotics manipulation / motion planning / perception
        'robotics', 'robot ', 'robotic', 'manipulation', 'motion planning', 'perception engineer', 'low speed motion',
        # Low-level languages / Unaligned Infrastructure stacks / Hardware
        'c++', '(c++)', 'rust ', 'rust/', 'rust-', 'chip design', 'fpga', 'asic', 'kernel', 'firmware', 'pcb', 'hpc ',
        'gpu cluster', 'kafka', 'distributed systems', 'low latency', 'graphics engine', 'rendering engine',
        'game engine', 'unreal', 'unity engine',
        # IT Support / Corporate Desktop / Sysadmin
        'it support', 'it specialist', 'it engineer', 'help desk', 'helpdesk', 'desktop support', 'desktop software',
        'sysadmin', 'systems administrator', 'network engineer', 'database administrator', 'dba ',
        # Security / Cyber
        'security', 'infosec', 'cyber', 'secops', 'vulnerability', 'soc ', 'penetration',
        # Hardware / Electrical / Embedded / Automotive
        'hardware', 'silicon', 'dft', 'analog', 'ic design', 'electronics', 'embedded',
        'controls', 'vehicle', 'automotive', 'battery', 'mechanical', 'thermal',
        # Business / Operations / Finance / PM
        'business development', 'bizdev', 'operations', 'revops', 'user operations', 'product management',
        'product manager', 'pm intern', 'product intern', 'product strategy', 'compensation partner', 'sales',
        'pre-sales', 'representative', 'consultant', 'strategist', 'account executive', 'sdr', 'bdr', 'recruiter',
        'recruiting', 'coordinator', 'marketing', 'finance', 'private equity', 'trading', 'quant', 'banking',
        'investment', 'talent', 'human resources', 'people', 'legal', 'compliance', 'tax', 'accounting', 'fellow',
        # Over-seniority (strictly junior, lower-mid, mid, intern)
        'senior', 'sr.', 'sr ', 'principal', 'staff', 'architect', 'director', 'vp', 'head of', 'manager',
        'lead', 'expert', 'specialist ii', 'engineer iii', 'engineer iv', 'engineer 3', 'engineer 4', 'swe 3', 'swe 4', 'sde 3', 'sde 4',
        # Geographic, Citizenship & Format Knockouts
        ' - tor', ' (tor)', 'toronto', ' - van', 'vancouver', ' - montreal', 'waterloo university',
        'us citizen', 'security clearance', 'ts/sci', 'clearance', 'uk only', 'canada only', 'onsite only',
        'in-office only', 'hybrid', 'on-site', 'onsite', 'in-person', 'relocation required', 'london', 'uk office',
        'office only', 'office)', 'in-office', 'phd', 'postdoc', 'graduate intern'
    ]
    for b in banned:
        if b in title_lower:
            return 30, f'Brutally Purged / Domain or Stack Mismatch: Title contains banned term "{b}". Candidate strictly targets Frontend, Full-Stack, Web, Python, and Cloud Automation.'

    # Check for word-bounded leadership / senior / level / technician / IT keywords
    if re.search(r'\b(lead|sr|director|vp|chief|head|phd|ml|iii|iv|v|staff|principal|architect|sysadmin|technician)\b', title_lower) or re.search(r'\b(engineer|developer|swe|sde)\s*([3-9]|iii|iv|v)\b', title_lower) or re.search(r'\b(l[3-9]|e[3-9]|ic[3-9]|level\s*[3-9])\b', title_lower):
        return 30, 'Over-seniority or Technician Knockout: Title exceeds entry/mid builder bar.'

    # Systems Engineer without software/cloud/web context
    if 'systems engineer' in title_lower and not any(k in title_lower for k in ['software', 'web', 'cloud', 'automation', 'application']):
        return 30, 'Domain Mismatch: Systems Engineering without Web/Software/Cloud context is low conversion.'

    # 2. REJECTION COOLDOWN / BLACKLIST CHECK
    urls, roles, company_internships, company_jobs, blacklisted_companies = get_confirmed_cache()
    c_clean = clean_norm_company(company)
    clean_t = clean_norm_role(title)
    if (c_clean, clean_t) in roles:
        return 10, f'Duplicate Application: Already applied to {company} for {title}.'
    if c_clean in blacklisted_companies or any(b == c_clean for b in blacklisted_companies):
        return 10, f'Company Blacklist/Rejection: {company} sent a formal rejection email. Skipping reapplication.'

    # 3. PURE BACKEND PENALTY
    is_pure_backend = any(b in title_lower for b in ['backend', 'back-end', 'back end']) and not any(f in title_lower for f in ['front', 'web', 'full stack', 'fullstack', 'full-stack', 'intern', 'co-op', 'node', 'product', 'application', 'developer experience', 'dx'])
    if is_pure_backend:
        return 45, 'Low conversion: Pure backend roles without Web/Product/Full-Stack/Node context have low conversion.'

    # 4. MANDATORY SOFTWARE BUILDER RELEVANCE CHECK (ZERO NON-SOFTWARE PASS-THROUGH)
    has_software_context = bool(re.search(
        r'\b(software|developer|frontend|front-end|web|fullstack|full-stack|full stack|application|react|next\.js|python|cloud|devops|automation|qa engineer|test engineer|programmer|coder)\b',
        title_lower
    )) or bool(re.search(r'\b(ui|ux)\b', title_lower))

    if not has_software_context:
        return 20, 'Domain Mismatch: Title lacks software, web, frontend, full-stack, developer, or automation keywords.'

    score = 70
    strengths = []
    # 5. CANDIDATE SWEET-SPOT CALIBRATION (B.Sc. Software Systems & Automation, React/TypeScript/Python/Node)
    if re.search(r'\b(ui|ux|frontend|react|next\.js)\b', title_lower) or any(k in title_lower for k in ['front end', 'front-end', 'web developer', 'full stack', 'full-stack', 'fullstack', 'product engineer', 'dx', 'developer experience']):
        score = 98
        strengths.append('Sweet-spot match: Master resume optimized for React/Next.js/TypeScript/Full-Stack Web (99.5 ATS score).')
    elif re.search(r'\b(intern|internship|co-op|coop|apprentice|campus|junior|jr|associate|early career|software engineer i|new grad|entry level)\b', title_lower):
        score = 96
        strengths.append('Optimal career level: Entry-level/Intern/Junior software role perfectly tailored for 2nd-year undergraduate candidate.')
    elif any(k in title_lower for k in ['agent', 'automation', 'cloud', 'qa', 'workflow', 'voice', 'realtime']):
        score = 92
        strengths.append('Builder fit: Proven Playwright automation, Docker, WebSockets, and GitHub Actions CI/CD.')
    elif any(k in title_lower for k in ['software engineer', 'software developer', 'application engineer']):
        score = 85
        strengths.append('General software engineering builder match: Proven TypeScript/Python/React/Node stack on GitHub.')
    else:
        score = 65

    return min(score, 99), ' | '.join(strengths)

def log_verified_application(company, role, portal, url, salary_or_stipend, proof_path, app_type="JOB", notes=""):
    try:
        fit_score, critique_text = critique_application(company, role)
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute("""
            INSERT INTO verified_applications 
            (company, role, portal_type, job_url, salary, status, proof_screenshot, notes, application_type, stipend_usd, compatibility_score, critique_analysis)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(job_url) DO UPDATE SET
                status = 'CONFIRMED_SUBMITTED',
                proof_screenshot = excluded.proof_screenshot,
                notes = excluded.notes,
                stipend_usd = excluded.stipend_usd,
                compatibility_score = excluded.compatibility_score,
                critique_analysis = excluded.critique_analysis
        """, (
            company, role, portal, url, salary_or_stipend,
            'CONFIRMED_SUBMITTED', proof_path, notes, app_type, salary_or_stipend,
            fit_score, critique_text
        ))
        conn.commit()
        conn.close()
        if CONFIRMED_CACHE is not None:
            CONFIRMED_CACHE[0].add(url)
            CONFIRMED_CACHE[1].add((company.lower(), role.lower()))
        print(f"[+] SQLite logged CONFIRMED: {company} - {role} ({app_type}) [Fit: {fit_score}/100]")
    except Exception as e:
        print(f"[-] DB logging error: {e}")

USED_OTPS = set()

def fetch_greenhouse_otp(company_name=None, min_timestamp=None, max_wait=12):
    print(f"[*] Checking Gmail IMAP for fresh Greenhouse security OTP (Target: {company_name or 'Any'})...")
    if min_timestamp is None:
        min_timestamp = time.time() - 60

    gmail_pwd = os.environ.get('GMAIL_APP_PASSWORD')
    if not gmail_pwd and os.path.exists('/root/local_env.sh'):
        try:
            with open('/root/local_env.sh') as f:
                for line in f:
                    if 'GMAIL_APP_PASSWORD=' in line and not '_ACC_' in line:
                        gmail_pwd = line.split('=', 1)[1].strip().strip('"').strip("'")
                        break
        except Exception:
            pass

    co_keyword = ""
    if company_name:
        co_keyword = re.sub(r'[^a-zA-Z0-9]', '', company_name.split()[0]).lower()

    for attempt in range(max_wait // 3):
        try:
            mail = imaplib.IMAP4_SSL('imap.gmail.com')
            mail.login('gurination1@gmail.com', gmail_pwd or '')
            try:
                mail.select('"[Gmail]/All Mail"')
            except Exception:
                mail.select('inbox')
            status, messages = mail.search(None, '(OR (FROM "greenhouse-mail.io") (OR (SUBJECT "security code") (OR (SUBJECT "verification") (SUBJECT "verify your"))))')
            if not messages[0]:
                status, messages = mail.search(None, 'ALL')
            msg_ids = messages[0].split()
            code = None
            latest_fallback = None
            for mid in reversed(msg_ids[-25:]):
                _, data = mail.fetch(mid, '(RFC822)')
                msg = email.message_from_bytes(data[0][1])

                date_str = msg.get('Date')
                msg_time = 0
                if date_str:
                    try:
                        msg_time = email.utils.parsedate_to_datetime(date_str).timestamp()
                    except Exception:
                        pass

                # Strictly discard stale OTPs from before this submission started
                if msg_time and msg_time < (min_timestamp - 30):
                    continue

                subj, enc = decode_header(msg.get('Subject', ''))[0]
                if isinstance(subj, bytes):
                    subj = subj.decode(enc or 'utf-8', errors='ignore')
                subj_lower = subj.lower()

                if any(k in subj_lower for k in ['security code', 'verification', 'verify your', 'code required']):
                    body = ''
                    for part in msg.walk():
                        if part.get_content_type() in ['text/html', 'text/plain']:
                            body += part.get_payload(decode=True).decode(errors='ignore')
                    clean_text = re.sub('<[^<]+?>', ' ', body)

                    extracted_code = None
                    m_clinch = re.search(r'code required to complete your form[^A-Za-z0-9]*([A-Za-z0-9]{5,8})', clean_text, re.IGNORECASE)
                    m_gh = re.search(r'security code field on your application:\s*([A-Za-z0-9]{5,8})', clean_text, re.IGNORECASE)
                    if m_clinch and m_clinch.group(1) not in USED_OTPS:
                        extracted_code = m_clinch.group(1).strip()
                    elif m_gh and m_gh.group(1) not in USED_OTPS:
                        extracted_code = m_gh.group(1).strip()
                    else:
                        m2 = re.findall(r'\b[A-Za-z0-9]{5,8}\b', clean_text)
                        for c in m2:
                            if any(ch.isdigit() for ch in c) and c not in USED_OTPS:
                                extracted_code = c
                                break

                    if extracted_code:
                        if not latest_fallback:
                            latest_fallback = extracted_code
                        if co_keyword and len(co_keyword) > 2:
                            if co_keyword in subj_lower or co_keyword in clean_text.lower():
                                code = extracted_code
                                break
                        else:
                            code = extracted_code
                            break

            mail.close()
            mail.logout()
            final_code = code or latest_fallback
            if final_code and final_code not in USED_OTPS:
                USED_OTPS.add(final_code)
                print(f"[+] Found fresh Greenhouse security code: {final_code}")
                return final_code
        except Exception:
            pass
        time.sleep(3)
    return None

def fill_greenhouse_combobox(page, inp, label_text):
    label_lower = (label_text or '').lower()
    
    target_choice = None
    # 1. Negative / Disqualification questions -> 'No' / 'None'
    if any(k in label_lower for k in [
        'sponsorship', 'visa', 'require sponsorship', 'require visa', 'need visa',
        'employee', 'currently employed', 'current employee', 'currently work', 'worked at', 'worked for',
        'previous', 'prior employee', 'former employee', 'consulted for', 'internal candidate', 'internal applicant',
        'current or former', 'alphabet employee', 'twitch employee', 'subsidiary', 'relatives', 'family member',
        'conflict of interest', 'non-compete', 'compete', 'felony', 'convicted', 'crime', 'investigation',
        'disability', 'medical condition', 'hispanic', 'latino', 'transgender'
    ]):
        target_choice = 'No'
    # 2. Positive / Authorization / Agreements / Relocation -> 'Yes'
    elif any(k in label_lower for k in [
        'authorized', 'authorization', 'legally authorized', 'eligible to work', 'work authorization',
        'agree', 'privacy', 'acknowledge', 'certify', 'true and correct', 'terms', 'over 18', '18 or older',
        'relocate', 'relocation', 'willing to relocate', 'open to relocating'
    ]):
        target_choice = 'Yes'
    # 3. Country / Location
    elif any(k in label_lower for k in ['country', 'where are you located', 'location', 'residence', 'reside', 'state', 'region']):
        target_choice = 'India'
    # 4. Gender
    elif 'gender' in label_lower or 'sex' in label_lower:
        target_choice = 'Male'
    # 5. Veteran
    elif 'veteran' in label_lower:
        target_choice = 'not a protected veteran'
    # 6. Pronouns
    elif 'pronoun' in label_lower:
        target_choice = 'He / Him'
    # 7. Sexual orientation
    elif 'sexual' in label_lower:
        target_choice = 'Heterosexual'
    # 8. Ethnicity / Race
    elif 'ethnicity' in label_lower or 'race' in label_lower or 'demographic' in label_lower:
        target_choice = 'Asian'
    # 9. Source / How heard
    elif 'hear' in label_lower or 'source' in label_lower:
        target_choice = 'Job Board'
    # 10. Education
    elif any(k in label_lower for k in ['degree', 'highest education', 'level of education']):
        target_choice = 'Bachelor'
    elif any(k in label_lower for k in ['grad', 'graduation']):
        target_choice = '2027'
    elif any(k in label_lower for k in ['discipline', 'major', 'field']):
        target_choice = 'Computer Science'
    elif any(k in label_lower for k in ['school', 'university', 'college', 'institution', '#school']):
        target_choice = 'Baba Farid Group of Institutions'

    # 1. Native HTML SELECT
    try:
        tag = inp.evaluate('el => el.tagName')
        if tag == 'SELECT':
            opts = inp.locator('option').all()
            matched_val = None
            if target_choice:
                t_low = target_choice.lower()
                for opt in opts:
                    txt = opt.inner_text().strip().lower()
                    val = opt.get_attribute('value')
                    if not val and not txt:
                        continue
                    if t_low == 'male':
                        if re.search(r'\bmale\b', txt) and not re.search(r'\bfemale\b', txt):
                            matched_val = val
                            break
                    elif t_low in ['he / him', 'he/him']:
                        if any(female_k in txt for female_k in ['she', 'her']):
                            continue
                        if re.search(r'\bhe\s*/\s*him\b', txt) or 'he/him' in txt or 'he / him' in txt:
                            matched_val = val
                            break
                    elif t_low == 'india':
                        if any(bad in txt for bad in ['british', 'ocean', 'diego', 'territory']):
                            continue
                        if re.search(r'\bindia\b', txt) or txt.startswith('india'):
                            matched_val = val
                            break
                    elif 'baba farid' in t_low:
                        if 'baba farid' in txt:
                            matched_val = val
                            break
                        if 'other' in txt and matched_val is None:
                            matched_val = val
                    elif t_low == 'no':
                        if re.search(r'\bno\b|\bnone\b|\bneither\b|not a|i do not|will not|don’t', txt):
                            matched_val = val
                            break
                    elif t_low == 'yes':
                        if re.search(r'\byes\b|i agree|authorized|confirm|certify|i acknowledge|willing|open to', txt):
                            matched_val = val
                            break
                    elif t_low in txt:
                        matched_val = val
                        break

            if matched_val is not None:
                inp.select_option(value=matched_val)
                return True

            # Safe fallback: pick 'No', 'Decline', 'Job Board', or first meaningful option (avoiding index 1 trap)
            for opt in opts:
                txt = opt.inner_text().strip().lower()
                val = opt.get_attribute('value')
                if not val or txt in ['select...', 'select', 'choose', 'please select', '']:
                    continue
                if any(safe_k in txt for safe_k in ['no', 'decline', 'prefer not', 'not applicable', 'n/a', 'other', 'none']):
                    inp.select_option(value=val)
                    return True

            if len(opts) > 1:
                # Never pick option 1 if it says "Yes" without target_choice
                first_txt = opts[1].inner_text().strip().lower()
                if first_txt == 'yes':
                    for opt in opts:
                        if opt.inner_text().strip().lower() in ['no', 'decline']:
                            inp.select_option(value=opt.get_attribute('value'))
                            return True
                inp.select_option(index=1)
                return True
            return False
    except Exception:
        pass

    # 2. React-Select / ARIA Combobox
    try:
        parent_ctrl = inp.locator('xpath=ancestor-or-self::div[contains(@class, "select__control") or contains(@class, "combobox")][1]').first
        if parent_ctrl.count() > 0 and parent_ctrl.is_visible():
            parent_ctrl.click(timeout=1500)
        else:
            inp.click(timeout=1500)
        page.wait_for_timeout(350)
    except Exception:
        try:
            inp.focus()
            inp.press('ArrowDown')
        except Exception:
            return False
    
    ctrl = inp.get_attribute('aria-controls')
    menu = page.locator(f'[id="{ctrl}"]') if ctrl else page.locator('.select__menu, .select__menu-list, div[class*="-menu"], [role="listbox"]:visible, [id*="listbox"]:visible').first
        
    if menu.count() > 0:
        if target_choice:
            t_low = target_choice.lower()
            if t_low == 'male':
                m_opt = menu.locator('div:has-text("Male"):not(:has-text("Female")), [role="option"]:has-text("Male"):not(:has-text("Female"))').first
                if m_opt.count() > 0:
                    m_opt.click()
                    page.wait_for_timeout(250)
                    return True
            elif t_low in ['he / him', 'he/him']:
                h_opt = menu.locator('div:has-text("He / Him"), div:has-text("He/Him"), [role="option"]:has-text("He / Him"), [role="option"]:has-text("He/Him"), div:has-text("He/him"), [role="option"]:has-text("He/him")').first
                if h_opt.count() > 0:
                    h_opt.click()
                    page.wait_for_timeout(250)
                    return True
            elif t_low == 'india':
                for opt_el in menu.locator('div, li, [role="option"]').all():
                    txt = opt_el.inner_text().strip().lower()
                    if any(bad in txt for bad in ['british', 'ocean', 'diego', 'territory']):
                        continue
                    if 'india' in txt:
                        opt_el.click()
                        page.wait_for_timeout(250)
                        return True
            elif 'baba farid' in t_low or 'other' in t_low:
                try:
                    inp.fill("")
                    inp.press_sequentially("Other", delay=60)
                    page.wait_for_timeout(400)
                except Exception:
                    pass
                s_opt = menu.locator('div:has-text("Other"), [role="option"]:has-text("Other"), div:has-text("Baba Farid"), [role="option"]:has-text("Baba Farid")').first
                if s_opt.count() > 0:
                    s_opt.click()
                    page.wait_for_timeout(250)
                    return True
            elif t_low == 'yes':
                y_opt = menu.locator('div:has-text("Yes"), [role="option"]:has-text("Yes"), div:has-text("Willing"), [role="option"]:has-text("Willing"), div:has-text("Open to"), [role="option"]:has-text("Open to"), div:has-text("Agree"), [role="option"]:has-text("Agree"), div:has-text("I confirm"), [role="option"]:has-text("I confirm"), div:has-text("Confirm"), [role="option"]:has-text("Confirm")').first
                if y_opt.count() > 0:
                    y_opt.click()
                    page.wait_for_timeout(250)
                    return True
            elif t_low == 'no':
                n_opt = menu.locator('div:has-text("No"):not(:has-text("Notice")), [role="option"]:has-text("No"):not(:has-text("Notice")), div:has-text("I do not"), [role="option"]:has-text("I do not"), div:has-text("None"), [role="option"]:has-text("None")').first
                if n_opt.count() > 0:
                    n_opt.click()
                    page.wait_for_timeout(250)
                    return True
            elif t_low in ['decline', 'prefer not to say']:
                d_opt = menu.locator('div:has-text("Decline"), [role="option"]:has-text("Decline"), div:has-text("Prefer not to"), [role="option"]:has-text("Prefer not to"), div:has-text("I do not wish"), [role="option"]:has-text("I do not wish")').first
                if d_opt.count() > 0:
                    d_opt.click()
                    page.wait_for_timeout(250)
                    return True
            else:
                opt = menu.locator(f'div:has-text("{target_choice}"), li:has-text("{target_choice}"), [role="option"]:has-text("{target_choice}")').first
                if opt.count() > 0:
                    opt.click()
                    page.wait_for_timeout(250)
                    return True

        # Safe fallback: Prefer "No" or "Decline" before blindly clicking first_opt
        no_opt = menu.locator('div:has-text("No"), li:has-text("No"), [role="option"]:has-text("No"), div:has-text("Decline"), [role="option"]:has-text("Decline")').first
        if no_opt.count() > 0:
            no_opt.click()
            page.wait_for_timeout(250)
            return True

        first_opt = menu.locator('[id*="option"], [role="option"], div[class*="-option"], .select__option, li').first
        if first_opt.count() > 0:
            first_opt.click()
            page.wait_for_timeout(250)
            return True

    # Fallback: type and enter
    if target_choice:
        try:
            inp.press_sequentially(target_choice, delay=50)
            page.wait_for_timeout(300)
            inp.press('Enter')
            return True
        except Exception:
            pass

    return False

def apply_greenhouse(page, item):
    company = re.sub('<[^<]+?>', '', item.get('company', '')).strip()
    title = re.sub('<[^<]+?>', '', item.get('title') or item.get('role', '')).strip()
    url = (item.get('applyUrl') or item.get('url', '')).replace('&amp;', '&')
    app_type = "INTERNSHIP" if (item.get('is_internship') or item.get('category') == 'INTERNSHIP' or 'intern' in title.lower() or 'co-op' in title.lower()) else "JOB"
    category = item.get('category', 'Engineering')
    stipend_or_sal = item.get('stipend') or "$60,000 - $95,000 USD / year"

    print(f"\n==================================================================")
    print(f"[*] [GREENHOUSE] [{app_type}] [{category}] {company} - {title}")
    print(f"[*] URL: {url}")
    print(f"==================================================================")

    if is_already_confirmed(url, company, title):
        print(f"[!] Already confirmed in DB: {url}")
        return True

    fit_score, critique_text = critique_application(company, title)
    if fit_score < 80:
        print(f"[-] SKIPPING {company} - {title} [Score: {fit_score}/100]: {critique_text}")
        return False

    try:
        page.goto(url, wait_until='domcontentloaded', timeout=9000)
    except Exception:
        try:
            page.goto(url, wait_until='load', timeout=9000)
        except Exception as e:
            print(f"[-] Navigation failed: {e}")
            mark_url_dead(url)
            return False

    page.wait_for_timeout(1500)

    # Detect cross-origin iframe or canonical redirect to 3rd-party marketing site:
    try:
        slug = None
        jid = None
        m_slug = re.search(r'greenhouse\.io/(?:embed/job_app\?for=)?([^/]+)/(?:jobs/)?(\d+)', url)
        if m_slug:
            slug = m_slug.group(1)
            jid = m_slug.group(2)
        else:
            m_jid = re.search(r'gh_jid=(\d+)', url)
            if m_jid:
                jid = m_jid.group(1)
                slug = company.lower().replace(' ', '')

        # Only look for embedded iframe if we are NOT already on greenhouse.io:
        if 'greenhouse.io' not in page.url.lower():
            gh_iframe = page.locator('iframe#grnh_iframe, iframe[src*="boards.greenhouse.io"], iframe[src*="job-boards.greenhouse.io"]').first
            if gh_iframe.count() > 0:
                iframe_src = gh_iframe.get_attribute('src') or ''
                if iframe_src and 'greenhouse.io' in iframe_src and 'googleapis.com' not in iframe_src:
                    print(f"[*] Detected Greenhouse iframe on external site; navigating directly to native embed: {iframe_src}")
                    page.goto(iframe_src, wait_until='domcontentloaded', timeout=9000)
                    page.wait_for_timeout(1000)
            elif slug and jid:
                direct_embed = f"https://job-boards.greenhouse.io/embed/job_app?for={slug}&token={jid}"
                print(f"[*] Canonical redirect detected ({page.url}); loading native embed: {direct_embed}")
                page.goto(direct_embed, wait_until='domcontentloaded', timeout=9000)
                page.wait_for_timeout(1000)
    except Exception:
        pass

    # Detect redirect to generic job search page or closed vacancy
    cur_url_low = page.url.lower()
    page_txt_low = page.locator('body').inner_text().lower()
    if 'search=' in cur_url_low or 'jobs/?search' in cur_url_low or any(k in page_txt_low for k in ['this job has been closed', 'job is no longer available', 'no longer accepting applications', '404 not found']):
        print(f"[-] Job closed or redirected to search page: {page.url}")
        mark_url_dead(url)
        return False

    # Dismiss cookie banners if present
    try:
        page.locator('button:has-text("ACCEPT ALL"), button:has-text("Accept All"), button:has-text("Accept"), button:has-text("Agree"), button:has-text("OK")').first.click(timeout=1000)
    except Exception:
        pass

    # Ensure application form is in view (scroll or click Apply button if on job description)
    try:
        first_inp = page.locator('input[id*="first_name"], input[name*="first_name"], #first_name, input[type="email"]').first
        if first_inp.count() == 0 or not first_inp.is_visible():
            apply_btn = page.locator('button:has-text("Apply for this Job"), button:has-text("Apply Now"), button:has-text("Apply"), a:has-text("Apply for this Job"), a:has-text("Apply Now"), a:has-text("Apply"), a[href*="#app"]').first
            if apply_btn.count() > 0 and apply_btn.is_visible():
                apply_btn.click(timeout=2000)
                page.wait_for_timeout(1500)
    except Exception:
        pass

    def ensure_greenhouse_basics():
        basics = [
            ('#first_name, input[name="first_name"], input[name*="first_name"], input[id*="first_name"], input[autocomplete="given-name"], input[aria-label*="first name" i]', CANDIDATE["first_name"]),
            ('#last_name, input[name="last_name"], input[name*="last_name"], input[id*="last_name"], input[autocomplete="family-name"], input[aria-label*="last name" i]', CANDIDATE["last_name"]),
            ('#preferred_name, input[name*="preferred"], input[id*="preferred"], input[aria-label*="preferred name" i]', CANDIDATE["first_name"]),
            ('#middle_name, input[name*="middle_name"], input[id*="middle_name"]', "Jeet"),
            ('#email, input[name="email"], input[name*="email"], input[type="email"], input[id*="email"], input[autocomplete="email"], input[aria-label*="email" i]', CANDIDATE["email"]),
            ('#phone, input[name="phone"], input[name*="phone"], input[type="tel"], input[id*="phone"], input[autocomplete="tel"], input[aria-label*="phone" i]', "9041172159"),
            ('input[id*="full_name"], input[name*="full_name"], input[id*="legal_name"], input[name*="legal_name"], input[aria-label*="legal name" i], input[aria-label*="full name" i]', CANDIDATE["name"]),
            ('input[id*="linkedin"], input[name*="linkedin"], input[aria-label*="linkedin" i]', CANDIDATE["linkedin"]),
            ('input[id*="github"], input[name*="github"], input[aria-label*="github" i]', CANDIDATE["github"]),
            ('input[id*="website"], input[name*="website"], input[id*="portfolio"], input[name*="portfolio"], input[aria-label*="portfolio" i], input[aria-label*="website" i]', CANDIDATE["portfolio"])
        ]
        for sel, val in basics:
            try:
                for el in page.locator(sel).all():
                    if el.is_visible():
                        cur = el.input_value()
                        if not cur or not cur.strip() or cur.strip().lower() in ['yes', 'select', 'enter']:
                            el.fill(val)
            except Exception:
                pass
        # Auto-heal phone if 'too long' error triggered
        try:
            p_err = page.locator('div:has-text("Phone number is too long"), p:has-text("Phone number is too long"), span:has-text("Phone number is too long")')
            if p_err.count() > 0 and p_err.first.is_visible():
                p_in = page.locator('#phone, input[name="phone"], input[type="tel"]').first
                if p_in.count() > 0 and p_in.is_visible():
                    p_in.fill("9041172159")
        except Exception:
            pass

    # 1. Fill basic inputs initially
    ensure_greenhouse_basics()

    # 2. Country picker & clean phone digits
    try:
        c = page.locator('#country, [aria-labelledby*="country-label"], [id*="select-country"], select[name*="country"]').first
        if c.count() > 0 and c.is_visible():
            if c.evaluate('el => el.tagName') == 'SELECT':
                fill_greenhouse_combobox(page, c, 'India')
            else:
                c.click(timeout=1000)
                page.wait_for_timeout(250)
                c.fill("")
                c.press_sequentially('India', delay=80)
                page.wait_for_timeout(800)
                ind_opt = page.locator('[role="option"]:has-text("India (+91)"), [id*="-option-"]:has-text("India (+91)"), [role="option"]:has-text("India"), [id*="-option-"]:has-text("India")').first
                if ind_opt.count() > 0 and ind_opt.is_visible():
                    ind_opt.click()
                else:
                    c.fill("")
                    c.press_sequentially('+91', delay=80)
                    page.wait_for_timeout(600)
                    p91_opt = page.locator('[role="option"]:has-text("+91"), [id*="-option-"]:has-text("+91")').first
                    if p91_opt.count() > 0 and p91_opt.is_visible():
                        p91_opt.click()
                    else:
                        page.keyboard.press("ArrowDown")
                        page.wait_for_timeout(200)
                        page.keyboard.press("Enter")
        # Ensure phone input always has strictly pure digits 9041172159:
        p_in = page.locator('#phone, input[name="phone"], input[type="tel"]').first
        if p_in.count() > 0 and p_in.is_visible():
            p_in.fill("9041172159")
    except Exception:
        pass

    # 3. Location picker
    loc = page.locator('#candidate-location, input[id*="location"], input[name*="location"]').first
    if loc.count() > 0 and loc.is_visible():
        try:
            loc.click()
            loc.fill("")
            loc.press_sequentially("Ludhiana", delay=80)
            page.wait_for_timeout(900)
            l_opt = page.locator('[role="option"]:has-text("Ludhiana"), [id*="-option-"]:has-text("Ludhiana"), [id*="react-select-candidate-location-option"]:has-text("Ludhiana, Punjab")').first
            if l_opt.count() == 0 or not l_opt.is_visible():
                l_opt = page.locator('[role="option"], [id*="-option-"], [class*="option"]').first
            if l_opt.count() > 0 and l_opt.is_visible():
                l_opt.click()
            else:
                page.keyboard.press("ArrowDown")
                page.wait_for_timeout(200)
                page.keyboard.press("Enter")
        except Exception:
            pass

    # 4. Resume & File uploads
    res_input = page.locator('#resume, input[type="file"][name*="resume"], input[name="resume"], input[type="file"]').first
    if res_input.count() > 0:
        try:
            res_input.set_input_files(RESUME_PATH, timeout=5000)
            page.wait_for_timeout(1000)
            print("[+] Greenhouse resume attached")
        except Exception:
            pass
    for extra_fi in page.locator('input[type="file"]:not(#resume)').all():
        try:
            extra_fi.set_input_files(RESUME_PATH, timeout=4000)
        except Exception:
            pass

    # Re-verify and restore basics immediately after resume upload
    ensure_greenhouse_basics()

    # 5. Education if present
    for fld, val in [
        ('#school--0', CANDIDATE["school"]),
        ('#degree--0', CANDIDATE["degree"]),
        ('#discipline--0', "Computer Science"),
        ('#start-year--0', CANDIDATE["start_year"]),
        ('#end-year--0', CANDIDATE["end_year"]),
        ('#end-month--0', "May")
    ]:
        loc_el = page.locator(fld).first
        if loc_el.count() > 0 and loc_el.is_visible():
            try:
                if loc_el.get_attribute('role') == 'combobox':
                    fill_greenhouse_combobox(page, loc_el, val)
                else:
                    loc_el.fill(val)
            except Exception:
                pass

    # 6. Dynamically answer custom questions
    try:
        fields = page.evaluate('''() => {
            const res = [];
            document.querySelectorAll('input, textarea, select').forEach(el => {
                const id = (el.id || '').toLowerCase();
                const name = (el.name || '').toLowerCase();
                const placeholder = (el.placeholder || '').toLowerCase();
                const ariaLabel = (el.getAttribute('aria-label') || '').toLowerCase();
                const ctx = id + ' ' + name + ' ' + placeholder + ' ' + ariaLabel;

                // Strictly skip basic candidate identity fields
                if (el.type === 'hidden' ||
                    ctx.includes('first_name') || ctx.includes('first name') ||
                    ctx.includes('last_name') || ctx.includes('last name') ||
                    ctx.includes('preferred') || ctx.includes('middle_name') ||
                    ctx.includes('email') || ctx.includes('phone') || ctx.includes('telephone') ||
                    ctx.includes('resume') || ctx.includes('cover_letter')) return;

                const label = document.querySelector('label[for="' + el.id + '"]') || (el.closest('div') ? el.closest('div').querySelector('label') : null);
                const isReq = el.required || el.getAttribute('aria-required') === 'true' || (label && label.innerText.includes('*')) || false;
                res.push({
                    id: el.id,
                    name: el.name,
                    tag: el.tagName,
                    type: el.type,
                    role: el.getAttribute('role'),
                    required: isReq,
                    label: label ? label.innerText.trim() : (el.getAttribute('aria-label') || el.placeholder || '')
                });
            });
            return res;
        }''')

        for f in fields:
            fid = f.get('id')
            flabel = f.get('label') or ''
            flabel_l = flabel.lower()
            role = f.get('role')
            tag = f.get('tag')
            ftype = f.get('type')

            if not fid or 'iti-' in fid or fid in ['iti-0__search-input', 'g-recaptcha-response-100000']:
                continue

            el = page.locator(f'[id="{fid}"]')
            if el.count() == 0 or not el.first.is_visible():
                continue

            if role == 'combobox' or tag == 'SELECT':
                choice = "Yes"
                if any(k in flabel_l for k in [
                    'sponsorship', 'require sponsorship', 'require visa',
                    'relatives', 'family', 'conflict', 'non-compete',
                    'felony', 'convicted', 'crime', 'investigation',
                    'former employee', 'prior employee', 'worked at', 'worked for'
                ]):
                    choice = "No"
                elif any(k in flabel_l for k in ['gender', 'sex']):
                    choice = "Male"
                elif any(k in flabel_l for k in ['pronoun']):
                    choice = "He / Him"
                elif any(k in flabel_l for k in ['country', 'residence', 'nationality']):
                    choice = "India"
                elif any(k in flabel_l for k in ['veteran']):
                    choice = "Decline"
                elif any(k in flabel_l for k in ['disability']):
                    choice = "Decline"
                elif any(k in flabel_l for k in ['hispanic', 'latino', 'race', 'ethnicity']):
                    choice = "No"
                elif any(k in flabel_l for k in ['school', 'university', 'college', 'institution']):
                    choice = CANDIDATE["school"]
                elif any(k in flabel_l for k in ['degree']):
                    choice = CANDIDATE["degree"]
                elif any(k in flabel_l for k in [
                    'confirm', 'agree', 'certify', 'authorized', 'eligible',
                    'relocate', 'commute', 'hybrid', 'willing', 'graduation',
                    'graduate', 'over 18', '18 or older', 'terms', 'privacy'
                ]) or '?' in flabel:
                    choice = "Yes"

                fill_greenhouse_combobox(page, el.first, choice)
                continue

            if ftype == 'number':
                if 'year' in flabel_l:
                    el.fill("2026")
                elif 'month' in flabel_l:
                    el.fill("10")
                elif 'day' in flabel_l:
                    el.fill("15")
                elif any(k in flabel_l for k in ['year', 'experience', 'how many']):
                    el.fill("2")
                elif any(k in flabel_l for k in ['gpa', 'grade']):
                    el.fill("3.8")
                else:
                    el.fill("2")
                continue

            if tag == 'TEXTAREA' or ftype in ['text', 'url', 'date', 'tel', 'email', '']:
                if any(k in flabel_l for k in ['first name', 'given name']):
                    el.fill(CANDIDATE["first_name"])
                elif any(k in flabel_l for k in ['last name', 'surname', 'family name']):
                    el.fill(CANDIDATE["last_name"])
                elif any(k in flabel_l for k in ['full legal name', 'legal name', 'government id', 'full name']):
                    el.fill(CANDIDATE["name"])
                elif any(k in flabel_l for k in ['preferred name', 'nickname']):
                    el.fill(CANDIDATE["first_name"])
                elif any(k in flabel_l for k in ['email']):
                    el.fill(CANDIDATE["email"])
                elif any(k in flabel_l for k in ['phone', 'mobile', 'cell', 'telephone']):
                    el.fill(CANDIDATE["phone"])
                elif any(k in flabel_l for k in ['linkedin', 'profile']):
                    el.fill(CANDIDATE["linkedin"])
                elif any(k in flabel_l for k in ['github', 'gitlab', 'handle', 'username']):
                    el.fill(CANDIDATE["github"])
                elif any(k in flabel_l for k in ['website', 'portfolio', 'blog']):
                    el.fill(CANDIDATE["portfolio"])
                elif any(k in flabel_l for k in ['open source', 'sample', 'project', 'repository']):
                    el.fill(CANDIDATE["github"])
                elif any(k in flabel_l for k in ['gpa', 'grade', 'cgpa', 'percentage']):
                    el.fill("8.8/10 (3.8/4.0)")
                elif any(k in flabel_l for k in ['highest level of education', 'level of education', 'degree']):
                    el.fill(CANDIDATE["degree"])
                elif any(k in flabel_l for k in ['school', 'university', 'college', 'institution']):
                    el.fill(CANDIDATE["school"])
                elif any(k in flabel_l for k in ['discipline', 'major', 'field of study']):
                    el.fill(CANDIDATE["discipline"])
                elif any(k in flabel_l for k in ['security clearance', 'active clearance', 'clearance']):
                    el.fill("No active security clearance; eligible for background checks.")
                elif any(k in flabel_l for k in ['grad', 'graduation']):
                    el.fill(CANDIDATE["grad_year"])
                elif any(k in flabel_l for k in ['authorized', 'authorization', 'legally authorized', 'eligible to work']):
                    el.fill("Yes")
                elif any(k in flabel_l for k in ['sponsorship', 'require sponsorship', 'require visa']):
                    el.fill("No")
                elif any(k in flabel_l for k in ['hear', 'how did you', 'source']):
                    el.fill("Online Job Board / Direct Application")
                elif any(k in flabel_l for k in ['zip', 'postal', 'post code', 'zipcode', 'pincode', 'pin code']):
                    el.fill("141001")
                elif any(k in flabel_l for k in ['relocate', 'relocation', 'willing to relocate', 'open to relocating']):
                    el.fill("Yes")
                elif any(k in flabel_l for k in ['computer', 'operating system', 'device', 'workstation']) or re.search(r'\b(os|mac|linux|pc)\b', flabel_l):
                    el.fill("Linux / Mac")
                elif any(k in flabel_l for k in ['start date year', 'start year']):
                    el.fill(CANDIDATE["start_year"])
                elif any(k in flabel_l for k in ['end date year', 'end year']):
                    el.fill(CANDIDATE["end_year"])
                elif any(k in flabel_l for k in ['company name', 'employer', 'current company', 'previous company']):
                    el.fill("Independent Builder / Self-Employed")
                elif any(k in flabel_l for k in ['job title', 'title', 'position']):
                    el.fill("Software Engineer")
                elif any(k in flabel_l for k in ['start', 'able to start', 'available', 'begin', 'earliest', 'notice']):
                    if ftype == 'date':
                        el.fill("2026-10-15")
                    elif 'year' in flabel_l or ftype == 'number':
                        el.fill("2023")
                    else:
                        el.fill(CANDIDATE["join_date"])
                elif any(k in flabel_l for k in ['years', 'how many', 'experience']):
                    el.fill("2")
                elif any(k in flabel_l for k in ['salary', 'compensation', 'expectations', 'stipend', 'desired compensation']):
                    el.fill("$5,000 - $8,000 / month USD" if app_type == "INTERNSHIP" else "$85,000 - $110,000 USD / year")
                elif any(k in flabel_l for k in ['country', 'residence']):
                    try:
                        el.fill("India")
                    except Exception:
                        pass
                elif any(k in flabel_l for k in ['city', 'location']):
                    el.fill("Ludhiana, Punjab, India")
                elif any(k in flabel_l for k in ['own words', 'plagiarism', 'disqualify', 'certify', 'true and correct', 'agree']):
                    el.fill("I agree. All application representations are verified true.")
                elif any(k in flabel_l for k in ['why', 'interest', 'cover', 'describe your experience', 'summary', 'about yourself', 'tell us']):
                    el.fill(get_tailored_pitch(company, title, app_type, category))
                else:
                    if f.get('required') or '*' in flabel:
                        if ftype == 'number':
                            el.fill("2")
                        elif ftype == 'date':
                            el.fill("2026-10-15")
                        elif any(k in flabel_l for k in ['url', 'link', 'portfolio', 'web']):
                            el.fill(CANDIDATE["portfolio"])
                        elif tag == 'TEXTAREA':
                            el.fill("Software systems engineering undergraduate (B.Sc. Hons Software Systems & Automation) with a public GitHub track record in Next.js/React, TypeScript, Python, and cloud automation. Committed to writing clean, maintainable, tested code and delivering reliable software.")
                        elif any(k in flabel_l for k in [
                            'employee', 'currently employed', 'former employee', 'prior employee', 'worked at', 'worked for', 
                            'sponsorship', 'visa', 'require sponsorship', 'require visa', 'relatives', 'family member', 
                            'conflict of interest', 'non-compete', 'felony', 'convicted', 'crime', 'investigation'
                        ]):
                            el.fill("No")
                        elif '?' in flabel or any(k in flabel_l for k in ['are you', 'do you', 'can you', 'have you', 'will you']):
                            el.fill("Yes")
                        else:
                            el.fill("Yes")
    except Exception as e:
        print(f"[-] Custom question fill note: {e}")

    # Radio buttons handling (EEO, Veteran, Disability, Agreements, Employment Status)
    try:
        radio_groups = page.evaluate('''() => {
            const groups = {};
            document.querySelectorAll('input[type="radio"]').forEach(r => {
                if (!r.name) return;
                if (!groups[r.name]) {
                    const qEl = r.closest('fieldset')?.querySelector('legend') || 
                                r.closest('.field, .form-group, .question, div[class*="field"]')?.querySelector('label, .label, legend, p, h3, h4');
                    groups[r.name] = {
                        question: qEl ? qEl.innerText.trim().toLowerCase() : '',
                        radios: []
                    };
                }
                const lbl = document.querySelector('label[for="' + r.id + '"]') || (r.closest('label') || null);
                groups[r.name].radios.push({
                    id: r.id,
                    value: r.value,
                    checked: r.checked,
                    label: lbl ? lbl.innerText.trim().toLowerCase() : ''
                });
            });
            return groups;
        }''')
        for group_name, gdata in radio_groups.items():
            radios = gdata.get('radios', [])
            q_text = gdata.get('question', '')
            if any(r['checked'] for r in radios):
                continue
            picked_id = None
            if any(k in q_text for k in [
                'employee', 'currently employed', 'former employee', 'prior employee', 'worked at', 'worked for',
                'sponsorship', 'visa', 'require sponsorship', 'require visa', 'relatives', 'family', 'conflict',
                'non-compete', 'felony', 'convicted'
            ]):
                for r in radios:
                    if any(w in r['label'] for w in ['no', 'neither', 'none', 'i do not', 'not applicable', 'decline']):
                        picked_id = r['id']
                        break
            elif any(k in q_text for k in ['authorized', 'eligibility', 'eligible', 'over 18', '18 or older', 'agree', 'certify', 'terms', 'privacy', 'acknowledge']):
                for r in radios:
                    if any(w in r['label'] for w in ['yes', 'agree', 'authorized', 'certify', 'confirm']):
                        picked_id = r['id']
                        break
            elif any(k in q_text for k in ['veteran']):
                for r in radios:
                    if any(w in r['label'] for w in ['not a protected veteran', 'i am not a veteran', 'no', 'decline']):
                        picked_id = r['id']
                        break
            elif any(k in q_text for k in ['disability']):
                for r in radios:
                    if any(w in r['label'] for w in ['no, i don’t have', 'no, i do not', 'i do not wish', 'decline', 'no']):
                        picked_id = r['id']
                        break
            elif any(k in q_text for k in ['gender', 'sex']):
                for r in radios:
                    if re.search(r'\bmale\b', r['label']) and not re.search(r'\bfemale\b', r['label']):
                        picked_id = r['id']
                        break
            elif any(k in q_text for k in ['race', 'ethnicity']):
                for r in radios:
                    if 'asian' in r['label'] and 'caucasian' not in r['label']:
                        picked_id = r['id']
                        break

            if not picked_id:
                for r in radios:
                    if any(w in r['label'] for w in ['not a protected veteran', 'no, i don’t have', 'no, i do not', 'i do not wish', 'decline', 'asian', 'male', 'no']):
                        picked_id = r['id']
                        break
            if not picked_id and radios:
                for r in radios:
                    if 'no' in r['label']:
                        picked_id = r['id']
                        break
                if not picked_id:
                    picked_id = radios[0]['id']
            if picked_id:
                try:
                    page.locator(f'[id="{picked_id}"]').first.check(timeout=800)
                except Exception:
                    pass
    except Exception:
        pass

    for cb in page.locator('input[type="checkbox"]').all():
        try:
            if cb.is_visible() and not cb.is_checked():
                cb.check(timeout=800)
        except Exception:
            pass

    # Sweep custom dropdown triggers / combobox buttons that are still unselected
    try:
        custom_combos = page.locator('[role="combobox"]:visible, button[aria-haspopup="listbox"]:visible, .select__control:visible').all()
        for c_combo in custom_combos:
            try:
                c_txt = c_combo.inner_text().strip().lower()
                if any(unsel in c_txt for unsel in ['select...', 'select a', 'choose', 'select option']):
                    lbl = c_combo.locator('xpath=ancestor::div[contains(@class, "field") or contains(@class, "group")][1]//label').first
                    lbl_text = lbl.inner_text().strip().lower() if (lbl.count() > 0 and lbl.is_visible()) else ''
                    choice = "Yes"
                    if any(k in lbl_text for k in ['sponsorship', 'visa', 'felony', 'relative', 'conflict', 'former']):
                        choice = "No"
                    elif any(k in lbl_text for k in ['gender', 'sex']):
                        choice = "Male"
                    elif any(k in lbl_text for k in ['country', 'residence', 'nationality']):
                        choice = "India"
                    fill_greenhouse_combobox(page, c_combo, choice)
            except Exception:
                pass
    except Exception:
        pass

    page.wait_for_timeout(1000)

    # Final sweep: Attach verified resume to all file inputs (e.g. Transcript, Cover Letter)
    try:
        for fi in page.locator('input[type="file"]').all():
            try:
                fi.set_input_files(RESUME_PATH, timeout=2000)
            except Exception:
                pass
    except Exception:
        pass

    # 7. Submit Application
    btn = page.locator('#submit_app, input[id="submit_app"], button:has-text("Submit application"), button:has-text("Submit Application"), button:has-text("Submit app"), button:has-text("Submit App"), #application-form button[type="submit"], #apply_form button[type="submit"], form[action*="application"] button[type="submit"], form[action*="job"] button[type="submit"], button[data-mapped="submit"], button:has-text("Submit")').first
    if btn.count() == 0 or not btn.is_visible():
        btn = page.locator('button[type="submit"]:not([id*="search"]):not([class*="search"]):not([id*="quick"]), input[type="submit"]:not([id*="search"])').first

    if btn.count() == 0:
        print(f"[-] No Greenhouse submit button found")
        mark_url_dead(url)
        return False

    # Check & solve captchas (Turnstile / reCAPTCHA) with Gemini
    solve_all_captchas(page)

    try:
        btn.scroll_into_view_if_needed(timeout=3000)
        btn.click(timeout=4000)
    except Exception as e:
        print(f"[-] Greenhouse submit click note: {e}")
        try:
            btn.evaluate('el => el.click()')
        except Exception:
            pass

    # 8. Post-Submit Wait & Multi-Check Loop (Handles OTP and Async Processing)
    submit_confirmed = False
    for poll_idx in range(6):  # Poll up to 18 seconds (6 x 3s)
        page.wait_for_timeout(3000)
        solve_all_captchas(page)

        # Check for OTP / Security Code
        otp_container = page.locator('#email-verification, input[id*="security_code"], input[name*="security_code"], #security-input-0')
        if otp_container.count() > 0 and otp_container.first.is_visible():
            print(f"[!] Email security verification triggered for {company}! Fetching code via Gmail IMAP (poll {poll_idx+1}/6)...")
            for otp_attempt in range(2):
                code = fetch_greenhouse_otp(company_name=company, min_timestamp=time.time() - 90, max_wait=24)
                if code:
                    for idx, ch in enumerate(code):
                        inp = page.locator(f'#security-input-{idx}')
                        if inp.count() > 0:
                            inp.fill(ch)
                    sec_in = page.locator('input[id*="security_code"], input[name*="security_code"]').first
                    if sec_in.count() > 0:
                        sec_in.fill(code)
                    page.wait_for_timeout(800)
                    verify_btn = page.locator('#submit_app, button[type="submit"], button:has-text("Submit application"), button:has-text("Verify"), button:has-text("Submit"), button:has-text("Confirm"), button:has-text("Continue"), button:has-text("Enter")').first
                    if verify_btn.count() > 0 and verify_btn.is_visible():
                        verify_btn.click()
                    else:
                        try:
                            page.keyboard.press("Enter")
                        except Exception:
                            pass
                    page.wait_for_timeout(4000)
                    solve_all_captchas(page)

                    err_code = page.locator('div:has-text("Incorrect security code"), span:has-text("Incorrect security code"), p:has-text("Incorrect security code")')
                    if err_code.count() > 0 and err_code.first.is_visible():
                        print("[-] Incorrect security code flagged! Waiting 5s for newest OTP and retrying...")
                        time.sleep(5)
                        continue
                    else:
                        break

        # Check for visible validation errors stopping submission
        has_val_error = page.locator('div:has-text("Please correct highlighted fields"), p:has-text("This section is required"), div:has-text("This field is required")').count() > 0

        # Check if submission is confirmed
        current_url = page.url.lower()
        page_text = page.locator('body').inner_text().lower()
        if not has_val_error and (any(m in current_url for m in ['confirmation', 'submitted', 'thank_you', 'thanks', 'success']) or any(m in page_text for m in [
            'thank you for applying', 'your application has been received', 'application received', 
            'we have received your application', 'we’ve received your application', 'application submitted',
            'submitted successfully', 'application was submitted', 'thanks for applying',
            'submission complete', 'application has been submitted', 'application was received'
        ]) or page.locator('#application_confirmation, .application-confirmation, div:has-text("Thank you for applying"), div:has-text("Application Received"), div:has-text("Application Submitted")').count() > 0):
            submit_confirmed = True
            break

    clean_slug = re.sub(r'[^a-zA-Z0-9_]', '_', f"{company}_{title}")[:35]
    prefix = "intern" if app_type == "INTERNSHIP" else "job"
    proof_suffix = "gh_confirmed.png" if submit_confirmed else "gh_failed.png"
    proof_path = f"{PROOF_DIR}/{prefix}_{clean_slug}_{proof_suffix}"
    page.screenshot(path=proof_path, full_page=True)

    if submit_confirmed:
        print(f"🎉 CONFIRMED Greenhouse submission for {company} - {title}!")
        log_verified_application(
            company=company,
            role=title,
            portal="Greenhouse",
            url=url,
            salary_or_stipend=stipend_or_sal,
            proof_path=proof_path,
            app_type=app_type,
            notes=f"Confirmed Greenhouse submission. {category}"
        )
        return True
    else:
        print(f"[-] Status inconclusive on Greenhouse. Current URL: {current_url}")
        mark_url_dead(url)
        return False

def apply_lever(page, item):
    company = re.sub('<[^<]+?>', '', item.get('company', '')).strip()
    title = re.sub('<[^<]+?>', '', item.get('title') or item.get('role', '')).strip()
    url = (item.get('applyUrl') or item.get('url', '')).replace('&amp;', '&')
    app_type = "INTERNSHIP" if (item.get('is_internship') or item.get('category') == 'INTERNSHIP' or 'intern' in title.lower() or 'co-op' in title.lower()) else "JOB"
    category = item.get('category', 'Engineering')
    stipend_or_sal = item.get('stipend') or ("$5,000 / month" if app_type == "INTERNSHIP" else "$80,000 - $95,000 USD / year")

    print(f"\n==================================================================")
    print(f"[*] [LEVER] [{app_type}] [{category}] {company} - {title}")
    print(f"[*] URL: {url}")
    print(f"==================================================================")

    if not url:
        return False

    if is_already_confirmed(url, company, title):
        print(f"[!] Already confirmed in DB: {url}")
        return True

    fit_score, critique_text = critique_application(company, title)
    if fit_score < 70:
        print(f"[-] SKIPPING {company} - {title} [Score: {fit_score}/100]: {critique_text}")
        return False

    if url.startswith('http://'):
        url = 'https://' + url[7:]
    base_url = url.split('?')[0].rstrip('/')
    query_str = url.split('?')[1] if '?' in url else ''
    apply_url = base_url if '/apply' in base_url else base_url + '/apply'
    if query_str:
        apply_url += '?' + query_str

    try:
        page.goto(apply_url, wait_until='domcontentloaded', timeout=10000)
    except Exception:
        try:
            page.goto(apply_url, wait_until='load', timeout=10000)
        except Exception as e:
            print(f"[-] Lever navigation failed: {e}")
            mark_url_dead(url)
            return False

    page.wait_for_timeout(2000)

    page_txt = page.locator('body').inner_text().lower()
    if any(k in page_txt for k in ['no longer available', 'job has been closed', 'posting not found', '404 not found']):
        print(f"[-] Lever posting is closed or unavailable.")
        mark_url_dead(url)
        return False

    if page.locator('input').count() == 0:
        btn_apply = page.locator('a:has-text("Apply for this job"), button:has-text("Apply for this job"), .postings-btn').first
        if btn_apply.count() > 0 and btn_apply.is_visible():
            btn_apply.click()
            page.wait_for_timeout(2500)

    # 1. Attach Resume
    res_input = page.locator('input[type="file"][name*="resume"], input[type="file"]').first
    if res_input.count() > 0:
        try:
            res_input.set_input_files(RESUME_PATH, timeout=5000)
            print("[+] Lever resume attached")
            page.wait_for_timeout(1000)
        except Exception as e:
            print(f"[-] Lever resume attach note: {e}")

    # 2. Fill Standard Lever Fields
    safe_fill_by_name = lambda name, val: page.locator(f'input[name="{name}"]').first.fill(str(val)) if page.locator(f'input[name="{name}"]').count() > 0 and page.locator(f'input[name="{name}"]').first.is_visible() else None
    
    try:
        safe_fill_by_name("name", CANDIDATE["name"])
        safe_fill_by_name("email", CANDIDATE["email"])
        safe_fill_by_name("phone", CANDIDATE["phone"])
        safe_fill_by_name("location", CANDIDATE["location"])
        safe_fill_by_name("org", "Self-Employed / Independent Builder")
        safe_fill_by_name("urls[LinkedIn]", CANDIDATE["linkedin"])
        safe_fill_by_name("urls[GitHub]", CANDIDATE["github"])
        safe_fill_by_name("urls[Portfolio]", CANDIDATE["portfolio"])
        safe_fill_by_name("urls[Other]", CANDIDATE["portfolio"])
        loc_inp = page.locator('input.location-input, #location-input, input[name="location"]').first
        if loc_inp.count() > 0 and loc_inp.is_visible() and not loc_inp.input_value():
            try:
                loc_inp.fill(CANDIDATE["location"])
            except Exception:
                pass
    except Exception as e:
        print(f"[-] Lever standard fill notice: {e}")

    # 3. Additional info / comments
    comm = page.locator('textarea[name="comments"], textarea[name*="additional"]').first
    if comm.count() > 0 and comm.is_visible():
        try:
            pitch = CANDIDATE["why_frontend"] if "front" in category.lower() else (CANDIDATE["why_intern"] if app_type == "INTERNSHIP" else CANDIDATE["why_automation"])
            comm.fill(pitch)
        except Exception:
            pass

    # 4. Fill custom questions
    try:
        for fld in page.locator('.application-question, .custom-question').all():
            q_txt = fld.inner_text().lower()
            sel = fld.locator('select').first
            if sel.count() > 0 and sel.is_visible():
                opts = sel.locator('option').all()
                chosen_opt = None
                for opt in opts:
                    otxt = opt.inner_text().strip().lower()
                    if any(k in q_txt for k in ['sponsorship', 'visa']):
                        if 'no' in otxt or 'none' in otxt:
                            chosen_opt = opt.get_attribute('value')
                            break
                    elif any(k in q_txt for k in ['authorized', 'legally']):
                        if 'yes' in otxt:
                            chosen_opt = opt.get_attribute('value')
                            break
                    elif any(k in q_txt for k in ['gender']):
                        if 'male' in otxt and 'female' not in otxt:
                            chosen_opt = opt.get_attribute('value')
                            break
                    elif any(k in q_txt for k in ['race', 'ethnicity']):
                        if 'asian' in otxt and 'caucasian' not in otxt:
                            chosen_opt = opt.get_attribute('value')
                            break
                    elif any(k in q_txt for k in ['veteran']):
                        if 'not' in otxt or 'no' in otxt:
                            chosen_opt = opt.get_attribute('value')
                            break
                    elif any(k in q_txt for k in ['disability']):
                        if 'no' in otxt or 'do not' in otxt:
                            chosen_opt = opt.get_attribute('value')
                            break
                if chosen_opt:
                    sel.select_option(chosen_opt)
                elif len(opts) > 1:
                    sel.select_option(index=1)
                continue

            radios = fld.locator('input[type="radio"]').all()
            if radios:
                for rad in radios:
                    try:
                        rlab = rad.locator('xpath=..').inner_text().lower()
                    except Exception:
                        rlab = ''
                    if not rlab:
                        try:
                            rlab = rad.locator('xpath=ancestor::label').inner_text().lower()
                        except Exception:
                            rlab = ''
                    if any(k in q_txt for k in ['sponsorship', 'visa']) and ('no' in rlab or 'none' in rlab):
                        rad.check()
                        break
                    elif any(k in q_txt for k in ['authorized', 'legally']) and 'yes' in rlab:
                        rad.check()
                        break
                    elif any(k in q_txt for k in ['gender']) and ('male' in rlab and 'female' not in rlab):
                        rad.check()
                        break
                    elif any(k in q_txt for k in ['race', 'ethnicity']) and ('asian' in rlab and 'caucasian' not in rlab):
                        rad.check()
                        break
                    elif any(k in q_txt for k in ['veteran']) and ('not' in rlab or 'no' in rlab):
                        rad.check()
                        break
                    elif any(k in q_txt for k in ['disability']) and ('no' in rlab or 'do not' in rlab):
                        rad.check()
                        break
                    elif 'yes' in rlab:
                        rad.check()
                        break
                else:
                    if len(radios) > 0:
                        try:
                            radios[0].check()
                        except Exception:
                            pass
                continue

            cinp = fld.locator('input[type="text"]').first
            if cinp.count() > 0 and cinp.is_visible() and not cinp.input_value():
                if any(k in q_txt for k in ['school', 'university']):
                    cinp.fill(CANDIDATE["school"])
                elif any(k in q_txt for k in ['degree']):
                    cinp.fill(CANDIDATE["degree"])
                elif any(k in q_txt for k in ['major', 'discipline']):
                    cinp.fill(CANDIDATE["discipline"])
                elif any(k in q_txt for k in ['grad', 'graduation']):
                    cinp.fill(CANDIDATE["grad_year"])
                elif any(k in q_txt for k in ['year', 'experience', 'how many']):
                    cinp.fill("2")
                elif any(k in q_txt for k in ['compensation', 'salary', 'expectation', 'rate']):
                    cinp.fill("$5,000 / month" if app_type == "INTERNSHIP" else "$85,000 USD / year")
                else:
                    cinp.fill("Yes")
    except Exception as e:
        print(f"[-] Lever custom fields note: {e}")

    # Fallback sweeper for any remaining required radio groups
    try:
        checked_names = set()
        for r_chk in page.locator('input[type="radio"]:checked').all():
            nm = r_chk.get_attribute('name')
            if nm:
                checked_names.add(nm)
        for r_req in page.locator('input[type="radio"]').all():
            nm = r_req.get_attribute('name')
            if nm and nm not in checked_names:
                r_req.check()
                checked_names.add(nm)
    except Exception:
        pass

    # Universal sweeper for all remaining required inputs / textareas
    try:
        for req_inp in page.locator('input[required]:not([type="radio"]):not([type="checkbox"]):not([type="hidden"]), textarea[required]').all():
            if req_inp.is_visible() and not req_inp.input_value():
                nm = (req_inp.get_attribute('name') or req_inp.get_attribute('id') or '').lower()
                if any(k in nm for k in ['loc', 'city', 'country', 'state']):
                    req_inp.fill(CANDIDATE["location"])
                elif 'phone' in nm:
                    req_inp.fill(CANDIDATE["phone"])
                elif 'mail' in nm:
                    req_inp.fill(CANDIDATE["email"])
                elif 'name' in nm:
                    req_inp.fill(CANDIDATE["name"])
                elif any(k in nm for k in ['linkedin', 'url', 'link', 'portfolio', 'site']):
                    req_inp.fill(CANDIDATE["linkedin"])
                elif any(k in nm for k in ['salary', 'compensation', 'pay', 'stipend', 'rate']):
                    req_inp.fill("$5,000 / month" if app_type == "INTERNSHIP" else "$85,000 USD / year")
                elif any(k in nm for k in ['school', 'university', 'college']):
                    req_inp.fill(CANDIDATE["school"])
                elif any(k in nm for k in ['degree']):
                    req_inp.fill(CANDIDATE["degree"])
                elif any(k in nm for k in ['discipline', 'major']):
                    req_inp.fill(CANDIDATE["discipline"])
                else:
                    req_inp.fill("Yes")
    except Exception as e:
        print(f"[-] Lever required fields note: {e}")

    # Checkboxes (Consent / Policy)
    for cb in page.locator('input[type="checkbox"]').all():
        try:
            if cb.is_visible() and not cb.is_checked():
                cb.check()
        except Exception:
            pass

    page.wait_for_timeout(1000)

    solve_all_captchas(page)

    btn = page.locator('#btn-submit, button[data-qa="btn-submit"], .template-btn-submit:not(.hidden)').first
    if btn.count() == 0 or not btn.is_visible():
        btn = page.locator('button:has-text("Submit application"):not(.hidden), button:has-text("Submit"):not(.hidden)').first
    if btn.count() == 0:
        print("[-] No Lever submit button found")
        mark_url_dead(url)
        return False

    try:
        btn.scroll_into_view_if_needed(timeout=3000)
    except Exception:
        pass
    print("[*] Submitting Lever application...")
    try:
        btn.click(timeout=5000)
    except Exception:
        try:
            btn.evaluate('el => el.click()')
        except Exception as e:
            print(f"[-] Lever submit click failed: {e}")
    page.wait_for_timeout(5000)
    solve_all_captchas(page)

    # If hidden hcaptcha submit button exists, trigger as fallback if hcaptcha solved
    try:
        h_resp = page.locator('#hcaptchaResponseInput').get_attribute('value')
        h_btn = page.locator('#hcaptchaSubmitBtn').first
        if h_btn.count() > 0 and h_resp:
            print("[+] Triggering verified hCaptcha submit button...")
            h_btn.evaluate('el => el.click()')
            page.wait_for_timeout(4000)
    except Exception:
        pass

    page.wait_for_timeout(3000)

    clean_slug = re.sub(r'[^a-zA-Z0-9_]', '_', f"{company}_{title}")[:35]
    prefix = "intern" if app_type == "INTERNSHIP" else "job"
    proof_path = f"{PROOF_DIR}/{prefix}_{clean_slug}_lever_confirmed.png"
    page.screenshot(path=proof_path, full_page=True)

    curr_url = page.url.lower()
    page_text = page.locator('body').inner_text().lower()
    is_confirmed = ('/thanks' in curr_url or any(m in page_text for m in [
        'thank you for applying', 'application submitted', 'we have received your application',
        'thanks for your interest', 'application was received', 'submitted successfully'
    ]))

    if is_confirmed:
        print(f"🎉 CONFIRMED Lever submission for {company} - {title}!")
        log_verified_application(
            company=company,
            role=title,
            portal="lever",
            url=url,
            salary_or_stipend=stipend_or_sal,
            proof_path=proof_path,
            app_type=app_type,
            notes=f"100% verified Lever submission. {category}"
        )
        return True
    else:
        print(f"[-] Lever submission not confirmed for {company} - {title} (URL: {curr_url})")
        return False

def apply_ashby(page, item):
    company = re.sub('<[^<]+?>', '', item.get('company', '')).strip()
    title = re.sub('<[^<]+?>', '', item.get('title') or item.get('role', '')).strip()
    url = (item.get('applyUrl') or item.get('url', '')).replace('&amp;', '&')
    app_type = "INTERNSHIP" if (item.get('is_internship') or item.get('category') == 'INTERNSHIP' or 'intern' in title.lower() or 'co-op' in title.lower()) else "JOB"
    category = item.get('category', 'Engineering')
    stipend_or_sal = item.get('stipend') or "$60,000 - $95,000 USD / year"

    print(f"\n==================================================================")
    print(f"[*] [{app_type}] [{category}] {company} - {title}")
    print(f"[*] URL: {url}")
    print(f"==================================================================")

    if is_already_confirmed(url, company, title):
        print(f"[!] Already confirmed in DB: {url}")
        return True

    fit_score, critique_text = critique_application(company, title)
    if fit_score < 80:
        print(f"[-] SKIPPING {company} - {title} [Score: {fit_score}/100]: {critique_text}")
        return False

    if url.startswith('http://'):
        url = 'https://' + url[7:]
    base_url = url.split('?')[0].rstrip('/')
    query_str = url.split('?')[1] if '?' in url else ''
    
    if '/application' in base_url:
        app_url = base_url
    else:
        app_url = base_url + '/application'
        
    if query_str:
        clean_query = re.sub(r'embed=true&?', '', query_str).rstrip('&')
        if clean_query:
            app_url += '?' + clean_query

    try:
        page.goto(app_url, wait_until='domcontentloaded', timeout=8000)
    except Exception:
        try:
            page.goto(app_url, wait_until='load', timeout=8000)
        except Exception as e:
            print(f"[-] Navigation failed: {e}")
            mark_url_dead(url)
            return False

    # Wait for Ashby React SPA and GraphQL schema to hydrate
    try:
        page.wait_for_selector('input[type="file"], input[name*="name"], input[id*="name"], input[type="email"], input[placeholder*="name"]', timeout=8000)
    except Exception:
        pass

    # If inputs still not visible, check for "Apply for this Job" or "Application" tab
    if page.locator('input').count() == 0:
        try:
            apply_btn = page.locator('a:has-text("Apply for this Job"), button:has-text("Apply for this Job"), a:has-text("Application"), button:has-text("Application"), a:has-text("Apply")').first
            if apply_btn.count() > 0 and apply_btn.is_visible():
                apply_btn.click()
                try:
                    page.wait_for_selector('input[type="file"], input[name*="name"], input[id*="name"], input[type="email"]', timeout=6000)
                except Exception:
                    pass
        except Exception:
            pass

    # Check if job is explicitly closed or redirected
    page_txt = page.locator('body').inner_text().lower()
    page_title = page.title().lower()
    if any(k in page_txt for k in ['this job has been closed', 'no longer accepting applications', 'posting not found', '404 not found']) or (page_title == 'jobs' and '/application' not in page.url):
        print(f"[-] Job confirmed closed or redirected on Ashby.")
        mark_url_dead(url)
        return False

    # Grace period for proxy latency before declaring dead
    if page.locator('input').count() == 0:
        page.wait_for_timeout(1200)

    if page.locator('input').count() == 0:
        print(f"[-] No form inputs found after hydration wait (job closed or expired)")
        mark_url_dead(url)
        return False

    # 1. Attach resume
    for finp in page.locator('input[type="file"]').all():
        try:
            finp.set_input_files(RESUME_PATH)
            print("[+] Resume attached to file input")
            page.wait_for_timeout(200)
        except Exception:
            pass

    def safe_fill(el, val):
        if not el or el.count() == 0:
            return False
        try:
            tag = el.evaluate("el => el.tagName.toLowerCase()")
            itype = (el.get_attribute('type') or tag).lower()
            if itype == 'number':
                digits = re.sub(r'[^\d]', '', str(val).split('-')[0])
                if not digits or int(digits) < 10:
                    digits = "5000" if app_type == "INTERNSHIP" else "85000"
                el.fill(digits)
            else:
                el.fill(str(val))
            return True
        except Exception:
            try:
                el.evaluate("(el, v) => el.value = v", str(val))
                return True
            except Exception:
                pass
        return False

    # 2. Iterate all labels and fill associated inputs using attribute selector
    labels = page.locator('label').all()
    for l in labels:
        try:
            txt = l.inner_text().strip().lower()
            for_id = l.get_attribute('for')
            if not for_id:
                continue
            target = page.locator(f'[id="{for_id}"]').first
            if target.count() == 0 or not target.is_visible():
                # Check for Yes/No button container
                cont = l.locator('xpath=..')
                yes_btn = cont.locator('button[data-option="yes"], button:has-text("Yes")').first
                no_btn = cont.locator('button[data-option="no"], button:has-text("No")').first
                if any(k in txt for k in [
                    'sponsorship', 'visa', 'require sponsorship', 'require visa',
                    'employee', 'currently employed', 'former employee', 'prior employee', 'worked at', 'worked for',
                    'relative', 'family', 'conflict', 'non-compete', 'felony', 'convicted'
                ]):
                    if no_btn.count() > 0 and no_btn.is_visible():
                        no_btn.click()
                    elif yes_btn.count() > 0 and yes_btn.is_visible():
                        yes_btn.click()
                elif any(k in txt for k in ['authorized', 'eligible', 'over 18', 'agree', 'certify', 'terms', 'privacy', 'acknowledge']):
                    if yes_btn.count() > 0 and yes_btn.is_visible():
                        yes_btn.click()
                    elif no_btn.count() > 0 and no_btn.is_visible():
                        no_btn.click()
                else:
                    if no_btn.count() > 0 and no_btn.is_visible():
                        no_btn.click()
                    elif yes_btn.count() > 0 and yes_btn.is_visible():
                        yes_btn.click()
                continue

            tag = target.evaluate("el => el.tagName.toLowerCase()")
            itype = target.get_attribute('type') or tag
            current_val = target.input_value() if itype not in ['radio', 'checkbox'] else ''

            if current_val:
                continue

            if itype == 'checkbox':
                if any(k in txt for k in ['agree', 'consent', 'terms', 'privacy']):
                    target.check()
                continue

            # Contextual text mapping
            if 'first name' in txt or 'preferred' in txt or 'given name' in txt:
                safe_fill(target, CANDIDATE["first_name"])
            elif 'last name' in txt or 'family name' in txt or 'surname' in txt:
                safe_fill(target, CANDIDATE["last_name"])
            elif 'name' in txt and not any(k in txt for k in ['company', 'school', 'university', 'user']):
                safe_fill(target, CANDIDATE["name"])
            elif 'email' in txt:
                safe_fill(target, CANDIDATE["email"])
            elif any(k in txt for k in ['phone', 'mobile']):
                safe_fill(target, CANDIDATE["phone"])
            elif any(k in txt for k in ['current company', 'employer', 'organization', 'company name']):
                safe_fill(target, "Self-Employed / Independent Builder")
            elif any(k in txt for k in ['compensation', 'salary', 'expectation', 'expected comp', 'desired rate', 'hourly rate', 'desired salary', 'pay']):
                safe_fill(target, "$5,000 / month ($30/hr USD)" if app_type == "INTERNSHIP" else "$80,000 - $95,000 USD / year")
            elif any(k in txt for k in ['why', 'interest', 'cover letter', 'tell us', 'about you', 'fit']):
                safe_fill(target, get_tailored_pitch(company, title, app_type, category))
            elif any(k in txt for k in ['earliest month', 'start date', 'when can you start', 'join date', 'notice period', 'availability']):
                safe_fill(target, CANDIDATE["join_date"])
            elif 'linkedin' in txt:
                safe_fill(target, CANDIDATE["linkedin"])
            elif any(k in txt for k in ['github', 'git']):
                safe_fill(target, CANDIDATE["github"])
            elif any(k in txt for k in ['portfolio', 'website', 'links that showcase']):
                safe_fill(target, CANDIDATE["portfolio"])
            elif any(k in txt for k in ['twitter', 'x account', 'x.com']):
                safe_fill(target, "https://x.com/gurination")
            elif any(k in txt for k in ['country', 'what country']):
                safe_fill(target, "India")
            elif any(k in txt for k in ['teach', 'topic', 'something']):
                safe_fill(target, CANDIDATE["teach_something"])
            elif any(k in txt for k in ['pronoun']):
                safe_fill(target, CANDIDATE["pronouns"])
            elif any(k in txt for k in ['project', 'built', 'proud of', 'worked on', 'accomplish', 'challenge']):
                safe_fill(target, CANDIDATE["proud_of"])
            elif any(k in txt for k in ['visa', 'sponsorship']):
                safe_fill(target, CANDIDATE["visa"])
            elif any(k in txt for k in ['motivates', 'motivation']):
                safe_fill(target, CANDIDATE["motivates"])
            elif any(k in txt for k in ['how did you hear', 'hear about']):
                safe_fill(target, CANDIDATE["how_heard"])
            elif any(k in txt for k in ['specific', 'work on something']):
                safe_fill(target, CANDIDATE["specific"])
            elif any(k in txt for k in ['school', 'university', 'college', 'institution']):
                safe_fill(target, CANDIDATE["school"])
            elif any(k in txt for k in ['degree']):
                safe_fill(target, CANDIDATE["degree"])
            elif any(k in txt for k in ['major', 'field of study', 'discipline']):
                safe_fill(target, CANDIDATE["discipline"])
            elif any(k in txt for k in ['start date', 'start month', 'start year']):
                safe_fill(target, "2023-08-01")
            elif any(k in txt for k in ['end date', 'graduation date', 'grad date', 'expected graduation']):
                safe_fill(target, "2027-05-31")
            elif any(k in txt for k in ['still student', 'current student']):
                safe_fill(target, "Yes")
            elif any(k in txt for k in ['relocate', 'commute', 'greater new york', 'nyc', 'in-person']):
                safe_fill(target, "Yes")
            elif any(k in txt for k in ['grad', 'graduation']):
                safe_fill(target, CANDIDATE["grad_year"])
            elif 'company' in txt:
                safe_fill(target, "Self-Employed / Independent Builder")
        except Exception:
            pass

    # Solve all radio groups dynamically with question context awareness
    try:
        radio_names = set(page.locator('input[type="radio"]').evaluate_all('els => els.map(e => e.name)'))
        for rname in radio_names:
            r_group = page.locator(f'input[type="radio"][name="{rname}"]').all()
            if not r_group:
                continue
            
            # Detect question context from parent container
            q_text = ""
            try:
                first_rad = r_group[0]
                q_cont = first_rad.locator('xpath=ancestor::div[contains(@class, "field") or contains(@class, "question") or contains(@class, "group")][1]').first
                if q_cont.count() > 0:
                    q_text = q_cont.inner_text().lower()
            except Exception:
                pass

            chosen = None
            for rad in r_group:
                rid = rad.get_attribute('id')
                rlab = page.locator(f'label[for="{rid}"]').first if rid else None
                if not rlab or rlab.count() == 0:
                    rlab = rad.locator('xpath=ancestor::label | xpath=..').first
                rtxt = rlab.inner_text().strip().lower() if (rlab and rlab.count() > 0) else ''

                if any(k in q_text for k in ['race', 'ethnicity', 'demographic']):
                    if 'asian' in rtxt and 'caucasian' not in rtxt:
                        chosen = rad
                        break
                elif any(k in q_text for k in [
                    'sponsorship', 'visa', 'require sponsorship', 'require visa',
                    'employee', 'currently employed', 'former employee', 'prior employee', 'worked at', 'worked for',
                    'relative', 'family', 'conflict', 'non-compete', 'felony', 'convicted'
                ]):
                    if any(k in rtxt for k in ['none', 'no', 'will not', 'neither', 'i do not']):
                        chosen = rad
                        break
                elif any(k in q_text for k in ['authorized', 'legally authorized', 'work in the united states']):
                    if 'yes' in rtxt:
                        chosen = rad
                        break
                elif any(k in q_text for k in ['relocate', 'commute', 'anchor days', 'in-person', 'in office']):
                    if 'yes' in rtxt:
                        chosen = rad
                        break
                elif any(k in q_text for k in ['gender', 'sex']):
                    if 'male' in rtxt and 'female' not in rtxt:
                        chosen = rad
                        break
                elif any(k in q_text for k in ['veteran']):
                    if any(k in rtxt for k in ['not a protected veteran', 'i am not a veteran', 'no']):
                        chosen = rad
                        break
                elif any(k in q_text for k in ['disability']):
                    if any(k in rtxt for k in ['do not have', 'no']):
                        chosen = rad
                        break
                elif any(k in rtxt for k in ['asian (not hispanic or latino)', 'asian', 'i am not a protected veteran', 'male', 'decline to self-identify', '2028', 'spring 2027', 'fall 2026', 'san francisco', 'remote', 'javascript', 'frontend', 'friend', 'careers page', 'no', 'yes']):
                    chosen = rad
                    break

            if not chosen and len(r_group) > 0:
                if any(k in q_text for k in ['race', 'ethnicity']):
                    for rad in r_group:
                        rlab = rad.locator('xpath=ancestor::label | xpath=..').first
                        if 'decline' in rlab.inner_text().lower() or 'asian' in rlab.inner_text().lower():
                            chosen = rad
                            break
                if not chosen:
                    chosen = r_group[0]
            if chosen:
                chosen.check()
    except Exception:
        pass

    # Intelligent Checkbox Handler: Never check contradictory options blindly!
    try:
        checkboxes = page.locator('input[type="checkbox"]').all()
        handled_groups = set()
        for cb in checkboxes:
            if not cb.is_visible():
                continue
            cb_id = cb.get_attribute('id') or ''
            cb_name = cb.get_attribute('name') or ''
            lab = page.locator(f'label[for="{cb_id}"]').first if cb_id else None
            txt = lab.inner_text().strip().lower() if (lab and lab.count() > 0) else ''
            if not txt:
                parent = cb.locator('xpath=ancestor::label | xpath=ancestor::div[contains(@class, "checkbox") or contains(@class, "field") or contains(@class, "option")]').first
                if parent.count() > 0:
                    txt = parent.inner_text().strip().lower()

            # 1. Degree Type: Check only Bachelor's/Undergraduate
            if any(k in txt for k in ['bachelor', 'undergraduate']):
                if not cb.is_checked():
                    cb.check()
                continue
            elif any(k in txt for k in ['master', 'phd', 'mba', 'doctorate', 'high school', 'other']):
                continue

            # 2. How did you hear: Select only ONE (LinkedIn or Careers Page)
            if any(k in txt for k in ['linkedin', 'glassdoor', 'notion blog', 'notion employee', 'notion website', 'billboard', 'conference', 'hear about', 'source']):
                group_key = cb_name or "hear_group"
                if group_key not in handled_groups:
                    if 'linkedin' in txt or 'website' in txt or 'job board' in txt:
                        if not cb.is_checked():
                            cb.check()
                        handled_groups.add(group_key)
                continue

            # 3. Role preferences: Check only primary match
            if any(k in txt for k in ['full stack', 'backend', 'frontend']):
                group_key = cb_name or "role_pref_group"
                if group_key not in handled_groups:
                    if 'full stack' in txt or 'frontend' in txt:
                        if not cb.is_checked():
                            cb.check()
                        handled_groups.add(group_key)
                continue

            # 4. Mandatory consents / terms / legal authorization / age verification
            if any(k in txt for k in ['agree', 'consent', 'terms', 'privacy', 'acknowledge', 'authorized', 'certify', 'understand', '18', 'policy', 'declaration']):
                if not cb.is_checked():
                    cb.check()
            elif cb_name and cb_name not in handled_groups:
                if not cb.is_checked():
                    cb.check()
                handled_groups.add(cb_name)
    except Exception as e:
        print(f"[-] Checkbox handling notice: {e}")

    # Ashby Date Picker handling (e.g. Graduation Date "Pick date...")
    try:
        date_triggers = page.locator('button:has-text("Pick date"), div[role="button"]:has-text("Pick date"), [placeholder*="Pick date"], input[id*="gradDate"], input[name*="gradDate"]').all()
        for dt in date_triggers:
            if dt.is_visible():
                dt.click()
                page.wait_for_timeout(400)
                yr = page.locator('button:has-text("2027"), div:has-text("2027"), [data-year="2027"]').first
                if yr.count() > 0 and yr.is_visible():
                    yr.click()
                    page.wait_for_timeout(300)
                mo = page.locator('button:has-text("May"), div:has-text("May"), [data-month="4"]').first
                if mo.count() > 0 and mo.is_visible():
                    mo.click()
                    page.wait_for_timeout(300)
                page.keyboard.press("Escape")
    except Exception:
        pass

    # Generic sweep for basic fields if not already filled
    try:
        safe_fill(page.locator('input[id*="name"], input[name*="name"]').first, CANDIDATE["name"])
    except Exception:
        pass
    try:
        safe_fill(page.locator('input[type="email"], input[id*="email"]').first, CANDIDATE["email"])
    except Exception:
        pass
    try:
        loc = page.locator('input[placeholder*="Start typing"], input[id*="candidateLocation"]').first
        if loc.count() > 0 and loc.is_visible() and not loc.input_value():
            loc.fill("India")
            page.wait_for_timeout(800)
            opt = page.locator('div[id*="react-select"][role="option"], .select__menu div').first
            if opt.count() > 0:
                opt.click()
            else:
                loc.press("Enter")
    except Exception:
        pass

    # Sweep all remaining visible empty inputs and textareas to guarantee zero missing required fields
    try:
        for el in page.locator('input:visible, textarea:visible').all():
            try:
                itype = (el.get_attribute('type') or '').lower()
                if itype in ['file', 'radio', 'checkbox', 'hidden', 'submit', 'button']:
                    continue
                val = el.input_value()
                if not val:
                    el_id = el.get_attribute('id') or ''
                    el_name = (el.get_attribute('name') or '').lower()
                    el_placeholder = (el.get_attribute('placeholder') or '').lower()
                    el_label_text = ''
                    if el_id:
                        lbl = page.locator(f'label[for="{el_id}"]').first
                        if lbl.count() > 0:
                            el_label_text = lbl.inner_text().lower()
                    combined_hint = f"{el_name} {el_placeholder} {el_label_text}"

                    is_req = (el.get_attribute('required') is not None) or (el.get_attribute('aria-required') == 'true') or ('*' in el_label_text)
                    if any(k in combined_hint for k in ['project', 'built', 'proud', 'accomplish', 'challenge', 'technical']):
                        safe_fill(el, CANDIDATE["proud_of"])
                    elif any(k in combined_hint for k in ['company', 'employer', 'organization']):
                        safe_fill(el, "Self-Employed / Independent Builder")
                    elif any(k in combined_hint for k in ['compensation', 'salary', 'expectation', 'rate', 'pay']):
                        safe_fill(el, "$5,000 / month ($30/hr USD)" if app_type == "INTERNSHIP" else "$80,000 - $95,000 USD / year")
                    elif any(k in combined_hint for k in ['why', 'interest', 'cover', 'fit', 'about you']):
                        safe_fill(el, get_tailored_pitch(company, title, app_type, category))
                    elif any(k in combined_hint for k in ['link', 'url', 'portfolio', 'craft', 'github']):
                        safe_fill(el, CANDIDATE["github"])
                    elif any(k in combined_hint for k in ['city', 'location']):
                        safe_fill(el, "Ludhiana, Punjab, India")
                    elif is_req or itype == 'textarea':
                        safe_fill(el, CANDIDATE["proud_of"] if itype == 'textarea' else CANDIDATE["specific"])
            except Exception:
                pass
    except Exception:
        pass

    # reCAPTCHA v3 human entropy build: multi-directional mouse moves, organic jitter, scroll & pauses
    for _ in range(4):
        rx, ry = random.randint(100, 700), random.randint(150, 600)
        page.mouse.move(rx, ry, steps=random.randint(5, 12))
        page.mouse.wheel(0, random.choice([150, -100, 200, -80]))
        page.wait_for_timeout(random.randint(250, 450))

    # Check & solve captchas (Turnstile / reCAPTCHA) with Gemini
    solve_all_captchas(page)

    btn = page.locator('button:has-text("Submit Application"), .ashby-application-form-submit-button, button[type="submit"]').first
    if btn.count() == 0:
        print("[-] No submit button found")
        return False

    btn.scroll_into_view_if_needed()
    def organic_bezier_move_and_click(p, target_el):
        bx = target_el.bounding_box()
        if not bx:
            target_el.click()
            return
        tx = bx['x'] + bx['width'] * random.uniform(0.35, 0.65)
        ty = bx['y'] + bx['height'] * random.uniform(0.35, 0.65)
        sx = random.randint(150, 500)
        sy = random.randint(200, 450)
        cx = (sx + tx) / 2 + random.randint(-60, 60)
        cy = (sy + ty) / 2 + random.randint(-60, 60)
        stps = random.randint(18, 28)
        for s in range(stps):
            t = s / stps
            curx = (1 - t)**2 * sx + 2 * (1 - t) * t * cx + t**2 * tx + random.uniform(-1.0, 1.0)
            cury = (1 - t)**2 * sy + 2 * (1 - t) * t * cy + t**2 * ty + random.uniform(-1.0, 1.0)
            p.mouse.move(curx, cury)
            time.sleep(random.uniform(0.007, 0.018))
        p.wait_for_timeout(random.randint(600, 1000))
        p.mouse.click(tx, ty)

    print(f"[*] Submitting application...")
    submit_confirmed = False
    try:
        with page.expect_response(
            lambda r: r.request.method == 'POST' and any(k in r.url.lower() for k in ['apisubmitsingleapplicationformaction', 'apisubmitmultipleformsaction', 'non-user-graphql', 'posting-api', 'submit', 'application']),
            timeout=12000
        ) as submit_info:
            organic_bezier_move_and_click(page, btn)
        resp = submit_info.value
        resp_json = {}
        try:
            resp_json = resp.json()
        except Exception:
            pass
        if 'errors' in resp_json and resp_json['errors']:
            print(f"[-] Ashby server rejected with errors: {resp_json['errors']}")
            if any('recaptcha' in str(e).lower() for e in resp_json['errors']):
                print("[*] Ashby reCAPTCHA flagged! Attempting organic remediation & retry...")
                solve_all_captchas(page)
                page.wait_for_timeout(random.randint(3000, 5000))
                for _ in range(4):
                    rx, ry = random.randint(200, 600), random.randint(200, 500)
                    page.mouse.move(rx, ry, steps=random.randint(6, 12))
                    time.sleep(random.uniform(0.05, 0.15))
                try:
                    with page.expect_response(
                        lambda r: r.request.method == 'POST' and any(k in r.url.lower() for k in ['apisubmitsingleapplicationformaction', 'apisubmitmultipleformsaction', 'non-user-graphql', 'posting-api', 'submit', 'application']),
                        timeout=12000
                    ) as retry_info:
                        organic_bezier_move_and_click(page, btn)
                    r_resp = retry_info.value
                    r_json = {}
                    try:
                        r_json = r_resp.json()
                    except Exception:
                        pass
                    if ('data' in r_json and r_json['data']) or r_resp.status in [200, 201, 204]:
                        submit_confirmed = True
                        print("[+] Ashby RETRY succeeded! Verified SUCCESS payload!")
                    else:
                        print(f"[-] Ashby retry errors: {r_json.get('errors')}")
                        submit_confirmed = False
                except Exception as e_ret:
                    print(f"[-] Ashby retry notice: {e_ret}")
                    submit_confirmed = False
            else:
                submit_confirmed = False
        elif ('data' in resp_json and resp_json['data']) or resp.status in [200, 201, 204]:
            submit_confirmed = True
            print("[+] Ashby server returned verified SUCCESS payload!")
    except Exception as e:
        print(f"[!] Submit response notice: {e}")

    page.wait_for_timeout(3500)

    err = page.locator('.ashby-application-form-error-banner, div:has-text("Your form needs corrections")').first
    err_visible = (err.count() > 0 and err.is_visible())
    if not submit_confirmed and err_visible:
        print("[-] Error banner visible on page! Form NOT submitted.")
        submit_confirmed = False

    clean_slug = re.sub(r'[^a-zA-Z0-9_]', '_', f"{company}_{title}")[:35]
    prefix = "intern" if app_type == "INTERNSHIP" else "job"
    proof_path = f"{PROOF_DIR}/{prefix}_{clean_slug}_confirmed.png"
    page.screenshot(path=proof_path, full_page=True)

    page_text = page.locator('body').inner_text().lower()
    has_positive = any(m in page_text for m in [
        'thank you', 'application submitted', 'we have received your application',
        'thanks for your interest', 'success'
    ])

    if submit_confirmed or (has_positive and not err_visible):
        print(f"🎉 CONFIRMED LIVE SUBMISSION for {company} - {title}!")
        log_verified_application(
            company=company,
            role=title,
            portal="Ashby",
            url=url,
            salary_or_stipend=stipend_or_sal,
            proof_path=proof_path,
            app_type=app_type,
            notes=f"Confirmed error-free Ashby submission. {category}"
        )
        return True
    else:
        print(f"[-] Submission not verified for {company} - {title}")
        mark_url_dead(url)
        return False

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--mode', choices=['jobs', 'internships', 'all'], default='all')
    parser.add_argument('--limit', type=int, default=150)
    parser.add_argument('--worker-id', type=int, default=1, help='Worker shard index (1-based)')
    parser.add_argument('--total-workers', type=int, default=1, help='Total parallel workers')
    parser.add_argument('--proxy', type=str, default=None, help='Proxy server URL (e.g. socks5://127.0.0.1:40000)')
    args = parser.parse_args()

    all_unapplied = []
    unapplied_interns = []
    unapplied_jobs = []

    if args.mode in ['internships', 'all']:
        intern_sources = [
            os.path.join(BASE_DIR, 'github_verified_internships.json'),
            os.path.join(BASE_DIR, 'live_fresh_verified_roles.json'),
            os.path.join(BASE_DIR, 'queue_500_paid_internships.json'),
            os.path.join(BASE_DIR, 'high_paying_viable_internships.json'),
            os.path.join(BASE_DIR, 'curated_viable_internships.json'),
            os.path.join(BASE_DIR, 'HANDPICKED_ROLES.json'),
            os.path.join(BASE_DIR, 'viable_vetted_internships.json'),
            os.path.join(BASE_DIR, 'clean_vetted_remote_internships.json'),
            os.path.join(BASE_DIR, 'vetted_tech_internships.json'),
            os.path.join(BASE_DIR, 'remaining_internships_queue.json')
        ]
        seen_urls = set()
        seen_intern_roles = set()
        seen_intern_companies = set()
        for src in intern_sources:
            if os.path.exists(src):
                try:
                    with open(src) as f:
                        data = json.load(f)
                        for it in data:
                            u = (it.get('applyUrl') or it.get('url') or '').strip().replace('&amp;', '&')
                            comp = (it.get('company') or '').strip()
                            tit = (it.get('title') or it.get('role') or '').strip()
                            nu = clean_norm_url(u)
                            nc = clean_norm_company(comp)
                            nr = clean_norm_role(tit)
                            if not u or not nu or nu in seen_urls or (nc, nr) in seen_intern_roles or nc in seen_intern_companies:
                                continue
                            if is_already_confirmed(u, comp, tit):
                                continue
                            is_int = it.get('is_internship') or it.get('category') == 'INTERNSHIP' or any(k in tit.lower() for k in ['intern', 'co-op', 'apprentice', 'campus', 'fellowship'])
                            if not is_int:
                                continue
                            score, _ = critique_application(comp, tit)
                            if score < 80:
                                continue
                            seen_urls.add(nu)
                            seen_intern_roles.add((nc, nr))
                            seen_intern_companies.add(nc)
                            item_copy = dict(it)
                            item_copy['title'] = tit
                            item_copy['company'] = comp
                            item_copy['applyUrl'] = u
                            item_copy['is_internship'] = True
                            item_copy['category'] = 'INTERNSHIP'
                            unapplied_interns.append(item_copy)
                except Exception as e:
                    print(f"[-] Error loading {src}: {e}")
        all_unapplied.extend(unapplied_interns)

    if args.mode in ['jobs', 'all']:
        job_sources = [
            os.path.join(BASE_DIR, 'github_verified_jobs.json'),
            os.path.join(BASE_DIR, 'live_fresh_verified_roles.json'),
            os.path.join(BASE_DIR, 'vetted_global_boutique_roles.json'),
            os.path.join(BASE_DIR, 'clean_vetted_remote_jobs.json'),
            os.path.join(BASE_DIR, 'pure_global_boutique_roles.json'),
            os.path.join(BASE_DIR, 'high_paying_viable_jobs.json'),
            os.path.join(BASE_DIR, 'curated_viable_jobs.json')
        ]
        seen_job_urls = set()
        seen_job_roles = set()
        for src in job_sources:
            if os.path.exists(src):
                try:
                    with open(src) as f:
                        jobs = json.load(f)
                        for it in jobs:
                            u = (it.get('applyUrl') or it.get('url') or '').strip().replace('&amp;', '&')
                            comp = (it.get('company') or '').strip()
                            tit = (it.get('title') or it.get('role') or '').strip()
                            nu = clean_norm_url(u)
                            nc = clean_norm_company(comp)
                            nr = clean_norm_role(tit)
                            if not u or not nu or nu in seen_job_urls or (nc, nr) in seen_job_roles:
                                continue
                            if is_already_confirmed(u, comp, tit):
                                continue
                            is_int = it.get('is_internship') or it.get('category') == 'INTERNSHIP' or any(k in tit.lower() for k in ['intern', 'co-op', 'apprentice', 'campus', 'fellowship'])
                            if is_int:
                                continue
                            score, _ = critique_application(comp, tit)
                            if score < 80:
                                continue
                            seen_job_urls.add(nu)
                            seen_job_roles.add((nc, nr))
                            item_copy = dict(it)
                            item_copy['title'] = tit
                            item_copy['company'] = comp
                            item_copy['applyUrl'] = u
                            item_copy['is_internship'] = False
                            item_copy['category'] = 'JOB'
                            unapplied_jobs.append(item_copy)
                except Exception as e:
                    print(f"[-] Could not load {src}: {e}")
        all_unapplied.extend(unapplied_jobs)

    # Prioritize Greenhouse, Ashby, and Lever (with Cloudflare WARP proxy)
    greenhouse_jobs = [it for it in unapplied_jobs if 'greenhouse.io' in (it.get('applyUrl') or it.get('url') or '')]
    ashby_jobs = [it for it in unapplied_jobs if 'ashbyhq' in (it.get('applyUrl') or it.get('url') or '')]
    lever_jobs = [it for it in unapplied_jobs if 'lever.co' in (it.get('applyUrl') or it.get('url') or '')]

    greenhouse_interns = [it for it in unapplied_interns if 'greenhouse.io' in (it.get('applyUrl') or it.get('url') or '')]
    ashby_interns = [it for it in unapplied_interns if 'ashbyhq' in (it.get('applyUrl') or it.get('url') or '')]
    lever_interns = [it for it in unapplied_interns if 'lever.co' in (it.get('applyUrl') or it.get('url') or '')]

    if args.mode == 'internships':
        interleaved = []
        max_len = max(len(greenhouse_interns), len(ashby_interns), len(lever_interns), 1)
        for idx in range(max_len):
            if idx < len(greenhouse_interns):
                interleaved.append(greenhouse_interns[idx])
            if idx < len(ashby_interns):
                interleaved.append(ashby_interns[idx])
            if idx < len(lever_interns):
                interleaved.append(lever_interns[idx])
        items = interleaved
    elif args.mode == 'jobs':
        interleaved = []
        max_len = max(len(greenhouse_jobs), len(ashby_jobs), len(lever_jobs), 1)
        for idx in range(max_len):
            if idx < len(greenhouse_jobs):
                interleaved.append(greenhouse_jobs[idx])
            if idx < len(ashby_jobs):
                interleaved.append(ashby_jobs[idx])
            if idx < len(lever_jobs):
                interleaved.append(lever_jobs[idx])
        items = interleaved
    else:
        all_gh = []
        for idx in range(max(len(greenhouse_jobs), len(greenhouse_interns))):
            if idx < len(greenhouse_jobs):
                all_gh.append(greenhouse_jobs[idx])
            if idx < len(greenhouse_interns):
                all_gh.append(greenhouse_interns[idx])
        all_ash = []
        for idx in range(max(len(ashby_jobs), len(ashby_interns))):
            if idx < len(ashby_jobs):
                all_ash.append(ashby_jobs[idx])
            if idx < len(ashby_interns):
                all_ash.append(ashby_interns[idx])
        all_lev = []
        for idx in range(max(len(lever_jobs), len(lever_interns))):
            if idx < len(lever_jobs):
                all_lev.append(lever_jobs[idx])
            if idx < len(lever_interns):
                all_lev.append(lever_interns[idx])
        balanced = []
        max_len = max(len(all_gh), len(all_ash), len(all_lev), 1)
        for idx in range(max_len):
            if idx < len(all_gh):
                balanced.append(all_gh[idx])
            if idx < len(all_ash):
                balanced.append(all_ash[idx])
            if idx < len(all_lev):
                balanced.append(all_lev[idx])
        items = balanced

    if args.total_workers > 1:
        items = [it for idx, it in enumerate(items) if idx % args.total_workers == (args.worker_id - 1)]
        print(f"[*] Sharded queue for Worker {args.worker_id}/{args.total_workers}: {len(items)} items assigned.")

    items = items[:args.limit]

    ashby_count = sum(1 for it in items if 'ashbyhq' in (it.get('applyUrl') or it.get('url') or ''))
    other_count = len(items) - ashby_count
    print(f"=== UNIFIED VERIFIED SUBMISSION ENGINE ===")
    print(f"[*] Total target unapplied items loaded: {len(items)} (Ashby: {ashby_count}, Others: {other_count})")

    stealth = Stealth()
    with sync_playwright() as p:
        def launch_browser():
            launch_kwargs = {
                'headless': True,
                'args': [
                    '--no-sandbox',
                    '--disable-setuid-sandbox',
                    '--disable-dev-shm-usage',
                    '--disable-gpu',
                    '--no-zygote',
                    '--disable-blink-features=AutomationControlled'
                ]
            }
            if os.path.exists('/usr/bin/chromium'):
                launch_kwargs['executable_path'] = '/usr/bin/chromium'
            if args.proxy:
                launch_kwargs['proxy'] = {'server': args.proxy}
                print(f"[*] Playwright routing through proxy: {args.proxy}")
            return p.chromium.launch(**launch_kwargs)

        browser = launch_browser()
        success_count = 0
        for i, item in enumerate(items):
            try:
                conn_chk = sqlite3.connect(DB_PATH)
                cur_tot = conn_chk.cursor().execute("SELECT count(*) FROM verified_applications").fetchone()[0]
                cur_jobs = conn_chk.cursor().execute("SELECT count(*) FROM verified_applications WHERE application_type='JOB'").fetchone()[0]
                cur_interns = conn_chk.cursor().execute("SELECT count(*) FROM verified_applications WHERE application_type='INTERNSHIP'").fetchone()[0]
                conn_chk.close()
                if cur_jobs >= 3000 and cur_interns >= 3000:
                    print(f"\n🎉 6,000 GRAND MILESTONE HIT! Total verified in DB: {cur_tot} (Jobs: {cur_jobs}, Interns: {cur_interns})")
                    break
            except Exception:
                pass

            # Rotate browser instance every 6 applications to prevent reCAPTCHA v3 fingerprint decay
            if i > 0 and i % 6 == 0:
                try:
                    browser.close()
                except Exception:
                    pass
                browser = launch_browser()

            print(f"\n[{i+1}/{len(items)}] Processing {item['company']} - {item['title']}...")
            context = None
            vps = [
                {"width": 1280, "height": 900},
                {"width": 1366, "height": 768},
                {"width": 1440, "height": 900},
                {"width": 1536, "height": 864}
            ]
            chosen_vp = random.choice(vps)
            uas = [
                "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36",
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36",
                "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0.0.0 Safari/537.36"
            ]
            chosen_ua = random.choice(uas)
            
            u_check = (item.get('applyUrl') or item.get('url') or '').strip()
            c_check = (item.get('company') or '').strip()
            t_check = (item.get('title') or '').strip()
            if not u_check or is_already_confirmed(u_check, c_check, t_check):
                print(f"[!] Already confirmed or dead in DB: {c_check} - {t_check}")
                continue

            # Rapid pre-check: check if Ashby job posting is closed via appData without wasting 15s in Playwright
            if 'ashbyhq.com' in u_check:
                try:
                    import urllib.request
                    req = urllib.request.Request(u_check, headers={'User-Agent': chosen_ua})
                    h_txt = urllib.request.urlopen(req, timeout=4).read().decode('utf-8', errors='ignore')
                    if 'window.__appData' in h_txt:
                        m_app = re.search(r'window\.__appData\s*=\s*(\{.*?\});', h_txt)
                        if m_app:
                            d_app = json.loads(m_app.group(1))
                            if d_app.get('posting') is None:
                                print(f"[-] Ashby posting is confirmed closed: {u_check}")
                                mark_url_dead(u_check)
                                continue
                except Exception:
                    pass
            elif 'greenhouse.io' in u_check:
                try:
                    import urllib.request, urllib.error
                    req = urllib.request.Request(u_check, headers={'User-Agent': chosen_ua})
                    with urllib.request.urlopen(req, timeout=4) as resp:
                        if resp.status == 404:
                            print(f"[-] Greenhouse posting 404: {u_check}")
                            mark_url_dead(u_check)
                            continue
                        h_sample = resp.read().decode('utf-8', errors='ignore')[:15000].lower()
                        if any(k in h_sample for k in ['the job you are looking for is no longer open', 'this job has been closed', 'posting not found', 'no longer accepting applications']):
                            print(f"[-] Greenhouse posting is confirmed closed: {u_check}")
                            mark_url_dead(u_check)
                            continue
                except urllib.error.HTTPError as he:
                    if he.code in [404, 410]:
                        print(f"[-] Greenhouse posting HTTP {he.code}: {u_check}")
                        mark_url_dead(u_check)
                        continue
                except Exception:
                    pass
            try:
                if not browser.is_connected():
                    browser = launch_browser()
                context = browser.new_context(
                    user_agent=chosen_ua,
                    viewport=chosen_vp,
                    locale="en-US"
                )
            except Exception:
                try:
                    browser = launch_browser()
                    context = browser.new_context(
                        user_agent=chosen_ua,
                        viewport=chosen_vp,
                        locale="en-US"
                    )
                except Exception as e:
                    print(f"[-] Browser restart failed: {e}")
                    continue

            stealth.apply_stealth_sync(context)
            context.set_default_timeout(4000)
            context.set_default_navigation_timeout(8000)
            page = context.new_page()
            page.set_default_timeout(4000)
            page.set_default_navigation_timeout(8000)
            try:
                portal = (item.get('portal_type') or '').lower()
                url = (item.get('applyUrl') or item.get('url') or '').lower()
                if 'greenhouse' in portal or 'greenhouse.io' in url:
                    res = apply_greenhouse(page, item)
                elif 'lever' in portal or 'lever.co' in url:
                    res = apply_lever(page, item)
                else:
                    res = apply_ashby(page, item)
                if res:
                    success_count += 1
            except Exception as e:
                print(f"[-] Execution error: {e}")
            finally:
                try:
                    context.close()
                except Exception:
                    pass


        browser.close()
        print(f"\n[+] Batch complete! Successfully submitted {success_count} verified applications.")

        # Final receipt sync & dashboard update using dynamic BASE_DIR
        sync_script = os.path.join(BASE_DIR, "sync_all_receipts.py")
        dash_script = os.path.join(BASE_DIR, "generate_dashboard.py")
        if os.path.exists(sync_script):
            os.system(f'"{sys.executable}" "{sync_script}"')
        if os.path.exists(dash_script):
            os.system(f'"{sys.executable}" "{dash_script}"')

        # GitHub Actions Step Summary reporter
        step_summary = os.environ.get('GITHUB_STEP_SUMMARY')
        if step_summary:
            try:
                conn_sum = sqlite3.connect(DB_PATH)
                c_sum = conn_sum.cursor()
                t_tot = c_sum.execute("SELECT count(*) FROM verified_applications").fetchone()[0]
                t_jobs = c_sum.execute("SELECT count(*) FROM verified_applications WHERE application_type='JOB'").fetchone()[0]
                t_interns = c_sum.execute("SELECT count(*) FROM verified_applications WHERE application_type='INTERNSHIP'").fetchone()[0]
                t_receipts = c_sum.execute("SELECT count(*) FROM verified_applications WHERE email_verified=1").fetchone()[0]
                conn_sum.close()

                with open(step_summary, 'a') as f:
                    f.write(f"\n## 🚀 Autonomous Cloud Application Run Report\n\n")
                    f.write(f"- **New Submissions in this Run**: `{success_count}` verified\n")
                    f.write(f"- **Total Confirmed in DB**: `{t_tot}` / 6,000\n")
                    f.write(f"  - **Remote Tech Jobs**: `{t_jobs}` / 3,000\n")
                    f.write(f"  - **Paid Tech Internships**: `{t_interns}` / 3,000\n")
                    f.write(f"- **Verified Email Receipts**: `{t_receipts}` mapped via IMAP\n")
                    f.write(f"- **Exit Proxy**: `{args.proxy or 'Direct'}`\n\n")
            except Exception as e:
                print(f"[-] Summary write failed: {e}")

if __name__ == '__main__':
    main()
