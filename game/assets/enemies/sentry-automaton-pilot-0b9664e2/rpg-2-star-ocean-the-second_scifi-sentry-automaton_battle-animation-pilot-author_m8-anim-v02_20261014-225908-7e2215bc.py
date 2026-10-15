"""Author the UNAPPROVED native-pixel sentry automaton battle ANIMATION pilot, revision v2 (21 frames, facing left).

v2 answers the creator's review of the real Godot v1 loop ("方向可以，继续修正遮挡与滑步"):
  1. Occlusion: at the unchanged 53 px melee spacing the heroes covered the eye, lens shutter and
     claw. v2 cells are 112x62: the unchanged 96x62 static plates sit 16 px from the left edge, so
     the strike can lunge past the static silhouette. The runtime draws the cell with its anchor at
     static x 30 instead of 48, which moves the sprite 18 px away from the party (visual only).
  2. Foot slide: v1 played four timed gait frames while the body travelled about 8 px per frame,
     so the planted feet slid. The v2 gait is eight frames driven by distance travelled: every
     frame is one 4 px step, and each stance foot moves exactly +4 px in the cell per step. The
     runtime moves the drawn sprite in the same 4 px steps, so stance feet stay fixed on the floor.

Plates, palette and compositor are unchanged. The static author script is imported unchanged for
its palette, Part class and compositor; only its canvas size globals are widened to the 112 px
cell before any part is built:
  rpg-2-star-ocean-the-second_scifi-sentry-automaton_battle-idle-pilot-author_m8-v01_20261014-221848-0b9664e2.py
Every coordinate below is the static script's coordinate plus integer joint offsets (body, head,
and hip / knee / foot per leg), plus the 16 px cell margin. Nothing is read from, traced from or
resampled from any image. The v1 files are not modified. Idle, wind-up, hit and defeat frames
reuse the v1 poses exactly; the gait and strike are new.

Frames (one 112x62 cell each, left to right):
  0-3   idle    as v1: breathe down 1px on bent knees, eye pulse, scan glance, fin twitch
  4-11  move    distance-locked diagonal gait, 8 steps of 4 px (one 32 px cycle)
  12-13 windup  as v1: rear back, near claw raised, fin flared, eye charging
  14-15 strike  lunge: body 7 px and head 11 px forward, the claw stamps 13 px ahead, then recoils
  16-17 hit     as v1: jolted back, eye shutter half/quarter closed, impact sparks
  18-20 defeat  as v1: knees splay, body sinks to the ground, eye and lights go dark

Row 60 is the last opaque row of every frame (ground anchor row).

Usage (bundled Python/Pillow runtime, run with -I):
  python <this file> --out DIR      -> scratch strip + 4x sheet + GIF for iteration, no manifest
  python <this file> --final DIR --preview-dir OUT
      -> new uniquely named strip PNG, one PNG per frame (in a .gdignore folder) and a manifest
         in DIR; a 4x review sheet and a looping GIF in OUT. Never overwrites.
"""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import uuid
from datetime import datetime
from pathlib import Path

from PIL import Image, ImageDraw

HERE = Path(__file__).resolve().parent
STATIC_AUTHOR = HERE / "rpg-2-star-ocean-the-second_scifi-sentry-automaton_battle-idle-pilot-author_m8-v01_20261014-221848-0b9664e2.py"
STATIC_PNG = HERE / "rpg-2-star-ocean-the-second_scifi-sentry-automaton_battle-idle-left_m8-pilot-v01_20261014-221901-e3ab87f9.png"
V1_AUTHOR = HERE / "rpg-2-star-ocean-the-second_scifi-sentry-automaton_battle-animation-pilot-author_m8-anim-v01_20261014-223554-0ae02683.py"
V1_STRIP = HERE / "rpg-2-star-ocean-the-second_scifi-sentry-automaton_battle-animation-strip-left_m8-anim-v01_20261014-223820-f181f893.png"
V1_MANIFEST = HERE / "rpg-2-star-ocean-the-second_scifi-sentry-automaton_battle-animation-manifest_m8-anim-v01_20261014-223820-f181f893.json"

_spec = importlib.util.spec_from_file_location("sentry_static_author", STATIC_AUTHOR)
static = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(static)

SLUG = static.SLUG
STATIC_SIZE = static.SIZE
STATIC_ANCHOR = static.ANCHOR
PALETTE = static.PALETTE
MARGIN = 16
W, H = STATIC_SIZE[0] + MARGIN, STATIC_SIZE[1]
SIZE = (W, H)
# The static compositor reads these module globals; widen its canvas to the v2 cell.
static.SIZE, static.W, static.H = SIZE, W, H
ANCHOR_ROW = STATIC_ANCHOR[1]
# Runtime draw anchor (cell coordinates): static x 30 instead of 48, so the sprite sits 18 px further from the party.
RUNTIME_ANCHOR = (30 + MARGIN, ANCHOR_ROW)
BODY_CENTER_X = STATIC_ANCHOR[0] + MARGIN
GAIT_STEP = 4
GAIT_FRAMES = 8

STATES = [
    ("idle", 4, 0.22, "loop"),
    ("move", GAIT_FRAMES, None, "distance"),
    ("windup", 2, None, "progress"),
    ("strike", 2, 0.15, "once"),
    ("hit", 2, 0.12, "once"),
    ("defeat", 3, 0.16, "hold-last"),
]

Z = (0, 0)


def add(*offsets):
    return (sum(o[0] for o in offsets), sum(o[1] for o in offsets))


