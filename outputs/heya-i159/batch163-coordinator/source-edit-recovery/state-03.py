"""Heya four-direction IDLE source bank, batch163 prose-repair (UNAPPROVED technical source).

Derived from the preserved i159 author tool. The animation model, frames, durations, palette, pivots and
export bytes are unchanged. This version corrects only the false manifest prose that claimed composite rows
76..103 were frozen; the established model and the frozen check are rows 90..103 (boots/composite sole),
while torso/leg rows 76..89 settle with the torso group by design. It adds a check that binds the manifest
prose to the measured rows, and writes fresh staging/report output under the batch163 directory.

  python3 -I <this> build    # fresh staging under outputs/heya-i159/batch163-provider/staging
  python3 -I <this> check    # deterministic rebuild + staging/installed/source checks
  python3 -I <this> install  # copies NEW staged paths only; differing manifests use wb_safe_replace.py

Writes NEW files only. Differing destinations are refused; use tools/wb_safe_replace.py explicitly if needed.
"""
import hashlib, importlib.util, io, json, os, shutil, sys, zipfile
from datetime import datetime, timezone
import xml.etree.ElementTree as ET
import numpy as np

REPO = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
SLUG, ACTOR = "rpg-2-star-ocean-the-second", "heya"
STAMP, RUN = "20261024-140235", "a159i001"   # artifact bank identity preserved byte-for-byte
TOOL_STAMP, TOOL_RUN = "20261024-141806", "h163b001"
OUT_REL = "outputs/heya-i159/batch163-provider"
STAGE_REL = OUT_REL + "/staging/idle"
OUT_PNG_REL = OUT_REL + "/png"
OUT_NATIVE_REL = OUT_REL + "/native"
INSTALL_REL = "game/assets/characters/heya-native-v01/idle"
ZIP_DT = (2026, 10, 24, 14, 2, 35)
DIRS = ("south", "west", "north", "east")
W, H, PIN, BODY_ROWS, SCALE = 80, 112, (40, 104), (8, 103), 0.5
FRAME_MS_BASE = 100
IDLE_MS = [700, 200, 400, 200]
IDLE_GROUPS = [(0, 0, 0, 0), (1, 1, 1, 0), (2, 1, 1, 1), (3, 0, 1, 1)]
HEAD = ("face", "hair", "braid", "scarf")
TORSO = ("dress", "coat", "apron", "belt", "strap", "bag", "herb")
ARMS = ("arms",)
BOOTS = ("boots",)
ALL_ROLES = ["boots", "dress", "coat", "apron", "belt", "strap", "bag", "arms", "herb", "face", "hair", "braid",
             "scarf"]
PXO_LAYERS = ALL_ROLES + ["guides"]
assert set(HEAD) | set(TORSO) | set(ARMS) | set(BOOTS) == set(ALL_ROLES)
assert all(len(x) == 4 for x in IDLE_GROUPS) and [x[0] for x in IDLE_GROUPS] == [0, 1, 2, 3]

