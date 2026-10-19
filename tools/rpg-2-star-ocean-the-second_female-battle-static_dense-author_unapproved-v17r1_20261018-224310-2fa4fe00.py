"""UNAPPROVED, TEST-ONLY v17r1 FACIAL finishing pass over the frozen v17 density prototype (ONE static frame).

v17r1 (root review 2026-10-18 of v17 3cf05f0d): the density method is kept; the eye/brow were too clustered and the bangs
too stripe-like. ONE bounded pass on the head layer's face/hair texels only (R1_EDIT_BOX); every other layer, the pin,
the cell, the logical extent and the palette are the frozen v17 values. The block below marked "v17r1" repaints head
rows by hand (same ASCII method); check proves the other 23 layers are byte-identical to the frozen v17 ORA layers and
that composite changes stay inside the edit box (+1 texel for the silhouette outline pass). v17 files are not touched.

Original v17 docstring follows.
UNAPPROVED, TEST-ONLY v17 density-method prototype: female protagonist battle idle facing right, ONE static frame.

Creator verdict on v16 (2026-10-18 22:01, verbatim): "this is just way too coarse, her face is not even recognizable".
Method change (not another tweak of v16): the frame is RE-AUTHORED at native 136x144 texels for the SAME logical 68x72
extent (pin 64,136 native = 32,68 logical). The game draws it with draw_texture_rect into 68x72 logical units; in the
project's default 1280x720 canvas_items window (factor 2) every native texel lands on one physical pixel. The 0.65
battle proportion is already baked into the 68x72 logical extent and is NOT applied again.

Authoring: every layer is placed by hand in this file - explicit ASCII rows for the head, face, hands, buckles and other
details, and hard-edged polygon / ellipse / line fills (integer vertices, PIL non-antialiased rasterisation) for broad
cloth and leather planes, followed by hand-typed fold, seam and highlight rows. No resampling, filtering, dithering,
noise, gradients, quantising, image generation or upscaling; v16 is NOT used as pixel input (only its logical bounding
box is compared in check). Binary alpha. Palette: v16's 33 keys + up to 15 disclosed keys (<= 48 colours).

Modes:  preview <dir>   inspection PNGs (one subject per file) outside the repo
        build           writes the native PNG, head PNG, layered .ora and manifest to outputs/battle-static-v17r1
        check           technical gates on the built files (writes nothing)
Run:    python -I -B <this file> preview <dir> | build | check
"""
import argparse, hashlib, io, json, os, sys, zipfile
import numpy as np
from PIL import Image, ImageDraw

SLUG = "rpg-2-star-ocean-the-second"
VER = "unapproved-v17r1"
STAMP = "20261018-224310"
RUN_ID = "2fa4fe00"
W, H = 136, 144
LOGICAL = (68, 72)
PIN = (64, 136)            # native; = logical (32, 68): first transparent row under the soles, between the feet
REPO = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
OUT_DIR_REL = "outputs/battle-static-v17r1"
V17_DIR_REL = "outputs/battle-static-v17"           # frozen v17 (read-only evidence; sha-pinned below)
V17_FROZEN = {
    "rpg-2-star-ocean-the-second_female-battle-idle-right_dense-native136_unapproved-v17_20261018-220631-cde3a961.png":
        "3cf05f0d3e560bdba5c4910b1192f5ff6ce34c99d747f2643e974fcaeb1d07db",
    "rpg-2-star-ocean-the-second_female-battle-idle-right_dense-layers_unapproved-v17_20261018-220631-59156ff8.ora":
        "ac001715a7ed7a930f02977a3f81d38434ae0d0a429c61f7d0ac3cfd85a9245c",
    "rpg-2-star-ocean-the-second_female-battle-idle-right_dense-head-native_unapproved-v17_20261018-220631-64242174.png":
        "767863fe6802df0df1f09c153f421f841ef63962651f5fdc096de115420e33e2",
    "rpg-2-star-ocean-the-second_female-battle-idle-right_dense-manifest_unapproved-v17_20261018-220631-36233c94.json":
        "a4aa499970b437c69da400644cbf3c7ce5aa4b71c2b3c0f3fac69cd02c1845d5",
    "rpg-2-star-ocean-the-second_female-battle-idle-right_dense-check-report_unapproved-v17_20261018-220631-c38bb78c.json":
        "6ebb04e38aca1e10b1cb1f1f77e68c8053d287dedbe3a0ae762e631226e99f0e",
    "rpg-2-star-ocean-the-second_v17-capture-measure-report_test-only_20261018-222918-7d41e2b6.json":
        "a7dd70447e6fbeb3683fe6635d5eceed3268380ebaab7a8de4a70fc2c40201dc",
    "rpg-2-star-ocean-the-second_v17-capture-measure-report-r2_test-only_20261018-222918-7d41e2b6.json":
        "e4820cc8f08754b06eeef432ad930d6d32aa3ba39d397a28364f721e66cd3384",
}
V17_PNG = "rpg-2-star-ocean-the-second_female-battle-idle-right_dense-native136_unapproved-v17_20261018-220631-cde3a961.png"
V17_ORA = "rpg-2-star-ocean-the-second_female-battle-idle-right_dense-layers_unapproved-v17_20261018-220631-59156ff8.ora"
R1_EDIT_BOX = (70, 17, 95, 44)     # x0, y0, x1, y1 exclusive: the ONLY head-layer texels v17r1 may change
R1_COMP_BOX = (69, 16, 96, 45)     # edit box + 1 texel: composite changes allowed (silhouette outline pass)
V16_PNG_REL = ("outputs/battle-static-v16/rpg-2-star-ocean-the-second_female-battle-idle-right_static-native0p65_"
               "unapproved-v16_20261018-212808-e75685af.png")
V16_PNG_SHA = "ce6d294c23f89556e3822470966704ef68534d4deb69500a03d47f63ca79b768"

PALETTE = {
    # ---- v16's 33 keys, unchanged values ----
    "K": "#16141a",                                                                  # outline
    "1": "#231816", "2": "#3d2a22", "3": "#5c3e2c", "4": "#82593b", "h": "#a8794f",  # hair dark -> sheen
    "S": "#fbd5b0", "s": "#e7a67c", "x": "#b36f50", "E": "#1d1214",                  # skin light/mid/shadow, lash/pupil
    "C": "#222839", "c": "#3a4560", "o": "#5e6e8c",                                  # v8 storm-slate coat
    "T": "#324542", "t": "#4a625c",                                                  # v8 spruce trousers
    "W": "#f3ead9", "w": "#c6b59d",                                                  # shirt / shadowed shirt
    "P": "#d7c0a8", "p": "#b09986",                                                  # pale beige cuff / buckle
    "L": "#2e1c14", "l": "#533626",                                                  # dark leather
    "d": "#45342e", "D": "#6f5a4c",                                                  # deep / lit boot + pack brown
    "Q": "#0a323b", "q": "#1a767b", "g": "#249b98", "G": "#6cc9bc",                  # teal
    "m": "#5a6470", "M": "#a9b5bd", "Z": "#eef4f5",                                  # steel
    "u": "#7a6f68", "e": "#2e364d", "n": "#5d4738",
    # ---- v17 disclosed density keys (each a deliberate plane, not a blend) ----
    "j": "#f2bd94",   # skin mid-light: cheek turning toward the ear, lower lid
    "k": "#8c4f3f",   # deep skin line: face profile, jaw / chin underside, ear canal, mouth corner
    "r": "#c7766b",   # lip
    "y": "#f6f0e6",   # eye white
    "i": "#7b4a2b",   # iris (brown, v8 identity)
    "b": "#3b2419",   # upper iris under the lash shadow
    "O": "#8495b3",   # lit storm-slate edge (shoulder top, lapel and hem edges in light)
    "f": "#a39079",   # deep shirt fold
    "N": "#8c7462",   # lit leather crest (boot toe, flap edge)
    "v": "#5f7c74",   # lit spruce (near thigh / shin front plane)
    "a": "#6b4a34",   # hair warm mid (strand body between 3 and 4)
    "z": "#7d8893",   # mid steel (blade flat, canister body)
}
EDGE_KEEP = set("k")       # silhouette texels that keep their own deep key instead of the black outline

