"""Female protagonist SOUTH RUN v10r1: ONE bounded amendment of v10 (m8-w14) - shorter leading reach + landing rule.

UNAPPROVED / NONRUNTIME, test-only, single direction.  Not art acceptance, not runtime integration, not a production
sprite.  The creator approved only the selout v8 SOUTH IDLE static frame and the 48 logical px display scale.

Parent: the v10 builder (read-only, sha256-text-lf-v1 pinned; the v10 asset folder and evidence are preserved unchanged).
Root review of v10: the slower cycle reads differently and identity is kept, but the leading leg is still a long
diagonal, and one mixed-frame-time stop held a boot raised 105.6 ms (Root criterion <= 100 ms).  v10r1 changes:

  * REACH (Root's choice): the same 44 px stance on the same 128 px stride (4.375 steps/s, 68.75 % contact) is split
    +8 / -36 instead of +12 / -32: the boot lands 8 rows in front of its v8 spot (4 fewer) and leaves 36 behind.  The
    planted boot still keeps its window row over the whole stance.  Stance-roll, torso-compression and torso-shift
    timing stay on v10's q (px since touchdown); the knee lean returns to 0 at the v8 spot (q 8).
  * SWING (re-authored curve, not a uniform stretch): the knee stays tucked forward through passing (hang until u 740,
    o -2), the leg opens late and short (reach u 740..940, o -2 -> +7) and the heel strike is a short lift-1 pose
    (o +7 -> +8).  v10 opened the leg at u 650 (o -5) and reached to o +12.
  * LANDING RULE (driver, recorded in the manifest stop block; implemented by the v10r1 capture tool): after a release,
    landing boots move on their own clock - a landing boot's mid-key view change is no longer held back by the other
    boot's change; only TOUCHDOWNS are staggered (two boots never touch down on the same frame; the later one keeps its
    last in-air key and touches down on the next frame).  The stop shuffle and the body settle keep v06's rules.
  * Art, leg rule, push-off boots, coat lag, seam ink and island rule are v10's unchanged; the new parts are v10's files
    (no new part PNGs).

Writes (only with --out-dir): 16 keyframe + 16 shadow PNGs, the keyframes .pxo (Pixelorama 1.2.3, 13 layers incl. the
shadow), a copy of v10's push-boot .ora (unchanged parts), the gait / pose manifest (parent v10 manifest + hash; sha256
of all 128 per-px nominal composites).  --preview <dir> writes scratch PNGs outside the repository.

Usage (repository root):
  python -I -B tools/<this file> --out-dir game/assets/characters/run-v10r1-unapproved
  python -I -B tools/<this file> --preview <abs scratch dir>
"""
import argparse, hashlib, importlib.util, json, os, sys

import numpy as np
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(HERE)
V10_BUILDER = "rpg-2-star-ocean-the-second_female-south-run-v10_authored-gait-pushoff-build_m8-w13_20261018-143213-ed496e32.py"
V10_BUILDER_SHA256_TEXT_LF = "1516f7f2ca8fa36ab5c354b625f1b2a5b41e0a1241bc3e995bc5d73126e8b859"
V10_DIR_REL = "game/assets/characters/run-v10-unapproved"
V10_MANIFEST = "rpg-2-star-ocean-the-second_female-south-run-v10_gait-pose-manifest_unapproved_20261018-143213-63dec7d3.json"
V10_MANIFEST_SHA256_TEXT_LF = "de1789e376c34340e8a4a61289b0998c917b954c9b48bd6bff6d46a999062cbd"
OUT_REL = "game/assets/characters/run-v10r1-unapproved"
SLUG = "rpg-2-star-ocean-the-second"
PART = "female-south-run-v10r1"
VARIANT = "unapproved"
STAMP = "20261018-142136"
RUN_ID = "249dbf66"
REPO_PATH_LIMIT = 250


def _fs(path):
    path = os.path.abspath(path)
    if os.name == "nt" and len(path) > 247 and not path.startswith("\\\\?\\"):
        return "\\\\?\\" + path
    return path


def sha_text_lf(path):
    with open(_fs(path), "rb") as f:
        return hashlib.sha256(f.read().replace(b"\r\n", b"\n")).hexdigest()