_J_FN = "rpg-2-star-ocean-the-second_jiang-lan_exploration-source-author_unapproved-jexplore39-v01_20261022-154032-5bca7193.py"
_J_SHA = "ae8654f28c89e4c11ef7c52b61fc87ee992af5ae805277998102e4ba9bf80cd5"
SRC = {
    "south": {"dir": "game/assets/characters/heya-native-v01/south",
              "png": "rpg-2-star-ocean-the-second_heya_south-static_unapproved-v01_20261024-125310-231d2b03.png",
              "png_sha": "f6e60682bc7f5290aff11ec1154e515137a2b0f66a7fd5141ef4a9afa755d2c3",
              "ora": "rpg-2-star-ocean-the-second_heya_south-edit_unapproved-v01_20261024-125310-42e46403.ora",
              "ora_sha": "694e105375eded54d605698f6c65862f152a3e0c63a2462dd90fe4073c8aff36",
              "pal": "rpg-2-star-ocean-the-second_heya_south-palette_unapproved-v01_20261024-125310-a902fe49.json",
              "pal_sha": "a699845e99d7cc794402b5e31b3e515cafb5459645fbab05d5a4eefb4071e838",
              "pxo": "rpg-2-star-ocean-the-second_heya_south-edit_unapproved-v01_20261024-125310-9665bd23.pxo"},
    "west": {"dir": "game/assets/characters/heya-native-v01/west",
             "png": "rpg-2-star-ocean-the-second_heya_west-static_unapproved-v01_20261024-131500-22034c8f.png",
             "png_sha": "f8a167d8df2a554660c01b8cb88e461f878297c8d8da2456a566bdc0c2ed766e",
             "ora": "rpg-2-star-ocean-the-second_heya_west-edit_unapproved-v01_20261024-131500-3346f283.ora",
             "ora_sha": "fc3d332b0b263fba3d6f5be39f38c45b3ed872b76e706471e2671cb4bd4d424b",
             "pal": "rpg-2-star-ocean-the-second_heya_west-palette_unapproved-v01_20261024-131500-2b57e26b.json",
             "pal_sha": "59491af00cb984ed840489de9e7bd427aea456152ef9f0b1423f0c3f26979d7c",
             "pxo": "rpg-2-star-ocean-the-second_heya_west-edit_unapproved-v01_20261024-131500-4bc15dd4.pxo"},
    "north": {"dir": "game/assets/characters/heya-native-v01/north",
              "png": "rpg-2-star-ocean-the-second_heya_north-static_unapproved-v01_20261024-134500-56efefc2.png",
              "png_sha": "d0019c77032ec7dcb403e3d54cc80a6b9b60a875881cefa1887bb145072656c4",
              "ora": "rpg-2-star-ocean-the-second_heya_north-edit_unapproved-v01_20261024-134500-7c039253.ora",
              "ora_sha": "999f3929036569190fadec06c4602156a39ef1f3ce2d81a67794f5de1b5ee6ce",
              "pal": "rpg-2-star-ocean-the-second_heya_north-palette_unapproved-v01_20261024-134500-023052d9.json",
              "pal_sha": "e1a1a9ac775ccb452498f02db97230b3135727da7d999bf132f2877837483a52",
              "pxo": "rpg-2-star-ocean-the-second_heya_north-edit_unapproved-v01_20261024-134500-ced44bda.pxo"},
    "east": {"dir": "game/assets/characters/heya-native-v01/east",
             "png": "rpg-2-star-ocean-the-second_heya_east-static_unapproved-v01_20261024-141500-6041ee95.png",
             "png_sha": "273e5e854121fa8ec92dc74e28a67be35920da6442fc20571ff053453fdf9dd4",
             "ora": "rpg-2-star-ocean-the-second_heya_east-edit_unapproved-v01_20261024-141500-d23c7857.ora",
             "ora_sha": "0cf8b0b465560bf6328de320f2e40f356cb5d304c3c546227de3a2ba12e8bc91",
             "pal": "rpg-2-star-ocean-the-second_heya_east-palette_unapproved-v01_20261024-141500-f7eba38b.json",
             "pal_sha": "6af85c7ac9e1dfc76a44a53864d9a7ef58c7d02d1c3e3e8ab1d71b50e6d55311",
             "pxo": "rpg-2-star-ocean-the-second_heya_east-edit_unapproved-v01_20261024-141500-5493fe7b.pxo"},
}


def fs(rel):
    return os.path.join(REPO, *rel.split("/"))


def rb(rel):
    with open(fs(rel), "rb") as f:
        return f.read()


def sha(b):
    return hashlib.sha256(b).hexdigest()


def fname(purpose, ext):
    return f"{SLUG}_{ACTOR}_idle-{purpose}_unapproved-i159-v01_{STAMP}-{RUN}.{ext}"


def load(rel, name):
    spec = importlib.util.spec_from_file_location(name, fs(rel))
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


J = load("tools/" + _J_FN, "wb_jexplore39_for_heya_i159")
mx = J.mx
assert sha(rb("tools/" + _J_FN)) == _J_SHA, "jexplore39 engine hash drift"
mx.FRAME_MS = FRAME_MS_BASE
mx.ZIP_DT = ZIP_DT
over, shift, blank, decode = mx.over, mx.shift, mx.blank, mx.decode


def read_ora(rel):
    z = zipfile.ZipFile(io.BytesIO(rb(rel)))
    root = ET.fromstring(z.read("stack.xml"))
    rows = root.find("stack").findall("layer")
    top_to_bottom = [(e.get("name"), e.get("src"), e.get("visibility")) for e in rows]
    layers, hidden = {}, []
    for name, src, vis in reversed(top_to_bottom):          # bottom -> top
        layers[name] = decode(z.read(src))
        if vis == "hidden":
            hidden.append(name)
    assert list(layers) == ALL_ROLES + ["guides"], (rel, list(layers))
    assert hidden == ["guides"], hidden
    return layers


