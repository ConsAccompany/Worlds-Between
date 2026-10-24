"""Muxiu NORTH walk/run loop + phase-aware stop source author (nw89a001, UNAPPROVED technical source).

content.char.muxiu.walk-north. NORTH ONLY. Thin bounded adapter over the frozen jexplore39 Jiang Lan exploration
author, same reuse pattern as the Muxiu muxsw69 south adapter: its in-place 12-phase front/back cycle (40 ms, host
140 logical px/s), stop_poses, contact_report, leg_transform and serializers (make_pxo/make_ora via mexplore23)
are reused unchanged. Actor bindings are rebound in memory only (no Jiang/Lin/Milo/Muxiu file is written):
  - neutral layers come from the Muxiu north static author draw() and must recompose to the existing Muxiu north
    static PNG bytes (hash-pinned); the editable neutral PXO/ORA/manifest/palette are read-only pins.
  - Muxiu 13 roles. head = face/hair/braid (braid rides the head: bob only, no secondary sway, disclosed);
    torso = shirt/belt/pouches/cloak/whistle; arm-like = arms + bracelet (the rope bracelet sits wholly in the
    x<40 column and moves with the character's left arm, screen left, so it never detaches);
    legs = trousers (rows >= LEG_TOP) + legwraps + boots, each split at x=40 and lifted below the knee per foot.
    render_idle/render_fb are Muxiu copies of the jexplore39 functions with only those role-group changes.
North is a back view: character's right = screen right. Braid plait crosses the screen-right shoulder, bracelet is
on the screen-left wrist, whistle body is front-worn (only its cord is visible). No north eyes/mouth.
One cycle serves walk/run at the host normal speed (no separate faster run cycle exists in this batch).
West/south/east and idle tasks are NOT produced here.

Usage:  <venv python> -B -X utf8 -I <tool> build|check
Writes only NEW files under outputs/muxiu-nw89/source and game/assets/characters/muxiu-native-v01/north-walk
(refuses to overwrite different bytes).
"""
import hashlib, importlib.util, json, os, sys
import numpy as np

_HERE = os.path.dirname(os.path.abspath(__file__))


def _load(fn, mod):
    spec = importlib.util.spec_from_file_location(mod, os.path.join(_HERE, fn))
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


_J_FN = "rpg-2-star-ocean-the-second_jiang-lan_exploration-source-author_unapproved-jexplore39-v01_20261022-154032-5bca7193.py"
_N_FN = "rpg-2-star-ocean-the-second_muxiu_north-static-author_unapproved-v01r2_20261024-080000-4e7d2c19.py"
TOOL_PINS = {_J_FN: "ae8654f28c89e4c11ef7c52b61fc87ee992af5ae805277998102e4ba9bf80cd5",   # raw bytes
             _N_FN: "06784115351bf1cfdf6c80c91e80f504267706304ec9d6731de8f97fa37b2e1c"}
for _fn, _want in TOOL_PINS.items():
    with open(os.path.join(_HERE, _fn), "rb") as _fh:
        assert hashlib.sha256(_fh.read()).hexdigest() == _want, f"reused tool drift: {_fn}"
J = _load(_J_FN, "wb_jexplore39_for_muxiu_nw")
MN = _load(_N_FN, "wb_muxiu_north_static_v01r2")
assert all(MN.PIN_OK.values()), f"Muxiu north static author pins drifted: {MN.PIN_OK}"
assert all(MN.MS.PIN_OK.values()), f"transitive Muxiu/helper pins drifted: {MN.MS.PIN_OK}"
mx, sha, sha_text, rb, rp, decode, blank, shift, over = J.mx, J.sha, J.sha_text, J.rb, J.rp, J.decode, J.blank, J.shift, J.over

STAMP, RUN = "20261024-084500", "nw89a001"
ACTOR = "muxiu"
ZIP_DT = (2026, 10, 24, 8, 45, 0)
DIRS = ("north",)
assert (J.W, J.H, J.PIN) == (MN.W, MN.H, MN.PIN) and tuple(MN.BODY_ROWS) == (8, J.SOLE)

