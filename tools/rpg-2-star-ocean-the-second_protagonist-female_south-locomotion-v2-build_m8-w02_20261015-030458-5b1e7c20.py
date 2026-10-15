"""Female protagonist - SOUTH locomotion v2 (run @ game speed + planted walk) - build and checker (M8).

Why v2 exists: walk v1 (m8-w01) slid ~44 screen px per stance at 60 px/s.  The runtime moves the
hero at MOVE_SPEED = 140 logical px/s (scifi_exploration_area.gd / survey_annex.gd) with a
time-driven 0.12 s/phase walk.  In this south view a planted foot can only "climb" ~12-16 texels
inside the 80x112 cell (6-8 logical px) before the leg collapses into the coat, so:
  * a WALK (a foot always on the ground) can only be planted if the body advances <= that climb per
    stance -> ~16 px/s at a 2 steps/s cadence (alternative B below);
  * at 140 px/s the gait must be a RUN: short ground contact (4 stance frames, 9.33 px of travel)
    matched to the in-cell climb, then flight frames where no foot is on the ground (alternative A).
Both loops are DISTANCE-keyed (frame = distance travelled, never time) and carry a tiny, bounded
root-motion offset (manifest "root_lock") that pins the planted sole to the ground in world space.

Art method (same rules as w01, no generative redraw, no resampling, filtering, flips or mirrors):
v8 is split into five texel layers (lossless re-stack gate); legs are rebuilt per pose from v8's
own thigh / knee / shin rows with integer placements, whole-row repeats/overlaps and palette-letter
boot drawings; torso rides the bob; forearm / fist pump against the legs; cape tip lags.

Usage (repository root, Codex-runtime Python 3.12 + Pillow + NumPy, run with -I):
  python -I tools/<this> --out-dir <dir>      # build into a scratch dir (determinism check)
  python -I tools/<this> --write              # build into game/assets/characters/walk-pilots-v2/
  python -I tools/<this> --check <dir>        # independent PNG-level checks -> stdout JSON
"""
import argparse, hashlib, io, json, os, sys, zipfile
import numpy as np
from PIL import Image

REPO = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
V8_REL = ("game/assets/characters/pixelorama-pilots/rpg-2-star-ocean-the-second_protagonist-female_"
          "south-idle-selout-v8-cloth-leather-candidate_m8-v08_20261015-021600-157a5ea0.png")
V8_SHA256 = "ccf9d2a293e7f1b9c706b4d2f1bf9c00b3c7714ec4e9b8bddf023e166f68b6fd"
OUT_REL = "game/assets/characters/walk-pilots-v2"
STAMP = "20261015-030458"
RUN_ID = "5b1e7c20"
VARIANT = "m8-w02"
SLUG = "rpg-2-star-ocean-the-second"
W, H = 80, 112
PIN = (40, 104)          # cell ground pin shared by every frame (same as v8 QA and w01)

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


# ----------------------------------------------------------------------------- layer split (as w01)
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


TORSO_FILL = {(18, 47): "K", (19, 47): "2", (20, 47): "2", (21, 47): "2", (22, 47): "2", (23, 47): "3", (24, 47): "K",
              (19, 52): "K", (20, 53): "K", (21, 53): "K", (22, 53): "T", (23, 53): "t", (24, 53): "t",
              (46, 53): "2", (47, 53): "2", (48, 53): "2", (49, 53): "2", (50, 53): "2", (51, 53): "K", (50, 52): "2",
              (53, 54): "K", (46, 54): "3", (46, 55): "3", (46, 56): "3"}
LEGVR_FILL = {(47, 66): "6", (47, 67): "6", (48, 67): "6", (48, 68): "6", (49, 68): "6", (50, 68): "3", (51, 68): "K",
              (49, 69): "6", (50, 69): "3", (51, 69): "K", (50, 70): "K"}

