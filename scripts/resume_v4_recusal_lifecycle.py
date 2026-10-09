#!/usr/bin/env python3
"""Resume v4 after substitute authorization was finalized during an RPC disconnect."""
import getpass,hashlib,json
from genlayer_py import create_account,create_client,studionet
from genlayer_py.types.transactions import TransactionStatus

CONTRACT="0x28A7CD54d40F85a466E482695E263372A7CE43dA"
AUTHORITY="0x1D283b45974B0be9630DFD1deC6A62a9B72B2760"
SUBSTITUTE="0xf96Cf822F9f4e76956AB9fAAa22B3BdCD7b10aD6"
ACTION="sha256:"+hashlib.sha256(b"mandate-glass-v4-recusal-vote").hexdigest()
def canonical(v):return json.dumps(v,sort_keys=True,separators=(",",":"),default=str)
def read(c,m,args=None):
 v=c.read_contract(address=CONTRACT,function_name=m,args=args or []);print("READ "+m+"="+canonical(v),flush=True);return v
def results(r):
 leader=(r.get("consensus_data") or {}).get("leader_receipt") or []
 return [str(x.get("execution_result","")) for x in (leader if isinstance(leader,list) else [leader]) if x and x.get("vote")!="idle"]
def write(c,label,m,args,success=True):
 tx=c.write_contract(address=CONTRACT,function_name=m,args=args,value=0);print("TX "+label+"="+str(tx),flush=True)
 r=c.wait_for_transaction_receipt(tx,status=TransactionStatus.FINALIZED,interval=4000,retries=300,full_transaction=True);xs=results(r);ok=bool(xs) and all(x=="SUCCESS" for x in xs)
 print("FINAL "+label+"="+canonical({"hash":str(tx),"status":r.get("status_name"),"result":r.get("result_name"),"execution":xs}),flush=True)
 assert ok==success;return str(tx)
def main():
 a=create_account(getpass.getpass("Authority/delegate private key: ").strip());b=create_account(getpass.getpass("Substitute private key: ").strip())
 assert str(a.address).lower()==AUTHORITY.lower() and str(b.address).lower()==SUBSTITUTE.lower()
 ca=create_client(chain=studionet,account=a);cb=create_client(chain=studionet,account=b)
 r=read(cb,"get_review",[2]);assert r["state"]==3 and r["authorization_scope"]
 txs={}
 txs["predecessor_vote_rejected"]=write(ca,"predecessor_vote_rejected","execute_vote",[2,1,ACTION,True],False)
 txs["execute_substitute_vote"]=write(cb,"execute_substitute_vote","execute_vote",[2,1,ACTION,True])
 txs["replay_rejected"]=write(cb,"replay_rejected","execute_vote",[2,1,ACTION,True],False)
 counts=read(cb,"get_counts");lineage=read(cb,"get_review_lineage",[2]);vote=read(cb,"get_vote",[1])
 assert counts=={"daos":1,"proposals":1,"reviews":2,"substitutions":1,"votes":1}
 assert [x["review_id"] for x in lineage]==[1,2] and lineage[0]["state"]==8 and lineage[1]["state"]==4
 assert vote["delegate"].lower()==SUBSTITUTE.lower()
 print("RESUME_COMPLETE\ntransactions="+canonical(txs),flush=True)
if __name__=="__main__":main()
