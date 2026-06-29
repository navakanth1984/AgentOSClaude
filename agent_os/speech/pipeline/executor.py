import hashlib
import json
import os
from dataclasses import dataclass
from typing import Dict, Any, List

import dataclasses

def _default_encoder(obj):
    if hasattr(obj, "model_dump"):
        return obj.model_dump()
    elif dataclasses.is_dataclass(obj):
        return dataclasses.asdict(obj)
    elif hasattr(obj, "__dict__"):
        return obj.__dict__
    # Do NOT fall back to str(obj): repr/str can change between versions or embed
    # memory addresses, which would silently destabilize cache fingerprints and
    # corrupt cached artifacts. Fail loud so the unsupported type is fixed at the
    # boundary (add model_dump / make it a dataclass / serialize explicitly).
    raise TypeError(
        f"Cannot serialize object of type {type(obj).__name__!r} for the pipeline "
        f"cache/fingerprint. Provide a dataclass, a .model_dump(), or a JSON-native value."
    )

from agent_os.speech.schema.jobs import EventBus

@dataclass
class StageContext:
    project_dir: str
    cache_dir: str
    config: Dict[str, Any]
    artifacts: Dict[str, Any]  # name -> content/path
    metrics: Dict[str, Any]
    event_bus: EventBus = dataclasses.field(default_factory=EventBus)
    run_id: str = "run_default"

    def emit_event(self, event: Any) -> None:
        self.event_bus.publish(event)

class Executor:
    def __init__(self, dag, context: StageContext):
        self.dag = dag
        self.context = context
        os.makedirs(self.context.cache_dir, exist_ok=True)
    
    def _compute_fingerprint(self, stage_name: str, input_artifacts: Dict[str, Any], stage_version: str) -> str:
        # Create a copy of config and stringify non-serializable objects
        clean_config = {}
        for k, v in self.context.config.items():
            if k == "tts_engine":
                continue # Skip the engine instance itself
            if hasattr(v, "model_dump"):
                clean_config[k] = v.model_dump()
            elif hasattr(v, "__dict__"):
                clean_config[k] = v.__dict__
            else:
                clean_config[k] = v

        data = {
            "stage": stage_name,
            "version": stage_version,
            "config": clean_config,
            "inputs": input_artifacts
        }
        
        data_str = json.dumps(data, sort_keys=True, default=_default_encoder)
        return hashlib.sha256(data_str.encode('utf-8')).hexdigest()

    def print_ascii_visualization(self, execution_order: List[str]):
        print("\nPipeline Execution DAG:")
        print("=======================")
        for i, node_name in enumerate(execution_order):
            print(f"  [{node_name}]")
            if i < len(execution_order) - 1:
                print("      |")
                print("      v")
        print("=======================\n")

    def run(self):
        execution_order = self.dag.get_execution_order()
        self.print_ascii_visualization(execution_order)
        print(f"Execution order: {execution_order}")
        
        for node_name in execution_order:
            stage = self.dag.nodes[node_name]
            
            # Gather inputs for this stage (based on dependencies)
            deps = self.dag.dependencies[node_name]
            input_artifacts = {dep: self.context.artifacts[dep] for dep in deps if dep in self.context.artifacts}
            
            # Compute fingerprint
            fingerprint = self._compute_fingerprint(node_name, input_artifacts, getattr(stage, "version", "1.0"))
            cache_file = os.path.join(self.context.cache_dir, f"{fingerprint}.json")
            
            print(f"[{node_name}] Fingerprint: {fingerprint}")
            
            if os.path.exists(cache_file):
                print(f"[{node_name}] CACHE HIT! Skipping execution.")
                with open(cache_file, 'r') as f:
                    output = json.load(f)
                self.context.artifacts[node_name] = output
            else:
                print(f"[{node_name}] Executing...")
                output = stage.run(self.context, input_artifacts)
                self.context.artifacts[node_name] = output
                
                # Save to cache
                with open(cache_file, 'w') as f:
                    json.dump(output, f, default=_default_encoder)
                print(f"[{node_name}] Execution complete and cached.")
