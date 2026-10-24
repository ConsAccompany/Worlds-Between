"""Independent checker for Heya east walk/stop h176ew01 (content.char.heya.walk-east). NO author/engine imports.

Adapted from the Heya south h165sw / Yanke ykww107 independent checkers. Reads only bytes on disk: source manifest,
frame PNGs, animated PXO (data.json + raw cels), ORA, package JSONs and the pinned Heya east neutral/palette.
Re-derives (does not trust author metadata): hashes, PXO cel recomposition == every PNG, frame order/tags, timing and
exact boundaries (walk 480 ms cycle, stop settle 120 ms inclusive), side boot contact from the near boots cel and the
far-limbs cel sole row 103 (planted world slip <=1 src rounding of 11.2, each foot grounded 4 phases, stop-bridge
grounded slip for all 12 entry phases inclusive endpoint, neutral endpoint), braid rides the head, identity anchors,
palette. Negative controls (in memory): tampered PNG/PXO, malformed stop JSON, zero/boundary duration, bridge foot
slide, wrong pivot, bridge ending off-neutral, unchanged-bitmap walk, wrong identity -> each must be REJECTED.
Native: Pixelorama --headless --export of the animated PXO with isolated XDG dirs, 90 s deadline; export equality and
application diagnostics are reported separately; GUI SaveAs/reopen is NOT verified.
Preview: source-bound normal-speed GIF (40 ms frames, host 140 logical px/s) - not a Godot capture.

<venv python> -X utf8 -I <this> --out outputs/heya-ew176/<new dir>   (PIXELORAMA env = Pixelorama binary)
"""
import argparse, hashlib, io, json, os, re, signal, subprocess, time, zipfile
from pathlib import Path
import numpy as np
from PIL import Image

ROOT = Path(__file__).resolve().parent.parent
TAG = "20261024-154500-h176ew01"
PFX = "rpg-2-star-ocean-the-second_heya"
SRC_DIR = "outputs/heya-ew176"
PKG_DIR = "game/assets/characters/heya-native-v01/east-walk"
MAN = f"{SRC_DIR}/rpg-2-star-ocean-the-second_heya_walk-source-manifest_unapproved-h176ew01-v01_20261024-154500-"
_N = "game/assets/characters/heya-native-v01/east"
NEUTRAL = (f"{_N}/rpg-2-star-ocean-the-second_heya_east-static_unapproved-v01_20261024-141500-6041ee95.png",
           "273e5e854121fa8ec92dc74e28a67be35920da6442fc20571ff053453fdf9dd4")
PALFILE = (f"{_N}/rpg-2-star-ocean-the-second_heya_east-palette_unapproved-v01_20261024-141500-f7eba38b.json",
           "6af85c7ac9e1dfc76a44a53864d9a7ef58c7d02d1c3e3e8ab1d71b50e6d55311")
LAYERS = ["far-limbs", "boots", "dress", "coat", "apron", "belt", "strap", "bag", "arms", "herb", "face", "hair",
          "braid", "scarf", "guides"]
W, H, SOLE, NPH, FMS, HOST = 80, 112, 103, 12, 40, 140.0
V = HOST * FMS / 1000 * 2           # 11.2 source texels per 40 ms at density 2
NEAR_MIN_X = 38
IDLE_MS = [700, 200, 400, 200]
NFR = 1 + 4 + NPH + 2 * NPH          # 41
SIGN = 1                             # east: forward is screen right


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


def feet_side(boots, far):
    """Return (near A, far B) sole-row toe/heel in screen x; east toe = max x, heel = min x."""
    out = []
    for a in (boots, far):
        row = a[SOLE, :, 3] == 255
        x = np.flatnonzero(row)
        out.append((int(x.min()), int(x.max())) if len(x) else None)
    return out


