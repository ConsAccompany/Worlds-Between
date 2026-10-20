"""Heroine (Sea of Stars direction) combat motion v02: the remaining six actions on the frozen v01 rig. TEST-ONLY, UNAPPROVED.

v01 (idle + attack, author sha b5d0926c..., 119/119) is frozen and only IMPORTED here (hash-pinned, read-only); none of
its files are rewritten. v02 adds move, guard, dodge, hit, skill and down with their own poses and durations, using the
same method: rigid whole-texel upper body (face texels exact), lagging ponytail over an anchored root, thigh/shin
RotSprite re-pose with painted hip/knee joint copies, repainted sword arm (sleeve/forearm/bracer capsules + the
still's fist and blade rotated about the grip) over the painted jacket side. New in v02:

  * feet may move by whole texels (move steps, dodge hop, skill step); the shin is re-posed from the moved ankle and
    each pose declares its sole row and in-cell root offset; pivot (64,136) never changes;
  * large crouches (dodge landing, skill, down) take the knee from two-bone IK (forward knee) instead of hand travel;
  * weapon outline repair: transparent texels touching exposed blade/fist fill get the blade outline colour #151728
    (fixes the broken guard/tip outline after rotation seen in v01);
  * skill fx: teal charge glints along the blade (telegraph) and a teal-edged crescent (strike).

The approved still (sha 4ce65a79...) stays read-only; every clip that ends returns to it.

    build | check (default)
"""
from pathlib import Path
import hashlib, importlib.util, io, json, math, os, sys, zipfile
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
V01 = ROOT / "tools/rpg-2-star-ocean-the-second_heroine-sea_combat-motion-author_test-only-v01_20261020-192028-9bab493d.py"
V01_SHA = "b5d0926c75bdd5da27299fec18f5293da8c68e6ae51e5956cfa5395ec41d64cc"
OUT = ROOT / "outputs/hero-sea-motion-v02"
SLUG, SUBJECT, VER, STAMP, UID = "rpg-2-star-ocean-the-second", "heroine-sea-combat", "test-only-v02", "20261020-193906", "4c7e2a90"


def _load_v01():
    assert hashlib.sha256(V01.read_bytes().replace(b"\r\n", b"\n")).hexdigest() == V01_SHA, "frozen v01 author changed"
    spec = importlib.util.spec_from_file_location("hsm_v01", str(V01))
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


v1 = _load_v01()
W, H, C, LAYERS, LEGS, PIN = v1.W, v1.H, v1.C, v1.LAYERS, v1.LEGS, v1.PIN
blank, over, shift, pick = v1.blank, v1.over, v1.shift, v1.pick

# action durations in the current arena (read-only): visual attack .39, hit .24, skill .45, down .30 (held), dodge_time .27,
# move/guard phases loop on .11/.18 s.
ARENA = {"hit": 0.24, "skill": 0.45, "down": 0.30, "dodge": 0.27}

