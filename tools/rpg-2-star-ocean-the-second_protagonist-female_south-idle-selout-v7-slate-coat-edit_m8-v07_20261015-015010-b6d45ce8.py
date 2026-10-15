"""Female protagonist south idle, selout v7 slate-coat pass (M8 v07), one frame.

Technical candidate only; unapproved; not used by the game runtime. No animation.
Input is the selout v6 candidate PNG (read-only, source-locked by SHA-256). Output is ONE
new PNG made by deterministic, texel-scoped recolours of v6 - no resampling, no alpha
changes, no shape changes, no dithering. Every changed texel is listed in the manifest.

Why: the user's reply to v6 was "明亮场景对比度仍不足" (bright-scene contrast still
insufficient). v6 darkened the coat but kept it the same warm red-brown hue as the warm
beige paving and its brown grout, so on the bright outskirts/city the coat still merged.
v7 changes the coat's hue family rather than only its value, and designs the edge:

  op 1  coat_slate      the coat texels v6 owns (v6 coat boxes, v6 roles m/n/b) move to a
                        new cool slate-taupe ramp: m -> P1 lit, n -> P2 base, b -> P3 shadow.
                        Same value order as v6, so the fold structure is kept; hue moves
                        from ~20 deg / sat ~0.4 to a near-neutral cool grey-taupe that sits
                        opposite the paving's warm 40 deg / sat ~0.47.
  op 2  trim_warm       the small lapel trims (v6 role r inside TRIM_BOXES, 14 texels)
                        become a warmer copper P4, so the trim reads as accent on the cooler
                        coat and the identity's brown/teal/cream read is kept.
  op 3  edge_cluster    9 hand-placed texels (EDGE_CLUSTERS, roles asserted): the lit rim
                        of the left sleeve is kept only at the shoulder (lower 6 rim texels
                        -> P2), and the right skirt hem row (3 texels) joins the P3 shadow.
                        The rest of the coat edge keeps v6's structure, now in slate: P1
                        rim on the lit side, 2-3 texel P3/q/K clusters on the shadow side.

Kept byte-identical to v6 (asserted): alpha everywhere, rows y8-33 (hair, ponytail, face),
rows y80-111 (boots), every texel outside the coat/trim boxes and edge-cluster texels, and
every teal, skin, metal, slate, cream, shirt and ink texel.

Run with the Codex-runtime Python (Pillow 12.3.0, NumPy 2.3.5), isolated mode:
  python -I <this script>                        # write PNG + manifest (refuses to change existing PNG bytes)
  python -I <this script> --out-dir <dir>        # determinism re-check into another folder
  python -I <this script> --qa-report <json>     # also embed Godot capture hashes in the manifest
  python -I <this script> --dump SRC|V7 x0 y0 x1 y1   # print a texel role map (review aid)
  python -I <this script> --preview <png> [--scale N] # v7 beside v6, nearest-neighbour enlarged (review aid)
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
SOURCE = PILOT_DIR / "rpg-2-star-ocean-the-second_protagonist-female_south-idle-selout-v6-value-separation-candidate_m8-v06_20261015-010000-5a7d3f18.png"
SOURCE_SHA256 = "f606afeb70e422b5f0c44373126a7112830e8ed47c22433b18255829fedd283b"
PRESERVED = {
    "v5": (PILOT_DIR / "rpg-2-star-ocean-the-second_protagonist-female_south-idle-selout-v5-lowerbody-hair-candidate_m8-v05_20261015-004000-8b3e5c07.png",
           "8ddac8acb4261cfc4e42ae9727b7cb5a4ff70791973909ab80cea33920ad7ace"),
    "v6_manifest": (PILOT_DIR / "rpg-2-star-ocean-the-second_protagonist-female_south-idle-selout-v6-value-separation-manifest_m8-v06_20261015-010000-c2e9081b.json",
                    "10dd17857ce1bc9fca1cfd84abbf4a76cc5346a87a27136ce32e386038c26572"),
}
RUN = "m8-v07_20261015-015010"
OUTPUT = f"rpg-2-star-ocean-the-second_protagonist-female_south-idle-selout-v7-slate-coat-candidate_{RUN}-05615df5.png"
MANIFEST = f"rpg-2-star-ocean-the-second_protagonist-female_south-idle-selout-v7-slate-coat-manifest_{RUN}-ed510f85.json"

MAX_COLOURS = 32
CELL = (80, 112)
PIN = (40, 104)
FEET_ROWS = 6

# v6 roles (unchanged from the v6 script) plus the four new v7 roles.
ROLES = [
    ("K", "0a0a0e"), ("k", "201c20"), ("O", "23252b"), ("T", "0a323b"), ("q", "302526"), ("G", "30333a"),
    ("b", "41302b"), ("t", "11525b"), ("n", "533b32"), ("y", "4a4749"), ("g", "474b54"), ("m", "634739"),
    ("L", "714730"), ("u", "1a767b"), ("l", "845436"), ("w", "7e5f4a"), ("z", "626873"), ("v", "249b98"),
    ("r", "a16f4b"), ("D", "bb7c50"), ("c", "b09986"), ("s", "e39664"), ("C", "d7c0a8"), ("B", "cfc8bd"),
    ("S", "fbc38d"), ("W", "faead4"), ("M", "9a4634"),
]
NEW_ROLES = [
    ("1", "625c61", "P1 coat lit, cool slate-taupe"),
    ("2", "46424a", "P2 coat base, cool slate-taupe"),
    ("3", "2d2c34", "P3 coat shadow / edge cluster, cool slate"),
    ("4", "c07a40", "P4 warm copper trim"),
]
ALL_ROLES = ROLES + [(ch, h) for ch, h, _ in NEW_ROLES]
SOURCE_ROLES = {ch for ch, _ in ROLES}

# op 1: the coat area is v6's coat area (same boxes and exclusions as the v6 script).
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
COAT_SLATE = {"m": "1", "n": "2", "b": "3"}

# op 2: lapel trims only (the diagonal r lines either side of the scarf). Only v6 role r
# inside these boxes changes. The skirt front edges keep v6's r: in copper they became long
# orange stripes at 48 px.
TRIM_BOXES = {
    "left_lapel_x26_30_y34_42": (26, 34, 30, 42),
    "right_lapel_x39_44_y34_42": (39, 34, 44, 42),
}
TRIM_FROM = {"r"}

# op 3: hand-placed edge clusters, (x, y) -> (expected v6 role, new role). Asserted.
# After op 1 the coat already keeps v6's edge structure: a P1 rim inside the ink on the lit
# (left) sleeve and 2-3 texel P3/q/K clusters on the shadow (right) sleeve and skirts. These
# texels shape it on purpose:
#   lower_left_sleeve_rim_to_base  the lit rim stops at the shoulder (rows 34-41), so the
#                                  highlight is a short shoulder cluster instead of a full-length
#                                  line, and the lower sleeve is a darker mass on bright paving.
#   right_skirt_hem_to_shadow      the right skirt's bottom row (outside v6's coat boxes, still
#                                  warm v6 b) joins the slate shadow, closing the coat's hem.
EDGE_CLUSTERS = {
    "lower_left_sleeve_rim_to_base": {(22, 42): ("m", "2"), (22, 43): ("m", "2"), (21, 44): ("m", "2"),
                                      (20, 45): ("m", "2"), (19, 46): ("m", "2"), (20, 46): ("m", "2")},
    "right_skirt_hem_to_shadow": {(44, 73): ("b", "3"), (45, 73): ("b", "3"), (46, 73): ("b", "3")},
}
EDGE_TEXELS = {xy: v for group in EDGE_CLUSTERS.values() for xy, v in group.items()}

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
    for ch, h in ALL_ROLES:
        if h == key:
            return ch
    return "?"


def role_grid(img):
    return [[role_of(img[y, x]) for x in range(CELL[0])] for y in range(CELL[1])]


def box_mask(boxes, exclude=None):
    m = np.zeros(CELL[::-1], bool)
    for x0, y0, x1, y1 in boxes.values():
        m[y0:y1, x0:x1] = True
    for x0, y0, x1, y1 in (exclude or {}).values():
        m[y0:y1, x0:x1] = False
    return m


def apply_ops(src):
    """All ops read v6 roles. Order of precedence where two apply: trim_warm, then
    edge_cluster, then coat_slate (a trim texel is never a coat texel, since roles differ)."""
    rmap = dict(ALL_ROLES)
    roles = role_grid(src)
    if any(r not in SOURCE_ROLES | {"."} for row in roles for r in row):
        sys.exit("v6 contains a colour outside the v6 role table")
    op = src[..., 3] == 255
    coat = box_mask(COAT_BOXES, COAT_EXCLUDE) & np.array([[roles[y][x] in COAT_SLATE for x in range(CELL[0])] for y in range(CELL[1])])
    trim = box_mask(TRIM_BOXES) & np.array([[roles[y][x] in TRIM_FROM for x in range(CELL[0])] for y in range(CELL[1])])

    for (x, y), (before, _) in EDGE_TEXELS.items():
        if roles[y][x] != before or not op[y, x]:
            sys.exit(f"edge cluster texel ({x},{y}) is v6 role {roles[y][x]}, expected {before}")
    out = src.copy()
    owner = {}
    for y in range(CELL[1]):
        for x in range(CELL[0]):
            new = None
            if trim[y, x]:
                new, why = "4", "trim_warm"
            elif (x, y) in EDGE_TEXELS:
                new, why = EDGE_TEXELS[(x, y)][1], "edge_cluster"
            elif coat[y, x]:
                new, why = COAT_SLATE[roles[y][x]], "coat_slate"
            if new is not None:
                out[y, x, :3] = hex_rgb(rmap[new])
                owner[(x, y)] = why
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
    keep_roles = SOURCE_ROLES - set(COAT_SLATE) - TRIM_FROM
    keep = np.array([[roles[y][x] in keep_roles for x in range(CELL[0])] for y in range(CELL[1])])
    inside = box_mask(COAT_BOXES, COAT_EXCLUDE) | box_mask(TRIM_BOXES)
    for x, y in EDGE_TEXELS:
        inside[y, x] = True
    return {
        "alpha_identical_everywhere": bool((out[..., 3] == src[..., 3]).all()),
        "rows_8_33_hair_ponytail_face_identical": bool((out[8:34] == src[8:34]).all()),
        "rows_80_and_below_boots_identical": bool((out[80:] == src[80:]).all()),
        "texels_outside_coat_trim_boxes_and_edge_clusters_identical": bool((out[~inside] == src[~inside]).all()),
        "ink_teal_skin_metal_cream_shirt_leather_texels_identical": bool((out[keep] == src[keep]).all()),
        "changes_only_from_coat_m_n_b_and_trim_r": touched_roles <= (set(COAT_SLATE) | TRIM_FROM),
        "only_declared_new_colours": {role_of(p) for p in out.reshape(-1, 4) if p[3] == 255} <= {ch for ch, _ in ALL_ROLES},
    }


def luma_arr(img):
    rgb = img[..., :3].astype(float)
    return 0.299 * rgb[..., 0] + 0.587 * rgb[..., 1] + 0.114 * rgb[..., 2]


def value_metrics(img, coat):
    """Coat mean luma / chroma and the share of coat texels within 12 deg of the paving hue
    (40 deg) with saturation > 0.25 - i.e. coat texels that share the bright paving's hue family."""
    op = img[..., 3] == 255
    m = coat & op
    rgb = img[..., :3].astype(float)[m] / 255.0
    mx, mn = rgb.max(1), rgb.min(1)
    sat = np.where(mx > 0, (mx - mn) / np.maximum(mx, 1e-9), 0)
    d = np.maximum(mx - mn, 1e-9)
    r, g, b = rgb.T
    h = np.where(mx == r, ((g - b) / d) % 6, np.where(mx == g, (b - r) / d + 2, (r - g) / d + 4)) * 60
    L = luma_arr(img)[m]
    return {
        "coat_texels": int(m.sum()),
        "coat_mean_luma": round(float(L.mean()), 2),
        "coat_luma_steps": sorted({round(float(v), 1) for v in L}),
        "coat_mean_hsv_saturation": round(float(sat.mean()), 3),
        "coat_share_warm_paving_hue_family": round(float(((abs(h - 40) <= 25) & (sat > 0.25)).mean()), 4),
    }


