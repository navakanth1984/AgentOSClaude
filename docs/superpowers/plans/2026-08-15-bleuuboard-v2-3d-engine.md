# BleuuBoard v2 — Fork + Babylon.js/Poly Haven Engine Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Fork BleuuBoard into `projects/bleuuboard-v2/`, replace its Three.js
rendering core with Babylon.js, and prove out a Poly Haven-sourced,
device-tiered PBR environment (desktop full-fidelity, mobile lightweight)
that loads progressively with zero added latency to first interactive paint.

**Architecture:** A new, isolated static site (own port, own server, own
Vercel project) built from a copy of the original's `index.html`/`server.cjs`.
Three.js CDN script tags are removed and replaced with Babylon.js CDN script
tags. A new `js/device-tier.js` module decides mobile vs. desktop quality at
load. A new `js/environment.js` module builds the Babylon scene (camera,
lights, ground) and loads Poly Haven HDRI/PBR textures progressively —
low-res placeholder first, full-res streamed in after first paint.

**Tech Stack:** Babylon.js (Apache-2.0, via CDN — `@babylonjs/core`,
`@babylonjs/loaders`), Poly Haven CC0 assets (HDRI + PBR textures, downloaded
and committed to the repo, not proxied at runtime), vanilla JS (no build
step, matching the original's zero-tooling convention), Node's built-in
`http` module for the dev server (matching `whiteboard-4d/server.cjs`).

## Global Constraints

- The original `whiteboard-4d/` and its Vercel deployments
  (`bleuboard.vercel.app`, `bleuboard-dev.vercel.app`) must not be modified
  or touched by any task in this plan.
- No build tooling is introduced (no webpack/Vite/npm scripts) — this fork
  stays a static HTML/CSS/JS site like the original, per the spec's
  "isolation via separate codebase, not architecture upheaval" framing.
- Only Poly Haven (CC0) assets are used in this plan. No Sketchfab or other
  variable-license source — explicitly deferred per spec.
- Every task must leave the app running with 0 browser console errors on
  both a 1920x1080 desktop viewport and a 390x844 mobile viewport before
  being considered done.
- This plan covers ONLY the environment/lighting/camera scene (the spec's
  success criteria). It does NOT port the original's drawing tools
  (strokes, text, image placement, raycasting-based object interaction) —
  that migration is out of scope here and would be a follow-up plan.

---

### Task 1: Fork skeleton — isolated server, port, and empty scene shell

**Files:**
- Create: `projects/bleuuboard-v2/server.cjs`
- Create: `projects/bleuuboard-v2/vercel.json`
- Create: `projects/bleuuboard-v2/index.html`
- Create: `projects/bleuuboard-v2/verify_server.js`

**Interfaces:**
- Consumes: nothing (first task)
- Produces: a running dev server at `http://127.0.0.1:3002/` serving
  `index.html`. Later tasks add `<script>` tags and `js/*.js` files into this
  `index.html` — they do not replace it.

- [ ] **Step 1: Create the server file**

`projects/bleuuboard-v2/server.cjs` — copy of `whiteboard-4d/server.cjs` with
the port changed from `3000` to `3002`:

```javascript
const http = require('http');
const fs = require('fs');
const path = require('path');

const PORT = 3002;
const MIME_TYPES = {
  '.html': 'text/html',
  '.js': 'text/javascript',
  '.css': 'text/css',
  '.json': 'application/json',
  '.png': 'image/png',
  '.svg': 'image/svg+xml',
  '.hdr': 'application/octet-stream',
  '.env': 'application/octet-stream',
  '.glb': 'model/gltf-binary',
  '.gltf': 'model/gltf+json',
  '.ktx2': 'application/octet-stream',
  '.bin': 'application/octet-stream',
  '.wasm': 'application/wasm'
};

http.createServer((req, res) => {
  const urlPath = req.url.split('?')[0];
  let filePath = path.join(__dirname, urlPath === '/' ? 'index.html' : urlPath);
  let extname = path.extname(filePath);

  fs.readFile(filePath, (err, content) => {
    if (err) {
      if (err.code === 'ENOENT') {
        res.writeHead(404);
        res.end('404 Not Found');
      } else {
        res.writeHead(500);
        res.end('500 Internal Error');
      }
    } else {
      res.writeHead(200, { 'Content-Type': MIME_TYPES[extname] || 'application/octet-stream' });
      res.end(content, 'utf-8');
    }
  });
}).listen(PORT, '127.0.0.1', () => {
  console.log(`Server running at http://127.0.0.1:${PORT}/`);
});
```

- [ ] **Step 2: Create the Vercel config**

`projects/bleuuboard-v2/vercel.json`:

```json
{
  "version": 2,
  "name": "bleuuboard-v2",
  "builds": [
    { "src": "index.html", "use": "@vercel/static" }
  ],
  "routes": [
    { "src": "/(.*)", "dest": "/index.html" }
  ]
}
```

- [ ] **Step 3: Create a minimal placeholder index.html**

`projects/bleuuboard-v2/index.html`:

```html
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
<title>BLEUUBOARD v2 — 4D Creative Whiteboard</title>
<style>
*{margin:0;padding:0;box-sizing:border-box;}
html,body{overflow:hidden;width:100%;height:100%;background:#00000d;}
canvas#c{position:fixed;inset:0;touch-action:none;display:block;}
</style>
</head>
<body>
<canvas id="c"></canvas>
</body>
</html>
```

- [ ] **Step 4: Write the verification script**

`projects/bleuuboard-v2/verify_server.js` — a plain Node script (no test
framework in this repo, matching the original's convention) that asserts the
server responds:

```javascript
const http = require('http');

http.get('http://127.0.0.1:3002/', (res) => {
  if (res.statusCode !== 200) {
    console.error(`FAIL: expected 200, got ${res.statusCode}`);
    process.exit(1);
  }
  let body = '';
  res.on('data', (chunk) => { body += chunk; });
  res.on('end', () => {
    if (!body.includes('BLEUUBOARD v2')) {
      console.error('FAIL: response body missing expected title');
      process.exit(1);
    }
    console.log('PASS: server responds 200 with expected content');
    process.exit(0);
  });
}).on('error', (err) => {
  console.error(`FAIL: request error — ${err.message}`);
  process.exit(1);
});
```

- [ ] **Step 5: Run the server and verify it fails without being started**

Run: `node "C:/Users/navka/navakanth001/projects/bleuuboard-v2/verify_server.js"`
Expected: FAIL with a connection error (`ECONNREFUSED`) — server isn't running yet.

- [ ] **Step 6: Start the server in the background, then verify it passes**

Run: `node "C:/Users/navka/navakanth001/projects/bleuuboard-v2/server.cjs"` (background)
Then run: `node "C:/Users/navka/navakanth001/projects/bleuuboard-v2/verify_server.js"`
Expected: `PASS: server responds 200 with expected content`, exit code 0.

- [ ] **Step 7: Commit**

```bash
git add projects/bleuuboard-v2/server.cjs projects/bleuuboard-v2/vercel.json projects/bleuuboard-v2/index.html projects/bleuuboard-v2/verify_server.js
git commit -m "feat(bleuuboard-v2): fork skeleton — isolated server on port 3002"
```

---

### Task 2: Replace Three.js with Babylon.js — bare scene, camera, canvas

**Files:**
- Modify: `projects/bleuuboard-v2/index.html`
- Create: `projects/bleuuboard-v2/verify_no_three.js`

**Interfaces:**
- Consumes: `index.html`'s `<canvas id="c">` from Task 1
- Produces: a global `window.__bleuu_scene` (Babylon `Scene` instance) and
  `window.__bleuu_engine` (Babylon `Engine` instance) that Task 3 and Task 4
  read to attach lights/environment.

- [ ] **Step 1: Write the failing verification script**

`projects/bleuuboard-v2/verify_no_three.js` — asserts `index.html` contains
no Three.js references and does contain Babylon.js references:

```javascript
const fs = require('fs');
const html = fs.readFileSync('C:/Users/navka/navakanth001/projects/bleuuboard-v2/index.html', 'utf-8');

const checks = [
  { name: 'no three.js CDN script', pass: !/cdn\.jsdelivr\.net\/npm\/three@/.test(html) },
  { name: 'no THREE. references', pass: !/THREE\./.test(html) },
  { name: 'babylon.js CDN script present', pass: /cdn\.babylonjs\.com\/babylon\.js/.test(html) },
  { name: 'BABYLON.Engine reference present', pass: /BABYLON\.Engine/.test(html) },
  { name: 'BABYLON.Scene reference present', pass: /BABYLON\.Scene/.test(html) },
];

let failed = false;
for (const c of checks) {
  console.log(`${c.pass ? 'PASS' : 'FAIL'}: ${c.name}`);
  if (!c.pass) failed = true;
}
process.exit(failed ? 1 : 0);
```

- [ ] **Step 2: Run it to verify it fails**

Run: `node "C:/Users/navka/navakanth001/projects/bleuuboard-v2/verify_no_three.js"`
Expected: FAIL on the Babylon checks — `index.html` from Task 1 has no engine
code at all yet.

- [ ] **Step 3: Add Babylon.js and the bare scene to index.html**

Modify `projects/bleuuboard-v2/index.html` — add before `</body>`:

```html
<script src="https://cdn.babylonjs.com/babylon.js"></script>
<script src="https://cdn.babylonjs.com/loaders/babylonjs.loaders.min.js"></script>
<script>
const canvas = document.getElementById('c');
const engine = new BABYLON.Engine(canvas, true, { preserveDrawingBuffer: true, stencil: true });
const scene = new BABYLON.Scene(engine);
scene.clearColor = new BABYLON.Color4(0, 0.0157, 0.051, 1);

const camera = new BABYLON.ArcRotateCamera(
  'camera', -Math.PI / 2, Math.PI / 2.5, 30,
  new BABYLON.Vector3(0, 0, 0), scene
);
camera.attachControl(canvas, true);
camera.lowerRadiusLimit = 5;
camera.upperRadiusLimit = 200;

window.__bleuu_engine = engine;
window.__bleuu_scene = scene;

engine.runRenderLoop(() => { scene.render(); });
window.addEventListener('resize', () => { engine.resize(); });
</script>
```

- [ ] **Step 4: Run the verification script to confirm it passes**

Run: `node "C:/Users/navka/navakanth001/projects/bleuuboard-v2/verify_no_three.js"`
Expected: all 5 checks PASS, exit code 0.

- [ ] **Step 5: Browser verification — 0 console errors, both viewports**

Using the Browser preview tool:
1. `preview_start` with `{url: "http://127.0.0.1:3002/"}` (start
   `server.cjs` first if not already running from Task 1)
2. `read_console_messages` with `onlyErrors: true` — expect an empty array
3. `resize_window` to `{preset: "mobile"}`, reload, `read_console_messages`
   with `onlyErrors: true` again — expect an empty array
4. `computer` `{action: "screenshot"}` on both viewports to confirm a dark
   canvas renders (no visible error overlay)

- [ ] **Step 6: Commit**

```bash
git add projects/bleuuboard-v2/index.html projects/bleuuboard-v2/verify_no_three.js
git commit -m "feat(bleuuboard-v2): replace Three.js with bare Babylon.js scene"
```

---

### Task 3: Device-tier detection module

**Files:**
- Create: `projects/bleuuboard-v2/js/device-tier.js`
- Modify: `projects/bleuuboard-v2/index.html`
- Create: `projects/bleuuboard-v2/verify_device_tier.js`

**Interfaces:**
- Consumes: nothing (pure function module, no Babylon dependency)
- Produces: global `window.BleuuDeviceTier.detect()` returning the exact
  string `'mobile'` or `'desktop'`. Task 4 calls this to decide which
  environment assets to load.

- [ ] **Step 1: Write the failing test**

`projects/bleuuboard-v2/verify_device_tier.js` — a Node-runnable test using a
minimal fake `navigator`/`window` (since this module must be loadable and
testable outside a real browser):

```javascript
// Minimal DOM/navigator stub so device-tier.js's logic can be unit-tested in Node
global.window = global;
global.navigator = { userAgent: '', maxTouchPoints: 0 };
global.matchMedia = (query) => ({ matches: false });

require('./js/device-tier.js');

function test(name, fn) {
  try {
    fn();
    console.log(`PASS: ${name}`);
  } catch (e) {
    console.error(`FAIL: ${name} — ${e.message}`);
    process.exitCode = 1;
  }
}

function assertEqual(actual, expected, msg) {
  if (actual !== expected) throw new Error(`${msg}: expected ${expected}, got ${actual}`);
}

test('desktop UA with no touch points detects desktop', () => {
  global.navigator.userAgent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)';
  global.navigator.maxTouchPoints = 0;
  assertEqual(window.BleuuDeviceTier.detect(), 'desktop', 'desktop UA');
});

