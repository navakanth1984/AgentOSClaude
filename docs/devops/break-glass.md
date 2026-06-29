# Break-Glass: Emergency `master` Protection Override

`master` is branch-protected with **`enforce_admins = true`**, which means even
repository admins cannot push directly or merge a PR that fails the required
`build` check. That is the desired steady state. This document is the **only**
sanctioned way to relax it, and exists for genuine emergencies where the normal
PR → CI → merge flow cannot resolve the incident in time.

> **Default answer is "don't."** If a hotfix can go through a normal PR and the
> `build` check passes, use the normal flow. Break-glass is for when the gate
> itself is the blocker.

## Current protected state (steady state)

| Setting | Value |
|---|---|
| `enforce_admins` | `true` |
| Required PR before merge | yes (0 approvals required — solo repo) |
| Required status checks | `build` |
| Force pushes | disabled |
| Branch deletion | disabled |

Snapshot it any time:

```bash
gh api repos/navakanth1984/AgentOSClaude/branches/master/protection > protection-backup.json
```

## When break-glass is justified

Use it **only** when all of these are true:

1. `master` is broken or a security/production incident requires an immediate fix.
2. The normal flow is genuinely blocked — e.g. the `build` workflow itself is
   broken (so no PR can ever go green), or GitHub Actions is down.
3. Waiting for the normal flow would cause material harm.

If the `build` check is merely *failing on a legitimate test*, that is **not** a
break-glass case — fix the test in a PR.

## Procedure

### Step 0 — Record the incident first
Before touching protection, write down: who, when, why, and the
commit/PR involved. Snapshot current protection (`protection-backup.json` above).

### Step 1 — Relax the minimum necessary
Prefer the **smallest** relaxation. In order of preference:

**(a) Drop admin enforcement only** (still requires the PR + check for others,
but lets an admin merge):
```bash
gh api -X DELETE repos/navakanth1984/AgentOSClaude/branches/master/protection/enforce_admins
```

**(b) If the `build` check itself is broken**, temporarily remove it as a
required check (keep PR + admin rules):
```bash
gh api -X PATCH repos/navakanth1984/AgentOSClaude/branches/master/protection/required_status_checks \
  -F 'contexts[]'   # empty set — no required contexts
```

Only fully disabling protection (`gh api -X DELETE .../master/protection`) as a
last resort, and never leave it in that state.

### Step 2 — Apply the hotfix
Open the hotfix PR and merge it (admin merge is now possible). Keep the change
as small as the incident requires.

### Step 3 — RESTORE protection immediately (mandatory)
This is not optional and should happen within minutes of the merge:

```bash
# Re-enable admin enforcement
gh api -X POST repos/navakanth1984/AgentOSClaude/branches/master/protection/enforce_admins

# Re-add the required build check (if you removed it in 1b)
gh api -X PATCH repos/navakanth1984/AgentOSClaude/branches/master/protection/required_status_checks \
  -F 'contexts[]=build'
```

If you fully deleted protection in Step 1, re-apply the full policy from the
snapshot:
```bash
gh api -X PUT repos/navakanth1984/AgentOSClaude/branches/master/protection \
  --input protection-backup.json
```

### Step 4 — Verify it's back
```bash
gh api repos/navakanth1984/AgentOSClaude/branches/master/protection \
  --jq '{enforce_admins:.enforce_admins.enabled, checks:.required_status_checks.contexts}'
```
Expected: `{"enforce_admins": true, "checks": ["build"]}`.

### Step 5 — Post-incident
- Append the incident (time relaxed, time restored, what was merged, root cause)
  to the team log / `wiki/log.md`.
- File a follow-up so the underlying cause (e.g. a flaky `build` workflow) is
  fixed through the normal flow, so the same break-glass isn't needed again.

## Invariant

**Protection is never left relaxed across a coffee break.** Relax → fix →
restore → verify, all in one sitting. If you cannot restore immediately, you
should not have relaxed it.
