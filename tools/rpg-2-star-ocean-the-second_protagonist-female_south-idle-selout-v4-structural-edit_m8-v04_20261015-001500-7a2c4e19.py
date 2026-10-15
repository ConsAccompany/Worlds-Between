"""Female protagonist south idle, selout v4 structural static refinement (M8 v04), one frame.

Technical candidate only; unapproved; not used by the game runtime. No animation.
Input is the selout v3 candidate PNG (read-only, source-locked by SHA-256). Output is ONE
new PNG made by an explicit, hand-authored texel edit map over v3 - not a resize.

v3 kept v2's texel-scale mottling; v4 redraws by shape and value instead (light from the
upper left):
  torso y34-62  coat in three tones (b shadow / m base / w light); tan collar facings that
                give way to lit-cloth coat-front edges (x29, x38) below the collar; a clean
                cream shirt V (c/C/W) with one small lacing X; a 4x4 metal-framed teal
                badge; a pocket flap with a metal clasp; a 3-row main belt (lit top / mid /
                shadow) with its buckle and loop; a 2-row hip belt with buckle; two tapered
                shirt tails; sleeves with lit outer edges; a shaded cuff underside on the
                right arm; the hip canister restated as one 3-tone metal bottle.
Revision 2 (after the first --preview): front edges tan -> coat light 'w'; shirt tails split
from their first row and shaded; canister de-speckled. Nothing else changed.
  hair y8-12    the single up-left tuft spike ("horn") becomes a gathered fan of three tips
                with a V notch, still rising from the tie; the fall, its highlight path and
                the negative-space gap are unchanged. The top row stays y=8 (height 96), so
                the 48 px display keeps an exact 1 texel : 1 window px mapping.
Kept byte-identical to v3 (asserted): rows y13-33 (hair fall, face), every teal texel
except the redrawn badge (scarf, scarf tail, bedroll), the fist (x24-28 y42-46), the left
cuff (x18-24 y47-53), the right cuff band (x45-51 y53-55), the right-edge ink (x55
y41-56), x51-54 above and below the canister, and everything from y=63 down (glove, legs,
knee guard, boots, buckles).
Alpha changes are allowed only in y8-12 (the tuft); everywhere else this is recolour-only.

Run with the Codex-runtime Python (Pillow 12.3.0, NumPy 2.3.5), isolated mode:
  python -I <this script>                        # write PNG + manifest (refuses to change existing PNG bytes)
  python -I <this script> --out-dir <dir>        # determinism re-check into another folder
  python -I <this script> --qa-report <json>     # also embed Godot capture hashes in the manifest
  python -I <this script> --dump SRC|V4 x0 y0 x1 y1   # print a texel role map (review aid)
  python -I <this script> --preview <png> [--scale N] # v4 only, nearest-neighbour enlarged (review aid)
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
SOURCE = PILOT_DIR / "rpg-2-star-ocean-the-second_protagonist-female_south-idle-selout-v3-polish-candidate_m8-v03_20261014-234700-3c9a5d27.png"
SOURCE_SHA256 = "21b148cc026a70cdb173200c46cf007f83e4963cd7b7a7c71a174a7cb343cbc3"
PRESERVED = {
    "v2": (PILOT_DIR / "rpg-2-star-ocean-the-second_protagonist-female_south-idle-selout-v2-polish-candidate_m8-v02_20261014-233300-d2eeefa2.png",
           "4c8a720adc93c2bdbf2039da929f96eb617d4829ab35da2333105ac7d870e6f5"),
    "v1": (PILOT_DIR / "rpg-2-star-ocean-the-second_protagonist-female_south-idle-refine-selout-candidate_m8-v01_20261014-231100-4d141ad5.png",
           "7cb9f7044ed728894ab613725f0c6bdd876c29527e505b7f061689112da37f88"),
}
RUN = "m8-v04_20261015-001500"
OUTPUT = f"rpg-2-star-ocean-the-second_protagonist-female_south-idle-selout-v4-structural-candidate_{RUN}-e5b81f36.png"
MANIFEST = f"rpg-2-star-ocean-the-second_protagonist-female_south-idle-selout-v4-structural-manifest_{RUN}-0c9d3a74.json"

MAX_COLOURS = 32
CELL = (80, 112)
PIN = (40, 104)
FEET_ROWS = 6
ALPHA_EDIT_ROWS = range(8, 13)  # only the tuft may change silhouette

# Role letters -> RGB hex. All are existing v3 colours (no new colours in v4).
ROLES = [
    ("K", "0a0a0e"), ("k", "201c20"), ("O", "23252b"), ("T", "0a323b"), ("q", "302526"), ("G", "30333a"),
    ("b", "41302b"), ("t", "11525b"), ("n", "533b32"), ("y", "4a4749"), ("g", "474b54"), ("m", "634739"),
    ("L", "714730"), ("u", "1a767b"), ("l", "845436"), ("w", "7e5f4a"), ("z", "626873"), ("v", "249b98"),
    ("r", "a16f4b"), ("D", "bb7c50"), ("c", "b09986"), ("s", "e39664"), ("C", "d7c0a8"), ("B", "cfc8bd"),
    ("S", "fbc38d"), ("W", "faead4"), ("M", "9a4634"),
]
TEAL = {"T", "t", "u", "v"}
BADGE_BOX = (39, 43, 43, 47)  # x0, y0, x1, y1 exclusive: the only teal texels v4 may change

# (row, first column, map): '.' keeps the v3 texel, '_' makes it transparent, else a role.
EDITS = {
    # Tuft: three tips (x20-21 y10, x23-24 y8, x28-29 y8) with a V notch at x25-27 y8-9 and
    # a crease (x26 y10); bright 'r' sheen only on the left lock's outer edge, a diagonal 'm'
    # sheen on the right lock. Old apex texels (25,8) and (26,9) become transparent.
    "hair_tuft_fan": [
        (8, 23, "KK_..KK"),
        (9, 22, "KlnK_KmnK"),
        (10, 20, "KKrnbnKmnbnK"),
        (11, 19, "KlrnbnmbnmnbK"),
        (12, 19, "KlrnbnmnbnmqK"),
    ],
    # Left shoulder, lapel and sleeve. Lit 'w' on the shoulder and the sleeve's outer edge,
    # base 'm', shadow 'b' toward the fist; tan collar trim 'r' from (27,35) down to x29,
    # which then runs as the coat-front edge to the belt. The backpack strap 'l' emerges
    # under the lapel at y38 and runs into the fist (unchanged at x24-28 y42-46).
    "coat_left_upper": [
        (34, 26, "wwm"),
        (35, 25, "wwrmm"),
        (36, 25, "wwmrm"),
        (37, 23, "Kwwmmrm"),
        (38, 23, "Kwlmmmr"),
        (39, 23, "Kwllmmr"),
        (40, 22, "Kwmllmmr"),
        (41, 22, "Kwmllmmrb"),
        (42, 21, "Kwm"),
        (43, 21, "Kwm"),
        (44, 20, "Kwmb"),
        (45, 19, "Kwmmb"),
        (46, 18, "Kwwmmb"),
    ],
    # Right shoulder and collar: trim 'r' diagonal (44,34)->(39,41) meeting the vertical
    # front edge at x38; lit 'w' beside the trim; strap 'l' over the right shoulder (x43-44
    # y37-40); 'b' contour where the arm meets the body (x45).
    "coat_right_upper": [
        (34, 41, "m..r"),
        (35, 41, "m.rmbb"),
        (36, 41, "wrmml"),
        (37, 40, "mrwllmm"),
        (38, 40, "mrwllmw"),
        (39, 40, "rmwllmw"),
        (40, 39, "mrwwllbw"),
        (41, 39, "rwwmmmbwwmnn"),
    ],
    # Chest to waist, x25-50 (fist, left cuff and scarf teal kept). Revision 2: below the
    # collar the coat-front edges (x29 left, x38 right) are the coat-light tone 'w' instead of
    # tan 'r' - tan now stays on the collar facings only, as in the reference, so the edges
    # read as lit cloth rather than two ruled lines; x39 beside the right edge drops to 'm' so
    # the edge stays one texel wide. Left coat panel b/m/m; shirt c|C/W|c with a lacing X
    # (x33-35 y46-48); right panel m base, b fold under the badge; badge 4x4 (B frame,
    # v/u/t centre); pocket flap L with clasp B (x41-43 y48-49); arm contour b at x45; sleeve
    # lit band (x46-47, moving to x47-48 from y47), shade x49-50.
    "torso_chest_waist": [
        (42, 29, "wc"),
        (42, 38, "wmmmmmmbwwmbb"),
        (43, 29, "wcC"),
        (43, 36, "ccwmBBmmmbwwmtb"),
        (44, 29, "wcCC"),
        (44, 35, "cCcwBvuBmbbwwmtb"),
        (45, 29, "wcWWCCCCcwButBmbbwwmtb"),
        (46, 29, "wcWWlClCcwmBBmmmbwwmbb"),
        (47, 25, "bbmmwcWCClCCcwmmmmmmbmwwmb"),
        (48, 26, "bmmwcCClClCcwmmLLLbbmwwmb"),
        (49, 26, "bmmwcCCCCCccwmmlBlbbmwwmb"),
        (50, 26, "bmmwcCWCCCccwmmmmmmbmwwmb"),
        (51, 27, "bmwcCCCCCccwmmmmmmbmwwmm"),
        (52, 27, "bmwcCCCccccwmbbmmm.mwwm"),
        (53, 28, "bwccccccccwmmmmm"),
    ],
    # Canister on the right hip (x51-54 y44-52), revision 2: v3's scattered cream/grey dots
    # become one readable metal bottle - dark cap (y44, y46 neck) with a lit cap face (y45),
    # a 3-tone body (B lit left / c mid / z shade right, y47-51), dark base (y52) - with an
    # ink seam x51 against the sleeve. Same position and size; the right-edge ink x55 and the
    # cuff (y53-55) are untouched.
    "canister": [
        (44, 51, "byy"),
        (45, 51, "bzB"),
        (46, 51, "byy"),
        (47, 51, "KBcz"),
        (48, 51, "KBcz"),
        (49, 51, "KBcz"),
        (50, 51, "KBcz"),
        (51, 51, "KBcz"),
        (52, 51, "Kyyy"),
    ],
    # Main belt (y54-56): lit top 'l', mid 'L', shadow 'b'; buckle B ring with K hole kept at
    # x32-34, small loop B at (38,55); belt spans x30-40 between the coat-front edges. Right
    # cuff underside shaded 'c' (y56 x47-50) to separate it from the forearm skin.
    # Hip belt (y57-58): 2-row band l/L across x25-40 with a 2x2 metal buckle at x33-34.
    "belts": [
        (54, 28, "bwllBBBllllll"),
        (55, 28, "mwLLBKBLLLBLL"),
        (56, 28, "mwbbBBBbbbbbb"),
        (56, 47, "cccc"),
        (57, 25, "llllllllBBlllllL"),
        (58, 25, "LLLLLLLLBBLLLLLL"),
    ],
    # Shirt tails (y59-62), revision 2: v4r1 started with one solid 8-wide cream row that
    # joined both tails into a block. Now the dark trouser gap (x34-35) starts at y59, each
    # tail carries one or two lit texels only, and shade 'c' wraps the outer and lower edges
    # so they taper: left tail x31-33 ending at y61, right tail x36-40 ending at y62.
    "shirt_tails": [
        (59, 31, "CWCmbCCc"),
        (60, 30, "cCCcbmCWCcc"),
        (61, 30, "ccmmwwmcCCcc"),
        (62, 37, "ccCc"),
    ],
}
SPECKLE_BOXES = {
    "torso_x18_55_y34_62": (18, 34, 56, 63),
    "left_coat_x18_29_y34_53": (18, 34, 30, 54),
    "shirt_x30_37_y42_53": (30, 42, 38, 54),
    "right_coat_x38_50_y34_53": (38, 34, 51, 54),
    "hair_tuft_x17_33_y8_14": (17, 8, 34, 15),
    "canister_x51_54_y44_52": (51, 44, 55, 53),
}

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
                if y not in ALPHA_EDIT_ROWS and (ch == "_" or src[y, x, 3] != 255):
                    sys.exit(f"edit at {(x, y)} in {region} would change alpha outside rows {ALPHA_EDIT_ROWS.start}-{ALPHA_EDIT_ROWS.stop - 1}")
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
    teal_src = np.array([[role_of(src[y, x]) in TEAL for x in range(CELL[0])] for y in range(CELL[1])])
    bx0, by0, bx1, by1 = BADGE_BOX
    teal_src[by0:by1, bx0:bx1] = False
    alpha_outside = np.ones(CELL[1], bool)
    alpha_outside[list(ALPHA_EDIT_ROWS)] = False
    return {
        "rows_13_33_hair_fall_and_face_identical": bool((out[13:34] == src[13:34]).all()),
        "rows_63_and_below_identical": bool((out[63:] == src[63:]).all()),
        "teal_texels_identical_except_badge": bool((out[teal_src] == src[teal_src]).all()),
        "fist_x24_28_y42_46_identical": bool((out[42:47, 24:29] == src[42:47, 24:29]).all()),
        "left_cuff_x18_24_y47_53_identical": bool((out[47:54, 18:25] == src[47:54, 18:25]).all()),
        "right_cuff_x45_51_y53_55_identical": bool((out[53:56, 45:52] == src[53:56, 45:52]).all()),
        "right_edge_ink_x55_y41_56_identical": bool((out[41:57, 55] == src[41:57, 55]).all()),
        "x51_54_outside_canister_y41_43_and_y53_56_identical": bool(
            (out[41:44, 51:55] == src[41:44, 51:55]).all() and (out[53:57, 51:55] == src[53:57, 51:55]).all()),
        "alpha_identical_outside_rows_8_12": bool((out[alpha_outside, :, 3] == src[alpha_outside, :, 3]).all()),
    }


def dump(img, x0, y0, x1, y1):
    print("    " + "".join(str(x // 10 % 10) for x in range(x0, x1)))
    print("    " + "".join(str(x % 10) for x in range(x0, x1)))
    for y in range(y0, y1):
        print("%3d " % y + "".join(role_of(img[y, x]) for x in range(x0, x1)))


def preview(out, path, scale):
    """v4 alone, nearest-neighbour enlarged on neutral grey (review aid; not a sheet)."""
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
        sys.exit("v3 source SHA-256 mismatch")
    for name, (p, h) in PRESERVED.items():
        if sha256(p) != h:
            sys.exit(f"{name} SHA-256 mismatch (must stay preserved)")
    src = np.array(Image.open(SOURCE).convert("RGBA"))
    out, owner = apply_edits(src)
    if args.dump:
        dump(src if args.dump[0] == "SRC" else out, *map(int, args.dump[1:]))
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
    speck = {name: {"v3": speckle(src, box), "v4": speckle(out, box)} for name, box in SPECKLE_BOXES.items()}
    v3_colours = sorted({role_of(p) for p in src.reshape(-1, 4) if p[3] == 255})
    v4_colours = sorted({role_of(p) for p in out.reshape(-1, 4) if p[3] == 255})
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
        "purpose": "Selout v4 structural static refinement of the female south idle: torso y34-62 redrawn as coherent value groups and the ponytail tuft reshaped from a single spike into a gathered fan. Static frame only.",
        "status": "technical candidate; unapproved; not runtime-integrated; no animation",
        "art_approved": False,
        "human_reviewed": False,
        "runtime_integrated": False,
        "walk_frames": 0,
        "authorship": "Edit map authored by Claude with file edits only (no execution); the script is run by Codex in the workspace.",
        "source": {"role": "read-only input (selout v3), source-locked", "file": str(SOURCE.relative_to(ROOT)).replace("\\", "/"),
                   "sha256": SOURCE_SHA256,
                   "also_preserved": {k: {"file": str(p.relative_to(ROOT)).replace("\\", "/"), "sha256": h} for k, (p, h) in PRESERVED.items()}},
        "editor": {"script": "tools/" + Path(__file__).name, "script_sha256": sha256(__file__),
                   "python": platform.python_version(), "pillow": PIL.__version__, "numpy": np.__version__,
                   "run_flags": "-I (isolated)",
                   "method": "explicit texel map (EDITS) over v3; alpha edits only in y8-12; no resampling, quantizing, filtering or AI editing"},
        "roles": {ch: "#" + h for ch, h in ROLES},
        "new_colours": [],
        "roles_present_v3": v3_colours,
        "roles_present_v4": v4_colours,
        "edit_map": {region: [{"row": y, "x0": x0, "map": spec} for y, x0, spec in rows] for region, rows in EDITS.items()},
        "output": {"file": OUTPUT, "format": "PNG RGBA 8-bit, single image, no metadata chunks",
                   "bytes": path.stat().st_size, "sha256": sha256(path), "measured": m},
        "protected_invariants": prot,
        "speckle_v3_vs_v4": speck,
        "pixel_changes": {"total": len(changes), "per_region": per_region, "texels": changes},
        "qa_captures": qa,
        "limitations": [
            "Static south idle only; no walk/turn frames; nothing wired into the runtime.",
            "The map was authored from texel role dumps without Claude seeing the v4 result; it needs visual review (preview and Godot captures) and likely another revision round.",
            "The torso is a stylised re-statement of the reference (tan collar facings, lit-cloth front edges, single lacing X, simplified pocket, belts and canister); small reference details such as extra straps, stitching and the lower hip pouch are simplified or left as v3 texture.",
            "Revision 2 was made from one 8x --preview read; the front-edge, shirt-tail and canister changes have not been seen rendered yet.",
            "The tuft fan still sits on top of the large viewer-left ponytail arc; at 48 px the overall hair mass remains the dominant, heavy shape.",
            "The backpack strap over the left shoulder now emerges under the lapel at y38 instead of crossing the collar.",
            "The lower-left coat skirt/pouch block (x22-29 y59-62) and the trousers keep v3 texture.",
            "The tuft keeps its top at y8 so the height stays 96; the fan is limited to rows 8-12 and the tie at (29-30,14) is unchanged.",
            "Visual approval remains human.",
        ],
    }
    (args.out_dir / MANIFEST).write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    print(f"PNG {path} sha256={sha256(path)}")
    print(f"  size={m['size']} h={m['visible_body_height_texels']} w={m['visible_body_width_texels']} alpha={m['alpha_values_present']} "
          f"colours={m['unique_opaque_rgb_colours']} anchor={m['foot_anchor_lowest_row_and_feet_mid_x']}")
    print(f"  protected={prot}")
    print(f"  changes={len(changes)} per_region={per_region}")
    for name, s in speck.items():
        print(f"  speckle {name}: v3 {s['v3']['speckle']}/{s['v3']['opaque']} -> v4 {s['v4']['speckle']}/{s['v4']['opaque']}")
    print(f"MANIFEST {args.out_dir / MANIFEST}")


if __name__ == "__main__":
    main()
