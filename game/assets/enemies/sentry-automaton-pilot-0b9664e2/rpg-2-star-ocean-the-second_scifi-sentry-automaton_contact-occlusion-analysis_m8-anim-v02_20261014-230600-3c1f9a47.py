"""Measure how much of the sentry's eye and claw the melee heroes cover, v1 against v2 (review aid, not shipped).

Composites the real native hero combat frames over the sentry strip cells in the battle's logical
640x360 space, the way battle_arena.gd draws them: hero cell at (hero_x - 30, 272 - 73), sentry
cell at (enemy_x - anchor_x, 272 - 60). Heroes stand at their real AI melee spacing: the sentry
stops 53 px from its target, the hero (range 61) closes to 53 px and Liang Xu (range 65) to 57 px.

Expressive regions per sentry frame (opaque sentry pixels inside):
  eye  - the brass bezel box (static x 10..30, y 12..32) moved by the frame's head offset
  claw - the near-front foot and lower shin box (static x 1..19, y 45..59) moved by the foot offset
Covered = a hero pixel is drawn on top of it. In v2 the sentry draws over the fighters during its own
strike, so nothing covers its strike frames; the hero pixels it hides are reported instead.

Usage: python -I <this file> --out outputs/<name>.json
"""

from __future__ import annotations

import argparse
import glob
import importlib.util
import json
from pathlib import Path

from PIL import Image

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
HERO_DIR = ROOT / "game/assets/characters/combat-prototypes"
V1_STRIP = HERE / "rpg-2-star-ocean-the-second_scifi-sentry-automaton_battle-animation-strip-left_m8-anim-v01_20261014-223820-f181f893.png"
V2_AUTHOR = HERE / "rpg-2-star-ocean-the-second_scifi-sentry-automaton_battle-animation-pilot-author_m8-anim-v02_20261014-225908-7e2215bc.py"
V1_AUTHOR = HERE / "rpg-2-star-ocean-the-second_scifi-sentry-automaton_battle-animation-pilot-author_m8-anim-v01_20261014-223554-0ae02683.py"
FLOOR = 272
HERO_ANCHOR = (30, 73)
ENEMY_X = 353
MEMBERS = {"protagonist-male": 53, "protagonist-female": 53, "liang-xu": 57}
# Hero actions that coincide with each sentry state in play.
PAIRINGS = {"windup": ["idle", "attack", "guard"], "strike": ["hit", "guard", "idle"], "hit": ["attack", "skill"]}


