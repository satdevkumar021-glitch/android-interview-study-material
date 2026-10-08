#!/usr/bin/env python3
"""
build_portal.py
Scans all Android Interview topic HTML files, validates their contents,
and builds:
1. topics_manifest.json
2. index.html - Master Study Hub & Interactive Reader
3. all_topics_combined.html - Master All-in-One Concatenated Compendium
"""

import os
import glob
import re
import json
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
    36: "AI Developer Tools & MCP for Android",
    37: "Jetpack Compose Animation & Motion",
    38: "Kotlin Multiplatform (KMP/KMM) in Production",
    39: "Android Accessibility (a11y) & Inclusive UI",
    40: "Modern Android Platform APIs (Android 12–16)",
    41: "Advanced Android Debugging, Tracing & Telemetry",
    42: "Compose Design Systems & Multi-Brand Theming",
}

def natural_sort_key(filename):
    m = re.match(r'^(\d+)([A-Z])_(.*)\.html$', os.path.basename(filename))
    if m:
        return (int(m.group(1)), m.group(2), m.group(3))
    return (9999, filename, '')

def clean_html_tags(text):
    text = re.sub(r'<[^>]+>', ' ', text)
    text = html.unescape(text)
    return re.sub(r'\s+', ' ', text).strip()

def scan_topics():
    all_files = sorted(glob.glob('*.html'))
    # Only pick actual topic files: e.g. 1A_..., 18A_..., 19B_...
    topic_files = [f for f in all_files if re.match(r'^\d+[A-Z]_.*\.html$', f)]
    topic_files = sorted(topic_files, key=natural_sort_key)
    
    topics = []
    for f in topic_files:
        with open(f, 'r', encoding='utf-8', errors='ignore') as fp:
            raw = fp.read()
            
        m = re.match(r'^(\d+)([A-Z])_(.*)\.html$', f)
        mod_num = int(m.group(1))
        mod_sub = m.group(2)
        slug = m.group(3)
        code = f"{mod_num}{mod_sub}"
        
        # Title
        title_m = re.search(r'<title>(.*?)</title>', raw, re.I)
        raw_title = title_m.group(1).strip() if title_m else f
        clean_title = re.sub(r'^\d+[A-Z]\s*[—–-]\s*', '', raw_title)
        clean_title = re.sub(r'\s*\|\s*Android Interview.*$', '', clean_title).strip()
        clean_title = html.unescape(clean_title)
        
        # Hero Description
        desc_m = re.search(r'<p class=\"hero-desc\">(.*?)</p>', raw, re.S)
        if not desc_m:
            desc_m = re.search(r'<div class=\"meta\">(.*?)</div>', raw, re.S)
        if not desc_m:
            desc_m = re.search(r'<div class=\"hero\">(.*?)</div>', raw, re.S)
        desc = clean_html_tags(desc_m.group(1)) if desc_m else "Comprehensive Android interview guide and deep dive."
        if len(desc) > 230:
            desc = desc[:227] + "..."
            
        # Tier
        tier = "Tier 1"
        if "badge-tier2" in raw or 'class="badge t2"' in raw or "Tier 2" in raw:
            tier = "Tier 2"
        elif "badge-tier3" in raw or 'class="badge t3"' in raw or "Tier 3" in raw:
            tier = "Tier 3"
            
        # Quizzes
        quiz_cnt = len(re.findall(r'class=[\"\']quiz-card[\"\']', raw)) + len(re.findall(r'<details', raw))
        
        # Sections
        sections = re.findall(r'<div class=[\"\']section[^\"]*[\"\']\s+id=[\"\']([^\"\']+)[\"\']', raw)
        if not sections:
            sections = re.findall(r'<section\s+id=[\"\']([^\"\']+)[\"\']', raw)
            
        is_tabbed = 'class="section' in raw or "class='section" in raw
        style_type = "Tabbed" if is_tabbed else "Scrollable"
        
        topics.append({
            'file': f,
            'code': code,
            'mod_num': mod_num,
            'mod_sub': mod_sub,
            'slug': slug,
            'clean_title': clean_title,
            'raw_title': raw_title,
            'desc': desc,
            'tier': tier,
            'quizzes': quiz_cnt,
            'sections': len(sections),
            'style_type': style_type
        })
        
    return topics

def generate_index_html(topics):
    modules = {}
    for t in topics:
        m = t['mod_num']
        if m not in modules:
            modules[m] = {
                'id': m,
                'name': MODULE_NAMES.get(m, f"Module {m}"),
                'topics': []
            }
        modules[m]['topics'].append(t)
        
    total_topics = len(topics)
    total_quizzes = sum(t['quizzes'] for t in topics)
    total_modules = len(modules)
    tier1_cnt = sum(1 for t in topics if t['tier'] == 'Tier 1')
    tier2_cnt = sum(1 for t in topics if t['tier'] == 'Tier 2')
    tier3_cnt = sum(1 for t in topics if t['tier'] == 'Tier 3')
    
    modules_json = json.dumps(topics)
    
    html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8"/>
