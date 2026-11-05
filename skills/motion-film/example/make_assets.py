"""Procedural assets for the demo film (no downloads): chapter grounds, a paper texture for the texture-cover transition,
a soft particle sprite and a burst. In a real project these come from your footage, photos and generated overlays
(see references/ai-assets.md)."""
import os, sys
import numpy as np
from PIL import Image, ImageFilter

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "kit"))
from filmkit.grounds import plate  # noqa: E402

A = os.path.join(HERE, "assets"); os.makedirs(A, exist_ok=True)
rng = np.random.default_rng(4)
plate(f"{A}/gr0.jpg", linear=(135, [(0, "#F6F3E8"), (.5, "#E7EBD6"), (1, "#C9D8B4")]), glows=[(1150, -200, 1100, "#F2C14E", .32), (-300, 600, 900, "#5FA36A", .18)], paper=.35)
plate(f"{A}/gr1.jpg", linear=(140, [(0, "#EEF0DF"), (.5, "#D3DFBF"), (1, "#A9C08E")]), glows=[(1300, -300, 1000, "#FFFFFF", .4), (-300, 500, 900, "#F2C14E", .22)], paper=.4)
plate(f"{A}/gr3.jpg", radial=(0.5, 0.42, [(0, "#FBFAF3"), (.55, "#E9EEDA"), (1, "#C4D6A8")]), glows=[(-200, -200, 900, "#5FA36A", .2), (1300, 400, 1000, "#F2C14E", .26)], paper=.3)

# paper texture with soft fibres (texture-cover transition), 1920x1080
def blurred_noise(h, w, sigma, down=4):
    n = rng.normal(0, 1, (h // down, w // down))
    img = Image.fromarray(np.clip(128 + n * 40, 0, 255).astype("uint8")).filter(ImageFilter.GaussianBlur(sigma))
    return np.asarray(img.resize((w, h), Image.BICUBIC), np.float32) - 128
fib = blurred_noise(1080, 1920, 0.6, 2) * 0.35 + blurred_noise(1080, 1920, 6, 4) * 0.5
base = np.dstack([np.full((1080, 1920), 238.0), np.full((1080, 1920), 236.0), np.full((1080, 1920), 226.0)]) + fib[..., None]
Image.fromarray(np.clip(base, 0, 255).astype("uint8")).save(f"{A}/paper.jpg", quality=90)

# soft round sprite (particles) and a burst on transparent
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
Image.fromarray(np.dstack([np.full((H, W), 246), np.full((H, W), 248), np.full((H, W), 236), al]).astype("uint8"), "RGBA").save(f"{A}/burst.png", optimize=True)
print("assets ok")
