#!/usr/bin/env python3
"""Pull collected labels from a tdh-labels checkout into the detector eval dirs.

Keeps the latest submission per (rater_id, transcript_id).

Usage: python pull_labels.py <tdh-labels-checkout> <dest data/labels dir>
"""
import json
import sys
from pathlib import Path


def main(labels_root: str, dest_root: str) -> None:
    src = Path(labels_root) / "expert"
    dest = Path(dest_root)
    latest: dict[tuple[str, str], tuple[str, dict]] = {}
    for f in sorted(src.glob("*/*.json")):
        rec = json.loads(f.read_text(encoding="utf-8"))
        rater = rec.get("rater_id", f.parent.name)
        ts = rec.get("submitted_at", f.stem)
        for tid, label in rec.get("payload", {}).get("labels", {}).items():
            key = (rater, tid)
            if key not in latest or ts > latest[key][0]:
                latest[key] = (ts, label)
    for (rater, tid), (_ts, label) in latest.items():
        out = dest / rater
        out.mkdir(parents=True, exist_ok=True)
        (out / f"{tid}.json").write_text(json.dumps(label, indent=2), encoding="utf-8")
    print(f"wrote {len(latest)} label files under {dest}")


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("usage: pull_labels.py <tdh-labels-checkout> <dest data/labels dir>")
        sys.exit(1)
    main(sys.argv[1], sys.argv[2])
