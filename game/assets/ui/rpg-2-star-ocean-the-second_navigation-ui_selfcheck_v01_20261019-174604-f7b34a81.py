"""Bounded package + geometry self-check for the navigation UI skin helper v01 (no Godot).

Run from the repo root:  PYTHONUTF8=1 <bundled python> -I game/assets/ui/<this file>
Checks (read-only):
  1. the copied battle-skin-v01 manifest (sha256-text-lf-v1 pin used by the helper), its typed fields and all 11
     skins: raw PNG sha256-bytes, RGBA size, slices leaving a stretch centre, PXO/ORA files present with their hashes;
  2. the helper's constants equal the manifest (package id, sizes, slices, manifest pin) and its safety idioms;
  3. the existing scenes still build the chrome ColorRects, buttons and labels at the literal geometry the helper
     assumes (scifi_exploration_area.gd, survey_annex.gd, scifi_world_map.gd), and the helper's plate clearance rules
     replayed on that geometry for every layer, including the annex's widened English Back button and the map's
     commerce member buttons.
It does not parse GDScript or render anything; root performs the Godot/runtime checks (EN/ZH captures, input,
default parity, refresh/language survival).
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
HELPER = ROOT / "game/scripts/rpg-2-star-ocean-the-second_navigation-ui_skin-helper_v01_20261019-174604-f7b34a81.gd"
EXPLORE = ROOT / "game/scripts/scifi_exploration_area.gd"
ANNEX = ROOT / "game/scripts/survey_annex.gd"
MAP = ROOT / "game/scripts/scifi_world_map.gd"
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


# 1./2. package and helper constants
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
body = helper_text.split("func _init", 1)
check("constructor loads nothing", "load" not in re.search(r"func _init\(.*?\n\n\n", helper_text, re.S).group(0).replace("asset_dir", ""))
check("helper uses JSON.new().parse, not parse_string", "JSON.new()" in helper_text and "parse_string" not in helper_text)
check("typed hash guard (_is_sha256 + _is_whole + is_finite)", all(s in helper_text for s in ("func _is_sha256", "func _is_whole", "is_finite(number)")))
check("helper never writes package files", not re.search(r"FileAccess\.open\([^)]*WRITE|save_png|ResourceSaver", helper_text))
check("plates mouse IGNORE + focus NONE + nearest", all(s in helper_text for s in ("MOUSE_FILTER_IGNORE", "FOCUS_NONE", "TEXTURE_FILTER_NEAREST")))
check("mutation only after validation marker", helper_text.index("_collect_targets(screen)\n") < helper_text.index("# --- Mutation starts here") < helper_text.index("_add_plate(item)\n"))
check("helper never touches overlay colour/visibility/mouse_filter of scene nodes",
      not re.search(r"(overlay|parent|chrome)\.(color|visible|mouse_filter)\s*=", helper_text))
check("helper refuses pre-styled buttons", "has_theme_stylebox_override(state)" in helper_text)


# 3. scene literals the helper relies on
def literals(tag, path, items):
    src = path.read_text(encoding="utf-8")
    for literal in items:
        check(f"{tag} literal {literal[:52]}", literal in src)


literals("explore", EXPLORE, [
    'header.size = Vector2(640, 62)', 'footer.position = Vector2(0, 318)', 'footer.size = Vector2(640, 42)',
    'title_label.position = Vector2(18, 5)', 'hint_label.position = Vector2(18, 33)',
    'back_button.position = Vector2(525, 12)', 'back_button.size = Vector2(98, 38)',
    'save_button.position = Vector2(418, 12)', 'save_button.size = Vector2(98, 38)',
    'feedback_label.position = Vector2(18, 322)', 'help_label.position = Vector2(18, 340)',
    'dialogue_overlay.size = Vector2(640, 360)', 'panel.position = Vector2(87, 93)', 'panel.size = Vector2(466, 185)',
    'dialogue_title.position = Vector2(110, 109)', 'dialogue_text.position = Vector2(110, 143)',
    'dialogue_text.size = Vector2(419, 74)', 'invite_button.position = Vector2(110, 228)',
    'invite_button.size = Vector2(183, 35)', 'later_button.position = Vector2(331, 228)', 'later_button.size = Vector2(198, 35)',
])
literals("annex", ANNEX, [
    'header.size = Vector2(640, 62)', 'footer.position = Vector2(0, 318)', 'footer.size = Vector2(640, 42)',
    'title_label = _label(canvas, Vector2(18, 6)', 'progress_label = _label(canvas, Vector2(18, 34)',
    'save_button = _button(canvas, Vector2(418, 12), Vector2(98, 38)', 'back_button = _button(canvas, Vector2(525, 12), Vector2(98, 38)',
    'help_label = _label(canvas, Vector2(18, 327)', 'overlay.size = Vector2(640, 360)',
    'panel.position = Vector2(53, 41)', 'panel.size = Vector2(534, 278)', 'overlay_title = _label(overlay, Vector2(75, 58)',
    'overlay_body.position = Vector2(75, 95)', 'Vector2(75, 190 + index * 34), Vector2(488, 30)',
    'Vector2(75 + (index % 2) * 249, 155 + (index / 2) * 37), Vector2(239, 32)', 'Vector2(409, 56), Vector2(154, 29)',
    'Vector2(75, 275), Vector2(145, 32)', 'Vector2(232, 275), Vector2(145, 32)', 'Vector2(409, 275), Vector2(154, 32)',
    'save_button.position.x = 398.0 if wide else 418.0', 'back_button.position.x = 503.0 if wide else 525.0',
    'back_button.size.x = 125.0 if wide else 98.0',
])
literals("map", MAP, [
    'const MAP_RECT := Rect2(0, 44, 640, 268)', 'header.size = Vector2(640, MAP_RECT.position.y)',
    'title_label = _label(canvas, Vector2(12, 3)', 'help_label = _label(canvas, Vector2(12, 25)',
    'Rect2(296, 6, 100, 32), 12, _open_save', 'Rect2(402, 6, 118, 32), 11, _open_growth', 'Rect2(526, 6, 102, 32), 12, _return_to_menu',
    'strip.position = Vector2(0, 313)', 'strip.size = Vector2(640, 47)', 'field_status = _label(canvas, Vector2(17, 319)',
    'Rect2(521, 317, 103, 37), 0, _open_field_log', 'Rect2(412, 317, 103, 37), 0, open_commerce',
    'panel.position = Vector2(48, 39)', 'panel.size = Vector2(544, 285)', 'field_title.position = Vector2(69, 53)',
    'field_body.position = Vector2(69, 93)', 'talk_button.position = Vector2(69, 274)', 'talk_button.size = Vector2(155, 34)',
    'field_close.position = Vector2(434, 274)', 'field_close.size = Vector2(135, 34)',
    'panel.position = Vector2(72, 62)', 'panel.size = Vector2(496, 236)', 'credits_title.position = Vector2(90, 72)',
    'credits_body.position = Vector2(90, 98)', 'Rect2(432, 256, 120, 30), 11, close_map_credits',
    'commerce_title.position = Vector2(69, 49)', 'commerce_body.position = Vector2(69, 78)',
    'Rect2(69 + index * 169, 228, 163, 30)', 'Rect2(69, 266, 150, 34), 11, _commerce_recall',
    'Rect2(227, 266, 200, 34), 11, _commerce_rest', 'Rect2(435, 266, 136, 34), 11, close_commerce',
    'for index in AppState.MEMBER_DEFS.size() - 1:',
])
app_src = (ROOT / "game/scripts/app_state.gd").read_text(encoding="utf-8")
member_block = app_src.split("const MEMBER_DEFS := {", 1)[1].split("\n}", 1)[0]
member_count = len(re.findall(r'^\t"[a-z-]+": \{', member_block, re.M))
check("MEMBER_DEFS count read", member_count >= 2, str(member_count))
# The route card and map frame keep their native science chrome; the helper must not name them as targets
# (route_card is read once, only as a kind-detection ref in _collect_targets).
detect = re.search(r"func _collect_targets.*?\n\n\n", helper_text, re.S).group(0)
check("route_card used only for kind detection", helper_text.count('"route_card"') == detect.count('"route_card"') == 1)
for untouched in ("depart_button", "cancel_button", "zoom_in_button", "globe_button", "relief_credit_button", "legend_backing", "map_frame"):
    check(f"map native chrome untouched: {untouched}", re.search(r'"%s"' % untouched, helper_text) is None)


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


allowance = float(re.search(r"LABEL_TOP_ALLOWANCE := ([\d.]+)", helper_text).group(1))
check("label top allowance is at most 1 px", allowance <= 1.0, str(allowance))


def clear(tag, plate, buttons, labels):
    ok = encloses((0, 0, 640, 360), plate)
    i = inner(plate)
    label_inner = (i[0], i[1] - allowance, i[2], i[3] + allowance)
    bad = [b for b in buttons if intersects(plate, b) and not encloses(i, b)]
    bad += [p for p in labels if has_point(plate, p) and not has_point(label_inner, p)]
    gaps = [min(b[1] - i[1], i[1] + i[3] - b[1] - b[3], b[0] - i[0], i[0] + i[2] - b[0] - b[2]) for b in buttons if intersects(plate, b)]
    check(f"clearance {tag}", ok and not bad, f"min inner gap {min(gaps) if gaps else 'n/a'} px; bad {bad}")


# exploration
ex_bar_buttons = [(525, 12, 98, 38), (418, 12, 98, 38)]
ex_bar_labels = [(18, 5), (18, 33), (18, 322), (18, 340)]
clear("explore header", rect_const("EXPLORE_HEADER_RECT"), ex_bar_buttons, ex_bar_labels)
clear("explore footer", rect_const("EXPLORE_FOOTER_RECT"), ex_bar_buttons, ex_bar_labels)
clear("explore dialogue panel", rect_const("EXPLORE_DIALOGUE_RECT"), [(110, 228, 183, 35), (331, 228, 198, 35)], [(110, 109), (110, 143)])
check("explore dialogue text box inside panel inner", encloses(inner(rect_const("EXPLORE_DIALOGUE_RECT")), (110, 143, 419, 74)))
# annex (both Back widths: zh/default 98 px at 525, Yonkers en 125 px at 503 with Save at 398)
an_labels = [(18, 6), (18, 34), (18, 327)]
for tag, buttons in (("default", [(418, 12, 98, 38), (525, 12, 98, 38)]), ("yonkers-en", [(398, 12, 98, 38), (503, 12, 125, 38)])):
    clear(f"annex header [{tag}]", rect_const("ANNEX_HEADER_RECT"), buttons, an_labels)
    clear(f"annex footer [{tag}]", rect_const("ANNEX_FOOTER_RECT"), buttons, an_labels)
an_overlay_buttons = [(75, 190 + i * 34, 488, 30) for i in range(3)] + [(75 + (i % 2) * 249, 155 + (i // 2) * 37, 239, 32) for i in range(6)] + \
    [(409, 56, 154, 29), (75, 275, 145, 32), (232, 275, 145, 32), (409, 275, 154, 32)]
clear("annex investigation panel", rect_const("ANNEX_OVERLAY_RECT"), an_overlay_buttons, [(75, 58), (75, 95)])
for h in (50, 92, 151):
    check(f"annex overlay_body h{h} inside panel inner", encloses(inner(rect_const("ANNEX_OVERLAY_RECT")), (75, 95, 488, h)))
# map
mp_bar_buttons = [(296, 6, 100, 32), (402, 6, 118, 32), (526, 6, 102, 32), (521, 317, 103, 37), (412, 317, 103, 37)]
mp_bar_labels = [(12, 3), (12, 25), (17, 319)]
clear("map header", rect_const("MAP_HEADER_RECT"), mp_bar_buttons, mp_bar_labels)
clear("map strip", rect_const("MAP_STRIP_RECT"), mp_bar_buttons, mp_bar_labels)
check("map header plate stays above the map frame", rect_const("MAP_HEADER_RECT")[3] <= 44)
check("map strip plate stays below the map frame", rect_const("MAP_STRIP_RECT")[1] >= 44 + 268 and rect_const("MAP_STRIP_RECT")[1] + rect_const("MAP_STRIP_RECT")[3] == 360)
clear("map field log panel", rect_const("MAP_FIELD_RECT"), [(69, 274, 155, 34), (434, 274, 135, 34)], [(69, 53), (69, 93)])
commerce_buttons = [(69 + i * 169, 228, 163, 30) for i in range(member_count - 1)] + [(69, 266, 150, 34), (227, 266, 200, 34), (435, 266, 136, 34)]
clear(f"map commerce panel ({member_count - 1} member buttons)", rect_const("MAP_COMMERCE_RECT"), commerce_buttons, [(69, 49), (69, 78)])
clear("map credits panel", rect_const("MAP_CREDITS_RECT"), [(432, 256, 120, 30)], [(90, 72), (90, 98)])

failed = [r for r in results if not r[1]]
for name, ok, detail in results:
    if not ok or detail:
        print(("PASS " if ok else "FAIL ") + name + (" :: " + detail if detail else ""))
print(f"NAVIGATION_UI_SELFCHECK checks {len(results)} fails {len(failed)} {'PASS' if not failed else 'FAIL'}")
sys.exit(1 if failed else 0)
