"""Author three small, layered NYC survey room fixtures at native game scale."""

from __future__ import annotations

from io import BytesIO
from pathlib import Path
import json
import xml.etree.ElementTree as ET
from zipfile import ZipFile, ZIP_STORED

from PIL import Image, ImageDraw


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "outputs" / "room2-fixtures-pilot"
OUT.mkdir(parents=True, exist_ok=True)
STAMP = "20261017-010000-7d3c8a91"
PREFIX = "rpg-2-star-ocean-the-second_nyc-public-facilities-room2"
W = H = 64

C = {
    "ink": "#151d21", "deep": "#263239", "slate": "#34434a",
    "steel": "#526269", "edge": "#839087", "shadow": "#141b1da8",
    "brass_dark": "#674927", "brass": "#a67b3d", "brass_light": "#d6af64",
    "paper_dark": "#a99b7e", "paper": "#d7c7a5", "paper_light": "#f0dfb8",
    "teal_dark": "#1b5c68", "teal": "#4fa5a2", "glow": "#8be9d7",
    "wood": "#514031", "wood_light": "#806247",
}


def layer():
    img = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    return img, ImageDraw.Draw(img)


def rect(draw, xy, fill, outline=None, width=1):
    draw.rectangle(xy, fill=C.get(fill, fill), outline=C.get(outline, outline), width=width)


def line(draw, xy, fill, width=1):
    draw.line(xy, fill=C.get(fill, fill), width=width)


def bench():
    contact, d = layer()
    d.ellipse((3, 49, 60, 59), fill=C["shadow"])
    body, d = layer()
    rect(d, (8, 33, 55, 45), "deep", "ink")
    rect(d, (10, 43, 15, 54), "slate", "ink")
    rect(d, (49, 43, 54, 54), "slate", "ink")
    rect(d, (17, 39, 47, 50), "steel", "ink")
    rect(d, (24, 42, 40, 48), "deep", "brass_dark")
    rect(d, (7, 27, 56, 37), "wood", "ink")
    rect(d, (9, 27, 54, 30), "wood_light")
    line(d, [(11, 31), (53, 31)], "brass_dark")
    line(d, [(12, 37), (51, 37)], "steel")
    rect(d, (8, 29, 10, 38), "brass_dark")
    rect(d, (53, 29, 55, 38), "brass")
    details, d = layer()
    # Open manual, with a broken spine and visible page stacks.
    d.polygon([(13, 17), (29, 19), (32, 21), (50, 18), (50, 33), (32, 36), (29, 34), (13, 32)], fill=C["ink"])
    d.polygon([(15, 19), (29, 21), (31, 23), (31, 33), (28, 32), (15, 30)], fill=C["paper"])
    d.polygon([(33, 23), (48, 20), (48, 30), (34, 33)], fill=C["paper_light"])
    line(d, [(32, 22), (32, 34)], "teal_dark", 2)
    line(d, [(17, 24), (27, 25)], "paper_dark")
    line(d, [(17, 27), (26, 28)], "paper_dark")
    rect(d, (38, 23, 42, 27), "brass", "brass_dark")
    line(d, [(36, 30), (45, 28)], "paper_dark")
    rect(d, (13, 36, 17, 38), "brass", "ink")
    rect(d, (47, 36, 51, 38), "brass", "ink")
    rect(d, (14, 40, 19, 42), "teal_dark")
    rect(d, (44, 40, 48, 42), "teal_dark")
    rect(d, (28, 44, 37, 45), "brass")
    for x, y in [(11, 33), (52, 33), (17, 47), (45, 47)]:
        rect(d, (x, y, x + 1, y + 1), "brass_light")
    line(d, [(19, 23), (25, 24)], "paper_light")
    line(d, [(38, 21), (44, 20)], "paper_light")
    rect(d, (20, 39, 22, 40), "glow")
    rect(d, (41, 39, 43, 40), "glow")
    return [contact, body, details]


def lectern():
    contact, d = layer()
    d.ellipse((10, 55, 55, 62), fill=C["shadow"])
    body, d = layer()
    rect(d, (23, 42, 40, 55), "deep", "ink")
    rect(d, (26, 27, 38, 52), "slate", "ink")
    rect(d, (28, 32, 35, 48), "teal_dark", "brass_dark")
    rect(d, (12, 54, 51, 59), "deep", "ink")
    rect(d, (16, 52, 47, 55), "steel", "ink")
    d.polygon([(9, 15), (52, 15), (57, 36), (8, 36)], fill=C["ink"])
    d.polygon([(12, 17), (49, 17), (53, 33), (11, 33)], fill=C["wood"])
    line(d, [(13, 18), (48, 18)], "wood_light")
    line(d, [(13, 31), (51, 31)], "brass_dark")
    line(d, [(11, 34), (53, 34)], "brass", 2)
    rect(d, (8, 32, 11, 38), "brass", "brass_dark")
    rect(d, (53, 32, 56, 38), "brass", "brass_dark")
    details, d = layer()
    # Upright closed log: clearly different from the bench's open pages.
    d.polygon([(19, 18), (40, 18), (43, 30), (20, 30)], fill=C["ink"])
    d.polygon([(20, 19), (39, 19), (42, 28), (21, 28)], fill=C["wood"])
    line(d, [(22, 21), (38, 21)], "brass")
    line(d, [(23, 26), (39, 26)], "brass_dark")
    rect(d, (24, 29, 42, 30), "paper_dark")
    rect(d, (37, 23, 43, 25), "brass", "ink")
    line(d, [(46, 19), (49, 30)], "brass_light", 2)
    rect(d, (45, 18, 47, 20), "brass_light")
    line(d, [(49, 30), (45, 32)], "teal")
    rect(d, (29, 38, 34, 45), "brass_dark")
    rect(d, (30, 39, 32, 43), "brass_light")
    rect(d, (17, 55, 21, 57), "brass")
    rect(d, (43, 55, 47, 57), "brass")
    line(d, [(25, 34), (39, 34)], "brass_light")
    rect(d, (28, 49, 37, 50), "steel")
    rect(d, (19, 23, 20, 26), "brass_dark")
    rect(d, (43, 25, 44, 28), "brass_dark")
    return [contact, body, details]


