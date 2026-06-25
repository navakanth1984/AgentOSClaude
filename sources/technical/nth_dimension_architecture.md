# Nth Dimension Academy - Dialogflow CX & Vertex AI Architecture

## Overview
This architecture deploys a production-grade Conversational AI agent for the **Nth Dimension Academy** website. The agent will serve as a teaching assistant for DP-600, DP-700, DP-750, DP-800, and Agent OS, utilizing your massive pool of Google Cloud credits (both the GenAI App Builder and Dialogflow CX credits).

## Component Architecture

### 1. The Brain: Vertex AI Search (GenAI App Builder)
Instead of feeding notes into a Python script, we will upload your Obsidian folders (DP-600, 700, 750, 800, Agent OS) directly into a **Vertex AI Data Store**. 
* **Why?** It acts as an enterprise-grade Retrieval-Augmented Generation (RAG) system. It automatically chunks, embeds, and searches your educational material.
* **Cost:** Covered by your ₹94,812 GenAI App Builder credit.

### 2. The Conversational Engine: Dialogflow CX
We will create a Dialogflow CX Agent and link it directly to the Vertex AI Data Store. We will configure it as a "Data Store Agent" (a generative fallback agent).
* **Why?** It manages user sessions, conversational memory, and safety filters automatically without you needing to write backend Python code.
* **Cost:** Covered by your ₹56,729 Dialogflow CX credit.

### 3. The Interface: Dialogflow Messenger (Web UI)
Google provides a pre-built web component called **Dialogflow Messenger**. We will embed a small snippet of HTML/JS into the Nth Dimension Academy website.
* **Speech-to-Text:** We do **not** need a separate Vertex AI API key for speech! Dialogflow Messenger has built-in microphone support. When users click the microphone icon, their voice is streamed directly to Dialogflow CX.
* **Cost:** The audio processing is covered specifically by the "Audio session for interacting with Dialogflow CX agents" SKU listed in your credits!

---

## Implementation Roadmap (Our Next Steps)

### Phase 1: Data Preparation
We need to aggregate the markdown files for DP-600, DP-700, DP-750, DP-800, and Agent OS from your local vault into a single folder, and upload them to a Google Cloud Storage bucket.

### Phase 2: Vertex AI Setup
We will use the Google Cloud Console (or `gcloud` scripts) to create a **Vertex AI Search Data Store** and point it at the Cloud Storage bucket so it can index all the educational material.

### Phase 3: Dialogflow CX Configuration
We will create the Dialogflow CX agent, configure its "Persona" (e.g., *You are an expert instructor for Nth Dimension Academy...*), and link it to the Data Store.

### Phase 4: Website Integration
We will generate the Dialogflow Messenger HTML snippet and inject it into the Nth Dimension Academy website codebase, enabling the text and voice (microphone) UI.