test('mobile UA detects mobile', () => {
  global.navigator.userAgent = 'Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X)';
  global.navigator.maxTouchPoints = 5;
  assertEqual(window.BleuuDeviceTier.detect(), 'mobile', 'mobile UA');
});

test('narrow viewport with touch points detects mobile even on ambiguous UA', () => {
  global.navigator.userAgent = 'Mozilla/5.0 (Linux; Android 13)';
  global.navigator.maxTouchPoints = 5;
  assertEqual(window.BleuuDeviceTier.detect(), 'mobile', 'android UA');
});
```

- [ ] **Step 2: Run it to verify it fails**

Run: `cd "C:/Users/navka/navakanth001/projects/bleuuboard-v2" && node verify_device_tier.js`
Expected: FAIL — `require('./js/device-tier.js')` throws `MODULE_NOT_FOUND`
since the file doesn't exist yet.

- [ ] **Step 3: Write the minimal implementation**

`projects/bleuuboard-v2/js/device-tier.js`:

```javascript
(function () {
  function detect() {
    const ua = navigator.userAgent || '';
    const isMobileUA = /Mobi|Android|iPhone|iPad|iPod/i.test(ua);
    const hasTouch = (navigator.maxTouchPoints || 0) > 0;
    return (isMobileUA || hasTouch) ? 'mobile' : 'desktop';
  }

  const api = { detect };
  if (typeof window !== 'undefined') {
    window.BleuuDeviceTier = api;
  }
  if (typeof module !== 'undefined' && module.exports) {
    module.exports = api;
  }
})();
```

- [ ] **Step 4: Run the test to verify it passes**

Run: `cd "C:/Users/navka/navakanth001/projects/bleuuboard-v2" && node verify_device_tier.js`
Expected: all 3 tests PASS, exit code 0.

- [ ] **Step 5: Wire the module into index.html**

Modify `projects/bleuuboard-v2/index.html` — add before the Babylon `<script>`
block from Task 2:

```html
<script src="js/device-tier.js"></script>
```

- [ ] **Step 6: Browser verification**

1. `preview_start` (or reuse the running server from Task 2)
2. `javascript_tool`: `window.BleuuDeviceTier.detect()` → expect `"desktop"`
   at default (desktop) viewport size
3. `resize_window` to `{preset: "mobile"}`, reload, `javascript_tool`:
   `window.BleuuDeviceTier.detect()` → expect `"mobile"`
4. `read_console_messages` with `onlyErrors: true` on both — expect empty

- [ ] **Step 7: Commit**

```bash
git add projects/bleuuboard-v2/js/device-tier.js projects/bleuuboard-v2/verify_device_tier.js projects/bleuuboard-v2/index.html
git commit -m "feat(bleuuboard-v2): device-tier detection module"
```

---

### Task 4: Poly Haven environment — progressive HDRI/PBR loading, tiered by device

**Files:**
- Create: `projects/bleuuboard-v2/js/environment.js`
- Create: `projects/bleuuboard-v2/assets/env/studio_small_08_1k.hdr` (Poly Haven, CC0)
- Create: `projects/bleuuboard-v2/assets/env/studio_small_08_2k.hdr` (Poly Haven, CC0)
- Create: `projects/bleuuboard-v2/assets/textures/concrete_floor/` (Poly Haven PBR set: `*_diff.jpg`, `*_nor.jpg`, `*_rough.jpg`, CC0)
- Modify: `projects/bleuuboard-v2/index.html`
- Create: `projects/bleuuboard-v2/verify_environment.js`

**Interfaces:**
- Consumes: `window.__bleuu_scene` (Task 2), `window.BleuuDeviceTier.detect()` (Task 3)
- Produces: `window.BleuuEnvironment.load(scene, tier)` — async function
  returning a Promise that resolves once environment loading (placeholder +
  full-res swap) completes. No later task in this plan consumes this return
  value directly; browser verification checks it manually.

- [ ] **Step 1: Download the Poly Haven assets (not code — asset acquisition)**

Download from Poly Haven (CC0, no attribution required, verify each URL
returns 200 before use):
- `https://polyhaven.com/a/studio_small_08` → download 1K `.hdr` (placeholder,
  smaller file) and 2K `.hdr` (full-res) into `projects/bleuuboard-v2/assets/env/`
