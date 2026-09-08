# Independent audit specification

Run id: `kemeny-three-part-independent-review-20260908`

## Frozen objective

Independently audit the selected branch-3 proof of the following statement:

> For all integers `a,b,c >= 3` and `p >= 1`, adding any missing edge inside any minimum-size non-singleton part of `K_{a,b,c} join K_p` strictly decreases the simple-random-walk Kemeny constant.

The audit must independently compare the source manuscript formula and conventions with the candidate; reconstruct the cleared polynomial identity with separate exact code; verify the complete integer domain, denominator signs, coefficient nonnegativity and strictness; cover tied minimum parts and all missing edges in a chosen part; replay the preserved selected checker; and prove that coefficient corruption and malformed certificates are rejected.

## Frozen read-only inputs

- `../kemeny-three-part-work/INDEPENDENT-REVIEW-REQUEST.md`
- `../kemeny-three-part-work/contract-v1.md`, expected SHA256 `563d11151e21d31a21804e7871db6979996bc2cbe4dc0ed3673563975b1d2aba`
- `../kemeny-three-part-work/selection-v1.json`, expected SHA256 `c750ff018cc7e04db9d9b964486d71a0e5f9b5a42ea93e9de25b68c73632b996`
- `../kemeny-three-part-explorer-3-work/proposal.md`, expected SHA256 `53c78f650397b3a791dd6b2a715f2294c564bcb9440feabce7327ceb4dcfa3e4`
- `../kemeny-three-part-explorer-3-work/publication-manifest.json`, expected SHA256 `30f667f7a0a7657444984f578bd9f51b9a217d93f2eca10dea5b34f49710f04c`
- `../kemeny-three-part-explorer-3-work/proof/coefficient-certificate.json`, expected SHA256 `540ea590fb2e3d671e95102ab8ac5b80a22752f85354c7ded4aa84a4848fb8a9`
- `../kemeny-three-part-explorer-3-work/proof/verify_coefficient_certificate.py`, expected SHA256 `08aee29b87793cb288eaa7dfe54dd748b169972c32e46ed6e1b5bb2e1f3327f5`
- `../kemeny-three-part-prior-art-work/priority-review-v2.json`, expected SHA256 `25545977eafd4f042d90ecc69dfcaf3f82bb86578a3653cb033388d5d2c1a75b`
- `../kemeny-postresult-review-work/sources/hu-kirkland-2019.pdf`, expected SHA256 `c896d263c6bec602274f84a29c30492f99e85e3bde654f3e61dcf5aa10718c77`

No competing proposal directory may be inspected. The selection file's frozen comparison is permitted by the review request. All writes are confined to this independent-work directory. Mathematical correctness is assessed separately from publication priority, global novelty, and practical impact.

## Required gates

1. Reproduction.
2. Specification compliance.
3. Source verification.
4. Implementation alignment.

The candidate is rejected on any decisive algebraic, domain, source-transcription, or checker-soundness flaw. A passing mathematical audit does not certify novelty or practical impact.
