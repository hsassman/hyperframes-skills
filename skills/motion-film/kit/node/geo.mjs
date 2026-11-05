// Writes assets/geo.js (window.FILM_GEO) for FILM3D.map from Natural Earth 50m (world-atlas).
// Usage: node geo.mjs --main 404 [--insets 426] [--neighbours 800,834,231] [--bbox lonMin,latMin,lonMax,latMax] [--out ../../path/assets/geo.js]
// Codes are ISO 3166-1 numeric (e.g. 404 Kenya, 250 France, 036 Australia, 076 Brazil).
// --bbox drops far-away islands/territories from every polygon set (keep the mainland in shot).
import fs from 'fs';
import path from 'path';
import { createRequire } from 'module';
import * as topojson from 'topojson-client';
const require = createRequire(import.meta.url);
const arg = (k, d) => { const i = process.argv.indexOf('--' + k); return i > 0 ? process.argv[i + 1] : d; };
const codes = (s) => (s ? s.split(',').map((c) => c.trim().padStart(3, '0')) : []);
const MAIN = codes(arg('main')), INSETS = codes(arg('insets')), NB = codes(arg('neighbours'));
if (!MAIN.length) { console.error('need --main <iso numeric>'); process.exit(1); }
const bbox = arg('bbox') ? arg('bbox').split(',').map(Number) : null;
const out = arg('out', 'geo.js');
const world = JSON.parse(fs.readFileSync(require.resolve('world-atlas/countries-50m.json')));
const fc = topojson.feature(world, world.objects.countries);

function dp(pts, eps) {   // Douglas–Peucker in lon/lat
  if (pts.length < 3) return pts;
  let dmax = 0, idx = 0; const a = pts[0], b = pts[pts.length - 1];
  for (let i = 1; i < pts.length - 1; i++) {
    const [x, y] = pts[i];
    const d = Math.abs((b[1] - a[1]) * x - (b[0] - a[0]) * y + b[0] * a[1] - b[1] * a[0]) / (Math.hypot(b[1] - a[1], b[0] - a[0]) || 1e-9);
    if (d > dmax) { dmax = d; idx = i; }
  }
  return dmax > eps ? [...dp(pts.slice(0, idx + 1), eps).slice(0, -1), ...dp(pts.slice(idx), eps)] : [a, b];
}
// closed rings: split at the farthest point first, or DP collapses the ring (start == end)
const simplify = (r, eps) => { let far = 0, fi = 0; r.forEach(([x, y], i) => { const d = Math.hypot(x - r[0][0], y - r[0][1]); if (d > far) { far = d; fi = i; } }); return [...dp(r.slice(0, fi + 1), eps).slice(0, -1), ...dp(r.slice(fi), eps)]; };
const inBox = (poly) => !bbox || poly[0].some(([lo, la]) => lo >= bbox[0] && la >= bbox[1] && lo <= bbox[2] && la <= bbox[3]);
function polys(codeList, eps) {
  const res = [];
  for (const f of fc.features) {
    if (!codeList.includes(String(f.id).padStart(3, '0'))) continue;
    const ps = f.geometry.type === 'Polygon' ? [f.geometry.coordinates] : f.geometry.coordinates;
    for (const p of ps) if (inBox(p)) res.push(p.map((r) => simplify(r, eps)));
  }
  return res;
}
const main = polys(MAIN, 0.012);
if (!main.length) { console.error('no polygons for', MAIN); process.exit(1); }
let lo0 = 1e9, la0 = 1e9, lo1 = -1e9, la1 = -1e9;
for (const p of main) for (const [lo, la] of p[0]) { lo0 = Math.min(lo0, lo); la0 = Math.min(la0, la); lo1 = Math.max(lo1, lo); la1 = Math.max(la1, la); }
const geo = { center: [(lo0 + lo1) / 2, (la0 + la1) / 2], span: [lo1 - lo0, la1 - la0], main, insets: polys(INSETS, 0.012), neighbours: polys(NB, 0.02) };
fs.mkdirSync(path.dirname(path.resolve(out)), { recursive: true });
fs.writeFileSync(out, 'window.FILM_GEO=' + JSON.stringify(geo) + ';\n');
console.log(`wrote ${out}: main ${main.length} polys, insets ${geo.insets.length}, neighbours ${geo.neighbours.length}, centre ${geo.center.map((v) => v.toFixed(2))}`);
