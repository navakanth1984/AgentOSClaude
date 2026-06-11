"""
notebooklm_agent.py — NotebookLM Browser Agent for Agent OS
Uses Playwright to automate NotebookLM (no official API exists).

HOW IT WORKS:
  1. Reads your real Google cookies directly from Chrome's SQLite database
  2. Injects them into a fresh Playwright browser — no login screen ever appears
  3. Google never sees an "automation login attempt" — we're already authenticated

WHY COOKIE INJECTION vs PROFILE COPY:
  Google blocks ALL Playwright-controlled browsers at login (even real Chrome)
  because it detects the WebDriver automation flag on the sign-in page.
  Cookie injection bypasses login entirely — we skip that page completely.

REQUIREMENTS:
  pip install playwright browser-cookie3
  python -m playwright install chromium
"""

import asyncio
import json
from pathlib import Path
from datetime import datetime

try:
    from playwright.async_api import async_playwright, BrowserContext, Page
    PLAYWRIGHT_AVAILABLE = True
except ImportError:
    PLAYWRIGHT_AVAILABLE = False

try:
    import browser_cookie3
    COOKIE_LIB_AVAILABLE = True
except ImportError:
    COOKIE_LIB_AVAILABLE = False

# ─── Config ───────────────────────────────────────────────────
NOTEBOOKLM_URL = "https://notebooklm.google.com"
ASSET_LIBRARY = Path(__file__).parent / "asset_library"
ASSET_LIBRARY.mkdir(exist_ok=True)

GOOGLE_DOMAINS = [".google.com", "notebooklm.google.com", "accounts.google.com"]
NOTEBOOK_CACHE = Path(__file__).parent / "notebook_cache.json"


# ─── Cookie Extraction ────────────────────────────────────────

def get_google_cookies() -> list[dict]:
    """
    Extract Google/NotebookLM cookies from your real Chrome installation.
    Uses browser_cookie3 which handles Windows DPAPI decryption automatically.
    Returns cookies in Playwright format: [{name, value, domain, path, ...}]
    """
    if not COOKIE_LIB_AVAILABLE:
        print("[NotebookLM] browser-cookie3 not installed.")
        print("  Run: python -m pip install browser-cookie3")
        return []

    # Make sure Chrome is closed — browser_cookie3 needs the DB unlocked
    cookies = []
    try:
        # Get cookies for Google domains from Chrome
        jar = browser_cookie3.chrome(domain_name=".google.com")
        for c in jar:
            cookies.append({
                "name":     c.name,
                "value":    c.value,
                "domain":   c.domain if c.domain.startswith(".") else f".{c.domain}",
                "path":     c.path or "/",
                "secure":   bool(c.secure),
                "httpOnly": False,
                "sameSite": "None",
            })
        print(f"[NotebookLM] Extracted {len(cookies)} Google cookies from Chrome.")
    except Exception as e:
        print(f"[NotebookLM] Cookie extraction failed: {e}")
        print("  Make sure Chrome is fully closed before running.")

    return cookies


# ─── Browser Context ─────────────────────────────────────────

async def get_browser_context(playwright, headless: bool = True) -> BrowserContext:
    """
    Launch a fresh Playwright Chromium browser and inject your real Google
    cookies. This bypasses the login page entirely — Google never sees an
    automation login attempt, so the 'Couldn't sign you in' block never fires.
    """
    # Launch fresh browser (no persistent profile needed)
    browser = await playwright.chromium.launch(
        headless=headless,
        args=["--no-sandbox", "--disable-blink-features=AutomationControlled"],
    )

    # Create context and inject cookies before loading any page
    context = await browser.new_context(
        viewport={"width": 1280, "height": 900},
        user_agent=(
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/125.0.0.0 Safari/537.36"
        ),
    )

    # Inject real Google cookies — this is what makes auth work
    cookies = get_google_cookies()
    if cookies:
        await context.add_cookies(cookies)
        print("[NotebookLM] Cookies injected. Navigating to NotebookLM...")
    else:
        print("[NotebookLM] No cookies — will need manual login.")

    return context


