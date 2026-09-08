# Frozen multipartite sign certificate

The full theorem, source formula, finite-support argument, ranking result,
reproduction command, and limitations are in
[the research note](../../docs/kemeny-network-design.md).

This package's certificate is copied byte-for-byte from the selected
arbitrary-part-count proposal. `verify_certificate.py` reconstructs its
polynomial using only Python integer arithmetic and fixes the accepted
certificate hash. Altering the certificate requires a new proof review.

The original candidate used SymPy for discovery. Its first symbolic attempt
omitted the singleton contribution to a cubic moment. That attempt is invalid
and retained in the author history. The corrected expression and certificate
were independently reconstructed before acceptance. The portable checker
uses the corrected moments directly, with every singleton contributing one.

The earlier three-part certificate remains in its own package as history.
The arbitrary-part-count theorem contains that case.
