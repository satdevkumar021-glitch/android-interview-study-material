#!/usr/bin/env python3
"""
fix_all_pages.py
================
Transforms all 97 topic HTML pages to the unified scroll-based design:

FOR TYPE-A PAGES (class="section" with onclick show() tabs):
  1. Make ALL sections always visible (remove display:none, active class toggle)
  2. Remove all .nav-buttons (prev/next bottom buttons)
  3. Convert sidebar <button onclick="show(...)"> to <a href="#sN" data-section="sN">
  4. Replace the show()/showSection() JS with scroll-spy + smooth-scroll
  5. Fix progress bar to start empty (not hardcoded 11%)
  6. Standardize CSS: --accent2 to #56cfb2, consistent section padding, border separators

FOR TYPE-B PAGES (legacy <nav><a href="#id"> with <section id="...">):
  1. Unify CSS variables to match Type-A design system
  2. Upgrade sidebar nav style to match Type-A (.sidebar, .nav-item, .nav-num)
  3. Upgrade hero to match Type-A design
  4. Replace IntersectionObserver scroll-spy with the unified version
  5. Ensure <main> has id="mainScroll"

TYPE-C (5A already converted): skip.
"""

import os
import re
import glob

# ─── File lists ──────────────────────────────────────────────────────────────
ALREADY_DONE = {'5A_Coroutines_Fundamentals.html'}

all_topic_files = sorted(
    f for f in glob.glob('*.html')
    if re.match(r'^\d+[A-Z]_.*\.html$', f) and f not in ALREADY_DONE
)

# Classify pages
type_a = [f for f in all_topic_files if 'onclick="show(' in open(f).read() or "onclick='show(" in open(f).read() or 'showSection' in open(f).read()]
type_b = [f for f in all_topic_files if f not in type_a]

print(f"Type A (onclick show): {len(type_a)}")
print(f"Type B (legacy nav):   {len(type_b)}")

# ─── UNIFIED SCROLL-SPY SCRIPT (replaces show/showSection + IntersectionObserver)
UNIFIED_SCROLL_JS = '''
<script>
// ── Unified Scroll-Spy & Smooth-Scroll ──────────────────────────────────────
(function () {
  'use strict';

  // Disable any legacy show/showSection functions so onclick does nothing
  window.show = function() {};
  window.showSection = function() {};

  var mainEl = document.getElementById('mainScroll') || document.querySelector('.main') || document.querySelector('main');
  if (!mainEl) return;

  // All sections (div.section[id] or section[id])
  var sections = Array.from(document.querySelectorAll('.section[id], section[id]'))
    .filter(function(s){ return s.id && !s.id.startsWith('aip-'); });
  // All sidebar nav items with data-section attribute
  var navItems = Array.from(document.querySelectorAll('.nav-item[data-section]'));
  var progressFill = document.getElementById('progressFill');

  function getActiveSection() {
    var scrollTop = mainEl.scrollTop;
    var threshold = mainEl.clientHeight * 0.38;
    var active = sections[0];
    for (var i = 0; i < sections.length; i++) {
      var sec = sections[i];
      if (sec.offsetTop - scrollTop <= threshold) active = sec;
    }
    return active;
  }

  function updateSidebar() {
    var active = getActiveSection();
    if (!active) return;
    navItems.forEach(function(item) {
      item.classList.toggle('active', item.dataset.section === active.id);
    });
    // Reading progress bar
    if (progressFill) {
      var scrollable = mainEl.scrollHeight - mainEl.clientHeight;
      var pct = scrollable > 0 ? Math.min((mainEl.scrollTop / scrollable) * 100, 100) : 0;
      progressFill.style.width = pct + '%';
    }
    // Auto-scroll sidebar to keep active item visible
    var activeItem = navItems.find(function(it){ return it.dataset.section === active.id; });
    if (activeItem) {
      var sidebar = activeItem.closest('.sidebar');
      if (sidebar) {
        var itemTop = activeItem.offsetTop;
        var sbH = sidebar.clientHeight;
        var sbScroll = sidebar.scrollTop;
        if (itemTop < sbScroll + 40 || itemTop > sbScroll + sbH - 60) {
          sidebar.scrollTop = Math.max(0, itemTop - sbH / 2 + 24);
        }
      }
    }
  }

  mainEl.addEventListener('scroll', updateSidebar, { passive: true });
  updateSidebar();

  // Smooth-scroll sidebar links
  navItems.forEach(function(item) {
    item.addEventListener('click', function(e) {
      e.preventDefault();
      var target = document.getElementById(item.dataset.section);
      if (target) {
        var topbarEl = document.getElementById('aip-topbar');
        var offset = topbarEl ? topbarEl.offsetHeight + 8 : 8;
        mainEl.scrollTo({ top: target.offsetTop - offset, behavior: 'smooth' });
      }
    });
  });
})();

function toggleQuiz(el) {
  var ans = el.nextElementSibling;
  var icon = el.querySelector('.toggle-icon');
  if (ans) ans.classList.toggle('open');
  if (icon) icon.classList.toggle('open');
}
</script>
'''

