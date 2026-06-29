---
title: Run a Private AI Coding Agent Locally: Setup & Design with Ollama, OpenCode, and Custom Workspace Skills
published: false
description: Build and configure a fully private local AI coding agent on your workstation using OpenCode, Ollama, and Qwen 2.5 Coder. Design custom instructions and workspace skill files.
tags: opencode, ollama, qwen, agents
canonical_url: https://medium.com/@praveenveera92/reclaiming-developer-autonomy-architectural-design-and-setup-of-a-local-ai-coding-agent
---

![Local AI Agent Architecture - At a Glance](https://raw.githubusercontent.com/praveenveera/software-permanence/main/assets/03-local-ai-enterprise.png?v=2)

Once you have local autocomplete and chat running inside your IDE, the next step is transitioning to autonomous execution. Setting up a local coding agent running directly inside your terminal or editor gives you a private, offline partner capable of executing shell commands, refactoring files, and diagnosing compilation errors.

This guide focuses on the workspace design, custom instructions, and domain-specific skills required to orchestrate a reliable local agent using **Ollama** and **OpenCode**.

---

### 🔰 What is an "AI Agent" (For Beginners)?

If you have only used ChatGPT or Claude in a browser, a coding agent behaves differently. Standard chat systems only output text; you must manually copy and paste the code block into your editor. 

An **AI agent** has "hands." It integrates directly with your workstation's filesystem and terminal. Instead of just suggesting code, the agent runs an active execution loop: it reads files, writes code modules, executes compiler test suites, inspects error outputs, and iterates autonomously until the task is complete.

---

## 1. The Local Agent Architecture

A private agentic workspace coordinates model outputs with local system execution. Here is the operational design of the loop:

```
┌────────────────────────────────────────────┐
│                 Developer                  │
│        Terminal / VS Code / OpenCode       │
└─────────────────────┬──────────────────────┘
                      │
┌─────────────────────▼──────────────────────┐
│                  OpenCode                  │
│  - Agent execution loop                    │
│  - Context window manager                  │
│  - Project instruction parser              │
│  - Tool permission registry                │
│  - Skills / specialist agents              │
└──────────────┬───────────────┬─────────────┘
               │               │
     ┌─────────▼──────┐  ┌────▼─────────────┐
     │ Project Repo   │  │ Local OS Tools   │
     │ - Source code  │  │ - Terminal bash  │
     │ - Docs         │  │ - Git versioning │
     │ - Test suites  │  │ - Linters        │
     └────────────────┘  └──────────────────┘
                      │
┌─────────────────────▼──────────────────────┐
│                   Ollama                     │
│           Local model inference            │
│       Qwen / Llama coding models           │
└────────────────────────────────────────────┘
```

1. **The Developer:** Initiates a task (e.g., "Add a health-check route") in the terminal interface.
2. **OpenCode (Agent Interface):** Reads global instructions, loads domain-specific skills, parses the repository directory, and maps available tools.
3. **Ollama (Local Runtime):** Handles prompt inference, generating tool-call tags in XML or JSON format.
4. **Local Tools:** The agent runtime parses the tags, requests developer permission, and executes the files or bash commands natively.

---

## 2. Step 1: Interface & Local Runtime Link (OpenCode)

OpenCode acts as the execution bridge, routing prompt contexts to your local Ollama API. Configure it by editing your workspace configuration file:

```json
{
  "provider": "ollama",
  "endpoint": "http://localhost:11434",
  "model": "qwen2.5-coder:14b-instruct",
  "default_agent": "builder",
  "system_instructions_path": "./.agents/instructions.md"
}
```

*Note: For the local model settings, we run the instruct weights via Ollama configured with a minimum context window (`num_ctx 16384`) and a deterministic temperature (`0.0`), as detailed in our first guide.*

---

## 3. Step 2: Project Instructions & Guardrails

To prevent the agent from executing destructive commands or writing non-compliant code, you must define project-specific guardrails. Create a project instructions file (`.agents/instructions.md`):

```markdown
# Project Instructions

## Architecture & Stack
- Frontend: Next.js (App Router, TypeScript)
- Backend: FastAPI (Python 3.11, Pydantic v2)
- Database: PostgreSQL

## Core Rules
- Do not modify database schemas without explicit permission.
- Do not introduce new third-party dependencies without explaining the rationale.
- Run linting and tests before proposing a completed task.

## Code Style
- Use TypeScript strict mode for frontend modules.
- Use asynchronous database operations (async/await) in Python.
- Add unit tests for all new business logic.

## Safety Constraints
- Never print secrets, API tokens, or environment files to standard out.
- Do not delete source files unless explicitly requested.
- Present a concrete plan before executing multi-file changes.
```

---

## 4. Step 3: Domain-Specific Skills (Specialist Guides)

Lightweight local models (like 14B parameters) can struggle with complex routing patterns or framework boilerplate. By organizing your codebase with a dedicated `skills/` directory, you equip your agent with specialized recipes:

```
project-root/
├── .agents/
│   └── instructions.md
└── skills/
    ├── nextjs-feature.md
    ├── fastapi-api.md
    ├── database-migration.md
    └── test-writing.md
```

Here is a sample skill definition file for writing endpoints (`skills/fastapi-api.md`):

```markdown
# FastAPI API Skill

When adding a new API endpoint to the backend:

1. Check existing router imports in `app/main.py`.
2. Define Pydantic request and response schemas in `app/schemas/`.
3. Use async database sessions with `sqlalchemy.ext.asyncio`.
4. Include explicit error handlers using `HTTPException` with clear detail messages.
5. Create a corresponding test file in `tests/test_api.py`.
6. Run linting and verify API responses before marking the task complete.
```

When a user prompts the agent to add a backend route, OpenCode automatically appends this skill file to the active system context, ensuring the model matches your codebase's architectural pattern without bloating the base system prompt.

---

## 5. Step 4: Tool Risk & Permission Registry

Giving an agent system access introduces risks. You must categorize available tools by risk level to prevent accidental system changes:

| Tool | Purpose | Risk Level | Safety Guideline |
| :--- | :--- | :--- | :--- |
| **Read Files** | Inspects code structures and configuration. | Low | Safe to execute automatically. |
| **Search Repo** | Locates variable definitions and file locations. | Low | Safe to execute automatically. |
| **Git Diff/Status** | Analyzes workspace changes. | Low | Safe to execute automatically. |
| **Run Tests** | Executes unit tests to validate code. | Medium | Restrict execution duration to prevent infinite loops. |
| **Modify Files** | Edits source code or templates. | Medium | Require manual review or run inside a Git sandbox. |
| **Delete Files** | Cleans up obsolete components. | High | Always prompt for explicit human confirmation. |
| **Shell Commands** | Runs compiler commands, builds, or scripts. | High | Never automate; require step-by-step developer approval. |

> 🛡️ **The Git Sandbox Rule:** Always initialize a Git repository and commit your active changes before letting a local agent write code. If the agent goes rogue, deletes files, or writes buggy code, you can roll back your entire workspace instantly by running:
> ```bash
> git reset --hard
> ```

---

## 6. Detailed Agent Workflow Trace

To understand how the agent uses instructions, skills, and tools under the hood, here is a trace of the execution loop when implementing a feature:

**User Prompt:** *"Add a health-check endpoint to the FastAPI service."*

```
1. Read Directory  ──> Locates app/main.py and skills/fastapi-api.md
2. Parse Rules     ──> Identifies FastAPI backend framework rules
3. Read main.py    ──> Finds existing router configuration
4. Propose Plan    ──> Prints target changes to terminal for approval
5. Edit Files      ──> Inserts /health endpoint using async route
6. Write Test      ──> Creates test_health_check in tests/test_api.py
7. Run CLI Command ──> Executes: pytest tests/test_api.py (Requires user approval)
8. Git Diff Check  ──> Displays final diff output and completes loop
```

---

## 7. Parallel Parser Implementations (Tool Calling)

Local agents use regular expressions to parse XML tool commands generated by the local model. Here is how you can implement a robust, non-greedy tool call extractor in both TypeScript and Python. *(For an in-depth analysis of why XML tags are used to prevent format failure loops, refer to our previous guide)*.

### TypeScript Implementation
```typescript
export function parseToolCall(output: string) {
  // Non-greedy regex prevents merging multiple distinct tags
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

### Python Implementation
```python
import re

def parse_tool_call(output: str):
    # Non-greedy regex pattern (.*?) avoids greedy tag merges
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

---

## 8. Live Validation & GitHub Repository

To demonstrate the viability of this design, the complete setup has been packaged and executed locally on an Apple Silicon workstation. 

### Companion Repository Code
All configuration files, project rules, specialized skills, and the active test-runner script are hosted in the companion repository:
👉 **[software-permanence/03-local-agent-setup](https://github.com/praveenveera/software-permanence/tree/main/03-local-agent-setup)**

### Step-by-Step Execution Logs
By running the local python simulator [`run_agent_loop.py`](https://github.com/praveenveera/software-permanence/blob/main/03-local-agent-setup/run_agent_loop.py), we triggered `qwen2.5-coder:14b` to read the codebase, parse our rules, write the route, and run unit tests. Here are the raw terminal logs from the execution:

```plaintext
=== Launching Local Agent Run Simulation ===
[Step 1] Loading workspace configs, guidelines, and skills...
[Step 2] Reading current workspace status...
[Step 3] Querying local model 'qwen2.5-coder:14b' via Ollama...
  └─ Generation completed in 4.71 seconds.
  └─ Prompt Tokens: 407, Generation Tokens: 135
[Step 4] Extracting tool call payload from model output...
  └─ Parsed Action: write_file to 'workspace/app/main.py'
[Step 5] Writing modified code to local workspace...
  └─ Updated 'workspace/app/main.py' successfully.
[Step 6] Adding health-check assertion to unittest suite...
  └─ Appended 'test_read_health' test case.
[Step 7] Running unittest suite to validate changes...

=== Workspace Test Results ===
Ran 2 tests in 0.013s
OK

[Pass] Agent validation completed with all test assertions passing!
```

### The Generated Endpoint Code
Here is the exact FastAPI router code created autonomously by the local model during the run, showing that it followed the async rules and exception detail handlers specified in `skills/fastapi-api.md`:

```python
@app.get("/health")
async def health_check():
    try:
        # Simulate a database check or other critical resource
        # For demonstration, we'll just return OK
        return {"status": "OK"}
    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal Server Error") from e
```

---

## 9. Hard-Earned Lessons: What Did Not Work Well

Running autonomous agent loops on local hardware highlighted several unique operational hurdles:

* **Tool Permission Fatigue:** Requiring user confirmation for high-risk tools like bash commands is necessary for safety, but it creates developer fatigue. You find yourself repeatedly hitting "Y" during compilation loops.
* **Recursive Error Loops:** If a model writes buggy code and the test step fails, smaller models can get stuck in a recursive loop (apologizing, rewriting the same bug, running tests, and failing again). Setting a hard execution breaker (halting after 3 failures) is critical.
* **Lack of Isolation:** Unlike cloud sandboxes, a local agent runs directly on your machine. If it runs `npm install`, it compiles binaries on your host OS. Containerizing your workspace or running it inside a Docker dev container is highly recommended for security.
* **Context Overload:** Attaching multiple skill files and file summaries to the prompt quickly eats up the 16k context window. You must actively prune inactive files from the agent's history to maintain generation accuracy.

---

## Summary

Designing a local coding agent gives you complete privacy and data sovereignty. By configuring Ollama with deterministic parameters, establishing clear instructions, organizing workspace skills, and enforcing the Git Sandbox rule, you can run a reliable agentic environment directly on your local workstation.

*Are you running local coding agents on your machine? What model sizes have worked best for your workflow? Let's discuss in the comments.*

---

**Hi, I'm Praveen Veera.** I build practical AI systems, specializing in Enterprise AI Platforms, Local LLMs, and Dev Tools.

Read my notes:
* **Substack Newsletter:** [softwarepermanence.substack.com](https://softwarepermanence.substack.com)
* **LinkedIn:** [linkedin.com/in/praveen-veera-6ab22567](https://www.linkedin.com/in/praveen-veera-6ab22567/)
* **GitHub (Companion Code):** [github.com/praveenveera/software-permanence](https://github.com/praveenveera/software-permanence)
* **Dev.to:** [dev.to/praveen_builds](https://dev.to/praveen_builds)
* **Medium:** [medium.com/@praveenveera92](https://medium.com/@praveenveera92)
* **Instagram:** [@praveen.builds](https://instagram.com/praveen.builds)
* **Hashnode:** [hashnode.com/@praveen-builds](https://hashnode.com/@praveen-builds)
