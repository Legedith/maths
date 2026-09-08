# Reuse MathGloss as a searchable concept and resource library

Prospective integration contract, 2026-09-08. The existing structured-checker
evaluation remains a separate milestone. This expansion does not claim that a
metadata import is a complete map of mathematics.

The user needs to find an existing mathematical concept and explore the
resources that describe it, including computer science concepts. Reuse the
independently reviewed MathGloss metadata/link export from commit
`b8f659605486f80f2816515f525af2c395c711fa`; retain its attribution, snapshot,
record keys, physical source locators and unreviewed identity/mapping status.
Do not fetch or copy the linked definitions or infer semantic edges from shared
labels. Integration follows the independent importer verdict.

Expose the complete accepted catalog through an accessible resource-library
view. Search recorded labels, resource names and Wikidata QIDs using documented
lexical matching. Let a user restrict matches to an available resource source.
Return deterministic ordering, total matching count and bounded pages without
silently dropping records. A search miss is not evidence of novelty.

Every displayed result must identify MathGloss as the source of the proposed
mapping, show its resource names and links, and offer the pinned source record.
Do not claim that importing a link verifies concept identity, resource quality,
availability, learner level or a mathematical theorem. Explain this briefly in
the library view, without replacing useful content with audit machinery.

Verification must compare the integrated catalog bytes to the audited export,
account for every accepted record and retained link, check Unicode fidelity,
and exercise search/filter/pagination against independently selected records.
Require an independent review of the integration and a focused check that any
WebMCP action updates the same visible search state as the ordinary form. Keep
the existing graph lab and research/formal search capabilities working.
