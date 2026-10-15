"""Author the UNAPPROVED native-pixel sentry automaton battle ANIMATION candidate, revision v3 (21 frames, facing left).

v3 is an isolated technical-art candidate on top of v2 (v2 is unapproved and awaiting human review;
nothing of v2 is modified). It targets the three visual issues the v2 QA note left open, without any
change to combat rules, timing, positions or the 21-frame state map:
  1. Strike reach: a target struck at 54-69 px (the unchanged 69 px reach) was hit while the v2
     lunge stopped about 16 px short of it. The physical lunge cannot know the target distance (the
     runtime picks frames by state and clock only), so v3 keeps the v2 lunge pose and adds a cyan
     claw-arc on the impact frame whose leading edge reaches enemy_x - 62, plus a breaking arc on the
     recoil frame. The arc is the strike's energy, drawn in the strike's existing front draw order.
  2. Charging eye: the runtime multiplies the whole sprite by ENEMY_WINDUP_MODULATE (1.0, 0.70, 0.66)
     during the wind-up, which turned the v2 cyan charge lens into a dull beige/teal disc. The v3
     wind-up frames repaint only the lens interior: a larger white-hot core inside a dark rim (coil),
     then a white ring around a cyan ring and white core (full charge), each with a four-point flare
     across the bezel, so the lens stays the brightest, highest-contrast part of the sprite under the
     unchanged tint. No palette colour keeps its cyan hue through that multiply; only luminance,
     contrast and structure can be recovered without a runtime change.
  3. Grounding: the runtime contact shadow is only drawn while enemy_hp > 0, so the v2 corpse floated.
     The v3 defeat frames carry a baked, ordered-dither shadow in the darkest palette colour, centred
     on the body like the runtime shadow and widening as the body settles.

Everything else is v2 pixel for pixel. The v2 author script is imported unchanged for its rig, poses,
palette and compositor; v3 only swaps the wind-up lens paint and adds effect pixels on transparent
cell pixels. Each v3 cell is the v2 cell placed 20 px from the left and on a 4 px taller canvas:
  - cell 132x66 (v2 112x62), runtime anchor (66, 60) (v2 46, 60), body centre x 84 (v2 64)
  - the anchor and body centre move with the margin, so the sprite draws exactly where v2 draws
  - frames 0-11 (idle, distance-keyed gait) and 16-17 (hit) are the v2 cells exactly, so the v2 gait
    lock and zero-slip measurement carry over unchanged
The runtime accepts these keys in ENEMY_SPRITE_ANIMATIONS["sentry"] already; v3 is not wired into
battle_arena.gd (a test-only helper points single battle instances at it).

Usage (bundled Python/Pillow runtime, run with -I):
  python <this file> --out DIR      -> scratch strip + frames for iteration, no manifest
  python <this file> --final DIR
      -> new uniquely named strip PNG, one PNG per frame (in a .gdignore folder) and a manifest in DIR.
         Never overwrites. No contact sheet or GIF is produced; review uses real Godot captures.
"""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import uuid
from datetime import datetime
from pathlib import Path

from PIL import Image

HERE = Path(__file__).resolve().parent
V2_AUTHOR = HERE / "rpg-2-star-ocean-the-second_scifi-sentry-automaton_battle-animation-pilot-author_m8-anim-v02_20261014-225908-7e2215bc.py"
V2_STRIP = HERE / "rpg-2-star-ocean-the-second_scifi-sentry-automaton_battle-animation-strip-left_m8-anim-v02_20261014-230329-ffefdc6f.png"
V2_MANIFEST = HERE / "rpg-2-star-ocean-the-second_scifi-sentry-automaton_battle-animation-manifest_m8-anim-v02_20261014-230329-ffefdc6f.json"
V2_STRIP_SHA256 = "26d1fb1c0d13371f348ec04c27b35901bd8a06701694446374dae6f27c35e52e"

_spec = importlib.util.spec_from_file_location("sentry_v2_author", V2_AUTHOR)
v2 = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(v2)

