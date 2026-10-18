"""Female protagonist - SOUTH RUN motion pilot v06 (m8-w09) - TEST-ONLY, single direction.

STATUS: UNAPPROVED / NONRUNTIME.  Nothing this script writes is a production sprite and nothing here is
runtime-integrated.  The creator approved only the selout v8 south idle STATIC frame and the 48-logical-px
exploration display scale; motion is NOT approved.  Claude reviewed the result as an agent; that is not a
human review.  Codex / the creator inspect the moving result before any acceptance.

v06 is a copy of the v05 builder
(tools/...south-run-v05-build_m8-w08_20261017-055617-998d6a83.py, not imported; every v05 file stays untouched).  ONE
bounded correction: Codex judged v05's 30 fps stops too sluggish (release -> v8 267-333 ms, last touchdown -> v8
167-200 ms) although its 60 fps stops improved.  The cause was a TICK-COUNTED settle: every body change after the
last touchdown took its own tick, so the same five changes cost 83 ms at 60 fps and 167-200 ms at 30 fps.  v06 keeps
the art, the gait and the v05 settle ORDER and makes the stop TIME-BASED (executed by the test-only GDScript
compositor; the rule and its constants are in the manifest's stop block):
  * every settle change (hair catch-up, torso re-centre, arm step, dip release, hair follow) gets a scheduled time in
    ms on an event clock: at least settle_gap_ms (one 60 fps tick) after the previous change, and the hair lag counts
    from the scheduled time of the body change it follows.  A frame shows every change whose time has passed, so at
    60 / 144 fps there is still at most one change per tick and at 30 fps two changes can share a tick;
  * touchdowns get event times too (start + duration, never before the previous frame), the shuffle of the second
    boot starts at that time, and the one-boot-change-per-tick hold shifts a held boot's clock by at most
    hold_shift_ms (v05: by a whole tick, 33 ms at 30 fps);
  * no boot skips a pose: a boot that would jump from its start pose straight to touchdown in one frame (a low frame
    rate) shows its mid key for that frame first.
The part library, keyframes, gait (stride 84 px, 6.67 steps/s at MOVE_SPEED 140, lift <= 2), compositor rules,
zero-slip planted boot, re-press rule and the <= 100 ms raised-boot limit are v05's, byte for byte in pixel content.

v05 is a copy of the v04 builder
(tools/...south-run-v04-build_m8-w07_20261017-015826-5b1e7d2a.py, not imported; every v04 file stays untouched).  The
creator viewed v04 in motion and asked for more polish of the run / stop; the creator standard
(docs/design/...character-motion_smooth-fluid-well-paced-creator-standard_v01_20261016-233420-702db4c9.md) asks for
smooth, fluid, well-paced motion.  Codex's v04 review asked for a shorter forward reach, a shorter airborne-looking
interval, and stops whose visible boot lands before the body settles.  v05 changes the GAIT and the STOP SETTLE only
(part library, compositor rules, identity rules and the zero-slip planted boot are v04's):
  * SHORTER STRIDE: one step is 42 px of body travel (v04 48), i.e. 6.67 steps/s at MOVE_SPEED 140 (v04 5.83); the
    boot lands V05_LAND = 2 rows below its v8 spot (v04 3), so the landing leg is one row shorter again;
  * LESS AIRBORNE LOOK: v04's swing boot spent most of its swing behind the body with lift 3, so in flight the lowest
    boot hung up to 6 rows above v8's ground (a hop).  v05's swing boot comes forward early and passes LOW (lift <= 2)
    near its v8 spot while the other boot is planted, then descends to land; the flight per step drops from 93 to 75 ms;
  * STOP SETTLE, ONE CHANGE PER TICK: after the last touchdown the torso re-centres first (while the body is dipped),
    then the dip releases, then the hair follows - v04 released the dip and the torso shift on the same tick;
  * the arms ease to N only while no boot is moving after a release would lengthen stops, so they keep v04's rule
    (one pose step per arm_step_ms on ticks where no boot changes its view).
Run speed (140 logical px/s), the single south direction, the part-library method, the zero-slip planted boot, the
contact-shadow overlay (test-only), the re-press rule and the <= 100 ms raised-boot limit after a release are kept.

(v04 header, kept.)  v04 is a copy of the v03 builder
(tools/...south-locomotion-compact-v03-build_m8-w06_20261017-012243-dd3b5479.py, not imported; every v03 file stays
untouched) with three TARGETED fixes from Codex's review of v03's 1x Godot stills, and nothing else:
  * FORWARD LANDING LEG shorter and articulated (v8 thigh rows 1:1, the shin takes the extra rows and slopes into the
    boot cuff, knee lean at touchdown);
  * HEAD / NECK ALIGNMENT: the head and hair lock move WITH the upper body (no neck shear);
  * SHORTER POST-CONTACT SETTLE (cape with the torso, hair one tick, 25 ms dip).

(v03 header, kept.)  v03 started as a copy of the v02 builder
(tools/...south-locomotion-compact-v02-build_m8-w05_20261016-200500-78e18209.py, not imported) and keeps v02's part
library method, zero-slip planted boot and re-press rule.  v03 answers Codex's v02 motion review
(docs/qa/...south-locomotion-compact-v02-codex-motion-review_unapproved-v01_20261016-191300-7a02d91c.md):
  * it is a deliberate RUN state (never called a walk): at MOVE_SPEED 140 a zero-slip contact can only last as long
    as the leg can absorb the travel, so a flight phase remains (see GAIT and the QA note for the numbers);
  * contact grows from 20 to 22 px with a heel-strike -> flat -> heel-up -> toe roll that keeps the lowest boot row
    pinned (strike +6 .. toe -16 instead of +8 .. -12), so the forward boot overhangs v8 by 6 rows, not 8;
  * low swing (lift <= 3 rows, was 8) with no kicked-up "sole" block;
  * the shoulders / torso / scarf / arms shift 1 texel with the stride (the head stays), arms use five poses;
  * hand-authored compact forward boots (strike / reach) replace v02's long blocky forward boot;
  * a separate per-foot contact-shadow part (single ink colour, binary alpha) drawn UNDER the sprite at a fixed
    opacity by the test-only capture, also under the v8 idle, so it never pops at the stop;
  * a shorter, lower stop (lift <= 2) with a torso weight shift toward the boot that carries the weight.

Why v02 (history, kept from the v02 header).  v01 (m8-w04) drew 8 whole frames at the logical position.  Its planted boot therefore slid with the body
in world space (4.64 window px per 60 fps tick, up to 121 px per ground contact), its reach->stop change was a
291-315 px silhouette jump, a quick re-press re-lifted the leg that had just landed, and two contact frames were
nearly v8.  A frame bank cannot fix the slide without a root lock, and a root lock forces sub-pixel-keyed stops
(v3r4: 187 stop frames).  v02 therefore changes the unit of art from "whole frame" to "part + rule":
  * a PART LIBRARY cut from v8 (cape / hair-lock lag variants, hips, coat skirt, upper body, arm poses, the
    v8 leg rows, and boot views) - separate PNGs + one layered .ora, all in the 80x120 cell with v8's pin;
  * GAIT KEYS (motion metadata in the manifest): stride, stance, landing / lift-off offsets, swing key table;
  * a small TEST-ONLY compositor (reference implementation here; the GDScript port lives in the Godot capture
    tool) that stacks the parts per tick.  The body is drawn at the logical position (no root lock, no body
    hop).  A boot in stance is drawn at a FIXED WINDOW ROW chosen when it lands, and its leg is re-stacked
    from v8's own leg rows between the hip and that boot (whole-row repeat / drop, as v01) - so the planted
    boot does not move in world space while the body passes over it.
The price is stated, not hidden: at MOVE_SPEED 140 a zero-slip contact can only last as long as the leg can
absorb the travel (20 window px here, ~71 ms), so the gait is a light run with a flight phase, not a walk.
Art method: texels are placed 1:1 in v8's palette (no generative redraw, resampling, filtering, flips or mirrors).
Helpers marked "copied" are copied verbatim from the v01 builder
(tools/...south-walk-compact-v01-build_m8-w04_20261016-184552-1c53af0d.py, itself copying v3r4), never imported.

Usage (repository root, Codex-runtime Python 3.12 + Pillow + NumPy, run with -I):
  python -I tools/<this> --out-dir <dir>      # build into a scratch dir (determinism check)
  python -I tools/<this> --write              # build into game/assets/characters/run-v06-unapproved/
  python -I tools/<this> --preview <dir>      # 4x nearest PNG per keyframe (scratch only; separate files, no sheet)
"""
import argparse, hashlib, io, json, math, os, sys, zipfile
import numpy as np
from PIL import Image

REPO = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
V8_REL = ("game/assets/characters/pixelorama-pilots/rpg-2-star-ocean-the-second_protagonist-female_"
          "south-idle-selout-v8-cloth-leather-candidate_m8-v08_20261015-021600-157a5ea0.png")
V8_SHA256 = "ccf9d2a293e7f1b9c706b4d2f1bf9c00b3c7714ec4e9b8bddf023e166f68b6fd"
OUT_REL = "game/assets/characters/run-v06-unapproved"
STAMP = "20261017-211600"
RUN_ID = "b5cda030"
VARIANT = "unapproved-nonruntime"
SLUG = "rpg-2-star-ocean-the-second"
PART = "south-run-v06"
W, H = 80, 120           # v8's 80x112 cell + 8 rows below for the forward (toward-camera) foot; same pin
V8_H = 112
PIN = (40, 104)          # cell ground pin shared with v8 and every earlier pilot
SPEED_PX_S = 140         # MOVE_SPEED, logical px/s (scifi_exploration_area.gd / survey_annex.gd), unchanged
HAIR_LOCK = (24, 31, 23)       # rows y0..y1, x <= x_max (v8 coordinates), as v3r3 / v3r4 / v01
CAPE_HEM_ROW = 64

# ============================================================================ copied verbatim from the v01 builder (lines 57-589)
# ============================================================================ copied verbatim from v3r4
ROLES = {"K": "#0a0a0e", "k": "#201c20", "O": "#23252b", "T": "#0a323b", "q": "#302526", "G": "#30333a",
         "b": "#41302b", "t": "#11525b", "n": "#533b32", "g": "#474b54", "m": "#634739", "L": "#714730",
         "u": "#1a767b", "l": "#845436", "w": "#7e5f4a", "z": "#626873", "v": "#249b98", "r": "#a16f4b",
         "D": "#bb7c50", "c": "#b09986", "s": "#e39664", "C": "#d7c0a8", "B": "#cfc8bd", "S": "#fbc38d",
         "W": "#faead4", "M": "#9a4634", "1": "#5e6e8c", "2": "#3a4560", "3": "#222839", "4": "#c07a40",
         "5": "#4a625c", "6": "#324542"}
RGB = {k: tuple(int(h[i:i + 2], 16) for i in (1, 3, 5)) for k, h in ROLES.items()}
INV = {v: k for k, v in RGB.items()}


def fid(role):
    return hashlib.sha256(f"{RUN_ID}:{role}".encode()).hexdigest()[:8]


# ============================================================================ v8 split
# Same ownership rules as w01/v2 (torso / right forearm / left fist / legs), then the torso is cut
# into the upper body (rows <= 57: head, chest, sleeves, belts), the coat skirt (rows >= 58) and the
# cape (teal run at the far left of rows >= 57).
def owner(x, y, ch):
    if y <= 60:
        if 47 <= y <= 53 and 18 <= x <= {47: 24, 52: 24, 53: 24}.get(y, 25):
            return "fist"
        if 53 <= y <= 56 and 46 <= x <= 53 and not (y == 53 and x >= 52):
            return "armr"
        if 57 <= y <= 60 and x >= 47:
            return "armr"
        return "torso"
    hand_left = {61: 47, 62: 47, 63: 47, 64: 47, 65: 47, 66: 47, 67: 47, 68: 48, 69: 49, 70: 50}
    if y in hand_left and x >= hand_left[y]:
        return "armr"
    coat_left = {61: 29, 62: 28, 63: 27}.get(y, 26 if y <= 70 else (25 if y <= 74 else -1))
    if x <= coat_left:
        return "torso"
    if y in (61, 62) and ch in "cC" and 30 <= x <= 40:
        return "torso"
    flap = {61: (43, 46), 62: (43, 46), 63: (43, 46), 64: (43, 46), 65: (43, 46), 66: (44, 46), 67: (44, 46),
            68: (44, 46), 69: (45, 47), 70: (45, 47), 71: (45, 48), 72: (45, 48), 73: (47, 48), 74: (47, 51),
            75: (48, 50)}
    if y in flap and flap[y][0] <= x <= flap[y][1]:
        return "torso"
    if y <= 70:
        return "legvl" if x <= 35 else "legvr"
    return "legvl" if x <= 36 else "legvr"


