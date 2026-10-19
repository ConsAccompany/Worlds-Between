#!/usr/bin/env python3
"""Build four original 128x80 encounter feedback effects as native pixel art.

Each kind has eight frames (transparent bookends, six distinct active frames),
three editable role layers, a frame PXO and a middle-frame ORA.  Every mark is
integer-aligned, antialiasing is off, and alpha never exceeds 166.

Native timing correction: Pixelorama stores ``frames[].duration`` as a
multiplier of ``1/fps`` rather than as seconds.  At fps 12 each frame therefore
stores ``durationSeconds / 8 * 12`` so a kind's native total is exactly its
manifest ``durationSeconds``.  Pixels, layer roles and manifest geometry are
unchanged from the original bench-v01 submission.
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
PREFIX = PROJECT + "_encounter_"
VARIANT = "timing-v02"
RUN_STAMP = "20261019-001519"
RUN_ID = "69291ffd"
TAG = VARIANT + "_" + RUN_STAMP + "-" + RUN_ID
SUFFIX = "_" + TAG
W, H = 128, 80
NATIVE_FPS = 12
PIVOT = (64, 48)
MAX_ALPHA = 166

KINDS = ("encounter", "victory", "defeat", "recovery")
DURATIONS = {"encounter": 0.50, "victory": 0.80, "defeat": 0.65, "recovery": 0.60}
LAYERS = {
    "encounter": ("alert-core", "amber-arcs", "directional-chevrons"),
    "victory": ("celebration-arcs", "teal-motes", "gold-motes"),
    "defeat": ("ground-dust", "dim-core", "ember-fragments"),
    "recovery": ("rebuild-core", "rebuilding-rings", "mint-sparks"),
}
# Deliberate timing: a quick rise to a readable peak, then a restrained tail.
ENVELOPE = {1: 0.42, 2: 0.78, 3: 1.00, 4: 0.82, 5: 0.60, 6: 0.36}


def new_cell() -> Image.Image:
    return Image.new("RGBA", (W, H), (0, 0, 0, 0))


def color(rgb: tuple[int, int, int], alpha: float) -> tuple[int, int, int, int]:
    a = max(0, min(MAX_ALPHA, int(round(alpha))))
    return (rgb[0], rgb[1], rgb[2], a)


def arc_points(cx: int, cy: int, radius: int, a0: float, a1: float, steps: int) -> list[tuple[int, int]]:
    points = []
    for i in range(steps + 1):
        angle = math.radians(a0 + (a1 - a0) * i / steps)
        points.append((int(round(cx + math.cos(angle) * radius)),
                       int(round(cy + math.sin(angle) * radius))))
    return points


def arc(draw: ImageDraw.ImageDraw, cx: int, cy: int, radius: int, a0: float, a1: float,
        rgba, width: int = 1, steps: int = 18) -> None:
    draw.line(arc_points(cx, cy, radius, a0, a1, steps), fill=rgba, width=width, joint="curve")


def diamond(draw: ImageDraw.ImageDraw, x: int, y: int, radius: int, rgba) -> None:
    for dy in range(-radius, radius + 1):
        span = radius - abs(dy)
        for dx in range(-span, span + 1):
            draw.point((x + dx, y + dy), fill=rgba)


def cross(draw: ImageDraw.ImageDraw, x: int, y: int, arm: int, rgba) -> None:
    draw.line((x - arm, y, x + arm, y), fill=rgba, width=1)
    draw.line((x, y - arm, x, y + arm), fill=rgba, width=1)


def build_encounter(f: int) -> dict[str, Image.Image]:
    out = {name: new_cell() for name in LAYERS["encounter"]}
    if f in (0, 7):
        return out
    env = ENVELOPE[f]
    q = f / 7.0
    dark, mid, hot = (145, 88, 27), (215, 143, 48), (248, 202, 100)
    a_core, a_mid, a_low = 166 * env, 132 * env, 82 * env

    # Central alert seed: directional rays are stronger near the origin.
    d = ImageDraw.Draw(out["alert-core"])
    cx, cy = 64, 48
    diamond(d, cx, cy, 1, color(hot, a_core))
    diamond(d, cx, cy, 2, color(mid, a_mid))
    d.point((cx - 3, cy), fill=color(hot, a_core))
    d.point((cx + 3, cy), fill=color(hot, a_core))
    d.point((cx, cy - 3), fill=color(mid, a_mid))
    d.point((cx, cy + 3), fill=color(mid, a_mid))
    for angle in (198, 226, 254, 282, 310, 338):
        rad = math.radians(angle)
        d.point((int(round(cx + math.cos(rad) * 6)), int(round(cy + math.sin(rad) * 6))),
                fill=color(dark, a_low))

    # Three expanding amber scan arcs, brightest and thickest at the core.
    d = ImageDraw.Draw(out["amber-arcs"])
    base_r = 14 + int(round(q * 13))
    for i, radius in enumerate((base_r, base_r + 5, base_r + 10)):
        if i == 0:
            arc(d, cx, 51, radius, 204, 336, color(hot, a_core), width=2)
        elif i == 1:
            arc(d, cx, 51, radius, 208, 332, color(mid, a_mid), width=2)
        else:
            arc(d, cx, 51, radius, 214, 326, color(dark, a_low), width=1)
    # The leading left tips make the scan direction explicit.
    lead_x = cx - int(round(base_r * 0.92))
    lead_y = 51 - int(round(base_r * 0.38))
    d.polygon([(lead_x - 4, lead_y), (lead_x, lead_y - 2), (lead_x, lead_y + 2)],
              fill=color(hot, a_core))
    d.point((lead_x - 1, lead_y + 3), fill=color(mid, a_mid))

    # Short left-pointing chevrons travel outward like an alert pulse.
    d = ImageDraw.Draw(out["directional-chevrons"])
    shift = int(round(q * 11))
    for i, y in enumerate((34, 42, 50)):
        bx = 54 - shift - i * 2
        rgba = color(hot if i == 2 else mid, a_core if i == 2 else a_mid)
        d.line([(bx, y - 4), (bx - 5, y), (bx, y + 4)], fill=rgba, width=2, joint="curve")
        d.point((bx - 4, y), fill=color(hot, a_core if i == 2 else a_mid))
    d.point((44 + shift // 2, 41), fill=color(dark, a_low))
    d.point((40 + shift // 2, 43), fill=color(dark, a_low))
    return out


def build_victory(f: int) -> dict[str, Image.Image]:
    out = {name: new_cell() for name in LAYERS["victory"]}
    if f in (0, 7):
        return out
    env = ENVELOPE[f]
    q = f / 7.0
    gold_dark, gold, gold_hot = (151, 108, 44), (214, 169, 73), (247, 216, 126)
    teal_dark, teal, mint = (36, 113, 106), (78, 178, 157), (166, 231, 201)
    a_hot, a_mid, a_low = 166 * env, 126 * env, 74 * env

    # A small broken crown of arcs opens above the focus.
    d = ImageDraw.Draw(out["celebration-arcs"])
    for i, radius in enumerate((20 + int(q * 5), 26 + int(q * 5))):
        a0, a1 = (208, 332) if i == 0 else (222, 318)
        arc(d, 64, 50, radius, a0, a1, color(gold if i == 0 else teal, a_mid if i == 0 else a_low),
            width=1, steps=20)
    d.line([(46, 30), (51, 26), (56, 29)], fill=color(teal, a_mid), width=1)
    d.line([(72, 27), (77, 23), (82, 26)], fill=color(gold, a_mid), width=1)

    # Teal secondary motes drift up on the outside.
    teal_motes = [(-35, 4, 0.02), (-25, 1, 0.10), (-14, 6, 0.18), (12, 2, 0.06),
                  (23, 7, 0.15), (33, 3, 0.23), (41, 8, 0.00)]
    d = ImageDraw.Draw(out["teal-motes"])
    for dx, drift, delay in teal_motes:
        phase = min(1.0, q * 1.05 + delay)
        y = 64 - int(round(phase * 38)) + (f % 2)
        x = 64 + dx + int(round(math.sin((q + delay) * math.pi) * drift))
        if 3 <= x <= 124 and 3 <= y <= 76:
            d.point((x, y), fill=color(mint, a_hot if phase > 0.55 else a_mid))
            d.point((x - 1, y), fill=color(teal, a_low))
            d.point((x, y - 1), fill=color(teal, a_mid))

    # Gold motes rise faster and provide the warm celebratory accents.
    gold_motes = [(-30, 14, 0.04, 1), (-20, 2, 0.20, 0), (-9, 10, 0.31, 1),
                  (2, 0, 0.09, 0), (11, 15, 0.25, 1), (21, 4, 0.14, 0),
                  (29, 12, 0.34, 1), (38, 6, 0.18, 0), (-3, 18, 0.40, 0)]
    d = ImageDraw.Draw(out["gold-motes"])
    for dx, top, delay, big in gold_motes:
        phase = min(1.0, q * 1.08 + delay)
        y = 63 - int(round(phase * 36)) - top // 3
        x = 64 + dx + int(round(math.sin((q * 1.4 + delay) * math.pi) * 2))
        if 2 <= x <= 125 and 2 <= y <= 77:
            if big:
                diamond(d, x, y, 1, color(gold_hot, a_hot))
                d.point((x - 2, y), fill=color(gold, a_mid))
            else:
                d.point((x, y), fill=color(gold_hot, a_hot if phase < 0.8 else a_mid))
                d.point((x, y - 1), fill=color(gold, a_mid))
                d.point((x - 1, y), fill=color(gold_dark, a_low))
    return out


def build_defeat(f: int) -> dict[str, Image.Image]:
    out = {name: new_cell() for name in LAYERS["defeat"]}
    if f in (0, 7):
        return out
    env = ENVELOPE[f]
    q = f / 7.0
    ember_dark, ember, ember_hot = (115, 70, 52), (168, 101, 67), (200, 132, 85)
    ash, ash_light = (92, 82, 72), (137, 120, 101)
    a_hot, a_mid, a_low = 156 * env, 118 * env, 66 * env

    # Quiet dust settles first and spreads along the floor band.
    d = ImageDraw.Draw(out["ground-dust"])
    dust = [(-43, 57), (-34, 62), (-27, 67), (-18, 70), (-10, 74), (-3, 69),
            (5, 73), (12, 76), (20, 70), (28, 66), (36, 61), (43, 57)]
    for i, (dx, y0) in enumerate(dust):
        if i % 2 == 0 or f >= 3:
            y = min(77, y0 + int(round(q * 5)))
            x = 64 + dx + int(round(math.sin(q * math.pi + i) * 2))
            d.point((x, y), fill=color(ash, a_low))
            if i % 3 == 0:
                d.point((x, y - 1), fill=color(ash_light, a_low))

    # The old core contracts and sinks, leaving a dim ring rather than a flash.
    d = ImageDraw.Draw(out["dim-core"])
    cy = 42 + int(round(q * 9))
    radius = max(3, 9 - f // 2)
    arc(d, 64, cy, radius, 18, 162, color(ember_dark, a_mid), width=1)
    arc(d, 64, cy, radius, 198, 342, color(ember, a_low), width=1)
    d.line([(64, cy - 2), (64, cy + 2)], fill=color(ember_hot, a_hot), width=1)
    d.point((63, cy), fill=color(ember, a_mid))
    d.point((65, cy), fill=color(ember, a_mid))
    d.point((64, cy + 3), fill=color(ember_dark, a_low))

    # Angular ember fragments tumble, then settle downward and outward.
    d = ImageDraw.Draw(out["ember-fragments"])
    fragments = [(-28, 26, 3, 2), (-20, 38, 4, -1), (-11, 31, 2, 1), (-3, 22, 3, 2),
                 (6, 35, 4, -1), (14, 27, 3, 1), (23, 39, 2, 2), (31, 31, 3, -1),
                 (-16, 46, 2, 1), (17, 48, 3, 1), (2, 41, 2, -1)]
    for i, (dx, y0, size, dxdrift) in enumerate(fragments):
        y = min(75, y0 + int(round(q * 27)) + (size - 2))
        x = 64 + dx + int(round(q * dxdrift * 5))
        if 2 <= x <= 125 and 2 <= y <= 77:
            rgba = color(ember_hot if size >= 3 else ember, a_hot if size >= 3 else a_mid)
            d.line([(x - size, y - 1), (x, y), (x + size, y + 2)], fill=rgba, width=1)
            d.point((x, y + 1), fill=color(ember_dark, a_low))
    return out


def build_recovery(f: int) -> dict[str, Image.Image]:
    out = {name: new_cell() for name in LAYERS["recovery"]}
    if f in (0, 7):
        return out
    env = ENVELOPE[f]
    q = f / 7.0
    teal_dark, teal, teal_light = (27, 99, 95), (57, 162, 150), (119, 215, 190)
    mint, mint_hot = (169, 235, 209), (222, 249, 232)
    a_hot, a_mid, a_low = 166 * env, 126 * env, 70 * env

    # A small machine-heart reassembles in place: only a restrained cross-core.
    d = ImageDraw.Draw(out["rebuild-core"])
    diamond(d, 64, 48, 1, color(teal_light, a_mid))
    d.point((64, 48), fill=color(mint_hot, a_hot))
    arm = 2 + min(4, f // 2)
    d.point((64 - arm, 48), fill=color(mint, a_hot))
    d.point((64 + arm, 48), fill=color(mint, a_hot))
    d.point((64, 48 - arm), fill=color(mint, a_hot))
    d.point((64, 48 + arm), fill=color(mint, a_hot))
    d.point((64 - arm + 1, 47), fill=color(teal_light, a_mid))
    d.point((64 + arm - 1, 49), fill=color(teal_light, a_mid))
    cross(d, 64, 48, 1, color(teal, a_low))

    # Three incomplete rings converge as the outer shell is rebuilt.
    d = ImageDraw.Draw(out["rebuilding-rings"])
    for i in range(3):
        radius = max(10, 32 - f * 2 + i * 5)
        spin = f * 13 + i * 47
        a0 = spin
        a1 = spin + 86 + i * 8
        arc(d, 64, 50, radius, a0, a1, color(teal_light if i == 0 else teal, a_hot if i == 0 else a_mid),
            width=1, steps=12)
        a2 = spin + 180
        arc(d, 64, 50, radius, a2, a2 + 44, color(teal_dark, a_low), width=1, steps=8)
    # Two bright closing brackets on the horizontal axis.
    reach = 8 + f
    d.line([(64 - reach, 50), (64 - reach + 3, 50)], fill=color(mint, a_hot), width=1)
    d.line([(64 + reach - 3, 50), (64 + reach, 50)], fill=color(mint, a_hot), width=1)

    # Sparks jump outward along fixed radial spokes, rebuilding the perimeter.
    d = ImageDraw.Draw(out["mint-sparks"])
    spokes = [(-31, 5), (-24, -12), (-15, 10), (-6, -20), (4, 14), (13, -16),
              (22, 11), (29, -7), (-36, -4), (36, 2)]
    for i, (dx, dy) in enumerate(spokes):
        reach = 0.35 + q * 0.9
        x = 64 + int(round(dx * reach))
        y = 50 + int(round(dy * reach)) - (f % 2)
        if 2 <= x <= 125 and 2 <= y <= 77:
            d.point((x, y), fill=color(mint_hot if i % 3 == 0 else mint, a_hot))
            d.point((x - 1, y), fill=color(teal, a_mid))
            if i % 2 == 0:
                d.point((x, y - 1), fill=color(teal_light, a_mid))
    return out


BUILDERS = {
    "encounter": build_encounter,
    "victory": build_victory,
    "defeat": build_defeat,
    "recovery": build_recovery,
}


def combine(layers: dict[str, Image.Image]) -> Image.Image:
    out = new_cell()
    for name in layers:
        out.alpha_composite(layers[name])
    return out


def clamp_alpha(img: Image.Image) -> None:
    """Hard-cap composited ink; overlapping drawn marks may otherwise stack."""
    alpha = img.getchannel("A").point(lambda value: min(value, MAX_ALPHA))
    img.putalpha(alpha)


def isolate_layer_alpha(layers: dict[str, Image.Image]) -> None:
    """Let only the topmost role own each pixel.

    This keeps role separation crisp and guarantees that alpha composition of
    the three layers can never push a frame above MAX_ALPHA.
    """
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


def load_helper():
    here = Path(__file__).resolve()
    helper_path = here.parent.parent / "inputs" / (
        PROJECT + "_benchmark_native-format-helper_v01_20261018-234437-8dfccbf6.py"
    )
    spec = importlib.util.spec_from_file_location("shared_native_helper", helper_path)
    if spec is None or spec.loader is None:
        raise RuntimeError("cannot load shared native-format helper")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def build(out_dir: Path) -> dict:
    out_dir.mkdir(parents=True, exist_ok=True)
    helper = load_helper()
    events = {}

    for kind in KINDS:
        # Pixelorama multiplies each frame duration by 1/fps at play time.
        native_multiplier = DURATIONS[kind] / 8.0 * NATIVE_FPS
        layers_by_frame = [BUILDERS[kind](f) for f in range(8)]
        for frame_layers in layers_by_frame:
            for img in frame_layers.values():
                clamp_alpha(img)
            isolate_layer_alpha(frame_layers)
        composites = [combine(layers_by_frame[f]) for f in range(8)]
        names = []
        for f in range(8):
            fname = PREFIX + kind + f"_frame-{f:02d}" + SUFFIX + ".png"
            save_png(composites[f], out_dir / fname)
            names.append(fname)

        pxo_name = PREFIX + kind + "_8frame" + SUFFIX + ".pxo"
        ora_name = PREFIX + kind + "_middle-layered" + SUFFIX + ".ora"
        data = helper.pxo_bytes(
            layers_by_frame,
            [native_multiplier] * 8,
            png_bytes(composites[3]),
            pxo_name,
        )
        (out_dir / pxo_name).write_bytes(data)
        (out_dir / ora_name).write_bytes(helper.ora_bytes(layers_by_frame[3]))
        events[kind] = {
            "durationSeconds": DURATIONS[kind],
            "cell": [W, H],
            "pivot": list(PIVOT),
            "frameCount": 8,
            "frames": names,
            "pxo": pxo_name,
            "ora": ora_name,
        }

    manifest_name = PREFIX + "asset-manifest" + SUFFIX + ".json"
    hashes: dict[str, str] = {}
    for kind in KINDS:
        entry = events[kind]
        for name in entry["frames"] + [entry["pxo"], entry["ora"]]:
            hashes[name] = sha256_file(out_dir / name)
    source_rel = Path(os.path.relpath(Path(__file__).resolve(), out_dir)).as_posix()
    manifest = {
        "schemaVersion": 1,
        "fps": NATIVE_FPS,
        "durationSemantics": "frames[].duration is a multiplier of 1/fps",
        "source": source_rel,
        "events": events,
        "sha256": dict(sorted(hashes.items())),
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
