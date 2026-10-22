"""Washington records chamber (scifi.ruins survey annex room 2) STYLE48: native 640x360 background from the generated
style48 common-style reference (UNAPPROVED candidate, not a default).

The creator approved the common science-scene material DIRECTION only; this room image, its default and final art are
NOT approved. Method of the style45/style46 tools:
  * Conversion: the 1672x941 generated reference is sampled once to 640x360 with NEAREST exact source-pixel sampling,
    src = floor((2*dst + 1) * src_size / (2 * 640|360)). No smoothing, filter, quantization, palette mapping or new
    pixels. It is generated raster, not hand-placed pixel art. The runtime output is that background PNG only.
  * Fixtures: the four authored v01 room-2 fixtures (three clue fixtures, analysis light table) are reused byte-for-byte
    at their unchanged runtime top-left positions, read from the immutable survey_annex.gd snapshot in outputs/style48
    (never the mutable game script). They are not copied into the runtime folder; their paths/hashes are pinned.
  * Planes: base (converted reference) + terminal + three clue planes, full canvas, alpha preserved, in the runtime
    y-sort draw order (terminal sorts first; no plane overlaps another). Flat = their composite, for review only; the
    game keeps drawing the separate sprites. A hidden locked guide plane shows the snapshot's room-2 feet blockers.
Editable sources: OpenRaster .ora + Pixelorama .pxo from the imported, unchanged v05 Chicago writers (build() is never
called). Also writes a zero-context unified diff for game/scripts/survey_annex.gd (flag --wdc-records-style48); the
module itself is never edited here. Apply with `git apply --unidiff-zero`.
Usage: python -X utf8 <this> [--check]   (--check rebuilds in memory and compares bytes; never writes)
"""
from __future__ import annotations

from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path
import difflib
import hashlib
import io
import json
import re
import sys
import zipfile

import numpy as np
from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
TAG = "20261022-185913-713cdcb1"
VARIANT = "unapproved-v01"
PROJECT = "rpg-2-star-ocean-the-second_wdc-records-room2"
OUT = ROOT / "outputs" / "style48"
RUNTIME = ROOT / "game" / "assets" / "environments" / "style48"
ZIP_TIME = (2026, 10, 22, 18, 59, 13)
MODULE = "game/scripts/survey_annex.gd"
PROPS = "game/assets/props/wdc-annex-room2/rpg-2-star-ocean-the-second_wdc-annex-room2_%s-pixel-fixture_unapproved-v01_20261018-001157-151fb8d0.png"
CLUES = ["machine-translation", "parallel-inscription", "erased-heading"]   # WDC_ROOM_TWO_FIXTURES order
TERMINAL = "analysis-light-table"
EXPECTED_POS = {"clue-0": (115, 164), "clue-1": (272, 164), "clue-2": (429, 164), "terminal": (272, 278)}
FIXTURE_KEYS = ["clue-0", "clue-1", "clue-2", "terminal"]                    # manifest row order
LAYERS = ["rt-background", "terminal", "clue-0", "clue-1", "clue-2"]         # bottom to top = runtime draw order
GUIDE = "room2-blockers-guide-hidden"
B, T = "sha256-bytes", "sha256-text-lf-v1"
INPUTS = {   # key -> (path relative to ROOT, hash algorithm, sha256); text = CRLF->LF before hashing
    "reference": ("outputs/style48/rpg-2-star-ocean-the-second_wdc-records-room2_common-style-reference_nonruntime-v01_20261022-185913-713cdcb1.png", B,
                  "3bd0f756d35dc36eb46b0238d1ce5a7e9b7e5f97ed57ab193aaf22d3decb08c3"),
    "reference-provenance": ("outputs/style48/rpg-2-star-ocean-the-second_wdc-records-room2_reference-provenance_nonruntime-v01_20261022-185913-713cdcb1.json", T,
                             "b9bb438fef1b4293ba8e2457ec244e97c6786603e2cdb90071b3f41badfa098f"),
    "input-module": ("outputs/style48/rpg-2-star-ocean-the-second_wdc-records-room2_survey-module-input_v01_20261022-185913-713cdcb1.gd", T,
                     "8db21a05504c027188d57c91e7852ef7d643d64401d6a0b96a21457b18888cbf"),   # == canonical survey_annex.gd
    "clue-0": (PROPS % CLUES[0], B, "03e826d1cab164b6152156c1eb73f022a8efd01805f060535c4f38a6efd8d4fc"),
    "clue-1": (PROPS % CLUES[1], B, "d3b01dbfbd66620844994739b1ef6db6ab101f0790c4bb1c90ad3d6ba49f6896"),
    "clue-2": (PROPS % CLUES[2], B, "f779857cd63ef74c9d190caa0a1eab0c4b41c6531809e6b7e5fef70eb5ae436a"),
    "terminal": (PROPS % TERMINAL, B, "5ab452660427fdb4c176a8eb183082e7e7d6900383c38382f0bd42a6056907d9"),
    "fixture-author": ("tools/rpg-2-star-ocean-the-second_wdc-annex-room2_records-chamber-fixtures-author_unapproved-v01_20261018-001157-151fb8d0.py", T,
                       "741777d1dbdb2f53fd4c5ac19b21ce1ebc064bc40e1f98ace89842a5b15ee04d"),
    "v05-writers": ("tools/rpg-2-star-ocean-the-second_chicago-loop_state-lake-block-pixel-author_unapproved-v05_20261017-234337-84862412.py", T,
                    "d4fa8a4f58140e46865339b0c9032883ec0e8399d674b246f047d014fb3428bb"),
}


