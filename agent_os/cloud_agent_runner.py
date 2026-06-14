"""
cloud_agent_runner.py — Stateful, self-correcting Cloud Agent runner for Agent OS.
Generates code to solve a task, executes it, self-corrects on errors, logs to agent_os.log,
saves assets to asset_library, and logs the execution summary to Obsidian.
"""

import sys
import os
import argparse
import subprocess
import shutil
import urllib.error
from pathlib import Path
from datetime import datetime

# Setup path so we can import from sibling files
sys.path.insert(0, str(Path(__file__).parent))

# Load .env
env_path = Path(__file__).parent / ".env"
if env_path.exists():
    with open(env_path, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                k, v = line.split("=", 1)
                os.environ.setdefault(k.strip(), v.strip())

from openrouter_client import call_openrouter
from obsidian_bridge import save_note

LOG_FILE = Path(__file__).parent / "agent_os.log"
ASSET_LIBRARY = Path(__file__).parent / "asset_library"
ASSET_LIBRARY.mkdir(exist_ok=True)


# Setup global trackers for active job status updates
_ACTIVE_JOB_ID = ""
_ACTIVE_JOB_TASK = ""
_ACTIVE_JOB_MODEL = ""
_ACTIVE_JOB_LOGS = []

def log(message: str):
    ts = datetime.now().strftime("%H:%M:%S")
    line = f"[{ts}] [CloudAgent] {message}"
    print(line)
    try:
        with open(LOG_FILE, "a", encoding="utf-8") as f:
            f.write(line + "\n")
    except Exception:
        pass
    
    # Update real-time status file if we are running in an active dashboard job
    if _ACTIVE_JOB_ID:
        import json
        _ACTIVE_JOB_LOGS.append(line)
        status_file = Path(__file__).parent / "scratch" / f"status_{_ACTIVE_JOB_ID}.json"
        status_file.parent.mkdir(parents=True, exist_ok=True)
        try:
            status_file.write_text(json.dumps({
                "job_id": _ACTIVE_JOB_ID,
                "task": _ACTIVE_JOB_TASK,
                "status": "RUNNING",
                "model": _ACTIVE_JOB_MODEL,
                "logs": _ACTIVE_JOB_LOGS,
                "last_updated": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }, indent=2), encoding="utf-8")
        except Exception:
            pass


def extract_code(text: str) -> str:
    import re
    # Match ```python ... ```
    match = re.search(r"```python(.*?)```", text, re.DOTALL | re.IGNORECASE)
    if match:
        return match.group(1).strip()
    # Match generic ``` ... ```
    match = re.search(r"```(.*?)```", text, re.DOTALL)
    if match:
        return match.group(1).strip()
    return text.strip()


def run_loop(task: str, model: str, job_id: str = ""):
    global _ACTIVE_JOB_ID, _ACTIVE_JOB_TASK, _ACTIVE_JOB_MODEL, _ACTIVE_JOB_LOGS
    _ACTIVE_JOB_ID = job_id
    _ACTIVE_JOB_TASK = task
    _ACTIVE_JOB_MODEL = model
    _ACTIVE_JOB_LOGS = []

    log(f"Starting cloud agent for task: '{task}' using model {model}")

    import uuid
    run_id = uuid.uuid4().hex[:8]
    scratch_dir = Path(__file__).parent / "scratch" / f"cloud_agent_{run_id}"
    scratch_dir.mkdir(parents=True, exist_ok=True)

    system_prompt = """You are an expert Python developer. Your goal is to write a single self-contained Python script to solve the user's task.
Requirements:
1. The code must be complete, executable, and self-contained.
2. Return ONLY the executable Python code inside a markdown code block starting with ```python and ending with ```.
3. Do not include any text, notes, or explanations outside of the code block.
4. Try to write all output or generated data to files in the current working directory, so they can be captured.
5. Do not use interactive input (e.g. input()). Keep all parameters hardcoded or derived.
6. Install/import standard libraries, or standard packages like requests, beautifulsoup4, etc. if needed.
"""

    prompt = f"Solve the following task: {task}"
    max_attempts = 5
    success = False
    final_code = ""
    logs = []
    active_model = model

    for attempt in range(1, max_attempts + 1):
        log(f"Attempt {attempt}/{max_attempts}...")
        try:
            response_text = call_openrouter(
                model=active_model,
                system=system_prompt,
                user=prompt,
                max_tokens=3000,
                temperature=0.2
            )
        except Exception as e:
            # Check if it's HTTPError 402 (Payment Required) or 404 (Not Found) or 429 (Too Many Requests)
            is_retryable_failure = False
            if isinstance(e, urllib.error.HTTPError) and e.code in (402, 404, 429):
                is_retryable_failure = True
            
            if is_retryable_failure and active_model != "openrouter/free":
                err_code = e.code if isinstance(e, urllib.error.HTTPError) else "Unknown"
                log(f"Model '{active_model}' failed with HTTP {err_code}. Falling back to 'openrouter/free'...")
                active_model = "openrouter/free"
                try:
                    response_text = call_openrouter(
                        model=active_model,
                        system=system_prompt,
                        user=prompt,
                        max_tokens=3000,
                        temperature=0.2
                    )
                except Exception as fallback_err:
                    err_msg = f"Failed to call OpenRouter fallback model: {fallback_err}"
                    log(err_msg)
                    logs.append(f"--- Attempt {attempt} ---\nOpenRouter Fallback Error: {fallback_err}")
                    prompt += f"\n\n--- Attempt {attempt} OpenRouter Error ---\n{fallback_err}\n\nPlease try again."
                    continue
            else:
                err_msg = f"Failed to call OpenRouter on attempt {attempt}: {e}"
                log(err_msg)
                logs.append(f"--- Attempt {attempt} ---\nOpenRouter Error: {e}")
                prompt += f"\n\n--- Attempt {attempt} OpenRouter Error ---\n{e}\n\nPlease try again."
                continue

        code = extract_code(response_text)
        if not code:
            err_msg = "No code block found in response."
            log(err_msg)
            logs.append(f"--- Attempt {attempt} ---\nError: {err_msg}\nResponse: {response_text}")
            prompt += f"\n\n--- Attempt {attempt} Error ---\n{err_msg}\n\nPlease format the code properly inside ```python ... ```."
            continue

        temp_script = scratch_dir / "temp_script.py"
        temp_script.write_text(code, encoding="utf-8")
        final_code = code

        log(f"Running script...")
        # Execute the python script
        try:
            result = subprocess.run(
                [sys.executable, str(temp_script)],
                cwd=str(scratch_dir),
                capture_output=True,
                text=True,
                timeout=120
            )

            stdout_snippet = result.stdout[-1000:] if result.stdout else ""
            stderr_snippet = result.stderr[-1000:] if result.stderr else ""

            logs.append(
                f"--- Attempt {attempt} Run ---\n"
                f"Exit Code: {result.returncode}\n"
                f"Stdout Snippet:\n{stdout_snippet}\n"
                f"Stderr Snippet:\n{stderr_snippet}"
            )

            if result.returncode == 0:
                log("Script executed successfully!")
                success = True
                break
            else:
                log(f"Script failed with exit code {result.returncode}.")
                
                # Check for ModuleNotFoundError to auto-install dependencies
                import re
                module_match = re.search(r"ModuleNotFoundError:\s*No\s*module\s*named\s*['\"]([^'\"]+)['\"]", result.stderr)
                if module_match:
                    module_name = module_match.group(1)
                    mapping = {
                        "bs4": "beautifulsoup4",
                        "yaml": "pyyaml",
                        "PIL": "pillow",
                        "fitz": "pymupdf",
                        "docx": "python-docx",
                        "pptx": "python-pptx",
                        "openpyxl": "openpyxl",
                    }
                    package_name = mapping.get(module_name, module_name)
                    log(f"Detected missing module: '{module_name}'. Attempting to install package '{package_name}'...")
                    
                    try:
                        install_res = subprocess.run(
                            [sys.executable, "-m", "pip", "install", package_name],
                            capture_output=True,
                            text=True,
                            timeout=60
                        )
                        if install_res.returncode == 0:
                            log(f"Successfully installed package '{package_name}'. Retrying script execution...")
                            # Rerun the script immediately
                            result = subprocess.run(
                                [sys.executable, str(temp_script)],
                                cwd=str(scratch_dir),
                                capture_output=True,
                                text=True,
                                timeout=120
                            )
                            stdout_snippet = result.stdout[-1000:] if result.stdout else ""
                            stderr_snippet = result.stderr[-1000:] if result.stderr else ""
                            
                            logs[-1] = (
                                f"--- Attempt {attempt} Run (Post-Dependency Install) ---\n"
                                f"Exit Code: {result.returncode}\n"
                                f"Stdout Snippet:\n{stdout_snippet}\n"
                                f"Stderr Snippet:\n{stderr_snippet}"
                            )
                            
                            if result.returncode == 0:
                                log("Script executed successfully after installing dependency!")
                                success = True
                                break
                            else:
                                log(f"Script failed again with exit code {result.returncode} after installing dependency.")
                        else:
                            log(f"Failed to install package '{package_name}': {install_res.stderr.strip()}")
                    except Exception as install_err:
                        log(f"Error running pip install: {install_err}")

                if not success:
                    prompt += (
                        f"\n\n--- Attempt {attempt} Code ---\n{code}\n\n"
                        f"--- Attempt {attempt} Run Exit Code: {result.returncode} ---\n"
                        f"Stdout:\n{result.stdout}\n"
                        f"Stderr:\n{result.stderr}\n\n"
                        f"Please correct the error, address why it failed, and output the complete corrected script."
                    )
        except subprocess.TimeoutExpired:
            log("Script execution timed out (limit: 120s).")
            logs.append(f"--- Attempt {attempt} Run ---\nError: TimeoutExpired")
            prompt += (
                f"\n\n--- Attempt {attempt} Code ---\n{code}\n\n"
                f"--- Attempt {attempt} Run Error: TimeoutExpired (120s limit reached) ---\n"
                f"Please optimize the script, make sure it is not looping infinitely, and output the corrected script."
            )
        except Exception as e:
            log(f"Error executing script: {e}")
            logs.append(f"--- Attempt {attempt} Run ---\nExecution Error: {e}")
            prompt += (
                f"\n\n--- Attempt {attempt} Code ---\n{code}\n\n"
                f"--- Attempt {attempt} Execution Error ---\n{e}\n\n"
                f"Please correct this issue and output the complete corrected script."
            )

    # Post-execution phase
    copied_assets = []
    # Copy any new files generated in scratch_dir
    if scratch_dir.exists():
        for item in scratch_dir.iterdir():
            if item.is_file() and item.name != "temp_script.py":
                dest = ASSET_LIBRARY / item.name
                try:
                    shutil.copy2(item, dest)
                    copied_assets.append(str(dest))
                    log(f"Copied generated asset to library: {item.name}")
                except Exception as e:
                    log(f"Failed to copy asset {item.name} to library: {e}")

    # Clean up temporary scratch folder
    try:
        shutil.rmtree(scratch_dir)
    except Exception as e:
        log(f"Warning: Failed to clean up scratch directory {scratch_dir}: {e}")

    # Generate summary note
    status_str = "SUCCESS" if success else "FAILED"
    log(f"Task finished. Status: {status_str}")

    # Write final status update
    if _ACTIVE_JOB_ID:
        import json
        status_file = Path(__file__).parent / "scratch" / f"status_{_ACTIVE_JOB_ID}.json"
        try:
            status_file.write_text(json.dumps({
                "job_id": _ACTIVE_JOB_ID,
                "task": _ACTIVE_JOB_TASK,
                "status": status_str,
                "model": _ACTIVE_JOB_MODEL,
                "logs": _ACTIVE_JOB_LOGS,
                "last_updated": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }, indent=2), encoding="utf-8")
        except Exception:
            pass

    details_md = f"""### Summary of Execution
- **Task**: {task}
- **Status**: {status_str}
- **Model Used**: `{active_model}`
- **Attempts**: {attempt if success else max_attempts}

### Created Assets
"""
    if copied_assets:
        for asset in copied_assets:
            details_md += f"- [{Path(asset).name}](file:///{asset.replace(chr(92), '/')})\n"
    else:
        details_md += "- None\n"

    details_md += f"\n### Final Source Code (`temp_script.py`)\n```python\n{final_code}\n```\n"
    details_md += "\n### Execution History Logs\n"
    for run_log in logs:
        details_md += f"\n```\n{run_log}\n```\n"

    note_title = f"Cloud Agent Run - {task[:40]}"
    try:
        note_path = save_note(
            title=note_title,
            key_idea=f"Cloud Agent executed task: '{task}' with status {status_str}",
            details=details_md,
            next_steps=["Verify the generated files in asset_library" if success else "Debug the python script failures"],
            tags=["cloud-agent", "execution-log", "agent-os"],
            folder="inbox"
        )
        log(f"Saved execution summary to Obsidian: {note_path.name}")
    except Exception as e:
        log(f"Failed to save summary to Obsidian: {e}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Agent OS Cloud Agent Runner")
    parser.add_argument("task", type=str, help="Task description")
    parser.add_argument("--model", type=str, default="google/gemini-2.5-flash", help="OpenRouter model ID")
    parser.add_argument("--job_id", type=str, default="", help="Unique job identifier")
    args = parser.parse_args()

    run_loop(args.task, args.model, args.job_id)
