# DAAVA: Chapter Two Design System

## Style Prompt
**Industrial Noir / Cyber-Brutalist**: A world of heavy concrete, toxic smog, and jittery neon. High-contrast chiaroscuro lighting. 14mm ultra-wide perspectives. The vibe is cavernous yet suffocating, reflecting the political and environmental weight of the climb.

## Colors
- **Industrial Orange**: `#E67E22` (Arjun's Jumpsuit - Safety/Urgency)
- **Midnight Blue**: `#2C3E50` (Arjun's Harness - Tactical/Solid)
- **Status Cyan**: `#00FFFF` (Glowing Markers/Neon - Tech/Insight)
- **Golden Rim**: `#F39C12` (Sunlight/Hope - High-contrast rim light)
- **Concrete Gray**: `#7F8C8D` (Environment - Neutral/Bleak)

## Typography
- **Primary**: "Inter" (Clean, industrial, modern)
- **Display**: "Outfit" (Sharp, geometric, high-impact)

## Motion Rules
- **Pacing**: Deliberate, tense holds followed by jittery neon-flicker transitions.
- **Entrances**: Hard `gsap.from()` with `power4.out` easing. No soft fades.
- **Hierarchy**: Text overlays should feel like HUD data, pinned to concrete textures.

## What NOT to Do
- No generic gradients.
- No rounded corners (keep it brutalist/sharp).
- No soft lighting (everything is hard shadows or piercing beams).
