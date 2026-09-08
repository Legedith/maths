# Candidate graph-general strength convexity and minimax theorem

Author analytic proposal, pending distinct independent audit and primary-source attribution. All three hypotheses hold under the explicit restrictions below. Zero evaluators were needed. This is not a generic novelty claim, physical-benefit claim or current-release change.

## Sharp resistance bound

Let G be a finite connected loopless undirected graph with positive conductance on every present edge, and let i,j be distinct nonadjacent vertices. Write m=sum_edges c_e for total UNDIRECTED conductance and r=R_eff(i,j). Parallel edges, if present, may be merged by summing conductances. There must be n>=3, since a connected two-vertex graph has no absent pair.

The Dirichlet principle says1/r is the minimum of sum_edges c_uv(V_u-V_v)^2 with V_i=1,V_j=0. Test V_v=1/2 at every other vertex. Because i,j are nonadjacent, its energy is(d_i+d_j)/4, where d_i,d_j are weighted degrees. Endpoint incident edge sets are disjoint, hence d_i+d_j<=m. Therefore

    1/r <= (d_i+d_j)/4 <= m/4,
    mr >= 4.

Equality mr=4 requires equality in BOTH steps. The second equality means no edge joins two vertices outside{i,j}. The trial potential must also be the unique harmonic interior solution. At any other vertex v its harmonic equation is(c_vj-c_vi)/2=0, so c_vi=c_vj (with an absent edge interpreted as zero). Connectedness and absence of all other edges require these equal conductances to be strictly positive. Thus equality holds exactly for a weighted K_(2,n-2), with endpoints i,j in the size-two part and c_iv=c_jv>0 separately for each intermediate v. Different branches may have different weights. Conversely each equal-weight branch has effective conductance c_iv/2, giving total1/r=sum_v c_iv/2=m/4. This proves sharpness and complete equality conditions. For n3 this is a two-edge path of equal conductances.

Nonadjacency matters: an existing edge in a two-vertex graph has mr=1, so the bound4 must not be silently applied to arbitrary pairs or edge reweighting. No self-loop convention is covered by this statement; the loopless graph and undirected-volume conventions are explicit.

## Strict convexity and attainment

Fix such G with n>=3, its Laplacian pseudoinverse M, and an allowed absent edge with incidence v. Put r=v^TMv>0,z=Mv. Workload is iid p_theta=(1-theta)Uniform+theta delta_q for a FIXED focus vertex q, with0<=l<=theta<=h<1. Neither chosen intervention nor law depends on the realized theta. Define

    T_theta=tr(M)+n theta M_qq,
    s_theta=||z||^2+n theta z_q^2>0,
    B_theta=r T_theta-s_theta,
    f_theta(t)=(m+t)[T_theta-t s_theta/(1+rt)], t>=0.

The established weighted commute/covariance identity and rank-one update give actual U_theta(t)=2(1-theta)f_theta(t)/n. Distinct strengths have distinct volumes m+t, which must remain inside f.

On1-perp, M is positive definite. The matrix K=rM-Mvv^TM is PSD by Cauchy-Schwarz and has rank n-2, so it is nonzero for n>=3. Consequently B_0=tr(K)>0; also B_theta=B_0+n theta K_qq>=B_0. Rewriting f gives

    f_theta(t)=(m+t)[B_theta/r+s_theta/(r(1+rt))]
                 >=(m+t)B_0/r>0.

This supplies positive lower bounds and coercivity uniformly in theta over the admitted compact interval; actual U has the additional uniform positive lower factor2(1-h)/n. A finite allowed edge set gives common bounds by taking the smallest positive B_0/r. Hence the continuum oracle is positive and attained, and each minimax objective attains its minimum at finite t.

Direct differentiation yields

    f_theta'(t)=[T_theta-m s_theta+B_theta(2t+rt^2)]/(1+rt)^2,
    f_theta''(t)=2s_theta(mr-1)/(1+rt)^3>0.

The sharp bound mr>=4 makes strictness immediate, including equality in that bound. Dividing the two endpoint objectives by their positive oracle constants preserves strict convexity. Their maximum is strictly convex: for two distinct strengths and a strict convex combination, each of the two functions lies strictly below the corresponding combination of endpoint maxima; taking their finite maximum preserves strictness. Subtracting1 changes nothing. Therefore EACH fixed edge has exactly ONE optimal deterministic minimax strength on[0,infinity). If its optimum is t0, it represents the shared no-action graph, not a distinct physical intervention. Different edges may have equal global values and location ties remain possible.

## General minimax rule

Allow any finite nonempty specified set of absent edges. Actions are choosing one edge and one fixed strength t>=0 before theta is known; the oracle has exactly that same continuum of options. No action is included once via t0. Positive-affine endpoint reduction extends to this setting: for any fixed action its actual U/(1-theta) is a positive affine function of theta with its own fixed volume. The ratio to the oracle is the supremum of ratios to all fixed actions. Each pairwise affine ratio is monotone or constant; sup over the action continuum commutes with max over the TWO workload endpoints. Thus worst relative regret is attained at l or h. The oracle's positivity and attainment were proved above, not assumed from a special graph example.

Let O_l,O_h be endpoint minima of f. For each edge, write A_theta=T_theta-m s_theta. Its endpoint minimizing strength is0 if A_theta>=0, otherwise

    t_theta=(sqrt(s_theta(mr-1)/B_theta)-1)/r.

The radicand exceeds1 in the latter case. Each endpoint oracle is obtained by finite comparison of these exact per-edge minima. To find the unique minimax strength for an edge it suffices to compare0, its two positive endpoint stationary strengths, and its positive balancing strength if present:

    t_balance=(T_h O_l-T_l O_h)/(B_l O_h-B_h O_l).

This follows because equality of normalized endpoint values cancels common(m+t)/(1+rt) and becomes linear. If denominator zero but numerator nonzero there is no crossing; if both vanish the normalized functions coincide identically and a stationary candidate suffices. Zero balancing strength is already0; negative strengths are inadmissible. For l=h the identical-function case applies. Duplicate candidate expressions must be merged, not misreported as several optimal strengths.

Completeness follows by considering an interior minimizer: either both endpoint functions are active and equal, or one is locally strictly active and its derivative is zero. The only finite boundary is0; coercivity rules out infinity. Strict convexity then rules out multiple distinct minimizing strengths for a single edge. Comparing finite per-edge minima and retaining ALL tied edge labels gives the complete deterministic global minimax set. This is a finite characterization, not a claimed bit-complexity or generic numerical algorithm guarantee.

## Restrictions, provenance and status

The focus q need not be a universal hub; only the iid uniform-plus-point-mass law matters. The theorem covers every fixed connected positive weighted loopless graph n>=3 with a nonempty allowed missing-edge set. Complete graphs have no such set and are excluded. The law remains fixed across actions. Theta1/point-mass zero regret, disconnected baselines, arbitrary non-iid demand, multiple-edge interventions, randomization, adaptive interventions and intervention costs require different analysis. No uniform bound over a varying graph family is claimed; all positivity/coercivity constants are for a fixed graph and finite edge set.

Accepted inverse/covariance and continuum-minimax audits are reused and pinned, while the Dirichlet bound, equality classification and strict-convexity extension are proved explicitly here. All three hypotheses are supported; no hypothesis was rejected. No matrix/graph grid, evaluator, source query, Git operation or shared write occurred. Typed claims preceded this prose. A distinct mathematical audit and primary attribution review are required before promotion; classical network/circuit or convex-analysis priority is not inferred from this derivation.
