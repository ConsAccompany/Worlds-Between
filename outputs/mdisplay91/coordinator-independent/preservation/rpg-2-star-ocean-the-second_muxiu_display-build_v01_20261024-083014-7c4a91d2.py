"""Muxiu display image: deterministic nearest-neighbour integer 2x of the committed native south static.

Derived from the credited Lin Que display64 crop builder; the pipeline is the same (pinned source ->
deterministic derivation -> manifest -> UI scene -> contract/malformed/probe checks) but the transform is
an exact integer pixel replication, not a rectangle slice, because the native south static is already the
authoritative 80x112 sprite. No repaint, no new generative pixels, no concept art, no default adoption.

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
RUN = "20261024-083014-7c4a91d2"
SOURCE = "game/assets/characters/muxiu-native-v01/south/rpg-2-star-ocean-the-second_muxiu_south-static_unapproved-v01_20261024-071500-ca23fad5.png"
SOURCE_SHA = "e14d5c50890d7fcd0c75eb362d2b08fd1d4ac02c9c33e04fc4861b5a7d7a26fe"
SOURCE_SIZE = (80, 112)
SOURCE_MANIFEST = "game/assets/characters/muxiu-native-v01/south/rpg-2-star-ocean-the-second_muxiu_south-manifest_unapproved-v01_20261024-071500-dd478113.json"
SOURCE_MANIFEST_SHA = "24c751575fe02a4857628dbfb8b379cd1d42344167062ae8ddbb033024e114de"
SOURCE_RAW_RGBA_SHA = "02cbb1d00a22eb4268bc40eddbfb5179b106f703645150c8f096bd06f50b5faa"
FACTOR = 2
OUT_DIR = ROOT / "game/assets/portraits/mdisplay91"
DISPLAY = OUT_DIR / f"rpg-2-star-ocean-the-second_muxiu_display-portrait_v01_{RUN}.png"
MANIFEST = OUT_DIR / f"rpg-2-star-ocean-the-second_muxiu_display-portrait-manifest_v01_{RUN}.json"


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
    if sha(src.tobytes()) != SOURCE_RAW_RGBA_SHA:
        raise SystemExit("FAIL source raw RGBA pin")
    man_raw = (ROOT / SOURCE_MANIFEST).read_bytes()
    if sha(man_raw) != SOURCE_MANIFEST_SHA:
        raise SystemExit("FAIL source manifest sha")
    out = replicate(src)
    buf = io.BytesIO()
    out.save(buf, format="PNG", optimize=False, compress_level=9)
    return src, out, buf.getvalue(), sha(out.tobytes())


def manifest(src, out, png: bytes, raw_hash: str) -> bytes:
    data = {
        "schema": "ds-portrait/display-image-manifest/v1",
        "content_id": "content.char.muxiu.display",
        "run_id": RUN,
        "subject": "muxiu",
        "status": "UNAPPROVED display image; derived from the unapproved native south static; not wired into any default",
        "source": {
            "path": SOURCE, "sha256": SOURCE_SHA, "width": SOURCE_SIZE[0], "height": SOURCE_SIZE[1],
            "mode": src.mode, "raw_rgba_sha256": SOURCE_RAW_RGBA_SHA,
            "role": "native-south-static-source"
        },
        "source_manifest": {
            "path": SOURCE_MANIFEST, "sha256": SOURCE_MANIFEST_SHA,
            "content_id": "content.char.muxiu.static-south", "pivot": [40, 104],
            "body_rows": [8, 103], "display_scale": 0.5
        },
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
            "mode": out.mode, "file_sha256": sha(png), "raw_rgba_sha256": raw_hash
        },
        "display_rule": "2x integer nearest replication; shown at native 160x224 in the 180x250 frame without further scaling",
        "identity": {
            "en": "Muxiu", "zh": "牧修", "age": 24, "role_en": "Animal carer", "role_zh": "动物照护者",
            "anchors_en": ["moss-green short cape", "knotted rope bracelet", "small whistle", "moving braid"],
            "anchors_zh": ["苔绿色短斗篷", "绳结手环", "小巧呼哨", "轻晃发辫"]
        },
        "pipeline_precedent": "tools/rpg-2-star-ocean-the-second_lin-que_display-crop-build_v01_20261023-214513-92b6d62b.py",
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
    src, out, png, raw_hash = derive()
    man = manifest(src, out, png, raw_hash)
    if mode == "build":
        write_safe(DISPLAY, png)
        write_safe(MANIFEST, man)
    fails = []
    if not DISPLAY.exists() or DISPLAY.read_bytes() != png:
        fails.append("display bytes differ from deterministic derivation")
    if not MANIFEST.exists() or MANIFEST.read_bytes() != man:
        fails.append("manifest bytes differ")
    if DISPLAY.exists():
        got = Image.open(DISPLAY)
        if got.size != (SOURCE_SIZE[0] * FACTOR, SOURCE_SIZE[1] * FACTOR):
            fails.append(f"display size {got.size}")
        if sha(got.convert("RGBA").tobytes()) != raw_hash:
            fails.append("display raw pixels != exact replication")
        g = got.convert("RGBA").load()
        s = src.load()
        for y in range(src.height):
            for x in range(src.width):
                want = s[x, y]
                for dy in range(FACTOR):
                    for dx in range(FACTOR):
                        if g[x * FACTOR + dx, y * FACTOR + dy] != want:
                            fails.append(f"pixel mismatch at {x},{y}")
                            break
                    else:
                        continue
                    break
            else:
                continue
            break
    for f in fails:
        print("FAIL", f)
    print("MDISPLAY91_BUILD", "OK" if not fails else "FAIL", raw_hash)
    return 0 if not fails else 1


if __name__ == "__main__":
    sys.exit(main())
