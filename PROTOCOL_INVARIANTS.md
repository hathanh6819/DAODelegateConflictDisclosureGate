# Mandate Glass protocol invariants

## Evidence and consensus

**MG-1 — Canonical acquisition.** Evidence is constructed only from the DAO-controlled repository, paths and proposal commit. Git tree identity, blob hashes, byte bounds and document schemas are verified before semantic judgment.

**MG-2 — Evidence-bound output.** The required canary is derived from the normalized evidence digest. Model responses with a missing or changed canary, extra keys, invented recipients, or invented relationships fail closed.

**MG-3 — Deterministic authority boundary.** AI classifies semantic relationship equivalence. Deterministic code controls identities, states, revisions, deadlines, authorization scopes and vote recording.

## Governance execution

**MG-4 — Complete scope.** An authorization binds DAO authority, proposal, delegate, action digest, per-review evidence commit, review revision, proposal revision and deadline.

**MG-5 — Atomic single use.** `execute_vote` records one vote and consumes its authorization in the same transaction. Any failed check changes neither value.

**MG-6 — Fail closed.** `UNDISCLOSED_CONFLICT` and `INSUFFICIENT_EVIDENCE` cannot authorize a vote.

## Recusal and substitution

**MG-7 — Voluntary identity-bound recusal.** Only the bound delegate can recuse its evaluated conflict review. Clear, pending, unresolved, authorized and consumed reviews cannot enter the remediation path.

**MG-8 — Authority-controlled succession.** Only the registered DAO authority may appoint a substitute, and only after recusal while the proposal remains open and unexpired.

**MG-9 — No inherited authorization.** A substitute starts with a fresh `PENDING` review, revision 1, empty evidence digest, empty scope, zero matches and zero consumption. Appointment requires a different valid evidence commit for the substitute; the predecessor becomes `SUPERSEDED`.

**MG-10 — No identity recycling.** A substitute address may not appear anywhere earlier in its review lineage. The lineage is bounded to three substitutions.

**MG-11 — Single successor.** Every recused review can produce at most one successor. A second appointment reverts and does not increment review or substitution counts.

**MG-12 — Auditable lineage.** Parent, root, successor, depth and recusal time are stored on-chain. `get_review_lineage` returns the root-first bounded chain used by the frontend and independent auditors.

## Test map

| Invariant | Primary verification |
|---|---|
| MG-1–MG-3 | `tests/test_document_security.py`, `tests/test_contract_invariants.py` |
| MG-4–MG-6 | `tests/test_governance_enforcement.py`, `runtime_tests/test_runtime_contract.py` |
| MG-7 | `test_conflicted_delegate_recuses_and_substitute_completes_fresh_gate`, `test_clear_review_cannot_recuse_and_lineage_cannot_repeat_delegate` |
| MG-8–MG-11 | `test_substitution_is_authority_controlled_bounded_and_non_repeating`, Direct Mode substitution lifecycle |
| MG-9, MG-12 | `test_substitute_review_inherits_proposal_but_not_authorization`, `test_review_lineage_is_public_and_bounded` |

