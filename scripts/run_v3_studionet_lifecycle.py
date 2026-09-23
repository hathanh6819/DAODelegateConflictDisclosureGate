#!/usr/bin/env python3
"""Run the Mandate Glass v3 Studionet lifecycle without storing secrets."""
import getpass
import hashlib
import json
import time

from genlayer_py import create_account, create_client, studionet
from genlayer_py.types.transactions import TransactionStatus


CONTRACT = "0xbd391006807E5cae85E26E50187F4CC2178c7C9c"
AUTHORITY = "0x1D283b45974B0be9630DFD1deC6A62a9B72B2760"
OUTSIDER = "0xf96Cf822F9f4e76956AB9fAAa22B3BdCD7b10aD6"
REPOSITORY = "hathanh6819/DAODelegateConflictEvidenceFixtures"
CLEAR_COMMIT = "ef4842d0724efe027134bafd856354a8db03872b"
UNDISCLOSED_COMMIT = "4ebd44c76a0c86f35537cef8ef0b9f6bd72b4f08"
POLICY = "Active canonical relationships to proposal recipients must be disclosed before voting."


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":"), default=str)


def checkpoint(condition, label):
    if not condition:
        raise RuntimeError("CHECKPOINT FAILED: " + label)
    print("CHECKPOINT OK: " + label, flush=True)


def read(client, method, args=None):
    value = client.read_contract(address=CONTRACT, function_name=method, args=args or [])
    print("READ " + method + "=" + canonical(value), flush=True)
    return value


def execution_results(receipt):
    consensus = receipt.get("consensus_data") or {}
    leader = consensus.get("leader_receipt") or []
    leaders = leader if isinstance(leader, list) else [leader]
    return [str(item.get("execution_result", "")) for item in leaders
            if item and item.get("vote") != "idle"]


def write(client, label, method, args, should_succeed=True):
    tx = client.write_contract(address=CONTRACT, function_name=method, args=args, value=0)
    print("TX " + label + "=" + str(tx), flush=True)
    receipt = client.wait_for_transaction_receipt(
        tx, status=TransactionStatus.FINALIZED, interval=4000, retries=300,
        full_transaction=True,
    )
    results = execution_results(receipt)
    success = bool(results) and all(result == "SUCCESS" for result in results)
    print("FINAL " + label + "=" + canonical({
        "hash": str(tx), "status": receipt.get("status_name"),
        "result": receipt.get("result_name"), "execution": results,
    }), flush=True)
    checkpoint(success == should_succeed, label + (" succeeds" if should_succeed else " is rejected"))
    return str(tx)


def action(label):
    return "sha256:" + hashlib.sha256(label.encode()).hexdigest()


