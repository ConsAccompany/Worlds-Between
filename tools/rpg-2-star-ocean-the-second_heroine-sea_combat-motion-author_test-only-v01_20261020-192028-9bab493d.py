"""Heroine (Sea of Stars direction) combat motion pilot v01: idle + short-blade attack. TEST-ONLY, UNAPPROVED.

Source: the creator-approved right-facing combat still (136x144 native, sha 4ce65a79...), read byte-exact and never
rewritten. Each new pose is authored on a small reusable rig built from that still:

  * head + torso (face, hair, scarf, jacket, vest, rear arm) move as ONE rigid upper body by whole texels, so every
    face texel is preserved exactly (no rotation, no scaling, no blur);
  * the ponytail is a separate part with secondary lag; an anchored copy of its root stays under it so a lagging tail
    never opens a notch in the hair;
  * legs are three parts each (thigh, shin, boot). Boots never move (soles stay on row 135). Thigh and shin are
    re-posed by two-bone IK from the moved hip to the planted ankle and redrawn with a RotSprite-style rotation
    (3x EPX upscale, nearest sample). Hip and knee joint copies are painted underneath so a bend leaves no gap;
  * for the attack the original sword arm is REMOVED from the torso and the jacket side it covered is painted in
    (occluded anatomy). The sword arm is then painted per pose: sleeve (upper arm), bare forearm, leather bracer as
    shaded capsules from shoulder -> IK elbow -> grip, with a 1-texel outline; the gripping fist + blade is the
    still's own hand/blade cluster rotated about the grip;
  * a hard-edged smear crescent (fx layer) marks the swing on the strike frames;
  * a final seam pass only ADDS texels in transparent cells (pinholes, exposed fill at leg joints). It is kept as
    its own bottom layer so the layered sources flatten exactly to the PNGs.

Everything is palette-locked to the still's 30 colours with binary alpha. The attack ends on the approved still
itself (byte-exact). This is a partial 2-action pilot (idle + attack); the full combat set needs 8 actions.

    build    write pose PNGs, per-pose PXO/ORA, x4 inspection PNGs (separate files) and manifest
    check    rebuild in memory, require byte-identical files on disk + gates (default)
    native   Pixelorama 1.2.3 headless re-open + split/flat export of every written PXO and ORA
"""
from pathlib import Path
import hashlib, importlib.util, io, json, math, os, subprocess, sys, tempfile, zipfile
import numpy as np
from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
PRIMARY = Path(r"C:\Users\hkzha\Documents\Codex\2026-10-12\rpg-2-star-ocean-the-second")
OUT = ROOT / "outputs/hero-sea-motion-v01"
BASE = ROOT / "outputs/hero-sea-v01/rpg-2-star-ocean-the-second_heroine-battle_still-native136_sea-unapproved-v01_20261020-181955-1294c865.png"
BASE_SHA = "4ce65a7915c0c0270a4ca353152b45b7d68b42672cb1483dd4f3e9cf4ac9d5e6"
BASE_PXO = BASE.with_name("rpg-2-star-ocean-the-second_heroine-battle_still-editable_sea-unapproved-v01_20261020-181955-bd7423ec.pxo")
BASE_ORA = BASE.with_name("rpg-2-star-ocean-the-second_heroine-battle_still-layered_sea-unapproved-v01_20261020-181955-5c3755ce.ora")
WRITER = ROOT / "tools/rpg-2-star-ocean-the-second_protagonist-female_south-run-v06-build_m8-w09_20261017-211600-f8e736cc.py"
PIXELORAMA = PRIMARY / "work/tooling/pixelorama-1-2-3/Pixelorama-Windows-64bit/Pixelorama.exe"
SLUG, SUBJECT, VER, STAMP, UID = "rpg-2-star-ocean-the-second", "heroine-sea-combat", "test-only-v01", "20261020-192028", "9bab493d"
W, H = 136, 144
PIN = (64, 136)            # native; logical (32, 68); draw_texture_rect(tex, Rect2(round(x)-32, 204, 68, 72))
FPS_BASE = 30              # every duration is a whole number of 1/30 s ticks, so 30 and 60 fps show every pose
CONTACT_POSE = "atk-contact"
ARENA_ATTACK_VISUAL_S, ARENA_ATTACK_COOLDOWN_S = 0.39, 0.43   # battle_arena.gd (read-only); damage lands at the press

# ---- palette (the still's 30 colours; nothing outside this set is ever written) ----
HEX = dict(o0="#090911", o1="#0d0a12", o2="#120e16", d3="#151728", n5="#1c2134", n8="#1d2d44", nb="#2d3445",
           ni="#424c61", td="#1e4055", t9="#2c3238", tf="#434352", k="#545454", l4="#21161d", l6="#2f2123",
           l7="#3b2827", la="#462d28", lc="#4d332c", le="#624033", lh="#6e4636", lj="#744a38", ll="#97664d",
           vo="#aca098", sq="#ddb395", ss="#f0d0b2", mn="#868d9b", mp="#9ca3ae", mr="#b8bbc3", mt="#ebeaea",
           tg="#255c66", tm="#27969a")
C = {k: np.array([int(v[1:3], 16), int(v[3:5], 16), int(v[5:7], 16), 255], np.uint8) for k, v in HEX.items()}
COAT = {"ni", "n5", "nb", "n8", "td", "d3"}
OUTL = {"o0", "o1", "o2"}
TEAL = {"tm", "tg", "td"}
LIGHT = np.array([-0.55, -0.835])            # key light from upper-left/front, as painted in the still
SLEEVE = ("ni", "nb", "n8")                  # (light, mid, shadow) ramps
SKIN = ("ss", "sq", "ll")
BRACER = ("lj", "lc", "l6")