# feet: whole-texel boot offsets; knees: (dx,dy) hand travel or "ik" (forward knee from two-bone IK)
P = {
    # move: short side-view shuffle step toward the enemy (right); arena slides x, the cell keeps pivot 64,136
    "move-a": {"body": (1, 1), "pony": (-1, 0), "feet": {"back": (0, 0), "front": (3, -3)}, "knees": "ik",
               "arm": {"grip": (88, 62), "blade": -30.0}},
    "move-b": {"body": (2, 2), "pony": (-1, 1), "feet": {"back": (0, 0), "front": (4, 0)}, "knees": "ik",
               "arm": {"grip": (89, 63), "blade": -36.0}},
    "move-c": {"body": (3, 1), "pony": (-2, 0), "feet": {"back": (3, -3), "front": (4, 0)}, "knees": "ik",
               "arm": {"grip": (89, 61), "blade": -32.0}},
    "move-d": {"body": (2, 0), "pony": (-1, -1), "feet": {"back": (2, 0), "front": (2, 0)}, "knees": "ik",
               "arm": {"grip": (88, 60), "blade": -38.0}},
    # guard: blade brought up across the front, weight back and low
    "guard-a": {"body": (-1, 2), "pony": (1, 0), "knees": {"back": (0, 1), "front": (0.5, 1)},
                "arm": {"grip": (86, 54), "blade": -72.0}},
    "guard-b": {"body": (-2, 3), "pony": (1, 1), "knees": {"back": (-0.5, 1.5), "front": (0.5, 1.5)},
                "arm": {"grip": (84, 52), "blade": -86.0}},
    "guard-c": {"body": (-2, 4), "pony": (1, 1), "knees": {"back": (-0.5, 2), "front": (1, 2)},
                "arm": {"grip": (84, 53), "blade": -84.0}},
    # dodge: backward hop (airborne, knees tucked) then a crouched landing
    "dodge-a": {"body": (-3, -4), "pony": (1, 1), "feet": {"back": (-3, -5), "front": (-2, -4)}, "knees": "ik",
                "arm": {"grip": (84, 58), "blade": -60.0}},
    "dodge-b": {"body": (-5, 4), "pony": (2, -1), "feet": {"back": (-4, 0), "front": (-4, 0)}, "knees": "ik",
                "arm": {"grip": (84, 62), "blade": -50.0}},
    # hit: recoil (pushed back, arm flung down-back) then partial recovery
    "hit-a": {"body": (-4, 2), "pony": (3, -1), "knees": {"back": (-2, 1), "front": (-1, 1)},
              "arm": {"grip": (80, 70), "blade": 110.0}},
    "hit-b": {"body": (-2, 2), "pony": (1, 0), "knees": {"back": (-1, 1), "front": (0, 1)},
              "arm": {"grip": (82, 66), "blade": 150.0}},
    # skill: two-stage charge telegraph, stepping strike, held contact, recovery
    "skill-tel-a": {"body": (-2, 4), "pony": (1, 0), "knees": "ik", "arm": {"grip": (74, 66), "blade": 160.0},
                    "fx": "glint"},
    "skill-tel-b": {"body": (-3, 5), "pony": (1, 1), "knees": "ik", "arm": {"grip": (72, 64), "blade": 175.0},
                    "fx": "glint2"},
    "skill-strike": {"body": (3, 4), "pony": (-2, -1), "feet": {"back": (0, 0), "front": (4, 0)}, "knees": "ik",
                     "arm": {"grip": (92, 52), "blade": -40.0}, "fx": ("skillsmear", "skill-tel-b", 9)},
    "skill-contact": {"body": (4, 3), "pony": (-3, -1), "feet": {"back": (0, 0), "front": (4, 0)}, "knees": "ik",
                      "arm": {"grip": (91, 56), "blade": -6.0}, "fx": ("skillsmear", "skill-strike", 6)},
    "skill-recover": {"body": (2, 2), "pony": (-1, 0), "feet": {"back": (0, 0), "front": (2, 0)}, "knees": "ik",
                      "arm": {"grip": (87, 62), "blade": -25.0}},
    # down: stagger, collapse past the rest crouch, settle (held by the arena)
    "down-a": {"body": (-2, 4), "pony": (2, 0), "knees": "ik", "arm": {"grip": (80, 68), "blade": 70.0}},
    "down-b": {"body": (-3, 11), "pony": (2, 2), "knees": "ik", "arm": {"grip": (79, 70), "blade": 85.0}},
    "down-c": {"body": (-3, 9), "pony": (1, 3), "knees": "ik", "arm": {"grip": (78, 69), "blade": 88.0}},
}
CLIPS = {
    "move": {"loop": True, "frames": [["move-a", 3], ["move-b", 3], ["move-c", 3], ["move-d", 3]]},
    "guard": {"loop": True, "enter": [["guard-a", 2]], "frames": [["guard-b", 6], ["guard-c", 6]]},
    "dodge": {"loop": False, "frames": [["dodge-a", 4], ["dodge-b", 4]], "then": "base", "arenaSeconds": ARENA["dodge"]},
    "hit": {"loop": False, "frames": [["hit-a", 4], ["hit-b", 3]], "then": "base", "arenaSeconds": ARENA["hit"]},
    "skill": {"loop": False, "frames": [["skill-tel-a", 4], ["skill-tel-b", 3], ["skill-strike", 1], ["skill-contact", 2],
                                        ["skill-recover", 3]], "then": "base", "arenaSeconds": ARENA["skill"],
              "stagedContactPose": "skill-contact"},
    "down": {"loop": False, "hold": True, "frames": [["down-a", 3], ["down-b", 3], ["down-c", 3]], "arenaSeconds": ARENA["down"]},
}
ACTIONS = list(CLIPS)


