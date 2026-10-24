"""Muxiu WEST idle static, native 80x112 source package (UNAPPROVED v01).

content.char.muxiu.static-west. Code-authored native pixels in the Sea of Stars direction (broad clusters,
upper-left light), 48 logical px at display scale 0.5. West = nose toward screen LEFT, so the character's LEFT
side faces the camera. Reauthored in forward coordinates with the Lin Que `P` pen (s = -1); it is not a
rotation, squash, recolour or mirror of south.

Identity (Bible character-06 via the Muxiu south v01 manifest; unapproved character sheet as identity reference
only, no pixels sampled): messy wavy dark-brown hair; the long braid is gathered at the nape and drapes over the
FAR (right) shoulder, so in profile it shows as a root knot at the nape and a plait hanging past the chest front
(screen left) with tan tie and tuft; moss-green short hooded capelet flaring back in an A-line, hood bunched behind
the neck, cream tree motif band, fringed hem; cream shirt at the open collar, under the hem and as the rolled
near sleeve; small wooden whistle on a tan cord at the chest front; knotted green/tan rope bracelet on the NEAR
(left) wrist; brown belt with front buckle, near hip pouch and far pouch peeking behind; olive-brown trousers with
near knee patch; green leg wraps with cream band and tan cords; brown boots, far leg darker and set slightly ahead.

Reuses the hash-pinned Muxiu south v01 author in memory (and through it Lin Que v01 `P`/finish/gates, Jiang v01
gates and the male v8pair PNG/PXO/ORA serializers) with the same palette, layers, outline colours and HARD gates.
Only the direction label is rebound in memory; the south tool and the committed south package stay byte-identical,
which this author verifies against the pinned south manifest.

  python -X utf8 -I <this> preview # content-named preview only (outputs/muxiu-w01/author), no source files
  python -X utf8 -I <this> build   # writes new files only (refuses to overwrite different bytes)
  python -X utf8 -I <this> check   # rebuilds twice in memory and compares with files on disk
"""
import hashlib, importlib.util, io, json, os, sys, zipfile

REPO = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
SLUG, ACTOR, D = "rpg-2-star-ocean-the-second", "muxiu", "west"
STAMP, RUN_ID = "20261024-055215", "20eb2717"
OUT_REL = "game/assets/characters/muxiu-native-v01/west"
QA_REL = "outputs/muxiu-w01/author"
SOUTH_TOOL_REL = "tools/rpg-2-star-ocean-the-second_muxiu_south-static-author_unapproved-v01_20261024-071500-6d3e9a51.py"
SOUTH_DIR_REL = "game/assets/characters/muxiu-native-v01/south"
SOUTH_MANIFEST_REL = SOUTH_DIR_REL + "/rpg-2-star-ocean-the-second_muxiu_south-manifest_unapproved-v01_20261024-071500-dd478113.json"
PINS = {SOUTH_TOOL_REL: "f329ac7aa595f003ba741ed8de6cf5aade1d912acfa65a1720ce731eb24737f1",   # committed f556e74e
        SOUTH_MANIFEST_REL: "24c751575fe02a4857628dbfb8b379cd1d42344167062ae8ddbb033024e114de"}


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
_spec = importlib.util.spec_from_file_location("muxiu_south_v01_for_west", fs(SOUTH_TOOL_REL))
MS = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(MS)                                   # pins Lin/Jiang/male/Milo tools itself (MS.PIN_OK)
MS.D = D                                                      # rebind the direction label in memory only
M, S = MS.M, MS.S
PAL, LAYERS, FILE_KEYS = MS.PAL, MS.LAYERS, MS.FILE_KEYS
W, H, PIN, BODY_ROWS, L = MS.W, MS.H, MS.PIN, MS.BODY_ROWS, MS.L


