"""Heroine (Sea of Stars direction) combat motion v04: re-authored DODGE and SKILL body poses only. TEST-ONLY, UNAPPROVED.

v01-v03 authors are frozen and only imported (hash-pinned, read-only). Root review: v02 dodge/skill moved the whole body
rigidly and read too upright in normal play. v04 changes the pose method for these seven poses, reusing the v03 builder:

  * the pelvis drops/shifts (hip-knee compression from two-bone IK against planted or airborne boots) and the upper body
    (ponytail, torso, head) is ROTATED as one group about the waist, so torso inclination is relative to the feet;
  * dodge: tucked backward hop with the chest pitched over the knees and the hair trailing forward, then a deep landing
    crouch (pelvis ~10 texels lower) with the blade kept low in front and the ponytail following through;
  * skill (Situational Insight, a self-buff): a forward-bowed coil (counterpose, blade drawn low behind), then the chest
    opens back and up with the blade raised upright in front (no impact smear: it is not a hit), then settles;
  * the sword arm is repainted from the rotated shoulder (v03 paint_arm_at); eyes stay open in all seven poses.

Pivot (64,136), 136x144 cell, the still's palette and binary alpha are unchanged; timing/ticks are not touched here.

    build | check (default)
"""
from pathlib import Path
import hashlib, importlib.util, io, json, math, os, sys, zipfile
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
V03 = ROOT / "tools/rpg-2-star-ocean-the-second_heroine-sea_combat-motion-author_test-only-v03_20261020-194523-e3b8d061.py"
V03_PIN = "d748e3ded03ff2725fba541aeb717388388587427e7636a9a257b954497f0a69"
OUT = ROOT / "outputs/hero-sea-motion-v04"
SLUG, SUBJECT, VER, STAMP, UID = "rpg-2-star-ocean-the-second", "heroine-sea-combat", "test-only-v04", "20261021-033551", "6598ac4e"
BASELINE_INDEX = "game/data/heroine-sea-combat-v01/rpg-2-star-ocean-the-second_heroine-sea-combat_spritesheet-index_v01_20261020-201338-38ecfcb0.json"
BASELINE_INDEX_SHA = "1abb5b67b3bf59c02b3c747068789a01509812aee97c105b9f5c15c7a60ffa49"

assert hashlib.sha256(V03.read_bytes().replace(b"\r\n", b"\n")).hexdigest() == V03_PIN, "frozen v03 author changed"
_spec = importlib.util.spec_from_file_location("hsm_v03", str(V03))
v3 = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(v3)          # v03 itself pin-checks v01/v02
v1 = v3.v1
W, H, LAYERS, PIN = v1.W, v1.H, v1.LAYERS, v1.PIN

# Source pose definitions. body: pelvis/upper-body offset (texels); lean: upper-body rotation about the waist (deg, + =
# forward toward the enemy); feet: whole-texel boot offsets (negative y = airborne); pony: extra hair follow-through;
# arm reach: grip offset from the ROTATED shoulder; blade: blade angle (deg, screen y down).
P = {
    "dodge-a": {"body": (-5, 3), "lean": 9.0, "pony": (3, -2), "legs": "ik", "eyes": "open",
                "feet": {"back": (-6, -6), "front": (-3, -5)}, "arm": {"reach": (11, 15), "blade": -55.0}},
    "dodge-b": {"body": (-7, 10), "lean": 15.0, "pony": (3, 2), "legs": "ik", "eyes": "open",
                "feet": {"back": (-6, 0), "front": (-4, 0)}, "arm": {"reach": (12, 14), "blade": -35.0}},
    "skill-tel-a": {"body": (-2, 6), "lean": 10.0, "pony": (2, 1), "legs": "ik", "eyes": "open",
                    "feet": {"back": (0, 0), "front": (0, 0)}, "arm": {"reach": (3, 17), "blade": 160.0}},
    "skill-tel-b": {"body": (-3, 9), "lean": 16.0, "pony": (3, 2), "legs": "ik", "eyes": "open",
                    "feet": {"back": (0, 0), "front": (-2, 0)}, "arm": {"reach": (1, 15), "blade": 172.0}},
    "skill-strike": {"body": (0, 3), "lean": -10.0, "pony": (-2, -2), "legs": "ik", "eyes": "open",
                     "feet": {"back": (0, 0), "front": (2, 0)}, "arm": {"reach": (10, 5), "blade": -84.0}},
    "skill-contact": {"body": (1, 4), "lean": -13.0, "pony": (-3, -2), "legs": "ik", "eyes": "open",
                      "feet": {"back": (0, 0), "front": (2, 0)}, "arm": {"reach": (12, 3), "blade": -80.0}},
    "skill-recover": {"body": (0, 3), "lean": -4.0, "pony": (-1, 0), "legs": "ik", "eyes": "open",
                      "feet": {"back": (0, 0), "front": (1, 0)}, "arm": {"reach": (12, 13), "blade": -50.0}},
}
AIRBORNE = {"dodge-a"}
v3.P = P                               # v03 build() reads its module-level pose table


