// Shared engine for the "S³ worlds": the closed 4D filament ("the nine") on S³ ⊂ ℝ⁴,
// 4D rotations, stereographic projection (x,y,z)/(1−w), glow shaders and a control panel.
// Each world page imports createWorld() and adds its own physics layer on top.
import * as THREE from 'three';
import { OrbitControls } from 'three/addons/controls/OrbitControls.js';
import { EffectComposer } from 'three/addons/postprocessing/EffectComposer.js';
import { RenderPass } from 'three/addons/postprocessing/RenderPass.js';
import { UnrealBloomPass } from 'three/addons/postprocessing/UnrealBloomPass.js';
import { OutputPass } from 'three/addons/postprocessing/OutputPass.js';

export { THREE };
export const TAU = Math.PI * 2, QUARTER = Math.PI / 4, DEG = Math.PI / 180;

// The "9" glyph preset from index.html (copied, not shared, so index.html stays untouched).
export const NINE = { a0: 0.2, n: 1, k: 44, amax: 0.72, tw: 0.09, eps: 0.005, tang: 0, curl: -78, pin: 1 };

// ---------- geometry on S³ ----------
export function buildNine(P = NINE, N = 9000) {
  const x = new Float32Array(N), y = new Float32Array(N), z = new Float32Array(N), w = new Float32Array(N);
  const n = Math.round(P.n), k = Math.round(P.k), sc = 0.75;
  const aMax = P.amax * Math.PI / 2, a0 = P.a0 * QUARTER, curl = P.curl * DEG;
  const env = (d, wd) => { const u = d / wd; return Math.exp(-u * u); };
  const B = new Float32Array(N), D = new Float32Array(N), G = new Float64Array(N + 1);
  for (let i = 0; i < N; i++) {
    let d = Math.abs(i / N - sc); d = Math.min(d, 1 - d);
    D[i] = d; B[i] = env(d, P.tw);
    G[i + 1] = G[i] + (1 - (1 - P.eps) * env(d, P.tw * 1.9));
  }
  const Gtot = G[N], ic = Math.round(sc * N);
  const W2 = Math.min(3.5 * P.tw, 0.24), W1 = Math.min(2 * P.tw, 0.75 * W2);
  for (let i = 0; i < N; i++) {
    const d = D[i];
    const pin = P.pin * (d <= W1 ? 1 : d >= W2 ? 0 : Math.cos(Math.PI / 2 * (d - W1) / (W2 - W1)) ** 2);
    const dG = (G[i] - G[ic]) / Gtot;
    const a = a0 + (Math.max(aMax, a0) - a0) * B[i];
    const th = P.tang * DEG + TAU * n * dG * (1 - pin) + curl * B[i];
    const ph = Math.PI / 2 + TAU * k * dG * (1 - pin);
    const ca = Math.cos(a), sa = Math.sin(a);
    x[i] = ca * Math.cos(th); y[i] = ca * Math.sin(th); z[i] = sa * Math.cos(ph); w[i] = sa * Math.sin(ph);
  }
  return { x, y, z, w, N };
}

// Hopf fibre over the Bloch-sphere point (polar η, azimuth ξ): ψ = (cos(η/2)e^{it}, sin(η/2)e^{i(t+ξ)}).
export function hopfFiber(eta, xi, m = 160) {
  const out = new Float32Array(4 * m), a = Math.cos(eta / 2), b = Math.sin(eta / 2);
  for (let j = 0; j < m; j++) {
    const t = TAU * j / m;
    out.set([a * Math.cos(t), a * Math.sin(t), b * Math.cos(t + xi), b * Math.sin(t + xi)], 4 * j);
  }
  return out;
}

// Hopf map S³ → S² (Bloch sphere) with ψ1 = x+iy, ψ2 = z+iw.
export function bloch(x, y, z, w, out, o = 0) {
  out[o] = 2 * (x * z + y * w); out[o + 1] = 2 * (y * z - x * w); out[o + 2] = x * x + y * y - z * z - w * w;
}

// ---------- 4D rotation + stereographic projection ----------
export function makeRot(ang) {
  const R = {};
  for (const p of ['xy', 'xw', 'yw', 'zw']) R[p] = [Math.cos(ang[p] || 0), Math.sin(ang[p] || 0)];
  return R;
}
export function rotate4(x, y, z, w, R, out) {
  let t, c, s;
  [c, s] = R.xy; t = x * c - y * s; y = x * s + y * c; x = t;
  [c, s] = R.xw; t = x * c - w * s; w = x * s + w * c; x = t;
  [c, s] = R.yw; t = y * c - w * s; w = y * s + w * c; y = t;
  [c, s] = R.zw; t = z * c - w * s; w = z * s + w * c; z = t;
  out[0] = x; out[1] = y; out[2] = z; out[3] = w;
  return out;
}
const T4 = [0, 0, 0, 0];
export function stereo(x, y, z, w, R, out, o) {
  rotate4(x, y, z, w, R, T4);
  const d = Math.max(1 - T4[3], 1e-5);
  out[o] = T4[0] / d; out[o + 1] = T4[1] / d; out[o + 2] = T4[2] / d;
  return T4[3];
}

