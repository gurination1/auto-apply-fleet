#!/usr/bin/env python3
"""
Master SWE Resume Generator for Gurdharam Jeet Singh
Engineered to the 100/100 Modern SWE Benchmark (Jake's Resume / Overleaf Standard):
- Complete Full-Spectrum Web Architecture Portfolio:
  1. EduCore ERP (React 19, TypeScript, Express, MariaDB/SQLite Two-Tier Failover, RBAC, Railway)
  2. Enterprise WhatsApp CRM (Official Meta Cloud API, Supabase PostgreSQL, 24h Radar)
  3. Dream Heights (Luxury Architectural Portal, React 18, Framer Motion, Lenis Smooth Scroll, Spatial Pins)
  4. SOLUM Minerals & Branders Suite (Next.js 15, App Router, 99+ Lighthouse, Zero Layout Shift)
- Consultancy: Real-Time Telephony Voice AI (<700ms Latency) & High-Throughput BullMQ Queues (25k+ Events)
- Zero Trading/Crypto content (100% targeted to enterprise tech, scaleups, and web systems)
- 9.1pt Body Typography, 1.22 Line-Height, 0.38in x 0.44in Balanced Margins (Zero Over-Densing)
- Chromium Headless Clean Export with --no-pdf-header-footer (Strict 1-Page Guarantee)
"""

import subprocess
import pypdf
import os

html_content = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Gurdharam Jeet Singh - Resume</title>
<style>
  @page {
    size: letter portrait;
    margin: 0.38in 0.44in 0.38in 0.44in;
  }
  * {
    box-sizing: border-box;
  }
  body {
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
    font-size: 9.1pt;
    line-height: 1.22;
    color: #111827;
    margin: 0;
    padding: 0;
    background: #ffffff;
  }
  .header {
    text-align: center;
    margin-bottom: 4px;
  }
  h1 {
    font-size: 16.5pt;
    font-weight: 800;
    letter-spacing: 0.5px;
    color: #0f172a;
    margin: 0 0 2px 0;
    text-transform: uppercase;
  }
  .subtitle {
    font-size: 9.4pt;
    font-weight: 600;
    color: #334155;
    margin-bottom: 2.5px;
  }
  .contact-bar {
    font-size: 8.5pt;
    color: #475569;
  }
  .contact-bar a {
    color: #0284c7;
    text-decoration: none;
    font-weight: 500;
  }
  h2 {
    font-size: 9.6pt;
    font-weight: 700;
    text-transform: uppercase;
    color: #0f172a;
    border-bottom: 1.5px solid #0f172a;
    padding-bottom: 1px;
    margin: 5.5px 0 3px 0;
    letter-spacing: 0.4px;
  }
  .skill-line {
    font-size: 8.8pt;
    line-height: 1.21;
    margin-bottom: 2px;
  }
  .skill-line strong {
    color: #0f172a;
  }
  .entry {
    margin-bottom: 3.8px;
  }
  .entry-header {
    display: flex;
    justify-content: space-between;
    font-size: 9.1pt;
    font-weight: 700;
    color: #0f172a;
  }
  .entry-subheader {
    display: flex;
    justify-content: space-between;
    font-size: 8.5pt;
    font-style: italic;
    color: #475569;
    margin-bottom: 1.5px;
  }
  .entry-subheader a {
    color: #0284c7;
    text-decoration: none;
    font-style: normal;
    font-weight: 500;
  }
  ul {
    margin: 0;
    padding-left: 14px;
  }
  li {
    font-size: 8.5pt;
    line-height: 1.20;
    color: #334155;
    margin-bottom: 1px;
  }
  li strong {
    color: #0f172a;
  }