- `https://polyhaven.com/a/concrete_floor_02` (or similar concrete/PBR
  texture set) → download the diffuse/normal/roughness JPGs into
  `projects/bleuuboard-v2/assets/textures/concrete_floor/`

Record the exact asset names/URLs used in a
`projects/bleuuboard-v2/assets/SOURCES.md` file (CC0, Poly Haven, URL, download
date) for future license auditing.

- [ ] **Step 2: Write the failing verification script**

`projects/bleuuboard-v2/verify_environment.js`:

```javascript
const fs = require('fs');
const path = require('path');

const base = 'C:/Users/navka/navakanth001/projects/bleuuboard-v2';

const checks = [
  { name: 'environment.js module exists', pass: fs.existsSync(path.join(base, 'js/environment.js')) },
  { name: '1k HDRI placeholder asset exists', pass: fs.existsSync(path.join(base, 'assets/env/studio_small_08_1k.hdr')) },
  { name: '2k HDRI full-res asset exists', pass: fs.existsSync(path.join(base, 'assets/env/studio_small_08_2k.hdr')) },
  { name: 'PBR texture directory exists', pass: fs.existsSync(path.join(base, 'assets/textures/concrete_floor')) },
  { name: 'SOURCES.md license record exists', pass: fs.existsSync(path.join(base, 'assets/SOURCES.md')) },
];

let failed = false;
for (const c of checks) {
  console.log(`${c.pass ? 'PASS' : 'FAIL'}: ${c.name}`);
  if (!c.pass) failed = true;
}
process.exit(failed ? 1 : 0);
```

