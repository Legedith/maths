# Conductance choice under uncertain iid workload

Frozen 2026-09-09. Base 74b26b660bb77cfeb83498b8558c2fd8f3c1c0d1,
completed draft PR13. Stay in random walks and network edge design. Root owns
all shared writes; independent agents own isolated D stages. Use uv and
D-local environments/caches. No Site or broader atlas expansion in this release.

## Objective and graph domain

Choose one missing edge and any fixed conductance t>=0 before an uncertain
workload is known, minimizing maximum relative regret against an oracle with
the same edge/strength options. Include no action once via t=0. The graph is
finite, connected, loopless, undirected, with positive conductance on every
present edge, n>=3, and a finite nonempty specified set of allowed absent pairs.
Parallel edges may be merged by summing conductances. Source and target are
iid from (1-theta)Uniform+theta delta_q for a fixed focus vertex q and a closed
interval 0<=l<=theta<=h<1. Zero self-hitting and conductance-proportional walk
transitions are required. The focus need not be a universal hub. Actual graph
volumes m+t must remain inside each candidate objective.

This extends the selected network-design subset to arbitrary connected
weighted graphs. It does not change the workload to arbitrary demand, add
multiple edges, permit adaptive or randomized decisions, include monetary
costs, or extend ratios to the zero-objective point theta=1. The separately
audited randomized-unit result is excluded so this release answers one
coherent question about deterministic strength choice.

## Mathematical claims and analytic requirements

1. Independently audit the sharp nonadjacent-terminal bound mr>=4, with m the
   total undirected conductance and r effective resistance. Retain the
   Dirichlet test-potential argument, all inequality directions, and complete
   weighted K_(2,n-2) equality conditions. The terminals occupy the size-two
   part and each intermediate vertex has equal positive conductance to both
   terminals. Do not apply this bound to an existing edge or self-loop model.
2. For M=L^+, v an allowed incidence vector, z=Mv, prove r=v^TMv>0,
   T_theta=tr(M)+n theta M_qq, s_theta=||z||^2+n theta z_q^2>0 and
   B_theta=rT_theta-s_theta>0. The PSD matrix rM-Mvv^TM has rank n-2 on
   1-perp, ensuring a strict positive trace for n>=3. Derive the uniform
   positivity/coercivity constants for each fixed graph and finite allowed
   edge set; establish attainment and positivity of the continuum oracle.
3. Actual U=2(1-theta)f/n, where
   f=(m+t)[T_theta-t*s_theta/(1+r*t)]. Verify both derivative identities,
   including f''=2s_theta(mr-1)/(1+rt)^3>0. Positive endpoint normalizations
   and a finite maximum preserve strict convexity, so each edge has exactly
   one optimal minimax strength. Different edge locations may tie; all t0
   labels represent the same no-action graph.
4. Extend the positive-affine endpoint lemma to the continuum of fixed
   edge/strength actions by interchanging a supremum with a maximum over two
   endpoints. Oracle positivity must precede division. Compute each endpoint
   oracle by its per-edge stationary minimum or t0. Retain every per-edge
   minimax candidate: t0, positive stationary strengths at either endpoint,
   and the positive balance (T_h O_l-T_l O_h)/(B_l O_h-B_h O_l) if present.
   Handle zero denominator/nonzero numerator, identical functions, zero or
   negative crossings, collapsed intervals and duplicate expressions. Prove
   completeness and retain all global location ties.
5. Reproduce the exact 344,[0,1/10] witness from its graph. All16missing
   pairs form four exact classes; all11 declared candidate entries are
   compared. Endpoint oracles are sqrt(112079)/33+5144/99 and
   sqrt(10081666)/250+162923/3000 in the f normalization. Restoration at its
   unique positive balancing strength strictly beats every endpoint-stationary
   candidate and t0. Exact rational radical enclosures decide every comparison;
   decimals are display only. This witness does not establish a universal
   best location or measured network benefit.

## Portable implementation and meaningful validation

Use the existing pinned Python3.12.11/SymPy1.14.0 uv project. Deliver an
importable exact solver for rational conductances and rational interval
endpoints, with explicit graph/focus/allowed-edge inputs. Construct the graph
pseudoinverse and its own formulas; never eval evidence strings. Return
certified per-edge strengths, endpoint oracles, minimax objective values and
every global location tie, with no action represented once. Exact equality
and ordering must not use numerical tolerances. If an implementation resource
cap prevents certification, report an explicit inconclusive comparison and
never return an uncertified recommendation; describe that implementation
limit separately from the mathematical finite characterization.

Provide a portable fresh-output checker for symbolic derivatives, the full
344 witness and meaningful API boundary cases: a weighted three-vertex path,
a symmetric four-cycle under collapsed uniform workload with tied locations,
and the344 untouched-A-only action set at theta14/405 whose optimum is no
action. Validate input restrictions and candidate completeness. Independent
graph constructions or direct objective comparisons should check outcomes,
rather than tests merely repeating the solver's selection branches. Retain
exact strengths, signs, radical bounds, all candidate labels, actual volumes
and implementation/runtime hashes. JSON is deterministic UTF-8 LF and
requires fresh output. Assertions remain enabled. The CLI runs without
historical D-stage paths.

Name every analytic bridge not mechanically formalized: Dirichlet equality,
graph inverse/covariance reduction, positive rank trace, uniform coercivity,
continuum endpoint interchange, strict convexity and global candidate
completeness. Do not describe finite API examples as a proof over all graphs
or claim Lean formalization. Preserve raw logs, failures, argv, environment,
return codes and exact outputs. Root performs an independent canonical run
through the existing logger with an explicit uv child and fresh attempt ID.

## Source, review and release gates

Ground typed claims before polished prose. Reuse unchanged accepted mathematical
and source audits with pinned hashes and distinct authors/reviewers. The new
graph-general proof and degree/resistance attribution each need a distinct
audit before promotion. For the prior strength-source packet, attach G1 to
actual primary model passages and the access-failure evidence, not only the
request array. Springer volume/pages/year are an unverified discovery lead;
omit them from verified citations unless new primary support is obtained.
Retain primary URLs, versions, locators, exact request metadata and raw hashes;
bulk third-party returns remain local. Access gaps cannot establish novelty.

The implementation author cannot self-certify code or final semantic gates.
Final Critic/Resolve is at most two rounds, followed by the deterministic
evidence gate. Promote only after PASS. Add exact CI replay; verify actual
post-push states and downloaded artifacts independently before claiming hosted
success. Use a draft PR based on codex/kemeny-unit-minimax. Leave previous
bundles immutable. Known circuit, inverse-update, convexity and robust regret
methods require attribution; priority of this particular characterization and
measured physical value remain unresolved. The broader goal remains active.