<meta name="viewport" content="width=device-width, initial-scale=1.0"/>
<title>Android Staff & Senior Interview Master Portal</title>
<style>
  :root {{
    --bg: #0b0d14;
    --surface: #141724;
    --surface-card: #1b1f30;
    --surface-hover: #242940;
    --border: #292d47;
    --border-subtle: #1f2338;
    --text: #e6e8f5;
    --muted: #8d93b8;
    --accent: #7c6af7;
    --accent-light: #9d8fff;
    --accent-glow: rgba(124, 106, 247, 0.25);
    --green: #3ecf8e;
    --green-glow: rgba(62, 207, 142, 0.2);
    --blue: #4f9eff;
    --yellow: #f5c842;
    --red: #ff6b6b;
    --radius: 12px;
    --radius-sm: 8px;
    --font-mono: "JetBrains Mono", "Fira Code", monospace;
  }}

  * {{ box-sizing: border-box; margin: 0; padding: 0; }}

  body {{
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
    background: var(--bg);
    color: var(--text);
    min-height: 100vh;
    line-height: 1.6;
    overflow-x: hidden;
  }}

  /* HEADER */
  header.portal-header {{
    background: linear-gradient(180deg, #181b2b 0%, #0e101a 100%);
    border-bottom: 1px solid var(--border);
    padding: 32px 40px;
    position: relative;
    box-shadow: 0 4px 24px rgba(0,0,0,0.4);
  }}

  .header-content {{
    max-width: 1440px;
    margin: 0 auto;
    display: flex;
    flex-direction: column;
    gap: 20px;
  }}

  .header-top {{
    display: flex;
    justify-content: space-between;
    align-items: flex-start;
    flex-wrap: wrap;
    gap: 20px;
  }}

  .header-title-box h1 {{
    font-size: 28px;
    font-weight: 800;
    letter-spacing: -0.02em;
    display: flex;
    align-items: center;
    gap: 12px;
  }}

  .header-title-box h1 span.logo-tag {{
    background: linear-gradient(135deg, #7c6af7, #4f9eff);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
  }}

  .header-title-box p {{
    color: var(--muted);
    font-size: 15px;
    margin-top: 6px;
    max-width: 780px;
  }}

  .header-actions {{
    display: flex;
    gap: 12px;
    flex-wrap: wrap;
  }}

  .btn {{
    display: inline-flex;
    align-items: center;
    gap: 8px;
    padding: 10px 18px;
    border-radius: var(--radius-sm);
    font-size: 13.5px;
    font-weight: 600;
    cursor: pointer;
    text-decoration: none;
    transition: all 0.2s ease;
    border: 1px solid transparent;
  }}

  .btn-primary {{
    background: var(--accent);
    color: #fff;
    box-shadow: 0 4px 16px var(--accent-glow);
  }}
  .btn-primary:hover {{
    background: var(--accent-light);
    transform: translateY(-1px);
    box-shadow: 0 6px 20px rgba(124, 106, 247, 0.4);
  }}

  .btn-secondary {{
    background: var(--surface-card);
    color: var(--text);
    border-color: var(--border);
  }}
  .btn-secondary:hover {{
    background: var(--surface-hover);
    border-color: var(--accent);
    color: #fff;
  }}

  .btn-accent2 {{
    background: rgba(62, 207, 142, 0.12);
    color: var(--green);
    border-color: rgba(62, 207, 142, 0.3);
  }}
  .btn-accent2:hover {{
    background: rgba(62, 207, 142, 0.2);
    border-color: var(--green);
  }}

  /* STATS BAR */
  .stats-grid {{
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
    gap: 16px;
    margin-top: 6px;
  }}

  .stat-card {{
    background: rgba(27, 31, 48, 0.6);
    backdrop-filter: blur(8px);
    border: 1px solid var(--border-subtle);
    border-radius: var(--radius);
    padding: 16px 20px;
    display: flex;
    flex-direction: column;
    gap: 4px;
    transition: transform 0.2s;
  }}
  .stat-card:hover {{
    transform: translateY(-2px);
    border-color: var(--border);
  }}

  .stat-label {{
    font-size: 12px;
    text-transform: uppercase;
    letter-spacing: 0.06em;
    color: var(--muted);
    font-weight: 600;
  }}

  .stat-val {{
    font-size: 24px;
    font-weight: 800;
    color: var(--text);
    display: flex;
    align-items: baseline;
    gap: 6px;
  }}

  .stat-val span.sub {{
    font-size: 13px;
    color: var(--muted);
    font-weight: 500;
  }}

  .progress-bar-wrap {{
    background: var(--surface);
    height: 8px;
    border-radius: 4px;
    overflow: hidden;
    margin-top: 8px;
    border: 1px solid var(--border-subtle);
  }}

  .progress-bar-fill {{
    height: 100%;
    background: linear-gradient(90deg, #7c6af7, #3ecf8e);
    width: 0%;
    transition: width 0.4s ease;
  }}

  /* TOOLBAR / CONTROLS */
  .controls-bar {{
    max-width: 1440px;
    margin: 0 auto;
    padding: 14px 40px;
    display: flex;
    gap: 16px;
    align-items: center;
    flex-wrap: wrap;
    justify-content: space-between;
    position: sticky;
    top: 0;
    z-index: 100;
    background: var(--bg);
    border-bottom: 1px solid var(--border-subtle);
  }}

  .search-box {{
    position: relative;
    flex: 1;
    min-width: 280px;
    max-width: 500px;
  }}

  .search-box input {{
    width: 100%;
    background: var(--surface-card);
    border: 1px solid var(--border);
    border-radius: var(--radius-sm);
    padding: 12px 16px 12px 42px;
    color: var(--text);
    font-size: 14px;
    outline: none;
    transition: all 0.2s;
  }}

  .search-box input:focus {{
    border-color: var(--accent);
    box-shadow: 0 0 0 3px var(--accent-glow);
  }}

  .search-box svg {{
    position: absolute;
    left: 14px;
    top: 50%;
    transform: translateY(-50%);
    width: 18px;
    height: 18px;
    fill: var(--muted);
  }}

  .filter-pills {{
    display: flex;
    gap: 8px;
    flex-wrap: wrap;
  }}

  .pill {{
    background: var(--surface-card);
    color: var(--muted);
    border: 1px solid var(--border-subtle);
    padding: 7px 14px;
    border-radius: 20px;
    font-size: 12.5px;
    font-weight: 600;
    cursor: pointer;
    transition: all 0.15s;
    user-select: none;
  }}
  .pill:hover {{
    color: var(--text);
    border-color: var(--border);
  }}
  .pill.active {{
    background: rgba(124, 106, 247, 0.15);
    color: var(--accent);
    border-color: var(--accent);
  }}

  /* BODY LAYOUT */
  .portal-body {{
    max-width: 1440px;
    margin: 24px auto 80px;
    padding: 0 40px;
    display: grid;
    grid-template-columns: 340px 1fr;
    gap: 28px;
    align-items: start;
  }}

  @media(max-width: 1024px) {{
    .portal-body {{
      grid-template-columns: 1fr;
      padding: 0 20px;
    }}
    .controls-bar {{
      padding: 0 20px;
    }}
    header.portal-header {{
      padding: 24px 20px;
    }}
  }}

  /* SIDEBAR ACCORDION */
  .modules-sidebar {{
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: var(--radius);
    padding: 18px 14px;
    position: sticky;
    top: 76px;
    max-height: calc(100vh - 96px);
    overflow-y: auto;
  }}

  .sidebar-title {{
    font-size: 12px;
    text-transform: uppercase;
    letter-spacing: 0.08em;
    color: var(--muted);
    font-weight: 700;
    padding: 4px 10px 14px;
    border-bottom: 1px solid var(--border);
    display: flex;
    justify-content: space-between;
    align-items: center;
  }}

  .module-group {{
    margin-top: 10px;
    border-bottom: 1px solid var(--border-subtle);
    padding-bottom: 10px;
  }}

  .module-header {{
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 9px 10px;
    border-radius: var(--radius-sm);
    cursor: pointer;
    font-size: 13.5px;
    font-weight: 600;
    color: var(--text);
    transition: background 0.15s;
    user-select: none;
  }}
  .module-header:hover {{
    background: var(--surface-card);
  }}

  .module-header .m-num {{
    background: rgba(124, 106, 247, 0.15);
    color: var(--accent);
    font-size: 11px;
    font-weight: 700;
    padding: 2px 7px;
    border-radius: 4px;
    margin-right: 8px;
  }}

  .module-header .arrow {{
    font-size: 10px;
    color: var(--muted);
    transition: transform 0.2s;
  }}
  .module-group.collapsed .arrow {{
    transform: rotate(-90deg);
  }}
  .module-group.collapsed .module-topics-list {{
    display: none;
  }}

  .module-topics-list {{
    padding: 4px 0 4px 8px;
    display: flex;
    flex-direction: column;
    gap: 3px;
  }}

  /* REAL HYPERLINK FOR SIDEBAR */
  .sidebar-topic-link {{
    display: flex;
    align-items: center;
    gap: 10px;
    padding: 8px 10px;
    border-radius: 6px;
    font-size: 12.5px;
    color: var(--muted);
    text-decoration: none;
    transition: all 0.15s;
  }}
  .sidebar-topic-link:hover {{
    background: var(--surface-card);
    color: var(--text);
    transform: translateX(2px);
  }}
  .sidebar-topic-link.active {{
    background: rgba(124, 106, 247, 0.15);
    color: var(--accent);
    font-weight: 600;
  }}

  .sidebar-topic-link .check-icon {{
    width: 16px;
    height: 16px;
    border-radius: 4px;
    border: 1.5px solid var(--muted);
    display: inline-flex;
    align-items: center;
    justify-content: center;
    font-size: 10px;
    flex-shrink: 0;
    color: transparent;
  }}
  .sidebar-topic-link.studied .check-icon {{
    background: var(--green);
    border-color: var(--green);
    color: #0b0d14;
    font-weight: 900;
  }}

  /* MAIN CONTENT AREA */
  .portal-main {{
    display: flex;
    flex-direction: column;
    gap: 24px;
  }}

  /* IN-APP STUDY READER CONTAINER */
  #studyReaderContainer {{
    display: none;
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: var(--radius);
    overflow: hidden;
    box-shadow: 0 8px 32px rgba(0,0,0,0.5);
    margin-bottom: 24px;
  }}

  #studyReaderContainer.active {{
    display: flex;
    flex-direction: column;
  }}

  .reader-toolbar {{
    background: #10121d;
    border-bottom: 1px solid var(--border);
    padding: 12px 20px;
    display: flex;
    align-items: center;
    justify-content: space-between;
    flex-wrap: wrap;
    gap: 12px;
  }}

  .reader-info {{
    display: flex;
    align-items: center;
    gap: 12px;
  }}

  .reader-title {{
    font-size: 15px;
    font-weight: 700;
    color: var(--text);
  }}

  .reader-controls {{
    display: flex;
    align-items: center;
    gap: 8px;
  }}

  .reader-iframe {{
    width: 100%;
    height: 82vh;
    border: none;
    background: #0f1117;
  }}

  /* TOPIC GRID ROADMAP */
  .module-section {{
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: var(--radius);
    padding: 24px 28px;
    margin-bottom: 24px;
    transition: border-color 0.2s;
  }}

  .module-section-header {{
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 18px;
    padding-bottom: 12px;
    border-bottom: 1px solid var(--border-subtle);
  }}

  .module-section-title {{
    font-size: 18px;
    font-weight: 700;
    display: flex;
    align-items: center;
    gap: 10px;
  }}

  .module-badge {{
    background: rgba(124, 106, 247, 0.12);
    color: var(--accent);
    font-size: 12px;
    padding: 3px 10px;
    border-radius: 6px;
    border: 1px solid rgba(124, 106, 247, 0.3);
  }}

  .topics-grid {{
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(320px, 1fr));
    gap: 16px;
  }}

  /* THE TOPIC CARD IS NOW A DIRECT CLICKABLE LINK */
  a.topic-card {{
    background: var(--surface-card);
    border: 1px solid var(--border-subtle);
    border-radius: var(--radius-sm);
    padding: 18px;
    display: flex;
    flex-direction: column;
    justify-content: space-between;
    gap: 14px;
    transition: all 0.2s ease;
    text-decoration: none;
    color: inherit;
    cursor: pointer;
    position: relative;
  }}

  a.topic-card:hover {{
    transform: translateY(-3px);
    border-color: var(--accent);
    background: var(--surface-hover);
    box-shadow: 0 6px 20px rgba(0,0,0,0.35);
  }}

  a.topic-card.studied {{
    border-color: rgba(62, 207, 142, 0.35);
    background: linear-gradient(180deg, #182030 0%, #131726 100%);
  }}

  .topic-card-header {{
    display: flex;
    justify-content: space-between;
    align-items: flex-start;
    gap: 10px;
  }}

  .topic-code {{
    font-family: var(--font-mono);
    font-size: 13px;
    font-weight: 700;
    color: var(--accent);
    background: rgba(124, 106, 247, 0.12);
    padding: 2px 8px;
    border-radius: 4px;
    border: 1px solid rgba(124, 106, 247, 0.25);
  }}

  .badge-tier1 {{
    background: rgba(62, 207, 142, 0.12);
    color: var(--green);
    border: 1px solid rgba(62, 207, 142, 0.25);
    font-size: 11px;
    padding: 2px 8px;
    border-radius: 4px;
    font-weight: 600;
  }}
  .badge-tier2 {{
    background: rgba(245, 200, 66, 0.12);
    color: var(--yellow);
    border: 1px solid rgba(245, 200, 66, 0.25);
    font-size: 11px;
    padding: 2px 8px;
    border-radius: 4px;
    font-weight: 600;
  }}
  .badge-tier3 {{
    background: rgba(79, 158, 255, 0.12);
    color: var(--blue);
    border: 1px solid rgba(79, 158, 255, 0.25);
    font-size: 11px;
    padding: 2px 8px;
    border-radius: 4px;
    font-weight: 600;
  }}

  .topic-card-body h3 {{
    font-size: 15.5px;
    font-weight: 700;
    color: var(--text);
    margin-bottom: 6px;
    line-height: 1.4;
    transition: color 0.15s;
  }}
  a.topic-card:hover .topic-card-body h3 {{
    color: var(--accent-light);
  }}

  .topic-card-body p {{
    font-size: 13px;
    color: var(--muted);
    line-height: 1.5;
  }}

  .topic-card-footer {{
    display: flex;
    justify-content: space-between;
    align-items: center;
    border-top: 1px solid var(--border-subtle);
    padding-top: 12px;
    gap: 8px;
  }}

  .quiz-count-badge {{
    font-size: 12px;
    color: var(--muted);
    display: inline-flex;
    align-items: center;
    gap: 4px;
  }}

  .card-action-btns {{
    display: flex;
    align-items: center;
    gap: 8px;
  }}

  .btn-sm {{
    padding: 5px 10px;
    font-size: 12px;
    border-radius: 5px;
  }}

  .study-toggle-btn {{
    background: none;
    border: none;
    cursor: pointer;
    font-size: 18px;
    color: var(--muted);
    display: inline-flex;
    align-items: center;
    padding: 4px;
    transition: transform 0.15s;
  }}
  .study-toggle-btn:hover {{
    transform: scale(1.15);
  }}

  .open-arrow {{
    font-size: 13px;
    font-weight: 700;
    color: var(--accent);
    display: inline-flex;
    align-items: center;
    gap: 4px;
  }}
  a.topic-card:hover .open-arrow {{
    color: #fff;
    transform: translateX(3px);
  }}

  
  /* MODALS FOR ROADMAP & AI PLAYBOOK */
  .portal-modal-backdrop {{
    display: none;
    position: fixed;
    top: 0; left: 0; right: 0; bottom: 0;
    background: rgba(8, 10, 16, 0.85);
    backdrop-filter: blur(10px);
    z-index: 2000;
    justify-content: center;
    align-items: center;
    padding: 24px;
  }}
  .portal-modal-backdrop.active {{
    display: flex;
  }}
  .portal-modal {{
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: var(--radius);
    width: 100%;
    max-width: 980px;
    max-height: 88vh;
    overflow-y: auto;
    box-shadow: 0 16px 48px rgba(0,0,0,0.6);
    display: flex;
    flex-direction: column;
    animation: modalSlideIn 0.25s ease;
  }}
  @keyframes modalSlideIn {{
    from {{ opacity: 0; transform: translateY(16px); }}
    to {{ opacity: 1; transform: translateY(0); }}
  }}
  .portal-modal-header {{
    background: #10121e;
    border-bottom: 1px solid var(--border);
    padding: 20px 28px;
    display: flex;
    justify-content: space-between;
    align-items: center;
    position: sticky;
    top: 0;
    z-index: 10;
  }}
  .portal-modal-header h2 {{
    font-size: 20px;
    font-weight: 800;
    color: var(--text);
    display: flex;
    align-items: center;
    gap: 10px;
  }}
  .portal-modal-body {{
    padding: 28px;
    color: var(--text);
    font-size: 14.5px;
    line-height: 1.7;
  }}
  .portal-modal-body h3 {{
    font-size: 16px;
    color: var(--accent);
    margin: 22px 0 10px;
    border-bottom: 1px solid var(--border-subtle);
    padding-bottom: 6px;
  }}
  .portal-modal-body h4 {{
    font-size: 14.5px;
    color: var(--yellow);
    margin: 16px 0 6px;
  }}
  .portal-modal-body p {{
    color: var(--muted);
    margin-bottom: 12px;
  }}
  .portal-modal-body ul, .portal-modal-body ol {{
    margin: 8px 0 16px 24px;
    color: var(--muted);
  }}
  .portal-modal-body li {{
    margin-bottom: 6px;
  }}
  .portal-modal-body li strong {{
    color: var(--text);
  }}
  .roadmap-tabs {{
    display: flex;
    gap: 8px;
    margin-bottom: 20px;
    border-bottom: 1px solid var(--border);
    padding-bottom: 12px;
    flex-wrap: wrap;
  }}
  .roadmap-tab-btn {{
    background: var(--surface-card);
    border: 1px solid var(--border-subtle);
    color: var(--muted);
    padding: 8px 16px;
    border-radius: var(--radius-sm);
    font-weight: 600;
    font-size: 13px;
    cursor: pointer;
  }}
  .roadmap-tab-btn:hover {{ color: var(--text); border-color: var(--border); }}
  .roadmap-tab-btn.active {{
    background: rgba(124, 106, 247, 0.15);
    color: var(--accent);
    border-color: var(--accent);
  }}
  .roadmap-content-pane {{ display: none; }}
  .roadmap-content-pane.active {{ display: block; }}
  .code-snippet {{
    background: #0d0f17;
    border: 1px solid var(--border);
    border-radius: 6px;
    padding: 14px;
    font-family: var(--font-mono);
    font-size: 12.5px;
    color: #abb2bf;
    overflow-x: auto;
    margin: 10px 0 16px;
  }}

  /* EMPTY SEARCH STATE */
  #noResults {{
    display: none;
    text-align: center;
    padding: 60px 20px;
    color: var(--muted);
    background: var(--surface);
    border: 1px dashed var(--border);
    border-radius: var(--radius);
  }}

  .shortcut-hint {{
    font-size: 11px;
    color: var(--muted);
    background: var(--surface-card);
    padding: 2px 6px;
    border-radius: 4px;
    border: 1px solid var(--border);
    font-family: var(--font-mono);
  }}