# Boots.  Row 0 = cuff row; x0 = cell column of string index 0; '.' = empty.
# vl_flat / vr_fwd are v8's own boots; the w01 redraws are reused; *_tuck are new v2 drawings of a
# foot kicked up behind the knee (seen from the front-top camera: cuff + rounded toe cap only).
BOOTS = {
    "vl_flat": (25, [
        "...qLLLLbq.", "...qLnLnbK.", "....kqbbk..", "....qbbbk..", "....qbbbk..", "...KsCbqLK.", "...KBBCLbK.",
        "...KCCqnqK.", "..KqnnbbbK.", "..nLLLbbbq.", ".nllLLqqbk.", "qLllLLqqkK.", "qbnnbqqK...", "qbqqbqK....",
        "KqbqqK.....", ".KKK......."]),
    "vl_fwd": (24, [
        "....qLLLLbq.", "....qLnLnbK.", ".....kqbbk..", ".....qbbbk..", ".....qbbbk..", "....KsCbqLK.",
        "....KBBCLbK.", "....KCCqnqK.", "...KqnnbbbK.", "...nLLLbbbq.", "..nllLLqqbk.", ".qLllLLqqkK.",
        ".qLllLLLqK..", "qLllrLLqqK..", "qbLlLLnqK...", "qbnnbbqqK...", "Kqbqqqqk....", ".qqqqqqK....",
        "..KKKKK....."]),
    "vl_heelup": (25, [
        "...qLLLLbq.", "...qLnLnbK.", "....kqbbk..", "....qbbbk..", "....qbbbk..", "...KsCbqLK.", "...KBBCLbK.",
        "...KCCqnqK.", "..KqnnbbbK.", "..nLLLbbbq.", "..qlLLqqbK.", "..qbnbqqK..", "..KqbqqK...", "...KKKK...."]),
    "vl_tuck": (25, [
        "...qLLLLbq.", "...qLnLnbK.", "...KqbbbqK.", "...KsCbqLK.", "...KbLLLbK.", "...KqnnbqK.", "....KqqqK..",
        ".....KKK..."]),
    "vr_fwd": (43, [
        "KbbnbLbK....", "qqLLLLbK....", "KqnnLLbK....", ".KnnLbqK....", "..kbbbqK....", "..Kqbbbn....",
        "..KqbCCqK...", "..KbCbqLK...", "..KbBBCKK...", "...KqCbbK...", "...KbLLLq...", "...KbLnnqK..",
        "...kqLLLLq..", "...kbLllLLK.", "...KqbllLLbK", "....KqnLrnbK", "....KbbqqqbK", ".....qqqqqqK",
        "......KKKKK."]),
    "vr_back": (43, [
        "KbbnbLbK....", "qqLLLLbK....", "KqnnLLbK....", ".KnnLbqK....", "..kbbbqK....", "..Kqbbbn....",
        "..KqbCCqK...", "..KbCbqLK...", "..KbBBCKK...", "...KqCbbK...", "...KbLLLq...", "...KbllLLK..",
        "...kqllLLq..", "...KqbLLbK..", "....KqqqK...", ".....KKK...."]),
    "vr_heelup": (43, [
        "KbbnbLbK....", "qqLLLLbK....", "KqnnLLbK....", ".KnnLbqK....", "..kbbbqK....", "..Kqbbbn....",
        "..KqbCCqK...", "..KbCbqLK...", "..KbBBCKK...", "...KqCbbK...", "...KbLLLq...", "...KblLLK...",
        "...KqbbqK...", "....KKKK...."]),
    "vr_tuck": (43, [
        "KbbnbLbK....", "qqLLLLbK....", "KqnnLLbK....", ".KqbCCqK....", ".KbLLLbK....", ".KqnnbqK....",
        "..KqqqK.....", "...KKK......"]),
}
LEG = {
    "vl": {"thigh": (61, 70), "knee": (71, 79), "fill_row": 70, "fill_extra": {26: "K"}},
    "vr": {"thigh": (61, 73), "knee": (74, 79), "fill_row": 72, "fill_extra": {}},
}


def shin_rows(sd):
    rows = [80, 81, 82, 83, 84]
    if sd > 0:
        rows = [80, 81] + [82] * (1 + sd) + [83, 84]
    if sd < 0:
        rows = [r for r in rows if r not in [83, 82, 81, 80][:-sd]]
    return rows


# ----------------------------------------------------------------------------- poses
# A leg pose: ky = cell row of the knee block top (absolute), sd = shin rows added(+)/removed(-),
# boot = variant, dx = lateral tuck of knee/shin/boot.  The thigh always hangs from the hip
# (row 61 + bob) down to ky-1 (fill-row repeats when longer, truncated under the knee when shorter).
def P(ky, sd, boot, dx=0):
    return {"ky": ky, "sd": sd, "boot": boot, "dx": dx}


