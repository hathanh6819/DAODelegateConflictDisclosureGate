# Verification record

## Automated checks

- Parser and source-security suite: 32 passed.
- Real GenLayer SDK Direct Mode suite: 8 passed.
- GenVM lint and validation: passed; 10 public methods (4 view, 6 write).
- Frontend TypeScript/Vite production build: passed.
- Dependency audit at installation: 0 known vulnerabilities.

## Covered adversarial behavior

- repository and path injection;
- wrong proposal and delegate identities;
- contributor-injected unknown evidence fields;
- duplicated recipient identity;
- canonical blob digest recomputation;
- malformed model output fails to an unresolved, non-authorizable state;
- undisclosed conflict cannot authorize;
- disclosed conflict can authorize exactly once;
- stale/replayed consumption and cancel-after-terminal are rejected;
- retry count and all network/file/tree sizes are bounded.

These are local verification results. Add exact deployed source checksum, Studionet contract address, canonical fixture revisions and finalized transaction hashes only after on-chain verification.
