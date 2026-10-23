"""Milo NORTH idle static, native 80x112 source package (UNAPPROVED v01).

content.char.milo.static-north. Code-authored native pixels in the Sea of Stars direction (broad clusters,
upper-left light), 48 logical px at display scale 0.5. North = back to the camera, so the character's RIGHT side
is on screen RIGHT: silver temple patch and medicine case on screen right, green wristband on the screen-left
wrist, cross-body strap from the screen-left shoulder to the screen-right hip. No face: back of the head, ears and
nape only. Reauthored as a back view; it is not a recolour or mirror of south. Contract (written before authoring):
outputs/milo-n01/rpg-2-star-ocean-the-second_milo_north-style-source-contract_unapproved-v01_20261023-225642-1b612f93.md

Reuses the hash-pinned, committed Milo south v01 author in memory (and through it Lin Que v01 finish/gates, Jiang
v01 gates and the male v8pair PNG/PXO/ORA serializers) with the same palette, layers, outline colours and HARD
gates. Only the direction label is rebound in memory. South's `face_has_eye` gate is swapped for the reused Lin
author's own north rule `north_face_no_eyes_or_mouth`. The committed south package must stay byte-identical,
which this author verifies against the pinned south manifest.

  python -X utf8 -I <this> build   # writes new files only (refuses to overwrite different bytes)
  python -X utf8 -I <this> check   # rebuilds twice in memory and compares with files on disk
"""
import hashlib, importlib.util, io, json, os, sys, zipfile

REPO = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
SLUG, ACTOR, D = "rpg-2-star-ocean-the-second", "milo", "north"
STAMP, RUN_ID = "20261023-225642", "1b612f93"
OUT_REL = "game/assets/characters/milo-native-v01/north"
QA_REL = "outputs/milo-n01/author"
CONTRACT_REL = "outputs/milo-n01/rpg-2-star-ocean-the-second_milo_north-style-source-contract_unapproved-v01_20261023-225642-1b612f93.md"
SOUTH_TOOL_REL = "tools/rpg-2-star-ocean-the-second_milo_south-static-author_unapproved-v01_20261023-215823-51a12dd6.py"
SOUTH_DIR_REL = "game/assets/characters/milo-native-v01/south"
SOUTH_MANIFEST_REL = SOUTH_DIR_REL + "/rpg-2-star-ocean-the-second_milo_south-manifest_unapproved-v01_20261023-215823-e604f893.json"
PINS = {SOUTH_TOOL_REL: "138a78d5a8ec32a4cbef7037c5eb5bda8740821f5868cf0a277ad4eda613cb6d",
        SOUTH_MANIFEST_REL: "913d3070528bfb8539c65e7570e73c5f7bedc1b45a23928ec9aa091db7324cf7"}


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
_spec = importlib.util.spec_from_file_location("milo_south_v01_for_north", fs(SOUTH_TOOL_REL))
MS = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(MS)                                   # pins Lin/Jiang/male tools itself (MS.PIN_OK)
MS.D = D                                                      # rebind the direction label in memory only
M, S = MS.M, MS.S
PAL, LAYERS, FILE_KEYS = MS.PAL, MS.LAYERS, MS.FILE_KEYS
W, H, PIN, BODY_ROWS, L = MS.W, MS.H, MS.PIN, MS.BODY_ROWS, MS.L


