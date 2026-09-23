# Mandate Glass Protocol v3 — Live Studionet E2E Evidence

**Verified date:** 23 September 2026  
**Network:** GenLayer Studionet  
**Contract:** [`0xAc4125fcc0BB7A11a97766F2E09ba67B48D638D1`](https://explorer-studio.genlayer.com/address/0xAc4125fcc0BB7A11a97766F2E09ba67B48D638D1)  
**Protocol:** `MandateGlassGovernanceGate` v3  
**Security profile:** `CANARY_AND_CANONICAL_GROUNDING`

## Deployment verification

The deployed source was read back from Studionet and matched the local source byte-for-byte.

| Check | Verified value |
|---|---|
| Source SHA-256 | `c411d606141ea114981a92151311faf7f3aee2760c82b12aeabf6ad030bfeff2` |
| Source size | `42,076 bytes` |
| Public methods | `16` (`7` view, `9` write) |
| Initial state | `0 DAOs / 0 proposals / 0 reviews / 0 votes` |
| Final state | `1 DAO / 2 proposals / 2 reviews / 1 vote` |

The lifecycle runner checked both transaction finality and non-idle leader receipt execution results. `MAJORITY_AGREE` on a rollback was classified as an expected rejection, never as successful execution.

## Actors and canonical evidence

- DAO authority and bound delegate: `0x1D283b45974B0be9630DFD1deC6A62a9B72B2760`
- Adversarial outsider: `0xf96Cf822F9f4e76956AB9fAAa22B3BdCD7b10aD6`
- Canonical repository: [`hathanh6819/DAODelegateConflictEvidenceFixtures`](https://github.com/hathanh6819/DAODelegateConflictEvidenceFixtures)
- Clear snapshot: [`ef4842d0724efe027134bafd856354a8db03872b`](https://github.com/hathanh6819/DAODelegateConflictEvidenceFixtures/tree/ef4842d0724efe027134bafd856354a8db03872b)
- Undisclosed-conflict snapshot: [`4ebd44c76a0c86f35537cef8ef0b9f6bd72b4f08`](https://github.com/hathanh6819/DAODelegateConflictEvidenceFixtures/tree/4ebd44c76a0c86f35537cef8ef0b9f6bd72b4f08)

## Live transaction ledger

| # | Scenario | Transaction | Finalized execution | Verified result |
|---:|---|---|---|---|
| 1 | Owner registers canonical DAO authority | [`0x326ce9…10d98`](https://explorer-studio.genlayer.com/tx/0x326ce9b924f934bc850f06496afd4b55bbea1c594283df736e1794e9c9210d98) | `SUCCESS` | DAO `1`; authority, repository, paths and policy bound |
| 2 | Authority registers clear proposal | [`0x0086fc…07c10`](https://explorer-studio.genlayer.com/tx/0x0086fc593c0a23c9249959a6118d555bcbb00d612496d2c2637e6497d1707c10) | `SUCCESS` | Proposal `1` bound to clear commit and action digest |
| 3 | Outsider impersonates bound delegate | [`0xc97b8d…f6675`](https://explorer-studio.genlayer.com/tx/0xc97b8d7480c2f7a9afa9a7a96f62a00ccd653342802698ec08fc3c328cef6675) | Expected `ERROR` | Review count remained `0` |
| 4 | Bound delegate opens clear review | [`0x7e6bb4…86378`](https://explorer-studio.genlayer.com/tx/0x7e6bb448d33d18d3fd9e63311e5d0491b20b835f5fa4ae548566d16610986378) | `SUCCESS` | Review `1` created |
| 5 | Validators evaluate clear evidence | [`0x6ea6df…b07b4`](https://explorer-studio.genlayer.com/tx/0x6ea6dfe75025a1554618701b96da43a6af737f2f9eaf03c22f9d0404801b07b4) | `SUCCESS` | `CLEAR`; zero matches; evidence digest bound |
| 6 | Scoped authorization issued | [`0x680e02…ed145`](https://explorer-studio.genlayer.com/tx/0x680e02e1bc6966fd369c64f485509cd3841a80a0e09005b20943e34cf35ed145) | `SUCCESS` | Review state `AUTHORIZED`; non-empty authorization scope |
| 7 | Wrong action digest attempted | [`0x14d95b…26229`](https://explorer-studio.genlayer.com/tx/0x14d95b2f3b347dea59714c00f54884ae590f9843bf885b634c26a0ab8c926229) | Expected `ERROR` | Authorization remained unused; vote count stayed `0` |
| 8 | Exact guarded vote executed | [`0x2d20a7…7c045`](https://explorer-studio.genlayer.com/tx/0x2d20a7c3f77bc29a8013e7ed6dec2450802877a2182b5283908be23d0907c045) | `SUCCESS` | Vote `1` recorded and authorization consumed atomically |
| 9 | Consumed authorization replayed | [`0xbbaa7f…ab576`](https://explorer-studio.genlayer.com/tx/0xbbaa7fcb73a4e1cf14000df2ec34a158251f7c0fc36fe528b114f1a556eab576) | Expected `ERROR` | Vote count remained `1` |
| 10 | Authority registers undisclosed proposal | [`0xd3931a…683f3`](https://explorer-studio.genlayer.com/tx/0xd3931afee7bfad6637ea51340ab237522c7928566b07f87fa7a8425a104683f3) | `SUCCESS` | Proposal `2` bound to undisclosed fixture |
| 11 | Delegate opens undisclosed review | [`0xa83290…26f9f`](https://explorer-studio.genlayer.com/tx/0xa83290c95d1561ca9ca6ca6cb2b1b5dfb7496512d60ae95b3fbf4cb5c4a26f9f) | `SUCCESS` | Review `2` created |
| 12 | Validators evaluate undisclosed evidence | [`0x6e4486…3820f`](https://explorer-studio.genlayer.com/tx/0x6e4486a656601d8677199b7c363571109778b30db2e0e1ddfe3be3471643820f) | `SUCCESS` | `UNDISCLOSED_CONFLICT`; one grounded match |
| 13 | Authorization attempted on conflict | [`0x544373…816f5`](https://explorer-studio.genlayer.com/tx/0x54437351cbcc8cc1392132335ad6b3b249554c625b0c2a4875ef4a27762816f5) | Expected `ERROR` | No authorization scope; vote count remained `1` |

## Positive-path state evidence

After the clear evaluation, review `1` reported:

```json
{
  "state": 2,
  "verdict": 1,
  "reason": "CLEAR",
  "match_count": 0,
  "evidence_digest": "sha256:8fe29ffae555ebc36d1543d2e7ebf0ba43df3bda167612cf7f5159a38086119f"
}
```

After atomic execution, the same review reported `state=4` and `authorization_consumed=1`. Vote `1` was bound to review `1`, proposal `1`, the exact delegate and exact registered action digest.

## Fail-closed conflict evidence

The undisclosed snapshot produced:

```json
{
  "state": 2,
  "verdict": 3,
  "reason": "UNDISCLOSED_CONFLICT",
  "match_count": 1,
  "authorization_scope": "",
  "authorization_consumed": 0,
  "evidence_digest": "sha256:bdf8857f1b2be928418571e662ecaf2cb2a0a8d6fda9024e1e1f367b097b3441"
}
```

The subsequent authorization transaction finalized with an agreed rollback. Review state and all counts remained unchanged.

## Final on-chain invariants

```json
{
  "daos": 1,
  "proposals": 2,
  "reviews": 2,
  "votes": 1
}
```

- Exactly one favorable review produced one vote.
- Wrong action scope did not consume the authorization.
- Successful execution consumed the authorization atomically with vote creation.
- Replay did not create a second vote.
- An undisclosed conflict did not receive authorization.
- Rejected transactions did not mutate contract accounting.

## Reproduction

The reusable runner is [`scripts/run_v3_studionet_lifecycle.py`](../scripts/run_v3_studionet_lifecycle.py). It reads private keys interactively with `getpass`; keys are never stored in source, output, evidence files or commits.

Local verification before the live run:

```text
49 security/parser tests passed
9 GenLayer SDK Direct Mode tests passed
7 frontend regression tests passed
GenVM lint passed for 16 public methods
Production frontend build passed
```
