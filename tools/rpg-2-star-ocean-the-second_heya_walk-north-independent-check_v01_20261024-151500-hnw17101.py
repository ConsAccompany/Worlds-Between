"""Independent checker for Heya north walk/stop hnw171 (content.char.heya.walk-north). NO author/engine imports.

Adapted from the Heya south h165sw checker (same validators, tamper controls, native export and preview),
retargeted to the Heya north static and the existing Muxiu muxiu_walk-north pipeline. Reads only bytes on disk: source manifest, frame PNGs, animated PXO (data.json +
raw cels), ORA, package JSONs and the pinned Heya south neutral/palette. Re-derives (does not trust author metadata):
  hashes, PXO cel recomposition == every PNG, frame order/tags, timing + exact boundaries (walk 480 ms cycle,
  stop settle 120 ms inclusive), feet from raw boots cel sole row 103 split x40 (in-place front/back residual = host
  advance 11.2 src/40 ms held frame, per planted run, stop-bridge grounded slip for all 12 stop-entry phases,
  neutral endpoint), braid rides the head, identity anchors, palette.
Negative controls (in memory): tampered PNG byte, tampered PXO cel, malformed stop JSON, zero/boundary duration,
bridge foot slide, wrong pivot, bridge ending off-neutral, unchanged-bitmap "walk" -> each must be REJECTED.
Native: Pixelorama --headless --export of the animated PXO with isolated XDG dirs, 90 s deadline; export equality
and application diagnostics are reported separately; GUI SaveAs/reopen is NOT verified.
Preview: source-bound normal-speed GIF (40 ms frames, host 140 logical px/s) - not a Godot capture.

<venv python> -X utf8 -I <this> --out outputs/heya-sw165/<new dir>   (PIXELORAMA env = Pixelorama binary)
"""
import argparse, hashlib, io, json, os, re, signal, subprocess, time, zipfile
from pathlib import Path
import numpy as np
from PIL import Image

ROOT = Path(__file__).resolve().parent.parent
TAG = "20261024-151500-hnw17101"
PFX = "rpg-2-star-ocean-the-second_heya"
SRC_DIR = "outputs/heya-nw171"
PKG_DIR = "game/assets/characters/heya-native-v01/north-walk"
MAN = f"{SRC_DIR}/rpg-2-star-ocean-the-second_heya_walk-source-manifest_unapproved-hnw171-v01_20261024-151500-"
_N = "game/assets/characters/heya-native-v01/north"
NEUTRAL = (f"{_N}/rpg-2-star-ocean-the-second_heya_north-static_unapproved-v01_20261024-134500-56efefc2.png",
           "d0019c77032ec7dcb403e3d54cc80a6b9b60a875881cefa1887bb145072656c4")
PALFILE = (f"{_N}/rpg-2-star-ocean-the-second_heya_north-palette_unapproved-v01_20261024-134500-023052d9.json",
           "e1a1a9ac775ccb452498f02db97230b3135727da7d999bf132f2877837483a52")
LAYERS = ["far-limbs", "boots", "dress", "coat", "apron", "belt", "strap", "bag", "arms", "herb", "face", "hair", "braid",
          "scarf", "guides"]
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


def feet(boots):
    row = boots[SOLE, :, 3] == 255
    xs = np.arange(W)
    out = []
    for m in (row & (xs < 40), row & (xs >= 40)):
        x = np.flatnonzero(m)
        out.append((int(x.min()), int(x.max())) if len(x) else None)
    return out


def lowest(a, x0, x1):
    ys = np.flatnonzero(a[:, x0:x1, 3].any(1))
    return int(ys.max()) if len(ys) else None


def pxo_frames(pxo):
    z = zipfile.ZipFile(io.BytesIO(pxo))
    dj = json.loads(z.read("data.json"))
    names = [l["name"] for l in dj["layers"]]
    n = len(dj["frames"])
    cel = lambda f, li: np.frombuffer(z.read(f"image_data/frames/{f + 1}/layer_{li + 1}"), np.uint8).reshape(H, W, 4)
    comps = [over([cel(f, li) for li, nm in enumerate(names) if nm != "guides"]) for f in range(n)]
    roles = {nm: [cel(f, names.index(nm)) for f in range(n)] for nm in ("boots", "arms", "braid", "hair", "face") if nm in names}
    return dj, names, comps, roles