# ------------------------------------------------------------------ north (back view)
def draw_north(Ls):
    """Screen coordinates. Character's right = screen right. Light stays upper-left on screen."""
    # boots: pale band at the top, green back pull-tab, raised heel counter
    b = Ls["boots"]
    for x0, x1 in ((29, 39), (41, 51)):
        b.shaded(x0 + 1, 88, x1 - 1, 97, "b1", "b2", "b3", 2, 2)
        b.rect(x0 + 1, 88, x1 - 1, 90, "w3"); b.hline(x0 + 1, x1 - 1, 88, "w2"); b.rect(x1 - 3, 88, x1 - 1, 90, "w4")
        b.rect(x0 + 4, 91, x0 + 6, 95, "g3"); b.hline(x0 + 4, x0 + 6, 91, "g2")    # back pull-tab
        b.shaded(x0 + 1, 96, x1 - 1, 101, "b2", "b2", "b3", 2, 2)
        b.rect(x0 + 3, 97, x1 - 3, 100, "b1")                                    # heel counter
        b.hline(x0, x1, 102, "b3"); b.hline(x0, x1, 103, "k1")

    # trousers: navy, green piping on the outer seams, back-knee folds, centre seam
    t = Ls["trousers"]
    t.rect(31, 63, 49, 69, "n2")
    t.shaded(30, 69, 39, 89, "n1", "n2", "n3", 2, 2)
    t.shaded(41, 69, 50, 89, "n1", "n2", "n3", 2, 2)
    t.vline(40, 63, 89, "n4")
    t.vline(31, 72, 88, "g3"); t.vline(49, 72, 88, "g3")
    t.rect(33, 83, 37, 83, "n3"); t.rect(43, 83, 47, 83, "n3")

    # undershirt: navy high collar visible just above the coat collar at the back of the neck
    u = Ls["undershirt"]
    u.rect(35, 30, 45, 34, "n2"); u.hline(35, 41, 30, "n1"); u.rect(44, 30, 45, 34, "n3")

    # coat: closed white/grey SHORT back (mid-thigh), standing collar, centre seam, green tab, short vent
    c = Ls["coat"]
    c.rows({37: (30, 50), 38: (27, 53), **{y: (26, 54) for y in range(39, 62)}}, "w2")
    c.shaded(26, 62, 54, 75, "w1", "w2", "w3", 2, 2)
    c.rows({76: (27, 53), 77: (27, 53)}, "w3")
    c.rect(26, 39, 28, 61, "w1"); c.rect(52, 39, 54, 61, "w3")                 # side light/shadow planes
    c.rows({32: (33, 47), **{y: (31, 49) for y in range(33, 37)}}, "w2")      # standing collar (back)
    c.rows({32: (33, 38), 33: (31, 37), 34: (31, 36)}, "w1"); c.rect(47, 32, 49, 36, "w3")
    c.hline(27, 53, 38, "w3"); c.hline(31, 49, 37, "w3")                      # collar fold, shoulder seam
    c.vline(40, 46, 61, "w3"); c.vline(40, 62, 69, "w3")                      # centre back seam
    c.rect(39, 39, 41, 44, "g2"); c.hline(39, 41, 39, "g1")                   # green back tab
    c.rect(27, 73, 29, 75, "g3"); c.rect(51, 73, 53, 75, "g3")                # hem accents

    # belt layer: the coat's back half-belt (the front belt is hidden from behind)
    bl = Ls["belt"]
    bl.rect(29, 57, 51, 59, "r2"); bl.hline(29, 51, 57, "r1")
    bl.rect(31, 57, 32, 58, "x2"); bl.rect(48, 57, 49, 58, "x2"); bl.hline(31, 32, 57, "x1"); bl.hline(48, 49, 57, "x1")

    # case: square white medicine case on the character's right hip (screen right); cross clear of the hand
    k = Ls["case"]
    k.shaded(53, 63, 67, 76, "w1", "w2", "w3", 2, 2)
    k.hline(53, 67, 66, "w3"); k.hline(54, 66, 63, "w1")                      # lid line
    k.rect(54, 63, 55, 76, "n2"); k.rect(65, 63, 66, 76, "n2"); k.vline(65, 63, 76, "n1")  # navy straps
    k.rect(54, 67, 55, 68, "x2"); k.rect(65, 67, 66, 68, "x2")                # buckles
    k.rect(59, 70, 61, 75, "g2"); k.rect(58, 71, 62, 73, "g2")                # green cross
    k.rect(59, 71, 60, 72, "g1"); k.rect(61, 71, 62, 73, "g3"); k.rect(59, 75, 61, 75, "g3")
    k.rect(57, 61, 63, 62, "n2"); k.hline(58, 62, 61, "n1")                   # handle

    # strap: cross-body, character's left shoulder (screen left) -> right hip (screen right); flat band
    s = Ls["strap"]
    for i in range(24):
        x, y = 31 + i, 37 + i
        s.hline(x, x + 2, y, "n1")
    s.rect(53, 60, 56, 62, "n2")

    # arms: rolled white sleeves, navy cuffs, bare forearms, backs of relaxed hands. Repair 1: the screen-left hand
    # (below the wristband, rows 63..69) is tucked 2 px inward against the hip (x 23..27) so the off-side hand stays
    # clear of the contract's case region bound (x <= 22); the screen-right hand is unchanged (hx = x0 + 1).
    a = Ls["arms"]
    for x0, hi, dk, hx in ((20, "w1", "w3", 23), (54, "w2", "w3", 55)):
        a.rows({38: (x0 + 1, x0 + 5), 39: (x0, x0 + 6)}, "w2")
        a.shaded(x0, 40, x0 + 6, 53, hi, "w2", dk, 2, 2)
        a.rect(x0, 54, x0 + 6, 57, "n2"); a.hline(x0, x0 + 6, 54, "n1"); a.hline(x0, x0 + 6, 57, "n3")
        a.shaded(x0 + 1, 58, x0 + 5, 62, "s1", "s2", "s3", 2, 1)
        a.shaded(hx, 63, hx + 4, 63, "s1", "s2", "s3", 2, 1)
        a.shaded(hx, 64, hx + 4, 68, "s2", "s2", "s3", 1, 1); a.hline(hx, hx + 4, 69, "s3")
    a.rect(20, 41, 21, 52, "w1")

    # wristband: bright green band on the character's left wrist (screen left)
    wb = Ls["wristband"]
    wb.rect(20, 60, 26, 62, "g2"); wb.hline(20, 26, 60, "g1"); wb.rect(25, 60, 26, 62, "g3")
    wb.rect(22, 61, 23, 61, "g1")

    # face layer: ears and nape only (no eyes, mouth, brows or stubble from behind)
    f = Ls["face"]
    f.rect(29, 21, 30, 26, "s2"); f.rect(29, 21, 29, 23, "s1")               # left ear (lit)
    f.rect(50, 21, 51, 26, "s3")                                             # right ear (shade)
    f.rows({28: (36, 44), 29: (36, 44)}, "s2"); f.rect(43, 28, 44, 29, "s3")  # nape

    # hair: very short spiky dark brown from behind; silver patch at the right temple (screen right)
    h = Ls["hair"]
    h.rows({8: (44, 45), 9: (44, 47), 10: (31, 49), **{y: (30, 50) for y in range(11, 15)},
            **{y: (29, 51) for y in range(15, 21)}, **{y: (31, 49) for y in range(21, 27)}, 27: (33, 47)}, "h2")
    h.rows({8: (38, 39), 9: (38, 41)}, "h2"); h.rows({8: (32, 33), 9: (32, 35)}, "h2")   # spike tips
    h.rows({9: (44, 47)}, "h3"); h.rows({8: (44, 45)}, "h3")
    h.rows({10: (32, 37), 11: (31, 38), 12: (32, 36)}, "h1")                  # upper-left sheen
    h.rect(29, 15, 30, 20, "h1")
    h.rect(46, 10, 47, 26, "h3")                                             # right (shadow) plane
    h.rows({24: (31, 49), 25: (31, 49), 26: (31, 49), 27: (33, 47)}, "h3")    # cropped nape shadow
    for x0 in (33, 38, 43):                                                  # short downward nape spikes
        h.rows({24: (x0, x0 + 2), 25: (x0, x0 + 2), 26: (x0 + 1, x0 + 1)}, "h2")
    h.rows({11: (48, 49), 12: (48, 50), 13: (48, 50), **{y: (48, 51) for y in range(14, 20)}, 20: (49, 51)},
           "a2")                                                              # silver temple patch
    h.rect(48, 12, 49, 14, "a1"); h.rows({19: (48, 50), 20: (49, 51)}, "a3")


