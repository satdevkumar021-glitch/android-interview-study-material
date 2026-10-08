# Android Interview Study Portal

A complete, self-contained web portal for senior/staff Android engineer interview preparation.
**105 topic pages · 1,000+ quiz Q&As · ~400,000 words of content**

---

## 🚀 Quick Start

```bash
# Clone
git clone https://github.com/satdevkumar021-glitch/android-interview-study-material.git
cd android-interview-study-material

# Start local server (any of these)
python3 -m http.server 8080
# or
npx serve .
# or open index.html directly in browser

# Open
open http://localhost:8080
```

---

## 📚 What's Inside

### Portal Structure
| File | Purpose |
|---|---|
| `index.html` | Master dashboard — search, filter, progress tracking across all 105 topics |
| `shared.js` | Injected on every page — top navbar, prev/next, progress, score modal, quiz |
| `shared.css` | Dark-theme styles for topbar, flip cards, score modal |
| `topics_manifest.json` | Metadata for all 105 topics (used by index.html and shared.js) |
| `build_portal.py` | Regenerates `index.html` and `all_topics_combined.html` from manifest |
| `all_topics_combined.html` | Single-file reference with all 105 topics concatenated |

### Topic Pages (105 total)

Every topic page has:
- ✅ **9 sections** — Overview, How It Works, Code Examples, Production Patterns, Pitfalls, Interview Framework, Quick Revision, Q&As
- ✅ **Scroll-spy sidebar** — highlights current section as you scroll
- ✅ **← Dashboard** back link in sidebar and hero
- ✅ **Dark theme** with syntax-highlighted Kotlin code
- ✅ **Quiz accordion** — click to reveal answer
- ✅ **30-second interview answer** on every theory page
- ✅ **Must-mention checklist** for each topic

---

## 📋 All 105 Topics

### Module 1 — Kotlin Language
`1A` Kotlin Basics & Null Safety · `1B` Kotlin Functions · `1C` Scope Functions · `1D` Kotlin OOP · `1E` Special Classes · `1F` Generics & Variance · `1G` Delegation & Operators · `1H` Collections · `1I` Inline & Recursion · `1J` Equality, Interop & Errors

### Module 2–4 — Android Core
`2A` Android Components · `2B` Activity Lifecycle & State · `2C` Launch Modes & Back Stack · `2D` Fragments · `2E` Intents · `3A` App Startup · `3B` Main Thread Internals · `3C` Binder & IPC · `3D` Process Model · `4A` ViewModel · `4B` LiveData · `4C` Lifecycle

### Module 5–6 — Coroutines & Flow
`5A` Coroutines Fundamentals · `5B` Builders & Dispatchers · `5C` Structured Concurrency · `5D` Cancellation & Exceptions · `5E` Scopes, Concurrency & Testing · `6A` Flow Core · `6B` Flow Operators · `6C` Builders & Channels · `6D` Sharing: stateIn & shareIn

### Module 7 — Jetpack Compose
`7A` Compose Fundamentals · `7B` State Management · `7C` Side Effects · `7D` Compose Performance · `7E` Compose UI · `7F` Compose Navigation · `37A` Compose Animation · `42A` Compose Design System & Multi-Brand Theming

### Module 8–9 — Architecture & Design Patterns
`8A` Architecture Patterns (MVVM, MVI) · `8B` Clean Architecture · `9A` SOLID Principles · `10A` Creational Patterns · `10B` Structural Patterns · `10C` Behavioral Patterns

### Module 11–12 — DI & Networking
`11A` DI & Hilt Basics · `11B` Hilt Components · `12A` REST & HTTP · `12B` Retrofit & OkHttp · `12C` Advanced Networking

### Module 13 — Storage
`13A` Room · `13B` Room vs SQLite · `13C` Other Storage · `13D` DataStore: Preferences & Proto ⭐

