# Nth Dimension Academy — Conversational AI
> Architecture for a teaching-assistant agent on the Nth Dimension Academy site, built on Google Cloud RAG.

## Summary
A production conversational agent that answers student questions on DP-600, DP-700, DP-750, DP-800, and Agent OS. The design deliberately avoids custom Python backends, leaning on managed Google Cloud services funded by existing credits.

## Details
- **Brain — Vertex AI Search (GenAI App Builder)**: Obsidian course folders are uploaded into a Vertex AI Data Store, which auto-chunks, embeds, and retrieves — an enterprise RAG layer rather than a hand-rolled script.
- **Engine — Dialogflow CX**: a "Data Store Agent" (generative fallback) linked to the Vertex store; handles sessions, conversational memory, and safety filters with no backend code.
- **Interface — Dialogflow Messenger**: a prebuilt HTML/JS web component embedded in the site, with built-in microphone speech-to-text (no separate speech API key needed).
- **Roadmap**: (1) aggregate course Markdown from the vault → GCS bucket; (2) create the Vertex Data Store over that bucket; (3) configure the Dialogflow CX agent persona + link; (4) inject the Messenger snippet into the site.
- Cost is covered by GenAI App Builder and Dialogflow CX credits.
- Source: [nth_dimension_architecture.md](file:///C:/Users/navka/navakanth001/sources/technical/nth_dimension_architecture.md)

## Connections
- The site itself is an active project at the repo root: `nthdimensionacademy/` and `nth-dimension-react/`.
- Course content overlaps [Microsoft Fabric (DP-700)](fabric-dp700.md).
- Shares the RAG-over-Markdown approach with [OKF Bundle Generator](okf-bundle-generator.md); contrasts with the unofficial-API approach in [NotebookLM Bridge](notebooklm-bridge.md).