</style>
</head>
<body>

<header class="portal-header">
  <div class="header-content">
    <div class="header-top">
      <div class="header-title-box">
        <h1>
          <span>⚡</span>
          <span class="logo-tag">Android Interview Master Hub</span>
        </h1>
        <p>Complete curriculum covering Android & Kotlin senior/staff engineering topics. Click any topic card to open the complete study material, or use the interactive Study Reader or All-in-One Compendium.</p>
      </div>
      <div class="header-actions">
        <a href="Android_Interview_Topic_Wise_PDFs.zip" class="btn btn-accent2" download style="background: linear-gradient(135deg, #4338ca, #6366f1); border:none; box-shadow: 0 4px 16px rgba(99,102,241,0.35);">
          📦 All 97 Topic PDFs (ZIP)
        </a>
        <a href="Android_Interview_Compact_Handbook.pdf" class="btn btn-primary" download style="background: linear-gradient(135deg, #059669, #10b981); border:none; box-shadow: 0 4px 16px rgba(16,185,129,0.35);">
          📄 Compact PDF (219 Pgs)
        </a>
        <a href="Android_Interview_Complete_Master.pdf" class="btn btn-secondary" download style="border-color: #6366f1; color: #a5b4fc;">
          📚 Complete PDF (1,037 Pgs)
        </a>
        <button class="btn btn-accent2" onclick="openRoadmapModal()">
          🗺️ Roadmap
        </button>
        <button class="btn btn-secondary" style="border-color:var(--accent); color:var(--accent-light);" onclick="openAiModal()">
          🤖 AI Playbook
        </button>
        <a href="all_topics_combined.html" class="btn btn-secondary" target="_blank">
          🌐 Compendium
        </a>
        <button class="btn btn-secondary" onclick="resetProgress()">
          🔄 Reset
        </button>
      </div>
    </div>

    <!-- STATS METRICS -->
    <div class="stats-grid">
      <div class="stat-card">
        <span class="stat-label">Total Topics</span>
        <div class="stat-val">{total_topics} <span class="sub">deep dives</span></div>
      </div>
      <div class="stat-card">
        <span class="stat-label">Modules</span>
        <div class="stat-val">{total_modules} <span class="sub">core tracks</span></div>
      </div>
      <div class="stat-card">
        <span class="stat-label">Interview Quizzes</span>
        <div class="stat-val">{total_quizzes} <span class="sub">scenarios</span></div>
      </div>
      <div class="stat-card">
        <span class="stat-label">Study Progress</span>
        <div class="stat-val"><span id="progressPercent">0%</span> <span class="sub" id="progressFraction">0/{total_topics}</span></div>
        <div class="progress-bar-wrap">
          <div class="progress-bar-fill" id="progressBarFill"></div>
        </div>
      </div>
    </div>
  </div>
</header>

<!-- SEARCH & FILTERS -->
<div class="controls-bar">
  <div class="search-box">
    <svg viewBox="0 0 24 24"><path d="M15.5 14h-.79l-.28-.27A6.471 6.471 0 0 0 16 9.5 6.5 6.5 0 1 0 9.5 16c1.61 0 3.09-.59 4.23-1.57l.27.28v.79l5 4.99L20.49 19l-4.99-5zm-6 0C7.01 14 5 11.99 5 9.5S7.01 5 9.5 5 14 7.01 14 9.5 11.99 14 9.5 14z"/></svg>
    <input type="text" id="searchInput" placeholder="Search topics, coroutines, compose, binder, SOLID, security..." oninput="handleSearch()"/>
  </div>

  <div class="filter-pills">
    <div class="pill active" data-filter="all" onclick="setFilter('all')">All ({total_topics})</div>
    <div class="pill" data-filter="Tier 1" onclick="setFilter('Tier 1')">Tier 1: Core ({tier1_cnt})</div>
    <div class="pill" data-filter="Tier 2" onclick="setFilter('Tier 2')">Tier 2: Advanced ({tier2_cnt})</div>
    <div class="pill" data-filter="Tier 3" onclick="setFilter('Tier 3')">Tier 3: Specialized ({tier3_cnt})</div>
    <div class="pill" data-filter="sysdesign" onclick="setFilter('sysdesign')">🏛️ System Design</div>
    <div class="pill" data-filter="coding" onclick="setFilter('coding')">💻 Coding / DS</div>
    <div class="pill" data-filter="aimodern" onclick="setFilter('aimodern')">🤖 AI & Modern</div>
    <div class="pill" data-filter="studied" onclick="setFilter('studied')">Studied (<span id="studiedCount">0</span>)</div>
    <div class="pill" data-filter="unstudied" onclick="setFilter('unstudied')">Remaining (<span id="unstudiedCount">{total_topics}</span>)</div>
  </div>
</div>

