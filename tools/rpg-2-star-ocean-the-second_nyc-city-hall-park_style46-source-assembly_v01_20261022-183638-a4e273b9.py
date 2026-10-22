"""NYC City Hall Park (scifi.city) STYLE46: native 640x360 source assembly from the generated style46 common-style
reference (UNAPPROVED candidate, not a default).

The creator approved the common science-scene style DIRECTION only; NYC final art and its default are NOT approved.
Method of the style45 tool:
  * Conversion: the 1672x941 generated reference is sampled once to 640x360 with NEAREST exact source-pixel sampling,
    src = floor((2*dst + 1) * src_size / (2 * 640|360)). Runtime UV-fit offset +24 logical rows: sy samples max(0,y-24), preserving the source file. No smoothing, filter, quantization, palette mapping or new
    pixels. It is generated raster, not hand-placed pixel art.
  * Planes: the immutable v06 runtime layers (rt-base, walkmask and the nine y-sort PNGs) are reused as geometry. The
    nine y-sort planes keep their exact binary alpha masks; their RGB is the converted reference. The base takes the
    converted reference except under the union of y-sort coverage, where it keeps the OLD v06 rt-base pixels as a
    hidden plate (old art, never seen in the no-actor composite).
  * Order: base, then the nine y-sort planes in the v06 scene order (= draw order: pivot z, ties in add order). The
    no-actor composite equals the converted reference exactly; the walk mask bytes are unchanged.
  * Scene data: new .json/.tres keep every gameplay field of v06 (canvas, ui_rows, ysort name/pivot/canopy, hotspots,
    legacy_positions, canopy_reveal); only base/walkmask/ysort png file names (and run/source/status text) change.
  * Silhouette alignment between the generated reference and the old masks is NOT proven; nothing here is approved art.
Editable sources: OpenRaster .ora + Pixelorama .pxo (1 base + 9 y-sort + hidden locked walk guide = 11 layers) from the
imported, unchanged v05 Chicago writers. Also writes a unified diff for game/scripts/city_hall_park_v06_scene.gd
(flag --nyc-common-style46); the module itself is never edited here.
Usage: python -X utf8 <this> [--check]   (--check rebuilds in memory and compares bytes; never writes)
"""
from __future__ import annotations

from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path
import difflib
import hashlib
import io
import json
import sys
import zipfile

import numpy as np
import PIL
from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
TAG = "20261022-183638-a4e273b9"
VARIANT = "unapproved-v01"
PROJECT = "rpg-2-star-ocean-the-second_nyc-city-hall-park"
OUT = ROOT / "outputs" / "style46"
RUNTIME = ROOT / "game" / "assets" / "environments" / "style46"
ZIP_TIME = (2026, 10, 22, 18, 36, 38)
V06D = "game/assets/environments/candidates/nyc-chp-v06_20261017-165253-4519dffe/"
V06F = "rpg-2-star-ocean-the-second_nyc-city-hall-park_%s_unapproved-v06_20261017-165253-4519dffe.%s"
MODULE = "game/scripts/city_hall_park_v06_scene.gd"
YSORT = ["rt-y-lamps-pr", "rt-y-bollard-p", "rt-y-lamp-ae", "rt-y-fount", "rt-y-lamp-pe", "rt-y-lamp-pw",
         "rt-y-bollard-j", "rt-y-elm", "rt-y-cart"]   # v06 scene.json ysort order
