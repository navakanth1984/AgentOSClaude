// Frame-exact renderer: drives a page's window.renderAt(t) in headless Chrome and pipes PNGs to ffmpeg.
// Page contract: window.renderAt(t), window.DURATION, window.__ready = true; honours ?render&w=&h=.
// FILM_URL env var = page URL without query (default http://localhost:5506/video.html).
// usage: node render.mjs keys <W> <H> <outDir>
//        node render.mjs video <W> <H> <fps> <out.mp4>
import puppeteer from 'puppeteer-core';
import { spawn } from 'node:child_process';
import { writeFileSync, mkdirSync, existsSync, renameSync } from 'node:fs';

const [, , mode = 'keys', W = '1920', H = '1080', a4, a5] = process.argv;
const browser = await puppeteer.launch({
  executablePath: 'C:/Program Files/Google/Chrome/Application/chrome.exe',
  headless: 'new',
  args: ['--use-angle=d3d11', '--ignore-gpu-blocklist', '--enable-unsafe-swiftshader', `--window-size=${W},${H}`],
});
const page = await browser.newPage();
await page.setViewport({ width: +W, height: +H, deviceScaleFactor: 1 });
page.on('console', m => { if (m.type() === 'error') console.error('PAGE:', m.text()); });
page.on('pageerror', e => console.error('PAGEERROR:', e.message));
const FILM_URL = process.env.FILM_URL || 'http://localhost:5506/video';   // clean URL: `serve` 301s .html and DROPS the query
await page.goto(`${FILM_URL}?render&w=${W}&h=${H}`, { waitUntil: 'load', timeout: 120000 });
const pageMode = await page.evaluate(() => [document.body.className, innerWidth, innerHeight]);
if (!String(pageMode[0]).includes('render')) throw new Error(`page not in render mode (${page.url()} -> ${pageMode}): did a redirect drop the ?query?`);
await page.waitForFunction('window.__ready === true', { timeout: 120000 });
console.log('renderer:', await page.evaluate(() => {
  const gl = document.querySelector('canvas').getContext('webgl2');
  const ext = gl && gl.getExtension('WEBGL_debug_renderer_info');
  return ext ? gl.getParameter(ext.UNMASKED_RENDERER_WEBGL) : 'unknown';
}));

const grab = async t => Buffer.from(await page.evaluate(t => {
  window.renderAt(t);
  return document.querySelector('canvas').toDataURL('image/png').split(',')[1];
}, t), 'base64');

if (mode === 'frames') {
  // resumable: one PNG per frame on disk, existing frames skipped; encode afterwards with ffmpeg (Chrome closed = RAM free)
  const fps = +a4, dir = a5; mkdirSync(dir, { recursive: true });
  const total = Math.round((await page.evaluate(() => window.DURATION)) * fps), t0 = Date.now();
  for (let f = 0; f < total; f++) {
    const fn = `${dir}/f_${String(f).padStart(5, '0')}.png`;
    if (existsSync(fn)) continue;
    writeFileSync(fn + '.tmp', await grab(f / fps)); renameSync(fn + '.tmp', fn);
    if (f % 30 === 0) console.log(`frame ${f}/${total}  ${((Date.now() - t0) / 1000).toFixed(0)}s`);
  }
  console.log(`done: ${total} frames → ${dir}`);
} else if (mode === 'keys') {
  mkdirSync(a4, { recursive: true });
  for (const t of (a5 ? a5.split(',').map(Number) : [1.5, 4, 6, 8, 10.5, 13, 15, 17, 19, 21, 23.2])) {
    writeFileSync(`${a4}/key_${String(t).padStart(4, '0')}.png`, await grab(t));
    console.log('key', t);
  }
} else {
  const fps = +a4, out = a5;
  const dur = await page.evaluate(() => window.DURATION);
  const total = Math.round(dur * fps);
  const ff = spawn('ffmpeg', ['-y', '-loglevel', 'error', '-f', 'image2pipe', '-framerate', String(fps), '-i', '-',
    ...(process.env.CODEC === 'x265'      // IMAX/4K master: HEVC 10-bit
      ? ['-c:v', 'libx265', '-pix_fmt', 'yuv420p10le', '-crf', '14', '-preset', 'medium', '-tag:v', 'hvc1', '-x265-params', 'log-level=error']
      : ['-c:v', 'libx264', '-pix_fmt', 'yuv420p', '-crf', '17', '-preset', 'slow']), '-movflags', '+faststart', out],
    { stdio: ['pipe', 'inherit', 'inherit'] });
  const t0 = Date.now();
  for (let f = 0; f < total; f++) {
    const buf = await grab(f / fps);
    if (!ff.stdin.write(buf)) await new Promise(r => ff.stdin.once('drain', r));
    if (f % 60 === 0) console.log(`frame ${f}/${total}  ${((Date.now() - t0) / 1000).toFixed(0)}s`);
  }
  ff.stdin.end();
  await new Promise(r => ff.on('close', r));
  console.log(`done: ${total} frames in ${((Date.now() - t0) / 1000).toFixed(0)}s → ${out}`);
}
await browser.close();
