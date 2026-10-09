# Mandate Glass v4.0.1 — Live Studionet E2E Evidence

**Date:** 2026-10-09  
**Contract:** [`0x28A7CD54d40F85a466E482695E263372A7CE43dA`](https://explorer-studio.genlayer.com/address/0x28A7CD54d40F85a466E482695E263372A7CE43dA)  
**Protocol:** `MandateGlassGovernanceGate` v4  
**Security profile:** `CANARY_GROUNDING_AND_RECUSAL_LINEAGE`  
**Source SHA-256:** `1bc6dfe09192b6c460526d70f249b80d898870afb67607793e5933bbc89a8488` (47,288 bytes)

## Result

The live lifecycle proves that an undisclosed conflict cannot receive a vote authorization, but governance does not dead-end. The conflicted delegate recused on-chain, the DAO authority appointed a distinct substitute bound to a fresh canonical evidence commit, and only that substitute could consume the newly issued authorization. Recycling the original delegate, appointing twice, predecessor voting and vote replay all finalized with execution errors.

Final counts: `1 DAO / 1 proposal / 2 reviews / 1 substitution / 1 vote`.

| Review | Delegate | Evidence | Verdict | Final state | Parent | Successor |
|---:|---|---|---|---|---:|---:|
| 1 | `0x1D283b45974B0be9630DFD1deC6A62a9B72B2760` | `4ebd44c…` | `UNDISCLOSED_CONFLICT` | `SUPERSEDED` | — | 2 |
| 2 | `0xf96Cf822F9f4e76956AB9fAAa22B3BdCD7b10aD6` | `bcf53e28…` | `CLEAR` | `CONSUMED` | 1 | — |

The single recorded vote belongs to the substitute and is bound to action digest `sha256:0092e5dd73c637a77c2ae2c600c87e751535218914b6bf0c01ea6fd30bef0e32`.

## Canonical evidence

- Fixture repository: [DAODelegateConflictEvidenceFixtures](https://github.com/hathanh6819/DAODelegateConflictEvidenceFixtures)
- Original delegate conflict snapshot: [`4ebd44c`](https://github.com/hathanh6819/DAODelegateConflictEvidenceFixtures/commit/4ebd44c76a0c86f35537cef8ef0b9f6bd72b4f08)
- Substitute fresh-clear snapshot: [`bcf53e2`](https://github.com/hathanh6819/DAODelegateConflictEvidenceFixtures/commit/bcf53e28e59b03e98f5225c5036ee9e456d66ae1)
- Conflict digest: `sha256:bdf8857f1b2be928418571e662ecaf2cb2a0a8d6fda9024e1e1f367b097b3441`
- Substitute digest: `sha256:6c1d0b33c7cb52b115a34a4fd8ef7c5bc6da655267555bd55039447cb2515128`
- Substitute scope: `sha256:22660cc8d77e78fab5b0e1f7cce65c7d0dd6e79e62f0ad578d0ef86e81326429`

## Finalized transaction ledger

| Step | Result | Transaction |
|---|---|---|
| Register DAO | Success | [`0xfdef…fec0`](https://explorer-studio.genlayer.com/tx/0xfdefc543ebc3c49476b00fcc714ccb7b5efeb6910e53d6e839a6ab66e0fefec0) |
| Register proposal | Success | [`0x6ede…675`](https://explorer-studio.genlayer.com/tx/0x6edeaa55ca86e677ac04366d38ec563dcfd0b78059611bd5df871ed1c7497675) |
| Create original review | Success | [`0xcfde…ced`](https://explorer-studio.genlayer.com/tx/0xcfdee6e55d958d78bceebfcf04992df659ebd88bc851d360c56b91b23c3b6ced) |
| Evaluate undisclosed conflict | Success | [`0x6283…fea`](https://explorer-studio.genlayer.com/tx/0x6283d3e18eac3c68fe13e331c52a7496a3a8ec0769d2cf99a288aff093bb7fea) |
| Authorize conflicted review | Rejected | [`0xdec5…8ca`](https://explorer-studio.genlayer.com/tx/0xdec50f5f8c1ef17234dbc694cbe8f5ebb08764349fc211df23ca76c500efb8ca) |
| Delegate recuses | Success | [`0x12ba…425`](https://explorer-studio.genlayer.com/tx/0x12bad223155668538af4080fd70aaa31738378945c924732d195741764ade425) |
| Recycle original delegate | Rejected | [`0xd8d6…905`](https://explorer-studio.genlayer.com/tx/0xd8d66d5ecca28f89ac52a5e88b188201a848efe15db27051bbec095d57a9f905) |
| Appoint substitute with fresh evidence | Success | [`0x3ada…781`](https://explorer-studio.genlayer.com/tx/0x3adad4f409dbd3df44d060f1fec7980b337c97301593b98723d8460371a68781) |
| Appoint second successor | Rejected | [`0x2f77…d6f`](https://explorer-studio.genlayer.com/tx/0x2f771eca5d2f159adeec49f4ad6b2eff58b4265d3288af0a15d7e2676d1d4d6f) |
| Evaluate substitute snapshot | Success | [`0x96ec…d98`](https://explorer-studio.genlayer.com/tx/0x96ec2cd5570f43b27e61c46c96a4ca3fa8d8a3b2339cd34ef8ca6bf31933dd98) |
| Original delegate uses successor scope | Rejected | [`0xe18a…37c`](https://explorer-studio.genlayer.com/tx/0xe18a9aa56554d3fe4ad3fbda46727794e9db2dac4104a3a893f9521ae245237c) |
| Substitute executes atomic vote | Success | [`0x3ab4…932`](https://explorer-studio.genlayer.com/tx/0x3ab448597833d4bd3f876015f1fe76321aea94ec3c3a7a485c4fdd0ac9e25932) |
| Replay authorization | Rejected | [`0x5605…63c`](https://explorer-studio.genlayer.com/tx/0x56053896aa89920c64fa8f3983be9fbd2cb8e87aad21cdb1b961f8be4915663c) |

The substitute authorization finalized successfully, proven by its `AUTHORIZED` readback and subsequent atomic consumption. The client disconnected after finalization before retaining that transaction hash, so this ledger does not invent one.

## Verification

The lifecycle runners prompt for private keys and never store them. Verified totals: 54 contract/security tests, 11 GenLayer SDK Direct Mode tests, 7 frontend tests, a passing production build, and clean GenVM lint with 19 methods.
