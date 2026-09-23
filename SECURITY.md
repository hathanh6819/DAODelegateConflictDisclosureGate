# Security policy and protocol v3 hardening

Mandate Glass treats every fetched document and every model response as hostile input. The contract authorizes governance actions only after deterministic acquisition, consensus, schema, identity, grounding, scope, revision, deadline, and replay checks succeed.

## Protocol v3 controls

### Prompt-injection canary

Each evaluation derives a canary from the SHA-256 digest of the normalized evidence bundle. The prompt requires the model to copy it exactly. The deterministic execution layer rejects missing, modified, or extra-schema responses before a verdict can become authorizable.

This does not claim that a canary prevents every model manipulation. It is a tamper signal that converts common instruction-following attacks into a fail-closed `UNRESOLVED` review.

### Canonical output grounding

The model may make the semantic judgment that an organization matches a proposal recipient, but it may not invent output identities. Every returned:

- `recipient_id` must exist in the locked proposal;
- `(organization, role)` pair must exactly match an active relationship in the locked DAO registry;
- match must be unique and canonically sorted;
- verdict must remain consistent with the match list and disclosure flags.

### Deployment schema isolation

The v1 migration reference has no public decorators. GenVM lint now discovers one deployable contract, `MandateGlassGovernanceGate`, with the expected 16-method protocol surface.

## Adversarial coverage

Automated tests reject:

1. a model instruction to replace the canary;
2. a response that omits the canary;
3. a response that adds an attacker-controlled schema field;
4. an invented recipient identity;
5. an invented organization/role pair.

Acquisition defenses from v2 remain in force: exact commit/tree identity, bounded recursive tree, Git blob SHA-1 recomputation, SHA-256 evidence receipt, strict JSON schemas, path/repository validation, size limits, validator equality, scoped authorization, atomic consumption, deadlines, revisions, and replay rejection.

## Reporting

Please open a private GitHub security advisory for suspected vulnerabilities. Do not include secrets, private keys, or personal evidence in a public issue.
