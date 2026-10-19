"""UNAPPROVED, read-only measure of the female battle static v16 party captures against v15 (writes nothing; JSON to stdout).

Context labels: every capture is the FROZEN 160b823 reference context drawn by the unchanged v14 probe script (sha256
720c8377...): its arena bands and radius-18 contact shadow are test-presentation context re-drawn by an in-memory probe
subclass, NOT proof that current main draws them by default, and NOT a claim that v16 is runtime / default integrated.

Inputs: the locked v15 PNG and its four root-reviewed 640x360 captures (archive / outskirts x zh / en, in
outputs/battle-static-v15), the v16 PNG and its four captures + manifests in outputs/battle-static-v16, and the run
directory holding the no-sprite frames of the v16 runs and of the v15 control runs made in the SAME isolated 160b823 tree
(ns_v16_<floor>-640-<lang>.png, ns_v15_<floor>-640-<lang>.png, v15ctl_<floor>-640-<lang>.png). Checks, per floor x
language:
  1. environment: the v15 control capture equals the root-reviewed v15 capture byte for byte, and the v16 run's
     no-sprite frame equals the v15 control run's (so the only difference between v15 and v16 captures is the sprite)
  2. fidelity: the v16 PNG composited at texture origin (268, 204) over the v16 no-sprite frame equals the v16 capture;
     the v16 capture differs from the v15 capture only inside the sprite's alpha
  3. probe manifest fields: sprite pixels 1590/1590, 0 off-palette, nearest match 1.0, crown y 211, sole y 271, bbox
     283-328, 0 opaque overlap with every companion, HUD language
  4. DESCRIPTIVE ONLY (not gated, no thresholds, not a success criterion): per region the mean |dL| (Rec.709 luma) of
     sprite texels against the floor pixels they cover and the share with |dL| < 20 (outline excluded), for v15 and
     v16 on the identical frame. A number does not decide whether the boots read; the root judges the images.

Run: python -I -B <this file> <run dir>
"""
import hashlib, io, json, os, sys
import numpy as np
from PIL import Image

REPO = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
ORIGIN = (268, 204)
OUTLINE = (0x16, 0x14, 0x1A)
_P = "rpg-2-star-ocean-the-second_female-battle-idle-right_"
V15_DIR = "outputs/battle-static-v15"
V16_DIR = "outputs/battle-static-v16"
V15_PNG = (V15_DIR + "/" + _P + "static-native0p65_unapproved-v15_20261018-210446-abde2095.png",
           "c6aca9b804d1fd83c284c1491cbeb347190d2528d8f05c460e1e055800e1f4e2")
V16_PNG = (V16_DIR + "/" + _P + "static-native0p65_unapproved-v16_20261018-212808-e75685af.png",
           "ce6d294c23f89556e3822470966704ef68534d4deb69500a03d47f63ca79b768")
