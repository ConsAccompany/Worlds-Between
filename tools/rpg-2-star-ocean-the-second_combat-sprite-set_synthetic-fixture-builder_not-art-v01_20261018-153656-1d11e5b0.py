"""Builds the SYNTHETIC DIAGNOSTIC combat sprite set fixtures for the opt-in combat sprite set pilot.

NOT ART. These are test fixtures only: a magenta-belted mannequin with action/frame labels, a facing arrow and a
magenta ground-anchor tick, drawn from code so the loader and playback can be checked (frame selection, timing, facing
mirroring, pivots, fallback). They prove loader behaviour, not smooth motion or character design, and must never be
reviewed, approved or shipped as character art. Nothing here is derived from the rejected 32x48 combat prototypes or
from any unapproved candidate frame.

Display proportion: crown row 15 to sole row 75 = 61 logical px at logical scale 1, the creator-approved 0.65 battle
display proportion (the same 61 px crown-to-sole as the 68x72 static pilots). Pivot (40, 76) = the floor point.

Usage: python -I <this file> [--check]   (--check rebuilds in memory and compares with the committed files)
"""
import hashlib
import io
import json
import math
import pathlib
import sys

from PIL import Image, ImageDraw

ROOT = pathlib.Path(__file__).resolve().parents[1]
FIXTURE_DIR = ROOT / "game/tests/fixtures/csp-fixture-v01_03f4172a"
RES_DIR = "res://tests/fixtures/csp-fixture-v01_03f4172a"
STAMP = "20261018-153656"
PREFIX = "rpg-2-star-ocean-the-second_combat-set"
CELL = (96, 80)
COLUMNS = 8
PIVOT = (40, 76)
# Per character: member id, appearance (hero only), file ids, identity fill, initial, whether the set carries a skill action.
CHARACTERS = [
    {"key": "hero:male", "member": "hero", "appearance": "male", "slug": "hero-male", "ids": ("5c2e81d4", "a7f03b69"), "fill": "#5eb6af", "initial": "H", "skill": True},
    {"key": "hero:female", "member": "hero", "appearance": "female", "slug": "hero-female", "stamp": "20261018-171817", "ids": ("6da48b19", "933ae4c0"), "fill": "#bba4d8", "initial": "H", "skill": True},
    {"key": "liang-xu", "member": "liang-xu", "slug": "liang-xu", "ids": ("e14b7a02", "3d9c6f18"), "fill": "#a6b4b8", "initial": "L", "skill": True},
    # Zhao Ling's set deliberately has no skill action, so the pilot's skill -> attack fallback is exercised in battle.
    {"key": "zhao-ling", "member": "zhao-ling", "slug": "zhao-ling", "ids": ("8b6d2e57", "f2a4c931"), "fill": "#69bbce", "initial": "Z", "skill": False},
    {"key": "ji-cheng", "member": "ji-cheng", "slug": "ji-cheng", "ids": ("4e07b9ac", "c58d1e3f"), "fill": "#6da78b", "initial": "J", "skill": True},
]
INDEX_NAME = f"{PREFIX}_fixture-index_not-art-v01_{STAMP}-03f4172a.json"
# action: (first cell, per-frame ms, loop, label letter)
ACTIONS = {
    "idle": (0, [240, 240, 240, 240], True, "I"),
    "move": (4, [90] * 8, True, "M"),
    "attack": (12, [50, 50, 70, 90, 70, 60], False, "A"),
    "skill": (18, [75] * 6, False, "S"),
    "dodge": (24, [50, 80, 80, 60], False, "D"),
    "guard": (28, [180, 180], True, "G"),
    "hit": (30, [80, 80, 80], False, "H"),
    "defeat": (33, [80, 80, 80, 120], False, "X"),
}
# Dodge frames 1 and 2 are drawn 6 px back inside the cell and declare their own pivot, so per-frame pivots are exercised.
DODGE_SHIFT = {1: -6, 2: -6}
OUTLINE = (16, 16, 16, 255)
MAGENTA = (255, 0, 255, 255)
GLYPHS = {
    "0": "111101101101111", "1": "010110010010111", "2": "111001111100111", "3": "111001111001111", "4": "101101111001001",
    "5": "111100111001111", "6": "111100111101111", "7": "111001001001001", "8": "111101111101111", "9": "111101111001111",
    "A": "010101111101101", "D": "110101101101110", "E": "111100110100111", "G": "111100101101111", "H": "101101111101101",
    "I": "111010010010111", "J": "001001001101111", "L": "100100100100111", "M": "101111111101101", "S": "111100111001111",
    "T": "111010010010010", "X": "101101010101101", "Z": "111001010100111",
}


