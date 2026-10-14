"""Author individual native-pixel side-view combat poses for Liang Xu.

Each frame is drawn at its final 80x80 pixel canvas; no concept art is resized.
The transparent anchor (30, 73) is the ground contact origin in every frame.
Run with the project's bundled Python/Pillow runtime. Re-running creates new
uniquely named files and a corresponding manifest without overwriting assets.
"""

from __future__ import annotations

import hashlib
import json
import uuid
from datetime import datetime
from pathlib import Path

from PIL import Image, ImageDraw


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "game" / "assets" / "characters" / "combat-prototypes"
SLUG = "rpg-2-star-ocean-the-second"
CHAR = "liang-xu"
SIZE = (80, 80)
ANCHOR = (30, 73)

C = {
    "line": "#1b1b23", "line_warm": "#36313a",
    "hair_deep": "#211e24", "hair": "#39333b", "hair_mid": "#58525b", "hair_hi": "#807982",
    "silver": "#c7c6ca", "silver_hi": "#f0ecdf",
    "skin_deep": "#8e5b50", "skin": "#bd8972", "skin_hi": "#e0b09a", "cheek": "#a46c5c",
    "coat_deep": "#262730", "coat": "#383943", "coat_mid": "#50505a", "coat_hi": "#6c6871",
    "shirt": "#202e43", "shirt_hi": "#385572", "pants": "#292c36", "pants_hi": "#44444e",
    "boot": "#22232c", "boot_hi": "#52505a", "glove": "#252831",
    "teal_deep": "#193653", "teal": "#356783", "teal_mid": "#6fa7c1", "teal_hi": "#c0e1e3",
    "pack": "#272a34", "pack_hi": "#494651", "leather": "#825847", "metal": "#bd865c",
    "blade_dark": "#283c52", "blade": "#6591b0", "blade_hi": "#d4e7e7",
}


def poly(d: ImageDraw.ImageDraw, pts: list[tuple[int, int]], key: str) -> None:
    d.polygon(pts, fill=C[key])


def box(d: ImageDraw.ImageDraw, rect: tuple[int, int, int, int], key: str) -> None:
    d.rectangle(rect, fill=C[key])


def leg(d: ImageDraw.ImageDraw, hip: tuple[int, int], knee: tuple[int, int],
        ankle: tuple[int, int], toe: int, back: bool = False) -> None:
    hx, hy = hip
    kx, ky = knee
    ax, ay = ankle
    poly(d, [(hx-4, hy), (hx+5, hy), (kx+5, ky), (ax+4, ay),
             (ax-4, ay), (kx-5, ky)], "line")
    poly(d, [(hx-2, hy+1), (hx+3, hy+1), (kx+3, ky), (ax+2, ay-1),
             (ax-2, ay-1), (kx-3, ky)], "pants" if back else "pants_hi")
    poly(d, [(ax-5, ay-1), (ax+4, ay-1), (toe+3, 73),
             (ax-6, 73)], "line")
    poly(d, [(ax-3, ay), (ax+3, ay), (toe+1, 71), (ax-4, 71)], "boot")
    box(d, (ax-2, ay+1, ax+2, ay+1), "boot_hi")


