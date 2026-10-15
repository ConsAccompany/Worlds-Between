"""Female protagonist south idle, selout v5 static refinement (M8 v05), one frame.

Technical candidate only; unapproved; not used by the game runtime. No animation.
Input is the selout v4 candidate PNG (read-only, source-locked by SHA-256). Output is ONE
new PNG made by an explicit, hand-authored texel edit map over v4 - not a resize.

v4 restated the torso; v5 continues below the belt and trims the hair mass (light from the
upper left, same palette, no new colours):
  lower body y57-73  coat skirts restated as darker cloth (b shadow / n base / m light)
                     with tan front-edge trims 'r' running diagonally down each skirt,
                     the right skirt's inner lining as one 'L' strip beside its trim;
                     trouser legs as three-tone cylinders (w lit left / m / b shadow
                     right) with the crotch shadow kept; the left-thigh strap restated as a
                     dark strap band with a muted 2x3 buckle and one metal glint (was cream
                     specks; revision 2 toned the buckle down after the first preview); the left
                     hip pouch kept as a small leather block (L/l/r, x25-26 y59-62).
                     Darker skirts give the lower half more contrast against warm paving.
  belt stack         the hip belt drops from 2 rows to 1 (y57, buckle kept); y58 becomes
                     shirt shadow / coat, so main belt + hip belt + tails read lighter.
  ponytail y16-33    the viewer-left fall loses one texel of outer width (rows 16-28) and
                     ends two rows higher (tip at y31 instead of y33); the crease, the
                     highlight path, the inner edge and the negative-space gap are kept.
  left cuff y47-53   toned down: cream base 'c' with one 'C' highlight, dark 'w' outer edge,
                     inner skin s/D instead of S, so it no longer outshines the face; one
                     fist texel (26,42) S -> s for the same reason.
Kept byte-identical to v4 (asserted): rows y8-14 (tuft, tie, crown); head, face and side lock
(y15-33, x>=25); every teal texel (scarf, scarf tail, badge, bedroll); the torso y34-53
outside the cuff box and the fist texel; canister; the viewer-right forearm, glove and
fingers (x47-52 y57-70); and everything from y=74 down (knee guard, boots, buckles).
Alpha may change only in the ponytail fall box (x13-24, y15-33).

Run with the Codex-runtime Python (Pillow 12.3.0, NumPy 2.3.5), isolated mode:
  python -I <this script>                        # write PNG + manifest (refuses to change existing PNG bytes)
  python -I <this script> --out-dir <dir>        # determinism re-check into another folder
  python -I <this script> --qa-report <json>     # also embed Godot capture hashes in the manifest
  python -I <this script> --dump SRC|V5 x0 y0 x1 y1   # print a texel role map (review aid)
  python -I <this script> --preview <png> [--scale N] # v5 only, nearest-neighbour enlarged (review aid)
"""

import argparse
import hashlib
import json
import platform
import sys
from pathlib import Path

import numpy as np
import PIL
from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
PILOT_DIR = ROOT / "game/assets/characters/pixelorama-pilots"
SOURCE = PILOT_DIR / "rpg-2-star-ocean-the-second_protagonist-female_south-idle-selout-v4-structural-candidate_m8-v04_20261015-001500-e5b81f36.png"
SOURCE_SHA256 = "da8a1ce11db136f7061206a3d8f5038b7d995016e36af2fc011d0a6f0dbcf4d7"
PRESERVED = {
    "v3": (PILOT_DIR / "rpg-2-star-ocean-the-second_protagonist-female_south-idle-selout-v3-polish-candidate_m8-v03_20261014-234700-3c9a5d27.png",
           "21b148cc026a70cdb173200c46cf007f83e4963cd7b7a7c71a174a7cb343cbc3"),
    "v2": (PILOT_DIR / "rpg-2-star-ocean-the-second_protagonist-female_south-idle-selout-v2-polish-candidate_m8-v02_20261014-233300-d2eeefa2.png",
           "4c8a720adc93c2bdbf2039da929f96eb617d4829ab35da2333105ac7d870e6f5"),
    "v1": (PILOT_DIR / "rpg-2-star-ocean-the-second_protagonist-female_south-idle-refine-selout-candidate_m8-v01_20261014-231100-4d141ad5.png",
           "7cb9f7044ed728894ab613725f0c6bdd876c29527e505b7f061689112da37f88"),
}
RUN = "m8-v05_20261015-004000"
OUTPUT = f"rpg-2-star-ocean-the-second_protagonist-female_south-idle-selout-v5-lowerbody-hair-candidate_{RUN}-8b3e5c07.png"
MANIFEST = f"rpg-2-star-ocean-the-second_protagonist-female_south-idle-selout-v5-lowerbody-hair-manifest_{RUN}-f41a7d92.json"

