"""
stress_pqc.py — PQC Engine Stress Tests
=========================================
Three axes:
  Axis 1 — Throughput   : ops/sec for keygen, encrypt, decrypt, sign, verify
  Axis 2 — Scale        : payload sizes 1B → 10MB, verify correctness + timing
  Axis 3 — Sustained    : 100 consecutive encrypt/decrypt cycles, detect degradation

Locked success criteria (do not modify):
  - Throughput encrypt > 5 ops/sec
  - Throughput verify  > 10 ops/sec
  - All payload sizes decrypt correctly (byte-perfect)
  - Sustained: last-10 avg within 2× of first-10 avg (no runaway slowdown)
"""

import sys, os, time, statistics, tracemalloc
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
sys.path.insert(0, os.path.dirname(__file__))
os.chdir(os.path.dirname(__file__))

from pqc_engine import PQCEngine

e = PQCEngine()
PASS = 0
FAIL = 0

def check(name, condition, detail=""):
    global PASS, FAIL
    symbol = "[PASS]" if condition else "[FAIL]"
    print(f"  {symbol} {name}" + (f"  ({detail})" if detail else ""))
    if condition:
        PASS += 1
    else:
        FAIL += 1

def hbar(label, value, max_val, width=30, unit=""):
    filled = int(width * min(value / max_val, 1.0))
    bar = "#" * filled + "-" * (width - filled)
    print(f"  {label:<18} [{bar}] {value:.1f}{unit}")

# ═══════════════════════════════════════════════════════════
print("=" * 60)
print("AXIS 1 — THROUGHPUT (ops/sec)")
print("=" * 60)

REPS = 10  # enough for stable average; keygen is slowest

# --- keygen ---
print(f"\n  keygen x{REPS}...")
times = []
for _ in range(REPS):
    t0 = time.perf_counter()
    e.keygen()
    times.append((time.perf_counter() - t0) * 1000)
kg_avg = statistics.mean(times)
kg_ops = 1000 / kg_avg
print(f"  avg={kg_avg:.1f}ms   {kg_ops:.1f} ops/sec")
hbar("keygen", kg_ops, 100, unit=" ops/s")
check("keygen > 1 ops/sec", kg_ops > 1, f"{kg_ops:.1f} ops/s")

# shared plaintext for remaining tests
PLAINTEXT = "Agent OS PQC stress test — quantum-safe encryption benchmark 2026"

# --- encrypt ---
print(f"\n  encrypt x{REPS}...")
times = []
enc_result = None
for _ in range(REPS):
    t0 = time.perf_counter()
    enc_result = e.encrypt(PLAINTEXT)
    times.append((time.perf_counter() - t0) * 1000)
enc_avg = statistics.mean(times)
enc_ops = 1000 / enc_avg
print(f"  avg={enc_avg:.1f}ms   {enc_ops:.1f} ops/sec")
hbar("encrypt", enc_ops, 100, unit=" ops/s")
check("encrypt > 5 ops/sec", enc_ops > 5, f"{enc_ops:.1f} ops/s")

# --- decrypt ---
print(f"\n  decrypt x{REPS}...")
times = []
for _ in range(REPS):
    t0 = time.perf_counter()
    dec = e.decrypt(enc_result["kem_ct"], enc_result["aes_ct"], enc_result["nonce"])
    times.append((time.perf_counter() - t0) * 1000)
dec_avg = statistics.mean(times)
dec_ops = 1000 / dec_avg
print(f"  avg={dec_avg:.1f}ms   {dec_ops:.1f} ops/sec")
hbar("decrypt", dec_ops, 100, unit=" ops/s")
check("decrypt > 5 ops/sec",  dec_ops > 5, f"{dec_ops:.1f} ops/s")
check("decrypt roundtrip OK", dec["plaintext"] == PLAINTEXT)

# --- sign ---
print(f"\n  sign x{REPS}...")
times = []
sig_result = None
for _ in range(REPS):
    t0 = time.perf_counter()
    sig_result = e.sign(PLAINTEXT)
    times.append((time.perf_counter() - t0) * 1000)
sign_avg = statistics.mean(times)
sign_ops = 1000 / sign_avg
print(f"  avg={sign_avg:.1f}ms   {sign_ops:.1f} ops/sec")
hbar("sign", sign_ops, 100, unit=" ops/s")
check("sign > 5 ops/sec", sign_ops > 5, f"{sign_ops:.1f} ops/s")

# --- verify ---
print(f"\n  verify x{REPS}...")
times = []
for _ in range(REPS):
    t0 = time.perf_counter()
    v = e.verify(PLAINTEXT, sig_result["signature"])
    times.append((time.perf_counter() - t0) * 1000)
ver_avg = statistics.mean(times)
ver_ops = 1000 / ver_avg
print(f"  avg={ver_avg:.1f}ms   {ver_ops:.1f} ops/sec")
hbar("verify", ver_ops, 100, unit=" ops/s")
check("verify > 10 ops/sec", ver_ops > 10, f"{ver_ops:.1f} ops/s")
check("verify correct",      v["valid"] is True)


