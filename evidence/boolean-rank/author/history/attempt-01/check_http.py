"""Check actual local routes; does not operate a browser."""
import hashlib
import json
from pathlib import Path
from urllib.request import urlopen

WORK = Path('D:/CodexWorkspaces/mathematics-atlas/boolean-rank-integration-work')
PROJECT = WORK.parent / 'project'
output = WORK / 'results/http-01.json'
if output.exists():
    raise FileExistsError(output)
expected = json.loads((PROJECT / 'data/atlas.json').read_bytes())
responses = []
with urlopen('http://127.0.0.1:8598/api/atlas', timeout=40) as response:
    body = response.read()
    actual = json.loads(body)
    if response.status != 200 or actual != expected:
        raise ValueError('Actual API route differs from canonical data')
    responses.append({'path': '/api/atlas', 'status': response.status, 'body_sha256': hashlib.sha256(body).hexdigest(), 'exact_json_equal': True, 'content_type': response.headers.get('Content-Type')})
    (WORK / 'results/http-01-api.json').write_bytes(body)
with urlopen('http://127.0.0.1:8598/', timeout=40) as response:
    body = response.read()
    text = body.decode('utf-8')
    if response.status != 200 or 'BOOLEAN RELATIONS' not in text or 'Curated connections' not in text:
        raise ValueError('Actual home route did not expose broadened scope')
    responses.append({'path': '/', 'status': response.status, 'body_sha256': hashlib.sha256(body).hexdigest(), 'broadened_scope_visible_in_response': True})
    (WORK / 'results/http-01-home.html').write_bytes(body)
report = {'passed': True, 'responses': responses, 'scope': 'Actual local HTTP response bodies and exact API object only; no browser interaction, visual, or deployed-site verification.'}
output.write_bytes((json.dumps(report, indent=2) + '\n').encode())
print(json.dumps(report, indent=2))