SLUG = v2.SLUG
PALETTE = v2.PALETTE
V2_W, V2_H = v2.SIZE
LEFT = 20
BOTTOM = 4
W, H = V2_W + LEFT, V2_H + BOTTOM
SIZE = (W, H)
ANCHOR_ROW = v2.ANCHOR_ROW
RUNTIME_ANCHOR = (v2.RUNTIME_ANCHOR[0] + LEFT, ANCHOR_ROW)
BODY_CENTER_X = v2.BODY_CENTER_X + LEFT
# v3 cell x of a static-plate x (static -> v2 adds the 16 px margin, v3 adds LEFT more).
OFFSET_X = v2.MARGIN + LEFT
STATES = v2.STATES
GAIT_STEP = v2.GAIT_STEP

# Runtime wind-up modulate (battle_arena.gd ENEMY_WINDUP_MODULATE), used only to measure the lens.
WINDUP_TINT = (1.0, 0.70, 0.66)
# Leading edge of the impact arc, relative to enemy_x (the unchanged strike reach is 69 px).
ARC_REACH = -62

BAYER4 = ((0, 8, 2, 10), (12, 4, 14, 6), (3, 11, 1, 9), (15, 7, 13, 5))


def rgb(key: str) -> tuple:
    h = PALETTE[key]
    return (int(h[1:3], 16), int(h[3:5], 16), int(h[5:7], 16))


# --- 2. Charging lens -------------------------------------------------------------------------------------
_v2_paint_lens = v2.paint_lens


def paint_lens_v3(r, mode: str) -> None:
    """v2 lens paints, plus the v3 wind-up lenses. Static eye: bezel oval 10..30 x 12..32, dark inner ring 13..27 x 15..29, lens 14..26 x 16..28."""
    if mode == "charge1v3":
        # Coil: dark teal rim, cyan ring, a 9 px white-hot core (v2: 6 px) and short flare stubs on the dark inner ring.
        r.oval(14, 16, 26, 28, "x")
        r.oval(15, 17, 25, 27, "z")
        r.oval(16, 18, 24, 26, "w", "p")
        r.px([(20, 15), (20, 29), (13, 22), (27, 22)], "z")
        r.px([(18, 19), (19, 19)], "z", "p")
    elif mode == "charge2v3":
        # Full charge: the white-hot charge has spread to a ring around a cyan ring and a white core, with a four-point
        # flare crossing the brass bezel. (A flat white disc measured brighter but read as a blank plate under the tint.)
        r.oval(14, 16, 26, 28, "y")
        r.oval(15, 17, 25, 27, "w")
        r.oval(17, 19, 23, 25, "z", "p")
        r.oval(18, 20, 22, 24, "w", "p")
        r.px([(20, 15), (20, 14), (20, 29), (20, 30), (13, 22), (12, 22), (27, 22), (28, 22)], "w")
        r.px([(20, 13), (20, 31), (11, 22), (29, 22)], "z")
    else:
        _v2_paint_lens(r, mode)


# build_parts() looks paint_lens up in the v2 module at call time; v2 modes keep their v2 paint.
v2.paint_lens = paint_lens_v3

# The v2 eye bezel box (static coordinates); the v3 lens repaint may only change pixels inside it.
EYE_BOX = (10, 12, 30, 32)
LENS_OVAL = (14, 16, 26, 28)
BEZEL_OVAL = (10, 12, 30, 32)
INNER_OVAL = (13, 15, 27, 29)


# --- 1. Strike claw-arc -----------------------------------------------------------------------------------
def arc_pixels(frame: str) -> list:
    """Cell-space (x, y, key) pixels of the claw-arc. Leading edge x(y) = tip + k (y - 42)^2 over rows 24..58,
    so it bows toward the party with its tip on row 42 at enemy_x - 62 and both ends curling back toward the sentry."""
    tip = RUNTIME_ANCHOR[0] + ARC_REACH
    k = 18 / 256
    out = []
    for y in range(24, 59):
        lead = tip + round(k * (y - 42) ** 2)
        # Thick in the middle, tapering to the ends.
        span = 1 if abs(y - 42) > 13 else (2 if abs(y - 42) > 7 else 3)
        if frame == "impact":
            out.append((lead, y, "z"))
            for i in range(1, span + 1):
                out.append((lead + i, y, "w" if i < span or span == 1 else "y"))
        else:
            # Recoil: the arc breaks up and dims in place, every other row, one pixel further out.
            if y % 2 == 0 and abs(y - 42) <= 15:
                out.append((lead - 1, y, "y"))
                if span > 1:
                    out.append((lead, y, "z" if abs(y - 42) <= 5 else "y"))
    return out


