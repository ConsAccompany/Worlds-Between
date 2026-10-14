"""Draw Milo's original 32x48 exploration frames at final pixel resolution.

The approved source sheet is a design reference, never downsampled or traced.
Re-running this script replaces only its own twenty Milo PNGs and manifest.
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

from PIL import Image, ImageDraw


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
OUT = HERE.parent / "native-animation"
PREVIEW_OUT = ROOT / "outputs"
STAMP = "m8-v01_20261014-185020"
PREFIX = "rpg-2-star-ocean-the-second_milo_native-exploration"
SOURCE = "outputs/rpg-2-star-ocean-the-second_milo_character-sheet_hairstyle-v02_20261013-161317-f1651dc0.png"
CITY = "game/assets/environments/rpg-2-star-ocean-the-second_scifi-city_environment-background_m8-v02_20261013-232003-48d0ab67.png"
C = {
    "ink": "#202733", "hair": "#49403e", "hair_light": "#71645c",
    "silver": "#c8c9c4", "silver_shadow": "#969b9e", "skin": "#d59b7c",
    "skin_light": "#e8b99a", "skin_shadow": "#aa7563", "eye": "#394e5a",
    "navy": "#263346", "navy_light": "#425571", "navy_dark": "#192737",
    "coat": "#d9dada", "coat_light": "#f1eeeb", "coat_shadow": "#a5adb4",
    "coat_deep": "#77838d", "green": "#5f9d34", "green_light": "#a4d86b",
    "green_dark": "#356d31", "bag": "#aeb6b9", "bag_top": "#e2e3de",
    "bag_side": "#657680", "metal": "#a99a75", "boot": "#303b4a",
    "boot_light": "#6a7480",
}


def rect(d: ImageDraw.ImageDraw, xy: tuple[int, int, int, int], color: str,
         outline: str | None = None) -> None:
    d.rectangle(xy, fill=C[color], outline=C[outline] if outline else None)


def poly(d: ImageDraw.ImageDraw, xy: list[tuple[int, int]], color: str,
         outline: str | None = "ink") -> None:
    d.polygon(xy, fill=C[color], outline=C[outline] if outline else None)


def line(d: ImageDraw.ImageDraw, xy: list[tuple[int, int]], color: str,
         width: int = 1) -> None:
    d.line(xy, fill=C[color], width=width)


def legs(d: ImageDraw.ImageDraw, direction: str, phase: int) -> None:
    # Contact pair -> passing pose -> opposite contact -> passing pose.
    shifts = {0: (0, 0), 1: (-3, 2), 2: (-1, 1), 3: (2, -3), 4: (1, -1)}
    left, right = shifts[phase]
    if direction == "west":
        left, right = -right, -left
    elif direction == "east":
        left, right = right, left
    poly(d, [(11, 31), (16, 31), (14 + left, 42), (10 + left, 42)], "navy_dark")
    poly(d, [(17, 31), (22, 31), (22 + right, 42), (17 + right, 42)], "navy")
    rect(d, (9 + left, 41, 14 + left, 44), "boot", "ink")
    rect(d, (17 + right, 41, 22 + right, 44), "boot", "ink")
    rect(d, (10 + left, 41, 12 + left, 41), "boot_light")
    rect(d, (18 + right, 41, 20 + right, 41), "boot_light")
    rect(d, (11 + left, 44, 13 + left, 44), "ink")
    rect(d, (19 + right, 44, 21 + right, 44), "ink")


def medical_bag(d: ImageDraw.ImageDraw, direction: str, phase: int) -> None:
    # The rectangular case hangs from his physical right shoulder. It changes
    # apparent side by facing; no left/right image mirroring is used.
    sway = {0: 0, 1: 1, 2: 0, 3: -1, 4: 0}[phase]
    if direction == "south":
        x, y = 3 + sway, 26
        line(d, [(12, 19), (x + 7, 27)], "navy_dark", 2)
    elif direction == "north":
        x, y = 22 + sway, 26
        line(d, [(19, 19), (x + 1, 27)], "navy_dark", 2)
    elif direction == "west":
        x, y = 3 + sway, 27
        line(d, [(17, 18), (x + 5, 28)], "navy_dark", 2)
    else:
        x, y = 22 + sway, 27
        line(d, [(15, 18), (x + 1, 28)], "navy_dark", 2)
    rect(d, (x, y, x + 7, y + 8), "bag_side", "ink")
    rect(d, (x + 1, y + 1, x + 6, y + 6), "bag", "ink")
    rect(d, (x + 2, y + 1, x + 5, y + 2), "bag_top")
    rect(d, (x + 3, y + 3, x + 4, y + 5), "green")
    rect(d, (x + 2, y + 4, x + 5, y + 4), "green")
    rect(d, (x + 2, y + 7, x + 5, y + 7), "navy_dark")


def coat_and_arms(d: ImageDraw.ImageDraw, direction: str, phase: int) -> None:
    swing = {0: (0, 0), 1: (2, -2), 2: (1, -1), 3: (-2, 2), 4: (-1, 1)}[phase]
    left, right = swing
    if direction == "north":
        poly(d, [(10, 19), (22, 19), (24, 36), (20, 39),
                 (16, 36), (12, 39), (8, 36)], "coat_shadow")
        poly(d, [(11, 20), (21, 20), (22, 35), (17, 37),
                 (13, 35)], "coat")
        line(d, [(16, 21), (16, 37)], "coat_deep")
        rect(d, (15, 20, 18, 25), "navy")
        rect(d, (16, 22, 17, 24), "green")
    elif direction == "south":
        poly(d, [(10, 19), (22, 19), (25, 37), (21, 39),
                 (17, 35), (12, 39), (7, 37)], "coat_shadow")
        poly(d, [(11, 20), (21, 20), (23, 35), (19, 37),
                 (17, 34), (12, 37), (9, 35)], "coat")
        poly(d, [(13, 21), (19, 21), (20, 33), (14, 33)], "navy")
        line(d, [(12, 20), (14, 34)], "coat_light", 2)
        line(d, [(21, 20), (20, 34)], "coat_light", 2)
        rect(d, (20, 27, 21, 29), "green")
        rect(d, (19, 28, 22, 28), "green")
        rect(d, (15, 25, 17, 26), "metal")
    else:
        poly(d, [(10, 19), (22, 19), (24, 36), (20, 39),
                 (16, 35), (12, 39), (8, 36)], "coat_shadow")
        poly(d, [(12, 20), (21, 20), (22, 34), (17, 37),
                 (11, 35)], "coat")
        front_x = 11 if direction == "west" else 21
        line(d, [(front_x, 21), (front_x + (-1 if direction == "west" else 1), 35)], "coat_light", 2)
        rect(d, (14, 22, 18, 31), "navy")
        rect(d, (16, 27, 17, 29), "green")
    # Open, high-collared jacket; the green wristband belongs to his left arm.
    poly(d, [(10, 20), (7, 23), (6 + left, 31),
             (9 + left, 33), (12, 27)], "coat_shadow")
    poly(d, [(22, 20), (25, 23), (26 + right, 31),
             (23 + right, 33), (20, 27)], "coat_light")
    rect(d, (6 + left, 31, 8 + left, 34), "skin", "ink")
    rect(d, (24 + right, 31, 26 + right, 34), "skin", "ink")
    if direction == "south":
        rect(d, (23 + right, 30, 26 + right, 32), "green_dark", "ink")
        rect(d, (24 + right, 30, 25 + right, 31), "green_light")
    elif direction == "north":
        rect(d, (6 + left, 30, 9 + left, 32), "green_dark", "ink")
        rect(d, (7 + left, 30, 8 + left, 31), "green_light")
    elif direction == "west":
        rect(d, (23 + right, 30, 26 + right, 32), "green_dark", "ink")
        rect(d, (24 + right, 30, 25 + right, 31), "green_light")
    else:
        rect(d, (6 + left, 30, 9 + left, 32), "green_dark", "ink")
        rect(d, (7 + left, 30, 8 + left, 31), "green_light")


def head_south(d: ImageDraw.ImageDraw) -> None:
    rect(d, (11, 9, 22, 20), "skin", "ink")
    rect(d, (14, 18, 19, 21), "skin_shadow")
    poly(d, [(10, 11), (10, 7), (12, 5), (15, 5), (17, 3),
             (19, 5), (22, 4), (24, 8), (23, 12), (20, 9),
             (15, 9), (12, 13)], "hair")
    line(d, [(12, 7), (15, 5), (20, 6), (22, 8)], "hair_light")
    poly(d, [(9, 9), (12, 8), (13, 12), (11, 16), (9, 15)], "silver")
    rect(d, (9, 13, 11, 15), "silver_shadow")
    rect(d, (14, 14, 15, 14), "eye")
    rect(d, (20, 14, 21, 14), "eye")
    line(d, [(16, 18), (19, 18)], "skin_shadow")
    rect(d, (10, 19, 13, 22), "coat_light", "ink")
    rect(d, (20, 19, 23, 22), "coat_light", "ink")


def head_north(d: ImageDraw.ImageDraw) -> None:
    poly(d, [(11, 7), (13, 5), (16, 5), (18, 3), (21, 5),
             (23, 8), (23, 17), (20, 20), (12, 20), (9, 17)], "hair")
    line(d, [(12, 7), (15, 6), (19, 6), (22, 8)], "hair_light")
    poly(d, [(22, 9), (25, 10), (24, 15), (22, 16)], "silver")
    rect(d, (10, 16, 12, 18), "skin_shadow")
    rect(d, (21, 16, 23, 18), "skin_shadow")
    rect(d, (10, 19, 13, 22), "coat_light", "ink")
    rect(d, (20, 19, 23, 22), "coat_light", "ink")


def head_west(d: ImageDraw.ImageDraw) -> None:
    poly(d, [(12, 11), (13, 7), (15, 5), (18, 4), (21, 5),
             (23, 9), (22, 17), (17, 20), (11, 17)], "hair")
    poly(d, [(10, 11), (15, 8), (18, 10), (17, 16),
             (12, 18), (9, 15)], "skin", "ink")
    poly(d, [(12, 7), (15, 6), (17, 10), (15, 16), (12, 16)], "silver")
    line(d, [(18, 5), (21, 6), (22, 9)], "hair_light")
    rect(d, (10, 14, 11, 14), "eye")
    rect(d, (11, 18, 13, 18), "skin_shadow")
    rect(d, (18, 19, 23, 22), "coat_light", "ink")


def head_east(d: ImageDraw.ImageDraw) -> None:
    poly(d, [(10, 9), (12, 6), (16, 4), (19, 5), (22, 4),
             (24, 9), (24, 17), (20, 20), (11, 17)], "hair")
    poly(d, [(16, 10), (22, 9), (25, 13), (24, 17),
             (20, 19), (16, 16)], "skin", "ink")
    # His right silver temple is mostly hidden on this opposite profile.
    rect(d, (10, 11, 11, 14), "silver_shadow")
    line(d, [(13, 7), (17, 5), (22, 7)], "hair_light")
    rect(d, (22, 14, 23, 14), "eye")
    rect(d, (20, 18, 22, 18), "skin_shadow")
    rect(d, (10, 19, 15, 22), "coat_light", "ink")


HEADS = {"south": head_south, "west": head_west,
         "north": head_north, "east": head_east}


def render(direction: str, phase: int) -> Image.Image:
    im = Image.new("RGBA", (32, 48), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    legs(d, direction, phase)
    coat_and_arms(d, direction, phase)
    medical_bag(d, direction, phase)
    HEADS[direction](d)
    return im


def validate(images: dict[tuple[str, int], Image.Image]) -> None:
    assert len(images) == 20
    for direction in HEADS:
        hashes = set()
        for phase in range(5):
            im = images[(direction, phase)]
            assert im.mode == "RGBA" and im.size == (32, 48)
            bounds = im.getbbox()
            assert bounds is not None and 2 <= bounds[0] and bounds[2] <= 31
            assert bounds[1] >= 2 and bounds[3] == 45, (direction, phase, bounds)
            for point in ((0, 0), (31, 0), (0, 47), (31, 47)):
                assert im.getpixel(point)[3] == 0
            assert any(im.getpixel((x, 44))[3] for x in range(7, 26))
            hashes.add(hashlib.sha256(im.tobytes()).hexdigest())
        assert len(hashes) == 5, direction
    assert images[("west", 0)].tobytes() != images[("east", 0)].tobytes()


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    PREVIEW_OUT.mkdir(parents=True, exist_ok=True)
    images = {(direction, phase): render(direction, phase)
              for direction in HEADS for phase in range(5)}
    validate(images)
    frames = []
    for direction in HEADS:
        for phase in range(5):
            action = "idle" if phase == 0 else "walk"
            variant = direction if phase == 0 else f"{direction}-phase-{phase:02d}"
            key = f"milo:{action}:{variant}:{STAMP}"
            uid = hashlib.sha256(key.encode()).hexdigest()[:8]
            name = f"{PREFIX}-{action}-{variant}_{STAMP}-{uid}.png"
            path = OUT / name
            images[(direction, phase)].save(path)
            with Image.open(path) as check:
                assert check.mode == "RGBA" and check.size == (32, 48)
            frames.append({
                "action": action, "direction": direction, "phase": phase,
                "path": "game/assets/characters/native-animation/" + name,
                "size": [32, 48], "anchor": [16, 44],
                "sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
                "stage": "native_exploration_prototype_not_accepted",
            })
    # Review frames are separate 640x360 images, with Milo at actual 1x game
    # size on the science-city candidate. They are visual evidence, not art QA.
    previews = []
    with Image.open(ROOT / CITY) as source_city:
        city = source_city.convert("RGBA").resize((640, 360), Image.Resampling.LANCZOS)
    for direction, phase in [(direction, 0) for direction in HEADS] + [("south", 2)]:
        review = city.copy()
        shade = Image.new("RGBA", (640, 360), (0, 0, 0, 0))
        shade_draw = ImageDraw.Draw(shade)
        shade_draw.ellipse((311, 238, 329, 242), fill=(19, 27, 34, 95))
        review = Image.alpha_composite(review, shade)
        review.alpha_composite(images[(direction, phase)], (304, 196))
        label = f"{direction}-idle" if phase == 0 else f"{direction}-walk-phase-{phase:02d}"
        uid = hashlib.sha256(("milo:game-scale:" + label + ":" + STAMP).encode()).hexdigest()[:8]
        name = f"rpg-2-star-ocean-the-second_milo_game-scale-{label}_{STAMP}-{uid}.png"
        review.save(PREVIEW_OUT / name)
        previews.append({"direction": direction, "phase": phase,
                         "path": "outputs/" + name, "canvas": [640, 360],
                         "sprite_anchor_on_canvas": [320, 240]})
    uid = hashlib.sha256(("milo:manifest:" + STAMP).encode()).hexdigest()[:8]
    manifest = OUT / f"{PREFIX}-manifest_{STAMP}-{uid}.json"
    manifest.write_text(json.dumps({
        "visual_id": "milo", "character": "米洛 / Milo", "region": "科技",
        "source_portrait": SOURCE, "source_portrait_approval": "approved",
        "generator": "game/assets/characters/directional-prototypes/" + Path(__file__).name,
        "runtime_sprite_approval": "pending", "frame_count": 20,
        "canvas": [32, 48], "anchor": [16, 44], "frames": frames,
        "review_scene_background": CITY, "game_scale_previews": previews,
    }, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(manifest)


if __name__ == "__main__":
    main()
