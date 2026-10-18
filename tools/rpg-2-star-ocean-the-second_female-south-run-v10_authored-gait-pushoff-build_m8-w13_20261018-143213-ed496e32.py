"""Female protagonist SOUTH RUN v10: ONE authored gait + push-off revision (m8-w13).

UNAPPROVED / NONRUNTIME, test-only, single direction.  Not art acceptance, not runtime integration, not a production
sprite.  The creator approved only the selout v8 SOUTH IDLE static frame and the 48 logical px display scale.

Why v10: v09 (a drawing-only fork of the v07 control candidate) kept v07's rhythm - 6.67 steps/s, 50 % of the cycle with
both boots off the floor - so the creator's rhythm objection ("smooth, fluid, well paced") was not addressed.  v10 is one
deliberate new design (not a parameter search) built on the v09 art sources (read-only, hash-pinned; v09 is preserved as a
partial fork):

  * GAIT (units: window px = source texels at the 0.5 display scale; MOVE_SPEED 140 logical px/s = 280 window px/s,
    unchanged): stride 128 px (two 64 px steps) = 4.375 steps/s; stance 44 px per boot = 157 ms; flight 20 px = 71 ms per
    step; at least one boot on the floor 88 / 128 = 68.75 % of the cycle (v07: 50 %).  The planted boot keeps its window
    row (zero slip) over the whole 44 px stance: it lands 12 rows in front of its v8 spot and leaves 32 rows behind it.
  * ONE LEG RULE for every state (contact, swing, stop, re-press): the leg is drawn from the hip down to the boot by its
    available length n (rows between the hip and the boot top).  Long (n >= v8's 24): the reaching / landing leg - thigh
    and shin both stretch by whole-row repeats, the shin slopes onto the cuff.  Medium: v06's proportional foreshortening.
    Short (n < 8, the rear push-off and the tucked swing): the leg holds its 8-row folded shape and the boot is drawn
    BEHIND it - the rear foot slides up behind the knee as the body passes over it (its world row never moves) and the
    swinging foot comes back out from under the knee.  Boot texels on the hips rows are never drawn.
  * AUTHORED PARTS: push-off boots (boot-<side>-toe, v8 shaft + a heel-high toe planted into the floor, the same 14-row
    height as the heel-up boot so the roll heel-up -> push does not move the leg); v09's kick boots and forward-knee bands
    (read-only) are used for the swing tuck.
  * SWING (new key table): toe-off -> heel kick (sole under the knee) -> knee-forward tuck, the foot hanging under the
    knee and unfolding -> open reach toward the camera -> heel strike 12 rows in front.
  * TORSO COMPRESSION: the body drops 1 row after touchdown, 2 rows through mid-stance and rises again for the push-off
    (bob levels by px since landing; never more than one row per frame).  Torso / head / arms shift toward the planted
    boot for most of the longer stance.  Arms keep the v06 poses, re-timed to the 128 px cycle.
  * COAT TRAILING: the coat panels below row 66 trail the torso shift (v09 csx) AND the body's vertical bob by the hair
    lag (hdy), so the hem lags the compression and the rise; a hem one row low repeats its top row (no gap row).
  * v09 seam close kept: transparent texels enclosed on four sides below the neck are closed with outline ink.
  * STOP / RE-PRESS: v06's event-clock stop and v07's re-press rule + rise lock, on the v10 offsets; Root relaxed exact
    v07 timing parity (settle <= 250 ms at 30 / 60 fps, <= 300 ms mixed; raised boot <= 100 ms; final frame = v8).

Writes (only with --out-dir): new part PNGs, 16 keyframe + 16 shadow PNGs, the keyframes .pxo (Pixelorama 1.2.3, 13
layers incl. the shadow), the new-parts .ora, the gait / pose manifest (incl. a sha256 of every per-px nominal
composite, so the GDScript port is checked on all 128 phases, not only on the keyframes).
--preview <dir> writes scratch review PNGs (outside the repository only).

Usage (repository root):
  python -I -B tools/<this file> --out-dir game/assets/characters/run-v10-unapproved
  python -I -B tools/<this file> --preview <abs scratch dir>
"""
import argparse, hashlib, importlib.util, io, json, os, sys, zipfile

import numpy as np
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(HERE)
V09_BUILDER = "rpg-2-star-ocean-the-second_female-south-run-v09_authored-gait-build_m8-w12_20261018-133700-4d620536.py"
V09_BUILDER_SHA256_TEXT_LF = "dc9c2705f44c87ea"   # prefix pinned in the v09 QA note; full digest recorded in the manifest
V09_MANIFEST_REL = ("game/assets/characters/run-v09-unapproved/rpg-2-star-ocean-the-second_female-south-run-v09_"
                    "pose-gait-manifest_unapproved_20261018-133700-39dc1e43.json")
