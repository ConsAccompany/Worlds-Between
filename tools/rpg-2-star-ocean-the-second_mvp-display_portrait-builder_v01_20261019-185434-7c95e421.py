#!/usr/bin/env python3
"""Deterministic builder for the four new MVP display-portrait packages.

Reuses only the stdlib PNG/ORA primitives in build_female_display_portrait.py.
Each package is one exact-pixel crop PNG, one single-layer ORA, one manifest and
one SHA-256 receipt.  No resample, repaint, AI invention or background removal.
"""
from __future__ import annotations

import argparse
import importlib.util
import json
import os
import sys
from datetime import datetime, timezone

HERE = os.path.dirname(os.path.abspath(__file__))
_spec = importlib.util.spec_from_file_location(
    "female_portrait_builder", os.path.join(HERE, "rpg-2-star-ocean-the-second_protagonist-female_display-portrait-builder_v01_20261019-182839-4d72f1c6.py")
)
_fb = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_fb)

PROJECT = "rpg-2-star-ocean-the-second"
PURPOSE = "display-portrait-crop"
VARIANT = "v01"
SCHEMA_ID = "ds-portrait/display-image-manifest/v1"
DISPLAY_RECT = {"x": 522, "y": 88, "width": 96, "height": 124}

VARIANTS = [
    {
        "subject": "protagonist-male",
        "content_id": "content.char.protagonist-male.display",
        "source": "outputs/rpg-2-star-ocean-the-second_protagonist_character-sheet_male_20261013-153316-5b7c19e2.png",
        "source_sha256": "d92a3c4442f71394bb118a5034c57d52a3e3e7b2142bcb2b0b69d964e3dc4765",
        "roi": (948, 54, 1187, 365),
        "appearance": "male",
        "member_id": "hero",
        "helper_variant": "protagonist-male",
    },
    {
        "subject": "liang-xu",
        "content_id": "content.char.liang-xu.display",
        "source": "outputs/rpg-2-star-ocean-the-second_liang-xu_character-sheet_v01_20261013-153556-c7630671.png",
        "source_sha256": "af2da3de75c8eea1779688b16396860721f7e2d9156fd90c28df13d0e2ffd56f",
        "roi": (930, 35, 1235, 403),
        "appearance": "any",
        "member_id": "liang-xu",
        "helper_variant": "liang-xu",
    },
    {
        "subject": "ji-cheng",
        "content_id": "content.char.ji-cheng.display",
        "source": "outputs/rpg-2-star-ocean-the-second_ji-cheng_character-sheet_v01_20261013-190436-dcea1a37.png",
        "source_sha256": "4165c47e28329e2d4fd2dd160886118a70cb06fd160172b90ba45f00584cc546",
        "roi": (830, 10, 1190, 420),
        "variant": "v02",
        "run_identity_override": ("2026-10-19T22:56:14Z", "2e8f935b"),
        "appearance": "any",
        "member_id": "ji-cheng",
        "helper_variant": "ji-cheng",
    },
    {
        "subject": "zhao-ling",
        "content_id": "content.char.zhao-ling.display",
        "source": "outputs/rpg-2-star-ocean-the-second_zhao-ling_character-sheet_v01_20261013-193120-54215370.png",
        "source_sha256": "5fe7b5e8f41878e0a96883164afb7069300663e03e4e9815f2cb17dc9500d780",
        "roi": (830, 15, 1210, 360),
        "appearance": "any",
        "member_id": "zhao-ling",
        "helper_variant": "zhao-ling",
    },
]


