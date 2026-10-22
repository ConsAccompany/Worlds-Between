"""Washington, D.C. Capitol west ruins (scifi.ruins) STYLE45: native 640x360 source assembly from the generated
style43 common-style reference (UNAPPROVED candidate, not a default).

The creator approved the common science-scene style DIRECTION (warm stone/brass, cool soft shadows, grouped foliage,
restrained teal tech) only; Washington final art and its default are NOT approved. Method of the style42 tool:
  * Conversion: the 1672x941 generated reference is sampled once to 640x360 with NEAREST exact source-pixel sampling,
    src = floor((2*dst + 1) * src_size / (2 * 640|360)). No smoothing, filter, quantization, palette mapping or new
    pixels. It is generated raster, not hand-placed pixel art.
  * Planes: the current WDC runtime layers (v13 rt-base; v12 rt-fg, rt-walk, rt-ys-mast/tripod/beacon/elm) are reused
    as geometry. The five foreground planes (rt-fg + four y-sort) keep their exact binary alpha masks; their RGB is the
    converted reference. The base takes the converted reference except under foreground coverage, where it keeps the
    OLD v13 rt-base pixels as a hidden plate (old art, never seen in the no-actor composite).
  * Order: base, rt-ys-mast, rt-ys-tripod, rt-ys-beacon, rt-ys-elm (the v12 V12_YSORT order), rt-fg on top. The
    no-actor composite equals the converted reference exactly; the walk mask bytes are unchanged.
  * Silhouette alignment between the generated reference and the old masks is NOT proven; nothing here is approved art.
Editable sources: OpenRaster .ora + Pixelorama .pxo (1 base + 5 foreground + hidden locked walk guide = 7 layers) from
the imported v05 Chicago writers. Also writes the opt-in router script game/scripts/style45/*.gd.
Usage: python -X utf8 <this> [--check]   (--check rebuilds in memory and compares bytes; never writes)
"""
from __future__ import annotations

from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path
import hashlib
import io
import json
import re
import sys
import zipfile

import numpy as np
import PIL
from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
TAG = "20261022-182109-a780b895"
VARIANT = "unapproved-v01"
SUBJECT = "rpg-2-star-ocean-the-second_wdc-capitol-west_style45"
OUT = ROOT / "outputs" / "style45"
RUNTIME = ROOT / "game" / "assets" / "environments" / "style45"
ROUTER = ROOT / "game" / "scripts" / "style45" / f"{SUBJECT}-router_{VARIANT}_{TAG}.gd"
ZIP_TIME = (2026, 10, 22, 18, 21, 8)
V12D = "game/assets/environments/candidates/wdc-cw-v12_20261017-235608-66d00477/"
V12F = "rpg-2-star-ocean-the-second_wdc-capitol-west_%s_unapproved-v12_20261017-235608-66d00477.png"
V13 = "game/assets/environments/candidates/wdc-cw-v13_20261018-100938-075675cf/rpg-2-star-ocean-the-second_wdc-capitol-west_rt-base_unapproved-v13_20261018-100938-075675cf.png"
SEL = "game/scripts/rpg-2-star-ocean-the-second_wdc-capitol-west_exploration-opt-in-selector_unapproved-%s.gd"
YSORT = ["rt-ys-mast", "rt-ys-tripod", "rt-ys-beacon", "rt-ys-elm"]   # v12 V12_YSORT order
FG = YSORT + ["rt-fg"]
LAYERS = ["rt-base"] + FG
GUIDE = "rt-walk-guide-hidden"
B, T = "sha256-bytes", "sha256-text-lf-v1"
INPUTS = {   # key -> (path relative to ROOT, hash algorithm, sha256); text = CRLF->LF before hashing
    "reference": ("outputs/style43/rpg-2-star-ocean-the-second_wdc-capitol-west_common-style-reference_nonruntime-v01_20261022-180616-f9471bf4.png", B,
                  "8e3a1cb78b3ba7bd645fa7c0e3c57194fb62147079369d6dc7ae4a6bad7cafe4"),
    "reference-provenance": ("outputs/style43/rpg-2-star-ocean-the-second_wdc-capitol-west_style-reference-provenance_nonruntime-v01_20261022-180616-f9471bf4.json", T, None),
    "rt-base": (V13, B, "cf1768928c964b306c2106573241b66eb86937f5bfcb88bd9bbca887974719d9"),
    "rt-fg": (V12D + V12F % "rt-fg", B, "74cf02cd48ce328679ccd262486707ae8b5db106a954c58eb91974975087893c"),
    "rt-walk": (V12D + V12F % "rt-walk", B, "40feec7301d62b16db63afd25e44b71f3e7ebe4d32805847451e3a533ee3c0d9"),
    "rt-ys-mast": (V12D + V12F % "rt-ys-mast", B, "fb784e18de7167042059356f46ff71bb1f528057e4f8dfbae1f0a041e345a42b"),
    "rt-ys-tripod": (V12D + V12F % "rt-ys-tripod", B, "b341224c9691b184b7ee7c89d14bfc4f3801d6d051527d998f24a18aafe6f6b0"),
    "rt-ys-beacon": (V12D + V12F % "rt-ys-beacon", B, "a2d054d05b5c98bde80afc5e40e2fdaa430b0bed61521c6aece7f089d6d28bbb"),
    "rt-ys-elm": (V12D + V12F % "rt-ys-elm", B, "139cb25883f4f249cdf327f51aa46f4e5bcbf3d38327bc314929da65e328e398"),
    "v12-unused-base": (V12D + V12F % "rt-base", B, "60474fcec7ad22e5492f8f79373791872cfbcdd237342ef85acf576237aa1a22"),
    "selector-v13": (SEL % "v13_20261018-135539-63201688", T, "ecf2fba2f2f89a92220abcd2f8ea8a966b814a4216e0046be02418d6497b2c30"),
    "selector-v12r2": (SEL % "v12r2_20261018-042200-7c1e5b39", T, "18cf5e307a31a245d8ad186bf6fb3edb4125d0fbaa8bcaad6b3798a01c9079e7"),
    "selector-v12r1": (SEL % "v12r1_20261018-034933-23596520", T, "4f64abb5a50531ae6a47a01b201164e2f84d80f0acbdf76041a7920d9847587f"),
    "selector-v12": (SEL % "v12_20261017-235608-66d00477", T, "34e017bfd281de4b6dc5be735824b4620a10fefda166b147cc2038dbe1dc0415"),
    "v05-writers": ("tools/rpg-2-star-ocean-the-second_chicago-loop_state-lake-block-pixel-author_unapproved-v05_20261017-234337-84862412.py", T,
                    "d4fa8a4f58140e46865339b0c9032883ec0e8399d674b246f047d014fb3428bb"),
}


