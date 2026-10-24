"""Yanke display image: deterministic nearest-neighbour integer 2x of the committed native south static.

Reuses the credited Muxiu mdisplay91 builder (itself derived from the Lin Que display64 pipeline): pinned source ->
deterministic derivation -> manifest -> UI scene -> contract/malformed/probe checks. The transform is an exact
integer pixel replication of the authoritative 80x112 south static. No repaint, no new generative pixels,
no concept art, no default adoption. The editable PXO/ORA sources are pinned as provenance only.

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
RUN = "20261024-100318-10cf38b5"
SDIR = "game/assets/characters/yanke-native-v01/south"
SOURCE = f"{SDIR}/rpg-2-star-ocean-the-second_yanke_south-static_unapproved-v01_20261024-084428-73949161.png"
SOURCE_SHA = "4f6bcf937390e300e2829ac052bcb1047fdb6387de41561490c757246a32fef0"
SOURCE_SIZE = (80, 112)
SOURCE_MANIFEST = f"{SDIR}/rpg-2-star-ocean-the-second_yanke_south-manifest_unapproved-v01_20261024-084428-4305a59b.json"
SOURCE_MANIFEST_SHA = "e57f5c93131daffff56bc75a47d9a2c1357f4c337797ea0d07c0c73918692e7e"
EDITABLE = {
    "pxo": (f"{SDIR}/rpg-2-star-ocean-the-second_yanke_south-edit_unapproved-v01_20261024-084428-5b76b5f2.pxo",
            "173779784354c7d2decbc87a0c13edfc2928d70aeabc91772e63d950d0b20992"),
    "ora": (f"{SDIR}/rpg-2-star-ocean-the-second_yanke_south-edit_unapproved-v01_20261024-084428-e87e7c42.ora",
            "d536eae42395ce5765f6b1f4eb201203ef0c77d44a4285568adf3ed6d2e67267"),
    "palette": (f"{SDIR}/rpg-2-star-ocean-the-second_yanke_south-palette_unapproved-v01_20261024-084428-76f9bb9e.json",
                "018567be5e0f4c73b71abdfd719088a99b29e0f4b696f6425137dbf357048d9b"),
}
SOURCE_COMMIT = "234cfabe"
FACTOR = 2
OUT_DIR = ROOT / "game/assets/portraits/ydisplay111"
DISPLAY = OUT_DIR / f"rpg-2-star-ocean-the-second_yanke_display-portrait_v01_{RUN}.png"
MANIFEST = OUT_DIR / f"rpg-2-star-ocean-the-second_yanke_display-portrait-manifest_v01_{RUN}.json"


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
        "content_id": "content.char.yanke.display",
        "run_id": RUN,
        "subject": "yanke",
        "status": "UNAPPROVED display image; derived from the unapproved native south static; not wired into any default",
        "source": {
            "path": SOURCE, "sha256": SOURCE_SHA, "width": SOURCE_SIZE[0], "height": SOURCE_SIZE[1],
            "mode": src.mode, "raw_rgba_sha256": src_raw,
            "role": "native-south-static-source", "source_commit": SOURCE_COMMIT
        },
        "source_manifest": {
            "path": SOURCE_MANIFEST, "sha256": SOURCE_MANIFEST_SHA,
            "content_id": "content.char.yanke.static-south", "pivot": [40, 104],
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
            "en": "Yanke", "zh": "岩柯", "age": 37, "role_en": "Heavy-tool craftsperson", "role_zh": "重型工具匠",
            "anchors_en": ["broad leather shoulder straps", "dark-brown work trousers", "notched heavy tool head",
                           "short curls and thick beard"],
            "anchors_zh": ["宽大的皮质肩带", "深棕工作裤", "带缺口的重型工具头", "短卷发与浓胡须"],
            "canon_ref": "outputs/rpg-2-star-ocean-the-second_game-bible_state_v01_20261013-195422-b8c16d42.json character-07"
        },
        "pipeline_precedent": "tools/rpg-2-star-ocean-the-second_muxiu_display-build_v01_20261024-083014-7c4a91d2.py",
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
    print("YDISPLAY111_BUILD", "OK" if not fails else "FAIL", src_raw, raw_hash)
    return 0 if not fails else 1


if __name__ == "__main__":
    sys.exit(main())
