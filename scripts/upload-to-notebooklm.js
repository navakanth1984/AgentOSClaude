#!/usr/bin/env node
/**
 * upload-to-notebooklm.js
 * Automates NotebookLM using your existing Chrome profile (already logged into Google).
 * No separate login needed.
 *
 * Usage:
 *   node scripts/upload-to-notebooklm.js --list
 *   node scripts/upload-to-notebooklm.js --name "Huberman Health" --urls-file youtube-urls.json
 *   node scripts/upload-to-notebooklm.js --name "My Notebook" --url "https://youtube.com/watch?v=..."
 */

const { chromium } = require('playwright');
const fs = require('fs');
const path = require('path');

const args = Object.fromEntries(
  process.argv.slice(2).reduce((acc, val, i, arr) => {
    if (val.startsWith('--')) acc.push([val.slice(2), arr[i + 1]]);
    return acc;
  }, [])
);

const NOTEBOOK_NAME = args.name || `Notebook ${new Date().toLocaleDateString()}`;
const URLS_FILE = args['urls-file'];
const SINGLE_URL = args.url;
const BATCH_SIZE = parseInt(args['batch-size'] || '5');

// Chrome profile — already logged into Google
const CHROME_USER_DATA = 'C:\\Users\\navka\\AppData\\Local\\Google\\Chrome\\User Data';
const CHROME_EXE = 'C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe';
const CHROME_EXE_86 = 'C:\\Program Files (x86)\\Google\\Chrome\\Application\\chrome.exe';

async function loadUrls() {
  if (SINGLE_URL) return [SINGLE_URL];
  if (URLS_FILE) {
    const data = JSON.parse(fs.readFileSync(URLS_FILE, 'utf8'));
    return data.videos.map(v => v.url);
  }
  console.error('ERROR: Provide --urls-file or --url');
  process.exit(1);
}

async function launchBrowser() {
  const tempProfile = path.join(process.env.TEMP || 'C:\\Temp', 'notebooklm-chrome-profile');
  const defaultDst  = path.join(tempProfile, 'Default', 'Network');
  fs.mkdirSync(defaultDst, { recursive: true });

  // Copy Chrome cookies (close Chrome first if it's running)
  const cookieSrc = path.join(CHROME_USER_DATA, 'Default', 'Network', 'Cookies');
  try {
    fs.copyFileSync(cookieSrc, path.join(defaultDst, 'Cookies'));
    console.log('Copied Google login cookies from Chrome.');
  } catch (e) {
    console.warn('Chrome cookies locked — close Chrome and try again, or log in manually.\n');
  }

  // Use real Chrome executable
  const executablePath =
    fs.existsSync(CHROME_EXE)    ? CHROME_EXE    :
    fs.existsSync(CHROME_EXE_86) ? CHROME_EXE_86 :
    undefined;

  console.log(`Browser: ${executablePath ? 'Google Chrome' : 'Playwright Chromium'}\n`);

  const browser = await chromium.launchPersistentContext(tempProfile, {
    headless: false,
    executablePath,
    args: [
      '--no-first-run',
      '--no-default-browser-check',
      '--disable-extensions',
      '--disable-blink-features=AutomationControlled', // avoids Google security block
    ],
    ignoreDefaultArgs: ['--enable-automation'],        // hides automation flag
    viewport: { width: 1280, height: 900 }
  });

  return browser;
}

async function goToNotebookLM(context) {
  const page = await context.newPage();
  await page.goto('https://notebooklm.google.com', { waitUntil: 'domcontentloaded', timeout: 30000 });
  await page.waitForTimeout(3000);

  const url = page.url();
  if (url.includes('accounts.google.com')) {
    console.log('\nStill redirected to login page.');
    console.log('Please sign in manually in the browser window that opened.');
    console.log('Waiting up to 2 minutes for you to log in...\n');
    await page.waitForURL('**/notebooklm.google.com**', { timeout: 120000 });
    console.log('Logged in successfully.\n');
  } else {
    console.log('Already logged in to NotebookLM.');
  }

  return page;
}

