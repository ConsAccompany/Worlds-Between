#!/usr/bin/env python3
"""Build the eight MVP skill VFX as original native pixel art.

One bounded package: eight distinct kind IDs, eight cels each, three editable
role layers per kind, one PXO carrying all eight cels and one middle-cel ORA
role snapshot.  Everything is integer-aligned aliased pixel work; there is no
generated-image paste, text, dither, noise, filtering or opaque flash.  Alpha
is hard-capped at 166 and every composite stays compact around the 32,32 pivot.

Native timing: Pixelorama stores ``frames[].duration`` as a multiplier of
``1/fps``.  At fps 12 each cel stores ``durationSeconds / 8 * 12``, so each
kind's native total equals its manifest ``durationSeconds`` exactly.

The shared native-format helper is loaded through the same portable relative
path convention as the verified common package.  Reference files are never
modified.
"""
from __future__ import annotations

import argparse
import hashlib
import importlib.util
import io
import json
import math
import os
from pathlib import Path
import xml.etree.ElementTree as ET
import zipfile

from PIL import Image, ImageDraw

PROJECT = "rpg-2-star-ocean-the-second"
SUBJECT = "skills"
PREFIX = PROJECT + "_" + SUBJECT + "_"
VARIANT = "skills-v01"
RUN_STAMP = "20261019-210111"
RUN_ID = "4fccfae0"
TAG = VARIANT + "_" + RUN_STAMP + "-" + RUN_ID
SUFFIX = "_" + TAG
SCOPE = "content.vfx.mvp-skills"

W, H = 64, 64
NATIVE_FPS = 12
PIVOT = (32, 32)
MAX_ALPHA = 166
MAX_EVENTS = 24
FRAME_COUNT = 8
ORA_FRAME = 3

KINDS = (
    "personal-hero",
    "personal-liang-xu",
    "personal-zhao-ling",
    "personal-ji-cheng",
    "job-sword",
    "job-firearms",
    "job-tactics",
    "job-relics",
)

DURATIONS = {
    "personal-hero": 0.45,
    "personal-liang-xu": 0.55,
    "personal-zhao-ling": 0.45,
    "personal-ji-cheng": 0.65,
    "job-sword": 0.30,
    "job-firearms": 0.25,
    "job-tactics": 0.55,
    "job-relics": 0.65,
}

LAYERS = {
    "personal-hero": ("teal-focus-brackets", "insight-iris", "converge-sparks"),
    "personal-liang-xu": ("amber-chevron-chain", "sage-signal-pulse", "direction-ticks"),
    "personal-zhao-ling": ("coral-charge-arc", "amber-momentum", "breakthrough-sparks"),
    "personal-ji-cheng": ("blue-glyph-ring", "teal-interference", "orbiting-fragments"),
    "job-sword": ("amber-crescent", "slash-contact", "edge-glints"),
    "job-firearms": ("amber-impact", "paired-rays", "offset-sparks"),
    "job-tactics": ("sage-order-chevrons", "teal-arrangement", "order-ticks"),
    "job-relics": ("teal-seal", "old-gold-corners", "seal-fragments"),
}

# Build / peak / dissipation sampled on eight cels.
ENVELOPES = {
    "personal-hero": (0.20, 0.42, 0.66, 0.88, 1.00, 0.78, 0.48, 0.20),
    "personal-liang-xu": (0.12, 0.30, 0.52, 0.76, 0.94, 1.00, 0.66, 0.28),
    "personal-zhao-ling": (0.12, 0.28, 0.50, 0.72, 0.92, 1.00, 0.70, 0.30),
    "personal-ji-cheng": (0.10, 0.28, 0.50, 0.72, 0.90, 1.00, 0.70, 0.30),
    "job-sword": (0.16, 0.42, 0.74, 1.00, 0.68, 0.40, 0.18, 0.06),
    "job-firearms": (0.35, 0.78, 1.00, 0.58, 0.32, 0.15, 0.07, 0.03),
    "job-tactics": (0.10, 0.26, 0.46, 0.68, 0.86, 1.00, 0.70, 0.30),
    "job-relics": (0.10, 0.26, 0.48, 0.70, 0.88, 1.00, 0.72, 0.32),
}

AMBER_DARK, AMBER_MID = (128, 78, 28), (196, 128, 42)
AMBER_HOT, AMBER_PALE = (240, 184, 80), (250, 220, 136)
TEAL_DARK, TEAL_MID = (24, 80, 86), (54, 138, 140)
TEAL_LIGHT, TEAL_PALE = (104, 192, 184), (166, 230, 212)
CORAL_DARK, CORAL_MID = (132, 64, 56), (190, 104, 88)
CORAL_HOT, CORAL_PALE = (228, 150, 126), (244, 188, 164)
SAGE_DARK, SAGE_MID = (58, 88, 66), (104, 142, 102)
SAGE_LIGHT, SAGE_PALE = (154, 188, 144), (198, 222, 176)
BLUE_DARK, BLUE_MID = (34, 62, 104), (58, 102, 152)
BLUE_LIGHT, BLUE_PALE = (102, 154, 196), (158, 204, 222)
GOLD_DARK, GOLD_MID = (104, 84, 44), (156, 126, 62)
GOLD_LIGHT, GOLD_PALE = (198, 168, 98), (224, 200, 140)


def new_cell() -> Image.Image:
    return Image.new("RGBA", (W, H), (0, 0, 0, 0))


def color(rgb: tuple[int, int, int], alpha: float) -> tuple[int, int, int, int]:
    a = max(0, min(MAX_ALPHA, int(round(alpha))))
    return (rgb[0], rgb[1], rgb[2], a)


def clamp01(value: float) -> float:
    return max(0.0, min(1.0, value))


