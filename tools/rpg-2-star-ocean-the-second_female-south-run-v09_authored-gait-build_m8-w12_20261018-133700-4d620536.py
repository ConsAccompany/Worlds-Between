"""Female protagonist SOUTH RUN v09: ONE authored pose / gait revision over the v07 control candidate (m8-w12).

UNAPPROVED / NONRUNTIME, test-only, single direction.  Not art acceptance, not runtime integration, not a production
sprite.  The creator approved only the selout v8 SOUTH IDLE static frame and the 48 logical px display scale.

What v09 changes (authored art + an authored state -> pose mapping; not a parameter search; v06 / v07 untouched):
  * CONTROL = v07, unchanged.  The gait driver state (boot offsets, lifts, VIEWS, knee lean, bob, torso shift, arms,
    hair / cape lag), stride 84 px, stance 21 px, land +2, lift-off -19, the stop event clock, the re-press rule and the
    v07 rise lock are v07's, state for state.  Two drafts that changed the swing table were rejected by the state-level
    sim before any capture: moving the boot path back for a deeper heel kick made 60 fps stops 200 -> 216.7 ms; keeping
    the path but changing the view column made a 48 fps stop hold a boot raised 104 ms (the stop allows one boot view
    change per tick).  So v09 changes only what is DRAWN for a state.
  * POSE MAPPING (draw rule): a swing boot in the "toe" view at lift >= 2 is drawn as a heel KICK (authored sole-first
    boot under the knee); "hang", and "reach" at lift >= 2, are drawn as the TUCKED leg; "reach" at lift 1 is the open
    leg reaching for the floor (v06 rule).  Along the steady cycle that turns v07's toe -> hang -> straight REACH from
    64 % of the swing (a stiff leg hovering in front for a third of the swing) into toe-off -> heel kick -> knee-forward
    tuck through passing -> the leg opens only for the last ~19 % (lift 1) -> strike.
  * TUCKED LEG.  v06 foreshortened a raised leg by dropping thigh, knee and shin rows in proportion (the leg telescopes
    like a cut-out).  v09 keeps the thigh and the knee band at their v8 length and lets only the SHIN foreshorten: the
    knee is drawn IN FRONT of the boot, the knee band is an authored forward-tilted knee (vl: guard plate tipped to the
    camera; vr: lit knee cap + crease), the remaining shin rows drop one ramp step into shadow, and the thigh leans so
    the knee sits over the raised boot's cuff.
  * KICK BOOT (part boot-<side>-kick): the heel / sole seen under the knee while the heel is up behind, authored in v8
    leather colours (after the v01 builder's sole view, redrawn smaller and lit so it does not read as an ink lump).
  * SEAM CLOSE: single see-through texels enclosed on four sides between composited parts (v06 left 21 of them in its
    12 keyframes at arm / coat / cape / leg joins) are closed with outline ink below the neck.
  * COAT HEM DRAG: the coat panels below row 66 follow the torso shift one cape-lag late (csx), so the coat tails trail
    the hip transfer instead of moving as one rigid block (csx == sx on the neutral state: the stop still ends on v8).
  Straight legs (contact views, toe at lift <= 1, reach at lift 1), arms, hair, cape, torso, head, every v06 boot view,
  the shadows and the neutral composition are v06's (the v06 builder is imported read-only and hash-pinned).

Writes (only with --out-dir): the 6 new part PNGs, 12 keyframe + 12 shadow PNGs, the keyframes .pxo (Pixelorama
1.2.3, 13 layers + shadow), the new-parts .ora, and the pose / gait amendment manifest.  --preview <dir> writes scratch
review PNGs only (never into the repository).

Usage (repository root):
  python -I -B tools/<this file> --out-dir game/assets/characters/run-v09-unapproved
  python -I -B tools/<this file> --preview <abs scratch dir>
"""
import argparse, hashlib, importlib.util, io, json, os, sys, zipfile

import numpy as np
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(HERE)
V06_BUILDER = "rpg-2-star-ocean-the-second_protagonist-female_south-run-v06-build_m8-w09_20261017-211600-f8e736cc.py"
V06_BUILDER_SHA256_TEXT_LF = "2b83a221"      # prefix pinned in the v07 QA note; the full digest is checked below
V06_MANIFEST_REL = ("game/assets/characters/run-v06-unapproved/rpg-2-star-ocean-the-second_protagonist-female_south-"
                    "run-v06-manifest_unapproved-nonruntime_20261017-211600-c619ea83.json")
