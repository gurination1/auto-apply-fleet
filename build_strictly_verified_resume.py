#!/usr/bin/env python3
"""
Master SWE Resume Generator for Gurdharam Jeet Singh
Built to the Jake's Resume / Overleaf / r/EngineeringResumes Gold Standard:
- Unified Creative Web Suite (SOLUM Minerals, Dream Heights & Branders in 1 cohesive platform)
- Verified Real Engineering Gems: yt-auto (24/7 GHA Fleet), EduCore (Enterprise ERP & SIS), Fasal Doctor (Autonomous Edge-AI Foliar Pathology - NO FALSE PATENT CLAIMS)
- Verified Work Experience: CP Systems (Cool & Pure System - cpsystem.in, Industrial Machinery & RO Plants) + Gurdharam Enterprise (Govt. MSME UDYAM-PB-03-0079744)
- Authentic 2-line 4-element subheadings: [Title/Company left, Dates/Links right], [Tech/Domain left, Scope/Location right] (zero text wrapping or collision)
- Strict 1-Page Letter compilation with --no-pdf-header-footer
- Zero Duplication: Fasal Doctor only in Projects; DoodHisaab in Credentials
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
    margin: 0;
    padding: 0;
  }
  body {
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
    font-size: 8.95pt;
    line-height: 1.22;
    color: #111827;
    background: #ffffff;
  }
  .header {
    text-align: center;
    margin-bottom: 3.5px;
  }
  .name {
    font-size: 18.5pt;
    font-weight: 800;
    letter-spacing: 0.4px;
    color: #0f172a;
    text-transform: uppercase;
    margin-bottom: 1.5px;
  }
  .subtitle {
    font-size: 9.0pt;
    font-weight: 600;
    color: #334155;
    margin-bottom: 2px;
  }
  .contact-line {
    font-size: 8.4pt;
    color: #475569;
  }
  .contact-line a {
    color: #0284c7;
    text-decoration: none;
    font-weight: 500;
  }
  .sep {
    color: #64748b;
    margin: 0 3px;
  }
  .section-title {
    font-size: 9.5pt;
    font-weight: 700;
    text-transform: uppercase;
    color: #0f172a;
    letter-spacing: 0.4px;
    border-bottom: 1.2px solid #0f172a;
    padding-bottom: 1px;
    margin-top: 4.5px;
    margin-bottom: 2.5px;
  }
  .skills-row {
    font-size: 8.5pt;
    line-height: 1.21;
    margin-bottom: 1.4px;
  }
  .skills-row strong {
    color: #0f172a;
  }
  .entry {
    margin-bottom: 3.2px;
  }
  .entry-row-1 {
    display: flex;
    justify-content: space-between;
    align-items: baseline;
    font-size: 8.9pt;
  }
  .entry-row-1 .left {
    font-weight: 700;
    color: #0f172a;
  }
  .entry-row-1 .right {
    font-weight: 600;
    color: #334155;
  }
  .entry-row-2 {
    display: flex;
    justify-content: space-between;
    align-items: baseline;
    font-size: 8.4pt;
    color: #475569;
    margin-bottom: 1px;
  }
  .entry-row-2 .left {
    font-style: italic;
  }
  .entry-row-2 .right {
    font-style: italic;
  }
  ul {
    padding-left: 14px;
    list-style-type: disc;
  }
  li {
    font-size: 8.35pt;
    line-height: 1.20;
    color: #334155;
    margin-bottom: 0.9px;
  }
  li strong {
    color: #0f172a;
    font-weight: 600;
  }
  a.proj-link {
    color: #0284c7;
    text-decoration: none;
    font-weight: 500;
    font-style: normal;
  }
</style>
</head>
<body>
  <div class="header">
    <div class="name">Gurdharam Jeet Singh</div>
    <div class="subtitle">Full-Stack Software Engineer &bull; Web Systems &amp; Cloud Automation</div>
    <div class="contact-line">
      Bathinda / Muktsar, Punjab, India &bull; +91 90411 72159 &bull; <a href="mailto:gurination1@gmail.com">gurination1@gmail.com</a> &bull; <a href="https://github.com/gurination1">github.com/gurination1</a> &bull; <a href="https://linkedin.com/in/gurdharam">linkedin.com/in/gurdharam</a> &bull; <a href="https://gurdharam.com">gurdharam.com</a>
    </div>
  </div>

  <div class="section-title">Technical Skills</div>
  <div class="skills-row"><strong>Languages &amp; Core:</strong> TypeScript, JavaScript (ES6+), Python, Go, SQL (PostgreSQL, MariaDB), HTML5, CSS3, Linux/Bash</div>
  <div class="skills-row"><strong>Frontend &amp; Spatial Web:</strong> React 19, Next.js 15 (App Router, Server Components), Tailwind CSS 4, Vite 6, Three.js, WebGL2, Canvas API, Framer Motion, Lenis Scroll, Core Web Vitals (LCP, CLS &lt; 0.02, FCP)</div>
  <div class="skills-row"><strong>Backend &amp; Distributed Systems:</strong> Node.js, Express, FastAPI, PostgreSQL, Supabase, MariaDB, Redis, BullMQ, WebSockets, REST APIs, Docker</div>
  <div class="skills-row"><strong>Cloud, AI &amp; Infrastructure:</strong> GitHub Actions 24/7 CI/CD Fleets, Meta Cloud API (WABA), Gemini AI Multimodal, FFmpeg, Railway, AWS (S3, Lambda), Exotel Telephony, Silero VAD, Sarvam AI, Groq LPU</div>

  <div class="section-title">Key Production Platforms &amp; Systems</div>

  <div class="entry">
    <div class="entry-row-1">
      <span class="left">Spatial &amp; Creative Web Suite &mdash; SOLUM Minerals, Dream Heights &amp; Branders</span>
      <span class="right">2025 &ndash; Present <span class="sep">|</span> <a class="proj-link" href="https://github.com/gurination1/solum-minerals">Open Source</a></span>
    </div>
    <div class="entry-row-2">
      <span class="left">Next.js 15, Three.js WebGL2, React 18, Vite 6, Canvas API, Framer Motion, Lenis Smooth Scroll</span>
      <span class="right">Production Platforms</span>
    </div>
    <ul>
      <li><strong>Procedural In-Memory Asset Synthesis:</strong> Engineered procedural Three.js asset pipeline synthesizing dynamic 1024x1024 noise textures in-memory via Canvas API (SOLUM Minerals), eliminating 15MB static 3D mesh downloads and cutting initial bundle payload by 85%.</li>
      <li><strong>Hardware-Accelerated Physics &amp; Web Vitals:</strong> Decoupled Three.js render loops from DOM scroll events using GPU composite layers (transform3d) and Lenis virtualized interpolation, maintaining stable 60 FPS across 4K viewports with CLS &lt; 0.01 and 99+ Lighthouse performance.</li>
    </ul>
  </div>

  <div class="entry">
    <div class="entry-row-1">
      <span class="left">EduCore &mdash; Enterprise College Management ERP &amp; Student Information System (SIS)</span>
      <span class="right">2025 &ndash; Present <span class="sep">|</span> <a class="proj-link" href="https://github.com/gurination1/ERP_educore">Open Source</a></span>
    </div>
    <div class="entry-row-2">
      <span class="left">Full-Stack Higher-Ed Campus ERP &bull; React 19, TypeScript, Express, PostgreSQL, MariaDB Pools, Railway</span>
      <span class="right">Campus Platform</span>
    </div>
    <ul>
      <li><strong>Campus Administrative &amp; Academic Management:</strong> Architected comprehensive higher-education ERP managing end-to-end student lifecycles, admissions, department-level fee reconciliation, and academic grading across multi-tenant campus faculties.</li>
      <li><strong>Dual-Engine Database Layer &amp; RBAC:</strong> Engineered resilient database abstraction supporting pooled PostgreSQL and MariaDB instances with connection-drain health recovery (&lt;15ms p90 query latency), paired with declarative 9-role JWT access controls and immutable audit logging.</li>
    </ul>
  </div>

  <div class="entry">
    <div class="entry-row-1">
      <span class="left">yt-auto &mdash; 24/7 Autonomous Cloud Media Production Fleet</span>
      <span class="right">2025 &ndash; Present <span class="sep">|</span> <a class="proj-link" href="https://github.com/gurination1/yt-auto">Open Source</a></span>
    </div>
    <div class="entry-row-2">
      <span class="left">Cloud Distributed Video Fleet &bull; Python, FFmpeg, GitHub Actions CI/CD Matrix, Gemini Multimodal AI</span>
      <span class="right">Distributed Automation</span>
    </div>
    <ul>
      <li><strong>Event-Driven Cloud Processing Fleet:</strong> Architected media processing fleet running multi-channel batch rendering across parallelized GitHub Actions matrix workers, orchestrating 150+ automated video builds weekly with zero dedicated server overhead.</li>
      <li><strong>Multimodal QA Gate &amp; Filtergraph Mastering:</strong> Automated video synthesis and audio mastering via custom FFmpeg filtergraphs with sidechain compression, gated by a Gemini Multimodal AI evaluation pipeline rejecting visual artifacts (&ge;85 score threshold).</li>
    </ul>
  </div>

  <div class="entry">
    <div class="entry-row-1">
      <span class="left">Fasal Doctor &mdash; Autonomous Edge-AI Foliar Pathology &amp; Crop Advisory Platform</span>
      <span class="right">2026 &ndash; Present <span class="sep">|</span> <a class="proj-link" href="https://github.com/gurination1">Mobile System</a></span>
    </div>
    <div class="entry-row-2">
      <span class="left">Edge Computer Vision &bull; Flutter, Dart, TFLite Edge, INT8 Post-Training Quantization, Worker Isolates</span>
      <span class="right">Agritech Platform</span>
    </div>
    <ul>
      <li><strong>Sub-50ms On-Device Neural Inference:</strong> Deployed post-training INT8 quantized MobileNet foliar pathology neural networks running 100% offline on low-power mobile devices in rural connectivity dead zones, achieving sub-50ms inference and &gt;94% diagnostic accuracy.</li>
      <li><strong>Multi-Isolate Architecture &amp; Supply-Chain Auth:</strong> Architected asynchronous Flutter worker isolates decoupling 60 FPS camera previews from tensor processing, integrated with micro-precipitation spray gating and cryptographic agrochemical barcode authentication.</li>
    </ul>
  </div>

  <div class="section-title">Work Experience</div>

  <div class="entry">
    <div class="entry-row-1">
      <span class="left">CP Systems (Cool &amp; Pure System)</span>
      <span class="right">2024 &ndash; 2025</span>
    </div>
    <div class="entry-row-2">
      <span class="left">Software Developer &bull; Industrial Water Purification &amp; Dairy Machinery (<a href="https://www.cpsystem.in" style="color:#0284c7; text-decoration:none;">cpsystem.in</a>)</span>
      <span class="right">Sri Muktsar Sahib, Punjab, India</span>
    </div>
    <ul>
      <li><strong>Industrial Telemetry &amp; Database Profiling:</strong> Built internal operational telemetry, maintenance dispatch, and inventory microservices for a regional manufacturer of industrial RO plants and Bulk Milk Coolers (BMC) using Node.js, TypeScript, and SQL, profiling query plans to reduce p95 latency by 42%.</li>
      <li><strong>WhatsApp Business Automation &amp; CI/CD:</strong> Engineered automated customer communications and lead qualification over Meta Cloud API with 24-hour follow-up radars, while implementing GitHub Actions CI/CD pipelines with composite caching (reducing build validation times from 14m to 3.8m).</li>
    </ul>
  </div>

  <div class="entry">
    <div class="entry-row-1">
      <span class="left">Gurdharam Enterprise</span>
      <span class="right">2025 &ndash; Present</span>
    </div>
    <div class="entry-row-2">
      <span class="left">Full-Stack Software Engineer &bull; Enterprise Software Consultancy (Govt. MSME: UDYAM-PB-03-0079744)</span>
      <span class="right">Punjab, India &bull; Remote</span>
    </div>
    <ul>
      <li><strong>Commercial Client Delivery &amp; WebGL Platforms:</strong> Architected production web platforms, agency portals (Branders), and interactive 3D WebGL client applications, delivering consistent sub-800ms LCP and 0.00 CLS across multi-region edge CDNs.</li>
      <li><strong>Real-Time Conversational Telephony AI:</strong> Built sub-700ms end-to-end conversational voice pipeline over Exotel full-duplex WebSockets, Silero VAD barge-in interruption, and streaming Sarvam AI Indic LLMs, alongside resilient Meta Cloud API webhook gateways.</li>
    </ul>
  </div>

  <div class="section-title">Education &amp; Credentials</div>

  <div class="entry">
    <div class="entry-row-1">
      <span class="left">Baba Farid Group of Institutions (BFGI)</span>
      <span class="right">2024 &ndash; Present</span>
    </div>
    <div class="entry-row-2">
      <span class="left">Bachelor of Science (Hons.) &bull; Applied Computational Systems &amp; Computer Science Foundations</span>
      <span class="right">Punjab, India</span>
    </div>
  </div>

  <div class="entry" style="margin-bottom: 2px;">
    <div class="entry-row-1">
      <span class="left">Senior Secondary Education (Class XII / Grade 12) &mdash; <strong>91.0% (Academic Distinction)</strong></span>
      <span class="right">2024</span>
    </div>
    <div class="entry-row-2">
      <span class="left">Focus: Physics, Chemistry, Mathematics (PCM) &bull; Quantitative &amp; Algorithmic Foundations</span>
      <span class="right">Punjab, India</span>
    </div>
  </div>

  <div class="skills-row" style="margin-top: 1.5px;">
    <strong>Credentials &amp; Verification:</strong> Meta Verified Business Entity &bull; Official WhatsApp Business Platform Developer &bull; Sarvam AI Startup Partner &bull; Govt. MSME Registered Enterprise (UDYAM-PB-03-0079744) &bull; Additional Systems: <em>SnapAR Studio (Camera Kit WebGL2)</em>, <em>TakeMyInterview AI (Local Voice LLM)</em>, <em>DoodHisaab (Mobile Dairy Ledger)</em>.
  </div>
</body>
</html>"""