def meter():
    contact, d = layer()
    d.ellipse((8, 55, 57, 62), fill=C["shadow"])
    body, d = layer()
    rect(d, (11, 53, 53, 59), "deep", "ink")
    rect(d, (15, 50, 49, 54), "steel", "ink")
    rect(d, (18, 38, 25, 52), "slate", "ink")
    rect(d, (40, 38, 47, 52), "slate", "ink")
    rect(d, (15, 16, 50, 40), "deep", "ink")
    d.ellipse((14, 7, 51, 44), fill=C["ink"])
    d.ellipse((17, 10, 48, 41), fill=C["brass_dark"])
    d.ellipse((20, 13, 45, 38), fill=C["brass_light"])
    d.ellipse((23, 16, 42, 35), fill=C["paper"])
    d.arc((18, 11, 47, 40), 205, 285, fill=C["brass_light"], width=2)
    d.arc((19, 12, 46, 39), 20, 85, fill=C["brass"], width=2)
    details, d = layer()
    # Needle and edge graduations remain visible at 1:1 size.
    for x, y in [(25, 23), (27, 20), (31, 19), (35, 20), (39, 23)]:
        line(d, [(x, y), (x, y + 2)], "slate")
    line(d, [(32, 29), (39, 23)], "ink", 2)
    line(d, [(32, 29), (39, 23)], "teal")
    rect(d, (31, 28, 33, 30), "brass", "ink")
    rect(d, (11, 26, 15, 34), "teal_dark", "ink")
    rect(d, (12, 28, 14, 31), "glow")
    rect(d, (50, 26, 54, 34), "teal_dark", "ink")
    rect(d, (51, 28, 53, 31), "glow")
    for x, y in [(19, 17), (45, 17), (19, 38), (45, 38)]:
        rect(d, (x, y, x + 1, y + 1), "brass_light")
    rect(d, (13, 55, 17, 57), "brass")
    rect(d, (48, 55, 52, 57), "brass")
    rect(d, (21, 43, 22, 48), "steel")
    rect(d, (43, 43, 44, 48), "steel")
    line(d, [(26, 35), (39, 35)], "paper_dark")
    rect(d, (30, 14, 34, 15), "paper_light")
    return [contact, body, details]


def png_bytes(img):
    buf = BytesIO()
    img.save(buf, format="PNG")
    return buf.getvalue()


def save_asset(slug, layers):
    merged = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    for img in layers:
        merged.alpha_composite(img)
    stem = f"{PREFIX}_{slug}-pixel-fixture_unapproved-v01_{STAMP}"
    png = OUT / f"{stem}.png"
    ora = OUT / f"{stem}.ora"
    merged.save(png)

    root = ET.Element("image", {"w": str(W), "h": str(H), "name": slug, "version": "0.0.3"})
    stack = ET.SubElement(root, "stack")
    with ZipFile(ora, "w") as z:
        z.writestr("mimetype", "image/openraster", compress_type=ZIP_STORED)
        z.writestr("mergedimage.png", png_bytes(merged))
        for i, (name, img) in enumerate(zip(["contact-shadow", "structure", "identity-detail"], layers)):
            src = f"data/layer{i:02d}.png"
            z.writestr(src, png_bytes(img))
            ET.SubElement(stack, "layer", {"name": name, "src": src, "x": "0", "y": "0", "opacity": "1.0", "visibility": "visible", "composite-op": "svg:src-over"})
        z.writestr("stack.xml", ET.tostring(root, encoding="utf-8", xml_declaration=True))
    return {"purpose": slug, "png": str(png.relative_to(ROOT)), "ora": str(ora.relative_to(ROOT)), "size": [W, H], "layers": 3, "status": "unapproved; not integrated"}


if __name__ == "__main__":
    items = [save_asset("repair-manual-bench", bench()), save_asset("duty-log-lectern", lectern()), save_asset("analog-load-meter", meter())]
    path = OUT / f"{PREFIX}_three-pixel-fixtures-manifest_unapproved-v01_{STAMP}.json"
    path.write_text(json.dumps({"assets": items, "source": str(Path(__file__).relative_to(ROOT))}, indent=2), encoding="utf-8")
    print(path)
