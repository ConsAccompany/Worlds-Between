"""Author individual native-pixel side-view combat poses for Zhao Ling.

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
CHAR = "zhao-ling"
SIZE = (80, 80)
ANCHOR = (30, 73)

C = {
    "line": "#1d222c", "line_warm": "#343846",
    "hair_deep": "#252730", "hair": "#343944", "hair_mid": "#576270", "hair_hi": "#84909a",
    "silver": "#69aac1", "silver_hi": "#c1e9e9",
    "skin_deep": "#916457", "skin": "#c69882", "skin_hi": "#e8b9a0", "cheek": "#ad7564",
    "coat_deep": "#292d34", "coat": "#3c4149", "coat_mid": "#5b6069", "coat_hi": "#81868b",
    "shirt": "#a3a4a0", "shirt_hi": "#d2cdbd", "pants": "#303640", "pants_hi": "#525862",
    "boot": "#232b34", "boot_hi": "#59616a", "glove": "#2a303b",
    "teal_deep": "#184559", "teal": "#267c93", "teal_mid": "#5ac0cd", "teal_hi": "#a9e7e5",
    "pack": "#313842", "pack_hi": "#5b626b", "leather": "#766450", "metal": "#a69674",
    "blade_dark": "#314351", "blade": "#7f9a9e", "blade_hi": "#e2e7db",
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
    # Zhao's hair is a swept, asymmetric bob: heavy front lock and cropped back.
    poly(d, [(x-15,y+8),(x-11,y+1),(x-4,y-3),(x+5,y-2),(x+12,y+3),
             (x+14,y+10),(x+13,y+17),(x+8,y+24),(x-1,y+25),
             (x-11,y+19)], "line")
    poly(d, [(x-9,y+7),(x-4,y+1),(x+4,y+1),(x+11,y+6),
             (x+12,y+17),(x+8,y+22),(x,y+23),(x-8,y+17)], "skin")
    poly(d, [(x+4,y+17),(x+11,y+16),(x+9,y+21),(x+3,y+23)], "skin_hi")
    box(d, (x+9,y+14,x+11,y+14), "line")
    box(d, (x+10,y+18,x+11,y+18), "cheek")
    box(d, (x+7,y+21,x+10,y+21), "line_warm")
    if hit:
        box(d, (x+8,y+14,x+11,y+14), "hair_deep")
    poly(d, [(x-14,y+12),(x-14,y+4),(x-9,y-1),(x-2,y-4),
             (x+5,y-3),(x+10,y+1),(x+15,y+3),(x+14,y+8),
             (x+10,y+7),(x+7,y+14),(x+2,y+17),(x-1,y+10),
             (x-8,y+12),(x-9,y+20),(x-14,y+18)], "hair_deep")
    poly(d, [(x-12,y+5),(x-7,y),(x+1,y-2),(x+7,y+1),
             (x+12,y+4),(x+10,y+7),(x+6,y+10),(x+2,y+14),
             (x-1,y+8),(x-8,y+10),(x-11,y+16)], "hair")
    poly(d, [(x-7,y+1),(x+1,y-2),(x+4,y-1),(x-3,y+4),
             (x-7,y+7)], "hair_mid")
    poly(d, [(x+5,y+1),(x+12,y+4),(x+8,y+9),(x+5,y+12),
             (x+3,y+7)], "hair_mid")
    box(d, (x-7,y+2,x-4,y+2), "hair_hi")
    # Blue headset wraps the crown; rear ear cup and radio antenna are iconic.
    d.line([(x-8,y+1),(x-5,y-2),(x+3,y-3),(x+8,y)], fill=C["teal_mid"], width=2)
    box(d, (x-12,y+6,x-6,y+16), "line")
    box(d, (x-11,y+7,x-7,y+15), "teal")
    box(d, (x-10,y+9,x-8,y+12), "teal_hi")
    box(d, (x-14,y-7,x-13,y+5), "metal")
    box(d, (x-15,y-8,x-12,y-6), "teal_hi")
    box(d, (x-8,y+17,x-6,y+20), "teal_mid")


def torso(d: ImageDraw.ImageDraw, dx: int, dy: int, lean: int = 0,
          scarf_tail: int = 0, skill: bool = False) -> tuple[int, int]:
    tx, ty = 28 + dx, 29 + dy
    # Compact radio pack sits high behind her shoulder, no long coat panels.
    poly(d, [(tx-17,ty+1),(tx-8,ty-2),(tx-4,ty+4),
             (tx-5,ty+25),(tx-16,ty+26)], "line")
    poly(d, [(tx-15,ty+3),(tx-9,ty+1),(tx-6,ty+5),
             (tx-7,ty+23),(tx-14,ty+24)], "pack")
    box(d, (tx-14,ty+7,tx-9,ty+10), "teal_deep")
    box(d, (tx-13,ty+8,tx-10,ty+8), "teal_mid")
    box(d, (tx-13,ty+17,tx-9,ty+18), "pack_hi")
    poly(d, [(tx-8,ty),(tx+8+lean,ty-1),(tx+13+lean,ty+7),
             (tx+11,ty+26),(tx+7,ty+29),(tx-10,ty+29),
             (tx-12,ty+22),(tx-11,ty+8)], "line")
    poly(d, [(tx-6,ty+2),(tx+7+lean,ty+1),(tx+11+lean,ty+8),
             (tx+9,ty+24),(tx+5,ty+27),(tx-8,ty+27),
             (tx-10,ty+21),(tx-9,ty+8)], "coat")
    poly(d, [(tx-4,ty+3),(tx+5,ty+3),(tx+6,ty+20),
             (tx+2,ty+25),(tx-5,ty+21)], "shirt")
    box(d, (tx-3,ty+9,tx+2,ty+10), "shirt_hi")
    poly(d, [(tx-9,ty+7),(tx-4,ty+2),(tx+2,ty+7),
             (tx+7,ty+19),(tx+9,ty+25),(tx+5,ty+27),
             (tx-2,ty+10)], "leather")
    box(d, (tx+4,ty+17,tx+6,ty+19), "metal")
    poly(d, [(tx-10,ty+26),(tx-3,ty+27),(tx-2,ty+32),
             (tx-8,ty+34)], "line")
    poly(d, [(tx-9,ty+27),(tx-4,ty+28),(tx-4,ty+31),
             (tx-8,ty+32)], "pack")
    box(d, (tx-8,ty+29,tx-5,ty+29), "metal")
    box(d, (tx-8,ty+25,tx+9,ty+27), "line")
    box(d, (tx-6,ty+25,tx+8,ty+26), "leather")
    box(d, (tx+2,ty+24,tx+4,ty+27), "metal")
    # Open workshop jacket and a small pale undershirt at the collar.
    poly(d, [(tx-9,ty),(tx-5,ty-6),(tx+1,ty-4),
             (tx+3,ty+4),(tx-4,ty+8)], "coat_hi")
    poly(d, [(tx+2,ty-4),(tx+8,ty-7),(tx+10,ty+1),
             (tx+4,ty+7)], "coat_mid")
    poly(d, [(tx-3,ty-3),(tx+2,ty+1),(tx+4,ty+7),
             (tx-3,ty+5)], "shirt_hi")
    # Moving cable from the radio pack reads as a loose mechanic's accessory.
    cable_x = max(2, tx-18-scarf_tail)
    cable_end = max(3, tx-12-scarf_tail)
    d.line([(tx-14,ty+19),(cable_x,ty+29),
            (cable_end,ty+36)], fill=C["teal_deep"], width=2)
    box(d, (cable_end,ty+35,cable_end+1,ty+37), "teal_mid")
    return tx, ty


def radio_tool(d: ImageDraw.ImageDraw, hand: tuple[int, int], pose: str) -> None:
    x, y = hand
    if pose == "none":
        return
    if pose == "forward":
        poly(d, [(x,y-5),(x+12,y-6),(x+16,y-4),
                 (x+16,y-1),(x+5,y),(x+1,y+4)], "line")
        box(d, (x+2,y-4,x+12,y-2), "pack_hi")
        box(d, (x+8,y-5,x+12,y-5), "metal")
        box(d, (x+13,y-4,x+17,y-3), "blade_dark")
        box(d, (x+5,y-2,x+8,y-1), "teal_mid")
        d.line([(x+17,y-3),(x+22,y-3)], fill=C["teal_mid"], width=2)
        poly(d, [(x+22,y-5),(x+26,y-3),(x+22,y-1)], "teal_hi")
    elif pose == "up":
        poly(d, [(x-5,y-14),(x+3,y-15),(x+5,y-2),
                 (x-2,y)], "line")
        box(d, (x-3,y-12,x+2,y-9), "pack_hi")
        box(d, (x-3,y-14,x+3,y-13), "metal")
        box(d, (x-1,y-8,x+2,y-6), "teal_mid")
    elif pose == "back":
        poly(d, [(x-13,y-15),(x-5,y-18),(x+1,y-5),
                 (x-6,y)], "line")
        box(d, (x-10,y-15,x-4,y-13), "pack_hi")
        box(d, (x-12,y-17,x-8,y-16), "metal")
        box(d, (x-5,y-11,x-3,y-8), "teal_mid")
    elif pose == "down":
        poly(d, [(x-1,y),(x+7,y+2),(x+10,y+9),
                 (x+4,y+13),(x,y+8)], "line")
        poly(d, [(x+1,y+3),(x+6,y+4),(x+8,y+9),
                 (x+4,y+11)], "pack_hi")
        box(d, (x+3,y+5,x+6,y+6), "teal_mid")
        box(d, (x+6,y+10,x+8,y+11), "metal")


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
    radio_tool(d, fore_arm[2], weapon)
    if action == "skill":
        hx, hy = fore_arm[2]
        # Echo-ranging concentric signal grows from the hand-held radio tool.
        radio_tool(d, (hx, hy+2), "up")
        radius = [3,5,7][phase-1]
        cx, cy = hx+11, hy-5
        d.ellipse((cx-radius, cy-radius, cx+radius, cy+radius),
                  outline=C["teal_mid"], width=2)
        box(d, (cx,cy,cx+1,cy+1), "teal_hi")
    return im


def fallen(phase: int) -> Image.Image:
    im = Image.new("RGBA", SIZE, (0,0,0,0))
    d = ImageDraw.Draw(im)
    # Cropped bob, headset, compact radio pack, and pale shirt remain visible.
    y = 0 if phase == 2 else -3
    poly(d, [(7,61+y),(22,59+y),(37,62+y),(50,66+y),
             (55,72),(8,73)], "line")
    poly(d, [(9,63+y),(22,61+y),(37,64+y),(48,68+y),
             (52,71),(9,71)], "coat")
    box(d, (11,59+y,21,63+y), "pack")
    box(d, (13,60+y,18,60+y), "teal_mid")
    poly(d, [(25,61+y),(38,63+y),(47,68+y),
             (34,70+y)], "shirt")
    box(d, (28,66+y,35,67+y), "leather")
    box(d, (31,65+y,33,68+y), "metal")
    poly(d, [(36,58+y),(45,56+y),(53,59+y),(61,64+y),
             (64,69+y),(59,72),(40,72)], "line")
    poly(d, [(39,61+y),(47,58+y),(54,61+y),(60,65+y),
             (60,70),(43,70)], "skin")
    box(d, (54,67+y,59,67+y), "skin_hi")
    poly(d, [(36,59+y),(40,55+y),(47,53+y),(54,57+y),
             (58,62+y),(56,66+y),(48,64+y),(42,66+y)], "hair_deep")
    poly(d, [(40,57+y),(48,55+y),(53,58+y),(55,62+y),
             (49,62+y),(44,64+y)], "hair")
    box(d, (42,56+y,45,56+y), "hair_hi")
    box(d, (40,61+y,43,65+y), "teal")
    box(d, (41,62+y,42,64+y), "teal_hi")
    box(d, (39,52+y,40,61+y), "metal")
    poly(d, [(18,66),(31,63),(37,67),(35,72),
             (16,73)], "pants")
    box(d, (8,70,23,73), "boot")
    box(d, (26,70,37,73), "boot")
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
