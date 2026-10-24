"""Milo NORTH walk/run loop + phase-aware stop source author (mnw01, UNAPPROVED technical source).

content.char.milo.walk-north. NORTH ONLY. Same thin bounded adapter as the committed Milo south msw01 author, over
the frozen jexplore39 Jiang Lan exploration engine: its front/back in-place 12-phase cycle (40 ms, host 140
logical px/s), stop_poses, contact_report and serializers (make_pxo/make_ora via mexplore23) are reused.
The committed msw01 south author is loaded only for its Milo render_idle/render_fb (wristband rides the arm column)
and its roles/palette bindings; then the engine is rebound in memory for north (no south/Jiang/Lin file is written):
  - neutral layers come from the committed Milo north static author draw() and must recompose to the existing
    Milo north static PNG bytes (hash-pinned); the north editable PXO/ORA/manifest/palette are read-only pins.
  - back view: character's right = screen right. Square medicine case (screen right) rides the torso (bob only);
    the green wristband is on the screen-left wrist, i.e. inside the x<40 arm column, so the reused split moves it
    with that arm. Foot A = viewer-left column = character's left foot.
One cycle serves walk/run at the host normal speed (no separate faster run cycle exists in this batch).
South/west/east are NOT produced here (Milo west is paused).

Usage:  python -X utf8 -I <tool> build|check
Writes only NEW files under outputs/milo-nw01 (package staged at outputs/milo-nw01/pkg; refuses to overwrite).
"""
import importlib.util, json, os, sys
import numpy as np

_HERE = os.path.dirname(os.path.abspath(__file__))


def _load(fn, mod):
    spec = importlib.util.spec_from_file_location(mod, os.path.join(_HERE, fn))
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


_SW_FN = "rpg-2-star-ocean-the-second_milo_walk-south-source-author_unapproved-msw01-v01_20261024-044311-5e7a0c19.py"
_MN_FN = "rpg-2-star-ocean-the-second_milo_north-static-author_unapproved-v01_20261023-225642-1b612f93.py"
SW = _load(_SW_FN, "wb_milo_walk_south_msw01_for_north")
MN = _load(_MN_FN, "wb_milo_north_static_v01")
J = SW.J
mx, sha, sha_text, rb, rp, decode, blank, shift, over = J.mx, J.sha, J.sha_text, J.rb, J.rp, J.decode, J.blank, J.shift, J.over
_J_FN = SW._J_FN

STAMP, RUN = "20261024-045533", "2abbb86c"
ACTOR = "milo"
ZIP_DT = (2026, 10, 24, 4, 55, 32)
DIRS = ("north",)
assert (J.W, J.H, J.PIN) == (MN.W, MN.H, MN.PIN) and tuple(MN.BODY_ROWS) == (8, J.SOLE)
assert all(MN.PIN_OK.values()) and all(MN.MS.PIN_OK.values()), "north static author tool pins drifted"
assert [n for n in MN.LAYERS if n != "guides"] == SW.ROLES and MN.PAL == SW.MS.PAL

ROLES, PAL, RGB, INV, DARK = SW.ROLES, SW.PAL, SW.RGB, SW.INV, SW.DARK
HEAD, TORSO, ARMLIKE = SW.HEAD, SW.TORSO, SW.ARMLIKE
render_idle, render_fb = SW.render_idle, SW.render_fb

_N = "game/assets/characters/milo-native-v01/north"
NEUTRAL = {"north": (f"{_N}/rpg-2-star-ocean-the-second_milo_north-static_unapproved-v01_20261023-225642-5968ba0c.png",
                     "cf1e559885f2a87c31a3c6cf9feee953d95c8c1ca138ecd9bd8d6838bee8da61")}
NEUTRAL_NATIVE = {  # existing Milo north static package: read-only pins (must stay byte-exact)
    f"{_N}/rpg-2-star-ocean-the-second_milo_north-edit_unapproved-v01_20261023-225642-7f054cac.pxo": "9d9004e65b032f68e06a0b064cf623c7996cdd7c679ef36d7c8a37ab0108baee",
    f"{_N}/rpg-2-star-ocean-the-second_milo_north-edit_unapproved-v01_20261023-225642-af5a9058.ora": "a7a691f63f3c776293cc6fede97b1895c7f48a961c3825a9d6368a1a426895cf",
    f"{_N}/rpg-2-star-ocean-the-second_milo_north-manifest_unapproved-v01_20261023-225642-163cf811.json": "0cb2b25f115117795dbc2788e9a2f448218c0899b8f2fc9929154ddb324402b1",
    f"{_N}/rpg-2-star-ocean-the-second_milo_north-palette_unapproved-v01_20261023-225642-a3a9c89f.json": "e837c5f76ad17caa7d2b9c269cec261c4813dc2238d6297514ae3d3aaf02554d"}


