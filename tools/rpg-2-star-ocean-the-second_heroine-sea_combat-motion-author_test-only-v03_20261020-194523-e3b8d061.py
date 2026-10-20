"""Heroine (Sea of Stars direction) combat motion v03: re-authored HIT and DOWN only. TEST-ONLY, UNAPPROVED.

v01 (idle, attack) and v02 (move, guard, dodge, skill and the superseded hit/down) are frozen and only imported
(hash-pinned, read-only). Root review: v02 hit-a read as standing with a lowered blade and v02 down-c as a near-standing
crouch. v03 changes the method for these two states only:

  * the whole upper body (ponytail, torso, head) is ROTATED as one group about the waist (RotSprite-style 3x EPX +
    nearest sample, no blur): hit leans back in recoil then recovers; down slumps forward;
  * expression masks (documented per pose): eyes squeezed/closed in hurt and down poses. Face texels are therefore NOT
    byte-identical to the still in these poses; identity is kept by head proportions, hair and outfit clusters;
  * down is a single-knee kneel: pelvis ~29 texels lower, front boot planted with the knee up, back thigh down to a
    knee on the floor (row 135), back shin and boot rotated to lie along the floor behind; blade rests low;
  * the sword arm is repainted from the ROTATED shoulder (sleeve/forearm/bracer capsules + the still's fist and blade
    rotated about the grip) with the v02 weapon outline repair.

Pivot (64,136), 136x144 cell, 30-colour palette and binary alpha are unchanged; no canvas or scale change.

    build | check (default)
"""
from pathlib import Path
import hashlib, importlib.util, io, json, math, os, sys, zipfile
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
V01 = ROOT / "tools/rpg-2-star-ocean-the-second_heroine-sea_combat-motion-author_test-only-v01_20261020-192028-9bab493d.py"
V02 = ROOT / "tools/rpg-2-star-ocean-the-second_heroine-sea_combat-motion-author_test-only-v02_20261020-193906-4c7e2a90.py"
PINS = {V01: "b5d0926c75bdd5da27299fec18f5293da8c68e6ae51e5956cfa5395ec41d64cc",
        V02: "d04ab3fb985fc8be5f44657f15d61520e536ab0c6ae7058b82ebbdf5c23f88d2"}
OUT = ROOT / "outputs/hero-sea-motion-v03"
SLUG, SUBJECT, VER, STAMP, UID = "rpg-2-star-ocean-the-second", "heroine-sea-combat", "test-only-v03", "20261020-194523", "e3b8d061"


def _load(path, label):
    assert hashlib.sha256(path.read_bytes().replace(b"\r\n", b"\n")).hexdigest() == PINS[path], f"frozen {path.name} changed"
    spec = importlib.util.spec_from_file_location(label, str(path))
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


v1 = _load(V01, "hsm_v01")
v2 = _load(V02, "hsm_v02")
W, H, C, LAYERS, LEGS, PIN = v1.W, v1.H, v1.C, v1.LAYERS, v1.LEGS, v1.PIN
blank, over, shift, pick = v1.blank, v1.over, v1.shift, v1.pick
WAIST = (62.0, 86.0)
EYES = (61, 28, 73, 34)          # x0, y0, x1, y1 (exclusive) in the still: both eyes and lashes

