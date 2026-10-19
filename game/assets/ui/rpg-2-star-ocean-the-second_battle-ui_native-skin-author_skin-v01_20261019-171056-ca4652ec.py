#!/usr/bin/env python3
"""Build the Worlds Between battle HUD skin kit as native pixel art.

Eleven separate nine-patch PNGs (no atlas, no contact sheet), each with a
one-frame role-layered PXO and ORA, plus a manifest with pixel size, slices,
roles, layer names and raw SHA-256 hashes.

Every pixel is painted from a small fixed palette by an integer "ring level"
rule on a chamfered rectangle: level 0 outline, 1 bevel, 2 hairline, 3+ field.
There is no smoothing, filtering, gradient or noise.  Corner cuts stay inside
the slice corners so stretching never touches a diagonal.

The shared native-format helper is imported from the copied, proven
``assets/inputs`` path relative to this author (same convention as the common
VFX author).  ``--check`` rebuilds into memory and compares every byte with the
files on disk without writing anything.
"""
from __future__ import annotations

import argparse
import hashlib
import importlib.util
import io
import json
import os
import sys
from pathlib import Path

from PIL import Image

PROJECT = "rpg-2-star-ocean-the-second"
SUBJECT = "battle-ui"
PREFIX = PROJECT + "_" + SUBJECT + "_"
VARIANT = "skin-v01"
RUN_STAMP = "20261019-171056"
RUN_ID = "ca4652ec"
TAG = VARIANT + "_" + RUN_STAMP + "-" + RUN_ID
SUFFIX = "_" + TAG
PACKAGE_DIR = "battle-skin-v01"

CLEAR = (0, 0, 0, 0)

# Palette: restrained science-region navy/teal, warm old bronze, pale parchment.
OUTLINE = (5, 9, 14, 255)
NAVY_BAND = (12, 22, 32, 255)
NAVY_PANEL = (21, 35, 47, 255)
TEAL_HAIR = (31, 74, 80, 255)
TEAL_HAIR_PANEL = (40, 92, 96, 255)
BRONZE_LIGHT = (184, 147, 90, 255)
BRONZE = (141, 106, 62, 255)
BRONZE_DARK = (90, 65, 39, 255)
BRONZE_DEEP = (74, 56, 35, 255)
PARCHMENT = (239, 226, 191, 255)

BTN_FIELD = (27, 51, 64, 255)
BTN_LIGHT = (79, 141, 139, 255)
BTN_DARK = (22, 50, 58, 255)
BTN_HOVER_FIELD = (35, 68, 84, 255)
BTN_HOVER_LIGHT = (110, 176, 170, 255)
BTN_HOVER_DARK = (28, 62, 70, 255)
BTN_PRESSED_FIELD = (18, 38, 51, 255)
BTN_PRESSED_TOP = (11, 25, 33, 255)
BTN_PRESSED_LOW = (62, 118, 116, 255)
BTN_DIS_OUTLINE = (10, 16, 23, 255)
BTN_DIS_BEVEL = (38, 50, 58, 255)
BTN_DIS_FIELD = (18, 27, 35, 255)

TROUGH_FIELD = (17, 30, 41, 255)
TROUGH_TOP = (10, 19, 27, 255)

# Semantic fills: (highlight row / tip, body, shadow row / left edge).
FILLS = {
    "health": ((240, 164, 143, 255), (214, 115, 99, 255), (142, 63, 57, 255)),
    "energy": ((169, 236, 234, 255), (79, 185, 190, 255), (35, 118, 124, 255)),
    "enemy": ((229, 154, 178, 255), (168, 80, 110, 255), (98, 38, 62, 255)),
}

# Button font colours (applied as theme colour overrides, never font/size).
FONT_COLORS = {
    "font_color": "#e8dcbf",
    "font_hover_color": "#f6efda",
    "font_pressed_color": "#efe2bf",
    "font_hover_pressed_color": "#efe2bf",
    "font_focus_color": "#f6efda",
    "font_disabled_color": "#7f8c90",
}


