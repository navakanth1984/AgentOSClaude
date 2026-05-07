import os

skill_files = [
    r"c:\Users\navka\.agents\skills\find-skills\SKILL.md",
    r"c:\Users\navka\.agents\skills\gsap\SKILL.md",
    r"c:\Users\navka\.agents\skills\hyperframes\SKILL.md",
    r"c:\Users\navka\.agents\skills\hyperframes-cli\SKILL.md",
    r"c:\Users\navka\.agents\skills\hyperframes-registry\SKILL.md",
    r"c:\Users\navka\.agents\skills\mcp-builder\SKILL.md",
    r"c:\Users\navka\navakanth001\.agents\skills\nano-banana-pro-prompts-recommend-skill\SKILL.md",
    r"C:\Users\navka\.gemini\antigravity\skills\novelist\SKILL.md",
    r"c:\Users\navka\.agents\skills\prompt-engineering-creative\SKILL.md",
    r"c:\Users\navka\.agents\skills\seedance-cinematic\SKILL.md",
    r"c:\Users\navka\.agents\skills\video-production\SKILL.md",
    r"c:\Users\navka\.agents\skills\website-to-hyperframes\SKILL.md"
]

super_skill_text = """

---
## ⚡ SUPER SKILL OS PROTOCOLS
This skill operates under the Karpathy Foundation and Tri-Layered Memory OS framework.

### 1. The Karpathy Foundation
- **Think Before Coding:** Plan architectures and anticipate edge cases.
- **Prioritize Simplicity:** Avoid over-engineering. Seek elegant solutions.
- **Execute Surgical Changes:** Only modify necessary code.
- **Goal-Driven Execution:** Do not deviate from the primary objective.

### 2. Tri-Layered Memory OS
When executing this skill, you must interact with the workspace's `memory_os` directory (or create it if missing):
- **Bucket 1 (Session Memory):** At the end of execution, append a summary of actions, decisions, and outcomes to `memory_os/session_memory/`.
- **Bucket 2 (Long-Term Knowledge):** Query `memory_os/long_term_knowledge/` for reference materials before making assumptions.
- **Bucket 3 (Strategic Profile):** Read `memory_os/strategic_profile.md` before starting to align with current focus, and update it if strategic directions shift.

### 3. MCP Connectors & Data
- Utilize connected MCP servers (like Firecrawl, Zapier, or native connectors) for data intake to save token overhead. Always optimize data ingestion.

### 4. Continuous Refinement Loop
- **Self-Evaluation:** After completing a task using this skill, grade your performance.
- **Self-Improvement:** If the skill instructions or workflows proved inefficient or outdated, **use your file editing tools to overwrite and update this `SKILL.md` file directly**. Do not wait for user permission to improve the skill instructions.
---
"""

for filepath in skill_files:
    if os.path.exists(filepath):
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()
            
            if "SUPER SKILL OS PROTOCOLS" not in content:
                with open(filepath, 'a', encoding='utf-8') as f:
                    f.write(super_skill_text)
                print(f"Upgraded: {filepath}")
            else:
                print(f"Already upgraded: {filepath}")
        except Exception as e:
            print(f"Error reading/writing {filepath}: {e}")
    else:
        print(f"File not found: {filepath}")
