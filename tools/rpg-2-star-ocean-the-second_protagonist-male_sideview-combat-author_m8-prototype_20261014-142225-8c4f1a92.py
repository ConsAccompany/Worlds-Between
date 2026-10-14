"""Author individual native-pixel side-view combat poses for the male protagonist.

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
CHAR = "protagonist-male"
SIZE = (80, 80)
ANCHOR = (30, 73)

C = {
    "line": "#25252b", "line_warm": "#3b3233",
    "hair_deep": "#302a2d", "hair": "#4c3935", "hair_mid": "#76554b", "hair_hi": "#a0775d",
    "skin_deep": "#9d604e", "skin": "#d4a07b", "skin_hi": "#efc39a", "cheek": "#b8795e",
    "coat_deep": "#453a39", "coat": "#685347", "coat_mid": "#896c58", "coat_hi": "#aa896b",
    "shirt": "#c9bba1", "shirt_hi": "#ece0c5", "pants": "#6d6258", "pants_hi": "#958577",
    "boot": "#3d3432", "boot_hi": "#6c5547", "glove": "#4a3d38",
    "teal_deep": "#1d4953", "teal": "#287d87", "teal_mid": "#51aeb3", "teal_hi": "#a4d6d0",
    "pack": "#544139", "pack_hi": "#816149", "leather": "#9c7656", "metal": "#dbbc8b",
    "blade_dark": "#54666c", "blade": "#b5ced0", "blade_hi": "#ecf3e8",
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
    # Face points right. Uneven peaks and a forward lock separate his head
    # silhouette from the female protagonist's tall side ponytail.
    poly(d, [(x-12,y+10),(x-11,y+3),(x-6,y-1),(x+4,y-2),(x+11,y+2),
             (x+14,y+7),(x+15,y+15),(x+11,y+22),(x+3,y+25),
             (x-8,y+21),(x-12,y+16)], "line")
    poly(d, [(x-9,y+10),(x-7,y+4),(x+2,y+1),(x+10,y+5),(x+12,y+11),
             (x+13,y+17),(x+8,y+22),(x+1,y+23),(x-8,y+18)], "skin")
    poly(d, [(x+4,y+18),(x+12,y+16),(x+10,y+21),(x+3,y+23)], "skin_hi")
    box(d, (x-11,y+12,x-9,y+16), "skin_deep")
    box(d, (x+10,y+15,x+11,y+15), "line")
    box(d, (x+11,y+18,x+13,y+18), "cheek")
    box(d, (x+7,y+20,x+10,y+20), "line_warm")
    if hit:
        box(d, (x+9,y+15,x+12,y+15), "hair_deep")
    # Jagged short-hair crown, asymmetric left and right side clumps.
    poly(d, [(x-14,y+10),(x-16,y+5),(x-12,y+4),(x-13,y+1),
             (x-8,y+2),(x-6,y-3),(x-2,y-1),(x+1,y-5),
             (x+5,y-2),(x+8,y-4),(x+10,y+1),(x+14,y),
             (x+12,y+5),(x+17,y+8),(x+13,y+11),(x+7,y+9),
             (x+4,y+12),(x-1,y+9),(x-6,y+13),(x-11,y+12)], "line")
    poly(d, [(x-12,y+6),(x-7,y+4),(x-4,y),(x,y+1),(x+3,y-2),
             (x+7,y+1),(x+9,y+3),(x+13,y+3),(x+11,y+7),
             (x+14,y+8),(x+9,y+8),(x+6,y+6),(x+3,y+10),
             (x-2,y+7),(x-7,y+10),(x-11,y+9)], "hair")
    poly(d, [(x-11,y+5),(x-6,y+3),(x-7,y+7),(x-12,y+9)], "hair_deep")
    poly(d, [(x-4,y+2),(x+1,y),(x+4,y+2),(x,y+4)], "hair_mid")
    poly(d, [(x+5,y+2),(x+9,y+3),(x+8,y+5),(x+3,y+5)], "hair_mid")
    box(d, (x-2,y+1,x+1,y+1), "hair_hi")


def pack(d: ImageDraw.ImageDraw, tx: int, ty: int, bounce: int) -> None:
    # Compact pack and rolled teal bedroll remain legible in the profile.
    poly(d, [(tx-12,ty+1),(tx-5,ty-2),(tx+1,ty+1),(tx+2,ty+22),
             (tx-5,ty+26),(tx-13,ty+22)], "line")
    poly(d, [(tx-10,ty+3),(tx-5,ty),(tx,ty+2),(tx,ty+20),
             (tx-5,ty+23),(tx-11,ty+20)], "pack")
    box(d, (tx-9,ty+8,tx-2,ty+9), "pack_hi")
    box(d, (tx-8,ty+18,tx-2,ty+19), "leather")
    poly(d, [(tx-7,ty+11),(tx-4,ty+8),(tx-1,ty+11),(tx-4,ty+14)], "teal_mid")
    poly(d, [(tx-4,ty+9),(tx-2,ty+11),(tx-4,ty+13),(tx-6,ty+11)], "teal_deep")
    poly(d, [(tx-12,ty-3+bounce),(tx-8,ty-5+bounce),(tx+1,ty-5+bounce),
             (tx+3,ty-2+bounce),(tx+1,ty+1+bounce),(tx-10,ty+1+bounce)], "line")
    box(d, (tx-10,ty-4+bounce,tx+1,ty-1+bounce), "teal")
    box(d, (tx-7,ty-4+bounce,tx-1,ty-4+bounce), "teal_hi")
    box(d, (tx-9,ty-5+bounce,tx-8,ty+1+bounce), "leather")


def torso(d: ImageDraw.ImageDraw, dx: int, dy: int, lean: int = 0,
          scarf_tail: int = 0, skill: bool = False) -> tuple[int, int]:
    tx, ty = 28 + dx, 29 + dy
    pack(d, tx-5, ty+1, 1 if skill else 0)
    poly(d, [(tx-7,ty),(tx+9+lean,ty-2),(tx+14+lean,ty+6),
             (tx+12+lean,ty+26),(tx+4,ty+37),(tx-12,ty+35),
             (tx-11,ty+8)], "line")
    poly(d, [(tx-5,ty+2),(tx+8+lean,ty),(tx+12+lean,ty+7),
             (tx+10+lean,ty+25),(tx+2,ty+34),(tx-9,ty+32),
             (tx-9,ty+8)], "coat")
    poly(d, [(tx-9,ty+23),(tx-1,ty+26),(tx-3,ty+35),(tx-11,ty+34)], "coat_deep")
    poly(d, [(tx+4,ty+22),(tx+11+lean,ty+20),(tx+8,ty+32),(tx+2,ty+35)], "coat_mid")
    poly(d, [(tx+2,ty+3),(tx+10+lean,ty+4),(tx+8,ty+21),(tx+1,ty+19)], "shirt")
    box(d, (tx+5,ty+8,tx+7,ty+17), "shirt_hi")
    poly(d, [(tx+9,ty+10),(tx+12,ty+13),(tx+9,ty+16),(tx+6,ty+13)], "teal_hi")
    poly(d, [(tx+9,ty+11),(tx+11,ty+13),(tx+9,ty+15),(tx+7,ty+13)], "teal")
    box(d, (tx-5,ty+26,tx+7,ty+28), "leather")
    box(d, (tx+4,ty+26,tx+5,ty+28), "metal")
    # Tea-green scarf crosses the neck and trails behind his left shoulder.
    poly(d, [(tx-7,ty-2),(tx-4,ty-7),(tx+7,ty-7),(tx+11,ty-1),
             (tx+5,ty+4),(tx-4,ty+2)], "teal_deep")
    poly(d, [(tx-5,ty-4),(tx-1,ty-6),(tx+7,ty-5),(tx+9,ty-1),
             (tx+4,ty+2),(tx-3,ty)], "teal")
    box(d, (tx-2,ty-4,tx+6,ty-4), "teal_mid")
    poly(d, [(tx-4,ty-1),(tx-10,ty+1),(tx-14-scarf_tail,ty+9),
             (tx-12-scarf_tail,ty+18),(tx-8,ty+15),(tx-5,ty+6)], "teal_deep")
    poly(d, [(tx-5,ty+1),(tx-10,ty+5),(tx-12-scarf_tail,ty+12),
             (tx-9,ty+12),(tx-5,ty+6)], "teal")
    box(d, (tx-10,ty+8,tx-8,ty+9), "teal_mid")
    return tx, ty


def sword(d: ImageDraw.ImageDraw, hand: tuple[int, int], pose: str) -> None:
    x, y = hand
    if pose == "none":
        return
    if pose == "forward":
        box(d, (x, y-2, x+7, y+1), "line")
        box(d, (x+2, y-1, x+6, y), "leather")
        box(d, (x+7, y-5, x+9, y+4), "metal")
        poly(d, [(x+10,y-2),(x+24,y-3),(x+28,y),(x+24,y+3),
                 (x+10,y+2)], "blade_dark")
        poly(d, [(x+11,y-1),(x+23,y-2),(x+27,y),(x+22,y),
                 (x+11,y+1)], "blade_hi")
    elif pose == "up":
        box(d, (x-2,y-7,x+1,y), "leather")
        box(d, (x-5,y-9,x+4,y-7), "metal")
        poly(d, [(x-2,y-10),(x-3,y-26),(x,y-31),(x+3,y-26),
                 (x+2,y-10)], "blade_dark")
        poly(d, [(x-1,y-11),(x-1,y-26),(x,y-29),(x+1,y-26),
                 (x,y-11)], "blade_hi")
    elif pose == "back":
        d.line([(x,y),(x-6,y-4),(x-15,y-19)], fill=C["blade_dark"], width=5)
        d.line([(x-6,y-5),(x-15,y-19)], fill=C["blade_hi"], width=2)
        box(d, (x-5,y-5,x+1,y-2), "metal")
    elif pose == "down":
        d.line([(x,y),(x+7,y+6),(x+19,y+15)], fill=C["blade_dark"], width=5)
        d.line([(x+8,y+7),(x+17,y+14)], fill=C["blade_hi"], width=2)
        box(d, (x+2,y+2,x+7,y+7), "metal")


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
        dx, dy, lean, tail = [(-4,5,-6,5),(-4,7,-9,4)][phase-1]
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
    head_y = 8 + dy
    hair_and_face(d, head_x, head_y, action == "hit")
    arm(d, *fore_arm)
    sword(d, fore_arm[2], weapon)
    if action == "skill":
        hx, hy = fore_arm[2]
        # Personal-skill read: a diamond of discovery light in the hand.
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
    # Horizontal silhouette on the same feet baseline; head faces right.
    y = 0 if phase == 2 else -3
    poly(d, [(7,63+y),(29,60+y),(46,62+y),(55,66+y),(57,73),
             (6,73)], "line")
    poly(d, [(9,64+y),(27,62+y),(42,64+y),(52,68+y),(53,71),
             (8,71)], "coat")
    box(d, (21,63+y,30,64+y), "coat_mid")
    box(d, (28,68+y,36,68+y), "leather")
    box(d, (31,68+y,32,68+y), "metal")
    poly(d, [(32,63+y),(35,65+y),(32,68+y),(29,65+y)], "teal_hi")
    poly(d, [(8,63+y),(17,61+y),(21,65+y),(16,70)], "teal_deep")
    box(d, (10,64+y,19,65+y), "teal")
    poly(d, [(35,57+y),(47,56+y),(54,60+y),(61,64+y),(63,69+y),
             (59,72),(39,72),(34,66+y)], "line")
    poly(d, [(37,60+y),(47,58+y),(54,62+y),(59,65+y),
             (59,70),(40,70),(36,65+y)], "skin")
    box(d, (53,66+y,58,66+y), "skin_hi")
    box(d, (56,68+y,58,68+y), "cheek")
    poly(d, [(34,59+y),(37,55+y),(42,57+y),(45,53+y),(50,56+y),
             (55,55+y),(56,60+y),(61,61+y),(59,65+y),
             (53,64+y),(48,61+y),(43,64+y),(37,63+y)], "hair")
    box(d, (41,57+y,47,58+y), "hair_mid")
    box(d, (55,67+y,57,67+y), "line")
    poly(d, [(19,66),(28,62),(34,64),(38,69),(32,73),(16,73)], "pants")
    box(d, (7,70,23,73), "boot")
    box(d, (25,70,36,73), "boot")
    # The later frame is fully grounded; earlier frame retains airborne gap.
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