LAYERS = []                # bottom -> top: Layer objects


class Layer:
    def __init__(self, name):
        self.name = name
        self.px = {}
        LAYERS.append(self)

    def _mask(self, draw_fn):
        im = Image.new("1", (W, H), 0)
        draw_fn(ImageDraw.Draw(im))
        a = np.array(im, dtype=bool)
        ys, xs = np.nonzero(a)
        return list(zip(xs.tolist(), ys.tolist()))

    def poly(self, key, pts):
        for p in self._mask(lambda d: d.polygon(pts, fill=1, outline=1)):
            self.px[p] = key
        return self

    def ellipse(self, key, box):
        for p in self._mask(lambda d: d.ellipse(box, fill=1, outline=1)):
            self.px[p] = key
        return self

    def line(self, key, pts, width=1):
        for p in self._mask(lambda d: d.line(pts, fill=1, width=width)):
            self.px[p] = key
        return self

    def shade(self, key, pts):
        """Recolour only texels this layer already owns inside the polygon (a light / shadow plane)."""
        for p in self._mask(lambda d: d.polygon(pts, fill=1, outline=1)):
            if p in self.px:
                self.px[p] = key
        return self

    def edge(self, key, only=None):
        """Recolour this layer's own boundary texels (4-neighbour outside the layer); only=set of directions."""
        dirs = {"l": (-1, 0), "r": (1, 0), "u": (0, -1), "d": (0, 1)}
        use = [dirs[k] for k in (only or "lrud")]
        hits = [p for p in self.px if any((p[0] + dx, p[1] + dy) not in self.px for dx, dy in use)]
        for p in hits:
            self.px[p] = key
        return self

    def paint(self, x0, y0, text):
        """ASCII rows: '.' keeps what is there, '_' erases, any palette key sets the texel."""
        for i, row in enumerate(text.strip("\n").split("\n")):
            for j, ch in enumerate(row.rstrip()):
                p = (x0 + j, y0 + i)
                if ch == ".":
                    continue
                if ch == "_":
                    self.px.pop(p, None)
                else:
                    self.px[p] = ch
        return self

    def rows(self, spec):
        """(y, x, keys) rows; same key semantics as paint."""
        for y, x, keys in spec:
            self.paint(x, y, keys)
        return self


# ===================================================================================================== layers
# ---------------------------------------------------------------- scarf tail hanging behind the hip (teal drape)
drape = Layer("hip-drape")
drape.poly("q", [(47, 74), (55, 76), (53, 84), (50, 90), (46, 88), (42, 92), (38, 87), (41, 80)])
drape.shade("g", [(47, 74), (55, 76), (54, 79), (45, 79)])
drape.line("Q", [(50, 78), (47, 86), (46, 88)])
drape.line("Q", [(44, 80), (41, 88)])
drape.paint(38, 88, """
q_q.
.q_q
""")

# ---------------------------------------------------------------- bedroll: teal cylinder, rolled end cap at the back
roll = Layer("bedroll")
roll.poly("g", [(34, 40), (57, 40), (58, 53), (34, 53)])
roll.shade("G", [(34, 40), (57, 40), (57, 42), (34, 42)])
roll.shade("q", [(34, 49), (58, 49), (58, 53), (34, 53)])
roll.shade("Q", [(34, 52), (58, 52), (58, 53), (34, 53)])
roll.ellipse("q", (29, 40, 39, 53))
roll.ellipse("g", (31, 42, 37, 51))
roll.paint(31, 42, """
..QQQ..
.Q.GgQ.
Q.G.qgQ
Qg.Q.gQ
Qg.Qq.Q
Qgq..gQ
.QgggQ.
..QQQ..
""")
for bx in (42, 51):                                    # two leather bindings bowing round the roll
    roll.poly("l", [(bx, 39), (bx + 2, 39), (bx + 2, 54), (bx, 54)])
    roll.line("L", [(bx, 39), (bx, 54)])
    roll.line("D", [(bx + 1, 40), (bx + 1, 42)])

# ---------------------------------------------------------------- pack: slumped canvas sack, soft flap, side bulge
pack = Layer("pack")
pack.poly("d", [(32, 54), (56, 53), (58, 58), (58, 74), (55, 78), (36, 78), (31, 74), (30, 60)])
pack.shade("D", [(31, 54), (56, 53), (57, 60), (46, 63), (33, 62)])
pack.shade("N", [(32, 54), (56, 53), (56, 55), (32, 56)])
pack.line("l", [(33, 62), (46, 63), (57, 60)])
pack.shade("n", [(40, 64), (52, 64), (55, 70), (50, 74), (41, 73)])
pack.shade("L", [(31, 74), (58, 73), (58, 78), (31, 78)])
pack.line("l", [(48, 66), (52, 72)])                   # one fold crease
pack.poly("l", [(44, 56), (46, 56), (46, 68), (44, 68)])   # flap strap
pack.paint(43, 62, """
pPPp
p..p
pPPp
""")
pack.paint(44, 63, "mm")

can = Layer("canister")                                # quiet steel bottle on the pack's visible side
can.poly("z", [(33, 61), (39, 61), (39, 72), (33, 72)])
can.shade("c", [(33, 61), (34, 61), (34, 72), (33, 72)])
can.shade("m", [(35, 61), (35, 72)])
can.shade("M", [(37, 62), (38, 62), (38, 71), (37, 71)])
can.paint(37, 63, "Z\nZ\nZ\nZ")
can.paint(34, 58, """
.mMm.
mzMzm
cmmmc
""")
can.paint(33, 66, "lllllll")
can.paint(33, 72, "ccccccc")

# ---------------------------------------------------------------- far (back) leg in the body's shadow, far boot
fleg = Layer("far-leg")
fleg.poly("T", [(56, 84), (68, 86), (66, 98), (62, 106), (59, 114), (48, 114), (50, 106), (54, 98)])
fleg.shade("C", [(56, 84), (59, 84), (56, 98), (52, 106), (50, 114), (48, 114), (50, 104), (54, 96)])
fleg.shade("t", [(66, 86), (68, 86), (66, 98), (62, 106), (59, 114), (57, 114), (60, 105), (64, 97)])
fleg.line("C", [(56, 100), (62, 101)])                 # knee crease
fboot = Layer("far-boot")
fboot.poly("d", [(48, 112), (59, 112), (59, 121), (61, 124), (63, 128), (63, 135), (54, 135), (54, 133), (48, 133),
                 (48, 135), (41, 135), (41, 130), (43, 125), (47, 121)])