OUT_REL = "game/assets/characters/run-v10-unapproved"
SLUG = "rpg-2-star-ocean-the-second"
PART = "female-south-run-v10"
VARIANT = "unapproved"
STAMP = "20261018-143213"
RUN_ID = "ed496e32"
REPO_PATH_LIMIT = 250


def _fs(path):
    path = os.path.abspath(path)
    if os.name == "nt" and len(path) > 247 and not path.startswith("\\\\?\\"):
        return "\\\\?\\" + path
    return path


def sha_text_lf(path):
    with open(_fs(path), "rb") as f:
        return hashlib.sha256(f.read().replace(b"\r\n", b"\n")).hexdigest()


def load_v09():
    path = os.path.join(HERE, V09_BUILDER)
    digest = sha_text_lf(path)
    if not digest.startswith(V09_BUILDER_SHA256_TEXT_LF):
        raise SystemExit(f"v09 builder is not the pinned file ({digest[:16]})")
    spec = importlib.util.spec_from_file_location("v09_builder", path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)          # the v09 module pins the v06 builder + v06 manifest itself
    return mod, digest


b9, V09_BUILDER_DIGEST = load_v09()
b6 = b9.b6
W, H = b6.W, b6.H
rdiv, shift, pick, rnd = b6.rdiv, b6.shift, b6.pick, b6.rnd
GROUND, KNEE_BAND, HIP_ROW, BOOT_TOP, INWARD = b6.GROUND, b6.KNEE_BAND, b6.HIP_ROW, b6.BOOT_TOP, b6.INWARD


def fid(role):
    return hashlib.sha256(f"{RUN_ID}:{role}".encode()).hexdigest()[:8]


