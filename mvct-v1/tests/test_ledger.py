from ledger import Ledger


def test_sair_and_session_lifecycle(tmp_path):
    db = str(tmp_path / "ledger.db")
    led = Ledger(db)
    sid = led.start_session(topic="houseplant", mode="experimental")
    led.log_turn(sid, role="learner", text="I'd test light and water separately",
                 classification="transfer", confidence=0.9,
                 evidence=[{"type": "self_initiated_decomposition", "quote": "x", "turn_index": 1}],
                 had_token=False)
    led.log_turn(sid, role="learner", text="I dunno", classification="none",
                 confidence=0.0, evidence=[], had_token=False)
    assert led.compute_sair(sid) == 0.5
    led.end_session(sid, status="success")
    assert led.session_status(sid) == "success"


def test_sair_zero_when_no_learner_turns(tmp_path):
    led = Ledger(str(tmp_path / "l.db"))
    sid = led.start_session(topic="houseplant", mode="control")
    assert led.compute_sair(sid) == 0.0