def split_v8(v8):
    P = {"torso": {}, "fist": {}, "armr": {}, "legvl": {}, "legvr": {}}
    for (x, y), ch in v8.items():
        P[owner(x, y, ch)][(x, y)] = ch
    P["armr"][(50, 52)] = P["torso"].pop((50, 52))
    torso = P.pop("torso")
    cape = {}
    for y in range(57, 76):
        xs = sorted(x for (x, yy) in torso if yy == y)
        seen_teal = False
        for x in xs:
            ch = torso[(x, y)]
            if ch in "utTv":
                seen_teal = True
            elif ch in "Kk" and (seen_teal or torso.get((x + 1, y), ".") in "utTv"):
                pass
            else:
                break
            cape[(x, y)] = ch
    P["cape"] = cape
    P["upper"] = {p: c for p, c in torso.items() if p[1] <= 57 and p not in cape}
    P["skirt"] = {p: c for p, c in torso.items() if p[1] >= 58 and p not in cape}
    return P


# ============================================================================ helpers
def sha256_file(path):
    with open(_fs(path), "rb") as f:
        return hashlib.sha256(f.read()).hexdigest()


def load_grid(path):
    a = np.array(Image.open(path).convert("RGBA"))
    return {(x, y): INV[tuple(int(c) for c in a[y, x, :3])] for y in range(H) for x in range(W) if a[y, x, 3]}


def v8_path_checked():
    """Source hash gate, run first by every mode (build, check, preview)."""
    path = os.path.join(REPO, V8_REL)
    if not os.path.isfile(path):
        raise SystemExit(f"v8 source missing: {V8_REL}; refusing to run")
    got = sha256_file(path)
    if got != V8_SHA256:
        raise SystemExit(f"v8 source SHA-256 mismatch ({got} != {V8_SHA256}); refusing to run")
    return path


def shift(d, dx, dy):
    return {(x + dx, y + dy): c for (x, y), c in d.items()}


def art(rows, x0, y0):
    return {(x0 + i, y0 + j): ch for j, row in enumerate(rows) for i, ch in enumerate(row) if ch not in ". "}


def rnd(v):
    return int(math.floor(v + 0.5))

# ============================================================================ legs
# Knee guard (viewer-left knee only, as v8): strap with a cream buckle above an ink-edged plate with
# a teal gem.  Anchor (0, 0) = knee centre.  "front" is v8's own plate (rows 71-79); "raised" (knee
# driven toward the camera) is one row taller and wider; "back" (knee behind the hip) is foreshortened.
GUARD = {
    "front": (-4, -6, [
        "....cB...",
        "..LLcKLL.",
        "....cc...",
        ".OOOOO...",
        "OGzzgGO..",
        "OGgvvGO..",
        "OGgvgBO..",
        "OGggGBO..",
        ".OGGGO..."]),
    "raised": (-4, -6, [
        "....cB...",
        "..LLcKLL.",
        ".OOOOOO..",
        "OGzzzgGO.",
        "OGgvvgGO.",
        "OGgvvgBO.",
        "OGggggBO.",
        "OGGgGGBO.",
        ".OOGGGO..",
        "..OOOO..."]),
    "back": (-4, -4, [
        "..LLcBLL.",
        ".OOOOO...",
        "OGzzgGO..",
        "OGgvgBO..",
        ".OGGGO..."]),
}

# Boots = v8 boot-shaft rows (exact v8 texel strings, cuff first: vl rows 85-92, vr rows 85-93) + a foot
# drawn per view in v8 leather / lace colours.  Offsets are the x of each row's first texel relative to
# the cuff's left edge.  v8's vr shaft leans 2 texels right; the run keeps every row's texels but sets
# them on the leg axis (a shift, no redraw).  Angled / lifted boots drop plain shaft rows.
SHAFT = {
    "vl": [(0, "qLLLLbq"), (0, "qLnLnbK"), (1, "kqbbk"), (1, "qbbbk"), (1, "qbbbk"),
           (0, "KsCbqLK"), (0, "KBBCLbK"), (0, "KCCqnqK")],
    "vr": [(0, "KbbnbLbK"), (0, "qqLLLLbK"), (0, "KqnnLLbK"), (1, "KnnLbqK"), (1, "kbbbqK"),
           (1, "KqbCCqK"), (1, "KbCbqLK"), (1, "KbBBCKK")],
}
SHAFT_KEEP = {"full": None, "short": (0, 1, 2, 3, 5, 6, 7)}
# Feet toward the camera, lit from the upper left like v8 (L/l lit, b/q shade, r specular, q tread).
# The stance views (strike, flat, heelup, toe) of one leg put the centre of their lowest row within
# 0.5 texel of each other relative to the cuff, so a planted toe cannot slide sideways when the view
# changes (vl: 1 texel out to the viewer-left, vr: 0.5-1 texel out to the viewer-right, as v8's splay).
FOOT = {
    "vl": {
        # v8 vl foot (rows 93-100), turned from its idle splay toward the camera
        "flat": ("full", [(-1, "KqnnbbbK"), (-1, "KnLLLbbqK"), (-2, "KnllLLLqbK"), (-2, "KqllrLLqbK"),
                          (-2, "KqLllLLbqK"), (-1, "KqbbbbqK"), (-1, "KqqqqqqK"), (0, "KKKKK")]),
        "strike": ("short", [(-1, "KqnnbbbK"), (-2, "KnLLLbbqK"), (-2, "KllrLLqbK"), (-2, "KqllLLbqK"),
                             (-2, "KqbqbqbqK"), (-1, "KKKKKKK")]),
        "heelup": ("full", [(-1, "KqnnbbbK"), (-1, "KnLLLbqK"), (-1, "KllLLqbK"), (-1, "KlrLLqK"),
                            (0, "KqLbqK"), (0, "KKKK")]),
        "toe": ("short", [(0, "KqnnbbK"), (0, "KlLLbqK"), (0, "KlrLqK"), (1, "KqbqK"), (1, "KKK")]),
        "hang": ("short", [(0, "KqnnbbK"), (0, "KlLLLbK"), (1, "KlrLqK"), (1, "KqLbK"), (2, "KK")]),
        "reach": ("full", [(-1, "KqnnbbbK"), (-2, "KnLLLbbqK"), (-2, "KllrLLqbK"), (-2, "KqLllLbqK"),
                           (-1, "KqqqqqK"), (0, "KKKKK")]),
    },
    "vr": {
        # v8 vr foot (rows 94-103), its last rows pulled 1-2 texels back under the shaft
        "flat": ("full", [(1, "KqCbbK"), (1, "KbLLLq"), (1, "KbLnnqK"), (1, "kqLLLLq"), (1, "kbLllLLK"),
                          (1, "KqbllLLbK"), (1, "KqnLrnbK"), (1, "KbbqqqbK"), (2, "qqqqqqK"), (2, "KKKKK")]),
        "strike": ("short", [(1, "KqCbbK"), (0, "KqbLLLqK"), (0, "KbLllLLK"), (0, "KqbLrnbqK"),
                             (0, "KqbqbqbqK"), (1, "KKKKKKK")]),
        "heelup": ("full", [(1, "KqCbbK"), (1, "KbLLLqK"), (1, "KbLlnqK"), (2, "KqLrLbK"), (3, "KqbqK"),
                            (3, "KKKK")]),
        "toe": ("short", [(1, "KqCbbK"), (1, "KbLLqK"), (2, "KqLrbK"), (3, "KqbK"), (3, "KKK")]),
        "hang": ("short", [(1, "KqCbbK"), (1, "KbLLLqK"), (1, "KqLrLbK"), (2, "KqbqK"), (2, "KKK")]),
        "reach": ("full", [(1, "KqCbbK"), (0, "KqbLLLqK"), (0, "KbLllLLqK"), (0, "KqbLrnbqK"),
                           (1, "KbbqqqbK"), (1, "KKKKKK")]),
    },
}
# Sole-on boot for a foot kicked up behind the knee: boot back, lit heel counter, heel seam, tread.
# Drawn just under the knee (the 16-bit front-run convention), so the kicked leg keeps a visible foot.
SOLE_VIEW = {
    "vl": [(0, "KqLLLbK"), (0, "KbLLbqK"), (-1, "KnlllnqK"), (-1, "KqbbbbqK"), (-1, "KKKKKKKK"),
           (-1, "KqbqbqbK"), (-1, "KbqbqbqK"), (0, "KqqqqK"), (1, "KKKK")],
    "vr": [(0, "KqLLLbK"), (0, "KbLLLqK"), (-1, "KnllLnqK"), (-1, "KqbbbbqK"), (-1, "KKKKKKKK"),
           (-1, "KqbqbqbK"), (-1, "KbqbqbqK"), (0, "KqqqqK"), (1, "KKKK")],
}


def boot_rows(side, view):
    if view == "sole":
        return SOLE_VIEW[side]
    keep, foot = FOOT[side][view]
    idx = SHAFT_KEEP[keep]
    return [r for i, r in enumerate(SHAFT[side]) if idx is None or i in idx] + foot


def boot_texels(side, view, cuff_x, sole):
    """Boot with its cuff centred on cuff_x and its lowest row on `sole`; returns (texels, top row)."""
    rows = boot_rows(side, view)
    o, top = rows[0]
    x0 = rnd(cuff_x - (o + (len(top) - 1) / 2))
    y0 = sole - len(rows) + 1
    tex = {}
    for j, (o, r) in enumerate(rows):
        for i, ch in enumerate(r):
            if ch not in ". ":
                tex[(x0 + o + i, y0 + j)] = ch
    return tex, y0


def limb_mask(joints):
    """joints: [(x, y, half_width), ...] top to bottom -> union of tapered capsules (texel centres)."""
    m = set()
    for (x0, y0, r0), (x1, y1, r1) in zip(joints, joints[1:]):
        R = max(r0, r1)
        dx, dy = x1 - x0, y1 - y0
        L2 = dx * dx + dy * dy
        for y in range(int(math.floor(min(y0, y1) - R)), int(math.ceil(max(y0, y1) + R)) + 1):
            for x in range(int(math.floor(min(x0, x1) - R)) - 1, int(math.ceil(max(x0, x1) + R)) + 2):
                t = 0.0 if L2 == 0 else max(0.0, min(1.0, ((x - x0) * dx + (y - y0) * dy) / L2))
                px, py = x0 + dx * t, y0 + dy * t
                r = r0 + (r1 - r0) * t
                if (x - px) ** 2 + (y - py) ** 2 <= r * r:
                    m.add((x, y))
    return m


# Lit-band drift per row: v8's trouser folds move the light 1 texel every few rows instead of running
# a straight stripe down the leg.
FOLD = (0, 0, 1, 1, 1, 0, 0, -1, -1, 0, 1, 1, 0, 0, 0, -1)


def shade_trouser(mask, y_min, ky, seed):
    """v8 trouser ramp per row run: K | 6 rim | 5 lit | 6 base | 3 shadow | K.  The lit band narrows at
    the knee and drifts with FOLD; texels with nothing below get an ink bottom edge."""
    out, rows = {}, {}
    for (x, y) in mask:
        if y >= y_min:
            rows.setdefault(y, []).append(x)
    for y, xs in rows.items():
        xs.sort()
        a, w = xs[0], xs[-1] - xs[0] + 1
        d = abs(y - ky)
        lit_to = 0.3 if d <= 1 else (0.42 if d <= 3 else 0.52)
        fd = FOLD[(y + seed) % len(FOLD)]
        for x in xs:
            i = x - a
            if i == 0 or i == w - 1:
                ch = "K"
            elif i == 1:
                ch = "6"
            elif (i - fd) / max(w - 1, 1) < lit_to:
                ch = "5"
            elif i / max(w - 1, 1) < 0.72:
                ch = "6"
            else:
                ch = "3"
            out[(x, y)] = ch
    for (x, y) in list(out):
        if (x, y + 1) not in mask and out[(x, y)] != "K":
            out[(x, y)] = "K"
    return out

def stack(layers):
    g = {}
    for name in LAYER_ORDER:
        g.update(layers.get(name, {}))
    return g


def to_rgba(grid):
    a = np.zeros((H, W, 4), np.uint8)
    for (x, y), c in grid.items():
        if not (0 <= x < W and 0 <= y < H):
            raise SystemExit(f"texel outside cell: {(x, y)}")
        a[y, x, :3] = RGB[c]
        a[y, x, 3] = 255
    return a


