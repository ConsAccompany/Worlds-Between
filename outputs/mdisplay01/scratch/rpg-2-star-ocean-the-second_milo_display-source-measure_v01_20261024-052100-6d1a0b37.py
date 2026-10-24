"""Read-only measurement of the Milo hairstyle-v02 sheet: size, background, column/row occupancy of figures.

Usage: python -I <this> SOURCE
Prints the background colour estimate and the foreground column runs (figure separation) and per-run bboxes.
"""
import hashlib
import sys

from PIL import Image

src = sys.argv[1]
raw = open(src, "rb").read()
print("sha256", hashlib.sha256(raw).hexdigest())
im = Image.open(src)
im.load()
print("size", im.size, "mode", im.mode)
rgb = im.convert("RGB")
w, h = rgb.size
corners = [rgb.getpixel(p) for p in ((0, 0), (w - 1, 0), (0, h - 1), (w - 1, h - 1), (w // 2, 0), (w // 2, h - 1))]
print("corners", corners)
bg = rgb.getpixel((0, 0))
px = rgb.load()
TH = 40


def fg(x, y):
    p = px[x, y]
    return abs(p[0] - bg[0]) + abs(p[1] - bg[1]) + abs(p[2] - bg[2]) > TH


cols = [sum(1 for y in range(0, h, 2) if fg(x, y)) for x in range(w)]
runs, start = [], None
for x, c in enumerate(cols + [0]):
    if c > 2 and start is None:
        start = x
    elif c <= 2 and start is not None:
        runs.append((start, x))
        start = None
print("column runs (>2 fg samples):", runs)
for a, b in runs:
    if b - a < 20:
        continue
    ys = [y for y in range(h) if any(fg(x, y) for x in range(a, b, 2))]
    print("run", (a, b), "width", b - a, "rows", (ys[0], ys[-1] + 1) if ys else None)
