"""
test_pqc_engine.py — Locked eval for PQCEngine
================================================
This file defines what SUCCESS means. Do not modify the assertions.
Follows the agentic-engineering principle: prepare.py is the locked oracle.

All 4 operations must pass:
  1. keygen   — produces keys of correct size
  2. encrypt  — produces non-empty ciphertext
  3. decrypt  — roundtrip recovers exact plaintext
  4. sign+verify — valid signature returns True; tampered message returns False
"""
import sys, os
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
sys.path.insert(0, os.path.dirname(__file__))
os.chdir(os.path.dirname(__file__))

from pqc_engine import PQCEngine
import time

PASS = 0
FAIL = 0

def check(name, condition, detail=""):
    global PASS, FAIL
    if condition:
        print(f"  [PASS] {name}")
        PASS += 1
    else:
        print(f"  [FAIL] {name}  {detail}")
        FAIL += 1

print("=" * 55)
print("PQCEngine — Locked Eval")
print("=" * 55)

engine = PQCEngine(auto_keygen=False)

# ── 1. Key generation ─────────────────────────────────────────────────────────
print("\n[ 1. keygen ]")
t0 = time.perf_counter()
kg = engine.keygen()
t_kg = (time.perf_counter() - t0) * 1000

check("status ok",         kg["status"] == "ok")
check("kem_pub 1184 bytes", kg["kem_pub_size"] == 1184)
check("dsa_pub 1952 bytes", kg["dsa_pub_size"] == 1952)
check("keygen < 50ms",      t_kg < 50, f"took {t_kg:.1f}ms")

# ── 2. Encrypt ────────────────────────────────────────────────────────────────
print("\n[ 2. encrypt ]")
plaintext = "Agent OS secret: quantum seed 2026-06-08"
t0 = time.perf_counter()
enc = engine.encrypt(plaintext)
t_enc = (time.perf_counter() - t0) * 1000

check("kem_ct present",    bool(enc.get("kem_ct")))
check("aes_ct present",    bool(enc.get("aes_ct")))
check("nonce present",     bool(enc.get("nonce")))
check("correct algorithm", "ML-KEM-768" in enc.get("algorithm", ""))
check("encrypt < 60ms",    t_enc < 60, f"took {t_enc:.1f}ms")

# ── 3. Decrypt roundtrip ──────────────────────────────────────────────────────
print("\n[ 3. decrypt roundtrip ]")
t0 = time.perf_counter()
dec = engine.decrypt(enc["kem_ct"], enc["aes_ct"], enc["nonce"])
t_dec = (time.perf_counter() - t0) * 1000

check("status ok",          dec["status"] == "ok")
check("plaintext recovered", dec["plaintext"] == plaintext)
check("decrypt < 30ms",     t_dec < 30, f"took {t_dec:.1f}ms")

# ── 3b. Tamper detection ──────────────────────────────────────────────────────
print("\n[ 3b. tamper detection ]")
import base64
# Flip one byte in the aes_ct
aes_bytes = bytearray(base64.b64decode(enc["aes_ct"]))
aes_bytes[0] ^= 0xFF
tampered_ct = base64.b64encode(bytes(aes_bytes)).decode()
try:
    engine.decrypt(enc["kem_ct"], tampered_ct, enc["nonce"])
    check("tampered ciphertext rejected", False, "should have raised")
except Exception:
    check("tampered ciphertext rejected", True)

# ── 4. Sign + verify ──────────────────────────────────────────────────────────
print("\n[ 4. sign + verify ]")
message = "Navakanth Agent OS API call 2026-06-08"

t0 = time.perf_counter()
signed = engine.sign(message)
t_sign = (time.perf_counter() - t0) * 1000

check("signature present",   bool(signed.get("signature")))
check("sig size 3309 bytes", signed["sig_size"] == 3309)
check("sign < 100ms",        t_sign < 100, f"took {t_sign:.1f}ms")

t0 = time.perf_counter()
v_ok = engine.verify(message, signed["signature"])
t_verify = (time.perf_counter() - t0) * 1000

check("valid=True for correct",  v_ok["valid"] is True)
check("verify < 50ms",           t_verify < 50, f"took {t_verify:.1f}ms")

# Tampered message must fail
v_bad = engine.verify("TAMPERED " + message, signed["signature"])
check("valid=False for tampered", v_bad["valid"] is False)

# ── 5. Status ─────────────────────────────────────────────────────────────────
print("\n[ 5. status ]")
s = engine.status()
check("keys_exist=True",   s["keys_exist"] is True)
check("quantum_safe=True", s["quantum_safe"] is True)
check("cost=$0.00",        s["cost"] == "$0.00 — runs on CPU")

# ── Summary ───────────────────────────────────────────────────────────────────
print()
print("=" * 55)
total = PASS + FAIL
print(f"  Result: {PASS}/{total} passed", "ALL OK" if FAIL == 0 else f"  {FAIL} FAILED")
print(f"  Timings: keygen={t_kg:.1f}ms  encrypt={t_enc:.1f}ms"
      f"  decrypt={t_dec:.1f}ms  sign={t_sign:.1f}ms  verify={t_verify:.1f}ms")
print("=" * 55)

sys.exit(0 if FAIL == 0 else 1)