def vent(Ls):
    """Short centre back vent: transparent slit in the coat hem so the trouser seam shows through."""
    a = Ls["coat"].a
    for y in range(70, 78):
        half = 0 if y < 74 else 1
        a[y, 40 - half:40 + half + 1] = 0


def draw():
    Ls = {n: L() for n in LAYERS}
    draw_north(Ls)
    vent(Ls)
    return M.finish(Ls)


# ------------------------------------------------------------------ package
def artifacts():
    hp = S.load_helper()
    hp.ZIP_DT, hp.LAYERS, hp.PAL = MS.ZIP_DT, LAYERS, PAL
    blobs = draw()
    full = S.compose_layers(blobs)
    png = hp.png_bytes(full)
    pxo = MS.fix_pxo_metadata(hp.make_pxo(blobs, png))           # labels use the rebound direction (north)
    ora = hp.make_ora(blobs, png)
    pal = (json.dumps({"actor_id": ACTOR, "name": f"{ACTOR}-{D}-v01", "colors": PAL}, indent=2) + "\n").encode()
    return hp, blobs, full, png, pxo, ora, pal


def south_unchanged():
    m = json.loads(open(fs(SOUTH_MANIFEST_REL), "rb").read())
    pal = json.loads(open(fs(f"{SOUTH_DIR_REL}/{m['files']['palette']['file']}"), "rb").read())
    files = {v["file"]: sha(open(fs(f"{SOUTH_DIR_REL}/{v['file']}"), "rb").read()) == v["rawsha256"]
             for v in m["files"].values()}
    return {"files_match_manifest": all(files.values()), "palette_colors_identical": pal["colors"] == PAL}


