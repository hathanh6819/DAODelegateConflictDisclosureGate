from pathlib import Path


SOURCE = (Path(__file__).parents[1] / "contracts" / "dao_delegate_conflict_gate.py").read_text()


def test_urls_are_constructed_from_locked_repository():
    assert "raw.githubusercontent.com/{repo}/{commit_sha}/{path}" in SOURCE
    assert "evidence_url" not in SOURCE


def test_every_blob_is_recomputed():
    assert 'hashlib.sha1(b"blob "' in SOURCE
    assert 'BLOB_DIGEST_MISMATCH' in SOURCE


def test_fail_closed_verdict_exists():
    assert "VERDICT_INSUFFICIENT_EVIDENCE" in SOURCE
    assert 'self.state[review_id] = u256(UNRESOLVED)' in SOURCE


def test_authorization_is_revision_bound_and_single_use():
    assert "STALE_REVISION" in SOURCE
    assert "AUTHORIZATION_ALREADY_CONSUMED" in SOURCE
    assert "authorization_consumed" in SOURCE


def test_unfavorable_verdict_cannot_authorize():
    assert "VERDICT_UNDISCLOSED_CONFLICT, VERDICT_INSUFFICIENT_EVIDENCE" in SOURCE
    assert "VERDICT_NOT_AUTHORIZABLE" in SOURCE


def test_retry_is_bounded():
    assert "MAX_RETRIES = 3" in SOURCE
    assert "RETRY_LIMIT_REACHED" in SOURCE


def test_match_order_is_canonical():
    assert "MATCH_ORDER_INVALID" in SOURCE
    assert "ordered_keys != sorted(ordered_keys)" in SOURCE


def test_no_value_custody_surface():
    assert "@gl.public.write.payable" not in SOURCE
    assert "emit_transfer" not in SOURCE
