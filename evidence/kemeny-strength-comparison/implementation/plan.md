# Frozen targeted implementation plan

Only this stage is writable. Baseline modules and original result are copied bytewise into baseline/. The baseline solver SHA256 is 11152f62717a691450361c4227a70eb7674e65b1c3bb3d5889464956898ad1a9.

H1: endpoint ordering equals the sign of the affine cross-product after cancelling positive factors; certified balance and coincident cases give exact equality.
H2: all original API cases retain exactly equal numerical objectives, strengths, actions and ties; original direct-grounded and invalid-input tests remain.
H3: the named (3,4,4), [0,9/10], all-16-edge regression completes with exact certificates and direct-grounded objective checks, or its failure is retained without budget expansion.

At most two full checker executions, each limited to 90 seconds by the existing process-tree-aware logger. Both outer logger and explicit child use uv. No general-comparator weakening, floating tolerance, graph grid, or changes to frozen inputs. Exact formulas and output bounds remain; expression formatting may differ when equal endpoint values are represented by the other endpoint. Independent implementation audit is required before promotion.