def sha(data):
    return hashlib.sha256(data).hexdigest()


def text_sha(data):
    return sha(data.replace(b"\r\n", b"\n"))


def lp(path):
    return Path("\\\\?\\" + str(Path(path).resolve()))


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
    spec = spec_from_file_location("chicago_author_v05_for_style45", ROOT / INPUTS["v05-writers"][0])
    mod = module_from_spec(spec)
    spec.loader.exec_module(mod)
    mod.PREFIX, mod.LAYERS, mod.GUIDE, mod.ZIP_TIME = SUBJECT, LAYERS, GUIDE, ZIP_TIME
    return mod


v5 = load_writers()
W, H = v5.W, v5.H
NAME = {k: f"{SUBJECT}-{k}_{VARIANT}_{TAG}.png" for k in LAYERS + ["rt-walk"]}
RES = {k: "res://" + (RUNTIME / NAME[k]).relative_to(ROOT / "game").as_posix() for k in LAYERS}


def rgba(data):
    return np.array(Image.open(io.BytesIO(data)).convert("RGBA"))


def selector_aliases():
    """The live selectors resolve rt-base to the v13 file and the other purposes to the v12 files read here."""
    v12 = read_input("selector-v12").decode("utf-8")
    v13 = read_input("selector-v13").decode("utf-8")
    d = re.search(r'const V12_DIR := "res://([^"]+)"', v12)[1]
    f = re.search(r'const V12_FILE := "([^"]+)"', v12)[1]
    base = re.search(r'const V13_BASE_PATH := "res://([^"]+)"', v13)[1]
    ys = re.findall(r'\["(rt-ys-[a-z]+)", \d+\]', re.search(r"const V12_YSORT := \[(.*)\]", v12)[1])
    got = {"rt-base": "game/" + base, **{k: "game/" + d + f % k for k in ["rt-fg", "rt-walk"] + ys}}
    if ys != YSORT or any(got[k] != INPUTS[k][0] for k in got):
        raise SystemExit(f"selector aliases do not resolve to the pinned inputs: {got}")
    for k in ("selector-v12r1", "selector-v12r2"):
        if "func _v12_path" in read_input(k).decode("utf-8"):
            raise SystemExit(f"{k} overrides _v12_path; router mapping would be bypassed")
    return got


