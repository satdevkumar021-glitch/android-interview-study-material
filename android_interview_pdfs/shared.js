/**
 * ANDROID INTERVIEW PREP — shared.js
 * Injected into every topic page.
 * Handles:
 *   1. Top navigation bar with Home link, prev/next, mark done
 *   2. Progress tracking (localStorage)
 *   3. Flip-card quiz enhancement (replaces/wraps quiz section)
 *   4. Section visit tracking
 *   5. Progress banner
 */

(function () {
  'use strict';

  // ── Google Fonts ────────────────────────────────────────────────
  const fontLink = document.createElement('link');
  fontLink.rel = 'stylesheet';
  fontLink.href = 'https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&family=JetBrains+Mono:wght@400;500&display=swap';
  document.head.appendChild(fontLink);

  // ── Shared CSS ──────────────────────────────────────────────────
  const cssLink = document.createElement('link');
  cssLink.rel = 'stylesheet';
  cssLink.href = 'shared.css';
  document.head.appendChild(cssLink);

  // ── Syllabus map (id → {prev, next, name, tier}) ────────────────
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
  ];

  // ── Progress helpers ────────────────────────────────────────────
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

  // ── Detect current topic ────────────────────────────────────────
  const curFile = window.location.pathname.split('/').pop() || '';
  const curIdx  = TOPICS.findIndex(t => t.file === curFile);
  const curTopic = curIdx >= 0 ? TOPICS[curIdx] : null;
  const prevTopic = curIdx > 0 ? TOPICS[curIdx - 1] : null;
  const nextTopic = curIdx >= 0 && curIdx < TOPICS.length - 1 ? TOPICS[curIdx + 1] : null;

  // ── Build top bar ───────────────────────────────────────────────
  function buildTopBar() {
    const overall = getOverall();
    const tp = curTopic ? getTP(curTopic.id) : null;
    const isDone = tp && tp.status === 'completed';

    const bar = document.createElement('div');
    bar.id = 'aip-topbar';
    const tierColors = { 1: '#f06b6b', 2: '#38d9b4', 3: '#f0a04b' };
    const tierColor = curTopic ? (tierColors[curTopic.tier] || '#7c6af7') : '#7c6af7';

    bar.innerHTML = `
      <a class="tb-home" href="../index.html">
        <span class="tb-logo">🤖</span>
        <span class="tb-name">Android Prep</span>
      </a>
      ${curTopic ? `
        <span class="tb-topic-id" style="color:${tierColor};background:${tierColor}22;border-color:${tierColor}44">${curTopic.id}</span>
        <span class="tb-topic-name">${curTopic.name}</span>
      ` : ''}
      <div class="tb-progress-wrap">
        <div class="tb-mini-bar">
          <div class="tb-mini-fill" style="width:${overall.pct}%"></div>
        </div>
        <span>${overall.done}/${overall.total}</span>
      </div>
      <div class="tb-actions">
        <button class="tb-btn prev-next" id="tb-prev" title="Previous topic" ${!prevTopic?'disabled style="opacity:.35"':''}>‹</button>
        <button class="tb-btn prev-next" id="tb-next" title="Next topic" ${!nextTopic?'disabled style="opacity:.35"':''}>›</button>
        <button class="tb-btn ${isDone?'done':''}" id="tb-done">
          ${isDone ? '✓ Done' : '◯ Mark Done'}
        </button>
        <button class="tb-btn" id="tb-score" title="Rate your understanding">🎯 Score</button>
        <button class="tb-btn" id="tb-pdf" title="Download as PDF">⬇ PDF</button>
      </div>
    `;
    document.body.insertBefore(bar, document.body.firstChild);
    document.body.classList.add('aip-injected');

    // Wire buttons
    if (prevTopic) {
      document.getElementById('tb-prev').onclick = () => window.location.href = prevTopic.file;
    }
    if (nextTopic) {
      document.getElementById('tb-next').onclick = () => window.location.href = nextTopic.file;
    }
    document.getElementById('tb-done').onclick = markDone;
    document.getElementById('tb-score').onclick = openScoreModal;
    document.getElementById('tb-pdf').onclick = () => window.print();
  }

  function markDone() {
    if (!curTopic) return;
    setTP(curTopic.id, { status: 'completed' });
    const btn = document.getElementById('tb-done');
    if (btn) { btn.textContent = '✓ Done'; btn.classList.add('done'); }
    updateMiniBar();
    showProgressBanner();
  }

  function updateMiniBar() {
    const overall = getOverall();
    const fill = document.querySelector('.tb-mini-fill');
    const label = document.querySelector('.tb-progress-wrap span');
    if (fill) fill.style.width = overall.pct + '%';
    if (label) label.textContent = `${overall.done}/${overall.total}`;
  }

  // ── Score modal ─────────────────────────────────────────────────
  function openScoreModal() {
    const existing = document.getElementById('aip-score-modal');
    if (existing) { existing.remove(); }

    const modal = document.createElement('div');
    modal.id = 'aip-score-modal';
    modal.style.cssText = `
      position:fixed;inset:0;z-index:99999;
      background:rgba(0,0,0,.75);backdrop-filter:blur(6px);
      display:flex;align-items:center;justify-content:center;
      font-family:'Inter',sans-serif;
    `;
    modal.innerHTML = `
      <div style="
        background:#1a1d27;border:1px solid #2e3149;border-radius:20px;
        padding:36px;max-width:400px;width:90%;text-align:center;
        box-shadow:0 20px 60px rgba(0,0,0,.6);
      ">
        <div style="font-size:32px;margin-bottom:10px">🎯</div>
        <h2 style="font-size:20px;font-weight:800;color:#e2e4f0;margin-bottom:8px">
          Rate Your Understanding
        </h2>
        <p style="font-size:13px;color:#8b90b8;margin-bottom:24px">
          How well do you know <strong style="color:#7c6af7">${curTopic ? curTopic.name : 'this topic'}</strong>?
        </p>
        <div style="display:grid;grid-template-columns:1fr 1fr;gap:10px;margin-bottom:20px">
          ${[
            {score:25,emoji:'😕',label:'Needs Review',sub:'0–25%',col:'#ff6b6b'},
            {score:50,emoji:'🤔',label:'Getting There',sub:'26–50%',col:'#f0a04b'},
            {score:75,emoji:'😊',label:'Good Grasp',sub:'51–75%',col:'#38d9b4'},
            {score:100,emoji:'🚀',label:'Interview Ready',sub:'76–100%',col:'#7c6af7'},
          ].map(o => `
            <div data-score="${o.score}" class="aip-score-opt" style="
              background:${o.col}18;border:2px solid ${o.col}44;border-radius:12px;
              padding:14px 8px;cursor:pointer;transition:all .15s;
            " onmouseover="this.style.borderColor='${o.col}'" onmouseout="this.style.borderColor='${o.col}44'">
              <div style="font-size:26px;margin-bottom:5px">${o.emoji}</div>
              <div style="font-size:13px;font-weight:700;color:${o.col}">${o.label}</div>
              <div style="font-size:11px;color:#8b90b8;margin-top:2px">${o.sub}</div>
            </div>
          `).join('')}
        </div>
        <div id="aip-score-skip" style="font-size:13px;color:#8b90b8;cursor:pointer;text-decoration:underline">
          Skip for now
        </div>
      </div>
    `;

    document.body.appendChild(modal);

    modal.querySelectorAll('.aip-score-opt').forEach(opt => {
      opt.addEventListener('click', () => {
        const score = parseInt(opt.dataset.score);
        if (curTopic) {
          setTP(curTopic.id, { score, status: 'completed' });
          markDone();
        }
        modal.remove();
        showProgressBanner(score);
      });
    });

    document.getElementById('aip-score-skip').onclick = () => modal.remove();
    modal.addEventListener('click', e => { if (e.target === modal) modal.remove(); });
  }

  // ── Progress banner ─────────────────────────────────────────────
  function showProgressBanner(score) {
    const overall = getOverall();
    const banner = document.createElement('div');
    banner.id = 'aip-progress-banner';
    banner.style.display = 'block';

    const scoreVal = score || (curTopic ? getTP(curTopic.id).score : null);
    const fillColor = !scoreVal ? '#7c6af7' :
      scoreVal >= 75 ? '#3ecf8e' : scoreVal >= 50 ? '#f5c842' : '#ff6b6b';
    const grade = !scoreVal ? '' :
      scoreVal >= 75 ? '🚀 Interview Ready!' : scoreVal >= 50 ? '📖 Keep practicing' : '🔄 Review again';

    banner.innerHTML = `
      <button class="pb-close" onclick="this.parentElement.remove()">×</button>
      <div class="pb-title">✓ Topic Complete</div>
      <div class="pb-score-row">
        <div class="pb-score">${overall.pct}%</div>
        <div class="pb-grade">
          Overall progress<br>
          ${overall.done} of ${overall.total} done
          ${scoreVal ? `<br><span style="color:${fillColor}">${grade}</span>` : ''}
        </div>
      </div>
      <div class="pb-bar">
        <div class="pb-fill" style="width:${overall.pct}%;background:${fillColor}"></div>
      </div>
      <div class="pb-status">
        <span>${overall.done} completed</span>
        <span>${overall.total - overall.done} remaining</span>
      </div>
    `;

    const existing = document.getElementById('aip-progress-banner');
    if (existing) existing.remove();
    document.body.appendChild(banner);
    setTimeout(() => { if (document.getElementById('aip-progress-banner') === banner) banner.remove(); }, 6000);
  }

  // ── Mark topic as started on page load ──────────────────────────
  function markStarted() {
    if (!curTopic) return;
    const tp = getTP(curTopic.id);
    if (tp.status === 'not_started') {
      setTP(curTopic.id, { status: 'in_progress' });
    }
  }

  // ── Section visit tracking ──────────────────────────────────────
  function trackSectionVisits() {
    if (!curTopic) return;
    const sections = document.querySelectorAll('.section[id]');
    if (!sections.length) return;

    const obs = new IntersectionObserver(entries => {
      entries.forEach(entry => {
        if (entry.isIntersecting) {
          const sid = entry.target.id;
          const tp = getTP(curTopic.id);
          const visited = new Set(tp.sectionsVisited || []);
          visited.add(sid);
          setTP(curTopic.id, { sectionsVisited: [...visited] });
          // Auto-complete if all 9 sections visited
          if (visited.size >= 9) {
            setTP(curTopic.id, { status: 'completed' });
            updateMiniBar();
            const btn = document.getElementById('tb-done');
            if (btn) { btn.textContent = '✓ Done'; btn.classList.add('done'); }
          }
        }
      });
    }, { threshold: 0.2 });

    sections.forEach(s => obs.observe(s));
  }

  // ── Flip Card Quiz ──────────────────────────────────────────────
  function buildFlipCards() {
    // Collect quiz questions from BOTH formats:
    // Format 1: .quiz-q / .quiz-a  (77 files)
    // Format 2: <details><summary> (15 files)
    const cards = [];

    // Format 1
    document.querySelectorAll('.quiz-q').forEach((qEl, i) => {
      const diffEl = qEl.querySelector('.diff-easy,.diff-badge');
      const diffText = diffEl ? diffEl.textContent.toLowerCase() : '';
      const diff = diffText.includes('easy') || diffText.includes('basic') ? 'easy'
                 : diffText.includes('hard') || diffText.includes('senior') ? 'hard'
                 : 'medium';
      const qText = qEl.querySelector('.quiz-q-text')?.innerText || qEl.innerText;
      const aEl = qEl.nextElementSibling;
      const aText = aEl && (aEl.classList.contains('quiz-a')) ? aEl.innerText : '';
      if (qText && qText.length > 5) {
        cards.push({ q: qText.trim(), a: aText.trim(), diff, index: i });
      }
    });

    // Format 2 (details/summary)
    if (!cards.length) {
      document.querySelectorAll('details').forEach((det, i) => {
        const sumEl = det.querySelector('summary');
        const ansEl = det.querySelector('.ans');
        if (!sumEl) return;
        const labelEl = sumEl.querySelector('.q-label,.q-basic,.q-mid,.q-senior');
        const labelTxt = labelEl ? labelEl.textContent.toLowerCase() : '';
        const diff = labelTxt.includes('basic') ? 'easy'
                   : labelTxt.includes('senior') ? 'hard'
                   : 'medium';
        const qText = sumEl.innerText.replace(labelEl ? labelEl.innerText : '', '').trim();
        const aText = ansEl ? ansEl.innerText.trim() : '';
        if (qText.length > 5) {
          cards.push({ q: qText, a: aText, diff, index: i });
        }
      });
    }

    if (!cards.length) return;

    // Load per-topic card state
    const cardStateKey = `aip_cards_${curTopic ? curTopic.id : 'unk'}`;
    let cardState = {};
    try { cardState = JSON.parse(localStorage.getItem(cardStateKey) || '{}'); } catch {}
    function saveCardState() { localStorage.setItem(cardStateKey, JSON.stringify(cardState)); }

    // Build the flip card section
    const section = document.createElement('div');
    section.className = 'aip-flip-section';
    section.id = 'aip-flip-section';

    const knownCount = Object.values(cardState).filter(v => v === 'known').length;
    const reviewCount = Object.values(cardState).filter(v => v === 'review').length;

    section.innerHTML = `
      <div class="aip-flip-header">
        <h3>🃏 Flashcard Review <span style="font-size:12px;color:#8b90b8;font-weight:500">(${cards.length} cards — tap to flip)</span></h3>
        <div class="aip-flip-controls">
          <div class="aip-search-wrap">
            <input class="aip-flip-search" id="aip-flip-search" placeholder="Search cards…" type="text"/>
          </div>
          <div class="aip-filter-btns">
            <button class="aip-filter-btn active" data-filter="all">All</button>
            <button class="aip-filter-btn easy" data-filter="easy">Easy</button>
            <button class="aip-filter-btn medium" data-filter="medium">Med</button>
            <button class="aip-filter-btn hard" data-filter="hard">Hard</button>
            <button class="aip-filter-btn" data-filter="review" style="color:#ff6b6b">Review</button>
          </div>
        </div>
      </div>
      <div class="aip-quiz-stats">
        <div class="aip-stat-chip"><span class="dot dot-all"></span>${cards.length} total</div>
        <div class="aip-stat-chip" id="aip-known-stat"><span class="dot dot-known"></span>${knownCount} known</div>
        <div class="aip-stat-chip" id="aip-review-stat"><span class="dot dot-review"></span>${reviewCount} to review</div>
        <div class="aip-stat-chip" id="aip-pct-stat" style="margin-left:auto;color:#7c6af7">
          ${cards.length ? Math.round((knownCount/cards.length)*100) : 0}% mastered
        </div>
      </div>
      <div class="aip-flip-grid" id="aip-flip-grid"></div>
    `;

    // Find insertion point: after quiz section or at end
    const quizSection = document.querySelector('#s9,.section:last-of-type,[id="quiz"]') || document.body;
    quizSection.appendChild
      ? quizSection.appendChild(section)
      : document.body.appendChild(section);

    let activeFilter = 'all';
    let searchQuery = '';

    function renderCards() {
      const grid = document.getElementById('aip-flip-grid');
      if (!grid) return;

      const filtered = cards.filter(c => {
        const matchFilter = activeFilter === 'all' ? true
          : activeFilter === 'review' ? cardState[c.index] === 'review'
          : c.diff === activeFilter;
        const matchSearch = !searchQuery || c.q.toLowerCase().includes(searchQuery) || c.a.toLowerCase().includes(searchQuery);
        return matchFilter && matchSearch;
      });

      if (!filtered.length) {
        grid.innerHTML = `<div class="aip-flip-empty" style="grid-column:1/-1">
          <div style="font-size:32px;margin-bottom:8px">🔍</div>
          No cards match your filter. <a onclick="resetFilter()" style="color:#7c6af7;cursor:pointer">Clear filters</a>
        </div>`;
        return;
      }

      grid.innerHTML = filtered.map(c => {
        const isKnown = cardState[c.index] === 'known';
        return `
          <div class="aip-flip-card ${isKnown ? 'aip-card-marked-known' : ''}"
               data-idx="${c.index}" data-diff="${c.diff}" onclick="flipCard(this)">
            <div class="aip-flip-inner">
              <div class="aip-flip-front">
                <div class="q-text">${escHtml(c.q)}</div>
                <div class="aip-flip-footer">
                  <span class="aip-diff-tag diff-${c.diff}">${c.diff}</span>
                  <span class="flip-hint">👆 tap to reveal</span>
                </div>
              </div>
              <div class="aip-flip-back">
                <div class="a-text">${escHtml(c.a) || '<em style="color:#8b90b8">See topic content</em>'}</div>
                <div class="aip-flip-footer">
                  <div class="aip-card-actions" onclick="event.stopPropagation()">
                    <button class="aip-know-btn" onclick="markCard(${c.index},'known')">✓ Got it</button>
                    <button class="aip-review-btn" onclick="markCard(${c.index},'review')">↩ Review</button>
                  </div>
                  <span class="flip-hint" style="color:#7c6af7">👆 tap to close</span>
                </div>
              </div>
            </div>
          </div>
        `;
      }).join('');
    }

    function updateStats() {
      const kn = Object.values(cardState).filter(v => v === 'known').length;
      const rv = Object.values(cardState).filter(v => v === 'review').length;
      const el1 = document.getElementById('aip-known-stat');
      const el2 = document.getElementById('aip-review-stat');
      const el3 = document.getElementById('aip-pct-stat');
      if (el1) el1.innerHTML = `<span class="dot dot-known"></span>${kn} known`;
      if (el2) el2.innerHTML = `<span class="dot dot-review"></span>${rv} to review`;
      if (el3) el3.textContent = `${cards.length ? Math.round((kn/cards.length)*100) : 0}% mastered`;
    }

    // Expose globals for inline onclick handlers
    window.flipCard = function(el) {
      el.classList.toggle('flipped');
    };
    window.markCard = function(idx, state) {
      cardState[idx] = state;
      saveCardState();
      updateStats();
      // Visual feedback
      const cardEl = document.querySelector(`.aip-flip-card[data-idx="${idx}"]`);
      if (cardEl) {
        if (state === 'known') {
          cardEl.classList.add('aip-card-marked-known');
          cardEl.classList.remove('flipped');
        } else {
          cardEl.classList.remove('aip-card-marked-known');
        }
      }
      // Auto-mark done if 80%+ known
      const knownCount = Object.values(cardState).filter(v => v === 'known').length;
      if (curTopic && knownCount / cards.length >= 0.8) {
        setTP(curTopic.id, { status: 'completed' });
        updateMiniBar();
        const btn = document.getElementById('tb-done');
        if (btn && !btn.classList.contains('done')) {
          btn.textContent = '✓ Done'; btn.classList.add('done');
        }
      }
    };
    window.resetFilter = function() {
      activeFilter = 'all'; searchQuery = '';
      const inp = document.getElementById('aip-flip-search');
      if (inp) inp.value = '';
      document.querySelectorAll('.aip-filter-btn').forEach(b => {
        b.classList.toggle('active', b.dataset.filter === 'all');
      });
      renderCards();
    };

    // Filter buttons
    section.querySelectorAll('.aip-filter-btn').forEach(btn => {
      btn.addEventListener('click', () => {
        section.querySelectorAll('.aip-filter-btn').forEach(b => b.classList.remove('active'));
        btn.classList.add('active');
        activeFilter = btn.dataset.filter;
        renderCards();
      });
    });

    // Search
    const searchInp = document.getElementById('aip-flip-search');
    if (searchInp) {
      searchInp.addEventListener('input', e => {
        searchQuery = e.target.value.toLowerCase();
        renderCards();
      });
    }

    renderCards();
  }

  function escHtml(str) {
    if (!str) return '';
    return str.replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;').replace(/"/g,'&quot;');
  }

  // ── Init ────────────────────────────────────────────────────────
  function init() {
    markStarted();
    buildTopBar();
    trackSectionVisits();

    // Build flip cards after page is fully rendered
    // Use requestIdleCallback if available, else setTimeout
    const schedule = window.requestIdleCallback || (fn => setTimeout(fn, 300));
    schedule(buildFlipCards);
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }
})();
