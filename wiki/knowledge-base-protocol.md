# Knowledge Base Protocol — Shared by Claude & Antigravity
> The one contract every AI agent in this workspace follows, so Claude and Antigravity feed and extract from the *same* self-improving knowledge base. Symbiotic by design.

This is the canonical protocol. `CLAUDE.md`, `AGENTS.md`, and `.antigravity.md` all defer to it.

## The two memory layers

1. **Graph layer (graphify)** — machine-extracted code/structure graphs. Each repo or app keeps its own under `.graphify/` (new) or `graphify-out/` (legacy): `GRAPH_REPORT.md` (plain-language map), `graph.json` (queryable), `manifest.json`. Built and refreshed by the `graphify` CLI — AST-only updates cost no tokens.
2. **Wiki layer (synthesis)** — human-readable `wiki/` pages: one per topic, cross-linked, every claim citing its source. The central map lives at the repo root `wiki/`; some sub-apps keep their own `wiki/` too. Indexed by [knowledge-base-map.md](knowledge-base-map.md).

The graph answers *"how is the code wired"*; the wiki answers *"what is this and why"*. Use both.

## EXTRACT — how either agent reads (in order)
1. Open [knowledge-base-map.md](knowledge-base-map.md) to find which repo/app owns the topic and which layers it has.
2. **Read the graph first** for that scope: `<repo>/.graphify/GRAPH_REPORT.md` (god nodes, communities, freshness hash). For cross-module "how does X relate to Y" questions, prefer the graph tools over grep:
   - `graphify query "<question>"` — broad context (BFS)
   - `graphify path "<A>" "<B>"` — shortest path between two concepts
   - `graphify explain "<node>"` — plain-language explanation
3. **Read the wiki** for the "what/why": the relevant `wiki/*.md` pages.
4. Only fall back to raw file reads / grep when neither layer covers it. If you read raw files to answer something durable, feed it back (below).

## FEED — how either agent writes back (keep both layers current)
- **After changing code:** run `graphify update <repo-path>` (or `graphify update .`) so the graph reflects the new structure. AST-only, no API cost. Check freshness with `git rev-parse HEAD` vs the hash in `GRAPH_REPORT.md`.
- **After adding notes/sources:** drop raw material in `sources/`, then ingest into `wiki/` — update or create the right page (never duplicate), cross-link it, and add a dated line to `wiki/log.md`.
- **New repo/app:** add a row to [knowledge-base-map.md](knowledge-base-map.md); build its graph with `graphify <path>` if it has code.
- The nightly task `wiki-nightly-ingest` (2:06 AM) runs the wiki side automatically.

## Live symbiosis via MCP (optional, recommended)
graphify exposes an MCP server so an agent can query a graph live instead of reading JSON:
```
graphify serve <repo>/.graphify/graph.json
```
This serves `query_graph`, `get_node`, `get_neighbors`, `get_community`, `god_nodes`, `graph_stats`, `shortest_path`. Wiring this into Claude Code / Antigravity lets both agents hit the identical graph in real time — the tightest form of the shared brain.

## Guardrails (non-negotiable, same for both agents)
- Only update or insert — **never replace or remove** another agent's work. Get explicit approval before moving/renaming/deleting any file; never delete (set aside in `wiki/_review/`).
- This repo is a **staging workshop**: root-level project folders are live workspaces that graduate into their own repos. Don't fold them into `sources/`; map them here instead.
- Graph and wiki artifacts are shared, git-tracked state. Treat them as common ground both agents own.
