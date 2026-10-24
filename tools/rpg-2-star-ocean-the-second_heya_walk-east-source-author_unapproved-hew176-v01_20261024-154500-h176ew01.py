"""Heya EAST walk/run loop + phase-aware stop source author (h176ew01, UNAPPROVED technical source).

content.char.heya.walk-east, batch176. EAST ONLY. Thin adapter over the frozen jexplore39 Jiang Lan exploration
author (side gait, stop_poses, contact_report, leg/arm transforms, serializers) using the established Yanke ykww107 /
Muxiu b84ww001 side-profile method, retargeted to the Heya east static roles:
  - neutral layers come from the Heya east static author draw() and must recompose to the installed east static
    PNG bytes (hash-pinned); the editable neutral PXO/ORA/manifest/palette are read-only pins.
  - Heya 13 roles. head = face/hair/braid (the low nape coil rides the head: bob only, no secondary sway, disclosed);
    torso = dress/coat/apron/belt/strap/bag/herb/scarf (open coat, apron, bag and scarf ride the torso: bob only);
    arm-like = arms (near arm only in the east profile; sheared about the shoulder); legs = boots only.
  - The east static has no trousers layer. Near boot = the near (character-right) boot columns at screen x >= 38;
    far limb = the complete boot silhouette recoloured with the pinned Heya DARK table (continuous dark boot by
    construction, no off-palette pixels). The A-line dress hem is torso-only and is NOT lifted, so a lifted boot can
    pass behind the static hem (static-texel limit, disclosed, not a repaint). Far limb is drawn behind in the
    "far-limbs" cel; no FAR_BASE is added because the complete boots silhouette already carries the far toe offset.
One cycle serves walk/run at host normal speed (no separate faster run cycle exists in this batch).
East only; south/north/west and idle tasks are NOT produced here; previous tools/statics are not modified.

Usage:  <venv python> -X utf8 -I <tool> build|check
Writes only NEW files under outputs/heya-ew176 and game/assets/characters/heya-native-v01/east-walk
(refuses to overwrite different bytes). Optional WB_STAGE_REL (relative outputs/ path) mirrors all writes and
rebuild reads into that staging tree; manifest paths stay repo-relative. No runtime default is changed.
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
_E_FN = "rpg-2-star-ocean-the-second_heya_east-static-author_unapproved-v01_20261024-141500-h155e001.py"
_R84_FN = "rpg-2-star-ocean-the-second_yanke_walk-west-source-author_unapproved-ykww107-v01_20261024-110000-y107ww01.py"
TOOL_PINS = {_J_FN: "ae8654f28c89e4c11ef7c52b61fc87ee992af5ae805277998102e4ba9bf80cd5",   # raw bytes
             _E_FN: "42c06afb67653975e3e2a385f2e7cd30c5ba936080f3fc14e9bb7b1e8b5c23e0"}
for _fn, _want in TOOL_PINS.items():
    with open(os.path.join(_HERE, _fn), "rb") as _fh:
        assert hashlib.sha256(_fh.read()).hexdigest() == _want, f"reused tool drift: {_fn}"
J = _load(_J_FN, "wb_jexplore39_for_heya_ww")
W = _load(_E_FN, "wb_heya_east_static_v01")
assert all(W.PIN_OK.values()), f"Heya east static author pins drifted: {W.PIN_OK}"
assert all(W.WEST.PIN_OK.values()) and all(W.WEST.MS.PIN_OK.values()), "Heya east/helper transitive pins drifted"
mx, sha, sha_text, rb, rp, decode, blank, shift, over = J.mx, J.sha, J.sha_text, J.rb, J.rp, J.decode, J.blank, J.shift, J.over

STAMP, RUN = "20261024-154500", "h176ew01"
ACTOR = "heya"
ZIP_DT = (2026, 10, 24, 15, 45, 0)
DIRS = ("east",)
assert (J.W, J.H, J.PIN) == (W.W, W.H, W.PIN) and tuple(W.BODY_ROWS) == (8, J.SOLE)

ROLES = [n for n in W.LAYERS if n != "guides"]
PAL = {k: "#" + v for k, v in W.PAL.items()}
RGB = {k: W.S.rgb(k) for k in W.PAL}
INV = {v: k for k, v in RGB.items()}
assert len(INV) == len(RGB)
# far-boot darkening: only boot leather / sole / eyelet colours occur in the boots layer
DARK = {k: k for k in PAL}
DARK.update({"r1": "r2", "r2": "r3", "r3": "r3", "y2": "y2"})
HEAD, TORSO, ARMLIKE = ("face", "hair", "braid"), ("dress", "coat", "apron", "belt", "strap", "bag", "herb", "scarf"), ("arms",)
LEGS = ("boots",)
assert set(HEAD + TORSO + ARMLIKE + LEGS) == set(ROLES) and len(ROLES) == 13
NEAR_MIN_X = 38          # east near boot columns (f <= 3); x <= 36 is the visible far boot toe/heel

_N = "game/assets/characters/heya-native-v01/east"
NEUTRAL = {"east": (f"{_N}/rpg-2-star-ocean-the-second_heya_east-static_unapproved-v01_20261024-141500-6041ee95.png",
                    "273e5e854121fa8ec92dc74e28a67be35920da6442fc20571ff053453fdf9dd4")}
NEUTRAL_NATIVE = {
    f"{_N}/rpg-2-star-ocean-the-second_heya_east-edit_unapproved-v01_20261024-141500-5493fe7b.pxo": "45ab6257e31b20fb756e1d18c687d1716c73d2fa22489737ed86fd5348e2bf56",
    f"{_N}/rpg-2-star-ocean-the-second_heya_east-edit_unapproved-v01_20261024-141500-d23c7857.ora": "0cf8b0b465560bf6328de320f2e40f356cb5d304c3c546227de3a2ba12e8bc91",
    f"{_N}/rpg-2-star-ocean-the-second_heya_east-manifest_unapproved-v01_20261024-141500-489081a6.json": "dc5e13978247c8781955785f2d5ef46a0ac0fe26ced3e03ed98ea1a871a6302d",
    f"{_N}/rpg-2-star-ocean-the-second_heya_east-palette_unapproved-v01_20261024-141500-f7eba38b.json": "6af85c7ac9e1dfc76a44a53864d9a7ef58c7d02d1c3e3e8ab1d71b50e6d55311"}


def load_neutral(d):
    rel, want = NEUTRAL[d]
    png = rb(rp(rel))
    assert sha(png) == want, f"{d} neutral PNG hash drift"
    lay = W.draw()
    comp = W.S.compose_layers({n: lay[n] for n in W.LAYERS})
    assert np.array_equal(comp, decode(png)), f"{d} Heya role layers != neutral PNG"
    return {n: lay[n].copy() for n in W.LAYERS}, png


# ----------------------------------------------------------------------------- Heya east renderer
def render_idle(base, i):
    t, h, a = J.IDLE[i]
    out = []
    for n in ROLES:
        dy = h if n in HEAD else (t if n in TORSO else (a if n in ARMLIKE else 0))
        out.append((n, shift(base[n], 0, dy) if dy else base[n].copy()))
    return [("far-limbs", blank())] + out


def side_parts(base, d):
    """Near boot = Heya near (screen-right) columns; far limb = complete dark boot silhouette (b84/ykww107 method)."""
    near_bt = base["boots"].copy()
    near_bt[:, :NEAR_MIN_X] = 0
    far_leg = J.recolor(base["boots"], DARK)
    return {"near_bt": near_bt, "far_leg": far_leg}


def static_feet(base, d):
    p = side_parts(base, d)
    return {"A": p["near_bt"], "B": p["far_leg"]}


def render_side(base, parts, d, q):
    s = J.side_sign(d)                       # east = +1 (forward is screen right)
    b = q["bob"]
    knee_a = s * (q["al"] * 0.6)
    knee_b = s * (q["bl"] * 0.6)
    near_bt = J.leg_transform(parts["near_bt"], s * q["ax"], q["al"], b, knee_a)
    far_leg = J.leg_transform(parts["far_leg"], s * q["bx"], q["bl"], b, knee_b)
    out = {"far-limbs": far_leg, "boots": near_bt,
           "arms": J.arm_transform(base["arms"], s * q["swing"], b)}
    for n in ROLES:
        if n not in out:
            out[n] = shift(base[n], 0, b) if b else base[n].copy()
    return [(n, J.clip_floor(out[n])) for n in J.PXO_LAYERS[:-1]], {"A": near_bt, "B": far_leg}


# ----------------------------------------------------------------------------- rebind (in memory only)
J.STAMP, J.RUN, J.ACTOR, J.ZIP_DT = STAMP, RUN, ACTOR, ZIP_DT
mx.ZIP_DT = ZIP_DT
J.DIRS = DIRS
J.OUT_REL, J.PKG_REL = "outputs/heya-ew176", "game/assets/characters/heya-native-v01/east-walk"
J.PFX = "rpg-2-star-ocean-the-second_heya_walk"
J.VAR = "unapproved-h176ew01-v01"
J.ROLES, J.PXO_LAYERS = ROLES, ["far-limbs"] + ROLES + ["guides"]
J.HEAD, J.TORSO = HEAD, TORSO
J.PAL, J.RGB, J.INV, J.DARK = PAL, RGB, INV, DARK
J.render_idle, J.render_side, J.side_parts = render_idle, render_side, side_parts
J.static_feet = static_feet
J.NEUTRAL, J.NEUTRAL_NATIVE, J.load_neutral = NEUTRAL, NEUTRAL_NATIVE, load_neutral
OUT_REL, PKG_REL, fname = J.OUT_REL, J.PKG_REL, J.fname


def stage_rel(rel):
    stage = os.environ.get("WB_STAGE_REL", "").strip("/")
    if not stage:
        return rel
    parts = stage.split("/")
    if parts[0] != "outputs" or len(parts) < 2 or any(p in ("", ".", "..") for p in parts):
        raise SystemExit("WB_STAGE_REL must be a relative path under outputs/")
    return stage + "/" + rel


def build_all():
    fsets, files, source = J.build_all()
    for k in ("source_inputs", "reused_helpers", "tool", "limitations", "task_ids", "visual_id", "walk_model"):
        source.pop(k)
    source["directions"]["east"]["ora"]["content"] = "supplementary: static neutral 13 Heya east role layers + hidden guides"
    source.update({
        "visual_id": ACTOR, "direction_scope": "east only (south/north/west and idle tasks not in this task)",
        "task_ids": ["content.char.heya.walk-east"],
        "dependency": {"content.char.heya.static-east": "DONE (neutral source pinned byte-exact)"},
        "identity": "Bible character-26 / companion #26: 44-year-old clinician; auburn braided coil LOW at the nape, "
                    "cool grey-white medical scarf with long near-front tail, ivory open clinician coat, pale apron, "
                    "charcoal underdress, dark-red emergency bag + brass clasps on the far (anatomical-left) hip, herb sprig, "
                    "dark gloves, brown leather boots with folded cuff and brass eyelet",
        "groups": {"head": list(HEAD), "torso": list(TORSO), "arm_like": list(ARMLIKE), "legs": list(LEGS),
                   "braid": "low nape coil rides the head (bob only); no secondary sway added; disclosed",
                   "coat_apron_bag_scarf": "ride the torso (bob only); no cloth secondary motion; disclosed",
                   "boots": "near boot = static columns x>=38; far limb = complete boot silhouette recoloured through "
                            "the pinned DARK table; dress hem is torso-only and not lifted"},
        "walk_model": {"side": "foot A = near boot planted p0-p3 at local +16.8/+5.6/-5.6/-16.8 (forward, rounded), "
                               f"swing p4-p11 (ease, lift up to {J.SWING_LIFT}); foot B = complete recoloured far boot, "
                               "same cycle shifted 6 phases; flight at p4,p5,p10,p11 (jog-like stride for 140 px/s); "
                               "no FAR_BASE added (far toe offset is already in the complete boot silhouette)",
                       "walk_run": "one cycle used for walk/run at host normal speed 140 logical px/s; no separate run-speed cycle",
                       "frame_hold": "each phase is held 40 ms; host moves continuously; root does not move in the source frames",
                       "bob": "body down 1 texel at p1,p2,p7,p8; never up",
                       "arms": "near arm shear about the shoulder opposite the near leg (+-6); far arm occluded in east profile"},
        "source_inputs": {"heya_east_static_author": {"file": "tools/" + _E_FN, "sha256_raw": TOOL_PINS[_E_FN],
                                                       "sha256_text_lf_v1": sha_text(rb(os.path.join(_HERE, _E_FN)))},
                          "neutral_pngs": {"east": {"file": NEUTRAL["east"][0], "sha256": NEUTRAL["east"][1]}},
                          "neutral_editables_pinned": NEUTRAL_NATIVE,
                          "static_qa": "outputs/heya-e155/author-check.log (HEYA_EAST_V01_ALL_OK)",
                          "method_reference": {"file": "tools/" + _R84_FN,
                                               "sha256_raw": sha(rb(os.path.join(_HERE, _R84_FN))),
                                               "use": "pattern only (not imported)"}},
        "reused_engine": {"file": "tools/" + _J_FN, "sha256_raw": TOOL_PINS[_J_FN],
                          "sha256_text_lf_v1": sha_text(rb(os.path.join(_HERE, _J_FN))),
                          "use": "side cycle timing/stance/lift, stop_poses, contact_report, leg_transform, arm_transform, "
                                 "recolor, serializers; Heya east renderer replaces Jiang roles"},
        "reused_helpers": {"file": "tools/" + J._MX_FN, "sha256_text_lf_v1": sha_text(rb(os.path.join(_HERE, J._MX_FN)))},
        "limitations": [
            "side planted foot residual at 40 ms boundaries is integer rounding of 11.2 src/phase (see contact_check); "
            "between boundaries the host moves continuously while the frame is held, so at 60 fps a planted foot sweeps "
            "the listed excursion and snaps back (frame quantization, disclosed); NOT footlocked, NOT slip-free",
            "far limb is the complete boot silhouette recoloured through the pinned DARK table; only the near boot "
            "columns are drawn in the near boots cel, so the far toe is carried in the far-limbs cel",
            "legs are sheared static boot texels (no foreshortening repaint); the A-line dress hem is torso-only and "
            "not lifted, so a lifted boot can pass behind the static hem (coarse lower-body silhouette, disclosed)",
            "braid, scarf tail, coat/apron/bag ride head/torso (no secondary motion); coarse frozen static, cosmetic "
            "refinement deferred",
            "Heya east static and portrait are UNAPPROVED; no art, motion or fluidity acceptance",
            "supplemental stop JSON is not read by the generic loader (immediate idle); stop playback is source scope only",
            "east only: package has no south/north/west entries and is opt-in/non-default"],
        "tool": {"file": "tools/" + os.path.basename(__file__), "sha256_text_lf_v1": sha_text(rb(os.path.abspath(__file__)))}})
    files[f"{OUT_REL}/{fname('source-manifest', 'json')}"] = (json.dumps(source, indent=2, ensure_ascii=False) + "\n").encode()
    files[PKG_REL + "/.gdignore"] = b""
    files[PKG_REL + "/.gitattributes"] = (
        "# Batch167 h176ew01 (content.char.heya.walk-east): preserve raw bytes on checkout.\n"
        "# Opt-in east-walk PNGs and JSON are hash-pinned; no text/EOL conversion.\n* -text -eol\n").encode()
    return fsets, files, source


# ----------------------------------------------------------------------------- east-only source checks
def source_checks(fsets, files, source):
    import io, zipfile
    res = []

    def ck(name, ok, detail=""):
        res.append({"check": name, "pass": bool(ok), "detail": detail})

    Wd, Hd, NPH = J.W, J.H, J.NPH
    pal = set(RGB.values())
    d = "east"
    e = source["directions"][d]
    stop_frames = [s for p in range(NPH) for s in e["stop_bridges"][f"phase{p}"] if "file" in s]
    allf = [e["static"]] + e["idle"] + e["walk"] + stop_frames
    bad = []
    for x in allf:
        a = decode(files[x["file"]]); al = a[..., 3]
        if a.shape != (Hd, Wd, 4) or set(np.unique(al)) - {0, 255} or al[0].any() or al[-1].any() or al[:, 0].any() or al[:, -1].any():
            bad.append(x["file"])
        if {tuple(c) for c in a[al == 255][:, :3]} - pal:
            bad.append(x["file"] + " palette")
    ck("east all frames 80x112 binary alpha, clear border, Heya palette only", not bad, bad[:3])
    ck("east static + idle f00 are the exact neutral PNG bytes", e["static"]["sha256"] == NEUTRAL[d][1] == e["idle"][0]["sha256"])
    ck("east counts idle 4 walk 12 stop bridge frames 24", (len(e["idle"]), len(e["walk"]), len(stop_frames)) == (4, 12, 24))
    ck("east every bridge = [walk p, s1, s2, idle f00]", all(
        v[0] == {"ref": "walk", "index": int(k[5:]), "k": 0.0} and v[-1] == {"ref": "idle", "index": 0, "k": 1.0} and len(v) == 4
        for k, v in e["stop_bridges"].items()))
    ck("east idle frames distinct (>=3)", len({files[x["file"]] for x in e["idle"]}) >= 3)
    low = {decode(files[x["file"]])[80:104].tobytes() for x in e["walk"]}
    ck("east walk lower body differs across phases (>=8)", len(low) >= 8, len(low))
    ck("east no walk phase equals the neutral bitmap", all(x["sha256"] != NEUTRAL[d][1] for x in e["walk"]))
    hs = [int(np.nonzero(decode(files[x["file"]])[..., 3].any(1))[0].min()) for x in allf]
    ck("east top row never above neutral (body never shifted up)", min(hs) >= 8, [min(hs), max(hs)])
    with zipfile.ZipFile(io.BytesIO(files[e["ora"]["file"]])) as z:
        comp = over([decode(z.read(f"data/{n}.png")) for n in ROLES])
        ck("east ORA role layers recompose to neutral PNG", np.array_equal(comp, decode(files[e["static"]["file"]])) and
           z.read("mergedimage.png") == files[e["static"]["file"]])
    with zipfile.ZipFile(io.BytesIO(files[e["pxo"]["file"]])) as z:
        nl = len(J.PXO_LAYERS)
        okp = len(allf) == e["pxo"]["frames"]
        okp &= [l["name"] for l in json.loads(z.read("data.json"))["layers"]] == J.PXO_LAYERS
        for fi, x in enumerate(allf, start=1):
            lays = [np.frombuffer(z.read(f"image_data/frames/{fi}/layer_{li}"), np.uint8).reshape(Hd, Wd, 4) for li in range(1, nl)]
            okp &= np.array_equal(over(lays), decode(files[x["file"]]))
        ck("east PXO (Heya 13 roles + far-limbs + guides) cels recompose to every frame PNG", okp, e["pxo"]["frames"])
    c = source["contact_check"][d]
    ck("east side planted foot world slip at 40 ms boundaries <= 1 source texel (rounding of 11.2)",
       c["walk_max_world_slip_src_at_40ms_boundaries"] <= 1.0,
       {"max_src": c["walk_max_world_slip_src_at_40ms_boundaries"],
        "60fps_excursion_src": c["walk_planted_foot_world_excursion_src_60fps_samples"]})
    ck("east each foot grounded 4 phases per cycle", all(sum(1 for r in c["per_phase_feet"] if r[k]["grounded"]) == 4 for k in ("A", "B")),
       [sum(1 for r in c["per_phase_feet"] if r[k]["grounded"]) for k in ("A", "B")])
    ck("east stop bridges: a grounded foot never moves (host stopped)", c["stop_bridge_grounded_slip_src_max"] == 0,
       c["stop_bridge_nonzero"][:3])
    # identity anchors visible in EVERY frame: low braid, grey-white scarf, dark-red bag, herb, ivory coat, pale apron
    hair_c = {RGB[k] for k in ("h1", "h2", "h3", "h4")}
    scarf_c, bag_c, herb_c = {RGB[k] for k in ("f1", "f2", "f3")}, {RGB[k] for k in ("b1", "b2", "b3")}, {RGB[k] for k in ("n1", "n2")}
    coat_c, apron_c = {RGB[k] for k in ("w1", "w2", "w3")}, {RGB[k] for k in ("v1", "v2", "v3")}
    miss = []
    for x in allf:
        a = decode(files[x["file"]]); m = a[..., 3] == 255
        reg = lambda y0, y1, x0, x1: {tuple(v) for v in a[y0:y1, x0:x1][m[y0:y1, x0:x1]][:, :3]}
        if not (hair_c & reg(8, 42, 24, 52) and scarf_c & reg(32, 58, 28, 50) and bag_c & reg(56, 84, 20, 34)
                and herb_c & reg(42, 53, 42, 52) and coat_c & reg(30, 90, 28, 48) and apron_c & reg(56, 88, 27, 49)):
            miss.append(x["file"].rsplit("/", 1)[-1])
    ck("identity: low braid, grey-white scarf, dark-red bag, herb, ivory coat + pale apron in every frame", not miss, miss[:3])
    fl = fsets["east"]
    det = 0
    for lay in [w[0] for w in fl["walk"]] + [s[0] for p in range(NPH) for s in fl["stop"][p]] + list(fl["idle"]):
        L = dict(lay)
        by = np.nonzero(L["braid"][..., 3].any(1))[0]; hy = np.nonzero(L["hair"][..., 3].any(1))[0]
        det += int((by.min() - hy.min()) != (np.nonzero(fl["base"]["braid"][..., 3].any(1))[0].min()
                                             - np.nonzero(fl["base"]["hair"][..., 3].any(1))[0].min()))
    ck("identity: braid stays on the head (constant offset to hair top in every frame)", det == 0, det)
    # structural far limb: one continuous darkened boot silhouette in every walk/stop cel
    def _far_errors(a):
        m = a[..., 3] == 255
        if not m.any():
            return ["empty far-limbs cel"]
        ys, xs = np.nonzero(m)
        errs = []
        if ys.max() - ys.min() < 10:
            errs.append(f"span {int(ys.max() - ys.min())}<10")
        if any(m[y].sum() < 2 for y in range(int(ys.min()), int(ys.max()) + 1)):
            errs.append("1-texel string row")
        seen = np.zeros_like(m); stack = [(int(ys[0]), int(xs[0]))]
        while stack:
            y, x = stack.pop()
            if not (0 <= y < J.H and 0 <= x < J.W) or seen[y, x] or not m[y, x]:
                continue
            seen[y, x] = True
            for dy in (-1, 0, 1):
                for dx in (-1, 0, 1):
                    if dy or dx:
                        stack.append((y + dy, x + dx))
        if not np.array_equal(seen, m):
            errs.append("disconnected far-limb fragments")
        keys = {INV[tuple(int(v) for v in a[y, x, :3])] for y, x in zip(*np.nonzero(m))}
        if keys - {"r2", "r3", "y2"}:
            errs.append("far limb holds non-darkened colours " + str(sorted(keys - {"r2", "r3", "y2"})))
        return errs

    far_bad = []
    near_bad = []
    for tag_, lay in ([("walk", w) for w in fl["walk"]] + [("stop", s) for p in range(NPH) for s in fl["stop"][p]]):
        L = dict(lay[0])
        errs = _far_errors(L["far-limbs"])
        if errs:
            far_bad.append([tag_, errs])
    # static part split (before gait shear): near boot must exclude far-only columns, far limb must include them
    base_parts = side_parts(fsets["east"]["base"], "east")
    if base_parts["near_bt"][:, :NEAR_MIN_X, 3].any() or not base_parts["far_leg"][:, :NEAR_MIN_X, 3].any():
        near_bad.append("static side_parts split")
    ck("structural far limb: every walk/stop cel is one continuous darkened boot silhouette (8-connected, no string)",
       not far_bad, far_bad[:3])
    ck("near boots cel excludes far-only columns (x < 38)", not near_bad, near_bad[:3])
    pk = json.loads(files[source["package"]["sprite_set"]])
    paths = [f["file"] for a in pk["actions"].values() for v in a.values() for f in v]
    durs = [f["duration_ms"] for a in pk["actions"].values() for v in a.values() for f in v]
    ok = pk["schema"] == "worlds-between.exploration-sprite-set.v1" and pk["actor_id"] == ACTOR and \
        set(pk["actions"]) == {"idle", "walk"} and all(set(pk["actions"][a]) == {"east"} for a in pk["actions"])
    ok &= all(isinstance(x, int) and 40 <= x <= 2000 for x in durs)
    ok &= all(files[PKG_REL + "/" + p] == files[OUT_REL + "/" + p] for p in paths)
    ck("runtime sprite set: schema/actor/east only/explicit durations/relative byte-equal PNG copies", ok, len(paths))
    stp = json.loads(files[source["package"]["stop_supplemental"]])
    sp = [s["file"] for v in stp["phase_bridges"]["east"].values() for s in v if "file" in s]
    ck("stop supplemental: actor, east only, 24 bridge frames, runtime_default false, byte-equal copies",
       stp["actor_id"] == ACTOR and list(stp["phase_bridges"]) == ["east"] and len(sp) == 24 and stp["runtime_default"] is False
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
        targets = {stage_rel(rel): b for rel, b in files.items()}
        for rel, b in targets.items():
            p = rp(rel)
            if os.path.exists(J._fs(p)) and rb(p) != b:
                raise SystemExit(f"refusing to overwrite different bytes: {rel}")
        mx.write_all(targets)
        print(f"WROTE {len(files)} files" + (f" under {stage_rel('')}" if stage_rel("") else ""))
    fails, n_ok = [], 0
    for rel, b in files.items():
        try:
            if rb(rp(stage_rel(rel))) == b:
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
    c = source["contact_check"]["east"]
    summary = {k: c[k] for k in ("walk_max_world_slip_src_at_40ms_boundaries", "walk_max_world_slip_logical_at_40ms_boundaries",
                                 "walk_planted_foot_world_excursion_src_60fps_samples",
                                 "walk_planted_foot_world_excursion_logical_60fps_samples",
                                 "flight_phases", "stop_bridge_grounded_slip_src_max")}
    print(json.dumps(summary))
    res = {"tool_sha256_text_lf_v1": source["tool"]["sha256_text_lf_v1"], "rebuild": {"checked": len(files), "ok": n_ok},
           "deterministic": det, "neutral_pins_exact_before_after": pins_ok, "source_checks": sc, "contacts": summary,
           "residual_disclosed": "side planted-foot world slip is integer rounding of 11.2 src/40 ms at boundaries; "
                                 "between held frames the host moves continuously (60 fps excursion reported); not footlocked",
           "not_run_here": ["Pixelorama native export (independent checker)", "Godot import/runtime", "normal-speed movie"],
           "fails": fails}
    print("RESULT", "PASS" if not fails else "FAIL", json.dumps(fails[:12]))
    out = rp(stage_rel(f"{OUT_REL}/{fname('check-result-' + mode, 'json')}"))
    os.makedirs(J._fs(os.path.dirname(out)), exist_ok=True)
    stem, ext = out[:-5], out[-5:]
    digest = sha((json.dumps(res) + "\n").encode())[:8]
    n = 0
    while True:
        cand = out if n == 0 else f"{stem}-{digest}" + (f"-{n}" if n > 1 else "") + ext
        try:
            with open(J._fs(cand), "xb") as fh:
                fh.write((json.dumps(res, indent=2) + "\n").encode())
            break
        except FileExistsError:
            n += 1
            if n > 9999:
                raise
    return 0 if not fails else 1


if __name__ == "__main__":
    sys.exit(main())