MAX_COLOURS = 32
CELL = (80, 112)
PIN = (40, 104)
FEET_ROWS = 6
ALPHA_EDIT_BOX = (13, 15, 25, 34)  # x0, y0, x1, y1 exclusive: the ponytail fall only

# Role letters -> RGB hex. All are existing v4 colours (no new colours in v5).
ROLES = [
    ("K", "0a0a0e"), ("k", "201c20"), ("O", "23252b"), ("T", "0a323b"), ("q", "302526"), ("G", "30333a"),
    ("b", "41302b"), ("t", "11525b"), ("n", "533b32"), ("y", "4a4749"), ("g", "474b54"), ("m", "634739"),
    ("L", "714730"), ("u", "1a767b"), ("l", "845436"), ("w", "7e5f4a"), ("z", "626873"), ("v", "249b98"),
    ("r", "a16f4b"), ("D", "bb7c50"), ("c", "b09986"), ("s", "e39664"), ("C", "d7c0a8"), ("B", "cfc8bd"),
    ("S", "fbc38d"), ("W", "faead4"), ("M", "9a4634"),
]
TEAL = {"T", "t", "u", "v"}

# (row, first column, map): '.' keeps the v4 texel, '_' makes it transparent, else a role.
EDITS = {
    # Ponytail fall (x13-24): outer outline moves in one column for rows 16-24 (x14/15 ->
    # x15/16) and rows 25-28; the outer lock keeps its sheen 'l'/'m' one texel inside the
    # edge and the crease ('b'/'k' at x18-19) is unchanged; the inner lock narrows from y27
    # and the tip now ends at y31 (x18) - rows 32-33 cleared. Inner edge and gap unchanged
    # down to y26.
    "ponytail_fall": [
        (16, 13, "___Klnbnmnqk"),
        (17, 13, "___Klbnmnqkq"),
        (18, 13, "__Kllbnmnqkb"),
        (19, 13, "__KmnknnqKKb"),
        (20, 13, "__KlnknnqqKK"),
        (21, 13, "__KlnknmqqK_"),
        (22, 13, "__KlnknmmqK_"),
        (23, 13, "__KmlknnmqK_"),
        (24, 13, "__KmnknqqK__"),
        (25, 13, "___KlknnqK__"),
        (26, 13, "___KlknnqK__"),
        (27, 13, "___KmkqqK___"),
        (28, 13, "___KmkK_____"),
        (29, 13, "____KlK_____"),
        (30, 13, "____KmK_____"),
        (31, 13, "_____K______"),
        (32, 13, "____________"),
        (33, 13, "____________"),
    ],
    # Left cuff ring and the skin inside it, toned down (same shape and outline).
    "left_cuff": [
        (47, 19, "cCCcw"),
        (48, 18, "cCDsscw"),
        (49, 18, "wcsssDc"),
        (50, 19, "cDsDcw"),
        (51, 19, "ccDccw"),
        (52, 20, "wcccw"),
        (53, 21, "www"),
    ],
    "fist_highlight": [
        (42, 26, "s"),
    ],
    # Hip belt reduced to one row (y57: L band, 2x1 metal buckle at x33-34); right coat
    # below the arm shaded n/b instead of lit w.
    "hip_belt": [
        (57, 25, "LLLLLLLLBBLLLLLL"),
        (57, 41, "wmnnnb"),
    ],
    # Below the belts, x21-48. Left: coat skirt b/n/m with a tan front-edge trim 'r' moving
    # from x29 (y61) to x26 (y64-70) and the hem outline kept at x24-25 y70; leather hip
    # pouch x25-26 y59-62. Shirt tails as v4 but starting from a shadow row at y58. Left leg
    # x27-34: m edge, w lit x28-30, m, b shadow x33-34. Crotch shadow b / kept ink. Right leg
    # x37-44: m inner seam, w lit x38-41, m, b; lining 'L' beside the right skirt trim 'r',
    # which runs x43 (y61-63) -> x44 (y64-65) -> x45 (y66) -> x46 (y67-68) -> x47 (y69-71).
    # Left-thigh strap y72: dark L band with a 2x3 buckle (K hole at (31,72)). Revision 2
    # (after the first --preview): the buckle frame is muted cream-dark 'c' with a single
    # metal glint 'B' at (31,71), so it no longer competes with the knee-guard buckle below.
    "lower_body": [
        (58, 25, "bnnmwccccbbcccccwmnnnb"),
        (59, 25, "LLnmwcCWCbbCCCccwmnnnb"),
        (60, 25, "lrnmwcCCcbbCWCccwmnnnb"),
        (61, 25, "llnmrccmmbbmcCCcwmrnnb"),
        (62, 25, "LLnrwwwmbbbbccccmmrnnb"),
        (63, 23, "bnnmrwwwmmbbbbmwwwmmrnnb"),
        (64, 23, "bnmrmwwwmmbbbbmwwwmbLrnb"),
        (65, 23, "bnmrmwwwmmbbbbmwwwmbLrnb"),
        (66, 22, "bnnmrmwwwmmbbKbmwwwmmbLrb"),
        (67, 21, "bbnnmrmmwwwmbb..mwwwmmbLnr"),
        (68, 22, "bnnmrmmwwwmb...mmwwwmbLnr"),
        (69, 22, "bnnmrmmwwwmb...mwwwwmmbLnr"),
        (70, 21, "bbbKKrmwwwmmbK..KwwwmmbbLnr"),
        (71, 26, "bmwwcBmbb...mwwwwmbLnrr"),
        (72, 27, "KLLcKLLk...bwwwwmbLb"),
        (73, 27, "Kmwccmbb...Kwwwwmbbb"),
    ],
}
SPECKLE_BOXES = {
    "lower_body_x21_47_y57_73": (21, 57, 48, 74),
    "left_leg_x26_34_y62_73": (26, 62, 35, 74),
    "right_leg_x37_46_y62_73": (37, 62, 47, 74),
    "left_cuff_x18_24_y47_53": (18, 47, 25, 54),
    "ponytail_fall_x13_24_y15_33": (14, 15, 25, 34),
}
CUFF_BOX = (18, 47, 25, 54)

