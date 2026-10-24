"""Milo EAST idle static, native 80x112 source package (UNAPPROVED v01).

content.char.milo.static-east. Code-authored native pixels in the Sea of Stars direction (broad clusters,
upper-left light), 48 logical px at display scale 0.5. East = nose toward screen RIGHT, so the character's RIGHT
side faces the camera: silver temple patch and the square medicine case are on the near side and fully shown; the
bright green wristband is on the far (left) wrist, whose forearm hangs just in front of the open coat. Authored in
forward coordinates with the Lin Que `P` pen (s = +1); it is not a mirror of the (uncommitted) west drawing.
Contract (written before authoring):
outputs/milo-e01/rpg-2-star-ocean-the-second_milo_east-style-source-contract_unapproved-v01_20261024-000137-e4a1c7d2.md

Reuses the hash-pinned, committed Milo south v01 author in memory (and through it Lin Que v01 `P`/finish/gates,
Jiang v01 gates and the male v8pair PNG/PXO/ORA serializers) with the same palette, layers, outline colours and
HARD gates. Only the direction label is rebound in memory. The committed south and north packages must stay
byte-identical, which this author verifies against their pinned manifests.

  python -X utf8 -I <this> build   # writes new files only (refuses to overwrite different bytes)
  python -X utf8 -I <this> check   # rebuilds twice in memory and compares with files on disk
"""
import hashlib, importlib.util, io, json, os, sys, zipfile

REPO = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
SLUG, ACTOR, D = "rpg-2-star-ocean-the-second", "milo", "east"
STAMP, RUN_ID = "20261024-000137", "e4a1c7d2"
OUT_REL = "game/assets/characters/milo-native-v01/east"
QA_REL = "outputs/milo-e01/author"
CONTRACT_REL = "outputs/milo-e01/rpg-2-star-ocean-the-second_milo_east-style-source-contract_unapproved-v01_20261024-000137-e4a1c7d2.md"
SOUTH_TOOL_REL = "tools/rpg-2-star-ocean-the-second_milo_south-static-author_unapproved-v01_20261023-215823-51a12dd6.py"
SOUTH_DIR_REL = "game/assets/characters/milo-native-v01/south"
SOUTH_MANIFEST_REL = SOUTH_DIR_REL + "/rpg-2-star-ocean-the-second_milo_south-manifest_unapproved-v01_20261023-215823-e604f893.json"
NORTH_DIR_REL = "game/assets/characters/milo-native-v01/north"
NORTH_MANIFEST_REL = NORTH_DIR_REL + "/rpg-2-star-ocean-the-second_milo_north-manifest_unapproved-v01_20261023-225642-163cf811.json"
PINS = {SOUTH_TOOL_REL: "138a78d5a8ec32a4cbef7037c5eb5bda8740821f5868cf0a277ad4eda613cb6d",
        SOUTH_MANIFEST_REL: "913d3070528bfb8539c65e7570e73c5f7bedc1b45a23928ec9aa091db7324cf7",
        NORTH_MANIFEST_REL: "0cb2b25f115117795dbc2788e9a2f448218c0899b8f2fc9929154ddb324402b1"}


def fs(rel):
    p = os.path.join(REPO, *rel.split("/"))
    return "\\\\?\\" + p if os.name == "nt" and len(p) > 240 and not p.startswith("\\\\?\\") else p


def sha(b):
    return hashlib.sha256(b).hexdigest()


def uid(*parts):
    return sha(":".join((RUN_ID,) + parts).encode())[:8]


def fname(purpose, ext):
    return f"{SLUG}_{ACTOR}_{D}-{purpose}_unapproved-v01_{STAMP}-{uid(D, purpose, ext)}.{ext}"


