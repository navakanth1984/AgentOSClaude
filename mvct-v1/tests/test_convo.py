from convo import build_transcript, add_turn


def test_build_transcript_has_required_keys():
    t = build_transcript()
    assert set(t.keys()) == {"transcript_id", "scenario", "target_asset", "turns"}
    assert t["scenario"] == "houseplant"
    assert t["target_asset"] == "problem_decomposition"
    assert t["turns"] == []


def test_add_turn_assigns_incrementing_index():
    t = build_transcript()
    add_turn(t, "ai", "Hello")
    add_turn(t, "learner", "Hi")
    assert [x["turn_index"] for x in t["turns"]] == [0, 1]
    assert t["turns"][0] == {"role": "ai", "text": "Hello", "turn_index": 0}