def main():
    key_a = getpass.getpass("Authority test-wallet private key: ").strip()
    key_b = getpass.getpass("Outsider test-wallet private key: ").strip()
    authority = create_account(key_a)
    outsider = create_account(key_b)
    key_a = key_b = ""
    checkpoint(str(authority.address).lower() == AUTHORITY.lower(), "authority wallet identity")
    checkpoint(str(outsider.address).lower() == OUTSIDER.lower(), "outsider wallet identity")

    a = create_client(chain=studionet, account=authority)
    b = create_client(chain=studionet, account=outsider)
    protocol = read(a, "get_protocol")
    checkpoint(protocol.get("version") == 3, "protocol v3")
    checkpoint(protocol.get("security_profile") == "CANARY_AND_CANONICAL_GROUNDING", "security profile")
    checkpoint(read(a, "get_counts") == {"daos": 0, "proposals": 0, "reviews": 0, "votes": 0}, "fresh deployment")

    txs = {}
    txs["register_dao"] = write(a, "register_dao", "register_dao", [
        AUTHORITY, REPOSITORY, "proposal.json", "affiliations.json", "disclosure.json", POLICY,
    ])
    checkpoint(read(a, "get_dao", [1])["authority"].lower() == AUTHORITY.lower(), "DAO authority bound")

    deadline = int(time.time()) + 7 * 24 * 60 * 60
    clear_action = action("mandate-glass-v3-clear-vote")
    txs["register_clear_proposal"] = write(a, "register_clear_proposal", "register_proposal", [
        1, "DAO-42", CLEAR_COMMIT, clear_action, deadline,
    ])

    before = read(a, "get_counts")
    txs["outsider_create_rejected"] = write(b, "outsider_create_rejected", "create_review", [1, AUTHORITY], False)
    checkpoint(read(a, "get_counts") == before, "outsider cannot impersonate delegate")

    txs["create_clear_review"] = write(a, "create_clear_review", "create_review", [1, AUTHORITY])
    txs["evaluate_clear"] = write(a, "evaluate_clear", "evaluate_review", [1, 1])
    clear = read(a, "get_review", [1])
    checkpoint(clear["state"] == 2 and clear["verdict"] == 1 and clear["match_count"] == 0, "CLEAR verdict grounded")
    checkpoint(str(clear["evidence_digest"]).startswith("sha256:"), "CLEAR evidence digest bound")

    txs["authorize_clear"] = write(a, "authorize_clear", "authorize_result", [1, 1])
    authorized = read(a, "get_review", [1])
    checkpoint(authorized["state"] == 3 and bool(authorized["authorization_scope"]), "scoped authorization issued")

    wrong_action = action("mandate-glass-v3-wrong-action")
    before_review = read(a, "get_review", [1])
    before_counts = read(a, "get_counts")
    txs["wrong_action_rejected"] = write(a, "wrong_action_rejected", "execute_vote", [1, 1, wrong_action, True], False)
    checkpoint(read(a, "get_review", [1]) == before_review and read(a, "get_counts") == before_counts,
               "wrong action leaves authorization and accounting unchanged")

    txs["execute_clear_vote"] = write(a, "execute_clear_vote", "execute_vote", [1, 1, clear_action, True])
    consumed = read(a, "get_review", [1])
    vote = read(a, "get_vote", [1])
    checkpoint(consumed["state"] == 4 and consumed["authorization_consumed"] == 1, "authorization consumed atomically")
    checkpoint(vote["review_id"] == 1 and vote["support"] is True and vote["action_digest"] == clear_action,
               "guarded vote recorded")

    before_counts = read(a, "get_counts")
    txs["replay_rejected"] = write(a, "replay_rejected", "execute_vote", [1, 1, clear_action, True], False)
    checkpoint(read(a, "get_counts") == before_counts, "replay leaves accounting unchanged")

    undisclosed_action = action("mandate-glass-v3-undisclosed-vote")
    txs["register_undisclosed_proposal"] = write(a, "register_undisclosed_proposal", "register_proposal", [
        1, "DAO-42", UNDISCLOSED_COMMIT, undisclosed_action, deadline,
    ])
    txs["create_undisclosed_review"] = write(a, "create_undisclosed_review", "create_review", [2, AUTHORITY])
    txs["evaluate_undisclosed"] = write(a, "evaluate_undisclosed", "evaluate_review", [2, 1])
    undisclosed = read(a, "get_review", [2])
    checkpoint(undisclosed["state"] == 2 and undisclosed["verdict"] == 3 and undisclosed["match_count"] >= 1,
               "UNDISCLOSED_CONFLICT verdict grounded")
    checkpoint(str(undisclosed["evidence_digest"]).startswith("sha256:"), "undisclosed evidence digest bound")

    before_counts = read(a, "get_counts")
    txs["undisclosed_authorize_rejected"] = write(
        a, "undisclosed_authorize_rejected", "authorize_result", [2, 1], False,
    )
    checkpoint(read(a, "get_counts") == before_counts and read(a, "get_review", [2]) == undisclosed,
               "undisclosed conflict cannot authorize or mutate accounting")

    final_counts = read(a, "get_counts")
    checkpoint(final_counts == {"daos": 1, "proposals": 2, "reviews": 2, "votes": 1}, "final v3 counts")
    print("LIFECYCLE_COMPLETE", flush=True)
    print("transactions=" + canonical(txs), flush=True)
    print("final_counts=" + canonical(final_counts), flush=True)


if __name__ == "__main__":
    main()