# Alternative A - RUN, 12 frames / 70 logical px cycle (35 px step, 4 steps/s at 140 px/s;
# runtime walk cadence is 4.17 steps/s).
# Stance: 4 frames, each held 7/3 px = exactly one 60 fps tick at 140 px/s, climbing the planted sole
# 109 -> 104 -> 100 -> 95 (5, 4, 5 texels), so the root lock moves the body ~2.5 / 2 / 2.5 px per tick
# instead of freezing it; the 2.33 px of stance travel not covered by the climb is returned over the
# two flight frames (77/6 px each).  The swing foot stays LOWER on screen than the push-off foot (it is
# ahead of it in depth).  Planted-boot dx values keep the toe centroid within ~1 texel across stance.
STANCE_HOLD = 7.0 / 3.0
FLIGHT_HOLD = 77.0 / 6.0
RUN_VL = {   # viewer-left leg (character's right, knee guard)
    "contact": P(75, 2, "vl_fwd"), "load": P(72, 0, "vl_fwd"), "mid": P(71, 0, "vl_flat", 1),
    "push": P(70, -2, "vl_heelup", -1),
    "trail1": P(69, -3, "vl_tuck", 1), "trail2": P(68, -3, "vl_tuck", 1), "kick": P(70, -3, "vl_tuck", 1),
    "pass": P(71, -2, "vl_heelup", 1), "pass2": P(73, -2, "vl_heelup", 1), "kneeup": P(74, -3, "vl_flat", 1),
    "reach1": P(70, 0, "vl_fwd"), "reach2": P(72, 1, "vl_fwd"),
}
RUN_VR = {
    "contact": P(78, 2, "vr_fwd", -1), "load": P(75, 0, "vr_fwd", -1), "mid": P(74, 0, "vr_back", 1),
    "push": P(73, -2, "vr_heelup", 1),
    "trail1": P(72, -3, "vr_tuck", -1), "trail2": P(71, -3, "vr_tuck", -1), "kick": P(73, -3, "vr_tuck", -1),
    "pass": P(74, -2, "vr_heelup", -1), "pass2": P(76, -2, "vr_heelup", -1), "kneeup": P(77, -3, "vr_back", -1),
    "reach1": P(73, 0, "vr_fwd"), "reach2": P(75, 1, "vr_fwd"),
}
# (key, intent, bob, vr pose, vl pose, fist(dx,dy), armr(dx,dy), cape dx, hold_px, planted legs)
RUN = [
    ("run-f01-contact-vr", "vr heel lands far forward (sole 109); vl kicked up behind; fist forward",
     1, "contact", "kick", (1, 2), (0, -2), 0, STANCE_HOLD, ["vr"]),
    ("run-f02-load-vr", "vr knee bends to take the weight (sole 104); vl folds under",
     2, "load", "pass", (1, 2), (0, -1), -1, STANCE_HOLD, ["vr"]),
    ("run-f03-mid-vr", "body lowest over vr (sole 100); vl knee coming through",
     2, "mid", "pass2", (1, 1), (0, -1), -1, STANCE_HOLD, ["vr"]),
    ("run-f04-push-vr", "vr toe-off behind (sole 95); vl knee driving forward, foot ahead (sole 100)",
     1, "push", "kneeup", (0, 1), (0, 0), -1, STANCE_HOLD, ["vr"]),
    ("run-f05-flight1-vr", "airborne: vr kicks up behind, vl reaches; arms swap",
     -1, "trail1", "reach1", (0, -1), (-1, 1), 0, FLIGHT_HOLD, []),
    ("run-f06-flight2-vr", "airborne high point: vr tucked, vl extended to land",
     -2, "trail2", "reach2", (0, -2), (-1, 2), 0, FLIGHT_HOLD, []),
    ("run-f07-contact-vl", "vl heel lands far forward (sole 109); vr kicked up behind; forearm forward",
     1, "kick", "contact", (0, -2), (-1, 2), 0, STANCE_HOLD, ["vl"]),
    ("run-f08-load-vl", "vl knee bends to take the weight (sole 104); vr folds under",
     2, "pass", "load", (0, -1), (-1, 2), 1, STANCE_HOLD, ["vl"]),
    ("run-f09-mid-vl", "body lowest over vl (sole 100); vr knee coming through",
     2, "pass2", "mid", (0, -1), (-1, 1), 1, STANCE_HOLD, ["vl"]),
    ("run-f10-push-vl", "vl toe-off behind (sole 95); vr knee driving forward, foot ahead (sole 100)",
     1, "kneeup", "push", (0, 0), (0, 1), 1, STANCE_HOLD, ["vl"]),
    ("run-f11-flight1-vl", "airborne: vl kicks up behind, vr reaches; arms swap",
     -1, "reach1", "trail1", (1, 1), (0, -1), 0, FLIGHT_HOLD, []),
    ("run-f12-flight2-vl", "airborne high point: vl tucked, vr extended to land",
     -2, "reach2", "trail2", (1, 2), (0, -2), 0, FLIGHT_HOLD, []),
]

