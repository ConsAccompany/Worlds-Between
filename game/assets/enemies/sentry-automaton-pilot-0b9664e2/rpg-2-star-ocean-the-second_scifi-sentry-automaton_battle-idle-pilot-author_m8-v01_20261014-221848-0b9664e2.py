"""Author the UNAPPROVED native-pixel sentry automaton battle pilot (one static idle frame, facing left).

Every plate, joint, light and grime pixel below is an explicitly placed shape or
pixel on the final 96x62 canvas. No concept image is opened, sampled, traced or
resized; the two unapproved sentry concepts and the patrol pilot were used only
as visual reference:
  outputs/rpg-2-star-ocean-the-second_scifi-sentry-automaton_character-sheet-unapproved_m8-v01_20261014-210321-64fc7295.png
  outputs/rpg-2-star-ocean-the-second_scifi-sentry-automaton_single-sprite-style-concept-unapproved_m8-v02_20261014-211731-d544cc62.png
  game/assets/enemies/patrol-automaton-pilot/rpg-2-star-ocean-the-second_scifi-patrol-automaton_battle-idle-left_m8-pilot-v01_20261014-220008-36512fae.png

Design read: low, wide four-leg crab stance with one large cyan eye in a brass
bezel at the front (left), a faceted slate carapace with brass straps, a far-side
hood fin, a near cheek plate, rear vent plate and a small top dome. It shares the
patrol's slate/brass/cyan palette but none of its tall humanoid shapes.

Parts are composited back to front. Each part gets a 1px dark ring, so a front
part leaves a seam where it overlaps a back part and the outer silhouette is
outlined. Top/left exterior outline pixels are then softened (selective outline).
The ground-contact anchor is the near-foot sole outline row; far feet sit 2px
higher for depth.

Usage (bundled Python/Pillow runtime, run with -I):
  python <this file> --out DIR      -> scratch render (PNG + 6x preview) for iteration, no manifest
  python <this file> --final DIR    -> new uniquely named PNG + manifest in DIR (never overwrites)
"""

from __future__ import annotations

import argparse
import hashlib
import json
import uuid
from datetime import datetime
from pathlib import Path

from PIL import Image, ImageDraw

SLUG = "rpg-2-star-ocean-the-second"
SIZE = (96, 62)
ANCHOR = (48, 60)
CONCEPTS = [
    "outputs/rpg-2-star-ocean-the-second_scifi-sentry-automaton_character-sheet-unapproved_m8-v01_20261014-210321-64fc7295.png",
    "outputs/rpg-2-star-ocean-the-second_scifi-sentry-automaton_single-sprite-style-concept-unapproved_m8-v02_20261014-211731-d544cc62.png",
]
PATROL_REF = "game/assets/enemies/patrol-automaton-pilot/rpg-2-star-ocean-the-second_scifi-patrol-automaton_battle-idle-left_m8-pilot-v01_20261014-220008-36512fae.png"

# Same ramps as the patrol pilot: dark slate, aged brass, one rust/grime tone, cyan sensor.
PALETTE = {
    "o": "#101217",
    "1": "#1b1f26", "2": "#282e37", "3": "#384049", "4": "#4c5562", "5": "#67717e", "6": "#8b95a1",
    "a": "#36291b", "b": "#5a462b", "c": "#806439", "d": "#a6864f", "e": "#cbb077",
    "r": "#4b3627",
    "x": "#0c363c", "y": "#188a92", "z": "#4bd5d2", "w": "#c6fff6",
}
INDEX = {key: i + 1 for i, key in enumerate(PALETTE)}
KEYS = {v: k for k, v in INDEX.items()}
W, H = SIZE


