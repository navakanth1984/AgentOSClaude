from sensor import TransferSensor, SensorReading


def fake_judge(transcript, api_key=None):
    return {
        "classification": "transfer",
        "confidence": 0.88,
        "confidence_breakdown": {"independent_variable_identification": 0.3},
        "evidence_quotes": [
            {"type": "self_initiated_decomposition", "quote": "x", "turn_index": 1}
        ],
    }


def test_read_normalizes_detector_output():
    r = TransferSensor(judge_fn=fake_judge).read({"turns": []})
    assert isinstance(r, SensorReading)
    assert r.classification == "transfer"
    assert r.confidence == 0.88
    assert r.evidence_quotes[0]["type"] == "self_initiated_decomposition"


def test_read_tolerates_missing_keys():
    r = TransferSensor(judge_fn=lambda t, api_key=None: {}).read({"turns": []})
    assert r.classification == "none"
    assert r.confidence == 0.0
    assert r.evidence_quotes == []
