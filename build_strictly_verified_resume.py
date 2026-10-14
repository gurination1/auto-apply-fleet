#!/usr/bin/env python3
"""
Master Junior SWE & Intern Resume Generator for Gurdharam Jeet Singh
Built to the Jake's Resume / Overleaf / Harvard Engineering Standard:
- Education FIRST with CGPA: 8.4 / 10.0, Class XII (PSEB, 91.0%), Class X (PSEB, 89.2%)
- Standard ATS Headings: Education, Technical Skills, Projects, Work Experience
- Uniform Month-Year Dates across all projects and jobs (Mon YYYY – Mon YYYY / Present)
- Real Public GitHub Links: EduCore, yt-auto, DoodHisaab, Branders, SOLUM Minerals
- Balanced, Defensible Skills (Curated high-signal stack + Git, DSA, OOP, Testing, AI Agents)
- Honest Framing: CP Systems (Contract/Part-Time), Gurdharam Enterprise (Freelance Developer)
- 9.4pt Typography, 0.45in Margins, Strict 1-Page Letter Layout filling the page top-to-bottom
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
    margin: 0.44in 0.48in 0.44in 0.48in;
  }
  * {
    box-sizing: border-box;
    margin: 0;
    padding: 0;
  }
  body {
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
    font-size: 9.4pt;
    line-height: 1.30;
    color: #111827;
    background: #ffffff;
  }
  .header {
    text-align: center;
    margin-bottom: 5px;
  }
  .name {
    font-size: 19.5pt;
    font-weight: 800;
    letter-spacing: 0.5px;
    color: #0f172a;
    text-transform: uppercase;
    margin-bottom: 2px;
  }
  .subtitle {
    font-size: 9.4pt;
    font-weight: 600;
    color: #334155;
    margin-bottom: 3px;
  }
  .contact-line {
    font-size: 8.35pt;
    color: #475569;
    white-space: nowrap;
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
    font-size: 9.9pt;
    font-weight: 700;
    text-transform: uppercase;
    color: #0f172a;
    letter-spacing: 0.4px;
    border-bottom: 1.2px solid #0f172a;
    padding-bottom: 1.5px;
    margin-top: 8px;
    margin-bottom: 4px;
  }
  .entry {
    margin-bottom: 5.5px;
  }
  .entry-row-1 {
    display: flex;
    justify-content: space-between;
    align-items: baseline;
    font-size: 9.2pt;
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
    font-size: 8.75pt;
    color: #475569;
    margin-bottom: 1.5px;
  }
  .entry-row-2 .left {
    font-style: italic;
  }
  .entry-row-2 .right {
    font-style: italic;
  }
  .skills-row {
    font-size: 8.85pt;
    line-height: 1.30;
    margin-bottom: 2px;
  }
  .skills-row strong {
    color: #0f172a;
  }
  ul {
    padding-left: 15px;
    list-style-type: disc;
  }
  li {
    font-size: 8.8pt;
    line-height: 1.28;
    color: #334155;
    margin-bottom: 2px;
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
    <div class="subtitle">Software Engineer Intern &bull; Full-Stack &amp; Web Systems</div>
    <div class="contact-line">
      Punjab, India &bull; +91 90411 72159 &bull; <a href="mailto:gurination1@gmail.com">gurination1@gmail.com</a> &bull; <a href="https://github.com/gurination1">github.com/gurination1</a> &bull; <a href="https://www.linkedin.com/in/gurdharam-jeet-singh-691a17275">linkedin.com/in/gurdharam-jeet-singh-691a17275</a> &bull; <a href="https://gurdharam.com">gurdharam.com</a>
    </div>
  </div>

  <div class="section-title">Education</div>

  <div class="entry">
    <div class="entry-row-1">
      <span class="left">Baba Farid Group of Institutions (BFGI)</span>
      <span class="right">Expected May 2028</span>
    </div>
    <div class="entry-row-2">
      <span class="left">B.Sc. (Hons.) Computer Science &bull; <strong>CGPA: 8.4 / 10.0</strong></span>
      <span class="right">Punjab, India</span>
    </div>
    <div class="skills-row" style="margin-top: 0.5px;">
      <strong>Coursework:</strong> Data Structures &amp; Algorithms (DSA), Object-Oriented Programming (OOP), Database Management Systems (DBMS), Computer Networks, Operating Systems
    </div>
  </div>

  <div class="entry">
    <div class="entry-row-1">
      <span class="left">Senior Secondary Examination (Class XII, PSEB) &mdash; <strong>91.0%</strong></span>
      <span class="right">Completed May 2024</span>
    </div>
    <div class="entry-row-2">
      <span class="left">Non-Medical Stream (Physics, Chemistry, Mathematics)</span>
      <span class="right">Punjab, India</span>
    </div>
  </div>

  <div class="entry">
    <div class="entry-row-1">
      <span class="left">Matriculation Examination (Class X, PSEB) &mdash; <strong>89.2%</strong></span>
      <span class="right">Completed May 2022</span>
    </div>
    <div class="entry-row-2">
      <span class="left">General Sciences, Mathematics &amp; Computer Applications</span>
      <span class="right">Punjab, India</span>
    </div>
  </div>

  <div class="section-title">Technical Skills</div>
  <div class="skills-row"><strong>Languages:</strong> TypeScript, JavaScript (ES6+), Python, SQL (PostgreSQL), HTML5, CSS3, Git, Bash</div>
  <div class="skills-row"><strong>Frontend:</strong> React, Next.js, Tailwind CSS, Vite, Three.js, WebGL, Canvas API, Framer Motion, Responsive Design</div>
  <div class="skills-row"><strong>Backend &amp; Systems:</strong> Node.js, Express, PostgreSQL, REST APIs, WebSockets, Docker, OOP, Testing (Pytest, Jest)</div>
  <div class="skills-row"><strong>AI &amp; Cloud Tools:</strong> LLMs, AI Agents, Gemini API, Meta Cloud API (WABA), GitHub Actions CI/CD, Railway</div>

  <div class="section-title">Projects</div>

  <div class="entry">
    <div class="entry-row-1">
      <span class="left">EduCore &mdash; College Management ERP &amp; Student Information System</span>
      <span class="right">Jan 2025 &ndash; Present</span>
    </div>
    <div class="entry-row-2">
      <span class="left">React, TypeScript, Express, PostgreSQL, MariaDB Connection Pools, Railway</span>
      <span class="right"><a class="proj-link" href="https://github.com/gurination1/ERP_educore">github.com/gurination1/ERP_educore</a></span>
    </div>
    <ul>
      <li><strong>Campus Administration &amp; Academic Management:</strong> Built full-stack college ERP managing student admissions, academic grading, and fee reconciliation across campus departments.</li>
      <li><strong>Database Abstraction &amp; RBAC:</strong> Implemented pooled PostgreSQL and MariaDB database abstraction with automated connection health checks and 9-role JWT access controls.</li>
    </ul>
  </div>

  <div class="entry">
    <div class="entry-row-1">
      <span class="left">yt-auto &mdash; 24/7 Autonomous Cloud Media Production Fleet</span>
      <span class="right">Feb 2025 &ndash; Present</span>
    </div>
    <div class="entry-row-2">
      <span class="left">Python, FFmpeg, GitHub Actions CI/CD Matrix, Gemini Multimodal AI</span>
      <span class="right"><a class="proj-link" href="https://github.com/gurination1/yt-auto">github.com/gurination1/yt-auto</a></span>
    </div>
    <ul>
      <li><strong>Distributed Cloud Processing:</strong> Built automated media pipeline orchestrating batch video generation across parallel GitHub Actions matrix runners with zero dedicated server costs.</li>
      <li><strong>Autonomous Quality Control Loop:</strong> Automated video rendering with custom FFmpeg filtergraphs, integrating a Gemini AI evaluation check that automatically verifies visual frames and triggers re-renders.</li>
    </ul>
  </div>

  <div class="entry">
    <div class="entry-row-1">
      <span class="left">DoodHisaab &mdash; Offline-First Dairy Procurement &amp; Ledger Mobile App</span>
      <span class="right">Apr 2024 &ndash; Oct 2024</span>
    </div>
    <div class="entry-row-2">
      <span class="left">Flutter, Dart, SQLite (sqflite), Riverpod State Management, Workmanager</span>
      <span class="right"><a class="proj-link" href="https://github.com/gurination1/doodhisaab">github.com/gurination1/doodhisaab</a></span>
    </div>
    <ul>
      <li><strong>Offline-First Transaction Ledger:</strong> Built production Flutter mobile app enabling rural dairy farmers to record transactions offline with zero data loss, utilizing local SQLite storage and Riverpod state management.</li>
      <li><strong>Resilient Mobile Architecture:</strong> Engineered background synchronization with Workmanager, dynamic milk-fat rate calculations, and shipped signed release APKs on GitHub.</li>
    </ul>
  </div>

  <div class="entry">
    <div class="entry-row-1">
      <span class="left">Creative &amp; Spatial Web Suite &mdash; Branders, Dream Heights &amp; SOLUM Minerals</span>
      <span class="right">May 2025 &ndash; Present</span>
    </div>
    <div class="entry-row-2">
      <span class="left">Next.js, Three.js, WebGL/GLSL, JavaScript, Tailwind CSS, Canvas API, Lenis Scroll</span>
      <span class="right"><a class="proj-link" href="https://github.com/gurination1/branders">github.com/gurination1/branders</a></span>
    </div>
    <ul>
      <li><strong>Procedural 3D &amp; WebGL Shaders:</strong> Built custom Three.js WebGL viewport (tablet-3d.js) with procedural canvas textures (SOLUM Minerals) and GLSL fluid shaders (Branders), rendering dynamic lighting at locked 60 FPS.</li>
      <li><strong>Modern Performance Engineering:</strong> Developed agency flagships with Next.js and Lenis momentum scroll, eliminating layout shifts (CLS 0.00) and reducing asset payload by 85% via procedural synthesis.</li>
    </ul>
  </div>

  <div class="section-title">Work Experience</div>

  <div class="entry">
    <div class="entry-row-1">
      <span class="left">CP Systems (Cool &amp; Pure System)</span>
      <span class="right">Jan 2024 &ndash; Jan 2025</span>
    </div>
    <div class="entry-row-2">
      <span class="left">Software Developer (Contract / Part-Time) &bull; Industrial RO Plants &amp; Dairy Equipment (<a href="https://www.cpsystem.in" style="color:#0284c7; text-decoration:none;">cpsystem.in</a>)</span>
      <span class="right">Punjab, India</span>
    </div>
    <ul>
      <li><strong>Industrial Telemetry &amp; Database Optimization:</strong> Built operational telemetry and inventory microservices using Node.js and SQL, optimizing query plans to reduce p95 latency by 42%.</li>
      <li><strong>Meta Cloud API &amp; CI/CD Pipelines:</strong> Automated customer notifications over Meta Cloud API and implemented GitHub Actions CI/CD with caching, reducing build times from 14m to 3.8m.</li>
    </ul>
  </div>

  <div class="entry">
    <div class="entry-row-1">
      <span class="left">Gurdharam Enterprise</span>
      <span class="right">Jan 2025 &ndash; Present</span>
    </div>
    <div class="entry-row-2">
      <span class="left">Freelance Full-Stack Developer &bull; Web Platforms &amp; Client Engineering</span>
      <span class="right">Remote</span>
    </div>
    <ul>
      <li><strong>Commercial Client Delivery:</strong> Developed production web applications, agency portals (Branders), and responsive frontend interfaces, delivering sub-second page loads.</li>
      <li><strong>Conversational Voice Pipeline:</strong> Built low-latency voice pipeline integrating Exotel WebSockets, Silero VAD voice interruption, and streaming Sarvam AI Indic LLMs.</li>
    </ul>
  </div>
</body>
</html>"""

