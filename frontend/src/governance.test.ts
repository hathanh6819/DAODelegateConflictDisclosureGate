import{describe,expect,it}from'vitest';
import{executionBlockReason,walletChanged}from'./App';
const delegate='0x1111111111111111111111111111111111111111';
const review:any={review_id:1,proposal_id:1,dao_id:1,delegate,state:3,revision:2,retry_count:0,verdict:1,reason:'CLEAR',evidence_digest:'sha256:x',match_count:0,authorization_consumed:0,authorization_scope:'sha256:scope'};
const proposal:any={proposal_id:1,dao_id:1,external_id:'DAO-42',snapshot_commit:'a'.repeat(40),action_digest:'sha256:'+'b'.repeat(64),deadline:'2000',revision:1,open:true};
describe('governance frontend guards',()=>{
 it('detects wallet/account changes before signing',()=>expect(walletChanged(delegate,'0x2222222222222222222222222222222222222222')).toBe(true));
 it('blocks a stale review revision',()=>expect(executionBlockReason(review,proposal,1000,delegate,1)).toBe('STALE_REVISION'));
 it('blocks deadline expiry',()=>expect(executionBlockReason(review,proposal,2001)).toBe('VOTE_WINDOW_CLOSED'));
 it('surfaces unresolved evidence for retry',()=>expect(executionBlockReason({...review,state:5},proposal,1000)).toBe('UNRESOLVED_EVIDENCE'));
 it('blocks an unapproved review',()=>expect(executionBlockReason({...review,state:2},proposal,1000)).toBe('NOT_AUTHORIZED'));
 it('permits the exact authorized governance path',()=>expect(executionBlockReason(review,proposal,1000)).toBe(''));
 it('blocks replay after atomic consumption',()=>expect(executionBlockReason({...review,state:4,authorization_consumed:1},proposal,1000)).toBe('NOT_AUTHORIZED'));
});