class Part:
    """One plate group drawn into its own index layer; later paints clip to the part mask."""

    def __init__(self, name: str):
        self.name = name
        self.layer = Image.new("L", SIZE, 0)
        self.draw = ImageDraw.Draw(self.layer)

    def poly(self, pts, key):
        self.draw.polygon(pts, fill=INDEX[key])

    def rect(self, x0, y0, x1, y1, key):
        self.draw.rectangle((x0, y0, x1, y1), fill=INDEX[key])

    def oval(self, x0, y0, x1, y1, key):
        self.draw.ellipse((x0, y0, x1, y1), fill=INDEX[key])

    def px(self, pts, key):
        for p in pts:
            self.layer.putpixel(p, INDEX[key])

    def _clip(self, shape_fn, key):
        mask = Image.new("L", SIZE, 0)
        shape_fn(ImageDraw.Draw(mask))
        src = self.layer.load()
        m = mask.load()
        for y in range(H):
            for x in range(W):
                if m[x, y] and src[x, y]:
                    src[x, y] = INDEX[key]

    def clip_rect(self, x0, y0, x1, y1, key):
        self._clip(lambda d: d.rectangle((x0, y0, x1, y1), fill=255), key)

    def clip_poly(self, pts, key):
        self._clip(lambda d: d.polygon(pts, fill=255), key)

    def clip_oval(self, x0, y0, x1, y1, key):
        self._clip(lambda d: d.ellipse((x0, y0, x1, y1), fill=255), key)

    def rim(self, lit: str, dark: str):
        """Recolour the part's own border: top/left-facing edge lit, bottom/right dark."""
        src = self.layer.load()
        inside = {(x, y) for y in range(H) for x in range(W) if src[x, y]}
        changes = {}
        for x, y in inside:
            up, left = (x, y - 1) not in inside, (x - 1, y) not in inside
            down, right = (x, y + 1) not in inside, (x + 1, y) not in inside
            if up or left:
                changes[(x, y)] = lit
            elif down or right:
                changes[(x, y)] = dark
        for (x, y), key in changes.items():
            src[x, y] = INDEX[key]


