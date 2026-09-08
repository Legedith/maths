# Independent profile and proposed algebra audit

Verdict: sampled-path observations and proposed algebra PASS within the qualifications below. Historical execution has an acknowledged uv convention deviation; this review does not certify full execution-convention compliance. No evaluator, retry, solver modification or performance measurement was performed. Excluded from PR14.

## Retained evidence

Report SHA256e0887232dac449dba631e3d21a61a6fed684374b81511cc5730314fd5820dcde and manifest SHA256c1675369f6604e3e0a0774029672330eb18759f0989fb66768ae5377a7c3608a match. Every manifest entry was independently hashed, including raw streams, wrapper, unchanged solver, raw logger and local SymPy simplify source. input-checks.json retains these results. The reviewer made one harmless failed read of nonexistent profile.py before reading the actual profile_wrapper.py; this was a metadata-read error, not a profile/evaluator attempt.

The actual wrapper enables faulthandler and requests repeated five-second dumps before importing SymPy. Its flushed stdout has wrapper_started310434.953000, before_sympy_import310434.968000, after_sympy_import310437.250000, after_solver_import310437.250000 and before_solve310437.250000. It has no after_solve marker, no later comparison/serialization markers, and no result.json exists. The2.282second import difference is arithmetic on those markers, not solve time. Dependency environment installation occurs before wrapper startup.

The first complete stderr sample follows wrapper line20 into solve line171, maximum75, minimum72, compare61 and SymPy simplify611. The inspected solver line171 constructs the maximum of the two endpoint regrets for a candidate. The inner stack includes sign/assumption inference, minimal-polynomial composition and factorization. Therefore this sample localizes an observed path in endpoint-regret comparison, not graph inversion or serialization. It does not identify the physical edge, strength, balancing status, total runtime share, or cause of the earlier timeout.

The second dump is truncated and followed by explicit Windows fatal exception/access violation text. Raw attempt-profile01.json records returncode3221225477 (0xC0000005), timed_out=false, termination=null and a30second requested limit. Its UTC timestamps differ by15.210530seconds. Thus this run ended abnormally before the timeout mechanism fired; the periodic faulthandler word Timeout is a stack-dump trigger, not evidence that the outer logger timed out. The retained logger code calls process-tree termination only on subprocess.TimeoutExpired, consistent with termination=null. No crash-cause attribution is established.

The report's outer shell exit1 and direct D Python logger invocation are reported shell-level facts, not fields in the child attempt JSON. The task handoff independently identifies that invocation. The uv child does not make a direct-python outer launcher compliant with the use-uv-for-Python convention. Preserve those historical bytes; future outer logger AND child invocations should use uv. The earlier robust-noaction rc124/noresult record remains a distinct attempt and is neither reproduced nor erased by this abnormal exit.

## Proposed affine comparison: analytically valid

For each endpoint j, write f_j(t)=(m+t)(T_j+B_j*t)/(1+r*t), where B_j=r*T_j-s_j. Relative regrets differ by f_0/O_0-f_1/O_1, since both subtract1. With m>0,t>=0,r>0 and O_0,O_1>0, its sign is exactly the sign of

    N(t)=(T_0+B_0*t)*O_1-(T_1+B_1*t)*O_0.

This is an affine cross-product; no changing-volume factor is dropped when comparing different edge actions. Its cancellation is only within the two endpoint branches of the SAME edge/strength. The factor(m+t)/[(1+r*t)O_0 O_1] is strictly positive.

Set D=B_0 O_1-B_1 O_0 and C=T_1 O_0-T_0 O_1. A certified balancing strength is t=C/D with D nonzero and t in the admissible domain. Then N(t)=D*t-C=0 identically. A future implementation may therefore certify equality analytically for such a candidate without asking generic simplification to rediscover it. If C=D=0, the branches coincide at every strength. If D=0,C!=0, there is no crossing and sign(-C) still needs exact certification. A zero crossing belongs to t0; negative crossings are inadmissible. Stationary/nonbalancing candidates still require certified signs of N(t), and cross-edge candidate comparisons remain necessary. Duplicate generating labels must not lose the known balance identity.

This validates a proposed algebraic replacement, not an implemented fix. The sampled frame does not prove it was a balance candidate. Other simplification/comparison/serialization paths can remain costly or fail. Exact cross-product equality and positive-factor assertions, nonbalance tests and regression outputs require new bounded implementation review before any speed, completion or crash-prevention claim.

## Scope of acknowledgment

Reproduction of retained metadata/stack localization: PASS, read-only. Algebra and model factors: PASS analytically. Claim alignment: PASS with the explicit limits on runtime share/crash cause. Execution convention: DEVIATION retained, not retroactively cured by uv child. No final four-gate implementation or release approval follows from this profile. No novelty, measured application impact or fix claim is established.
