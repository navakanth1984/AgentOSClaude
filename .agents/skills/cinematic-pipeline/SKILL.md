---
name: cinematic-pipeline
description: "Cinematic OS Platform — Master orchestrator compiler coordinating Natural Language parsing, SceneManifest compilation, Backend Capability Negotiation, and Prompt Evaluation. Exposes the CinematicService boundary and the Swarm capability-oriented runtime contract."
---
# Cinematic OS Platform SDK
Welcome to the **Cinematic OS** SDK and capability specification. Cinematic OS is a layered compiler platform that translates natural language scene descriptions into deterministic render prompt packets for multiple generative video backends.
---
## 1. Purpose
The core architecture of Cinematic OS is designed around a single guiding principle: **Decouple transport and consumption layers from the compilation runtime.**
Every user interface (REST endpoints, CLI tools, Agent Swarm runtime, and Filmmaking Studio orchestrators) must interact with the compilation engine through the unified orchestration boundary: `CinematicService`.
```text
  Dashboard / UI       REST API        Swarm Runtime       Filmmaking Studio
        │                 │                  │                     │
        └─────────────────┴──────────────────┴─────────────────────┘
                                  │
                           CinematicService
                        ┌─────────┴─────────┐
                        ▼                   ▼
                   Parser Engine     Compiler Pipeline
                        │                   │
                        ▼                   ▼
                  Model Routers       Compiler Passes
                        │                   │
                        ▼                   ▼
                 Model Providers   Negotiated Capabilities
                        │                   │
                        └─────────┬─────────┘
                                  ▼
                          Evaluation Router
```
---
## 2. Public API Reference
The `CinematicService` class exposes four primary thread-safe, immutable methods:
### `async compile_from_text`
Parses raw natural language text, constructs a validated `SceneManifest` intermediate representation (IR), negotiates backend capabilities, and compiles target prompts.
```python
async def compile_from_text(
    self,
    text: str,
    options: CompileOptions,
    context: dict[str, Any] | None = None
) -> CompileResult:
    """
    Args:
        text: Raw natural language scene description or script.
        options: CompileOptions specifying target backend, fps, and multi-shot configuration.
        context: Optional execution metadata dictionary containing request_id, tracing, etc.
    Returns:
        An immutable CompileResult containing the parsed manifest, outputs, diagnostics, and metrics.
    """
```
### `async compile_from_manifest`
Bypasses the natural language parsing stage to compile directly from a pre-constructed `SceneManifest` object.
```python
async def compile_from_manifest(
    self,
    manifest: SceneManifest,
    options: CompileOptions,
    context: dict[str, Any] | None = None
) -> CompileResult:
    """
    Args:
        manifest: Pre-validated SceneManifest object.
        options: CompileOptions configuration.
        context: Execution metadata dictionary.
    """
```
### `async validate_manifest`
Executes the three-stage validation pipeline on a manifest.
```python
async def validate_manifest(
    self,
    manifest: SceneManifest
) -> tuple[bool, list[Diagnostic]]:
    """
    Returns:
        A tuple of (is_valid, list_of_diagnostics).
    """
```
### `get_presets`
Returns a read-only view of target camera and lighting configuration presets.
```python
def get_presets(self) -> dict[str, Any]:
    """
    Returns:
        Structured dictionary containing all active compiler presets.
    """
```
---
## 3. Runtime Compilation Flow
The compilation process is executed as a series of immutable stages:
```text
  [Stage 1: Raw Text] ──▶ NaturalLanguageParser (Model Router / Provider)
                                │
                                ▼
  [Stage 2: Parsed IR] ──▶ ManifestBuilder (Deterministic defaults)
                                │
                                ▼
  [Stage 3: Validation] ──▶ 3-Stage Validator (Schema, Semantic, Compiler)
                                │
                                ▼
  [Stage 4: Negotiation] ──▶ CapabilityRegistry (Capabilities intersection)
                                │
                                ▼
  [Stage 5: Compilation] ──▶ CompilerPasses (SceneGraph, PresetResolver)
                                │
                                ▼
  [Stage 6: Outputs] ──▶ CompileResult (Flow Omni, Higgsfield, ChatGPT prompts)
                                │
                                ▼
  [Stage 7: Evaluation] ──▶ EvaluationRouter (Heuristic & Cloud scoring)
```
---
## 4. Swarm Capability Registration
Cinematic OS registers with the Agent OS Swarm Cluster as a capability-oriented runtime module:
* **Descriptor**:
  - `name`: `"cinematic-pipeline"`
  - `description`: `"Parses natural language scene description to SceneManifest and compiles to visual backend prompts."`
  - `accepts_type`: `str` / `SceneManifest`
  - `returns_type`: `CompileResult`