# ─── CSS ADDITIONS for Type-A to ensure sections are visible + separated ─────
TYPE_A_CSS_PATCH = '''
  /* === Scroll-mode overrides === */
  .section { display: block !important; opacity: 1 !important; animation: none !important; padding: 40px 48px; max-width: 920px; border-bottom: 1px solid var(--border); }
  .section:last-of-type { border-bottom: none; }
  .nav-buttons { display: none !important; }
  .main { overflow-y: auto; }
  .progress-fill { transition: width 0.1s linear; }
  @media(max-width:768px){ .section { padding: 24px 16px !important; } }
'''

# ─── TYPE-B UNIFIED CSS (replaces disparate nav/sidebar styles) ───────────────
TYPE_B_SIDEBAR_CSS = '''
  /* === Unified sidebar (Type-B → Type-A style) === */
  .sidebar { width: 260px; min-width: 260px; background: var(--surface); border-right: 1px solid var(--border); position: sticky; top: 0; height: 100vh; overflow-y: auto; padding: 24px 16px; display: flex; flex-direction: column; gap: 4px; flex-shrink: 0; }
  .sidebar-header { font-size: 11px; text-transform: uppercase; letter-spacing: .1em; color: var(--muted); font-weight: 700; margin-bottom: 12px; padding-bottom: 10px; border-bottom: 1px solid var(--border); }
  .nav-item { display: flex; align-items: center; gap: 10px; padding: 8px 12px; border-radius: 7px; cursor: pointer; color: var(--muted); font-size: 13px; font-weight: 500; transition: all .15s; border: none; background: none; width: 100%; text-align: left; text-decoration: none; }
  .nav-item:hover { background: var(--surface2); color: var(--text); }
  .nav-item.active { background: rgba(124,106,247,.15); color: var(--accent); }
  .nav-num { background: var(--surface2); color: var(--muted); font-size: 10px; font-weight: 700; padding: 2px 6px; border-radius: 4px; min-width: 22px; text-align: center; flex-shrink: 0; }
  .nav-item.active .nav-num { background: rgba(124,106,247,.25); color: var(--accent); }
  /* Scroll-mode */
  section[id] { display: block !important; padding: 40px 48px; border-bottom: 1px solid var(--border); }
  section[id]:last-of-type { border-bottom: none; }
  .nav-buttons { display: none !important; }
  .main, main { overflow-y: auto; }
  .progress-bar { position: fixed; top: 0; left: 0; right: 0; height: 3px; background: var(--border); z-index: 100; }
  .progress-fill { height: 100%; background: linear-gradient(90deg,var(--accent),var(--accent2)); transition: width 0.1s linear; }
  @media(max-width:768px){ section[id] { padding: 24px 16px !important; } .sidebar { display: none; } }
  ::-webkit-scrollbar{width:6px;height:6px;}::-webkit-scrollbar-track{background:transparent;}::-webkit-scrollbar-thumb{background:var(--border);border-radius:3px;}
'''


