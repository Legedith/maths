# Continuous perturbation certificate CLI preparation

The standard-library verifier requires --output PATH. The parent directory must already exist. Existing outputs are refused; use a new filename for every execution. No mathematics, graph/workload set, interval, certificate fields, or positivity criterion changed.

Canonical PowerShell command (choose a fresh output filename):

```powershell
$env:UV_CACHE_DIR='D:/CodexWorkspaces/mathematics-atlas/astra-continuous-portable-work/uv-cache'
$env:UV_PROJECT_ENVIRONMENT='D:/CodexWorkspaces/mathematics-atlas/astra-continuous-portable-work/.venv'
uv run --isolated --python 3.12.11 python D:/CodexWorkspaces/mathematics-atlas/astra-continuous-portable-work/verify_continuous_perturbation.py --output D:/CodexWorkspaces/mathematics-atlas/astra-continuous-portable-work/fresh-certificate.json
```

Function-level change: main() now parses required --output using argparse and selects args.output as destination. The existing assert refusing any existing output is retained at its original position before writing. Only the argparse import and these interface lines changed; changes.diff records the exact difference. As before, refusal occurs after computation. The script has no non-standard-library dependency.

Validation: attempt1 fresh output rc0/empty stderr, complete decoded JSON equality against frozen root result after removing only implementation_sha256. This includes all mathematical fields, coefficients, minima, metadata and records. The embedded implementation hash correctly changed to the new file hash. attempt2-existing deliberately reused the same output path, returned1 with the expected refusal, and left output bytes unchanged. Both attempts were capped at60seconds and finished within that bound. All argv/runtime/returncode and byte streams are retained. comparison.json records equality and hashes. No extra numerical cases or broad suite were run.

Accepted input script SHA256 c6ca55ac065e8ed75ff16680dfddea2a3d32e4e0054fe2ee7836bfe2bbe83625; accepted result13d3f0af59ccae1e848fe2c1c79d87cca1539b3e304fc6c8d3994ab0af5b09e0. New script6625373266410d302527d509516bb7df6c9a397573f42ba85798d9fe089853bb; replay03b7294b89656601b4ec8d69554a5d64affd209412d46df50f889ebca0eaabdc.

This is an implementation preparation packet, not an independent evidence or publication verdict. Its author does not self-certify the changed interface. Root integration and separate independent review remain pending. Project and every other stage stayed read-only; no push, deployment, Sites or UI work occurred.
