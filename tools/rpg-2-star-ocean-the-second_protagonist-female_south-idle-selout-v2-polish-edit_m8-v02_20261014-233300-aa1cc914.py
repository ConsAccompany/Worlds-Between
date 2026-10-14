"""Female protagonist south idle, selout v2 static polish (M8 v02), single frame.

Technical candidate only; unapproved; not used by the game runtime. No animation.
Input is the selout v1 candidate PNG (read-only, byte-preserved). Output is ONE new PNG
made by an explicit, hand-authored texel edit map applied on top of selout v1 - not a
new downscale. Every changed texel is listed in the manifest.

Edit regions (cell coordinates, 80x112 cell; body occupies x 13..55, y 8..103):
  ponytail   rows  8-33, x 13-41  tuft -> fall as one arc split by a crease into a long outer
                                  lock (warm highlight path r/l/m 1 texel inside the outer edge)
                                  and a shorter inner lock; forked tapered tip; transparent
                                  1-2 texel gap between the fall and the head's side lock
  face       rows 22-35, x 31-40  level 2x3 eyes (lash with outer flick / white + pupil /
                                  lid + iris), nose shadow, 2-texel closed smile (skin shadow + new mouth colour), blush,
                                  jaw/chin outline, neck shadow;
                                  the noisy ear/cheek blob is replaced by the side lock
  scarf      rows 34-44, x 29-40  darkest-teal (#0a323b) edge against the coat, clean
                                  bandana triangle, light-teal fold highlight
  hands      rows 40-53, x 18-28  viewer-left gloved fist outlined, cuff ring cleaned
             rows 57-70, x 47-53  viewer-right forearm/glove/fingers outlined against coat
Untouched: everything at y >= 72 (knee guard, legs, boots, buckles) and every texel the
maps mark '.'.

Run with the Codex-runtime Python (Pillow 12.3.0, NumPy 2.3.5), isolated mode:
  python -I <this script>                  # write PNG + manifest (refuses to change existing PNG bytes)
  python -I <this script> --out-dir <tmp>  # determinism re-check into another folder
  python -I <this script> --qa-report <json>  # also embed Godot capture hashes in the manifest
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
SOURCE = PILOT_DIR / "rpg-2-star-ocean-the-second_protagonist-female_south-idle-refine-selout-candidate_m8-v01_20261014-231100-4d141ad5.png"
SOURCE_SHA256 = "7cb9f7044ed728894ab613725f0c6bdd876c29527e505b7f061689112da37f88"
RUN = "m8-v02_20261014-233300"
OUTPUT = f"rpg-2-star-ocean-the-second_protagonist-female_south-idle-selout-v2-polish-candidate_{RUN}-d2eeefa2.png"
MANIFEST = f"rpg-2-star-ocean-the-second_protagonist-female_south-idle-selout-v2-polish-manifest_{RUN}-d4a8a850.json"

MAX_COLOURS = 32
CELL = (80, 112)
PIN = (40, 104)
FEET_ROWS = 6
PROTECTED_FROM_ROW = 72  # knee guard (y 74-79), legs, boots and buckles must stay byte-identical

# Roles. All but 'M' are existing selout v1 colours; 'M' (mouth) is the only new colour.
ROLES = {
    "K": "0a0a0e",  # ink outline
    "k": "201c20",  # deepest hair/glove shadow
    "q": "302526",  # dark hair
    "b": "41302b",  # hair dark-mid / coat darkest
    "n": "533b32",  # hair mid
    "m": "634739",  # hair light-mid / coat
    "w": "7e5f4a",  # coat light
    "L": "714730",  # iris / tie shadow
    "l": "845436",  # warm highlight (hair path), strap
    "r": "a16f4b",  # bright warm highlight (hair path top), tie
    "D": "bb7c50",  # skin shadow
    "s": "e39664",  # skin mid
    "S": "fbc38d",  # skin light
    "W": "faead4",  # eye white / cuff light
    "C": "d7c0a8",  # cuff mid
    "c": "b09986",  # cuff dark
    "T": "0a323b",  # scarf edge (darkest teal)
    "t": "11525b",  # scarf shade
    "u": "1a767b",  # scarf mid
    "v": "249b98",  # scarf fold highlight
    "M": "9a4634",  # mouth (new)
}

# (row, first column, map). '.' keeps the selout v1 texel, '_' makes it transparent,
# any other character is a role above. Rows are listed top to bottom per region.
EDITS = {
    "ponytail_and_head": [
        (8, 13, "___________KK_____"),
        (9, 13, "_________KKlnK_K__"),
        (10, 13, "________KlrnbnKnK_"),
        (11, 13, "_______KlrnbmnbnK_"),
        (12, 13, "______KlrnbnmnnqnK"),
        (13, 13, "_____KlnnbnmnnqnqKKKKK_"),
        (14, 13, "____KmnnbnmnnqnqLrnmmnKK_"),
        (15, 13, "___KlnnbnmnqkkkqqnmllmnK"),
        (16, 13, "__KlnnbnmnqknnmnnnnmmnnnK_"),
        (17, 13, "__KlnbnmnqkqnnnmnnqnnmnnnK"),
        (18, 13, "_Kmlnbnmnqkbnmnnqnnqnnmnnn"),
        (19, 13, "_KnmnknnqKKbnnmnqnnnqnnmnn"),
        (20, 13, "_KmnnknnqqKKbnmnqnnbnnnmnn"),
        (21, 13, "_KlmnknmqqK_Kbnmnqnnbnnnmnn"),
        (22, 13, "_KllnknmmqK_Kqnmnqnnlnnnnnnn"),
        (23, 13, "_KmlnknnmqK_KqnmnqnnnlnnSsnnn"),
        (24, 13, "_KnmnknqqK__KqnmnqqnnnlSSsnnn"),
        (25, 13, "__KmnknnqK__KqnmnqnqnnlSSSsn"),
        (26, 13, "__KlmknnqK__KqnmqqqnqnSSSSsq"),
        (27, 13, "__KmlknnqK__KqnmqqqnSSSSSSSq"),
        (28, 13, "___KmlkqK___KqnmqqKKKSSSKKKk"),
        (29, 13, "___KmlkK____KqnmqqSWkSSSkWsk"),
        (30, 13, "___KmlK_____KqnmqqSsLSSSLssk"),
        (31, 13, "____KlK_____KqnmqqSSSSSDSSsk"),
        (32, 13, "____KmK_____KqbmqKDsSSSSsDK"),
        (33, 13, "_____K______KqqbKKKDSDMSDK"),
    ],
    "chin_and_scarf": [
        (34, 31, "TKDssDKTtt"),
        (35, 30, "bTtTDDTtuuT"),
        (36, 30, "bTuuttuuutT"),
        (37, 30, "TvuuuuuutT"),
        (38, 30, "TvuuutuutT"),
        (39, 30, "TvuuutuutT"),
        (40, 30, "TuvuututT"),
        (41, 31, "TvuututT"),
        (42, 31, "TuvuttT"),
        (43, 32, "TutTC"),
        (44, 33, "TT"),
    ],
    "left_hand": [
        (42, 24, "KsSSK"),
        (43, 24, "KDssK"),
        (44, 24, "KqnnK"),
        (45, 24, "KnmnK"),
        (46, 24, ".KnK"),
        (47, 18, "KCWWCcK"),
        (48, 18, "CWDssCcK"),
        (49, 18, "cWsSSsCK"),
        (50, 18, "KCDsssCK"),
        (51, 18, "KCWDsCcK"),
        (52, 19, "KcCCCc"),
        (53, 20, "KcccK"),
    ],
    "right_hand": [
        (57, 47, "ksSSsK_"),
        (58, 47, "ksSSsK_"),
        (59, 47, "ksSSsK"),
        (60, 47, "ksSSsK"),
        (61, 47, "KkqqkK"),
        (62, 47, "KqbnqK"),
        (63, 47, "KqnbqK"),
        (64, 47, "KqbbqK_"),
        (65, 47, "KkqqkK_"),
        (66, 47, "KDSSsK_"),
        (67, 47, "KsSsDK_"),
        (68, 48, "KssDK_"),
        (69, 49, "KsK_"),
        (70, 50, "K_"),
    ],
}

N4 = [(-1, 0), (1, 0), (0, -1), (0, 1)]
N8 = N4 + [(-1, -1), (-1, 1), (1, -1), (1, 1)]


def sha256(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def hex_rgb(h):
    return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))


def apply_edits(src):
    out = src.copy()
    owner = {}
    for region, rows in EDITS.items():
        for y, x0, spec in rows:
            for i, ch in enumerate(spec):
                x = x0 + i
                if ch == ".":
                    continue
                if (x, y) in owner:
                    sys.exit(f"texel {(x, y)} edited by both {owner[(x, y)]} and {region}")
                owner[(x, y)] = region
                if ch == "_":
                    out[y, x] = (0, 0, 0, 0)
                else:
                    out[y, x] = hex_rgb(ROLES[ch]) + (255,)
    return out, owner


def feet_anchor(op):
    rows = np.where(op.any(1))[0]
    bottom = int(rows.max())
    cols = np.where(op[bottom - FEET_ROWS + 1: bottom + 1].any(0))[0]
    return bottom, (int(cols.min()) + int(cols.max()) + 1) // 2


def checks(src, out):
    a = out[..., 3]
    op = a == 255
    ys, xs = np.where(op)
    colours = sorted({tuple(int(v) for v in c) for c in out[op][:, :3]})
    src_op = src[..., 3] == 255
    isolated = [(int(x), int(y)) for y, x in zip(ys, xs)
                if not any(0 <= y + dy < op.shape[0] and 0 <= x + dx < op.shape[1] and op[y + dy, x + dx] for dy, dx in N8)]
    pinholes = [(x, y) for y in range(1, op.shape[0] - 1) for x in range(1, op.shape[1] - 1)
                if not op[y, x] and all(op[y + dy, x + dx] for dy, dx in N4)]
    knee = (slice(74, 80), slice(26, 33))
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
        "foot_anchor_source": list(feet_anchor(src_op)),
        "rows_from_72_byte_identical_to_source": bool((out[PROTECTED_FROM_ROW:] == src[PROTECTED_FROM_ROW:]).all()),
        "knee_guard_block_x26_32_y74_79_identical": bool((out[knee] == src[knee]).all()),
        "isolated_opaque_texels_8n": isolated,
        "transparent_pinholes_4n": pinholes,
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out-dir", type=Path, default=PILOT_DIR)
    ap.add_argument("--qa-report", type=Path)
    args = ap.parse_args()
    if sha256(SOURCE) != SOURCE_SHA256:
        sys.exit("selout v1 SHA-256 mismatch")
    src = np.array(Image.open(SOURCE).convert("RGBA"))
    out, owner = apply_edits(src)
    m = checks(src, out)
    ok = (m["size"] == list(CELL) and m["alpha_values_present"] == [0, 255] and m["partial_alpha_texels"] == 0
          and m["transparent_texels_with_nonzero_rgb"] == 0 and m["visible_body_height_texels"] == 96
          and m["unique_opaque_rgb_colours"] <= MAX_COLOURS and m["opaque_texels_on_cell_border"] == 0
          and m["foot_anchor_lowest_row_and_feet_mid_x"] == m["foot_anchor_source"] == [PIN[1] - 1, PIN[0]]
          and m["rows_from_72_byte_identical_to_source"] and m["knee_guard_block_x26_32_y74_79_identical"])
    if not ok:
        print(json.dumps(m, indent=1))
        sys.exit("integrity check failed")
    args.out_dir.mkdir(parents=True, exist_ok=True)
    path = args.out_dir / OUTPUT
    tmp = path.with_suffix(".tmp.png")
    Image.fromarray(out, "RGBA").save(tmp, optimize=False, compress_level=9)
    if path.exists() and path.read_bytes() != tmp.read_bytes():
        tmp.unlink()
        sys.exit(f"refusing to change existing bytes of {path.name}")
    tmp.replace(path)
    if sha256(SOURCE) != SOURCE_SHA256:
        sys.exit("selout v1 bytes changed")
    changes = []
    for y, x in zip(*np.where((out != src).any(-1))):
        b, a = src[y, x], out[y, x]
        fmt = lambda p: "transparent" if p[3] == 0 else "#%02x%02x%02x" % tuple(int(v) for v in p[:3])
        changes.append({"x": int(x), "y": int(y), "region": owner[(int(x), int(y))], "before": fmt(b), "after": fmt(a)})
    per_region = {}
    for c in changes:
        per_region[c["region"]] = per_region.get(c["region"], 0) + 1
    kinds = {"opaque_to_transparent": sum(c["after"] == "transparent" and c["before"] != "transparent" for c in changes),
             "transparent_to_opaque": sum(c["before"] == "transparent" and c["after"] != "transparent" for c in changes),
             "recoloured": sum(c["before"] != "transparent" and c["after"] != "transparent" for c in changes)}
    qa = None
    if args.qa_report:
        rep = json.loads(args.qa_report.read_text(encoding="utf-8"))
        qa = {"report": args.qa_report.name, "report_sha256": sha256(args.qa_report),
              "captures": [{k: c[k] for k in ("scene", "variant", "capture", "capture_sha256", "capture_size",
                                              "pilot_visible_logical", "pilot_window_diff_bounds_measured", "pilot_texel_fidelity")}
                           for c in rep["captures"]]}
    manifest = {
        "project": "Worlds Between",
        "milestone": "M8",
        "purpose": "One deliberate pixel-level static polish (v2) of the selout south idle, which the creator chose as closer. Static frame only.",
        "status": "technical candidate; unapproved; not runtime-integrated; no animation",
        "art_approved": False,
        "runtime_integrated": False,
        "walk_frames": 0,
        "requested_changes": [
            "cleaner ponytail silhouette and negative space (viewer-left fall no longer merges with the head)",
            "warm highlight path describing the ponytail sweep",
            "more readable 3/4 face: eyes, nose, mouth, chin",
            "crisper teal scarf vs brown coat boundary",
            "better coat/hand separation",
        ],
        "source": {"role": "read-only input (selout v1); bytes preserved and re-verified after writing",
                   "file": str(SOURCE.relative_to(ROOT)).replace("\\", "/"), "sha256": SOURCE_SHA256,
                   "upstream_reference": "game/assets/characters/pixelorama-pilots/rpg-2-star-ocean-the-second_protagonist-female_south-idle-refinement-reference_m8-v01_20261014-230012-9b6c4a31.png (consulted visually for ponytail/hand structure only; no pixels sampled)"},
        "editor": {"script": "tools/" + Path(__file__).name, "script_sha256": sha256(__file__),
                   "python": platform.python_version(), "pillow": PIL.__version__, "numpy": np.__version__,
                   "run_flags": "-I (isolated)", "method": "explicit texel edit map (EDITS) over selout v1; no resampling, quantizing, filtering or AI editing"},
        "roles": {k: "#" + v for k, v in ROLES.items()},
        "new_colours": ["#" + ROLES["M"]],
        "edit_map": {region: [{"row": y, "x0": x0, "map": spec} for y, x0, spec in rows] for region, rows in EDITS.items()},
        "output": {"file": OUTPUT, "format": "PNG RGBA 8-bit, single image, no metadata chunks",
                   "bytes": path.stat().st_size, "sha256": sha256(path), "measured": m},
        "pixel_changes": {"total": len(changes), "per_region": per_region, "kinds": kinds, "texels": changes},
        "qa_captures": qa,
        "limitations": [
            "Static south idle only; no walk/turn frames; nothing wired into the runtime.",
            "The ponytail is re-drawn as one arc of two locks with a forked tip; the reference's many loose strands are intentionally simplified, so it reads tidier than the reference.",
            "The ear on the viewer-left side was removed (covered by the side lock) to keep the face shape clean.",
            "Eyes are made level and 3 texels tall (the reference head tilt is dropped) for readability at 48 logical px.",
            "Face, hands and scarf are a manual interpretation at 96 texels; they are not measured against the reference.",
            "One new colour (#9a4634 mouth) was added; all other edit colours are existing selout v1 colours.",
            "Rows y >= 72 (knee guard, legs, boots, buckles) are byte-identical to selout v1; the coat torso outside the listed maps is unchanged and keeps v1's residual texture noise.",
            "Visual approval remains human; checks here are integrity and measurement only.",
        ],
    }
    (args.out_dir / MANIFEST).write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    print(f"PNG {path} sha256={sha256(path)}")
    print(f"  size={m['size']} h={m['visible_body_height_texels']} w={m['visible_body_width_texels']} alpha={m['alpha_values_present']} "
          f"colours={m['unique_opaque_rgb_colours']} anchor={m['foot_anchor_lowest_row_and_feet_mid_x']} "
          f"rows72+_identical={m['rows_from_72_byte_identical_to_source']} knee_identical={m['knee_guard_block_x26_32_y74_79_identical']}")
    print(f"  isolated={m['isolated_opaque_texels_8n']} pinholes={m['transparent_pinholes_4n']}")
    print(f"  changes={len(changes)} per_region={per_region} kinds={kinds}")
    print(f"MANIFEST {args.out_dir / MANIFEST}")


if __name__ == "__main__":
    main()
