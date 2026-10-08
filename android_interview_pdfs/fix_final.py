#!/usr/bin/env python3
"""
fix_final.py — Complete final fix for all 97 topic pages.

Bugs fixed:
  1. Duplicate scroll-spy <script> blocks (every page has 2 — remove the older one)
  2. Old `function show(` still present in 21 pages → stub it out
  3. 5A display:none on .section not overridden (5A has its own inline spy, but no CSS override)
  4. Scroll container conflict: .main overflow-y:auto + mainEl.scrollTop-based spy is correct
     (window scroll would conflict with sticky sidebar). Verify the pattern is consistent.
  5. Ensure sidebar `top` accounts for topbar (shared.css handles via body.aip-injected rule)
  6. Consistent CSS: remove fadeIn animation reference since all sections are visible
"""

import os, re, glob

topic_files = sorted(
    f for f in glob.glob('*.html')
    if re.match(r'^\d+[A-Z]_.*\.html$', f)
)

CANONICAL_SCROLL_SCRIPT = '''
<script>
// ── Scroll-spy & smooth-scroll (canonical v5) ────────────────────────────────
(function () {
  'use strict';
  window.show = function() {};
  window.showSection = function() {};

  var mainEl = document.getElementById('mainScroll') ||
               document.querySelector('.main') ||
               document.querySelector('main');
  if (!mainEl) return;

  var sections = Array.from(
    document.querySelectorAll('.section[id], section[id]')
  ).filter(function(s){ return s.id && !s.id.startsWith('aip-'); });

  var navItems = Array.from(
    document.querySelectorAll('.nav-item[data-section]')
  );

  var progressFill = document.getElementById('progressFill');

  function getActiveSection() {
    var scrollTop = mainEl.scrollTop;
    var threshold = mainEl.clientHeight * 0.38;
    var active = sections[0];
    for (var i = 0; i < sections.length; i++) {
      if (sections[i].offsetTop - scrollTop <= threshold) active = sections[i];
    }
    return active;
  }

  function updateSidebar() {
    var active = getActiveSection();
    if (!active) return;
    navItems.forEach(function(item) {
      item.classList.toggle('active', item.dataset.section === active.id);
    });
    if (progressFill) {
      var scrollable = mainEl.scrollHeight - mainEl.clientHeight;
      progressFill.style.width =
        (scrollable > 0 ? Math.min((mainEl.scrollTop / scrollable) * 100, 100) : 0) + '%';
    }
    // keep active sidebar item in view
    var activeItem = navItems.find(function(it){
      return it.dataset.section === active.id;
    });
    if (activeItem) {
      var sb = activeItem.closest('.sidebar');
      if (sb) {
        var iTop = activeItem.offsetTop, sbH = sb.clientHeight, sbS = sb.scrollTop;
        if (iTop < sbS + 40 || iTop > sbS + sbH - 60)
          sb.scrollTop = Math.max(0, iTop - sbH / 2 + 24);
      }
    }
  }

  mainEl.addEventListener('scroll', updateSidebar, { passive: true });
  // Run once on load (after a tick so layout is complete)
  setTimeout(updateSidebar, 0);

  navItems.forEach(function(item) {
    item.addEventListener('click', function(e) {
      e.preventDefault();
      var target = document.getElementById(item.dataset.section);
      if (!target) return;
      var tb = document.getElementById('aip-topbar');
      var offset = tb ? tb.offsetHeight + 8 : 8;
      mainEl.scrollTo({ top: Math.max(0, target.offsetTop - offset), behavior: 'smooth' });
    });
  });
}());

function toggleQuiz(el) {
  var ans = el.nextElementSibling;
  var icon = el.querySelector('.toggle-icon');
  if (ans)  ans.classList.toggle('open');
  if (icon) icon.classList.toggle('open');
}
</script>
'''

SCROLL_CSS_BLOCK = '''  /* === Scroll-mode: all sections always visible === */
  .section { display: block !important; opacity: 1 !important; animation: none !important;
             padding: 40px 48px; max-width: 920px; border-bottom: 1px solid var(--border); }
  .section:last-of-type { border-bottom: none; }
  section[id] { display: block !important; padding: 40px 48px;
                border-bottom: 1px solid var(--border); }
  section[id]:last-of-type { border-bottom: none; }
  .nav-buttons { display: none !important; }
  .main { overflow-y: auto; flex: 1; }
  main { overflow-y: auto; flex: 1; }
  @media(max-width:768px){
    .section, section[id] { padding: 24px 16px !important; }
    .sidebar { display: none !important; }
  }
'''


