"""ExecutionMode — the set of orchestration strategies an ExecutionRequest can pick."""

from enum import Enum


class ExecutionMode(str, Enum):
    SINGLE = "single"     # one model, one call — wraps existing call_openrouter path
    SWARM = "swarm"        # existing 5-role parallel research swarm (agent_os/swarm.py)
    MIXTURE = "mixture"     # parallel fan-out across N models + aggregation (MoA)
    DEBATE = "debate"        # stub — not implemented this pass (see Phase 2)
    AUTO = "auto"             # stub — not implemented this pass (see Phase 3)
