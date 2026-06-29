---
title: Stop Paying for Copilot: Run Local LLMs in VS Code & CLI (For Free)
published: false
description: Configure a private, local AI coding assistant in VS Code & terminal using Ollama, Continue.dev, and Qwen 2.5 Coder. Save on Github Copilot costs with open-weights LLMs.
tags: ollama, continue, qwen, copilot
canonical_url: https://medium.com/@praveenveera92/running-local-llms-in-vs-code-and-cli-for-private-development
---

![Local AI Reference Card - At a Glance](https://raw.githubusercontent.com/praveenveera/software-permanence/main/assets/01-local-llm-vscode.png?v=2)

Running generative AI assistants locally on your workstation is the most direct way to protect code privacy, maintain compliance, and eliminate monthly API subscription costs.

However, moving off the cloud is not as simple as installing an extension. A misconfigured setup can introduce frustrating latency, drain your workstation battery, and fail to provide accurate autocomplete suggestions.

This guide provides a conceptual overview of the local AI landscape followed by an actionable **five-step guide** to move your setup from the cloud to a fully local workstation.

---

## 1. Local vs. Cloud: Engineering Tradeoffs

Choosing a local setup is not a pure upgrade; it involves a series of engineering tradeoffs. While local models offer absolute data privacy and near-zero latency, they compromise on reasoning capacity and context across multiple files compared to models hosted in the cloud. Understanding these boundaries is critical to knowing when to keep development local and when to leverage the cloud:

| Dimension | Local Assistant (e.g., Qwen 14B / Gemma 12B) | Cloud Assistant (e.g., Claude 3.5 Sonnet / GPT-4o) |
| --- | --- | --- |
| **Data Privacy** | 100% Private (No data leaves your workstation) | Subject to compliance review (Data sent to third party servers) |
| **Token Cost** | **$0 / month** (Runs entirely on local electricity) | $10–$20/mo subscription or fees based on token usage |
| **Autocomplete Latency** | **~150ms** (Instant, zero network delay) | ~500ms - 1.2s (Depends on network stability and cloud congestion) |
| **Offline Capability** | Yes (Works on planes, trains, or secure offline VPCs) | No (Crashes instantly without active internet connection) |
| **Cognitive Ceiling** | **Low to Medium** (Struggles with reasoning across multiple files) | **High** (Resolves complex logic across different modules) |

### Where Local Models Fail

*   **The Abstract Ceiling:** A 14B model lacks the neural density to construct deep mental abstractions of complex codebases. If you ask a local model to resolve circular dependencies across three separate modules, it will likely output syntax-valid but logically broken code.
    
*   **Rare Libraries & Edge Cases:** Cloud models are pre-trained on terabytes of code, including obscure libraries and legacy documentation. Local models are far more narrow; they struggle with undocumented frameworks, internal APIs, or specialized languages (like COBOL or Rust edge-cases).
    
*   **Multi-Modal Limitations:** Local setups cannot parse wireframes or UI mockups to generate front-end CSS layouts on consumer GPUs without immediately triggering out-of-memory (OOM) errors.
    

### The Local Model Landscape

*   `Qwen2.5-Coder` **(The Gold Standard):** Google-rivaling coding performance. It is optimized specifically for *Fill-in-the-Middle* autocomplete tasks, making it the most fluent local coding weight available today.
    
*   `DeepSeek-Coder` **(The Alternative):** Highly optimized for Python and C++ structures. However, its older codebase context means it slightly lags behind Qwen on modern multi-language syntax.
    
*   `Gemma 4 QAT` **(The Logic Specialist):** Excellent logic capabilities and a robust 32k context capability, though it requires custom parameter configuration in Ollama to run smoothly.
    

---

## 2. The Systems Metrics That Matter

When running local models, developer experience is governed by three primary systems metrics:

1.  **Time to First Token (TTFT) / Context Pre-fill Latency:** The delay (in milliseconds) between triggering an autocomplete completion and the model generating its first character. In autocomplete, a TTFT above **250ms** breaks your visual typing flow.
    
2.  **Token Generation Throughput (Tokens/Second):** The speed at which the model streams its output text once it starts writing. For real-time reading, you need at least **20–30 tokens/second**. For autocomplete, the model should complete lines instantly (**75+ tokens/second**).
    
3.  **VRAM Footprint vs. System Memory Swap:** If a model fits 100% inside VRAM, it runs at full speed. If it overflows by even **10MB**, the OS pages the remaining weights to system RAM, creating a massive memory bus bottleneck. This drops speeds from 30 tokens/sec to **under 2 tokens/sec**. Always size your models to fit within 70% of your total VRAM, leaving 30% headroom for your OS and browser.
    

---

## 🚀 The Local AI Developer Journey

```plaintext
  ├── Step 1: Audit Your Hardware (VRAM Sizing)
  ├── Step 2: Spin Up the Model Runner (Ollama)
  ├── Step 3: Link the IDE Interface (Continue config.json)
  ├── Step 4: Protect Workspace CPU (.continueignore)
  └── Step 5: Expand to the Command Line (CLI Pipes)
```

---

### Step 1: Audit Your Hardware (The "Kitchen Counter" Rule)

Running models locally requires matching model parameters to your system's memory (VRAM/RAM).

> 💡 **The Kitchen Counter Analogy:** Think of VRAM (GPU memory) as your kitchen counter, and system RAM/swap as the pantry down the hall. If all your ingredients fit on the counter (VRAM), you prepare the meal instantly. If the ingredients are too large and overflow the counter, you have to run back and forth to the pantry (RAM) for every single step. Your cooking speed collapses. Keep your models strictly within VRAM bounds.

Here is your hardware compatibility reference sheet:

| System VRAM (Kitchen Counter) | Model Parameter Size | Recommended Models | Quantization | VRAM Footprint |
| --- | --- | --- | --- | --- |
| **8 GB** | 1B - 3B | `qwen2.5-coder:1.5b` | `Q4_K_M` | ~1.6 GB |
| **16 GB** | 7B - 8B | `qwen2.5-coder:7b` | `Q4_K_M` | ~4.7 GB |
| **24 GB** | 12B - 14B | `qwen2.5-coder:14b` | `Q4_K_M` | ~9.3 GB |
| **32 GB+** | 14B - 22B | `codestral:22b` | `Q4_K_M` | ~15.1 GB |

### Sizing Models to Task Complexity

To optimize compute resources, structure your workflow by mapping developer tasks to model sizes:

*   **Simple Tasks (Tab Autocomplete & Syntax Matching):** Single-line completions, closing parentheses, standard imports, variable assignments. Requires < 200ms latency. Sized at **1.5B to 3B parameters** (e.g., `Qwen2.5-Coder-1.5B-Base`).
    
*   **Medium Tasks (Context-Aware Chat & Unit Testing):** Writing utility functions, refactoring single files, generating test suites, explaining compilation errors. Sized at **7B to 14B parameters** (e.g., `Qwen2.5-Coder-14B-Instruct` or `Gemma-4-12B`).
    
*   **Complex Tasks (Multi-File Debugging & System Architecture):** Architectural planning, debugging cross-module dependencies, codebase index search. Sized at **22B+ parameters** (e.g., `Codestral-22B` or private VPC-hosted 70B+ models).
    

---

### Step 2: Spin Up the Model Runner (Ollama)

Ollama acts as the engine room of your setup. It manages model weights, schedules GPU memory allocation, and exposes local API endpoints.

1.  Download and install [Ollama for macOS](https://ollama.com).
    
2.  Pull the two models we need (one lightweight model optimized for tab autocomplete, and one larger model for reasoning in chat):
    
    ```bash
    # Pull the lightweight autocomplete model (Base model)
    ollama pull qwen2.5-coder:1.5b-base
    
    # Pull the chat sidebar reasoning model (Instruct model)
    ollama pull qwen2.5-coder:14b-instruct
    ```
    

### (Optional) Tuning Parameters via a Custom Modelfile

If you need custom parameters, such as running **Gemma 4 12B QAT** with an expanded 32k context window:

1.  Locate your local GGUF file directory and create a `Modelfile`:
    
    ```dockerfile
    FROM /path/to/local/gemma-4-12b-it-QAT.gguf
    PARAMETER num_ctx 32768
    ```
    
2.  Build the model in Ollama:
    
    ```bash
    ollama create gemma4:12b-qat-32k -f Modelfile
    ```
    

---

### Step 3: Link the IDE Interface (Continue config.json)

Now we connect VS Code to your local Ollama engine using the open-source **Continue.dev** extension.

1.  Install the `Continue` extension in VS Code.
    
2.  Open the Continue settings (`config.json`) and configure it to point to your local Ollama instance:
    

```json
{
  "models": [
    {
      "title": "Ollama - Qwen 14B Coder",
      "provider": "ollama",
      "model": "qwen2.5-coder:14b",
      "apiBase": "http://localhost:11434"
    },
    {
      "title": "Ollama - Gemma 4 QAT",
      "provider": "ollama",
      "model": "gemma4:12b-qat-32k",
      "apiBase": "http://localhost:11434"
    }
  ],
  "tabAutocompleteModel": {
    "title": "Ollama - Autocomplete",
    "provider": "ollama",
    "model": "qwen2.5-coder:1.5b-base",
    "apiBase": "http://localhost:11434"
  }
}
```

### Enabling the VS Code CLI Command

To open your configuration file directly from your terminal, enable the VS Code shell utility:

1.  Open VS Code, open the Command Palette (`Cmd+Shift+P` on macOS, `Ctrl+Shift+P` on Windows/Linux).
    
2.  Run: `Shell Command: Install 'code' command in PATH`.
    
3.  Now, you can open and edit your configuration file directly from your terminal:
    
    ```bash
    code ~/.continue/config.json
    ```
    

### Replacing Copilot Features 1-to-1

Once Continue is connected to your local model runner, here is how you trigger the models to replace Copilot's core capabilities:

*   **Inline Autocomplete (Ghost Text):** As you write code, the lightweight `Qwen-1.5B-Base` model streams single-line completions inline. Press `Tab` to accept.
    
*   **In-Place Code Editing (`Cmd+I` / `Ctrl+I`):** Select a block of code, press `Cmd+I` (macOS) or `Ctrl+I` (Windows/Linux), type your editing instruction (e.g. *"Convert this loop to a list comprehension"*), and press Enter. The model will edit the file inline.
    
*   **Sidebar Chat & Context (`Cmd+L` / `Ctrl+L`):** Press `Cmd+L` to open the chat panel. Type `@` to reference specific files, terminal shell commands, or your entire codebase index, routing the queries to your larger `Qwen-14B-Instruct` model.
    

> ℹ️ **Isolate Autocomplete from Chat:** Do not route both chat and autocomplete to the same model. Tab autocomplete requires immediate responses. Use `Qwen-1.5B-Base` for autocomplete (optimized for fast, inline Fill-in-the-Middle tasks) and `Qwen-14B-Instruct` for the chat sidebar.

### Workstation Benchmark Results (Measured Live on Apple M5 Pro)

To prove local viability, we measured prompt pre-fill speeds (Time to First Token) and token generation throughput (text output speed) using your hardware configuration:

| Model Configuration | Parameter Size | VRAM Footprint | Quantization | Context Pre-fill Speed | Token Generation Speed | Sizing Latency |
| --- | --- | --- | --- | --- | --- | --- |
| **Qwen2.5-Coder (Base)** | 1.5B | 1.6 GB | `Q4_K_M` | 190.6 tok/s | **188.4 tok/s** | < 80ms (Real-time autocomplete) |
| **Gemma 4 QAT** | 12B | 7.0 GB | `Q4_K_M` | 129.5 tok/s | **34.8 tok/s** | Real-time reasoning |
| **Qwen2.5-Coder (Instruct)** | 14B | 9.0 GB | `Q4_K_M` | 214.8 tok/s | **30.0 tok/s** | Cloud-parity chat speed |

#### Benchmark Test Script & Code Reference
The benchmark tests were executed locally using the companion test script. The full source code is hosted in the companion repository:
👉 **[software-permanence/01-local-llm-vscode](https://github.com/praveenveera/software-permanence/tree/main/01-local-llm-vscode)**

Here is the raw terminal log output of running [`test_local_llm.py`](https://github.com/praveenveera/software-permanence/blob/main/01-local-llm-vscode/test_local_llm.py) against Ollama:

```plaintext
=== Running Local LLM Workstation Benchmark ===
Target model: qwen2.5-coder:14b (Q4_K_M)

[Step 1] Measuring Context Pre-fill Speed (Time to First Token)
  - Processing prompt size: 8192 tokens
  - Pre-fill throughput: 214.8 tokens/second

[Step 2] Measuring Text Generation Speed (Output Throughput)
  - Generating 500 response tokens
  - Generation throughput: 30.0 tokens/second

[Step 3] Verifying Tool-Calling Parse Compliance
  - XML Tool Extraction: PASSED (Regex matched 100% output)
  - JSON Tool Extraction: FAILED (Output wrapped in Markdown fences)

=== Validation Complete: Qwen 14B behaves at cloud-parity speed ===
```

---

### Step 4: Protect Workspace CPU (.continueignore)

By default, Continue tries to index every file in your workspace to build local vector embeddings for chat retrieval. On large projects, this causes your CPU usage to spike to 100% and chokes autocomplete.

To prevent this, create a `.continueignore` file in the root of your project directory:

```plaintext
.git/
node_modules/
dist/
build/
.svelte-kit/
*.log
```

### Fixing Context Shifting Latency

Autocomplete can freeze for 2-3 seconds when you switch tabs because Continue is parsing the entire contents of the new file.

*   **The Fix:** In VS Code settings, search for `Continue: Tab Autocomplete Options`, and set `Prefix Length` to `500` and `Suffix Length` to `250`. Reducing these boundaries limits context parsing size, giving you instant tab completions upon tab switching.
    

---

### Step 5: Expand to the Command Line (Terminal Agents & Pipes)

Once your local model runner is set up, you aren't restricted to the IDE. Ollama’s desktop interface includes a native **Launch** registry that allows you to spin up open-source terminal agents directly from your CLI.

> ⚠️ **Beginner Warning (The Git Sandbox Rule):** Terminal-native agents (`opencode`, `claude`) execute edits and run commands directly on your local system. Before launching an agent from your CLI, **always ensure you are running it inside a clean Git repository.** If the agent runs a destructive command or writes broken code, you can roll back your workspace instantly via `git reset --hard`.

### 1. Launching Terminal-Native Coding Agents

Instead of paid cloud services, you can run autonomous command-line developers directly inside your shell:

*   **OpenCode (Anomaly's open-source coding agent):** An autonomous terminal coder that reads build logs, refactors files, and handles tasks locally:
    
    ```bash
    ollama launch opencode
    ```
    
*   **Copilot CLI (Terminal helper agent):** Explains shell commands, generates commands from natural language, and handles prompt operations in your terminal:
    
    ```bash
    ollama launch copilot-cli
    ```
    
*   **Claude Code (Subagent coding CLI):** Anthropic’s subagent developer interface configured to run locally:
    
    ```bash
    ollama launch claude
    ```
    

### 2. Piping Logs for Custom Debugging

For quick troubleshooting, you can pipe compiler errors or log dumps directly into the model without copying and pasting:

```bash
# Pipe an execution error log to Ollama
cat error.log | ollama run qwen2.5-coder:14b "Explain this error and suggest a fix"
```

### Direct Programmatic API Access

You can call your local models directly inside your applications or custom tooling. Here is how to execute a generation request using Curl and Python:

#### Using Curl:
```bash
curl -s -X POST http://localhost:11434/api/generate -d '{
  "model": "qwen2.5-coder:14b",
  "prompt": "Convert this bash script to a Python script: $(cat build.sh)",
  "stream": false
}' | jq '.response'
```

#### Using Python:
```python
import urllib.request
import json

payload = {
    "model": "qwen2.5-coder:14b",
    "prompt": "Convert this bash script to a Python script.",
    "stream": False
}

req = urllib.request.Request(
    "http://localhost:11434/api/generate",
    data=json.dumps(payload).encode("utf-8"),
    headers={"Content-Type": "application/json"}
)

with urllib.request.urlopen(req) as response:
    response_data = json.loads(response.read().decode("utf-8"))
    print(response_data.get("response"))
```

---

## Pro-Tips & Troubleshooting

### Issue: Port 11434 is Already in Use

On macOS, Ollama runs as a background service and will block port `11434` even if the app UI is closed.

*   **The fix:** Manually kill the background process via terminal:
    
    ```bash
    pkill Ollama
    ```
    

### Issue: Zero-Lag Loading (keep_alive)

By default, Ollama unloads models from memory after 5 minutes of inactivity. When you trigger code completion later, you face a 5–10 second delay as the model loads back into VRAM.

*   **The fix:** Set the model to remain permanently loaded in GPU memory by configuring the `keep_alive` parameter to `-1` (always stay in memory) or `30m` (30 minutes) in your API settings.
    

### 🔰 Beginner's Troubleshooting Checklist

If your local development setup is failing, use this diagnostic guide to find the cause:
*   **Is Ollama running?** Open your terminal and run `ollama list`. If it fails with a connection error, the Ollama application service is shut down.
*   **Is autocomplete lagging?** If suggestions take more than 2-3 seconds, check if your model is spilling into system RAM. In Activity Monitor (macOS) or Task Manager (Windows), look at memory swap. If swap is active, you are running a model too large for your VRAM.
*   **Is Continue forgetting instructions?** If the sidebar chat stops responding or behaves erratically, you have hit the context limit of the loaded model. Restart the chat session to clean the active history window.

---

## Summary

Running local models provides code privacy and offline capabilities. By combining **Ollama**, **LM Studio**, and **Continue**, you can configure a usable local developer environment in both your IDE and terminal.

*What models are you running locally for autocomplete? Let me know in the comments.*

---

**Hi, I'm Praveen Veera.** I build practical AI systems, specializing in Enterprise AI Platforms, Local LLMs, and Dev Tools.

Read my notes:
*   **Substack Newsletter:** [softwarepermanence.substack.com](https://softwarepermanence.substack.com)
*   **LinkedIn:** [linkedin.com/in/praveen-veera-6ab22567](https://www.linkedin.com/in/praveen-veera-6ab22567/)
*   **GitHub (Companion Code):** [github.com/praveenveera/software-permanence](https://github.com/praveenveera/software-permanence)
*   **Dev.to:** [dev.to/praveen_builds](https://dev.to/praveen_builds)
*   **Medium:** [medium.com/@praveenveera92](https://medium.com/@praveenveera92)
*   **Instagram:** [@praveen.builds](https://instagram.com/praveen.builds)
*   **Hashnode:** [hashnode.com/@praveen-builds](https://hashnode.com/@praveen-builds)
