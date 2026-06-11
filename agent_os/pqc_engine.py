"""
pqc_engine.py — Post-Quantum Cryptography for Agent OS
=======================================================
Wraps three NIST-standardized algorithms:

  ML-KEM-768  (Kyber)     → key encapsulation  (replaces RSA/ECDH)
  ML-DSA-65   (Dilithium) → digital signatures  (replaces RSA/ECDSA)
  AES-256-GCM             → symmetric encryption (unchanged, quantum-safe)

Flow for encrypting data:
  1. Kyber.keygen()            → (public_key, secret_key)
  2. Kyber.encaps(public_key)  → (shared_secret, kem_ciphertext)
  3. AES-GCM.encrypt(shared_secret, plaintext) → ciphertext
  4. Store: kem_ciphertext + aes_ciphertext

Flow for decrypting:
  1. Kyber.decaps(secret_key, kem_ciphertext) → shared_secret
  2. AES-GCM.decrypt(shared_secret, aes_ciphertext) → plaintext

Cost: $0. Runs on your CPU. ~3-23ms per operation.
"""

import os
import json
import base64
import hashlib
import logging
from datetime import datetime, timezone
from pathlib import Path

from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from kyber_py.ml_kem import ML_KEM_768
from dilithium_py.ml_dsa import ML_DSA_65

# ── Key storage ──────────────────────────────────────────────────────────────
_KEY_DIR  = Path(__file__).parent / "pqc_keys"
_KEM_PUB  = _KEY_DIR / "kem_public.bin"
_KEM_SEC  = _KEY_DIR / "kem_secret.bin"
_DSA_PUB  = _KEY_DIR / "dsa_public.bin"
_DSA_SEC  = _KEY_DIR / "dsa_secret.bin"
_LOG_FILE = Path(__file__).parent / "pqc_log.json"

logger = logging.getLogger(__name__)