def load_v10():
    path = os.path.join(HERE, V10_BUILDER)
    if sha_text_lf(path) != V10_BUILDER_SHA256_TEXT_LF:
        raise SystemExit("v10 builder is not the pinned file")
    if sha_text_lf(os.path.join(REPO, V10_DIR_REL, V10_MANIFEST)) != V10_MANIFEST_SHA256_TEXT_LF:
        raise SystemExit("v10 manifest is not the pinned file")
    spec = importlib.util.spec_from_file_location("v10_builder", path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)          # the v10 module pins the v09 builder, which pins v06
    return mod


b10 = load_v10()
b6 = b10.b6
W, H = b6.W, b6.H


def fid(role):
    return hashlib.sha256(f"{RUN_ID}:{role}".encode()).hexdigest()[:8]


# ===================================================================================================== r1 gait
SD, E, A = 128, 44, 8
BK = A - E                       # -36
GAIT_R1 = dict(b10.GAIT10)
GAIT_R1.update({
    "land_offset": A, "liftoff_offset": BK,
    "stance_knee_kin": [[0, 1], [A, 0]],
    # (u per mille of the 84 px swing, o, lift, view from this key on, knee lean)
    "swing_keys": [
        [0, BK, 1, "toe", 0],
        [100, -34, 3, "kick", 1],
        [250, -29, 4, "kick", 1],
        [380, -22, 4, "hang", 1],
        [520, -14, 4, "hang", 1],
        [650, -7, 3, "hang", 1],
        [740, -2, 3, "reach", 1],
        [860, 4, 2, "reach", 1],
        [940, 7, 1, "strike", 1],
        [1000, A, 1, "strike", 1],
    ],
})
STOP_R1 = dict(b10.STOP10)
STOP_R1.update({
    "v10r1_landing_rule": "after a release, landing boots move on their own event clock: a landing boot's view change "
                          "(start key -> mid key) is not held back by the other boot's change; only touchdowns are "
                          "staggered - two boots never touch down on the same frame: the boot whose touchdown is due "
                          "first (tie: the earlier move start, then vl) lands, the other keeps its last in-air key "
                          "(u 999) and lands on the next frame.  v06's no-pose-skip (a boot shows its mid key before "
                          "touching down), the shuffle (one boot at a time, after every landing) and the body settle "
                          "are unchanged.  (v06 / v10: at most one boot changed its view per frame; the held boot's "
                          "clock moved by <= hold_shift_ms, so a stop released with both boots in the air could hold "
                          "the second boot raised 105.6 ms with mixed frame times.)",
})
RESTART_R1 = dict(b10.RESTART10)

POSE_NAMES = {
    0: "vl heel strike 8 rows in front; vr toe-off behind the knee",
    8: "vl at its v8 spot, loading (body 1 row down); vr heel kick",
    16: "vl mid-stance (2 rows down); vr kick, sole under the knee",
    24: "vl mid-stance; vr tucked knee passing",
    32: "vl heel-up push (1 row down); vr foot hanging under the knee",
    40: "vl push-off, boot behind the knee; vr knee still tucked forward",
    48: "flight: vl toe-off; vr leg opening late",
    56: "flight: vl kick; vr short reach, about to strike",
    64: "vr heel strike 8 rows in front; vl toe-off behind the knee",
    72: "vr at its v8 spot, loading (body 1 row down); vl heel kick",
    80: "vr mid-stance (2 rows down); vl kick, sole under the knee",
    88: "vr mid-stance; vl tucked knee passing",
    96: "vr heel-up push (1 row down); vl foot hanging under the knee",
    104: "vr push-off, boot behind the knee; vl knee still tucked forward",
    112: "flight: vr toe-off; vl leg opening late",
    120: "flight: vr kick; vl short reach, about to strike",
}


def apply_r1():
    """Point the v10 module's gait globals at the r1 values (its nominal / reachable / feasibility helpers read them)."""
    b10.A, b10.BK, b10.E, b10.SD = A, BK, E, SD
    b10.GAIT10 = GAIT_R1
    b10.STOP10 = STOP_R1
    b10.RESTART10 = RESTART_R1


apply_r1()


# ===================================================================================================== build
def grid_sha(grid, shadow):
    return hashlib.sha256(b6.to_rgba(grid).tobytes() + b6.to_rgba(shadow).tobytes()).hexdigest()


