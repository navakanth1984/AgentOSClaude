"""Internalization Ledger — pedagogical history (distinct from the runtime Monitor).
Stdlib sqlite3, zero extra deps. Computes SAIR (Self-Initiated Asset Invocation Rate).
"""
import sqlite3
import json
import time


class Ledger:
    def __init__(self, db_path: str):
        self._db = sqlite3.connect(db_path)
        self._db.execute(
            """CREATE TABLE IF NOT EXISTS sessions(
                id INTEGER PRIMARY KEY AUTOINCREMENT, topic TEXT, mode TEXT,
                status TEXT DEFAULT 'open', started REAL)"""
        )
        self._db.execute(
            """CREATE TABLE IF NOT EXISTS turns(
                id INTEGER PRIMARY KEY AUTOINCREMENT, session_id INTEGER, role TEXT,
                text TEXT, classification TEXT, confidence REAL, evidence TEXT,
                had_token INTEGER)"""
        )
        self._db.commit()

    def start_session(self, topic: str, mode: str) -> int:
        cur = self._db.execute(
            "INSERT INTO sessions(topic,mode,started) VALUES(?,?,?)",
            (topic, mode, time.time()),
        )
        self._db.commit()
        assert cur.lastrowid is not None
        return cur.lastrowid

    def log_turn(self, session_id: int, role: str, text: str, classification: str,
                 confidence: float, evidence: list, had_token: bool) -> None:
        self._db.execute(
            "INSERT INTO turns(session_id,role,text,classification,confidence,evidence,had_token)"
            " VALUES(?,?,?,?,?,?,?)",
            (session_id, role, text, classification, confidence,
             json.dumps(evidence), 1 if had_token else 0),
        )
        self._db.commit()

    def compute_sair(self, session_id: int) -> float:
        rows = self._db.execute(
            "SELECT evidence FROM turns WHERE session_id=? AND role='learner'",
            (session_id,),
        ).fetchall()
        if not rows:
            return 0.0
        self_init = sum(
            1 for (ev,) in rows
            if any(q.get("type") == "self_initiated_decomposition" for q in json.loads(ev))
        )
        return self_init / len(rows)

    def end_session(self, session_id: int, status: str) -> None:
        self._db.execute("UPDATE sessions SET status=? WHERE id=?", (status, session_id))
        self._db.commit()

    def session_status(self, session_id: int) -> str:
        row = self._db.execute(
            "SELECT status FROM sessions WHERE id=?", (session_id,)
        ).fetchone()
        return row[0] if row else "unknown"