</style>
</head>
<body>
  <div class="header">
    <h1>Gurdharam Jeet Singh</h1>
    <div class="subtitle">Full-Stack Software Engineer &bull; Web Systems &amp; Spatial Frontend Architect</div>
    <div class="contact-bar">
      Bathinda / Muktsar, Punjab, India &bull; +91 90411 72159 &bull; <a href="mailto:gurination1@gmail.com">gurination1@gmail.com</a> &bull; <a href="https://github.com/gurination1">github.com/gurination1</a> &bull; <a href="https://linkedin.com/in/gurdharam">linkedin.com/in/gurdharam</a> &bull; <a href="https://gurdharam.com">gurdharam.com</a>
    </div>
  </div>

  <h2>Technical Skills</h2>
  <div class="skill-line"><strong>Languages &amp; Core:</strong> TypeScript, JavaScript (ES6+), Python, Go, SQL, HTML5, CSS3</div>
  <div class="skill-line"><strong>Frontend &amp; Spatial Web:</strong> React 19, Next.js 15 (App Router, Server Components), Tailwind CSS 4, Vite 6, Framer Motion, Lenis Smooth Scroll, Three.js, WebGL2 (Camera Kit), Core Web Vitals (LCP, CLS &lt; 0.02)</div>
  <div class="skill-line"><strong>Backend &amp; Distributed Systems:</strong> Node.js, Express, FastAPI, PostgreSQL, Supabase, MariaDB/SQLite Failover, Redis &amp; BullMQ, WebSockets, REST APIs, Docker, Linux/Bash</div>
  <div class="skill-line"><strong>Cloud &amp; Platform Infrastructure:</strong> Official Meta WhatsApp Cloud API (WABA), GitHub Actions 24/7 CI/CD Fleets, Railway, AWS (S3, Lambda), Exotel Telephony, Gemini AI</div>

  <h2>Key Production Platforms &amp; Systems</h2>

  <div class="entry">
    <div class="entry-header">
      <span>SOLUM Minerals &mdash; Procedural 3D WebGL Bio-Carbon Platform</span>
      <span>2026 (Oct) &ndash; Present</span>
    </div>
    <div class="entry-subheader">
      <span>Lead Frontend Architect &bull; Next.js 15, Three.js, WebGL2, Tailwind CSS</span>
      <span><a href="https://github.com/gurination1/solum-minerals">Open Source</a></span>
    </div>
    <ul>
      <li><strong>Procedural 3D WebGL Rendering:</strong> Engineered code-generated Three.js WebGL tablet model synthesizing 1024x1024 noise textures procedurally in memory via Canvas API, eliminating 15MB+ of 3D asset downloads.</li>
      <li><strong>Scroll Kinematics &amp; Core Web Vitals:</strong> Implemented scroll-linked camera interpolation and river kinematics in Next.js 15 App Router, achieving a 99+ Lighthouse score with zero layout shift (CLS &lt; 0.02) and sub-second FCP.</li>
    </ul>
  </div>

  <div class="entry">
    <div class="entry-header">
      <span>Dream Heights &mdash; Luxury Spatial Real Estate Portal</span>
      <span>2025 &ndash; Present</span>
    </div>
    <div class="entry-subheader">
      <span>Spatial &amp; Frontend Architect &bull; React 18, TypeScript, Tailwind CSS, Framer Motion, Lenis</span>
      <span><a href="https://github.com/gurination1/dreamheights">Open Source</a></span>
    </div>
    <ul>
      <li><strong>Spatial Architectural Pins &amp; Navigation:</strong> Built luxury residence exploration portal in React 18 and Vite 6 featuring spatial residence pins, dynamic floor-plan modals, and custom interactive architectural emblems.</li>
      <li><strong>Hardware-Accelerated Physics &amp; Inertial Momentum:</strong> Integrated Lenis 1.1 smooth scrolling with Framer Motion layout transitions, maintaining silky 60 FPS rendering across high-DPI viewports.</li>
    </ul>
  </div>

  <div class="entry">
    <div class="entry-header">
      <span>EduCore — Enterprise College Management ERP</span>
      <span>2025 &ndash; Present</span>
    </div>
    <div class="entry-subheader">
      <span>Lead Full-Stack Architect &bull; React 19, TypeScript, Express, PostgreSQL, MariaDB, Railway</span>
      <span><a href="https://github.com/gurination1/ERP_educore">Open Source</a></span>
    </div>
    <ul>
      <li><strong>Dual-Engine Relational Architecture:</strong> Engineered multi-tenant campus ERP supporting PostgreSQL and MariaDB connection pools with automatic connection health recovery, parameterized query sanitization, and sub-15ms latency.</li>
      <li><strong>9-Role RBAC &amp; Dynamic Schema Builder:</strong> Built strict JWT role-based access control across 9 permission tiers, paired with a runtime form schema builder and forensic audit trail logging actor IP, device profile, and data diffs.</li>
    </ul>
  </div>

  <div class="entry">
    <div class="entry-header">
      <span>Enterprise WhatsApp AI &amp; Lead Management CRM</span>
      <span>2025 &ndash; Present</span>
    </div>
    <div class="entry-subheader">
      <span>Lead Architect &bull; Meta Cloud API, Node.js, Express, Supabase (PostgreSQL)</span>
      <span>Production Platform</span>
    </div>
    <ul>
      <li><strong>Official Meta Cloud API Architecture:</strong> Engineered multi-tenant CRM gateway integrating Meta Graph Cloud API (WABA ID: 106690...), handling bi-directional messaging, template dispatch, and HMAC-verified webhooks.</li>
      <li><strong>24-Hour Autonomous Follow-Up Radar:</strong> Built real-time engagement engine with dynamic cadences (24h/36h/48h/72h), tracking lead conversation states and triggering automated follow-ups via Supabase.</li>
    </ul>
  </div>

  <h2>Work Experience</h2>

  <div class="entry">
    <div class="entry-header">
      <span>Gurdharam Software Consultancy &bull; Systems &amp; Web Engineer</span>
      <span>2025 &ndash; Present</span>
    </div>
    <div class="entry-subheader">
      <span>Independent Software Consultancy &bull; Remote</span>
      <span>Punjab, India</span>
    </div>
    <ul>
      <li><strong>Telephonic Voice AI &amp; High-Throughput Queues:</strong> Built real-time telephony agent over Exotel WebSockets, SIP, and VoIP, achieving &lt;700ms turn latency across Sarvam AI Indic LLMs, Groq LPU, and Silero VAD, with Redis/BullMQ processing 25,000+ daily events.</li>
      <li><strong>Branders Digital Agency Platform:</strong> Architected client agency platform featuring interactive Three.js 3D viewport, CSS3 physics navigation, and mobile-hardened layouts designed for high-conversion client acquisition.</li>
    </ul>
  </div>

  <h2>Education &amp; Credentials</h2>

  <div class="entry">
    <div class="entry-header">
      <span>Baba Farid Group of Institutions (BFGI) &mdash; B.Sc. in Computer Science</span>
      <span>Expected May 2027</span>
    </div>
    <div class="entry-subheader">
      <span>Core: Data Structures &amp; Algorithms, Database Systems, Computer Networks, Operating Systems</span>
      <span>Punjab, India</span>
    </div>
  </div>

  <div class="skill-line" style="margin-top: 2px;">
    <strong>Credentials &amp; Verification:</strong> Meta Verified Business Entity &bull; Official WhatsApp Business Platform Developer &bull; Sarvam AI Startup Partner &bull; Govt. MSME Registered Enterprise (UDYAM-PB-03-0079744).
  </div>