class PQCEngine:
    """
    Thin wrapper around ML-KEM-768, ML-DSA-65, and AES-256-GCM.
    Keys are generated once and persisted to pqc_keys/.
    Every operation is logged to pqc_log.json.

    Keys are cached in memory after first load — eliminates repeated disk I/O
    on every sign/encrypt/verify call (was 100 disk reads per 100 signs).
    """

    # Class-level key cache — shared across all instances in the same process
    _dsa_sk: bytes | None = None
    _dsa_pk: bytes | None = None
    _kem_pk: bytes | None = None
    _kem_sk: bytes | None = None

    def __init__(self, auto_keygen: bool = True):
        _KEY_DIR.mkdir(exist_ok=True)
        if auto_keygen and not self._keys_exist():
            self.keygen()
        self._load_keys_to_cache()

    def _load_keys_to_cache(self):
        """Load keys from disk into class-level cache if not already loaded."""
        if PQCEngine._dsa_sk is None and _DSA_SEC.exists():
            PQCEngine._dsa_sk = _DSA_SEC.read_bytes()
        if PQCEngine._dsa_pk is None and _DSA_PUB.exists():
            PQCEngine._dsa_pk = _DSA_PUB.read_bytes()
        if PQCEngine._kem_pk is None and _KEM_PUB.exists():
            PQCEngine._kem_pk = _KEM_PUB.read_bytes()
        if PQCEngine._kem_sk is None and _KEM_SEC.exists():
            PQCEngine._kem_sk = _KEM_SEC.read_bytes()

    # ── Public API ────────────────────────────────────────────────────────────

    def keygen(self) -> dict:
        """
        Generate fresh ML-KEM + ML-DSA keypairs and save to disk.
        Call once; keys persist across restarts.
        """
        kem_pk, kem_sk = ML_KEM_768.keygen()
        dsa_pk, dsa_sk = ML_DSA_65.keygen()

        _KEM_PUB.write_bytes(kem_pk)
        _KEM_SEC.write_bytes(kem_sk)
        _DSA_PUB.write_bytes(dsa_pk)
        _DSA_SEC.write_bytes(dsa_sk)

        result = {
            "action":       "keygen",
            "kem_pub_size": len(kem_pk),   # 1184 bytes
            "dsa_pub_size": len(dsa_pk),   # 1952 bytes
            "timestamp":    _now(),
            "status":       "ok",
        }
        self._log(result)
        return result

    def encrypt(self, plaintext: str | bytes) -> dict:
        """
        Encrypt plaintext using ML-KEM + AES-256-GCM.
        Returns a dict with all parts needed for decryption.
        Caller keeps the secret key (stored in pqc_keys/kem_secret.bin).
        """
        if isinstance(plaintext, str):
            plaintext = plaintext.encode()

        kem_pk = PQCEngine._kem_pk or _KEM_PUB.read_bytes()

        # Step 1: Kyber encapsulation → shared secret
        shared_secret, kem_ct = ML_KEM_768.encaps(kem_pk)

        # Step 2: AES-256-GCM encryption using shared secret as key
        nonce       = os.urandom(12)                    # 96-bit nonce
        aes_key     = shared_secret[:32]                # 256-bit AES key
        aes_ct      = AESGCM(aes_key).encrypt(nonce, plaintext, None)

        result = {
            "action":       "encrypt",
            "kem_ct":       _b64(kem_ct),               # send to recipient
            "aes_ct":       _b64(aes_ct),               # encrypted data
            "nonce":        _b64(nonce),                 # IV for AES
            "plaintext_len": len(plaintext),
            "timestamp":    _now(),
            "algorithm":    "ML-KEM-768 + AES-256-GCM",
        }
        self._log({k: v for k, v in result.items() if k not in ("kem_ct", "aes_ct", "nonce")})
        return result

    def decrypt(self, kem_ct_b64: str, aes_ct_b64: str, nonce_b64: str) -> dict:
        """
        Decrypt using secret key on disk.
        Raises ValueError if tampered.
        """
        kem_sk  = _KEM_SEC.read_bytes()
        kem_ct  = base64.b64decode(kem_ct_b64)
        aes_ct  = base64.b64decode(aes_ct_b64)
        nonce   = base64.b64decode(nonce_b64)

        # Step 1: Kyber decapsulation → recover shared secret
        shared_secret = ML_KEM_768.decaps(kem_sk, kem_ct)

        # Step 2: AES-256-GCM decryption (raises InvalidTag if tampered)
        aes_key   = shared_secret[:32]
        plaintext = AESGCM(aes_key).decrypt(nonce, aes_ct, None)

        result = {
            "action":    "decrypt",
            "plaintext": plaintext.decode(errors="replace"),
            "timestamp": _now(),
            "status":    "ok",
        }
        self._log({"action": "decrypt", "timestamp": _now(), "status": "ok"})
        return result

    def sign(self, message: str | bytes) -> dict:
        """
        Sign a message with ML-DSA-65 (Dilithium).
        Returns the signature as base64.
        """
        if isinstance(message, str):
            message = message.encode()

        dsa_sk  = PQCEngine._dsa_sk or _DSA_SEC.read_bytes()
        sig     = ML_DSA_65.sign(dsa_sk, message)
        msg_hash = hashlib.sha256(message).hexdigest()[:16]

        result = {
            "action":    "sign",
            "signature": _b64(sig),
            "sig_size":  len(sig),           # 3309 bytes
            "msg_hash":  msg_hash,
            "timestamp": _now(),
            "algorithm": "ML-DSA-65 (Dilithium-3)",
        }
        self._log({k: v for k, v in result.items() if k != "signature"})
        return result

    def verify(self, message: str | bytes, signature_b64: str,
               public_key_b64: str | None = None) -> dict:
        """
        Verify a Dilithium signature.
        Uses stored public key if public_key_b64 is None.
        """
        if isinstance(message, str):
            message = message.encode()

        if public_key_b64:
            dsa_pk = base64.b64decode(public_key_b64)
        else:
            dsa_pk = PQCEngine._dsa_pk or _DSA_PUB.read_bytes()

        sig   = base64.b64decode(signature_b64)
        valid = ML_DSA_65.verify(dsa_pk, message, sig)

        result = {
            "action":    "verify",
            "valid":     valid,
            "msg_hash":  hashlib.sha256(message).hexdigest()[:16],
            "timestamp": _now(),
        }
        self._log(result)
        return result

    def status(self) -> dict:
        """Return current key status — no secrets exposed."""
        return {
            "keys_exist":    self._keys_exist(),
            "kem_pub_size":  len(_KEM_PUB.read_bytes()) if _KEM_PUB.exists() else 0,
            "dsa_pub_size":  len(_DSA_PUB.read_bytes()) if _DSA_PUB.exists() else 0,
            "key_dir":       str(_KEY_DIR),
            "algorithm_kem": "ML-KEM-768 (Kyber-768) — NIST FIPS 203",
            "algorithm_sig": "ML-DSA-65 (Dilithium-3) — NIST FIPS 204",
            "quantum_safe":  True,
            "cost":          "$0.00 — runs on CPU",
        }

    def get_log(self, n: int = 20) -> list:
        """Return last n PQC operation log entries."""
        if not _LOG_FILE.exists():
            return []
        try:
            entries = json.loads(_LOG_FILE.read_text(encoding="utf-8"))
            return entries[-n:]
        except Exception:
            return []

    def public_keys(self) -> dict:
        """Return public keys as base64 — safe to share."""
        return {
            "kem_public_key": _b64(_KEM_PUB.read_bytes()) if _KEM_PUB.exists() else None,
            "dsa_public_key": _b64(_DSA_PUB.read_bytes()) if _DSA_PUB.exists() else None,
        }

    # ── Private helpers ──────────────────────────────────────────────────────

    def _keys_exist(self) -> bool:
        return all(p.exists() for p in [_KEM_PUB, _KEM_SEC, _DSA_PUB, _DSA_SEC])

    def _log(self, entry: dict) -> None:
        entries = []
        if _LOG_FILE.exists():
            try:
                entries = json.loads(_LOG_FILE.read_text(encoding="utf-8"))
            except Exception:
                entries = []
        entries.append(entry)
        entries = entries[-500:]   # keep last 500 entries
        _LOG_FILE.write_text(json.dumps(entries, indent=2), encoding="utf-8")


# ── Utilities ────────────────────────────────────────────────────────────────

def _b64(data: bytes) -> str:
    return base64.b64encode(data).decode()

def _now() -> str:
    return datetime.now(timezone.utc).isoformat()