- [ ] **Step 3: Run it to verify it fails**

Run: `node "C:/Users/navka/navakanth001/projects/bleuuboard-v2/verify_environment.js"`
Expected: FAIL on all 5 checks — nothing created yet.

- [ ] **Step 4: Write the environment module**

`projects/bleuuboard-v2/js/environment.js`:

```javascript
(function () {
  async function load(scene, tier) {
    const isMobile = tier === 'mobile';

    // Progressive load: placeholder (1k) first on every tier so first paint
    // is never blocked, then swap to full-res (2k) only on desktop.
    const placeholderHDRI = new BABYLON.HDRCubeTexture(
      'assets/env/studio_small_08_1k.hdr', scene, 128, false, true, false, true
    );
    scene.environmentTexture = placeholderHDRI;
    scene.createDefaultSkybox(placeholderHDRI, true, 1000);

    const ground = BABYLON.MeshBuilder.CreateGround('ground', { width: 120, height: 120 }, scene);
    const groundMat = new BABYLON.PBRMaterial('groundMat', scene);

    if (isMobile) {
      // Mobile tier: solid color, no texture fetch, no full-res swap.
      groundMat.albedoColor = new BABYLON.Color3(0.25, 0.25, 0.27);
      groundMat.roughness = 0.9;
      ground.material = groundMat;
      return Promise.resolve({ tier: 'mobile', hdri: '1k', textured: false });
    }

    // Desktop tier: PBR textures + full-res HDRI swap after first paint.
    groundMat.albedoTexture = new BABYLON.Texture('assets/textures/concrete_floor/concrete_floor_02_diff.jpg', scene);
    groundMat.bumpTexture = new BABYLON.Texture('assets/textures/concrete_floor/concrete_floor_02_nor.jpg', scene);
    groundMat.metallicTexture = new BABYLON.Texture('assets/textures/concrete_floor/concrete_floor_02_rough.jpg', scene);
    groundMat.useRoughnessFromMetallicTextureAlpha = false;
    groundMat.useRoughnessFromMetallicTextureGreen = true;
    ground.material = groundMat;

    return new Promise((resolve) => {
      const fullHDRI = new BABYLON.HDRCubeTexture(
        'assets/env/studio_small_08_2k.hdr', scene, 256, false, true, false, true
      );
      fullHDRI.onLoadObservable.addOnce(() => {
        scene.environmentTexture = fullHDRI;
        scene.createDefaultSkybox(fullHDRI, true, 1000);
        resolve({ tier: 'desktop', hdri: '2k', textured: true });
      });
    });
  }

  const api = { load };
  if (typeof window !== 'undefined') {
    window.BleuuEnvironment = api;
  }
  if (typeof module !== 'undefined' && module.exports) {
    module.exports = api;
  }
})();
```

