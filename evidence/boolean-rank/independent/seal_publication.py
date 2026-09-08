from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parent
PROJECT = Path(r"D:\CodexWorkspaces\mathematics-atlas\project")
FREEZE = Path(
    r"D:\CodexWorkspaces\mathematics-atlas\boolean-rank-integration-work"
    r"\implementation-freeze-v2.json"
)
ADMITTED = Path(
    r"D:\CodexWorkspaces\mathematics-atlas\boolean-rank-clarification-work"
    r"\corrected-records-v1.json"
)
SOURCE_REVIEW = Path(
    r"D:\CodexWorkspaces\mathematics-atlas\boolean-rank-correction-review-work"
    r"\correction-review.json"
)
CONTRACT = PROJECT / "docs" / "boolean-rank-contract.md"
BUNDLE = PROJECT / ".codex" / "evidence" / "runs" / "boolean-rank-integration-v1" / "bundle.json"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def file_record(path: Path, *, relative_to: Path | None = None) -> dict[str, object]:
    base = relative_to or ROOT
    return {
        "path": path.relative_to(base).as_posix(),
        "bytes": path.stat().st_size,
        "sha256": sha256(path),
    }


def external_record(path: Path) -> dict[str, object]:
    return {
        "path": str(path),
        "bytes": path.stat().st_size,
        "sha256": sha256(path),
    }


def canonical_write(path: Path, value: object) -> None:
    path.write_bytes(
        (json.dumps(value, ensure_ascii=True, sort_keys=True, indent=2) + "\n").encode(
            "utf-8"
        )
    )


def run_record(relative: str) -> dict[str, object]:
    path = ROOT / relative
    value = json.loads(path.read_text(encoding="utf-8"))
    return {
        **file_record(path),
        "attempt_id": value["attempt_id"],
        "returncode": value["returncode"],
        "timed_out": value["timed_out"],
        "started_at_utc": value["started_at_utc"],
        "ended_at_utc": value["ended_at_utc"],
        "stdout_sha256": value["stdout"]["sha256"],
        "stderr_sha256": value["stderr"]["sha256"],
    }


def tree_summary(paths: list[Path], label: str) -> dict[str, object]:
    records = [file_record(path) for path in sorted(paths)]
    digest_input = b"".join(
        f"{record['path']}\0{record['bytes']}\0{record['sha256']}\n".encode("utf-8")
        for record in records
    )
    return {
        "path_group": label,
        "file_count": len(records),
        "bytes": sum(int(record["bytes"]) for record in records),
        "record_list_sha256": hashlib.sha256(digest_input).hexdigest(),
        "retained_locally": True,
        "copy": False,
    }


