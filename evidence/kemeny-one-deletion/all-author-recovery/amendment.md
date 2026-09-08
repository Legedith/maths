# Bounded recovery after serialization failure

2026-09-08. Root authorization for one additional execution, explicitly
amending the earlier two-batch cap. The original all-deletions packet stays
frozen and incomplete. This is an extra execution, not a reclassification
of its failed attempts as success or as outside its original budget.

Evidence: astra-all-deletions-work/batch2.log and six case logs show every
symbolic subprocess failed at json.dumps on a SymPy BooleanTrue after
coefficient construction. No complete symbolic certificate was saved.
The wrapper's zero exit status does not certify any of those subprocesses.
The earlier batch also retained its separate bool-subtraction failure.

Permit one recovery run in a new, separate stage. Copy the frozen code,
change only the JSON serialization of Boolean positivity flags to native
bool, and run exactly the same six symbolic cases with the same per-case
300-second cap. Do not repeat the completed finite matrix batch, change
the domain, add parameter searches, or switch mathematical methods.
Record exact source diff, all input hashes, argv/stdout/stderr and actual
subprocess return codes. Aggregate status must fail if any child fails.
If any coefficient is not positive, report it; no further repair/search is
authorized by this amendment. Any surviving theorem needs independent audit.

Reason: the failed serialization prevents inspection of already declared
mathematical work. A bounded engineering correction restores reviewable
outputs; no new search direction or score selection is being authorized.