* **Invocation**:
  - Executed via `CapabilityRegistry.execute("cinematic-pipeline", input_data, options, context)`
  - Encapsulated by `CapabilityContext` carrying unique `request_id`, thread logging, and progress reporting callbacks.
---
## 5. Model Provider Routing
Language generation and scoring tasks are abstracted away from raw model endpoints via the **Hybrid Model Router**:
1. **`GenerationProvider` / `EvaluationProvider` Protocols**: Defines call boundaries for chat completion and scoring endpoints.
2. **Providers**:
   - `OllamaProvider`: Local execution (fallback-ready for local Gemma models).
   - `OpenRouterProvider`: Cloud fallback endpoint.
3. **`RoutingPolicy` Engine**: Matches tasks with providers using one of 7 policies:
   - `LOCAL_FIRST`: Run Ollama, fallback to OpenRouter on error or missing model.
   - `CLOUD_ONLY`: Direct routing to high-fidelity cloud models.
   - `HEURISTIC_ONLY`: Speed-optimized routing with no LLM evaluation step.
---
## 6. Compiler Validation Passes
Every compilation run undergoes a strict three-stage validation pipeline:
|
 Pass
|
 Type
|
 Target
|
 Description
|
|
----
|
----
|
------
|
-----------
|
|
**
Stage 1
**
|
 Schema
|
 Datatypes
|
 Verifies datatypes, non-empty IDs, and range bounds.
|
|
**
Stage 2
**
|
 Semantic
|
 Scene Graph
|
 Verifies coordinate anchors, character placements, and scene graph coherence.
|
|
**
Stage 3
**
|
 Compiler
|
 Constraints
|
 Checks backend constraints (e.g. max beats, voice options, asset limits).
|
---
## 7. Backend Capability Negotiation
A core innovation in Cinematic OS is **Dynamic Capability Negotiation**. Rather than raising hard errors when a scene uses features not supported by a backend (such as multi-shot transitions on a single-shot generator), the compiler dynamically scales the scene manifest downward.
$$	ext{SceneManifest} \cap 	ext{CompileOptions} \cap 	ext{BackendCapabilities} 	o 	ext{NegotiatedCapabilities}$$
For example, compiling a 5-beat manifest for **Higgsfield** (which only supports single-shot outputs):
1. The registry detects Higgsfield's limit of `max_beats = 1`.
2. The negotiation engine caps the manifest timeline to beat `0`.
3. A `warning` diagnostic is appended to the context.
4. Compilation continues successfully with the capped timeline, preventing failures in production.
---
## 8. Extension Guide: Adding a Rendering Backend
To add a new generative backend (e.g. `RunwayGen3`):
1. **Register Capabilities**:
   Open `backend_capabilities.py` and register the capabilities in `CapabilityRegistry`:
   ```python
   CapabilityRegistry.register(
       "runway_gen3",
       BackendCapabilities(
           supported_formats=["mp4"],
           max_duration_sec=10,
           max_beats=3,
           supports_spatial_audio=False,
           supports_multi_shot=True,
       )
   )
   ```
2. **Implement Compile Pass**:
   Modify `dsl_compiler.py` (or subclass the compiler passes) to construct the prompt templates for the new backend:
   ```python
   def _compile_runway(self, context: CompilerContext) -> dict[str, Any]:
       # Read negotiated capabilities from context
       caps = context.negotiated
       # Generate runway prompt using screenplay action and camera presets
       return {"runway_prompt": "..."}
   ```
3. **Expose Target inside `CinematicService`**:
   Ensure `CinematicService` translates compiler outputs into the stable `CompileResult.targets` dictionary.
4. **Register Frontend Tab**:
   Add a toggle button inside `dashboard.html`'s Target Output Prompts panel to view the generated prompt.