def build_one(spec: dict, ts: datetime, compact: str, base_run_id: str, out_dir: str, workspace: str) -> dict:
    variant = spec.get("variant", VARIANT)
    if "run_identity_override" in spec:
        stamp, base_run_id = spec["run_identity_override"]
        ts = datetime.fromisoformat(stamp.replace("Z", "+00:00"))
        compact = ts.strftime("%Y%m%d-%H%M%S")
    left, top, right, bottom = spec["roi"]
    width, height = right - left, bottom - top
    source_path = os.path.join(workspace, spec["source"])
    source_bytes = open(source_path, "rb").read()
    source_sha = _fb.sha256_bytes(source_bytes)
    if source_sha != spec["source_sha256"]:
        raise _fb.BuildError(f"{spec['subject']}: source SHA-256 mismatch: {source_sha}")
    sw, sh, src_rows, color_type = _fb.decode_png(source_bytes)
    if (sw, sh) != (1916, 821):
        raise _fb.BuildError(f"{spec['subject']}: source dimensions {sw}x{sh} != 1916x821")
    if left < 0 or top < 0 or right > sw or bottom > sh:
        raise _fb.BuildError(f"{spec['subject']}: ROI outside source")
    crop_rows = [src_rows[y][left * 4 : right * 4] for y in range(top, bottom)]
    crop_png = _fb.encode_png_rgba(width, height, crop_rows)
    crop_sha = _fb.sha256_bytes(crop_png)
    dw, dh, decoded, decoded_type = _fb.decode_png(crop_png)
    if (dw, dh) != (width, height) or decoded_type != 6:
        raise _fb.BuildError(f"{spec['subject']}: crop PNG decode contract failed")
    for y in range(height):
        if decoded[y] != crop_rows[y]:
            raise _fb.BuildError(f"{spec['subject']}: crop pixel mismatch row {y}")

    run_id = __import__("hashlib").sha256(f"{base_run_id}|{spec['subject']}".encode()).hexdigest()[:8]
    layer_name = f"original-illustration-crop-{left}-{top}-{right}-{bottom}"
    ora_bytes = _fb.build_ora(crop_png, width, height)
    # Rebuild the ORA with the variant layer name while keeping one layer and
    # byte-identical image payloads.
    import io
    from zipfile import ZipFile, ZIP_STORED, ZipInfo

    stack = (
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        f'<image version="0.0.3" w="{width}" h="{height}">\n'
        '  <stack name="root">\n'
        f'    <layer name="{layer_name}" src="data/layer1.png" x="0" y="0" '
        'visibility="visible" opacity="1.0" composite-op="svg:src-over"/>\n'
        '  </stack>\n'
        "</image>\n"
    ).encode("utf-8")

    def info(name):
        zi = ZipInfo(name, date_time=(1980, 1, 1, 0, 0, 0))
        zi.compress_type = ZIP_STORED
        zi.create_system = 0
        zi.external_attr = 0o644 << 16
        return zi

    buf = io.BytesIO()
    with ZipFile(buf, "w") as zf:
        zf.writestr(info("mimetype"), b"image/openraster")
        zf.writestr(info("stack.xml"), stack)
        zf.writestr(info("data/layer1.png"), crop_png)
        zf.writestr(info("Thumbnails/thumbnail.png"), crop_png)
        zf.writestr(info("mergedimage.png"), crop_png)
    ora_bytes = buf.getvalue()

    from xml.etree import ElementTree
    with ZipFile(io.BytesIO(ora_bytes), "r") as zf:
        if zf.namelist()[0] != "mimetype" or zf.read("mimetype") != b"image/openraster":
            raise _fb.BuildError(f"{spec['subject']}: bad ORA mimetype")
        root = ElementTree.fromstring(zf.read("stack.xml"))
        layers = [n for n in root.iter() if n.tag == "layer"]
        if len(layers) != 1 or layers[0].get("src") != "data/layer1.png":
            raise _fb.BuildError(f"{spec['subject']}: ORA must have exactly one layer")
        if zf.read("data/layer1.png") != crop_png or zf.read("mergedimage.png") != crop_png:
            raise _fb.BuildError(f"{spec['subject']}: ORA PNG payload mismatch")

    stem = f"{PROJECT}_{spec['subject']}_{PURPOSE}_{variant}_{compact}-{run_id}"
    crop_name = f"{stem}.png"
    ora_name = f"{PROJECT}_{spec['subject']}_display-portrait-editable_{variant}_{compact}-{run_id}.ora"
    manifest_name = f"{PROJECT}_{spec['subject']}_display-portrait-manifest_{variant}_{compact}-{run_id}.json"
    receipt_name = f"{PROJECT}_{spec['subject']}_display-portrait-checksums_{variant}_{compact}-{run_id}.sha256"
    paths = {n: os.path.join(out_dir, n) for n in (crop_name, ora_name, manifest_name, receipt_name)}
    for path in paths.values():
        if os.path.exists(path):
            raise _fb.BuildError(f"refusing to overwrite {os.path.basename(path)}")

    iso = ts.isoformat().replace("+00:00", "Z")
    manifest = {
        "schema": SCHEMA_ID,
        "content_id": spec["content_id"],
        "package_id": stem,
        "run": {
            "timestamp_utc": iso,
            "timestamp_compact_utc": compact,
            "unique_id": run_id,
            "id": f"{compact}-{run_id}",
        },
        "project": PROJECT,
        "subject": spec["subject"],
        "purpose": PURPOSE,
        "variant": variant,
        "source": {
            "path": spec["source"].replace("\\", "/"),
            "sha256": spec["source_sha256"],
            "bytes": len(source_bytes),
            "width": sw,
            "height": sh,
            "bit_depth": 8,
            "color_type": color_type,
            "role": "unapproved-concept-sheet",
        },
        "crop": {
            "left": left,
            "top": top,
            "right": right,
            "bottom": bottom,
            "width": width,
            "height": height,
            "coordinate_space": "source pixels, top-left origin, right/bottom exclusive",
            "method": "exact-pixel-rectangle-slice",
            "resampled": False,
            "repainted": False,
            "ai_generated": False,
            "background_removed": False,
            "invented_pixels": False,
            "pixel_count": width * height,
        },
        "image": {
            "path": crop_name,
            "sha256": crop_sha,
            "bytes": len(crop_png),
            "width": width,
            "height": height,
            "format": "PNG",
            "color": "RGBA8",
        },
        "layer": {
            "name": layer_name,
            "role": "original illustration crop preserved as one editable layer",
            "width": width,
            "height": height,
            "sha256": crop_sha,
            "native_png_equality": True,
        },
        "outputs": [
            {
                "kind": "crop-png",
                "path": crop_name,
                "sha256": crop_sha,
                "bytes": len(crop_png),
                "width": width,
                "height": height,
            },
            {
                "kind": "editable-openraster-ora",
                "path": ora_name,
                "sha256": _fb.sha256_bytes(ora_bytes),
                "bytes": len(ora_bytes),
                "openraster_version": "0.0.3",
                "layers": 1,
                "layer_sha256": crop_sha,
                "layer_native_png_equality": True,
            },
        ],
        "display": {
            "helper": "rpg-2-star-ocean-the-second_mvp-display_portrait-helper_v01_20261019-185434-7c95e421.gd",
            "variant_key": spec["helper_variant"],
            "content_id": spec["content_id"],
            "image_path": crop_name,
            "image_sha256": crop_sha,
            "image_width": width,
            "image_height": height,
            "rect": dict(DISPLAY_RECT),
            "stretch_mode": "KEEP_ASPECT_CENTERED",
            "appearance_required": spec["appearance"],
            "member_id_required": spec["member_id"],
            "selection_rule": "selected_id-whitelist",
            "panel_condition": "node_panel_hidden",
            "pilot_flag": "--mvp-display-portraits-pilot",
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
                "Original source is AI-generated; exact crop adds no new generative pixels. No human artist attribution and no approval were supplied. This is a "
                "derived crop of an unapproved concept sheet; it is not accepted "
                "character canon and not an approved static."
            ),
            "new_identity_created": False,
            "semantic_anatomy_claims": False,
            "handpainted_claims": False,
        },
        "verification": {
            "builder": "tools/rpg-2-star-ocean-the-second_mvp-display_portrait-builder_v01_20261019-185434-7c95e421.py",
            "python": sys.version.split()[0],
            "stdlib_only": True,
            "checks": {
                "source_sha256": True,
                "source_dimensions": True,
                "crop_dimensions": True,
                "crop_rgba_pixels_equal_source_roi": True,
                "crop_pixel_count": width * height,
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
        f"{_fb.sha256_bytes(ora_bytes)}  {ora_name}\n"
        f"{_fb.sha256_bytes(manifest_bytes)}  {manifest_name}\n"
    )
    open(paths[crop_name], "wb").write(crop_png)
    open(paths[ora_name], "wb").write(ora_bytes)
    open(paths[manifest_name], "wb").write(manifest_bytes)
    with open(paths[receipt_name], "w", encoding="utf-8", newline="\n") as f:
        f.write(receipt)
    return {
        "subject": spec["subject"],
        "run_id": run_id,
        "crop": crop_name,
        "crop_sha256": crop_sha,
        "ora": ora_name,
        "ora_sha256": _fb.sha256_bytes(ora_bytes),
        "manifest": manifest_name,
        "manifest_sha256": _fb.sha256_bytes(manifest_bytes),
        "width": width,
        "height": height,
        "pixels": width * height,
    }


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--workspace", default=os.path.dirname(HERE))
    parser.add_argument("--out-dir", default=None)
    parser.add_argument("--timestamp-utc", required=True)
    parser.add_argument("--run-id", required=True)
    args = parser.parse_args(argv)
    workspace = os.path.abspath(args.workspace)
    out_dir = os.path.abspath(args.out_dir or os.path.join(workspace, "deliverables"))
    os.makedirs(out_dir, exist_ok=True)
    ts = datetime.fromisoformat(args.timestamp_utc.replace("Z", "+00:00"))
    if ts.tzinfo is None:
        raise _fb.BuildError("--timestamp-utc must include an offset")
    ts = ts.astimezone(timezone.utc).replace(microsecond=0)
    compact = ts.strftime("%Y%m%d-%H%M%S")
    if len(args.run_id) != 8 or any(c not in "0123456789abcdef" for c in args.run_id):
        raise _fb.BuildError("--run-id must be 8 lowercase hex characters")
    results = [build_one(spec, ts, compact, args.run_id, out_dir, workspace) for spec in VARIANTS]
    print(json.dumps({"timestamp_utc": ts.isoformat().replace("+00:00", "Z"), "results": results}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
