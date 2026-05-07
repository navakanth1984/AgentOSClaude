#!/usr/bin/env node
/**
 * generate-bookmarklet.js
 * Reads youtube-urls.json and produces:
 *   1. bookmarklet.js  — paste into browser console on NotebookLM to auto-add URLs
 *   2. urls.txt        — plain list of URLs as fallback
 */

const fs = require('fs');

const data = JSON.parse(fs.readFileSync('youtube-urls.json', 'utf8'));
const urls = data.videos.map(v => v.url);

console.log(`Loaded ${urls.length} URLs from youtube-urls.json\n`);

// --- Plain URL list ---
fs.writeFileSync('urls.txt', urls.join('\n'));
console.log(`urls.txt saved (${urls.length} lines)`);

// --- Browser console script ---
// This runs inside NotebookLM and adds URLs one by one via the UI
const consoleScript = `
(async () => {
  const urls = ${JSON.stringify(urls, null, 2)};

  const sleep = ms => new Promise(r => setTimeout(r, ms));

  const click = sel => {
    const el = document.querySelector(sel);
    if (el) { el.click(); return true; }
    return false;
  };

  const clickText = text => {
    const els = [...document.querySelectorAll('button, li, [role="menuitem"], [role="option"]')];
    const el = els.find(e => e.textContent.trim().toLowerCase().includes(text.toLowerCase()));
    if (el) { el.click(); return true; }
    return false;
  };

  const typeIn = async (sel, value) => {
    const input = document.querySelector(sel);
    if (!input) return false;
    input.focus();
    input.value = value;
    input.dispatchEvent(new Event('input', { bubbles: true }));
    input.dispatchEvent(new Event('change', { bubbles: true }));
    await sleep(300);
    return true;
  };

  console.log('Starting upload of', urls.length, 'URLs to NotebookLM...');

  for (let i = 0; i < urls.length; i++) {
    const url = urls[i];
    console.log(\`[\${i+1}/\${urls.length}] \${url}\`);

    // Click "Add source"
    clickText('add source');
    await sleep(1000);

    // Click "YouTube" or "Website" option
    if (!clickText('youtube')) clickText('website');
    await sleep(800);

    // Find URL input and fill it
    const inputSel = 'input[type="url"], input[placeholder*="URL" i], input[placeholder*="link" i], input[placeholder*="youtube" i]';
    const typed = await typeIn(inputSel, url);
    if (!typed) {
      console.warn('Could not find URL input — skipping', url);
      // Try to close any open dialog
      document.querySelector('button[aria-label*="close" i], button[aria-label*="cancel" i]')?.click();
      await sleep(500);
      continue;
    }

    await sleep(400);

    // Click Insert / Add / Confirm
    if (!clickText('insert')) if (!clickText('add')) clickText('confirm');
    await sleep(1500);

    if ((i + 1) % 10 === 0) {
      console.log(\`Uploaded \${i+1}/\${urls.length} — pausing 3s...\`);
      await sleep(3000);
    }
  }

  console.log('Done! All', urls.length, 'URLs submitted.');
})();
`.trim();

fs.writeFileSync('bookmarklet.js', consoleScript);
console.log('bookmarklet.js saved\n');

console.log('='.repeat(60));
console.log('HOW TO USE:');
console.log('='.repeat(60));
console.log('1. Open DuckDuckGo browser');
console.log('2. Go to https://notebooklm.google.com');
console.log('3. Create a new notebook called "Huberman Health"');
console.log('4. Open the browser DevTools console:');
console.log('   Press F12  →  click "Console" tab');
console.log('5. Copy the contents of bookmarklet.js');
console.log('6. Paste into the console and press Enter');
console.log('7. Watch it add URLs automatically\n');
console.log(`Total URLs to upload: ${urls.length}`);
