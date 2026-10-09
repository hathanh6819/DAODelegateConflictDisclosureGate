# Mandate Glass — Milestone Upgrade Evidence

## Milestone

**Conflict Recusal & Substitute Delegate Lineage**

Mandate Glass has been upgraded from protocol v3 to v4.0.1. This milestone converts conflict detection from a terminal block into an enforceable governance-continuity workflow while preserving a public, immutable accountability trail.

## What changed

- Conflicted delegates can recuse on-chain only after an evaluated conflict verdict.
- The DAO authority can appoint one distinct substitute to a recused review.
- Every substitute receives a new review bound to a different canonical Git commit; verdicts, evidence digests and authorization state never carry across the boundary.
- Root, parent, successor, depth and recusal time create an auditable lineage.
- Bounded non-repetition prevents delegate cycling; a predecessor cannot use a successor's authorization.
- Authorization scope binds the per-review evidence commit.
- The frontend exposes the complete remediation workflow and lineage.

## Why this is material

Protocol v3 correctly blocked an undisclosed conflict but offered no safe way for a live proposal to continue. Protocol v4 preserves that safety decision while letting a separately accountable delegate proceed only after a fresh canonical review. The original conflict remains visible and cannot be overwritten.

## Verification

```text
pytest tests:          54 passed
pytest runtime_tests: 11 passed
frontend tests:        7 passed
frontend build:        passed
GenVM lint:            passed
Public methods:        19 (8 view, 11 write)
Source SHA-256:         1bc6dfe09192b6c460526d70f249b80d898870afb67607793e5933bbc89a8488
```

The source deployed at `0x28A7CD54d40F85a466E482695E263372A7CE43dA` matches the 47,288-byte local contract exactly. The public lifecycle finishes at `1 DAO / 1 proposal / 2 reviews / 1 substitution / 1 vote` and verifies five negative paths in addition to the successful remediation path.

## Evidence

- [Live application](https://mandate-glass.vercel.app/)
- [Studionet v4.0.1 contract](https://explorer-studio.genlayer.com/address/0x28A7CD54d40F85a466E482695E263372A7CE43dA)
- [Exact milestone comparison](https://github.com/hathanh6819/DAODelegateConflictDisclosureGate/compare/3b73d71...main)
- [Live v4 transaction ledger](https://github.com/hathanh6819/DAODelegateConflictDisclosureGate/blob/main/docs/LIVE_E2E_V4.md)
- [Formal protocol invariants](https://github.com/hathanh6819/DAODelegateConflictDisclosureGate/blob/main/PROTOCOL_INVARIANTS.md)
- [Detailed milestone record](https://github.com/hathanh6819/DAODelegateConflictDisclosureGate/blob/main/docs/milestones/2026-10-conflict-recusal-lineage-v1.md)

## Submission text

**Title:** Conflict Recusal & Substitute Delegate Lineage

**Changes & Improvements:** Mandate Glass v4.0.1 adds an enforceable recovery path when a DAO delegate has a disclosed or undisclosed conflict. The bound delegate can recuse on-chain; the DAO authority may appoint a distinct, non-repeating substitute; and the substitute must pass a new canonical review tied to a different Git evidence commit before receiving a separately scoped authorization. Root/parent/successor lineage, substitution depth and recusal time remain publicly auditable. Authorization now binds per-review evidence, and predecessor, recycling, duplicate-appointment and replay attempts fail closed. The frontend exposes the complete remediation workflow. Verified with 54 security tests, 11 GenLayer Direct Mode tests, 7 UI tests, exact deployed-source parity and a live Studionet lifecycle ending in one atomic substitute vote.
