"""Heroine Sea-of-Stars front/back (south/north) articulated walk + phase-aware stop source v01 (contract cc857a56).
UNAPPROVED, test-only. Writes only outputs/hsea-front17/src-v01-<tag>/. Baseline = stop15 f141d653 (unapproved).

Method change for south/north (old: whole leg row-resampled = leg compression, arms frozen in the torso):
- legs are split at the knee row: the swinging leg foreshortens ONLY the thigh (knee comes toward/away from the camera),
  the shin + boot are the original source pixels moved rigidly up by the lift and 0-2 px toward the body midline;
  bent-knee read: south = knee-cap light row + crease row below it, north = back-of-knee fold row (source trouser
  ramp colours only). Planted leg keeps full source length. Overlap is baked as occlusion: south swinging leg is
  in front of the planted leg, north swinging leg goes behind it (layer order itself unchanged).
- forearms + gloves are cut out of the torso layer (elbow row down, teal scarf excluded) into the existing
  near-arm/far-arm layers and swing counter to the legs: forward = hand rises up to 2 px over the sleeve and 1 px
  toward the midline (foreshortened forearm), back = hand drops 1 px (elbow row stretched by one source row).
  Shoulders/upper sleeves stay with the torso; torso only bobs (v04 BOB), scarf tail sways 1 px late, ponytail
  keeps the v04 one-phase bob lag over the v04 hair/scarf underlay in upper-body (removing it opened a 1 px gap).
- same 80x112, density 2, pivot (40,104), 12 phases, BOB, cadence; idle bytes, palette, face and scale unchanged.
Phase bridges for south/north: s0 = exact new walk[p], s1 k=0.4, s2 k=0.8 (all pose parameters released toward
rest with the same method), s3 = exact original idle0. Legacy contact bridges: b0 = phase c s1, b1 = phase c s2,
final = exact idle0. East/west (24 walk, 96 phase, 8 legacy) and all 4 idle PNGs are copied byte-identically.
Usage: python -I <this> [--out-tag YYYYMMDD-HHMMSS]      (author; refuses an existing run directory)
       python -I <this> --verify <run-dir>               (rebuild in memory with the run's tag, compare every byte)
"""
import importlib.util, json, sys, datetime, math, io, zipfile
from pathlib import Path
import numpy as np
from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
V15 = "tools/rpg-2-star-ocean-the-second_heroine-sea-explore_phase-stop-author_test-only-v01_20261021-014500-c5e17a29.py"
BASE_RUN = "outputs/hsea-stop15/src-v01-20261021-015000"
BASE_TAG, BASE_UID = "20261021-015000", "f141d653"
_s = importlib.util.spec_from_file_location("v15", ROOT / V15); v15 = importlib.util.module_from_spec(_s); _s.loader.exec_module(v15)
v8, v4, v3 = v15.v8, v15.v4, v15.v3
W, H, SOLE, N = v3.W, v3.H, v3.SOLE, 12
PRE = "rpg-2-star-ocean-the-second_heroine-sea"
K = (0.0, 0.4, 0.8, 1.0)
ORDER = ["under-trouser-paint", "far-leg", "near-leg", "upper-body", "far-arm", "near-arm", "hair-scarf-follow"]
LIFT = [0, 0, 0, 0, 0, 1, 2, 4, 5, 4, 2, 1]      # near-leg thigh foreshortening px (far leg = LIFT[p+6]); p8 passing
# per direction: v04 build_dir args, knee row, forearm boxes (x0, x1, elbow_y, bottom_y) for image-left / image-right
SPEC = {"south": {"args": ("front", 68, 41, 14, (27, 55), 12), "knee": 80, "toward_camera": True,
                  "arm_left": (22, 32, 57, 68), "arm_right": (52, 62, 57, 70)},
        "north": {"args": ("front", 71, 41, 14, (29, 52), 3), "knee": 83, "toward_camera": False,
                  "arm_left": (20, 29, 59, 71), "arm_right": (51, 58, 62, 73)}}