N4 = [(-1, 0), (1, 0), (0, -1), (0, 1)]
N8 = N4 + [(-1, -1), (-1, 1), (1, -1), (1, 1)]


def sha256(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def hex_rgb(h):
    return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))


def role_of(px):
    if px[3] == 0:
        return "."
    key = "%02x%02x%02x" % tuple(int(v) for v in px[:3])
    for ch, h in ROLES:
        if h == key:
            return ch
    return "?"


def in_box(x, y, box):
    return box[0] <= x < box[2] and box[1] <= y < box[3]


def apply_edits(src):
    out = src.copy()
    owner = {}
    rmap = dict(ROLES)
    for region, rows in EDITS.items():
        for y, x0, spec in rows:
            for i, ch in enumerate(spec):
                x = x0 + i
                if ch == ".":
                    continue
                if (x, y) in owner:
                    sys.exit(f"texel {(x, y)} edited by both {owner[(x, y)]} and {region}")
                if ch != "_" and ch not in rmap:
                    sys.exit(f"unknown role {ch!r} at {(x, y)} in {region}")
                if not in_box(x, y, ALPHA_EDIT_BOX) and (ch == "_" or src[y, x, 3] != 255):
                    sys.exit(f"edit at {(x, y)} in {region} would change alpha outside the ponytail box {ALPHA_EDIT_BOX}")
                owner[(x, y)] = region
                out[y, x] = (0, 0, 0, 0) if ch == "_" else hex_rgb(rmap[ch]) + (255,)
    return out, owner


