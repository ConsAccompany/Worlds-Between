"""Independent checker for the Heya four-direction idle source bank (i159).

Recomputes from PNG/PXO/ORA/palette bytes only; does not import the author tool. Real negative controls mutate
temporary copies and must make the same validator fail. Writes only NEW reports under outputs/heya-i159/qa.
"""
import argparse, hashlib, io, json, os, shutil, sys, tempfile, zipfile
from datetime import datetime, timezone
import xml.etree.ElementTree as ET
import numpy as np
from PIL import Image

ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
DIRS = ("south", "west", "north", "east")
HEAD = {"face", "hair", "braid", "scarf"}
TORSO = {"dress", "coat", "apron", "belt", "strap", "bag", "herb"}
ARMS = {"arms"}
ROLES = ["boots", "dress", "coat", "apron", "belt", "strap", "bag", "arms", "herb", "face", "hair", "braid",
         "scarf"]
W, H, PIN, BODY = 80, 112, [40, 104], [8, 103]
DUR = [700, 200, 400, 200]
OFF = [(0, 0, 0), (1, 1, 0), (1, 1, 1), (0, 1, 1)]


def sha(b):
    return hashlib.sha256(b).hexdigest()


def rb(p):
    with open(p, "rb") as f:
        return f.read()


def dec(b):
    return np.array(Image.open(io.BytesIO(b)).convert("RGBA"))


def shift(a, dy):
    if dy == 0:
        return a.copy()
    o = np.zeros_like(a)
    ys, xs = np.nonzero(a[..., 3])
    ny = ys + dy
    ok = (ny >= 0) & (ny < a.shape[0])
    o[ny[ok], xs[ok]] = a[ys[ok], xs[ok]]
    return o


def over(ls):
    o = np.zeros_like(ls[0])
    for a in ls:
        al = a[..., 3:4].astype(np.uint16)
        o[..., :3] = (a[..., :3].astype(np.uint16) * al + o[..., :3].astype(np.uint16) * (255 - al)) // 255
        o[..., 3:4] = np.maximum(o[..., 3:4], a[..., 3:4])
    return o.astype(np.uint8)


def read_ora(p):
    z = zipfile.ZipFile(io.BytesIO(rb(p)))
    rows = ET.fromstring(z.read("stack.xml")).find("stack").findall("layer")
    out, hidden = {}, []
    for e in reversed(rows):
        out[e.get("name")] = dec(z.read(e.get("src")))
        if e.get("visibility") == "hidden":
            hidden.append(e.get("name"))
    return out, hidden