def lum(c): return 0.299 * c[0] + 0.587 * c[1] + 0.114 * c[2]


def trouser_ramp(leg, y0, y1):
    px = leg[y0:y1][leg[y0:y1, :, 3] > 0][:, :3].astype(int)
    vals, cnt = np.unique(px, axis=0, return_counts=True)
    blue = sorted([tuple(int(x) for x in v) for v, c in zip(vals, cnt) if v[2] > v[0] and c >= 3], key=lum)
    return blue[1], blue[-1]                     # darkest non-outline, lightest (both existing source colours)


def articulate(seg, hip, knee, lift, inward, accent, ramp):
    """Thigh rows hip..knee-1 resampled to (knee-hip-lift) rows; shin+boot rows knee..SOLE moved rigidly up by lift
    and `inward` px in x. Returns (layer, new_knee_row)."""
    if lift == 0 and inward == 0:
        return seg.copy(), knee
    out = v3.blank(); nt = knee - hip; nd = nt - lift
    for i in range(nd):
        out[hip + i] = seg[hip + min(nt - 1, int(round(i * (nt - 1) / max(1, nd - 1))))]
    lower = np.roll(seg[knee:SOLE + 1], inward, 1)
    yk = knee - lift
    m = lower[..., 3] > 0; tgt = out[yk:yk + len(lower)]; tgt[m] = lower[m]
    if lift >= 2:                                # bent-knee read on interior pixels only (outline kept)
        dark, light = ramp
        rows = [(yk, light), (yk + 1, dark)] if accent == "cap" else [(yk, dark)]
        for y, col in rows:
            xs = np.nonzero(out[y, :, 3] > 0)[0]
            for x in xs[1:-1]: out[y, x, :3] = col
    return out, yk


