# Why a connection needs its assumptions

These three teaching examples use the same small network. They are explicitly authored annotations, separate from the independent evaluation and the prospective retrieval study. An independent verifier checked the numerical values and assumption behavior of the retained 1.0.1 runs; the [verification record](../evidence/assumption-checks/independent/raw/teaching-examples-v1.0.1-verification.json) preserves the reruns and expected checks. The commands below use whichever checker version is installed in the checkout.

```text
vertex 0 -- conductance 2 -- vertex 1 -- conductance 1 -- vertex 2
```

Think of conductance as how easily an edge carries electrical current. The same weights define a random walker: at the middle vertex, it chooses the left edge with probability 2/3 and the right edge with probability 1/3.

The established connection says that the expected trip from one end to the other and back equals effective resistance multiplied by the sum of weighted degrees. This is the conductance-volume convention in Levin and Peres with Wilmer, [Markov Chains and Mixing Times, second edition](https://pages.uoregon.edu/dlevin/MARKOV/mcmt2e.pdf), book p.116 and Proposition 10.7 on pp.131–132. The source locators and source hash were checked independently in the prospective audit's source record.

For this network, the checker separately solves electrical and random-walk equations. It obtains resistance **3/2** and expected round trip **9**. Weighted degrees are 2, 3 and 1, with total **6**, so the source formula gives `6 × 3/2 = 9`.

The deliberately altered formula replaces the weighted total by twice the number of edges: `2 × 2 × 3/2 = 6`. That gives a concrete counterexample: **9 is not 6**. This alteration is synthetic; it is not an error attributed to the textbook.

The third annotation explicitly requires every edge to have unit conductance. The checker reads the Laplacian entries to test that requirement, finds it false, and returns **not_applicable** before evaluating the conclusion. This distinguishes a failed hypothesis from a calculation that happened to work on one graph.

## Reproduce each record

```powershell
uv run --frozen python -m atlas_checks fixtures/assumption-checks/teaching/weighted-commute-source-formula.json
uv run --frozen python -m atlas_checks fixtures/assumption-checks/teaching/weighted-commute-synthetic-missing-weights.json
uv run --frozen python -m atlas_checks fixtures/assumption-checks/teaching/weighted-commute-failed-unit-weight-assumption.json
```

The full values, assumptions and expression traces are retained under `evidence/assumption-checks/teaching/`. The first record only checks one instance of a known sourced theorem; it does not prove that theorem universally. The other two demonstrate different ways an attempted application can fail. A person or agent still has to translate the intended statement and source definitions into an accurate annotation.
