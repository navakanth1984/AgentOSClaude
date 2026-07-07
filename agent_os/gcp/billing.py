import logging
from typing import Dict, Any

logger = logging.getLogger(__name__)

# Basic token costs per 1k tokens (in USD)
PRICING_TABLE = {
    # Local Ollama is free
    "ollama_local": {"prompt": 0.0, "completion": 0.0},
    # Gemini AI Studio (Standard rates)
    "gemini_direct": {"prompt": 0.00015, "completion": 0.0006},
    # OpenRouter Gemini Flash alias
    "openrouter": {"prompt": 0.000075, "completion": 0.0003},
}

class BudgetManager:
    """
    Enforces daily budgets, tracks pricing metrics, and manages cost allocations.
    """

    def __init__(self, daily_budget_usd: float = 2.0):
        self.daily_budget_usd = daily_budget_usd
        self.accumulated_cost_usd = 0.0

    def estimate_cost(self, provider_id: str, prompt_tokens: int, completion_tokens: int) -> float:
        prices = PRICING_TABLE.get(provider_id, {"prompt": 0.0, "completion": 0.0})
        cost = (prompt_tokens / 1000.0) * prices["prompt"] + (completion_tokens / 1000.0) * prices["completion"]
        return cost

    def log_request(self, provider_id: str, prompt_tokens: int, completion_tokens: int):
        cost = self.estimate_cost(provider_id, prompt_tokens, completion_tokens)
        self.accumulated_cost_usd += cost
        logger.info(
            "Transaction logged",
            extra={
                "provider_id": provider_id,
                "cost": cost,
                "total_cost": self.accumulated_cost_usd,
            }
        )

    def is_under_budget(self) -> bool:
        return self.accumulated_cost_usd < self.daily_budget_usd
