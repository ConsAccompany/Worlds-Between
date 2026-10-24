"""Independent checker for Milo east walk/stop mew01 (content.char.milo.walk-east). NO author/engine imports.

Derived from the committed mnw01/msw01 independent checkers (same validators), rebound to the east SIDE view. Reads
only bytes on disk: source manifest, frame PNGs, animated PXO (data.json + raw cels), ORA, package JSONs and the
pinned Milo east neutral. Re-derives (does not trust author metadata):
  hashes, PXO cel recomposition == every PNG, frame order/tags, timing + exact boundaries (walk 480 ms cycle,
  stop settle 120 ms inclusive), feet from raw cels on sole row 103 (near foot = 'boots' cel, far foot =
  'far-limbs' cel), world-space planted-foot slip at 140 logical px/s at 40 ms boundaries, at every 1 ms
  hold/tick sample and at 60 fps ticks; stop-bridge grounded slip (host stopped); profile identity anchors
  (case left of pivot, wristband right of pivot, silver temple patch, profile eye), palette.
Negative controls (in memory): tampered PNG byte, tampered PXO cel, malformed stop JSON, zero/boundary duration,
bridge foot slide, planted-foot walk slide, wrong pivot, west/north entries, mirrored identity -> each REJECTED.
Native: Pixelorama --headless --export of the animated PXO with isolated XDG dirs, 90 s deadline; export equality
and application diagnostics are reported separately; GUI SaveAs/reopen is NOT verified.
Preview: source-bound normal-speed GIF (40 ms frames, host 140 logical px/s moving screen-right) - not a Godot capture.

python -X utf8 -I <this> --out outputs/milo-ew01/<new dir>
"""
import argparse, hashlib, io, json, os, re, signal, subprocess, time, zipfile
from pathlib import Path
import numpy as np
from PIL import Image

ROOT = Path(__file__).resolve().parent.parent
TAG = "20261024-061500-3e1a5c07"
PFX = "rpg-2-star-ocean-the-second_milo"
D = "east"
OUTROOT = "outputs/milo-ew01"
MAN = OUTROOT + "/rpg-2-star-ocean-the-second_milo_walk-source-manifest_unapproved-mew01-v01_20261024-061500-"
NEUTRAL = ("game/assets/characters/milo-native-v01/east/rpg-2-star-ocean-the-second_milo_east-static_unapproved-v01_20261024-000137-820dcbf2.png",
           "af45b51d44c0b409267c2995ec196593cbf0fca6cbb178c01b65e6f0d749e070")
PALFILE = ("game/assets/characters/milo-native-v01/east/rpg-2-star-ocean-the-second_milo_east-palette_unapproved-v01_20261024-000137-29b43d49.json",
           "c322e69c1ca22a79347e1981d82bc5d4cab6b8e4dc901a3a88add70ff3b01333")
W, H, SOLE, NPH, FMS, HOST = 80, 112, 103, 12, 40, 140.0
V = HOST * FMS / 1000 * 2           # 11.2 source texels per 40 ms at density 2
IDLE_MS = [700, 200, 400, 200]
LAYERS = ["far-limbs", "boots", "trousers", "undershirt", "coat", "belt", "case", "strap", "arms", "wristband", "face", "hair", "guides"]


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


def foot(cel):
    """(heel_x, toe_x) on the sole row for a facing-east foot, or None if lifted."""
    x = np.flatnonzero(cel[SOLE, :, 3] == 255)
    return (int(x.min()), int(x.max())) if len(x) else None


def pxo_frames(pxo):
    z = zipfile.ZipFile(io.BytesIO(pxo))
    dj = json.loads(z.read("data.json"))
    names = [l["name"] for l in dj["layers"]]
    n = len(dj["frames"])
    cel = lambda f, li: np.frombuffer(z.read(f"image_data/frames/{f + 1}/layer_{li + 1}"), np.uint8).reshape(H, W, 4)
    comps = [over([cel(f, li) for li, nm in enumerate(names) if nm != "guides"]) for f in range(n)]
    layer = lambda nm: [cel(f, names.index(nm)) for f in range(n)] if nm in names else []
    return dj, names, comps, {k: layer(k) for k in ("boots", "far-limbs", "arms", "wristband", "case")}


