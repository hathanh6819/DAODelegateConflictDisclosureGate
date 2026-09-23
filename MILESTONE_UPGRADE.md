# Mandate Glass — Milestone Upgrade Evidence

## Milestone

**Security & Consensus Hardening v1 — Evidence-Bound AI Verdicts**

Mandate Glass has been upgraded from protocol v2 to protocol v3. This milestone hardens the boundary between untrusted evidence, nondeterministic AI judgment, and deterministic governance authorization. The upgraded contract is deployed on Studionet and the production frontend is live on Vercel.

## What changed

### Before: protocol v2

- The model returned only `verdict` and `matches`.
- Structural checks rejected malformed JSON, duplicate matches, incorrect ordering, and verdict/match inconsistencies.
- Evidence was explicitly labelled as untrusted in the prompt, but there was no evidence-specific tamper signal in the model response.
- A syntactically valid response could name a recipient or relationship that did not exist in the locked canonical documents.
- The frontend accepted only protocol v2 and pointed to the retired v2 deployment.
- GenVM lint could select the retained v1 migration reference instead of the production governance gate.

### After: protocol v3

- Every evaluation derives a unique canary from the SHA-256 digest of the normalized evidence bundle.
- The model must return that canary exactly; missing or modified canaries fail closed to `INSUFFICIENT_EVIDENCE`.
- Every returned `recipient_id` must exist in the proposal locked at the registered Git commit.
- Every returned `(organization, role)` pair must exactly match an active relationship in the canonical DAO registry.
- Additional or attacker-controlled response fields are rejected.
- The v1 migration reference no longer exposes public decorators, so GenVM discovers only `MandateGlassGovernanceGate`.
- The frontend requires protocol v3 and security profile `CANARY_AND_CANONICAL_GROUNDING` before displaying governance state.
- The production environment points exclusively to the verified v3 Studionet deployment.

## Why this matters

GenLayer is used for the semantic judgment that differently named organizations may represent the same real-world entity. However, AI is not trusted to define governance identities. Protocol v3 preserves semantic consensus while deterministically restricting model output to identities and relationships present in the DAO-controlled, commit-locked evidence snapshot.

This separates responsibilities clearly:

1. **Git and cryptographic checks** establish evidence identity.
2. **GenLayer validator consensus** performs semantic entity matching.
3. **Deterministic contract checks** ground the result in canonical records.
4. **Scoped authorization** binds the approved result to one DAO, proposal, delegate, action digest, revision, and deadline.
5. **Atomic execution** records the vote and consumes its authorization in the same transaction.

## Adversarial coverage added

Five new attack vectors are explicitly tested:

1. The model replaces the required canary.
2. The model omits the canary field.
3. The model adds an attacker-controlled schema field.
4. The model invents a recipient identity.
5. The model invents an organization and role.

All five cases fail closed before authorization can be issued.

## Quantified improvements

| Metric | Before | After |
|---|---:|---:|
| Explicit injection/hallucination vectors tested | 0 | 5 |
| Deterministic output-grounding dimensions | 0 | 2 |
| Evidence-bound canaries per evaluation | 0 | 1 |
| Production contract methods verified | 16 | 16 |
| Security/parser tests | 40 | 49 |
| GenLayer SDK Direct Mode tests | 9 | 9 |
| Frontend regression tests | 7 | 7 |
| Protocol version | 2 | 3 |

## Verification results

The milestone was verified with the following results:

```text
pytest tests:          49 passed
pytest runtime_tests:  9 passed
frontend tests:        7 passed
frontend build:        passed
GenVM lint:            passed
Discovered contract:   MandateGlassGovernanceGate
Public methods:        16 (7 view, 9 write)
```

The deployed source was independently read back from Studionet. Its SHA-256 checksum matches the local contract source byte-for-byte:

```text
c411d606141ea114981a92151311faf7f3aee2760c82b12aeabf6ad030bfeff2
```

The verified on-chain identity is:

```json
{
  "name": "MandateGlassGovernanceGate",
  "version": 3,
  "security_profile": "CANARY_AND_CANONICAL_GROUNDING",
  "max_files": 8,
  "max_file_bytes": 10000,
  "max_total_bytes": 28000,
  "max_retries": 3
}
```

