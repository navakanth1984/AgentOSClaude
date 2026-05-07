import os
import time
import base64
from openai import OpenAI
from dotenv import load_dotenv
from pathlib import Path

# Load environment
env_path = Path("c:/Users/navka/navakanth001/.env")
load_dotenv(dotenv_path=env_path)

class NIMBench:
    def __init__(self, base_url="https://integrate.api.nvidia.com/v1"):
        self.client = OpenAI(base_url=base_url, api_key=os.getenv("NVIDIA_API_KEY"))

    def stress_test_reasoning(self, model, complexity_level=1):
        """Tests logical depth and multi-step reasoning."""
        prompts = {
            1: "If I have 3 apples and you have 2 oranges, and we swap one of each, but then a bird steals half of the fruit that was swapped, how much fruit do we each have left? Explain step by step.",
            2: "Analyze the potential socio-economic impact of a hypothetical discovery of room-temperature superconductors on the global energy market over the next 50 years. Address infrastructure, geopolitical shifts, and environmental impact.",
            3: "A room contains 3 light bulbs and 3 switches outside the room. Each switch controls one bulb. You can only enter the room once. How do you determine which switch controls which bulb using thermal properties and logical state changes?"
        }
        prompt = prompts.get(complexity_level, prompts[1])
        return self._run_test(model, "Reasoning", prompt)

    def stress_test_context(self, model, context_size="16k"):
        """Tests context retention and 'needle in a haystack' retrieval."""
        # Generating a 'haystack' of filler text
        haystack = "The quick brown fox jumps over the lazy dog. " * 1000 
        needle = "SECRET_KEY_NVIDIA_2026: 'Supercomputing is for everyone'."
        combined_context = f"{haystack[:len(haystack)//2]} {needle} {haystack[len(haystack)//2:]}"
        
        prompt = f"Within the following text, find the secret key and repeat it exactly: {combined_context}"
        return self._run_test(model, f"Context ({context_size})", prompt)

    def stress_test_coding(self, model):
        """Tests complex algorithmic generation and bug fixing."""
        prompt = """Write a highly optimized Python implementation of a distributed Raft consensus algorithm. 
        Focus on leader election and log replication. Include docstrings and handle edge cases like network partitions."""
        return self._run_test(model, "Coding", prompt)

    def _run_test(self, model, test_name, prompt):
        print(f"\n[TEST: {test_name}] Model: {model}")
        start_time = time.time()
        try:
            completion = self.client.chat.completions.create(
                model=model,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.1, # Low temp for deterministic limit testing
                max_tokens=2048
            )
            duration = time.time() - start_time
            content = completion.choices[0].message.content
            print(f"✅ Completed in {duration:.2f}s")
            return {
                "model": model,
                "test": test_name,
                "duration": duration,
                "output": content,
                "success": True
            }
        except Exception as e:
            print(f"❌ Failed: {e}")
            return {"model": model, "test": test_name, "success": False, "error": str(e)}

if __name__ == "__main__":
    bench = NIMBench()
    
    # Models to test (based on our earlier discovery)
    models_to_test = [
        "nvidia/llama-3.3-nemotron-super-49b-v1.5", # High reasoning
        "qwen/qwen2.5-coder-32b-instruct",          # Coding specialist
        "meta/llama-3.1-8b-instruct"                # Efficiency/Latency test
    ]
    
    results = []
    for model in models_to_test:
        print(f"\n{'='*50}\nEVALUATING: {model}\n{'='*50}")
        # Test Reasoning
        results.append(bench.stress_test_reasoning(model, complexity_level=3))
        # Test Coding
        results.append(bench.stress_test_coding(model))
        # Test Context (Small scale for API limits, but enough to see quality)
        results.append(bench.stress_test_context(model))

    # Summary of findings
    print(f"\n\n{'#'*50}\nFINAL SUMMARY\n{'#'*50}")
    for r in results:
        status = "PASS" if r['success'] else "FAIL"
        print(f"Model: {r['model']} | Test: {r['test']} | Status: {status} | Time: {r.get('duration', 0):.2f}s")
