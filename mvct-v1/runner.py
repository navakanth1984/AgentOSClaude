"""Scripted control-vs-experimental harness — the part that makes this evidence,
not a demo. Replays one annotated learner script through both arms with identical
inputs; the only difference is whether the constitutional gate is active.

sensor_fn (judge_fn) and llm_fn are injectable so the whole harness runs offline.
"""
import os
import time
from dataclasses import dataclass

import config
from auditor import CapabilityAuditor
from convo import build_transcript, add_turn
from knowledge import HouseplantKnowledgeProvider
from ledger import Ledger
from monitor import Monitor
from sensor import TransferSensor
from socratic import SocraticInterface


@dataclass
class RunResult:
    mode: str
    turn_unlocked: int | None        # reply ordinal at which the answer unlocked
    answer_exposed_turn: int | None  # reply ordinal at which the answer first appeared
    unlock_latency: int | None       # transcript-turn unlock minus annotated correct-reasoning turn
    sair: float


def _answer_visible(text: str, knowledge: HouseplantKnowledgeProvider) -> bool:
    low = text.lower()
    return any(term.lower() in low for term in knowledge.leak_blocklist())


def run_script(script: dict, mode: str, judge_fn=None, llm_fn=None, db_dir: str = ".") -> RunResult:
    assert mode in ("control", "experimental")
    knowledge = HouseplantKnowledgeProvider()
    key = config.gate_key()
    gate_enabled = mode == "experimental"

    sensor = TransferSensor(judge_fn=judge_fn)
    auditor = CapabilityAuditor(sensor, config.DEFAULT_POLICY, key)
    interface = SocraticInterface(knowledge, key, llm_fn=llm_fn, gate_enabled=gate_enabled)
    ledger = Ledger(os.path.join(db_dir, "ledger.db"))
    monitor = Monitor(os.path.join(db_dir, "monitor.db"))
    sid = ledger.start_session(topic=script["topic"], mode=mode)
    rid = monitor.start(mode=mode)

    transcript = build_transcript()
    add_turn(transcript, "ai", knowledge.scenario_prompt())

    answer_exposed_turn: int | None = None
    turn_unlocked: int | None = None
    reply_no = 0

    for learner_text in script["learner_turns"]:
        add_turn(transcript, "learner", learner_text)
        current_turn = len(transcript["turns"]) - 1

        token = None
        classification, confidence, evidence = "none", 0.0, []
        if gate_enabled:
            t0 = time.perf_counter()
            res = auditor.evaluate(transcript, current_turn)
            latency_ms = (time.perf_counter() - t0) * 1000
            token, classification, confidence, evidence = (
                res.token, res.classification, res.confidence, res.evidence)
            monitor.record_gate(rid, current_turn, classification, confidence,
                                granted=token is not None, reason=res.reason, latency_ms=latency_ms)

        ledger.log_turn(sid, "learner", learner_text, classification, confidence,
                        evidence, had_token=token is not None)

        reply = interface.respond(transcript, token, current_turn)
        add_turn(transcript, "ai", reply)
        reply_no += 1
        if answer_exposed_turn is None and _answer_visible(reply, knowledge):
            answer_exposed_turn = reply_no
        if token is not None and turn_unlocked is None:
            turn_unlocked = reply_no

    status = "success" if turn_unlocked is not None else ("control" if mode == "control" else "failure")
    ledger.end_session(sid, status=status)
    unlock_latency = (None if not gate_enabled
                      else monitor.compute_unlock_latency(rid, script["turn_first_correct_reasoning"]))
    return RunResult(mode, turn_unlocked, answer_exposed_turn, unlock_latency, ledger.compute_sair(sid))