def rgb(hexs):
    return tuple(int(hexs[i:i + 2], 16) for i in (0, 2, 4))


# ----------------------------------------------------------------------------- pure validators (reused by controls)
def v_stop(stop, png_names):
    errs = []
    if stop.get("frame_ms") != FMS or stop.get("settle_ms_inclusive") != 3 * FMS or stop.get("runtime_default") is not False:
        errs.append("stop timing/default fields")
    if stop.get("pivot") != [40, 104] or stop.get("logical_height") != 48:
        errs.append("stop pivot/height")
    pb = stop.get("phase_bridges", {})
    if list(pb) != [D] or sorted(pb[D]) != sorted(f"phase{p}" for p in range(NPH)):
        errs.append("stop phases/direction scope")
    else:
        for p in range(NPH):
            s = pb[D][f"phase{p}"]
            if len(s) != 4 or s[0] != {"ref": "walk", "index": p, "k": 0.0} or s[-1] != {"ref": "idle", "index": 0, "k": 1.0}:
                errs.append(f"bridge phase{p} endpoints")
            elif any(x.get("file", "").rsplit("/", 1)[-1] not in png_names for x in s[1:3]):
                errs.append(f"bridge phase{p} frame file")
    return errs


def v_timing(ss):
    errs = []
    idle = [f["duration_ms"] for f in ss["actions"]["idle"].get(D, [])]
    walk = [f["duration_ms"] for f in ss["actions"]["walk"].get(D, [])]
    if idle != IDLE_MS:
        errs.append(f"idle durations {idle}")
    if walk != [FMS] * NPH:
        errs.append(f"walk durations {walk}")
    if not all(isinstance(x, int) and x > 0 for x in idle + walk):
        errs.append("non-positive duration")
    if set(ss["actions"]["idle"]) != {D} or set(ss["actions"]["walk"]) != {D}:
        errs.append("direction scope")
    if ss.get("pivot") != [40, 104] or ss.get("frame_size") != [W, H] or ss.get("density") != 2:
        errs.append("contract")
    return errs


def v_identity(im, P):
    """Profile facing screen right: white case + green cross LEFT of the pivot column (x 22..40, rows 60..79),
    green wristband RIGHT of it (x 41..61, rows 56..68), silver temple patch and green profile eye present."""
    m = im[..., 3] == 255
    case = {tuple(v) for v in im[60:80, 22:41][m[60:80, 22:41]][:, :3]}
    wb = {tuple(v) for v in im[56:69, 41:62][m[56:69, 41:62]][:, :3]}
    allc = {tuple(v) for v in im[m][:, :3]}
    return {P["g2"], P["w1"]} <= case and bool({P["g1"], P["g2"]} & wb) and P["a2"] in allc and P["e2"] in allc


def v_endpoint(s2_cels, s2_img, neutral_img):
    """s2 -> idle f00 (exact static bytes, whose 'boots' cel holds BOTH feet, so cel-split heel/toe are not comparable):
    profile geometry on the sole row: the neutral front edge is the near toe and the back edge is the set-back far
    heel. A grounded s2 near foot's toe must equal the neutral front edge, a grounded s2 far foot's heel the neutral
    back edge, and each grounded foot's sole extent must be opaque in the neutral sole row. Pixel equality is NOT
    used: a lifted near foot in s2 uncovers far-leg fill that the landed near boot hides again (occlusion, not slip).
    Returns summed texel error (0 = no slip at settle)."""
    del s2_img
    xs = np.flatnonzero(neutral_img[SOLE, :, 3] == 255)
    back, front = int(xs.min()), int(xs.max())
    bad = 0
    for k, cel in enumerate(s2_cels):
        f = foot(cel)
        if f is None:
            continue
        bad += abs(f[1] - front) if k == 0 else abs(f[0] - back)
        bad += int((neutral_img[SOLE, f[0]:f[1] + 1, 3] != 255).sum())
    return bad


def frame_at(durs, t):
    t %= sum(durs)
    acc = 0
    for i, d in enumerate(durs):
        if t < acc + d:
            return i
        acc += d


