"""Site Builder — generate a self-contained HTML site from a prompt.

Routes through the shared ``call_openrouter`` helper so every generation stays
inside Agent OS model-economics governance (single routing point + free-model
fallback), consistent with swarm / goal / creative subsystems. Optionally pulls
brand signals (dominant colors + fonts) from a URL via the Firecrawl CLI before
generating, so the page can be styled to match an existing brand.
"""
from __future__ import annotations

import re
import subprocess
from collections import Counter
from pathlib import Path
from typing import Optional

from openrouter_client import call_openrouter

SITES_DIR = Path(__file__).parent / "asset_library" / "sites"
DEFAULT_MODEL = "anthropic/claude-opus-4"

SYSTEM_PROMPT = (
    "You are an expert front-end designer. Produce ONE complete, self-contained "
    "HTML5 document: inline <style> only, no external assets, no JS frameworks, "
    "responsive, accessible. Return ONLY the HTML, starting with <!DOCTYPE html>. "
    "No markdown code fences, no commentary before or after."
)


def _extract_html(text: str) -> str:
    """Strip markdown fences / stray prose; keep the document from <!doctype>/<html>."""
    text = text.strip()
    if text.startswith("```"):
        text = re.sub(r"^```[a-zA-Z]*\n", "", text)
        text = re.sub(r"\n```\s*$", "", text)
    m = re.search(r"(?is)<!doctype html.*?</html>", text)
    if m:
        return m.group(0)
    m = re.search(r"(?is)<html.*?</html>", text)
    return m.group(0) if m else text


def _scrape_brand(url: str) -> str:
    """Best-effort brand hint from a URL via Firecrawl. Never raises — returns '' on failure."""
    try:
        out = subprocess.run(
            ["firecrawl", "scrape", url, "--format", "rawHtml"],
            capture_output=True,
            text=True,
            timeout=90,
        )
        html = out.stdout or ""
        colors = re.findall(r"#[0-9a-fA-F]{6}", html)
        top = [c for c, _ in Counter(c.lower() for c in colors).most_common(6)]
        fonts = list(dict.fromkeys(re.findall(r"font-family:\s*([^;\"}<]+)", html)))[:4]
        if not top and not fonts:
            return ""
        parts = []
        if top:
            parts.append(f"Dominant colors: {', '.join(top)}.")
        if fonts:
            parts.append(f"Fonts: {', '.join(f.strip() for f in fonts)}.")
        return "Match this brand identity. " + " ".join(parts)
    except Exception:
        return ""


def build_site(
    prompt: str,
    brand_url: Optional[str] = None,
    model: Optional[str] = None,
    site_id: str = "site",
) -> dict:
    """Generate a self-contained HTML site and write it under asset_library/sites/<site_id>/.

    Returns a manifest dict with the on-disk path, the dashboard-served web path,
    the model used, whether a brand hint was applied, and the byte size.
    """
    brand_hint = _scrape_brand(brand_url) if brand_url else ""
    user = prompt if not brand_hint else f"{prompt}\n\n{brand_hint}"

    raw = call_openrouter(
        model=model or DEFAULT_MODEL,
        system=SYSTEM_PROMPT,
        user=user,
        max_tokens=8000,
        temperature=0.5,
    )
    html = _extract_html(raw)

    out_dir = SITES_DIR / site_id
    out_dir.mkdir(parents=True, exist_ok=True)
    html_path = out_dir / "index.html"
    html_path.write_text(html, encoding="utf-8")

    return {
        "html_path": str(html_path),
        "web_path": f"/asset_library/sites/{site_id}/index.html",
        "model": model or DEFAULT_MODEL,
        "brand_used": bool(brand_hint),
        "bytes": len(html),
    }


def export_pdf(site_id: str) -> dict:
    """Render an already-generated site's index.html to a print-fidelity PDF.

    Uses headless Chromium (Playwright) so CSS renders exactly as in a browser —
    python-pptx/wkhtmltopdf can't match that. Returns a manifest with the served
    web path to the PDF. Raises FileNotFoundError if the site hasn't been built.
    """
    from playwright.sync_api import sync_playwright

    out_dir = SITES_DIR / site_id
    html_path = out_dir / "index.html"
    if not html_path.exists():
        raise FileNotFoundError(f"No generated site for id '{site_id}' — build it first.")

    pdf_path = out_dir / "site.pdf"
    with sync_playwright() as p:
        browser = p.chromium.launch()
        try:
            page = browser.new_page()
            # 'load' (not 'networkidle') — the page is fully self-contained, so waiting
            # for network idle adds nothing and can hang headless Chromium on Windows.
            page.goto(html_path.as_uri(), wait_until="load", timeout=20000)
            page.pdf(
                path=str(pdf_path),
                format="A4",
                print_background=True,
                margin={"top": "0", "bottom": "0", "left": "0", "right": "0"},
            )
        finally:
            browser.close()

    return {
        "pdf_path": str(pdf_path),
        "web_path": f"/asset_library/sites/{site_id}/site.pdf",
        "bytes": pdf_path.stat().st_size,
    }
