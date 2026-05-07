#!/usr/bin/env node
/**
 * get-youtube-urls.js
 * Fetches all videos from a YouTube channel and filters by topic keywords.
 *
 * Usage:
 *   node scripts/get-youtube-urls.js --channel UCO_gBdHekc74feh0bNWoOuA --topic "health sleep focus" --max 300
 *
 * Requires: YOUTUBE_API_KEY env variable
 *   Get a free key at: https://console.cloud.google.com → Enable YouTube Data API v3
 */

const https = require('https');

const args = Object.fromEntries(
  process.argv.slice(2).reduce((acc, val, i, arr) => {
    if (val.startsWith('--')) acc.push([val.slice(2), arr[i + 1]]);
    return acc;
  }, [])
);

const API_KEY = process.env.YOUTUBE_API_KEY;
const CHANNEL_ID = args.channel;
const TOPIC_KEYWORDS = (args.topic || '').toLowerCase().split(' ').filter(Boolean);
const MAX_RESULTS = parseInt(args.max || '300');
const OUTPUT_FILE = args.output || 'youtube-urls.json';

if (!API_KEY) {
  console.error('ERROR: Set YOUTUBE_API_KEY environment variable');
  console.error('  Get a free key: https://console.cloud.google.com → Enable YouTube Data API v3');
  process.exit(1);
}

if (!CHANNEL_ID) {
  console.error('ERROR: --channel <channelId> is required');
  console.error('  Example: node scripts/get-youtube-urls.js --channel UCO_gBdHekc74feh0bNWoOuA --topic "health sleep"');
  process.exit(1);
}

function get(url) {
  return new Promise((resolve, reject) => {
    https.get(url, (res) => {
      let data = '';
      res.on('data', chunk => data += chunk);
      res.on('end', () => {
        try { resolve(JSON.parse(data)); }
        catch (e) { reject(new Error('Failed to parse response')); }
      });
    }).on('error', reject);
  });
}

async function getChannelUploadsPlaylist(channelId) {
  const url = `https://www.googleapis.com/youtube/v3/channels?part=contentDetails&id=${channelId}&key=${API_KEY}`;
  const data = await get(url);
  if (!data.items?.length) throw new Error(`Channel not found: ${channelId}`);
  return data.items[0].contentDetails.relatedPlaylists.uploads;
}

async function getAllVideos(playlistId) {
  const videos = [];
  let pageToken = '';

  do {
    const url = `https://www.googleapis.com/youtube/v3/playlistItems?part=snippet&playlistId=${playlistId}&maxResults=50&pageToken=${pageToken}&key=${API_KEY}`;
    const data = await get(url);

    for (const item of data.items || []) {
      videos.push({
        id: item.snippet.resourceId.videoId,
        title: item.snippet.title,
        description: item.snippet.description?.slice(0, 200) || '',
        published: item.snippet.publishedAt,
        url: `https://www.youtube.com/watch?v=${item.snippet.resourceId.videoId}`
      });
    }

    pageToken = data.nextPageToken || '';
    process.stderr.write(`\rFetched ${videos.length} videos...`);
  } while (pageToken && videos.length < MAX_RESULTS);

  process.stderr.write('\n');
  return videos;
}

function filterByTopic(videos, keywords) {
  if (!keywords.length) return videos;
  return videos.filter(v => {
    const text = (v.title + ' ' + v.description).toLowerCase();
    return keywords.some(kw => text.includes(kw));
  });
}

async function main() {
  console.log(`Fetching videos from channel: ${CHANNEL_ID}`);
  console.log(`Topic filter: ${TOPIC_KEYWORDS.join(', ') || 'none (all videos)'}`);

  const playlistId = await getChannelUploadsPlaylist(CHANNEL_ID);
  const allVideos = await getAllVideos(playlistId);
  const filtered = filterByTopic(allVideos, TOPIC_KEYWORDS);

  const result = {
    channel: CHANNEL_ID,
    topic: TOPIC_KEYWORDS.join(' '),
    total_fetched: allVideos.length,
    total_filtered: filtered.length,
    generated: new Date().toISOString(),
    videos: filtered
  };

  const fs = require('fs');
  fs.writeFileSync(OUTPUT_FILE, JSON.stringify(result, null, 2));

  console.log(`\nResults:`);
  console.log(`  Total videos on channel: ${allVideos.length}`);
  console.log(`  Matching topic: ${filtered.length}`);
  console.log(`  Saved to: ${OUTPUT_FILE}`);
  console.log(`\nFirst 5 matches:`);
  filtered.slice(0, 5).forEach(v => console.log(`  - ${v.title}`));

  // Also print just URLs to stdout for piping
  process.stdout.write('\n--- URLS ---\n');
  filtered.forEach(v => console.log(v.url));
}

main().catch(err => {
  console.error('Error:', err.message);
  process.exit(1);
});
