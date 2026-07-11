# Google Anti-Gravity
> Rebuilt multi-agent architecture and operational framework powered by Gemini 3.5 Flash.

## Overview
Google Anti-Gravity has transitioned from a single AI-powered code editor into five decoupled components that operate off a shared agent engine. This modular approach allows for flexible, multi-modal interaction, parallel agent execution, and isolated git workspaces.

Source: [google-antigravity-rebuild.md](../sources/technical/google-antigravity-rebuild.md)

---

## Architectural Components
The system is divided into five specialized interfaces and integration layers:

1. **Standalone Desktop App:** Designed purely for orchestrating and managing execution flow, intentionally excluding a code editor. It serves as a dedicated command center for users to:
   * **Launch & Monitor:** Initiate agents, track live progress, and run multiple agents concurrently.
   * **Schedule:** Set background tasks and routines to run automatically.
   * **Automate Work Trees:** Native integration to set up Git work trees automatically for new conversations.
2. **The Original IDE:** The traditional integrated development environment, recommended when manual code editing alongside the AI is preferred.
3. **Command Line Interface (CLI):** A native Go-based CLI allowing users to run agents directly from the terminal, including a migration command to port old configurations.
4. **Developer SDK:** A software development kit designed for building custom applications on top of the Anti-Gravity engine.
5. **Managed Agents API:** An API interface to spin up an agent in a fully sandboxed and isolated environment with a single API call.

Source: [google-antigravity-rebuild.md](../sources/technical/google-antigravity-rebuild.md)

---

## Workspace Isolation (Git Work Trees)
Anti-Gravity natively integrates with Git work trees to provide isolated, temporary environments for primary agents and sub-agents:
* **Background Setup:** Starting a new conversation with the "new work tree" option in the desktop app triggers an automatic work tree setup in the background.
* **Main Folder Protection:** Confining agents' work to these separate trees ensures the main working folder stays clean and avoids pollution or corruption.
* **Sub-Agent Isolation:** When tasks are delegated, the system automatically creates dedicated work trees for each sub-agent.
* **Hands-Free Cleanup:** Temporary work trees are automatically cleaned up and deleted once the tasks are finished.

Source: [google-antigravity-rebuild.md](../sources/technical/google-antigravity-rebuild.md)

---

## Sidebar & UI Rework
The desktop app's sidebar interface has been redesigned to support complex multi-agent orchestration across projects:
* **Work Tree Toggle:** Users can manually toggle work tree names on or off in the sidebar, which is highly beneficial when running different agents across multiple projects to distinguish between isolated environments.
* **Conversation Grouping:** Conversations can be grouped by project, status, or recency.
* **Project Renaming:** The interface supports direct renaming of projects.

Source: [google-antigravity-rebuild.md](../sources/technical/google-antigravity-rebuild.md)

---

## Operational Model & Sub-Agent Orchestration
The engine is powered by **Gemini 3.5 Flash** as its default model to enable fast, low-latency execution of complex workflows.

### Sub-Agent Lifecycle
Unlike the legacy architecture, the rebuilt engine spawns specialized **sub-agents** dynamically to solve subsets of larger tasks.
* **Types:** Sub-agents can be built-in specialists, exact clones of the main agent, or dynamically-defined custom agents.
* **Permissions & Isolation:** They inherit the main agent's permission boundaries but execute in fully isolated environments.
* **Workspace Isolation:** Supported natively by Git work tree automation.

Source: [google-antigravity-rebuild.md](../sources/technical/google-antigravity-rebuild.md)

---

### Key Workflow Benefits
* **Parallel Execution:** Large tasks are split and processed simultaneously by multiple sub-agents, reducing overall time-to-completion.
* **Context Isolation:** Memory and context limits remain clean for the main agent, avoiding performance degradation under complex multi-step tasks.
* **Clean Workspace:** Native Git worktree automation handles sandbox scratch spaces seamlessly.

Source: [google-antigravity-rebuild.md](../sources/technical/google-antigravity-rebuild.md)
