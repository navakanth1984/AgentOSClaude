Extract a design "blueprint" from a reference website and apply it to a new design task, without hallucinating details that weren't actually observed.

## Input: $ARGUMENTS

Expected form: `<source-url> for <new-project-topic/description>`
(e.g. `https://antigravity.google for a landing page selling handmade phone cases`)

If `$ARGUMENTS` is missing the URL or the topic, stop and ask the user for whichever is missing — do not guess a URL and do not invent a topic.

---

## Step 0 — Preconditions

- This command produces a **visual design** (page/poster/deck/etc). Before writing any HTML, invoke the `create_visual_design_express_skill` skill (or the project's `frontend-design` skill if the target is a responsive app UI, not a fixed-canvas design) and follow its guidance for authoring + delivery choice. Don't skip this because a blueprint step is involved — extraction feeds the design skill, it doesn't replace it.
- If the user hasn't said where the output should land (Adobe Express doc, standalone HTML/PPTX/PDF, or both), ask before producing the final artifact — per that skill's own instructions.

## Step 1 — Fetch the reference site (ground truth, not memory)

1. Use `firecrawl-scrape` (preferred) or `WebFetch` to pull the actual rendered content of the URL. Do not describe the site from training-data familiarity — even "famous" sites may have redesigned since your knowledge cutoff.
2. If the fetch fails (blocked, JS-only shell with no content, 404, paywall):
   - Retry once with a different tool (e.g. WebFetch if firecrawl failed, or vice versa).
   - If still failing, tell the user explicitly: "I couldn't retrieve `<url>` (`<error>`). I can't extract a design from a site I haven't actually seen — please paste a screenshot, the HTML, or a different URL." Do not fabricate a blueprint from the name/reputation of the site alone.
3. If the page is a JS-rendered SPA and the scrape returns an empty shell, note this and ask the user for a screenshot instead of guessing.

## Step 2 — Extract the blueprint (observation only)

From the fetched content/screenshot, extract only what is directly observable. For each attribute, cite where it came from (a CSS value, a visible color swatch, a font-family declaration) — if you can't point to evidence, mark it "not determined" rather than inventing a plausible-sounding value.

Capture:
- **Typography**: font-family stack(s), weight contrasts (e.g. thin display + bold body), approximate size scale/ratio, letter-spacing/line-height patterns if visible in CSS.
- **Color**: exact hex/rgb values pulled from CSS or swatches — never approximate a brand color from memory ("Google blue" ≠ a specific hex unless you saw it).
- **Layout rules**: grid/columns, spacing scale, section rhythm, whitespace density.
- **Motion/interactivity**: only describe animations/transitions you can see in the CSS/JS (transition durations, easing, scroll-triggers) — don't assume "smooth animations" as a generic compliment if you didn't verify a transition property.
- **Distinctive signature elements**: the 1-3 things that make this site's identity recognizable (e.g. floating orbs, a specific grain texture, a signature hover state) — these are the highest-value, highest-hallucination-risk items, so hold them to the strictest evidence bar.

Write this to a short blueprint artifact (in-memory summary is fine for a single-shot task; write a scratch file only if the user will want to reuse it across sessions).

## Step 3 — Flag extraction vs. inspiration

State explicitly to the user which elements are being **reused as structural/stylistic patterns** (typography scale, spacing system, motion language) versus which would constitute **copying protected brand assets** (logos, exact copy, proprietary imagery) — and exclude the latter from the new design. The goal is leveling up the craft, not reproducing the source.

## Step 4 — Apply to the new project

1. Re-state the new project's topic/goal back to the user in one line to confirm you're building the right thing before generating output.
2. Generate the new design's HTML by transplanting the extracted *rules* (type scale, color system, spacing, motion language, signature-element pattern) onto content appropriate to the new topic — do not reuse the source site's actual copy or imagery.
3. Follow the visual-design skill's export path (Express import via `export_html_to_express`, or direct file derivation) per the user's chosen destination from Step 0. Always run `html_export_readiness_skill` immediately before every `export_html_to_express` call, including retries.

## Step 5 — Verify before declaring done

- Re-open/preview the generated output and check it against the blueprint: are the typography/color/motion rules actually present in the output, not just described in prose?
- If any extracted attribute was marked "not determined" in Step 2, tell the user what was skipped and why, rather than silently filling it with a plausible default.
- Summarize in 2-3 sentences: what was extracted, what was deliberately left out (branding/copy), and where the output landed.