# arm reach: grip offset from the ROTATED shoulder. lean: upper-body rotation (deg, + = clockwise = forward toward the enemy); feet: whole-texel boot offsets;
# legs: "ik" (two-bone, forward knee, boots planted) or "kneel"; eyes: "open" | "squeeze" | "closed"
P = {
    "hit-a": {"body": (-4, 3), "lean": -15.0, "pony": (3, 2), "legs": "ik", "eyes": "squeeze",
              "arm": {"reach": (6, 20), "blade": 125.0}},
    "hit-b": {"body": (-3, 2), "lean": -8.0, "pony": (2, 1), "legs": "ik", "eyes": "squeeze",
              "arm": {"reach": (9, 18), "blade": 160.0}},
    "hit-c": {"body": (-1, 1), "lean": -3.0, "pony": (1, 0), "legs": "ik", "eyes": "open",
              "arm": {"reach": (12, 15), "blade": -30.0}},
    "down-a": {"body": (-1, 12), "lean": 10.0, "pony": (1, -2), "legs": "ik", "feet": {"back": (0, 0), "front": (3, 0)},
               "eyes": "squeeze", "arm": {"reach": (10, 18), "blade": 60.0}},
    "down-b": {"body": (-1, 30), "lean": 20.0, "pony": (0, -3), "legs": "kneel", "feet": {"back": (0, 0), "front": (6, 0)},
               "eyes": "closed", "arm": {"reach": (10, 19), "blade": 80.0}},
    "down-c": {"body": (-1, 29), "lean": 16.0, "pony": (1, 1), "legs": "kneel", "feet": {"back": (0, 0), "front": (6, 0)},
               "eyes": "closed", "arm": {"reach": (9, 19), "blade": 84.0}},
}
CLIPS = {
    "hit": {"loop": False, "frames": [["hit-a", 2], ["hit-b", 3], ["hit-c", 2]], "then": "base", "arenaSeconds": 0.24},
    "down": {"loop": False, "hold": True, "frames": [["down-a", 3], ["down-b", 3], ["down-c", 3]], "arenaSeconds": 0.30},
}


def sha(b):
    return hashlib.sha256(b).hexdigest()


def fid(role):
    return sha(f"{UID}:{role}".encode())[:8]


def name(purpose, ext):
    return f"{SLUG}_{SUBJECT}_{purpose}_{VER}_{STAMP}-{fid(purpose)}.{ext}"


def rotp(part, src, dst, deg):
    """v01 RotSprite rotation; a zero angle with a fractional move still goes through the nearest sampler."""
    return v1.rotate_part(part, src, dst, deg if abs(deg) > 1e-9 else 1e-7)


def rot_pt(p, c, deg):
    r = math.radians(deg)
    x, y = p[0] - c[0], p[1] - c[1]
    return (c[0] + x * math.cos(r) - y * math.sin(r), c[1] + x * math.sin(r) + y * math.cos(r))


def expression(S, R, mode):
    """Return a copy of the still with the eye region repainted (documented expression mask) and the mask."""
    E = S.copy()
    mask = np.zeros((H, W), bool)
    if mode == "open":
        return E, mask
    x0, y0, x1, y1 = EYES
    K = v1.key_of(S)
    for y in range(y0, y1):
        for x in range(x0, x1):
            if R["head"][y, x] and K[y, x] not in ("ss", "sq", "ll", "lj", "lh", "le", "la", "l6", "l7", "lc"):
                E[y, x] = C["ss"] if y < y1 - 2 else C["sq"]
                mask[y, x] = True
    lid_rows = {"squeeze": 31, "closed": 32}
    ly = lid_rows[mode]
    for xa, xb in ((62, 67), (69, 72)):
        for x in range(xa, xb):
            E[ly, x] = C["l7"]
            mask[ly, x] = True
        if mode == "squeeze":                                  # squeezed: lid line kinks down at the outer corner
            E[ly + 1, xb - 1] = C["l7"]
            mask[ly + 1, xb - 1] = True
    return E, mask


def paint_arm_at(sh, grip, blade, S, R):
    el = v1.ik(sh, grip, v1.UPPER_LEN, v1.FORE_LEN, prefer_down=True)
    u = np.array(grip) - np.array(el)
    u = u / np.linalg.norm(u)
    arm = blank()
    fill = np.zeros((H, W), bool)
    fill |= v1.paint_capsule(arm, sh, el, 4.0, 3.4, v1.SLEEVE)
    fore_end = (grip[0] - u[0] * 2.0, grip[1] - u[1] * 2.0)
    fill |= v1.paint_capsule(arm, el, fore_end, 2.4, 2.2, v1.SKIN)
    fill |= v1.paint_capsule(arm, (el[0] - u[0] * 0.5, el[1] - u[1] * 0.5), (el[0] + u[0] * 1.6, el[1] + u[1] * 1.6), 3.6, 3.4, v1.SLEEVE)
    fill |= v1.paint_capsule(arm, (grip[0] - u[0] * 6.0, grip[1] - u[1] * 6.0), fore_end, 2.9, 2.9, v1.BRACER)
    v1.outline_ring(arm, fill)
    weapon = rotp(pick(S, R["fist"]), v1.GRIP0, grip, blade - v1.BLADE0)
    repaired = v2.weapon_outline(weapon)
    return arm, weapon, {"shoulder": [round(sh[0], 3), round(sh[1], 3)], "elbow": [round(el[0], 3), round(el[1], 3)],
                         "grip": [round(grip[0], 3), round(grip[1], 3)]}, repaired


