export type Review = {
  review_id:number; creator:string; repository:string; snapshot_commit:string;
  proposal_path:string; registry_path:string; disclosure_path:string; proposal_id:string;
  delegate:string; policy:string; vote_deadline:string; created_at:string; state:number;
  revision:number; retry_count:number; verdict:number; reason:string; evidence_digest:string;
  match_count:number; authorization_consumed:number;
};
export type Match = {recipient_id:string;organization:string;role:string;disclosed:boolean};
const address = import.meta.env.VITE_CONTRACT_ADDRESS?.trim();
let sdkPromise:Promise<any>|null=null;
let clientPromise:Promise<any>|null=null;
async function sdk(){if(!sdkPromise)sdkPromise=Promise.all([import('genlayer-js'),import('genlayer-js/chains'),import('genlayer-js/types')]).then(([core,chains,types])=>({createClient:core.createClient,studionet:chains.studionet,TransactionStatus:types.TransactionStatus}));return sdkPromise;}
async function reader(){if(!clientPromise)clientPromise=sdk().then(({createClient,studionet})=>createClient({chain:studionet}));return clientPromise;}
export const contractAddress = address || '';
function requireAddress(){if(!/^0x[0-9a-fA-F]{40}$/.test(contractAddress)) throw new Error('Verified contract address is not configured.'); return contractAddress as `0x${string}`;}
export async function read<T>(functionName:string,args:(string|number)[]=[]):Promise<T>{
  const client=await reader();
  const value=await client.readContract({address:requireAddress(),functionName,args,jsonSafeReturn:true});
  return value as T;
}
export async function loadReviews(){
  const [protocol,count]=await Promise.all([read<any>('get_protocol'),read<number>('get_count')]);
  if(protocol?.name!=='DAODelegateConflictDisclosureGate'||protocol?.version!==1) throw new Error('Contract identity or protocol version mismatch.');
  if(!Number.isSafeInteger(count)||count<0) throw new Error('Invalid review count.');
  const first=Math.max(1,count-49); const ids=Array.from({length:Math.max(0,count-first+1)},(_,i)=>first+i);
  const reviews:Review[]=[]; const matches:Record<number,Match[]>={};
  for(let offset=0;offset<ids.length;offset+=8){
    const batch=await Promise.all(ids.slice(offset,offset+8).map(async id=>{
      const review=await read<Review>('get_review',[id]);
      if(review.review_id!==id||review.match_count<0||review.match_count>12) throw new Error('Invalid review record.');
      const rows=await Promise.all(Array.from({length:review.match_count},(_,index)=>read<Match>('get_match',[id,index])));
      return {review,rows};
    }));
    batch.forEach(({review,rows})=>{reviews.push(review);matches[review.review_id]=rows;});
  }
  return {reviews,matches,total:count};
}
async function wallet(){
  const provider=(window as any).ethereum; if(!provider?.request) throw new Error('Install a compatible browser wallet.');
  const accounts=await provider.request({method:'eth_requestAccounts'}); const account=accounts?.[0];
  if(!/^0x[0-9a-fA-F]{40}$/.test(account||'')) throw new Error('Wallet returned no valid account.');
  const {createClient,studionet}=await sdk();
  await createClient({chain:studionet,provider,account}).connect('studionet'); return {provider,account};
}
export async function connect(){return (await wallet()).account as string;}
export async function write(functionName:string,args:(string|number)[],expected:string){
  const {provider,account}=await wallet(); if(account.toLowerCase()!==expected.toLowerCase()) throw new Error('Wallet account changed. Reconnect.');
  const {createClient,studionet,TransactionStatus}=await sdk(); const client=await reader();
  const hash=await createClient({chain:studionet,provider,account}).writeContract({address:requireAddress(),functionName,args,value:0n});
  if(!/^0x[0-9a-fA-F]{64}$/.test(hash)) throw new Error('No valid transaction hash returned.');
  const receipt:any=await client.waitForTransactionReceipt({hash,status:TransactionStatus.FINALIZED,interval:4000,retries:90});
  const leaders=receipt?.consensus_data?.leader_receipt; const list=Array.isArray(leaders)?leaders:leaders?[leaders]:[];
  if(!list.length||list.some((item:any)=>item.execution_result!=='SUCCESS')) throw new Error(`Finalized execution failed. Inspect ${hash}.`);
  return hash as string;
}
