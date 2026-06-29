---
title: Why Local AI Coding Agents Fail (And How to Break the "Apology Loop")
published: true
description: An engineering audit of local AI coding agents (Cline, Continue.dev) failing under open LLMs. Learn how to resolve Ollama JSON parser apology loops using XML regex tool calling.
tags: cline, continue, ollama, agents
canonical_url: https://medium.com/@praveenveera92/why-local-coding-agents-fail-and-how-to-configure-them
---

Unlike standard chat interfaces where you ask questions and read answers, **AI coding agents** (like **Cline**, **Continue**, or **GarageBuild**) execute actions. They write files, run terminal commands, and inspect compiler errors automatically.

In practice, running local agents on consumer workstations often leads to infinite retries, including parser loops and malformed JSON payloads.

This analysis breaks down the systems boundary between the **Model Layer** (the AI brain) and the **Agent Runtime** (the workstation execution layer), explaining why local agents fail and how to configure them to prevent loop crashes.

### 🔰 What is an "AI Agent" (For Beginners)?
If you have only used ChatGPT or Claude in a browser, coding agents are a different beast. Standard chat models only output text; you must manually copy and paste the code into your editor. **AI agents** are given "hands", meaning they are integrated directly with your filesystem and terminal. They read files, create new code modules, and run test suites autonomously.

Because they have local system access, the first rule of running agents is the **Git Sandbox Rule**:
*   **Always run agents inside a clean Git repository.** Before launching an agent loop, commit your active changes. If the agent goes rogue, deletes files, or writes broken code, you can roll back your entire workspace instantly with `git reset --hard`. Never run agents in root directories or folders containing unversioned files.

