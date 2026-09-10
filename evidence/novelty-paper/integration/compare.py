from pathlib import Path
import hashlib,json,subprocess,sys
P=Path(__file__).resolve().parent.parent/'project';E=P/'evidence/novelty-paper'
a=json.loads((E/'clique/author/result.json').read_bytes())
b=json.loads((P/'work/novelty-paper/clique.json').read_bytes())
r=json.loads((E/'clique/review/result.json').read_bytes())
assert a['rows']==b['rows']
assert [{k:row[k] for k in ['k','K','delta']} for row in b['rows']]==r['rows']
for name,old in [('polynomial','check-01'),('ranking','ranking-01')]:
    assert (P/f'work/novelty-paper/{name}.json').read_bytes()==(P/f'evidence/kemeny-multipartite/integration/{old}.json').read_bytes()
result={'all_rows_equal':True,'independent_rows_equal':True,'row_count':len(b['rows']),'unchanged_main_checks_byte_identical':True,'python':sys.version,'uv':subprocess.check_output(['uv','--version'],text=True).strip(),'code_sha256':hashlib.sha256((P/'experiments/kemeny-multipartite-proof/verify_clique_example.py').read_bytes()).hexdigest()}
(P/'work/novelty-paper/portable-comparison.json').write_bytes((json.dumps(result,indent=2)+'\n').encode())
print(json.dumps(result))
