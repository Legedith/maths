# A safe insertion after a hub link fails

Consider three groups of vertices. Every vertex connects to all vertices in
the other groups, and a hub connects to everyone. Our earlier result gives
a useful new link inside a smallest group. The theorem here says a specific
such link still helps when one of its endpoints loses its connection to the
hub. Improvement means a strict decrease in stationary-target Kemeny's
constant for the simple random walk.

The proof and dependency-free checker have passed separate mathematical
and implementation reviews. The certificate covers an infinite family;
the small matrix examples are diagnostics. Publication originality and
practical benefit remain unresolved.

## Theorem and exact scope

Let a,b,c be integers with 3 <= a <= b,c. Let G be the complete multipartite
graph with parts A,B,C,{h} of sizes a,b,c,1. Choose distinct u,v in A and
put H=G-uh. Then

    K(H+uv) - K(H) < 0.

Here P=D^(-1)A is the unweighted transition matrix and K uses zero hitting
time when the sampled target is the starting vertex. The quantifiers allow
any original minimum part, including ties, and any distinct u,v in that
part, provided the deleted edge is uh. For a fixed H this proves improvement
for every added uv incident to its damaged vertex u.

This statement covers exactly three non-singleton parts and one hub. It
does not assert that every other missing edge in H helps, that uv is the
best intervention, or that every possible deleted edge is tolerated.

## Proof

Use the six cells {u},{v},A\{u,v},B,C,{h}, of sizes 1,1,a-2,b,c,1.
For e=0 before insertion and e=1 after it, their neighbor-count matrix is

```text
       u  v  A-rest  B  C  h
u      0  e     0    b  c  0
v      e  0     0    b  c  1
A-rest 0  0     0    b  c  1
B      1  1    a-2   0  c  1
C      1  1    a-2   b  0  1
h      0  1    a-2   b  c  0
```

Call this R_e, its diagonal matrix of row sums D_e, and L_e=D_e-R_e.
The transition matrix on cell-constant vectors is Q_e=D_e^(-1)R_e.
Each non-singleton cell is an independent twin class: its vertices are
nonadjacent and have identical neighbors outside that cell. A vector
supported there whose coordinates sum to zero is sent to zero by the full
transition matrix. The three such subspaces have total dimension
(a-3)+(b-1)+(c-1)=n-6, where n=a+b+c+1. Together with cell-constant vectors
they give a direct sum of the entire vertex space. The case a=3 simply
has zero omitted dimensions for A-rest.

Thus the full transition spectrum consists of the quotient spectrum plus
n-6 zeros, counting multiplicity. In the spectral expression
K=sum_(lambda != 1) 1/(1-lambda), each omitted mode contributes 1; their
contribution cancels in the difference. This standard expression also
follows from the fundamental-matrix formula used in the exact diagnostics;
see [Altafini et al., Corollaries 2.2-2.3, printed p. 651](https://arpi.unipi.it/bitstream/11568/1170026/2/Poloni_1170026.pdf).

Both graphs are connected and undirected with positive degrees. Their
transition matrices are similar to real symmetric matrices, with simple
eigenvalue 1 and every other eigenvalue less than 1. The quotient inherits
these spectral properties. Write

    F_e(t) = det(L_e+tD_e),
    q_e1 = [t]F_e(t),  q_e2 = [t^2]F_e(t).

If mu_2,...,mu_6 are the five positive nonzero eigenvalues of I-Q_e,
then F_e(t)=det(D_e) t product_i(t+mu_i). Consequently q_e1>0 and

    K_e = n-6 + q_e2/q_e1,
    Delta = N/(q_11 q_01),
    N = q_12 q_01 - q_02 q_11.

Set a=3+x,b=3+x+y,c=3+x+z. This covers the entire required integer domain
by x,y,z>=0. Exact reconstruction gives -N as the polynomial stored in
[symbolic.json](../experiments/kemeny-one-deletion-proof/symbolic.json),
with 284 nonzero coefficients, all positive integers. Its minimum
coefficient is 6, its constant coefficient is 1,784,916,000, and its total
degree is 10. Therefore -N >= 1,784,916,000 > 0. The denominator is strictly
positive, proving Delta<0. Permuting vertices and relabelling a selected
minimum part proves the asserted endpoint and tie quantifiers.

## Reproduction and independent checks

The author used exact principal-minor sums. An independent reviewer
reconstructed both full determinants by all signed permutations and checked
the complete coefficient list. The portable implementation uses a third
implementation: a subset dynamic program for the determinant in
Z[x,y,z,t]/(t^3). Truncation preserves the required coefficients of t and
t^2. It reconstructs both matrices, checks cell balance, positive degrees,
zero constant determinants, positive ratio denominators, and the entire
negative-numerator dictionary. It never evaluates the symbolic expression
strings in the historical author certificate.

From a fresh checkout, with uv installed:

```powershell
$env:UV_CACHE_DIR = 'D:/CodexWorkspaces/mathematics-atlas/uv-cache'
uv run --project experiments/kemeny-one-deletion-proof --frozen python experiments/kemeny-one-deletion-proof/verify_certificate.py --certificate experiments/kemeny-one-deletion-proof/symbolic.json --output work/kemeny-one-deletion-proof/check-01.json
```

Use a fresh output name on subsequent runs. The project pins Python 3.12.11
and has no Python package dependencies. Other platforms can use their own
cache directory. The certificate is pinned by SHA256; the checker rejects
a changed input. This is an exact computational certificate with an
independently audited mathematical bridge, not a Lean formalization.

Exact full adjacency matrices, separately constructed from vertex part
labels, give the following diagnostic differences:

| (a,b,c) | K(H+uv)-K(H) |
| --- | --- |
| (3,3,3) | -787/41664 |
| (3,4,5) | -89013391/6289074792 |
| (4,4,6) | -3360439/385735350 |

All six full-matrix K values agree with the quotient plus its omitted
modes. These checks were independently repeated. A reviewer initially
compared decimal-string coefficients with integers; the original failure
and the correction are retained. No finite grid is used as the proof of
the universal claim.

## Relation to existing work and remaining discovery

Equitable/twin quotient reductions are published tools; see
[Breen, deBlieck and Vander Meulen, Section 3](https://arxiv.org/html/2608.04150v1).
Ordinary edge-deletion updates also already exist in
[Altafini et al., Theorem 3.1, printed p. 652](https://arpi.unipi.it/bitstream/11568/1170026/2/Poloni_1170026.pdf).
Their Section 4 replaces an edge with two loops to obtain a nonnegative
centrality measure, which changes the operation being studied. Here uh is
simply removed. Also, u and v cease to be twins after that deletion, so
a twin-insertion theorem cannot directly supply this sign conclusion.

The potential contribution is this particular full-domain sign guarantee.
The bounded source investigation did not identify an existing theorem
settling it; that does not establish global originality. The model concerns
random-walk exploration of a highly structured network. It does not by
itself establish faster routing, lower latency, or a measurable improvement
in a deployed system.

Tolerance of every single-edge failure and optimal intervention after the
specified hub-link failure were subsequently proved and independently
audited in the [broader research note](kemeny-fault-tolerant-design.md).
Those conclusions use their own complete certificates and orbit arguments.

The [evidence index](../evidence/kemeny-one-deletion/README.md) links the
frozen author packet, independent reviews, raw results, and release bundle.