async def ensure_logged_in(page: Page) -> bool:
    """
    Navigate to NotebookLM and check if we're logged in.
    If not, wait for the user to log in manually (up to 120 seconds).
    """
    await page.goto(NOTEBOOKLM_URL, wait_until="domcontentloaded", timeout=60_000)
    await asyncio.sleep(3)

    # Check for login state by looking for the notebook list or the sign-in button
    url = page.url
    if "accounts.google.com" in url or "signin" in url.lower():
        print("[NotebookLM] Not logged in. Please log in in the browser window...")
        print("[NotebookLM] Waiting up to 120 seconds for login...")
        try:
            await page.wait_for_url(f"{NOTEBOOKLM_URL}/**", timeout=120_000)
            print("[NotebookLM] Login detected. Session saved.")
            return True
        except Exception:
            print("[NotebookLM] Login timeout. Please try again.")
            return False

    print("[NotebookLM] Already logged in.")
    return True


# ─── Notebook Operations ──────────────────────────────────────

async def list_notebooks(page: Page) -> dict:
    """
    Scrape the NotebookLM home page and separate notebooks by owner:
      - "mine"     → your own notebooks (default view)
      - "featured" → NotebookLM featured/example notebooks

    Strategy: run a single evaluate() call to walk the DOM in-browser.
    This is faster than Playwright's element handles and lets us inspect
    the full ancestor chain to detect which section each card is in.

    Returns: {"mine": [...], "featured": [...]}
    Each item: {"title": str, "url": str, "type": "mine"|"featured"}
    """
    await page.goto(NOTEBOOKLM_URL, wait_until="domcontentloaded", timeout=60_000)
    await asyncio.sleep(4)

    result = await page.evaluate("""() => {
        const mine = [];
        const featured = [];
        const seen = new Set();

        // Keywords that identify a "Featured" section heading
        const featuredKeywords = ['featured', 'explore', 'example', 'template', 'discover', 'try'];

        // Helper: walk up DOM ancestors to find the section heading text
        function getSectionLabel(el) {
            let node = el;
            for (let i = 0; i < 12; i++) {
                node = node.parentElement;
                if (!node) break;
                // Look for a heading (h1-h4) or element with heading-like class near this node
                const headings = node.querySelectorAll('h1, h2, h3, h4, [class*="section"], [class*="heading"], [class*="category"]');
                for (const h of headings) {
                    const text = h.innerText.trim().toLowerCase();
                    if (text) return text;
                }
            }
            return '';
        }

        // Helper: extract the title from a card link element
        function getTitle(link) {
            // Try heading inside the link
            for (const sel of ['h3', 'h2', 'h4', '[class*="title"]', '[class*="name"]', '[class*="label"]']) {
                const el = link.querySelector(sel);
                if (el) {
                    const t = el.innerText.trim();
                    if (t && t.toLowerCase() !== 'untitled') return t;
                }
            }
            // Try the link's own text
            const t = link.innerText.trim();
            if (t && t.length < 200) return t;
            return 'Untitled';
        }

        const links = document.querySelectorAll('a[href*="/notebook/"]');
        for (const link of links) {
            const href = link.getAttribute('href') || '';
            if (!href.includes('/notebook/')) continue;
            if (seen.has(href)) continue;
            seen.add(href);

            const title = getTitle(link);
            const sectionLabel = getSectionLabel(link);
            const isFeatured = featuredKeywords.some(kw => sectionLabel.includes(kw));

            const notebook = { title, url: href, type: isFeatured ? 'featured' : 'mine' };
            if (isFeatured) {
                featured.push(notebook);
            } else {
                mine.push(notebook);
            }
        }

        return { mine, featured };
    }""")

    my_notebooks = result.get("mine", [])
    featured_notebooks = result.get("featured", [])

    print(f"[NotebookLM] My notebooks: {len(my_notebooks)} | Featured: {len(featured_notebooks)}")

    # If titles are all "Untitled", save DOM for debugging
    titled = [n for n in my_notebooks if n["title"] != "Untitled"]
    if not titled and my_notebooks:
        print("[NotebookLM] All titles are 'Untitled' — saving DOM snapshot...")
        snapshot_path = ASSET_LIBRARY / "notebooklm_dom.html"
        html = await page.content()
        snapshot_path.write_text(html, encoding="utf-8")
        print(f"[NotebookLM] DOM saved: {snapshot_path}")

    return {"mine": my_notebooks, "featured": featured_notebooks}