fboot.shade("n", [(54, 113), (60, 113), (60, 121), (63, 125), (64, 128), (57, 127), (55, 121)])
fboot.shade("D", [(58, 121), (61, 123), (64, 127), (65, 130), (60, 129)])
fboot.shade("L", [(40, 132), (65, 132), (65, 135), (40, 135)])
fboot.shade("L", [(40, 128), (44, 128), (44, 135), (40, 135)])
fboot.paint(47, 112, "LdnnnnnnndLL\nlDNNNNNNDDl.")    # turned cuff lip
fboot.paint(47, 117, "LLLLLLLLLLLLL")              # ankle strap
fboot.paint(55, 117, "mM")

# ---------------------------------------------------------------- coat back tail (split skirt behind the far leg line)
tail = Layer("coat-tail")
tail.poly("e", [(52, 78), (65, 78), (65, 92), (59, 104), (52, 108), (44, 111), (36, 109), (38, 102), (44, 92), (48, 84)])
tail.shade("C", [(48, 80), (52, 80), (44, 96), (40, 106), (37, 106), (42, 96)])
tail.shade("c", [(60, 79), (65, 79), (65, 92), (60, 102), (57, 102), (61, 91)])
tail.line("C", [(56, 82), (50, 98), (47, 108)])        # two long folds
tail.line("C", [(61, 86), (56, 100)])
tail.line("o", [(62, 82), (58, 96)])
tail.line("l", [(36, 109), (44, 111), (52, 108), (59, 104)])   # leather hem binding

# ---------------------------------------------------------------- near (front) leg: thigh, steel knee pad, shin, boot
nleg = Layer("near-leg")
nleg.poly("T", [(74, 86), (90, 86), (94, 96), (93, 104), (90, 113), (78, 113), (78, 104), (75, 96)])
nleg.shade("C", [(74, 86), (77, 86), (78, 100), (80, 113), (78, 113), (77, 104), (75, 96)])
nleg.shade("t", [(84, 86), (90, 86), (94, 96), (93, 104), (90, 113), (86, 113), (89, 104), (89, 95)])
nleg.shade("v", [(89, 88), (91, 88), (93, 96), (91, 97)])
nleg.line("C", [(80, 98), (86, 99)])
nleg.line("t", [(81, 106), (85, 112)])
nleg.paint(86, 95, """
.KKKKK.
KmMMMmK
KmMZMmK
KlmMmlK
KlmmmlK
.KmmmK.
..KKK..
""")
nboot = Layer("near-boot")
nboot.poly("d", [(78, 112), (89, 112), (89, 120), (93, 123), (97, 126), (99, 130), (99, 135), (88, 135), (88, 133),
                 (81, 133), (81, 135), (74, 135), (74, 129), (76, 124), (78, 120)])
nboot.shade("D", [(84, 113), (90, 113), (90, 120), (94, 123), (97, 126), (98, 129), (88, 128), (86, 121)])
nboot.shade("N", [(91, 122), (95, 124), (98, 128), (94, 128)])
nboot.shade("n", [(76, 121), (86, 121), (88, 128), (77, 128)])
nboot.shade("L", [(73, 132), (99, 132), (99, 135), (73, 135)])
nboot.shade("L", [(73, 128), (77, 128), (77, 135), (73, 135)])
nboot.paint(77, 112, "LdnnnnnnnDDdL\nlDNNNNNNNNNDl")    # turned cuff lip
nboot.paint(77, 117, "LLLLLLLLLLLLL")
nboot.paint(86, 116, "KMMK\nKmmK")                  # strap buckle
nboot.paint(82, 131, "nnnnnnnnnnnnnnnn")            # lit welt edge above the forefoot sole

# ---------------------------------------------------------------- coat: torso and front skirt panel (storm slate)
coat = Layer("coat")
coat.poly("c", [(55, 43), (66, 41), (75, 44), (85, 46), (90, 52), (91, 77), (52, 79), (53, 62), (54, 48)])
coat.poly("c", [(64, 78), (91, 77), (93, 85), (93, 92), (86, 96), (73, 97), (65, 94)])
coat.shade("e", [(53, 46), (60, 44), (60, 79), (52, 79)])
coat.shade("C", [(53, 50), (56, 50), (56, 79), (52, 79)])
coat.shade("o", [(80, 46), (86, 46), (91, 52), (91, 77), (86, 77), (86, 56)])
coat.shade("o", [(86, 80), (91, 79), (93, 85), (93, 92), (89, 93), (88, 86)])
coat.line("O", [(66, 42), (75, 44), (85, 46)])          # lit shoulder seam
coat.line("O", [(92, 84), (93, 91)])
coat.line("e", [(70, 82), (68, 94)])                   # skirt folds
coat.line("e", [(78, 84), (77, 96)])
coat.line("l", [(65, 95), (73, 97), (86, 96), (93, 92)])   # leather hem binding
shirt = Layer("shirt")
shirt.poly("W", [(77, 50), (88, 49), (90, 56), (90, 76), (77, 76), (79, 62)])
shirt.shade("w", [(77, 50), (80, 50), (81, 62), (79, 76), (77, 76), (79, 62)])
shirt.line("f", [(82, 66), (84, 75)])
shirt.line("w", [(86, 66), (88, 75)])
shirt.paint(82, 51, """
p.p
.p.
p.p
.p.
p.p
""")
shirt.line("O", [(76, 50), (78, 62), (76, 76)])          # coat lapel edge in light
belt = Layer("belt")
belt.poly("L", [(52, 76), (91, 75), (91, 80), (52, 81)])
belt.line("l", [(52, 76), (91, 75)])
belt.paint(70, 75, """
PPPPP
P.m.P
P.m.P
PPPPP
""")
belt.paint(71, 76, "LmL\nLmL")
belt.poly("D", [(55, 80), (62, 80), (62, 87), (55, 87)])   # small pouch at the back hip
belt.line("d", [(55, 87), (62, 87)])
belt.line("N", [(55, 80), (62, 80)])
belt.paint(57, 82, "lPl")

# ---------------------------------------------------------------- raised coat collar standing behind the nape
collar = Layer("collar")
collar.poly("o", [(57, 40), (60, 35), (64, 34), (67, 38), (67, 45), (59, 46)])
collar.shade("c", [(57, 40), (60, 35), (61, 35), (60, 46), (57, 46)])
collar.line("O", [(60, 35), (64, 34)])
collar.line("e", [(65, 37), (65, 45)])

# ---------------------------------------------------------------- ponytail (behind the head)
pony = Layer("ponytail")
pony.poly("2", [(62, 21), (60, 15), (56, 9), (50, 4), (44, 3), (39, 6), (36, 11), (34, 17), (33, 24), (34, 30),
                (37, 35), (39, 30), (41, 24), (44, 18), (49, 14), (54, 15), (58, 21)])
pony.shade("1", [(33, 20), (40, 18), (44, 18), (41, 26), (39, 31), (37, 35), (33, 28)])
pony.shade("3", [(42, 5), (50, 5), (56, 10), (52, 11), (46, 9), (40, 11), (37, 15)])
pony.shade("a", [(45, 4), (51, 5), (55, 9), (50, 8), (45, 7)])
pony.line("1", [(55, 13), (48, 9), (42, 11), (38, 17), (36, 25)])
pony.line("4", [(53, 7), (47, 6), (41, 9)])
pony.line("h", [(49, 5), (45, 5)])
pony.line("3", [(57, 17), (51, 12), (45, 13), (41, 18), (38, 26), (38, 31)])
pony.line("1", [(60, 18), (54, 16), (48, 16), (44, 21), (40, 30)])