def sha(b):
    return hashlib.sha256(b).hexdigest()


def fid(role):
    return sha(f"{UID}:{role}".encode())[:8]


def name(purpose, ext):
    return f"{SLUG}_{SUBJECT}_{purpose}_{VER}_{STAMP}-{fid(purpose)}.{ext}"


def knee_for(pose, side, hip, ankle):
    g = LEGS[side]
    k = pose["knees"]
    if k == "ik":
        l1, l2 = math.dist(g["hip"], g["knee"]), math.dist(g["knee"], g["ankle"])
        d = math.dist(hip, ankle)
        if d >= l1 + l2 - 0.3:                                   # (near) straight: keep the drawn bend
            return (g["knee"][0] + hip[0] - g["hip"][0], g["knee"][1] + (hip[1] - g["hip"][1] + ankle[1] - g["ankle"][1]) / 2)
        c = v1.ik(hip, ankle, l1, l2, prefer_down=True)
        a, b = v1.ik(hip, ankle, l1, l2, prefer_down=True), v1.ik(hip, ankle, l1, l2, prefer_down=False)
        return max(a, b, key=lambda q: q[0])                       # knee forward (toward the enemy)
    kx, ky = k[side]
    return (g["knee"][0] + kx, g["knee"][1] + ky)


def weapon_outline(weapon):
    O = weapon[..., 3] > 0
    K = v1.key_of(weapon)
    fill = O & ~np.vectorize(lambda k: k in v1.OUTL or k == "d3")(K)
    ring = np.zeros_like(O)
    ring[1:] |= fill[:-1]
    ring[:-1] |= fill[1:]
    ring[:, 1:] |= fill[:, :-1]
    ring[:, :-1] |= fill[:, 1:]
    ring &= ~O
    weapon[ring] = C["d3"]
    return int(ring.sum())


def glint(grip, deg, n, phase):
    lay = blank()
    r = math.radians(deg)
    ux, uy = math.cos(r), math.sin(r)
    tip = math.hypot(108.5 - v1.GRIP0[0], 41.5 - v1.GRIP0[1])
    for i in range(n):
        t = 8 + (tip - 8) * (i + phase) / n
        side = 3 if i % 2 == 0 else -3
        x = grip[0] + ux * t - uy * side
        y = grip[1] + uy * t + ux * side
        xi, yi = int(math.floor(x)), int(math.floor(y))
        for ddx, ddy, key in ((0, 0, "tm"), (1, 0, "tg"), (-1, 0, "tg"), (0, 1, "tg"), (0, -1, "tg")):
            if 1 <= xi + ddx < W - 1 and 0 <= yi + ddy < PIN[1]:
                if key == "tm" or lay[yi + ddy, xi + ddx, 3] == 0:
                    lay[yi + ddy, xi + ddx] = C[key]
    return lay


