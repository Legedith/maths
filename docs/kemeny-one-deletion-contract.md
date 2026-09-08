# One-deletion certificate release contract

Freeze: 2026-09-08. This release addresses the specified hub-link deletion
in the current Kemeny network-design research subset. It does not replace
the broader discovery goal.

For integers a,b,c >= 3 with a <= b,c, form G = K_(a,b,c) join K_1.
Choose distinct u,v in the a-part and let h be the universal vertex.
For H = G - uh, prove or refute K(H + uv) - K(H) < 0 using the unweighted
simple random walk and stationary-target convention (zero hitting time at
the starting target). Cover every admitted tuple and choice of vertices.
Do not claim this deletion is worst or that every other deletion is safe.

The selected author packet is frozen at
astra-damage-symbolic-work/symbolic.json, SHA256
a5a096223ad9fdd3744a08d5fcfbd9643a5090431eadd501d13ead449cab2940.
Its two declared experiment batches and failures remain historical evidence.
Root will implement a dependency-free exact determinant reconstruction;
an independent Astra reviewer will verify the graph reduction, polynomial
identity, domain, and implementation alignment. Neither author nor root may
self-certify the final semantic checks.

The portable evaluator uses integer sparse polynomials in x,y,z and a
determinant parameter t, truncated modulo t^3. A subset dynamic program
computes det(L+tD), independently of the author's principal-minor sums.
Use a=3+x, b=3+x+y, c=3+x+z. Check the t coefficient is positive in both
graphs, form the exact numerator of the difference of coefficient ratios,
and compare its full negative coefficient dictionary against the frozen
certificate. Reject changed proof inputs and refuse to overwrite results.

Canonical evaluator (fresh output path on subsequent runs):

    uv run --project experiments/kemeny-one-deletion-proof --frozen python experiments/kemeny-one-deletion-proof/verify_certificate.py --certificate experiments/kemeny-one-deletion-proof/symbolic.json --output work/kemeny-one-deletion-proof/check-01.json

Retain exact argv, runtime provenance, raw stdout/stderr, exit status, and
all attempts. Use uv and isolated D-drive environments/cache. Review is
limited to two Ground/Critic/Resolve rounds. All four chain-of-evidence
checks and the deterministic gate must pass before promotion. Reuse earlier
unchanged evidence. Add the canonical check to the existing proof CI.

Publication originality and real-world benefit need separate evidence;
neither is established by a symbolic certificate or a literature-search gap.
Other deletion orbits are a separate exploration, outside this release claim.
