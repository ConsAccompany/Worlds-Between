#!/usr/bin/env python3
"""Patrol machine battle animation v01 -- UNAPPROVED technical candidate (content.enemy.patrol.battle-animation).

One authored pass: every pixel is placed from integer rig poses (Pillow ImageDraw, no antialias, no randomness,
no fonts, no generated or traced pixels).  The identity follows the selected Patrol native static; nothing is
copied from the Sentry.  Contract: the sibling *_battle-animation-contract_* note.

Writes (into --out-dir, default this directory): per-frame layered PXO, one ORA per state (representative frame),
the runtime strip PNG, the runtime JSON package and a manifest with sha256 of every artefact.  Every artefact is
re-opened and checked (layer pixels, composites, durations, tags) before anything is written; --check rebuilds in
memory and compares against the files on disk byte for byte.

Usage: python -I <this> [--out-dir DIR] [--check]
"""
import argparse
import hashlib
import importlib.util
import io
import json
import os
import sys
import zipfile
from xml.etree import ElementTree as ET

from PIL import Image, ImageDraw

sys.dont_write_bytecode = True

STAMP = "v01_20261019-194007-a4b10a85"
PREFIX = "rpg-2-star-ocean-the-second_patrol_"
HERE = os.path.dirname(os.path.abspath(__file__))
HELPER = os.path.join(HERE, "..", "..", "inputs",
                      "rpg-2-star-ocean-the-second_benchmark_native-format-helper_v01_20261018-234437-8dfccbf6.py")
RES_DIR = "res://assets/enemies/patrol-anim-v01"
W, H = 112, 72
ANCHOR = (56, 66)
SOLE = 65
BODY_CENTER_X = 60
GAIT_STEP = 4
FPS = 12
PXO_DT = (2026, 10, 19, 0, 0, 0)
LAYERS = ["shadow", "far-leg", "hull", "head", "near-leg", "prod", "fx"]
TINTED = {"far-leg", "hull", "head", "near-leg", "prod"}

# Palette: warm sandstone plating, cool steel joints, teal tech light, one amber warning (Patrol static family).
OUT = (36, 30, 34, 255)
STEEL_D = (66, 64, 72, 255)
STEEL_M = (104, 104, 110, 255)
STEEL_L = (150, 150, 150, 255)
STEEL_H = (192, 190, 184, 255)
FAR_M = (84, 78, 82, 255)
FAR_D = (56, 52, 60, 255)
PLATE_D = (112, 82, 60, 255)
PLATE_M = (156, 118, 82, 255)
PLATE_L = (196, 158, 108, 255)
PLATE_H = (226, 200, 150, 255)
MOSS = (86, 102, 60, 255)
MOSS_L = (122, 140, 78, 255)
AMBER = (236, 168, 56, 255)
AMBER_D = (170, 96, 34, 255)
AMBER_H = (255, 214, 120, 255)
TEAL_D = (26, 98, 104, 255)
TEAL = (48, 168, 166, 255)
TEAL_L = (156, 236, 218, 255)
TEAL_X = (214, 255, 240, 255)
VISOR = (24, 34, 44, 255)
DARK_LENS = (44, 54, 60, 255)
SHADOW = (18, 14, 22, 110)
SMOKE = (92, 88, 92, 200)
HIT_TINT = (255, 140, 120)

STATES = {"idle": 4, "move": 6, "windup": 3, "strike": 3, "hit": 3, "defeat": 5}
FRAME_TIME = {"idle": 0.22, "move": 0.073, "windup": 0.217, "strike": 0.11, "hit": 0.09, "defeat": 0.15}
REP = {"idle": 0, "move": 1, "windup": 2, "strike": 0, "hit": 0, "defeat": 4}


def P(**kw):
    pose = {"bx": 0, "by": 0, "hx": 0, "hy": 0, "near": (-2, 0), "far": (3, 0), "lens": "lit", "prod": 0.0,
            "spark": 0, "charge": 0, "warn": False, "tint": 0.0, "sway": 0, "smoke": 0, "sparks": 0,
            "droop": 0, "shadow": 20}
    pose.update(kw)
    return pose


