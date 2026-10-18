"""Walk reachability check for the Chicago Loop State/Lake v05 material-depth pass (UNAPPROVED, opt-in).

Usage: python -I <this file> [--report <json path>]
Flood-fills the authored walk mask (author.walkable, 4-connected) from the arrival spawn and checks that
  RCH1 every walkable pixel is one region reachable from the spawn;
  RCH2 each of the three read-only sites (kiosk, stair, pylon) is a reachable standing spot;
  RCH3 the under-L lane, the State St crosswalk and the stair foot used by the Godot captures are reachable;
  RCH4 the v05 walk grid and blocks equal the v04 author's (v05 changes art only).
"""

from __future__ import annotations

from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path
import argparse
import json
import sys
from collections import deque

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
PRE = "rpg-2-star-ocean-the-second_chicago-loop_state-lake-block-pixel-author_unapproved-"
AUTHORS = {"v05": ROOT / f"tools/{PRE}v05_20261017-234337-84862412.py", "v04": ROOT / f"tools/{PRE}v04_20261017-230650-c0d4b7f0.py"}
CAPTURE_SPOTS = {"under-l-lane-east": (565, 220), "under-l-lane-mid": (300, 220), "crosswalk": (40, 240), "stair-foot": (560, 222),
                 "open-plaza": (300, 220), "behind-west-column": (140, 182), "approved-ref": (296, 228)}


def load(path, name):
    spec = spec_from_file_location(name, path)
    mod = module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def reach(grid, start):
    seen = np.zeros_like(grid)
    q = deque([start[::-1]])
    seen[start[1], start[0]] = True
    while q:
        y, x = q.popleft()
        for yy, xx in ((y - 1, x), (y + 1, x), (y, x - 1), (y, x + 1)):
            if 0 <= yy < grid.shape[0] and 0 <= xx < grid.shape[1] and grid[yy, xx] and not seen[yy, xx]:
                seen[yy, xx] = True
                q.append((yy, xx))
    return seen


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--report", default="")
    a = ap.parse_args()
    v5, v4 = load(AUTHORS["v05"], "chi_author_v05"), load(AUTHORS["v04"], "chi_author_v04")
    grid = v5.walk_grid()
    seen = reach(grid, v5.SPAWN)
    sites = {"kiosk": v5.KIOSK, "stair": v5.STAIR, "pylon": v5.PYLON}
    r = {"walkable_px": int(grid.sum()), "reachable_px": int(seen.sum()),
         "sites": {k: bool(seen[p[1], p[0]]) for k, p in sites.items()},
         "capture_spots": {k: bool(seen[p[1], p[0]]) for k, p in CAPTURE_SPOTS.items()}}
    gates = {"RCH1_one_region_from_spawn": r["reachable_px"] == r["walkable_px"] > 60000,
             "RCH2_sites_reachable": all(r["sites"].values()),
             "RCH3_capture_spots_reachable": all(r["capture_spots"].values()),
             "RCH4_walk_grid_and_blocks_equal_v04": bool((grid == v4.walk_grid()).all()) and v5.BLOCKS == v4.BLOCKS and v5.WALK == v4.WALK}
    report = {"gates": gates, "passed": sum(gates.values()), "total": len(gates), "details": r}
    if a.report:
        Path(a.report).write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    for k, v in gates.items():
        print(("PASS " if v else "FAIL ") + k)
    print(json.dumps(r))
    print(f"CHICAGO_LOOP_V05_WALK_REACHABILITY {report['passed']}/{report['total']}")
    return 0 if report["passed"] == report["total"] else 1


if __name__ == "__main__":
    sys.exit(main())