def sha(b):
    return hashlib.sha256(b).hexdigest()


def fid(role):
    return sha(f"{UID}:{role}".encode())[:8]


def name(purpose, ext):
    return f"{SLUG}_{SUBJECT}_{purpose}_{VER}_{STAMP}-{fid(purpose)}.{ext}"


def rel(p):
    return str(p.relative_to(ROOT)).replace("\\", "/")


def outputs():
    raw = v1.long(v1.BASE).read_bytes()
    assert sha(raw) == v1.BASE_SHA
    S = v1.decode(raw)
    R = v1.rig(S)
    poses = {pid: dict(zip(("layers", "info"), v3.build(pid, S, R))) for pid in P}
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
                                               order=LAYERS, dt=(2026, 10, 21, 3, 35, 51)))
        files[f"{pid}.x4"] = (name(f"pose-{pid}-inspect-x4", "png"), v1.png_bytes(v1.inspect_x4(flat)))
    revision = {
        "schema": "worlds-between.heroine-combat-pose-revision/1",
        "baselineIndex": BASELINE_INDEX, "baselineIndexSha256": BASELINE_INDEX_SHA,
        "cell": [W, H], "pivot": [64, 136], "tickRate": 30,
        "overrides": {pid: {"png": rel(OUT / files[f"{pid}.png"][0]), "sha256": sha(files[f"{pid}.png"][1]),
                            "pxo": rel(OUT / files[f"{pid}.pxo"][0]), "pxoSha256": sha(files[f"{pid}.pxo"][1]),
                            "ora": rel(OUT / files[f"{pid}.ora"][0]), "oraSha256": sha(files[f"{pid}.ora"][1])} for pid in P},
        "artApproved": False,
    }
    files["revision"] = (name("pose-revision-manifest", "json"), (json.dumps(revision, indent=2) + "\n").encode())
    author = {
        "status": "TEST-ONLY v04 revision of DODGE and SKILL body poses only; UNAPPROVED; not a runtime package.",
        "frozenInputs": {rel(V03): V03_PIN, rel(v1.BASE): v1.BASE_SHA},
        "method": __doc__.strip().split("\n\n")[1],
        "poses": {pid: {**{k: (list(v) if isinstance(v, tuple) else v) for k, v in P[pid].items() if k not in ("arm", "feet")},
                        "feet": {k: list(v) for k, v in P[pid]["feet"].items()},
                        "arm": {"reachFromShoulder": list(P[pid]["arm"]["reach"]), "bladeDeg": P[pid]["arm"]["blade"]},
                        "rig": poses[pid]["info"]} for pid in P},
        "source": {"file": rel(Path(__file__).resolve()), "sha256TextLf": sha(Path(__file__).read_bytes().replace(b"\r\n", b"\n"))},
        "files": {role: {"name": n, "sha256": sha(b)} for role, (n, b) in sorted(files.items())},
        "artApproved": False, "timingChanged": False, "runtimeDefaultChanged": False, "guiSaveAsVerified": False,
        "nativeCliChecked": False,
    }
    files["author"] = (name("author-manifest", "json"), (json.dumps(author, indent=1) + "\n").encode())
    return files, flats, poses, revision, S


