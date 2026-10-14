#!/usr/bin/env python3
"""
fix_layout_study.py
Rewrites CSS and JS on all 105 topic pages to:
1. Fix layout so WINDOW scrolls (not .main) — no conflict with shared.js
2. Remove duplicate page-level scroll-spy (shared.js handles it)
3. Add study-friendly design enhancements
"""

import os, re, glob

TOPIC_FILES = sorted([f for f in os.listdir('.') if re.match(r'\d+[A-Z]_.*\.html$', f)])

# ─── NEW CSS BLOCK ────────────────────────────────────────────────────────────
NEW_STYLE_ADDITIONS = """
  /* ═══════════════════════════════════════════════════
     LAYOUT FIX — window scrolls, sidebar stays sticky
     Works perfectly with shared.js patchScrollMode()
  ═══════════════════════════════════════════════════ */

  /* 1. Root layout: flex row, full viewport height */
  html, body { height: 100%; }
  body { overflow-y: scroll; }          /* body = scroll container */
  .layout { display: flex; align-items: flex-start; min-height: 100vh; }

  /* 2. Sidebar: sticky to top, scrolls internally — shared.js sets top:52px */
  .sidebar {
    position: sticky;
    top: 0;
    height: 100vh;
    overflow-y: auto;
    flex-shrink: 0;
    width: 260px; min-width: 260px;
    scrollbar-width: thin;
    scrollbar-color: var(--border) transparent;
  }

  /* 3. Main: fills remaining width, NOT a scroll container */
  .main { flex: 1; overflow: visible; min-width: 0; }

  /* 4. All sections always visible, stacked vertically */
  .section {
    display: block !important;
    opacity: 1 !important;
    animation: none !important;
    border-bottom: 1px solid var(--border);
    padding: 44px 52px;
    max-width: 900px;
  }
  .section:last-of-type { border-bottom: none; padding-bottom: 80px; }
  section[id] {
    display: block !important;
    border-bottom: 1px solid var(--border);
    padding: 44px 52px;
    max-width: 900px;
  }
  section[id]:last-of-type { border-bottom: none; padding-bottom: 80px; }

  /* ═══════════════════════════════════════════════════
     STUDY-FRIENDLY DESIGN ENHANCEMENTS
  ═══════════════════════════════════════════════════ */

  /* Better section titles */
  .section-title {
    font-size: 21px; font-weight: 800;
    margin-bottom: 28px; padding-bottom: 16px;
    border-bottom: 1px solid var(--border);
    display: flex; align-items: center; gap: 12px;
    letter-spacing: -0.3px;
  }

  /* Sidebar — active item highlight: left accent bar */
  .nav-item.active,
  .nav-item.aip-nav-active {
    background: rgba(124,106,247,.13) !important;
    color: var(--accent) !important;
    border-left: 3px solid var(--accent);
    padding-left: 9px !important;
  }
  .nav-item.active .nav-num,
  .nav-item.aip-nav-active .nav-num {
    background: rgba(124,106,247,.28) !important;
    color: var(--accent) !important;
  }
  /* Default nav items: no left border */
  .nav-item { border-left: 3px solid transparent; }

  /* Section entry fade-in as user scrolls */
  @keyframes sectionIn {
    from { opacity: 0; transform: translateY(12px); }
    to   { opacity: 1; transform: translateY(0); }
  }
  .section-visible { animation: sectionIn 0.35s ease forwards; }

  /* Code blocks: better readability */
  pre {
    background: var(--code-bg);
    border: 1px solid var(--border);
    border-radius: var(--radius);
    padding: 20px 22px;
    overflow-x: auto;
    margin: 16px 0 22px;
    font-size: 13px;
    line-height: 1.65;
    position: relative;
  }

  /* Callout improvements */
  .callout {
    border-left: 3px solid;
    padding: 14px 18px;
    border-radius: 0 10px 10px 0;
    margin: 18px 0;
    font-size: 14px;
    line-height: 1.7;
  }

  /* Quiz cards: cleaner */
  .quiz-card {
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: 10px;
    margin-bottom: 14px;
    overflow: hidden;
    transition: border-color .2s;
  }
  .quiz-card:hover { border-color: rgba(124,106,247,.4); }

  /* Smooth scroll offset for topbar */
  .section[id]::before, section[id]::before {
    content: '';
    display: block;
    height: 60px;
    margin-top: -60px;
    pointer-events: none;
    visibility: hidden;
  }

  /* Keyboard hint in sidebar */
  .nav-hint {
    font-size: 10px; color: var(--muted); text-align: center;
    padding: 10px 0 4px; margin-top: auto; opacity: .5;
    letter-spacing: .05em;
  }

  /* Hide old nav buttons */
  .nav-buttons { display: none !important; }

  /* Hide old progress bar (shared.js adds its own) */
  .progress-bar { display: none !important; }

  /* Mobile */
  @media (max-width: 768px) {
    .sidebar { display: none !important; }
    .section, section[id] { padding: 28px 18px !important; }
    .hero { padding: 28px 18px 24px !important; }
    .hero h1 { font-size: 22px !important; }
  }

  /* Scrollbar */
  ::-webkit-scrollbar { width: 6px; height: 6px; }
  ::-webkit-scrollbar-track { background: transparent; }
  ::-webkit-scrollbar-thumb { background: var(--border); border-radius: 3px; }

  /* Reading progress per-section: thin colored bar at section top */
  .section-read-bar {
    height: 2px;
    background: linear-gradient(90deg, var(--accent), var(--accent2));
    width: 0%;
    transition: width 0.4s ease;
    border-radius: 1px;
    margin-bottom: 20px;
  }
  .section.read .section-read-bar { width: 100%; }
"""

