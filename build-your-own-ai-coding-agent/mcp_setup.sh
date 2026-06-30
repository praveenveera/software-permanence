#!/bin/bash
# Local AI Coding Agent MCP Setup helper script
echo "=== Setting up Model Context Protocol (MCP) filesystem server ==="
mkdir -p "$HOME/agent-workspace"
echo "Creating agent workspace directory at $HOME/agent-workspace"
echo "Copy your project files there for the agent to access."
echo ""
echo "Add this block to your ~/.continue/config.json 'mcpServers' config:"
echo ""
cat <<EOF
"mcpServers": {
  "filesystem": {
    "command": "npx",
    "args": [
      "-y",
      "@modelcontextprotocol/server-filesystem",
      "$HOME/agent-workspace"
    ]
  }
}
EOF
echo ""
echo "=== Done ==="
