# Exact unequal-family no-action counterexample

Exploratory analytic proposal; independent verification required. The claim that the best required unit insertion always strictly improves no action is FALSE on the unequal domain. A counterexample is

    (a,b,c)=(3,4,4), theta=14/405.

At this workload the optimal required insertions are restoration uh and every internal pair in either largest part B or C. All have the same objective, which is strictly ABOVE no action by

    7429/11809800 expected steps.

This is a modeled iid expected-step statement, not physical latency or impact evidence. It is excluded from PR11.

## Hand-verifiable rational proof

Use the accepted unit workload envelope for3<=a<=b<=c,c>a. Define n=a+b+c+1, d=n-a, e=n-c, m=ab+ac+bc+a+b+c-1,
 k=(n-1)(d-1)/(nd), W=[n(n-1)+d(d-1)]/(n^2d^2),
 T0=sum_q(q-1)/(n-q)+3/n, T=T0+W/k,
 h0=(n-1)/n^2+1/(n^2k), C=2/[e(e+2)], R=W/k.
The restore slope in the scaled score is1/(nk), and the restore/C crossing is tau=nkC-nW. The actual no-action improvement for a candidate with scaled score S(theta) is

    U_baseline-U_candidate = 2(1-theta)/n * [(m+1)S(theta)-T-theta*n*h0].

The m versus m+1 distinction is essential. No common-volume cancellation is made here.

For344 these values simplify exactly:

    n=12, d=9, e=8, m=50,
    k=22/27, W=17/972,
    T0=2/9+3/8+3/8+1/4=11/9,
    R=17/792, T=985/792, h0=269/3168,
    C=1/40,
    tau=12*(22/27)/40-12*(17/972)=14/405.

The accepted full unequal envelope guarantees that at this admitted0<tau<1, restoration and all largest-part pairs are the complete optimum set; incident-u and untouched A pairs are strictly worse. Since b=c=4, both B and C contribute6pairs, plus the single restoration:13optimal unit edges. The remaining3missing A pairs are nonoptimal.

At the crossing the optimum margin is

    F=(51/40)-(985/792)-(14/405)*(269/264)
     =31/990-1883/53460
     =-209/53460
     =-19/4860.

Therefore

    U_baseline-U_best
      =2*(391/405)/12 * (-19/4860)
      =-7429/11809800 <0.

The optimum required unit insertion is already worse than baseline; every other required unit insertion is still worse. This is a complete exact counterexample, not merely failure of a sufficient bound. No additional graph evaluation or numerical grid was run to obtain it: the second symbolic branch's boundary a=3,b=a+1,c=b identified the rational specialization, and the displayed arithmetic was derived by hand after the evaluator cap was exhausted.

## Discovery route, hypotheses and failures

The frozen contract considered unconditional crossing-margin positivity, separate tau branches, and symbolic counterexample analysis. The selected simplification was

    F_C(tau)=C[m-(n-1)k]-T0+(n-1)W.

It follows by substituting tau=nkC-nW and h0 above: the W/k terms cancel and n^2 k h0=(n-1)k+1. If this margin were positive throughout the unequal domain and restoration slope were positive, it would settle both tau<1 and tau>=1 because F_C decreases with theta. This was a falsifiable sufficient route, not an assumption.

Batch1 attempted a shifted coefficient certificate on the broader sorted domain a=x+3,b=a+y,c=b+z. It found117crossing numerator terms,9negative, and constant-51842; the restoration slope had34positive terms and constant1964. The run timed out with rc124 after intermediate output/result production; recorded elapsed66.828s includes process termination/setup overhead beyond the60s subprocess cap. It is a FAILED attempt, not a successful proof. Its intermediate result.json and all raw bytes are retained.

Batch2 was frozen separately to split the unequal integer domain into b=a,c=a+1+z and b=a+1+y,c=b+z. It independently reconstructs the intermediate numerator by exact polynomial division and verifies the formal cancellation without large rational expansion. The first branch reported34positive terms,constant366368. The second branch failed its positivity assertion, rc1. No batch2.json was produced, and no complete partial theorem is promoted from that failed run. The failure prompted the hand-verifiable344counterexample above. No third evaluator or retry occurred.

The two required remaining inequalities from the earlier packet cannot both hold universally: the tau<1 crossing positivity condition fails exactly here. Accordingly there is no need to settle the tau>=1 branch to refute the universal claim. That branch remains unresolved by this packet. The earlier equal-family theorem is unaffected, since c>a here. This packet does not classify all improving/nonimproving triples or workloads.

## Evidence and scope

contract.md and batch2-plan.md precede their respective attempts. check.py/run.py/stdout.bin/stderr.bin/run.json and check2.py/run2.py/batch2-stdout.bin/batch2-stderr.bin/batch2-run.json retain code and all failures. Python3.12.11/SymPy1.14.0 used uv with Dcache/environment. input-hashes.json pins accepted envelope/inverse and earlier no-action packets. hashes.json freezes this stage. No author self-certification, shared repository edits, Git activity, source search or current-release change occurred. A separate reviewer should check the displayed rational specialization and accepted optimum-set bridge before promotion.

## Exact actual objectives (hand symbolic boundary evaluation)

To make the volume arithmetic fully explicit, the common bracket for baseline is

    B=T/n+theta*h0
     =985/9504+3766/1283040
     =136741/1283040.

Thus

    U_baseline=100*(391/405)*B=53465731/5196312.

At the optimum crossing the scaled score is C=1/40, so the unscaled covariance score decrement is C/n=1/480 and

    B-C/n=134068/1283040=33517/320760,
    U_best=102*(391/405)*(33517/320760)
          =222787499/21651300.

Subtracting these exact objectives gives7429/11809800 as above. All denominators are positive. The baseline volume is50 and the inserted volume is51. Theta14/405 is strictly between0and1, and1-theta=391/405>0. These are hand rational evaluations at the symbolic branch boundary, not a third machine evaluator.

Complete ties: restoration contributes1edge; each of B,C has4vertices and contributes binomial(4,2)=6internal edges. The13tied best unit insertions exhaust the accepted unequal envelope at its crossing. Of the16total missing edges, the remaining two u-incident A edges and one untouched A pair have strictly smaller score under the accepted envelope, hence strictly larger inserted objective. Therefore EVERY one of the16missing unit insertions is worse than no action in this counterexample.
