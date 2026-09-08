# Reproduce the MSC classification index

From the repository root, using uv and a new output directory:

```powershell
uv run --project experiments/msc-index --frozen python experiments/msc-index/import_msc.py --source-root experiments/msc-index/inputs --output-dir work/msc-index-run
```

The three generated JSON files must match `data/msc/subjects.json`, `references.json` and `summary.json` byte-for-byte. The pinned official CSV, suggested Turtle and source-manifest are included. No source is fetched at runtime. Source attribution and dataset terms are in [the data notice](../../data/msc/NOTICE.md).

The source Turtle contains a placeholder date, `2021-03-xx`; RDFLib reports that retained metadata warning during parsing. The importer does not consume the date. Existing output paths are rejected and left unchanged.

Independent source and adapter verification is required before publication. The [contract](contract-v1.md) states the exact boundary: classification navigation and faithfully retained source references, not new mathematical knowledge.
