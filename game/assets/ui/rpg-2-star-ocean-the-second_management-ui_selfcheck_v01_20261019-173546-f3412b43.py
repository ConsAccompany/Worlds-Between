"""Bounded package + geometry self-check for the management UI skin helper v01 (no Godot).

Run from the repo root:  PYTHONUTF8=1 <bundled python> -I game/assets/ui/<this file>
Checks (read-only):
  1. the copied battle-skin-v01 manifest (sha256-text-lf-v1 pin used by the helper), its typed fields and all 11
     skins: raw PNG sha256-bytes, RGBA size, slices leaving a stretch centre, PXO/ORA files present with their hashes;
  2. the helper's constants equal the manifest (package id, sizes, slices, manifest pin);
  3. the plate clearance rules from the helper, replayed on the literal geometry of growth_screen.gd / save_screen.gd
     (both save modes, both growth layers), including that the screens' geometry literals are still the ones assumed.
It does not parse GDScript or render anything; root performs the Godot/runtime checks.
"""
import hashlib
import json
import pathlib
import re
import sys

from PIL import Image

ROOT = pathlib.Path(__file__).resolve().parents[3]
PKG = ROOT / "game/assets/ui/battle-skin-v01"
MANIFEST = PKG / "rpg-2-star-ocean-the-second_battle-ui_asset-manifest_skin-v01_20261019-171056-ca4652ec.json"
HELPER = ROOT / "game/scripts/rpg-2-star-ocean-the-second_management-ui_skin-helper_v01_20261019-173546-f3412b43.gd"
GROWTH = ROOT / "game/scripts/growth_screen.gd"
SAVE = ROOT / "game/scripts/save_screen.gd"
REQUIRED = {
    "hud-band": ((24, 24), (4, 4, 4, 4)), "panel": ((24, 24), (4, 4, 4, 4)),
    "button-normal": ((16, 16), (4, 4, 4, 4)), "button-hover": ((16, 16), (4, 4, 4, 4)),
    "button-pressed": ((16, 16), (4, 4, 4, 4)), "button-disabled": ((16, 16), (4, 4, 4, 4)),
    "button-focus": ((16, 16), (4, 4, 4, 4)), "bar-trough": ((16, 16), (4, 4, 4, 4)),
    "bar-fill-health": ((16, 16), (2, 4, 2, 4)), "bar-fill-energy": ((16, 16), (2, 4, 2, 4)),
    "bar-fill-enemy": ((16, 16), (2, 4, 2, 4)),
}
results = []


def check(name, ok, detail=""):
    results.append((name, bool(ok), detail))


