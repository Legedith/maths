import json
from pathlib import Path
p=Path('D:/CodexWorkspaces/mathematics-atlas/astra-all-deletions-recovery-work/uB.json'); d=json.loads(p.read_text()); print(list(d)); print({k:v for k,v in d.items() if k not in ['q','N','D','negative_N_shift_terms','D_shift_terms']})