def rgba(hex_color, alpha=255):
    h = hex_color.lstrip("#")
    return (int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16), alpha)


def shade(color, factor):
    return tuple(max(0, min(255, round(c * factor))) for c in color[:3]) + (255,)


def text(draw, x, y, string, color):
    for char in string:
        bits = GLYPHS[char]
        for i, bit in enumerate(bits):
            if bit == "1":
                draw.point((x + i % 3, y + i // 3), fill=color)
        x += 4


def limb(draw, a, b, width, color):
    draw.line([a, b], fill=color, width=width)
    r = width // 2
    for p in (a, b):
        draw.ellipse([p[0] - r, p[1] - r, p[0] + r, p[1] + r], fill=color)


def pose(action, frame):
    """Joint offsets for one frame (facing right). Values are small integers so every frame is crisp."""
    p = {"lean": 0, "bob": 0, "crouch": 0, "ff": 5, "bf": -5, "fl": 0, "bl": 0, "hand_f": (13, 12), "hand_b": (-9, 14),
         "weapon": 0, "flash": False, "ring": 0, "shield": False}
    if action == "idle":
        p["bob"] = [0, 1, 1, 0][frame]
        p["hand_f"] = (13, 12 + p["bob"])
    elif action == "move":
        phase = frame / 8 * 2 * math.pi
        swing = round(9 * math.sin(phase))
        p.update(ff=swing, bf=-swing, fl=max(0, round(4 * math.cos(phase))), bl=max(0, round(-4 * math.cos(phase))),
                 bob=-round(abs(math.sin(phase))), lean=2, hand_f=(6 - swing, 14), hand_b=(-4 + swing, 14))
    elif action == "attack":
        p.update([
            dict(lean=-2, hand_f=(-4, 4), weapon=0),
            dict(lean=-3, hand_f=(-8, -2), weapon=10),
            dict(lean=2, hand_f=(16, 4), weapon=14),
            dict(lean=4, ff=10, hand_f=(22, 8), weapon=20),
            dict(lean=2, ff=8, hand_f=(18, 12), weapon=12),
            dict(lean=0, hand_f=(14, 13), weapon=0),
        ][frame])
    elif action == "skill":
        p.update(hand_f=(6, -14), hand_b=(-2, -14), ring=3 + frame, bob=-1 if frame in (2, 3) else 0)
    elif action == "dodge":
        p.update([dict(crouch=4, lean=-2), dict(crouch=8, lean=-4, ff=8, bf=-9), dict(crouch=8, lean=-4, ff=8, bf=-9), dict(crouch=3, lean=-1)][frame])
        p["hand_f"] = (10, 6)
    elif action == "guard":
        p.update(hand_f=(14, 0), hand_b=(12, 4), shield=True, bob=frame, ff=6, bf=-7)
    elif action == "hit":
        p.update(lean=[-3, -5, -2][frame], hand_f=(6, 16), flash=frame == 0, bf=-8)
    elif action == "defeat":
        p.update([dict(lean=-4, crouch=4, flash=True), dict(crouch=12, lean=2, ff=9, bf=-4, hand_f=(10, 18))][frame] if frame < 2 else {})
    return p


def draw_figure(fill, action, frame, shift):
    """One cell: the mannequin silhouette with a 1 px outline, labels and the ground-anchor tick."""
    body = Image.new("RGBA", CELL, (0, 0, 0, 0))
    d = ImageDraw.Draw(body)
    px = PIVOT[0] + shift
    color = rgba(fill)
    leg = shade(color, 0.62)
    skin = rgba("#e5c594")
    p = pose(action, frame)
    if p["flash"]:
        color = shade(color, 1.45)
    if action == "defeat" and frame >= 2:
        if frame == 2:  # falling: body tipped back on one knee
            limb(d, (px + 6, 74), (px + 2, 66), 4, leg)
            limb(d, (px + 2, 66), (px - 6, 58), 4, leg)
            d.polygon([(px - 6, 60), (px - 20, 44), (px - 26, 50), (px - 10, 64)], fill=color)
            d.ellipse([px - 34, 38, px - 22, 50], fill=skin)
        else:  # lying on the floor
            d.rectangle([px - 22, 66, px + 4, 74], fill=color)
            limb(d, (px + 4, 71), (px + 24, 73), 4, leg)
            d.ellipse([px - 35, 64, px - 23, 75], fill=skin)
            d.rectangle([px - 6, 66, px - 4, 74], fill=MAGENTA)
    else:
        hip = (px + p["lean"], 50 + p["bob"] + p["crouch"])
        shoulder = (px + p["lean"] + (1 if p["lean"] > 0 else 0), 32 + p["bob"] + p["crouch"])
        for foot_dx, lift, colour in ((p["bf"], p["bl"], shade(leg, 0.8)), (p["ff"], p["fl"], leg)):
            foot = (px + foot_dx, 74 - lift)
            knee = ((hip[0] + foot[0]) // 2 + 3, (hip[1] + foot[1]) // 2 - lift)
            limb(d, (hip[0] + (2 if colour == leg else -2), hip[1]), knee, 4, colour)
            limb(d, knee, foot, 4, colour)
            d.rectangle([foot[0] - 2, foot[1] - 1, foot[0] + 4, foot[1] + 1], fill=shade(colour, 0.7))
        limb(d, (shoulder[0] - 3, shoulder[1] + 2), (shoulder[0] + p["hand_b"][0], shoulder[1] + p["hand_b"][1]), 3, shade(color, 0.75))
        d.polygon([(shoulder[0] - 6, shoulder[1]), (shoulder[0] + 6, shoulder[1]), (hip[0] + 5, hip[1]), (hip[0] - 5, hip[1])], fill=color)
        d.rectangle([hip[0] - 5, hip[1] - 2, hip[0] + 5, hip[1]], fill=MAGENTA)
        # Facing arrow on the chest: points to the authored facing (right).
        cx, cy = shoulder[0] + 1, shoulder[1] + 7
        d.polygon([(cx - 3, cy - 3), (cx + 2, cy), (cx - 3, cy + 3)], fill=(255, 255, 255, 255))
        head = (shoulder[0] + (1 if p["lean"] > 0 else 0), 21 + p["bob"] + p["crouch"])
        d.ellipse([head[0] - 6, head[1] - 6, head[0] + 6, head[1] + 6], fill=skin)
        d.point((head[0] + 3, head[1] - 1), fill=OUTLINE)
        hand = (shoulder[0] + p["hand_f"][0], shoulder[1] + p["hand_f"][1])
        limb(d, (shoulder[0] + 3, shoulder[1] + 2), hand, 3, shade(color, 0.9))
        if p["weapon"]:
            limb(d, hand, (hand[0] + p["weapon"], hand[1] - 2), 2, (226, 236, 222, 255))
        if p["shield"]:
            d.rectangle([hand[0] + 2, shoulder[1] - 6, hand[0] + 5, shoulder[1] + 24], fill=(167, 215, 238, 255))
        if p["ring"]:
            r = p["ring"]
            c = (shoulder[0] + 2, shoulder[1] - 14)
            d.ellipse([c[0] - r, c[1] - r, c[0] + r, c[1] + r], outline=(0, 255, 255, 255), width=2)
    # 1 px outline around the whole silhouette.
    cell = Image.new("RGBA", CELL, (0, 0, 0, 0))
    src, dst = body.load(), cell.load()
    for y in range(CELL[1]):
        for x in range(CELL[0]):
            if src[x, y][3]:
                dst[x, y] = src[x, y][:3] + (255,)
            elif any(0 <= x + dx < CELL[0] and 0 <= y + dy < CELL[1] and src[x + dx, y + dy][3] for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1))):
                dst[x, y] = OUTLINE
    d = ImageDraw.Draw(cell)
    # Ground-anchor tick under the floor point: rows 76-77 land on screen rows 272-273 (the floor) at the fighter's x.
    d.point([(px, PIVOT[1]), (px, PIVOT[1] + 1)], fill=MAGENTA)
    d.point([(px - 1, PIVOT[1] + 1), (px + 1, PIVOT[1] + 1)], fill=MAGENTA)
    return cell


def build():
    files = {}
    sets = {}
    for ch in CHARACTERS:
        sheet = Image.new("RGBA", (CELL[0] * COLUMNS, CELL[1] * 5), (0, 0, 0, 0))
        actions = {}
        for name, (first, durations, loop, letter) in ACTIONS.items():
            frames = []
            for i, ms in enumerate(durations):
                index = first + i
                shift = DODGE_SHIFT.get(i, 0) if name == "dodge" else 0
                cell = draw_figure(ch["fill"], name, i, shift)
                d = ImageDraw.Draw(cell)
                text(d, 1, 1, f"{letter}{i}", (255, 224, 0, 255))
                text(d, 1, 7, "TEST", (255, 0, 255, 255))
                text(d, 13, 1, ch["initial"], (255, 255, 255, 255))
                sheet.alpha_composite(cell, ((index % COLUMNS) * CELL[0], (index // COLUMNS) * CELL[1]))
                entry = {"cell": index, "ms": ms}
                if shift:
                    entry["pivot"] = [PIVOT[0] + shift, PIVOT[1]]
                frames.append(entry)
            if name == "skill" and not ch["skill"]:
                continue
            actions[name] = {"loop": loop, "frames": frames}
        sheet_name = f"{PREFIX}_{ch['slug']}-sheet_not-art-v01_{ch.get('stamp', STAMP)}-{ch['ids'][0]}.png"
        manifest_name = f"{PREFIX}_{ch['slug']}-manifest_not-art-v01_{ch.get('stamp', STAMP)}-{ch['ids'][1]}.json"
        buffer = io.BytesIO()
        sheet.save(buffer, "PNG", optimize=False, compress_level=9)
        files[sheet_name] = buffer.getvalue()
        character = {"member_id": ch["member"]}
        if "appearance" in ch:
            character["appearance"] = ch["appearance"]
        manifest = {
            "schema": "worlds-between.combat-sprite-set/1",
            "set_id": f"synthetic-diagnostic-{ch['slug']}-v01",
            "character": character,
            "art_status": "synthetic-diagnostic-test-fixture-not-art",
            "art_approved": False,
            "note": "NOT ART: code-drawn diagnostic mannequin for loader/playback tests only. Never review or ship as character art.",
            "sheet": sheet_name,
            "sheet_sha256": hashlib.sha256(files[sheet_name]).hexdigest(),
            "cell_size": list(CELL),
            "pivot": list(PIVOT),
            "authored_facing": "right",
            "logical_scale": 1,
            "display_proportion": "0.65",
            "actions": actions,
        }
        files[manifest_name] = (json.dumps(manifest, indent=2) + "\n").encode()
        sets[ch["key"]] = f"{RES_DIR}/{manifest_name}"
    index = {
        "schema": "worlds-between.combat-sprite-set-index/1",
        "art_status": "synthetic-diagnostic-test-fixture-not-art",
        "art_approved": False,
        "note": "Synthetic diagnostic fixtures for the opt-in --combat-sprite-set-pilot only. Both hero appearances have distinct synthetic sets; neither is character art.",
        "sets": sets,
    }
    files[INDEX_NAME] = (json.dumps(index, indent=2) + "\n").encode()
    return files


def main():
    files = build()
    if "--check" in sys.argv:
        bad = []
        for name, data in files.items():
            path = FIXTURE_DIR / name
            current = path.read_bytes() if path.exists() else b""
            if name.endswith(".json"):
                current = current.replace(b"\r\n", b"\n")
            if current != data:
                bad.append(name)
        print("FIXTURE CHECK " + ("PASS" if not bad else "FAIL " + ", ".join(bad)) + f" files={len(files)}")
        sys.exit(1 if bad else 0)
    FIXTURE_DIR.mkdir(parents=True, exist_ok=True)
    for name, data in files.items():
        (FIXTURE_DIR / name).write_bytes(data)
        print(f"{name} {hashlib.sha256(data).hexdigest()}")


if __name__ == "__main__":
    main()