# ----------------------------------------------------------------------------- pure validators (reused by controls)
def v_stop(stop, png_names):
    errs = []
    if stop.get("frame_ms") != FMS or stop.get("settle_ms_inclusive") != 3 * FMS or stop.get("runtime_default") is not False:
        errs.append("stop timing/default fields")
    if stop.get("pivot") != [40, 104] or stop.get("logical_height") != 48:
        errs.append("stop pivot/height")
    pb = stop.get("phase_bridges", {})
    if list(pb) != ["north"] or sorted(pb["north"]) != sorted(f"phase{p}" for p in range(NPH)):
        errs.append("stop phases/direction scope")
    else:
        for p in range(NPH):
            s = pb["north"][f"phase{p}"]
            if len(s) != 4 or s[0] != {"ref": "walk", "index": p, "k": 0.0} or s[-1] != {"ref": "idle", "index": 0, "k": 1.0}:
                errs.append(f"bridge phase{p} endpoints")
            elif any(x.get("file", "").rsplit("/", 1)[-1] not in png_names for x in s[1:3]):
                errs.append(f"bridge phase{p} frame file")
    return errs


def v_timing(ss):
    errs = []
    idle = [f["duration_ms"] for f in ss["actions"]["idle"]["north"]]
    walk = [f["duration_ms"] for f in ss["actions"]["walk"]["north"]]
    if idle != IDLE_MS:
        errs.append(f"idle durations {idle}")
    if walk != [FMS] * NPH:
        errs.append(f"walk durations {walk}")
    if not all(isinstance(x, int) and x > 0 for x in idle + walk):
        errs.append("non-positive duration")
    if set(ss["actions"]["idle"]) != {"north"} or set(ss["actions"]["walk"]) != {"north"}:
        errs.append("direction scope")
    if ss.get("pivot") != [40, 104] or ss.get("frame_size") != [W, H] or ss.get("density") != 2:
        errs.append("contract")
    return errs


def v_articulated(walk_imgs, neutral):
    """An 'articulated walk' must not be an unchanged bitmap: every phase differs from neutral below the hip and
    at least 8 distinct lower-body states exist."""
    low = [im[80:104].tobytes() for im in walk_imgs]
    return {"phases_equal_neutral_lower": sum(1 for x in low if x == neutral[80:104].tobytes()), "distinct_lower": len(set(low))}


def frame_at(durs, t):
    t %= sum(durs)
    acc = 0
    for i, d in enumerate(durs):
        if t < acc + d:
            return i
        acc += d
    return len(durs) - 1


