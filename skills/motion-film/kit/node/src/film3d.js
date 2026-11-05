// film3d — Three.js layers for HyperFrames films, rendered deterministically from timeline time.
// Every layer is a pure function of t: HyperFrames seeks frame by frame (hf-seek), so nothing may depend on wall-clock
// time, requestAnimationFrame or the previous frame.
//
// Layers:
//   FILM3D.particles(canvasId, opts)  dust / snow / sparks / crystals (optional sprite texture)
//   FILM3D.map(canvasId, opts)        extruded country with hand-drawn boiling coastline, routes from a home point,
//                                     pins, labels, descent / orbit / push-in camera and a screen-space follower element
// Geography comes from window.FILM_GEO (written by geo.mjs into assets/geo.js).
import * as THREE from 'three';
import { EffectComposer } from 'three/examples/jsm/postprocessing/EffectComposer.js';
import { RenderPass } from 'three/examples/jsm/postprocessing/RenderPass.js';
import { UnrealBloomPass } from 'three/examples/jsm/postprocessing/UnrealBloomPass.js';
import { OutputPass } from 'three/examples/jsm/postprocessing/OutputPass.js';
import { Line2 } from 'three/examples/jsm/lines/Line2.js';
import { LineMaterial } from 'three/examples/jsm/lines/LineMaterial.js';
import { LineGeometry } from 'three/examples/jsm/lines/LineGeometry.js';

const W = 1920, H = 1080;
const DEF = { land: '#3A8FA3', side: '#173F4A', neighbour: '#2C6673', ground: '#163E47', bg: ['#2E7F91', '#123640', '#08171C'],
  fog: '#123640', route: '#E8743B', routeStart: '#FFE3CC', coast: '#FAF6F0', pin: '#E8743B', home: '#FFFFFF' };
function mulberry32(a) { return function () { a |= 0; a = a + 0x6D2B79F5 | 0; let t = Math.imul(a ^ a >>> 15, 1 | a); t = t + Math.imul(t ^ t >>> 7, 61 | t) ^ t; return ((t ^ t >>> 14) >>> 0) / 4294967296; }; }
const clamp = (v, a = 0, b = 1) => Math.min(b, Math.max(a, v));
const lerp = (a, b, t) => a + (b - a) * t;
const ease = {
  inOut2: (t) => t < .5 ? 2 * t * t : 1 - Math.pow(-2 * t + 2, 2) / 2,
  inOut3: (t) => t < .5 ? 4 * t * t * t : 1 - Math.pow(-2 * t + 2, 3) / 2,
  out3: (t) => 1 - Math.pow(1 - t, 3),
  in3: (t) => t * t * t,
  back: (t) => { const c1 = 1.9, c3 = c1 + 1; return 1 + c3 * Math.pow(t - 1, 3) + c1 * Math.pow(t - 1, 2); },
};
const seg = (t, a, b) => clamp((t - a) / (b - a));

const layers = [];
function renderAll(t) { for (const L of layers) { if (t >= L.start - 1e-4 && t < L.end + 1e-4) L.render(t); } }
function ready(key, promise) { window.__hf = window.__hf || {}; window.__hf.buildReady = window.__hf.buildReady || {}; window.__hf.buildReady[key] = promise; }

