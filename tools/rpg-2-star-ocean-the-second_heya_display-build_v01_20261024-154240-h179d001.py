"""Heya display image: deterministic nearest-neighbour integer 2x of the committed native south static.

Reuses the credited Yanke ydisplay111 / Muxiu mdisplay91 builder (itself derived from the Lin Que display64
pipeline): pinned source -> deterministic derivation -> manifest -> UI scene -> contract/malformed/probe
checks. The transform is an exact integer pixel replication of the authoritative 80x112 south static. No
repaint, no new generative pixels, no concept art, no default adoption. The editable PXO/ORA sources and the
palette are pinned as provenance only.

Usage: python -I <this> build   -> writes display PNG + manifest (refuses to overwrite differing bytes)
       python -I <this> check   -> re-derives from source and verifies pins; exit 1 on any failure
"""
import hashlib
import io
import json
import sys
from pathlib import Path

from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
RUN = "20261024-154240-h179d001"
SDIR = "game/assets/characters/heya-native-v01/south"
SOURCE = f"{SDIR}/rpg-2-star-ocean-the-second_heya_south-static_unapproved-v01_20261024-125310-231d2b03.png"
SOURCE_SHA = "f6e60682bc7f5290aff11ec1154e515137a2b0f66a7fd5141ef4a9afa755d2c3"
SOURCE_RAW_RGBA_SHA = "59e322f03c33987b28999d3cd6cbeec3e16c41dcc793387d38b168fede145d65"
SOURCE_SIZE = (80, 112)
SOURCE_MANIFEST = f"{SDIR}/rpg-2-star-ocean-the-second_heya_south-manifest_unapproved-v01_20261024-125310-a9210ea1.json"
SOURCE_MANIFEST_SHA = "d6ddec7e38d74083e6a774d96e7235c9b64fe5ba7b7ec3664f5067f82217d80c"
EDITABLE = {
    "pxo": (f"{SDIR}/rpg-2-star-ocean-the-second_heya_south-edit_unapproved-v01_20261024-125310-9665bd23.pxo",
            "f5613b9d4b787e694eddf0c76bb0de28535495849d427d838c30647b7257b12a"),
    "ora": (f"{SDIR}/rpg-2-star-ocean-the-second_heya_south-edit_unapproved-v01_20261024-125310-42e46403.ora",
            "694e105375eded54d605698f6c65862f152a3e0c63a2462dd90fe4073c8aff36"),
    "palette": (f"{SDIR}/rpg-2-star-ocean-the-second_heya_south-palette_unapproved-v01_20261024-125310-a902fe49.json",
                "a699845e99d7cc794402b5e31b3e515cafb5459645fbab05d5a4eefb4071e838"),
}
SOURCE_COMMIT = "dc8ad3b4cff0ac375a00dee3b46ab8135e27e80f"
FACTOR = 2
OUT_DIR = ROOT / "game/assets/portraits/hdisplay179"
DISPLAY = OUT_DIR / f"rpg-2-star-ocean-the-second_heya_display-portrait_v01_{RUN}.png"
MANIFEST = OUT_DIR / f"rpg-2-star-ocean-the-second_heya_display-portrait-manifest_v01_{RUN}.json"


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def replicate(src: Image.Image) -> Image.Image:
    """Exact nearest-neighbour pixel replication by an integer factor (no interpolation)."""
    dst = Image.new("RGBA", (src.width * FACTOR, src.height * FACTOR))
    src_px = src.load()
    dst_px = dst.load()
    for y in range(src.height):
        for x in range(src.width):
            p = src_px[x, y]
            for dy in range(FACTOR):
                for dx in range(FACTOR):
                    dst_px[x * FACTOR + dx, y * FACTOR + dy] = p
    return dst


def derive():
    raw = (ROOT / SOURCE).read_bytes()
    if sha(raw) != SOURCE_SHA:
        raise SystemExit(f"FAIL source sha {sha(raw)} != {SOURCE_SHA}")
    src = Image.open(io.BytesIO(raw))
    src.load()
    if src.size != SOURCE_SIZE:
        raise SystemExit(f"FAIL source size {src.size}")
    if src.mode != "RGBA":
        raise SystemExit(f"FAIL source mode {src.mode}")
    if sha(src.convert("RGBA").tobytes()) != SOURCE_RAW_RGBA_SHA:
        raise SystemExit("FAIL source raw RGBA pin")
    man_raw = (ROOT / SOURCE_MANIFEST).read_bytes()
    if sha(man_raw) != SOURCE_MANIFEST_SHA:
        raise SystemExit("FAIL source manifest sha")
    sm = json.loads(man_raw)
    if sm.get("files", {}).get("png", {}).get("rawsha256") != SOURCE_SHA:
        raise SystemExit("FAIL source manifest does not pin the source PNG")
    for k, (p, h) in EDITABLE.items():
        if sha((ROOT / p).read_bytes()) != h:
            raise SystemExit(f"FAIL editable {k} sha")
        if sm["files"][k]["rawsha256"] != h:
            raise SystemExit(f"FAIL source manifest {k} pin")
    out = replicate(src)
    buf = io.BytesIO()
    out.save(buf, format="PNG", optimize=False, compress_level=9)
    return src, out, buf.getvalue(), sha(src.tobytes()), sha(out.tobytes())


