#!/usr/bin/env python3
"""
fix_scroll_spy.py
=================
THE definitive fix. Root cause:
  shared.js patchScrollMode() sets: .main, main { overflow: visible !important }
  This means the WINDOW scrolls, not the <main> element.
  All previous scroll spies used mainEl.scrollTop which is always 0 — broken.

Fix: Replace every inline scroll spy with a window-scroll based version
that uses getBoundingClientRect() so it works regardless of scroll container.

Also: shared.js uses .aip-nav-active class for highlights via IntersectionObserver.
Our CSS uses .active class. The page inline script must add BOTH classes so
whichever system is active, the sidebar item gets highlighted.
"""

import os, re, glob

TOPIC_FILES = sorted(
    f for f in glob.glob('*.html')
    if re.match(r'^\d+[A-Z]_.*\.html$', f)
)

# The correct scroll spy — uses window.scrollY + getBoundingClientRect
# Works whether window scrolls or mainEl scrolls (checks both)
CORRECT_SCROLL_SPY = '''<script>
(function () {
  'use strict';

  // Neutralise legacy tab-switching functions
  window.show        = function () {};
  window.showSection = function () {};

  // ── Collect sections & nav items ───────────────────────────────────────────
  var sections = Array.from(
    document.querySelectorAll('.section[id], section[id]')
  ).filter(function (s) {
    return s.id && !s.id.startsWith('aip-') && s.id !== 'aip-flip-section';
  });

  var navItems = Array.from(
    document.querySelectorAll('.nav-item[data-section]')
  );

  var progressFill = document.getElementById('progressFill');

  // ── Determine which section is currently "active" ──────────────────────────
  // Uses getBoundingClientRect so it works with ANY scroll container
  // (window scroll OR inner div scroll — shared.js forces window scroll)
  function getActiveSection () {
    var topbarH = 0;
    var tb = document.getElementById('aip-topbar');
    if (tb) topbarH = tb.offsetHeight;

    // The active section is the LAST one whose top edge is above 40% of viewport
    var viewH   = window.innerHeight || document.documentElement.clientHeight;
    var threshold = topbarH + viewH * 0.38;
    var active  = sections[0];

    for (var i = 0; i < sections.length; i++) {
      var rect = sections[i].getBoundingClientRect();
      if (rect.top <= threshold) {
        active = sections[i];
      }
    }
    return active;
  }

  // ── Update sidebar highlight + progress bar ─────────────────────────────────
  function updateSidebar () {
    var active = getActiveSection();
    if (!active) return;

    navItems.forEach(function (item) {
      var isActive = item.dataset.section === active.id;
      // Support BOTH class systems: our .active AND shared.js .aip-nav-active
      item.classList.toggle('active',          isActive);
      item.classList.toggle('aip-nav-active',  isActive);
    });

    // Progress bar (top thin gradient bar)
    if (progressFill) {
      var docH  = document.documentElement.scrollHeight - window.innerHeight;
      var pct   = docH > 0 ? Math.min((window.scrollY / docH) * 100, 100) : 0;
      progressFill.style.width = pct + '%';
    }

    // Keep the active sidebar link scrolled into view
    var activeItem = navItems.find(function (it) {
      return it.dataset.section === active.id;
    });
    if (activeItem) {
      var sb = activeItem.closest('.sidebar') ||
               activeItem.closest('nav:not(#aip-topbar)');
      if (sb) {
        var iTop = activeItem.offsetTop;
        var sbH  = sb.clientHeight;
        var sbS  = sb.scrollTop;
        if (iTop < sbS + 44 || iTop > sbS + sbH - 64) {
          sb.scrollTop = Math.max(0, iTop - sbH / 2 + 24);
        }
      }
    }
  }

  // Listen on WINDOW (shared.js forces main to overflow:visible so window scrolls)
  window.addEventListener('scroll', updateSidebar, { passive: true });
  // Also listen on any inner scroll container as fallback
  var mainEl = document.getElementById('mainScroll') ||
               document.querySelector('.main') ||
               document.querySelector('main');
  if (mainEl && mainEl !== document.body) {
    mainEl.addEventListener('scroll', updateSidebar, { passive: true });
  }

  // Run after layout is complete
  setTimeout(updateSidebar, 100);

  // ── Sidebar clicks → smooth scroll ─────────────────────────────────────────
  navItems.forEach(function (item) {
    item.addEventListener('click', function (e) {
      e.preventDefault();
      var target = document.getElementById(item.dataset.section);
      if (!target) return;
      var tb     = document.getElementById('aip-topbar');
      var offset = (tb ? tb.offsetHeight : 0) + 12;
      var y      = target.getBoundingClientRect().top + window.scrollY - offset;
      window.scrollTo({ top: Math.max(0, y), behavior: 'smooth' });
    });
  });

}());

// ── Quiz accordion ────────────────────────────────────────────────────────────
function toggleQuiz (el) {
  var ans  = el.nextElementSibling;
  var icon = el.querySelector('.toggle-icon');
  if (ans)  ans.classList.toggle('open');
  if (icon) icon.classList.toggle('open');
}
</script>
'''

