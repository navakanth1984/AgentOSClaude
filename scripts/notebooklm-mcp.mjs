#!/usr/bin/env node
/**
 * notebooklm-mcp.mjs
 * MCP server for NotebookLM + YouTube workflow.
 * Registered in .mcp.json — Claude Code loads it as native tools.
 *
 * Tools:
 *   notebooklm_list_notebooks   — list all notebooks
 *   notebooklm_create_notebook  — create notebook + add YouTube sources
 *   youtube_fetch_urls          — fetch channel videos filtered by topic
 *   save_to_obsidian            — save a note to the Obsidian vault
 */

import { McpServer } from "@modelcontextprotocol/sdk/server/mcp.js";
import { StdioServerTransport } from "@modelcontextprotocol/sdk/server/stdio.js";
import { z } from "zod";
import { chromium } from "playwright";
import fs from "fs";
import path from "path";
import https from "https";
import { fileURLToPath } from "url";

const __dirname = path.dirname(fileURLToPath(import.meta.url));

// --- Chrome config ---
const CHROME_USER_DATA = "C:\\Users\\navka\\AppData\\Local\\Google\\Chrome\\User Data";
const CHROME_EXE       = "C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe";
const CHROME_EXE_86    = "C:\\Program Files (x86)\\Google\\Chrome\\Application\\chrome.exe";
const TEMP_PROFILE     = path.join(process.env.TEMP || "C:\\Temp", "notebooklm-mcp-profile");

// --- Browser helpers ---

async function launchBrowser() {
  const defaultDst = path.join(TEMP_PROFILE, "Default", "Network");
  fs.mkdirSync(defaultDst, { recursive: true });

  const cookieSrc = path.join(CHROME_USER_DATA, "Default", "Network", "Cookies");
  try { fs.copyFileSync(cookieSrc, path.join(defaultDst, "Cookies")); } catch (_) {}

  const executablePath =
    fs.existsSync(CHROME_EXE)    ? CHROME_EXE :
    fs.existsSync(CHROME_EXE_86) ? CHROME_EXE_86 :
    undefined;

  return chromium.launchPersistentContext(TEMP_PROFILE, {
    headless: false,
    executablePath,
    args: ["--no-first-run", "--no-default-browser-check", "--disable-extensions",
           "--disable-blink-features=AutomationControlled"],
    ignoreDefaultArgs: ["--enable-automation"],
    viewport: { width: 1280, height: 900 }
  });
}

async function goToNotebookLM(context) {
  const page = await context.newPage();
  await page.goto("https://notebooklm.google.com", { waitUntil: "domcontentloaded", timeout: 30000 });
  await page.waitForTimeout(3000);
  if (page.url().includes("accounts.google.com")) {
    await page.waitForURL("**/notebooklm.google.com**", { timeout: 120000 });
  }
  return page;
}

async function addUrlSource(page, url) {
  const addBtn = page.locator('button:has-text("Add source"), button:has-text("+ Add")').first();
  await addBtn.waitFor({ timeout: 10000 });
  await addBtn.click();
  await page.waitForTimeout(800);

  const youtubeOpt = page.locator('button:has-text("YouTube"), li:has-text("YouTube")').first();
  const websiteOpt = page.locator('button:has-text("Website"), button:has-text("URL")').first();
  if (await youtubeOpt.isVisible({ timeout: 2000 })) await youtubeOpt.click();
  else if (await websiteOpt.isVisible({ timeout: 2000 })) await websiteOpt.click();
  await page.waitForTimeout(600);

  const urlInput = page.locator('input[type="url"], input[placeholder*="url" i], input[placeholder*="YouTube" i]').first();
  await urlInput.waitFor({ timeout: 5000 });
  await urlInput.fill(url);
  await page.waitForTimeout(300);

  const insertBtn = page.locator('button:has-text("Insert"), button:has-text("Add"), button:has-text("Confirm")').first();
  if (await insertBtn.isVisible({ timeout: 2000 })) await insertBtn.click();
  else await page.keyboard.press("Enter");
  await page.waitForTimeout(1200);
}

