from policy import STRICT, RESEARCH, BINARY, satisfies


def test_named_policies():
    assert STRICT.confidence_floor == 0.90
    assert RESEARCH.confidence_floor == 0.65
    assert BINARY.confidence_floor == 0.0
    assert STRICT.classification_required == "transfer"


def test_satisfies_requires_classification_and_floor():
    assert satisfies(STRICT, "transfer", 0.91) is True
    assert satisfies(STRICT, "transfer", 0.89) is False
    assert satisfies(STRICT, "transitional", 0.99) is False
    assert satisfies(BINARY, "transfer", 0.0) is True