# ─── NEW PAGE-LEVEL JS (replaces the old one) ────────────────────────────────
NEW_PAGE_JS = """<script>
/* Page-level JS — minimal, no duplicate scroll-spy (shared.js owns that) */
(function () {

  /* ── Sidebar nav click → smooth scroll ── */
  document.querySelectorAll('.nav-item[data-section]').forEach(function (item) {
    item.addEventListener('click', function (e) {
      e.preventDefault();
      var target = document.getElementById(item.dataset.section);
      if (!target) return;
      var tb  = document.getElementById('aip-topbar');
      var off = (tb ? tb.offsetHeight : 52) + 16;
      var y   = target.getBoundingClientRect().top + window.scrollY - off;
      window.scrollTo({ top: Math.max(0, y), behavior: 'smooth' });
    });
  });

  /* ── Section fade-in on first scroll into view ── */
  if ('IntersectionObserver' in window) {
    var fadeObs = new IntersectionObserver(function (entries) {
      entries.forEach(function (entry) {
        if (entry.isIntersecting) {
          entry.target.classList.add('section-visible');
          fadeObs.unobserve(entry.target);
        }
      });
    }, { threshold: 0.05 });

    document.querySelectorAll('.section[id], section[id]').forEach(function (s) {
      fadeObs.observe(s);
    });
  }

}());

/* ── Quiz accordion ── */
function toggleQuiz(el) {
  var ans  = el.nextElementSibling;
  var icon = el.querySelector('.toggle-icon');
  if (ans)  ans.classList.toggle('open');
  if (icon) icon.classList.toggle('open');
}
</script>
<script src="shared.js"></script>"""

def fix_page(fname):
    with open(fname, encoding='utf-8') as f:
        content = f.read()

    original = content

    # ── 1. Remove old .main { overflow-y: auto } and height:100vh conflicts ──
    content = re.sub(
        r'\.main\s*\{[^}]*overflow-y\s*:\s*auto[^}]*\}',
        '.main { flex: 1; overflow: visible; min-width: 0; }',
        content
    )
    # Remove height:100vh on .layout
    content = re.sub(
        r'(\.layout\s*\{[^}]*?)min-height\s*:\s*100vh([^}]*\})',
        lambda m: m.group(1) + 'min-height: 100vh' + m.group(2),
        content
    )

    # ── 2. Inject new CSS just before </style> ──
    if NEW_STYLE_ADDITIONS.strip()[:30] not in content:
        content = content.replace('</style>', NEW_STYLE_ADDITIONS + '\n</style>', 1)

    # ── 3. Replace the old page-level <script>...</script> + shared.js block ──
    # Pattern: the IIFE scroll spy + toggleQuiz + shared.js load
    old_script_pat = re.compile(
        r'<script>\s*\(function\s*\(\s*\)\s*\{.*?toggleQuiz.*?\}\s*</script>\s*<script\s+src=["\']shared\.js["\']></script>',
        re.DOTALL
    )
    if old_script_pat.search(content):
        content = old_script_pat.sub(NEW_PAGE_JS, content)
    elif '<script src="shared.js"></script>' in content and 'toggleQuiz' in content:
        # Fallback: remove everything from the last <script> before shared.js through the shared.js tag
        old_last_script_pat = re.compile(
            r'<script>\s*\(function[\s\S]*?</script>\s*<script src="shared\.js"></script>',
            re.DOTALL
        )
        if old_last_script_pat.search(content):
            content = old_last_script_pat.sub(NEW_PAGE_JS, content)

    if content != original:
        with open(fname, 'w', encoding='utf-8') as f:
            f.write(content)
        return True
    return False

print(f"Processing {len(TOPIC_FILES)} pages...\n")
fixed = 0
skipped = 0
for fname in TOPIC_FILES:
    result = fix_page(fname)
    if result:
        fixed += 1
        print(f"  ✅ Fixed: {fname}")
    else:
        skipped += 1
        print(f"  ⏭  Skipped (already up to date): {fname}")

print(f"\nDone: {fixed} fixed, {skipped} skipped out of {len(TOPIC_FILES)} pages")
