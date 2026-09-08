# MathGloss as a reusable concept and identity backbone

## Recommendation

Use MathGloss as a **pinned metadata and outbound-link seed**, not as the authority for concept identity, pedagogical order, or mathematical relationships. Its strongest reusable field is the Wikidata QID already attached to each row. Import only the QID, recorded label, source names, and source URLs; attach the exact MathGloss commit/path/row and mark every mapping as an unreviewed MathGloss assertion. Do not import definitions, linked prose, or relation files in the minimal pass.

Use MaRDI only as an optional, separately namespaced identifier crosswalk. A MaRDI `Q` number and a Wikidata `Q` number are different identifier spaces. Store the full MaRDI entity URI and connect it to a Wikidata QID only when the MaRDI item has external-ID property P12. Do not merge records by label.

This gives the atlas a useful discovery layer while preserving three boundaries:

1. a shared label is not evidence of equivalence;
2. a source link is not permission to duplicate that source's prose;
3. a MathGloss or MaRDI assertion remains attributable to its source and snapshot until reviewed.

## Evidence boundary

The review pins MathGloss repository commit [`b8f659605486f80f2816515f525af2c395c711fa`](https://github.com/MathGloss/MathGloss/tree/b8f659605486f80f2816515f525af2c395c711fa) (git tree `8095d87e49a050b7e034cf8771266fea6c488142`), the 2023 paper [arXiv:2311.12649v1](https://arxiv.org/html/2311.12649v1), and mardiclient commit [`5d827473a992234b06f86e78f35a63dd16bfb971`](https://github.com/MaRDI4NFDI/mardiclient/tree/5d827473a992234b06f86e78f35a63dd16bfb971). MaRDI API responses were retrieved on 2026-09-08. The content inspection was deliberately small; it supports the import design but no claim about overall mapping accuracy or error prevalence.

## What MathGloss supplies

The paper describes MathGloss as a linked database for undergraduate mathematical concepts drawn from several resources. It says terms are organized through Wikidata mappings, some produced with `wikimapper` and some manually. It also says undesirable mappings can result from overloaded words and places systematic verification of Wikidata mappings in future work. These are direct statements in [section 2](https://arxiv.org/html/2311.12649v1#S2) and [section 6](https://arxiv.org/html/2311.12649v1#S6).

The beginner scope is mixed. The Chicago subset is described as undergraduate-oriented but non-exhaustive and dependent on the first author's courses and interests; nLab is explicitly described as not intended for undergraduates. See [sections 3.1 and 3.4](https://arxiv.org/html/2311.12649v1#S3). MathGloss therefore offers useful destinations for learners but does not itself provide a complete curriculum, difficulty scale, prerequisite order, or reviewed equivalence relation.

The current repository has a simple machine-readable core:

| Artifact | Exact schema or role | Provenance carried in the artifact |
|---|---|---|
| [`data/database.csv`](https://github.com/MathGloss/MathGloss/blob/b8f659605486f80f2816515f525af2c395c711fa/data/database.csv) | `Wikidata ID,Wikidata Label`, then paired `BCT/Chicago/Clowder/Context/Mathlib/nLab/PlanetMath Name,Link` columns | QID, recorded label, per-source name and URL |
| Per-source term lists | `title,link` or `title,link,suggestion` | Source title and URL; no identity decision |
| [`data/alignments/compiled/*`](https://github.com/MathGloss/MathGloss/tree/b8f659605486f80f2816515f525af2c395c711fa/data/alignments/compiled) | `Wikidata ID,Title,Link,Label,Layer,Score,Reason,Alternates,Provenance` | Mapping method fields exist here, but are absent from the canonical database CSV |
| [`data/relations/graph_edges.csv`](https://github.com/MathGloss/MathGloss/blob/b8f659605486f80f2816515f525af2c395c711fa/data/relations/graph_edges.csv) | `source_id,source_label,property_id,property_label,target_id,target_label` | Wikidata-derived edge representation; no per-row retrieval revision in the CSV |
| [`data/relations/chicago_llm_relations.csv`](https://github.com/MathGloss/MathGloss/blob/b8f659605486f80f2816515f525af2c395c711fa/data/relations/chicago_llm_relations.csv) | Includes `relation,confidence,context,model,cache_hit` | Explicitly a model-assisted cache; unsuitable for the minimal identity import |

The main CSV does not carry mapping confidence, manual-review status, source retrieval time, license, or a relation between its paired source links beyond their being placed on the same QID row. Those fields must not be inferred.

## License findings

| Material | Exact declaration found | Reuse consequence |
|---|---|---|
| MathGloss paper | [arXiv v1 displays CC BY 4.0](https://arxiv.org/abs/2311.12649). | The paper can be cited and summarized under that license. This does not license every linked corpus. |
| MathGloss repository code | The pinned root [`LICENSE`](https://github.com/MathGloss/MathGloss/blob/b8f659605486f80f2816515f525af2c395c711fa/LICENSE) is the MIT text, and GitHub's license API classifies it as SPDX `MIT`. | Reusing repository code requires retaining the notice. The notice unexpectedly names `GitHub, Inc.` as copyright holder, so this review does not infer ownership beyond the file's text. |
| MathGloss data and hosted content | The pinned [`README.md`](https://github.com/MathGloss/MathGloss/blob/b8f659605486f80f2816515f525af2c395c711fa/README.md#license-and-citation) says “MathGloss is released under the repository's LICENSE.” No separate database/content license or per-source rights inventory was found in the snapshot. | Treat the repository's MIT declaration as the project's stated license, but avoid duplicating Chicago definitions or third-party corpus prose because the repository does not establish the rights chain for each incorporated source. Metadata and outbound links are the safe minimal use. |
| MaRDI client code | Pinned [`pyproject.toml`](https://github.com/MaRDI4NFDI/mardiclient/blob/5d827473a992234b06f86e78f35a63dd16bfb971/pyproject.toml#L11) declares `BSD-3-Clause` and a BSD classifier. GitHub's license endpoint returns 404 because the repository has no root license file. | The design does not need to vendor this client; use the public HTTP APIs. If code reuse is later desired, obtain/retain the missing license text first. |
| MaRDI portal data/content | The live Action API reports empty `rightsinfo` (`{"url":"","text":""}`). The official [portal disclaimer](https://portal.mardi4nfdi.de/wiki/Project:General_disclaimer) says use is subject to applicable data licenses and directs users to each entry for its license. | No blanket portal-data license was established. Retain identifiers/links and inspect a record's own license before copying any substantive content. |

The license scan and exact raw responses are retained in `logs/16-mathgloss-license-scan.txt`, `raw/mardi-siteinfo.json`, and `raw/github-mathgloss-license.json`.

## MaRDI identifier comparison

MaRDI is useful as a richer identifier and provenance layer, but its local IDs must remain namespaced:

- Live site information gives the concept base URI `https://portal.mardi4nfdi.de/entity/` and enumerates Wikibase property datatypes in the [Action API](https://portal.mardi4nfdi.de/w/api.php?action=query&meta=siteinfo&siprop=general%7Crightsinfo&format=json).
- MaRDI property [P12](https://portal.mardi4nfdi.de/wiki/Property:P12) is an `external-id` labeled “Wikidata QID,” described as the corresponding Wikidata QID, with formatter URL `https://www.wikidata.org/wiki/$1`.
- The official [mardiclient README](https://github.com/MaRDI4NFDI/mardiclient/blob/5d827473a992234b06f86e78f35a63dd16bfb971/README.md#L40-L41) explicitly distinguishes Wikidata prefixes (`wd:`, `wdt:`) from MaRDI identifiers.
- A bounded live SPARQL query returned pairs such as MaRDI `https://portal.mardi4nfdi.de/entity/Q100002` and Wikidata `Q27860816`. The corresponding Action API record exposes `id`, `type`, `lastrevid`, `modified`, multilingual labels/descriptions, claims keyed by property, statement IDs/ranks, typed values, qualifiers/references when present, and sitelinks. The [MaRDI Knowledge Graph API page](https://portal.mardi4nfdi.de/wiki/Service:6775567) identifies the Action API as the official machine interface; the [query service](https://query.portal.mardi4nfdi.de/) exposes SPARQL.

The richer schema can preserve statement-level references and qualifiers, but their presence is record-dependent. The inspected P12 assertion on Q100002 has a statement ID and rank but no reference block. Do not turn “schema can represent provenance” into “every assertion is sourced.”

## Minimal import record

Use a record shaped like this:

```json
{
  "id": "wikidata:Q181296",
  "label_as_recorded": "abelian group",
  "links_as_recorded": [
    {
      "source": "Chicago",
      "name_as_recorded": "abelian group",
      "url": "https://mathgloss.github.io/MathGloss/chicago/abelian_group"
    }
  ],
  "asserted_by": "MathGloss",
  "source_snapshot": {
    "commit": "b8f659605486f80f2816515f525af2c395c711fa",
    "path": "data/database.csv",
    "csv_line": 1445
  },
  "identity_review": "unreviewed",
  "content_policy": "metadata_and_link_only",
  "mardi_crosswalks": []
}
```

Apply these deterministic rules:

1. Accept only a syntactically valid Wikidata QID and non-empty HTTP(S) source links.
2. Key by `wikidata:Q…`, not the label. Preserve every source's own recorded name.
3. Record the immutable MathGloss commit, file, and CSV line. If importing from a compiled alignment, additionally retain `Layer`, `Score`, `Reason`, `Alternates`, and `Provenance` verbatim.
4. Set identity review to `unreviewed` on import. Label normalization may route review; it may not merge records or prove equivalence.
5. Queue scope differences for review. In the fixed sample, the row labeled `random variable` links a PlanetMath entry named `Weibull random variable`, and `conditional probability` links one named `regular conditional probability`. These observations do not prove either mapping wrong; they show why label matching is insufficient.
6. Add a MaRDI crosswalk only as `{ "uri": "https://portal.mardi4nfdi.de/entity/Q…", "via_property": "P12", "wikidata_qid": "Q…", "statement_id": "…", "lastrevid": … }`. Keep the MaRDI URI and Wikidata ID distinct.
7. Never ingest `chicago/*.md`, descriptions from linked sources, or `data/relations/*` in this first pass. Relationships require their own source-specific evidence and license review.
8. Refresh by producing a new pinned snapshot and diffing records; never mutate away the old source locator.

## Fixed sample

The complete metadata/link-only records are in [`records/sample-metadata-records.json`](records/sample-metadata-records.json). They were extracted by the retained uv-run script and contain no definitions or inferred relationships.

| Wikidata ID | Label recorded by MathGloss | Present source links | Pinned CSV line |
|---|---|---|---:|
| Q181296 | abelian group | Chicago, nLab, PlanetMath | 1445 |
| Q178546 | determinant | BCT, Chicago, Mathlib, nLab, PlanetMath | 1418 |
| Q230655 | connected graph | Chicago, nLab, PlanetMath | 1917 |
| Q1006032 | discrete Fourier transform | nLab, PlanetMath | 8 |
| Q1028292 | Grover's algorithm | nLab | 32 |
| Q1028209 | Deutsch–Jozsa algorithm | nLab | 31 |
| Q163310 | Turing machine | Mathlib, nLab, PlanetMath | 1111 |
| Q341835 | Ackermann function | Mathlib, PlanetMath | 2527 |
| Q176623 | random variable | nLab, PlanetMath | 1380 |
| Q327069 | conditional probability | Mathlib, PlanetMath | 2464 |

The sample confirms that computer-science-related entries exist, including quantum algorithms, computability, and a transform used in computation. It is a purposive schema sample, not a random sample and not an accuracy evaluation.

## Reproducibility artifacts

- `records/retrieval-ledger.jsonl`: typed source records and exact locators.
- `records/claim-evidence.jsonl`: material claims linked to source records.
- `records/sample-metadata-records.json`: ten pinned metadata/link-only examples.
- `scripts/extract_sample.py`: deterministic extractor, run with uv.
- `logs/`: chronological commands, successful responses, and failed retrieval/query attempts.
- `raw/`: pinned repository snapshot and raw API/HTML responses.
- `logs/15-file-hashes.json`: SHA-256 and byte size for the principal raw and derived artifacts.

No concept equivalence, prerequisite edge, licensing conclusion beyond the located declarations, or overall quality rate is claimed.