def legs_for(pose, side, hip, S, R, lay):
    g, parts = LEGS[side], R["legs"][side]
    fx_, fy_ = pose.get("feet", {"back": (0, 0), "front": (0, 0)})[side]
    l1, l2 = math.dist(g["hip"], g["knee"]), math.dist(g["knee"], g["ankle"])
    L = lay["leg-" + side]
    boot_deg, boot_pivot_dst = 0.0, None
    if pose["legs"] == "kneel" and side == "back":
        knee = (hip[0] - 1.0, 131.0)                           # knee pad on the floor under the hip
        ankle = (knee[0] - l2, 131.5)                           # shin lies back along the floor
        boot_deg = -88.0                                       # calf boot rotated to lie behind, sole facing back
        boot_pivot_dst = ankle
    else:
        ankle = (g["ankle"][0] + fx_, g["ankle"][1] + fy_)
        d = math.dist(hip, ankle)
        if d >= l1 + l2 - 0.3:
            knee = (g["knee"][0] + hip[0] - g["hip"][0], g["knee"][1] + hip[1] - g["hip"][1])
        else:
            a, b = v1.ik(hip, ankle, l1, l2, prefer_down=True), v1.ik(hip, ankle, l1, l2, prefer_down=False)
            knee = max(a, b, key=lambda q: q[0])
    th = v1.ang((knee[0] - hip[0], knee[1] - hip[1])) - v1.ang((g["knee"][0] - g["hip"][0], g["knee"][1] - g["hip"][1]))
    sh = v1.ang((knee[0] - ankle[0], knee[1] - ankle[1])) - v1.ang((g["knee"][0] - g["ankle"][0], g["knee"][1] - g["ankle"][1]))
    if boot_pivot_dst is not None:
        boot = rotp(pick(S, parts["boot"]), g["ankle"], boot_pivot_dst, boot_deg)
        sh = v1.ang((knee[0] - ankle[0], knee[1] - ankle[1])) - v1.ang((g["knee"][0] - g["ankle"][0], g["knee"][1] - g["ankle"][1]))
    else:
        boot = shift(pick(S, parts["boot"]), fx_, fy_)
    over(L, rotp(pick(S, parts["kneecopy"]), g["knee"], knee, (th + sh) / 2))
    over(L, rotp(pick(S, parts["hipcopy"]), g["hip"], hip, th))
    over(L, boot)
    over(L, rotp(pick(S, parts["shin"]), g["ankle"], ankle, sh))
    over(L, rotp(pick(S, parts["thigh"]), g["hip"], hip, th))
    return {"hip": [round(hip[0], 3), round(hip[1], 3)], "knee": [round(knee[0], 3), round(knee[1], 3)],
            "ankle": [round(ankle[0], 3), round(ankle[1], 3)], "thighDeg": round(th, 3), "shinDeg": round(sh, 3),
            "bootDeg": boot_deg, "thighStretch": round(math.dist(hip, knee) - l1, 3), "shinStretch": round(math.dist(knee, ankle) - l2, 3)}