def sha(data):
    return hashlib.sha256(data).hexdigest()


def text_sha(data):
    return sha(data.replace(b"\r\n", b"\n"))


def lp(path):
    s = str(Path(path).resolve())
    return Path(s if s.startswith("\\\\?\\") else "\\\\?\\" + s)


def read_input(key):
    path, algo, want = INPUTS[key]
    data = lp(ROOT / path).read_bytes()
    got = text_sha(data) if algo == T else sha(data)
    if got != want:
        raise SystemExit(f"input hash mismatch: {path}: {got} != {want}")
    return data


def load_writers():
    """v05 Chicago author imported unchanged for png_bytes/ora_bytes/pxo_bytes; its build() is never called."""
    read_input("v05-writers")
    spec = spec_from_file_location("chicago_author_v05_for_style48", lp(ROOT / INPUTS["v05-writers"][0]))
    mod = module_from_spec(spec)
    spec.loader.exec_module(mod)
    mod.PREFIX, mod.LAYERS, mod.GUIDE, mod.ZIP_TIME = PROJECT, LAYERS, GUIDE, ZIP_TIME
    return mod


v5 = load_writers()
W, H = v5.W, v5.H


def asset(purpose, ext):
    return f"{PROJECT}_style48-{purpose}_{VARIANT}_{TAG}.{ext}"


BACKGROUND = RUNTIME / asset("rt-background", "png")
RES_BACKGROUND = "res://" + BACKGROUND.relative_to(ROOT / "game").as_posix()
NUM = r"(-?\d+(?:\.\d+)?)"


def module_facts(text):
    """Room-2 fixture geometry as the immutable snapshot declares it (the runtime truth this package must match)."""
    def one(pattern):
        found = re.findall(pattern, text, re.M)
        if len(found) != 1:
            raise SystemExit(f"module fact not unique: {pattern}")
        return found[0]
    clue_x = [float(x) for x, _ in re.findall(r"Vector2\(" + NUM + ", " + NUM + r"\)",
                                              one(r"^const CLUE_POSITIONS := \[(.*)\]$"))]
    top = float(one(r"^const WDC_ROOM_TWO_FIXTURE_TOP := " + NUM + "$"))
    tx, ty = one(r"^const WDC_ROOM_TWO_TERMINAL_ORIGIN := Vector2\(" + NUM + ", " + NUM + r"\)$")
    dx = float(one(r"^\t\tfixture\.position = Vector2\(CLUE_POSITIONS\[index\]\.x - " + NUM + r", WDC_ROOM_TWO_SORT_Y\)$"))
    one(r"^\t\tfixture\.offset = Vector2\(0, WDC_ROOM_TWO_FIXTURE_TOP - WDC_ROOM_TWO_SORT_Y\)$")
    one(r"^\tterminal\.position = Vector2\(WDC_ROOM_TWO_TERMINAL_ORIGIN\.x, 0\)$")
    one(r"^\tterminal\.offset = Vector2\(0, WDC_ROOM_TWO_TERMINAL_ORIGIN\.y\)$")
    fixtures = re.findall(r'preload\("res://(assets/props/wdc-annex-room2/[^"]+)"\)',
                          one(r"^const WDC_ROOM_TWO_FIXTURES := \[\n((?:\t.*\n)+)\]$"))
    terminal = one(r'^const WDC_ROOM_TWO_TERMINAL := preload\("res://([^"]+)"\)$')
    blockers = [tuple(int(v) for v in r) for r in re.findall(r"Rect2\((\d+), (\d+), (\d+), (\d+)\)",
                                                             one(r"^const WDC_ROOM_TWO_BLOCKERS := \[\n((?:\t.*\n)+)\]$"))]
    pos = {f"clue-{i}": (int(x - dx), int(top)) for i, x in enumerate(clue_x)} | {"terminal": (int(float(tx)), int(float(ty)))}
    files = {f"clue-{i}": "game/" + f for i, f in enumerate(fixtures)} | {"terminal": "game/" + terminal}
    return pos, files, blockers