def validate(root):
    fails, checks, data = [], [], {}
    manpaths = {}
    for d in DIRS:
        hits = [os.path.join(root, d, f) for f in os.listdir(os.path.join(root, d)) if "manifest" in f]
        if len(hits) != 1:
            fails.append(f"{d}: manifest count {len(hits)}")
            continue
        manpaths[d] = hits[0]
        m = json.loads(rb(hits[0]))
        data[d] = m
        x = m["directions"]
        if m["canvas"] != [W, H] or m["pivot"] != PIN or m["body_rows"] != BODY:
            fails.append(f"{d}: contract")
        if (m["frame_durations_ms"] != DUR or m["cycle_ms"] != 1500 or not m["loop"] or
                [fr["duration_ms"] for fr in x["frames"]] != DUR):
            fails.append(f"{d}: timing")
        sfile = x["static_png"]["file"]
        staticp = os.path.join(ROOT, sfile) if "/" in sfile else os.path.join(
            ROOT, "game/assets/characters/heya-native-v01", d, sfile)
        static = dec(rb(staticp))
        if sha(rb(staticp)) != x["static_png"]["sha256"]:
            fails.append(f"{d}: static input hash")
        pal = json.loads(rb(os.path.join(root, d, x["palette_copy"]["file"])))["colors"]
        pset = {tuple(int(v[i:i + 2], 16) for i in (0, 2, 4)) for v in pal.values()}
        if sha(rb(os.path.join(root, d, x["palette_copy"]["file"]))) != x["palette_copy"]["sha256"]:
            fails.append(f"{d}: palette copy hash")
        frames = []
        for fr in x["frames"]:
            p = os.path.join(root, d, fr["file"])
            b = rb(p)
            if sha(b) != fr["sha256"]:
                fails.append(f"{d}: frame {fr['index']} hash")
            a = dec(b)
            frames.append(a)
            if a.shape != (H, W, 4) or set(np.unique(a[..., 3])) - {0, 255}:
                fails.append(f"{d}: frame {fr['index']} alpha/shape")
            if a[0].any() or a[-1].any() or a[:, 0].any() or a[:, -1].any():
                fails.append(f"{d}: frame {fr['index']} border")
            used = {tuple(int(v) for v in r[:3]) for r in a.reshape(-1, 4) if r[3]}
            if not used <= pset:
                fails.append(f"{d}: frame {fr['index']} palette")
        if not (len(frames) == 4 and np.array_equal(frames[0], static)):
            fails.append(f"{d}: f00 != static")
        ora, hidden = read_ora(os.path.join(root, d, x["static_layers_ora"]["file"]))
        if list(ora) != ROLES + ["guides"] or hidden != ["guides"]:
            fails.append(f"{d}: ORA layer order/hidden")
        elif not np.array_equal(over([ora[n] for n in ROLES]), static):
            fails.append(f"{d}: ORA != static")
        pxo = zipfile.ZipFile(io.BytesIO(rb(os.path.join(root, d, x["animated_pxo"]["file"]))))
        j = json.loads(pxo.read("data.json"))
        if not (j["pxo_version"] == 7 and j["fps"] == 10.0 and len(j["frames"]) == 4 and
                [f["duration"] for f in j["frames"]] == [7.0, 2.0, 4.0, 2.0] and
                [l["name"] for l in j["layers"]] == ROLES + ["guides"] and
                j["layers"][-1]["visible"] is False and j["layers"][-1]["locked"] is True and
                j["tags"] == [{"name": "idle", "from": 1, "to": 4, "color": "8e3b36"}]):
            fails.append(f"{d}: PXO metadata")
        try:
            declared = json.loads(j["user_data"])["declared_palette"]
            cols = declared["colors"]
            pcol = {tuple(int(round(float(v.strip()) * 255)) for v in cols[k]["color"].strip("()").split(",")[:3])
                    for k in cols}
            if not pset <= pcol:
                fails.append(f"{d}: PXO declared palette missing source colours")
        except Exception as e:
            fails.append(f"{d}: PXO user_data {e}")
        # per-frame layer cells must be exact vertical shifts of the static role layer
        exact = True
        for i, a in enumerate(frames):
            t, h, ar = OFF[i]
            for li, n in enumerate(ROLES, 1):
                cell = np.frombuffer(pxo.read(f"image_data/frames/{i + 1}/layer_{li}"), np.uint8).reshape((H, W, 4))
                dy = h if n in HEAD else (t if n in TORSO else (ar if n in ARMS else 0))
                exact &= np.array_equal(cell, shift(ora[n], dy))
            comp = over([np.frombuffer(pxo.read(f"image_data/frames/{i + 1}/layer_{li}"), np.uint8).reshape((H, W, 4))
                         for li in range(1, len(ROLES) + 1)])
            exact &= np.array_equal(comp, a)
        if not exact:
            fails.append(f"{d}: PXO cells are not exact model shifts")
        if not all(np.array_equal(frames[i][90:104], static[90:104]) for i in range(4)):
            fails.append(f"{d}: lower-body/sole rows move")
        if not np.array_equal(pxo.read("image_data/frames/1/layer_1"),
                              pxo.read("image_data/frames/4/layer_1")):
            fails.append(f"{d}: boots layer not planted")
        ch = [int(np.count_nonzero(np.any(frames[i] != frames[(i - 1) % 4], axis=2))) for i in range(4)]
        if not all(0 < c <= 900 for c in ch):
            fails.append(f"{d}: motion/loop closure {ch}")
        checks.append({"direction": d, "frames": len(frames), "changed_pixels_cycle": ch,
                       "f00_exact_static": np.array_equal(frames[0], static)})
    return fails, checks, manpaths, data