def build(pid, S, R):
    pose = P[pid]
    dx, dy = pose["body"]
    deg = pose["lean"]
    E, emask = expression(S, R, pose["eyes"])
    pivot = (WAIST[0] + dx, WAIST[1] + dy)
    lay = {n: blank() for n in LAYERS}
    up = {n: blank() for n in ("ponytail", "torso", "head")}
    px, py = pose["pony"]
    over(up["ponytail"], shift(pick(E, R["root"] & (R["pony"] | R["head"])), dx, dy))
    over(up["ponytail"], shift(pick(E, R["pony"]), dx + px, dy + py))
    over(up["torso"], shift(pick(E, R["torso"] & ~R["arm"]), dx, dy))
    under = v1.jacket_underlay(dx, dy)
    empty = (up["torso"][..., 3] == 0) & (under[..., 3] > 0)
    up["torso"][empty] = under[empty]
    over(up["head"], shift(pick(E, R["head"]), dx, dy))
    for n in up:
        lay[n] = rotp(up[n], pivot, pivot, deg)
    joints = {}
    for side in ("back", "front"):
        hip0 = (LEGS[side]["hip"][0] + dx, LEGS[side]["hip"][1] + dy)
        joints[side] = legs_for(pose, side, rot_pt(hip0, pivot, deg), S, R, lay)
    sh = rot_pt((v1.SHOULDER[0] + dx, v1.SHOULDER[1] + dy), pivot, deg)
    grip = (sh[0] + pose["arm"]["reach"][0], sh[1] + pose["arm"]["reach"][1])   # grip relative to the rotated shoulder
    lay["arm"], lay["weapon"], arm, repaired = paint_arm_at(sh, grip, pose["arm"]["blade"], S, R)
    flat = blank()
    for n in LAYERS[1:]:
        over(flat, lay[n])
    yy, xx = np.mgrid[0:H, 0:W]
    lay["seams"] = v1.seams(flat, (yy >= 70) & (yy < 136))
    over(flat, lay["seams"])
    closed = 0
    for comp in v1.hole_components(flat):
        if len(comp) <= 4:
            for y, x in comp:
                lay["seams"][y, x] = C["o1"]
            closed += len(comp)
    # cell margins are part of the declared contract: clear anything a rotated part pushed into them
    for n in LAYERS:
        lay[n][:, 0] = 0
        lay[n][:, W - 1] = 0
        lay[n][PIN[1]:] = 0
    return lay, {"joints": joints, "arm": arm, "weaponOutlineTexelsRepaired": repaired, "pocketsClosed": closed,
                 "upperBodyRotationDeg": deg, "rotationPivot": [pivot[0], pivot[1]],
                 "expression": pose["eyes"], "expressionMaskTexels": int(emask.sum()),
                 "expressionMaskBox": list(EYES) if emask.any() else None}


def outputs():
    raw = v1.long(v1.BASE).read_bytes()
    assert sha(raw) == v1.BASE_SHA
    S = v1.decode(raw)
    R = v1.rig(S)
    poses = {pid: dict(zip(("layers", "info"), build(pid, S, R))) for pid in P}
    writer = v1.module(v1.WRITER, "established_pxo_writer")
    writer.W, writer.H = W, H
    writer.to_rgba = lambda im: np.ascontiguousarray(im, np.uint8)
    files, flats = {}, {}
    for pid, p in poses.items():
        flat = v1.flatten(p["layers"])
        flats[pid] = flat
        png = v1.png_bytes(flat)
        files[f"{pid}.png"] = (name(f"pose-{pid}-native136", "png"), png)
        files[f"{pid}.ora"] = (name(f"pose-{pid}-layered", "ora"), v1.ora_bytes(p["layers"], flat))
        files[f"{pid}.pxo"] = (name(f"pose-{pid}-editable", "pxo"),
                               writer.make_pxo([p["layers"]], [1.0], png, name(f"pose-{pid}-pxo-export", "png"), 30,
                                               order=LAYERS, dt=(2026, 10, 20, 19, 45, 22)))
        files[f"{pid}.x4"] = (name(f"pose-{pid}-inspect-x4", "png"), v1.png_bytes(v1.inspect_x4(flat)))
    tick = 1 / 30
    clips = {}
    for cid, c in CLIPS.items():
        t, fr = 0, []
        for pid, n in c["frames"]:
            fr.append({"pose": pid, "ticks": n, "start_s": round(t * tick, 6), "duration_s": round(n * tick, 6)})
            t += n
        clips[cid] = {**{k: v for k, v in c.items() if k != "frames"}, "frames": fr, "frames_total_s": round(t * tick, 6)}
    manifest = {
        "status": "TEST-ONLY v03 revision of HIT and DOWN only (supersedes v02 hit-a/hit-b/down-a/down-b/down-c for review). "
                  "UNAPPROVED motion; not loaded by the game. idle/attack (v01) and move/guard/dodge/skill (v02) unchanged.",
        "task": "content.combat.protagonist-female.combat-actions",
        "frozenInputs": {str(k.relative_to(ROOT)).replace("\\", "/"): v for k, v in PINS.items()},
        "approvedSource": {"file": str(v1.BASE.relative_to(ROOT)).replace("\\", "/"), "sha256": v1.BASE_SHA, "rewritten": False},
        "cell": [W, H], "logicalExtent": [68, 72], "pinNative": list(PIN), "pinLogical": [32, 68],
        "displayRequirement": "draw_texture_rect(texture, Rect2(round(x)-32, 204, 68, 72), tile=false), nearest, no mipmaps",
        "faceContract": "NOT byte-exact in v03 poses: the upper body is rotated (RotSprite, nearest) and hurt/down poses repaint the "
                        "eyes inside the declared expression mask box; identity = same head/hair/outfit clusters and proportions",
        "clips": clips,
        "poses": {pid: {**{k: (list(v) if isinstance(v, tuple) else v) for k, v in P[pid].items() if k not in ("arm", "feet")},
                        "feet": {k: list(v) for k, v in P[pid].get("feet", {"back": (0, 0), "front": (0, 0)}).items()},
                        "arm": {"reachFromShoulder": list(P[pid]["arm"]["reach"]), "bladeDeg": P[pid]["arm"]["blade"]},
                        "rig": poses[pid]["info"],
                        "layerTexels": {n: int((poses[pid]["layers"][n][..., 3] > 0).sum()) for n in LAYERS}} for pid in P},
        "layers": LAYERS, "method": __doc__.strip().split("\n\n")[1],
        "source": {"file": str(Path(__file__).resolve().relative_to(ROOT)).replace("\\", "/"),
                   "sha256TextLf": sha(Path(__file__).read_bytes().replace(b"\r\n", b"\n"))},
        "files": {role: {"name": n, "sha256": sha(b)} for role, (n, b) in sorted(files.items())},
        "artApproved": False, "motionApproved": False, "hitSynchronized": False, "runtimeDefaultChanged": False,
        "gameSourceChanged": False, "guiSaveAsVerified": False,
    }
    files["manifest"] = (name("manifest", "json"), (json.dumps(manifest, indent=1) + "\n").encode())
    return files, flats, poses, manifest, S, R