def poses():
    out = []
    # idle: 1 px breathe, head lags a frame, lens pulse, antenna sways against the bob.
    out += [P(), P(by=1, sway=1, lens="bright"), P(by=1, hy=1, sway=1), P(hy=1)]
    # move: distance gait, 4 px per step; planted foot offset rises +4 per step so it stays world-fixed.
    near_x = [-4, 0, 4, 2, 0, -2]
    lift = [0, 0, 0, 3, 4, 2]
    bob = [0, 1, 0, 0, 1, 0]
    for p in range(6):
        q = (p + 3) % 6
        out.append(P(by=bob[p], hy=bob[(p + 5) % 6], near=(near_x[p], lift[p]), far=(near_x[q] + 5, lift[q]),
                     sway=-1 if bob[p] else 0, shadow=19))
    # windup: pull back, crouch, charge (3 phases across the real 0.65 s windup).
    out += [P(bx=2, by=1, hx=2, lens="bright", sway=1),
            P(bx=4, by=3, hx=4, hy=1, lens="bright", warn=True, charge=1, sway=2),
            P(bx=5, by=3, hx=6, hy=1, lens="bright", warn=True, charge=2, prod=0.15, sway=2)]
    # strike (drawn in front): contact lunge, hold, recover.  Damage lands at windup end -> frame 0 is contact.
    out += [P(bx=-6, by=1, hx=-8, hy=2, near=(-6, 0), far=(5, 0), lens="bright", prod=1.0, spark=2, sway=-2),
            P(bx=-5, by=1, hx=-6, hy=2, near=(-6, 0), far=(5, 0), prod=0.8, spark=1, sway=-1),
            P(bx=-2, hx=-2, hy=1, near=(-4, 0), far=(4, 0), prod=0.3, sway=0)]
    # hit: recoil with a moderate baked warm tint, no white flash.
    out += [P(bx=4, hx=3, hy=-1, lens="dim", tint=0.30, sparks=1, sway=2),
            P(bx=2, hx=2, tint=0.15, sway=1),
            P(bx=1, hx=1, tint=0.0)]
    # defeat: sparks, buckle, slump, collapse, dark lens + smoke (last frame holds).
    out += [P(bx=5, hx=3, lens="dim", tint=0.25, sparks=2, sway=2),
            P(bx=4, by=5, hx=3, hy=3, lens="dim", sparks=1, droop=2, near=(-4, 0), far=(5, 0), shadow=21),
            P(bx=3, by=10, hx=3, hy=6, lens="dim", droop=4, near=(-6, 0), far=(7, 0), shadow=22),
            P(bx=2, by=15, hx=-4, hy=7, lens="dark", droop=5, near=(3, 0), far=(10, 0), smoke=1, shadow=22),
            P(bx=2, by=16, hx=-5, hy=8, lens="dark", droop=5, near=(3, 0), far=(10, 0), smoke=2, shadow=22)]
    assert len(out) == sum(STATES.values())
    return out


def blank():
    return Image.new("RGBA", (W, H), (0, 0, 0, 0))


def ik_knee(hip, ankle, l1=11.0, l2=12.0):
    """Reverse knee: the knee bends FORWARD (toward -x, the party) of the hip-ankle line."""
    hx, hy = hip
    ax, ay = ankle
    dx, dy = ax - hx, ay - hy
    d = max(1.0, min((dx * dx + dy * dy) ** 0.5, l1 + l2 - 0.01))
    a = (l1 * l1 - l2 * l2 + d * d) / (2 * d)
    h = max(0.0, l1 * l1 - a * a) ** 0.5
    mx, my = hx + a * dx / d, hy + a * dy / d
    # Perpendicular pointing forward (-x).
    px, py = -dy / d, dx / d
    if px > 0:
        px, py = -px, -py
    # A collapsing hip must not push the knee through the floor: the knee folds forward instead.
    return (round(mx + h * px), min(round(my + h * py), SOLE - 4))


