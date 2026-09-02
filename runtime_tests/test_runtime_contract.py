import hashlib
import json
import re
from datetime import datetime
import pytest

CONTRACT="contracts/dao_delegate_conflict_gate.py"
REPO="authority/dao-governance"
COMMIT="a"*40
DELEGATE="0x1111111111111111111111111111111111111111"

def deadline(vm):
    return int(datetime.fromisoformat(vm._datetime.replace("Z","+00:00")).timestamp())+3600

def create(contract,vm):
    return contract.create_review(REPO,COMMIT,"proposal.json","affiliations.json","disclosure.json","DAO-42",DELEGATE,
                                  "Active relationships to recipients must be disclosed",deadline(vm))

def mock_snapshot(vm, disclosed=True):
    docs={
      "proposal.json":json.dumps({"proposal_id":"DAO-42","recipients":[{"id":"R1","name":"Acme Labs Foundation","aliases":["Acme Labs"]}]},separators=(",",":")),
      "affiliations.json":json.dumps({"delegates":[{"address":DELEGATE,"relationships":[{"organization":"Acme Labs","role":"Advisor","active":True}]}]},separators=(",",":")),
      "disclosure.json":json.dumps({"delegate":DELEGATE,"relationships":[{"organization":"Acme Labs Foundation","role":"Advisor"}] if disclosed else []},separators=(",",":"))}
    entries=[]
    for path,body in docs.items():
        raw=body.encode();blob=hashlib.sha1(b"blob "+str(len(raw)).encode()+b"\x00"+raw).hexdigest()
        entries.append({"path":path,"mode":"100644","type":"blob","sha":blob,"size":len(raw)})
    tree="b"*40; api=f"https://api.github.com/repos/{REPO}"
    responses={f"{api}/git/commits/{COMMIT}":json.dumps({"sha":COMMIT,"tree":{"sha":tree}}),
               f"{api}/git/trees/{tree}?recursive=1":json.dumps({"sha":tree,"truncated":False,"tree":entries})}
    for path,body in docs.items():responses[f"https://raw.githubusercontent.com/{REPO}/{COMMIT}/{path}"]=body
    for url,body in responses.items():vm.mock_web("^"+re.escape(url)+"$",{"status":200,"body":body})

def test_real_sdk_schema_and_creation(direct_deploy,direct_vm):
    c=direct_deploy(CONTRACT);assert c.get_protocol()["version"]==1;assert c.get_count()==0
    assert create(c,direct_vm)==1;record=c.get_review(1);assert record["delegate"].lower()==DELEGATE;assert record["state"]==1

def test_canonical_disclosed_conflict_authorization_is_single_use(direct_deploy,direct_vm):
    c=direct_deploy(CONTRACT);rid=create(c,direct_vm);mock_snapshot(direct_vm,True)
    direct_vm.mock_llm("conflict-of-interest disclosure verifier",json.dumps({"verdict":"DISCLOSED_CONFLICT","matches":[{"recipient_id":"R1","organization":"Acme Labs","role":"Advisor","disclosed":True}]}))
    c.evaluate_review(rid,1);review=c.get_review(rid);assert review["verdict"]==2;assert len(review["evidence_digest"])==71
    assert c.get_match(rid,0)["disclosed"] is True
    c.authorize_result(rid,1);c.consume_authorization(rid,1);assert c.get_review(rid)["state"]==4
    with pytest.raises(Exception,match="NOT_AUTHORIZED"):c.consume_authorization(rid,1)

def test_undisclosed_conflict_cannot_authorize(direct_deploy,direct_vm):
    c=direct_deploy(CONTRACT);rid=create(c,direct_vm);mock_snapshot(direct_vm,False)
    direct_vm.mock_llm("conflict-of-interest disclosure verifier",json.dumps({"verdict":"UNDISCLOSED_CONFLICT","matches":[{"recipient_id":"R1","organization":"Acme Labs","role":"Advisor","disclosed":False}]}))
    c.evaluate_review(rid,1);assert c.get_review(rid)["verdict"]==3
    with pytest.raises(Exception,match="VERDICT_NOT_AUTHORIZABLE"):c.authorize_result(rid,1)

def test_malformed_model_output_is_retryable_and_non_authorizable(direct_deploy,direct_vm):
    c=direct_deploy(CONTRACT);rid=create(c,direct_vm);mock_snapshot(direct_vm,True)
    direct_vm.mock_llm("conflict-of-interest disclosure verifier","not-json")
    c.evaluate_review(rid,1);review=c.get_review(rid);assert review["state"]==5;assert review["evidence_digest"]==""
    with pytest.raises(Exception,match="INVALID_REVIEW_STATE"):c.authorize_result(rid,1)

def test_creator_can_cancel_only_before_evaluation(direct_deploy,direct_vm):
    c=direct_deploy(CONTRACT);rid=create(c,direct_vm);c.cancel_pending(rid);assert c.get_review(rid)["state"]==6
    with pytest.raises(Exception,match="ONLY_PENDING_CAN_CANCEL"):c.cancel_pending(rid)

@pytest.mark.parametrize("repo",["../repo","owner","owner/repo/extra"])
def test_repository_injection_rejected_in_real_contract(direct_deploy,direct_vm,repo):
    c=direct_deploy(CONTRACT)
    with pytest.raises(Exception,match="INVALID_REPOSITORY"):
        c.create_review(repo,COMMIT,"proposal.json","affiliations.json","disclosure.json","DAO-42",DELEGATE,"Policy",deadline(direct_vm))
    assert c.get_count()==0
