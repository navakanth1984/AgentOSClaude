import os
import re

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
    r"c:\Users\navka\.agents\skills\website-to-hyperframes\SKILL.md",
    r"C:\Users\navka\.gemini\skills\screenplay-skill\SKILL.md",
    r"C:\Users\navka\.gemini\skills\cinematography-skill\SKILL.md",
    r"C:\Users\navka\.gemini\skills\direction-skill\SKILL.md",
    r"c:\Users\navka\navakanth001\.agents\skills\context-engineering-consulting\SKILL.md",
    r"C:\Users\navka\.gemini\skills\karpathy-coding-guidelines\SKILL.md",
    r"c:\Users\navka\navakanth001\.agents\skills\acting-performance-skill\SKILL.md",
    r"c:\Users\navka\navakanth001\.agents\skills\skill-creator\SKILL.md"
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

### 2. Tri-Layered Memory OS & Hierarchical Memory
When executing this skill, you must interact with the workspace's `memory_os` directory (or create it if missing):
- **Bucket 1 (Session Memory):** At the end of execution, append a summary of actions, decisions, and outcomes to `memory_os/session_memory/`.
- **Bucket 2 (Long-Term Knowledge):** Query `memory_os/long_term_knowledge/` for reference materials before making assumptions.
- **Bucket 3 (Strategic Profile):** Read `memory_os/strategic_profile.md` before starting to align with current focus, and update it if strategic directions shift.
- **Hierarchical Delegation:** To escape context window limits, delegate data-heavy tasks to specialized sub-agents that return only refined results. Use **Smart Truncation** (Head/Tail retention) to keep the main context lean.

### 3. MCP Connectors & Data
- Utilize connected MCP servers (like Firecrawl, Zapier, or native connectors) for data intake to save token overhead. Always optimize data ingestion.

### 4. Continuous Refinement Loop
- **Self-Evaluation:** After completing a task using this skill, grade your performance.
- **Self-Improvement:** If the skill instructions or workflows proved inefficient or outdated, **use your file editing tools to overwrite and update this `SKILL.md` file directly**. Do not wait for user permission to improve the skill instructions.
---
"""

# Robust regex to match any version of the SUPER SKILL OS PROTOCOLS block
# Handles different emojis, broken encodings, and spacing variations
BLOCK_PATTERN = re.compile(r'\n*---+\s*\n## .*?SUPER SKILL OS PROTOCOLS.*?---+', re.DOTALL)

def upgrade_skill(filepath):
    if not os.path.exists(filepath):
        print(f"File not found: {filepath}")
        return

    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Check if the latest version is already there (exactly as defined)
        target_text = super_skill_text.strip()
        if target_text in content and "Hierarchical Memory" in content:
            # Check if there are multiple blocks or if the content matches perfectly
            # If we remove all blocks and re-append, does it change anything?
            new_content = BLOCK_PATTERN.sub('', content).rstrip() + super_skill_text
            if new_content.strip() == content.strip():
                print(f"Already up-to-date: {filepath}")
                return

        # Clean up ALL existing blocks and append the new one
        clean_content = BLOCK_PATTERN.sub('', content).rstrip()
        final_content = clean_content + super_skill_text
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(final_content)
        print(f"Upgraded/Cleaned: {filepath}")
        
    except Exception as e:
        print(f"Error processing {filepath}: {e}")

if __name__ == "__main__":
    for filepath in skill_files:
        upgrade_skill(filepath)