PIN_OK = {rel: sha(open(fs(rel), "rb").read()) == want for rel, want in PINS.items()}
_spec = importlib.util.spec_from_file_location("milo_south_v01_for_east", fs(SOUTH_TOOL_REL))
MS = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(MS)                                   # pins Lin/Jiang/male tools itself (MS.PIN_OK)
MS.D = D                                                      # rebind the direction label in memory only
M, S = MS.M, MS.S
PAL, LAYERS, FILE_KEYS = MS.PAL, MS.LAYERS, MS.FILE_KEYS
W, H, PIN, BODY_ROWS, L = MS.W, MS.H, MS.PIN, MS.BODY_ROWS, MS.L


# ------------------------------------------------------------------ east (profile, nose to screen right)
def draw_east(Ls):
    """Forward coordinates: f > 0 is the facing direction (screen x = 40 + f). Light stays upper-left on screen,
    so on this profile the back (screen-left) edge carries the highlight and the front edge the shade."""
    p = {n: M.P(Ls[n], 1) for n in LAYERS}

    # boots: near (right) boot in front, toe to screen right, pale band and green patch; far boot set back, darker
    b = p["boots"]
    b.shaded(-8, 90, -2, 101, "b2", "b2", "b3", 1, 1)                                  # far boot (heel side)
    b.rect(-8, 90, -5, 91, "w4")                                                        # far pale band, in shade
    b.shaded(-4, 88, 4, 101, "b1", "b2", "b3", 2, 2)
    b.rect(-4, 88, 4, 90, "w3"); b.rect(-4, 88, 4, 88, "w2"); b.rect(3, 88, 4, 90, "w4")  # pale band
    b.rect(-1, 92, 1, 94, "g3"); b.rect(-1, 92, 0, 92, "g2")                           # green patch
    b.shaded(5, 97, 8, 101, "b2", "b2", "b3", 1, 1); b.rect(5, 97, 6, 97, "b1")        # toe cap
    b.rect(-8, 102, 8, 102, "b3"); b.rect(-8, 103, 8, 103, "k1")                       # soles

    # trousers: navy; far (left) leg behind and darker; green piping on the near leg's outer seam
    t = p["trousers"]
    t.rect(-7, 63, 4, 69, "n2")
    t.shaded(-7, 69, -2, 89, "n2", "n3", "n4", 1, 1)
    t.shaded(-3, 69, 3, 89, "n1", "n2", "n3", 2, 1)
    t.rect(0, 74, 0, 88, "g3")
    t.rect(2, 81, 3, 81, "n3"); t.rect(-3, 84, -2, 84, "n3")                            # knee fold, back crease

    # undershirt: navy high zip collar at the throat and the shirt edge in the open coat front
    u = p["undershirt"]
    u.rows({33: (1, 3), **{y: (0, 4) for y in range(34, 38)}}, "n2"); u.rect(3, 34, 4, 37, "n3")
    u.shaded(2, 38, 6, 64, "n1", "n2", "n3", 1, 1)
    u.rect(5, 39, 5, 59, "x2")                                                          # zip

    # coat: white/grey SHORT coat, standing collar behind the neck, open front; no chest cross (far chest)
    c = p["coat"]
    c.rows({37: (-5, 2), 38: (-6, 3), **{y: (-7, 3) for y in range(39, 62)}}, "w2")
    c.rect(-7, 39, -6, 61, "w1"); c.rect(2, 40, 3, 61, "w3")                           # lit back / shaded front
    c.shaded(-8, 62, 4, 75, "w1", "w2", "w3", 2, 2)
    c.rows({76: (-8, 4), 77: (-7, 3)}, "w3")
    c.rows({32: (-5, -2), **{y: (-6, -1) for y in range(33, 38)}}, "w2"); c.rect(-6, 33, -5, 37, "w1")  # collar
    c.rect(-2, 33, -1, 37, "w3")
    c.rect(2, 72, 4, 75, "g3"); c.rect(2, 72, 3, 72, "g2")                             # front hem accent

    # belt: only in the open front
    bl = p["belt"]
    bl.rect(4, 61, 7, 63, "r2"); bl.rect(4, 61, 7, 61, "r1"); bl.rect(6, 61, 7, 63, "x2"); bl.rect(6, 61, 7, 61, "x1")

    # case: on the near (right) hip, broad face to the camera, riding back past the coat edge
    k = p["case"]
    k.shaded(-15, 64, 0, 77, "w1", "w2", "w3", 2, 2)
    k.rect(-15, 67, 0, 67, "w3"); k.rect(-14, 64, -1, 64, "w1")                        # lid line, lid light
    k.rect(-14, 64, -13, 77, "n2"); k.rect(-2, 64, -1, 77, "n2"); k.rect(-14, 64, -14, 77, "n1")  # straps
    k.rect(-14, 68, -13, 69, "x2"); k.rect(-2, 68, -1, 69, "x2")                       # buckles
    k.rect(-9, 69, -6, 75, "g2"); k.rect(-11, 71, -4, 73, "g2")                        # green cross
    k.rect(-9, 69, -8, 71, "g1"); k.rect(-11, 71, -10, 72, "g1"); k.rect(-5, 72, -4, 73, "g3")
    k.rect(-7, 74, -6, 75, "g3")
    k.rect(-10, 62, -4, 63, "n2"); k.rect(-9, 62, -5, 62, "n1")                        # handle

    # strap: cross-body from the far (left) shoulder; only its front branch shows, chest front -> case handle
    s = p["strap"]
    for i in range(24):
        f = 3 - (i * 12) // 23
        s.rect(f - 1, 38 + i, f + 1, 38 + i, "n1")

    # far (left) arm: upper arm hidden by the torso; forearm and hand hang just ahead of the open front
    a = p["arms"]
    a.rect(7, 50, 9, 53, "w3"); a.rect(7, 50, 8, 50, "w2")                             # sleeve at the elbow
    a.rect(7, 54, 10, 57, "n3"); a.rect(7, 54, 10, 54, "n2")                           # far cuff
    a.shaded(7, 58, 9, 59, "s2", "s3", "s3", 1, 1)
    a.shaded(7, 63, 10, 67, "s2", "s3", "s3", 1, 1); a.rect(7, 68, 9, 68, "s4")       # far hand
    # near (right) arm: rolled sleeve, navy cuff, forearm, relaxed hand at the case's front-upper corner
    a.rows({37: (-3, 0), 38: (-4, 1)}, "w2")
    a.shaded(-4, 39, 1, 53, "w1", "w2", "w3", 2, 1)
    a.rect(-4, 54, 1, 57, "n2"); a.rect(-4, 54, 1, 54, "n1"); a.rect(-4, 57, 1, 57, "n3")   # navy cuff
    a.shaded(-3, 58, 1, 62, "s1", "s2", "s3", 1, 1)
    a.shaded(-3, 63, 1, 68, "s1", "s2", "s3", 1, 1); a.rect(2, 64, 2, 66, "s2")       # hand, thumb forward
    a.rect(-3, 69, 1, 69, "s3")

    # wristband: bright green on the far (left) wrist, in front of the body
    wb = p["wristband"]
    wb.shaded(6, 60, 10, 62, "g1", "g2", "g3", 1, 1); wb.rect(6, 60, 10, 60, "g1")

    # face: profile, one green eye, nose leading right, ear mid-head, smile corner, stubble on jaw/chin
    fc = p["face"]
    fc.rows({**{y: (-3, 7) for y in range(15, 28)}, 28: (-2, 7), 29: (-2, 7), 30: (-2, 6), 31: (-1, 6),
             32: (1, 5), 33: (2, 4)}, "s2")
    fc.rect(-3, 15, -2, 27, "s1"); fc.rect(6, 26, 7, 31, "s3")                         # lit back / shaded jaw
    fc.rows({23: (8, 8), 24: (8, 9), 25: (8, 9)}, "s2"); fc.rect(9, 25, 9, 25, "s3"); fc.rect(7, 26, 8, 26, "s3")
    fc.rect(-2, 21, 1, 26, "s1"); fc.rect(-1, 22, 0, 25, "s3"); fc.rect(0, 23, 0, 24, "s4")   # ear
    fc.rect(3, 21, 7, 21, "h3")                                                         # brow
    fc.rect(4, 23, 7, 23, "h4"); fc.rect(4, 24, 5, 25, "e2"); fc.rect(6, 24, 6, 25, "e1"); fc.px(4, 24, "h4")
    fc.rect(5, 29, 7, 29, "m1"); fc.px(5, 28, "m1")                                    # smile corner
    fc.rows({30: (1, 5), 31: (1, 5), 32: (2, 4), 33: (2, 4)}, "j1")                    # stubble

    # hair: short spikes up/back, cropped nape, sheen at the lit back, silver patch at the near (right) temple
    h = p["hair"]
    # spike rows: each row-9 segment extends 2 px back of its tip and the gaps are 2 px, so outline runs join
    h.rows({8: (-7, -6), 9: (-9, -6)}, "h2"); h.rows({8: (-1, 0), 9: (-3, 0)}, "h2"); h.rows({8: (5, 6), 9: (3, 6)}, "h3")
    h.rows({10: (-10, 7), 11: (-10, 8), **{y: (-11, 8) for y in range(12, 17)}, 17: (-10, 8),
            **{y: (-10, 2) for y in range(18, 21)},
            21: (-10, -3), 22: (-10, -3), 23: (-9, -3), 24: (-9, -3), 25: (-8, -3), 26: (-7, -3), 27: (-6, -4)}, "h2")
    h.rows({18: (3, 8), 19: (5, 8), 20: (7, 8)}, "h3")                                 # fringe tips (front, shade)
    h.rect(1, 21, 2, 23, "h3")                                                          # cropped sideburn
    h.rows({9: (-8, -6), 10: (-9, -3), 11: (-9, -4), 12: (-10, -6)}, "h1")            # upper-left sheen (back)
    h.rect(-11, 13, -10, 16, "h1"); h.rect(-10, 17, -9, 19, "h1")
    h.rect(5, 10, 8, 17, "h3")                                                          # front shade plane
    h.rows({14: (-5, -4), 15: (-4, -3)}, "h3")                                         # spike break
    h.rows({12: (-1, 2), **{y: (-2, 3) for y in range(13, 20)}, 20: (-1, 2)}, "a2")   # silver temple patch
    h.rect(-2, 13, -1, 15, "a1"); h.rows({19: (1, 3), 20: (0, 2)}, "a3")


