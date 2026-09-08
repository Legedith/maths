import hashlib, json, os, pathlib, subprocess, time
base = pathlib.Path(__file__).resolve().parent
source = base.parent / 'astra-workload-portable-work'
env = os.environ.copy()
env.update(UV_CACHE_DIR=str(base/'uv-cache'), UV_PYTHON_INSTALL_DIR='D:/uv-python', UV_PROJECT_ENVIRONMENT=str(base/'.venv'))
argv = ['uv', 'run', '--frozen', '--project', str(base), 'python', str(base/'verify_workload_envelope.py'), '--output', str(base/'replay.json')]
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
records = []
for attempt in (1, 2):
    start = time.monotonic()
    try:
        p = subprocess.run(argv, cwd=base, env=env, capture_output=True, timeout=60)
        stdout, stderr, rc = p.stdout, p.stderr, p.returncode
    except subprocess.TimeoutExpired as exc:
        stdout, stderr, rc = exc.stdout or b'', exc.stderr or b'', 'timeout'
    (base/f'attempt-{attempt}.stdout.bin').write_bytes(stdout)
    (base/f'attempt-{attempt}.stderr.bin').write_bytes(stderr)
    record = dict(argv=argv, cwd=str(base), environment={k:env[k] for k in ('UV_CACHE_DIR','UV_PYTHON_INSTALL_DIR','UV_PROJECT_ENVIRONMENT')}, rc=rc, seconds=time.monotonic()-start)
    record['output_sha256'] = sha(base/'replay.json') if (base/'replay.json').exists() else None
    (base/f'attempt-{attempt}.json').write_text(json.dumps(record, indent=2)+'\n', encoding='utf-8')
    records.append(record)
    if attempt == 1 and rc != 0:
        break
files = ['verify_workload_envelope.py','pyproject.toml','uv.lock']
result = dict(copies={f:dict(source=sha(source/f),copy=sha(base/f)) for f in files}, expected_result=sha(source/'result.json'), attempts=records)
result['exact_replay'] = records[0]['output_sha256'] == result['expected_result']
result['exclusive_output'] = len(records)==2 and records[1]['rc']==2 and records[1]['output_sha256']==records[0]['output_sha256']
(base/'reproduction.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
print(json.dumps(result,indent=2))