ROUTER_TEXT = f'''extends "res://{INPUTS["selector-v13"][0][5:]}"

# Washington, D.C. ruins (scifi.ruins): STYLE45 common-style candidate router (UNAPPROVED; art not accepted, not a default).
# Off unless `-- --wdc-common-style45` is given. Without it, _ready() and _v12_path() hand straight to the v13
# selector, so every existing flag, override and the sdef35 default policy behave exactly as before.
# With the flag and AppState.current_destination_id == "scifi.ruins", v13 (and through it v12r2/v12r1/v12) is forced
# on for this _ready() only (v13_override is restored afterwards), and the base, the foreground and the four Y-sorted
# textures come from game/assets/environments/style45/. The walk mask stays the original v12 rt-walk file; camera,
# movement, interactions, dialogue, save, battle and return are the selector's own code. Cmdline args persist, so the
# flag also applies when the scene reloads on a real battle return.
# Art: generated style43 reference NEAREST-sampled to 640x360 and cut by the old binary masks (generated raster, no
# hand pixel art); old v13 rt-base pixels sit hidden under foreground coverage; silhouette alignment is unproven.
# Source: tools/{Path(__file__).name}
# To remove: point game/scenes/scifi_exploration_area.tscn back at the v13 selector.

const STYLE45_FLAG := "--wdc-common-style45"
const STYLE45_TEXTURES := {{
{chr(10).join(f'	"{k}": "{RES[k]}",' for k in LAYERS)}
}}

var style45_active := false


func _ready() -> void:
	if not (OS.get_cmdline_user_args().has(STYLE45_FLAG) and AppState.current_destination_id == "scifi.ruins"):
		super()
		return
	style45_active = true
	var saved := v13_override
	v13_override = 1
	super()
	v13_override = saved
	style45_active = v13_active


func _v12_path(purpose: String) -> String:
	if style45_active and STYLE45_TEXTURES.has(purpose):
		return String(STYLE45_TEXTURES[purpose])
	return super(purpose)
'''


