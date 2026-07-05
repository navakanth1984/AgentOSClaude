# Audio-First Animation Workflow for Low-Budget AI Video Production

## Strategy Overview
Under tight credit or budget constraints in tools like Google Flow (Gemini Omni Flash/Veo 3.1) and ElevenLabs, visual assets must be generated around pre-recorded audio timelines, rather than generating visuals first and trying to overlay audio post-hoc.

## Approved Protocol
1. **Script Timeline Mapping:** Write the complete script and map out rough scene durations.
2. **Audio-First Generation (Voiceover & Dubbing):**
   * Generate character voices and narrator tracks using ElevenLabs *first*.
   * Extract the exact timestamps of phrases, pauses, and sound cues from the generated audio files.
3. **Timed Video Prompting:**
   * Write video prompts in Google Flow that specify actions synced directly to the audio timestamps (e.g., `"Hanuman leaps on the downbeat, mid-air for exactly 3 seconds, landing on second 4."`).
   * Match camera movements and edits to the tempo (BPM) of the background track.
4. **Free Image Sandboxing:**
   * Run initial prompt experiments on free models (e.g. Nano Banana 2) to lock in characters, colors, and art style.
   * Do not consume video render credits until the static keyframe composition is fully approved.
5. **Video Seed Reference:** Use the finalized free images as reference/seed frames for the video generator.