def build(pid, S, R):
    pose = P[pid]
    dx, dy = pose["body"]
    feet = pose.get("feet", {"back": (0, 0), "front": (0, 0)})
    lay = {n: blank() for n in LAYERS}
    px, py = pose["pony"]
    over(lay["ponytail"], shift(pick(S, R["root"] & (R["pony"] | R["head"])), dx, dy))
    over(lay["ponytail"], shift(pick(S, R["pony"]), dx + px, dy + py))
    joints = {}
    for side in ("back", "front"):
        g, parts = LEGS[side], R["legs"][side]
        fx_, fy_ = feet[side]
        hip = (g["hip"][0] + dx, g["hip"][1] + dy)
        ankle = (g["ankle"][0] + fx_, g["ankle"][1] + fy_)
        knee = knee_for(pose, side, hip, ankle)
        th = v1.ang((knee[0] - hip[0], knee[1] - hip[1])) - v1.ang((g["knee"][0] - g["hip"][0], g["knee"][1] - g["hip"][1]))
        sh = v1.ang((knee[0] - ankle[0], knee[1] - ankle[1])) - v1.ang((g["knee"][0] - g["ankle"][0], g["knee"][1] - g["ankle"][1]))
        L = lay["leg-" + side]
        over(L, shift(pick(S, parts["hipcopy"]), dx, dy))
        kd = (math.floor(knee[0] - g["knee"][0] + 0.5), math.floor(knee[1] - g["knee"][1] + 0.5))
        over(L, shift(pick(S, parts["kneecopy"]), *kd))
        over(L, v1.rotate_part(pick(S, parts["shin"]), g["ankle"], ankle, sh))
        over(L, v1.rotate_part(pick(S, parts["thigh"]), g["hip"], hip, th))
        over(L, shift(pick(S, parts["boot"]), fx_, fy_))
        joints[side] = {"hip": [round(hip[0], 3), round(hip[1], 3)], "knee": [round(knee[0], 3), round(knee[1], 3)],
                        "ankle": [ankle[0], ankle[1]], "foot": [fx_, fy_], "thighDeg": round(th, 3), "shinDeg": round(sh, 3),
                        "thighStretch": round(math.dist(hip, knee) - math.dist(g["hip"], g["knee"]), 3),
                        "shinStretch": round(math.dist(knee, ankle) - math.dist(g["knee"], g["ankle"]), 3)}
    over(lay["torso"], shift(pick(S, R["torso"] & ~R["arm"]), dx, dy))
    under = v1.jacket_underlay(dx, dy)
    empty = (lay["torso"][..., 3] == 0) & (under[..., 3] > 0)
    lay["torso"][empty] = under[empty]
    over(lay["head"], shift(pick(S, R["head"]), dx, dy))
    lay["arm"], lay["weapon"], arm = v1.paint_arm(pose, S, R, (dx, dy))
    repaired = weapon_outline(lay["weapon"])
    flat = blank()
    for n in LAYERS[1:]:
        over(flat, lay[n])
    yy, xx = np.mgrid[0:H, 0:W]
    lay["seams"] = v1.seams(flat, (yy >= 80) & (yy < 136))
    over(flat, lay["seams"])
    allowed = {(y + dy, x + dx) for y, x in v1.hole_cells(S)}
    closed = 0
    for comp in v1.hole_components(flat):
        if not set(comp) <= allowed and len(comp) <= 4:
            for y, x in comp:
                lay["seams"][y, x] = C["o1"]
            closed += len(comp)
    info = {"joints": joints, "arm": {k: [round(v[0], 3), round(v[1], 3)] for k, v in arm.items()},
            "weaponOutlineTexelsRepaired": repaired, "pocketsClosed": closed,
            "soleRow": PIN[1] - 1 + max(feet["back"][1], feet["front"][1]),
            "inCellRootOffset": [(feet["back"][0] + feet["front"][0]) / 2, 0]}
    return lay, info


def add_fx(poses):
    for pid, p in P.items():
        fx = p.get("fx")
        if fx is None:
            continue
        a = poses[pid]["info"]["arm"]
        if fx in ("glint", "glint2"):
            layer = glint(a["grip"], p["arm"]["blade"], 4, 0.0 if fx == "glint" else 0.5)
        else:
            _, prev, width = fx
            layer = v1.smear_layer(tuple(a["shoulder"]), tuple(poses[prev]["info"]["arm"]["tip"]), tuple(a["tip"]), width)
            edge = layer[..., 3] > 0
            core = np.all(layer == C["mt"], axis=-1)
            layer[edge & ~core] = C["tm"]                      # teal-edged crescent marks the skill swing
        busy = (poses[pid]["layers"]["arm"][..., 3] > 0) | (poses[pid]["layers"]["weapon"][..., 3] > 0)
        layer[busy] = 0
        layer[:, 0] = 0
        layer[:, W - 1] = 0
        layer[PIN[1]:] = 0
        poses[pid]["layers"]["fx"] = layer


