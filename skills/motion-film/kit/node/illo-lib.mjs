// Hand-drawn illustration builder. An illustration is a list of ordered parts that the composition draws on one by one:
//   line  — a stroke that draws on (pathLength + dashoffset), edge-boiled by the composition's SVG filter
//   fill  — a flat colour block offset from the outline (screen-print feel) that fades in behind the line that just drew
//   hatch — rough.js hachure shading, drawn on quickly
// Output JSON per illustration: { w, h, parts: [{ id, d, kind, color, width, order, dur, dx?, dy?, group? }] }
import rough from 'roughjs';

const gen = rough.generator();
let _s = 7;
export const rnd = () => { _s = (_s * 16807) % 2147483647; return (_s - 1) / 2147483646; };
export const seed = (n) => { _s = n; };
const f = (v) => (Math.round(v * 10) / 10).toString();

/** Catmull-Rom through points -> cubic bezier path (open or closed). */
export function smooth(pts, closed = false, tension = 0.5) {
  if (pts.length < 2) return '';
  const n = pts.length; const get = (i) => closed ? pts[(i + n) % n] : pts[Math.max(0, Math.min(n - 1, i))];
  let d = `M${f(pts[0][0])},${f(pts[0][1])}`;
  for (let i = 0; i < (closed ? n : n - 1); i++) {
    const p0 = get(i - 1), p1 = get(i), p2 = get(i + 1), p3 = get(i + 2); const t = tension / 3;
    d += ` C${f(p1[0] + (p2[0] - p0[0]) * t)},${f(p1[1] + (p2[1] - p0[1]) * t)} ${f(p2[0] - (p3[0] - p1[0]) * t)},${f(p2[1] - (p3[1] - p1[1]) * t)} ${f(p2[0])},${f(p2[1])}`;
  }
  return closed ? d + ' Z' : d;
}
export const line = (pts) => 'M' + pts.map((q) => `${f(q[0])},${f(q[1])}`).join(' L');
/** Small seeded wobble so straight geometry reads as drawn by hand. */
export const wob = (pts, a = 1.2) => pts.map(([x, y]) => [x + (rnd() - 0.5) * 2 * a, y + (rnd() - 0.5) * 2 * a]);
export function ell(cx, cy, rx, ry, rot = 0, a0 = 0, a1 = Math.PI * 2, n = 28) {
  const out = [];
  for (let i = 0; i <= n; i++) {
    const t = a0 + (a1 - a0) * i / n, x = rx * Math.cos(t), y = ry * Math.sin(t);
    out.push([cx + x * Math.cos(rot) - y * Math.sin(rot), cy + x * Math.sin(rot) + y * Math.cos(rot)]);
  }
  return out;
}
export const rotp = (pts, cx, cy, a) => pts.map(([x, y]) => [cx + (x - cx) * Math.cos(a) - (y - cy) * Math.sin(a), cy + (x - cx) * Math.sin(a) + (y - cy) * Math.cos(a)]);
export const add = (pts, dx, dy) => pts.map(([x, y]) => [x + dx, y + dy]);
export function hatch(d, opt = {}) {
  const sh = gen.path(d, { fill: 'x', fillStyle: opt.style || 'hachure', hachureAngle: opt.angle ?? -41, hachureGap: opt.gap ?? 11,
    fillWeight: opt.weight ?? 2.2, roughness: opt.rough ?? 1.1, bowing: 0.8, stroke: 'none', seed: opt.seed ?? 3, disableMultiStroke: true, disableMultiStrokeFill: true });
  return gen.toPaths(sh).filter((p) => p.fill === 'none' || p.stroke !== 'none').map((p) => p.d).join(' ');
}
/** Builder: parts draw in the order they are added. dur = seconds for a line to draw (scaled by the composition's speed). */
export function Illo(w, h) {
  const parts = []; let order = 0;
  return {
    w, h, parts,
    line(id, d, color, width = 7, dur = 0.5, extra = {}) { parts.push({ id, d, kind: 'line', color, width, order: order++, dur, ...extra }); },
    fill(id, d, color, dx = 10, dy = 10, extra = {}) { parts.push({ id, d, kind: 'fill', color, dx, dy, order: order++, dur: 0.35, ...extra }); },
    hatch(id, d, color, width = 2.4, dur = 0.35, extra = {}) { parts.push({ id, d, kind: 'hatch', color, width, order: order++, dur, ...extra }); },
    beat() { order++; },
    json() { return { w, h, parts }; },
  };
}