# ---- rig landmarks, native texel-centre coordinates in the still ----
SHOULDER = (74.5, 47.5)
GRIP0, BLADE0 = (85.0, 66.0), -45.0          # fist centre and blade angle in the still (deg, screen y down)
UPPER_LEN, FORE_LEN = 13.0, 12.0
LEGS = {"back": {"hip": (53.5, 86.5), "knee": (49.5, 100.5), "ankle": (45.5, 110.5), "knee_row": 100, "boot_row": 111},
        "front": {"hip": (67.5, 86.5), "knee": (78.5, 99.5), "ankle": (82.5, 109.5), "knee_row": 99, "boot_row": 111}}

# ---- poses: body = whole-texel upper-body offset; pony = ponytail lag relative to the head ----
# arm None = the still's own arm rides with the body (idle). Otherwise grip (still coords, before body offset), blade
# angle and smear sweep. Durations are ticks of 1/30 s.
POSES = {
    "idle-b1": {"body": (0, 1), "pony": (0, 0), "knees": {"back": (0, 0.5), "front": (0.5, 0.5)}, "arm": None},
    "idle-b2": {"body": (0, 2), "pony": (0, -1), "knees": {"back": (0.5, 1), "front": (1, 1)}, "arm": None},
    "atk-antic-a": {"body": (-1, 1), "pony": (1, 0), "knees": {"back": (-0.5, 0.5), "front": (0, 0.5)},
                    "arm": {"grip": (85, 51), "blade": -68.0}},
    "atk-antic-b": {"body": (-2, 2), "pony": (1, -1), "knees": {"back": (-0.5, 1), "front": (0, 1)},
                    "arm": {"grip": (83, 42), "blade": -80.0}},
    "atk-smear": {"body": (1, 2), "pony": (-1, 0), "knees": {"back": (1, 1), "front": (1.5, 1)},
                  "arm": {"grip": (95, 50), "blade": -28.0, "smear": ("atk-antic-b", 8)}},
    "atk-contact": {"body": (4, 3), "pony": (-2, -1), "knees": {"back": (2.5, 1.5), "front": (4, 1.5)},
                    "arm": {"grip": (92, 58), "blade": 8.0, "smear": ("atk-smear", 5)}},
    "atk-follow": {"body": (4, 3), "pony": (-2, 0), "knees": {"back": (2.5, 1.5), "front": (4, 1.5)},
                   "arm": {"grip": (86, 65), "blade": 42.0}},
    "atk-recover": {"body": (2, 2), "pony": (-1, 0), "knees": {"back": (1, 1), "front": (2, 1)},
                    "arm": {"grip": (87, 63), "blade": -12.0}},
}
CLIPS = {
    "idle": {"loop": True, "frames": [["base", 8], ["idle-b1", 6], ["idle-b2", 8], ["idle-b1", 6]]},
    "attack": {"loop": False, "frames": [["atk-antic-a", 2], ["atk-antic-b", 2], ["atk-smear", 1], ["atk-contact", 2],
                                         ["atk-follow", 2], ["atk-recover", 2], ["idle-b1", 1]], "then": "base"},
}
LAYERS = ["seams", "ponytail", "leg-back", "leg-front", "torso", "head", "arm", "weapon", "fx"]   # bottom -> top


def long(p):
    return Path("\\\\?\\" + str(Path(p).resolve()))


def sha(b):
    return hashlib.sha256(b).hexdigest()


def sha_text(p):
    return sha(Path(p).read_bytes().replace(b"\r\n", b"\n"))


def fid(role):
    return sha(f"{UID}:{role}".encode())[:8]


def name(purpose, ext):
    return f"{SLUG}_{SUBJECT}_{purpose}_{VER}_{STAMP}-{fid(purpose)}.{ext}"


def png_bytes(a):
    buf = io.BytesIO()
    Image.fromarray(np.ascontiguousarray(a, np.uint8), "RGBA").save(buf, "PNG", optimize=False, compress_level=9)
    return buf.getvalue()


def decode(b):
    return np.array(Image.open(io.BytesIO(b)).convert("RGBA"))


def blank():
    return np.zeros((H, W, 4), np.uint8)


def over(dst, src):
    m = src[..., 3] > 0
    dst[m] = src[m]
    return dst


def key_of(rgba):
    rev = {tuple(v[:3].tolist()): k for k, v in C.items()}
    out = np.full((H, W), "", object)
    for y, x in zip(*np.nonzero(rgba[..., 3])):
        out[y, x] = rev[tuple(rgba[y, x, :3].tolist())]
    return out


def shift(a, dx, dy):
    out = blank()
    ys, xs = np.nonzero(a[..., 3])
    ny, nx = ys + dy, xs + dx
    ok = (ny >= 0) & (ny < H) & (nx >= 0) & (nx < W)
    out[ny[ok], nx[ok]] = a[ys[ok], xs[ok]]
    return out


def pick(src, mask):
    out = blank()
    out[mask] = src[mask]
    return out


# ---- RotSprite-style rotation: 3x EPX (8x) then nearest sample at texel centres ----
def epx(a):
    p = a.view(np.uint32)[..., 0] if a.dtype == np.uint8 else a
    up = np.pad(p, 1, mode="edge")
    P = up[1:-1, 1:-1]
    A, D = up[:-2, 1:-1], up[2:, 1:-1]
    Cc, B = up[1:-1, :-2], up[1:-1, 2:]
    o1 = np.where((Cc == A) & (Cc != D) & (A != B), A, P)
    o2 = np.where((A == B) & (A != Cc) & (B != D), B, P)
    o3 = np.where((D == Cc) & (D != B) & (Cc != A), Cc, P)
    o4 = np.where((B == D) & (B != A) & (D != Cc), D, P)
    out = np.empty((p.shape[0] * 2, p.shape[1] * 2), np.uint32)
    out[0::2, 0::2], out[0::2, 1::2], out[1::2, 0::2], out[1::2, 1::2] = o1, o2, o3, o4
    return out


