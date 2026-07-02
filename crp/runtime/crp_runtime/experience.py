"""Relational SQLite Experience Database (ADR-002, spec 5.4).

Every harness decision is stored with its full inputs (spec, constraints,
profile) and outputs (decision, scores, rejections, telemetry events) so a
run can be replayed and compared byte-for-byte. Serialization is canonical
(sorted keys) to keep replay comparison deterministic (R-004). Event streams
are evidence: stored verbatim, never normalized.
"""

from __future__ import annotations

import json
import sqlite3
import subprocess
import time
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any

from crp_runtime.harness import RunRecord
from crp_runtime.policy import Constraints, Profile

SCHEMA_VERSION = 1

_SCHEMA = """
CREATE TABLE IF NOT EXISTS runs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    recorded_at TEXT NOT NULL,
    spec_json TEXT NOT NULL,
    constraints_json TEXT NOT NULL,
    profile_json TEXT NOT NULL,
    chosen TEXT NOT NULL,
    decision_latency_ms REAL NOT NULL,
    dropped INTEGER NOT NULL,
    git_commit TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS scores (
    run_id INTEGER NOT NULL REFERENCES runs(id),
    plugin TEXT NOT NULL,
    score REAL NOT NULL
);
CREATE TABLE IF NOT EXISTS rejections (
    run_id INTEGER NOT NULL REFERENCES runs(id),
    plugin TEXT NOT NULL,
    reason TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS events (
    run_id INTEGER NOT NULL REFERENCES runs(id),
    seq INTEGER NOT NULL,
    timestamp_ns INTEGER NOT NULL,
    kind INTEGER NOT NULL,
    tensor_id INTEGER NOT NULL,
    value REAL NOT NULL
);
"""


def canonical_json(payload: dict[str, Any]) -> str:
    return json.dumps(payload, sort_keys=True, separators=(",", ":"))


def _git_commit() -> str:
    try:
        return subprocess.run(
            ["git", "rev-parse", "HEAD"],
            capture_output=True,
            text=True,
            check=True,
            cwd=Path(__file__).resolve().parent,
        ).stdout.strip()
    except (subprocess.CalledProcessError, FileNotFoundError):
        return "unknown"


@dataclass(frozen=True)
class StoredRun:
    run_id: int
    spec_json: str
    constraints: Constraints
    profile: Profile
    chosen: str
    decision_latency_ms: float
    dropped: int
    git_commit: str
    scores: dict[str, float] = field(default_factory=dict)
    rejections: dict[str, str] = field(default_factory=dict)
    events: list[tuple[int, int, int, float]] = field(default_factory=list)


class ExperienceDB:
    def __init__(self, path: str | Path) -> None:
        self._conn = sqlite3.connect(str(path))
        self._conn.executescript(_SCHEMA)
        self._conn.execute(f"PRAGMA user_version = {SCHEMA_VERSION}")
        self._conn.commit()

    @property
    def schema_version(self) -> int:
        row = self._conn.execute("PRAGMA user_version").fetchone()
        return int(row[0])

    def insert_run(
        self, record: RunRecord, constraints: Constraints, profile: Profile
    ) -> int:
        cur = self._conn.execute(
            "INSERT INTO runs (recorded_at, spec_json, constraints_json, profile_json,"
            " chosen, decision_latency_ms, dropped, git_commit)"
            " VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
            (
                time.strftime("%Y-%m-%dT%H:%M:%S%z"),
                record.spec_json,
                canonical_json(asdict(constraints)),
                canonical_json(asdict(profile)),
                record.decision.chosen,
                record.decision.decision_latency_ms,
                record.dropped,
                _git_commit(),
            ),
        )
        run_id = cur.lastrowid
        assert run_id is not None
        self._conn.executemany(
            "INSERT INTO scores (run_id, plugin, score) VALUES (?, ?, ?)",
            [(run_id, name, score) for name, score in record.decision.scores.items()],
        )
        self._conn.executemany(
            "INSERT INTO rejections (run_id, plugin, reason) VALUES (?, ?, ?)",
            [(run_id, name, why) for name, why in record.decision.rejected.items()],
        )
        self._conn.executemany(
            "INSERT INTO events (run_id, seq, timestamp_ns, kind, tensor_id, value)"
            " VALUES (?, ?, ?, ?, ?, ?)",
            [(run_id, seq, *event) for seq, event in enumerate(record.events)],
        )
        self._conn.commit()
        return run_id

    def get_run(self, run_id: int) -> StoredRun:
        row = self._conn.execute(
            "SELECT spec_json, constraints_json, profile_json, chosen,"
            " decision_latency_ms, dropped, git_commit FROM runs WHERE id = ?",
            (run_id,),
        ).fetchone()
        if row is None:
            raise KeyError(f"run {run_id} not found")
        scores = {
            name: score
            for name, score in self._conn.execute(
                "SELECT plugin, score FROM scores WHERE run_id = ?", (run_id,)
            )
        }
        rejections = {
            name: why
            for name, why in self._conn.execute(
                "SELECT plugin, reason FROM rejections WHERE run_id = ?", (run_id,)
            )
        }
        events = [
            (int(ts), int(kind), int(tid), float(value))
            for ts, kind, tid, value in self._conn.execute(
                "SELECT timestamp_ns, kind, tensor_id, value FROM events"
                " WHERE run_id = ? ORDER BY seq",
                (run_id,),
            )
        ]
        return StoredRun(
            run_id=run_id,
            spec_json=row[0],
            constraints=Constraints(**json.loads(row[1])),
            profile=Profile(**json.loads(row[2])),
            chosen=row[3],
            decision_latency_ms=row[4],
            dropped=row[5],
            git_commit=row[6],
            scores=scores,
            rejections=rejections,
            events=events,
        )

    def runs(self) -> list[int]:
        return [r[0] for r in self._conn.execute("SELECT id FROM runs ORDER BY id")]

    def close(self) -> None:
        self._conn.close()
