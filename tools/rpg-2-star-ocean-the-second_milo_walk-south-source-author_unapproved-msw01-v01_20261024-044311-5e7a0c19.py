"""Milo SOUTH walk/run loop + phase-aware stop source author (msw01, UNAPPROVED technical source).

content.char.milo.walk-south. SOUTH ONLY. Thin bounded adapter over the frozen jexplore39 Jiang Lan exploration
author (same reuse pattern as the Lin Que lexplore59 adapter): its front/back in-place 12-phase cycle (40 ms,
host 140 logical px/s), stop_poses, contact_report, serializers (make_pxo/make_ora via mexplore23) are reused.
Actor bindings are rebound in memory only (no Jiang/Lin/Milo file is written):
  - neutral layers come from the Milo south static author draw() and must recompose to the existing Milo south
    static PNG bytes (hash-pinned); editable neutral PXO/ORA are read-only pins.
  - Milo 11 roles; head = face/hair; torso = undershirt/coat/belt/case/strap (square medicine case rides the
    torso: bob only, no swing); arm-like = arms + wristband (the bright green wristband moves with the
    character's left arm column so it never detaches). render_idle/render_fb are Milo copies of the jexplore39
    functions with that single arm-like change; everything else is the frozen engine.
One cycle serves walk/run at the host normal speed (no separate faster run cycle exists in this batch).
West/north/east are NOT produced (Milo west is paused).

Usage:  python -X utf8 -I <tool> build|check
Writes only NEW files under outputs/milo-sw01 and game/data/milo-sw01 (refuses to overwrite different bytes).
"""
import importlib.util, json, os, sys
import numpy as np

_HERE = os.path.dirname(os.path.abspath(__file__))


def _load(fn, mod):
    spec = importlib.util.spec_from_file_location(mod, os.path.join(_HERE, fn))
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


_J_FN = "rpg-2-star-ocean-the-second_jiang-lan_exploration-source-author_unapproved-jexplore39-v01_20261022-154032-5bca7193.py"
_M_FN = "rpg-2-star-ocean-the-second_milo_south-static-author_unapproved-v01_20261023-215823-51a12dd6.py"
J = _load(_J_FN, "wb_jexplore39_for_milo_sw")
MS = _load(_M_FN, "wb_milo_south_static_v01")
mx, sha, sha_text, rb, rp, decode, blank, shift, over = J.mx, J.sha, J.sha_text, J.rb, J.rp, J.decode, J.blank, J.shift, J.over

STAMP, RUN = "20261024-044311", "5e7a0c19"
ACTOR = "milo"
ZIP_DT = (2026, 10, 24, 4, 43, 10)
DIRS = ("south",)
assert (J.W, J.H, J.PIN) == (MS.W, MS.H, MS.PIN) and tuple(MS.BODY_ROWS) == (8, J.SOLE)

ROLES = [n for n in MS.LAYERS if n != "guides"]
PAL = {k: "#" + v for k, v in MS.PAL.items()}
RGB = {k: MS.S.rgb(k) for k in MS.PAL}
INV = {v: k for k, v in RGB.items()}
assert len(INV) == len(RGB)
DARK = {k: k for k in PAL}            # far-limb recolor is side-only; unused for south (identity, disclosed)
HEAD, TORSO, ARMLIKE = ("face", "hair"), ("undershirt", "coat", "belt", "case", "strap"), ("arms", "wristband")
assert set(HEAD + TORSO + ARMLIKE + ("boots", "trousers")) == set(ROLES)

_N = "game/assets/characters/milo-native-v01/south"
NEUTRAL = {"south": (f"{_N}/rpg-2-star-ocean-the-second_milo_south-static_unapproved-v01_20261023-215823-28a012bd.png",
                     "3822b31805729f3091a61b3e073ade723f613049db4622364dc162a5101fa473")}
NEUTRAL_NATIVE = {  # existing Milo south static package: read-only pins (must stay byte-exact)
    f"{_N}/rpg-2-star-ocean-the-second_milo_south-edit_unapproved-v01_20261023-215823-aaf32a0b.pxo": "400c634f35c8aa43cce6ddf607968ac9a8041edd7c5caf4b582083164004c51f",
    f"{_N}/rpg-2-star-ocean-the-second_milo_south-edit_unapproved-v01_20261023-215823-e1afaba2.ora": "1545d66ca66296e44d37466526f262431a03740f93b8935161dd91408de56b2c",
    f"{_N}/rpg-2-star-ocean-the-second_milo_south-manifest_unapproved-v01_20261023-215823-e604f893.json": "913d3070528bfb8539c65e7570e73c5f7bedc1b45a23928ec9aa091db7324cf7",
    f"{_N}/rpg-2-star-ocean-the-second_milo_south-palette_unapproved-v01_20261023-215823-ef8896f1.json": "cae805d053847d1c39f3c8de7801ca826c2679b5db5abb75b22238990dbac927"}


