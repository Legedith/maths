from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parent

PUBLIC_FILES = [
    ".python-version",
    "pyproject.toml",
    "uv.lock",
    "extract_pdf_text.py",
    "scan_terms.py",
    "seal_review.py",
    "retrieval.json",
    "search-log.json",
    "source-notes.json",
    "term-scan.json",
    "namespace-source-check.json",
    "verdict.md",
    "logs/extract.stdout.json",
    "logs/extract.stderr.txt",
    "logs/term-scan.stdout.txt",
    "logs/term-scan.stderr.txt",
    "logs/uv-lock.txt",
    "logs/uv-sync.txt",
    "logs/local-clique-1210.6965.fetch.json",
    "logs/local-clique-1210.6965.stderr.txt",
    "logs/pdftotext-check.json",
    "logs/pdftotext-check.stdout.txt",
    "logs/pdftotext-check.stderr.txt",
    "logs/seal-attempt01.stdout.txt",
    "logs/seal-attempt01.stderr.txt",
]

LOCAL_SOURCE_FILES = [
    "sources/hu-kirkland-2019.pdf",
    "sources/hu-kirkland-2019.page-marked.txt",
    "sources/ciardo-1909.12549.pdf",
    "sources/ciardo-1909.12549.page-marked.txt",
    "sources/kim-2112.03655.pdf",
    "sources/kim-2112.03655.page-marked.txt",
    "sources/local-clique-1210.6965.html",
]

EXTERNAL_INPUTS = [
    (
        Path("D:/CodexWorkspaces/mathematics-atlas/discovery-next-work/proposal.md"),
        "proposal reviewed before the bounded post-result source check",
    ),
    (
        Path("D:/CodexWorkspaces/mathematics-atlas/discovery-next-work/source-notes.json"),
        "pre-study source notes reviewed as an input",
    ),
    (
        Path("D:/CodexWorkspaces/mathematics-atlas/kemeny-prior-art-work/source-notes.json"),
        "sealed pre-computation four-source prior-art review",
    ),
    (
        Path("D:/CodexWorkspaces/mathematics-atlas/kemeny-prior-art-work/supplement-2306.04005.json"),
        "sealed supplementary primary-source check",
    ),
    (
        Path("D:/CodexWorkspaces/mathematics-atlas/kemeny-independent-work/independent-output-seal.json"),
        "blind independent census output seal",
    ),
    (
        Path("D:/CodexWorkspaces/mathematics-atlas/kemeny-independent-work/run-01/witnesses.json"),
        "blind independent exact witness record",
    ),
    (
        Path("D:/CodexWorkspaces/mathematics-atlas/kemeny-independent-work/comparison-01/comparison.json"),
        "exact author-independent structural comparison",
    ),
    (
        Path("D:/CodexWorkspaces/mathematics-atlas/kemeny-study-work/evidence/prior-art/post-result-root-notes.json"),
        "unsealed root note consumed only as the trigger for the separate namespace check",
    ),
]


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def record(path: Path, *, base: Path | None = None, role: str | None = None) -> dict:
    result = {
        "path": path.relative_to(base).as_posix() if base else path.as_posix(),
        "bytes": path.stat().st_size,
        "sha256": sha256(path),
    }
    if role is not None:
        result["role"] = role
    return result


def validate_json_files(paths: list[Path]) -> None:
    for path in paths:
        if path.suffix == ".json":
            json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, payload: dict) -> None:
    path.write_text(
        json.dumps(payload, ensure_ascii=True, indent=2) + "\n",
        encoding="utf-8",
        newline="\n",
    )


def main() -> int:
    public_paths = [ROOT / relative for relative in PUBLIC_FILES]
    local_source_paths = [ROOT / relative for relative in LOCAL_SOURCE_FILES]
    all_required = public_paths + local_source_paths + [path for path, _ in EXTERNAL_INPUTS]
    missing = [path.as_posix() for path in all_required if not path.is_file()]
    if missing:
        raise FileNotFoundError(json.dumps(missing, indent=2))

    validate_json_files(public_paths)
    frozen_at = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
    review_seal = {
        "schema_version": "kemeny-postresult-review-seal-v1",
        "artifact_type": "independent_bounded_source_review_seal",
        "frozen_at_utc": frozen_at,
        "auditor": "/root/sol_atlas_audit",
        "status": "bounded_review_complete_no_exact_prior_art_blocker_located",
        "scope": {
            "targeted_queries": 6,
            "new_relevant_full_primary_papers": 3,
            "new_mathematical_census_run": False,
            "global_novelty_certified": False,
            "finite_census_final_semantic_gate_certified_here": False,
        },
        "findings": {
            "zero_change_single_edge_additions_are_prior_art": True,
            "general_nonadjacent_twin_edge_change_formula_is_prior_art": True,
            "generic_braess_set_and_published_p7_interaction_are_prior_art": True,
            "exact_e_question_z_w_witness_located_in_reviewed_sources": False,
            "published_minimum_order_six_located_in_reviewed_sources": False,
            "exact_prior_art_blocker_located": False,
            "namespace_source_check": "arXiv:1210.6965v1 uses kc(G) for local clique cover number, not Kemeny's constant",
        },
        "calibration": "The negative literature-search findings are bounded non-locations, not evidence of global novelty. The minimum-order statement comes from excluding orders two through five and exhibiting an order-six witness in the separately sealed census; it is not a classification of larger graphs and remains subject to its designated final semantic gate.",
        "artifacts": [record(path, base=ROOT) for path in public_paths],
        "retained_local_sources": [record(path, base=ROOT) for path in local_source_paths],
        "external_inputs": [record(path, role=role) for path, role in EXTERNAL_INPUTS],
        "publication_boundary": {
            "full_pdfs_page_marked_full_texts_and_raw_html": "retained locally; excluded from publication copy set",
            "virtual_environment_and_cache": "excluded",
            "raw_http_headers": "retained locally but excluded because they contain transient cookies",
        },
    }
    seal_path = ROOT / "review-seal.json"
    write_json(seal_path, review_seal)

    copy_paths = public_paths + [seal_path]
    manifest = {
        "schema_version": "kemeny-postresult-publication-manifest-v1",
        "artifact_type": "compact_independent_review_publication_manifest",
        "created_at_utc": frozen_at,
        "source_review_seal": record(seal_path, base=ROOT),
        "records": [
            {**record(path, base=ROOT), "copy": True}
            for path in copy_paths
        ],
        "totals": {
            "copy_files": len(copy_paths),
            "copy_bytes": sum(path.stat().st_size for path in copy_paths),
        },
        "excluded": [
            "sources/*.pdf",
            "sources/*.page-marked.txt",
            "sources/local-clique-1210.6965.html",
            ".venv/**",
            "logs/*.headers.txt",
            "empty download stderr logs not otherwise needed",
        ],
        "note": "Primary-source URLs, exact source hashes, and locators remain in source-notes.json and review-seal.json. Full texts stay in the independent staging directory only.",
    }
    manifest_path = ROOT / "publication-manifest.json"
    write_json(manifest_path, manifest)
    validate_json_files([seal_path, manifest_path])
    print(
        json.dumps(
            {
                "review_seal": record(seal_path, base=ROOT),
                "publication_manifest": record(manifest_path, base=ROOT),
                "copy_files": len(copy_paths),
                "copy_bytes": sum(path.stat().st_size for path in copy_paths),
            },
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
