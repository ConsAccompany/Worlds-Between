"""UNAPPROVED, read-only measure for the female side-view battle idle STATIC candidate v13 (NONRUNTIME, test-only).
Bounded copy of the v12 measure tool (v11 -> v12, v12 -> v13), plus a boot split by the runtime contact-shadow ellipse
and a back-region darkness count.

For each real Godot 640x360 four-person capture of v13 and its matching no-sprite frame (probe, draw-order or overlay
mode of the v13 capture script):
  1. fidelity: the v13 PNG drawn texel-for-texel at the texture origin (268, 204) over the no-sprite frame must equal the
     Godot capture RGBA exactly, and only the sprite's own opaque texels may differ
  2. v12 (locked PNG) composited offline over the same no-sprite frame, so v12 and v13 are compared on an identical
     background (valid: neither has an opaque texel under a companion and both share the same pin)
  3. per region, excluding the outline colour: mean |dL| (Rec.709 luma) of sprite texels against the background they
     cover, share with |dL| < 20, background mean L, saturated-orange share. Regions: head rows 1-19, torso 20-37, lower
     body 38-67, boots 57-67, boot contact rows 62-66, and (v13) the boot texels on rows 57-66 split into those standing
     on paving and those inside the runtime contact-shadow ellipse (radius 18, y scale 0.28 at the pin)
  3b. back region (x <= 31, rows 20-56: pack, roll, back tail): texels darker than L 45 incl. outline, and mean L
Sprite-only (no capture needed):
  4. silhouette width per band (bbox width and mean opaque texels per row), all layers and without the sword
     (sword-blade, sword-guard, fist, read from each version's .ora): head 7-19, torso 20-39, coat skirt 40-56,
     lower body 40-67, boots 57-67
  5. foot pin: pin texel (32, 68) -> screen (300, 272); sole row; per-boot texel span on the sole row
Writes nothing; prints one JSON report.

Run:  python -I -B <this file> <arena>=<mode>=<v13 capture png>=<no-sprite png> [...]  (mode: probe | draw-order | overlay)
"""
import colorsys, hashlib, io, json, os, sys, zipfile
import numpy as np
from PIL import Image

REPO = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
D = "game/assets/characters/combat-sideview-pilots/rpg-2-star-ocean-the-second_protagonist-female_sideview-idle-right-static-native0p65_"
SPRITES = {
    "v12": (D + "unapproved-v12_20261017-224530-fbd81525.png",
            "27f0f79e25dd7587386c5e20df865322aea3a6de024bcf8e745fe02b97c3a079",
            D + "editable-layers_unapproved-v12_20261017-224530-2ae3fe34.ora",
            "4fde9395cab3cf66377f12f6f4b0c309308cc56fd43857e7eda12ca5f3c8772d"),
    "v13": (D + "unapproved-v13_20261017-235615-1195f40e.png",
            "5b295aa1d19dcceb69b740e983eb2695d966701a4ead4ad8bbb72f13af6ebdb2",
            D + "editable-layers_unapproved-v13_20261017-235615-3fffbeeb.ora",
            "0fb1eda94deb9721446e543883779975bbb2983a516b0acb1017d83373088fb7"),
}
ORIGIN = (268, 204)                 # texel (0, 0) at 640x360: hero x 300 - pin x 32, floor 272 - pin y 68
PIN = (32, 68)
OUTLINE = (0x16, 0x14, 0x1A)
REGIONS = {"head": (1, 19), "torso": (20, 37), "lower_body": (38, 67), "boots": (57, 67), "boot_contact": (62, 66)}
BANDS = {"head": (7, 19), "torso": (20, 39), "coat_skirt": (40, 56), "lower_body": (40, 67), "boots": (57, 67)}
SWORD = ("sword-blade", "sword-guard", "fist")
BACK = (31, 20, 56)                 # x <= 31, rows 20-56