async def open_notebook(page: Page, notebook_url: str) -> bool:
    """Navigate to a specific notebook."""
    full_url = notebook_url if notebook_url.startswith("http") else f"{NOTEBOOKLM_URL}{notebook_url}"
    # Use domcontentloaded — NotebookLM's Angular app never reaches "networkidle"
    # because it makes continuous background requests.
    await page.goto(full_url, wait_until="domcontentloaded", timeout=60_000)
    await asyncio.sleep(5)  # let Angular render components
    print(f"[NotebookLM] Opened: {full_url}")
    return True


async def get_studio_content(page: Page) -> list[dict]:
    """
    Navigate to the Studio tab and scrape all generated content
    (audio overviews, study guides, etc.)
    Returns list of {type, title, url} dicts.
    """
    assets = []
    try:
        # Wait for page to be interactive, then dump current URL for debug
        await asyncio.sleep(2)
        print(f"[NotebookLM] Current URL: {page.url}")

        # NotebookLM notebook page layout:
        # Left: sources panel | Center: chat | Right: Studio panel
        # Studio content is usually already visible in the right panel — no tab click needed.
        # Try multiple selector patterns to find studio output cards.

        await asyncio.sleep(1)

        # Find the Studio panel — the outermost [class*='studio'] element contains all outputs.
        # The last one (most deeply nested) has the actual output list text.
        studio_els = await page.query_selector_all("[class*='studio']")
        print(f"[NotebookLM] Found {len(studio_els)} studio elements")

        # Known Studio output types NotebookLM offers
        OUTPUT_TYPES = [
            "Audio Overview",
            "Slide deck",
            "Video Overview",
            "FAQ",
            "Study guide",
            "Briefing doc",
            "Timeline",
        ]

        # Scan all studio elements for known output type names
        found_types = set()
        for el in studio_els:
            text = (await el.inner_text()).strip()
            for ot in OUTPUT_TYPES:
                if ot.lower() in text.lower() and ot not in found_types:
                    found_types.add(ot)
                    # Try to determine if it's already generated or just available
                    status = "available"  # default; generated ones would have audio player etc.
                    assets.append({
                        "type": ot,
                        "status": status,
                        "note": "Run generate command to create if not yet generated",
                    })

        # Save screenshot for reference
        screenshot_path = ASSET_LIBRARY / "notebook_studio_screenshot.png"
        await page.screenshot(path=str(screenshot_path))
        print(f"[NotebookLM] Screenshot saved: {screenshot_path}")

    except Exception as e:
        print(f"[NotebookLM] Studio scrape error: {e}")

    print(f"[NotebookLM] Found {len(assets)} studio assets")
    return assets