def gates(files, flats, poses, revision, S):
    res = []

    def gate(k, ok, info=None):
        res.append({"key": k, "pass": bool(ok), "info": info})
    base_cols = {tuple(c) for c in S[S[..., 3] > 0][:, :3].tolist()}
    gate("baseline index sha", sha(v1.long(ROOT / BASELINE_INDEX).read_bytes()) == BASELINE_INDEX_SHA)
    gate("revision manifest keys exact", list(revision) == ["schema", "baselineIndex", "baselineIndexSha256", "cell", "pivot",
                                                           "tickRate", "overrides", "artApproved"] and
         sorted(revision["overrides"]) == sorted(P) and
         all(list(o) == ["png", "sha256", "pxo", "pxoSha256", "ora", "oraSha256"] for o in revision["overrides"].values()))
    for pid, flat in flats.items():
        op = flat[..., 3] > 0
        ys, xs = np.nonzero(op)
        cols = {tuple(c) for c in flat[op][:, :3].tolist()}
        info = poses[pid]["info"]
        gate(f"{pid}: binary alpha + palette subset of still", set(np.unique(flat[..., 3]).tolist()) <= {0, 255} and cols <= base_cols, len(cols))
        gate(f"{pid}: head/hair not cut (top row >= 2), margins clear", ys.min() >= 2 and not op[:, :1].any() and not op[:, -1:].any()
             and not op[PIN[1]:].any(), [int(xs.min()), int(xs.max()), int(ys.min()), int(ys.max())])
        if pid in AIRBORNE:
            gate(f"{pid}: airborne (lowest row 125..133)", 125 <= ys.max() <= 133, int(ys.max()))
        else:
            gate(f"{pid}: grounded (lowest row 135)", ys.max() == PIN[1] - 1, int(ys.max()))
        st = [abs(j[k]) for j in info["joints"].values() for k in ("thighStretch", "shinStretch")]
        gate(f"{pid}: no joint-capsule stretch (|stretch| <= 0.6 texel)", max(st) <= 0.6, round(max(st), 3))
        new = [c for c in v1.hole_components(flat) if len(c) <= 4]
        gate(f"{pid}: no pinhole pockets", not new, len(new))
        z = zipfile.ZipFile(io.BytesIO(files[f"{pid}.ora"][1]))
        zp = zipfile.ZipFile(io.BytesIO(files[f"{pid}.pxo"][1]))
        cels = [np.frombuffer(zp.read(f"image_data/frames/1/layer_{i}"), np.uint8).reshape(H, W, 4) for i in range(1, len(LAYERS) + 1)]
        gate(f"{pid}: PNG == layers, ORA merged == PNG, PXO cels == ORA layers",
             np.array_equal(v1.decode(files[f"{pid}.png"][1]), flat) and np.array_equal(v1.decode(z.read("mergedimage.png")), flat) and
             all(np.array_equal(c, v1.decode(z.read(f"data/{i:02d}-{n}.png"))) for i, (c, n) in enumerate(zip(cels, LAYERS))))
        gate(f"{pid}: torso inclined relative to feet (|lean| >= 8 deg)", abs(P[pid]["lean"]) >= 8 or pid == "skill-recover", P[pid]["lean"])
    hip = {pid: max(j["hip"][1] for j in poses[pid]["info"]["joints"].values()) for pid in P}
    gate("dodge-b: pelvis compressed >= 8 texels below still hips (86.5)", hip["dodge-b"] - 86.5 >= 8, round(hip["dodge-b"], 2))
    gate("dodge: moves backward (pelvis and boots shift -x)", P["dodge-b"]["body"][0] < 0 and all(v[0] < 0 for v in P["dodge-b"]["feet"].values()))
    gate("skill: counterpose then opening (tel lean > 0, strike/contact lean < 0, recover |lean| smaller)",
         P["skill-tel-a"]["lean"] > 0 < P["skill-tel-b"]["lean"] and P["skill-strike"]["lean"] < 0 and P["skill-contact"]["lean"] < 0
         and abs(P["skill-recover"]["lean"]) < abs(P["skill-contact"]["lean"]))
    gate("skill-tel-b: pelvis coiled >= 7 texels below still", hip["skill-tel-b"] - 86.5 >= 7, round(hip["skill-tel-b"], 2))
    shas = [sha(files[f"{p}.png"][1]) for p in P]
    gate("seven pose images unique", len(set(shas)) == 7)
    return res


def main():
    mode = sys.argv[1] if len(sys.argv) > 1 else "check"
    files, flats, poses, revision, S = outputs()
    det = all(files[k][1] == b for k, (n, b) in outputs()[0].items())
    res = [{"key": "deterministic rebuild", "pass": det, "info": None}] + gates(files, flats, poses, revision, S)
    if mode == "build":
        os.makedirs(v1.long(OUT), exist_ok=True)
        for role, (n, b) in files.items():
            p = v1.long(OUT / n)
            if p.exists():
                assert p.read_bytes() == b, f"refusing to overwrite a different file: {n}"
            else:
                p.write_bytes(b)
    else:
        for role, (n, b) in files.items():
            p = v1.long(OUT / n)
            res.append({"key": f"on-disk bytes equal rebuild: {role}", "pass": p.exists() and p.read_bytes() == b, "info": None})
    fails = [r for r in res if not r["pass"]]
    for r in fails:
        print("FAIL", r["key"], r["info"])
    print("HSM04", mode.upper(), "PASS" if not fails else "FAIL", f"{len(res) - len(fails)}/{len(res)}")
    if mode == "check":
        text = json.dumps({"mode": "check", "gates": res, "passed": len(res) - len(fails), "total": len(res),
                           "revisionSha256": sha(files["revision"][1])}, indent=1) + "\n"
        with open(v1.long(OUT / name("check-report", "json")), "w", encoding="utf-8", newline="\n") as f:
            f.write(text)
    return 0 if not fails else 1


if __name__ == "__main__":
    sys.exit(main())
