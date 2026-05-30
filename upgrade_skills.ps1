$files = @(
    "c:\Users\navka\.agents\skills\find-skills\SKILL.md",
    "c:\Users\navka\.agents\skills\gsap\SKILL.md",
    "c:\Users\navka\.agents\skills\hyperframes\SKILL.md",
    "c:\Users\navka\.agents\skills\hyperframes-cli\SKILL.md",
    "c:\Users\navka\.agents\skills\hyperframes-registry\SKILL.md",
    "c:\Users\navka\.agents\skills\mcp-builder\SKILL.md",
    "c:\Users\navka\navakanth001\.agents\skills\nano-banana-pro-prompts-recommend-skill\SKILL.md",
    "C:\Users\navka\.gemini\antigravity\skills\novelist\SKILL.md",
    "c:\Users\navka\.agents\skills\prompt-engineering-creative\SKILL.md",
    "c:\Users\navka\.agents\skills\seedance-cinematic\SKILL.md",
    "c:\Users\navka\.agents\skills\video-production\SKILL.md",
    "c:\Users\navka\.agents\skills\website-to-hyperframes\SKILL.md",
    "C:\Users\navka\.gemini\skills\screenplay-skill\SKILL.md",
    "C:\Users\navka\.gemini\skills\cinematography-skill\SKILL.md",
    "C:\Users\navka\.gemini\skills\direction-skill\SKILL.md",
    "c:\Users\navka\navakanth001\.agents\skills\context-engineering-consulting\SKILL.md",
    "C:\Users\navka\.gemini\skills\karpathy-coding-guidelines\SKILL.md",
    "c:\Users\navka\navakanth001\.agents\skills\acting-performance-skill\SKILL.md",
    "c:\Users\navka\navakanth001\.agents\skills\skill-creator\SKILL.md"
)

$text = @"

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
"@

foreach ($file in $files) {
    if (Test-Path $file) {
        $content = [System.IO.File]::ReadAllText($file)
        if (-not $content.Contains("SUPER SKILL OS PROTOCOLS")) {
            [System.IO.File]::AppendAllText($file, $text)
            Write-Host "Upgraded: $file"
        } else {
            Write-Host "Already upgraded: $file"
        }
    } else {
        Write-Host "File not found: $file"
    }
}