def build():
    aliases = selector_aliases()
    ref = np.array(Image.open(io.BytesIO(read_input("reference"))).convert("RGBA"))
    if (ref[..., 3] != 255).any():
        raise SystemExit("reference has transparency")
    sh, sw = ref.shape[:2]
    sx, sy = (np.arange(W) * 2 + 1) * sw // (2 * W), (np.arange(H) * 2 + 1) * sh // (2 * H)
    conv = ref[sy][:, sx]
    old = {k: rgba(read_input(k)) for k in LAYERS + ["rt-walk"]}
    if any(a.shape != (H, W, 4) for a in old.values()) or (old["rt-base"][..., 3] != 255).any():
        raise SystemExit("old layer size or opaque base differs")
    cover = np.zeros((H, W), bool)
    planes = {}
    for k in FG:
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
    if not np.array_equal(np.array(flat), conv) or any(not np.array_equal(planes[k][..., 3], old[k][..., 3]) for k in FG):
        raise SystemExit("no-actor composite != converted reference, or a mask changed")
    walk_bytes = read_input("rt-walk")
    guide = Image.open(io.BytesIO(walk_bytes)).convert("RGBA")
    files = {}

    def put(path, data, role):
        files[path.relative_to(ROOT).as_posix()] = (data, role)
    for k in LAYERS:
        put(RUNTIME / NAME[k], v5.png_bytes(layers[k]), f"runtime texture 640x360 RGBA for purpose {k}")
    put(RUNTIME / NAME["rt-walk"], walk_bytes, "walk mask: exact byte copy of v12 rt-walk (reference only; router keeps the original)")
    put(OUT / f"{SUBJECT}-flat-640x360_{VARIANT}_{TAG}.png", v5.png_bytes(flat), "flat no-actor composite (= converted reference)")
    put(OUT / f"{SUBJECT}-layered-source_{VARIANT}_{TAG}.ora", v5.ora_bytes(layers, guide, flat), "OpenRaster editable planes (7 layers)")
    pxo = io.BytesIO()
    with zipfile.ZipFile(io.BytesIO(v5.pxo_bytes(layers, guide, flat))) as zin, zipfile.ZipFile(pxo, "w", zipfile.ZIP_DEFLATED) as z:
        for info in zin.infolist():
            payload = zin.read(info.filename)
            if info.filename == "data.json":
                payload = payload.replace(b"chicago-loop-state-lake-v05", b"wdc-capitol-west-style45-v01")
            z.writestr(zipfile.ZipInfo(info.filename, ZIP_TIME), payload, zipfile.ZIP_DEFLATED)
    put(OUT / f"{SUBJECT}-layered-source_{VARIANT}_{TAG}.pxo", pxo.getvalue(), "Pixelorama editable planes (pxo_version 7, 7 layers)")
    put(ROUTER, ROUTER_TEXT.encode("utf-8"), "opt-in router script extending the v13 selector (flag --wdc-common-style45)")
    is_text = lambda p: p.endswith(".gd")
    prov = read_input("reference-provenance")
    manifest = {
        "project": "Worlds Between", "scene": "Washington, D.C. Capitol west ruins (scifi.ruins), abandoned Capitol collapse",
        "status": "UNAPPROVED candidate; art not accepted; default false; no existing game file, selector, .tscn, ledger or Bible changed",
        "art_unapproved": True, "default_adopted": False,
        "approval_scope": "Creator approved the common science-scene style direction only; Washington final art/default not approved.",
        "authorship": "Generated raster (style43 image_gen reference) NEAREST-sampled; no hand pixel art. Assembled by Claude (Claude Code).",
        "generated_provenance": {"file": INPUTS["reference"][0], "sha256": INPUTS["reference"][2], "size": [sw, sh],
                                 "provenance_file": INPUTS["reference-provenance"][0], "provenance_sha256_text_lf": text_sha(prov),
                                 "tool": json.loads(prov.decode("utf-8")).get("tool")},
        "conversion": {"method": "NEAREST exact source-pixel sampling, src = floor((2*dst+1)*src_size/(2*dst_size))",
                       "native_size": [W, H], "source_columns_sample": sx[:6].tolist(), "source_rows_sample": sy[:6].tolist()},
        "hidden_plate": {"from": INPUTS["rt-base"][0], "pixels": int(cover.sum()), "share": round(float(cover.mean()), 4),
                         "note": "old v13 rt-base under foreground coverage; not shown in the no-actor composite; old art, not restyled"},
        "layers_bottom_to_top": LAYERS + [GUIDE + " (hidden, locked)"],
        "composite_check": "base + 4 y-sort + fg == flat == converted reference (exact RGBA); fg/y-sort alpha == old masks",
        "walk_mask": {"unchanged": True, "file": INPUTS["rt-walk"][0], "sha256": INPUTS["rt-walk"][2]},
        "selector_aliases": aliases,
        "purposes": {k: {"old": INPUTS[k][0], "new": (RUNTIME / NAME[k]).relative_to(ROOT).as_posix(), "res": RES[k]} for k in LAYERS}
                    | {"rt-walk": {"old": INPUTS["rt-walk"][0], "new": None, "note": "router keeps the original file"}},
        "old_paths": {INPUTS[k][0]: {"hash_algorithm": INPUTS[k][1], "sha256": INPUTS[k][2]} for k in LAYERS + ["rt-walk", "v12-unused-base"]},
        "inputs": {k: {"file": p, "hash_algorithm": a, "sha256": h or text_sha(prov)} for k, (p, a, h) in INPUTS.items()},
        "router": {"script": ROUTER.relative_to(ROOT).as_posix(), "flag": "--wdc-common-style45", "extends": INPUTS["selector-v13"][0],
                   "wiring": "not wired; root switches game/scenes/scifi_exploration_area.tscn after inspection"},
        "toolchain": {"pillow": PIL.__version__, "numpy": np.__version__},
        "limitations": [
            "Art unapproved; generated-image pixel clusters, not native hand-placed pixels.",
            "Silhouette alignment of the generated reference to the old v12/v13 masks is unproven; rims of the wrong surface may ride on planes.",
            "Hidden plate is old v13 art and could appear if a foreground plane is ever not drawn.",
            "Not run in Godot by the producer (no import/render in this stale checkout); root owns live bilingual/walk/battle/return checks.",
        ],
        "files": {p: {"sha256": text_sha(d) if is_text(p) else sha(d), "hash_algorithm": T if is_text(p) else B, "role": r}
                  for p, (d, r) in files.items()},
        "source": Path(__file__).resolve().relative_to(ROOT).as_posix(), "source_sha256_text_lf": text_sha(Path(__file__).read_bytes()),
    }
    put(OUT / f"{SUBJECT}-manifest_{VARIANT}_{TAG}.json", (json.dumps(manifest, indent=2, ensure_ascii=False) + "\n").encode("utf-8"), "manifest")
    return files


def main():
    files = build()
    if "--check" in sys.argv[1:]:
        bad = [p for p, (d, _) in files.items() if not lp(ROOT / p).exists()
               or (lp(ROOT / p).read_bytes().replace(b"\r\n", b"\n") if p.endswith((".gd", ".json")) else lp(ROOT / p).read_bytes()) != d]
        print(json.dumps({"check": "FAIL" if bad else "PASS", "files": len(files), "mismatched": bad}, indent=1))
        sys.exit(1 if bad else 0)
    for p, (data, _) in files.items():
        path = ROOT / p
        if path.parent not in (OUT, RUNTIME, ROUTER.parent) or TAG not in path.name:
            raise SystemExit(f"refusing to write outside the STYLE45 scope: {p}")
        lp(path.parent).mkdir(parents=True, exist_ok=True)
        lp(path).write_bytes(data)
    print(json.dumps({"written": len(files), "files": sorted(files)}, indent=1))


if __name__ == "__main__":
    main()