def load(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def hero_frames(member: str, action: str) -> list:
    files = sorted(set(glob.glob(str(HERO_DIR / f"*{member}_sideview-{action}-right-phase-*.png"))))
    return [(Path(f).name, Image.open(f).convert("RGBA")) for f in files]


def regions(p: dict, margin: int) -> dict:
    hx, hy = p["head"]
    (fx, fy) = p["nfl"][1]
    return {"eye": (10 + hx + margin, 12 + hy, 30 + hx + margin, 32 + hy),
            "claw": (1 + fx + margin, 45 + fy, 19 + fx + margin, 59 + fy)}


def measure(cell: Image.Image, origin: tuple, boxes: dict, hero: Image.Image, hero_origin: tuple, sentry_on_top: bool) -> dict:
    cp, hp = cell.load(), hero.load()
    out = {}
    for name, (x0, y0, x1, y1) in boxes.items():
        total = covered = 0
        for y in range(max(0, y0), min(cell.height, y1 + 1)):
            for x in range(max(0, x0), min(cell.width, x1 + 1)):
                if cp[x, y][3] == 0:
                    continue
                total += 1
                sx, sy = origin[0] + x - hero_origin[0], origin[1] + y - hero_origin[1]
                if not sentry_on_top and 0 <= sx < hero.width and 0 <= sy < hero.height and hp[sx, sy][3] > 0:
                    covered += 1
        out[name] = round(covered / max(1, total), 3)
    # Hero pixels hidden under the sentry when it is drawn on top.
    hidden = 0
    if sentry_on_top:
        for y in range(hero.height):
            for x in range(hero.width):
                if hp[x, y][3] == 0:
                    continue
                cx, cy = hero_origin[0] + x - origin[0], hero_origin[1] + y - origin[1]
                if 0 <= cx < cell.width and 0 <= cy < cell.height and cp[cx, cy][3] > 0:
                    hidden += 1
    out["heroPixelsHidden"] = hidden
    return out


def run_version(label: str, cells: list, frames: list, states: dict, anchor_x: int, margin: int, front_states: set) -> dict:
    result = {}
    for state, actions in PAIRINGS.items():
        for frame in states[state]:
            pose = frames[frame][1]
            boxes = regions(pose, margin)
            origin = (ENEMY_X - anchor_x, FLOOR - 60)
            for member, spacing in MEMBERS.items():
                hero_x = ENEMY_X - spacing
                hero_origin = (hero_x - HERO_ANCHOR[0], FLOOR - HERO_ANCHOR[1])
                for action in actions:
                    for name, img in hero_frames(member, action):
                        key = f"{state}|f{frame}|{member}|{action}|{name.split('_sideview-')[1].split('_')[0]}"
                        result[key] = measure(cells[frame], origin, boxes, img, hero_origin, state in front_states)
    return result


def summarize(rows: dict) -> dict:
    by = {}
    for key, v in rows.items():
        state, _, member, action, _ = key.split("|")
        for region in ("eye", "claw"):
            by.setdefault(f"{state}|{action}|{region}", []).append(v[region])
    return {k: {"mean": round(sum(v) / len(v), 3), "max": max(v), "n": len(v)} for k, v in sorted(by.items())}


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", type=Path, required=True)
    args = ap.parse_args()
    v1 = load(V1_AUTHOR, "sentry_v1_author")
    v2 = load(V2_AUTHOR, "sentry_v2_author")
    v1_strip = Image.open(V1_STRIP).convert("RGBA")
    v1_cells = [v1_strip.crop((i * 96, 0, (i + 1) * 96, 62)) for i in range(v1_strip.width // 96)]
    v2_cells = v2.render_all()
    v1_states = {"windup": [8, 9], "strike": [10, 11], "hit": [12, 13]}
    v2_states = {"windup": [12, 13], "strike": [14, 15], "hit": [16, 17]}
    rows_v1 = run_version("v1", v1_cells, v1.FRAMES, v1_states, 48, 0, set())
    rows_v2 = run_version("v2", v2_cells, v2.FRAMES, v2_states, v2.RUNTIME_ANCHOR[0], v2.MARGIN, {"strike"})
    # The same v2 frames and anchor with the heroes always on top, to separate the layering from the spacing.
    rows_v2_flat = run_version("v2-heroes-on-top", v2_cells, v2.FRAMES, v2_states, v2.RUNTIME_ANCHOR[0], v2.MARGIN, set())
    report = {
        "project": "rpg-2-star-ocean-the-second",
        "purpose": "sentry eye/claw coverage by melee heroes at real AI spacing, v1 against v2 (review aid; not art acceptance)",
        "method": __doc__.strip().splitlines()[2:13],
        "enemyX": ENEMY_X,
        "spacing": MEMBERS,
        "v1": {"anchorX": 48, "cell": [96, 62], "sentryOnTopStates": [], "summary": summarize(rows_v1), "rows": rows_v1},
        "v2": {"anchorX": v2.RUNTIME_ANCHOR[0], "cell": list(v2.SIZE), "sentryOnTopStates": ["strike"], "summary": summarize(rows_v2), "rows": rows_v2},
        "v2HeroesAlwaysOnTop": {"note": "v2 frames and anchor without the strike draw-order rule", "summary": summarize(rows_v2_flat)},
        "script": str(Path(__file__).resolve().relative_to(ROOT)).replace("\\", "/"),
    }
    args.out.write_text(json.dumps(report, indent=1) + "\n", encoding="utf-8")
    for state in PAIRINGS:
        for action in PAIRINGS[state]:
            for region in ("eye", "claw"):
                k = f"{state}|{action}|{region}"
                a, b, c = report["v1"]["summary"][k], report["v2"]["summary"][k], report["v2HeroesAlwaysOnTop"]["summary"][k]
                print(f"{k:28s} v1 mean {a['mean']:.3f} max {a['max']:.3f} | v2 mean {b['mean']:.3f} max {b['max']:.3f} | v2 heroes-on-top mean {c['mean']:.3f} max {c['max']:.3f}")


if __name__ == "__main__":
    main()