def arc_points(cx: int, cy: int, radius: float, a0: float, a1: float,
               steps: int) -> list[tuple[int, int]]:
    points = []
    for i in range(steps + 1):
        angle = math.radians(a0 + (a1 - a0) * i / steps)
        points.append((int(round(cx + math.cos(angle) * radius)),
                       int(round(cy + math.sin(angle) * radius))))
    return points


def arc(draw: ImageDraw.ImageDraw, cx: int, cy: int, radius: float, a0: float,
        a1: float, rgba, width: int = 1, steps: int = 16) -> None:
    draw.line(arc_points(cx, cy, radius, a0, a1, steps), fill=rgba,
              width=width, joint="curve")


def diamond(draw: ImageDraw.ImageDraw, x: int, y: int, radius: int, rgba) -> None:
    for dy in range(-radius, radius + 1):
        span = radius - abs(dy)
        for dx in range(-span, span + 1):
            draw.point((x + dx, y + dy), fill=rgba)


def cross(draw: ImageDraw.ImageDraw, x: int, y: int, arm: int, rgba) -> None:
    draw.line((x - arm, y, x + arm, y), fill=rgba, width=1)
    draw.line((x, y - arm, x, y + arm), fill=rgba, width=1)


def chevron(draw: ImageDraw.ImageDraw, x: int, y: int, size: int, rgba) -> None:
    draw.line([(x - size, y - size), (x, y)], fill=rgba, width=1)
    draw.line([(x, y), (x - size, y + size)], fill=rgba, width=1)


def pixel(draw: ImageDraw.ImageDraw, x: int, y: int, rgba) -> None:
    if 0 <= x < W and 0 <= y < H:
        draw.point((x, y), fill=rgba)


# ---------------------------------------------------------------------------
# personal-hero: restrained teal focusing brackets converging at eye level.
# ---------------------------------------------------------------------------
def build_personal_hero(f: int) -> dict[str, Image.Image]:
    out = {name: new_cell() for name in LAYERS["personal-hero"]}
    env = ENVELOPES["personal-hero"][f]
    cx, cy = 32, 28
    conv = 16.0 - 8.0 * env

    # Four L-brackets close in on the weapon/eye-level focus, then relax.
    d = ImageDraw.Draw(out["teal-focus-brackets"])
    for sx in (-1, 1):
        for sy in (-1, 1):
            x = cx + int(round(sx * conv))
            y = cy + int(round(sy * conv * 0.9))
            arm = 3
            d.line([(x, y), (x - sx * arm, y)],
                   fill=color(TEAL_LIGHT, 148 * env), width=1)
            d.line([(x, y), (x, y - sy * arm)],
                   fill=color(TEAL_LIGHT, 148 * env), width=1)
            pixel(d, x, y, color(TEAL_PALE, 160 * env))
            if env > 0.55:
                pixel(d, x - sx, y - sy, color(TEAL_MID, 96 * env))
    # Thin sightlines keep the cue readable as focus rather than a cage.
    reach = int(round(conv * 0.62))
    for sx in (-1, 1):
        d.line([(cx + sx * (reach + 2), cy), (cx + sx * 3, cy)],
               fill=color(TEAL_MID, 106 * env), width=1)
    if f >= 1:
        d.line([(cx, cy - int(round(conv * 0.9)) + 3),
                (cx, cy - 4)], fill=color(TEAL_DARK, 78 * env), width=1)
        d.line([(cx, cy + 4),
                (cx, cy + int(round(conv * 0.9)) - 3)],
               fill=color(TEAL_DARK, 78 * env), width=1)

    # A small insight iris; no filled disc and no white flash.
    d = ImageDraw.Draw(out["insight-iris"])
    diamond(d, cx, cy, 1, color(TEAL_LIGHT, 132 * env))
    pixel(d, cx, cy, color(TEAL_PALE, 158 * env))
    d.line([(cx - 3, cy), (cx - 1, cy)], fill=color(TEAL_MID, 112 * env))
    d.line([(cx + 1, cy), (cx + 3, cy)], fill=color(TEAL_MID, 112 * env))
    pixel(d, cx, cy - 2, color(TEAL_LIGHT, 120 * env))
    pixel(d, cx, cy + 2, color(TEAL_LIGHT, 120 * env))
    if f >= 2:
        arc(d, cx, cy, 4, -72, -18, color(TEAL_MID, 88 * env), width=1, steps=7)
        arc(d, cx, cy, 4, 18, 72, color(TEAL_MID, 88 * env), width=1, steps=7)

    # Four diagonal motes converge; sparse and fully deterministic.
    d = ImageDraw.Draw(out["converge-sparks"])
    r = 13.0 - 6.0 * env
    for index, (sx, sy) in enumerate(((1, 1), (1, -1), (-1, 1), (-1, -1))):
        x = cx + int(round(sx * r))
        y = cy + int(round(sy * r * 0.72))
        x2 = cx + int(round(sx * (r - 2.5)))
        y2 = cy + int(round(sy * (r - 2.5) * 0.72))
        d.line([(x, y), (x2, y2)],
               fill=color(TEAL_PALE if index % 2 == 0 else TEAL_LIGHT, 124 * env),
               width=1)
        if f >= 2:
            pixel(d, x + sx, y + sy, color(TEAL_MID, 86 * env))
    return out


