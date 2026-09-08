# Structured transfer held-out suite v1

This directory is the public release of the prospective 80-case structured evaluation. The implementation was frozen and its first outputs were retained before the oracle or seed was opened. The suite is finite and nonexhaustive: it tests the frozen grammar and named quantities on fresh exact weighted graphs, but it does not establish correctness for every valid input.

Files:

- `suite.json` is the exact decrypted historical plaintext. Its SHA-256 is `ddf50219b87547a9cae547d936a7afba76380f11c4cda7c5fbb473635a01d9ee`.
- `cases.json` separates the 80 inputs and public case metadata from their expected results.
- `oracle.json` contains the expected results released after the code freeze and retained first run.
- `seed.json` discloses the generation seed and cryptographic derivation record. The historical seed commitment used the two literal ASCII characters backslash and zero after its prefix; the AES key and nonce derivations used a NUL byte.
- `run_public_suite.py` runs the inputs against the exact frozen 1.0.2 project bytes, retains all outputs, and only then invokes `compare_public_suite.py`.
- `release-manifest.json` gives byte sizes and SHA-256 hashes.

Run from any checkout with `uv` available:

```text
uv run --no-project python run_public_suite.py --project-root /path/to/project --output-dir /path/to/new-output-directory
```

The runner checks the 1.0.2 freeze manifest and all 19 declared files before execution. It takes `--project-root` and `--output-dir`; no private absolute path or unreleased secret is required. The expected result is 80/80 semantic matches across 54 mathematical cases, 12 definedness/provenance/precedence cases, and 14 malformed/type/resource cases, with no escaped implementation exception.

This evaluates structured AST inputs. It does not evaluate natural-language theorem understanding, retrieval quality, theorem novelty, execution timing, or practical impact.