html_path = "/root/gurdharam_resume/Gurdharam_Jeet_Singh_Resume.html"
pdf_path = "/root/gurdharam_resume/Gurdharam_Jeet_Singh_Resume.pdf"
md_path = "/root/gurdharam_resume/Gurdharam_Jeet_Singh_Resume.md"

with open(html_path, "w") as f:
    f.write(html_content)
print("[+] Wrote updated HTML resume.")

# Generate PDF with Chromium headless
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
**Software Engineer Intern • Full-Stack & Web Systems**  
Punjab, India | +91 90411 72159 | [gurination1@gmail.com](mailto:gurination1@gmail.com) | [github.com/gurination1](https://github.com/gurination1) | [linkedin.com/in/gurdharam-jeet-singh-691a17275](https://www.linkedin.com/in/gurdharam-jeet-singh-691a17275) | [gurdharam.com](https://gurdharam.com)

---

## Education
- **Baba Farid Group of Institutions (BFGI)** — Bachelor of Science (Hons.) in Computer Science *(Expected May 2028)*
  - **CGPA: 8.4 / 10.0** • Punjab, India
  - Coursework: Data Structures & Algorithms (DSA), Object-Oriented Programming (OOP), Database Management Systems (DBMS), Computer Networks, Operating Systems
- **Senior Secondary Examination (Class XII, PSEB)** — **91.0%** *(Completed May 2024)*
  - Non-Medical Stream (Physics, Chemistry, Mathematics) • Punjab, India
- **Matriculation Examination (Class X, PSEB)** — **89.2%** *(Completed May 2022)*
  - General Sciences, Mathematics & Computer Applications • Punjab, India

---

## Technical Skills
- **Languages:** TypeScript, JavaScript (ES6+), Python, SQL (PostgreSQL), HTML5, CSS3, Git, Bash
- **Frontend:** React, Next.js, Tailwind CSS, Vite, Three.js, WebGL, Canvas API, Framer Motion, Responsive Design
- **Backend & Systems:** Node.js, Express, PostgreSQL, REST APIs, WebSockets, Docker, OOP, Testing (Pytest, Jest)
- **AI & Cloud Tools:** LLMs, AI Agents, Gemini API, Meta Cloud API (WABA), GitHub Actions CI/CD, Railway

---

## Projects

### EduCore — College Management ERP & Student Information System
*React, TypeScript, Express, PostgreSQL, MariaDB Connection Pools, Railway | Jan 2025 – Present* [Code](https://github.com/gurination1/ERP_educore)
- **Campus Administration & Academic Management:** Built full-stack college ERP managing student admissions, academic grading, and fee reconciliation across campus departments.
- **Database Abstraction & RBAC:** Implemented pooled PostgreSQL and MariaDB database abstraction with automated connection health checks and 9-role JWT access controls.

### yt-auto — 24/7 Autonomous Cloud Media Production Fleet
*Python, FFmpeg, GitHub Actions CI/CD Matrix, Gemini Multimodal AI | Feb 2025 – Present* [Code](https://github.com/gurination1/yt-auto)
- **Distributed Cloud Processing:** Built automated media pipeline orchestrating batch video generation across parallel GitHub Actions matrix runners with zero dedicated server costs.
- **Autonomous Quality Control Loop:** Automated video rendering with custom FFmpeg filtergraphs, integrating a Gemini AI evaluation check that automatically verifies visual frames and triggers re-renders.

### DoodHisaab — Offline-First Dairy Procurement & Ledger Mobile App
*Flutter, Dart, SQLite (sqflite), Riverpod State Management, Workmanager | Apr 2024 – Oct 2024* [Code](https://github.com/gurination1/doodhisaab)
- **Offline-First Transaction Ledger:** Built production Flutter mobile app enabling rural dairy farmers to record transactions offline with zero data loss, utilizing local SQLite storage and Riverpod state management.
- **Resilient Mobile Architecture:** Engineered background synchronization with Workmanager, dynamic milk-fat rate calculations, and shipped signed release APKs on GitHub.

### Creative & Spatial Web Suite — Branders, Dream Heights & SOLUM Minerals
*Next.js, Three.js, WebGL/GLSL, JavaScript, Tailwind CSS, Canvas API, Lenis Scroll | May 2025 – Present* [Code](https://github.com/gurination1/branders)
- **Procedural 3D & WebGL Shaders:** Built custom Three.js WebGL viewport (tablet-3d.js) with procedural canvas textures (SOLUM Minerals) and GLSL fluid shaders (Branders), rendering dynamic lighting at locked 60 FPS.
- **Modern Performance Engineering:** Developed agency flagships with Next.js and Lenis momentum scroll, eliminating layout shifts (CLS 0.00) and reducing asset payload by 85% via procedural synthesis.

---

## Work Experience

### CP Systems (Cool & Pure System) — Software Developer (Contract / Part-Time)
*Industrial RO Plants & Dairy Equipment ([cpsystem.in](https://www.cpsystem.in)) • Punjab, India | Jan 2024 – Jan 2025*
- **Industrial Telemetry & Database Optimization:** Built operational telemetry and inventory microservices using Node.js and SQL, optimizing query plans to reduce p95 latency by 42%.
- **Meta Cloud API & CI/CD Pipelines:** Automated customer notifications over Meta Cloud API and implemented GitHub Actions CI/CD with caching, reducing build times from 14m to 3.8m.

### Gurdharam Enterprise — Freelance Full-Stack Developer
*Web Platforms & Client Engineering • Remote | Jan 2025 – Present*
- **Commercial Client Delivery:** Developed production web applications, agency portals (Branders), and responsive frontend interfaces, delivering sub-second page loads.
- **Conversational Voice Pipeline:** Built low-latency voice pipeline integrating Exotel WebSockets, Silero VAD voice interruption, and streaming Sarvam AI Indic LLMs.
"""

with open(md_path, "w") as f:
    f.write(md_content)
print("[+] Wrote Markdown companion resume.")