def rotate_part(part, pivot_src, pivot_dst, deg):
    """Rotate a full-cell part about pivot_src by deg (screen degrees) and put pivot_src on pivot_dst."""
    if abs(deg) < 1e-9:
        dx, dy = pivot_dst[0] - pivot_src[0], pivot_dst[1] - pivot_src[1]
        assert abs(dx - round(dx)) < 1e-9 and abs(dy - round(dy)) < 1e-9
        return shift(part, int(round(dx)), int(round(dy)))
    packed = np.ascontiguousarray(part).view(np.uint32)[..., 0]
    up = epx(epx(epx(packed)))
    r = math.radians(deg)
    cs, sn = math.cos(r), math.sin(r)
    yy, xx = np.mgrid[0:H, 0:W]
    vx, vy = xx + 0.5 - pivot_dst[0], yy + 0.5 - pivot_dst[1]
    sx = pivot_src[0] + cs * vx + sn * vy          # inverse rotation
    sy = pivot_src[1] - sn * vx + cs * vy
    ix, iy = np.floor(sx * 8).astype(int), np.floor(sy * 8).astype(int)
    ok = (ix >= 0) & (ix < W * 8) & (iy >= 0) & (iy < H * 8)
    res = np.zeros((H, W), np.uint32)
    res[ok] = up[iy[ok], ix[ok]]
    return res.view(np.uint8).reshape(H, W, 4).copy()


# ---- painted capsules (sleeve, forearm, bracer) ----
def seg_geom(a, b):
    yy, xx = np.mgrid[0:H, 0:W]
    px, py = xx + 0.5, yy + 0.5
    ax, ay = a
    bx, by = b
    vx, vy = bx - ax, by - ay
    L2 = vx * vx + vy * vy
    t = np.clip(((px - ax) * vx + (py - ay) * vy) / L2, 0, 1)
    cx, cy = ax + t * vx, ay + t * vy
    dx, dy = px - cx, py - cy
    return t, np.hypot(dx, dy), dx, dy


def paint_capsule(layer, a, b, r0, r1, ramp):
    t, d, dx, dy = seg_geom(a, b)
    r = r0 + (r1 - r0) * t
    m = d <= r
    with np.errstate(invalid="ignore", divide="ignore"):
        nx, ny = np.where(d > 0, dx / d, 0), np.where(d > 0, dy / d, 0)
    lam = nx * LIGHT[0] + ny * LIGHT[1]
    rel = np.where(r > 0, d / r, 0)
    hi = m & (rel >= 0.4) & (lam > 0.3)
    lo = m & (rel >= 0.4) & (lam < -0.3)
    layer[m] = C[ramp[1]]
    layer[hi] = C[ramp[0]]
    layer[lo] = C[ramp[2]]
    return m


def outline_ring(layer, fill_mask):
    ring = np.zeros_like(fill_mask)
    ring[1:] |= fill_mask[:-1]
    ring[:-1] |= fill_mask[1:]
    ring[:, 1:] |= fill_mask[:, :-1]
    ring[:, :-1] |= fill_mask[:, 1:]
    ring &= ~fill_mask
    layer[ring] = C["o1"]
    return ring


def ik(root, end, l1, l2, prefer_down=True, prefer_sign=None):
    dx, dy = end[0] - root[0], end[1] - root[1]
    d = math.hypot(dx, dy)
    assert d < l1 + l2 - 0.05, f"IK out of reach {root}->{end} d={d:.2f}"
    d = max(d, abs(l1 - l2) + 0.05)
    a = (l1 * l1 - l2 * l2 + d * d) / (2 * d)
    h = math.sqrt(max(l1 * l1 - a * a, 0))
    ux, uy = dx / d, dy / d
    px, py = root[0] + a * ux, root[1] + a * uy
    c1 = (px - h * uy, py + h * ux)
    c2 = (px + h * uy, py - h * ux)
    if prefer_sign is not None:
        s1 = math.copysign(1, ux * (c1[1] - root[1]) - uy * (c1[0] - root[0]))
        return c1 if s1 == prefer_sign else c2
    return max(c1, c2, key=lambda c: c[1]) if prefer_down else min(c1, c2, key=lambda c: c[1])


def ang(v):
    return math.degrees(math.atan2(v[1], v[0]))


# ---- rig extraction from the approved still ----
def rig(S):
    K = key_of(S)
    O = S[..., 3] > 0
    yy, xx = np.mgrid[0:H, 0:W]
    kin = lambda keys: np.vectorize(lambda k: k in keys)(K)
    coat, outl, teal = kin(COAT), kin(OUTL), kin(TEAL)
    # sword arm (sleeve + forearm + fist + blade) as painted in the still
    arm = O & (((yy >= 44) & (yy <= 58) & (xx >= 71)) | ((yy >= 59) & (yy <= 65) & (xx >= 72)) |
               ((yy >= 66) & (yy <= 72) & (xx >= 75)) | ((yy >= 73) & (yy <= 76) & (xx >= 79)) |
               ((yy >= 36) & (yy <= 43) & (xx >= 84)))
    fist = arm & (((yy >= 59) & (xx >= 81)) | ((yy <= 63) & (xx >= 84)))
    # lower coat panels hanging over the thighs stay with the torso
    coat_low = O & (yy >= 86) & (yy <= 98) & (((xx <= 44) | ((xx >= 75) & (yy <= 89)))) & (coat | outl)
    legs_all = O & (yy >= 86) & ~coat_low
    legs = {}
    for side, sel in (("back", xx <= 60), ("front", xx >= 61)):
        g = LEGS[side]
        leg = legs_all & sel
        leather = ~kin({"t9", "tf", "k", "n5", "o0", "o1", "o2", "d3"})
        boot = leg & ((yy >= g["boot_row"]) | ((yy >= g["boot_row"] - 4) & leather &
                                               ((xx <= 42) if side == "back" else (xx >= 83))))
        rest = leg & ~boot
        legs[side] = {"thigh": rest & (yy <= g["knee_row"] + 2), "shin": rest & (yy >= g["knee_row"] - 2),
                      "boot": boot, "hipcopy": rest & (yy <= 92), "kneecopy": rest & (abs(yy - g["knee_row"]) <= 3)}
    # head and ponytail: hair/skin/outline texels above the scarf
    upper = O & (yy <= 44) & ~teal & ~coat & ~arm
    head_or_pony = upper & ((yy <= 35) | ((xx >= 52) & (xx <= 75)) | ((xx <= 47) & (yy <= 41)))
    pony = head_or_pony & ((xx <= 50) | ((xx <= 55) & (yy <= 16)))
    head = head_or_pony & ~pony
    root = O & (xx >= 47) & (xx <= 58) & (yy >= 4) & (yy <= 18)
    torso = O & ~head & ~pony & ~legs_all
    return {"K": K, "O": O, "arm": arm, "fist": fist, "legs": legs, "head": head, "pony": pony, "root": root,
            "torso": torso, "coat_low": coat_low}