def png_bytes(a):
    buf = io.BytesIO()
    Image.fromarray(a, "RGBA").save(buf, format="PNG")
    return buf.getvalue()

def _inside(path, root):
    path, root = os.path.normcase(os.path.realpath(path)), os.path.normcase(os.path.realpath(root))
    return path == root or path.startswith(root + os.sep)


# Windows: MAX_PATH is 260 including the file name, and these AGENTS names are ~130 characters, so a
# scratch dir under %TEMP% or a deep checkout overflows it (LongPathsEnabled is 0 on the dev machine).
# _fs() hands the OS the extended-length form of an absolute path only when it is needed.
WIN_MAX_PATH = 259
WIN_LONG_PREFIX = "\\\\?\\"         # the four characters  \\?\


def _fs(path):
    path = os.path.abspath(path)
    if os.name == "nt" and len(path) > WIN_MAX_PATH - 12 and not path.startswith(WIN_LONG_PREFIX):
        if path.startswith("\\\\"):                       # \\server\share\... -> \\?\UNC\server\share\...
            return WIN_LONG_PREFIX + "UNC\\" + path[2:]
        return WIN_LONG_PREFIX + path
    return path


def _out_dir(arg):
    """Resolve a --out-dir / --preview / --check argument against the current directory, and say so."""
    path = os.path.abspath(arg)
    if path != arg:
        print("DIR", path, "(resolved from", repr(arg) + ")", file=sys.stderr)
    return path

def make_pxo(per_frame_layers, durations, preview_png, fname, fps, order=None, dt=(2026, 10, 15, 3, 43, 26),
             opacity=None):
    order = order or LAYER_ORDER     # v3r3 passes its own layer order and zip time
    opacity = opacity or {}          # v03: per-layer opacity (the contact-shadow layer)
    layer_json = [{"animated_params": "Dictionary[String, Dictionary]({\n\"opacity\": {}\n})", "blend_mode": 0,
                   "clipping_mask": False, "effects": [], "locked": False, "metadata": {}, "name": n,
                   "new_cels_linked": False, "opacity": opacity.get(n, 1.0), "parent": -1, "type": 0,
                   "ui_color": "(0.0, 0.0, 0.0, 0.0)", "visible": True} for n in order]
    frames_json = [{"cels": [{"metadata": {}, "opacity": 1.0, "ui_color": "(0.0, 0.0, 0.0, 0.0)", "z_index": 0}
                             for _ in order], "duration": d, "metadata": {}} for d in durations]
    export_profile = {"crop_mode": "0", "current_tab": "0", "direction": "0", "directory_path": "\"\"",
                      "erase_unselected_area": "false", "export_json": "false", "export_layers": "0",
                      "file_format": "0", "file_name": json.dumps(fname), "frame_current_tag": "0",
                      "include_tag_in_filename": "false", "interpolation": "0", "lines_count": "1",
                      "new_dir_for_each_frame_tag": "false", "number_of_digits": "4", "number_of_frames": "1",
                      "orientation": "0", "repeat_count": "0", "resize": "100", "save_quality": "0.75",
                      "separator_character": "\"_\"", "sheet_layers_as_separate_files": "false",
                      "split_layers": "false"}
    data = {"author_company": "", "author_contact": "", "author_display_name": "", "author_real_name": "",
            "brushes": [], "color_mode": 5, "current_frame": 0, "current_layer": 4, "export_profile": export_profile,
            "fps": fps, "frames": frames_json, "guides": [], "layers": layer_json, "license": "", "metadata": {},
            "next_keyframe_id": 0, "palettes": [], "pixelorama_version": "v1.2.3-stable",
            "project_current_palette_name": "", "pxo_version": 7, "reference_images": [], "size_x": W, "size_y": H,
            "symmetry_points": [W - 1.0, H - 1.0], "tags": [], "tile_mode_x_basis_x": W, "tile_mode_x_basis_y": 0,
            "tile_mode_y_basis_x": 0, "tile_mode_y_basis_y": H, "tilesets": [], "user_data": "",
            "vanishing_points": []}
    buf = io.BytesIO()
    # dt: fixed zip time (zip needs even seconds) -> byte-identical rebuilds
    with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as z:
        def put(name, payload):
            z.writestr(zipfile.ZipInfo(name, dt), payload, zipfile.ZIP_DEFLATED)
        put("data.json", json.dumps(data, separators=(",", ":")))
        put("mimetype", "application/x-pixelorama")
        put("preview.png", preview_png)
        for fi, layers in enumerate(per_frame_layers, start=1):
            put(f"image_data/frames/{fi}/", b"")
            for li, name in enumerate(order, start=1):
                put(f"image_data/frames/{fi}/layer_{li}", to_rgba(layers[name]).tobytes())
                put(f"image_data/frames/{fi}/indices_layer_{li}", b"\x00")
    return buf.getvalue()



REPO_PATH_LIMIT = 250        # v03: every asset path inside this checkout stays under MAX_PATH (259) with margin


def _write(out_dir, name, data):
    path = os.path.join(out_dir, name)
    in_repo = os.path.join(REPO, OUT_REL, name)
    if len(os.path.abspath(in_repo)) > REPO_PATH_LIMIT:
        raise SystemExit(f"asset path would be {len(os.path.abspath(in_repo))} characters (> {REPO_PATH_LIMIT}): {name}")
    if os.path.exists(_fs(path)):
        with open(_fs(path), "rb") as f:
            if f.read() != data:
                raise SystemExit(f"refusing to overwrite different bytes: {path}")
    else:
        with open(_fs(path), "wb") as f:
            f.write(data)
    return path

def lag(part, root_row, dx, dy):
    """Rigid (dx, dy) move of a hanging part.  dy > 0 opens a gap under its attachment row; the gap is
    filled by repeating that row (moved by dx).  dy < 0 tucks the attachment row under the part above."""
    out = {}
    for k in range(max(dy, 0)):
        for (x, y), c in part.items():
            if y == root_row:
                out[(x + dx, y + k)] = c
    out.update(shift(part, dx, dy))
    return out


def flare(hem, dx):
    """Shear the hem outward (dx <= 0) growing toward its tip: row y moves by round(dx * (y - 63) / 12).
    Each row keeps its inner (right) ink run where it was, moves the rest, and closes the gap by repeating
    the last moved texel (texel repeat), so the cape stretches instead of tearing off the coat."""
    if dx == 0:
        return dict(hem)
    rows = {}
    for (x, y), c in hem.items():
        rows.setdefault(y, {})[x] = c
    out = {}
    for y, row in rows.items():
        s = rnd(dx * (y - CAPE_HEM_ROW + 1) / 12)
        xs = sorted(row)
        k = len(xs)
        while k > 1 and row[xs[k - 1]] in "Kk":      # trailing ink run stays put
            k -= 1
        body, ink = xs[:k], xs[k:]
        for x in body:
            out[(x + s, y)] = row[x]
        for x in range(body[-1] + s + 1, body[-1] + 1):
            out[(x, y)] = row[body[-1]]
        for x in ink:
            out[(x, y)] = row[x]
    return out


def cape_layer(top, hem, dx, dy):
    layer = lag(flare(hem, dx), CAPE_HEM_ROW, 0, dy)
    layer.update(top)                # the attachment wins where a raised hem overlaps it
    return layer

BELL_ZONE = (42, 46, 18, 24)            # v8 rows y0..y1, x0..x1 of her right sleeve's bell cuff
L_SEGMENTS = (("cuff", 52, 56), ("wrist", 57, 60), ("bracer", 61, 65), ("fingers", 66, 70))
ARM_HOME_BOX = {"R": (18, 42, 24, 53), "L": (46, 52, 53, 70)}           # v8 x0, y0, x1, y1 (inclusive)
# Knuckles toward the camera, lit from the upper left like v8 (S lit skin, s skin, D shade).
FRONT_FIST = {
    "L": [".KKKK.",
          "KSSssK",
          "KSsDsK",
          "KsDsDK",
          "KLrlLK",
          ".KKKK."],
}
# Poses, back to front.  Item = (segment, kept row indices or None = all, top row, x offset or per-row list
# [, "behind"]).  "behind" texels go to the arm's back layer, under the coat and upper body, so a hand swung
# back is partly hidden by the hip.  ("art", name, x0, y0) places an authored block.  Rows are v8 rows;
# sway / bob are added by the caller.
ARM_POSES = {
    "R": {
        "B2": [("fist", [0, 1, 2, 3, 4, 6], 46, 2, "behind"), ("bell", [0, 1, 2, 4], 42, 0)],
        "B1": [("fist", None, 46, 1, "behind"), ("bell", [0, 1, 2, 3, 4], 42, 0)],
        "N": [("bell", None, 42, 0), ("fist", None, 47, 0)],
        "F1": [("bell", [0, 1, 2, 4], 42, 1), ("fist", None, 44, 2)],
        "F2": [("bell", [0, 2, 4], 42, 1), ("fist", [0, 1, 2, 3, 4, 5], 41, 3)],
    },
    "L": {
        "B2": [("cuff", [0, 1, 2, 4], 51, 0), ("wrist", [0, 3], 55, -1, "behind"), ("bracer", [0, 2, 4], 57, -2, "behind"),
               ("fingers", None, 60, -2, "behind")],
        "B1": [("cuff", None, 52, 0), ("wrist", [0, 2, 3], 57, 0), ("bracer", [0, 1, 3, 4], 60, -1, "behind"),
               ("fingers", None, 64, -1, "behind")],
        "N": [("cuff", None, 52, 0), ("wrist", None, 57, 0), ("bracer", None, 61, 0), ("fingers", None, 66, 0)],
        "F1": [("cuff", [0, 1, 2, 4], 51, -1), ("wrist", [0], 55, -2), ("bracer", [0, 2, 4], 56, -2),
               ("fingers", None, 59, -2)],
        "F2": [("cuff", [0, 1, 2, 4], 51, -1), ("art", "L", 44, 45)],
    },
}
POSE_ORDER = ["B2", "B1", "N", "F1", "F2"]


def arm_pose_name(f):
    """Forwardness f in [-1, 1] -> pose key (thresholds 0.3 / 0.8)."""
    if f >= 0.8:
        return "F2"
    if f >= 0.3:
        return "F1"
    if f > -0.3:
        return "N"
    if f > -0.8:
        return "B1"
    return "B2"


def split_arms(P, upper):
    """Arm segments from v8 (R: bell cuff from the upper body + fist part; L: armr cut by rows)."""
    y0, y1, x0, x1 = BELL_ZONE
    bell = {p: c for p, c in upper.items() if y0 <= p[1] <= y1 and x0 <= p[0] <= x1}
    seg = {"R": {"bell": bell, "fist": dict(P["fist"])}, "L": {}}
    for name, a, b in L_SEGMENTS:
        seg["L"][name] = {p: c for p, c in P["armr"].items() if a <= p[1] <= b}
    return seg, {p: c for p, c in upper.items() if p not in bell}


def restack(part, keep, top, dx):
    rows = sorted({y for (_, y) in part})
    kept = rows if keep is None else [rows[i] for i in keep]
    out = {}
    for j, y in enumerate(kept):
        ox = dx[j] if isinstance(dx, (list, tuple)) else dx
        for (x, yy), c in part.items():
            if yy == y:
                out[(x + ox, top + j)] = c
    return out


def arm_texels(seg, side, pose):
    """-> (front texels, behind texels) in v8 coordinates."""
    front, back = {}, {}
    for item in ARM_POSES[side][pose]:
        if item[0] == "art":
            front.update(art(FRONT_FIST[item[1]], item[2], item[3]))
            continue
        name, keep, top, dx = item[:4]
        tex = restack(seg[side][name], keep, top, dx)
        if item[4:] == ("behind",):
            back.update(tex)
        else:
            front.update(tex)
    return front, back


def arm_layers(seg, poses, sway, bob, body):
    out = {}
    for side, layer in (("R", "arm-vl"), ("L", "arm-vr")):
        front, back = arm_texels(seg, side, poses[side])
        moved, behind = shift(front, sway, bob), shift(back, sway, bob)
        home = shift({p: c for part in seg[side].values() for p, c in part.items()}, sway, bob)
        seam = {}
        for (x, y) in home:
            if (x, y) in moved or (x, y) in behind or (x, y) in body:
                continue
            nb = [q for q in ((x - 1, y), (x + 1, y), (x, y - 1), (x, y + 1)) if q in body and q not in home]
            if nb and not any(body[q] in "Kk" for q in nb) and not any(moved.get(q) in ("K", "k") for q in nb):
                seam[(x, y)] = "K"
        out[layer], out[layer + "-back"], out[layer + "-seam"] = moved, behind, seam
    return out


