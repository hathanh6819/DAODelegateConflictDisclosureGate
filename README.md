# DAO Delegate Conflict Disclosure Gate

Live application: [mandate-glass.vercel.app](https://mandate-glass.vercel.app/)

An Intelligent Contract that decides whether a DAO delegate disclosed canonical active affiliations that semantically match recipients of one specific proposal, then enforces that result on a proposal-bound governance vote.

The design is intentionally narrow. It does not claim to discover private relationships or prove every real-world conflict. It compares three DAO-controlled documents locked in one exact public GitHub snapshot before the vote deadline:

1. `proposal.json` — proposal identity and recipient names/aliases;
2. `affiliations.json` — the DAO-maintained authoritative delegate relationship registry;
3. `disclosure.json` — the disclosure bound to the exact delegate address.

Validators construct GitHub endpoints from stored fields, fetch the exact commit and complete recursive tree, retrieve every bounded regular file, recompute each Git blob SHA-1 and bind the normalized evidence to a SHA-256 receipt. Contributor-selected evidence URLs and declared digests are not accepted.

GenLayer is necessary for semantic entity matching such as `Acme Labs`, `Acme Foundation` and `Acme Labs Foundation`. The model output is structurally bounded and validator consensus must agree on the complete verdict and match list. Missing, malformed, oversized or inconsistent evidence fails closed to `INSUFFICIENT_EVIDENCE`.

## Protocol v3 security milestone

The next release adds an evidence-bound prompt-injection canary and deterministic canonical grounding for every model-produced match. Five adversarial injection/hallucination vectors now fail closed, and GenVM schema discovery is isolated to the 16-method governance gate. See [CHANGELOG.md](CHANGELOG.md), [SECURITY.md](SECURITY.md), and the [milestone evidence record](docs/milestones/2026-09-security-consensus-hardening-v1.md).

Protocol v3 is deployed on Studionet with source, schema, identity and security profile independently verified. The fresh deployment intentionally starts with empty governance state; lifecycle evidence will be recorded separately.

## Verdicts

- `CLEAR`: no active canonical affiliation matches a proposal recipient.
- `DISCLOSED_CONFLICT`: matches exist and every matching relationship was disclosed.
- `UNDISCLOSED_CONFLICT`: at least one matching relationship was not disclosed.
- `INSUFFICIENT_EVIDENCE`: acquisition, identity, schema or consensus failed.

Only `CLEAR` and `DISCLOSED_CONFLICT` may create an authorization. Every authorization is bound to the DAO authority, proposal, delegate, target action digest, review revision, proposal revision and expiry. The delegate consumes it atomically inside `execute_vote`; the same transaction records the governance vote and marks the authorization used. Failed scope, identity, expiry, revision, unresolved-evidence and replay checks leave vote accounting unchanged. The contract has no payout or custody surface.

## Local verification

```powershell
pytest tests -q -p no:cacheprovider
pytest runtime_tests -q -p no:cacheprovider
$env:PYTHONIOENCODING='utf-8'
genvm-lint check contracts/dao_delegate_conflict_gate.py
cd frontend
npm ci
npm test
npm run build
```

## Deployment

Protocol v3 is deployed on Studionet at [`0xAc4125fcc0BB7A11a97766F2E09ba67B48D638D1`](https://explorer-studio.genlayer.com/address/0xAc4125fcc0BB7A11a97766F2E09ba67B48D638D1). Its deployed source matches checksum `c411d606141ea114981a92151311faf7f3aee2760c82b12aeabf6ad030bfeff2`, protocol identity `MandateGlassGovernanceGate` v3, security profile `CANARY_AND_CANONICAL_GROUNDING`, and all 16 public methods. The finalized lifecycle verifies one atomic guarded vote plus impersonation, wrong-action, replay and undisclosed-conflict rejection. The frontend is bound only to this verified address.

Do not represent local Direct Mode results as on-chain proof. Source matching, canonical acquisition, validator consensus, authorization, replay rejection and final state must be verified on the deployed Studionet contract.
