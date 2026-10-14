"""Author individual native-pixel side-view combat poses for Ji Cheng.

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
from io import BytesIO
from pathlib import Path

from PIL import Image, ImageDraw


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "game" / "assets" / "characters" / "combat-prototypes"
SLUG = "rpg-2-star-ocean-the-second"
CHAR = "ji-cheng"
SIZE = (80, 80)
ANCHOR = (30, 73)

C = {
    "line": "#1b2423", "line_warm": "#363e3b",
    "hair_deep": "#24282c", "hair": "#3c4042", "hair_mid": "#62686a", "hair_hi": "#92989a",
    "silver": "#bbc1bd", "silver_hi": "#e2e3d8",
    "skin_deep": "#8c6155", "skin": "#c09680", "skin_hi": "#e1b39c", "cheek": "#a16b5c",
    "coat_deep": "#20382e", "coat": "#304e3c", "coat_mid": "#52705a", "coat_hi": "#758976",
    "shirt": "#413f3a", "shirt_hi": "#72736b", "pants": "#303536", "pants_hi": "#515954",
    "boot": "#202a2b", "boot_hi": "#59635c", "glove": "#2a3330",
    "teal_deep": "#245341", "teal": "#397e5e", "teal_mid": "#87bc8b", "teal_hi": "#d2e3ae",
    "pack": "#3b3c32", "pack_hi": "#666651", "leather": "#7d6848", "metal": "#c0a979",
    "blade_dark": "#5d7169", "blade": "#acb8a3", "blade_hi": "#e3e5c8",
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
    # Shaved right temple opposes a heavy left curtain ending in silver at shoulder.
    poly(d, [(x-14,y+7),(x-11,y),(x-4,y-4),(x+5,y-3),(x+12,y+3),
             (x+14,y+10),(x+13,y+17),(x+8,y+24),(x-1,y+25),
             (x-11,y+20)], "line")
    poly(d, [(x-9,y+7),(x-4,y+1),(x+4,y+1),(x+11,y+6),
             (x+12,y+17),(x+8,y+22),(x,y+23),(x-8,y+17)], "skin")
    poly(d, [(x+4,y+17),(x+11,y+16),(x+9,y+21),(x+3,y+23)], "skin_hi")
    box(d, (x+9,y+14,x+11,y+14), "line")
    box(d, (x+10,y+18,x+11,y+18), "cheek")
    box(d, (x+7,y+21,x+10,y+21), "line_warm")
    if hit:
        box(d, (x+8,y+14,x+11,y+14), "hair_deep")
    poly(d, [(x-15,y+6),(x-12,y),(x-5,y-4),(x+3,y-4),
             (x+8,y-1),(x+10,y+4),(x+4,y+4),(x-3,y+8),
             (x-7,y+14),(x-8,y+29),(x-11,y+32),
             (x-16,y+28),(x-14,y+17)], "hair_deep")
    poly(d, [(x-12,y+4),(x-7,y-1),(x+1,y-3),(x+6,y),
             (x+5,y+4),(x-2,y+7),(x-6,y+14),
             (x-8,y+25),(x-12,y+29),(x-14,y+26),
             (x-12,y+14)], "hair")
    poly(d, [(x-8,y),(x-1,y-3),(x+3,y-2),(x-2,y+2),
             (x-6,y+6)], "hair_mid")
    box(d, (x-7,y+1,x-4,y+1), "hair_hi")
    # The temple has a visible shaved wedge with two short stubble strokes.
    poly(d, [(x+4,y+3),(x+10,y+4),(x+9,y+10),
             (x+4,y+11),(x+1,y+8)], "skin_deep")
    poly(d, [(x+5,y+4),(x+9,y+5),(x+8,y+8),
             (x+4,y+9)], "skin")
    box(d, (x+5,y+5,x+7,y+5), "hair_mid")
    box(d, (x+5,y+7,x+6,y+7), "hair_mid")
    # Silver ends are a separate high-contrast wedge, not a broad side lock.
    poly(d, [(x-14,y+23),(x-10,y+25),(x-8,y+28),
             (x-11,y+32),(x-16,y+28)], "silver")
    box(d, (x-13,y+26,x-11,y+28), "silver_hi")


def torso(d: ImageDraw.ImageDraw, dx: int, dy: int, lean: int = 0,
          scarf_tail: int = 0, skill: bool = False) -> tuple[int, int]:
    tx, ty = 28 + dx, 29 + dy
    # A satchel sits on the back; the split forest-green coat exposes a pale
    # patterned inner hanging panel. Its silhouette is unlike Zhao's short jacket.
    poly(d, [(tx-16,ty+8),(tx-10,ty+5),(tx-5,ty+9),
             (tx-5,ty+24),(tx-15,ty+26)], "line")
    poly(d, [(tx-14,ty+9),(tx-10,ty+7),(tx-7,ty+10),
             (tx-7,ty+23),(tx-13,ty+24)], "pack")
    box(d, (tx-14,ty+14,tx-8,ty+15), "metal")
    poly(d, [(tx-9,ty),(tx+8+lean,ty-1),(tx+13+lean,ty+7),
             (tx+10,ty+26),(tx+17+scarf_tail,ty+34),
             (tx+13+scarf_tail,ty+38),(tx+2,ty+34),
             (tx-9-scarf_tail,ty+39),(tx-14-scarf_tail,ty+35),
             (tx-11,ty+8)], "line")
    poly(d, [(tx-7,ty+2),(tx+7+lean,ty+1),(tx+11+lean,ty+8),
             (tx+8,ty+25),(tx+14+scarf_tail,ty+34),
             (tx+12+scarf_tail,ty+36),(tx+2,ty+31),
             (tx-10-scarf_tail,ty+36),(tx-12-scarf_tail,ty+33),
             (tx-9,ty+8)], "coat")
    poly(d, [(tx-10,ty+15),(tx-3,ty+17),(tx-4,ty+31),
             (tx-11-scarf_tail,ty+35)], "coat_deep")
    poly(d, [(tx+2,ty+26),(tx+9,ty+23),
             (tx+15+scarf_tail,ty+35),(tx+11+scarf_tail,ty+36),
             (tx+3,ty+31)], "shirt_hi")
    d.line([(tx+4,ty+30),(tx+10+scarf_tail,ty+35)], fill=C["metal"], width=1)
    box(d, (tx+8,ty+30,tx+9,ty+31), "coat_mid")
    poly(d, [(tx-2,ty+3),(tx+6,ty+3),(tx+5,ty+19),
             (tx-1,ty+24)], "shirt")
    poly(d, [(tx-8,ty+4),(tx-3,ty+1),(tx+3,ty+7),
             (tx+7,ty+21),(tx+9,ty+25),(tx+5,ty+27),
             (tx-2,ty+9)], "leather")
    box(d, (tx+2,ty+18,tx+4,ty+20), "metal")
    box(d, (tx-7,ty+25,tx+9,ty+27), "line")
    box(d, (tx-6,ty+25,tx+8,ty+26), "leather")
    box(d, (tx+2,ty+24,tx+4,ty+27), "metal")
    # A high dark collar and rolled green lapels frame the head.
    poly(d, [(tx-8,ty+1),(tx-7,ty-8),(tx-2,ty-10),
             (tx+1,ty-3),(tx+6,ty-9),(tx+10,ty-6),
             (tx+9,ty+4),(tx+2,ty+7),(tx-4,ty+6)], "line")
    poly(d, [(tx-6,ty-6),(tx-3,ty-8),(tx,ty-2),
             (tx+1,ty+5),(tx-5,ty+3)], "coat_mid")
    poly(d, [(tx+6,ty-7),(tx+8,ty-5),(tx+8,ty+2),
             (tx+3,ty+5)], "coat_hi")
    box(d, (tx-1,ty+4,tx+2,ty+5), "metal")
    return tx, ty


def magnifier(d: ImageDraw.ImageDraw, hand: tuple[int, int], pose: str) -> None:
    x, y = hand
    if pose == "none":
        return
    if pose == "forward":
        d.line([(x,y),(x+5,y-3)], fill=C["line"], width=4)
        d.line([(x+1,y-1),(x+5,y-3)], fill=C["metal"], width=2)
        d.ellipse((x+4,y-12,x+15,y-1), fill=C["line"])
        d.ellipse((x+5,y-11,x+14,y-2), fill=C["metal"])
        d.ellipse((x+7,y-9,x+12,y-4), fill=C["blade"])
        box(d, (x+8,y-8,x+10,y-7), "blade_hi")
        d.line([(x+15,y-6),(x+21,y-6)], fill=C["teal_mid"], width=2)
        poly(d, [(x+21,y-8),(x+25,y-6),(x+21,y-4)], "teal_hi")
    elif pose == "up":
        d.line([(x,y),(x,y-7)], fill=C["line"], width=4)
        d.line([(x,y-1),(x,y-7)], fill=C["metal"], width=2)
        d.ellipse((x-6,y-19,x+6,y-7), fill=C["line"])
        d.ellipse((x-5,y-18,x+5,y-8), fill=C["metal"])
        d.ellipse((x-3,y-16,x+3,y-10), fill=C["blade"])
        box(d, (x-1,y-15,x+1,y-14), "blade_hi")
    elif pose == "back":
        d.line([(x,y),(x-4,y-6)], fill=C["line"], width=4)
        d.line([(x-1,y-1),(x-4,y-6)], fill=C["metal"], width=2)
        d.ellipse((x-15,y-20,x-3,y-8), fill=C["line"])
        d.ellipse((x-14,y-19,x-4,y-9), fill=C["metal"])
        d.ellipse((x-12,y-17,x-6,y-11), fill=C["blade"])
    elif pose == "down":
        d.line([(x,y),(x+4,y+3)], fill=C["line"], width=4)
        d.line([(x+1,y),(x+4,y+3)], fill=C["metal"], width=2)
        d.ellipse((x+3,y+2,x+13,y+12), fill=C["line"])
        d.ellipse((x+4,y+3,x+12,y+11), fill=C["metal"])
        d.ellipse((x+6,y+5,x+10,y+9), fill=C["blade"])


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
    magnifier(d, fore_arm[2], weapon)
    if action == "skill":
        hx, hy = fore_arm[2]
        # Fault-line recollection projects a changing stepped relic glyph.
        magnifier(d, (hx, hy+2), "up")
        radius = [3,5,7][phase-1]
        cx, cy = hx+11, hy-7
        poly(d, [(cx,cy-radius),(cx+radius,cy),
                 (cx,cy+radius),(cx-radius,cy)], "teal_deep")
        poly(d, [(cx,cy-radius+2),(cx+radius-2,cy),
                 (cx,cy+radius-2),(cx-radius+2,cy)], "teal_mid")
        box(d, (cx-1,cy-1,cx+1,cy+1), "metal")
    return im


def fallen(phase: int) -> Image.Image:
    im = Image.new("RGBA", SIZE, (0,0,0,0))
    d = ImageDraw.Draw(im)
    # Long green split coat and silver-tipped hair remain visible when down.
    y = 0 if phase == 2 else -3
    poly(d, [(6,62+y),(20,58+y),(32,61+y),(46,63+y),
             (57,69+y),(59,73),(6,73)], "line")
    poly(d, [(8,63+y),(20,60+y),(32,63+y),(44,65+y),
             (55,70+y),(55,71),(8,71)], "coat")
    poly(d, [(8,63+y),(18,59+y),(28,64+y),(19,70+y),
             (7,72)], "coat_deep")
    poly(d, [(30,64+y),(43,65+y),(53,70+y),
             (42,71)], "shirt_hi")
    box(d, (30,68+y,38,68+y), "leather")
    box(d, (33,66+y,35,69+y), "metal")
    poly(d, [(36,59+y),(45,55+y),(53,57+y),(61,63+y),
             (65,69+y),(61,72),(41,72),(35,65+y)], "line")
    poly(d, [(39,61+y),(47,58+y),(54,60+y),(60,65+y),
             (61,70),(43,70),(38,65+y)], "skin")
    box(d, (54,67+y,59,67+y), "skin_hi")
    poly(d, [(34,60+y),(39,54+y),(44,53+y),(50,54+y),
             (54,58+y),(54,64+y),(48,63+y),(45,67+y),
             (38,67+y)], "hair_deep")
    poly(d, [(37,60+y),(42,55+y),(48,55+y),(51,59+y),
             (48,64+y),(41,65+y)], "hair")
    box(d, (41,55+y,45,55+y), "hair_hi")
    poly(d, [(36,63+y),(41,65+y),(44,68+y),
             (41,72),(35,71)], "silver")
    box(d, (38,67+y,40,68+y), "silver_hi")
    box(d, (57,67+y,59,67+y), "line")
    poly(d, [(18,66),(30,63),(37,66),(38,71),
             (31,73),(16,73)], "pants")
    box(d, (6,70,23,73), "boot")
    box(d, (26,70,38,73), "boot")
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
    phases = {"idle": 2, "move": 4, "attack": 3, "guard": 2,
              "dodge": 2, "hit": 2, "down": 2, "skill": 3}
    rendered = []
    for action, count in phases.items():
        for phase in range(1, count + 1):
            im = fallen(phase) if action == "down" else ordinary(action, phase)
            metrics = validate(im, action, phase)
            blob = BytesIO()
            im.save(blob, format="PNG")
            rendered.append((action, phase, metrics, blob.getvalue()))
    # Validate the complete batch before writing any asset, avoiding orphan
    # frames if a late action violates the canvas or uniqueness requirements.
    hashes = [hashlib.sha256(blob).hexdigest() for _, _, _, blob in rendered]
    assert len(rendered) == 20 and len(set(hashes)) == 20
    timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    rows = []
    writes = []
    for action, phase, metrics, blob in rendered:
            filename = (f"{SLUG}_{CHAR}_sideview-{action}-right-phase-{phase:02d}"
                        f"_m8-prototype_{timestamp}-{uuid.uuid4().hex[:8]}.png")
            path = OUT / filename
            writes.append((path, blob))
            rows.append({"action": action, "facing": "right", "phase": phase,
                         "path": path.relative_to(ROOT).as_posix(), "dimensions": list(SIZE),
                         "anchor": list(ANCHOR), "sha256": hashlib.sha256(blob).hexdigest(),
                         **metrics})
    OUT.mkdir(parents=True, exist_ok=True)
    for path, blob in writes:
        path.write_bytes(blob)
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
