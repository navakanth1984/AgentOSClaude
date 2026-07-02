# Milestone 2 Benchmark Report — Tier-0 Telemetry

Date: 2026-07-02 | Host: Windows 11, AMD Ryzen 5 5600H | Build: --release, stable-x86_64-pc-windows-gnu

| Measurement | Value | Spec §2a verdict |
|---|---|---|
| Rust `record()` (criterion mean, 312M iters) | 17.7 ns (CI 17.0–18.4 ns) | target <5 µs: **pass** (~280×) |
| Python `record()` (pytest mean, N=50k) | 0.238 µs | hard limit 10 µs: **pass** (42×); target 5 µs: **pass** (21×) |
| Drop behavior under full buffer | non-blocking, counted (`dropped()`) | required: **pass** |

Evidence: `crp/telemetry/target/criterion` report (`cargo +stable-x86_64-pc-windows-gnu bench`) and `pytest crp/runtime/tests/test_budget.py -v -s` output.

Toolchain note: MSVC linking is unavailable on this host (VS 2026 without the
Windows SDK; Git's coreutils `link.exe` shadows MSVC link). Builds use the GNU
toolchain with WinLibs `dlltool` — see `crp/tools/rust-env.ps1`.

Conclusion: the <5 µs Tier-0 budget is real on this host with wide margin. The
raw Rust path costs ~18 ns per event; crossing the Python boundary adds ~220 ns
(PyO3 call + timestamping), still ~21× inside the target. Risk R-002 (telemetry
overhead exceeds budget) shows no evidence at Tier 0; the binding overhead is
the dominant term, so future budget pressure should be attacked at the call
boundary (batching), not inside the ring buffer.
