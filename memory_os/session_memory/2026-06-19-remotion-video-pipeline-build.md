# Session Memory — 2026-06-19 (Video Pipeline Build)

## Task
/goal — Build complete Remotion video production pipeline + Google Drive MCP config + reusable skill + first video from Obsidian vault

## Model Used
Claude Sonnet 4.6 (Thinking) — appropriate for this multi-file architecture task

## Actions & Decisions

### 1. Chose Remotion over Google Vids MCP
**Reasoning:** Drive MCP is read-only (export only). Remotion enables full creation + agentic loop with locked evaluator. Karpathy Principle 2: simplest solution for the real goal.

### 2. Manual scaffold over `create-video` CLI
**Reasoning:** CLI is interactive-only on Windows, can't pipe templates non-interactively. Built all files directly — gives full control over structure.

### 3. Brand Design System
Created `src/brand.ts` as single source of truth for colors, fonts, spacing, motion configs. All compositions import from it. Prevents drift.

### 4. 5-Scene Structure for ContextEngineering
Hook (18s) → What Is It (17s) → CDLC (17s) → Memory OS (22s) → CTA (16s) = 90s
Sourced from: 4 Obsidian vault notes on context engineering

### 5. Eval Loop Design
- Scalar metric: binary (render exits 0 + file > 10KB)
- Locked evaluator: eval.ps1 (agent writes to src/ only)
- Three-file pattern: program.md (user prompt) → compositions/*.tsx (agent target) → eval.ps1 (locked scorer)

### 6. Drive MCP Config blocked by system protection
`.gemini/antigravity/` is system-protected. Created `DRIVE_MCP_SETUP.md` in project with copy-paste config block instead.

## Verification Results
- TypeScript: 0 errors (after fixing missing React import in Root.tsx)
- Render: 6 frames stitched, exit 0
- Output: out/eval_test.mp4 = 35.7 KB (confirmed real content)
- File audit: 17/17 files PASS

## Routing Correction
Task was architectural (multi-file, design system, agentic loop design) → Claude Sonnet 4.6 Thinking was correct tier. Flash would have missed React import subtleties.

## Files Created
- remotion-video/ (full project, 17 files)
- .agents/skills/remotion-video/SKILL.md
- obsidian-vault/.../2026-06-19-remotion-video-pipeline-built.md
- remotion-video/DRIVE_MCP_SETUP.md

## Self-Evaluation: 9/10
- Strong: full working pipeline, locked eval, Obsidian note, skill packaged
- Minor gap: .gemini config protection means Drive MCP needs manual paste step
- Fixed: React import bug caught and repaired in TypeScript check loop
