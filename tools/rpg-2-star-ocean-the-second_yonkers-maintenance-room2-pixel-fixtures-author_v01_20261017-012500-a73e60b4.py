"""Three distinct native-pixel investigation fixtures for Yonkers maintenance room 2."""

from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path
import json

ROOT = Path(__file__).resolve().parents[1]
source = ROOT / "tools/rpg-2-star-ocean-the-second_nyc-room2-pixel-fixtures-author_v01_20261017-010000-7d3c8a91.py"
spec = spec_from_file_location("room_fixture_layers", source)
art = module_from_spec(spec)
spec.loader.exec_module(art)
art.OUT = ROOT / "outputs/yonkers-room2-fixtures-pilot"
art.OUT.mkdir(parents=True, exist_ok=True)
art.PREFIX = "rpg-2-star-ocean-the-second_yonkers-maintenance-room2"
art.STAMP = "20261017-012500-a73e60b4"
art.C.update({"slate": "#34454a", "steel": "#577478", "edge": "#9cb7ab", "brass": "#8f835a", "brass_light": "#c6bd8c", "teal": "#55a4a1", "glow": "#9ddbc8"})
C = art.C


def line_checker():
    shadow, d = art.layer()
    d.ellipse((7, 52, 57, 61), fill=C["shadow"])
    body, d = art.layer()
    art.line(d, [(31, 32), (13, 55)], "ink", 5)
    art.line(d, [(33, 32), (51, 55)], "ink", 5)
    art.line(d, [(31, 32), (13, 55)], "steel", 2)
    art.line(d, [(33, 32), (51, 55)], "steel", 2)
    art.rect(d, (12, 53, 21, 56), "steel", "ink")
    art.rect(d, (44, 53, 53, 56), "steel", "ink")
    art.rect(d, (14, 14, 50, 36), "slate", "ink", 2)
    art.rect(d, (18, 17, 46, 30), "teal_dark", "brass_dark")
    art.rect(d, (17, 35, 47, 39), "steel", "ink")
    details, d = art.layer()
    # Pulse line and hanging inspection lead give the station its purpose.
    art.line(d, [(20, 25), (25, 25), (27, 20), (30, 27), (34, 22), (38, 25), (44, 25)], "glow", 2)
    art.rect(d, (18, 32, 24, 34), "brass")
    art.rect(d, (37, 32, 43, 34), "brass")
    art.line(d, [(47, 34), (54, 42), (51, 51)], "ink", 2)
    art.rect(d, (48, 48, 53, 52), "brass_light", "ink")
    art.rect(d, (29, 40, 35, 42), "glow")
    return [shadow, body, details]


def patrol_log():
    shadow, d = art.layer()
    d.ellipse((9, 54, 55, 61), fill=C["shadow"])
    body, d = art.layer()
    art.rect(d, (11, 49, 53, 57), "deep", "ink")
    art.rect(d, (21, 32, 43, 51), "slate", "ink")
    art.rect(d, (13, 10, 51, 36), "steel", "ink", 2)
    art.rect(d, (16, 13, 48, 30), "teal_dark", "ink")
    art.rect(d, (19, 37, 45, 42), "deep", "ink")
    details, d = art.layer()
    for y, width in [(17, 17), (21, 24), (25, 13)]:
        art.line(d, [(20, y), (20 + width, y)], "glow")
    art.rect(d, (43, 16, 46, 18), "brass_light")
    art.rect(d, (42, 26, 46, 28), "brass")
    art.rect(d, (23, 43, 41, 48), "paper_dark", "ink")
    art.line(d, [(25, 45), (37, 45)], "wood")
    art.rect(d, (16, 52, 22, 54), "brass")
    art.rect(d, (42, 52, 48, 54), "brass")
    return [shadow, body, details]


def battery_log():
    shadow, d = art.layer()
    d.ellipse((6, 52, 59, 61), fill=C["shadow"])
    body, d = art.layer()
    art.rect(d, (7, 45, 56, 57), "deep", "ink", 2)
    art.rect(d, (9, 36, 54, 49), "slate", "ink")
    for x in (12, 27, 42):
        art.rect(d, (x, 14, x + 10, 41), "steel", "ink", 2)
        art.rect(d, (x + 2, 18, x + 8, 33), "teal_dark", "brass_dark")
        art.rect(d, (x + 4, 9, x + 6, 13), "brass", "ink")
    details, d = art.layer()
    for x, height in [(12, 7), (27, 12), (42, 10)]:
        art.rect(d, (x + 3, 33 - height, x + 7, 32), "teal")
    art.rect(d, (16, 48, 48, 52), "brass_dark", "ink")
    for x in (20, 28, 36, 44):
        art.rect(d, (x, 49, x + 1, 50), "glow")
    art.line(d, [(13, 43), (50, 43)], "edge")
    return [shadow, body, details]


def analysis_console():
    shadow, d = art.layer()
    d.ellipse((5, 52, 59, 61), fill=C["shadow"])
    body, d = art.layer()
    art.rect(d, (7, 48, 56, 56), "deep", "ink")
    art.rect(d, (12, 22, 52, 49), "slate", "ink", 2)
    art.rect(d, (17, 26, 47, 37), "teal_dark", "brass_dark")
    d.polygon([(13, 38), (51, 38), (57, 47), (8, 47)], fill=C["steel"], outline=C["ink"])
    details, d = art.layer()
    art.line(d, [(19, 32), (26, 32), (29, 29), (35, 34), (45, 29)], "glow", 2)
    for x in (19, 26, 33, 40):
        art.rect(d, (x, 41, x + 4, 42), "brass_light")
    art.rect(d, (27, 51, 37, 53), "teal")
    art.rect(d, (12, 48, 16, 50), "brass_dark")
    art.rect(d, (48, 48, 52, 50), "brass_dark")
    return [shadow, body, details]


if __name__ == "__main__":
    items = [art.save_asset("line-checker", line_checker()), art.save_asset("patrol-log-terminal", patrol_log()), art.save_asset("battery-log-rack", battery_log()), art.save_asset("analysis-console", analysis_console())]
    path = art.OUT / f"{art.PREFIX}_four-pixel-fixtures-manifest_unapproved-v01_{art.STAMP}.json"
    path.write_text(json.dumps({"assets": items, "source": str(Path(__file__).relative_to(ROOT))}, indent=2), encoding="utf-8")
    print(path)