def outputs():
    raw = v1.long(v1.BASE).read_bytes()
    assert sha(raw) == v1.BASE_SHA
    S = v1.decode(raw)
    R = v1.rig(S)
    poses = {pid: dict(zip(("layers", "info"), build(pid, S, R))) for pid in P}
    add_fx(poses)
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
                                               order=LAYERS, dt=(2026, 10, 20, 19, 39, 6)))
        files[f"{pid}.x4"] = (name(f"pose-{pid}-inspect-x4", "png"), v1.png_bytes(v1.inspect_x4(flat)))
    tick = 1.0 / 30
    clips = {}
    for cid, clip in CLIPS.items():
        c = {k: v for k, v in clip.items() if k not in ("frames", "enter")}
        for part in ("enter", "frames"):
            if part in clip:
                t, fr = 0, []
                for pid, n in clip[part]:
                    fr.append({"pose": pid, "ticks": n, "start_s": round(t * tick, 6), "duration_s": round(n * tick, 6)})
                    t += n
                c[part] = fr
                c[part + "_total_s"] = round(t * tick, 6)
        clips[cid] = c
    manifest = {
        "status": "TEST-ONLY v02 source subset: move, guard, dodge, hit, skill, down. UNAPPROVED motion; not a runtime package, "
                  "not loaded by the game; no game/default/camera/party change. With v01 (idle, attack) all 8 actions have "
                  "authored source poses, but the parent task stays IN_PROGRESS (no loader/gameplay playback evidence, no approval).",
        "task": "content.combat.protagonist-female.combat-actions",
        "frozenV01": {"author": str(V01.relative_to(ROOT)).replace("\\", "/"), "sha256TextLf": V01_SHA,
                      "manifest": "outputs/hero-sea-motion-v01/rpg-2-star-ocean-the-second_heroine-sea-combat_manifest_test-only-v01_20261020-192028-7e93a93c.json",
                      "actions": ["idle", "attack"]},
        "approvedSource": {"file": str(v1.BASE.relative_to(ROOT)).replace("\\", "/"), "sha256": v1.BASE_SHA, "rewritten": False},
        "cell": [W, H], "logicalExtent": [68, 72], "pinNative": list(PIN), "pinLogical": [32, 68],
        "displayRequirement": "draw_texture_rect(texture, Rect2(round(x)-32, 204, 68, 72), tile=false), nearest, no mipmaps",
        "margins": "col 0, col 135 and rows 136..143 transparent in every pose; no pose needed larger bounds",
        "tickSeconds": round(tick, 9), "clips": clips, "arenaDurations": ARENA,
        "poses": {pid: {"body": list(P[pid]["body"]), "ponytailLag": list(P[pid]["pony"]),
                        "feet": {k: list(v) for k, v in P[pid].get("feet", {"back": (0, 0), "front": (0, 0)}).items()},
                        "knees": P[pid]["knees"] if P[pid]["knees"] == "ik" else {k: list(v) for k, v in P[pid]["knees"].items()},
                        "arm": {"grip": list(P[pid]["arm"]["grip"]), "bladeDeg": P[pid]["arm"]["blade"]},
                        "fx": P[pid].get("fx") if isinstance(P[pid].get("fx"), (str, type(None))) else list(P[pid]["fx"]),
                        "rig": poses[pid]["info"],
                        "layerTexels": {n: int((poses[pid]["layers"][n][..., 3] > 0).sum()) for n in LAYERS}} for pid in P},
        "layers": LAYERS,
        "method": __doc__.strip().split("\n\n")[1],
        "source": {"file": str(Path(__file__).resolve().relative_to(ROOT)).replace("\\", "/"),
                   "sha256TextLf": sha(Path(__file__).read_bytes().replace(b"\r\n", b"\n"))},
        "files": {role: {"name": n, "sha256": sha(b)} for role, (n, b) in sorted(files.items())},
        "artApproved": False, "motionApproved": False, "runtimeDefaultChanged": False, "gameSourceChanged": False,
        "guiSaveAsVerified": False, "hitSynchronized": False, "loaderPlaybackEvidence": False,
    }
    files["manifest"] = (name("manifest", "json"), (json.dumps(manifest, indent=1) + "\n").encode())
    return files, flats, poses, manifest, S, R


