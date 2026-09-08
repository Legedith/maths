# Structured transfer checker interface, version 1

Frozen before implementation. This supplements `assumption-check-contract.md`; source and implementation reviews may identify errors, but any correction must retain the earlier contract and explain the change. The existing lab's interface and results remain unchanged.

## Input and output

One check has `id`, `graph`, `source`, `target`, `provenance`, `assumptions`, and `claim`. `graph` has integer `n` and `edges`, each an object with integer `u`, integer `v`, and `conductance` written as an integer or a rational string `p/q`. Boolean and floating-point substitutes for integers are invalid. Rational numerator/denominator strings are limited to 12 digits each; conductances must be positive. Reject loops, duplicate undirected edges, unsupported properties, directions and multigraphs. Vertices range from 0 to n-1, n is 2–6, and terminals are distinct.

`provenance` contains `kind` (`source_annotation` or `synthetic`), `source_url`, `source_locator`, `annotation_id`, `annotator`, and `interpretation` (`explicit`, `ambiguous` or `unsupported`). These fields record supplied provenance; the checker does not verify a URL or assert that an annotator's interpretation is correct. Empty fields are invalid. Ambiguous or unsupported interpretation yields `abstain` before mathematical claim evaluation.

`assumptions` is a list of `{id, expression}` records with unique nonempty IDs. `claim` is one boolean expression. A recorded false assumption yields `not_applicable`, even if the conclusion happens to hold. An unevaluable assumption or expression yields `abstain`. Otherwise a false claim yields `counterexample` and a true claim yields `no_counterexample_in_instance`. Never upgrade the latter to a universal proof. Structural violations yield `invalid_input`. Return structured JSON for all five verdicts, including errors, normalized input where available, source/annotation provenance, evaluated assumptions, exact expression trace and algorithm version.

## Expression language

Expressions are objects with exactly the listed fields:

- `{"kind":"rational","value":"p/q"}` or integer `value`.
- `{"kind":"boolean","value":true}`.
- `{"kind":"quantity","name":"resistance"}`.
- `{"kind":"binary","op":"add|sub|mul|div|eq|ne|lt|le|and|or","left":EXPR,"right":EXPR}`.
- `{"kind":"unary","op":"neg|not|sum|product","arg":EXPR}`.
- `{"kind":"entry","arg":EXPR,"indices":[i]}` or two indices `[i,j]`.

Arithmetic and order comparisons require rational scalars; boolean operations require booleans. Equality accepts operands of the same shape and type, including exact vector/matrix equality. `sum` and `product` accept rational vectors; `entry` indexes vectors or matrices with nonnegative in-range integer indices. No coercion between booleans and numbers. Division by zero, invalid type operations, unknown quantities and unsupported expressions abstain rather than fabricate a value. Cap the AST at depth 20 and 300 nodes; reject structural/resource-limit violations explicitly. No input is executed as Python code.

## Quantities and conventions

Expose these names: `n`, `edge_count`, `total_conductance`, `degrees`, `laplacian`, `transition_matrix`, `laplacian_rw`, `laplacian_rank`, `laplacian_determinant`, `target_cofactor`, `nonzero_spectrum_product`, `rw_nonzero_spectrum_product`, `tree_mass`, `tree_edge_mass`, `edge_probability`, `stationary_measure`, `stationary_distribution`, `resistance`, `hit_forward`, `hit_backward`, `commute`, `potentials`, `ones`, `connected`, `terminals_connected`, `terminal_is_edge`, and `period`.

`A[u,v]` is conductance, `D` is the diagonal degree/conductance matrix, `L=D-A`, and `total_conductance=sum(degrees)=2*sum(edge conductances)`. Choose **row-stochastic** `P=D^-1 A`: row distributions evolve as `mu P`, and column-valued functions as `P f`. The exposed random-walk Laplacian is exactly `L_rw=I-P=D^-1 L`. The symmetric normalized matrix `D^-1/2 L D^-1/2` is a different object and is not exposed under this name. `P`, `L_rw` and the stationary-distribution quantity are undefined when an isolated vertex makes this transition convention undefined. `stationary_measure` is the unnormalized degree vector.

`tree_mass` is the sum of products of conductances over all spanning trees; it is zero when there is no spanning tree. `tree_edge_mass` and `edge_probability` refer only to the selected existing terminal edge in a connected graph. They are undefined for nonedges or disconnected graphs, so the checker cannot fabricate a zero-valued substitute for an inapplicable edge theorem. `target_cofactor` deletes the target row and column from the combinatorial Laplacian.

`nonzero_spectrum_product` is exposed only for connected graphs, where it can be computed as the sum of all principal (n-1)-minors. The random-walk version uses the same coefficient of L_rw and also requires connectedness. Do not call this sum a nonzero-spectrum product on disconnected graphs, where the nullity changes.

Resistance and directed hitting times are defined when the two terminals share a connected component and may be solved on that component. Different components yield undefined quantities, not a finite placeholder. Global `potentials` require a connected graph and ground the target at zero. `period` is defined for a connected graph in this domain: certify 2 with an explicit bipartition/parity argument, or 1 with an odd-cycle certificate. Finite transition samples alone are insufficient. `ones` and the Laplacian rank/nullspace calculation supply an exact gauge witness.

The implementation must construct electrical and Markov systems separately and enumerate weighted trees independently of determinants/resistance. Sharing generic rational linear algebra is permitted and must be disclosed. The independent evaluation must include five- and six-vertex examples, rational weights, nonedges, disconnected same/different terminal components, isolated vertices, type errors, malformed input, failed assumptions with accidentally true conclusions, ambiguous interpretation, and AST bounds.