def manifest(src, out, png: bytes, src_raw: str, raw_hash: str) -> bytes:
    opaque = sum(1 for a in out.getchannel("A").tobytes() if a > 0)
    data = {
        "schema": "ds-portrait/display-image-manifest/v1",
        "content_id": "content.char.heya.display",
        "run_id": RUN,
        "subject": "heya",
        "status": "UNAPPROVED display image; derived from the unapproved native south static; not wired into any default",
        "source": {
            "path": SOURCE, "sha256": SOURCE_SHA, "width": SOURCE_SIZE[0], "height": SOURCE_SIZE[1],
            "mode": src.mode, "raw_rgba_sha256": src_raw,
            "role": "native-south-static-source", "source_commit": SOURCE_COMMIT
        },
        "source_manifest": {
            "path": SOURCE_MANIFEST, "sha256": SOURCE_MANIFEST_SHA,
            "content_id": "content.char.heya.static-south", "pivot": [40, 104],
            "body_rows": [8, 103], "display_scale": 0.5
        },
        "editable_sources": {k: {"path": p, "sha256": h} for k, (p, h) in EDITABLE.items()},
        "transform": {
            "method": "nearest-neighbor-integer-upscale", "factor": FACTOR,
            "source_rect": [0, 0, SOURCE_SIZE[0], SOURCE_SIZE[1]],
            "coordinate_space": "source texels, top-left origin, right/bottom exclusive",
            "resampled": True, "pixel_replication_only": True,
            "repainted": False, "ai_generated_new_pixels": False,
            "new_colour_values": False, "alpha_preserved": True
        },
        "output": {
            "path": DISPLAY.relative_to(ROOT).as_posix(), "width": out.size[0], "height": out.size[1],
            "mode": out.mode, "file_sha256": sha(png), "raw_rgba_sha256": raw_hash,
            "opaque_texels": opaque
        },
        "display_rule": "2x integer nearest replication; shown at native 160x224 in the 180x250 frame without further scaling",
        "identity": {
            "en": "Heya", "zh": "赫娅", "age": 44, "role_en": "Clinician", "role_zh": "诊疗师",
            "anchors_en": ["auburn braided coil low at the nape", "grey-white medical scarf",
                           "ivory clinician coat", "dark-red emergency bag"],
            "anchors_zh": ["赤褐色盘辫低置颈后", "灰白医巾", "象牙白诊疗外套", "暗红急救袋"],
            "canon_ref": "outputs/rpg-2-star-ocean-the-second_game-bible_state_v01_20261013-195422-b8c16d42.json character-26"
        },
        "pipeline_precedent": "tools/rpg-2-star-ocean-the-second_yanke_display-build_v01_20261024-100318-10cf38b5.py",
    }
    return (json.dumps(data, indent=2, ensure_ascii=False) + "\n").encode("utf-8")


def write_safe(path: Path, data: bytes) -> None:
    if path.exists():
        if path.read_bytes() == data:
            return
        raise SystemExit(f"REFUSE overwrite of differing {path.name}")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(data)


def main() -> int:
    mode = sys.argv[1] if len(sys.argv) > 1 else ""
    if mode not in ("build", "check"):
        print(__doc__)
        return 2
    src, out, png, src_raw, raw_hash = derive()
    man = manifest(src, out, png, src_raw, raw_hash)
    if mode == "build":
        write_safe(DISPLAY, png)
        write_safe(MANIFEST, man)
    fails = []
    if not DISPLAY.exists() or DISPLAY.read_bytes() != png:
        fails.append("display bytes differ from deterministic derivation")
    if not MANIFEST.exists() or MANIFEST.read_bytes() != man:
        fails.append("manifest bytes differ")
    if DISPLAY.exists():
        got = Image.open(DISPLAY).convert("RGBA")
        if got.size != (SOURCE_SIZE[0] * FACTOR, SOURCE_SIZE[1] * FACTOR):
            fails.append(f"display size {got.size}")
        if sha(got.tobytes()) != raw_hash:
            fails.append("display raw pixels != exact replication")
        g, s = got.load(), src.convert("RGBA").load()
        bad = next(((x, y) for y in range(src.height) for x in range(src.width)
                    for dy in range(FACTOR) for dx in range(FACTOR)
                    if g[x * FACTOR + dx, y * FACTOR + dy] != s[x, y]), None)
        if bad is not None:
            fails.append(f"pixel mismatch at {bad}")
    for f in fails:
        print("FAIL", f)
    print("HDISPLAY179_BUILD", "OK" if not fails else "FAIL", src_raw, raw_hash)
    return 0 if not fails else 1


if __name__ == "__main__":
    sys.exit(main())