def gates(files, flats, poses, manifest, S, R):
    res = []

    def gate(k, ok, info=None):
        res.append({"key": k, "pass": bool(ok), "info": info})
    base_cols = {tuple(c) for c in S[S[..., 3] > 0][:, :3].tolist()}
    gate("approved still unchanged (4ce65a79...)", sha(v1.long(v1.BASE).read_bytes()) == v1.BASE_SHA)
    gate("frozen v01 author unchanged (b5d0926c...)", sha(V01.read_bytes().replace(b"\r\n", b"\n")) == V01_SHA)
    face_mask = R["head"][18:42, 54:77]
    face = S[18:42, 54:77]
    base_holes = set(v1.hole_cells(S))
    pngs = {}
    for pid, flat in flats.items():
        dx, dy = P[pid]["body"]
        feet = P[pid].get("feet", {"back": (0, 0), "front": (0, 0)})
        op = flat[..., 3] > 0
        ys, xs = np.nonzero(op)
        cols = {tuple(c) for c in flat[op][:, :3].tolist()}
        gate(f"{pid}: binary alpha + palette-locked (still's 30)", set(np.unique(flat[..., 3]).tolist()) <= {0, 255} and cols <= base_cols, len(cols))
        gate(f"{pid}: margins (col 0/135, rows 136..143 transparent)", not op[:, 0].any() and not op[:, -1].any() and not op[PIN[1]:].any(),
             [int(xs.min()), int(xs.max()), int(ys.min()), int(ys.max())])
        ok_feet = True
        for side in ("back", "front"):
            b = R["legs"][side]["boot"]
            fx_, fy_ = feet[side]
            moved = v1.shift(v1.pick(S, b), fx_, fy_)
            front = sum((poses[pid]["layers"][n][..., 3] > 0) for n in ("arm", "weapon", "fx")) > 0
            m = (moved[..., 3] > 0) & ~front                 # the arm/blade may pass in front of a boot
            ok_feet &= np.array_equal(flat[m], moved[m])
        sole = poses[pid]["info"]["soleRow"]
        gate(f"{pid}: boots byte-exact at declared foot offsets, lowest row = declared sole row {sole}", ok_feet and ys.max() == sole)
        region = flat[18 + dy:42 + dy, 54 + dx:77 + dx]
        gate(f"{pid}: face texels exact at body offset {dx},{dy}", np.array_equal(region[face_mask], face[face_mask]))
        new = set(v1.hole_cells(flat)) - {(y + dy, x + dx) for y, x in base_holes}
        comps = [c for c in v1.hole_components(flat) if set(c) & new]
        gate(f"{pid}: no new pinhole (enclosed pocket <= 4 texels) outside the still's pockets", all(len(c) > 4 for c in comps),
             {"newNegativeSpacePockets(>4, reported for visual review)": [[len(c), list(c[0])] for c in comps]})
        gate(f"{pid}: layer stack == PNG; ORA merged == PNG", np.array_equal(v1.flatten(poses[pid]["layers"]), v1.decode(files[f"{pid}.png"][1]))
             and np.array_equal(v1.decode(zipfile.ZipFile(io.BytesIO(files[f"{pid}.ora"][1])).read("mergedimage.png")), flat))
        z = zipfile.ZipFile(io.BytesIO(files[f"{pid}.ora"][1]))
        zp = zipfile.ZipFile(io.BytesIO(files[f"{pid}.pxo"][1]))
        d = json.loads(zp.read("data.json"))
        cels = [np.frombuffer(zp.read(f"image_data/frames/1/layer_{i}"), np.uint8).reshape(H, W, 4) for i in range(1, len(LAYERS) + 1)]
        gate(f"{pid}: PXO 136x144 one frame, layer order, cels == ORA layers", (d["size_x"], d["size_y"]) == (W, H) and len(d["frames"]) == 1
             and [l["name"] for l in d["layers"]] == LAYERS and all(np.array_equal(c, v1.decode(z.read(f"data/{i:02d}-{n}.png")))
                                                                   for i, (c, n) in enumerate(zip(cels, LAYERS))))
        pngs[pid] = sha(files[f"{pid}.png"][1])
    gate("every v02 pose image unique (no relabeled repeats) and none equals the base or a v01 pose",
         len(set(pngs.values())) == len(pngs) and not (set(pngs.values()) & ({v1.BASE_SHA} | set(_v01_pose_shas()))))
    owner = {}
    for cid, c in CLIPS.items():
        for part in ("enter", "frames"):
            for pid, _ in c.get(part, []):
                owner.setdefault(pid, set()).add(cid)
    gate("each pose belongs to exactly one action", all(len(v) == 1 for v in owner.values()) and set(owner) == set(P))
    gate("every duration whole 1/30 s ticks (30/60 parity)", all(isinstance(n, int) and n >= 1 for c in CLIPS.values()
                                                              for part in ("enter", "frames") for _, n in c.get(part, [])))
    cl = manifest["clips"]
    for cid in ("hit", "skill", "down"):
        gate(f"{cid} clip fits the arena visual {ARENA[cid]} s", cl[cid]["frames_total_s"] <= ARENA[cid] + 1e-9, cl[cid]["frames_total_s"])
    gate("dodge clip fits dodge_time .27 s", cl["dodge"]["frames_total_s"] <= ARENA["dodge"] + 1e-9, cl["dodge"]["frames_total_s"])
    gate("skill has telegraph (2 poses) / contact / recovery", [f["pose"] for f in cl["skill"]["frames"]] ==
         ["skill-tel-a", "skill-tel-b", "skill-strike", "skill-contact", "skill-recover"])
    down = [P[f["pose"]]["body"][1] for f in cl["down"]["frames"]]
    gate("down sinks past rest then settles (overshoot then hold)", down[1] > down[2] > down[0] and cl["down"].get("hold") is True, down)
    gate("hit/dodge/skill end on the approved still", all(cl[c]["then"] == "base" for c in ("hit", "dodge", "skill")))
    gate("hit synchronisation not claimed", manifest["hitSynchronized"] is False)
    return res


