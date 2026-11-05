"""Turn generated or shot images into composition-ready assets.

Generated overlays (frost, smoke, clouds, powder bursts, sparks, snowflakes) are easiest to get from an image model as
"white/coloured element on pure black". This module turns those into clean RGBA:

  cutout   alpha from luminance + un-premultiplied edges (no grey cut-out fringe) + feathered frame edges
  sprite   square, centred cutout for particle textures (FILM3D.particles sprite)
  tint     recolour a cutout into brand colours by luminance
  cover    resize/crop to fill an exact size
  texture  keep only a texture's fibre detail (high-pass) and lay it over a designed plate — real material, your grade
  cleanup  conservative photo clean-up (denoise, neutral highlights, local contrast, light sharpen) that keeps framing exact

CLI:
  python3 prep.py cutout in.png out.png [--lo .05 --hi .6 --gamma .9 --feather .1 --size 1920x1080 --warm]
  python3 prep.py sprite in.png out.png [--px 256]
  python3 prep.py tint in.png out.png --dark '#123640' --light '#3A8FA3'
  python3 prep.py texture plate.jpg texture.png out.jpg [--strength .03 --radius 28]
  python3 prep.py cleanup in.jpg out.jpg
"""
import argparse
import numpy as np
from PIL import Image, ImageFilter


def cover(im, W, H):
    w, h = im.size; s = max(W / w, H / h)
    im = im.resize((round(w * s), round(h * s)), Image.LANCZOS)
    x, y = (im.width - W) // 2, (im.height - H) // 2
    return im.crop((x, y, x + W, y + H))


def lum_alpha(arr, lo=0.05, hi=0.65, gamma=1.0):
    l = arr.max(axis=2) / 255.0
    return np.clip((l - lo) / (hi - lo), 0, 1) ** gamma