def fix_type_a(filepath):
    """Transform Type-A pages (onclick show/showSection) to scroll mode."""
    with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
        html = f.read()

    original = html

    # 1. Fix CSS variables: accent2 inconsistency (#4f9eff → #56cfb2)
    html = html.replace('--accent2:#4f9eff', '--accent2:#56cfb2')
    html = html.replace('--accent2: #4f9eff', '--accent2: #56cfb2')
    # Add surface2 if missing
    if '--surface2' not in html:
        html = html.replace('--radius:10px', '--surface2:#222535;--radius:10px')

    # 2. Remove hardcoded progress width on progressFill
    html = re.sub(r'(<div[^>]*id="progressFill"[^>]*style=")[^"]*(")', r'\1width:0%\2', html)
    html = re.sub(r"(<div[^>]*id='progressFill'[^>]*style=')[^']*(')", r"\1width:0%\2", html)

    # 3. Add CSS patch before </style> (first occurrence)
    if TYPE_A_CSS_PATCH.strip() not in html:
        html = html.replace('</style>\n</head>', TYPE_A_CSS_PATCH + '</style>\n</head>', 1)

    # 4. Make .main scrollable (not overflow:auto on a fixed height)
    #    ensure layout is flex
    html = re.sub(r'\.main\s*\{([^}]*?)overflow-y\s*:\s*auto([^}]*?)\}',
                  lambda m: '.main {' + m.group(1) + 'overflow-y:auto' + m.group(2) + '}', html)

    # 5. Convert sidebar buttons to <a> links with data-section
    def convert_nav_button(m):
        full = m.group(0)
        # Extract section id from onclick show('s1',1) or showSection('s1',1)
        sid_m = re.search(r"show(?:Section)?\s*\(\s*['\"](\w+)['\"]", full)
        if not sid_m:
            return full
        sid = sid_m.group(1)
        # Extract inner HTML (content between > and </button>)
        inner_m = re.search(r'>(.*?)</button>', full, re.S)
        inner = inner_m.group(1) if inner_m else sid
        return f'<a class="nav-item" href="#{sid}" data-section="{sid}">{inner}</a>'

    html = re.sub(
        r'<button[^>]*class=["\']nav-item[^"\']*["\'][^>]*>.*?</button>',
        convert_nav_button, html, flags=re.S
    )

    # 6. Add id="mainScroll" to <main class="main"> if missing
    if 'id="mainScroll"' not in html:
        html = re.sub(r'<main\s+class="main"', '<main class="main" id="mainScroll"', html)
        html = re.sub(r'<main\s+class=\'main\'', '<main class="main" id="mainScroll"', html)

    # 7. Remove nav-buttons divs entirely
    html = re.sub(r'\s*<div class=["\']nav-buttons["\']>.*?</div>', '', html, flags=re.S)

    # 8. Remove active class from first section (all sections always visible now)
    html = re.sub(r'class="section active"', 'class="section"', html)
    html = re.sub(r"class='section active'", "class='section'", html)

    # 9. Replace show()/showSection() JS block + old progress script with unified scroll-spy
    #    Remove the old <script> block that contains function show(...) or showSection(...)
    html = re.sub(
        r'<script>\s*function\s+(?:show|showSection)\s*\(.*?</script>',
        '', html, flags=re.S
    )
    # Also remove any standalone show() / showSection() inline scripts
    html = re.sub(
        r'<script>\s*(?:const|let|var)\s+sections\s*=.*?</script>',
        '', html, flags=re.S
    )

    # 10. Inject unified scroll-spy before </body>
    if 'getActiveSection' not in html:
        html = html.replace('</body>', UNIFIED_SCROLL_JS + '\n</body>', 1)

    if html != original:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(html)
        return True
    return False


def get_sidebar_header(filepath, html):
    """Extract topic code + name for sidebar header."""
    fname = os.path.basename(filepath)
    m = re.match(r'^(\d+[A-Z])_(.*)\.html$', fname)
    if m:
        code = m.group(1)
        name = m.group(2).replace('_', ' ')
        return f"{code} · {name}"
    title_m = re.search(r'<title>(.*?)</title>', html, re.I)
    return title_m.group(1).strip() if title_m else fname