def gates(files, flats, poses, manifest, S, R):
    res = []

    def gate(k, ok, info=None):
        res.append({"key": k, "pass": bool(ok), "info": info})
    base_cols = {tuple(c) for c in S[S[..., 3] > 0][:, :3].tolist()}
    gate("approved still unchanged", sha(v1.long(v1.BASE).read_bytes()) == v1.BASE_SHA)
    gate("frozen v01/v02 authors unchanged", all(sha(k.read_bytes().replace(b"\r\n", b"\n")) == v for k, v in PINS.items()))
    hips = {}
    for pid, flat in flats.items():
        op = flat[..., 3] > 0
        ys, xs = np.nonzero(op)
        cols = {tuple(c) for c in flat[op][:, :3].tolist()}
        gate(f"{pid}: binary alpha + palette-locked (still's 30)", set(np.unique(flat[..., 3]).tolist()) <= {0, 255} and cols <= base_cols, len(cols))
        gate(f"{pid}: margins (col 0/135, rows 136..143 transparent)", not op[:, 0].any() and not op[:, -1].any() and not op[PIN[1]:].any(),
             [int(xs.min()), int(xs.max()), int(ys.min()), int(ys.max())])
        gate(f"{pid}: grounded (lowest row 135)", ys.max() == PIN[1] - 1)
        new = [c for c in v1.hole_components(flat) if len(c) <= 4]
        gate(f"{pid}: no pinhole pockets (<= 4 texels)", not new, len(new))
        z = zipfile.ZipFile(io.BytesIO(files[f"{pid}.ora"][1]))
        zp = zipfile.ZipFile(io.BytesIO(files[f"{pid}.pxo"][1]))
        cels = [np.frombuffer(zp.read(f"image_data/frames/1/layer_{i}"), np.uint8).reshape(H, W, 4) for i in range(1, len(LAYERS) + 1)]
        gate(f"{pid}: layers == PNG, ORA merged == PNG, PXO cels == ORA layers",
             np.array_equal(v1.flatten(poses[pid]["layers"]), v1.decode(files[f"{pid}.png"][1])) and
             np.array_equal(v1.decode(z.read("mergedimage.png")), flat) and
             all(np.array_equal(c, v1.decode(z.read(f"data/{i:02d}-{n}.png"))) for i, (c, n) in enumerate(zip(cels, LAYERS))))
        hips[pid] = max(j["hip"][1] for j in poses[pid]["info"]["joints"].values())
    for pid in ("hit-a", "hit-b"):
        gate(f"{pid}: upper body actually rotated back (lean < -5 deg), not a translation", P[pid]["lean"] < -5)
    gate("hit recovers: lean magnitude decreases a > b > c", abs(P["hit-a"]["lean"]) > abs(P["hit-b"]["lean"]) > abs(P["hit-c"]["lean"]))
    gate("down: pelvis materially lower (>= 25 texels below the still's hips at 86.5) in down-b/down-c",
         hips["down-b"] - 86.5 >= 25 and hips["down-c"] - 86.5 >= 25, {k: round(v, 2) for k, v in hips.items()})
    kb = poses["down-c"]["info"]["joints"]["back"]["knee"]
    gate("down: back knee on the floor (knee centre >= row 130)", kb[1] >= 130 and poses["down-b"]["info"]["joints"]["back"]["knee"][1] >= 130, kb)
    gate("down: drops past then settles (down-b pelvis lower than down-c, both lower than down-a)",
         P["down-b"]["body"][1] > P["down-c"]["body"][1] > P["down-a"]["body"][1])
    gate("down: torso slumps forward (lean >= 10 deg) and blade rests low (grip below row 95 final)",
         all(P[p]["lean"] >= 10 and poses[p]["info"]["arm"]["grip"][1] >= 95 for p in ("down-b", "down-c")),
         [poses[p]["info"]["arm"]["grip"] for p in ("down-b", "down-c")])
    gate("clips fit arena: hit <= .24 s, down <= .30 s", manifest["clips"]["hit"]["frames_total_s"] <= 0.24 + 1e-9 and
         manifest["clips"]["down"]["frames_total_s"] <= 0.30 + 1e-9)
    gate("face byte-equality NOT claimed (expression/rotation declared)", "NOT byte-exact" in manifest["faceContract"])
    shas = [sha(files[f"{p}.png"][1]) for p in P]
    gate("v03 pose images unique", len(set(shas)) == len(shas))
    return res


