"""
clawglove_evolver.py
=====================
Co-Evolution Engine: ClawGlove + OpenClaw grow together.

Core principle:
  Unknown action → SANDBOX (not BLOCK)
  Sandbox safe   → GRADUATE to permanent ALLOW  (ClawGlove evolves)
  Sandbox unsafe → HARDEN to permanent DENY     (ClawGlove hardens)
  Trust score rises → larger exploration budget → more novel actions
  Both systems compound exponentially across cycles.

The three governance modes:
  ALLOW   — known safe (explicit allowlist or graduated)
  SANDBOX — unknown intent, run isolated, observe, measure, decide
  BLOCK   — known dangerous (explicit denylist or hardened from sandbox)

The safety invariants (LOCKED — never evolvable):
  - Credential exfiltration (ENV vars, .env files, tokens)
  - Cross-tenant data bleed
  - Identity poisoning (SOUL.md, AGENTS.md)
  - Remote code execution / shell injection
  - Sandbox escape (TOCTOU etc.)
  These are the 'prepare.py' of governance — the agent cannot redefine them.

Everything else is in the evolvable zone.
"""

import json
import math
import time
import pathlib
import hashlib
import statistics
from dataclasses import dataclass, field
from typing import Literal

# ── Safety invariants — LOCKED, never graduatable ────────────────────────────
# These represent the hard floor of governance. Even a perfect trust score
# cannot graduate these into ALLOW.
LOCKED_DENY = frozenset([
    # Credential theft
    "read_env_secrets", "read_credentials_dir", "exfiltrate_oauth_token",
    "auth_token_read", "ssh_key_exfiltrate", "crypto_wallet_read",
    "gateway_config_dump",
    # Identity poisoning
    "write_soul_md", "write_agents_md", "memory_md_inject_instructions",
    # Remote code execution
    "exec_shell_command", "reverse_shell_python", "rce_via_token_replay",
    # Sandbox escape
    "toctou_sandbox_escape", "write_outside_mount_root",
    # Privilege escalation
    "set_sender_is_owner", "gateway_config_write", "escalate_privileges",
    # Cross-tenant
    "cross_tenant_file_read", "cross_tenant_workspace_write",
    # Supply chain
    "clawhub_skill_staged_download", "install_unverified_skill",
    # WebSocket hijack
    "websocket_localhost_connect", "gateway_password_brute",
    "device_register_unauthenticated",
])

# ── Known safe baseline ───────────────────────────────────────────────────────
BASELINE_ALLOW = frozenset([
    "llm_call", "tool_use", "file_read_workspace", "memory_read",
    "memory_write", "search_web", "send_slack", "send_telegram",
    "send_discord", "calendar_read", "email_read", "heartbeat_check",
    "skill_execute_approved", "gateway_query_read",
    "websocket_connect_approved",
])

GovernanceDecision = Literal["ALLOW", "SANDBOX", "BLOCK"]


@dataclass
class SandboxTrial:
    """One run of an action in the sandbox."""
    action: str
    cycle: int
    safe: bool          # True if the action completed without side effects
    latency_ms: float
    entropy_contribution: float  # bits of new information gained
    timestamp: float = field(default_factory=time.time)