_V15C = V15_DIR + "/" + _P + "party-capture-"
V15_CAPS = {
    ("archive", "zh"): (_V15C + "archive-640-zh_unapproved-v15_20261018-210446-a586f209.png",
                        "e4357f367dd76f97cf2c106f5c4bbe29429dfa914e71500a88d73e1f33cd4d79"),
    ("archive", "en"): (_V15C + "archive-640-en_unapproved-v15_20261018-210446-d7efa712.png",
                        "f7087453537999f1297b53e4d8ddf61f67014e3e27570ef60610dd3c9e2ecc7e"),
    ("outskirts", "zh"): (_V15C + "outskirts-640-zh_unapproved-v15_20261018-210446-b75254f4.png",
                          "cde3cc16a63ad3436c3a20919f20d8dd4c1e4504500236ef261eebf5909cbda5"),
    ("outskirts", "en"): (_V15C + "outskirts-640-en_unapproved-v15_20261018-210446-ca75b69d.png",
                          "0a447c471addbd902090ca37dc8c14514b1b282f2248b1fb05b2612029d5e2d0"),
}
_V16C = V16_DIR + "/" + _P + "cap-ref160b823-"
V16_CAPS = {   # (png, manifest); hashes are recorded, not pinned, because this tool measures them
    ("archive", "zh"): (_V16C + "archive-640-zh_unapproved-v16_20261018-212808-111b8e75.png",
                        _V16C + "archive-640-zh-manifest_unapproved-v16_20261018-212808-9b33c431.json"),
    ("archive", "en"): (_V16C + "archive-640-en_unapproved-v16_20261018-212808-018e4300.png",
                        _V16C + "archive-640-en-manifest_unapproved-v16_20261018-212808-46b1b1d5.json"),
    ("outskirts", "zh"): (_V16C + "outskirts-640-zh_unapproved-v16_20261018-212808-82ac83e8.png",
                          _V16C + "outskirts-640-zh-manifest_unapproved-v16_20261018-212808-fc6c8d23.json"),
    ("outskirts", "en"): (_V16C + "outskirts-640-en_unapproved-v16_20261018-212808-e3d6352b.png",
                          _V16C + "outskirts-640-en-manifest_unapproved-v16_20261018-212808-cb9bb113.json"),
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
    v15 = rgba(pinned(*V15_PNG))
    v16 = rgba(pinned(*V16_PNG))
    alpha_same = bool(np.array_equal(v15[..., 3], v16[..., 3]))
    rep = {"status": "UNAPPROVED, read-only measure; writes nothing",
           "context": "frozen 160b823 tree + unchanged v14 probe; bands and radius-18 contact shadow are test-presentation "
                      "context, not current-main default art and not a runtime-integration claim",
           "v15_png": {"file": V15_PNG[0], "sha256": V15_PNG[1]}, "v16_png": {"file": V16_PNG[0], "sha256": V16_PNG[1]},
           "sprite_alpha_identical_v15_v16": alpha_same, "runs": {}}
    ok = alpha_same
    for (floor, lang), (v16_rel, man_rel) in V16_CAPS.items():
        tag = f"{floor}-640-{lang}"
        cap16_b = raw(repo(v16_rel))
        man_b = raw(repo(man_rel))
        man = json.loads(man_b)
        cap15 = rgba(pinned(*V15_CAPS[(floor, lang)]))
        ctl_b = raw(os.path.join(run, f"v15ctl_{tag}.png"))
        ns16_b = raw(os.path.join(run, f"ns_v16_{tag}.png"))
        ns15_b = raw(os.path.join(run, f"ns_v15_{tag}.png"))
        cap16, ns16 = rgba(cap16_b), rgba(ns16_b)
        diff = (cap16 != cap15).any(-1)
        inside = np.zeros(diff.shape, bool)
        inside[ORIGIN[1]:ORIGIN[1] + 72, ORIGIN[0]:ORIGIN[0] + 68] = v16[..., 3] == 255
        m = man["measurement"]
        g = {
            "v15_control_capture_equals_root_reviewed_v15_capture":
                hashlib.sha256(ctl_b).hexdigest() == V15_CAPS[(floor, lang)][1],
            "v16_nosprite_equals_v15_control_nosprite": ns16_b == ns15_b,
            "v16_png_over_nosprite_equals_v16_capture": np.array_equal(composite(v16, ns16), cap16),
            "v16_vs_v15_capture_differs_only_inside_sprite_alpha": bool(not (diff & ~inside).any()),
            "manifest_capture_sha_matches_file": man["captureSha256"] == hashlib.sha256(cap16_b).hexdigest(),
            "manifest_candidate_is_v16": man["candidateSha256"] == V16_PNG[1],
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
            "v16_capture": {"file": v16_rel, "sha256": hashlib.sha256(cap16_b).hexdigest()},
            "v16_manifest": {"file": man_rel, "sha256_bytes": hashlib.sha256(man_b).hexdigest()},
            "nosprite_v16_sha256": hashlib.sha256(ns16_b).hexdigest(),
            "v15_control_capture_sha256": hashlib.sha256(ctl_b).hexdigest(),
            "changed_screen_px_v15_to_v16": int(diff.sum()),
            "gates": g,
            "descriptive_only_regions_v15": regions(v15, ns16), "descriptive_only_regions_v16": regions(v16, ns16),
        }
    rep["result"] = "PASS" if ok else "FAIL"
    print(json.dumps(rep, indent=1, ensure_ascii=False))
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