<!-- BODY LAYOUT -->
<div class="portal-body">
  <!-- SIDEBAR NAVIGATION -->
  <aside class="modules-sidebar">
    <div class="sidebar-title">
      <span>Curriculum Modules</span>
      <span class="shortcut-hint">{total_topics} Topics</span>
    </div>
    <div id="sidebarModulesList">
      <!-- Populated via JS with actual <a> links -->
    </div>
  </aside>

  <!-- MAIN AREA -->
  <main class="portal-main">
    <!-- IN-APP STUDY READER CONTAINER -->
    <div id="studyReaderContainer">
      <div class="reader-toolbar">
        <div class="reader-info">
          <button class="btn btn-secondary btn-sm" onclick="navigateTopic(-1)" title="Previous Topic (Shortcut: Left Arrow or [)">← Prev</button>
          <div class="reader-title" id="readerTopicTitle">Topic Title</div>
          <button class="btn btn-secondary btn-sm" onclick="navigateTopic(1)" title="Next Topic (Shortcut: Right Arrow or ])">Next →</button>
        </div>
        <div class="reader-controls">
          <button class="btn btn-accent2 btn-sm" id="readerMarkStudiedBtn" onclick="toggleCurrentTopicStudied()">Mark Studied ✓</button>
          <a id="readerExternalLink" href="#" target="_blank" class="btn btn-secondary btn-sm" title="Open in dedicated tab">Open Dedicated Tab ↗</a>
          <button class="btn btn-secondary btn-sm" onclick="closeStudyReader()">Close ✕</button>
        </div>
      </div>
      <iframe id="studyIframe" class="reader-iframe" src="about:blank"></iframe>
    </div>


    <!-- PREPARATION ROADMAP MODAL -->
    <div id="roadmapModal" class="portal-modal-backdrop" onclick="closeModalOnBackdrop(event, 'roadmapModal')">
      <div class="portal-modal">
        <div class="portal-modal-header">
          <h2>🗺️ Android Senior & Staff Preparation Roadmap</h2>
          <button class="btn btn-secondary btn-sm" onclick="closeRoadmapModal()">Close ✕</button>
        </div>
        <div class="portal-modal-body">
          <p>Choose your preparation track based on your target timeline and interview goals. All 97 topics are mapped below:</p>
          
          <div class="roadmap-tabs">
            <button class="roadmap-tab-btn active" onclick="switchRoadmapTab('tab30')">⚡ 30-Day Senior Sprint</button>
            <button class="roadmap-tab-btn" onclick="switchRoadmapTab('tab60')">🏆 60-Day Full Staff Mastery</button>
            <button class="roadmap-tab-btn" onclick="switchRoadmapTab('tabSys')">🏛️ 14-Day System Design Track</button>
            <button class="roadmap-tab-btn" onclick="switchRoadmapTab('tabCoding')">💻 Live Coding & Algorithms</button>
            <button class="roadmap-tab-btn" onclick="switchRoadmapTab('tabMethod')">📖 5-Step Study Protocol</button>
          </div>

          <!-- TAB 1: 30-DAY -->
          <div id="tab30" class="roadmap-content-pane active">
            <h4>Week 1: Kotlin Core, Coroutines & Reactive Flow</h4>
            <ul>
              <li><strong>Days 1–2: Kotlin Core Essentials</strong> — Topics 1A (Null Safety), 1C (Scope Functions), 1D (OOP), 1E (Special Classes), 1F (Generics & Variance).</li>
              <li><strong>Days 3–5: Coroutines & Concurrency</strong> — Topics 5A (Fundamentals), 5B (Dispatchers), 5C (Structured Concurrency), 5D (Cancellation & Exceptions), 5E (Testing).</li>
              <li><strong>Days 6–7: Kotlin Flow</strong> — Topics 6A (Cold vs Hot), 6B (Operators), 6C (Channels), 6D (stateIn / shareIn).</li>
            </ul>

            <h4>Week 2: Jetpack Compose & Clean Architecture</h4>
            <ul>
              <li><strong>Days 8–10: Jetpack Compose</strong> — Topics 7A (Fundamentals), 7B (State & Recomposition), 7C (Side Effects), 7D (Performance & Stability), 7E (UI), 7F (Navigation).</li>
              <li><strong>Days 11–12: Architecture & Dependency Injection</strong> — Topics 8A (MVI/MVVM), 8B (Clean Architecture), 9A (SOLID), 11A–11B (Hilt DI).</li>
              <li><strong>Days 13–14: Networking & Offline Storage</strong> — Topics 12A–12C (Retrofit, OkHttp, SSL Pinning) and 13A–13C (Room Database & DataStore).</li>
            </ul>

            <h4>Week 3: System Design & Platform Scenarios</h4>
            <ul>
              <li><strong>Days 15–18: System Design Case Studies</strong> — Topics 30A (Offline Catalog), 30B (Auth Flow), 30D (Chat App), 30F (Image Feed), 30G (Modular Scale).</li>
              <li><strong>Days 19–21: Debugging & Real-World Troubleshooting</strong> — Topics 33A (Crashes & ANRs), 33B (Concurrency Races), 33C (Scale & Leak Issues).</li>
            </ul>

            <h4>Week 4: Testing, Performance & Mock Interviews</h4>
            <ul>
              <li><strong>Days 22–24: Testing & Quality</strong> — Topics 20A–20C (Unit Tests, Turbine for Flow, Compose UI Tests).</li>
              <li><strong>Days 25–27: Performance, Memory & Leaks</strong> — Topics 21A (Systrace/Perfetto) and 22A (LeakCanary & Heap Dumps).</li>
              <li><strong>Days 28–30: Behavioral & Leadership</strong> — Topic 35A (STAR Method, Technical Strategy, Conflict Resolution) and mock practice.</li>
            </ul>
          </div>

          <!-- TAB 2: 60-DAY -->
          <div id="tab60" class="roadmap-content-pane">
            <p><strong>The Complete 8-Week Curriculum for Staff / Principal Engineer candidates:</strong></p>
            <ul>
              <li><strong>Phase 1 (Weeks 1–2): Language & Concurrency Mastery</strong> — Modules 1A–1J, 5A–5E, 6A–6D (19 Topics).</li>
              <li><strong>Phase 2 (Weeks 3–4): Android Platform Internals & Lifecycle</strong> — Modules 2A–2E, 3A–3D (Binder, Looper, LMK), 4A–4C, 14A–17A (Services, Receivers, Providers).</li>
              <li><strong>Phase 3 (Weeks 5–6): Modern UI, Design Patterns & Architecture</strong> — Modules 7A–7F, 8A–8B, 9A, 10A–10C, 11A–11B, 18A (Compose, Hilt, Clean Arch).</li>
              <li><strong>Phase 4 (Weeks 7–8): System Design, Enterprise Tooling & Modern Tech</strong> — Modules 19A–19B (Security), 21A–26A (Performance, Gradle, CI/CD), 30A–30G (System Design), 36A–41A (AI, KMP, a11y, Modern APIs).</li>
            </ul>
          </div>

          <!-- TAB 3: SYSTEM DESIGN -->
          <div id="tabSys" class="roadmap-content-pane">
            <h4>The 14-Day Senior System Design Checklist</h4>
            <p>Focus purely on high-level architecture rounds (Google, Meta, Uber, Amazon):</p>
            <ol>
              <li><strong>Framework: The 5-Step Mobile Design Framework</strong> (Requirements & Scope -> High-Level Architecture -> Data Layer & Cache -> Concurrency & Offline Sync -> Deep-Dives / Bottlenecks).</li>
              <li><strong>Case Study 30A: Offline-First Product Catalog</strong> — Master cache-aside, Room caching, WorkManager periodic sync, conflict resolution.</li>
              <li><strong>Case Study 30B: Login / Auth Architecture</strong> — Token refresh interceptors, biometrics, secure Keystore storage, session expiration.</li>
              <li><strong>Case Study 30D: Real-time Chat App</strong> — WebSocket connection management, SQLite message buffer, read receipts, push notification wakeup.</li>
              <li><strong>Case Study 30F: Image-Heavy Feed (Instagram clone)</strong> — Three-tier caching (L1 Memory, L2 Disk, L3 Network), prefetching, bitmap pooling.</li>
              <li><strong>Case Study 30G: Large-Scale Modular App</strong> — Core-api / Core-impl pattern, feature isolation, dynamic feature delivery.</li>
            </ol>
          </div>

          <!-- TAB 4: CODING -->
          <div id="tabCoding" class="roadmap-content-pane">
            <h4>Live Coding & DS/Algo for Android Devs</h4>
            <p>Master the top 50 coding problems commonly asked in Android technical rounds:</p>
            <ul>
              <li><strong>Module 34A: Strings Coding</strong> — Two-pointers, anagrams, palindrome partitioning, regex matchers.</li>
              <li><strong>Module 34B: Arrays & Collections</strong> — Sliding window, prefix sums, duplicate detection, Kotlin collection operations.</li>
              <li><strong>Module 34C: Math & Recursion</strong> — Backtracking, permutation generation, tree traversal, dynamic programming memoization.</li>
              <li><strong>Module 34D: Data Structures & Search</strong> — Custom LRU Cache in Kotlin, Trie for search autocomplete, binary search variants.</li>
              <li><strong>Module 34E: Android-Specific Coding</strong> — Custom Flow operators, debounce implementations, throttleFirst, SparseArray vs HashMap.</li>
            </ul>
          </div>

          <!-- TAB 5: METHOD -->
          <div id="tabMethod" class="roadmap-content-pane">
            <h4>The 5-Step Daily Study Protocol</h4>
            <p>How to study each topic in 25–35 minutes for maximum retention:</p>
            <ol>
              <li><strong>Step 1: Read the 1-Line Summary & Problem Statement (3 min)</strong> — Understand <em>why</em> this technology was created and what problem it solves.</li>
              <li><strong>Step 2: Trace the Internal Architecture / ASCII Flow (5 min)</strong> — Visualize how objects interact in memory or across IPC threads.</li>
              <li><strong>Step 3: Review the Production Code Example (7 min)</strong> — Focus on idiomatic Kotlin and real-world edge-case handling.</li>
              <li><strong>Step 4: Memorize the Traps & Anti-Patterns (5 min)</strong> — Interviewers love asking about what breaks or causes leaks in production.</li>
              <li><strong>Step 5: Test Yourself on the 10 Interview Quizzes (10 min)</strong> — Read the question, attempt the answer out loud, then toggle to reveal the solution.</li>
            </ol>
          </div>
        </div>
      </div>
    </div>

    <!-- AI & MCP PLAYBOOK MODAL -->
    <div id="aiModal" class="portal-modal-backdrop" onclick="closeModalOnBackdrop(event, 'aiModal')">
      <div class="portal-modal">
        <div class="portal-modal-header">
          <h2>🤖 AI & Model Context Protocol (MCP) for Android Developers</h2>
          <button class="btn btn-secondary btn-sm" onclick="closeAiModal()">Close ✕</button>
        </div>
        <div class="portal-modal-body">
          <p>How senior and staff Android developers leverage AI and MCP servers to multiply development speed, automate code review, and build on-device AI features in 2024–2026:</p>
          
          <h3>1. Two Pillars of AI in Android Development</h3>
          <ul>
            <li><strong>Pillar 1: On-Device AI in the App</strong> — Running local models directly on mobile silicon (NPU/GPU) using <em>Gemini Nano</em>, <em>Google AICore</em>, and <em>LiteRT (TensorFlow Lite)</em>. No network latency, 100% offline, zero cloud API cost, and private user data. (Covered in <strong>Topic 36A</strong>).</li>
            <li><strong>Pillar 2: AI-Powered Developer Tooling</strong> — Using Cursor, GitHub Copilot, Claude Code, and Model Context Protocol (MCP) to automate testing, code reviews, and architecture refactoring. (Covered in <strong>Topic 36B</strong>).</li>
          </ul>

          <h3>2. What is Model Context Protocol (MCP) & Why It Matters for Android</h3>
          <p>MCP (created by Anthropic) is an open standard that allows AI assistants (like Claude, Cursor, or IDE plugins) to securely connect to external tools, local emulators, databases, and project documentation.</p>
          
          <h4>Practical MCP Servers Every Android Developer Should Use:</h4>
          <ul>
            <li><strong>1. `adb-mcp`</strong> — Enables AI to run ADB commands directly from chat: capture device screenshots, inspect View/Compose hierarchy, dump memory (`dumpsys meminfo`), install APKs, and retrieve logcat stack traces automatically.</li>
            <li><strong>2. `android-docs-mcp`</strong> — Indexes local Android Jetpack, Compose, and Coroutines documentation so your AI generates hallucination-free code using the latest 2024–2026 APIs.</li>
            <li><strong>3. `git-pr-review-mcp`</strong> — Automated code review bot that checks your PR diffs for Compose recomposition anti-patterns, missing a11y labels, and unhandled coroutine cancellations.</li>
          </ul>

          <h3>3. Production `.cursorrules` for Android Projects</h3>
          <p>Drop this configuration into your project root (`.cursorrules`) to force your AI assistant to generate senior-grade Kotlin & Compose code:</p>
          <div class="code-snippet">