def shadow_mask(h, w):
    """Texels whose screen-pixel centre is inside the runtime contact shadow (pin on screen (300, 272), radius 18,
    y scale 0.28); the probe/draw-order no-sprite frames confirm the span row by row."""
    ty, tx = np.mgrid[0:h, 0:w]
    dx = (ORIGIN[0] + tx + 0.5 - 300.0) / 18.0
    dy = (ORIGIN[1] + ty + 0.5 - 272.0) / (18.0 * 0.28)
    return dx * dx + dy * dy <= 1.0


def _fs(path):
    """Extended-length prefix on Windows: the .ora paths are longer than MAX_PATH (LongPathsEnabled is 0)."""
    path = os.path.abspath(path)
    return "\\\\?\\" + path if os.name == "nt" and len(path) > 247 and not path.startswith("\\\\?\\") else path


def read(rel, want):
    with open(_fs(os.path.join(REPO, *rel.split("/"))), "rb") as f:
        data = f.read()
    if hashlib.sha256(data).hexdigest() != want:
        raise SystemExit(f"hash changed: {rel}")
    return data


def rgba(data):
    return np.array(Image.open(io.BytesIO(data)).convert("RGBA"))


def lum(rgb):
    rgb = np.asarray(rgb, float)
    return 0.2126 * rgb[..., 0] + 0.7152 * rgb[..., 1] + 0.0722 * rgb[..., 2]


def orange(rgb):
    h, s, v = colorsys.rgb_to_hsv(*(int(c) / 255 for c in rgb))
    return 10 / 360 <= h <= 50 / 360 and s >= 0.45 and v >= 0.40


def composite(sprite, bg):
    out = bg.copy()
    h, w = sprite.shape[:2]
    x0, y0 = ORIGIN
    m = sprite[..., 3] == 255
    out[y0:y0 + h, x0:x0 + w][m] = sprite[m]
    return out


def regions(sprite, bg):
    h, w = sprite.shape[:2]
    x0, y0 = ORIGIN
    under = bg[y0:y0 + h, x0:x0 + w, :3]
    op = (sprite[..., 3] == 255) & ~(sprite[..., :3] == np.array(OUTLINE)).all(-1)
    out = {}
    sh = shadow_mask(h, w)
    masks = {}
    for name, (r0, r1) in REGIONS.items():
        m = op.copy()
        m[:r0] = False
        m[r1 + 1:] = False
        masks[name] = m
    boots = masks["boots"].copy()
    boots[67:] = False
    masks["boots_rows_57_66_on_paving"] = boots & ~sh
    masks["boots_rows_57_66_in_shadow"] = boots & sh
    for name, m in masks.items():
        d = np.abs(lum(sprite[..., :3][m]) - lum(under[m]))
        out[name] = {"texels": int(m.sum()), "mean_abs_dL": round(float(d.mean()), 1),
                     "share_abs_dL_lt_20": round(float((d < 20).mean()), 3),
                     "background_mean_L": round(float(lum(under[m]).mean()), 1),
                     "orange_share": round(sum(orange(c) for c in sprite[..., :3][m]) / max(1, int(m.sum())), 3)}
    back = sprite[..., 3] == 255
    back[:, BACK[0] + 1:] = False
    back[:BACK[1]] = False
    back[BACK[2] + 1:] = False
    L = lum(sprite[..., :3])
    out["back_region_x_le_31_rows_20_56"] = {"texels": int(back.sum()), "texels_L_lt_45_incl_outline": int((back & (L < 45)).sum()),
                                             "texels_L_lt_45_excl_outline": int((back & op & (L < 45)).sum()),
                                             "mean_L_excl_outline": round(float(L[back & op].mean()), 1)}
    return out


def widths(alpha):
    out = {}
    for name, (r0, r1) in BANDS.items():
        a = alpha[r0:r1 + 1]
        xs = np.nonzero(a.any(0))[0]
        out[name] = {"bbox_x": [int(xs.min()), int(xs.max())], "bbox_width": int(xs.max() - xs.min() + 1),
                     "mean_opaque_texels_per_row": round(float(a.sum(1).mean()), 1),
                     "max_row_span": int(max((np.nonzero(r)[0].max() - np.nonzero(r)[0].min() + 1) if r.any() else 0
                                             for r in a))}
    return out


