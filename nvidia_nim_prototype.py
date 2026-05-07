import os
from openai import OpenAI
from dotenv import load_dotenv
from pathlib import Path

def get_client():
    env_path = Path("c:/Users/navka/navakanth001/.env")
    load_dotenv(dotenv_path=env_path)
    
    api_key = os.getenv("NVIDIA_API_KEY")
    if not api_key:
        raise ValueError("NVIDIA_API_KEY not found in .env")

    client = OpenAI(
        base_url="https://integrate.api.nvidia.com/v1",
        api_key=api_key
    )
    return client

import json
import base64

def get_image_base64(image_path):
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode('utf-8')

class BudgetMonitor:
    def __init__(self, threshold=5000, log_file="nim_usage_log.json"):
        self.threshold = threshold
        self.log_file = Path(log_file)
        self.cumulative_usage = self._load_usage()

    def _load_usage(self):
        if self.log_file.exists():
            with open(self.log_file, "r") as f:
                return json.load(f)
        return {"total_tokens": 0, "calls": 0}

    def _save_usage(self):
        with open(self.log_file, "w") as f:
            json.dump(self.cumulative_usage, f, indent=2)

    def log_call(self, usage, model):
        total = usage.total_tokens
        self.cumulative_usage["total_tokens"] += total
        self.cumulative_usage["calls"] += 1
        self._save_usage()

        print(f"\n📊 QUOTA & USAGE:")
        print(f"  - Prompt Tokens: {usage.prompt_tokens}")
        print(f"  - Completion Tokens: {usage.completion_tokens}")
        print(f"  - Total Tokens: {total}")
        print(f"  - Model: {model}")
        print(f"  - Cumulative Total: {self.cumulative_usage['total_tokens']}")

        if total > self.threshold:
            print(f"\n⚠️  BUDGET ALERT: This call used {total} tokens, which exceeds your threshold of {self.threshold}!")

def chat_prototype(model="nvidia/llama-3.3-nemotron-super-49b-v1.5", prompt="Write a short poem about GPU-accelerated AI.", budget_threshold=5000):
    print(f"🚀 Prototyping Chat with {model}...")
    client = get_client()
    monitor = BudgetMonitor(threshold=budget_threshold)
    
    completion = client.chat.completions.create(
        model=model,
        messages=[{"role": "user", "content": prompt}],
        temperature=0.2,
        top_p=0.7,
        max_tokens=1024,
        stream=True,
        stream_options={"include_usage": True}
    )

    print("\n--- Response ---\n")
    usage = None
    for chunk in completion:
        if chunk.choices and chunk.choices[0].delta.content is not None:
            print(chunk.choices[0].delta.content, end="", flush=True)
        if chunk.usage:
            usage = chunk.usage
    print("\n\n--- End of Response ---")
    
    if usage:
        monitor.log_call(usage, model)

def vision_prototype(model="nvidia/llama-3.1-nemotron-nano-vl-8b-v1", image_path="scene1_plate.jpg", prompt="Describe this scene in detail.", budget_threshold=5000):
    print(f"🚀 Prototyping Vision with {model}...")
    client = get_client()
    monitor = BudgetMonitor(threshold=budget_threshold)
    
    if os.path.exists(image_path):
        print(f"📦 Encoding local image: {image_path}")
        image_base64 = get_image_base64(image_path)
        image_content = {"url": f"data:image/jpeg;base64,{image_base64}"}
    else:
        print(f"🌐 Using fallback URL (assuming it exists or was provided)")
        image_content = {"url": image_path}

    completion = client.chat.completions.create(
        model=model,
        messages=[
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": prompt},
                    {"type": "image_url", "image_url": image_content}
                ]
            }
        ],
        max_tokens=1024,
        stream=True,
        stream_options={"include_usage": True}
    )

    print("\n--- Response ---\n")
    usage = None
    for chunk in completion:
        if chunk.choices and chunk.choices[0].delta.content is not None:
            print(chunk.choices[0].delta.content, end="", flush=True)
        if chunk.usage:
            usage = chunk.usage
    print("\n\n--- End of Response ---")

    if usage:
        monitor.log_call(usage, model)

if __name__ == "__main__":
    import sys
    
    threshold = int(sys.argv[2]) if len(sys.argv) > 2 else 5000
    
    if len(sys.argv) > 1 and sys.argv[1] == "vision":
        vision_prototype(budget_threshold=threshold)
    else:
        chat_prototype(budget_threshold=threshold)
