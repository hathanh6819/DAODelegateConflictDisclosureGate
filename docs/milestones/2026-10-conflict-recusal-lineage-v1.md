# Milestone — Conflict Recusal & Substitute Delegate Lineage

## Outcome

Protocol v4 turns conflict detection into an enforceable governance-remediation workflow. A conflicted delegate can now recuse on-chain; the DAO authority appoints a distinct successor; and that successor must pass a completely fresh canonical disclosure review before receiving a scoped vote authorization.

## Material changes

- New `RECUSED` and `SUPERSEDED` lifecycle states.
- New `recuse_review(review_id, expected_revision)` delegate action.
- New `appoint_substitute(review_id, expected_revision, substitute)` authority action.
- Bounded non-repeating lineage with a maximum of three substitutions.
- Fresh-review isolation: no verdict, digest, matches, authorization or consumed state crosses the substitution boundary. Every substitute binds a different evidence commit, and that commit is part of the authorization scope.
- New `get_review_lineage` audit view and expanded review/count readbacks.
- New frontend remediation desk and root/parent/successor lineage display.
- Formal invariant document mapping security properties to tests.

## Why this matters

Protocol v3 could detect and block an undisclosed conflict but left a live proposal without a safe continuation path. Protocol v4 preserves the block while allowing governance to continue through a new accountable delegate. The original conflict remains permanently visible, the DAO cannot silently rewrite its result, the same delegate cannot cycle back into the lineage, and the successor receives no inherited authorization.

## Verification

- `pytest tests -q -p no:cacheprovider`: 54 passed.
- `pytest runtime_tests -q -p no:cacheprovider`: 11 passed.
- `genvm-lint check contracts/dao_delegate_conflict_gate.py --json`: passed; 19 methods, 8 views, 11 writes.
- `npm test -- --run`: 7 passed.
- `npm run build`: passed.
- Contract source SHA-256: `1bc6dfe09192b6c460526d70f249b80d898870afb67607793e5933bbc89a8488` (47,288 bytes).

The first empty v4 deployment at `0x3C9B63637b963FBDc4D7d256489C956679be204c` exposed a lifecycle mismatch before any DAO state was written: a single proposal snapshot could not represent both the original delegate's disclosure and a substitute's fresh disclosure. v4.0.1 corrects this with per-review evidence commits and supersedes that unused address.

## Live deployment and lifecycle

The corrected v4.0.1 source is deployed at [`0x28A7CD54d40F85a466E482695E263372A7CE43dA`](https://explorer-studio.genlayer.com/address/0x28A7CD54d40F85a466E482695E263372A7CE43dA). Deployed source is byte-for-byte identical to the verified local source.

The completed Studionet lifecycle ends at `1 DAO / 1 proposal / 2 reviews / 1 substitution / 1 vote`. It proves an undisclosed-conflict review cannot be authorized; the conflicted delegate recuses; recycling that delegate fails; the authority appoints a distinct substitute using a fresh evidence commit; the predecessor cannot use the successor authorization; the substitute votes atomically; and replay fails. See the [complete transaction ledger](../LIVE_E2E_V4.md).

