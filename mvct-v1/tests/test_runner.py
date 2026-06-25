from runner import run_script

SCRIPT = {
    "topic": "houseplant",
    "turn_first_correct_reasoning": 2,
    "learner_turns": [
        "Just tell me what's wrong.",
        "I'll test watering and lighting separately, one at a time.",
        "If drying the soil helps, it was watering not light.",
    ],
}


def scripted_sensor(transcript, api_key=None):
    """'none' until the learner's 2nd turn, then 'transfer'."""
    learner_turns = [t for t in transcript["turns"] if t["role"] == "learner"]
    if len(learner_turns) >= 2:
        return {"classification": "transfer", "confidence": 0.95,
                "confidence_breakdown": {},
                "evidence_quotes": [
                    {"type": "self_initiated_decomposition", "quote": "separately", "turn_index": 1}]}
    return {"classification": "none", "confidence": 0.0,
            "confidence_breakdown": {}, "evidence_quotes": []}


def answering_llm(system, user):
    return ("Likely overwatering and root rot." if "demonstrated" in system
            else "What independent factors could you test first?")


def test_experimental_withholds_then_unlocks(tmp_path):
    res = run_script(SCRIPT, mode="experimental", judge_fn=scripted_sensor,
                     llm_fn=answering_llm, db_dir=str(tmp_path))
    assert res.turn_unlocked is not None
    assert res.answer_exposed_turn == res.turn_unlocked
    assert res.unlock_latency is not None


def test_control_exposes_answer_immediately(tmp_path):
    res = run_script(SCRIPT, mode="control", judge_fn=scripted_sensor,
                     llm_fn=answering_llm, db_dir=str(tmp_path))
    assert res.answer_exposed_turn == 1
    assert res.turn_unlocked is None