- [ ] **Step 5: Create the SOURCES.md license record**

`projects/bleuuboard-v2/assets/SOURCES.md`:

```markdown
# Asset Sources

All assets in this directory are CC0 (public domain) from Poly Haven —
no attribution required, free for any use.

| Asset | Poly Haven page | Downloaded |
|---|---|---|
| studio_small_08_1k.hdr / 2k.hdr | https://polyhaven.com/a/studio_small_08 | 2026-08-15 |
| concrete_floor/* | https://polyhaven.com/a/concrete_floor_02 | 2026-08-15 |
```

- [ ] **Step 6: Wire environment.js into index.html**

Modify `projects/bleuuboard-v2/index.html` — add the script tag after
`device-tier.js` and before the Babylon scene-setup block, then call it once
the scene exists:

```html
<script src="js/environment.js"></script>
```

And inside the existing Babylon `<script>` block from Task 2, after
`window.__bleuu_scene = scene;`, add:

```javascript
const tier = window.BleuuDeviceTier.detect();
window.BleuuEnvironment.load(scene, tier).then((result) => {
  window.__bleuu_env_loaded = result;
  console.log('[bleuuboard-v2] environment loaded:', result);
});
```

- [ ] **Step 7: Run the file-existence verification script to confirm it passes**

Run: `node "C:/Users/navka/navakanth001/projects/bleuuboard-v2/verify_environment.js"`
Expected: all 5 checks PASS, exit code 0.

