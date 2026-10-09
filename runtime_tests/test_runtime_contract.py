import hashlib,json,re
from datetime import datetime,timezone
import pytest

CONTRACT="contracts/dao_delegate_conflict_gate.py";REPO="authority/dao-governance";COMMIT="a"*40
DELEGATE="0x1111111111111111111111111111111111111111";OTHER="0x2222222222222222222222222222222222222222";ACTION="sha256:"+"b"*64
def now(vm):return int(datetime.fromisoformat(vm._datetime.replace("Z","+00:00")).timestamp())
def sender(vm,address):
 from genlayer.py.types import Address
 vm.sender=Address(address);vm.origin=Address(address)
def setup(c,vm):
 owner=c.owner;dao=c.register_dao(owner,REPO,"proposal.json","affiliations.json","disclosure.json","Active recipient relationships must be disclosed");pid=c.register_proposal(dao,"DAO-42",COMMIT,ACTION,now(vm)+3600);sender(vm,DELEGATE);rid=c.create_review(pid,DELEGATE);return dao,pid,rid,owner
def mock_snapshot(vm,disclosed=True,delegate=DELEGATE):
 docs={"proposal.json":json.dumps({"proposal_id":"DAO-42","recipients":[{"id":"R1","name":"Acme Labs Foundation","aliases":["Acme Labs"]}]},separators=(",",":")),"affiliations.json":json.dumps({"delegates":[{"address":delegate,"relationships":[{"organization":"Acme Labs","role":"Advisor","active":True}]}]},separators=(",",":")),"disclosure.json":json.dumps({"delegate":delegate,"relationships":[{"organization":"Acme Labs Foundation","role":"Advisor"}] if disclosed else []},separators=(",",":"))}
 entries=[]
 for path,body in docs.items():
  raw=body.encode();blob=hashlib.sha1(b"blob "+str(len(raw)).encode()+b"\x00"+raw).hexdigest();entries.append({"path":path,"mode":"100644","type":"blob","sha":blob,"size":len(raw)})
 tree="c"*40;api=f"https://api.github.com/repos/{REPO}";responses={f"{api}/git/commits/{COMMIT}":json.dumps({"sha":COMMIT,"tree":{"sha":tree}}),f"{api}/git/trees/{tree}?recursive=1":json.dumps({"sha":tree,"truncated":False,"tree":entries})}
 for path,body in docs.items():responses[f"https://raw.githubusercontent.com/{REPO}/{COMMIT}/{path}"]=body
 for url,body in responses.items():vm.mock_web("^"+re.escape(url)+"$",{"status":200,"body":body})
 ordered_urls=[f"{api}/git/commits/{COMMIT}",f"{api}/git/trees/{tree}?recursive=1"]+[f"https://raw.githubusercontent.com/{REPO}/{COMMIT}/{path}" for path in sorted(docs)]
 receipts=[{"url":url,"sha256":hashlib.sha256(responses[url].encode()).hexdigest()} for url in ordered_urls]
 evidence={"repo":REPO,"commit":COMMIT,"proposal_id":"DAO-42","delegate":delegate,"policy":"Active recipient relationships must be disclosed","recipients":json.loads(docs["proposal.json"])["recipients"],"canonical_relationships":json.loads(docs["affiliations.json"])["delegates"][0]["relationships"],"declared_relationships":json.loads(docs["disclosure.json"])["relationships"],"snapshot":{path:{"blob":next(x["sha"] for x in entries if x["path"]==path),"content":body} for path,body in docs.items()},"receipts":receipts}
 digest=hashlib.sha256(json.dumps(evidence,sort_keys=True,separators=(",",":")).encode()).hexdigest();vm._mandate_canary="MANDATE_GLASS_"+digest[:16]
def decide(vm,verdict,disclosed=True):
 matches=[] if verdict=="CLEAR" else [{"recipient_id":"R1","organization":"Acme Labs","role":"Advisor","disclosed":disclosed}];vm.mock_llm("conflict-of-interest disclosure verifier",json.dumps({"verdict":verdict,"matches":matches,"canary":vm._mandate_canary}))

