"""UNAPPROVED, read-only measure of the female battle static v15 party captures against v14 (writes nothing; JSON to stdout).

Inputs: the locked v14 PNG and its four tracked 640x360 probe captures (archive / outskirts x zh / en), the v15 PNG and
its four captures + manifests in outputs/battle-static-v15, and the run directory holding the no-sprite frames of the
v15 runs and of the v14 control runs made in the SAME isolated 160b823 tree (ns_v15_<floor>-640-<lang>.png,
ns_v14_<floor>-640-<lang>.png, v14ctl_<floor>-640-<lang>.png). Checks, per floor x language:
  1. environment: the v14 control capture equals the tracked v14 capture byte for byte, and the v15 run's no-sprite
     frame equals the v14 control run's (so the only difference between v14 and v15 captures is the sprite)
  2. fidelity: the v15 PNG composited at texture origin (268, 204) over the v15 no-sprite frame equals the v15 capture;
     v15 capture differs from the v14 capture only inside the sprite's alpha
  3. probe manifest fields: sprite pixels 1590/1590, 0 off-palette, nearest match 1.0, crown y 211, sole y 271, bbox
     283-328, 0 opaque overlap with every companion, HUD language
  4. DESCRIPTIVE (not gated, no thresholds): per region the mean |dL| (Rec.709 luma) of sprite texels against the floor
     pixels they cover and the share with |dL| < 20 (outline excluded), for v14 and v15 on the identical frame; the
     same region set as the v13-vs-v14 measure tool. A number does not decide whether the frame reads better.

Run: python -I -B <this file> <run dir>
"""
import hashlib, io, json, os, sys
import numpy as np
from PIL import Image

REPO = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
ORIGIN = (268, 204)
OUTLINE = (0x16, 0x14, 0x1A)
V14_PNG = ("game/assets/characters/combat-sideview-pilots/rpg-2-star-ocean-the-second_protagonist-female_sideview-"
           "idle-right-static-native0p65_unapproved-v14_20261018-084553-336f663b.png",
           "86286082c59d923e27fdf572a616467e9acfb2912d55c7b639167c8789ae43dc")
V15_DIR = "outputs/battle-static-v15"
V15_PNG = (V15_DIR + "/rpg-2-star-ocean-the-second_female-battle-idle-right_static-native0p65_unapproved-v15_"
           "20261018-210446-abde2095.png", "c6aca9b804d1fd83c284c1491cbeb347190d2528d8f05c460e1e055800e1f4e2")
_V14C = "outputs/rpg-2-star-ocean-the-second_protagonist-female_sideview-idle-right-static-native0p65_party-capture-"
V14_CAPS = {
    ("archive", "zh"): (_V14C + "archive-640-probe-zh_unapproved-v14_20261018-084553-5a0ec9d0.png",
                        "775803bfb013097db6450605548018f7e56c8bcc601f17849ff993518f92b414"),
    ("archive", "en"): (_V14C + "archive-640-probe-en_unapproved-v14_20261018-084553-7c83e367.png",
                        "1ddd41235a53f345b6ff9ea41cfe9bd89fd482900cdedaf6077b9046c75970c1"),
    ("outskirts", "zh"): (_V14C + "outskirts-640-probe-zh_unapproved-v14_20261018-084553-f1b7abb6.png",
                          "cd750d835665b98477efd89a73a3d2d1faf2416d7b80e65d7fe0a78599631d6b"),
    ("outskirts", "en"): (_V14C + "outskirts-640-probe-en_unapproved-v14_20261018-084553-cb540bbe.png",
                          "b2595418166a3bb72423005eeb9900fe4d2a78441bb9ea7ba537a95f8df0fafc"),
}
_V15C = V15_DIR + "/rpg-2-star-ocean-the-second_female-battle-idle-right_party-capture-"
V15_CAPS = {   # (png, manifest); hashes are recorded, not pinned, because this tool measures them
    ("archive", "zh"): (_V15C + "archive-640-zh_unapproved-v15_20261018-210446-a586f209.png",
                        _V15C + "archive-640-zh-manifest_unapproved-v15_20261018-210446-3014d9cb.json"),
    ("archive", "en"): (_V15C + "archive-640-en_unapproved-v15_20261018-210446-d7efa712.png",
                        _V15C + "archive-640-en-manifest_unapproved-v15_20261018-210446-9603e004.json"),
    ("outskirts", "zh"): (_V15C + "outskirts-640-zh_unapproved-v15_20261018-210446-b75254f4.png",
                          _V15C + "outskirts-640-zh-manifest_unapproved-v15_20261018-210446-afd13c93.json"),
    ("outskirts", "en"): (_V15C + "outskirts-640-en_unapproved-v15_20261018-210446-ca75b69d.png",
                          _V15C + "outskirts-640-en-manifest_unapproved-v15_20261018-210446-e5dd62df.json"),
}
REGIONS = {"head": (1, 19), "torso": (20, 37), "lower_body": (38, 67), "skirt_legs": (40, 56), "boots": (57, 67),
           "boot_contact": (62, 66)}
BACK = (31, 20, 56)                 # x <= 31, rows 20-56: pack, roll, back tail


def _fs(path):
    path = os.path.abspath(path)
    return "\\\\?\\" + path if os.name == "nt" and len(path) > 247 and not path.startswith("\\\\?\\") else path


def raw(path):
    with open(_fs(path), "rb") as f:
        return f.read()


def repo(rel):
    return os.path.join(REPO, *rel.split("/"))


def pinned(rel, want):
    data = raw(repo(rel))
    if hashlib.sha256(data).hexdigest() != want:
        raise SystemExit(f"hash changed: {rel}")
    return data


def rgba(data):
    return np.array(Image.open(io.BytesIO(data)).convert("RGBA"))


