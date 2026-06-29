import json
import urllib.request
import time

OLLAMA_URL = "http://localhost:11434/api/generate"
MODEL_NAME = "qwen2.5-coder:14b"

def query_ollama(prompt, system_prompt="", stream=False):
    payload = {
        "model": MODEL_NAME,
        "prompt": prompt,
        "system": system_prompt,
        "stream": stream,
        "options": {
            "temperature": 0.2
        }
    }
    req = urllib.request.Request(
        OLLAMA_URL, 
        data=json.dumps(payload).encode('utf-8'),
        headers={'Content-Type': 'application/json'}
    )
    try:
        with urllib.request.urlopen(req) as response:
            res_data = json.loads(response.read().decode('utf-8'))
            return res_data
    except Exception as e:
        print(f"Error querying Ollama: {e}")
        return None

def test_context_latency():
    print("\n--- Benchmark 1: Context Evaluation Latency ---")
    
    # 1. Small Context
    small_prompt = "Write a hello world function in TypeScript."
    print("Testing small prompt (~10 tokens)...")
    res_small = query_ollama(small_prompt)
    if res_small:
        eval_sec = res_small.get('prompt_eval_duration', 0) / 1e9
        print(f"Small Prompt Eval Duration: {eval_sec:.4f} seconds (Tokens: {res_small.get('prompt_eval_count', 0)})")
    
    # 2. Large Context (~8000 tokens)
    print("Generating large dummy code context (~8000 tokens)...")
    large_context = " // " + "dummy code payload " * 4000
    large_prompt = f"{large_context}\n\nWrite a hello world function in TypeScript based on the file context above."
    
    print("Testing large prompt (~8000 tokens)...")
    res_large = query_ollama(large_prompt)
    if res_large:
        eval_sec = res_large.get('prompt_eval_duration', 0) / 1e9
        print(f"Large Prompt Eval Duration: {eval_sec:.4f} seconds (Tokens: {res_large.get('prompt_eval_count', 0)})")
        # Calculate prompt eval tokens/sec
        tokens = res_large.get('prompt_eval_count', 0)
        if eval_sec > 0:
            print(f"Prompt Eval Speed (Pre-fill): {tokens / eval_sec:.2f} tokens/second")

def test_tool_calling_output():
    print("\n--- Benchmark 2: Tool-Calling Parsing (JSON vs XML) ---")
    
    # Tool instruction
    tool_instruction = "Edit the file './src/main.ts' to add a console log 'App started'."
    
    # 1. JSON Request
    json_system = (
        "You are an AI assistant. You must call tools using JSON. "
        "Format: {\"tool\": \"write_file\", \"arguments\": {\"path\": \"./src/main.ts\", \"content\": \"console.log('App started');\"}}"
    )
    print("Requesting tool call in JSON format...")
    res_json = query_ollama(tool_instruction, system_prompt=json_system)
    if res_json:
        response_text = res_json.get('response', '')
        print("\n[JSON Output Raw]:")
        print(response_text)
        
        # Test JSON parse directly
        try:
            json.loads(response_text)
            print(">>> Result: Raw JSON parsed successfully with zero scrubbers!")
        except Exception:
            print(">>> Result: Failed to parse directly as JSON (probably contains conversational text or markdown blocks).")
            
    # 2. XML Request
    xml_system = (
        "You are an AI assistant. You must call tools using XML tags. "
        "Format: <write_file path=\"./src/main.ts\">console.log('App started');</write_file>"
    )
    print("\nRequesting tool call in XML format...")
    res_xml = query_ollama(tool_instruction, system_prompt=xml_system)
    if res_xml:
        response_text = res_xml.get('response', '')
        print("\n[XML Output Raw]:")
        print(response_text)
        
        # Test regex parse
        import re
        xml_regex = r'<write_file path="(.+?)">([\s\S]*?)</write_file>'
        match = re.search(xml_regex, response_text)
        if match:
            print(f">>> Result: XML Regex Parsed Successfully! Path: {match.group(1)}")
        else:
            print(">>> Result: XML Regex Parsing Failed.")

if __name__ == "__main__":
    test_context_latency()
    test_tool_calling_output()