# --- 3. Defeat shadow -------------------------------------------------------------------------------------
# (half width, half height, peak density) per defeat frame; the body sinks 3 / 7 / 9 px over these frames.
SHADOW = {18: (30, 4.5, 6 / 16), 19: (40, 5.0, 8 / 16), 20: (46, 5.0, 8 / 16)}
SHADOW_KEY = "o"


def shadow_pixels(frame: int) -> list:
    """Ordered-dither ellipse in the darkest palette colour, centred on the body centre and the floor line
    (between rows 59 and 60, as the runtime shadow is centred on ARENA_FLOOR_Y). Density falls off toward the rim."""
    rx, ry, peak = SHADOW[frame]
    cx, cy = BODY_CENTER_X, ANCHOR_ROW
    out = []
    for y in range(int(cy - ry) - 1, int(cy + ry) + 2):
        for x in range(int(cx - rx) - 1, int(cx + rx) + 2):
            dx = (x + 0.5 - cx) / rx
            dy = (y + 0.5 - cy) / ry
            r = (dx * dx + dy * dy) ** 0.5
            if r >= 1.0 or not (0 <= x < W and 0 <= y < H):
                continue
            density = peak if r < 0.55 else peak * (1.0 - (r - 0.55) / 0.45 * 0.75)
            if BAYER4[y % 4][x % 4] + 0.5 < density * 16:
                out.append((x, y, SHADOW_KEY))
    return out


# --- Frames -----------------------------------------------------------------------------------------------
def v3_poses() -> list:
    frames = []
    for i, (state, p) in enumerate(v2.FRAMES):
        p = dict(p)
        if i == 12:
            p["eye"] = "charge1v3"
        elif i == 13:
            p["eye"] = "charge2v3"
        frames.append((state, p))
    return frames


FRAMES = v3_poses()
EFFECTS = {14: "impact", 15: "recoil"}


def place(cell: Image.Image) -> Image.Image:
    img = Image.new("RGBA", SIZE, (0, 0, 0, 0))
    img.paste(cell, (LEFT, 0))
    return img


def paint_transparent(img: Image.Image, pixels: list) -> int:
    """Effect pixels only fill transparent cell pixels, so no v2 sentry pixel is ever repainted."""
    px = img.load()
    count = 0
    for x, y, key in pixels:
        assert 0 <= x < W and 0 <= y < H, (x, y)
        if px[x, y][3] == 0:
            px[x, y] = rgb(key) + (255,)
            count += 1
    return count


def render_all() -> tuple[list, dict]:
    frames, added = [], {}
    for i, (state, p) in enumerate(FRAMES):
        img = place(v2.render(p))
        if i in EFFECTS:
            added[i] = paint_transparent(img, arc_pixels(EFFECTS[i]))
        if i in SHADOW:
            added[i] = paint_transparent(img, shadow_pixels(i))
        frames.append(img)
    expected = [s for s, n, _, _ in STATES for _ in range(n)]
    assert [s for s, _ in FRAMES] == expected and len(frames) == 21, "frame order must match the v2 state map"
    return frames, added


def pixels(img: Image.Image) -> list:
    return list(img.get_flattened_data() if hasattr(img, "get_flattened_data") else img.getdata())


def luma(c) -> float:
    return (0.2126 * c[0] + 0.7152 * c[1] + 0.0722 * c[2]) / 255.0


def tinted(c, tint) -> tuple:
    return tuple(round(c[i] * tint[i]) for i in range(3))


def in_oval(x, y, box) -> bool:
    x0, y0, x1, y1 = box
    cx, cy, rx, ry = (x0 + x1) / 2, (y0 + y1) / 2, (x1 - x0) / 2 + 0.5, (y1 - y0) / 2 + 0.5
    return ((x - cx) / rx) ** 2 + ((y - cy) / ry) ** 2 <= 1.0


