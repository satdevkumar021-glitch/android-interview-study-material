#!/usr/bin/env python3
"""
fix_sidebar_fixed.py
====================
Permanently fixes the sidebar scroll bug across all 105 topic HTML files.

ROOT CAUSE:
  - Some files had `body { display: flex }` with `nav { position: sticky }`
  - Some had `.sidebar { position: sticky }` inside a height-constrained layout
  - `position: sticky` breaks when any ancestor has overflow constraints
  - Multiple conflicting CSS blocks fought each other

THE FIX (applied once, permanently, to every topic HTML file):
  1. Replace ALL sidebar CSS rules with a single clean `position: fixed` block
  2. Ensure `.main` / `main` has `margin-left: 260px` to clear the fixed sidebar
  3. Remove `display: flex` from body (fixed sidebar is out of flow, no flex needed)
  4. Remove all conflicting `position: sticky` / `height: 100%` body/html rules
  5. Inject a clean <style> block at the end of <head> so it always wins specificity
"""

import os, re, sys

WORKSPACE = os.path.dirname(os.path.abspath(__file__))

# The definitive sidebar CSS injected at the END of <head> — highest cascade priority
FIXED_SIDEBAR_STYLE = """
  <!-- ═══════════════════════════════════════════════════════════════
       FIXED SIDEBAR — injected by fix_sidebar_fixed.py
       Sidebar is locked to viewport. Only content scrolls.
  ═══════════════════════════════════════════════════════════════ -->
  <style id="aip-fixed-sidebar">
    /* 1. Body: natural document scroll — no flex, no height constraint */
    html { min-height: 100%; }
    body {
      display: block !important;
      height: auto !important;
      min-height: 100vh;
      overflow-y: auto !important;
      overflow-x: hidden;
    }

    /* 2. Layout wrapper: simple block container */
    .layout { display: block !important; min-height: 100vh; }

    /* 3. SIDEBAR — fixed to viewport, never scrolls with page */
    .sidebar,
    nav.sidebar {
      position: fixed !important;
      left: 0 !important;
      top: 0 !important;            /* shared.js overrides to 52px after topbar injects */
      width: 260px !important;
      min-width: 260px !important;
      height: 100vh !important;     /* shared.js overrides to calc(100vh - 52px) */
      overflow-y: auto !important;
      overflow-x: hidden !important;
      z-index: 200 !important;
      background: var(--surface, #1a1d27) !important;
      border-right: 1px solid var(--border, #2e3148) !important;
    }

    /* 4. Main content: pushed right to clear the 260px fixed sidebar */
    .main,
    main#mainScroll,
    main {
      display: block !important;
      margin-left: 260px !important;   /* shared.js keeps this in sync */
      width: auto !important;
      max-width: none !important;
      overflow: visible !important;
      height: auto !important;
    }

    /* 5. Active sidebar highlight */
    .nav-item.aip-nav-active,
    nav a.aip-nav-active {
      background: rgba(124,106,247,0.18) !important;
      color: #7c6af7 !important;
      border-left-color: #7c6af7 !important;
    }
    .nav-item.aip-nav-active .nav-num {
      background: rgba(124,106,247,0.28) !important;
      color: #7c6af7 !important;
    }

    /* 6. Mobile: sidebar becomes off-canvas drawer */
    @media (max-width: 768px) {
      .sidebar, nav.sidebar {
        left: -280px !important;
        top: 0 !important;
        height: 100vh !important;
        z-index: 9000 !important;
        transition: left 0.28s cubic-bezier(0.4,0,0.2,1) !important;
        box-shadow: 4px 0 32px rgba(0,0,0,0.7) !important;
      }
      .sidebar.aip-open, nav.sidebar.aip-open {
        left: 0 !important;
      }
      .main, main#mainScroll, main {
        margin-left: 0 !important;
      }
    }
  </style>"""


def fix_file(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        html = f.read()

    original = html

    # ── Step 1: Remove the old "LAYOUT FIX" block entirely ──────────────────
    # This block contained the conflicting sticky/height-constrained rules
    html = re.sub(
        r'/\*\s*[═=]{3,}.*?LAYOUT FIX.*?[═=]{3,}\s*\*/'
        r'.*?'
        r'(?=\s*/\*\s*[═=]{3,}|\s*</style>|\s*</head>)',
        '',
        html,
        flags=re.DOTALL
    )

    # ── Step 2: Remove any remaining conflicting body/html height rules ──────
    # Remove: html, body { height: 100%; }  or  html { min-height: 100%; }
    html = re.sub(r'\s*html,\s*body\s*\{\s*height:\s*100%[^}]*\}\s*', '\n', html)
    html = re.sub(r'\s*html\s*\{\s*min-height:\s*100%[^}]*\}\s*', '\n', html)
    # Remove: body { overflow-y: scroll; }
    html = re.sub(r'\s*body\s*\{\s*overflow-y:\s*scroll[^}]*\}\s*', '\n', html)

    # ── Step 3: Fix body { display: flex } → display: block ─────────────────
    # Only fix the top-level body rule that has display:flex (Scrollable format)
    html = re.sub(
        r'(body\s*\{[^}]*?)display\s*:\s*flex([^}]*\})',
        r'\1display:block\2',
        html
    )

    # ── Step 4: Fix nav { position: sticky } → position: fixed ──────────────
    # Catch bare `nav { ... position:sticky ... }` rules in Scrollable format
    html = re.sub(
        r'(nav\s*\{[^}]*?)position\s*:\s*sticky([^}]*\})',
        r'\1position:fixed\2',
        html
    )

    # ── Step 5: Remove any duplicate/old sidebar fixed-style block we injected before
    html = re.sub(
        r'\s*<!-- ═+\s*FIXED SIDEBAR[^>]*>.*?</style>\s*',
        '',
        html,
        flags=re.DOTALL
    )

    # ── Step 6: Inject our definitive style block just before </head> ────────
    if '</head>' in html:
        html = html.replace('</head>', FIXED_SIDEBAR_STYLE + '\n</head>', 1)
    else:
        # fallback: inject before <body>
        html = html.replace('<body', FIXED_SIDEBAR_STYLE + '\n<body', 1)

    if html != original:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(html)
        return True
    return False


def main():
    topic_files = [
        f for f in os.listdir(WORKSPACE)
        if f.endswith('.html')
        and f not in ('index.html', 'all_topics_combined.html',
                      'android_interview_compact_guide.html')
    ]
    topic_files.sort()

    fixed = 0
    skipped = 0
    for fname in topic_files:
        path = os.path.join(WORKSPACE, fname)
        if fix_file(path):
            fixed += 1
            print(f'  ✅ Fixed: {fname}')
        else:
            skipped += 1
            print(f'  — Skipped (no change): {fname}')

    print(f'\nDone. {fixed} files fixed, {skipped} unchanged.')


if __name__ == '__main__':
    main()
