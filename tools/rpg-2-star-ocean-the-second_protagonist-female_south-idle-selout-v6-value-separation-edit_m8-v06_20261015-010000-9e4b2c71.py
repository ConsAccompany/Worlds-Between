"""Female protagonist south idle, selout v6 value/separation pass (M8 v06), one frame.

Technical candidate only; unapproved; not used by the game runtime. No animation.
Input is the selout v5 candidate PNG (read-only, source-locked by SHA-256). Output is ONE
new PNG made by deterministic, region-scoped colour-role operations on v5 - no resampling,
no new colours, no alpha changes, no added trims.

Why: at 48 logical px in the bright city/outskirts, v5's coat midtones sit close to the warm
paving and the figure is held only by its outline. v6 groups values instead of adding detail:

  op 1  coat_darken     inside the coat boxes only, each coat-cloth texel steps one value
                        darker: w (#7e5f4a) -> m (#634739), m -> n (#533b32), n -> b (#41302b).
                        Upper coat (shoulders, panels, sleeves, x18-29 / x38-50, y34-53, fist
                        and left cuff excluded), lower right coat (x41-46, y57-60) and both coat
                        skirts (left x21-29 y57-61, x21-27 y62-63, x21-25 y64-71; right x43-47
                        y61-72). Internal structure is kept (lit band stays lighter than base
                        stays lighter than shadow); the darkest step merges n into b.
                        Shirt, belts, straps, trims, badge, pocket, canister, trousers, skin,
                        scarf and hair are not remapped (role filter + box exclusions).
  op 2  contour_ink     silhouette-edge texels (opaque with a transparent 4-neighbour) in rows
                        y34-79 whose role is cloth/leather/cream (w m n b l L r c C) become ink
                        K (#0a0a0e), giving a continuous dark contour against bright ground.
                        Teal, skin, metal and slate edges are left as they are; hair/face rows
                        and the boots (y>=80) are untouched.

Result intent: three big value groups at game scale - dark coat, mid trousers, light shirt -
plus the teal scarf and skin accents, with a crisp dark edge on bright backgrounds.

Kept byte-identical to v5 (asserted): rows y8-33 (hair, ponytail, face), y80-111 (boots,
buckles), every teal texel, every skin/face/metal/slate texel, and alpha everywhere.

Run with the Codex-runtime Python (Pillow 12.3.0, NumPy 2.3.5), isolated mode:
  python -I <this script>                        # write PNG + manifest (refuses to change existing PNG bytes)
  python -I <this script> --out-dir <dir>        # determinism re-check into another folder
  python -I <this script> --qa-report <json>     # also embed Godot capture hashes in the manifest
  python -I <this script> --dump SRC|V6 x0 y0 x1 y1   # print a texel role map (review aid)
  python -I <this script> --preview <png> [--scale N] # v6 only, nearest-neighbour enlarged (review aid)
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
SOURCE = PILOT_DIR / "rpg-2-star-ocean-the-second_protagonist-female_south-idle-selout-v5-lowerbody-hair-candidate_m8-v05_20261015-004000-8b3e5c07.png"
SOURCE_SHA256 = "8ddac8acb4261cfc4e42ae9727b7cb5a4ff70791973909ab80cea33920ad7ace"
PRESERVED = {
    "v4": (PILOT_DIR / "rpg-2-star-ocean-the-second_protagonist-female_south-idle-selout-v4-structural-candidate_m8-v04_20261015-001500-e5b81f36.png",
           "da8a1ce11db136f7061206a3d8f5038b7d995016e36af2fc011d0a6f0dbcf4d7"),
    "v3": (PILOT_DIR / "rpg-2-star-ocean-the-second_protagonist-female_south-idle-selout-v3-polish-candidate_m8-v03_20261014-234700-3c9a5d27.png",
           "21b148cc026a70cdb173200c46cf007f83e4963cd7b7a7c71a174a7cb343cbc3"),
    "v2": (PILOT_DIR / "rpg-2-star-ocean-the-second_protagonist-female_south-idle-selout-v2-polish-candidate_m8-v02_20261014-233300-d2eeefa2.png",
           "4c8a720adc93c2bdbf2039da929f96eb617d4829ab35da2333105ac7d870e6f5"),
    "v1": (PILOT_DIR / "rpg-2-star-ocean-the-second_protagonist-female_south-idle-refine-selout-candidate_m8-v01_20261014-231100-4d141ad5.png",
           "7cb9f7044ed728894ab613725f0c6bdd876c29527e505b7f061689112da37f88"),
}
RUN = "m8-v06_20261015-010000"
OUTPUT = f"rpg-2-star-ocean-the-second_protagonist-female_south-idle-selout-v6-value-separation-candidate_{RUN}-5a7d3f18.png"
MANIFEST = f"rpg-2-star-ocean-the-second_protagonist-female_south-idle-selout-v6-value-separation-manifest_{RUN}-c2e9081b.json"

MAX_COLOURS = 32
CELL = (80, 112)
PIN = (40, 104)
FEET_ROWS = 6

ROLES = [
    ("K", "0a0a0e"), ("k", "201c20"), ("O", "23252b"), ("T", "0a323b"), ("q", "302526"), ("G", "30333a"),
    ("b", "41302b"), ("t", "11525b"), ("n", "533b32"), ("y", "4a4749"), ("g", "474b54"), ("m", "634739"),
    ("L", "714730"), ("u", "1a767b"), ("l", "845436"), ("w", "7e5f4a"), ("z", "626873"), ("v", "249b98"),
    ("r", "a16f4b"), ("D", "bb7c50"), ("c", "b09986"), ("s", "e39664"), ("C", "d7c0a8"), ("B", "cfc8bd"),
    ("S", "fbc38d"), ("W", "faead4"), ("M", "9a4634"),
]
TEAL = {"T", "t", "u", "v"}
NEVER_TOUCH = TEAL | {"s", "S", "D", "M", "W", "B", "O", "G", "g", "z", "y", "k", "q"}

# op 1: one-step coat darkening. Boxes are (x0, y0, x1, y1) exclusive; exclusions are carved
# out of the union. Only texels whose v5 role is a key of COAT_STEP are changed.
COAT_STEP = {"w": "m", "m": "n", "n": "b"}
COAT_BOXES = {
    "upper_left_coat_and_sleeve": (18, 34, 30, 54),
    "upper_right_coat_and_sleeve": (38, 34, 51, 54),
    "lower_right_coat_below_arm": (41, 57, 47, 61),
    "left_skirt_y57_61": (21, 57, 30, 62),
    "left_skirt_y62_63": (21, 62, 28, 64),
    "left_skirt_y64_71": (21, 64, 26, 72),
    "right_skirt_y61_72": (43, 61, 48, 73),
}
COAT_EXCLUDE = {
    "fist_x24_28_y42_46": (24, 42, 29, 47),
    "left_cuff_x18_24_y47_53": (18, 47, 25, 54),
    "right_forearm_glove_fingers_x47_52_y57_70": (47, 57, 53, 71),
}

# op 2: dark contour on silhouette edges.
CONTOUR_ROWS = (34, 80)  # y0, y1 exclusive
CONTOUR_ROLES = {"w", "m", "n", "b", "l", "L", "r", "c", "C"}

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


def role_grid(img):
    return [[role_of(img[y, x]) for x in range(CELL[0])] for y in range(CELL[1])]


def in_box(x, y, box):
    return box[0] <= x < box[2] and box[1] <= y < box[3]


def coat_mask():
    m = np.zeros(CELL[::-1], bool)
    for x0, y0, x1, y1 in COAT_BOXES.values():
        m[y0:y1, x0:x1] = True
    for x0, y0, x1, y1 in COAT_EXCLUDE.values():
        m[y0:y1, x0:x1] = False
    return m


def apply_ops(src):
    """Both ops read v5 roles (not each other's output), so the result does not depend on order;
    where both apply, the contour wins."""
    rmap = dict(ROLES)
    roles = role_grid(src)
    if any(r == "?" for row in roles for r in row):
        sys.exit("v5 contains a colour outside the role table")
    out = src.copy()
    owner = {}
    cm = coat_mask()
    op = src[..., 3] == 255
    for y in range(CELL[1]):
        for x in range(CELL[0]):
            r = roles[y][x]
            if cm[y, x] and r in COAT_STEP:
                out[y, x, :3] = hex_rgb(rmap[COAT_STEP[r]])
                owner[(x, y)] = "coat_darken"
    for y in range(*CONTOUR_ROWS):
        for x in range(CELL[0]):
            if not op[y, x] or roles[y][x] not in CONTOUR_ROLES:
                continue
            if any(not (0 <= y + dy < CELL[1] and 0 <= x + dx < CELL[0]) or not op[y + dy, x + dx] for dy, dx in N4):
                out[y, x, :3] = hex_rgb(rmap["K"])
                owner[(x, y)] = "contour_ink"
    return out, owner, roles


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


def protected(src, out, roles):
    changed = (out != src).any(-1)
    touched_roles = {roles[y][x] for y, x in zip(*np.where(changed))}
    never = np.array([[roles[y][x] in NEVER_TOUCH for x in range(CELL[0])] for y in range(CELL[1])])
    return {
        "alpha_identical_everywhere": bool((out[..., 3] == src[..., 3]).all()),
        "rows_8_33_hair_ponytail_face_identical": bool((out[8:34] == src[8:34]).all()),
        "rows_80_and_below_boots_identical": bool((out[80:] == src[80:]).all()),
        "teal_skin_metal_slate_texels_identical": bool((out[never] == src[never]).all()),
        "changes_only_from_cloth_leather_cream_roles": touched_roles <= (set(COAT_STEP) | CONTOUR_ROLES),
        "no_new_colours": {role_of(p) for p in out.reshape(-1, 4) if p[3] == 255} <= {ch for ch, _ in ROLES},
    }


def luma(img, mask):
    rgb = img[..., :3].astype(float)
    y = 0.299 * rgb[..., 0] + 0.587 * rgb[..., 1] + 0.114 * rgb[..., 2]
    return round(float(y[mask].mean()), 2) if mask.any() else None


def value_metrics(img, src_roles):
    """Objective readability numbers: mean luma per value group and the dark share of the
    silhouette edge (y34-79). Groups are defined from v5 roles so v5 and v6 compare like
    for like."""
    op = img[..., 3] == 255
    cm = coat_mask()
    group = lambda roles: np.array([[src_roles[y][x] in roles for x in range(CELL[0])] for y in range(CELL[1])])
    coat = cm & group(set(COAT_STEP) | {"b"}) & op
    shirt = np.zeros_like(op)
    shirt[42:63, 30:41] = True
    shirt &= group({"c", "C", "W"}) & op
    legs = np.zeros_like(op)
    legs[62:74, 27:35] = True
    legs[62:74, 37:45] = True
    legs &= group({"w", "m", "b"}) & op
    edge = np.zeros_like(op)
    for y in range(*CONTOUR_ROWS):
        for x in range(CELL[0]):
            if op[y, x] and any(not op[y + dy, x + dx] for dy, dx in N4):
                edge[y, x] = True
    rgb = img[..., :3].astype(float)
    L = 0.299 * rgb[..., 0] + 0.587 * rgb[..., 1] + 0.114 * rgb[..., 2]
    return {
        "coat_mean_luma": luma(img, coat),
        "shirt_mean_luma": luma(img, shirt),
        "legs_mean_luma": luma(img, legs),
        "silhouette_edge_texels_y34_79": int(edge.sum()),
        "silhouette_edge_share_luma_below_40": round(float((L[edge] < 40).mean()), 4),
    }


def dump(img, x0, y0, x1, y1):
    print("    " + "".join(str(x // 10 % 10) for x in range(x0, x1)))
    print("    " + "".join(str(x % 10) for x in range(x0, x1)))
    for y in range(y0, y1):
        print("%3d " % y + "".join(role_of(img[y, x]) for x in range(x0, x1)))


def preview(out, path, scale):
    """v6 alone, nearest-neighbour enlarged on neutral grey (review aid; not a sheet)."""
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
        sys.exit("v5 source SHA-256 mismatch")
    for name, (p, h) in PRESERVED.items():
        if sha256(p) != h:
            sys.exit(f"{name} SHA-256 mismatch (must stay preserved)")
    src = np.array(Image.open(SOURCE).convert("RGBA"))
    if args.dump and args.dump[0] == "SRC":
        dump(src, *map(int, args.dump[1:]))
        return
    out, owner, roles = apply_ops(src)
    if args.dump:
        dump(out, *map(int, args.dump[1:]))
        return
    m = checks(src, out)
    prot = protected(src, out, roles)
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
    fmt = lambda p: "#%02x%02x%02x" % tuple(int(v) for v in p[:3])
    changes = [{"x": int(x), "y": int(y), "op": owner[(int(x), int(y))], "role_before": roles[y][x],
                "before": fmt(src[y, x]), "after": fmt(out[y, x])}
               for y, x in zip(*np.where((out != src).any(-1)))]
    per_op = {}
    for c in changes:
        per_op[c["op"]] = per_op.get(c["op"], 0) + 1
    vm = {"v5": value_metrics(src, roles), "v6": value_metrics(out, roles)}
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
        "purpose": "Selout v6 value/separation pass of the female south idle for 48 logical px readability on bright ground: coat one value step darker in coat regions, dark silhouette contour on cloth edges. Static frame only.",
        "status": "technical candidate; unapproved; not runtime-integrated; no animation",
        "art_approved": False,
        "human_reviewed": False,
        "runtime_integrated": False,
        "walk_frames": 0,
        "authorship": "Operations authored by Claude with file edits only (no execution); the script is run by Codex in the workspace.",
        "source": {"role": "read-only input (selout v5), source-locked", "file": str(SOURCE.relative_to(ROOT)).replace("\\", "/"),
                   "sha256": SOURCE_SHA256,
                   "also_preserved": {k: {"file": str(p.relative_to(ROOT)).replace("\\", "/"), "sha256": h} for k, (p, h) in PRESERVED.items()}},
        "editor": {"script": "tools/" + Path(__file__).name, "script_sha256": sha256(__file__),
                   "python": platform.python_version(), "pillow": PIL.__version__, "numpy": np.__version__,
                   "run_flags": "-I (isolated)",
                   "method": "two region-scoped colour-role operations over v5 (coat_darken, contour_ink); recolour only; no resampling, quantizing, filtering or AI editing"},
        "operations": {
            "coat_darken": {"step": COAT_STEP, "boxes": COAT_BOXES, "excluded": COAT_EXCLUDE},
            "contour_ink": {"rows": list(CONTOUR_ROWS), "edge_rule": "opaque texel with a transparent 4-neighbour",
                            "roles": sorted(CONTOUR_ROLES), "to": "K #0a0a0e"},
        },
        "roles": {ch: "#" + h for ch, h in ROLES},
        "new_colours": [],
        "output": {"file": OUTPUT, "format": "PNG RGBA 8-bit, single image, no metadata chunks",
                   "bytes": path.stat().st_size, "sha256": sha256(path), "measured": m},
        "protected_invariants": prot,
        "value_metrics_v5_vs_v6": vm,
        "pixel_changes": {"total": len(changes), "per_op": per_op, "texels": changes},
        "qa_captures": qa,
        "limitations": [
            "Static south idle only; no walk/turn frames; nothing wired into the runtime.",
            "Operations were authored without Claude seeing the v6 result; a --preview read and Godot captures are needed before judging.",
            "One-step darkening merges the coat's two darkest tones (n into b), so the coat has fewer internal shades than v5; fine fold detail in shadow is reduced on purpose.",
            "A darker coat may sit closer to the hair darks at the shoulders and read heavier in the dark annex room; it is tuned for the bright city/outskirts.",
            "The ink contour is a uniform K edge on cloth; it is not light-direction aware (no lighter rim on the lit side).",
            "Shirt, legs, scarf, skin, hair and boots are unchanged, so any remaining issues there (e.g. ponytail size) carry over from v5.",
            "Visual approval remains human.",
        ],
    }
    (args.out_dir / MANIFEST).write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    print(f"PNG {path} sha256={sha256(path)}")
    print(f"  size={m['size']} h={m['visible_body_height_texels']} w={m['visible_body_width_texels']} alpha={m['alpha_values_present']} "
          f"colours={m['unique_opaque_rgb_colours']} anchor={m['foot_anchor_lowest_row_and_feet_mid_x']} opaque={m['opaque_texels']}")
    print(f"  protected={prot}")
    print(f"  changes={len(changes)} per_op={per_op}")
    print(f"  value_metrics v5={vm['v5']}")
    print(f"  value_metrics v6={vm['v6']}")
    print(f"MANIFEST {args.out_dir / MANIFEST}")


if __name__ == "__main__":
    main()