def build_parts() -> list[Part]:
    parts = []

    # Far-side rear leg: darkest ramp, foot 2px above the near soles.
    p = Part("far_rear_leg")
    p.poly([(60, 28), (66, 26), (73, 34), (69, 38)], "2")
    p.clip_poly([(60, 28), (66, 26), (68, 28), (62, 30)], "3")
    p.poly([(68, 37), (73, 37), (77, 52), (72, 52)], "2")
    p.clip_poly([(72, 37), (73, 37), (77, 52), (76, 52)], "1")
    p.oval(67, 32, 73, 38, "b")
    p.oval(68, 33, 71, 36, "a")
    p.px([(69, 33), (68, 34)], "c")
    p.rect(67, 53, 79, 57, "1")
    p.rect(67, 53, 79, 53, "2")
    p.rect(76, 53, 79, 57, "b")
    p.px([(76, 53), (77, 53)], "c")
    parts.append(p)

    # Far-side front leg, half hidden behind the eye housing.
    p = Part("far_front_leg")
    p.poly([(40, 28), (44, 32), (32, 40), (29, 36)], "2")
    p.poly([(26, 39), (31, 39), (29, 52), (24, 52)], "2")
    p.clip_poly([(30, 39), (31, 39), (29, 52), (28, 52)], "1")
    p.oval(25, 34, 31, 40, "b")
    p.oval(26, 35, 29, 38, "a")
    p.px([(27, 35), (26, 36)], "c")
    p.rect(19, 53, 31, 57, "1")
    p.rect(19, 53, 31, 53, "2")
    p.rect(19, 53, 22, 57, "b")
    p.px([(20, 53), (21, 53)], "c")
    parts.append(p)

    # Underslung drive housing: ribbed dark machinery with one brass gear.
    p = Part("belly")
    p.poly([(32, 25), (80, 25), (75, 35), (38, 35)], "1")
    for x in range(40, 74, 4):
        p.clip_rect(x, 29, x, 33, "2")
    p.oval(50, 28, 58, 36, "b")
    p.oval(52, 30, 56, 34, "a")
    p.px([(51, 30), (52, 29), (53, 29)], "c")
    p.px([(54, 32)], "c")
    parts.append(p)

    # Main carapace: rounded crab shell, low at the eye, high mid-back, sloped tail.
    p = Part("shell")
    p.poly([(28, 15), (36, 9), (46, 6), (55, 4), (66, 4), (76, 6), (85, 11), (91, 18), (91, 24), (86, 30), (30, 30)], "4")
    p.clip_poly([(36, 9), (46, 6), (55, 4), (66, 4), (72, 5), (66, 8), (56, 8), (46, 10), (38, 13)], "5")
    p.clip_poly([(72, 5), (85, 11), (91, 18), (91, 23), (84, 20), (76, 12), (68, 9)], "3")
    p.clip_rect(26, 23, 92, 30, "3")
    p.rim("6", "2")
    p.clip_rect(29, 23, 90, 23, "2")
    p.clip_rect(29, 24, 89, 24, "4")
    # Brass straps over the top plates, raked back with the dome.
    for x0 in (47, 69):
        p.clip_poly([(x0, 5), (x0 + 3, 5), (x0 + 4, 22), (x0 + 1, 22)], "c")
        p.clip_poly([(x0, 5), (x0 + 1, 5), (x0 + 2, 22), (x0 + 1, 22)], "d")
        p.clip_poly([(x0 + 3, 5), (x0 + 3, 5), (x0 + 4, 22), (x0 + 4, 22)], "b")
        p.clip_rect(x0 + 1, 25, x0 + 4, 27, "b")
        p.clip_rect(x0 + 1, 25, x0 + 3, 25, "c")
    # Skirt plate seams and rear vents.
    for x in (60, 79):
        p.clip_rect(x, 25, x, 29, "2")
        p.clip_rect(x + 1, 25, x + 1, 29, "4")
    for x in (83, 85, 87):
        p.clip_rect(x, 25, x, 28, "1")
    p.px([(89, 21), (89, 22)], "y")
    p.px([(90, 21)], "z")
    # Top panel seams and rivets.
    p.px([(38, 15), (39, 15), (40, 14), (41, 14), (42, 14), (43, 14)], "3")
    p.px([(56, 13), (57, 13), (58, 13), (59, 13), (60, 13), (61, 13), (62, 13), (63, 13)], "3")
    p.px([(77, 14), (78, 14), (79, 15), (80, 15), (81, 16)], "3")
    p.px([(40, 20), (61, 19), (80, 19)], "2")
    p.px([(40, 19), (61, 18), (80, 18)], "6")
    # Grime and rust specks.
    p.px([(44, 9), (56, 17), (36, 21), (73, 10), (65, 21), (84, 17)], "3")
    p.px([(54, 20), (76, 20), (44, 27), (66, 28)], "r")
    parts.append(p)

    # Small top sensor dome, seated in the carapace.
    p = Part("dome")
    p.oval(55, 2, 63, 9, "3")
    p.clip_oval(56, 3, 61, 6, "4")
    p.px([(58, 4), (59, 4)], "5")
    p.px([(60, 5)], "y")
    p.rect(55, 7, 63, 8, "b")
    p.px([(56, 7), (57, 7)], "c")
    parts.append(p)

    # Far-side visor fin flaring forward above the eye.
    p = Part("far_fin")
    p.poly([(3, 12), (10, 5), (21, 6), (23, 10), (12, 13), (6, 18)], "3")
    p.rim("4", "2")
    p.px([(10, 8), (11, 8), (12, 8)], "1")
    parts.append(p)

    # Near rear leg: brass hip, raised knee, raked shin, toe-capped block foot.
    p = Part("near_rear_leg")
    p.poly([(64, 29), (70, 27), (86, 36), (81, 42)], "4")
    p.clip_poly([(64, 29), (70, 27), (86, 36), (84, 37), (68, 30)], "5")
    p.clip_poly([(84, 39), (86, 36), (86, 38), (81, 42)], "3")
    p.oval(61, 26, 69, 34, "c")
    p.clip_oval(61, 26, 67, 32, "d")
    p.oval(63, 28, 67, 32, "b")
    p.px([(64, 29)], "e")
    p.px([(65, 30)], "a")
    p.poly([(79, 41), (87, 41), (92, 54), (84, 54)], "4")
    p.clip_poly([(79, 41), (81, 41), (86, 54), (84, 54)], "5")
    p.clip_poly([(86, 41), (87, 41), (92, 54), (90, 54)], "3")
    p.clip_rect(80, 47, 90, 47, "3")
    p.oval(79, 35, 87, 43, "c")
    p.clip_oval(79, 35, 85, 41, "d")
    p.oval(81, 37, 85, 41, "b")
    p.px([(81, 36), (82, 36)], "e")
    p.px([(83, 39)], "a")
    p.rect(79, 55, 94, 59, "3")
    p.rect(79, 55, 94, 55, "4")
    p.rect(79, 59, 94, 59, "1")
    p.rect(89, 54, 94, 59, "c")
    p.rect(89, 54, 94, 54, "d")
    p.px([(89, 55)], "e")
    p.rect(89, 59, 94, 59, "b")
    p.px([(82, 59), (85, 59)], "2")
    parts.append(p)

    # Near front leg: thigh from under the eye housing, brass knee, forward-raked shin, toe-capped foot.
    p = Part("near_front_leg")
    p.poly([(30, 33), (36, 37), (19, 47), (15, 41)], "4")
    p.clip_poly([(30, 33), (32, 34), (16, 43), (15, 41)], "5")
    p.clip_poly([(35, 37), (36, 37), (19, 47), (18, 46)], "3")
    p.poly([(11, 45), (19, 45), (13, 54), (5, 54)], "4")
    p.clip_poly([(11, 45), (13, 45), (7, 54), (5, 54)], "5")
    p.clip_poly([(18, 45), (19, 45), (13, 54), (11, 54)], "3")
    p.clip_rect(6, 50, 17, 50, "3")
    p.oval(11, 39, 19, 47, "c")
    p.clip_oval(11, 39, 17, 45, "d")
    p.oval(13, 41, 17, 45, "b")
    p.px([(13, 40), (14, 40)], "e")
    p.px([(15, 43)], "a")
    p.rect(1, 55, 16, 59, "3")
    p.rect(1, 55, 16, 55, "4")
    p.rect(1, 59, 16, 59, "1")
    p.rect(1, 54, 6, 59, "c")
    p.rect(1, 54, 6, 54, "d")
    p.px([(1, 55), (2, 54)], "e")
    p.rect(1, 59, 6, 59, "b")
    p.px([(10, 59), (13, 59)], "2")
    parts.append(p)

    # Eye housing: octagonal dark frame under the bezel.
    p = Part("eye_housing")
    p.poly([(8, 17), (13, 10), (29, 9), (35, 15), (35, 32), (29, 38), (14, 38), (8, 32)], "2")
    p.rim("3", "1")
    p.rect(33, 20, 33, 25, "z")
    p.rect(34, 20, 34, 25, "x")
    p.px([(33, 20)], "w")
    parts.append(p)

    # Single large cyan eye in a brass bezel.
    p = Part("eye")
    p.oval(10, 12, 30, 32, "c")
    p.clip_poly([(30, 18), (30, 32), (16, 32)], "b")
    p.clip_poly([(10, 12), (23, 12), (10, 25)], "d")
    p.px([(14, 14), (15, 14), (13, 15), (12, 16)], "e")
    p.oval(13, 15, 27, 29, "a")
    p.oval(14, 16, 26, 28, "x")
    p.oval(15, 17, 25, 27, "y")
    p.oval(16, 18, 23, 25, "z")
    p.clip_poly([(25, 20), (25, 27), (18, 27)], "x")
    p.clip_poly([(25, 21), (25, 26), (20, 26)], "y")
    p.px([(17, 19), (18, 19), (17, 20)], "w")
    p.px([(19, 21), (20, 21), (19, 22), (20, 22)], "w")
    p.px([(23, 24), (22, 25)], "z")
    parts.append(p)

    # Near cheek plate behind the eye, slotted, with a brass rivet.
    p = Part("cheek_plate")
    p.poly([(34, 12), (40, 7), (47, 12), (47, 33), (41, 38), (34, 34)], "4")
    p.clip_poly([(34, 12), (40, 7), (47, 12), (40, 10), (36, 14)], "5")
    p.clip_poly([(44, 14), (47, 12), (47, 33), (44, 35)], "3")
    p.rim("6", "2")
    p.clip_rect(40, 16, 40, 27, "1")
    p.clip_rect(41, 16, 41, 27, "3")
    p.oval(38, 29, 42, 33, "c")
    p.px([(39, 30)], "e")
    p.px([(41, 32)], "b")
    p.px([(37, 22), (45, 18)], "3")
    parts.append(p)

    return parts