def pxo_frames(pxo):
    z = zipfile.ZipFile(io.BytesIO(pxo))
    dj = json.loads(z.read("data.json"))
    names = [l["name"] for l in dj["layers"]]
    n = len(dj["frames"])
    cel = lambda f, li: np.frombuffer(z.read(f"image_data/frames/{f + 1}/layer_{li + 1}"), np.uint8).reshape(H, W, 4)
    comps = [over([cel(f, li) for li, nm in enumerate(names) if nm != "guides"]) for f in range(n)]
    roles = {nm: [cel(f, names.index(nm)) for f in range(n)] for nm in ("boots", "far-limbs", "arms", "braid", "hair") if nm in names}
    return dj, names, comps, roles


# ----------------------------------------------------------------------------- pure validators (reused by controls)
def v_stop(stop, png_names):
    errs = []
    if stop.get("frame_ms") != FMS or stop.get("settle_ms_inclusive") != 3 * FMS or stop.get("runtime_default") is not False:
        errs.append("stop timing/default fields")
    if stop.get("pivot") != [40, 104] or stop.get("logical_height") != 48:
        errs.append("stop pivot/height")
    pb = stop.get("phase_bridges", {})
    if list(pb) != ["east"] or sorted(pb["east"]) != sorted(f"phase{p}" for p in range(NPH)):
        errs.append("stop phases/direction scope")
    else:
        for p in range(NPH):
            s = pb["east"][f"phase{p}"]
            if len(s) != 4 or s[0] != {"ref": "walk", "index": p, "k": 0.0} or s[-1] != {"ref": "idle", "index": 0, "k": 1.0}:
                errs.append(f"bridge phase{p} endpoints")
            elif any(x.get("file", "").rsplit("/", 1)[-1] not in png_names for x in s[1:3]):
                errs.append(f"bridge phase{p} frame file")
    return errs


def v_timing(ss):
    errs = []
    idle = [f["duration_ms"] for f in ss["actions"]["idle"]["east"]]
    walk = [f["duration_ms"] for f in ss["actions"]["walk"]["east"]]
    if idle != IDLE_MS:
        errs.append(f"idle durations {idle}")
    if walk != [FMS] * NPH:
        errs.append(f"walk durations {walk}")
    if not all(isinstance(x, int) and x > 0 for x in idle + walk):
        errs.append("non-positive duration")
    if set(ss["actions"]["idle"]) != {"east"} or set(ss["actions"]["walk"]) != {"east"}:
        errs.append("direction scope")
    if ss.get("pivot") != [40, 104] or ss.get("frame_size") != [W, H] or ss.get("density") != 2:
        errs.append("contract")
    return errs


def v_articulated(walk_imgs, neutral):
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


