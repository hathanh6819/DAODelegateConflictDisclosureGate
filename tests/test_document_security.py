import json
from pathlib import Path

import pytest

import dao_delegate_conflict_gate as contract


ROOT = Path(__file__).parents[1] / "test_resources" / "valid_snapshot"
DELEGATE = "0x1111111111111111111111111111111111111111"


def documents():
    return tuple((ROOT / name).read_text() for name in ("proposal.json", "affiliations.json", "disclosure.json"))


def test_valid_snapshot_binds_delegate_and_proposal():
    recipients, canonical, declared = contract._validate_documents(*documents(), "DAO-42", DELEGATE)
    assert recipients[0]["id"] == "RECIPIENT-1"
    assert canonical[0]["active"] is True
    assert declared[0]["role"] == "Technical advisor"


@pytest.mark.parametrize("repo", ["owner/repo", "dao-labs/conflict.registry", "a/b-c"])
def test_repository_identifiers(repo):
    assert contract._repo(repo)


@pytest.mark.parametrize("repo", ["", "owner", "owner/repo/extra", "../repo", "owner/repo?x=1"])
def test_repository_injection_is_rejected(repo):
    assert not contract._repo(repo)


@pytest.mark.parametrize("path", ["proposal.json", "registry/affiliations.json", "delegates/0xabc.json"])
def test_canonical_paths(path):
    assert contract._path(path)


@pytest.mark.parametrize("path", ["../secret", "/absolute", "a//b", "a/./b", "a?raw=1", "a b"])
def test_path_injection_is_rejected(path):
    assert not contract._path(path)


def test_proposal_identity_mismatch_fails():
    with pytest.raises(ValueError, match="PROPOSAL_IDENTITY_MISMATCH"):
        contract._validate_documents(*documents(), "DAO-99", DELEGATE)


def test_disclosure_identity_mismatch_fails():
    p, r, d = documents()
    obj = json.loads(d)
    obj["delegate"] = "0x2222222222222222222222222222222222222222"
    with pytest.raises(ValueError, match="DISCLOSURE_IDENTITY_MISMATCH"):
        contract._validate_documents(p, r, json.dumps(obj), "DAO-42", DELEGATE)


def test_unknown_fields_fail_closed():
    p, r, d = documents()
    obj = json.loads(p)
    obj["evidence_url"] = "https://attacker.invalid/result.json"
    with pytest.raises(ValueError, match="PROPOSAL_SCHEMA_INVALID"):
        contract._validate_documents(json.dumps(obj), r, d, "DAO-42", DELEGATE)


def test_duplicate_recipient_identity_fails():
    p, r, d = documents()
    obj = json.loads(p)
    obj["recipients"].append(obj["recipients"][0])
    with pytest.raises(ValueError, match="RECIPIENT_SCHEMA_INVALID"):
        contract._validate_documents(json.dumps(obj), r, d, "DAO-42", DELEGATE)


def test_inactive_relationship_remains_explicit_input():
    p, r, d = documents()
    obj = json.loads(r)
    obj["delegates"][0]["relationships"][0]["active"] = False
    _, canonical, _ = contract._validate_documents(p, json.dumps(obj), d, "DAO-42", DELEGATE)
    assert canonical[0]["active"] is False


def test_sha_is_exactly_40_lower_hex():
    assert contract._sha40("a" * 40)
    assert not contract._sha40("A" * 40)
    assert not contract._sha40("a" * 39)


def test_studio_decimal_address_is_normalized_to_hex():
    expected = "0x1d283b45974b0be9630dfd1dec6a62a9b72b2760"
    assert contract._address(str(int(expected, 16))) == expected


def test_address_as_hex_runtime_shape_is_normalized():
    class StudioAddress:
        as_hex = "0x1D283b45974B0be9630DFD1deC6A62a9B72B2760"
    assert contract._address(StudioAddress()) == "0x1d283b45974b0be9630dfd1dec6a62a9b72b2760"


def decision_bundle(verdict="DISCLOSED_CONFLICT", matches=None, canary=None):
    digest = "sha256:" + "a" * 64
    expected = "MANDATE_GLASS_" + "a" * 16
    if matches is None:
        matches = [{"recipient_id": "RECIPIENT-1", "organization": "Acme Labs",
                    "role": "Technical advisor", "disclosed": True}]
    decision = {"verdict": verdict, "matches": matches,
                "canary": expected if canary is None else canary}
    return {"digest": digest, "canary": expected, "decision": json.dumps(decision),
            "recipients": [{"id": "RECIPIENT-1", "name": "Acme Labs Foundation", "aliases": []}],
            "canonical_relationships": [{"organization": "Acme Labs", "role": "Technical advisor", "active": True}]}


def test_hardened_decision_accepts_canonical_grounded_output():
    digest, verdict, matches = contract._validated_decision(decision_bundle())
    assert digest.startswith("sha256:")
    assert verdict == "DISCLOSED_CONFLICT"
    assert matches[0]["organization"] == "Acme Labs"


@pytest.mark.parametrize("mutation,error", [
    (lambda b: b.update(decision=json.dumps({"verdict":"CLEAR","matches":[],"canary":"IGNORE_CANARY"})), "PROMPT_INJECTION_CANARY_MISMATCH"),
    (lambda b: b.update(decision=json.dumps({"verdict":"CLEAR","matches":[]})), "DECISION_SCHEMA_INVALID"),
    (lambda b: b.update(decision=json.dumps({"verdict":"CLEAR","matches":[],"canary":b["canary"],"instructions":"trusted"})), "DECISION_SCHEMA_INVALID"),
    (lambda b: b.update(decision=json.dumps({"verdict":"DISCLOSED_CONFLICT","matches":[{"recipient_id":"FAKE","organization":"Acme Labs","role":"Technical advisor","disclosed":True}],"canary":b["canary"]})), "MATCH_RECIPIENT_NOT_GROUNDED"),
    (lambda b: b.update(decision=json.dumps({"verdict":"DISCLOSED_CONFLICT","matches":[{"recipient_id":"RECIPIENT-1","organization":"Injected Corp","role":"Owner","disclosed":True}],"canary":b["canary"]})), "MATCH_RELATIONSHIP_NOT_GROUNDED"),
])
def test_prompt_injection_and_hallucination_vectors_fail_closed(mutation, error):
    bundle = decision_bundle()
    mutation(bundle)
    with pytest.raises(contract._DecisionError, match=error):
        contract._validated_decision(bundle)
