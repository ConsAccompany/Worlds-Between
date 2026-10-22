"""Jiang Lan (jiang-lan) four-direction EXPLORATION SOURCE author (jexplore39, UNAPPROVED technical source).

4-frame idle loops, 12-phase walk cycles (40 ms) and phase-aware stop bridges for south/west/north/east at the
frozen Jiang Lan static contract (80x112 cell, pivot 40/104, body rows 8..103 = 96 texels = 48 logical px).

- Neutral layers are NOT redrawn: the 9 role layers (boots, trousers, shirt, vest, arms, devices, face, hair,
  goggles) + hidden guides come from the south static author (south) and the directions static author
  (west/north/east), and must recompose to the existing static PNG bytes. Static and idle f00 ARE those bytes;
  every stop bridge ends on idle f00.
- idle: torso/head/arm groups settle 0/1 texel (never up), legs fixed.
- side (west/east): stride matched to the normal host speed (140 logical px/s = 11.2 source texels per 40 ms
  phase). Each foot is planted 4 phases (local x +16.8, +5.6, -5.6, -16.8 rounded) and swings 8 phases, so the
  cycle has two short flight phases per step: at this speed and leg length a slip-free stride is a jog, not a
  double-support walk (disclosed). Legs are the static near-leg texels sheared about the hip (piecewise
  hip-knee-ankle), lifted below the knee; the far leg/arm are darkened copies of the near limb (static only
  shows a 3-texel far strip). Light stays upper-left; east/west keep their authored side details.
- front/back (south/north): in-place cycle on the same timing (foot lifted below the knee for 8 of 12 phases),
  column split at x=40; planted feet do not travel in screen y (residual disclosed, not a slip pass).
- stop: host stops on release at phase p; bridge [walk p, s1, s2, idle f00]. A grounded foot never moves while
  grounded in a bridge (lifted feet step to neutral).

Character-agnostic helpers (shift/mirror/over, PNG encode/decode, PXO/ORA writers) are imported from the
mexplore23 author. No source tool is modified. No Pixelorama/Godot run here.

Usage:  python -X utf8 -I <tool> build|check
Writes only NEW files under outputs/jexplore39 and game/data/jexplore39.
"""
import importlib.util, io, json, math, os, sys, zipfile
import numpy as np

_HERE = os.path.dirname(os.path.abspath(__file__))


def _load(fn, mod):
    spec = importlib.util.spec_from_file_location(mod, os.path.join(_HERE, fn))
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


_MX_FN = "rpg-2-star-ocean-the-second_protagonist-male_explore-4dir-source-author_unapproved-mexplore23-v01_20261021-162551-6e3b1a7d.py"
_S_FN = "rpg-2-star-ocean-the-second_jiang-lan_south-static-author_unapproved-v01_20261021-235007-514b9771.py"
_D_FN = "rpg-2-star-ocean-the-second_jiang-lan_directions-static-author_unapproved-v01_20261022-153020-105a0103.py"
mx = _load(_MX_FN, "wb_mexplore23_helpers")
S = _load(_S_FN, "wb_jiang_south_v01")
D = _load(_D_FN, "wb_jiang_dirs_v01")
_fs, rp, rb, sha, sha_text, png_bytes, decode, blank = mx._fs, mx.rp, mx.rb, mx.sha, mx.sha_text, mx.png_bytes, mx.decode, mx.blank
shift, mirror, over = mx.shift, mx.mirror, mx.over

STAMP, RUN = "20261022-154032", "5bca7193"
OUT_REL, PKG_REL = "outputs/jexplore39", "game/data/jexplore39"
PFX = "rpg-2-star-ocean-the-second_jiang-lan_explore"
VAR = "unapproved-jexplore39-v01"
ACTOR = "jiang-lan"
W, H, PIN, SOLE = 80, 112, (40, 104), 103
assert (W, H, PIN) == (S.W, S.H, S.PIN) == (mx.W, mx.H, mx.PIN) and S.BODY_ROWS == (8, SOLE)
ZIP_DT = (2026, 10, 22, 15, 40, 32)
mx.ZIP_DT = ZIP_DT                    # in-process only: zip entry dates for this run's PXO/ORA
DIRS = ("south", "west", "north", "east")
NPH, FRAME_MS, IDLE_MS = 12, 40, [700, 200, 400, 200]
HOST_LOGICAL_PX_S = 140.0
V = HOST_LOGICAL_PX_S * FRAME_MS / 1000.0 * 2     # 11.2 source texels per 40 ms phase
ROLES = [n for n in S.LAYERS if n != "guides"]    # Jiang 9-role order (bottom->top), not the male names
PXO_LAYERS = ["far-limbs"] + ROLES + ["guides"]
HEAD, TORSO = ("face", "hair", "goggles"), ("shirt", "vest", "devices")
LEG_TOP, KNEE, ANKLE = 69, 80, 96                 # leg rows: hips < 69 move with the body
STANCE = (16.8, 5.6, -5.6, -16.8)                 # planted local forward offsets, 4 phases x 11.2
SWING_LIFT = 7
FB_SWING = (2, 3, 4, 4, 3, 2, 1, 1)                # front/back lift p4..p11 of a swing: quick toe-off, slow set-down
FB_LIFT = max(FB_SWING)
FAR_BASE = 2                                      # static far foot toe sits 2 texels ahead of the near toe

PAL = {k: "#" + v for k, v in S.PAL.items()}     # scalar '#rrggbb' strings
RGB = {k: S.rgb(k) for k in S.PAL}
INV = {v: k for k, v in RGB.items()}
assert len(INV) == len(RGB)
DARK = {"c1": "c2", "c2": "c3", "c3": "c4", "c4": "c4", "v1": "c2", "v2": "c3", "v3": "c3", "v4": "c4",
        "o1": "o3", "o2": "o3", "o3": "o3", "g1": "c3", "g2": "c4", "k1": "k1",
        "s1": "s2", "s2": "s3", "s3": "s4", "s4": "s4"}

