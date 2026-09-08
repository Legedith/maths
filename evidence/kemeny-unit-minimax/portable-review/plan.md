# Frozen independent implementation audit plan

Targets: verify_unit_minimax.py SHA39100ca08b809d629341326eab55f27278b29ef73243b0a6061003f5a6872a6a, result.json SHAe7d260218dd6ed48700fff61417311d2b10f48f30ec15ef3e8287644a07bcc60; contract SHA19d4aac28a4df98d217a8a2c57cc8b4a345facaff0e408ef074f30830de0075e. All source stages remain read-only.

Four checks: reproduction from byte-copied code/locked env; contract and complete-policy scope; distinct endpoint/full-minimax audit entailment; implementation alignment including full positive dictionaries,22 matrix candidates, actual volumes, exact witnesses and abstract example limits.

Exactly two logged subprocess attempts, each60s: uv run --frozen python copied-code --output fresh-result.json; then same argv for expected existing-output rejection. Assertions enabled, no PYTHONOPTIMIZE. Require first rc0/byte-identical result and second rc2/unchanged output. Retain stdout/stderr/argv/cwd/environment/timing. No new graph grid or searches; no self-certification of authored endpoint mathematics; use distinct accepted reviews. Public release/CI approval excluded.