# Alternative B - PLANTED WALK, 8 frames / 16 logical px cycle (8 px step).  The planted sole climbs
# 110 -> 106 -> 102 -> 98 -> 94 (4 texels = 2 px per frame) and every frame is held for 2 px, so the
# planted foot is world-locked with ZERO root drift.  Physically consistent speed ~16 px/s (2 steps/s).
WALK_VL = {
    "contact": P(76, 2, "vl_fwd"), "down": P(73, 1, "vl_fwd"), "pass": P(73, 0, "vl_flat", 1),
    "up": P(70, -1, "vl_flat", 1), "toeoff": P(70, -3, "vl_heelup", -1), "swing1": P(71, -2, "vl_heelup", 1),
    "swing2": P(73, -2, "vl_flat", 1), "swing3": P(72, 0, "vl_fwd"),
}
WALK_VR = {
    "contact": P(79, 2, "vr_fwd", -1), "down": P(76, 1, "vr_fwd", -1), "pass": P(76, 0, "vr_back", 1),
    "up": P(73, -1, "vr_back", 1), "toeoff": P(73, -3, "vr_heelup", 1), "swing1": P(74, -2, "vr_heelup", -1),
    "swing2": P(76, -2, "vr_back", -1), "swing3": P(75, 0, "vr_fwd"),
}
WALK = [
    ("walk-f01-contact-vr", "vr heel lands forward (sole 110); vl toe-off far behind (sole 94), both planted",
     1, "contact", "toeoff", (0, 1), (0, -2), 0, 2.0, ["vr", "vl"]),
    ("walk-f02-down-vr", "weight onto vr; vl heel-up lifts", 1, "down", "swing1", (0, 1), (0, -1), -1, 2.0, ["vr"]),
    ("walk-f03-pass-vr", "vr under body; vl passes, knee forward", 0, "pass", "swing2", (0, 0), (0, 0), -1, 2.0, ["vr"]),
    ("walk-f04-up-vr", "vr behind, rising; vl reaches forward", 0, "up", "swing3", (0, -1), (-1, 1), 0, 2.0, ["vr"]),
    ("walk-f05-contact-vl", "vl heel lands forward (sole 110); vr toe-off far behind (sole 94), both planted",
     1, "toeoff", "contact", (0, -1), (-1, 1), 0, 2.0, ["vl", "vr"]),
    ("walk-f06-down-vl", "weight onto vl; vr heel-up lifts", 1, "swing1", "down", (0, -1), (-1, 1), 1, 2.0, ["vl"]),
    ("walk-f07-pass-vl", "vl under body; vr passes, knee forward", 0, "swing2", "pass", (0, 0), (0, 0), 1, 2.0, ["vl"]),
    ("walk-f08-up-vl", "vl behind, rising; vr reaches forward", 0, "swing3", "up", (0, 1), (0, -1), 0, 2.0, ["vl"]),
]
ALTS = {
    "run": {"frames": RUN, "vl": RUN_VL, "vr": RUN_VR, "speed_px_s": 140.0,
            "label": "A: run at the real game speed (MOVE_SPEED 140)"},
    "walk": {"frames": WALK, "vl": WALK_VL, "vr": WALK_VR, "speed_px_s": 16.0,
             "label": "B: planted walk at its physically consistent speed"},
}
LAYER_ORDER = ["leg-vl", "leg-vr", "torso", "arm-right-forearm", "arm-left-fist"]


# ----------------------------------------------------------------------------- helpers
def sha256_file(path):
    with open(path, "rb") as f:
        return hashlib.sha256(f.read()).hexdigest()


def load_grid(path):
    a = np.array(Image.open(path).convert("RGBA"))
    return {(x, y): INV[tuple(int(c) for c in a[y, x, :3])] for y in range(H) for x in range(W) if a[y, x, 3]}


def shift(d, dx, dy):
    return {(x + dx, y + dy): c for (x, y), c in d.items()}


def rows_of(d, y0, y1):
    return {(x, y): c for (x, y), c in d.items() if y0 <= y <= y1}


def art(rows, x0, y0):
    return {(x0 + i, y0 + j): ch for j, row in enumerate(rows) for i, ch in enumerate(row) if ch != "."}


def split_layers(v8):
    L = {"torso": {}, "fist": {}, "armr": {}, "legvl": {}, "legvr": {}}
    for (x, y), ch in v8.items():
        L[owner(x, y, ch)][(x, y)] = ch
    L["armr"][(50, 52)] = L["torso"].pop((50, 52))
    t = dict(TORSO_FILL); t.update(L["torso"]); L["torso"] = t
    r = dict(LEGVR_FILL); r.update(L["legvr"]); L["legvr"] = r
    return L


def build_leg(L, side, bob, pose):
    spec, src, out = LEG[side], L["leg" + side], {}
    t0, t1 = spec["thigh"]
    k0, k1 = spec["knee"]
    ky, sd, boot, dx = pose["ky"], pose["sd"], pose["boot"], pose.get("dx", 0)
    hip = t0 + bob
    n_src = t1 - t0 + 1
    n = ky - hip                                       # thigh rows available above the knee
    if n >= n_src:                                     # longer thigh: repeat the fill row near the bottom
        rows = list(range(t0, t1 + 1))
        cut = rows.index(spec["fill_row"])
        rows = rows[:cut] + [spec["fill_row"]] * (n - n_src + 1) + rows[cut + 1:]
    else:                                              # foreshortened thigh: knee covers the lower rows
        rows = list(range(t0, t0 + max(n, 0)))
    for i, sy in enumerate(rows):
        for (x, y), c in src.items():
            if y == sy:
                out[(x, hip + i)] = c
        if sy == spec["fill_row"] and i != rows.index(spec["fill_row"]):
            for x, c in spec["fill_extra"].items():
                out[(x, hip + i)] = c
    shin = shin_rows(sd)
    k_len = k1 - k0 + 1
    for i, sy in enumerate(shin):
        for (x, y), c in src.items():
            if y == sy:
                out[(x + dx, ky + k_len + i)] = c
    out.update(shift(rows_of(src, k0, k1), dx, ky - k0))
    x0, art_rows = BOOTS[boot]
    top = ky + k_len + len(shin)
    out.update(art(art_rows, x0 + dx, top))
    return out, top + len(art_rows) - 1


