# Companion Code: Build a Fully Autonomous Local AI Coding Agent

This folder contains verified configuration templates and custom workspace skills to deploy a private, local-first coding assistant using OpenCode, Ollama, and the Model Context Protocol (MCP).

Detailed guide and systems evaluation: [Read the full guide on Medium](https://medium.com/@praveenveera92/building-a-fully-autonomous-local-coding-agent-with-opencode-ollama-skills-tools-and-mcp).

## Prerequisites
* Local system (Mac, Windows, or Linux) with Ollama installed.
* Node.js 18+ or Python 3.10+ to run custom workspace skills.
* Git installed.

## Subfolder Structure
* `opencode-config.json`: Workspace configurations defining model names and local MCP server mappings.
* `verify_exports.py`: A workspace verification skill written in Python.
* `verify_exports.ts`: A workspace verification skill written in TypeScript.

## Quick Start

### 1. Model Initialization
Download the base model for autocomplete and instruct model for reasoning:
```bash
ollama pull qwen2.5-coder:1.5b
ollama pull qwen2.5-coder:14b
```

### 2. Configure OpenCode
Copy the `opencode-config.json` template into your local workspace configuration directory (e.g. `~/.config/opencode/config.json`) and configure your filesystem path:
```json
{
  "model": "qwen2.5-coder:14b",
  "temperature": 0.1,
  "mcpServers": {
    "filesystem": {
      "command": "npx",
      "args": [
        "-y",
        "@modelcontextprotocol/server-filesystem",
        "/absolute/path/to/your/project"
      ]
    }
  }
}
```

### 3. Launch Agent Loop
Start the autonomous developer console:
```bash
ollama launch opencode
```
Ensure you run this command inside a clean Git repository. If the agent makes erroneous edits, run `git reset --hard` to restore the workspace instantly.