# CSS that must be in every page — works with window-scroll model
SCROLL_CSS = '''  /* ── Scroll-mode: all sections always visible ── */
  .section { display: block !important; opacity: 1 !important; animation: none !important;
             padding: 40px 48px; max-width: 920px;
             border-bottom: 1px solid var(--border); }
  .section:last-of-type { border-bottom: none; }
  section[id] { display: block !important; padding: 40px 48px;
                border-bottom: 1px solid var(--border); }
  section[id]:last-of-type { border-bottom: none; }
  .nav-buttons { display: none !important; }
  /* Both .active (ours) and .aip-nav-active (shared.js) highlight the sidebar item */
  .nav-item.active,
  .nav-item.aip-nav-active {
    background: rgba(124,106,247,.15) !important;
    color: var(--accent, #7c6af7) !important;
  }
  .nav-item.active .nav-num,
  .nav-item.aip-nav-active .nav-num {
    background: rgba(124,106,247,.25) !important;
    color: var(--accent, #7c6af7) !important;
  }
  @media(max-width:768px){
    .section, section[id] { padding: 24px 16px !important; }
    .sidebar { display: none !important; }
  }
'''

def fix_page(path):
    with open(path, 'r', encoding='utf-8', errors='ignore') as f:
        html = f.read()
    orig = html

    # 1. Remove every existing scroll-spy script block
    # Match any <script> that contains getActiveSection OR window.show= OR showSection
    html = re.sub(
        r'<script>(?:(?!</script>).)*?(?:getActiveSection|window\.show\s*=|showSection\s*=)(?:(?!</script>).)*?</script>',
        '', html, flags=re.S
    )

    # 2. Remove duplicate CSS scroll-mode blocks
    html = re.sub(
        r'/\*\s*(?:===\s*)?Scroll-mode.*?(?=@media\s*\(max-width\s*:\s*768|</style>)',
        '', html, flags=re.S
    )

    # 3. Inject correct CSS before </style>
    if 'Scroll-mode: all sections always visible' not in html:
        html = re.sub(r'(</style>)', SCROLL_CSS + r'\1', html, count=1)

    # 4. Remove section active class (all visible now)
    html = re.sub(r'class="section active"', 'class="section"', html)
    html = re.sub(r"class='section active'", "class='section'", html)

    # 5. Inject correct scroll spy just before </body>
    #    (must come BEFORE shared.js so shared.js sees our nav items already wired)
    if 'getBoundingClientRect' not in html:
        html = html.replace(
            '<script src="shared.js"></script>\n</body>',
            CORRECT_SCROLL_SPY + '<script src="shared.js"></script>\n</body>'
        )
        # fallback if shared.js line not present
        if 'getBoundingClientRect' not in html:
            html = html.replace('</body>', CORRECT_SCROLL_SPY + '<script src="shared.js"></script>\n</body>')

    # 6. Ensure shared.js is included (only once, at end)
    shared_count = html.count('<script src="shared.js"></script>')
    if shared_count > 1:
        # Remove all, then add back once before </body>
        html = html.replace('<script src="shared.js"></script>', '')
        html = html.replace('</body>', '<script src="shared.js"></script>\n</body>', 1)
    elif shared_count == 0:
        html = html.replace('</body>', '<script src="shared.js"></script>\n</body>', 1)

    if html != orig:
        with open(path, 'w', encoding='utf-8') as f:
            f.write(html)
        return True
    return False


ok = err = 0
for f in TOPIC_FILES:
    try:
        if fix_page(f):
            ok += 1
            print(f'  ✓ {f}')
        else:
            print(f'  – {f}')
    except Exception as e:
        err += 1
        print(f'  ✗ {f}: {e}')

print(f'\n✅ {ok}/{len(TOPIC_FILES)} pages updated. Errors: {err}')
