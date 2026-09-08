"""Exact witness for an annotated external summary's normalization mismatch.

The phrase was interpreted by a human reviewer; this is not an NLP classifier.
"""
from fractions import Fraction
import json
from pathlib import Path
from atlas_engine import analyze_graph

payload = {'n':2,'edges':[[0,1]],'source':0,'target':1}
result = analyze_graph(payload)
degrees = [1,1]
mass = sum(degrees)
normalized_total = sum(Fraction(d,mass) for d in degrees)
resistance = Fraction(result['resistance'])
candidate = resistance * normalized_total
original = resistance * mass
assert result['hit_forward'] == '1' and result['hit_backward'] == '1'
assert candidate == 1 and Fraction(result['commute']) == 2 and original == 2
report = {
    'passed':True,
    'finding':'Under the standard normalized-probability interpretation, the annotated summary formula fails on a two-vertex unit-edge network. The original paper uses an unnormalized conductance measure and is correct.',
    'input':payload,'exact_result':result,'normalized_stationary_probabilities':['1/2','1/2'],
    'normalized_total':str(normalized_total),'conductance_measure_total':str(mass),
    'candidate_prediction':str(candidate),'actual_commute':result['commute'],
    'original_formula_prediction':str(original),'candidate_disproved':candidate != Fraction(result['commute']),
    'scope':'One externally retrieved generated summary, manually annotated. No estimate of error prevalence; no new general mathematical theorem; no claim the original paper is incorrect.'
}
out=Path('evidence/reuse');out.mkdir(parents=True,exist_ok=True)
(out/'normalization-witness.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8',newline='\n')
print(json.dumps(report,indent=2))
