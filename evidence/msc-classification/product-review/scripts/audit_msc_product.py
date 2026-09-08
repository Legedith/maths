"""Independent HTTP and source-to-view checks for the MSC subject browser."""
from __future__ import annotations

import argparse
import hashlib
import html
import json
import math
import re
import sys
import traceback
import unicodedata
import urllib.error
import urllib.parse
import urllib.request
from collections import Counter, defaultdict
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable


EXPECTED_DATA_HASHES = {
    "data/msc/subjects.json": "32fb0eddc9f189e68b9fa312e8e29c399deee65d4d282d1e61235be33a22400e",
    "data/msc/references.json": "75ecd4b71056274ad342c72a5324770e2257e0ff3a88662dfe457c9127b4bc35",
    "data/msc/summary.json": "7816ecdc34c3fe3981bef3f18a6ff0effe16e12aca5dc95460f8604dee7715ed",
}
PAGE_SIZE = 24
SUPPORTED_PREDICATES = {
    "http://msc2020.org/resources/MSC/msc2020/mscvocab#seeAlso",
    "http://msc2020.org/resources/MSC/msc2020/mscvocab#seeMainly",
    "http://msc2020.org/resources/MSC/msc2020/mscvocab#seeConditionally",
}


def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def canonical_digest(value: Any) -> str:
    return digest(json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8"))


def normalize(value: str) -> str:
    folded = unicodedata.normalize("NFKC", value).lower()
    replaced = "".join(ch if unicodedata.category(ch)[:1] in {"L", "N"} else " " for ch in folded)
    return " ".join(replaced.split())


def summary(row: dict[str, Any]) -> dict[str, Any]:
    return {
        "code": row["code"],
        "label": row["label_as_recorded"],
        "kind": row["kind"],
        "parent": row["navigation_parent_code"],
    }


@dataclass
class HttpResult:
    url: str
    method: str
    status: int
    headers: dict[str, str]
    body: bytes

    def json(self) -> Any:
        return json.loads(self.body.decode("utf-8"))


class Auditor:
    def __init__(self, project_root: Path, origin: str, raw_dir: Path) -> None:
        self.project_root = project_root
        self.origin = origin.rstrip("/")
        self.raw_dir = raw_dir
        self.raw_dir.mkdir(parents=True, exist_ok=False)
        self.checks: list[dict[str, Any]] = []
        self.http_requests = 0
        self.http_statuses: Counter[int] = Counter()
        self.http_ledger = hashlib.sha256()
        self.retained_http: list[dict[str, Any]] = []

        subject_bytes = (project_root / "data/msc/subjects.json").read_bytes()
        reference_bytes = (project_root / "data/msc/references.json").read_bytes()
        self.index = json.loads(subject_bytes)
        self.references = json.loads(reference_bytes)
        self.subjects: list[dict[str, Any]] = self.index["subjects"]
        self.by_code = {row["code"]: row for row in self.subjects}
        self.by_uri = {row["uri"]: row for row in self.subjects}
        self.collections = {row["uri"]: row for row in self.references["collections"]}
        self.children: dict[str | None, list[dict[str, Any]]] = defaultdict(list)
        self.outgoing: dict[str, list[dict[str, Any]]] = defaultdict(list)
        self.incoming: dict[str, list[dict[str, Any]]] = defaultdict(list)
        for row in self.subjects:
            self.children[row["navigation_parent_code"]].append(row)
        for relation in self.references["relations"]:
            self.outgoing[relation["from_uri"]].append(relation)
            self.incoming[relation["to_uri"]].append(relation)

    def check(self, name: str, action: Callable[[], Any], gate: str) -> None:
        try:
            detail = action()
            record: dict[str, Any] = {"name": name, "gate": gate, "passed": True}
            if detail is not None:
                record["detail"] = detail
            self.checks.append(record)
        except Exception as exc:  # retain all independent failures
            self.checks.append(
                {
                    "name": name,
                    "gate": gate,
                    "passed": False,
                    "error": f"{type(exc).__name__}: {exc}",
                    "traceback": traceback.format_exc(),
                }
            )

    def fetch(
        self,
        path: str,
        *,
        method: str = "GET",
        retain_as: str | None = None,
    ) -> HttpResult:
        url = self.origin + path
        request = urllib.request.Request(url, method=method)
        try:
            with urllib.request.urlopen(request, timeout=15) as response:
                status = response.status
                headers = {key.lower(): value for key, value in response.headers.items()}
                body = response.read()
        except urllib.error.HTTPError as exc:
            status = exc.code
            headers = {key.lower(): value for key, value in exc.headers.items()}
            body = exc.read()
        self.http_requests += 1
        self.http_statuses[status] += 1
        body_hash = digest(body)
        self.http_ledger.update(f"{method}\0{url}\0{status}\0{body_hash}\n".encode("utf-8"))
        result = HttpResult(url=url, method=method, status=status, headers=headers, body=body)
        if retain_as:
            body_path = self.raw_dir / f"{retain_as}.body.bin"
            meta_path = self.raw_dir / f"{retain_as}.json"
            body_path.write_bytes(body)
            metadata = {
                "schema_version": "msc-product-http-response-v1",
                "request": {"method": method, "url": url},
                "response": {
                    "status": status,
                    "headers": headers,
                    "body_path": body_path.name,
                    "body_bytes": len(body),
                    "body_sha256": body_hash,
                },
            }
            meta_path.write_text(json.dumps(metadata, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
            self.retained_http.append({"name": retain_as, **metadata["response"]})
        return result

    @staticmethod
    def expect(condition: bool, message: str) -> None:
        if not condition:
            raise AssertionError(message)

    def expected_search(self, query: str, parent: str) -> list[dict[str, Any]]:
        terms = normalize(query).split()
        expected: list[dict[str, Any]] = []
        for row in self.subjects:
            if parent == "root" and row["navigation_parent_code"] is not None:
                continue
            if parent not in {"root", "all"} and row["navigation_parent_code"] != parent:
                continue
            text = normalize(f"{row['code']} {row['label_as_recorded']} {row['description_as_recorded']}")
            if all(term in text for term in terms):
                expected.append(row)
        return expected

    def assert_list_page(
        self,
        result: HttpResult,
        *,
        query: str,
        parent: str,
        page: int,
        expected: list[dict[str, Any]],
    ) -> dict[str, Any]:
        self.expect(result.status == 200, f"expected HTTP 200, got {result.status} for {result.url}")
        self.expect(result.headers.get("cache-control") == "no-store", "success response lacks Cache-Control: no-store")
        value = result.json()
        expected_pages = math.ceil(len(expected) / PAGE_SIZE)
        expected_records = [summary(row) for row in expected[(page - 1) * PAGE_SIZE : page * PAGE_SIZE]]
        self.expect(value["query"] == query.strip(), "API did not preserve trimmed query")
        self.expect(value["parent"] == parent, "API parent differs")
        self.expect(value["page"] == page, "API page differs")
        self.expect(value["subjects"] == 6603 and value["topLevels"] == 63 and value["references"] == 3083, "catalogue totals differ")
        self.expect(value["metadata"] == self.index["metadata"], "API metadata differs from source index")
        self.expect(value["total"] == len(expected), "API total differs")
        self.expect(value["pageSize"] == PAGE_SIZE, "page-size contract differs")
        self.expect(value["pages"] == expected_pages, "page count differs")
        self.expect(value["records"] == expected_records, "page records or source order differ")
        self.expect(len(value["records"]) <= PAGE_SIZE, "list response exceeds page bound")
        return value

    def walk_list(self, query: str, parent: str, *, retain_prefix: str | None = None) -> dict[str, Any]:
        expected = self.expected_search(query, parent)
        query_args = {"q": query, "parent": parent, "page": "1"}
        first_path = "/api/subjects?" + urllib.parse.urlencode(query_args, quote_via=urllib.parse.quote)
        first = self.fetch(first_path, retain_as=f"{retain_prefix}-page-1" if retain_prefix else None)
        first_value = self.assert_list_page(first, query=query, parent=parent, page=1, expected=expected)
        actual_codes = [row["code"] for row in first_value["records"]]
        page_hashes = [digest(first.body)]
        for page in range(2, first_value["pages"] + 1):
            query_args["page"] = str(page)
            path = "/api/subjects?" + urllib.parse.urlencode(query_args, quote_via=urllib.parse.quote)
            response = self.fetch(path)
            value = self.assert_list_page(response, query=query, parent=parent, page=page, expected=expected)
            actual_codes.extend(row["code"] for row in value["records"])
            page_hashes.append(digest(response.body))
        self.expect(actual_codes == [row["code"] for row in expected], "pagination lost, duplicated, or reordered subjects")
        return {
            "query": query,
            "parent": parent,
            "records": len(actual_codes),
            "pages": first_value["pages"],
            "codes_sha256": canonical_digest(actual_codes),
            "page_body_hashes_sha256": canonical_digest(page_hashes),
        }

    def decorate_endpoint(self, uri: str) -> dict[str, Any]:
        if uri in self.by_uri:
            row = self.by_uri[uri]
            return {"kind": "subject", "uri": uri, "code": row["code"], "label": row["label_as_recorded"]}
        collection = self.collections[uri]
        label = next((term["value"] for term in collection["labels"] if term.get("language") == "en"), uri)
        return {"kind": "collection", "uri": uri, "code": None, "label": label}

    def expected_detail(self, code: str) -> dict[str, Any]:
        row = self.by_code[code]
        ancestors: list[dict[str, Any]] = []
        parent = row["navigation_parent_code"]
        while parent:
            ancestor = self.by_code[parent]
            ancestors.insert(0, summary(ancestor))
            parent = ancestor["navigation_parent_code"]

        def decorate(relation: dict[str, Any]) -> dict[str, Any]:
            return {
                **relation,
                "from": self.decorate_endpoint(relation["from_uri"]),
                "to": self.decorate_endpoint(relation["to_uri"]),
            }

        outgoing = self.outgoing[row["uri"]]
        related_collection_uris = list(dict.fromkeys(rel["to_uri"] for rel in outgoing if rel["target_kind"] == "collection"))
        related_collections = []
        for uri in related_collection_uris:
            collection = self.collections[uri]
            related_collections.append(
                {
                    **collection,
                    "members": [summary(self.by_uri[member]) for member in collection["member_uris"]],
                }
            )
        children = self.children[row["code"]]
        return {
            "subjects": 6603,
            "topLevels": 63,
            "references": 3083,
            "metadata": self.index["metadata"],
            "subject": row,
            "ancestors": ancestors,
            "childCount": len(children),
            "children": [summary(child) for child in children[:PAGE_SIZE]],
            "outgoing": [decorate(rel) for rel in outgoing],
            "incoming": [decorate(rel) for rel in self.incoming[row["uri"]]],
            "collections": related_collections,
        }

    def check_detail(self, code: str, retain_as: str) -> dict[str, Any]:
        response = self.fetch(f"/api/subjects?code={urllib.parse.quote(code)}", retain_as=retain_as)
        self.expect(response.status == 200, f"detail {code} returned {response.status}")
        self.expect(response.headers.get("cache-control") == "no-store", "detail response lacks no-store")
        actual = response.json()
        expected = self.expected_detail(code)
        self.expect(actual == expected, f"detail {code} differs from raw source-derived oracle")
        incident = len(actual["outgoing"]) + len(actual["incoming"])
        self.expect(incident <= 512, "detail incident references exceed bound")
        self.expect(len(actual["children"]) <= PAGE_SIZE, "detail children exceed page bound")
        self.expect(all(len(collection["members"]) <= 512 for collection in actual["collections"]), "collection exceeds bound")
        return {
            "code": code,
            "body_sha256": digest(response.body),
            "children_returned": len(actual["children"]),
            "child_count": actual["childCount"],
            "outgoing": len(actual["outgoing"]),
            "incoming": len(actual["incoming"]),
            "collections": len(actual["collections"]),
        }

    def check_data_integrity(self) -> dict[str, Any]:
        actual_hashes = {}
        for relative, expected_hash in EXPECTED_DATA_HASHES.items():
            raw = (self.project_root / relative).read_bytes()
            actual_hashes[relative] = digest(raw)
            self.expect(actual_hashes[relative] == expected_hash, f"hash drift: {relative}")
        self.expect(len(self.subjects) == 6603, "subject count differs")
        self.expect(len(self.references["relations"]) == 3083, "reference count differs")
        self.expect(len(self.children[None]) == 63, "root count differs")
        self.expect(len(self.by_code) == len(self.subjects), "duplicate subject codes")
        self.expect(len(self.by_uri) == len(self.subjects), "duplicate subject URIs")
        self.expect(self.index["metadata"]["data_license"] == "CC-BY-NC-SA-4.0", "license metadata differs")
        self.expect(
            {item["id"] for item in self.index["metadata"]["sources"]}
            == {"msc2020-official-csv", "msc2020-skos-suggestion4"},
            "source IDs differ",
        )
        for row in self.subjects:
            self.expect(row["classification_status"] == "upstream_subject_classification", f"bad subject status {row['code']}")
            self.expect(row["source_locator"]["source_id"] == "msc2020-official-csv", f"bad source locator {row['code']}")
            parent = row["navigation_parent_code"]
            self.expect(parent is None or parent in self.by_code, f"missing parent {row['code']}")
        for relation in self.references["relations"]:
            self.expect(relation["from_uri"] in self.by_uri, "missing reference source")
            self.expect(relation["to_uri"] in self.by_uri or relation["to_uri"] in self.collections, "missing reference target")
            self.expect(relation["predicate_uri"] in SUPPORTED_PREDICATES, "unsupported predicate")
            self.expect(relation["source_id"] == "msc2020-skos-suggestion4", "reference source ID differs")
            self.expect(relation["status"] == "upstream_classification_reference", "reference status differs")
            expected_kind = "subject" if relation["to_uri"] in self.by_uri else "collection"
            self.expect(relation["target_kind"] == expected_kind, "target kind differs")
            if relation["predicate_uri"].endswith("#seeConditionally"):
                self.expect(bool(relation["scope_records"]), "conditional reference lacks qualifier")
        incident = {
            row["code"]: len(self.outgoing[row["uri"]]) + len(self.incoming[row["uri"]])
            for row in self.subjects
        }
        self.expect(max(incident.values()) <= 512, "incident-reference load bound exceeded")
        self.expect(all(len(item["member_uris"]) <= 512 for item in self.collections.values()), "collection load bound exceeded")
        return {
            "hashes": actual_hashes,
            "subjects": len(self.subjects),
            "top_levels": len(self.children[None]),
            "references": len(self.references["relations"]),
            "predicate_counts": dict(Counter(rel["predicate_uri"].split("#")[-1] for rel in self.references["relations"])),
            "max_incident_references": max(incident.values()),
            "max_collection_members": max(len(item["member_uris"]) for item in self.collections.values()),
        }

    def check_all_navigation_pages(self) -> dict[str, Any]:
        summaries = [self.walk_list("", "root")]
        for parent, children in self.children.items():
            if parent is None or not children:
                continue
            summaries.append(self.walk_list("", parent))
        flattened = [row["code"] for parent in self.children.values() for row in parent]
        self.expect(len(flattened) == 6603 and len(set(flattened)) == 6603, "source hierarchy is not a partition")
        return {
            "navigation_scopes": len(summaries),
            "records_across_scopes": sum(item["records"] for item in summaries),
            "scope_summaries_sha256": canonical_digest(summaries),
        }

    def check_full_catalogue_pages(self) -> dict[str, Any]:
        return self.walk_list("", "all", retain_prefix="all-subjects")

    def check_search_pages(self) -> list[dict[str, Any]]:
        queries = ["graph theory", "68-q25", "６８Ｑ２５", "n-folds", "differential numerical"]
        return [self.walk_list(query, "all", retain_prefix=f"search-{index}") for index, query in enumerate(queries, 1)]

    def check_selected_details(self) -> list[dict[str, Any]]:
        return [
            self.check_detail("03B45", "detail-conditional"),
            self.check_detail("00A15", "detail-collection"),
            self.check_detail("32-00", "detail-hierarchy-disagreement"),
            self.check_detail("01A16", "detail-label-difference"),
            self.check_detail("00-01", "detail-empty-leaf"),
            self.check_detail("14J40", "detail-tex-string"),
            self.check_detail("01-XX", "detail-max-outgoing"),
        ]

    def check_invalid_api(self) -> dict[str, Any]:
        oversized = urllib.parse.quote("x" * 301)
        invalid_paths = [
            "/api/subjects?code=",
            "/api/subjects?code=99-XX",
            "/api/subjects?code=68-xx",
            "/api/subjects?code=68-XX&q=",
            "/api/subjects?code=68-XX&page=1",
            "/api/subjects?q=x&q=y",
            "/api/subjects?%71=x&q=y",
            "/api/subjects?parent=68-XX&parent=68-XX",
            "/api/subjects?unknown=x",
            "/api/subjects?Q=x",
            "/api/subjects?parent=99-XX",
            "/api/subjects?parent=68-xx",
            "/api/subjects?page=0",
            "/api/subjects?page=-1",
            "/api/subjects?page=01",
            "/api/subjects?page=1.0",
            "/api/subjects?page=1e1",
            "/api/subjects?page=%2B1",
            "/api/subjects?page=%201",
            "/api/subjects?page=1000001",
            f"/api/subjects?q={oversized}",
        ]
        statuses = []
        for index, path in enumerate(invalid_paths, 1):
            response = self.fetch(path, retain_as=f"invalid-{index:02d}")
            self.expect(response.status == 400, f"invalid API request was not 400: {path} -> {response.status}")
            self.expect(response.headers.get("cache-control") == "no-store", f"invalid API response lacks no-store: {path}")
            value = response.json()
            self.expect(isinstance(value, dict) and isinstance(value.get("error"), str), "invalid response lacks structured error")
            statuses.append({"path": path[:120], "status": response.status, "error": value["error"]})
        exact_limit = self.fetch(f"/api/subjects?q={urllib.parse.quote('x' * 300)}", retain_as="valid-query-limit")
        self.expect(exact_limit.status == 200, "300-character query was rejected")
        self.expect(len(exact_limit.json()["records"]) <= PAGE_SIZE, "limit response is unbounded")
        far_page = self.fetch("/api/subjects?parent=all&page=1000000", retain_as="valid-far-page")
        self.assert_list_page(far_page, query="", parent="all", page=1000000, expected=self.subjects)
        post = self.fetch("/api/subjects", method="POST", retain_as="invalid-method-post")
        self.expect(post.status == 405, f"POST should be method-not-allowed, got {post.status}")
        return {"invalid_get_cases": statuses, "exact_query_limit_status": exact_limit.status, "far_page_status": far_page.status, "post_status": post.status}

    def rendered_contains(self, body: str, value: str) -> bool:
        return value in self.rendered_text(body)

    @staticmethod
    def rendered_text(body: str) -> str:
        # React may insert an empty hydration-boundary comment between adjacent
        # text nodes. Removing only that marker keeps this an HTTP-body check.
        return html.unescape(body.replace("<!-- -->", ""))

    def check_html_views(self) -> dict[str, Any]:
        retained: dict[str, str] = {}
        paths = {
            "root": "/subjects",
            "conditional": "/subjects/03B45",
            "collection": "/subjects/00A15",
            "hierarchy": "/subjects/32-00",
            "label": "/subjects/01A16",
            "empty": "/subjects/00-01",
            "tex": "/subjects/14J40",
            "invalid": "/subjects/99-XX",
            "invalid_case": "/subjects/68-xx",
            "search": "/subjects?q=graph%20theory&parent=all&page=1",
            "duplicate_query": "/subjects?q=x&q=y",
        }
        responses: dict[str, HttpResult] = {}
        for name, path in paths.items():
            responses[name] = self.fetch(path, retain_as=f"page-{name}")
            retained[name] = digest(responses[name].body)
        for name in paths.keys() - {"invalid", "invalid_case"}:
            self.expect(responses[name].status == 200, f"page {name} returned {responses[name].status}")
        self.expect(responses["invalid"].status == 404 and responses["invalid_case"].status == 404, "invalid dynamic routes do not return 404")

        root_body = responses["root"].body.decode("utf-8")
        root_text = self.rendered_text(root_body)
        self.expect("6,603 subject categories" in root_text, "root count is absent")
        self.expect("Mathematical Reviews and zbMATH" in root_text and "MSC2020 SKOS contributors" in root_text, "attribution is absent")
        self.expect("CC BY-NC-SA 4.0" in root_text, "data terms are absent")
        for row in self.children[None][:PAGE_SIZE]:
            self.expect(self.rendered_contains(root_body, row["label_as_recorded"]), f"root label absent: {row['code']}")

        conditional = responses["conditional"].body.decode("utf-8")
        condition_detail = self.expected_detail("03B45")
        self.expect("Conditional cross-reference" in self.rendered_text(conditional), "conditional display label absent")
        for relation in condition_detail["outgoing"]:
            self.expect(self.rendered_contains(conditional, relation["predicate_uri"]), "conditional predicate URI absent")
            self.expect(self.rendered_contains(conditional, relation["from_uri"]), "conditional source endpoint absent")
            self.expect(self.rendered_contains(conditional, relation["to_uri"]), "conditional target endpoint absent")
            for scope_record in relation["scope_records"]:
                self.expect(self.rendered_contains(conditional, scope_record["uri"]), "qualifier URI absent")
                for scope in scope_record["scopes"]:
                    self.expect(self.rendered_contains(conditional, scope["value"]), "qualifier text absent")
                    self.expect(self.rendered_contains(conditional, scope["datatype"]), "qualifier datatype absent")

        collection = responses["collection"].body.decode("utf-8")
        collection_detail = self.expected_detail("00A15")["collections"][0]
        self.expect("62 categories grouped by the source" in self.rendered_text(collection), "collection count absent")
        for member in [collection_detail["members"][0], collection_detail["members"][31], collection_detail["members"][-1]]:
            self.expect(self.rendered_contains(collection, member["code"]), f"collection member absent: {member['code']}")
            self.expect(self.rendered_contains(collection, member["label"]), f"collection member label absent: {member['code']}")

        hierarchy = responses["hierarchy"].body.decode("utf-8")
        hierarchy_row = self.by_code["32-00"]
        self.expect("linked-data source records additional parents" in self.rendered_text(hierarchy), "hierarchy disagreement explanation absent")
        for uri in hierarchy_row["rdf_broader_uris"]:
            self.expect(self.rendered_contains(hierarchy, uri), "recorded RDF parent absent")

        label = responses["label"].body.decode("utf-8")
        label_row = self.by_code["01A16"]
        self.expect("use different label text" in self.rendered_text(label), "label-disagreement explanation absent")
        self.expect(self.rendered_contains(label, label_row["label_as_recorded"]), "official label absent")
        for term in label_row["rdf_labels"]:
            self.expect(self.rendered_contains(label, term["value"]), "RDF label absent")

        empty = self.rendered_text(responses["empty"].body.decode("utf-8"))
        self.expect("This is a leaf category" in empty, "empty leaf message absent")
        self.expect("No outgoing cross-reference is recorded" in empty, "empty outgoing message absent")

        tex_raw = responses["tex"].body.decode("utf-8")
        tex_value = self.by_code["14J40"]["label_as_recorded"]
        self.expect(self.rendered_contains(tex_raw, tex_value), "TeX-looking source label is absent")
        self.expect("\\(n&gt;4\\)" in tex_raw, "greater-than sign was not HTML-escaped in rendered text")

        duplicate = self.rendered_text(responses["duplicate_query"].body.decode("utf-8"))
        self.expect('role="alert"' in responses["duplicate_query"].body.decode("utf-8") and "Use one query" in duplicate, "duplicate page query lacks user-facing error")
        search = self.rendered_text(responses["search"].body.decode("utf-8"))
        for row in self.expected_search("graph theory", "all")[:PAGE_SIZE]:
            self.expect(row["label_as_recorded"] in search, f"search page label absent: {row['code']}")
        return {"retained_page_body_hashes": retained, "tex_probe": {"code": "14J40", "value": tex_value}, "empty_leaf": "00-01"}

    def run(self) -> dict[str, Any]:
        self.check("frozen data and structural source metadata", self.check_data_integrity, "source_to_view_fidelity")
        self.check("all catalogue API pages preserve source order", self.check_full_catalogue_pages, "functional_reproduction")
        self.check("all populated immediate-child API scopes preserve the hierarchy", self.check_all_navigation_pages, "functional_reproduction")
        self.check("representative normalized AND-search pages match an independent lexical oracle", self.check_search_pages, "functional_reproduction")
        self.check("selected detail API records match raw source-derived records", self.check_selected_details, "source_to_view_fidelity")
        self.check("strict API and bounded edge cases", self.check_invalid_api, "specification_compliance")
        self.check("server-rendered HTTP bodies preserve required labels, qualifiers and caveats", self.check_html_views, "implementation_alignment")
        failed = [row for row in self.checks if not row["passed"]]
        gate_status: dict[str, str] = {}
        for gate in ("source_to_view_fidelity", "specification_compliance", "implementation_alignment", "functional_reproduction"):
            scoped = [row for row in self.checks if row["gate"] == gate]
            gate_status[gate] = "pass" if scoped and all(row["passed"] for row in scoped) else "fail"
        return {
            "schema_version": "independent-msc-product-audit-v1",
            "auditor": "/root/sol_atlas_audit",
            "scope": "Code, raw data, HTTP/API behavior and server-rendered response bodies; no browser DOM, screenshot, visual, semantic-equivalence, mathematical-truth or coverage evaluation.",
            "project_root": str(self.project_root.resolve()),
            "origin": self.origin,
            "status": "pass" if not failed else "fail",
            "gates": gate_status,
            "checks": self.checks,
            "http": {
                "requests": self.http_requests,
                "statuses": {str(key): value for key, value in sorted(self.http_statuses.items())},
                "request_body_ledger_sha256": self.http_ledger.hexdigest(),
                "retained_responses": self.retained_http,
            },
            "failed_checks": len(failed),
        }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--project-root", type=Path, required=True)
    parser.add_argument("--origin", required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--raw-dir", type=Path, required=True)
    args = parser.parse_args()
    if args.output.exists():
        raise FileExistsError(f"Refusing to overwrite: {args.output}")
    auditor = Auditor(args.project_root.resolve(), args.origin, args.raw_dir.resolve())
    result = auditor.run()
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps({
        "status": result["status"],
        "gates": result["gates"],
        "checks": len(result["checks"]),
        "failed_checks": result["failed_checks"],
        "http_requests": result["http"]["requests"],
        "http_ledger_sha256": result["http"]["request_body_ledger_sha256"],
        "output": str(args.output.resolve()),
        "output_sha256": digest(args.output.read_bytes()),
    }, sort_keys=True))
    return 0 if result["status"] == "pass" else 1


if __name__ == "__main__":
    sys.exit(main())