def hair_and_face(d: ImageDraw.ImageDraw, x: int, y: int, hit: bool = False) -> None:
    # Compact high bun, then a broad bright silver sweep over the left temple.
    # The loose lock falls below the collar even at battle-view resolution.
    poly(d, [(x-14,y+8),(x-12,y+1),(x-6,y-3),(x+4,y-3),(x+11,y+2),
             (x+14,y+9),(x+14,y+17),(x+8,y+24),(x-1,y+25),
             (x-11,y+20),(x-14,y+14)], "line")
    poly(d, [(x-9,y+8),(x-7,y+2),(x+4,y),(x+11,y+5),(x+13,y+12),
             (x+12,y+17),(x+8,y+21),(x,y+23),(x-8,y+18)], "skin")
    poly(d, [(x+4,y+17),(x+11,y+16),(x+10,y+20),(x+3,y+22)], "skin_hi")
    box(d, (x+10,y+13,x+12,y+13), "line")
    box(d, (x+11,y+17,x+12,y+17), "cheek")
    box(d, (x+7,y+21,x+10,y+21), "line_warm")
    if hit:
        box(d, (x+9,y+13,x+12,y+13), "hair_deep")
    poly(d, [(x-13,y+12),(x-14,y+3),(x-10,y-1),(x-5,y-3),
             (x+4,y-4),(x+10,y-1),(x+13,y+4),(x+14,y+8),
             (x+8,y+7),(x+3,y+5),(x-4,y+8),(x-9,y+12)], "hair_deep")
    poly(d, [(x-11,y+6),(x-7,y-1),(x+1,y-2),(x+8,y+1),
             (x+10,y+4),(x+4,y+3),(x-4,y+6),(x-8,y+10)], "hair")
    # High bun at rear crown, a distinct round profile rather than a ponytail.
    poly(d, [(x-11,y+1),(x-15,y-2),(x-16,y-6),(x-13,y-9),
             (x-9,y-10),(x-5,y-7),(x-5,y-3),(x-8,y+1)], "line")
    poly(d, [(x-13,y-2),(x-14,y-6),(x-11,y-8),(x-8,y-6),
             (x-7,y-3),(x-9,y-1)], "hair_mid")
    box(d, (x-12,y-7,x-10,y-6), "hair_hi")
    poly(d, [(x-7,y),(x-3,y-3),(x+2,y-3),(x+3,y),
             (x-2,y+3),(x-4,y+8),(x-6,y+12),(x-8,y+8)], "silver")
    poly(d, [(x-5,y-1),(x-1,y-3),(x+1,y-2),(x-3,y+2),
             (x-5,y+8),(x-7,y+8)], "silver_hi")
    poly(d, [(x-9,y+10),(x-6,y+10),(x-4,y+18),
             (x-7,y+27),(x-11,y+30),(x-12,y+26),
             (x-9,y+18)], "silver")
    box(d, (x-10,y+15,x-8,y+19), "silver_hi")


def torso(d: ImageDraw.ImageDraw, dx: int, dy: int, lean: int = 0,
          scarf_tail: int = 0, skill: bool = False) -> tuple[int, int]:
    tx, ty = 28 + dx, 29 + dy
    # Floor-length coat panels and blue inset are her dominant combat read.
    poly(d, [(tx-8,ty),(tx+8+lean,ty-1),(tx+13+lean,ty+7),
             (tx+11+lean,ty+27),(tx+17+scarf_tail,ty+35),
             (tx+12+scarf_tail,ty+39),(tx+1,ty+34),
             (tx-8-scarf_tail,ty+39),(tx-14-scarf_tail,ty+35),
             (tx-11,ty+8)], "line")
    poly(d, [(tx-6,ty+2),(tx+7+lean,ty+1),(tx+11+lean,ty+8),
             (tx+9,ty+26),(tx+14+scarf_tail,ty+35),
             (tx+11+scarf_tail,ty+36),(tx+1,ty+31),
             (tx-9-scarf_tail,ty+36),(tx-12-scarf_tail,ty+34),
             (tx-9,ty+8)], "coat")
    poly(d, [(tx-7,ty+14),(tx-2,ty+14),(tx-3,ty+33),
             (tx-10-scarf_tail,ty+35)], "coat_deep")
    poly(d, [(tx+1,ty+24),(tx+8,ty+22),(tx+11+scarf_tail,ty+34),
             (tx+3,ty+31)], "shirt")
    box(d, (tx+3,ty+27,tx+5,ty+33), "shirt_hi")
    poly(d, [(tx+6,ty+2),(tx+11,ty+5),(tx+9,ty+21),
             (tx+2,ty+18)], "coat_mid")
    box(d, (tx-3,ty+12,tx-2,ty+27), "coat_hi")
    box(d, (tx-5,ty+25,tx+7,ty+27), "line")
    box(d, (tx-4,ty+25,tx+6,ty+26), "leather")
    box(d, (tx+1,ty+24,tx+3,ty+27), "metal")
    # Tall split collar and bright copper ring fastener.
    poly(d, [(tx-8,ty+1),(tx-7,ty-10),(tx-2,ty-12),
             (tx+1,ty-4),(tx+6,ty-12),(tx+11,ty-9),
             (tx+9,ty+4),(tx+3,ty+8),(tx-3,ty+7)], "line")
    poly(d, [(tx-6,ty-8),(tx-3,ty-10),(tx,ty-3),
             (tx+3,ty+5),(tx-5,ty+3)], "coat_mid")
    poly(d, [(tx+6,ty-9),(tx+9,ty-7),(tx+8,ty+2),
             (tx+3,ty+5)], "coat_hi")
    d.ellipse((tx-1,ty+2,tx+5,ty+8), fill=C["metal"])
    d.ellipse((tx+1,ty+4,tx+3,ty+6), fill=C["coat_deep"])
    box(d, (tx+1,ty+8,tx+2,ty+14), "metal")
    return tx, ty


