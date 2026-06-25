from monitor import Monitor


def test_records_and_computes_unlock_latency(tmp_path):
    mon = Monitor(str(tmp_path / "mon.db"))
    sid = mon.start(mode="experimental")
    mon.record_gate(sid, turn=1, classification="none", confidence=0.0,
                    granted=False, reason="locked", latency_ms=12.0)
    mon.record_gate(sid, turn=3, classification="transfer", confidence=0.95,
                    granted=True, reason="unlocked", latency_ms=15.0)
    assert mon.turn_unlocked(sid) == 3
    assert mon.compute_unlock_latency(sid, turn_first_correct_reasoning=3) == 0
    assert mon.compute_unlock_latency(sid, turn_first_correct_reasoning=2) == 1


def test_unlock_latency_none_when_never_unlocked(tmp_path):
    mon = Monitor(str(tmp_path / "m.db"))
    sid = mon.start(mode="experimental")
    mon.record_gate(sid, turn=1, classification="none", confidence=0.0,
                    granted=False, reason="locked", latency_ms=9.0)
    assert mon.turn_unlocked(sid) is None
    assert mon.compute_unlock_latency(sid, turn_first_correct_reasoning=1) is None