ROLES = [n for n in MN.LAYERS if n != "guides"]
PAL = {k: "#" + v for k, v in MN.PAL.items()}
RGB = {k: MN.S.rgb(k) for k in MN.PAL}
INV = {v: k for k, v in RGB.items()}
assert len(INV) == len(RGB)
DARK = {k: k for k in PAL}            # far-limb recolor is side-only; unused for north (identity, disclosed)
HEAD, TORSO, ARMLIKE = ("face", "hair", "braid"), ("shirt", "belt", "pouches", "cloak", "whistle"), ("arms", "bracelet")
LEGS = ("trousers", "legwraps", "boots")
assert set(HEAD + TORSO + ARMLIKE + LEGS) == set(ROLES) and len(ROLES) == 13
BRACELET_ARM_TOP_OFFSET = 68 - 59     # neutral: bracelet top row 68, screen-left arm top row 59

_N = "game/assets/characters/muxiu-native-v01/north"
NEUTRAL = {"north": (f"{_N}/rpg-2-star-ocean-the-second_muxiu_north-static_unapproved-v01_20261024-080000-f1f63759.png",
                     "03062ace22b7e83aacf8d02b6b0d715e6ff0d4ef74c71770ff7fb8aeb96e5bbe")}
NEUTRAL_NATIVE = {  # existing Muxiu north static package: read-only pins (must stay byte-exact)
    f"{_N}/rpg-2-star-ocean-the-second_muxiu_north-edit_unapproved-v01_20261024-080000-4b1f2dd1.pxo": "e3152eee03091ec05b4114446a3a6a05fb75c3c65e45783d6f87c58a2ad3f95c",
    f"{_N}/rpg-2-star-ocean-the-second_muxiu_north-edit_unapproved-v01_20261024-080000-bbe8ce6f.ora": "8c9c990eb80151597e51249ff70560bbfa11d2cd839b64502bcd310f3a09d4e4",
    f"{_N}/rpg-2-star-ocean-the-second_muxiu_north-manifest_unapproved-v01_20261024-080000-d1f8693c.json": "089c18947c03eea607a3213fb326fdc97abe46555175546622e124ec1878b542",
    f"{_N}/rpg-2-star-ocean-the-second_muxiu_north-palette_unapproved-v01_20261024-080000-b950d628.json": "834805c28e3d19f45ee7d60d6ea645290d0f6d8f8006d48b6d2e68d6b823be34"}


def load_neutral(d):
    rel, want = NEUTRAL[d]
    png = rb(rp(rel))
    assert sha(png) == want, f"{d} neutral PNG hash drift"
    lay = MN.draw()
    comp = MN.S.compose_layers({n: lay[n] for n in MN.LAYERS})
    assert np.array_equal(comp, decode(png)), f"{d} Muxiu north role layers != neutral PNG"
    return {n: lay[n].copy() for n in MN.LAYERS}, png


# ----------------------------------------------------------------------------- Muxiu north renderer variants
def render_idle(base, i):
    t, h, a = J.IDLE[i]
    out = []
    for n in ROLES:
        dy = h if n in HEAD else (t if n in TORSO else (a if n in ARMLIKE else 0))
        out.append((n, shift(base[n], 0, dy) if dy else base[n].copy()))
    return [("far-limbs", blank())] + out


def render_fb(base, d, q):
    b = q["bob"]
    out, feet, legs = {}, {}, {n: [] for n in LEGS}
    for key, x0, x1 in (("A", 0, 40), ("B", 40, J.W)):
        lift = q["al"] if key == "A" else q["bl"]
        for n in LEGS:
            src = J.rows(base[n], J.LEG_TOP) if n == "trousers" else base[n]
            piece = J.leg_transform(J.cols(src, x0, x1), 0, lift, b)
            legs[n].append(piece)
            if n == "boots":
                feet[key] = piece
    out["trousers"] = over([shift(J.rows(base["trousers"], 0, J.LEG_TOP), 0, b)] + legs["trousers"])
    out["legwraps"], out["boots"] = over(legs["legwraps"]), over(legs["boots"])
    for n in ARMLIKE:
        a = base[n]
        out[n] = over([shift(J.cols(a, 0, 40), 0, b + q["arm_dy_l"]), shift(J.cols(a, 40, J.W), 0, b + q["arm_dy_r"])])
    out["far-limbs"] = blank()
    for n in ROLES:
        if n not in out:
            out[n] = shift(base[n], 0, b) if b else base[n].copy()
    return [(n, J.clip_floor(out[n])) for n in J.PXO_LAYERS[:-1]], feet


