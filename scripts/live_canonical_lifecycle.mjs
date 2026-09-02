import { createAccount, createClient } from '../frontend/node_modules/genlayer-js/dist/index.js';
import { studionet } from '../frontend/node_modules/genlayer-js/dist/chains/index.js';
import { TransactionStatus } from '../frontend/node_modules/genlayer-js/dist/types/index.js';

const ADDRESS = '0x2C32b1A27C80C81239Ba883812979E2E1b358786';
const REPO = 'hathanh6819/DAODelegateConflictEvidenceFixtures';
const DELEGATE = '0xc67532aef9d2879cba9375a02e6217a3524657b8';
const COMMITS = {
  disclosed: '9219776b7398f5e30b354b1e97c47f02bdd0dcf4',
  undisclosed: '160b50e69190ee81334b896065840ee7a8e5746b',
  ambiguous: '27dadd3c94f7b2266f81f463ca6c9c645e91fd33',
  clear: '979eb6b163c53e44486995952942608793d9e118',
};
const account = createAccount('0x4f3edf983ac636a65a842ce7c78d9aa706d3b113bce9c46f30d7d21715b23b1d');
const writer = createClient({ chain: studionet, account });
const reader = createClient({ chain: studionet });

const explorer = hash => `https://explorer-studio.genlayer.com/tx/${hash}`;
const sleep = ms => new Promise(resolve => setTimeout(resolve, ms));

async function finalized(label, hash, shouldSucceed = true) {
  console.log(`TX ${label} ${hash} ${explorer(hash)}`);
  const receipt = await reader.waitForTransactionReceipt({ hash, status: TransactionStatus.FINALIZED, interval: 4000, retries: 120 });
  const tx = await reader.getTransaction({ hash });
  const leader = receipt?.consensus_data?.leader_receipt;
  const leaders = Array.isArray(leader) ? leader : leader ? [leader] : [];
  const execution = leaders.filter(item => item.vote !== 'idle').map(item => item.execution_result);
  const success = execution.length > 0 && execution.every(result => result === 'SUCCESS');
  console.log(`RESULT ${label} finalized=${tx.status_name ?? 'FINALIZED'} consensus=${tx.result_name} execution=${execution.join(',') || 'MISSING'}`);
  if (success !== shouldSucceed) throw new Error(`${label}: expected success=${shouldSucceed}, execution=${execution.join(',') || 'MISSING'}`);
  return tx;
}

async function write(label, functionName, args, shouldSucceed = true) {
  const hash = await writer.writeContract({ address: ADDRESS, functionName, args, value: 0n });
  await finalized(label, hash, shouldSucceed);
  await sleep(1000);
  return hash;
}

async function review(id) {
  return reader.readContract({ address: ADDRESS, functionName: 'get_review', args: [BigInt(id)], jsonSafeReturn: true });
}

async function create(label, commit) {
  const before = Number(await reader.readContract({ address: ADDRESS, functionName: 'get_count', args: [] }));
  const deadline = BigInt(Math.floor(Date.now() / 1000) + 86400);
  await write(`${label}:create`, 'create_review', [REPO, commit, 'proposal.json', 'affiliations.json', 'disclosure.json', 'DAO-42', DELEGATE, 'Active relationships to proposal recipients must be disclosed before voting.', deadline]);
  const after = Number(await reader.readContract({ address: ADDRESS, functionName: 'get_count', args: [] }));
  if (after !== before + 1) throw new Error(`${label}: count invariant failed`);
  return after;
}

async function evaluate(label, id) {
  await write(`${label}:evaluate`, 'evaluate_review', [BigInt(id), 1n]);
  const state = await review(id);
  console.log(`STATE ${label}`, JSON.stringify(state));
  if (state.state !== 2 || !String(state.evidence_digest).startsWith('sha256:')) throw new Error(`${label}: evaluation did not bind evidence`);
  return state;
}

async function main() {
  console.log(`ACCOUNT ${account.address}`);
  console.log(`CONTRACT ${ADDRESS}`);
  let count = Number(await reader.readContract({ address: ADDRESS, functionName: 'get_count', args: [] }));

  let disclosedId = 1;
  if (count === 0) {
    disclosedId = await create('disclosed', COMMITS.disclosed);
    const disclosed = await evaluate('disclosed', disclosedId);
    if (disclosed.verdict !== 2 || disclosed.match_count < 1) throw new Error('disclosed verdict mismatch');
    await write('disclosed:authorize', 'authorize_result', [BigInt(disclosedId), 1n]);
    await write('disclosed:consume', 'consume_authorization', [BigInt(disclosedId), 1n]);
    await write('disclosed:replay-must-fail', 'consume_authorization', [BigInt(disclosedId), 1n], false);
    count = 1;
  }
  const afterReplay = await review(disclosedId);
  if (afterReplay.snapshot_commit !== COMMITS.disclosed || afterReplay.state !== 4 || afterReplay.authorization_consumed !== 1) throw new Error('replay/state invariant failed');

  let undisclosedId = 2;
  if (count < 2) {
    undisclosedId = await create('undisclosed', COMMITS.undisclosed);
    const undisclosed = await evaluate('undisclosed', undisclosedId);
    if (undisclosed.verdict !== 3 || undisclosed.match_count < 1) throw new Error('undisclosed verdict mismatch');
    await write('undisclosed:authorize-must-fail', 'authorize_result', [BigInt(undisclosedId), 1n], false);
    count = 2;
  }
  const afterReject = await review(undisclosedId);
  if (afterReject.snapshot_commit !== COMMITS.undisclosed || afterReject.state !== 2 || afterReject.verdict !== 3 || afterReject.authorization_consumed !== 0) throw new Error('failed authorization changed state');

  if (count >= 3) {
    const ambiguous = await review(3);
    if (ambiguous.snapshot_commit !== COMMITS.ambiguous || ambiguous.state !== 2 || ambiguous.verdict !== 3) throw new Error('ambiguous adversarial record changed');
  }
  let clearId = 4;
  if (count < 4) {
    clearId = await create('clear', COMMITS.clear);
  }
  let clear = await review(clearId);
  if (clear.state === 1) clear = await evaluate('clear', clearId);
  if (clear.verdict !== 1 || clear.match_count !== 0) throw new Error('clear verdict mismatch');
  if (clear.state === 2) {
    await write('clear:authorize', 'authorize_result', [BigInt(clearId), 1n]);
    clear = await review(clearId);
  }
  if (clear.snapshot_commit !== COMMITS.clear || clear.state !== 3 || clear.verdict !== 1) throw new Error('clear authorization invariant failed');
  console.log('FINAL', JSON.stringify({ disclosedId, undisclosedId, clearId, count: await reader.readContract({ address: ADDRESS, functionName: 'get_count', args: [] }) }));
}

main().catch(error => { console.error(error); process.exitCode = 1; });
