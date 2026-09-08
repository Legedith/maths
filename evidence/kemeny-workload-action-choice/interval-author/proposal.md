# Candidate exact no-action interval for (3,4,4)

Root analytic derivation, pending independent audit. This is separate from
PR11 and from damage's frozen counterexample packet. No evaluator is run for
this derivation. It uses the accepted full unit workload envelope and the
counterexample constants reported by damage; those constants still require
independent reconstruction.

For a=3,b=c=4, n=12,m=50,k=22/27,W=17/972, let
T=985/792, h=M_hh=269/3168, C=1/40, R=17/792.
The full insertion envelope uses all internal B/C pairs below tau=14/405 and
restoration above, with their union at tau. Define actual baseline minus
inserted hitting time as2(1-theta)F(theta)/n. The two relevant margins simplify
by rational arithmetic to

    F_C(theta)=51/40-985/792-theta*(269/264)
              =31/990-(269/264)*theta,
    F_R(theta)=51*(17/792)-985/792
                 +theta*(51/(12*(22/27))-269/264)
              =-59/396+(277/66)*theta.

Their zeros are L=124/4035 and R0=59/1662. Exact cross products give
0<L<tau<R0<1:124*405=50220<56490=14*4035, and
14*1662=23268<23895=59*405.

The best insertion's improvement is the maximum of all insertion margins,
and the accepted insertion envelope reduces it to F_C before tau and F_R
after tau. These margins have negative and positive slopes respectively.
Thus allowing no action produces a complete finite-family decision rule:

- 0<=theta<L: precisely all internal B/C pairs minimize the objective.
- theta=L: those pairs and no action tie; all other insertions are worse.
- L<theta<R0: no action uniquely beats every unit insertion.
- theta=R0: restoration and no action tie; all other insertions are worse.
- R0<theta<1: restoration is uniquely best.

At tau, every best insertion is worse than no action by
2*(391/405)*(19/4860)/12=7429/11809800 walk steps.
The statement includes all individual pairs in both largest parts. At theta1
every actual objective is zero, so strict conclusions exclude that endpoint.
The action set is no action or exactly one missing UNIT insertion; this does
not optimize strength, price interventions, or measure physical-network gain.

Typed claims: rational identities/zero locations -> displayed rational
arithmetic; complete policy -> those identities, slope signs and the accepted
full unit insertion envelope; exact gap -> positive prefactor and evaluated
margin-19/4860. No generic Braess phenomenon or algorithm novelty is claimed.
An independent reviewer must reconstruct the graph inverse, all candidate
objectives, the convention and endpoint/tie reasoning before promotion.
