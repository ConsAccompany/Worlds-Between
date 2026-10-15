"""Female protagonist south idle, selout v3 static polish (M8 v03), single frame.

Technical candidate only; unapproved; not used by the game runtime. No animation.
Input is the selout v2 candidate PNG (read-only, byte-preserved). Output is ONE new PNG
made by an explicit, hand-authored texel edit map applied on top of v2 - not a resize.
Edits are recolour-only (alpha unchanged) with existing v2 colours: right coat panel and
sleeve re-clustered into light/mid/shade bands, left coat strip de-inked, hip-belt and trim
specks removed, trousers under the shirt tails consolidated, the viewer-right glove turned
from a near-black block into warm leather, and a small face legibility pass. Hair/ponytail,
scarf and everything from y=66 down are asserted identical to v2.

Run with the Codex-runtime Python (Pillow 12.3.0, NumPy 2.3.5), isolated mode:
  python -I <this script>                      # write PNG + manifest (refuses to change existing PNG bytes)
  python -I <this script> --out-dir <dir>      # determinism re-check into another folder
  python -I <this script> --qa-report <json>   # also embed Godot capture hashes in the manifest
  python -I <this script> --dump SRC|V3 x0 y0 x1 y1   # print a texel role map (review aid)
  python -I <this script> --preview <png>      # write a nearest-neighbour review sheet (review aid)
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
SOURCE = PILOT_DIR / "rpg-2-star-ocean-the-second_protagonist-female_south-idle-selout-v2-polish-candidate_m8-v02_20261014-233300-d2eeefa2.png"
SOURCE_SHA256 = "4c8a720adc93c2bdbf2039da929f96eb617d4829ab35da2333105ac7d870e6f5"
V1 = PILOT_DIR / "rpg-2-star-ocean-the-second_protagonist-female_south-idle-refine-selout-candidate_m8-v01_20261014-231100-4d141ad5.png"
V1_SHA256 = "7cb9f7044ed728894ab613725f0c6bdd876c29527e505b7f061689112da37f88"
RUN = "m8-v03_20261014-234700"
OUTPUT = f"rpg-2-star-ocean-the-second_protagonist-female_south-idle-selout-v3-polish-candidate_{RUN}-3c9a5d27.png"
MANIFEST = f"rpg-2-star-ocean-the-second_protagonist-female_south-idle-selout-v3-polish-manifest_{RUN}-b47e2c10.json"

MAX_COLOURS = 32
CELL = (80, 112)
PIN = (40, 104)
FEET_ROWS = 6

# Role letters -> RGB hex. All are v2 colours unless marked new.
ROLES = [
    ("K", "0a0a0e"), ("k", "201c20"), ("O", "23252b"), ("T", "0a323b"), ("q", "302526"), ("G", "30333a"),
    ("b", "41302b"), ("t", "11525b"), ("n", "533b32"), ("y", "4a4749"), ("g", "474b54"), ("m", "634739"),
    ("L", "714730"), ("u", "1a767b"), ("l", "845436"), ("w", "7e5f4a"), ("z", "626873"), ("v", "249b98"),
    ("r", "a16f4b"), ("D", "bb7c50"), ("c", "b09986"), ("s", "e39664"), ("C", "d7c0a8"), ("B", "cfc8bd"),
    ("S", "fbc38d"), ("W", "faead4"), ("M", "9a4634"),
]

# (row, first column, map): '.' keeps the v2 texel, '_' makes it transparent, else a role.
# Every edit below recolours an opaque texel to another opaque existing v2 colour; no alpha
# changes, so the silhouette, height, foot anchor and palette size cannot grow.
EDITS = {
    # Face, read at 1 texel = 1 screen px. Soft cast shadow under the bangs (row 27, the
    # parting at x 35-36 stays lit); lash flicks at (31,28)/(39,28) removed so each eye reads
    # as a vertical dark mark instead of a horizontal bar; pupils pure ink; mouth 2 texels.
    "face": [
        (27, 33, "ss..sss"),
        (28, 31, "S.......s"),
        (29, 33, "K...K"),
        (33, 34, "M"),
    ],
    # Viewer-right glove (x 48-51 inside the v2 outline): v2 was k/q/b near-black. Now a warm
    # leather cuff band (L r l L), lit glove back (m/l top-left), shade toward the right (n/b),
    # and a darker knuckle row above the skin fingers. The x 47/52 ink outline is kept so the
    # hand still separates from the coat.
    "glove": [
        (61, 47, ".LrlL."),
        (62, 47, ".mlmn."),
        (63, 47, ".mmnb."),
        (64, 47, ".nmnb."),
        (65, 47, ".bnbb."),
    ],
    # Right coat panel + upper sleeve (x 43-50). v2 mixed m/w/n/b/D texel by texel. Now:
    # x43 lapel-side coat 'm', x44 coat shade 'n', x45 'b' contour between body and arm,
    # x46-47 lit sleeve 'w' band (shifting to x47-48 from y47 as the arm hangs), x48 'm',
    # x49-50 sleeve shade 'n' (the teal strap texels at x49 y43-45 are kept), and a 2x2
    # fold shadow 'bb' under the chest badge (x44-45 y44-45). The pocket clasp (x43-44 y48)
    # and leather pocket flap (x43-44 y50-51) are kept.
    "coat_right_panel": [
        (41, 43, "mnbwwmnn"),
        (42, 43, "mnbwwmnn"),
        (43, 43, "mnbwwmtb"),
        (44, 43, "mbbwwmtb"),
        (45, 43, "mbbwwmtb"),
        (46, 43, "mnbwwmnn"),
        (47, 43, "mnbmwwmn"),
        (48, 43, "..bnwwmn"),
        (49, 43, "nmbmwwmn"),
        (50, 43, "..bmwwmn"),
        (51, 43, "..bmwwmm"),
    ],
    # Left coat strip between the cuff and the shirt (x 26-30, y 48-51): v2 had two parallel
    # ink lines (x27 and x29) plus a stray ink texel at (30,49). x29 stays the coat-front edge;
    # x26-28 become coat cloth (b/n/m), the stray ink becomes shirt shade 'c'.
    "coat_left_strip": [
        (48, 27, "m"),
        (49, 27, "m..c"),
        (50, 26, "bn"),
        (51, 27, "b"),
    ],
    # Hip belt and front trim specks: single cream/dark texels inside the leather band and an
    # isolated skin-tone texel in the right front trim become the surrounding leather.
    "lower_coat_specks": [
        (57, 29, "l.......l"),
        (58, 38, "l"),
        (59, 28, "l"),
        (62, 43, "r"),
    ],
    # Trousers just below the shirt tails (x 28-42, y 63-65): lit left leg 'w', centre
    # shade 'm' with the seam 'b' at x34 leading into the existing crotch shadow (y66+), a
    # one-row cast shadow 'm' under the right shirt tail (y63 x34-40), then the lit right leg
    # 'w' with 'm' toward the coat trim. Rows 66-70 are already clustered and stay as in v2.
    "trousers": [
        (63, 28, "wwwwmmmmmmmmmnn"),
        (64, 28, "wwwwwmbmmwwwwml"),
        (65, 28, "wwwwmmbnmmwwwml"),
    ],
}
# Regions that must stay byte-identical to v2 (asserted): hair/ponytail rows, scarf, and
# everything from y=66 down (fingers, legs, knee guard, boots, buckles).
PROTECT = {
    "hair_and_ponytail_rows_8_26": (slice(8, 27), slice(0, 80)),
    "scarf_x29_40_y34_44": (slice(34, 45), slice(29, 41)),
    "rows_66_and_below": (slice(66, 112), slice(0, 80)),
}
SPECKLE_BOXES = {
    "right_coat_panel_x43_50_y41_51": (43, 41, 51, 52),
    "left_coat_strip_x26_30_y47_52": (26, 47, 31, 53),
    "trousers_x28_42_y63_65": (28, 63, 43, 66),
    "glove_x48_51_y61_65": (48, 61, 52, 66),
    "torso_x18_55_y34_71": (18, 34, 56, 72),
}

N4 = [(-1, 0), (1, 0), (0, -1), (0, 1)]
N8 = N4 + [(-1, -1), (-1, 1), (1, -1), (1, 1)]


def roles():
    return dict(ROLES)


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


def apply_edits(src):
    out = src.copy()
    owner = {}
    rmap = roles()
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
                # v3 only recolours: an edit landing on a transparent v2 texel means the map
                # is misaligned, so stop rather than grow the silhouette.
                if src[y, x, 3] != 255:
                    sys.exit(f"edit at {(x, y)} in {region} targets a transparent v2 texel")
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
    n = 0
    tot = 0
    for y in range(y0, y1):
        for x in range(x0, x1):
            if not op[y, x]:
                continue
            tot += 1
            same = False
            for dy, dx in N8:
                yy, xx = y + dy, x + dx
                if op[yy, xx] and (img[yy, xx, :3] == img[y, x, :3]).all():
                    same = True
                    break
            n += 0 if same else 1
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
        "foot_anchor_source": list(feet_anchor(src[..., 3] == 255)),
        "knee_guard_block_x26_32_y74_79_identical_to_v2": bool((out[knee] == src[knee]).all()),
        "isolated_opaque_texels_8n": isolated,
        "transparent_pinholes_4n": pinholes,
    }


def dump(img, x0, y0, x1, y1):
    print("    " + "".join(str(x // 10 % 10) for x in range(x0, x1)))
    print("    " + "".join(str(x % 10) for x in range(x0, x1)))
    for y in range(y0, y1):
        print("%3d " % y + "".join(role_of(img[y, x]) for x in range(x0, x1)))


def preview(src, out, path):
    """v2 | v3 at 8x on grey, then 1x and 2x on light and dark grounds (review aid only)."""
    sc = 8
    w, h = CELL[0] * sc, CELL[1] * sc
    sheet = Image.new("RGBA", (2 * w + 30 + 2 * 170, h + 20), (50, 50, 50, 255))
    for n, img in enumerate((src, out)):
        im = Image.fromarray(img, "RGBA")
        bg = Image.new("RGBA", (w, h), (150, 150, 150, 255))
        bg.alpha_composite(im.resize((w, h), Image.NEAREST))
        sheet.alpha_composite(bg, (10 + n * (w + 10), 10))
        for k, col in enumerate(((196, 176, 146, 255), (30, 40, 46, 255))):
            g = Image.new("RGBA", CELL, col)
            g.alpha_composite(im)
            sheet.alpha_composite(g.resize((160, 224), Image.NEAREST), (2 * w + 30 + n * 170, 10 + k * 232))
            sheet.alpha_composite(g, (2 * w + 30 + n * 170, 480 + k * 120))
    sheet.save(path)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out-dir", type=Path, default=PILOT_DIR)
    ap.add_argument("--qa-report", type=Path)
    ap.add_argument("--dump", nargs=5)
    ap.add_argument("--preview", type=Path)
    args = ap.parse_args()
    if sha256(SOURCE) != SOURCE_SHA256 or sha256(V1) != V1_SHA256:
        sys.exit("source SHA-256 mismatch (v2 or v1 changed)")
    src = np.array(Image.open(SOURCE).convert("RGBA"))
    out, owner = apply_edits(src)
    if args.dump:
        dump(src if args.dump[0] == "SRC" else out, *map(int, args.dump[1:]))
        return
    if args.preview:
        preview(src, out, args.preview)
        print("PREVIEW", args.preview)
        return
    m = checks(src, out)
    protected = {name: bool((out[box] == src[box]).all()) for name, box in PROTECT.items()}
    ok = (m["size"] == list(CELL) and m["alpha_values_present"] == [0, 255] and m["partial_alpha_texels"] == 0
          and m["transparent_texels_with_nonzero_rgb"] == 0 and m["visible_body_height_texels"] == 96
          and m["unique_opaque_rgb_colours"] <= MAX_COLOURS and m["opaque_texels_on_cell_border"] == 0
          and m["foot_anchor_lowest_row_and_feet_mid_x"] == m["foot_anchor_source"] == [PIN[1] - 1, PIN[0]]
          and m["knee_guard_block_x26_32_y74_79_identical_to_v2"] and not m["isolated_opaque_texels_8n"]
          and not m["transparent_pinholes_4n"] and all(protected.values())
          and bool((out[..., 3] == src[..., 3]).all()))
    if not ok:
        print(json.dumps({"checks": {k: v for k, v in m.items() if k != "palette_hex"}, "protected": protected}, indent=1))
        sys.exit("integrity check failed")
    args.out_dir.mkdir(parents=True, exist_ok=True)
    path = args.out_dir / OUTPUT
    tmp = path.with_suffix(".tmp.png")
    Image.fromarray(out, "RGBA").save(tmp, optimize=False, compress_level=9)
    if path.exists() and path.read_bytes() != tmp.read_bytes():
        tmp.unlink()
        sys.exit(f"refusing to change existing bytes of {path.name}")
    tmp.replace(path)
    if sha256(SOURCE) != SOURCE_SHA256 or sha256(V1) != V1_SHA256:
        sys.exit("v2 or v1 bytes changed")
    fmt = lambda p: "transparent" if p[3] == 0 else "#%02x%02x%02x" % tuple(int(v) for v in p[:3])
    changes = [{"x": int(x), "y": int(y), "region": owner[(int(x), int(y))], "before": fmt(src[y, x]), "after": fmt(out[y, x])}
               for y, x in zip(*np.where((out != src).any(-1)))]
    no_op = sorted(f"{x},{y}" for (x, y) in owner if (out[y, x] == src[y, x]).all())
    per_region = {}
    for c in changes:
        per_region[c["region"]] = per_region.get(c["region"], 0) + 1
    speck = {name: {"v2": speckle(src, box), "v3": speckle(out, box)} for name, box in SPECKLE_BOXES.items()}
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
        "purpose": "Selout v3 static polish of the female south idle: cleaner coat panels, a glove that no longer reads as a dark block, and a small face legibility pass at 48 logical px. Static frame only.",
        "status": "technical candidate; unapproved; not runtime-integrated; no animation",
        "art_approved": False,
        "runtime_integrated": False,
        "walk_frames": 0,
        "authorship": "Edit map authored by Claude (file edits only); the script is executed by Codex in the workspace.",
        "source": {"role": "read-only input (selout v2); bytes re-verified after writing",
                   "file": str(SOURCE.relative_to(ROOT)).replace("\\", "/"), "sha256": SOURCE_SHA256,
                   "also_preserved": {"file": str(V1.relative_to(ROOT)).replace("\\", "/"), "sha256": V1_SHA256}},
        "editor": {"script": "tools/" + Path(__file__).name, "script_sha256": sha256(__file__),
                   "python": platform.python_version(), "pillow": PIL.__version__, "numpy": np.__version__,
                   "run_flags": "-I (isolated)",
                   "method": "explicit texel recolour map (EDITS) over v2; recolour-only (alpha unchanged); no resampling, quantizing, filtering or AI editing"},
        "roles": {ch: "#" + h for ch, h in ROLES},
        "new_colours": [],
        "edit_map": {region: [{"row": y, "x0": x0, "map": spec} for y, x0, spec in rows] for region, rows in EDITS.items()},
        "output": {"file": OUTPUT, "format": "PNG RGBA 8-bit, single image, no metadata chunks",
                   "bytes": path.stat().st_size, "sha256": sha256(path), "measured": m},
        "protected_regions_identical_to_v2": protected,
        "alpha_identical_to_v2": True,
        "speckle_v2_vs_v3": speck,
        "pixel_changes": {"total": len(changes), "per_region": per_region,
                          "mapped_but_unchanged_texels": no_op, "texels": changes},
        "qa_captures": qa,
        "limitations": [
            "Static south idle only; no walk/turn frames; nothing wired into the runtime.",
            "The edit map was authored from texel role dumps without Claude rendering or viewing the v3 result; visual review of the Godot captures is required before any further judgement.",
            "Coat clean-up covers the right coat panel/sleeve (x43-50 y41-51), the left strip beside the shirt (x26-30 y48-51), hip-belt specks and trousers y63-65; the left shoulder/strap area, shirt lacing and the lower coat skirts keep v2 texture.",
            "The right sleeve is restated as a lit vertical band with a dark body/arm contour; this is an interpretation of the reference's shading, not a measurement.",
            "Face changes are deliberately small (bang shadow, flicks removed, pure-ink pupils, 2-texel mouth); the mouth may read slightly heavier when zoomed even though it targets 1x legibility.",
            "Hair, ponytail, scarf, knee guard, legs, boots and buckles are asserted byte-identical to v2.",
            "Visual approval remains human.",
        ],
    }
    (args.out_dir / MANIFEST).write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    print(f"PNG {path} sha256={sha256(path)}")
    print(f"  size={m['size']} h={m['visible_body_height_texels']} w={m['visible_body_width_texels']} alpha={m['alpha_values_present']} "
          f"colours={m['unique_opaque_rgb_colours']} anchor={m['foot_anchor_lowest_row_and_feet_mid_x']} protected={protected}")
    print(f"  changes={len(changes)} per_region={per_region} mapped_but_unchanged={len(no_op)}")
    for name, s in speck.items():
        print(f"  speckle {name}: v2 {s['v2']['speckle']}/{s['v2']['opaque']} -> v3 {s['v3']['speckle']}/{s['v3']['opaque']}")
    print(f"MANIFEST {args.out_dir / MANIFEST}")


if __name__ == "__main__":
    main()