lock = Layer("loose-lock")     # thin lock falling from the tie behind the head
lock.poly("2", [(58, 20), (55, 20), (52, 25), (50, 31), (51, 33), (53, 28), (56, 23)])
lock.line("3", [(56, 21), (53, 26), (51, 31)])

# ---------------------------------------------------------------- head: hair mass, bangs, ear, face (hand-typed)
# x54..x94, y14..y44.  Light from the upper right (front).  Near eye x81-85, far eye x88, nose tip x91, chin y39.
head = Layer("head")
# crown and bangs roots, y14..y23 (row strings start at x54)
head.paint(54, 14, """
..............22333443322
...........12233344444443322
.........112233344444hhh443322
........1122334444hhh444hh43322
.......111223444hh44334444hh4322
......11122334hh443323344444h4322
.....1112233hh4433221344h43134h432
....111122344332233212344h3124h4322
....111122233223321221344134h13h412
...11112222332233221112341244124h132
""")
# back of the head: strands pulled up-left toward the tie, y24..y40, x54..x71 (back edge column given per row)
BACK_HAIR = [(24, 3, "122332123321232"), (25, 2, "1122332123321232"), (26, 2, "1122233212332123"),
             (27, 2, "1112223321233212"), (28, 2, "1112222332123321"), (29, 2, "1111222233212332"),
             (30, 2, "1111222223321233"), (31, 2, "1111122222332123"), (32, 3, "111122222332122"),
             (33, 3, "111112222233212"), (34, 4, "11112222233212"), (35, 5, "1111222223321"),
             (36, 6, "111122222332"), (37, 7, "11112222321"), (38, 8, "1111222321"), (39, 9, "111122321"),
             (40, 10, "11112221")]
for y, r, keys in BACK_HAIR:
    assert r + len(keys) == 18, (y, r, keys)
    head.rows([(y, 54 + r, keys)])
# face, bangs tips, side lock and ear: 23 texels per row from x72 (r18) to x94; '_' = clear
FACE = {
    24: "222134313413h414h3K____",   # swept bang locks, separations x75 x78 x82 (tips point down-right)
    25: "2211232123S232SS2Sk____",   # zig-zag hairline: forehead shows between the lock tips
    26: "211113212SSS1SSSSSSk___",
    27: "2211132sSSS332SSS32k___",   # near brow arch x81-83, far brow x89-90 (mid hair brown)
    28: "1221132sS33SSS2SSSk____",   # near brow outer tail x79-80, inner end x86
    29: "1jjs132sSEEEEESSEEk____",   # ear top x73-75; lash line x81-85; far lash x88-89
    30: "1sxs132jEyybbkSSybSk___",   # outer lash flick x80, whites x81-82, upper iris x83-84, inner corner x85
    31: "1xks132jSjyEiSSSSxSSk__",   # white x82, pupil x83, lower iris x84; nose bridge to x91
    32: "1sxs132sSSjijSSSSSSSk__",   # lower iris rim x83 between lid shades; nose tip x91, profile x92
    33: "1jsx122sSSSSSSSSSSxk___",   # nostril shade x90
    34: "21xs121sSSSSSSSSSSsk___",
    35: "211x121sSSSSSSSSkrSk___",   # mouth corner x88, lip x89
    36: "221112kxsSSSSSSSSjk____",   # lower lip shade x89; jaw corner x78 behind the side lock
    37: "22111xxxksSSSSSSSk_____",   # jaw line runs down-right to the chin
    38: "11kxxxxxsskkjSSSk______",
    39: "1kxxxxsssjsxkkkk_______",   # chin underside x84-87
    40: "1kxxxsssssxk___________",   # neck (scarf covers y41+)
    41: "1kxxxsssssxk___________",
    42: "1kxxxsssssxk___________",
    43: "1kxxxsssssxk___________",
}
for y, keys in FACE.items():
    assert len(keys) == 23, (y, len(keys))
    head.rows([(y, 72, keys)])

# ---------------------------------------------------------------- v17r1 facial finishing (head layer only, R1_EDIT_BOX)
# Bangs: three coherent locks instead of per-column 1/3/4 stripes - A temple lock (roots x74-80) sweeping down-left into
# the side lock in front of the ear, a short centre lock M (tip x84-85 on y25), and a front lock B down the profile (tip
# x89-90 on y26); forehead shows between them. Each lock: dark edge on its shadow side, warm mid body, light/sheen on top.
# Eye: near brow on y27 only, clear skin row y28, upper lash y29 (3 black texels tapered by deep skin / dark iris),
# white both sides of a 2-texel iris with the pupil under the lash (looking forward-right), soft lower lid y32.
# Profile: brow ridge x91 -> bridge -> rounded tip x92 (y31-32) -> under-nose x91 -> upper lip / mouth / lower lip ->
# rounded chin (x89 y38) instead of the v17 triangular nose and stepped receding chin.
R1_ROWS = {   # y: (x0, keys); 23 keys from x72 (= x72..x94) unless noted; '_' clears
    18: (70, "hh444a4444hh4322"),
    19: (70, "444a3a4444hhh4322"),
    20: (72, "3a44hh44a3234h42_______"),
    21: (72, "23a44hh4a3234h243______"),
    22: (72, "233a44h4a234h324a______"),
    23: (72, "1233a4h4a234h32343_____"),
    24: (72, "223a4h4a2SS243S2433____"),   # forehead windows x81-82 and x86
    25: (72, "1223a4a2SSSS32SS243____"),   # M tip x84-85; B x88-90
    26: (72, "211223a2SSSSSSSSS23k___"),   # A tip x79, B tip x89-90, forehead profile x91
    27: (72, "211123asS33222SS32Sk___"),   # near brow x81-85 (inner end darker), far brow x88-89
    28: (72, "122123asSSSSSSSSSSSk___"),   # clear skin row between brows and lashes
    29: (72, "1jjs23asSkEEEbSSbESk___"),   # near lash x81-85 (k taper, EEE, b), far lash x88-89
    30: (72, "1sxs23ajbyybEySSybSk___"),   # whites x81-82 + x85, upper iris x83, pupil x84; far eye x88-89
    31: (72, "1xks23ajSjyiijSSSSSSk__"),   # lower iris x83-84; bridge reaches x92
    32: (72, "1sxs23asSSjjjSSSSSSSk__"),   # soft lower lid x82-84; nose tip x92
    33: (72, "1jsx23sSSSSSSSSSSSxk___"),   # nostril shade x90, under-nose x91
    34: (72, "21xs23sSSSSSSSSSSSsk___"),
    35: (72, "221x23sSSSSSSSSSSrrk___"),   # upper lip x89-90
    36: (72, "221122kxsSSSSSSxkkk____"),   # soft mouth corner x87, mouth line x88-89, profile x90
    37: (72, "22111xxxksSSSSSSrrk____"),   # lower lip x88-89
    38: (72, "11kxxxxxsskkjSSjjk_____"),   # lip shadow x87-88, chin front x89
    39: (72, "1kxxxxsssjsxkkkkk______"),   # chin underside x84-88
}
for y, (x0, keys) in R1_ROWS.items():
    assert R1_EDIT_BOX[0] <= x0 and x0 + len(keys) <= R1_EDIT_BOX[2] and R1_EDIT_BOX[1] <= y < R1_EDIT_BOX[3], (y, x0)
    assert x0 != 72 or len(keys) == 23, (y, len(keys))
    head.rows([(y, x0, keys)])

