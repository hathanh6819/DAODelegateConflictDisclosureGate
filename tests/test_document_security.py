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
