"""Heroine Sea-of-Stars phase-aware side stop source v01 (contract 99b25894). UNAPPROVED, test-only.
Fixes the v08 first side-stop defect: walk -> b0 switched arm method (authored sleeve -> original idle glove) and snapped
the legs toward the nearest contact 0/6. Here every one of the 12 outgoing east/west walk phases gets its own 4-sample
bridge: s0 = exact outgoing walk frame, s1 = early release (k=0.4), s2 = near rest (k=0.8), s3 = exact original idle0.
s1/s2 are drawn with the same v08 method as walk (v06 paint_leg legs, v08 coat panel upper body, v08 paint_arm sleeve
arms, coat-front-edge/hair layers bob-rolled), with foot targets, lift, bob, scarf sway and both arm angle pairs linearly
interpolated from the outgoing phase toward rest -> one continuous arm path; no glove swap before s3, no crossfade,
noise, random or body scale change. The single swap to the original glove happens only at s3 (exact idle0, protected).
Imports the v08 tool (b4e61d02) read-only and regenerates its east layers; asserts all 52 idle/walk and the 16 legacy
stop PNGs equal the v08 run bytes before writing. Writes only outputs/hsea-stop15/src-v01-<tag>/.
West = east mirrored (disclosed, as v08). Usage: python -I <this> [--out-tag YYYYMMDD-HHMMSS]
"""
import importlib.util, json, sys, datetime, math, io
from pathlib import Path
import numpy as np
from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
V08 = "tools/rpg-2-star-ocean-the-second_heroine-sea-explore_arm-source-author_test-only-v08_20261020-222336-b4e61d02.py"
V08_RUN = "outputs/hsea-arms12/src-v08-20261020-222336"
V08_TAG, V08_UID = "20261020-222336", "0ad0e3f5"
_s = importlib.util.spec_from_file_location("v08", ROOT / V08); v8 = importlib.util.module_from_spec(_s); _s.loader.exec_module(v8)
v6, v4, v3 = v8.v6, v8.v4, v8.v3
W, H, SOLE, N = v3.W, v3.H, v3.SOLE, 12
K = (0.0, 0.4, 0.8, 1.0)            # release fraction per sample; s0/s3 are exact copies, not re-rendered
IDLE_FOOT = (52, 36)                # v08 b0 idle foot targets (near, far)
PRE = "rpg-2-star-ocean-the-second_heroine-sea"


def xp(p):
    p = str(p)
    return Path("\\\\?\\" + p) if sys.platform == "win32" and not p.startswith("\\\\?\\") else Path(p)


def lerp(a, b, k): return a + (b - a) * k