# ----------------------------------------------------------------------------- rebind (in memory only)
J.STAMP, J.RUN, J.ACTOR, J.ZIP_DT = STAMP, RUN, ACTOR, ZIP_DT
mx.ZIP_DT = ZIP_DT
J.DIRS = DIRS
J.OUT_REL, J.PKG_REL = "outputs/muxiu-nw89/source", "game/assets/characters/muxiu-native-v01/north-walk"
J.PFX = "rpg-2-star-ocean-the-second_muxiu_walk"
J.VAR = "unapproved-nw89-v01"
J.ROLES, J.PXO_LAYERS = ROLES, ["far-limbs"] + ROLES + ["guides"]
J.HEAD, J.TORSO = HEAD, TORSO
J.PAL, J.RGB, J.INV, J.DARK = PAL, RGB, INV, DARK
J.render_idle, J.render_fb = render_idle, render_fb
J.NEUTRAL, J.NEUTRAL_NATIVE, J.load_neutral = NEUTRAL, NEUTRAL_NATIVE, load_neutral
OUT_REL, PKG_REL, fname = J.OUT_REL, J.PKG_REL, J.fname


def build_all():
    fsets, files, source = J.build_all()
    old = f"{OUT_REL}/{fname('source-manifest', 'json')}"
    for k in ("source_inputs", "reused_helpers", "tool", "limitations", "task_ids", "visual_id", "walk_model"):
        source.pop(k)
    source["directions"]["north"]["ora"]["content"] = "supplementary: static neutral 13 Muxiu north role layers + hidden guides"
    source.update({
        "visual_id": ACTOR, "direction_scope": "north only (south/west/east and idle tasks not in this task)",
        "task_ids": ["content.char.muxiu.walk-north"],
        "dependency": {"content.char.muxiu.static-north": "DONE (neutral source pinned byte-exact)"},
        "identity": "Bible character-06: 24, animal carer; moss short cloak, rope bracelet, small whistle, braid (north/back)",
        "groups": {"head": list(HEAD), "torso": list(TORSO), "arm_like": list(ARMLIKE), "legs": list(LEGS),
                   "braid": "rides the head (bob only), plait over the screen-right shoulder; no secondary sway added; disclosed",
                   "bracelet": f"rides the screen-left arm column (constant {BRACELET_ARM_TOP_OFFSET}-row offset to left-arm top)"},
        "walk_model": {"front": f"in place; foot A = viewer-left column (x<40) of trousers-below-hip/legwraps/boots lifted "
                                f"below the knee p4-p11 by {list(J.FB_SWING)}, B = x>=40 same shifted 6 phases; "
                                "contact p0 (both planted, A at toe-off boundary), plant p0-p3, swing p4-p11; "
                                "arms+bracelet +-1 texel per column in counter-phase; body down 1 texel at p1,p2,p7,p8, never up",
                       "walk_run": "one cycle used for walk/run at host normal speed 140 logical px/s; no separate run-speed cycle",
                       "frame_hold": "each phase is held 40 ms; host moves continuously; root does not move in the source frames"},
        "source_inputs": {"muxiu_north_static_author": {"file": "tools/" + _N_FN, "sha256_raw": TOOL_PINS[_N_FN],
                                                         "sha256_text_lf_v1": sha_text(rb(os.path.join(_HERE, _N_FN)))},
                          "neutral_pngs": {"north": {"file": NEUTRAL["north"][0], "sha256": NEUTRAL["north"][1]}},
                          "neutral_editables_pinned": NEUTRAL_NATIVE,
                          "static_qa": "docs/qa/rpg-2-star-ocean-the-second_muxiu_north-static-source-verdict_unapproved-v01_20261024-061800-b62a0001.md"},
        "reused_engine": {"file": "tools/" + _J_FN, "sha256_raw": TOOL_PINS[_J_FN],
                          "sha256_text_lf_v1": sha_text(rb(os.path.join(_HERE, _J_FN))),
                          "use": "front/back cycle timing, stop_poses, contact_report, leg_transform, serializers; "
                                 "render_idle/render_fb replaced by Muxiu copies (legwraps articulate with legs; bracelet rides left arm column)"},
        "reused_helpers": {"file": "tools/" + J._MX_FN, "sha256_text_lf_v1": sha_text(rb(os.path.join(_HERE, J._MX_FN)))},
        "reused_tool_pins": {**MN.PINS, **MN.MS.PINS},
        "limitations": [
            "north cycle is IN PLACE: a planted foot travels with the host by 11.2 source texels (5.6 logical) per 40 ms; "
            "this is the frozen jexplore39/muxsw69 front/back residual, reused without threshold change; NOT slip-free, NOT footlocked",
            "contact metrics are not fluidity, footlock or human motion acceptance",
            "legs are the static leg texels lifted below the knee row 80 (no foreshortening repaint); trousers below the hip are split at x=40, so a lifted leg separates from the standing leg (static-texel limit, disclosed)",
            "braid, pouches and cloak ride head/torso (no secondary motion); coarse frozen static, cosmetic refinement deferred",
            "Muxiu north static and portrait are UNAPPROVED; no art, motion or fluidity acceptance",
            "supplemental stop JSON is not read by the generic loader (immediate idle); stop playback is source scope only, not normal-host playback",
            "north only: package has no south/west/east entries and is opt-in/non-default"],
        "tool": {"file": "tools/" + os.path.basename(__file__), "sha256_text_lf_v1": sha_text(rb(os.path.abspath(__file__)))}})
    files[old] = (json.dumps(source, indent=2, ensure_ascii=False) + "\n").encode()
    return fsets, files, source


