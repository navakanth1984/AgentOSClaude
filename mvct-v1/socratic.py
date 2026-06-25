"""Socratic Interface: model proposes, Python disposes.

The LLM generates the next tutor turn, but a deterministic guard enforces the
constitutional invariants regardless of what the model says:
  - Invariant 1: no canonical answer tokens while locked (deterministic).
  - Invariant 2: no logically-equivalent complete solution while locked
    (best-effort via the blocklist of canonical variables — see spec section 4).
Unlocking is gated on a verified PermissionToken (Invariant 3 lives in permission.py).
"""
from typing import Callable, Optional

from permission import verify_token, PermissionToken

REFUSAL = (
    "I won't hand you that yet. What independent factors could you test "
    "one at a time, and which would you check first?"
)

LOCKED_SYSTEM = (
    "You are a Socratic tutor for a houseplant-diagnosis problem. "
    "You must NOT state the diagnosis or name the candidate causes (e.g. water, light, "
    "soil, drainage, roots, pests). Do NOT enumerate the factors for the learner — that "
    "robs them of the decomposition. Ask exactly ONE probing question that pushes the "
    "learner to identify independent, separately-testable causes themselves."
)
UNLOCKED_SYSTEM = (
    "The learner has demonstrated genuine problem decomposition. You may now give the "
    "full diagnosis and the reasoning, clearly and concisely."
)


def guard_turn(text: str, token: PermissionToken | None, blocklist: list[str],
               key: bytes, current_turn: int) -> tuple[str, bool]:
    """Returns (safe_text, blocked). While locked (no valid token), any turn containing
    a blocklisted term is replaced wholesale with a Socratic refusal."""
    if verify_token(key, token, current_turn):
        return text, False
    lowered = text.lower()
    if any(term.lower() in lowered for term in blocklist):
        return REFUSAL, True
    return text, False


def _transcript_to_user_msg(transcript: dict) -> str:
    lines = [f'{t["role"]}: {t["text"]}' for t in transcript["turns"]]
    return "Conversation so far:\n" + "\n".join(lines) + "\n\nYour next turn:"


def _default_llm(system: str, user: str) -> str:
    import os
    import google.generativeai as genai  # type: ignore

    genai.configure(api_key=os.environ.get("GEMINI_API_KEY", ""))
    model = genai.GenerativeModel(model_name="gemini-2.5-flash", system_instruction=system)
    resp = model.generate_content(
        user, generation_config=genai.GenerationConfig(temperature=0.3)
    )
    return resp.text.strip()


class SocraticInterface:
    def __init__(self, knowledge, key: bytes,
                 llm_fn: Optional[Callable[[str, str], str]] = None,
                 gate_enabled: bool = True):
        self._k = knowledge
        self._key = key
        self._gate_enabled = gate_enabled
        self._llm: Callable[[str, str], str] = llm_fn or _default_llm

    def respond(self, transcript: dict, token: PermissionToken | None,
                current_turn: int) -> str:
        unlocked = (not self._gate_enabled) or verify_token(self._key, token, current_turn)
        system = UNLOCKED_SYSTEM if unlocked else LOCKED_SYSTEM
        raw = self._llm(system, _transcript_to_user_msg(transcript))
        if not self._gate_enabled:
            return raw  # control arm: ungated
        safe, _ = guard_turn(raw, token, self._k.leak_blocklist(), self._key, current_turn)
        return safe