def terminal(d: ImageDraw.ImageDraw, hand: tuple[int, int], pose: str) -> None:
    x, y = hand
    if pose == "none":
        return
    if pose == "forward":
        poly(d, [(x+1,y-9),(x+10,y-10),(x+12,y-3),
                 (x+3,y-1)], "line")
        poly(d, [(x+3,y-8),(x+9,y-8),(x+10,y-4),
                 (x+4,y-3)], "teal_deep")
        box(d, (x+5,y-7,x+8,y-7), "teal_hi")
        d.line([(x+12,y-5),(x+21,y-5)], fill=C["teal_mid"], width=2)
        poly(d, [(x+20,y-8),(x+25,y-5),(x+20,y-2),
                 (x+22,y-5)], "teal_hi")
    elif pose == "up":
        poly(d, [(x-4,y-16),(x+3,y-17),(x+5,y-2),
                 (x-2,y-1)], "line")
        poly(d, [(x-2,y-14),(x+2,y-15),(x+3,y-4),
                 (x-1,y-3)], "teal_deep")
        box(d, (x,y-12,x+1,y-7), "teal_mid")
        box(d, (x-5,y-17,x+4,y-16), "metal")
    elif pose == "back":
        poly(d, [(x-12,y-15),(x-4,y-18),(x+2,y-4),
                 (x-6,y-1)], "line")
        poly(d, [(x-10,y-14),(x-4,y-16),(x,y-5),
                 (x-5,y-3)], "teal_deep")
        box(d, (x-7,y-13,x-3,y-12), "teal_mid")
        box(d, (x-12,y-16,x-5,y-15), "metal")
    elif pose == "down":
        poly(d, [(x-2,y+1),(x+8,y+2),(x+10,y+13),
                 (x,y+12)], "line")
        poly(d, [(x,y+3),(x+6,y+4),(x+8,y+11),
                 (x+2,y+10)], "teal_deep")
        box(d, (x+2,y+5,x+6,y+5), "teal_mid")
        box(d, (x+3,y+8,x+6,y+8), "teal_hi")


def arm(d: ImageDraw.ImageDraw, shoulder: tuple[int, int], elbow: tuple[int, int],
        hand: tuple[int, int], back: bool = False) -> None:
    sx, sy = shoulder
    ex, ey = elbow
    hx, hy = hand
    width = 8 if back else 9
    d.line([(sx,sy),(ex,ey),(hx,hy)], fill=C["line"], width=width+3, joint="curve")
    d.line([(sx,sy),(ex,ey),(hx,hy-1)], fill=C["coat_deep" if back else "coat_mid"],
           width=width, joint="curve")
    box(d, (hx-3,hy-3,hx+3,hy+3), "line")
    box(d, (hx-2,hy-2,hx+2,hy+2), "glove")
    box(d, (hx,hy-2,hx+2,hy-1), "skin_deep")


