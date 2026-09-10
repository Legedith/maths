from pathlib import Path
import json,hashlib
S=Path(__file__).parent;B=S.parent;P=B/'project'
paths=[B/'novelty-conjecture-bridge-work/bridge.md',B/'novelty-conjecture-bridge-work/plan.md',B/'novelty-conjecture-bridge-work/hashes.json',B/'kemeny-postresult-review-work/sources/hu-kirkland-2019.pdf',B/'kemeny-postresult-review-work/sources/hu-kirkland-2019.page-marked.txt',P/'evidence/kemeny-three-part/independent/source-domain-proof-notes.md',P/'evidence/kemeny-multipartite/general-review/report.md',P/'evidence/kemeny-multipartite/general-review/evaluate.py',P/'evidence/kemeny-multipartite/general-review/result.json',P/'evidence/kemeny-multipartite/general-review/run-2.json',P/'experiments/kemeny-multipartite-proof/certificate.json',P/'evidence/kemeny-multipartite/ranking-review/review.md',P/'evidence/kemeny-multipartite/ranking-review/hashes.json',P/'evidence/kemeny-multipartite/ranking-review/stdout.txt',P/'evidence/kemeny-multipartite/ranking-review/rc.txt',P/'evidence/kemeny-multipartite/ranking-review/check.py']
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
assert sha(paths[3])=='c896d263c6bec602274f84a29c30492f99e85e3bde654f3e61dcf5aa10718c77'
assert sha(paths[4])=='603a2406e9d3ae27f07f008aa0a5797f1ea161ce13f4a66e2049fd9177cdb917'
assert sha(paths[6])=='85b165206fd017efbd2d26feee1d50ec438f8c1531ff5900e47d765f174a3e39'
assert sha(paths[10])=='b264e53aa98bb9171fcb327cb82cd01ec31e4c67eecbf30af6752545c078804c'
assert sha(paths[11])=='9142b6e6d2d761e86ffefa60d430c37a1aafa67a6e542f889a4a0797c76e4039'
run=json.loads(paths[9].read_bytes());assert run['returncode']==0 and run['stderr']=='' and json.loads(run['stdout'])==json.loads(paths[8].read_bytes())
assert paths[14].read_text().strip()=='0'
old=json.loads(paths[12].read_bytes())
for row in old:
 if Path(row['Path']).name in ['check.py','stdout.txt']:
  target=P/'evidence/kemeny-multipartite/ranking-review'/Path(row['Path']).name;assert sha(target)==row['Hash'].lower()
checks=[dict(id='reproduction',status='pass',type='methodological',evidence=['B007','B008','B009','B010','B011','B012','B014','B015','B016'],note='Reused distinct accepted proof audits with unchanged frozen certificate/source hashes and raw rc0 records; no evaluator rerun.'),dict(id='specification_compliance',status='pass',type='conclusion',evidence=['B001','B005','B007','B012'],note='All r>=3, p>=1, minimum part>=3 cases covered, including ties; one strict-decrease nonedge refutes every-nonedge-positive definition. r=2 ranking validates graph criterion.'),dict(id='source_verification',status='pass',type='citation',evidence=['B004','B005','B006'],note='Pinned primary page19 lines1177-1229, page12 lines699-714 and page3 definition inspected. Equation13 qualification retained; current priority not assessed.'),dict(id='implementation_alignment',status='pass',type='methodological',evidence=['B001','B007','B008','B011','B012'],note='Bridge uses accepted all-r strict sign theorem and separately audited optional actual-change ranking; finite coefficient certificate linked to analytic gap-support extension.')]
verdict=dict(status='corrections',required_corrections=['Replace P2 ranking-review SHA256 in bridge.md with 9142b6e6d2d761e86ffefa60d430c37a1aafa67a6e542f889a4a0797c76e4039 (remove extra a); refresh bridge hash manifest.'],input_bridge_sha256=sha(paths[0]),checks=checks,mathematical_bridge_settles_historical_r_ge_3=True,novelty_priority_status='not_assessed',limitations=['No new evaluator, PDF render or literature search.','Do not assert literal malformed equation13 or a fully reconstructed replacement polynomial.','Original proof audits reused as distinct audits, not self-certified anew.'])
(S/'verdict.json').write_text(json.dumps(verdict,indent=2)+'\n',encoding='utf-8')
paths += [S/'plan.md',S/'review.md',S/'verdict.json',Path(__file__)]
(S/'hashes.json').write_text(json.dumps(dict(artifacts=[dict(id=f'B{i+1:03}',path=str(p),sha256=sha(p),bytes=p.stat().st_size) for i,p in enumerate(paths)]),indent=2)+'\n',encoding='utf-8')
print(json.dumps(dict(status=verdict['status'],inputs=len(paths),bridge_sha256=sha(paths[0]))))
