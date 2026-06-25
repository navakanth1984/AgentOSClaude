from auditor import CapabilityAuditor
from policy import STRICT
from permission import verify_token
from sensor import TransferSensor

KEY = b"test-key"


def _judge(classification, confidence):
    return lambda transcript, api_key=None: {
        "classification": classification,
        "confidence": confidence,
        "confidence_breakdown": {},
        "evidence_quotes": [],
    }


def _auditor(judge, policy=STRICT):
    return CapabilityAuditor(TransferSensor(judge_fn=judge), policy, KEY)


def test_transfer_above_floor_mints_valid_token():
    res = _auditor(_judge("transfer", 0.95)).evaluate({"turns": []}, current_turn=2)
    assert res.token is not None
    assert verify_token(KEY, res.token, current_turn=2) is True


def test_below_floor_no_token():
    res = _auditor(_judge("transfer", 0.50)).evaluate({"turns": []}, current_turn=2)
    assert res.token is None
    assert res.classification == "transfer"


def test_non_transfer_no_token():
    res = _auditor(_judge("transitional", 0.99)).evaluate({"turns": []}, current_turn=2)
    assert res.token is None


def test_sensor_failure_fails_closed():
    def boom(transcript, api_key=None):
        raise RuntimeError("sensor down")

    res = _auditor(boom).evaluate({"turns": []}, current_turn=2)
    assert res.token is None
    assert "fail-closed" in res.reason
