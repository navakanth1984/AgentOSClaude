"""Metrics Monitor — runtime behavior (distinct from the pedagogical Ledger).
Records every gate evaluation and computes Unlock Latency.

Unlock Latency = turn_unlocked - turn_first_correct_reasoning (script annotation).
Ideal 0; positive = the gate hesitated; negative = it unlocked early (a safety failure).
"""
import sqlite3
import time


class Monitor:
    def __init__(self, db_path: str):
        self._db = sqlite3.connect(db_path)
        self._db.execute(
            """CREATE TABLE IF NOT EXISTS runs(
                id INTEGER PRIMARY KEY AUTOINCREMENT, mode TEXT, started REAL)"""
        )
        self._db.execute(
            """CREATE TABLE IF NOT EXISTS gate_evals(
                id INTEGER PRIMARY KEY AUTOINCREMENT, run_id INTEGER, turn INTEGER,
                classification TEXT, confidence REAL, granted INTEGER, reason TEXT,
                latency_ms REAL)"""
        )
        self._db.commit()

    def start(self, mode: str) -> int:
        cur = self._db.execute("INSERT INTO runs(mode,started) VALUES(?,?)", (mode, time.time()))
        self._db.commit()
        assert cur.lastrowid is not None
        return cur.lastrowid

    def record_gate(self, run_id: int, turn: int, classification: str, confidence: float,
                    granted: bool, reason: str, latency_ms: float) -> None:
        self._db.execute(
            "INSERT INTO gate_evals(run_id,turn,classification,confidence,granted,reason,latency_ms)"
            " VALUES(?,?,?,?,?,?,?)",
            (run_id, turn, classification, confidence, 1 if granted else 0, reason, latency_ms),
        )
        self._db.commit()

    def turn_unlocked(self, run_id: int) -> int | None:
        row = self._db.execute(
            "SELECT MIN(turn) FROM gate_evals WHERE run_id=? AND granted=1", (run_id,)
        ).fetchone()
        return row[0] if row else None

    def compute_unlock_latency(self, run_id: int, turn_first_correct_reasoning: int) -> int | None:
        unlocked = self.turn_unlocked(run_id)
        if unlocked is None:
            return None
        return unlocked - turn_first_correct_reasoning
