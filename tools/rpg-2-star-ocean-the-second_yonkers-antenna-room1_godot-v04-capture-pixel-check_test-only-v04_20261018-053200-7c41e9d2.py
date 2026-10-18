"""Pixel check of the actual Godot v04 test-only captures (Yonkers antenna corridor room 1).

For each zh/en entry capture, takes the plate pixels that v04 changed against v03, minus those under an opaque antenna or
foreground texel (their screen boxes are known), and counts how many equal v04 versus v03. Pixels covered by UI or the
heroine match neither plate and are simply not counted.
A real v04 render must match v04 on all of them. Also confirms the 30 captures are 640x360 and the log has
YK1_V04_ALL_OK, YK1_V04_TEXTURES_IN_USE and no script error.

Usage: python -I <this file>
"""
import json
from pathlib import Path

import numpy as np
from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "outputs/yonkers-room1-v04_523bba3b"
CAP = OUT / "godot-test-only"
STAMP = "20261018-053200-7c41e9d2"
LOG = OUT / f"rpg-2-star-ocean-the-second_yonkers-antenna-room1_godot-v04-test-only-check-log_{STAMP}.txt"
V03 = ROOT / "game/assets/environments/yonkers-antenna-room1/rpg-2-star-ocean-the-second_yonkers-antenna-room1_corridor-plate_unapproved-v03_20261017-224447-15709be4.png"
V04 = OUT / "nonruntime-exports/rpg-2-star-ocean-the-second_yonkers-antenna-room1_corridor-plate-material-depth_unapproved-v04_20261018-052445-523bba3b.png"


def rgb(p):
    return np.array(Image.open(p).convert("RGB")).astype(np.int16)


def main():
    p3, p4 = rgb(V03), rgb(V04)
    changed = (p3 != p4).any(axis=2)
    exports = OUT / "nonruntime-exports"
    covered = np.array(Image.open(next(exports.glob("*_foreground-occluder_*.png"))).convert("RGBA"))[..., 3] > 0
    for x, slug in zip((163, 320, 477), ("antenna-a-lattice-yagi", "antenna-b-dish", "antenna-c-guyed-whip")):
        alpha = np.array(Image.open(next(exports.glob(f"*_{slug}_*.png"))).convert("RGBA"))[..., 3] > 0
        covered[58:210, x - 64:x + 64] |= alpha
    changed &= ~covered
    rep = {"changed_plate_px": int(changed.sum()), "captures": {}}
    for lang in ("zh", "en"):
        cap = rgb(CAP / f"rpg-2-star-ocean-the-second_yonkers-antenna-room1_v04-material-depth-test-only-godot-{lang}-entry-640x360_{STAMP}.png")
        eq4 = (cap == p4).all(axis=2) & changed
        eq3 = (cap == p3).all(axis=2) & changed
        rep["captures"][lang] = {"visible_changed_px_matching_v04": int(eq4.sum()), "matching_v03": int(eq3.sum())}
    names = sorted(p.name for p in CAP.glob("*.png"))
    rep["capture_count"] = len(names)
    rep["all_640x360"] = all(Image.open(CAP / n).size == (640, 360) for n in names)
    log = LOG.read_text(encoding="utf-8", errors="replace")
    rep["log_all_ok"] = "YK1_V04_ALL_OK" in log and "YK1_V04_TEXTURES_IN_USE" in log
    rep["log_fail_or_script_errors"] = log.count("YK1_V04_FAIL") + log.count("SCRIPT ERROR")
    ok = all(c["visible_changed_px_matching_v04"] > 5000 and c["matching_v03"] == 0 for c in rep["captures"].values()) \
        and rep["capture_count"] == 30 and rep["all_640x360"] and rep["log_all_ok"] and rep["log_fail_or_script_errors"] == 0
    rep["result"] = "PASS" if ok else "FAIL"
    path = OUT / f"rpg-2-star-ocean-the-second_yonkers-antenna-room1_godot-v04-capture-pixel-check-report_test-only_{STAMP}.json"
    path.write_text(json.dumps(rep, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(rep))
    print("V04_CAPTURE_PIXEL_CHECK " + rep["result"])


if __name__ == "__main__":
    main()
