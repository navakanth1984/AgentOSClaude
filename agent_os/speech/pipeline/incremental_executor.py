import time
import os
import json
from typing import Dict, Any, List
from collections import defaultdict
from pathlib import Path
import soundfile as sf

from agent_os.speech.pipeline.executor import StageContext, Executor
from agent_os.speech.pipeline.graph import DAG
from agent_os.speech.schema.models import ExecutionPlanEntry, ensure_execution_plan
from agent_os.speech.schema.events import (
    PipelineStarted, ChunkStarted, ChunkSynthesized, ChunkTrimmed,
    ChapterProgress, ChapterCompleted, PipelineCompleted
)

class IncrementalExecutor:
    def __init__(self, dag: DAG, context: StageContext):
        self.dag = dag
        self.context = context
        os.makedirs(self.context.cache_dir, exist_ok=True)

    def run(self) -> None:
        if not self.context.run_id or self.context.run_id == "run_default":
            import uuid
            self.context.run_id = str(uuid.uuid4())
        run_id = self.context.run_id
        
        # Start Pipeline Event
        self.context.emit_event(PipelineStarted(run_id=run_id, timestamp=time.time()))
        
        # 1. Run parsing, segmenting, routing upfront
        # We find their order in DAG.
        execution_order = self.dag.get_execution_order()
        
        pre_loop_stages = []
        loop_stages = []
        
        # Synthesize, Trim, Append are part of the incremental loop.
        # Parse, Segment, Context, Route are run upfront.
        for node in execution_order:
            if node in ["synthesize", "trim", "append", "merge"]:
                loop_stages.append(node)
            else:
                pre_loop_stages.append(node)
                
        print(f"[IncrementalExecutor] Upfront stages: {pre_loop_stages}")
        print(f"[IncrementalExecutor] Incremental loop stages: {loop_stages}")
        
        # Run upfront stages
        for node_name in pre_loop_stages:
            stage = self.dag.nodes[node_name]
            deps = self.dag.dependencies[node_name]
            input_artifacts = {dep: self.context.artifacts[dep] for dep in deps if dep in self.context.artifacts}
            
            print(f"[{node_name}] Executing upfront...")
            output = stage.run(self.context, input_artifacts)
            self.context.artifacts[node_name] = output

        # Identify route output
        route_output = self.context.artifacts.get("route")
        if not route_output or "execution_plan" not in route_output:
            raise RuntimeError("RouteStage must output an execution_plan.")
            
        full_plan: List[ExecutionPlanEntry] = ensure_execution_plan(route_output["execution_plan"])
        total_chunks = len(full_plan)
        
        # Setup tracking
        chapter_chunks = defaultdict(list)
        for entry in full_plan:
            chapter_chunks[entry.chapter_id].append(entry)
            
        chapter_totals = {cid: len(entries) for cid, entries in chapter_chunks.items()}
        chapter_completed = defaultdict(int)
        
        pipeline_start_time = time.time()

        # Clean up existing final chapter audio files to ensure clean idempotency on resume
        for chapter_id in chapter_totals.keys():
            out_file = Path(self.context.project_dir) / f"Chapter_{chapter_id}.wav"
            if out_file.exists():
                try:
                    out_file.unlink()
                except Exception:
                    pass

        # Run chunk by chunk incremental loop
        # We run Synthesize -> Trim -> Append per chunk.
        synthesize_stage = self.dag.nodes.get("synthesize")
        trim_stage = self.dag.nodes.get("trim")
        append_stage = self.dag.nodes.get("append")
        
        if not (synthesize_stage and trim_stage and append_stage):
            raise RuntimeError("IncrementalExecutor requires synthesize, trim, and append stages in DAG.")

        for entry in full_plan:
            # Cooperative cancellation check
            from agent_os.speech.schema.jobs import SpeechJobStore, JobState
            current_job = SpeechJobStore.load(run_id)
            if current_job and current_job.state == JobState.CANCELLED:
                print(f"[IncrementalExecutor] Cooperative cancellation requested. Halting loop.")
                break

            chunk_id = entry.chunk_id
            chapter_id = entry.chapter_id
            
            # Emit ChunkStarted event
            self.context.emit_event(ChunkStarted(run_id=run_id, timestamp=time.time(), chunk_id=chunk_id))
            
            # 1. Synthesize single chunk
            print(f"[IncrementalExecutor] Synthesizing chunk {chunk_id}...")
            # We mock the input route for this single chunk
            single_route = {"execution_plan": [entry]}
            synth_result = synthesize_stage.run(self.context, {"route": single_route})
            
            # Emit ChunkSynthesized event
            # Read output path to get details
            synth_entry = ensure_execution_plan(synth_result["execution_plan"])[0]
            sample_rate = 24000
            duration = 0.0
            try:
                info = sf.info(synth_entry.expected_output_path)
                sample_rate = info.samplerate
                duration = info.duration
            except Exception:
                pass
                
            self.context.emit_event(ChunkSynthesized(
                run_id=run_id, timestamp=time.time(),
                chunk_id=chunk_id, sample_rate=sample_rate, duration_sec=duration
            ))
            
            # 2. Trim single chunk
            print(f"[IncrementalExecutor] Trimming chunk {chunk_id}...")
            trim_result = trim_stage.run(self.context, {"synthesize": synth_result})
            
            trim_entry = ensure_execution_plan(trim_result["execution_plan"])[0]
            trimmed_duration = 0.0
            try:
                info = sf.info(trim_entry.expected_output_path)
                trimmed_duration = info.duration
            except Exception:
                pass
                
            self.context.emit_event(ChunkTrimmed(
                run_id=run_id, timestamp=time.time(),
                chunk_id=chunk_id, duration_sec=trimmed_duration
            ))
            
            # 3. Append single chunk (this emits ChunkAppended internally)
            print(f"[IncrementalExecutor] Appending chunk {chunk_id}...")
            append_stage.run(self.context, {"trim": trim_result})
            
            # Progress reporting
            chapter_completed[chapter_id] += 1
            self.context.emit_event(ChapterProgress(
                run_id=run_id, timestamp=time.time(),
                chapter_id=chapter_id,
                completed_chunks=chapter_completed[chapter_id],
                total_chunks=chapter_totals[chapter_id]
            ))
            
            # If chapter complete, emit ChapterCompleted
            if chapter_completed[chapter_id] == chapter_totals[chapter_id]:
                output_path = Path(self.context.project_dir) / f"Chapter_{chapter_id}.wav"
                self.context.emit_event(ChapterCompleted(
                    run_id=run_id, timestamp=time.time(),
                    chapter_id=chapter_id, output_path=str(output_path)
                ))

        # Pipeline complete
        total_pipeline_time = time.time() - pipeline_start_time
        self.context.emit_event(PipelineCompleted(
            run_id=run_id, timestamp=time.time(),
            total_duration_sec=total_pipeline_time
        ))
        print("[IncrementalExecutor] Complete.")
