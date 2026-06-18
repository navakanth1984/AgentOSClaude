"""
gcp_billing_scraper.py — Scrapes GCP Billing Credits directly from GCP Console.
Uses Playwright to inject Chrome session cookies and navigate the GCP Billing Console.
"""

import sys
import os
import re
import json
import asyncio
from pathlib import Path
from datetime import datetime

try:
    from playwright.async_api import async_playwright, BrowserContext
    PLAYWRIGHT_AVAILABLE = True
except ImportError:
    PLAYWRIGHT_AVAILABLE = False

try:
    import browser_cookie3
    COOKIE_LIB_AVAILABLE = True
except ImportError:
    COOKIE_LIB_AVAILABLE = False

USAGE_PATH = Path(__file__).parent.parent / "memory_os" / "gcp_credit_usage.json"
SCREENSHOT_PATH = Path(__file__).parent.parent / "memory_os" / "gcp_credits_screenshot.png"


def log(msg: str):
    """Write diagnostic messages to sys.stderr so stdout remains pure JSON."""
    print(msg, file=sys.stderr, flush=True)


def get_google_cookies() -> list[dict]:
    """Extract Google auth cookies from Chrome."""
    if not COOKIE_LIB_AVAILABLE:
        log("[GCP Scraper] browser-cookie3 not installed.")
        return []

    cookies = []
    try:
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
        log(f"[GCP Scraper] Extracted {len(cookies)} Google cookies from Chrome.")
    except Exception as e:
        log(f"[GCP Scraper] Cookie extraction failed: {e}")
        log("  Make sure Chrome is fully closed before running.")

    return cookies


async def scrape_gcp_credits():
    if not PLAYWRIGHT_AVAILABLE:
        return {"error": "Playwright is not installed."}

    if not USAGE_PATH.exists():
        return {"error": "gcp_credit_usage.json registry not found."}

    # Load config from registry
    try:
        registry = json.loads(USAGE_PATH.read_text(encoding="utf-8"))
    except Exception as e:
        return {"error": f"Failed to read registry: {e}"}

    project_id = registry["config"].get("project_id", "nthdim-academy-v2")
    billing_id = registry["config"].get("billing_account_id", "015936-156B27-56F23F")
    
    url = f"https://console.cloud.google.com/billing/{billing_id}/credits?project={project_id}"
    log(f"[GCP Scraper] Navigating to: {url}")

    async with async_playwright() as p:
        browser = await p.chromium.launch(
            headless=True,
            args=["--no-sandbox", "--disable-blink-features=AutomationControlled"]
        )
        context = await browser.new_context(
            viewport={"width": 1400, "height": 900},
            user_agent=(
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/125.0.0.0 Safari/537.36"
            )
        )

        cookies = get_google_cookies()
        if cookies:
            await context.add_cookies(cookies)

        page = await context.new_page()
        
        try:
            # Navigate and wait for network idle
            await page.goto(url, wait_until="networkidle", timeout=30000)
            log("[GCP Scraper] Page loaded. Waiting for billing components...")
            
            # Wait for content to render (GCP Console is dynamic)
            await page.wait_for_timeout(10000)
            
            # Save screenshot for verification
            await page.screenshot(path=str(SCREENSHOT_PATH))
            log(f"[GCP Scraper] Diagnostic screenshot saved: {SCREENSHOT_PATH.name}")

            # Extract full page text
            page_text = await page.evaluate("() => document.body.innerText")
            
            # ── Regex Parsing ──
            # Try to match GenAI App Builder values
            genai_match = re.search(
                r"GenAI\s+App\s+Builder.*?(?:₹|INR)\s*([\d,]+\.\d{2})\s*([\d,]+\.\d{2})",
                page_text, re.IGNORECASE | re.DOTALL
            )
            if not genai_match:
                # Fallback broad match
                genai_match = re.search(
                    r"GenAI App Builder.*?([\d,]+\.\d{2})",
                    page_text, re.IGNORECASE | re.DOTALL
                )

            # Try to match Dialogflow CX values
            df_match = re.search(
                r"Dialogflow\s+CX\s+Trial.*?(?:₹|INR)\s*([\d,]+\.\d{2})\s*([\d,]+\.\d{2})",
                page_text, re.IGNORECASE | re.DOTALL
            )
            if not df_match:
                df_match = re.search(
                    r"Dialogflow CX.*?([\d,]+\.\d{2})",
                    page_text, re.IGNORECASE | re.DOTALL
                )

            updated = False
            
            if genai_match:
                vals = genai_match.groups()
                if len(vals) >= 2:
                    rem = float(vals[0].replace(",", ""))
                    total = float(vals[1].replace(",", ""))
                    registry["genai_voucher"]["remaining"] = rem
                    registry["genai_voucher"]["total"] = total
                else:
                    rem = float(vals[0].replace(",", ""))
                    registry["genai_voucher"]["remaining"] = rem
                updated = True
                log(f"[GCP Scraper] Scraped GenAI App Builder: remaining = {rem}")
            else:
                log("[GCP Scraper] Warning: Could not locate GenAI App Builder text on page.")

            if df_match:
                vals = df_match.groups()
                if len(vals) >= 2:
                    rem = float(vals[0].replace(",", ""))
                    total = float(vals[1].replace(",", ""))
                    registry["dialogflow_trial"]["remaining"] = rem
                    registry["dialogflow_trial"]["total"] = total
                else:
                    rem = float(vals[0].replace(",", ""))
                    registry["dialogflow_trial"]["remaining"] = rem
                updated = True
                log(f"[GCP Scraper] Scraped Dialogflow CX Trial: remaining = {rem}")
            else:
                log("[GCP Scraper] Warning: Could not locate Dialogflow CX Trial text on page.")

            if updated:
                # Save back to JSON registry
                USAGE_PATH.write_text(json.dumps(registry, indent=2), encoding="utf-8")
                log("[GCP Scraper] Registry updated successfully.")
                await browser.close()
                return {"success": True, "registry": registry}
            else:
                await browser.close()
                # Return page text excerpt for debugging if both match failed
                excerpt = page_text[:1000]
                return {"success": False, "error": "No matching credit elements found on page.", "excerpt": excerpt}

        except Exception as err:
            await browser.close()
            return {"success": False, "error": f"Scrape loop failed: {err}"}


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--run":
        res = asyncio.run(scrape_gcp_credits())
        print(json.dumps(res, indent=2))
