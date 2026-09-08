# Preimplementation clarification 2

2026-09-08. Decisions sent to the implementation worker and independent verifier before their dependent code/evaluation, in response to the independent interface review. Retained outside the currently publishing checkout until the next milestone is integrated.

Structural invalidity anywhere takes first priority. Next, ambiguous or unsupported interpretation abstains. Evaluate all declared assumptions using only their referenced quantities: any false assumption yields `not_applicable` even if another is undefined; otherwise any undefined assumption abstains. Only then evaluate the claim. Boolean `and` and `or` are strict: an undefined operand propagates even when short-circuit evaluation could produce a Boolean. Boolean literals accept both true and false. Referencing no undefined quantity must not fail because an unrelated catalogue quantity happens to be undefined.

Direction is fixed: `hit_forward=E_source tau_target`, `hit_backward=E_target tau_source`, `commute=hit_forward+hit_backward`; global potentials solve `L v=e_source-e_target` with `v_target=0`, and resistance is `v_source-v_target`.

Keep the frozen quantity name `total_conductance`, but the trace must explain it as `sum_degrees=2*sum_edge_conductances`, also called graph volume. The degree-normalized stationary vector for a disconnected graph without isolates is canonical but may be nonunique and need not be a limit. Period 2 carries an explicit bipartition certificate; period 1 carries an explicit odd-cycle certificate.

Normalize rational signs, gcd and leading zeros. Numerators may have an optional plus/minus sign; denominators must be positive. A zero or negative denominator is structurally invalid. The 12-digit limit excludes a sign but counts written digits, and applies to integer and string constants. The 300-node limit is total across every assumption and the claim; AST root depth is 1, maximum 20. Source URL text records provenance without fetching or claiming proof of source entailment.