def sha_bytes(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def sha_text_lf(path):
    return hashlib.sha256(path.read_bytes().replace(b"\r\n", b"\n")).hexdigest()


def whole(v):
    return isinstance(v, (int, float)) and not isinstance(v, bool) and float(v) == int(v)


# 1. package
helper_text = HELPER.read_text(encoding="utf-8")
pin = re.search(r'MANIFEST_SHA256_TEXT_LF := "([0-9a-f]{64})"', helper_text).group(1)
check("manifest sha256-text-lf-v1 equals helper pin", sha_text_lf(MANIFEST) == pin, pin)
m = json.loads(MANIFEST.read_text(encoding="utf-8"))
check("schemaVersion 1", whole(m.get("schemaVersion")) and m["schemaVersion"] == 1)
check("packageId", m.get("packageId") == re.search(r'PACKAGE_ID := "([^"]+)"', helper_text).group(1))
check("filter nearest", m.get("filter") == "nearest")
check("skinOrder is the 11 required keys", sorted(m.get("skinOrder", [])) == sorted(REQUIRED) and len(set(m["skinOrder"])) == 11)
for key, (size, sl) in REQUIRED.items():
    e = m["skins"][key]
    check(f"{key} size field", list(e["size"]) == list(size) and all(whole(v) for v in e["size"]))
    got = tuple(e["slices"][s] for s in ("left", "top", "right", "bottom"))
    check(f"{key} slices field", got == sl and all(whole(v) and v >= 1 for v in got) and len(e["slices"]) == 4)
    check(f"{key} slice bounds leave centre", sl[0] + sl[2] < size[0] and sl[1] + sl[3] < size[1])
    for field in ("png", "pxo", "ora"):
        p = PKG / e[field]
        ok = "/" not in e[field] and "\\" not in e[field] and p.is_file() and sha_bytes(p) == e["sha256"][e[field]]
        check(f"{key} {field} present + sha256-bytes", ok)
    im = Image.open(PKG / e["png"])
    check(f"{key} png RGBA {size}", im.mode == "RGBA" and im.size == tuple(size), f"{im.mode} {im.size}")
    hp = re.search(r'"%s": \[Vector2i\((\d+), (\d+)\), \[(\d+), (\d+), (\d+), (\d+)\]\]' % re.escape(key), helper_text)
    check(f"{key} helper REQUIRED matches", hp and tuple(map(int, hp.groups())) == tuple(size) + sl)
for name in ("font_color", "font_hover_color", "font_pressed_color", "font_hover_pressed_color", "font_focus_color", "font_disabled_color"):
    v = m["fontColors"].get(name)
    check(f"fontColors.{name}", isinstance(v, str) and re.fullmatch(r"#[0-9a-fA-F]{6}", v) is not None)
check("helper uses JSON.new().parse, not parse_string", "JSON.new()" in helper_text and "parse_string" not in helper_text)
check("helper never writes package files", not re.search(r"FileAccess\.open\([^)]*WRITE|save_png|ResourceSaver", helper_text))
check("plates mouse IGNORE + focus NONE", "MOUSE_FILTER_IGNORE" in helper_text and "FOCUS_NONE" in helper_text)

# 2./3. geometry replay (literal geometry from the existing screens, asserted against their source)
g_src = GROWTH.read_text(encoding="utf-8")
s_src = SAVE.read_text(encoding="utf-8")
for literal in ["_button(Vector2(500, 8), Vector2(121, 31), _leave)", "Vector2(18 + index * 124, 47), Vector2(117, 29)",
                "Vector2(20 + stage * 151, 225), Vector2(146, 31)", "Vector2(329, 225), Vector2(141, 31)",
                "Vector2(478, 225), Vector2(143, 31)", "Vector2(20 + index * 122, 279), Vector2(116, 41)",
                "Vector2(20, 324), Vector2(300, 29)", "Vector2(329, 324), Vector2(141, 29)",
                "Vector2(500, 8), Vector2(121, 31), _show_nodes.bind(false), node_panel",
                "Vector2(20 + (index / 2) * 122, 62 + (index % 2) * 37)", "Vector2(20 + (index % 5) * 122, 158 + (index / 5) * 37)",
                "_button(at, Vector2(116, 33), callback, node_panel)", "_label(Vector2(20, 44), 11"]:
    check(f"growth literal {literal[:40]}", literal in g_src)
for literal in ["_button(Vector2(530, 7), Vector2(92, 31), _back)", "var y := 46 + index * 37", "_row(Vector2(16, y - 2), Vector2(608, 34))",
                "_label(Vector2(24, y + 5), 11", "Vector2(433, y + 1), Vector2(90, 27)", "Vector2(529, y + 1), Vector2(88, 27)",
                "var y := 181 + index * 31", "_row(Vector2(16, y - 2), Vector2(608, 29))", "_label(Vector2(24, y + 4), 10",
                "Vector2(529, y), Vector2(88, 25)", "_label(Vector2(20, 160), 14", "_label(Vector2(20, 340), 10"]:
    check(f"save literal {literal[:40]}", literal in s_src)


def rect_const(name):
    v = re.search(name + r" := Rect2\(([\d., ]+)\)", helper_text).group(1)
    return tuple(float(x) for x in v.split(","))


def intersects(a, b):
    return a[0] < b[0] + b[2] and b[0] < a[0] + a[2] and a[1] < b[1] + b[3] and b[1] < a[1] + a[3]


def encloses(outer, r):
    return outer[0] <= r[0] and outer[1] <= r[1] and r[0] + r[2] <= outer[0] + outer[2] and r[1] + r[3] <= outer[1] + outer[3]


def inner(r, s=4):
    return (r[0] + s, r[1] + s, r[2] - 2 * s, r[3] - 2 * s)


def has_point(r, p):
    return r[0] <= p[0] < r[0] + r[2] and r[1] <= p[1] < r[1] + r[3]


def clear(tag, plate, buttons, labels):
    ok = encloses((0, 0, 640, 360), plate)
    bad = [b for b in buttons if intersects(plate, b) and not encloses(inner(plate), b)]
    bad += [p for p in labels if has_point(plate, p) and not has_point(inner(plate), p)]
    gaps = [min(b[1] - inner(plate)[1], inner(plate)[1] + inner(plate)[3] - b[1] - b[3], b[0] - inner(plate)[0],
                inner(plate)[0] + inner(plate)[2] - b[0] - b[2]) for b in buttons if intersects(plate, b)]
    check(f"clearance {tag}", ok and not bad, f"min inner gap {min(gaps) if gaps else 'n/a'} px; bad {bad}")


growth_main_buttons = [(500, 8, 121, 31)] + [(18 + i * 124, 47, 117, 29) for i in range(5)] + \
    [(20 + s * 151, 225, 146, 31) for s in range(2)] + [(329, 225, 141, 31), (478, 225, 143, 31)] + \
    [(20 + i * 122, 279, 116, 41) for i in range(5)] + [(20, 324, 300, 29), (329, 324, 141, 29)]
growth_main_labels = [(20, 10), (21, 91), (21, 121), (21, 148), (21, 174), (21, 201)]
node_buttons = [(500, 8, 121, 31)] + [(20 + (i // 2) * 122, 62 + (i % 2) * 37, 116, 33) for i in range(10)] + \
    [(20 + (i % 5) * 122, 158 + (i // 5) * 37, 116, 33) for i in range(10)]
node_labels = [(20, 10), (20, 44), (20, 140), (20, 236)]
groups = re.search(r"GROWTH_GROUP_RECTS := \[Rect2\(([\d, ]+)\), Rect2\(([\d, ]+)\)\]", helper_text).groups()
growth_plates = [rect_const("GROWTH_HEADER_RECT")] + [tuple(float(x) for x in g.split(",")) for g in groups]
for i, p in enumerate(growth_plates):
    clear(f"growth main plate {i} {p}", p, growth_main_buttons, growth_main_labels)
clear("growth node header", rect_const("NODE_HEADER_RECT"), node_buttons, node_labels)
check("growth plates do not overlap each other", not any(intersects(a, b) for i, a in enumerate(growth_plates) for b in growth_plates[i + 1:]))

save_header = rect_const("SAVE_HEADER_RECT")
for mode in ("save", "load"):
    rows, buttons, labels = [], [(530, 7, 92, 31)], [(20, 8), (20, 160), (20, 340)]
    for i in range(3):
        y = 46 + i * 37
        row_buttons = ([(433, y + 1, 90, 27)] if mode == "save" else []) + [(529, y + 1, 88, 27)]
        rows.append(((16, y - 2, 608, 34), row_buttons, (24, y + 5)))
    for i in range(5):
        y = 181 + i * 31
        rows.append(((16, y - 2, 608, 29), [(529, y, 88, 25)], (24, y + 4)))
    for r in rows:
        buttons += r[1]
        labels.append(r[2])
    clear(f"save[{mode}] header", save_header, buttons, labels)
    check(f"save[{mode}] header clears rows", not any(intersects(save_header, r[0]) for r in rows))
    for i, (row, row_buttons, _) in enumerate(rows):
        right = min([row[0] + row[2]] + [b[0] - 4 for b in row_buttons])
        cell = (row[0], row[1], right - row[0], row[3])
        clear(f"save[{mode}] row {i} cell w{cell[2]:.0f}", cell, buttons, labels)

failed = [r for r in results if not r[1]]
for name, ok, detail in results:
    if not ok or detail:
        print(("PASS " if ok else "FAIL ") + name + (" :: " + detail if detail else ""))
print(f"MANAGEMENT_UI_SELFCHECK checks {len(results)} fails {len(failed)} {'PASS' if not failed else 'FAIL'}")
sys.exit(1 if failed else 0)
