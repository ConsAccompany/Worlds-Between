"""Author three distinct, editable 64-pixel civic-archive clue fixtures."""

from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path
import json

ROOT = Path(__file__).resolve().parents[1]
source = ROOT / "tools/rpg-2-star-ocean-the-second_nyc-room2-pixel-fixtures-author_v01_20261017-010000-7d3c8a91.py"
spec = spec_from_file_location("room_fixture_layers", source)
art = module_from_spec(spec)
spec.loader.exec_module(art)
art.OUT = ROOT / "outputs/room1-fixtures-pilot"
art.OUT.mkdir(parents=True, exist_ok=True)
art.PREFIX = "rpg-2-star-ocean-the-second_nyc-public-facilities-room1"
art.STAMP = "20261017-011700-b45e18a9"
C = art.C


def usage_meter():
    shadow, d = art.layer()
    d.ellipse((6, 53, 58, 61), fill=C["shadow"])
    body, d = art.layer()
    art.rect(d, (12, 49, 52, 57), "deep", "ink")
    art.rect(d, (15, 18, 49, 51), "slate", "ink", 2)
    art.rect(d, (18, 21, 46, 43), "brass_dark", "brass")
    art.rect(d, (21, 24, 43, 39), "paper_dark", "ink")
    art.rect(d, (19, 45, 45, 48), "steel", "ink")
    art.rect(d, (20, 8, 44, 19), "deep", "ink")
    art.rect(d, (23, 11, 41, 16), "teal_dark", "brass")
    details, d = art.layer()
    # Three horizontal load channels and a moving pointer, unlike Room 2's round dial.
    for y, width in [(27, 15), (32, 21), (37, 11)]:
        art.line(d, [(24, y), (42, y)], "ink", 2)
        art.line(d, [(24, y), (24 + width, y)], "teal", 2)
    art.line(d, [(37, 24), (37, 40)], "brass_light")
    art.rect(d, (29, 12, 35, 14), "glow")
    for x in (18, 44):
        art.rect(d, (x, 46, x + 1, 47), "brass_light")
    art.rect(d, (28, 51, 36, 53), "brass")
    return [shadow, body, details]


def old_conduit():
    shadow, d = art.layer()
    d.ellipse((5, 54, 60, 61), fill=C["shadow"])
    body, d = art.layer()
    art.rect(d, (8, 48, 55, 57), "deep", "ink")
    art.rect(d, (12, 46, 52, 50), "steel", "ink")
    art.rect(d, (16, 12, 27, 48), "brass_dark", "ink", 2)
    art.rect(d, (38, 18, 49, 48), "brass_dark", "ink", 2)
    art.rect(d, (20, 18, 24, 44), "steel", "brass")
    art.rect(d, (42, 23, 46, 44), "steel", "brass")
    art.rect(d, (24, 10, 44, 22), "steel", "ink", 2)
    art.rect(d, (24, 11, 44, 14), "brass")
    art.rect(d, (28, 22, 37, 42), "ink", "brass_dark")
    details, d = art.layer()
    # Broken capped pipe, exposed teal flow and three diagnostic valves.
    art.line(d, [(30, 27), (35, 27), (35, 38)], "teal", 2)
    art.rect(d, (26, 24, 38, 27), "brass", "ink")
    for y in (29, 36, 43):
        art.rect(d, (12, y, 17, y + 3), "brass", "ink")
        art.rect(d, (47, y, 52, y + 3), "brass", "ink")
    art.line(d, [(31, 10), (35, 6), (39, 9)], "edge", 2)
    art.rect(d, (31, 6, 36, 8), "ink")
    art.rect(d, (27, 49, 38, 51), "glow")
    art.line(d, [(18, 16), (18, 20)], "brass_light")
    return [shadow, body, details]


def resident_notes():
    shadow, d = art.layer()
    d.ellipse((7, 55, 57, 61), fill=C["shadow"])
    body, d = art.layer()
    art.rect(d, (12, 50, 52, 57), "deep", "ink")
    art.rect(d, (27, 29, 37, 51), "slate", "ink")
    art.rect(d, (8, 10, 55, 39), "wood", "ink", 2)
    art.rect(d, (11, 13, 52, 35), "paper_dark", "brass_dark")
    art.rect(d, (9, 38, 54, 42), "wood_light", "ink")
    details, d = art.layer()
    # Layered resident postings, each with a separate wax or brass pin.
    art.rect(d, (13, 16, 26, 29), "paper", "ink")
    art.rect(d, (28, 14, 39, 31), "paper_light", "ink")
    art.rect(d, (41, 17, 51, 30), "paper", "ink")
    for x, y in ((18, 17), (33, 15), (46, 18)):
        art.rect(d, (x, y, x + 1, y + 1), "brass")
    for xy in ([(15, 22), (24, 22)], [(30, 22), (37, 22)], [(43, 23), (49, 23)]):
        art.line(d, xy, "wood")
    art.line(d, [(16, 25), (23, 25)], "wood")
    art.line(d, [(30, 26), (37, 26)], "wood")
    art.line(d, [(43, 26), (48, 26)], "wood")
    art.rect(d, (10, 39, 15, 40), "brass_light")
    art.rect(d, (48, 39, 53, 40), "brass_light")
    art.rect(d, (30, 43, 34, 45), "teal")
    return [shadow, body, details]


if __name__ == "__main__":
    items = [art.save_asset("usage-console", usage_meter()), art.save_asset("old-conduit", old_conduit()), art.save_asset("resident-notes-board", resident_notes())]
    name = f"{art.PREFIX}_three-pixel-fixtures-manifest_unapproved-v01_{art.STAMP}.json"
    path = art.OUT / name
    path.write_text(json.dumps({"assets": items, "source": str(Path(__file__).relative_to(ROOT))}, indent=2), encoding="utf-8")
    print(path)