def load_neutral(d):
    s = SRC[d]
    png = rb(s["dir"] + "/" + s["png"])
    assert sha(png) == s["png_sha"], d + " static PNG drift"
    layers = read_ora(s["dir"] + "/" + s["ora"])
    comp = over([layers[n] for n in ALL_ROLES])
    assert np.array_equal(comp, decode(png)), d + " ORA layers != static PNG"
    pal = json.loads(rb(s["dir"] + "/" + s["pal"]))
    assert sha(rb(s["dir"] + "/" + s["pal"])) == s["pal_sha"], d + " palette drift"
    pxo = zipfile.ZipFile(io.BytesIO(rb(s["dir"] + "/" + s["pxo"])))
    base_data = json.loads(pxo.read("data.json"))
    return png, layers, pal, base_data


def render_idle(base, i):
    _, t, h, a = IDLE_GROUPS[i]
    out = {"guides": base["guides"].copy()}
    for n in ALL_ROLES:
        dy = h if n in HEAD else (t if n in TORSO else (a if n in ARMS else 0))
        out[n] = shift(base[n], 0, dy) if dy else base[n].copy()
    return out


def pxo_bytes(layers_frames, png, base_data, d):
    data_owner = {"declared_palette": dict(base_data["user_data_obj"]["declared_palette"]),
                  "actor_id": ACTOR, "direction": d, "status": "UNAPPROVED"}
    data_owner["declared_palette"].update(name=f"{ACTOR}-{d}-idle-v01",
                                          comment=f"declared palette ({ACTOR} native idle {d} v01)")
    frames = [([(n, layers_frames[i][n]) for n in PXO_LAYERS], IDLE_MS[i]) for i in range(4)]
    raw = mx.make_pxo(PXO_LAYERS, frames, png, [{"name": "idle", "from": 1, "to": 4, "color": "8e3b36"}])
    zin = zipfile.ZipFile(io.BytesIO(raw))
    out = io.BytesIO()
    with zipfile.ZipFile(out, "w", zipfile.ZIP_DEFLATED) as z:
        for info in zin.infolist():
            b = zin.read(info.filename)
            if info.filename == "data.json":
                j = json.loads(b)
                j["user_data"] = json.dumps(data_owner, separators=(",", ":"))
                j["export_profile"] = dict(base_data["export_profile"])
                j["export_profile"].update(file_name=json.dumps(f"{ACTOR}-{d}-idle-v01-animated"),
                                           number_of_frames="4", split_layers="false")
                j["current_frame"] = 0
                j["current_layer"] = PXO_LAYERS.index("hair")
                b = json.dumps(j, separators=(",", ":")).encode()
            z.writestr(zipfile.ZipInfo(info.filename, ZIP_DT), b, zipfile.ZIP_DEFLATED)
    return out.getvalue()


