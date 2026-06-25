# MVCT V1 — The Microscope

Binary answer-gate tutor over the validated `transfer-detector-v0`. It proves one
falsifiable claim: *a capability detector can serve as a constitutional gate that
governs answer release — more effectively than an identical ungated tutor.*

See the design spec: `../docs/superpowers/specs/2026-06-25-mvct-v1-design.md`.

## Layout
`sensor` (detector firewall) → `auditor` (sole token minter) → `permission` (HMAC
capability) → `socratic` (LLM + guard) → `ledger`/`monitor`. `knowledge` supplies the
mandatory houseplant domain; `runner` is the control-vs-experimental harness.

## Setup
```bash
python -m pip install pytest google-generativeai
```
The detector is resolved via path (see `pyproject.toml` / repo `pyrefly.toml`); no
editable install needed.

## Test (offline, no API key, zero cost)
```bash
python -m pytest mvct-v1/ -q          # from repo root
```

## Run the experiment (control vs experimental) — needs a key (billable)
```bash
export GEMINI_API_KEY=...
cd mvct-v1 && PYTHONPATH=../transfer-detector-v0 python -c \
"import json, runner; s=json.load(open('scripts/demo_transfer.json')); \
print(runner.run_script(s,'control')); print(runner.run_script(s,'experimental'))"
```

## Interactive demo — needs a key
```bash
export GEMINI_API_KEY=...
cd mvct-v1 && PYTHONPATH=../transfer-detector-v0 python loop.py
```

## Constitutional invariants (enforced in Python, never trusted to the LLM)
1. No canonical answer tokens while locked (deterministic).
2. No equivalent complete solution while locked (best-effort via the blocklist;
   full semantic-equivalence detection is a known V1 limit — spec §4).
3. Unlock only via an Auditor-minted HMAC `PermissionToken`.

## Known limits
- The detector was validated against a **synthetic** human ceiling. Swap
  `TransferSensor`'s `judge_fn` for a real-human-validated detector before drawing
  strong conclusions. V1 results are conditional on that ceiling.
- Single topic / single asset by design. Knowledge graph, causal memory, graded
  scaffold-withdrawal, and the developmental controller are deferred (spec §9).
