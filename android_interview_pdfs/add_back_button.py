#!/usr/bin/env python3
"""
add_back_button.py
Add a visible "← Dashboard" back link at the top of every topic page's sidebar.
Also adds a small "← Back to Dashboard" link in the hero section.
"""
import os, re, glob

TOPIC_FILES = sorted(
    f for f in glob.glob('*.html')
    if re.match(r'^\d+[A-Z]_.*\.html$', f)
)

# CSS for the back button - added once per page
BACK_BTN_CSS = '''  /* ── Dashboard back link ── */
  .sidebar-back {
    display: flex;
    align-items: center;
    gap: 8px;
    padding: 8px 12px 12px;
    margin-bottom: 8px;
    border-bottom: 1px solid var(--border, #2e3149);
    text-decoration: none;
    color: var(--muted, #8b90b8);
    font-size: 12px;
    font-weight: 600;
    transition: color .15s;
    letter-spacing: 0.02em;
  }
  .sidebar-back:hover { color: var(--accent, #7c6af7); }
  .sidebar-back svg { width:14px; height:14px; flex-shrink:0; fill:currentColor; }
  .hero-back {
    display: inline-flex;
    align-items: center;
    gap: 6px;
    font-size: 12px;
    color: var(--muted, #8b90b8);
    text-decoration: none;
    margin-bottom: 14px;
    transition: color .15s;
    font-weight: 500;
  }
  .hero-back:hover { color: var(--accent, #7c6af7); }
  .hero-back svg { width:12px; height:12px; fill:currentColor; }
'''

BACK_LINK_HTML = '''  <a class="sidebar-back" href="index.html">
    <svg viewBox="0 0 24 24"><path d="M20 11H7.83l5.59-5.59L12 4l-8 8 8 8 1.41-1.41L7.83 13H20v-2z"/></svg>
    Dashboard
  </a>
'''

HERO_BACK_HTML = '''    <a class="hero-back" href="index.html">
      <svg viewBox="0 0 24 24"><path d="M20 11H7.83l5.59-5.59L12 4l-8 8 8 8 1.41-1.41L7.83 13H20v-2z"/></svg>
      Back to Dashboard
    </a>
'''

def fix(path):
    with open(path, 'r', encoding='utf-8', errors='ignore') as f:
        html = f.read()
    orig = html

    # 1. Inject CSS before </style>
    if 'sidebar-back' not in html:
        html = re.sub(r'(</style>)', BACK_BTN_CSS + r'\1', html, count=1)

    # 2. Insert back link at TOP of sidebar (right after sidebar-header div)
    if 'sidebar-back' not in html or 'href="index.html"' not in html.split('class="sidebar"')[1][:500] if 'class="sidebar"' in html else True:
        html = re.sub(
            r'(<div[^>]*class=["\']sidebar-header["\'][^>]*>.*?</div>)',
            r'\1\n' + BACK_LINK_HTML,
            html, count=1, flags=re.S
        )

    # 3. Insert hero-back link at TOP of hero div (before hero-tag)
    if 'hero-back' not in html:
        html = re.sub(
            r'(<div[^>]*class=["\']hero["\'][^>]*>\s*)',
            r'\1' + HERO_BACK_HTML,
            html, count=1
        )

    if html != orig:
        with open(path, 'w', encoding='utf-8') as f:
            f.write(html)
        return True
    return False

ok = err = 0
for f in TOPIC_FILES:
    try:
        if fix(f):
            ok += 1
            print(f'  ✓ {f}')
        else:
            print(f'  – {f}')
    except Exception as e:
        err += 1
        print(f'  ✗ {f}: {e}')

print(f'\n✅ {ok}/{len(TOPIC_FILES)} pages updated. Errors: {err}')
