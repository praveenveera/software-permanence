# Software Permanence: Local AI Reference Configurations

Welcome to the companion repository for the **Software Permanence** publication series. This repository hosts verified config templates, ignore rules, and automation scripts to help you run private, local AI developer loops on your workstation.

Subscribe to the newsletter for deep-dives into running open weights, building modular workflows, and reclaiming your code privacy:
👉 **[softwarepermanence.substack.com](https://softwarepermanence.substack.com)**

---

## 📅 Publication Status Tracker

This table tracks the publication status of each article across platforms and links to their companion configurations:

| Topic / Title | Companion Code | Substack | Dev.to | Medium | Hashnode |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **01. Stop Paying for Copilot** | [`01-local-llm-vscode/`](./01-local-llm-vscode/) | 📝 Draft | 📝 Draft | 📝 Draft | [📝 Draft (Preview)](https://praveen-builds.hashnode.dev/preview/6a41ed198ead0237e96ce3a7) |
| **02. Why Local Coding Agents Fail** | *(Pending)* | 📝 Draft | 📝 Draft | 📝 Draft | 📝 Draft |
| **03. Local AI for Enterprise Developers** | *(Pending)* | 📝 Draft | 📝 Draft | 📝 Draft | 📝 Draft |

---

## 📂 Repository Contents

### [01-local-llm-vscode](./01-local-llm-vscode/)
Configuration templates to replace GitHub Copilot with local Ollama models in VS Code:
*   `config.json`: Router configurations separating autocomplete (`qwen2.5-coder:1.5b-base`) from chat reasoning (`qwen2.5-coder:14b-instruct`).
*   `.continueignore`: Pre-configured directory exclusion templates to prevent 100% CPU loops from workspace indexers.
*   `Modelfile`: Ollama create template to build custom models with extended context windows (e.g., Gemma 4 12B QAT with 32k context).

---

## 🚀 Quick Setup: VS Code Local AI

### Step 1: Install Ollama & Pull Weights
1. Download and install [Ollama](https://ollama.com).
2. Pull the models from your terminal:
   ```bash
   # Base model for inline tab autocomplete
   ollama pull qwen2.5-coder:1.5b-base
   
   # Instruct model for chat sidebar reasoning
   ollama pull qwen2.5-coder:14b-instruct
   ```

### Step 2: Configure Continue Extension in VS Code
1. Install the **Continue** extension from the VS Code Marketplace.
2. Open your terminal and open Continue's config file (ensure you have the VS Code `code` CLI installed in your PATH):
   ```bash
   code ~/.continue/config.json
   ```
3. Copy the template settings from [`01-local-llm-vscode/config.json`](./01-local-llm-vscode/config.json) into your file.

### Step 3: Prevent CPU Spikes
Copy [`01-local-llm-vscode/.continueignore`](./01-local-llm-vscode/.continueignore) into the root of your project workspace to exclude folders like `node_modules` or `dist` from indexers.

---

## 💻 Terminal CLI Integrations

### Native Ollama Agents
You can launch autonomous developer TUI agents natively using the Ollama desktop registry:
```bash
# Launch autonomous coding agent
ollama launch opencode

# Launch local command helper
ollama launch copilot-cli
```

### Log Piping
Pipe execution dumps directly to your local models for instant debugging:
```bash
cat error.log | ollama run qwen2.5-coder:14b "Explain this error"
```

---

## 📊 Hardware Sizing Guide

| System VRAM | Max Model Size | Recommended Model | Quantization | VRAM Footprint |
| :--- | :--- | :--- | :--- | :--- |
| **8 GB** | < 3B | `qwen2.5-coder:1.5b` | `Q4_K_M` | ~1.6 GB |
| **16 GB** | 7B - 8B | `qwen2.5-coder:7b` | `Q4_K_M` | ~4.7 GB |
| **24 GB** | 12B - 14B | `qwen2.5-coder:14b` | `Q4_K_M` | ~9.3 GB |
| **32 GB+** | 14B - 22B | `codestral:22b` | `Q4_K_M` | ~15.1 GB |

---

## ✍️ Authorship
Created by **Praveen Veera** — Enterprise AI Architect & Platform Builder.
*   **LinkedIn:** [linkedin.com/in/praveen-veera-6ab22567](https://linkedin.com/in/praveen-veera-6ab22567)
*   **Dev.to:** [dev.to/praveen_builds](https://dev.to/praveen_builds)
*   **Instagram:** [@praveen.builds](https://instagram.com/praveen.builds)
