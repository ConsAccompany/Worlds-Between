#!/usr/bin/env python3
"""Deterministic builder for the bounded female display-portrait package.

Input : the unapproved female concept sheet (RGB/RGBA PNG).
Output: one exact-pixel crop PNG, one single-layer OpenRaster (.ora), one
        machine-readable manifest, and one SHA-256 receipt.

The builder uses only the Python standard library.  It never resamples,
repaints, generates pixels, removes a background or invents content.  The
only pixel operation is an exact rectangle slice in source pixel space.

Run from the ds-portrait workspace:
    python build/build_female_display_portrait.py

Reproducibility: pass --timestamp-utc and --run-id explicitly.  The same
inputs plus the same explicit run identity produce byte-identical artifacts.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import secrets
import struct
import sys
import zlib
from datetime import datetime, timezone
from zipfile import ZIP_STORED, ZipFile, ZipInfo

PROJECT = "rpg-2-star-ocean-the-second"
SUBJECT = "protagonist-female"
PURPOSE = "display-portrait-crop"
VARIANT = "v01"
CONTENT_ID = "content.char.protagonist-female.display"
SCHEMA_ID = "ds-portrait/display-image-manifest/v1"
SOURCE_REL = (
    "outputs/rpg-2-star-ocean-the-second_protagonist_character-sheet_female_"
    "20261013-153316-8fa4d0c3.png"
)
SOURCE_SHA256 = "3d876c4f666913d6110fe8a058b79a55ce82ac225577d87f1f02624affeea58d"
SOURCE_WIDTH = 1916
SOURCE_HEIGHT = 821
CROP_LEFT, CROP_TOP, CROP_RIGHT, CROP_BOTTOM = 952, 42, 1191, 353
CROP_WIDTH = CROP_RIGHT - CROP_LEFT
CROP_HEIGHT = CROP_BOTTOM - CROP_TOP
LAYER_NAME = "original-illustration-crop-952-42-1191-353"
DISPLAY_RECT = {"x": 522, "y": 88, "width": 96, "height": 124}


class BuildError(RuntimeError):
    pass


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _chunk(kind: bytes, payload: bytes) -> bytes:
    return (
        struct.pack(">I", len(payload))
        + kind
        + payload
        + struct.pack(">I", zlib.crc32(kind + payload) & 0xFFFFFFFF)
    )


def decode_png(data: bytes):
    """Decode a non-interlaced 8-bit PNG to (width, height, RGBA rows)."""
    if not data.startswith(b"\x89PNG\r\n\x1a\n"):
        raise BuildError("not a PNG (bad signature)")
    pos = 8
    ihdr = None
    palette = None
    trns = b""
    idat = bytearray()
    seen_iend = False
    while pos < len(data):
        if pos + 8 > len(data):
            raise BuildError("truncated PNG chunk header")
        (length,) = struct.unpack(">I", data[pos : pos + 4])
        kind = data[pos + 4 : pos + 8]
        payload = data[pos + 8 : pos + 8 + length]
        crc_raw = data[pos + 8 + length : pos + 12 + length]
        if len(payload) != length or len(crc_raw) != 4:
            raise BuildError("truncated PNG chunk")
        (crc,) = struct.unpack(">I", crc_raw)
        if zlib.crc32(kind + payload) & 0xFFFFFFFF != crc:
            raise BuildError(f"bad PNG CRC in {kind!r}")
        pos += 12 + length
        if kind == b"IHDR":
            ihdr = struct.unpack(">IIBBBBB", payload)
        elif kind == b"PLTE":
            palette = payload
        elif kind == b"tRNS":
            trns = payload
        elif kind == b"IDAT":
            idat.extend(payload)
        elif kind == b"IEND":
            seen_iend = True
            break
    if ihdr is None or not seen_iend or not idat:
        raise BuildError("missing IHDR, IDAT or IEND")
    width, height, depth, color_type, comp, filt, interlace = ihdr
    if depth != 8 or comp != 0 or filt != 0 or interlace != 0:
        raise BuildError(
            "only non-interlaced 8-bit PNG is supported, got "
            f"depth={depth} interlace={interlace}"
        )
    channels = {0: 1, 2: 3, 3: 1, 4: 2, 6: 4}.get(color_type)
    if channels is None:
        raise BuildError(f"unsupported PNG color type {color_type}")
    if color_type == 3 and palette is None:
        raise BuildError("indexed PNG without PLTE")
    raw = zlib.decompress(bytes(idat))
    stride = width * channels
    expected = height * (stride + 1)
    if len(raw) != expected:
        raise BuildError(f"unexpected decompressed size {len(raw)} != {expected}")
    bpp = channels
    rows = []
    prev = bytearray(stride)
    off = 0
    for _ in range(height):
        ftype = raw[off]
        off += 1
        row = bytearray(raw[off : off + stride])
        off += stride
        if ftype == 0:
            pass
        elif ftype == 1:
            for i in range(bpp, stride):
                row[i] = (row[i] + row[i - bpp]) & 0xFF
        elif ftype == 2:
            for i in range(stride):
                row[i] = (row[i] + prev[i]) & 0xFF
        elif ftype == 3:
            for i in range(stride):
                left = row[i - bpp] if i >= bpp else 0
                row[i] = (row[i] + ((left + prev[i]) >> 1)) & 0xFF
        elif ftype == 4:
            for i in range(stride):
                a = row[i - bpp] if i >= bpp else 0
                b = prev[i]
                c = prev[i - bpp] if i >= bpp else 0
                p = a + b - c
                pa, pb, pc = abs(p - a), abs(p - b), abs(p - c)
                pr = a if (pa <= pb and pa <= pc) else (b if pb <= pc else c)
                row[i] = (row[i] + pr) & 0xFF
        else:
            raise BuildError(f"bad PNG filter type {ftype}")
        prev = row
        rows.append(row)

    rgba_rows = []
    for row in rows:
        out = bytearray(width * 4)
        if color_type == 6:
            out[:] = row
        elif color_type == 2:
            for x in range(width):
                out[4 * x : 4 * x + 3] = row[3 * x : 3 * x + 3]
                out[4 * x + 3] = 255
        elif color_type == 0:
            for x in range(width):
                g = row[x]
                out[4 * x : 4 * x + 4] = bytes((g, g, g, 255))
        elif color_type == 4:
            for x in range(width):
                g, a = row[2 * x], row[2 * x + 1]
                out[4 * x : 4 * x + 4] = bytes((g, g, g, a))
        elif color_type == 3:
            for x in range(width):
                idx = row[x]
                if 3 * idx + 3 > len(palette):
                    raise BuildError("PLTE index out of range")
                r, g, b = palette[3 * idx : 3 * idx + 3]
                a = trns[idx] if idx < len(trns) else 255
                out[4 * x : 4 * x + 4] = bytes((r, g, b, a))
        rgba_rows.append(bytes(out))
    return width, height, rgba_rows, color_type


def encode_png_rgba(width: int, height: int, rows) -> bytes:
    raw = bytearray()
    for row in rows:
        raw.append(0)  # filter: None
        raw.extend(row)
    ihdr = struct.pack(">IIBBBBB", width, height, 8, 6, 0, 0, 0)
    return (
        b"\x89PNG\r\n\x1a\n"
        + _chunk(b"IHDR", ihdr)
        + _chunk(b"IDAT", zlib.compress(bytes(raw), 9))
        + _chunk(b"IEND", b"")
    )


def _zip_info(name: str) -> ZipInfo:
    info = ZipInfo(name, date_time=(1980, 1, 1, 0, 0, 0))
    info.compress_type = ZIP_STORED
    info.create_system = 0
    info.external_attr = 0o644 << 16
    return info


def build_ora(layer_png: bytes, width: int, height: int) -> bytes:
    import io

    stack = (
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        f'<image version="0.0.3" w="{width}" h="{height}">\n'
        '  <stack name="root">\n'
        f'    <layer name="{LAYER_NAME}" src="data/layer1.png" x="0" y="0" '
        'visibility="visible" opacity="1.0" composite-op="svg:src-over"/>\n'
        "  </stack>\n"
        "</image>\n"
    ).encode("utf-8")
    buf = io.BytesIO()
    with ZipFile(buf, "w") as zf:
        zf.writestr(_zip_info("mimetype"), b"image/openraster")
        zf.writestr(_zip_info("stack.xml"), stack)
        zf.writestr(_zip_info("data/layer1.png"), layer_png)
        zf.writestr(_zip_info("Thumbnails/thumbnail.png"), layer_png)
        zf.writestr(_zip_info("mergedimage.png"), layer_png)
    return buf.getvalue()


def build(args) -> dict:
    workspace = os.path.abspath(args.workspace)
    source_path = os.path.abspath(args.source)
    out_dir = os.path.abspath(args.out_dir)
    os.makedirs(out_dir, exist_ok=True)

    if args.timestamp_utc:
        ts = datetime.fromisoformat(args.timestamp_utc.replace("Z", "+00:00"))
        if ts.tzinfo is None:
            raise BuildError("--timestamp-utc must include an offset")
        ts = ts.astimezone(timezone.utc).replace(microsecond=0)
    else:
        ts = datetime.now(timezone.utc).replace(microsecond=0)
    compact = ts.strftime("%Y%m%d-%H%M%S")
    run_id = args.run_id or secrets.token_hex(4)
    if len(run_id) != 8 or any(c not in "0123456789abcdef" for c in run_id):
        raise BuildError("--run-id must be exactly 8 lowercase hex characters")
    iso = ts.isoformat().replace("+00:00", "Z")

    source_bytes = open(source_path, "rb").read()
    source_sha = sha256_bytes(source_bytes)
    if source_sha != SOURCE_SHA256:
        raise BuildError(
            f"source SHA-256 mismatch: got {source_sha}, expected {SOURCE_SHA256}"
        )
    sw, sh, src_rows, source_color_type = decode_png(source_bytes)
    if (sw, sh) != (SOURCE_WIDTH, SOURCE_HEIGHT):
        raise BuildError(f"source dimensions {sw}x{sh} != 1916x821")
    if CROP_LEFT < 0 or CROP_TOP < 0 or CROP_RIGHT > sw or CROP_BOTTOM > sh:
        raise BuildError("crop rectangle outside source bounds")
    if (CROP_WIDTH, CROP_HEIGHT) != (239, 311):
        raise BuildError("crop rectangle did not resolve to 239x311")

    crop_rows = [src_rows[y][CROP_LEFT * 4 : CROP_RIGHT * 4] for y in range(CROP_TOP, CROP_BOTTOM)]
    crop_png = encode_png_rgba(CROP_WIDTH, CROP_HEIGHT, crop_rows)
    crop_sha = sha256_bytes(crop_png)

    # Independent decode of the artifact, compared pixel-by-pixel to the ROI.
    dw, dh, decoded_rows, decoded_color_type = decode_png(crop_png)
    if (dw, dh) != (CROP_WIDTH, CROP_HEIGHT):
        raise BuildError("crop PNG dimension check failed")
    if decoded_color_type != 6:
        raise BuildError("crop PNG is not RGBA")
    for y in range(CROP_HEIGHT):
        if decoded_rows[y] != crop_rows[y]:
            raise BuildError(f"crop pixel mismatch at row {y}")

    ora_bytes = build_ora(crop_png, CROP_WIDTH, CROP_HEIGHT)

    stem = f"{PROJECT}_{SUBJECT}_{PURPOSE}_{VARIANT}_{compact}-{run_id}"
    crop_name = f"{stem}.png"
    ora_name = f"{PROJECT}_{SUBJECT}_display-portrait-editable_{VARIANT}_{compact}-{run_id}.ora"
    manifest_name = f"{PROJECT}_{SUBJECT}_display-portrait-manifest_{VARIANT}_{compact}-{run_id}.json"
    receipt_name = f"{PROJECT}_{SUBJECT}_display-portrait-checksums_{VARIANT}_{compact}-{run_id}.sha256"
    paths = {n: os.path.join(out_dir, n) for n in (crop_name, ora_name, manifest_name, receipt_name)}
    existing = [p for p in paths.values() if os.path.exists(p)]
    if existing and not args.force:
        raise BuildError(
            "refusing to overwrite existing artifacts (use a new run id): "
            + ", ".join(os.path.basename(p) for p in existing)
        )

    # Verify the ORA container independently: single layer, byte-identical PNG.
    import io
    from xml.etree import ElementTree

    with ZipFile(io.BytesIO(ora_bytes), "r") as zf:
        names = zf.namelist()
        if names[0] != "mimetype" or zf.read("mimetype") != b"image/openraster":
            raise BuildError("ORA mimetype entry is not first/uncompressed/openraster")
        root = ElementTree.fromstring(zf.read("stack.xml"))
        layers = [n for n in root.iter() if n.tag == "layer"]
        if len(layers) != 1:
            raise BuildError(f"ORA must contain exactly one layer, got {len(layers)}")
        layer_png = zf.read("data/layer1.png")
        if layer_png != crop_png:
            raise BuildError("ORA layer PNG is not byte-identical to crop PNG")
        if zf.read("mergedimage.png") != crop_png:
            raise BuildError("ORA mergedimage.png is not byte-identical to crop PNG")
        if zf.read("Thumbnails/thumbnail.png") != crop_png:
            raise BuildError("ORA thumbnail is not byte-identical to crop PNG")
        lw, lh, layer_rows, _ = decode_png(layer_png)
        if (lw, lh) != (CROP_WIDTH, CROP_HEIGHT):
            raise BuildError("ORA layer native dimensions changed")
        for y in range(CROP_HEIGHT):
            if layer_rows[y] != crop_rows[y]:
                raise BuildError(f"ORA layer pixel mismatch at row {y}")

    image_rel = crop_name
    manifest = {
        "schema": SCHEMA_ID,
        "content_id": CONTENT_ID,
        "package_id": f"{PROJECT}_{SUBJECT}_{PURPOSE}_{VARIANT}_{compact}-{run_id}",
        "run": {
            "timestamp_utc": iso,
            "timestamp_compact_utc": compact,
            "unique_id": run_id,
            "id": f"{compact}-{run_id}",
        },
        "project": PROJECT,
        "subject": SUBJECT,
        "purpose": PURPOSE,
        "variant": VARIANT,
        "source": {
            "path": SOURCE_REL.replace("\\", "/"),
            "sha256": SOURCE_SHA256,
            "bytes": len(source_bytes),
            "width": sw,
            "height": sh,
            "bit_depth": 8,
            "color_type": source_color_type,
            "role": "unapproved-concept-sheet",
        },
        "crop": {
            "left": CROP_LEFT,
            "top": CROP_TOP,
            "right": CROP_RIGHT,
            "bottom": CROP_BOTTOM,
            "width": CROP_WIDTH,
            "height": CROP_HEIGHT,
            "coordinate_space": "source pixels, top-left origin, right/bottom exclusive",
            "method": "exact-pixel-rectangle-slice",
            "resampled": False,
            "repainted": False,
            "ai_generated": False,
            "ai_generated_field_scope": "crop operation adds no newly generated pixels; original source is AI-generated",
            "background_removed": False,
            "invented_pixels": False,
            "pixel_count": CROP_WIDTH * CROP_HEIGHT,
        },
        "image": {
            "path": image_rel,
            "sha256": crop_sha,
            "bytes": len(crop_png),
            "width": CROP_WIDTH,
            "height": CROP_HEIGHT,
            "format": "PNG",
            "color": "RGBA8",
        },
        "layer": {
            "name": LAYER_NAME,
            "role": "original illustration crop preserved as one editable layer",
            "width": CROP_WIDTH,
            "height": CROP_HEIGHT,
            "sha256": crop_sha,
            "native_png_equality": True,
        },
        "outputs": [
            {
                "kind": "crop-png",
                "path": crop_name,
                "sha256": crop_sha,
                "bytes": len(crop_png),
                "width": CROP_WIDTH,
                "height": CROP_HEIGHT,
            },
            {
                "kind": "editable-openraster-ora",
                "path": ora_name,
                "sha256": sha256_bytes(ora_bytes),
                "bytes": len(ora_bytes),
                "openraster_version": "0.0.3",
                "layers": 1,
                "layer_sha256": crop_sha,
                "layer_native_png_equality": True,
            },
        ],
        "display": {
            "helper": "rpg-2-star-ocean-the-second_protagonist-female_display-portrait-helper_v01_20261019-182839-4d72f1c6.gd",
            "content_id": CONTENT_ID,
            "image_path": image_rel,
            "image_sha256": crop_sha,
            "image_width": CROP_WIDTH,
            "image_height": CROP_HEIGHT,
            "rect": dict(DISPLAY_RECT),
            "stretch_mode": "KEEP_ASPECT_CENTERED",
            "appearance_required": "female",
            "member_id_required": "hero",
            "panel_condition": "node_panel_hidden",
            "pilot_flag": "--female-display-portrait-pilot",
            "draw_order": "above-background-below-node-overlay",
        },
        "provenance": {
            "source_status": "unapproved-concept-source",
            "original_source_ai_generated": True,
            "new_generative_processing": False,
            "unapproved": True,
            "accepted_character_canon": False,
            "approved_static": False,
            "full_sprite_approved": False,
            "human_artist": False,
            "approval": "none",
            "approval_note": (
                "Original concept sheet is AI-generated. Crop performs no new generative processing. No human artist attribution and no approval were supplied. "
                "This is a derived crop of an unapproved concept sheet; it is "
                "not accepted character canon and not an approved static."
            ),
            "new_identity_created": False,
            "semantic_anatomy_claims": False,
            "handpainted_claims": False,
        },
        "verification": {
            "builder": "tools/rpg-2-star-ocean-the-second_protagonist-female_display-portrait-builder_v01_20261019-182839-4d72f1c6.py",
            "python": sys.version.split()[0],
            "stdlib_only": True,
            "checks": {
                "source_sha256": True,
                "source_dimensions": True,
                "crop_dimensions": True,
                "crop_rgba_pixels_equal_source_roi": True,
                "crop_pixel_count": CROP_WIDTH * CROP_HEIGHT,
                "crop_png_redecoded_rgba": True,
                "ora_single_layer": True,
                "ora_layer_png_byte_equal_crop_png": True,
                "ora_layer_native_dimensions": True,
                "ora_layer_pixels_equal_crop": True,
                "no_resample": True,
                "no_repaint_or_ai": True,
                "background_not_removed": True,
            },
        },
    }

    manifest_bytes = (json.dumps(manifest, indent=2, ensure_ascii=False) + "\n").encode("utf-8")
    receipt = (
        f"{crop_sha}  {crop_name}\n"
        f"{sha256_bytes(ora_bytes)}  {ora_name}\n"
        f"{sha256_bytes(manifest_bytes)}  {manifest_name}\n"
    )

    with open(paths[crop_name], "wb") as f:
        f.write(crop_png)
    with open(paths[ora_name], "wb") as f:
        f.write(ora_bytes)
    with open(paths[manifest_name], "wb") as f:
        f.write(manifest_bytes)
    with open(paths[receipt_name], "w", encoding="utf-8", newline="\n") as f:
        f.write(receipt)

    return {
        "timestamp_utc": iso,
        "run_id": run_id,
        "out_dir": out_dir,
        "files": list(paths.values()),
        "crop_sha256": crop_sha,
        "ora_sha256": sha256_bytes(ora_bytes),
        "manifest_sha256": sha256_bytes(manifest_bytes),
    }


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--workspace", default=os.getcwd())
    parser.add_argument("--source", default=None)
    parser.add_argument("--out-dir", default=None)
    parser.add_argument("--timestamp-utc", default=None, help="ISO-8601 UTC, e.g. 2026-10-19T22:30:00Z")
    parser.add_argument("--run-id", default=None, help="8 lowercase hex characters")
    parser.add_argument("--force", action="store_true")
    args = parser.parse_args(argv)
    args.workspace = os.path.abspath(args.workspace)
    args.source = args.source or os.path.join(args.workspace, SOURCE_REL)
    args.out_dir = args.out_dir or os.path.join(args.workspace, "deliverables")
    try:
        result = build(args)
    except BuildError as exc:
        print(f"BUILD FAILED: {exc}", file=sys.stderr)
        return 2
    print(json.dumps(result, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