LAYERS = ["rt-base"] + YSORT
GUIDE = "walkmask-guide-hidden"
B, T = "sha256-bytes", "sha256-text-lf-v1"
INPUTS = {   # key -> (path relative to ROOT, hash algorithm, sha256); text = CRLF->LF before hashing
    "reference": ("outputs/style46/rpg-2-star-ocean-the-second_nyc-city-hall-park_common-style-reference_nonruntime-v01_20261022-183638-a4e273b9.png", B,
                  "1fce3a043fc9996ad7cbce8412cffedd79b63de68c53b0cf70f9da99b284c944"),
    "reference-provenance": ("outputs/style46/rpg-2-star-ocean-the-second_nyc-city-hall-park_reference-provenance_nonruntime-v01_20261022-183638-a4e273b9.json", T, None),
    **{k: (V06D + V06F % (k, "png"), B, None) for k in LAYERS + ["walkmask"]},
    "scene-json": (V06D + V06F % ("scene", "json"), T, None),
    "scene-tres": (V06D + V06F % ("scene", "tres"), T, None),
    "scene-module": ("outputs/style46/root/rpg-2-star-ocean-the-second_nyc-style46_v06-module-input-snapshot_v01_20261022-183638-a4e273b9.gd", T, None),
    "v05-writers": ("tools/rpg-2-star-ocean-the-second_chicago-loop_state-lake-block-pixel-author_unapproved-v05_20261017-234337-84862412.py", T,
                    "d4fa8a4f58140e46865339b0c9032883ec0e8399d674b246f047d014fb3428bb"),
}
PINS = {   # immutable v06 inputs + canonical module (equal in C at 3fd6cba), pinned at first assembly
    "rt-base": "d516b4c40412dc7d7ba92c9383c4558a3c893ea1d55a57fbd911d56728881317",
    "rt-y-lamps-pr": "c4113b5defe6f2810ffa7393c444a78b6e25f9d905e9ff6d566f806435480790",
    "rt-y-bollard-p": "c920b52873bb14f9a7dc802489ae0b1b0b681ff9efe5a2e8958827b26315aa83",
    "rt-y-lamp-ae": "ad7b3bea225f610005d7b980f0039f3414eeda3ef41fede11af908a568579fa6",
    "rt-y-fount": "a17fe30d6655a2224089e6e29d415080d964fa230415e03361124b1fda74842f",
    "rt-y-lamp-pe": "c31d4a33383c8fbd203d9c98db427653dceb05436e545899b47a4bb0592e31e6",
    "rt-y-lamp-pw": "90ec87700907da1a6dffd90910d7e5291ce24173fb21293a6f96359a720d141e",
    "rt-y-bollard-j": "c9d819a384773a6007838fef44f6df98219a303e15c3f070a75a6a900ae2e950",
    "rt-y-elm": "b643344f9ef25834458c9835e918fc00d0f858469445ae1c97d295b223070076",
    "rt-y-cart": "4722b825ffeca2a51f051755390a2d919c1a17f0c7c78d1e3820dfa321fa01f5",
    "walkmask": "674fb82d5f9ad3cd94971f5a41c780ee2369ad5453fc4c5555180b42a83be928",
    "scene-json": "f057872dc4b0d9fed41dcb19de0637084180a64631a1af0f360edc205270352c",
    "scene-tres": "8fee36f86bede6bcc92cdc1e441ead88b59c075edffe43c843871ea0599eb05d",
    "scene-module": "55e3c6238b004d55c218fa6cb6ce0a3a2f80780d2a3de4073017c213a326b70a",
    "reference-provenance": "b67c8ecac295de1d617001c254debcb36409598ca36f6a694cdc145c203d944c",
}
INPUTS = {k: (p, a, h or PINS[k]) for k, (p, a, h) in INPUTS.items()}


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
    if want is not None and got != want:
        raise SystemExit(f"input hash mismatch: {path}: {got} != {want}")
    return data



def load_writers():
    """v05 Chicago author imported unchanged for png_bytes/ora_bytes/pxo_bytes; its build() is never called."""
    read_input("v05-writers")
    spec = spec_from_file_location("chicago_author_v05_for_style46", ROOT / INPUTS["v05-writers"][0])
    mod = module_from_spec(spec)
    spec.loader.exec_module(mod)
    mod.PREFIX, mod.LAYERS, mod.GUIDE, mod.ZIP_TIME = PROJECT, LAYERS, GUIDE, ZIP_TIME
    return mod