V06_MANIFEST_SHA256_TEXT_LF = "f59b04fa672250c7525dda79d7cc3771830fa80a03fec339ff21fa19298e6b17"
OUT_REL = "game/assets/characters/run-v09-unapproved"
SLUG = "rpg-2-star-ocean-the-second"
PART = "female-south-run-v09"
VARIANT = "unapproved"
STAMP = "20261018-133700"
RUN_ID = "4d620536"
REPO_PATH_LIMIT = 250


def _fs(path):
    path = os.path.abspath(path)
    if os.name == "nt" and len(path) > 247 and not path.startswith("\\\\?\\"):
        return "\\\\?\\" + path
    return path


def sha_text_lf(path):
    with open(_fs(path), "rb") as f:
        return hashlib.sha256(f.read().replace(b"\r\n", b"\n")).hexdigest()


def load_v06():
    path = os.path.join(HERE, V06_BUILDER)
    digest = sha_text_lf(path)
    if not digest.startswith(V06_BUILDER_SHA256_TEXT_LF):
        raise SystemExit(f"v06 builder is not the pinned file ({digest[:16]})")
    if sha_text_lf(os.path.join(REPO, V06_MANIFEST_REL)) != V06_MANIFEST_SHA256_TEXT_LF:
        raise SystemExit("v06 manifest is not the pinned file")
    spec = importlib.util.spec_from_file_location("v06_builder", path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod, digest


b6, V06_BUILDER_DIGEST = load_v06()
W, H = b6.W, b6.H
rdiv, shift, pick = b6.rdiv, b6.shift, b6.pick
V06_COMPOSE_LEG = b6.compose_leg
GROUND, KNEE_BAND, HIP_ROW, BOOT_TOP, INWARD = b6.GROUND, b6.KNEE_BAND, b6.HIP_ROW, b6.BOOT_TOP, b6.INWARD


def fid(role):
    return hashlib.sha256(f"{RUN_ID}:{role}".encode()).hexdigest()[:8]


# ===================================================================================================== authored pose rule
V07_SWING_KEYS = [list(k) for k in b6.GAIT["swing_keys"]]


def draw_kind(foot):
    """v09 state -> pose: 'kick' (heel up behind), 'tuck' (knee forward, shin tucked) or None (v06 leg)."""
    if foot["view"] == "toe" and foot["lift"] >= 2:
        return "kick"
    if foot["view"] == "hang" or (foot["view"] == "reach" and foot["lift"] >= 2):
        return "tuck"
    return None


KICK_DROP = 2           # the kick boot's lowest row sits 2 rows below the v8 ground row at o = lift = 0 (under the knee)
SHIN_SHADE = {"5": "6"}  # a foreshortened shin turns away from the light (its lit texels drop one ramp step)
COAT_HEM_ROW = 66       # coat-skirt rows >= this trail the torso shift (drawn at csx instead of sx)
SEAM_ROW0 = 41          # enclosed see-through texels from this row down are closed with ink (v06 had 21 in its 12 keys)

# authored kicked-up boot seen from under the knee: shaft back, lit heel counter, sole edge, tread (x offsets from the
# cuff-centred left edge, top row first).  Light leather faces up (the heel catches the light), not an ink lump.
KICK_BOOT = {
    "vl": [(1, "KbLLbK"), (0, "KnlllLqK"), (0, "KlrllLbK"), (0, "KqbbbbqK"), (1, "KqqqqK"), (2, "KKKK")],
    "vr": [(1, "KbLLbK"), (0, "KqLlllnK"), (0, "KbLllrlK"), (0, "KqbbbbqK"), (1, "KqqqqK"), (2, "KKKK")],
}

# authored forward-tilted knee bands, replacing the v8 knee band rows of a tucked leg: {row: (x0, texels)}
KNEE_FWD = {
    # vl: strap + buckle as v8; the guard plate (v8 size) tips toward the camera - it starts one row higher, shows a
    # lit top face (z) and closes with an outline row, so the knee reads as coming forward
    "vl": {71: (26, "K655cB63K"),
           72: (27, "KLLcKLLk"),
           73: (27, "OOOOO63K"),
           74: (26, "OGzzzGO3K"),
           75: (26, "OGzvvgO3K"),
           76: (26, "OGgvvGOqK"),
           77: (26, "OGggBBOkK"),
           78: (27, "OGGGO63K"),
           79: (27, "KOOOK63K")},
    # vr: the knee cap catches the light (5 cluster) and a dark crease closes the band under it
    "vr": {76: (39, "K6655666K"),
           77: (39, "K655556663K"),
           78: (40, "K5555666K"),
           79: (40, "K6556663K"),
           80: (41, "K333333K")},
}


def top_centre(part):
    y = min(y for (_, y) in part)
    xs = [x for (x, yy) in part if yy == y]
    return (min(xs) + max(xs)) / 2


def kick_part(side, parts):
    """KICK_BOOT rows, top row centred midway between the cuffs of the v06 toe and hang boots it is drawn between (the
    swing goes toe -> kick -> hang; a draft centred on v8's cuff column made the foot jump 3-4 texels sideways on each
    switch), lowest row on GROUND + KICK_DROP."""
    rows = KICK_BOOT[side]
    o, top = rows[0]
    cx = (top_centre(parts[f"boot-{side}-toe"]) + top_centre(parts[f"boot-{side}-hang"])) / 2
    x0 = b6.rnd(cx - (o + (len(top) - 1) / 2))
    y0 = GROUND[side] + KICK_DROP - len(rows) + 1
    return {(x0 + o + i, y0 + j): ch for j, (o, r) in enumerate(rows) for i, ch in enumerate(r) if ch not in ". "}


def knee_part(side):
    out = {}
    for y, (x0, s) in KNEE_FWD[side].items():
        for i, ch in enumerate(s):
            if ch not in ". ":
                out[(x0 + i, y)] = ch
    return out


def extent(row_texels):
    xs = [x for x in row_texels]
    return min(xs), max(xs)


def compose_leg9(parts, side, bob, foot):
    """v09 leg.  Tucked views: thigh + knee band 1:1 (authored forward knee), shin foreshortened (only what is left above
    the boot, in shadow), knee in front of the boot, thigh leaning so the knee sits over the cuff.  Other views: v06."""
    kind = draw_kind(foot)
    if kind is None:
        return V06_COMPOSE_LEG(parts, side, bob, foot)
    dy = foot["o"] - foot["lift"]
    boot = shift(parts[f"boot-{side}-kick" if kind == "kick" else f"boot-{side}-{foot['view']}"], 0, dy)
    bt = min(y for (_, y) in boot)
    k0, k1 = KNEE_BAND[side]
    T, K, S = list(range(HIP_ROW, k0)), list(range(k0, k1 + 1)), list(range(k1 + 1, BOOT_TOP))
    n = bt - (HIP_ROW + bob)
    ns = max(0, n - len(T) - len(K))
    sh = pick(S, ns)
    src = b6.rows_of_part(parts[f"leg-src-{side}"])
    knee = b6.rows_of_part(parts[f"knee-{side}-fwd"])
    cuff = extent([x for (x, y) in boot if y == bt])
    kb = extent(list(knee[k1]))
    align = rdiv(cuff[0] + cuff[1] - kb[0] - kb[1], 2)
    kd = foot["kin"] * INWARD[side] + rdiv(align * max(0, 4 - ns), 4)
    out = {}
    y = HIP_ROW + bob
    nt = len(T)
    for i, sy in enumerate(T):
        dx = rdiv(kd * i * i, (nt - 1) ** 2)
        for x, c in src.get(sy, {}).items():
            out[(x + dx, y)] = c
        y += 1
    for sy in K:
        for x, c in knee[sy].items():
            out[(x + kd, y)] = c
        y += 1
    if sh:
        srow = list(src.get(BOOT_TOP - 1, {}))
        end = rdiv(cuff[0] + cuff[1] - min(srow) - max(srow), 2)
        for i, sy in enumerate(sh):
            dx = kd + rdiv((end - kd) * (i + 1), len(sh) + 1)
            for x, c in src.get(sy, {}).items():
                out[(x + dx, y)] = SHIN_SHADE.get(c, c)
            y += 1
    full = dict(boot)
    full.update(out)          # the knee / leg in front of the boot
    return full, boot, GROUND[side] + dy


def compose9(parts, state):
    """b6.compose with the v09 leg and the coat-hem drag; returns (layers, shadow, info) like b6.compose."""
    saved = b6.compose_leg
    b6.compose_leg = compose_leg9
    try:
        layers, shadow, info = b6.compose(parts, state)
    finally:
        b6.compose_leg = saved
    b, sx, csx = state["bob"], state["sx"], state["csx"]
    if csx != sx:
        # redo the composition with the dragged hem (pinhole / seam fills depend on the coat layer)
        coat = {}
        for (x, y), c in parts["coat-skirt"].items():
            coat[(x + (csx if y >= COAT_HEM_ROW else sx), y + b)] = c
        b6.compose_leg = compose_leg9
        orig_shift = b6.shift
        try:
            def shift_hook(d, dx, dy, _coat=coat, _src=parts["coat-skirt"]):
                if d is _src:
                    return dict(_coat)
                return orig_shift(d, dx, dy)
            b6.shift = shift_hook
            layers, shadow, info = b6.compose(parts, state)
        finally:
            b6.shift = orig_shift
            b6.compose_leg = saved
    # v09 see-through seam fill: a transparent texel closed left, right, above AND below (rows >= 41, below the neck) is
    # a hole between composited parts (arm / coat / cape / leg joins; v8 itself has none) -> outline ink, torso layer
    g = b6.stack(layers)
    fill = {(x, y): "K" for y in range(SEAM_ROW0, H - 1) for x in range(1, W - 1)
            if (x, y) not in g and (x - 1, y) in g and (x + 1, y) in g and (x, y - 1) in g and (x, y + 1) in g}
    layers["torso"].update(fill)
    info["v09_seam_filled"] = len(fill)
    return layers, shadow, info


def build_parts9():
    v8, P = b6.split_checked()
    parts = b6.build_parts(v8, P)
    new = {}
    for side in ("vl", "vr"):
        new[f"boot-{side}-kick"] = kick_part(side, parts)
        new[f"knee-{side}-fwd"] = knee_part(side)
    parts.update(new)
    return v8, parts, new


nominal_state9 = b6.nominal_state      # the v07 state, unchanged (v09 changes only the drawing)


# authored pose names of the 12 review keyframes (vl leads at phase 0)
POSE_NAMES = {0: "vl contact (strike, knee lean); vr knee forward, shin tucked, passing behind",
              7: "vl down / compression (body 1 row low); vr tucked knee passing the planted boot",
              14: "vl heel-up push; vr tucked knee in front", 21: "vl toe-off; vr tucked knee at the front",
              28: "flight: vl heel kick (sole under the knee); vr leg opens low toward the floor",
              35: "flight: vl heel kick; vr open leg about to land",
              42: "vr contact (strike); vl knee forward, shin tucked, passing behind",
              49: "vr down / compression; vl tucked knee passing the planted boot",
              56: "vr heel-up push; vl tucked knee in front", 63: "vr toe-off; vl tucked knee at the front",
              70: "flight: vr heel kick (sole under the knee); vl leg opens low toward the floor",
              77: "flight: vr heel kick; vl open leg about to land"}
KEY_PHASES = sorted(POSE_NAMES)


def feasibility(parts):
    states = b6.reachable_feet()
    bad = []
    for side in ("vl", "vr"):
        for bob in (0, 1):
            for (o, lift, view, kin) in sorted(states, key=str):
                try:
                    leg, boot, sole = compose_leg9(parts, side, bob, {"o": o, "lift": lift, "view": view, "kin": kin})
                except SystemExit as e:
                    bad.append((side, bob, view, o, lift, str(e)[:60]))
                    continue
                if any(not (0 <= x < W and HIP_ROW + bob <= y < H) for (x, y) in leg):
                    bad.append((side, bob, view, o, lift, "outside"))
    return len(states), bad


def to_png(grid):
    return b6.png_bytes(b6.to_rgba(grid))


def build(out_dir, preview_dir=None):
    v8, parts, new = build_parts9()
    palette = set(v8.values())
    neutral, nshadow, _ = compose9(parts, b6.NEUTRAL)
    if b6.stack(neutral) != v8:
        raise SystemExit("neutral composition != v8")
    for k, p in new.items():
        if not set(p.values()) <= palette:
            raise SystemExit(f"{k}: colour outside v8's palette")
    n_states, bad = feasibility(parts)
    if bad:
        raise SystemExit(f"{len(bad)} reachable legs do not fit: {bad[:5]}")
    frames = {}
    for ph in KEY_PHASES:
        st = nominal_state9(ph)
        layers, shadow, info = compose9(parts, st)
        g = b6.stack(layers)
        if not set(g.values()) <= palette:
            raise SystemExit(f"keyframe {ph}: colour outside v8's palette")
        if info["seam_filled"]:
            raise SystemExit(f"keyframe {ph}: neck seam fill {info['seam_filled']}")
        frames[f"k{ph:02d}"] = {"phase": ph, "state": st, "layers": layers, "grid": g, "shadow": shadow, "info": info}
    if preview_dir:
        return v8, parts, new, frames
    sd = b6.GAIT["stride_px"]
    per_px = []
    for ph in range(sd):
        st = nominal_state9(ph)
        per_px.append({"phase_px": ph, "bob": st["bob"], "hdy": st["hdy"], "sx": st["sx"], "csx": st["csx"], "arms": st["arms"],
                       "feet": {s: dict(st["feet"][s], contact=b6.in_contact(st["feet"][s])) for s in ("vl", "vr")}})
    for row in per_px:
        for side in ("vl", "vr"):
            row["feet"][side]["draw"] = draw_kind(row["feet"][side]) or ("contact" if row["feet"][side]["contact"] else "v06-leg")
    shares = {}
    for row in per_px:
        f = row["feet"]["vl"]
        if not f["contact"]:
            k = f["draw"] if f["draw"] != "v06-leg" else "v06:" + f["view"] + "-l" + str(f["lift"])
            shares[k] = shares.get(k, 0) + 1
    v07_shares = {}
    for row in per_px:
        f = row["feet"]["vl"]
        if not f["contact"]:
            k = f["view"] + "-l" + str(f["lift"])
            v07_shares[k] = v07_shares.get(k, 0) + 1
    # ------------------------------------------------------------------------------------------------- write
    os.makedirs(_fs(out_dir), exist_ok=True)
    written = []

    def put(name, data):
        in_repo = os.path.join(REPO, OUT_REL, name)
        if len(os.path.abspath(in_repo)) > REPO_PATH_LIMIT:
            raise SystemExit(f"asset path would be {len(os.path.abspath(in_repo))} characters: {name}")
        path = os.path.join(out_dir, name)
        if os.path.exists(_fs(path)):
            with open(_fs(path), "rb") as f:
                if f.read() != data:
                    raise SystemExit(f"refusing to overwrite different bytes: {name}")
        else:
            with open(_fs(path), "wb") as f:
                f.write(data)
        written.append(name)
        return hashlib.sha256(data).hexdigest()

    part_entries = []
    for role in sorted(new):
        data = to_png(new[role])
        name = f"{SLUG}_{PART}_part-{role}_{VARIANT}_{STAMP}-{fid('part-' + role)}.png"
        part_entries.append({"role": role, "file": name, "sha256": put(name, data), "opaque_texels": len(new[role])})
    key_entries = []
    for key, fr in frames.items():
        name = f"{SLUG}_{PART}_keyframe-{fr['phase']:02d}px_{VARIANT}_{STAMP}-{fid('key-' + key)}.png"
        sname = f"{SLUG}_{PART}_keyframe-{fr['phase']:02d}px-shadow_{VARIANT}_{STAMP}-{fid('kshadow-' + key)}.png"
        fr["png"] = to_png(fr["grid"])
        key_entries.append({"key": key, "phase_px": fr["phase"], "pose": POSE_NAMES[fr["phase"]], "file": name,
                            "sha256": put(name, fr["png"]), "shadow_file": sname, "shadow_sha256": put(sname, to_png(fr["shadow"])),
                            "state": fr["state"], "near_leg": fr["info"]["near"], "legs": fr["info"]["legs"]})
    keys = list(frames)
    pxo = b6.make_pxo([dict(frames[k]["layers"], shadow=frames[k]["shadow"]) for k in keys], [1.0] * len(keys),
                      frames[keys[0]]["png"], f"{PART}-keyframes", 26.7, order=b6.PXO_LAYERS, dt=(2026, 10, 18, 13, 37, 0),
                      opacity={"shadow": b6.SHADOW_OPACITY})
    pxo_name = f"{SLUG}_{PART}_keyframes-editable_{VARIANT}_{STAMP}-{fid('keyframes-pxo')}.pxo"
    pxo_sha = put(pxo_name, pxo)
    ora = make_ora(new, part_entries, b6.stack(neutral))
    ora_name = f"{SLUG}_{PART}_new-parts-editable_{VARIANT}_{STAMP}-{fid('parts-ora')}.ora"
    ora_sha = put(ora_name, ora)
    gd = os.path.join(out_dir, ".gdignore")
    if not os.path.exists(_fs(gd)):
        open(_fs(gd), "wb").close()
    manifest = {
        "project": "Worlds Between", "milestone": "M8", "character": "protagonist-female", "direction": "south",
        "motion_state": "run at MOVE_SPEED 140", "part": PART, "workstream": "m8-w12", "stamp_utc": STAMP, "run_id": RUN_ID,
        "status": "UNAPPROVED / NONRUNTIME test-only single-direction motion candidate (authored pose / gait revision over "
                  "v07); Codex / creator review pending; not a production sprite, not wired into the runtime",
        "art_approved": False, "human_reviewed": False, "runtime_integrated": False, "walk_animation_approved": False,
        "run_animation_approved": False, "stop_animation_approved": False, "counts_toward_art_acceptance": False,
        "approved_scope_unchanged": "selout v8 SOUTH IDLE static frame and the 48 logical px display scale only",
        "exploration_sprites_counter_unchanged": "0/52",
        "amends": {"v06_manifest": V06_MANIFEST_REL, "v06_manifest_sha256_text_lf_v1": V06_MANIFEST_SHA256_TEXT_LF,
                   "v06_builder": "tools/" + V06_BUILDER, "v06_builder_sha256_text_lf_v1": V06_BUILDER_DIGEST,
                   "v07_control": "rise lock (v07 restart amendment) kept on; v07 gait driver class used unchanged",
                   "reads_v06_art_read_only": "every v06 part PNG (boots of the v06 views, legs, arms, cape, hair, torso, "
                                              "head, hips, coat, shadows) is used unchanged from game/assets/characters/run-v06-unapproved/"},
        "builder": "tools/" + os.path.basename(os.path.abspath(__file__)),
        "gait": {"unchanged_from_v07": True, "swing_keys": V07_SWING_KEYS,
                 "note": "the gait-driver state is v07's for every input (stride 84 px, stance 21 px, land +2, lift-off -19, "
                         "swing keys incl. views, stance roll, bob / torso / arm / hair / cape timing, stop clock, re-press, "
                         "rise lock); v09 changes only what is drawn for a state",
                 "rejected_drafts": ["boot path moved back for a deeper heel kick: 60 fps stop 200 -> 216.7 ms (state-level sim)",
                                     "v07 path with a changed view column (hang until u 840): a 48 fps stop held a boot raised "
                                     "104 ms (> 100) because the stop allows one boot view change per tick"],
                 "swing_px_by_drawn_pose_v09": shares, "swing_px_by_view_v07": v07_shares},
        "art_amendment": {
            "draw_rule": "toe at lift >= 2 -> kick (boot-<side>-kick + tucked leg); hang, or reach at lift >= 2 -> tucked leg "
                         "with the state's own boot view; every other state -> the v06 leg",
            "kick_drop_rows": KICK_DROP, "shin_shade": SHIN_SHADE,
            "shin_shade_rgb": {b6.ROLES[k]: b6.ROLES[v] for k, v in SHIN_SHADE.items()},
            "kick_boot_rows": {s: [list(r) for r in KICK_BOOT[s]] for s in ("vl", "vr")},
            "knee_fwd": {s: {str(y): list(v) for y, v in KNEE_FWD[s].items()} for s in ("vl", "vr")},
            "coat_hem_row": COAT_HEM_ROW, "seam_row0": SEAM_ROW0,
            "seam_rule": "after v06's pinhole / neck-seam fills: every transparent texel at row >= seam_row0 closed left, "
                         "right, above and below by opaque texels -> ink (#0a0a0e), all found first then filled; v8 has none",
            "leg_rule_tucked": "kick / tuck: rows hip(61+bob).. = v8 thigh rows 1:1 (lean t^2 toward kd), the authored "
                               "forward knee band 1:1 at kd, then shin rows = pick(v8 shin rows, max(0, boot top - hip - "
                               "thigh - knee)) shaded one ramp step darker, sloping to the cuff; kd = kin * inward + "
                               "rdiv(align * max(0, 4 - shin rows), 4), align = rdiv(cuff top-row x0 + x1 - knee bottom-row "
                               "x0 - x1, 2); the boot is drawn first and the leg over it (the knee in front)",
            "leg_rule_other_views": "v06 compose_leg unchanged (contact views, toe at lift <= 1, reach at lift 1, strike)",
            "coat_rule": "coat-skirt rows < 66 at (sx, bob) as v06; rows >= 66 at (csx, bob) - the hem trails the torso shift "
                         "by the cape lag (csx == sx on the neutral state, so the stop still ends on v8 exactly)"},
        "parts_new": part_entries,
        "keyframes": key_entries,
        "editable_sources": {"keyframes_pxo": pxo_name, "keyframes_pxo_sha256": pxo_sha, "keyframes_pxo_layers": b6.PXO_LAYERS,
                             "new_parts_ora": ora_name, "new_parts_ora_sha256": ora_sha},
        "metrics": {"reachable_foot_states": n_states, "nominal_per_px": per_px},
    }
    mname = f"{SLUG}_{PART}_pose-gait-manifest_{VARIANT}_{STAMP}-{fid('manifest')}.json"
    put(mname, (json.dumps(manifest, indent=1) + "\n").encode("utf-8"))
    print(f"wrote {len(written)} files to {out_dir}")
    print("MANIFEST", mname)
    return manifest


def make_ora(parts, part_entries, merged):
    dt = (2026, 10, 18, 13, 37, 0)
    lines = ['<?xml version="1.0" encoding="UTF-8"?>', f'<image version="0.0.6" w="{W}" h="{H}">', "  <stack>"]
    for e in reversed(part_entries):
        lines.append(f'    <layer name="{e["role"]}" src="data/{e["role"]}.png" x="0" y="0" opacity="1.000" '
                     'visibility="visible" composite-op="svg:src-over"/>')
    lines += ["  </stack>", "</image>", ""]
    merged_png = to_png(merged)
    members = [("mimetype", b"image/openraster"), ("stack.xml", "\n".join(lines).encode("utf-8"))]
    members += [(f"data/{e['role']}.png", to_png(parts[e["role"]])) for e in part_entries]
    members += [("Thumbnails/thumbnail.png", merged_png), ("mergedimage.png", merged_png)]
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w") as z:
        for name, data in members:
            zi = zipfile.ZipInfo(name, date_time=dt)
            zi.compress_type = zipfile.ZIP_STORED
            zi.create_system = 3
            zi.external_attr = 0o100644 << 16
            z.writestr(zi, data)
    return buf.getvalue()


def preview(out_dir):
    """Scratch only: v07 (v06 art + v06 swing) and v09 keyframes, one PNG per keyframe per version, at 1x and 6x."""
    v8, parts, new, frames = build(None, preview_dir=out_dir)
    os.makedirs(_fs(out_dir), exist_ok=True)
    for ver in ("v07", "v09"):
        for ph in KEY_PHASES:
            if ver == "v09":
                fr = frames[f"k{ph:02d}"]
                grid, shadow = fr["grid"], fr["shadow"]
            else:
                layers, shadow, _ = b6.compose(parts, b6.nominal_state(ph))
                grid = b6.stack(layers)
            for scale in (1, 6):
                bg = Image.new("RGBA", (W, H), (150, 140, 128, 255))
                sh = b6.to_rgba(shadow)
                sh[..., 3] = (sh[..., 3].astype(np.float32) * b6.SHADOW_OPACITY).astype(np.uint8)
                bg.alpha_composite(Image.fromarray(sh, "RGBA"))
                bg.alpha_composite(Image.fromarray(b6.to_rgba(grid), "RGBA"))
                bg.resize((W * scale, H * scale), Image.NEAREST).save(_fs(os.path.join(out_dir, f"{ver}_k{ph:02d}_x{scale}.png")))
    print("preview written to", out_dir)


def main():
    ap = argparse.ArgumentParser()
    g = ap.add_mutually_exclusive_group(required=True)
    g.add_argument("--out-dir")
    g.add_argument("--preview")
    a = ap.parse_args()
    if a.preview:
        p = os.path.abspath(a.preview)
        if os.path.normcase(p).startswith(os.path.normcase(REPO) + os.sep):
            raise SystemExit("--preview must be outside the repository")
        preview(p)
    else:
        build(os.path.abspath(a.out_dir))


if __name__ == "__main__":
    main()