# ═══════════════════════════════════════════════════════════
print()
print("=" * 60)
print("AXIS 2 — PAYLOAD SCALE (1 B → 10 MB)")
print("=" * 60)

SIZES = [
    (1,           "1 B"),
    (1_000,       "1 KB"),
    (10_000,      "10 KB"),
    (100_000,     "100 KB"),
    (1_000_000,   "1 MB"),
    (5_000_000,   "5 MB"),
    (10_000_000,  "10 MB"),
]

print(f"\n  {'Size':<10} {'Enc ms':>8} {'Dec ms':>8} {'Correct':>8}")
print(f"  {'-'*10} {'-'*8} {'-'*8} {'-'*8}")

all_correct = True
for size, label in SIZES:
    payload = b"Q" * size

    t0 = time.perf_counter()
    enc = e.encrypt(payload)
    t_enc = (time.perf_counter() - t0) * 1000

    t0 = time.perf_counter()
    dec = e.decrypt(enc["kem_ct"], enc["aes_ct"], enc["nonce"])
    t_dec = (time.perf_counter() - t0) * 1000

    # byte-perfect check
    correct = dec["plaintext"].encode(errors="replace") == payload or \
              dec["plaintext"] == payload.decode(errors="replace")
    if not correct:
        all_correct = False

    flag = "OK" if correct else "FAIL"
    print(f"  {label:<10} {t_enc:>7.1f}ms {t_dec:>7.1f}ms {flag:>8}")

check("all payloads decrypt correctly", all_correct)


# ═══════════════════════════════════════════════════════════
print()
print("=" * 60)
print("AXIS 3 — SUSTAINED LOAD (100 encrypt+decrypt cycles)")
print("=" * 60)

N = 100
payload = b"sustained load test payload " * 10   # 280 bytes
times_enc = []
times_dec = []

tracemalloc.start()
snap1 = tracemalloc.take_snapshot()

print(f"\n  Running {N} encrypt+decrypt cycles...")
for i in range(N):
    t0 = time.perf_counter()
    enc = e.encrypt(payload)
    times_enc.append((time.perf_counter() - t0) * 1000)

    t0 = time.perf_counter()
    dec = e.decrypt(enc["kem_ct"], enc["aes_ct"], enc["nonce"])
    times_dec.append((time.perf_counter() - t0) * 1000)

snap2 = tracemalloc.take_snapshot()
tracemalloc.stop()

# Memory delta
top_stats = snap2.compare_to(snap1, "lineno")
mem_delta_kb = sum(s.size_diff for s in top_stats) / 1024

first10_enc = statistics.mean(times_enc[:10])
last10_enc  = statistics.mean(times_enc[-10:])
ratio       = last10_enc / first10_enc if first10_enc > 0 else 1.0

first10_dec = statistics.mean(times_dec[:10])
last10_dec  = statistics.mean(times_dec[-10:])

print(f"  encrypt  first-10 avg: {first10_enc:.1f}ms   last-10 avg: {last10_enc:.1f}ms   ratio: {ratio:.2f}x")
print(f"  decrypt  first-10 avg: {first10_dec:.1f}ms   last-10 avg: {last10_dec:.1f}ms")
print(f"  memory delta across {N} cycles: {mem_delta_kb:+.1f} KB")

# Histogram buckets
buckets = {}
for t in times_enc:
    b = int(t // 10) * 10
    buckets[b] = buckets.get(b, 0) + 1
print(f"\n  Encrypt time distribution ({N} samples):")
for b in sorted(buckets):
    bar = "#" * buckets[b]
    print(f"    {b:>3}-{b+10:<3}ms  {bar} ({buckets[b]})")

check("no runaway slowdown (ratio < 2×)", ratio < 2.0, f"ratio={ratio:.2f}")
check("memory stable (delta < 5 MB)",     mem_delta_kb < 5_000, f"{mem_delta_kb:+.0f} KB")


# ═══════════════════════════════════════════════════════════
print()
print("=" * 60)
total = PASS + FAIL
status = "ALL PASS" if FAIL == 0 else f"{FAIL} FAILED"
print(f"  STRESS TEST RESULT: {PASS}/{total}  {status}")
print(f"  Throughput summary:")
print(f"    keygen  {kg_ops:>6.1f} ops/sec  ({kg_avg:.0f}ms avg)")
print(f"    encrypt {enc_ops:>6.1f} ops/sec  ({enc_avg:.0f}ms avg)")
print(f"    decrypt {dec_ops:>6.1f} ops/sec  ({dec_avg:.0f}ms avg)")
print(f"    sign    {sign_ops:>6.1f} ops/sec  ({sign_avg:.0f}ms avg)")
print(f"    verify  {ver_ops:>6.1f} ops/sec  ({ver_avg:.0f}ms avg)")
print("=" * 60)

sys.exit(0 if FAIL == 0 else 1)