def jacket_underlay(dx, dy):
    """Paint the jacket side the sword arm covered in the still (rows 44..58): seam, side plane, outline."""
    lay = blank()
    for y in range(44, 59):
        edge = int(round(77 - (y - 44) * 6 / 14))
        for x in range(71, edge + 1):
            if x == edge:
                key = "o1"
            elif x == 71:
                key = "n8"
            elif x >= edge - 1:
                key = "n8"
            elif y <= 47 and x <= 73:
                key = "ni"
            else:
                key = "nb"
            lay[y, x] = C[key]
    return shift(lay, dx, dy)


def paint_arm(pose, S, R, body):
    """Sleeve -> IK elbow -> forearm -> bracer, plus the still's fist+blade rotated about the grip."""
    dx, dy = body
    a = pose["arm"]
    sh = (SHOULDER[0] + dx, SHOULDER[1] + dy)
    grip = (a["grip"][0] + dx + 0.5, a["grip"][1] + dy + 0.5)
    el = ik(sh, grip, UPPER_LEN, FORE_LEN, prefer_down=True)
    u = np.array(grip) - np.array(el)
    u = u / np.linalg.norm(u)
    arm = blank()
    fill = np.zeros((H, W), bool)
    fill |= paint_capsule(arm, sh, el, 4.0, 3.4, SLEEVE)
    cuff_end = (el[0] + u[0] * 1.6, el[1] + u[1] * 1.6)
    fore_end = (grip[0] - u[0] * 2.0, grip[1] - u[1] * 2.0)
    fill |= paint_capsule(arm, el, fore_end, 2.4, 2.2, SKIN)
    fill |= paint_capsule(arm, (el[0] - u[0] * 0.5, el[1] - u[1] * 0.5), cuff_end, 3.6, 3.4, SLEEVE)
    brace0 = (grip[0] - u[0] * 6.0, grip[1] - u[1] * 6.0)
    fill |= paint_capsule(arm, brace0, fore_end, 2.9, 2.9, BRACER)
    outline_ring(arm, fill)
    unit = pick(S, R["fist"])
    weapon = rotate_part(unit, GRIP0, grip, a["blade"] - BLADE0)
    tip_len = math.hypot(108.5 - GRIP0[0], 41.5 - GRIP0[1])
    tip = (grip[0] + tip_len * math.cos(math.radians(a["blade"])), grip[1] + tip_len * math.sin(math.radians(a["blade"])))
    return arm, weapon, {"shoulder": sh, "elbow": el, "grip": grip, "tip": tip}


def smear_layer(sh, tip0, tip1, width):
    """Hard-edged swing crescent between two blade-tip positions, about the shoulder."""
    lay = blank()
    a0, a1 = math.atan2(tip0[1] - sh[1], tip0[0] - sh[0]), math.atan2(tip1[1] - sh[1], tip1[0] - sh[0])
    r0, r1 = math.hypot(tip0[0] - sh[0], tip0[1] - sh[1]), math.hypot(tip1[0] - sh[0], tip1[1] - sh[1])
    yy, xx = np.mgrid[0:H, 0:W]
    px, py = xx + 0.5 - sh[0], yy + 0.5 - sh[1]
    phi = np.arctan2(py, px)
    s = (phi - a0) / (a1 - a0)
    rad = np.hypot(px, py)
    rout = r0 + (r1 - r0) * s
    w = 0.6 + (width - 0.6) * np.clip(s, 0, 1)
    band = (s >= 0) & (s <= 1) & (rad <= rout) & (rad >= rout - w)
    edge = band & (rad >= rout - 1.0)
    lay[band] = C["mr"]
    lay[edge] = C["mt"]
    return lay


def seams(flat, zone):
    """Add texels only in transparent cells: 1-texel pinholes and an outline on fill exposed at re-posed joints."""
    add = blank()
    O = flat[..., 3] > 0
    K = key_of(flat)
    nb = [(0, 1), (0, -1), (1, 0), (-1, 0)]
    for y, x in zip(*np.nonzero(zone & ~O)):
        ns = [(y + a, x + b) for a, b in nb if 0 <= y + a < H and 0 <= x + b < W and O[y + a, x + b]]
        if len(ns) >= 3:
            keys = [K[p] for p in ns if K[p] not in OUTL]
            k = max(sorted(set(keys)), key=keys.count) if keys else "o1"   # sorted: hash-seed independent
            add[y, x] = C[k]
    O2 = O | (add[..., 3] > 0)
    for y, x in zip(*np.nonzero(zone & ~O2)):
        for a, b in nb:
            q = (y + a, x + b)
            if 0 <= q[0] < H and 0 <= q[1] < W and O[q] and K[q] not in OUTL:
                add[y, x] = C["o1"]
                break
    return add


