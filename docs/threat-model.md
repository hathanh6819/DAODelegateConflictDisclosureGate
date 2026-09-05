# Threat model

## Governance enforcement added in protocol v2

- Only the contract owner can enroll a DAO authority; only that exact authority can register proposals or revise the canonical source mapping.
- A proposal is an on-chain record binding the DAO, external proposal identity, immutable Git commit, exact action SHA-256, voting deadline and proposal revision.
- A delegate can open a review only for its own address. The contract constructs all evidence URLs from the DAO-controlled mapping and the proposal commit.
- Authorization binds DAO authority, proposal, delegate, action, review revision, proposal revision and expiry.
- `execute_vote` validates the complete scope and atomically records the vote and consumes authorization. Any failed check reverts both operations.
- Undisclosed conflicts and unresolved evidence never reach the authorized state. Closed/expired proposals, stale revisions, changed accounts, wrong actions and replay attempts leave vote accounting unchanged.

## Trust boundaries

- Interested users may choose workflow inputs but cannot provide arbitrary evidence URLs.
- The review creator is treated as the DAO authority for the locked repository and registry snapshot.
- GitHub commit, tree and raw endpoints are acquisition sources; content identity is verified cryptographically.
- Model output is nondeterministic and accepted only after strict validator equality and deterministic invariant checks.

## Fail-closed cases

- repository, path, commit, proposal or delegate identity mismatch;
- missing, truncated or oversized tree;
- more than 8 files, unsupported Git objects, binary data or Git LFS pointers;
- raw body whose byte length or recomputed Git blob SHA-1 differs from the tree;
- unknown JSON keys, duplicate identities or excessive relationship counts;
- malformed, duplicated, unsorted or internally inconsistent model match records;
- stale revision, unfavorable verdict, replayed authorization or retry exhaustion.

## Explicit limitation

The contract verifies disclosure completeness against the registered DAO affiliation registry. It cannot discover relationships absent from that authoritative registry. This limitation is explicit so the verdict is not overstated.