// ------------------------------------------------------------------ particles
// opts: start, end, count, size, color, seed, drift:[x,y,z], focus, fadeIn, fadeOut, additive, shape (0 soft dot, 1 star crystal),
//       beam (light shaft), sprite (image url, luminance = alpha), timeOffset, alphaAt(t)
function particles(canvasId, o) {
  const canvas = document.getElementById(canvasId);
  const renderer = new THREE.WebGLRenderer({ canvas, alpha: true, antialias: false, preserveDrawingBuffer: true, premultipliedAlpha: true });
  renderer.setPixelRatio(1); renderer.setSize(W, H, false); renderer.setClearColor(0x000000, 0);
  const scene = new THREE.Scene();
  const camera = new THREE.PerspectiveCamera(40, W / H, 0.1, 100); camera.position.set(0, 0, 12);
  const N = o.count || 900, rnd = mulberry32(o.seed || 7);
  const pos = new Float32Array(N * 3), sd = new Float32Array(N * 4);
  for (let i = 0; i < N; i++) {
    pos[i * 3] = (rnd() - .5) * 26; pos[i * 3 + 1] = (rnd() - .5) * 15; pos[i * 3 + 2] = (rnd() - .5) * 14;
    for (let k = 0; k < 4; k++) sd[i * 4 + k] = rnd();
  }
  const g = new THREE.BufferGeometry();
  g.setAttribute('position', new THREE.BufferAttribute(pos, 3));
  g.setAttribute('aSeed', new THREE.BufferAttribute(sd, 4));
  const mat = new THREE.ShaderMaterial({
    transparent: true, depthWrite: false, blending: o.additive ? THREE.AdditiveBlending : THREE.NormalBlending,
    uniforms: { uTime: { value: 0 }, uColor: { value: new THREE.Color(o.color || '#FFF6E8') }, uSize: { value: o.size || 26 }, uFocus: { value: o.focus ?? 2.0 },
      uDrift: { value: new THREE.Vector3(...(o.drift || [0.18, 0.10, 0])) }, uAlpha: { value: 1 }, uShape: { value: o.shape || 0 }, uBeam: { value: o.beam ? 1 : 0 },
      uTex: { value: null }, uUseTex: { value: 0 } },
    vertexShader: /* glsl */`
      attribute vec4 aSeed; uniform float uTime, uSize, uFocus; uniform vec3 uDrift; uniform float uBeam;
      varying float vA; varying float vBlur; varying float vRot;
      void main(){
        vec3 p = position; float t = uTime;
        p += uDrift * t * (0.6 + aSeed.x);
        p.x += sin(t * (0.35 + aSeed.y * 0.5) + aSeed.z * 6.283) * (0.25 + aSeed.w * 0.35);
        p.y += cos(t * (0.28 + aSeed.x * 0.4) + aSeed.w * 6.283) * (0.18 + aSeed.y * 0.25);
        p.x = mod(p.x + 13.0, 26.0) - 13.0; p.y = mod(p.y + 7.5, 15.0) - 7.5;
        vec4 mv = modelViewMatrix * vec4(p, 1.0);
        float dist = abs(-mv.z - (12.0 - uFocus));
        vBlur = clamp(dist / 7.0, 0.0, 1.0);
        float s = uSize * (0.35 + aSeed.y * 0.9) * (1.0 + vBlur * 2.2);
        gl_PointSize = s * (10.0 / -mv.z);
        float beam = 1.0;
        if (uBeam > 0.5) { vec2 sp = mv.xy / -mv.z; float d = abs(sp.y + sp.x * 0.55 - 0.15); beam = 0.35 + 1.1 * smoothstep(0.55, 0.0, d); }
        vA = (0.25 + aSeed.z * 0.75) * (1.0 - vBlur * 0.65) * beam;
        vRot = aSeed.w * 6.283 + t * (aSeed.x - 0.5) * 0.8;
        gl_Position = projectionMatrix * mv;
      }`,
    fragmentShader: /* glsl */`
      uniform vec3 uColor; uniform float uAlpha, uShape, uUseTex; uniform sampler2D uTex; varying float vA; varying float vBlur; varying float vRot;
      void main(){
        vec2 c = gl_PointCoord - 0.5; float r = length(c); float a;
        if (uUseTex > 0.5) {
          float cs = cos(vRot), sn = sin(vRot);
          vec2 q = vec2(cs * c.x - sn * c.y, sn * c.x + cs * c.y) + 0.5;
          vec4 tx = texture2D(uTex, q);
          float lum = max(tx.r, max(tx.g, tx.b));
          gl_FragColor = vec4(mix(uColor, tx.rgb, 0.6), lum * vA * uAlpha * (1.0 - vBlur * 0.45));
          #include <colorspace_fragment>
          return;
        }
        if (uShape < 0.5) { a = smoothstep(0.5, 0.5 - (0.12 + vBlur * 0.38), r); }
        else {
          float ang = atan(c.y, c.x) + vRot;
          float arms = pow(abs(cos(ang * 3.0)), 18.0) * smoothstep(0.5, 0.05, r);
          float core = smoothstep(0.16, 0.0, r);
          a = max(arms * (1.0 - vBlur), core) + smoothstep(0.5, 0.2, r) * vBlur * 0.5;
        }
        gl_FragColor = vec4(uColor, a * vA * uAlpha);
        #include <colorspace_fragment>
      }`,
  });
  scene.add(new THREE.Points(g, mat));
  if (o.sprite) ready('sprite_' + canvasId, new Promise((res) => {
    new THREE.TextureLoader().load(o.sprite, (tx) => { tx.colorSpace = THREE.SRGBColorSpace; mat.uniforms.uTex.value = tx; mat.uniforms.uUseTex.value = 1; res(); }, undefined, () => res());
  }));
  const L = {
    start: o.start, end: o.end,
    render(t) {
      const u = t - o.start;
      mat.uniforms.uTime.value = u + (o.timeOffset || 0);
      let a = 1;
      if (o.fadeIn) a *= ease.inOut2(seg(u, 0, o.fadeIn));
      if (o.fadeOut) a *= 1 - ease.inOut2(seg(t, o.end - o.fadeOut, o.end));
      if (o.alphaAt) a *= o.alphaAt(t);
      mat.uniforms.uAlpha.value = a;
      camera.position.x = Math.sin(u * 0.12) * 0.4; camera.lookAt(0, 0, 0);
      renderer.render(scene, camera);
    },
  };
  layers.push(L); return L;
}