def ora_alpha_without(ora, skip):
    with zipfile.ZipFile(io.BytesIO(ora)) as z:
        names = [n[len("data/"):-len(".png")] for n in z.namelist() if n.startswith("data/") and n.endswith(".png")]
        a = None
        for n in names:
            if n == "guides" or n in skip:
                continue
            la = rgba(z.read(f"data/{n}.png"))[..., 3] > 0
            a = la if a is None else (a | la)
    return a


def foot_pin(alpha):
    sole = int(np.nonzero(alpha.any(1))[0].max())
    runs, x = [], 0                     # contiguous opaque runs on the sole row (one per boot)
    while x < alpha.shape[1]:
        if alpha[sole, x]:
            x1 = x
            while x1 + 1 < alpha.shape[1] and alpha[sole, x1 + 1]:
                x1 += 1
            runs.append([x, x1])
            x = x1 + 1
        else:
            x += 1
    return {"pin_texel": list(PIN), "pin_screen": [ORIGIN[0] + PIN[0], ORIGIN[1] + PIN[1]], "sole_row": sole,
            "sole_screen_y": ORIGIN[1] + sole, "pin_row_and_below_clear": bool(not alpha[PIN[1]:].any()),
            "sole_row_runs_x": runs, "stance_x_on_sole_row": [runs[0][0], runs[-1][1]] if runs else None,
            "pin_column_clear_on_sole_row": bool(not alpha[sole, PIN[0]])}


def main():
    spr, sprite_only = {}, {}
    for ver, (png_rel, png_sha, ora_rel, ora_sha) in SPRITES.items():
        spr[ver] = rgba(read(png_rel, png_sha))
        ora = read(ora_rel, ora_sha)
        a = spr[ver][..., 3] > 0
        sprite_only[ver] = {"opaque_texels": int(a.sum()), "widths_all_layers": widths(a),
                            "widths_without_sword_arm_hand": widths(ora_alpha_without(ora, SWORD)),
                            "foot_pin": foot_pin(a)}
    report = {"status": "UNAPPROVED, NONRUNTIME read-only measure; writes nothing", "sprites": sprite_only,
              "arenas": {}}
    ok = True
    for arg in sys.argv[1:]:
        arena, mode, cap_path, ns_path = arg.split("=")
        cap, bg = np.array(Image.open(cap_path).convert("RGBA")), np.array(Image.open(ns_path).convert("RGBA"))
        if cap.shape != (360, 640, 4) or bg.shape != (360, 640, 4):
            raise SystemExit(f"{arena}: expected 640x360 frames")
        exact = bool(np.array_equal(composite(spr["v13"], bg), cap))
        diff_px = int((cap != bg).any(-1).sum())
        expected_px = int((spr["v13"][..., 3] == 255).sum())
        ok &= exact and diff_px == expected_px
        entry = {"mode": mode, "capture_sha256": hashlib.sha256(open(cap_path, "rb").read()).hexdigest(),
                 "nosprite_sha256": hashlib.sha256(open(ns_path, "rb").read()).hexdigest(),
                 "offline_v13_composite_equals_godot_capture": exact,
                 "capture_minus_nosprite_changed_px": diff_px, "v13_opaque_texels": expected_px,
                 "v13": regions(spr["v13"], bg),
                 # valid in both modes: neither version has an opaque texel under a companion (0 px overlap in every
                 # capture manifest) and both share the same screen bbox, so draw order cannot change their pixels
                 "v12_same_background": regions(spr["v12"], bg)}
        report["arenas"][f"{arena}:{mode}"] = entry
    report["fidelity_pass"] = ok
    print(json.dumps(report, indent=1))
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
