# CRP Gate 2 Compiler Conformance Report

Date: 2026-07-03 | Commit: 12b8e50f (merged to master via PR #27) | Spec: [IR_SPEC.md](IR_SPEC.md) v1.0.0 / [COMPILER_ABI.md](COMPILER_ABI.md) ABI 1

## Environment

| Key | Value |
|---|---|
| cpu | AMD64 Family 25 Model 80 Stepping 0, AuthenticAMD |
| os | Windows-11-10.0.26200-SP0 |
| python | 3.12.10 |
| numpy | 2.4.2 |
| scipy | 1.17.0 |
| thread_count | unrecorded |
| power_profile | unrecorded |
| affinity | default |

## Hard Acceptance

Every criterion below is machine-checked by `research/tests/acceptance/test_g2_compiler_pipeline.py` (5 tests) plus `research/tests/unit/test_compiler.py` (8 tests). Full suite: **23/23 passed** (`pytest research/tests`, `PYTHONPATH=crp`).

| Criterion | Evidence | Verdict |
|---|---|---|
| 6-stage pipeline executes in fixed order (parser → schema → canonicalizer → semantic → template → ast_guard) | `pipeline.py::IRCompiler.compile_ir` | PASS |
| Parser stage rejects malformed JSON | `test_golden_invalid_and_regressions_v1` (`IR:PAR_001`) | PASS |
| Schema stage rejects unsupported/missing IR ABI | `test_golden_invalid_and_regressions_v1` — `invalid_version.json` → `IR:SCH_002` | PASS |
| Canonicalization is RFC 8785 (JCS) and byte-identical for identical input | `test_golden_files_v1` — `canonical_ir.json` exact match | PASS |
| Semantic validation enforced per template strategy | `test_semantic_stage` (unit) | PASS |
| Template registry emits only the immutable Template ABI 1 signatures (`TEMPLATE-001..004`) | `COMPILER_ABI.md` §3, `test_template_stage` | PASS |
| AST Guard blocks disallowed imports, blocked builtins (`eval`, `exec`, `open`, `input`, `globals`, `locals`, `compile`, `dir`, `vars`, `getattr`, `setattr`), and dunder-attribute calls on all generated candidate code | `ast_guard.py::ASTStage`, `test_ast_stage` | PASS |
| Compiler never executes generated code (only parses/inspects it) | `ast_guard.py` calls `ast.parse` only, no `exec`/`eval` in `compiler/` package | PASS |
| Full byte-identical golden-file match (plugin source, canonical IR, manifest, all hash fields) | `test_golden_files_v1` | PASS |
| Stable error taxonomy — every failure stage maps to its documented external code (`IR:PAR_001` … `IR:AST_006`) | `test_golden_invalid_and_regressions_v1` | PASS |
| Regression fixture(s) still pass | `regressions/regression_001.json` in `test_golden_invalid_and_regressions_v1` | PASS |
| Gate 1 sandbox compatibility unaffected by compiler addition | `test_g1_process_isolation.py` (8 tests, unchanged, all pass in the same run) | PASS |

## Determinism Evidence

`test_determinism_verification` compiles the same golden IR (`uniform_quant.json`) 50 times, mutating an unrelated environment variable each iteration, and asserts every artifact is byte-identical. Reference hashes (golden fixture `research/tests/golden/v1/ir/expected/uniform_quant/`):

| Field | Value |
|---|---|
| `ir_hash` | `11ee57369b86be7cccfccd308bbb97a0292acf1c6849a4b52655443a5ba0d51e` |
| `plugin_hash` | `87bdbfbefcb42d80bbd380c02ba86c559c6af046b930d349f97dbf1a6b8a6bf8` |
| `registry_hash` | `c5420de11103dbd440f262bfafc9e426145d54371865d03473c249c8f7f2664d` |
| `manifest_hash` | `379d89a3fcd4715db1b6a7fe71b04d4b95f35655894801c78ccb0d76f9ce4da9` |

`generated_at` is fixed to the epoch constant (`1970-01-01T00:00:00Z`) precisely so timestamps never enter the hash — determinism is unconditional, not "same machine, same day."

## Compiler Purity

`test_compiler_purity` walks the AST of every file in `research/compiler/` (excluding the legacy shims `compiler.py`/`legacy.py`) and fails on any import outside the allow-list `{json, hashlib, ast, typing, dataclasses, types, re}` plus internal `research.*` modules. No filesystem writes, sockets, environment reads, subprocess, or `os` module access are reachable from the compiler package — confirmed by both the allow-list scan and manual read of `pipeline.py`/`ast_guard.py`.

## Cross-Platform Verification

| OS | Status |
|---|---|
| Windows | PASS — full suite run this report cites |
| Linux | Not verified in this cycle |
| macOS | Not verified in this cycle |

Carried as a known limitation (below), not a hard-acceptance blocker: the pipeline has no OS-specific code paths (no filesystem/network access per the purity check), so cross-platform risk is judged low, but it is unverified, not proven.

## Golden File Verification

- `ir/uniform_quant.json` → full manifest/plugin/canonical-IR/hash match (`test_golden_files_v1`)
- `invalid/invalid_version.json` → `IR:SCH_002` (`test_golden_invalid_and_regressions_v1`)
- `regressions/regression_001.json` → expected error code match (`test_golden_invalid_and_regressions_v1`)

## Sandbox Compatibility

All 8 Gate 1 process-isolation acceptance tests (`test_g1_process_isolation.py`) pass unmodified in the same suite run as the Gate 2 tests — the compiler's addition introduces no regression to crash containment, resource limits, cleanup latency, or functional correctness of the sandboxed executor.

## Runtime Regression

`test_memory_stability`: 100 repeated compilations of the same golden IR show RSS growth ≤ 5 MB threshold after a 5-run warm-up and `gc.collect()` — no per-compile memory leak in the pipeline.

## Soft Objectives (0 defined for Gate 2)

Gate 2 has no soft (aspirational) targets in [BENCHMARK-M3M4.md](BENCHMARK-M3M4.md) or the deferred-work registry ([GATE-REPORT-PATTERN.md](GATE-REPORT-PATTERN.md)). Decision-latency softness (RFC-0005) belongs to the representation-selection runtime (Phase 0 / Gate 4 concern), not the compiler.

## Known Limitations

- **Cross-platform unverified** — only run on Windows so far; no Linux/macOS CI leg exists yet for `research/tests`. Low risk given the purity constraint, but not evidence.
- **RFC-0005 (shared Stage-0 analysis cache)** — orthogonal to the compiler; tracked against Gate 2 (post) per the deferred-work registry, does not block this freeze.
- **Full replay provenance** (replay/compiler versions, plugin+manifest hashes stored per decision) — explicitly deferred to Gate 3 per the deferred-work registry; Gate 2 emits the hashes but does not yet persist them into a provenance store.

## Future RFCs

- Linux/macOS CI matrix for `crp/research/tests` (currently Windows-only).
- Compiler ABI 2 (multi-IR-ABI acceptance, Template ABI 2) — no immediate driver; the compatibility matrix in `COMPILER_ABI.md` already reserves the row.

## Freeze Declaration

**Gate 2 (IR Compiler): FROZEN.** All hard-acceptance criteria pass (23/23 tests), determinism is proven per fixed golden hashes, purity is enforced by AST-level import allow-listing, and Gate 1 sandbox compatibility is unaffected. Per [GATE-REPORT-PATTERN.md](GATE-REPORT-PATTERN.md), `COMPILER_ABI.md` and `IR_SPEC.md` remain frozen; further compiler changes require an RFC or a documented defect. Reproduce with `PYTHONPATH=crp pytest crp/research/tests` from repo root, or `pytest research/tests` from `crp/`.

Gate 3 (Provenance) may now treat `CompilerArtifact`/`CompilerManifest` as an immutable input per the provenance chain in `ROADMAP-R1.md`.