def fix_page(filepath):
    with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
        html = f.read()
    original = html

    # ── 1. Remove ALL existing scroll-spy / show() script blocks ──────────────
    # Pattern A: our injected canonical script block
    html = re.sub(
        r'<script>\s*//\s*──\s*(?:Scroll-spy|Unified Scroll)[^\n]*\n.*?</script>',
        '', html, flags=re.S
    )
    # Pattern B: the previous fix_all_pages.py injected block (starts with window.show =)
    html = re.sub(
        r'<script>\s*// ──.*?window\.show\s*=.*?</script>',
        '', html, flags=re.S
    )
    # Pattern C: any block containing getActiveSection
    html = re.sub(
        r'<script>[^<]*getActiveSection[^<]*(?:<(?!/script>)[^<]*)*</script>',
        '', html, flags=re.S
    )
    # Pattern D: old show()/showSection() inline function blocks
    html = re.sub(
        r'<script>\s*function\s+(?:show|showSection)\s*\(.*?</script>',
        '', html, flags=re.S
    )
    # Pattern E: old sections/total array approach
    html = re.sub(
        r'<script>\s*(?:const|let|var)\s+sections\s*=\s*\[.*?</script>',
        '', html, flags=re.S
    )
    # Pattern F: old IntersectionObserver for Type-B pages
    html = re.sub(
        r'<script>\s*const links\s*=\s*document\.querySelectorAll.*?</script>',
        '', html, flags=re.S
    )

    # Stub any remaining show() / showSection() function definitions
    # (edge case: some pages have show() defined outside a script block we matched)
    html = re.sub(
        r'(function\s+show\s*\([^)]*\)\s*\{)',
        r'/* stubbed */function show(id,n){',
        html
    )

    # ── 2. Remove duplicate/outdated scroll CSS patches ───────────────────────
    html = re.sub(
        r'/\* === Scroll-mode overrides? === \*/.*?(?=@media|</style>)',
        '', html, flags=re.S
    )
    html = re.sub(
        r'/\* === Unified sidebar.*?=== \*/.*?(?=@media|</style>)',
        '', html, flags=re.S
    )

    # ── 3. Inject clean scroll CSS before </style> ────────────────────────────
    if 'Scroll-mode: all sections always visible' not in html:
        html = re.sub(r'(</style>\s*</head>)', SCROLL_CSS_BLOCK + r'\1', html, count=1)

    # ── 4. Inject canonical scroll-spy script before </body> ──────────────────
    html = html.replace('</body>', CANONICAL_SCROLL_SCRIPT + '\n</body>', 1)

    # ── 5. Ensure .main and mainScroll are correct ────────────────────────────
    # main tag: must have id="mainScroll"
    if 'id="mainScroll"' not in html:
        html = re.sub(r'<main\b(?![^>]*id=)', '<main id="mainScroll"', html, count=1)
    # class="main" div: must have id="mainScroll"
    html = re.sub(
        r'<(main|div)\s+class="main"(?![^>]*id=)',
        r'<\1 class="main" id="mainScroll"',
        html, count=1
    )

    # ── 6. Fix CSS variables consistency ─────────────────────────────────────
    html = html.replace('--accent2:#4f9eff', '--accent2:#56cfb2')
    html = html.replace('--accent2: #4f9eff', '--accent2: #56cfb2')
    if '--surface2' not in html:
        html = re.sub(r'(--border:\s*#2e314[89]\s*;)',
                      r'\1--surface2:#222535;', html, count=1)
    if '--code-bg' not in html:
        html = re.sub(r'(--radius:\s*10px\s*;)',
                      r'--code-bg:#13151f;\1', html, count=1)

    # ── 7. Fix progress bar initial value ─────────────────────────────────────
    html = re.sub(
        r'(<div[^>]*id=["\']progressFill["\'][^>]*style=["\'])width:\d+%(["\'])',
        r'\1width:0%\2', html
    )

    # ── 8. Ensure sidebar nav items use data-section ─────────────────────────
    # Convert any remaining old-style button onclick nav items
    def convert_btn(m):
        full = m.group(0)
        sid_m = re.search(r"show(?:Section)?\s*\(\s*['\"](\w+)['\"]", full)
        if not sid_m:
            return full
        sid = sid_m.group(1)
        inner_m = re.search(r'>(.*?)</button>', full, re.S)
        inner = inner_m.group(1) if inner_m else sid
        return f'<a class="nav-item" href="#{sid}" data-section="{sid}">{inner}</a>'
    html = re.sub(
        r'<button[^>]*class=["\']nav-item[^"\']*["\'][^>]*>.*?</button>',
        convert_btn, html, flags=re.S
    )

    # ── 9. Remove .active from first section (all visible now) ───────────────
    html = re.sub(r'class="section active"', 'class="section"', html)
    html = re.sub(r"class='section active'", "class='section'", html)

    # ── 10. Ensure shared.js is last script ───────────────────────────────────
    if '<script src="shared.js"></script>' not in html:
        html = html.replace(CANONICAL_SCROLL_SCRIPT + '\n</body>',
                            CANONICAL_SCROLL_SCRIPT +
                            '\n<script src="shared.js"></script>\n</body>', 1)
    else:
        # Move shared.js to just before </body> if it's not already there
        html = html.replace('<script src="shared.js"></script>', '')
        html = html.replace(CANONICAL_SCROLL_SCRIPT + '\n</body>',
                            CANONICAL_SCROLL_SCRIPT +
                            '\n<script src="shared.js"></script>\n</body>', 1)

    if html != original:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(html)
        return True
    return False


changed = 0
errors = []
for f in topic_files:
    try:
        if fix_page(f):
            changed += 1
            print(f'  ✓ {f}')
        else:
            print(f'  – {f} (no change needed)')
    except Exception as e:
        errors.append((f, e))
        print(f'  ✗ {f}: {e}')

print(f'\n✅ {changed}/{len(topic_files)} pages updated.')
if errors:
    print(f'⚠️  {len(errors)} errors:')
    for ef, em in errors:
        print(f'   {ef}: {em}')
