# Generative Production Workflows
> Best practices and identified pitfalls for creating generative media.

## Audio-First for Generative Video

A core principle for efficient generative video production is to follow an **audio-first** workflow.

### Pitfall: Visual-First Dubbing
- **Problem:** Rendering video clips first and then attempting to dub voiceover narration afterwards leads to significant inefficiency and wasted resources.
- **Reason:** It is difficult to align pre-rendered video pacing with a voiceover track without extensive re-rendering. This process can lead to a ~40% increase in token and rendering credit usage.
- **Mandated Solution:** Always generate and lock the voiceover (e.g., using ElevenLabs) and any background music *before* prompting the video generation model for specific clip durations, camera movements, or character actions.

This ensures the visual generation is timed to a fixed audio track, eliminating costly re-renders for pacing adjustments.

## Connections
- This principle was identified during the production of the [Vaayuthram Vaalagaathram](vaayuthram-vaalagaathram.md) project.