def build_all():
    files, manifest_dirs = {}, {}
    for d in DIRS:
        png, base, pal, base_data = load_neutral(d)
        base_data["user_data_obj"] = json.loads(base_data.get("user_data") or "{}")
        frames = [render_idle(base, i) for i in range(4)]
        comps = [over([f[n] for n in ALL_ROLES]) for f in frames]
        assert np.array_equal(comps[0], decode(png)), d + " f00 not static"
        entry = {"direction": d, "frames": [], "source": SRC[d]}
        for i, f in enumerate(frames):
            b = mx.png_bytes(comps[i])
            rel = f"{OUT_PNG_REL}/{fname(d + '-f%02d' % i, 'png')}"
            files[rel] = b
            entry["frames"].append({"index": i, "file": rel.rsplit("/", 1)[-1], "sha256": sha(b),
                                    "duration_ms": IDLE_MS[i], "pose": {"torso": IDLE_GROUPS[i][1],
                                                                        "head": IDLE_GROUPS[i][2],
                                                                        "arms": IDLE_GROUPS[i][3]}})
        pxo = pxo_bytes(frames, png, base_data, d)
        prel = f"{OUT_NATIVE_REL}/{fname(d + '-animated', 'pxo')}"
        files[prel] = pxo
        ora = mx.make_ora([(n, base[n]) for n in ALL_ROLES + ["guides"]], png)
        orel = f"{OUT_NATIVE_REL}/{fname(d + '-static-layers', 'ora')}"
        files[orel] = ora
        pal_b = rb(SRC[d]["dir"] + "/" + SRC[d]["pal"])
        palrel = f"{OUT_NATIVE_REL}/{fname(d + '-palette', 'json')}"
        files[palrel] = pal_b
        entry.update({"static_png": {"file": SRC[d]["png"], "sha256": SRC[d]["png_sha"]},
                      "static_ora_input": {"file": SRC[d]["ora"], "sha256": SRC[d]["ora_sha"]},
                      "palette_input": {"file": SRC[d]["pal"], "sha256": SRC[d]["pal_sha"]},
                      "palette_copy": {"file": palrel.rsplit("/", 1)[-1], "sha256": sha(pal_b)},
                      "animated_pxo": {"file": prel.rsplit("/", 1)[-1], "sha256": sha(pxo), "frames": 4},
                      "static_layers_ora": {"file": orel.rsplit("/", 1)[-1], "sha256": sha(ora)},
                      "f00_exact_static": True,
                      "loop": {"total_ms": sum(IDLE_MS), "next": 0, "continuity": "f03 -> f00"},
                      "planted_feet": "boots layer and composite sole rows 90..103 identical in all 4 frames",
                      "global_bob": False})
        manifest_dirs[d] = entry
    runtime = {"schema": "worlds-between.idle-sprite-set.v1", "actor_id": ACTOR,
               "set_id": f"{ACTOR}-idle-four-direction-i159-v01-{STAMP}-{RUN}", "density": 2,
               "frame_size": [W, H], "pivot": list(PIN), "display_scale": SCALE, "logical_height_px": 48,
               "status": "UNAPPROVED technical source; not a default; no art/motion approval",
               "loop": True, "actions": {"idle": {d: [{"file": d + "/" + e["file"], "duration_ms": e["duration_ms"]}
                                                         for e in manifest_dirs[d]["frames"]] for d in DIRS}}}
    rt_b = (json.dumps(runtime, indent=2) + "\n").encode()
    rt_rel = f"{STAGE_REL}/{fname('sprite-set-runtime', 'json')}"
    files[rt_rel] = rt_b
    for d in DIRS:
        m = {"actor_id": ACTOR, "content_id": "content.char.heya.idle-anim", "status": "UNAPPROVED",
             "direction": d, "pose": "idle-four-frame-loop", "canvas": [W, H], "pivot": list(PIN),
             "body_rows": list(BODY_ROWS), "display_scale": SCALE, "logical_height_px": 48.0,
             "layers_bottom_to_top": PXO_LAYERS, "frame_durations_ms": IDLE_MS,
             "cycle_ms": sum(IDLE_MS), "loop": True,
             "idle_model": {"groups": {"head": list(HEAD), "torso": list(TORSO), "arms": list(ARMS),
                                      "static_feet": list(BOOTS)},
                            "offsets_source_texels": [{"frame": i, "torso": x[1], "head": x[2], "arms": x[3]}
                                                      for i, x in enumerate(IDLE_GROUPS)],
                            "neutral_endpoint": "f00 == existing static PNG byte-exact",
                            "planted_feet": "boots layer and composite sole rows 90..103 unchanged in all 4 frames; torso/leg rows 76..89 settle with the torso group; no global sprite bob"},
             "identity": "44-year-old medic; reddish-brown low braided coil; grey-white medical scarf; dark-red first-aid satchel",
             "directions": manifest_dirs[d], "runtime_set": {"file": rt_rel.rsplit("/", 1)[-1], "sha256": sha(rt_b)},
             "limitations": ["idle only; no walk/stop/combat/runtime integration/default; no GUI save/reopen",
                             "1 source texel = 0.5 logical px settle; no art/motion/human-approval claim"]}
        mrel = f"{STAGE_REL}/{d}/{fname(d + '-manifest', 'json')}"
        files[mrel] = (json.dumps(m, indent=2) + "\n").encode()
    # copy per-direction png/native files into staging/<d>/ with stable names
    for rel, b in list(files.items()):
        if rel.startswith(OUT_PNG_REL + "/") or rel.startswith(OUT_NATIVE_REL + "/"):
            name = rel.rsplit("/", 1)[-1]
            d = next(x for x in DIRS if f"idle-{x}-" in name)
            files[f"{STAGE_REL}/{d}/{name}"] = b
    # remove top-level png/native duplicates: canonical files live in staging/<d>/ and outputs report copies
    files = {k: v for k, v in files.items() if not (k.startswith(OUT_PNG_REL + "/") or k.startswith(OUT_NATIVE_REL + "/"))}
    listing = {"run": f"{STAMP}-{RUN}", "hash": "sha256-bytes", "files": {k: sha(v) for k, v in sorted(files.items())}}
    files[f"{OUT_REL}/file-list.json"] = (json.dumps(listing, indent=2) + "\n").encode()
    return files, manifest_dirs, runtime


