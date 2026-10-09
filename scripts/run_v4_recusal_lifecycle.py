#!/usr/bin/env python3
"""Run the live Mandate Glass v4 recusal/substitute lifecycle without storing secrets."""
import getpass
import hashlib
import json
import time

from genlayer_py import create_account, create_client, studionet
from genlayer_py.types.transactions import TransactionStatus

CONTRACT="0x28A7CD54d40F85a466E482695E263372A7CE43dA"
AUTHORITY="0x1D283b45974B0be9630DFD1deC6A62a9B72B2760"
SUBSTITUTE="0xf96Cf822F9f4e76956AB9fAAa22B3BdCD7b10aD6"
CONFLICT_COMMIT="4ebd44c76a0c86f35537cef8ef0b9f6bd72b4f08"
CLEAR_COMMIT="bcf53e28e59b03e98f5225c5036ee9e456d66ae1"
ACTION="sha256:"+hashlib.sha256(b"mandate-glass-v4-recusal-vote").hexdigest()

def canonical(value):return json.dumps(value,sort_keys=True,separators=(",",":"),default=str)
def checkpoint(ok,label):
    if not ok:raise RuntimeError("CHECKPOINT FAILED: "+label)
    print("CHECKPOINT OK: "+label,flush=True)
def read(client,method,args=None):
    value=client.read_contract(address=CONTRACT,function_name=method,args=args or [])
    print("READ "+method+"="+canonical(value),flush=True);return value
def execution_results(receipt):
    leader=(receipt.get("consensus_data") or {}).get("leader_receipt") or []
    return [str(x.get("execution_result","")) for x in (leader if isinstance(leader,list) else [leader]) if x and x.get("vote")!="idle"]
def write(client,label,method,args,should_succeed=True):
    tx=client.write_contract(address=CONTRACT,function_name=method,args=args,value=0)
    print("TX "+label+"="+str(tx),flush=True)
    receipt=client.wait_for_transaction_receipt(tx,status=TransactionStatus.FINALIZED,interval=4000,retries=300,full_transaction=True)
    results=execution_results(receipt);success=bool(results) and all(x=="SUCCESS" for x in results)
    print("FINAL "+label+"="+canonical({"hash":str(tx),"status":receipt.get("status_name"),"result":receipt.get("result_name"),"execution":results}),flush=True)
    checkpoint(success==should_succeed,label+(" succeeds" if should_succeed else " is rejected"));return str(tx)

def main():
    key_a=getpass.getpass("Authority/delegate private key: ").strip()
    key_b=getpass.getpass("Substitute private key: ").strip()
    authority=create_account(key_a);substitute=create_account(key_b);key_a=key_b=""
    checkpoint(str(authority.address).lower()==AUTHORITY.lower(),"authority identity")
    checkpoint(str(substitute.address).lower()==SUBSTITUTE.lower(),"substitute identity")
    a=create_client(chain=studionet,account=authority);b=create_client(chain=studionet,account=substitute)
    checkpoint(read(a,"get_counts")=={"daos":1,"proposals":0,"reviews":0,"votes":0,"substitutions":0},"clean registered DAO")
    deadline=int(time.time())+7*24*60*60
    txs={"register_dao":"0xfdefc543ebc3c49476b00fcc714ccb7b5efeb6910e53d6e839a6ab66e0fefec0"}
    txs["register_proposal"]=write(a,"register_proposal","register_proposal",[1,"DAO-42",CONFLICT_COMMIT,ACTION,deadline])
    txs["create_conflict_review"]=write(a,"create_conflict_review","create_review",[1,AUTHORITY])
    txs["evaluate_conflict"]=write(a,"evaluate_conflict","evaluate_review",[1,1])
    conflict=read(a,"get_review",[1]);checkpoint(conflict["state"]==2 and conflict["verdict"]==3,"undisclosed conflict grounded")
    txs["authorize_conflict_rejected"]=write(a,"authorize_conflict_rejected","authorize_result",[1,1],False)
    txs["recuse_conflict"]=write(a,"recuse_conflict","recuse_review",[1,1])
    txs["recycled_delegate_rejected"]=write(a,"recycled_delegate_rejected","appoint_substitute",[1,1,AUTHORITY,CLEAR_COMMIT],False)
    txs["appoint_substitute"]=write(a,"appoint_substitute","appoint_substitute",[1,1,SUBSTITUTE,CLEAR_COMMIT])
    original=read(a,"get_review",[1]);successor=read(a,"get_review",[2])
    checkpoint(original["state"]==8 and original["successor_review_id"]==2,"predecessor superseded")
    checkpoint(successor["state"]==1 and successor["parent_review_id"]==1 and successor["evidence_commit"]==CLEAR_COMMIT and not successor["authorization_scope"],"fresh substitute review isolated")
    txs["second_appointment_rejected"]=write(a,"second_appointment_rejected","appoint_substitute",[1,1,SUBSTITUTE,CLEAR_COMMIT],False)
    txs["evaluate_substitute"]=write(b,"evaluate_substitute","evaluate_review",[2,1])
    clear=read(b,"get_review",[2]);checkpoint(clear["state"]==2 and clear["verdict"]==1 and clear["match_count"]==0,"substitute clear verdict grounded")
    txs["authorize_substitute"]=write(b,"authorize_substitute","authorize_result",[2,1])
    txs["predecessor_vote_rejected"]=write(a,"predecessor_vote_rejected","execute_vote",[2,1,ACTION,True],False)
    txs["execute_substitute_vote"]=write(b,"execute_substitute_vote","execute_vote",[2,1,ACTION,True])
    txs["replay_rejected"]=write(b,"replay_rejected","execute_vote",[2,1,ACTION,True],False)
    final=read(b,"get_counts");lineage=read(b,"get_review_lineage",[2]);vote=read(b,"get_vote",[1])
    checkpoint(final=={"daos":1,"proposals":1,"reviews":2,"votes":1,"substitutions":1},"final v4 counts")
    checkpoint([x["review_id"] for x in lineage]==[1,2] and lineage[0]["state"]==8 and lineage[1]["state"]==4,"root-first lineage")
    checkpoint(vote["delegate"].lower()==SUBSTITUTE.lower(),"only substitute vote recorded")
    print("LIFECYCLE_COMPLETE\ntransactions="+canonical(txs)+"\nfinal_counts="+canonical(final),flush=True)

if __name__=="__main__":main()