def build_front(d, base):
    sp = SPEC[d]; hip = sp["args"][1]; knee = sp["knee"]
    f, _, _, order, _ = v4.build_dir(base, *sp["args"]); L0 = f[0][1]
    assert list(order) == ORDER
    follow = L0["hair-scarf-follow"]; up = L0["upper-body"].copy()     # v04 underlay kept: no gap when follow lags
    teal = v4.is_teal(base); arms = {}
    for side in ("left", "right"):
        x0, x1, ey, by = sp["arm_" + side]
        m = np.zeros((H, W), bool); m[ey:by + 1, x0:x1 + 1] = True; m &= (up[..., 3] > 0) & ~teal
        arms[side] = (np.where(m[..., None], up, 0).astype(np.uint8), ey)
        up[m] = 0
    near_side, far_side = "right", "left"      # near-leg = image-right in both front and back views
    idle = {"under-trouser-paint": L0["under-trouser-paint"], "far-leg": L0["far-leg"], "near-leg": L0["near-leg"],
            "upper-body": up, "far-arm": arms[far_side][0], "near-arm": arms[near_side][0], "hair-scarf-follow": follow}
    assert np.array_equal(v3.compose(idle, ORDER), v3.compose(L0, ORDER))
    ramps = {k: trouser_ramp(L0[k], hip, knee) for k in ("near-leg", "far-leg")}
    accent = "cap" if sp["toward_camera"] else "fold"
    under = L0["under-trouser-paint"]

    def arm(layer_ey, fwd, b, side):
        a, ey = layer_ey
        dy = int(round(-2 * fwd)) if fwd > 0 else int(round(-fwd))
        inward = (1 if side == "left" else -1) * (1 if fwd > 0.6 else 0)
        o = v3.blank()
        src = np.roll(np.roll(a, b, 0), inward, 1)
        if dy <= 0:
            o[:H + dy] = src[-dy:] if dy else src
        else:                                   # hand drops: stretch the elbow row by dy source rows
            o[dy:] = src[:H - dy]
            top = src[ey + b]
            for r in range(dy): o[ey + b + r][top[:, 3] > 0] = top[top[:, 3] > 0]
        return o, dy, inward

    def pose(p, k):
        r = 1.0 - k
        ln, lf = int(round(LIFT[p] * r)), int(round(LIFT[(p + 6) % N] * r))
        b, blag = int(round(v4.BOB[p] * r)), int(round(v4.BOB[(p - 1) % N] * r))
        sw = int(round(-math.sin(2 * math.pi * (p - 1.5) / N) * r))
        fwd_near = math.cos(2 * math.pi * p / N) * r      # near leg forward at p0 contact, back at p6
        L = {"under-trouser-paint": np.roll(under, b, 0) if b >= 0 else under.copy(), "upper-body": np.roll(up, b, 0),
             "hair-scarf-follow": v8.sway(np.roll(follow, blag, 0), sw)}
        nin, fin = -int(round(ln / 2.5)), int(round(lf / 2.5))
        L["near-leg"], nk = articulate(idle["near-leg"], hip, knee, ln, nin, accent, ramps["near-leg"])
        L["far-leg"], fk = articulate(idle["far-leg"], hip, knee, lf, fin, accent, ramps["far-leg"])
        if b < 0:                                           # v04 rule: torso up 1 px -> extend leg tops by one row
            for key in ("near-leg", "far-leg"):
                lg = L[key]; tp = lg[hip]; gap = (lg[hip - 1, :, 3] == 0) & (tp[:, 3] > 0); lg[hip - 1][gap] = tp[gap]
        # baked overlap: south swinging far leg in front of planted near leg; north swinging near leg behind far leg
        occl = 0
        if (sp["toward_camera"] and lf > ln) or (not sp["toward_camera"] and ln > lf):
            m = (L["far-leg"][..., 3] > 0) & (L["near-leg"][..., 3] > 0); occl = int(m.sum()); L["near-leg"][m] = 0
        # arms counter the legs: the arm on the far-leg side swings forward with the near leg
        L["far-arm"], fdy, fdx = arm(arms[far_side], fwd_near, b, far_side)
        L["near-arm"], ndy, ndx = arm(arms[near_side], -fwd_near, b, near_side)
        for kk in L: L[kk][SOLE + 1:] = 0
        info = {"k": k, "bob": b, "scarf_dx": sw, "near_lift": ln, "far_lift": lf, "near_knee_row": nk, "far_knee_row": fk,
                "near_shin_dx": nin, "far_shin_dx": fin, "near_occluded_px": occl, "far_arm_fwd": round(fwd_near, 3),
                "far_hand_dy_dx": [fdy, fdx], "near_hand_dy_dx": [ndy, ndx]}
        return v3.compose(L, ORDER), L, info
    a1, L1, _ = pose(0, 1.0)
    assert np.array_equal(a1, v3.compose(idle, ORDER)), d     # fully released pose == exact idle0
    return pose, idle


def decode_pxo(b, order):
    z = zipfile.ZipFile(io.BytesIO(b)); data = json.loads(z.read("data.json"))
    assert [l["name"] for l in data["layers"]] == list(order) and data["size_x"] == W and data["size_y"] == H
    out = []
    for fi in range(1, len(data["frames"]) + 1):
        lay = {n: np.frombuffer(z.read(f"image_data/frames/{fi}/layer_{li}"), np.uint8).reshape(H, W, 4)
               for li, n in enumerate(order, start=1)}
        out.append(v3.compose(lay, order))
    return out