def test_authority_controls_sources_and_stale_revision(direct_deploy,direct_vm):
 c=direct_deploy(CONTRACT);owner=c.owner;dao=c.register_dao(owner,REPO,"proposal.json","affiliations.json","disclosure.json","Policy");sender(direct_vm,OTHER)
 with pytest.raises(Exception,match="ONLY_DAO_AUTHORITY"):c.update_dao_sources(dao,1,REPO,"proposal.json","affiliations.json","disclosure.json","Changed")
 sender(direct_vm,owner);c.update_dao_sources(dao,1,REPO,"proposal.json","affiliations.json","disclosure.json","Changed")
 with pytest.raises(Exception,match="STALE_DAO_REVISION"):c.update_dao_sources(dao,1,REPO,"proposal.json","affiliations.json","disclosure.json","Replay")
def test_delegate_identity_is_bound(direct_deploy,direct_vm):
 c=direct_deploy(CONTRACT);owner=c.owner;dao=c.register_dao(owner,REPO,"proposal.json","affiliations.json","disclosure.json","Policy");pid=c.register_proposal(dao,"DAO-42",COMMIT,ACTION,now(direct_vm)+3600);sender(direct_vm,OTHER)
 with pytest.raises(Exception,match="ONLY_BOUND_DELEGATE"):c.create_review(pid,DELEGATE)
 assert c.get_counts()["reviews"]==0
def test_clear_vote_is_atomic_scoped_and_single_use(direct_deploy,direct_vm):
 c=direct_deploy(CONTRACT);_,pid,rid,_=setup(c,direct_vm);mock_snapshot(direct_vm);decide(direct_vm,"CLEAR");c.evaluate_review(rid,1);c.authorize_result(rid,1);before=c.get_counts()["votes"]
 with pytest.raises(Exception,match="ACTION_SCOPE_MISMATCH"):c.execute_vote(rid,1,"sha256:"+"d"*64,True)
 assert c.get_counts()["votes"]==before and c.get_review(rid)["authorization_consumed"]==0
 vid=c.execute_vote(rid,1,ACTION,True);assert c.get_vote(vid)["proposal_id"]==pid and c.get_review(rid)["authorization_consumed"]==1
 with pytest.raises(Exception,match="NOT_AUTHORIZED"):c.execute_vote(rid,1,ACTION,True)
 assert c.get_counts()["votes"]==before+1
def test_undisclosed_and_unresolved_block_real_vote(direct_deploy,direct_vm):
 c=direct_deploy(CONTRACT);_,_,rid,_=setup(c,direct_vm);mock_snapshot(direct_vm,False);decide(direct_vm,"UNDISCLOSED_CONFLICT",False);c.evaluate_review(rid,1)
 with pytest.raises(Exception,match="VERDICT_NOT_AUTHORIZABLE"):c.authorize_result(rid,1)
 with pytest.raises(Exception,match="NOT_AUTHORIZED"):c.execute_vote(rid,1,ACTION,True)
 assert c.get_counts()["votes"]==0
def test_unresolved_blocks_real_vote(direct_deploy,direct_vm):
 c=direct_deploy(CONTRACT);_,_,rid,_=setup(c,direct_vm);mock_snapshot(direct_vm);direct_vm.mock_llm("conflict-of-interest disclosure verifier","bad");c.evaluate_review(rid,1);assert c.get_review(rid)["state"]==5
 with pytest.raises(Exception,match="INVALID_REVIEW_STATE"):c.authorize_result(rid,1)
 with pytest.raises(Exception,match="NOT_AUTHORIZED"):c.execute_vote(rid,1,ACTION,True)
 assert c.get_counts()["votes"]==0
def test_retry_recovers_unresolved_evidence(direct_deploy,direct_vm):
 c=direct_deploy(CONTRACT);_,_,rid,_=setup(c,direct_vm);mock_snapshot(direct_vm);direct_vm.mock_llm("conflict-of-interest disclosure verifier","bad");c.evaluate_review(rid,1);assert c.get_review(rid)["state"]==5;direct_vm.clear_mocks();mock_snapshot(direct_vm);decide(direct_vm,"DISCLOSED_CONFLICT");c.retry_review(rid,1);assert c.get_review(rid)["state"]==2 and c.get_review(rid)["retry_count"]==1