def thick(d, a, b, width, fill):
    d.line([a, b], fill=OUT, width=width + 2)
    d.line([a, b], fill=fill, width=width)


def draw_leg(d, hip, foot_x, lift, mid, dark, light):
    ankle = (foot_x, SOLE - 3 - lift)
    knee = ik_knee(hip, ankle)
    thick(d, hip, knee, 4, mid)
    d.line([(hip[0] - 1, hip[1]), (knee[0] - 1, knee[1] - 1)], fill=light)
    thick(d, knee, ankle, 3, dark)
    d.line([(knee[0] + 1, knee[1]), (ankle[0] + 1, ankle[1])], fill=mid)
    d.ellipse([knee[0] - 3, knee[1] - 3, knee[0] + 3, knee[1] + 3], fill=dark, outline=OUT)
    d.point((knee[0] - 1, knee[1] - 1), fill=light)
    # boot: wedge toe forward (left), heel spur back; sole on row SOLE when planted.
    sole = SOLE - lift
    ax = ankle[0]
    d.polygon([(ax - 7, sole), (ax - 5, sole - 4), (ax + 3, sole - 4), (ax + 5, sole)], fill=mid, outline=OUT)
    d.line([(ax - 4, sole - 3), (ax + 2, sole - 3)], fill=light)
    d.line([(ax - 6, sole - 1), (ax + 4, sole - 1)], fill=dark)


def lens_colors(mode):
    return {"lit": (TEAL, TEAL_L), "bright": (TEAL_L, TEAL_X), "dim": (TEAL_D, TEAL), "dark": (DARK_LENS, DARK_LENS)}[mode]


