"""HMAC-signed capability token. Only a holder of the gate key can mint a token that
verifies; every other module can only verify one. This structurally enforces
Invariant 3: the unlock decision can originate only from the Capability Auditor.
"""
import hmac
import hashlib
import time
from dataclasses import dataclass


@dataclass(frozen=True)
class PermissionToken:
    issued_by: str
    timestamp: float
    classification: str
    confidence: float
    expires_at_turn: int
    signature: str


def _payload(issued_by: str, timestamp: float, classification: str,
             confidence: float, expires_at_turn: int) -> bytes:
    return f"{issued_by}|{timestamp}|{classification}|{confidence:.6f}|{expires_at_turn}".encode()


def mint_token(key: bytes, *, classification: str, confidence: float,
               current_turn: int, ttl_turns: int = 0,
               issuer: str = "CapabilityAuditor") -> PermissionToken:
    ts = time.time()
    expires = current_turn + ttl_turns
    sig = hmac.new(
        key, _payload(issuer, ts, classification, confidence, expires), hashlib.sha256
    ).hexdigest()
    return PermissionToken(issuer, ts, classification, confidence, expires, sig)


def verify_token(key: bytes, token: PermissionToken | None, current_turn: int) -> bool:
    if token is None:
        return False
    expected = hmac.new(
        key,
        _payload(token.issued_by, token.timestamp, token.classification,
                 token.confidence, token.expires_at_turn),
        hashlib.sha256,
    ).hexdigest()
    if not hmac.compare_digest(expected, token.signature):
        return False
    return current_turn <= token.expires_at_turn