NEUTRAL = {
    "south": ("game/assets/characters/jiang-lan-native-south-v01/rpg-2-star-ocean-the-second_jiang-lan_south-idle-static_unapproved-v01_20261021-235007-5f1c2a90.png",
              "fb7de93bbfb9dd9e50fde752588b82e3baa5070cbf46b7003f051ac9a7433092"),
    "west": ("game/assets/characters/jiang-lan-native-directions-v01/west/rpg-2-star-ocean-the-second_jiang-lan_west-static_unapproved-v01_20261022-153020-a657c4cc.png",
             "56609c0e264201f96aaf221aa94d2a9137e25dfebc98eeb417d1c640d4cd9b95"),
    "north": ("game/assets/characters/jiang-lan-native-directions-v01/north/rpg-2-star-ocean-the-second_jiang-lan_north-static_unapproved-v01_20261022-153020-28e75f42.png",
              "d558bc46c2ac287c0ff300538bfd7a33f79fa6afb78f7da3730ce1ff20d6b9ed"),
    "east": ("game/assets/characters/jiang-lan-native-directions-v01/east/rpg-2-star-ocean-the-second_jiang-lan_east-static_unapproved-v01_20261022-153020-609cc5bb.png",
             "b355331f7b012b7366100cfe62ba7f55e6662d70882d56c2477ffa5fd98ed57e"),
}
NEUTRAL_NATIVE = {  # editable neutral sources: read-only pins (must stay byte-exact)
    "game/assets/characters/jiang-lan-native-south-v01/rpg-2-star-ocean-the-second_jiang-lan_south-idle-static-editable_unapproved-v01_20261021-235007-a3e07b14.pxo": "530ca642dbc4a0189de008e1b71a6912c547b72fa9a3bb8e2833e0c7f5d82d7e",
    "game/assets/characters/jiang-lan-native-south-v01/rpg-2-star-ocean-the-second_jiang-lan_south-idle-static-editable_unapproved-v01_20261021-235007-c81d4e62.ora": "6cba6e8b01c34b96b949f698165707b56e3a379e9cc75dae121aaee2c22c775c",
    "game/assets/characters/jiang-lan-native-directions-v01/west/rpg-2-star-ocean-the-second_jiang-lan_west-edit_unapproved-v01_20261022-153020-ad7a2399.pxo": "2af25d0234e288a133684762a863b823c4fb5a3c184195542075b4c76b9a298b",
    "game/assets/characters/jiang-lan-native-directions-v01/west/rpg-2-star-ocean-the-second_jiang-lan_west-edit_unapproved-v01_20261022-153020-a9aedf6f.ora": "35386bf532aea0fc0d6f5bacfd15a4a97b6d1f7a7851ad55e84b48c58bf006f2",
    "game/assets/characters/jiang-lan-native-directions-v01/north/rpg-2-star-ocean-the-second_jiang-lan_north-edit_unapproved-v01_20261022-153020-ec8c2637.pxo": "9dc7dc22ff08383ddd51462bf692a0897cef782751eae9dc98afe77d91f32412",
    "game/assets/characters/jiang-lan-native-directions-v01/north/rpg-2-star-ocean-the-second_jiang-lan_north-edit_unapproved-v01_20261022-153020-8b79a2c1.ora": "5bc679b7c9865dee588aaa7f0768dd956012945637c6c6c56c526727e395f190",
    "game/assets/characters/jiang-lan-native-directions-v01/east/rpg-2-star-ocean-the-second_jiang-lan_east-edit_unapproved-v01_20261022-153020-3668a51e.pxo": "9aa70dcc38802bd5cc243f7453943ae88f1b6bc9938ef6674b941d2693385019",
    "game/assets/characters/jiang-lan-native-directions-v01/east/rpg-2-star-ocean-the-second_jiang-lan_east-edit_unapproved-v01_20261022-153020-f9908af9.ora": "709b8e401f44f645e0eabe6a3fc2d1505370e0a57ff201395dde963edefc0220",
}


def pins_state():
    out = {}
    for rel, want in list(NEUTRAL_NATIVE.items()) + [v for v in NEUTRAL.values()]:
        try:
            out[rel] = sha(rb(rp(rel))) == want
        except OSError:
            out[rel] = False
    return out


# ----------------------------------------------------------------------------- neutral layers (exact)
def load_neutral(d):
    rel, want = NEUTRAL[d]
    png = rb(rp(rel))
    assert sha(png) == want, f"{d} neutral PNG hash drift"
    lay = S.draw() if d == "south" else D.draw(d)
    comp = S.compose_layers({n: lay[n] for n in S.LAYERS})
    assert np.array_equal(comp, decode(png)), f"{d} role layers != neutral PNG"
    return {n: lay[n].copy() for n in S.LAYERS}, png


def recolor(a, table):
    o = a.copy()
    m = a[..., 3] == 255
    for y, x in zip(*np.nonzero(m)):
        k = INV[tuple(int(v) for v in a[y, x, :3])]
        o[y, x, :3] = RGB[table.get(k, k)]
    return o


def rows(a, y0=0, y1=H):
    o = a.copy(); o[:y0] = 0; o[y1:] = 0
    return o


def cols(a, x0, x1):
    o = blank(); o[:, x0:x1] = a[:, x0:x1]
    return o