def load_neutral(d):
    rel, want = NEUTRAL[d]
    png = rb(rp(rel))
    assert sha(png) == want, f"{d} neutral PNG hash drift"
    lay = MN.draw()
    comp = MN.S.compose_layers({n: lay[n] for n in MN.LAYERS})
    assert np.array_equal(comp, decode(png)), f"{d} Milo role layers != neutral PNG"
    return {n: lay[n].copy() for n in MN.LAYERS}, png


# ----------------------------------------------------------------------------- rebind (in memory only)
J.STAMP, J.RUN, J.ACTOR, J.ZIP_DT = STAMP, RUN, ACTOR, ZIP_DT
mx.ZIP_DT = ZIP_DT
J.DIRS = DIRS
J.OUT_REL, J.PKG_REL = "outputs/milo-nw01", "outputs/milo-nw01/pkg"
J.PFX = "rpg-2-star-ocean-the-second_milo_walk"
J.VAR = "unapproved-mnw01-v01"
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
    source.update({
        "visual_id": ACTOR, "direction_scope": "north only (west paused; south committed separately; east not in this task)",
        "task_ids": ["content.char.milo.walk-north"],
        "dependency": {"content.char.milo.static-north": "DONE (neutral source pinned byte-exact)"},
        "groups": {"head": list(HEAD), "torso": list(TORSO), "arm_like": list(ARMLIKE), "legs": ["trousers", "boots"],
                   "case": "square medicine case (screen right, back view) rides torso (bob only); no secondary swing added; disclosed"},
        "walk_model": {"back": f"in place; foot A = viewer-left column (x<40, character's left foot) lifted p4-p11 by {list(J.FB_SWING)}, "
                               "B = x>=40 same shifted 6 phases; arms +-1 texel per column, wristband rides the screen-left "
                               "(x<40) arm column; body down 1 texel at p1,p2,p7,p8, never up",
                       "walk_run": "one cycle used for walk/run at host normal speed 140 logical px/s; no separate run-speed cycle"},
        "source_inputs": {"milo_north_static_author": {"file": "tools/" + _MN_FN, "sha256_text_lf_v1": sha_text(rb(os.path.join(_HERE, _MN_FN)))},
                          "milo_walk_south_author": {"file": "tools/" + _SW_FN, "sha256_text_lf_v1": sha_text(rb(os.path.join(_HERE, _SW_FN))),
                                                     "use": "Milo render_idle/render_fb, roles/palette bindings (south pins checked on import, not written)"},
                          "neutral_pngs": {"north": {"file": NEUTRAL["north"][0], "sha256": NEUTRAL["north"][1]}},
                          "neutral_editables_pinned": NEUTRAL_NATIVE},
        "reused_engine": {"file": "tools/" + _J_FN, "sha256_text_lf_v1": sha_text(rb(os.path.join(_HERE, _J_FN))),
                          "use": "front/back cycle timing, stop_poses, contact_report, leg_transform, serializers; "
                                 "render_idle/render_fb replaced by the msw01 Milo copies (wristband rides arm column)"},
        "reused_helpers": {"file": "tools/" + J._MX_FN, "sha256_text_lf_v1": sha_text(rb(os.path.join(_HERE, J._MX_FN)))},
        "limitations": [
            "back cycle is IN PLACE: a planted foot travels with the host by 11.2 source texels (5.6 logical) per 40 ms; "
            "this is the frozen jexplore39/msw01 front/back residual; NOT slip-free, NOT footlocked",
            "contact metrics are not fluidity, footlock or human motion acceptance",
            "legs are the static leg texels lifted below the knee (no foreshortening repaint); coat and case ride the torso",
            "Milo north static is UNAPPROVED; no art, motion or fluidity acceptance",
            "supplemental stop JSON is not read by the generic loader (immediate idle); stop playback is source scope only",
            "north only: package has no south/west/east entries, is opt-in/non-default and staged under outputs/ (not game/data)"],
        "tool": {"file": "tools/" + os.path.basename(__file__), "sha256_text_lf_v1": sha_text(rb(os.path.abspath(__file__)))}})
    files[old] = (json.dumps(source, indent=2, ensure_ascii=False) + "\n").encode()
    return fsets, files, source


