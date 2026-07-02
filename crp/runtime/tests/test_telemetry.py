import pytest

crp_telemetry = pytest.importorskip("crp_telemetry")


def test_record_drain_roundtrip() -> None:
    t = crp_telemetry.Telemetry(capacity=8)
    assert t.record(kind=1, tensor_id=7, value=0.5) is True
    assert len(t) == 1
    events = t.drain(10)
    assert len(events) == 1
    ts, kind, tensor_id, value = events[0]
    assert ts > 0 and kind == 1 and tensor_id == 7 and value == 0.5


def test_full_buffer_drops_without_raising() -> None:
    t = crp_telemetry.Telemetry(capacity=2)
    assert t.record(kind=1, tensor_id=1, value=0.0)
    assert t.record(kind=2, tensor_id=2, value=0.0)
    assert t.record(kind=3, tensor_id=3, value=0.0) is False
    assert t.dropped() == 1