# ----------------------------------------------------------------------------- north-only source checks
def source_checks(fsets, files, source):
    """jexplore39 per-direction checks for north + package/identity checks (4-direction cross checks do not apply)."""
    import io, zipfile
    res = []

    def ck(name, ok, detail=""):
        res.append({"check": name, "pass": bool(ok), "detail": detail})

    W, H, NPH = J.W, J.H, J.NPH
    pal = set(RGB.values())
    d = "north"
    e = source["directions"][d]
    stop_frames = [s for p in range(NPH) for s in e["stop_bridges"][f"phase{p}"] if "file" in s]
    allf = [e["static"]] + e["idle"] + e["walk"] + stop_frames
    bad = []
    for x in allf:
        a = decode(files[x["file"]]); al = a[..., 3]
        if a.shape != (H, W, 4) or set(np.unique(al)) - {0, 255} or al[0].any() or al[-1].any() or al[:, 0].any() or al[:, -1].any():
            bad.append(x["file"])
        if {tuple(c) for c in a[al == 255][:, :3]} - pal:
            bad.append(x["file"] + " palette")
    ck("north all frames 80x112 binary alpha, clear border, Muxiu palette only", not bad, bad[:3])
    ck("north static + idle f00 are the exact neutral PNG bytes", e["static"]["sha256"] == NEUTRAL[d][1] == e["idle"][0]["sha256"])
    ck("north counts idle 4 walk 12 stop bridge frames 24", (len(e["idle"]), len(e["walk"]), len(stop_frames)) == (4, 12, 24))
    ck("north every bridge = [walk p, s1, s2, idle f00]", all(
        v[0] == {"ref": "walk", "index": int(k[5:]), "k": 0.0} and v[-1] == {"ref": "idle", "index": 0, "k": 1.0} and len(v) == 4
        for k, v in e["stop_bridges"].items()))
    ck("north idle frames distinct (>=3)", len({files[x["file"]] for x in e["idle"]}) >= 3)
    low = {decode(files[x["file"]])[69:104].tobytes() for x in e["walk"]}
    ck("north walk lower body differs across phases (>=8)", len(low) >= 8, len(low))
    ck("north no walk phase equals the neutral bitmap", all(x["sha256"] != NEUTRAL[d][1] for x in e["walk"]))
    hs = [int(np.nonzero(decode(files[x["file"]])[..., 3].any(1))[0].min()) for x in allf]
    ck("north top row never above neutral (body never shifted up)", min(hs) >= 8, [min(hs), max(hs)])
    with zipfile.ZipFile(io.BytesIO(files[e["ora"]["file"]])) as z:
        comp = over([decode(z.read(f"data/{n}.png")) for n in ROLES])
        ck("north ORA role layers recompose to neutral PNG", np.array_equal(comp, decode(files[e["static"]["file"]])) and
           z.read("mergedimage.png") == files[e["static"]["file"]])
    with zipfile.ZipFile(io.BytesIO(files[e["pxo"]["file"]])) as z:
        nl = len(J.PXO_LAYERS)
        okp = len(allf) == e["pxo"]["frames"]
        okp &= [l["name"] for l in json.loads(z.read("data.json"))["layers"]] == J.PXO_LAYERS
        for fi, x in enumerate(allf, start=1):
            lays = [np.frombuffer(z.read(f"image_data/frames/{fi}/layer_{li}"), np.uint8).reshape(H, W, 4) for li in range(1, nl)]
            okp &= np.array_equal(over(lays), decode(files[x["file"]]))
        ck("north PXO (Muxiu 13 roles + far-limbs + guides) cels recompose to every frame PNG", okp, e["pxo"]["frames"])
    c = source["contact_check"][d]
    ck("north stop bridges: a grounded foot never moves (host stopped)", c["stop_bridge_grounded_slip_src_max"] == 0, c["stop_bridge_nonzero"][:3])
    ck("north each foot grounded 4 phases per cycle (p0-p3 lifted p4-p11)",
       all(sum(1 for r in c["per_phase_feet"] if r[k]["grounded"]) == 4 for k in ("A", "B")),
       [sum(1 for r in c["per_phase_feet"] if r[k]["grounded"]) for k in ("A", "B")])
    # identity anchors visible in EVERY frame (north orientation): hair mass, braid over screen-RIGHT shoulder,
    # rope bracelet on screen-LEFT wrist, moss capelet + cream back tree. Whistle wood must stay front-only.
    hair_c, rope_c, moss_c = {RGB[k] for k in ("h1", "h2", "h3")}, {RGB["q1"], RGB["c2"]}, {RGB["c1"], RGB["c2"]}
    miss = []
    for x in allf:
        a = decode(files[x["file"]]); m = a[..., 3] == 255
        reg = lambda y0, y1, x0, x1: {tuple(v) for v in a[y0:y1, x0:x1][m[y0:y1, x0:x1]][:, :3]}
        if not (hair_c & reg(8, 30, 24, 56) and {RGB["h2"], RGB["h3"]} & reg(29, 43, 43, 58)
                and rope_c & reg(66, 74, 14, 24) and moss_c <= reg(30, 62, 20, 60)
                and RGB["w2"] in reg(46, 56, 34, 46)):
            miss.append(x["file"].rsplit("/", 1)[-1])
    ck("identity: hair, braid screen-right, bracelet screen-left, moss cloak + cream back tree in every frame", not miss, miss[:3])
    wood = {RGB["x1"], RGB["x2"]}
    wf = [x["file"].rsplit("/", 1)[-1] for x in allf
          if {tuple(int(v) for v in cc) for cc in decode(files[x["file"]])[..., :3][decode(files[x["file"]])[..., 3] == 255]} & wood]
    ck("north whistle body not drawn through the back (no wood colours)", not wf, wf[:3])
    eye = {RGB["e1"], RGB["e2"], RGB["m1"]}
    nl2 = [lay for lay in fsets[d]["idle"]] + [w[0] for w in fsets[d]["walk"]] + [x[0] for p in range(NPH) for x in fsets[d]["stop"][p]]
    nb = sum(1 for lay in nl2 for n, a in lay if n == "face" and {tuple(int(v) for v in cc) for cc in a[a[..., 3] == 255][:, :3]} & eye)
    ck("north face layer has no eye/mouth colours in any frame (rear neck/ears only)", nb == 0, {"frames": len(nl2), "with_eyes": nb})
    fl = fsets[d]
    det = 0
    for lay in [w[0] for w in fl["walk"]] + [s[0] for p in range(NPH) for s in fl["stop"][p]] + list(fl["idle"]):
        L = dict(lay)
        wy = np.nonzero(L["bracelet"][..., 3].any(1))[0]; ay = np.nonzero(J.cols(L["arms"], 0, 40)[..., 3].any(1))[0]
        det += int((wy.min() - ay.min()) != BRACELET_ARM_TOP_OFFSET)
    ck("identity: bracelet stays on the left arm (constant offset to left-arm top in every frame)", det == 0, det)
    pk = json.loads(files[source["package"]["sprite_set"]])
    paths = [f["file"] for a in pk["actions"].values() for v in a.values() for f in v]
    durs = [f["duration_ms"] for a in pk["actions"].values() for v in a.values() for f in v]
    ok = pk["schema"] == "worlds-between.exploration-sprite-set.v1" and pk["actor_id"] == ACTOR and \
        set(pk["actions"]) == {"idle", "walk"} and all(set(pk["actions"][a]) == {"north"} for a in pk["actions"])
    ok &= all(isinstance(x, int) and 40 <= x <= 2000 for x in durs)
    ok &= all(files[PKG_REL + "/" + p] == files[OUT_REL + "/" + p] for p in paths)
    ck("runtime sprite set: schema/actor/north only/explicit durations/relative byte-equal PNG copies", ok, len(paths))
    stp = json.loads(files[source["package"]["stop_supplemental"]])
    sp = [s["file"] for v in stp["phase_bridges"]["north"].values() for s in v if "file" in s]
    ck("stop supplemental: actor, north only, 24 bridge frames, runtime_default false, byte-equal copies",
       stp["actor_id"] == ACTOR and list(stp["phase_bridges"]) == ["north"] and len(sp) == 24 and stp["runtime_default"] is False
       and all(files[PKG_REL + "/" + p] == files[OUT_REL + "/" + p] for p in sp), len(sp))
    reg = json.loads(files[source["package"]["registry"]])
    ck("package-local registry lists ONLY muxiu -> this set", list(reg["actors"]) == [ACTOR] and PKG_REL + "/" + reg["actors"][ACTOR] == source["package"]["sprite_set"])
    ck("all written paths are under the assigned roots", all(r.startswith((OUT_REL + "/", PKG_REL + "/")) for r in files))
    return res


