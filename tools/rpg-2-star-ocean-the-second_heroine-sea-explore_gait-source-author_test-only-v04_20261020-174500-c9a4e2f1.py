"""Heroine Sea-of-Stars exploration idle + 12-phase walk source, v04 (gait revision over v03 b81d5c3e).

UNAPPROVED, test-only. Writes only outputs/hsea-gait09/src-v04-<tag>/. Reuses the v03 module's adaptation, segment
split and rotation helpers (imported read-only, nothing in v03 changes) and the same approved inputs:
south idle f00 = approved static bytes verbatim; east/north = Codex imagegen hse-dir08 bases (unapproved).
v04 changes:
- 12 walk phases, contacts at phase 0 (near leg) and 6 (far leg); push-off p5/p11, passing p8/p2.
- side view: near arm (front edge) rotates about the shoulder, far forearm/hand shifts, both counter to the legs;
  arm holes in the upper-body layer are filled row-wise from the adjacent coat pixels of the same row.
- ponytail tuft and scarf tail follow the body bob one phase late (secondary follow-through, source pixels only).
- bridges: 2 frames per contact per direction easing contact -> exact idle0 (supplemental transition manifest).
- west = east mirrored (disclosed).
Usage: python -I <this> [--out-tag YYYYMMDD-HHMMSS]
"""
import hashlib, importlib.util, io, json, sys, zipfile, datetime, math
import xml.etree.ElementTree as ET
from pathlib import Path
import numpy as np
from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
V03 = "tools/rpg-2-star-ocean-the-second_heroine-sea-explore_source-author_test-only-v03_20261020-172000-b81d5c3e.py"
_s = importlib.util.spec_from_file_location("v03", ROOT / V03); v3 = importlib.util.module_from_spec(_s); _s.loader.exec_module(v3)
W, H, PIV, SOLE = v3.W, v3.H, v3.PIV, v3.SOLE
FRAME_MS, IDLE_MS = 40, 600          # nominal authoring only; the runtime distance driver ignores cadence
DT = v3.DT
N = 12
# near-leg plan (thigh deg forward+, knee bend deg, lift px). p0 heel contact, p3 mid-stance, p5 push-off,
# p6 toe-off (far contact), p8 passing (knee high), p10-11 reach. Far leg = plan[(p + 6) % 12].
SIDE = [(26, 3, 0), (18, 8, 0), (9, 5, 0), (0, 2, 0), (-11, 3, 0), (-22, 10, 0),
        (-27, 22, 1), (-14, 40, 4), (2, 44, 5), (15, 32, 4), (24, 14, 2), (27, 5, 0)]
FRONT = [(0, 0), (0, 0), (0, 0), (0, 0), (0, 0), (1, 0), (2, 0), (5, 1), (7, 1), (5, 1), (2, 0), (1, 0)]
BOB = [1, 1, 0, -1, -1, 0, 1, 1, 0, -1, -1, 0]   # +1 = 1 px lower (loading), -1 = 1 px higher (mid-stance)
CLIP = []
ARM_K = 0.32                                      # arm degrees per thigh degree, counter-phase
# side-view arm landmarks on the adapted east base (inspected 8x grid): (x0, x1, y0, y1, pivot, fill-from side)
NEAR_ARM = (51, 58, 44, 73, (53, 45), -1)
FAR_ARM = (30, 38, 47, 66, (37, 46), +1)


def is_teal(a):
    r, g, b = (a[..., i].astype(int) for i in range(3))
    return (a[..., 3] > 0) & (g > r + 25) & (b > r + 25)


def take(up, box, excl):
    x0, x1, y0, y1 = box[:4]
    m = np.zeros((H, W), bool); m[y0:y1 + 1, x0:x1 + 1] = True; m &= (up[..., 3] > 0) & ~excl
    arm = np.where(m[..., None], up, 0).astype(np.uint8)
    rest = up.copy(); side = box[5]
    for y in range(y0, y1 + 1):              # row-wise fill of the arm hole from the adjacent coat column
        xs = np.nonzero(m[y])[0]
        if not len(xs): continue
        src = (xs.min() - 1) if side < 0 else (xs.max() + 1)
        for x in xs:
            rest[y, x] = up[y, src] if 0 <= src < W and up[y, src, 3] and not m[y, src] else 0
    return arm, rest