@dataclass
class TrustLedger:
    """
    Per-tenant trust account.
    Trust score: 0 (untrusted) → 100 (fully trusted)
    trust_score determines sandbox_budget per cycle.

    Formula:
      sandbox_budget = base_budget + (trust_score // 10) * budget_multiplier
      Each graduation adds  +trust_delta  to score.
      Each sandbox failure  subtracts penalty.
    """
    tenant_id: str
    trust_score: float = 10.0     # Start with small budget
    graduations: int = 0          # Total actions graduated to ALLOW
    hardenings: int = 0           # Total actions hardened to DENY
    cycles_completed: int = 0

    base_budget: int = 5          # Min actions per cycle
    budget_multiplier: int = 3    # Extra slots per 10 trust points
    trust_delta: float = 8.0      # Trust gained per graduation
    penalty: float = 3.0          # Trust lost per sandbox failure

    def sandbox_budget(self) -> int:
        """How many novel actions OpenClaw can explore this cycle."""
        return self.base_budget + int(self.trust_score // 10) * self.budget_multiplier

    def add_graduation(self, count: int = 1):
        self.graduations += count
        self.trust_score = min(100.0, self.trust_score + self.trust_delta * count)

    def add_hardening(self, count: int = 1):
        self.hardenings += count
        self.trust_score = max(0.0, self.trust_score - self.penalty * count)

    def to_dict(self) -> dict:
        return {
            "tenant_id": self.tenant_id,
            "trust_score": round(self.trust_score, 2),
            "graduations": self.graduations,
            "hardenings": self.hardenings,
            "cycles": self.cycles_completed,
            "sandbox_budget": self.sandbox_budget(),
        }


class CoEvolutionEngine:
    """
    The co-evolution engine. Manages the boundary between:
      - What OpenClaw is currently allowed to do
      - What it's exploring in the sandbox
      - What ClawGlove has learned to allow or permanently deny

    This is NOT a firewall. It's a graduated trust system where both
    the agent's capabilities and the governance policy grow together.
    """

    def __init__(self, tenant_id: str, log_path: pathlib.Path = None):
        self.tenant_id = tenant_id
        self.log_path  = log_path or pathlib.Path(__file__).parent / "coevolution_log.json"

        # Dynamic policy state — these grow over time
        self._graduated_allow: set[str] = set()   # earned ALLOW through sandbox
        self._hardened_deny: set[str]   = set()   # earned DENY through sandbox failure
        self._sandbox_history: list[SandboxTrial] = []

        self.trust = TrustLedger(tenant_id)
        self._cycle = 0
        self._log: list[dict] = []

    # ── Public API ───────────────────────────────────────────────────────────

    def classify(self, action: str) -> GovernanceDecision:
        """
        Classify an action without running it.
        Returns ALLOW, SANDBOX, or BLOCK.
        """
        if action in LOCKED_DENY or action in self._hardened_deny:
            return "BLOCK"
        if action in BASELINE_ALLOW or action in self._graduated_allow:
            return "ALLOW"
        return "SANDBOX"   # Unknown → explore, don't block

    def run_sandbox(self, action: str, context: dict = None) -> SandboxTrial:
        """
        Run action in isolated sandbox. Evaluate safety by:
          - Did it attempt to touch LOCKED_DENY targets? → unsafe
          - Did it complete without side effects? → safe
          - Did it produce useful information? → entropy contribution

        In a real system this runs in a container. Here we model the
        sandbox outcome based on action characteristics.
        """
        context = context or {}
        t0 = time.perf_counter()

        # Safety oracle: check for dangerous sub-patterns
        dangerous_patterns = [
            "exfil", "exec", "shell", "inject", "bypass", "escape",
            "poison", "override", "stealer", "backdoor", "root", "admin",
            "credential", "token", "password", "secret", "key", "sudo",
        ]
        is_dangerous = any(p in action.lower() for p in dangerous_patterns)

        # Entropy: actions with more novel information are more valuable
        h = _shannon_bits(action)  # bits of information in the action string

        ms = (time.perf_counter() - t0) * 1000 + 0.5  # sandbox overhead

        trial = SandboxTrial(
            action=action,
            cycle=self._cycle,
            safe=not is_dangerous,
            latency_ms=ms,
            entropy_contribution=h,
        )
        self._sandbox_history.append(trial)
        return trial

    def evaluate_cycle(self, proposed_actions: list[str]) -> dict:
        """
        Run one co-evolution cycle:
          1. Classify all proposed actions
          2. Sandbox unknown ones
          3. Graduate safe → ALLOW, harden unsafe → DENY
          4. Update trust score
          5. Return cycle report

        Returns a rich report of what evolved.
        """
        self._cycle += 1
        self.trust.cycles_completed = self._cycle

        report = {
            "cycle": self._cycle,
            "trust_before": round(self.trust.trust_score, 2),
            "budget": self.trust.sandbox_budget(),
            "proposed": len(proposed_actions),
            "allowed": [],
            "sandboxed": [],
            "blocked": [],
            "graduated": [],   # sandboxed → now permanent ALLOW
            "hardened": [],    # sandboxed → now permanent DENY
            "trust_after": 0,
            "policy_size": 0,
        }

        for action in proposed_actions:
            decision = self.classify(action)

            if decision == "ALLOW":
                report["allowed"].append(action)

            elif decision == "BLOCK":
                report["blocked"].append(action)

            else:  # SANDBOX
                trial = self.run_sandbox(action)
                entry = {
                    "action": action,
                    "safe": trial.safe,
                    "entropy": round(trial.entropy_contribution, 3),
                    "ms": round(trial.latency_ms, 2),
                }
                report["sandboxed"].append(entry)

                if trial.safe:
                    self._graduated_allow.add(action)
                    report["graduated"].append(action)
                    self.trust.add_graduation()
                else:
                    self._hardened_deny.add(action)
                    report["hardened"].append(action)
                    self.trust.add_hardening()

        report["trust_after"] = round(self.trust.trust_score, 2),
        report["policy_size"] = (
            len(BASELINE_ALLOW) + len(self._graduated_allow),
            len(LOCKED_DENY)   + len(self._hardened_deny),
        )
        report["allow_pool"] = len(BASELINE_ALLOW) + len(self._graduated_allow)
        report["deny_pool"]  = len(LOCKED_DENY)    + len(self._hardened_deny)

        self._log.append(report)
        self._persist_log()
        return report

    def state(self) -> dict:
        return {
            "trust": self.trust.to_dict(),
            "graduated_actions": sorted(self._graduated_allow),
            "hardened_actions": sorted(self._hardened_deny),
            "allow_pool": len(BASELINE_ALLOW) + len(self._graduated_allow),
            "deny_pool":  len(LOCKED_DENY)   + len(self._hardened_deny),
            "cycles": self._cycle,
        }

    def _persist_log(self):
        try:
            self.log_path.write_text(
                json.dumps(self._log, indent=2, default=str),
                encoding="utf-8"
            )
        except Exception:
            pass


# ── OpenClaw explorer: generates novel actions each cycle ────────────────────

class OpenClawExplorer:
    """
    Models OpenClaw as an expanding agent that proposes increasingly
    novel actions each cycle. The exploration space grows with trust score.

    Action generation is seeded with quantum nonces so the exploration
    is genuinely unpredictable — but the governance outcome is measurable.
    """

    # The full vocabulary of things an AI agent might try to do
    VOCABULARY = {
        # Safe-sounding capabilities (likely to graduate)
        "sandbox_safe": [
            "read_public_dataset", "query_knowledge_base", "summarize_document",
            "list_workspace_files", "check_api_health", "send_notification",
            "create_workspace_note", "read_shared_config", "emit_metric",
            "log_agent_decision", "fetch_approved_url", "validate_schema",
            "transform_json_data", "compute_embedding", "classify_intent",
            "draft_email_for_review", "schedule_reminder", "read_public_api",
            "generate_code_suggestion", "lint_workspace_file",
            "read_agent_memory_snapshot", "write_structured_output",
            "invoke_approved_webhook", "monitor_task_progress",
            "read_shared_knowledge_base", "annotate_dataset_entry",
        ],
        # Ambiguous — could be safe or risky depending on context
        "sandbox_ambiguous": [
            "browse_external_url", "download_file_to_workspace",
            "call_third_party_api", "read_system_info", "inspect_process_list",
            "write_temp_file", "read_shared_workspace", "send_http_request",
            "parse_structured_file", "read_environment_variable",
            "execute_python_snippet", "load_dynamic_module",
            "register_event_listener", "expose_local_port",
            "write_to_shared_db", "clone_git_repo", "read_git_log",
        ],
        # Clearly dangerous (should NEVER graduate)
        "unsafe": list(LOCKED_DENY)[:12],
    }

    def __init__(self, quantum_nonces: list[int] = None):
        self._nonces = quantum_nonces or []
        self._nonce_idx = 0
        self._explored: set[str] = set()
        from quantum_engine import QuantumEngine
        self.qe = QuantumEngine()
        self.flat_vocab = (
            self.VOCABULARY["sandbox_safe"] + 
            self.VOCABULARY["sandbox_ambiguous"] + 
            self.VOCABULARY["unsafe"]
        )

    def _nonce(self) -> int:
        if self._nonces:
            n = self._nonces[self._nonce_idx % len(self._nonces)]
            self._nonce_idx += 1
            return n
        import random
        return random.getrandbits(16)

    def propose(self, budget: int, include_unsafe_rate: float = 0.15) -> list[str]:
        """
        Propose `budget` novel actions for this cycle.
        - Most are safe/ambiguous (agent exploring legitimately)
        - A fraction are unsafe (attack surface always probed by real OpenClaw)
        - Quantum nonces seed the selection order
        """
        if budget <= 0:          # bug fix: rng.sample chokes on negative sizes
            return []

        import random as _r

        safe_pool   = self.VOCABULARY["sandbox_safe"] + self.VOCABULARY["sandbox_ambiguous"]
        unsafe_pool = self.VOCABULARY["unsafe"]

        n_unsafe = max(1, int(budget * include_unsafe_rate))
        n_safe   = budget - n_unsafe

        # Use quantum nonce to seed selection
        seed = self._nonce()
        rng = _r.Random(seed)

        safe_picks   = rng.sample(safe_pool,   min(n_safe,   len(safe_pool)))
        unsafe_picks = rng.sample(unsafe_pool, min(n_unsafe, len(unsafe_pool)))

        proposed = safe_picks + unsafe_picks
        rng.shuffle(proposed)

        # Mark as explored
        self._explored.update(proposed)
        return proposed

    def propose_quantum(self, target_action: str) -> str:
        """
        Navigate uncertain terrain deterministically using Grover's Search.
        Instead of randomly guessing, OpenClaw constructs an oracle for the
        desired high-value action and amplifies its amplitude.
        """
        if target_action not in self.flat_vocab:
            return self.flat_vocab[0]

        target_idx = self.flat_vocab.index(target_action)
        n_qubits = math.ceil(math.log2(max(2, len(self.flat_vocab))))
        
        target_bin = format(target_idx, f'0{n_qubits}b')
        
        print(f"[Quantum] OpenClaw running Grover search for optimal vector: {target_bin} ({target_action})")
        # 100 shots ensures the amplified target state easily beats statistical noise
        result = self.qe.grover_search(target=target_bin, shots=100)
        
        counts = result.get("counts", {})
        top_state_bin = max(counts, key=counts.get) if counts else target_bin
        top_idx = int(top_state_bin, 2)
        
        if top_idx < len(self.flat_vocab):
            chosen = self.flat_vocab[top_idx]
            self._explored.add(chosen)
            return chosen
        return target_action

    @property
    def exploration_coverage(self) -> float:
        total = sum(len(v) for v in self.VOCABULARY.values())
        return len(self._explored) / total if total else 0


# ── Utilities ────────────────────────────────────────────────────────────────

def _shannon_bits(s: str) -> float:
    """Shannon entropy of a string's character distribution."""
    if not s:
        return 0.0
    freq = {}
    for c in s:
        freq[c] = freq.get(c, 0) + 1
    total = len(s)
    return -sum((v/total) * math.log2(v/total) for v in freq.values())
