"""UNAPPROVED, test-only, READ-ONLY: commit-closure and evidence check for two static pilots.

  female protagonist side-view battle static v08 (run 326522f8)   and   Liang Xu south idle static pilot v01 (run baa30d44)

Both pilots stay UNAPPROVED / NONRUNTIME (accepted full sprites 0/52, no animation). This tool writes nothing, runs no
Pixelorama or Godot, and does not import either author tool. It answers one question deterministically: does a checkout
(working tree or clean clone) hold every file a selective commit of the two packages needs, with the exact bytes the QA
notes, manifests and capture reports were made from?

Gates
  package_files_locked      every package file exists and matches its lock (sha256-bytes for .png/.pxo/.ora,
                            sha256-text-lf-v1 for text, so core.autocrlf=true and false clones both pass)
  dependencies_locked       every file the packages read or lock that is already in Git exists with the expected bytes
  v08_manifest / v08_captures         internal hashes, UNAPPROVED flags, capture geometry the QA note quotes
  liang_manifest / liang_capture_report  internal hashes, UNAPPROVED flags, 0/52, tool self-hash
  liang_reference_drift_known         the manifest's reference hashes differ from the checkout ONLY for the known set
                                      (the Game Bible state changed in 4245dd2 after the build); any new drift fails
  editables_independent     .pxo and .ora decoded here (not by the author tools): layer names/flags, hidden locked
                            guides, src-over composite of the visible layers == the PNG, binary alpha, cell size
  doc_paths_resolve         every full repo path or relative link cited by the four QA/audit docs exists
  liang_no_gendered_pronoun no he/him/his/she/her pronoun in the Liang package text, except the QA note's quoted
                            pronoun-inconsistency bullet
Reported only: Git tracked state of each file (in HEAD or to-be-added), external tools present, and whether
game/scripts/battle_arena.gd is the band-capable working-tree build the v08 band captures were made with.

Usage:  python -I -B <this file> [--root <checkout>]          exit 0 = PASS
"""
import argparse, hashlib, io, json, os, re, subprocess, sys, zipfile
import xml.etree.ElementTree as ET
import numpy as np
from PIL import Image

S = "rpg-2-star-ocean-the-second_"
F08 = "game/assets/characters/combat-sideview-pilots/" + S + "protagonist-female_sideview-idle-right-static-native0p65_"
CAP08 = "outputs/" + S + "protagonist-female_sideview-idle-right-static-native0p65_party-capture-"
LX = "game/assets/characters/liang-xu/south-idle-static-pilot-unapproved-v01/"
LXC = "_unapproved-v01_20261016-141751-bd083d0a"

V08_PNG = F08 + "unapproved-v08_20261016-095054-a06775a0.png"
V08_PXO = F08 + "editable-layers_unapproved-v08_20261016-095054-2574ce1c.pxo"
V08_ORA = F08 + "editable-layers_unapproved-v08_20261016-095054-314d939f.ora"
V08_MAN = F08 + "manifest_unapproved-v08_20261016-095054-ab653c87.json"
V08_CAPS = {"ruins": (CAP08 + "ruins_unapproved-v08_20261016-095054-a7962fdf.png",
                      CAP08 + "ruins-manifest_unapproved-v08_20261016-095054-1a83eade.json"),
            "outskirts": (CAP08 + "outskirts_unapproved-v08_20261016-095054-d9a8abaf.png",
                          CAP08 + "outskirts-manifest_unapproved-v08_20261016-095054-7dee7835.json")}
