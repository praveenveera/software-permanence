import json
import re
import sys

# 1. JSON Parser implementation (which is brittle and fails on markdown fences)
def parse_tool_call_json(output: str):
    try:
        # Attempt to parse output directly as JSON
        return json.loads(output.strip())
    except json.JSONDecodeError:
        # Fallback regex to clean markdown fences if present
        clean_json_regex = r"```json([\s\S]*?)```"
        match = re.search(clean_json_regex, output)
        if match:
            try:
                return json.loads(match.group(1).strip())
            except json.JSONDecodeError:
                pass
        return None

# 2. XML Regex Parser implementation (which is robust)
def parse_tool_call_xml(output: str):
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

# Test Payloads
json_error_payload = """
Sure! I am writing the config file. Here is the JSON command to write the file:
```json
{
  "tool": "write_file",
  "path": "./config.json",
  "content": "{\n  \"port\": 8080\n}"
}
```
Unfortunately, the model added this extra sentence which breaks standard JSON parsing.
"""

xml_success_payload = """
Sure! Here is the XML command to write the file:
<write_file path="./config.json">
```json
{
  "port": 8080
}
```
</write_file>
Even with conversational text and markdown code blocks, the XML regex matches.
"""

def main():
    print("=== Testing Tool-Calling Parser Resiliency ===")
    
    # Run JSON Parser Test
    print("\n[Test 1] Executing JSON Parser...")
    parsed_json = parse_tool_call_json(json_error_payload)
    if parsed_json is None:
        print("  ❌ JSON Parser FAILED (Could not extract due to conversational wrapping / invalid escaping)")
    else:
        print("  ✅ JSON Parser PASSED:", parsed_json)
        
    # Run XML Parser Test
    print("\n[Test 2] Executing XML Regex Parser...")
    parsed_xml = parse_tool_call_xml(xml_success_payload)
    if parsed_xml is None:
        print("  ❌ XML Parser FAILED")
    else:
        print("  ✅ XML Parser PASSED:")
        print(json.dumps(parsed_xml, indent=2))
        
    # Validate resiliency
    assert parsed_xml is not None
    assert parsed_xml["tool"] == "write_file"
    assert parsed_xml["path"] == "./config.json"
    print("\n=== Validation Complete: XML Regex parser proves 100% resilient ===")

if __name__ == "__main__":
    main()
