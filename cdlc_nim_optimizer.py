import os
import time
from openai import OpenAI
from dotenv import load_dotenv
from pathlib import Path

# Load environment
env_path = Path("c:/Users/navka/navakanth001/.env")
load_dotenv(dotenv_path=env_path)

class CDLC_Optimizer:
    def __init__(self, base_url="https://integrate.api.nvidia.com/v1"):
        self.client = OpenAI(base_url=base_url, api_key=os.getenv("NVIDIA_API_KEY"))

    def run_engineered_test(self, model, system_prompt, user_prompt):
        """Runs a test using CDLC Phase 1 'Generated' Context."""
        print(f"\n🚀 [CDLC PHASE 1] Model: {model}")
        start_time = time.time()
        try:
            completion = self.client.chat.completions.create(
                model=model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.1,
                max_tokens=2048
            )
            duration = time.time() - start_time
            content = completion.choices[0].message.content
            print(f"✅ Completed in {duration:.2f}s")
            return content
        except Exception as e:
            return f"❌ Error: {e}"

if __name__ == "__main__":
    optimizer = CDLC_Optimizer()
    
    # Context from nim_context_packages.md
    reasoning_system = """You are an Elite Systems Engineer and Logical Architect. Follow the L.O.G.I.C. Framework:
    1. L - List Variables
    2. O - Observe Constraints
    3. G - Generate Hypotheses
    4. I - Internal Validation
    5. C - Conclude"""
    
    puzzle_prompt = "A room contains 3 light bulbs and 3 switches outside the room. Each switch controls one bulb. You can only enter the room once. How do you determine which switch controls which bulb?"

    # Testing the 8B model with Engineered Context
    model_8b = "meta/llama-3.1-8b-instruct"
    print("\n--- Testing 8B Model with Engineered Context ---")
    result_8b = optimizer.run_engineered_test(model_8b, reasoning_system, puzzle_prompt)
    print(result_8b)
