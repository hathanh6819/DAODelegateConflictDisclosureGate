# Changelog

## [4.0.1] - 2026-10-09

### Fresh substitute evidence binding

- Added a per-review evidence commit. The original review inherits the proposal snapshot; each substitute appointment must bind a different valid Git commit containing that delegate's canonical registry and disclosure documents.
- Added the evidence commit to the complete authorization scope, so neither evidence revision nor delegate identity can be swapped after authorization.
- Added `FRESH_EVIDENCE_REQUIRED` and `INVALID_EVIDENCE_COMMIT` guards plus regression coverage.
- The empty v4.0.0 deployment `0x3C9B63637b963FBDc4D7d256489C956679be204c` is superseded before any DAO or proposal registration. A fresh deployment is required.

## [4.0.0] - 2026-10-09

### Conflict Recusal & Substitute Delegate Lineage

- Added on-chain recusal for evaluated `DISCLOSED_CONFLICT` and `UNDISCLOSED_CONFLICT` reviews.
- Added DAO-authority appointment of a distinct substitute after recusal. A substitute receives a fresh pending review and never inherits evidence, verdict, authorization scope, or consumption state.
- Added bounded, non-repeating review lineage with parent, root, successor, depth and recusal timestamp provenance.
- Added terminal `SUPERSEDED` state for the replaced review and replay protection against a second appointment.
- Added `get_review_lineage` plus substitution counters and lineage fields in `get_review`.
- Added v4 frontend remediation workflow and visible lineage provenance.
- Expanded verification to 54 security/invariant tests and 11 GenLayer Direct Mode tests; frontend tests and production build pass; GenVM validates 19 public methods.

### Deployment status

Protocol v4 changes storage and ABI and therefore requires a fresh Studionet deployment. Protocol v3 remains the verified production deployment until v4 source parity and live recusal lifecycle are complete.

## [3.0.0] - 2026-09-23

### Security & Consensus Hardening v1

- Added an evidence-digest-derived prompt-injection canary. Missing, altered, or schema-bypassed canaries now fail closed to `INSUFFICIENT_EVIDENCE`.
- Added deterministic grounding checks: model-produced recipient IDs must exist in the locked proposal and organization/role pairs must match an active canonical registry relationship exactly.
- Removed public decorators from the retained v1 migration reference so GenVM schema discovery exposes only `MandateGlassGovernanceGate` (16 methods).
- Added five adversarial injection/hallucination vectors plus positive grounding coverage.
- Upgraded the frontend identity gate and visible network banner from protocol v2 to hardened protocol v3.
- Added cross-runtime address normalization for `Address.as_hex`, hexadecimal strings, and Studio's decimal calldata representation after live owner-call verification exposed the incompatibility.

### Verification

- 49 parser/security tests pass.
- 9 real GenLayer SDK Direct Mode tests pass.
- 7 frontend regression tests pass.
- Production frontend build passes.
- GenVM lint validates `MandateGlassGovernanceGate` with 16 public methods.

### Deployment status

Protocol v3 is deployed at `0xAc4125fcc0BB7A11a97766F2E09ba67B48D638D1`. On-chain source checksum, protocol identity, security profile, and all 16 methods match this release. The finalized lifecycle verifies a guarded atomic vote and four adversarial rejection paths, ending at `1 DAO / 2 proposals / 2 reviews / 1 vote`.

The protocol v3 frontend is deployed at [mandate-glass.vercel.app](https://mandate-glass.vercel.app/), built from the verified production address configuration.