def pinhole_fill(layers, y0):
    """Single transparent texels closed left, right and above below the belt that touch a redrawn leg /
    hips texel -> ink (as v3r2)."""
    g = stack(layers)
    legs = set(layers["hips"]) | set(layers["leg-far"]) | set(layers["leg-near"])
    fill = {}
    for y in range(y0, H):
        for x in range(1, W - 1):
            nb = ((x - 1, y), (x + 1, y), (x, y - 1))
            if (x, y) not in g and all(q in g for q in nb) and any(q in legs for q in nb):
                fill[(x, y)] = "K"
    return fill





# ============================================================================ v03: rig constants
# v8 leg anatomy (v8 rows), unchanged from v02.  Thigh = 61 .. knee top - 1; knee band (vl: strap, buckle and guard plate;
# vr: knee cap and crease); shin = knee bottom + 1 .. 84; boot = 85 .. ground row.
GROUND = {"vl": 100, "vr": 103}         # v8's own lowest boot rows (offset 0 = v8's spot)
KNEE_BAND = {"vl": (71, 79), "vr": (76, 80)}
HIP_ROW = 61
BOOT_TOP = 85
KNEE_MIN_ROWS = 5                       # the knee band is only squeezed in rare extreme states (counted in the manifest)
CUFF_X = {"vl": 31.0, "vr": 46.5}       # v8 cuff centres (boot_texels aligns the shaft's first row on them)
INWARD = {"vl": 1, "vr": -1}            # +1 texel toward the body's centre line
# v03 boot views.  The four STANCE views keep their lowest row on the ground row, so a planted boot rolls
# strike -> v8 -> heelup -> toe without leaving its pinned window row.  Swing uses toe / hang / reach / strike with
# lift >= 1.  v02's kicked-up "sole" block is not used.
BOOT_VIEWS = ["v8", "strike", "heelup", "toe", "hang", "reach"]
STANCE_VIEWS = ("strike", "v8", "heelup", "toe")
BOOT_ALIGN = {"toe": (1.0, 0), "heelup": (1.0, 0), "hang": (0.5, 1), "reach": (1.0, 0), "strike": (1.0, 0)}
# Hand-authored v03 forward boots (compact toe cap toward the camera, no tread block), v8 leather / lace colours only.
# toe / heelup / hang keep the v01 / v02 rows (FOOT above).
FOOT_V03 = {
    "vl": {
        "strike": ("short", [(-1, "KqnnbbbK"), (-1, "KnLLLbbqK"), (-1, "KllrLLqbK"), (-1, "KqbbbbbqK"), (0, "KKKKKKK")]),
        "reach": ("short", [(-1, "KqnnbbbK"), (-1, "KnLLLbbqK"), (-1, "KlrLLLqbK"), (0, "KqbbbqK"), (1, "KKKKK")]),
    },
    "vr": {
        "strike": ("short", [(1, "KqCbbK"), (0, "KqbLLLqK"), (0, "KbLllLLK"), (0, "KqbLrnbqK"), (0, "KbbqqqbK"),
                             (1, "KKKKKK")]),
        "reach": ("short", [(1, "KqCbbK"), (0, "KqbLLLqK"), (0, "KbLlrLLK"), (1, "KqbqqbK"), (2, "KKKK")]),
    },
}
# v04: the forward views (strike, reach) keep v8's WHOLE boot shaft (8 rows), so a landing leg no longer makes up the
# missing boot rows with repeated trouser rows (v03 used the short 7-row shaft).
V04_FULL_SHAFT_VIEWS = ("strike", "reach")
ARM_SET = ["B2", "B1", "N", "F1", "F2"]
HDY = (-1, 0, 1)
HTAG = {-1: "m1", 0: "0", 1: "p1"}     # part-name tag of a hair / cape lag dy
STAG = {-1: "m1", 0: "0", 1: "p1"}     # part-name tag of a torso / cape lateral shift
SHADOW_LIFTS = (0, 1, 2, 3)
SHADOW_OPACITY = 0.38                   # drawn by the test-only capture under the sprite (single ink colour, binary mask)
# v04: the head and hair lock follow the torso's lateral shift too (v03: head steady -> 1-texel neck shear); only the
# hips / legs (and the cape, which follows late) do not.
TORSO_SX_PARTS = ("head", "hair-lock", "torso", "arms", "coat-skirt")
LAYER_ORDER = ["cape", "arm-vl-back", "arm-vr-back", "hips", "leg-far", "leg-near", "coat-skirt", "torso", "head",
               "hair-lock", "arm-vl", "arm-vr"]
PXO_LAYERS = ["shadow"] + LAYER_ORDER   # the editable .pxo adds the contact shadow as its bottom layer (layer opacity)


def head_texel(x, y):
    """v8 head (hair, face, chin, neck skin).  v03 kept it steady while the torso shifted; v04 shifts it WITH the torso
    (same (sx, bob)), so the part split only matters for the layer order."""
    if y <= 28:
        return True
    if y <= 33:
        return x <= 40
    if y == 34:
        return 32 <= x <= 37
    if y == 35:
        return 34 <= x <= 35
    return False


# Gait keys (units: window px = texels at the 0.5 display scale; MOVE_SPEED 140 logical px/s = 280 window px/s).
# Distance-driven: the phase is the body's travelled window px modulo the stride, so 30 / 60 / 144 fps share it.
# Foot offsets "o" are rows relative to that foot's v8 spot (+ = toward the camera = lower on screen); "lift" raises
# the sole.  Sole row in the cell = GROUND + o - lift.  v05: a stance boot lands at o = +V05_LAND (v04: +3) and is
# drawn at a fixed window row until o = V05_LAND - V05_STANCE (v04: 3 - 22 = -19, the same rear limit); its view rolls
# by q = px since landing, its lowest row never moves.
V04_LAND = 3                     # kept for the v04 reference numbers below
V05_LAND = 2
V05_STANCE = 21
GAIT = {
    "stride_px": 84,                 # v05: one full cycle (two steps of 42 px) = 6.67 steps/s at 140 (v02-v04: 96, 5.83)
    "stance_px": V05_STANCE,         # zero-slip contact length = land_offset - liftoff_offset (v04 22)
    "land_offset": V05_LAND,         # v04: 3, v03: 6, v02: 8 (forward overhang below v8's ground row)
    "liftoff_offset": V05_LAND - V05_STANCE,   # -19 (v04 -19: the rear limit the leg rig can draw is unchanged)
    "phase_offset_px": {"vl": 0, "vr": 42},
    # q -> view from this q on; v8 exactly at q = land_offset (the v8 spot), heel-up / toe at v04's offsets
    "stance_roll": [[0, "strike"], [V05_LAND, "v8"], [V05_LAND + 11, "heelup"], [V05_LAND + 16, "toe"]],
    # knee lean inward by q since landing: 1 texel at touchdown, 0 from q = land_offset on (the boot at its v8 spot must
    # draw v8 exactly, so a stop never pops).  v04: 2 / 1 / 0 (Codex flagged a possible knock-kneed read at 2)
    "stance_knee_kin": [[0, 1], [V05_LAND, 0]],
    "bob_stance_q": [2, 14],         # body 1 row lower while a planted boot's q is in [2, 14) (mid-stance compression)
    "torso_shift_stance_q": [3, 17], # torso (with head, arms) 1 texel toward a planted boot while its q is in [3, 17)
    "arm_peak_px": {"L": 9, "R": 56},   # contralateral; R peaks 47 px after L (v04 10 / 64 on a 96 px cycle)
    "arm_pose_bands_px": [7, 16, 26, 35],   # distance from the forward peak: F2 | F1 | N | B1 | B2 (v04 x 84 / 96)
    "hair_lag_px": 9,                # hair / cape follow the bob 9 px (~32 ms at 140) late
    "cape_shift_lag_px": 9,          # the cape follows the torso shift 9 px late
    # swing key table: (u per mille of the 63 px swing, o, lift, boot view from this key on, knee lean inward).
    # v05: lift <= 2 (v04 3).  The boot clears the floor in the toe view, comes FORWARD early (o -19 -> -3 by u 460,
    # while the other boot is planted from u 333 to 667), passes low near its v8 spot, and descends onto the landing
    # row during the flight (u 667 .. 1000), so one boot is always close to the floor line (see "hop_look" metrics).
    "swing_keys": [
        [0, V05_LAND - V05_STANCE, 1, "toe", 0],
        [110, V05_LAND - 19, 2, "toe", 1],
        [270, V05_LAND - 13, 2, "hang", 1],
        [460, V05_LAND - 5, 2, "hang", 1],
        [640, V05_LAND - 2, 2, "reach", 1],
        [840, V05_LAND - 1, 1, "reach", 1],
        [930, V05_LAND, 1, "strike", 1],
        [1000, V05_LAND, 1, "strike", 1],
    ],
}


# v04's forward leg over its nominal cycle (v04 QA note / manifest metrics.forward_leg_nominal_cycle): v05 must be shorter.
V04_FORWARD_LEG = {"hip_to_sole_rows_max": {"vl": 43, "vr": 46}, "cuff_jog_texels_max": {"vl": 1.0, "vr": 1.0}}
# v04's gait numbers (v04 manifest gait block) and its floor gap (this builder's floor_gap() rule run on the v04 GAIT keys
# in a scratch script, nothing written): the lowest drawn boot sole above its v8 ground row, per px of the nominal cycle.
V04_GAIT_REFERENCE = {"stride_px": 96, "steps_per_s": 5.833, "stance_px": 22, "stance_ms": 78.571, "flight_ms_per_step": 92.857,
                      "airborne_share": 0.5417, "swing_lift_max_rows": 3, "land_offset": 3, "liftoff_offset": -19,
                      "floor_gap_rows_max": 10, "floor_gap_rows_mean": 3.52, "floor_gap_share_ge_2_rows": 0.6042,
                      "floor_gap_share_ge_3_rows": 0.5208}


# v03's forward leg (boot ahead of v8's ground row) over its nominal cycle, measured with leg_metrics() on the v03 builder
# (loaded read-only in a scratch script, nothing written): the numbers v04 must improve on.
V03_FORWARD_LEG = {"hip_to_sole_rows_max": {"vl": 46, "vr": 49}, "trouser_rows_max": {"vl": 34, "vr": 36},
                   "cuff_jog_texels_max": {"vl": 4.0, "vr": 6.0}}


def stance_kin(q):
    """v04 knee lean (texels inward) of a planted boot q px after landing."""
    kin = 0
    for q0, k in GAIT["stance_knee_kin"]:
        if q >= q0:
            kin = k
    return kin