# ---------------------------------------------------------------------------
# personal-liang-xu: amber linked chevrons with a sage signal pulse.
# ---------------------------------------------------------------------------
def build_personal_liang_xu(f: int) -> dict[str, Image.Image]:
    out = {name: new_cell() for name in LAYERS["personal-liang-xu"]}
    env = ENVELOPES["personal-liang-xu"][f]
    q = f / 7.0
    chain = ((19, 36), (27, 32), (35, 28))

    # A relay of three directional chevrons; each lights in turn.
    d = ImageDraw.Draw(out["amber-chevron-chain"])
    for index, (x, y) in enumerate(chain):
        pulse = clamp01((f - index * 1.5) / 4.0)
        local = env * (0.34 + 0.66 * pulse)
        rgb = AMBER_HOT if index == 2 else AMBER_MID
        chevron(d, x, y, 3, color(rgb, 148 * local))
        pixel(d, x, y, color(AMBER_PALE, 158 * local))
        if index > 0:
            px0, py0 = chain[index - 1]
            d.line([(px0 + 1, py0), (x - 3, y)],
                   fill=color(AMBER_DARK, 92 * local), width=1)
        if f >= 2 + index:
            d.line([(x + 1, y), (x + 2, y)],
                   fill=color(AMBER_PALE, 132 * local), width=1)
            pixel(d, x - 1, y - 1, color(AMBER_HOT, 104 * local))

    # Sage pulse: broken concentric arcs, never a closed ring.
    d = ImageDraw.Draw(out["sage-signal-pulse"])
    base = 6 + int(round(7 * env))
    for ring in range(2):
        radius = base + ring * 3
        fade = 132 * env / (1 + ring * 0.45)
        for a0, a1 in ((-75, -25), (25, 75), (105, 155), (205, 255)):
            arc(d, 30, 32, radius, a0, a1,
                color(SAGE_LIGHT if ring == 0 else SAGE_MID, fade),
                width=1, steps=8)
    diamond(d, 18, 38, 1, color(SAGE_MID, 108 * env))
    pixel(d, 18, 38, color(SAGE_PALE, 142 * env))
    d.line([(20, 37), (23, 36)], fill=color(SAGE_LIGHT, 96 * env), width=1)
    if f >= 3:
        arc(d, 18, 38, 4, -48, 48, color(SAGE_DARK, 78 * env), width=1, steps=8)

    # Direction ticks trail the relay and settle during dissipation.
    d = ImageDraw.Draw(out["direction-ticks"])
    travel = int(round(q * 3))
    for index, (x, y) in enumerate(chain):
        tx = x - 6 - travel
        d.line([(tx, y), (tx + 2, y)],
               fill=color(SAGE_LIGHT if index % 2 else AMBER_MID, 104 * env),
               width=1)
        if index == 2:
            d.line([(tx - 2, y - 2), (tx, y)],
                   fill=color(AMBER_HOT, 96 * env), width=1)
            d.line([(tx - 2, y + 2), (tx, y)],
                   fill=color(AMBER_HOT, 96 * env), width=1)
    for index in range(3):
        x = 15 + index * 4 - travel
        y = 41 + index % 2
        pixel(d, x, y, color(AMBER_DARK, 86 * env))
        pixel(d, x + 1, y, color(SAGE_MID, 68 * env))
    return out


# ---------------------------------------------------------------------------
# personal-zhao-ling: controlled coral/amber forward charge arc.
# ---------------------------------------------------------------------------
def build_personal_zhao_ling(f: int) -> dict[str, Image.Image]:
    out = {name: new_cell() for name in LAYERS["personal-zhao-ling"]}
    env = ENVELOPES["personal-zhao-ling"][f]
    q = f / 7.0
    cx, cy = 29, 32
    radius = int(round(8 + 5 * env))
    span = 35 + 30 * env
    tip_x = cx + radius + 1

    # Coral outer charge bow, deliberately open at the forward lip.
    d = ImageDraw.Draw(out["coral-charge-arc"])
    for index, (a0, a1) in enumerate(((-span, -8), (8, span))):
        arc(d, cx, cy, radius, a0, a1,
            color(CORAL_HOT if index == 0 else CORAL_MID, 138 * env),
            width=2 if f in (4, 5) else 1, steps=14)
    if f >= 2:
        arc(d, cx, cy, radius + 3, -span * 0.68, span * 0.68,
            color(CORAL_DARK, 82 * env), width=1, steps=14)
    pixel(d, tip_x, cy, color(CORAL_PALE, 152 * env))
    d.line([(tip_x - 2, cy - 2), (tip_x, cy)],
           fill=color(CORAL_HOT, 132 * env), width=1)
    d.line([(tip_x - 2, cy + 2), (tip_x, cy)],
           fill=color(CORAL_HOT, 132 * env), width=1)

    # Amber momentum sits inside the bow and points the charge forward.
    d = ImageDraw.Draw(out["amber-momentum"])
    inner = int(round(5 + 4 * env))
    arc(d, cx, cy, inner, -span * 0.62, span * 0.62,
        color(AMBER_MID, 124 * env), width=1, steps=12)
    d.line([(cx - 4, cy), (cx + inner, cy)],
           fill=color(AMBER_HOT, 104 * env), width=1)
    pixel(d, cx + inner + 1, cy, color(AMBER_PALE, 148 * env))
    diamond(d, cx, cy, 1, color(AMBER_MID, 98 * env))
    pixel(d, cx, cy, color(AMBER_PALE, 118 * env))

    # A short forward fan sells the breakthrough without becoming a beam.
    d = ImageDraw.Draw(out["breakthrough-sparks"])
    for index, angle in enumerate((-32, 0, 32)):
        rad = math.radians(angle)
        r0 = 1 + env
        r1 = 3 + 4 * env
        x0 = tip_x + int(round(math.cos(rad) * r0))
        y0 = cy + int(round(math.sin(rad) * r0))
        x1 = tip_x + int(round(math.cos(rad) * r1))
        y1 = cy + int(round(math.sin(rad) * r1))
        d.line([(x0, y0), (x1, y1)],
               fill=color(CORAL_PALE if index == 1 else AMBER_HOT, 132 * env),
               width=1)
    for index, y in enumerate((27, 37)):
        x = cx - radius - 2 + int(round(q * 2))
        d.line([(x, y), (x + 2, y)],
               fill=color(AMBER_DARK, 88 * env), width=1)
        if f <= 3:
            pixel(d, x - 1, y, color(CORAL_MID, 72 * env))
    return out