# Android Senior Engineering AI Rules
- Language: Kotlin 2.0+ (K2 compiler). Follow official Kotlin style guides.
- Architecture: Unidirectional Data Flow (MVI/MVVM) with StateFlow and immutable UiState.
- UI: Jetpack Compose only. Never use XML unless specifically requested.
- Compose Guidelines:
  * Hoist state to callers; pass stateless event lambdas.
  * Annotate domain models with @Immutable or @Stable to guarantee recomposition skipping.
  * Use rememberUpdatedState for callbacks passed into LaunchedEffect.
  * Minimum touch target: 48dp on all interactive composables. Always provide contentDescription for icons.
- Concurrency:
  * Never use GlobalScope. Always inject CoroutineDispatcher via constructor.
  * Use Turbine and StandardTestDispatcher for testing Flows and StateFlows.
- Clean Code:
  * Prefer sealed interfaces for UiState and UiEvents.
  * Catch specific exceptions (CancellationException must always be rethrown!).
          </div>

          <h3>4. High-Yield AI Prompting Templates for Android</h3>
          <ul>
            <li><strong>Refactoring XML to Compose:</strong> <em>"Convert this Android XML layout and ViewBinding Activity into idiomatic Jetpack Compose. Hoist all state into a single immutable UiState data class and expose events via sealed interface."</em></li>
            <li><strong>Writing Turbine Flow Tests:</strong> <em>"Generate a complete JUnit 5 test suite for this ViewModel using MockK, Turbine, and StandardTestDispatcher. Test success, loading, network failure, and empty states."</em></li>
            <li><strong>Performance Optimization:</strong> <em>"Analyze this Composable function for unnecessary recompositions. Identify non-stable parameters, missing derivedStateOf calls, and suggest layout optimizations."</em></li>
          </ul>
        </div>
      </div>
    </div>

    <!-- ROADMAP MODULE SECTIONS -->
    <div id="roadmapContainer">
"""

    for mod_id in sorted(modules.keys()):
        mod = modules[mod_id]
        html_content += f"""
      <div class="module-section" id="mod-sec-{mod_id}" data-mod-id="{mod_id}">
        <div class="module-section-header">
          <div class="module-section-title">
            <span class="module-badge">Module {mod_id}</span>
            <span>{mod['name']}</span>
          </div>
          <div class="quiz-count-badge">
            <span>{len(mod['topics'])} topics · {sum(x['quizzes'] for x in mod['topics'])} interview Q&As</span>
          </div>
        </div>
        <div class="topics-grid">
"""
        for t in mod['topics']:
            tier_class = f"badge-{t['tier'].lower().replace(' ', '')}"
            html_content += f"""
          <a href="{t['file']}" class="topic-card" id="card-{t['code']}" data-code="{t['code']}" data-tier="{t['tier']}" data-file="{t['file']}">
            <div class="topic-card-header">
              <span class="topic-code">{t['code']}</span>
              <span class="{tier_class}">{t['tier']}</span>
            </div>
            <div class="topic-card-body">
              <h3>{html.escape(t['clean_title'])}</h3>
              <p>{html.escape(t['desc'])}</p>
            </div>
            <div class="topic-card-footer">
              <div class="quiz-count-badge">
                <span>⚡ {t['quizzes']} Q&As</span>
              </div>
              <div class="card-action-btns">
                <button class="study-toggle-btn" onclick="toggleTopicDone('{t['code']}', event)" title="Toggle studied status">
                  <span class="check-box-display">⚪</span>
                </button>
                <button class="btn btn-secondary btn-sm" onclick="event.preventDefault(); event.stopPropagation(); openStudyReader('{t['code']}');" title="Open inside portal study reader">Reader 📖</button>
                <a href="topic_pdfs/{t['file'].replace('.html', '.pdf')}" class="btn btn-secondary btn-sm" download title="Download this topic's PDF" onclick="event.stopPropagation();" style="border-color:#38bdf8; color:#7dd3fc;">PDF 📄</a>
                <span class="open-arrow">Study →</span>
              </div>
            </div>
          </a>
"""
        html_content += """
        </div>
      </div>
"""

    html_content += f"""
      <div id="noResults">
        <h3>No matching topics found</h3>
        <p style="margin-top:8px;">Try searching for another keyword like "coroutine", "binder", "compose", or "security".</p>
      </div>
    </div>
  </main>
</div>