async def generate_and_download_audio(page: Page, context) -> dict:
    """
    Full Step 3 pipeline — two strategies depending on notebook state:

    STRATEGY A — Audio already exists (Play button present):
      Click Play → audio fetched from GCS immediately → intercept bytes → save

    STRATEGY B — Audio needs generation (Generate button only):
      Click Generate Audio Overview → wait for server-side generation →
      intercept the audio network response when it arrives

    WHY Play-first:
      If audio already exists, clicking Play fetches it from Google Cloud Storage
      within ~1 second. Clicking Generate instead queues server-side re-creation
      which can take 2-6+ minutes and uses a polling flow that's harder to intercept.

    WHY network interception (not DOM scraping):
      NotebookLM serves audio via signed HTTPS URLs that change every request.
      page.on("response") fires for every network response in parallel with the page.
      We catch audio/* bytes directly — UI structure is irrelevant.
    """
    result = {"triggered": False, "downloaded": False, "path": None, "error": None}

    try:
        # ── 0. Set up network interception FIRST (before any clicks) ──
        # This ensures we don't miss any audio response that fires immediately after click.
        ts = datetime.now().strftime("%Y%m%d_%H%M%S")
        save_path = ASSET_LIBRARY / f"{ts}_audio_overview"
        audio_captured = asyncio.Event()
        audio_url_found = [None]
        all_audio_urls = []  # log every audio URL seen for debugging

        async def capture_audio_response(response):
            """
            Fires for every HTTP response the browser receives.
            Saves the first audio response larger than 10 KB.
            NotebookLM audio comes from storage.googleapis.com with
            content-type: audio/mpeg or audio/wav.
            HLS chunks (.m4s, .ts) are smaller — we skip those and wait
            for the full file (the player fetches it in one or few requests).
            """
            content_type = response.headers.get("content-type", "")
            url = response.url

            is_audio = (
                "audio/" in content_type
                or "video/mp4" in content_type           # sometimes wrapped in mp4 container
                or url.endswith((".wav", ".mp3", ".m4a", ".ogg", ".opus", ".aac"))
                or ("storage.googleapis.com" in url and
                    any(ext in url for ext in [".wav", ".mp3", ".m4a", ".ogg", ".opus", ".aac"]))
            )

            if is_audio:
                all_audio_urls.append(url[:100])
                if not audio_captured.is_set():
                    print(f"[NotebookLM] Audio response: {url[:80]}... (type={content_type})")
                    try:
                        body = await response.body()
                        print(f"[NotebookLM] Audio body size: {len(body)} bytes")
                        if len(body) > 50_000:  # >50 KB = real audio file (not stub/manifest)
                            # Determine extension from content-type or URL
                            if "mpeg" in content_type or url.endswith(".mp3"):
                                ext = ".mp3"
                            elif "ogg" in content_type or url.endswith(".ogg"):
                                ext = ".ogg"
                            elif "mp4" in content_type or url.endswith(".m4a"):
                                ext = ".m4a"
                            else:
                                ext = ".wav"
                            final_path = save_path.with_suffix(ext)
                            final_path.write_bytes(body)
                            result["downloaded"] = True
                            result["path"] = str(final_path)
                            audio_url_found[0] = url
                            audio_captured.set()
                            print(f"[NotebookLM] ✓ Audio saved: {final_path.name} ({len(body)//1024} KB)")
                        else:
                            print(f"[NotebookLM] Skipping small response ({len(body)} bytes) — likely HLS chunk or manifest")
                    except Exception as e:
                        print(f"[NotebookLM] Could not read audio response body: {e}")

        page.on("response", lambda r: asyncio.ensure_future(capture_audio_response(r)))

        # ── 1. Check all button states ──
        all_btns = await page.query_selector_all("button[aria-label]")
        all_labels = [await b.get_attribute("aria-label") for b in all_btns]
        print(f"[NotebookLM] Visible buttons: {[l for l in all_labels if l]}")

        # ── STRATEGY A: Play existing audio ──
        # Look for the "Play" button that belongs to the Audio Overview card.
        # In the Studio panel, the first Play button after "Customise Audio Overview" is the one.
        # We find it by locating "Customise Audio Overview" button and then the sibling Play button.
        play_btn = None

        # Try: find Play button near the Customise Audio Overview button
        customise_btn = await page.query_selector('button[aria-label="Customise Audio Overview"], button[aria-label="Customize Audio Overview"]')
        if customise_btn:
            print("[NotebookLM] Audio overview exists. Looking for Play button...")
            # The Play button is a sibling in the same card container
            # Walk up to the card parent then find the Play button inside it
            play_btn = await page.evaluate("""(customiseBtn) => {
                // Walk up to find the card container (up to 8 levels)
                let el = customiseBtn;
                for (let i = 0; i < 8; i++) {
                    el = el.parentElement;
                    if (!el) break;
                    const play = el.querySelector('button[aria-label="Play"]');
                    if (play) return play;
                }
                return null;
            }""", customise_btn)

            # Fallback: any Play button on the page (first one = Audio Overview player)
            if not play_btn:
                play_btn = await page.query_selector('button[aria-label="Play"]')

        if play_btn:
            result["triggered"] = True
            print("[NotebookLM] Clicking Play to stream existing audio overview...")
            if hasattr(play_btn, 'click'):
                await play_btn.click()
            else:
                # play_btn came from evaluate() as an ElementHandle-like object — re-query
                play_btn = await page.query_selector('button[aria-label="Play"]')
                if play_btn:
                    await play_btn.click()

            print("[NotebookLM] Play clicked. Audio should stream within 10-30 seconds...")
            try:
                await asyncio.wait_for(audio_captured.wait(), timeout=60)  # 60 sec max for existing audio
                print("[NotebookLM] ✓ Audio captured via Play.")
            except asyncio.TimeoutError:
                print("[NotebookLM] Play didn't deliver audio in 60s. Trying Generate flow...")
                # Fall through to Strategy B

        # ── STRATEGY B: Generate fresh audio ──
        if not audio_captured.is_set():
            gen_card_btn = None
            for aria_label, state in [
                ("Generate Audio Overview", "generate"),
                ("Customise Audio Overview", "customise"),
                ("Customize Audio Overview", "customise"),
            ]:
                gen_card_btn = await page.query_selector(f'button[aria-label="{aria_label}"]')
                if gen_card_btn:
                    print(f"[NotebookLM] Using Generate flow via '{aria_label}'...")
                    break

            if gen_card_btn:
                await gen_card_btn.click()
                await asyncio.sleep(3)
                result["triggered"] = True

                # Click Generate inside the dialog that opens
                for sel in ["button:has-text('Generate')", "[role='dialog'] button", "mat-dialog-container button"]:
                    gen_btn = await page.query_selector(sel)
                    if gen_btn:
                        label_text = (await gen_btn.inner_text()).strip()
                        if label_text:
                            print(f"[NotebookLM] Clicking '{label_text}' in dialog...")
                            await gen_btn.click()
                            break

                MAX_WAIT = 720  # 12 minutes
                print(f"[NotebookLM] Waiting up to {MAX_WAIT//60} min for generation + audio delivery...")
                try:
                    # Poll with progress ticks so you can see it's still alive
                    tick = 0
                    while not audio_captured.is_set():
                        try:
                            await asyncio.wait_for(audio_captured.wait(), timeout=30)
                            break  # captured!
                        except asyncio.TimeoutError:
                            tick += 30
                            if tick >= MAX_WAIT:
                                raise asyncio.TimeoutError
                            mins, secs = divmod(tick, 60)
                            print(f"[NotebookLM] Still generating... {mins}m{secs:02d}s elapsed "
                                  f"(max {MAX_WAIT//60}m) | audio URLs seen: {len(all_audio_urls)}")
                    print("[NotebookLM] ✓ Audio captured after generation.")
                except asyncio.TimeoutError:
                    await page.screenshot(path=str(ASSET_LIBRARY / "generation_timeout.png"))
                    print(f"[NotebookLM] {MAX_WAIT//60} min timeout. Audio URLs seen: {all_audio_urls}")
                    print(f"[NotebookLM] Screenshot: generation_timeout.png")
                    result["error"] = f"Audio not detected in {MAX_WAIT//60} minutes. Check generation_timeout.png"
                    return result
            else:
                result["error"] = "No audio overview button found at all."
                await page.screenshot(path=str(ASSET_LIBRARY / "generate_debug.png"))
                print(f"[NotebookLM] {result['error']} All labels: {all_labels}")
                return result

        # ── Auto-save note to Obsidian ──
        if result["downloaded"]:
            try:
                from obsidian_bridge import save_note
                save_note(
                    title=f"Audio Overview — {Path(result['path']).name}",
                    key_idea="NotebookLM audio overview auto-captured via network interception.",
                    details=(
                        f"File: `{result['path']}`\n"
                        f"Notebook: {page.url}\n"
                        f"Source URL: {audio_url_found[0]}"
                    ),
                    next_steps=[
                        "hermes load " + Path(result['path']).name,
                        "Load into Hermes for avatar video generation",
                    ],
                    tags=["notebooklm", "audio", "asset", "agent-os"],
                    folder="ai",
                )
                print("[NotebookLM] Asset noted in Obsidian.")
            except Exception:
                pass

    except Exception as e:
        result["error"] = str(e)
        print(f"[NotebookLM] Generate+download error: {e}")

    return result