# Release / re-press rules, executed by the TEST-ONLY GDScript compositor (time domain once the body has stopped).
STOP = {
    "rule": "on the release tick the hero stops (runtime unchanged).  1) every boot in the air flies to its v8 spot "
            "and lands (lift <= 2, lift >= 1 until touchdown); 2) then each planted boot that is not on its v8 spot does "
            "one low shuffle step (lift 1 for an offset <= 3 rows, else 2) to it, rearmost first; a planted boot never "
            "moves while planted; at most one boot changes its view or touches down per tick (the other holds one tick); "
            "3) weight shift: while one boot moves, the torso shifts 1 texel toward the boot that carries the weight; "
            "after the last touchdown the body stays 1 row low (dip); the torso shift returns first (one texel per "
            "change, while dipped), then the arms step toward N, then - at least settle_ms after the touchdown - the dip "
            "returns, then the hair follows; hair / cape move at most one row / texel per tick; "
            "4) the tick after the composite equals v8 (neutral state), the v8 PNG itself is shown.  "
            "v06 TIME-BASED CLOCK (v05 counted ticks): every touchdown and every settle change has an event time in ms. "
            "A touchdown happens at start + duration, but never before the previous frame (a boot that is still drawn in "
            "the air on a frame cannot have landed before it).  The second boot's shuffle starts at the first boot's "
            "touchdown time.  A boot held by the one-boot-change-per-tick rule shifts its clock by min(frame time, "
            "hold_shift_ms) (v05: a whole frame).  A moving boot never jumps from its start pose to touchdown in one frame: "
            "it shows its mid key on that frame first (only at frame times > land / shuffle half durations).  After the "
            "last touchdown the settle changes run in v05's order on the event clock: the hair catch-up at the dip time + "
            "stop_hair_lag_ms; each torso step, arm step and the dip release at least settle_gap_ms after the previous "
            "change (arm steps also arm_step_ms apart, the dip release also settle_ms after the touchdown); the hair "
            "follows the dip release by stop_hair_lag_ms.  Each frame draws the state at its own time: at <= 1 frame per "
            "settle_gap_ms (60 fps and above) that is at most one change per tick, as in v05; at 30 fps two changes can "
            "share a frame (a 16 ms hair lag is shorter than one 33 ms frame, so the hair moves with the body).",
    "land_ms_base": 34, "land_ms_per_px": 2, "land_ms_per_lift": 4, "land_ms_max": 84,
    "shuffle_ms_base": 34, "shuffle_ms_per_px": 2, "shuffle_ms_max": 60, "shuffle_lift_max": 2,
    "arm_step_ms": 25, "hair_lag_ms": 34,
    # v04: settle dip 25 ms, hair 16 ms after a stop, cape with the torso
    "settle_ms": 25, "stop_hair_lag_ms": 16, "stop_cape_lag_ms": 0,
    "settle_order": ["hair_catch_up", "torso_shift_to_0", "arm_step_toward_N", "dip_release", "hair_follow"],
    # v06: the settle runs on an event clock (ms), not on frame counts
    "settle_clock": "event-time-ms (v06; v05: one change per frame)",
    "settle_gap_ms": 16.667,          # minimum time between two settle changes = one 60 fps frame
    "hold_shift_ms": 16.667,          # a boot held one frame by the one-boot-change rule loses at most this much time
    "no_pose_skip": True,             # a moving boot shows its mid key before touchdown on every frame rate
    "settle_one_body_change_per_tick": "at frame times <= settle_gap_ms (60 fps and above); at 30 fps up to 2",
    "land_keys": "[[0, o0, l0, view0, kin0], [500, rdiv(o0, 2), max(1, min(2, l0)), reach, 0], [1000, 0, 1, strike, 0]]; "
                 "at u >= 1000 the boot is in contact on its spot (stance view for q = land_offset)",
    "shuffle_keys": "[[0, o0, 1, toe if the planted view v0 is toe else heelup, 0], [500, rdiv(o0, 2), "
                    "min(2, 1 + |o0| // 4), hang, 1], [1000, 0, 1, strike, 0]] (v04: the toe start is new)",
}
RESTART = {
    "rule": "on a re-press the planted boot (if two: the one that landed LAST) stays in stance and keeps its window row; "
            "the gait phase is re-derived from its offset (q = land_offset - o); the other boot (if planted: lifted now; "
            "if in the air: kept where it is) gets a re-planned swing from its current offset / lift to land_offset at "
            "its next scheduled landing (the stride sync of 48 px is kept).  The leg that landed last is never the one "
            "that lifts first, so the next touchdown is always the other boot.  With both boots in the air the frozen "
            "phase resumes.  Arms ease to the gait pose one arm and one pose step per tick until they match it.",
    "replan_keys": "[[0, o0, max(1, l0), toe if view0 is a stance view else view0, kin0], [500, rdiv(o0 + land_offset, 2), "
                   "max(l0, hs), hang, 1], [800, land_offset - 1, max(1, rdiv(hs, 2)), reach, 0], "
                   "[1000, land_offset, 1, strike, 0]]; hs = clamp(rdiv(3 * remaining_px, stride_px - stance_px), "
                   "replan_lift_min, replan_lift_max)",
    "replan_lift_max": 3, "replan_lift_min": 2,
}


def rdiv(n, d):
    """floor(n / d + 1/2) for integers, d > 0 (the GDScript port uses the same integer formula)."""
    return (2 * n + d) // (2 * d)


def load_v8_grid(path):
    a = np.array(Image.open(path).convert("RGBA"))
    if a.shape != (V8_H, W, 4):
        raise SystemExit(f"v8 cell is {a.shape}, expected {(V8_H, W, 4)}")
    return {(x, y): INV[tuple(int(c) for c in a[y, x, :3])] for y in range(V8_H) for x in range(W) if a[y, x, 3]}


def split_checked():
    v8 = load_v8_grid(v8_path_checked())
    P = split_v8(v8)
    seen = {}
    for name, part in P.items():
        for p, c in part.items():
            if p in seen or v8.get(p) != c:
                raise SystemExit(f"v8 split is not a partition at {p} ({name})")
            seen[p] = name
    if len(seen) != len(v8):
        raise SystemExit("v8 split dropped texels")
    return v8, P


def split3(P):
    """As v01 / v02: hair lock off the upper body, cape top / hem, arm segments."""
    y0, y1, xmax = HAIR_LOCK
    lock = {p: c for p, c in P["upper"].items() if y0 <= p[1] <= y1 and p[0] <= xmax}
    upper = {p: c for p, c in P["upper"].items() if p not in lock}
    top = {p: c for p, c in P["cape"].items() if p[1] < CAPE_HEM_ROW}
    hem = {p: c for p, c in P["cape"].items() if p[1] >= CAPE_HEM_ROW}
    seg, upper = split_arms(P, upper)
    return lock, upper, top, hem, seg


# ============================================================================ v03: part library
def boot_rows_v03(side, view):
    keep, foot = FOOT_V03[side][view] if view in FOOT_V03[side] else FOOT[side][view]
    if view in V04_FULL_SHAFT_VIEWS:
        keep = "full"
    idx = SHAFT_KEEP[keep]
    return [r for i, r in enumerate(SHAFT[side]) if idx is None or i in idx] + foot


def boot_texels_v03(side, view, cuff_x, sole):
    """As boot_texels (v01), with the v03 authored views."""
    rows = boot_rows_v03(side, view)
    o, top = rows[0]
    x0 = rnd(cuff_x - (o + (len(top) - 1) / 2))
    y0 = sole - len(rows) + 1
    tex = {}
    for j, (o, r) in enumerate(rows):
        for i, ch in enumerate(r):
            if ch not in ". ":
                tex[(x0 + o + i, y0 + j)] = ch
    return tex, y0


def boot_part(side, view, legpart):
    """Boot texels with the sole on v8's ground row (offset 0)."""
    if view == "v8":
        return {p: c for p, c in legpart.items() if p[1] >= BOOT_TOP}
    share, lean = BOOT_ALIGN[view]
    probe, _ = boot_texels_v03(side, view, CUFF_X[side], GROUND[side])
    v8_toe = [x for (x, y) in legpart if y == GROUND[side]]
    view_toe = [x for (x, y) in probe if y == GROUND[side]]
    bdx = lean * INWARD[side] + rnd(share * (sum(v8_toe) / len(v8_toe) - sum(view_toe) / len(view_toe)))
    tex, _ = boot_texels_v03(side, view, CUFF_X[side] + bdx, GROUND[side])
    return tex


def shadow_centre(legpart, side):
    """x centre of the v8 boot's lowest five rows (the foot's mass on the floor)."""
    xs = [x for (x, y) in legpart if y > GROUND[side] - 5]
    return rnd(sum(xs) / len(xs))


def shadow_part(cx, ground, lift):
    """Contact shadow on the floor under a foot: a flat 5-row ellipse centred on the foot, narrower as the foot lifts.
    Single ink colour, binary alpha (opacity is applied when it is drawn)."""
    hw = 6 - min(lift, 3)
    rows = [(-2, hw - 2), (-1, hw), (0, hw), (1, hw - 1), (2, hw - 3)]
    out = {}
    for dy, h in rows:
        if h < 0:
            continue
        for x in range(cx - h, cx + h + 1):
            out[(x, ground + dy)] = "K"
    return out


def build_parts(v8, P):
    lock, upper, top, hem, seg = split3(P)
    parts = {}
    for h in HDY:
        parts[f"cape-hdy-{HTAG[h]}"] = cape_layer(top, hem, 0, h)
        parts[f"hair-hdy-{HTAG[h]}"] = lag(lock, HAIR_LOCK[0], 0, h)
    parts["hips"] = {p: c for k in ("legvl", "legvr") for p, c in P[k].items() if p[1] <= 66}
    parts["coat-skirt"] = dict(P["skirt"])
    parts["head"] = {p: c for p, c in upper.items() if head_texel(*p)}
    parts["torso"] = {p: c for p, c in upper.items() if not head_texel(*p)}
    for side in ("vl", "vr"):
        parts[f"leg-src-{side}"] = {p: c for p, c in P["leg" + side].items() if p[1] < BOOT_TOP}
        for view in BOOT_VIEWS:
            parts[f"boot-{side}-{view}"] = boot_part(side, view, P["leg" + side])
        cx = shadow_centre(P["leg" + side], side)
        for lift in SHADOW_LIFTS:
            parts[f"shadow-{side}-l{lift}"] = shadow_part(cx, GROUND[side], lift)
    # body for the arm seams: the neutral (v8) stack without arms
    body = {}
    for k in ("cape-hdy-0", "hips", "coat-skirt", "torso", "head", "hair-hdy-0"):
        body.update(parts[k])
    for side in ("vl", "vr"):
        body.update(P["leg" + side])
    for pose in ARM_SET:
        al = arm_layers(seg, {"R": pose, "L": pose}, 0, 0, body)
        for side, layer in (("R", "arm-vl"), ("L", "arm-vr")):
            parts[f"{layer}-{pose}-front"] = al[layer]
            parts[f"{layer}-{pose}-back"] = al[layer + "-back"]
            parts[f"{layer}-{pose}-seam"] = al[layer + "-seam"]
    return parts


