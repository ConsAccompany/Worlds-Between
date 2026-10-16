"""UNAPPROVED, test-only measurement: female side-view battle static v08 vs v09, per audited issue, in the real captures.

Reads only. Same method as the v07-vs-v08 measure: for each version it imports the author tool (layer definitions only;
main() is not run), finds which layer is topmost at every opaque texel, and maps each texel to its 2x2 screen block in
that version's 1280x720 Godot party capture (texture origin 536, 408). Value separation per region = mean |dL| (Rec.709
luma) between the capture and the no-sprite capture of the same arena, plus the share of pixels with |dL| < 20. The
no-sprite frame is identical for v08 and v09 outside the sprite's own pixels (checked here), so one frame serves both.

Structural checks for the three issues the Codex v08 visual audit (5e1b7d6c) names:
  legs       visible texels of the far leg and near leg (a drape must not cover the stance), far-leg trouser and boot
             value separation, boot texels standing in the contact shadow (rows 62-65)
  roll       roll bbox, transparent columns between the roll and the next opaque texel to its right per row, roll teal to
             scarf teal Chebyshev gap, roll texels 4-adjacent to coat/scarf/collar texels
  drape      visible drape texels, max width per row, lowest row, drape texels 4-adjacent to visible far-leg texels
Kept-fix checks (v08 fixes that v09 must not lose): sword light core components, hand/hilt clearance above the belt.

Usage:  python -I -B <this file> <no-sprite ruins png> <no-sprite outskirts png>
"""
import glob, importlib.util, json, os, sys
import numpy as np
from PIL import Image

REPO = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
ORIGIN = (536, 408)
SOLE_ROW, BELT_TOP = 67, 38
VERS = {
    "v08": ("*0p65-author_unapproved-v08_20261016-095054-326522f8.py", "unapproved-v08_20261016-095054"),
    "v09": ("*0p65-author_unapproved-v09_20261016-135202-43cf7e01.py", "unapproved-v09_20261016-135202"),
}
REGIONS = {
    "far leg trouser (rows 42-57, visible part)": ["far-leg@trouser"],
    "far boot (rows 58-67)": ["far-leg@boot"],
    "near boot (rows 58-67)": ["near-leg@boot"],
    "both boots, contact-shadow rows 62-65": ["far-leg@shadow", "near-leg@shadow"],
    "hip drape": ["hip-drape"],
    "coat skirt (visible part)": ["coat-skirt"],
    "hip band (all layers, rows 38-54)": ["*@hip"],
    "bedroll": ["bedroll"],
    "back gear (pack + bedroll)": ["pack", "bedroll"],
    "teal (scarf + bedroll + drape)": ["scarf-neck", "bedroll", "hip-drape"],
    "sword (blade + guard)": ["sword-blade", "sword-guard"],
    "jacket (coat torso incl. belt)": ["coat"],
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
            if part == "boot" and not 58 <= y <= 67:
                continue
            if part == "shadow" and not 62 <= y <= 65:
                continue
            if part == "hip" and not 38 <= y <= 54:
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


def structure(owner, key):
    vis = lambda n: {p for p, o in owner.items() if o == n}
    blade = {p for p in vis("sword-blade") if key[p] in "ZM"}
    hand = vis("fist") | vis("sword-guard")
    roll, scarf, drape = vis("bedroll"), vis("scarf-neck"), vis("hip-drape")
    body = vis("coat") | scarf | vis("collar") | vis("collar-front")
    roll_teal = {p for p in roll if key[p] in "QqgG"}
    scarf_teal = {p for p in scarf if key[p] in "QqgG"}
    rx, ry = [p[0] for p in roll], [p[1] for p in roll]
    gaps = {}
    for y in sorted(set(ry)):
        right = max(x for x, yy in roll if yy == y)
        nxt = min((x for (x, yy) in owner if yy == y and x > right), default=None)
        gaps[y] = None if nxt is None else nxt - right - 1
    far, near = vis("far-leg"), vis("near-leg")
    dy = sorted({y for _, y in drape})
    return {
        "far_leg_visible_texels": len(far),
        "far_leg_visible_trouser_texels": sum(1 for p in far if p[1] <= 57),
        "near_leg_visible_texels": len(near),
        "boot_texels_in_contact_shadow_rows_62_65": {k: {c: sum(1 for p in v if 62 <= p[1] <= 65 and key[p] == c)
                                                        for c in "KLlbB"} for k, v in (("far", far), ("near", near))},
        "far_trouser_keys": {c: sum(1 for p in far if p[1] <= 57 and key[p] == c) for c in "KCTt"},
        "bedroll_bbox_w_x_h": [max(rx) - min(rx) + 1, max(ry) - min(ry) + 1],
        "bedroll_rows": [min(ry), max(ry)],
        "bedroll_transparent_columns_to_next_texel_by_row": gaps,
        "bedroll_teal_to_scarf_teal_min_gap_texels": cheb_gap(roll_teal, scarf_teal),
        "bedroll_texels_4adjacent_to_coat_scarf_collar": adjacent(roll, body),
        "drape_visible_texels": len(drape),
        "drape_rows": [dy[0], dy[-1]],
        "drape_max_width_texels": max(len([1 for (x, y) in drape if y == r]) for r in dy),
        "drape_texels_4adjacent_to_far_leg": adjacent(drape, far),
        "sword_light_texels": len(blade),
        "sword_light_core_4connected_components": components(blade),
        "hand_hilt_rows_clear_of_belt_top": BELT_TOP - max(y for _, y in hand) - 1,
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
        rep[tag] = {"structure": structure(owner, key)}
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
