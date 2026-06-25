import json

import pull_labels


def test_keeps_latest_per_rater_transcript(tmp_path):
    src = tmp_path / "labels"
    (src / "expert" / "expert_a").mkdir(parents=True)
    early = {"rater_id": "expert_a", "submitted_at": "2026-06-25T09:00:00Z",
             "payload": {"labels": {"t01": {"classification": "none"}}}}
    late = {"rater_id": "expert_a", "submitted_at": "2026-06-25T10:00:00Z",
            "payload": {"labels": {"t01": {"classification": "transfer"}}}}
    (src / "expert" / "expert_a" / "a.json").write_text(json.dumps(early))
    (src / "expert" / "expert_a" / "b.json").write_text(json.dumps(late))
    dest = tmp_path / "out"
    pull_labels.main(str(src), str(dest))
    got = json.loads((dest / "expert_a" / "t01.json").read_text())
    assert got["classification"] == "transfer"
