// Example illustrations for the demo film. Copy this file per project and draw the objects your story needs.
// Rules that keep illustrations readable on screen (learned the hard way):
//  - Draw the real object people will recognise in one second; add the one detail that names it (a handle, a steam curl, tape).
//  - Outline first, flat offset fill behind it, details last. 6–8 px outlines at 1080p; thinner for detail.
//  - Don't decorate with shapes that read as something else (a ring on a handle reads as a magnifying glass).
// Usage: node illos.mjs [out.json]   (default ./illos.json)
import fs from 'fs';
import { Illo, seed, smooth, line, wob, ell, hatch } from './illo-lib.mjs';

const INK = '#1F2A30', ACCENT = '#E8743B', WARM = '#F2D3A6', MID = '#C99460', LIGHT = '#E9C08A', LEAF = '#5FA36A';

function parcel() {
  seed(505);
  const I = Illo(680, 600);
  const F = [[90, 230], [400, 230], [400, 520], [90, 520]], Sd = [[400, 230], [560, 150], [560, 430], [400, 520]], Tp = [[90, 230], [250, 150], [560, 150], [400, 230]];
  const D = (pts) => smooth(wob(pts, 1.4), true, 0.08);
  I.fill('ff', D(F), LIGHT, 11, 11); I.fill('sf', D(Sd), MID, 11, 11); I.fill('tf', D(Tp), WARM, 11, 11);
  I.line('bx', D(F) + ' ' + D(Sd) + ' ' + D(Tp), INK, 6.5, 0.9);
  I.line('sm', smooth(wob([[170, 190], [330, 190], [480, 190]], 0.8)), INK, 4.5, 0.35);
  const tapeTop = smooth([[150, 176], [490, 176], [490, 204], [150, 204]], true, 0), tapeSide = smooth([[480, 190], [500, 180], [500, 460], [480, 470]], true, 0);
  I.fill('tpe', tapeTop + ' ' + tapeSide, 'rgba(255,248,232,0.82)', 0, 0);
  I.line('tpl', line([[150, 176], [490, 176]]) + ' ' + line([[150, 204], [480, 204]]) + ' ' + line([[500, 180], [500, 460]]), INK, 2.6, 0.5);
  const up = [130, 170].map((x) => line([[x, 300], [x, 262]]) + ' ' + line([[x - 12, 274], [x, 260], [x + 12, 274]])).join(' ');
  I.line('mk', up, INK, 4.2, 0.4);
  I.hatch('sh', hatch(D(Sd), { gap: 14 }), INK, 2.2, 0.35);
  return I.json();
}

function sprout() {
  seed(212);
  const I = Illo(520, 560);
  const soil = smooth(wob([[40, 430], [140, 400], [260, 392], [380, 402], [480, 432], [470, 520], [50, 520]], 2), true, 0.3);
  I.fill('sf', soil, '#8A5A3C', 10, 10);
  I.line('so', soil, INK, 6.5, 0.6);
  I.line('st', smooth(wob([[262, 400], [258, 330], [268, 250], [262, 170]], 0.8)), INK, 6.5, 0.5);
  const leafL = smooth([[262, 260], [200, 220], [140, 232], [178, 286], [262, 262]], true, 0.4);
  const leafR = smooth([[264, 196], [330, 140], [404, 150], [362, 214], [264, 198]], true, 0.4);
  I.fill('lf', leafL + ' ' + leafR, LEAF, 9, 9);
  I.line('lv', leafL + ' ' + leafR, INK, 6, 0.7);
  I.line('vn', smooth([[262, 260], [210, 248], [170, 252]]) + ' ' + smooth([[264, 196], [320, 168], [370, 162]]), INK, 3.2, 0.4);
  I.hatch('sh', hatch(soil, { gap: 12, angle: 30 }), INK, 2.0, 0.35);
  return I.json();
}

function cup() {
  seed(77);
  const I = Illo(560, 600);
  const body = smooth(wob([[110, 250], [430, 250], [404, 500], [380, 530], [160, 530], [136, 500]], 1.2), true, 0.18);
  const handle = smooth([[428, 300], [500, 304], [506, 388], [418, 420]], false, 0.6);
  const saucer = smooth(ell(270, 545, 220, 34, 0, 0, Math.PI * 2, 24).slice(0, -1), true);
  I.fill('scf', saucer, WARM, 8, 8); I.line('sc', saucer, INK, 6, 0.5);
  I.fill('bf', body, '#FFFDF8', 10, 10); I.line('bd', body + ' ' + handle, INK, 6.5, 0.8);
  const rim = smooth(ell(270, 250, 160, 26, 0, 0, Math.PI * 2, 24).slice(0, -1), true);
  I.fill('cf', rim, '#6B3E26', 0, 0); I.line('rm', rim, INK, 5, 0.4);
  I.line('band', smooth(wob([[124, 330], [270, 342], [420, 330]], 0.6)), ACCENT, 9, 0.4);
  const steam = [0, 1, 2].map((k) => smooth(wob([[200 + k * 70, 220], [185 + k * 70, 170], [215 + k * 70, 120], [195 + k * 70, 70]], 2))).join(' ');
  I.line('stm', steam, INK, 4.5, 0.7);
  return I.json();
}

const out = process.argv[2] || new URL('./illos.json', import.meta.url).pathname;
const res = { parcel: parcel(), sprout: sprout(), cup: cup() };
fs.writeFileSync(out, JSON.stringify(res));
console.log('wrote', out, Object.fromEntries(Object.entries(res).map(([k, v]) => [k, v.parts.length])));