// --- YouTube helper ---

function httpGet(url) {
  return new Promise((resolve, reject) => {
    https.get(url, (res) => {
      let data = "";
      res.on("data", chunk => data += chunk);
      res.on("end", () => {
        try { resolve(JSON.parse(data)); }
        catch (e) { reject(new Error("Failed to parse YouTube API response")); }
      });
    }).on("error", reject);
  });
}

async function fetchYouTubeVideos(channelId, topic, max) {
  const apiKey = process.env.YOUTUBE_API_KEY;
  if (!apiKey) throw new Error("YOUTUBE_API_KEY env variable is not set");

  const channelData = await httpGet(
    `https://www.googleapis.com/youtube/v3/channels?part=contentDetails&id=${channelId}&key=${apiKey}`
  );
  if (!channelData.items?.length) throw new Error(`Channel not found: ${channelId}`);
  const playlistId = channelData.items[0].contentDetails.relatedPlaylists.uploads;

  const videos = [];
  let pageToken = "";
  do {
    const data = await httpGet(
      `https://www.googleapis.com/youtube/v3/playlistItems?part=snippet&playlistId=${playlistId}&maxResults=50&pageToken=${pageToken}&key=${apiKey}`
    );
    for (const item of data.items || []) {
      videos.push({
        id:        item.snippet.resourceId.videoId,
        title:     item.snippet.title,
        url:       `https://www.youtube.com/watch?v=${item.snippet.resourceId.videoId}`,
        published: item.snippet.publishedAt,
      });
    }
    pageToken = data.nextPageToken || "";
  } while (pageToken && videos.length < max);

  const keywords = topic.toLowerCase().split(/\s+/).filter(Boolean);
  const filtered = keywords.length
    ? videos.filter(v => keywords.some(kw => v.title.toLowerCase().includes(kw)))
    : videos;

  return { channel: channelId, topic, total_fetched: videos.length, total_filtered: filtered.length, videos: filtered };
}

// --- MCP Server ---

const server = new McpServer({ name: "notebooklm-mcp-server", version: "1.0.0" });

// Tool 1: List notebooks
server.registerTool(
  "notebooklm_list_notebooks",
  {
    title: "List NotebookLM Notebooks",
    description: "Opens NotebookLM in Chrome and lists all existing notebook titles.",
    inputSchema: {},
    annotations: { readOnlyHint: true, openWorldHint: true }
  },
  async () => {
    const context = await launchBrowser();
    try {
      const page = await goToNotebookLM(context);
      await page.waitForTimeout(2000);

      const items = await page.locator('[data-testid*="notebook"], .notebook-item, article, [class*="NotebookCard"]').all();
      const notebooks = [];
      for (let i = 0; i < items.length; i++) {
        const title = await items[i].textContent().catch(() => `Notebook ${i + 1}`);
        notebooks.push(title.trim().slice(0, 100));
      }

      const result = { count: notebooks.length, notebooks };
      return {
        content: [{ type: "text", text: JSON.stringify(result, null, 2) }],
        structuredContent: result
      };
    } finally {
      await context.close();
    }
  }
);

