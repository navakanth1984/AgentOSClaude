---
date: 2026-06-07
tags: [notebooklm, workflow, content-creation, productivity, ai-tools, templates]
project: "AI-Automation"
source: "NotebookLM advanced workflow guide"
---

# NotebookLM 6-Step Production Workflow

## Key Idea
NotebookLM's power isn't just generation — it's **source attribution + iteration**. The
"recipe" metaphor means every output is reproducible, shareable, and team-ready. The
source-linked output also builds audience trust that generic AI can't.

## Details

### Step 1 — Upload & Generate
- Drop PDFs, notes, or docs into a notebook
- Type a prompt: "build a study guide / timeline / briefing doc"
- Output arrives in seconds

### Step 2 — Fact-Check via Source Attribution
- Click **source attribution** to see the exact prompt + sources used
- Click any line of text → jumps to the exact file it came from
- Fact-check in seconds instead of digging through documents
- ⚠️ AI is not guaranteed accurate — always double-check legal, health, or critical data

### Step 3 — Refine with Iterate
- If output is too long, too jargon-heavy, or off-tone → hit **Iterate**
- Original sources and setup are preserved automatically
- Prompt the tweak: "rewrite for a beginner", "keep under 300 words", "add bullet summary"
- No need to start over — iterate in place

### Step 4 — Repurpose for Multiple Audiences
Using one source set, iterate to create:
- **Detailed version** → internal team / expert audience
- **Short version** → onboarding / new members
- **Tiny version** → email draft / social post
Core facts stay consistent across all versions

### Step 5 — Save the Recipe as a Template
- Once a recipe works → save it
- Any team member can rerun it to get the same document type
- Use cases: weekly update, welcome guide, client briefing
- Eliminates reinvention — one good prompt = repeatable system

### Step 6 — Share with Source Attribution to Build Trust
- Recipients see the sources attached to each fact
- Removes "was this just made up by AI?" doubt
- Especially powerful for community, clients, and high-stakes audiences

## Integration with Agent OS

This workflow maps directly onto Agent OS capabilities:

| NotebookLM Step | Agent OS Equivalent |
|---|---|
| Upload & Generate | `find_matching_notebooks()` → cache search |
| Source Attribution | Notebook URLs injected into swarm notes |
| Iterate | Re-run `/swarm` with refined prompt |
| Multi-audience repurpose | `/swarm` × N with different angle prompts |
| Save recipe as template | Skill scaffold via `builders._scaffold_skill()` |
| Share with attribution | Obsidian note with `## Your NotebookLM Sources` section |

**Next integration idea:** Add an `iterate` flag to `/swarm` endpoint — takes a prior swarm
note path and a refinement prompt, reruns only the agents that need updating.

## Action / Next Steps
- [ ] Apply iterate pattern to next swarm run — refine one output for 3 audiences
- [ ] Build a NotebookLM "recipe library" note listing best-performing prompt templates
- [ ] Add `iterate` parameter to `run_swarm()` in swarm.py
- [ ] Share a source-attributed swarm note with someone to test the trust-building effect
