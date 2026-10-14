"""Deterministic south-idle quantized downscale experiment (female protagonist, M8 v01).

Technical experiment only. Output is unapproved and not used by the game runtime.
Two standalone candidates are made from the read-only premium south concept:
  boxquant      premultiplied BOX (area average) resize
  lanczosquant  premultiplied LANCZOS resize
Both then get binary alpha (>=128 -> 255, else 0), a <=48 colour median-cut palette
(no dither) built from that candidate's opaque texels, and placement on an 80x112
cell with the feet midpoint on ground pin (40,104). No hand edits, no AI pixels.

Run with the Codex-runtime Python (Pillow 12.3.0, NumPy 2.3.5), isolated mode:
  python -I <this script>                      # write PNGs + manifest (refuses to change existing PNG bytes)
  python -I <this script> --out-dir <tmp>      # determinism re-check into another folder
  python -I <this script> --qa-capture boxquant=<png> --qa-capture lanczosquant=<png>
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
SOURCE = ROOT / "game/assets/characters/high-fidelity-prototypes/rpg-2-star-ocean-the-second_protagonist-female_south-exploration-premium-pixel_m8-concept_20261014-145800-62c3a10f.png"
SOURCE_SHA256 = "28f9efacce914fa232f6dbc99b063e68e0bce25f4162c9f70eb62ffdfc2fb222"
PILOT_DIR = ROOT / "game/assets/characters/pixelorama-pilots"
PRIOR_MANIFEST = "rpg-2-star-ocean-the-second_protagonist-female_south-idle-pixelorama-pilot-manifest_m8-v01_20261014-211454-868681b7.json"
MANIFEST_NAME = "rpg-2-star-ocean-the-second_protagonist-female_south-idle-quantized-downscale-manifest_m8-v01_20261014-212322-aa446773.json"
VARIANTS = {
    "boxquant": {
        "file": "rpg-2-star-ocean-the-second_protagonist-female_south-idle-boxquant-pilot_m8-v01_20261014-212322-7c30d48c.png",
        "resample": Image.Resampling.BOX,
        "resample_name": "BOX",
    },
    "lanczosquant": {
        "file": "rpg-2-star-ocean-the-second_protagonist-female_south-idle-lanczosquant-pilot_m8-v01_20261014-212322-b9fd58f7.png",
        "resample": Image.Resampling.LANCZOS,
        "resample_name": "LANCZOS",
    },
}

CROP_ALPHA = 128
BODY_HEIGHT = 96
CELL = (80, 112)
PIN = (40, 104)
ALPHA_CUT = 128
COLOURS = 48
KMEANS_PASSES = 3
FEET_ROWS = 6


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def crop_box(source: np.ndarray) -> tuple[tuple[float, float, float, float], int, dict]:
    ys, xs = np.nonzero(source[..., 3] >= CROP_ALPHA)
    x0, x1, y0, y1 = int(xs.min()), int(xs.max()) + 1, int(ys.min()), int(ys.max()) + 1
    step = (y1 - y0) / BODY_HEIGHT
    width = int(np.ceil((x1 - x0) / step))
    centre = (x0 + x1) / 2
    box = (centre - width * step / 2, float(y0), centre + width * step / 2, float(y1))
    facts = {
        "strong_alpha_threshold": CROP_ALPHA,
        "strong_alpha_bounds_xyxy_exclusive": [x0, y0, x1, y1],
        "strong_alpha_size": [x1 - x0, y1 - y0],
        "source_px_per_texel": step,
        "resize_box_xyxy": list(box),
        "resize_box_note": "Height is exactly the strong-alpha bounds; width is widened symmetrically to a whole number of texels at the same step (no trim, no aspect change).",
    }
    return box, width, facts


def quantize(rgba: np.ndarray) -> np.ndarray:
    opaque = rgba[..., 3] == 255
    strip = Image.fromarray(np.ascontiguousarray(rgba[opaque][:, :3]).reshape(1, -1, 3), "RGB")
    indexed = strip.quantize(colors=COLOURS, method=Image.Quantize.MEDIANCUT,
                             kmeans=KMEANS_PASSES, dither=Image.Dither.NONE)
    palette = np.array(indexed.getpalette()[: 3 * COLOURS], dtype=np.uint8).reshape(-1, 3)
    out = np.zeros_like(rgba)
    out[opaque, :3] = palette[np.array(indexed).reshape(-1)]
    out[opaque, 3] = 255
    return out


def build(source_image: Image.Image, box, width: int, resample) -> tuple[np.ndarray, dict]:
    # Pillow premultiplies RGBA for every filter except NEAREST, so edge colours are not darkened.
    small = np.array(source_image.resize((width, BODY_HEIGHT), resample, box=box))
    small[..., 3] = np.where(small[..., 3] >= ALPHA_CUT, 255, 0)
    small[small[..., 3] == 0] = 0
    small = quantize(small)
    opaque = small[..., 3] == 255
    feet = np.nonzero(opaque[-FEET_ROWS:].any(axis=0))[0]
    feet_mid = (int(feet.min()) + int(feet.max())) // 2
    rows = np.nonzero(opaque.any(axis=1))[0]
    off_x = PIN[0] - feet_mid
    off_y = PIN[1] - 1 - int(rows.max())
    cell = np.zeros((CELL[1], CELL[0], 4), dtype=np.uint8)
    cell[off_y:off_y + BODY_HEIGHT, off_x:off_x + width] = small
    placement = {
        "body_block_size": [width, BODY_HEIGHT],
        "body_block_offset_in_cell": [off_x, off_y],
        "feet_rows_used": FEET_ROWS,
        "feet_span_x_in_block": [int(feet.min()), int(feet.max())],
        "rule": "Lowest opaque row sits at y = pin_y - 1 (ground line y = 104 under offset = -pin); x = 40 is the integer midpoint of the opaque span in the lowest 6 body rows.",
    }
    return cell, placement


def measure(cell: np.ndarray) -> dict:
    alpha = cell[..., 3]
    opaque = alpha == 255
    ys, xs = np.nonzero(alpha > 0)
    colours = np.unique(cell[opaque][:, :3], axis=0)
    border = opaque[0].sum() + opaque[-1].sum() + opaque[1:-1, 0].sum() + opaque[1:-1, -1].sum()
    return {
        "size": [cell.shape[1], cell.shape[0]],
        "alpha_values_present": sorted(int(v) for v in np.unique(alpha)),
        "partial_alpha_texels": int(((alpha > 0) & (alpha < 255)).sum()),
        "opaque_texels": int(opaque.sum()),
        "unique_opaque_rgb_colours": int(len(colours)),
        "palette_hex": ["#%02x%02x%02x" % tuple(int(c) for c in rgb) for rgb in colours],
        "alpha_bounds_inclusive_xyxy": [int(xs.min()), int(ys.min()), int(xs.max()), int(ys.max())],
        "visible_body_height_texels": int(ys.max() - ys.min() + 1),
        "visible_body_width_texels": int(xs.max() - xs.min() + 1),
        "opaque_texels_on_cell_border": int(border),
        "ground_pin": list(PIN),
        "lowest_opaque_row": int(ys.max()),
    }


def png_bytes(cell: np.ndarray) -> bytes:
    from io import BytesIO
    buffer = BytesIO()
    Image.fromarray(cell, "RGBA").save(buffer, format="PNG", optimize=False, compress_level=9)
    return buffer.getvalue()


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--out-dir", type=Path, default=PILOT_DIR)
    parser.add_argument("--qa-capture", action="append", default=[], help="variant=path to a 1280x720 Godot capture")
    args = parser.parse_args()

    source_data = SOURCE.read_bytes()
    if sha256(source_data) != SOURCE_SHA256:
        print("source hash mismatch; refusing to run", file=sys.stderr)
        return 1
    source_image = Image.open(SOURCE).convert("RGBA")
    box, width, crop_facts = crop_box(np.array(source_image))
    args.out_dir.mkdir(parents=True, exist_ok=True)

    candidates = []
    for variant, spec in VARIANTS.items():
        cell, placement = build(source_image, box, width, spec["resample"])
        data = png_bytes(cell)
        target = args.out_dir / spec["file"]
        if target.exists() and target.read_bytes() != data:
            print(f"{target.name} exists with different bytes; refusing to overwrite", file=sys.stderr)
            return 1
        target.write_bytes(data)
        candidates.append({
            "variant": variant,
            "file": spec["file"],
            "format": "PNG RGBA (8-bit), single image, no metadata chunks",
            "bytes": len(data),
            "sha256": sha256(data),
            "resample": spec["resample_name"],
            "placement": placement,
            "measured": measure(cell),
            "hand_edits": [],
            "status": "technical experiment; unapproved; not runtime-integrated",
        })
        print(f"{variant}: {target} sha256={sha256(data)}")

    captures = []
    for item in args.qa_capture:
        variant, _, path = item.partition("=")
        capture = Path(path)
        data = capture.read_bytes()
        with Image.open(capture) as shot:
            size = list(shot.size)
        captures.append({"variant": variant, "file": capture.resolve().relative_to(ROOT).as_posix(),
                         "size": size, "bytes": len(data), "sha256": sha256(data)})

    script_data = Path(__file__).read_bytes()
    manifest = {
        "project": "Worlds Between",
        "milestone": "M8",
        "purpose": "Bounded technical experiment: can a deterministic crop + downsample + binary alpha + <=48 colour quantize improve the 96x115 Pixelorama downscale pilot at game size, without AI image editing.",
        "status": "technical experiment only; unapproved; not integrated; idle frame only, no walk frames",
        "art_approved": False,
        "runtime_integrated": False,
        "walk_frames": 0,
        "acceptance_counters_unchanged": {
            "runtime_exploration_sprites_accepted": "0/52",
            "scene_quality_gates_passed": "0/11",
        },
        "source": {
            "role": "read-only input",
            "file": SOURCE.relative_to(ROOT).as_posix(),
            "size": list(source_image.size),
            "bytes": len(source_data),
            "sha256": SOURCE_SHA256,
        },
        "prior_pilot_for_comparison": {
            "manifest": PRIOR_MANIFEST,
            "downscale_png_measured": {"size": [96, 115], "visible_body_height": 107, "partial_alpha_texels": 3476, "rgba_colours": 3070},
            "relationship": "Not used as input. These candidates start again from the source concept.",
        },
        "generator": {
            "script": Path(__file__).resolve().relative_to(ROOT).as_posix(),
            "script_sha256": sha256(script_data),
            "python": platform.python_version(),
            "pillow": PIL.__version__,
            "numpy": np.__version__,
            "run_flags": "-I (isolated)",
        },
        "method": {
            "steps": [
                f"1. Verify source SHA-256, load as RGBA.",
                f"2. Crop box: strong-alpha (alpha >= {CROP_ALPHA}) bounds; height mapped exactly to {BODY_HEIGHT} texels; width widened symmetrically to a whole texel count at the same step.",
                "3. Resize the crop box to the body block with Pillow Image.resize(resample, box=...). Pillow premultiplies alpha for BOX and LANCZOS.",
                f"4. Binary alpha: alpha >= {ALPHA_CUT} -> 255, else 0; transparent texels set to RGBA 0,0,0,0.",
                f"5. Palette: Pillow quantize(colors={COLOURS}, method=MEDIANCUT, kmeans={KMEANS_PASSES}, dither=NONE) on that candidate's opaque texels only; map each opaque texel to its palette entry.",
                f"6. Place the block on an {CELL[0]}x{CELL[1]} transparent cell with integer offsets: lowest opaque row at y={PIN[1] - 1}, feet-span midpoint at x={PIN[0]}.",
                "7. Save PNG RGBA (optimize=False, compress_level=9). No cleanup edits were applied.",
            ],
            "crop": crop_facts,
            "cleanup_edits": "none (0 texels). Candidate pinholes/orphans found at the body-block level all sit inside the source's stray hair strands, so they were left as source detail.",
            "tested_not_emitted": "NEAREST (centre sampling) was tried in a scratch folder outside the repo with the same crop, alpha and palette steps. It was visibly noisier (random dark outline samples through the coat and hair), so it was not emitted. Limit: two candidates.",
        },
        "pilot_targets_from_memo": {
            "reference": "docs/character-visuals/rpg-2-star-ocean-the-second_character-visuals_art-pipeline-decision-memo_m8-v01_20261014-165532-0cc81856.md",
            "cell": list(CELL),
            "ground_pin": list(PIN),
            "visible_body_height": "96 +/- 1",
            "partial_alpha_texels": 0,
            "max_colours": COLOURS,
            "note": "Pilot parameters only; not an approved standard.",
        },
        "candidates": candidates,
        "qa_captures": captures,
        "review": {
            "e10_user_review": "not done",
            "assessment": "Technical measurements only. Whether the 96-texel quantized idle keeps the approved detail (memo R1 / E10) is the user's call.",
            "technical_observations_by_claude": [
                "Both candidates stay source-recognisable at 48 logical px: ponytail, teal scarf and scarf tail, bedroll, long coat, boots, and a dark knee-guard patch on the viewer-left knee.",
                "LANCZOS is slightly crisper (edges, knee guard, eyes) than BOX; BOX is smoother but muddier.",
                "Lost or weakened at this density: eye/face detail (1-2 texel features), chest badge (1-2 teal texels), buckles and belt hardware, ponytail crown (thin, broken), knee-guard contrast.",
                "No dark outline survives the area average, so the coat and trousers sit close to the beige/brown paving in value.",
                "Stray hair texels on the viewer-left side are source detail (messy hair), but read as noise at this size.",
                "QA scene anchors the sprite on its alpha-bounds centre (existing script behaviour, unchanged), not on the declared pin x=40; the 1:1 texel check is unaffected.",
            ],
        },
    }
    manifest_path = args.out_dir / MANIFEST_NAME
    manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    print(f"manifest: {manifest_path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
