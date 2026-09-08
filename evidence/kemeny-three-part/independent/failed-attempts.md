# Retained failed or superseded attempts

1. `Get-Command pdfinfo,pdftotext,pdftoppm` returned three command-not-found errors because Poppler was not on `PATH`. No source or project file was changed. The audit then used the bundled read-only executables at `C:/Users/Legedith/.cache/codex-runtimes/codex-primary-runtime/dependencies/native/poppler/Library/bin/`; the captured `pdfinfo` and rendering attempts succeeded.

2. `logs/attempt-author-checker-adversarial-01.json` records a successful mathematical replay, but its harness subprocess invoked the uv-managed base interpreter because the command used the bare name `python`. The runner itself was in the isolated environment, but this did not meet the strongest reading of "replay in a fresh environment." Nothing from that attempt is used as final evidence. `logs/attempt-author-checker-adversarial-02.json` supersedes it and explicitly invokes `.venv-author-replay-02/Scripts/python.exe`; its report and every per-case stdout/stderr file are retained separately.

3. A post-completion evidence-gate invocation supplied an absolute value to `--bundle` and exited 1 with `absolute paths are forbidden`. It did not mutate any artifact. The immediately following invocation used the workspace-relative bundle path required by the gate.

No algebraic or source-transcription probe failed. The independent polynomial evaluator was frozen before its canonical run and was not edited afterward.