def draw():
    Ls = {n: L() for n in LAYERS}
    draw_east(Ls)
    return M.finish(Ls)


# ------------------------------------------------------------------ package
def artifacts():
    hp = S.load_helper()
    hp.ZIP_DT, hp.LAYERS, hp.PAL = MS.ZIP_DT, LAYERS, PAL
    blobs = draw()
    full = S.compose_layers(blobs)
    png = hp.png_bytes(full)
    pxo = MS.fix_pxo_metadata(hp.make_pxo(blobs, png))           # labels use the rebound direction (east)
    ora = hp.make_ora(blobs, png)
    pal = (json.dumps({"actor_id": ACTOR, "name": f"{ACTOR}-{D}-v01", "colors": PAL}, indent=2) + "\n").encode()
    return hp, blobs, full, png, pxo, ora, pal


def package_unchanged(manifest_rel, dir_rel):
    m = json.loads(open(fs(manifest_rel), "rb").read())
    pal = json.loads(open(fs(f"{dir_rel}/{m['files']['palette']['file']}"), "rb").read())
    files = {v["file"]: sha(open(fs(f"{dir_rel}/{v['file']}"), "rb").read()) == v["rawsha256"]
             for v in m["files"].values()}
    return {"files_match_manifest": all(files.values()), "palette_colors_identical": pal["colors"] == PAL}