def feet_anchor(op):
    rows = np.where(op.any(1))[0]
    bottom = int(rows.max())
    cols = np.where(op[bottom - FEET_ROWS + 1: bottom + 1].any(0))[0]
    return bottom, (int(cols.min()) + int(cols.max()) + 1) // 2


def speckle(img, box):
    """Opaque texels in box whose RGB matches none of their opaque 8-neighbours."""
    x0, y0, x1, y1 = box
    op = img[..., 3] == 255
    n = tot = 0
    for y in range(y0, y1):
        for x in range(x0, x1):
            if not op[y, x]:
                continue
            tot += 1
            if not any(op[y + dy, x + dx] and (img[y + dy, x + dx, :3] == img[y, x, :3]).all() for dy, dx in N8):
                n += 1
    return {"box_xyxy_exclusive": list(box), "opaque": tot, "speckle": n, "share": round(n / tot, 4) if tot else None}


def checks(src, out):
    a = out[..., 3]
    op = a == 255
    ys, xs = np.where(op)
    colours = sorted({tuple(int(v) for v in c) for c in out[op][:, :3]})
    isolated = [(int(x), int(y)) for y, x in zip(ys, xs)
                if not any(0 <= y + dy < op.shape[0] and 0 <= x + dx < op.shape[1] and op[y + dy, x + dx] for dy, dx in N8)]
    pinholes = [(x, y) for y in range(1, op.shape[0] - 1) for x in range(1, op.shape[1] - 1)
                if not op[y, x] and all(op[y + dy, x + dx] for dy, dx in N4)]
    return {
        "size": [out.shape[1], out.shape[0]],
        "alpha_values_present": sorted(int(v) for v in np.unique(a)),
        "partial_alpha_texels": int(((a > 0) & (a < 255)).sum()),
        "transparent_texels_with_nonzero_rgb": int(((a == 0) & out[..., :3].any(-1)).sum()),
        "opaque_texels": int(op.sum()),
        "unique_opaque_rgb_colours": len(colours),
        "palette_hex": ["#%02x%02x%02x" % c for c in colours],
        "alpha_bounds_inclusive_xyxy": [int(xs.min()), int(ys.min()), int(xs.max()), int(ys.max())],
        "visible_body_height_texels": int(ys.max() - ys.min() + 1),
        "visible_body_width_texels": int(xs.max() - xs.min() + 1),
        "opaque_texels_on_cell_border": int(op[0].sum() + op[-1].sum() + op[:, 0].sum() + op[:, -1].sum()),
        "foot_anchor_lowest_row_and_feet_mid_x": list(feet_anchor(op)),
        "foot_anchor_source": list(feet_anchor(src[..., 3] == 255)),
        "isolated_opaque_texels_8n": isolated,
        "transparent_pinholes_4n": pinholes,
    }


def protected(src, out):
    """Named invariants that must all be True."""
    teal = np.array([[role_of(src[y, x]) in TEAL for x in range(CELL[0])] for y in range(CELL[1])])
    torso_keep = np.ones((20, CELL[0]), bool)  # rows 34-53
    cx0, cy0, cx1, cy1 = CUFF_BOX
    torso_keep[cy0 - 34:cy1 - 34, cx0:cx1] = False
    torso_keep[42 - 34, 26] = False
    alpha_keep = np.ones(CELL[::-1], bool)
    ax0, ay0, ax1, ay1 = ALPHA_EDIT_BOX
    alpha_keep[ay0:ay1, ax0:ax1] = False
    return {
        "rows_8_14_tuft_tie_crown_identical": bool((out[8:15] == src[8:15]).all()),
        "head_face_sidelock_y15_33_x25plus_identical": bool((out[15:34, 25:] == src[15:34, 25:]).all()),
        "teal_texels_identical": bool((out[teal] == src[teal]).all()),
        "torso_y34_53_identical_except_cuff_and_fist_texel": bool((out[34:54][torso_keep] == src[34:54][torso_keep]).all()),
        "right_forearm_glove_fingers_x47_52_y57_70_identical": bool((out[57:71, 47:53] == src[57:71, 47:53]).all()),
        "rows_74_and_below_identical": bool((out[74:] == src[74:]).all()),
        "alpha_identical_outside_ponytail_box": bool((out[..., 3][alpha_keep] == src[..., 3][alpha_keep]).all()),
    }