def lens_metrics(img: Image.Image, head: tuple, tint) -> dict:
    """Lens disc vs the dark eye housing around the bezel, after the runtime modulate."""
    hx, hy = head
    px = img.load()
    lens, housing = [], []
    for y in range(EYE_BOX[1] - 4, EYE_BOX[3] + 5):
        for x in range(EYE_BOX[0] - 2, EYE_BOX[2] + 5):
            cx, cy = x + hx + OFFSET_X, y + hy
            c = px[cx, cy]
            if c[3] == 0:
                continue
            value = luma(tinted(c, tint))
            if in_oval(x, y, LENS_OVAL):
                lens.append(value)
            elif not in_oval(x, y, BEZEL_OVAL):
                housing.append(value)
    mean = sum(lens) / len(lens)
    hmean = sum(housing) / len(housing)
    return {"lensPx": len(lens), "lensMeanLuma": round(mean, 3), "lensPeakLuma": round(max(lens), 3),
            "lensBrightShare": round(sum(1 for v in lens if v >= 0.6) / len(lens), 3),
            "housingMeanLuma": round(hmean, 3), "lensMinusHousing": round(mean - hmean, 3)}


def check(frames: list, added: dict) -> dict:
    v2_strip = Image.open(V2_STRIP).convert("RGBA")
    assert hashlib.sha256(V2_STRIP.read_bytes()).hexdigest() == V2_STRIP_SHA256, "v2 strip changed"
    v2_cells = [v2_strip.crop((i * V2_W, 0, (i + 1) * V2_W, V2_H)) for i in range(21)]
    window = lambda img: img.crop((LEFT, 0, LEFT + V2_W, V2_H))
    palette = {rgb(k) for k in PALETTE}
    report, diffs = [], {}
    for i, img in enumerate(frames):
        state = FRAMES[i][0]
        a, b = window(img).load(), v2_cells[i].load()
        changed = [(x, y) for y in range(V2_H) for x in range(V2_W) if a[x, y] != b[x, y]]
        # Outside the v2 window (left margin and the 4 extra rows) only effect / shadow pixels may appear.
        outside = sum(1 for y in range(H) for x in range(W) if (x < LEFT or y >= V2_H) and img.getpixel((x, y))[3])
        if i == 12 or i == 13:
            head = FRAMES[i][1]["head"]
            for x, y in changed:
                sx, sy = x - v2.MARGIN - head[0], y - head[1]
                assert in_oval(sx, sy, INNER_OVAL) or (sx == 20 or sy == 22) and in_oval(sx, sy, BEZEL_OVAL), ("lens repaint left the bezel", i, sx, sy)
            # The repaint keeps every pixel opaque that was opaque (and vice versa): silhouette and outline unchanged.
            assert all((a[x, y][3] > 0) == (b[x, y][3] > 0) for x, y in changed)
            assert outside == 0
        elif i in added:
            assert all(b[x, y][3] == 0 for x, y in changed), ("effect repainted a v2 pixel", i)
        else:
            assert not changed and outside == 0, ("frame must equal v2", i, len(changed), outside)
        diffs[i] = len(changed) + outside
        bbox = img.getbbox()
        body_bottom = window(img).getbbox()[3] - 1 if i not in SHADOW else v2_cells[i].getbbox()[3] - 1
        assert body_bottom == ANCHOR_ROW, (i, body_bottom)
        if i not in SHADOW:
            assert bbox[3] - 1 == ANCHOR_ROW, (i, bbox)
        colours = {c[:3] for c in pixels(img) if c[3]}
        assert colours <= palette, (i, colours - palette)
        assert {c[3] for c in pixels(img)} <= {0, 255}
        report.append({"index": i, "state": state, "opaqueBBox": list(bbox), "colourCount": len(colours),
                       "opaquePixels": sum(1 for c in pixels(img) if c[3]), "pixelsDifferentFromV2": diffs[i],
                       "anchorRowRuns": v2.ground_runs(window(img))})
    # The v2 author's own checks (static pilot, v1 reuse, gait lock) still pass on the v2 strip, and v3 frames 0-11
    # equal those cells (asserted above), so the gait lock and zero-slip carry over unchanged.
    v2_report = v2.check(v2_cells)
    impact = frames[14]
    lead = impact.getbbox()[0] - RUNTIME_ANCHOR[0]
    assert lead == ARC_REACH, lead
    # Lens under the runtime wind-up tint, against v2's wind-up lens and the untinted idle lens.
    lens = {}
    for i in (12, 13):
        head = FRAMES[i][1]["head"]
        lens[f"v3_f{i}_tinted"] = lens_metrics(frames[i], head, WINDUP_TINT)
        lens[f"v2_f{i}_tinted"] = lens_metrics(place(v2_cells[i]), head, WINDUP_TINT)
    lens["idle_f0_untinted"] = lens_metrics(frames[0], (0, 0), (1.0, 1.0, 1.0))
    for i in (12, 13):
        assert lens[f"v3_f{i}_tinted"]["lensMeanLuma"] > lens[f"v2_f{i}_tinted"]["lensMeanLuma"]
        assert lens[f"v3_f{i}_tinted"]["lensMinusHousing"] > lens[f"v2_f{i}_tinted"]["lensMinusHousing"]
    assert lens["v3_f13_tinted"]["lensMeanLuma"] >= lens["idle_f0_untinted"]["lensMeanLuma"]
    shadow = {}
    for i in SHADOW:
        base = place(v2_cells[i]).load()
        rows = [y for y in range(H) for x in range(W) if frames[i].getpixel((x, y))[3] and not base[x, y][3]]
        shadow[i] = {"addedPx": added[i], "belowFloorRowPx": sum(1 for y in rows if y > ANCHOR_ROW), "halfWidth": SHADOW[i][0],
                     "halfHeight": SHADOW[i][1], "peakDensity": SHADOW[i][2]}
    return {"frames": report, "gaitLock": v2_report["gaitLock"], "arcLeadRelEnemyX": lead,
            "arcPx": {14: added[14], 15: added[15]}, "lens": lens, "shadow": shadow}