async def take_notebook_screenshot(page: Page, name: str = "notebook") -> Path:
    """Save a screenshot of the current notebook to the asset library."""
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    path = ASSET_LIBRARY / f"{ts}_{name}.png"
    await page.screenshot(path=str(path), full_page=False)
    print(f"[NotebookLM] Screenshot saved: {path}")
    return path


# ─── High-Level Commands ──────────────────────────────────────

async def run_session(command: str = "list", notebook_url: str = "", headless: bool = True) -> dict:
    """
    Main entry point. Commands:
      "list"       — list all notebooks
      "studio"     — open notebook and get studio content
      "generate"   — trigger audio overview generation
      "screenshot" — take a screenshot of the current notebook
    """
    if not PLAYWRIGHT_AVAILABLE:
        return {"error": "Playwright not installed. Run: pip install playwright && python -m playwright install chromium"}

    result = {}
    async with async_playwright() as p:
        context = await get_browser_context(p, headless=headless)
        page = await context.new_page()   # cookie context uses new_page(), not pages[0]

        logged_in = await ensure_logged_in(page)
        if not logged_in:
            await context.browser.close()
            return {"error": "Login failed — make sure Chrome is closed and browser-cookie3 is installed"}

        if command == "list":
            data = await list_notebooks(page)  # {"mine": [...], "featured": [...]}
            result["notebooks"] = data["mine"]
            result["featured"] = data["featured"]
            # Write cache so server.py /notebooks endpoint can serve it instantly
            cache = {
                "notebooks": data["mine"],       # default: user's own
                "featured": data["featured"],
                "total": len(data["mine"]),
                "featured_total": len(data["featured"]),
                "cached_at": datetime.now().isoformat(),
            }
            NOTEBOOK_CACHE.write_text(json.dumps(cache, indent=2, ensure_ascii=False), encoding="utf-8")
            print(f"[NotebookLM] Cache written: {NOTEBOOK_CACHE} (mine={len(data['mine'])}, featured={len(data['featured'])})")

        elif command == "studio" and notebook_url:
            await open_notebook(page, notebook_url)
            result["assets"] = await get_studio_content(page)

        elif command == "generate" and notebook_url:
            await open_notebook(page, notebook_url)
            result.update(await generate_and_download_audio(page, context))

        elif command == "screenshot":
            if notebook_url:
                await open_notebook(page, notebook_url)
            path = await take_notebook_screenshot(page)
            result["screenshot"] = str(path)

        await context.browser.close()

    return result


# ─── CLI Entry Point ──────────────────────────────────────────

if __name__ == "__main__":
    import sys
    cmd = sys.argv[1] if len(sys.argv) > 1 else "list"
    url = sys.argv[2] if len(sys.argv) > 2 else ""
    headless = "--headful" not in sys.argv

    print(f"[NotebookLM Agent] Running command: {cmd} (headless={headless})")
    result = asyncio.run(run_session(cmd, url, headless=headless))
    print(json.dumps(result, indent=2))
