/**
 * ANDROID INTERVIEW PREP — shared.js  v4 (scroll-mode, all bugs fixed)
 * Injected into every topic page. Handles:
 *   1. Top navigation bar (Home, prev/next, Mark Done, Score, PDF)
 *   2. Progress tracking (localStorage)
 *   3. SCROLL-MODE: all sections visible, sidebar auto-highlights on scroll
 *   4. Smooth-scroll on sidebar nav item click
 *   5. Section visit tracking via IntersectionObserver
 *   6. Flip-card quiz (unchanged logic)
 *   7. Score modal + progress banner
 */

(function () {
  'use strict';

  // ── Google Fonts ─────────────────────────────────────────────────
  const fontLink = document.createElement('link');
  fontLink.rel = 'stylesheet';
  fontLink.href = 'https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&family=JetBrains+Mono:wght@400;500&display=swap';
  document.head.appendChild(fontLink);

  // ── Shared CSS ───────────────────────────────────────────────────
  const cssLink = document.createElement('link');
  cssLink.rel = 'stylesheet';
  cssLink.href = new URL('shared.css', scriptUrl).href;
  document.head.appendChild(cssLink);

  // ── Syllabus map ─────────────────────────────────────────────────
  const TOPICS = [
    {id:'1A',name:'Kotlin Basics & Null Safety',file:'1A_Kotlin_Basics_Null_Safety.html',tier:1},
    {id:'1B',name:'Kotlin Functions',file:'1B_Kotlin_Functions.html',tier:1},
    {id:'1C',name:'Scope Functions',file:'1C_Scope_Functions.html',tier:1},
    {id:'1D',name:'Kotlin OOP',file:'1D_Kotlin_OOP.html',tier:1},
    {id:'1E',name:'Special Classes',file:'1E_Special_Classes.html',tier:1},
    {id:'1F',name:'Generics & Variance',file:'1F_Generics_Variance.html',tier:1},
    {id:'1G',name:'Delegation & Operators',file:'1G_Delegation_Operators.html',tier:1},
    {id:'1H',name:'Collections',file:'1H_Collections.html',tier:1},
    {id:'1I',name:'Inline & Recursion',file:'1I_Inline_Recursion.html',tier:1},
    {id:'1J',name:'Equality, Interop & Errors',file:'1J_Equality_Interop_Errors.html',tier:1},
    {id:'2A',name:'Components Overview',file:'2A_Components_Overview.html',tier:2},
    {id:'2B',name:'Activity Lifecycle & State',file:'2B_Activity_Lifecycle_State.html',tier:2},
    {id:'2C',name:'Launch Modes & Back Stack',file:'2C_Launch_Modes_Back_Stack.html',tier:2},
    {id:'2D',name:'Fragments',file:'2D_Fragments.html',tier:2},
    {id:'2E',name:'Intents',file:'2E_Intents.html',tier:2},
    {id:'3A',name:'App Startup',file:'3A_App_Startup.html',tier:1},
    {id:'3B',name:'Main Thread Internals',file:'3B_Main_Thread_Internals.html',tier:1},
    {id:'3C',name:'Binder & IPC',file:'3C_Binder_IPC.html',tier:1},
    {id:'3D',name:'Process Model',file:'3D_Process_Model.html',tier:1},
    {id:'4A',name:'ViewModel',file:'4A_ViewModel.html',tier:1},
    {id:'4B',name:'LiveData',file:'4B_LiveData.html',tier:1},
    {id:'4C',name:'Lifecycle',file:'4C_Lifecycle.html',tier:1},
    {id:'5A',name:'Coroutines Fundamentals',file:'5A_Coroutines_Fundamentals.html',tier:1},
    {id:'5B',name:'Builders & Dispatchers',file:'5B_Builders_Dispatchers.html',tier:1},
    {id:'5C',name:'Structured Concurrency',file:'5C_Structured_Concurrency.html',tier:1},
    {id:'5D',name:'Cancellation & Exceptions',file:'5D_Cancellation_Exceptions.html',tier:1},
    {id:'5E',name:'Scopes, Concurrency & Testing',file:'5E_Scopes_Concurrency_Testing.html',tier:1},
    {id:'6A',name:'Flow Core',file:'6A_Flow_Core.html',tier:1},
    {id:'6B',name:'Flow Operators',file:'6B_Flow_Operators.html',tier:1},
    {id:'6C',name:'Builders & Channels',file:'6C_Builders_Channels.html',tier:1},
    {id:'6D',name:'Sharing',file:'6D_Sharing.html',tier:1},
    {id:'7A',name:'Compose Fundamentals',file:'7A_Compose_Fundamentals.html',tier:1},
    {id:'7B',name:'State Management',file:'7B_State_Management.html',tier:1},
    {id:'7C',name:'Side Effects',file:'7C_Side_Effects.html',tier:1},
    {id:'7D',name:'Compose Performance',file:'7D_Compose_Performance.html',tier:1},
    {id:'7E',name:'Compose UI',file:'7E_Compose_UI.html',tier:1},
    {id:'7F',name:'Compose Navigation',file:'7F_Compose_Navigation.html',tier:1},
    {id:'8A',name:'Architecture Patterns',file:'8A_Architecture_Patterns.html',tier:1},
    {id:'8B',name:'Clean Architecture',file:'8B_Clean_Architecture.html',tier:1},
    {id:'9A',name:'SOLID Principles',file:'9A_SOLID_Principles.html',tier:1},
    {id:'10A',name:'Creational Patterns',file:'10A_Creational_Patterns.html',tier:2},
    {id:'10B',name:'Structural Patterns',file:'10B_Structural_Patterns.html',tier:2},
    {id:'10C',name:'Behavioral Patterns',file:'10C_Behavioral_Patterns.html',tier:2},
    {id:'11A',name:'DI & Hilt Basics',file:'11A_DI_Hilt_Basics.html',tier:1},
    {id:'11B',name:'Hilt Components',file:'11B_Hilt_Components.html',tier:1},
    {id:'12A',name:'REST & HTTP',file:'12A_REST_HTTP.html',tier:1},
    {id:'12B',name:'Retrofit & OkHttp',file:'12B_Retrofit_OkHttp.html',tier:1},
    {id:'12C',name:'Advanced Networking',file:'12C_Advanced_Networking.html',tier:1},
    {id:'13A',name:'Room',file:'13A_Room.html',tier:1},
    {id:'13B',name:'Room vs SQLite',file:'13B_Room_vs_SQLite.html',tier:1},
    {id:'13C',name:'Other Storage',file:'13C_Other_Storage.html',tier:1},
    {id:'14A',name:'WorkManager',file:'14A_WorkManager.html',tier:2},
    {id:'14B',name:'Choosing the Right Tool',file:'14B_Choosing_Right_Tool.html',tier:2},
    {id:'15A',name:'Services',file:'15A_Services.html',tier:2},
    {id:'16A',name:'BroadcastReceiver',file:'16A_BroadcastReceiver.html',tier:3},
    {id:'17A',name:'ContentProvider',file:'17A_ContentProvider.html',tier:3},
    {id:'18A',name:'Navigation & Deep Linking',file:'18A_Navigation.html',tier:2},
    {id:'19A',name:'Data & Network Security',file:'19A_Data_Network_Security.html',tier:2},
    {id:'19B',name:'App Hardening & Auth',file:'19B_App_Hardening.html',tier:2},
    {id:'20A',name:'Unit Testing',file:'20A_Unit_Testing.html',tier:2},
    {id:'20B',name:'Coroutines & Flow Testing',file:'20B_Coroutines_Flow_Testing.html',tier:2},
    {id:'20C',name:'UI & Network Testing',file:'20C_UI_Network_Testing.html',tier:2},
    {id:'21A',name:'Performance',file:'21A_Performance.html',tier:2},
    {id:'22A',name:'Memory Management',file:'22A_Memory_Management.html',tier:2},
    {id:'23A',name:'Gradle / Build System',file:'23A_Gradle.html',tier:3},
    {id:'24A',name:'Modularization',file:'24A_Modularization.html',tier:2},
    {id:'25A',name:'CI/CD',file:'25A_CICD.html',tier:2},
    {id:'26A',name:'Code Quality',file:'26A_Code_Quality.html',tier:2},
    {id:'27A',name:'Permissions',file:'27A_Permissions.html',tier:3},
    {id:'28A',name:'RecyclerView',file:'28A_RecyclerView.html',tier:3},
    {id:'28B',name:'Legacy UI',file:'28B_Legacy_UI.html',tier:3},
    {id:'29A',name:'Paging 3',file:'29A_Paging3.html',tier:3},
    {id:'30A',name:'System Design: Offline Catalog',file:'30A_System_Design_Offline_Catalog.html',tier:1},
    {id:'30B',name:'System Design: Login / Auth',file:'30B_System_Design_Login_Auth.html',tier:1},
    {id:'30C',name:'System Design: Shopping Cart',file:'30C_System_Design_Shopping_Cart.html',tier:1},
    {id:'30D',name:'System Design: Chat App',file:'30D_System_Design_Chat.html',tier:1},
    {id:'30E',name:'System Design: Push Notifications',file:'30E_System_Design_Push_Notifications.html',tier:1},
    {id:'30F',name:'System Design: Image Feed',file:'30F_System_Design_Image_Feed.html',tier:1},
    {id:'30G',name:'System Design: Large-scale App',file:'30G_System_Design_Large_Scale_App.html',tier:1},
    {id:'31A',name:'Firebase',file:'31A_Firebase.html',tier:3},
    {id:'32A',name:'App Release',file:'32A_App_Release.html',tier:3},
    {id:'33A',name:'Debugging Scenarios',file:'33A_Debugging_Scenarios.html',tier:1},
    {id:'33B',name:'Data & Concurrency Scenarios',file:'33B_Data_Concurrency_Scenarios.html',tier:1},
    {id:'33C',name:'Platform & Scale Scenarios',file:'33C_Platform_Scale_Scenarios.html',tier:1},
    {id:'34A',name:'Strings Coding',file:'34A_Strings_Coding.html',tier:1},
    {id:'34B',name:'Arrays & Collections',file:'34B_Arrays_Collections_Coding.html',tier:1},
    {id:'34C',name:'Math & Recursion',file:'34C_Math_Recursion_Coding.html',tier:1},
    {id:'34D',name:'Data Structures & Search',file:'34D_Data_Structures_Search.html',tier:1},
    {id:'34E',name:'Android Coding',file:'34E_Android_Coding.html',tier:1},
    {id:'35A',name:'Behavioral & Senior Leadership',file:'35A_Behavioral_Senior_Leadership.html',tier:1},
    {id:'36A',name:'AI Integration in Android',file:'36A_AI_Integration_Android.html',tier:1},
    {id:'36B',name:'AI Developer Tools',file:'36B_AI_Dev_Tools.html',tier:1},
    {id:'37A',name:'Jetpack Compose Animation',file:'37A_Compose_Animation.html',tier:1},
    {id:'38A',name:'Kotlin Multiplatform (KMP/KMM)',file:'38A_Kotlin_Multiplatform.html',tier:2},
    {id:'39A',name:'Android Accessibility',file:'39A_Accessibility.html',tier:2},
    {id:'40A',name:'Android New APIs (12–16)',file:'40A_Android_New_APIs.html',tier:1},
    {id:'41A',name:'Advanced Android Debugging',file:'41A_Advanced_Debugging.html',tier:2},
  ];

  // ── Progress helpers ─────────────────────────────────────────────
  const PK = 'aip_v2_progress';
  function loadProg() {
    try { return JSON.parse(localStorage.getItem(PK) || '{}'); } catch { return {}; }
  }
  function saveProg(p) { localStorage.setItem(PK, JSON.stringify(p)); }
  function getTP(id) {
    return loadProg()[id] || { status: 'not_started', score: null, sectionsVisited: [] };
  }
  function setTP(id, upd) {
    const p = loadProg();
    p[id] = { ...getTP(id), ...upd };
    saveProg(p);
  }
  function getOverall() {
    const p = loadProg();
    const total = TOPICS.length;
    const done = TOPICS.filter(t => p[t.id] && p[t.id].status === 'completed').length;
    const scores = TOPICS.map(t => p[t.id] && p[t.id].score).filter(Boolean);
    const avg = scores.length ? Math.round(scores.reduce((a,b)=>a+b,0)/scores.length) : 0;
    return { total, done, avg, pct: Math.round((done/total)*100) };
  }

  // ── Detect current topic ─────────────────────────────────────────
  const curFile = window.location.pathname.split('/').pop() || '';
  const curIdx  = TOPICS.findIndex(t => t.file === curFile);
  const curTopic = curIdx >= 0 ? TOPICS[curIdx] : null;
  const prevTopic = curIdx > 0 ? TOPICS[curIdx - 1] : null;
  const nextTopic = curIdx >= 0 && curIdx < TOPICS.length - 1 ? TOPICS[curIdx + 1] : null;

  // ══════════════════════════════════════════════════════════════════
  //  SCROLL-MODE PATCH (v4 — all bugs fixed)
  // ══════════════════════════════════════════════════════════════════
  function patchScrollMode() {

    // ── 1. Hide OLD inline progress bar (Format A files have one) ──
    //      and prevent show()/showSection() from hiding sections
    const killStyle = document.createElement('style');
    killStyle.textContent = `
      /* Hide the original topic-page progress bar — shared.js replaces it */
      .progress-bar { display: none !important; }
      /* Kill the show/hide section animation — all sections stay visible */
      .section, .section.active { display: block !important; opacity: 1 !important; animation: none !important; }
      section[id] { display: block !important; opacity: 1 !important; }
      /* Dividers between sections for visual separation */
      .section + .section, section[id] + section[id] { border-top: 1px solid #2e3149; }
      /* Kill nav-buttons (prev/next inside content) — scroll replaces them */
      .nav-buttons { display: none !important; }
      /* Sidebar: sticky on desktop, full viewport height, internal scroll */
      .sidebar { position: sticky !important; top: 52px !important; height: calc(100vh - 52px) !important; overflow-y: auto !important; flex-shrink: 0 !important; }
      nav:not(.topnav):not(#aip-topbar) { position: sticky !important; top: 52px !important; height: calc(100vh - 52px) !important; overflow-y: auto !important; flex-shrink: 0 !important; }
      /* Layout: flex row, main scrolls naturally with page */
      .layout { display: flex !important; align-items: flex-start !important; }
      /* CRITICAL FIX: main must NOT be the scroll container — page body scrolls */
      .main, main { overflow: visible !important; height: auto !important; }
      /* Section padding */
      .section { padding: 40px 48px !important; max-width: 900px !important; }
      section[id] { padding: 40px 48px !important; }
      /* Active sidebar item */
      .aip-nav-active { background: rgba(124,106,247,0.18) !important; color: #7c6af7 !important; }
      .aip-nav-active .nav-num { background: rgba(124,106,247,0.28) !important; color: #7c6af7 !important; }
      /* Nav dot — section visited indicator */
      .aip-nav-dot { width:7px; height:7px; border-radius:50%; background:#2e3149; flex-shrink:0; margin-left:auto; transition:background 0.25s; display:inline-block; }
      .aip-nav-dot.visited { background:#3ecf8e; }
      .nav-item { display:flex !important; align-items:center !important; }
      /* Scroll progress bar at very top */
      #aip-scroll-progress { position:fixed; top:0; left:0; right:0; height:3px; background:#2e3149; z-index:10000; pointer-events:none; }
      #aip-scroll-progress-fill { height:100%; background:linear-gradient(90deg,#7c6af7,#3ecf8e); width:0%; transition:width 0.1s linear; }
      /* Hidden offset anchors for scroll-to with topbar offset */
      .aip-anc { display:block; position:relative; top:-70px; visibility:hidden; pointer-events:none; height:0; }
      /* Bottom "next topic" banner */
      #aip-next-banner { margin:32px 48px 60px; max-width:900px; background:linear-gradient(135deg,#1a1d27 0%,#1d1538 100%); border:1px solid rgba(124,106,247,0.35); border-radius:16px; padding:28px 32px; display:flex; align-items:center; justify-content:space-between; gap:20px; flex-wrap:wrap; }
      .nb-text { font-size:15px; color:#e2e4f0; font-weight:600; }
      .nb-sub { font-size:13px; color:#8b90b8; margin-top:4px; }
      .nb-btns { display:flex; gap:12px; flex-wrap:wrap; }
      .nb-btn { padding:10px 20px; border-radius:8px; font-size:14px; font-weight:700; cursor:pointer; border:none; transition:all .15s; font-family:inherit; }
      .nb-done { background:#3ecf8e; color:#0f1117; }
      .nb-done:hover { background:#2db87a; }
      .nb-next { background:#7c6af7; color:#fff; }
      .nb-next:hover { background:#6b5ce7; }
      .nb-home { background:#222535; color:#e2e4f0; border:1px solid #2e3149; }
      .nb-home:hover { background:#2e3149; }
      /* Mobile: full-width sections, sidebar as slide-in drawer */
      @media (max-width: 768px) {
        .section, section[id] { padding:24px 16px !important; }
        #aip-next-banner { margin:24px 16px 48px; padding:20px; }
        .sidebar, nav:not(.topnav) {
          position:fixed !important; left:-270px !important; top:0 !important;
          height:100vh !important; width:260px !important; z-index:9000 !important;
          transition:transform 0.25s ease !important; overflow-y:auto !important;
          background:#1a1d27 !important; box-shadow:4px 0 24px rgba(0,0,0,.6) !important;
        }
        .sidebar.aip-open, nav.aip-open { left:0 !important; }
        #aip-mob-overlay { display:none; position:fixed; inset:0; background:rgba(0,0,0,.5); z-index:8999; }
        #aip-mob-overlay.open { display:block; }
        #aip-mob-fab { display:flex !important; }
      }
      #aip-mob-fab {
        display:none; position:fixed; bottom:22px; left:18px; z-index:9001;
        width:46px; height:46px; border-radius:50%; background:#7c6af7; color:#fff;
        border:none; font-size:19px; cursor:pointer; align-items:center; justify-content:center;
        box-shadow:0 4px 18px rgba(124,106,247,.55); font-family:inherit;
      }
    `;
    document.head.appendChild(killStyle);

    // ── 2. Scroll progress bar (inserted AFTER topbar, which is inserted first) ──
    //      We use setTimeout(0) so topbar is already in DOM
    setTimeout(function() {
      if (!document.getElementById('aip-scroll-progress')) {
        const spBar = document.createElement('div');
        spBar.id = 'aip-scroll-progress';
        spBar.innerHTML = '<div id="aip-scroll-progress-fill"></div>';
        // Insert at top of body
        document.body.insertBefore(spBar, document.body.firstChild);
      }
      window.addEventListener('scroll', function() {
        const fill = document.getElementById('aip-scroll-progress-fill');
        if (!fill) return;
        const scrollTop = window.scrollY;
        const docH = document.documentElement.scrollHeight - window.innerHeight;
        fill.style.width = (docH > 0 ? Math.min((scrollTop / docH) * 100, 100) : 0) + '%';
      }, { passive: true });
    }, 0);

    // ── 3. Collect all section elements (handles Format A and Format B) ──
    function getAllSections() {
      // Format A: div.section with id
      let sects = Array.from(document.querySelectorAll('.section[id]'))
        .filter(s => s.id && s.id !== 'aip-flip-section' && !s.id.startsWith('aip-'));
      // Format B: <section id="..."> (not .section class)
      if (!sects.length) {
        sects = Array.from(document.querySelectorAll('section[id]'))
          .filter(s => s.id && s.id !== 'aip-flip-section' && !s.id.startsWith('aip-'));
      }
      return sects;
    }

    // ── 4. Build sidebar nav → section mapping ──
    //      Strategy: match by onclick content, then by href, then by position index
    function buildNavMap(sections) {
      if (!sections.length) return [];
      const navMap = [];
      const usedNavEls = new Set(); // prevent double-matching

      // All sidebar nav candidates
      const allNavCandidates = Array.from(document.querySelectorAll(
        '.sidebar .nav-item, nav:not(#aip-topbar) a, nav:not(#aip-topbar) button'
      )).filter(el => !el.closest('#aip-topbar'));

      sections.forEach(function(sect, i) {
        // Insert hidden offset anchor at top of section
        if (!document.getElementById('aip-anc-' + sect.id)) {
          const anc = document.createElement('span');
          anc.className = 'aip-anc';
          anc.id = 'aip-anc-' + sect.id;
          sect.insertBefore(anc, sect.firstChild);
        }

        let navEl = null;
        const sid = sect.id;

        // Pass 1: match by onclick containing section id string
        for (let el of allNavCandidates) {
          if (usedNavEls.has(el)) continue;
          const oc = el.getAttribute('onclick') || '';
          if (oc.includes("'" + sid + "'") || oc.includes('"' + sid + '"')) {
            navEl = el; break;
          }
        }

        // Pass 2: match by href anchor
        if (!navEl) {
          for (let el of allNavCandidates) {
            if (usedNavEls.has(el)) continue;
            const href = el.getAttribute('href') || '';
            if (href === '#' + sid) { navEl = el; break; }
          }
        }

        // Pass 3: match by numeric position index in onclick (show('s1',1) → index 1)
        if (!navEl) {
          for (let el of allNavCandidates) {
            if (usedNavEls.has(el)) continue;
            const oc = el.getAttribute('onclick') || '';
            // match `,1)` or `, 1)` where 1 = i+1
            const numMatch = oc.match(/,\s*(\d+)\s*\)/);
            if (numMatch && parseInt(numMatch[1]) === i + 1) {
              navEl = el; break;
            }
          }
        }

        // Pass 4: positional fallback — use unmatched nav candidate at index i
        if (!navEl) {
          const unmatched = allNavCandidates.filter(el => !usedNavEls.has(el));
          if (unmatched[i]) navEl = unmatched[i];
        }

        if (navEl) {
          usedNavEls.add(navEl);
          navMap.push({ navEl, sect });
        }
      });

      return navMap;
    }

    // ── 5. Wire sidebar clicks → smooth scroll ──
    function wireNavClicks(navMap) {
      navMap.forEach(function({ navEl, sect }) {
        // Neutralise the old onclick (show()/showSection()) without losing the element
        navEl.removeAttribute('onclick');
        // For <a> tags, prevent default anchor jump (we handle scroll manually)
        navEl.style.cursor = 'pointer';
        navEl.style.textDecoration = 'none';

        // Add progress dot to nav item
        if (!navEl.querySelector('.aip-nav-dot')) {
          const dot = document.createElement('span');
          dot.className = 'aip-nav-dot';
          dot.dataset.sid = sect.id;
          navEl.appendChild(dot);
        }

        navEl.addEventListener('click', function(e) {
          e.preventDefault();
          e.stopPropagation();
          const topbarEl = document.getElementById('aip-topbar');
          const topbarH = topbarEl ? topbarEl.offsetHeight : 52;
          const rect = sect.getBoundingClientRect();
          const y = rect.top + window.scrollY - topbarH - 8;
          window.scrollTo({ top: Math.max(0, y), behavior: 'smooth' });
          // Close mobile drawer
          closeMobileDrawer();
        });
      });
    }

    // ── 6. Scroll-spy: highlight active nav item as user scrolls ──
    function wireScrollSpy(navMap, sections) {
      if (!navMap.length) return;

      // Single IntersectionObserver — fires when section enters top 40% of viewport
      // rootMargin: shrink top by 60px (below topbar), shrink bottom by 50%
      // So the "active zone" = from topbar to middle of screen
      const obs = new IntersectionObserver(function(entries) {
        entries.forEach(function(entry) {
          const sid = entry.target.id;
          const match = navMap.find(function(m) { return m.sect.id === sid; });
          if (!match) return;

          if (entry.isIntersecting) {
            // Mark this nav item active
            navMap.forEach(function(m) { m.navEl.classList.remove('aip-nav-active'); });
            match.navEl.classList.add('aip-nav-active');

            // Scroll sidebar to keep active item visible
            const sidebar = match.navEl.closest('.sidebar') ||
                            match.navEl.closest('nav:not(#aip-topbar)');
            if (sidebar) {
              const itemOffTop = match.navEl.offsetTop;
              const sbH = sidebar.offsetHeight;
              const sbScroll = sidebar.scrollTop;
              if (itemOffTop < sbScroll + 48 || itemOffTop > sbScroll + sbH - 72) {
                sidebar.scrollTo({ top: Math.max(0, itemOffTop - sbH / 2 + 24), behavior: 'smooth' });
              }
            }

            // Track section as visited for progress
            if (curTopic) {
              const tp = getTP(curTopic.id);
              const visited = new Set(tp.sectionsVisited || []);
              visited.add(sid);
              setTP(curTopic.id, { sectionsVisited: [...visited] });

              // Mark dot visited
              const dot = match.navEl.querySelector('.aip-nav-dot');
              if (dot) dot.classList.add('visited');

              // Auto-complete when all sections seen
              if (visited.size >= sections.length) {
                setTP(curTopic.id, { status: 'completed' });
                updateMiniBar();
                const doneBtn = document.getElementById('tb-done');
                if (doneBtn) { doneBtn.textContent = '✓ Done'; doneBtn.classList.add('done'); }
              }
            }
          }
        });
      }, {
        // Active zone: entries fire when section top crosses 60px–50% of viewport height
        rootMargin: '-60px 0px -50% 0px',
        threshold: 0
      });

      sections.forEach(function(s) { obs.observe(s); });
    }

    // ── 7. Bottom "end of topic" banner ──
    function injectEndBanner() {
      if (document.getElementById('aip-next-banner')) return; // guard duplicates
      const banner = document.createElement('div');
      banner.id = 'aip-next-banner';
      const topicName = nextTopic ? nextTopic.name : null;
      banner.innerHTML =
        '<div>' +
          '<div class="nb-text">\uD83C\uDF89 You\'ve reached the end of this topic!</div>' +
          '<div class="nb-sub">' +
            (topicName
              ? 'Up next: <strong style="color:#7c6af7">' + topicName + '</strong>'
              : "You've completed the full syllabus \u2014 well done!") +
          '</div>' +
        '</div>' +
        '<div class="nb-btns">' +
          '<button class="nb-btn nb-home" id="nb-home-btn">\uD83C\uDFE0 Dashboard</button>' +
          '<button class="nb-btn nb-done" id="nb-done-btn">\u2713 Mark Done</button>' +
          (nextTopic ? '<button class="nb-btn nb-next" id="nb-next-btn">Next: ' + topicName + ' \u2192</button>' : '') +
        '</div>';

      const main = document.querySelector('.main') || document.querySelector('main') || document.body;
      main.appendChild(banner);

      document.getElementById('nb-home-btn').addEventListener('click', function() {
        window.location.href = '../index.html';
      });
      document.getElementById('nb-done-btn').addEventListener('click', function() {
        markDone();
        const b = document.getElementById('nb-done-btn');
        if (b) { b.textContent = '\u2713 Done!'; b.disabled = true; b.style.opacity = '0.7'; }
      });
      if (nextTopic) {
        document.getElementById('nb-next-btn').addEventListener('click', function() {
          window.location.href = nextTopic.file;
        });
      }
    }

    // ── 8. Mobile drawer ──
    function injectMobileDrawer() {
      if (document.getElementById('aip-mob-fab')) return;

      const overlay = document.createElement('div');
      overlay.id = 'aip-mob-overlay';
      document.body.appendChild(overlay);

      const fab = document.createElement('button');
      fab.id = 'aip-mob-fab';
      fab.setAttribute('aria-label', 'Open navigation menu');
      fab.textContent = '\u2630'; // ☰
      document.body.appendChild(fab);

      fab.addEventListener('click', function() {
        const sb = document.querySelector('.sidebar') || document.querySelector('nav:not(#aip-topbar)');
        if (sb) sb.classList.toggle('aip-open');
        overlay.classList.toggle('open');
      });
      overlay.addEventListener('click', closeMobileDrawer);
    }

    function closeMobileDrawer() {
      const sb = document.querySelector('.sidebar') || document.querySelector('nav:not(#aip-topbar)');
      if (sb) sb.classList.remove('aip-open');
      const ov = document.getElementById('aip-mob-overlay');
      if (ov) ov.classList.remove('open');
    }

    // ── Disable show() / showSection() so clicking nav doesn't hide sections ──
    window.show = function() {};
    window.showSection = function() {};

    // ── Run ──
    const sections = getAllSections();
    const navMap = buildNavMap(sections);
    wireNavClicks(navMap);
    wireScrollSpy(navMap, sections);
    injectEndBanner();
    injectMobileDrawer();

    // Set first nav item active on load
    if (navMap.length) navMap[0].navEl.classList.add('aip-nav-active');
  }

  // ── Build top bar ─────────────────────────────────────────────────
  function buildTopBar() {
    if (document.getElementById('aip-topbar')) return;
    const overall = getOverall();
    const tp = curTopic ? getTP(curTopic.id) : null;
    const isDone = tp && tp.status === 'completed';

    const bar = document.createElement('div');
    bar.id = 'aip-topbar';
    const tierColors = { 1: '#f06b6b', 2: '#38d9b4', 3: '#f0a04b' };
    const tierColor = curTopic ? (tierColors[curTopic.tier] || '#7c6af7') : '#7c6af7';

    bar.innerHTML =
      '<a class="tb-home" href="../index.html">' +
        '<span class="tb-logo">\uD83E\uDD16</span>' +
        '<span class="tb-name">Android Prep</span>' +
      '</a>' +
      (curTopic
        ? '<span class="tb-topic-id" style="color:' + tierColor + ';background:' + tierColor + '22;border-color:' + tierColor + '44">' + curTopic.id + '</span>' +
          '<span class="tb-topic-name">' + curTopic.name + '</span>'
        : '') +
      '<div class="tb-progress-wrap">' +
        '<div class="tb-mini-bar"><div class="tb-mini-fill" style="width:' + overall.pct + '%"></div></div>' +
        '<span>' + overall.done + '/' + overall.total + '</span>' +
      '</div>' +
      '<div class="tb-actions">' +
        '<button class="tb-btn prev-next" id="tb-prev" title="Previous topic"' + (!prevTopic ? ' disabled style="opacity:.35"' : '') + '>\u2039</button>' +
        '<button class="tb-btn prev-next" id="tb-next" title="Next topic"' + (!nextTopic ? ' disabled style="opacity:.35"' : '') + '>\u203a</button>' +
        '<button class="tb-btn' + (isDone ? ' done' : '') + '" id="tb-done">' + (isDone ? '\u2713 Done' : '\u25ef Mark Done') + '</button>' +
        '<button class="tb-btn" id="tb-score" title="Rate your understanding">\uD83C\uDFAF Score</button>' +
        '<button class="tb-btn" id="tb-pdf" title="Download as PDF">\u2193 PDF</button>' +
      '</div>';

    document.body.insertBefore(bar, document.body.firstChild);
    document.body.classList.add('aip-injected');

    if (prevTopic) document.getElementById('tb-prev').addEventListener('click', function() { window.location.href = prevTopic.file; });
    if (nextTopic) document.getElementById('tb-next').addEventListener('click', function() { window.location.href = nextTopic.file; });
    document.getElementById('tb-done').addEventListener('click', markDone);
    document.getElementById('tb-score').addEventListener('click', openScoreModal);
    document.getElementById('tb-pdf').addEventListener('click', function() { window.print(); });
  }

  function markDone() {
    if (!curTopic) return;
    setTP(curTopic.id, { status: 'completed' });
    const btn = document.getElementById('tb-done');
    if (btn) { btn.textContent = '\u2713 Done'; btn.classList.add('done'); }
    updateMiniBar();
    showProgressBanner();
  }

  function updateMiniBar() {
    const overall = getOverall();
    const fill = document.querySelector('.tb-mini-fill');
    const label = document.querySelector('.tb-progress-wrap span');
    if (fill) fill.style.width = overall.pct + '%';
    if (label) label.textContent = overall.done + '/' + overall.total;
  }

  // ── Score modal ───────────────────────────────────────────────────
  function openScoreModal() {
    const existing = document.getElementById('aip-score-modal');
    if (existing) existing.remove();

    const modal = document.createElement('div');
    modal.id = 'aip-score-modal';
    modal.style.cssText = 'position:fixed;inset:0;z-index:99999;background:rgba(0,0,0,.75);backdrop-filter:blur(6px);display:flex;align-items:center;justify-content:center;font-family:"Inter",sans-serif;';

    const opts = [
      {score:25,emoji:'\uD83D\uDE15',label:'Needs Review',sub:'0\u201325%',col:'#ff6b6b'},
      {score:50,emoji:'\uD83E\uDD14',label:'Getting There',sub:'26\u201350%',col:'#f0a04b'},
      {score:75,emoji:'\uD83D\uDE0A',label:'Good Grasp',sub:'51\u201375%',col:'#38d9b4'},
      {score:100,emoji:'\uD83D\uDE80',label:'Interview Ready',sub:'76\u2013100%',col:'#7c6af7'},
    ];

    modal.innerHTML =
      '<div style="background:#1a1d27;border:1px solid #2e3149;border-radius:20px;padding:36px;max-width:400px;width:90%;text-align:center;box-shadow:0 20px 60px rgba(0,0,0,.6);">' +
        '<div style="font-size:32px;margin-bottom:10px">\uD83C\uDFAF</div>' +
        '<h2 style="font-size:20px;font-weight:800;color:#e2e4f0;margin-bottom:8px">Rate Your Understanding</h2>' +
        '<p style="font-size:13px;color:#8b90b8;margin-bottom:24px">How well do you know <strong style="color:#7c6af7">' + (curTopic ? curTopic.name : 'this topic') + '</strong>?</p>' +
        '<div style="display:grid;grid-template-columns:1fr 1fr;gap:10px;margin-bottom:20px">' +
          opts.map(function(o) {
            return '<div data-score="' + o.score + '" class="aip-score-opt" style="background:' + o.col + '18;border:2px solid ' + o.col + '44;border-radius:12px;padding:14px 8px;cursor:pointer;transition:all .15s;">' +
              '<div style="font-size:26px;margin-bottom:5px">' + o.emoji + '</div>' +
              '<div style="font-size:13px;font-weight:700;color:' + o.col + '">' + o.label + '</div>' +
              '<div style="font-size:11px;color:#8b90b8;margin-top:2px">' + o.sub + '</div>' +
            '</div>';
          }).join('') +
        '</div>' +
        '<div id="aip-score-skip" style="font-size:13px;color:#8b90b8;cursor:pointer;text-decoration:underline">Skip for now</div>' +
      '</div>';

    document.body.appendChild(modal);

    modal.querySelectorAll('.aip-score-opt').forEach(function(opt) {
      opt.addEventListener('mouseover', function() { opt.style.transform = 'scale(1.03)'; });
      opt.addEventListener('mouseout',  function() { opt.style.transform = ''; });
      opt.addEventListener('click', function() {
        const score = parseInt(opt.dataset.score);
        if (curTopic) { setTP(curTopic.id, { score, status: 'completed' }); markDone(); }
        modal.remove();
        showProgressBanner(score);
      });
    });

    document.getElementById('aip-score-skip').addEventListener('click', function() { modal.remove(); });
    modal.addEventListener('click', function(e) { if (e.target === modal) modal.remove(); });
  }

  // ── Progress banner ───────────────────────────────────────────────
  function showProgressBanner(score) {
    const overall = getOverall();
    const existing = document.getElementById('aip-progress-banner');
    if (existing) existing.remove();

    const banner = document.createElement('div');
    banner.id = 'aip-progress-banner';
    banner.style.display = 'block';

    const scoreVal = score || (curTopic ? getTP(curTopic.id).score : null);
    const fillColor = !scoreVal ? '#7c6af7' : scoreVal >= 75 ? '#3ecf8e' : scoreVal >= 50 ? '#f5c842' : '#ff6b6b';
    const grade = !scoreVal ? '' : scoreVal >= 75 ? '\uD83D\uDE80 Interview Ready!' : scoreVal >= 50 ? '\uD83D\uDCD6 Keep practicing' : '\uD83D\uDD04 Review again';

    banner.innerHTML =
      '<button class="pb-close" id="pb-close-btn">\u00D7</button>' +
      '<div class="pb-title">\u2713 Topic Complete</div>' +
      '<div class="pb-score-row">' +
        '<div class="pb-score">' + overall.pct + '%</div>' +
        '<div class="pb-grade">Overall progress<br>' + overall.done + ' of ' + overall.total + ' done' +
          (scoreVal ? '<br><span style="color:' + fillColor + '">' + grade + '</span>' : '') +
        '</div>' +
      '</div>' +
      '<div class="pb-bar"><div class="pb-fill" style="width:' + overall.pct + '%;background:' + fillColor + '"></div></div>' +
      '<div class="pb-status"><span>' + overall.done + ' completed</span><span>' + (overall.total - overall.done) + ' remaining</span></div>';

    document.body.appendChild(banner);
    document.getElementById('pb-close-btn').addEventListener('click', function() { banner.remove(); });
    setTimeout(function() { if (document.body.contains(banner)) banner.remove(); }, 6000);
  }

  // ── Mark topic as started ─────────────────────────────────────────
  function markStarted() {
    if (!curTopic) return;
    const tp = getTP(curTopic.id);
    if (tp.status === 'not_started') setTP(curTopic.id, { status: 'in_progress' });
  }

  // ── Flip Card Quiz ────────────────────────────────────────────────
  function buildFlipCards() {
    const cards = [];

    // Format 1: .quiz-q / .quiz-a
    document.querySelectorAll('.quiz-q').forEach(function(qEl, i) {
      const diffEl = qEl.querySelector('.diff-easy,.diff-badge,.diff-medium,.diff-hard');
      const diffText = diffEl ? diffEl.textContent.toLowerCase() : '';
      const diff = diffText.includes('easy') || diffText.includes('basic') ? 'easy'
                 : diffText.includes('hard') || diffText.includes('senior') ? 'hard' : 'medium';
      const qText = (qEl.querySelector('.quiz-q-text') || qEl).innerText || '';
      const aEl = qEl.nextElementSibling;
      const aText = aEl && aEl.classList.contains('quiz-a') ? aEl.innerText : '';
      if (qText.trim().length > 5) cards.push({ q: qText.trim(), a: aText.trim(), diff, index: i });
    });

    // Format 2: <details><summary>
    if (!cards.length) {
      document.querySelectorAll('details').forEach(function(det, i) {
        const sumEl = det.querySelector('summary');
        const ansEl = det.querySelector('.ans');
        if (!sumEl) return;
        const labelEl = sumEl.querySelector('.q-label,.q-basic,.q-mid,.q-senior');
        const labelTxt = labelEl ? labelEl.textContent.toLowerCase() : '';
        const diff = labelTxt.includes('basic') ? 'easy' : labelTxt.includes('senior') ? 'hard' : 'medium';
        const qText = sumEl.innerText.replace(labelEl ? labelEl.innerText : '', '').trim();
        const aText = ansEl ? ansEl.innerText.trim() : '';
        if (qText.length > 5) cards.push({ q: qText, a: aText, diff, index: i });
      });
    }

    if (!cards.length) return;

    const csKey = 'aip_cards_' + (curTopic ? curTopic.id : 'unk');
    let cardState = {};
    try { cardState = JSON.parse(localStorage.getItem(csKey) || '{}'); } catch {}
    function saveCS() { localStorage.setItem(csKey, JSON.stringify(cardState)); }

    const knownC = Object.values(cardState).filter(function(v) { return v === 'known'; }).length;
    const reviewC = Object.values(cardState).filter(function(v) { return v === 'review'; }).length;

    const section = document.createElement('div');
    section.className = 'aip-flip-section';
    section.id = 'aip-flip-section';
    section.innerHTML =
      '<div class="aip-flip-header">' +
        '<h3>\uD83C\uDCCF Flashcard Review <span style="font-size:12px;color:#8b90b8;font-weight:500">(' + cards.length + ' cards \u2014 tap to flip)</span></h3>' +
        '<div class="aip-flip-controls">' +
          '<div class="aip-search-wrap"><input class="aip-flip-search" id="aip-flip-search" placeholder="Search cards\u2026" type="text"/></div>' +
          '<div class="aip-filter-btns">' +
            '<button class="aip-filter-btn active" data-filter="all">All</button>' +
            '<button class="aip-filter-btn easy" data-filter="easy">Easy</button>' +
            '<button class="aip-filter-btn medium" data-filter="medium">Med</button>' +
            '<button class="aip-filter-btn hard" data-filter="hard">Hard</button>' +
            '<button class="aip-filter-btn" data-filter="review" style="color:#ff6b6b">Review</button>' +
          '</div>' +
        '</div>' +
      '</div>' +
      '<div class="aip-quiz-stats">' +
        '<div class="aip-stat-chip"><span class="dot dot-all"></span>' + cards.length + ' total</div>' +
        '<div class="aip-stat-chip" id="aip-known-stat"><span class="dot dot-known"></span>' + knownC + ' known</div>' +
        '<div class="aip-stat-chip" id="aip-review-stat"><span class="dot dot-review"></span>' + reviewC + ' to review</div>' +
        '<div class="aip-stat-chip" id="aip-pct-stat" style="margin-left:auto;color:#7c6af7">' + (cards.length ? Math.round((knownC/cards.length)*100) : 0) + '% mastered</div>' +
      '</div>' +
      '<div class="aip-flip-grid" id="aip-flip-grid"></div>';

    // Append after last quiz section or inside main
    const quizEl = document.querySelector('#s9') || document.querySelector('[id="quiz"]') ||
                   document.querySelector('.section:last-of-type') || document.querySelector('section:last-of-type');
    if (quizEl) {
      quizEl.insertAdjacentElement('afterend', section);
    } else {
      (document.querySelector('.main') || document.querySelector('main') || document.body).appendChild(section);
    }

    let activeFilter = 'all', searchQuery = '';

    function renderCards() {
      const grid = document.getElementById('aip-flip-grid');
      if (!grid) return;
      const filtered = cards.filter(function(c) {
        const mf = activeFilter === 'all' ? true : activeFilter === 'review' ? cardState[c.index] === 'review' : c.diff === activeFilter;
        const ms = !searchQuery || c.q.toLowerCase().includes(searchQuery) || c.a.toLowerCase().includes(searchQuery);
        return mf && ms;
      });
      if (!filtered.length) {
        grid.innerHTML = '<div class="aip-flip-empty" style="grid-column:1/-1;text-align:center;padding:40px;color:#8b90b8"><div style="font-size:32px;margin-bottom:8px">\uD83D\uDD0D</div>No cards match. <span onclick="resetFilter()" style="color:#7c6af7;cursor:pointer;text-decoration:underline">Clear filters</span></div>';
        return;
      }
      grid.innerHTML = filtered.map(function(c) {
        const isKnown = cardState[c.index] === 'known';
        return '<div class="aip-flip-card' + (isKnown ? ' aip-card-marked-known' : '') + '" data-idx="' + c.index + '" data-diff="' + c.diff + '" onclick="flipCard(this)">' +
          '<div class="aip-flip-inner">' +
            '<div class="aip-flip-front">' +
              '<div class="q-text">' + escHtml(c.q) + '</div>' +
              '<div class="aip-flip-footer"><span class="aip-diff-tag diff-' + c.diff + '">' + c.diff + '</span><span class="flip-hint">\uD83D\uDC46 tap to reveal</span></div>' +
            '</div>' +
            '<div class="aip-flip-back">' +
              '<div class="a-text">' + (escHtml(c.a) || '<em style="color:#8b90b8">See topic content</em>') + '</div>' +
              '<div class="aip-flip-footer">' +
                '<div class="aip-card-actions" onclick="event.stopPropagation()">' +
                  '<button class="aip-know-btn" onclick="markCard(' + c.index + ',\'known\')">\u2713 Got it</button>' +
                  '<button class="aip-review-btn" onclick="markCard(' + c.index + ',\'review\')">\u21A9 Review</button>' +
                '</div>' +
                '<span class="flip-hint" style="color:#7c6af7">\uD83D\uDC46 tap to close</span>' +
              '</div>' +
            '</div>' +
          '</div>' +
        '</div>';
      }).join('');
    }

    function updateFlipStats() {
      const kn = Object.values(cardState).filter(function(v) { return v === 'known'; }).length;
      const rv = Object.values(cardState).filter(function(v) { return v === 'review'; }).length;
      const e1 = document.getElementById('aip-known-stat');
      const e2 = document.getElementById('aip-review-stat');
      const e3 = document.getElementById('aip-pct-stat');
      if (e1) e1.innerHTML = '<span class="dot dot-known"></span>' + kn + ' known';
      if (e2) e2.innerHTML = '<span class="dot dot-review"></span>' + rv + ' to review';
      if (e3) e3.textContent = (cards.length ? Math.round((kn/cards.length)*100) : 0) + '% mastered';
    }

    window.flipCard = function(el) { el.classList.toggle('flipped'); };
    window.markCard = function(idx, state) {
      cardState[idx] = state;
      saveCS();
      updateFlipStats();
      const cardEl = document.querySelector('.aip-flip-card[data-idx="' + idx + '"]');
      if (cardEl) {
        cardEl.classList.toggle('aip-card-marked-known', state === 'known');
        if (state === 'known') cardEl.classList.remove('flipped');
      }
      const kn = Object.values(cardState).filter(function(v) { return v === 'known'; }).length;
      if (curTopic && cards.length && kn / cards.length >= 0.8) {
        setTP(curTopic.id, { status: 'completed' });
        updateMiniBar();
        const btn = document.getElementById('tb-done');
        if (btn && !btn.classList.contains('done')) { btn.textContent = '\u2713 Done'; btn.classList.add('done'); }
      }
    };
    window.resetFilter = function() {
      activeFilter = 'all'; searchQuery = '';
      const inp = document.getElementById('aip-flip-search');
      if (inp) inp.value = '';
      section.querySelectorAll('.aip-filter-btn').forEach(function(b) { b.classList.toggle('active', b.dataset.filter === 'all'); });
      renderCards();
    };

    section.querySelectorAll('.aip-filter-btn').forEach(function(btn) {
      btn.addEventListener('click', function() {
        section.querySelectorAll('.aip-filter-btn').forEach(function(b) { b.classList.remove('active'); });
        btn.classList.add('active');
        activeFilter = btn.dataset.filter;
        renderCards();
      });
    });

    const searchInp = document.getElementById('aip-flip-search');
    if (searchInp) {
      searchInp.addEventListener('input', function(e) {
        searchQuery = e.target.value.toLowerCase().trim();
        renderCards();
      });
    }

    renderCards();
  }

  function escHtml(str) {
    if (!str) return '';
    return str.replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;').replace(/"/g,'&quot;');
  }

  // ── Init ──────────────────────────────────────────────────────────
  function init() {
    markStarted();
    buildTopBar();          // topbar first — adds body padding-top via shared.css
    patchScrollMode();      // then scroll mode — uses topbar height for offsets

    const schedule = window.requestIdleCallback || function(fn) { setTimeout(fn, 400); };
    schedule(buildFlipCards);
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }

})();