V08_QA = "docs/qa/" + S + "protagonist-female_battle-static-v08-game-scale-defect-pass_qa-note_unapproved-v01_20261016-095054-68ec4f17.md"
V08_AUDIT = "docs/qa/" + S + "protagonist-female_battle-static-v08-codex-visual-audit_unapproved-v01_20261016-145125-5e1b7d6c.md"
LX_PNG = LX + S + "liang-xu_south-idle-static-pilot_unapproved-v01_20261016-140940-46a036ed.png"
LX_PXO = LX + S + "liang-xu_south-idle-static-pilot-editable_unapproved-v01_20261016-140940-65edcfd2.pxo"
LX_PAL = LX + S + "liang-xu_south-idle-static-pilot-palette_unapproved-v01_20261016-140940-cda9b0c6.json"
LX_MAN = LX + S + "liang-xu_south-idle-static-pilot-manifest_unapproved-v01_20261016-140940-74be7552.json"
LX_TOOL = "tools/" + S + "liang-xu_south-idle-static-pilot-build-and-check_unapproved-v01_20261016-140940-6a60848d.py"
LX_REPORT = "outputs/" + S + "city-bright-dark_liang-xu-south-idle-static-pilot-capture-report" + LXC + ".json"
LX_CAPS = ["outputs/" + S + n + LXC + ".png" for n in (
    "city-bright_liang-xu-south-idle-static-pilot-h48", "city-bright_liang-xu-pilot-with-female-v8-benchmark-h48",
    "survey-annex-room2-dark_liang-xu-south-idle-static-pilot-h48",
    "survey-annex-room2-dark_liang-xu-pilot-with-female-v8-benchmark-h48")]
LX_QA = "docs/qa/" + S + "liang-xu_south-idle-static-pilot_48px-identity-qa-note_unapproved-v01_20261016-140940-d01e679f.md"
LX_AUDIT = "docs/qa/" + S + "liang-xu_south-idle-static-pilot-codex-visual-audit_unapproved-v01_20261016-145125-76c4ab13.md"
PIPELINE_DOC = "docs/design/" + S + "character-sprites_pixel-art-production-pipeline_unapproved-v01_20261015-040155-ffd3391d.md"
V8_SOUTH = ("game/assets/characters/pixelorama-pilots/" + S + "protagonist-female_south-idle-selout-v8-cloth-leather-"
            "candidate_m8-v08_20261015-021600-157a5ea0.png")
B, T = "sha256-bytes", "sha256-text-lf-v1"