# ---------------------------------------------------------------------------
# personal-ji-cheng: blue/teal broken glyph ring and sparse orbital fragments.
# ---------------------------------------------------------------------------
def build_personal_ji_cheng(f: int) -> dict[str, Image.Image]:
    out = {name: new_cell() for name in LAYERS["personal-ji-cheng"]}
    env = ENVELOPES["personal-ji-cheng"][f]
    cx, cy = 32, 32
    radius = 11

    # Broken ring: eight short arcs with eight separate angular glyph marks.
    d = ImageDraw.Draw(out["blue-glyph-ring"])
    spin = f * 4
    for index in range(8):
        a0 = index * 45 + 18 + spin
        arc(d, cx, cy, radius, a0, a0 + 16,
            color(BLUE_MID if index % 2 else BLUE_DARK, 108 * env),
            width=1, steps=6)
        angle = math.radians(index * 45 + spin)
        x = cx + int(round(math.cos(angle) * radius))
        y = cy + int(round(math.sin(angle) * radius))
        tx = int(round(-math.sin(angle)))
        ty = int(round(math.cos(angle)))
        nx = int(round(math.cos(angle)))
        ny = int(round(math.sin(angle)))
        radial = 1 if index % 2 == 0 else -1
        d.line([(x, y), (x + tx * 2, y + ty * 2)],
               fill=color(BLUE_LIGHT if index % 3 else BLUE_PALE, 142 * env),
               width=1)
        d.line([(x, y), (x + nx * radial * 2, y + ny * radial * 2)],
               fill=color(BLUE_MID, 118 * env), width=1)
        pixel(d, x, y, color(BLUE_PALE, 150 * env))
    # Inner broken seal ring keeps the glyph structure readable at 1x.
    for index in range(4):
        a0 = index * 90 + 12 - spin * 0.5
        arc(d, cx, cy, 6, a0, a0 + 32,
            color(TEAL_MID, 92 * env), width=1, steps=6)
    diamond(d, cx, cy, 1, color(TEAL_LIGHT, 96 * env))

    # Deterministic records interference: offset scan slices and corner tears.
    d = ImageDraw.Draw(out["teal-interference"])
    for index, y in enumerate((26, 30, 34, 38)):
        shift = ((f * 2 + index * 3) % 7) - 3
        x0 = 22 + shift
        d.line([(x0, y), (x0 + 7, y)], fill=color(TEAL_LIGHT, 108 * env), width=1)
        d.line([(x0 + 11, y), (x0 + 17, y)],
               fill=color(TEAL_MID, 92 * env), width=1)
        if index % 2 == 0:
            pixel(d, x0 + 9, y - 1, color(TEAL_PALE, 118 * env))
    for index, (bx, by) in enumerate(((24, 24), (38, 28), (26, 40), (40, 36))):
        ox = (f + index) % 3
        d.line([(bx + ox, by), (bx + ox + 1, by)],
               fill=color(TEAL_PALE if index % 2 == 0 else BLUE_LIGHT, 124 * env),
               width=1)
    d.line([(43, 29), (43, 31)], fill=color(TEAL_MID, 88 * env), width=1)
    d.line([(21, 33), (21, 36)], fill=color(TEAL_MID, 88 * env), width=1)

    # Five sparse angular fragments orbit the glyph ring.
    d = ImageDraw.Draw(out["orbiting-fragments"])
    for index in range(5):
        angle = math.radians(index * 72 + f * 13 + 10)
        orbit = 15 + index % 2
        x = cx + int(round(math.cos(angle) * orbit))
        y = cy + int(round(math.sin(angle) * orbit))
        rgba = color(BLUE_PALE if index % 2 == 0 else TEAL_LIGHT, 142 * env)
        pixel(d, x, y, rgba)
        if index in (0, 3):
            d.line([(x, y), (x + (1 if math.cos(angle) >= 0 else -1), y)],
                   fill=color(BLUE_MID, 100 * env), width=1)
        if index == 1:
            pixel(d, x, y - 1, color(TEAL_MID, 92 * env))
    return out


