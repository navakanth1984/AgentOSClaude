# tdh backend — manual setup (one-time)

These steps need a human (token creation + Vercel env vars). The code is already deployed-ready
on branch `label-collection-backend`.

## 1. Create the private data repo
- New GitHub repo: **`tdh-labels`** (Private).
- Copy the contents of `tdh-labels-seed/` (`pull_labels.py`, `README.md`) into it; commit + push.

## 2. Fine-grained token (least privilege)
- GitHub → Settings → Developer settings → **Fine-grained tokens** → Generate new token.
- Resource owner: your account. Repository access: **Only select repositories → `tdh-labels`**.
- Permissions: **Contents → Read and write** (nothing else). Generate and copy the token.

## 3. Vercel env vars (BOTH projects: `tdh-labeler` and `tdh-bluff`)
Project → Settings → Environment Variables (Production):
- `GITHUB_TOKEN` = the fine-grained token from step 2
- `GITHUB_REPO`  = `navakanth1984/tdh-labels`
- `GITHUB_BRANCH`= `main`
- **`tdh-labeler` ONLY:** `RATER_ALLOWLIST` = `code1:expert_a,code2:expert_b`
  (one code per recruited expert; the code maps to the rater_id used in the saved path)

## 4. Deploy the branch
- Merge `label-collection-backend` to the branch Vercel tracks, or point each Vercel project's
  production branch at it, then **Redeploy** both projects. The `api/submit` function ships
  automatically (Vercel auto-detects the `api/` directory; `tests/` is excluded via `.vercelignore`).

## 5. Verify (end-to-end)
- Open `tdh-labeler.vercel.app`, label one item, enter a **valid** code, click Export →
  status shows `✓ saved to server: expert/<rater>/<ts>.json`.
- `git clone`/`pull` `tdh-labels` → the file is present under `expert/<rater>/`.
- Try a **bad** code → status shows `⚠ server save failed (bad_code)`; nothing is committed.
- `tdh-bluff.vercel.app`: answer the puzzles, Finish → `✓ sent — thank you!`; file under `lay/`.

## Notes
- The local JSON download still happens on every submit (fallback) — if the server save fails for
  any reason, the rater can still send you the downloaded file.
- Rotate `GITHUB_TOKEN` if it ever leaks; its scope is limited to the `tdh-labels` repo only.
