"""Diagnostic only: list isolated texels (same metric as the Muxiu south gate) for a Muxiu north author revision.
Usage: python -I <this> <author tool path>"""
import importlib.util, sys
import numpy as np
spec = importlib.util.spec_from_file_location("north_author", sys.argv[1])
A = importlib.util.module_from_spec(spec); spec.loader.exec_module(A)
full = A.S.compose_layers(A.draw())
inv = {A.S.rgb(k): k for k in A.PAL}
rgb = full[..., :3].astype(int); op = full[..., 3] == 255
for y, x in zip(*np.nonzero(op)):
    same = 0
    for dy, dx in ((1, 0), (-1, 0), (0, 1), (0, -1)):
        yy, xx = y + dy, x + dx
        if 0 <= yy < A.H and 0 <= xx < A.W and op[yy, xx] and (rgb[yy, xx] == rgb[y, x]).all():
            same += 1
    if same == 0:
        print(int(x), int(y), inv.get(tuple(int(v) for v in full[y, x, :3]), "?"))
