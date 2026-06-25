---
date: 2026-06-25
tags: [mvct, nth-brain, transfer-detector, data-collection, backend, vercel, spec]
project: "NTH Brain / MVCT — Stage B"
status: design-approved
depends_on: "tdh-labeler + tdh-bluff (deployed Vercel static sites); transfer-detector-v0 eval pipeline"
---

# Label-Collection Backend — Design Spec

## 1. Objective
Replace the "rater downloads a JSON file and emails it to you" flow with a serverless endpoint that **auto-persists each submission to a private GitHub repo**, tagged and organized by track + rater + timestamp, downloadable later and ready to feed the detector eval pipeline. This is **Stage B infrastructure** — collecting the independent human ground truth that is the project's hard-stop gate.

### Non-negotiable integrity invariants (what the contamination incident taught)
1. **Write-only endpoint** — the response never returns detector predictions or any other rater's labels. Blindness is preserved by construction.
2. **Server-side validation + contamination guard** — reject malformed payloads and any rationale matching `/Human [AB] rationale for/i` (the known templated-junk signature).
3. **Frozen eval set enforced server-side** — reject any `transcript_id` outside the frozen 16-ID pilot.
4. **Local-download fallback retained** — the browser still downloads the file even when the POST succeeds, so a flaky network never loses a rater's work.
5. **Append-only** — every submission is a new uniquely-named file; nothing is ever overwritten. Git history is the audit trail.

---

## 2. Architecture

```text
Rater (browser — blind labeling UI UNCHANGED)
   │ clicks Submit
   ▼
index.html exportAll():  (1) local download  ← fallback, always runs
                         (2) POST same JSON (+ access code) → /api/submit
   ▼
/api/submit   (Vercel serverless fn, Node 18+, ZERO deps — global fetch only)
   ├─ auth     expert → code ∈ RATER_ALLOWLIST → resolves rater_id
   │           lay    → no code; best-effort IP rate-limit + size cap
   ├─ validate track schema + contamination guard + frozen-ID check + size cap
   ├─ stamp    server-side: rater_id, track, submitted_at (UTC), tool_version
   └─ commit   PUT GitHub Contents API → NEW file (no SHA, never overwrites)
   ▼
private repo  tdh-labels/   ← git pull later → pull_labels.py → eval pipeline
```

Two Vercel projects (`tdh-labeler`, `tdh-bluff`) each get their own `api/submit.js`. They are near-identical; the only differences are the track name (`expert` / `lay`), the payload schema, and whether an access code is required. Each function is self-contained (separate deploys — no shared module across projects).

---

## 3. Storage repo & tagging

