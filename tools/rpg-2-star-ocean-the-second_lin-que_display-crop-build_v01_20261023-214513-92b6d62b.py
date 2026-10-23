"""Lin Que display portrait: exact pixel crop of the UNAPPROVED concept source sheet (no repaint/resample).

Derived from the credited Jiang Lan display40 builder; only the subject, source pin and rectangle differ.
The rectangle holds the whole front-view figure (measured bbox 40,11,583,798 against the sheet background)
with margin, excludes the back view (starts x=604), and has the 180x250 display box aspect (0.72).

Usage: python -I <this> build   -> writes crop PNG + manifest (refuses to overwrite differing bytes)
       python -I <this> check   -> re-derives crop from source and verifies pins; exit 1 on any failure
"""
import hashlib
import io
import json
import sys
from pathlib import Path

from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
RUN = "20261023-214513-92b6d62b"
SOURCE = "outputs/rpg-2-star-ocean-the-second_lin-que_character-sheet_v01_20261013-153556-88b92720.png"
SOURCE_SHA = "24007e147c9dd67b330af4a84ac13054f65989cddb9bdf2702dc5c80de7fb352"
SOURCE_SIZE = (1916, 821)
RECT = (16, 0, 592, 800)  # left, top, right(excl), bottom(excl)
OUT_DIR = ROOT / "game/assets/portraits/ldisplay64"
CROP = OUT_DIR / f"rpg-2-star-ocean-the-second_lin-que_display-portrait-crop_v01_{RUN}.png"
MANIFEST = OUT_DIR / f"rpg-2-star-ocean-the-second_lin-que_display-portrait-manifest_v01_{RUN}.json"


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def derive():
    raw = (ROOT / SOURCE).read_bytes()
    if sha(raw) != SOURCE_SHA:
        raise SystemExit(f"FAIL source sha {sha(raw)} != {SOURCE_SHA}")
    src = Image.open(io.BytesIO(raw))
    src.load()
    if src.size != SOURCE_SIZE:
        raise SystemExit(f"FAIL source size {src.size}")
    crop = src.crop(RECT)
    rgba_raw = crop.convert("RGBA").tobytes()
    buf = io.BytesIO()
    crop.save(buf, format="PNG", optimize=False, compress_level=9)
    return src, crop, buf.getvalue(), sha(rgba_raw)


def manifest(src, crop, png: bytes, raw_hash: str) -> bytes:
    data = {
        "schema": "ds-portrait/display-image-manifest/v1",
        "content_id": "content.char.lin-que.display",
        "run_id": RUN,
        "subject": "lin-que",
        "status": "UNAPPROVED display crop; source portrait is an unaccepted concept; not wired into any default",
        "source": {"path": SOURCE, "sha256": SOURCE_SHA, "width": SOURCE_SIZE[0], "height": SOURCE_SIZE[1],
                   "mode": src.mode, "role": "unapproved-concept-source-portrait"},
        "crop": {"left": RECT[0], "top": RECT[1], "right": RECT[2], "bottom": RECT[3],
                 "coordinate_space": "source pixels, top-left origin, right/bottom exclusive",
                 "method": "exact-pixel-rectangle-slice", "resampled": False, "repainted": False,
                 "ai_generated_new_pixels": False, "pixelized": False},
        "output": {"path": CROP.relative_to(ROOT).as_posix(), "width": crop.size[0], "height": crop.size[1],
                   "mode": crop.mode, "file_sha256": sha(png), "raw_rgba_sha256": raw_hash},
        "display_rule": "nearest filter, keep aspect, no upscale beyond fit box",
        "pipeline_precedent": "tools/rpg-2-star-ocean-the-second_jiang-lan_display-crop-build_v01_20261022-155956-1414792c.py",
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
    src, crop, png, raw_hash = derive()
    man = manifest(src, crop, png, raw_hash)
    if mode == "build":
        write_safe(CROP, png)
        write_safe(MANIFEST, man)
    fails = []
    if not CROP.exists() or CROP.read_bytes() != png:
        fails.append("crop bytes differ from deterministic derivation")
    if not MANIFEST.exists() or MANIFEST.read_bytes() != man:
        fails.append("manifest bytes differ")
    if CROP.exists():
        got = Image.open(CROP)
        if got.size != (RECT[2] - RECT[0], RECT[3] - RECT[1]):
            fails.append(f"crop size {got.size}")
        if sha(got.convert("RGBA").tobytes()) != raw_hash:
            fails.append("crop raw pixels != source rect")
    for f in fails:
        print("FAIL", f)
    print("LDISPLAY64_CROP", "OK" if not fails else "FAIL", raw_hash)
    return 0 if not fails else 1


if __name__ == "__main__":
    sys.exit(main())
