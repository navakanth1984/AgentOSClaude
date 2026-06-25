"""Builds transcript dicts that conform to transfer-detector-v0's transcript.schema.json.

The schema is strict (additionalProperties: false) — the dict must contain exactly
transcript_id, scenario, target_asset, turns. Do not add keys.
"""


def build_transcript(transcript_id: str = "t01", scenario: str = "houseplant") -> dict:
    return {
        "transcript_id": transcript_id,
        "scenario": scenario,
        "target_asset": "problem_decomposition",
        "turns": [],
    }


def add_turn(transcript: dict, role: str, text: str) -> dict:
    assert role in ("ai", "learner"), f"bad role: {role}"
    transcript["turns"].append(
        {"role": role, "text": text, "turn_index": len(transcript["turns"])}
    )
    return transcript