def main():
    mode = sys.argv[1] if len(sys.argv) > 1 else "check"
    files, flats, poses, manifest, S, R = outputs()
    det = all(files[k][1] == b for k, (n, b) in outputs()[0].items())
    res = [{"key": "deterministic rebuild", "pass": det, "info": None}] + gates(files, flats, poses, manifest, S, R)
    if mode == "build":
        os.makedirs(v1.long(OUT), exist_ok=True)
        for role, (n, b) in files.items():
            p = v1.long(OUT / n)
            if p.exists():
                assert p.read_bytes() == b, f"refusing to overwrite a different frozen file: {n}"
            else:
                p.write_bytes(b)
    elif mode == "check":
        for role, (n, b) in files.items():
            p = v1.long(OUT / n)
            res.append({"key": f"on-disk bytes equal rebuild: {role}", "pass": p.exists() and p.read_bytes() == b, "info": None})
    fails = [r for r in res if not r["pass"]]
    for r in fails:
        print("FAIL", r["key"], r["info"])
    print("HSM03", mode.upper(), "PASS" if not fails else "FAIL", f"{len(res) - len(fails)}/{len(res)}")
    if mode == "check":
        text = json.dumps({"mode": "check", "gates": res, "passed": len(res) - len(fails), "total": len(res),
                           "source": manifest["source"], "manifestSha256": sha(files["manifest"][1])}, indent=1) + "\n"
        p = v1.long(OUT / name("check-report", "json"))
        if not p.exists() or p.read_bytes() != text.encode():
            with open(p, "w", encoding="utf-8", newline="\n") as f:
                f.write(text)
    if mode == "preview":
        from PIL import Image
        for pid, flat in flats.items():
            Image.fromarray(v1.inspect_x4(flat)).save(sys.argv[2] + f"/v3_{pid}.png")
    return 0 if not fails else 1


if __name__ == "__main__":
    sys.exit(main())
