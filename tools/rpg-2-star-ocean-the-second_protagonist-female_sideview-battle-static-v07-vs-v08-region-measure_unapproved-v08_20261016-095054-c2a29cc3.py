"""UNAPPROVED, test-only measurement: female side-view battle static v07 vs v08, per defect, in the real captures.

Reads only. For each version it imports the author tool (layer definitions only; main() is not run), finds which layer
is topmost at every opaque texel, and maps each texel to its 2x2 screen block in that version's 1280x720 Godot party
capture (texture origin 536, 408). Value separation per region = mean |dL| (Rec.709 luma) between the capture and the
no-sprite capture of the same arena, plus the share of pixels with |dL| < 20 (the v05-v07 QA metric). The no-sprite
frame is identical for v07 and v08 outside the sprite's own pixels (checked here), so one frame serves both.

Structural checks for the five defects the v07 game-scale audit names:
  sword      4-connected components of the visible light blade texels (edge light Z + steel M): 1 = one unbroken
             light core; more = dark outline steps cut the blade into segments
  hand_belt  rows of clearance between the lowest hand/hilt texel (glove, guard, grip) and the belt's top row, and
             hand/hilt texels 4-adjacent to belt texels
  hip        value separation of the jacket (coat torso), skirt, hip drape and the whole hip band (rows 38-52)
  back_gear  bedroll bounding box (w x h), ponytail/bedroll contacts, bedroll-scarf gap, teal texels at the back
  boots      sole-row footprint of each boot, gap between them, stance width, rear heel lift above the sole row

Usage:  python -I -B <this file> <no-sprite ruins png> <no-sprite outskirts png>
"""
import glob, importlib.util, json, os, sys
import numpy as np
from PIL import Image

REPO = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
ORIGIN = (536, 408)
SOLE_ROW, BELT_TOP = 67, 38
VERS = {
    "v07": ("*0p65-author_unapproved-v07_20261016-070549-0e2efcac.py", "unapproved-v07_20261016-070549"),
    "v08": ("*0p65-author_unapproved-v08_20261016-095054-326522f8.py", "unapproved-v08_20261016-095054"),
}
REGIONS = {
    "jacket (coat torso incl. belt)": ["coat"],
    "coat skirt": ["coat-skirt"],
    "hip drape (v08 only)": ["hip-drape"],
    "hip band (all layers, rows 38-52)": ["*@hip"],
    "far leg trouser (rows 42-57)": ["far-leg@trouser"],
    "boots (rows 57-67, both)": ["far-leg@boot", "near-leg@boot"],
    "back gear (pack + bedroll)": ["pack", "bedroll"],
    "teal (scarf + bedroll + drape)": ["scarf-neck", "bedroll", "hip-drape"],
    "sword (blade + guard)": ["sword-blade", "sword-guard"],
    "ponytail": ["ponytail"],
}


def load(tag):
    path = glob.glob(os.path.join(REPO, "tools", VERS[tag][0]))[0]
    spec = importlib.util.spec_from_file_location(f"author_{tag}", path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def lum(a):
    a = a.astype(float)
    return 0.2126 * a[..., 0] + 0.7152 * a[..., 1] + 0.0722 * a[..., 2]


def topmost(mod):
    owner, key = {}, {}
    for name, texels in mod.LAYERS:
        for x, y, ch in texels:
            owner[(x, y)] = name
            key[(x, y)] = ch
    return owner, key


def region_of(owner, spec):
    out = set()
    for s in spec:
        name, _, part = s.partition("@")
        for (x, y), n in owner.items():
            if name != "*" and n != name:
                continue
            if part == "trouser" and not 42 <= y <= 57:
                continue
            if part == "boot" and not 57 <= y <= 67:
                continue
            if part == "hip" and not 38 <= y <= 52:
                continue
            out.add((x, y))
    return out


def components(cells):
    cells, n = set(cells), 0
    while cells:
        n += 1
        stack = [cells.pop()]
        while stack:
            x, y = stack.pop()
            for q in ((x + 1, y), (x - 1, y), (x, y + 1), (x, y - 1)):
                if q in cells:
                    cells.remove(q)
                    stack.append(q)
    return n


def adjacent(a, b):
    return sum(1 for (x, y) in a if any((x + dx, y + dy) in b for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1))))


def cheb_gap(a, b):
    return min((max(abs(p[0] - q[0]), abs(p[1] - q[1])) for p in a for q in b), default=None)


