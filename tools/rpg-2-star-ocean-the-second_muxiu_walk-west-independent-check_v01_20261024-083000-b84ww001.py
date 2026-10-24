"""Independent checker b84 for Muxiu WEST walk/stop b84ww001 (content.char.muxiu.walk-west). NO author/engine imports.

Minimal extension of the preserved b78ww002 checker for the new scoped paths plus explicit raw-limb and visible
continuity checks and a negative control that must reject the ORIGINAL fragmented far-limb geometry. All original
checks, negative controls and timing/slip thresholds are retained unchanged.

Reads only bytes on disk: source manifest, frame PNGs, animated PXO (data.json + raw cels), ORA, package JSONs and the
pinned Muxiu west neutral/palette. Re-derives (does not trust author metadata): hashes, PXO cel recomposition == every
PNG, frame order/tags, timing boundaries, side-gait contacts from separate raw boot cels (`far-limbs` = complete
authored far limb, `boots` = near boot), 40 ms world-slip residual, 60 fps held-frame excursion, all 12 stop bridges,
exact neutral endpoint, legwrap articulation, bracelet-on-arm and identity anchors.
b84 structural checks: every `far-limbs` cel is one 8-connected opaque mass spanning hip->ankle with no 1-texel
string row and containing trouser + legwrap + boot role colours; visible far-limb colour survives near-leg alpha-over;
the original 2-5 texel split sliver is rejected by the same predicate.
Negative controls (in memory): tampered PNG, tampered PXO cel, malformed stop JSON/timing/direction/missing frame,
bad pivot, slid bridge foot, off-neutral endpoint, unchanged "walk", fragmented original far limb -> each REJECTED.
Native: Pixelorama --headless export of the animated PXO with isolated XDG dirs, 90 s deadline; export equality and
application diagnostics are reported separately; GUI SaveAs/reopen is NOT verified.
Preview: source-bound normal-speed GIF (40 ms frames, host 140 logical px/s translating WEST/screen-left at
11.2 source px per 40 ms, no vertical displacement) - not a Godot capture.

<venv python> -X utf8 -I <this> --out outputs/muxiu-ww84/<new dir>   (PIXELORAMA env = Pixelorama binary)
"""
import argparse, hashlib, io, json, os, re, signal, subprocess, time, zipfile
from pathlib import Path
import numpy as np
from PIL import Image

ROOT = Path(__file__).resolve().parent.parent
TAG = "20261024-083000-b84ww001"
PFX = "rpg-2-star-ocean-the-second_muxiu"
SRC_DIR = "outputs/muxiu-ww84"
PKG_DIR = "game/assets/characters/muxiu-native-v01/west-walk-b84"
MAN = f"{SRC_DIR}/rpg-2-star-ocean-the-second_muxiu_walk-source-manifest_unapproved-b84ww001-v01_20261024-083000-"
_N = "game/assets/characters/muxiu-native-v01/west"
NEUTRAL = (f"{_N}/rpg-2-star-ocean-the-second_muxiu_west-static_unapproved-v01_20261024-055724-74e5c117.png",
           "0eb36b3bfed70b1ffcf0a20401e7948e683e317d4ca3db6fa6a4f06e6d2d8ec0")
PALFILE = (f"{_N}/rpg-2-star-ocean-the-second_muxiu_west-palette_unapproved-v01_20261024-055724-adb333d7.json",
           "dd8ff4213df8f14a73842a6142ef82c3a8eb799388b360777b5a561f1ecbd6fc")
LAYERS = ["far-limbs", "boots", "legwraps", "trousers", "shirt", "belt", "pouches", "cloak", "arms", "bracelet", "whistle",
          "face", "hair", "braid", "guides"]
W, H, SOLE, NPH, FMS, HOST = 80, 112, 103, 12, 40, 140.0
V = HOST * FMS / 1000 * 2           # 11.2 source texels per 40 ms at density 2
IDLE_MS = [700, 200, 400, 200]
NFR = 1 + 4 + NPH + 2 * NPH          # 41


def sha(b):
    return hashlib.sha256(b).hexdigest()


def rd(rel):
    return (ROOT / rel).read_bytes()


def dec(b):
    return np.asarray(Image.open(io.BytesIO(b)).convert("RGBA"))


def over(layers):
    o = np.zeros((H, W, 4), np.uint8)
    for a in layers:
        m = a[..., 3] == 255
        o[m] = a[m]
    return o


def th(cel):
    """West faces screen-left: toe = min x, heel = max x on the sole row; None if not grounded."""
    row = cel[SOLE, :, 3] == 255
    xs = np.flatnonzero(row)
    return (int(xs.min()), int(xs.max())) if len(xs) else None


def static_feet_ep(boots):
    """b84 neutral endpoint. The static neutral draws one complete leg silhouette; idle f00 draws a blank
    `far-limbs` cel (the far limb is fully occluded), so both modeled neutral feet share that complete boot extent.
    The old front/back split is retained separately only to build the fragmented-geometry negative control."""
    return boots, boots