def gates(r):
    g = MS.gates(r)
    with zipfile.ZipFile(io.BytesIO(r[4])) as z:
        dj = z.read("data.json")
    g["pxo_labels_east"] = b"milo-east" in dj and b"milo-south" not in dj
    return g


HARD = MS.HARD + ["pxo_labels_east"]


def manifest(files, g):
    m = {"actor_id": ACTOR, "content_id": f"content.char.{ACTOR}.static-{D}", "status": "UNAPPROVED",
         "direction": D, "pose": "idle-static", "canvas": [W, H], "pivot": list(PIN), "body_rows": list(BODY_ROWS),
         "display_scale": S.DISPLAY_SCALE, "logical_height_px": (BODY_ROWS[1] - BODY_ROWS[0] + 1) * S.DISPLAY_SCALE,
         "layers": [{"name": n, "visible": n != "guides"} for n in LAYERS],
         "face_layer_role": "profile face, one green eye, brow, nose leading screen right, ear, smile corner, stubble",
         "view_notes": "east profile (nose to screen right; the character's RIGHT side faces the camera): short "
                       "up/back dark-brown spikes, cropped nape, silver patch at the near (right) temple; navy zip "
                       "high collar under a standing white collar; white/grey short coat to mid-thigh with open "
                       "front, navy shirt edge, zip and belt; no chest cross (it is on the far left chest); front "
                       "branch of the cross-body strap from the chest front to the case handle; square white case "
                       "with navy straps, buckles and green cross on the near (right) hip, riding back past the "
                       "coat; near arm with rolled sleeve, navy cuff and relaxed hand at the case corner; far "
                       "forearm just ahead of the coat front with the bright green wristband on the far (left) "
                       "wrist; near leg in front with green piping, far leg set back and darker; boots with pale "
                       "bands, green patch on the near boot",
         "authored_deviations_from_sheet": [
             "coat length: Bible character-04 says SHORT coat; the sheet shows knee length. Mid-thigh hem used.",
             "case strap: drawn cross-body (character's left shoulder to right hip) as in south v01; only the "
             "front branch is visible in this profile.",
             "far wristband: the far (left) forearm hangs slightly ahead of the open coat so the wristband is "
             "visible at 48 px (explicit readability choice in the contract)."],
         "files": {k: {"file": fname(*FILE_KEYS[k]), "rawsha256": sha(b)} for k, b in files.items()},
         "colour_count": g["colour_count"], "genuine_visible_role_layers": g["genuine_visible_role_layers"],
         "isolated_texels": g["isolated_texels"],
         "portrait_ref": {"file": MS.PORTRAIT_REL, "expected_sha256": MS.PORTRAIT_SHA, "approval": "approved source portrait",
                          "use": "identity reference only (approved hairstyle sheet); no pixels sampled"},
         "continuity_ref": {"south": {"file": SOUTH_MANIFEST_REL, "rawsha256": PINS[SOUTH_MANIFEST_REL]},
                            "north": {"file": NORTH_MANIFEST_REL, "rawsha256": PINS[NORTH_MANIFEST_REL]},
                            "use": "Milo south v01 palette/layers/outline/gates; no pixels copied"},
         "style_contract": "docs/design/rpg-2-star-ocean-the-second_characters_sea-of-stars-style-direction_v01_20261020-181026-f5938409.md",
         "view_contract": CONTRACT_REL,
         "source_contract": "same as Milo south v01: 80x112, pivot (40,104), body rows 8..103, display scale 0.5 = "
                            "48 logical px, binary alpha, transparent border, same declared 40-entry palette, "
                            "24..48 used colours, >=8 genuine role layers, hidden guides layer",
         "author_tool": "tools/" + os.path.basename(__file__), "reused_tool_pins": {**PINS, **MS.PINS},
         "serialization_helper": S.HELPER_REL,
         "pixel_source": "code-authored native pixels, declared palette",
         "limitations": "east static only; no runtime wiring, no motion, no creator art approval"}
    return (json.dumps(m, indent=2) + "\n").encode()


