# Workspace OS — Sprint 7 Execution Plan

**Status:** Proposed 2026-07-18 (Sprint 6 completion baseline)
**Supersedes:** Monolithic Azure Integration roadmap.
**One-line summary:** *Establish the underlying architecture of a Spatial Operating System for Thought, prioritizing event loops and capability buses over ad-hoc features.*

---

## 1. The 4-Layer Workspace Architecture

To build a sustainable platform without getting bogged down in monolithic technical stacks, we divide development into four decoupled semantic layers:

```
┌─────────────────────────────────────────────────────────┐
│ Layer 4: Collaboration (Yjs, WebRTC, SignalR Sync)     │
├─────────────────────────────────────────────────────────┤
│ Layer 3: AI Workspace (Foundry Agents, Search Index)    │
├─────────────────────────────────────────────────────────┤
│ Layer 2: Knowledge Workspace (Metadata, Relationships)  │
├─────────────────────────────────────────────────────────┤
│ Layer 1: Spatial Workspace (Three.js, SAS, HUD)         │
└─────────────────────────────────────────────────────────┘
```

1.  **Layer 1: Spatial Workspace (Current, 90% Complete)**: Owns 3D rendering, canvas, selection, camera, and basic spatial orientation (SAS v1.0). **Status: Frozen** except for minor bug fixes.
2.  **Layer 2: Knowledge Workspace (Next Priority)**: Transitions objects from simple visual meshes to full Knowledge Nodes with Metadata, Relationships, History, Permissions, and Vector Embeddings.
3.  **Layer 3: AI Workspace**: Implements context-aware reasoning (e.g. "organize this cluster", "find contradictions") utilizing Azure AI Search and Foundry Agent Services.
4.  **Layer 4: Collaboration**: Integrates Yjs multiplayer cursors and SignalR event sync *only* after data structures in Layer 2/3 stabilize.

---

## 2. The Capability Bus Pattern

Nothing talks directly to anything else. The **Capability Bus** manages all state changes and propagates events to subsystems:

```text
Object Created/Moved
      │
      ▼
┌──────────────┐
│  Event Bus   │
└──────┬───────┘
       ├─────────────────┼───────────────────┤
       ▼                 ▼                   ▼
┌──────────────┐  ┌──────────────┐   ┌───────────────┐
│ Search Index │  │ Graph Memory │   │ Collaboration │
└──────────────┘  └──────────────┘   └───────────────┘
```

---

## 3. Sprint 7 Deliverables

### A. Event Bus 2.0 & Capability Bus
*   Establish a global `EventBus` that streams workspace events (creation, movement, relationship mutations, selection).
*   Create a plugin registry where capabilities subscribe to specific events.

### B. Knowledge Objects (Layer 2)
*   Define a standardized data structure for workspace nodes:
    ```typescript
    interface KnowledgeNode {
      id: string;
      type: string;
      visual: VisualProperties; // mesh, position, scale
      metadata: Record<string, any>;
      relationships: Relationship[];
      history: VersionHistory[];
    }
    ```

### C. IKOS Plugin SDK
*   Create a simple plugin registration hook to keep the core lightweight:
    ```typescript
    registerCapability({
      id: "planner-agent",
      onWorkspaceOpen(ws) {},
      onObjectCreated(obj) {},
      onSelectionChanged(selection) {},
    });
    ```

---

## 4. Prioritized Tool Integration Roadmap

| Integration Phase | Component | Technology | Cost / Footprint |
| :--- | :--- | :--- | :--- |
| **Phase 1 (Search)** | Workspace Search | Azure AI Search | Paid (Basic SKU ~₹6k/mo) |
| **Phase 2 (Layouts)** | Auto Layouts | ELK.js | Open Source (₹0) |
| **Phase 3 (Agents)** | Workspace Assistants | Foundry Agent Service | Paid (Consumption) |
| **Phase 4 (Sync)** | Multiplayer | Yjs / SignalR | Open Source / Paid |