def mutate(src, label, mutator):
    td = tempfile.mkdtemp(prefix="wb-heya-i159-neg-")
    root = os.path.join(td, "idle")
    shutil.copytree(src, root)
    mutator(root)
    fails, _, _, _ = validate(root)
    return {"control": label, "rejected": bool(fails), "observed_fails": fails[:4], "temp": td}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", default="game/assets/characters/heya-native-v01/idle")
    ap.add_argument("--out", default="outputs/heya-i159/qa")
    a = ap.parse_args()
    root = os.path.join(ROOT, a.root) if not os.path.isabs(a.root) else a.root
    fails, checks, manpaths, data = validate(root)

    def first(d, suffix):
        return os.path.join(root, d, [f for f in os.listdir(os.path.join(root, d)) if suffix in f][0])

    def flip_png(r):
        p = [os.path.join(r, "south", f) for f in os.listdir(os.path.join(r, "south")) if "-f01_" in f][0]
        im = Image.open(p).convert("RGBA")
        arr = np.array(im)
        ys, xs = np.nonzero(arr[..., 3])
        y, x = int(ys[len(ys) // 2]), int(xs[len(xs) // 2])
        arr[y, x, :3] = 255 - arr[y, x, :3]
        arr[y, x, 3] = 255
        Image.fromarray(arr).save(p)

    def change_duration(r):
        p = [os.path.join(r, "west", f) for f in os.listdir(os.path.join(r, "west")) if "animated" in f][0]
        z = zipfile.ZipFile(p)
        out = io.BytesIO()
        with zipfile.ZipFile(out, "w", zipfile.ZIP_DEFLATED) as o:
            for i in z.infolist():
                b = z.read(i.filename)
                if i.filename == "data.json":
                    j = json.loads(b); j["frames"][1]["duration"] = 3.0; b = json.dumps(j).encode()
                o.writestr(i, b)
        open(p, "wb").write(out.getvalue())

    def alter_ora(r):
        p = [os.path.join(r, "north", f) for f in os.listdir(os.path.join(r, "north")) if "static-layers" in f][0]
        z = zipfile.ZipFile(p)
        out = io.BytesIO()
        with zipfile.ZipFile(out, "w", zipfile.ZIP_DEFLATED) as o:
            for i in z.infolist():
                b = z.read(i.filename)
                if i.filename == "data/boots.png":
                    arr = dec(b); arr[90, 40, :3] = [1, 2, 3]; arr[90, 40, 3] = 255
                    buf = io.BytesIO(); Image.fromarray(arr).save(buf, "PNG"); b = buf.getvalue()
                o.writestr(i, b)
        open(p, "wb").write(out.getvalue())

    controls = [mutate(root, "png_pixel_flip", flip_png), mutate(root, "pxo_frame_duration", change_duration),
                mutate(root, "ora_static_pixel", alter_ora)]
    # manifest duration mutation
    def man_duration(r):
        p = [os.path.join(r, "east", f) for f in os.listdir(os.path.join(r, "east")) if "manifest" in f][0]
        m = json.loads(rb(p)); m["directions"]["frames"][2]["duration_ms"] = 900
        open(p, "w").write(json.dumps(m))
    controls.append(mutate(root, "manifest_duration", man_duration))
    # palette mutation
    def pal_mut(r):
        p = [os.path.join(r, "south", f) for f in os.listdir(os.path.join(r, "south")) if "palette" in f][0]
        j = json.loads(rb(p)); j["colors"]["s1"] = "010203"; open(p, "w").write(json.dumps(j))
    controls.append(mutate(root, "palette_colour", pal_mut))
    neg_ok = all(c["rejected"] for c in controls)
    if not neg_ok:
        fails.append("negative controls not all rejected")
    report = {"task": "content.char.heya.idle-anim independent source check", "status": "UNAPPROVED",
              "root": os.path.relpath(root, ROOT), "passed": not fails, "checks": checks,
              "negative_controls": controls, "negative_controls_all_rejected": neg_ok,
              "failures": fails, "limitations": ["no Pixelorama export", "no Godot runtime", "no human review"],
              "generated_utc": datetime.now(timezone.utc).isoformat()}
    os.makedirs(os.path.join(ROOT, a.out), exist_ok=True)
    rid = datetime.now(timezone.utc).strftime("%Y%m%d-%H%M%S")
    path = os.path.join(ROOT, a.out, f"rpg-2-star-ocean-the-second_heya_idle-independent-check_v01_{rid}.json")
    open(path, "w").write(json.dumps(report, indent=2) + "\n")
    print(json.dumps({"report": os.path.relpath(path, ROOT), "passed": not fails, "directions": len(checks),
                      "negative_controls": len(controls), "negative_all_rejected": neg_ok,
                      "failures": fails}, indent=2))
    return 0 if not fails else 1


if __name__ == "__main__":
    sys.exit(main())
