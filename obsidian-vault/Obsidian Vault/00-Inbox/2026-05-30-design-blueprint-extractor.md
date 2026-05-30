---
date: 2026-05-30
tags: [ai-workflows, web-design, firecrawl, gemini, prompt-engineering]
project: "AI Tools & Automation"
source: "Design Blueprint Extraction Workflow"
---

# Design Blueprint Extraction Workflow

## Key Idea
Extract the semantic structure, typographic ratios, and micro-spacing scale ("design DNA") of a premium website using scraping tools and LLM deconstruction. This allows you to recreate high-fidelity layouts for completely new businesses without direct plagiarism or direct copying of assets.

## Details
The process isolates layout structure from brand-specific elements using a three-file architectural blueprint:
1. **`builderbrief.mmd`**: A Mermaid.js flow diagram representing container hierarchies.
2. **`scaffold.html`**: A content-agnostic semantic HTML structure with generic placeholders.
3. **`design-tokens.css`**: Spacing grids, color systems, and typographic variables.

### Extraction Channels
* **Channel 1 (Firecrawl API)**: Scraping a reference URL into clean markdown/JSON.
* **Channel 2 (Direct Prompting)**: Sharing code or structural fragments directly with an LLM for component deconstruction.
* **Channel 3 (Bookmarklet Automation)**: Automating URL ingestion pipelines directly into AI hubs (such as NotebookLM or Google AI Studio).

### The Deconstruction Prompt
This prompt is used in Claude or Gemini to act as a custom Design Blueprint Extractor:

```markdown
You are a master Creative Web Architect and Senior Frontend Engineer specializing in Design System Deconstruction.
Your task is to analyze the provided scraped website markdown/HTML and extract its core layout architecture, spatial DNA, and visual structure without copying its specific branding, text content, or assets.

### Target Site Context
- Brand Name: [Specify target, e.g., rocket.net]
- Description: [Specify target service, e.g., Premium Managed WordPress Hosting]

Please generate the following three files based on your deconstruction:

---

### FILE 1: `builderbrief.mmd` (Mermaid Structural Brief)
Generate a clean Mermaid.js flow diagram illustrating the semantic hierarchy and layout architecture of the website's sections, columns, and interactive containers.
- Represent sections, grids, flex containers, and main UI blocks.
- Use clean, human-readable labels.
- Structure it from the top-level body wrapper down to critical leaf components.

### FILE 2: `scaffold.html` (Semantic Layout Structure)
Provide the full, working HTML skeleton representing the target's grid, flex containers, and structural sections.
- Use pristine semantic HTML5 elements (`<header>`, `<nav>`, `<main>`, `<section>`, `<footer>`).
- DO NOT include specific business copy or branded text. Instead, use general structural placeholders (e.g., `<h2>Section Title Placeholder</h2>`, `<p>Body copy placeholder explaining product features...</p>`).
- Use logical class names reflecting the layout (e.g., `class="hero-section"`, `class="feature-grid"`, `class="card-container"`).
- Keep all structural tags, layout grids, columns, and container wrappers exactly corresponding to the target's visual balance.

### FILE 3: `design-tokens.css` (Design & Spacing Variables)
Extract the micro-spacing scales, typographic hierarchies, and layout rules, outputting them as a clean stylesheet of CSS Custom Properties (`:root` variables) and core classes.
- **Typography Scale**: Define variables for font sizes, font weights, and line heights representing the visual hierarchy. Use fallback system font stacks that mimic the target's typography (e.g., Outfit, Inter, JetBrains Mono).
- **Color Harmony System**: Extract the functional color roles (Primary, Secondary, Backgrounds, Accent, Borders, Shadow Glows) and represent them using premium HSL color tokens.
- **Spacing Scale**: Map out the exact padding, margin, and gap scales (in `rem` or `px`) used to build the sections, headers, and container grids.
- **Visual Utility Classes**: Provide the base structural CSS styles required to lay out `scaffold.html` (e.g., `.grid-3-col`, `.flex-between`, `.glassmorphic-card`).

---

[PASTE YOUR SCRAPED WEBSITE DATA OR HTML CONTENT HERE]
```

### The Re-Synthesis Prompt
Use this in Google AI Studio / Gemini to rebuild a customized site from the extracted files:

```markdown
You are an expert Frontend Designer and Web Developer.
I have uploaded the design blueprint files (`builderbrief.mmd`, `scaffold.html`, and `design-tokens.css`) from a reference website to use as our layout architecture and design system.

### My New Business Context
- Business Name: [Your Business Name, e.g., Fabric Frontier]
- One-line Description: [e.g., An AI-assisted workspace orchestrator for modern creatives]
- Brand Color Palette Preference: [e.g., Deep Space Cyberpunk: obsidian dark backgrounds, vibrant neon cyan accents]

### Instructions
1. Analyze the uploaded `scaffold.html` and `design-tokens.css` to fully understand the grid architecture, spacing system, container hierarchies, and typography styles.
2. Build a completely custom, premium landing page for my new business.
3. Keep the exact spatial layout, grid dimensions, and container hierarchies defined in `scaffold.html`. 
4. Customize the colors, text copy, image assets, navigation links, and icons to fit my new business perfectly. Adjust the CSS variables in `design-tokens.css` to reflect my brand color choices while preserving the structural spacing tokens.
5. Provide a single, complete `index.html` file containing the semantic structural elements and the embedded modern styling in a `<style>` block (or linked stylesheet) along with any required vanilla JavaScript interactive animations (e.g., mouse-move parallax, smooth disclosure cards, or interactive menus).
```

## Action / Next Steps
- [ ] Install Firecrawl CLI (`npx -y firecrawl-cli@latest init --all --browser`) or sign up to get an API key.
- [ ] Run a test scrape on a high-fidelity landing page of choice and save the resulting markdown as a design reference.
- [ ] Deconstruct the reference using the **Deconstruction Prompt** in Claude.
- [ ] Upload the generated blueprint files into Google AI Studio and prompt Gemini to build a customized workspace landing page for `Fabric-Frontier`.
