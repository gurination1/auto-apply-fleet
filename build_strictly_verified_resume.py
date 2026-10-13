#!/usr/bin/env python3
"""
Master ATS Resume Generator for Gurdharam Jeet Singh
100/100 Benchmark-Engineered Single-Page Architecture:
- Strict 1-Page Letter Budget (Chromium headless with --no-pdf-header-footer)
- Executive Typography: 8.6pt body font, 1.23 line-height, 0.35in x 0.40in balanced margins
- High Recruiter Legibility (Eliminates over-cramming and microscopic text)
- 100% Truthful to Real Production Codebases & GitHub Repositories (@gurination1)
- Featured Enterprise WhatsApp CRM (Official Meta Cloud API, 24h Follow-up Radar, Supabase)
- Standard ATS Taxonomy (Summary, Technical Skills, Key Projects, Experience, Education & Credentials)
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
    margin: 0.35in 0.40in 0.35in 0.40in;
  }
  * {
    box-sizing: border-box;
  }
  body {
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
    font-size: 8.6pt;
    line-height: 1.23;
    color: #1e293b;
    margin: 0;
    padding: 0;
    background: #ffffff;
  }
  .header {
    text-align: center;
    border-bottom: 1.5px solid #0f172a;
    padding-bottom: 3px;
    margin-bottom: 4px;
  }
  h1 {
    font-size: 15.5pt;
    font-weight: 800;
    letter-spacing: 0.6px;
    color: #0f172a;
    margin: 0 0 1px 0;
    text-transform: uppercase;
  }
  .subtitle {
    font-size: 9.0pt;
    font-weight: 600;
    color: #334155;
    margin-bottom: 2.5px;
  }
  .contact-bar {
    font-size: 8.0pt;
    color: #475569;
  }
  .contact-bar a {
    color: #0284c7;
    text-decoration: none;
    font-weight: 500;
  }
  h2 {
    font-size: 9.3pt;
    font-weight: 700;
    text-transform: uppercase;
    color: #0f172a;
    border-bottom: 1px solid #cbd5e1;
    padding-bottom: 1px;
    margin: 5px 0 3px 0;
    letter-spacing: 0.4px;
  }
  .summary {
    font-size: 8.4pt;
    line-height: 1.24;
    color: #334155;
    margin-bottom: 3px;
    text-align: justify;
  }
  .skill-group {
    font-size: 8.2pt;
    line-height: 1.20;
    margin-bottom: 2px;
  }
  .skill-group strong {
    color: #0f172a;
  }
  .item {
    margin-bottom: 4px;
  }
  .item-head {
    display: flex;
    justify-content: space-between;
    font-size: 8.8pt;
    font-weight: 700;
    color: #0f172a;
  }
  .item-subhead {
    display: flex;
    justify-content: space-between;
    font-size: 8.2pt;
    font-style: italic;
    color: #475569;
    margin-bottom: 1.5px;
  }
  .item-subhead a {
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
    font-size: 8.2pt;
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
    <div class="subtitle">Full-Stack Software Engineer &bull; Web Systems &amp; Cloud Automation</div>
    <div class="contact-bar">
      Punjab, India &bull; +91 90411 72159 &bull; <a href="mailto:gurination1@gmail.com">gurination1@gmail.com</a> &bull; <a href="https://github.com/gurination1">github.com/gurination1</a> &bull; <a href="https://linkedin.com/in/gurdharam">linkedin.com/in/gurdharam</a> &bull; <a href="https://gurdharam.com">gurdharam.com</a>
    </div>
  </div>

  <h2>Professional Summary</h2>
  <div class="summary">
    Full-Stack Software Engineer with production experience shipping modern Next.js 15, TypeScript, and Node.js web applications and autonomous cloud automation fleets. Architect of commercial web portals with 99+ Lighthouse scores, enterprise WhatsApp CRM platforms over official Meta Cloud APIs, and real-time distributed pipelines processing 25,000+ daily events. Available immediately for remote Software Engineering internships and full-time roles worldwide.
  </div>

  <h2>Technical Skills</h2>
  <div class="skill-group"><strong>Frontend &amp; UI Systems:</strong> React, Next.js 15 (App Router, Server Components), TypeScript, JavaScript (ES6+), Tailwind CSS, Three.js, WebGL2, HTML5/CSS3, Core Web Vitals (LCP, CLS &lt; 0.02), Lenis Smooth Scroll.</div>
  <div class="skill-group"><strong>Backend &amp; Distributed Architecture:</strong> Node.js, Express, Python (FastAPI, Asyncio), PostgreSQL, Supabase, Redis &amp; BullMQ, WebSockets, REST APIs, Webhook Ingestion, Docker, Linux / Bash.</div>
  <div class="skill-group"><strong>Cloud, DevOps &amp; AI Integration:</strong> GitHub Actions CI/CD (24/7 Cloud Fleets), Official Meta WhatsApp Cloud API (WABA), Gemini API / LLM Orchestration, Voice AI (SIP, WebSockets, Silero VAD), AWS (S3, Lambda), Playwright E2E.</div>

  <h2>Key Engineering Projects</h2>

  <div class="item">
    <div class="item-head">
      <span>Enterprise WhatsApp AI &amp; Lead Management CRM</span>
      <span>2025 &ndash; Present</span>
    </div>
    <div class="item-subhead">
      <span>Lead Architect &bull; Meta Cloud API, Node.js, Express, Supabase (PostgreSQL)</span>
      <span>Production Platform</span>
    </div>
    <ul>
      <li><strong>Official Meta Cloud API Architecture:</strong> Engineered multi-tenant CRM gateway integrating Meta Graph Cloud API (WABA ID: 106690...), handling bi-directional messaging, template dispatch, and HMAC-verified webhooks.</li>
      <li><strong>24-Hour Autonomous Follow-Up Radar:</strong> Built real-time engagement engine with dynamic cadences (24h/36h/48h/72h), tracking lead conversation states and triggering automated follow-ups via Supabase (PostgreSQL).</li>
      <li><strong>Failover LLM Pipeline &amp; Phone Routing:</strong> Integrated multi-key Gemini AI pool for automated intent parsing and lead qualification with 99.9% uptime, multi-coordinator SMS/WhatsApp dispatch, and live control dashboard.</li>
    </ul>
  </div>

  <div class="item">
    <div class="item-head">
      <span>SOLUM Minerals &amp; Commercial Web Suite</span>
      <span>2025 &ndash; Present</span>
    </div>
    <div class="item-subhead">
      <span>Full-Stack Web Architect &bull; Next.js 15, TypeScript, Tailwind CSS</span>
      <span>Commercial Platforms</span>
    </div>
    <ul>
      <li><strong>SOLUM Minerals Geology Portal:</strong> Architected responsive commercial web platform using Next.js 15 App Router, achieving a 99+ Lighthouse performance rating with interactive product showcases and zero layout shift (CLS &lt; 0.02).</li>
      <li><strong>Branders Digital Experience Platform:</strong> Engineered agency web platform with modern micro-interactions, responsive navigation, and physics-hardened layouts designed for high-conversion client acquisition.</li>
    </ul>
  </div>

  <div class="item">
    <div class="item-head">
      <span>Autonomous Media Generation Cloud Fleet (yt-auto)</span>
      <span>2025 &ndash; Present</span>
    </div>
    <div class="item-subhead">
      <span>Lead Automation Architect &bull; Python, FFmpeg, GitHub Actions CI/CD</span>
      <span><a href="https://github.com/gurination1/yt-auto">Open Source</a></span>
    </div>
    <ul>
      <li><strong>100% Headless Cloud Fleet Execution:</strong> Engineered resilient media generation pipeline running autonomously on GitHub Actions across 15 daily slots with automated matrix workers and zero local server dependencies.</li>
      <li><strong>Dual-Gate Multimodal Quality Control:</strong> Integrated FFmpeg black-frame detection and Gemini Multimodal Judge AI enforcing strict &ge;85/100 publication standards, dynamic audio ducking, and millisecond subtitle rendering.</li>
    </ul>
  </div>

  <h2>Work Experience</h2>

  <div class="item">
    <div class="item-head">
      <span>Gurdharam Software Consultancy &bull; Systems &amp; Web Engineer</span>
      <span>2025 &ndash; Present</span>
    </div>
    <div class="item-subhead">
      <span>Independent Software Consultancy &bull; Remote</span>
      <span>Punjab, India</span>
    </div>
    <ul>
      <li><strong>Telephonic Voice AI Agent:</strong> Built real-time telephony agent over Exotel WebSockets, SIP, and VoIP, achieving &lt;700ms turn latency across Sarvam AI Indic LLMs, Groq LPU, and Silero VAD barge-in for natural spoken dialogue.</li>
      <li><strong>High-Throughput Webhook Processing:</strong> Architected distributed queue worker system using Redis and BullMQ, reliably processing 25,000+ daily webhook events with automated retry logic and sub-5-minute SLA.</li>
    </ul>
  </div>

  <h2>Education &amp; Credentials</h2>

  <div class="item">
    <div class="item-head">
      <span>Baba Farid Group of Institutions (BFGI) &mdash; B.Sc. in Computer Science</span>
      <span>Expected May 2027</span>
    </div>
    <div class="item-subhead">
      <span>Core: Data Structures &amp; Algorithms, Database Systems, Computer Networks, Operating Systems</span>
      <span>Punjab, India</span>
    </div>
  </div>

  <div class="skill-group" style="margin-top: 3px;">
    <strong>Credentials &amp; Verification:</strong> Meta Verified Business Entity &bull; Official WhatsApp Business Platform Developer &bull; Sarvam AI Startup Developer Partner &bull; Govt. MSME Registered Enterprise (UDYAM-PB-03-0079744).
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
**Full-Stack Software Engineer • Web Systems & Cloud Automation**  
Punjab, India • +91 90411 72159 • [gurination1@gmail.com](mailto:gurination1@gmail.com) • [github.com/gurination1](https://github.com/gurination1) • [linkedin.com/in/gurdharam](https://linkedin.com/in/gurdharam) • [gurdharam.com](https://gurdharam.com)

---

## Professional Summary
Full-Stack Software Engineer with production experience shipping modern Next.js 15, TypeScript, and Node.js web applications and autonomous cloud automation fleets. Architect of commercial web portals with 99+ Lighthouse scores, enterprise WhatsApp CRM platforms over official Meta Cloud APIs, and real-time distributed pipelines processing 25,000+ daily events. Available immediately for remote Software Engineering internships and full-time roles worldwide.

---

## Technical Skills
- **Frontend & UI Systems:** React, Next.js 15 (App Router, Server Components), TypeScript, JavaScript (ES6+), Tailwind CSS, Three.js, WebGL2, HTML5/CSS3, Core Web Vitals (LCP, CLS < 0.02), Lenis Smooth Scroll.
- **Backend & Distributed Architecture:** Node.js, Express, Python (FastAPI, Asyncio), PostgreSQL, Supabase, Redis & BullMQ, WebSockets, REST APIs, Webhook Ingestion, Docker, Linux / Bash.
- **Cloud, DevOps & AI Integration:** GitHub Actions CI/CD (24/7 Cloud Fleets), Official Meta WhatsApp Cloud API (WABA), Gemini API / LLM Orchestration, Voice AI (SIP, WebSockets, Silero VAD), AWS (S3, Lambda), Playwright E2E.

---

## Key Engineering Projects

### Enterprise WhatsApp AI & Lead Management CRM
*Lead Architect • Meta Cloud API, Node.js, Express, Supabase (PostgreSQL) | 2025 – Present*
- **Official Meta Cloud API Architecture:** Engineered multi-tenant CRM gateway integrating Meta Graph Cloud API (WABA ID: 106690...), handling bi-directional messaging, template dispatch, and HMAC-verified webhooks.
- **24-Hour Autonomous Follow-Up Radar:** Built real-time engagement engine with dynamic cadences (24h/36h/48h/72h), tracking lead conversation states and triggering automated follow-ups via Supabase (PostgreSQL).
- **Failover LLM Pipeline & Phone Routing:** Integrated multi-key Gemini AI pool for automated intent parsing and lead qualification with 99.9% uptime, multi-coordinator SMS/WhatsApp dispatch, and live control dashboard.

### SOLUM Minerals & Commercial Web Suite
*Full-Stack Web Architect • Next.js 15, TypeScript, Tailwind CSS | 2025 – Present*
- **SOLUM Minerals Geology Portal:** Architected responsive commercial web platform using Next.js 15 App Router, achieving a 99+ Lighthouse performance rating with interactive product showcases and zero layout shift (CLS < 0.02).
- **Branders Digital Experience Platform:** Engineered agency web platform with modern micro-interactions, responsive navigation, and physics-hardened layouts designed for high-conversion client acquisition.

### Autonomous Media Generation Cloud Fleet (yt-auto)
*Lead Automation Architect • Python, FFmpeg, GitHub Actions CI/CD | 2025 – Present*
- **100% Headless Cloud Fleet Execution:** Engineered resilient media generation pipeline running autonomously on GitHub Actions across 15 daily slots with automated matrix workers and zero local server dependencies.
- **Dual-Gate Multimodal Quality Control:** Integrated FFmpeg black-frame detection and Gemini Multimodal Judge AI enforcing strict ≥85/100 publication standards, dynamic audio ducking, and millisecond subtitle rendering.

---

## Work Experience

### Gurdharam Software Consultancy • Systems & Web Engineer
*Independent Software Consultancy • Remote | Punjab, India | 2025 – Present*
- **Telephonic Voice AI Agent:** Built real-time telephony agent over Exotel WebSockets, SIP, and VoIP, achieving <700ms turn latency across Sarvam AI Indic LLMs, Groq LPU, and Silero VAD barge-in for natural spoken dialogue.
- **High-Throughput Webhook Processing:** Architected distributed queue worker system using Redis and BullMQ, reliably processing 25,000+ daily webhook events with automated retry logic and sub-5-minute SLA.

---

## Education & Credentials
- **Baba Farid Group of Institutions (BFGI)** — B.Sc. in Computer Science *(Expected May 2027)*
  - Core: Data Structures & Algorithms, Database Systems, Computer Networks, Operating Systems
- **Credentials & Verification:** Meta Verified Business Entity • Official WhatsApp Business Platform Developer • Sarvam AI Startup Developer Partner • Govt. MSME Registered Enterprise (UDYAM-PB-03-0079744).
"""

with open(md_path, "w") as f:
    f.write(md_content)

print("[+] Wrote Markdown companion resume.")