def follow_mask(base, top, band):
    m = np.zeros((H, W), bool)
    m[top:top + 9] = base[top:top + 9, :, 3] > 0                     # ponytail / crown tuft
    t = is_teal(base); t[:52] = False; t[:, band[0]:band[1] + 1] = False
    return m | t                                                      # scarf tail outside the leg band


def build_dir(base, kind, hip, xsplit, knee_rel, band, extra, facing=1):
    up, left, right = v3.mask_split(base, hip, xsplit, band, extra)
    under = v3.underpaint(base, hip, band)
    top = int(np.nonzero(base[..., 3].any(1))[0][0])
    fm = follow_mask(base, top, band)
    follow = np.where(fm[..., None], up, 0).astype(np.uint8)
    excl = is_teal(base)
    if kind == "side":
        near_arm, up2 = take(up, NEAR_ARM, excl); far_arm, up2 = take(up2, FAR_ARM, excl)
    else:
        near_arm = far_arm = v3.blank(); up2 = up
    idle = {"under-trouser-paint": under, "far-leg": left if facing > 0 else right,
            "near-leg": right if facing > 0 else left, "upper-body": up2,
            "far-arm": far_arm, "near-arm": near_arm, "hair-scarf-follow": follow}
    order = ["under-trouser-paint", "far-leg", "near-leg", "upper-body", "far-arm", "near-arm", "hair-scarf-follow"]
    assert np.array_equal(v3.compose(idle, order), base)
    near, far = idle["near-leg"], idle["far-leg"]
    nh = int(np.nonzero(near[hip:, :, 3].any(0))[0].mean()); fh = int(np.nonzero(far[hip:, :, 3].any(0))[0].mean())

    def pose(q, r, b, blag):
        L = {"under-trouser-paint": np.roll(under, b, 0), "upper-body": np.roll(up2, b, 0),
             "hair-scarf-follow": np.roll(follow, blag, 0)}
        if kind == "side":
            L["near-leg"] = v3.leg_side(near, (nh, hip), hip + knee_rel, q[0], q[1], q[2], facing)
            L["far-leg"] = v3.leg_side(far, (fh, hip), hip + knee_rel, r[0], r[1], r[2], facing)
            L["near-leg"] = np.roll(L["near-leg"], b if q[2] == 0 else min(b, 0), 0)
            L["far-leg"] = np.roll(L["far-leg"], b if r[2] == 0 else min(b, 0), 0)
            for key, st in (("near-leg", q), ("far-leg", r)):   # stance legs: rotation lifts the sole; snap it to ground
                if st[2] == 0:
                    lowest = int(np.nonzero(L[key][..., 3].any(1))[0][-1])
                    if lowest < SOLE: L[key] = np.roll(L[key], SOLE - lowest, 0)
            na = -ARM_K * q[0]                       # near arm swings opposite the near leg
            px, py = NEAR_ARM[4]
            o = v3.blank(); v3.rot_paste(o, near_arm, (px, py), -na * facing, (px, py + b)); L["near-arm"] = o
            fs = int(round(-ARM_K * r[0] / 6.0)) * facing          # far forearm: small horizontal counter-shift
            L["far-arm"] = np.roll(np.roll(far_arm, b, 0), fs, 1)
        else:
            L["near-leg"] = v3.leg_front(near, hip, q[0], q[1], 1 if facing > 0 else -1)
            L["far-leg"] = v3.leg_front(far, hip, r[0], r[1], -1 if facing > 0 else 1)
            for key, st in (("near-leg", q[0]), ("far-leg", r[0])):
                if b > 0 and st == 0: L[key] = v3.leg_front(L[key], hip, 0, 0, 1)
            L["near-arm"] = v3.blank(); L["far-arm"] = v3.blank()
        if b < 0:
            L["under-trouser-paint"] = under.copy()
            for key in ("near-leg", "far-leg"):
                lg = L[key]; tp = lg[hip]; gap = (lg[hip - 1, :, 3] == 0) & (tp[:, 3] > 0)
                lg[hip - 1][gap] = tp[gap]
        clipped = 0
        for k in L:                                  # ground plane: layers carry exactly what the export shows
            clipped += int((L[k][SOLE + 1:, :, 3] > 0).sum()); L[k][SOLE + 1:] = 0
        CLIP.append(clipped)
        return v3.compose(L, order), L

    plan = SIDE if kind == "side" else FRONT
    walk = [pose(plan[p], plan[(p + 6) % N], BOB[p], BOB[(p - 1) % N]) for p in range(N)]
    bridges = {}
    for c in (0, 6):                                   # contact -> idle0, 2 eased frames (2/3, 1/3 of contact pose)
        q, r = plan[c], plan[(c + 6) % N]
        fr = []
        for k in (2 / 3, 1 / 3):
            sc = lambda t: tuple(int(round(v * k)) for v in t)
            fr.append(pose(sc(q), sc(r), 0, 0))
        bridges[c] = fr
    return [(base.copy(), idle)], walk, bridges, order, (nh, fh)