def strip_of(frames):
    strip = Image.new("RGBA", (W * len(frames), H), (0, 0, 0, 0))
    for i, f in enumerate(frames):
        strip.paste(f, (i * W, 0))
    return strip


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", type=Path, default=None)
    ap.add_argument("--final", type=Path, default=None)
    args = ap.parse_args()
    frames, added = render_all()
    report = check(frames, added)
    if args.out:
        args.out.mkdir(parents=True, exist_ok=True)
        strip_of(frames).save(args.out / "strip.png")
        for i, f in enumerate(frames):
            f.save(args.out / f"f{i:02d}.png")
        print(json.dumps({k: report[k] for k in ("arcLeadRelEnemyX", "arcPx", "lens", "shadow")}, indent=1))
        return
    out_dir: Path = args.final
    root = out_dir.resolve().parents[3]
    stamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    token = uuid.uuid4().hex[:8]
    tag = "m8-anim-v03"
    path = out_dir / f"{SLUG}_scifi-sentry-automaton_battle-animation-strip-left_{tag}_{stamp}-{token}.png"
    mpath = out_dir / f"{SLUG}_scifi-sentry-automaton_battle-animation-manifest_{tag}_{stamp}-{token}.json"
    # Short folder and file names: the full Windows path must stay under 260 characters.
    fdir = out_dir / f"frames_{tag}_{token}"
    for p in (path, mpath, fdir):
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
        "asset": "scifi sentry automaton battle animation candidate v3 (science-region ruins enemy)",
        "revision": tag,
        "basedOn": {"manifest": rel(V2_MANIFEST), "strip": rel(V2_STRIP), "stripSha256": V2_STRIP_SHA256,
                    "note": "v2 files are unchanged and v2 stays the battle_arena.gd runtime default; v3 is an isolated candidate"},
        "status": "animation_candidate_unapproved",
        "artAccepted": False,
        "artAcceptanceCount": 0,
        "humanReview": "pending - the creator approved the visual/animation direction and asked for occlusion and foot-slide fixes (v2); v2 and v3 both await Codex/human review; this is not animation acceptance",
        "runtimeWiring": "not wired: battle_arena.gd still points ENEMY_SPRITE_ANIMATIONS['sentry'] at v2. The test-only helper applies the entry below to single battle instances.",
        "runtimeEntry": {"cell": [W, H], "anchor": list(RUNTIME_ANCHOR), "body_center_x": BODY_CENTER_X,
                         "unchangedFromV2": ["states", "frame_time", "gait_step_px", "move_grace", "front_states"]},
        "file": rel(path),
        "sha256": sha(path),
        "sha256Algorithm": "sha256-bytes",
        "stripSize": list(strip.size),
        "cellSize": list(SIZE),
        "frameCount": len(frames),
        "v2CellOffsetInCell": [LEFT, 0],
        "staticPlateOffsetInCell": [OFFSET_X, 0],
        "runtimeAnchor": list(RUNTIME_ANCHOR),
        "bodyCenterX": BODY_CENTER_X,
        "runtimeAnchorNote": "draw the cell at (enemy_x - %d, 272 - %d): the same screen placement as v2 (cell x %d = v2 cell x %d). The ring and contact shadow centre on cell x %d (enemy_x + %d), as in v2." % (RUNTIME_ANCHOR[0], ANCHOR_ROW, RUNTIME_ANCHOR[0], v2.RUNTIME_ANCHOR[0], BODY_CENTER_X, BODY_CENTER_X - RUNTIME_ANCHOR[0]),
        "facing": "left (toward party)",
        "states": states,
        "changesFromV2": {
            "windupLens": "frames 12-13 repaint only the lens interior and a four-point flare inside the bezel (silhouette, outline and every other pixel unchanged)",
            "strikeArc": "frame 14 adds a cyan claw-arc whose leading edge reaches enemy_x %d; frame 15 adds its broken remnant. Only transparent pixels are filled; the v2 lunge pose is unchanged" % ARC_REACH,
            "defeatShadow": "frames 18-20 add an ordered-dither shadow in palette colour 'o' (%s) under the body, centred on the body centre and the floor line; it widens as the body settles. Only transparent pixels are filled" % PALETTE[SHADOW_KEY],
            "identicalToV2": [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 16, 17],
        },
        "rowRule": "row 60 is the last opaque body row of every frame; only the defeat shadow uses rows 61-64",
        "gaitLock": report["gaitLock"],
        "arcLeadRelEnemyX": report["arcLeadRelEnemyX"],
        "arcPixels": report["arcPx"],
        "lensUnderWindupTint": {"tint": list(WINDUP_TINT), "metric": "Rec.709 luma of sRGB values after the runtime multiply; housing = opaque eye-box pixels outside the bezel", **report["lens"]},
        "defeatShadow": report["shadow"],
        "frameReport": report["frames"],
        "frameFiles": [{"index": i, "state": FRAMES[i][0], "file": rel(p), "sha256": sha(p)} for i, p in enumerate(frame_files)],
        "palette": PALETTE,
        "alphaValues": [0, 255],
        "method": "The v2 author script is imported unchanged (rig, poses, palette, compositor). v3 swaps the wind-up lens paint (two new lens modes inside the bezel) and places the v2 cell 20 px from the left of a 132x66 cell, then fills transparent pixels with explicit claw-arc and shadow pixels. No image is read, traced, resampled, resized or generated by AI.",
        "authorScript": rel(script),
        "authorScriptSha256": sha(script),
        "v2AuthorScript": rel(V2_AUTHOR),
        "v2AuthorScriptSha256": sha(V2_AUTHOR),
        "previews": "none: no contact sheet, collage or GIF; review uses separate real 1280x720 Godot captures",
        "scope": "sentry enemy only; candidate asset, not referenced by battle_arena.gd",
        "createdAt": datetime.now().isoformat(timespec="seconds"),
    }
    mpath.write_text(json.dumps(manifest, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(path)
    print(mpath)
    print(fdir)
    print("sha256", manifest["sha256"], "strip", strip.size)
    print(json.dumps({k: report[k] for k in ("arcLeadRelEnemyX", "arcPx", "lens", "shadow")}, indent=1))


if __name__ == "__main__":
    main()