def frame_layers(L, alt, fr):
    key, intent, bob, vr_pose, vl_pose, fist, armr, cape = fr[:8]
    legs, soles = {}, {}
    legs["vl"], soles["vl"] = build_leg(L, "vl", bob, ALTS[alt]["vl"][vl_pose])
    legs["vr"], soles["vr"] = build_leg(L, "vr", bob, ALTS[alt]["vr"][vr_pose])
    torso = dict(L["torso"])
    if cape:
        tip = {(x, y): c for (x, y), c in torso.items() if 67 <= y <= 74 and x <= 20}
        for p in tip:
            del torso[p]
        moved = shift(tip, cape, 0)
        if cape < 0:
            for y in range(67, 75):
                xs = [x for (x, yy) in tip if yy == y]
                if xs:
                    moved[(max(xs), y)] = tip[(max(xs), y)]
        torso.update(moved)
    layers = {"leg-vl": legs["vl"], "leg-vr": legs["vr"], "torso": shift(torso, 0, bob),
              "arm-right-forearm": shift(L["armr"], armr[0], bob + armr[1]),
              "arm-left-fist": shift(L["fist"], fist[0], bob + fist[1])}
    # Limb swings can open single-texel pinholes where a moved limb used to cover the body.  Each is
    # closed with the most common colour of its 4 neighbours (tie: left neighbour), in the torso layer.
    g = stack(layers)
    pins = {}
    for (x, y) in [(x, y) for x in range(1, W - 1) for y in range(1, H - 1)]:
        if (x, y) not in g and all(n in g for n in ((x - 1, y), (x + 1, y), (x, y - 1), (x, y + 1))):
            ns = [g[(x - 1, y)], g[(x + 1, y)], g[(x, y - 1)], g[(x, y + 1)]]
            pins[(x, y)] = max(ns, key=lambda c: (ns.count(c), c == ns[0]))
    layers["torso"].update(pins)
    soles["pinholes_closed"] = len(pins)
    return layers, soles


IDLE_POSE = {"vl": P(71, 0, "vl_flat"), "vr": P(74, 0, "vr_fwd")}


def stack(layers):
    g = {}
    for name in LAYER_ORDER:
        g.update(layers[name])
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


def frame_name(key):
    return f"{SLUG}_protagonist-female_south-locomotion-v2-{key}_{VARIANT}_{STAMP}-{fid(key)}.png"


def pxo_name(alt):
    return f"{SLUG}_protagonist-female_south-locomotion-v2-{alt}-editable_{VARIANT}_{STAMP}-{fid('pxo-' + alt)}.pxo"


MANIFEST_NAME = f"{SLUG}_protagonist-female_south-locomotion-v2-manifest_{VARIANT}_{STAMP}-{fid('manifest')}.json"


# ----------------------------------------------------------------------------- root lock model
def root_lock(frames_meta):
    """Per-frame root offset r (logical px, + = sprite drawn further south than the logical position).

    Within a frame that has a planted leg the sprite is frozen (r falls 1:1 with distance), and at a
    frame change the sprite moves by exactly the planted sole's in-cell climb / 2, so that sole never
    moves on screen.  Flight frames ramp r linearly back so the loop is periodic.  r0 is chosen so the
    offset is centred on 0.  Returns per-frame (r_start, slope) with r(s_local) = r_start + slope*s_local.
    """
    n = len(frames_meta)
    # pass 1: relative r with r_start[0] = 0
    starts, slopes = [0.0] * n, [0.0] * n
    r = 0.0
    flight = [i for i, f in enumerate(frames_meta) if not f["planted"]]
    for i, f in enumerate(frames_meta):
        starts[i] = r
        if f["planted"]:
            slopes[i] = -1.0
            r -= f["hold_px"]
            nxt = frames_meta[(i + 1) % n]
            carried = [leg for leg in f["planted"] if leg in nxt["planted"]]
            if carried:
                leg = carried[0]
                r += (f["sole"][leg] - nxt["sole"][leg]) / 2.0
    # r is now the drift over one cycle with flight frames at slope 0 -> spread it over flight frames
    drift = r
    if abs(drift) > 1e-9:
        if not flight:
            raise SystemExit(f"walk loop is not periodic: root drift {drift} px per cycle with no flight frame")
        fdist = sum(frames_meta[i]["hold_px"] for i in flight)
        r = 0.0
        for i, f in enumerate(frames_meta):
            starts[i] = r
            if f["planted"]:
                r -= f["hold_px"]
                nxt = frames_meta[(i + 1) % n]
                carried = [leg for leg in f["planted"] if leg in nxt["planted"]]
                if carried:
                    r += (f["sole"][carried[0]] - nxt["sole"][carried[0]]) / 2.0
            else:
                slopes[i] = -drift / fdist
                r += slopes[i] * f["hold_px"]
        assert abs(r) < 1e-9
    # centre
    ends = [starts[i] + slopes[i] * frames_meta[i]["hold_px"] for i in range(n)]
    mid = (max(starts + ends) + min(starts + ends)) / 2.0
    return [round(s - mid, 4) for s in starts], [round(s, 6) for s in slopes]