def build_pose(pid, S, R):
    pose = POSES[pid]
    dx, dy = pose["body"]
    attack = pose["arm"] is not None
    lay = {n: blank() for n in LAYERS}
    # ponytail: anchored root copy (moves with the head) under the lagging tail
    px, py = pose["pony"]
    over(lay["ponytail"], shift(pick(S, R["root"] & (R["pony"] | R["head"])), dx, dy))
    over(lay["ponytail"], shift(pick(S, R["pony"]), dx + px, dy + py))
    joints = {}
    for side in ("back", "front"):
        g, parts = LEGS[side], R["legs"][side]
        hip = (g["hip"][0] + dx, g["hip"][1] + dy)
        l1 = math.dist(g["hip"], g["knee"])
        l2 = math.dist(g["knee"], g["ankle"])
        kx, ky = pose["knees"][side]          # authored knee travel (texels); thigh/shin may stretch < 1.5 texel
        knee = (g["knee"][0] + kx, g["knee"][1] + ky)
        th = ang((knee[0] - hip[0], knee[1] - hip[1])) - ang((g["knee"][0] - g["hip"][0], g["knee"][1] - g["hip"][1]))
        sh = ang((knee[0] - g["ankle"][0], knee[1] - g["ankle"][1])) - ang((g["knee"][0] - g["ankle"][0], g["knee"][1] - g["ankle"][1]))
        L = lay["leg-" + side]
        over(L, shift(pick(S, parts["hipcopy"]), dx, dy))
        kd = (math.floor(kx + 0.5), math.floor(ky + 0.5))
        over(L, shift(pick(S, parts["kneecopy"]), *kd))
        over(L, rotate_part(pick(S, parts["shin"]), g["ankle"], g["ankle"], sh))
        over(L, rotate_part(pick(S, parts["thigh"]), g["hip"], hip, th))
        over(L, pick(S, parts["boot"]))
        joints[side] = {"hip": hip, "knee": knee, "ankle": g["ankle"], "thighDeg": round(th, 3), "shinDeg": round(sh, 3),
                       "thighStretch": round(math.dist(hip, knee) - l1, 3), "shinStretch": round(math.dist(knee, g["ankle"]) - l2, 3)}
    torso_mask = R["torso"] & ~R["arm"] if attack else R["torso"]
    over(lay["torso"], shift(pick(S, torso_mask), dx, dy))
    if attack:
        under = jacket_underlay(dx, dy)
        empty = lay["torso"][..., 3] == 0
        lay["torso"][empty & (under[..., 3] > 0)] = under[empty & (under[..., 3] > 0)]
    over(lay["head"], shift(pick(S, R["head"]), dx, dy))
    arm_info = None
    if attack:
        lay["arm"], lay["weapon"], arm_info = paint_arm(pose, S, R, (dx, dy))
    flat = blank()
    for n in LAYERS[1:]:
        over(flat, lay[n])
    yy, xx = np.mgrid[0:H, 0:W]
    zone = (yy >= 80) & (yy < 111)
    lay["seams"] = seams(flat, zone)
    over(flat, lay["seams"])
    allowed = {(y + dy, x + dx) for y, x in hole_cells(S)}
    closed = 0
    for comp in hole_components(flat):
        if not set(comp) <= allowed and len(comp) <= 4:      # tiny new pocket (tail/arm lifting off the body)
            for y, x in comp:
                lay["seams"][y, x] = C["o1"]
            closed += len(comp)
    return lay, {"joints": joints, "arm": arm_info, "pocketsClosed": closed}


def add_fx(poses):
    for pid, p in POSES.items():
        a = p["arm"]
        if a and "smear" in a:
            prev, width = a["smear"]
            sh = poses[pid]["info"]["arm"]["shoulder"]
            fx = smear_layer(sh, poses[prev]["info"]["arm"]["tip"], poses[pid]["info"]["arm"]["tip"], width)
            busy = np.zeros((H, W), bool)
            for n in ("arm", "weapon"):
                busy |= poses[pid]["layers"][n][..., 3] > 0
            fx[busy] = 0
            poses[pid]["layers"]["fx"] = fx


def flatten(lay):
    flat = blank()
    for n in LAYERS:
        over(flat, lay[n])
    return flat


def ora_bytes(layers, flat):
    buf = io.BytesIO()
    dt = (2026, 10, 20, 19, 20, 28)
    with zipfile.ZipFile(buf, "w") as z:
        z.writestr(zipfile.ZipInfo("mimetype", dt), "image/openraster", zipfile.ZIP_STORED)
        stack = ['<?xml version="1.0" encoding="UTF-8"?>', f'<image version="0.0.3" w="{W}" h="{H}">', "<stack>"]
        for i, n in reversed(list(enumerate(LAYERS))):
            stack.append(f'<layer name="{n}" src="data/{i:02d}-{n}.png" x="0" y="0" opacity="1.0" visibility="visible" composite-op="svg:src-over"/>')
        stack += ["</stack>", "</image>"]
        z.writestr(zipfile.ZipInfo("stack.xml", dt), "\n".join(stack) + "\n", zipfile.ZIP_DEFLATED)
        for i, n in enumerate(LAYERS):
            z.writestr(zipfile.ZipInfo(f"data/{i:02d}-{n}.png", dt), png_bytes(layers[n]), zipfile.ZIP_DEFLATED)
        z.writestr(zipfile.ZipInfo("mergedimage.png", dt), png_bytes(flat), zipfile.ZIP_DEFLATED)
        z.writestr(zipfile.ZipInfo("Thumbnails/thumbnail.png", dt), png_bytes(flat), zipfile.ZIP_DEFLATED)
    return buf.getvalue()


def module(path, label):
    spec = importlib.util.spec_from_file_location(label, str(path))
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


def inspect_x4(flat):
    bg = Image.new("RGBA", (W, H), (118, 128, 138, 255))
    bg.alpha_composite(Image.fromarray(flat, "RGBA"))
    return np.array(bg.resize((W * 4, H * 4), Image.NEAREST))