def gates(r):
    g = MS.gates(r)                                               # Lin gates run with d == "north"
    with zipfile.ZipFile(io.BytesIO(r[4])) as z:
        dj = z.read("data.json")
    g["pxo_labels_north"] = b"milo-north" in dj and b"milo-south" not in dj
    return g


HARD = [k for k in MS.HARD if k != "face_has_eye"] + ["north_face_no_eyes_or_mouth", "pxo_labels_north"]


def manifest(files, g):
    m = {"actor_id": ACTOR, "content_id": f"content.char.{ACTOR}.static-{D}", "status": "UNAPPROVED",
         "direction": D, "pose": "idle-static", "canvas": [W, H], "pivot": list(PIN), "body_rows": list(BODY_ROWS),
         "display_scale": S.DISPLAY_SCALE, "logical_height_px": (BODY_ROWS[1] - BODY_ROWS[0] + 1) * S.DISPLAY_SCALE,
         "layers": [{"name": n, "visible": n != "guides"} for n in LAYERS],
         "face_layer_role": "ears and nape only (no eyes, mouth, brows or stubble)",
         "view_notes": "back view (character's right = screen right): very short spiky dark-brown hair with the "
                       "silver patch at the right temple (screen right); navy high collar above the white coat's "
                       "standing collar; closed white/grey short coat back to mid-thigh with centre seam, green back "
                       "tab, back half-belt (belt layer), short centre vent and green hem accents; cross-body strap "
                       "from the left shoulder (screen left) to the square white case with navy straps and green "
                       "cross on the right hip (screen right); bright green wristband on the left wrist (screen "
                       "left); rolled sleeves, navy cuffs, backs of hands; navy trousers with green piping; boots "
                       "with pale bands, green back pull-tabs and heel counters",
         "authored_deviations_from_sheet": [
             "coat length: Bible character-04 says SHORT coat; the sheet shows knee length. Mid-thigh hem used.",
             "case strap: drawn cross-body (character's left shoulder to right hip) as in south v01.",
             "silver patch: kept on the character's right temple per south canon (screen right from behind); the "
             "sheet's back view shows it on the head's screen-left side, inconsistent with its own front views."],
         "files": {k: {"file": fname(*FILE_KEYS[k]), "rawsha256": sha(b)} for k, b in files.items()},
         "colour_count": g["colour_count"], "genuine_visible_role_layers": g["genuine_visible_role_layers"],
         "isolated_texels": g["isolated_texels"],
         "portrait_ref": {"file": MS.PORTRAIT_REL, "expected_sha256": MS.PORTRAIT_SHA, "approval": "approved source portrait",
                          "use": "identity reference only (approved hairstyle sheet); no pixels sampled"},
         "continuity_ref": {"file": SOUTH_MANIFEST_REL, "rawsha256": PINS[SOUTH_MANIFEST_REL],
                            "use": "Milo south v01 palette/layers/outline/gates; no pixels copied"},
         "style_contract": "docs/design/rpg-2-star-ocean-the-second_characters_sea-of-stars-style-direction_v01_20261020-181026-f5938409.md",
         "view_contract": CONTRACT_REL,
         "source_contract": "same as Milo south v01: 80x112, pivot (40,104), body rows 8..103, display scale 0.5 = "
                            "48 logical px, binary alpha, transparent border, same declared 40-entry palette, "
                            "24..48 used colours, >=8 genuine role layers, hidden guides layer",
         "gate_swap": "south face_has_eye replaced by the reused Lin author's north_face_no_eyes_or_mouth",
         "author_tool": "tools/" + os.path.basename(__file__), "reused_tool_pins": {**PINS, **MS.PINS},
         "serialization_helper": S.HELPER_REL,
         "pixel_source": "code-authored native pixels, declared palette",
         "limitations": "north static only; no runtime wiring, no east/west, no motion, no creator art approval"}
    return (json.dumps(m, indent=2) + "\n").encode()