def main():
    mode = sys.argv[1] if len(sys.argv) > 1 else "check"
    if mode not in ("build", "check"):
        raise SystemExit("usage: build|check")
    pins_before = {rel: sha(rb(rp(rel))) == want for rel, want in list(NEUTRAL_NATIVE.items()) + [v for v in NEUTRAL.values()]}
    fsets, files, source = build_all()
    _, files2, _ = build_all()
    det = files.keys() == files2.keys() and all(files[k] == files2[k] for k in files)
    listing_rel = f"{OUT_REL}/{fname('file-list', 'json')}"
    files[listing_rel] = (json.dumps({"run": f"{STAMP}-{RUN}", "hash": "sha256-bytes",
                                      "files": {r: sha(b) for r, b in sorted(files.items())}}, indent=2) + "\n").encode()
    if mode == "build":
        for rel, b in files.items():
            p = rp(rel)
            if os.path.exists(J._fs(p)) and rb(p) != b:
                raise SystemExit(f"refusing to overwrite different bytes: {rel}")
        mx.write_all(files)
        print(f"WROTE {len(files)} files")
    fails, n_ok = [], 0
    for rel, b in files.items():
        try:
            if rb(rp(rel)) == b:
                n_ok += 1
            else:
                fails.append(f"rebuild differs {rel}")
        except OSError:
            fails.append(f"missing {rel}")
    print(f"REBUILD {n_ok}/{len(files)}  DETERMINISTIC {det}")
    if not det:
        fails.append("non-deterministic build")
    sc = source_checks(fsets, files, source)
    for c in sc:
        if not c["pass"]:
            fails.append("source " + c["check"])
    print(f"SOURCE {sum(c['pass'] for c in sc)}/{len(sc)}")
    pins_after = {rel: sha(rb(rp(rel))) == want for rel, want in list(NEUTRAL_NATIVE.items()) + [v for v in NEUTRAL.values()]}
    pins_ok = all(pins_before.values()) and all(pins_after.values()) and all(MN.PIN_OK.values()) and all(MN.MS.PIN_OK.values())
    if not pins_ok:
        fails.append("neutral source pins drifted")
    c = source["contact_check"]["north"]
    summary = {k: c[k] for k in ("walk_max_world_slip_src_at_40ms_boundaries", "walk_max_world_slip_logical_at_40ms_boundaries",
                                 "flight_phases", "stop_bridge_grounded_slip_src_max")}
    print(json.dumps(summary))
    res = {"tool_sha256_text_lf_v1": source["tool"]["sha256_text_lf_v1"], "rebuild": {"checked": len(files), "ok": n_ok},
           "deterministic": det, "neutral_pins_exact_before_after": pins_ok, "source_checks": sc, "contacts": summary,
           "residual_disclosed": "north in-place planted-foot world slip 11.2 src (5.6 logical) per 40 ms; not footlocked",
           "not_run_here": ["Pixelorama native export (independent checker)", "Godot import/runtime", "normal-speed movie"],
           "fails": fails}
    print("RESULT", "PASS" if not fails else "FAIL", json.dumps(fails[:12]))
    out = rp(f"{OUT_REL}/{fname('check-result-' + mode, 'json')}")
    os.makedirs(J._fs(os.path.dirname(out)), exist_ok=True)
    with open(J._fs(out), "wb") as fh:
        fh.write((json.dumps(res, indent=2) + "\n").encode())
    return 0 if not fails else 1


if __name__ == "__main__":
    sys.exit(main())