v5 = load_writers()
W, H = v5.W, v5.H


def asset(purpose, ext):
    return f"{PROJECT}_style46-{purpose}_{VARIANT}_{TAG}.{ext}"


NAME = {k: asset(k, "png") for k in LAYERS + ["walkmask"]}
SCENE_JSON = asset("scene", "json")
SCENE_RES = asset("scene", "tres")
RES_DIR = "res://" + RUNTIME.relative_to(ROOT / "game").as_posix() + "/"


def rgba(data):
    return np.array(Image.open(io.BytesIO(data)).convert("RGBA"))


def tres_text(scene):
    """Same layout as the v06 .tres: compact sorted JSON in a Godot string (backslash and quote escaped)."""
    s = json.dumps(scene, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
    return '[gd_resource type="Resource" format=3]\n\n[resource]\nmetadata/scene_json = "' + \
        s.replace("\\", "\\\\").replace('"', '\\"') + '"\n'


def json_text(scene):
    return json.dumps(scene, indent=2, ensure_ascii=False) + "\n"


GAMEPLAY = ["canvas", "ui_rows", "hotspots", "legacy_positions", "canopy_reveal"]


def new_scene(old):
    scene = json.loads(json.dumps(old))
    by_file = {INPUTS[k][0].rsplit("/", 1)[1]: NAME[k] for k in LAYERS + ["walkmask"]}
    scene["run"] = f"style46_{TAG}"
    scene["source"] = ("STYLE46: generated common-style reference NEAREST-sampled to 640x360, cut by the v06 binary y-sort masks; "
                       "old v06 rt-base hidden under y-sort coverage; v06 walk mask bytes unchanged")
    scene["status"] = "UNAPPROVED candidate; art not accepted; opt-in --nyc-common-style46 only; not a default"
    scene["base"] = by_file[old["base"]]
    scene["walkmask"] = by_file[old["walkmask"]]
    for entry in scene["ysort"]:
        entry["png"] = by_file[entry["png"]]
    if [e["png"] for e in old["ysort"]] != [INPUTS[k][0].rsplit("/", 1)[1] for k in YSORT]:
        raise SystemExit("v06 ysort order differs from YSORT")
    strip = lambda s: {k: v for k, v in s.items() if k not in ("run", "source", "status", "base", "walkmask", "ysort")} | \
        {"ysort": [{k: v for k, v in e.items() if k != "png"} for e in s["ysort"]]}
    if strip(scene) != strip(old) or set(scene) != set(old) or any(k not in old for k in GAMEPLAY):
        raise SystemExit("gameplay fields changed")
    return scene


MODULE_EDITS = [
    ('const CLI_FLAG := "--city-hall-park-v06"\n',
     'const CLI_FLAG := "--city-hall-park-v06"\n'
     '# STYLE46 common-style candidate (UNAPPROVED, opt-in only): same scene data, new art files.\n'
     'const STYLE46_FLAG := "--nyc-common-style46"\n'
     f'const STYLE46_DIR := "{RES_DIR}"\n'
     f'const STYLE46_RES := "{SCENE_RES}"\n'),
    ('var source_dir := ""\n', 'var source_dir := ""\nvar runtime_dir := RUN_DIR\n'),
    ('\tif OS.get_cmdline_user_args().has(CLI_FLAG):\n',
     '\tif OS.get_cmdline_user_args().has(CLI_FLAG) or OS.get_cmdline_user_args().has(STYLE46_FLAG):\n'),
    ('\tsource_dir = dev_dir()\n\tvar json_text := ""\n\tif source_dir.is_empty():\n\t\tvar resource: Resource = load(RUN_DIR + SCENE_RES)\n',
     '\tsource_dir = dev_dir()\n\tvar style46 := OS.get_cmdline_user_args().has(STYLE46_FLAG)\n'
     '\truntime_dir = STYLE46_DIR if style46 else RUN_DIR\n\tvar json_text := ""\n\tif source_dir.is_empty():\n'
     '\t\tvar resource: Resource = load(runtime_dir + (STYLE46_RES if style46 else SCENE_RES))\n'),
    ('\t\tvar texture: Texture2D = load(RUN_DIR + file_name)\n', '\t\tvar texture: Texture2D = load(runtime_dir + file_name)\n'),
    ('\t\treturn load(RUN_DIR + file_name)\n', '\t\treturn load(runtime_dir + file_name)\n'),
]


def module_patch():
    old = read_input("scene-module").decode("utf-8").replace("\r\n", "\n")
    new = old
    for a, b in MODULE_EDITS:
        if new.count(a) != 1:
            raise SystemExit(f"module anchor not unique: {a!r}")
        new = new.replace(a, b)
    if "RUN_DIR + " in new.split("const SCENE_JSON", 1)[1].replace("runtime_dir := RUN_DIR", ""):
        raise SystemExit("a RUN_DIR load path was left unrouted")
    diff = difflib.unified_diff(old.splitlines(True), new.splitlines(True), f"a/{MODULE}", f"b/{MODULE}", n=0)
    return "".join(diff), text_sha(new.encode("utf-8"))


def build():
    ref = np.array(Image.open(io.BytesIO(read_input("reference"))).convert("RGBA"))
    if (ref[..., 3] != 255).any():
        raise SystemExit("reference has transparency")
    sh, sw = ref.shape[:2]
    sx, sy = (np.arange(W) * 2 + 1) * sw // (2 * W), (np.maximum(0, np.arange(H) - 24) * 2 + 1) * sh // (2 * H)
    conv = ref[sy][:, sx]
    raw = {k: read_input(k) for k in LAYERS + ["walkmask"]}
    old = {k: rgba(d) for k, d in raw.items()}
    if any(a.shape != (H, W, 4) for a in old.values()) or (old["rt-base"][..., 3] != 255).any():
        raise SystemExit("old layer size or opaque base differs")
    cover = np.zeros((H, W), bool)
    planes = {}
    for k in YSORT:
        m = old[k][..., 3]
        if not np.isin(m, (0, 255)).all():
            raise SystemExit(f"{k}: alpha not binary")
        p = np.zeros((H, W, 4), np.uint8)
        p[m == 255] = conv[m == 255]
        planes[k] = p
        cover |= m == 255
    base = conv.copy()
    base[cover] = old["rt-base"][cover]
    planes = {"rt-base": base, **planes}
    layers = {k: Image.fromarray(planes[k], "RGBA") for k in LAYERS}
    flat = Image.new("RGBA", (W, H))
    for k in LAYERS:
        flat.alpha_composite(layers[k])
    if not np.array_equal(np.array(flat), conv) or any(not np.array_equal(planes[k][..., 3], old[k][..., 3]) for k in YSORT):
        raise SystemExit("no-actor composite != converted reference, or a mask changed")
    old_json, old_tres = read_input("scene-json"), read_input("scene-tres")
    old_scene = json.loads(old_json)
    if json_text(old_scene).encode("utf-8") != old_json.replace(b"\r\n", b"\n") or \
            tres_text(old_scene).encode("utf-8") != old_tres.replace(b"\r\n", b"\n") or \
            json.loads(tres_text(old_scene).split('= "', 1)[1][:-2].replace('\\"', '"').replace("\\\\", "\\")) != old_scene:
        raise SystemExit("v06 .json/.tres layout not reproduced; formatter would drift")
    scene = new_scene(old_scene)
    patch, patched_sha = module_patch()
    guide = Image.open(io.BytesIO(raw["walkmask"])).convert("RGBA")
    files = {}

    def put(path, data, role):
        files[path.relative_to(ROOT).as_posix()] = (data, role)
    for k in LAYERS:
        put(RUNTIME / NAME[k], v5.png_bytes(layers[k]), f"runtime texture 640x360 RGBA for v06 purpose {k}")
    put(RUNTIME / NAME["walkmask"], raw["walkmask"], "walk mask: exact byte copy of the v06 walkmask")
    put(RUNTIME / SCENE_JSON, json_text(scene).encode("utf-8"), "scene data (dev-dir/audit twin of the .tres); v06 gameplay fields")
    put(RUNTIME / SCENE_RES, tres_text(scene).encode("utf-8"), "scene resource (metadata scene_json) loaded with --nyc-common-style46")
    put(OUT / asset("flat-640x360", "png"), v5.png_bytes(flat), "flat no-actor composite (= converted reference)")
    put(OUT / asset("scene-layers", "ora"), v5.ora_bytes(layers, guide, flat), "OpenRaster editable planes (11 layers)")
    pxo = io.BytesIO()
    with zipfile.ZipFile(io.BytesIO(v5.pxo_bytes(layers, guide, flat))) as zin, zipfile.ZipFile(pxo, "w", zipfile.ZIP_DEFLATED) as z:
        for info in zin.infolist():
            payload = zin.read(info.filename)
            if info.filename == "data.json":
                payload = payload.replace(b"chicago-loop-state-lake-v05", b"nyc-city-hall-park-style46-v01")
            z.writestr(zipfile.ZipInfo(info.filename, ZIP_TIME), payload, zipfile.ZIP_DEFLATED)
    put(OUT / asset("scene-layers", "pxo"), pxo.getvalue(), "Pixelorama editable planes (11 layers)")
    put(OUT / asset("module-flag-diff", "patch"), patch.encode("utf-8"),
        f"unified diff for {MODULE} (not applied here; root integrates)")
    is_text = lambda p: p.endswith((".patch", ".json", ".tres"))
    prov = read_input("reference-provenance")
    all_new = sorted(list(files) + [(OUT / asset("manifest", "json")).relative_to(ROOT).as_posix(),
                                    Path(__file__).resolve().relative_to(ROOT).as_posix()])
    manifest = {
        "project": "Worlds Between", "scene": "NYC City Hall Park (scifi.city), common-style candidate STYLE46",
        "status": "UNAPPROVED candidate; art not accepted; not a default; no existing game file, module, .tscn, ledger or Bible changed",
        "art_unapproved": True, "default_adopted": False,
        "approval_scope": "Creator approved the common science-scene style direction only; NYC final art/default not approved.",
        "authorship": "Generated raster (style46 image_gen reference) NEAREST-sampled; NOT hand pixel art. Assembled by Claude (Claude Code).",
        "generated_provenance": {"file": INPUTS["reference"][0], "sha256": INPUTS["reference"][2], "size": [sw, sh],
                                 "provenance_file": INPUTS["reference-provenance"][0], "provenance_sha256_text_lf": text_sha(prov),
                                 "tool": json.loads(prov.decode("utf-8")).get("tool")},
        "conversion": {"runtime_uv_row_offset": 24, "offset_reason": "Match unchanged fountain/walk geometry; first24 sampled rows repeat beneath the opaque header, bottom24 source rows drop below visible gameplay", "method": "NEAREST source-pixel sampling with runtime UV y-offset +24 logical pixels; src_y=floor((2*max(0,dst_y-24)+1)*src_height/(2*360))",
                       "native_size": [W, H], "source_columns_sample": sx[:6].tolist(), "source_rows_sample": sy[:6].tolist()},
        "hidden_plate": {"from": INPUTS["rt-base"][0], "pixels": int(cover.sum()), "share": round(float(cover.mean()), 4),
                         "note": "old v06 rt-base under the union of y-sort coverage; not shown in the no-actor composite; old art, not restyled"},
        "layers_bottom_to_top": LAYERS + [GUIDE + " (hidden, locked)"],
        "composite_check": "base + 9 y-sort (v06 order) == flat == converted reference (exact RGBA); y-sort alpha == v06 masks",
        "walk_mask": {"unchanged_bytes": True, "old": INPUTS["walkmask"][0], "new": (RUNTIME / NAME["walkmask"]).relative_to(ROOT).as_posix(),
                      "sha256": sha(raw["walkmask"])},
        "scene_data": {"gameplay_fields_identical": GAMEPLAY + ["ysort name/pivot/canopy order"],
                       "renamed": ["base", "walkmask", "ysort[].png"], "text_updated": ["run", "source", "status"],
                       "tres_format": "v06 layout reproduced byte-exact before writing (compact sorted JSON in metadata/scene_json)"},
        "purposes": {k: {"old": INPUTS[k][0], "new": (RUNTIME / NAME[k]).relative_to(ROOT).as_posix(), "res": RES_DIR + NAME[k]}
                     for k in LAYERS + ["walkmask"]},
        "module_patch": {"target": MODULE, "target_sha256_text_lf": text_sha(read_input("scene-module")),
                         "patched_sha256_text_lf": patched_sha, "flag": "--nyc-common-style46",
                         "behaviour": ["enabled_override still decides first", "flag makes enabled() true",
                                       "flag: load_scene loads STYLE46_DIR + STYLE46_RES and _image/_texture use runtime_dir = STYLE46_DIR",
                                       "no flag: runtime_dir = RUN_DIR and SCENE_RES (v06 unchanged)",
                                       "dev_dir (--chp6-dir=) precedence unchanged", "cmdline flag persists across battle return / scene reload",
                                       "no default/art-default bit, no resource takeover"],
                         "apply": "git apply --check then git apply (patch is LF; target is LF ASCII)"},
        "inputs": {k: {"file": p, "hash_algorithm": a, "sha256": h}
                   for k, (p, a, h) in INPUTS.items()},
        "toolchain": {"pillow": PIL.__version__, "numpy": np.__version__},
        "limitations": [
            "Art unapproved; generated-image pixel clusters, not native hand-placed pixels.",
            "Silhouette alignment of the generated reference to the v06 y-sort masks and walk mask is unproven; rims of the wrong surface may ride on planes.",
            "Hidden plate is old v06 art and could appear if a y-sort plane is ever not drawn or is reveal-dithered (tree-east-elm canopy reveal).",
            "Not run in Godot and not imported by the producer (stale checkout); root owns import, live bilingual/walk/battle/return checks.",
        ],
        "all_new_paths": all_new,
        "files": {p: {"sha256": text_sha(d) if is_text(p) else sha(d), "hash_algorithm": T if is_text(p) else B, "role": r}
                  for p, (d, r) in files.items()},
        "source": Path(__file__).resolve().relative_to(ROOT).as_posix(), "source_sha256_text_lf": text_sha(Path(__file__).read_bytes()),
    }
    put(OUT / asset("manifest", "json"), json_text(manifest).encode("utf-8"), "manifest")
    return files


def main():
    files = build()
    if "--check" in sys.argv[1:]:
        bad = [p for p, (d, _) in files.items() if not lp(ROOT / p).exists()
               or (lp(ROOT / p).read_bytes().replace(b"\r\n", b"\n") if p.endswith((".patch", ".json", ".tres")) else lp(ROOT / p).read_bytes()) != d]
        print(json.dumps({"check": "FAIL" if bad else "PASS", "files": len(files), "mismatched": bad}, indent=1))
        sys.exit(1 if bad else 0)
    for p, (data, _) in files.items():
        path = ROOT / p
        if path.parent not in (OUT, RUNTIME) or TAG not in path.name or (path.parent == OUT and "_style46-" not in path.name):
            raise SystemExit(f"refusing to write outside the STYLE46 scope: {p}")
        lp(path.parent).mkdir(parents=True, exist_ok=True)
        lp(path).write_bytes(data)
    print(json.dumps({"written": len(files), "files": sorted(files)}, indent=1))


if __name__ == "__main__":
    main()
