from datetime import datetime, timezone
from hashlib import sha256
from pathlib import Path
import json
from urllib.request import Request, urlopen

directory = Path(__file__).resolve().parent
records = []
for n in range(2, 7):
    url = f'https://users.cecs.anu.edu.au/~bdm/data/graph{n}c.g6'
    target = directory / f'graph{n}c.g6'
    assert not target.exists()
    started = datetime.now(timezone.utc).isoformat()
    with urlopen(Request(url, headers={'User-Agent': 'MathematicsAtlas research input snapshot'}), timeout=30) as response:
        data = response.read()
        status = response.status
        final_url = response.url
    target.write_bytes(data)
    records.append({'path': target.name, 'source_url': url, 'final_url': final_url, 'started_at_utc': started, 'ended_at_utc': datetime.now(timezone.utc).isoformat(), 'http_status': status, 'bytes': len(data), 'sha256': sha256(data).hexdigest()})
manifest = {'schema_version': 'kemeny-pair-source-inputs-v1', 'selection': 'All five official connected simple graph files for orders 2 through 6; filenames observed in the official catalogue.', 'status': 'source_inputs_only_no_graph_computation', 'catalogue_url': 'https://users.cecs.anu.edu.au/~bdm/data/graphs.html', 'files': records}
(directory / 'source-manifest.json').write_text(json.dumps(manifest, indent=2) + '\n', encoding='utf-8', newline='\n')
print(json.dumps(manifest, indent=2))
