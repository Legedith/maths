import subprocess,json
from pathlib import Path
r=Path(__file__).parent; args=[str(r/'.venv/Scripts/python.exe'),str(r/'evaluate.py')]; p=subprocess.run(args,capture_output=True,text=True,encoding='utf8',errors='replace'); (r/'round2-run.json').write_text(json.dumps({'argv':args,'cwd':str(Path.cwd()),'stdout':p.stdout,'stderr':p.stderr,'returncode':p.returncode},indent=2)); print(p.stdout,p.stderr); raise SystemExit(p.returncode)
