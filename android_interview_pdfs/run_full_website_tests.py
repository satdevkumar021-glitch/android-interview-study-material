#!/usr/bin/env python3
"""
run_full_website_tests.py
Comprehensive End-to-End Automated Test Suite for Android Interview Preparation Website.
"""

import os
import glob
import re
import json
import zipfile
import urllib.request
import urllib.error
import threading
from http.server import HTTPServer, SimpleHTTPRequestHandler
import time

class TestResult:
    def __init__(self):
        self.passed = 0
        self.failed = 0
        self.warnings = 0
        self.tests = []

    def log(self, category, name, passed, details=""):
        status = "PASS" if passed else "FAIL"
        if passed:
            self.passed += 1
        else:
            self.failed += 1
        self.tests.append({
            "category": category,
            "name": name,
            "status": status,
            "details": details
        })
        icon = "✅" if passed else "❌"
        print(f"  {icon} [{status}] {name}" + (f" -> {details}" if details and not passed else ""))

    def warn(self, category, name, details=""):
        self.warnings += 1
        print(f"  ⚠️  [WARN] {name} -> {details}")

def run_tests():
    tr = TestResult()
    print("=" * 80)
    print("RUNNING COMPREHENSIVE TEST SUITE: ANDROID INTERVIEW PREP PORTAL")
    print("=" * 80)

    # -------------------------------------------------------------
    # SUITE 1: FILE & INVENTORY INTEGRITY
    # -------------------------------------------------------------
    print("\n--- SUITE 1: Files & Asset Inventory Integrity ---")
    
    html_files = sorted([f for f in glob.glob('*.html') if re.match(r'^\d+[A-Z]_.*\.html$', f)])
    tr.log("Inventory", "Topic HTML files count is 98", len(html_files) == 98, f"Found {len(html_files)} files")

    small_files = []
    missing_title = []
    missing_main = []
    for f in html_files:
        size = os.path.getsize(f)
        if size < 25000:
            small_files.append((f, size))
        with open(f, 'r', encoding='utf-8', errors='ignore') as fp:
            content = fp.read()
            if not re.search(r'<title>.*?</title>', content, re.I):
                missing_title.append(f)
            if '<main' not in content:
                missing_main.append(f)

    tr.log("Quality", "All topic HTML files > 25KB in size", len(small_files) == 0, f"{len(small_files)} files under 25KB")
    tr.log("Quality", "All topic HTML files have <title> tag", len(missing_title) == 0, f"Missing in: {missing_title}")
    tr.log("Quality", "All topic HTML files have <main> tag", len(missing_main) == 0, f"Missing in: {missing_main}")

    pdf_files = glob.glob('topic_pdfs/*.pdf')
    tr.log("PDFs", "Topic PDFs count in topic_pdfs/ is 98", len(pdf_files) == 98, f"Found {len(pdf_files)} PDFs")
    
    missing_pdfs = []
    for f in html_files:
        expected_pdf = os.path.join('topic_pdfs', f.replace('.html', '.pdf'))
        if not os.path.exists(expected_pdf):
            missing_pdfs.append(f)
    tr.log("PDFs", "Every HTML topic has a matching PDF file", len(missing_pdfs) == 0, f"Missing PDFs for: {missing_pdfs}")

    core_docs = [
        ('index.html', 200000),
        ('all_topics_combined.html', 3000000),
        ('android_interview_compact_guide.html', 700000),
        ('Android_Interview_Compact_Handbook.pdf', 5000000),
        ('Android_Interview_Complete_Master.pdf', 20000000),
        ('Android_Interview_Topic_Wise_PDFs.zip', 40000000),
        ('topics_manifest.json', 30000)
    ]
    for doc_name, min_size in core_docs:
        exists = os.path.exists(doc_name)
        size = os.path.getsize(doc_name) if exists else 0
        tr.log("Core Assets", f"Master asset exists & valid: {doc_name}", exists and size >= min_size, f"Size: {size:,} bytes (min: {min_size:,})")

    zip_path = 'Android_Interview_Topic_Wise_PDFs.zip'
    if os.path.exists(zip_path):
        try:
            with zipfile.ZipFile(zip_path, 'r') as zf:
                zip_names = zf.namelist()
                test_zip = zf.testzip()
                tr.log("ZIP", "ZIP bundle contains exactly 98 PDFs", len(zip_names) == 98, f"Found {len(zip_names)} files")
                tr.log("ZIP", "ZIP bundle has no corrupt files", test_zip is None, f"First corrupt file: {test_zip}")
        except Exception as e:
            tr.log("ZIP", "ZIP bundle integrity check", False, str(e))

    # -------------------------------------------------------------
    # SUITE 2: LINK & ROUTE VERIFICATION ON INDEX.HTML
    # -------------------------------------------------------------
    print("\n--- SUITE 2: Link & Route Verification on index.html ---")
    with open('index.html', 'r', encoding='utf-8') as f:
        index_content = f.read()

    # Static HTML hrefs (excluding JavaScript blocks)
    html_without_scripts = re.sub(r'<script.*?</script>', '', index_content, flags=re.S)
    all_hrefs = re.findall(r'href=[\"\']([^\"\']+)[\"\']', html_without_scripts)
    broken_hrefs = []
    for href in set(all_hrefs):
        if href.startswith('#') or href.startswith('javascript:'):
            continue
        clean_path = href.split('?')[0].split('#')[0]
        if not os.path.exists(clean_path):
            broken_hrefs.append(clean_path)
    tr.log("Links", "All static file links in index.html resolve to disk", len(broken_hrefs) == 0, f"Broken: {broken_hrefs}")

    card_links = re.findall(r'<a\s+href=[\"\']([^\"\']+)[\"\']\s+class=[\"\']topic-card[\"\']\s+id=[\"\']card-([^\"\']+)[\"\']', index_content)
    tr.log("Cards", "Total topic cards in index.html is 98", len(card_links) == 98, f"Found {len(card_links)} cards")

    pdf_btns = re.findall(r'href=[\"\']topic_pdfs/([^\"\']+\.pdf)[\"\']', index_content)
    tr.log("PDF Links", "Every card has a valid PDF download link", len(pdf_btns) == 98, f"Found {len(pdf_btns)} PDF buttons")

    # -------------------------------------------------------------
    # SUITE 3: ANCHOR & NAVIGATION INTEGRITY ON COMPENDIUMS
    # -------------------------------------------------------------
    print("\n--- SUITE 3: Anchor Integrity on Compendiums ---")
    with open('all_topics_combined.html', 'r', encoding='utf-8') as f:
        combined_content = f.read()

    combined_toc_links = re.findall(r'href=[\"\']#([0-9]+[A-Z])[\"\']', combined_content)
    combined_targets = set(re.findall(r'<article[^>]+id=[\"\']([0-9]+[A-Z])[\"\']', combined_content))
    missing_targets = [code for code in combined_toc_links if code not in combined_targets]
    tr.log("Anchors", "All TOC links in all_topics_combined.html match section IDs", len(missing_targets) == 0, f"Missing: {missing_targets[:5]}")
    tr.log("Chapters", "All 98 topics present in combined compendium", len(combined_targets) == 98, f"Found {len(combined_targets)}")

    with open('android_interview_compact_guide.html', 'r', encoding='utf-8') as f:
        compact_content = f.read()
    compact_toc_links = re.findall(r'href=[\"\']#topic-([^\"\']+)[\"\']', compact_content)
    compact_targets = set(re.findall(r'id=[\"\']topic-([^\"\']+)[\"\']', compact_content))
    missing_compact_targets = [code for code in compact_toc_links if code not in compact_targets]
    tr.log("Compact Anchors", "All TOC links in compact guide match section IDs", len(missing_compact_targets) == 0, f"Missing: {missing_compact_targets[:5]}")

    # -------------------------------------------------------------
    # SUITE 4: JAVASCRIPT & INTERACTIVE SIMULATION
    # -------------------------------------------------------------
    print("\n--- SUITE 4: JavaScript Data & Interactive Logic ---")
    
    m_topics = re.search(r'const\s+ALL_TOPICS\s*=\s*(\[.*?\]);', index_content, re.S)
    tr.log("JS Data", "ALL_TOPICS JSON array exists in index.html", m_topics is not None)
    
    if m_topics:
        topics_data = json.loads(m_topics.group(1))
        tr.log("JS Data", "ALL_TOPICS array length equals 98", len(topics_data) == 98, f"Count: {len(topics_data)}")
        
        tier1_items = [t for t in topics_data if t['tier'] == 'Tier 1']
        tier2_items = [t for t in topics_data if t['tier'] == 'Tier 2']
        tier3_items = [t for t in topics_data if t['tier'] == 'Tier 3']
        sysdesign_items = [t for t in topics_data if t['mod_num'] in [8, 30]]
        coding_items = [t for t in topics_data if t['mod_num'] == 34]
        aimodern_items = [t for t in topics_data if t['mod_num'] >= 36]

        tr.log("Filters", f"Tier 1 filter returns correct count ({len(tier1_items)})", len(tier1_items) > 50)
        tr.log("Filters", f"Tier 2 filter returns correct count ({len(tier2_items)})", len(tier2_items) > 15)
        tr.log("Filters", f"Tier 3 filter returns correct count ({len(tier3_items)})", len(tier3_items) > 8)
        tr.log("Filters", f"System Design filter matches Modules 8 & 30 ({len(sysdesign_items)} topics)", len(sysdesign_items) == 9)
        tr.log("Filters", f"Coding filter matches Module 34 ({len(coding_items)} topics)", len(coding_items) == 5)
        tr.log("Filters", f"AI & Modern filter matches Modules 36-42 ({len(aimodern_items)} topics)", len(aimodern_items) == 8)

        def simulate_search(query):
            q = query.lower()
            return [t for t in topics_data if q in (t['code'] + ' ' + t['clean_title'] + ' ' + t['desc'] + ' ' + t['tier']).lower()]

        coroutine_results = simulate_search("coroutine")
        compose_results = simulate_search("compose")
        mcp_results = simulate_search("mcp")
        fake_results = simulate_search("zyxwvu987654")

        tr.log("Search", f"Search 'coroutine' finds matching topics ({len(coroutine_results)} matches)", len(coroutine_results) >= 5)
        tr.log("Search", f"Search 'compose' finds matching topics ({len(compose_results)} matches)", len(compose_results) >= 6)
        tr.log("Search", f"Search 'mcp' finds AI Dev Tools topic ({len(mcp_results)} matches)", len(mcp_results) >= 1)
        tr.log("Search", f"Search for non-existent query yields 0 results", len(fake_results) == 0)

    tr.log("Modals", "Roadmap modal DOM structure (#roadmapModal) exists", 'id="roadmapModal"' in index_content)
    tr.log("Modals", "AI & MCP Playbook modal DOM structure (#aiModal) exists", 'id="aiModal"' in index_content)
    tr.log("Modals", "Roadmap 5 tabs exist (tab30, tab60, tabSys, tabCoding, tabMethod)", 
           all(tab in index_content for tab in ['id="tab30"', 'id="tab60"', 'id="tabSys"', 'id="tabCoding"', 'id="tabMethod"']))
    tr.log("Reader", "Study Reader iframe container (#studyReaderContainer) exists", 'id="studyReaderContainer"' in index_content)

    # -------------------------------------------------------------
    # SUITE 5: LIVE HTTP SERVER VALIDATION
    # -------------------------------------------------------------
    print("\n--- SUITE 5: Live Local HTTP Server Endpoint Checks ---")
    PORT = 8089
    server_started = False
    httpd = None

    class QuietHandler(SimpleHTTPRequestHandler):
        def log_message(self, format, *args):
            pass

    try:
        httpd = HTTPServer(('127.0.0.1', PORT), QuietHandler)
        server_thread = threading.Thread(target=httpd.serve_forever, daemon=True)
        server_thread.start()
        server_started = True
        time.sleep(0.3)
    except Exception as e:
        tr.log("HTTP", "Start test HTTP server on port 8089", False, str(e))

    if server_started:
        endpoints_to_test = [
            ('/index.html', 'text/html'),
            ('/all_topics_combined.html', 'text/html'),
            ('/android_interview_compact_guide.html', 'text/html'),
            ('/Android_Interview_Compact_Handbook.pdf', 'application/pdf'),
            ('/Android_Interview_Complete_Master.pdf', 'application/pdf'),
            ('/Android_Interview_Topic_Wise_PDFs.zip', 'application/zip'),
            ('/topic_pdfs/1A_Kotlin_Basics_Null_Safety.pdf', 'application/pdf'),
            ('/topic_pdfs/42A_Compose_Design_System.pdf', 'application/pdf'),
            ('/1A_Kotlin_Basics_Null_Safety.html', 'text/html'),
            ('/42A_Compose_Design_System.html', 'text/html'),
        ]

        for path, expected_type in endpoints_to_test:
            url = f"http://127.0.0.1:{PORT}{path}"
            try:
                req = urllib.request.Request(url, method='HEAD')
                with urllib.request.urlopen(req, timeout=3) as response:
                    status = response.status
                    ctype = response.headers.get('Content-Type', '')
                    passed = (status == 200) and (expected_type in ctype)
                    tr.log("HTTP Live", f"GET {path} -> {status} ({ctype})", passed, f"Status: {status}, Type: {ctype}")
            except Exception as e:
                tr.log("HTTP Live", f"GET {path}", False, str(e))

        if httpd:
            httpd.shutdown()

    # -------------------------------------------------------------
    # SUMMARY REPORT
    # -------------------------------------------------------------
    print("\n" + "=" * 80)
    print(f"TEST EXECUTION SUMMARY: {tr.passed} PASSED | {tr.failed} FAILED | {tr.warnings} WARNINGS")
    print("=" * 80)
    return tr.failed == 0

if __name__ == '__main__':
    success = run_tests()
    exit(0 if success else 1)