def build(tag):
    uid = v3.sha(("hsea-front17-v01" + tag).encode())[:8]
    base = ROOT / BASE_RUN
    oname = lambda s, ext: f"{PRE}_{s}_unapproved-stop15-v01_{BASE_TAG}-{BASE_UID}.{ext}"
    nname = lambda s, ext: f"{PRE}_{s}_unapproved-front17-v01_{tag}-{uid}.{ext}"
    om = json.loads((v15.xp(base) / oname("explore-source-set", "json")).read_text(encoding="utf-8"))
    ot = json.loads((v15.xp(base) / oname("explore-stop-transition-manifest", "json")).read_text(encoding="utf-8"))
    rd = lambda f: (v15.xp(base) / f).read_bytes()
    dec = lambda b: np.array(Image.open(io.BytesIO(b)).convert("RGBA"))
    files, prov, checks = {}, [], []
    raw = (ROOT / v3.SOUTH).read_bytes(); assert v3.sha(raw) == v3.SOUTH_SHA
    south = dec(raw); pal = v3.palette_of(south)
    bases = {"south": south, "north": v3.adapt(v3.GEN["north"], pal)[0]}
    fronts = {}
    for d in ("south", "north"):
        pose, idle = build_front(d, bases[d])
        ib = rd(om["actions"]["idle"][d][0]["file"])
        assert np.array_equal(dec(ib), v3.compose(idle, ORDER)), d       # layers reproduce the protected idle exactly
        fronts[d] = (pose, idle, ib)
    assert rd(om["actions"]["idle"]["south"][0]["file"]) == raw
    checks.append("south/north idle layers compose to the protected stop15 idle bytes; south idle == approved 6bf1d688")
    actions = {"idle": {}, "walk": {}}; walk_L = {}; poses_info = {}
    for act in ("idle", "walk"):
        for d, fr in om["actions"][act].items():
            actions[act][d] = []
            for i, f in enumerate(fr):
                fn = nname(f"explore-{d}-{act}-f{i:02d}", "png")
                if d in fronts and act == "walk":
                    arr, L, inf = fronts[d][0](i, 0.0); b = v3.png(arr); walk_L.setdefault(d, []).append(L)
                    poses_info.setdefault(d, {})[f"walk{i:02d}"] = inf
                    prov.append({"file": fn, "authored": "front/back articulated method", "replaces": f"{BASE_RUN}/{f['file']}", "sha256": v3.sha(b)})
                else:
                    b = rd(f["file"]); prov.append({"file": fn, "copied_from": f"{BASE_RUN}/{f['file']}", "sha256": v3.sha(b)})
                files[fn] = b; actions[act][d].append({"file": fn, "duration_ms": f["duration_ms"]})
    # phase bridges: side copied byte-identically, front/back authored
    phase, ph_info, ph_frames = {}, {}, {}
    for d in ("south", "west", "north", "east"):
        phase[d] = {}
        for p in range(N):
            lst = []
            for si in range(4):
                fn = nname(f"explore-{d}-phstop-p{p:02d}-s{si}", "png")
                if d in ("east", "west"):
                    of = ot["phase_bridges"][d][f"phase{p}"]["bridge"][si]
                    b = rd(of["file"]); assert v3.sha(b) == of["sha256"]
                    prov.append({"file": fn, "copied_from": f"{BASE_RUN}/{of['file']}", "sha256": v3.sha(b)})
                else:
                    pose, idle, ib = fronts[d]
                    if si == 0: b = files[actions["walk"][d][p]["file"]]; L = walk_L[d][p]; inf = {"k": 0.0, "exact": f"walk f{p:02d}"}
                    elif si == 3: b = ib; L = idle; inf = {"k": 1.0, "exact": "idle f00"}
                    else: arr, L, inf = pose(p, K[si]); b = v3.png(arr)
                    assert np.array_equal(dec(b), v3.compose(L, ORDER)), (d, p, si)
                    ph_frames.setdefault(d, []).append(L); ph_info.setdefault(d, {}).setdefault(f"phase{p}", []).append(inf)
                files[fn] = b; lst.append({"file": fn, "sha256": v3.sha(b)})
            phase[d][f"phase{p}"] = {"from_walk_frame": p, "bridge": lst}
    trans = {}
    for d, cs in ot["directions"].items():
        trans[d] = {}
        for c, e in cs.items():
            lst = []; wf = e["from_walk_frame"]
            for k, bf in enumerate(e["bridge"]):
                fn = nname(f"explore-{d}-stop-c{wf:02d}-b{k}", "png")
                if d in ("east", "west"):
                    b = rd(bf["file"]); assert v3.sha(b) == bf["sha256"]
                    prov.append({"file": fn, "copied_from": f"{BASE_RUN}/{bf['file']}", "sha256": v3.sha(b)})
                else:
                    b = files[phase[d][f"phase{wf}"]["bridge"][k + 1]["file"]]
                    prov.append({"file": fn, "equals": phase[d][f"phase{wf}"]["bridge"][k + 1]["file"], "sha256": v3.sha(b)})
                files[fn] = b; lst.append({"file": fn, "sha256": v3.sha(b)})
            trans[d][c] = {"from_walk_frame": wf, "bridge": lst, "final": actions["idle"][d][0]["file"]}
    # native sources
    spec = importlib.util.spec_from_file_location("pxo_writer", ROOT / v3.WRITER)
    wr = importlib.util.module_from_spec(spec); spec.loader.exec_module(wr)
    wr.W, wr.H = W, H; wr.to_rgba = lambda a: np.ascontiguousarray(a, np.uint8)
    src = []
    for d in ("south", "north"):
        pose, idle, ib = fronts[d]
        for kind, per, durs, fo, names in (
                ("layers", [idle] + walk_L[d], [v4.IDLE_MS / 1000] + [v4.FRAME_MS / 1000] * N, "idle f00, walk f00-f11",
                 [actions["idle"][d][0]["file"]] + [w["file"] for w in actions["walk"][d]]),
                ("phstop-layers", ph_frames[d], [v4.FRAME_MS / 1000] * 48, "phase p00..p11 x sample s0..s3 (frame = 4*p + s)",
                 [s["file"] for p in range(N) for s in phase[d][f"phase{p}"]["bridge"]])):
            per = [{k: L[k] for k in ORDER} for L in per]
            fn = nname(f"explore-{d}-{kind}", "pxo")
            b = wr.make_pxo(per, durs, v3.png(v3.compose(per[0], ORDER)), fn[:-4] + ".png", 16, order=ORDER, dt=v3.DT)
            comp = decode_pxo(b, ORDER)
            for i, nm in enumerate(names): assert np.array_equal(comp[i], dec(files[nm])), (fn, i)
            files[fn] = b
            src.append({"direction": d, "file": fn, "format": "pixelorama-pxo", "sha256": v3.sha(b), "frame_order": fo,
                        "frames": len(per), "frame_files": names, "layers_bottom_to_top": ORDER})
    for s in om["source_files"]:                 # side phase PXOs reused byte-identically
        b = rd(s["file"]); assert v3.sha(b) == s["sha256"]
        fn = nname(f"explore-{s['direction']}-phstop-layers", "pxo"); files[fn] = b
        src.append({**s, "file": fn, "copied_from": f"{BASE_RUN}/{s['file']}",
                    "frame_files": [x["file"] for p in range(N) for x in phase[s["direction"]][f"phase{p}"]["bridge"]]})
    checks.append("every authored PNG decodes equal to its layer composite; every PXO frame decodes equal to its mapped PNG")
    tool = {"file": "tools/" + Path(__file__).name, "sha256TextLf": v3.sha(Path(__file__).read_bytes().replace(b"\r\n", b"\n"))}
    side_orig = [s for s in om["original_source_files"] if s["direction"] in ("east", "west")]
    man = dict(om)
    man.update({"actions": actions, "source_files": src,
        "original_source_files": side_orig + [{**s, "status": "superseded for south/north walk by front17 (read-only, not used)"}
                                              for s in om["original_source_files"] if s["direction"] in ("south", "north")],
        "status": "UNAPPROVED test-only; south/north walk + phase bridges authored with articulated front/back method; "
                  "all idle, east/west walk/phase/legacy bytes copied unchanged",
        "author_tool": tool, "copied_png_provenance": prov, "baseline": f"{BASE_RUN}/{oname('explore-source-set', 'json')}",
        "reused_v15_module": {"file": V15, "sha256TextLf": v3.sha((ROOT / V15).read_bytes().replace(b"\r\n", b"\n"))},
        "front_back_method": {"lift_plan_near": LIFT, "knee_rows": {d: SPEC[d]["knee"] for d in SPEC},
                              "forearm_boxes": {d: {"left": SPEC[d]["arm_left"], "right": SPEC[d]["arm_right"]} for d in SPEC},
                              "per_pose": poses_info}})
    man["disclosure"] = list(om.get("disclosure", [])) + [
        "south/north: side-view east-west mechanics untouched; front/back legs = thigh-only foreshortening + rigid source shin/boot",
        "front/back forearms are source pixels cut from the torso; upper sleeves stay with the torso (no shoulder rotation)",
        "knee accent rows recolour existing pixels with existing trouser colours; no new colours",
        "legacy south/north contact bridges b0/b1 equal phase-bridge s1/s2 of that contact phase",
        "metrics and byte checks only; no fluidity/visual-quality claim; root judges normal-speed actual game"]
    mj = nname("explore-source-set", "json")
    files[mj] = json.dumps(man, indent=1).encode("utf-8")
    tj = nname("explore-stop-transition-manifest", "json")
    files[tj] = json.dumps({"schema": "worlds-between.exploration-stop-transition.supplemental.v1",
        "source_manifest": mj, "source_set": mj, "source_set_sha256": v3.sha(files[mj]),
        "rule": "legacy directions/contact0/contact6 unchanged in meaning; phase_bridges for south/west/north/east: on release "
                "at walk frame p play phase_bridges[dir][phase p].bridge s1,s2 then s3 (= exact idle0); s0 is the outgoing walk frame",
        "frame_ms": v4.FRAME_MS, "pivot": [40, 104], "logical_height": 48, "settle_ms_inclusive": 120,
        "directions": trans, "phase_bridges": phase, "phase_bridge_poses_east": ot.get("phase_bridge_poses_east"),
        "phase_bridge_poses_front_back": ph_info, "side_bridge_poses_legacy": ot.get("side_bridge_poses_legacy"),
        "baseline_transition": f"{BASE_RUN}/{oname('explore-stop-transition-manifest', 'json')}", "author_tool": tool,
        "self_checks": checks}, indent=1, default=lambda o: list(o)).encode("utf-8")
    return files, tj