# ---------------------------------------------------------------------------
# job-sword: one precise amber crescent contact slash.
# ---------------------------------------------------------------------------
def build_job_sword(f: int) -> dict[str, Image.Image]:
    out = {name: new_cell() for name in LAYERS["job-sword"]}
    env = ENVELOPES["job-sword"][f]
    q = f / 7.0
    cx, cy = 31, 32
    radius = int(round(9 + 4 * env))
    half = 28 + 34 * env
    tip_x = cx + radius

    # A single warm crescent; width only thickens around the contact frames.
    d = ImageDraw.Draw(out["amber-crescent"])
    arc(d, cx, cy, radius, -half, half, color(AMBER_HOT, 152 * env),
        width=2 if f in (2, 3, 4) else 1, steps=26)
    left = arc_points(cx, cy, radius, -half, -half, 1)[0]
    right = arc_points(cx, cy, radius, half, half, 1)[0]
    pixel(d, left[0], left[1], color(AMBER_PALE, 134 * env))
    pixel(d, right[0], right[1], color(AMBER_PALE, 134 * env))

    # Contact: a perpendicular notch and inner echo, not an expanding ring.
    d = ImageDraw.Draw(out["slash-contact"])
    d.line([(tip_x, cy - 2), (tip_x, cy + 2)],
           fill=color(AMBER_PALE, 148 * env), width=1)
    pixel(d, tip_x + 1, cy, color(AMBER_PALE, 154 * env))
    if f >= 1:
        arc(d, cx, cy, max(3, radius - 4), -half * 0.52, half * 0.52,
            color(AMBER_MID, 108 * env), width=1, steps=12)
    d.line([(cx - radius - 1, cy), (cx - radius + 1, cy)],
           fill=color(AMBER_DARK, 94 * env), width=1)
    if f >= 4:
        pixel(d, tip_x - 2, cy, color(AMBER_MID, 80 * env))

    # Three edge glints and two trailing ticks, kept off the body.
    d = ImageDraw.Draw(out["edge-glints"])
    for index, angle in enumerate((-half * 0.74, 0, half * 0.74)):
        rad = math.radians(angle)
        x = cx + int(round(math.cos(rad) * (radius + 2)))
        y = cy + int(round(math.sin(rad) * (radius + 2)))
        pixel(d, x, y, color(AMBER_PALE if index == 1 else AMBER_HOT, 146 * env))
        if index == 1:
            pixel(d, x + 1, y, color(AMBER_PALE, 128 * env))
    trail = int(round(q * 4))
    for index, y in enumerate((28, 36)):
        x = cx - radius - 4 - trail
        d.line([(x, y), (x + 2, y)], fill=color(AMBER_DARK, 84 * env), width=1)
    return out


# ---------------------------------------------------------------------------
# job-firearms: compact tracer impact with short offset paired rays.
# ---------------------------------------------------------------------------
def build_job_firearms(f: int) -> dict[str, Image.Image]:
    out = {name: new_cell() for name in LAYERS["job-firearms"]}
    env = ENVELOPES["job-firearms"][f]
    cx, cy = 32, 32

    # Target impact only: a small hot core with cardinal chips, no beam.
    d = ImageDraw.Draw(out["amber-impact"])
    diamond(d, cx, cy, 1, color(AMBER_HOT, 148 * env))
    pixel(d, cx, cy, color(AMBER_PALE, 160 * env))
    for index, (dx, dy) in enumerate(((1, 0), (-1, 0), (0, 1), (0, -1))):
        pixel(d, cx + dx * 2, cy + dy * 2,
              color(AMBER_MID if index % 2 else AMBER_HOT, 106 * env))
    d.line([(cx + 2, cy), (cx + 3, cy)], fill=color(AMBER_PALE, 124 * env), width=1)

    # Exactly two short rays, offset above and below the core with a gap.
    d = ImageDraw.Draw(out["paired-rays"])
    reach = int(round(5 + 3 * env))
    for side in (-1, 1):
        x0 = cx + 2
        y0 = cy + side * 3
        x1 = cx + reach
        y1 = y0 + side
        d.line([(x0, y0), (x1, y1)],
               fill=color(AMBER_HOT if side < 0 else AMBER_PALE, 146 * env),
               width=1)
        pixel(d, x1, y1, color(AMBER_PALE, 150 * env))

    # Sparse offset debris reinforces a stopped tracer, still no long trail.
    d = ImageDraw.Draw(out["offset-sparks"])
    drift = int(round(env * 2))
    for index, (dx, dy) in enumerate(((3, -5), (6, -2), (6, 2), (3, 5))):
        x = cx + dx + drift
        y = cy + dy
        pixel(d, x, y, color(AMBER_PALE if index % 2 else AMBER_MID, 128 * env))
        if index in (0, 3):
            pixel(d, x + 1, y - (1 if dy < 0 else -1),
                  color(AMBER_DARK, 78 * env))
    return out


# ---------------------------------------------------------------------------
# job-tactics: sage/teal arrangement pulse of three ordered chevrons.
# ---------------------------------------------------------------------------
def build_job_tactics(f: int) -> dict[str, Image.Image]:
    out = {name: new_cell() for name in LAYERS["job-tactics"]}
    env = ENVELOPES["job-tactics"][f]
    q = f / 7.0
    rows = (24, 32, 40)
    tip_x = 37

    # Three parallel chevrons pulse top-to-bottom in formation order.
    d = ImageDraw.Draw(out["sage-order-chevrons"])
    for index, y in enumerate(rows):
        pulse = clamp01((f - index * 1.5) / 4.0)
        local = env * (0.45 + 0.55 * pulse)
        chevron(d, tip_x, y, 4, color(SAGE_LIGHT, 150 * local))
        pixel(d, tip_x, y, color(SAGE_PALE, 158 * local))
        if pulse > 0.15:
            pixel(d, tip_x + 1, y, color(TEAL_PALE, 126 * local))
            d.line([(tip_x - 2, y - 2), (tip_x - 1, y)],
                   fill=color(SAGE_PALE, 112 * local), width=1)
            d.line([(tip_x - 2, y + 2), (tip_x - 1, y)],
                   fill=color(SAGE_PALE, 112 * local), width=1)

    # Teal arrangement rail and travelling pulse frame the three orders.
    d = ImageDraw.Draw(out["teal-arrangement"])
    d.line([(23, 20), (23, 28)], fill=color(TEAL_MID, 106 * env), width=1)
    d.line([(23, 36), (23, 44)], fill=color(TEAL_MID, 106 * env), width=1)
    for y in rows:
        d.line([(23, y), (30, y)], fill=color(TEAL_DARK, 92 * env), width=1)
        pixel(d, 23, y, color(TEAL_LIGHT, 124 * env))
    diamond(d, 23, 32, 1, color(TEAL_MID, 88 * env))
    pulse_y = 20 + int(round(q * 24))
    d.line([(22, pulse_y), (24, pulse_y)],
           fill=color(TEAL_PALE, 144 * env), width=1)
    pixel(d, 23, pulse_y, color(TEAL_PALE, 158 * env))
    pixel(d, 21, pulse_y, color(TEAL_DARK, 82 * env))

    # Echo count increases down the formation, making order legible sans text.
    d = ImageDraw.Draw(out["order-ticks"])
    for index, y in enumerate(rows):
        for echo in range(index + 1):
            x = 31 - echo * 4
            local = env * (0.72 - echo * 0.13)
            chevron(d, x, y, 2,
                    color(TEAL_LIGHT if echo % 2 == 0 else SAGE_MID, 96 * local))
            pixel(d, x, y, color(SAGE_PALE, 112 * local))
    return out


