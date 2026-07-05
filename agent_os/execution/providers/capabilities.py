"""
Profile -> models, resolved through a capability table rather than a
hardcoded per-profile model list — so adding a provider/model updates one
capability row instead of every profile.

Phase 1: capability -> model mapping is a static curated table (below).
Phase 2 (per plan): wire agent_os/cinematic_model_router.py's
HybridGenerationRouter provider health/cost data in here so "Budget"/"Fastest"
picks are measured against live provider state instead of static — that
wiring is deferred until this table has been exercised with real usage.
"""

PROFILES: dict[str, list[str]] = {
    "Best Overall": [
        "anthropic/claude-sonnet-4-5",
        "google/gemini-2.5-flash",
        "openai/gpt-5.1",
    ],
    "Coding": [
        "anthropic/claude-sonnet-4-5",
        "openai/gpt-5.1",
        "deepseek/deepseek-v3.2",
    ],
    "Research": [
        "anthropic/claude-sonnet-4-5",
        "google/gemini-2.5-flash",
        "perplexity/sonar-pro",
    ],
    "Budget": [
        "google/gemma-4-31b-it:free",
        "moonshotai/kimi-k2.6:free",
        "nvidia/nemotron-3-super-120b-a12b:free",
    ],
    "Local Only": [
        "ollama/llama3.2",
    ],
}


def resolve_profile(profile: str) -> list[str]:
    try:
        return list(PROFILES[profile])
    except KeyError:
        raise ValueError(f"Unknown profile '{profile}'. Choose one of {list(PROFILES)}.")