def dump(img, x0, y0, x1, y1):
    print("    " + "".join(str(x // 10 % 10) for x in range(x0, x1)))
    print("    " + "".join(str(x % 10) for x in range(x0, x1)))
    for y in range(y0, y1):
        print("%3d " % y + "".join(role_of(img[y, x]) for x in range(x0, x1)))


def preview(src, out, path, scale):
    """v6 | v7 side by side, nearest-neighbour enlarged on neutral grey (review aid; not an asset)."""
    bg = Image.new("RGBA", (CELL[0] * scale * 2, CELL[1] * scale), (150, 150, 150, 255))
    for i, arr in enumerate((src, out)):
        im = Image.fromarray(arr, "RGBA").resize((CELL[0] * scale, CELL[1] * scale), Image.NEAREST)
        bg.alpha_composite(im, (i * CELL[0] * scale, 0))
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
        sys.exit("v6 source SHA-256 mismatch")
    preserved = PRESERVED
    for name, (p, h) in preserved.items():
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
        preview(src, out, args.preview, args.scale)
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
    if sha256(SOURCE) != SOURCE_SHA256 or any(sha256(p) != h for p, h in preserved.values()):
        sys.exit("a preserved source changed")
    fmt = lambda p: "#%02x%02x%02x" % tuple(int(v) for v in p[:3])
    changes = [{"x": int(x), "y": int(y), "op": owner[(int(x), int(y))], "role_before": roles[y][x],
                "role_after": role_of(out[y, x]), "before": fmt(src[y, x]), "after": fmt(out[y, x])}
               for y, x in zip(*np.where((out != src).any(-1)))]
    per_op = {}
    for c in changes:
        per_op[c["op"]] = per_op.get(c["op"], 0) + 1
    coat = box_mask(COAT_BOXES, COAT_EXCLUDE) & np.array([[roles[y][x] in COAT_SLATE for x in range(CELL[0])] for y in range(CELL[1])])
    vm = {"v6": value_metrics(src, coat), "v7": value_metrics(out, coat)}
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
        "purpose": "Selout v7 slate-coat pass of the female south idle, answering the user's v6 reply '明亮场景对比度仍不足': coat moved to a cool slate-taupe ramp, warm copper lapel trims, hand-placed edge clusters (shoulder-only lit rim, slate hem). Static frame only.",
        "status": "technical candidate; unapproved; not runtime-integrated; no animation",
        "art_approved": False,
        "human_reviewed": False,
        "runtime_integrated": False,
        "walk_frames": 0,
        "authorship": "Operations authored and run by Claude (Claude Code) in the workspace; results were previewed and checked in Godot before this manifest was written.",
        "source": {"role": "read-only input (selout v6), source-locked", "file": str(SOURCE.relative_to(ROOT)).replace("\\", "/"),
                   "sha256": SOURCE_SHA256,
                   "also_preserved": {k: {"file": str(p.relative_to(ROOT)).replace("\\", "/"), "sha256": h} for k, (p, h) in preserved.items()}},
        "editor": {"script": "tools/" + Path(__file__).name, "script_sha256": sha256(__file__),
                   "python": platform.python_version(), "pillow": PIL.__version__, "numpy": np.__version__,
                   "run_flags": "-I (isolated)",
                   "method": "three texel-scoped recolour operations over v6 (coat_slate, trim_warm, edge_cluster); recolour only; no resampling, quantizing, filtering, dithering or AI editing",
                   "pixel_editor_compatibility": "single 80x112 RGBA PNG, binary alpha, <=32 colours; opens as-is in Pixelorama 1.2.3 (work/tooling/pixelorama-1-2-3) for manual texel edits"},
        "operations": {
            "coat_slate": {"map": COAT_SLATE, "boxes": COAT_BOXES, "excluded": COAT_EXCLUDE},
            "trim_warm": {"from_roles": sorted(TRIM_FROM), "to": "4", "boxes": TRIM_BOXES},
            "edge_cluster": {name: [{"x": x, "y": y, "v6_role": b, "to": a} for (x, y), (b, a) in group.items()]
                             for name, group in EDGE_CLUSTERS.items()},
        },
        "roles": {ch: "#" + h for ch, h in ROLES},
        "new_colours": {ch: {"hex": "#" + h, "use": use} for ch, h, use in NEW_ROLES},
        "output": {"file": OUTPUT, "format": "PNG RGBA 8-bit, single image, no metadata chunks",
                   "bytes": path.stat().st_size, "sha256": sha256(path), "measured": m},
        "protected_invariants": prot,
        "coat_metrics_v6_vs_v7": vm,
        "pixel_changes": {"total": len(changes), "per_op": per_op, "texels": changes},
        "qa_captures": qa,
        "limitations": [
            "Static south idle only; no walk/turn frames; nothing wired into the runtime.",
            "Only the coat changes hue; trousers, hair and boots keep v6's warm browns, so the lower legs still sit in the paving's hue family.",
            "Only 9 texels are hand-placed edge clusters; the rest of the coat edge is v6's existing value structure recoloured, so the silhouette line itself is still v6's uniform K ink.",
            "Four new colours (27 -> 31 of 32); the warm copper trim is a new hue, not taken from the concept palette.",
            "Visual approval remains human.",
        ],
    }
    (args.out_dir / MANIFEST).write_text(json.dumps(manifest, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"PNG {path} sha256={sha256(path)}")
    print(f"  size={m['size']} h={m['visible_body_height_texels']} w={m['visible_body_width_texels']} alpha={m['alpha_values_present']} "
          f"colours={m['unique_opaque_rgb_colours']} anchor={m['foot_anchor_lowest_row_and_feet_mid_x']} opaque={m['opaque_texels']}")
    print(f"  protected={prot}")
    print(f"  changes={len(changes)} per_op={per_op}")
    print(f"  coat v6={vm['v6']}")
    print(f"  coat v7={vm['v7']}")
    print(f"MANIFEST {args.out_dir / MANIFEST}")


if __name__ == "__main__":
    main()