def composite(parts: list[Part]) -> Image.Image:
    grid = [[0] * W for _ in range(H)]
    for part in parts:
        src = part.layer.load()
        inside = {(x, y) for y in range(H) for x in range(W) if src[x, y]}
        for x, y in inside:
            for nx, ny in ((x + 1, y), (x - 1, y), (x, y + 1), (x, y - 1)):
                if 0 <= nx < W and 0 <= ny < H and (nx, ny) not in inside:
                    grid[ny][nx] = INDEX["o"]
        for x, y in inside:
            grid[y][x] = src[x, y]
    # Selective outline: soften exterior outline on lit top/left edges.
    soft = {}
    for y in range(H):
        for x in range(W):
            if grid[y][x] != INDEX["o"]:
                continue
            exterior = any(
                not (0 <= nx < W and 0 <= ny < H) or grid[ny][nx] == 0
                for nx, ny in ((x + 1, y), (x - 1, y), (x, y + 1), (x, y - 1))
            )
            if not exterior:
                continue
            for nx, ny in ((x + 1, y), (x, y + 1)):
                if 0 <= nx < W and 0 <= ny < H:
                    key = KEYS.get(grid[ny][nx])
                    if key in ("d", "e"):
                        soft[(x, y)] = "a"
                    elif key in ("5", "6"):
                        soft[(x, y)] = "1"
    for (x, y), key in soft.items():
        grid[y][x] = INDEX[key]
    img = Image.new("RGBA", SIZE, (0, 0, 0, 0))
    out = img.load()
    for y in range(H):
        for x in range(W):
            if grid[y][x]:
                h = PALETTE[KEYS[grid[y][x]]]
                out[x, y] = (int(h[1:3], 16), int(h[3:5], 16), int(h[5:7], 16), 255)
    return img


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", type=Path, default=None)
    ap.add_argument("--final", type=Path, default=None)
    args = ap.parse_args()
    img = composite(build_parts())
    bbox = img.getbbox()
    # Contact check: the anchor row is the last opaque row and both near feet touch it.
    assert bbox[3] - 1 == ANCHOR[1], bbox
    sole = [x for x in range(W) if img.getpixel((x, ANCHOR[1]))[3]]
    assert min(sole) <= 2 and max(sole) >= W - 3, (min(sole), max(sole))
    colours = sorted({c for c in img.getdata() if c[3]})
    if args.out:
        args.out.mkdir(parents=True, exist_ok=True)
        img.save(args.out / "pilot.png")
        bg = Image.new("RGBA", SIZE, (118, 122, 128, 255))
        bg.alpha_composite(img)
        bg.resize((W * 6, H * 6), Image.NEAREST).save(args.out / "pilot_6x.png")
        print("scratch", args.out, "bbox", bbox, "colours", len(colours))
        return
    out_dir: Path = args.final
    root = out_dir.resolve().parents[3]
    out_dir.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    token = uuid.uuid4().hex[:8]
    path = out_dir / f"{SLUG}_scifi-sentry-automaton_battle-idle-left_m8-pilot-v01_{stamp}-{token}.png"
    mpath = out_dir / f"{SLUG}_scifi-sentry-automaton_battle-pilot-manifest_m8-pilot-v01_{stamp}-{token}.json"
    assert not path.exists() and not mpath.exists()
    img.save(path)
    digest = hashlib.sha256(path.read_bytes()).hexdigest()
    alpha = sorted({c[3] for c in img.getdata()})
    script = Path(__file__).resolve()
    manifest = {
        "project": SLUG,
        "asset": "scifi sentry automaton battle sprite pilot (science-region ruins enemy)",
        "status": "pilot_unapproved",
        "artAccepted": False,
        "artAcceptanceCount": 0,
        "runtimeIntegrated": False,
        "file": str(path.resolve().relative_to(root)).replace("\\", "/"),
        "sha256": digest,
        "size": list(SIZE),
        "opaqueBBox": list(bbox),
        "groundAnchor": list(ANCHOR),
        "groundAnchorNote": "anchor row = near-foot sole outline row; draw at (enemy_x - 48, 272 - 60) so that row lands on ARENA_FLOOR_Y 272. Far feet end 2 px higher for depth.",
        "facing": "left (toward party)",
        "frames": ["idle (single static frame)"],
        "displayScale": "1 native px = 1 logical px in the 640x360 view = 2x2 physical px at 1280x720",
        "alphaValues": alpha,
        "colourCount": len(colours),
        "palette": PALETTE,
        "paletteNote": "identical ramps to the patrol pilot palette for regional coherence",
        "method": "Hand-authored in code: explicit plate polygons, joints, lens rings and grime pixels on the final native canvas, composited with per-part outline seams and a top/left selective outline. No concept image is read, traced, resampled or resized.",
        "authorScript": str(script.relative_to(root)).replace("\\", "/"),
        "authorScriptSha256": hashlib.sha256(script.read_bytes()).hexdigest(),
        "referenceConcepts": CONCEPTS,
        "referencePalette": PATROL_REF,
        "scope": "sentry enemy only; not wired into battle_arena.gd (another session owns it). In-game the sentry still draws the placeholder block.",
        "createdAt": datetime.now().isoformat(timespec="seconds"),
    }
    mpath.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    print(path)
    print(mpath)
    print("sha256", digest, "bbox", bbox, "colours", len(colours), "alpha", alpha)


if __name__ == "__main__":
    main()
