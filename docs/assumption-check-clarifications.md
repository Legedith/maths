# Preimplementation clarification 1

2026-09-08. This resolves the implementation worker's question before dependent parser implementation; it does not change a test result or relax a scored case. The original interface remains retained with SHA-256 `63bea7e1be12ef64e172508d235d1f1ff5cbca137d461c51d849c1ef160a26bf`.

Unknown AST kind/operator, missing/extra fields, wrong structural field types, negative/noninteger/boolean indices, or resource bounds produce `invalid_input`. A structurally valid unknown quantity, runtime operand/shape error, division by zero, out-of-range indexing after the operand shape is known, or undefined quantity produces `abstain`. A final claim or assumption evaluating to a non-boolean also abstains. This resolves the interface's ambiguous phrase “unsupported expressions” by separating unsupported syntax from unsupported evaluation.

All input record types use exactly the listed fields. Source and target are strict non-boolean integers. Integer strings such as `"2"` are rational constants; trim surrounding whitespace. A denominator must use the nonnegative integer-string syntax and be nonzero. Conductances must be positive. The 12-digit numerator/denominator bound applies to integer and string representations alike. No boolean/number coercion is allowed.

Top-level `id` is a nonempty string, consistent with annotation and assumption IDs. Numeric identifiers are not coerced into strings. This answers a second worker question before the ID validator is implemented.