# ----------------------------------------------------------------------------- pxo
def make_pxo(per_frame_layers, preview_png, fname, fps):
    layer_json = [{"animated_params": "Dictionary[String, Dictionary]({\n\"opacity\": {}\n})", "blend_mode": 0,
                   "clipping_mask": False, "effects": [], "locked": False, "metadata": {}, "name": n,
                   "new_cels_linked": False, "opacity": 1.0, "parent": -1, "type": 0,
                   "ui_color": "(0.0, 0.0, 0.0, 0.0)", "visible": True} for n in LAYER_ORDER]
    frames_json = [{"cels": [{"metadata": {}, "opacity": 1.0, "ui_color": "(0.0, 0.0, 0.0, 0.0)", "z_index": 0}
                             for _ in LAYER_ORDER], "duration": 1.0, "metadata": {}} for _ in per_frame_layers]
    export_profile = {"crop_mode": "0", "current_tab": "0", "direction": "0", "directory_path": "\"\"",
                      "erase_unselected_area": "false", "export_json": "false", "export_layers": "0",
                      "file_format": "0", "file_name": json.dumps(fname), "frame_current_tag": "0",
                      "include_tag_in_filename": "false", "interpolation": "0", "lines_count": "1",
                      "new_dir_for_each_frame_tag": "false", "number_of_digits": "4", "number_of_frames": "1",
                      "orientation": "0", "repeat_count": "0", "resize": "100", "save_quality": "0.75",
                      "separator_character": "\"_\"", "sheet_layers_as_separate_files": "false",
                      "split_layers": "false"}
    data = {"author_company": "", "author_contact": "", "author_display_name": "", "author_real_name": "",
            "brushes": [], "color_mode": 5, "current_frame": 0, "current_layer": 2, "export_profile": export_profile,
            "fps": fps, "frames": frames_json, "guides": [], "layers": layer_json, "license": "", "metadata": {},
            "next_keyframe_id": 0, "palettes": [], "pixelorama_version": "v1.2.3-stable",
            "project_current_palette_name": "", "pxo_version": 7, "reference_images": [], "size_x": W, "size_y": H,
            "symmetry_points": [W - 1.0, H - 1.0], "tags": [], "tile_mode_x_basis_x": W, "tile_mode_x_basis_y": 0,
            "tile_mode_y_basis_x": 0, "tile_mode_y_basis_y": H, "tilesets": [], "user_data": "",
            "vanishing_points": []}
    buf = io.BytesIO()
    dt = (2026, 10, 15, 3, 4, 58)
    with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as z:
        def put(name, payload):
            z.writestr(zipfile.ZipInfo(name, dt), payload, zipfile.ZIP_DEFLATED)
        put("data.json", json.dumps(data, separators=(",", ":")))
        put("mimetype", "application/x-pixelorama")
        put("preview.png", preview_png)
        for fi, layers in enumerate(per_frame_layers, start=1):
            put(f"image_data/frames/{fi}/", b"")
            for li, name in enumerate(LAYER_ORDER, start=1):
                put(f"image_data/frames/{fi}/layer_{li}", to_rgba(layers[name]).tobytes())
                put(f"image_data/frames/{fi}/indices_layer_{li}", b"\x00")
    return buf.getvalue()


