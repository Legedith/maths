# PR16 hosted CI audit

PASS for head `ba90dd8fceb136cc757b06b9511e3aebc9b515fb`.

**reproduction (pass):** Two downloaded hosted check.json artifacts independently byte-compared with integration/check-01.json; SHA256 cbb643c5f3fb79f2df2af5d51744c56ae4908bd5aaba66b82bacfdf3ed0fcfc7. Both JSON pointers /direct_first_step_comparisons=30, /symbolic_identities=3, /invalid_rejections=7 and /root_degeneracies length=7.

**specification_compliance (pass):** Raw ci-status-01.stdout.bin JSON /workflow_runs contains exactly 12 completed successful records, six unique workflows each on push and pull_request, all /head_sha equal the audited head. Scope is the retained PR16 hosted CI packet.

**source_verification (pass):** Raw gh API stdout SHA matches ci-status-01.json /stdout_sha256. Both download receipt /returncode=0 and stream SHA256 values match retained bytes. Artifact file hashes match receipt /files; no live GitHub refresh was performed.

**implementation_alignment (pass):** Both outputs /module_hashes have exactly three entries, independently matching experiments/kemeny-source-target-proof files. Runtime /runtime pins Python 3.12.11 and SymPy 1.14.0. Raw attempt logs /argv use child uv, /returncode=0, /timed_out=false, /timeout_seconds=90. Workflow kemeny-three-part.yml lines 199-215 uses outer uv and retains artifacts.

Audited bundle SHA256: `3aa645f02fcd789f62c05b1e6d3e1a8c7824f4d395f8bb17e34196192247f93e`.

No proof evaluator was rerun. This review covers retained hosted CI evidence only, not novelty, practical impact, later heads, or completion of mathematics. Exact input paths and independently computed hashes are in ci-manifest.json.
