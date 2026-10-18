"""Pixel comparison for the opt-in sentry v2 pilot default-off parity captures (UNAPPROVED, art acceptance 0).

Usage: python -I <this file> <parity-dir> <stamp> [<report.json>]

<parity-dir> holds the three runs of one stamp from the companion Godot capture script: `--variant=base` against the
base eb70de1 export, `--variant=off` against the candidate worktree without a flag, and `--variant=on` against the
candidate worktree with `--sentry-v2-pilot`. Captures are paired by the name between the variant and the stamp
(<PREFIX>_<variant>-<enemy>-<state>-<language>-<window>_<stamp>.png). Pass rules:
  - every default-off capture equals the base capture pixel for pixel (RGBA, 0 differing pixels);
  - with the flag on, every patrol capture still equals the base (the flag is sentry only);
  - with the flag on, every sentry capture differs from the base (the pilot really renders).
"""

import hashlib
import json
import os
import re
import sys
from pathlib import Path

from PIL import Image

PREFIX = "rpg-2-star-ocean-the-second_sentry-v2-parity"
STAMP_PATTERN = re.compile(r"^[0-9]{8}-[0-9]{6}-[0-9a-f]{8}$")


def capture_name(variant, key, stamp):
    return "%s_%s-%s_%s.png" % (PREFIX, variant, key, stamp)


def load(path):
    with Image.open(path) as image:
        return image.convert("RGBA")


def diff(a, b):
    if a.size != b.size:
        return {"sizeA": list(a.size), "sizeB": list(b.size), "differingPixels": None, "bbox": None}
    pa = a.tobytes()
    pb = b.tobytes()
    count = 0
    x0 = y0 = 10**9
    x1 = y1 = -1
    width = a.size[0]
    for offset in range(0, len(pa), 4):
        if pa[offset:offset + 4] != pb[offset:offset + 4]:
            count += 1
            pixel = offset // 4
            x, y = pixel % width, pixel // width
            x0, y0, x1, y1 = min(x0, x), min(y0, y), max(x1, x), max(y1, y)
    return {"differingPixels": count, "bbox": [x0, y0, x1, y1] if count else None}


def sha256(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def long_path(path):
    # Stamped names in a worktree's outputs dir pass MAX_PATH (260) on Windows; use the extended-length prefix there.
    text = os.path.abspath(path)
    if os.name == "nt" and not text.startswith("\\\\?\\"):
        text = "\\\\?\\" + text
    return Path(text)


def main():
    parity_dir = long_path(sys.argv[1])
    stamp = sys.argv[2]
    if not STAMP_PATTERN.match(stamp):
        sys.exit("stamp must be YYYYMMDD-HHMMSS-<8 lowercase hex>")
    report_path = long_path(sys.argv[3]) if len(sys.argv) > 3 else None
    head = PREFIX + "_base-"
    tail = "_" + stamp + ".png"
    keys = sorted(p.name[len(head):-len(tail)] for p in parity_dir.glob(head + "*" + tail))
    rows = []
    failures = []
    for key in keys:
        paths = {variant: parity_dir / capture_name(variant, key, stamp) for variant in ("base", "off", "on")}
        missing = [str(path.name) for path in paths.values() if not path.is_file()]
        if missing:
            failures.append("missing capture: %s" % ", ".join(missing))
            continue
        base = load(paths["base"])
        off = load(paths["off"])
        on = load(paths["on"])
        off_diff = diff(base, off)
        on_diff = diff(base, on)
        enemy = key.split("-")[0]
        rows.append({"key": key, "enemy": enemy, "baseFile": paths["base"].name, "defaultOffFile": paths["off"].name, "flagOnFile": paths["on"].name,
                     "baseSha256": sha256(paths["base"]), "defaultOffSha256": sha256(paths["off"]),
                     "flagOnSha256": sha256(paths["on"]), "defaultOffVsBase": off_diff, "flagOnVsBase": on_diff})
        if off_diff["differingPixels"] != 0:
            failures.append("default-off differs from base: %s %s" % (key, off_diff))
        if enemy == "patrol" and on_diff["differingPixels"] != 0:
            failures.append("flag-on patrol differs from base: %s %s" % (key, on_diff))
        if enemy == "sentry" and not on_diff["differingPixels"]:
            failures.append("flag-on sentry equals base (pilot not rendered): %s" % key)
    if len(keys) != 32:
        failures.append("expected 32 captures, found %d" % len(keys))
    report = {"stamp": stamp, "captures": len(keys), "failures": failures, "rows": rows,
              "summary": {"defaultOffZeroDiff": sum(1 for r in rows if r["defaultOffVsBase"]["differingPixels"] == 0),
                          "flagOnPatrolZeroDiff": sum(1 for r in rows if r["enemy"] == "patrol" and r["flagOnVsBase"]["differingPixels"] == 0),
                          "flagOnSentryDiffers": sum(1 for r in rows if r["enemy"] == "sentry" and r["flagOnVsBase"]["differingPixels"])}}
    if report_path is not None:
        report_path.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8", newline="\n")
    for row in rows:
        print("%s off=%s on=%s" % (row["key"], row["defaultOffVsBase"]["differingPixels"], row["flagOnVsBase"]["differingPixels"]))
    print("SUMMARY %s" % json.dumps(report["summary"]))
    if failures:
        for failure in failures:
            print("FAIL " + failure)
        sys.exit(1)
    print("SENTRY_V2_DEFAULT_PARITY PASS")


if __name__ == "__main__":
    main()