- [ ] **Step 8: Browser verification — desktop tier**

1. Ensure server is running (`server.cjs` on port 3002), viewport at desktop default
2. Navigate/reload `http://127.0.0.1:3002/`
3. `read_console_messages` with `onlyErrors: true` → expect empty array
4. `javascript_tool`: `window.__bleuu_env_loaded` → expect
   `{tier: 'desktop', hdri: '2k', textured: true}` (poll/wait briefly if the
   HDRI hasn't finished loading yet)
5. `computer` `{action: "screenshot"}` → expect a lit ground plane with
   visible texture/reflection, not a flat color

- [ ] **Step 9: Browser verification — mobile tier**

1. `resize_window` to `{preset: "mobile"}`, reload
2. `read_console_messages` with `onlyErrors: true` → expect empty array
3. `javascript_tool`: `window.__bleuu_env_loaded` → expect
   `{tier: 'mobile', hdri: '1k', textured: false}`
4. `computer` `{action: "screenshot"}` → expect a solid-color ground (no
   texture fetch attempted), confirming the mobile tier skipped the heavier assets

- [ ] **Step 10: Commit**

```bash
git add projects/bleuuboard-v2/js/environment.js projects/bleuuboard-v2/assets/ projects/bleuuboard-v2/index.html projects/bleuuboard-v2/verify_environment.js
git commit -m "feat(bleuuboard-v2): Poly Haven PBR environment, device-tiered + progressive load"
```

---

### Task 5: Lighting pass — sun + fill lights matching original's mood, both tiers

**Files:**
- Modify: `projects/bleuuboard-v2/js/environment.js`
- Modify: `projects/bleuuboard-v2/verify_environment.js`

**Interfaces:**
- Consumes: `scene` parameter already passed into `BleuuEnvironment.load()`
- Produces: no new exports — extends the existing `load()` function's side
  effects (adds lights to the scene passed in)

- [ ] **Step 1: Write the failing test — extend verify_environment.js**

Add to `projects/bleuuboard-v2/verify_environment.js`, before the existing
`checks` array's `process.exit`:

```javascript
const envSource = fs.readFileSync(path.join(base, 'js/environment.js'), 'utf-8');
const lightChecks = [
  { name: 'environment.js creates a DirectionalLight (sun)', pass: /new BABYLON\.DirectionalLight/.test(envSource) },
  { name: 'environment.js creates a HemisphericLight (ambient fill)', pass: /new BABYLON\.HemisphericLight/.test(envSource) },
];
for (const c of lightChecks) {
  console.log(`${c.pass ? 'PASS' : 'FAIL'}: ${c.name}`);
  if (!c.pass) failed = true;
}
```

- [ ] **Step 2: Run it to verify it fails**

Run: `node "C:/Users/navka/navakanth001/projects/bleuuboard-v2/verify_environment.js"`
Expected: the two new light checks FAIL (not yet implemented); the 5 asset
checks from Task 4 still PASS.

- [ ] **Step 3: Add lights to environment.js**

Modify `projects/bleuuboard-v2/js/environment.js` — inside the `load`
function, immediately after `scene.createDefaultSkybox(placeholderHDRI, true, 1000);`
near the top (so both tiers get lighting, not just desktop):

```javascript
    const ambient = new BABYLON.HemisphericLight('ambient', new BABYLON.Vector3(0, 1, 0), scene);
    ambient.intensity = 0.6;
    ambient.diffuse = new BABYLON.Color3(0.1, 0.16, 0.33);

    const sun = new BABYLON.DirectionalLight('sun', new BABYLON.Vector3(-0.5, -1, -0.3), scene);
    sun.intensity = 2.0;
    sun.diffuse = new BABYLON.Color3(1, 1, 1);
```

- [ ] **Step 4: Run the verification script to confirm it passes**

Run: `node "C:/Users/navka/navakanth001/projects/bleuuboard-v2/verify_environment.js"`
Expected: all 7 checks PASS (5 from Task 4 + 2 new light checks), exit code 0.

- [ ] **Step 5: Browser verification — both viewports**

1. Desktop viewport: reload, `read_console_messages` `onlyErrors: true` →
   empty; `computer` `{action: "screenshot"}` → visible directional shading
   on the ground plane (not flat/uniform lighting)
2. `resize_window` `{preset: "mobile"}`, reload, same checks

- [ ] **Step 6: Commit**

```bash
git add projects/bleuuboard-v2/js/environment.js projects/bleuuboard-v2/verify_environment.js
git commit -m "feat(bleuuboard-v2): directional + ambient lighting, both device tiers"
```

---

### Task 6: Final ADLC verification pass — matches original's verified bar

**Files:**
- Create: `projects/bleuuboard-v2/verification/desktop-screenshot.png` (captured, not authored)
- Create: `projects/bleuuboard-v2/verification/mobile-screenshot.png` (captured, not authored)
- Create: `projects/bleuuboard-v2/VERIFICATION.md`

**Interfaces:**
- Consumes: the fully assembled `index.html` from Tasks 1–5
- Produces: nothing consumed by other tasks — this is the plan's final gate

- [ ] **Step 1: Run every prior verification script in sequence**

```bash
cd "C:/Users/navka/navakanth001/projects/bleuuboard-v2"
node verify_server.js
node verify_no_three.js
node verify_device_tier.js
node verify_environment.js
```

Expected: all four scripts print only `PASS:` lines and exit code 0.

- [ ] **Step 2: Full browser pass — desktop (1920x1080)**

1. `resize_window` `{preset: "desktop"}`
2. Reload `http://127.0.0.1:3002/`
3. `read_console_messages` `onlyErrors: true` → expect `[]`
4. `read_network_requests` → confirm no 404s for any `assets/` path
5. `computer` `{action: "screenshot"}` → save as
   `projects/bleuuboard-v2/verification/desktop-screenshot.png`

- [ ] **Step 3: Full browser pass — mobile (390x844)**

1. `resize_window` `{preset: "mobile"}`
2. Reload
3. `read_console_messages` `onlyErrors: true` → expect `[]`
4. `read_network_requests` → confirm mobile tier did NOT fetch
   `concrete_floor_02_diff.jpg` or `studio_small_08_2k.hdr` (proves the
   device-tier gating in Task 4 actually skips heavy assets, not just
   claims to)
5. `computer` `{action: "screenshot"}` → save as
   `projects/bleuuboard-v2/verification/mobile-screenshot.png`

- [ ] **Step 4: Write the verification record**

`projects/bleuuboard-v2/VERIFICATION.md`:

```markdown
# BleuuBoard v2 — Engine Sub-project Verification

Date: 2026-08-15
Scope: Task 1–5 of `docs/superpowers/plans/2026-08-15-bleuuboard-v2-3d-engine.md`

## Results

- [ ] Desktop (1920x1080): 0 console errors, PBR environment + textured
      ground + directional lighting visible, screenshot captured
- [ ] Mobile (390x844): 0 console errors, lightweight tier confirmed via
      network log (no 2k HDRI / PBR texture fetches), screenshot captured
- [ ] Original `whiteboard-4d/` and its Vercel deployments: unmodified
      (confirm via `git status` showing no changes outside `projects/bleuuboard-v2/`)

## Explicitly out of scope (per spec)

- Drawing tools / raycasting-based interaction (strokes, text, image
  placement) — not ported in this plan
- MUI/React UI, Keycloak SSO — separate sub-projects
```

- [ ] **Step 5: Confirm original app is untouched**

Run: `cd "C:/Users/navka/navakanth001" && git status --porcelain whiteboard-4d/`
Expected: empty output (no changes).

- [ ] **Step 6: Commit**

```bash
git add projects/bleuuboard-v2/verification/ projects/bleuuboard-v2/VERIFICATION.md
git commit -m "docs(bleuuboard-v2): final verification pass for engine sub-project"
```

---

## Not in this plan (deferred to follow-up plans)

- Porting the original's drawing/stroke/text/image tools onto the Babylon
  scene (separate plan — raycasting-based interaction is a distinct, larger
  surface area than the environment/lighting work here)
- MUI/React UI migration (sub-project 2)
- Keycloak SSO with email + global phone (sub-project 3)
- Any asset source beyond Poly Haven
