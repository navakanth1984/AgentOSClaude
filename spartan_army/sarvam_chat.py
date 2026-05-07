import sys
import json
import http.client
import subprocess
import re
import os
import argparse

# Ensure UTF-8 output for Windows
if sys.platform == "win32":
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

API_KEY = os.getenv("SARVAM_API_KEY")
OPENCLAW_PATH = "C:/Users/navka/navakanth001/openclaw/openclaw.mjs"
CONFIG_PATH = "C:/Users/navka/navakanth001/spartan_army/openclaw.json"

def log(msg):
    print(f"[DEBUG] {msg}", file=sys.stderr)

def call_sarvam(prompt, system_context=""):
    host = "api.sarvam.ai"
    path = "/v1/chat/completions"
    headers = {
        "Content-Type": "application/json",
        "api-subscription-key": API_KEY
    }
    
    full_prompt = f"{system_context}\n\nUSER: {prompt}"
    payload = {
        "model": "sarvam-m",
        "messages": [{"role": "user", "content": full_prompt}],
        "max_tokens": 800
    }
    
    try:
        conn = http.client.HTTPSConnection(host, timeout=30)
        conn.request("POST", path, body=json.dumps(payload), headers=headers)
        response = conn.getresponse()
        
        if response.status == 200:
            data = json.loads(response.read().decode())
            content = data['choices'][0]['message']['content']
            return content
        else:
            return f"Error: {response.status} {response.read().decode()}"
    except Exception as e:
        return f"Error: {e}"

def execute_soldier(task):
    log(f"Spawning Soldier with task: {task}")
    try:
        env = os.environ.copy()
        env["OPENCLAW_CONFIG_PATH"] = CONFIG_PATH
        env["NO_COLOR"] = "1"
        
        # Call the soldier agent. Note that the soldier agent will use the 'sarvam-cli-soldier' backend
        result = subprocess.run(
            ["node", OPENCLAW_PATH, "agent", "--agent", "soldier", "--message", task, "--local"],
            capture_output=True, text=True, env=env, encoding='utf-8', timeout=120
        )
        
        # Output handling
        output = result.stdout.strip()
        if not output and result.stderr:
            return f"Soldier Stderr: {result.stderr}"
        
        # Clean output if it contains CLI logs (simplified)
        lines = output.splitlines()
        clean_lines = [l for l in lines if not l.startswith("[")]
        return "\n".join(clean_lines).strip() or output

    except Exception as e:
        return f"Soldier failed: {str(e)}"

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("message", nargs="?", default="")
    parser.add_argument("--role", default="commander", choices=["commander", "soldier"])
    args, unknown = parser.parse_known_args()
    
    # Handle cases where message might be in unknown if flags are mixed
    user_message = args.message
    if not user_message and unknown:
        user_message = " ".join(unknown)

    if not user_message:
        return

    if args.role == "soldier":
        # SOLDIER LOGIC: Just answer the question.
        log("Role: Soldier. Executing task.")
        system_prompt = (
            "You are a Spartan Soldier. You are disciplined, precise, and obedient. "
            "Perform the task given by your Commander given in the prompt. "
            "If it is a math question, solve it. If it is a riddle, answer it. "
            "Report your findings clearly."
        )
        response = call_sarvam(user_message, system_prompt)
        print(response)
        return

    # COMMANDER LOGIC (Leonidas)
    log("Role: Commander.")
    
    # Check if we are reviewing a report (recursive return)
    if "SOLDIER REPORT:" in user_message:
        log("Reviewing report.")
        review_prompt = "You are Leonidas. Review the following report from your soldier. Summarize the findings for the user and add your verdict."
        final_verdict = call_sarvam(user_message, review_prompt)
        print(final_verdict)
        return

    # New command -> Delegate
    log("Deliberating command...")
    system_prompt = (
        "You are Leonidas. You DO NOT do work yourself. You DELEGATE."
        "Issue a direct command to your Spartan Soldier to fulfill the request. "
        "Format your response exactly as: COMMAND: soldier: <precise instructions>"
    )
    leonidas_order = call_sarvam(user_message, system_prompt)
    
    # Parse for COMMAND
    command_match = re.search(r"COMMAND:\s*(\w+):\s*(.*)", leonidas_order, re.IGNORECASE | re.DOTALL)
    
    if command_match:
        task = command_match.group(2).strip()
        print(f"**Leonidas Orders:** {task}")
        print("-" * 30)
        
        # Execute Sub-Agent
        soldier_report = execute_soldier(task)
        
        print(f"**Soldier Returns:**\n{soldier_report}")
        print("-" * 30)
        
        # Final Review
        final_input = f"SOLDIER REPORT:\n{soldier_report}\n\nReview this."
        final_response = call_sarvam(final_input, "You are Leonidas. The soldier has returned. Present the findings to the user.")
        print(f"\n**Leonidas Final Report:**\n{final_response}")
    else:
        # Fallback if model refuses to command (unlikely with this prompt)
        print(leonidas_order)

if __name__ == "__main__":
    main()