# ----------------------------------------------------------------------------- north-only source checks
def source_checks(fsets, files, source):
    """jexplore39 per-direction checks for north + package/identity checks (the 4-direction cross checks do not apply)."""
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
    ck("north all frames 80x112 binary alpha, clear border, Milo palette only", not bad, bad[:3])
    ck("north static + idle f00 are the exact neutral PNG bytes", e["static"]["sha256"] == NEUTRAL[d][1] == e["idle"][0]["sha256"])
    ck("north counts idle 4 walk 12 stop bridge frames 24", (len(e["idle"]), len(e["walk"]), len(stop_frames)) == (4, 12, 24))
    ck("north every bridge = [walk p, s1, s2, idle f00]", all(
        v[0] == {"ref": "walk", "index": int(k[5:]), "k": 0.0} and v[-1] == {"ref": "idle", "index": 0, "k": 1.0} and len(v) == 4
        for k, v in e["stop_bridges"].items()))
    ck("north idle frames distinct (>=3)", len({files[x["file"]] for x in e["idle"]}) >= 3)
    low = {decode(files[x["file"]])[69:104].tobytes() for x in e["walk"]}
    ck("north walk lower body differs across phases (>=8)", len(low) >= 8, len(low))
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
        ck("north PXO (Milo 11 roles + far-limbs + guides) cels recompose to every frame PNG", okp, e["pxo"]["frames"])
    c = source["contact_check"][d]
    ck("north stop bridges: a grounded foot never moves (host stopped)", c["stop_bridge_grounded_slip_src_max"] == 0, c["stop_bridge_nonzero"][:3])
    ck("north each foot grounded 4 phases per cycle (p0-p3 lifted p4-p11)",
       all(sum(1 for r in c["per_phase_feet"] if r[k]["grounded"]) == 4 for k in ("A", "B")),
       [sum(1 for r in c["per_phase_feet"] if r[k]["grounded"]) for k in ("A", "B")])
    # identity anchors visible in EVERY frame (back view: case white + green cross screen RIGHT, wristband screen LEFT)
    case_c, wb_c = {RGB["g2"]}, {RGB["g1"], RGB["g2"]}
    miss = []
    for x in allf:
        a = decode(files[x["file"]]); m = a[..., 3] == 255
        right = {tuple(v) for v in a[58:80, 50:70][m[58:80, 50:70]][:, :3]}
        left = {tuple(v) for v in a[55:70, 16:30][m[55:70, 16:30]][:, :3]}
        if not (case_c <= right and RGB["w1"] in right and wb_c & left):
            miss.append(x["file"].rsplit("/", 1)[-1])
    ck("identity: case (white + green cross, screen right) and green wristband (screen left) in every frame", not miss, miss[:3])
    eye = {RGB["e1"], RGB["e2"], RGB["m1"]}
    fl = fsets["north"]
    lays = [w[0] for w in fl["walk"]] + [s[0] for p in range(NPH) for s in fl["stop"][p]] + list(fl["idle"])
    nb = sum(1 for lay in lays for n, a in lay if n == "face" and {tuple(int(v) for v in cc) for cc in a[a[..., 3] == 255][:, :3]} & eye)
    ck("north face layer has no eye/mouth colours in any frame (ears/nape only)", nb == 0, {"frames": len(lays), "with_eyes": nb})
    det = 0
    for lay in lays:
        L = dict(lay)
        wy = np.nonzero(L["wristband"][..., 3].any(1))[0]; ay = np.nonzero(J.cols(L["arms"], 0, 40)[..., 3].any(1))[0]
        det += int((wy.min() - ay.min()) != (60 - 38))
    ck("identity: wristband stays on the screen-left arm (constant offset to left-arm top in every frame)", det == 0, det)
    base_case = fl["base"]["case"]
    rig = sum(1 for lay in lays if not any(np.array_equal(dict(lay)["case"], shift(base_case, 0, dy) if dy else base_case) for dy in (0, 1)))
    ck("case layer is the neutral case shifted by 0/+1 texel only (rides torso bob, never detaches)", rig == 0, rig)
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
    ck("package-local registry lists ONLY milo -> this set", list(reg["actors"]) == [ACTOR] and PKG_REL + "/" + reg["actors"][ACTOR] == source["package"]["sprite_set"])
    ck("all written paths are under the assigned root outputs/milo-nw01", all(r.startswith(OUT_REL + "/") for r in files))
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
    c = source["contact_check"]["north"]
    summary = {k: c[k] for k in ("walk_max_world_slip_src_at_40ms_boundaries", "walk_max_world_slip_logical_at_40ms_boundaries",
                                 "flight_phases", "stop_bridge_grounded_slip_src_max")}
    print(json.dumps(summary))
    res = {"tool_sha256_text_lf_v1": source["tool"]["sha256_text_lf_v1"], "rebuild": {"checked": len(files), "ok": n_ok},
           "deterministic": det, "neutral_pins_exact_before_after": pins_ok, "source_checks": sc, "contacts": summary,
           "residual_disclosed": "back in-place planted-foot world slip 11.2 src (5.6 logical) per 40 ms; not footlocked",
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