tie = Layer("hair-tie")
tie.paint(59, 15, """
.KK.
KlNK
KLlK
KlNK
.KK.
""")


# ---------------------------------------------------------------- near arm: storm-slate sleeve, rolled beige cuff, forearm
arm = Layer("near-arm")
arm.poly("c", [(62, 46), (74, 46), (78, 52), (79, 62), (75, 67), (66, 67), (62, 58)])
arm.shade("o", [(70, 46), (74, 46), (78, 52), (79, 62), (76, 63), (75, 52)])
arm.shade("e", [(62, 52), (65, 52), (67, 66), (64, 66), (62, 58)])
arm.line("O", [(66, 46), (74, 46), (77, 50)])
arm.edge("C", only="ld")
arm.line("e", [(68, 58), (74, 62)])                    # elbow fold
arm.poly("P", [(75, 57), (80, 56), (82, 64), (77, 67)])    # rolled cuff
arm.line("p", [(76, 61), (81, 60)])
arm.line("p", [(77, 66), (81, 64)])
arm.poly("s", [(80, 56), (87, 54), (87, 62), (82, 64)])    # forearm
arm.shade("S", [(81, 56), (88, 54), (88, 57), (82, 59)])
arm.line("x", [(82, 64), (89, 62)])

# ---------------------------------------------------------------- teal scarf: two wraps round the neck, knot under the chin
# (drawn over the sleeve top: the scarf sits on the shoulders, the upper arm hangs below it)
scarf_low = Layer("scarf-lower-wrap")
scarf_low.poly("q", [(61, 46), (70, 48), (80, 50), (87, 49), (88, 53), (80, 55), (70, 54), (62, 52)])
scarf_low.edge("Q", only="d")
scarf_low.edge("g", only="u")
scarf_low.line("Q", [(69, 48), (71, 53)])
scarf_low.line("Q", [(77, 50), (78, 54)])
scarf_up = Layer("scarf-upper-wrap")
scarf_up.poly("g", [(63, 41), (72, 40), (80, 41), (86, 43), (86, 48), (80, 48), (70, 46), (61, 46)])
scarf_up.edge("q", only="d")
scarf_up.edge("G", only="u")
scarf_up.shade("G", [(71, 41), (79, 42), (79, 43), (71, 42)])
scarf_up.line("q", [(67, 42), (69, 46)])
scarf_up.line("q", [(76, 42), (78, 47)])
knot = Layer("scarf-knot")
knot.ellipse("g", (80, 44, 88, 52))
knot.edge("Q", only="dl")
knot.paint(83, 45, "GG\nGgG\n.Gg")
knot.poly("q", [(82, 51), (87, 51), (87, 56), (85, 58), (83, 56)])     # short tail over the chest
knot.line("g", [(85, 52), (85, 56)])
knot.line("Q", [(82, 52), (83, 56)])

# ---------------------------------------------------------------- short blade raised forward, steel crossguard
blade = Layer("sword-blade")
blade.line("M", [(98, 52), (119, 34)], width=4)
blade.line("Z", [(97, 50), (118, 32)])
blade.line("z", [(100, 53), (120, 36)])
blade.paint(118, 31, "_Z\nZM")
guard = Layer("sword-guard")
guard.line("m", [(93, 49), (101, 58)], width=3)
guard.line("M", [(94, 49), (101, 57)])
guard.line("L", [(95, 56), (87, 64)], width=2)          # grip below the hands
guard.paint(83, 64, "mM\nmm")

# ---------------------------------------------------------------- two fingerless-gloved hands closed round the grip
hands = Layer("hands")
hands.paint(85, 52, """
...KKKKK....
..KlDDDlKK..
.KlDNNDlsSK.
KLlDDDllsSsK
KLlllllsxSsK
KLLLllsSxssK
.KKKKKxssxK.
KLlDDDlsSsK.
KLlDDllsxsK.
KLLlllsSxsK.
.KLLLlsssK..
..KKKKKKK...
""")


# ===================================================================================================== raster
def hex_rgb(h):
    return tuple(int(h[i:i + 2], 16) for i in (1, 3, 5))


def compose(layers=None):
    """Returns ({layer: key grid}, key grid) after the silhouette outline pass. Key grid: H x W array of str ('' = clear)."""
    grids = {}
    comp = np.full((H, W), "", dtype="<U1")
    for lay in (layers or LAYERS):
        g = np.full((H, W), "", dtype="<U1")
        for (x, y), ch in lay.px.items():
            if ch not in PALETTE:
                raise SystemExit(f"{lay.name}: unknown key {ch!r} at x{x} y{y}")
            if not (0 <= x < W and 0 <= y < H):
                raise SystemExit(f"{lay.name}: texel ({x},{y}) outside the cell")
            g[y, x] = ch
        grids[lay.name] = g
        m = g != ""
        comp[m] = g[m]
    op = comp != ""
    pad = np.pad(op, 1, constant_values=False)
    edge = op & ~(pad[:-2, 1:-1] & pad[2:, 1:-1] & pad[1:-1, :-2] & pad[1:-1, 2:])
    keep = np.isin(comp, list(EDGE_KEEP))
    comp[edge & ~keep] = "K"
    return grids, comp


def to_rgba(grid):
    a = np.zeros((H, W, 4), np.uint8)
    for k, v in PALETTE.items():
        m = grid == k
        a[m, :3] = hex_rgb(v)
        a[m, 3] = 255
    return a


def render():
    grids, comp = compose()
    return {n: to_rgba(g) for n, g in grids.items()}, to_rgba(comp)


def png_bytes(rgba):
    buf = io.BytesIO()
    Image.fromarray(rgba, "RGBA").save(buf, "PNG", optimize=False, compress_level=9)
    return buf.getvalue()


def on_bg(rgba, bg, zoom):
    im = Image.new("RGBA", (rgba.shape[1], rgba.shape[0]), bg + (255,))
    im.alpha_composite(Image.fromarray(rgba, "RGBA"))
    return im.resize((im.width * zoom, im.height * zoom), Image.NEAREST)


def preview(out):
    os.makedirs(out, exist_ok=True)
    _, comp = render()
    for name, bg in (("mid", (120, 130, 140)), ("dark", (40, 36, 44)), ("light", (205, 200, 190))):
        on_bg(comp, bg, 6).save(os.path.join(out, f"v17-full-x6-{name}.png"))
    head = comp[8:48, 50:100]
    on_bg(np.ascontiguousarray(head), (120, 130, 140), 14).save(os.path.join(out, "v17-head-x14.png"))
    on_bg(comp, (120, 130, 140), 2).save(os.path.join(out, "v17-full-x2.png"))
    print("PREVIEW", out)


# ===================================================================================================== build / check
V16_KEYS = set("K1234hSsxECcoTtWwPpLldDQqgGmMZuen")
NEW_KEYS = [k for k in PALETTE if k not in V16_KEYS]
HEAD_BOX = (52, 12, 96, 48)            # x0, y0, x1, y1 (exclusive): head, neck and scarf top, cut from the composite
FACE_BOX = (72, 22, 95, 44)            # native face region (side lock, ear, skin, features)
V16_FACE_BOX = (36, 11, 48, 22)        # the same region in v16's logical texels
SUBJECT = "female-battle-idle-right"
WIN_LONG_PREFIX = "\\\\?\\"