def sole_anchor(layer):
    a = layer[..., 3] > 0
    ys = np.nonzero(a.any(1))[0]
    if not len(ys): return None
    yb = int(ys[-1]); xs = np.nonzero(a[yb - 1:yb + 1].any(0))[0]
    return [round(float(xs.mean()), 1), yb]


def main():
    tag = sys.argv[sys.argv.index("--out-tag") + 1] if "--out-tag" in sys.argv else datetime.datetime.now().strftime("%Y%m%d-%H%M%S")
    uid = v3.sha(("v04" + tag).encode())[:8]
    run = ROOT / "outputs" / "hsea-gait09" / f"src-v04-{tag}"; run.mkdir(parents=True, exist_ok=True)
    raw = (ROOT / v3.SOUTH).read_bytes(); assert v3.sha(raw) == v3.SOUTH_SHA
    south = np.array(Image.open(io.BytesIO(raw)).convert("RGBA")); pal = v3.palette_of(south)
    bases, adapt_info = {"south": south}, {}
    for d, p in v3.GEN.items():
        bases[d], adapt_info[d] = v3.adapt(p, pal)
        adapt_info[d].update(file=p, sha256=v3.sha((ROOT / p).read_bytes()))
    spec_dirs = {"south": ("front", 68, 41, 14, (27, 55), 12), "north": ("front", 71, 41, 14, (29, 52), 3),
                 "east": ("side", 73, 44, 13, (29, 57), 0)}
    out = {d: build_dir(bases[d], *s) for d, s in spec_dirs.items()}
    ef, ew, eb, eo, eh = out["east"]
    mir = lambda L: {k: v[:, ::-1].copy() for k, v in L.items()}
    mf = lambda fr: [(a[:, ::-1].copy(), mir(L)) for a, L in fr]
    out["west"] = (mf(ef), mf(ew), {c: mf(v) for c, v in eb.items()}, eo, eh)
    spec = importlib.util.spec_from_file_location("pxo_writer", ROOT / v3.WRITER)
    wr = importlib.util.module_from_spec(spec); spec.loader.exec_module(wr)
    wr.W, wr.H = W, H; wr.to_rgba = lambda a: np.ascontiguousarray(a, np.uint8)
    pre = "rpg-2-star-ocean-the-second_heroine-sea"
    actions = {"idle": {}, "walk": {}}; src = []; trans = {}; anchors = {}
    for d in ("south", "west", "north", "east"):
        idle, walk, bridges, order, _ = out[d]
        allf = []
        for act, fr in (("idle", idle), ("walk", walk)):
            actions[act][d] = []
            for i, (arr, L) in enumerate(fr):
                b = raw if (d == "south" and act == "idle") else v3.png(arr)
                if d == "south" and act == "idle": assert np.array_equal(arr, south)
                fn = f"{pre}_explore-{d}-{act}-f{i:02d}_unapproved-v04_{tag}-{uid}.png"
                (run / fn).write_bytes(b)
                actions[act][d].append({"file": fn, "duration_ms": IDLE_MS if act == "idle" else FRAME_MS})
                allf.append((L, (IDLE_MS if act == "idle" else FRAME_MS) / 1000))
        anchors[d] = [{"phase": p, "near": sole_anchor(L["near-leg"]), "far": sole_anchor(L["far-leg"])} for p, (_, L) in enumerate(walk)]
        trans[d] = {}
        for c, fr in bridges.items():
            lst = []
            for k, (arr, L) in enumerate(fr):
                fn = f"{pre}_explore-{d}-stop-c{c:02d}-b{k}_unapproved-v04_{tag}-{uid}.png"
                (run / fn).write_bytes(v3.png(arr)); lst.append({"file": fn, "sha256": v3.sha((run / fn).read_bytes())})
                allf.append((L, FRAME_MS / 1000))
            trans[d][f"contact{c}"] = {"from_walk_frame": c, "bridge": lst, "final": actions["idle"][d][0]["file"]}
        per = [{k: L[k] for k in order} for L, _ in allf]
        pxo = f"{pre}_explore-{d}-layers_unapproved-v04_{tag}-{uid}.pxo"
        (run / pxo).write_bytes(wr.make_pxo(per, [t for _, t in allf], v3.png(v3.compose(per[0], order)), pxo[:-4] + ".png", 16, order=order, dt=DT))
        ora = f"{pre}_explore-{d}-idle0-layers_unapproved-v04_{tag}-{uid}.ora"
        with zipfile.ZipFile(run / ora, "w") as z:
            z.writestr(zipfile.ZipInfo("mimetype", DT), "image/openraster")
            z.writestr(zipfile.ZipInfo("mergedimage.png", DT), v3.png(v3.compose(per[0], order)))
            root = ET.Element("image", {"w": str(W), "h": str(H)}); st = ET.SubElement(root, "stack")
            for i, k in enumerate(order[::-1]):
                z.writestr(zipfile.ZipInfo(f"data/l{i}.png", DT), v3.png(per[0][k]))
                ET.SubElement(st, "layer", {"name": k, "src": f"data/l{i}.png", "x": "0", "y": "0"})
            z.writestr(zipfile.ZipInfo("stack.xml", DT), ET.tostring(root, encoding="utf8"))
        src += [{"direction": d, "file": pxo, "format": "pixelorama-pxo", "sha256": v3.sha((run / pxo).read_bytes()),
                 "frame_order": "idle f00, walk f00-f11, stop c00 b0-b1, stop c06 b0-b1"},
                {"direction": d, "file": ora, "format": "openraster-supplemental-idle0", "sha256": v3.sha((run / ora).read_bytes())}]
    tool = {"file": str(Path(__file__).relative_to(ROOT)).replace("\\", "/"),
            "sha256TextLf": v3.sha(Path(__file__).read_bytes().replace(b"\r\n", b"\n"))}
    man = {"schema": "worlds-between.exploration-source.v1", "actor_id": "protagonist-female", "density": 2,
           "frame_size": [W, H], "pivot": list(PIV), "actions": actions, "source_files": src,
           "status": "UNAPPROVED test-only candidate; generated-base adaptation; no runtime/default change",
           "author_tool": tool, "reused_v03_module": {"file": V03, "sha256TextLf": v3.sha((ROOT / V03).read_bytes().replace(b"\r\n", b"\n"))},
           "generated_bases": adapt_info, "approved_south": {"file": v3.SOUTH, "sha256": v3.SOUTH_SHA},
           "gait": {"walk_frames": N, "phase_index": "floor(phase*12)", "contacts": {"near": 0, "far": 6},
                    "nominal_frame_ms": FRAME_MS, "side_plan": SIDE, "front_plan": FRONT, "bob": BOB, "arm_k": ARM_K, "ground_clip_px_per_pose": CLIP},
           "disclosure": ["west = east mirrored; asymmetric straps/scarf tail flip sides",
                          "arms articulated in east/west only; north/south arms remain fixed to the torso layer",
                          "south walk legs come from the approved static's own legs; idle f00 exact bytes"]}
    mp = run / f"{pre}_explore-source-manifest_unapproved-v04_{tag}-{uid}.json"
    mp.write_text(json.dumps(man, indent=1), encoding="utf-8", newline="\n")
    tp = run / f"{pre}_explore-stop-transition-manifest_unapproved-v04_{tag}-{uid}.json"
    tp.write_text(json.dumps({"schema": "worlds-between.exploration-stop-transition.supplemental.v1", "source_manifest": mp.name,
                              "rule": "on release: continue to next contact (0 or 6) within <=120 ms, play its 2 bridge frames, then exact idle0",
                              "directions": trans, "sole_anchors_source_px": anchors, "author_tool": tool}, indent=1),
                  encoding="utf-8", newline="\n")
    print(mp)


if __name__ == "__main__":
    main()