# ---------------------------------------------------------------------------
# job-relics: muted teal/old-gold angular seal with broken concentric corners.
# ---------------------------------------------------------------------------
def build_job_relics(f: int) -> dict[str, Image.Image]:
    out = {name: new_cell() for name in LAYERS["job-relics"]}
    env = ENVELOPES["job-relics"][f]
    q = f / 7.0
    cx, cy = 32, 32
    radius = 12 + int(round(env))

    # Octagonal seal: eight shortened straight edges leave every corner broken.
    d = ImageDraw.Draw(out["teal-seal"])
    vertices = []
    for index in range(8):
        angle = math.radians(index * 45 + 22.5)
        vertices.append((cx + int(round(math.cos(angle) * radius)),
                         cy + int(round(math.sin(angle) * radius))))
    for index in range(8):
        x0, y0 = vertices[index]
        x1, y1 = vertices[(index + 1) % 8]
        dx, dy = x1 - x0, y1 - y0
        length = max(1.0, math.hypot(dx, dy))
        ux, uy = dx / length, dy / length
        trim = 1.6
        d.line([(int(round(x0 + ux * trim)), int(round(y0 + uy * trim))),
                (int(round(x1 - ux * trim)), int(round(y1 - uy * trim)))],
               fill=color(TEAL_LIGHT if index % 2 == 0 else TEAL_MID, 132 * env),
               width=1)
    # Inner concentric diamond seal, also broken at its four corners.
    inner = 6
    diamond_vertices = ((cx, cy - inner), (cx + inner, cy),
                        (cx, cy + inner), (cx - inner, cy))
    for index in range(4):
        x0, y0 = diamond_vertices[index]
        x1, y1 = diamond_vertices[(index + 1) % 4]
        d.line([(x0 + (1 if index in (0, 1) else -1), y0 + 1),
                (x1 - (1 if index in (1, 2) else -1), y1 - 1)],
               fill=color(TEAL_DARK, 104 * env), width=1)
    diamond(d, cx, cy, 1, color(TEAL_MID, 88 * env))
    pixel(d, cx, cy, color(TEAL_PALE, 134 * env))

    # Old-gold corner brackets at two radii; the inner set lights at peak.
    d = ImageDraw.Draw(out["old-gold-corners"])
    for sx in (-1, 1):
        for sy in (-1, 1):
            x = cx + sx * 16
            y = cy + sy * 16
            arm = 3
            d.line([(x, y), (x - sx * arm, y)],
                   fill=color(GOLD_MID, 136 * env), width=1)
            d.line([(x, y), (x, y - sy * arm)],
                   fill=color(GOLD_MID, 136 * env), width=1)
            pixel(d, x, y, color(GOLD_PALE, 146 * env))
            if env > 0.55:
                ix = cx + sx * 9
                iy = cy + sy * 9
                d.line([(ix, iy), (ix - sx * 2, iy)],
                       fill=color(GOLD_LIGHT, 118 * env), width=1)
                d.line([(ix, iy), (ix, iy - sy * 2)],
                       fill=color(GOLD_LIGHT, 118 * env), width=1)
                pixel(d, ix, iy, color(GOLD_PALE, 132 * env))

    # Six angular seal chips drift outward along the diagonals and cardinals.
    d = ImageDraw.Draw(out["seal-fragments"])
    angles = (45, 90, 135, 215, 270, 325)
    drift = int(round(2 + 3 * env))
    for index, angle in enumerate(angles):
        rad = math.radians(angle + q * 6)
        orbit = 14 + drift + index % 2
        x = cx + int(round(math.cos(rad) * orbit))
        y = cy + int(round(math.sin(rad) * orbit))
        rgba = color(GOLD_LIGHT if index % 2 == 0 else TEAL_MID, 128 * env)
        pixel(d, x, y, rgba)
        if index in (0, 2, 4):
            d.line([(x, y), (x + (1 if x >= cx else -1), y)],
                   fill=color(GOLD_DARK, 88 * env), width=1)
    return out


BUILDERS = {
    "personal-hero": build_personal_hero,
    "personal-liang-xu": build_personal_liang_xu,
    "personal-zhao-ling": build_personal_zhao_ling,
    "personal-ji-cheng": build_personal_ji_cheng,
    "job-sword": build_job_sword,
    "job-firearms": build_job_firearms,
    "job-tactics": build_job_tactics,
    "job-relics": build_job_relics,
}


def combine(layers: dict[str, Image.Image]) -> Image.Image:
    out = new_cell()
    for name in layers:
        out.alpha_composite(layers[name])
    return out


def clamp_alpha(img: Image.Image) -> None:
    alpha = img.getchannel("A").point(lambda value: min(value, MAX_ALPHA))
    img.putalpha(alpha)