# Files a selective commit must add (all untracked at HEAD 4245dd2 when this tool was written).
PACKAGES = {
    "female-battle-static-v08": [
        ("tools/" + S + "protagonist-female_sideview-battle-idle-right-native-0p65-author_unapproved-v08_20261016-095054-326522f8.py", T, "67af475bc9642d40b97117b9358768d4354d742913202676cc231d80c194283b"),
        ("tools/" + S + "protagonist-female_sideview-battle-static-v07-vs-v08-region-measure_unapproved-v08_20261016-095054-c2a29cc3.py", T, "e0e1d252f4a95b942aafdd07b117167604c15f3c903debd2d2fed3025d86823c"),
        (V08_PNG, B, "edee2924e1058fa2058f04ea2d507f744e97c93999c6183bf7b7730c51d0adc5"),
        (V08_PXO, B, "bf7111a24953699ca966fc5f68bc5f8512456f64a4c0578e99f64df2d04544cb"),
        (V08_ORA, B, "818e4bd4e0618a42d8680033a3d92b8a28ad660cee4cda3e488c0598e6048e34"),
        (V08_MAN, T, "8ec39ef6ac086507c4061d9976100ce4954fc9856a6bfabce9e6a926a903814b"),
        (V08_CAPS["ruins"][0], B, "2865e4d5460c4448723a0a242560d08d944ede037ca63f0a75479a4460f1f55d"),
        (V08_CAPS["ruins"][1], T, "ee2d29ed924ef6044c733f85749b3bc54d665b20e8dacbe9b3679f513d24fd40"),
        (V08_CAPS["outskirts"][0], B, "19c5677e2766868905ed509770ea106cb2e98b939f08193e6a4a275a60c95e56"),
        (V08_CAPS["outskirts"][1], T, "0e5a691793dec07622a381692c4413f7503856fcee02f1964a650935af10feec"),
        (V08_QA, T, "1700f98a00caa6ebbde4f4daaa0600988b25c167a484fabefb63480e42f6acd4"),
        (V08_AUDIT, T, "6c558f2a19da77bc2166a9be5fa8dcc08a6b8cfa4043b9fd6757e6c586c23de6"),
    ],
    "liang-xu-south-static-v01": [
        (LX_TOOL, T, "a91cea8abfe3d4cc8b1028f69a53e004bc3cd72b6116c5a3d8298a1bfc56609b"),
        ("tools/" + S + "liang-xu_south-idle-static-pilot-godot-capture_unapproved-v01_20261016-140940-0e7a1c55.gd", T, "b553990b620edf795c88abee26511cdfb8a7b5a16e8fd1049d8465ed83af238f"),
        (LX + ".gdignore", T, hashlib.sha256(b"").hexdigest()),
        (LX_PNG, B, "9fee901809d33128839779cc1e926fc314f4d92fd11baa3b857d4cffebfe38ab"),
        (LX_PXO, B, "26024bdd2c2d16b29c6a0e5df63a17038d29829506f505f0ca37f13a73ff09ee"),
        (LX_PAL, T, "6d0be31c634e113fcdbecdd655d7791f4b2f9e05f59487601d774cfd2f7e9c4f"),
        (LX_MAN, T, "5cd6fea99e3ba4d8298448d57c9b450185040f39a7f965020a70475521b0bcfa"),
        ("outputs/" + S + "liang-xu_south-idle-static-pilot-x4-nearest-preview_unapproved-v01_20261016-140940-3018cfc8.png", B, "6021596235fa7196539f6a763c0f4e3ed0c1641a721e157fa8b289ae935b4c35"),
        (LX_CAPS[0], B, "d2c340780ed6c8f1c8b4da9f538a647f93527d61a8e5ce68e08c1e44b7abdc20"),
        (LX_CAPS[1], B, "bc232b4158e261960b83b5d9536b0b0e831228a2f08a1fb0bd0b2bbd5e4fbbf1"),
        (LX_CAPS[2], B, "b8e6dc1898f7ace208285c6961bfb72a900cf5b76badd0f7ce9b41befcbea3b7"),
        (LX_CAPS[3], B, "72cab5f1feeb49293b89e5f1fca1f2081d6746b1a09ef8fc9092b486107a8423"),
        (LX_REPORT, T, "42919c83b400c790fce28ccc1da46308bb6581719f3ad64186ee7a8473434787"),
        (LX_QA, T, "b398d62adf6b3169508fd43c69e52bd86ec3d8a23dad968920875202aee98463"),
        (LX_AUDIT, T, "ccc2333d7a7942f8eceec5549660eeed3d2c06348567a03746a02f59cdfffd8d"),
        # untracked design doc the Liang manifest locks; without it the Liang `build` mode raises FileNotFoundError
        (PIPELINE_DOC, T, "100b428aceb2aef95794dec7e531cc1bad78904ae70d07dd366934b084c95766"),
    ],
}
# Already in Git at HEAD 4245dd2; read, locked or globbed by the package tools.
DEPENDENCIES = [
    (F08 + "unapproved-v07_20261016-070549-6711a51d.png", B, "b6b26f4085696d3d77f300b827497e703c30b6d73b3e8c439007670c3a48b3cb", "v08 author tool v07 lock"),
    (F08 + "editable-layers_unapproved-v07_20261016-070549-f6ab9173.pxo", B, "01b0b6fc4773ded5203ac7e30528767507fa5cc8e928eac7ce241dae39951e75", "v08 author tool v07 lock"),
    (F08 + "editable-layers_unapproved-v07_20261016-070549-c3e59c16.ora", B, "6072987caaa1eeb9a9fdcfa88092d36de5dc301b701cf195ce07d1b881d4732b", "v08 author tool v07 lock"),
    (F08 + "manifest_unapproved-v07_20261016-070549-04075564.json", T, "fb26fa64460d568307c009c3d30237062c6635fd9e9d2f6eb6759958844776f5", "v08 author tool v07 lock"),
    ("tools/" + S + "protagonist-female_sideview-battle-idle-right-native-0p65-author_unapproved-v07_20261016-070549-0e2efcac.py", T, "14b1303708e111e8eae37debe8badcc2498e4939b7be99e136d02344d633f812", "imported by the v07-vs-v08 measure tool"),
    (CAP08 + "ruins_unapproved-v07_20261016-070549-fedb99df.png", B, "56d7b1033452e5cdecb5b8ea73160faa84a4f60f83efda04158c22e8c219d82c", "globbed by the measure tool"),
    (CAP08 + "outskirts_unapproved-v07_20261016-070549-129e2621.png", B, "8a83a28352cb7b026dbd8d276695d65e105e845528e04ddc6895f43e62e89333", "globbed by the measure tool"),
    ("tools/" + S + "protagonist-female_sideview-battle-idle-right-native-0p65-party-capture-clean-clone_unapproved-v07r1_20261016-085133-1c89279f.gd", T, "2498b627927c141b61554ea3d538ea2ec7cdcd4100347efc20063394dc9830be", "v08 capture script (used unchanged)"),
    (V8_SOUTH, B, "ccf9d2a293e7f1b9c706b4d2f1bf9c00b3c7714ec4e9b8bddf023e166f68b6fd", "v08 coat reference; Liang S4 + capture benchmark lock"),
]
LIANG_KNOWN_REFERENCE_DRIFT = {"game_bible_state"}      # outputs/...game-bible_state...json changed in 4245dd2
BAND_ARENA_TEXT_LF = "be8859a8398ecc7d6744c6755e59924cafce43b0cb0f20f375ac32a28592acae"   # working-tree build used
PRONOUN = re.compile(r"\b(he|him|his|himself|she|her|hers|herself)\b", re.I)
PRONOUN_ALLOWED = [(LX_QA, "Pronoun inconsistency.")]   # the QA note quotes the conflicting sources on purpose
EXTERNAL = {"pixelorama_1_2_3": "work/tooling/pixelorama-1-2-3/Pixelorama-Windows-64bit/Pixelorama.exe",
            "godot_4_7_2": "work/tooling/godot-4-7-2/Godot_v4.7.2-stable_win64_console.exe"}

