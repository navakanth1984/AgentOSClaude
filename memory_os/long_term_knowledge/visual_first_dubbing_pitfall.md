# Pitfall Warning: Visual-First Dubbing in Generative AI Video

## Identified Point of Failure
Attempting to render video clips first and subsequently overlaying voiceover tracks (dubbing) leads to a major credit leak. 

## Rationale
1. **Pacing Mismatch:** Generative video models (like Gemini Omni Flash) produce dynamic motion that cannot easily be stretched or squeezed to fit voiceover narration without editing software.
2. **Re-render Waste:** Directing the video first forces the creator to repeatedly re-prompt and re-render visual clips (wasting Flow credits) in order to align characters' mouth shapes, actions, or transitions to the natural rhythm of the voiceover.
3. **Credit Leak:** Tests indicate a ~40% increase in token and rendering credit usage when aligning audio to video compared to the reverse.

## Mandated Fix
Always generate and lock the voiceover (ElevenLabs) and music background tracks *before* prompting video clip duration or camera tracking.