# ============================================================================ v03: reference compositor
def pick(src_rows, n):
    """n output rows taken from src_rows by nearest whole-row repeat / drop (no resampling of texels)."""
    if n <= 0:
        return []
    k = len(src_rows)
    return [src_rows[min(k - 1, (i * k) // n)] for i in range(n)]


def leg_rows_plan(side, bob, bt):
    """Row plan between the hip (61 + bob) and the boot top bt: (thigh rows, knee rows, shin rows) or None."""
    k0, k1 = KNEE_BAND[side]
    T, K, S = list(range(HIP_ROW, k0)), list(range(k0, k1 + 1)), list(range(k1 + 1, BOOT_TOP))
    n = bt - (HIP_ROW + bob)
    full = len(T) + len(K) + len(S)
    if n < full:
        # v03: a leg shorter than v8's (the boot behind the body, higher on screen) is FORESHORTENED as a whole: the
        # thigh, the knee band and the shin all lose whole rows in proportion, so the knee guard reads as tilted away
        # rather than lifted toward the camera (v02 crushed only the thigh and kept the full guard under the coat).
        if n < KNEE_MIN_ROWS + 2:
            return None
        nk = max(KNEE_MIN_ROWS, rdiv(n * len(K), full))
        nt = max(1, rdiv((n - nk) * len(T), len(T) + len(S)))
        ns = n - nk - nt
        if ns < 1:
            nt, ns = nt - (1 - ns), 1
        if nt < 1:
            return None
        return pick(T, nt), pick(K, nk), pick(S, ns)
    # v04: a leg LONGER than v8's (the forward / landing boot) keeps v8's thigh rows 1:1 and the whole knee band; only
    # the shin takes the extra rows, so the knee sits where v8's knee is and the leg breaks there (with the knee lean)
    # instead of v03's evenly repeated thigh + shin rows (a straight stilt).
    rest = n - len(K)
    nt = max(1, min(rest - 1, len(T)))
    return pick(T, nt), K, pick(S, rest - nt)


def rows_of_part(part):
    rows = {}
    for (x, y), c in part.items():
        rows.setdefault(y, {})[x] = c
    return rows


def compose_leg(parts, side, bob, foot):
    """One leg from v8's own leg rows + a boot part.  foot = {o, lift, view, kin}.  -> (texels, boot texels, sole)."""
    dy = foot["o"] - foot["lift"]
    boot = shift(parts[f"boot-{side}-{foot['view']}"], 0, dy)
    bt = min(y for (_, y) in boot)
    plan = leg_rows_plan(side, bob, bt)
    if plan is None:
        raise SystemExit(f"leg {side} bob {bob} foot {foot}: no room between hip and boot top {bt}")
    th, kn, sh = plan
    kdx = foot["kin"] * INWARD[side]
    src = rows_of_part(parts[f"leg-src-{side}"])
    out = {}
    y = HIP_ROW + bob
    for i, sy in enumerate(th):
        dx = rdiv(kdx * i * i, (len(th) - 1) ** 2) if len(th) > 1 else 0
        for x, c in src.get(sy, {}).items():
            out[(x + dx, y)] = c
        y += 1
    for sy in kn:
        for x, c in src.get(sy, {}).items():
            out[(x + kdx, y)] = c
        y += 1
    # v04: on a leg longer than v8's (more shin rows than v8's shin) the shin slopes from the knee to the boot's cuff
    # (cdx = cuff centre - v8 shin-bottom centre, whole texels), so the leg breaks at the knee instead of running
    # straight down and jogging sideways into a strike / reach boot (v03: the shin returned to v8's x, a 4-6 texel jog).
    # Every other leg keeps v03's rule (the shin returns to v8's x at the boot).
    end = 0
    if len(sh) > BOOT_TOP - 1 - KNEE_BAND[side][1]:
        brow = [x for (x, yy) in boot if yy == bt]
        srow = list(src.get(BOOT_TOP - 1, {}))
        end = rdiv(min(brow) + max(brow) - min(srow) - max(srow), 2)
    for i, sy in enumerate(sh):
        dx = kdx + rdiv((end - kdx) * (i + 1), len(sh) + 1)
        for x, c in src.get(sy, {}).items():
            out[(x + dx, y)] = c
        y += 1
    out.update(boot)
    return out, boot, GROUND[side] + dy


def leg_metrics(leg, boot, sole, bob):
    """Hip-to-sole rows, trouser rows (hip .. boot top - 1) and the cuff jog: |centre x of the boot's top row - centre x
    of the trouser row just above it| (texels; v03's straight forward leg jogged 4-6 texels into the strike boot)."""
    bt = min(y for (_, y) in boot)
    above = [x for (x, y) in leg if y == bt - 1 and (x, y) not in boot]
    cuff = [x for (x, y) in boot if y == bt]
    jog = abs((min(cuff) + max(cuff)) - (min(above) + max(above))) / 2 if above else None
    return {"hip_to_sole_rows": sole - (HIP_ROW + bob) + 1, "trouser_rows": bt - (HIP_ROW + bob), "cuff_jog_texels": jog}


def in_contact(foot):
    return foot["lift"] == 0 and foot["view"] in STANCE_VIEWS


def near_leg(feet):
    c = {s: in_contact(feet[s]) for s in ("vl", "vr")}
    if c["vl"] != c["vr"]:
        return "vl" if not c["vl"] else "vr"
    return "vl" if feet["vl"]["o"] > feet["vr"]["o"] else "vr"


def seam_fill(g, y0, y1):
    """Single transparent texels closed left, right and above between rows y0..y1 -> ink (v03's neck / shoulder seam
    rule, kept as a guard; with v04's rigid head + torso shift it is expected to fill nothing - counted per keyframe)."""
    fill = {}
    for y in range(y0, y1 + 1):
        for x in range(1, W - 1):
            if (x, y) not in g and (x - 1, y) in g and (x + 1, y) in g and (x, y - 1) in g:
                fill[(x, y)] = "K"
    return fill


def compose(parts, state):
    """state = {bob, hdy, sx, csx, arms {R, L}, feet {vl, vr: {o, lift, view, kin}}} -> (layers, shadow, info)."""
    b, h, sx, csx = state["bob"], state["hdy"], state["sx"], state["csx"]
    legs, boots, soles = {}, {}, {}
    for side in ("vl", "vr"):
        legs[side], boots[side], soles[side] = compose_leg(parts, side, b, state["feet"][side])
    near = near_leg(state["feet"])
    far = "vl" if near == "vr" else "vr"
    R, L = state["arms"]["R"], state["arms"]["L"]
    torso = shift(parts["torso"], sx, b)
    torso.update(shift(parts[f"arm-vl-{R}-seam"], sx, b))
    torso.update(shift(parts[f"arm-vr-{L}-seam"], sx, b))
    layers = {
        "cape": shift(parts[f"cape-hdy-{HTAG[h]}"], csx, b),
        "arm-vl-back": shift(parts[f"arm-vl-{R}-back"], sx, b),
        "arm-vr-back": shift(parts[f"arm-vr-{L}-back"], sx, b),
        "hips": shift(parts["hips"], 0, b),
        "leg-far": dict(legs[far]), "leg-near": dict(legs[near]),
        "coat-skirt": shift(parts["coat-skirt"], sx, b),
        "torso": torso,
        "head": shift(parts["head"], sx, b),                       # v04: with the torso (v03: 0, b)
        "hair-lock": shift(parts[f"hair-hdy-{HTAG[h]}"], sx, b),
        "arm-vl": shift(parts[f"arm-vl-{R}-front"], sx, b),
        "arm-vr": shift(parts[f"arm-vr-{L}-front"], sx, b),
    }
    holes = pinhole_fill(layers, HIP_ROW + b)
    layers["leg-near"].update(holes)
    seams = seam_fill(stack(layers), 28 + b, 40 + b) if sx else {}
    layers["torso"].update(seams)
    shadow = {}
    for side in ("vl", "vr"):
        f = state["feet"][side]
        shadow.update(shift(parts[f"shadow-{side}-l{min(f['lift'], 3)}"], 0, f["o"]))
    return layers, shadow, {"boots": boots, "soles": soles, "near": near, "pinholes_filled": len(holes),
                            "seam_filled": len(seams),
                            "legs": {s: leg_metrics(legs[s], boots[s], soles[s], b) for s in ("vl", "vr")}}


# ============================================================================ v03: nominal gait (keyframes)
def interp_keys(keys, u):
    """keys [[u, o, lift, view, kin], ...] (u per mille, ascending) -> (o, lift, view, kin) at u (0..1000)."""
    for i in range(len(keys) - 1):
        u0, o0, l0, v0, k0 = keys[i]
        u1, o1, l1 = keys[i + 1][:3]
        if u0 <= u < u1 or (i == len(keys) - 2 and u >= u1):
            t = min(u, u1) - u0
            return o0 + rdiv((o1 - o0) * t, u1 - u0), l0 + rdiv((l1 - l0) * t, u1 - u0), v0, k0
    raise SystemExit(f"u {u} outside the key table")


def stance_view(q):
    view = None
    for q0, name in GAIT["stance_roll"]:
        if q >= q0:
            view = name
    return view


def nominal_foot(side, phase):
    g = GAIT
    sd, e = g["stride_px"], g["stance_px"]
    q = (phase - g["phase_offset_px"][side]) % sd
    if q < e:
        return {"o": g["land_offset"] - q, "lift": 0, "view": stance_view(q),
                "kin": stance_kin(q)}, q
    u = rdiv(1000 * (q - e), sd - e)
    o, lift, view, kin = interp_keys(g["swing_keys"], u)
    return {"o": o, "lift": lift, "view": view, "kin": kin}, q


def nominal_bob(phase):
    a, z = GAIT["bob_stance_q"]
    for s in ("vl", "vr"):
        f, q = nominal_foot(s, phase)
        if in_contact(f) and a <= q < z:
            return 1
    return 0


def nominal_sx(phase):
    a, z = GAIT["torso_shift_stance_q"]
    for s in ("vl", "vr"):
        f, q = nominal_foot(s, phase)
        if in_contact(f) and a <= q < z:
            return -INWARD[s]            # toward the planted boot (vl: viewer-left = -1)
    return 0


def arm_pose(side, phase):
    sd = GAIT["stride_px"]
    f = (phase - GAIT["arm_peak_px"][side]) % sd
    d = min(f, sd - f)
    b1, b2, b3, b4 = GAIT["arm_pose_bands_px"]
    if d <= b1:
        return "F2"
    if d <= b2:
        return "F1"
    if d < b3:
        return "N"
    if d < b4:
        return "B1"
    return "B2"


def nominal_state(phase):
    feet = {s: nominal_foot(s, phase)[0] for s in ("vl", "vr")}
    bob = nominal_bob(phase)
    hdy = max(-1, min(1, nominal_bob(phase - GAIT["hair_lag_px"]) - bob))
    return {"bob": bob, "hdy": hdy, "sx": nominal_sx(phase), "csx": nominal_sx(phase - GAIT["cape_shift_lag_px"]),
            "arms": {"R": arm_pose("R", phase), "L": arm_pose("L", phase)}, "feet": feet}


NEUTRAL = {"bob": 0, "hdy": 0, "sx": 0, "csx": 0, "arms": {"R": "N", "L": "N"},
           "feet": {s: {"o": 0, "lift": 0, "view": "v8", "kin": 0} for s in ("vl", "vr")}}
KEYFRAME_PHASES = list(range(0, GAIT["stride_px"], 7))     # v05: 12 review keyframes per cycle (every 7 px = 25 ms)


# ============================================================================ v03: gates and metrics
def grid_rows(g):
    ys = [y for (_, y) in g]
    return min(ys), max(ys)


def head_top(g):
    return min(y for (x, y) in g if 10 <= x < 70)


def land_keys(o0, l0, v0, k0):
    """Release: a boot in the air flies to its v8 spot (time domain, u per mille of the landing duration)."""
    return [[0, o0, l0, v0, k0], [500, rdiv(o0, 2), max(1, min(2, l0)), "reach", 0], [1000, 0, 1, "strike", 0]]


def shuffle_keys(o0, v0):
    """Release: a planted boot off its v8 spot takes one low step to it.  v04: a boot planted in the toe view (heel
    already up, only reachable at the far back of the contact) lifts in that view; every other boot lifts heel-up as v03
    (the 14-row heel-up boot does not fit under the hip at v04's rear limit o = -18 with the 1-row dip)."""
    first = "toe" if v0 == "toe" else "heelup"
    return [[0, o0, 1, first, 0], [500, rdiv(o0, 2), min(2, 1 + abs(o0) // 4), "hang", 1], [1000, 0, 1, "strike", 0]]


def replan_keys(o0, l0, v0, k0, hs):
    """Re-press: the lifting / airborne boot swings from where it is to the landing offset (distance domain)."""
    a = GAIT["land_offset"]
    return [[0, o0, max(1, l0), "toe" if v0 in STANCE_VIEWS else v0, k0], [500, rdiv(o0 + a, 2), max(l0, hs), "hang", 1],
            [800, a - 1, max(1, rdiv(hs, 2)), "reach", 0], [1000, a, 1, "strike", 0]]


def reachable_feet():
    """Closure of every foot state (o, lift, view, kin) the compositor can draw: stance, the swing table, and any
    chain of landing / shuffle / re-plan moves started from any reachable state at any u (integer per mille)."""
    g = GAIT
    seen = set()
    todo = []

    def add(t):
        if t not in seen:
            seen.add(t)
            todo.append(t)
    for q in range(g["stride_px"]):
        f = nominal_foot("vl", q + g["phase_offset_px"]["vl"])[0]
        add((f["o"], f["lift"], f["view"], f["kin"]))
    for o in range(g["liftoff_offset"] + 1, g["land_offset"] + 1):        # stance at any offset (stop / re-press)
        for kin in (0, 1, 2):
            add((o, 0, stance_view(g["land_offset"] - o), kin))
    add((0, 0, "v8", 0))
    hs_set = range(RESTART["replan_lift_min"], RESTART["replan_lift_max"] + 1)
    tables_done = set()
    while todo:
        o0, l0, v0, k0 = todo.pop()
        tabs = [("land", (o0, l0, v0, k0))] + [("replan", (o0, l0, v0, k0, hs)) for hs in hs_set]
        if v0 in STANCE_VIEWS and l0 == 0 and o0 != 0:
            tabs.append(("shuffle", (o0, v0)))
        for kind, args in tabs:
            if (kind, args) in tables_done:
                continue
            tables_done.add((kind, args))
            keys = {"land": land_keys, "shuffle": shuffle_keys, "replan": replan_keys}[kind](*args)
            for u in range(1001):
                o, lift, view, kin = interp_keys(keys, u)
                add((o, lift, view, kin))
    return seen


def feasibility_sweep(parts):
    """Every leg the compositor can be asked for (reachable_feet x both sides x bob 0/1) must fit between the hip and
    the boot, and stay inside the 80x120 cell; knee-band squeezes are counted."""
    states = reachable_feet()
    bad, n, squeezed = [], 0, []
    for side in ("vl", "vr"):
        for bob in (0, 1):
            for (o, lift, view, kin) in sorted(states, key=str):
                boot = shift(parts[f"boot-{side}-{view}"], 0, o - lift)
                bt = min(y for (_, y) in boot)
                n += 1
                plan = leg_rows_plan(side, bob, bt)
                if plan is None or max(y for (_, y) in boot) > H - 1:
                    bad.append((side, bob, view, o, lift))
                elif len(plan[1]) < KNEE_BAND[side][1] - KNEE_BAND[side][0] + 1:
                    squeezed.append(len(plan[1]))
    fs = {"legs_foreshortened": len(squeezed), "knee_band_rows_min": min(squeezed) if squeezed else None,
          "knee_band_rows_full": {s: KNEE_BAND[s][1] - KNEE_BAND[s][0] + 1 for s in ("vl", "vr")}}
    return n, bad, len(states), fs


def identity_check(v8, grid, state, layers):
    """v04: head AND torso texels in rows 8..57 outside the declared arm / hair zones = v8 moved by the same (sx, bob),
    exactly, wherever a swung arm (F2 fist in front of the chest) does not cover them (counted).  Neck rows 29..40 are
    counted separately: a neck texel off its v8 place relative to the torso is a shear."""
    b, sx = state["bob"], state["sx"]
    arm_front = set(layers["arm-vl"]) | set(layers["arm-vr"])
    mism = checked = arm_cover = neck_checked = neck_mism = 0
    for (x, y), c in v8.items():
        if y > 57 or (y >= 40 and (x <= 27 or x >= 45)) or (HAIR_LOCK[0] - 1 <= y <= HAIR_LOCK[1] + 1 and x <= HAIR_LOCK[2] + 1):
            continue
        q = (x + sx, y + b)
        if q in arm_front:
            arm_cover += 1
            continue
        checked += 1
        bad = grid.get(q) != c
        mism += bad
        if 29 <= y <= 40:
            neck_checked += 1
            neck_mism += bad
    return {"checked_texels": checked, "mismatched": mism, "neck_rows_29_40_checked": neck_checked,
            "neck_rows_29_40_mismatched": neck_mism, "head_dx_minus_torso_dx": 0,
            "texels_under_a_swung_arm": arm_cover}


def floor_gap(phase):
    """v05 hop-look metric: rows between v8's ground row and the LOWEST drawn boot sole (0 when a boot reaches it).  A gap
    means both boots are drawn above the floor line at once, which reads as a hop / hang at gameplay size."""
    low = max(nominal_foot(s, phase)[0]["o"] - nominal_foot(s, phase)[0]["lift"] for s in ("vl", "vr"))
    return max(0, -low)


def gait_numbers():
    sd, e = GAIT["stride_px"], GAIT["stance_px"]
    v = 2 * SPEED_PX_S
    cyc = 1000 * sd / v
    air = 0
    lifts = []
    for ph in range(sd):
        c = [in_contact(nominal_foot(s, ph)[0]) for s in ("vl", "vr")]
        air += not any(c)
        lifts += [nominal_foot(s, ph)[0]["lift"] for s in ("vl", "vr")]
    return {"speed_window_px_s": v, "cycle_ms_at_140": round(cyc, 3), "steps_per_s": round(2000 / cyc, 3),
            "stance_ms_at_140": round(1000 * e / v, 3), "flight_ms_per_step_at_140": round(1000 * (sd / 2 - e) / v, 3),
            "airborne_share_of_cycle": round(air / sd, 4), "swing_lift_max_rows": max(lifts),
            "floor_gap_rows_max": max(floor_gap(ph) for ph in range(sd)),
            "floor_gap_rows_mean": round(sum(floor_gap(ph) for ph in range(sd)) / sd, 2),
            "floor_gap_share_ge_2_rows": round(sum(floor_gap(ph) >= 2 for ph in range(sd)) / sd, 4),
            "floor_gap_share_ge_3_rows": round(sum(floor_gap(ph) >= 3 for ph in range(sd)) / sd, 4),
            "v04_reference": V04_GAIT_REFERENCE,
            "v02_reference": {"stance_px": 20, "stance_ms": 71.429, "flight_ms_per_step": 100.0, "airborne_share": 0.5833,
                              "swing_lift_max_rows": 8, "land_offset": 8, "liftoff_offset": -12},
            "v03_reference": {"stance_px": 22, "stance_ms": 78.571, "flight_ms_per_step": 92.857, "airborne_share": 0.5417,
                              "swing_lift_max_rows": 3, "land_offset": 6, "liftoff_offset": -16},
            "zero_slip_walk_needs": "no flight requires stance_px >= stride_px / 2, i.e. a stride <= 2 x %d px here: about "
                                    "%.1f steps/s at 140 logical px/s, so this is a run, not a walk" % (e, v / e)}


def build(out_dir):
    v8, P = split_checked()
    parts = build_parts(v8, P)
    palette = set(v8.values())
    # gate: neutral composition rebuilds v8 exactly (so the stop ends on v8 with no pop)
    neutral_layers, neutral_shadow, _ = compose(parts, NEUTRAL)
    spot = nominal_foot("vl", GAIT["phase_offset_px"]["vl"] + GAIT["land_offset"])[0]
    if (spot["o"], spot["lift"], spot["view"], spot["kin"]) != (0, 0, "v8", 0):
        raise SystemExit(f"a planted boot at its v8 spot is not drawn as v8 (kin / view): {spot}")
    if stack(neutral_layers) != v8:
        diff = set(stack(neutral_layers).items()) ^ set(v8.items())
        raise SystemExit(f"neutral composition differs from v8 at {len(diff)} texel entries")
    n_sweep, bad, n_states, squeezed = feasibility_sweep(parts)
    if bad:
        raise SystemExit(f"{len(bad)} of {n_sweep} reachable legs do not fit: {bad[:6]}")
    for k, part in parts.items():
        if not set(part.values()) <= palette:
            raise SystemExit(f"part {k}: colour outside v8's palette")
        for (x, y) in part:
            if not (0 <= x < W and 0 <= y < H):
                raise SystemExit(f"part {k}: texel outside the cell {(x, y)}")
    # ---------------------------------------------------------------- keyframes
    frames = {}
    identity = {}
    for ph in KEYFRAME_PHASES:
        st = nominal_state(ph)
        layers, shadow, info = compose(parts, st)
        g = stack(layers)
        if not set(g.values()) <= palette:
            raise SystemExit(f"keyframe {ph}: colour outside v8's palette")
        key = f"k{ph:02d}"
        frames[key] = {"phase": ph, "state": st, "layers": layers, "grid": g, "shadow": shadow, "info": info}
        identity[key] = identity_check(v8, g, st, layers)
        if identity[key]["mismatched"]:
            raise SystemExit(f"{key}: {identity[key]['mismatched']} identity texels differ from v8 + (sx, bob)")
        if info["seam_filled"]:
            raise SystemExit(f"{key}: the rigid head + torso shift opened {info['seam_filled']} neck seam texels")
    # ---------------------------------------------------------------- v04 forward-leg metrics over the nominal cycle
    fwd = {"hip_to_sole_rows_max": {}, "trouser_rows_max": {}, "cuff_jog_texels_max": {}}
    for ph in range(GAIT["stride_px"]):
        st = nominal_state(ph)
        info = compose(parts, st)[2]
        for s in ("vl", "vr"):
            if st["feet"][s]["o"] > 0:                      # the boot ahead of v8's ground row (reach / strike / landing)
                lm = info["legs"][s]
                fwd["hip_to_sole_rows_max"][s] = max(fwd["hip_to_sole_rows_max"].get(s, 0), lm["hip_to_sole_rows"])
                fwd["trouser_rows_max"][s] = max(fwd["trouser_rows_max"].get(s, 0), lm["trouser_rows"])
                fwd["cuff_jog_texels_max"][s] = max(fwd["cuff_jog_texels_max"].get(s, 0), lm["cuff_jog_texels"] or 0)
    fwd["v8_hip_to_sole_rows"] = {s: GROUND[s] - HIP_ROW + 1 for s in ("vl", "vr")}
    fwd["v8_trouser_rows"] = BOOT_TOP - HIP_ROW
    fwd["v03_reference"] = V03_FORWARD_LEG
    fwd["v04_reference"] = V04_FORWARD_LEG
    if any(fwd["hip_to_sole_rows_max"][s] >= V04_FORWARD_LEG["hip_to_sole_rows_max"][s] for s in ("vl", "vr")):
        raise SystemExit(f"v05 forward leg not shorter than v04: {fwd}")
    if any(fwd["cuff_jog_texels_max"][s] > 1 for s in ("vl", "vr")):
        raise SystemExit(f"v05 cuff jog above v04's 1 texel: {fwd}")
    # ---------------------------------------------------------------- nominal per-px table (what the compositor draws)
    sd = GAIT["stride_px"]
    per_px = []
    for ph in range(sd):
        st = nominal_state(ph)
        per_px.append({"phase_px": ph, "bob": st["bob"], "hdy": st["hdy"], "sx": st["sx"], "csx": st["csx"],
                       "arms": st["arms"],
                       "feet": {s: dict(st["feet"][s], contact=in_contact(st["feet"][s]),
                                         sole_row=GROUND[s] + st["feet"][s]["o"] - st["feet"][s]["lift"])
                                for s in ("vl", "vr")}})
    # world-space row of a planted boot along the nominal cycle: body row Y = phase; boot window row = Y + GROUND + o.
    contact_world = {}
    for s in ("vl", "vr"):
        rows, runs, views = [], [], []
        for ph in range(2 * sd):
            f = nominal_foot(s, ph)[0]
            if in_contact(f):
                rows.append(ph + GROUND[s] + f["o"])
                views.append(f["view"])
            elif rows:
                runs.append((rows, views))
                rows, views = [], []
        contact_world[s] = {"contacts": len(runs), "px_per_contact": sorted({len(r) for r, _ in runs}),
                            "max_world_row_change_in_contact": max(max(r) - min(r) for r, _ in runs),
                            "roll_views_in_order": sorted({tuple(dict.fromkeys(v)) for _, v in runs})}
    # extents over every reachable leg state (display / collision bounds; the pin row is PIN[1] = 104, v8 ground 103)
    low = 0
    for side in ("vl", "vr"):
        for (o, lift, view, kin) in reachable_feet():
            low = max(low, max(y for (_, y) in shift(parts[f"boot-{side}-{view}"], 0, o - lift)))
    shadow_low = max(y for side in ("vl", "vr") for (_, y) in shift(parts[f"shadow-{side}-l0"], 0, GAIT["land_offset"]))
    bounds = {"v8_lowest_row": 103, "sprite_lowest_row_any_reachable_state": low,
              "sprite_rows_below_v8_ground": low - 103, "sprite_logical_px_below_v8_ground": (low - 103) / 2,
              "shadow_lowest_row": shadow_low, "max_visible_height_texels": None,
              "collision": "runtime collision is the hero foot point (CityNavigation / annex clamps), unchanged; the "
                           "pilot is display-only and never feeds back into movement"}
    tops = [grid_rows(fr["grid"])[0] for fr in frames.values()]
    bounds["max_visible_height_texels_keyframes"] = max(grid_rows(fr["grid"])[1] - grid_rows(fr["grid"])[0] + 1
                                                        for fr in frames.values())
    bounds["crown_rows_keyframes"] = sorted(set(tops))
    del bounds["max_visible_height_texels"]
    # ---------------------------------------------------------------- write
    os.makedirs(_fs(out_dir), exist_ok=True)
    written = []
    part_entries = []
    for role in sorted(parts):
        data = png_bytes(to_rgba(parts[role]))
        name = f"{SLUG}_protagonist-female_{PART}-part-{role}_{VARIANT}_{STAMP}-{fid('part-' + role)}.png"
        written.append(_write(out_dir, name, data))
        part_entries.append({"role": role, "file": name, "sha256": hashlib.sha256(data).hexdigest(),
                             "opaque_texels": len(parts[role])})
    frame_entries = []
    for key, fr in frames.items():
        data = png_bytes(to_rgba(fr["grid"]))
        name = f"{SLUG}_protagonist-female_{PART}-keyframe-{fr['phase']:02d}px_{VARIANT}_{STAMP}-{fid('key-' + key)}.png"
        written.append(_write(out_dir, name, data))
        sdata = png_bytes(to_rgba(fr["shadow"]))
        sname = f"{SLUG}_protagonist-female_{PART}-keyframe-{fr['phase']:02d}px-shadow_{VARIANT}_{STAMP}-{fid('kshadow-' + key)}.png"
        written.append(_write(out_dir, sname, sdata))
        top, lo = grid_rows(fr["grid"])
        frame_entries.append({"key": key, "phase_px": fr["phase"], "file": name, "sha256": hashlib.sha256(data).hexdigest(),
                              "shadow_file": sname, "shadow_sha256": hashlib.sha256(sdata).hexdigest(),
                              "state": fr["state"], "near_leg": fr["info"]["near"], "soles": fr["info"]["soles"],
                              "crown_row": head_top(fr["grid"]), "lowest_row": lo, "visible_height_texels": lo - top + 1,
                              "pinholes_filled": fr["info"]["pinholes_filled"], "seam_filled": fr["info"]["seam_filled"],
                              "legs": fr["info"]["legs"]})
        fr["png"] = data
    # layered editable sources: keyframes .pxo (frames x 13 layers incl. the shadow) and the part library .ora
    keys = list(frames)
    pxo_name = f"{SLUG}_protagonist-female_{PART}-keyframes-editable_{VARIANT}_{STAMP}-{fid('keyframes-pxo')}.pxo"
    pxo = make_pxo([dict(frames[k]["layers"], shadow=frames[k]["shadow"]) for k in keys], [1.0] * len(keys),
                   frames[keys[0]]["png"], f"{PART}-keyframes", 35.0, order=PXO_LAYERS, dt=(2026, 10, 17, 21, 16, 0),
                   opacity={"shadow": SHADOW_OPACITY})
    written.append(_write(out_dir, pxo_name, pxo))
    ora_name = f"{SLUG}_protagonist-female_{PART}-part-library-editable_{VARIANT}_{STAMP}-{fid('parts-ora')}.ora"
    ora = make_ora(parts, part_entries, stack(neutral_layers))
    written.append(_write(out_dir, ora_name, ora))
    gd = os.path.join(out_dir, ".gdignore")
    if not os.path.exists(_fs(gd)):
        with open(_fs(gd), "wb") as f:
            f.write(b"")
    manifest = {
        "project": "Worlds Between", "milestone": "M8", "character": "protagonist-female", "direction": "south",
        "motion_state": "run (deliberate run state at MOVE_SPEED 140; NOT a walk)",
        "part": PART, "variant": VARIANT, "workstream": "m8-w09", "stamp_utc": STAMP, "run_id": RUN_ID,
        "status": "UNAPPROVED / NONRUNTIME test-only single-direction motion pilot; Codex / creator visual review pending; "
                  "motion not approved; not a production sprite or runtime replacement",
        "art_approved": False, "human_reviewed": False, "runtime_integrated": False,
        "walk_animation_approved": False, "run_animation_approved": False, "stop_animation_approved": False,
        "counts_toward_art_acceptance": False,
        "approved_scope_unchanged": "selout v8 SOUTH IDLE static frame and the 48 logical px display scale only",
        "exploration_sprites_counter_unchanged": "0/52",
        "source": {"v8_png": V8_REL, "v8_sha256_bytes": V8_SHA256},
        "builder": {"path": "tools/" + os.path.basename(os.path.abspath(__file__)),
                    "started_from": "tools/rpg-2-star-ocean-the-second_protagonist-female_south-run-v05-build_m8-w08_20261017-055617-998d6a83.py (copied, not imported; v05 files untouched)"},
        "v06_changes": {
            "answers": "Codex: v05 60 fps stops improved, but at 30 fps release -> v8 grew to 267-333 ms and last touchdown -> "
                       "v8 to 167-200 ms (too sluggish for an acceptance candidate); fix the frame-rate-dependent settle",
            "cause": "v05 settle counted frames: each of up to five body changes after the last touchdown took its own "
                     "frame, and the one-boot-change hold cost a whole frame",
            "fix": "time-based stop clock (stop.settle_clock, settle_gap_ms, hold_shift_ms, no_pose_skip): touchdown and "
                   "settle changes have event times in ms; each frame draws the state at its own time",
            "unchanged": "art (every part / keyframe / shadow PNG has v05's pixels), gait (stride 84 px, 6.67 steps/s, lift <= "
                         "2, land +2), MOVE_SPEED 140, compositor, zero-slip planted boot, settle order, land / shuffle "
                         "keys and durations, re-press rule, <= 100 ms raised boot"},
        "v05_changes": {
            "answers": "creator: v04 not accepted, polish the run / stop (smooth, fluid, well-paced standard); Codex v04 review: "
                       "shorter forward reach, shorter airborne-looking interval, the visible boot lands before the body settles",
            "shorter_stride": "step 48 -> 42 px of body travel (stride_px 96 -> 84): 5.83 -> 6.67 steps/s at MOVE_SPEED 140; "
                              "land_offset 3 -> %d, so the landing leg is 1 row shorter again (hip-to-sole max 43/46 -> "
                              "gated below v04); knee lean at touchdown 2 -> 1 texel" % V05_LAND,
            "less_airborne_look": "swing lift <= 2 (v04 3); the swing boot comes forward early and passes low near its v8 spot "
                                  "while the other boot is planted, then descends onto the landing row during the flight; "
                                  "flight per step 93 -> 75 ms; floor gap (lowest boot above v8's ground row): see "
                                  "gait.floor_gap_* against gait.v04_reference",
            "stop_settle": "after the last touchdown one body change per tick: torso re-centres (while dipped), then the dip "
                           "releases (>= settle_ms after the touchdown), then the hair; arms step on other ticks",
            "unchanged": "MOVE_SPEED 140, single south direction, v04 part library rules (boots, legs, arms, head / torso rigid "
                         "block, cape, hair), zero-slip planted boot and stance roll, re-press rule, landing / shuffle "
                         "keys, test-only contact shadow, <= 100 ms raised boot after a release"},
        "cell": [W, H], "v8_cell": [W, V8_H], "ground_pin_cell": list(PIN),
        "display": {"scale": 0.5, "logical_height_px": 48, "filter": "nearest", "flip_h": False,
                    "body_draw_offset": "none: the body is drawn at the logical position",
                    "stance_boot": "drawn at the window row fixed on landing; its leg is re-stacked from v8 rows each tick",
                    "shadow": {"parts": "shadow-<side>-l<lift>", "colour": ROLES["K"], "opacity": SHADOW_OPACITY,
                               "drawn": "as a separate test-only sprite UNDER the character, also under the v8 idle "
                                        "(two v8-spot ellipses), so it never pops at the stop; the character PNGs "
                                        "contain no shadow texels"}},
        "rig": {"ground_rows": GROUND, "knee_band_rows": KNEE_BAND, "hip_row": HIP_ROW, "boot_top_row": BOOT_TOP,
                "inward_dx": INWARD, "boot_views": BOOT_VIEWS, "stance_views": list(STANCE_VIEWS), "arm_poses": ARM_SET,
                "hair_cape_dy": list(HDY), "torso_shift_dx": [-1, 0, 1], "layer_order": LAYER_ORDER,
                "pxo_layer_order": PXO_LAYERS, "torso_shift_parts": list(TORSO_SX_PARTS),
                "head_rule": "v8 rows <= 28, rows 29..33 x <= 40, chin row 34 x 32..37, neck row 35 x 34..35 (the head "
                             "part); v04: drawn at (sx, bob) like the torso, so it never shears against the neck",
                "leg_rule": "rows hip(61+bob) .. boot top-1 = thigh + v8 knee band + shin.  Shorter than v8: thigh, knee "
                            "band (min 5 rows) and shin lose whole rows in proportion (as v03).  Longer than v8 (v04): "
                            "v8's thigh rows 1:1 + the whole knee band + the shin by nearest whole-row repeat.  Knee lean "
                            "kin texels inward, thigh lean grows with t^2; the shin returns to 0 at the boot, except on a "
                            "leg longer than v8 (v04): it slopes from the knee lean to end = rdiv(cuff top-row x0 + x1 - "
                            "v8 row-84 x0 - x1, 2), row i at kin_dx + rdiv((end - kin_dx) * (i + 1), shin_rows + 1); "
                            "pinhole fill as v01; neck / shoulder seam fill (single closed holes -> ink) when the torso is "
                            "shifted (v04: fills nothing in the keyframes, gated)"},
        "gait": dict(GAIT, **gait_numbers()),
        "stop": STOP, "restart": RESTART,
        "parts": part_entries,
        "keyframes": frame_entries,
        "editable_sources": {"keyframes_pxo": pxo_name, "keyframes_pxo_sha256": hashlib.sha256(pxo).hexdigest(),
                             "keyframes_pxo_layers": PXO_LAYERS,
                             "part_library_ora": ora_name, "part_library_ora_sha256": hashlib.sha256(ora).hexdigest()},
        "metrics": {"identity_head_and_torso": identity, "forward_leg_nominal_cycle": fwd, "feasibility_sweep_legs": n_sweep,
                    "reachable_foot_states": n_states, "knee_band_foreshortening": squeezed, "bounds": bounds,
                    "nominal_contact_world_rows": contact_world, "nominal_per_px": per_px},
        "size_cost": {"part_pngs": len(part_entries), "keyframe_pngs": len(frame_entries),
                      "keyframe_shadow_pngs": len(frame_entries),
                      "part_png_bytes": sum(os.path.getsize(_fs(os.path.join(out_dir, e["file"]))) for e in part_entries),
                      "runtime_lookup": "per tick: phase = travelled window px mod stride; feet from the stance roll / "
                                        "swing keys; stop and re-press by the rules above; no sub-pixel stop table"},
    }
    mname = f"{SLUG}_protagonist-female_{PART}-manifest_{VARIANT}_{STAMP}-{fid('manifest')}.json"
    mbytes = (json.dumps(manifest, indent=1, sort_keys=False, default=list) + "\n").encode("utf-8")
    written.append(_write(out_dir, mname, mbytes))
    print(f"wrote {len(written)} files to {out_dir}")
    return manifest, frames


def make_ora(parts, part_entries, merged):
    """OpenRaster 0.0.6 part library: one layer per part, all at (0, 0) in the 80x120 cell.  Every member is STORED
    with a fixed timestamp; mimetype first.  mergedimage = the neutral (v8) composition."""
    dt = (2026, 10, 17, 21, 16, 0)
    lines = ['<?xml version="1.0" encoding="UTF-8"?>', f'<image version="0.0.6" w="{W}" h="{H}">', "  <stack>"]
    for e in reversed(part_entries):
        lines.append(f'    <layer name="{e["role"]}" src="data/{e["role"]}.png" x="0" y="0" opacity="1.000" '
                     'visibility="visible" composite-op="svg:src-over"/>')
    lines += ["  </stack>", "</image>", ""]
    merged_png = png_bytes(to_rgba(merged))
    members = [("mimetype", b"image/openraster"), ("stack.xml", "\n".join(lines).encode("utf-8"))]
    members += [(f"data/{e['role']}.png", png_bytes(to_rgba(parts[e["role"]]))) for e in part_entries]
    members += [("Thumbnails/thumbnail.png", merged_png), ("mergedimage.png", merged_png)]
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w") as z:
        for name, data in members:
            zi = zipfile.ZipInfo(name, date_time=dt)
            zi.compress_type = zipfile.ZIP_STORED
            zi.create_system = 3
            zi.external_attr = 0o100644 << 16
            z.writestr(zi, data)
    return buf.getvalue()


def preview(out_dir):
    """Scratch review only: one 4x nearest PNG per keyframe on a mid-grey floor, shadow blended at SHADOW_OPACITY."""
    v8, P = split_checked()
    parts = build_parts(v8, P)
    os.makedirs(_fs(out_dir), exist_ok=True)
    for ph in KEYFRAME_PHASES:
        layers, shadow, _ = compose(parts, nominal_state(ph))
        bg = Image.new("RGBA", (W, H), (150, 140, 128, 255))
        sh = to_rgba(shadow)
        sh[..., 3] = (sh[..., 3].astype(np.float32) * SHADOW_OPACITY).astype(np.uint8)
        bg.alpha_composite(Image.fromarray(sh, "RGBA"))
        bg.alpha_composite(Image.fromarray(to_rgba(stack(layers)), "RGBA"))
        bg.resize((W * 4, H * 4), Image.NEAREST).save(_fs(os.path.join(
            out_dir, f"{SLUG}_protagonist-female_{PART}-keyframe-{ph:02d}-review-4x-scratch_{VARIANT}_{STAMP}-{fid('preview-' + str(ph))}.png")))


def main():
    ap = argparse.ArgumentParser()
    g = ap.add_mutually_exclusive_group(required=True)
    g.add_argument("--out-dir")
    g.add_argument("--write", action="store_true")
    g.add_argument("--preview")
    a = ap.parse_args()
    if a.preview:
        d = _out_dir(a.preview)
        if _inside(d, os.path.join(REPO, "game")):
            raise SystemExit("--preview must not write under game/")
        preview(d)
    elif a.write:
        build(os.path.join(REPO, OUT_REL))
    else:
        build(_out_dir(a.out_dir))


if __name__ == "__main__":
    main()
