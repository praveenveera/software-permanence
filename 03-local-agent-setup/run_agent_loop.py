import os
import sys
import re
import json
import urllib.request
import subprocess
import time

def parse_tool_call(output: str):
    # Non-greedy regex pattern (.*?) avoids greedy tag merges
    file_write_regex = r'<write_file\s+path="([^"]+)">([\s\S]*?)</write_file>'
    match = re.search(file_write_regex, output)
    if match:
        content = match.group(2).strip()
        # Clean markdown code fences if output by the model
        if content.startswith("```"):
            first_newline = content.find("\n")
            if first_newline != -1:
                content = content[first_newline+1:]
            if content.endswith("```"):
                content = content[:-3]
        return {
            "tool": "write_file",
            "path": match.group(1),
            "content": content.strip()
        }
    return None

def query_ollama(endpoint: str, model: str, system_prompt: str, user_prompt: str):
    payload = {
        "model": model,
        "prompt": f"System Guidelines:\n{system_prompt}\n\nUser Task:\n{user_prompt}",
        "options": {
            "temperature": 0.0,
            "num_ctx": 16384
        },
        "stream": False
    }
    
    req = urllib.request.Request(
        f"{endpoint}/api/generate",
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json"}
    )
    
    start_time = time.time()
    with urllib.request.urlopen(req) as response:
        duration = time.time() - start_time
        response_data = json.loads(response.read().decode("utf-8"))
        return {
            "response": response_data.get("response"),
            "duration": duration,
            "eval_count": response_data.get("eval_count", 0),
            "prompt_eval_count": response_data.get("prompt_eval_count", 0)
        }

def main():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(script_dir)
    
    print("=== Launching Local Agent Run Simulation ===")
    
    # 1. Load Configurations & Rules
    print("[Step 1] Loading workspace configs, guidelines, and skills...")
    with open("opencode.json", "r") as f:
        config = json.load(f)
    
    with open(".agents/instructions.md", "r") as f:
        instructions = f.read()
        
    with open("skills/fastapi-api.md", "r") as f:
        api_skill = f.read()
        
    system_prompt = f"{instructions}\n\n## Specialized Skill Guidelines\n{api_skill}"
    
    # 2. Inspect codebase
    print("[Step 2] Reading current workspace status...")
    main_py_path = "workspace/app/main.py"
    with open(main_py_path, "r") as f:
        current_main_code = f.read()
        
    user_prompt = f"""
Here is the current content of '{main_py_path}':
```python
{current_main_code}
```

Task: Following instructions.md and the fastapi-api.md skill, write a health-check endpoint (route `/health`) returning `{{"status": "OK"}}` in '{main_py_path}'.

Output format: You MUST output the complete updated content of '{main_py_path}' wrapped inside a <write_file path="{main_py_path}">...code...</write_file> tag.
Do not output anything else.
"""

    # 3. Query Ollama Local Model
    print(f"[Step 3] Querying local model '{config['model']}' via Ollama...")
    try:
        result = query_ollama(
            endpoint=config["endpoint"],
            model=config["model"],
            system_prompt=system_prompt,
            user_prompt=user_prompt
        )
    except Exception as e:
        print(f"[Error] Failed to connect to local Ollama server: {e}", file=sys.stderr)
        print("Please verify that Ollama application is running locally.", file=sys.stderr)
        sys.exit(1)
        
    print(f"  └─ Generation completed in {result['duration']:.2f} seconds.")
    print(f"  └─ Prompt Tokens: {result['prompt_eval_count']}, Generation Tokens: {result['eval_count']}")
    
    # 4. Parse XML Tool Call
    print("[Step 4] Extracting tool call payload from model output...")
    tool_call = parse_tool_call(result["response"])
    
    if not tool_call:
        print("[Fail] Parser could not find a valid XML tool tag in response!")
        print("Raw Response:", result["response"])
        sys.exit(1)
        
    print(f"  └─ Parsed Action: write_file to '{tool_call['path']}'")
    
    # 5. Apply filesystem modifications (Simulating Workspace Edit)
    print("[Step 5] Writing modified code to local workspace...")
    with open(tool_call["path"], "w") as f:
        f.write(tool_call["content"])
    print(f"  └─ Updated '{tool_call['path']}' successfully.")
    
    # 6. Add Test Case (Simulating Agent test generation)
    print("[Step 6] Adding health-check assertion to unittest suite...")
    test_suite_path = "workspace/tests/test_api.py"
    health_test_code = """

    def test_read_health(self):
        response = self.client.get("/health")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {"status": "OK"})
"""
    with open(test_suite_path, "a") as f:
        f.write(health_test_code)
    print(f"  └─ Appended 'test_read_health' test case.")
    
    # 7. Run Local Tests (Simulating Agent verify command step)
    print("[Step 7] Running unittest suite to validate changes...")
    
    # Run test command (ensuring workspace is in PYTHONPATH)
    env = os.environ.copy()
    env["PYTHONPATH"] = os.path.join(script_dir, "workspace")
    
    test_run = subprocess.run(
        ["python3", "-m", "unittest", "workspace/tests/test_api.py"],
        capture_output=True,
        text=True,
        env=env
    )
    
    print("\n=== Workspace Test Results ===")
    print(test_run.stdout)
    print(test_run.stderr)
    if test_run.returncode == 0:
        print("[Pass] Agent validation completed with all test assertions passing!")
    else:
        print("[Fail] Parser output or endpoint failed test execution.")
        sys.exit(1)

if __name__ == "__main__":
    main()