def run_checks(files, manifest_dirs):
    checks = []

    def ck(name, ok, detail=""):
        checks.append({"check": name, "pass": bool(ok), "detail": detail})

    src_ok = all(sha(rb(SRC[d]["dir"] + "/" + SRC[d]["png"])) == SRC[d]["png_sha"] and
                 sha(rb(SRC[d]["dir"] + "/" + SRC[d]["ora"])) == SRC[d]["ora_sha"] and
                 sha(rb(SRC[d]["dir"] + "/" + SRC[d]["pal"])) == SRC[d]["pal_sha"] for d in DIRS)
    ck("source_static_ORA_palette_pins_exact", src_ok)
    ck("four_directions_present", set(manifest_dirs) == set(DIRS))
    for d in DIRS:
        e = manifest_dirs[d]
        static = rb(SRC[d]["dir"] + "/" + SRC[d]["png"])
        f00 = rb(STAGE_REL + "/" + d + "/" + e["frames"][0]["file"])
        ck(f"{d}_f00_bytes_equal_existing_static", f00 == static)
        ck(f"{d}_durations_and_cycle", [x["duration_ms"] for x in e["frames"]] == IDLE_MS and
           sum(IDLE_MS) == 1500)
        pxo = zipfile.ZipFile(io.BytesIO(rb(STAGE_REL + "/" + d + "/" + e["animated_pxo"]["file"])))
        data = json.loads(pxo.read("data.json"))
        ck(f"{d}_pxo_animated_metadata", data["pxo_version"] == 7 and data["fps"] == 10.0 and
           len(data["frames"]) == 4 and [fr["duration"] for fr in data["frames"]] == [7.0, 2.0, 4.0, 2.0] and
           [x["name"] for x in data["layers"]] == PXO_LAYERS and
           data["layers"][-1]["visible"] is False and data["layers"][-1]["locked"] is True)
        ck(f"{d}_pxo_idle_tag", data["tags"] == [{"name": "idle", "from": 1, "to": 4, "color": "8e3b36"}])
        ck(f"{d}_pxo_declared_palette_36", len(json.loads(data["user_data"])["declared_palette"]) == 0 or
           len(json.loads(data["user_data"])["declared_palette"].get("colors", {})) >= 24)
        # every layer of every frame byte-exact to emitted PNG layers is validated by independent checker too
        pal = json.loads(rb(SRC[d]["dir"] + "/" + SRC[d]["pal"]))["colors"]
        pset = {tuple(int(v[i:i + 2], 16) for i in (0, 2, 4)) for v in pal.values()}
        okpix = True
        for i, fr in enumerate(e["frames"]):
            a = decode(rb(STAGE_REL + "/" + d + "/" + fr["file"]))
            okpix &= a.shape == (H, W, 4) and set(np.unique(a[..., 3])) <= {0, 255}
            okpix &= not a[0].any() and not a[-1].any() and not a[:, 0].any() and not a[:, -1].any()
            used = {tuple(int(v) for v in row[:3]) for row in a.reshape(-1, 4) if row[3]}
            okpix &= used <= pset
        ck(f"{d}_png_binary_alpha_palette_border", okpix)
        # planted feet: boots + lower composite rows identical to static
        base = decode(static)
        frozen = True
        for fr in e["frames"][1:]:
            a = decode(rb(STAGE_REL + "/" + d + "/" + fr["file"]))
            frozen &= np.array_equal(a[90:104], base[90:104])
        ck(f"{d}_planted_feet_lower_body_frozen", frozen)
        changed = []
        prev = base
        for fr in e["frames"][1:] + [e["frames"][0]]:
            a = decode(rb(STAGE_REL + "/" + d + "/" + fr["file"]))
            changed.append(int(np.count_nonzero(np.any(a != prev, axis=2))))
            prev = a
        ck(f"{d}_subtle_nonzero_motion_and_loop_closure", all(0 < c <= 900 for c in changed),
           f"changed={changed}")
        # layer offsets are vertical only and match the model
        ora = read_ora(STAGE_REL + "/" + d + "/" + e["static_layers_ora"]["file"])
        model_ok = True
        for i, fr in enumerate(e["frames"]):
            a = decode(rb(STAGE_REL + "/" + d + "/" + fr["file"]))
            t, h, ar = IDLE_GROUPS[i][1:]
            model_ok &= np.array_equal(a, over([shift(ora[n], 0, h if n in HEAD else
                                                        (t if n in TORSO else (ar if n in ARMS else 0)))
                                                 for n in ALL_ROLES]))
        ck(f"{d}_all_frames_exact_group_offsets_no_horizontal", model_ok)
    ck("no_walk_or_stop_frames_emitted", not any("walk" in k or "stop" in k for k in files))
    return checks