# ------------------------------------------------------------------ west (profile, nose to screen left)
def draw_west(Ls):
    """Forward coordinates: f > 0 is the facing direction (screen x = 40 - f). Light stays upper-left on screen,
    so P.shaded puts the highlight on the front (screen-left) edge."""
    p = {n: M.P(Ls[n], -1) for n in LAYERS}

    # boots: near boot with folded cuff and laces; far boot darker, set a little ahead
    b = p["boots"]
    b.shaded(-1, 92, 7, 101, "r2", "r2", "r3", 1, 1); b.rect(8, 97, 9, 101, "r2")      # far boot + toe
    b.shaded(-5, 92, 4, 101, "r1", "r2", "r3", 2, 2)
    b.rect(-5, 92, 4, 93, "r2"); b.rect(-5, 92, 4, 92, "r1")                           # cuff
    b.rect(1, 95, 3, 97, "q2")                                                         # laces
    b.shaded(5, 97, 7, 101, "r1", "r1", "r2", 1, 1)                                    # near toe
    b.rect(-6, 99, -6, 102, "r3"); b.rect(-6, 102, 9, 102, "r3")                       # heel, welt
    b.rect(-6, 103, 9, 103, "k1")                                                      # sole

    # leg wraps: green cloth, cream top band, broad tan cord bands; far leg darker
    lw = p["legwraps"]
    lw.shaded(-1, 82, 5, 91, "c3", "c3", "c3", 1, 1)
    lw.rect(-1, 82, 5, 83, "w3"); lw.rect(-1, 86, 5, 86, "q2")
    lw.shaded(-5, 82, 2, 91, "c2", "c2", "c3", 2, 2)
    lw.rect(-5, 82, 2, 82, "w2"); lw.rect(-5, 83, 2, 83, "w3")                         # cream top band
    lw.rect(-5, 85, 2, 85, "q2"); lw.rect(-5, 88, 2, 88, "q2")                         # cord bands
    lw.rect(-3, 86, -1, 87, "q1")                                                      # cord knot

    # trousers: olive-brown, loose; far leg darker and ahead; patch on the near knee
    t = p["trousers"]
    t.rect(-8, 64, 6, 70, "t2")
    t.shaded(-1, 70, 5, 83, "t2", "t3", "t4", 1, 1)
    t.shaded(-6, 70, 2, 83, "t1", "t2", "t3", 2, 2)
    t.rect(-1, 75, 2, 79, "t3"); t.rect(-1, 75, 2, 75, "t4")                           # knee patch

    # shirt: cream; open collar at the throat, band between capelet hem and belt
    sh = p["shirt"]
    sh.rows({32: (1, 4), 33: (1, 5), 34: (1, 6), 35: (2, 6), 36: (3, 6)}, "w1")
    sh.rect(1, 34, 2, 36, "w2")                                                        # collar fold
    sh.shaded(-9, 55, 7, 61, "w1", "w2", "w3", 2, 3)

    # belt: brown leather, brass buckle at the front
    bl = p["belt"]
    bl.rect(-9, 61, 7, 64, "r2"); bl.rect(-9, 61, 7, 61, "r1"); bl.rect(-9, 64, 7, 64, "r3")
    bl.rect(4, 61, 7, 64, "y1"); bl.rect(5, 62, 6, 63, "r3")

    # pouches: near (left) hip pouch at the back hip; larger far (right) pouch peeks out behind
    pc = p["pouches"]
    pc.shaded(-13, 63, -10, 70, "r2", "r2", "r3", 1, 2); pc.rect(-13, 63, -10, 64, "r3")
    pc.shaded(-9, 62, -4, 71, "r1", "r2", "r3", 2, 2); pc.rect(-9, 62, -4, 65, "r3"); pc.rect(-9, 62, -4, 62, "r2")
    pc.rect(-7, 66, -6, 67, "y1")

    # cloak: moss-green short hooded capelet; hood bunched behind the neck, A-line flare to the back
    c = p["cloak"]
    rows = {}
    for y in range(33, 59):
        k = y - 33
        rows[y] = (-6 - min(k, 10) // 2 - max(0, k - 10) // 3, 4 + min(k, 8) // 2 + max(0, k - 8) // 8)
    c.rows(rows, "c2")
    for y, (b0, f0) in rows.items():                            # light plane at the front, shadow at the back
        c.rect(f0 - 2, y, f0, y, "c1"); c.rect(b0, y, b0 + 3, y, "c3")
    c.rows({y: (-7, 2) for y in range(33, 36)}, "c1")           # shoulder top catches the light
    c.rows({28: (-9, -5), 29: (-11, -4), **{y: (-12, -3) for y in range(30, 35)}}, "c3")   # hood roll
    c.rows({29: (-9, -6), 30: (-10, -6), 31: (-11, -7)}, "c2")
    for y in range(50, 54):                                     # cream tree motif band
        c.rect(rows[y][0] + 3, y, rows[y][1] - 2, y, "c3")
    for mf in (1, -9):
        c.rect(mf, 49, mf, 54, "w2"); c.rect(mf - 1, 50, mf + 1, 50, "w2"); c.rect(mf - 2, 52, mf + 2, 52, "w2")
    for y in range(55, 59):                                     # fringe
        c.rect(rows[y][0], y, rows[y][1], y, "c3")
    b0, f0 = rows[58]
    for ff in range(f0 - 1, b0 - 1, -4):
        c.rect(ff - 1, 59, ff, 61, "q2"); c.rect(ff - 1, 59, ff, 59, "c3")

    # arms: near (left) forearm below the capelet, cream rolled sleeve, relaxed hand with thumb forward
    a = p["arms"]
    a.shaded(-2, 57, 4, 62, "w1", "w2", "w3", 2, 2); a.rect(-2, 62, 4, 62, "w3")       # rolled sleeve
    a.shaded(-1, 63, 3, 69, "s1", "s2", "s3", 2, 1)
    a.shaded(-1, 70, 3, 75, "s2", "s2", "s3", 1, 1); a.rect(-1, 76, 3, 76, "s3")
    a.rect(-1, 72, 3, 72, "s3")                                                        # knuckle line
    a.rect(4, 70, 5, 72, "s2")                                                         # thumb

    # bracelet: knotted green/tan rope on the near (left) wrist
    q = p["bracelet"]
    q.rect(-2, 67, 4, 69, "c2")
    for ff in range(-2, 5, 2):
        q.rect(ff, 67, ff, 69, "q1")
    q.rect(1, 70, 2, 71, "c3")                                                         # dangling knot

    # whistle: tan cord from the collar, small wooden whistle hanging at the chest front
    wh = p["whistle"]
    for i in range(5):
        wh.rect(2 + i, 33 + i, 3 + i, 33 + i, "q2")
    wh.rect(5, 38, 7, 38, "y1")                                                        # brass ring
    wh.shaded(5, 39, 7, 45, "x1", "x1", "x2", 1, 1); wh.rect(5, 45, 7, 45, "x2")
    wh.rect(5, 41, 7, 41, "q2")                                                        # cord wrap

    # face: profile, one brown-green eye, brow, nose leading left, ear mid-head, smile corner
    fc = p["face"]
    fc.rows({**{y: (-4, 7) for y in range(14, 23)}, **{y: (-4, 8) for y in range(23, 28)}, 28: (-4, 7),
             29: (-4, 7), 30: (-3, 7), 31: (-2, 6), 32: (0, 5)}, "s2")
    fc.rows({23: (9, 9), 24: (9, 10), 25: (9, 10)}, "s2"); fc.rect(9, 23, 9, 24, "s1"); fc.rect(8, 26, 9, 26, "s3")
    fc.rect(5, 18, 7, 22, "s1"); fc.rect(-4, 18, -3, 29, "s3")                        # lit front / shaded back
    fc.rect(-3, 33, 2, 36, "s3"); fc.rect(0, 33, 2, 35, "s2")                          # neck
    fc.rect(-3, 21, -1, 26, "s3"); fc.rect(-2, 22, -1, 25, "s2")                       # ear
    fc.rect(3, 20, 7, 20, "h3")                                                        # soft brow
    fc.rect(3, 22, 6, 22, "h4"); fc.rect(3, 23, 3, 24, "e1"); fc.rect(4, 23, 5, 24, "e2"); fc.px(5, 23, "h4")
    fc.rect(5, 29, 7, 29, "m1"); fc.px(5, 28, "m1")                                    # easy smile corner
    fc.rect(4, 26, 5, 27, "s1")                                                        # cheek plane

    # hair: messy wavy dark brown; tufted crown, fringe swept forward, lock before the ear, full back to the nape
    h = p["hair"]
    h.rows({8: (-3, 2), 9: (-7, 4), 10: (-9, 6), **{y: (-10, 7) for y in range(11, 15)},
            **{y: (-10, 8) for y in range(15, 18)}, **{y: (-10, -1) for y in range(18, 21)},
            **{y: (-10, -4) for y in range(21, 27)}, **{y: (-10, -5) for y in range(27, 30)}}, "h2")
    h.rows({8: (-9, -7), 9: (-10, -8)}, "h3")                                          # back crown tuft
    h.rows({18: (4, 8), 19: (5, 8)}, "h2")                                             # fringe lock tips
    h.rect(0, 19, 1, 25, "h3")                                                         # side lock before the ear
    h.rows({9: (0, 3), 10: (0, 5), 11: (1, 6), 12: (2, 5)}, "h1")                      # upper-left sheen
    h.rows({14: (3, 5), 15: (4, 6)}, "h1"); h.rect(-9, 12, -8, 16, "h1")
    h.rect(-10, 17, -8, 29, "h3"); h.rows({12: (-3, -2), 13: (-2, -1), 14: (-1, 0)}, "h3")  # back plane, wave break
    h.rows({11: (-12, -11), 12: (-12, -11), 15: (-12, -11), 16: (-11, -11)}, "h3")     # messy back locks

    # braid: gathered knot at the nape, then the plait over the far shoulder hangs past the chest front
    br = p["braid"]
    for y in range(27, 33):
        br.rect(-9, y, -6, y, "h2" if (y // 2) % 2 else "h3")
    br.rect(-9, 27, -8, 30, "h1")
    br.rows({32: (5, 7), 33: (6, 8)}, "h3")                                            # crest over the far shoulder
    for i, y in enumerate(range(34, 60)):
        f0 = 7 + min(i, 4) // 2
        seg = (i // 3) % 2
        br.rect(f0, y, f0 + 2, y, "h2" if seg == 0 else "h3")
        br.px(f0 + 2 - 2 * seg, y, "h1" if seg == 0 else "h4")
    br.rect(8, 60, 12, 61, "q1"); br.rect(8, 61, 12, 61, "q2")                         # tan tie
    br.rows({62: (8, 12), 63: (8, 13), 64: (8, 13), 65: (9, 12), 66: (9, 11)}, "h2")   # tuft
    br.rows({63: (12, 13), 64: (12, 13)}, "h1"); br.rows({65: (9, 10), 66: (9, 10)}, "h3")


def draw():
    Ls = {n: L() for n in LAYERS}
    draw_west(Ls)
    return M.finish(Ls)


# ------------------------------------------------------------------ package
def artifacts():
    hp = S.load_helper()
    hp.ZIP_DT, hp.LAYERS, hp.PAL = MS.ZIP_DT, LAYERS, PAL
    blobs = draw()
    full = S.compose_layers(blobs)
    png = hp.png_bytes(full)
    pxo = MS.fix_pxo_metadata(hp.make_pxo(blobs, png))           # labels use the rebound direction (west)
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
    g = MS.gates(r)
    with zipfile.ZipFile(io.BytesIO(r[4])) as z:
        dj = z.read("data.json")
    g["pxo_labels_west"] = b"muxiu-west" in dj and b"muxiu-south" not in dj
    return g


HARD = MS.HARD + ["pxo_labels_west"]


def manifest(files, g):
    m = {"actor_id": ACTOR, "content_id": f"content.char.{ACTOR}.static-{D}", "status": "UNAPPROVED",
         "direction": D, "pose": "idle-static", "canvas": [W, H], "pivot": list(PIN), "body_rows": list(BODY_ROWS),
         "display_scale": S.DISPLAY_SCALE, "logical_height_px": (BODY_ROWS[1] - BODY_ROWS[0] + 1) * S.DISPLAY_SCALE,
         "layers": [{"name": n, "visible": n != "guides"} for n in LAYERS],
         "face_layer_role": "profile face, one brown-green eye, soft brow, nose leading screen left, ear, smile corner, neck",
         "view_notes": "west profile (nose to screen left; the character's LEFT side faces the camera): messy wavy "
                       "dark-brown hair with forward fringe, lock before the ear and full back; braid gathered at the "
                       "nape and draped over the far (right) shoulder, hanging past the chest front with tan tie and "
                       "tuft; moss-green short hooded capelet, hood bunched behind the neck, A-line flare to the back, "
                       "cream tree motif band and fringed hem; cream shirt at the open collar, under the hem and as "
                       "the rolled near sleeve; small wooden whistle on a tan cord at the chest front; knotted "
                       "green/tan rope bracelet on the near (left) wrist; brown belt with front brass buckle, near hip "
                       "pouch, far pouch peeking behind; olive-brown trousers with near knee patch; green leg wraps "
                       "with cream band and tan cords; brown boots, far leg darker and set slightly ahead",
         "authored_deviations_from_sheet": [
             "pose: neutral profile idle with the near arm down; the sheet's 3/4 pose has the right hand at the clasp.",
             "braid: the far-shoulder drape is shown as a nape knot plus the plait hanging past the chest front, an "
             "explicit profile readability choice continuous with south v01 (the sheet's back view differs).",
             "chest straps and extra belt charms/cloth tatters omitted for 48 px readability."],
         "files": {k: {"file": fname(*FILE_KEYS[k]), "rawsha256": sha(b)} for k, b in files.items()},
         "colour_count": g["colour_count"], "genuine_visible_role_layers": g["genuine_visible_role_layers"],
         "isolated_texels": g["isolated_texels"],
         "portrait_ref": {"file": MS.PORTRAIT_REL, "expected_sha256": MS.PORTRAIT_SHA, "approval": "UNAPPROVED",
                          "use": "identity reference only; no pixels sampled"},
         "continuity_ref": {"file": SOUTH_MANIFEST_REL, "rawsha256": PINS[SOUTH_MANIFEST_REL],
                            "use": "Muxiu south v01 palette/layers/outline/gates; no pixels copied"},
         "bible_ref": "character-06: 24yo animal carer; moss-green short cloak, knotted rope bracelet, small whistle, "
                      "swaying braid",
         "style_contract": "docs/design/rpg-2-star-ocean-the-second_characters_sea-of-stars-style-direction_v01_20261020-181026-f5938409.md",
         "source_contract": "same as Muxiu south v01: 80x112, pivot (40,104), body rows 8..103, display scale 0.5 = "
                            "48 logical px, binary alpha, transparent border, same declared palette, 24..48 used "
                            "colours, >=8 genuine role layers, hidden guides layer",
         "replaces_placeholder": "does not modify the old 32x48 native-animation placeholder; it is not counted",
         "author_tool": "tools/" + os.path.basename(__file__), "reused_tool_pins": {**PINS, **MS.PINS},
         "serialization_helper": S.HELPER_REL,
         "pixel_source": "code-authored native pixels, declared palette",
         "limitations": "west static only; no runtime wiring, no east/north, no motion, no creator art approval"}
    return (json.dumps(m, indent=2) + "\n").encode()


def write_new(rel, data):
    """Write new bytes only; identical existing bytes are left untouched, different bytes are refused."""
    p = fs(rel)
    if os.path.exists(p):
        if open(p, "rb").read() != data:
            raise SystemExit(f"refusing to overwrite different file {rel}")
        return
    os.makedirs(os.path.dirname(p), exist_ok=True)
    with open(p, "xb") as fh:
        fh.write(data)


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
    if cmd in ("build", "preview"):                            # content-named preview: never reuses a name
        from PIL import Image
        buf = io.BytesIO()
        Image.fromarray(r1[2], "RGBA").resize((W * 6, H * 6), Image.NEAREST).save(buf, "PNG")
        prev = f"{QA_REL}/{SLUG}_{ACTOR}_{D}-preview-x6_unapproved-v01_{STAMP}-{sha(r1[3])[:8]}.png"
        write_new(prev, buf.getvalue())
        print("preview:", prev, sha(buf.getvalue()))
    if cmd == "build":
        if bad:
            raise SystemExit(f"hard gates failed: {bad}")
        if not os.path.isfile(fs("game/assets/characters/muxiu-native-v01/.gdignore")):
            raise SystemExit("missing parent .gdignore (created by south v01); not recreated here")
        for rel, data in named.items():
            write_new(rel, data)
        listing = {"outputs": {rel: sha(b) for rel, b in sorted(named.items())},
                   "qa_preview_nonsource": {prev: sha(open(fs(prev), "rb").read())}, "hash": "sha256 of raw bytes"}
        write_new(f"{QA_REL}/{SLUG}_{ACTOR}_{D}-output-paths-rawhashes_unapproved-v01_{STAMP}-{uid('paths')}.json",
                  (json.dumps(listing, indent=2) + "\n").encode())
    disk = {rel: (sha(open(fs(rel), "rb").read()) == sha(b)) if os.path.exists(fs(rel)) else None
            for rel, b in named.items()}
    report = {k: g[k] for k in ("body_rows", "colour_count", "genuine_visible_role_layers", "visible_role_texels",
                                "isolated_texels", "silhouette_width", "identity_colours_visible", "binary_alpha",
                                "no_opaque_border", "pin_inside_feet_span", "all_colours_declared", "ora_hidden",
                                "face_has_eye", "deterministic_rebuild")}
    report.update(tool_pins_ok={**PIN_OK, **MS.PIN_OK}, south_unchanged=su, disk_matches_rebuild=disk,
                  hard_failures=bad)
    print(json.dumps(report, indent=1))
    ok = not bad and all(v is True for v in disk.values())
    print("MUXIU_WEST_V01_" + ("ALL_OK" if ok else "FAIL"))
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
