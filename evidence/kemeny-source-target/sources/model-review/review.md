# Independent source audit

Status: PASS, bounded source support only. Auditor: astra_damage_symbolic, distinct from source investigator. No required correction. No new retrieval, evaluator, code execution, or repository write. This does not independently re-certify the reviewer's own earlier mathematical proposal or approve a release.

The frozen source notes (SHA256 14b9a376fcf7323f055fccc9b47c61e710350638c346fb33b0bd0f603d3dfadf) and manifest (3404c2c4729286a1a0288095152cd39eb45a4cb55fe74841db7ecf56b1aa60fb) match. All 13 manifest entries were checked against actual bytes; input-hash-check.json retains expected and observed hashes.

## Request and access record

Root request-01 contains three search_query entries, request-02 one DOI open, request-03 one search_query entry: exactly four queries and one attempted direct open. Investigator request-01 has one repository open; request-02 has one requirements open plus one dataset click. Thus three additional page accesses means two opens and one click, not three open-array entries. Zero new searches and zero finds is accurate. These counts come from original structured requests, not reconstructed history.

Root raw-02 explicitly records DOI HTTP 403. Root raw-03 first result is indexed text attributed to the ACM publisher URL; it contains actual author/article passages, not only metadata or an AI summary. It has discontinuities and omitted equations/sections, so it is not a verified complete article/PDF. The retained AI-summary heading is not evidence for the reviewed attributions. The incomplete direct access does not negate the retained publisher passages or imply absence of other results in the full paper.

## Primary support and precise comparison

[Martinez, Cinus, Bonchi and Vitria, ACM TIST 2025](https://doi.org/10.1145/3744658): root raw-03 first publisher result, bibliographic header, supports volume 16(4), article 93, publication 18 August 2025. Section 1 describes directed d-regular probability-weighted recommendation graphs, random-walk target reachability, probability-preserving outgoing-link replacement and continuous probability adjustment. Its algorithm paragraphs describe greedy rank-one changes; Section 7 explicitly names BGS and SLSQP with analytical gradients and projection. Sections 3-4 identify relevance constraints and the directed recommendation model. These support the notes' broad prior-work attribution.

An important convention retained in Section 4: GAR averages target hitting paths from non-target starting nodes. The proposed model includes source=target with zero hitting time and allows a nonuniform mixed target law. Thus exact normalization should be checked before any implementation comparison. The notes do not assert an identical normalization. Directed probability rewiring under relevance constraints differs from inserting one absent undirected conductance with actual changing volume and interval relative regret. This supports partial overlap and non-established equivalence only, not proof that no theorem elsewhere covers the proposal. Broad reachability optimization and rank-one methods must remain credited as known; no generic novelty clearance follows.

## Repository and terms

[Author repository](https://github.com/alexmartinezmiguel/reachability), investigator raw-01 lines 148-160 and 184-238, supports the script inventory, BGS/SLSQP usage, and NELAGT-2022 preprocessing instructions (line 210). This is README-level description, not inspection or verification of the algorithms' source implementations. [Requirements](https://raw.githubusercontent.com/alexmartinezmiguel/reachability/main/requirements.txt), raw-02 lines 48,73,84, supports NumPy 1.24.4, SciPy 1.10.1, SymPy 1.12. The inspected root/README does not visibly provide a Python-version pin, result hashes, or code license. This does not establish absence elsewhere, or legal prohibition. Dataset click failure is explicit in raw-02; dataset terms remain unverified. The publisher page's article license is not evidence of repository-code or dataset terms. The source revision is main rather than an immutable commit pin.

The suggested synthetic comparison is future work, conditional on model alignment and terms/revision checks. Neither the paper's reported empirical improvements nor public repository visibility demonstrate benefit of the proposed theorem or authorize code/data reuse. No reproduction, benchmark, download approval, or physical validation is established.

## Scoped gates

Specification compliance PASS: retained primary evidence only, no additional queries or evaluator.
Source entailment PASS: precise narrow attributions supported by author publisher passages and repository records.
Methodological integrity PASS: original request arrays, failures and every manifest hash checked; excerpt/fulltext distinction preserved.
Conclusion integrity PASS: partial overlap and bounded access gaps; no absence, novelty, benefit, or reuse-authorization inference. No release or hosted-CI gate.
