# Sprint 3B UX Review (Director Studio V2 - Gate C)

*This document captures friction points logged during a simulated real-user validation pass (Pass 6 & 7) of Director Studio V2's Experience Layer. The goal is to view the app through the eyes of a filmmaker, not a developer.*

## Pass 6 — Real User Validation

### 1. Creating a Short (YouTube Shorts)
**Flow:** Welcome -> "YouTube Shorts" -> 9:16 Aspect Ratio -> 30s Runtime -> Name & Idea -> Create
- **Friction (Confusing):** The "Target Runtime" defaults to 15s. While selecting 30s is easy, the disclaimer *"The backend currently tracks runtime in whole minutes..."* breaks immersion. It sounds like an error rather than a creative choice.
- **Friction (Slow):** Typing the "Idea" text area feels slightly detached from the "Name" input. The jump between the two could be smoothed.
- **Expectation:** I'd expect to just write a prompt and let the app figure out the name, or have the name auto-generate based on the idea if left blank.

### 2. Creating a Video (YouTube Video)
**Flow:** Welcome -> "YouTube Video" -> 16:9 Aspect Ratio -> 5 min Runtime -> Details -> Create
- **Friction (Confusing):** The "Provider" dropdown defaults to a backend fallback chain. As a filmmaker, I don't care about "OpenRouter" or "MockProvider" unless something breaks. It feels too technical for a creative wizard.
- **Expectation:** I'd expect just a "Quality vs Speed" toggle, or no provider choice at all unless I explicitly open an "Advanced Settings" drawer.

### 3. Creating Images
**Flow:** Welcome -> "Images" -> 1:1 Aspect Ratio -> Create
- **Friction (Slow):** Since Images don't have a runtime, Step 1 (Look) feels overly sparse. It's just a giant Aspect Ratio picker. 
- **Expectation:** I'd expect Step 1 and Step 2 to be combined for Images so I can select the ratio and type my prompt on the same screen, reducing the number of clicks.

### 4. Restoring Yesterday's Project
**Flow:** Welcome -> "Continue Working" -> Click Project
- **Friction (Confusing):** The "Continue Working" cards show the idea text, but if my idea was a 3-paragraph prompt, the card might truncate it in a weird way. 
- **Expectation:** I'd expect a visual thumbnail (even a placeholder or an auto-generated mood image) instead of just text, so I can visually recognize my projects instantly.

### 5. Exporting
**Flow:** (Simulated since Gate C doesn't cover export yet, but observing the Recent Activity)
- **Friction (Confusing):** "Recent Activity" shows "Package exported" but no context of *what* was exported or where it went. 
- **Expectation:** I'd expect a clear "Download" or "Open Folder" button right in the activity feed so I can grab the asset immediately.

---

## Pass 7 — Creator Psychology (Creator Experience Review)

*Focus: What would make a user excited to keep using this application? Forget architecture, forget SDKs.*

### 1. Emotional Reward is Missing
- **Observation:** The project creation flow ends in a static, functional wait ("Create -> Wait -> Project Created").
- **Friction:** Five seconds of waiting feels like dead time. 
- **Creator Expectation:** It should feel like a studio spinning up. Dynamic loading states ("🎬 Director's Chair Reserved", "Preparing Story Department...", "Connecting AI Departments...", "Welcome aboard") would turn a wait into an exciting buildup.

### 2. "Fill Forms" vs. "Start Creating"
- **Observation:** The wizard asks for Name, Idea, Runtime, Aspect Ratio, and Provider. It feels like filing paperwork.
- **Friction:** Too many decisions before the creative process begins. 
- **Creator Expectation:** It should feel magical. A single prompt: *"✨ Describe the movie in one sentence."* The system should infer the rest or ask later if absolutely necessary.

### 3. Technical Leakage in the UI
- **Observation:** Providers (Gemini, OpenRouter, MockProvider, DeepSeek) are surfaced to the user.
- **Friction:** 95% of creators do not know or care about backend LLM routing. Exposing it drops excitement and raises cognitive load.
- **Creator Expectation:** Replace providers with a simple "Generation Quality" choice (⚡ Fast, ⭐ Balanced, 💎 Highest Quality), moving the actual LLM selection into a hidden "Advanced" section.

### 4. Progress Visibility
- **Observation:** The "Continue Working" cards show a single percentage (e.g., 83%).
- **Friction:** A percentage is abstract. It doesn't tell the filmmaker what is actually done and what needs attention.
- **Creator Expectation:** A visual checklist of stages (Story ✔, Screenplay ✔, Audio ✔, Poster ○, Export ○) makes progress instantly meaningful and provides a clear next action.

### 5. Quick Start Expansion
- **Observation:** Currently planned Quick Start buttons are basic.
- **Friction:** Missing the opportunity to tap into what creators actually want to make right now.
- **Creator Expectation:** A robust "🔥 Trending" row with 1-click templates (30s Mythology Short, AI Podcast, Faceless YouTube Video, Cinematic Trailer, Instagram Reel) to get them creating within 20 seconds of opening the app.

## Conclusion
To succeed as a creative OS, NAC must reduce the number of upfront decisions, hide technical complexity (providers, backend disclaimers), and maximize emotional reward during loading states. Every unnecessary click must justify itself; fields should be inferred, generated, or postponed whenever possible.
