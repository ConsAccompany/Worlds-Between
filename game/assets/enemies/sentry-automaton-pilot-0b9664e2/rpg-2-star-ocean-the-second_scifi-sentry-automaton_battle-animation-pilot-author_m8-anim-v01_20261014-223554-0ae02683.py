"""Author the UNAPPROVED native-pixel sentry automaton battle ANIMATION pilot (17 frames, facing left).

This re-poses the exact plates of the static sentry pilot. The static author
script is imported unchanged for its palette, Part class and compositor:
  rpg-2-star-ocean-the-second_scifi-sentry-automaton_battle-idle-pilot-author_m8-v01_20261014-221848-0b9664e2.py
Every coordinate below is the static script's coordinate plus an integer joint
offset: body (belly, shell, dome), head (eye housing, eye, cheek plate, far fin)
and, per leg, hip / knee / foot. Polygon vertices are tagged with the joint they
follow, so a moving knee bends the thigh and shin instead of sliding the leg.
Nothing is read from, traced from or resampled from any image; the neutral pose
must reproduce the static pilot PNG pixel for pixel (asserted).

Frames (one 96x62 cell each, left to right):
  0-3   idle    breathe down 1px on bent knees, eye pulse, scan glance, fin twitch
  4-7   move    diagonal gait: near-front + far-rear lift, then near-rear + far-front
  8-9   windup  rear back, near front leg raised, fin flared, eye charging
  10-11 strike  head ram + near front stomp, rear legs push, eye flash, sparks/dust
  12-13 hit     knocked back, eye shutter half/quarter closed, impact sparks
  14-16 defeat  knees splay, body sinks to the ground, eye and lights go dark

Every frame keeps the static canvas and ground anchor (48, 60): row 60 is the
last opaque row and a near foot is planted on it in every frame.

Usage (bundled Python/Pillow runtime, run with -I):
  python <this file> --out DIR      -> scratch strip + 6x sheet for iteration, no manifest
  python <this file> --final DIR --preview-dir OUT
                                    -> new uniquely named strip PNG + manifest in DIR,
                                       4x review sheet + looping GIF previews in OUT (never overwrites)
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
STATIC_MANIFEST = HERE / "rpg-2-star-ocean-the-second_scifi-sentry-automaton_battle-pilot-manifest_m8-pilot-v01_20261014-221901-e3ab87f9.json"

_spec = importlib.util.spec_from_file_location("sentry_static_author", STATIC_AUTHOR)
static = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(static)

SLUG = static.SLUG
SIZE = static.SIZE
ANCHOR = static.ANCHOR
PALETTE = static.PALETTE
INDEX = static.INDEX
W, H = SIZE

STATES = [
    ("idle", 4, 0.22, "loop"),
    ("move", 4, 0.12, "loop"),
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
    """A static Part whose coordinates are shifted by named joint offsets."""

    def __init__(self, name: str, joints: dict, default: str):
        super().__init__(name)
        self.j = joints
        self.d = default

    def _pt(self, p):
        x, y = p[0], p[1]
        dx, dy = self.j[p[2] if len(p) > 2 else self.d]
        return (x + dx, y + dy)

    def _box(self, x0, y0, x1, y1, tag):
        dx, dy = self.j[tag or self.d]
        return x0 + dx, y0 + dy, x1 + dx, y1 + dy

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
        pts = [(x + dx, y + dy) for x, y in pts]
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
    body, head = p["body"], p["head"]
    lit = p["lights"]
    parts = []

    # Far-side rear leg (static coordinates, joint-tagged).
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

    # Far-side front leg, half hidden behind the eye housing.
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

    # Underslung drive housing.
    r = Rig("belly", {"b": body}, "b")
    r.poly([(32, 25), (80, 25), (75, 35), (38, 35)], "1")
    for x in range(40, 74, 4):
        r.clip_rect(x, 29, x, 33, "2")
    r.oval(50, 28, 58, 36, "b")
    r.oval(52, 30, 56, 34, "a")
    r.px([(51, 30), (52, 29), (53, 29)], "c")
    r.px([(54, 32)], "c")
    parts.append(r)

    # Main carapace.
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
    # Rear status lights: dark when off, white-hot while charging.
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

    # Top sensor dome (may rattle relative to the shell).
    r = Rig("dome", {"d": add(body, p["dome"])}, "d")
    r.oval(55, 2, 63, 9, "3")
    r.clip_oval(56, 3, 61, 6, "4")
    r.px([(58, 4), (59, 4)], "5")
    r.px([(60, 5)], {"on": "y", "bright": "z", "off": "2"}[lit])
    r.rect(55, 7, 63, 8, "b")
    r.px([(56, 7), (57, 7)], "c")
    parts.append(r)

    # Far-side visor fin (follows the head, plus its own flare).
    r = Rig("far_fin", {"f": add(head, p["fin"])}, "f")
    r.poly([(3, 12), (10, 5), (21, 6), (23, 10), (12, 13), (6, 18)], "3")
    r.rim("4", "2")
    r.px([(10, 8), (11, 8), (12, 8)], "1")
    parts.append(r)

    # Near rear leg.
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

    # Near front leg (hip rides with the head).
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

    # Eye housing with its forward status strip.
    r = Rig("eye_housing", {"e": head}, "e")
    r.poly([(8, 17), (13, 10), (29, 9), (35, 15), (35, 32), (29, 38), (14, 38), (8, 32)], "2")
    r.rim("3", "1")
    strip = {"on": ("z", "x", "w"), "bright": ("w", "y", "w"), "off": ("x", "1", "y")}[lit]
    r.rect(33, 20, 33, 25, strip[0])
    r.rect(34, 20, 34, 25, strip[1])
    r.px([(33, 20)], strip[2])
    parts.append(r)

    # Single large eye in a brass bezel; the lens state carries most of the expression.
    eye_joints = {"e": head, "p": add(head, p["pupil"])}
    r = Rig("eye", eye_joints, "e")
    r.oval(10, 12, 30, 32, "c")
    r.clip_poly([(30, 18), (30, 32), (16, 32)], "b")
    r.clip_poly([(10, 12), (23, 12), (10, 25)], "d")
    r.px([(14, 14), (15, 14), (13, 15), (12, 16)], "e")
    r.oval(13, 15, 27, 29, "a")
    paint_lens(r, p["eye"])
    parts.append(r)

    # Near cheek plate.
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
    """Lens rings inside the bezel. 'normal' is the static pilot lens exactly; the glint/core follow the pupil joint."""
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
        # Charging: the cyan core swells and a white-hot centre grows toward the target.
        r.oval(14, 16, 26, 28, "y")
        r.oval(15, 17, 25, 27, "z")
        core = {"charge1": (17, 19, 22, 24), "charge2": (16, 18, 23, 25), "flash": (15, 17, 24, 26)}[mode]
        r.oval(*core, "w", "p")
        if mode != "flash":
            r.clip_poly([(25, 21, "p"), (25, 27, "p"), (19, 27, "p")], "y")
        r.px([(14, 22), (14, 21)], "w" if mode == "flash" else "z")
    elif mode in ("hurt0", "hurt1"):
        # A slate shutter drops over the lens (the concept's folding plates); the iris dims behind it.
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
        assert 0 <= x < W and 0 <= y <= ANCHOR[1], (x, y)
        h = PALETTE[key]
        out[x, y] = (int(h[1:3], 16), int(h[3:5], 16), int(h[5:7], 16), 255)
    return img


def sparks(points, key):
    return [(x, y, key) for x, y in points]


FRAMES = [
    # idle: breathe, pulse, glance
    ("idle", pose()),
    ("idle", pose(body=(0, 1), head=(0, 1), nfl=((0, 1), Z), nrl=((0, 1), Z), ffl=((0, 1), Z), frl=((0, 1), Z))),
    ("idle", pose(body=(0, 1), head=(0, 1), nfl=((0, 1), Z), nrl=((0, 1), Z), ffl=((0, 1), Z), frl=((0, 1), Z),
                  eye="pulse")),
    ("idle", pose(fin=(0, -1), pupil=(-1, 0))),
    # move: diagonal pairs lift and swing forward (toward the party, left)
    ("move", pose(head=(0, -1), nfl=((-1, -2), (-1, -3)), frl=((-1, -2), (-2, -3)), pupil=(-1, 0))),
    ("move", pose(body=(0, 1), head=(0, 1), nfl=((-1, 1), (-1, 0)), nrl=((0, 1), Z), ffl=((0, 1), Z), frl=((-1, 1), (-1, 0)),
                  pupil=(-1, 0))),
    ("move", pose(head=(0, -1), nfl=((-1, 0), (-1, 0)), nrl=((-2, -2), (-2, -3)), ffl=((-1, -2), (-2, -3)), frl=((-1, 0), (-1, 0)),
                  pupil=(-1, 0))),
    ("move", pose(body=(0, 1), head=(0, 1), nfl=((0, 1), Z), nrl=((-1, 1), (-1, 0)), ffl=((-1, 1), (-1, 0)), frl=((0, 1), Z),
                  pupil=(-1, 0))),
    # windup: rear back on the hind legs, near claw-foot raised, fin flared, eye charging
    ("windup", pose(body=(2, 0), head=(2, -1), fin=(0, -1), nfl=((3, -3), (2, -4)), nrl=((1, 0), Z), ffl=((1, 0), Z), frl=((1, 0), Z),
                    eye="charge1", lights="bright")),
    ("windup", pose(body=(3, 1), head=(3, -2), fin=(1, -2), nfl=((5, -5), (4, -7)), nrl=((2, 1), Z), ffl=((2, 0), Z), frl=((2, 1), Z),
                    eye="charge2", lights="bright")),
    # strike: ram forward and down, near foot stamps, hind legs push, flash + sparks + dust
    ("strike", pose(body=(-2, 1), head=(-4, 2), fin=(1, 1), nfl=((-3, 2), Z), nrl=((-2, -1), Z), ffl=((-2, 1), Z), frl=((-2, 0), Z),
                    eye="flash", pupil=(-1, 0), lights="bright",
                    fx=sparks([(1, 18), (0, 22), (2, 26), (1, 30), (3, 14)], "w") + sparks([(0, 16), (2, 20), (0, 28), (3, 33)], "z")
                    + sparks([(0, 57), (18, 58), (19, 57), (0, 59), (18, 60)], "6") + sparks([(17, 59), (20, 59), (1, 52)], "5"))),
    ("strike", pose(body=(-1, 1), head=(-2, 1), nfl=((-2, 1), Z), nrl=((-1, 0), Z), ffl=((-1, 1), Z), frl=((-1, 0), Z),
                    eye="charge1", pupil=(-1, 0),
                    fx=sparks([(1, 21), (2, 29)], "y") + sparks([(0, 55), (19, 56), (21, 58)], "5"))),
    # hit: jolted back away from the party, shutter snaps over the lens, sparks off the bezel
    ("hit", pose(body=(2, 0), head=(3, -1), fin=(1, -1), dome=(1, 0), nfl=((2, 0), Z), nrl=((1, 1), Z), ffl=((1, 0), Z), frl=((1, 1), Z),
                 eye="hurt0",
                 fx=sparks([(8, 11), (6, 14), (9, 9)], "w") + sparks([(5, 12), (7, 8), (4, 16)], "e"))),
    ("hit", pose(body=(1, 0), head=(1, 0), nfl=((1, 0), Z), nrl=((1, 0), Z), ffl=((1, 0), Z), frl=((1, 0), Z),
                 eye="hurt1", fx=sparks([(4, 10), (3, 15)], "d"))),
    # defeat: knees splay, body sinks onto the belly, lights die; feet stay planted on the anchor row
    ("defeat", pose(body=(0, 3), head=(0, 4), fin=(0, 1), nfl=((-2, 3), Z), nrl=((2, 3), Z), ffl=((-1, 3), Z), frl=((1, 3), Z),
                    eye="dim", lights="off")),
    ("defeat", pose(body=(0, 7), head=(-1, 9), fin=(1, 2), nfl=((-3, 7), Z), nrl=((3, 7), Z), ffl=((-2, 7), Z), frl=((2, 7), Z),
                    eye="dark", lights="off")),
    ("defeat", pose(body=(0, 9), head=(-1, 12), fin=(1, 3), dome=(1, 0), nfl=((-4, 9), Z), nrl=((4, 9), Z), ffl=((-3, 9), Z), frl=((3, 9), Z),
                    eye="off", lights="off",
                    fx=sparks([(83, 17), (84, 17), (85, 17), (84, 16), (85, 16), (86, 13), (87, 13), (87, 12), (88, 12)], "5")
                    + sparks([(86, 12), (88, 8), (89, 8), (89, 7)], "6"))),
]


def render_all() -> list[Image.Image]:
    frames = [render(p) for _, p in FRAMES]
    expected = [s for s, n, _, _ in STATES for _ in range(n)]
    assert [s for s, _ in FRAMES] == expected, "frame order must match STATES"
    return frames


def check(frames: list[Image.Image]) -> dict:
    static_png = Image.open(STATIC_PNG).convert("RGBA")
    assert frames[0].tobytes() == static_png.tobytes(), "neutral idle frame must equal the static pilot"
    palette = {tuple(int(h[i:i + 2], 16) for i in (1, 3, 5)) for h in PALETTE.values()}
    report = []
    for i, img in enumerate(frames):
        bbox = img.getbbox()
        assert bbox[3] - 1 == ANCHOR[1], (i, bbox)
        colours = {c[:3] for c in pixels(img) if c[3]}
        assert colours <= palette, (i, colours - palette)
        assert {c[3] for c in pixels(img)} <= {0, 255}
        near_soles = [x for x in range(W) if img.getpixel((x, ANCHOR[1] - 1))[3] and (x <= 17 or x >= 78)]
        report.append({"index": i, "state": FRAMES[i][0], "opaqueBBox": list(bbox), "colourCount": len(colours),
                       "opaquePixels": sum(1 for c in pixels(img) if c[3]),
                       "nearSoleColumnsOnAnchorRowMinus1": [min(near_soles), max(near_soles)] if near_soles else None})
    return {"frames": report}


def pixels(img: Image.Image) -> list:
    return list(img.get_flattened_data() if hasattr(img, "get_flattened_data") else img.getdata())


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
    d.text((pad, 4), "Sentry automaton animation pilot - UNAPPROVED, art acceptance 0 (native 96x62 cells, %dx nearest)" % scale, fill=(230, 230, 230, 255))
    counters = {}
    for i, f in enumerate(frames):
        state = FRAMES[i][0]
        counters[state] = counters.get(state, -1) + 1
        x0 = pad + (i % cols) * cw
        y0 = 18 + pad + (i // cols) * ch
        d.text((x0, y0), "%02d %s %d" % (i, state, counters[state]), fill=(200, 210, 220, 255))
        bg = Image.new("RGBA", SIZE, (118, 122, 128, 255))
        bg.alpha_composite(f)
        big = bg.resize((W * scale, H * scale), Image.NEAREST)
        sheet.paste(big, (x0, y0 + label_h))
        # Anchor row marker.
        ay = y0 + label_h + ANCHOR[1] * scale + scale - 1
        d.line((x0, ay, x0 + W * scale - 1, ay), fill=(255, 80, 60, 255))
    return sheet


def loop_gif(frames, path: Path, scale: int) -> list:
    """Looping GIF preview through every state with runtime-like timings (nearest enlargement, review only)."""
    seq = []
    idx = {s: [i for i, (st, _) in enumerate(FRAMES) if st == s] for s, _, _, _ in STATES}
    for _ in range(2):
        seq += [(i, 220) for i in idx["idle"]]
    for _ in range(2):
        seq += [(i, 120) for i in idx["move"]]
    seq += [(idx["windup"][0], 240), (idx["windup"][1], 240)]
    seq += [(idx["strike"][0], 150), (idx["strike"][1], 150)]
    seq += [(i, 220) for i in idx["idle"]]
    seq += [(idx["hit"][0], 120), (idx["hit"][1], 120)]
    seq += [(i, 220) for i in idx["idle"]]
    seq += [(i, 160) for i in idx["defeat"]] + [(idx["defeat"][-1], 900)]
    imgs = []
    for i, _ in seq:
        bg = Image.new("RGBA", (W + 16, H + 8), (118, 122, 128, 255))
        bg.alpha_composite(frames[i], (8, 4))
        ImageDraw.Draw(bg).line((0, 4 + ANCHOR[1] + 1, W + 15, 4 + ANCHOR[1] + 1), fill=(84, 88, 94, 255))
        imgs.append(bg.resize(((W + 16) * scale, (H + 8) * scale), Image.NEAREST).convert("P", palette=Image.ADAPTIVE, colors=64))
    imgs[0].save(path, save_all=True, append_images=imgs[1:], duration=[d for _, d in seq], loop=0, disposal=2)
    return [[FRAMES[i][0], i, d] for i, d in seq]


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
        print("scratch", args.out, json.dumps([(f["state"], f["opaqueBBox"]) for f in report["frames"]]))
        return
    out_dir: Path = args.final
    prev: Path = args.preview_dir
    root = out_dir.resolve().parents[3]
    stamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    token = uuid.uuid4().hex[:8]
    path = out_dir / f"{SLUG}_scifi-sentry-automaton_battle-animation-strip-left_m8-anim-v01_{stamp}-{token}.png"
    mpath = out_dir / f"{SLUG}_scifi-sentry-automaton_battle-animation-manifest_m8-anim-v01_{stamp}-{token}.json"
    spath = prev / f"{SLUG}_scifi-sentry-automaton-animation-pilot_4x-frame-sheet_m8-anim-v01_{stamp}-{token}.png"
    gpath = prev / f"{SLUG}_scifi-sentry-automaton-animation-pilot_3x-loop-preview_m8-anim-v01_{stamp}-{token}.gif"
    for p in (path, mpath, spath, gpath):
        assert not p.exists(), p
    strip = strip_of(frames)
    strip.save(path)
    review_sheet(frames, 4).save(spath)
    gif_seq = loop_gif(frames, gpath, 3)
    rel = lambda p: str(p.resolve().relative_to(root)).replace("\\", "/")
    sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
    script = Path(__file__).resolve()
    states = {}
    cursor = 0
    for name, count, frame_time, mode in STATES:
        states[name] = {"frames": list(range(cursor, cursor + count)), "frameTime": frame_time, "mode": mode}
        cursor += count
    manifest = {
        "project": SLUG,
        "asset": "scifi sentry automaton battle animation pilot (science-region ruins enemy)",
        "status": "animation_pilot_unapproved",
        "artAccepted": False,
        "artAcceptanceCount": 0,
        "humanReview": "pending - the creator accepted the static sentry's visual direction only ('方向可以，继续完善动作'); this animation is not art-approved",
        "file": rel(path),
        "sha256": sha(path),
        "stripSize": list(strip.size),
        "cellSize": list(SIZE),
        "frameCount": len(frames),
        "groundAnchor": list(ANCHOR),
        "groundAnchorNote": "same canvas and anchor as the static pilot: draw cell at (enemy_x - 48, 272 - 60); row 60 is the last opaque row of every frame",
        "facing": "left (toward party)",
        "states": states,
        "stateTimingNote": "windup frames are selected by remaining wind-up (first half / second half); strike and hit play once; defeat holds its last frame",
        "frameReport": report["frames"],
        "neutralFrameEqualsStaticPilot": True,
        "staticPilot": {"file": rel(STATIC_PNG), "sha256": sha(STATIC_PNG), "manifest": rel(STATIC_MANIFEST)},
        "palette": PALETTE,
        "alphaValues": [0, 255],
        "method": "Re-posed native pixel plates: the static author's palette, Part class and compositor are imported unchanged; every plate uses the static coordinates plus integer body/head/hip/knee/foot joint offsets, and lens/light states are explicit palette paints. A few effect pixels (sparks, dust, smoke) are placed explicitly. No image is read, traced, resampled, resized or generated by AI.",
        "authorScript": rel(script),
        "authorScriptSha256": sha(script),
        "staticAuthorScript": rel(STATIC_AUTHOR),
        "staticAuthorScriptSha256": sha(STATIC_AUTHOR),
        "previews": {
            "frameSheet4x": {"file": rel(spath), "sha256": sha(spath), "note": "nearest-neighbour enlargement for review only"},
            "loopGif3x": {"file": rel(gpath), "sha256": sha(gpath), "sequence": gif_seq, "note": "nearest-neighbour enlargement for review only"},
        },
        "scope": "sentry enemy only; drawn by battle_arena.gd behind ENEMY_SPRITE_PILOT_ENABLED and the nested ENEMY_SPRITE_ANIMATION_ENABLED switch",
        "createdAt": datetime.now().isoformat(timespec="seconds"),
    }
    mpath.write_text(json.dumps(manifest, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(path)
    print(mpath)
    print(spath)
    print(gpath)
    print("sha256", manifest["sha256"], "strip", strip.size)


if __name__ == "__main__":
    main()
