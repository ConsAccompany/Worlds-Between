"""Author distinct native-resolution animation poses for the male protagonist.

Each frame starts from the hand-authored idle construction for identity, then
redraws legs, boots, arms, and (for combat) face/torso details on the native
32x48 canvas. Nothing is resized or shifted wholesale. Run with Pillow.
"""

from __future__ import annotations

import hashlib
import importlib.util
import json
import uuid
from datetime import datetime
from pathlib import Path

from PIL import Image, ImageDraw


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "game" / "assets" / "characters" / "native-animation"
IDLE_SCRIPT = ROOT / "tools" / "rpg-2-star-ocean-the-second_protagonist-male_native-sprite-authoring_m8-v01_20261014-135140-71e3a4c9.py"
spec = importlib.util.spec_from_file_location("male_idle_authoring", IDLE_SCRIPT)
assert spec and spec.loader
idle = importlib.util.module_from_spec(spec)
spec.loader.exec_module(idle)
C = idle.C


def base(direction: str) -> Image.Image:
    im = Image.new("RGBA", (32, 48), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    if direction == "south":
        idle.draw_south(d)
    elif direction == "north":
        idle.draw_north(d)
    else:
        idle.draw_side(d, direction)
    d.rectangle((0, 0, 31, 2), fill=(0, 0, 0, 0))
    return im


def pants_and_coat(im: Image.Image, direction: str, phase: int) -> None:
    """Change each leg's stride while preserving the fixed foot baseline."""
    d = ImageDraw.Draw(im)
    p = lambda pts, key: d.polygon(pts, fill=C[key])
    r = lambda box, key: d.rectangle(box, fill=C[key])
    d.rectangle((4, 35, 28, 44), fill=(0, 0, 0, 0))

    if direction in ("south", "north"):
        # Independent asymmetric feet: contact, passing, opposite contact,
        # and opposite passing. Boot toes and pant-lighting change by phase.
        configs = {
            1: ((8, 14, 7, 16), (19, 22, 19, 24)),
            2: ((10, 14, 8, 16), (17, 21, 17, 24)),
            3: ((10, 13, 9, 16), (18, 24, 17, 27)),
            4: ((9, 14, 8, 15), (18, 22, 16, 24)),
        }
        left, right = configs[phase]
        for idx, (pant_l, pant_r, boot_l, boot_r) in enumerate((left, right)):
            ankle = 41 if (phase in (1, 3) and ((phase == 1) == (idx == 0))) else 40
            p([(pant_l, 35), (pant_r, 35), (pant_r + 1, ankle),
               (pant_l - 1, ankle)], "outline")
            r((pant_l + 1, 36, pant_r, ankle - 1), "trouser" if idx == 0 else "trouser_light")
            p([(boot_l, ankle), (boot_r - 1, ankle), (boot_r, 44),
               (boot_l, 44)], "boot")
            r((boot_l + 2, ankle, min(boot_l + 5, boot_r - 1), ankle), "boot_light")
        # The split explorer-coat hem must remain above the independently moving legs.
        p([(8, 35), (13, 35), (12, 37), (8, 37)], "coat_dark")
        p([(19, 35), (24, 35), (24, 37), (21, 37)], "coat_hem")
        r((15, 35, 18, 36), "coat")
    else:
        # In profile, front and rear feet separate in stride and cross in
        # passing phases. The east and west geometry is deliberately distinct.
        forward = 1 if direction == "east" else -1
        configs = {
            1: ((-3, -3), (3, 2)),
            2: ((-1, 0), (1, 0)),
            3: ((3, 2), (-3, -3)),
            4: ((1, 0), (-1, 0)),
        }
        rear, front = configs[phase]
        for idx, (center, (hip_shift, toe_shift)) in enumerate(zip((12, 20), (rear, front))):
            hip_x = center + hip_shift * forward
            toe_x = center + toe_shift * forward
            p([(hip_x - 2, 35), (hip_x + 2, 35), (toe_x + 2, 41),
               (toe_x - 2, 41)], "outline")
            p([(hip_x - 1, 36), (hip_x + 1, 36), (toe_x + 1, 40),
               (toe_x - 1, 40)], "trouser" if idx == 0 else "trouser_light")
            p([(toe_x - 3, 40), (toe_x + 3, 40),
               (toe_x + 4 * forward, 44), (toe_x - 3 * forward, 44)], "boot")
            r((min(toe_x - 1, toe_x + 1), 41, max(toe_x - 1, toe_x + 1), 41), "boot_light")
        p([(8, 35), (13, 35), (11, 37), (8, 37)], "coat_dark")
        p([(18, 35), (24, 34), (23, 37), (19, 37)], "coat_hem")


def swing_arms(im: Image.Image, direction: str, phase: int) -> None:
    """Redraw narrow sleeve/hand ends for reciprocal arm motion."""
    d = ImageDraw.Draw(im)
    p = lambda pts, key: d.polygon(pts, fill=C[key])
    r = lambda box, key: d.rectangle(box, fill=C[key])
    # The outermost pixels are independent arm tips; the coat torso stays put.
    if direction in ("south", "north"):
        d.rectangle((4, 28, 7, 34), fill=(0, 0, 0, 0))
        d.rectangle((26, 28, 28, 34), fill=(0, 0, 0, 0))
        left_y, right_y = {1: (27, 33), 2: (30, 31), 3: (33, 27), 4: (31, 30)}[phase]
        p([(7, 25), (9, 27), (8, left_y + 4), (5, left_y + 4),
           (4, left_y + 2), (5, left_y)], "outline")
        p([(7, 26), (8, 28), (7, left_y + 2), (5, left_y + 2),
           (5, left_y + 1)], "coat")
        r((5, left_y + 3, 7, left_y + 4), "skin_shadow")
        r((6, left_y + 3, 7, left_y + 3), "skin")
        p([(24, 25), (26, 26), (28, right_y), (28, right_y + 3),
           (26, right_y + 5), (24, right_y + 4)], "outline")
        p([(25, 26), (26, 27), (27, right_y), (27, right_y + 2),
           (25, right_y + 3)], "coat")
        r((26, right_y + 3, 27, right_y + 4), "skin_shadow")
        r((26, right_y + 3, 26, right_y + 3), "skin")
    else:
        lead_right = direction == "east"
        outer_x = 26 if lead_right else 5
        d.rectangle((outer_x, 29, outer_x + 2, 34), fill=(0, 0, 0, 0))
        y = {1: 27, 2: 30, 3: 33, 4: 30}[phase]
        if lead_right:
            p([(23, 25), (26, 26), (28, y + 1), (27, y + 4),
               (25, y + 5), (23, y + 2)], "outline")
            p([(24, 26), (26, 27), (27, y + 1), (26, y + 3), (24, y + 2)], "coat")
            r((26, y + 3, 27, y + 4), "skin")
        else:
            p([(9, 25), (6, 26), (4, y + 1), (5, y + 4),
               (7, y + 5), (9, y + 2)], "outline")
            p([(8, 26), (6, 27), (5, y + 1), (6, y + 3), (8, y + 2)], "coat")
            r((5, y + 3, 6, y + 4), "skin")


def walk(direction: str, phase: int) -> Image.Image:
    im = base(direction)
    pants_and_coat(im, direction, phase)
    swing_arms(im, direction, phase)
    return im


def attack(phase: int) -> Image.Image:
    im = base("south")
    d = ImageDraw.Draw(im)
    p = lambda pts, key: d.polygon(pts, fill=C[key])
    r = lambda box, key: d.rectangle(box, fill=C[key])
    # Both poses have stationary head and feet. Shoulder, elbow and fist move.
    d.rectangle((23, 23, 30, 35), fill=(0, 0, 0, 0))
    if phase == 1:  # Wind-up: elbow high, fist beside head.
        p([(22, 23), (25, 22), (27, 19), (29, 20), (29, 25),
           (26, 27), (25, 31), (22, 30)], "outline")
        p([(23, 24), (25, 23), (27, 21), (28, 22), (28, 24),
           (25, 26), (24, 29)], "coat")
        r((27, 18, 29, 20), "skin_shadow")
        r((27, 18, 28, 19), "skin")
        p([(8, 35), (13, 35), (12, 37), (8, 37)], "coat_dark")
    else:  # Release: arm stretches across the fixed canvas toward screen right.
        p([(22, 24), (26, 23), (30, 22), (31, 24), (31, 27),
           (27, 28), (24, 30), (22, 29)], "outline")
        p([(23, 25), (27, 24), (30, 23), (30, 26),
           (26, 27), (24, 28)], "coat")
        r((29, 23, 31, 25), "skin_shadow")
        r((30, 23, 31, 24), "skin")
        # Two cool accent pixels carry the scarf/coat accent into the action.
        r((25, 22, 27, 22), "teal_light")
        r((28, 21, 29, 21), "teal")
    return im


def hit() -> Image.Image:
    im = base("south")
    d = ImageDraw.Draw(im)
    p = lambda pts, key: d.polygon(pts, fill=C[key])
    r = lambda box, key: d.rectangle(box, fill=C[key])
    # Guarded flinch: fists rise, eyes shut, torso gets a brief warm highlight.
    d.rectangle((4, 26, 8, 34), fill=(0, 0, 0, 0))
    d.rectangle((25, 26, 28, 34), fill=(0, 0, 0, 0))
    p([(8, 23), (10, 24), (9, 27), (7, 29), (5, 28), (5, 25)], "outline")
    p([(8, 24), (9, 25), (8, 27), (6, 27), (6, 25)], "coat")
    r((5, 24, 7, 25), "skin_shadow")
    r((6, 24, 7, 24), "skin")
    p([(23, 23), (26, 24), (28, 25), (28, 28), (26, 29), (24, 27)], "outline")
    p([(24, 24), (26, 25), (27, 26), (27, 27), (25, 27)], "coat")
    r((26, 24, 28, 25), "skin_shadow")
    r((26, 24, 27, 24), "skin")
    r((13, 14, 14, 14), "hair_dark")
    r((19, 14, 20, 14), "hair_dark")
    r((12, 15, 13, 15), "cheek")
    r((19, 15, 20, 15), "cheek")
    r((12, 27, 13, 31), "coat_light")
    r((21, 27, 22, 31), "coat_light")
    return im


def verify(im: Image.Image, action: str, direction: str, phase: int) -> dict:
    assert im.mode == "RGBA" and im.size == (32, 48)
    assert all(im.getpixel(pos)[3] == 0 for pos in ((0, 0), (31, 0), (0, 47), (31, 47)))
    bbox = im.getbbox()
    assert bbox and bbox[3] == 45, (action, direction, phase, bbox)
    assert bbox[1] == 3, (action, direction, phase, bbox)
    assert im.getpixel((16, 44))[3] == 0 or any(im.getpixel((x, 44))[3] for x in range(6, 28))
    palette = {Image.Image.getpixel(im, (x, y)) for y in range(48) for x in range(32) if im.getpixel((x, y))[3]}
    original = base(direction)
    differences = sum(1 for y in range(48) for x in range(32) if im.getpixel((x, y)) != original.getpixel((x, y)))
    assert differences >= 25, (action, direction, phase, differences)
    assert len(palette) <= 32, (action, direction, phase, len(palette))
    return {"visible_bbox": list(bbox), "palette_colors": len(palette), "pixels_changed_from_idle": differences}


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    rows = []
    frames = [("walk", direction, phase, walk(direction, phase))
              for direction in ("south", "west", "north", "east") for phase in range(1, 5)]
    frames += [("attack", "south", phase, attack(phase)) for phase in (1, 2)]
    frames.append(("hit", "south", 1, hit()))
    assert len(frames) == 19
    for action, direction, phase, im in frames:
        metrics = verify(im, action, direction, phase)
        file_name = (
            "rpg-2-star-ocean-the-second_protagonist-male"
            f"_native-{action}-{direction}-phase-{phase:02d}_m8-v01_{stamp}-{uuid.uuid4().hex[:8]}.png"
        )
        target = OUT / file_name
        im.save(target)
        content = target.read_bytes()
        rows.append({
            "action": action,
            "direction": direction,
            "phase": phase,
            "path": target.relative_to(ROOT).as_posix(),
            "dimensions": [32, 48],
            "sha256": hashlib.sha256(content).hexdigest(),
            **metrics,
        })
    # Check that no two animation phases accidentally have identical pixels.
    hashes = [r["sha256"] for r in rows]
    assert len(set(hashes)) == len(hashes), "An animation frame duplicates another frame"
    manifest = OUT / (
        "rpg-2-star-ocean-the-second_protagonist-male"
        f"_native-animation-manifest_m8-v01_{stamp}-{uuid.uuid4().hex[:8]}.json"
    )
    manifest.write_text(json.dumps({
        "character": "protagonist-male",
        "status": "prototype",
        "canvas": [32, 48],
        "anchor": [16, 44],
        "frame_count": len(rows),
        "frames": rows,
    }, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(manifest)
    print(f"Verified {len(rows)} unique native RGBA animation frames")


if __name__ == "__main__":
    main()