<script>
  const ALL_TOPICS = {modules_json};
  let currentTopicCode = ALL_TOPICS[0].code;
  let currentFilter = 'all';
  let searchQuery = '';

  const STORAGE_KEY = 'android_prep_studied_topics_v1';
  let studiedSet = new Set(JSON.parse(localStorage.getItem(STORAGE_KEY) || '[]'));

  function saveProgress() {{
    localStorage.setItem(STORAGE_KEY, JSON.stringify(Array.from(studiedSet)));
    updateProgressUI();
  }}

  function resetProgress() {{
    if (confirm("Reset all study progress checkmarks?")) {{
      studiedSet.clear();
      saveProgress();
    }}
  }}

  function updateProgressUI() {{
    const total = ALL_TOPICS.length;
    const studiedCount = studiedSet.size;
    const pct = Math.round((studiedCount / total) * 100);

    document.getElementById('progressPercent').innerText = pct + '%';
    document.getElementById('progressFraction').innerText = studiedCount + '/' + total;
    document.getElementById('progressBarFill').style.width = pct + '%';
    document.getElementById('studiedCount').innerText = studiedCount;
    document.getElementById('unstudiedCount').innerText = total - studiedCount;

    ALL_TOPICS.forEach(t => {{
      const card = document.getElementById('card-' + t.code);
      const isDone = studiedSet.has(t.code);
      if (card) {{
        card.classList.toggle('studied', isDone);
        const checkDisplay = card.querySelector('.check-box-display');
        if (checkDisplay) {{
          checkDisplay.innerText = isDone ? '🟢' : '⚪';
        }}
      }}
      const sideLink = document.getElementById('sidelink-' + t.code);
      if (sideLink) {{
        sideLink.classList.toggle('studied', isDone);
      }}
    }});

    const markBtn = document.getElementById('readerMarkStudiedBtn');
    if (markBtn) {{
      const done = studiedSet.has(currentTopicCode);
      markBtn.innerText = done ? 'Studied ✓' : 'Mark Studied';
      markBtn.classList.toggle('btn-accent2', done);
      markBtn.classList.toggle('btn-secondary', !done);
    }}
  }}

  function toggleTopicDone(code, event) {{
    if (event) {{
      event.preventDefault();
      event.stopPropagation();
    }}
    if (studiedSet.has(code)) {{
      studiedSet.delete(code);
    }} else {{
      studiedSet.add(code);
    }}
    saveProgress();
  }}

  function toggleCurrentTopicStudied() {{
    toggleTopicDone(currentTopicCode);
  }}

  function buildSidebar() {{
    const sidebarEl = document.getElementById('sidebarModulesList');
    const modulesMap = {{}};
    ALL_TOPICS.forEach(t => {{
      if (!modulesMap[t.mod_num]) {{
        modulesMap[t.mod_num] = [];
      }}
      modulesMap[t.mod_num].push(t);
    }});

    let html = '';
    for (const modNum in modulesMap) {{
      const topics = modulesMap[modNum];
      html += `
        <div class="module-group" id="side-mod-${{modNum}}">
          <div class="module-header" onclick="toggleModuleGroup('${{modNum}}')">
            <span><span class="m-num">M${{modNum}}</span> Track</span>
            <span class="arrow">▼</span>
          </div>
          <div class="module-topics-list">
      `;
      topics.forEach(t => {{
        const isDone = studiedSet.has(t.code);
        html += `
          <a href="${{t.file}}" class="sidebar-topic-link ${{isDone ? 'studied' : ''}}" id="sidelink-${{t.code}}">
            <span class="check-icon">✓</span>
            <span style="font-family:var(--font-mono); font-size:11.5px; font-weight:700; color:var(--accent);">${{t.code}}</span>
            <span style="overflow:hidden; text-overflow:ellipsis; white-space:nowrap;">${{t.clean_title}}</span>
          </a>
        `;
      }});
      html += `</div></div>`;
    }}
    sidebarEl.innerHTML = html;
  }}

  function toggleModuleGroup(modNum) {{
    const el = document.getElementById('side-mod-' + modNum);
    if (el) el.classList.toggle('collapsed');
  }}

  // Study Reader Controller
  function openStudyReader(code) {{
    const topic = ALL_TOPICS.find(t => t.code === code);
    if (!topic) return;

    currentTopicCode = code;
    const container = document.getElementById('studyReaderContainer');
    const iframe = document.getElementById('studyIframe');
    const titleEl = document.getElementById('readerTopicTitle');
    const extLink = document.getElementById('readerExternalLink');

    titleEl.innerHTML = `<span style="color:var(--accent); font-family:var(--font-mono); font-weight:700;">[${{topic.code}}]</span> ${{topic.clean_title}}`;
    extLink.href = topic.file;
    iframe.src = topic.file;

    container.classList.add('active');
    container.scrollIntoView({{ behavior: 'smooth', block: 'start' }});

    document.querySelectorAll('.sidebar-topic-link').forEach(el => el.classList.remove('active'));
    const sideLink = document.getElementById('sidelink-' + code);
    if (sideLink) sideLink.classList.add('active');

    updateProgressUI();
  }}

  function closeStudyReader() {{
    const container = document.getElementById('studyReaderContainer');
    const iframe = document.getElementById('studyIframe');
    container.classList.remove('active');
    iframe.src = 'about:blank';
  }}

  function navigateTopic(dir) {{
    const idx = ALL_TOPICS.findIndex(t => t.code === currentTopicCode);
    if (idx === -1) return;
    const nextIdx = idx + dir;
    if (nextIdx >= 0 && nextIdx < ALL_TOPICS.length) {{
      openStudyReader(ALL_TOPICS[nextIdx].code);
    }}
  }}

  function setFilter(filter) {{
    currentFilter = filter;
    document.querySelectorAll('.filter-pills .pill').forEach(p => {{
      p.classList.toggle('active', p.getAttribute('data-filter') === filter);
    }});
    applyFilters();
  }}


  // Modal controllers
  function openRoadmapModal() {{
    document.getElementById('roadmapModal').classList.add('active');
  }}
  function closeRoadmapModal() {{
    document.getElementById('roadmapModal').classList.remove('active');
  }}
  function openAiModal() {{
    document.getElementById('aiModal').classList.add('active');
  }}
  function closeAiModal() {{
    document.getElementById('aiModal').classList.remove('active');
  }}
  function closeModalOnBackdrop(e, modalId) {{
    if (e.target.id === modalId) {{
      document.getElementById(modalId).classList.remove('active');
    }}
  }}

  function switchRoadmapTab(tabId) {{
    document.querySelectorAll('.roadmap-tab-btn').forEach(btn => btn.classList.remove('active'));
    document.querySelectorAll('.roadmap-content-pane').forEach(pane => pane.classList.remove('active'));
    
    event.target.classList.add('active');
    document.getElementById(tabId).classList.add('active');
  }}

  // Enhanced Filter Logic

  function handleSearch() {{
    searchQuery = document.getElementById('searchInput').value.toLowerCase().trim();
    applyFilters();
  }}

  function applyFilters() {{
    let visibleCount = 0;
    ALL_TOPICS.forEach(t => {{
      const card = document.getElementById('card-' + t.code);
      const isStudied = studiedSet.has(t.code);
      
      let matchesFilter = true;
      if (currentFilter === 'Tier 1' || currentFilter === 'Tier 2' || currentFilter === 'Tier 3') {{
        matchesFilter = (t.tier === currentFilter);
      }} else if (currentFilter === 'studied') {{
        matchesFilter = isStudied;
      }} else if (currentFilter === 'unstudied') {{
        matchesFilter = !isStudied;
      }} else if (currentFilter === 'sysdesign') {{
        matchesFilter = (t.mod_num === 30 || t.mod_num === 8);
      }} else if (currentFilter === 'coding') {{
        matchesFilter = (t.mod_num === 34);
      }} else if (currentFilter === 'aimodern') {{
        matchesFilter = (t.mod_num >= 36);
      }}

      let matchesSearch = true;
      if (searchQuery) {{
        const fullHaystack = (t.code + ' ' + t.clean_title + ' ' + t.desc + ' ' + t.tier).toLowerCase();
        matchesSearch = fullHaystack.includes(searchQuery);
      }}

      const show = matchesFilter && matchesSearch;
      if (card) {{
        card.style.display = show ? 'flex' : 'none';
        if (show) visibleCount++;
      }}
    }});

    const modSections = document.querySelectorAll('.module-section');
    modSections.forEach(sec => {{
      const visibleCards = sec.querySelectorAll('.topic-card:not([style*="display: none"])');
      sec.style.display = visibleCards.length > 0 ? 'block' : 'none';
    }});

    document.getElementById('noResults').style.display = visibleCount === 0 ? 'block' : 'none';
  }}

  document.addEventListener('keydown', (e) => {{
    if (document.getElementById('studyReaderContainer').classList.contains('active')) {{
      if (e.key === 'ArrowLeft' || e.key === '[') {{
        navigateTopic(-1);
      }} else if (e.key === 'ArrowRight' || e.key === ']') {{
        navigateTopic(1);
      }} else if (e.key === 'Escape') {{
        closeStudyReader();
      }} else if (e.key.toLowerCase() === 'c') {{
        toggleCurrentTopicStudied();
      }}
    }}
  }});

  window.addEventListener('DOMContentLoaded', () => {{
    buildSidebar();
    updateProgressUI();
  }});
</script>

