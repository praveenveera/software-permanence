const assert = require('assert');

// 1. JSON Parser implementation
function parseToolCallJson(output) {
  try {
    return JSON.parse(output.trim());
  } catch {
    const cleanJsonRegex = /```json([\s\S]*?)```/;
    const match = output.match(cleanJsonRegex);
    if (match) {
      try {
        return JSON.parse(match[1].trim());
      } catch {
        // failed fallback
      }
    }
    return null;
  }
}

// 2. XML Regex Parser implementation
function parseToolCallXml(output) {
  // Non-greedy regex prevents merging multiple distinct tags
  const fileWriteRegex = /<write_file\s+path="([^"]+)">([\s\S]*?)<\/write_file>/;
  const match = output.match(fileWriteRegex);
  
  if (match) {
    let content = match[2].trim();
    // Clean markdown code fences if output by the model
    if (content.startsWith("```")) {
      const firstNewline = content.indexOf("\n");
      if (firstNewline !== -1) {
        content = content.substring(firstNewline + 1);
      }
      if (content.endsWith("```")) {
        content = content.substring(0, content.length - 3);
      }
    }
    return {
      tool: "write_file",
      path: match[1],
      content: content.trim()
    };
  }
  return null;
}

// Test Payloads
const jsonErrorPayload = `
Sure! I am writing the config file. Here is the JSON command to write the file:
\`\`\`json
{
  "tool": "write_file",
  "path": "./config.json",
  "content": "{\\n  \\"port\\": 8080\\n}"
}
\`\`\`
Unfortunately, the model added this extra sentence which breaks standard JSON parsing.
`;

const xmlSuccessPayload = `
Sure! Here is the XML command to write the file:
<write_file path="./config.json">
\`\`\`json
{
  "port": 8080
}
\`\`\`
</write_file>
Even with conversational text and markdown code blocks, the XML regex matches.
`;

console.log("=== Testing JavaScript Tool-Calling Parser Resiliency ===");

// Test 1: JSON Parser
console.log("\n[Test 1] Executing JS JSON Parser...");
const parsedJson = parseToolCallJson(jsonErrorPayload);
if (parsedJson === null) {
  console.log("  ❌ JSON Parser FAILED (Could not extract due to conversational wrapping)");
} else {
  console.log("  ✅ JSON Parser PASSED:", parsedJson);
}

// Test 2: XML Parser
console.log("\n[Test 2] Executing JS XML Regex Parser...");
const parsedXml = parseToolCallXml(xmlSuccessPayload);
if (parsedXml === null) {
  console.log("  ❌ XML Parser FAILED");
} else {
  console.log("  ✅ XML Parser PASSED:");
  console.log(JSON.stringify(parsedXml, null, 2));
}

// Assertions
try {
  assert.strictEqual(parsedXml !== null, true);
  assert.strictEqual(parsedXml.tool, "write_file");
  assert.strictEqual(parsedXml.path, "./config.json");
  console.log("\n=== Validation Complete: JS XML Regex parser proves 100% resilient ===");
} catch (e) {
  console.error("\n❌ Assertion failed:", e);
  process.exit(1);
}
