"""Author female protagonist animation prototypes at native 32x48 resolution.

The four approved-for-study directional idle drawings are the source layer.
This script redraws legs, sleeves, and the outer tip of the side ponytail at
the pixel level. It never translates the whole sprite or rescales pixels.
"""

from __future__ import annotations

import importlib.util
import json
from datetime import datetime
from pathlib import Path
from uuid import uuid4

from PIL import Image, ImageDraw


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "tools" / "rpg-2-star-ocean-the-second_protagonist-female_native-idle-pixels_m8-prototype_20261014-135437-b4a2e1c7.py"
OUT = ROOT / "game" / "assets" / "characters" / "native-animation"
OUT.mkdir(parents=True, exist_ok=True)
STAMP = datetime.now().strftime("%Y%m%d-%H%M%S")
PREFIX = "rpg-2-star-ocean-the-second_protagonist-female"

spec = importlib.util.spec_from_file_location("female_idle_art", SOURCE)
assert spec and spec.loader
idle = importlib.util.module_from_spec(spec)
spec.loader.exec_module(idle)
P = idle.P
FACINGS = {"south": idle.south, "west": idle.west,
           "north": idle.north, "east": idle.east}
HAIR = {P[k] for k in ("hair_dark", "hair", "hair_light", "hair_glint")}
LEG = {P[k] for k in ("pants_dark", "pants", "pants_light",
                       "boot_dark", "boot", "boot_light")}


def erase_palette(im: Image.Image, box: tuple[int, int, int, int], colors: set[str]):
    rgb = {tuple(bytes.fromhex(c.lstrip("#"))) for c in colors}
    for y in range(box[1], box[3]):
        for x in range(box[0], box[2]):
            if im.getpixel((x, y))[:3] in rgb:
                im.putpixel((x, y), (0, 0, 0, 0))


def legs(im: Image.Image, phase: int, facing: str):
    # Remove only pants and boots; the asymmetric coat hem stays in place.
    erase_palette(im, (7, 33, 26, 45), LEG)
    d = ImageDraw.Draw(im)
    # Heel and toe positions change, while every phase has the same y=44 floor.
    if phase == 1:
        left, right, lk, rk = 6, 18, 10, 21
    elif phase == 2:
        left, right, lk, rk = 9, 17, 12, 20
    elif phase == 3:
        left, right, lk, rk = 9, 21, 12, 22
    else:
        left, right, lk, rk = 8, 18, 11, 21
    if facing in ("west", "east"):
        # Profile stride separates the near and far legs along travel.
        shift = (-1 if facing == "west" else 1)
        if phase in (1, 3):
            left += shift
            right += shift
    for x, knee, light in ((left, lk, True), (right, rk, False)):
        d.polygon([(x + 2, 33), (x + 7, 33), (knee + 5, 39),
                   (x + 6, 41), (x + 1, 40)],
                  fill=P["pants"], outline=P["edge"])
        d.rectangle((x + 3, 35, x + 4, 38), fill=P["pants_light" if light else "pants_dark"])
        d.polygon([(x, 40), (x + 7, 40), (x + 8, 43),
                   (x + 7, 44), (x, 44)], fill=P["boot"], outline=P["edge"])
        d.line((x + 1, 41, x + 5, 41), fill=P["boot_light"])
        d.line((x, 44, x + 7, 44), fill=P["boot_dark"])


def arms(im: Image.Image, phase: int, facing: str):
    # Repaint the exposed wrist/sleeve tips rather than slide the whole figure.
    d = ImageDraw.Draw(im)
    stride = (1, 0, -1, 0)[phase - 1]
    if facing in ("south", "north"):
        for x, sign in ((7, stride), (24, -stride)):
            d.rectangle((x - 1, 31, x + 1, 36), fill=(0, 0, 0, 0))
            y = 31 + sign
            d.rectangle((x - 1, y, x + 1, y + 2), fill=P["skin"])
            d.line((x - 1, y + 3, x + 1, y + 3), fill=P["coat_dark"])
    else:
        x = 8 if facing == "west" else 25
        d.rectangle((x - 1, 30, x + 1, 36), fill=(0, 0, 0, 0))
        y = 31 + stride
        d.rectangle((x - 1, y, x + 1, y + 2), fill=P["skin"])
        d.line((x - 1, y + 3, x + 1, y + 3), fill=P["coat_dark"])


