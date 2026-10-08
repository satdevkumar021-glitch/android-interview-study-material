#!/usr/bin/env python3
"""
build_compact_handbook.py
Generates:
1. android_interview_compact_guide.html - High-density, print-optimized compact HTML guide
2. Android_Interview_Compact_Handbook.pdf - Compact, fast-revision PDF of all 97 topics
"""

import glob
import re
import os
import subprocess
import html

MODULE_NAMES = {
    1: "Kotlin Core & Language Features",
    2: "Android Core Components & Lifecycle",
    3: "System Architecture & Android Internals",
    4: "Architecture Components & Lifecycle State",
    5: "Kotlin Coroutines & Concurrency",
    6: "Kotlin Flow & Reactive Streams",
    7: "Jetpack Compose & Modern UI",
    8: "Architecture Patterns & Clean Architecture",
    9: "SOLID Principles in Android/Kotlin",
    10: "Design Patterns (GoF & Android)",
    11: "Dependency Injection (Hilt & Dagger)",
    12: "Networking, REST & HTTP Protocols",
    13: "Local Data Storage & Persistence",
    14: "Background Processing & Task Scheduling",
    15: "Android Services Deep Dive",
    16: "Broadcast Receivers & IPC Events",
    17: "Content Providers & Scoped Data Sharing",
    18: "Jetpack Navigation & Deep Linking",
    19: "Android Security, Cryptography & Hardening",
    20: "Automated Testing (Unit, Coroutines, UI)",
    21: "Android Performance & Profiling",
    22: "Memory Management & Leak Detection",
    23: "Gradle Build System & Convention Plugins",
    24: "Modularization Architecture",
    25: "CI/CD Pipelines & Mobile DevOps",
    26: "Code Quality, Linters & Static Analysis",
    27: "Android Permissions System & Scoped Storage",
    28: "RecyclerView & Legacy Android Views",
    29: "Paging 3 Architecture & Large Datasets",
    30: "Senior Android System Design Case Studies",
    31: "Firebase Integration & Cloud Architecture",
    32: "App Release, Signing & Play Store Deployment",
    33: "Scenario-Based Debugging & Troubleshooting",
    34: "Data Structures, Algorithms & Coding Practice",
    35: "Behavioral & Senior Engineering Leadership",
    36: "AI Developer Tools & On-Device AI for Android",
    37: "Jetpack Compose Animation & Motion",
    38: "Kotlin Multiplatform (KMP/KMM) in Production",
    39: "Android Accessibility (a11y) & Inclusive UI",
    40: "Modern Android Platform APIs (Android 12–16)",
    41: "Advanced Android Debugging, Tracing & Telemetry",
    42: "Compose Design Systems & Multi-Brand Theming",
}

def clean_tags(text):
    text = re.sub(r'<[^>]+>', ' ', text)
    text = html.unescape(text)
    return re.sub(r'\s+', ' ', text).strip()

def natural_sort_key(filename):
    m = re.match(r'^(\d+)([A-Z])_', os.path.basename(filename))
    if m:
        return (int(m.group(1)), m.group(2))
    return (9999, filename)

