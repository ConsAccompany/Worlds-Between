"""Heya SOUTH walk/run loop + phase-aware stop source author (h165sw, UNAPPROVED technical source).

content.char.heya.walk-south. SOUTH ONLY. Thin bounded adapter over the frozen jexplore39 Jiang Lan exploration
author, same reuse pattern as the Lin Que lexplore59, Milo msw01, Muxiu muxsw69 and Yanke yksw105 adapters: its
front/back in-place 12-phase cycle (40 ms, host 140 logical px/s), stop_poses, contact_report, leg_transform and
serializers (make_pxo/make_ora via mexplore23) are reused unchanged. Actor bindings are rebound in memory only
(no Jiang/Lin/Milo/Muxiu/Yanke/Heya file is written):
  - neutral layers come from the Heya south static author draw() and must recompose to the existing Heya south
    static PNG bytes (hash-pinned); the editable neutral PXO/ORA/manifest/palette are read-only pins.
  - Heya 13 roles. head = face/hair/braid (the low braided coil rides the head: bob only, no secondary sway,
    disclosed); torso = dress/coat/apron/belt/strap/bag/herb/scarf (the open clinician coat, apron and bag ride the
    torso: bob only); arm-like = arms (counter-phase +-1 per column); legs = boots, split at x=40 and lifted below
    the knee per foot. The static source has no separate trousers layer; the A-line dress hem is torso-only and is
    NOT lifted, so a lifted boot can pass behind the hem (static-texel limit, disclosed, not a repaint).
    render_idle/render_fb are Heya copies of the jexplore39 functions with only those role-group changes.
One cycle serves walk/run at the host normal speed (no separate faster run cycle exists in this batch).
West/north/east and idle tasks are NOT produced here.

Usage:  <venv python> -X utf8 -I <tool> build|check
Writes only NEW files under outputs/heya-sw165 and game/assets/characters/heya-native-v01/south-walk
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
_H_FN = "rpg-2-star-ocean-the-second_heya_south-static-author_unapproved-v01_20261024-125310-h148s001.py"
TOOL_PINS = {_J_FN: "ae8654f28c89e4c11ef7c52b61fc87ee992af5ae805277998102e4ba9bf80cd5",   # raw bytes
             _H_FN: "3bccc473faba713b7ea096ffa9154dd7b59f91fcc303b393e421ccd2bca1b31e"}
for _fn, _want in TOOL_PINS.items():
    with open(os.path.join(_HERE, _fn), "rb") as _fh:
        assert hashlib.sha256(_fh.read()).hexdigest() == _want, f"reused tool drift: {_fn}"
J = _load(_J_FN, "wb_jexplore39_for_heya_sw")
HS = _load(_H_FN, "wb_heya_south_static_v01")
assert all(HS.PIN_OK.values()), f"Heya static author pins drifted: {HS.PIN_OK}"
mx, sha, sha_text, rb, rp, decode, blank, shift, over = J.mx, J.sha, J.sha_text, J.rb, J.rp, J.decode, J.blank, J.shift, J.over

STAMP, RUN = "20261024-143000", "h165s001"
ACTOR = "heya"
ZIP_DT = (2026, 10, 24, 14, 30, 0)
DIRS = ("south",)
assert (J.W, J.H, J.PIN) == (HS.W, HS.H, HS.PIN) and tuple(HS.BODY_ROWS) == (8, J.SOLE)

ROLES = [n for n in HS.LAYERS if n != "guides"]
PAL = {k: "#" + v for k, v in HS.PAL.items()}
RGB = {k: HS.S.rgb(k) for k in HS.PAL}
INV = {v: k for k, v in RGB.items()}
assert len(INV) == len(RGB)
DARK = {k: k for k in PAL}            # far-limb recolor is side-only; unused for south (identity, disclosed)
HEAD, TORSO, ARMLIKE = ("face", "hair", "braid"), ("dress", "coat", "apron", "belt", "strap", "bag", "herb", "scarf"), ("arms",)
LEGS = ("boots",)
assert set(HEAD + TORSO + ARMLIKE + LEGS) == set(ROLES) and len(ROLES) == 13

_N = "game/assets/characters/heya-native-v01/south"
NEUTRAL = {"south": (f"{_N}/rpg-2-star-ocean-the-second_heya_south-static_unapproved-v01_20261024-125310-231d2b03.png",
                     "f6e60682bc7f5290aff11ec1154e515137a2b0f66a7fd5141ef4a9afa755d2c3")}
NEUTRAL_NATIVE = {  # existing Heya south static package: read-only pins (must stay byte-exact)
    f"{_N}/rpg-2-star-ocean-the-second_heya_south-edit_unapproved-v01_20261024-125310-9665bd23.pxo": "f5613b9d4b787e694eddf0c76bb0de28535495849d427d838c30647b7257b12a",
    f"{_N}/rpg-2-star-ocean-the-second_heya_south-edit_unapproved-v01_20261024-125310-42e46403.ora": "694e105375eded54d605698f6c65862f152a3e0c63a2462dd90fe4073c8aff36",
    f"{_N}/rpg-2-star-ocean-the-second_heya_south-manifest_unapproved-v01_20261024-125310-a9210ea1.json": "d6ddec7e38d74083e6a774d96e7235c9b64fe5ba7b7ec3664f5067f82217d80c",
    f"{_N}/rpg-2-star-ocean-the-second_heya_south-palette_unapproved-v01_20261024-125310-a902fe49.json": "a699845e99d7cc794402b5e31b3e515cafb5459645fbab05d5a4eefb4071e838"}


def load_neutral(d):
    rel, want = NEUTRAL[d]
    png = rb(rp(rel))
    assert sha(png) == want, f"{d} neutral PNG hash drift"
    lay = HS.draw()
    comp = HS.S.compose_layers({n: lay[n] for n in HS.LAYERS})
    assert np.array_equal(comp, decode(png)), f"{d} Heya role layers != neutral PNG"
    return {n: lay[n].copy() for n in HS.LAYERS}, png


# ----------------------------------------------------------------------------- Heya renderer variants
def render_idle(base, i):
    t, h, a = J.IDLE[i]
    out = []
    for n in ROLES:
        dy = h if n in HEAD else (t if n in TORSO else (a if n in ARMLIKE else 0))
        out.append((n, shift(base[n], 0, dy) if dy else base[n].copy()))
    return [("far-limbs", blank())] + out


def render_fb(base, d, q):
    b = q["bob"]
    out, feet = {}, {}
    legs_bt = []
    for key, x0, x1 in (("A", 0, 40), ("B", 40, J.W)):
        lift = q["al"] if key == "A" else q["bl"]
        bt = J.leg_transform(J.cols(base["boots"], x0, x1), 0, lift, b)
        legs_bt.append(bt)
        feet[key] = bt
    out["boots"] = over(legs_bt)
    arms = base["arms"]
    out["arms"] = over([shift(J.cols(arms, 0, 40), 0, b + q["arm_dy_l"]), shift(J.cols(arms, 40, J.W), 0, b + q["arm_dy_r"])])
    out["far-limbs"] = blank()
    for n in ROLES:
        if n not in out:
            out[n] = shift(base[n], 0, b) if b else base[n].copy()
    return [(n, J.clip_floor(out[n])) for n in J.PXO_LAYERS[:-1]], feet


# ----------------------------------------------------------------------------- rebind (in memory only)
J.STAMP, J.RUN, J.ACTOR, J.ZIP_DT = STAMP, RUN, ACTOR, ZIP_DT
mx.ZIP_DT = ZIP_DT
J.DIRS = DIRS
J.OUT_REL, J.PKG_REL = "outputs/heya-sw165", "game/assets/characters/heya-native-v01/south-walk"
J.PFX = "rpg-2-star-ocean-the-second_heya_walk"
J.VAR = "unapproved-h165sw-v01"
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
    source["directions"]["south"]["ora"]["content"] = "supplementary: static neutral 13 Heya role layers + hidden guides"
    source.update({
        "visual_id": ACTOR, "direction_scope": "south only (west/north/east and idle tasks not in this task)",
        "task_ids": ["content.char.heya.walk-south"],
        "dependency": {"content.char.heya.static-south": "DONE (neutral source pinned byte-exact)"},
        "identity": "Bible character-26 / companion #26: 44-year-old clinician; auburn braided coil LOW at the nape, "
                    "cool grey-white medical scarf with long screen-right tail, ivory open clinician coat, pale apron, "
                    "charcoal underdress, dark-red emergency bag + brass clasps at screen-right hip, herb sprig screen "
                    "left, dark gloves, brown leather boots",
        "groups": {"head": list(HEAD), "torso": list(TORSO), "arm_like": list(ARMLIKE), "legs": list(LEGS),
                   "braid": "low nape coil rides the head (bob only); no secondary sway added; disclosed",
                   "coat_apron_bag": "ride the torso (bob only); no cloth secondary motion; disclosed",
                   "boots": "static boot texels split at x=40, lifted below knee p4-p11 per foot; dress hem is torso-only"},
        "walk_model": {"front": f"in place; foot A = viewer-left column (x<40) of boots lifted below the knee p4-p11 "
                                f"by {list(J.FB_SWING)}, B = x>=40 same shifted 6 phases; contact p0 (both planted, "
                                "A at toe-off boundary), plant p0-p3, swing p4-p11; arms +-1 texel per column in "
                                "counter-phase; body down 1 texel at p1,p2,p7,p8, never up",
                       "walk_run": "one cycle used for walk/run at host normal speed 140 logical px/s; no separate run-speed cycle",
                       "frame_hold": "each phase is held 40 ms; host moves continuously; root does not move in the source frames"},
        "source_inputs": {"heya_south_static_author": {"file": "tools/" + _H_FN, "sha256_raw": TOOL_PINS[_H_FN],
                                                         "sha256_text_lf_v1": sha_text(rb(os.path.join(_HERE, _H_FN)))},
                          "neutral_pngs": {"south": {"file": NEUTRAL["south"][0], "sha256": NEUTRAL["south"][1]}},
                          "neutral_editables_pinned": NEUTRAL_NATIVE,
                          "static_qa": "outputs/heya-s148/coordinator-author-check.log (HEYA_SOUTH_V01_ALL_OK)"},
        "reused_engine": {"file": "tools/" + _J_FN, "sha256_raw": TOOL_PINS[_J_FN],
                          "sha256_text_lf_v1": sha_text(rb(os.path.join(_HERE, _J_FN))),
                          "use": "front/back cycle timing, stop_poses, contact_report, leg_transform, serializers; "
                                 "render_idle/render_fb replaced by Heya copies (boots-only legs; 13 Heya roles)"},
        "reused_helpers": {"file": "tools/" + J._MX_FN, "sha256_text_lf_v1": sha_text(rb(os.path.join(_HERE, J._MX_FN)))},
        "limitations": [
            "front cycle is IN PLACE: a planted foot travels with the host by 11.2 source texels (5.6 logical) per 40 ms; "
            "this is the frozen jexplore39/lexplore59/msw01/muxsw69/yksw105 front residual, reused without threshold change; "
            "NOT slip-free, NOT footlocked",
            "contact metrics are not fluidity, footlock or human motion acceptance",
            "legs are the static boot texels lifted below the knee row 80 (no foreshortening repaint); the Heya static has no "
            "separate trousers layer, and the A-line dress hem is torso-only, so a lifted boot passes behind the static hem "
            "and the lower-body silhouette is coarse (static-texel limit, disclosed)",
            "braid, scarf tail, coat/apron and bag ride head/torso (no secondary motion); coarse frozen static, cosmetic "
            "refinement deferred",
            "Heya south static and portrait are UNAPPROVED; no art, motion or fluidity acceptance",
            "supplemental stop JSON is not read by the generic loader (immediate idle); stop playback is source scope only",
            "south only: package has no west/north/east entries and is opt-in/non-default"],
        "tool": {"file": "tools/" + os.path.basename(__file__), "sha256_text_lf_v1": sha_text(rb(os.path.abspath(__file__)))}})
    files[old] = (json.dumps(source, indent=2, ensure_ascii=False) + "\n").encode()
    files[PKG_REL + "/.gdignore"] = b""
    files[PKG_REL + "/.gitattributes"] = (
        "# Batch165 h165sw (content.char.heya.walk-south): preserve raw bytes on checkout.\n"
        "# Opt-in south-walk PNGs and JSON are hash-pinned; no text/EOL conversion.\n* -text -eol\n").encode()
    return fsets, files, source


# ----------------------------------------------------------------------------- south-only source checks
def source_checks(fsets, files, source):
    """jexplore39 per-direction checks for south + package/identity checks (4-direction cross checks do not apply)."""
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
    ck("south all frames 80x112 binary alpha, clear border, Heya palette only", not bad, bad[:3])
    ck("south static + idle f00 are the exact neutral PNG bytes", e["static"]["sha256"] == NEUTRAL[d][1] == e["idle"][0]["sha256"])
    ck("south counts idle 4 walk 12 stop bridge frames 24", (len(e["idle"]), len(e["walk"]), len(stop_frames)) == (4, 12, 24))
    ck("south every bridge = [walk p, s1, s2, idle f00]", all(
        v[0] == {"ref": "walk", "index": int(k[5:]), "k": 0.0} and v[-1] == {"ref": "idle", "index": 0, "k": 1.0} and len(v) == 4
        for k, v in e["stop_bridges"].items()))
    ck("south idle frames distinct (>=3)", len({files[x["file"]] for x in e["idle"]}) >= 3)
    low = {decode(files[x["file"]])[80:104].tobytes() for x in e["walk"]}
    ck("south walk lower body differs across phases (>=8)", len(low) >= 8, len(low))
    ck("south no walk phase equals the neutral bitmap", all(x["sha256"] != NEUTRAL[d][1] for x in e["walk"]))
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
        ck("south PXO (Heya 13 roles + far-limbs + guides) cels recompose to every frame PNG", okp, e["pxo"]["frames"])
    c = source["contact_check"][d]
    ck("south stop bridges: a grounded foot never moves (host stopped)", c["stop_bridge_grounded_slip_src_max"] == 0, c["stop_bridge_nonzero"][:3])
    ck("south each foot grounded 4 phases per cycle (p0-p3 lifted p4-p11)",
       all(sum(1 for r in c["per_phase_feet"] if r[k]["grounded"]) == 4 for k in ("A", "B")),
       [sum(1 for r in c["per_phase_feet"] if r[k]["grounded"]) for k in ("A", "B")])
    # identity anchors visible in EVERY frame: low braided coil, grey-white scarf, dark-red bag, herb, ivory coat, pale apron
    hair_c, scarf_c, bag_c, herb_c = {RGB[k] for k in ("h1", "h2", "h3")}, {RGB[k] for k in ("f1", "f2", "f3")}, \
        {RGB[k] for k in ("b1", "b2", "b3")}, {RGB[k] for k in ("n1", "n2")}
    coat_c, apron_c = {RGB[k] for k in ("w1", "w2", "w3")}, {RGB[k] for k in ("v1", "v2", "v3")}
    miss = []
    for x in allf:
        a = decode(files[x["file"]]); m = a[..., 3] == 255
        reg = lambda y0, y1, x0, x1: {tuple(v) for v in a[y0:y1, x0:x1][m[y0:y1, x0:x1]][:, :3]}
        if not (hair_c & reg(24, 42, 18, 62) and scarf_c & reg(32, 64, 28, 54) and bag_c & reg(58, 82, 50, 66)
                and herb_c & reg(40, 54, 28, 40) and coat_c & reg(30, 90, 24, 56) and apron_c & reg(58, 88, 28, 52)):
            miss.append(x["file"].rsplit("/", 1)[-1])
    ck("identity: low braid, grey-white scarf, dark-red bag, herb, ivory coat + pale apron in every frame", not miss, miss[:3])
    # braid rides the head exactly (same dy as hair top edge)
    fl = fsets["south"]
    det = 0
    for lay in [w[0] for w in fl["walk"]] + [s[0] for p in range(NPH) for s in fl["stop"][p]] + list(fl["idle"]):
        L = dict(lay)
        by = np.nonzero(L["braid"][..., 3].any(1))[0]; hy = np.nonzero(L["hair"][..., 3].any(1))[0]
        det += int((by.min() - hy.min()) != (np.nonzero(fl["base"]["braid"][..., 3].any(1))[0].min()
                                             - np.nonzero(fl["base"]["hair"][..., 3].any(1))[0].min()))
    ck("identity: braid stays on the head (constant offset to hair top in every frame)", det == 0, det)
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
    ck("package-local registry lists ONLY heya -> this set", list(reg["actors"]) == [ACTOR] and PKG_REL + "/" + reg["actors"][ACTOR] == source["package"]["sprite_set"])
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
