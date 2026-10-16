"""UNAPPROVED, test-only measurement: female side-view battle static v06 vs v07, per layer region, in the real captures.

Reads only. For each version it imports the author tool (layer definitions only; main() is not run), finds which layer
is topmost at every opaque texel, and maps each texel to its 2x2 screen block in that version's 1280x720 Godot party
capture (texture origin 536, 408). Value separation per region = mean |dL| (Rec.709 luma) between the capture and the
v07 no-sprite capture of the same arena, plus the share of pixels with |dL| < 20 (the v05/v06 QA metric). The no-sprite
frame is identical across versions outside the sprite's own pixels, so v06 captures are measured against it too.

Structural checks that the v06 audit's four defects are about:
  ponytail_vs_bedroll   texels where the ponytail touches (4-neighbour) or is covered by the bedroll; min gap
  back_cluster          gear layers (pack, bedroll, buckle) whose texels lie above the scarf's top row / beside the head
  collar_in_front       collar texels to the right of (in front of) the scarf's front edge
  coat_leg_same_colour  4-neighbour pairs across the coat-skirt / far-leg boundary with the SAME colour (fusing)

Usage:  python -I -B <this file> <v07 no-sprite ruins png> <v07 no-sprite outskirts png>
"""
import glob, importlib.util, json, os, sys
import numpy as np
from PIL import Image

REPO = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
ORIGIN = (536, 408)
VERS = {
    "v06": ("*0p65-author_unapproved-v06_20261016-065106-7ac0f8e3.py", "unapproved-v06_20261016-065106"),
    "v07": ("*0p65-author_unapproved-v07_20261016-070549-0e2efcac.py", "unapproved-v07_20261016-070549"),
}
REGIONS = {
    "coat (torso + skirt)": ["coat", "coat-skirt"],
    "collar (all collar layers)": ["collar", "collar-front"],
    "far leg trouser (rows 42-56)": ["far-leg@trouser"],
    "boots (rows 57-67, both)": ["far-leg@boot", "near-leg@boot"],
    "back gear (pack + bedroll)": ["pack", "bedroll"],
    "teal (scarf + bedroll)": ["scarf-neck", "bedroll"],
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
    owner = {}
    for name, texels in mod.LAYERS:
        for x, y, _ in texels:
            owner[(x, y)] = name
    return owner


def region_of(owner, spec):
    out = set()
    for s in spec:
        name, _, part = s.partition("@")
        for (x, y), n in owner.items():
            if n != name:
                continue
            if part == "trouser" and not 42 <= y <= 56:
                continue
            if part == "boot" and not 57 <= y <= 67:
                continue
            out.add((x, y))
    return out


def structure(mod, owner):
    layer = {n: {(x, y) for x, y, _ in t} for n, t in mod.LAYERS}
    key = {}
    for n, t in mod.LAYERS:
        for x, y, ch in t:
            key[(x, y)] = ch
    pony_all, roll_all = layer.get("ponytail", set()), layer.get("bedroll", set())
    pony_vis = {p for p in pony_all if owner[p] == "ponytail"}
    roll_vis = {p for p in roll_all if owner[p] == "bedroll"}
    touch = sum(1 for (x, y) in pony_vis if any((x + dx, y + dy) in roll_vis
                                                 for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1))))
    covered = len(pony_all - pony_vis)
    gap = min((max(abs(a[0] - b[0]), abs(a[1] - b[1])) for a in pony_vis for b in roll_vis), default=None)
    scarf = {p for p in layer["scarf-neck"] if owner[p] == "scarf-neck"}
    scarf_top = min(y for _, y in scarf)
    gear = [n for n in ("pack", "bedroll", "pack-buckle") if n in layer]
    gear_above_scarf = sum(1 for n in gear for (x, y) in layer[n] if owner[(x, y)] == n and y < scarf_top)
    front_by_row = {}
    for x, y in scarf:
        front_by_row[y] = max(front_by_row.get(y, -1), x)
    collar_front = sum(1 for n in ("collar", "collar-front") if n in layer
                       for (x, y) in layer[n] if owner[(x, y)] == n
                       and (y not in front_by_row or x >= front_by_row[y]) and x > 32)
    same = 0
    for (x, y), n in owner.items():
        if n != "coat-skirt":
            continue
        for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            q = (x + dx, y + dy)
            if owner.get(q) == "far-leg" and key[q] == key[(x, y)] and key[q] != "K":
                same += 1
    return {"ponytail_texels_touching_bedroll": touch, "ponytail_texels_hidden_under_later_layers": covered,
            "ponytail_to_bedroll_min_gap_texels": gap, "visible_ponytail_texels": len(pony_vis),
            "ponytail_lowest_visible_row": max(y for _, y in pony_vis),
            "gear_texels_above_scarf_top_row": gear_above_scarf, "scarf_top_row": scarf_top,
            "collar_texels_in_front_of_scarf_front_edge": collar_front,
            "coat_skirt_far_leg_same_colour_neighbour_pairs": same}


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
        owner = topmost(mod)
        rep[tag] = {"structure": structure(mod, owner)}
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