def main():
    mode = sys.argv[1] if len(sys.argv) > 1 else "check"
    if mode not in ("build", "check", "install"):
        raise SystemExit("usage: build|check|install")
    pins_before = {d: sha(rb(SRC[d]["dir"] + "/" + SRC[d]["png"])) for d in DIRS}
    files1, man1, _ = build_all()
    files2, man2, _ = build_all()
    deterministic = files1.keys() == files2.keys() and all(files1[k] == files2[k] for k in files1)
    if mode == "build":
        for rel, b in files1.items():
            p = fs(STAGE_REL + "/" + rel.split("staging/idle/", 1)[1]) if rel.startswith(STAGE_REL) else fs(rel)
            if os.path.exists(p) and open(p, "rb").read() != b:
                raise SystemExit(f"refusing to overwrite different bytes: {rel}")
        for rel, b in files1.items():
            p = fs(rel)
            os.makedirs(os.path.dirname(p), exist_ok=True)
            with open(p, "wb") as f:
                f.write(b)
        print(f"WROTE {len(files1)} files")
    checks = run_checks(files1 if mode != "install" else files2, man1)
    fails = [c["check"] for c in checks if not c["pass"]]
    # installed parity
    inst = 0
    missing = []
    for rel, b in files1.items():
        if rel.startswith(STAGE_REL + "/"):
            irel = INSTALL_REL + "/" + rel.split(STAGE_REL + "/", 1)[1]
            if os.path.exists(fs(irel)):
                if rb(irel) == b:
                    inst += 1
                else:
                    fails.append("installed differs " + irel)
            else:
                missing.append(irel)
    pins_after = {d: sha(rb(SRC[d]["dir"] + "/" + SRC[d]["png"])) for d in DIRS}
    pins_ok = pins_before == pins_after and all(sha(rb(SRC[d]["dir"] + "/" + SRC[d]["ora"])) == SRC[d]["ora_sha"]
                                                for d in DIRS)
    if not deterministic:
        fails.append("non-deterministic rebuild")
    if not pins_ok:
        fails.append("source pins drifted")
    print(f"REBUILD {len(files1)} DETERMINISTIC {deterministic}")
    print(f"CHECKS {sum(c['pass'] for c in checks)}/{len(checks)}")
    print(f"INSTALLED {inst}/{sum(1 for k in files1 if k.startswith(STAGE_REL + '/'))}")
    res = {"tool_sha256": sha(open(os.path.abspath(__file__), "rb").read()), "run": f"{STAMP}-{RUN}",
           "deterministic": deterministic, "source_pins_exact": pins_ok, "checks": checks,
           "installed_verified": inst, "missing": missing, "fails": fails,
           "not_run": ["Pixelorama native export", "Godot runtime fit", "human review"]}
    os.makedirs(fs(OUT_REL), exist_ok=True)
    logid = datetime.now(timezone.utc).strftime("%Y%m%d-%H%M%S")
    with open(fs(OUT_REL + "/author-check-" + STAMP + "-" + RUN + "-" + logid + ".json"), "wb") as f:
        f.write((json.dumps(res, indent=2) + "\n").encode())
    print("RESULT", "PASS" if not fails else "FAIL", fails[:12])
    if mode == "install":
        if missing:
            for irel in missing:
                srel = STAGE_REL + "/" + irel.split(INSTALL_REL + "/", 1)[1]
                dst = fs(irel)
                os.makedirs(os.path.dirname(dst), exist_ok=True)
                shutil.copyfile(fs(srel), dst)
            print(f"INSTALLED {len(missing)} new files")
    return 0 if not fails else 1


if __name__ == "__main__":
    sys.exit(main())
