# Local AI Coding Agent: Configuration & Custom Skills

This directory contains the configurations, scripts, and skills to run a private, local-first AI coding agent on your workstation using Ollama, Continue.dev, and Model Context Protocol (MCP).

Read the full tutorial on [Medium](https://medium.com/@praveenveera92) or [Dev.to](https://dev.to/praveen_builds).

## Prerequisites
- Local machine (Compatible with macOS M-series, Windows RTX GPU, or Linux)
- Ollama installed (`https://ollama.com`)
- Node.js 18+ and Python 3.10+ installed

## Setup Guide

### 1. Download Local Model Weights
Pull the autocomplete and chat models:
```bash
# Autocomplete (Base)
ollama pull qwen2.5-coder:1.5b-base

# Agent & Chat (Instruct)
ollama pull qwen2.5-coder:14b-instruct
```

### 2. Configure Continue Extension
Copy the settings from `continue_config.json` into your `~/.continue/config.json`.

### 3. Expose Custom Filesystem Tools
Enable the Model Context Protocol (MCP) filesystem server:
```json
"mcpServers": {
  "filesystem": {
    "command": "npx",
    "args": [
      "-y",
      "@modelcontextprotocol/server-filesystem",
      "/path/to/your/workspace"
    ]
  }
}
```

### 4. Custom Skill Utilities
The `/skills` directory features standard utilities in Python and JavaScript to parse exports and scan packages locally.