def load_neutral(d):
    rel, want = NEUTRAL[d]
    png = rb(rp(rel))
    assert sha(png) == want, f"{d} neutral PNG hash drift"
    lay = MS.draw()
    comp = MS.S.compose_layers({n: lay[n] for n in MS.LAYERS})
    assert np.array_equal(comp, decode(png)), f"{d} Milo role layers != neutral PNG"
    return {n: lay[n].copy() for n in MS.LAYERS}, png


# ----------------------------------------------------------------------------- Milo renderer variants
def render_idle(base, i):
    t, h, a = J.IDLE[i]
    out = []
    for n in ROLES:
        dy = h if n in HEAD else (t if n in TORSO else (a if n in ARMLIKE else 0))
        out.append((n, shift(base[n], 0, dy) if dy else base[n].copy()))
    return [("far-limbs", blank())] + out


def render_fb(base, d, q):
    b = q["bob"]
    out, feet, legs_tr, legs_bt = {}, {}, [], []
    for key, x0, x1 in (("A", 0, 40), ("B", 40, J.W)):
        lift = q["al"] if key == "A" else q["bl"]
        tr = J.cols(J.rows(base["trousers"], J.LEG_TOP), x0, x1)
        bt = J.cols(base["boots"], x0, x1)
        legs_tr.append(J.leg_transform(tr, 0, lift, b))
        bt2 = J.leg_transform(bt, 0, lift, b)
        legs_bt.append(bt2)
        feet[key] = bt2
    out["trousers"] = over([shift(J.rows(base["trousers"], 0, J.LEG_TOP), 0, b)] + legs_tr)
    out["boots"] = over(legs_bt)
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
J.OUT_REL, J.PKG_REL = "outputs/milo-sw01", "game/data/milo-sw01"
J.PFX = "rpg-2-star-ocean-the-second_milo_walk"
J.VAR = "unapproved-msw01-v01"
J.ROLES, J.PXO_LAYERS = ROLES, ["far-limbs"] + ROLES + ["guides"]
J.HEAD, J.TORSO = HEAD, TORSO
J.PAL, J.RGB, J.INV, J.DARK = PAL, RGB, INV, DARK
J.render_idle, J.render_fb = render_idle, render_fb
OUT_REL, PKG_REL, fname = J.OUT_REL, J.PKG_REL, J.fname


def _bind_pins():
    J.NEUTRAL, J.NEUTRAL_NATIVE, J.load_neutral = NEUTRAL, NEUTRAL_NATIVE, load_neutral


_bind_pins()


def build_all():
    fsets, files, source = J.build_all()
    old = f"{OUT_REL}/{fname('source-manifest', 'json')}"
    for k in ("source_inputs", "reused_helpers", "tool", "limitations", "task_ids", "visual_id", "walk_model"):
        source.pop(k)
    source.update({
        "visual_id": ACTOR, "direction_scope": "south only (west paused; north/east not in this task)",
        "task_ids": ["content.char.milo.walk-south"],
        "dependency": {"content.char.milo.static-south": "DONE (neutral source pinned byte-exact)"},
        "groups": {"head": list(HEAD), "torso": list(TORSO), "arm_like": list(ARMLIKE), "legs": ["trousers", "boots"],
                   "case": "square medicine case rides torso (bob only); no secondary swing added; disclosed"},
        "walk_model": {"front": f"in place; foot A = viewer-left column (x<40) lifted p4-p11 by {list(J.FB_SWING)}, "
                                "B = x>=40 same shifted 6 phases; arms+wristband +-1 texel per column; "
                                "body down 1 texel at p1,p2,p7,p8, never up",
                       "walk_run": "one cycle used for walk/run at host normal speed 140 logical px/s; no separate run-speed cycle"},
        "source_inputs": {"milo_south_static_author": {"file": "tools/" + _M_FN, "sha256_text_lf_v1": sha_text(rb(os.path.join(_HERE, _M_FN)))},
                          "neutral_pngs": {"south": {"file": NEUTRAL["south"][0], "sha256": NEUTRAL["south"][1]}},
                          "neutral_editables_pinned": NEUTRAL_NATIVE},
        "reused_engine": {"file": "tools/" + _J_FN, "sha256_text_lf_v1": sha_text(rb(os.path.join(_HERE, _J_FN))),
                          "use": "front/back cycle timing, stop_poses, contact_report, leg_transform, serializers; "
                                 "render_idle/render_fb replaced by Milo copies (wristband rides arm column)"},
        "reused_helpers": {"file": "tools/" + J._MX_FN, "sha256_text_lf_v1": sha_text(rb(os.path.join(_HERE, J._MX_FN)))},
        "limitations": [
            "front cycle is IN PLACE: a planted foot travels with the host by 11.2 source texels (5.6 logical) per 40 ms; "
            "this is the frozen jexplore39/lexplore59 front residual; NOT slip-free, NOT footlocked",
            "contact metrics are not fluidity, footlock or human motion acceptance",
            "legs are the static leg texels lifted below the knee (no foreshortening repaint); coat skirt and case ride the torso",
            "Milo south static is UNAPPROVED; no art, motion or fluidity acceptance",
            "supplemental stop JSON is not read by the generic loader (immediate idle); stop playback is source scope only",
            "south only: package has no west/north/east entries and is opt-in/non-default"],
        "tool": {"file": "tools/" + os.path.basename(__file__), "sha256_text_lf_v1": sha_text(rb(os.path.abspath(__file__)))}})
    files[old] = (json.dumps(source, indent=2, ensure_ascii=False) + "\n").encode()
    return fsets, files, source


