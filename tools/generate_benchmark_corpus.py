"""Deterministic benchmark corpus generator.

Given a fixed seed and generator version, this emits byte-for-byte identical
corpus files. Regenerating in two years yields the same input unless the
generator version is intentionally bumped. Each paragraph is sized to stay under
the SegmentStage chunk limit (500 chars), so paragraphs ~= chunks.

Usage:
    python tools/generate_benchmark_corpus.py --tier smoke
    python tools/generate_benchmark_corpus.py --tier medium --out corpus/medium
    python tools/generate_benchmark_corpus.py --all
"""
import argparse
import hashlib
import json
import random
from pathlib import Path

GENERATOR_VERSION = "1.0"
SEED = 20260627

# Fixed vocabulary — changing this changes the generator version.
_WORDS = [
    "the", "river", "stone", "morning", "quiet", "traveller", "lantern", "field",
    "distant", "mountain", "whisper", "iron", "garden", "hollow", "amber", "tide",
    "north", "ember", "silver", "thread", "hour", "window", "winter", "harbor",
    "echo", "marble", "shadow", "willow", "copper", "meadow", "signal", "drift",
]

TIERS = {
    "smoke":  {"paragraphs": 5,    "sentences": (2, 3)},
    "medium": {"paragraphs": 100,  "sentences": (2, 4)},
    "large":  {"paragraphs": 1000, "sentences": (2, 4)},
}


def _sentence(rng: random.Random) -> str:
    n = rng.randint(6, 12)
    words = [rng.choice(_WORDS) for _ in range(n)]
    words[0] = words[0].capitalize()
    return " ".join(words) + rng.choice([".", ".", ".", "!", "?"])


def _paragraph(rng: random.Random, sent_range) -> str:
    n = rng.randint(*sent_range)
    para = " ".join(_sentence(rng) for _ in range(n))
    # Keep paragraphs under the 500-char chunk limit so each ~= one chunk.
    return para[:480].rstrip()


def generate(tier: str, out_dir: Path) -> dict:
    cfg = TIERS[tier]
    # Seed is tier-specific but fixed, so tiers differ yet each is reproducible.
    rng = random.Random(f"{SEED}:{GENERATOR_VERSION}:{tier}")
    paragraphs = [_paragraph(rng, cfg["sentences"]) for _ in range(cfg["paragraphs"])]
    corpus_text = "\n\n".join(paragraphs) + "\n"

    out_dir.mkdir(parents=True, exist_ok=True)
    corpus_path = out_dir / "chapter.txt"
    corpus_path.write_text(corpus_text, encoding="utf-8", newline="\n")

    sha = hashlib.sha256(corpus_text.encode("utf-8")).hexdigest()
    metadata = {
        "generator_version": GENERATOR_VERSION,
        "seed": SEED,
        "tier": tier,
        "paragraphs": cfg["paragraphs"],
        "target_chunks": cfg["paragraphs"],  # paragraphs ~= chunks (under 500 chars)
        "sentence_distribution": f"uniform{cfg['sentences']}",
        "sha256": sha,
        "corpus_file": "chapter.txt",
    }
    (out_dir / "metadata.json").write_text(
        json.dumps(metadata, indent=2) + "\n", encoding="utf-8", newline="\n"
    )
    return metadata


def main():
    ap = argparse.ArgumentParser(description="Generate deterministic benchmark corpora.")
    ap.add_argument("--tier", choices=list(TIERS), help="Which tier to generate.")
    ap.add_argument("--out", type=Path, help="Output directory (default: corpus/<tier>).")
    ap.add_argument("--all", action="store_true", help="Generate all tiers.")
    args = ap.parse_args()

    tiers = list(TIERS) if args.all else ([args.tier] if args.tier else [])
    if not tiers:
        ap.error("specify --tier <name> or --all")

    for tier in tiers:
        out = args.out if (args.out and not args.all) else Path("corpus") / tier
        meta = generate(tier, out)
        print(f"[{tier}] {meta['paragraphs']} paragraphs -> {out/'chapter.txt'} "
              f"(sha256 {meta['sha256'][:12]}...)")


if __name__ == "__main__":
    main()