def main():
    cmd = sys.argv[1] if len(sys.argv) > 1 else "check"
    r1, r2 = artifacts(), artifacts()
    g = gates(r1)
    g["deterministic_rebuild"] = all(a == b for a, b in zip(r1[3:], r2[3:]))
    su = south_unchanged()
    bad = [k for k in HARD + ["deterministic_rebuild"] if not g[k]]
    bad += [f"tool_pin:{rel}" for rel, ok in {**PIN_OK, **MS.PIN_OK}.items() if not ok]
    bad += [f"south:{k}" for k, v in su.items() if not v]
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
        os.makedirs(fs("outputs/milo-n01/scratch"), exist_ok=True)
        Image.fromarray(r1[2], "RGBA").resize((W * 6, H * 6), Image.NEAREST).save(
            fs("outputs/milo-n01/scratch/milo-north-draft-x6.png"))
    disk = {rel: (sha(open(fs(rel), "rb").read()) == sha(b)) if os.path.exists(fs(rel)) else None
            for rel, b in named.items()}
    report = {k: g[k] for k in ("body_rows", "colour_count", "genuine_visible_role_layers", "visible_role_texels",
                                "isolated_texels", "silhouette_width", "identity_colours_visible", "binary_alpha",
                                "no_opaque_border", "pin_inside_feet_span", "all_colours_declared", "ora_hidden",
                                "north_face_no_eyes_or_mouth", "deterministic_rebuild")}
    report.update(tool_pins_ok={**PIN_OK, **MS.PIN_OK}, south_unchanged=su, disk_matches_rebuild=disk,
                  hard_failures=bad)
    print(json.dumps(report, indent=1))
    ok = not bad and all(v is True for v in disk.values())
    print("MILO_NORTH_V01_" + ("ALL_OK" if ok else "FAIL"))
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
