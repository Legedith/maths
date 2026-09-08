# Structured-check inputs

`teaching/` contains the current explicitly annotated learning examples. The source formula, deliberate synthetic alteration and failed-hypothesis example are different records. See `docs/assumption-teaching-examples.md` for their scope and commands.

`weighted-counterexample.json` is the original worker development input, preserved byte for byte with its freeze manifest at commit `97b5aaf`. It deliberately applies an unweighted factor to a weighted graph. Its supplied `source_annotation` field is historical input metadata, not a finding that the cited textbook states that false formula. Use the clearly labelled files in `teaching/` for explanation or presentation.

The independently prepared 80-case evaluation and the 24-result prospective retrieval study have separate records and are not generated from these teaching examples.