def mid(a, b):
    return ((a[0] + b[0]) // 2, (a[1] + b[1]) // 2)


class Rig(static.Part):
    """A static Part whose coordinates are shifted by named joint offsets and the cell margin."""

    def __init__(self, name: str, joints: dict, default: str):
        super().__init__(name)
        self.j = joints
        self.d = default

    def _pt(self, p):
        dx, dy = self.j[p[2] if len(p) > 2 else self.d]
        return (p[0] + dx + MARGIN, p[1] + dy)

    def _box(self, x0, y0, x1, y1, tag):
        dx, dy = self.j[tag or self.d]
        return x0 + dx + MARGIN, y0 + dy, x1 + dx + MARGIN, y1 + dy

    def poly(self, pts, key):
        super().poly([self._pt(p) for p in pts], key)

    def clip_poly(self, pts, key):
        super().clip_poly([self._pt(p) for p in pts], key)

    def rect(self, x0, y0, x1, y1, key, tag=None):
        super().rect(*self._box(x0, y0, x1, y1, tag), key)

    def clip_rect(self, x0, y0, x1, y1, key, tag=None):
        super().clip_rect(*self._box(x0, y0, x1, y1, tag), key)

    def oval(self, x0, y0, x1, y1, key, tag=None):
        super().oval(*self._box(x0, y0, x1, y1, tag), key)

    def clip_oval(self, x0, y0, x1, y1, key, tag=None):
        super().clip_oval(*self._box(x0, y0, x1, y1, tag), key)

    def px(self, pts, key, tag=None):
        dx, dy = self.j[tag or self.d]
        pts = [(x + dx + MARGIN, y + dy) for x, y in pts]
        super().px([p for p in pts if 0 <= p[0] < W and 0 <= p[1] < H], key)


def pose(body=Z, head=Z, fin=Z, dome=Z, nfl=(Z, Z), nrl=(Z, Z), ffl=(Z, Z), frl=(Z, Z),
         eye="normal", pupil=Z, lights="on", fx=()):
    """Leg tuples are (knee, foot) absolute offsets; hips follow the body (front-near hip follows the head)."""
    return dict(body=body, head=head, fin=fin, dome=dome, nfl=nfl, nrl=nrl, ffl=ffl, frl=frl,
                eye=eye, pupil=pupil, lights=lights, fx=list(fx))


def leg_joints(hip, knee_foot):
    knee, foot = knee_foot
    return {"h": hip, "k": knee, "f": foot, "m": mid(knee, foot)}


def build_parts(p: dict) -> list:
    """Same plates and coordinates as the v1 rig (and the static pilot)."""
    body, head = p["body"], p["head"]
    lit = p["lights"]
    parts = []

    r = Rig("far_rear_leg", leg_joints(body, p["frl"]), "k")
    r.poly([(60, 28, "h"), (66, 26, "h"), (73, 34, "k"), (69, 38, "k")], "2")
    r.clip_poly([(60, 28, "h"), (66, 26, "h"), (68, 28, "h"), (62, 30, "h")], "3")
    r.poly([(68, 37, "k"), (73, 37, "k"), (77, 52, "f"), (72, 52, "f")], "2")
    r.clip_poly([(72, 37, "k"), (73, 37, "k"), (77, 52, "f"), (76, 52, "f")], "1")
    r.oval(67, 32, 73, 38, "b")
    r.oval(68, 33, 71, 36, "a")
    r.px([(69, 33), (68, 34)], "c")
    r.rect(67, 53, 79, 57, "1", "f")
    r.rect(67, 53, 79, 53, "2", "f")
    r.rect(76, 53, 79, 57, "b", "f")
    r.px([(76, 53), (77, 53)], "c", "f")
    parts.append(r)

    r = Rig("far_front_leg", leg_joints(body, p["ffl"]), "k")
    r.poly([(40, 28, "h"), (44, 32, "h"), (32, 40, "k"), (29, 36, "k")], "2")
    r.poly([(26, 39, "k"), (31, 39, "k"), (29, 52, "f"), (24, 52, "f")], "2")
    r.clip_poly([(30, 39, "k"), (31, 39, "k"), (29, 52, "f"), (28, 52, "f")], "1")
    r.oval(25, 34, 31, 40, "b")
    r.oval(26, 35, 29, 38, "a")
    r.px([(27, 35), (26, 36)], "c")
    r.rect(19, 53, 31, 57, "1", "f")
    r.rect(19, 53, 31, 53, "2", "f")
    r.rect(19, 53, 22, 57, "b", "f")
    r.px([(20, 53), (21, 53)], "c", "f")
    parts.append(r)

    r = Rig("belly", {"b": body}, "b")
    r.poly([(32, 25), (80, 25), (75, 35), (38, 35)], "1")
    for x in range(40, 74, 4):
        r.clip_rect(x, 29, x, 33, "2")
    r.oval(50, 28, 58, 36, "b")
    r.oval(52, 30, 56, 34, "a")
    r.px([(51, 30), (52, 29), (53, 29)], "c")
    r.px([(54, 32)], "c")
    parts.append(r)

    r = Rig("shell", {"b": body}, "b")
    r.poly([(28, 15), (36, 9), (46, 6), (55, 4), (66, 4), (76, 6), (85, 11), (91, 18), (91, 24), (86, 30), (30, 30)], "4")
    r.clip_poly([(36, 9), (46, 6), (55, 4), (66, 4), (72, 5), (66, 8), (56, 8), (46, 10), (38, 13)], "5")
    r.clip_poly([(72, 5), (85, 11), (91, 18), (91, 23), (84, 20), (76, 12), (68, 9)], "3")
    r.clip_rect(26, 23, 92, 30, "3")
    r.rim("6", "2")
    r.clip_rect(29, 23, 90, 23, "2")
    r.clip_rect(29, 24, 89, 24, "4")
    for x0 in (47, 69):
        r.clip_poly([(x0, 5), (x0 + 3, 5), (x0 + 4, 22), (x0 + 1, 22)], "c")
        r.clip_poly([(x0, 5), (x0 + 1, 5), (x0 + 2, 22), (x0 + 1, 22)], "d")
        r.clip_poly([(x0 + 3, 5), (x0 + 3, 5), (x0 + 4, 22), (x0 + 4, 22)], "b")
        r.clip_rect(x0 + 1, 25, x0 + 4, 27, "b")
        r.clip_rect(x0 + 1, 25, x0 + 3, 25, "c")
    for x in (60, 79):
        r.clip_rect(x, 25, x, 29, "2")
        r.clip_rect(x + 1, 25, x + 1, 29, "4")
    for x in (83, 85, 87):
        r.clip_rect(x, 25, x, 28, "1")
    vent = {"on": ("y", "z"), "bright": ("z", "w"), "off": ("2", "3")}[lit]
    r.px([(89, 21), (89, 22)], vent[0])
    r.px([(90, 21)], vent[1])
    r.px([(38, 15), (39, 15), (40, 14), (41, 14), (42, 14), (43, 14)], "3")
    r.px([(56, 13), (57, 13), (58, 13), (59, 13), (60, 13), (61, 13), (62, 13), (63, 13)], "3")
    r.px([(77, 14), (78, 14), (79, 15), (80, 15), (81, 16)], "3")
    r.px([(40, 20), (61, 19), (80, 19)], "2")
    r.px([(40, 19), (61, 18), (80, 18)], "6")
    r.px([(44, 9), (56, 17), (36, 21), (73, 10), (65, 21), (84, 17)], "3")
    r.px([(54, 20), (76, 20), (44, 27), (66, 28)], "r")
    parts.append(r)

    r = Rig("dome", {"d": add(body, p["dome"])}, "d")
    r.oval(55, 2, 63, 9, "3")
    r.clip_oval(56, 3, 61, 6, "4")
    r.px([(58, 4), (59, 4)], "5")
    r.px([(60, 5)], {"on": "y", "bright": "z", "off": "2"}[lit])
    r.rect(55, 7, 63, 8, "b")
    r.px([(56, 7), (57, 7)], "c")
    parts.append(r)

    r = Rig("far_fin", {"f": add(head, p["fin"])}, "f")
    r.poly([(3, 12), (10, 5), (21, 6), (23, 10), (12, 13), (6, 18)], "3")
    r.rim("4", "2")
    r.px([(10, 8), (11, 8), (12, 8)], "1")
    parts.append(r)

    r = Rig("near_rear_leg", leg_joints(body, p["nrl"]), "k")
    r.poly([(64, 29, "h"), (70, 27, "h"), (86, 36, "k"), (81, 42, "k")], "4")
    r.clip_poly([(64, 29, "h"), (70, 27, "h"), (86, 36, "k"), (84, 37, "k"), (68, 30, "h")], "5")
    r.clip_poly([(84, 39, "k"), (86, 36, "k"), (86, 38, "k"), (81, 42, "k")], "3")
    r.oval(61, 26, 69, 34, "c", "h")
    r.clip_oval(61, 26, 67, 32, "d", "h")
    r.oval(63, 28, 67, 32, "b", "h")
    r.px([(64, 29)], "e", "h")
    r.px([(65, 30)], "a", "h")
    r.poly([(79, 41, "k"), (87, 41, "k"), (92, 54, "f"), (84, 54, "f")], "4")
    r.clip_poly([(79, 41, "k"), (81, 41, "k"), (86, 54, "f"), (84, 54, "f")], "5")
    r.clip_poly([(86, 41, "k"), (87, 41, "k"), (92, 54, "f"), (90, 54, "f")], "3")
    r.clip_rect(80, 47, 90, 47, "3", "m")
    r.oval(79, 35, 87, 43, "c")
    r.clip_oval(79, 35, 85, 41, "d")
    r.oval(81, 37, 85, 41, "b")
    r.px([(81, 36), (82, 36)], "e")
    r.px([(83, 39)], "a")
    r.rect(79, 55, 94, 59, "3", "f")
    r.rect(79, 55, 94, 55, "4", "f")
    r.rect(79, 59, 94, 59, "1", "f")
    r.rect(89, 54, 94, 59, "c", "f")
    r.rect(89, 54, 94, 54, "d", "f")
    r.px([(89, 55)], "e", "f")
    r.rect(89, 59, 94, 59, "b", "f")
    r.px([(82, 59), (85, 59)], "2", "f")
    parts.append(r)

    r = Rig("near_front_leg", leg_joints(head, p["nfl"]), "k")
    r.poly([(30, 33, "h"), (36, 37, "h"), (19, 47, "k"), (15, 41, "k")], "4")
    r.clip_poly([(30, 33, "h"), (32, 34, "h"), (16, 43, "k"), (15, 41, "k")], "5")
    r.clip_poly([(35, 37, "h"), (36, 37, "h"), (19, 47, "k"), (18, 46, "k")], "3")
    r.poly([(11, 45, "k"), (19, 45, "k"), (13, 54, "f"), (5, 54, "f")], "4")
    r.clip_poly([(11, 45, "k"), (13, 45, "k"), (7, 54, "f"), (5, 54, "f")], "5")
    r.clip_poly([(18, 45, "k"), (19, 45, "k"), (13, 54, "f"), (11, 54, "f")], "3")
    r.clip_rect(6, 50, 17, 50, "3", "m")
    r.oval(11, 39, 19, 47, "c")
    r.clip_oval(11, 39, 17, 45, "d")
    r.oval(13, 41, 17, 45, "b")
    r.px([(13, 40), (14, 40)], "e")
    r.px([(15, 43)], "a")
    r.rect(1, 55, 16, 59, "3", "f")
    r.rect(1, 55, 16, 55, "4", "f")
    r.rect(1, 59, 16, 59, "1", "f")
    r.rect(1, 54, 6, 59, "c", "f")
    r.rect(1, 54, 6, 54, "d", "f")
    r.px([(1, 55), (2, 54)], "e", "f")
    r.rect(1, 59, 6, 59, "b", "f")
    r.px([(10, 59), (13, 59)], "2", "f")
    parts.append(r)

    r = Rig("eye_housing", {"e": head}, "e")
    r.poly([(8, 17), (13, 10), (29, 9), (35, 15), (35, 32), (29, 38), (14, 38), (8, 32)], "2")
    r.rim("3", "1")
    strip = {"on": ("z", "x", "w"), "bright": ("w", "y", "w"), "off": ("x", "1", "y")}[lit]
    r.rect(33, 20, 33, 25, strip[0])
    r.rect(34, 20, 34, 25, strip[1])
    r.px([(33, 20)], strip[2])
    parts.append(r)

    eye_joints = {"e": head, "p": add(head, p["pupil"])}
    r = Rig("eye", eye_joints, "e")
    r.oval(10, 12, 30, 32, "c")
    r.clip_poly([(30, 18), (30, 32), (16, 32)], "b")
    r.clip_poly([(10, 12), (23, 12), (10, 25)], "d")
    r.px([(14, 14), (15, 14), (13, 15), (12, 16)], "e")
    r.oval(13, 15, 27, 29, "a")
    paint_lens(r, p["eye"])
    parts.append(r)

    r = Rig("cheek_plate", {"e": head}, "e")
    r.poly([(34, 12), (40, 7), (47, 12), (47, 33), (41, 38), (34, 34)], "4")
    r.clip_poly([(34, 12), (40, 7), (47, 12), (40, 10), (36, 14)], "5")
    r.clip_poly([(44, 14), (47, 12), (47, 33), (44, 35)], "3")
    r.rim("6", "2")
    r.clip_rect(40, 16, 40, 27, "1")
    r.clip_rect(41, 16, 41, 27, "3")
    r.oval(38, 29, 42, 33, "c")
    r.px([(39, 30)], "e")
    r.px([(41, 32)], "b")
    r.px([(37, 22), (45, 18)], "3")
    parts.append(r)

    return parts


def paint_lens(r: Rig, mode: str) -> None:
    """Lens rings inside the bezel, as v1. 'normal' is the static pilot lens exactly."""
    if mode in ("normal", "pulse"):
        r.oval(14, 16, 26, 28, "x")
        r.oval(15, 17, 25, 27, "y")
        r.oval(16, 18, 23, 25, "z", "p")
        if mode == "pulse":
            r.clip_oval(15, 17, 25, 27, "z", "p")
            r.clip_oval(17, 19, 22, 24, "w", "p")
        r.clip_poly([(25, 20, "p"), (25, 27, "p"), (18, 27, "p")], "x")
        r.clip_poly([(25, 21, "p"), (25, 26, "p"), (20, 26, "p")], "y")
        r.px([(17, 19), (18, 19), (17, 20)], "w", "p")
        r.px([(19, 21), (20, 21), (19, 22), (20, 22)], "w", "p")
        r.px([(23, 24), (22, 25)], "z", "p")
    elif mode in ("charge1", "charge2", "flash"):
        r.oval(14, 16, 26, 28, "y")
        r.oval(15, 17, 25, 27, "z")
        core = {"charge1": (17, 19, 22, 24), "charge2": (16, 18, 23, 25), "flash": (15, 17, 24, 26)}[mode]
        r.oval(*core, "w", "p")
        if mode != "flash":
            r.clip_poly([(25, 21, "p"), (25, 27, "p"), (19, 27, "p")], "y")
        r.px([(14, 22), (14, 21)], "w" if mode == "flash" else "z")
    elif mode in ("hurt0", "hurt1"):
        r.oval(14, 16, 26, 28, "x")
        r.oval(15, 17, 25, 27, "y")
        r.oval(17, 19, 22, 24, "z", "p")
        r.px([(18, 20)], "w", "p")
        lid = 22 if mode == "hurt0" else 19
        r.clip_rect(13, 15, 27, lid, "3")
        r.clip_rect(13, 15, 27, lid - 2, "4")
        r.clip_rect(13, lid, 27, lid, "1")
        r.clip_rect(13, lid - 4, 27, lid - 4, "5")
    elif mode == "dim":
        r.oval(14, 16, 26, 28, "x")
        r.oval(16, 18, 23, 25, "y")
        r.px([(17, 19), (18, 19)], "z")
    elif mode == "dark":
        r.oval(14, 16, 26, 28, "1")
        r.oval(16, 18, 23, 25, "x")
        r.px([(17, 19)], "y")
    elif mode == "off":
        r.oval(14, 16, 26, 28, "1")
        r.oval(16, 18, 23, 25, "2")
        r.px([(17, 19), (18, 19)], "3")
    else:
        raise ValueError(mode)


def render(p: dict) -> Image.Image:
    img = static.composite(build_parts(p))
    out = img.load()
    for x, y, key in p["fx"]:
        cx = x + MARGIN
        assert 0 <= cx < W and 0 <= y <= ANCHOR_ROW, (x, y)
        h = PALETTE[key]
        out[cx, y] = (int(h[1:3], 16), int(h[3:5], 16), int(h[5:7], 16), 255)
    return img


def sparks(points, key):
    return [(x, y, key) for x, y in points]


# Distance-locked gait. Diagonal pairs: A = near-front + far-rear, B = near-rear + far-front.
# A foot in stance moves +GAIT_STEP px per step in the cell (backward, away from the party) while the
# runtime moves the sprite GAIT_STEP px toward the party, so it stays on one floor pixel.
# Stance starts: the near-front foot lands on its static spot and pushes 12 px back; the near-rear foot
# lands 12 px forward and pushes back to its static spot; far feet stroke 6 px either side of static.
SWING_X = (10, 7, 5, 2)
GAIT_LEGS = {
    # leg: (stance start step, stance start x, swing lift peak)
    "nfl": (0, 0, 4),
    "frl": (0, -6, 3),
    "nrl": (4, -12, 4),
    "ffl": (4, -6, 3),
}


def gait_foot(leg: str, step: int):
    start, x0, peak = GAIT_LEGS[leg]
    k = (step - start) % GAIT_FRAMES
    if k < 4:
        return (x0 + GAIT_STEP * k, 0), True
    j = k - 4
    lift = (peak // 2, peak, peak, peak // 2)[j]
    return (x0 + SWING_X[j], -lift), False


def gait_pose(step: int) -> dict:
    # The body dips 1 px as each pair lands (steps 0 and 4).
    dy = 1 if step % 4 == 0 else 0
    legs = {}
    for leg in GAIT_LEGS:
        (fx, fy), _ = gait_foot(leg, step)
        # The knee follows the foot halfway forward and most of the way up, so the shin swings, not slides.
        legs[leg] = ((fx // 2 if fx >= 0 else -((-fx) // 2), dy + (fy * 3) // 4), (fx, fy))
    return pose(body=(0, dy), head=(0, dy), pupil=(-1, 0), **legs)


IDLE_LEGS_DOWN = dict(nfl=((0, 1), Z), nrl=((0, 1), Z), ffl=((0, 1), Z), frl=((0, 1), Z))

FRAMES = [
    # idle (v1 poses)
    ("idle", pose()),
    ("idle", pose(body=(0, 1), head=(0, 1), **IDLE_LEGS_DOWN)),
    ("idle", pose(body=(0, 1), head=(0, 1), eye="pulse", **IDLE_LEGS_DOWN)),
    ("idle", pose(fin=(0, -1), pupil=(-1, 0))),
] + [("move", gait_pose(step)) for step in range(GAIT_FRAMES)] + [
    # windup (v1 poses): rear back on the hind legs, near claw raised, fin flared, eye charging
    ("windup", pose(body=(2, 0), head=(2, -1), fin=(0, -1), nfl=((3, -3), (2, -4)), nrl=((1, 0), Z), ffl=((1, 0), Z), frl=((1, 0), Z),
                    eye="charge1", lights="bright")),
    ("windup", pose(body=(3, 1), head=(3, -2), fin=(1, -2), nfl=((5, -5), (4, -7)), nrl=((2, 1), Z), ffl=((2, 0), Z), frl=((2, 1), Z),
                    eye="charge2", lights="bright")),
    # strike (v2): lunge past the static silhouette. Body 7 px and head 11 px forward and down, the raised
    # claw stamps 13 px ahead of its static spot, the hind legs straighten with their feet planted.
    ("strike", pose(body=(-7, 1), head=(-11, 2), fin=(1, 1), nfl=((-12, 1), (-13, 0)), nrl=((-4, -1), Z), ffl=((-5, 1), Z), frl=((-4, 0), Z),
                    eye="flash", pupil=(-1, 0), lights="bright",
                    fx=sparks([(-9, 20), (-10, 24), (-8, 28), (-9, 32), (-7, 16)], "w") + sparks([(-11, 18), (-10, 22), (-11, 30), (-8, 35)], "z")
                    + sparks([(-14, 57), (4, 58), (5, 57), (-14, 59), (4, 60), (-13, 56)], "6") + sparks([(3, 59), (6, 59), (-15, 60)], "5"))),
    # recoil: the claw lifts and comes back toward its static spot, body and head draw back.
    ("strike", pose(body=(-3, 1), head=(-5, 1), nfl=((-5, -2), (-6, -3)), nrl=((-2, 0), Z), ffl=((-2, 1), Z), frl=((-2, 0), Z),
                    eye="charge1", pupil=(-1, 0),
                    fx=sparks([(-3, 21), (-2, 29)], "y") + sparks([(-14, 59), (-12, 58), (4, 59)], "5"))),
    # hit (v1 poses)
    ("hit", pose(body=(2, 0), head=(3, -1), fin=(1, -1), dome=(1, 0), nfl=((2, 0), Z), nrl=((1, 1), Z), ffl=((1, 0), Z), frl=((1, 1), Z),
                 eye="hurt0",
                 fx=sparks([(8, 11), (6, 14), (9, 9)], "w") + sparks([(5, 12), (7, 8), (4, 16)], "e"))),
    ("hit", pose(body=(1, 0), head=(1, 0), nfl=((1, 0), Z), nrl=((1, 0), Z), ffl=((1, 0), Z), frl=((1, 0), Z),
                 eye="hurt1", fx=sparks([(4, 10), (3, 15)], "d"))),
    # defeat (v1 poses)
    ("defeat", pose(body=(0, 3), head=(0, 4), fin=(0, 1), nfl=((-2, 3), Z), nrl=((2, 3), Z), ffl=((-1, 3), Z), frl=((1, 3), Z),
                    eye="dim", lights="off")),
    ("defeat", pose(body=(0, 7), head=(-1, 9), fin=(1, 2), nfl=((-3, 7), Z), nrl=((3, 7), Z), ffl=((-2, 7), Z), frl=((2, 7), Z),
                    eye="dark", lights="off")),
    ("defeat", pose(body=(0, 9), head=(-1, 12), fin=(1, 3), dome=(1, 0), nfl=((-4, 9), Z), nrl=((4, 9), Z), ffl=((-3, 9), Z), frl=((3, 9), Z),
                    eye="off", lights="off",
                    fx=sparks([(83, 17), (84, 17), (85, 17), (84, 16), (85, 16), (86, 13), (87, 13), (87, 12), (88, 12)], "5")
                    + sparks([(86, 12), (88, 8), (89, 8), (89, 7)], "6"))),
]
# v1 frame index each reused pose came from (the v2 cell crop at the margin must equal the v1 cell).
V1_REUSED = {0: 0, 1: 1, 2: 2, 3: 3, 12: 8, 13: 9, 16: 12, 17: 13, 18: 14, 19: 15, 20: 16}


def render_all() -> list[Image.Image]:
    frames = [render(p) for _, p in FRAMES]
    expected = [s for s, n, _, _ in STATES for _ in range(n)]
    assert [s for s, _ in FRAMES] == expected, "frame order must match STATES"
    return frames


def pixels(img: Image.Image) -> list:
    return list(img.get_flattened_data() if hasattr(img, "get_flattened_data") else img.getdata())


def ground_runs(img: Image.Image) -> list:
    """Opaque runs on the anchor row: the grounded near feet (far feet end 2 px higher)."""
    runs, start = [], None
    for x in range(W + 1):
        on = x < W and img.getpixel((x, ANCHOR_ROW))[3] > 0
        if on and start is None:
            start = x
        elif not on and start is not None:
            runs.append((start, x - 1))
            start = None
    return runs


def check(frames: list[Image.Image]) -> dict:
    static_png = Image.open(STATIC_PNG).convert("RGBA")
    v1 = Image.open(V1_STRIP).convert("RGBA")
    sw = STATIC_SIZE[0]
    crop = lambda img: img.crop((MARGIN, 0, MARGIN + sw, H))
    assert crop(frames[0]).tobytes() == static_png.tobytes(), "neutral idle frame must equal the static pilot"
    assert all(frames[0].getpixel((x, y))[3] == 0 for y in range(H) for x in range(MARGIN)), "idle margin must be empty"
    for i2, i1 in V1_REUSED.items():
        assert crop(frames[i2]).tobytes() == v1.crop((i1 * sw, 0, (i1 + 1) * sw, H)).tobytes(), ("v1 pose changed", i2, i1)
        assert all(frames[i2].getpixel((x, y))[3] == 0 for y in range(H) for x in range(MARGIN)), ("reused pose spills into margin", i2)
    palette = {tuple(int(h[i:i + 2], 16) for i in (1, 3, 5)) for h in PALETTE.values()}
    report = []
    for i, img in enumerate(frames):
        bbox = img.getbbox()
        assert bbox[3] - 1 == ANCHOR_ROW, (i, bbox)
        colours = {c[:3] for c in pixels(img) if c[3]}
        assert colours <= palette, (i, colours - palette)
        assert {c[3] for c in pixels(img)} <= {0, 255}
        report.append({"index": i, "state": FRAMES[i][0], "opaqueBBox": list(bbox), "colourCount": len(colours),
                       "opaquePixels": sum(1 for c in pixels(img) if c[3]), "anchorRowRuns": ground_runs(img)})
    # Gait lock: between consecutive steps every foot that stays in stance moves exactly +GAIT_STEP px in the cell,
    # and the grounded near-foot runs on the anchor row move by the same amount (pixel check of the composited frames).
    move = [i for i, (s, _) in enumerate(FRAMES) if s == "move"]
    lock = []
    for step in range(GAIT_FRAMES):
        nxt = (step + 1) % GAIT_FRAMES
        for leg in GAIT_LEGS:
            (x0, _), s0 = gait_foot(leg, step)
            (x1, _), s1 = gait_foot(leg, nxt)
            if s0 and s1:
                assert x1 - x0 == GAIT_STEP, (leg, step, x0, x1)
                lock.append({"leg": leg, "step": step, "cellShiftPx": x1 - x0})
        a, b = ground_runs(frames[move[step]]), ground_runs(frames[move[nxt]])
        for leg, side in (("nfl", 0), ("nrl", 1)):
            if gait_foot(leg, step)[1] and gait_foot(leg, nxt)[1]:
                ra = [r for r in a if (r[0] < W // 2) == (side == 0)]
                rb = [r for r in b if (r[0] < W // 2) == (side == 0)]
                assert len(ra) == 1 and len(rb) == 1, (leg, step, a, b)
                assert rb[0][0] - ra[0][0] == GAIT_STEP and rb[0][1] - ra[0][1] == GAIT_STEP, (leg, step, ra, rb)
        # One near foot is always on the ground.
        assert any(gait_foot(leg, step)[1] for leg in ("nfl", "nrl")), step
    return {"frames": report, "gaitLock": lock}


def strip_of(frames):
    strip = Image.new("RGBA", (W * len(frames), H), (0, 0, 0, 0))
    for i, f in enumerate(frames):
        strip.paste(f, (i * W, 0))
    return strip


def review_sheet(frames, scale: int) -> Image.Image:
    """Nearest-neighbour enlargement for human review only (never shipped)."""
    pad, label_h = 8, 14
    cols = 4
    rows = (len(frames) + cols - 1) // cols
    cw, ch = W * scale + pad, H * scale + pad + label_h
    sheet = Image.new("RGBA", (cols * cw + pad, rows * ch + pad + 18), (24, 28, 36, 255))
    d = ImageDraw.Draw(sheet)
    d.text((pad, 4), "Sentry automaton animation pilot v2 - UNAPPROVED, art acceptance 0 (native 112x62 cells, %dx nearest; red = anchor row, cyan = runtime anchor x)" % scale, fill=(230, 230, 230, 255))
    counters = {}
    for i, f in enumerate(frames):
        state = FRAMES[i][0]
        counters[state] = counters.get(state, -1) + 1
        x0 = pad + (i % cols) * cw
        y0 = 18 + pad + (i // cols) * ch
        d.text((x0, y0), "%02d %s %d" % (i, state, counters[state]), fill=(200, 210, 220, 255))
        bg = Image.new("RGBA", SIZE, (118, 122, 128, 255))
        bg.alpha_composite(f)
        sheet.paste(bg.resize((W * scale, H * scale), Image.NEAREST), (x0, y0 + label_h))
        ay = y0 + label_h + ANCHOR_ROW * scale + scale - 1
        d.line((x0, ay, x0 + W * scale - 1, ay), fill=(255, 80, 60, 255))
        ax = x0 + RUNTIME_ANCHOR[0] * scale
        d.line((ax, y0 + label_h + (ANCHOR_ROW + 1) * scale, ax, y0 + label_h + H * scale - 1), fill=(80, 220, 230, 255))
    return sheet


def loop_gif(frames, path: Path, scale: int) -> list:
    """Looping GIF preview with runtime-like timing; the gait travels across a marked floor (review only)."""
    idx = {s: [i for i, (st, _) in enumerate(FRAMES) if st == s] for s, _, _, _ in STATES}
    # Gait at 68 px/s: one 4 px step every 1/17 s, shown at 59 ms per step.
    step_ms = round(1000 * GAIT_STEP / 68.0)
    travel = 2 * GAIT_FRAMES * GAIT_STEP
    seq = [(i, 220, 0) for i in idx["idle"]]
    for n in range(2 * GAIT_FRAMES):
        seq.append((idx["move"][n % GAIT_FRAMES], step_ms, -(n * GAIT_STEP)))
    end = -travel
    seq += [(idx["windup"][0], 240, end), (idx["windup"][1], 240, end)]
    seq += [(idx["strike"][0], 150, end), (idx["strike"][1], 150, end)]
    seq += [(i, 220, end) for i in idx["idle"]]
    seq += [(idx["hit"][0], 120, end), (idx["hit"][1], 120, end)]
    seq += [(i, 220, end) for i in idx["idle"]]
    seq += [(i, 160, end) for i in idx["defeat"]] + [(idx["defeat"][-1], 900, end)]
    cw = W + travel + 16
    imgs = []
    for i, _, dx in seq:
        bg = Image.new("RGBA", (cw, H + 8), (118, 122, 128, 255))
        d = ImageDraw.Draw(bg)
        d.line((0, 4 + ANCHOR_ROW + 1, cw - 1, 4 + ANCHOR_ROW + 1), fill=(84, 88, 94, 255))
        # Floor ticks every 8 px make foot slip visible.
        for x in range(0, cw, 8):
            d.point((x, 4 + ANCHOR_ROW + 2), fill=(60, 64, 70, 255))
        bg.alpha_composite(frames[i], (8 + travel + dx, 4))
        imgs.append(bg.resize((cw * scale, (H + 8) * scale), Image.NEAREST).convert("P", palette=Image.ADAPTIVE, colors=64))
    imgs[0].save(path, save_all=True, append_images=imgs[1:], duration=[d for _, d, _ in seq], loop=0, disposal=2)
    return [[FRAMES[i][0], i, d, dx] for i, d, dx in seq]


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", type=Path, default=None)
    ap.add_argument("--final", type=Path, default=None)
    ap.add_argument("--preview-dir", type=Path, default=None)
    args = ap.parse_args()
    frames = render_all()
    report = check(frames)
    if args.out:
        args.out.mkdir(parents=True, exist_ok=True)
        strip_of(frames).save(args.out / "strip.png")
        review_sheet(frames, 4).save(args.out / "sheet_4x.png")
        loop_gif(frames, args.out / "loop.gif", 3)
        print("scratch", args.out, json.dumps([(f["state"], f["opaqueBBox"], f["anchorRowRuns"]) for f in report["frames"]]))
        return
    out_dir: Path = args.final
    prev: Path = args.preview_dir
    root = out_dir.resolve().parents[3]
    stamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    token = uuid.uuid4().hex[:8]
    tag = "m8-anim-v02"
    path = out_dir / f"{SLUG}_scifi-sentry-automaton_battle-animation-strip-left_{tag}_{stamp}-{token}.png"
    mpath = out_dir / f"{SLUG}_scifi-sentry-automaton_battle-animation-manifest_{tag}_{stamp}-{token}.json"
    # Short folder and file names: the full Windows path must stay under 260 characters.
    fdir = out_dir / f"frames_{tag}_{token}"
    spath = prev / f"{SLUG}_scifi-sentry-automaton-animation-pilot_4x-frame-sheet_{tag}_{stamp}-{token}.png"
    gpath = prev / f"{SLUG}_scifi-sentry-automaton-animation-pilot_3x-loop-preview_{tag}_{stamp}-{token}.gif"
    for p in (path, mpath, fdir, spath, gpath):
        assert not p.exists(), p
    strip = strip_of(frames)
    strip.save(path)
    # One file per frame. The .gdignore keeps Godot from importing these review copies; the runtime reads the strip.
    fdir.mkdir()
    (fdir / ".gdignore").write_text("", encoding="utf-8")
    frame_files = []
    counters = {}
    for i, f in enumerate(frames):
        state = FRAMES[i][0]
        counters[state] = counters.get(state, -1) + 1
        fpath = fdir / f"{SLUG}_sentry_anim-f{i:02d}-{state}{counters[state]}_{tag}_{stamp}-{token}.png"
        f.save(fpath)
        frame_files.append(fpath)
    review_sheet(frames, 4).save(spath)
    gif_seq = loop_gif(frames, gpath, 3)
    rel = lambda p: str(p.resolve().relative_to(root)).replace("\\", "/")
    sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
    for i, fpath in enumerate(frame_files):
        assert strip.crop((i * W, 0, (i + 1) * W, H)).tobytes() == Image.open(fpath).convert("RGBA").tobytes(), fpath
    script = Path(__file__).resolve()
    states = {}
    cursor = 0
    for name, count, frame_time, mode in STATES:
        states[name] = {"frames": list(range(cursor, cursor + count)), "frameTime": frame_time, "mode": mode}
        cursor += count
    states["move"]["stepPx"] = GAIT_STEP
    manifest = {
        "project": SLUG,
        "asset": "scifi sentry automaton battle animation pilot v2 (science-region ruins enemy)",
        "revision": tag,
        "supersedes": {"manifest": rel(V1_MANIFEST), "strip": rel(V1_STRIP), "note": "v1 files are unchanged; the runtime entry now points at v2"},
        "status": "animation_pilot_unapproved",
        "artAccepted": False,
        "artAcceptanceCount": 0,
        "humanReview": "pending - the creator viewed the real Godot v1 loop and answered '方向可以，继续修正遮挡与滑步' (direction OK, keep fixing occlusion and foot sliding); this is not animation acceptance",
        "file": rel(path),
        "sha256": sha(path),
        "stripSize": list(strip.size),
        "cellSize": list(SIZE),
        "frameCount": len(frames),
        "staticPlateOffsetInCell": [MARGIN, 0],
        "runtimeAnchor": list(RUNTIME_ANCHOR),
        "bodyCenterX": BODY_CENTER_X,
        "runtimeAnchorNote": "draw the cell at (enemy_x - %d, 272 - %d); the static pilot draws its 96x62 image at (enemy_x - 48, 212). The animated sprite therefore sits %d px further from the party (visual only), and the wind-up ring and contact shadow centre on cell x %d (enemy_x + %d)." % (RUNTIME_ANCHOR[0], ANCHOR_ROW, BODY_CENTER_X - RUNTIME_ANCHOR[0], BODY_CENTER_X, BODY_CENTER_X - RUNTIME_ANCHOR[0]),
        "facing": "left (toward party)",
        "states": states,
        "stateTimingNote": "move frames are chosen by distance travelled (one frame per 4 px step; the drawn sprite also moves in 4 px steps); windup frames by remaining wind-up (first half / second half); strike and hit play once; defeat holds its last frame",
        "gaitLock": report["gaitLock"],
        "frameReport": report["frames"],
        "frameFiles": [{"index": i, "state": FRAMES[i][0], "file": rel(p), "sha256": sha(p)} for i, p in enumerate(frame_files)],
        "neutralFrameEqualsStaticPilot": True,
        "reusedV1Poses": {str(k): v for k, v in V1_REUSED.items()},
        "staticPilot": {"file": rel(STATIC_PNG), "sha256": sha(STATIC_PNG)},
        "palette": PALETTE,
        "alphaValues": [0, 255],
        "method": "Re-posed native pixel plates: the static author's palette, Part class and compositor are imported unchanged (canvas size globals widened to the 112 px cell); every plate uses the static coordinates plus integer body/head/hip/knee/foot joint offsets and a 16 px cell margin. Lens/light states are explicit palette paints and a few effect pixels are placed explicitly. No image is read, traced, resampled, resized or generated by AI.",
        "authorScript": rel(script),
        "authorScriptSha256": sha(script),
        "staticAuthorScript": rel(STATIC_AUTHOR),
        "staticAuthorScriptSha256": sha(STATIC_AUTHOR),
        "v1AuthorScript": rel(V1_AUTHOR),
        "previews": {
            "frameSheet4x": {"file": rel(spath), "sha256": sha(spath), "note": "nearest-neighbour enlargement for review only"},
            "loopGif3x": {"file": rel(gpath), "sha256": sha(gpath), "sequence": gif_seq, "note": "nearest-neighbour enlargement for review only; the gait moves the cell in 4 px steps over a ticked floor so foot lock can be judged"},
        },
        "scope": "sentry enemy only; drawn by battle_arena.gd behind ENEMY_SPRITE_PILOT_ENABLED and the nested ENEMY_SPRITE_ANIMATION_ENABLED switch",
        "createdAt": datetime.now().isoformat(timespec="seconds"),
    }
    mpath.write_text(json.dumps(manifest, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(path)
    print(mpath)
    print(fdir)
    print(spath)
    print(gpath)
    print("sha256", manifest["sha256"], "strip", strip.size)


if __name__ == "__main__":
    main()
