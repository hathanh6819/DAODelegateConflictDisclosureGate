import { createClient } from '../frontend/node_modules/genlayer-js/dist/index.js';
import { studionet } from '../frontend/node_modules/genlayer-js/dist/chains/index.js';

const hash = process.argv[2];
if (!/^0x[0-9a-fA-F]{64}$/.test(hash ?? '')) throw new Error('Usage: node scripts/inspect_transaction.mjs 0x<64 hex>');
const client = createClient({ chain: studionet });
const tx = await client.getTransaction({ hash });
const summarize = receipt => receipt ? {
  mode: receipt.mode,
  vote: receipt.vote,
  execution_result: receipt.execution_result,
  result: receipt.result,
  contract_state_hash: receipt.contract_state_hash,
  error: receipt.genvm_result?.error_description ?? receipt.genvm_result?.stderr ?? '',
} : null;
const consensus = tx.consensus_data ?? {};
console.log(JSON.stringify({
  hash: tx.hash,
  status: tx.statusName ?? tx.status_name,
  consensus_result: tx.result_name,
  last_round: tx.last_round,
  leader_receipt: Array.isArray(consensus.leader_receipt) ? consensus.leader_receipt.map(summarize) : summarize(consensus.leader_receipt),
  validator_receipts: (consensus.validators ?? []).map(summarize),
}, (_, value) => typeof value === 'bigint' ? value.toString() : value, 2));