def warp(a, dxf, dyf):
    """Move each row y by (dxf(y), dyf(y)); rows are written top->bottom so lower rows win overlaps (knee)."""
    o = blank()
    for y in np.nonzero(a[..., 3].any(1))[0]:
        dx, dy = int(dxf(y)), int(dyf(y))
        ny = y + dy
        if not 0 <= ny < H:
            continue
        xs = np.nonzero(a[y, :, 3] == 255)[0]
        nx = xs + dx
        ok = (nx >= 0) & (nx < W)
        o[ny, nx[ok]] = a[y, xs[ok]]
    return o


def clip_floor(a):
    a = a.copy(); a[SOLE + 1:] = 0
    return a


def leg_transform(piece, fdx_screen, lift, bob, knee_fwd_screen=0):
    kdx = fdx_screen * (KNEE - LEG_TOP) / (ANKLE - LEG_TOP) + knee_fwd_screen

    def dxf(y):
        if y < LEG_TOP:
            return 0
        if y < KNEE:
            return round(kdx * (y - LEG_TOP) / (KNEE - LEG_TOP))
        if y < ANKLE:
            return round(kdx + (fdx_screen - kdx) * (y - KNEE) / (ANKLE - KNEE))
        return round(fdx_screen)
    return clip_floor(warp(piece, dxf, lambda y: bob if y < KNEE else -lift))


def arm_transform(a, swing_screen, dy):
    return warp(a, lambda y: round(swing_screen * min(max((y - 40) / 26.0, 0.0), 1.0)), lambda y: dy)


# ----------------------------------------------------------------------------- poses
def ease(t):
    return 0.5 - 0.5 * math.cos(math.pi * t)


def foot(ph):
    """Forward local offset (source texels, relative to that foot's neutral) and lift for one foot.
    Planted phases 0..3 (world-locked at 11.2/phase), swing phases 4..11."""
    if ph < 4:
        return STANCE[ph], 0
    j = ph - 3                          # 1..8
    t = j / 9.0
    return STANCE[3] + (STANCE[0] - STANCE[3]) * ease(t), round(SWING_LIFT * math.sin(math.pi * t))


def walk_pose(p, side):
    ax, al = foot(p)
    bx, bl = foot((p + 6) % NPH)
    bob = 1 if p % 6 in (1, 2) else 0                 # compress at mid-stance; never shift the body up
    if not side:
        al = FB_SWING[p - 4] if p >= 4 else 0
        q = (p + 6) % NPH
        bl = FB_SWING[q - 4] if q >= 4 else 0
        ax = bx = 0.0
    swing = -6.0 * math.cos(2 * math.pi * p / NPH) if side else 0.0
    arm_dy = (round(math.sin(2 * math.pi * p / NPH)), -round(math.sin(2 * math.pi * p / NPH))) if not side else (0, 0)
    return {"ax": round(ax), "al": int(al), "bx": round(bx), "bl": int(bl), "bob": bob, "swing": round(swing),
            "arm_dy_l": arm_dy[0], "arm_dy_r": arm_dy[1], "planted": "".join(k for k, l in (("A", al), ("B", bl)) if l == 0) or "flight"}


NEUTRAL_POSE = {"ax": 0, "al": 0, "bx": 0, "bl": 0, "bob": 0, "swing": 0, "arm_dy_l": 0, "arm_dy_r": 0}


def stop_poses(wp):
    """s1: grounded feet stay; lifted feet halfway toward neutral.  s2: feet lifted in s1 land on neutral;
    a still-displaced grounded foot lifts and moves halfway (it lands on idle f00)."""
    s1, s2 = dict(NEUTRAL_POSE), dict(NEUTRAL_POSE)
    for k in ("a", "b"):
        x, l = wp[k + "x"], wp[k + "l"]
        if l == 0:
            s1[k + "x"], s1[k + "l"] = x, 0
        else:
            s1[k + "x"], s1[k + "l"] = round(x / 2), max(1, math.ceil(l / 2))
    for k in ("a", "b"):
        x, l = s1[k + "x"], s1[k + "l"]
        if l > 0 or x == 0:
            s2[k + "x"], s2[k + "l"] = 0, 0
        else:
            s2[k + "x"], s2[k + "l"] = round(x / 2), 2
    s1.update(bob=0, swing=round(wp["swing"] / 2), arm_dy_l=0, arm_dy_r=0)
    s2.update(bob=1, swing=round(wp["swing"] / 4), arm_dy_l=0, arm_dy_r=0)
    return s1, s2


IDLE = [(0, 0, 0), (1, 1, 0), (1, 1, 1), (0, 1, 1)]   # (torso, head, arms) settle texels; f00 neutral


# ----------------------------------------------------------------------------- renderers
def render_idle(base, i):
    t, h, a = IDLE[i]
    out = []
    for n in ROLES:
        dy = h if n in HEAD else (t if n in TORSO else (a if n == "arms" else 0))
        out.append((n, shift(base[n], 0, dy) if dy else base[n].copy()))
    return [("far-limbs", blank())] + out


def side_sign(d):
    return 1 if d == "east" else -1


def side_parts(base, d):
    s = side_sign(d)
    xs = np.arange(W)
    f = (xs - 40) * s
    tr, bt = base["trousers"], base["boots"]
    near_tr = rows(tr, LEG_TOP); near_tr[:, f > 1] = 0
    near_bt = bt.copy(); near_bt[:, f > 5] = 0
    hips = rows(tr, 0, LEG_TOP)
    far_leg = recolor(over([near_bt, near_tr]), DARK)
    far_arm = recolor(base["arms"], DARK)
    return {"near_tr": near_tr, "near_bt": near_bt, "hips": hips, "far_leg": far_leg, "far_arm": far_arm}