def extract_topic_compact(filepath):
    with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
        raw = f.read()

    m_code = re.match(r'^(\d+)([A-Z])_', os.path.basename(filepath))
    mod_num = int(m_code.group(1)) if m_code else 999
    sub_code = m_code.group(2) if m_code else ''
    code = f"{mod_num}{sub_code}"

    # Title
    title_m = re.search(r'<title>(.*?)</title>', raw, re.I)
    title = title_m.group(1).strip() if title_m else filepath
    clean_title = re.sub(r'^\d+[A-Z]\s*[—–-]\s*', '', title)
    clean_title = re.sub(r'\s*\|\s*Android Interview.*$', '', clean_title).strip()

    # Tier
    tier = 'Tier 1'
    if 'badge-tier2' in raw or 'badge t2' in raw or 'Tier 2' in raw:
        tier = 'Tier 2'
    elif 'badge-tier3' in raw or 'badge t3' in raw or 'Tier 3' in raw:
        tier = 'Tier 3'

    # Description
    desc_m = re.search(r'<p class=\"hero-desc\">(.*?)</p>', raw, re.S)
    if not desc_m:
        desc_m = re.search(r'<div class=\"meta\">(.*?)</div>', raw, re.S)
    desc = clean_tags(desc_m.group(1)) if desc_m else ""
    if len(desc) > 240:
        desc = desc[:237] + "..."

    # Sections extraction
    sections = {}
    if 'id="s1"' in raw:
        starts = [m.start() for m in re.finditer(r'<div class=[\"\']section[^\"]*[\"\']\s+id=[\"\']s\d[\"\']', raw)]
        for i, pos in enumerate(starts):
            end = starts[i+1] if i+1 < len(starts) else raw.find('</main>')
            chunk = raw[pos:end]
            sec_id = re.search(r'id=[\"\'](s\d)[\"\']', chunk).group(1)
            sections[sec_id] = chunk

        overview = sections.get('s1', '')
        how_it_works = sections.get('s2', '')
        pitfalls = sections.get('s6', '') or sections.get('s5', '')
        revision = sections.get('s8', '')
        quiz_sec = sections.get('s9', '')
    else:
        sec_matches = list(re.finditer(r'<section\s+id=[\"\']([^\"\']+)[\"\']', raw))
        for i, m in enumerate(sec_matches):
            pos = m.start()
            end = sec_matches[i+1].start() if i+1 < len(sec_matches) else raw.find('</main>')
            chunk = raw[pos:end]
            sections[m.group(1)] = chunk

        overview = sections.get('overview', '')
        how_it_works = sections.get('how', '')
        pitfalls = sections.get('pitfalls', '') or sections.get('alt', '')
        revision = sections.get('revision', '')
        quiz_sec = sections.get('quiz', '') or sections.get('interview', '')

    # Clean redundant elements
    def clean_chunk(ch):
        ch = re.sub(r'<div class=[\"\']section-title[\"\']>.*?</div>', '', ch, flags=re.S)
        ch = re.sub(r'<div class=[\"\']nav-buttons[\"\']>.*?</div>', '', ch, flags=re.S)
        ch = re.sub(r'<button class=[\"\']btn[^\"]*[\"\']>.*?</button>', '', ch, flags=re.S)
        ch = re.sub(r'onclick=[\"\'][^\"\']*[\"\']', '', ch)
        return ch

    overview_clean = clean_chunk(overview)
    revision_clean = clean_chunk(revision)
    pitfalls_clean = clean_chunk(pitfalls)

    # Extract Top 3 Quizzes
    quiz_items = []
    # Try quiz-card divs
    cards = re.findall(r'<div class=[\"\']quiz-card[\"\']>(.*?)</div>\s*</div>\s*</div>', quiz_sec, re.S)
    if not cards:
        cards = re.findall(r'<div class=[\"\']quiz-card[\"\']>(.*?)</div>\s*</div>', quiz_sec, re.S)

    for c in cards[:3]:
        q_text_m = re.search(r'class=[\"\']quiz-q-text[\"\']>(.*?)</div>', c, re.S)
        if not q_text_m:
            q_text_m = re.search(r'class=[\"\']quiz-q[\"\'][^>]*>(.*?)</div>', c, re.S)
        q_text = q_text_m.group(1).strip() if q_text_m else "Scenario Question"

        a_text_m = re.search(r'class=[\"\']quiz-a[\"\'][^>]*>(.*)$', c, re.S)
        a_text = a_text_m.group(1).strip() if a_text_m else "Answer details"

        quiz_items.append((q_text, a_text))

    # If details tags (Scrollable architecture)
    if not quiz_items:
        details_list = re.findall(r'<details[^>]*>(.*?)</details>', quiz_sec, re.S)
        for d in details_list[:3]:
            sum_m = re.search(r'<summary[^>]*>(.*?)</summary>', d, re.S)
            q_text = sum_m.group(1).strip() if sum_m else "Scenario Question"
            ans_m = re.search(r'class=[\"\']ans[\"\'][^>]*>(.*)$', d, re.S)
            a_text = ans_m.group(1).strip() if ans_m else d
            quiz_items.append((q_text, a_text))

    return {
        'code': code,
        'mod_num': mod_num,
        'clean_title': clean_title,
        'tier': tier,
        'desc': desc,
        'overview': overview_clean,
        'revision': revision_clean,
        'pitfalls': pitfalls_clean,
        'quizzes': quiz_items
    }