ROOT = None


def fs(rel):
    p = os.path.abspath(os.path.join(ROOT, *rel.split("/")))
    return p if os.name != "nt" or p.startswith("\\\\?\\") else "\\\\?\\" + p   # names exceed MAX_PATH on Windows


def exists(rel):
    return os.path.isfile(fs(rel))


def read(rel):
    with open(fs(rel), "rb") as f:
        return f.read()


def digest(data, alg):
    return hashlib.sha256(data if alg == B else data.replace(b"\r\n", b"\n")).hexdigest()


def rgba(data):
    im = Image.open(io.BytesIO(data))
    return im.mode, np.array(im.convert("RGBA"))


def over(layers, shape):
    out = np.zeros(shape, np.uint8)
    for a in layers:                       # binary alpha: src-over == topmost opaque texel wins
        m = a[..., 3] > 0
        out[m] = a[m]
    return out


def git(*args):
    try:
        p = subprocess.run(["git", "-C", ROOT, *args], capture_output=True, text=True, timeout=60)
        return p.returncode, p.stdout
    except (OSError, subprocess.SubprocessError):
        return None, ""


def lock_table(entries):
    rows = {}
    for rel, alg, want, *_ in entries:
        got = digest(read(rel), alg) if exists(rel) else None
        rows[rel] = {"present": got is not None, "match": got == want, "algorithm": alg,
                     **({} if got == want else {"expected": want, "actual": got})}
    return rows


def pxo_check(rel, png_a, want_names):
    with zipfile.ZipFile(io.BytesIO(read(rel))) as z:
        d = json.loads(z.read("data.json"))
        w, h = d["size_x"], d["size_y"]
        names = [l["name"] for l in d["layers"]]
        vis = [l for l in d["layers"] if l.get("visible")]
        guides = d["layers"][-1]
        blobs = {l["name"]: np.frombuffer(z.read(f"image_data/frames/1/layer_{i + 1}"), np.uint8).reshape(h, w, 4)
                 for i, l in enumerate(d["layers"])}
    comp = over([blobs[l["name"]] for l in vis], (h, w, 4))
    opaque = [blobs[l["name"]][..., 3] > 0 for l in vis]
    overlap = int((np.sum(opaque, axis=0) > 1).sum())
    return {"size": [w, h], "pxo_version": d["pxo_version"], "layers": len(names), "names_match": names == want_names,
            "guides_last_hidden_locked": guides["name"] == "guides" and not guides["visible"] and guides["locked"],
            "visible_layers": len(vis), "composite_equals_png": comp.tobytes() == png_a.tobytes(),
            "texels_covered_by_more_than_one_layer": overlap}, blobs