def build_east():
    """Re-run the v08 east construction (same calls, same order) and return walk layers, idle layers, helpers."""
    raw = (ROOT / v3.SOUTH).read_bytes(); assert v3.sha(raw) == v3.SOUTH_SHA
    south = np.array(Image.open(io.BytesIO(raw)).convert("RGBA")); pal = v3.palette_of(south)
    base, _ = v3.adapt(v3.GEN["east"], pal)
    ef, ew, eb, order, _ = v4.build_dir(base, "side", 73, 44, 13, (29, 57), 0)
    idle_L = ef[0][1]
    trouser = v6.ramp(idle_L["near-leg"], (74, 92), lambda c: c[2] > c[0])
    boot = v6.ramp(idle_L["near-leg"], (93, 104), lambda c: c[0] > c[2])
    v6.SRC["near"], v6.SRC["far"] = idle_L["near-leg"], idle_L["far-leg"]; v6.PAL = pal.astype(float)
    blank = v3.blank()
    ren = {"near-arm": "coat-front-edge", "far-arm": "idle-arm-glove"}
    side_idle = {ren.get(k, k): v for k, v in idle_L.items()}
    side_idle["near-arm-sleeve"] = blank.copy(); side_idle["far-arm-sleeve"] = blank.copy()
    assert np.array_equal(v3.compose(side_idle, v8.ORDER_SIDE), ef[0][0])
    glove = idle_L["far-arm"][..., 3] > 0; up0 = idle_L["upper-body"]
    gy = np.nonzero(glove.any(1))[0]; gy0, gy1 = int(gy[0]), int(gy[-1])
    left = lambda row: int(np.nonzero(row[:, 3] > 0)[0][0])
    e_top, e_bot = left(up0[gy0 - 1]), left(up0[gy1 + 1])
    navy = lambda c: int(c[2]) >= int(c[0])
    panel = up0.copy()                                   # identical to v08 coat panel construction
    for y in range(gy0, gy1 + 1):
        xs = np.nonzero(glove[y])[0]
        if not len(xs): continue
        edge = int(round(e_top + (e_bot - e_top) * (y - gy0) / max(1, gy1 - gy0))); w = int(xs.max() - xs.min() + 1)
        navy_row = [x for x in range(xs.max() + 1, W) if up0[y, x, 3] and navy(up0[y, x]) and not glove[y, x]]
        for x in xs:
            if x < edge: panel[y, x] = 0; continue
            sx = x + w
            if 0 <= sx < W and up0[y, sx, 3] and navy(up0[y, sx]) and not glove[y, sx]: panel[y, x] = up0[y, sx]
            elif navy_row: panel[y, x] = up0[y, min(navy_row, key=lambda q: abs(q - sx))]
            else: panel[y, x, :3] = v8.SLEEVE[1]; panel[y, x, 3] = 255
            if x == edge: panel[y, x, :3] = v8.SLEEVE[0]

    def pose(p, k):
        """v08 walk method at outgoing phase p, released by fraction k toward rest (k=0 reproduces walk[p])."""
        b = int(round(v4.BOB[p] * (1 - k)))
        sw = int(round(-math.sin(2 * math.pi * (p - 1.5) / N) * (1 - k)))
        src = ew[p][1]
        L = {"upper-body": src["upper-body"].copy(), "coat-front-edge": np.roll(idle_L["near-arm"], b, 0),
             "hair-scarf-follow": v8.sway(np.roll(idle_L["hair-scarf-follow"], b, 0) if k else src["hair-scarf-follow"], sw)}
        nf, nl = v6.foot_x(p); ff, fl = v6.foot_x(p + 6)
        hip = (v6.HIP[0], v6.HIP[1] + b)
        L["near-leg"], _, _ = v6.paint_leg(hip, lerp(nf, IDLE_FOOT[0], k), nl * (1 - k), 1, trouser, boot, False)
        L["far-leg"], _, _ = v6.paint_leg(hip, lerp(ff, IDLE_FOOT[1], k), fl * (1 - k), 1, trouser, boot, True)
        L["under-trouser-paint"] = blank.copy()
        na = [lerp(a, r, k) for a, r in zip(v8.arm_angles(p), v8.REST)]
        fa = [lerp(a, r, k) for a, r in zip(v8.arm_angles(p + 6), v8.REST)]
        L["idle-arm-glove"] = blank.copy(); L["upper-body"] = np.roll(panel, b, 0)
        L["near-arm-sleeve"], ne, nw = v8.paint_arm((v8.SHOULDER[0], v8.SHOULDER[1] + b), *na, v8.SLEEVE, v8.GAUNT)
        L["far-arm-sleeve"], fe, fw = v8.paint_arm((v8.FAR_SHOULDER[0], v8.FAR_SHOULDER[1] + b), *fa, v8.FAR_SLEEVE, v8.FAR_GAUNT)
        for kk in L: L[kk][SOLE + 1:] = 0
        info = {"k": k, "bob": b, "scarf_dx": sw, "near_foot": [round(lerp(nf, IDLE_FOOT[0], k), 2), round(nl * (1 - k), 2)],
                "far_foot": [round(lerp(ff, IDLE_FOOT[1], k), 2), round(fl * (1 - k), 2)],
                "near_deg": [round(v, 2) for v in na], "far_deg": [round(v, 2) for v in fa],
                "near_wrist": nw, "far_wrist": fw, "method": "v08 walk method (paint_leg + coat panel + paint_arm)"}
        return v3.compose(L, v8.ORDER_SIDE), L, info
    return pose, side_idle