def build_compact_html(topic_data_list):
    # Group by module for Table of Contents
    modules = {}
    for t in topic_data_list:
        m = t['mod_num']
        if m not in modules:
            modules[m] = {
                'name': MODULE_NAMES.get(m, f"Module {m}"),
                'topics': []
            }
        modules[m]['topics'].append(t)

    # Build TOC HTML
    toc_html = ""
    for m in sorted(modules.keys()):
        mod = modules[m]
        toc_html += f"""
        <div class="compact-toc-group">
          <div class="compact-toc-mod-title">Module {m}: {mod['name']}</div>
          <div class="compact-toc-items">
        """
        for t in mod['topics']:
            tier_badge = f"<span class='compact-toc-tier tier-{t['tier'].lower().replace(' ', '')}'>{t['tier']}</span>"
            toc_html += f"""
            <a href="#topic-{t['code']}" class="compact-toc-link">
              <span class="compact-toc-code">{t['code']}</span>
              <span class="compact-toc-name">{t['clean_title']}</span>
              {tier_badge}
            </a>
            """
        toc_html += "</div></div>"

    # Build Topics HTML
    topics_html = ""
    for t in topic_data_list:
        tier_class = f"badge-{t['tier'].lower().replace(' ', '')}"
        
        # Build quiz HTML
        quizzes_html = ""
        for idx, (q, a) in enumerate(t['quizzes'], 1):
            quizzes_html += f"""
            <div class="compact-qa-box">
              <div class="compact-qa-q"><strong>Q{idx}:</strong> {q}</div>
              <div class="compact-qa-a">{a}</div>
            </div>
            """

        topics_html += f"""
        <section class="compact-topic" id="topic-{t['code']}">
          <!-- TOPIC HEADER -->
          <div class="compact-header">
            <div class="compact-header-left">
              <span class="compact-code">{t['code']}</span>
              <h2 class="compact-title">{html.escape(t['clean_title'])}</h2>
            </div>
            <div class="compact-header-right">
              <span class="badge {tier_class}">{t['tier']}</span>
              <span class="compact-mod-badge">Mod {t['mod_num']}</span>
            </div>
          </div>
          
          <div class="compact-desc">
            <strong>Key Concept:</strong> {html.escape(t['desc'])}
          </div>

          <div class="compact-grid">
            <!-- REVISION SHEET -->
            <div class="compact-col">
              <div class="compact-section-hdr">⚡ Quick Revision & Mechanics</div>
              <div class="compact-section-body">
                {t['revision'] if t['revision'].strip() else t['overview']}
              </div>
            </div>

            <!-- PITFALLS & GOTCHAS -->
            <div class="compact-col">
              <div class="compact-section-hdr">⚠️ Traps & Production Gotchas</div>
              <div class="compact-section-body">
                {t['pitfalls'] if t['pitfalls'].strip() else "<p>Always enforce non-null typing, test lifecycle cancellation, and verify memory leak profiles.</p>"}
              </div>
            </div>
          </div>

          <!-- TOP SCENARIO QUESTIONS -->
          <div class="compact-qa-section">
            <div class="compact-section-hdr">🎯 High-Yield Interview Q&As</div>
            <div class="compact-qa-list">
              {quizzes_html if quizzes_html else "<p>Review complete question set in master compendium.</p>"}
            </div>
          </div>
        </section>
        """

    full_html = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8"/>
