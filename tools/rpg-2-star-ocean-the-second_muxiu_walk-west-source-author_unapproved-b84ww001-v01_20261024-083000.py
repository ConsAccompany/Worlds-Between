"""Muxiu WEST walk/run loop + phase-aware stop source author (b84ww001, UNAPPROVED technical source).

content.char.muxiu.walk-west, batch84 second serial job. WEST ONLY. Bounded structural limb repair over the
preserved b78ww001-v01r1 author: the old adapter split ONE neutral boot/wrap/trouser into front/back fragments;
its "far boot" mask (x<=32) kept only a 2-5 texel boot sliver while the far wrap/trouser masks kept the back
fragments, so the far limb read as a thin detached dark string with no continuous clothed leg.
CHANGE OF METHOD (once): the far limb is now an explicitly authored COMPLETE occluded limb silhouette - the whole
near-role boot + legwrap + below-hip trouser composite recoloured with the pinned Muxiu DARK far-shading table
(r1->r2->r3, t1->t2->t3->t4, w1->w2->w3, q1->q2) and articulated with the same far leg_transform. It is therefore
continuous boot->wrap->trouser by construction, with deliberate occlusion under the cloak and behind the near leg,
instead of moving a neutral sliver. No arbitrary dark pixels and no palette additions.

Thin adapter over the frozen jexplore39 Jiang Lan exploration author (side gait, stop_poses, contact_report,
serializers) and the final Muxiu west static author r2 (neutral layers/palette). Canonical
content.char.muxiu.walk-south remains TODO; it is NOT a dependency of west and is neither produced nor claimed
here. Actor bindings are rebound in memory only (no Jiang/Lin/Milo/Muxiu static file is written):
  - neutral layers come from the Muxiu west static author draw() and must recompose to the installed west static
    PNG bytes (hash-pinned); the editable neutral PXO/ORA/manifest/palette are read-only pins.
  - Muxiu 13 roles. head = face/hair/braid (braid rides the head: bob only, no secondary sway, disclosed);
    torso = shirt/belt/pouches/cloak/whistle; near arm-like = arms + bracelet (same arm_transform, so the rope
    bracelet never detaches); legs = trousers (rows >= LEG_TOP) + legwraps + boots, articulated together.
  - Side gait: near and far feet use the frozen jexplore39 stance/lift (unchanged stance/lift/timing and far
    transform offset). The near limb keeps the complete authored role pieces; the far limb is the complete
    recoloured role composite above. West art is NOT mirrored; facing stays screen-left. One cycle serves
    walk/run at host normal speed.
NORTH/SOUTH/EAST and idle tasks are NOT produced here.

Usage:  <venv python> -X utf8 -I <tool> build|check
Writes only NEW files under outputs/muxiu-ww84 and game/assets/characters/muxiu-native-v01/west-walk-b84
(refuses to overwrite different bytes). Optional WB_STAGE_REL (a relative outputs/ path) mirrors all writes and
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
_W_FN = "rpg-2-star-ocean-the-second_muxiu_west-static-author_unapproved-v01r2_20261024-055724-17c9961a.py"
TOOL_PINS = {_J_FN: "ae8654f28c89e4c11ef7c52b61fc87ee992af5ae805277998102e4ba9bf80cd5",   # raw bytes
             _W_FN: "cac9bc0e781804f84f529c16b0de2fe43bf664603eee9572e2110e2097d41cb6"}
for _fn, _want in TOOL_PINS.items():
    with open(os.path.join(_HERE, _fn), "rb") as _fh:
        assert hashlib.sha256(_fh.read()).hexdigest() == _want, f"reused tool drift: {_fn}"
J = _load(_J_FN, "wb_jexplore39_for_muxiu_ww")
W = _load(_W_FN, "wb_muxiu_west_static_v01r2")
assert all(W.PIN_OK.values()), f"Muxiu west static author pins drifted: {W.PIN_OK}"
mx, sha, sha_text, rb, rp, decode, blank, shift, over = J.mx, J.sha, J.sha_text, J.rb, J.rp, J.decode, J.blank, J.shift, J.over

STAMP, RUN = "20261024-083000", "b84ww001"
ACTOR = "muxiu"
ZIP_DT = (2026, 10, 24, 8, 30, 0)
DIRS = ("west",)
assert (J.W, J.H, J.PIN) == (W.W, W.H, W.PIN) and tuple(W.BODY_ROWS) == (8, J.SOLE)

ROLES = [n for n in W.LAYERS if n != "guides"]
PAL = {k: "#" + v for k, v in W.PAL.items()}
RGB = {k: W.S.rgb(k) for k in W.PAL}
INV = {v: k for k, v in RGB.items()}
assert len(INV) == len(RGB)
# far-limb darkening (only boots/legwraps/trousers colours occur in that limb)
DARK = {k: k for k in PAL}
DARK.update({"r1": "r2", "r2": "r3", "r3": "r3", "c1": "c2", "c2": "c3", "c3": "c4", "c4": "c4",
             "w1": "w2", "w2": "w3", "w3": "w3", "t1": "t2", "t2": "t3", "t3": "t4", "t4": "t4",
             "q1": "q2", "q2": "q2", "k1": "k1"})
HEAD, TORSO, ARMLIKE = ("face", "hair", "braid"), ("shirt", "belt", "pouches", "cloak", "whistle"), ("arms", "bracelet")
LEGS = ("trousers", "legwraps", "boots")
assert set(HEAD + TORSO + ARMLIKE + LEGS) == set(ROLES) and len(ROLES) == 13
BRACELET_ARM_TOP_OFFSET = 67 - 57     # neutral west: bracelet top row 67, arm/sleeve top row 57

_N = "game/assets/characters/muxiu-native-v01/west"
NEUTRAL = {"west": (f"{_N}/rpg-2-star-ocean-the-second_muxiu_west-static_unapproved-v01_20261024-055724-74e5c117.png",
                    "0eb36b3bfed70b1ffcf0a20401e7948e683e317d4ca3db6fa6a4f06e6d2d8ec0")}
NEUTRAL_NATIVE = {
    f"{_N}/rpg-2-star-ocean-the-second_muxiu_west-edit_unapproved-v01_20261024-055724-7b8925b9.pxo": "8fb88fe3ea8430cc7d4971731579106324cc5cb9aa7ab159ceb9ec4d4265f4ca",
    f"{_N}/rpg-2-star-ocean-the-second_muxiu_west-edit_unapproved-v01_20261024-055724-73a0748b.ora": "4eb224d6e2b1fedd66045d1c06ffb435d16a2f1d532d7bf83ff86635f24b35e9",
    f"{_N}/rpg-2-star-ocean-the-second_muxiu_west-manifest_unapproved-v01_20261024-055724-a2f2ac0f.json": "c92fb90c2f6a54b778856329f1c60b6db269070244e38c897bee5f7a13dc4772",
    f"{_N}/rpg-2-star-ocean-the-second_muxiu_west-palette_unapproved-v01_20261024-055724-adb333d7.json": "dd8ff4213df8f14a73842a6142ef82c3a8eb799388b360777b5a561f1ecbd6fc"}


def load_neutral(d):
    rel, want = NEUTRAL[d]
    png = rb(rp(rel))
    assert sha(png) == want, f"{d} neutral PNG hash drift"
    lay = W.draw()
    comp = W.S.compose_layers({n: lay[n] for n in W.LAYERS})
    assert np.array_equal(comp, decode(png)), f"{d} Muxiu role layers != neutral PNG"
    return {n: lay[n].copy() for n in W.LAYERS}, png


# ----------------------------------------------------------------------------- Muxiu west renderer
def render_idle(base, i):
    t, h, a = J.IDLE[i]
    out = []
    for n in ROLES:
        dy = h if n in HEAD else (t if n in TORSO else (a if n in ARMLIKE else 0))
        out.append((n, shift(base[n], 0, dy) if dy else base[n].copy()))
    return [("far-limbs", blank())] + out


def _split(a, far_m):
    """Partition one finished role layer by a forward-coordinate mask; the two parts recompose exactly."""
    op = a[..., 3] == 255
    far, near = np.zeros_like(a), np.zeros_like(a)
    mf = far_m & op
    mn = (~far_m) & op
    far[mf], near[mn] = a[mf], a[mn]
    return far, near


def side_parts(base, d):
    """Author the COMPLETE far limb instead of relabelling fragments of the single neutral leg.

    b78ww001 split one boot/wrap/trouser set by forward masks: the far boot kept only a 2-5 texel sliver while the
    far wrap/trouser kept back fragments, so the far limb had no continuous clothed mass. Here the near limb keeps
    the complete authored role pieces; the far limb is one complete occluded silhouette composed from the same
    boot+legwrap+below-hip-trouser role art and recoloured through the pinned Muxiu DARK table. It is continuous
    boot->wrap->trouser by construction, is deliberately occluded under the cloak and behind the near leg, and
    contains no synthesized pixels outside the pinned palette."""
    ys = np.indices((J.H, J.W))[0]
    near_bt = base["boots"].copy()
    near_lw = base["legwraps"].copy()
    near_tr = np.where((ys >= J.LEG_TOP)[..., None], base["trousers"], 0).astype(np.uint8)
    hips = np.where((ys < J.LEG_TOP)[..., None], base["trousers"], 0).astype(np.uint8)
    near_leg = over([near_lw, near_tr, near_bt])
    far_leg = J.recolor(near_leg, DARK)
    return {"near_bt": near_bt, "near_lw": near_lw, "near_tr": near_tr, "hips": hips, "far_leg": far_leg}


def static_feet(base, d):
    # Idle f00 draws no far limb (fully occluded); its modelled neutral footprint is the same complete silhouette.
    p = side_parts(base, d)
    return {"A": p["near_bt"], "B": p["far_leg"]}


def render_side(base, parts, d, q):
    s = J.side_sign(d)                       # west = -1 (forward is screen left)
    b = q["bob"]
    knee_a = s * (q["al"] * 0.6)
    knee_b = s * (q["bl"] * 0.6)
    near_bt = J.leg_transform(parts["near_bt"], s * q["ax"], q["al"], b, knee_a)
    near_lw = J.leg_transform(parts["near_lw"], s * q["ax"], q["al"], b, knee_a)
    near_tr = J.leg_transform(parts["near_tr"], s * q["ax"], q["al"], b, knee_a)
    far_leg = J.leg_transform(parts["far_leg"], s * q["bx"], q["bl"], b, knee_b)
    out = {"far-limbs": far_leg, "boots": near_bt, "legwraps": near_lw,
           "trousers": over([shift(parts["hips"], 0, b), near_tr]),
           "arms": J.arm_transform(base["arms"], s * q["swing"], b),
           "bracelet": J.arm_transform(base["bracelet"], s * q["swing"], b)}
    for n in ROLES:
        if n not in out:
            out[n] = shift(base[n], 0, b) if b else base[n].copy()
    return [(n, J.clip_floor(out[n])) for n in J.PXO_LAYERS[:-1]], {"A": near_bt, "B": far_leg}


# ----------------------------------------------------------------------------- rebind (in memory only)
J.STAMP, J.RUN, J.ACTOR, J.ZIP_DT = STAMP, RUN, ACTOR, ZIP_DT
mx.ZIP_DT = ZIP_DT
J.DIRS = DIRS
J.OUT_REL, J.PKG_REL = "outputs/muxiu-ww84", "game/assets/characters/muxiu-native-v01/west-walk-b84"
J.PFX = "rpg-2-star-ocean-the-second_muxiu_walk"
J.VAR = "unapproved-b84ww001-v01"
J.ROLES, J.PXO_LAYERS = ROLES, ["far-limbs"] + ROLES + ["guides"]
J.HEAD, J.TORSO = HEAD, TORSO
J.PAL, J.RGB, J.INV, J.DARK = PAL, RGB, INV, DARK
J.render_idle, J.render_side, J.side_parts = render_idle, render_side, side_parts
J.static_feet = static_feet
J.NEUTRAL, J.NEUTRAL_NATIVE, J.load_neutral = NEUTRAL, NEUTRAL_NATIVE, load_neutral
OUT_REL, PKG_REL, fname = J.OUT_REL, J.PKG_REL, J.fname


def stage_rel(rel):
    """Optional fresh staging tree; keys in the manifest/file-list stay repo-relative."""
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
    source["directions"]["west"]["ora"]["content"] = "supplementary: static neutral 13 Muxiu west role layers + hidden guides"
    source.update({
        "visual_id": ACTOR, "direction_scope": "west only (south/north/east and idle tasks not in this task)",
        "task_ids": ["content.char.muxiu.walk-west"],
        "dependency": {"content.char.muxiu.static-west": "DONE (neutral source pinned byte-exact)",
                       "content.char.muxiu.walk-south": "NOT a west dependency; canonical south remains TODO and is not "
                                                        "produced or claimed here. Only an uncommitted prior adapter "
                                                        "pattern is reused."},
        "identity": "Bible character-06: 24, animal carer; moss short cloak, rope bracelet, small whistle, braid",
        "groups": {"head": list(HEAD), "torso": list(TORSO), "arm_like": list(ARMLIKE), "legs": list(LEGS),
                   "braid": "rides the head (bob only); no secondary sway added; disclosed",
                   "bracelet": f"same arm_transform as the near arm (constant {BRACELET_ARM_TOP_OFFSET}-row offset to arm top)",
                   "far_limb": "explicit complete authored far limb in the PXO far-limbs cel: the full near-role "
                                "boot+legwrap+below-hip-trouser silhouette recoloured with the pinned Muxiu DARK table "
                                "(continuous boot->wrap->trouser; occluded under the cloak/behind the near leg; no "
                                "synthesized off-palette or arbitrary dark pixels)"},
        "walk_model": {"side": "foot A = near leg planted p0-p3 at local +16.8/+5.6/-5.6/-16.8 (forward, rounded), "
                               f"swing p4-p11 (ease, lift up to {J.SWING_LIFT}); foot B = complete authored far limb "
                               "(boot+legwrap+below-hip trouser silhouette recoloured), same cycle shifted 6 phases; "
                               "flight at p4,p5,p10,p11 (jog-like stride required to match 140 px/s)",
                       "walk_run": "one cycle used for walk/run at host normal speed 140 logical px/s; no separate run-speed cycle",
                       "frame_hold": "each phase is held 40 ms; host moves continuously; root does not move in the source frames",
                       "bob": "body down 1 texel at p1,p2,p7,p8; never up",
                       "arms": "near arm and rope bracelet share one shear about the shoulder opposite the near leg (+-6); "
                               "no second arm is drawn"},
        "source_inputs": {"muxiu_west_static_author": {"file": "tools/" + _W_FN, "sha256_raw": TOOL_PINS[_W_FN],
                                                       "sha256_text_lf_v1": sha_text(rb(os.path.join(_HERE, _W_FN)))},
                          "neutral_pngs": {"west": {"file": NEUTRAL["west"][0], "sha256": NEUTRAL["west"][1]}},
                          "neutral_editables_pinned": NEUTRAL_NATIVE,
                          "static_qa": "docs/qa/rpg-2-star-ocean-the-second_muxiu_west-static-source-verdict_unapproved-v01_20261024-060500-b60a0001.md"},
        "reused_engine": {"file": "tools/" + _J_FN, "sha256_raw": TOOL_PINS[_J_FN],
                          "sha256_text_lf_v1": sha_text(rb(os.path.join(_HERE, _J_FN))),
                          "use": "side cycle timing/stance/lift, stop_poses, contact_report, leg_transform, arm_transform, "
                                 "serializers; Muxiu side renderer replaces Jiang roles so legwraps articulate and the "
                                 "bracelet rides the near arm"},
        "reused_helpers": {"file": "tools/" + J._MX_FN, "sha256_text_lf_v1": sha_text(rb(os.path.join(_HERE, J._MX_FN)))},
        "limitations": [
            "side planted foot residual at 40 ms boundaries is integer rounding of 11.2 src/phase (see contact_check); "
            "between boundaries the host moves continuously while the frame is held, so at 60 fps a planted foot sweeps "
            "the listed excursion and snaps back (frame quantization, disclosed); NOT footlocked, NOT slip-free",
            "far limb is the complete authored boot+legwrap+trouser silhouette recoloured through the pinned Muxiu "
            "DARK table and articulated by the unchanged far transform; its upper trouser is deliberately occluded "
            "under the cloak and behind the near leg; no far arm is drawn (only the near arm and bracelet)",
            "legs are sheared static texels (no foreshortening repaint); coarse frozen static, cosmetic refinement deferred",
            "braid, pouches and cloak ride head/torso (bob only, no secondary motion)",
            "Muxiu west static and portrait are UNAPPROVED; no art, motion or fluidity acceptance",
            "supplemental stop JSON is not read by the generic loader (immediate idle); stop playback is source scope only",
            "west only: package has no south/north/east entries and is opt-in/non-default"],
        "tool": {"file": "tools/" + os.path.basename(__file__), "sha256_text_lf_v1": sha_text(rb(os.path.abspath(__file__)))}})
    files[f"{OUT_REL}/{fname('source-manifest', 'json')}"] = (json.dumps(source, indent=2, ensure_ascii=False) + "\n").encode()
    return fsets, files, source


# ----------------------------------------------------------------------------- west-only source checks
def source_checks(fsets, files, source):
    import io, zipfile
    res = []

    def ck(name, ok, detail=""):
        res.append({"check": name, "pass": bool(ok), "detail": detail})

    Wd, Hd, NPH = J.W, J.H, J.NPH
    pal = set(RGB.values())
    d = "west"
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
    ck("west all frames 80x112 binary alpha, clear border, Muxiu palette only", not bad, bad[:3])
    ck("west static + idle f00 are the exact neutral PNG bytes", e["static"]["sha256"] == NEUTRAL[d][1] == e["idle"][0]["sha256"])
    ck("west counts idle 4 walk 12 stop bridge frames 24", (len(e["idle"]), len(e["walk"]), len(stop_frames)) == (4, 12, 24))
    ck("west every bridge = [walk p, s1, s2, idle f00]", all(
        v[0] == {"ref": "walk", "index": int(k[5:]), "k": 0.0} and v[-1] == {"ref": "idle", "index": 0, "k": 1.0} and len(v) == 4
        for k, v in e["stop_bridges"].items()))
    ck("west idle frames distinct (>=3)", len({files[x["file"]] for x in e["idle"]}) >= 3)
    low = {decode(files[x["file"]])[69:104].tobytes() for x in e["walk"]}
    ck("west walk lower body differs across phases (>=8)", len(low) >= 8, len(low))
    ck("west no walk phase equals the neutral bitmap", all(x["sha256"] != NEUTRAL[d][1] for x in e["walk"]))
    hs = [int(np.nonzero(decode(files[x["file"]])[..., 3].any(1))[0].min()) for x in allf]
    ck("west top row never above neutral (body never shifted up)", min(hs) >= 8, [min(hs), max(hs)])
    with zipfile.ZipFile(io.BytesIO(files[e["ora"]["file"]])) as z:
        comp = over([decode(z.read(f"data/{n}.png")) for n in ROLES])
        ck("west ORA role layers recompose to neutral PNG", np.array_equal(comp, decode(files[e["static"]["file"]])) and
           z.read("mergedimage.png") == files[e["static"]["file"]])
    with zipfile.ZipFile(io.BytesIO(files[e["pxo"]["file"]])) as z:
        nl = len(J.PXO_LAYERS)
        okp = len(allf) == e["pxo"]["frames"]
        okp &= [l["name"] for l in json.loads(z.read("data.json"))["layers"]] == J.PXO_LAYERS
        for fi, x in enumerate(allf, start=1):
            lays = [np.frombuffer(z.read(f"image_data/frames/{fi}/layer_{li}"), np.uint8).reshape(Hd, Wd, 4) for li in range(1, nl)]
            okp &= np.array_equal(over(lays), decode(files[x["file"]]))
        ck("west PXO (Muxiu 13 roles + far-limbs + guides) cels recompose to every frame PNG", okp, e["pxo"]["frames"])
    c = source["contact_check"][d]
    ck("west side planted foot world slip at 40 ms boundaries <= 1 source texel (rounding of 11.2)",
       c["walk_max_world_slip_src_at_40ms_boundaries"] <= 1.0,
       {"max_src": c["walk_max_world_slip_src_at_40ms_boundaries"],
        "60fps_excursion_src": c["walk_planted_foot_world_excursion_src_60fps_samples"]})
    ck("west each foot grounded 4 phases per cycle", all(sum(1 for r in c["per_phase_feet"] if r[k]["grounded"]) == 4 for k in ("A", "B")),
       [sum(1 for r in c["per_phase_feet"] if r[k]["grounded"]) for k in ("A", "B")])
    ck("west stop bridges: a grounded foot never moves (host stopped)", c["stop_bridge_grounded_slip_src_max"] == 0,
       c["stop_bridge_nonzero"][:3])
    # identity anchors visible in EVERY frame (west profile: braid screen-left/front, bracelet near wrist, whistle, moss cloak + clasp)
    hair_c, rope_c, wood_c, moss_c = {RGB[k] for k in ("h1", "h2", "h3")}, {RGB["q1"], RGB["q2"]}, {RGB["x1"], RGB["x2"]}, {RGB["c1"], RGB["c2"]}
    miss = []
    for x in allf:
        a = decode(files[x["file"]]); m = a[..., 3] == 255
        reg = lambda y0, y1, x0, x1: {tuple(v) for v in a[y0:y1, x0:x1][m[y0:y1, x0:x1]][:, :3]}
        if not (hair_c & reg(33, 70, 28, 38) and rope_c & reg(65, 74, 33, 46) and wood_c & reg(37, 47, 32, 41)
                and moss_c <= reg(28, 63, 31, 56) and RGB["y1"] in reg(28, 70, 31, 52)):
            miss.append(x["file"].rsplit("/", 1)[-1])
    ck("identity: braid (front/left), rope bracelet (near wrist), whistle, moss cloak + brass clasp in every frame", not miss, miss[:3])
    fl = fsets["west"]

    def _far_limb_errors(a):
        """b84 structural far-limb predicate: one continuous clothed silhouette, not a detached boot sliver."""
        m = a[..., 3] == 255
        if not m.any():
            return ["empty far-limbs cel"]
        ys, xs = np.nonzero(m)
        errs = []
        if ys.max() - ys.min() < 18:
            errs.append(f"span {int(ys.max() - ys.min())}<18")
        if any((m[y].sum() < 2) for y in range(int(ys.min()), int(ys.max()) + 1)):
            errs.append("1-texel string row")
        seen = np.zeros_like(m)
        stack = [(int(ys[0]), int(xs[0]))]
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
        if not (keys & {"t1", "t2", "t3", "t4"}):
            errs.append("no trouser mass")
        if not (keys & {"w1", "w2", "w3", "w4", "c2", "c3", "c4", "q1", "q2"}):
            errs.append("no legwrap mass")
        if not (keys & {"r1", "r2", "r3", "r4", "k1"}):
            errs.append("no boot mass")
        return errs

    far_bad = []
    for tag_, lay in ([("walk", w) for w in fl["walk"]] + [("stop", s) for p in range(NPH) for s in fl["stop"][p]]):
        errs = _far_limb_errors(dict(lay[0])["far-limbs"])
        if errs:
            far_bad.append([tag_, errs])
    ck("structural far limb: every walk/stop cel is one continuous clothed boot+wrap+trouser silhouette "
       "(8-connected, spans hip->ankle, no 1-texel string, all three leg roles present)", not far_bad, far_bad[:3])
    det = 0
    for lay in [w[0] for w in fl["walk"]] + [s[0] for p in range(NPH) for s in fl["stop"][p]] + list(fl["idle"]):
        L = dict(lay)
        wy = np.nonzero(L["bracelet"][..., 3].any(1))[0]; ay = np.nonzero(L["arms"][..., 3].any(1))[0]
        det += int((wy.min() - ay.min()) != BRACELET_ARM_TOP_OFFSET)
    ck("identity: bracelet stays on the near arm (constant offset to arm top in every frame)", det == 0, det)
    pk = json.loads(files[source["package"]["sprite_set"]])
    paths = [f["file"] for a in pk["actions"].values() for v in a.values() for f in v]
    durs = [f["duration_ms"] for a in pk["actions"].values() for v in a.values() for f in v]
    ok = pk["schema"] == "worlds-between.exploration-sprite-set.v1" and pk["actor_id"] == ACTOR and \
        set(pk["actions"]) == {"idle", "walk"} and all(set(pk["actions"][a]) == {"west"} for a in pk["actions"])
    ok &= all(isinstance(x, int) and 40 <= x <= 2000 for x in durs)
    ok &= all(files[PKG_REL + "/" + p] == files[OUT_REL + "/" + p] for p in paths)
    ck("runtime sprite set: schema/actor/west only/explicit durations/relative byte-equal PNG copies", ok, len(paths))
    stp = json.loads(files[source["package"]["stop_supplemental"]])
    sp = [s["file"] for v in stp["phase_bridges"]["west"].values() for s in v if "file" in s]
    ck("stop supplemental: actor, west only, 24 bridge frames, runtime_default false, byte-equal copies",
       stp["actor_id"] == ACTOR and list(stp["phase_bridges"]) == ["west"] and len(sp) == 24 and stp["runtime_default"] is False
       and all(files[PKG_REL + "/" + p] == files[OUT_REL + "/" + p] for p in sp), len(sp))
    reg = json.loads(files[source["package"]["registry"]])
    ck("package-local registry lists ONLY muxiu -> this set", list(reg["actors"]) == [ACTOR] and PKG_REL + "/" + reg["actors"][ACTOR] == source["package"]["sprite_set"])
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
    c = source["contact_check"]["west"]
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
    with open(J._fs(out), "wb") as fh:
        fh.write((json.dumps(res, indent=2) + "\n").encode())
    return 0 if not fails else 1


if __name__ == "__main__":
    sys.exit(main())
