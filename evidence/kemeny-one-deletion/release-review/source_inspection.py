import json,re
from pathlib import Path
p=Path('D:/CodexWorkspaces/mathematics-atlas/astra-damage-prior-art-work/damage_sources4.json');txt=json.loads(p.read_text(encoding='utf-8-sig'))
for line in txt.splitlines():
 m=re.match(r'L(\d+)@',line)
 if m and (208<=int(m[1])<=217 or 242<=int(m[1])<=257 or 300<=int(m[1])<=317):print(line)