// ---------- shaders ----------
const VERT = /* glsl */`
  attribute float aW;
  uniform float uClip, uSize, uPix;
  varying float vW, vFade;
  void main() {
    vec4 mv = modelViewMatrix * vec4(position, 1.0);
    gl_Position = projectionMatrix * mv;
    vFade = 1.0 - smoothstep(uClip * 0.45, uClip, length(position));
    vW = aW;
    gl_PointSize = uSize * uPix / max(-mv.z, 0.1);
  }`;
const RAMP = /* glsl */`
  uniform vec3 uC0, uC1, uC2, uC3;
  uniform float uAlpha, uHot;
  varying float vW, vFade;
  vec3 ramp(float w) {
    float t = clamp(w * 0.5 + 0.5, 0.0, 1.0);
    if (t < 0.5)  return mix(uC0, uC1, t / 0.5);
    if (t < 0.86) return mix(uC1, uC2, (t - 0.5) / 0.36);
    return mix(uC2, uC3, (t - 0.86) / 0.14);
  }`;
const FRAG_LINE = RAMP + `
  void main() { gl_FragColor = vec4(ramp(vW) * (0.55 + uHot * max(vW, 0.0)), uAlpha * vFade); }`;
const FRAG_PTS = RAMP + `
  void main() {
    float r = length(gl_PointCoord - 0.5); if (r > 0.5) discard;
    float g = exp(-r * r * 18.0);
    gl_FragColor = vec4(ramp(vW) * g * (0.6 + uHot * max(vW, 0.0)), uAlpha * vFade * g);
  }`;
const hex = c => new THREE.Color(c);

// ---------- world shell ----------
const CSS = `
  :root { --fg:#d9e6ff; --dim:#8090b0; --acc:#5fe3ff; --hot:#ffa24a; }
  html,body { margin:0; height:100%; color:var(--fg); overflow:hidden;
    font:13px/1.4 ui-sans-serif, system-ui, "Segoe UI", sans-serif; }
  canvas { display:block; }
  .box { position:fixed; background:rgba(8,12,24,.74); backdrop-filter:blur(8px);
    border:1px solid rgba(255,255,255,.1); border-radius:10px; }
  #panel { top:12px; left:12px; width:280px; max-height:calc(100% - 24px); overflow:auto; padding:12px 14px; }
  #panel h1 { font-size:14px; margin:0 0 2px; letter-spacing:.05em; }
  #panel .sub { color:var(--dim); font-size:11px; margin-bottom:6px; }
  fieldset { border:none; border-top:1px solid rgba(255,255,255,.08); margin:8px 0 0; padding:8px 0 0; }
  legend { color:var(--acc); font-size:11px; text-transform:uppercase; letter-spacing:.08em; padding:0; }
  label { display:grid; grid-template-columns:1fr 52px; align-items:center; gap:2px 8px; margin:5px 0; }
  label span.v { text-align:right; color:var(--hot); font-variant-numeric:tabular-nums; }
  label input[type=range] { grid-column:1 / span 2; width:100%; accent-color:var(--acc); }
  .row { display:flex; gap:6px; flex-wrap:wrap; align-items:center; margin-top:6px; }
  button, a.btn { background:rgba(255,255,255,.07); color:var(--fg); border:1px solid rgba(255,255,255,.2);
    border-radius:6px; padding:4px 9px; cursor:pointer; font:inherit; text-decoration:none; }
  button:hover, a.btn:hover { background:rgba(255,255,255,.16); }
  button.on { border-color:var(--acc); color:var(--acc); }
  .chk { display:flex; gap:6px; align-items:center; margin:5px 0; }
  #caption { right:12px; top:12px; width:340px; max-height:55%; overflow:auto; padding:10px 14px;
    font-size:12px; line-height:1.55; color:#b8c4dc; }
  #caption h2 { font-size:12px; margin:0 0 4px; color:var(--acc); text-transform:uppercase; letter-spacing:.08em; }
  #caption b { color:var(--fg); font-weight:600; }
  #caption .honest { margin-top:6px; padding-top:6px; border-top:1px solid rgba(255,255,255,.1); color:var(--dim); }
  #hud { right:12px; bottom:12px; padding:8px 12px; font:12px/1.5 ui-monospace, Consolas, monospace;
    color:var(--dim); min-width:260px; }
  #hud b { color:var(--fg); font-weight:500; }
`;