# ----------------------------------------------------------------------------- build
def build(out_dir):
    v8_path = os.path.join(REPO, V8_REL)
    if sha256_file(v8_path) != V8_SHA256:
        raise SystemExit("v8 source SHA-256 mismatch; refusing to build")
    v8 = load_grid(v8_path)
    L = split_layers(v8)
    idle = {"leg-vl": build_leg(L, "vl", 0, IDLE_POSE["vl"])[0], "leg-vr": build_leg(L, "vr", 0, IDLE_POSE["vr"])[0],
            "torso": L["torso"], "arm-right-forearm": L["armr"], "arm-left-fist": L["fist"]}
    if stack(idle) != v8:
        raise SystemExit("layer split / leg rebuild is not lossless: idle re-stack differs from v8")
    os.makedirs(out_dir, exist_ok=True)
    written, alts_meta = [], {}
    for alt, spec in ALTS.items():
        frames_meta, per_frame_layers, previews = [], [], []
        for order, fr in enumerate(spec["frames"], start=1):
            key, intent, bob, vr_pose, vl_pose, fist, armr, cape, hold, planted = fr
            layers, soles = frame_layers(L, alt, fr)
            pinholes = soles.pop("pinholes_closed")
            overlap = len(set(layers["leg-vl"]) & set(layers["leg-vr"]))
            if overlap:
                raise SystemExit(f"{key}: leg layers overlap ({overlap}); fixed .pxo layer order would not reproduce PNG")
            data = png_bytes(to_rgba(stack(layers)))
            name = frame_name(key)
            written.append(_write(out_dir, name, data))
            per_frame_layers.append(layers)
            previews.append(data)
            frames_meta.append({"order": order, "key": key, "intent": intent, "file": name,
                                "sha256": hashlib.sha256(data).hexdigest(), "bytes": len(data),
                                "bob": bob, "pose": {"vr": vr_pose, "vl": vl_pose, "fist": list(fist), "armr": list(armr),
                                                     "cape": cape},
                                "sole": soles, "planted": planted, "hold_px": hold, "pinholes_closed": pinholes})
        r0, slope = root_lock(frames_meta)
        for f, a, b in zip(frames_meta, r0, slope):
            f["root_lock"] = {"r_start_px": a, "slope": b}
        cycle = sum(f["hold_px"] for f in frames_meta)
        fps = round(spec["speed_px_s"] / cycle * len(frames_meta), 3)
        pxo = make_pxo(per_frame_layers, previews[0], f"protagonist-female-south-locomotion-v2-{alt}", fps)
        written.append(_write(out_dir, pxo_name(alt), pxo))
        alts_meta[alt] = {"label": spec["label"], "speed_logical_px_s": spec["speed_px_s"],
                          "cycle_logical_px": cycle, "steps_per_cycle": 2,
                          "steps_per_s": round(spec["speed_px_s"] / (cycle / 2), 3),
                          "mean_frame_rate_fps": fps,
                          "planted_distance_px_per_step": sum(f["hold_px"] for f in frames_meta if f["planted"]) / 2,
                          "loop": [f["key"] for f in frames_meta], "frames": frames_meta,
                          "editable": {"file": pxo_name(alt), "sha256": hashlib.sha256(pxo).hexdigest(),
                                       "format": f"Pixelorama pxo_version 7 (v1.2.3), {len(frames_meta)} frames x 5 layers"}}
    manifest = {
        "project": "Worlds Between", "milestone": "M8", "variant": VARIANT,
        "purpose": "Female protagonist south locomotion v2: distance-keyed, root-locked run at the real 140 px/s and a planted walk alternative, from approved static selout v8.",
        "status": "technical prototype for human review; unapproved; not runtime-integrated",
        "art_approved": False, "human_reviewed": False, "runtime_integrated": False,
        "gates_changed": "none",
        "supersedes_for_review": "walk-pilots/ m8-w01 (left immutable)",
        "source": {"file": V8_REL, "sha256": V8_SHA256, "role": "read-only, source-locked; v8 approved as STATIC 48 px baseline only"},
        "builder": {"script": os.path.relpath(os.path.abspath(__file__), REPO).replace("\\", "/"),
                    "python": sys.version.split()[0], "pillow": Image.__version__, "numpy": np.__version__},
        "cell": [W, H], "ground_pin_cell": list(PIN),
        "display": {"logical_height_px": 48, "scale": 0.5, "texel_to_screen_px_at_1280x720": 1, "filter": "nearest"},
        "runtime_grounding": {"MOVE_SPEED_logical_px_s": 140.0,
                              "source": "game/scripts/scifi_exploration_area.gd and survey_annex.gd (const MOVE_SPEED := 140.0)",
                              "runtime_walk": "time-driven 4 phases x 0.12 s (step 33.6 px at 140 px/s); unchanged"},
        "locomotion_model": {
            "frame_selection": "distance-keyed: s = distance travelled mod cycle; frame = cumulative hold_px table",
            "root_lock": "draw_y = logical_y + r_start_px + slope * s_in_frame (logical px). slope -1 freezes the sprite while a foot is planted; at frame changes the sprite moves by the planted sole's climb/2; flight frames ramp r back.",
            "sole": "lowest opaque cell row of each leg's boot as built (texels; 2 texels = 1 logical px)"},
        "alternatives": alts_meta,
        "layer_order_back_to_front": LAYER_ORDER,
        "files_added": [os.path.basename(p) for p in written] + [MANIFEST_NAME],
    }
    written.append(_write(out_dir, MANIFEST_NAME, (json.dumps(manifest, indent=1) + "\n").encode()))
    for p in written:
        print("WROTE", os.path.basename(p), sha256_file(p))


def _write(out_dir, name, data):
    path = os.path.join(out_dir, name)
    if os.path.exists(path):
        with open(path, "rb") as f:
            if f.read() != data:
                raise SystemExit(f"refusing to overwrite different bytes: {path}")
    else:
        with open(path, "wb") as f:
            f.write(data)
    return path


