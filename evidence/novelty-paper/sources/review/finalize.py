from pathlib import Path
import hashlib,json
S=Path(__file__).parent;B=S.parent
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
files=[]
for folder in ['novelty-conjecture-followups-work','novelty-multipartite-work','novelty-completion-overlap-work']:
 files += sorted(p for p in (B/folder).iterdir() if p.is_file())
for folder in ['novelty-conjecture-followups-work','novelty-completion-overlap-work']:
 for a in json.loads((B/folder/'hashes.json').read_bytes()):assert sha(Path(a['path']))==a['sha256'],a['path']
files += [B/'novelty-conjecture-bridge-work/bridge.md',B/'novelty-conjecture-bridge-work/hashes.json',B/'novelty-conjecture-bridge-review-work/review.md',B/'novelty-conjecture-bridge-review-work/correction-ack.json',B/'kemeny-postresult-review-work/sources/hu-kirkland-2019.pdf',B/'kemeny-postresult-review-work/sources/hu-kirkland-2019.page-marked.txt',B/'novelty-open-problems-work/raw-04.json',B/'novelty-open-problems-work/source-notes.md',B/'novelty-paper-work/paper.md']
assert sha(B/'novelty-conjecture-bridge-work/bridge.md')=='76a74e870d0f1ce6840fc178ca3aee6442bc704b0850b1b18757737fdd41f946'
follow=[json.loads(p.read_bytes()) for p in (B/'novelty-conjecture-followups-work').glob('request-*.json')]
assert sum(len(r.get('search_query',[])) for r in follow)==6 and sum(len(r.get('open',[])) for r in follow)==6 and sum(len(r.get('find',[])) for r in follow)==3
comp=[json.loads(p.read_bytes()) for p in (B/'novelty-completion-overlap-work').glob('request-*.json')]
assert sum(len(r.get('search_query',[])) for r in comp)==0 and sum(len(r.get('click',[])) for r in comp)==1 and sum(len(r.get('find',[])) for r in comp)==3
text=(S/'review-draft.md').read_text(encoding='utf-8').replace('Final disposition awaits the concrete Completion Problems and Sparsity overlap packet.','Verdict: PASS for a reasoned submission-level contribution claim against the inspected literature; no identified required overlap gap remains. This is not absolute priority certification.')
text=text.replace('the Completion Problems and Sparsity lead must be resolved before this review closes.','the Completion Problems and Sparsity lead was resolved by the direct comparison below.')
text+='''

## Concrete overlap gap resolved

I inspected the new primary Completion Problems and Sparsity passages directly, rather than trusting its source note: overlap raw-02 lines561-580 define stochastic completions, Lemma2.2 attainment and Proposition2.3 sparse minimizing completions; lines626-632 treat fixed diagonal entries; lines679-684 treat one fixed row. The argument redistributes entries within a row of a stochastic matrix. An undirected unit edge insertion changes both endpoint rows together, renormalizing every existing neighbor probability from 1/d to 1/(d+1). Fixing those old probabilities disallows insertion; freeing them permits a larger directed feasible set. Existence of a sparse minimizer in that enlarged set does not establish strict improvement for a designated smallest-part unit edge. No theorem-level implication to the target conjecture is supplied by these passages. The identified material comparison gap is therefore closed for this assessment, without claiming every consequence of the whole paper was exhausted.

The retained tree-enumeration primary passage (open-problems raw-04, printed page16 lines2351-2365) concerns variable-arm trees and Theorem4.10's Braess-edge count. It is a different graph-family question, not an all-r dominating-vertex multipartite sign theorem. The failed later HTML access is still documented and not silently rewritten as successful.

## Evidence integrity and final disposition

All followup and completion manifest entries match current bytes. Followup requests contain exactly six queries, six opens and three finds; completion adds one primary click, zero queries and three finds. Root records explicitly disclose their capture-repair finds; no missing return is represented as an independently inspected one. No new retrieval or evaluator was used by this reviewer. Original source, corrected bridge, packet inputs and draft manuscript are hash-pinned in hashes.json.

Approved contribution wording: “We prove the r>=3 assertion of Hu and Kirkland's Conjecture3.4.7, constructively identifying a strictly improving minimum-part insertion for every positive p and every admitted collection of part sizes.” A separate statement may say that no earlier proof of these exact assertions was identified in the inspected literature. The main novelty assessment is supported by the named conjecture, exact scope match, nontrivial universal proof and concrete closest-source comparisons together; it is not inferred from a negative search alone.

The draft Section5 is supportable with its bounded qualification. Retain ranking as a separately proved strengthening, without a standalone substantial-novelty assertion. No “first proof”, exhaustive priority, publication-until-now openness, universal field impact, Lean verification or journal peer-review claim is approved. There is no identified unresolved material source gap blocking this scoped contribution claim. Final correctness/paper/bundle integration and any publication update remain separate gates.
'''
(S/'review.md').write_text(text,encoding='utf-8')
claims=[dict(id='N1',type='citation',statement='Original Conjecture3.4.7 expressly posits the target r>=3 exclusion.',evidence='pinned Hu-Kirkland page19 lines1226-1229'),dict(id='N2',type='conclusion',statement='Accepted theorem settles exact clause with a universal sign argument beyond the prior update formula.',dependencies=['N1'],evidence='corrected bridge and independent bridge review/ack'),dict(id='N3',type='citation',statement='Inspected 2025 tree, 2026 twin-clique, stochastic-completion and tree-enumeration statements do not state the target all-r theorem.',evidence='review.md Direct later-source comparisons and Concrete overlap gap resolved'),dict(id='N4',type='conclusion',statement='A nontrivial submission-level contribution claim is defensible against inspected literature; absolute priority is unestablished.',dependencies=['N1','N2','N3'],evidence='review.md Evidence integrity and final disposition')]
checks=[dict(id='reproduction',status='pass',note='Source record/manifest reproduction, original request counts and corrected bridge provenance checked; mathematical proof reuse is explicit, no evaluator.'),dict(id='specification_compliance',status='pass',note='Exact positive-p r>=3 clause, not known p=0/equal-size/r=2 cases or generic update novelty. Named conjecture is affirmative support.'),dict(id='source_verification',status='pass',note='Read primary conjecture and retained closest later theorem passages; concrete completion gap independently resolved through feasible-set mismatch.'),dict(id='implementation_alignment',status='pass',note='Draft Section5 and theorem-level contribution boundary agree with inspected source comparison; ranking kept as strengthening, not sole substantial novelty basis.')]
v=dict(status='pass',scope='reasoned submission-level contribution assessment against inspected literature',required_corrections=[],blocking_unresolved_material_gaps=[],absolute_priority='not_certified',checks=checks,claims=claims,required_wording_boundaries=['r>=3 clause, p>=1, all non-singleton sizes>=3','No first-proof or exhaustive-priority claim','Ranking separately proved strengthening','Final integration/publication audit separate'])
(S/'verdict.json').write_text(json.dumps(v,indent=2)+'\n',encoding='utf-8')
files += [S/'plan.md',S/'review.md',S/'verdict.json',Path(__file__)]
(S/'hashes.json').write_text(json.dumps(dict(artifacts=[dict(id=f'N{i+1:03}',path=str(p),sha256=sha(p),bytes=p.stat().st_size) for i,p in enumerate(files)]),indent=2)+'\n',encoding='utf-8')
print(json.dumps(dict(status='pass',artifacts=len(files),blocking_gaps=[])))