// ------------------------------------------------------------------ 3D map
// opts: start, end, colors (see DEF), home: {ll:[lon,lat]}, cities: [{ll:[lon,lat], at (s after start), label (element id)}],
//       homeNote (element id that follows the home point), follow: {el, t0, t1} (element pinned to home on screen, e.g. a burst),
//       highStart (descend from straight above), pull0/pull1 (descent window, s), viewShift (px, frees screen space for text),
//       pushIn (seconds of push into home at the end, default 1), scale (world units per degree, default auto)
function map(canvasId, o) {
  const GEO = window.FILM_GEO;
  if (!GEO) throw new Error('FILM3D.map: window.FILM_GEO missing — run kit/node geo.mjs and load assets/geo.js');
  const col = { ...DEF, ...(o.colors || {}) };
  const [LON0, LAT0] = GEO.center; const COS0 = Math.cos(LAT0 * Math.PI / 180);
  const S = o.scale || (9.5 / Math.max(GEO.span[0] * COS0, GEO.span[1]));
  const PX = (lon) => (lon - LON0) * COS0 * S, PZ = (lat) => -(lat - LAT0) * S;
  const DEPTH = 0.32;
  const shapeFromRings = (rings) => {
    const sh = new THREE.Shape(rings[0].map(([lo, la]) => new THREE.Vector2(PX(lo), -PZ(la))));
    for (let i = 1; i < rings.length; i++) sh.holes.push(new THREE.Path(rings[i].map(([lo, la]) => new THREE.Vector2(PX(lo), -PZ(la)))));
    return sh;
  };
  const canvas = document.getElementById(canvasId);
  const renderer = new THREE.WebGLRenderer({ canvas, antialias: true, preserveDrawingBuffer: true });
  renderer.setPixelRatio(1); renderer.setSize(W, H, false);
  renderer.shadowMap.enabled = true; renderer.shadowMap.type = THREE.PCFSoftShadowMap;
  const scene = new THREE.Scene();
  const bg = document.createElement('canvas'); bg.width = 1024; bg.height = 576;
  { const x = bg.getContext('2d'); const gr = x.createRadialGradient(560, 250, 40, 512, 300, 700); gr.addColorStop(0, col.bg[0]); gr.addColorStop(0.45, col.bg[1]); gr.addColorStop(1, col.bg[2]); x.fillStyle = gr; x.fillRect(0, 0, 1024, 576); }
  const bgt = new THREE.CanvasTexture(bg); bgt.colorSpace = THREE.SRGBColorSpace; scene.background = bgt;
  scene.fog = new THREE.Fog(col.fog, 16, 34);
  const camera = new THREE.PerspectiveCamera(32, W / H, 0.1, 200);
  const ground = new THREE.Mesh(new THREE.PlaneGeometry(60, 60), new THREE.MeshStandardMaterial({ color: col.ground, roughness: 1 }));
  ground.rotation.x = -Math.PI / 2; ground.receiveShadow = true; scene.add(ground);

  const nMat = new THREE.MeshStandardMaterial({ color: col.neighbour, roughness: 0.9 });
  for (const poly of GEO.neighbours || []) {
    const geo = new THREE.ExtrudeGeometry(shapeFromRings(poly), { depth: 0.03, bevelEnabled: false }); geo.rotateX(-Math.PI / 2);
    const m = new THREE.Mesh(geo, nMat); m.receiveShadow = true; scene.add(m);
  }
  const topMat = new THREE.MeshStandardMaterial({ color: col.land, roughness: 0.55 });
  const sideMat = new THREE.MeshStandardMaterial({ color: col.side, roughness: 0.8 });
  for (const poly of GEO.main) {
    const g = new THREE.ExtrudeGeometry(shapeFromRings(poly), { depth: DEPTH, bevelEnabled: true, bevelThickness: 0.04, bevelSize: 0.035, bevelSegments: 2, curveSegments: 4 });
    g.rotateX(-Math.PI / 2); const m = new THREE.Mesh(g, [topMat, sideMat]); m.castShadow = true; m.receiveShadow = true; scene.add(m);
  }
  for (const poly of GEO.insets || []) {   // enclaves sit slightly lower, e.g. a country inside the main one
    const g = new THREE.ExtrudeGeometry(shapeFromRings(poly), { depth: DEPTH * 0.82, bevelEnabled: true, bevelThickness: 0.03, bevelSize: 0.02, bevelSegments: 1 });
    g.rotateX(-Math.PI / 2); const m = new THREE.Mesh(g, [new THREE.MeshStandardMaterial({ color: new THREE.Color(col.land).multiplyScalar(0.85), roughness: 0.6 }), sideMat]); m.castShadow = true; scene.add(m);
  }
  // hand-drawn coastline on the largest main polygon, boiling at 10 fps
  const ring = GEO.main.map(p => p[0]).sort((a, b) => b.length - a.length)[0];
  const basePts = ring.map(([lo, la]) => [PX(lo), DEPTH + 0.045, PZ(la)]);
  const lineGeo = new LineGeometry();
  const lineMat = new LineMaterial({ color: col.coast, linewidth: 3.2, transparent: true, opacity: 0.95, resolution: new THREE.Vector2(W, H) });
  const coast = new Line2(lineGeo, lineMat); scene.add(coast);
  let lastBoil = -1;
  const boilCoast = (step) => {
    if (step === lastBoil) return; lastBoil = step;
    const r = mulberry32(1000 + step); const arr = [];
    for (const [x, y, z] of basePts) arr.push(x + (r() - .5) * 0.022, y, z + (r() - .5) * 0.022);
    lineGeo.setPositions(arr); coast.computeLineDistances();
  };
  scene.add(new THREE.HemisphereLight('#FFF4E6', col.fog, 1.35));
  const sun = new THREE.DirectionalLight('#FFFFFF', 1.9); sun.position.set(-7, 12, 7); sun.castShadow = true;
  sun.shadow.mapSize.set(2048, 2048); Object.assign(sun.shadow.camera, { left: -9, right: 9, top: 9, bottom: -9, near: 1, far: 40 }); sun.shadow.bias = -0.0008; sun.shadow.radius = 4;
  scene.add(sun);

  const P3 = ([lo, la], y = DEPTH + 0.05) => new THREE.Vector3(PX(lo), y, PZ(la));
  const home3 = P3(o.home ? o.home.ll : GEO.center);
  const routes = [];
  const routeMatProto = {
    transparent: true, depthWrite: false,
    vertexShader: `varying vec2 vUv; void main(){ vUv = uv; gl_Position = projectionMatrix * modelViewMatrix * vec4(position,1.0); }`,
    fragmentShader: `uniform vec3 uColor, uStart; uniform float uProgress, uAlpha; varying vec2 vUv;
      void main(){ if (vUv.x > uProgress) discard;
        float head = smoothstep(uProgress - 0.12, uProgress, vUv.x);
        vec3 base = mix(uStart, uColor, smoothstep(0.0, 0.55, vUv.x));
        gl_FragColor = vec4(base * (1.0 + head * 1.4), uAlpha);
        #include <colorspace_fragment>
      }`,
  };
  const pinMat = new THREE.MeshStandardMaterial({ color: col.pin, roughness: 0.35, emissive: col.pin, emissiveIntensity: 0.35 });
  const stemMat = new THREE.MeshStandardMaterial({ color: '#FAF6F0', roughness: 0.6 });
  (o.cities || []).forEach((c) => {
    const end = P3(c.ll); const dist = home3.distanceTo(end);
    const mid = home3.clone().lerp(end, 0.5); mid.y += 0.45 + dist * 0.22;
    const curve = new THREE.QuadraticBezierCurve3(home3.clone(), mid, end.clone());
    const mat = new THREE.ShaderMaterial({ ...routeMatProto, uniforms: { uColor: { value: new THREE.Color(col.route) }, uStart: { value: new THREE.Color(col.routeStart) }, uProgress: { value: 0 }, uAlpha: { value: 1 } } });
    const mesh = new THREE.Mesh(new THREE.TubeGeometry(curve, 160, 0.019, 8, false), mat); scene.add(mesh);
    const packet = new THREE.Mesh(new THREE.SphereGeometry(0.05, 16, 12), new THREE.MeshBasicMaterial({ color: '#FFFFFF' })); scene.add(packet);
    const pin = new THREE.Group();
    const stem = new THREE.Mesh(new THREE.CylinderGeometry(0.012, 0.012, 0.26, 8), stemMat); stem.position.y = 0.13; stem.castShadow = true;
    const head = new THREE.Mesh(new THREE.SphereGeometry(0.075, 20, 14), pinMat); head.position.y = 0.29; head.castShadow = true;
    pin.add(stem, head); pin.position.copy(end).setY(DEPTH + 0.04); pin.scale.setScalar(0.0001); scene.add(pin);
    routes.push({ curve, mat, mesh, packet, pin, at: c.at, end, label: c.label ? document.getElementById(c.label) : null });
  });
  const home = new THREE.Group();
  const hstem = new THREE.Mesh(new THREE.CylinderGeometry(0.016, 0.016, 0.42, 8), stemMat); hstem.position.y = 0.21;
  const hhead = new THREE.Mesh(new THREE.SphereGeometry(0.09, 24, 16), new THREE.MeshStandardMaterial({ color: col.home, emissive: '#FFF4E6', emissiveIntensity: 0.25, roughness: 0.35 })); hhead.position.y = 0.45;
  home.add(hstem, hhead); home.position.copy(home3).setY(DEPTH + 0.04); scene.add(home);

  const composer = new EffectComposer(renderer);
  composer.setPixelRatio(1); composer.setSize(W, H);
  composer.addPass(new RenderPass(scene, camera));
  composer.addPass(new UnrealBloomPass(new THREE.Vector2(W, H), 0.55, 0.5, 0.78));
  composer.addPass(new OutputPass());

  const center = new THREE.Vector3(0, 0, 0);
  const sph = (target, radius, polarDeg, azDeg) => { const p = polarDeg * Math.PI / 180, a = azDeg * Math.PI / 180; return new THREE.Vector3(target.x + radius * Math.sin(p) * Math.sin(a), target.y + radius * Math.cos(p), target.z + radius * Math.sin(p) * Math.cos(a)); };
  const proj = new THREE.Vector3();
  const toScreen = (v) => { proj.copy(v).project(camera); return [(proj.x + 1) / 2 * W, (1 - proj.y) / 2 * H, proj.z]; };
  const homeNote = o.homeNote ? document.getElementById(o.homeNote) : null;
  const span = o.end - o.start, push = o.pushIn ?? 1.0;
  function cameraAt(t) {
    const u = t - o.start;
    const k1 = ease.inOut3(seg(u, o.pull0 ?? 0.85, o.pull1 ?? 3.0));
    const k2 = seg(u, o.pull1 ?? 3.0, span - push);
    const k3 = push > 0 ? ease.in3(seg(u, span - push, span)) : 0;
    const tgt = o.highStart ? center.clone() : home3.clone().setY(0).lerp(center, k1);
    let radius = (o.highStart ? lerp(30, 12.8, k1) : lerp(3.4, 12.8, k1)) - 0.9 * k2, polar = lerp(o.highStart ? 2 : 6, 47, k1) + 3 * k2, az = lerp(-24, -12, k1) + 9 * k2;
    if (k3 > 0) { tgt.lerp(home3.clone().setY(0.2), k3); radius = lerp(radius, 1.4, k3); polar = lerp(polar, 20, k3); }
    camera.position.copy(sph(tgt, radius, polar, az)); camera.lookAt(tgt);
    const shift = (o.viewShift || 0) * k1 * (1 - k3);
    if (Math.abs(shift) > 0.5) camera.setViewOffset(W, H, shift, 0, W, H); else camera.clearViewOffset();
    camera.updateMatrixWorld();
    return u;
  }
  if (o.follow) {   // e.g. a burst image that must open from home wherever home sits on screen
    const fe = document.getElementById(o.follow.el);
    layers.push({ start: o.follow.t0 - 0.05, end: o.follow.t1 + 0.05, render(t) {
      if (!fe) return;
      cameraAt(Math.min(t, o.end));
      const [x, y] = toScreen(home3.clone().setY(DEPTH + 0.3));
      fe.style.left = x.toFixed(1) + 'px'; fe.style.top = y.toFixed(1) + 'px';
    } });
  }
  const L = {
    start: o.start, end: o.end,
    render(t) {
      const u = cameraAt(t);
      boilCoast(Math.floor(t * 10));
      lineMat.opacity = 0.95 * ease.inOut2(seg(u, 0.1, 0.9));
      routes.forEach((r) => {
        const p = ease.inOut2(seg(u, r.at, r.at + 1.0));
        r.mat.uniforms.uProgress.value = p; r.mesh.visible = p > 0.001;
        const trip = (q) => { const w = seg(u, r.at + q, r.at + q + 1.1); return w > 0 && w < 1 ? w : -1; };
        let w = trip(1.05); if (w < 0) w = trip(2.6);
        r.packet.visible = w >= 0; if (w >= 0) r.packet.position.copy(r.curve.getPointAt(ease.inOut2(w)));
        r.pin.scale.setScalar(Math.max(0.0001, ease.back(seg(u, r.at + 0.85, r.at + 1.25))));
        if (r.label) { const [x, y] = toScreen(r.end.clone().setY(DEPTH + 0.36)); r.label.style.left = x.toFixed(1) + 'px'; r.label.style.top = y.toFixed(1) + 'px'; r.label.style.opacity = ease.out3(seg(u, r.at + 0.95, r.at + 1.3)).toFixed(3); }
      });
      if (homeNote) { const [nx, ny] = toScreen(home3.clone().setY(DEPTH)); homeNote.style.left = nx.toFixed(1) + 'px'; homeNote.style.top = ny.toFixed(1) + 'px'; }
      composer.render();
    },
  };
  layers.push(L); return L;
}

window.FILM3D = { particles, map, renderAll, layers };
window.addEventListener('hf-seek', (e) => renderAll(e.detail.time));
