import json
from pathlib import Path
from atlas_engine import analyze_graph

fixtures = json.loads(Path('fixtures/supplemental-six.json').read_text(encoding='utf-8'))
records = []
for fixture in fixtures['valid']:
    result = analyze_graph(fixture['input'])
    for key, expected in fixture['expected'].items():
        assert result[key] == expected, (fixture['id'], key, result[key], expected)
    records.append({'id':fixture['id'], 'kind':'post-freeze-supplemental', 'input':fixture['input'], 'result':result})
out = Path('evidence/supplemental'); out.mkdir(parents=True, exist_ok=True)
(out/'records.jsonl').write_text(''.join(json.dumps(r,sort_keys=True,separators=(',',':'))+'\n' for r in records),encoding='utf-8',newline='\n')
summary={'passed':True,'record_count':len(records),'scope':fixtures['status']}
(out/'summary.json').write_text(json.dumps(summary,indent=2)+'\n',encoding='utf-8',newline='\n')
print(json.dumps(summary,indent=2))
