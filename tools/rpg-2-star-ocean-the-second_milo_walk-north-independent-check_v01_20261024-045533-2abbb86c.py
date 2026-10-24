"""Independent checker for Milo north walk/stop mnw01 (content.char.milo.walk-north). NO author/engine imports.

Derived from the committed msw01 south independent checker (same validators), rebound to north. Reads only bytes
on disk: source manifest, frame PNGs, animated PXO (data.json + raw cels), ORA, package JSONs and the pinned Milo
north neutral. Re-derives (does not trust author metadata):
  hashes, PXO cel recomposition == every PNG, frame order/tags, timing + exact boundaries (walk 480 ms cycle,
  stop settle 120 ms inclusive), feet from raw boots cel sole row 103 split x40 (in-place back residual = host
  advance 11.2 src/40 ms, stop-bridge grounded slip), back-view identity anchors (case screen right, wristband
  screen left), no face features, palette.
Negative controls (in memory): tampered PNG byte, tampered PXO cel, malformed stop JSON, zero/boundary duration,
bridge foot slide, wrong pivot, south/west entries, wrong-side identity -> each must be REJECTED.
Native: Pixelorama --headless --export of the animated PXO with isolated XDG dirs, 90 s deadline; export equality
and application diagnostics are reported separately; GUI SaveAs/reopen is NOT verified.
Preview: source-bound normal-speed GIF (40 ms frames, host 140 logical px/s moving up-screen) - not a Godot capture.

python -X utf8 -I <this> --out outputs/milo-nw01/<new dir>
"""
import argparse, hashlib, io, json, os, re, signal, subprocess, time, zipfile
from pathlib import Path
import numpy as np
from PIL import Image

ROOT = Path(__file__).resolve().parent.parent
TAG = "20261024-045533-2abbb86c"
PFX = "rpg-2-star-ocean-the-second_milo"
D = "north"
OUTROOT = "outputs/milo-nw01"
MAN = OUTROOT + "/rpg-2-star-ocean-the-second_milo_walk-source-manifest_unapproved-mnw01-v01_20261024-045533-"
NEUTRAL = ("game/assets/characters/milo-native-v01/north/rpg-2-star-ocean-the-second_milo_north-static_unapproved-v01_20261023-225642-5968ba0c.png",
           "cf1e559885f2a87c31a3c6cf9feee953d95c8c1ca138ecd9bd8d6838bee8da61")
PALFILE = ("game/assets/characters/milo-native-v01/north/rpg-2-star-ocean-the-second_milo_north-palette_unapproved-v01_20261023-225642-a3a9c89f.json",
           "e837c5f76ad17caa7d2b9c269cec261c4813dc2238d6297514ae3d3aaf02554d")
W, H, SOLE, NPH, FMS, HOST = 80, 112, 103, 12, 40, 140.0
V = HOST * FMS / 1000 * 2           # 11.2 source texels per 40 ms at density 2
IDLE_MS = [700, 200, 400, 200]
GREEN = {(0x74, 0xd9, 0x3a), (0xc6, 0xf7, 0x6a)}
G2, W1 = (0x74, 0xd9, 0x3a), (0xfc, 0xfc, 0xfa)
EYE = {(0xf6, 0xf7, 0xf2), (0x3e, 0x8a, 0x3c), (0x9a, 0x52, 0x43)}


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


def pxo_frames(pxo):
    z = zipfile.ZipFile(io.BytesIO(pxo))
    dj = json.loads(z.read("data.json"))
    names = [l["name"] for l in dj["layers"]]
    n = len(dj["frames"])
    cel = lambda f, li: np.frombuffer(z.read(f"image_data/frames/{f + 1}/layer_{li + 1}"), np.uint8).reshape(H, W, 4)
    comps = [over([cel(f, li) for li, nm in enumerate(names) if nm != "guides"]) for f in range(n)]
    layer = lambda nm: [cel(f, names.index(nm)) for f in range(n)]
    return dj, names, comps, layer("boots"), layer("face")


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