### Module 14–18 — Android Platform
`14A` WorkManager · `14B` Choosing the Right Background Tool · `15A` Services · `16A` BroadcastReceiver · `17A` ContentProvider · `18A` Navigation & Deep Linking · `27A` Permissions · `28A` RecyclerView · `28B` Legacy UI · `29A` Paging 3

### Module 19 — Security
`19A` Data & Network Security · `19B` App Hardening & Auth · `19C` Secrets & API Key Security ⭐ · `42C` Advanced App Security: FLAG_SECURE & Hardening ⭐

### Module 20 — Testing
`20A` Unit Testing · `20B` Coroutines & Flow Testing · `20C` UI & Network Testing · `20D` Compose UI Testing ⭐

### Module 21–26 — Performance & Build
`21A` Android Performance · `21B` Baseline Profiles & Macrobenchmark ⭐ · `21C` App Startup Performance ⭐ · `22A` Memory Management & Leaks · `23A` Gradle / Build System · `24A` Modularization · `25A` CI/CD · `26A` Code Quality

### Module 30 — System Design
`30A` Offline-First Product Catalog · `30B` Login / Auth · `30C` Shopping Cart · `30D` Chat Application · `30E` Push Notifications · `30F` Image-heavy Feed · `30G` Large-scale Modular App

### Module 31–35 — Release, Debugging & Coding
`31A` Firebase · `32A` App Release · `33A` Debugging Scenarios · `33B` Data & Concurrency Scenarios · `33C` Platform & Scale Scenarios · `34A` Strings Coding · `34B` Arrays & Collections Coding · `34C` Math & Recursion Coding · `34D` Data Structures & Search · `34E` Android Coding · `35A` Behavioral & Senior Leadership

### Module 36–42 — Advanced & Modern
`36A` AI Integration in Android · `36B` AI Developer Tools · `38A` Kotlin Multiplatform (KMP) · `39A` Android Accessibility · `40A` Android New APIs (12–16) · `41A` Advanced Android Debugging · `42B` Trustworthy AI: Principles & Responsible Development ⭐

> ⭐ = newly added pages

---

## 🛠 Technical Details

### Every topic page follows this exact pattern:
```
div.layout
  nav.sidebar
    .sidebar-back → index.html
    .nav-item[data-section="sN"] × 9
  main.main
    div.hero
      .hero-back → index.html
    div.section[id="s1"] … div.section[id="s9"]
  script (window scroll-spy, getBoundingClientRect)
  script src="shared.js"
```

### Scroll-spy uses `window` scroll (not element scroll):
`shared.js` injects `main { overflow: visible !important }` — so the **window** scrolls, not `<main>`.
All pages listen on `window.addEventListener('scroll')` and use `getBoundingClientRect()`.

### Rebuilding the portal:
```bash
python3 build_portal.py
# Regenerates: index.html, all_topics_combined.html, topics_manifest.json
```

---

## 📊 Stats

| Metric | Value |
|---|---|
| Total topic pages | 105 |
| Quiz Q&As across all pages | 1,000+ |
| Average words per page | ~3,800 |
| Total content | ~400,000 words |
| Pages passing full audit | 105/105 ✅ |
| Broken links | 0 ✅ |
| Personal/company references | 0 ✅ |

---

## 📁 Repository Structure

```
android-interview-study-material/
├── index.html                   # Master dashboard
├── shared.js                    # Shared JS (topbar, quiz, progress, nav)
├── shared.css                   # Shared CSS (topbar, flip cards, modals)
├── topics_manifest.json         # All 105 topic metadata
├── all_topics_combined.html     # Single-file reference (all 105 topics)
├── build_portal.py              # Portal regeneration script
├── [1A-42C]_*.html              # 105 individual topic pages
└── README.md                    # This file
```

---

## 🔧 Contributing / Regenerating

To add a new topic page:
1. Create `NN_Topic_Name.html` following the 9-section structure
2. Add entry to `topics_manifest.json`
3. Add entry to `shared.js` TOPICS array
4. Run `python3 build_portal.py` to update `index.html`

---

## 📄 License

For personal study use. Content is general technical education material — no proprietary or confidential information.