SNAPSHOT_REF = INPUTS["input-module"][0]
MODULE_EDITS = [   # (anchor, replacement) on the LF snapshot; each anchor must occur exactly once
    ('const WDC_ROOM_TWO_FLAG := "--wdc-records-chamber-v01"\n',
     'const WDC_ROOM_TWO_FLAG := "--wdc-records-chamber-v01"\n'
     '# Washington room 2 STYLE48 common-style background (UNAPPROVED, opt-in `-- --wdc-records-style48`): new background\n'
     '# texture only; the v01 fixtures, anchors and blockers are unchanged and also enabled by this flag.\n'
     'const WDC_RECORDS_STYLE48_FLAG := "--wdc-records-style48"\n'
     f'const WDC_RECORDS_STYLE48_BACKGROUND := preload("{RES_BACKGROUND}")\n'),
    ('\tif wdc_room_two_walls and (OS.get_cmdline_user_args().has(WDC_ROOM_TWO_FLAG) or SceneDefaults35.default_on(SceneDefaults35.RECORDS)):\n',
     '\tif wdc_room_two_walls and (OS.get_cmdline_user_args().has(WDC_ROOM_TWO_FLAG) or OS.get_cmdline_user_args().has(WDC_RECORDS_STYLE48_FLAG) or SceneDefaults35.default_on(SceneDefaults35.RECORDS)):\n'),
    ('\t\tdraw_texture_rect(ROOM_TWO_BACKGROUND[destination_id], Rect2(0, 0, 640, 360), false)\n',
     '\t\tdraw_texture_rect(_room_two_background(), Rect2(0, 0, 640, 360), false)\n'),
    ('func _build_wdc_room_two() -> void:\n',
     '# STYLE48: the new background only in Washington room 2 with its flag (or the sdef35 RECORDS default once the\n'
     '# creator authorizes it); --wdc-records-chamber-v01 alone and every other destination/room keep the original plate.\n'
     'func _room_two_background() -> Texture2D:\n'
     '\tif destination_id == "scifi.ruins" and room == 2 and (OS.get_cmdline_user_args().has(WDC_RECORDS_STYLE48_FLAG) or SceneDefaults35.default_on(SceneDefaults35.RECORDS)):\n'
     '\t\treturn WDC_RECORDS_STYLE48_BACKGROUND\n'
     '\treturn ROOM_TWO_BACKGROUND[destination_id]\n'
     '\n\n'
     'func _build_wdc_room_two() -> void:\n'),
]


def apply_zero_context(old_lines, patch):
    """Independent re-application of the n=0 diff (as `git apply --unidiff-zero` would) to prove it reproduces new."""
    out, at = [], 0
    lines = patch.splitlines(True)
    i = 2
    while i < len(lines):
        m = re.match(r"@@ -(\d+)(?:,(\d+))? \+(\d+)(?:,(\d+))? @@", lines[i])
        start, count = int(m.group(1)), int(m.group(2) or 1)
        cut = start if count == 0 else start - 1
        out += old_lines[at:cut]
        at = cut
        i += 1
        while i < len(lines) and lines[i][:1] in ("-", "+"):
            if lines[i][0] == "-":
                if old_lines[at] != lines[i][1:]:
                    raise SystemExit(f"zero-context hunk does not match snapshot line {at + 1}")
                at += 1
            else:
                out.append(lines[i][1:])
            i += 1
        if at != cut + count:
            raise SystemExit("zero-context hunk length mismatch")
    return out + old_lines[at:]


