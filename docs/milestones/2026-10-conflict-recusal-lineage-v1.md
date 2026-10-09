# Milestone — Conflict Recusal & Substitute Delegate Lineage

## Outcome

Protocol v4 turns conflict detection into an enforceable governance-remediation workflow. A conflicted delegate can now recuse on-chain; the DAO authority appoints a distinct successor; and that successor must pass a completely fresh canonical disclosure review before receiving a scoped vote authorization.

## Material changes

- New `RECUSED` and `SUPERSEDED` lifecycle states.
- New `recuse_review(review_id, expected_revision)` delegate action.
- New `appoint_substitute(review_id, expected_revision, substitute)` authority action.
- Bounded non-repeating lineage with a maximum of three substitutions.
- Fresh-review isolation: no verdict, digest, matches, authorization or consumed state crosses the substitution boundary.
- New `get_review_lineage` audit view and expanded review/count readbacks.
- New frontend remediation desk and root/parent/successor lineage display.
- Formal invariant document mapping security properties to tests.

## Why this matters

Protocol v3 could detect and block an undisclosed conflict but left a live proposal without a safe continuation path. Protocol v4 preserves the block while allowing governance to continue through a new accountable delegate. The original conflict remains permanently visible, the DAO cannot silently rewrite its result, the same delegate cannot cycle back into the lineage, and the successor receives no inherited authorization.

## Verification

- `pytest tests -q -p no:cacheprovider`: 53 passed.
- `pytest runtime_tests -q -p no:cacheprovider`: 11 passed.
- `genvm-lint check contracts/dao_delegate_conflict_gate.py --json`: passed; 19 methods, 8 views, 11 writes.
- `npm test -- --run`: 7 passed.
- `npm run build`: passed.
- Contract source SHA-256: `c635864024582a25e61938d8224d837780f1658c27c07054e8836edd3ab1d548`.

## Deployment gate

Fresh v4 deployment and live evidence are required because storage and ABI changed. Production remains on verified v3 until deployed/local source parity, one conflict-recusal-substitute-vote lifecycle, negative replay tests, frontend environment update and Vercel verification are complete.

