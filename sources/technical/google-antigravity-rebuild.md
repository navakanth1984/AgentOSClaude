Google Anti-Gravity was completely rebuilt from a single AI-powered code editor into **five separate pieces that all work off the same shared agent engine**. This new infrastructure allows users to interact with the system in different ways depending on their needs, rather than treating AI agents as a side feature bolted onto a single app.

The five components of the new architecture are:

1. **Standalone Desktop App:** This application intentionally **does not include a code editor**. It serves as a dedicated command center for managing and orchestrating AI agents, specifically built for users who prefer to "direct traffic" rather than manually write code. 
   
   The main benefits of using the desktop app include:
   * **Launching and Monitoring Agents:** The interface is designed purely to let you launch agents, watch their progress, and comfortably run several of them at the same time.
   * **Scheduling Background Work:** You can use the app to schedule tasks for your agents to run automatically in the background.
   * **Seamless Work Tree Setup:** The desktop app integrates natively with Git work trees. When you start a new conversation, you can simply select the "new work tree" option, and the app will automatically configure an isolated environment in the background before the conversation even begins.
2. **The Original IDE:** This is the traditional integrated development environment. Google still recommends using this component **if you want to manually edit the code yourself** alongside the AI.
3. **Command Line Interface (CLI):** Built natively in Go, the new CLI allows users to **run agents directly from their terminal**. This replaces the older Gemini CLI, and Google provides a built-in migration command to automatically transfer your old configurations to the new tool.
4. **Developer SDK:** A Software Development Kit designed for developers who want to **build custom applications on top of the entire Anti-Gravity system**.
5. **Managed Agents API:** An interface that allows you to **spin up an agent in its own isolated environment with just a single API call**.

**How the System Operates**

At the core of this architecture is a massive shift in how the agents process tasks. The system is entirely powered by a new default model, **Gemini 3.5 Flash**, which runs much faster than previous models and makes complex multi-agent workflows viable.

The engine's standout feature is its ability to utilize **sub-agents**. While the older system essentially only offered a single main agent and a browser helper, the new architecture allows the main agent to **spawn multiple sub-agents on the fly to tackle different pieces of a large problem at the same time**.

These sub-agents can be built-in specialists, exact clones of the main agent, or entirely new agents defined in the moment based on the specific task. Each sub-agent inherits the main agent's permissions and operates in its own completely isolated space. 

**Native Git Work Tree Integration**

Anti-Gravity natively integrates with Git work trees to provide isolated, temporary environments for AI agents to operate in, ensuring the primary working files remain untouched.
* **Background Setup:** When starting a new conversation in the desktop app, you can select "new work tree," and Anti-Gravity automatically configures the environment in the background before the conversation starts.
* **Protecting Your Main Folder:** By confining agent execution to these separate trees, the main working folder stays completely clean and avoids getting messy or corrupted.
* **Sub-Agent Isolation:** If the main agent delegates parts of a task to sub-agents, the system automatically creates dedicated Git work trees for each sub-agent, giving them their own isolated spaces to function.
* **Hands-Free Cleanup:** Once the agents or sub-agents finish their tasks, the system automatically cleans up and deletes the temporary Git work trees, removing any need for manual management.

**Sidebar Interface Rework**

The desktop app features a reworked sidebar interface to support multi-agent orchestration across different workspaces:
* **Work Tree Toggle:** Users can manually toggle the visibility of work tree names on or off in the sidebar. This helps easily distinguish between various isolated environments when running multiple agents across projects.
* **Conversation Grouping:** Conversations can be grouped by project, by status, or by how recent they are.
* **Project Renaming:** The interface allows users to rename projects dynamically.

Ultimately, these sub-agent and isolated workflows are made viable by the underlying engine upgrade to the **Gemini 3.5 Flash model**, whose high processing speed ensures that running multiple agents in parallel feels seamless and responsive.