<meta name="viewport" content="width=device-width, initial-scale=1.0"/>
<title>Android Senior & Staff Interview — Compact Quick-Revision Handbook</title>
<style>
  :root {{
    --font: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
    --mono: "JetBrains Mono", "Fira Code", "Cascadia Code", monospace;
    --text: #111827;
    --muted: #4b5563;
    --border: #d1d5db;
    --border-light: #e5e7eb;
    --bg-card: #f9fafb;
    --bg-code: #f3f4f6;
    --accent: #4f46e5;
    --accent-light: #e0e7ff;
    --green: #059669;
    --green-bg: #ecfdf5;
    --yellow: #d97706;
    --yellow-bg: #fffbeb;
    --red: #dc2626;
    --red-bg: #fef2f2;
    --blue: #2563eb;
    --blue-bg: #eff6ff;
  }}

  * {{ box-sizing: border-box; margin: 0; padding: 0; }}

  body {{
    font-family: var(--font);
    color: var(--text);
    background: #ffffff;
    font-size: 11pt;
    line-height: 1.45;
  }}

  /* COVER PAGE */
  .cover-page {{
    padding: 60pt 40pt;
    text-align: center;
    page-break-after: always;
    break-after: page;
    min-height: 85vh;
    display: flex;
    flex-direction: column;
    justify-content: center;
    align-items: center;
  }}

  .cover-tag {{
    display: inline-block;
    background: var(--accent-light);
    color: var(--accent);
    padding: 6pt 16pt;
    border-radius: 20pt;
    font-size: 11pt;
    font-weight: 700;
    letter-spacing: 0.05em;
    text-transform: uppercase;
    margin-bottom: 24pt;
  }}

  .cover-title {{
    font-size: 32pt;
    font-weight: 900;
    color: #0f172a;
    line-height: 1.2;
    margin-bottom: 16pt;
    max-width: 650pt;
  }}

  .cover-subtitle {{
    font-size: 15pt;
    color: var(--muted);
    max-width: 550pt;
    line-height: 1.5;
    margin-bottom: 36pt;
  }}

  .cover-stats {{
    display: flex;
    gap: 24pt;
    justify-content: center;
    margin-bottom: 40pt;
  }}

  .cover-stat-box {{
    background: var(--bg-card);
    border: 1px solid var(--border);
    border-radius: 8pt;
    padding: 14pt 24pt;
  }}

  .cover-stat-val {{
    font-size: 26pt;
    font-weight: 900;
    color: var(--accent);
  }}

  .cover-stat-lbl {{
    font-size: 10pt;
    text-transform: uppercase;
    color: var(--muted);
    font-weight: 600;
  }}

  /* TABLE OF CONTENTS */
  .compact-toc-page {{
    padding: 30pt 40pt;
    page-break-after: always;
    break-after: page;
  }}

  .compact-toc-page h2 {{
    font-size: 20pt;
    font-weight: 800;
    margin-bottom: 16pt;
    border-bottom: 2px solid var(--accent);
    padding-bottom: 8pt;
  }}

  .compact-toc-grid {{
    column-count: 2;
    column-gap: 24pt;
  }}

  .compact-toc-group {{
    break-inside: avoid;
    margin-bottom: 14pt;
  }}

  .compact-toc-mod-title {{
    font-size: 10pt;
    font-weight: 800;
    text-transform: uppercase;
    color: var(--accent);
    background: var(--accent-light);
    padding: 3pt 8pt;
    border-radius: 4pt;
    margin-bottom: 4pt;
  }}

  .compact-toc-items {{
    display: flex;
    flex-direction: column;
    gap: 2pt;
    padding-left: 4pt;
  }}

  .compact-toc-link {{
    display: flex;
    justify-content: space-between;
    align-items: center;
    text-decoration: none;
    color: var(--text);
    font-size: 9pt;
    padding: 2pt 4pt;
    border-radius: 3pt;
  }}
  .compact-toc-link:hover {{
    background: var(--bg-card);
    color: var(--accent);
  }}

  .compact-toc-code {{
    font-family: var(--mono);
    font-weight: 700;
    color: var(--accent);
    min-width: 24pt;
  }}

  .compact-toc-name {{
    flex: 1;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
    margin: 0 6pt;
  }}

  .compact-toc-tier {{
    font-size: 7pt;
    font-weight: 700;
    padding: 1pt 5pt;
    border-radius: 3pt;
  }}
  .tier-tier1 {{ background: var(--green-bg); color: var(--green); }}
  .tier-tier2 {{ background: var(--yellow-bg); color: var(--yellow); }}
  .tier-tier3 {{ background: var(--blue-bg); color: var(--blue); }}

  /* TOPIC CHAPTER (1-2 PAGES PER TOPIC) */
  .compact-topic {{
    page-break-before: always;
    break-before: page;
    padding: 28pt 36pt;
    border-bottom: 1px solid var(--border-light);
  }}

  .compact-header {{
    display: flex;
    justify-content: space-between;
    align-items: center;
    border-bottom: 1.5pt solid var(--border);
    padding-bottom: 8pt;
    margin-bottom: 8pt;
  }}

  .compact-header-left {{
    display: flex;
    align-items: baseline;
    gap: 10pt;
  }}

  .compact-code {{
    font-family: var(--mono);
    font-size: 14pt;
    font-weight: 900;
    color: #ffffff;
    background: var(--accent);
    padding: 2pt 8pt;
    border-radius: 4pt;
  }}

  .compact-title {{
    font-size: 15pt;
    font-weight: 800;
    color: #0f172a;
  }}

  .compact-header-right {{
    display: flex;
    gap: 6pt;
    align-items: center;
  }}

  .badge {{
    font-size: 8.5pt;
    font-weight: 700;
    padding: 2pt 8pt;
    border-radius: 4pt;
  }}
  .badge-tier1 {{ background: var(--green-bg); color: var(--green); border: 1px solid rgba(5,150,105,0.3); }}
  .badge-tier2 {{ background: var(--yellow-bg); color: var(--yellow); border: 1px solid rgba(217,119,6,0.3); }}
  .badge-tier3 {{ background: var(--blue-bg); color: var(--blue); border: 1px solid rgba(37,99,235,0.3); }}

  .compact-mod-badge {{
    font-size: 8.5pt;
    background: var(--bg-card);
    border: 1px solid var(--border);
    padding: 2pt 6pt;
    border-radius: 4pt;
    font-weight: 600;
    color: var(--muted);
  }}

  .compact-desc {{
    font-size: 10pt;
    color: #374151;
    background: var(--bg-card);
    border-left: 3pt solid var(--accent);
    padding: 6pt 10pt;
    border-radius: 0 4pt 4pt 0;
    margin-bottom: 12pt;
  }}

  /* TWO-COLUMN GRID */
  .compact-grid {{
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 14pt;
    margin-bottom: 14pt;
  }}

  .compact-col {{
    background: #ffffff;
    border: 1px solid var(--border);
    border-radius: 6pt;
    overflow: hidden;
  }}

  .compact-section-hdr {{
    background: var(--bg-card);
    border-bottom: 1px solid var(--border);
    padding: 5pt 10pt;
    font-size: 9.5pt;
    font-weight: 800;
    color: #1e293b;
    text-transform: uppercase;
    letter-spacing: 0.03em;
  }}

  .compact-section-body {{
    padding: 8pt 10pt;
    font-size: 9pt;
    line-height: 1.45;
  }}

  .compact-section-body h3, .compact-section-body h4 {{
    font-size: 9.5pt;
    font-weight: 700;
    color: var(--accent);
    margin: 6pt 0 3pt;
  }}
  .compact-section-body p {{ margin-bottom: 5pt; color: #374151; }}
  .compact-section-body ul, .compact-section-body ol {{ padding-left: 14pt; margin-bottom: 6pt; }}
  .compact-section-body li {{ margin-bottom: 3pt; color: #374151; }}

  /* CODE & TABLES IN COMPACT VIEW */
  pre, .ascii, .ascii-box {{
    background: var(--bg-code);
    border: 1px solid var(--border);
    border-radius: 4pt;
    padding: 6pt 8pt;
    font-family: var(--mono);
    font-size: 8pt;
    line-height: 1.35;
    margin: 5pt 0;
    overflow-x: auto;
    color: #1e293b;
    page-break-inside: avoid;
    break-inside: avoid;
  }}
  code {{ font-family: var(--mono); font-size: 8pt; }}
  p code, li code, td code {{
    background: #e5e7eb;
    color: #1e1b4b;
    padding: 1pt 4pt;
    border-radius: 3pt;
  }}

  table {{
    width: 100%;
    border-collapse: collapse;
    font-size: 8pt;
    margin: 5pt 0;
  }}
  th, td {{
    border: 1px solid var(--border);
    padding: 4pt 6pt;
    text-align: left;
    vertical-align: top;
  }}
  th {{ background: #f3f4f6; font-weight: 700; color: #111827; }}

  .cheat-grid, .grid2 {{
    display: grid;
    grid-template-columns: 1fr;
    gap: 6pt;
  }}
  .cheat-card, .card {{
    background: var(--bg-card);
    border: 1px solid var(--border-light);
    border-radius: 4pt;
    padding: 6pt;
  }}
  .cheat-card h4, .card h4 {{
    font-size: 8.5pt;
    font-weight: 700;
    color: var(--accent);
    margin-bottom: 3pt;
  }}

  /* QA SECTION */
  .compact-qa-section {{
    border: 1px solid var(--border);
    border-radius: 6pt;
    overflow: hidden;
    page-break-inside: avoid;
    break-inside: avoid;
  }}

  .compact-qa-list {{
    padding: 8pt 10pt;
    display: flex;
    flex-direction: column;
    gap: 8pt;
  }}

  .compact-qa-box {{
    background: var(--bg-card);
    border: 1px solid var(--border-light);
    border-radius: 4pt;
    padding: 6pt 8pt;
    font-size: 8.5pt;
    line-height: 1.4;
  }}

  .compact-qa-q {{
    font-weight: 700;
    color: #0f172a;
    margin-bottom: 4pt;
  }}

  .compact-qa-a {{
    color: #334155;
    padding-left: 6pt;
    border-left: 2pt solid var(--border);
  }}

  /* PRINT SETUP */
  @page {{
    size: A4 portrait;
    margin: 10mm 10mm 10mm 10mm;
  }}

  @media print {{
    body {{
      background: #ffffff !important;
      color: #000000 !important;
      font-size: 10pt !important;
    }}
    .compact-topic {{
      page-break-before: always !important;
      break-before: page !important;
      padding: 0 !important;
      margin-bottom: 15pt !important;
    }}
    .cover-page {{
      page-break-after: always !important;
      break-after: page !important;
      padding-top: 100pt !important;
    }}
    .compact-toc-page {{
      page-break-after: always !important;
      break-after: page !important;
      padding: 0 !important;
    }}
  }}
</style>
</head>
<body>

<!-- COVER PAGE -->
<div class="cover-page">
  <div class="cover-tag">Senior & Staff Android Engineering</div>
  <h1 class="cover-title">Android Interview Mastery</h1>
  <div class="cover-subtitle">Compact High-Yield Revision Handbook · 97 Topics Across 41 Core Tracks · Essential Architecture, Production Gotchas & Top Interview Scenarios</div>
  
  <div class="cover-stats">
    <div class="cover-stat-box">
      <div class="cover-stat-val">97</div>
      <div class="cover-stat-lbl">Topics</div>
    </div>
    <div class="cover-stat-box">
      <div class="cover-stat-val">41</div>
      <div class="cover-stat-lbl">Modules</div>
    </div>
    <div class="cover-stat-box">
      <div class="cover-stat-val">290+</div>
      <div class="cover-stat-lbl">Top Scenarios</div>
    </div>
    <div class="cover-stat-box">
      <div class="cover-stat-val">100%</div>
      <div class="cover-stat-lbl">Offline Ready</div>
    </div>
  </div>

  <p style="font-size:10pt; color:var(--muted);">Designed for rapid pre-interview revision, tablet reading, and clean printing.</p>
</div>

<!-- TABLE OF CONTENTS -->
<div class="compact-toc-page">
  <h2>Table of Contents (97 Topics)</h2>
  <div class="compact-toc-grid">
    {toc_html}
  </div>
</div>

<!-- COMPACT TOPICS -->
{topics_html}

</body>
</html>
"""
    return full_html

def main():
    print("=== Scanning all topic HTML files ===")
    files = [f for f in glob.glob('*.html') if re.match(r'^\d+[A-Z]_.*\.html$', f)]
    files = sorted(files, key=natural_sort_key)
    print(f"Found {len(files)} topic files.")

    print("Extracting compact data...")
    data_list = []
    for f in files:
        data_list.append(extract_topic_compact(f))

    print("Generating android_interview_compact_guide.html...")
    compact_html = build_compact_html(data_list)
    with open('android_interview_compact_guide.html', 'w', encoding='utf-8') as out:
        out.write(compact_html)
    print(f"Generated android_interview_compact_guide.html ({len(compact_html)} bytes)")

    print("Converting to Android_Interview_Compact_Handbook.pdf via Chrome headless...")
    chrome_cmd = [
        "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
        "--headless=new",
        "--disable-gpu",
        "--no-pdf-header-footer",
        "--print-to-pdf=Android_Interview_Compact_Handbook.pdf",
        "android_interview_compact_guide.html"
    ]
    res = subprocess.run(chrome_cmd, capture_output=True, text=True)
    if os.path.exists("Android_Interview_Compact_Handbook.pdf"):
        size_mb = os.path.getsize("Android_Interview_Compact_Handbook.pdf") / 1024 / 1024
        print(f"Generated Android_Interview_Compact_Handbook.pdf ({size_mb:.2f} MB)")
    else:
        print("Error: Chrome failed to generate PDF:", res.stderr)

if __name__ == '__main__':
    main()
