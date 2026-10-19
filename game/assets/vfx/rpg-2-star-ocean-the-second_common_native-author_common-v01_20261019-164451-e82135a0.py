#!/usr/bin/env python3
"""Build five original 64x64 common combat VFX as native pixel art.

Each kind has eight cels, three editable role layers, a frame PXO and a
middle-frame role-layer ORA.  Only integer-aligned, aliased marks are used;
alpha is hard-capped at 166 so nothing can become an opaque body-obscuring
flash.  The five sets stay locally compact around the 32,32 pivot.

Native timing: Pixelorama stores ``frames[].duration`` as a multiplier of
``1/fps`` rather than as seconds.  At fps 12 each frame therefore stores
``durationSeconds / 8 * 12``, so a kind's native total is exactly its manifest
``durationSeconds``: attack .22, dodge .27, guard .30, hit .20, heal .55.

The shared native-format helper is imported from the copied, proven encounter
input path relative to this author, matching the encounter author's portable
source/helper convention.
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

from PIL import Image, ImageDraw

PROJECT = "rpg-2-star-ocean-the-second"
SUBJECT = "common"
PREFIX = PROJECT + "_" + SUBJECT + "_"
VARIANT = "common-v01"
RUN_STAMP = "20261019-164451"
RUN_ID = "e82135a0"
TAG = VARIANT + "_" + RUN_STAMP + "-" + RUN_ID
SUFFIX = "_" + TAG
W, H = 64, 64
NATIVE_FPS = 12
PIVOT = (32, 32)
MAX_ALPHA = 166
MAX_EVENTS = 24

KINDS = ("attack", "dodge", "guard", "hit", "heal")
DURATIONS = {
    "attack": 0.22,
    "dodge": 0.27,
    "guard": 0.30,
    "hit": 0.20,
    "heal": 0.55,
}
LAYERS = {
    "attack": ("amber-core", "contact-arcs", "motion-sparks"),
    "dodge": ("teal-afterimage", "motion-streaks", "foot-dust"),
    "guard": ("teal-bulwark", "brace-arcs", "guard-sparks"),
    "hit": ("coral-impact", "recoil-arcs", "coral-fragments"),
    "heal": ("sage-core", "healing-rings", "sage-motes"),
}
# Anticipation -> contact/peak -> dissipation, sampled on eight cels.
ENVELOPES = {
    "attack": (0.16, 0.38, 0.70, 1.00, 0.74, 0.48, 0.26, 0.10),
    "dodge":  (0.14, 0.35, 0.70, 1.00, 0.78, 0.54, 0.30, 0.11),
    "guard":  (0.12, 0.32, 0.66, 1.00, 0.82, 0.60, 0.34, 0.12),
    "hit":    (0.12, 0.36, 1.00, 0.80, 0.58, 0.36, 0.18, 0.07),
    "heal":   (0.10, 0.26, 0.50, 0.74, 1.00, 0.78, 0.48, 0.20),
}
ORA_FRAME = 3

AMBER_DARK, AMBER_MID = (139, 84, 28), (208, 140, 46)
AMBER_HOT, AMBER_PALE = (245, 196, 92), (252, 220, 145)
TEAL_DARK, TEAL_MID = (30, 92, 94), (62, 150, 150)
TEAL_LIGHT, TEAL_PALE = (122, 205, 197), (180, 235, 218)
CORAL_DARK, CORAL_MID = (146, 78, 70), (199, 119, 105)
CORAL_HOT, CORAL_PALE = (232, 160, 142), (244, 192, 169)
SAGE_DARK, SAGE_MID = (68, 98, 74), (112, 150, 108)
SAGE_LIGHT, SAGE_PALE = (166, 197, 154), (206, 226, 184)


def new_cell() -> Image.Image:
    return Image.new("RGBA", (W, H), (0, 0, 0, 0))


def color(rgb: tuple[int, int, int], alpha: float) -> tuple[int, int, int, int]:
    a = max(0, min(MAX_ALPHA, int(round(alpha))))
    return (rgb[0], rgb[1], rgb[2], a)


def arc_points(cx: int, cy: int, radius: int, a0: float, a1: float,
               steps: int) -> list[tuple[int, int]]:
    points = []
    for i in range(steps + 1):
        angle = math.radians(a0 + (a1 - a0) * i / steps)
        points.append((int(round(cx + math.cos(angle) * radius)),
                       int(round(cy + math.sin(angle) * radius))))
    return points


def arc(draw: ImageDraw.ImageDraw, cx: int, cy: int, radius: int, a0: float,
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


def build_attack(f: int) -> dict[str, Image.Image]:
    out = {name: new_cell() for name in LAYERS["attack"]}
    env = ENVELOPES["attack"][f]
    q = f / 7.0
    reach = max(2, int(round(4 + 14 * env)))

    # Amber core: a compact forward spear seeded in the palm of the strike.
    d = ImageDraw.Draw(out["amber-core"])
    diamond(d, 32, 32, 1 + (1 if env > 0.55 else 0), color(AMBER_HOT, 150 * env))
    d.point((32, 32), fill=color(AMBER_PALE, 166 * env))
    if reach > 3:
        d.line([(33, 32), (32 + reach, 32)], fill=color(AMBER_MID, 150 * env), width=2)
        d.point((32 + reach, 32), fill=color(AMBER_HOT, 166 * env))
        d.point((32 + reach - 1, 31), fill=color(AMBER_PALE, 120 * env))
    if f <= 2:
        # Anticipation: the spear is still drawn back before it leaves.
        d.line([(30 - f, 32), (26 - f, 32)], fill=color(AMBER_DARK, 96 * env), width=1)
        d.point((25 - f, 32), fill=color(AMBER_MID, 116 * env))

    # Contact arcs open forward and thin out during dissipation.
    d = ImageDraw.Draw(out["contact-arcs"])
    radius = 6 + int(round(9 * env))
    arc(d, 30, 32, radius, -58, 58, color(AMBER_MID, 142 * env),
        width=2 if f in (2, 3, 4) else 1, steps=18)
    arc(d, 30, 32, radius + 3, -46, 46, color(AMBER_DARK, 88 * env),
        width=1, steps=16)
    if f >= 2:
        tip = 32 + radius
        d.line([(tip, 27), (tip, 37)], fill=color(AMBER_HOT, 150 * env), width=1)
    if f >= 1:
        inner = max(2, radius - 4)
        d.line([(32, 29), (32 + inner, 29)], fill=color(AMBER_PALE, 90 * env), width=1)
        d.line([(32, 35), (32 + inner - 1, 35)], fill=color(AMBER_PALE, 70 * env), width=1)

    # Sparse directional spark clusters; no noise, no dithered field.
    d = ImageDraw.Draw(out["motion-sparks"])
    for index, (angle, span) in enumerate(((-72, 3), (-48, 5), (-22, 7), (2, 8),
                                           (26, 7), (52, 5), (76, 3))):
        rad = math.radians(angle)
        r0 = 8 + int(round(2 * env))
        r1 = r0 + int(round(span * env))
        x0 = 32 + int(round(math.cos(rad) * r0))
        y0 = 32 + int(round(math.sin(rad) * r0))
        x1 = 32 + int(round(math.cos(rad) * r1))
        y1 = 32 + int(round(math.sin(rad) * r1))
        rgba = color(AMBER_HOT if index in (2, 3, 4) else AMBER_MID, 140 * env)
        d.line([(x0, y0), (x1, y1)], fill=rgba, width=1)
        if index % 2 == 0:
            d.point((x1, y1), fill=color(AMBER_PALE, 150 * env))
    if f >= 2:
        for index in range(2):
            x = 32 - 8 - 3 * index - int(round(q * 2))
            y = 28 + 6 * index
            d.point((x, y), fill=color(AMBER_DARK, 100 * env))
    return out


def build_dodge(f: int) -> dict[str, Image.Image]:
    out = {name: new_cell() for name in LAYERS["dodge"]}
    env = ENVELOPES["dodge"][f]
    q = f / 7.0
    shift = int(round(q * 9))

    # Teal afterimage brackets trail left of the moving focus.
    d = ImageDraw.Draw(out["teal-afterimage"])
    for index in range(3):
        x = 32 - 5 - index * 5 - shift
        if x < 12:
            continue
        half = 7 + index * 2
        alpha = 120 * env / (index + 1)
        d.line([(x, 32 - half), (x, 32 + half)],
               fill=color(TEAL_LIGHT if index == 0 else TEAL_MID, alpha), width=1)
        d.line([(x, 32 - half), (x - 2, 32 - half + 2)],
               fill=color(TEAL_MID, alpha * 0.8), width=1)
        d.line([(x, 32 + half), (x - 2, 32 + half - 2)],
               fill=color(TEAL_MID, alpha * 0.8), width=1)
    if f >= 2:
        x = 32 + 7 + int(round(env * 6))
        d.line([(x - 3, 27), (x, 32), (x - 3, 37)],
               fill=color(TEAL_PALE, 150 * env), width=1)

    # Horizontal speed streaks, longest at the dash peak and gone by the tail.
    d = ImageDraw.Draw(out["motion-streaks"])
    for index, y in enumerate((25, 29, 35, 39)):
        length = 5 + int(round(10 * env))
        x0 = 31 - shift - index * 2
        x1 = max(6, x0 - length)
        d.line([(x0, y), (x1, y)],
               fill=color(TEAL_LIGHT if index % 2 else TEAL_MID, 104 * env),
               width=1)
        if f >= 3 and index in (1, 2):
            d.point((x1 - 1, y), fill=color(TEAL_DARK, 96 * env))
    if f >= 2:
        x0 = 36
        x1 = x0 + 3 + int(round(4 * env))
        d.line([(x0, 32), (x1, 32)], fill=color(TEAL_PALE, 142 * env), width=1)

    # A few low, hard-edged dust ticks sell the launch without covering a body.
    d = ImageDraw.Draw(out["foot-dust"])
    if env > 0.20:
        puffs = ((28, 43), (34, 44), (24, 46), (38, 42), (31, 47))
        for index, (px, py) in enumerate(puffs):
            drift = int(round(q * 5)) + index % 2
            x = px - drift
            d.point((x, py), fill=color(TEAL_DARK, 82 * env))
            if index % 2 == 0:
                d.point((x + 1, py - 1), fill=color(TEAL_MID, 72 * env))
    return out


def build_guard(f: int) -> dict[str, Image.Image]:
    out = {name: new_cell() for name in LAYERS["guard"]}
    env = ENVELOPES["guard"][f]
    q = f / 7.0

    # A compact forward bulwark: two nested teal arcs, never a filled disc.
    d = ImageDraw.Draw(out["teal-bulwark"])
    radius = 10 + int(round(4 * env))
    arc(d, 29, 32, radius, -64, 64, color(TEAL_LIGHT, 160 * env),
        width=2 if f in (2, 3, 4) else 1, steps=22)
    arc(d, 29, 32, radius - 3, -52, 52, color(TEAL_MID, 122 * env),
        width=1, steps=18)
    if f >= 3:
        d.line([(29, 28), (29, 36)], fill=color(TEAL_PALE, 122 * env), width=1)
    arc(d, 23, 32, 7, -122, 122, color(TEAL_DARK, 84 * env), width=1, steps=16)

    # Brace ticks and a centre anchor keep the guard readable at 1x.
    d = ImageDraw.Draw(out["brace-arcs"])
    arm = 3 + int(round(2 * env))
    d.line([(31, 22), (36, 23), (40, 26)], fill=color(TEAL_MID, 110 * env), width=1)
    d.line([(31, 42), (36, 41), (40, 38)], fill=color(TEAL_MID, 110 * env), width=1)
    d.line([(20, 32), (26, 32)], fill=color(TEAL_DARK, 96 * env), width=1)
    diamond(d, 28, 32, 1, color(TEAL_LIGHT, 132 * env))
    d.point((28, 32), fill=color(TEAL_PALE, 150 * env))
    if f >= 1:
        d.line([(26, 32 - arm), (26, 32 + arm)],
               fill=color(TEAL_MID, 94 * env), width=1)

    # Contact sparks appear only at the forward lip, then drift and fade.
    d = ImageDraw.Draw(out["guard-sparks"])
    if f >= 2:
        tip = 32 + radius
        for index, angle in enumerate((-38, 0, 38)):
            rad = math.radians(angle)
            r0 = 1 + int(round(2 * env))
            r1 = 3 + int(round(5 * env))
            x0 = tip + int(round(math.cos(rad) * r0))
            y0 = 32 + int(round(math.sin(rad) * r0))
            x1 = tip + int(round(math.cos(rad) * r1))
            y1 = 32 + int(round(math.sin(rad) * r1))
            d.line([(x0, y0), (x1, y1)],
                   fill=color(TEAL_PALE if index == 1 else TEAL_LIGHT, 148 * env),
                   width=1)
        d.point((tip, 32), fill=color(TEAL_PALE, 160 * env))
        if f >= 4:
            d.point((tip + 1, 32), fill=color(TEAL_MID, 90 * env))
    if q > 0.5:
        d.point((24, 27), fill=color(TEAL_DARK, 72 * env))
        d.point((23, 37), fill=color(TEAL_DARK, 64 * env))
    return out


def build_hit(f: int) -> dict[str, Image.Image]:
    out = {name: new_cell() for name in LAYERS["hit"]}
    env = ENVELOPES["hit"][f]
    q = f / 7.0

    # Soft-coral impact core: small, hot but never white and never a screen flash.
    d = ImageDraw.Draw(out["coral-impact"])
    diamond(d, 32, 32, 1 + (1 if env > 0.60 else 0), color(CORAL_HOT, 160 * env))
    d.point((32, 32), fill=color(CORAL_PALE, 166 * env))
    for index in range(8):
        angle = math.radians(index * 45 + 22)
        r0 = 3 + int(round(3 * env))
        r1 = r0 + 4 + int(round(4 * env))
        x0 = 32 + int(round(math.cos(angle) * r0))
        y0 = 32 + int(round(math.sin(angle) * r0))
        x1 = 32 + int(round(math.cos(angle) * r1))
        y1 = 32 + int(round(math.sin(angle) * r1))
        d.line([(x0, y0), (x1, y1)],
               fill=color(CORAL_HOT if index % 2 else CORAL_MID, 142 * env),
               width=1)
    if f >= 2:
        d.line([(24, 32), (19, 32)], fill=color(CORAL_MID, 104 * env), width=1)

    # Broken recoil arcs expand with clear gaps rather than a solid ring.
    d = ImageDraw.Draw(out["recoil-arcs"])
    radius = 7 + int(round(8 * env))
    for index, (a0, a1) in enumerate(((-80, -20), (20, 80), (100, 160),
                                      (200, 260), (280, 340))):
        rgba = color(CORAL_HOT if index in (1, 2) else CORAL_MID,
                     118 * env / (1 + 0.15 * index))
        arc(d, 32, 32, radius, a0, a1, rgba, width=1, steps=12)
    if f in (2, 3):
        arc(d, 32, 32, radius + 2, 118, 242, color(CORAL_DARK, 72 * env),
            width=1, steps=14)

    # Angular coral fragments move outward along fixed spokes.
    d = ImageDraw.Draw(out["coral-fragments"])
    directions = ((1, 0), (1, 1), (0, 1), (-1, 1), (-1, 0), (-1, -1),
                  (0, -1), (1, -1))
    distance = 5 + int(round(10 * env))
    for index, (dx, dy) in enumerate(directions):
        reach = distance + index % 3
        x = 32 + int(round(dx * reach * 0.72))
        y = 32 + int(round(dy * reach * 0.72))
        rgba = color(CORAL_HOT if index % 3 == 0 else CORAL_MID, 146 * env)
        d.point((x, y), fill=rgba)
        if index % 3 == 0 and env > 0.45:
            d.point((x + (1 if dx >= 0 else -1), y), fill=color(CORAL_PALE, 100 * env))
    if q > 0.55:
        d.point((22, 29), fill=color(CORAL_DARK, 72 * env))
        d.point((22, 35), fill=color(CORAL_DARK, 64 * env))
    return out


def build_heal(f: int) -> dict[str, Image.Image]:
    out = {name: new_cell() for name in LAYERS["heal"]}
    env = ENVELOPES["heal"][f]
    q = f / 7.0
    cy = 35

    # A restrained sage core, deliberately small so it never masks the body.
    d = ImageDraw.Draw(out["sage-core"])
    diamond(d, 32, cy, 1 + (1 if env > 0.62 else 0), color(SAGE_LIGHT, 150 * env))
    d.point((32, cy), fill=color(SAGE_PALE, 160 * env))
    arm = 2 + int(round(3 * env))
    cross(d, 32, cy, arm, color(SAGE_MID, 132 * env))
    if f >= 1:
        d.point((32 - arm - 1, cy), fill=color(SAGE_PALE, 110 * env))
        d.point((32 + arm + 1, cy), fill=color(SAGE_PALE, 110 * env))

    # Three broken, slowly turning rings rebuild the silhouette in place.
    d = ImageDraw.Draw(out["healing-rings"])
    base = 6 + int(round(6 * env))
    for index in range(3):
        radius = base + index * 3
        spin = f * 11 + index * 37
        alpha = 130 * env / (1 + 0.35 * index)
        arc(d, 32, cy, radius, spin, spin + 110,
            color(SAGE_LIGHT if index == 0 else SAGE_MID, alpha), width=1, steps=14)
        arc(d, 32, cy, radius, spin + 190, spin + 230,
            color(SAGE_DARK, alpha * 0.55), width=1, steps=8)
    # Two closing brackets mark the rebuilt perimeter.
    reach = 7 + int(round(6 * env))
    d.line([(32 - reach, cy), (32 - reach + 2, cy)],
           fill=color(SAGE_LIGHT, 120 * env), width=1)
    d.line([(32 + reach - 2, cy), (32 + reach, cy)],
           fill=color(SAGE_LIGHT, 120 * env), width=1)

    # Deterministic rising motes; no random generator and no dithered fill.
    d = ImageDraw.Draw(out["sage-motes"])
    xs = (-12, -7, -2, 3, 8, 13, 0)
    rise = 6 + int(round(q * 18))
    for index, dx in enumerate(xs):
        x = 32 + dx
        wobble = int(round(math.sin((f + index) * 0.7)))
        y = 44 - rise - index % 3 + wobble
        y = max(14, min(47, y))
        d.point((x, y), fill=color(SAGE_PALE if index % 3 == 0 else SAGE_LIGHT,
                                  138 * env))
        d.point((x - 1, y), fill=color(SAGE_MID, 88 * env))
        d.point((x, y - 1), fill=color(SAGE_MID, 88 * env))
    return out


BUILDERS = {
    "attack": build_attack,
    "dodge": build_dodge,
    "guard": build_guard,
    "hit": build_hit,
    "heal": build_heal,
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
        # Pixelorama multiplies each frame duration by 1/fps at play time.
        native_multiplier = DURATIONS[kind] / 8.0 * NATIVE_FPS
        layers_by_frame = [BUILDERS[kind](f) for f in range(8)]
        for frame_layers in layers_by_frame:
            for img in frame_layers.values():
                clamp_alpha(img)
            isolate_layer_alpha(frame_layers)
        composites = [combine(layers_by_frame[f]) for f in range(8)]

        frame_names = []
        for f in range(8):
            fname = PREFIX + kind + f"_frame-{f:02d}" + SUFFIX + ".png"
            save_png(composites[f], out_dir / fname)
            frame_names.append(fname)
            artifacts[fname] = sha256_file(out_dir / fname)

        pxo_name = PREFIX + kind + "_8frame" + SUFFIX + ".pxo"
        ora_name = PREFIX + kind + "_middle-layered" + SUFFIX + ".ora"
        pxo_data = helper.pxo_bytes(
            layers_by_frame,
            [native_multiplier] * 8,
            png_bytes(composites[ORA_FRAME]),
            pxo_name,
        )
        (out_dir / pxo_name).write_bytes(pxo_data)
        artifacts[pxo_name] = hashlib.sha256(pxo_data).hexdigest()
        ora_data = helper.ora_bytes(layers_by_frame[ORA_FRAME])
        (out_dir / ora_name).write_bytes(ora_data)
        artifacts[ora_name] = hashlib.sha256(ora_data).hexdigest()

        events[kind] = {
            "durationSeconds": DURATIONS[kind],
            "cell": [W, H],
            "pivot": list(PIVOT),
            "frameCount": 8,
            "frames": frame_names,
            "pxo": pxo_name,
            "ora": ora_name,
            "oraFrame": ORA_FRAME,
            "layerRoles": list(LAYERS[kind]),
            "nativeFrameDurations": [native_multiplier] * 8,
            "nativeDurationSecondsTotal": sum([native_multiplier] * 8) / NATIVE_FPS,
        }

    manifest_name = PREFIX + "asset-manifest" + SUFFIX + ".json"
    manifest = {
        "schemaVersion": 2,
        "project": PROJECT,
        "subject": SUBJECT,
        "variant": VARIANT,
        "packageId": RUN_STAMP + "-" + RUN_ID,
        "scope": "content.vfx.common",
        "fps": NATIVE_FPS,
        "cell": [W, H],
        "pivot": list(PIVOT),
        "frameCount": 8,
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
            "helperOrigin": "copied proven encounter native-format helper",
            "pixeloramaArtifactFormat": "PXO v7 / ORA role layers",
        },
        "events": events,
        "sha256": dict(sorted(artifacts.items())),
    }
    (out_dir / manifest_name).write_text(
        json.dumps(manifest, indent=2, sort_keys=False) + "\n", encoding="utf-8"
    )
    return manifest


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out-dir", required=True, type=Path)
    args = parser.parse_args()
    build(args.out_dir.resolve())


if __name__ == "__main__":
    main()
