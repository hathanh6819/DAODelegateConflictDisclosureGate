# Verification record

> The finalized Studionet transactions below verify the retired registry-only protocol v1. They are retained as historical evidence and must not be presented as verification of protocol v2. Protocol v2 requires a fresh deployment and fresh governance lifecycle transactions.

## Protocol v2 pre-deployment verification

- 40 parser, source-security and governance-enforcement checks passed.
- 9 real GenLayer SDK Direct Mode tests passed.
- 7 frontend governance regression tests passed.
- GenVM lint passed.
- Production frontend build passed and is bound to the verified v2 contract address.
- Direct-contract cases cover DAO authority and source revision, proposal and delegate identity, action scope, stale revision, deadline expiry, unresolved-evidence recovery, hidden-conflict blocking, closed-proposal blocking, atomic vote accounting and replay rejection.

## Protocol v2 deployment verification

- Contract: [`0x9A354B54296BBe45Ec8D7600dEbBd5eDf2510DdA`](https://explorer-studio.genlayer.com/address/0x9A354B54296BBe45Ec8D7600dEbBd5eDf2510DdA)
- Deployment: [`0x5d96f1e1b109b5e1eae11b77af6d62270c3b85fbc64fccb06add73c7c1195724`](https://explorer-studio.genlayer.com/tx/0x5d96f1e1b109b5e1eae11b77af6d62270c3b85fbc64fccb06add73c7c1195724)
- Deployer and contract owner: `0xa365F55A3bf352767bc5c5739FfDDAee8FcF3a19`
- Deployed source: `41,667` bytes, SHA-256 `da85824a0937e4b826ea64a04c13e3d6b5e680e3abbdefb7718f98cb98f889da`.
- Schema and protocol: `MandateGlassGovernanceGate` v2, 16 public methods.
- Initial state: zero DAOs, proposals, reviews and votes.

## Protocol v2 finalized Studionet behavior

The v2 lifecycle checks both the top-level consensus result and the non-idle leader
receipt. `MAJORITY_AGREE` on an error is recorded as a rejected transaction, never as
successful execution.

### Clear result, scoped authorization and atomic vote

- Authority registration: [`0xa90854e8df05a1b2288a593e5d77b8921357487da10a93bcf10b40cfadd2f1f2`](https://explorer-studio.genlayer.com/tx/0xa90854e8df05a1b2288a593e5d77b8921357487da10a93bcf10b40cfadd2f1f2)
- Proposal #3, locked to fixture commit [`ef4842d0724efe027134bafd856354a8db03872b`](https://github.com/hathanh6819/DAODelegateConflictEvidenceFixtures/tree/ef4842d0724efe027134bafd856354a8db03872b): [`0x0c6aff690d8ad0c4d35af8d23712f74b5450f251fe14bc277cd0c8830672af1a`](https://explorer-studio.genlayer.com/tx/0x0c6aff690d8ad0c4d35af8d23712f74b5450f251fe14bc277cd0c8830672af1a)
- [Open review #1](https://explorer-studio.genlayer.com/tx/0x959ad51c65dc0f78c85504bbea49c4bbc94d4bed2177f61d7f85d560c6b74e7a)
- [Canonical evaluation](https://explorer-studio.genlayer.com/tx/0x1876d598c7c82058afdabb57e5b792f918917703d59f73d900a3b299786ae123): `CLEAR`, evidence `sha256:4c9491a3ee724dc6e7fd51022f613271b33586903bb275ab8aae08523b50f330`.
- [Issue scoped authorization](https://explorer-studio.genlayer.com/tx/0x073340b1e87ccf123c1d72390551ea4347ffd93a089171adec7c5a9d9b6444b1)
- [Atomic FOR vote and consumption](https://explorer-studio.genlayer.com/tx/0x3c65b33bf85d4e15e0b24fadf2d66049fab367b22856411c092a5fffbdc9d020): review state `CONSUMED`, `authorization_consumed=1`, vote count `1`.
- [Replay attempt](https://explorer-studio.genlayer.com/tx/0xbbe40dd82630b3bd475e30da1fc725a04e0077ec4ceb0ec3c603cfe1909d4004): agreed `ERROR / NOT_AUTHORIZED`; all counts unchanged.

### Identity mismatch, unresolved retry and blocked authorization

- [Open adversarial review #2](https://explorer-studio.genlayer.com/tx/0x2b273b251db0bbd27cc7ef986673c028ad022ed96fb10a7aef38a07ca736a389)
- [Canonical evaluation](https://explorer-studio.genlayer.com/tx/0xe945423a86cecbc9d4cf1748ef0cd983e191de06c8a49f9c0b5d8144deb709f5): `UNRESOLVED / DELEGATE_NOT_IN_REGISTRY`, no digest and no authorization scope.
- [Rejected authorization](https://explorer-studio.genlayer.com/tx/0x0a907c10325b16f00ff249120d59b07a1c997d694f90fe523fc1dfa3f7acb36a): agreed `ERROR / INVALID_REVIEW_STATE`; counts unchanged.
- [Retry](https://explorer-studio.genlayer.com/tx/0x751587d813f3ed34156328fb67fa910abb60531eb1519bcb8a47822300b3285b): retry count advanced to `1`, while the unresolved identity mismatch remained fail-closed and vote count stayed `1`.

### Undisclosed conflict blocks the governance path

- Proposal #4: [`0x05918bfaba0dfac53465ff83f93b65a93e29dd500a19dd5fc8a1226d62418771`](https://explorer-studio.genlayer.com/tx/0x05918bfaba0dfac53465ff83f93b65a93e29dd500a19dd5fc8a1226d62418771), locked to immutable fixture [`4ebd44c76a0c86f35537cef8ef0b9f6bd72b4f08`](https://github.com/hathanh6819/DAODelegateConflictEvidenceFixtures/tree/4ebd44c76a0c86f35537cef8ef0b9f6bd72b4f08).
- [Open review #3](https://explorer-studio.genlayer.com/tx/0x702bc361908b4615a90c48b6d6399776cad1494e8252e15d836baef6d1a3f974)
- [Canonical evaluation](https://explorer-studio.genlayer.com/tx/0x82ee384e935bc2b05da17bbf31868e6be472f6496c2c084ec696e3b5cf3480af): `UNDISCLOSED_CONFLICT`, one undisclosed `Acme Labs / Advisor` match, evidence `sha256:8498243e15dcebe254ef161c66952c64bb64b38f7c8acd6abc6d0f3a9f1c6367`.
- [Rejected authorization](https://explorer-studio.genlayer.com/tx/0xbf9d489a948565b3685dfaafe6844f05fca54db70fd3ca5714921d04207e1f3c): agreed `ERROR / VERDICT_NOT_AUTHORIZABLE`; review and accounting remained unchanged, with zero scope and total vote count `1`.

Final v2 state after these checks: `1 DAO / 4 proposals / 3 reviews / 1 vote`.

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

## Verified Studionet deployment

- Contract: [`0x2C32b1A27C80C81239Ba883812979E2E1b358786`](https://explorer-studio.genlayer.com/address/0x2C32b1A27C80C81239Ba883812979E2E1b358786)
- Deployed source SHA-256: `79b5c454722adb7fefc0523ceaf2a2034e3b2e69383a5148e001c16955fcacd6`
- Deployed source size: `23,387` bytes
- Schema: 10 public methods; protocol name/version and all acquisition bounds match the repository.
- Canonical fixture repository: [DAODelegateConflictEvidenceFixtures](https://github.com/hathanh6819/DAODelegateConflictEvidenceFixtures)

## Canonical on-chain lifecycle

All state below was read back from the deployed contract after finalized consensus. A top-level `MAJORITY_AGREE` is not treated as execution success: the runner checks non-idle leader receipts' `execution_result` and the resulting contract state.

### Disclosed conflict — authorizable and single-use

- Immutable fixture: [`9219776b7398f5e30b354b1e97c47f02bdd0dcf4`](https://github.com/hathanh6819/DAODelegateConflictEvidenceFixtures/tree/9219776b7398f5e30b354b1e97c47f02bdd0dcf4)
- [Create review #1](https://explorer-studio.genlayer.com/tx/0x5076ca5eebf162b3855b240520fe817e01fe23b020ac35cddbb0359de11185fb)
- [Evaluate](https://explorer-studio.genlayer.com/tx/0x8c53e102bf339f4c45ba88ed98550131453bff076e16ced5b6468dd5b21a0f75): `DISCLOSED_CONFLICT`, one disclosed match, evidence `sha256:ed2642f3c7b36c7e62b37db04b84a6c716616d7f4c8dfec1940a45bde6bfc814`.
- [Authorize](https://explorer-studio.genlayer.com/tx/0x7d6e4dfc0296ab96e568b6ccdfc25497ee8cf6b31893c4ca29fe6adb2656151d) and [consume](https://explorer-studio.genlayer.com/tx/0xc11afed1f0125be4df454745af56eaeb59eb662e9bcbe0ade3d35a528fc741d0) succeeded.
- [Replay attempt](https://explorer-studio.genlayer.com/tx/0x9c80d96b34b9f9874637397679195db81e92d90fef61af6276ca9a12c357df65) finalized with agreed `ERROR / NOT_AUTHORIZED`; state remained consumed and `authorization_consumed=1`.

### Undisclosed conflict — fail closed

- Immutable fixture: [`160b50e69190ee81334b896065840ee7a8e5746b`](https://github.com/hathanh6819/DAODelegateConflictEvidenceFixtures/tree/160b50e69190ee81334b896065840ee7a8e5746b)
- [Create review #2](https://explorer-studio.genlayer.com/tx/0xc5492914d1210002c5cd423a0d3ca1d92e8fa0519aaad92cd7b01127f6a8e3aa)
- [Evaluate](https://explorer-studio.genlayer.com/tx/0xd04a55c4b111bcf31f4f390b03afe3d6e1a55afd4a00076217bf378c9d7706e4): `UNDISCLOSED_CONFLICT`, one undisclosed match, evidence `sha256:754a0c29f1571658847e33e63723bc37ef24a0a899325c1c6731fd889ecd5976`.
- [Unauthorized approval attempt](https://explorer-studio.genlayer.com/tx/0x16f3099aebfcb073812ecfe259784c59188a577dc3cac1416addd8536f21e726) finalized with agreed `ERROR`; state remained evaluated and unconsumed.

### Clear result — authorizable

- An intentionally ambiguous snapshot at [`27dadd3c94f7b2266f81f463ca6c9c645e91fd33`](https://github.com/hathanh6819/DAODelegateConflictEvidenceFixtures/tree/27dadd3c94f7b2266f81f463ca6c9c645e91fd33) produced `UNDISCLOSED_CONFLICT` in review #3 and was preserved as adversarial evidence.
- Unambiguous immutable fixture: [`979eb6b163c53e44486995952942608793d9e118`](https://github.com/hathanh6819/DAODelegateConflictEvidenceFixtures/tree/979eb6b163c53e44486995952942608793d9e118)
- [Create review #4](https://explorer-studio.genlayer.com/tx/0x46fe8412aed1a243d64c6c81eed9f449a1a1b1fcdb1b46b6ab3d08f5dd8d1083)
- [Evaluate](https://explorer-studio.genlayer.com/tx/0xb61bca68141e01ede4b8dacd3ceb519aba6e6b2800878df8e14d277caabda6da): `CLEAR`, zero matches, evidence `sha256:831abbbc642e2bdf640cd5500b9b70614c46d85d7456cb60a7c240aeec0b2dc1`.
- [Authorize](https://explorer-studio.genlayer.com/tx/0x0f67b452c234964188f1f5fa0715eb41c71874f78996755040dfa2f49ac1f42c) succeeded; review #4 is authorized.

The reusable runner is `scripts/live_canonical_lifecycle.mjs`; `scripts/inspect_transaction.mjs` exposes compact leader/validator receipt evidence for any transaction hash.
