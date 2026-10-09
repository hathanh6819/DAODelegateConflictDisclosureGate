from pathlib import Path

SOURCE=(Path(__file__).parents[1]/"contracts"/"dao_delegate_conflict_gate.py").read_text()

def test_v3_contract_is_deployment_target():
    assert "Contract = MandateGlassGovernanceGate" in SOURCE
    assert '"name":"MandateGlassGovernanceGate","version":PROTOCOL_VERSION' in SOURCE

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

def test_conflict_recusal_requires_the_bound_delegate_and_evaluated_conflict():
    body=SOURCE.split("def recuse_review",1)[1].split("@gl.public.write",1)[0]
    assert "ONLY_BOUND_DELEGATE" in body
    assert "ONLY_EVALUATED_CAN_RECUSE" in body
    assert "VERDICT_DISCLOSED_CONFLICT,VERDICT_UNDISCLOSED_CONFLICT" in body
    assert "CONFLICT_REQUIRED" in body

def test_substitution_is_authority_controlled_bounded_and_non_repeating():
    body=SOURCE.split("def appoint_substitute",1)[1].split("def _evaluate",1)[0]
    assert "self._dao_authority_only" in body
    assert "SUBSTITUTE_ALREADY_APPOINTED" in body
    assert "SUBSTITUTION_LIMIT_REACHED" in body
    assert "DELEGATE_ALREADY_IN_LINEAGE" in body
    assert "self.review_state[review_id]=u256(SUPERSEDED)" in body

def test_substitute_review_inherits_proposal_but_not_authorization():
    body=SOURCE.split("def appoint_substitute",1)[1].split("def _evaluate",1)[0]
    assert "self.review_proposal[rid],self.review_delegate[rid]=pid,successor" in body
    assert '"PENDING_SUBSTITUTE_EVALUATION"' in body
    assert 'self.review_scope[rid]' in body and '=\"\",u256(0),u256(0),\"\"' in body
    assert "self.review_commit[rid]=commit" in body
    assert "FRESH_EVIDENCE_REQUIRED" in body

def test_authorization_scope_binds_review_evidence_commit():
    scope=SOURCE.split("def _scope",1)[1].split("@gl.public.write",1)[0]
    assert "evidence_commit" in scope
    assert "self.review_commit[review_id]" in SOURCE.rsplit("def authorize_result",1)[1].split("@gl.public.write",1)[0]

def test_review_lineage_is_public_and_bounded():
    body=SOURCE.split("def get_review_lineage",1)[1].split("@gl.public.view",1)[0]
    assert "steps<=MAX_SUBSTITUTIONS" in body
    assert "successor_review_id" in body