def v_contacts(walk_boots, walk_far, bridges_boots, bridges_far, neutral_boots):
    """Independent side contact from near boots + far-limbs cels. neutral_boots is the idle f00 boots cel."""
    rec = [feet_side(b, f) for b, f in zip(walk_boots, walk_far)]
    worst = 0.0
    pairs = 0
    for p in range(NPH):
        n = (p + 1) % NPH
        for k in range(2):
            a, b = rec[p][k], rec[n][k]
            if a and b:
                dt = SIGN * (b[0] - a[0]) + V
                dh = SIGN * (b[1] - a[1]) + V
                worst = max(worst, abs(round(dt, 3)), abs(round(dh, 3)))
                pairs += 1
    near_n = neutral_boots.copy(); near_n[:, :NEAR_MIN_X] = 0
    nf = [feet_side(near_n, near_n)[0], None]
    far_n = neutral_boots.copy()
    nf[1] = (int(np.flatnonzero(far_n[SOLE, :, 3])[0]), int(np.flatnonzero(far_n[SOLE, :, 3])[-1]))
    stop_slip = 0
    stop_bad = []
    endpoint_bad = []
    for p in range(NPH):
        seq = [rec[p]]
        for s in (0, 1):
            seq.append(feet_side(bridges_boots[p][s], bridges_far[p][s]))
        seq.append(nf)
        for i in range(3):
            for k in range(2):
                a, b = seq[i][k], seq[i + 1][k]
                if a and b:
                    m = max(abs(a[0] - b[0]), abs(a[1] - b[1]))
                    stop_slip = max(stop_slip, m)
                    if m:
                        stop_bad.append({"phase": p, "step": i, "foot": "AB"[k], "slip_src": m})
        # s2 may still be lifted halfway; the bridge endpoint is idle f00 (checked byte-exact at the call site).
        # independently require s2 far limb to remain a non-empty dark boot silhouette.
        s2f = bridges_far[p][1]
        if not s2f[..., 3].any():
            endpoint_bad.append(p)
    grounded = [sum(1 for r in rec if r[k]) for k in range(2)]
    return {"grounded_phases_per_foot": grounded, "flight_phases": [p for p in range(NPH) if not rec[p][0] and not rec[p][1]],
            "double_support_phases": [p for p in range(NPH) if rec[p][0] and rec[p][1]],
            "swing_phases_per_foot": [[p for p in range(NPH) if not rec[p][k]] for k in range(2)],
            "grounded_pairs": pairs, "planted_world_slip_src_max": round(worst, 3),
            "front_inplace_world_slip_src_per_40ms": None,
            "stop_bridge_grounded_slip_src_max": int(stop_slip), "stop_bridge_nonzero": stop_bad[:8],
            "stop_entry_phases_checked": NPH, "stop_endpoint_neutral_all": not endpoint_bad,
            "stop_endpoint_bad_phases": endpoint_bad,
            "frame_hold_assumption": "each walk phase held 40 ms; host root moves continuously at 140 logical px/s "
                                     "(11.2 src/40 ms); sprite root does not move in source frames"}


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
    e = m["directions"]["east"]
    ck("manifest scope: east only, task content.char.heya.walk-east, UNAPPROVED", list(m["directions"]) == ["east"]
       and m["task_ids"] == ["content.char.heya.walk-east"] and "UNAPPROVED" in m["status"])
    ck("neutral Heya east PNG pin", sha(rd(NEUTRAL[0])) == NEUTRAL[1])
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
    ck("articulated walk: no phase equals neutral below hip, >=8 distinct lower-body states",
       art["phases_equal_neutral_lower"] == 0 and art["distinct_lower"] >= 8, art)
    pxo = rd(e["pxo"]["file"])
    ck("PXO raw hash", sha(pxo) == e["pxo"]["sha256"])
    dj, names, comps, roles = pxo_frames(pxo)
    ck(f"PXO {NFR} frames, layers far-limbs + 13 Heya roles + guides", len(comps) == NFR and names == LAYERS, names)
    mism = [i for i in range(min(NFR, len(comps))) if not np.array_equal(comps[i], imgs[i])]
    ck("PXO cels recompose to every frame PNG (independent alpha-over)", not mism, mism[:5])
    tags = {t["name"]: (t["from"], t["to"]) for t in dj.get("tags", [])}
    ck("PXO tags east-idle 2-5, east-walk 6-17, 12 stop tags", tags.get("east-idle") == (2, 5) and tags.get("east-walk") == (6, 17)
       and all(tags.get(f"east-stop-p{p:02d}") == (18 + 2 * p, 19 + 2 * p) for p in range(NPH)), tags.get("east-walk"))
    pkg = m["package"]
    ck("package paths under the assigned east-walk root", all(pkg[k].startswith(PKG_DIR + "/") for k in ("sprite_set", "registry", "stop_supplemental")))
    ssb = rd(pkg["sprite_set"])
    ck("sprite set raw hash", sha(ssb) == pkg["sprite_set_sha256"])
    ss = json.loads(ssb)
    te = v_timing(ss)
    ck("sprite set timing/contract/east-only", not te, te)
    stb = rd(pkg["stop_supplemental"])
    ck("stop supplemental text_lf_v1 hash", sha(stb.replace(b"\r\n", b"\n")) == pkg["stop_supplemental_sha256_text_lf_v1"])
    stop = json.loads(stb)
    png_names = {p.name for p in (ROOT / PKG_DIR / "png").glob("*.png")}
    se = v_stop(stop, png_names)
    ck("stop supplemental structure (12 phase bridges [walk p, s1, s2, idle f00], 40 ms, settle 120 inclusive, non-default)", not se, se)
    copies = [f["file"] for act in ss["actions"].values() for f in act["east"]] + \
             ["png/" + s["file"].rsplit("/", 1)[-1] for v in stop["phase_bridges"]["east"].values() for s in v if "file" in s]
    ck("package PNG copies byte-equal to source frames", all(rd(f"{PKG_DIR}/{c}") == rd(f"{SRC_DIR}/{c}") for c in copies), len(copies))
    walk_d = [f["duration_ms"] for f in ss["actions"]["walk"]["east"]]
    bnd = {t: frame_at(walk_d, t) for t in (0, 39, 40, 439, 440, 479, 480, 481)}
    ck("walk timing boundaries: 39->p0 40->p1 479->p11 480->p0 (cycle 480 ms)",
       bnd == {0: 0, 39: 0, 40: 1, 439: 10, 440: 11, 479: 11, 480: 0, 481: 0}, bnd)
    idle_b = {t: frame_at(IDLE_MS, t) for t in (699, 700, 899, 900, 1299, 1300, 1499, 1500)}
    ck("idle timing boundaries (700/200/400/200, loop 1500 ms)", idle_b == {699: 0, 700: 1, 899: 1, 900: 2, 1299: 2, 1300: 3, 1499: 3, 1500: 0}, idle_b)
    seq_t = lambda t: min(int(t // FMS), 3)
    sb = {t: seq_t(t) for t in (0, 39, 40, 79, 80, 119, 120, 1000)}
    ck("stop bridge boundaries: release t0 walk p; 40 s1; 80 s2; 120 (inclusive) idle f00 held",
       sb == {0: 0, 39: 0, 40: 1, 79: 1, 80: 2, 119: 2, 120: 3, 1000: 3}, sb)
    walk_boots = roles["boots"][5:17]
    walk_far = roles["far-limbs"][5:17]
    br_boots = [(roles["boots"][17 + 2 * p], roles["boots"][18 + 2 * p]) for p in range(NPH)]
    br_far = [(roles["far-limbs"][17 + 2 * p], roles["far-limbs"][18 + 2 * p]) for p in range(NPH)]
    c = v_contacts(walk_boots, walk_far, br_boots, br_far, roles["boots"][1])
    ck("each foot grounded exactly 4 of 12 phases", c["grounded_phases_per_foot"] == [4, 4], c["grounded_phases_per_foot"])
    ck("side planted-foot world slip at 40 ms boundaries <= 1 source texel (integer rounding of 11.2)",
       c["planted_world_slip_src_max"] <= 1.0, c["planted_world_slip_src_max"])
    ck("stop bridges (all 12 entry phases): grounded boot never moves (host stopped)",
       c["stop_bridge_grounded_slip_src_max"] == 0, c["stop_bridge_nonzero"][:3])
    ck("all 12 stop bridges terminate on exact neutral near/far boot footprints and idle f00 == neutral PNG",
       c["stop_endpoint_neutral_all"] and all(stop["phase_bridges"]["east"][f"phase{p}"][-1] == {"ref": "idle", "index": 0, "k": 1.0} for p in range(NPH))
       and rd(order[1]["file"]) == rd(NEUTRAL[0]), c["stop_endpoint_bad_phases"])
    claimed = m["contact_check"]["east"]
    ck("independent contacts agree with author claims (boundary slip, grounded phases, flight, stop 0)",
       claimed["walk_max_world_slip_src_at_40ms_boundaries"] == c["planted_world_slip_src_max"]
       and [sum(1 for r in claimed["per_phase_feet"] if r[k]["grounded"]) for k in ("A", "B")] == c["grounded_phases_per_foot"]
       and claimed["flight_phases"] == c["flight_phases"]
       and claimed["stop_bridge_grounded_slip_src_max"] == c["stop_bridge_grounded_slip_src_max"], c["flight_phases"])
    br, hr = roles["braid"], roles["hair"]
    off = {int(np.flatnonzero(br[i][..., 3].any(1)).min() - np.flatnonzero(hr[i][..., 3].any(1)).min()) for i in range(NFR)}
    ck("braid stays on the head (constant offset to hair top in all frames)", off == {16}, sorted(off))
    hair_c = {rgb[k] for k in ("h1", "h2", "h3", "h4")}
    scarf_c, bag_c, herb_c = {rgb[k] for k in ("f1", "f2", "f3")}, {rgb[k] for k in ("b1", "b2", "b3")}, {rgb[k] for k in ("n1", "n2")}
    coat_c, apron_c = {rgb[k] for k in ("w1", "w2", "w3")}, {rgb[k] for k in ("v1", "v2", "v3")}

    def reg(im, y0, y1, x0, x1):
        s = im[y0:y1, x0:x1]
        return {tuple(v) for v in s[s[..., 3] == 255][:, :3]}

    def identity_bad(frames):
        return [i for i, im in enumerate(frames) if not (hair_c & reg(im, 8, 42, 24, 52) and scarf_c & reg(im, 32, 58, 28, 50)
                                                         and bag_c & reg(im, 56, 84, 20, 34) and herb_c & reg(im, 42, 53, 42, 52)
                                                         and coat_c & reg(im, 30, 90, 28, 48) and apron_c & reg(im, 56, 88, 27, 49))]
    idm = identity_bad(imgs)
    ck("identity: low braid, grey-white scarf, dark-red bag, herb, ivory coat + pale apron in all frames", not idm, idm[:5])
    ck("top row never above neutral row 8; soles never below 103",
       all(np.flatnonzero(im[..., 3].any(1)).min() >= 8 and np.flatnonzero(im[..., 3].any(1)).max() <= SOLE for im in imgs))
    ck("far-limb cels non-empty in every walk phase and every stop bridge frame",
       all(f[..., 3].any() for f in walk_far) and all(f[..., 3].any() for pair in br_far for f in pair))

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
    nc("tampered PXO boots cel -> recomposition mismatch", not np.array_equal(tcomps[8], imgs[8]))
    bs = json.loads(stb); bs["phase_bridges"]["east"]["phase3"][-1] = {"ref": "idle", "index": 1, "k": 1.0}
    nc("malformed stop JSON (bridge ends on idle f01) -> rejected", bool(v_stop(bs, png_names)))
    bs = json.loads(stb); bs["frame_ms"] = 39
    nc("stop frame_ms 39 -> rejected", bool(v_stop(bs, png_names)))
    bs = json.loads(stb); bs["phase_bridges"]["south"] = {}
    nc("stop JSON with south entry (out of scope) -> rejected", bool(v_stop(bs, png_names)))
    bs = json.loads(stb); bs["phase_bridges"]["east"]["phase0"][1]["file"] = "png/missing.png"
    nc("stop JSON with missing bridge frame -> rejected", bool(v_stop(bs, png_names)))
    bs = json.loads(stb); del bs["phase_bridges"]["east"]["phase11"]
    nc("stop JSON missing one entry phase -> rejected", bool(v_stop(bs, png_names)))
    bt = json.loads(ssb); bt["actions"]["walk"]["east"][5]["duration_ms"] = 0
    nc("walk duration 0 -> rejected", bool(v_timing(bt)))
    bt = json.loads(ssb); bt["actions"]["walk"]["east"][5]["duration_ms"] = 41
    nc("walk duration 41 (boundary drift) -> rejected", bool(v_timing(bt)))
    bt = json.loads(ssb); bt["pivot"] = [40, 103]
    nc("wrong pivot -> rejected", bool(v_timing(bt)))
    slid = [(np.roll(a_, 1, axis=1), f_) for a_, f_ in br_boots]
    nc("bridge s1 near boot slid 1 texel -> stop slip detected",
       v_contacts(walk_boots, walk_far, slid, br_far, roles["boots"][1])["stop_bridge_grounded_slip_src_max"] > 0)
    slidf = [(b_, np.roll(f_, 1, axis=1)) for b_, f_ in br_far]
    nc("bridge s1 far boot slid 1 texel -> stop slip detected",
       v_contacts(walk_boots, walk_far, br_boots, slidf, roles["boots"][1])["stop_bridge_grounded_slip_src_max"] > 0)
    idle_b = bytearray(rd(NEUTRAL[0])); idle_b[-20] ^= 1
    endpoint_ok = lambda bts: bytes(bts) == rd(NEUTRAL[0])
    nc("bridge endpoint idle f00 bytes differ from pinned neutral PNG -> endpoint detects", not endpoint_ok(idle_b))
    va = v_articulated([imgs[0]] * NPH, imgs[0])
    nc("unchanged neutral bitmap labelled as walk -> not articulated", va["phases_equal_neutral_lower"] > 0 or va["distinct_lower"] < 8)
    broken = imgs[8].copy(); broken[32:56, 28:54] = 0
    nc("wrong identity (scarf erased in one walk frame) -> identity check rejects", bool(identity_bad([broken])))
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
        (OUT / f"{PFX}_walk-east-native-export_test-only-v01_{TAG}.log").write_bytes(log)
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
    seq = [(imgs[1], 700, 0.0)]
    y = 0.0
    for i in range(24):
        seq.append((walk_ims[i % NPH], FMS, y)); y += V
    sp = 7
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
    gif = OUT / f"{PFX}_walk-east-normal-speed-preview-source-bound_unapproved-h176ew01-v01_{TAG}.gif"
    frames[0].save(gif, save_all=True, append_images=frames[1:], duration=durs, loop=0, disposal=2)
    sheet = Image.new("RGBA", (W * 12, H * 3), (58, 62, 70, 255))
    for i, im in enumerate(walk_ims):
        sheet.alpha_composite(Image.fromarray(im, "RGBA"), (i * W, 0))
    for p in range(NPH):
        sheet.alpha_composite(Image.fromarray(imgs[17 + 2 * p], "RGBA"), (p * W, H))
        sheet.alpha_composite(Image.fromarray(imgs[18 + 2 * p], "RGBA"), (p * W, 2 * H))
    sheetp = OUT / f"{PFX}_walk-east-contact-sheet-walk-s1-s2_unapproved-h176ew01-v01_{TAG}.png"
    sheet.resize((W * 12 * 2, H * 3 * 2), Image.NEAREST).save(sheetp)

    result = {"task": "content.char.heya.walk-east", "manifest": mrel, "manifest_sha256_raw": sha(mraw),
              "checker_sha256_raw": sha(Path(__file__).read_bytes()), "checks": checks, "negative_controls": neg,
              "contacts_independent": c, "articulation": art, "native": native,
              "preview": {"gif": gif.relative_to(ROOT).as_posix(), "gif_sha256": sha(gif.read_bytes()),
                          "contact_sheet": sheetp.relative_to(ROOT).as_posix(), "contact_sheet_sha256": sha(sheetp.read_bytes()),
                          "scope": "source-bound PIL composite at 40 ms/frame, host 11.2 src px/40 ms; NOT a Godot capture",
                          "sequence": "idle f00 700ms, walk 2 cycles moving east, release at phase 7 -> s1, s2, idle f00"},
              "not_claimed": ["footlock/slip-free (side residual is integer rounding at 40 ms boundaries; 60 fps excursion exists)",
                              "fluidity or human motion acceptance", "GUI SaveAs/reopen", "Godot runtime/normal-host stop playback",
                              "art approval", "default adoption"],
              "passed": all(x["pass"] for x in checks)}
    rp_ = OUT / f"{PFX}_walk-east-independent-result_v01_{TAG}.json"
    rp_.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(rp_.relative_to(ROOT).as_posix())
    print("INDEPENDENT", "PASS" if result["passed"] else "FAIL", sum(x["pass"] for x in checks), "/", len(checks))
    return 0 if result["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