def main():
    cmd = sys.argv[1] if len(sys.argv) > 1 else "check"
    r1, r2 = artifacts(), artifacts()
    g = gates(r1)
    g["deterministic_rebuild"] = all(a == b for a, b in zip(r1[3:], r2[3:]))
    su = {"south": package_unchanged(SOUTH_MANIFEST_REL, SOUTH_DIR_REL),
          "north": package_unchanged(NORTH_MANIFEST_REL, NORTH_DIR_REL)}
    bad = [k for k in HARD + ["deterministic_rebuild"] if not g[k]]
    bad += [f"tool_pin:{rel}" for rel, ok in {**PIN_OK, **MS.PIN_OK}.items() if not ok]
    bad += [f"{d}:{k}" for d, v in su.items() for k, ok in v.items() if not ok]
    files = dict(zip(("png", "pxo", "ora", "palette"), r1[3:]))
    named = {f"{OUT_REL}/{fname(*FILE_KEYS[k])}": b for k, b in files.items()}
    named[f"{OUT_REL}/{fname('manifest', 'json')}"] = manifest(files, g)
    if cmd == "build":
        if bad:
            raise SystemExit(f"hard gates failed: {bad}")
        for rel, data in named.items():
            p = fs(rel)
            os.makedirs(os.path.dirname(p), exist_ok=True)
            if os.path.exists(p) and open(p, "rb").read() != data:
                raise SystemExit(f"refusing to overwrite different file {rel}")
            open(p, "wb").write(data)
        from PIL import Image
        os.makedirs(fs(QA_REL), exist_ok=True)
        prev = f"{QA_REL}/{SLUG}_{ACTOR}_{D}-preview-x6_unapproved-v01_{STAMP}-{uid(D, 'preview')}.png"
        Image.fromarray(r1[2], "RGBA").resize((W * 6, H * 6), Image.NEAREST).save(fs(prev))
        listing = {"outputs": {rel: sha(b) for rel, b in sorted(named.items())},
                   "qa_preview_nonsource": {prev: sha(open(fs(prev), "rb").read())}, "hash": "sha256 of raw bytes"}
        lp = f"{QA_REL}/{SLUG}_{ACTOR}_{D}-output-paths-rawhashes_unapproved-v01_{STAMP}-{uid('paths')}.json"
        open(fs(lp), "wb").write((json.dumps(listing, indent=2) + "\n").encode())
    elif cmd == "preview":                                     # scratch preview only; writes no source file
        from PIL import Image
        os.makedirs(fs("outputs/milo-e01/scratch"), exist_ok=True)
        Image.fromarray(r1[2], "RGBA").resize((W * 6, H * 6), Image.NEAREST).save(
            fs("outputs/milo-e01/scratch/milo-east-draft-x6.png"))
    disk = {rel: (sha(open(fs(rel), "rb").read()) == sha(b)) if os.path.exists(fs(rel)) else None
            for rel, b in named.items()}
    report = {k: g[k] for k in ("body_rows", "colour_count", "genuine_visible_role_layers", "visible_role_texels",
                                "isolated_texels", "silhouette_width", "identity_colours_visible", "binary_alpha",
                                "no_opaque_border", "pin_inside_feet_span", "all_colours_declared", "ora_hidden",
                                "face_has_eye", "deterministic_rebuild")}
    report.update(tool_pins_ok={**PIN_OK, **MS.PIN_OK}, packages_unchanged=su, disk_matches_rebuild=disk,
                  hard_failures=bad)
    print(json.dumps(report, indent=1))
    ok = not bad and all(v is True for v in disk.values())
    print("MILO_EAST_V01_" + ("ALL_OK" if ok else "FAIL"))
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
