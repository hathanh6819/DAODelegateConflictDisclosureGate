from pathlib import Path

SOURCE=(Path(__file__).parents[1]/"contracts"/"dao_delegate_conflict_gate.py").read_text()

def test_v2_contract_is_deployment_target():
    assert "Contract = MandateGlassGovernanceGate" in SOURCE
    assert '"name":"MandateGlassGovernanceGate","version":2' in SOURCE

def test_authority_controls_canonical_sources():
    assert "ONLY_DAO_AUTHORITY" in SOURCE
    assert "STALE_DAO_REVISION" in SOURCE
    assert "def update_dao_sources" in SOURCE

def test_proposal_binds_commit_action_and_deadline():
    assert "proposal_commit" in SOURCE
    assert "proposal_action" in SOURCE
    assert "proposal_deadline" in SOURCE

def test_authorization_scope_is_complete():
    for field in ("dao_authority","proposal_revision","review_revision","proposal_deadline","proposal_action"):
        assert field in SOURCE
    assert "AUTHORIZATION_SCOPE_MISMATCH" in SOURCE

def test_governance_action_and_consumption_are_atomic():
    body=SOURCE.split("def execute_vote",1)[1].split("@gl.public.view",1)[0]
    assert "self.vote_count=vid" in body
    assert "self.review_consumed[review_id],self.review_state[review_id]" in body

def test_hidden_and_unresolved_results_cannot_authorize():
    assert "VERDICT_CLEAR,VERDICT_DISCLOSED_CONFLICT" in SOURCE
    assert "VERDICT_NOT_AUTHORIZABLE" in SOURCE

def test_action_identity_and_delegate_are_enforced():
    assert "ACTION_SCOPE_MISMATCH" in SOURCE
    assert "ONLY_BOUND_DELEGATE" in SOURCE

def test_no_payout_or_custody_surface_in_v2():
    v2=SOURCE.split("class MandateGlassGovernanceGate",1)[1]
    assert "@gl.public.write.payable" not in v2
    assert "emit_transfer" not in v2