def legacy_far_sliver(boots):
    """The original b78ww001 far-boot mask: x<=32 (or x<=35 above row 96) of the single neutral boot. Used ONLY
    as the negative-control fixture that the b84 continuity predicate must reject."""
    ys, xs = np.indices((H, W)); f = 40 - xs
    far_m = (f >= 8) | ((f >= 5) & (ys <= 96))
    far = np.zeros_like(boots)
    m = far_m & (boots[..., 3] == 255)
    far[m] = boots[m]
    return far


def far_limb_errors(a, rgb):
    """b84 raw-limb structural predicate: one continuous clothed boot+wrap+trouser silhouette."""
    m = a[..., 3] == 255
    if not m.any():
        return ["empty far-limbs cel"]
    ys, xs = np.nonzero(m)
    errs = []
    if int(ys.max() - ys.min()) < 18:
        errs.append(f"span {int(ys.max() - ys.min())}<18")
    widths = [int(m[y].sum()) for y in range(int(ys.min()), int(ys.max()) + 1)]
    if min(widths) < 2:
        errs.append("1-texel string row")
    if max(widths) < 8:
        errs.append("max row width <8")
    seen = np.zeros_like(m)
    stack = [(int(ys[0]), int(xs[0]))]
    while stack:
        y, x = stack.pop()
        if not (0 <= y < H and 0 <= x < W) or seen[y, x] or not m[y, x]:
            continue
        seen[y, x] = True
        for dy in (-1, 0, 1):
            for dx in (-1, 0, 1):
                if dy or dx:
                    stack.append((y + dy, x + dx))
    if not np.array_equal(seen, m):
        errs.append("disconnected fragments")
    fam = set()
    for y, x in zip(*np.nonzero(m)):
        c = tuple(int(v) for v in a[y, x, :3])
        for k_, S in (("trouser", {rgb[k] for k in ("t1", "t2", "t3", "t4")}),
                      ("legwrap", {rgb[k] for k in ("w1", "w2", "w3", "w4", "c2", "c3", "c4", "q1", "q2")}),
                      ("boot", {rgb[k] for k in ("r1", "r2", "r3", "r4", "k1")})):
            if c in S:
                fam.add(k_)
    if fam != {"trouser", "legwrap", "boot"}:
        errs.append("missing clothed roles: " + ",".join(sorted({"trouser", "legwrap", "boot"} - fam)))
    return errs


def pxo_frames(pxo):
    z = zipfile.ZipFile(io.BytesIO(pxo))
    dj = json.loads(z.read("data.json"))
    names = [l["name"] for l in dj["layers"]]
    n = len(dj["frames"])
    cel = lambda f, li: np.frombuffer(z.read(f"image_data/frames/{f + 1}/layer_{li + 1}"), np.uint8).reshape(H, W, 4)
    comps = [over([cel(f, li) for li, nm in enumerate(names) if nm != "guides"]) for f in range(n)]
    roles = {nm: [cel(f, names.index(nm)) for f in range(n)] for nm in ("far-limbs", "boots", "legwraps", "arms", "bracelet") if nm in names}
    return dj, names, comps, roles


# ----------------------------------------------------------------------------- pure validators (reused by controls)
def v_stop(stop, png_names):
    errs = []
    if stop.get("frame_ms") != FMS or stop.get("settle_ms_inclusive") != 3 * FMS or stop.get("runtime_default") is not False:
        errs.append("stop timing/default fields")
    if stop.get("pivot") != [40, 104] or stop.get("logical_height") != 48:
        errs.append("stop pivot/height")
    pb = stop.get("phase_bridges", {})
    if list(pb) != ["west"] or sorted(pb["west"]) != sorted(f"phase{p}" for p in range(NPH)):
        errs.append("stop phases/direction scope")
    else:
        for p in range(NPH):
            s = pb["west"][f"phase{p}"]
            if len(s) != 4 or s[0] != {"ref": "walk", "index": p, "k": 0.0} or s[-1] != {"ref": "idle", "index": 0, "k": 1.0}:
                errs.append(f"bridge phase{p} endpoints")
            elif any(x.get("file", "").rsplit("/", 1)[-1] not in png_names for x in s[1:3]):
                errs.append(f"bridge phase{p} frame file")
    return errs


def v_timing(ss):
    errs = []
    idle = [f["duration_ms"] for f in ss["actions"]["idle"]["west"]]
    walk = [f["duration_ms"] for f in ss["actions"]["walk"]["west"]]
    if idle != IDLE_MS:
        errs.append(f"idle durations {idle}")
    if walk != [FMS] * NPH:
        errs.append(f"walk durations {walk}")
    if not all(isinstance(x, int) and x > 0 for x in idle + walk):
        errs.append("non-positive duration")
    if set(ss["actions"]["idle"]) != {"west"} or set(ss["actions"]["walk"]) != {"west"}:
        errs.append("direction scope")
    if ss.get("pivot") != [40, 104] or ss.get("frame_size") != [W, H] or ss.get("density") != 2:
        errs.append("contract")
    return errs