def cutout(im, lo=0.05, hi=0.6, gamma=0.9, feather=0.0, size=None, lift=0.0, warm=False, blur=0.0):
    """Element on black -> RGBA. Edges are un-premultiplied (they were mixed with black, so their RGB is too dark);
    interiors keep their own shading. feather fades the outer frame (fraction of width/height) so no rectangle shows."""
    im = im.convert("RGB")
    if size:
        im = cover(im, *size)
    a = np.asarray(im, np.float32)
    al = lum_alpha(a, lo, hi, gamma)
    if blur:
        al = np.asarray(Image.fromarray((al * 255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(blur)), np.float32) / 255.0
    l = a.max(axis=2, keepdims=True) / 255.0
    unpre = np.clip(a / np.clip(l, 0.04, 1.0), 0, 255)
    w = np.clip((l - 0.30) / 0.45, 0, 1)
    rgb = unpre * (1 - w) + a * w
    if lift:
        rgb = 255 - (255 - rgb) * (1 - lift)
    if warm:
        rgb = rgb * np.array([1.0, 0.988, 0.975], np.float32)
    if feather:
        Hh, Ww = al.shape
        yy = np.linspace(0, 1, Hh)[:, None]; xx = np.linspace(0, 1, Ww)[None, :]
        al = al * np.clip(np.minimum(np.minimum(xx, 1 - xx), np.minimum(yy, 1 - yy)) / feather, 0, 1) ** 1.4
    return Image.fromarray(np.dstack([rgb, al * 255]).clip(0, 255).astype(np.uint8), "RGBA")


def sprite(im, px=256, lo=0.06, hi=0.8):
    im = im.convert("RGB"); w, h = im.size; c = min(w, h)
    im = im.crop(((w - c) // 2, (h - c) // 2, (w + c) // 2, (h + c) // 2)).resize((px, px), Image.LANCZOS)
    a = np.asarray(im, np.float32)
    return Image.fromarray(np.dstack([a, lum_alpha(a, lo, hi) * 255]).clip(0, 255).astype(np.uint8), "RGBA")


def _hex(h):
    h = h.lstrip("#"); return np.array([int(h[i:i + 2], 16) for i in (0, 2, 4)], np.float32)


def tint(im, dark, light):
    """Recolour by luminance between two brand colours, keeping alpha."""
    im = im.convert("RGBA"); a = np.asarray(im, np.float32)
    lum = a[..., :3].max(axis=2, keepdims=True) / 255.0
    rgb = _hex(dark) * (1 - lum) + _hex(light) * lum
    return Image.fromarray(np.dstack([rgb, a[..., 3]]).clip(0, 255).astype(np.uint8), "RGBA")


def texture(plate, tex, strength=0.03, radius=28):
    """Lay a material's fine detail (paper fibre, kraft, linen, concrete) over a designed plate without its colour."""
    plate = plate.convert("RGB"); k = np.asarray(cover(tex.convert("RGB"), *plate.size), np.float32).mean(axis=2)
    blur = np.asarray(Image.fromarray(k.clip(0, 255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(radius)), np.float32)
    hp = k - blur; hp = hp / (np.abs(hp).std() + 1e-6)
    out = np.asarray(plate, np.float32) * (1.0 + hp[..., None] * strength)
    return Image.fromarray(out.clip(0, 255).astype(np.uint8))


def cleanup(path_in, path_out, denoise=4, neutral=True, clahe=1.5, sharpen=0.45):
    """Deterministic photo clean-up. Use this instead of asking an image model to 'clean up' photos that contain printed
    text, labels or logos — models redraw them (garbled words, wrong marks) and re-frame the shot."""
    import cv2
    im = cv2.imread(path_in)
    den = cv2.fastNlMeansDenoisingColored(im, None, denoise, denoise, 7, 21)
    lab = cv2.cvtColor(den, cv2.COLOR_BGR2LAB).astype(np.float32)
    L, A, B = lab[..., 0], lab[..., 1], lab[..., 2]
    if neutral:
        hi = L > np.percentile(L, 85)
        A += (128.0 - A[hi].mean()); B += (126.0 - B[hi].mean())
    Lu = cv2.createCLAHE(clipLimit=clahe, tileGridSize=(6, 6)).apply(L.clip(0, 255).astype(np.uint8)).astype(np.float32)
    L = L * 0.45 + Lu * 0.55
    out = cv2.cvtColor(np.dstack([L, A, B]).clip(0, 255).astype(np.uint8), cv2.COLOR_LAB2BGR)
    bl = cv2.GaussianBlur(out, (0, 0), 1.1)
    out = cv2.addWeighted(out, 1 + sharpen, bl, -sharpen, 0)
    cv2.imwrite(path_out, out, [cv2.IMWRITE_JPEG_QUALITY, 93])


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("op", choices=["cutout", "sprite", "tint", "texture", "cleanup"])
    ap.add_argument("paths", nargs="+")
    ap.add_argument("--lo", type=float, default=0.05); ap.add_argument("--hi", type=float, default=0.6)
    ap.add_argument("--gamma", type=float, default=0.9); ap.add_argument("--feather", type=float, default=0.0)
    ap.add_argument("--blur", type=float, default=0.0); ap.add_argument("--lift", type=float, default=0.0)
    ap.add_argument("--size", default=None); ap.add_argument("--warm", action="store_true")
    ap.add_argument("--px", type=int, default=256); ap.add_argument("--dark"); ap.add_argument("--light")
    ap.add_argument("--strength", type=float, default=0.03); ap.add_argument("--radius", type=int, default=28)
    a = ap.parse_args()
    if a.op == "cutout":
        size = tuple(int(v) for v in a.size.split("x")) if a.size else None
        cutout(Image.open(a.paths[0]), a.lo, a.hi, a.gamma, a.feather, size, a.lift, a.warm, a.blur).save(a.paths[1], optimize=True)
    elif a.op == "sprite":
        sprite(Image.open(a.paths[0]), a.px).save(a.paths[1])
    elif a.op == "tint":
        tint(Image.open(a.paths[0]), a.dark, a.light).save(a.paths[1])
    elif a.op == "texture":
        texture(Image.open(a.paths[0]), Image.open(a.paths[1]), a.strength, a.radius).save(a.paths[2], quality=92)
    else:
        cleanup(a.paths[0], a.paths[1])
    print("wrote", a.paths[-1])