def ora_check(rel, png_a, pxo_blobs):
    with zipfile.ZipFile(io.BytesIO(read(rel))) as z:
        first = z.infolist()[0]
        stack = ET.fromstring(z.read("stack.xml"))
        layers = list(stack.iter("layer"))[::-1]           # stack.xml lists top first
        imgs = {l.get("name"): rgba(z.read(l.get("src")))[1] for l in layers}
    vis = [l.get("name") for l in layers if l.get("visibility") == "visible"]
    comp = over([imgs[n] for n in vis], png_a.shape)
    return {"mimetype_first_stored": first.filename == "mimetype" and first.compress_type == zipfile.ZIP_STORED,
            "layers": len(layers), "guides_hidden": any(l.get("name") == "guides" and l.get("visibility") == "hidden"
                                                         for l in layers),
            "composite_equals_png": comp.tobytes() == png_a.tobytes(),
            "layers_equal_pxo_layers": all(imgs[n].tobytes() == pxo_blobs[n].tobytes() for n in vis)}


def png_stats(a):
    al = np.unique(a[..., 3]).tolist()
    op = a[..., 3] > 0
    return {"size": [a.shape[1], a.shape[0]], "alpha_values": al, "opaque_texels": int(op.sum()),
            "colours": int(len(np.unique(a[op][:, :3], axis=0))),
            "border_clear": bool(not op[0].any() and not op[-1].any() and not op[:, 0].any() and not op[:, -1].any())}


def doc_paths(rel):
    """Full repo paths in backticks/links, and relative markdown links, cited by a doc."""
    text = read(rel).decode("utf-8")
    base = os.path.dirname(rel)
    found = set()
    for m in re.finditer(r"\]\(([^)\s]+)\)", text):
        target = m.group(1).split("#")[0]
        if target and "://" not in target:
            found.add(os.path.normpath(os.path.join(base, target)).replace("\\", "/"))
    for m in re.finditer(r"(?<![\w./…-])((?:game|tools|outputs|docs)/[\w./-]+\.(?:png|pxo|ora|json|md|py|gd|tscn))", text):
        found.add(m.group(1))
    return sorted(p for p in found if "…" not in p and "..." not in p and "<" not in p)