async function listNotebooks(page) {
  await page.waitForTimeout(2000);
  const items = await page.locator('[data-testid*="notebook"], .notebook-item, article, [class*="NotebookCard"]').all();
  console.log(`\nFound ${items.length} notebooks:\n`);
  for (let i = 0; i < items.length; i++) {
    const title = await items[i].textContent().catch(() => `Notebook ${i + 1}`);
    console.log(`  ${i + 1}. ${title.trim().slice(0, 80)}`);
  }
  if (items.length === 0) {
    console.log('  (No notebooks found — you may need to scroll or the page structure changed)');
    console.log('  Check the browser window to confirm you are logged in.');
  }
}

async function createNotebook(page, name) {
  console.log(`\nCreating notebook: "${name}"`);

  // Look for "New notebook" or "+" button
  const newBtn = page.locator('button:has-text("New notebook"), [aria-label="New notebook"], button:has-text("Create"), [aria-label*="new"]').first();
  await newBtn.waitFor({ timeout: 15000 });
  await newBtn.click();
  await page.waitForTimeout(2000);

  // Fill in notebook title if a dialog appears
  const titleInput = page.locator('input[placeholder*="title" i], input[placeholder*="name" i], input[aria-label*="title" i]').first();
  if (await titleInput.isVisible({ timeout: 3000 })) {
    await titleInput.clear();
    await titleInput.fill(name);
    const confirmBtn = page.locator('button:has-text("Create"), button:has-text("Done"), button:has-text("OK")').first();
    if (await confirmBtn.isVisible({ timeout: 2000 })) {
      await confirmBtn.click();
    } else {
      await page.keyboard.press('Enter');
    }
    await page.waitForTimeout(1500);
  }

  console.log('Notebook created.');
}

async function addUrlSource(page, url) {
  // Click "Add source"
  const addBtn = page.locator('button:has-text("Add source"), [aria-label*="Add source"], button:has-text("+ Add")').first();
  await addBtn.waitFor({ timeout: 10000 });
  await addBtn.click();
  await page.waitForTimeout(1000);

  // Click "YouTube" or "Website" option from the menu
  const youtubeOpt = page.locator('button:has-text("YouTube"), li:has-text("YouTube"), [aria-label*="YouTube"]').first();
  const websiteOpt = page.locator('button:has-text("Website"), li:has-text("Website"), button:has-text("URL")').first();

  if (await youtubeOpt.isVisible({ timeout: 2000 })) {
    await youtubeOpt.click();
  } else if (await websiteOpt.isVisible({ timeout: 2000 })) {
    await websiteOpt.click();
  }
  await page.waitForTimeout(800);

  // Type the URL
  const urlInput = page.locator('input[type="url"], input[placeholder*="url" i], input[placeholder*="link" i], input[placeholder*="YouTube" i]').first();
  await urlInput.waitFor({ timeout: 5000 });
  await urlInput.fill(url);
  await page.waitForTimeout(300);

  // Confirm / Insert
  const insertBtn = page.locator('button:has-text("Insert"), button:has-text("Add"), button:has-text("Confirm")').first();
  if (await insertBtn.isVisible({ timeout: 2000 })) {
    await insertBtn.click();
  } else {
    await page.keyboard.press('Enter');
  }
  await page.waitForTimeout(1200);
}

async function main() {
  const context = await launchBrowser();
  const page = await goToNotebookLM(context);

  if ('list' in args) {
    await listNotebooks(page);
    await context.close();
    return;
  }

  const urls = await loadUrls();
  console.log(`\nUploading ${urls.length} URLs to notebook: "${NOTEBOOK_NAME}"`);
  console.log('Watch the browser window to track progress.\n');

  await createNotebook(page, NOTEBOOK_NAME);

  let uploaded = 0;
  for (const url of urls) {
    try {
      await addUrlSource(page, url);
      uploaded++;
      process.stdout.write(`\r  Uploaded: ${uploaded}/${urls.length}`);
    } catch (err) {
      console.error(`\n  Failed: ${url} — ${err.message}`);
    }
  }

  console.log(`\n\nDone. ${uploaded}/${urls.length} sources uploaded to "${NOTEBOOK_NAME}".`);
  console.log('Open NotebookLM to confirm: https://notebooklm.google.com\n');

  // Keep browser open so user can see result
  console.log('Press Ctrl+C to close the browser and exit.');
  await new Promise(() => {}); // keep alive
}

main().catch(err => {
  console.error('\nError:', err.message);
  console.error(err.stack);
  process.exit(1);
});
