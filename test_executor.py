import os
import shutil
from agent_os.speech.pipeline.graph import DAG
from agent_os.speech.pipeline.executor import Executor, StageContext

class NormalizeStage:
    version = "1.0"
    def run(self, context: StageContext, inputs: dict):
        text = context.config.get("input_text", "")
        return {"normalized": text.strip().lower()}

class ParseStage:
    version = "1.0"
    def run(self, context: StageContext, inputs: dict):
        normalized = inputs.get("normalize", {}).get("normalized", "")
        return {"words": normalized.split()}

class CountStage:
    version = "1.0"
    def run(self, context: StageContext, inputs: dict):
        words = inputs.get("parse", {}).get("words", [])
        return {"count": len(words)}

def main():
    # Cleanup previous tests
    if os.path.exists("test_cache"):
        shutil.rmtree("test_cache")
        
    dag = DAG()
    dag.add_node("normalize", NormalizeStage())
    dag.add_node("parse", ParseStage(), depends_on=["normalize"])
    dag.add_node("count", CountStage(), depends_on=["parse"])
    
    context = StageContext(
        project_dir="test_project",
        cache_dir="test_cache",
        config={"input_text": "  Hello World! Agent OS is great.  "},
        artifacts={},
        metrics={}
    )
    
    executor = Executor(dag, context)
    print("\n=== FIRST RUN ===")
    executor.run()
    print("Result:", context.artifacts["count"])
    
    print("\n=== SECOND RUN (Should skip all via cache hits) ===")
    context.artifacts = {} # reset artifacts in memory
    executor.run()
    
    print("\n=== THIRD RUN (Change config, should re-run all) ===")
    context.config["input_text"] = "Different text entirely!"
    context.artifacts = {}
    executor.run()
    print("Result:", context.artifacts["count"])

if __name__ == "__main__":
    main()