def dump(img, x0, y0, x1, y1):
    print("    " + "".join(str(x // 10 % 10) for x in range(x0, x1)))
    print("    " + "".join(str(x % 10) for x in range(x0, x1)))
    for y in range(y0, y1):
        print("%3d " % y + "".join(role_of(img[y, x]) for x in range(x0, x1)))


def preview(out, path, scale):
    """v5 alone, nearest-neighbour enlarged on neutral grey (review aid; not a sheet)."""
    im = Image.fromarray(out, "RGBA").resize((CELL[0] * scale, CELL[1] * scale), Image.NEAREST)
    bg = Image.new("RGBA", im.size, (150, 150, 150, 255))
    bg.alpha_composite(im)
    bg.save(path)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out-dir", type=Path, default=PILOT_DIR)
    ap.add_argument("--qa-report", type=Path)
    ap.add_argument("--dump", nargs=5)
    ap.add_argument("--preview", type=Path)
    ap.add_argument("--scale", type=int, default=8)
    args = ap.parse_args()
    if sha256(SOURCE) != SOURCE_SHA256:
        sys.exit("v4 source SHA-256 mismatch")
    for name, (p, h) in PRESERVED.items():
        if sha256(p) != h:
            sys.exit(f"{name} SHA-256 mismatch (must stay preserved)")
    src = np.array(Image.open(SOURCE).convert("RGBA"))
    if args.dump and args.dump[0] == "SRC":
        dump(src, *map(int, args.dump[1:]))
        return
    out, owner = apply_edits(src)
    if args.dump:
        dump(out, *map(int, args.dump[1:]))
        return
    m = checks(src, out)
    prot = protected(src, out)
    ok = (m["size"] == list(CELL) and m["alpha_values_present"] == [0, 255] and m["partial_alpha_texels"] == 0
          and m["transparent_texels_with_nonzero_rgb"] == 0 and m["visible_body_height_texels"] == 96
          and m["alpha_bounds_inclusive_xyxy"][1] == 8 and m["alpha_bounds_inclusive_xyxy"][3] == 103
          and m["unique_opaque_rgb_colours"] <= MAX_COLOURS and m["opaque_texels_on_cell_border"] == 0
          and m["foot_anchor_lowest_row_and_feet_mid_x"] == m["foot_anchor_source"] == [PIN[1] - 1, PIN[0]]
          and not m["isolated_opaque_texels_8n"] and not m["transparent_pinholes_4n"] and all(prot.values()))
    if not ok:
        print(json.dumps({"checks": {k: v for k, v in m.items() if k != "palette_hex"}, "protected": prot}, indent=1))
        sys.exit("integrity check failed")
    if args.preview:
        preview(out, args.preview, args.scale)
        print("PREVIEW", args.preview)
        return
    args.out_dir.mkdir(parents=True, exist_ok=True)
    path = args.out_dir / OUTPUT
    tmp = path.with_suffix(".tmp.png")
    Image.fromarray(out, "RGBA").save(tmp, optimize=False, compress_level=9)
    if path.exists() and path.read_bytes() != tmp.read_bytes():
        tmp.unlink()
        sys.exit(f"refusing to change existing bytes of {path.name}")
    tmp.replace(path)
    if sha256(SOURCE) != SOURCE_SHA256 or any(sha256(p) != h for p, h in PRESERVED.values()):
        sys.exit("a preserved source changed")
    fmt = lambda p: "transparent" if p[3] == 0 else "#%02x%02x%02x" % tuple(int(v) for v in p[:3])
    changes = [{"x": int(x), "y": int(y), "region": owner[(int(x), int(y))], "before": fmt(src[y, x]), "after": fmt(out[y, x])}
               for y, x in zip(*np.where((out != src).any(-1)))]
    per_region = {}
    for c in changes:
        per_region[c["region"]] = per_region.get(c["region"], 0) + 1
    speck = {name: {"v4": speckle(src, box), "v5": speckle(out, box)} for name, box in SPECKLE_BOXES.items()}
    qa = None
    if args.qa_report:
        rep = json.loads(args.qa_report.read_text(encoding="utf-8"))
        qa = {"report": args.qa_report.name, "report_sha256": sha256(args.qa_report),
              "captures": [{k: c.get(k) for k in ("scene", "variant", "capture", "capture_sha256", "capture_size",
                                                  "pilot_visible_logical", "pilot_window_diff_bounds_measured", "pilot_texel_fidelity")}
                           for c in rep["captures"]]}
    manifest = {
        "project": "Worlds Between",
        "milestone": "M8",
        "purpose": "Selout v5 static refinement of the female south idle: lower body and coat skirts restated as three-tone shapes, lighter belt stack, slimmer/shorter ponytail fall, toned-down left cuff. Static frame only.",
        "status": "technical candidate; unapproved; not runtime-integrated; no animation",
        "art_approved": False,
        "human_reviewed": False,
        "runtime_integrated": False,
        "walk_frames": 0,
        "authorship": "Edit map authored by Claude with file edits only (no execution); the script is run by Codex in the workspace.",
        "source": {"role": "read-only input (selout v4), source-locked", "file": str(SOURCE.relative_to(ROOT)).replace("\\", "/"),
                   "sha256": SOURCE_SHA256,
                   "also_preserved": {k: {"file": str(p.relative_to(ROOT)).replace("\\", "/"), "sha256": h} for k, (p, h) in PRESERVED.items()}},
        "editor": {"script": "tools/" + Path(__file__).name, "script_sha256": sha256(__file__),
                   "python": platform.python_version(), "pillow": PIL.__version__, "numpy": np.__version__,
                   "run_flags": "-I (isolated)",
                   "method": "explicit texel map (EDITS) over v4; alpha edits only in the ponytail fall box; no resampling, quantizing, filtering or AI editing"},
        "roles": {ch: "#" + h for ch, h in ROLES},
        "new_colours": [],
        "edit_map": {region: [{"row": y, "x0": x0, "map": spec} for y, x0, spec in rows] for region, rows in EDITS.items()},
        "output": {"file": OUTPUT, "format": "PNG RGBA 8-bit, single image, no metadata chunks",
                   "bytes": path.stat().st_size, "sha256": sha256(path), "measured": m},
        "protected_invariants": prot,
        "speckle_v4_vs_v5": speck,
        "pixel_changes": {"total": len(changes), "per_region": per_region, "texels": changes},
        "qa_captures": qa,
        "limitations": [
            "Static south idle only; no walk/turn frames; nothing wired into the runtime.",
            "The map was authored from texel reconstructions without Claude seeing the v5 result; it needs a --preview read and Godot captures, and likely one more revision.",
            "Lower-body shapes are a stylised re-statement of the reference (diagonal skirt trims, one lining strip, one thigh-strap buckle, simplified pouch); stitching and extra straps are not drawn.",
            "The coat skirt behind the viewer-right hand (x48-52 y70-75) and both lower legs from y74 (knee guard, boots) are unchanged v4 texture.",
            "The ponytail fall is one texel slimmer and two rows shorter; the tuft fan, tie and crown above y15 are unchanged, so the hair is still the largest single shape.",
            "The hip belt is now one row; its buckle is a 2x1 metal mark rather than a 2x2 ring.",
            "Visual approval remains human.",
        ],
    }
    (args.out_dir / MANIFEST).write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    print(f"PNG {path} sha256={sha256(path)}")
    print(f"  size={m['size']} h={m['visible_body_height_texels']} w={m['visible_body_width_texels']} alpha={m['alpha_values_present']} "
          f"colours={m['unique_opaque_rgb_colours']} anchor={m['foot_anchor_lowest_row_and_feet_mid_x']} opaque={m['opaque_texels']}")
    print(f"  protected={prot}")
    print(f"  changes={len(changes)} per_region={per_region}")
    for name, s in speck.items():
        print(f"  speckle {name}: v4 {s['v4']['speckle']}/{s['v4']['opaque']} -> v5 {s['v5']['speckle']}/{s['v5']['opaque']}")
    print(f"MANIFEST {args.out_dir / MANIFEST}")


if __name__ == "__main__":
    main()