def test_closed_proposal_invalidates_authorization(direct_deploy,direct_vm):
 c=direct_deploy(CONTRACT);_,pid,rid,owner=setup(c,direct_vm);mock_snapshot(direct_vm);decide(direct_vm,"CLEAR");c.evaluate_review(rid,1);c.authorize_result(rid,1);sender(direct_vm,owner);c.close_proposal(pid,1);sender(direct_vm,DELEGATE)
 with pytest.raises(Exception,match="VOTE_WINDOW_CLOSED"):c.execute_vote(rid,1,ACTION,True)
 assert c.get_counts()["votes"]==0 and c.get_review(rid)["authorization_consumed"]==0
def test_deadline_expiry_blocks_vote_without_consuming(direct_deploy,direct_vm):
 c=direct_deploy(CONTRACT);_,pid,rid,_=setup(c,direct_vm);mock_snapshot(direct_vm);decide(direct_vm,"CLEAR");c.evaluate_review(rid,1);c.authorize_result(rid,1);deadline=int(c.get_proposal(pid)["deadline"]);direct_vm.warp(datetime.fromtimestamp(deadline+1,timezone.utc).isoformat().replace('+00:00','Z'))
 with pytest.raises(Exception,match="VOTE_WINDOW_CLOSED"):c.execute_vote(rid,1,ACTION,True)
 assert c.get_counts()["votes"]==0 and c.get_review(rid)["authorization_consumed"]==0
def test_conflicted_delegate_recuses_and_substitute_completes_fresh_gate(direct_deploy,direct_vm):
 c=direct_deploy(CONTRACT);_,pid,rid,owner=setup(c,direct_vm);mock_snapshot(direct_vm,False);decide(direct_vm,"UNDISCLOSED_CONFLICT",False);c.evaluate_review(rid,1)
 assert c.recuse_review(rid,1)==rid and c.get_review(rid)["state"]==7
 sender(direct_vm,owner);successor=c.appoint_substitute(rid,1,OTHER)
 assert c.get_review(rid)["state"]==8 and c.get_review(rid)["successor_review_id"]==successor
 assert c.get_review(successor)["parent_review_id"]==rid and c.get_review(successor)["authorization_scope"]==""
 with pytest.raises(Exception,match="SUBSTITUTE_ALREADY_APPOINTED"):c.appoint_substitute(rid,1,OTHER)
 sender(direct_vm,OTHER);direct_vm.clear_mocks();mock_snapshot(direct_vm,True,OTHER);decide(direct_vm,"CLEAR");c.evaluate_review(successor,1);c.authorize_result(successor,1);vid=c.execute_vote(successor,1,ACTION,True)
 assert c.get_vote(vid)["delegate"].lower()==OTHER.lower()
 lineage=c.get_review_lineage(successor);assert [x["review_id"] for x in lineage]==[rid,successor]
 assert lineage[0]["state"]==8 and lineage[1]["state"]==4 and c.get_counts()["substitutions"]==1

def test_clear_review_cannot_recuse_and_lineage_cannot_repeat_delegate(direct_deploy,direct_vm):
 c=direct_deploy(CONTRACT);_,_,rid,owner=setup(c,direct_vm);mock_snapshot(direct_vm);decide(direct_vm,"CLEAR");c.evaluate_review(rid,1)
 with pytest.raises(Exception,match="CONFLICT_REQUIRED"):c.recuse_review(rid,1)
 # Turn this fixture into a conflict to exercise lineage identity rejection.
 c.review_verdict[rid]=3;c.recuse_review(rid,1);sender(direct_vm,owner)
 with pytest.raises(Exception,match="DELEGATE_ALREADY_IN_LINEAGE"):c.appoint_substitute(rid,1,DELEGATE)

def test_protocol_and_schema(direct_deploy,direct_vm):
 c=direct_deploy(CONTRACT);assert c.get_protocol()["version"]==4;assert c.get_protocol()["security_profile"]=="CANARY_GROUNDING_AND_RECUSAL_LINEAGE";assert c.get_counts()=={"daos":0,"proposals":0,"reviews":0,"votes":0,"substitutions":0}