# ----------------------------------------------------------------------------- south-only source checks
def source_checks(fsets, files, source):
    """jexplore39 per-direction checks for south + package/identity checks (the 4-direction cross checks do not apply)."""
    import io, zipfile
    res = []

    def ck(name, ok, detail=""):
        res.append({"check": name, "pass": bool(ok), "detail": detail})

    W, H, NPH = J.W, J.H, J.NPH
    pal = set(RGB.values())
    d = "south"
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
    ck("south all frames 80x112 binary alpha, clear border, Milo palette only", not bad, bad[:3])
    ck("south static + idle f00 are the exact neutral PNG bytes", e["static"]["sha256"] == NEUTRAL[d][1] == e["idle"][0]["sha256"])
    ck("south counts idle 4 walk 12 stop bridge frames 24", (len(e["idle"]), len(e["walk"]), len(stop_frames)) == (4, 12, 24))
    ck("south every bridge = [walk p, s1, s2, idle f00]", all(
        v[0] == {"ref": "walk", "index": int(k[5:]), "k": 0.0} and v[-1] == {"ref": "idle", "index": 0, "k": 1.0} and len(v) == 4
        for k, v in e["stop_bridges"].items()))
    ck("south idle frames distinct (>=3)", len({files[x["file"]] for x in e["idle"]}) >= 3)
    low = {decode(files[x["file"]])[69:104].tobytes() for x in e["walk"]}
    ck("south walk lower body differs across phases (>=8)", len(low) >= 8, len(low))
    hs = [int(np.nonzero(decode(files[x["file"]])[..., 3].any(1))[0].min()) for x in allf]
    ck("south top row never above neutral (body never shifted up)", min(hs) >= 8, [min(hs), max(hs)])
    with zipfile.ZipFile(io.BytesIO(files[e["ora"]["file"]])) as z:
        comp = over([decode(z.read(f"data/{n}.png")) for n in ROLES])
        ck("south ORA role layers recompose to neutral PNG", np.array_equal(comp, decode(files[e["static"]["file"]])) and
           z.read("mergedimage.png") == files[e["static"]["file"]])
    with zipfile.ZipFile(io.BytesIO(files[e["pxo"]["file"]])) as z:
        nl = len(J.PXO_LAYERS)
        okp = len(allf) == e["pxo"]["frames"]
        okp &= [l["name"] for l in json.loads(z.read("data.json"))["layers"]] == J.PXO_LAYERS
        for fi, x in enumerate(allf, start=1):
            lays = [np.frombuffer(z.read(f"image_data/frames/{fi}/layer_{li}"), np.uint8).reshape(H, W, 4) for li in range(1, nl)]
            okp &= np.array_equal(over(lays), decode(files[x["file"]]))
        ck("south PXO (Milo 11 roles + far-limbs + guides) cels recompose to every frame PNG", okp, e["pxo"]["frames"])
    c = source["contact_check"][d]
    ck("south stop bridges: a grounded foot never moves (host stopped)", c["stop_bridge_grounded_slip_src_max"] == 0, c["stop_bridge_nonzero"][:3])
    ck("south each foot grounded 4 phases per cycle (p0-p3 lifted p4-p11)",
       all(sum(1 for r in c["per_phase_feet"] if r[k]["grounded"]) == 4 for k in ("A", "B")),
       [sum(1 for r in c["per_phase_feet"] if r[k]["grounded"]) for k in ("A", "B")])
    # identity anchors visible in EVERY frame (case white+green cross, wristband green, coat white, navy)
    case_c, wb_c = {RGB["g2"]}, {RGB["g1"], RGB["g2"]}
    miss = []
    for x in allf:
        a = decode(files[x["file"]]); m = a[..., 3] == 255
        left = {tuple(v) for v in a[60:80, 10:30][m[60:80, 10:30]][:, :3]}
        right = {tuple(v) for v in a[55:70, 52:62][m[55:70, 52:62]][:, :3]}
        if not (case_c <= left and RGB["w1"] in left and wb_c & right):
            miss.append(x["file"].rsplit("/", 1)[-1])
    ck("identity: case (white + green cross, screen left) and green wristband (screen right) in every frame", not miss, miss[:3])
    fl = fsets["south"]
    det = 0
    for lay, *_ in [(w[0],) for w in fl["walk"]] + [(s[0],) for p in range(NPH) for s in fl["stop"][p]] + [(l,) for l in fl["idle"]]:
        L = dict(lay)
        wy = np.nonzero(L["wristband"][..., 3].any(1))[0]; ay = np.nonzero(J.cols(L["arms"], 40, W)[..., 3].any(1))[0]
        det += int((wy.min() - ay.min()) != (60 - 38))
    ck("identity: wristband stays on the arm (constant offset to right-arm top in every frame)", det == 0, det)
    pk = json.loads(files[source["package"]["sprite_set"]])
    paths = [f["file"] for a in pk["actions"].values() for v in a.values() for f in v]
    durs = [f["duration_ms"] for a in pk["actions"].values() for v in a.values() for f in v]
    ok = pk["schema"] == "worlds-between.exploration-sprite-set.v1" and pk["actor_id"] == ACTOR and \
        set(pk["actions"]) == {"idle", "walk"} and all(set(pk["actions"][a]) == {"south"} for a in pk["actions"])
    ok &= all(isinstance(x, int) and 40 <= x <= 2000 for x in durs)
    ok &= all(files[PKG_REL + "/" + p] == files[OUT_REL + "/" + p] for p in paths)
    ck("runtime sprite set: schema/actor/south only/explicit durations/relative byte-equal PNG copies", ok, len(paths))
    stp = json.loads(files[source["package"]["stop_supplemental"]])
    sp = [s["file"] for v in stp["phase_bridges"]["south"].values() for s in v if "file" in s]
    ck("stop supplemental: actor, south only, 24 bridge frames, runtime_default false, byte-equal copies",
       stp["actor_id"] == ACTOR and list(stp["phase_bridges"]) == ["south"] and len(sp) == 24 and stp["runtime_default"] is False
       and all(files[PKG_REL + "/" + p] == files[OUT_REL + "/" + p] for p in sp), len(sp))
    reg = json.loads(files[source["package"]["registry"]])
    ck("package-local registry lists ONLY milo -> this set", list(reg["actors"]) == [ACTOR] and PKG_REL + "/" + reg["actors"][ACTOR] == source["package"]["sprite_set"])
    ck("all written paths are under the assigned roots", all(r.startswith((OUT_REL + "/", PKG_REL + "/")) for r in files))
    return res


def main():
    mode = sys.argv[1] if len(sys.argv) > 1 else "check"
    if mode not in ("build", "check"):
        raise SystemExit("usage: build|check")
    pins_before = J.pins_state()
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
    pins_ok = all(pins_before.values()) and all(J.pins_state().values())
    if not pins_ok:
        fails.append("neutral source pins drifted")
    c = source["contact_check"]["south"]
    summary = {k: c[k] for k in ("walk_max_world_slip_src_at_40ms_boundaries", "walk_max_world_slip_logical_at_40ms_boundaries",
                                 "flight_phases", "stop_bridge_grounded_slip_src_max")}
    print(json.dumps(summary))
    res = {"tool_sha256_text_lf_v1": source["tool"]["sha256_text_lf_v1"], "rebuild": {"checked": len(files), "ok": n_ok},
           "deterministic": det, "neutral_pins_exact_before_after": pins_ok, "source_checks": sc, "contacts": summary,
           "residual_disclosed": "front in-place planted-foot world slip 11.2 src (5.6 logical) per 40 ms; not footlocked",
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