def ponytail(im: Image.Image, phase: int, facing: str):
    # Only the free end is redrawn. Knot and head remain stable identity cues.
    d = ImageDraw.Draw(im)
    tail = (0, 2, 4, 1)[phase - 1]
    if facing in ("south", "north", "east"):
        erase_palette(im, (0, 20, 7, 29), HAIR)
        x = 1 if facing != "east" else 3
        d.polygon([(x + 4, 19), (x + 5, 22), (x + 3, 25 + tail),
                   (x, 27 + tail), (x + 1, 23), (x + 2, 20)],
                  fill=P["hair_dark"])
        d.line((x + 2, 21, x + 1, 25 + tail), fill=P["hair_light"])
    else:
        erase_palette(im, (25, 18, 31, 28), HAIR)
        d.polygon([(24, 17), (28, 19), (29, 23 + tail),
                   (27, 25 + tail), (25, 21)], fill=P["hair_dark"])
        d.line((27, 20, 28, 23 + tail), fill=P["hair_light"])


def walk(facing: str, phase: int) -> Image.Image:
    im = FACINGS[facing]().copy()
    legs(im, phase, facing)
    arms(im, phase, facing)
    ponytail(im, phase, facing)
    return im


def attack(phase: int) -> Image.Image:
    im = idle.south().copy()
    d = ImageDraw.Draw(im)
    legs(im, 1 if phase == 1 else 3, "south")
    # Right arm coils inward, then drives outward. Teal scarf tail responds.
    d.rectangle((23, 22, 28, 36), fill=(0, 0, 0, 0))
    if phase == 1:
        d.polygon([(23, 21), (27, 23), (24, 28), (19, 29), (18, 26)],
                  fill=P["coat"], outline=P["edge"])
        d.rectangle((18, 25, 20, 27), fill=P["skin"])
        d.line((21, 27, 24, 30), fill=P["teal_light"], width=2)
    else:
        d.polygon([(23, 21), (27, 22), (29, 26), (28, 29), (23, 28)],
                  fill=P["coat"], outline=P["edge"])
        d.rectangle((28, 26, 31, 28), fill=P["skin"])
        d.line((21, 28, 25, 31), fill=P["teal_light"], width=2)
    return im


def hit() -> Image.Image:
    im = idle.south().copy()
    d = ImageDraw.Draw(im)
    legs(im, 3, "south")
    # Open arms and a compressed scarf make recoil legible without flash tint.
    d.rectangle((5, 27, 10, 36), fill=(0, 0, 0, 0))
    d.rectangle((22, 27, 27, 36), fill=(0, 0, 0, 0))
    d.polygon([(9, 22), (5, 24), (2, 29), (4, 31), (10, 27)],
              fill=P["coat"], outline=P["edge"])
    d.rectangle((2, 29, 4, 31), fill=P["skin"])
    d.polygon([(23, 22), (27, 24), (30, 29), (28, 31), (22, 27)],
              fill=P["coat"], outline=P["edge"])
    d.rectangle((28, 29, 30, 31), fill=P["skin"])
    d.rectangle((13, 15, 14, 15), fill=P["edge"])
    d.rectangle((18, 15, 19, 15), fill=P["edge"])
    d.line((13, 23, 20, 23), fill=P["teal_light"], width=1)
    return im


def save(im: Image.Image, action: str, direction: str, phase: int) -> dict:
    assert im.mode == "RGBA" and im.size == (32, 48)
    assert im.getpixel((0, 0))[3] == 0 and im.getpixel((31, 47))[3] == 0
    assert any(im.getpixel((x, 44))[3] for x in range(32)), "floor anchor missing"
    name = f"{PREFIX}_native-{action}-{direction}-phase-{phase:02d}_m8-prototype_{STAMP}-{uuid4().hex[:8]}.png"
    path = OUT / name
    im.save(path, optimize=True)
    return {"action": action, "direction": direction, "phase": phase,
            "path": path.relative_to(ROOT).as_posix()}


def main():
    frames = [save(walk(direction, phase), "walk", direction, phase)
              for direction in FACINGS for phase in range(1, 5)]
    frames += [save(attack(phase), "attack", "south", phase)
               for phase in range(1, 3)]
    frames.append(save(hit(), "hit", "south", 1))
    manifest = {
        "character": "protagonist-female", "status": "prototype",
        "canvas": [32, 48], "frameCount": len(frames),
        "sourceIdleScript": SOURCE.relative_to(ROOT).as_posix(),
        "floorBaselineY": 44,
        "notes": "Four-direction exploration walks are prototypes. South attack and hit are exploratory motion studies only, not finished horizontal combat art. Game-size review and acceptance remain pending.",
        "frames": frames,
    }
    path = OUT / f"{PREFIX}_native-animation-manifest_m8-prototype_{STAMP}-{uuid4().hex[:8]}.json"
    path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(path)
    print(f"frames={len(frames)}")


if __name__ == "__main__":
    main()