## Deployment evidence

- **Live application:** [https://mandate-glass.vercel.app/](https://mandate-glass.vercel.app/)
- **Studionet contract:** [`0xAc4125fcc0BB7A11a97766F2E09ba67B48D638D1`](https://explorer-studio.genlayer.com/address/0xAc4125fcc0BB7A11a97766F2E09ba67B48D638D1)
- **Source checksum:** `c411d606141ea114981a92151311faf7f3aee2760c82b12aeabf6ad030bfeff2`
- **Vercel production deployment:** `dpl_6p6Wo2LgLeHmsCP6jMWFQYVy1Cij`
- **Deployment status:** source, schema, identity, security profile, and production frontend verified

The finalized v3 lifecycle ends at `1 DAO / 2 proposals / 2 reviews / 1 vote`. It proves a grounded `CLEAR` verdict, scoped authorization and atomic vote consumption, plus fail-closed rejection of delegate impersonation, wrong action scope, replay and an `UNDISCLOSED_CONFLICT` authorization attempt.

### Finalized lifecycle transactions

- [Register DAO](https://explorer-studio.genlayer.com/tx/0x326ce9b924f934bc850f06496afd4b55bbea1c594283df736e1794e9c9210d98)
- [Evaluate CLEAR evidence](https://explorer-studio.genlayer.com/tx/0x6ea6dfe75025a1554618701b96da43a6af737f2f9eaf03c22f9d0404801b07b4)
- [Issue scoped authorization](https://explorer-studio.genlayer.com/tx/0x680e02e1bc6966fd369c64f485509cd3841a80a0e09005b20943e34cf35ed145)
- [Atomic guarded vote](https://explorer-studio.genlayer.com/tx/0x2d20a7c3f77bc29a8013e7ed6dec2450802877a2182b5283908be23d0907c045)
- [Wrong action rejected](https://explorer-studio.genlayer.com/tx/0x14d95b2f3b347dea59714c00f54884ae590f9843bf885b634c26a0ab8c926229)
- [Replay rejected](https://explorer-studio.genlayer.com/tx/0xbbaa7fcb73a4e1cf14000df2ec34a158251f7c0fc36fe528b114f1a556eab576)
- [Evaluate undisclosed conflict](https://explorer-studio.genlayer.com/tx/0x6e4486a656601d8677199b7c363571109778b30db2e0e1ddfe3be3471643820f)
- [Undisclosed authorization rejected](https://explorer-studio.genlayer.com/tx/0x54437351cbcc8cc1392132335ad6b3b249554c625b0c2a4875ef4a27762816f5)

## Code and evidence links

- [Complete milestone diff](https://github.com/hathanh6819/DAODelegateConflictDisclosureGate/compare/d45ae4b...main)
- [Protocol v3 contract](https://github.com/hathanh6819/DAODelegateConflictDisclosureGate/blob/main/contracts/dao_delegate_conflict_gate.py)
- [Adversarial security tests](https://github.com/hathanh6819/DAODelegateConflictDisclosureGate/blob/main/tests/test_document_security.py)
- [Security documentation](https://github.com/hathanh6819/DAODelegateConflictDisclosureGate/blob/main/SECURITY.md)
- [Deployment record](https://github.com/hathanh6819/DAODelegateConflictDisclosureGate/blob/main/deployments/deployment.json)
- [Changelog](https://github.com/hathanh6819/DAODelegateConflictDisclosureGate/blob/main/CHANGELOG.md)
- [Detailed milestone record](https://github.com/hathanh6819/DAODelegateConflictDisclosureGate/blob/main/docs/milestones/2026-09-security-consensus-hardening-v1.md)

## Reproduction commands

```powershell
pytest tests -q -p no:cacheprovider
pytest runtime_tests -q -p no:cacheprovider
$env:PYTHONIOENCODING='utf-8'
genvm-lint check contracts/dao_delegate_conflict_gate.py
cd frontend
npm test
npm run build
```

## Submission summary

This is clear new work beyond the accepted project: a security and consensus architecture improvement, a new protocol version, a new verified contract deployment, and a new production frontend deployment. It is not a resubmission, rename, or cosmetic-only update.