def render_side(base, parts, d, q):
    s = side_sign(d)
    b = q["bob"]
    knee_a = s * (q["al"] * 0.6)
    knee_b = s * (q["bl"] * 0.6)
    near_tr = leg_transform(parts["near_tr"], s * q["ax"], q["al"], b, knee_a)
    near_bt = leg_transform(parts["near_bt"], s * q["ax"], q["al"], b, knee_a)
    far_leg = leg_transform(parts["far_leg"], s * (q["bx"] + FAR_BASE), q["bl"], b, knee_b)
    far_arm = arm_transform(parts["far_arm"], -s * q["swing"], b)
    out = {"far-limbs": over([far_arm, far_leg]), "boots": near_bt,
           "trousers": over([shift(parts["hips"], 0, b), near_tr]),
           "arms": arm_transform(base["arms"], s * q["swing"], b)}
    for n in ROLES:
        if n not in out:
            out[n] = shift(base[n], 0, b) if b else base[n].copy()
    return [(n, clip_floor(out[n])) for n in PXO_LAYERS[:-1]], {"A": near_bt, "B": far_leg}


def render_fb(base, d, q):
    b = q["bob"]
    out = {}
    feet = {}
    legs_tr, legs_bt = [], []
    for key, x0, x1 in (("A", 0, 40), ("B", 40, W)):
        lift = q["al"] if key == "A" else q["bl"]
        tr = cols(rows(base["trousers"], LEG_TOP), x0, x1)
        bt = cols(base["boots"], x0, x1)
        legs_tr.append(leg_transform(tr, 0, lift, b))
        bt2 = leg_transform(bt, 0, lift, b)
        legs_bt.append(bt2)
        feet[key] = bt2
    out["trousers"] = over([shift(rows(base["trousers"], 0, LEG_TOP), 0, b)] + legs_tr)
    out["boots"] = over(legs_bt)
    arms = base["arms"]
    out["arms"] = over([shift(cols(arms, 0, 40), 0, b + q["arm_dy_l"]), shift(cols(arms, 40, W), 0, b + q["arm_dy_r"])])
    out["far-limbs"] = blank()
    for n in ROLES:
        if n not in out:
            out[n] = shift(base[n], 0, b) if b else base[n].copy()
    return [(n, clip_floor(out[n])) for n in PXO_LAYERS[:-1]], feet


def render(base, parts, d, q):
    return render_side(base, parts, d, q) if d in ("west", "east") else render_fb(base, d, q)


def sole(piece, d):
    """Measured from rendered texels: grounded if the foot piece occupies the sole row; toe/heel in screen x."""
    ys, xs = np.nonzero(piece[..., 3] == 255)
    low = int(ys.max()) if len(ys) else -1
    on = xs[ys == SOLE]
    if not len(on):
        return {"grounded": False, "lowest_row": low}
    s = side_sign(d) if d in ("west", "east") else 1
    return {"grounded": True, "lowest_row": low, "toe_x": int(on.max() if s > 0 else on.min()),
            "heel_x": int(on.min() if s > 0 else on.max())}


def static_feet(base, d):
    """Neutral feet from the static boots layer (near f<=5 / far peek f>=6 on sides, x<40 / x>=40 front/back)."""
    bt = base["boots"]
    if d in ("west", "east"):
        s = side_sign(d)
        f = (np.arange(W) - 40) * s
        a, b = bt.copy(), bt.copy()
        a[:, f > 5] = 0; b[:, f <= 5] = 0
        return {"A": a, "B": b}
    return {"A": cols(bt, 0, 40), "B": cols(bt, 40, W)}


# ----------------------------------------------------------------------------- build
def fname(subject, ext):
    tag = sha(f"{RUN}:{subject}".encode())[:8]
    return f"{PFX}-{subject}_{VAR}_{STAMP}-{tag}.{ext}"


def frame_set(d):
    base, png = load_neutral(d)
    side = d in ("west", "east")
    parts = side_parts(base, d) if side else None
    idle = [render_idle(base, i) for i in range(4)]
    neutral = over([a for _, a in idle[0]])
    assert np.array_equal(neutral, decode(png))
    nfeet = static_feet(base, d)
    walk = []
    for p in range(NPH):
        q = walk_pose(p, side)
        lay, feet = render(base, parts, d, q)
        walk.append((lay, q, feet))
    stop = {}
    for p in range(NPH):
        s1, s2 = stop_poses(walk[p][1])
        seq = []
        for q in (s1, s2):
            lay, feet = render(base, parts, d, q)
            seq.append((lay, q, feet))
        stop[p] = seq
    return {"base": base, "png": png, "neutral": neutral, "idle": idle, "walk": walk, "stop": stop, "nfeet": nfeet}


