"""Build the 4x inspection sheet for the UNAPPROVED sentry automaton battle pilot.

Panels (all nearest-neighbour, 1 native/logical px = 4x4 px):
  A  native pilot PNG on neutral grey
  B  same pilot on a checkerboard (alpha check: only 0 / 255 expected)
  C  shared-baseline scale lineup: Liang Xu idle, patrol pilot, sentry pilot
  D  OFFLINE mock-up: pilot pasted at 2x onto an existing ruins-sentry Godot capture,
     anchor at logical (560, 272). Not a runtime render; the sentry is not wired into the game.
  +  palette strip
Usage: python -I <this> SENTRY_PNG
Writes a new uniquely named PNG to outputs/ and prints its path and SHA-256.
"""

from __future__ import annotations

import hashlib
import sys
import uuid
from datetime import datetime
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[4]
SLUG = "rpg-2-star-ocean-the-second"
LIANG = ROOT / "game/assets/characters/combat-prototypes/rpg-2-star-ocean-the-second_liang-xu_sideview-idle-right-phase-01_m8-prototype_20261014-143736-36cefff5.png"
PATROL = ROOT / "game/assets/enemies/patrol-automaton-pilot/rpg-2-star-ocean-the-second_scifi-patrol-automaton_battle-idle-left_m8-pilot-v01_20261014-220008-36512fae.png"
CAPTURE = ROOT / "outputs/rpg-2-star-ocean-the-second_scifi-battle-arena-candidate_ruins-sentry-en_m8-v01_20261014-213850-7980bec6.png"
LIANG_ANCHOR, PATROL_ANCHOR, SENTRY_ANCHOR = (30, 73), (29, 90), (48, 60)
MOCK_X = 560
GREY = (118, 122, 128, 255)
INK = (232, 236, 240, 255)
BG = (24, 28, 34, 255)


def x4(img: Image.Image) -> Image.Image:
    return img.resize((img.width * 4, img.height * 4), Image.NEAREST)


def on_grey(img: Image.Image) -> Image.Image:
    bg = Image.new("RGBA", img.size, GREY)
    bg.alpha_composite(img)
    return bg


def on_checker(img: Image.Image) -> Image.Image:
    bg = Image.new("RGBA", img.size)
    d = ImageDraw.Draw(bg)
    for y in range(0, img.height, 4):
        for x in range(0, img.width, 4):
            d.rectangle((x, y, x + 3, y + 3), fill=(200, 60, 200, 255) if (x // 4 + y // 4) % 2 else (60, 200, 90, 255))
    bg.alpha_composite(img)
    return bg


def lineup(sentry: Image.Image) -> Image.Image:
    base = 96
    panel = Image.new("RGBA", (262, 100), GREY)
    ImageDraw.Draw(panel).line((0, base + 1, 262, base + 1), fill=(90, 94, 100, 255))
    for img, anchor, x in ((Image.open(LIANG).convert("RGBA"), LIANG_ANCHOR, 34),
                           (Image.open(PATROL).convert("RGBA"), PATROL_ANCHOR, 104),
                           (sentry, SENTRY_ANCHOR, 196)):
        panel.alpha_composite(img, (x - anchor[0], base - anchor[1]))
    return panel


def mockup(sentry: Image.Image) -> Image.Image:
    shot = Image.open(CAPTURE).convert("RGBA")
    shot.alpha_composite(sentry.resize((sentry.width * 2, sentry.height * 2), Image.NEAREST),
                         ((MOCK_X - SENTRY_ANCHOR[0]) * 2, (272 - SENTRY_ANCHOR[1]) * 2))
    left, top = (MOCK_X - SENTRY_ANCHOR[0] - 12) * 2, (272 - SENTRY_ANCHOR[1] - 10) * 2
    crop = shot.crop((left, top, left + (96 + 24) * 2, top + (62 + 22) * 2))
    return crop.resize((crop.width * 2, crop.height * 2), Image.NEAREST)


def main() -> None:
    sentry_path = Path(sys.argv[1])
    sentry = Image.open(sentry_path).convert("RGBA")
    font = ImageFont.load_default(size=18)
    small = ImageFont.load_default(size=14)
    panels = [
        ("A  native 96x62, 4x, neutral grey", x4(on_grey(sentry))),
        ("B  alpha check on checkerboard (alpha values 0/255 only)", x4(on_checker(sentry))),
        ("C  shared baseline: Liang Xu idle / patrol pilot / sentry pilot", x4(lineup(sentry))),
        ("D  OFFLINE MOCK-UP on ruins capture, anchor (560, 272) - not a Godot render", mockup(sentry)),
    ]
    colours = sorted({p[:3] for p in sentry.getdata() if p[3]}, key=lambda p: sum(p))
    pad, head = 24, 30
    width = max(p.width for _, p in panels) + pad * 2
    rows = [(panels[0], panels[1]), (panels[2],), (panels[3],)]
    row_h = [max(p.height for _, p in r) + head + pad for r in rows]
    width = max(width, panels[0][1].width + panels[1][1].width + pad * 3)
    height = 60 + sum(row_h) + 80
    sheet = Image.new("RGBA", (width, height), BG)
    d = ImageDraw.Draw(sheet)
    d.text((pad, 16), "Sentry automaton battle pilot - UNAPPROVED, art acceptance 0, not runtime-integrated", font=font, fill=INK)
    y = 60
    for r, h in zip(rows, row_h):
        x = pad
        for label, img in r:
            d.text((x, y), label, font=small, fill=INK)
            sheet.alpha_composite(img, (x, y + head))
            x += img.width + pad
        y += h
    d.text((pad, y), f"palette ({len(colours)} colours, shared with patrol pilot)", font=small, fill=INK)
    for i, c in enumerate(colours):
        d.rectangle((pad + i * 36, y + 24, pad + i * 36 + 31, y + 55), fill=c + (255,))
    out = ROOT / "outputs" / f"{SLUG}_scifi-sentry-automaton-pilot_4x-inspection_m8-v01_{datetime.now():%Y%m%d-%H%M%S}-{uuid.uuid4().hex[:8]}.png"
    assert not out.exists()
    sheet.save(out)
    print(out.relative_to(ROOT))
    print("sha256", hashlib.sha256(out.read_bytes()).hexdigest(), "size", sheet.size)


if __name__ == "__main__":
    main()