def v_identity(im):
    """Back view: white case + green cross on screen RIGHT, green wristband on screen LEFT."""
    m = im[..., 3] == 255
    right = {tuple(v) for v in im[58:80, 50:70][m[58:80, 50:70]][:, :3]}
    left = {tuple(v) for v in im[55:70, 16:30][m[55:70, 16:30]][:, :3]}
    return {G2, W1} <= right and bool(left & GREEN)


def frame_at(durs, t):
    t %= sum(durs)
    acc = 0
    for i, d in enumerate(durs):
        if t < acc + d:
            return i
        acc += d


def v_contacts(walk_boots, bridges_boots, neutral_boots):
    rec = [feet(b) for b in walk_boots]
    pairs = []
    for p in range(NPH):
        for k in range(2):
            if rec[p][k] and rec[(p + 1) % NPH][k]:
                d = abs(rec[(p + 1) % NPH][k][0] - rec[p][k][0]) + abs(rec[(p + 1) % NPH][k][1] - rec[p][k][1])
                pairs.append({"from": p, "foot": "AB"[k], "screen_toe_heel_change_src": d, "world_slip_src": round(V + 0, 3)})
    stop_slip = []
    nf = feet(neutral_boots)
    for p in range(NPH):
        seq = [rec[p], feet(bridges_boots[p][0]), feet(bridges_boots[p][1]), nf]
        for a, b in zip(seq, seq[1:]):
            for k in range(2):
                if a[k] and b[k]:
                    stop_slip.append(max(abs(a[k][0] - b[k][0]), abs(a[k][1] - b[k][1])))
    grounded = [sum(1 for r in rec if r[k]) for k in range(2)]
    return {"grounded_phases_per_foot": grounded, "flight_phases": [p for p in range(NPH) if not rec[p][0] and not rec[p][1]],
            "grounded_pairs": len(pairs), "planted_screen_motion_src_max": max(x["screen_toe_heel_change_src"] for x in pairs),
            "back_inplace_world_slip_src_per_40ms": V if pairs else None, "back_inplace_world_slip_logical_per_40ms": V / 2 if pairs else None,
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
        print(("PASS " if ok else "FAIL ") + name, "" if detail is None else json.dumps(detail)[:200], flush=True)

    mans = sorted((ROOT / OUTROOT).glob(Path(MAN).name + "*.json"))
    ck("exactly one source manifest", len(mans) == 1, [m.name for m in mans])
    mrel = mans[0].relative_to(ROOT).as_posix()
    mraw = rd(mrel)
    m = json.loads(mraw)
    e = m["directions"][D]
    ck("manifest scope: north only, task content.char.milo.walk-north, UNAPPROVED", list(m["directions"]) == [D]
       and m["task_ids"] == ["content.char.milo.walk-north"] and "UNAPPROVED" in m["status"])
    # pins
    ck("neutral Milo north PNG pin", sha(rd(NEUTRAL[0])) == NEUTRAL[1])
    ck("palette file pin", sha(rd(PALFILE[0])) == PALFILE[1])
    pal = {tuple(int(v[i:i + 2], 16) for i in (0, 2, 4)) for v in json.loads(rd(PALFILE[0]))["colors"].values()}
    pins = m["source_inputs"]["neutral_editables_pinned"]
    ck("neutral editable pins byte-exact (north PXO/ORA/manifest/palette)", len(pins) == 4 and all(sha(rd(r)) == h for r, h in pins.items()), len(pins))
    tool_refs = [("reused_engine", m["reused_engine"]["file"], m["reused_engine"]["sha256_text_lf_v1"]),
                 ("reused_helpers", m["reused_helpers"]["file"], m["reused_helpers"]["sha256_text_lf_v1"]),
                 ("tool", m["tool"]["file"], m["tool"]["sha256_text_lf_v1"])] + \
                [(k, v["file"], v["sha256_text_lf_v1"]) for k, v in m["source_inputs"].items() if isinstance(v, dict) and "sha256_text_lf_v1" in v]
    for key, f, h in tool_refs:
        ck(f"{key} text_lf_v1 hash matches tool file", sha(rd(f).replace(b"\r\n", b"\n").replace(b"\r", b"\n")) == h, f)
    # frames
    stop_frames = [s for p in range(NPH) for s in e["stop_bridges"][f"phase{p}"] if "file" in s]
    order = [e["static"]] + e["idle"] + e["walk"] + stop_frames
    ok_hash = all(sha(rd(x["file"])) == x["sha256"] for x in order)
    ck("all 41 frame PNG raw hashes match manifest", ok_hash and len(order) == 41, len(order))
    imgs = [dec(rd(x["file"])) for x in order]
    bad = [i for i, im in enumerate(imgs) if im.shape != (H, W, 4) or set(np.unique(im[..., 3])) - {0, 255}
           or im[0, :, 3].any() or im[-1, :, 3].any() or im[:, 0, 3].any() or im[:, -1, 3].any()
           or {tuple(c) for c in im[im[..., 3] == 255][:, :3]} - pal]
    ck("frames 80x112, binary alpha, clear border, palette subset of pinned Milo palette", not bad, bad[:5])
    ck("static and idle f00 are the neutral bytes", rd(order[0]["file"]) == rd(NEUTRAL[0]) == rd(order[1]["file"]))
    # PXO
    pxo = rd(e["pxo"]["file"])
    ck("PXO raw hash", sha(pxo) == e["pxo"]["sha256"])
    dj, names, comps, boots, faces = pxo_frames(pxo)
    ck("PXO 41 frames, layers far-limbs + 11 Milo roles + guides",
       len(comps) == 41 and names == ["far-limbs", "boots", "trousers", "undershirt", "coat", "belt", "case", "strap", "arms", "wristband", "face", "hair", "guides"], names)
    mism = [i for i in range(min(41, len(comps))) if not np.array_equal(comps[i], imgs[i])]
    ck("PXO cels recompose to every frame PNG (independent alpha-over)", not mism, mism[:5])
    tags = {t["name"]: (t["from"], t["to"]) for t in dj.get("tags", [])}
    ck("PXO tags north-idle 2-5, north-walk 6-17, 12 stop tags", tags.get("north-idle") == (2, 5) and tags.get("north-walk") == (6, 17)
       and all(tags.get(f"north-stop-p{p:02d}") == (18 + 2 * p, 19 + 2 * p) for p in range(NPH)) and len(tags) == 14, tags.get("north-walk"))
    # ORA (neutral layered source)
    with zipfile.ZipFile(io.BytesIO(rd(e["ora"]["file"]))) as z:
        ora_ok = sha(rd(e["ora"]["file"])) == e["ora"]["sha256"] and z.read("mergedimage.png") == rd(NEUTRAL[0]) and \
            np.array_equal(over([dec(z.read(f"data/{n}.png")) for n in names[1:-1]]), imgs[0])
    ck("ORA raw hash; merged == neutral bytes; role layers recompose to neutral", ora_ok)
    # package + timing
    pkg = m["package"]
    ssb = rd(pkg["sprite_set"])
    ck("sprite set raw hash", sha(ssb) == pkg["sprite_set_sha256"])
    ss = json.loads(ssb)
    te = v_timing(ss)
    ck("sprite set timing/contract/north-only", not te, te)
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
    # stop bridge frame files in the stop JSON are exactly the manifest's bridge PNGs (hash-bound)
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
    # bridge endpoints by bytes: entry 0 == walk p frame, entry 3 == neutral
    ck("every bridge endpoint resolves to exact walk p / neutral idle f00 bytes",
       all(rd(e["walk"][s[0]["index"]]["file"]) == rd(order[5 + p]["file"]) and rd(e["idle"][s[-1]["index"]]["file"]) == rd(NEUTRAL[0])
           for p in range(NPH) for s in [e["stop_bridges"][f"phase{p}"]]))
    # contacts (raw boots cels)
    walk_boots = boots[5:17]
    br_boots = [(boots[17 + 2 * p], boots[18 + 2 * p]) for p in range(NPH)]
    c = v_contacts(walk_boots, br_boots, boots[0])
    ck("each foot grounded exactly 4 of 12 phases", c["grounded_phases_per_foot"] == [4, 4], c["grounded_phases_per_foot"])
    ck("planted foot screen position constant while grounded (in place)", c["planted_screen_motion_src_max"] == 0, c["planted_screen_motion_src_max"])
    ck("stop bridges: grounded foot never moves (host stopped)", c["stop_bridge_grounded_slip_src_max"] == 0, c["stop_bridge_grounded_slip_src_max"])
    claimed = m["contact_check"][D]
    ck("independent contacts agree with author claims (residual 11.2 src, flight phases, stop 0)",
       claimed["walk_max_world_slip_src_at_40ms_boundaries"] == round(V, 3) and claimed["flight_phases"] == c["flight_phases"]
       and claimed["stop_bridge_grounded_slip_src_max"] == c["stop_bridge_grounded_slip_src_max"], c["flight_phases"])
    # identity anchors from raw pixels
    idm = [i for i, im in enumerate(imgs) if not v_identity(im)]
    ck("identity: white medicine case w/ green cross (screen right) + green wristband (screen left) in all frames", not idm, idm[:5])
    fe = [i for i, f in enumerate(faces) if {tuple(int(v) for v in cc) for cc in f[f[..., 3] == 255][:, :3]} & EYE]
    ck("back view: raw face cels have no eye/mouth colours in any frame", not fe, fe[:5])
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
            d_ = zin.read(info.filename)
            if info.filename == "image_data/frames/9/layer_2":
                arr = np.frombuffer(d_, np.uint8).reshape(H, W, 4).copy(); arr[SOLE, 30] = [255, 0, 0, 255]; d_ = arr.tobytes()
            zo.writestr(info, d_)
    _, _, tcomps, _, _ = pxo_frames(zb.getvalue())
    nc("tampered PXO cel -> recomposition mismatch", not np.array_equal(tcomps[8], imgs[8]))
    bs = json.loads(stb); bs["phase_bridges"][D]["phase3"][-1] = {"ref": "idle", "index": 1, "k": 1.0}
    nc("malformed stop JSON (bridge ends on idle f01) -> rejected", bool(v_stop(bs, png_names)))
    bs = json.loads(stb); bs["frame_ms"] = 39
    nc("stop frame_ms 39 -> rejected", bool(v_stop(bs, png_names)))
    bs = json.loads(stb); bs["settle_ms_inclusive"] = 119
    nc("stop settle 119 ms -> rejected", bool(v_stop(bs, png_names)))
    bs = json.loads(stb); bs["phase_bridges"]["west"] = {}
    nc("stop JSON with west entry (paused direction) -> rejected", bool(v_stop(bs, png_names)))
    bs = json.loads(stb); bs["phase_bridges"] = {"south": bs["phase_bridges"][D]}
    nc("stop JSON relabelled south -> rejected", bool(v_stop(bs, png_names)))
    bs = json.loads(stb); bs["phase_bridges"][D]["phase0"][1]["file"] = "png/missing.png"
    nc("stop JSON with missing bridge frame -> rejected", bool(v_stop(bs, png_names)))
    bs = json.loads(stb); del bs["phase_bridges"][D]["phase11"]
    nc("stop JSON missing phase11 -> rejected", bool(v_stop(bs, png_names)))
    bt = json.loads(ssb); bt["actions"]["walk"][D][5]["duration_ms"] = 0
    nc("walk duration 0 -> rejected", bool(v_timing(bt)))
    bt = json.loads(ssb); bt["actions"]["walk"][D][5]["duration_ms"] = 41
    nc("walk duration 41 (boundary drift) -> rejected", bool(v_timing(bt)))
    bt = json.loads(ssb); bt["actions"]["idle"][D][0]["duration_ms"] = 699
    nc("idle f00 duration 699 -> rejected", bool(v_timing(bt)))
    bt = json.loads(ssb); bt["pivot"] = [40, 103]
    nc("wrong pivot -> rejected", bool(v_timing(bt)))
    bt = json.loads(ssb); bt["actions"]["walk"]["south"] = bt["actions"]["walk"][D]
    nc("sprite set with extra south entry -> rejected", bool(v_timing(bt)))
    slid = [(np.roll(a_, 1, axis=1), b_) for a_, b_ in br_boots]
    nc("bridge s1 foot slid 1 texel -> stop slip detected", v_contacts(walk_boots, slid, boots[0])["stop_bridge_grounded_slip_src_max"] > 0)
    nc("horizontally mirrored neutral (south-style sides) -> identity rejected", not v_identity(imgs[0][:, ::-1].copy()))
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
        (OUT / f"{PFX}_walk-north-native-export_test-only-v01_{TAG}.log").write_bytes(log)
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
    y = travel                                                    # start low, walk north (up-screen) at host speed
    seq = [(imgs[1], 700, y)]                                     # idle f00
    for i in range(24):                                           # 2 walk cycles moving north at host speed
        seq.append((walk_ims[i % NPH], FMS, y)); y -= V
    sp = 7                                                        # explicit release at phase 7
    seq.append((walk_ims[sp], FMS, y))
    seq += [(imgs[17 + 2 * sp], FMS, y), (imgs[18 + 2 * sp], FMS, y), (imgs[1], 900, y)]
    ch = int(H + travel + 8)
    frames, durs = [], []
    for im, d_, yy in seq:
        cv = Image.new("RGBA", (W + 40, ch), (58, 62, 70, 255))
        g_ = Image.new("RGBA", (W + 40, 1), (90, 96, 108, 255))
        for gy in range(SOLE + 1, ch, 22):
            cv.paste(g_, (0, gy))
        cv.alpha_composite(Image.fromarray(im, "RGBA"), (20, int(round(yy))))
        frames.append(cv.resize(((W + 40) * S, ch * S), Image.NEAREST).convert("P", palette=Image.ADAPTIVE, colors=255))
        durs.append(d_)
    gif = OUT / f"{PFX}_walk-north-normal-speed-preview-source-bound_unapproved-mnw01-v01_{TAG}.gif"
    frames[0].save(gif, save_all=True, append_images=frames[1:], duration=durs, loop=0, disposal=2)
    sheet = Image.new("RGBA", (W * 12, H * 3), (58, 62, 70, 255))
    for i, im in enumerate(walk_ims):
        sheet.alpha_composite(Image.fromarray(im, "RGBA"), (i * W, 0))
    for p in range(NPH):
        sheet.alpha_composite(Image.fromarray(imgs[17 + 2 * p], "RGBA"), (p * W, H))
        sheet.alpha_composite(Image.fromarray(imgs[18 + 2 * p], "RGBA"), (p * W, 2 * H))
    sheetp = OUT / f"{PFX}_walk-north-contact-sheet-walk-s1-s2_unapproved-mnw01-v01_{TAG}.png"
    sheet.resize((W * 12 * 2, H * 3 * 2), Image.NEAREST).save(sheetp)

    result = {"task": "content.char.milo.walk-north", "manifest": mrel, "manifest_sha256_raw": sha(mraw),
              "checker_sha256_raw": sha(Path(__file__).read_bytes()), "checks": checks, "negative_controls": neg,
              "contacts_independent": c, "native": native,
              "preview": {"gif": gif.relative_to(ROOT).as_posix(), "gif_sha256": sha(gif.read_bytes()),
                          "contact_sheet": sheetp.relative_to(ROOT).as_posix(), "contact_sheet_sha256": sha(sheetp.read_bytes()),
                          "scope": "source-bound PIL composite at 40 ms/frame, host 11.2 src px/40 ms; NOT a Godot capture",
                          "sequence": "idle f00 700ms, walk 2 cycles moving north (up-screen), release at phase 7 -> s1, s2, idle f00"},
              "not_claimed": ["footlock/slip-free (back is in place: 5.6 logical px/40 ms residual)", "fluidity or human motion acceptance",
                              "GUI SaveAs/reopen", "Godot runtime/normal-host stop playback", "art approval", "four-direction loader readiness"],
              "passed": all(x["pass"] for x in checks)}
    rp_ = OUT / f"{PFX}_walk-north-independent-result_v01_{TAG}.json"
    rp_.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(rp_.relative_to(ROOT).as_posix())
    print("INDEPENDENT", "PASS" if result["passed"] else "FAIL", sum(x["pass"] for x in checks), "/", len(checks))
    return 0 if result["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