def build(out_dir):
    v8, parts, new9, new = b10.build_parts10()
    palette = set(v8.values())
    neutral, _, _ = b10.compose10(parts, b6.NEUTRAL)
    if b6.stack(neutral) != v8:
        raise SystemExit("neutral composition != v8")
    n_states, bad, modes = b10.feasibility(parts)
    if bad:
        raise SystemExit(f"{len(bad)} reachable legs do not fit: {bad[:5]}")
    frames = b10.frames_of(parts)
    for key, fr in frames.items():
        if not set(fr["grid"].values()) <= palette:
            raise SystemExit(f"{key}: colour outside v8's palette")
        if fr["info"]["seam_filled"]:
            raise SystemExit(f"{key}: neck seam fill {fr['info']['seam_filled']}")
        if len(b10.components8(fr["grid"])) != 1:
            raise SystemExit(f"{key}: more than one silhouette")
    per_px = []
    for ph in range(SD):
        st = b10.nominal_state(ph)
        layers, shadow, info = b10.compose10(parts, st)
        per_px.append({"phase_px": ph, "bob": st["bob"], "hdy": st["hdy"], "sx": st["sx"], "csx": st["csx"], "arms": st["arms"],
                       "feet": {s: dict(st["feet"][s], contact=b10.in_contact(st["feet"][s]), leg_mode=info["leg_modes"][s]["mode"])
                                for s in ("vl", "vr")},
                       "composite_sha256": grid_sha(b6.stack(layers), shadow),
                       "silhouettes": len(b10.components8(b6.stack(layers))), "leg_islands_dropped": info["v10_leg_islands_dropped"]})
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

    m10 = json.load(open(_fs(os.path.join(REPO, V10_DIR_REL, V10_MANIFEST)), encoding="utf-8"))
    key_entries = []
    for key, fr in frames.items():
        name = f"{SLUG}_{PART}_keyframe-{fr['phase']:03d}px_{VARIANT}_{STAMP}-{fid('key-' + key)}.png"
        sname = f"{SLUG}_{PART}_keyframe-{fr['phase']:03d}px-shadow_{VARIANT}_{STAMP}-{fid('kshadow-' + key)}.png"
        fr["png"] = b10.to_png(fr["grid"])
        key_entries.append({"key": key, "phase_px": fr["phase"], "pose": POSE_NAMES[fr["phase"]], "file": name,
                            "sha256": put(name, fr["png"]), "shadow_file": sname, "shadow_sha256": put(sname, b10.to_png(fr["shadow"])),
                            "state": fr["state"], "near_leg": fr["info"]["near"], "legs": fr["info"]["legs"],
                            "leg_modes": fr["info"]["leg_modes"]})
    keys = list(frames)
    pxo = b6.make_pxo([dict(frames[k]["layers"], shadow=frames[k]["shadow"]) for k in keys], [1.0] * len(keys),
                      frames[keys[0]]["png"], f"{PART}-keyframes", 35.0, order=b6.PXO_LAYERS, dt=(2026, 10, 18, 14, 21, 36),
                      opacity={"shadow": b6.SHADOW_OPACITY})
    pxo_name = f"{SLUG}_{PART}_keyframes-editable_{VARIANT}_{STAMP}-{fid('keyframes-pxo')}.pxo"
    pxo_sha = put(pxo_name, pxo)
    gd = os.path.join(out_dir, ".gdignore")
    if not os.path.exists(_fs(gd)):
        open(_fs(gd), "wb").close()
    gn = b10.gait_numbers()
    gn["v10_reference"] = {"land_offset": 12, "liftoff_offset": -32, "stride_px": 128, "stance_px": 44, "steps_per_s": 4.375,
                           "ground_contact_share": 0.6875}
    manifest = {
        "project": "Worlds Between", "milestone": "M8", "character": "protagonist-female", "direction": "south",
        "motion_state": "run at MOVE_SPEED 140", "part": PART, "workstream": "m8-w14", "stamp": STAMP, "run_id": RUN_ID,
        "status": "UNAPPROVED / NONRUNTIME test-only single-direction motion candidate: bounded r1 amendment of v10 "
                  "(shorter leading reach +8 / -36 over the same 44 px stance, re-authored swing curve, staggered-touchdown "
                  "landing rule); Root / creator review pending; not a production sprite, not wired into the runtime",
        "art_approved": False, "human_reviewed": False, "runtime_integrated": False, "walk_animation_approved": False,
        "run_animation_approved": False, "stop_animation_approved": False, "counts_toward_art_acceptance": False,
        "approved_scope_unchanged": "selout v8 SOUTH IDLE static frame and the 48 logical px display scale only",
        "exploration_sprites_counter_unchanged": "0/52",
        "parent": {"version": "v10", "v10_builder": "tools/" + V10_BUILDER, "v10_builder_sha256_text_lf_v1": V10_BUILDER_SHA256_TEXT_LF,
                   "v10_manifest": V10_DIR_REL + "/" + V10_MANIFEST, "v10_manifest_sha256_text_lf_v1": V10_MANIFEST_SHA256_TEXT_LF,
                   "v10_status": "preserved unchanged (assets, tools, receipts, MP4s, PNGs); r1 writes only its own folder",
                   "changed": ["land_offset 12 -> 8, liftoff_offset -32 -> -36 (same stance / stride)",
                               "stance_knee_kin returns to 0 at q 8", "swing_keys re-authored", "stop: staggered-touchdown landing rule"],
                   "unchanged": ["art parts (v10 push-boot parts, v09 kick / knee parts, v06 parts)", "leg rule", "coat rule",
                                 "seam and island rules", "stance roll / bob / torso-shift q tables", "arms / hair / cape timing",
                                 "stop durations", "re-press rule + rise lock"]},
        "based_on": m10["based_on"],
        "builder": "tools/" + os.path.basename(os.path.abspath(__file__)),
        "units": m10["units"],
        "gait": dict(GAIT_R1, **gn),
        "stop": STOP_R1, "restart": RESTART_R1,
        "leg_rule": m10["leg_rule"], "coat_rule": m10["coat_rule"], "seam_rule": m10["seam_rule"],
        "island_rule": m10["island_rule"], "island_max_texels": m10["island_max_texels"],
        "parts_new": [dict(e, file_dir=V10_DIR_REL) for e in m10["parts_new"]],
        "parts_new_note": "v10's push-boot part PNGs, used read-only from the v10 folder (no new part PNGs in r1)",
        "parts_from_v09": m10["parts_from_v09"],
        "keyframes": key_entries,
        "editable_sources": {"keyframes_pxo": pxo_name, "keyframes_pxo_sha256": pxo_sha, "keyframes_pxo_layers": b6.PXO_LAYERS,
                             "new_parts_ora": V10_DIR_REL + "/" + m10["editable_sources"]["new_parts_ora"],
                             "new_parts_ora_sha256": m10["editable_sources"]["new_parts_ora_sha256"]},
        "metrics": {"reachable_foot_states": n_states, "reachable_leg_modes_x_sides_x_bob": modes, "nominal_per_px": per_px},
    }
    mname = f"{SLUG}_{PART}_gait-pose-manifest_{VARIANT}_{STAMP}-{fid('manifest')}.json"
    put(mname, (json.dumps(manifest, indent=1) + "\n").encode("utf-8"))
    print(f"wrote {len(written)} files to {out_dir}")
    print("MANIFEST", mname)
    print("GAIT", json.dumps(gn))
    return manifest


def preview(out_dir):
    v8, parts, _, _ = b10.build_parts10()
    os.makedirs(_fs(out_dir), exist_ok=True)
    for ph in range(SD):
        layers, shadow, info = b10.compose10(parts, b10.nominal_state(ph))
        grid = b6.stack(layers)
        bg = Image.new("RGBA", (W, H), (150, 140, 128, 255))
        sh = b6.to_rgba(shadow)
        sh[..., 3] = (sh[..., 3].astype(np.float32) * b6.SHADOW_OPACITY).astype(np.uint8)
        bg.alpha_composite(Image.fromarray(sh, "RGBA"))
        bg.alpha_composite(Image.fromarray(b6.to_rgba(grid), "RGBA"))
        bg.save(_fs(os.path.join(out_dir, f"v10_p{ph:03d}_x1.png")))
    print("GAIT", json.dumps(b10.gait_numbers()))
    n_states, bad, modes = b10.feasibility(parts)
    print("reachable", n_states, "bad", len(bad), bad[:5], modes)


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
