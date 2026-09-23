# Milestone evidence: Security & Consensus Hardening v1

## Before

- Model output contained `verdict` and `matches` only.
- Structural validation rejected malformed output, but a syntactically valid model response could name a recipient or canonical relationship not present in the locked evidence.
- Evidence was labelled untrusted in the prompt, but there was no per-evaluation tamper signal.
- GenVM lint selected the decorated v1 migration reference instead of the 16-method v2 deployment target.

## After

- A unique canary is derived from each evidence SHA-256 and enforced after validator consensus.
- Recipient IDs and active relationship pairs are deterministically grounded against the locked Git snapshot.
- Five explicit injection/hallucination vectors fail closed.
- GenVM lint selects `MandateGlassGovernanceGate` and validates all 16 methods.
- The frontend refuses any contract that is not protocol v3 with security profile `CANARY_AND_CANONICAL_GROUNDING`.

## Quantified change

| Control | Before | After |
|---|---:|---:|
| Injection/hallucination vectors explicitly tested | 0 | 5 |
| Deterministic model-output grounding dimensions | 0 | 2 |
| Per-evaluation evidence-bound canaries | 0 | 1 |
| Deployable schema selected by lint | v1 reference / 10 methods | v3 gate / 16 methods |

## Verification commands

```powershell
pytest tests -q -p no:cacheprovider
pytest runtime_tests -q -p no:cacheprovider
$env:PYTHONIOENCODING='utf-8'
genvm-lint check contracts/dao_delegate_conflict_gate.py
cd frontend
npm test
npm run build
```

## Deployment evidence

- Studionet contract: [`0xbd391006807E5cae85E26E50187F4CC2178c7C9c`](https://explorer-studio.genlayer.com/address/0xbd391006807E5cae85E26E50187F4CC2178c7C9c)
- Source SHA-256: `e63aea8df2fdfbb7cecaa66ac393894192ca1b33ec2330e86171454a3b3d0a76`
- Verified identity: `MandateGlassGovernanceGate` protocol v3
- Verified security profile: `CANARY_AND_CANONICAL_GROUNDING`
- Verified schema: 16 methods
- Production frontend environment points exclusively to the v3 address.

The fresh deployment has zero DAO/proposal/review/vote records. Lifecycle and adversarial Studionet transactions are intentionally tracked as the next evidence step rather than claimed here.
