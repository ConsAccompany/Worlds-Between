"""Scratch QA (not source): x6 east draft beside Milo south/north at x6, plus a copy with isolated texels marked
magenta. Imports the east author in memory only; writes argv[1] (PNG) and prints isolated coordinates."""
import glob, importlib.util, os, sys
import numpy as np
from PIL import Image

R = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "../../.."))
sp = importlib.util.spec_from_file_location("east", glob.glob(os.path.join(R, "tools/*milo_east-static-author*.py"))[0])
E = importlib.util.module_from_spec(sp); sp.loader.exec_module(E)
full = E.S.compose_layers(E.draw())
op = full[..., 3] == 255; rgb = full[..., :3].astype(int); iso = []
for y, x in zip(*np.nonzero(op)):
    if not any(0 <= y + dy < 112 and 0 <= x + dx < 80 and op[y + dy, x + dx] and (rgb[y + dy, x + dx] == rgb[y, x]).all()
               for dy, dx in ((1, 0), (-1, 0), (0, 1), (0, -1))):
        iso.append((int(x), int(y)))
print("isolated", len(iso), "(x, y; f = x - 40):", iso)
mark = full.copy()
for x, y in iso:
    mark[y, x] = (255, 0, 255, 255)
refs = [np.array(Image.open(glob.glob(os.path.join(R, f"game/assets/characters/milo-native-v01/{d}/*static_*.png"))[0]).convert("RGBA"))
        for d in ("south", "north")]
ims = refs + [full, mark]
out = Image.new("RGBA", (80 * 6 * len(ims), 112 * 6), (120, 130, 120, 255))
for i, a in enumerate(ims):
    out.alpha_composite(Image.fromarray(a, "RGBA").resize((480, 672), Image.NEAREST), (480 * i, 0))
out.save(sys.argv[1])
