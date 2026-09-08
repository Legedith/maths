# Contributing a connection

Start with one precise statement that would help someone reuse an idea. Explain the terms, the hypotheses, the direction of the relation, and a concrete example. Include a primary source with a section, theorem, equation or page locator. When the connection is your own proposal, explicitly mark it `proposed` and include the intended proof obligation.

An analogy, a modelling choice, a reduction, a dependency and an equivalence are different relations. In particular, similarity does not establish theorem equivalence, and a model's mathematical property does not establish empirical validity for a physical or biological system. A source-backed theorem does not automatically have a Lean proof.

Edit `data/atlas.json`, adding source metadata before references to it. Use stable descriptive IDs, existing concept IDs where possible, and beginner-readable explanations. Add a learning journey or contribution task only when its steps are useful and its acceptance criteria can be checked. Run `uv run --frozen python scripts/validate_atlas.py` and `node scripts/check-atlas.ts` after edits. Structural validation does not replace independent source review.

For a candidate discovery, record what was searched, including alternate names and adjacent fields; state the exact conjecture and assumptions. Retain counterexamples and failed attempts. A finite exhaustive result must name its finite universe. A general claim needs a proof, a checked formalization, or a complete algorithmic certificate with a proof of the verifier. A reviewer who did not author the result must audit the proof, implementation and raw artifacts before it is promoted.

For an optimization, freeze the workload and baseline before measuring. Preserve the same outputs, input boundary and verification obligations. Keep raw times, failures, environment, code hashes and actual commands. Separate arithmetic-operation counts, bit complexity and machine-specific time. Avoid tuning a test and calling it held out.

Use uv and an isolated `.venv` for Python. Keep large caches and experiments on D: on the original Windows host. Agents must observe `AGENTS.md`: shared writes stay serial and only the Site owner edits or deploys the Site checkout.