def _v01_pose_shas():
    m = json.loads(v1.long(ROOT / "outputs/hero-sea-motion-v01/rpg-2-star-ocean-the-second_heroine-sea-combat_manifest_test-only-v01_20261020-192028-7e93a93c.json").read_text(encoding="utf-8"))
    return [v["sha256"] for v in m["poseFiles"].values()]


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
    else:
        for role, (n, b) in files.items():
            p = v1.long(OUT / n)
            res.append({"key": f"on-disk bytes equal rebuild: {role}", "pass": p.exists() and p.read_bytes() == b, "info": None})
    fails = [r for r in res if not r["pass"]]
    for r in fails:
        print("FAIL", r["key"], r["info"])
    print("HSM02", mode.upper(), "PASS" if not fails else "FAIL", f"{len(res) - len(fails)}/{len(res)}")
    if mode == "check":
        report = {"mode": "check", "gates": res, "passed": len(res) - len(fails), "total": len(res),
                  "source": manifest["source"], "manifestSha256": sha(files["manifest"][1])}
        text = json.dumps(report, indent=1) + "\n"
        p = v1.long(OUT / name("check-report", "json"))
        if not p.exists() or p.read_bytes() != text.encode():
            with open(p, "w", encoding="utf-8", newline="\n") as f:
                f.write(text)
    return 0 if not fails else 1


if __name__ == "__main__":
    sys.exit(main())