def level(x: int, y: int, w: int, h: int, cut: int) -> tuple[int, str]:
    """Ring level on a chamfered rectangle plus the side that set it."""
    terms = [(x, "left"), (y, "top"), (w - 1 - x, "right"), (h - 1 - y, "bottom")]
    cx = x if x < w // 2 else w - 1 - x
    cy = y if y < h // 2 else h - 1 - y
    corner = ("t" if y < h // 2 else "b") + ("l" if x < w // 2 else "r")
    terms.append((cx + cy - cut, "diag-" + corner))
    value, side = min(terms, key=lambda t: t[0])
    return value, side


def lit(side: str) -> str:
    if side in ("left", "top", "diag-tl"):
        return "light"
    if side in ("right", "bottom", "diag-br"):
        return "dark"
    return "mid"


def corner_local(x: int, y: int, w: int, h: int) -> tuple[int, int]:
    return (x if x < w // 2 else w - 1 - x, y if y < h // 2 else h - 1 - y)


def paint(w: int, h: int, fn) -> dict[str, Image.Image]:
    """Run a per-pixel painter returning (role, rgba) into ordered role layers."""
    layers: dict[str, Image.Image] = {}
    order: list[str] = []
    cells = []
    for y in range(h):
        for x in range(w):
            role, rgba = fn(x, y)
            cells.append((x, y, role, rgba))
            if role is not None and role not in order:
                order.append(role)
    for role in order:
        layers[role] = Image.new("RGBA", (w, h), CLEAR)
    for x, y, role, rgba in cells:
        if role is not None and rgba[3] > 0:
            layers[role].putpixel((x, y), rgba)
    return layers


def frame_painter(w, h, cut, outline, bevel_light, bevel_mid, bevel_dark,
                  hair, field, rivet=None):
    def fn(x, y):
        lv, side = level(x, y, w, h, cut)
        if lv < 0:
            return None, CLEAR
        if lv == 0:
            return "outline", outline
        if lv == 1:
            tone = lit(side)
            return "bevel", {"light": bevel_light, "mid": bevel_mid, "dark": bevel_dark}[tone]
        if lv == 2 and hair is not None:
            return "hairline", hair
        if rivet is not None and corner_local(x, y, w, h) == (3, 3):
            return "joint", rivet
        return "field", field
    return fn


# --- Skin definitions -------------------------------------------------------

def skin_hud_band():
    return paint(24, 24, frame_painter(24, 24, 3, OUTLINE, BRONZE, BRONZE_DARK,
                                       BRONZE_DARK, TEAL_HAIR, NAVY_BAND,
                                       rivet=BRONZE_LIGHT))


def skin_panel():
    return paint(24, 24, frame_painter(24, 24, 3, OUTLINE, BRONZE_LIGHT, BRONZE,
                                       BRONZE_DARK, TEAL_HAIR_PANEL, NAVY_PANEL,
                                       rivet=BRONZE_LIGHT))


def skin_button_normal():
    return paint(16, 16, frame_painter(16, 16, 1, OUTLINE, BTN_LIGHT, BTN_DARK,
                                       BTN_DARK, None, BTN_FIELD))


def skin_button_hover():
    return paint(16, 16, frame_painter(16, 16, 1, BRONZE, BTN_HOVER_LIGHT,
                                       BTN_HOVER_DARK, BTN_HOVER_DARK, None,
                                       BTN_HOVER_FIELD))


def skin_button_pressed():
    # Inverted bevel: shadow on top/left, teal catch-light low/right.
    return paint(16, 16, frame_painter(16, 16, 1, BRONZE_DARK, BTN_PRESSED_TOP,
                                       BTN_PRESSED_TOP, BTN_PRESSED_LOW, None,
                                       BTN_PRESSED_FIELD))


def skin_button_disabled():
    return paint(16, 16, frame_painter(16, 16, 1, BTN_DIS_OUTLINE, BTN_DIS_BEVEL,
                                       BTN_DIS_BEVEL, BTN_DIS_BEVEL, None,
                                       BTN_DIS_FIELD))


def skin_button_focus():
    # Overlay drawn above the state skin: parchment ring, bronze corner brackets,
    # transparent field so the state underneath still reads.
    w = h = 16

    def fn(x, y):
        lv, _side = level(x, y, w, h, 1)
        if lv < 0:
            return None, CLEAR
        if lv == 0:
            return "focus-ring", PARCHMENT
        cx, cy = corner_local(x, y, w, h)
        if lv == 1 and cx <= 3 and cy <= 3:
            return "corner-brackets", BRONZE_LIGHT
        return "clear-field", CLEAR
    return paint(w, h, fn)


def skin_bar_trough():
    w = h = 16

    def fn(x, y):
        lv, _side = level(x, y, w, h, 1)
        if lv < 0:
            return None, CLEAR
        if lv == 0:
            return "bronze-rim", BRONZE_DEEP
        if lv == 1:
            return "inner-shadow", OUTLINE
        if y == 2:
            return "trough", TROUGH_TOP
        return "trough", TROUGH_FIELD
    return paint(w, h, fn)


def fill_painter(kind):
    light, body, shadow = FILLS[kind]
    w = h = 16

    def fn(x, y):
        # Rows 0-1 / 14-15 and columns 0 / 15 stay clear so the trough rim shows.
        if y < 2 or y > 13 or x == 0 or x == 15:
            return "clear-inset", CLEAR
        if x == 1:
            return "shadow", shadow
        if x == 14:
            return "tip", light
        if y == 2:
            return "highlight", light
        if y == 13:
            return "shadow", shadow
        return "body", body
    return paint(w, h, fn)


SLICE4 = {"left": 4, "top": 4, "right": 4, "bottom": 4}
SLICE_FILL = {"left": 2, "top": 4, "right": 2, "bottom": 4}

SKINS = [
    # key, builder, slices, intended nodes
    ("hud-band", skin_hud_band, SLICE4,
     "NinePatchRect child of header ColorRect (0,0 640x90) and footer ColorRect (0,302 640x58)"),
    ("panel", skin_panel, SLICE4,
     "NinePatchRect child of pause panel ColorRect (55,43 530x265) and result panel ColorRect (112,99 416x171)"),
    ("button-normal", skin_button_normal, SLICE4, "Button 'normal' StyleBoxTexture"),
    ("button-hover", skin_button_hover, SLICE4, "Button 'hover' StyleBoxTexture"),
    ("button-pressed", skin_button_pressed, SLICE4,
     "Button 'pressed' and 'hover_pressed' StyleBoxTexture"),
    ("button-disabled", skin_button_disabled, SLICE4, "Button 'disabled' StyleBoxTexture"),
    ("button-focus", skin_button_focus, SLICE4, "Button 'focus' overlay StyleBoxTexture"),
    ("bar-trough", skin_bar_trough, SLICE4, "ProgressBar 'background' for hp/energy/enemy bars"),
    ("bar-fill-health", lambda: fill_painter("health"), SLICE_FILL, "hp_bar 'fill'"),
    ("bar-fill-energy", lambda: fill_painter("energy"), SLICE_FILL, "energy_bar 'fill'"),
    ("bar-fill-enemy", lambda: fill_painter("enemy"), SLICE_FILL, "enemy_bar 'fill'"),
]
assert len(SKINS) <= 11


# --- IO ---------------------------------------------------------------------

def helper_path() -> Path:
    here = Path(__file__).resolve()
    return here.parent.parent / "inputs" / (
        PROJECT + "_benchmark_native-format-helper_v01_20261018-234437-8dfccbf6.py"
    )


def load_helper():
    spec = importlib.util.spec_from_file_location("shared_native_helper", helper_path())
    if spec is None or spec.loader is None:
        raise RuntimeError("cannot load shared native-format helper")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def png_bytes(img: Image.Image) -> bytes:
    buf = io.BytesIO()
    img.save(buf, format="PNG", compress_level=9)
    return buf.getvalue()


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def combine(layers: dict[str, Image.Image]) -> Image.Image:
    first = next(iter(layers.values()))
    out = Image.new("RGBA", first.size, CLEAR)
    for img in layers.values():
        out.alpha_composite(img)
    return out


def render(out_dir: Path) -> dict[str, bytes]:
    """Return {filename: bytes} for the whole package (pure, no writes)."""
    helper = load_helper()
    source_path = Path(__file__).resolve()
    helper_file = helper_path().resolve()
    files: dict[str, bytes] = {}
    skins = {}
    for key, builder, slices, nodes in SKINS:
        layers = builder()
        composite = combine(layers)
        w, h = composite.size
        png_name = PREFIX + "skin-" + key + SUFFIX + ".png"
        pxo_name = PREFIX + "skin-" + key + "_1frame" + SUFFIX + ".pxo"
        ora_name = PREFIX + "skin-" + key + "_layered" + SUFFIX + ".ora"
        png = png_bytes(composite)
        pxo = helper.pxo_bytes([layers], [1.0], png, pxo_name)
        ora = helper.ora_bytes(layers)
        files[png_name] = png
        files[pxo_name] = pxo
        files[ora_name] = ora
        colors = sorted({c for c in composite.getdata() if c[3] > 0})
        skins[key] = {
            "png": png_name,
            "pxo": pxo_name,
            "ora": ora_name,
            "size": [w, h],
            "slices": dict(slices),
            "layerRoles": list(layers),
            "opaqueColorCount": len(colors),
            "intendedNodes": nodes,
            "sha256": {png_name: sha(png), pxo_name: sha(pxo), ora_name: sha(ora)},
        }
    manifest_name = PREFIX + "asset-manifest" + SUFFIX + ".json"
    manifest = {
        "schemaVersion": 1,
        "project": PROJECT,
        "subject": SUBJECT,
        "variant": VARIANT,
        "packageId": RUN_STAMP + "-" + RUN_ID,
        "scope": "content.ui-visual.battle",
        "status": "UNAPPROVED technical candidate; not creator-approved",
        "filter": "nearest",
        "skinOrder": [s[0] for s in SKINS],
        "fontColors": FONT_COLORS,
        "source": {"path": Path(os.path.relpath(source_path, out_dir)).as_posix(),
                   "sha256": sha(source_path.read_bytes())},
        "helper": {"path": Path(os.path.relpath(helper_file, out_dir)).as_posix(),
                   "sha256": sha(helper_file.read_bytes()),
                   "origin": "copied proven native-format helper (PXO v7 / ORA)"},
        "skins": skins,
    }
    files[manifest_name] = (json.dumps(manifest, indent=2) + "\n").encode("utf-8")
    return files


def self_check(files: dict[str, bytes]) -> list[str]:
    """Structural checks on the in-memory package; returns failure strings."""
    import zipfile
    fails = []
    manifest = json.loads(next(v for k, v in files.items() if k.endswith(".json")))
    for key, entry in manifest["skins"].items():
        img = Image.open(io.BytesIO(files[entry["png"]]))
        if img.mode != "RGBA" or list(img.size) != entry["size"]:
            fails.append(f"{key}: mode/size {img.mode} {img.size}")
        s = entry["slices"]
        w, h = img.size
        if s["left"] + s["right"] >= w or s["top"] + s["bottom"] >= h:
            fails.append(f"{key}: slices leave no stretch centre")
        alphas = {p[3] for p in img.getdata()}
        if not alphas <= {0, 255}:
            fails.append(f"{key}: non-binary alpha {sorted(alphas)}")
        # Stretch-safety: every centre row / column must be uniform across the
        # stretched span so nine-patch scaling cannot smear a detail.
        px = img.load()
        for y in range(h):
            row = {px[x, y] for x in range(s["left"], w - s["right"])}
            if len(row) != 1:
                fails.append(f"{key}: row {y} not uniform in stretch span")
                break
        for x in range(w):
            col = {px[x, y] for y in range(s["top"], h - s["bottom"])}
            if len(col) != 1:
                fails.append(f"{key}: column {x} not uniform in stretch span")
                break
        with zipfile.ZipFile(io.BytesIO(files[entry["ora"]])) as z:
            merged = Image.open(io.BytesIO(z.read("mergedimage.png"))).convert("RGBA")
            if merged.tobytes() != img.tobytes():
                fails.append(f"{key}: ORA merged image differs from PNG")
        with zipfile.ZipFile(io.BytesIO(files[entry["pxo"]])) as z:
            data = json.loads(z.read("data.json"))
            if [data["size_x"], data["size_y"]] != entry["size"] or len(data["frames"]) != 1:
                fails.append(f"{key}: PXO header size/frames")
            names = [l["name"] for l in data["layers"]]
            if names != entry["layerRoles"]:
                fails.append(f"{key}: PXO layer names")
            merged = Image.new("RGBA", img.size, CLEAR)
            for i in range(len(names)):
                raw = z.read(f"image_data/frames/1/layer_{i + 1}")
                merged.alpha_composite(Image.frombytes("RGBA", img.size, raw))
            if merged.tobytes() != img.tobytes():
                fails.append(f"{key}: PXO layers do not composite to PNG")
    return fails


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out-dir", required=True, type=Path)
    parser.add_argument("--check", action="store_true",
                        help="rebuild in memory and compare bytes with --out-dir; no writes")
    args = parser.parse_args()
    out_dir = args.out_dir.resolve()
    files = render(out_dir)
    fails = self_check(files)
    if args.check:
        for name, data in files.items():
            path = out_dir / name
            if not path.is_file() or path.read_bytes() != data:
                fails.append(f"byte mismatch or missing: {name}")
        extra = sorted(p.name for p in out_dir.iterdir() if p.name not in files) if out_dir.is_dir() else []
        if extra:
            fails.append(f"unexpected files: {extra}")
    else:
        out_dir.mkdir(parents=True, exist_ok=True)
        for name, data in files.items():
            (out_dir / name).write_bytes(data)
    for f in fails:
        print("FAIL", f)
    print(("CHECK" if args.check else "BUILD"), "files", len(files), "fails", len(fails),
          "PASS" if not fails else "FAIL")
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main())
