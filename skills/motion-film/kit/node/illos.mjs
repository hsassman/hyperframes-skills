// Example illustrations for the demo film. Copy this file per project and write one builder per object your story needs.
// Rules that keep illustrations readable on screen:
//  - Draw the real object people will recognise in one second; add the one detail that names it.
//  - Outline first, flat offset fill behind it, details last. 6–8 px outlines at 1080p; thinner for detail.
//  - Don't decorate with shapes that read as something else.
// Usage: node illos.mjs [out.json]   (default ./illos.json)
import fs from 'fs';
import { Illo, seed, smooth, wob, ell, hatch } from './illo-lib.mjs';

const INK = '#1C2228', SOIL = '#7A5236', LEAF = '#5FA36A', LEAF2 = '#3F7F52', BARK = '#8C6A4A';

function sprout() {
  seed(212);
  const I = Illo(520, 560);
  const soil = smooth(wob([[40, 430], [140, 400], [260, 392], [380, 402], [480, 432], [470, 520], [50, 520]], 2), true, 0.3);
  I.fill('sf', soil, SOIL, 10, 10);
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

function tree() {
  seed(931);
  const I = Illo(620, 700);
  const ground = smooth(wob([[60, 640], [200, 622], [420, 622], [560, 640]], 1.5));
  const trunk = smooth(wob([[282, 640], [290, 520], [284, 420], [300, 330], [338, 330], [334, 420], [342, 520], [352, 640]], 1.2), true, 0.25);
  const crown = smooth(wob(ell(312, 250, 210, 175, 0, 0, Math.PI * 2, 14).slice(0, -1), 16), true, 0.5);
  const crown2 = smooth(wob(ell(250, 300, 120, 92, 0.2, 0, Math.PI * 2, 10).slice(0, -1), 9), true, 0.5);
  I.fill('tf', trunk, BARK, 9, 9);
  I.line('tr', trunk, INK, 6.5, 0.6);
  I.fill('cf', crown, LEAF, 12, 12);
  I.line('cr', crown, INK, 7, 0.9);
  I.fill('cf2', crown2, LEAF2, 0, 0);
  I.hatch('cs', hatch(crown2, { gap: 13, angle: -35 }), INK, 2.2, 0.4);
  I.line('br', smooth([[318, 360], [270, 300], [236, 278]]) + ' ' + smooth([[322, 350], [380, 290], [420, 270]]), INK, 4, 0.4);
  I.line('gd', ground, INK, 5, 0.4);
  return I.json();
}

const out = process.argv[2] || new URL('./illos.json', import.meta.url).pathname;
const res = { sprout: sprout(), tree: tree() };
fs.writeFileSync(out, JSON.stringify(res));
console.log('wrote', out, Object.fromEntries(Object.entries(res).map(([k, v]) => [k, v.parts.length])));
