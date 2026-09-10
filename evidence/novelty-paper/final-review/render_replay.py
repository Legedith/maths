from pathlib import Path
import contextlib,io,json,hashlib
P=Path('D:/CodexWorkspaces/mathematics-atlas/project');S=Path(__file__).parent
code=(P/'scripts/build_research_paper.py').read_text(encoding='utf-8')
assert code.count("(ROOT/'docs/index.html').write_bytes(page.encode('utf-8'))")==1
assert code.count("(ROOT/'docs/.nojekyll').write_bytes(b'')")==1
code=code.replace("(ROOT/'docs/index.html').write_bytes(page.encode('utf-8'))","assert (ROOT/'docs/index.html').read_bytes()==page.encode('utf-8')")
code=code.replace("(ROOT/'docs/.nojekyll').write_bytes(b'')","assert (ROOT/'docs/.nojekyll').read_bytes()==b''")
buf=io.StringIO()
with contextlib.redirect_stdout(buf):exec(compile(code,str(P/'scripts/build_research_paper.py'),'exec'),{'__file__':str(P/'scripts/build_research_paper.py')})
actual=json.loads(buf.getvalue());expected=json.loads((P/'evidence/novelty-paper/integration/build-logs/attempt-paper-build-01.stdout.bin').read_bytes());assert actual==expected
actual['independent_read_only_replay']='byte-identical'
with (S/'renderer-result.json').open('x',encoding='utf-8') as f:json.dump(actual,f,indent=2);f.write('\n')
print(json.dumps(actual))