</body>
</html>
"""
    return html_content

def extract_main_content(filepath, code):
    with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
        raw = f.read()

    main_m = re.search(r'<main[^>]*>(.*?)</main>', raw, re.S)
    if not main_m:
        return f"<div class='topic-error'>Failed to extract content for {code}</div>"
        
    content = main_m.group(1)

    # Namespace IDs to avoid collision
    content = re.sub(r'\bid=\"s([1-9])\"', rf'id=\"{code}_s\1\"', content)
    content = re.sub(r'\bid=\"(overview|how|when|prod|alt|pitfalls|interview|revision|quiz)\"', rf'id=\"{code}_\1\"', content)
    content = re.sub(r'onclick=[\"\'](?:showSection|show)\([^\)]+\)[\"\']', '', content)
    
    return content

def generate_combined_html(topics):
    toc_html = ""
    modules_map = {}
    for t in topics:
        if t['mod_num'] not in modules_map:
            modules_map[t['mod_num']] = []
        modules_map[t['mod_num']].append(t)
        
    for mod_num in sorted(modules_map.keys()):
        tlist = modules_map[mod_num]
        mod_name = MODULE_NAMES.get(mod_num, f"Module {mod_num}")
        toc_html += f"""
        <div class="toc-module-group">
          <div class="toc-module-header">
            <span class="toc-mod-badge">M{mod_num}</span>
            <span class="toc-mod-name">{mod_name}</span>
          </div>
          <ul class="toc-topic-list">
        """
        for t in tlist:
            toc_html += f"""
            <li>
              <a href="#{t['code']}" class="toc-link" onclick="highlightTocLink(this)">
                <span class="toc-code">{t['code']}</span>
                <span class="toc-text">{t['clean_title']}</span>
              </a>
            </li>
            """
        toc_html += "</ul></div>"

    chapters_html = ""
    for i, t in enumerate(topics):
        next_topic = topics[i+1] if i + 1 < len(topics) else None
        prev_topic = topics[i-1] if i > 0 else None
        
        main_content = extract_main_content(t['file'], t['code'])
        
        footer_html = f"""
        <div class="chapter-footer">
          <div class="footer-nav-left">
            {"<a href='#" + prev_topic['code'] + "' class='footer-nav-btn'>← Previous: " + prev_topic['code'] + " " + prev_topic['clean_title'] + "</a>" if prev_topic else ""}
          </div>
          <div class="footer-nav-center">
            <a href="#top" class="footer-nav-btn btn-top">↑ Top of Document</a>
            <a href="{t['file']}" target="_blank" class="footer-nav-btn" style="margin-left:8px;">Open Single Page ↗</a>
          </div>
          <div class="footer-nav-right">
            {"<a href='#" + next_topic['code'] + "' class='footer-nav-btn next-btn'>Next: " + next_topic['code'] + " " + next_topic['clean_title'] + " →</a>" if next_topic else "<span class='footer-end'>🎉 End of Curriculum</span>"}
          </div>
        </div>
        """
        
        chapters_html += f"""
        <article class="topic-chapter" id="{t['code']}" data-code="{t['code']}">
          {main_content}
          {footer_html}
        </article>
        """

    total_topics = len(topics)
    total_quizzes = sum(t['quizzes'] for t in topics)

    combined_html = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8"/>
<meta name="viewport" content="width=device-width, initial-scale=1.0"/>
<title>Android Senior & Staff Interview Preparation — Complete Master Compendium</title>
<style>
  :root {{
    --bg: #0f1117;
    --surface: #1a1d27;
    --surface2: #222535;
    --border: #2e3149;
    --text: #e2e4f0;
    --muted: #8b90b8;
    --accent: #7c6af7;
    --accent2: #56cfb2;
    --green: #3ecf8e;
    --red: #ff6b6b;
    --yellow: #f5c842;
    --orange: #ff9f43;
    --warn: #f0a04b;
    --danger: #f06b6b;
    --good: #56cfb2;
    --code-bg: #13151f;
    --radius: 10px;
    --toc-width: 320px;
  }}

  * {{ box-sizing: border-box; margin: 0; padding: 0; }}
  html {{ scroll-behavior: smooth; }}

  body {{
    font-family: -apple-system, "Segoe UI", system-ui, sans-serif;
    background: var(--bg);
    color: var(--text);
    font-size: 15px;
    line-height: 1.7;
    display: flex;
    flex-direction: column;
    min-height: 100vh;
  }}

  /* TOP STICKY BAR */
  .master-top-bar {{
    position: sticky;
    top: 0;
    z-index: 1000;
    background: rgba(20, 23, 36, 0.96);
    backdrop-filter: blur(12px);
    border-bottom: 1px solid var(--border);
    padding: 10px 24px;
    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: 16px;
  }}

  .reading-progress-bar {{
    position: absolute;
    bottom: 0;
    left: 0;
    height: 3px;
    background: linear-gradient(90deg, #7c6af7, #3ecf8e);
    width: 0%;
    transition: width 0.1s;
  }}

  .top-bar-left {{
    display: flex;
    align-items: center;
    gap: 14px;
  }}

  .brand-badge {{
    font-weight: 800;
    font-size: 14px;
    color: var(--text);
    display: flex;
    align-items: center;
    gap: 8px;
    text-decoration: none;
  }}

  .brand-badge span.pill {{
    background: linear-gradient(135deg, #7c6af7, #4f9eff);
    color: #fff;
    font-size: 11px;
    padding: 2px 8px;
    border-radius: 4px;
  }}

  .top-bar-right {{
    display: flex;
    align-items: center;
    gap: 8px;
    flex-wrap: wrap;
  }}

  .btn-bar {{
    display: inline-flex;
    align-items: center;
    gap: 6px;
    background: var(--surface2);
    color: var(--text);
    border: 1px solid var(--border);
    padding: 6px 12px;
    border-radius: 6px;
    font-size: 12.5px;
    font-weight: 600;
    cursor: pointer;
    text-decoration: none;
    transition: all 0.15s;
  }}
  .btn-bar:hover {{
    background: var(--accent);
    color: #fff;
    border-color: var(--accent);
  }}

  /* COMPENDIUM CONTAINER */
  .compendium-layout {{
    display: flex;
    flex: 1;
    position: relative;
  }}

  /* FLOATING / STICKY TABLE OF CONTENTS */
  aside.master-toc {{
    width: var(--toc-width);
    min-width: var(--toc-width);
    height: calc(100vh - 54px);
    position: sticky;
    top: 54px;
    overflow-y: auto;
    background: var(--surface);
    border-right: 1px solid var(--border);
    padding: 20px 14px 40px;
    display: flex;
    flex-direction: column;
    gap: 14px;
    flex-shrink: 0;
  }}

  .toc-header {{
    font-size: 11px;
    text-transform: uppercase;
    letter-spacing: 0.1em;
    color: var(--muted);
    font-weight: 700;
    padding: 0 8px 10px;
    border-bottom: 1px solid var(--border);
    display: flex;
    justify-content: space-between;
  }}

  .toc-module-group {{
    margin-bottom: 6px;
  }}

  .toc-module-header {{
    display: flex;
    align-items: center;
    gap: 8px;
    padding: 6px 8px;
    font-size: 12px;
    font-weight: 700;
    color: var(--text);
    border-radius: 4px;
    background: rgba(255, 255, 255, 0.02);
  }}

  .toc-mod-badge {{
    background: rgba(124, 106, 247, 0.15);
    color: var(--accent);
    padding: 1px 6px;
    border-radius: 3px;
    font-size: 10px;
  }}

  .toc-topic-list {{
    list-style: none;
    padding-left: 6px;
    margin-top: 4px;
    display: flex;
    flex-direction: column;
    gap: 2px;
  }}

  .toc-link {{
    display: flex;
    align-items: center;
    gap: 8px;
    padding: 6px 8px;
    border-radius: 5px;
    color: var(--muted);
    font-size: 12px;
    text-decoration: none;
    transition: all 0.15s;
  }}
  .toc-link:hover, .toc-link.active {{
    background: rgba(124, 106, 247, 0.15);
    color: var(--accent);
  }}
  .toc-link .toc-code {{
    font-family: monospace;
    font-weight: 700;
    min-width: 26px;
    color: var(--accent2);
    font-size: 11px;
  }}
  .toc-link .toc-text {{
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
  }}

  /* MAIN CONTINUOUS STREAM */
  main.compendium-stream {{
    flex: 1;
    min-width: 0;
    padding: 0;
    background: var(--bg);
  }}

  /* CHAPTER STYLING */
  .topic-chapter {{
    border-bottom: 8px solid #08090e;
    padding-bottom: 60px;
    position: relative;
  }}

  .topic-chapter .hero {{
    background: linear-gradient(135deg, #171a27 0%, #15102a 100%);
    border-bottom: 1px solid var(--border);
    padding: 48px 56px 40px;
  }}

  .topic-chapter .hero h1 {{
    font-size: 30px;
    font-weight: 800;
    line-height: 1.3;
    margin-bottom: 12px;
    color: var(--text);
  }}
  .topic-chapter .hero h1 span {{ color: var(--accent); }}

  /* OVERRIDE: FORCE ALL SECTIONS TO SHOW IN CONTINUOUS MODE */
  .topic-chapter .section {{
    display: block !important;
    opacity: 1 !important;
    transform: none !important;
    padding: 36px 56px;
    max-width: 960px;
    border-bottom: 1px dashed rgba(46, 49, 73, 0.4);
  }}

  .topic-chapter section {{
    margin-bottom: 40px;
    padding: 0 56px;
    max-width: 960px;
  }}

  .topic-chapter .nav-buttons {{
    display: none !important;
  }}

  /* CHAPTER FOOTER */
  .chapter-footer {{
    margin: 40px 56px 0;
    padding-top: 24px;
    border-top: 1px solid var(--border);
    display: flex;
    justify-content: space-between;
    align-items: center;
    gap: 16px;
    flex-wrap: wrap;
    max-width: 960px;
  }}

  .footer-nav-btn {{
    display: inline-flex;
    align-items: center;
    gap: 6px;
    background: var(--surface);
    color: var(--muted);
    border: 1px solid var(--border);
    padding: 8px 14px;
    border-radius: 6px;
    font-size: 13px;
    font-weight: 600;
    text-decoration: none;
    transition: all 0.15s;
  }}
  .footer-nav-btn:hover {{
    background: var(--surface2);
    color: var(--text);
    border-color: var(--accent);
  }}
  .footer-nav-btn.next-btn {{
    background: rgba(124, 106, 247, 0.12);
    color: var(--accent);
    border-color: rgba(124, 106, 247, 0.3);
  }}
  .footer-nav-btn.next-btn:hover {{
    background: var(--accent);
    color: #fff;
  }}

  .section-title {{
    font-size: 20px;
    font-weight: 800;
    margin-bottom: 24px;
    padding-bottom: 14px;
    border-bottom: 1px solid var(--border);
    display: flex;
    align-items: center;
    gap: 12px;
  }}
  .section-icon {{
    width: 32px; height: 32px;
    border-radius: 8px;
    display: flex; align-items: center; justify-content: center;
    font-size: 16px;
    background: rgba(124,106,247,0.15);
  }}

  h2 {{ font-size: 19px; font-weight: 700; color: var(--accent2); margin: 28px 0 12px; }}
  h3 {{ font-size: 15px; font-weight: 700; color: var(--accent2); margin: 24px 0 10px; }}
  h4 {{ font-size: 14px; font-weight: 600; color: var(--yellow); margin: 20px 0 8px; }}
  p {{ color: var(--muted); margin-bottom: 14px; line-height: 1.7; }}
  p strong, li strong, td strong {{ color: var(--text); }}
  li {{ color: var(--muted); margin-bottom: 6px; }}
  ul, ol {{ padding-left: 20px; margin-bottom: 14px; }}

  /* CODE & DIAGRAMS */
  pre {{
    background: var(--code-bg);
    border: 1px solid var(--border);
    border-radius: var(--radius);
    padding: 18px 20px;
    overflow-x: auto;
    margin: 14px 0 20px;
    font-size: 13px;
    line-height: 1.6;
    color: #c9d1d9;
  }}
  code {{
    font-family: "JetBrains Mono", "Fira Code", monospace;
    font-size: 13px;
  }}
  p code, li code, td code {{
    background: rgba(124,106,247,0.12);
    color: #b8b0ff;
    padding: 2px 6px;
    border-radius: 4px;
    font-size: 12.5px;
  }}
  .kw {{ color: #c084fc; }}
  .fn {{ color: #7dd3fc; }}
  .str {{ color: #86efac; }}
  .cm {{ color: #6b7280; font-style: italic; }}
  .cl, .type {{ color: #fbbf24; }}
  .nu, .num {{ color: #f9a8d4; }}
  .an, .ann {{ color: #fb923c; }}

  .ascii, .ascii-box {{
    font-family: monospace;
    background: #141724;
    border: 1px solid var(--border);
    border-radius: 8px;
    padding: 16px;
    font-size: 12.5px;
    color: #abb2bf;
    white-space: pre;
    overflow-x: auto;
    margin: 14px 0 20px;
  }}

  /* TABLES */
  .table-wrap {{ overflow-x: auto; margin: 14px 0 20px; }}
  table {{ width: 100%; border-collapse: collapse; font-size: 13.5px; margin: 14px 0; }}
  th {{
    background: var(--surface2);
    color: var(--text);
    font-weight: 700;
    padding: 10px 14px;
    text-align: left;
    border: 1px solid var(--border);
  }}
  td {{ padding: 10px 14px; border: 1px solid var(--border); color: var(--muted); vertical-align: top; }}
  tr:nth-child(even) td {{ background: rgba(255,255,255,0.015); }}
  tr:hover td {{ background: rgba(124, 106, 247, 0.05); }}

  /* CALLOUTS & BOXES */
  .callout, .box {{
    border-radius: 8px;
    padding: 14px 18px;
    margin: 14px 0;
    font-size: 14px;
    border-left: 4px solid;
  }}
  .callout-green, .box.good {{ border-color: var(--green); background: rgba(62,207,142,0.08); }}
  .callout-red, .box.danger {{ border-color: var(--red); background: rgba(255,107,107,0.08); }}
  .callout-yellow, .box.warn {{ border-color: var(--yellow); background: rgba(245,200,66,0.08); }}
  .callout-blue, .box.info {{ border-color: var(--accent2); background: rgba(86,207,178,0.08); }}
  .callout-purple {{ border-color: var(--accent); background: rgba(124,106,247,0.08); }}
  .callout-label {{ font-size: 11px; font-weight: 800; letter-spacing: 0.08em; text-transform: uppercase; margin-bottom: 6px; }}
  .callout-green .callout-label {{ color: var(--green); }}
  .callout-red .callout-label {{ color: var(--red); }}
  .callout-yellow .callout-label {{ color: var(--yellow); }}
  .callout-blue .callout-label {{ color: var(--accent2); }}
  .callout-purple .callout-label {{ color: var(--accent); }}

  .grid2 {{ display: grid; grid-template-columns: 1fr 1fr; gap: 16px; margin: 14px 0; }}
  @media(max-width: 768px) {{ .grid2 {{ grid-template-columns: 1fr; }} }}
  .card {{ background: var(--surface); border: 1px solid var(--border); border-radius: 8px; padding: 16px; }}
  .card h4 {{ margin-top: 0; color: var(--accent2); }}

  /* BADGES */
  .badge {{ display: inline-flex; align-items: center; gap: 6px; font-size: 12px; font-weight: 600; padding: 4px 12px; border-radius: 6px; }}
  .badge-tier1, .badge.t1 {{ background: rgba(62,207,142,0.12); color: var(--green); border: 1px solid rgba(62,207,142,0.25); }}
  .badge-tier2, .badge.t2 {{ background: rgba(245,200,66,0.12); color: var(--yellow); border: 1px solid rgba(245,200,66,0.25); }}
  .badge-tier3, .badge.t3 {{ background: rgba(79,158,255,0.12); color: var(--blue); border: 1px solid rgba(79,158,255,0.25); }}
  .badge-id {{ background: rgba(124,106,247,0.12); color: var(--accent); border: 1px solid rgba(124,106,247,0.25); }}
  .hero-tag {{ display: inline-flex; align-items: center; gap: 8px; background: rgba(124,106,247,0.12); border: 1px solid rgba(124,106,247,0.3); color: var(--accent); font-size: 12px; font-weight: 700; padding: 4px 12px; border-radius: 20px; margin-bottom: 16px; }}

  /* QUIZ CARDS & DETAILS */
  .quiz-card {{
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: var(--radius);
    margin-bottom: 14px;
    overflow: hidden;
  }}
  .quiz-q {{
    padding: 16px 20px;
    cursor: pointer;
    display: flex;
    justify-content: space-between;
    align-items: center;
    gap: 12px;
    user-select: none;
    font-weight: 600;
  }}
  .quiz-q:hover {{ background: var(--surface2); }}
  .quiz-meta {{ display: flex; align-items: center; gap: 8px; flex-shrink: 0; }}
  .toggle-icon {{ font-size: 12px; color: var(--muted); transition: transform 0.2s; }}
  .toggle-icon.open {{ transform: rotate(180deg); }}
  .quiz-a {{
    display: none;
    padding: 18px 20px;
    border-top: 1px solid var(--border);
    background: #12141e;
    font-size: 14px;
    line-height: 1.7;
  }}
  .quiz-a.open {{ display: block; }}

  details {{
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: 8px;
    margin: 10px 0;
  }}
  details summary {{
    padding: 14px 18px;
    cursor: pointer;
    font-weight: 600;
    color: var(--text);
    list-style: none;
    display: flex;
    justify-content: space-between;
  }}
  details summary::after {{ content: '▶'; font-size: 11px; color: var(--muted); }}
  details[open] summary::after {{ content: '▼'; }}
  details .ans {{
    padding: 16px 18px;
    border-top: 1px solid var(--border);
    background: #12141e;
    font-size: 14px;
  }}

  .diff-badge {{ font-size: 11px; font-weight: 700; padding: 2px 7px; border-radius: 4px; }}
  .diff-easy, .q-basic {{ background: rgba(62,207,142,0.2); color: var(--green); }}
  .diff-mid, .q-mid {{ background: rgba(245,200,66,0.2); color: var(--yellow); }}
  .diff-hard, .q-senior {{ background: rgba(255,107,107,0.2); color: var(--red); }}
  .tag-scenario {{ background: rgba(79,158,255,0.2); color: var(--blue); font-size: 11px; padding: 2px 7px; border-radius: 4px; }}

  @media(max-width: 1024px) {{
    aside.master-toc {{ display: none; }}
    .topic-chapter .hero, .topic-chapter .section, .topic-chapter section {{ padding-left: 24px; padding-right: 24px; }}
  }}

  @media print {{
    body {{
      background: #ffffff !important;
      color: #111827 !important;
      font-size: 12pt !important;
      line-height: 1.5 !important;
    }}

    .master-top-bar, aside.master-toc, .chapter-footer, .btn-bar, .hero-tag {{
      display: none !important;
    }}

    .compendium-layout {{ display: block !important; }}
    main.compendium-stream {{ background: #ffffff !important; }}

    .topic-chapter {{
      page-break-before: always !important;
      break-before: page !important;
      border-bottom: none !important;
      padding-bottom: 30pt !important;
    }}

    .topic-chapter .hero {{
      background: #f8fafc !important;
      border: 1px solid #e2e8f0 !important;
      border-radius: 8px !important;
      padding: 20pt !important;
      margin-bottom: 20pt !important;
    }}

    .topic-chapter .hero h1 {{
      color: #0f172a !important;
      font-size: 22pt !important;
    }}

    .topic-chapter .section, .topic-chapter section {{
      padding: 0 !important;
      max-width: 100% !important;
      border-bottom: none !important;
      margin-bottom: 20pt !important;
    }}

    .quiz-a {{
      display: block !important;
      background: #f8fafc !important;
      color: #1e293b !important;
      border: 1px solid #e2e8f0 !important;
    }}

    details {{
      display: block !important;
      border: 1px solid #e2e8f0 !important;
    }}
    details .ans {{
      display: block !important;
      background: #f8fafc !important;
      color: #1e293b !important;
    }}

    pre, .ascii, .ascii-box {{
      background: #f1f5f9 !important;
      color: #0f172a !important;
      border: 1px solid #cbd5e1 !important;
      page-break-inside: avoid !important;
      break-inside: avoid !important;
    }}

    table, .card, .callout, .box {{
      page-break-inside: avoid !important;
      break-inside: avoid !important;
    }}

    th {{ background: #e2e8f0 !important; color: #0f172a !important; }}
    td {{ color: #334155 !important; border-color: #cbd5e1 !important; }}
    p, li {{ color: #334155 !important; }}
  }}
</style>
</head>
<body id="top">

<div class="master-top-bar">
  <div class="top-bar-left">
    <a href="index.html" class="brand-badge">
      <span>← Return to Portal</span>
      <span class="pill">Hub</span>
    </a>
    <span style="color:var(--muted); font-size:12.5px;">| Complete Android Handbook ({total_topics} Topics · {total_quizzes} Quizzes)</span>
  </div>
  <div class="top-bar-right">
    <button class="btn-bar" onclick="expandAllQuizzes()">Expand All Q&As</button>
    <button class="btn-bar" onclick="collapseAllQuizzes()">Collapse Q&As</button>
    <button class="btn-bar" style="background:var(--accent); color:#fff; border-color:var(--accent);" onclick="printHandbook()">🖨️ Print / Save PDF</button>
  </div>
  <div class="reading-progress-bar" id="readingProgress"></div>
</div>

<div class="compendium-layout">
  <aside class="master-toc" id="masterToc">
    <div class="toc-header">
      <span>Table of Contents</span>
      <span>{total_topics} Chapters</span>
    </div>
    {toc_html}
  </aside>

  <main class="compendium-stream">
    {chapters_html}
  </main>
</div>

<script>
  function toggleQuiz(el) {{
    const a = el.nextElementSibling;
    const ic = el.querySelector('.toggle-icon');
    const isOpen = a.classList.contains('open');
    a.classList.toggle('open', !isOpen);
    if (ic) ic.classList.toggle('open', !isOpen);
  }}
  const tq = toggleQuiz;
  const toggleQ = toggleQuiz;

  document.addEventListener('click', (e) => {{
    const q = e.target.closest('.quiz-q');
    if (q && !q.getAttribute('onclick')) {{
      toggleQuiz(q);
    }}
  }});

  function expandAllQuizzes() {{
    document.querySelectorAll('.quiz-a').forEach(a => a.classList.add('open'));
    document.querySelectorAll('.toggle-icon').forEach(ic => ic.classList.add('open'));
    document.querySelectorAll('details').forEach(d => d.open = true);
  }}

  function collapseAllQuizzes() {{
    document.querySelectorAll('.quiz-a').forEach(a => a.classList.remove('open'));
    document.querySelectorAll('.toggle-icon').forEach(ic => ic.classList.remove('open'));
    document.querySelectorAll('details').forEach(d => d.open = false);
  }}

  function printHandbook() {{
    expandAllQuizzes();
    setTimeout(() => {{
      window.print();
    }}, 200);
  }}

  function highlightTocLink(linkEl) {{
    document.querySelectorAll('.toc-link').forEach(l => l.classList.remove('active'));
    linkEl.classList.add('active');
  }}

  window.addEventListener('scroll', () => {{
    const winScroll = document.documentElement.scrollTop || document.body.scrollTop;
    const height = document.documentElement.scrollHeight - document.documentElement.clientHeight;
    const scrolled = (winScroll / height) * 100;
    document.getElementById('readingProgress').style.width = scrolled + '%';

    const chapters = document.querySelectorAll('.topic-chapter');
    let currentId = '';
    chapters.forEach(ch => {{
      const rect = ch.getBoundingClientRect();
      if (rect.top <= 140 && rect.bottom >= 140) {{
        currentId = ch.getAttribute('data-code');
      }}
    }});
    if (currentId) {{
      document.querySelectorAll('.toc-link').forEach(l => {{
        const href = l.getAttribute('href');
        l.classList.toggle('active', href === '#' + currentId);
      }});
    }}
  }});

  if (window.location.hash === '#print') {{
    window.addEventListener('DOMContentLoaded', () => {{
      printHandbook();
    }});
  }}
</script>

</body>
</html>
"""
    return combined_html

def main():
    print("=== Scanning Android Interview Topics ===")
    topics = scan_topics()
    print(f"Found {len(topics)} topics.")
    
    with open('topics_manifest.json', 'w', encoding='utf-8') as f:
        json.dump(topics, f, indent=2)
    print("Updated topics_manifest.json")
    
    print("Generating index.html (Master Portal & Reader)...")
    index_content = generate_index_html(topics)
    with open('index.html', 'w', encoding='utf-8') as f:
        f.write(index_content)
    print(f"Generated index.html ({len(index_content)} bytes)")
    
    print("Generating all_topics_combined.html (Concatenated Compendium)...")
    combined_content = generate_combined_html(topics)
    with open('all_topics_combined.html', 'w', encoding='utf-8') as f:
        f.write(combined_content)
    print(f"Generated all_topics_combined.html ({len(combined_content)} bytes)")
    
    print("\nAll tasks built successfully!")

if __name__ == '__main__':
    main()