A **new private GitHub repo `tdh-labels`** (separate from the instrument/main repo so the commit token's blast radius is one data repo):

```text
tdh-labels/
├── expert/<rater_id>/<UTC-ISO-timestamp>.json   # one file per submission, append-only
├── lay/<handle-or-anonhash>/<UTC-ISO-timestamp>.json
├── pull_labels.py   # expert/<rater>/*.json → transfer-detector-v0/data/labels/human_a|b
└── README.md        # how the data is organized + how to pull it
```

- **Tagging = path + commit metadata.** Track, rater, and time are encoded in the path; the git author/date and commit message add a second layer.
- **No write races.** Unique timestamped paths mean every commit is a *create* — no SHA fetch, no merge conflict, concurrent submissions are independent.
- Re-submissions by the same rater create additional timestamped files; `pull_labels.py` keeps the latest per `(rater, transcript_id)` when importing.

---

## 4. Endpoint contract

**Request** `POST /api/submit` · `Content-Type: application/json` · body ≤ 256 KB:
```jsonc
// expert (tdh-labeler) — mirrors current exportAll() out, plus code
{
  "track": "expert",
  "code": "<per-rater access code>",
  "_rater": "<client-typed name, NOT trusted for attribution>",
  "labels": { "t01": { "classification": "transfer", "human_confidence": 0.8,
                       "evidence_types_present": [...], "anti_evidence_types_present": [...],
                       "evidence_quotes": [{"type": "...", "quote": "..."}],
                       "partial_transfer": false, "rationale": "..." }, ... }
}
// lay (tdh-bluff) — the bluff game's export shape (exact fields pinned in the plan), no code
```

**Responses (write-only — no data echoed back):**
- `200 {"ok": true, "file": "expert/<rater_id>/<ts>.json"}`
- `401 {"ok": false, "error": "bad_code"}` (expert, code not in allowlist)
- `422 {"ok": false, "error": "validation"|"contamination"|"unknown_transcript_id"}`
- `413 {"ok": false, "error": "too_large"}`
- `429 {"ok": false, "error": "rate_limited"}` (lay)
- `502 {"ok": false, "error": "commit_failed"}` (GitHub API failure)

**Server-side processing order:** method/size check → auth → schema validation → contamination guard → frozen-ID check → resolve `rater_id` from code (expert) → build path → commit.

---

## 5. Validation rules
- **Schema** — expert: each label needs `transcript_id`-keyed entry with `classification ∈ {transfer,transitional,none}`; evidence_quotes well-formed. Lay: bluff shape (3-way vote + sure toggle), pinned in the plan after reading `tdh-bluff/index.html`.
- **Contamination guard** — reject if any `rationale` matches `/Human [AB] rationale for/i`.
- **Frozen-ID enforcement** — accept only the 16 pilot IDs (`t01 t02 t06 t07 t14 t17 t19 t20 t23 t26 t28 t31 t32 t33 t35 t40`); reject submissions referencing any other id. The allowed set lives in a single constant.
- **Size cap** — 256 KB; reject larger.

---

## 6. Client changes (small, additive)
`exportAll()` is extended (both tools):
1. Keep the existing local download verbatim (fallback).
2. `POST` the same `out` object (plus `track` and, for the labeler, the `code` from a new field) to `/api/submit`.
3. Render a status line: `✓ saved to server` / `⚠ server save failed — please email the downloaded file`.

The labeler gains one input: **rater access code** (next to the existing name field). The bluff tool adds no code field. No change to the blind labeling UI or the data the rater sees.

---

## 7. Secrets & environment (server-side only; never in the client)
Per Vercel project:
- `GITHUB_TOKEN` — fine-grained PAT scoped to **only** `tdh-labels`, `contents: read/write`.
- `GITHUB_REPO` — e.g. `navakanth1984/tdh-labels`.
- `GITHUB_BRANCH` — default `main`.
- `RATER_ALLOWLIST` — `code:rater_id` pairs (expert project only), e.g. `a1b2:expert_b,c3d4:expert_a`.

The static client never holds the token or the allowlist.

---

## 8. Error handling
- POST failure of any kind → the local download already ran, so no data is lost; the client tells the rater to email the file as a fallback.
- GitHub API non-2xx → `502`; the function logs the status but returns no sensitive detail.
- Malformed/oversize/contaminated → 4xx with a terse reason; nothing is committed.

---

## 9. Testing (DI + TDD, mirroring mvct-v1)
`submit.js` exports a pure `handle(payload, env, commitFn)` core; the Vercel handler is a thin wrapper that calls it. Node tests inject a fake `commitFn` (no network):
- valid expert submission → `commitFn` called with path `expert/<resolved_rater>/<ts>.json`; `200`.
- missing/unknown code → `401`, no commit.
- rationale matching the contamination signature → `422`.
- `transcript_id` outside the frozen set → `422`.
- payload > 256 KB → `413`.
- lay open submission with valid bluff shape → `200`.
- `commitFn` throws → `502`.

---

## 10. Security threat model

| ID | Threat | Mitigation |
|----|--------|-----------|
| S1 | Public endpoint abused to spam-commit to your GitHub | Expert gated by per-rater code; lay rate-limited + size-capped; dedicated repo limits blast radius |
| S2 | Token leak compromises code/instrument | Fine-grained PAT scoped to **only** `tdh-labels`, contents-only |
| S3 | Off-protocol / junk pollutes the kill-gate dataset | Frozen-ID enforcement + schema + contamination guard, server-side |
| S4 | Rater spoofs identity (claims to be Human A) | Attribution comes from the **server-resolved** `rater_id` (via code), not the client-typed name |
| S5 | Blindness broken (rater sees detector calls / others' labels) | Write-only endpoint; nothing returned but `{ok, file}` |

---

## 11. Manual steps (require your hands — I'll give click-by-click)
1. Create the private `tdh-labels` GitHub repo.
2. Create a fine-grained PAT scoped to `tdh-labels` (contents:read/write).
3. Add env vars (`GITHUB_TOKEN`, `GITHUB_REPO`, `GITHUB_BRANCH`, `RATER_ALLOWLIST`) to both Vercel projects.
4. Issue each recruited rater a code (and record code→rater_id in `RATER_ALLOWLIST`).
5. Redeploy both projects → URLs updated.

---

## 12. Deferred (YAGNI / anti-scope)
Admin dashboard/UI · database · email/Slack notifications · realtime · OAuth login · automated rater onboarding · lay-track code-gating · server-side dedup (handled at pull time). Git + `pull_labels.py` is the read path.

## 13. Definition of Done
A recruited rater opens `tdh-labeler.vercel.app`, labels the pilot blind, enters their code, submits → a new file appears at `tdh-labels/expert/<their_id>/<ts>.json` (verified by `git pull`), with no detector output ever exposed; bad codes, off-set IDs, and contaminated rationales are rejected; the local download still works as fallback; `pull_labels.py` lands the data in `transfer-detector-v0/data/labels/` for `eval/human_ceiling.py`.
