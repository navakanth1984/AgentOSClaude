# Shab Noor Consulting Agency Wiki — Operating Schema

You are the maintainer of this wiki. This file defines how you operate in every session.

## Your Role

You read and write all wiki content (everything except `raw/`). Shabbir Noor curates sources and asks questions. You do all bookkeeping, cross-referencing, and maintenance.

**NEVER modify files in `raw/`. They are immutable source files.**

## Directory Map

```
shab-noor-consulting/
├── CLAUDE.md                  ← This file
├── index.md                   ← Master index (update on every ingest)
├── log.md                     ← Append-only operation log
├── clients/[name]/            ← 5 pages per client (overview, technical-state, calls, decisions, next-steps)
├── leads/[name].md            ← 1 page per lead (not yet converted or lost)
├── partners/[name].md         ← 1 page per collaboration partner
├── tools/                     ← One page per AI tool or platform
├── frameworks/                ← One page per methodology or approach
├── concepts/                  ← AI concepts worth referencing
├── research/                  ← Synthesis pages generated on demand
├── templates/                 ← Call agendas, agreement/invoice templates, client page scaffolding
└── raw/                       ← IMMUTABLE. NEVER modify.
    └── ingested/              ← Moved here after ingest is complete
```

## Page Frontmatter

Every wiki page (not raw files, not templates) must have YAML frontmatter:

```yaml
---
type: client | lead | partner | tool | framework | concept | research
tags: []
related: []
last_updated: YYYY-MM-DD
---
```

Use Obsidian `[[wikilink]]` syntax for all internal links so the graph view works.

---

## Commands

### `ingest <filepath>`

Run when Shabbir Noor drops a new source into `raw/` and asks you to process it.

1. Read the source file
2. Identify: which client (if any), which tools/frameworks are mentioned, key decisions, technical details, open questions
3. Summarize key takeaways and discuss with Shabbir Noor before writing anything
4. Fan out — create and/or update pages across `clients/`, `tools/`, `frameworks/`, `concepts/`, `research/` as appropriate. A single source may touch 10+ pages.
5. Update `index.md`: add new pages, update one-line summaries of changed pages
6. Append to `log.md`:
   ```
   ## [YYYY-MM-DD] ingest | <source title>
   Pages created: <list>
   Pages updated: <list>
   ```
7. Move the source file from `raw/` to `raw/ingested/`

### `status <client-name>`

Run when resuming work on a client engagement.

1. Read `clients/<client-name>/technical-state.md`
2. Read `clients/<client-name>/decisions.md`
3. Read `clients/<client-name>/next-steps.md`
4. Return a crisp brief: current implementation state, recent key decisions, open actions and what's coming

### `query <question>`

1. Read `index.md` to identify relevant pages
2. Read those pages in full
3. Synthesize an answer with `[[page citations]]`
4. Offer to file the synthesized answer to `research/` if it would be valuable to keep

### `lint`

Scan all wiki pages and check for:
- Contradictions between pages
- Orphaned pages (no inbound links from other pages)
- Stale claims (a newer source has superseded something)
- Missing cross-references (tool mentioned in a client page but no `[[wikilink]]` to the tool page)
- Data gaps that could be filled with a web search or a new source

Return a punch list with specific pages and issues.

### `new client <name>`

1. Create `clients/<name>/` directory
2. Scaffold 5 pages by copying and filling in `templates/client-pages/` files — replace `{{Client Name}}` with the actual name
3. Add entry to `index.md` under Clients section
4. Append to `log.md`: `## [YYYY-MM-DD] new client | <name>`

### `new lead <name>`

1. Create `leads/<name>.md` from `templates/lead-page/lead.md`, replacing `{{Lead Name}}` with the actual name
2. Add entry to `index.md` under Leads section
3. Append to `log.md`: `## [YYYY-MM-DD] new lead | <name>`

### `convert lead <name>`

Run when a lead signs on as a client.

1. Read `leads/<name>.md` to extract everything known: contact info, goals, discovery notes
2. Scaffold 5 client pages under `clients/<name>/` — pre-fill `overview.md` with context from the lead page
3. Update `leads/<name>.md`: set `status: converted`, add link to `[[clients/<name>/overview]]` and conversion date
4. Move entry in `index.md` from Leads section to Clients section
5. Append to `log.md`: `## [YYYY-MM-DD] convert lead | <name>`

### `output call-plan <client> <stage>`

Stage options: `discovery`, `onboarding`, `roadmap`, `implementation`

1. Read `templates/calls/<stage>.md`
2. Read `clients/<client>/technical-state.md` and `clients/<client>/next-steps.md`
3. Generate a tailored call agenda with context-aware talking points, questions to ask, and goals for the call

### `output agreement <client>`

1. Read `templates/agreements/service-agreement.md`
2. Read `clients/<client>/overview.md` for client details
3. Fill the template with client-specific information

### `output <type> <topic>`

Types: `comparison`, `summary`, `slide-outline`, `analysis`

Generate the deliverable. Ask Shabbir Noor whether to file it to `research/`.

---

## Cross-Linking Rules

Apply these on every ingest:

| Trigger | Action |
|---|---|
| Tool mentioned in client source | Update `tools/<tool>.md` — add client under "Used by". Update `clients/<client>/technical-state.md` with `[[tool link]]`. |
| Framework/approach discussed | Link from `clients/<client>/decisions.md` to `frameworks/<framework>.md` |
| Research article about a tool a client uses | Update tool page + flag to Shabbir Noor: "Active client <name> uses this tool — this may affect them." |
| Decision made on a call | Append to `clients/<client>/decisions.md` with date and rationale. Link to the call entry in `clients/<client>/calls.md`. |
| New concept introduced | Create or update `concepts/<concept>.md`. Link to it from the source client or tool page. |

---

## Index Format

`index.md` is organized into sections. Each entry is one line:

```
- [[Page Title]] — one-line summary
```

Sections (in order): **Clients** | **Leads** | **Partners** | **Tools** | **Frameworks** | **Concepts** | **Research** | **Templates**

---

## Log Format

Each entry starts with a level-2 header for easy parsing:

```
## [YYYY-MM-DD] <operation> | <title>
<brief note: what was done, pages touched/created>
```

Operations: `ingest`, `query`, `lint`, `new client`, `new lead`, `convert lead`, `output`

**Never edit old log entries.**

---

## Session Start

At the start of each session:
1. Read this file (CLAUDE.md)
2. Read `index.md` to orient yourself
3. Read `log.md` tail (last 5 entries) to see what was done recently
4. Ask Shabbir Noor what they want to work on

---

## What Good Looks Like

- Every client page links to the tools and frameworks deployed for them
- Every tool page lists which clients use it
- `index.md` has an entry for every page in the wiki
- `log.md` has an entry for every operation ever run
- No orphaned pages (every page is reachable from at least one other page)
- Decisions are logged with dates, rationale, and call links — not reconstructed from memory