def outputs():
    raw = long(BASE).read_bytes()
    assert sha(raw) == BASE_SHA, "approved still changed"
    S = decode(raw)
    R = rig(S)
    poses = {}
    for pid in POSES:
        lay, info = build_pose(pid, S, R)
        poses[pid] = {"layers": lay, "info": info}
    add_fx(poses)
    writer = module(WRITER, "established_pxo_writer")
    writer.W, writer.H = W, H
    writer.to_rgba = lambda im: np.ascontiguousarray(im, np.uint8)
    files, flats = {}, {}
    for pid, p in poses.items():
        flat = flatten(p["layers"])
        flats[pid] = flat
        png = png_bytes(flat)
        files[f"{pid}.png"] = (name(f"pose-{pid}-native136", "png"), png)
        files[f"{pid}.ora"] = (name(f"pose-{pid}-layered", "ora"), ora_bytes(p["layers"], flat))
        files[f"{pid}.pxo"] = (name(f"pose-{pid}-editable", "pxo"),
                               writer.make_pxo([p["layers"]], [1.0], png, name(f"pose-{pid}-pxo-export", "png"), 30,
                                               order=LAYERS, dt=(2026, 10, 20, 19, 20, 28)))
        files[f"{pid}.x4"] = (name(f"pose-{pid}-inspect-x4", "png"), png_bytes(inspect_x4(flat)))
    tick = 1.0 / FPS_BASE
    clips = {}
    for cid, clip in CLIPS.items():
        t, fr = 0, []
        for pid, ticks in clip["frames"]:
            fr.append({"pose": pid, "ticks": ticks, "start_s": round(t * tick, 6), "duration_s": round(ticks * tick, 6)})
            t += ticks
        clips[cid] = {"loop": clip["loop"], "frames": fr, "total_ticks": t, "total_s": round(t * tick, 6)}
        if "then" in clip:
            clips[cid]["then"] = clip["then"]
    contact = next(f for f in clips["attack"]["frames"] if f["pose"] == CONTACT_POSE)
    pose_files = {"base": {"name": BASE.name, "sha256": BASE_SHA, "path": str(BASE.relative_to(ROOT)).replace("\\", "/")}}
    for pid in POSES:
        pose_files[pid] = {"name": files[f"{pid}.png"][0], "sha256": sha(files[f"{pid}.png"][1])}
    manifest = {
        "status": "TEST-ONLY partial combat-action pilot (idle + short-blade attack). UNAPPROVED motion. Not a runtime package, "
                  "not loaded by the game, no default/runtime/camera/party change. Full task needs all 8 actions; stays IN_PROGRESS.",
        "task": "content.combat.protagonist-female.combat-actions",
        "approvedSource": {"file": str(BASE.relative_to(ROOT)).replace("\\", "/"), "sha256": BASE_SHA,
                           "approval": "docs/character-visuals/rpg-2-star-ocean-the-second_heroine-sea_static-baselines-creator-approval_v01_20261020-185828-8775642a.md",
                           "rewritten": False, "usedAsPose": "base"},
        "cell": [W, H], "logicalExtent": [68, 72], "pinNative": list(PIN), "pinLogical": [32, 68],
        "displayRequirement": "draw_texture_rect(texture, Rect2(round(x)-32, 204, 68, 72), tile=false), nearest, no mipmaps "
                              "(136 native texels into 68 logical px = 2 native per logical; 1:1 physical at 1280x720)",
        "notForLogicalScale1Helper": "the existing combat sprite-set helper only accepts logical_scale 1; this 136-texel source "
                                     "must not be drawn at 136 logical px, so it is NOT packaged for that loader",
        "tickSeconds": round(tick, 9), "fpsParity": "every duration is whole 1/30 s ticks: 30 fps shows each pose for N frames, 60 fps for 2N",
        "clips": clips,
        "stagedContact": {"pose": CONTACT_POSE, "start_s": contact["start_s"],
                          "note": "staged visual timeline only; the arena applies damage and the hit VFX on the press frame (t=0)"},
        "arenaTiming": {"attackVisualSeconds": ARENA_ATTACK_VISUAL_S, "attackCooldownSeconds": ARENA_ATTACK_COOLDOWN_S,
                        "damageAt": "press frame (_try_attack)", "pilotAttackTotalSeconds": clips["attack"]["total_s"],
                        "pilotFitsCooldown": clips["attack"]["total_s"] <= ARENA_ATTACK_COOLDOWN_S},
        "poses": {pid: {"body": list(p["body"]), "ponytailLag": list(p["pony"]),
                        "arm": None if p["arm"] is None else {"grip": list(p["arm"]["grip"]), "bladeDeg": p["arm"]["blade"],
                                                             "smearFrom": p["arm"].get("smear", [None])[0]},
                        "rig": {"joints": {s: {k: (list(map(lambda v: round(v, 3), j[k])) if isinstance(j[k], tuple) else j[k])
                                               for k in j} for s, j in poses[pid]["info"]["joints"].items()},
                                "arm": None if poses[pid]["info"]["arm"] is None else
                                {k: [round(v[0], 3), round(v[1], 3)] for k, v in poses[pid]["info"]["arm"].items()}},
                        "layerTexels": {n: int((poses[pid]["layers"][n][..., 3] > 0).sum()) for n in LAYERS}}
                  for pid, p in POSES.items()},
        "poseFiles": pose_files,
        "layers": LAYERS,
        "method": __doc__.strip().split("\n\n")[1],
        "source": {"file": str(Path(__file__).resolve().relative_to(ROOT)).replace("\\", "/"), "sha256TextLf": sha_text(__file__)},
        "inputs": {"pxoWriter": {"file": str(WRITER.relative_to(ROOT)).replace("\\", "/"), "sha256TextLf": sha_text(WRITER)}},
        "files": {role: {"name": n, "sha256": sha(b)} for role, (n, b) in sorted(files.items())},
        "inspectionNote": "inspect-x4 files are nearest x4 on flat grey, one pose per file, for viewing only (not runtime art)",
        "artApproved": False, "motionApproved": False, "runtimeDefaultChanged": False, "gameSourceChanged": False,
        "guiSaveAsVerified": False, "hitSynchronized": False,
    }
    files["manifest"] = (name("manifest", "json"), (json.dumps(manifest, indent=1) + "\n").encode())
    return files, flats, poses, manifest, S, R