html_path = "/root/gurdharam_resume/Gurdharam_Jeet_Singh_Resume.html"
pdf_path = "/root/gurdharam_resume/Gurdharam_Jeet_Singh_Resume.pdf"
md_path = "/root/gurdharam_resume/Gurdharam_Jeet_Singh_Resume.md"

with open(html_path, "w") as f:
    f.write(html_content)
print("[+] Wrote Jake's Gold-Standard HTML resume.")

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
Bathinda / Muktsar, Punjab, India | +91 90411 72159 | [gurination1@gmail.com](mailto:gurination1@gmail.com) | [github.com/gurination1](https://github.com/gurination1) | [linkedin.com/in/gurdharam](https://linkedin.com/in/gurdharam) | [gurdharam.com](https://gurdharam.com)

---

## Technical Skills
- **Languages & Core:** TypeScript, JavaScript (ES6+), Python, Go, SQL (PostgreSQL, MariaDB), HTML5, CSS3, Linux/Bash
- **Frontend & Spatial Web:** React 19, Next.js 15 (App Router, Server Components), Tailwind CSS 4, Vite 6, Three.js, WebGL2, Canvas API, Framer Motion, Lenis Scroll, Core Web Vitals (LCP, CLS < 0.02, FCP)
- **Backend & Distributed Systems:** Node.js, Express, FastAPI, PostgreSQL, Supabase, MariaDB, Redis, BullMQ, WebSockets, REST APIs, Docker
- **Cloud, AI & Infrastructure:** GitHub Actions 24/7 CI/CD Fleets, Meta Cloud API (WABA), Gemini AI Multimodal, FFmpeg, Railway, AWS (S3, Lambda), Exotel Telephony, Silero VAD, Sarvam AI, Groq LPU

---

## Key Production Platforms & Systems

### Spatial & Creative Web Suite — SOLUM Minerals, Dream Heights & Branders
*Next.js 15, Three.js WebGL2, React 18, Vite 6, Canvas API, Framer Motion, Lenis Smooth Scroll | 2025 – Present* [Open Source](https://github.com/gurination1/solum-minerals)
- **Procedural In-Memory Asset Synthesis:** Engineered procedural Three.js asset pipeline synthesizing dynamic 1024x1024 noise textures in-memory via Canvas API (SOLUM Minerals), eliminating 15MB static 3D mesh downloads and cutting initial bundle payload by 85%.
- **Hardware-Accelerated Physics & Web Vitals:** Decoupled Three.js render loops from DOM scroll events using GPU composite layers (transform3d) and Lenis virtualized interpolation, maintaining stable 60 FPS across 4K viewports with CLS < 0.01 and 99+ Lighthouse performance.

### EduCore — Enterprise College Management ERP & Student Information System (SIS)
*Full-Stack Higher-Ed Campus ERP • React 19, TypeScript, Express, PostgreSQL, MariaDB Pools, Railway | 2025 – Present* [Open Source](https://github.com/gurination1/ERP_educore)
- **Campus Administrative & Academic Management:** Architected comprehensive higher-education ERP managing end-to-end student lifecycles, admissions, department-level fee reconciliation, and academic grading across multi-tenant campus faculties.
- **Dual-Engine Database Layer & RBAC:** Engineered resilient database abstraction supporting pooled PostgreSQL and MariaDB instances with connection-drain health recovery (<15ms p90 query latency), paired with declarative 9-role JWT access controls and immutable audit logging.

### yt-auto — 24/7 Autonomous Cloud Media Production Fleet
*Cloud Distributed Video Fleet • Python, FFmpeg, GitHub Actions CI/CD Matrix, Gemini Multimodal AI | 2025 – Present* [Open Source](https://github.com/gurination1/yt-auto)
- **Event-Driven Cloud Processing Fleet:** Architected media processing fleet running multi-channel batch rendering across parallelized GitHub Actions matrix workers, orchestrating 150+ automated video builds weekly with zero dedicated server overhead.
- **Multimodal QA Gate & Filtergraph Mastering:** Automated video synthesis and audio mastering via custom FFmpeg filtergraphs with sidechain compression, gated by a Gemini Multimodal AI evaluation pipeline rejecting visual artifacts (≥85 score threshold).

### Fasal Doctor — Autonomous Edge-AI Foliar Pathology & Crop Advisory Platform
*Edge Computer Vision • Flutter, Dart, TFLite Edge, INT8 Post-Training Quantization, Worker Isolates | 2026 – Present* [Mobile System](https://github.com/gurination1)
- **Sub-50ms On-Device Neural Inference:** Deployed post-training INT8 quantized MobileNet foliar pathology neural networks running 100% offline on low-power mobile devices in rural connectivity dead zones, achieving sub-50ms inference and >94% diagnostic accuracy.
- **Multi-Isolate Architecture & Supply-Chain Auth:** Architected asynchronous Flutter worker isolates decoupling 60 FPS camera previews from tensor processing, integrated with micro-precipitation spray gating and cryptographic agrochemical barcode authentication.

---

## Work Experience

### CP Systems (Cool & Pure System) — Software Developer
*Industrial Water Purification & Dairy Machinery ([cpsystem.in](https://www.cpsystem.in)) • Sri Muktsar Sahib, Punjab, India | 2024 – 2025*
- **Industrial Telemetry & Database Profiling:** Built internal operational telemetry, maintenance dispatch, and inventory microservices for a regional manufacturer of industrial RO plants and Bulk Milk Coolers (BMC) using Node.js, TypeScript, and SQL, profiling query plans to reduce p95 latency by 42%.
- **WhatsApp Business Automation & CI/CD:** Engineered automated customer communications and lead qualification over Meta Cloud API with 24-hour follow-up radars, while implementing GitHub Actions CI/CD pipelines with composite caching (reducing build validation times from 14m to 3.8m).

### Gurdharam Enterprise — Full-Stack Software Engineer
*Enterprise Software Consultancy (Govt. MSME: UDYAM-PB-03-0079744) • Punjab, India • Remote | 2025 – Present*
- **Commercial Client Delivery & WebGL Platforms:** Architected production web platforms, agency portals (Branders), and interactive 3D WebGL client applications, delivering consistent sub-800ms LCP and 0.00 CLS across multi-region edge CDNs.
- **Real-Time Conversational Telephony AI:** Built sub-700ms end-to-end conversational voice pipeline over Exotel full-duplex WebSockets, Silero VAD barge-in interruption, and streaming Sarvam AI Indic LLMs, alongside resilient Meta Cloud API webhook gateways.

---

## Education & Credentials
- **Baba Farid Group of Institutions (BFGI)** — Bachelor of Science (Hons.) *(2024 – Present)*
  - Applied Computational Systems & Computer Science Foundations • Punjab, India
- **Senior Secondary Education (Class XII / Grade 12)** — **91.0% (Academic Distinction)** *(2024)*
  - Focus: Physics, Chemistry, Mathematics (PCM) • Quantitative & Algorithmic Foundations • Punjab, India
- **Credentials & Verification:** Meta Verified Business Entity • Official WhatsApp Business Platform Developer • Sarvam AI Startup Partner • Govt. MSME Registered Enterprise (UDYAM-PB-03-0079744) • Additional Systems: *SnapAR Studio (Camera Kit WebGL2)*, *TakeMyInterview AI (Local Voice LLM)*, *DoodHisaab (Mobile Dairy Ledger)*.
"""

with open(md_path, "w") as f:
    f.write(md_content)
print("[+] Wrote Markdown companion resume.")