def main():
    global ROOT
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--root", default=os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
    ROOT = os.path.abspath(ap.parse_args().root)
    rep, g = {"status": "UNAPPROVED test-only read-only closure check; nothing written", "root": ROOT}, {}

    pk = {name: lock_table(entries) for name, entries in PACKAGES.items()}
    dep = lock_table(DEPENDENCIES)
    rep["package_files"], rep["dependencies"] = pk, dep
    g["package_files_locked"] = all(r["match"] for t in pk.values() for r in t.values())
    g["dependencies_locked"] = all(r["match"] for r in dep.values())
    if not (g["package_files_locked"] and g["dependencies_locked"]):
        rep["gates"], rep["result"] = g, "FAIL"
        print(json.dumps(rep, indent=1))
        return 1

    # female battle static v08
    man = json.loads(read(V08_MAN))
    f = man["files"]
    g["v08_manifest"] = (f["png"]["file"] == V08_PNG and f["pxo"]["file"] == V08_PXO and f["ora"]["file"] == V08_ORA
                         and f["png"]["sha256"] == digest(read(V08_PNG), B) and f["pxo"]["sha256"] == digest(read(V08_PXO), B)
                         and f["ora"]["sha256"] == digest(read(V08_ORA), B)
                         and man["art_approved"] is False and man["runtime_integrated"] is False
                         and man["animation"] is False and man["game_bible_or_acceptance_counters_changed"] is False
                         and all(dep[k]["match"] and digest(read(k), B if not k.endswith(".json") else T) == v
                                 for k, v in man["refines"]["files"].items()))
    caps = {}
    for arena, (png_rel, man_rel) in V08_CAPS.items():
        c = json.loads(read(man_rel))
        m = c["measurement"]
        caps[arena] = {
            "capture_sha_matches": c["captureSha256"] == digest(read(png_rel), B),
            "candidate_is_v08_png": c["candidateSha256"] == digest(read(V08_PNG), B),
            "arena": c["arena"] == arena and c["arenaMode"] == "arena-override-band",
            "battle_arena_build": c["battleArenaScriptSha256Bytes"],
            "disc_not_drawn": c["controlledFighterDiscDrawn"] is False, "acceptance_0": c["artAcceptanceCount"] == 0,
            "crown_422_sole_543_61px": (m["crownScreenY"], m["soleScreenYInclusive"], m["crownToSoleLogicalPx"]) == (422, 543, 61.0),
            "nearest_5452_of_5452": (m["nearestPredictionMatchPx"], m["expectedSpritePixels"]) == (5452, 5452),
            "off_palette_0": m["offPaletteSpritePixels"] == 0,
            "liang_gap_10_no_overlap": (m["companionOverlap"]["liang-xu"]["bboxGapScreenPx"],
                                        m["companionOverlap"]["liang-xu"]["opaqueOnOpaqueScreenPx"]) == (10, 0),
            "png_1280x720": rgba(read(png_rel))[1].shape[:2] == (720, 1280)}
    rep["v08_captures"] = caps
    g["v08_captures"] = all(v for c in caps.values() for k, v in c.items() if k != "battle_arena_build") and all(
        c["battle_arena_build"] == BAND_ARENA_TEXT_LF for c in caps.values())
    mode, a08 = rgba(read(V08_PNG))
    want08 = [l["name"] for l in man["layers_bottom_to_top"]]          # 18 art layers, then "guides"
    px08, blobs08 = pxo_check(V08_PXO, a08, want08)
    ora08 = ora_check(V08_ORA, a08, blobs08)
    st08 = png_stats(a08)
    rep["v08_editables"] = {"png": {"mode": mode, **st08}, "pxo": px08, "ora": ora08}
    ok08 = (mode == "RGBA" and st08["size"] == [68, 72] and st08["alpha_values"] == [0, 255] and st08["border_clear"]
            and st08["colours"] <= 32 and px08["size"] == [68, 72] and px08["layers"] == 19 and px08["visible_layers"] == 18
            and px08["names_match"] and px08["guides_last_hidden_locked"] and px08["composite_equals_png"]
            and ora08["mimetype_first_stored"] and ora08["layers"] == 19 and ora08["guides_hidden"]
            and ora08["composite_equals_png"] and ora08["layers_equal_pxo_layers"])

    # Liang Xu south idle static v01
    lm = json.loads(read(LX_MAN).decode("utf-8"))
    lf = lm["files"]
    g["liang_manifest"] = (lf["png"]["sha256"] == digest(read(LX_PNG), B) and lf["pxo"]["sha256"] == digest(read(LX_PXO), B)
                           and lf["palette"]["sha256"] == digest(read(LX_PAL), T)
                           and lm["tool"]["file"] == LX_TOOL and lm["tool"]["sha256"] == digest(read(LX_TOOL), T)
                           and lm["art_approved"] is False and lm["human_reviewed"] is False
                           and lm["runtime_integrated"] is False and "no animation" in lm["status"]
                           and lm["acceptance_counters_unchanged"]["runtime_exploration_sprites_accepted"] == "0/52")
    drift = {}
    for k, v in lm["references"].items():
        got = digest(read(v["file"]), v["hash_algorithm"]) if exists(v["file"]) else None
        if got != v["sha256"]:
            drift[k] = {"file": v["file"], "manifest": v["sha256"], "checkout": got}
    rep["liang_reference_drift"] = drift
    g["liang_reference_drift_known"] = set(drift) <= LIANG_KNOWN_REFERENCE_DRIFT and all(
        d["checkout"] is not None for d in drift.values())
    cr = json.loads(read(LX_REPORT).decode("utf-8"))
    cap_rows = {c["capture"]: c["capture_sha256"] for c in cr["captures"]}
    rep["liang_capture_report"] = {"captures_listed": sorted(cap_rows), "sources": cr["sources"]}
    g["liang_capture_report"] = (cr["sources"]["liang"]["sha256"] == digest(read(LX_PNG), B)
                                 and cr["sources"]["female-v8-benchmark"]["sha256"] == digest(read(V8_SOUTH), B)
                                 and sorted(cap_rows) == sorted(LX_CAPS)
                                 and all(cap_rows[p] == digest(read(p), B) for p in LX_CAPS)
                                 and all(rgba(read(p))[1].shape[:2] == (720, 1280) for p in LX_CAPS)
                                 and cr["art_approved"] is False and cr["human_reviewed"] is False
                                 and cr["acceptance_counters_unchanged"]["runtime_exploration_sprites_accepted"] == "0/52")
    lmode, alx = rgba(read(LX_PNG))
    stlx = png_stats(alx)
    wantlx = [l["name"] for l in lf["pxo"]["layers_bottom_to_top"]]
    pxlx, _ = pxo_check(LX_PXO, alx, wantlx)
    pal = json.loads(read(LX_PAL).decode("utf-8"))
    declared = {tuple(int(e["hex"][i:i + 2], 16) for i in (1, 3, 5)) for r in pal["ramps"].values() for e in r}
    used = {tuple(c) for c in np.unique(alx[alx[..., 3] > 0][:, :3], axis=0).tolist()}
    rep["liang_editables"] = {"png": {"mode": lmode, **stlx}, "pxo": pxlx,
                              "palette": {"declared": len(declared), "used": len(used), "equal": declared == used},
                              "gdignore_empty": read(LX + ".gdignore") == b""}
    oklx = (lmode == "RGBA" and stlx["size"] == [80, 112] and stlx["alpha_values"] == [0, 255] and stlx["border_clear"]
            and stlx["opaque_texels"] == 2471 and pxlx["size"] == [80, 112] and pxlx["layers"] == 10
            and pxlx["visible_layers"] == 9 and pxlx["names_match"] and pxlx["guides_last_hidden_locked"]
            and pxlx["composite_equals_png"] and pxlx["texels_covered_by_more_than_one_layer"] == 0
            and declared == used and len(declared) == 33 and read(LX + ".gdignore") == b"")
    g["editables_independent"] = ok08 and oklx

    # documents
    docs = {}
    for d in (V08_QA, V08_AUDIT, LX_QA, LX_AUDIT):
        paths = doc_paths(d)
        docs[d] = {"cited": len(paths), "missing": [p for p in paths if not exists(p)]}
    rep["doc_paths"] = docs
    g["doc_paths_resolve"] = all(not v["missing"] for v in docs.values())
    hits = []
    for rel in (LX_QA, LX_AUDIT, LX_MAN, LX_PAL, LX_REPORT):
        for n, line in enumerate(read(rel).decode("utf-8").splitlines(), 1):
            if PRONOUN.search(line) and not any(rel == r and key in line for r, key in PRONOUN_ALLOWED):
                hits.append(f"{rel}:{n}")
    rep["liang_pronoun_hits_outside_allowed_quote"] = hits
    g["liang_no_gendered_pronoun"] = not hits

    # reported only
    rc, _ = git("rev-parse", "--verify", "HEAD")
    if rc == 0:
        tracked = {}
        for name, entries in PACKAGES.items():
            tracked[name] = {"in_HEAD": [], "not_in_HEAD": []}
            for rel, *_ in entries:
                rc2, _ = git("cat-file", "-e", f"HEAD:{rel}")
                tracked[name]["in_HEAD" if rc2 == 0 else "not_in_HEAD"].append(rel)
        rep["git"] = {"HEAD": git("rev-parse", "--short", "HEAD")[1].strip(), "packages": tracked,
                      "dependencies_not_in_HEAD": [rel for rel, *_ in DEPENDENCIES if git("cat-file", "-e", f"HEAD:{rel}")[0] != 0]}
        g["dependencies_in_HEAD"] = not rep["git"]["dependencies_not_in_HEAD"]
    arena = "game/scripts/battle_arena.gd"
    ba = digest(read(arena), T) if exists(arena) else None
    rep["battle_arena_gd"] = {"sha256_text_lf": ba, "band_capable_build_used_by_v08_captures": ba == BAND_ARENA_TEXT_LF,
                              "note": "v08 band captures reproduce byte-identically only with this build; with HEAD's "
                                      "battle_arena.gd the committed v07r1 script falls back to head-geometric-backdrop"}
    rep["external_tools_present"] = {k: exists(v) for k, v in EXTERNAL.items()}
    rep["gates"] = g
    rep["result"] = "PASS" if all(g.values()) else "FAIL"
    print(json.dumps(rep, indent=1, ensure_ascii=False))
    return 0 if rep["result"] == "PASS" else 1


if __name__ == "__main__":
    sys.exit(main())