def contact_report(d, fs):
    """Actual rendered sole texels. World forward coordinate = local forward + host advance (11.2 src/40 ms)."""
    side = d in ("west", "east")
    s = side_sign(d) if side else 1
    rec = []
    for p in range(NPH):
        rec.append({k: sole(fs["walk"][p][2][k], d) for k in ("A", "B")})
    walk_pairs, worst = [], 0.0
    for p in range(NPH):
        n = (p + 1) % NPH
        for k in ("A", "B"):
            a, b = rec[p][k], rec[n][k]
            if a["grounded"] and b["grounded"]:
                if side:
                    dl = s * (b["toe_x"] - a["toe_x"])
                    dh = s * (b["heel_x"] - a["heel_x"])
                    slip = round(max(abs(dl + V), abs(dh + V)), 3)
                else:
                    slip = round(V, 3)          # in place: planted foot travels with the host in screen y
                worst = max(worst, slip)
                walk_pairs.append({"from": p, "to": n, "foot": k, "world_slip_src": slip})
    # 60 fps samples over two cycles: frame = floor(t / 40 ms), host continuous
    saw = 0.0
    if side:
        for k in ("A", "B"):
            run, best = [], 0.0
            for i in range(int(2 * NPH * FRAME_MS * 60 / 1000)):
                t = i / 60.0
                fi = int(t * 1000 // FRAME_MS)
                r = rec[fi % NPH][k]
                if r["grounded"]:
                    run.append(s * (r["toe_x"] - 40) + 2 * HOST_LOGICAL_PX_S * t)
                else:
                    if len(run) > 1:
                        best = max(best, max(run) - min(run))
                    run = []
            saw = max(saw, best)
    stops, sworst = [], 0.0
    nf = {k: sole(fs["nfeet"][k], d) for k in ("A", "B")}
    for p in range(NPH):
        seq = [rec[p]] + [{k: sole(x[2][k], d) for k in ("A", "B")} for x in fs["stop"][p]] + [nf]
        for i in range(3):
            for k in ("A", "B"):
                a, b = seq[i][k], seq[i + 1][k]
                if a["grounded"] and b["grounded"]:
                    m = abs(b["toe_x"] - a["toe_x"])          # host stopped: any toe change is slip
                    if side and k == "A":
                        m = max(m, abs(b["heel_x"] - a["heel_x"]))
                    sworst = max(sworst, m)
                    if m:
                        stops.append({"phase": p, "step": i, "foot": k, "slip_src": m})
    return {"per_phase_feet": rec, "walk_grounded_pairs": walk_pairs,
            "walk_max_world_slip_src_at_40ms_boundaries": round(worst, 3),
            "walk_max_world_slip_logical_at_40ms_boundaries": round(worst / 2, 3),
            "walk_planted_foot_world_excursion_src_60fps_samples": round(saw, 3) if side else None,
            "walk_planted_foot_world_excursion_logical_60fps_samples": round(saw / 2, 3) if side else None,
            "flight_phases": [p for p in range(NPH) if not rec[p]["A"]["grounded"] and not rec[p]["B"]["grounded"]],
            "stop_bridge_grounded_slip_src_max": sworst, "stop_bridge_nonzero": stops[:8],
            "neutral_feet": nf}


def artifacts():
    files, man, fsets = {}, {}, {}
    for d in DIRS:
        f = frame_set(d)
        fsets[d] = f
        entry = {"neutral_source": {"file": NEUTRAL[d][0], "sha256": NEUTRAL[d][1], "hash": "sha256-bytes"},
                 "static": None, "idle": [], "walk": [], "stop_bridges": {}}
        native, tags = [], []
        G = f["base"]["guides"]

        def emit(subject, layers, pose, ms, role):
            comp = over([a for _, a in layers])
            png = f["png"] if np.array_equal(comp, f["neutral"]) else png_bytes(comp)
            rel = f"{OUT_REL}/png/{fname(subject, 'png')}"
            files[rel] = png
            native.append((list(layers) + [("guides", G)], ms))
            e = {"file": rel, "sha256": sha(png), "duration_ms": ms, "role": role}
            if pose is not None:
                e["pose"] = {k: v for k, v in pose.items()}
            return e, comp

        e, _ = emit(f"{d}-static", f["idle"][0], None, 600, "static neutral (exact existing PNG bytes)")
        e["duration_ms"] = None
        entry["static"] = e
        start = len(native)
        for i, lay in enumerate(f["idle"]):
            e, comp = emit(f"{d}-idle-f{i:02d}", lay, {"torso": IDLE[i][0], "head": IDLE[i][1], "arms": IDLE[i][2]}, IDLE_MS[i], "idle loop")
            entry["idle"].append(e)
        tags.append({"name": f"{d}-idle", "from": start + 1, "to": len(native)})
        start = len(native)
        for p, (lay, q, _) in enumerate(f["walk"]):
            e, _ = emit(f"{d}-walk-p{p:02d}", lay, q, FRAME_MS, "walk phase")
            e["phase"] = p
            entry["walk"].append(e)
        tags.append({"name": f"{d}-walk", "from": start + 1, "to": len(native)})
        for p in range(NPH):
            seq, start = [{"ref": "walk", "index": p, "k": 0.0}], len(native)
            for si, (lay, q, _) in enumerate(f["stop"][p], start=1):
                e, _ = emit(f"{d}-stop-p{p:02d}-s{si}", lay, q, FRAME_MS, "phase-aware stop bridge")
                e["k"] = si / 3.0
                seq.append(e)
            seq.append({"ref": "idle", "index": 0, "k": 1.0})
            tags.append({"name": f"{d}-stop-p{p:02d}", "from": start + 1, "to": len(native)})
            entry["stop_bridges"][f"phase{p}"] = seq
        pxo = mx.make_pxo(PXO_LAYERS, native, f["png"], tags)
        ora = mx.make_ora([(n, f["base"][n]) for n in ROLES] + [("guides", G)], f["png"])
        prel, orel = f"{OUT_REL}/{fname(d + '-editable', 'pxo')}", f"{OUT_REL}/{fname(d + '-static-layers', 'ora')}"
        files[prel], files[orel] = pxo, ora
        entry["pxo"] = {"file": prel, "sha256": sha(pxo), "frames": len(native), "layers_bottom_to_top": PXO_LAYERS,
                        "frame_order": "static, idle f00-f03, walk p00-p11, stop p00..p11 x (s1,s2)"}
        entry["ora"] = {"file": orel, "sha256": sha(ora), "layers_bottom_to_top": ROLES + ["guides"],
                        "content": "supplementary: static neutral 9 role layers + hidden guides"}
        man[d] = entry
    return fsets, files, man


def build_all():
    fsets, files, man = artifacts()
    contacts = {d: contact_report(d, fsets[d]) for d in DIRS}
    entry = lambda e: {"file": "png/" + e["file"].rsplit("/", 1)[-1], "duration_ms": e["duration_ms"]}
    set_name = fname("sprite-set-runtime", "json")
    sprite_set = {"schema": "worlds-between.exploration-sprite-set.v1", "set_id": f"{ACTOR}-exploration-source-{STAMP}-{RUN}",
                  "actor_id": ACTOR, "density": 2, "frame_size": [W, H], "pivot": list(PIN),
                  "status": "UNAPPROVED technical source; not wired into any default; frame paths are relative to this JSON",
                  "actions": {"idle": {d: [entry(e) for e in man[d]["idle"]] for d in DIRS},
                              "walk": {d: [entry(e) for e in man[d]["walk"]] for d in DIRS}}}
    stop = {"schema": "worlds-between.exploration-stop-transition.supplemental.v1", "actor_id": ACTOR,
            "rule": "phase-aware stop: on release at walk phase p the host position stops immediately; play bridge "
                    "[walk p exact, s1, s2, idle f00 exact] at frame_ms each; settle 120 ms inclusive",
            "frame_ms": FRAME_MS, "settle_ms_inclusive": FRAME_MS * 3, "pivot": list(PIN), "logical_height": 48,
            "runtime_default": False,
            "phase_bridges": {d: {k: [s if "ref" in s else {"file": "png/" + s["file"].rsplit("/", 1)[-1], "k": i / 3.0, "sha256": s["sha256"]}
                                      for i, s in enumerate(v)] for k, v in man[d]["stop_bridges"].items()} for d in DIRS}}
    ss_b = (json.dumps(sprite_set, indent=2, ensure_ascii=False) + "\n").encode()
    st_b = (json.dumps(stop, indent=2, ensure_ascii=False) + "\n").encode()
    files[f"{PKG_REL}/{set_name}"] = ss_b
    stop_rel = f"{PKG_REL}/{fname('stop-transition-supplemental', 'json')}"
    files[stop_rel] = st_b
    for rel, payload in list(files.items()):
        if rel.startswith(OUT_REL + "/png/"):
            files[PKG_REL + "/png/" + rel.rsplit("/", 1)[-1]] = payload
    reg_rel = PKG_REL + "/" + fname("sprite-set-registry", "json")
    files[reg_rel] = (json.dumps({"schema": "worlds-between.exploration-sprite-set-registry.v1", "actors": {ACTOR: set_name}}, indent=2) + "\n").encode()
    source = {"project": "Worlds Between", "visual_id": ACTOR, "run_id": RUN, "variant": VAR,
              "status": "UNAPPROVED technical source; art and motion not approved; not runtime-integrated; no default changed",
              "task_ids": ["content.char.jiang-lan.idle-anim", "content.char.jiang-lan.walk-south", "content.char.jiang-lan.walk-west",
                           "content.char.jiang-lan.walk-north", "content.char.jiang-lan.walk-east"],
              "contract": {"cell": [W, H], "pivot": list(PIN), "density": 2, "body_rows": [8, SOLE], "logical_height": 48,
                           "alpha": "binary", "filter": "nearest", "palette": PAL, "palette_size": len(PAL)},
              "timing": {"idle_ms": IDLE_MS, "walk_frame_ms": FRAME_MS, "walk_phases": NPH, "cycle_ms": NPH * FRAME_MS,
                         "stop_bridge_frames": 2, "settle_ms_inclusive": FRAME_MS * 3,
                         "host_normal_speed_logical_px_s": HOST_LOGICAL_PX_S, "host_advance_per_phase_source": V},
              "walk_model": {"side": "foot A = near leg planted p0-p3 at local +16.8/+5.6/-5.6/-16.8 (forward, rounded), swing p4-p11 "
                                     f"(ease, lift up to {SWING_LIFT}); foot B = far leg, same shifted 6 phases, neutral +{FAR_BASE}; "
                                     "flight at p4,p5,p10,p11 (jog-like stride required to match 140 px/s)",
                             "front_back": f"in place; foot A = viewer-left column (x<40) lifted p4-p11 by {list(FB_SWING)}, B = x>=40 same shifted 6 phases",
                             "bob": "body down 1 texel at p1,p2,p7,p8; never up", "arms": "side: near arm sheared about the shoulder opposite the near leg (+-6), far arm darkened copy; front/back: +-1 texel"},
              "idle_model": {"frames": 4, "duration_ms": IDLE_MS, "groups_torso_head_arms": IDLE, "neutral_endpoint": "f00 == static (exact bytes)"},
              "source_inputs": {"south_static_author": {"file": "tools/" + _S_FN, "sha256_text_lf_v1": sha_text(rb(os.path.join(_HERE, _S_FN)))},
                                "directions_static_author": {"file": "tools/" + _D_FN, "sha256_text_lf_v1": sha_text(rb(os.path.join(_HERE, _D_FN)))},
                                "neutral_pngs": {d: {"file": NEUTRAL[d][0], "sha256": NEUTRAL[d][1]} for d in DIRS},
                                "neutral_editables_pinned": NEUTRAL_NATIVE},
              "reused_helpers": {"file": "tools/" + _MX_FN, "sha256_text_lf_v1": sha_text(rb(os.path.join(_HERE, _MX_FN))),
                                 "use": "shift/mirror/over, png encode/decode, make_pxo/make_ora (male layer names NOT used)"},
              "directions": man, "contact_check": contacts,
              "package": {"sprite_set": f"{PKG_REL}/{set_name}", "sprite_set_sha256": sha(ss_b), "registry": reg_rel,
                          "stop_supplemental": stop_rel, "stop_supplemental_sha256_text_lf_v1": sha_text(st_b)},
              "limitations": [
                  "side gait is a jog-like stride with 2 flight phases per step: at 140 logical px/s and this leg length a "
                  "double-support walk cannot be world-locked at 40 ms (would need +-33 texel feet)",
                  "side planted-foot residual at 40 ms boundaries is integer rounding of 11.2/phase (see contact_check); "
                  "between boundaries the host moves continuously while the frame is held, so at 60 fps a planted foot "
                  "sweeps the listed excursion and snaps back (frame quantization, disclosed, not a pass)",
                  "front/back cycles are in place: a planted foot travels with the host by 11.2 source texels (5.6 logical) per 40 ms",
                  "legs are sheared static texels (lean, slight stretch) and far limbs are darkened near-limb copies; "
                  "coarse frozen statics, no repaint; cosmetic refinement deferred until after MVP",
                  "no Pixelorama round-trip, no Godot import, no normal-speed movie in this batch (root owns those)",
                  "metrics are not motion acceptance; creator review of a normal-speed movie is required"],
              "tool": {"file": "tools/" + os.path.basename(__file__), "sha256_text_lf_v1": sha_text(rb(os.path.abspath(__file__)))}}
    files[f"{OUT_REL}/{fname('source-manifest', 'json')}"] = (json.dumps(source, indent=2, ensure_ascii=False) + "\n").encode()
    return fsets, files, source


# ----------------------------------------------------------------------------- checks
def source_checks(fsets, files, source):
    res = []

    def ck(name, ok, detail=""):
        res.append({"check": name, "pass": bool(ok), "detail": detail})

    pal = set(RGB.values())
    for d in DIRS:
        e = source["directions"][d]
        stop_frames = [s for p in range(NPH) for s in e["stop_bridges"][f"phase{p}"] if "file" in s]
        allf = [e["static"]] + e["idle"] + e["walk"] + stop_frames
        bad = []
        for x in allf:
            a = decode(files[x["file"]]); al = a[..., 3]
            if a.shape != (H, W, 4) or set(np.unique(al)) - {0, 255} or al[0].any() or al[-1].any() or al[:, 0].any() or al[:, -1].any():
                bad.append(x["file"])
            if {tuple(c) for c in a[al == 255][:, :3]} - pal:
                bad.append(x["file"] + " palette")
        ck(f"{d} all frames 80x112 binary alpha, clear border, Jiang palette only", not bad, bad[:3])
        ck(f"{d} static + idle f00 are the exact neutral PNG bytes",
           e["static"]["sha256"] == NEUTRAL[d][1] and e["idle"][0]["sha256"] == NEUTRAL[d][1])
        ck(f"{d} counts idle 4 walk 12 stop bridge frames 24", (len(e["idle"]), len(e["walk"]), len(stop_frames)) == (4, 12, 24))
        ck(f"{d} every bridge = [walk p, s1, s2, idle f00]", all(
            v[0] == {"ref": "walk", "index": int(k[5:]), "k": 0.0} and v[-1] == {"ref": "idle", "index": 0, "k": 1.0} and len(v) == 4
            for k, v in e["stop_bridges"].items()))
        idl = {files[x["file"]] for x in e["idle"]}
        ck(f"{d} idle frames distinct (>=3)", len(idl) >= 3, len(idl))
        low = {decode(files[x["file"]])[69:104].tobytes() for x in e["walk"]}
        ck(f"{d} walk lower body differs across phases", len(low) >= 8, len(low))
        hs = [int(np.nonzero(decode(files[x["file"]])[..., 3].any(1))[0].min()) for x in allf]
        ck(f"{d} top row never above neutral (body never shifted up)", min(hs) >= 8, [min(hs), max(hs)])
        with zipfile.ZipFile(io.BytesIO(files[e["ora"]["file"]])) as z:
            comp = over([decode(z.read(f"data/{n}.png")) for n in ROLES])
            ck(f"{d} ORA role layers recompose to neutral PNG", np.array_equal(comp, decode(files[e["static"]["file"]])) and
               z.read("mergedimage.png") == files[e["static"]["file"]])
        with zipfile.ZipFile(io.BytesIO(files[e["pxo"]["file"]])) as z:
            nl = len(PXO_LAYERS)
            okp = len(allf) == e["pxo"]["frames"]
            dj = json.loads(z.read("data.json"))
            okp &= [l["name"] for l in dj["layers"]] == PXO_LAYERS
            for fi, x in enumerate(allf, start=1):
                lays = [np.frombuffer(z.read(f"image_data/frames/{fi}/layer_{li}"), np.uint8).reshape(H, W, 4) for li in range(1, nl)]
                okp &= np.array_equal(over(lays), decode(files[x["file"]]))
            ck(f"{d} PXO (Jiang 9 roles + far-limbs + guides) cels recompose to every frame PNG", okp, e["pxo"]["frames"])
        c = source["contact_check"][d]
        if d in ("west", "east"):
            ck(f"{d} side planted foot world slip at 40 ms boundaries <= 1 source texel (rounding of 11.2)",
               c["walk_max_world_slip_src_at_40ms_boundaries"] <= 1.0,
               {"max_src": c["walk_max_world_slip_src_at_40ms_boundaries"], "60fps_excursion_src": c["walk_planted_foot_world_excursion_src_60fps_samples"]})
            ck(f"{d} each foot grounded 4 phases per cycle", all(sum(1 for r in c["per_phase_feet"] if r[k]["grounded"]) == 4 for k in ("A", "B")),
               [sum(1 for r in c["per_phase_feet"] if r[k]["grounded"]) for k in ("A", "B")])
        ck(f"{d} stop bridges: a grounded foot never moves (host stopped)", c["stop_bridge_grounded_slip_src_max"] == 0,
           c["stop_bridge_nonzero"][:3])
    st = {d: decode(files[source["directions"][d]["static"]["file"]]) for d in DIRS}
    ck("east is not a mirror of west (statics)", not np.array_equal(st["east"], mirror(st["west"])))
    we = sum(not np.array_equal(decode(files[a["file"]]), mirror(decode(files[b["file"]])))
             for a, b in zip(source["directions"]["east"]["walk"], source["directions"]["west"]["walk"]))
    ck("east walk frames are not mirrors of west walk frames (side asymmetry kept)", we == NPH, we)
    eye = {RGB["e1"], RGB["e2"], RGB["m1"]}
    fn = fsets["north"]
    nl = [lay for lay in fn["idle"]] + [w[0] for w in fn["walk"]] + [x[0] for p in range(NPH) for x in fn["stop"][p]]
    nb = sum(1 for lay in nl for n, a in lay if n == "face" and {tuple(int(v) for v in cc) for cc in a[a[..., 3] == 255][:, :3]} & eye)
    ck("north face layer has no eye/mouth colours in any frame (rear neck/ears only)", nb == 0, {"frames": len(nl), "with_eyes": nb})
    pk = json.loads(files[source["package"]["sprite_set"]])
    paths = [f["file"] for a in pk["actions"].values() for v in a.values() for f in v]
    durs = [f["duration_ms"] for a in pk["actions"].values() for v in a.values() for f in v]
    ok = pk["schema"] == "worlds-between.exploration-sprite-set.v1" and pk["actor_id"] == ACTOR and \
        set(pk["actions"]) == {"idle", "walk"} and all(set(pk["actions"][a]) == set(DIRS) for a in pk["actions"])
    ok &= all(isinstance(x, int) and 40 <= x <= 2000 for x in durs)
    ok &= all(files[PKG_REL + "/" + p] == files[OUT_REL + "/" + p] for p in paths)
    ck("runtime sprite set: schema/actor/4 dirs/explicit durations/relative byte-equal PNG copies", ok, len(paths))
    stp = json.loads(files[source["package"]["stop_supplemental"]])
    sp = [s["file"] for d in DIRS for v in stp["phase_bridges"][d].values() for s in v if "file" in s]
    ck("stop supplemental: actor, 96 bridge frames, byte-equal copies",
       stp["actor_id"] == ACTOR and len(sp) == 96 and all(files[PKG_REL + "/" + p] == files[OUT_REL + "/" + p] for p in sp), len(sp))
    reg = json.loads(files[source["package"]["registry"]])
    ck("registry lists ONLY jiang-lan -> this set", list(reg["actors"]) == [ACTOR] and PKG_REL + "/" + reg["actors"][ACTOR] == source["package"]["sprite_set"])
    ck("palette scalars are '#rrggbb'", all(isinstance(v, str) and len(v) == 7 and v[0] == "#" and int(v[1:], 16) >= 0 for v in PAL.values()))
    ck("all written paths are under the assigned roots", all(r.startswith((OUT_REL + "/", PKG_REL + "/")) for r in files))
    return res


def main():
    mode = sys.argv[1] if len(sys.argv) > 1 else "check"
    if mode not in ("build", "check"):
        raise SystemExit("usage: build|check")
    pins_before = pins_state()
    fsets, files, source = build_all()
    _, files2, _ = build_all()
    det = files.keys() == files2.keys() and all(files[k] == files2[k] for k in files)
    listing_rel = f"{OUT_REL}/{fname('file-list', 'json')}"
    files[listing_rel] = (json.dumps({"run": f"{STAMP}-{RUN}", "hash": "sha256-bytes",
                                      "files": {r: sha(b) for r, b in sorted(files.items())}}, indent=2) + "\n").encode()
    if mode == "build":
        for rel, b in files.items():
            p = rp(rel)
            if os.path.exists(_fs(p)) and rb(p) != b:
                raise SystemExit(f"refusing to overwrite different bytes: {rel}")
        mx.write_all(files)
        print(f"WROTE {len(files)} files")
    fails = []
    n_ok = 0
    for rel, b in files.items():
        try:
            if rb(rp(rel)) == b:
                n_ok += 1
            else:
                fails.append(f"rebuild differs {rel}")
        except OSError:
            fails.append(f"missing {rel}")
    print(f"REBUILD {n_ok}/{len(files)}  DETERMINISTIC {det}")
    if not det:
        fails.append("non-deterministic build")
    sc = source_checks(fsets, files, source)
    for c in sc:
        if not c["pass"]:
            fails.append("source " + c["check"])
    print(f"SOURCE {sum(c['pass'] for c in sc)}/{len(sc)}")
    pins_after = pins_state()
    pins_ok = all(pins_before.values()) and all(pins_after.values())
    if not pins_ok:
        fails.append("neutral source pins drifted")
    summary = {d: {k: source["contact_check"][d][k] for k in (
        "walk_max_world_slip_src_at_40ms_boundaries", "walk_planted_foot_world_excursion_src_60fps_samples",
        "flight_phases", "stop_bridge_grounded_slip_src_max")} for d in DIRS}
    print(json.dumps(summary))
    res = {"tool_sha256_text_lf_v1": source["tool"]["sha256_text_lf_v1"], "rebuild": {"checked": len(files), "ok": n_ok},
           "deterministic": det, "neutral_pins_exact_before_after": pins_ok, "source_checks": sc, "contacts": summary,
           "not_run": ["Pixelorama native export", "Godot import/runtime", "normal-speed movie"], "fails": fails}
    print("RESULT", "PASS" if not fails else "FAIL", json.dumps(fails[:12]))
    out = rp(f"{OUT_REL}/{fname('check-result', 'json')}")
    os.makedirs(_fs(os.path.dirname(out)), exist_ok=True)
    with open(_fs(out), "wb") as fh:
        fh.write((json.dumps(res, indent=2) + "\n").encode())
    return 0 if not fails else 1


if __name__ == "__main__":
    sys.exit(main())