function slider(id, label, min, max, step, value) {
  return `<label>${label} <span class="v" id="v_${id}"></span>` +
    `<input id="${id}" type="range" min="${min}" max="${max}" step="${step}" value="${value}"></label>`;
}

/**
 * cfg: { title, sub, accent, bg, palette:[c0,c1,c2,c3], hot, nine:{...}, camera:{pos,target,fov},
 *        bloom, clip, controls:[{id,label,min,max,step,value}], toggles:[{id,label,checked}],
 *        spinPlanes, spin:{plane,speed}, caption (HTML), setup(ctx), update(ctx), hud(ctx) → HTML }
 */
export function createWorld(cfg) {
  const style = document.createElement('style');
  style.textContent = CSS + (cfg.accent ? `:root{--acc:${cfg.accent}}` : '');
  document.head.appendChild(style);
  document.body.style.background = cfg.bg || '#03040a';

  const planes = cfg.spinPlanes || ['zw', 'xw', 'yw'];
  const spinCfg = cfg.spin || { plane: planes[0], speed: 0 };
  const controls = cfg.controls || [];
  const toggles = [{ id: 'pts', label: 'plasma particles on the filament', checked: true }, ...(cfg.toggles || [])];
  const planeLabel = p => p === 'prec' ? 'Larmor (xy+zw)' : p;

  const panel = document.createElement('div');
  panel.id = 'panel'; panel.className = 'box';
  panel.innerHTML = `
    <button id="panelToggle" style="float:right;margin:-2px -4px 0 6px" title="hide controls">⟨</button>
    <div id="panelBody">
    <h1>${cfg.title}</h1><div class="sub">${cfg.sub}</div>
    <div class="row"><a class="btn" href="worlds.html">← all worlds</a><a class="btn" href="index.html">original nine</a></div>
    ${controls.length ? `<fieldset><legend>${cfg.controlsLegend || 'This world'}</legend>${
      controls.map(c => slider(c.id, c.label, c.min, c.max, c.step, c.value)).join('')}</fieldset>` : ''}
    <fieldset><legend>4D rotation</legend>
      ${slider('rxw', 'xw angle', -180, 180, 0.5, 0)}${slider('ryw', 'yw angle', -180, 180, 0.5, 0)}
      ${slider('rzw', 'zw angle', -180, 180, 0.5, 0)}
      ${slider('spd', 'auto-spin speed (°/s)', 0, 90, 1, spinCfg.speed)}
      <div class="row">spin: ${planes.map(p => `<button data-plane="${p}">${planeLabel(p)}</button>`).join('')}</div>
    </fieldset>
    <fieldset><legend>Render</legend>
      ${slider('bloom', 'bloom', 0, 3, 0.05, cfg.bloom ?? 0.9)}${slider('clip', 'clip radius', 6, 80, 1, cfg.clip ?? 28)}
      ${toggles.map(t => `<div class="chk"><input id="${t.id}" type="checkbox" ${t.checked ? 'checked' : ''}><span>${t.label}</span></div>`).join('')}
      <div class="row"><button id="resetView">reset view</button><span style="color:var(--dim)">space = pause</span></div>
    </fieldset></div>`;
  document.body.appendChild(panel);
  let panelOpen = true;
  panel.querySelector('#panelToggle').onclick = () => {
    panelOpen = !panelOpen;
    panel.querySelector('#panelBody').style.display = panelOpen ? '' : 'none';
    panel.style.width = panelOpen ? '' : 'auto';
    panel.querySelector('#panelToggle').textContent = panelOpen ? '⟨' : '☰ controls';
  };
  const cap = document.createElement('div'); cap.id = 'caption'; cap.className = 'box';
  cap.innerHTML = `<button id="capToggle" style="float:right;margin:-2px -4px 0 6px">–</button><div id="capBody">${cfg.caption || ''}</div>`;
  const setCap = open => { cap.querySelector('#capBody').style.display = open ? '' : 'none';
    cap.style.width = open ? '' : 'auto'; cap.querySelector('#capToggle').textContent = open ? '–' : 'ⓘ why S³ here?'; };
  let capOpen = innerWidth > 1100;
  setCap(capOpen);
  cap.querySelector('#capToggle').onclick = () => setCap(capOpen = !capOpen);
  const hudEl = document.createElement('div'); hudEl.id = 'hud'; hudEl.className = 'box';
  document.body.append(cap, hudEl);

  const $ = id => document.getElementById(id);
  const U = {}, T = {};
  const sliderIds = [...controls.map(c => c.id), 'rxw', 'ryw', 'rzw', 'spd', 'bloom', 'clip'];
  const read = () => {
    for (const id of sliderIds) { U[id] = parseFloat($(id).value); $('v_' + id).textContent = +U[id].toFixed(3); }
    for (const t of toggles) T[t.id] = $(t.id).checked;
  };
  read();
  sliderIds.forEach(id => $(id).addEventListener('input', read));
  toggles.forEach(t => $(t.id).addEventListener('change', read));
  let spinPlane = spinCfg.plane;
  const markPlane = () => panel.querySelectorAll('[data-plane]').forEach(b => b.classList.toggle('on', b.dataset.plane === spinPlane));
  panel.querySelectorAll('[data-plane]').forEach(b => b.onclick = () => { spinPlane = b.dataset.plane; markPlane(); });
  markPlane();

  // --- three.js ---
  const renderer = new THREE.WebGLRenderer({ antialias: true });
  renderer.setPixelRatio(Math.min(devicePixelRatio, 2));
  renderer.setSize(innerWidth, innerHeight);
  document.body.prepend(renderer.domElement);
  const scene = new THREE.Scene();
  const cam = cfg.camera || {};
  const camera = new THREE.PerspectiveCamera(cam.fov || 45, innerWidth / innerHeight, 0.01, 5000);
  const orbit = new OrbitControls(camera, renderer.domElement);
  orbit.enableDamping = true;
  const homeView = () => {
    camera.position.set(...(cam.pos || [-1.1, -1.2, 8.5]));
    orbit.target.set(...(cam.target || [-1.1, -1.2, 0]));
  };
  homeView();
  $('resetView').onclick = homeView;

  const mats = [];
  const pix = () => renderer.getPixelRatio() * innerHeight / 900;
  const pal = (cfg.palette || ['#5220ff', '#1ae0ff', '#ff851f', '#fff5e0']).map(hex);
  function makeMat(kind, { alpha = 0.8, size = 20, palette, hot = cfg.hot ?? 0.9, additive = true } = {}) {
    const p = palette ? palette.map(hex) : pal;
    const m = new THREE.ShaderMaterial({
      vertexShader: VERT, fragmentShader: kind === 'points' ? FRAG_PTS : FRAG_LINE,
      transparent: true, depthWrite: false, blending: additive ? THREE.AdditiveBlending : THREE.NormalBlending,
      uniforms: {
        uClip: { value: U.clip }, uSize: { value: size }, uPix: { value: pix() }, uAlpha: { value: alpha },
        uHot: { value: hot }, uC0: { value: p[0] }, uC1: { value: p[1] }, uC2: { value: p[2] }, uC3: { value: p[3] },
      },
    });
    mats.push(m);
    return m;
  }

  // Generic projected objects: closed loops (Curves4D) and point clouds (Points4D).
  class Curves4D {
    constructor(loops, opts = {}) {
      let V = 0; for (const L of loops) V += (L.length / 4) * 2;
      this.src = new Float32Array(V * 4); let v = 0;
      for (const L of loops) {
        const m = L.length / 4;
        for (let j = 0; j < m; j++) {
          const j2 = (j + 1) % m;
          this.src.set(L.subarray(4 * j, 4 * j + 4), 4 * v++);
          this.src.set(L.subarray(4 * j2, 4 * j2 + 4), 4 * v++);
        }
      }
      this.V = V; this.pos = new Float32Array(V * 3); this.w = new Float32Array(V);
      const g = new THREE.BufferGeometry();
      g.setAttribute('position', new THREE.BufferAttribute(this.pos, 3));
      g.setAttribute('aW', new THREE.BufferAttribute(this.w, 1));
      this.obj = new THREE.LineSegments(g, opts.material || makeMat('line', opts));
      this.obj.frustumCulled = false;
    }
    update(R) {
      const s = this.src;
      for (let v = 0; v < this.V; v++) this.w[v] = stereo(s[4 * v], s[4 * v + 1], s[4 * v + 2], s[4 * v + 3], R, this.pos, 3 * v);
      this.obj.geometry.attributes.position.needsUpdate = this.obj.geometry.attributes.aW.needsUpdate = true;
    }
  }
  class Points4D {
    constructor(src /* Float32Array 4M */, opts = {}) {
      this.src = src; this.M = src.length / 4;
      this.pos = new Float32Array(this.M * 3); this.w = new Float32Array(this.M);
      const g = new THREE.BufferGeometry();
      g.setAttribute('position', new THREE.BufferAttribute(this.pos, 3));
      g.setAttribute('aW', new THREE.BufferAttribute(this.w, 1));
      this.obj = new THREE.Points(g, opts.material || makeMat('points', opts));
      this.obj.frustumCulled = false;
    }
    update(R) {
      const s = this.src;
      for (let i = 0; i < this.M; i++) this.w[i] = stereo(s[4 * i], s[4 * i + 1], s[4 * i + 2], s[4 * i + 3], R, this.pos, 3 * i);
      this.obj.geometry.attributes.position.needsUpdate = this.obj.geometry.attributes.aW.needsUpdate = true;
    }
  }

  // The nine itself.
  const nineP = { ...NINE, ...(cfg.nine || {}) };
  const nine4 = buildNine(nineP);
  const ninePos = new Float32Array(nine4.N * 3), nineW = new Float32Array(nine4.N);
  const nineGeo = new THREE.BufferGeometry();
  nineGeo.setAttribute('position', new THREE.BufferAttribute(ninePos, 3));
  nineGeo.setAttribute('aW', new THREE.BufferAttribute(nineW, 1));
  const nineLine = new THREE.LineLoop(nineGeo, makeMat('line', { alpha: 0.85 }));
  const ninePts = new THREE.Points(nineGeo, makeMat('points', { alpha: 0.5, size: 20 }));
  nineLine.frustumCulled = ninePts.frustumCulled = false;
  scene.add(nineLine, ninePts);

  const composer = new EffectComposer(renderer);
  composer.addPass(new RenderPass(scene, camera));
  const bloom = new UnrealBloomPass(new THREE.Vector2(innerWidth, innerHeight), U.bloom, 0.55, 0.0);
  composer.addPass(bloom);
  composer.addPass(new OutputPass());

  const tracked = [];
  const ctx = {
    THREE, scene, camera, renderer, U, T, makeMat, Curves4D, Points4D, nine4, ninePos, nineW, nineLine,
    t: 0, dt: 0, spin: 0, R: null, ang: null,
    track(o) { tracked.push(o); return o; },
  };
  cfg.setup?.(ctx);

  let paused = false, last = performance.now();
  addEventListener('keydown', e => { if (e.code === 'Space') { paused = !paused; e.preventDefault(); } });
  addEventListener('resize', () => {
    camera.aspect = innerWidth / innerHeight; camera.updateProjectionMatrix();
    renderer.setSize(innerWidth, innerHeight); composer.setSize(innerWidth, innerHeight);
    for (const m of mats) m.uniforms.uPix.value = pix();
  });

  function frame(now) {
    const dt = Math.min((now - last) / 1000, 0.1); last = now;
    if (!paused) { ctx.t += dt; ctx.spin += U.spd * dt; }
    ctx.dt = paused ? 0 : dt;
    const ang = { xy: 0, xw: U.rxw * DEG, yw: U.ryw * DEG, zw: U.rzw * DEG };
    const s = ctx.spin * DEG;
    if (spinPlane === 'prec') { ang.xy -= s / 2; ang.zw += s / 2; } else ang[spinPlane] += s;
    ctx.ang = ang; ctx.spinPlane = spinPlane;
    const R = ctx.R = makeRot(ang);

    let minGap = 2;
    for (let i = 0; i < nine4.N; i++) {
      const w = stereo(nine4.x[i], nine4.y[i], nine4.z[i], nine4.w[i], R, ninePos, 3 * i);
      nineW[i] = w; if (1 - w < minGap) minGap = 1 - w;
    }
    nineGeo.attributes.position.needsUpdate = nineGeo.attributes.aW.needsUpdate = true;
    ninePts.visible = T.pts;
    for (const o of tracked) if (o.obj.visible !== false) o.update(R);
    for (const m of mats) m.uniforms.uClip.value = U.clip;
    bloom.strength = U.bloom;
    cfg.update?.(ctx);

    hudEl.innerHTML = `closest approach to pole 1−w = <b>${minGap.toExponential(2)}</b><br>` +
      `spin (${planeLabel(spinPlane)}) = <b>${ctx.spin.toFixed(1)}°</b>${paused ? ' (paused)' : ''}` +
      (cfg.hud ? '<br>' + cfg.hud(ctx) : '');
    orbit.update();
    composer.render();
    requestAnimationFrame(frame);
  }
  requestAnimationFrame(frame);
  window.__world = ctx;
  return ctx;
}
