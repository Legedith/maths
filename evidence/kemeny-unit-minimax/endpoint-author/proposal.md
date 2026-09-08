# Candidate minimax endpoint theorem

Author analytic packet; independent audit and integration pending. This is elementary linear-fractional reasoning using established workload identities, not a novelty claim. No evaluator or graph grid was run. It applies to a finite action set, not automatically to freely variable-strength actions.

## Domain and workload reduction

Let E be a finite nonempty set of interventions on the SAME n>=2 vertices. Each produces a fixed connected undirected graph with positive conductances on its present edges, weighted random-walk transitions, total undirected conductance m_e>0, and Laplacian pseudoinverse M_e. Different actions MAY have different fixed volumes. An action may be no action; none may depend on theta. Let endpoints be iid from p_theta=(1-theta)w+theta delta_hub, w=1/n, with diagonal hitting zero and theta in the closed interval[l,h] satisfying0<=l<=h<1.

The accepted commute/covariance identity gives
 U_e(theta)=2m_e(1-theta)[tr(M_e)/n+theta(M_e)_hub,hub]
           =(1-theta)L_e(theta),
 L_e(theta)=alpha_e+theta beta_e,
 alpha_e=2m_e tr(M_e)/n, beta_e=2m_e(M_e)_hub,hub.
Thus different FIXED candidate volumes are absorbed into their own alpha,beta. They must not be canceled separately. Since tr(M_e)>0 and beta_e>=0, these lines and actual objectives are strictly positive on the admitted interval. More generally, the theorem below needs only positive affine reduced lines, regardless of their origin or slope signs.

The n1 graph and a point-mass workload have zero objective and undefined0/0 relative regret; exclude them. At theta1 the hub mixture is a point mass, every actual objective vanishes, and the endpoint theorem below cannot classify its actual relative regret. A limiting normalized ratio at1 is a different explicitly extended quantity, not the stated loss. Disconnected actions with infinite hitting time also fall outside this theorem.

## Endpoint theorem

Define the pointwise oracle Ustar(theta)=min_j U_j(theta)>0 and regret
 rho_e(theta)=U_e(theta)/Ustar(theta)-1.
For every action e,
 max_{theta in[l,h]}rho_e(theta)=max{rho_e(l),rho_e(h)}.

Proof: cancellation of the common positive1-theta gives
 1+rho_e(theta)=L_e(theta)/min_j L_j(theta)=max_j L_e(theta)/L_j(theta).
For any pair e,j, write their lines A+Btheta and C+Dtheta. Positivity of the denominator implies
 d/dtheta[(A+Btheta)/(C+Dtheta)]=(BC-AD)/(C+Dtheta)^2.
The derivative has constant sign or vanishes identically. Therefore each pairwise ratio lies below the larger of its two endpoint values throughout the interval. Taking the finite maximum over j preserves that bound:
 1+rho_e(theta)<=max_j max{L_e(l)/L_j(l),L_e(h)/L_j(h)}
 =max{1+rho_e(l),1+rho_e(h)}.
The reverse inequality for the maximum holds because both endpoints belong to the interval. Oracle switches introduce no exception. Continuity/positivity and finite E ensure maxima exist. For l=h the statement is tautological.

Corollary: every deterministic minimax action is found exactly by minimizing
 R_e=max{L_e(l)/min_j L_j(l)-1,L_e(h)/min_j L_j(h)-1}
over the full finite set. This computes the COMPLETE minimax set if all actions are retained, even when several oracle lines cross. No interior oracle-switch calculation is needed to determine the value or an optimal action.

## Two-action criterion, strict interior crossing

Suppose the relevant two reduced lines are A(theta),B(theta)>0 and cross strictly inside(l,h), with A(l)<B(l) and B(h)<A(h). For the TWO-ACTION problem,
 R_A=A(h)/B(h)-1,
 R_B=B(l)/A(l)-1.
Their other endpoint regrets vanish. Thus
 A is minimax iff A(l)A(h)<=B(l)B(h),
 B is minimax iff A(l)A(h)>=B(l)B(h).
Strict product inequality gives a unique minimizing ACTION among these two; equality gives both. Product comparison follows by multiplying the positive quantities A(l)B(h); there is no logarithm, approximation or common-volume assumption.

For A, its ratio to B strictly increases because the lines cross with the stated endpoint order, so its unique worst workload is h. For B the ratio to A strictly decreases and its unique worst workload is l. Each regret is zero on the interval where that action is oracle, including their crossing. At product equality the two different actions share the minimax value, but each has its own worst endpoint.

Boundary cases: if crossing is only at l or h, the action smaller on the interior is pointwise no worse, has zero regret everywhere, and uniquely minimizes among nonidentical lines on a nondegenerate interval. The other action has positive regret at the opposite endpoint. If lines coincide identically, both have zero regret and every workload is worst/best. If no crossing occurs and one line is strictly smaller somewhere and no larger everywhere, that action alone minimizes the two-action problem with zero regret. For a collapsed interval l=h, the minimax set is exactly the oracle tie set there, all with zero regret. Identical edge labels/objective lines may give multiple physical actions, which must all be retained.

## What domination must mean

To use a two-action calculation for a larger set, it is sufficient that EVERY excluded action C is pointwise weakly dominated by one FIXED retained action (A<=C everywhere, or B<=C everywhere). Then the oracle is min(A,B), and a retained action has regret no greater than its dominated action at every theta. Removing those actions preserves the minimax VALUE and at least one minimax action.

It need NOT preserve the COMPLETE minimax set. Example on[0,1/2]: A=1+2theta,B=2-2theta,C=3/2+theta. A<=C everywhere. The two retained actions both have maximum relative regret1, and C also has maximum1: at the left endpoint its regret is1/2 and at the right endpoint1. Thus C remains a tied minimax action despite being dominated. All lines are positive; this is an abstract affine example, not an asserted realization by a particular graph intervention. To exclude C from the full minimax set, calculate its endpoint score or prove a sufficient strict gap there. Pointwise STRICT domination at both endpoints by a fixed retained action suffices to give strictly larger worst regret than that action.

A weaker condition, C(theta)>=min(A(theta),B(theta)), is NOT enough to remove C for minimax optimization. Example on[0,1/2]: A=1+2theta,B=2-2theta,C=3/2. C never beats the pointwise oracle, but its maximum relative regret is1/2 while each retained line has maximum1. It is the better compromise. Again this is a positive-affine counterexample to an elimination inference, not a graph-family claim.

For a graph family with all other actions pointwise dominated, the exact meaning of domination and whether all tied minimizers are requested therefore matter. This packet does not assume either domination property for the currently studied multipartite family. General's separate forbidden-strength work is not used as an unverified premise.

## Provenance and limitations

Methodological claims use the accepted iid commute/covariance bridge plus the displayed derivative identity and elementary finite maxima. Different fixed volumes are explicitly included. Analytic conclusions are endpoint reduction and the conditional two-action product criterion; the two counterexamples delimit action elimination only. No external priority source or new algorithm claim is made. The finite minimax H09 graph packet is not required as a premise and is not re-evaluated.

All reasoning is analytic; zero numerical evaluators, no source queries, no graph expansion or shared edits. The action set is deterministic and finite: randomized intervention policies, theta-adaptive actions, disconnected graphs, arbitrary non-iid demand and infinite strength families require separate analysis. In particular no general physical robustness or practical benefit follows. Excluded fromPR12 and pending distinct independent audit.