def fid(role):
    return hashlib.sha256(f"{RUN_ID}:{role}".encode()).hexdigest()[:8]


NAMES = {
    "png": f"{SLUG}_{SUBJECT}_dense-native136_{VER}_{STAMP}-{fid('png')}.png",
    "head": f"{SLUG}_{SUBJECT}_dense-head-native_{VER}_{STAMP}-{fid('head')}.png",
    "ora": f"{SLUG}_{SUBJECT}_dense-layers_{VER}_{STAMP}-{fid('ora')}.ora",
    "inspect_full": f"{SLUG}_{SUBJECT}_dense-inspect-full-x4_{VER}_{STAMP}-{fid('inspect_full')}.png",
    "inspect_head": f"{SLUG}_{SUBJECT}_dense-inspect-head-x8_{VER}_{STAMP}-{fid('inspect_head')}.png",
    "manifest": f"{SLUG}_{SUBJECT}_dense-manifest_{VER}_{STAMP}-{fid('manifest')}.json",
    "check": f"{SLUG}_{SUBJECT}_dense-check-report_{VER}_{STAMP}-{fid('check')}.json",
}


def fs(path):
    path = os.path.abspath(path)
    return WIN_LONG_PREFIX + path if os.name == "nt" and len(path) > 240 else path


def sha(data):
    return hashlib.sha256(data).hexdigest()


def outline_layer(grids, comp):
    pre = np.full((H, W), "", dtype="<U1")
    for lay in LAYERS:
        g = grids[lay.name]
        pre[g != ""] = g[g != ""]
    g = np.full((H, W), "", dtype="<U1")
    g[pre != comp] = comp[pre != comp]
    return g


def ora_bytes(grids, comp):
    """OpenRaster: every authored layer bottom->top plus the silhouette 'outline' layer on top (stacking = the PNG)."""
    order = [lay.name for lay in LAYERS] + ["outline"]
    stack = dict(grids)
    stack["outline"] = outline_layer(grids, comp)
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w") as z:
        def put(name, data, method=zipfile.ZIP_DEFLATED):
            info = zipfile.ZipInfo(name, date_time=(1980, 1, 1, 0, 0, 0))
            info.compress_type = method
            z.writestr(info, data)
        put("mimetype", b"image/openraster", zipfile.ZIP_STORED)
        xml = [f'<?xml version="1.0" encoding="UTF-8"?>\n<image version="0.0.3" w="{W}" h="{H}">\n<stack>']
        for i, name in enumerate(reversed(order)):
            xml.append(f'<layer name="{name}" src="data/{len(order) - 1 - i:02d}-{name}.png" x="0" y="0" '
                       f'opacity="1.0" visibility="visible"/>')
        xml.append("</stack>\n</image>\n")
        put("stack.xml", "\n".join(xml).encode())
        for i, name in enumerate(order):
            put(f"data/{i:02d}-{name}.png", png_bytes(to_rgba(stack[name])))
        put("mergedimage.png", png_bytes(to_rgba(comp)))
    return buf.getvalue()


def decode(data):
    return np.array(Image.open(io.BytesIO(data)).convert("RGBA"))


def head_crop(rgba):
    x0, y0, x1, y1 = HEAD_BOX
    return np.ascontiguousarray(rgba[y0:y1, x0:x1])


