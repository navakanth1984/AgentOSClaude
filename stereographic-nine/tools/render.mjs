// Frame-exact renderer: drives video.html's renderAt(t) in headless Chrome and pipes PNGs to ffmpeg.
// usage: node render.mjs keys <W> <H> <outDir>
//        node render.mjs video <W> <H> <fps> <out.mp4>
import puppeteer from 'puppeteer-core';
import { spawn } from 'node:child_process';
import { writeFileSync, mkdirSync } from 'node:fs';

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
await page.goto(`http://localhost:5506/video.html?render&w=${W}&h=${H}`, { waitUntil: 'networkidle0', timeout: 120000 });
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

if (mode === 'keys') {
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
    '-c:v', 'libx264', '-pix_fmt', 'yuv420p', '-crf', '17', '-preset', 'slow', '-movflags', '+faststart', out],
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
