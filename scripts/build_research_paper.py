"""Deterministically render the reviewed README as a GitHub Pages research paper."""
from pathlib import Path
import hashlib,html,json,re
from html.parser import HTMLParser
from urllib.parse import urlsplit,unquote
import markdown

ROOT=Path(__file__).resolve().parents[1]
SOURCE=ROOT/'README.md'
BASE='https://github.com/Legedith/maths/blob/codex/research-paper/'
text=SOURCE.read_text(encoding='utf-8')
math=[]
def protect(match):
    value=match.group(0);block=value.startswith('$$')
    body=value[2:-2] if block else value[1:-1]
    tag='div' if block else 'span'
    rendered=f'<{tag} class="equation">'+('\\[' if block else '\\(')+html.escape(body.strip())+('\\]' if block else '\\)')+f'</{tag}>'
    math.append(rendered)
    return f'PAPERMATHTOKEN{len(math)-1}END'
protected=re.sub(r'\$\$[\s\S]*?\$\$|(?<!\$)\$(?!\$)[^\n$]+\$',protect,text)
md=markdown.Markdown(extensions=['fenced_code','tables','toc','sane_lists'])
body=md.convert(protected)
for i,value in enumerate(math):body=body.replace(f'PAPERMATHTOKEN{i}END',value)
body=re.sub(r'<p>(<div class="equation">[\s\S]*?</div>)</p>',r'\1',body)
local_links=[]
def link(match):
    target=html.unescape(match[1])
    if not urlsplit(target).scheme and not target.startswith('#'):
        p=ROOT/unquote(target.split('#')[0])
        if not p.is_file():raise ValueError(f'Missing paper link: {target}')
        local_links.append(target);target=BASE+target
    return 'href="'+html.escape(target,quote=True)+'"'
body=re.sub(r'href="([^"]+)"',link,body)
source_sha=hashlib.sha256(SOURCE.read_bytes()).hexdigest()
page='''<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Optimal Edge Insertion and a Multipartite Braess Conjecture</title>
<meta name="description" content="A constructive proof of the r≥3 assertion of Hu–Kirkland's multipartite Braess conjecture, strict edge ranking, and reproducible exact certificates.">
<meta name="paper-source-sha256" content="'''+source_sha+'''">
<link rel="canonical" href="https://legedith.github.io/maths/">
<link rel="stylesheet" href="paper.css">
<script defer src="paper.js"></script>
<script defer src="https://cdn.jsdelivr.net/npm/mathjax@3.2.2/es5/tex-mml-chtml.js"></script>
</head><body><a class="skip" href="#paper">Skip to paper</a>
<div class="page-shell"><aside aria-label="Contents"><a class="journal" href="https://github.com/Legedith/maths">MATHEMATICS ATLAS<br><span>Research note · 2026</span></a>
<nav aria-label="Paper sections">'''+md.toc+'''</nav><button type="button" id="print-paper">Print / save PDF</button></aside>
<main id="paper"><article>'''+body+'''</article><footer>Computer-assisted mathematics with independent audits. Novelty assessed against inspected literature; no exhaustive priority or journal peer-review claim.</footer></main></div>
</body></html>
'''
class Check(HTMLParser):
    def __init__(self):super().__init__();self.ids=[];self.anchors=[];self.h1=0
    def handle_starttag(self,tag,attrs):
        attrs=dict(attrs)
        if 'id' in attrs:self.ids.append(attrs['id'])
        if tag=='a' and attrs.get('href','').startswith('#'):self.anchors.append(attrs['href'][1:])
        if tag=='h1':self.h1+=1
check=Check();check.feed(page)
assert check.h1==1 and len(check.ids)==len(set(check.ids))
assert set(check.anchors)<=set(check.ids)
assert 'PAPERMATHTOKEN' not in page and 'SUPPLEMENT-' not in page
for asset in ('paper.css','paper.js'):assert (ROOT/'docs'/asset).is_file()
(ROOT/'docs/index.html').write_bytes(page.encode('utf-8'))
(ROOT/'docs/.nojekyll').write_bytes(b'')
print(json.dumps(dict(status='PASS',readme_sha256=source_sha,html_sha256=hashlib.sha256(page.encode()).hexdigest(),math_expressions=len(math),checked_repository_links=len(local_links),checked_fragment_links=len(check.anchors),html_h1_count=check.h1)))
