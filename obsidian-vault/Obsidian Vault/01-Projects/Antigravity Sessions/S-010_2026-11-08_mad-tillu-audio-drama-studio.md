---
session_id: "S-010"
date: "2026-11-09"
project: "MAD TILLU Audio Drama & Sarvam Voice Studio"
tool: "Antigravity"
status: "✅ Completed"
tags: [session, handoff, audio-drama, sarvam-ai, elevenlabs, voice-matching, mad-tillu]
---

# Session S-010 — MAD TILLU Multi-Engine Audio Drama Studio

## Context
- **Project**: MAD TILLU (DJ Tillu × MAD crossover feature development draft)
- **Tool Used**: Antigravity
- **Worktree**: `setup_sarvam_api`
- **Output Standards**: 24,000 Hz, 16-bit Mono PCM, Native Unicode Telugu

## What Was Accomplished
1. **Calibrated Sarcastic & Witty Delivery for DJ Tillu**:
   - Tested 23 male personas in Sarvam AI. Identified `mani` (`bulbul:v3`) as the exact timbre and swagger match for Siddhu Jonnalagadda. Calibrated pacing to 1.12x–1.16x with rhetorical lifts and sarcastic comedic timing.
2. **Solved Audio Degradation & Metallic Buzzing**:
   - Diagnosed root cause of earlier climax buzzing: Romanized English text caused phonetic dropouts and misidentified words like "emi" as "E-M-I".
   - Converted all screenplay dialogue to native Telugu Unicode script (`ఆ రాడ్ తీయి.`, `సేమ్ బాక్స్... సేమ్ వెయిట్... డోంట్ ఓపెన్`). Verified 100% crystal-clear human speech via `saaras:v3`.
3. **Batch-Synthesized Act Two Master Audio Drama**:
   - **Scene 19-20 (Interval Fallout & The Decoy Ledger)**: Lakshmi and Savitri compare postings in front of Inspector Rao; Tillu and Laddu discover the 25-year decoy message pattern (`scene_19_20_interval_fallout_master.wav`, 57.3s, 2.75 MB).
   - **Scene 25-27 (Bangkok Muay Thai Gym & Anna's Midpoint)**: The brothers find Bunty's shrine, the duplicate passport with Ganesh Kumar Goud, and meet Anna (`scene_25_27_bangkok_midpoint_master.wav`, 45.3s, 2.17 MB).
4. **ElevenLabs Onboarding & Vendor Benchmarking**:
   - Successfully onboarded ElevenLabs via `@elevenlabs/cli` (`onboard check`, verified key ending in `021d`).
   - Discovered and added 5 native Telugu-tagged community voices (`Srinu`, `Sagar`, `Bharadwaj`, `Reddamma`, `Vandana`) to user's library and generated a test table read (`elevenlabs_scene25_27_bangkok_midpoint_master.mp3`).
   - **Forensic Diagnosis of Why ElevenLabs / CosyVoice Sound Artificial**:
     - *ElevenLabs*: Western prosodic algorithms apply unnatural stress and syllable duration curves to Dravidian languages; community voices suffer from room reverb and mic artifacts.
     - *CosyVoice*: CJK/English tokenizer drops non-CJK Indic characters completely.
     - *Sarvam AI*: Native Indian language LLM/TTS understands Telugu sandhi, dental vs. retroflex consonants, and regional dialect rhythm.
5. **Exact Character-to-Actor Voice Match Suite (Sarvam Studio)**:
   - Generated 16 high-fidelity audition takes in `voice_samples/movie_character_auditions/`:
     - **DJ Tillu (Siddhu Jonnalagadda)**: `mani` (1.16x fast sarcastic) vs. `sunny` (1.14x street swagger) vs. `tarun` (1.12x crisp).
     - **Laddu (Vishnu Oi)**: `rohan` (0.96x innocent/plaintive) vs. `sumit` (0.95x soft) vs. `tarun_te_narration` (0.96x grounded).
     - **Anjaneyulu (Muralidhar Goud - Father)**: `ratan` (0.88x gravelly/weary) vs. `anand` (0.88x gentle/apologetic) vs. `ashutosh` (0.86x broken).
     - **Anna (Bangkok Crime Boss)**: `kabir` (0.86x deep baritone) vs. `ratan` (0.82x chilling menace) vs. `tarun_te_narration` (0.88x smooth predator).
     - **Lakshmi (Lakshmi Sujatha - Mother 1)**: `kavitha_te_conversation` (0.96x forensic) vs. `roopa` (0.98x authoritative).
     - **Savitri (Village Mother 2)**: `kavitha_te_narration` (0.88x devout) vs. `priya` (0.90x emotional restraint).

## Current File States
| File | Status | Notes |
|------|--------|-------|
| `batch_act2_studio.py` | ✅ Production | Complete Act Two batch ingestion and table-read rendering pipeline |
| `unified_voice_studio.py` | ✅ Ready | Multi-engine studio combiner (24kHz resampler + dialogue stitcher) |
| `elevenlabs_table_read.py` | ✅ Integrated | ElevenLabs table-read synthesis script with Telugu voice mapping |
| `scratch/audition_movie_characters.py` | ✅ Auditions | 16-take character matching suite across the entire main cast |
| `voice_samples/mad_tillu_act2/` | ✅ Generated | Act Two master scenes (1m 42s total duration) |
| `voice_samples/movie_character_auditions/` | ✅ Generated | 16 actor-matched audition takes in 24kHz studio quality |

## Key Decisions Made
- **Voice Engine**: Selected Sarvam AI as the definitive production engine for Telugu audio dramas due to authentic Indic prosody, regional dialect fluency, and sub-second generation speeds.
- **Audio Fidelity**: Standardized on 24,000 Hz 16-bit Mono PCM across all models and engines.
- **Dialect & Script Integrity**: All Telugu lines must be passed as native Telugu Unicode script to prevent phonetic degeneration.

## Resume Instructions
> When continuing this session:
> 1. Use the calibrated Sarvam voice lineup (`mani` for Tillu, `rohan` for Laddu, `ratan` for Father, `kabir` for Anna, `kavitha` for Mothers).
> 2. To render Act Three (Cards 40–53, The Wedding Climax), run `python.exe batch_act2_studio.py` with the expanded manifest.
