# 🔄 Session-Start Checklist

*This file is the canonical session-start protocol. Every AI agent reads this at session start.*  
*Location: `memory_os/session-start-checklist.md`*

---

## 1. Context Restore (30 seconds)
- [ ] List last 5 files in `memory_os/session_memory/`
- [ ] Ask user which session to restore (or start fresh)

## 2. Model Economics Checkpoint (autonomous — 15 seconds)
- [ ] Read `memory_os/strategic_profile.md`
- [ ] Read `memory_os/long_term_knowledge/model-routing-corrections.md`
- [ ] Read `memory_os/model-usage-log.json` (last entry)
- [ ] Display quick routing card:

```
╔══════════════════════════════════════════════════╗
║  🧠 MODEL ECONOMICS CHECKPOINT                  ║
╠══════════════════════════════════════════════════╣
║  Active Model:  [model name]                     ║
║  Tier:          [1-5]                            ║
║  Today's Focus: [from strategic_profile]         ║
║  Suggested Tier: [based on planned work]         ║
║  Corrections:   [count from routing-corrections] ║
╚══════════════════════════════════════════════════╝
```

- [ ] If mismatch detected (e.g., Tier 5 model for Tier 2 work), suggest switching
- [ ] If no mismatch, confirm and proceed

## 3. Quick Reference — When to Flag

| Situation | Action |
|:---|:---|
| User starts simple task on Opus | "Quick model check: switch to Flash for this?" |
| User starts architecture task on Flash | "This looks like Tier 4-5 work. Consider Opus?" |
| User hasn't mentioned model in 3+ sessions | Gently remind: "Running model economics check..." |
| Session cost > $5 estimated | Flag: "Session cost is getting high. Review routing?" |

## 4. Session-End Logging
- [ ] Append to `memory_os/model-usage-log.json`
- [ ] Note any routing corrections in `model-routing-corrections.md`
- [ ] Run `session_end.py`

---

*This checklist is self-improving. If steps prove inefficient, update directly.*  
*Last updated: 2026-06-12*