def isolate_layer_alpha(layers: dict[str, Image.Image]) -> None:
    """Let only the topmost role own each pixel, keeping roles crisp and capped."""
    names = list(layers)
    pixels = [layers[name].load() for name in names]
    for y in range(H):
        for x in range(W):
            top = -1
            for index in range(len(names)):
                if pixels[index][x, y][3] > 0:
                    top = index
            if top < 0:
                continue
            for index in range(len(names)):
                if index != top and pixels[index][x, y][3] > 0:
                    pixels[index][x, y] = (0, 0, 0, 0)


def png_bytes(img: Image.Image) -> bytes:
    buf = io.BytesIO()
    img.save(buf, format="PNG", compress_level=9)
    return buf.getvalue()


def save_png(img: Image.Image, path: Path) -> None:
    img.save(path, format="PNG", compress_level=9)


def sha256_bytes(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def helper_path() -> Path:
    here = Path(__file__).resolve()
    return here.parent.parent / "inputs" / (
        PROJECT + "_benchmark_native-format-helper_v01_20261018-234437-8dfccbf6.py"
    )


def load_helper():
    helper = helper_path()
    spec = importlib.util.spec_from_file_location("shared_native_helper", helper)
    if spec is None or spec.loader is None:
        raise RuntimeError("cannot load shared native-format helper")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def validate_cell(img: Image.Image, label: str, require_content: bool = True) -> None:
    if img.size != (W, H):
        raise RuntimeError(f"{label}: expected 64x64, got {img.size}")
    if img.mode != "RGBA":
        raise RuntimeError(f"{label}: expected RGBA")
    alpha_max = img.getchannel("A").getextrema()[1]
    if alpha_max > MAX_ALPHA:
        raise RuntimeError(f"{label}: alpha {alpha_max} exceeds {MAX_ALPHA}")
    bbox = img.getbbox()
    if bbox is None:
        if require_content:
            raise RuntimeError(f"{label}: empty role/cell")
        return
    if bbox[0] < 10 or bbox[1] < 10 or bbox[2] > 54 or bbox[3] > 54:
        raise RuntimeError(f"{label}: silhouette not compact: {bbox}")


def validate_pxo(path: Path, kind: str, expected_duration: float,
                 layer_roles: tuple[str, ...]) -> None:
    with zipfile.ZipFile(path) as archive:
        names = set(archive.namelist())
        if "data.json" not in names or "preview.png" not in names:
            raise RuntimeError(f"{path.name}: missing PXO core members")
        if archive.read("mimetype") != b"application/x-pixelorama":
            raise RuntimeError(f"{path.name}: bad PXO mimetype")
        data = json.loads(archive.read("data.json"))
        if data.get("fps") != NATIVE_FPS:
            raise RuntimeError(f"{path.name}: fps is not native 12")
        if data.get("size_x") != W or data.get("size_y") != H:
            raise RuntimeError(f"{path.name}: wrong PXO cell size")
        if [layer["name"] for layer in data["layers"]] != list(layer_roles):
            raise RuntimeError(f"{path.name}: layer roles do not match")
        if len(data["frames"]) != FRAME_COUNT:
            raise RuntimeError(f"{path.name}: not eight cels")
        native_total = sum(float(frame["duration"]) for frame in data["frames"])
        if abs(native_total / NATIVE_FPS - expected_duration) > 1e-6:
            raise RuntimeError(f"{path.name}: native duration mismatch")
        preview = Image.open(io.BytesIO(archive.read("preview.png")))
        validate_cell(preview.convert("RGBA"), f"{path.name} preview")
        for frame_index in range(1, FRAME_COUNT + 1):
            for layer_index in range(1, len(layer_roles) + 1):
                member = f"image_data/frames/{frame_index}/layer_{layer_index}"
                if member not in names:
                    raise RuntimeError(f"{path.name}: missing {member}")
                if len(archive.read(member)) != W * H * 4:
                    raise RuntimeError(f"{path.name}: bad raw cel length")
            if f"image_data/frames/{frame_index}/" not in names:
                raise RuntimeError(f"{path.name}: missing frame directory")
        if kind not in BUILDERS:
            raise RuntimeError(f"{path.name}: unknown kind {kind}")


def validate_ora(path: Path, layer_roles: tuple[str, ...]) -> None:
    with zipfile.ZipFile(path) as archive:
        names = set(archive.namelist())
        if "mimetype" not in names or "mergedimage.png" not in names:
            raise RuntimeError(f"{path.name}: missing ORA core members")
        if archive.read("mimetype") != b"image/openraster":
            raise RuntimeError(f"{path.name}: bad ORA mimetype")
        root = ET.fromstring(archive.read("stack.xml"))
        stack = root.find("stack")
        if stack is None:
            raise RuntimeError(f"{path.name}: missing ORA stack")
        ora_layers = [layer.get("name") for layer in stack.findall("layer")]
        if ora_layers != list(reversed(layer_roles)):
            raise RuntimeError(f"{path.name}: ORA role layers do not match")
        for layer in stack.findall("layer"):
            src = layer.get("src")
            if src not in names:
                raise RuntimeError(f"{path.name}: missing ORA layer {src}")
        merged = Image.open(io.BytesIO(archive.read("mergedimage.png"))).convert("RGBA")
        validate_cell(merged, f"{path.name} mergedimage")


def build(out_dir: Path) -> dict:
    out_dir.mkdir(parents=True, exist_ok=True)
    helper = load_helper()
    source_path = Path(__file__).resolve()
    helper_file = helper_path().resolve()
    source_rel = Path(os.path.relpath(source_path, out_dir)).as_posix()
    helper_rel = Path(os.path.relpath(helper_file, out_dir)).as_posix()
    source_sha = sha256_file(source_path)
    helper_sha = sha256_file(helper_file)

    events = {}
    artifacts: dict[str, str] = {}

    for kind in KINDS:
        # Pixelorama multiplies each cel duration by 1/fps at play time.
        native_multiplier = DURATIONS[kind] / 8.0 * NATIVE_FPS
        layers_by_frame = [BUILDERS[kind](f) for f in range(FRAME_COUNT)]
        for frame_index, frame_layers in enumerate(layers_by_frame):
            if list(frame_layers) != list(LAYERS[kind]):
                raise RuntimeError(f"{kind}: role order drift")
            for role, img in frame_layers.items():
                clamp_alpha(img)
            isolate_layer_alpha(frame_layers)
            for role, img in frame_layers.items():
                validate_cell(img, f"{kind} f{frame_index} {role}")
        composites = [combine(layers_by_frame[f]) for f in range(FRAME_COUNT)]
        for frame_index, composite in enumerate(composites):
            validate_cell(composite, f"{kind} f{frame_index} composite")

        frame_names = []
        for f in range(FRAME_COUNT):
            fname = PREFIX + kind + f"_frame-{f:02d}" + SUFFIX + ".png"
            save_png(composites[f], out_dir / fname)
            frame_names.append(fname)
            artifacts[fname] = sha256_file(out_dir / fname)

        pxo_name = PREFIX + kind + "_8cel" + SUFFIX + ".pxo"
        ora_name = PREFIX + kind + "_middle-layered" + SUFFIX + ".ora"
        pxo_data = helper.pxo_bytes(
            layers_by_frame,
            [native_multiplier] * FRAME_COUNT,
            png_bytes(composites[ORA_FRAME]),
            pxo_name,
        )
        (out_dir / pxo_name).write_bytes(pxo_data)
        artifacts[pxo_name] = sha256_bytes(pxo_data)
        validate_pxo(out_dir / pxo_name, kind, DURATIONS[kind], LAYERS[kind])

        ora_data = helper.ora_bytes(layers_by_frame[ORA_FRAME])
        (out_dir / ora_name).write_bytes(ora_data)
        artifacts[ora_name] = sha256_bytes(ora_data)
        validate_ora(out_dir / ora_name, LAYERS[kind])

        events[kind] = {
            "durationSeconds": DURATIONS[kind],
            "cell": [W, H],
            "pivot": list(PIVOT),
            "frameCount": FRAME_COUNT,
            "frames": frame_names,
            "pxo": pxo_name,
            "ora": ora_name,
            "oraFrame": ORA_FRAME,
            "layerRoles": list(LAYERS[kind]),
            "nativeFrameDurations": [native_multiplier] * FRAME_COUNT,
            "nativeDurationSecondsTotal": sum([native_multiplier] * FRAME_COUNT) / NATIVE_FPS,
        }

    manifest_name = PREFIX + "asset-manifest" + SUFFIX + ".json"
    manifest = {
        "schemaVersion": 2,
        "project": PROJECT,
        "subject": SUBJECT,
        "variant": VARIANT,
        "packageId": RUN_STAMP + "-" + RUN_ID,
        "scope": SCOPE,
        "fps": NATIVE_FPS,
        "cell": [W, H],
        "pivot": list(PIVOT),
        "frameCount": FRAME_COUNT,
        "kindOrder": list(KINDS),
        "maxEvents": MAX_EVENTS,
        "durationSemantics": "frames[].duration is a multiplier of 1/fps",
        "source": {
            "path": source_rel,
            "sha256": source_sha,
        },
        "helper": {
            "path": helper_rel,
            "sha256": helper_sha,
        },
        "provenance": {
            "author": source_rel,
            "authorSha256": source_sha,
            "helper": helper_rel,
            "helperSha256": helper_sha,
            "helperOrigin": "copied proven native-format helper",
            "pixeloramaArtifactFormat": "PXO v7 full 8-cel / ORA middle-cel role snapshot",
        },
        "events": events,
        "sha256": dict(sorted(artifacts.items())),
    }
    (out_dir / manifest_name).write_text(
        json.dumps(manifest, indent=2, sort_keys=False) + "\n", encoding="utf-8"
    )

    # Read-back structural check, scoped to this one package.
    reloaded = json.loads((out_dir / manifest_name).read_text(encoding="utf-8"))
    if reloaded["kindOrder"] != list(KINDS):
        raise RuntimeError("manifest kind order does not round-trip")
    if set(reloaded["events"]) != set(KINDS):
        raise RuntimeError("manifest events do not round-trip")
    for name, digest in reloaded["sha256"].items():
        if sha256_file(out_dir / name) != digest:
            raise RuntimeError(f"manifest hash mismatch for {name}")
    if len(reloaded["sha256"]) != len(KINDS) * 10:
        raise RuntimeError("manifest does not hash all 80 artifacts")
    if sha256_file(source_path) != reloaded["source"]["sha256"]:
        raise RuntimeError("author raw hash mismatch")
    if sha256_file(helper_file) != reloaded["helper"]["sha256"]:
        raise RuntimeError("helper raw hash mismatch")

    print(f"package: {out_dir}")
    print(f"manifest: {manifest_name}")
    print(f"kinds: {len(KINDS)} cels: {len(KINDS) * FRAME_COUNT} "
          f"pxo: {len(KINDS)} ora: {len(KINDS)} artifacts: {len(artifacts)}")
    for kind in KINDS:
        entry = events[kind]
        print(f"  {kind}: {entry['durationSeconds']:.2f}s "
              f"{entry['nativeFrameDurations'][0]:.4f}x8 "
              f"roles={len(entry['layerRoles'])}")
    return manifest


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out-dir", required=True, type=Path)
    args = parser.parse_args()
    build(args.out_dir.resolve())


if __name__ == "__main__":
    main()