def v_contacts(walk_feet, bridge_feet, neutral_feet):
    """walk_feet[p] = (A, B) each (heel_x, toe_x) or None. World x = screen x + host advance (east = +x)."""
    pairs, worst = [], 0.0
    for p in range(NPH):
        n = (p + 1) % NPH
        for k in range(2):
            a, b = walk_feet[p][k], walk_feet[n][k]
            if a and b:
                s = round(max(abs(b[0] - a[0] + V), abs(b[1] - a[1] + V)), 3)
                worst = max(worst, s)
                pairs.append({"from": p, "foot": "AB"[k], "world_slip_src": s})
    # hold/tick sampling: every 1 ms over two cycles, and 60 fps ticks; frame = floor(t/40 ms), host continuous
    def excursion(times):
        best = 0.0
        for k in range(2):
            run = []
            for t in times + [None]:
                f = walk_feet[int(t // FMS) % NPH][k] if t is not None else None
                if f:
                    w = 2 * HOST * t / 1000.0
                    run.append((f[0] + w, f[1] + w))
                else:
                    if len(run) > 1:
                        best = max(best, max(r[0] for r in run) - min(r[0] for r in run), max(r[1] for r in run) - min(r[1] for r in run))
                    run = []
        return round(best, 3)
    ms = [float(t) for t in range(2 * NPH * FMS)]
    fps60 = [i * 1000 / 60 for i in range(int(2 * NPH * FMS * 60 / 1000))]
    edges = {}
    for t in (0, 39, 40, 79, 80, 119, 120, 159, 160):                   # first near stance p0..p3 hold starts/ends
        f = walk_feet[int(t // FMS) % NPH][0]
        edges[t] = None if f is None else round(f[1] + 2 * HOST * t / 1000.0, 3)
    stop_slip = []
    for p in range(NPH):
        seq = [walk_feet[p], bridge_feet[p][0], bridge_feet[p][1]]   # s2 -> idle f00 is checked by v_endpoint (pixels)
        for a, b in zip(seq, seq[1:]):
            for k in range(2):
                if a[k] and b[k]:
                    stop_slip.append(max(abs(a[k][0] - b[k][0]), abs(a[k][1] - b[k][1])))
    grounded = [sum(1 for r in walk_feet if r[k]) for k in range(2)]
    return {"grounded_phases_per_foot": grounded, "flight_phases": [p for p in range(NPH) if not walk_feet[p][0] and not walk_feet[p][1]],
            "grounded_pairs": len(pairs), "walk_max_world_slip_src_at_40ms_boundaries": worst,
            "walk_max_world_slip_logical_at_40ms_boundaries": round(worst / 2, 3),
            "planted_world_excursion_src_1ms_hold_samples": excursion(ms),
            "planted_world_excursion_src_60fps_ticks": excursion(fps60),
            "near_toe_world_src_at_hold_edges_ms": edges,
            "stop_bridge_grounded_slip_src_max": max(stop_slip) if stop_slip else 0}


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
        print(("PASS " if ok else "FAIL ") + name, "" if detail is None else json.dumps(detail)[:220], flush=True)

    mans = sorted((ROOT / OUTROOT).glob(Path(MAN).name + "*.json"))
    ck("exactly one source manifest", len(mans) == 1, [m.name for m in mans])
    mrel = mans[0].relative_to(ROOT).as_posix()
    mraw = rd(mrel)
    m = json.loads(mraw)
    e = m["directions"][D]
    ck("manifest scope: east only, task content.char.milo.walk-east, UNAPPROVED", list(m["directions"]) == [D]
       and m["task_ids"] == ["content.char.milo.walk-east"] and "UNAPPROVED" in m["status"])
    ck("neutral Milo east PNG pin", sha(rd(NEUTRAL[0])) == NEUTRAL[1])
    ck("palette file pin", sha(rd(PALFILE[0])) == PALFILE[1])
    P = {k: rgb(v) for k, v in json.loads(rd(PALFILE[0]))["colors"].items()}
    pal = set(P.values())
    pins = m["source_inputs"]["neutral_editables_pinned"]
    ck("neutral editable pins byte-exact (east PXO/ORA/manifest/palette)", len(pins) == 4 and all(sha(rd(r)) == h for r, h in pins.items()), len(pins))
    tool_refs = [("reused_engine", m["reused_engine"]["file"], m["reused_engine"]["sha256_text_lf_v1"]),
                 ("reused_helpers", m["reused_helpers"]["file"], m["reused_helpers"]["sha256_text_lf_v1"]),
                 ("tool", m["tool"]["file"], m["tool"]["sha256_text_lf_v1"])] + \
                [(k, v["file"], v["sha256_text_lf_v1"]) for k, v in m["source_inputs"].items() if isinstance(v, dict) and "sha256_text_lf_v1" in v]
    for key, f, h in tool_refs:
        ck(f"{key} text_lf_v1 hash matches tool file", sha(rd(f).replace(b"\r\n", b"\n").replace(b"\r", b"\n")) == h, f)
    stop_frames = [s for p in range(NPH) for s in e["stop_bridges"][f"phase{p}"] if "file" in s]
    order = [e["static"]] + e["idle"] + e["walk"] + stop_frames
    ck("all 41 frame PNG raw hashes match manifest", all(sha(rd(x["file"])) == x["sha256"] for x in order) and len(order) == 41, len(order))
    imgs = [dec(rd(x["file"])) for x in order]
    bad = [i for i, im in enumerate(imgs) if im.shape != (H, W, 4) or set(np.unique(im[..., 3])) - {0, 255}
           or im[0, :, 3].any() or im[-1, :, 3].any() or im[:, 0, 3].any() or im[:, -1, 3].any()
           or {tuple(c) for c in im[im[..., 3] == 255][:, :3]} - pal]
    ck("frames 80x112, binary alpha, clear border, palette subset of pinned Milo palette", not bad, bad[:5])
    ck("static and idle f00 are the neutral bytes", rd(order[0]["file"]) == rd(NEUTRAL[0]) == rd(order[1]["file"]))
    pxo = rd(e["pxo"]["file"])
    ck("PXO raw hash", sha(pxo) == e["pxo"]["sha256"])
    dj, names, comps, cels = pxo_frames(pxo)
    ck("PXO 41 frames, layers far-limbs + 11 Milo roles + guides", len(comps) == 41 and names == LAYERS, names)
    mism = [i for i in range(min(41, len(comps))) if not np.array_equal(comps[i], imgs[i])]
    ck("PXO cels recompose to every frame PNG (independent alpha-over)", not mism, mism[:5])
    tags = {t["name"]: (t["from"], t["to"]) for t in dj.get("tags", [])}
    ck("PXO tags east-idle 2-5, east-walk 6-17, 12 stop tags", tags.get("east-idle") == (2, 5) and tags.get("east-walk") == (6, 17)
       and all(tags.get(f"east-stop-p{p:02d}") == (18 + 2 * p, 19 + 2 * p) for p in range(NPH)) and len(tags) == 14, tags.get("east-walk"))
    with zipfile.ZipFile(io.BytesIO(rd(e["ora"]["file"]))) as z:
        ora_ok = sha(rd(e["ora"]["file"])) == e["ora"]["sha256"] and z.read("mergedimage.png") == rd(NEUTRAL[0]) and \
            np.array_equal(over([dec(z.read(f"data/{n}.png")) for n in names[1:-1]]), imgs[0])
    ck("ORA raw hash; merged == neutral bytes; role layers recompose to neutral", ora_ok)
    pkg = m["package"]
    ssb = rd(pkg["sprite_set"])
    ck("sprite set raw hash", sha(ssb) == pkg["sprite_set_sha256"])
    ss = json.loads(ssb)
    te = v_timing(ss)
    ck("sprite set timing/contract/east-only", not te, te)
    stb = rd(pkg["stop_supplemental"])
    ck("stop supplemental text_lf_v1 hash", sha(stb.replace(b"\r\n", b"\n")) == pkg["stop_supplemental_sha256_text_lf_v1"])
    stop = json.loads(stb)
    pkgdir = Path(pkg["sprite_set"]).parent.as_posix()
    png_names = {p.name for p in (ROOT / pkgdir / "png").glob("*.png")}
    se = v_stop(stop, png_names)
    ck("stop supplemental structure (12 phase bridges [walk p, s1, s2, idle f00], 40 ms, settle 120 inclusive, non-default)", not se, se)
    copies = [f["file"] for act in ss["actions"].values() for f in act[D]] + \
             ["png/" + s["file"].rsplit("/", 1)[-1] for v in stop["phase_bridges"][D].values() for s in v if "file" in s]
    ck("package PNG copies byte-equal to source frames", all(rd(f"{pkgdir}/{c}") == rd(f"{OUTROOT}/{c}") for c in copies), len(copies))
    sj = [(s["file"].rsplit("/", 1)[-1], s["sha256"]) for p in range(NPH) for s in stop["phase_bridges"][D][f"phase{p}"] if "file" in s]
    ck("stop JSON bridge frames == manifest bridge frames, in order, hashes match bytes",
       sj == [(x["file"].rsplit("/", 1)[-1], x["sha256"]) for x in stop_frames] and all(sha(rd(f"{pkgdir}/png/{n}")) == h for n, h in sj), len(sj))
    walk_d = [f["duration_ms"] for f in ss["actions"]["walk"][D]]
    bnd = {t: frame_at(walk_d, t) for t in (0, 39, 40, 439, 440, 479, 480, 481)}
    ck("walk timing boundaries: 39->p0 40->p1 479->p11 480->p0 (cycle 480 ms)",
       bnd == {0: 0, 39: 0, 40: 1, 439: 10, 440: 11, 479: 11, 480: 0, 481: 0}, bnd)
    idle_b = {t: frame_at(IDLE_MS, t) for t in (699, 700, 899, 900, 1299, 1300, 1499, 1500)}
    ck("idle timing boundaries (700/200/400/200, loop 1500 ms)", idle_b == {699: 0, 700: 1, 899: 1, 900: 2, 1299: 2, 1300: 3, 1499: 3, 1500: 0}, idle_b)
    seq_t = lambda t: min(int(t // FMS), 3)
    sb = {t: seq_t(t) for t in (0, 39, 40, 79, 80, 119, 120, 1000)}
    ck("stop bridge boundaries: release t0 walk p; 40 s1; 80 s2; 120 (inclusive) idle f00 held",
       sb == {0: 0, 39: 0, 40: 1, 79: 1, 80: 2, 119: 2, 120: 3, 1000: 3}, sb)
    ck("every bridge endpoint resolves to exact walk p / neutral idle f00 bytes (stop settles exactly to neutral from all 12 phases)",
       all(rd(e["walk"][s[0]["index"]]["file"]) == rd(order[5 + p]["file"]) and rd(e["idle"][s[-1]["index"]]["file"]) == rd(NEUTRAL[0])
           for p in range(NPH) for s in [e["stop_bridges"][f"phase{p}"]]))
    # contacts from raw cels: near foot = boots cel, far foot = far-limbs cel
    ft = [(foot(cels["boots"][i]), foot(cels["far-limbs"][i])) for i in range(41)]
    walk_feet = ft[5:17]
    br_feet = [(ft[17 + 2 * p], ft[18 + 2 * p]) for p in range(NPH)]
    c = v_contacts(walk_feet, br_feet, ft[0])
    ck("each foot grounded exactly 4 of 12 phases", c["grounded_phases_per_foot"] == [4, 4], c["grounded_phases_per_foot"])
    ck("side planted foot world slip at 40 ms boundaries <= 1 source texel (frozen jexplore39 gate; rounding of 11.2)",
       c["walk_max_world_slip_src_at_40ms_boundaries"] <= 1.0, c["walk_max_world_slip_src_at_40ms_boundaries"])
    ck("stop bridges walk p -> s1 -> s2: grounded foot never moves (host stopped; cel toe and heel)", c["stop_bridge_grounded_slip_src_max"] == 0, c["stop_bridge_grounded_slip_src_max"])
    s2c = lambda p: (cels["boots"][18 + 2 * p], cels["far-limbs"][18 + 2 * p])
    ep = [v_endpoint(s2c(p), imgs[18 + 2 * p], imgs[1]) for p in range(NPH)]
    c["stop_endpoint_s2_to_idle_f00_mismatched_texels"] = ep
    ck("stop bridges s2 -> idle f00: grounded s2 foot texels reappear unchanged in neutral (all 12 phases)", not any(ep), ep)
    claimed = m["contact_check"][D]
    ck("independent contacts agree with author claims (boundary slip, flight phases, stop 0)",
       abs(claimed["walk_max_world_slip_src_at_40ms_boundaries"] - c["walk_max_world_slip_src_at_40ms_boundaries"]) < 1e-6
       and claimed["flight_phases"] == c["flight_phases"] and claimed["stop_bridge_grounded_slip_src_max"] == c["stop_bridge_grounded_slip_src_max"] == 0
       and not any(ep),
       {"claimed": claimed["walk_max_world_slip_src_at_40ms_boundaries"], "independent": c["walk_max_world_slip_src_at_40ms_boundaries"]})
    idm = [i for i, im in enumerate(imgs) if not v_identity(im, P)]
    ck("identity: white case w/ green cross (left of pivot), green wristband (right of pivot), silver patch, profile eye in all frames", not idm, idm[:5])
    det = []
    for i in range(41):
        wb, ar = cels["wristband"][i], cels["arms"][i]
        wy = np.flatnonzero(wb[..., 3].any(1)); wx = np.flatnonzero(wb[..., 3].any(0))
        if not (len(wy) == 3 and ar[wy.min() - 1, wx.min():wx.max() + 1, 3].any() and ar[wy.max() + 1, wx.min():wx.max() + 1, 3].any()):
            det.append(i)
    ck("wristband cel attached to forearm texels directly above and below in every frame (raw cels)", not det, det[:5])
    case0 = cels["case"][0]
    rig = [i for i in range(41) if not any(np.array_equal(cels["case"][i], np.roll(case0, dy, axis=0)) for dy in (0, 1))]
    ck("case cel is the neutral case shifted by 0/+1 row only (rides torso bob)", not rig, rig[:5])
    ck("top row never above neutral row 8; soles never below 103",
       all(np.flatnonzero(im[..., 3].any(1)).min() >= 8 and np.flatnonzero(im[..., 3].any(1)).max() <= SOLE for im in imgs))
    disclosed = {"planted_world_excursion_src_1ms_hold_samples": c["planted_world_excursion_src_1ms_hold_samples"],
                 "planted_world_excursion_logical_1ms_hold_samples": round(c["planted_world_excursion_src_1ms_hold_samples"] / 2, 3),
                 "planted_world_excursion_src_60fps_ticks": c["planted_world_excursion_src_60fps_ticks"],
                 "near_toe_world_src_at_hold_edges_ms": c["near_toe_world_src_at_hold_edges_ms"],
                 "flight_phases": c["flight_phases"],
                 "status": "RESIDUAL, NOT A PASS: within each held 40 ms frame the host moves continuously, so the planted foot "
                           "slides forward up to the listed excursion and snaps back at the next tick; not footlocked/slip-free"}
    print("DISCLOSED_RESIDUAL", json.dumps(disclosed), flush=True)

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
            d_ = zin.read(info.filename)
            if info.filename == "image_data/frames/9/layer_2":
                arr = np.frombuffer(d_, np.uint8).reshape(H, W, 4).copy(); arr[SOLE, 30] = [255, 0, 0, 255]; d_ = arr.tobytes()
            zo.writestr(info, d_)
    _, _, tcomps, _ = pxo_frames(zb.getvalue())
    nc("tampered PXO cel -> recomposition mismatch", not np.array_equal(tcomps[8], imgs[8]))
    bs = json.loads(stb); bs["phase_bridges"][D]["phase3"][-1] = {"ref": "idle", "index": 1, "k": 1.0}
    nc("malformed stop JSON (bridge ends on idle f01) -> rejected", bool(v_stop(bs, png_names)))
    bs = json.loads(stb); bs["frame_ms"] = 39
    nc("stop frame_ms 39 -> rejected", bool(v_stop(bs, png_names)))
    bs = json.loads(stb); bs["settle_ms_inclusive"] = 119
    nc("stop settle 119 ms -> rejected", bool(v_stop(bs, png_names)))
    bs = json.loads(stb); bs["phase_bridges"]["west"] = {}
    nc("stop JSON with west entry (paused direction) -> rejected", bool(v_stop(bs, png_names)))
    bs = json.loads(stb); bs["phase_bridges"] = {"north": bs["phase_bridges"][D]}
    nc("stop JSON relabelled north -> rejected", bool(v_stop(bs, png_names)))
    bs = json.loads(stb); bs["phase_bridges"][D]["phase0"][1]["file"] = "png/missing.png"
    nc("stop JSON with missing bridge frame -> rejected", bool(v_stop(bs, png_names)))
    bs = json.loads(stb); del bs["phase_bridges"][D]["phase11"]
    nc("stop JSON missing phase11 -> rejected", bool(v_stop(bs, png_names)))
    nc("truncated (malformed) stop JSON bytes -> parse rejected", _parse_fails(stb[: len(stb) // 2]))
    bt = json.loads(ssb); bt["actions"]["walk"][D][5]["duration_ms"] = 0
    nc("walk duration 0 -> rejected", bool(v_timing(bt)))
    bt = json.loads(ssb); bt["actions"]["walk"][D][5]["duration_ms"] = 41
    nc("walk duration 41 (boundary drift) -> rejected", bool(v_timing(bt)))
    bt = json.loads(ssb); bt["actions"]["idle"][D][0]["duration_ms"] = 699
    nc("idle f00 duration 699 -> rejected", bool(v_timing(bt)))
    bt = json.loads(ssb); bt["pivot"] = [40, 103]
    nc("wrong pivot -> rejected", bool(v_timing(bt)))
    bt = json.loads(ssb); bt["actions"]["walk"]["west"] = bt["actions"]["walk"][D]
    nc("sprite set with extra west entry -> rejected", bool(v_timing(bt)))
    slid = [((x[0][0] + 1, x[0][1] + 1) if x[0] else None, x[1]) for x, _ in br_feet]
    nc("bridge s1 near foot slid 1 texel -> stop slip detected",
       v_contacts(walk_feet, [(s, b[1]) for s, b in zip(slid, br_feet)], ft[0])["stop_bridge_grounded_slip_src_max"] > 0)
    for p_ in (0, 6):
        cs = list(s2c(p_))
        k_ = 0 if foot(cs[0]) else 1                                # slide the foot that is GROUNDED in this s2
        cs[k_] = np.roll(cs[k_], -1, axis=1)
        nc(f"stop p{p_:02d} s2 grounded {'near' if k_ == 0 else 'far'} foot cel slid 1 texel -> endpoint slip detected",
           v_endpoint(tuple(cs), over(cs), imgs[1]) > 0)
    wf = list(walk_feet); wf[2] =((wf[2][0][0] + 2, wf[2][0][1] + 2), wf[2][1])
    nc("walk p02 planted near foot moved 2 texels -> boundary slip > 1 detected", v_contacts(wf, br_feet, ft[0])["walk_max_world_slip_src_at_40ms_boundaries"] > 1.0)
    wf = [(f[1], f[0]) for f in walk_feet]
    nc("west-style reversed travel (host -x) -> boundary slip > 1 detected",
       v_contacts([((W - 1 - f[0][1], W - 1 - f[0][0]) if f[0] else None, (W - 1 - f[1][1], W - 1 - f[1][0]) if f[1] else None) for f in walk_feet],
                  br_feet, ft[0])["walk_max_world_slip_src_at_40ms_boundaries"] > 1.0)
    nc("horizontally mirrored neutral (west-style, case/wristband swapped) -> identity rejected", not v_identity(imgs[0][:, ::-1].copy(), P))
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
        (OUT / f"{PFX}_walk-east-native-export_test-only-v01_{TAG}.log").write_bytes(log)
        got = sorted(run.glob("*.png"), key=lambda q: [int(x) if x.isdigit() else x for x in re.split(r"(\d+)", q.name)])
        exact = sum(1 for i, q in enumerate(got) if i < 41 and np.array_equal(np.asarray(Image.open(q).convert("RGBA")), imgs[i]))
        text = log.decode("utf-8", "replace")
        diags = [ln for ln in text.splitlines() if any(s in ln for s in ("ERROR:", "SCRIPT ERROR", "Parse Error", "WARNING:"))]
        native = {"run": True, "command": cmd, "exit": p.returncode, "timeout": to, "elapsed_s": round(time.monotonic() - t0, 2),
                  "frames_expected": 41, "frames_emitted": len(got), "frames_rgba_exact": exact,
                  "source_unchanged": sha(src.read_bytes()) == before, "diagnostics": diags[:20],
                  "application_clean": p.returncode == 0 and not to and not diags, "gui_saveas_reopen_verified": False}
        ck("native Pixelorama export: 41/41 frames RGBA-exact, exit 0, no timeout, source unchanged",
           p.returncode == 0 and not to and len(got) == 41 == exact and native["source_unchanged"],
           {k: native[k] for k in ("exit", "timeout", "frames_emitted", "frames_rgba_exact")})
        print("APPLICATION_DIAGNOSTICS (separate, not an export-equality gate):", len(diags), flush=True)

    # ------------------------------------------------------------------ source-bound normal-speed preview
    S = 3
    walk_ims = imgs[5:17]
    travel = 2 * NPH * V + V
    x = 0.0
    seq = [(imgs[1], 700, x)]
    for i in range(24):                                           # 2 walk cycles moving east at host speed
        seq.append((walk_ims[i % NPH], FMS, x)); x += V
    sp = 7                                                        # explicit release at phase 7
    seq.append((walk_ims[sp], FMS, x))
    seq += [(imgs[17 + 2 * sp], FMS, x), (imgs[18 + 2 * sp], FMS, x), (imgs[1], 900, x)]
    cw = int(W + travel + 16)
    frames, durs = [], []
    for im, d_, xx in seq:
        cv = Image.new("RGBA", (cw, H + 8), (58, 62, 70, 255))
        g_ = Image.new("RGBA", (1, 4), (90, 96, 108, 255))
        for gx in range(0, cw, 22):
            cv.paste(g_, (gx, SOLE + 1))
        cv.alpha_composite(Image.fromarray(im, "RGBA"), (8 + int(round(xx)), 0))
        frames.append(cv.resize((cw * S, (H + 8) * S), Image.NEAREST).convert("P", palette=Image.ADAPTIVE, colors=255))
        durs.append(d_)
    gif = OUT / f"{PFX}_walk-east-normal-speed-preview-source-bound_unapproved-mew01-v01_{TAG}.gif"
    frames[0].save(gif, save_all=True, append_images=frames[1:], duration=durs, loop=0, disposal=2)
    sheet = Image.new("RGBA", (W * 12, H * 3), (58, 62, 70, 255))
    for i, im in enumerate(walk_ims):
        sheet.alpha_composite(Image.fromarray(im, "RGBA"), (i * W, 0))
    for p in range(NPH):
        sheet.alpha_composite(Image.fromarray(imgs[17 + 2 * p], "RGBA"), (p * W, H))
        sheet.alpha_composite(Image.fromarray(imgs[18 + 2 * p], "RGBA"), (p * W, 2 * H))
    sheetp = OUT / f"{PFX}_walk-east-contact-sheet-walk-s1-s2_unapproved-mew01-v01_{TAG}.png"
    sheet.resize((W * 12 * 2, H * 3 * 2), Image.NEAREST).save(sheetp)

    result = {"task": "content.char.milo.walk-east", "manifest": mrel, "manifest_sha256_raw": sha(mraw),
              "checker_sha256_raw": sha(Path(__file__).read_bytes()), "checks": checks, "negative_controls": neg,
              "contacts_independent": c, "disclosed_residual": disclosed, "native": native,
              "preview": {"gif": gif.relative_to(ROOT).as_posix(), "gif_sha256": sha(gif.read_bytes()),
                          "contact_sheet": sheetp.relative_to(ROOT).as_posix(), "contact_sheet_sha256": sha(sheetp.read_bytes()),
                          "scope": "source-bound PIL composite at 40 ms/frame, host 11.2 src px/40 ms; NOT a Godot capture",
                          "sequence": "idle f00 700ms, walk 2 cycles moving east (screen right), release at phase 7 -> s1, s2, idle f00"},
              "not_claimed": ["footlock/slip-free (within-hold residual disclosed above)", "fluidity or human motion acceptance",
                              "GUI SaveAs/reopen", "Godot runtime/normal-host stop playback", "art approval", "four-direction loader readiness"],
              "passed": all(x["pass"] for x in checks)}
    rp_ = OUT / f"{PFX}_walk-east-independent-result_v01_{TAG}.json"
    rp_.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(rp_.relative_to(ROOT).as_posix())
    print("INDEPENDENT", "PASS" if result["passed"] else "FAIL", sum(x["pass"] for x in checks), "/", len(checks))
    return 0 if result["passed"] else 1


def _parse_fails(b):
    try:
        json.loads(b)
        return False
    except ValueError:
        return True


if __name__ == "__main__":
    raise SystemExit(main())