def lum(rgb):
    rgb = np.asarray(rgb, float)
    return 0.2126 * rgb[..., 0] + 0.7152 * rgb[..., 1] + 0.0722 * rgb[..., 2]


def shadow_mask(h, w):
    ty, tx = np.mgrid[0:h, 0:w]
    dx = (ORIGIN[0] + tx + 0.5 - 300.0) / 18.0
    dy = (ORIGIN[1] + ty + 0.5 - 272.0) / (18.0 * 0.28)
    return dx * dx + dy * dy <= 1.0


def composite(sprite, bg):
    out = bg.copy()
    h, w = sprite.shape[:2]
    m = sprite[..., 3] == 255
    out[ORIGIN[1]:ORIGIN[1] + h, ORIGIN[0]:ORIGIN[0] + w][m] = sprite[m]
    return out


def regions(sprite, bg):
    h, w = sprite.shape[:2]
    under = bg[ORIGIN[1]:ORIGIN[1] + h, ORIGIN[0]:ORIGIN[0] + w, :3]
    op = (sprite[..., 3] == 255) & ~(sprite[..., :3] == np.array(OUTLINE)).all(-1)
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
    back = op.copy()
    back[:, BACK[0] + 1:] = False
    back[:BACK[1]] = False
    back[BACK[2] + 1:] = False
    masks["back_x_le_31_rows_20_56"] = back
    out = {}
    for name, m in masks.items():
        d = np.abs(lum(sprite[..., :3][m]) - lum(under[m]))
        out[name] = {"texels": int(m.sum()), "mean_abs_dL": round(float(d.mean()), 1),
                     "share_abs_dL_lt_20": round(float((d < 20).mean()), 3),
                     "sprite_mean_L": round(float(lum(sprite[..., :3][m]).mean()), 1),
                     "background_mean_L": round(float(lum(under[m]).mean()), 1)}
    return out


def main():
    run = sys.argv[1]
    v14 = rgba(pinned(*V14_PNG))
    v15 = rgba(pinned(*V15_PNG))
    alpha_same = bool(np.array_equal(v14[..., 3], v15[..., 3]))
    rep = {"status": "UNAPPROVED, read-only measure; writes nothing",
           "v14_png": {"file": V14_PNG[0], "sha256": V14_PNG[1]}, "v15_png": {"file": V15_PNG[0], "sha256": V15_PNG[1]},
           "sprite_alpha_identical_v14_v15": alpha_same, "runs": {}}
    ok = alpha_same
    for (floor, lang), (v15_rel, man_rel) in V15_CAPS.items():
        tag = f"{floor}-640-{lang}"
        cap15_b = raw(repo(v15_rel))
        man_b = raw(repo(man_rel))
        man = json.loads(man_b)
        cap14 = rgba(pinned(*V14_CAPS[(floor, lang)]))
        ctl_b = raw(os.path.join(run, f"v14ctl_{tag}.png"))
        ns15_b = raw(os.path.join(run, f"ns_v15_{tag}.png"))
        ns14_b = raw(os.path.join(run, f"ns_v14_{tag}.png"))
        cap15, ns15 = rgba(cap15_b), rgba(ns15_b)
        diff = (cap15 != cap14).any(-1)
        inside = np.zeros(diff.shape, bool)
        inside[ORIGIN[1]:ORIGIN[1] + 72, ORIGIN[0]:ORIGIN[0] + 68] = v15[..., 3] == 255
        m = man["measurement"]
        g = {
            "v14_control_capture_equals_tracked_v14_capture": hashlib.sha256(ctl_b).hexdigest() == V14_CAPS[(floor, lang)][1],
            "v15_nosprite_equals_v14_control_nosprite": ns15_b == ns14_b,
            "v15_png_over_nosprite_equals_v15_capture": np.array_equal(composite(v15, ns15), cap15),
            "v15_vs_v14_capture_differs_only_inside_sprite_alpha": bool(not (diff & ~inside).any()),
            "manifest_capture_sha_matches_file": man["captureSha256"] == hashlib.sha256(cap15_b).hexdigest(),
            "manifest_candidate_is_v15": man["candidateSha256"] == V15_PNG[1],
            "sprite_pixels_1590_of_1590": m["spritePixels"] == 1590 and m["expectedSpritePixels"] == 1590,
            "off_palette_0_nearest_1": m["offPaletteSpritePixels"] == 0 and m["nearestPredictionMatchRatio"] == 1.0,
            "crown_y211_sole_y271_bbox_283_328": m["crownScreenY"] == 211 and m["soleScreenYInclusive"] == 271
            and m["spriteBBoxScreen"]["left"] == 283 and m["spriteBBoxScreen"]["rightInclusive"] == 328,
            "no_opaque_overlap_with_companions": all(c["opaqueOnOpaqueScreenPx"] == 0
                                                     for c in m["companionOverlap"].values()),
            "hud_language": man.get("language") == lang,
        }
        ok = ok and all(g.values())
        rep["runs"][tag] = {
            "v15_capture": {"file": v15_rel, "sha256": hashlib.sha256(cap15_b).hexdigest()},
            "v15_manifest": {"file": man_rel, "sha256_bytes": hashlib.sha256(man_b).hexdigest()},
            "nosprite_v15_sha256": hashlib.sha256(ns15_b).hexdigest(),
            "v14_control_capture_sha256": hashlib.sha256(ctl_b).hexdigest(),
            "changed_screen_px_v14_to_v15": int(diff.sum()),
            "gates": g,
            "descriptive_regions_v14": regions(v14, ns15), "descriptive_regions_v15": regions(v15, ns15),
        }
    rep["result"] = "PASS" if ok else "FAIL"
    print(json.dumps(rep, indent=1, ensure_ascii=False))
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