def v_contacts(walk_boots, bridges_boots, neutral_boots, endpoint_boots=None):
    """endpoint_boots = the raw idle f00 boots cel each bridge ends on (defaults to neutral for controls)."""
    endpoint_boots = neutral_boots if endpoint_boots is None else endpoint_boots
    rec = [feet(b) for b in walk_boots]
    pairs = []
    for p in range(NPH):
        for k in range(2):
            if rec[p][k] and rec[(p + 1) % NPH][k]:
                d = abs(rec[(p + 1) % NPH][k][0] - rec[p][k][0]) + abs(rec[(p + 1) % NPH][k][1] - rec[p][k][1])
                pairs.append({"from": p, "foot": "AB"[k], "screen_toe_heel_change_src": d, "world_slip_src": round(V, 3)})
    runs = []                                   # consecutive grounded phases per foot (cyclic), held 40 ms each
    for k in range(2):
        g = [bool(r[k]) for r in rec]
        start = next(p for p in range(NPH) if g[p] and not g[p - 1])
        n = 0
        while g[(start + n) % NPH] and n < NPH:
            n += 1
        runs.append({"foot": "AB"[k], "first_phase": start, "phases": n, "held_ms": n * FMS,
                     "in_place_world_travel_src": round(n * V, 3), "in_place_world_travel_logical": round(n * V / 2, 3)})
    stop_slip, endpoint = [], []
    nf, ef = feet(neutral_boots), feet(endpoint_boots)
    for p in range(NPH):
        seq = [rec[p], feet(bridges_boots[p][0]), feet(bridges_boots[p][1]), ef]
        for a, b in zip(seq, seq[1:]):
            for k in range(2):
                if a[k] and b[k]:
                    stop_slip.append(max(abs(a[k][0] - b[k][0]), abs(a[k][1] - b[k][1])))
        endpoint.append(ef == nf and bool(np.array_equal(endpoint_boots, neutral_boots)))
    grounded = [sum(1 for r in rec if r[k]) for k in range(2)]
    return {"grounded_phases_per_foot": grounded, "flight_phases": [p for p in range(NPH) if not rec[p][0] and not rec[p][1]],
            "double_support_phases": [p for p in range(NPH) if rec[p][0] and rec[p][1]],
            "swing_phases_per_foot": [[p for p in range(NPH) if not rec[p][k]] for k in range(2)],
            "grounded_pairs": len(pairs), "planted_screen_motion_src_max": max(x["screen_toe_heel_change_src"] for x in pairs),
            "front_inplace_world_slip_src_per_40ms": V if pairs else None, "front_inplace_world_slip_logical_per_40ms": V / 2 if pairs else None,
            "planted_runs": runs,
            "frame_hold_assumption": "each walk phase held 40 ms; host root moves continuously at 140 logical px/s (11.2 src/40 ms); "
                                     "sprite root does not move in source frames, so planted-foot world travel == host travel",
            "stop_bridge_grounded_slip_src_max": max(stop_slip) if stop_slip else 0, "stop_entry_phases_checked": NPH,
            "stop_endpoint_neutral_all": all(endpoint)}


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
    e = m["directions"]["north"]
    ck("manifest scope: north only, task content.char.heya.walk-north, UNAPPROVED", list(m["directions"]) == ["north"]
       and m["task_ids"] == ["content.char.heya.walk-north"] and "UNAPPROVED" in m["status"])
    ck("neutral Heya north PNG pin", sha(rd(NEUTRAL[0])) == NEUTRAL[1])
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
    ck("frames 80x112, binary alpha, clear border, palette subset of pinned Heya palette", not bad, bad[:5])
    ck("static and idle f00 are the neutral bytes", rd(order[0]["file"]) == rd(NEUTRAL[0]) == rd(order[1]["file"]))
    art = v_articulated(imgs[5:17], imgs[0])
    ck("articulated walk: no phase equals neutral below hip, >=8 distinct lower-body states", art["phases_equal_neutral_lower"] == 0
       and art["distinct_lower"] >= 8, art)
    pxo = rd(e["pxo"]["file"])
    ck("PXO raw hash", sha(pxo) == e["pxo"]["sha256"])
    dj, names, comps, roles = pxo_frames(pxo)
    ck(f"PXO {NFR} frames, layers far-limbs + 13 Heya roles + guides", len(comps) == NFR and names == LAYERS, names)
    mism = [i for i in range(min(NFR, len(comps))) if not np.array_equal(comps[i], imgs[i])]
    ck("PXO cels recompose to every frame PNG (independent alpha-over)", not mism, mism[:5])
    tags = {t["name"]: (t["from"], t["to"]) for t in dj.get("tags", [])}
    ck("PXO tags north-idle 2-5, north-walk 6-17, 12 stop tags", tags.get("north-idle") == (2, 5) and tags.get("north-walk") == (6, 17)
       and all(tags.get(f"north-stop-p{p:02d}") == (18 + 2 * p, 19 + 2 * p) for p in range(NPH)), tags.get("north-walk"))
    pkg = m["package"]
    ck("package paths under the assigned north-walk root", all(pkg[k].startswith(PKG_DIR + "/") for k in ("sprite_set", "registry", "stop_supplemental")))
    ssb = rd(pkg["sprite_set"])
    ck("sprite set raw hash", sha(ssb) == pkg["sprite_set_sha256"])
    ss = json.loads(ssb)
    te = v_timing(ss)
    ck("sprite set timing/contract/north-only", not te, te)
    stb = rd(pkg["stop_supplemental"])
    ck("stop supplemental text_lf_v1 hash", sha(stb.replace(b"\r\n", b"\n")) == pkg["stop_supplemental_sha256_text_lf_v1"])
    stop = json.loads(stb)
    png_names = {p.name for p in (ROOT / PKG_DIR / "png").glob("*.png")}
    se = v_stop(stop, png_names)
    ck("stop supplemental north structure (12 phase bridges [walk p, s1, s2, idle f00], 40 ms, settle 120 inclusive, non-default)", not se, se)
    copies = [f["file"] for act in ss["actions"].values() for f in act["north"]] + \
             ["png/" + s["file"].rsplit("/", 1)[-1] for v in stop["phase_bridges"]["north"].values() for s in v if "file" in s]
    ck("package PNG copies byte-equal to source frames", all(rd(f"{PKG_DIR}/{c}") == rd(f"{SRC_DIR}/{c}") for c in copies), len(copies))
    walk_d = [f["duration_ms"] for f in ss["actions"]["walk"]["north"]]
    bnd = {t: frame_at(walk_d, t) for t in (0, 39, 40, 439, 440, 479, 480, 481)}
    ck("walk timing boundaries: 39->p0 40->p1 479->p11 480->p0 (cycle 480 ms)",
       bnd == {0: 0, 39: 0, 40: 1, 439: 10, 440: 11, 479: 11, 480: 0, 481: 0}, bnd)
    idle_b = {t: frame_at(IDLE_MS, t) for t in (699, 700, 899, 900, 1299, 1300, 1499, 1500)}
    ck("idle timing boundaries (700/200/400/200, loop 1500 ms)", idle_b == {699: 0, 700: 1, 899: 1, 900: 2, 1299: 2, 1300: 3, 1499: 3, 1500: 0}, idle_b)
    seq_t = lambda t: min(int(t // FMS), 3)
    sb = {t: seq_t(t) for t in (0, 39, 40, 79, 80, 119, 120, 1000)}
    ck("stop bridge boundaries: release t0 walk p; 40 s1; 80 s2; 120 (inclusive) idle f00 held",
       sb == {0: 0, 39: 0, 40: 1, 79: 1, 80: 2, 119: 2, 120: 3, 1000: 3}, sb)
    boots = roles["boots"]
    walk_boots = boots[5:17]
    br_boots = [(boots[17 + 2 * p], boots[18 + 2 * p]) for p in range(NPH)]
    c = v_contacts(walk_boots, br_boots, boots[0], boots[1])
    ck("each foot grounded exactly 4 of 12 phases", c["grounded_phases_per_foot"] == [4, 4], c["grounded_phases_per_foot"])
    ck("planted foot screen position constant while grounded (in place)", c["planted_screen_motion_src_max"] == 0, c["planted_screen_motion_src_max"])
    ck("north stop bridges (all 12 entry phases): grounded foot never moves (host stopped)", c["stop_bridge_grounded_slip_src_max"] == 0, c["stop_bridge_grounded_slip_src_max"])
    ck("all 12 stop bridges terminate in exact neutral feet + neutral PNG (idle f00)", c["stop_endpoint_neutral_all"]
       and all(stop["phase_bridges"]["north"][f"phase{p}"][-1] == {"ref": "idle", "index": 0, "k": 1.0} for p in range(NPH))
       and rd(order[1]["file"]) == rd(NEUTRAL[0]))
    claimed = m["contact_check"]["north"]
    ck("independent contacts agree with author claims (residual 11.2 src, flight phases, stop 0)",
       claimed["walk_max_world_slip_src_at_40ms_boundaries"] == round(V, 3) and claimed["flight_phases"] == c["flight_phases"]
       and claimed["stop_bridge_grounded_slip_src_max"] == c["stop_bridge_grounded_slip_src_max"], c["flight_phases"])
    # braid rides the head: constant top-row offset to the hair layer in every frame
    br, hr = roles["braid"], roles["hair"]
    off = {int(np.flatnonzero(br[i][..., 3].any(1)).min() - np.flatnonzero(hr[i][..., 3].any(1)).min()) for i in range(NFR)}
    exp_off = int(np.flatnonzero(br[0][..., 3].any(1)).min() - np.flatnonzero(hr[0][..., 3].any(1)).min())
    ck("braid stays on the head (constant offset to hair top in all frames)", off == {exp_off}, sorted(off))
    hair_c, scarf_c, bag_c, herb_c = {rgb[k] for k in ("h1", "h2", "h3")}, {rgb[k] for k in ("f1", "f2", "f3")}, \
        {rgb[k] for k in ("b1", "b2", "b3")}, {rgb[k] for k in ("n1", "n2")}
    coat_c, apron_c = {rgb[k] for k in ("w1", "w2", "w3")}, {rgb[k] for k in ("v1", "v2", "v3")}

    def reg(im, y0, y1, x0, x1):
        s = im[y0:y1, x0:x1]
        return {tuple(v) for v in s[s[..., 3] == 255][:, :3]}
    def identity_bad(frames):
        return [i for i, im in enumerate(frames) if not (hair_c & reg(im, 8, 42, 24, 56) and scarf_c & reg(im, 32, 64, 24, 50)
                                                         and bag_c & reg(im, 56, 82, 12, 30) and herb_c & reg(im, 52, 64, 42, 52)
                                                         and coat_c & reg(im, 30, 90, 24, 56) and apron_c & reg(im, 58, 82, 26, 54))]
    idm = identity_bad(imgs)
    ck("identity (rear): low braid, scarf back tail screen-left, bag screen-left, herb screen-right, coat + apron in all frames", not idm, idm[:5])
    eye_c = {rgb[k] for k in ("e1", "e2", "m1")}
    eb = [i for i, im in enumerate(roles["face"]) if {tuple(v) for v in im[im[..., 3] == 255][:, :3]} & eye_c]
    ck("north rear face layer has no eye/mouth colours in any frame", not eb, eb[:5])
    south_png = dec(rd("game/assets/characters/heya-native-v01/south/rpg-2-star-ocean-the-second_heya_south-static_unapproved-v01_20261024-125310-231d2b03.png"))
    nm = imgs[0]
    mirror_px = int(np.count_nonzero((np.fliplr(south_png) != nm).any(2) & (nm[..., 3] > 0)))
    ck("north static is not a horizontal mirror of south (>=400 opaque texels differ); rear view is own art",
       mirror_px >= 400 and np.array_equal(nm, dec(rd(NEUTRAL[0]))), {"mirror_pixel_diff": mirror_px})
    ck("top row never above neutral row 8; soles never below 103",
       all(np.flatnonzero(im[..., 3].any(1)).min() >= 8 and np.flatnonzero(im[..., 3].any(1)).max() <= SOLE for im in imgs))

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
    bs = json.loads(stb); bs["phase_bridges"]["north"]["phase3"][-1] = {"ref": "idle", "index": 1, "k": 1.0}
    nc("malformed stop JSON (bridge ends on idle f01) -> rejected", bool(v_stop(bs, png_names)))
    bs = json.loads(stb); bs["frame_ms"] = 39
    nc("stop frame_ms 39 -> rejected", bool(v_stop(bs, png_names)))
    bs = json.loads(stb); bs["phase_bridges"]["south"] = {}
    nc("stop JSON with west entry (out of scope) -> rejected", bool(v_stop(bs, png_names)))
    bs = json.loads(stb); bs["phase_bridges"]["north"]["phase0"][1]["file"] = "png/missing.png"
    nc("stop JSON with missing bridge frame -> rejected", bool(v_stop(bs, png_names)))
    bs = json.loads(stb); del bs["phase_bridges"]["north"]["phase11"]
    nc("stop JSON missing one entry phase -> rejected", bool(v_stop(bs, png_names)))
    bt = json.loads(ssb); bt["actions"]["walk"]["north"][5]["duration_ms"] = 0
    nc("walk duration 0 -> rejected", bool(v_timing(bt)))
    bt = json.loads(ssb); bt["actions"]["walk"]["north"][5]["duration_ms"] = 41
    nc("walk duration 41 (boundary drift) -> rejected", bool(v_timing(bt)))
    bt = json.loads(ssb); bt["pivot"] = [40, 103]
    nc("wrong pivot -> rejected", bool(v_timing(bt)))
    slid = [(np.roll(a_, 1, axis=1), b_) for a_, b_ in br_boots]
    nc("bridge s1 foot slid 1 texel -> stop slip detected", v_contacts(walk_boots, slid, boots[0])["stop_bridge_grounded_slip_src_max"] > 0)
    off_n = np.roll(boots[0], 1, axis=1)
    nc("bridge endpoint off-neutral (neutral feet shifted 1 texel) -> endpoint/slip detected",
       (lambda r: r["stop_bridge_grounded_slip_src_max"] > 0 or not r["stop_endpoint_neutral_all"])(v_contacts(walk_boots, br_boots, boots[0], off_n)))
    va = v_articulated([imgs[0]] * NPH, imgs[0])
    nc("unchanged neutral bitmap labelled as walk -> not articulated", va["phases_equal_neutral_lower"] > 0 or va["distinct_lower"] < 8)
    broken = imgs[8].copy(); broken[32:64, 28:54] = 0
    nc("wrong identity (scarf erased in one walk frame) -> identity check rejects", bool(identity_bad([broken])))
    ck("north all negative controls rejected", all(n["rejected"] for n in neg), [n["control"] for n in neg if not n["rejected"]])

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
        pix = os.environ.get("PIXELORAMA") or "/home/kel/projects/worlds-between/tooling/pixelorama-1.2.3/Pixelorama-Linux-64bit/Pixelorama.x86_64"
        cmd = [pix, "--headless", "--audio-driver", "Dummy", "--quit", "--", "--export", "-o",
               str(run / f"requested_{TAG}.png"), str(src)]
        t0 = time.monotonic()
        p = subprocess.Popen(cmd, cwd=run, env=env, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, start_new_session=True)
        to = False
        try:
            log = p.communicate(timeout=90)[0]
        except subprocess.TimeoutExpired:
            to = True; os.killpg(p.pid, signal.SIGKILL); log = p.communicate()[0]
        (OUT / f"{PFX}_walk-north-native-export_test-only-v01_{TAG}.log").write_bytes(log)
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

    # ------------------------------------------------------------------ source-bound normal-speed preview
    S = 3
    walk_ims = imgs[5:17]
    seq = [(imgs[1], 700, 0.0)]                                   # idle f00
    y = 0.0
    for i in range(24):                                           # 2 walk cycles moving south at host speed
        seq.append((walk_ims[i % NPH], FMS, y)); y += V
    sp = 7                                                        # explicit release phase 7
    seq.append((walk_ims[sp], FMS, y))
    seq += [(imgs[17 + 2 * sp], FMS, y), (imgs[18 + 2 * sp], FMS, y), (imgs[1], 900, y)]
    ch = int(H + y + 8)
    frames, durs = [], []
    for im, d, yy in seq:
        cv = Image.new("RGBA", (W + 40, ch), (58, 62, 70, 255))
        g_ = Image.new("RGBA", (W + 40, 1), (90, 96, 108, 255))
        for gy in range(SOLE + 1, ch, 22):
            cv.paste(g_, (0, gy))
        cv.alpha_composite(Image.fromarray(im, "RGBA"), (20, int(round(yy))))
        frames.append(cv.resize(((W + 40) * S, ch * S), Image.NEAREST).convert("P", palette=Image.ADAPTIVE, colors=255))
        durs.append(d)
    gif = OUT / f"{PFX}_walk-north-normal-speed-preview-source-bound_unapproved-hnw171-v01_{TAG}.gif"
    frames[0].save(gif, save_all=True, append_images=frames[1:], duration=durs, loop=0, disposal=2)
    sheet = Image.new("RGBA", (W * 12, H * 3), (58, 62, 70, 255))
    for i, im in enumerate(walk_ims):
        sheet.alpha_composite(Image.fromarray(im, "RGBA"), (i * W, 0))
    for p in range(NPH):
        sheet.alpha_composite(Image.fromarray(imgs[17 + 2 * p], "RGBA"), (p * W, H))
        sheet.alpha_composite(Image.fromarray(imgs[18 + 2 * p], "RGBA"), (p * W, 2 * H))
    sheetp = OUT / f"{PFX}_walk-north-contact-sheet-walk-s1-s2_unapproved-hnw171-v01_{TAG}.png"
    sheet.resize((W * 12 * 2, H * 3 * 2), Image.NEAREST).save(sheetp)

    result = {"task": "content.char.heya.walk-north", "manifest": mrel, "manifest_sha256_raw": sha(mraw),
              "checker_sha256_raw": sha(Path(__file__).read_bytes()), "checks": checks, "negative_controls": neg,
              "contacts_independent": c, "articulation": art, "native": native,
              "preview": {"gif": gif.relative_to(ROOT).as_posix(), "gif_sha256": sha(gif.read_bytes()),
                          "contact_sheet": sheetp.relative_to(ROOT).as_posix(), "contact_sheet_sha256": sha(sheetp.read_bytes()),
                          "scope": "source-bound PIL composite at 40 ms/frame, host 11.2 src px/40 ms; NOT a Godot capture",
                          "sequence": "idle f00 700ms, walk 2 cycles moving north, release at phase 7 -> s1, s2, idle f00"},
              "not_claimed": ["footlock/slip-free (front is in place: 5.6 logical px/40 ms residual, 22.4 logical per 160 ms plant)",
                              "fluidity or human motion acceptance", "GUI SaveAs/reopen", "Godot runtime/normal-host stop playback",
                              "art approval", "default adoption"],
              "passed": all(x["pass"] for x in checks)}
    rp_ = OUT / f"{PFX}_walk-north-independent-result_v01_{TAG}.json"
    rp_.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(rp_.relative_to(ROOT).as_posix())
    print("INDEPENDENT", "PASS" if result["passed"] else "FAIL", sum(x["pass"] for x in checks), "/", len(checks))
    return 0 if result["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