def v_articulated(walk_imgs, neutral):
    low = [im[69:104].tobytes() for im in walk_imgs]
    return {"phases_equal_neutral_lower": sum(1 for x in low if x == neutral[69:104].tobytes()), "distinct_lower": len(set(low))}


def frame_at(durs, t):
    t %= sum(durs)
    acc = 0
    for i, d in enumerate(durs):
        if t < acc + d:
            return i
        acc += d


def world_slip(a, b):
    """a,b = (toe,heel) of the same foot on consecutive held phases. West forward is -x; host advances +V src."""
    return max(abs(-(b[0] - a[0]) + V), abs(-(b[1] - a[1]) + V))


def v_contacts(near, far, stop_near, stop_far, ep_near, ep_far):
    """near/far: per-phase (toe,heel)|None for the 12 walk phases; stop_*: per phase [s1,s2] tuples;
    ep_*: neutral endpoint feet derived independently from the static boot cel."""
    rec = [{"A": near[p], "B": far[p]} for p in range(NPH)]
    pairs = []
    for p in range(NPH):
        n = (p + 1) % NPH
        for k in ("A", "B"):
            if rec[p][k] and rec[n][k]:
                pairs.append({"from": p, "foot": k, "world_slip_src": round(world_slip(rec[p][k], rec[n][k]), 3)})
    # 60 fps samples over two cycles: frame = floor(t/40 ms), host continuous at 280 source px/s
    saw = 0.0
    for k in ("A", "B"):
        run, best = [], 0.0
        for i in range(int(2 * NPH * FMS * 60 / 1000)):
            t = i / 60.0
            fi = int(t * 1000 // FMS)
            r = rec[fi % NPH][k]
            if r:
                run.append((40 - r[0]) + 2 * HOST * t)
            else:
                if len(run) > 1:
                    best = max(best, max(run) - min(run))
                run = []
        saw = max(saw, best)
    stop_slip, endpoint = [], []
    for p in range(NPH):
        seq = [(near[p], far[p])] + list(zip(stop_near[p], stop_far[p])) + [(ep_near, ep_far)]
        for a, b in zip(seq, seq[1:]):
            for k in range(2):
                if a[k] and b[k]:
                    stop_slip.append(max(abs(a[k][0] - b[k][0]), abs(a[k][1] - b[k][1])))
        endpoint.append(seq[-1] == (ep_near, ep_far))
    grounded = [sum(1 for r in rec if r[k]) for k in ("A", "B")]
    return {"grounded_phases_per_foot": grounded,
            "flight_phases": [p for p in range(NPH) if not rec[p]["A"] and not rec[p]["B"]],
            "double_support_phases": [p for p in range(NPH) if rec[p]["A"] and rec[p]["B"]],
            "grounded_pairs": len(pairs), "world_slip_src_max_at_40ms": max(x["world_slip_src"] for x in pairs) if pairs else None,
            "walk_planted_foot_world_excursion_src_60fps": round(saw, 3),
            "walk_planted_foot_world_excursion_logical_60fps": round(saw / 2, 3),
            "stop_bridge_grounded_slip_src_max": max(stop_slip) if stop_slip else 0,
            "stop_entry_phases_checked": NPH, "stop_endpoint_neutral_all": all(endpoint),
            "frame_hold_assumption": "each walk phase held 40 ms; host root moves continuously at 140 logical px/s; "
                                     "between held frames a planted foot sweeps the 60 fps excursion (not footlock)"}


# ----------------------------------------------------------------------------- main
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    ap.add_argument("--skip-native", action="store_true")
    a = ap.parse_args()
    OUT = ROOT / a.out
    OUT.mkdir(parents=True, exist_ok=False)
    checks = []

    def ck(name, ok, detail=None):
        checks.append({"check": name, "pass": bool(ok), "detail": detail})
        print(("PASS " if ok else "FAIL ") + name, "" if detail is None else json.dumps(detail)[:200], flush=True)

    mans = sorted((ROOT / SRC_DIR).glob(Path(MAN).name + "*.json"))
    ck("exactly one source manifest", len(mans) == 1, [m.name for m in mans])
    mrel = mans[0].relative_to(ROOT).as_posix()
    mraw = rd(mrel)
    m = json.loads(mraw)
    e = m["directions"]["west"]
    ck("manifest scope: west only, task content.char.muxiu.walk-west, UNAPPROVED", list(m["directions"]) == ["west"]
       and m["task_ids"] == ["content.char.muxiu.walk-west"] and "UNAPPROVED" in m["status"])
    south_dep = m.get("dependency", {}).get("content.char.muxiu.walk-south", "")
    ck("manifest dependency: canonical south TODO, not a west dependency, no completion claim",
       "TODO" in south_dep and "NOT a west dependency" in south_dep and "prior batch, done" not in south_dep, south_dep)
    ck("neutral Muxiu west PNG pin", sha(rd(NEUTRAL[0])) == NEUTRAL[1])
    ck("palette file pin", sha(rd(PALFILE[0])) == PALFILE[1])
    hexes = json.loads(rd(PALFILE[0]))["colors"]
    rgb = {k: tuple(int(v[i:i + 2], 16) for i in (0, 2, 4)) for k, v in hexes.items()}
    pal = set(rgb.values())
    pins = m["source_inputs"]["neutral_editables_pinned"]
    ck("neutral editable pins byte-exact", all(sha(rd(r)) == h for r, h in pins.items()) and len(pins) == 4, len(pins))
    for key in ("reused_engine", "reused_helpers", "tool"):
        f = m[key]["file"]
        ck(f"{key} text_lf_v1 hash matches tool file", sha(rd(f).replace(b"\r\n", b"\n").replace(b"\r", b"\n")) == m[key]["sha256_text_lf_v1"], f)
    stop_frames = [s for p in range(NPH) for s in e["stop_bridges"][f"phase{p}"] if "file" in s]
    order = [e["static"]] + e["idle"] + e["walk"] + stop_frames
    ok_hash = all(sha(rd(x["file"])) == x["sha256"] for x in order)
    ck(f"all {NFR} frame PNG raw hashes match manifest", ok_hash and len(order) == NFR, len(order))
    imgs = [dec(rd(x["file"])) for x in order]
    bad = [i for i, im in enumerate(imgs) if im.shape != (H, W, 4) or set(np.unique(im[..., 3])) - {0, 255}
           or im[0, :, 3].any() or im[-1, :, 3].any() or im[:, 0, 3].any() or im[:, -1, 3].any()
           or {tuple(c) for c in im[im[..., 3] == 255][:, :3]} - pal]
    ck("frames 80x112, binary alpha, clear border, palette subset of pinned Muxiu palette", not bad, bad[:5])
    ck("static and idle f00 are the neutral bytes", rd(order[0]["file"]) == rd(NEUTRAL[0]) == rd(order[1]["file"]))
    art = v_articulated(imgs[5:17], imgs[0])
    ck("articulated walk: no phase equals neutral below hip, >=8 distinct lower-body states", art["phases_equal_neutral_lower"] == 0
       and art["distinct_lower"] >= 8, art)
    pxo = rd(e["pxo"]["file"])
    ck("PXO raw hash", sha(pxo) == e["pxo"]["sha256"])
    dj, names, comps, roles = pxo_frames(pxo)
    ck(f"PXO {NFR} frames, layers far-limbs + 13 Muxiu roles + guides", len(comps) == NFR and names == LAYERS, names)
    mism = [i for i in range(min(NFR, len(comps))) if not np.array_equal(comps[i], imgs[i])]
    ck("PXO cels recompose to every frame PNG (independent alpha-over)", not mism, mism[:5])
    tags = {t["name"]: (t["from"], t["to"]) for t in dj.get("tags", [])}
    ck("PXO tags west-idle 2-5, west-walk 6-17, 12 stop tags", tags.get("west-idle") == (2, 5) and tags.get("west-walk") == (6, 17)
       and all(tags.get(f"west-stop-p{p:02d}") == (18 + 2 * p, 19 + 2 * p) for p in range(NPH)), tags.get("west-walk"))
    pkg = m["package"]
    ck("package paths under the assigned west-walk root", all(pkg[k].startswith(PKG_DIR + "/") for k in ("sprite_set", "registry", "stop_supplemental")))
    ssb = rd(pkg["sprite_set"])
    ck("sprite set raw hash", sha(ssb) == pkg["sprite_set_sha256"])
    ss = json.loads(ssb)
    te = v_timing(ss)
    ck("sprite set timing/contract/west-only", not te, te)
    stb = rd(pkg["stop_supplemental"])
    ck("stop supplemental text_lf_v1 hash", sha(stb.replace(b"\r\n", b"\n")) == pkg["stop_supplemental_sha256_text_lf_v1"])
    stop = json.loads(stb)
    png_names = {p.name for p in (ROOT / PKG_DIR / "png").glob("*.png")}
    se = v_stop(stop, png_names)
    ck("stop supplemental structure (12 phase bridges [walk p, s1, s2, idle f00], 40 ms, settle 120 inclusive, non-default)", not se, se)
    copies = [f["file"] for act in ss["actions"].values() for f in act["west"]] + \
             ["png/" + s["file"].rsplit("/", 1)[-1] for v in stop["phase_bridges"]["west"].values() for s in v if "file" in s]
    ck("package PNG copies byte-equal to source frames", all(rd(f"{PKG_DIR}/{c}") == rd(f"{SRC_DIR}/{c}") for c in copies), len(copies))
    walk_d = [f["duration_ms"] for f in ss["actions"]["walk"]["west"]]
    bnd = {t: frame_at(walk_d, t) for t in (0, 39, 40, 439, 440, 479, 480, 481)}
    ck("walk timing boundaries: 39->p0 40->p1 479->p11 480->p0 (cycle 480 ms)",
       bnd == {0: 0, 39: 0, 40: 1, 439: 10, 440: 11, 479: 11, 480: 0, 481: 0}, bnd)
    idle_b = {t: frame_at(IDLE_MS, t) for t in (699, 700, 899, 900, 1299, 1300, 1499, 1500)}
    ck("idle timing boundaries (700/200/400/200, loop 1500 ms)", idle_b == {699: 0, 700: 1, 899: 1, 900: 2, 1299: 2, 1300: 3, 1499: 3, 1500: 0}, idle_b)
    seq_t = lambda t: min(int(t // FMS), 3)
    sb = {t: seq_t(t) for t in (0, 39, 40, 79, 80, 119, 120, 1000)}
    ck("stop bridge boundaries: release t0 walk p; 40 s1; 80 s2; 120 (inclusive) idle f00 held",
       sb == {0: 0, 39: 0, 40: 1, 79: 1, 80: 2, 119: 2, 120: 3, 1000: 3}, sb)
    # contacts: near boot = boots cel, authored far boot = far-limbs cel
    near_all = [th(x) for x in roles["boots"]]
    far_all = [th(x) for x in roles["far-limbs"]]
    near_w, far_w = near_all[5:17], far_all[5:17]
    stop_near = [[near_all[17 + 2 * p], near_all[18 + 2 * p]] for p in range(NPH)]
    stop_far = [[far_all[17 + 2 * p], far_all[18 + 2 * p]] for p in range(NPH)]
    ep_near, ep_far = static_feet_ep(roles["boots"][0])
    c = v_contacts(near_w, far_w, stop_near, stop_far, th(ep_near), th(ep_far))
    ck("each foot grounded exactly 4 of 12 phases", c["grounded_phases_per_foot"] == [4, 4], c["grounded_phases_per_foot"])
    ck("side world slip at 40 ms boundaries is integer rounding <=1 src texel", c["world_slip_src_max_at_40ms"] <= 1.0, c["world_slip_src_max_at_40ms"])
    ck("stop bridges (all 12 entry phases): grounded foot never moves (host stopped)", c["stop_bridge_grounded_slip_src_max"] == 0, c["stop_bridge_grounded_slip_src_max"])
    ck("all 12 stop bridges terminate in exact neutral feet + neutral PNG (idle f00)", c["stop_endpoint_neutral_all"]
       and all(stop["phase_bridges"]["west"][f"phase{p}"][-1] == {"ref": "idle", "index": 0, "k": 1.0} for p in range(NPH))
       and rd(order[1]["file"]) == rd(NEUTRAL[0]))
    claimed = m["contact_check"]["west"]
    ck("independent contacts agree with author claims (world slip, flight phases, 60fps excursion, stop 0)",
       claimed["walk_max_world_slip_src_at_40ms_boundaries"] == c["world_slip_src_max_at_40ms"]
       and claimed["flight_phases"] == c["flight_phases"]
       and claimed["walk_planted_foot_world_excursion_src_60fps_samples"] == c["walk_planted_foot_world_excursion_src_60fps"]
       and claimed["stop_bridge_grounded_slip_src_max"] == c["stop_bridge_grounded_slip_src_max"], c["flight_phases"])
    # legwrap articulation exists and stays inside the floor (independent, weaker than per-column author check)
    lw = roles["legwraps"]
    ck("legwraps articulate across the cycle (>=8 distinct states, no alpha below sole)",
       len({x.tobytes() for x in lw[5:17]}) >= 8 and all(not x[SOLE + 1:, :, 3].any() for x in lw))
    # b84 structural far limb: raw cel continuity (independent of author metadata) for every walk + stop frame
    far_cels = roles["far-limbs"]
    raw_bad = [(i, far_limb_errors(cel, rgb)) for i, cel in enumerate(far_cels) if i >= 5 and far_limb_errors(cel, rgb)]
    ck("b84 raw far limb: every walk/stop PXO far-limbs cel is ONE 8-connected clothed boot+wrap+trouser mass "
       "(span>=18 rows, no 1-texel string row, all three leg roles present)", not raw_bad, raw_bad[:5])
    # visible continuity: far-limb texels actually survive alpha-over of the near/torso/cloak layers
    vis_bad, vis_min = [], 10 ** 9
    for i in range(5, NFR):
        cel = far_cels[i]
        m = cel[..., 3] == 255
        vis = m & (comps[i][..., 3] == 255) & np.all(comps[i][..., :3] == cel[..., :3], axis=2)
        ys, xs = np.nonzero(vis)
        vis_min = min(vis_min, len(ys))
        if not len(ys):
            vis_bad.append((i, "fully occluded"))
        elif int(ys.max() - ys.min()) < 6:
            vis_bad.append((i, f"visible span {int(ys.max() - ys.min())}<6"))
    ck("b84 visible far limb: in all 36 walk/stop composed frames the far leg remains visibly exposed "
       "(non-zero, vertical span>=6) rather than collapsing behind the near leg", not vis_bad,
       {"bad": vis_bad[:5], "min_visible_texels": vis_min})
    br, ar = roles["bracelet"], roles["arms"]
    off = {int(np.flatnonzero(br[i][..., 3].any(1)).min() - np.flatnonzero(ar[i][..., 3].any(1)).min()) for i in range(NFR)}
    ck("bracelet stays on the near arm (constant offset in all 41 frames)", off == {10}, sorted(off))
    hair_c, rope_c, wood_c = {rgb[k] for k in ("h1", "h2", "h3")}, {rgb["q1"], rgb["q2"]}, {rgb["x1"], rgb["x2"]}

    def reg(im, y0, y1, x0, x1):
        s = im[y0:y1, x0:x1]
        return {tuple(v) for v in s[s[..., 3] == 255][:, :3]}
    idm = [i for i, im in enumerate(imgs) if not (hair_c & reg(im, 33, 70, 28, 38) and rope_c & reg(im, 65, 74, 33, 46)
                                                  and wood_c & reg(im, 37, 47, 32, 41) and {rgb["c1"], rgb["c2"]} <= reg(im, 28, 63, 31, 56)
                                                  and rgb["y1"] in reg(im, 28, 70, 31, 52))]
    ck("identity: braid (front/left), rope bracelet (near wrist), wooden whistle, moss cloak + brass clasp in all frames", not idm, idm[:5])
    ck("top row never above neutral row 8; soles never below 103",
       all(np.flatnonzero(im[..., 3].any(1)).min() >= 8 and np.flatnonzero(im[..., 3].any(1)).max() <= SOLE for im in imgs))
    ck("west art is not a horizontal mirror of any frame (authored profile, independent of east)",
       all(not np.array_equal(im, im[:, ::-1]) for im in imgs))

    # ------------------------------------------------------------------ negative controls (must be rejected)
    neg = []

    def nc(name, rejected):
        neg.append({"control": name, "rejected": bool(rejected)})
        print(("REJECTED " if rejected else "NOT-REJECTED ") + name, flush=True)

    t = bytearray(rd(order[8]["file"])); t[-20] ^= 1
    nc("tampered walk PNG byte -> hash mismatch", sha(bytes(t)) != order[8]["sha256"])
    zin = zipfile.ZipFile(io.BytesIO(pxo)); zb = io.BytesIO()
    with zipfile.ZipFile(zb, "w") as zo:
        for info in zin.infolist():
            d = zin.read(info.filename)
            if info.filename == "image_data/frames/9/layer_2":
                arr = np.frombuffer(d, np.uint8).reshape(H, W, 4).copy(); arr[SOLE, 30] = [255, 0, 0, 255]; d = arr.tobytes()
            zo.writestr(info, d)
    _, _, tcomps, _ = pxo_frames(zb.getvalue())
    nc("tampered PXO cel -> recomposition mismatch", not np.array_equal(tcomps[8], imgs[8]))
    bs = json.loads(stb); bs["phase_bridges"]["west"]["phase3"][-1] = {"ref": "idle", "index": 1, "k": 1.0}
    nc("malformed stop JSON (bridge ends on idle f01) -> rejected", bool(v_stop(bs, png_names)))
    bs = json.loads(stb); bs["frame_ms"] = 39
    nc("stop frame_ms 39 -> rejected", bool(v_stop(bs, png_names)))
    bs = json.loads(stb); bs["phase_bridges"]["south"] = {}
    nc("stop JSON with south entry (out of scope) -> rejected", bool(v_stop(bs, png_names)))
    bs = json.loads(stb); bs["phase_bridges"]["west"]["phase0"][1]["file"] = "png/missing.png"
    nc("stop JSON with missing bridge frame -> rejected", bool(v_stop(bs, png_names)))
    bs = json.loads(stb); del bs["phase_bridges"]["west"]["phase11"]
    nc("stop JSON missing one entry phase -> rejected", bool(v_stop(bs, png_names)))
    bt = json.loads(ssb); bt["actions"]["walk"]["west"][5]["duration_ms"] = 0
    nc("walk duration 0 -> rejected", bool(v_timing(bt)))
    bt = json.loads(ssb); bt["actions"]["walk"]["west"][5]["duration_ms"] = 41
    nc("walk duration 41 (boundary drift) -> rejected", bool(v_timing(bt)))
    bt = json.loads(ssb); bt["pivot"] = [40, 103]
    nc("wrong pivot -> rejected", bool(v_timing(bt)))
    slid_n = [[(x[0] + 1, x[1] + 1) if x else None for x in s] for s in stop_near]
    nc("bridge s1 near foot slid 1 texel -> stop slip detected",
       v_contacts(near_w, far_w, slid_n, stop_far, th(ep_near), th(ep_far))["stop_bridge_grounded_slip_src_max"] > 0)
    slid_f = [[(x[0] + 1, x[1] + 1) if x else None for x in s] for s in stop_far]
    nc("bridge s2 far foot slid 1 texel -> stop slip detected",
       v_contacts(near_w, far_w, stop_near, slid_f, th(ep_near), th(ep_far))["stop_bridge_grounded_slip_src_max"] > 0)
    ep_off = np.roll(ep_near, 1, axis=1)
    nc("neutral endpoint near foot shifted 1 texel -> endpoint/slip detected",
       (lambda r: r["stop_bridge_grounded_slip_src_max"] > 0 or not r["stop_endpoint_neutral_all"])(v_contacts(near_w, far_w, stop_near, stop_far, th(ep_off), th(ep_far))))
    va = v_articulated([imgs[0]] * NPH, imgs[0])
    nc("unchanged neutral bitmap labelled as walk -> not articulated", va["phases_equal_neutral_lower"] > 0 or va["distinct_lower"] < 8)
    old_sliver = legacy_far_sliver(roles["boots"][0])
    nc("ORIGINAL fragmented far-limb geometry (2-5 texel front-boot split) -> rejected by b84 continuity "
       "(thin string / missing trouser+wrap mass)",
       bool(far_limb_errors(old_sliver, rgb)))
    frag = roles["far-limbs"][8].copy(); frag[70:80] = 0
    nc("far limb severed above the boot (disconnected mass) -> rejected", bool(far_limb_errors(frag, rgb)))
    ck("all negative controls rejected", all(n["rejected"] for n in neg), [n["control"] for n in neg if not n["rejected"]])

    # ------------------------------------------------------------------ native Pixelorama export
    native = {"run": False}
    if not a.skip_native:
        run = OUT / "native"
        run.mkdir()
        env = dict(os.environ)
        for key in ("DATA", "CONFIG", "CACHE"):
            (OUT / "xdg" / key.lower()).mkdir(parents=True)
            env["XDG_" + key + "_HOME"] = str(OUT / "xdg" / key.lower())
        src = ROOT / e["pxo"]["file"]
        before = sha(src.read_bytes())
        cmd = [os.environ["PIXELORAMA"], "--headless", "--audio-driver", "Dummy", "--quit", "--", "--export", "-o",
               str(run / f"requested_{TAG}.png"), str(src)]
        t0 = time.monotonic()
        p = subprocess.Popen(cmd, cwd=run, env=env, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, start_new_session=True)
        to = False
        try:
            log = p.communicate(timeout=90)[0]
        except subprocess.TimeoutExpired:
            to = True; os.killpg(p.pid, signal.SIGKILL); log = p.communicate()[0]
        (OUT / f"{PFX}_walk-west-native-export_test-only-v01_{TAG}.log").write_bytes(log)
        got = sorted(run.glob("*.png"), key=lambda q: [int(x) if x.isdigit() else x for x in re.split(r"(\d+)", q.name)])
        exact = sum(1 for i, q in enumerate(got) if i < NFR and np.array_equal(np.asarray(Image.open(q).convert("RGBA")), imgs[i]))
        text = log.decode("utf-8", "replace")
        diags = [ln for ln in text.splitlines() if any(s in ln for s in ("ERROR:", "SCRIPT ERROR", "Parse Error", "WARNING:"))]
        native = {"run": True, "command": cmd, "exit": p.returncode, "timeout": to, "elapsed_s": round(time.monotonic() - t0, 2),
                  "frames_expected": NFR, "frames_emitted": len(got), "frames_rgba_exact": exact,
                  "source_unchanged": sha(src.read_bytes()) == before, "diagnostics": diags[:20],
                  "application_clean": p.returncode == 0 and not to and not diags, "gui_saveas_reopen_verified": False}
        ck(f"native Pixelorama export: {NFR}/{NFR} frames RGBA-exact, exit 0, no timeout, source unchanged",
           p.returncode == 0 and not to and len(got) == NFR == exact and native["source_unchanged"],
           {k: native[k] for k in ("exit", "timeout", "frames_emitted", "frames_rgba_exact")})
        print("APPLICATION_DIAGNOSTICS (separate, not an export-equality gate):", len(diags), flush=True)

    S = 3
    walk_ims = imgs[5:17]
    sp = 7
    travel = V * 24
    x0 = travel + 20.0                       # west/screen-left travel; final left edge stays at x=20
    xs = []
    seq = [(imgs[1], 700, x0)]
    x = x0
    for i in range(24):
        seq.append((walk_ims[i % NPH], FMS, x)); xs.append(x); x -= V
    seq.append((walk_ims[sp], FMS, x)); xs.append(x)
    seq += [(imgs[17 + 2 * sp], FMS, x), (imgs[18 + 2 * sp], FMS, x), (imgs[1], 900, x)]
    cw, ch = int(round(x0 + W + 20)), int(H + 8)
    frames, durs = [], []
    for im, d, xx in seq:
        cv = Image.new("RGBA", (cw, ch), (58, 62, 70, 255))
        gv = Image.new("RGBA", (1, ch), (90, 96, 108, 255))
        gh = Image.new("RGBA", (cw, 1), (90, 96, 108, 255))
        for gx in range(0, cw, 22):
            cv.paste(gv, (gx, 0))
        cv.paste(gh, (0, SOLE + 1))
        cv.alpha_composite(Image.fromarray(im, "RGBA"), (int(round(xx)), 0))
        frames.append(cv.resize((cw * S, ch * S), Image.NEAREST).convert("P", palette=Image.ADAPTIVE, colors=255))
        durs.append(d)
    preview_ok = (all(abs((a - b) - V) < 1e-9 for a, b in zip(xs, xs[1:]))
                  and abs((x0 - xs[-1]) - 24 * V) < 1e-9)
    ck("preview translates horizontally WEST at 11.2 src px/40 ms, zero vertical displacement, 40 ms retained",
       preview_ok and durs[1:26] == [FMS] * 25 and ch == H + 8,
       {"step_src": round(xs[0] - xs[1], 3), "travel_src": round(x0 - xs[-1], 3), "canvas": [cw, ch]})
    gif = OUT / f"{PFX}_walk-west-normal-speed-preview-source-bound_unapproved-b84ww001-v01_{TAG}.gif"
    frames[0].save(gif, save_all=True, append_images=frames[1:], duration=durs, loop=0, disposal=2)
    sheet = Image.new("RGBA", (W * 12, H * 3), (58, 62, 70, 255))
    for i, im in enumerate(walk_ims):
        sheet.alpha_composite(Image.fromarray(im, "RGBA"), (i * W, 0))
    for p in range(NPH):
        sheet.alpha_composite(Image.fromarray(imgs[17 + 2 * p], "RGBA"), (p * W, H))
        sheet.alpha_composite(Image.fromarray(imgs[18 + 2 * p], "RGBA"), (p * W, 2 * H))
    sheetp = OUT / f"{PFX}_walk-west-contact-sheet-walk-s1-s2_unapproved-b84ww001-v01_{TAG}.png"
    sheet.resize((W * 12 * 2, H * 3 * 2), Image.NEAREST).save(sheetp)

    result = {"task": "content.char.muxiu.walk-west", "manifest": mrel, "manifest_sha256_raw": sha(mraw),
              "checker_sha256_raw": sha(Path(__file__).read_bytes()), "checks": checks, "negative_controls": neg,
              "contacts_independent": c, "articulation": art, "native": native,
              "preview": {"gif": gif.relative_to(ROOT).as_posix(), "gif_sha256": sha(gif.read_bytes()),
                          "contact_sheet": sheetp.relative_to(ROOT).as_posix(), "contact_sheet_sha256": sha(sheetp.read_bytes()),
                          "axis": "horizontal x only, screen-left = west; vertical offset constant 0",
                          "host_logical_px_s": HOST, "source_px_per_40ms": V,
                          "gif_canvas_px": [cw * S, ch * S], "frames": len(seq), "durations_ms": durs,
                          "scope": "source-bound PIL composite at 40 ms/frame, host 140 logical px/s = 11.2 source px "
                                   "per 40 ms westward (screen-left); NOT a Godot capture",
                          "sequence": "idle f00 700ms; walk 2 cycles translating west; release at phase 7 -> s1, s2, "
                                      "idle f00 with host stopped",
                          "supersedes_wrong_b78ww001_preview": "The old b78ww001 preview (retained under indep-r3 and "
                                      "hermes78-independent) translated the sprite DOWNWARD in a tall canvas copied "
                                      "from the south preview. It did not demonstrate west motion. This r1 preview "
                                      "is horizontal westward translation and is the only preview evidence here."},
              "not_claimed": ["footlock/slip-free (40 ms boundary residual is integer rounding; 60 fps held-frame excursion "
                              f"{c['walk_planted_foot_world_excursion_logical_60fps']} logical px is disclosed)",
                              "fluidity or human motion acceptance", "GUI SaveAs/reopen", "Godot runtime/normal-host stop playback",
                              "art approval", "default adoption"],
              "passed": all(x["pass"] for x in checks)}
    rp_ = OUT / f"{PFX}_walk-west-independent-result_v01_{TAG}.json"
    rp_.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(rp_.relative_to(ROOT).as_posix())
    print("INDEPENDENT", "PASS" if result["passed"] else "FAIL", sum(x["pass"] for x in checks), "/", len(checks))
    return 0 if result["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
