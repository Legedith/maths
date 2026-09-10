from pathlib import Path
import hashlib,json
S=Path(__file__).parent;B=S.parent/'novelty-conjecture-bridge-work'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
b=(B/'bridge.md').read_bytes()
good=b'9142b6e6d2d761e86ffefa60d430c37a1aafa67a6e542f889a4a0797c76e4039'
bad=b'9142b6e6d2d761e86ffefa60d430c37a1aaafa67a6e542f889a4a0797c76e4039'
assert b.count(good)==1 and hashlib.sha256(b.replace(good,bad)).hexdigest()=='15a3941afb41bf9de014dea1569a5fe28508dd8af25850360eb90386a5c3df12'
assert sha(B/'bridge.md')=='76a74e870d0f1ce6840fc178ca3aee6442bc704b0850b1b18757737fdd41f946'
for r in json.loads((B/'hashes.json').read_bytes()):assert sha(B/r['path'])==r['sha256']
v=dict(status='pass',required_corrections=[],bridge_sha256=sha(B/'bridge.md'),manifest_sha256=sha(B/'hashes.json'),note='Only malformed P2 hash changed; reverse substitution recovers original audited bridge hash. Prior semantic approval carries forward. Original corrections verdict retained. Novelty/priority separate.')
(S/'correction-ack.json').write_text(json.dumps(v,indent=2)+'\n')
print(json.dumps(v))
