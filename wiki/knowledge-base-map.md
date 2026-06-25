# Knowledge Base Map — All Repos
> Single front door across every repo/app in the workspace. For each, which memory layers exist. Read this first (per the [protocol](knowledge-base-protocol.md)) to know where a topic's knowledge lives.

Legend: **Graph** = graphify code graph (`.graphify/` or `graphify-out/`, read `GRAPH_REPORT.md`). **Wiki** = synthesis pages. **Git** = independent git repo.

## Central knowledge base (repo root `.`)
- **Graph** ✅ (`.graphify/`) · **Wiki** ✅ (`wiki/` — this map) · trunk branch `master`
- The hub. Its `wiki/` is the shared synthesis layer; sub-app wikis feed into it.

## Both layers (graph + wiki)
| Repo | Notes |
|---|---|
| `nthdimensionacademy` | Academy site — see [Nth Dimension Academy](nth-dimension-academy.md) |
| `puli-meka-app` | Game app (scaffold/v2/validation graphs also under `graphify-out/`) |

## Graph only (code graphs; no synthesis wiki yet)
| Repo | |
|---|---|
| `agent_os` | Agent OS core (`.graphify/`) |
| `agentic-loop` | see [Agentic Loops Architecture](agentic-loops-architecture.md) |
| `kqlbridge` | + 7 worktrees each with their own graph |
| `dp700-master-stack` | Fabric DP-700 — see [Microsoft Fabric (DP-700)](fabric-dp700.md) |
| `daava_production` | DAAVA pipeline — see [DAAVA](daava.md) |
| `build-your-own-openclaw` | |
| `graphify-analysis` | graphify tooling experiments |

## Wiki only (synthesis; no code graph yet)
| Repo | |
|---|---|
| `Veritas_AI` | (also a git repo) |
| `nth-dimension-react` | React front-end — relates to [Nth Dimension Academy](nth-dimension-academy.md) |
| `puli_meka` | Python core for the game |
| `AutoGrade_Backend`, `AutoGrade_Flutter` | grading app pair |
| `git-template` | repo scaffolding template |

## Git repos with no KB layer yet (candidates for `graphify <path>`)
`Anuvedhai` · `Claude-Desktop-LLM` · `ClawGlove` · `TranceSQL` · `flutter_sdk` · `nth-brain` · `ltx_video_source` · `open-design` · `openclaw` · `sanatana-wisdom-react`

> To onboard one: `graphify <repo-path>` builds its graph; add a `wiki/` overview page if it warrants synthesis; then move its row up into the right section above.

## Maintenance
- Refresh a graph after code changes: `graphify update <repo-path>` (AST-only, free).
- Wiki ingest + nightly loop: see [CLAUDE.md](CLAUDE.md) and the `wiki-nightly-ingest` task.
- Keep this map current: whenever a repo gains/loses a layer, update its row (per the [protocol](knowledge-base-protocol.md) FEED rules).
