"""Lin Que (lin-que) four-direction EXPLORATION SOURCE author (lexplore59, UNAPPROVED technical source).

THIN ADAPTER over the frozen jexplore39 Jiang Lan exploration author: its renderer (idle settle, side shear
stride, front/back in-place cycle, phase-aware stop bridges), serializers, contact report and source checker
are reused unchanged. Only actor bindings are replaced in memory (no Jiang file is written):
actor/paths/run, ROLES/PXO_LAYERS (Lin 11 roles), palette/RGB/INV/DARK (Lin keys), HEAD/TORSO groups, neutral
pins and load_neutral (Lin static author draw(direction) must recompose to the existing Lin static PNG bytes).
Source-manifest metadata (task ids, inputs, tool, limitations) is rewritten for Lin; check labels relabelled.

Groups: head = face/hair/goggles; torso = cape/coat/belt/firearm/scarf (cape and scarf ride the torso, no
extra follow-through added in this batch). Body/identity/pivot frozen; existing Lin statics are UNAPPROVED.

Usage:  python -X utf8 -I <tool> build|check
Writes only NEW files under outputs/lexplore59 and game/data/lexplore59.
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
_L_FN = "rpg-2-star-ocean-the-second_lin-que_four-direction-static-author_unapproved-v01_20261022-222500-3d61c74e.py"
J = _load(_J_FN, "wb_jexplore39_for_lin")
LQ = _load(_L_FN, "wb_lin_static_v01")
mx, sha, sha_text, rb, rp, decode = J.mx, J.sha, J.sha_text, J.rb, J.rp, J.decode

STAMP, RUN = "20261022-231558", "6875dc75"
ACTOR = "lin-que"
ZIP_DT = (2026, 10, 22, 23, 15, 58)
assert (J.W, J.H, J.PIN) == (LQ.W, LQ.H, LQ.PIN) and LQ.BODY_ROWS == (8, J.SOLE)

ROLES = [n for n in LQ.LAYERS if n != "guides"]
PAL = {k: "#" + v for k, v in LQ.PAL.items()}
RGB = {k: LQ.S.rgb(k) for k in LQ.PAL}
INV = {v: k for k, v in RGB.items()}
assert len(INV) == len(RGB)
# far-limb shading: one step darker within each Lin ramp (total over every key so recolor never misses)
DARK = {"s1": "s2", "s2": "s3", "s3": "s4", "s4": "s4", "n1": "n2", "n2": "n3", "n3": "n4", "n4": "n4",
        "e1": "e1", "e2": "e2", "m1": "m1", "c1": "c2", "c2": "c3", "c3": "c4", "c4": "c4",
        "t1": "t2", "t2": "t3", "t3": "c3", "w1": "w2", "w2": "w3", "w3": "w3", "g1": "g2", "g2": "g2",
        "l1": "l2", "l2": "l2", "d1": "d2", "d2": "d3", "d3": "d3", "b1": "b2", "b2": "k1", "k1": "k1",
        "r1": "r2", "r2": "r2", "x1": "x2", "x2": "x3", "x3": "x3"}
assert set(DARK) == set(PAL) and set(DARK.values()) <= set(PAL)

_N = "game/assets/characters/lin-que-native-v01"
NEUTRAL = {
    "south": (f"{_N}/south/rpg-2-star-ocean-the-second_lin-que_south-static_unapproved-v01_20261022-222500-72fae449.png",
              "d64f4e6b94efa9c7a85e4b3b40bf78d61933173e918246fc250974269b308fa8"),
    "west": (f"{_N}/west/rpg-2-star-ocean-the-second_lin-que_west-static_unapproved-v01_20261022-222500-30482526.png",
             "14d5d1034c5e420a5654960149fda405be26171b68ff652ccaa7dc179bb47b2e"),
    "north": (f"{_N}/north/rpg-2-star-ocean-the-second_lin-que_north-static_unapproved-v01_20261022-222500-3e2fb99e.png",
              "6886b3375f19a5657aeb5adcf018e8e7b2ce7f94a29e8da86425594fb5e46c7b"),
    "east": (f"{_N}/east/rpg-2-star-ocean-the-second_lin-que_east-static_unapproved-v01_20261022-222500-069d1137.png",
             "627e6b7855ab61af02275c6e30c1bd38fb4ca318913157fe252387421dc13c16"),
}
NEUTRAL_NATIVE = {  # editable neutral sources: read-only pins (must stay byte-exact)
    f"{_N}/south/rpg-2-star-ocean-the-second_lin-que_south-edit_unapproved-v01_20261022-222500-6a109419.pxo": "8a2711de66722b5e3e8cc38f057bc7b892db30e5b0814ac81f17f4efe41e01aa",
    f"{_N}/south/rpg-2-star-ocean-the-second_lin-que_south-edit_unapproved-v01_20261022-222500-61e0d6b4.ora": "b00f4bb547fa66eba276f3021c3c52410dee6cbb412a70a896e3a62f0397f7c3",
    f"{_N}/west/rpg-2-star-ocean-the-second_lin-que_west-edit_unapproved-v01_20261022-222500-793306c9.pxo": "3b1885510e6f456c7aca3f31a451a9f980287b75186e22d8ddd50632566fab40",
    f"{_N}/west/rpg-2-star-ocean-the-second_lin-que_west-edit_unapproved-v01_20261022-222500-71637717.ora": "f2f91134d94471536e7a2f863f8d64b4d1130aaa2378ffefafe51d7dd0096971",
    f"{_N}/north/rpg-2-star-ocean-the-second_lin-que_north-edit_unapproved-v01_20261022-222500-73301932.pxo": "49269082bb6ac4bb493a03abaf935cb150f7f9c72d79c4c7c750dbdf4e504e65",
    f"{_N}/north/rpg-2-star-ocean-the-second_lin-que_north-edit_unapproved-v01_20261022-222500-15311346.ora": "4437e4e3b8825e3f8a3c0e67d0f0360692c598f7c83766f1a2538b8cb17c8b72",
    f"{_N}/east/rpg-2-star-ocean-the-second_lin-que_east-edit_unapproved-v01_20261022-222500-7f36963d.pxo": "81c2e9ad5cf28a669a2c8b3559ad987fb649660e6035fd8e1aeeff41cfb41ae1",
    f"{_N}/east/rpg-2-star-ocean-the-second_lin-que_east-edit_unapproved-v01_20261022-222500-54c441bb.ora": "2a40216c786713698c015bec44eb81d9eee5194ee774cbec16b785a2d1510e0d",
}


def load_neutral(d):
    rel, want = NEUTRAL[d]
    png = rb(rp(rel))
    assert sha(png) == want, f"{d} neutral PNG hash drift"
    lay = LQ.draw(d)
    comp = LQ.S.compose_layers({n: lay[n] for n in LQ.LAYERS})
    assert np.array_equal(comp, decode(png)), f"{d} role layers != neutral PNG"
    return {n: lay[n].copy() for n in LQ.LAYERS}, png


# ----------------------------------------------------------------------------- rebind (in memory only)
J.STAMP, J.RUN, J.ACTOR, J.ZIP_DT = STAMP, RUN, ACTOR, ZIP_DT
mx.ZIP_DT = ZIP_DT
J.OUT_REL, J.PKG_REL = "outputs/lexplore59", "game/data/lexplore59"
J.PFX = "rpg-2-star-ocean-the-second_lin-que_explore"
J.VAR = "unapproved-lexplore59-v01"
J.ROLES, J.PXO_LAYERS = ROLES, ["far-limbs"] + ROLES + ["guides"]
J.HEAD, J.TORSO = ("face", "hair", "goggles"), ("cape", "coat", "belt", "firearm", "scarf")
J.PAL, J.RGB, J.INV, J.DARK = PAL, RGB, INV, DARK
J.NEUTRAL, J.NEUTRAL_NATIVE, J.load_neutral = NEUTRAL, NEUTRAL_NATIVE, load_neutral
J.FAR_BASE = 3   # measured: Lin static far toe sits 3 texels ahead of the near toe (west and east); Jiang was 2
OUT_REL, PKG_REL, fname = J.OUT_REL, J.PKG_REL, J.fname

LABELS = (("Jiang palette", "Lin palette"), ("Jiang 9 roles", "Lin 11 roles"), ("jiang-lan", "lin-que"))


def build_all():
    fsets, files, source = J.build_all()
    old = f"{OUT_REL}/{fname('source-manifest', 'json')}"
    for k in ("source_inputs", "reused_helpers", "tool", "limitations", "task_ids", "visual_id"):
        source.pop(k)
    source.update({
        "visual_id": ACTOR,
        "task_ids": ["content.char.lin-que.idle-anim", "content.char.lin-que.walk-south", "content.char.lin-que.walk-west",
                     "content.char.lin-que.walk-north", "content.char.lin-que.walk-east"],
        "groups": {"head": list(J.HEAD), "torso": list(J.TORSO), "legs": ["trousers", "boots"], "arms": ["arms"],
                   "cape_scarf_follow_through": "none added (ride torso group); disclosed"},
        "source_inputs": {"lin_static_author": {"file": "tools/" + _L_FN, "sha256_text_lf_v1": sha_text(rb(os.path.join(_HERE, _L_FN)))},
                          "neutral_pngs": {d: {"file": NEUTRAL[d][0], "sha256": NEUTRAL[d][1]} for d in J.DIRS},
                          "neutral_editables_pinned": NEUTRAL_NATIVE},
        "reused_engine": {"file": "tools/" + _J_FN, "sha256_text_lf_v1": sha_text(rb(os.path.join(_HERE, _J_FN))),
                          "use": "renderer/stop bridges/contact report/source checks/serializers; actor bindings rebound in memory"},
        "reused_helpers": {"file": "tools/" + J._MX_FN, "sha256_text_lf_v1": sha_text(rb(os.path.join(_HERE, J._MX_FN)))},
        "limitations": [
            "side gait is the jexplore39 jog-like stride (2 flight phases per step) needed to world-lock feet at 140 logical px/s",
            "side planted-foot residual at 40 ms boundaries is integer rounding of 11.2/phase; 60 fps frame-hold excursion listed in contact_check (disclosed, not a pass)",
            "front/back cycles are in place: a planted foot travels with the host by 11.2 source texels (5.6 logical) per 40 ms; NOT slip-free",
            "side legs are sheared near-leg texels; the far leg/arm are darkened near-limb copies (static far-leg texels are not kept in walk frames)",
            "cape and scarf ride the torso group (bob/settle only); no secondary follow-through in this batch",
            "Lin statics are UNAPPROVED; no art, motion or fluidity acceptance; no Pixelorama round-trip, no Godot import/capture",
            "supplemental stop JSON is not read by the generic loader (immediate idle); stop playback not demonstrated at runtime"],
        "tool": {"file": "tools/" + os.path.basename(__file__), "sha256_text_lf_v1": sha_text(rb(os.path.abspath(__file__)))}})
    files[old] = (json.dumps(source, indent=2, ensure_ascii=False) + "\n").encode()
    return fsets, files, source


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
    sc = J.source_checks(fsets, files, source)
    for c in sc:
        for a, b in LABELS:
            c["check"] = c["check"].replace(a, b)
        if not c["pass"]:
            fails.append("source " + c["check"])
    print(f"SOURCE {sum(c['pass'] for c in sc)}/{len(sc)}")
    pins_ok = all(pins_before.values()) and all(J.pins_state().values())
    if not pins_ok:
        fails.append("neutral source pins drifted")
    summary = {d: {k: source["contact_check"][d][k] for k in (
        "walk_max_world_slip_src_at_40ms_boundaries", "walk_planted_foot_world_excursion_src_60fps_samples",
        "flight_phases", "stop_bridge_grounded_slip_src_max")} for d in J.DIRS}
    print(json.dumps(summary))
    res = {"tool_sha256_text_lf_v1": source["tool"]["sha256_text_lf_v1"], "rebuild": {"checked": len(files), "ok": n_ok},
           "deterministic": det, "neutral_pins_exact_before_after": pins_ok, "source_checks": sc, "contacts": summary,
           "not_run": ["Pixelorama native export", "Godot import/runtime", "normal-speed movie"], "fails": fails}
    print("RESULT", "PASS" if not fails else "FAIL", json.dumps(fails[:12]))
    out = rp(f"{OUT_REL}/{fname('check-result', 'json')}")
    os.makedirs(J._fs(os.path.dirname(out)), exist_ok=True)
    with open(J._fs(out), "wb") as fh:
        fh.write((json.dumps(res, indent=2) + "\n").encode())
    return 0 if not fails else 1


if __name__ == "__main__":
    sys.exit(main())
