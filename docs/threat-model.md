# Threat model

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
