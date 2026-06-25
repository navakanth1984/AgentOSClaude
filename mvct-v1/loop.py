"""Interactive demo. Run:  GEMINI_API_KEY=... python loop.py
Without a key the detector returns 'none' (stays locked) — expected offline.
"""
import time

import config
from auditor import CapabilityAuditor
from convo import build_transcript, add_turn
from knowledge import HouseplantKnowledgeProvider
from ledger import Ledger
from monitor import Monitor
from sensor import TransferSensor
from socratic import SocraticInterface


def main() -> None:
    knowledge = HouseplantKnowledgeProvider()
    key = config.gate_key()
    auditor = CapabilityAuditor(TransferSensor(), config.DEFAULT_POLICY, key)
    interface = SocraticInterface(knowledge, key)
    ledger = Ledger("ledger.db")
    monitor = Monitor("monitor.db")
    sid = ledger.start_session(topic="houseplant", mode="experimental")
    rid = monitor.start(mode="experimental")

    transcript = build_transcript()
    add_turn(transcript, "ai", knowledge.scenario_prompt())
    print(f"\nTUTOR: {knowledge.scenario_prompt()}\n(type 'quit' to exit)\n")

    while True:
        try:
            user = input("YOU: ").strip()
        except EOFError:
            user = "quit"
        if user.lower() == "quit":
            ledger.end_session(sid, status="failure")
            print("\n[session ended — answer not earned]")
            break

        add_turn(transcript, "learner", user)
        current_turn = len(transcript["turns"]) - 1

        t0 = time.perf_counter()
        res = auditor.evaluate(transcript, current_turn)
        monitor.record_gate(rid, current_turn, res.classification, res.confidence,
                            granted=res.token is not None, reason=res.reason,
                            latency_ms=(time.perf_counter() - t0) * 1000)
        ledger.log_turn(sid, "learner", user, res.classification, res.confidence,
                        res.evidence, had_token=res.token is not None)

        reply = interface.respond(transcript, res.token, current_turn)
        add_turn(transcript, "ai", reply)
        print(f"TUTOR: {reply}  [{res.classification} {res.confidence:.2f}]\n")

        if res.token is not None:
            ledger.end_session(sid, status="success")
            print(f"[answer earned — SAIR={ledger.compute_sair(sid):.2f}]")
            break


if __name__ == "__main__":
    main()
