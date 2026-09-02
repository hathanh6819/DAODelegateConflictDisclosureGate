# DAO Delegate Conflict Disclosure Gate

Live application: [mandate-glass.pages.dev](https://mandate-glass.pages.dev/)

An Intelligent Contract that decides whether a DAO delegate disclosed canonical active affiliations that semantically match recipients of one specific proposal.

The design is intentionally narrow. It does not claim to discover private relationships or prove every real-world conflict. It compares three DAO-controlled documents locked in one exact public GitHub snapshot before the vote deadline:

1. `proposal.json` — proposal identity and recipient names/aliases;
2. `affiliations.json` — the DAO-maintained authoritative delegate relationship registry;
3. `disclosure.json` — the disclosure bound to the exact delegate address.

Validators construct GitHub endpoints from stored fields, fetch the exact commit and complete recursive tree, retrieve every bounded regular file, recompute each Git blob SHA-1 and bind the normalized evidence to a SHA-256 receipt. Contributor-selected evidence URLs and declared digests are not accepted.

GenLayer is necessary for semantic entity matching such as `Acme Labs`, `Acme Foundation` and `Acme Labs Foundation`. The model output is structurally bounded and validator consensus must agree on the complete verdict and match list. Missing, malformed, oversized or inconsistent evidence fails closed to `INSUFFICIENT_EVIDENCE`.

## Verdicts

- `CLEAR`: no active canonical affiliation matches a proposal recipient.
- `DISCLOSED_CONFLICT`: matches exist and every matching relationship was disclosed.
- `UNDISCLOSED_CONFLICT`: at least one matching relationship was not disclosed.
- `INSUFFICIENT_EVIDENCE`: acquisition, identity, schema or consensus failed.

Only `CLEAR` and `DISCLOSED_CONFLICT` may create an authorization. The authorization is revision-bound, consumable once, and only the original DAO creator may consume it. The contract has no payout or custody surface.

## Local verification

```powershell
pytest tests -q -p no:cacheprovider
pytest runtime_tests -q -p no:cacheprovider
$env:PYTHONIOENCODING='utf-8'
genvm-lint check contracts/dao_delegate_conflict_gate.py
cd frontend
npm ci
npm run build
```

## Deployment

The verified Studionet deployment is [`0x2C32b1A27C80C81239Ba883812979E2E1b358786`](https://explorer-studio.genlayer.com/address/0x2C32b1A27C80C81239Ba883812979E2E1b358786). It was deployed with no constructor arguments. The production frontend is bound to this address through `frontend/.env.production`; no fallback contract or simulated registry is used.

Do not represent local Direct Mode results as on-chain proof. Source matching, canonical acquisition, validator consensus, authorization, replay rejection and final state must be verified on the deployed Studionet contract.