def build_frame(pose):
    L = {name: blank() for name in LAYERS}
    bx, by = pose["bx"], pose["by"]
    cx, cy = 62 + bx, 37 + by                       # hull centre
    hip_near, hip_far = (cx - 4, cy + 11), (cx + 2, cy + 10)
    hcx, hcy = cx - 18 + pose["hx"], cy - 8 + pose["hy"] + pose["droop"]

    # shadow: contact ellipse under the feet, narrows slightly as the body lifts on the gait.
    d = ImageDraw.Draw(L["shadow"])
    sx = 58 + bx // 2
    sw = pose["shadow"]
    d.ellipse([sx - sw, 63, sx + sw, 68], fill=SHADOW)

    d = ImageDraw.Draw(L["far-leg"])
    draw_leg(d, hip_far, hip_far[0] + pose["far"][0], pose["far"][1], FAR_M, FAR_D, STEEL_M)

    # hull: armoured egg with four-step warm plate ramp, belly seam, amber warning plate, rear teal vent, antenna.
    d = ImageDraw.Draw(L["hull"])
    tip = (cx + 12 + pose["sway"], cy - 26 + pose["droop"] // 2)
    d.line([(cx + 9, cy - 10), tip], fill=OUT, width=3)
    d.line([(cx + 9, cy - 10), tip], fill=STEEL_L, width=1)
    d.rectangle([tip[0] - 1, tip[1] - 2, tip[0] + 1, tip[1]], fill=TEAL if pose["lens"] != "dark" else TEAL_D, outline=OUT)
    if pose["lens"] in ("lit", "bright"):
        d.point((tip[0], tip[1] - 1), fill=TEAL_L)
    d.rectangle([cx + 12, cy - 7, cx + 18, cy + 3], fill=STEEL_D, outline=OUT)
    for yy in (cy - 5, cy - 2, cy + 1):
        d.line([(cx + 14, yy), (cx + 16, yy)], fill=TEAL if pose["lens"] != "dark" else TEAL_D)
    d.ellipse([cx - 16, cy - 12, cx + 16, cy + 11], fill=PLATE_D, outline=OUT)
    d.ellipse([cx - 14, cy - 11, cx + 13, cy + 5], fill=PLATE_M)
    d.ellipse([cx - 11, cy - 10, cx + 7, cy - 2], fill=PLATE_L)
    d.line([(cx - 7, cy - 9), (cx + 2, cy - 9)], fill=PLATE_H)
    d.point((cx - 9, cy - 8), fill=PLATE_H)
    d.line([(cx - 14, cy + 4), (cx + 14, cy + 4)], fill=PLATE_D)
    d.line([(cx - 13, cy + 5), (cx + 13, cy + 5)], fill=OUT)
    for rx in (cx - 10, cx - 3, cx + 4, cx + 11):
        d.point((rx, cy + 7), fill=PLATE_L)
    amber, amber_d = (AMBER_H, AMBER) if pose["warn"] else (AMBER, AMBER_D)
    d.rectangle([cx - 1, cy - 5, cx + 8, cy], fill=amber, outline=OUT)
    for k in range(0, 9, 3):
        d.line([(cx + k, cy - 1), (cx + k + 3, cy - 4)], fill=amber_d)
    d.ellipse([cx - 8, cy + 6, cx + 2, cy + 13], fill=MOSS, outline=OUT)
    d.point((cx - 5, cy + 8), fill=MOSS_L)

    # head: chamfered steel visor box on a neck strut, one teal lens at the front.
    d = ImageDraw.Draw(L["head"])
    thick(d, (cx - 10, cy - 3), (hcx + 6, hcy + 2), 3, STEEL_D)
    box = [(hcx - 12, hcy - 4), (hcx - 9, hcy - 7), (hcx + 8, hcy - 7), (hcx + 11, hcy - 4),
           (hcx + 11, hcy + 4), (hcx + 8, hcy + 6), (hcx - 9, hcy + 6), (hcx - 12, hcy + 3)]
    d.polygon(box, fill=STEEL_M, outline=OUT)
    d.line([(hcx - 8, hcy - 6), (hcx + 7, hcy - 6)], fill=STEEL_H)
    d.line([(hcx - 10, hcy - 5), (hcx + 9, hcy - 5)], fill=STEEL_L)
    d.line([(hcx - 9, hcy + 5), (hcx + 8, hcy + 5)], fill=STEEL_D)
    d.line([(hcx - 11, hcy + 3), (hcx + 10, hcy + 3)], fill=STEEL_D)
    d.rectangle([hcx - 12, hcy - 2, hcx + 3, hcy + 1], fill=VISOR)
    base, core = lens_colors(pose["lens"])
    d.rectangle([hcx - 12, hcy - 2, hcx - 8, hcy + 1], fill=base, outline=None)
    d.line([(hcx - 11, hcy - 1), (hcx - 10, hcy - 1)], fill=core)
    if pose["lens"] in ("lit", "bright"):
        d.point((hcx - 7, hcy), fill=TEAL_D)
    if pose["lens"] == "bright":
        d.point((hcx - 13, hcy - 1), fill=TEAL_L)
        d.point((hcx - 13, hcy), fill=TEAL)
    d.rectangle([hcx + 5, hcy - 3, hcx + 8, hcy + 1], fill=STEEL_D, outline=OUT)

    d = ImageDraw.Draw(L["near-leg"])
    draw_leg(d, hip_near, hip_near[0] + pose["near"][0], pose["near"][1], STEEL_M, STEEL_D, STEEL_L)

    # prod: short shock prod under the visor; extends ~14 px at contact.  Never a claw.
    d = ImageDraw.Draw(L["prod"])
    root = (hcx - 4, hcy + 7)
    reach = round(5 + 14 * pose["prod"])
    ptip = (root[0] - reach, root[1] + (1 if pose["prod"] > 0.5 else 0))
    thick(d, (root[0] + 3, root[1] - 1), root, 2, STEEL_D)
    thick(d, root, ptip, 1, STEEL_L)
    d.rectangle([ptip[0] - 2, ptip[1] - 1, ptip[0], ptip[1] + 1], fill=TEAL if pose["lens"] != "dark" else STEEL_D, outline=OUT)

    # fx: charge glints, contact spark, damage sparks, smoke.
    d = ImageDraw.Draw(L["fx"])
    tx, ty = ptip[0] - 1, ptip[1]
    if pose["charge"]:
        for dx, dy in ((-3, 0), (0, -3), (0, 3)) if pose["charge"] == 1 else ((-4, 0), (-3, -3), (-3, 3), (0, -4), (0, 4)):
            d.point((tx + dx, ty + dy), fill=TEAL_L)
    if pose["spark"]:
        r = 2 + 2 * pose["spark"]
        for dx, dy in ((-r, 0), (0, -r), (0, r), (-r + 1, -r + 1), (-r + 1, r - 1)):
            d.line([(tx, ty), (tx + dx, ty + dy)], fill=TEAL_L)
        d.point((tx - 1, ty), fill=TEAL_X)
        d.point((tx - r - 1, ty), fill=TEAL)
    if pose["sparks"]:
        for dx, dy in ((cx - 6, cy - 10), (cx + 5, cy - 13), (cx + 12, cy - 4))[:1 + pose["sparks"]]:
            d.line([(dx - 1, dy), (dx + 1, dy)], fill=AMBER_H)
            d.line([(dx, dy - 1), (dx, dy + 1)], fill=AMBER_H)
    if pose["smoke"]:
        for k in range(pose["smoke"] + 1):
            ox, oy = cx + 4 + 3 * k, cy - 14 - 4 * k
            d.ellipse([ox - 2, oy - 2, ox + 2, oy + 1], fill=SMOKE)

    if pose["tint"] > 0:
        for name in TINTED:
            L[name] = tint_layer(L[name], pose["tint"])
    return L


def tint_layer(image, k):
    px = image.load()
    for y in range(H):
        for x in range(W):
            r, g, b, a = px[x, y]
            if a:
                px[x, y] = (round(r + (HIT_TINT[0] - r) * k), round(g + (HIT_TINT[1] - g) * k),
                            round(b + (HIT_TINT[2] - b) * k), a)
    return image


def composite(layers):
    out = blank()
    for name in LAYERS:
        out = Image.alpha_composite(out, layers[name])
    return out


def png(image):
    buf = io.BytesIO()
    image.save(buf, "PNG", optimize=False, compress_level=9)
    return buf.getvalue()


def sha(data):
    return hashlib.sha256(data).hexdigest()


def load_helper():
    spec = importlib.util.spec_from_file_location("patrol_native_format_helper", HELPER)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    module.W, module.H = W, H
    return module


def state_ranges():
    ranges, start = {}, 0
    for state, count in STATES.items():
        ranges[state] = list(range(start, start + count))
        start += count
    return ranges


def build():
    helper = load_helper()
    ranges = state_ranges()
    frames = [build_frame(p) for p in poses()]
    comps = [composite(f) for f in frames]
    for i, c in enumerate(comps):
        if c.getbbox() is None:
            raise RuntimeError(f"frame {i} is empty")
        # Hit tint stays moderate: no fully white body pixels and no frame mostly near-white.
        bright = sum(1 for p in c.get_flattened_data() if p[3] == 255 and min(p[:3]) >= 235)
        if bright > 12:
            raise RuntimeError(f"frame {i}: {bright} near-white pixels (flash guard)")
    durations, tags = [], []
    for state, idx in ranges.items():
        durations += [FRAME_TIME[state] * FPS] * len(idx)
        tags.append({"color": "(0.2, 0.6, 0.6, 1.0)", "from": idx[0] + 1, "name": state, "to": idx[-1] + 1,
                     "user_data": ""})
    files = {}
    strip = Image.new("RGBA", (W * len(comps), H), (0, 0, 0, 0))
    for i, c in enumerate(comps):
        strip.paste(c, (i * W, 0))
    strip_name = f"{PREFIX}battle-animation-strip_{STAMP}.png"
    files[strip_name] = png(strip)
    pxo_name = f"{PREFIX}battle-animation-layered_{STAMP}.pxo"
    raw = helper.make_pxo(frames, durations, png(comps[0]), pxo_name, FPS, order=LAYERS, dt=PXO_DT)
    files[pxo_name] = patch_pxo(raw, tags, json.dumps({"pivot": list(ANCHOR), "cell": [W, H], "states": ranges}))
    check_pxo(files[pxo_name], frames, comps, durations, tags)
    ora_names = {}
    for state, idx in ranges.items():
        index = idx[REP[state]]
        name = f"{PREFIX}battle-animation-{state}-f{index:02d}-layers_{STAMP}.ora"
        files[name] = helper.ora_bytes({n: frames[index][n] for n in LAYERS})
        check_ora(files[name], frames[index], comps[index])
        ora_names[state] = name
    package_name = f"{PREFIX}battle-animation-runtime-package_{STAMP}.json"
    package = {
        "schema": "worlds-between.enemy-battle-animation.v1",
        "enemy": "patrol",
        "approved": False,
        "strip": f"{RES_DIR}/{strip_name}",
        "strip_sha256": sha(files[strip_name]),
        "cell": [W, H],
        "anchor": list(ANCHOR),
        "body_center_x": BODY_CENTER_X,
        "frame_count": len(comps),
        "states": ranges,
        "frame_time": {k: FRAME_TIME[k] for k in ("idle", "strike", "hit", "defeat")},
        "gait_step_px": GAIT_STEP,
        "move_grace": 0.08,
        "front_states": ["strike"],
        "windup_phases": True,
        "telegraph_center_y": 244.0,
        "telegraph_scale": [1.6, 1.05],
    }
    files[package_name] = (json.dumps(package, indent=2, ensure_ascii=False) + "\n").encode("utf-8")
    manifest_name = f"{PREFIX}battle-animation-manifest_{STAMP}.json"
    manifest = {
        "task": "content.enemy.patrol.battle-animation",
        "status": "UNAPPROVED technical candidate; off by default; not a full-sprite or art acceptance claim",
        "identitySource": "assets/enemies/patrol/static-bench-v01 (selected Patrol native static); no Sentry pixels used",
        "builder": os.path.basename(__file__),
        "builderSha256TextLf": sha(open(__file__, "rb").read().replace(b"\r\n", b"\n")),
        "helperSha256TextLf": sha(open(HELPER, "rb").read().replace(b"\r\n", b"\n")),
        "loader": f"{PREFIX}battle-animation-loader_{STAMP}.gd",
        "loaderSha256TextLf": sha(open(os.path.join(HERE, f"{PREFIX}battle-animation-loader_{STAMP}.gd"), "rb").read().replace(b"\r\n", b"\n")),
        "hashNormalization": {"png/pxo/ora": "sha256-bytes", "json/md/py/gd": "sha256-text-lf-v1"},
        "cell": [W, H], "anchor": list(ANCHOR), "layers": LAYERS, "states": ranges,
        "frameTimeSeconds": FRAME_TIME, "pxoFps": FPS, "pxoDurationsInFrames": durations,
        "oraRepresentatives": ora_names,
        "artefacts": {n: sha(b) for n, b in sorted(files.items())},
    }
    files[manifest_name] = (json.dumps(manifest, indent=2, ensure_ascii=False) + "\n").encode("utf-8")
    return files, frames, comps


def patch_pxo(raw, tags, user_data):
    with zipfile.ZipFile(io.BytesIO(raw)) as src:
        data = json.loads(src.read("data.json"))
        data["tags"] = tags
        data["user_data"] = user_data
        out = io.BytesIO()
        with zipfile.ZipFile(out, "w", zipfile.ZIP_DEFLATED) as dst:
            for info in src.infolist():
                payload = src.read(info.filename)
                if info.filename == "data.json":
                    payload = json.dumps(data, separators=(",", ":")).encode("utf-8")
                dst.writestr(zipfile.ZipInfo(info.filename, PXO_DT), payload, zipfile.ZIP_DEFLATED)
    return out.getvalue()


def check_pxo(raw, frames, comps, durations, tags):
    with zipfile.ZipFile(io.BytesIO(raw)) as z:
        if z.testzip() is not None:
            raise RuntimeError("PXO CRC")
        data = json.loads(z.read("data.json"))
        n = len(frames)
        if len(z.namelist()) != 3 + n + n * len(LAYERS) * 2:
            raise RuntimeError("PXO entry count")
        if (data["size_x"], data["size_y"], data["fps"], data["pxo_version"]) != (W, H, FPS, 7):
            raise RuntimeError("PXO header")
        if [l["name"] for l in data["layers"]] != LAYERS or len(data["frames"]) != n or data["tags"] != tags:
            raise RuntimeError("PXO layers/frames/tags")
        for i in range(n):
            if abs(data["frames"][i]["duration"] - durations[i]) > 1e-12:
                raise RuntimeError(f"PXO duration {i}")
            acc = blank()
            for li, name in enumerate(LAYERS, start=1):
                cel = Image.frombytes("RGBA", (W, H), z.read(f"image_data/frames/{i + 1}/layer_{li}"))
                if cel.tobytes() != frames[i][name].tobytes():
                    raise RuntimeError(f"PXO cel {i}/{name}")
                acc = Image.alpha_composite(acc, cel)
            if acc.tobytes() != comps[i].tobytes():
                raise RuntimeError(f"PXO composite {i}")


def check_ora(raw, layers, comp):
    with zipfile.ZipFile(io.BytesIO(raw)) as z:
        if z.testzip() is not None or z.read("mimetype") != b"image/openraster":
            raise RuntimeError("ORA container")
        stack = ET.fromstring(z.read("stack.xml")).findall(".//layer")
        if [el.get("name") for el in stack] != list(reversed(LAYERS)):
            raise RuntimeError("ORA stack order")
        for el in stack:
            img = Image.open(io.BytesIO(z.read(el.get("src")))).convert("RGBA")
            if img.tobytes() != layers[el.get("name")].tobytes():
                raise RuntimeError(f"ORA layer {el.get('name')}")
        merged = Image.open(io.BytesIO(z.read("mergedimage.png"))).convert("RGBA")
        if merged.tobytes() != comp.tobytes():
            raise RuntimeError("ORA merged")


def ext(path):
    path = os.path.abspath(path)
    return "\\\\?\\" + path if os.name == "nt" and not path.startswith("\\\\?\\") else path


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out-dir", default=HERE)
    ap.add_argument("--check", action="store_true")
    args = ap.parse_args()
    files, _, _ = build()
    again, _, _ = build()
    if {k: sha(v) for k, v in files.items()} != {k: sha(v) for k, v in again.items()}:
        raise SystemExit("PATROL_ANIM_BUILD FAIL non-deterministic rebuild")
    if args.check:
        bad = []
        for name, data in files.items():
            path = ext(os.path.join(args.out_dir, name))
            if not os.path.exists(path):
                bad.append(f"missing {name}")
                continue
            disk = open(path, "rb").read()
            if name.endswith((".json",)):
                disk, data = disk.replace(b"\r\n", b"\n"), data.replace(b"\r\n", b"\n")
            if disk != data:
                bad.append(f"differs {name}")
        if bad:
            raise SystemExit("PATROL_ANIM_CHECK FAIL " + "; ".join(bad))
        print(f"PATROL_ANIM_CHECK OK files={len(files)}")
        return
    os.makedirs(ext(args.out_dir), exist_ok=True)
    for name, data in files.items():
        with open(ext(os.path.join(args.out_dir, name)), "wb") as fh:
            fh.write(data)
    print(f"PATROL_ANIM_BUILD OK files={len(files)}")
    for name, data in sorted(files.items()):
        print(sha(data), name)


if __name__ == "__main__":
    main()
