# Changelog

## [3.0.0] - 2026-09-23

### Security & Consensus Hardening v1

- Added an evidence-digest-derived prompt-injection canary. Missing, altered, or schema-bypassed canaries now fail closed to `INSUFFICIENT_EVIDENCE`.
- Added deterministic grounding checks: model-produced recipient IDs must exist in the locked proposal and organization/role pairs must match an active canonical registry relationship exactly.
- Removed public decorators from the retained v1 migration reference so GenVM schema discovery exposes only `MandateGlassGovernanceGate` (16 methods).
- Added five adversarial injection/hallucination vectors plus positive grounding coverage.
- Upgraded the frontend identity gate and visible network banner from protocol v2 to hardened protocol v3.

### Verification

- 47 parser/security tests pass.
- 9 real GenLayer SDK Direct Mode tests pass.
- 7 frontend regression tests pass.
- Production frontend build passes.
- GenVM lint validates `MandateGlassGovernanceGate` with 16 public methods.

### Deployment status

Protocol v3 changes contract execution semantics and requires a new Studionet deployment. The existing v2 address remains the production address until the v3 deployment is finalized and independently verified.
