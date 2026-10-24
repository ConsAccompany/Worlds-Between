"""Milo EAST walk/run loop + phase-aware stop source author (mew01, UNAPPROVED technical source).

content.char.milo.walk-east. EAST ONLY. Same thin bounded adapter as the committed Milo south msw01 / north mnw01
authors, over the frozen jexplore39 Jiang Lan exploration engine: its SIDE 12-phase cycle (40 ms, world-locked
stance 16.8/5.6/-5.6/-16.8 at host 140 logical px/s = 11.2 source texels per phase), leg_transform/arm_transform,
stop_poses, contact_report (40 ms boundaries + 60 fps samples) and serializers (make_pxo/make_ora via mexplore23).
The committed msw01 south author is loaded only for its Milo render_idle and roles/palette bindings; the engine is
then rebound in memory for east (no south/north/Jiang/Lin file is written):
  - neutral layers come from the committed Milo east static author draw() and must recompose to the existing
    Milo east static PNG bytes (hash-pinned); the east editable PXO/ORA/manifest/palette are read-only pins.
  - Milo-east side split (replaces jexplore39 side_parts/static_feet/render_side, which assume Jiang's far toe
    PEEKING AHEAD of the near toe): Milo's far leg is SET BACK 4 texels (static far boot f-8..-2, near f-4..8).
    near leg = trousers f>=-3 / boots f>=-4 (rows >= LEG_TOP); far leg = the visible static far strip over a
    darkened near-leg copy shifted -4 (hidden fill, so the far leg has a full silhouette when it swings), with
    every texel visible at neutral forced to the neutral pixel so the neutral pose recomposes byte-exact.
  - arms: near arm (f<=2) shears with the near-arm swing; the far forearm (f>=6) and the green far-wrist
    wristband share the opposite shear (identical row transform), so the wristband never detaches.
    The far forearm stays in the 'arms' role layer in front of the coat (as in the static); disclosed.
  - square medicine case (near hip, screen left of the pivot) rides the torso (bob only); no secondary swing.
One cycle serves walk/run at the host normal speed (no separate faster run cycle exists in this batch).
South/north/west are NOT produced here (Milo west is paused).

Usage:  python -X utf8 -I <tool> build|check
Writes only NEW files under outputs/milo-ew01 (package staged at outputs/milo-ew01/pkg; refuses to overwrite).
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
_ME_FN = "rpg-2-star-ocean-the-second_milo_east-static-author_unapproved-v01_20261024-000137-e4a1c7d2.py"
SW = _load(_SW_FN, "wb_milo_walk_south_msw01_for_east")
ME = _load(_ME_FN, "wb_milo_east_static_v01")
J = SW.J
mx, sha, sha_text, rb, rp, decode, blank, shift, over = J.mx, J.sha, J.sha_text, J.rb, J.rp, J.decode, J.blank, J.shift, J.over
_J_FN = SW._J_FN

STAMP, RUN = "20261024-061500", "3e1a5c07"
ACTOR = "milo"
ZIP_DT = (2026, 10, 24, 6, 15, 0)
DIRS = ("east",)
assert (J.W, J.H, J.PIN) == (ME.W, ME.H, ME.PIN) and tuple(ME.BODY_ROWS) == (8, J.SOLE)
assert all(ME.PIN_OK.values()) and all(ME.MS.PIN_OK.values()), "east static author tool pins drifted"
assert [n for n in ME.LAYERS if n != "guides"] == SW.ROLES and ME.PAL == SW.MS.PAL

ROLES, PAL, RGB, INV = SW.ROLES, SW.PAL, SW.RGB, SW.INV
HEAD, TORSO, ARMLIKE = SW.HEAD, SW.TORSO, SW.ARMLIKE
render_idle = SW.render_idle
# far-limb shade: one ramp step darker within the same Milo palette family (k1 stays; ramp ends stay)
DARK = {k: (k[0] + str(int(k[1]) + 1)) if (k[0] + str(int(k[1]) + 1)) in PAL else k for k in PAL}
FAR_SET_BACK = -4          # Milo east far leg sits 4 texels behind the near leg (static far boot heel f-8, near f-4)
NEAR_TR_MIN, NEAR_BT_MIN = -3, -4
NEAR_ARM_MAX, FAR_ARM_MIN = 2, 6

_E = "game/assets/characters/milo-native-v01/east"
NEUTRAL = {"east": (f"{_E}/rpg-2-star-ocean-the-second_milo_east-static_unapproved-v01_20261024-000137-820dcbf2.png",
                    "af45b51d44c0b409267c2995ec196593cbf0fca6cbb178c01b65e6f0d749e070")}
NEUTRAL_NATIVE = {  # existing Milo east static package: read-only pins (must stay byte-exact)
    f"{_E}/rpg-2-star-ocean-the-second_milo_east-edit_unapproved-v01_20261024-000137-8799fd7f.pxo": "a854453e33abcfe03437a7c0cc90f50a72660772a983f78792cf802aa620b17a",
    f"{_E}/rpg-2-star-ocean-the-second_milo_east-edit_unapproved-v01_20261024-000137-a77ff61f.ora": "56171d13a062b1eff9a48201b3338c06d861365cbbf318af5af865258d484b78",
    f"{_E}/rpg-2-star-ocean-the-second_milo_east-manifest_unapproved-v01_20261024-000137-1a15f1d2.json": "dc77dec5f89b68754782bef12c158fbccda29ba314bf998cbab1da3ab936db44",
    f"{_E}/rpg-2-star-ocean-the-second_milo_east-palette_unapproved-v01_20261024-000137-29b43d49.json": "c322e69c1ca22a79347e1981d82bc5d4cab6b8e4dc901a3a88add70ff3b01333"}


def load_neutral(d):
    rel, want = NEUTRAL[d]
    png = rb(rp(rel))
    assert sha(png) == want, f"{d} neutral PNG hash drift"
    lay = ME.draw()
    comp = ME.S.compose_layers({n: lay[n] for n in ME.LAYERS})
    assert np.array_equal(comp, decode(png)), f"{d} Milo role layers != neutral PNG"
    return {n: lay[n].copy() for n in ME.LAYERS}, png


# ----------------------------------------------------------------------------- Milo east side split
def _fcol(lo=None, hi=None):
    f = np.arange(J.W) - 40
    keep = np.ones(J.W, bool)
    if lo is not None:
        keep &= f >= lo
    if hi is not None:
        keep &= f <= hi
    return keep


def _mask_cols(a, keep):
    o = a.copy(); o[:, ~keep] = 0
    return o


def side_parts(base, d):
    assert d == "east"
    legs = J.rows(base["trousers"], J.LEG_TOP)
    near_tr = _mask_cols(legs, _fcol(NEAR_TR_MIN))
    near_bt = _mask_cols(base["boots"], _fcol(NEAR_BT_MIN))
    far_tr = _mask_cols(legs, _fcol(hi=NEAR_TR_MIN - 1))
    near_bt[far_tr[..., 3] == 255] = 0     # near boot-top texels hidden under the far trouser leg in the static
    far_strip = over([_mask_cols(base["boots"], _fcol(hi=NEAR_BT_MIN - 1)), far_tr])
    fill = shift(J.recolor(over([near_bt, near_tr]), DARK), FAR_SET_BACK, 0)
    far_leg = over([fill, far_strip])
    hips = J.rows(base["trousers"], 0, J.LEG_TOP)
    parts = {"near_tr": near_tr, "near_bt": near_bt, "hips": hips, "far_leg": far_leg,
             "near_arm": _mask_cols(base["arms"], _fcol(hi=NEAR_ARM_MAX)), "far_arm": _mask_cols(base["arms"], _fcol(FAR_ARM_MIN))}
    assert np.array_equal(over([parts["near_arm"], parts["far_arm"]]), base["arms"]), "arm split lost texels"
    # neutral exactness: every far-leg texel left visible at the neutral pose takes the neutral pixel (or is cleared)
    lay, _ = render_side(base, parts, d, dict(J.NEUTRAL_POSE))
    upper = over([a for n, a in lay if n != "far-limbs"])[..., 3] == 255
    neutral = ME.S.compose_layers({n: base[n] for n in ME.LAYERS})
    vis = (far_leg[..., 3] == 255) & ~upper
    far_leg[vis] = neutral[vis]
    parts["far_leg"] = far_leg
    lay, _ = render_side(base, parts, d, dict(J.NEUTRAL_POSE))
    assert np.array_equal(over([a for _, a in lay]), neutral), "east neutral pose != neutral PNG"
    return parts


def render_side(base, parts, d, q):
    s = J.side_sign(d)
    b = q["bob"]
    knee_a = s * (q["al"] * 0.6)
    knee_b = s * (q["bl"] * 0.6)
    near_tr = J.leg_transform(parts["near_tr"], s * q["ax"], q["al"], b, knee_a)
    near_bt = J.leg_transform(parts["near_bt"], s * q["ax"], q["al"], b, knee_a)
    far_leg = J.leg_transform(parts["far_leg"], s * q["bx"], q["bl"], b, knee_b)
    out = {"far-limbs": far_leg, "boots": near_bt,
           "trousers": over([shift(parts["hips"], 0, b), near_tr]),
           "arms": over([J.arm_transform(parts["far_arm"], -s * q["swing"], b), J.arm_transform(parts["near_arm"], s * q["swing"], b)]),
           "wristband": J.arm_transform(base["wristband"], -s * q["swing"], b)}
    for n in ROLES:
        if n not in out:
            out[n] = shift(base[n], 0, b) if b else base[n].copy()
    return [(n, J.clip_floor(out[n])) for n in J.PXO_LAYERS[:-1]], {"A": near_bt, "B": far_leg}


def static_feet(base, d):
    """Neutral feet = the side split at the neutral pose (near boot / full far leg incl. hidden fill)."""
    p = side_parts(base, d)
    return {"A": p["near_bt"], "B": p["far_leg"]}


# ----------------------------------------------------------------------------- rebind (in memory only)
J.STAMP, J.RUN, J.ACTOR, J.ZIP_DT = STAMP, RUN, ACTOR, ZIP_DT
mx.ZIP_DT = ZIP_DT
J.DIRS = DIRS
J.OUT_REL, J.PKG_REL = "outputs/milo-ew01", "outputs/milo-ew01/pkg"
J.PFX = "rpg-2-star-ocean-the-second_milo_walk"
J.VAR = "unapproved-mew01-v01"
J.ROLES, J.PXO_LAYERS = ROLES, ["far-limbs"] + ROLES + ["guides"]
J.HEAD, J.TORSO = HEAD, TORSO
J.PAL, J.RGB, J.INV, J.DARK = PAL, RGB, INV, DARK
J.FAR_BASE = 0
J.render_idle = render_idle
J.side_parts, J.render_side, J.static_feet = side_parts, render_side, static_feet
J.NEUTRAL, J.NEUTRAL_NATIVE, J.load_neutral = NEUTRAL, NEUTRAL_NATIVE, load_neutral
OUT_REL, PKG_REL, fname = J.OUT_REL, J.PKG_REL, J.fname


def boundary_samples(c):
    """World-space planted-foot position at explicit hold/tick boundaries (t = k*40 ms and k*40+39 ms, plus 60 fps
    tick times), foot A/B, host continuous at 140 logical px/s. Returns per-foot max excursion within each stance."""
    V, HOST = J.V, J.HOST_LOGICAL_PX_S
    out = {}
    for k in ("A", "B"):
        rec = [r[k] for r in c["per_phase_feet"]]
        runs, cur = [], []
        for ms in range(0, 2 * J.NPH * J.FRAME_MS):
            r = rec[(ms // J.FRAME_MS) % J.NPH]
            if r["grounded"]:
                cur.append((ms, (r["toe_x"] - 40) + 2 * HOST * ms / 1000.0, (r["heel_x"] - 40) + 2 * HOST * ms / 1000.0))
            elif cur:
                runs.append(cur); cur = []
        if cur:
            runs.append(cur)
        exc = [round(max(max(v[1] for v in r) - min(v[1] for v in r), max(v[2] for v in r) - min(v[2] for v in r)), 3) for r in runs]
        tick = [(ms, round(w, 3)) for r in runs[:1] for ms, w, _ in r if ms % J.FRAME_MS in (0, J.FRAME_MS - 1)]
        out[k] = {"stances_sampled_1ms": len(runs), "max_world_excursion_src_within_stance_1ms": max(exc) if exc else None,
                  "first_stance_toe_world_src_at_hold_start_end": tick}
    del V
    return out


def build_all():
    fsets, files, source = J.build_all()
    old = f"{OUT_REL}/{fname('source-manifest', 'json')}"
    for k in ("source_inputs", "reused_helpers", "tool", "limitations", "task_ids", "visual_id", "walk_model"):
        source.pop(k)
    c = source["contact_check"]["east"]
    c["hold_tick_boundary_samples"] = boundary_samples(c)
    source.update({
        "visual_id": ACTOR, "direction_scope": "east only (west paused; south/north committed separately)",
        "task_ids": ["content.char.milo.walk-east"],
        "dependency": {"content.char.milo.static-east": "DONE (neutral source pinned byte-exact)"},
        "groups": {"head": list(HEAD), "torso": list(TORSO), "arm_like": list(ARMLIKE), "legs": ["trousers", "boots", "far-limbs"],
                   "case": "square medicine case (near hip, screen left of pivot) rides torso (bob only); no secondary swing added; disclosed"},
        "walk_model": {"side": "foot A = near leg planted p0-p3 at local +16.8/+5.6/-5.6/-16.8 (forward, rounded), swing p4-p11 "
                               f"(ease, lift up to {J.SWING_LIFT}); foot B = far leg set back {FAR_SET_BACK} texels, same cycle shifted 6 phases; "
                               "flight at p4,p5,p10,p11 (jog-like stride required to match 140 px/s)",
                       "arms": "near arm sheared about the shoulder opposite the near leg (+-6); far forearm + wristband the opposite shear",
                       "bob": "body down 1 texel at p1,p2,p7,p8; never up",
                       "walk_run": "one cycle used for walk/run at host normal speed 140 logical px/s; no separate run-speed cycle"},
        "source_inputs": {"milo_east_static_author": {"file": "tools/" + _ME_FN, "sha256_text_lf_v1": sha_text(rb(os.path.join(_HERE, _ME_FN)))},
                          "milo_walk_south_author": {"file": "tools/" + _SW_FN, "sha256_text_lf_v1": sha_text(rb(os.path.join(_HERE, _SW_FN))),
                                                     "use": "Milo render_idle, roles/palette bindings (south pins checked on import, not written)"},
                          "neutral_pngs": {"east": {"file": NEUTRAL["east"][0], "sha256": NEUTRAL["east"][1]}},
                          "neutral_editables_pinned": NEUTRAL_NATIVE},
        "reused_engine": {"file": "tools/" + _J_FN, "sha256_text_lf_v1": sha_text(rb(os.path.join(_HERE, _J_FN))),
                          "use": "side cycle timing/stance, leg_transform, arm_transform, stop_poses, contact_report, serializers; "
                                 "side_parts/static_feet/render_side replaced by Milo-east split (far leg set back, wristband on far arm)"},
        "reused_helpers": {"file": "tools/" + J._MX_FN, "sha256_text_lf_v1": sha_text(rb(os.path.join(_HERE, J._MX_FN)))},
        "limitations": [
            "side gait is the frozen jexplore39 jog-like stride with 2 flight phases per step (p4,p5,p10,p11); not a double-support walk",
            "planted-foot world residual at 40 ms boundaries is integer rounding of 11.2 src/phase (see contact_check); between boundaries "
            "the frame is held while the host moves continuously, so a planted foot sweeps up to ~11 src (~5.6 logical) and snaps back "
            "at each 40 ms tick (frame quantization; disclosed, NOT slip-free, NOT footlocked)",
            "far leg is the visible static far strip over a darkened near-leg copy (hidden fill); legs are sheared static texels, no repaint",
            "far forearm + wristband stay in front of the coat in every phase (static layering); physically it should pass behind the torso when swung back",
            "contact metrics are not fluidity, footlock or human motion acceptance",
            "Milo east static is UNAPPROVED; no art, motion or fluidity acceptance",
            "supplemental stop JSON is not read by the generic loader (immediate idle); stop playback is source scope only",
            "east only: package has no south/west/north entries, is opt-in/non-default and staged under outputs/ (not game/data)"],
        "tool": {"file": "tools/" + os.path.basename(__file__), "sha256_text_lf_v1": sha_text(rb(os.path.abspath(__file__)))}})
    files[old] = (json.dumps(source, indent=2, ensure_ascii=False) + "\n").encode()
    return fsets, files, source


# ----------------------------------------------------------------------------- east-only source checks
def source_checks(fsets, files, source):
    import io, zipfile
    res = []

    def ck(name, ok, detail=""):
        res.append({"check": name, "pass": bool(ok), "detail": detail})

    W, H, NPH = J.W, J.H, J.NPH
    pal = set(RGB.values())
    d = "east"
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
    ck("east all frames 80x112 binary alpha, clear border, Milo palette only", not bad, bad[:3])
    ck("east static + idle f00 are the exact neutral PNG bytes", e["static"]["sha256"] == NEUTRAL[d][1] == e["idle"][0]["sha256"])
    ck("east counts idle 4 walk 12 stop bridge frames 24", (len(e["idle"]), len(e["walk"]), len(stop_frames)) == (4, 12, 24))
    ck("east every bridge = [walk p, s1, s2, idle f00]", all(
        v[0] == {"ref": "walk", "index": int(k[5:]), "k": 0.0} and v[-1] == {"ref": "idle", "index": 0, "k": 1.0} and len(v) == 4
        for k, v in e["stop_bridges"].items()))
    ck("east idle frames distinct (>=3)", len({files[x["file"]] for x in e["idle"]}) >= 3)
    low = {decode(files[x["file"]])[69:104].tobytes() for x in e["walk"]}
    ck("east walk lower body differs across phases (>=8)", len(low) >= 8, len(low))
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
            lays = [np.frombuffer(z.read(f"image_data/frames/{fi}/layer_{li}"), np.uint8).reshape(H, W, 4) for li in range(1, nl)]
            okp &= np.array_equal(over(lays), decode(files[x["file"]]))
        ck("east PXO (Milo 11 roles + far-limbs + guides) cels recompose to every frame PNG", okp, e["pxo"]["frames"])
    c = source["contact_check"][d]
    ck("east side planted foot world slip at 40 ms boundaries <= 1 source texel (rounding of 11.2)",
       c["walk_max_world_slip_src_at_40ms_boundaries"] <= 1.0,
       {"max_src": c["walk_max_world_slip_src_at_40ms_boundaries"], "60fps_excursion_src": c["walk_planted_foot_world_excursion_src_60fps_samples"]})
    ck("east each foot grounded 4 phases per cycle", all(sum(1 for r in c["per_phase_feet"] if r[k]["grounded"]) == 4 for k in ("A", "B")),
       [sum(1 for r in c["per_phase_feet"] if r[k]["grounded"]) for k in ("A", "B")])
    ck("east stop bridges: a grounded foot never moves (host stopped)", c["stop_bridge_grounded_slip_src_max"] == 0, c["stop_bridge_nonzero"][:3])
    # identity (profile facing screen right): case white + green cross LEFT of pivot; wristband green RIGHT of pivot;
    # silver temple patch and the green profile eye visible
    fl = fsets["east"]
    lays = [list(fl["idle"][0])] + list(fl["idle"]) + [w[0] for w in fl["walk"]] + [s[0] for p in range(NPH) for s in fl["stop"][p]]
    miss = []
    for x in allf:
        a = decode(files[x["file"]]); m = a[..., 3] == 255
        case = {tuple(v) for v in a[60:80, 22:41][m[60:80, 22:41]][:, :3]}
        wb = {tuple(v) for v in a[56:69, 41:62][m[56:69, 41:62]][:, :3]}
        allc = {tuple(v) for v in a[m][:, :3]}
        if not ({RGB["g2"], RGB["w1"]} <= case and {RGB["g1"], RGB["g2"]} & wb and RGB["a2"] in allc and RGB["e2"] in allc):
            miss.append(x["file"].rsplit("/", 1)[-1])
    ck("identity: case (white + green cross, left of pivot), wristband (right of pivot), silver patch, eye in every frame", not miss, miss[:3])
    det = []
    for i, lay in enumerate(lays):
        L = dict(lay)
        wy = np.nonzero(L["wristband"][..., 3].any(1))[0]; wx = np.nonzero(L["wristband"][..., 3].any(0))[0]
        above = L["arms"][wy.min() - 1, wx.min():wx.max() + 1, 3].any(); below = L["arms"][wy.max() + 1, wx.min():wx.max() + 1, 3].any()
        if not (above and below and len(wy) == 3):
            det.append(i)
    ck("identity: wristband attached to the far forearm (arm texels directly above and below the band in every frame)", not det, det[:5])
    base_case = fl["base"]["case"]
    rig = sum(1 for lay in lays if not any(np.array_equal(dict(lay)["case"], shift(base_case, 0, dy) if dy else base_case) for dy in (0, 1)))
    ck("case layer is the neutral case shifted by 0/+1 texel only (rides torso bob, never detaches)", rig == 0, rig)
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
    ck("package-local registry lists ONLY milo -> this set", list(reg["actors"]) == [ACTOR] and PKG_REL + "/" + reg["actors"][ACTOR] == source["package"]["sprite_set"])
    ck("all written paths are under the assigned root outputs/milo-ew01", all(r.startswith(OUT_REL + "/") for r in files))
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
    c = source["contact_check"]["east"]
    summary = {k: c[k] for k in ("walk_max_world_slip_src_at_40ms_boundaries", "walk_max_world_slip_logical_at_40ms_boundaries",
                                 "walk_planted_foot_world_excursion_src_60fps_samples", "walk_planted_foot_world_excursion_logical_60fps_samples",
                                 "flight_phases", "stop_bridge_grounded_slip_src_max")}
    summary["hold_tick_1ms_max_excursion_src"] = {k: v["max_world_excursion_src_within_stance_1ms"] for k, v in c["hold_tick_boundary_samples"].items()}
    print(json.dumps(summary))
    res = {"tool_sha256_text_lf_v1": source["tool"]["sha256_text_lf_v1"], "rebuild": {"checked": len(files), "ok": n_ok},
           "deterministic": det, "neutral_pins_exact_before_after": pins_ok, "source_checks": sc, "contacts": summary,
           "residual_disclosed": "side planted foot: <=1 src at 40 ms boundaries (rounding); within a held 40 ms frame the host "
                                 "moves continuously so the planted foot sweeps the listed excursion and snaps back; not footlocked",
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