def fix_type_b(filepath):
    """Transform Type-B pages (legacy <nav><a href="#..."> with <section id="...">) to unified design."""
    with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
        html = f.read()

    original = html

    # 1. Unify CSS variables
    # These pages use --muted:#8b8fa8 (slightly different) → normalize
    html = html.replace('--muted:#8b8fa8', '--muted:#8b90b8')
    html = html.replace('--muted: #8b8fa8', '--muted: #8b90b8')
    # Add missing vars
    if '--surface2' not in html:
        html = re.sub(r'(--surface:\s*#1a1d27\s*;)', r'\1--surface2:#222535;', html)
    if '--code-bg' not in html:
        html = re.sub(r'(--good:\s*#56cfb2\s*;)', r'\1--code-bg:#13151f;--radius:10px;', html)
    if '--accent2' not in html:
        html = re.sub(r'(--accent:\s*#7c6af7\s*;)', r'\1--accent2:#56cfb2;', html)

    # 2. Replace <nav> sidebar with unified .sidebar structure
    # Extract nav links
    nav_links = re.findall(r'<a\s+href="#(\w+)">(.*?)</a>', html)

    if nav_links:
        sidebar_header = get_sidebar_header(filepath, html)
        num = 1
        nav_items_html = ''
        for anchor_id, label in nav_links:
            # Clean label (remove number prefix like "1 · ")
            clean_label = re.sub(r'^\d+\s*[·\-]\s*', '', label).strip()
            nav_items_html += f'\n  <a class="nav-item" href="#{anchor_id}" data-section="{anchor_id}"><span class="nav-num">{num}</span> {clean_label}</a>'
            num += 1

        new_sidebar = (
            f'<nav class="sidebar" id="sidebar">\n'
            f'  <div class="sidebar-header">{sidebar_header}</div>'
            f'{nav_items_html}\n'
            f'</nav>'
        )

        # Replace existing <nav>...</nav>
        html = re.sub(r'<nav>.*?</nav>', new_sidebar, html, count=1, flags=re.S)

    # 3. Add unified sidebar CSS before </style>
    if 'Unified sidebar' not in html:
        html = html.replace('</style>\n</head>', TYPE_B_SIDEBAR_CSS + '</style>\n</head>', 1)

    # 4. Add id="mainScroll" to <main>
    if 'id="mainScroll"' not in html:
        html = re.sub(r'<main\b', '<main id="mainScroll"', html, count=1)

    # 5. Add progress bar (if not present)
    if 'progress-bar' not in html and 'progressFill' not in html:
        html = html.replace(
            '</style>\n</head>',
            '</style>\n</head>\n',
        )
        html = html.replace(
            '<body>',
            '<body>\n<div class="progress-bar"><div class="progress-fill" id="progressFill" style="width:0%"></div></div>'
        )

    # 6. Wrap body content in .layout div if not already
    if 'class="layout"' not in html:
        # Wrap <nav...> and <main...> together
        html = re.sub(
            r'(<nav class="sidebar".*?</nav>\s*<main)',
            r'<div class="layout">\1',
            html, count=1, flags=re.S
        )
        html = html.replace('</main>\n</body>', '</main>\n</div>\n</body>', 1)
        html = html.replace('</main>\n\n</body>', '</main>\n</div>\n\n</body>', 1)

    # 7. Remove old IntersectionObserver scroll spy and replace with unified
    html = re.sub(
        r'<script>\s*const links\s*=.*?</script>',
        '', html, flags=re.S
    )

    # 8. Inject unified scroll-spy before </body>
    if 'getActiveSection' not in html:
        # Add type-B section selector comment
        unified = UNIFIED_SCROLL_JS.replace(
            "'.section[id], section[id]'",
            "'section[id], .section[id]'"
        )
        html = html.replace('</body>', unified + '\n</body>', 1)

    # 9. Add shared.js if not present
    if 'shared.js' not in html:
        html = html.replace('</body>', '<script src="shared.js"></script>\n</body>', 1)

    if html != original:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(html)
        return True
    return False


# ─── Run ─────────────────────────────────────────────────────────────────────
changed_a = 0
changed_b = 0
errors = []

print("\n── Type A pages ──")
for f in type_a:
    try:
        if fix_type_a(f):
            changed_a += 1
            print(f"  ✓ {f}")
        else:
            print(f"  – {f} (no change)")
    except Exception as e:
        errors.append((f, str(e)))
        print(f"  ✗ {f}: {e}")

print("\n── Type B pages ──")
for f in type_b:
    try:
        if fix_type_b(f):
            changed_b += 1
            print(f"  ✓ {f}")
        else:
            print(f"  – {f} (no change)")
    except Exception as e:
        errors.append((f, str(e)))
        print(f"  ✗ {f}: {e}")

print(f"\n✅ Done: {changed_a} Type-A + {changed_b} Type-B pages updated.")
if errors:
    print(f"⚠️  {len(errors)} errors:")
    for ef, em in errors:
        print(f"   {ef}: {em}")
