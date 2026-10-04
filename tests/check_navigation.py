"""Check local navigation targets under a GitHub Pages project prefix."""
import re
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urljoin, urlsplit, unquote

ROOT = Path(__file__).resolve().parents[1]
BASE = 'https://example.github.io/android-interview-study-material/'

class Links(HTMLParser):
    def __init__(self, text):
        super().__init__()
        self.targets = []
        self.feed(text)
    def handle_starttag(self, tag, attrs):
        self.targets.extend(value for key, value in attrs if key in ('href', 'src') and value)

errors = []
checked = 0
for page in ROOT.rglob('*.html'):
    text = page.read_text()
    targets = Links(text).targets
    targets += re.findall(r"\bgo\(['\"]([^'\"]+)['\"]\)", text)
    for target in targets:
        if target.startswith(('http:', 'https:', 'data:', 'mailto:', 'javascript:', 'about:', '#')):
            continue
        resolved = urlsplit(urljoin(BASE + page.relative_to(ROOT).as_posix(), target))
        if not resolved.path.startswith('/android-interview-study-material/'):
            errors.append(f'{page.relative_to(ROOT)}: escapes project: {target}')
            continue
        local = ROOT / unquote(resolved.path.removeprefix('/android-interview-study-material/'))
        if not local.is_file():
            errors.append(f'{page.relative_to(ROOT)}: missing target: {target}')
        checked += 1
# Shared navigation is injected in lesson pages; validate its Home target in that context.
shared = (ROOT / 'android_interview_pdfs/shared.js').read_text()
assert "new URL('../index.html', scriptUrl).href" in shared
assert 'href="${dashboardUrl}"' in shared
assert "new URL('shared.css', scriptUrl).href" in shared
for source in (ROOT / 'index.html', ROOT / 'android_interview_pdfs/shared.js'):
    for filename in re.findall(r"file:\s*['\"]([^'\"]+)['\"]", source.read_text()):
        assert (source.parent / filename).is_file(), f'{source.name}: missing topic {filename}'
assert (ROOT / 'index.html').is_file()
assert not errors, '\n'.join(errors)
print(f'Passed: {checked} local links and roadmap card targets across all HTML pages.')