# ===================================================================================================== v10 gait
SD, E, A = 128, 44, 12
BK = A - E                       # -32: lift-off offset
GAIT10 = {
    "stride_px": SD, "stance_px": E, "land_offset": A, "liftoff_offset": BK,
    "phase_offset_px": {"vl": 0, "vr": SD // 2},
    # q (px since touchdown) -> boot view from this q on; the v8 view covers q = land_offset (o = 0) exactly
    "stance_roll": [[0, "strike"], [4, "v8"], [26, "heelup"], [34, "toe"]],
    "stance_knee_kin": [[0, 1], [A, 0]],
    # torso compression: body rows down by q since touchdown (0 before 2: the landing frame is not yet loaded); every
    # level lasts >= 10 px so a 30 fps tick (9.3 px) never skips one (the driver also steps the bob one row per tick)
    "bob_levels": [[0, 0], [2, 1], [12, 2], [24, 1], [34, 0]],
    "bob_stance_q": [2, 34],                          # (v06 field, informative: the q range with any compression)
    "torso_shift_stance_q": [4, 32],
    "arm_peak_px": {"L": 14, "R": 85},                # v06 9 / 56 on 84 px, x 128 / 84
    "arm_pose_bands_px": [11, 24, 40, 53],            # v06 7 / 16 / 26 / 35, x 128 / 84
    "hair_lag_px": 10, "cape_shift_lag_px": 10,       # nominal table only (the driver lags by hair_lag_ms = 34)
    # (u per mille of the 84 px swing, o, lift, view from this key on, knee lean).  Lowest drawn row (vl) along the
    # swing: 69 (toe-off, behind the knee) -> 70..80 (kick: sole under the knee) -> 78..92 (hang: foot under the knee,
    # unfolding) -> 92..107 (reach) -> 111 (strike) -> touchdown at 112 (o = +12).
    "swing_keys": [
        [0, BK, 1, "toe", 0],
        [100, -30, 3, "kick", 1],
        [250, -25, 4, "kick", 1],
        [380, -19, 4, "hang", 1],
        [520, -12, 4, "hang", 1],
        [650, -5, 3, "reach", 1],
        [780, 2, 2, "reach", 1],
        [900, 8, 1, "strike", 1],
        [1000, A, 1, "strike", 1],
    ],
}
SPEED_WINDOW_PX_S = 280
STOP10 = dict(b6.STOP)
STOP10.update({
    "v10_note": "v06 event-clock stop rule unchanged; ONE duration re-tuned: land_ms_max 70 -> 60, so a boot released "
                "high in the swing (o -22, lift 4) lands in two 30 fps frames, not three (with 70 ms three 30 fps stops "
                "released in early stance took 266.7 ms; Root relaxed exact v07 timing parity: settle <= 250 ms at "
                "30 / 60 fps, <= 300 ms mixed frame times, raised boot <= 100 ms)",
    "land_ms_base": 34, "land_ms_per_px": 1, "land_ms_per_lift": 4, "land_ms_max": 60,
    "shuffle_ms_base": 34, "shuffle_ms_per_px": 1, "shuffle_ms_max": 56,
})
RESTART10 = dict(b6.RESTART)
RESTART10.update({"replan_lift_min": 2, "replan_lift_max": 4, "v07_rise_lock": True})

STANCE_VIEWS = ("strike", "v8", "heelup", "toe")
TUCK_VIEWS = ("kick", "hang")      # swing views drawn with the v09 forward knee, boot behind the leg
N_FOLD = 8                         # rows of the folded leg; a shorter room puts the boot behind the leg
HIPS_BOTTOM = 66                   # boot texels on rows <= this (+ bob) are never drawn (behind the hips / coat)
COAT_HEM_ROW = b9.COAT_HEM_ROW     # 66
SEAM_ROW0 = b9.SEAM_ROW0           # 41
ISLAND_MAX = 12                    # a leg-only fragment up to this size, cut off from the body, is dropped (behind the coat)

# ===================================================================================================== authored parts
# push-off boot (heel high behind, toe planted into the floor), drawn below v8's 8-row shaft (the same 14-row height as
# the heel-up boot, so the heel-up -> push roll does not change the leg).  x offsets from the cuff-centred left edge.
PUSH_FOOT = {
    "vl": [(-1, "KqnnbbbK"), (0, "KnLLLqK"), (0, "KlLLqbK"), (1, "KlrqK"), (1, "KqbK"), (1, "KKK")],
    "vr": [(1, "KqCbbK"), (1, "KbLLLqK"), (1, "KbLlqK"), (2, "KqLrK"), (2, "KqbK"), (2, "KKK")],
}


def rows_to_texels(rows, x0, y0):
    return {(x0 + o + i, y0 + j): ch for j, (o, r) in enumerate(rows) for i, ch in enumerate(r) if ch not in ". "}


def lowest_centre(part):
    y = max(yy for (_, yy) in part)
    xs = [x for (x, yy) in part if yy == y]
    return (min(xs) + max(xs)) / 2


def push_part(side, parts):
    """v8 shaft + PUSH_FOOT, lowest row on GROUND, its lowest-row centre on the heel-up boot's (the roll keeps the toe)."""
    rows = list(b6.SHAFT[side]) + PUSH_FOOT[side]
    probe = rows_to_texels(rows, 0, GROUND[side] - len(rows) + 1)
    dx = rnd(lowest_centre(parts[f"boot-{side}-heelup"]) - lowest_centre(probe))
    return shift(probe, dx, 0)


# ===================================================================================================== leg rule
def leg_plan(side, n, tuck):
    """(thigh source rows, knee source rows, shin source rows, mode) for n rows between the hip and the boot top."""
    k0, k1 = KNEE_BAND[side]
    T, K, S = list(range(HIP_ROW, k0)), list(range(k0, k1 + 1)), list(range(k1 + 1, BOOT_TOP))
    full = len(T) + len(K) + len(S)
    if n >= full:
        e = n - full
        et = rdiv(e * len(T), len(T) + len(S))
        return pick(T, len(T) + et), K, pick(S, len(S) + e - et), "long"
    mode = "medium" if n >= N_FOLD else "folded"
    m = max(n, N_FOLD)
    nk = max(b6.KNEE_MIN_ROWS, rdiv(m * len(K), full))
    nt = max(1, rdiv((m - nk) * len(T), len(T) + len(S)))
    ns = m - nk - nt
    if ns < 1:
        nt, ns = nt - (1 - ns), 1
    return pick(T, nt), pick(K, nk), pick(S, ns), mode


def compose_leg10(parts, side, bob, foot):
    view = foot["view"]
    dy = foot["o"] - foot["lift"]
    boot = shift(parts[f"boot-{side}-{view}"], 0, dy)
    bt = min(y for (_, y) in boot)
    n = bt - (HIP_ROW + bob)
    tuck = view in TUCK_VIEWS
    th, kn, sh, mode = leg_plan(side, n, tuck)
    src = b6.rows_of_part(parts[f"leg-src-{side}"])
    ksrc = b6.rows_of_part(parts[f"knee-{side}-fwd"]) if tuck else src
    cuff = [x for (x, y) in boot if y == bt]
    kd = foot["kin"] * INWARD[side]
    if tuck and len(sh) < 4:
        # v09: a short shin puts the knee over the cuff (thigh leans toward it)
        kb = list(ksrc[KNEE_BAND[side][1]])
        kd += rdiv(rdiv(min(cuff) + max(cuff) - min(kb) - max(kb), 2) * (4 - len(sh)), 4)
    out = {}
    y = HIP_ROW + bob
    for i, sy in enumerate(th):
        dx = rdiv(kd * i * i, (len(th) - 1) ** 2) if len(th) > 1 else 0
        for x, c in src.get(sy, {}).items():
            out[(x + dx, y)] = c
        y += 1
    for sy in kn:
        for x, c in ksrc.get(sy, {}).items():
            out[(x + kd, y)] = c
        y += 1
    end = kd
    if mode == "long" and len(sh) > BOOT_TOP - 1 - KNEE_BAND[side][1]:
        srow = list(src.get(BOOT_TOP - 1, {}))
        end = rdiv(min(cuff) + max(cuff) - min(srow) - max(srow), 2)
    elif mode == "medium" and not tuck:
        end = 0                                          # v06: the shin returns to v8's x at the boot
    for i, sy in enumerate(sh):
        dx = kd + rdiv((end - kd) * (i + 1), len(sh) + 1)
        for x, c in src.get(sy, {}).items():
            out[(x + dx, y)] = b9.SHIN_SHADE.get(c, c) if tuck else c
        y += 1
    vis = {q: c for q, c in boot.items() if q[1] > HIPS_BOTTOM + bob}
    if mode == "folded" or tuck:
        full = dict(vis)
        full.update(out)              # the boot behind the leg (rear push-off, tucked swing)
    else:
        full = dict(out)
        full.update(vis)
    return full, boot, GROUND[side] + dy, {"mode": mode, "n": n}


LEG_INFO = {}


def _leg_hook(parts, side, bob, foot):
    full, boot, sole, info = compose_leg10(parts, side, bob, foot)
    LEG_INFO[side] = info
    return full, boot, sole


def components8(grid):
    """8-connected components of the opaque texels, smallest first (ties: top-left first, deterministic)."""
    pts, out = set(grid), []
    for s in sorted(grid, key=lambda q: (q[1], q[0])):
        if s not in pts:
            continue
        pts.discard(s)
        st, c = [s], {s}
        while st:
            x, y = st.pop()
            for dy in (-1, 0, 1):
                for dx in (-1, 0, 1):
                    q = (x + dx, y + dy)
                    if q in pts:
                        pts.discard(q)
                        c.add(q)
                        st.append(q)
        out.append(c)
    return sorted(out, key=len)


def compose10(parts, state):
    """b6.compose with the v10 leg, the coat hem lagging (csx, hdy), and the v09 enclosed-seam ink fill."""
    b, sx, csx, h = state["bob"], state["sx"], state["csx"], state["hdy"]
    coat = {}
    for (x, y), c in sorted(parts["coat-skirt"].items(), key=lambda kv: (kv[0][1], kv[0][0])):   # row-major (GDScript order)
        if y >= COAT_HEM_ROW:
            coat[(x + csx, y + b + h)] = c
            if h > 0 and y == COAT_HEM_ROW:
                coat[(x + csx, y + b)] = c          # the hem one row low repeats its top row (no gap row)
        else:
            coat[(x + sx, y + b)] = c
    saved_leg, saved_shift = b6.compose_leg, b6.shift
    src_coat = parts["coat-skirt"]

    def shift_hook(d, dx, dy):
        return dict(coat) if d is src_coat else saved_shift(d, dx, dy)
    b6.compose_leg, b6.shift = _leg_hook, shift_hook
    try:
        layers, shadow, info = b6.compose(parts, state)
    finally:
        b6.compose_leg, b6.shift = saved_leg, saved_shift
    g = b6.stack(layers)
    fill = {(x, y): "K" for y in range(SEAM_ROW0, H - 1) for x in range(1, W - 1)
            if (x, y) not in g and (x - 1, y) in g and (x + 1, y) in g and (x, y - 1) in g and (x, y + 1) in g}
    layers["torso"].update(fill)
    info["v09_seam_filled"] = len(fill)
    # v10: the tucked swing thigh can peek past the coat edge as a few texels cut off from the body by a transparent gap;
    # such leg-only fragments (8-connected, <= ISLAND_MAX texels, not the body) are behind the coat and are not drawn
    legpos = set(layers["leg-far"]) | set(layers["leg-near"])
    comps = components8(b6.stack(layers))
    dropped = 0
    for c in comps[:-1]:
        if len(c) <= ISLAND_MAX and c <= legpos:
            for q in c:
                for l in layers.values():
                    l.pop(q, None)
            dropped += len(c)
    info["v10_leg_islands_dropped"] = dropped
    info["leg_modes"] = {s: dict(LEG_INFO[s]) for s in ("vl", "vr")}
    return layers, shadow, info


# ===================================================================================================== nominal gait
def interp_keys(keys, u):
    return b6.interp_keys(keys, u)


def stance_view(q):
    v = None
    for q0, name in GAIT10["stance_roll"]:
        if q >= q0:
            v = name
    return v


def stance_kin(q):
    k = 0
    for q0, kk in GAIT10["stance_knee_kin"]:
        if q >= q0:
            k = kk
    return k


def bob_level(q):
    lv = 0
    for q0, b in GAIT10["bob_levels"]:
        if q >= q0:
            lv = b
    return lv


def in_contact(f):
    return f["lift"] == 0 and f["view"] in STANCE_VIEWS


def nominal_foot(side, phase):
    q = (phase - GAIT10["phase_offset_px"][side]) % SD
    if q < E:
        return {"o": A - q, "lift": 0, "view": stance_view(q), "kin": stance_kin(q)}, q
    u = rdiv(1000 * (q - E), SD - E)
    o, lift, view, kin = interp_keys(GAIT10["swing_keys"], u)
    return {"o": o, "lift": lift, "view": view, "kin": kin}, q


def nominal_bob(phase):
    b = 0
    for s in ("vl", "vr"):
        f, q = nominal_foot(s, phase)
        if in_contact(f):
            b = max(b, bob_level(q))
    return b


def nominal_sx(phase):
    a, z = GAIT10["torso_shift_stance_q"]
    for s in ("vl", "vr"):
        f, q = nominal_foot(s, phase)
        if in_contact(f) and a <= q < z:
            return -INWARD[s]
    return 0


def arm_pose(side, phase):
    f = (phase - GAIT10["arm_peak_px"][side]) % SD
    d = min(f, SD - f)
    b1, b2, b3, b4 = GAIT10["arm_pose_bands_px"]
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
    hdy = max(-1, min(1, nominal_bob(phase - GAIT10["hair_lag_px"]) - bob))
    return {"bob": bob, "hdy": hdy, "sx": nominal_sx(phase), "csx": nominal_sx(phase - GAIT10["cape_shift_lag_px"]),
            "arms": {"R": arm_pose("R", phase), "L": arm_pose("L", phase)}, "feet": feet}


KEY_PHASES = list(range(0, SD, 8))          # 16 review keyframes, every 8 px = 28.6 ms at 140
POSE_NAMES = {
    0: "vl heel strike 12 rows in front (long leg); vr toe-off behind the knee",
    8: "vl loading (body 1 row down); vr heel kick",
    16: "vl mid-stance (2 rows down); vr kick, sole under the knee",
    24: "vl mid-stance; vr tucked knee passing",
    32: "vl heel-up push (1 row down); vr foot hanging under the knee",
    40: "vl push-off, boot sliding behind the knee; vr leg opening forward",
    48: "flight: vl toe-off; vr reaching toward the camera",
    56: "flight: vl kick; vr about to strike",
    64: "vr heel strike 12 rows in front (long leg); vl toe-off behind the knee",
    72: "vr loading (body 1 row down); vl heel kick",
    80: "vr mid-stance (2 rows down); vl kick, sole under the knee",
    88: "vr mid-stance; vl tucked knee passing",
    96: "vr heel-up push (1 row down); vl foot hanging under the knee",
    104: "vr push-off, boot sliding behind the knee; vl leg opening forward",
    112: "flight: vr toe-off; vl reaching toward the camera",
    120: "flight: vr kick; vl about to strike",
}


def land_keys(o0, l0, v0, k0):
    return [[0, o0, l0, v0, k0], [500, rdiv(o0, 2), max(1, min(2, l0)), "reach", 0], [1000, 0, 1, "strike", 0]]


def shuffle_keys(o0, v0):
    first = "toe" if v0 == "toe" else "heelup"
    return [[0, o0, 1, first, 0], [500, rdiv(o0, 2), min(2, 1 + abs(o0) // 4), "hang", 1], [1000, 0, 1, "strike", 0]]


def replan_keys(o0, l0, v0, k0, hs):
    return [[0, o0, max(1, l0), "toe" if v0 in STANCE_VIEWS else v0, k0], [500, rdiv(o0 + A, 2), max(l0, hs), "hang", 1],
            [800, A - 1, max(1, rdiv(hs, 2)), "reach", 0], [1000, A, 1, "strike", 0]]


def reachable_feet():
    seen, todo = set(), []

    def add(t):
        if t not in seen:
            seen.add(t)
            todo.append(t)
    for q in range(SD):
        f = nominal_foot("vl", q)[0]
        add((f["o"], f["lift"], f["view"], f["kin"]))
    for o in range(BK + 1, A + 1):
        for kin in (0, 1):
            add((o, 0, stance_view(A - o), kin))
    add((0, 0, "v8", 0))
    hs_set = range(RESTART10["replan_lift_min"], RESTART10["replan_lift_max"] + 1)
    done = set()
    while todo:
        o0, l0, v0, k0 = todo.pop()
        tabs = [("land", (o0, l0, v0, k0))] + [("replan", (o0, l0, v0, k0, hs)) for hs in hs_set]
        if v0 in STANCE_VIEWS and l0 == 0 and o0 != 0:
            tabs.append(("shuffle", (o0, v0)))
        for kind, args in tabs:
            if (kind, args) in done:
                continue
            done.add((kind, args))
            keys = {"land": land_keys, "shuffle": shuffle_keys, "replan": replan_keys}[kind](*args)
            for u in range(1001):
                add(tuple(interp_keys(keys, u)))
    return seen


def feasibility(parts):
    states = reachable_feet()
    bad, modes = [], {}
    for side in ("vl", "vr"):
        for bob in (0, 1, 2):
            for (o, lift, view, kin) in sorted(states, key=str):
                full, boot, sole, info = compose_leg10(parts, side, bob, {"o": o, "lift": lift, "view": view, "kin": kin})
                modes[info["mode"]] = modes.get(info["mode"], 0) + 1
                if any(not (0 <= x < W and 0 <= y < H) for (x, y) in list(full) + list(boot)):
                    bad.append((side, bob, view, o, lift, "outside"))
                lift_c = min(lift, 3)
                for (x, y) in parts[f"shadow-{side}-l{lift_c}"]:
                    if not (0 <= y + o < H):
                        bad.append((side, bob, view, o, lift, "shadow outside"))
                        break
    return len(states), bad, modes


def gait_numbers():
    v = SPEED_WINDOW_PX_S
    cyc = 1000 * SD / v
    contact_any = 0
    floor_gap = []
    for ph in range(SD):
        fs = [nominal_foot(s, ph)[0] for s in ("vl", "vr")]
        contact_any += any(in_contact(f) for f in fs)
        floor_gap.append(max(0, -max(f["o"] - f["lift"] for f in fs)))
    return {"speed_window_px_s": v, "cycle_ms_at_140": round(cyc, 3), "steps_per_s": round(2000 / cyc, 4),
            "stance_ms_at_140": round(1000 * E / v, 3), "flight_ms_per_step_at_140": round(1000 * (SD / 2 - E) / v, 3),
            "ground_contact_share_of_cycle": round(contact_any / SD, 4), "airborne_share_of_cycle": round(1 - contact_any / SD, 4),
            "floor_gap_rows_max": max(floor_gap), "floor_gap_rows_mean": round(sum(floor_gap) / SD, 3),
            "v07_reference": {"stride_px": 84, "steps_per_s": 6.667, "stance_px": 21, "ground_contact_share": 0.5}}


# ===================================================================================================== build
def build_parts10():
    v8, parts, new9 = b9.build_parts9()
    new = {}
    for side in ("vl", "vr"):
        new[f"boot-{side}-toe"] = push_part(side, parts)
    parts.update(new)
    return v8, parts, new9, new


def to_png(grid):
    return b6.png_bytes(b6.to_rgba(grid))


def grid_sha(grid, shadow):
    return hashlib.sha256(b6.to_rgba(grid).tobytes() + b6.to_rgba(shadow).tobytes()).hexdigest()


def frames_of(parts):
    frames = {}
    for ph in KEY_PHASES:
        st = nominal_state(ph)
        layers, shadow, info = compose10(parts, st)
        frames[f"k{ph:03d}"] = {"phase": ph, "state": st, "layers": layers, "grid": b6.stack(layers), "shadow": shadow, "info": info}
    return frames


def build(out_dir):
    v8, parts, new9, new = build_parts10()
    palette = set(v8.values())
    neutral, nshadow, _ = compose10(parts, b6.NEUTRAL)
    if b6.stack(neutral) != v8:
        raise SystemExit("neutral composition != v8")
    for k, p in new.items():
        if not set(p.values()) <= palette:
            raise SystemExit(f"{k}: colour outside v8's palette")
    n_states, bad, modes = feasibility(parts)
    if bad:
        raise SystemExit(f"{len(bad)} reachable legs do not fit: {bad[:5]}")
    frames = frames_of(parts)
    for key, fr in frames.items():
        if not set(fr["grid"].values()) <= palette:
            raise SystemExit(f"{key}: colour outside v8's palette")
        if fr["info"]["seam_filled"]:
            raise SystemExit(f"{key}: neck seam fill {fr['info']['seam_filled']}")
    per_px = []
    for ph in range(SD):
        st = nominal_state(ph)
        layers, shadow, info = compose10(parts, st)
        per_px.append({"phase_px": ph, "bob": st["bob"], "hdy": st["hdy"], "sx": st["sx"], "csx": st["csx"], "arms": st["arms"],
                       "feet": {s: dict(st["feet"][s], contact=in_contact(st["feet"][s]), leg_mode=info["leg_modes"][s]["mode"])
                                for s in ("vl", "vr")},
                       "composite_sha256": grid_sha(b6.stack(layers), shadow)})
    os.makedirs(_fs(out_dir), exist_ok=True)
    written = []

    def put(name, data):
        in_repo = os.path.join(REPO, OUT_REL, name)
        if len(os.path.abspath(in_repo)) > REPO_PATH_LIMIT:
            raise SystemExit(f"asset path would be {len(os.path.abspath(in_repo))} characters: {name}")
        path = os.path.join(out_dir, name)
        if os.path.exists(_fs(path)):
            with open(_fs(path), "rb") as f:
                if f.read() != data:
                    raise SystemExit(f"refusing to overwrite different bytes: {name}")
        else:
            with open(_fs(path), "wb") as f:
                f.write(data)
        written.append(name)
        return hashlib.sha256(data).hexdigest()

    part_entries = []
    for role in sorted(new):
        name = f"{SLUG}_{PART}_part-{role}-push_{VARIANT}_{STAMP}-{fid('part-' + role)}.png"
        part_entries.append({"role": role, "file": name, "sha256": put(name, to_png(new[role])), "opaque_texels": len(new[role]),
                             "note": "push-off boot; replaces the v06 toe view in v10 (v06 file untouched)"})
    key_entries = []
    for key, fr in frames.items():
        name = f"{SLUG}_{PART}_keyframe-{fr['phase']:03d}px_{VARIANT}_{STAMP}-{fid('key-' + key)}.png"
        sname = f"{SLUG}_{PART}_keyframe-{fr['phase']:03d}px-shadow_{VARIANT}_{STAMP}-{fid('kshadow-' + key)}.png"
        fr["png"] = to_png(fr["grid"])
        key_entries.append({"key": key, "phase_px": fr["phase"], "pose": POSE_NAMES[fr["phase"]], "file": name,
                            "sha256": put(name, fr["png"]), "shadow_file": sname, "shadow_sha256": put(sname, to_png(fr["shadow"])),
                            "state": fr["state"], "near_leg": fr["info"]["near"], "legs": fr["info"]["legs"],
                            "leg_modes": fr["info"]["leg_modes"]})
    keys = list(frames)
    pxo = b6.make_pxo([dict(frames[k]["layers"], shadow=frames[k]["shadow"]) for k in keys], [1.0] * len(keys),
                      frames[keys[0]]["png"], f"{PART}-keyframes", 35.0, order=b6.PXO_LAYERS, dt=(2026, 10, 18, 14, 32, 13),
                      opacity={"shadow": b6.SHADOW_OPACITY})
    pxo_name = f"{SLUG}_{PART}_keyframes-editable_{VARIANT}_{STAMP}-{fid('keyframes-pxo')}.pxo"
    pxo_sha = put(pxo_name, pxo)
    ora = make_ora(new, part_entries, b6.stack(neutral))
    ora_name = f"{SLUG}_{PART}_new-parts-editable_{VARIANT}_{STAMP}-{fid('parts-ora')}.ora"
    ora_sha = put(ora_name, ora)
    gd = os.path.join(out_dir, ".gdignore")
    if not os.path.exists(_fs(gd)):
        open(_fs(gd), "wb").close()
    m9 = json.load(open(_fs(os.path.join(REPO, V09_MANIFEST_REL)), encoding="utf-8"))
    manifest = {
        "project": "Worlds Between", "milestone": "M8", "character": "protagonist-female", "direction": "south",
        "motion_state": "run at MOVE_SPEED 140", "part": PART, "workstream": "m8-w13", "stamp_utc": STAMP, "run_id": RUN_ID,
        "status": "UNAPPROVED / NONRUNTIME test-only single-direction motion candidate (authored gait + push-off revision "
                  "based on the v09 art sources); Root / creator review pending; not a production sprite, not wired into the runtime",
        "art_approved": False, "human_reviewed": False, "runtime_integrated": False, "walk_animation_approved": False,
        "run_animation_approved": False, "stop_animation_approved": False, "counts_toward_art_acceptance": False,
        "approved_scope_unchanged": "selout v8 SOUTH IDLE static frame and the 48 logical px display scale only",
        "exploration_sprites_counter_unchanged": "0/52",
        "based_on": {"v09_builder": "tools/" + V09_BUILDER, "v09_builder_sha256_text_lf_v1": V09_BUILDER_DIGEST,
                     "v09_manifest": V09_MANIFEST_REL, "v09_manifest_sha256_text_lf_v1": sha_text_lf(os.path.join(REPO, V09_MANIFEST_REL)),
                     "v09_parts_used_read_only": [e["file"] for e in m9["parts_new"]],
                     "v06_manifest_sha256_text_lf_v1": b9.V06_MANIFEST_SHA256_TEXT_LF,
                     "v09_status": "preserved unchanged as a partial (drawing-only) fork; v10 does not overwrite any v09 file"},
        "builder": "tools/" + os.path.basename(os.path.abspath(__file__)),
        "units": "window px = source texels: the 80x120 cell is drawn at sprite scale 0.5 into the 640x360 canvas, which "
                 "the 1280x720 window shows at 2x; MOVE_SPEED 140 logical px/s = 280 window px/s",
        "gait": dict(GAIT10, **gait_numbers()),
        "stop": STOP10, "restart": RESTART10,
        "leg_rule": {"n_fold_rows": N_FOLD, "hips_bottom_row": HIPS_BOTTOM, "tuck_views": list(TUCK_VIEWS),
                     "rule": "n = boot top - (hip 61 + bob).  long (n >= 24): thigh = pick(v8 thigh, 10|15 + rdiv(e * T, T + S)), "
                             "v8 knee band 1:1, shin = pick(v8 shin, S + rest), the shin slopes onto the cuff (v04 end rule); "
                             "medium (8 <= n < 24) and folded (n < 8, planned at 8 rows): v06 proportional foreshortening "
                             "(knee >= 5 rows); a folded leg (and every kick / hang leg) is drawn OVER its boot, every other "
                             "boot over its leg; boot texels on rows <= 66 + bob are not drawn; kick / hang use the v09 forward "
                             "knee rows, a shaded shin and v09's knee-over-cuff lean when the shin has < 4 rows; a medium "
                             "non-tuck shin returns to v8's x (v06)"},
        "coat_rule": "coat-skirt rows < 66 at (sx, bob); rows >= 66 at (csx, bob + hdy); with hdy = +1 the hem's top row is "
                     "also drawn at (csx, 66 + bob) so no gap row opens; csx == sx and hdy == 0 on the neutral state",
        "seam_rule": "v09: transparent texels at rows >= 41 closed left, right, above and below -> ink",
        "island_rule": "v10, after the seam fill: an 8-connected component of the stacked frame that is not the largest, has "
                       f"<= {ISLAND_MAX} texels and lies wholly on leg-far / leg-near texels (a tucked thigh peeking past the "
                       "coat edge across a transparent gap) is removed from every layer",
        "island_max_texels": ISLAND_MAX,
        "parts_new": part_entries,
        "parts_from_v09": m9["parts_new"],
        "keyframes": key_entries,
        "editable_sources": {"keyframes_pxo": pxo_name, "keyframes_pxo_sha256": pxo_sha, "keyframes_pxo_layers": b6.PXO_LAYERS,
                             "new_parts_ora": ora_name, "new_parts_ora_sha256": ora_sha},
        "metrics": {"reachable_foot_states": n_states, "reachable_leg_modes_x_sides_x_bob": modes, "nominal_per_px": per_px},
    }
    mname = f"{SLUG}_{PART}_gait-pose-manifest_{VARIANT}_{STAMP}-{fid('manifest')}.json"
    put(mname, (json.dumps(manifest, indent=1) + "\n").encode("utf-8"))
    print(f"wrote {len(written)} files to {out_dir}")
    print("MANIFEST", mname)
    print("GAIT", json.dumps(gait_numbers()))
    return manifest


def make_ora(parts, part_entries, merged):
    dt = (2026, 10, 18, 14, 32, 13)
    lines = ['<?xml version="1.0" encoding="UTF-8"?>', f'<image version="0.0.6" w="{W}" h="{H}">', "  <stack>"]
    for e in reversed(part_entries):
        lines.append(f'    <layer name="{e["role"]}" src="data/{e["role"]}.png" x="0" y="0" opacity="1.000" '
                     'visibility="visible" composite-op="svg:src-over"/>')
    lines += ["  </stack>", "</image>", ""]
    merged_png = to_png(merged)
    members = [("mimetype", b"image/openraster"), ("stack.xml", "\n".join(lines).encode("utf-8"))]
    members += [(f"data/{e['role']}.png", to_png(parts[e["role"]])) for e in part_entries]
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
    """Scratch only: every v10 keyframe at 1x and 6x on a mid floor colour (one PNG each), and a per-px 1x strip."""
    v8, parts, new9, new = build_parts10()
    os.makedirs(_fs(out_dir), exist_ok=True)
    for ph in range(SD):
        layers, shadow, info = compose10(parts, nominal_state(ph))
        grid = b6.stack(layers)
        bg = Image.new("RGBA", (W, H), (150, 140, 128, 255))
        sh = b6.to_rgba(shadow)
        sh[..., 3] = (sh[..., 3].astype(np.float32) * b6.SHADOW_OPACITY).astype(np.uint8)
        bg.alpha_composite(Image.fromarray(sh, "RGBA"))
        bg.alpha_composite(Image.fromarray(b6.to_rgba(grid), "RGBA"))
        bg.save(_fs(os.path.join(out_dir, f"v10_p{ph:03d}_x1.png")))
        if ph in KEY_PHASES:
            bg.resize((W * 6, H * 6), Image.NEAREST).save(_fs(os.path.join(out_dir, f"v10_k{ph:03d}_x6.png")))
    print("GAIT", json.dumps(gait_numbers()))
    n_states, bad, modes = feasibility(parts)
    print("reachable", n_states, "bad", len(bad), bad[:5], modes)
    print("preview written to", out_dir)


def main():
    ap = argparse.ArgumentParser()
    g = ap.add_mutually_exclusive_group(required=True)
    g.add_argument("--out-dir")
    g.add_argument("--preview")
    a = ap.parse_args()
    if a.preview:
        p = os.path.abspath(a.preview)
        if os.path.normcase(p).startswith(os.path.normcase(REPO) + os.sep):
            raise SystemExit("--preview must be outside the repository")
        preview(p)
    else:
        build(os.path.abspath(a.out_dir))


if __name__ == "__main__":
    main()