def module_patch():
    old = read_input("input-module").decode("utf-8").replace("\r\n", "\n")
    new = old
    for a, b in MODULE_EDITS:
        if new.count(a) != 1:
            raise SystemExit(f"module anchor not unique: {a!r}")
        new = new.replace(a, b)
    o, n = old.splitlines(True), new.splitlines(True)
    removed = [l for l in difflib.ndiff(o, n) if l.startswith("- ")]
    if [l[2:] for l in removed] != [MODULE_EDITS[1][0], MODULE_EDITS[2][0]]:
        raise SystemExit("patch removes lines other than the fixture condition and the room-2 background draw")
    diff = "".join(difflib.unified_diff(o, n, f"a/{MODULE}", f"b/{MODULE}", n=0))
    if "".join(apply_zero_context(o, diff)) != new:
        raise SystemExit("zero-context patch does not reproduce the patched module")
    return diff, text_sha(new.encode("utf-8")), sha(old.encode("utf-8"))


def build():
    module_text = read_input("input-module").decode("utf-8").replace("\r\n", "\n")
    pos, files_in_module, blockers = module_facts(module_text)
    if pos != EXPECTED_POS or files_in_module != {k: INPUTS[k][0] for k in FIXTURE_KEYS}:
        raise SystemExit(f"snapshot fixture geometry/paths differ: {pos} {files_in_module}")
    read_input("fixture-author")
    ref = np.array(Image.open(io.BytesIO(read_input("reference"))).convert("RGBA"))
    if (ref[..., 3] != 255).any():
        raise SystemExit("reference has transparency")
    sh, sw = ref.shape[:2]
    sx, sy = (np.arange(W) * 2 + 1) * sw // (2 * W), (np.arange(H) * 2 + 1) * sh // (2 * H)
    conv = np.ascontiguousarray(ref[sy][:, sx])
    raw = {k: read_input(k) for k in FIXTURE_KEYS}
    layers = {"rt-background": Image.fromarray(conv, "RGBA")}
    cover = np.zeros((H, W), np.uint8)
    for k in FIXTURE_KEYS:
        prop = Image.open(io.BytesIO(raw[k]))
        if prop.mode != "RGBA" or prop.size != ((96, 40) if k == "terminal" else (96, 72)):
            raise SystemExit(f"{k}: unexpected prop size/mode {prop.size} {prop.mode}")
        plane = Image.new("RGBA", (W, H))
        plane.paste(prop, pos[k])
        x, y = pos[k]
        if not np.array_equal(np.array(plane)[y:y + prop.height, x:x + prop.width], np.array(prop)):
            raise SystemExit(f"{k}: plane does not carry the prop pixels exactly")
        cover += (np.array(plane)[..., 3] > 0)
        layers[k] = plane
    if cover.max() > 1:
        raise SystemExit("fixture planes overlap; draw order would matter")
    flat = Image.new("RGBA", (W, H))
    for k in LAYERS:
        flat.alpha_composite(layers[k])
    expect = Image.fromarray(conv, "RGBA")
    for k in ["terminal", "clue-0", "clue-1", "clue-2"]:
        expect.alpha_composite(Image.open(io.BytesIO(raw[k])).convert("RGBA"), pos[k])
    if not np.array_equal(np.array(flat), np.array(expect)) or (np.array(flat)[..., 3] != 255).any():
        raise SystemExit("flat != background + props at runtime positions")
    guide = Image.new("RGBA", (W, H))
    g = np.array(guide)
    for x, y, w, h in blockers:
        g[y:y + h, x:x + w] = (255, 0, 64, 96)
    guide = Image.fromarray(g, "RGBA")
    patch, patched_sha, _ = module_patch()
    files = {}

    def put(path, data, role):
        files[path.relative_to(ROOT).as_posix()] = (data, role)
    put(BACKGROUND, v5.png_bytes(layers["rt-background"]),
        "NEW runtime background 640x360 RGBA (generated raster NEAREST-sampled; not hand pixel art; no props/characters/markers)")
    put(OUT / asset("flat-640x360", "png"), v5.png_bytes(flat),
        "review-only flat: new background + the four unchanged props at runtime positions (not a runtime file)")
    put(OUT / asset("layered-source", "ora"), v5.ora_bytes(layers, guide, flat),
        "OpenRaster editable full-canvas planes: 5 visible (background, terminal, 3 clues) + hidden blockers guide")
    pxo = io.BytesIO()
    with zipfile.ZipFile(io.BytesIO(v5.pxo_bytes(layers, guide, flat))) as zin, zipfile.ZipFile(pxo, "w", zipfile.ZIP_DEFLATED) as z:
        for info in zin.infolist():
            payload = zin.read(info.filename)
            if info.filename == "data.json":
                payload = payload.replace(b"chicago-loop-state-lake-v05", b"wdc-records-room2-style48-v01")
            z.writestr(zipfile.ZipInfo(info.filename, ZIP_TIME), payload, zipfile.ZIP_DEFLATED)
    put(OUT / asset("layered-source", "pxo"), pxo.getvalue(),
        "Pixelorama editable full-canvas planes: 5 visible + hidden locked blockers guide")
    put(OUT / asset("module-flag-diff", "patch"), patch.encode("utf-8"),
        f"proposed zero-context unified diff for {MODULE} (not applied; git apply --unidiff-zero); patched sha256-text-lf-v1 {patched_sha}")
    roles = {"reference": "generated common-style reference (image_gen; UNAPPROVED room image, direction approved only)",
             "reference-provenance": "generation provenance of the reference",
             "input-module": f"immutable snapshot of canonical {MODULE} (geometry source and patch base)",
             "fixture-author": "author of the unchanged v01 room-2 fixtures",
             "v05-writers": "Chicago v05 author; png/ora/pxo writers imported unchanged (build() never called)",
             **{k: f"unchanged v01 runtime prop, top-left {list(pos[k])} (not duplicated)" for k in FIXTURE_KEYS}}
    entries = {INPUTS[k][0]: {"sha256": INPUTS[k][2], "hash_algorithm": INPUTS[k][1], "role": roles[k]} for k in INPUTS}
    is_text = lambda p: p.endswith((".patch", ".json"))
    entries |= {p: {"sha256": text_sha(d) if is_text(p) else sha(d), "hash_algorithm": T if is_text(p) else B, "role": r}
                for p, (d, r) in files.items()}
    me = Path(__file__).resolve().relative_to(ROOT).as_posix()
    entries[me] = {"sha256": text_sha(Path(__file__).read_bytes()), "hash_algorithm": T, "role": "this builder (source)"}
    manifest = {
        "source_reference": {"file": INPUTS["reference"][0], "sha256": INPUTS["reference"][2]},
        "background": BACKGROUND.relative_to(ROOT).as_posix(),
        "fixtures": [{"file": INPUTS[k][0], "position": list(pos[k]), "sha256": INPUTS[k][2]} for k in FIXTURE_KEYS],
        "files": dict(sorted(entries.items())),
        "native_size": [W, H],
        "default_adopted": False,
        "art_unapproved": True,
        "source": me,
        "input_module": INPUTS["input-module"][0],
    }
    put(OUT / asset("manifest", "json"), (json.dumps(manifest, indent=2, ensure_ascii=False) + "\n").encode("utf-8"), "manifest")
    return files


def main():
    files = build()
    if "--check" in sys.argv[1:]:
        bad = [p for p, (d, _) in files.items() if not lp(ROOT / p).exists()
               or (lp(ROOT / p).read_bytes().replace(b"\r\n", b"\n") if p.endswith((".patch", ".json")) else lp(ROOT / p).read_bytes()) != d]
        print(json.dumps({"check": "FAIL" if bad else "PASS", "files": len(files), "mismatched": bad}, indent=1))
        sys.exit(1 if bad else 0)
    inputs = {INPUTS[k][0] for k in INPUTS}
    for p, (data, _) in files.items():
        path = ROOT / p
        if path.parent not in (OUT, RUNTIME) or TAG not in path.name or "_style48-" not in path.name or p in inputs:
            raise SystemExit(f"refusing to write outside the STYLE48 scope: {p}")
        lp(path.parent).mkdir(parents=True, exist_ok=True)
        lp(path).write_bytes(data)
    print(json.dumps({"written": len(files), "files": sorted(files)}, indent=1))


if __name__ == "__main__":
    main()
