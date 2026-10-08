#!/usr/bin/env python3
"""
generate_all_topic_pdfs.py
Generates individual, beautifully formatted topic-wise PDFs for all 97 Android interview topics.
Also creates a master ZIP archive: Android_Interview_Topic_Wise_PDFs.zip
"""

import os
import glob
import re
import subprocess
import shutil
import zipfile
import time
from concurrent.futures import ThreadPoolExecutor

PRINT_CSS = """
<style id="topic-pdf-print-override">
  @media print, all {
    body {
      background: #ffffff !important;
      color: #111827 !important;
      font-size: 10.5pt !important;
      line-height: 1.5 !important;
    }
    .sidebar, nav, .nav-buttons, .sidebar-header, .hero-tag, .btn, .progress-bar-wrap {
      display: none !important;
    }
    .layout, main, .main {
      display: block !important;
      margin: 0 !important;
      padding: 0 !important;
      width: 100% !important;
      max-width: 100% !important;
    }
    .section {
      display: block !important;
      opacity: 1 !important;
      transform: none !important;
      padding: 14pt 0 !important;
      max-width: 100% !important;
      border-bottom: 1px dashed #cbd5e1 !important;
    }
    section {
      display: block !important;
      padding: 14pt 0 !important;
      max-width: 100% !important;
      margin-bottom: 14pt !important;
    }
    .hero {
      background: #f8fafc !important;
      border: 1.5pt solid #cbd5e1 !important;
      border-radius: 8pt !important;
      padding: 18pt !important;
      margin-bottom: 18pt !important;
    }
    .hero h1 {
      color: #0f172a !important;
      font-size: 19pt !important;
      margin-bottom: 6pt !important;
    }
    .hero-desc {
      color: #475569 !important;
      font-size: 10.5pt !important;
    }
    .quiz-a {
      display: block !important;
      background: #f8fafc !important;
      color: #1e293b !important;
      border: 1pt solid #cbd5e1 !important;
      padding: 10pt 14pt !important;
    }
    details {
      display: block !important;
      border: 1pt solid #cbd5e1 !important;
      margin-bottom: 8pt !important;
    }
    details .ans {
      display: block !important;
      background: #f8fafc !important;
      color: #1e293b !important;
      padding: 10pt 14pt !important;
    }
    pre, .ascii, .ascii-box {
      background: #f1f5f9 !important;
      color: #0f172a !important;
      border: 1pt solid #cbd5e1 !important;
      font-size: 8.5pt !important;
      page-break-inside: avoid !important;
      break-inside: avoid !important;
    }
    p, li, td { color: #334155 !important; }
    h2, h3, h4 { color: #0f172a !important; }
    table, .card, .callout, .box {
      page-break-inside: avoid !important;
      break-inside: avoid !important;
    }
    th { background: #e2e8f0 !important; color: #0f172a !important; }
    td { color: #334155 !important; border-color: #cbd5e1 !important; }
  }
  @page {
    size: A4 portrait;
    margin: 12mm 12mm 12mm 12mm;
  }
</style>
"""

def natural_sort_key(filename):
    m = re.match(r'^(\d+)([A-Z])_', os.path.basename(filename))
    if m:
        return (int(m.group(1)), m.group(2))
    return (9999, filename)

def convert_single_file(args):
    html_file, temp_html, out_pdf = args
    try:
        with open(html_file, 'r', encoding='utf-8', errors='ignore') as f:
            raw = f.read()

        # Inject print CSS before </head>
        modified_html = raw.replace('</head>', PRINT_CSS + '\n</head>')

        with open(temp_html, 'w', encoding='utf-8') as f:
            f.write(modified_html)

        cmd = [
            "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
            "--headless=new",
            "--disable-gpu",
            "--no-pdf-header-footer",
            f"--print-to-pdf={out_pdf}",
            temp_html
        ]
        res = subprocess.run(cmd, capture_output=True, text=True)
        
        # Clean up temp html file immediately
        if os.path.exists(temp_html):
            os.remove(temp_html)
            
        if os.path.exists(out_pdf):
            size = os.path.getsize(out_pdf)
            return True, html_file, out_pdf, size
        else:
            return False, html_file, out_pdf, 0
    except Exception as e:
        return False, html_file, out_pdf, str(e)

def main():
    start_time = time.time()
    out_dir = "topic_pdfs"
    temp_dir = "temp_pdf_html"
    os.makedirs(out_dir, exist_ok=True)
    os.makedirs(temp_dir, exist_ok=True)

    files = [f for f in glob.glob('*.html') if re.match(r'^\d+[A-Z]_.*\.html$', f)]
    files = sorted(files, key=natural_sort_key)
    total_files = len(files)
    print(f"=== Generating Topic-Wise PDFs for {total_files} Topics ===")

    tasks = []
    for f in files:
        base = os.path.splitext(f)[0]
        temp_html = os.path.join(temp_dir, f"{base}_print.html")
        out_pdf = os.path.join(out_dir, f"{base}.pdf")
        tasks.append((f, temp_html, out_pdf))

    success_count = 0
    total_bytes = 0
    
    # Run with 6 workers in parallel for high throughput
    with ThreadPoolExecutor(max_workers=6) as executor:
        for idx, result in enumerate(executor.map(convert_single_file, tasks), 1):
            success, src, pdf_path, size = result
            if success:
                success_count += 1
                total_bytes += size
                pdf_name = os.path.basename(pdf_path)
                print(f"[{idx:2d}/{total_files}] Generated: {pdf_name:42s} ({size//1024:4d} KB)")
            else:
                print(f"[{idx:2d}/{total_files}] Failed: {src} -> {size}")

    # Remove temp dir
    if os.path.exists(temp_dir):
        shutil.rmtree(temp_dir)

    print(f"\nSuccessfully generated {success_count}/{total_files} topic PDFs! ({total_bytes / 1024 / 1024:.2f} MB total)")

    # Create ZIP archive
    zip_name = "Android_Interview_Topic_Wise_PDFs.zip"
    print(f"Creating ZIP bundle: {zip_name} ...")
    with zipfile.ZipFile(zip_name, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for root, _, pdf_files in os.walk(out_dir):
            for pdf in sorted(pdf_files):
                if pdf.endswith('.pdf'):
                    pdf_full = os.path.join(root, pdf)
                    zipf.write(pdf_full, arcname=pdf)
    zip_size = os.path.getsize(zip_name) / 1024 / 1024
    print(f"Created {zip_name} ({zip_size:.2f} MB) in {time.time() - start_time:.1f}s.")

if __name__ == '__main__':
    main()