// Tool 2: Create notebook + add sources
server.registerTool(
  "notebooklm_create_notebook",
  {
    title: "Create NotebookLM Notebook",
    description: "Creates a new NotebookLM notebook and adds YouTube URLs as sources. Pass urls as an array of YouTube video URLs.",
    inputSchema: {
      name: z.string().describe("Notebook name"),
      urls: z.array(z.string()).optional().default([]).describe("YouTube URLs to add as sources")
    },
    annotations: { destructiveHint: false }
  },
  async ({ name, urls }) => {
    const context = await launchBrowser();
    try {
      const page = await goToNotebookLM(context);

      // Create notebook
      const newBtn = page.locator('button:has-text("New notebook"), [aria-label="New notebook"]').first();
      await newBtn.waitFor({ timeout: 15000 });
      await newBtn.click();
      await page.waitForTimeout(2000);

      const titleInput = page.locator('input[placeholder*="title" i], input[placeholder*="name" i]').first();
      if (await titleInput.isVisible({ timeout: 3000 })) {
        await titleInput.clear();
        await titleInput.fill(name);
        await page.keyboard.press("Enter");
        await page.waitForTimeout(1500);
      }

      // Add sources
      let uploaded = 0;
      const failed = [];
      for (const url of urls) {
        try {
          await addUrlSource(page, url);
          uploaded++;
        } catch (e) {
          failed.push({ url, error: e.message });
        }
      }

      const result = { notebook: name, sources_requested: urls.length, sources_uploaded: uploaded, sources_failed: failed };
      return {
        content: [{ type: "text", text: JSON.stringify(result, null, 2) }],
        structuredContent: result
      };
    } finally {
      await context.close();
    }
  }
);

// Tool 3: Fetch YouTube URLs by topic
server.registerTool(
  "youtube_fetch_urls",
  {
    title: "Fetch YouTube URLs by Topic",
    description: "Fetches videos from a YouTube channel filtered by topic keywords. Requires YOUTUBE_API_KEY env variable. Returns video titles and URLs.",
    inputSchema: {
      channel_id: z.string().describe("YouTube channel ID (e.g. UCO_gBdHekc74feh0bNWoOuA)"),
      topic:      z.string().optional().default("").describe("Space-separated keywords to filter videos (e.g. 'health sleep focus')"),
      max:        z.number().int().min(1).max(500).optional().default(100).describe("Max videos to fetch from the channel")
    },
    annotations: { readOnlyHint: true, openWorldHint: true }
  },
  async ({ channel_id, topic, max }) => {
    const result = await fetchYouTubeVideos(channel_id, topic, max);
    return {
      content: [{ type: "text", text: JSON.stringify(result, null, 2) }],
      structuredContent: result
    };
  }
);

// Tool 4: Save to Obsidian vault
server.registerTool(
  "save_to_obsidian",
  {
    title: "Save Note to Obsidian",
    description: "Saves content (e.g. a NotebookLM answer or research summary) to the Obsidian vault at 01-Projects/AI-Automation/.",
    inputSchema: {
      title:   z.string().describe("Note title"),
      content: z.string().describe("Main content to save"),
      tags:    z.array(z.string()).optional().default([]).describe("Extra tags for the note"),
      source:  z.string().optional().default("NotebookLM").describe("Source description")
    },
    annotations: { readOnlyHint: false }
  },
  async ({ title, content, tags, source }) => {
    const date = new Date().toISOString().split("T")[0];
    const slug = title.toLowerCase().replace(/[^a-z0-9]+/g, "-").replace(/^-|-$/g, "");
    const filename = `${date}-${slug}.md`;
    const vaultDir = "C:\\Users\\navka\\OneDrive\\Documents\\Obsidian Vault\\01-Projects\\AI-Automation";
    const filepath = path.join(vaultDir, filename);

    const tagsList = ["notebooklm", "ai-automation", ...tags].map(t => `"${t}"`).join(", ");
    const note = `---
date: ${date}
tags: [${tagsList}]
project: "AI-Automation"
source: "${source}"
---

# ${title}

## Key Idea
${content}

## Action / Next Steps
- [ ] Review and organize
`;

    fs.mkdirSync(vaultDir, { recursive: true });
    fs.writeFileSync(filepath, note, "utf8");

    const result = { saved: true, path: filepath, filename };
    return {
      content: [{ type: "text", text: `Saved to Obsidian: ${filepath}` }],
      structuredContent: result
    };
  }
);

// Start
const transport = new StdioServerTransport();
await server.connect(transport);
