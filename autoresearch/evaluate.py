# evaluate.py — DO NOT MODIFY
# This is the scoring function. The agent must never touch this file.
# Modifying it would let the agent cheat by redefining what "success" means.

import json
import re
import anthropic
from datetime import date
from pathlib import Path
from train import get_prompt

TODAY = date.today().isoformat()
client = anthropic.Anthropic()
VAULT_ROOT = Path(r"C:\Users\navka\OneDrive\Documents\Obsidian Vault")

with open("test_inputs.json") as f:
    TEST_CASES = json.load(f)


def build_vault_tags() -> set[str]:
    """Scan all vault notes and collect every tag that exists."""
    vault_tags = set()
    for md_file in VAULT_ROOT.rglob("*.md"):
        try:
            content = md_file.read_text(encoding="utf-8", errors="ignore")
            match = re.search(r"tags:\s*\[([^\]]+)\]", content)
            if match:
                for tag in match.group(1).split(","):
                    vault_tags.add(tag.strip().strip('"').strip("'").lower())
        except Exception:
            continue
    return vault_tags


VAULT_TAGS = build_vault_tags()  # built once at import time


def score_structure(note: str) -> tuple[int, list[str]]:
    """Score 0-40 based on structural compliance with the vault format."""
    score = 0
    reasons = []

    # Frontmatter block (10 pts)
    if re.search(r"^---\n.*?\n---", note, re.DOTALL | re.MULTILINE):
        score += 10
    else:
        reasons.append("missing frontmatter block")

    # Required frontmatter fields (6 pts total, 2 each)
    for field in ["date:", "tags:", "project:", "source:"]:
        if field in note:
            score += 1.5
        else:
            reasons.append(f"missing frontmatter field: {field}")

    # Has a title (# heading) (5 pts)
    if re.search(r"^# .+", note, re.MULTILINE):
        score += 5
    else:
        reasons.append("missing # title")

    # Has Key Idea section (5 pts)
    if "## Key Idea" in note:
        score += 5
    else:
        reasons.append("missing ## Key Idea section")

    # Has Details section (5 pts)
    if "## Details" in note:
        score += 5
    else:
        reasons.append("missing ## Details section")

    # Has Action / Next Steps with a checkbox (5 pts)
    if re.search(r"- \[ \]", note):
        score += 5
    else:
        reasons.append("missing checkbox action item")

    return int(score), reasons


def score_length(note: str) -> tuple[int, str]:
    """Score 0-20 based on word count (target: 150-400 words)."""
    words = len(note.split())
    if 150 <= words <= 400:
        return 20, f"good length ({words} words)"
    elif 100 <= words < 150 or 400 < words <= 500:
        return 10, f"acceptable length ({words} words)"
    elif words < 100:
        return 0, f"too short ({words} words)"
    else:
        return 5, f"too long ({words} words)"


def score_tag_relevance(note: str, expected_tags: list[str]) -> tuple[int, str]:
    """Score 0-10 based on how many expected topic words appear in the note."""
    note_lower = note.lower()
    matched = sum(1 for tag in expected_tags if tag.lower().replace("-", " ") in note_lower or tag.lower() in note_lower)
    ratio = matched / len(expected_tags)
    score = int(ratio * 10)
    return score, f"{matched}/{len(expected_tags)} expected topics matched"


def score_tag_consistency(note: str) -> tuple[int, str]:
    """Score 0-10 based on how many of the note's tags already exist in the vault.
    Rewards prompts that generate reusable, consistent tags — which improves
    related-note linking over time."""
    match = re.search(r"tags:\s*\[([^\]]+)\]", note)
    if not match:
        return 0, "no tags found"

    note_tags = [t.strip().strip('"').strip("'").lower() for t in match.group(1).split(",")]
    if not note_tags:
        return 0, "empty tags"

    matched = sum(1 for t in note_tags if t in VAULT_TAGS)
    ratio = matched / len(note_tags)
    score = int(ratio * 10)
    return score, f"{matched}/{len(note_tags)} tags reuse existing vault tags"


def score_quality(note: str, raw_input: str) -> tuple[int, str]:
    """Score 0-20 using an LLM judge on overall note quality."""
    judge_prompt = f"""Rate this Obsidian vault note on a scale of 0 to 20.

Source material:
{raw_input[:600]}

Generated note:
{note[:800]}

Score based on:
- Does the Key Idea capture the actual core insight? (not generic filler)
- Are the Details specific and useful?
- Is the Action item concrete and actionable?
- Would this note be worth keeping in a personal knowledge base?

Reply with ONLY a single integer from 0 to 20. Nothing else."""

    try:
        result = client.messages.create(
            model="claude-haiku-4-5-20251001",
            max_tokens=5,
            messages=[{"role": "user", "content": judge_prompt}]
        )
        score = int(re.search(r"\d+", result.content[0].text).group())
        return min(score, 20), "llm-judge score"
    except Exception as e:
        return 0, f"judge failed: {e}"


def evaluate_single(test_case: dict) -> dict:
    """Run one test case and return its score breakdown."""
    prompt = get_prompt(today=TODAY)

    response = client.messages.create(
        model="claude-haiku-4-5-20251001",
        max_tokens=600,
        system=prompt,
        messages=[{"role": "user", "content": test_case["raw_input"]}]
    )
    note = response.content[0].text.strip()

    struct_score, struct_reasons = score_structure(note)
    length_score, length_reason = score_length(note)
    tag_score, tag_reason = score_tag_relevance(note, test_case["expected_tags"])
    consistency_score, consistency_reason = score_tag_consistency(note)
    quality_score, quality_reason = score_quality(note, test_case["raw_input"])

    total = struct_score + length_score + tag_score + consistency_score + quality_score

    return {
        "id": test_case["id"],
        "total": total,
        "breakdown": {
            "structure": struct_score,
            "length": length_score,
            "tag_relevance": tag_score,
            "tag_consistency": consistency_score,
            "quality": quality_score,
        },
        "notes": struct_reasons + [length_reason, tag_reason, consistency_reason, quality_reason],
        "generated_note": note,
    }


def run_evaluation(verbose: bool = True) -> float:
    """Evaluate all test cases and return average score (0-100)."""
    scores = []

    for tc in TEST_CASES:
        result = evaluate_single(tc)
        scores.append(result["total"])

        if verbose:
            print(f"\n[{result['id']}] Score: {result['total']}/100")
            print(f"  Structure:       {result['breakdown']['structure']}/40")
            print(f"  Length:          {result['breakdown']['length']}/20")
            print(f"  Tag relevance:   {result['breakdown']['tag_relevance']}/10")
            print(f"  Tag consistency: {result['breakdown']['tag_consistency']}/10")
            print(f"  Quality:         {result['breakdown']['quality']}/20")
            if result["notes"]:
                print(f"  Notes:     {'; '.join(result['notes'])}")

    avg = sum(scores) / len(scores)
    print(f"\nSCORE: {avg:.1f}")
    return avg


if __name__ == "__main__":
    run_evaluation(verbose=True)