</body>
</html>"""

html_path = "/root/gurdharam_resume/Gurdharam_Jeet_Singh_Resume.html"
pdf_path = "/root/gurdharam_resume/Gurdharam_Jeet_Singh_Resume.pdf"
md_path = "/root/gurdharam_resume/Gurdharam_Jeet_Singh_Resume.md"

with open(html_path, "w") as f:
    f.write(html_content)

print("[+] Wrote balanced master HTML resume.")

# Generate PDF with Chromium headless without header/footer
cmd = [
    "/usr/bin/chromium",
    "--headless",
    "--disable-gpu",
    "--no-sandbox",
    "--no-pdf-header-footer",
    f"--print-to-pdf={pdf_path}",
    html_path
]
subprocess.run(cmd, check=True)
print("[+] Generated clean single-page PDF via Chromium.")

# Verify page count
reader = pypdf.PdfReader(pdf_path)
page_count = len(reader.pages)
print(f"[+] Total PDF pages: {page_count}")
assert page_count == 1, f"Resume exceeded 1 page! Count: {page_count}"

# Generate companion Markdown version
md_content = """# Gurdharam Jeet Singh
**Full-Stack Software Engineer • Web Systems & Spatial Frontend Architect**  
Bathinda / Muktsar, Punjab, India • +91 90411 72159 • [gurination1@gmail.com](mailto:gurination1@gmail.com) • [github.com/gurination1](https://github.com/gurination1) • [linkedin.com/in/gurdharam](https://linkedin.com/in/gurdharam) • [gurdharam.com](https://gurdharam.com)

---

## Technical Skills
- **Languages & Core:** TypeScript, JavaScript (ES6+), Python, Go, SQL, HTML5, CSS3
- **Frontend & Spatial Web:** React 19, Next.js 15 (App Router, Server Components), Tailwind CSS 4, Vite 6, Framer Motion, Lenis Smooth Scroll, Three.js, WebGL2 (Camera Kit), Core Web Vitals (LCP, CLS < 0.02)
- **Backend & Distributed Systems:** Node.js, Express, FastAPI, PostgreSQL, Supabase, MariaDB/SQLite Failover, Redis & BullMQ, WebSockets, REST APIs, Docker, Linux/Bash
- **Cloud & Platform Infrastructure:** Official Meta WhatsApp Cloud API (WABA), GitHub Actions 24/7 CI/CD Fleets, Railway, AWS (S3, Lambda), Exotel Telephony, Gemini AI

---

## Key Production Platforms & Systems

### SOLUM Minerals — Procedural 3D WebGL Bio-Carbon Platform
*Lead Frontend Architect • Next.js 15, Three.js, WebGL2, Tailwind CSS | 2026 (Oct) – Present* [Open Source](https://github.com/gurination1/solum-minerals)
- **Procedural 3D WebGL Rendering:** Engineered code-generated Three.js WebGL tablet model synthesizing 1024x1024 noise textures procedurally in memory via Canvas API, eliminating 15MB+ of 3D asset downloads.
- **Scroll Kinematics & Core Web Vitals:** Implemented scroll-linked camera interpolation and river kinematics in Next.js 15 App Router, achieving a 99+ Lighthouse score with zero layout shift (CLS < 0.02) and sub-second FCP.

### Dream Heights — Luxury Spatial Real Estate Portal
*Spatial & Frontend Architect • React 18, TypeScript, Tailwind CSS, Framer Motion, Lenis | 2025 – Present* [Open Source](https://github.com/gurination1/dreamheights)
- **Spatial Architectural Pins & Navigation:** Built luxury residence exploration portal in React 18 and Vite 6 featuring spatial residence pins, dynamic floor-plan modals, and custom interactive architectural emblems.
- **Hardware-Accelerated Physics & Inertial Momentum:** Integrated Lenis 1.1 smooth scrolling with Framer Motion layout transitions, maintaining silky 60 FPS rendering across high-DPI viewports.

### EduCore — Enterprise College Management ERP
*Lead Full-Stack Architect • React 19, TypeScript, Express, PostgreSQL, MariaDB, Railway | 2025 – Present* [Open Source](https://github.com/gurination1/ERP_educore)
- **Dual-Engine Relational Architecture:** Engineered multi-tenant campus ERP supporting PostgreSQL and MariaDB connection pools with automatic connection health recovery, parameterized query sanitization, and sub-15ms latency.
- **9-Role RBAC & Dynamic Schema Builder:** Built strict JWT role-based access control across 9 permission tiers, paired with a runtime form schema builder and forensic audit trail logging actor IP, device profile, and data diffs.

### Enterprise WhatsApp AI & Lead Management CRM
*Lead Architect • Meta Cloud API, Node.js, Express, Supabase (PostgreSQL) | 2025 – Present*
- **Official Meta Cloud API Architecture:** Engineered multi-tenant CRM gateway integrating Meta Graph Cloud API (WABA ID: 106690...), handling bi-directional messaging, template dispatch, and HMAC-verified webhooks.
- **24-Hour Autonomous Follow-Up Radar:** Built real-time engagement engine with dynamic cadences (24h/36h/48h/72h), tracking lead conversation states and triggering automated follow-ups via Supabase.

---

## Work Experience

### Gurdharam Software Consultancy • Systems & Web Engineer
*Independent Software Consultancy • Remote | Punjab, India | 2025 – Present*
- **Telephonic Voice AI & High-Throughput Queues:** Built real-time telephony agent over Exotel WebSockets, SIP, and VoIP, achieving <700ms turn latency across Sarvam AI Indic LLMs, Groq LPU, and Silero VAD, with Redis/BullMQ processing 25,000+ daily events.
- **Branders Digital Agency Platform:** Architected client agency platform featuring interactive Three.js 3D viewport, CSS3 physics navigation, and mobile-hardened layouts designed for high-conversion client acquisition.

---

## Education & Credentials
- **Baba Farid Group of Institutions (BFGI)** — B.Sc. in Computer Science *(Expected May 2027)*
  - Core: Data Structures & Algorithms, Database Systems, Computer Networks, Operating Systems
- **Credentials & Verification:** Meta Verified Business Entity • Official WhatsApp Business Platform Developer • Sarvam AI Startup Partner • Govt. MSME Registered Enterprise (UDYAM-PB-03-0079744)
"""

with open(md_path, "w") as f:
    f.write(md_content)

print("[+] Wrote Markdown companion resume.")
