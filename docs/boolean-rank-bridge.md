# The same yes/no relation in different mathematical languages

Start with a table whose rows and columns have labels. A 1 means that the pair
is allowed; a 0 means it is not. Choose a set of rows and a set of columns such
that every crossing between them is a 1. This is an all-one rectangle. It need
not look contiguous on the page: row and column labels, not their display
order, define it.

Cover all the 1-cells with these rectangles. Overlap is allowed, and no
rectangle may include a 0-cell. The same choice of rectangles can be read as
Boolean factors or as complete bipartite subgraphs with fixed row and column
sides. These established translations let a reader carry an actual solution
from one formulation to another.

| Atlas connection | What is preserved |
|---|---|
| R1: Boolean rank and all-one rectangle cover | The two optimum counts agree. A factorization with k factors gives at most k nonempty rectangles; t rectangles give t Boolean factors. |
| R2: Rectangle cover and fixed-side biclique cover | Each covered matrix cell corresponds to one graph edge, and the cover cardinality is unchanged. |
| R3: Rectangle cover and the cited nondeterministic communication model | For nonempty 1-support, the minimum maximum leaf depth is the ceiling of the base-two logarithm of the minimum cover count. |
| R4: Local Boolean rank and local biclique cover | Participation of each row or column becomes participation of the corresponding graph vertex. The worst participation count is unchanged. |

R1, R2 and R4 follow the definitions and correspondences in Javadi, Maleki and
Omoomi, [Local Clique Covering of Graphs](https://arxiv.org/pdf/1210.6965v1),
Introduction, printed pages 2–3. R3 uses Sections 2.1–2.3 and Proposition 3 of
Karchmer, Newman, Saks and Wigderson,
[Non-deterministic Communication Complexity with Few Witnesses](https://www.math.ias.edu/~avi/PUBLICATIONS/MYPAPERS/SAKS/KCOVER/JOURNAL/kcover.pdf).
The linked manuscript's title page is dated February 11, 2003; that date is
used for its source record, not asserted as a journal publication date.

The map uses `rc_1` to mean a cover of 1-cells with unrestricted overlap. This
is the second paper's `kappa`, not its multiplicity-one parameter `kappa_1`.
Likewise `N^1_S2` means that paper's `n(f)` under its local leaf-test convention;
it is not `n_1(f)`, deterministic communication cost, privacy, latency or a
deployed-system measurement. The communication matrix is `M_f[x,y]=f(x,y)`.

Keep the row and column sets finite, nonempty and labeled. In the graph
formulation they are fixed disjoint sides, and the table is the rectangular
biadjacency matrix. The full symmetric adjacency matrix used elsewhere in the
network map is a different representation. For the local objectives, count
rectangles touching a row or column, or bicliques touching a vertex; counting
how often an individual cell or edge is covered changes the problem.

For an all-zero table, the Atlas explicitly allows zero factors, empty OR,
and an empty cover. Both count minima are then zero. For an all-zero function,
it additionally adopts a depth-zero constant-reject protocol. These local
definitions and elementary arguments extend the nonzero formula using
`ceil(log_2(max(1,rc_1(M_f))))`. They do not attribute a value for `log(0)` to
the paper. Each connection displays its own case, convention and argument.

The source corrections passed a separate
[independent semantic review](../evidence/boolean-rank/source-review/correction-review.json).
The exact earlier proposal is retained unchanged, including its historical
pending-review wording; the later review records its admission. The product integration passed its separate
[scoped independent product review](boolean-rank-verification.md), which
compares the frozen 49-file implementation with the admitted records and
does not constitute a new primary-source proof. The [projection](../evidence/boolean-rank/integration-projection.json)
records the actual added data and retained source hashes.

These are known relationships. This region does not establish a new theorem,
algorithm, automatic cross-domain match, general solver, benchmark result or
real-world benefit. A separately checked finite teaching example and a
separate role-mining reproduction are not silently promoted into these
general mathematical statements.
