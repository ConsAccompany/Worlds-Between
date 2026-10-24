"""Read-only diagnostic: list isolated opaque texels (same metric as the south v01 gate) of a PNG.

v02: re-executes itself under the project venv python (system python3 lacks numpy; v01 failed with rc1).
Usage (from repo/): python3 -I <this> <png> [downscale]   (6 for the x6 previews). Prints y, x, f = 40 - x, colour.
"""
import os
import pathlib
import subprocess
import sys

try:
    import numpy as np
    from PIL import Image
except ModuleNotFoundError:
    R = pathlib.Path(__file__).resolve().parents[2]
    py = os.path.abspath(R.parent / 'tooling/venv/bin/python')     # not resolve(): keep the venv symlink
    sys.exit(subprocess.run([py, '-I', __file__, *sys.argv[1:]], timeout=60).returncode)

a = np.array(Image.open(sys.argv[1]).convert('RGBA'))
k = int(sys.argv[2]) if len(sys.argv) > 2 else 1
a = a[::k, ::k]
op = a[..., 3] == 255; rgb = a[..., :3].astype(int); H, W = op.shape; out = []
for y, x in zip(*np.nonzero(op)):
    if not any(0 <= y + dy < H and 0 <= x + dx < W and op[y + dy, x + dx] and (rgb[y + dy, x + dx] == rgb[y, x]).all()
               for dy, dx in ((1, 0), (-1, 0), (0, 1), (0, -1))):
        out.append((int(y), int(x), 40 - int(x), '%02x%02x%02x' % tuple(rgb[y, x])))
print(len(out))
for o in out:
    print(*o)