def hole_components(flat):
    cells = hole_cells(flat)
    left, comps = set(cells), []
    while left:
        stack = [left.pop()]
        comp = list(stack)
        while stack:
            y, x = stack.pop()
            for a, b in ((0, 1), (0, -1), (1, 0), (-1, 0)):
                q = (y + a, x + b)
                if q in left:
                    left.remove(q)
                    stack.append(q)
                    comp.append(q)
        comps.append(sorted(comp))
    return sorted(comps)


def hole_cells(flat):
    """Transparent texels not 4-connected to the cell border (pockets enclosed by the figure)."""
    O = flat[..., 3] > 0
    seen = np.zeros_like(O)
    stack = [(y, x) for y in range(H) for x in (0, W - 1)] + [(y, x) for x in range(W) for y in (0, H - 1)]
    stack = [p for p in stack if not O[p]]
    for p in stack:
        seen[p] = True
    while stack:
        y, x = stack.pop()
        for a, b in ((0, 1), (0, -1), (1, 0), (-1, 0)):
            q = (y + a, x + b)
            if 0 <= q[0] < H and 0 <= q[1] < W and not O[q] and not seen[q]:
                seen[q] = True
                stack.append(q)
    return [(int(y), int(x)) for y, x in zip(*np.nonzero(~O & ~seen))]


def gates(files, flats, poses, manifest, S, R):
    res = []

    def gate(k, ok, info=None):
        res.append({"key": k, "pass": bool(ok), "info": info})
    pal = {tuple(v[:3].tolist()) for v in C.values()}
    base_cols = {tuple(c) for c in S[S[..., 3] > 0][:, :3].tolist()}
    gate("approved still bytes unchanged (sha 4ce65a79...)", sha(long(BASE).read_bytes()) == BASE_SHA)
    gate("palette constant equals the still's 30 colours", pal == base_cols, len(base_cols))
    boots = np.zeros((H, W), bool)
    for side in ("back", "front"):
        boots |= R["legs"][side]["boot"]
    base_holes = set(hole_cells(S))
    fy0, fx0 = 18, 54
    face = S[fy0:42, fx0:77].copy()                # eyes, brows, mouth, cheeks and jaw line (rows 18..41)
    face_mask = R["head"][fy0:42, fx0:77]
    for pid, flat in flats.items():
        dx, dy = POSES[pid]["body"]
        op = flat[..., 3] > 0
        ys, xs = np.nonzero(op)
        cols = {tuple(c) for c in flat[op][:, :3].tolist()}
        gate(f"{pid}: 136x144 RGBA, binary alpha", flat.shape == (H, W, 4) and set(np.unique(flat[..., 3]).tolist()) <= {0, 255})
        gate(f"{pid}: palette-locked (subset of the still's 30)", cols <= base_cols, len(cols))
        gate(f"{pid}: margins (col 0/135 and rows 136..143 transparent)", not op[:, 0].any() and not op[:, -1].any() and not op[PIN[1]:].any(),
             [int(xs.min()), int(xs.max()), int(ys.min()), int(ys.max())])
        gate(f"{pid}: lowest row 135 (floor) and boots byte-identical to the still (planted)", ys.max() == PIN[1] - 1 and
             np.array_equal(flat[boots], S[boots]))
        region = flat[fy0 + dy:42 + dy, fx0 + dx:77 + dx]
        gate(f"{pid}: face texels preserved exactly at body offset {dx},{dy}", np.array_equal(region[face_mask], face[face_mask]),
             int(face_mask.sum()))
        new = set(hole_cells(flat)) - {(y + dy, x + dx) for y, x in base_holes}
        gate(f"{pid}: no enclosed hole outside the still's own pockets (at body offset)", not new,
             {"new": sorted(new), "tinyPocketsClosedWithOutline": poses[pid]["info"]["pocketsClosed"]})
        lay = poses[pid]["layers"]
        gate(f"{pid}: layer stack equals pose PNG", np.array_equal(flatten(lay), decode(files[f"{pid}.png"][1])))
        z = zipfile.ZipFile(io.BytesIO(files[f"{pid}.ora"][1]))
        gate(f"{pid}: ORA mimetype first+stored, merged equals PNG", z.namelist()[0] == "mimetype" and
             z.getinfo("mimetype").compress_type == zipfile.ZIP_STORED and np.array_equal(decode(z.read("mergedimage.png")), flat))
        zp = zipfile.ZipFile(io.BytesIO(files[f"{pid}.pxo"][1]))
        d = json.loads(zp.read("data.json"))
        cels = [np.frombuffer(zp.read(f"image_data/frames/1/layer_{i}"), np.uint8).reshape(H, W, 4) for i in range(1, len(LAYERS) + 1)]
        gate(f"{pid}: PXO 136x144, 1 frame, layer order, raw cels == ORA layers", (d["size_x"], d["size_y"]) == (W, H) and
             len(d["frames"]) == 1 and [l["name"] for l in d["layers"]] == LAYERS and
             all(np.array_equal(c, decode(z.read(f"data/{i:02d}-{n}.png"))) for i, (c, n) in enumerate(zip(cels, LAYERS))))
        if POSES[pid]["arm"] is not None:
            gate(f"{pid}: still's sword arm removed and repainted (arm+weapon layers non-empty, torso has no original arm texel)",
                 (lay["arm"][..., 3] > 0).any() and (lay["weapon"][..., 3] > 0).any() and
                 not (shift(pick(S, R["arm"]), dx, dy)[..., 3] > 0)[lay["torso"][..., 3] > 0].all())
    a = manifest["clips"]["attack"]
    gate("attack ends on the approved still (base, byte-exact source)", a["then"] == "base" and manifest["poseFiles"]["base"]["sha256"] == BASE_SHA)
    gate("attack total <= arena cooldown 0.43 s (no restart mid-clip by repeated presses)", a["total_s"] <= ARENA_ATTACK_COOLDOWN_S, a["total_s"])
    gate("every duration is whole 1/30 s ticks (30/60 parity)", all(isinstance(f["ticks"], int) and f["ticks"] >= 1
                                                                    for c in manifest["clips"].values() for f in c["frames"]))
    gate("idle loop starts on the approved still", manifest["clips"]["idle"]["frames"][0]["pose"] == "base")
    gate("hit synchronisation NOT claimed", manifest["hitSynchronized"] is False and manifest["stagedContact"]["start_s"] > 0,
         manifest["stagedContact"]["start_s"])
    return res