def structure(tag, owner, key):
    vis = lambda n: {p for p, o in owner.items() if o == n}
    blade = {p for p in vis("sword-blade") if key[p] in "ZM"}
    if tag == "v07":    # v07: glove is the leather/tan part of the near-arm layer
        hand = {p for p in vis("near-arm") if key[p] in "BbLl"} | vis("sword-guard")
    else:
        hand = vis("fist") | vis("sword-guard")
    belt = {p for p in vis("coat") if p[1] >= BELT_TOP}
    roll, pony, scarf = vis("bedroll"), vis("ponytail"), vis("scarf-neck")
    roll_teal = {p for p in roll if key[p] in "QqgG"}
    scarf_teal = {p for p in scarf if key[p] in "QqgG"}
    rx, ry = [p[0] for p in roll], [p[1] for p in roll]
    boots = {}
    for leg in ("far-leg", "near-leg"):
        b = {p for p in vis(leg) if p[1] >= 57}
        sole = sorted(x for x, y in b if y == SOLE_ROW)
        xs = sorted({x for x, _ in b})
        heel_x = xs[0]
        boots[leg] = {"sole_row_columns": [sole[0], sole[-1]] if sole else None,
                      "x_extent": [xs[0], xs[-1]],
                      "heel_lift_rows": SOLE_ROW - max(y for x, y in b if x == heel_x)}
    gap = boots["near-leg"]["sole_row_columns"][0] - boots["far-leg"]["sole_row_columns"][1] - 1
    return {
        "sword_light_texels": len(blade),
        "sword_light_core_4connected_components": components(blade),
        "hand_hilt_lowest_row": max(y for _, y in hand),
        "hand_hilt_rows_clear_of_belt_top": BELT_TOP - max(y for _, y in hand) - 1,
        "hand_hilt_texels_4adjacent_to_belt": adjacent(hand, belt),
        "bedroll_bbox_w_x_h": [max(rx) - min(rx) + 1, max(ry) - min(ry) + 1],
        "bedroll_rows": [min(ry), max(ry)],
        "ponytail_texels_touching_bedroll": adjacent(pony, roll),
        "ponytail_to_bedroll_min_gap_texels": cheb_gap(pony, roll),
        "bedroll_teal_to_scarf_teal_min_gap_texels": cheb_gap(roll_teal, scarf_teal),
        "boots": boots,
        "sole_row_gap_between_boots_texels": gap,
        "stance_width_texels": boots["near-leg"]["x_extent"][1] - boots["far-leg"]["x_extent"][0] + 1,
        "leftmost_texel_x": min(x for x, _ in owner),
    }


def measure(owner, cap, bg):
    L, B = lum(cap[..., :3]), lum(bg[..., :3])
    out = {}
    for rname, spec in list(REGIONS.items()) + [("whole sprite", None)]:
        tex = set(owner) if spec is None else region_of(owner, spec)
        d = []
        for x, y in tex:
            sx, sy = ORIGIN[0] + 2 * x, ORIGIN[1] + 2 * y
            d.extend(np.abs(L[sy:sy + 2, sx:sx + 2] - B[sy:sy + 2, sx:sx + 2]).ravel())
        d = np.array(d)
        out[rname] = {"texels": len(tex), "mean_abs_dL": round(float(d.mean()), 1) if d.size else None,
                      "pct_under_20": round(100.0 * float((d < 20).mean()), 1) if d.size else None}
    return out


def main():
    bgs = {"ruins": np.array(Image.open(sys.argv[1]).convert("RGBA")),
           "outskirts": np.array(Image.open(sys.argv[2]).convert("RGBA"))}
    rep = {"status": "UNAPPROVED test-only measurement", "no_sprite_frames": sys.argv[1:3]}
    for tag in VERS:
        mod = load(tag)
        owner, key = topmost(mod)
        rep[tag] = {"structure": structure(tag, owner, key)}
        for arena, bg in bgs.items():
            pat = os.path.join(REPO, "outputs", f"*party-capture-{arena}_{VERS[tag][1]}-*.png")
            cap_path = glob.glob(pat)[0]
            cap = np.array(Image.open(cap_path).convert("RGBA"))
            diff = np.abs(cap[..., :3].astype(int) - bg[..., :3].astype(int)).sum(-1) > 0
            sprite = np.zeros(diff.shape, bool)
            for x, y in owner:
                sprite[ORIGIN[1] + 2 * y:ORIGIN[1] + 2 * y + 2, ORIGIN[0] + 2 * x:ORIGIN[0] + 2 * x + 2] = True
            rep[tag][arena] = {"capture": os.path.basename(cap_path),
                               "pixels_differing_from_no_sprite_outside_sprite": int((diff & ~sprite).sum()),
                               "regions": measure(owner, cap, bg)}
    print(json.dumps(rep, indent=1))


if __name__ == "__main__":
    main()