def main():
    tag = sys.argv[sys.argv.index("--out-tag") + 1] if "--out-tag" in sys.argv else datetime.datetime.now().strftime("%Y%m%d-%H%M%S")
    uid = v3.sha(("hsea-stop15-v01" + tag).encode())[:8]
    old = xp(ROOT / V08_RUN)
    run = xp(ROOT / "outputs" / "hsea-stop15" / f"src-v01-{tag}"); run.mkdir(parents=True, exist_ok=False)
    oname = lambda s: f"{PRE}_{s}_unapproved-v08_{V08_TAG}-{V08_UID}"
    nname = lambda s, ext: f"{PRE}_{s}_unapproved-stop15-v01_{tag}-{uid}.{ext}"
    om = json.loads((old / (oname("explore-source-manifest") + ".json")).read_text(encoding="utf-8"))
    ot = json.loads((old / (oname("explore-stop-transition-manifest") + ".json")).read_text(encoding="utf-8"))
    pose, side_idle = build_east()
    # protected originals: regenerated east layers must reproduce the v08 bytes exactly
    walk_L = []
    for p in range(N):
        arr, L, _ = pose(p, 0.0)
        assert v3.png(arr) == (old / (oname(f"explore-east-walk-f{p:02d}") + ".png")).read_bytes(), p
        walk_L.append(L)
    assert v3.png(v3.compose(side_idle, v8.ORDER_SIDE)) == (old / (oname("explore-east-idle-f00") + ".png")).read_bytes()
    provenance, copied = [], {}
    # copy all 52 idle/walk + 16 legacy stop PNGs with new unique names (bytes unchanged)
    actions = {"idle": {}, "walk": {}}
    for act in ("idle", "walk"):
        for d, fr in om["actions"][act].items():
            actions[act][d] = []
            for i, f in enumerate(fr):
                b = (old / f["file"]).read_bytes(); fn = nname(f"explore-{d}-{act}-f{i:02d}", "png")
                (run / fn).write_bytes(b); copied[f["file"]] = fn
                actions[act][d].append({"file": fn, "duration_ms": f["duration_ms"]})
                provenance.append({"file": fn, "copied_from": f"{V08_RUN}/{f['file']}", "sha256": v3.sha(b)})
    trans = {}
    for d, cs in ot["directions"].items():
        trans[d] = {}
        for c, e in cs.items():
            lst = []
            for k, bf in enumerate(e["bridge"]):
                b = (old / bf["file"]).read_bytes(); assert v3.sha(b) == bf["sha256"]
                fn = nname(f"explore-{d}-stop-c{e['from_walk_frame']:02d}-b{k}", "png")
                (run / fn).write_bytes(b); lst.append({"file": fn, "sha256": v3.sha(b)})
                provenance.append({"file": fn, "copied_from": f"{V08_RUN}/{bf['file']}", "sha256": v3.sha(b)})
            trans[d][c] = {"from_walk_frame": e["from_walk_frame"], "bridge": lst, "final": copied[e["final"]]}
    # new phase bridges: east authored, west mirrored
    phase, info, frames = {"east": {}, "west": {}}, {}, {"east": [], "west": []}
    idle_arr = v3.compose(side_idle, v8.ORDER_SIDE)
    for p in range(N):
        samples = [(None, walk_L[p], {"k": 0.0, "exact": f"walk f{p:02d}"})]
        for k in K[1:3]:
            arr, L, inf = pose(p, k); samples.append((arr, L, inf))
        samples.append((idle_arr, side_idle, {"k": 1.0, "exact": "idle f00"}))
        info[f"phase{p}"] = [s[2] for s in samples]
        for d in ("east", "west"):
            lst = []
            for si, (arr, L, _) in enumerate(samples):
                LL = L if d == "east" else {kk: v[:, ::-1].copy() for kk, v in L.items()}
                if si == 0: b = (run / actions["walk"][d][p]["file"]).read_bytes()
                elif si == 3: b = (run / actions["idle"][d][0]["file"]).read_bytes()
                else: b = v3.png(v3.compose(LL, v8.ORDER_SIDE))
                assert np.array_equal(v3.compose(LL, v8.ORDER_SIDE), np.array(Image.open(io.BytesIO(b)).convert("RGBA"))), (d, p, si)
                fn = nname(f"explore-{d}-phstop-p{p:02d}-s{si}", "png"); (run / fn).write_bytes(b)
                lst.append({"file": fn, "sha256": v3.sha(b)}); frames[d].append(LL)
            phase[d][f"phase{p}"] = {"from_walk_frame": p, "bridge": lst}
    spec = importlib.util.spec_from_file_location("pxo_writer", ROOT / v3.WRITER)
    wr = importlib.util.module_from_spec(spec); spec.loader.exec_module(wr)
    wr.W, wr.H = W, H; wr.to_rgba = lambda a: np.ascontiguousarray(a, np.uint8)
    src = []
    for d in ("east", "west"):
        per = [{k: L[k] for k in v8.ORDER_SIDE} for L in frames[d]]
        pxo = nname(f"explore-{d}-phstop-layers", "pxo")
        (run / pxo).write_bytes(wr.make_pxo(per, [v4.FRAME_MS / 1000] * len(per), v3.png(v3.compose(per[0], v8.ORDER_SIDE)),
                                            pxo[:-4] + ".png", 16, order=v8.ORDER_SIDE, dt=v3.DT))
        src.append({"direction": d, "file": pxo, "format": "pixelorama-pxo", "sha256": v3.sha((run / pxo).read_bytes()),
                    "frame_order": "phase p00..p11 x sample s0..s3 (frame = 4*p + s)", "frames": len(per),
                    "layers_bottom_to_top": list(v8.ORDER_SIDE)})
    tool = {"file": str(Path(__file__).relative_to(ROOT)).replace("\\", "/"),
            "sha256TextLf": v3.sha(Path(__file__).read_bytes().replace(b"\r\n", b"\n"))}
    old_src = [{"file": f"{V08_RUN}/{s['file']}", "format": s["format"], "sha256": s["sha256"], "direction": s["direction"],
                "status": "read-only original 52-frame v08 source package (not copied)"} for s in om["source_files"]]
    man = dict(om); man.update({"actions": actions, "source_files": src, "original_source_files": old_src,
        "status": "UNAPPROVED test-only; v08 idle/walk bytes copied unchanged; phase-aware side stop PXOs only",
        "author_tool": tool, "copied_png_provenance": provenance,
        "reused_v08_module": {"file": V08, "sha256TextLf": v3.sha((ROOT / V08).read_bytes().replace(b"\r\n", b"\n"))}})
    man["disclosure"] = list(om.get("disclosure", [])) + ["phase bridges s3 is exact idle0: the only arm-method swap (authored sleeve -> original glove) happens there",
                                                        "west phase bridges = east mirrored", "no GUI/runtime fluidity claim; metrics only"]
    mp = run / nname("explore-source-set", "json")
    mp.write_text(json.dumps(man, indent=1), encoding="utf-8", newline="\n")
    tp = run / nname("explore-stop-transition-manifest", "json")
    tp.write_text(json.dumps({"schema": "worlds-between.exploration-stop-transition.supplemental.v1",
        "source_manifest": mp.name, "source_set": mp.name, "source_set_sha256": v3.sha(mp.read_bytes()),
        "rule": "legacy directions/contact0/contact6 unchanged in meaning; east/west phase_bridges: on release at walk "
                "frame p play phase_bridges[dir][phase p].bridge s1,s2 then s3 (= exact idle0); s0 is the outgoing walk frame",
        "frame_ms": v4.FRAME_MS, "pivot": [40, 104], "logical_height": 48, "settle_ms_inclusive": 120,
        "directions": trans, "phase_bridges": phase, "phase_bridge_poses_east": info,
        "side_bridge_poses_legacy": ot.get("side_bridge_poses"), "baseline_transition": f"{V08_RUN}/{oname('explore-stop-transition-manifest')}.json",
        "author_tool": tool}, indent=1, default=lambda o: list(o)), encoding="utf-8", newline="\n")
    print(str(tp).replace("\\\\?\\", ""))


if __name__ == "__main__":
    main()