# ----------------------------------------------------------------------------- independent checks
KNEE_GUARD = set("OGzgv")


def check(frame_dir):
    """Reads only the PNGs (frames + v8) and the .pxo files on disk."""
    v8a = np.array(Image.open(os.path.join(REPO, V8_REL)).convert("RGBA"))
    v8_cols = {tuple(c) for c in v8a[v8a[..., 3] > 0][:, :3].tolist()}
    res = {"alternatives": {}}
    all_hashes = []
    for alt, spec in ALTS.items():
        out = []
        for fr in spec["frames"]:
            key = fr[0]
            p = os.path.join(frame_dir, frame_name(key))
            im = Image.open(p)
            a = np.array(im.convert("RGBA"))
            op = a[..., 3] > 0
            ys, xs = np.nonzero(op)
            cols = {tuple(c) for c in a[op][:, :3].tolist()}
            r = {"key": key, "size": list(im.size), "alpha_values": sorted(set(np.unique(a[..., 3]).tolist())),
                 "border_opaque": int(op[0].sum() + op[-1].sum() + op[:, 0].sum() + op[:, -1].sum()),
                 "colours": len(cols), "colours_outside_v8": len(cols - v8_cols),
                 "visible_height": int(ys.max() - ys.min() + 1), "top_row": int(ys.min()), "lowest_row": int(ys.max())}
            bob = None
            for dy in range(-3, 4):
                if np.array_equal(np.roll(v8a, dy, axis=0)[8 + dy:34 + dy], a[8 + dy:34 + dy]):
                    bob = dy
                    break
            r["bob_found_by_head_search"] = bob
            mism = 0
            if bob is not None:
                sh = np.roll(v8a, bob, axis=0)
                for y in range(8 + bob, 53 + bob):
                    for x in range(W):
                        if 16 <= x <= 26 and 44 + bob <= y <= 57 + bob:
                            continue
                        if 44 <= x <= 55 and 49 + bob <= y:
                            continue
                        if not np.array_equal(sh[y, x], a[y, x]):
                            mism += 1
            r["locked_upper_body_mismatch_texels"] = mism
            r["sole_row_vl"] = int(max(y for y, x in zip(ys, xs) if y >= 78 and x < 38))
            r["sole_row_vr"] = int(max(y for y, x in zip(ys, xs) if y >= 78 and x >= 38))
            kg = [(x, y) for y, x in zip(ys, xs) if 64 <= y <= 90 and x < 40
                  and INV.get(tuple(int(c) for c in a[y, x, :3])) in KNEE_GUARD]
            r["knee_guard_texels"] = len(kg)
            r["knee_guard_on_viewer_left"] = bool(kg) and float(np.mean([p[0] for p in kg])) < PIN[0]
            # interior holes: transparent texels enclosed left+right and above+below by opaque ones in rows 40-100
            holes = 0
            for y in range(40, 101):
                row = op[y]
                if not row.any():
                    continue
                for x in range(1, W - 1):
                    if not row[x] and row[:x].any() and row[x + 1:].any() and op[:y, x].any() and op[y + 1:, x].any():
                        if op[y, x - 1] and op[y, x + 1] and op[y - 1, x] and op[y + 1, x]:
                            holes += 1
            r["single_texel_pinholes"] = holes
            r["identical_to_v8"] = bool(np.array_equal(a, v8a))
            out.append(r)
            all_hashes.append(sha256_file(p))
        with zipfile.ZipFile(os.path.join(frame_dir, pxo_name(alt))) as z:
            d = json.loads(z.read("data.json"))
            ok = []
            for fi, fr in enumerate(spec["frames"], start=1):
                comp = np.zeros((H, W, 4), np.uint8)
                for li in range(1, len(d["layers"]) + 1):
                    cel = np.frombuffer(z.read(f"image_data/frames/{fi}/layer_{li}"), np.uint8).reshape(H, W, 4)
                    m = cel[..., 3] > 0
                    comp[m] = cel[m]
                ok.append(bool(np.array_equal(comp, np.array(Image.open(os.path.join(frame_dir, frame_name(fr[0]))).convert("RGBA")))))
        res["alternatives"][alt] = {"frames": out, "pxo": {"frames": len(d["frames"]), "pxo_version": d["pxo_version"],
                                                           "restack_equals_png_per_frame": ok}}
    res["all_frames_unique"] = len(set(all_hashes)) == len(all_hashes)
    res["v8_unchanged"] = sha256_file(os.path.join(REPO, V8_REL)) == V8_SHA256
    return res


def main():
    ap = argparse.ArgumentParser()
    g = ap.add_mutually_exclusive_group(required=True)
    g.add_argument("--out-dir")
    g.add_argument("--write", action="store_true")
    g.add_argument("--check")
    args = ap.parse_args()
    if args.check:
        print(json.dumps(check(args.check), indent=1))
        return
    build(args.out_dir or os.path.join(REPO, OUT_REL))


if __name__ == "__main__":
    main()
