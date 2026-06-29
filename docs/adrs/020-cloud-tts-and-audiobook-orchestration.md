# ADR-020: Cloud TTS Integration and Audiobook Orchestration

## Status

Accepted — implemented across the v1.1.0 P1 milestone (Sarvam engine, audiobook
orchestrator) and P2 governance pass (this record).

## Context

The V1.1 speech subsystem froze a hardened synthesis DAG (`SpeechService`) with
typed contracts, deterministic caching, per-voice routing, and per-chunk
resumability. Two capabilities sat outside that core and needed first-class
designs:

1. **Cloud / network TTS engines.** The local engines (Kokoro, Piper) load a
   model file from disk. Indian-language synthesis (Telugu, Hindi, Tamil, and 8
   more) is served by **Sarvam**, a hosted API with no local model. We needed a
   way to add a network engine without special-casing the pipeline.
2. **Book-level orchestration.** The legacy `audiobook_pipeline.py` monolith
   (since removed) produced full audiobooks. The V1.1 DAG only knows about a
   single job; it has no concept of "a book of ordered chapters." We needed a
   thin layer that composes the DAG rather than reimplementing synthesis.

## Decision

### 1. Cloud engines implement the same `TTSEngine` protocol (ADR-014)

`SarvamEngine` is a drop-in alongside `KokoroEngine`/`PiperEngine` — the pipeline
sees only the protocol, not the transport. The only network-specific divergences
are isolated behind the protocol methods:

- **`validate_model()` checks for `SARVAM_API_KEY`** instead of a model file on
  disk. There is no `model_path`; a synthetic `sarvam://bulbul:v3` identifier is
  used so the performance-profiler's `_engine_version()` has a stable value.
- **Model:** `bulbul:v3`, sample rate **22050 Hz**, default speaker `rohan`
  (verified across all 11 advertised languages). 38 speakers are exposed for
  multi-speaker casting via the voice map.
- **Speed maps to the provider's `pace` parameter**; gender metadata is carried
  in `EngineCapabilities`.

This keeps "is it cloud or local?" a property of the *engine*, never a branch in
the DAG.

### 2. Segment chunking respects per-engine request limits

`bulbul:v3` enforces a soft per-request cap (`max_text_length = 1000`
characters). The engine chunks text above that limit before issuing requests and
concatenates the returned audio. The limit is declared in `EngineCapabilities`
so the routing/segmentation stages can reason about it generically rather than
hard-coding a Sarvam constant elsewhere.

### 3. The audiobook orchestrator composes `SpeechService`, it does not replace it

`agent_os/speech/audiobook.py` owns **only** what the DAG does not:

- **Chapter resolution** — a single file (optionally split on `Chapter N`
  markers into `src_chapters/`), or every `.txt`/`.md` in a directory, ordered.
- **One `SpeechService` job per chapter** — synthesis, caching, and per-chunk
  resumability stay in the DAG, so a re-run skips already-synthesized chunks for
  free.
- **Stitching** chapter WAVs into one `book.wav` with `CHAPTER_GAP_SEC` (0.7 s)
  of inter-chapter silence.
- **Optional MP3 export** via `ffmpeg`.
- **A stable `audiobooks/<name>/` layout + manifest**, plus optional parallel
  chapter processing (`concurrent.futures`).

## Consequences

- **Pros:**
  - Adding a cloud provider is "implement the protocol + declare capabilities" —
    no pipeline changes. The 22050 Hz / pace / chunking specifics never leak.
  - Resumability and caching are inherited, not reimplemented, so the audiobook
    layer stays small and the monolith stays deleted.
  - Per-engine limits (text length, speaker set, gender) are data in
    `EngineCapabilities`, keeping the routing layer engine-agnostic.
- **Cons:**
  - Network engines add a failure mode the local engines do not have (API
    auth/availability); callers must handle `validate_model()` raising when
    `SARVAM_API_KEY` is absent.
  - MP3 export depends on `ffmpeg` being on PATH; it is optional and degrades to
    WAV-only when missing.