def ordinary(action: str, phase: int) -> Image.Image:
    im = Image.new("RGBA", SIZE, (0,0,0,0))
    d = ImageDraw.Draw(im)
    if action == "idle":
        dx, dy, lean, tail = (0, -1 if phase == 2 else 0, 0, phase-1)
        legs = [((25,56),(25,65),(21,69),26), ((36,56),(39,65),(41,69),47)]
        back_arm = ((21,35),(16,45),(20,54))
        fore_arm = ((40,34),(43,43),(45,49))
        weapon = "down"
    elif action == "move":
        stride = [-7,-3,7,3][phase-1]
        dx, dy, lean, tail = (0, 1 if phase in (1,3) else 0, 1, 2 if phase in (1,3) else 1)
        legs = [((25,56),(24+stride//2,64),(20+stride,69),25+stride),
                ((36,56),(37-stride//2,64),(39-stride,69),45-stride)]
        back_arm = ((21,35),(15-stride//2,43),(19-stride//2,51))
        fore_arm = ((40,34),(45+stride//2,42),(47+stride//2,49))
        weapon = "down"
    elif action == "attack":
        dx, dy, lean, tail = [(0,0,-2,2),(3,1,4,5),(1,0,2,3)][phase-1]
        legs = [((25,56),(22,64),(17,69),21), ((36,56),(41,63),(46,69),52)]
        back_arm = ((21,35),(15,42),(20,49))
        fore_arm = [((40,34),(37,25),(34,21)),
                    ((43,35),(50,37),(48,40)),
                    ((42,34),(50,43),(49,49))][phase-1]
        weapon = ["back","forward","down"][phase-1]
    elif action == "guard":
        dx, dy, lean, tail = (0, 0 if phase == 1 else 1, -1, 0)
        legs = [((25,56),(22,64),(18,69),23), ((36,56),(41,64),(43,69),49)]
        back_arm = ((21,35),(22,41),(31,44))
        fore_arm = ((40,34),(46,39),(43,35 if phase == 1 else 33))
        weapon = "up"
    elif action == "dodge":
        dx, dy, lean, tail = [(-4,4,-6,5),(-4,5,-9,4)][phase-1]
        legs = [((20,62),(14,67),(11,69),15), ((33,62),(38,66),(45,69),52)]
        back_arm = ((16,41),(11,49),(8,54))
        fore_arm = ((34,39),(37,46),(39,53))
        weapon = "down"
    elif action == "hit":
        dx, dy, lean, tail = [(-3,1,-5,4),(-5,3,-8,6)][phase-1]
        legs = [((22,57),(19,65),(15,69),20), ((33,57),(36,64),(39,69),45)]
        back_arm = ((18,36),(13,30),(17,26))
        fore_arm = ((37,35),(42,29),(39,25))
        weapon = "down"
    elif action == "skill":
        dx, dy, lean, tail = [(0,0,0,2),(1,-1,2,4),(2,0,3,6)][phase-1]
        legs = [((25,56),(22,64),(17,69),22), ((36,56),(41,64),(46,69),52)]
        back_arm = ((21,35),(18,28),(20,22))
        fore_arm = [((40,34),(45,37),(47,39)),
                    ((42,34),(49,35),(52,32)),
                    ((43,34),(51,33),(55,29))][phase-1]
        weapon = "none"
    else:
        raise ValueError(action)

    for idx, (hip,knee,ankle,toe) in enumerate(legs):
        leg(d, hip, knee, ankle, toe, idx == 0)
    torso(d, dx, dy, lean, tail, action == "skill")
    arm(d, *back_arm, back=True)
    head_x = 26 + dx + lean//2
    head_y = 12 + dy
    hair_and_face(d, head_x, head_y, action == "hit")
    arm(d, *fore_arm)
    terminal(d, fore_arm[2], weapon)
    if action == "skill":
        hx, hy = fore_arm[2]
        # Tactical calibration pulse expands from the tablet in her hand.
        terminal(d, (hx, hy+2), "down")
        radius = [3,5,7][phase-1]
        poly(d, [(hx+7,hy-radius),(hx+7+radius,hy),
                 (hx+7,hy+radius),(hx+7-radius,hy)], "teal_deep")
        poly(d, [(hx+7,hy-radius+2),(hx+7+radius-2,hy),
                 (hx+7,hy+radius-2),(hx+7-radius+2,hy)], "teal_hi")
        box(d, (hx+7,hy,hx+8,hy+1), "blade_hi")
    return im


def fallen(phase: int) -> Image.Image:
    im = Image.new("RGBA", SIZE, (0,0,0,0))
    d = ImageDraw.Draw(im)
    # Horizontal silhouette on the same feet baseline: long coat and bun stay visible.
    y = 0 if phase == 2 else -3
    poly(d, [(6,63+y),(18,58+y),(32,61+y),(45,62+y),
             (56,67+y),(58,73),(6,73)], "line")
    poly(d, [(8,63+y),(18,60+y),(32,63+y),(44,64+y),
             (54,69+y),(54,71),(8,71)], "coat")
    poly(d, [(8,63+y),(15,59+y),(28,64+y),(17,68+y),
             (7,72)], "coat_deep")
    poly(d, [(30,64+y),(43,65+y),(52,70+y),
             (37,71)], "shirt")
    box(d, (29,68+y,36,69+y), "leather")
    d.ellipse((32,65+y,36,69+y), fill=C["metal"])
    poly(d, [(35,59+y),(44,55+y),(52,56+y),(61,62+y),
             (65,68+y),(61,72),(40,72),(35,66+y)], "line")
    poly(d, [(39,60+y),(46,58+y),(53,59+y),(60,64+y),
             (61,70),(42,70),(38,65+y)], "skin")
    box(d, (53,67+y,59,67+y), "skin_hi")
    box(d, (58,68+y,60,68+y), "cheek")
    poly(d, [(34,59+y),(39,54+y),(44,55+y),(47,52+y),
             (52,54+y),(58,57+y),(61,63+y),(57,66+y),
             (48,62+y),(40,65+y)], "hair")
    d.ellipse((38,51+y,46,57+y), fill=C["hair_deep"])
    box(d, (40,52+y,43,53+y), "hair_hi")
    poly(d, [(45,54+y),(48,53+y),(52,56+y),(49,61+y),
             (46,64+y),(44,63+y)], "silver")
    box(d, (46,55+y,48,57+y), "silver_hi")
    box(d, (57,67+y,59,67+y), "line")
    poly(d, [(17,67),(30,63),(35,65),(38,70),
             (31,73),(15,73)], "pants")
    box(d, (6,70,21,73), "boot")
    box(d, (25,70,36,73), "boot")
    # In the first frame her head is still dropping; the second is fully grounded.
    return im


def validate(im: Image.Image, action: str, phase: int) -> dict:
    assert im.mode == "RGBA" and im.size == SIZE
    assert all(im.getpixel(pos)[3] == 0 for pos in ((0,0),(79,0),(0,79),(79,79)))
    bbox = im.getbbox()
    assert bbox is not None and bbox[0] >= 1 and bbox[1] >= 1, (action, phase, bbox)
    assert bbox[2] <= 79 and bbox[3] <= 74, (action, phase, bbox)
    assert bbox[3] == 74, (action, phase, bbox)
    used = {px for px in im.get_flattened_data() if px[3]}
    assert len(used) <= 34, (action, phase, len(used))
    assert len(used) >= 12, (action, phase, len(used))
    return {"visible_bbox": list(bbox), "palette_colors": len(used)}


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    phases = {"idle": 2, "move": 4, "attack": 3, "guard": 2,
              "dodge": 2, "hit": 2, "down": 2, "skill": 3}
    rows = []
    for action, count in phases.items():
        for phase in range(1, count + 1):
            im = fallen(phase) if action == "down" else ordinary(action, phase)
            metrics = validate(im, action, phase)
            filename = (f"{SLUG}_{CHAR}_sideview-{action}-right-phase-{phase:02d}"
                        f"_m8-prototype_{timestamp}-{uuid.uuid4().hex[:8]}.png")
            path = OUT / filename
            im.save(path)
            rows.append({"action": action, "facing": "right", "phase": phase,
                         "path": path.relative_to(ROOT).as_posix(), "dimensions": list(SIZE),
                         "anchor": list(ANCHOR), "sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
                         **metrics})
    hashes = [row["sha256"] for row in rows]
    assert len(set(hashes)) == len(hashes), "Some action frames are identical"
    manifest = OUT / (f"{SLUG}_{CHAR}_sideview-combat-manifest_m8-prototype_"
                      f"{timestamp}-{uuid.uuid4().hex[:8]}.json")
    manifest.write_text(json.dumps({"character": CHAR, "status": "unapproved_prototype",
                                    "facing": "right", "canvas": list(SIZE),
                                    "anchor": list(ANCHOR), "frame_count": len(rows),
                                    "actions": phases, "frames": rows},
                                   ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(manifest.relative_to(ROOT).as_posix())
    print(f"Validated {len(rows)} unique native side-view PNGs across {len(phases)} actions")


if __name__ == "__main__":
    main()
