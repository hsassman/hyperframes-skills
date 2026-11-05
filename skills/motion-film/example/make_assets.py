"""Procedural assets for the demo film (no downloads): chapter grounds, a corrugated shutter texture, a soft sprite and a
powder burst. In a real project these come from your footage, photos and generated overlays (see references/ai-assets.md)."""
import os, sys
import numpy as np
from PIL import Image, ImageFilter

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "kit"))
from filmkit.grounds import plate  # noqa: E402

A = os.path.join(HERE, "assets"); os.makedirs(A, exist_ok=True)
plate(f"{A}/gr0.jpg", linear=(135, [(0, "#FFF4E6"), (.45, "#FBE3C8"), (1, "#F6C79A")]), glows=[(1100, -200, 1100, "#E8743B", .36), (-300, 600, 900, "#2BA3B8", .2)], paper=.35)
plate(f"{A}/gr1.jpg", linear=(140, [(0, "#F3DEC0"), (.5, "#D9B285"), (1, "#B9885A")]), glows=[(1300, -300, 1000, "#FFFFFF", .4), (-300, 500, 900, "#E8743B", .3)], paper=.4)
plate(f"{A}/gr3.jpg", radial=(0.5, 0.42, [(0, "#FFF6EA"), (.55, "#FBE0C2"), (1, "#F6B67A")]), glows=[(-200, -200, 900, "#2BA3B8", .2), (1300, 400, 1000, "#E8743B", .3)], paper=.3)

# corrugated steel shutter, 1920x1120
y = np.arange(1120)[:, None].astype(np.float32); x = np.arange(1920)[None, :].astype(np.float32)
rib = 0.5 + 0.5 * np.sin(y / 46 * 2 * np.pi)
base = 120 + 70 * rib ** 1.5 + 8 * np.sin(x / 300 + y / 900)
rng = np.random.default_rng(4)
noise = np.asarray(Image.fromarray(np.clip(128 + rng.normal(0, 30, (560, 960)), 0, 255).astype("uint8")).filter(ImageFilter.GaussianBlur(1)).resize((1920, 1120)), np.float32) - 128
steel = np.clip(base + noise * 0.25, 0, 255)
rgb = np.dstack([steel * 0.93, steel * 0.98, steel * 1.02])
rgb[1080:] *= 0.45
Image.fromarray(np.clip(rgb, 0, 255).astype("uint8")).save(f"{A}/shutter.jpg", quality=90)

# soft round sprite (particles) and a powder burst on transparent
yy, xx = np.mgrid[0:256, 0:256].astype(np.float32); r = np.hypot(xx - 128, yy - 128) / 128
spr = np.clip(1 - r, 0, 1) ** 2 * 255
Image.fromarray(np.dstack([np.full_like(spr, 255)] * 3 + [spr]).astype("uint8"), "RGBA").save(f"{A}/sprite.png")
H, W = 1300, 2300
yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
ang = np.arctan2(yy - H / 2, xx - W / 2); rad = np.hypot((xx - W / 2) / (W / 2), (yy - H / 2) / (H / 2))
lobes = 0.62 + 0.18 * np.sin(ang * 7 + 1.3) + 0.1 * np.sin(ang * 13 + 0.4)
n2 = np.asarray(Image.fromarray(np.clip(128 + rng.normal(0, 70, (H // 4, W // 4)), 0, 255).astype("uint8")).filter(ImageFilter.GaussianBlur(2)).resize((W, H)), np.float32) / 255
al = np.clip((lobes - rad) * 3.2 + (n2 - 0.5) * 0.9, 0, 1)
al = np.asarray(Image.fromarray((al * 255).astype("uint8")).filter(ImageFilter.GaussianBlur(3)), np.float32)
Image.fromarray(np.dstack([np.full((H, W), 252), np.full((H, W), 244), np.full((H, W), 231), al]).astype("uint8"), "RGBA").save(f"{A}/burst.png", optimize=True)
print("assets ok")
