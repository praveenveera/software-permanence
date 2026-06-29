function parseToolCall(output) {
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

module.exports = { parseToolCall };
