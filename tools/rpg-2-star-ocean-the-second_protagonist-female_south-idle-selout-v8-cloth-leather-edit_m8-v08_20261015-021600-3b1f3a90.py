"""Female protagonist south idle, selout v8 cloth/leather hierarchy pass (M8 v08), one frame.

Technical candidate only; unapproved; not used by the game runtime. No animation.
Input is the selout v7 candidate PNG (read-only, source-locked by SHA-256). Output is ONE
new PNG made by deterministic, texel-scoped recolours of v7 - no resampling, no alpha
changes, no shape changes, no dithering, no AI redraw. Every changed texel is in the manifest.

Why: Codex's visual review of the v7 1280x720 captures: the upper-coat palette shift is subtle
at full scale and the lower body still merges with the warm paving; the v7 QA note also shows
the city local minimum coat contrast fell below v6. v8 sets one material rule for the whole
figure instead of recolouring the coat alone:

    cloth = cool      coat (storm slate, the strongest-chroma dark mass) and trousers (deep
                      spruce-grey, a darker cut of the concept sheet's own #547b76 swatch)
    leather = warm    belt, straps, boots, lapel/front trims keep the warm umber family
    light accents     face, shirt, cuffs and laces are untouched

  op 1  coat_storm_slate   v7's three coat colours (roles 1/2/3, every texel that has them)
                           move to a bluer, wider ramp. Same texels, same value order, so the
                           fold structure is kept; this repurposes the v7 slots, no new count.
  op 2  coat_cluster       hand-placed texels (asserted) that merge 1-texel lit/shadow stripes
                           on the right sleeve into a shadow-side mass and widen the lit
                           shoulder cluster, so light/mid/shadow read as three groups at 1:1.
  op 3  trousers_spruce    the trouser texels (TROUSER_BOXES minus exclusions, v7 roles
                           w/m/b/n only): w -> T1 lit, m -> T2 base, b/n -> coat shadow 3
                           (one shared cool deep for all cloth). On the right leg the lit
                           column is kept only on its left (lit) side.
  op 4  boots_umber        boot texels (BOOT_BOXES, roles l/L/n/b/m) step one value down the
                           existing warm leather ramp (l->L, L->n, n->b, b->q, m->n), closer to
                           the concept's dark boots; hand-placed toe-cap texels keep v7's l.
  op 5  palette_merge      the 7 flask texels of y #4a4749 become g #474b54 (dE76 ~4), freeing
                           a slot so the palette stays at 32.

Kept byte-identical to v7 (asserted): alpha everywhere, rows y8-33 (hair, ponytail, face),
every ink K/k, teal, skin, metal, cream, shirt and strap texel, and every texel outside the
declared boxes and hand-placed lists.

Run with the Codex-runtime Python (Pillow 12.3.0, NumPy 2.3.5), isolated mode:
  python -I <this script>                        # write PNG + manifest (refuses to change existing PNG bytes)
  python -I <this script> --out-dir <dir>        # determinism re-check into another folder
  python -I <this script> --qa-report <json>     # also embed Godot capture hashes in the manifest
  python -I <this script> --dump SRC|V8 x0 y0 x1 y1   # print a texel role map (review aid)
  python -I <this script> --preview <png> [--scale N] # v7 beside v8, nearest-neighbour enlarged (review aid)
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
SOURCE = PILOT_DIR / "rpg-2-star-ocean-the-second_protagonist-female_south-idle-selout-v7-slate-coat-candidate_m8-v07_20261015-015010-05615df5.png"
SOURCE_SHA256 = "4ada7df785a2a6fd19dea74b199f28d9d2101bfe75f306529412d17a4d5bb295"
PRESERVED = {
    "v6": (PILOT_DIR / "rpg-2-star-ocean-the-second_protagonist-female_south-idle-selout-v6-value-separation-candidate_m8-v06_20261015-010000-5a7d3f18.png",
           "f606afeb70e422b5f0c44373126a7112830e8ed47c22433b18255829fedd283b"),
    "v7_manifest": (PILOT_DIR / "rpg-2-star-ocean-the-second_protagonist-female_south-idle-selout-v7-slate-coat-manifest_m8-v07_20261015-015010-ed510f85.json",
                    "fbfd0be07475a843a0391c614a28cef7b42d2abdb0c90200ecc3db89c9afee5f"),
}
RUN = "m8-v08_20261015-021600"
OUTPUT = f"rpg-2-star-ocean-the-second_protagonist-female_south-idle-selout-v8-cloth-leather-candidate_{RUN}-157a5ea0.png"
MANIFEST = f"rpg-2-star-ocean-the-second_protagonist-female_south-idle-selout-v8-cloth-leather-manifest_{RUN}-2d6c5eff.json"

MAX_COLOURS = 32
CELL = (80, 112)
PIN = (40, 104)
FEET_ROWS = 6

# v7 roles (v6's 27 plus v7's four). v7 coat roles 1/2/3 keep their characters in v8 but
# take new colours (op 1); "4" (copper lapel trim) is unchanged.
V7_ROLES = [
    ("K", "0a0a0e"), ("k", "201c20"), ("O", "23252b"), ("T", "0a323b"), ("q", "302526"), ("G", "30333a"),
    ("b", "41302b"), ("t", "11525b"), ("n", "533b32"), ("y", "4a4749"), ("g", "474b54"), ("m", "634739"),
    ("L", "714730"), ("u", "1a767b"), ("l", "845436"), ("w", "7e5f4a"), ("z", "626873"), ("v", "249b98"),
    ("r", "a16f4b"), ("D", "bb7c50"), ("c", "b09986"), ("s", "e39664"), ("C", "d7c0a8"), ("B", "cfc8bd"),
    ("S", "fbc38d"), ("W", "faead4"), ("M", "9a4634"),
    ("1", "625c61"), ("2", "46424a"), ("3", "2d2c34"), ("4", "c07a40"),
]
# v8 role table: coat slots repurposed, two new trouser colours, y retired.
V8_COAT = {"1": "5e6e8c", "2": "3a4560", "3": "222839"}
V8_NEW = [
    ("1", "5e6e8c", "C1 coat lit, storm slate (repurposes v7 P1 #625c61)"),
    ("2", "3a4560", "C2 coat base, storm slate (repurposes v7 P2 #46424a)"),
    ("3", "222839", "C3 coat shadow and shared cloth deep (repurposes v7 P3 #2d2c34)"),
    ("5", "4a625c", "T1 trousers lit, spruce-grey (darker cut of the concept swatch #547b76)"),
    ("6", "324542", "T2 trousers base, spruce-grey"),
]
V8_ROLES = [(ch, V8_COAT.get(ch, h)) for ch, h in V7_ROLES if ch != "y"] + [(ch, h) for ch, h, _ in V8_NEW if ch in "56"]
SOURCE_ROLES = {ch for ch, _ in V7_ROLES}

# op 2: hand-placed coat clusters, (x, y) -> (expected v7 role, new role). Asserted.
COAT_CLUSTERS = {
    # Right (shadow-side) forearm x46-48, rows 42-52: v7 runs a 2-texel lit fold the full
    # length of the sleeve, as bright as the lit shoulder, so the shadow side had no shadow
    # mass. Below the shoulder cap the fold drops to base: the right sleeve reads as one
    # base/shadow group; its lit cap at rows 37-41 is kept.
    "right_forearm_fold_to_base": {(x, y): ("1", "2") for y in range(42, 53)
                                   for x in ((46, 47) if y <= 46 else (47, 48))},
    # Lit shoulder cluster on the light side: v7's rim narrows to 1 texel at rows 37-41; the
    # next texel inward (v7 base 2) joins it so the lit shoulder is a consistent 2-texel band.
    "left_shoulder_lit_widen": {(26, 37): ("2", "1"), (24, 40): ("2", "1"), (24, 41): ("2", "1")},
}
COAT_CLUSTER_TEXELS = {xy: v for g in COAT_CLUSTERS.values() for xy, v in g.items()}

# op 3: trouser area. Rows 61-84; the coat skirts, coat front edges (r), glove, knee pad and
# hanging strap are excluded by role (only v7 w/m/b/n change) and by the exclusion boxes.
TROUSER_BOXES = {
    "thighs_x27_43_y61_74": (27, 61, 43, 74),
    "right_outer_thigh_x46_51_y68_74": (46, 68, 51, 74),
    "left_shin_x26_36_y74_85": (26, 74, 36, 85),
    "right_shin_x38_50_y74_85": (38, 74, 50, 85),
}
TROUSER_EXCLUDE = {
    "right_glove_x47_53_y57_67": (47, 57, 53, 67),
}
TROUSER_MAP = {"w": "5", "m": "6", "b": "3", "n": "3"}
# Right leg: keep T1 lit only on its left (lit) side; v7 w at or right of this x per row band
# becomes T2 base.
RIGHT_LEG_LIT_MAX_X = [((61, 74), 40), ((74, 85), 43)]

# op 4: boots. Rows 85-102, both feet; one step down the existing warm leather ramp.
BOOT_BOXES = {
    "left_boot_x24_36_y85_103": (24, 85, 36, 103),
    "right_boot_x42_56_y85_103": (42, 85, 56, 103),
}
BOOT_MAP = {"l": "L", "L": "n", "n": "b", "b": "q", "m": "n"}
# Toe-cap / cuff highlight texels that keep v7's lit l (asserted to be l in v7).
BOOT_KEEP_LIT = {(27, 95), (28, 95), (27, 96), (28, 96), (49, 98), (50, 98), (49, 99), (50, 99)}

# op 5
PALETTE_MERGE = {"y": "g"}

N4 = [(-1, 0), (1, 0), (0, -1), (0, 1)]
N8 = N4 + [(-1, -1), (-1, 1), (1, -1), (1, 1)]


def sha256(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def hex_rgb(h):
    return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))


def role_of(px, table):
    if px[3] == 0:
        return "."
    key = "%02x%02x%02x" % tuple(int(v) for v in px[:3])
    for ch, h in table:
        if h == key:
            return ch
    return "?"


def role_grid(img, table):
    return [[role_of(img[y, x], table) for x in range(CELL[0])] for y in range(CELL[1])]


def box_mask(boxes, exclude=None):
    m = np.zeros(CELL[::-1], bool)
    for x0, y0, x1, y1 in boxes.values():
        m[y0:y1, x0:x1] = True
    for x0, y0, x1, y1 in (exclude or {}).values():
        m[y0:y1, x0:x1] = False
    return m


def right_leg_lit_limit(y):
    for (y0, y1), x in RIGHT_LEG_LIT_MAX_X:
        if y0 <= y < y1:
            return x
    return None


def apply_ops(src):
    """Every op reads v7 roles. Precedence: coat_cluster, then coat_storm_slate (roles 1-3),
    then trousers_spruce, boots_umber, palette_merge (their source roles are disjoint)."""
    roles = role_grid(src, V7_ROLES)
    if any(r not in SOURCE_ROLES | {"."} for row in roles for r in row):
        sys.exit("v7 contains a colour outside the v7 role table")
    op = src[..., 3] == 255
    for (x, y), (before, _) in COAT_CLUSTER_TEXELS.items():
        if roles[y][x] != before or not op[y, x]:
            sys.exit(f"coat cluster texel ({x},{y}) is v7 role {roles[y][x]}, expected {before}")
    for x, y in BOOT_KEEP_LIT:
        if roles[y][x] != "l":
            sys.exit(f"boot highlight texel ({x},{y}) is v7 role {roles[y][x]}, expected l")
    trousers = box_mask(TROUSER_BOXES, TROUSER_EXCLUDE)
    boots = box_mask(BOOT_BOXES)
    if (trousers & boots).any():
        sys.exit("trouser and boot boxes overlap")
    rmap = dict(V8_ROLES)
    out = src.copy()
    owner, after = {}, {}
    for y in range(CELL[1]):
        for x in range(CELL[0]):
            r = roles[y][x]
            new = None
            if (x, y) in COAT_CLUSTER_TEXELS:
                new, why = COAT_CLUSTER_TEXELS[(x, y)][1], "coat_cluster"
            elif r in V8_COAT:
                new, why = r, "coat_storm_slate"
            elif trousers[y, x] and r in TROUSER_MAP:
                new, why = TROUSER_MAP[r], "trousers_spruce"
                lim = right_leg_lit_limit(y)
                if new == "5" and x >= 37 and lim is not None and x >= lim:
                    new = "6"
            elif boots[y, x] and r in BOOT_MAP and (x, y) not in BOOT_KEEP_LIT:
                new, why = BOOT_MAP[r], "boots_umber"
            elif r in PALETTE_MERGE:
                new, why = PALETTE_MERGE[r], "palette_merge"
            if new is not None:
                out[y, x, :3] = hex_rgb(rmap[new])
                after[(x, y)] = new
                if (out[y, x] != src[y, x]).any():
                    owner[(x, y)] = why
    return out, owner, roles, after


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
    touched = {roles[y][x] for y, x in zip(*np.where(changed))}
    allowed = set(V8_COAT) | set(TROUSER_MAP) | set(BOOT_MAP) | set(PALETTE_MERGE)
    keep_roles = SOURCE_ROLES - allowed
    keep = np.array([[roles[y][x] in keep_roles for x in range(CELL[0])] for y in range(CELL[1])])
    return {
        "alpha_identical_everywhere": bool((out[..., 3] == src[..., 3]).all()),
        "rows_8_33_hair_ponytail_face_identical": bool((out[8:34] == src[8:34]).all()),
        "ink_teal_skin_metal_cream_shirt_strap_trim_texels_identical": bool((out[keep] == src[keep]).all()),
        "changes_only_from_declared_roles": touched <= allowed,
        "no_change_outside_coat_roles_trouser_boot_boxes_and_flask": bool(not (changed & ~(
            np.isin(np.array(roles), list(V8_COAT)) | box_mask(TROUSER_BOXES, TROUSER_EXCLUDE) | box_mask(BOOT_BOXES)
            | np.isin(np.array(roles), list(PALETTE_MERGE)))).any()),
        "only_v8_palette_colours": {role_of(p, V8_ROLES) for p in out.reshape(-1, 4) if p[3] == 255} <= {ch for ch, _ in V8_ROLES},
    }


def luma(rgb):
    rgb = np.asarray(rgb, float)
    return 0.299 * rgb[..., 0] + 0.587 * rgb[..., 1] + 0.114 * rgb[..., 2]


def region_metrics(img, mask):
    """Mean luma, luma steps, mean HSV saturation and the share of texels in the warm paving
    hue family (within 25 deg of 40 deg, saturation > 0.25), for the masked opaque texels."""
    m = mask & (img[..., 3] == 255)
    rgb = img[..., :3].astype(float)[m] / 255.0
    mx, mn = rgb.max(1), rgb.min(1)
    sat = np.where(mx > 0, (mx - mn) / np.maximum(mx, 1e-9), 0)
    d = np.maximum(mx - mn, 1e-9)
    r, g, b = rgb.T
    h = np.where(mx == r, ((g - b) / d) % 6, np.where(mx == g, (b - r) / d + 2, (r - g) / d + 4)) * 60
    L = luma(rgb * 255)
    return {"texels": int(m.sum()), "mean_luma": round(float(L.mean()), 2),
            "luma_steps": sorted({round(float(v), 1) for v in L}),
            "mean_hsv_saturation": round(float(sat.mean()), 3),
            "share_warm_paving_hue_family": round(float(((abs(h - 40) <= 25) & (sat > 0.25)).mean()), 4)}


def dump(img, table, x0, y0, x1, y1):
    print("    " + "".join(str(x // 10 % 10) for x in range(x0, x1)))
    print("    " + "".join(str(x % 10) for x in range(x0, x1)))
    for y in range(y0, y1):
        print("%3d " % y + "".join(role_of(img[y, x], table) for x in range(x0, x1)))


def preview(src, out, path, scale):
    """v7 | v8 side by side, nearest-neighbour enlarged on neutral grey (review aid; not an asset)."""
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
        sys.exit("v7 source SHA-256 mismatch")
    for name, (p, h) in PRESERVED.items():
        if sha256(p) != h:
            sys.exit(f"{name} SHA-256 mismatch (must stay preserved)")
    src = np.array(Image.open(SOURCE).convert("RGBA"))
    if args.dump and args.dump[0] == "SRC":
        dump(src, V7_ROLES, *map(int, args.dump[1:]))
        return
    out, owner, roles, after = apply_ops(src)
    if args.dump:
        dump(out, V8_ROLES, *map(int, args.dump[1:]))
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
    if sha256(SOURCE) != SOURCE_SHA256 or any(sha256(p) != h for p, h in PRESERVED.values()):
        sys.exit("a preserved source changed")
    fmt = lambda p: "#%02x%02x%02x" % tuple(int(v) for v in p[:3])
    changes = [{"x": int(x), "y": int(y), "op": owner[(int(x), int(y))], "role_before": roles[y][x],
                "role_after": after[(int(x), int(y))], "before": fmt(src[y, x]), "after": fmt(out[y, x])}
               for y, x in zip(*np.where((out != src).any(-1)))]
    per_op = {}
    for c in changes:
        per_op[c["op"]] = per_op.get(c["op"], 0) + 1
    role_arr = np.array(roles)
    coat_mask = np.isin(role_arr, list(V8_COAT))
    lower_mask = np.zeros(CELL[::-1], bool)
    for c in changes:
        if c["op"] in ("trousers_spruce", "boots_umber"):
            lower_mask[c["y"], c["x"]] = True
    metrics = {"coat (v7 roles 1/2/3)": {"v7": region_metrics(src, coat_mask), "v8": region_metrics(out, coat_mask)},
               "lower body recoloured (trousers + boots)": {"v7": region_metrics(src, lower_mask), "v8": region_metrics(out, lower_mask)}}
    qa = None
    if args.qa_report:
        rep = json.loads(args.qa_report.read_text(encoding="utf-8"))
        qa = {"report": args.qa_report.name, "report_sha256": sha256(args.qa_report),
              "captures": [{k: c.get(k) for k in ("scene", "variant", "capture", "capture_sha256", "capture_size",
                                                  "pilot_visible_logical", "pilot_window_diff_bounds_measured", "pilot_texel_fidelity")}
                           for c in rep["captures"]]}
    region_lists = {"coat": [[int(x), int(y)] for y, x in zip(*np.where(coat_mask))],
                    "trousers": sorted([c["x"], c["y"]] for c in changes if c["op"] == "trousers_spruce"),
                    "boots": sorted([c["x"], c["y"]] for c in changes if c["op"] == "boots_umber")}
    manifest = {
        "project": "Worlds Between",
        "milestone": "M8",
        "purpose": "Selout v8 cloth/leather hierarchy pass of the female south idle, answering Codex's v7 review (upper-coat shift subtle at full scale; lower body still merges with warm paving; v7 city minimum coat contrast below v6): cloth cool (storm-slate coat, spruce-grey trousers), leather warm (belt, straps, trims, boots one step deeper). Static frame only.",
        "status": "technical candidate; unapproved; not runtime-integrated; no animation",
        "art_approved": False,
        "human_reviewed": False,
        "runtime_integrated": False,
        "walk_frames": 0,
        "authorship": "Operations authored and run by Claude (Claude Code) in the workspace; previewed and checked in Godot before this manifest was written.",
        "source": {"role": "read-only input (selout v7), source-locked", "file": str(SOURCE.relative_to(ROOT)).replace("\\", "/"),
                   "sha256": SOURCE_SHA256,
                   "also_preserved": {k: {"file": str(p.relative_to(ROOT)).replace("\\", "/"), "sha256": h} for k, (p, h) in PRESERVED.items()}},
        "editor": {"script": "tools/" + Path(__file__).name, "script_sha256": sha256(__file__),
                   "python": platform.python_version(), "pillow": PIL.__version__, "numpy": np.__version__,
                   "run_flags": "-I (isolated)",
                   "method": "five texel-scoped recolour operations over v7 (coat_storm_slate, coat_cluster, trousers_spruce, boots_umber, palette_merge); recolour only; no resampling, quantizing, filtering, dithering or AI editing",
                   "pixel_editor_compatibility": "single 80x112 RGBA PNG, binary alpha, <=32 colours; opens as-is in Pixelorama 1.2.3 (work/tooling/pixelorama-1-2-3) for manual texel edits"},
        "operations": {
            "coat_storm_slate": {"roles_recoloured": {ch: {"v7": "#" + dict(V7_ROLES)[ch], "v8": "#" + h} for ch, h in V8_COAT.items()}},
            "coat_cluster": {name: [{"x": x, "y": y, "v7_role": b, "to": a} for (x, y), (b, a) in sorted(g.items())]
                             for name, g in COAT_CLUSTERS.items()},
            "trousers_spruce": {"map": TROUSER_MAP, "boxes": TROUSER_BOXES, "excluded": TROUSER_EXCLUDE,
                                "right_leg_lit_max_x": [{"rows": list(r), "w_at_or_right_of_x_becomes_T2": x} for r, x in RIGHT_LEG_LIT_MAX_X]},
            "boots_umber": {"map": BOOT_MAP, "boxes": BOOT_BOXES, "kept_lit_l": sorted(list(t) for t in BOOT_KEEP_LIT)},
            "palette_merge": {"map": PALETTE_MERGE, "from": "#4a4749", "to": "#474b54"},
        },
        "roles_v8": {ch: "#" + h for ch, h in V8_ROLES},
        "palette_changes": {"repurposed": {ch: use for ch, _, use in V8_NEW if ch in V8_COAT},
                            "new": {ch: {"hex": "#" + h, "use": use} for ch, h, use in V8_NEW if ch in "56"},
                            "retired": {"y": "#4a4749 (flask; merged into g #474b54)"},
                            "count_v7_to_v8": "31 -> 32"},
        "output": {"file": OUTPUT, "format": "PNG RGBA 8-bit, single image, no metadata chunks",
                   "bytes": path.stat().st_size, "sha256": sha256(path), "measured": m},
        "protected_invariants": prot,
        "region_metrics_v7_vs_v8": metrics,
        "qa_regions_texel_xy": region_lists,
        "pixel_changes": {"total": len(changes), "per_op": per_op, "texels": changes},
        "qa_captures": qa,
        "limitations": [
            "Static south idle only; no walk/turn frames; nothing wired into the runtime.",
            "Coat and trousers are now cool hues that the 21:9 concept does not use for cloth (its coat and trousers are warm grey-brown taupe); the spruce-grey is a darker cut of the concept's own #547b76 swatch, the slate is not from the concept. Identity is a human review call.",
            "The silhouette line is still v7's uniform K ink; no outline was added or thickened.",
            "Boots are one value step deeper than v7 (closer to the concept's dark boots); that is a darkening of the smallest region only.",
            "Visual approval remains human.",
        ],
    }
    (args.out_dir / MANIFEST).write_text(json.dumps(manifest, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"PNG {path} sha256={sha256(path)}")
    print(f"  size={m['size']} h={m['visible_body_height_texels']} w={m['visible_body_width_texels']} alpha={m['alpha_values_present']} "
          f"colours={m['unique_opaque_rgb_colours']} anchor={m['foot_anchor_lowest_row_and_feet_mid_x']} opaque={m['opaque_texels']}")
    print(f"  protected={prot}")
    print(f"  changes={len(changes)} per_op={per_op}")
    for k, v in metrics.items():
        print(f"  {k}: v7={v['v7']}")
        print(f"  {' ' * len(k)}  v8={v['v8']}")
    print(f"MANIFEST {args.out_dir / MANIFEST}")


if __name__ == "__main__":
    main()