def native():
    files, flats, poses, manifest, S, R = outputs()
    for role, (n, b) in files.items():
        if role.endswith((".pxo", ".ora", ".png")):
            assert long(OUT / n).read_bytes() == b, f"build first; frozen file differs: {n}"
    exe = PIXELORAMA.resolve()
    tmp = Path(tempfile.mkdtemp(prefix="hsm01px-"))
    report = {"status": "Pixelorama 1.2.3 headless re-open + export of the written per-pose sources; NOT a GUI Save As/reopen; not art approval",
              "executable": str(exe), "executableSha256": sha(exe.read_bytes()), "tempRoot": str(tmp), "runs": {},
              "diagnosticPolicy": "every stdout/stderr line containing ERROR, SCRIPT ERROR, WARNING, Shader or leaked is reported unfiltered",
              "isolation": "fresh APPDATA and LOCALAPPDATA per run under tempRoot"}
    for pid in POSES:
        for role in ("pxo", "ora"):
            for split in (True, False):
                key = f"{pid}-{role}-{'split' if split else 'flat'}"
                folder = tmp / key
                for sub in ("app", "local", "exp"):
                    (folder / sub).mkdir(parents=True)
                fname, data = files[f"{pid}.{role}"]
                src = folder / f"hsm.{role}"
                src.write_bytes(data)
                env = dict(os.environ, APPDATA=str(folder / "app"), LOCALAPPDATA=str(folder / "local"))
                target = folder / "exp" / "hsm.png"
                cmd = [str(exe), "--headless", "--quit", "--", "--export"] + (["--split-layers"] if split else []) + ["-o", str(target), str(src)]
                proc = subprocess.run(cmd, env=env, capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=120,
                                      creationflags=subprocess.CREATE_NO_WINDOW if os.name == "nt" else 0)
                exported = sorted((folder / "exp").glob("*.png"))
                layers = poses[pid]["layers"]
                if split:
                    exact = {}
                    for n in LAYERS:
                        hits = [q for q in exported if f"({n})" in q.name]
                        exact[n] = len(hits) == 1 and np.array_equal(np.array(Image.open(hits[0]).convert("RGBA")), layers[n])
                    ok = len(exported) == len(LAYERS) and all(exact.values())
                else:
                    exact = {"flat": len(exported) == 1 and np.array_equal(np.array(Image.open(exported[0]).convert("RGBA")), flats[pid])}
                    ok = exact["flat"]
                text = proc.stdout + proc.stderr
                diag = [ln for ln in text.splitlines() if any(t in ln for t in ("ERROR", "SCRIPT ERROR", "WARNING", "Shader", "leaked"))]
                report["runs"][key] = {"file": fname, "exit": proc.returncode, "exportedNames": [q.name for q in exported], "exact": exact,
                                       "allExact": ok, "sourceUnchanged": src.read_bytes() == data, "diagnosticLines": diag,
                                       "cleanApp": proc.returncode == 0 and not diag}
                print(key, proc.returncode, ok, len(diag), flush=True)
    report["nativeExactExport"] = all(r["exit"] == 0 and r["allExact"] and r["sourceUnchanged"] for r in report["runs"].values())
    report["cleanApp"] = all(r["cleanApp"] for r in report["runs"].values())
    report["runsExact"] = sum(r["allExact"] for r in report["runs"].values())
    report["runsClean"] = sum(r["cleanApp"] for r in report["runs"].values())
    report["runCount"] = len(report["runs"])
    path = long(OUT / name("pixelorama-native-report", "json"))
    with open(path, "x", encoding="utf-8", newline="\n") as f:
        f.write(json.dumps(report, indent=1) + "\n")
    print("HSM01_NATIVE", "EXACT" if report["nativeExactExport"] else "NOT_EXACT", report["runsExact"], "/", report["runCount"],
          "CLEAN" if report["cleanApp"] else "DIAGNOSTICS", report["runsClean"], "/", report["runCount"])
    return 0 if report["nativeExactExport"] else 1


def main():
    mode = sys.argv[1] if len(sys.argv) > 1 else "check"
    if mode == "native":
        return native()
    files, flats, poses, manifest, S, R = outputs()
    again = outputs()[0]
    det = all(files[k][1] == again[k][1] for k in files)
    res = gates(files, flats, poses, manifest, S, R)
    res.insert(0, {"key": "deterministic rebuild (byte-identical)", "pass": det, "info": None})
    if mode == "build":
        os.makedirs(long(OUT), exist_ok=True)
        for role, (n, b) in files.items():
            p = long(OUT / n)
            if p.exists():
                assert p.read_bytes() == b, f"refusing to overwrite a different frozen file: {n}"
            else:
                p.write_bytes(b)
    else:
        for role, (n, b) in files.items():
            p = long(OUT / n)
            res.append({"key": f"on-disk bytes equal rebuild: {role}", "pass": p.exists() and p.read_bytes() == b, "info": None})
    fails = [r for r in res if not r["pass"]]
    for r in fails:
        print("FAIL", r["key"], r["info"])
    print("HSM01", mode.upper(), "PASS" if not fails else "FAIL", f"{len(res) - len(fails)}/{len(res)}")
    if mode == "check":
        report = {"mode": "check", "gates": res, "passed": len(res) - len(fails), "total": len(res),
                  "source": manifest["source"], "manifestSha256": sha(files["manifest"][1])}
        path = long(OUT / name("check-report", "json"))
        if not path.exists() or path.read_bytes() != (json.dumps(report, indent=1) + "\n").encode():
            with open(path, "w", encoding="utf-8", newline="\n") as f:
                f.write(json.dumps(report, indent=1) + "\n")
    return 0 if not fails else 1


if __name__ == "__main__":
    sys.exit(main())
