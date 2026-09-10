from pathlib import Path
import json,hashlib,re,contextlib,io
from html.parser import HTMLParser
P=Path('D:/CodexWorkspaces/mathematics-atlas/project');O=Path(__file__).parent
bp=P/'.codex/evidence/runs/research-paper-v1/bundle.json';digest=hashlib.sha256(bp.read_bytes()).hexdigest()
b=json.loads(bp.read_bytes());arts={a['id']:a for a in b['artifacts']}
assert digest=='b7802c039c6578e46bca0b965b939f32b5c55cacc9804393201a76f957c12c3b'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
for a in arts.values():
 p=(P/a['path']).resolve();assert p.is_relative_to(P.resolve()) and p.is_file();assert sha(p)==a['sha256'],a['id']
claims={c['id']:c for c in b['claims']}
locators=0
def supports(cid,seen):
 global locators
 assert cid not in seen
 c=claims[cid];assert c['status']=='supported'
 for s in c['supports']:
  if 'claim_id' in s:supports(s['claim_id'],seen|{cid});continue
  p=P/arts[s['artifact_id']]['path'];t=p.read_text(encoding='utf-8');loc=s.get('locator');locators+=1
  if loc.startswith('contains:'):assert loc[9:] in t
  elif loc.startswith('line:'):
   nums=list(map(int,loc[5:].split('-')));assert 1<=nums[0]<=nums[-1]<=len(t.splitlines())
   if 'expected' in s:assert str(s['expected']) in '\n'.join(t.splitlines()[nums[0]-1:nums[-1]])
  elif loc.startswith('json:'):
   obj=json.loads(t)
   for k in (loc[5:].strip('/').split('/') if loc[5:].strip('/') else []):
    k=k.replace('~1','/').replace('~0','~');obj=obj[int(k)] if isinstance(obj,list) else obj[k]
   if 'expected' in s:assert obj==s['expected']
  else:raise AssertionError(loc)
for cid in claims:supports(cid,set())
log=json.loads((P/arts['A132']['path']).read_bytes());assert log['returncode']==0 and not log['timed_out']
for stream in ['stdout','stderr']:
 p=P/'evidence/research-paper/build'/log[stream]['path'];assert sha(p)==log[stream]['sha256'] and p.stat().st_size==log[stream]['bytes']
build=json.loads((P/arts['A134']['path']).read_bytes());assert build['readme_sha256']==sha(P/'README.md') and build['html_sha256']==sha(P/'docs/index.html')
# Replay only rendering in memory: replace the two writes with byte assertions.
code=(P/'scripts/build_research_paper.py').read_text(encoding='utf-8')
code=code.replace("(ROOT/'docs/index.html').write_bytes(page.encode('utf-8'))","pass")
code=code.replace("(ROOT/'docs/.nojekyll').write_bytes(b'')","assert (ROOT/'docs/.nojekyll').read_bytes()==b''")
buf=io.StringIO()
ns={'__file__':str(P/'scripts/build_research_paper.py')}
with contextlib.redirect_stdout(buf):exec(compile(code,str(P/'scripts/build_research_paper.py'),'exec'),ns)
(O/'replayed-index.html').write_bytes(ns['page'].encode())
assert json.loads(buf.getvalue())==build
css=(P/'docs/paper.css').read_text();depth=0;extra=[]
for i,ch in enumerate(css):
 if ch=='{':depth+=1
 elif ch=='}':
  depth-=1
  if depth<0:extra.append(i)
assert depth==0 and len(extra)==0
class Parse(HTMLParser):
 def __init__(self):super().__init__();self.stack=[];self.errors=[]
 def handle_starttag(self,t,a):
  if t not in {'area','base','br','col','embed','hr','img','input','link','meta','param','source','track','wbr'}:self.stack.append(t)
 def handle_endtag(self,t):
  if not self.stack or self.stack.pop()!=t:self.errors.append(t)
h=Parse();h.feed((P/'docs/index.html').read_text());assert not h.stack and not h.errors
out=dict(input_bundle_sha256=digest,artifact_count=len(arts),claim_count=len(claims),recursive_support_checks=locators,hashes_locators_dependencies='PASS',raw_build_log='PASS',read_only_renderer_replay='byte-identical',html_nesting='PASS',css_extra_closing_brace_offsets=extra)
(O/'release-static-results.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(out))
