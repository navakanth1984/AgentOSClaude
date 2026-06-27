"""Regression test: the executor's CACHE-HIT (warm) path must reconstruct
dataclass artifacts so downstream stages can use attribute access.

This guards the bug where route -> synthesize/trim/merge crashed with
'dict has no attribute ...' on the second run, because only the cold path
(live in-memory dataclasses) was ever exercised by the acceptance run.

Runs with no TTS engine / no network.
"""
import os
import shutil
import tempfile

from agent_os.speech.pipeline.graph import DAG
from agent_os.speech.pipeline.executor import Executor, StageContext
from agent_os.speech.schema.models import (
    ExecutionPlanEntry, EngineName, Language, ensure_execution_plan,
)


class PlanStage:
    """Emits a list of ExecutionPlanEntry dataclasses (like RouteStage)."""
    version = "1.0"

    def run(self, context, inputs):
        entry = ExecutionPlanEntry(
            chunk_id=1, chapter_id="c1", text="Hello.", engine=EngineName.KOKORO,
            voice="af", language=Language.EN, speed=1.0, pitch=1.0, volume_gain_db=0.0,
            cache_key="k1", expected_output_path="out.wav", pause_before_ms=0,
            pause_after_ms=0, status="pending",
        )
        return {"execution_plan": [entry]}


class ConsumerStage:
    """Consumes the plan via attribute access (like SynthesizeStage)."""
    version = "1.0"

    def run(self, context, inputs):
        plan = ensure_execution_plan(inputs["plan"]["execution_plan"])
        # The line that crashed on a cache hit before ensure_execution_plan existed.
        paths = [e.expected_output_path for e in plan]
        assert all(isinstance(e, ExecutionPlanEntry) for e in plan)
        return {"paths": paths}


def main():
    cache_dir = tempfile.mkdtemp(prefix="warm_cache_test_")
    try:
        dag = DAG()
        dag.add_node("plan", PlanStage())
        dag.add_node("consume", ConsumerStage(), depends_on=["plan"])

        ctx = StageContext(project_dir=cache_dir, cache_dir=cache_dir,
                           config={}, artifacts={}, metrics={})

        print("=== COLD RUN (writes cache) ===")
        Executor(dag, ctx).run()
        assert ctx.artifacts["consume"]["paths"] == ["out.wav"]

        print("\n=== WARM RUN (reads cache -> the path that used to crash) ===")
        ctx.artifacts = {}
        Executor(dag, ctx).run()
        assert ctx.artifacts["consume"]["paths"] == ["out.wav"]

        print("\nPASS: warm cache-hit path reconstructs dataclasses correctly.")
    finally:
        shutil.rmtree(cache_dir, ignore_errors=True)


if __name__ == "__main__":
    main()