def main():
    if "--verify" in sys.argv:
        run = v15.xp(Path(sys.argv[sys.argv.index("--verify") + 1]).resolve())
        tag = run.name.split("src-v01-")[1]
        files, _ = build(tag)
        on_disk = sorted(p.name for p in run.iterdir() if p.is_file())
        bad = [n for n, b in files.items() if not (run / n).is_file() or (run / n).read_bytes() != b]
        extra = sorted(set(on_disk) - set(files))
        print(f"VERIFY {'PASS' if not bad and not extra else 'FAIL'} rebuilt={len(files)} on_disk={len(on_disk)} mismatched={bad[:5]} extra={extra[:5]}")
        sys.exit(0 if not bad and not extra else 1)
    tag = sys.argv[sys.argv.index("--out-tag") + 1] if "--out-tag" in sys.argv else datetime.datetime.now(datetime.timezone.utc).strftime("%Y%m%d-%H%M%S")
    run = v15.xp(ROOT / "outputs" / "hsea-front17" / f"src-v01-{tag}")
    files, tj = build(tag)
    run.mkdir(parents=True, exist_ok=False)
    for n, b in files.items(): (run / n).write_bytes(b)
    print(f"WROTE {len(files)} files")
    print(str(run / tj).replace("\\\\?\\", ""))


if __name__ == "__main__":
    main()