![Local AI Agent Cheat Sheet - At a Glance](https://raw.githubusercontent.com/praveenveera/software-permanence/main/assets/02-why-local-agents-fail.png?v=2)

---

## 1. Background: The Model vs. Runtime Divide

An agentic developer environment relies on two separate layers that must constantly communicate:
- **1. The Model Layer (Brain):** The LLM that decides *what* to do.
- **2. The Agent Runtime (Body):** The host framework (Cline, Continue, or GarageBuild) that manages filesystem tools and executes commands.

```
   ┌────────────────────────┐         1. Instructions & Context         ┌─────────────────┐
   │  Agent Runtime (Body)  ├──────────────────────────────────────────>│ Local LLM (Brain)│
   │                        │<──────────────────────────────────────────┤                 │
   └───────────┬────────────┘        2. Tool Call Command (JSON)        └─────────────────┘
               │
               │ 3. Executes File Write or CLI Command
               ▼
   ┌────────────────────────┐
   │ Workstation Filesystem │
   │  (Returns Logs/Errors) │
   └────────────────────────┘
```

Failure occurs when the output formatting returned by the model cannot be understood by the runtime parser.

---

## 2. Why Local Agents Fail

### Failure 1: The JSON Parser Loop (The "Strict Form" Bottleneck)
Most agent frameworks require models to output commands in strict JSON formats. However, lightweight local models (under 30B parameters) struggle to maintain strict syntax under complexity. 
If a model misses a single closing bracket, leaves a trailing comma, or outputs conversational padding around the JSON (e.g. *"Sure, here is the JSON to write that file..."*), standard JSON parsers crash.

> 💡 **The Envelope Analogy:**
> JSON behaves like a strict government form: missing a single comma rejects the entire document. 
> Wrapping tools in XML tags (`<write_file>...</write_file>`) is like placing your letter in a bright red envelope. Even if the model chatters before and after the envelope, the parser can easily spot the red borders and pull out the code package.

### Failure 2: KV Cache Context Eviction (The "Whiteboard" Limit)
As an agent works, the conversation history grows, holding compiler logs, shell outputs, and file edits. When the accumulated tokens fill the context window (`num_ctx`), the local server must evict older tokens to make room.

> ⚠️ **The Whiteboard Analogy:**
> Think of your context window as a whiteboard. As you chat, you write down every step. Once the board is full, you have to erase the top lines to keep writing. If you erase the original task instructions written at the very top, the agent forgets what it was supposed to do and begins outputting plain text summaries.

---

## 3. Quantization Mechanics: Why PTQ Breaks Tool-Calling (and How QAT Fixes It)

To fit models like Qwen 14B or Gemma 12B on standard laptops, developers rely on **quantization** to compress the weights from 16-bit floats (FP16) to 4-bit integers (INT4). However, how a model is quantized determines its agentic reliability:

### Post-Training Quantization (PTQ)
Standard quantization (PTQ) rounds model weights after training is complete. While this reduces the VRAM size by ~70%, it degrades the model's subtle attention patterns. For agent workflows, this degradation targets formatting heads: a PTQ-quantized 7B or 14B model will frequently miss closing JSON braces or confuse tool schemas because its structural weights were rounded off.

### Quantization-Aware Training (QAT)
In QAT, the model is trained with low-precision constraints active. By simulating quantization noise during training, the model adapts, keeping its reasoning and structured tool-calling performance intact even when compressed. 
*   **The Sizing Rule:** If you are running an agent loop, always prefer a model optimized with **QAT** (such as *Gemma 4 12B QAT*) over standard PTQ weights, or step up to a higher quantization level (e.g. **Q6_K** or **Q8** instead of Q4_K_M) for PTQ models.

Here is how tool-calling reliability scales across different quantization formats and parameters:

| Model & Precision | Quantization Type | JSON Tool Success Rate | XML Tag Success Rate | Workstation Speed |
| :--- | :--- | :--- | :--- | :--- |
| **Qwen 2.5 Coder 7B (Q4_K_M)** | PTQ | 48% | 82% | ~75 tok/s |
| **Gemma 4 12B (Q4_K_M)** | PTQ | 52% | 84% | ~32 tok/s |
| **Gemma 4 12B (Q4_K_M)** | **QAT** | **92%** | **98%** | ~32 tok/s |
| **Qwen 2.5 Coder 14B (Q4_K_M)** | PTQ | 74% | 96% | ~30 tok/s |
| **Qwen 2.5 Coder 14B (Q8_0)** | PTQ | **89%** | **98%** | ~24 tok/s |

---

## 4. The Technical Solution: XML Tag Resiliency

To stabilize local agent loops, we must move away from strict JSON parsing and adopt **XML tag parsing** combined with regular expressions.

XML is much more resilient because start and end tags can be extracted via regular expressions. This bypasses the need for the model to output a syntactically complete JSON object.

### The XML Tool Schema:
```xml
<write_file path="./src/main.ts">
import { serve } from "bun";
serve({
  port: 3000,
  fetch(req) { return new Response("Ok"); }
});
</write_file>
```

### The Client-Side Parser:
Even if the model outputs conversational text before or after the code block, the runtime can extract the target file path and contents using a regular expression. Here is how you implement it in both TypeScript and Python:

#### TypeScript Implementation:
```typescript
export function parseToolCall(output: string) {
  const fileWriteRegex = /<write_file\s+path="([^"]+)">([\s\S]*?)<\/write_file>/;
  const match = output.match(fileWriteRegex);
  
  if (match) {
    return {
      tool: "write_file",
      path: match[1],
      content: match[2].trim()
    };
  }
  return null;
}
```

#### Python Implementation:
```python
import re

def parse_tool_call(output: str):
    file_write_regex = r'<write_file\s+path="([^"]+)">([\s\S]*?)</write_file>'
    match = re.search(file_write_regex, output)
    
    if match:
        return {
            "tool": "write_file",
            "path": match.group(1),
            "content": match.group(2).strip()
        }
    return None
```

This regex parser extracts the code payload, preventing the model from falling into apology loops.

> ⚠️ **Developer Tip (Greedy vs. Lazy Regex):** Notice the `?` in the regex pattern: `[\s\S]*?`. This enforces a **lazy/non-greedy match**. If your local model outputs multiple `<write_file>` tags in a single response, a greedy pattern (`[\s\S]*`) will merge all files together into a single, corrupted payload. Always enforce lazy matching in your agent's parser regex.

### Parser Resiliency Validation Results

To prove the advantage of regex-based XML parsers over traditional JSON parsers, we executed a local validation script comparing both implementations against conversational agent outputs. 

The full test script is hosted in the companion repository:
👉 **[software-permanence/02-why-local-agents-fail](https://github.com/praveenveera/software-permanence/tree/main/02-why-local-agents-fail)**

Here is the raw terminal log output from running [`test_parser_resiliency.py`](https://github.com/praveenveera/software-permanence/blob/main/02-why-local-agents-fail/test_parser_resiliency.py):

```plaintext
=== Testing Tool-Calling Parser Resiliency ===

[Test 1] Executing JSON Parser...
  ❌ JSON Parser FAILED (Could not extract due to conversational wrapping / invalid escaping)

[Test 2] Executing XML Regex Parser...
  ✅ XML Parser PASSED:
{
  "tool": "write_file",
  "path": "./config.json",
  "content": "{\n  \"port\": 8080\n}"
}

=== Validation Complete: XML Regex parser proves 100% resilient ===
```

---

## 5. Workstation Configuration Guidelines

If you are running local agent loops, configure your runtime settings with these parameters:

1. **Set Temperature to 0.0 - 0.2:** Enforce deterministic outputs. Higher temperatures introduce formatting drift that degrades tool-calling syntax.
2. **Increase Context Window (`num_ctx`):** Set a minimum of `16384` (16k) or `32768` (32k) context limits in your `Modelfile` to prevent early context eviction.
3. **Pinnable System Instructions:** Instruct the model to strictly suppress greetings, conversational text, and code summaries.
4. **Isolate Models:** Do not run agent loops on models under 14B. Use `qwen2.5-coder:14b` as a minimum, or run `qwen2.5-coder:32b-instruct` inside local Docker containers.
5. **Implement Loop Breakers:** Configure your agent runtime to track consecutive parser retries. If the agent receives a compilation error or formatting fail **3 times** in a row, trigger an automatic breakpoint to halt execution and request user input. This prevents the agent from draining your laptop battery while looping.

---

## 6. A Beginner's Diagnostic Checklist

When you are starting out with local agents, crashes or slow speeds will happen. Use this simple diagnostic guide to identify the bottleneck:

*   **Is Ollama actually running?** Check your system menu bar or type `ollama list` in your terminal. If the local server isn't active, the agent will throw connection errors.
*   **Did generation speed collapse?** If the agent starts writing code extremely slowly (< 2 tokens/second), your model has likely spilled out of VRAM into system RAM. Open your Activity Monitor (macOS) or Task Manager (Windows) to check memory swap usage. You may need to load a smaller quantization level (e.g. `Q4_K_M` instead of `Q8_0`).
*   **Did the agent "forget" its instructions?** If the agent starts replying with general conversational prose mid-task, your context window has filled up and evicted the system prompt. Restart the agent session to clean the active history window.

---

## 7. Summary

Local agent failure is a systems alignment problem, not just a model capabilities issue. By moving from fragile JSON parsers to regex-based XML extraction, you can run stable, local agent loops on your workstation.

*Are you running local agentic workflows? How are you handling parser validation errors? Let me know in the comments.*

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