def build_files():
    grids, comp = compose()
    rgba = to_rgba(comp)
    files = {
        "png": png_bytes(rgba),
        "head": png_bytes(head_crop(rgba)),
        "ora": ora_bytes(grids, comp),
    }
    full = on_bg(rgba, (120, 130, 140), 4)
    buf = io.BytesIO(); full.save(buf, "PNG"); files["inspect_full"] = buf.getvalue()
    hv = on_bg(head_crop(rgba), (120, 130, 140), 8)
    buf = io.BytesIO(); hv.save(buf, "PNG"); files["inspect_head"] = buf.getvalue()
    used = {k: int((comp == k).sum()) for k in PALETTE if (comp == k).any()}
    manifest = {
        "status": "UNAPPROVED test-only v17r1 facial finishing pass over the frozen v17 density prototype (static still). "
                  "Not art approval, not runtime adoption, no animation, no default change.",
        "creatorVerdictAnswered": "this is just way too coarse, her face is not even recognizable (v16, 2026-10-18 22:01)",
        "rootReviewAnswered": "v17 density method real; eye/brow too heavily clustered, bangs too stripe-like (coarse-face "
                              "rejection follow-up, 2026-10-18)",
        "v17r1Scope": {"editedLayer": "head", "headEditBox": list(R1_EDIT_BOX), "compositeChangeBox": list(R1_COMP_BOX),
                       "frozenV17Png": {"name": V17_PNG, "sha256": V17_FROZEN[V17_PNG]},
                       "frozenV17Ora": {"name": V17_ORA, "sha256": V17_FROZEN[V17_ORA]},
                       "otherLayers": "byte-identical to the frozen v17 ORA layers (check gate)"},
        "method": "new hand-placed native 136x144 pixel art (2 texels per logical pixel) for the same logical 68x72 "
                  "battle extent; ASCII rows + non-antialiased polygon/ellipse/line fills + hand-typed detail rows; no "
                  "resampling, filtering, dithering, noise, generation or upscaling; v16 not used as pixel input",
        "cell": [W, H], "logicalExtent": list(LOGICAL), "nativePin": list(PIN), "logicalPin": [PIN[0] // 2, PIN[1] // 2],
        "displayRequirement": "draw_texture_rect(texture, Rect2(round(x)-32, 272-68, 68, 72)) with nearest filtering; "
                              "the 0.65 battle proportion is already baked into the 68x72 logical extent (not applied "
                              "again). The current game's draw_texture() would draw this file at double size: adopting "
                              "it needs that one draw-call change (not made).",
        "palette": PALETTE, "paletteUsedCount": len(used), "paletteLimit": 48, "keyTexelCounts": used,
        "disclosedNewKeysVsV16": {k: PALETTE[k] for k in NEW_KEYS},
        "layers": [{"name": lay.name, "texels": len(lay.px)} for lay in LAYERS] + [
            {"name": "outline", "texels": int((outline_layer(grids, comp) != "").sum()),
             "note": "silhouette pass: edge texels become K (skin profile keeps k); stored as its own ORA layer"}],
        "headBox": list(HEAD_BOX), "faceBox": list(FACE_BOX),
        "files": {k: {"name": NAMES[k], "sha256": sha(v)} for k, v in files.items()},
        "rgbaSha256": sha(rgba.tobytes()),
        "tool": {"file": "tools/" + os.path.basename(os.path.abspath(__file__))},
        "inspectionZoomsNote": "inspect-* files are nearest-neighbour zooms on a flat grey for root viewing only; they "
                               "are not runtime art and are not the density evidence (the 1280 captures are)",
        "knownLimitations": [
            "body unchanged from v17 by design: boots are still heavy blocks; coat torso planes are broad; gloved hands "
            "are a compact mass; back hair mass is dark",
            "the face is still small at the normal 1280 size (about 20x16 physical px of skin); expression neutral",
            "the blade tip overlaps the next party member in the normal four-person layout (unchanged from v16)",
            "at the native 640x360 compatibility path nearest sampling keeps 1 of 4 native texels: thin 1-texel "
            "lines (outline, lash, brow) can drop out there",
        ],
    }
    files["manifest"] = (json.dumps(manifest, indent=1, ensure_ascii=False) + "\n").encode()
    return files, grids, comp


def build():
    out = os.path.join(REPO, OUT_DIR_REL)
    files, _, _ = build_files()
    os.makedirs(fs(out), exist_ok=True)
    for k, data in files.items():
        path = os.path.join(out, NAMES[k])
        if os.path.exists(fs(path)):
            if open(fs(path), "rb").read() != data:
                raise SystemExit(f"refusing to overwrite a different {path}")
            continue
        with open(fs(path), "wb") as f:
            f.write(data)
    print("BUILD OK", OUT_DIR_REL, {k: sha(v)[:12] for k, v in files.items()})


def check():
    out = os.path.join(REPO, OUT_DIR_REL)
    results, info = [], {}

    def gate(name, ok, detail=None):
        results.append({"gate": name, "pass": bool(ok), "detail": detail})

    files, grids, comp = build_files()
    disk = {}
    for k in files:
        path = os.path.join(out, NAMES[k])
        disk[k] = open(fs(path), "rb").read() if os.path.exists(fs(path)) else None
    for k in ("png", "head", "ora", "manifest"):
        gate(f"built {k} equals this tool's deterministic output", disk[k] == files[k], NAMES[k])
    png = decode(disk["png"])
    gate("native cell 136x144", png.shape[:2] == (H, W), list(png.shape))
    gate("binary alpha (no antialias fringe)", set(np.unique(png[..., 3]).tolist()) <= {0, 255})
    op = png[..., 3] == 255
    pal = {hex_rgb(v): k for k, v in PALETTE.items()}
    rgb = [tuple(c) for c in png[op][:, :3].tolist()]
    off = sorted({c for c in rgb if c not in pal})
    used = sorted({pal[c] for c in rgb if c in pal})
    gate("every opaque texel is a palette colour", not off, [list(c) for c in off][:5])
    gate("palette used <= 48 colours", len(used) <= 48, {"used": len(used), "keys": "".join(used)})
    info["newKeysUsed"] = [k for k in NEW_KEYS if k in used]
    pad = np.pad(op, 1, constant_values=False)
    edge = op & ~(pad[:-2, 1:-1] & pad[2:, 1:-1] & pad[1:-1, :-2] & pad[1:-1, 2:])
    edge_keys = sorted({pal[tuple(c)] for c in png[edge][:, :3].tolist()})
    gate("silhouette edge is the outline K or the deep skin profile k only (no halo / rim / neon)",
         set(edge_keys) <= {"K", "k"}, edge_keys)
    gate("rows 136..143 transparent (soles end on row 135)", not op[136:].any() and op[135].any())
    xs135 = np.nonzero(op[135])[0]
    gate("pin (64,136) transparent; feet on both sides of x64 on row 135",
         not op[136, 64] and not op[135, 64] and (xs135 < 64).any() and (xs135 > 64).any(), xs135.tolist())
    ys, xs = np.nonzero(op)
    b17 = [int(xs.min()), int(ys.min()), int(xs.max()), int(ys.max())]
    v16_bytes = open(fs(os.path.join(REPO, V16_PNG_REL)), "rb").read()
    gate("v16 PNG present and unchanged (protected evidence)", sha(v16_bytes) == V16_PNG_SHA, sha(v16_bytes)[:16])
    v16 = decode(v16_bytes)
    op16 = v16[..., 3] == 255
    ys16, xs16 = np.nonzero(op16)
    b16 = [int(xs16.min()), int(ys16.min()), int(xs16.max()), int(ys16.max())]
    b17_logical = [b17[0] / 2, b17[1] / 2, (b17[2] + 1) / 2 - 1, (b17[3] + 1) / 2 - 1]
    delta = [round(a - b, 2) for a, b in zip(b17_logical, b16)]
    gate("same apparent bounds as v16 (every bbox edge within 2 logical px)", all(abs(d) <= 2 for d in delta),
         {"v17NativeInclusive": b17, "v17Logical": b17_logical, "v16LogicalInclusive": b16, "deltaLogical": delta})
    blocks = png.reshape(H // 2, 2, W // 2, 2, 4).transpose(0, 2, 1, 3, 4).reshape(H // 2, W // 2, 4, 4)
    full = (blocks[..., 3] == 255).all(axis=2)
    nonuni = np.array([[len({tuple(t) for t in blocks[i, j, :, :3].tolist()}) > 1 for j in range(W // 2)]
                       for i in range(H // 2)])
    n_full, n_non = int(full.sum()), int((full & nonuni).sum())
    up16 = np.repeat(np.repeat(v16, 2, axis=0), 2, axis=1)
    both = op & (up16[..., 3] == 255)
    same = int((both & (png[..., :3] == up16[..., :3]).all(axis=2)).sum())
    info["density"] = {"opaqueTexels": int(op.sum()), "v16OpaqueTexels": int(op16.sum()),
                       "fullyOpaque2x2Blocks": n_full, "nonUniform2x2Blocks": n_non,
                       "nonUniformShare": round(n_non / max(n_full, 1), 4),
                       "texelsEqualToNearestUpscaledV16": same, "texelsOpaqueInBoth": int(both.sum()),
                       "equalShare": round(same / max(int(both.sum()), 1), 4)}
    gate("not a nearest-neighbour upscale: >= 25% of fully opaque 2x2 blocks carry sub-logical detail",
         n_non / max(n_full, 1) >= 0.25, info["density"])
    gate("not v16 re-used: < 50% of shared opaque texels equal the nearest-upscaled v16",
         same / max(int(both.sum()), 1) < 0.5, info["density"]["equalShare"])
    fx0, fy0, fx1, fy1 = FACE_BOX
    face = png[fy0:fy1, fx0:fx1]
    fop = face[..., 3] == 255
    face_cols = {tuple(c) for c in face[fop][:, :3].tolist()}
    gx0, gy0, gx1, gy1 = V16_FACE_BOX
    f16 = v16[gy0:gy1, gx0:gx1]
    f16op = f16[..., 3] == 255
    f16_cols = {tuple(c) for c in f16[f16op][:, :3].tolist()}
    info["face"] = {"v17NativeFaceTexels": int(fop.sum()), "v17FaceColours": len(face_cols),
                    "v16LogicalFaceTexels": int(f16op.sum()), "v16FaceColours": len(f16_cols),
                    "v17FeatureKeys": "".join(sorted({pal[c] for c in face_cols}))}
    gate("face carries distinct eye white, iris, pupil/lash, lip and deep skin keys",
         {"y", "i", "b", "E", "r", "k", "S"} <= {pal[c] for c in face_cols}, info["face"])
    gate("head PNG equals the composite crop", np.array_equal(decode(disk["head"]), head_crop(png)), list(HEAD_BOX))
    z = zipfile.ZipFile(io.BytesIO(disk["ora"]))
    names = z.namelist()
    gate("ora mimetype stored first", names[0] == "mimetype" and z.read("mimetype") == b"image/openraster")
    stack = np.zeros((H, W, 4), np.uint8)
    layer_files = sorted(n for n in names if n.startswith("data/"))
    for n in layer_files:
        a = decode(z.read(n))
        m = a[..., 3] == 255
        stack[m] = a[m]
    gate("ora layers stacked bottom->top equal the PNG exactly", np.array_equal(stack, png),
         {"layers": len(layer_files)})
    gate("ora mergedimage equals the PNG", np.array_equal(decode(z.read("mergedimage.png")), png))
    game_writes = [n for n in os.listdir(fs(out)) if n.endswith((".gd", ".tscn", ".import", ".godot"))]
    gate("nothing game-side written to the output folder", not game_writes, game_writes)

    # ---------------------------------------------------------------- v17r1 scope gates (frozen v17 is the reference)
    v17dir = os.path.join(REPO, V17_DIR_REL)
    frozen = {n: sha(open(fs(os.path.join(v17dir, n)), "rb").read()) if os.path.exists(fs(os.path.join(v17dir, n)))
              else None for n in V17_FROZEN}
    gate("frozen v17 files present and unchanged (PNG, ORA, head, manifest, check report, measure reports 62/72 + r2)",
         all(frozen[n] == V17_FROZEN[n] for n in V17_FROZEN), {n[-60:]: (frozen[n] or "MISSING")[:16] for n in frozen})
    z17 = zipfile.ZipFile(io.BytesIO(open(fs(os.path.join(v17dir, V17_ORA)), "rb").read()))
    l17 = sorted(n for n in z17.namelist() if n.startswith("data/"))
    gate("same ORA layer names and stacking order as frozen v17", l17 == layer_files, {"v17": len(l17), "r1": len(layer_files)})
    x0, y0, x1, y1 = R1_EDIT_BOX
    cx0, cy0, cx1, cy1 = R1_COMP_BOX
    inside_edit = np.zeros((H, W), bool); inside_edit[y0:y1, x0:x1] = True
    inside_comp = np.zeros((H, W), bool); inside_comp[cy0:cy1, cx0:cx1] = True
    body_same, layer_diffs = [], {}
    for n in layer_files:
        a17, a1 = decode(z17.read(n)), decode(z.read(n))
        d = (a17 != a1).any(axis=2)
        layer_diffs[n] = int(d.sum())
        if not n.endswith(("-head.png", "-outline.png")):
            body_same.append(z17.read(n) == z.read(n) and not d.any())
    gate("every non-head authored layer (23 of 24) is byte-identical to frozen v17 (body/boots/coat/gear/arm/scarf/blade/"
         "hands/ponytail/tie)", len(body_same) == len(layer_files) - 2 and all(body_same),
         {k[5:]: v for k, v in layer_diffs.items() if v})
    hn = [n for n in layer_files if n.endswith("-head.png")][0]
    hd = (decode(z17.read(hn)) != decode(z.read(hn))).any(axis=2)
    gate("head-layer changes lie only inside the face/hair edit box", not (hd & ~inside_edit).any(),
         {"changedHeadTexels": int(hd.sum()), "outsideBox": int((hd & ~inside_edit).sum()), "box": list(R1_EDIT_BOX)})
    on = [n for n in layer_files if n.endswith("-outline.png")][0]
    od = (decode(z17.read(on)) != decode(z.read(on))).any(axis=2)
    png17 = decode(open(fs(os.path.join(v17dir, V17_PNG)), "rb").read())
    cd = (png17 != png).any(axis=2)
    gate("composite PNG changes lie only inside the edit box + 1 texel (outline pass); body pixels unchanged",
         not (cd & ~inside_comp).any() and not (od & ~inside_comp).any(),
         {"changedTexels": int(cd.sum()), "outsideCompBox": int((cd & ~inside_comp).sum()),
          "outlineChanged": int(od.sum()), "box": list(R1_COMP_BOX)})
    gate("pin, cell, logical extent unchanged from v17 (rows 136+ clear, pin texel clear, same size)",
         png17.shape == png.shape and np.array_equal(png17[100:], png[100:]), list(PIN))

    def keys_of(a):
        k = np.full((H, W), "", dtype="<U1")
        for key, v in PALETTE.items():
            k[(a[..., 3] == 255) & (a[..., :3] == hex_rgb(v)).all(axis=2)] = key
        return k
    k17, k1 = keys_of(png17), keys_of(png)
    hair, skin = set("1234ha"), set("Ssjxk")
    brow = [k1[27, x] for x in range(81, 86)]
    gap = [k1[28, x] for x in range(80, 87)]
    lash = [k1[29, x] for x in range(82, 85)]
    gate("near brow (y27 x81-85, hair keys) is separated from the upper lash (y29) by a clear skin row (y28 x80-86)",
         all(c in hair for c in brow) and all(c in set("Ssj") for c in gap) and all(c == "E" for c in lash),
         {"brow": "".join(brow), "skinRow": "".join(gap), "lash": "".join(lash)})
    eye = (slice(26, 34), slice(79, 91))

    def count(kk, chars):
        return int(np.isin(kk[eye], list(chars)).sum())
    info["eyeBox"] = {"box": [79, 26, 91, 34],
                      "v17": {"E": count(k17, "E"), "b": count(k17, "b"), "y": count(k17, "y"), "i": count(k17, "i")},
                      "v17r1": {"E": count(k1, "E"), "b": count(k1, "b"), "y": count(k1, "y"), "i": count(k1, "i")}}
    gate("less near-eye black mass than v17 (fewer E lash/pupil texels; dark E+b not above v17) with at least as many "
         "eye-white texels", count(k1, "E") < count(k17, "E") and count(k1, "Eb") <= count(k17, "Eb")
         and count(k1, "y") >= count(k17, "y"), info["eyeBox"])

    def hair_flips(kk):
        n = 0
        for y in range(20, 27):
            for x in range(72, 90):
                a_, b_ = kk[y, x], kk[y, x + 1]
                if a_ in hair and b_ in hair and abs("1234".find(a_.replace("a", "3").replace("h", "4"))
                                                     - "1234".find(b_.replace("a", "3").replace("h", "4"))) >= 2:
                    n += 1
        return n
    info["bangStripes"] = {"rows": [20, 26], "x": [72, 90],
                           "definition": "adjacent hair texel pairs whose value steps by >= 2 ramp levels (1..4)",
                           "v17": hair_flips(k17), "v17r1": hair_flips(k1)}
    gate("bangs: fewer hard value flips between neighbouring hair texels than v17 (stripe/checker reduction)",
         hair_flips(k1) < hair_flips(k17), info["bangStripes"])
    ok = all(r["pass"] for r in results)
    report = {"status": "UNAPPROVED v17r1 facial finishing check (v17 gates + v17r1 scope gates)", "pass": ok,
              "passed": sum(r["pass"] for r in results), "total": len(results), "gates": results, "info": info,
              "pngSha256": sha(disk["png"]), "tool": "tools/" + os.path.basename(os.path.abspath(__file__))}
    print(json.dumps(report, indent=1, ensure_ascii=False))
    print("CHECK", "PASS" if ok else "FAIL", f"{report['passed']}/{report['total']}")
    return report


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("mode", choices=["preview", "build", "check"])
    ap.add_argument("dir", nargs="?")
    ap.add_argument("--write-report", action="store_true", help="check: also write the check report JSON")
    a = ap.parse_args()
    if a.mode == "preview":
        preview(a.dir)
    elif a.mode == "build":
        build()
    else:
        rep = check()
        if a.write_report:
            path = os.path.join(REPO, OUT_DIR_REL, NAMES["check"])
            data = (json.dumps(rep, indent=1, ensure_ascii=False) + "\n").encode()
            if os.path.exists(fs(path)) and open(fs(path), "rb").read() != data:
                raise SystemExit("refusing to overwrite a different check report")
            open(fs(path), "wb").write(data)
        sys.exit(0 if rep["pass"] else 1)


if __name__ == "__main__":
    main()