def main() -> None:
    expected = {
        FREEZE: "391aa34b932aa37c4ccb45e2b9ee589ba3eaec38540c15f9d43b9581c420f7f6",
        CONTRACT: "a302711e12faa6526456d92a42707f94c55ff421c7afabe58f925133c071dcda",
        ADMITTED: "0ba1c19b75b0b37fcd29214d3ad5565aca747481aba779084e23367b0a110fd2",
        SOURCE_REVIEW: "13bff50ecbd050f359a7948996197e9b09a12c5a5305fedb4aa40804cefcbad0",
        BUNDLE: "d5f1f0e07be30477cb5338a53916ce7f85fd0ed840bd928e0aa9da6fb0017d50",
        ROOT / "checker-freeze.json": "c335dd28d7af4286e6603e2383352c2fe253a7fd59455f7967f7f3f37ba53539",
    }
    mismatches = {
        str(path): {"expected": digest, "actual": sha256(path)}
        for path, digest in expected.items()
        if sha256(path) != digest
    }
    if mismatches:
        raise SystemExit(f"pinned input mismatch: {json.dumps(mismatches, indent=2)}")

    independent_data = ROOT / "results" / "independent-data-02" / "independent-data-check.json"
    independent_runtime = ROOT / "results" / "independent-runtime-05" / "independent-runtime-check.json"
    canonical_validation = ROOT / "results" / "canonical" / "validation.json"
    canonical_functional = ROOT / "results" / "canonical" / "functional.json"
    canonical_navigation = ROOT / "results" / "canonical" / "navigation.json"
    data_value = json.loads(independent_data.read_text(encoding="utf-8"))
    runtime_value = json.loads(independent_runtime.read_text(encoding="utf-8"))
    validation_value = json.loads(canonical_validation.read_text(encoding="utf-8"))
    functional_value = json.loads(canonical_functional.read_text(encoding="utf-8"))
    navigation_value = json.loads(canonical_navigation.read_text(encoding="utf-8"))
    assert data_value["passed"] and len(data_value["checks"]) == 22
    assert runtime_value["passed"] and len(runtime_value["checks"]) == 6
    assert validation_value["passed"]
    assert functional_value["passed"] and functional_value["check_count"] == 9
    assert navigation_value["passed"] and navigation_value["navigation_pairs"] == 1600

    runs = [
        run_record("logs/data/attempt-independent-data-02.json"),
        run_record("logs/runtime/attempt-independent-runtime-05.json"),
        run_record("logs/canonical/attempt-canonical-validation-01.json"),
        run_record("logs/canonical/attempt-canonical-functional-01.json"),
        run_record("logs/canonical/attempt-canonical-navigation-01.json"),
        run_record("logs/canonical/attempt-canonical-pytest-01.json"),
    ]
    assert all(run["returncode"] == 0 and not run["timed_out"] for run in runs)

    report = {
        "schema_version": "boolean-rank-integration-independent-product-audit-v1",
        "audited_at_utc": datetime.now(timezone.utc).isoformat(),
        "auditor": {
            "identity": "/root/sol_atlas_audit",
            "role": "independent product auditor and earlier integration-design author",
            "implementation_author": False,
            "role_disclosure": (
                "The auditor previously authored nonbinding integration-design advice. "
                "Root authored the 49-file implementation; this audit compares it directly "
                "with the admitted corrected records and upstream independent source review."
            ),
        },
        "overall_status": "PASS_SCOPED",
        "reviewed_snapshot": {
            "freeze": external_record(FREEZE),
            "verified_file_count": 49,
            "all_frozen_hashes_matched": True,
            "newline_delta": (
                "Freeze v2 differs from v1 only by CRLF-to-LF normalization of atlas.json, "
                "README.md and integration-projection.json; parsed JSON values and text lines "
                "were retained by the author's correction record. The audit used v2 bytes."
            ),
        },
        "inputs": {
            "contract": external_record(CONTRACT),
            "admitted_corrected_records": external_record(ADMITTED),
            "upstream_independent_correction_review": external_record(SOURCE_REVIEW),
            "checker_freeze": file_record(ROOT / "checker-freeze.json"),
            "author_bundle_draft": external_record(BUNDLE),
        },
        "four_checks": [
            {
                "id": "implementation_alignment",
                "status": "PASS",
                "auditor": "/root/sol_atlas_audit",
                "note": (
                    "Actual data, TypeScript types, API, find_connection tool and connection "
                    "rendering retain every admitted R1-R4 semantic field. All old corpus records "
                    "remain value-identical to baseline; the release adds exactly 7 nodes, 8 "
                    "edges, 2 sources and 2 journeys."
                ),
                "evidence": [
                    file_record(independent_data),
                    file_record(independent_runtime),
                    file_record(ROOT / "results" / "canonical" / "functional.json"),
                    file_record(ROOT / "results" / "canonical" / "functional-rendered.json"),
                ],
            },
            {
                "id": "reproduction",
                "status": "PASS",
                "auditor": "/root/sol_atlas_audit",
                "note": (
                    "Frozen independent checks and four canonical replays all exited zero: "
                    "22/22 independent data checks, 15/15 fresh malformed cases, 6/6 runtime "
                    "checks, structural validation, 9/9 author functional checks, 1,600 "
                    "ordered navigation pairs and 35 targeted pytest cases."
                ),
                "evidence": [
                    file_record(independent_data),
                    file_record(independent_runtime),
                    file_record(canonical_validation),
                    file_record(canonical_functional),
                    file_record(canonical_navigation),
                    run_record("logs/canonical/attempt-canonical-pytest-01.json"),
                ],
            },
            {
                "id": "source_verification",
                "status": "PASS",
                "auditor": "/root/sol_atlas_audit",
                "note": (
                    "Scoped product-source gate: the implementation exactly projects the four "
                    "relationships admitted by the pinned independent correction review. This "
                    "audit checked source IDs, URLs, locators, scope limits and local-convention "
                    "attribution; it did not perform a new primary-paper entailment review."
                ),
                "evidence": [
                    external_record(ADMITTED),
                    external_record(SOURCE_REVIEW),
                    file_record(independent_data),
                ],
            },
            {
                "id": "specification_compliance",
                "status": "PASS",
                "auditor": "/root/sol_atlas_audit",
                "note": (
                    "The frozen implementation meets the contract's typed schema, exact addition "
                    "counts, old-record preservation, source/witness/boundary/notation display, "
                    "strict malformed-input behavior, search and navigation requirements."
                ),
                "evidence": [
                    external_record(CONTRACT),
                    file_record(independent_data),
                    file_record(independent_runtime),
                    file_record(canonical_validation),
                ],
            },
        ],
        "source_matrix": [
            {
                "relationships": ["R1", "R2", "R4"],
                "source": "Local Clique Covering of Graphs",
                "url": "https://arxiv.org/pdf/1210.6965v1",
                "locator": (
                    "printed p. 2, Boolean-rank, rectangle-cover, biclique-cover and "
                    "biadjacency paragraphs; first lines of printed p. 3 for lr_B(A)=lbc(G)"
                ),
                "product_scope": (
                    "Supports the factor/rectangle, fixed-bipartition rectangle/biclique and "
                    "local incidence correspondences. Atlas empty-support conventions are "
                    "separate local definitions."
                ),
            },
            {
                "relationships": ["R3"],
                "source": "Non-deterministic Communication Complexity with Few Witnesses",
                "url": (
                    "https://www.math.ias.edu/~avi/PUBLICATIONS/MYPAPERS/SAKS/KCOVER/"
                    "JOURNAL/kcover.pdf"
                ),
                "locator": "printed p. 3 Section 2.1; p. 4 Section 2.2; p. 5 Proposition 3 and proof",
                "product_scope": (
                    "Supports unrestricted kappa, maximum-leaf-depth n(f), and the ceiling-log "
                    "relation when the 1-support is nonempty. The all-zero totalization and Atlas "
                    "superscript notation are explicitly local."
                ),
            },
        ],
        "material_alignment_findings": [
            {
                "id": "R1-two-inequalities",
                "status": "supported",
                "locator": "project/data/atlas.json:2182 and 2192-2211",
                "finding": (
                    "A k-factor Boolean factorization yields at most k nonempty rectangles; a "
                    "t-rectangle cover yields exactly t factors. The two inequalities, rather "
                    "than false exact-k preservation after omission, prove equality of minima."
                ),
            },
            {
                "id": "R3-domain-and-notation",
                "status": "supported",
                "locator": "project/data/atlas.json:2277-2308",
                "finding": (
                    "The source-backed nonzero formula is separated from the Atlas all-zero "
                    "definition; M_f, maximum leaf depth, n(f) versus n_1(f), unrestricted kappa "
                    "versus kappa_1, and the deterministic-complexity boundary are all visible."
                ),
            },
            {
                "id": "R4-participation-objective",
                "status": "supported",
                "locator": "project/data/atlas.json:2329-2356",
                "finding": (
                    "The equality preserves row/column-to-vertex participation. The product "
                    "explicitly excludes per-cell or per-edge witness multiplicity."
                ),
            },
            {
                "id": "semantic-display-and-api",
                "status": "supported",
                "locator": (
                    "project/lib/atlas.ts:19-51; project/components/atlas-map.tsx:50-88; "
                    "project/app/api/atlas/route.ts:1-6; project/lib/use-atlas-tools.ts:135-159"
                ),
                "finding": (
                    "Typed fields survive the API and find_connection path and are rendered as "
                    "source scope, forward/reverse/result witnesses, local cases and notation."
                ),
            },
            {
                "id": "malformed-record-guards",
                "status": "supported",
                "locator": "project/scripts/validate_atlas.py:81-106 and 133-166",
                "finding": (
                    "The validator enforces complete admitted-translation fields and safe, "
                    "hash-matched curation references. Fifteen independently generated malformed "
                    "cases were rejected without traceback."
                ),
            },
        ],
        "reproduction": {
            "successful_runs": runs,
            "outputs": [
                file_record(independent_data),
                file_record(independent_runtime),
                file_record(ROOT / "results" / "independent-runtime-05" / "geometry.json"),
                file_record(ROOT / "results" / "independent-runtime-05" / "rendered-connections.json"),
                file_record(canonical_validation),
                file_record(canonical_functional),
                file_record(ROOT / "results" / "canonical" / "functional-rendered.json"),
                file_record(canonical_navigation),
            ],
            "author_build_context": (
                "The author's production build attempt boolean-build-01 exited zero before the "
                "value-preserving LF-only correction. This audit independently loaded the final "
                "v2 data and runtime modules and exercised the live final product, but did not "
                "repeat the production build."
            ),
        },
        "bundle_draft_claim_review": {
            "bundle": external_record(BUNDLE),
            "approved_claim_ids": ["C001", "C002", "C003", "C004", "C005", "C006", "C007"],
            "note": (
                "The seven current statements are aligned with their cited artifacts and retain "
                "the historical/final-run distinctions. Approval is limited to the draft bytes "
                "identified above; later bundle changes require an explicit delta review."
            ),
        },
        "retained_checker_history": [
            {
                "attempt": "independent-data-01",
                "classification": "auditor-checker false failure",
                "reason": "Raw Markdown matching did not normalize backticks and whitespace.",
                "retained": file_record(ROOT / "logs" / "data" / "attempt-independent-data-01.json"),
            },
            {
                "attempts": ["independent-runtime-01", "independent-runtime-02", "independent-runtime-03"],
                "classification": "auditor-loader failures before assertions",
                "reason": "The custom ESM loader needed React CommonJS named-export interop.",
                "retained": [
                    file_record(ROOT / "logs" / "runtime" / f"attempt-{name}.json")
                    for name in ("independent-runtime-01", "independent-runtime-02", "independent-runtime-03")
                ],
            },
            {
                "attempt": "independent-runtime-04",
                "classification": "auditor-checker false failure after 5 of 6 checks passed",
                "reason": (
                    "The HTTP assertion searched raw streamed HTML for adjacent dynamic text; "
                    "React inserted an empty comment separator. V6 removes only comment "
                    "separators before checking the same count and scope text."
                ),
                "retained": file_record(ROOT / "logs" / "runtime" / "attempt-independent-runtime-04.json"),
            },
        ],
        "limitations": [
            "No browser DOM, screenshot or visual-quality audit was performed or is claimed.",
            "The finite teaching illustration and role pilot are outside this product gate.",
            "Structural and functional checks do not independently prove the cited mathematics; source entailment rests on the pinned upstream independent correction review.",
            "No formal-proof, retrieval-quality, discovery, novelty, prevalence or practical-impact claim is supported by this audit.",
            "The live HTTP check used the already running localhost:8598 IPv6-bound server; server startup portability was not re-evaluated here.",
        ],
        "material_defects": [],
        "required_changes": [],
    }
    report_path = ROOT / "final-boolean-rank-integration-audit.json"
    canonical_write(report_path, report)

    copy_paths: set[Path] = {
        report_path,
        ROOT / "seal_publication.py",
        ROOT / "checker-freeze.json",
        ROOT / "checker-freeze-v1.json",
        ROOT / "checker-freeze-v2.json",
        ROOT / "checker-freeze-v3.json",
        ROOT / "checker-freeze-v4.json",
        ROOT / "checker-freeze-v5.json",
        ROOT / "environment.json",
        ROOT / "freeze_checker.py",
        ROOT / "independent_data_check.py",
        ROOT / "independent_runtime_check.mjs",
        ROOT / "pyproject.toml",
        ROOT / "run_logged.py",
        ROOT / "uv.lock",
    }
    for directory in (ROOT / "history", ROOT / "logs"):
        copy_paths.update(path for path in directory.rglob("*") if path.is_file())
    copy_paths.update(
        {
            ROOT / "results" / "independent-data-01" / "freeze-hash-verification.json",
            ROOT / "results" / "independent-data-01" / "independent-data-check.json",
            ROOT / "results" / "independent-data-02" / "freeze-hash-verification.json",
            ROOT / "results" / "independent-data-02" / "independent-data-check.json",
            ROOT / "results" / "independent-runtime-04" / "geometry.json",
            ROOT / "results" / "independent-runtime-04" / "independent-runtime-check.json",
            ROOT / "results" / "independent-runtime-04" / "rendered-connections.json",
            ROOT / "results" / "independent-runtime-05" / "geometry.json",
            ROOT / "results" / "independent-runtime-05" / "independent-runtime-check.json",
            ROOT / "results" / "independent-runtime-05" / "rendered-connections.json",
        }
    )
    copy_paths.update(
        path for path in (ROOT / "results" / "canonical").rglob("*") if path.is_file()
    )
    for path in (ROOT / "results" / "independent-data-02" / "malformed").rglob("*"):
        if path.is_file() and path.name != "corpus.json":
            copy_paths.add(path)

    omitted_attempt1 = [
        path
        for path in (ROOT / "results" / "independent-data-01" / "malformed").rglob("*")
        if path.is_file()
    ]
    omitted_success_corpora = [
        path
        for path in (ROOT / "results" / "independent-data-02" / "malformed").rglob("corpus.json")
        if path.is_file()
    ]
    manifest = {
        "schema_version": "boolean-rank-integration-independent-publication-manifest-v1",
        "created_at_utc": datetime.now(timezone.utc).isoformat(),
        "auditor": "/root/sol_atlas_audit",
        "scope": (
            "Compact publication set for the frozen Boolean-rank integration product audit. "
            "Full deterministic mutation corpora remain locally retained to avoid duplicating "
            "large atlas values in the public evidence copy."
        ),
        "report": file_record(report_path),
        "records": [
            {**file_record(path), "copy": True}
            for path in sorted(copy_paths)
        ],
        "retained_local_groups": [
            {
                **tree_summary(
                    omitted_attempt1,
                    "results/independent-data-01/malformed/**",
                ),
                "reason": (
                    "The retained attempt-01 summary and command logs document the checker false "
                    "failure; attempt-02 republishes the same generated malformed-case evidence."
                ),
            },
            {
                **tree_summary(
                    omitted_success_corpora,
                    "results/independent-data-02/malformed/*/corpus.json",
                ),
                "reason": (
                    "Each full mutated atlas is deterministically regenerated by the frozen "
                    "independent checker; commands, validator reports and raw stdout/stderr are "
                    "included for every case."
                ),
            },
        ],
        "external_inputs_not_copied_here": [
            external_record(FREEZE),
            external_record(CONTRACT),
            external_record(ADMITTED),
            external_record(SOURCE_REVIEW),
            external_record(BUNDLE),
        ],
        "manifest_self_excluded": True,
    }
    canonical_write(ROOT / "publication-manifest.json", manifest)


if __name__ == "__main__":
    main()
