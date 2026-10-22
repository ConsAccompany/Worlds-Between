#!/usr/bin/env python3
"""Independent source check for content.char.jiang-lan.static-south.

Read-only over the game tree; writes only to --out. Art stays UNAPPROVED.
Usage:
  python ...py --root . --out outputs/jiang37/deepseek
Optional explicit refs: --png PATH --ora PATH --source-portrait PATH
Exit: 0 pass, 1 failure, 2 source manifest absent (explicit pending).
"""
from __future__ import annotations
import argparse, hashlib, io, json, re, shutil, sys, zipfile
from pathlib import Path
from xml.etree import ElementTree as ET
from PIL import Image

TASK = "content.char.jiang-lan.static-south"
REL = "game/assets/characters/jiang-lan-native-south-v01"
W, H = 80, 112
PIVOT, BODY_H, SCALE = (40, 104), 96, 0.5
PALETTE_MAX, ROLE_MIN = 48, 8
ROLE_WORDS = {
    "body": ("body", "torso", "base"), "head": ("head", "face", "skin"),
    "hair": ("hair", "ponytail", "bangs"), "eyes": ("eye", "brow", "lash"),
    "mouth": ("mouth", "lip"), "outfit": ("outfit", "tunic", "dress", "coat", "jacket",
    "shirt", "robe", "uniform", "clothes", "cloak", "armor"),
    "arms": ("arm", "hand", "glove", "sleeve"), "legs": ("leg", "thigh", "pant",
    "trouser", "boot", "shoe", "foot", "feet", "sock"),
    "belt": ("belt", "sash", "strap", "buckle"),
    "accessory": ("accessory", "badge", "pendant", "necklace", "bag", "pouch", "scarf", "hat"),
}
GUIDE_RE = re.compile(r"guide|pivot|ref|sketch|skeleton|measure", re.I)


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def dig(obj, keys):
    """Deep first-key lookup (manifest schemas vary)."""
    if isinstance(obj, dict):
        for k in keys:
            if k in obj:
                return obj[k]
        for v in obj.values():
            r = dig(v, keys)
            if r is not None:
                return r
    elif isinstance(obj, list):
        for v in obj:
            r = dig(v, keys)
            if r is not None:
                return r
    return None


def refs(obj, ext):
    found = []
    def walk(x):
        if isinstance(x, dict):
            p = x.get("path") or x.get("file") or x.get("src")
            h = x.get("rawsha256") or x.get("sha256") or x.get("hash")
            if isinstance(p, str) and p.lower().endswith(ext) and isinstance(h, str):
                found.append((p, h))
            for v in x.values():
                walk(v)
        elif isinstance(x, list):
            for v in x:
                walk(v)
    walk(obj)
    return found


def resolve(root: Path, base: Path, rel: str) -> Path | None:
    for cand in (base / rel, root / rel, root / "game" / rel):
        if cand.is_file():
            return cand.resolve()
    return None


def primary_ref(m, ext, base: Path, root: Path):
    """Prefer explicit export/static refs; exclude portrait refs."""
    hits = refs(m, ext)
    for want in ("static", "south", "export", "sprite", "png"):
        for p, h in hits:
            if want in p.lower() and "portrait" not in p.lower():
                q = resolve(root, base, p)
                if q:
                    return q, h
    for p, h in hits:
        if "portrait" not in p.lower() and "source" not in p.lower():
            q = resolve(root, base, p)
            if q:
                return q, h
    for k in ("png", "export", "output", "image"):
        v = m.get(k)
        if isinstance(v, str) and v.lower().endswith(ext):
            h = m.get(k + "Sha256") or m.get("sha256")
            q = resolve(root, base, v)
            if q and isinstance(h, str):
                return q, h
    return None


def portrait_ref(m, base: Path, root: Path):
    node = dig(m, ("portrait_ref", "sourcePortrait", "source_portrait", "sourcePortraitRef", "portraitRef"))
    if isinstance(node, dict):
        p = node.get("path") or node.get("file")
        h = node.get("sha256") or node.get("hash")
        if isinstance(p, str) and isinstance(h, str):
            q = resolve(root, base, p)
            if q:
                return q, h
    if isinstance(node, str):
        h = dig(m, ("sourcePortraitSha256", "source_portrait_sha256", "portraitSha256"))
        q = resolve(root, base, node)
        if q and isinstance(h, str):
            return q, h
    return None


def png_stats(path: Path):
    im = Image.open(path).convert("RGBA")
    px = list(im.getdata())
    alpha = {p[3] for p in px}
    opaque = [p for p in px if p[3] == 255]
    colors = {(p[0], p[1], p[2]) for p in opaque}
    bbox = im.getchannel("A").getbbox()
    border = any(px[x][3] for x in range(W)) or any(px[(H - 1) * W + x][3] for x in range(W)) or \
        any(px[y * W][3] for y in range(H)) or any(px[y * W + W - 1][3] for y in range(H))
    return dict(size=im.size, px=px, alpha_ok=alpha <= {0, 255}, bbox=bbox,
                colors=len(colors), border=bool(border), opaque=len(opaque))


def ora_layers(z: zipfile.ZipFile):
    root = ET.fromstring(z.read("stack.xml"))
    out = []
    def walk(el, parent_visible=True, parent_opacity=1.0):
        for ch in el:
            vis = parent_visible and ch.get("visibility", "visible") != "hidden"
            op = parent_opacity * float(ch.get("opacity", "1") or 1)
            if ch.tag == "layer":
                out.append(dict(name=ch.get("name", ""), src=ch.get("src", ""),
                                x=int(ch.get("x", "0")), y=int(ch.get("y", "0")),
                                visible=vis, opacity=op, op=ch.get("composite-op", "svg:src-over")))
            elif ch.tag == "stack":
                walk(ch, vis, op)
    walk(root)
    return out


def compose(z, layers):
    canvas = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    for L in reversed(layers):  # ORA XML is top-to-bottom
        if not L["visible"] or L["opacity"] <= 0 or not L["src"]:
            continue
        im = Image.open(io.BytesIO(z.read(L["src"]))).convert("RGBA")
        if L["opacity"] < 1:
            im.putalpha(im.getchannel("A").point(lambda a: int(a * L["opacity"])))
        canvas.alpha_composite(im, (L["x"], L["y"]))
    return canvas


def role_of(name: str):
    # Frozen Jiang contract: boots/trousers and face/hair/goggles are distinct editable roles.
    # Do not collapse nine genuine layers into five broader categories.
    allowed = {"boots", "trousers", "shirt", "vest", "arms", "devices", "face", "hair", "goggles"}
    return name.lower() if name.lower() in allowed else None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", default=".")
    ap.add_argument("--out", default="outputs/jiang37/deepseek")
    ap.add_argument("--png")
    ap.add_argument("--ora")
    ap.add_argument("--source-portrait")
    a = ap.parse_args()
    root, out = Path(a.root).resolve(), Path(a.out).resolve()
    src = root / REL
    out.mkdir(parents=True, exist_ok=True)
    report = {"schema": "worlds-between.jiang-lan.static-source-check.v1", "task": TASK,
              "generated": __import__("datetime").datetime.now(__import__("datetime").timezone.utc).isoformat(), "approval": "unapproved",
              "root": str(root), "source_dir": str(src), "checks": [], "hashes": {},
              "limitations": ["No GUI-clean inference from metadata.",
                              "Art/motion/default adoption are separate; output is UNAPPROVED."]}
    checks = report["checks"]
    def add(cid, ok, detail):
        checks.append({"id": cid, "ok": bool(ok), "detail": detail})

    manifests = sorted(src.glob("*manifest*.json")) if src.is_dir() else []
    if not manifests:
        report.update(status="pending-source",
                      reason=f"source manifest absent: {REL}/*manifest*.json",
                      pxo={"status": "pending", "export_root": str(out / "pxo-roundtrip")},
                      gui_clean="not_verified")
        (out / "rpg-2-star-ocean-the-second_jiang-lan_static-source-check_v01_20261021-235007-514b9771.json").write_text(
            json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
        print(json.dumps({"status": "pending-source", "manifest": str(src / "*manifest*.json")}))
        return 2

    mpath = manifests[0]
    m = json.loads(mpath.read_text(encoding="utf-8-sig"))
    report["manifest"] = str(mpath)
    report["manifest_keys"] = list(m.keys()) if isinstance(m, dict) else type(m).__name__
    report["hashes"]["manifest_sha256"] = sha256(mpath)

    png = Path(a.png).resolve() if a.png else (primary_ref(m, ".png", src, root) or (None, None))[0]
    declared_png_sha = (primary_ref(m, ".png", src, root) or (None, None))[1]
    if a.png:
        declared_png_sha = dig(m, ("pngSha256", "png_sha256"))
    ora = Path(a.ora).resolve() if a.ora else next(iter(sorted(src.glob("*.ora"))), None)

    actor = dig(m, ("actor", "actorId", "actor_id"))
    if isinstance(actor, dict):
        actor = actor.get("id")
    subject = dig(m, ("subject",))
    if actor is None and isinstance(subject, dict):
        actor = subject.get("id")
    direction = dig(m, ("direction", "facing"))
    add("actor", str(actor).lower() == "jiang-lan", f"actor={actor!r}")
    if direction is not None:
        add("direction", str(direction).lower() == "south", f"direction={direction!r}")
    scale = dig(m, ("displayScale", "display_scale", "scaleFactor"))
    if scale is None:
        scale = m.get("scale") if isinstance(m, dict) else None
    try:
        scale_ok = scale is not None and abs(float(scale) - SCALE) < 1e-9
    except (TypeError, ValueError):
        scale_ok = False
    add("scale", scale_ok, f"scale={scale!r} expected {SCALE}")
    piv = dig(m, ("pivot", "pivotPoint", "origin"))
    if isinstance(piv, dict):
        piv = [piv.get("x"), piv.get("y")]
    if isinstance(piv, str):
        try:
            piv = [int(v) for v in re.split(r"[, ]+", piv.strip())]
        except ValueError:
            pass
    try:
        pivot_ok = isinstance(piv, (list, tuple)) and len(piv) == 2 and \
            int(piv[0]) == PIVOT[0] and int(piv[1]) == PIVOT[1]
    except (TypeError, ValueError):
        pivot_ok = False
    add("pivot", pivot_ok, f"pivot={piv!r} expected {PIVOT}")

    if not png or not png.is_file():
        add("png", False, f"PNG not resolved (manifest={mpath.name})")
    if not ora or not Path(ora).is_file():
        add("ora", False, f"ORA not found under {src}")
    if not png or not png.is_file() or not ora or not Path(ora).is_file():
        report.update(status="failed")
        (out / "rpg-2-star-ocean-the-second_jiang-lan_static-source-check_v01_20261021-235007-514b9771.json").write_text(
            json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
        print(json.dumps({"status": "failed", "reason": "PNG/ORA missing"}))
        return 1

    report["hashes"]["png_sha256"] = sha256(png)
    report["hashes"]["ora_sha256"] = sha256(ora)
    actual = report["hashes"]["png_sha256"]
    add("manifest_png_hash", declared_png_sha == actual,
        f"declared={declared_png_sha!r} actual={actual}")

    st = png_stats(png)
    add("png_size", st["size"] == (W, H), f"size={st['size']} expected {(W, H)}")
    add("binary_alpha", st["alpha_ok"], "alpha values must be 0/255")
    bb = st["bbox"]
    add("body_96_texels", bb is not None and bb[1] == 8 and bb[3] == PIVOT[1] and
        bb[3] - bb[1] == BODY_H, f"bbox={bb} expected top=8 bottom={PIVOT[1]} height={BODY_H}")
    add("pivot_on_baseline", bb is not None and bb[3] == PIVOT[1], f"bbox_bottom={bb and bb[3]}")
    add("no_border", not st["border"], "no opaque pixels on the 80x112 canvas perimeter")
    add("palette_le_48", st["colors"] <= PALETTE_MAX, f"unique_opaque_rgb={st['colors']} max={PALETTE_MAX}")

    portraits = [(Path(a.source_portrait).resolve(), None)] if a.source_portrait else []
    if not portraits:
        pr = portrait_ref(m, src, root)
        portraits = [pr] if pr else []
    if not portraits:
        add("source_portrait_hash", False, "manifest source portrait ref/path+sha256 not found")
    else:
        pp, ph = portraits[0]
        if not pp or not pp.is_file():
            add("source_portrait_hash", False, f"portrait missing: {pp}")
        else:
            report["hashes"]["source_portrait_sha256"] = sha256(pp)
            add("source_portrait_hash", ph is None or ph == report["hashes"]["source_portrait_sha256"],
                f"declared={ph!r} actual={report['hashes']['source_portrait_sha256']}")

    with zipfile.ZipFile(ora) as z:
        names = set(z.namelist())
        layers = ora_layers(z)
        merged = Image.open(io.BytesIO(z.read("mergedimage.png"))).convert("RGBA") if "mergedimage.png" in names else None
        composed = compose(z, layers)
        roles, genuine = set(), 0
        for L in layers:
            if not L["visible"] or not L["src"] or L["src"] not in names:
                continue
            im = Image.open(io.BytesIO(z.read(L["src"]))).convert("RGBA")
            if sum(1 for p in im.getdata() if p[3]) >= 8:
                genuine += 1
                r = role_of(L["name"])
                if r:
                    roles.add(r)
    add("ora_merged_equals_png", merged is not None and merged.size == (W, H) and
        merged.tobytes() == bytes(b for p in st["px"] for b in p),
        "mergedimage.png pixel-equal to PNG")
    ref_px = bytes(b for p in st["px"] for b in p)
    add("ora_visible_reconstructs_png", composed.tobytes() == ref_px,
        "compositing visible ORA layers pixel-equal to PNG (top-to-bottom XML, bottom-up alpha)")

    add("role_layers_ge_8", len(roles) >= ROLE_MIN,
        f"distinct_roles={sorted(roles)} genuine_layers={genuine} min={ROLE_MIN}")
    guides = [L["name"] for L in layers if not L["visible"] and GUIDE_RE.search(L["name"])]
    visible_guides = [L["name"] for L in layers if L["visible"] and GUIDE_RE.search(L["name"])]
    add("hidden_guides", bool(guides) and not visible_guides,
        f"hidden={guides} visible_guides={visible_guides}")

    # Same-output-root negative control: copy manifest once, flip only the PNG hash.
    ctl = out / "control"
    ctl.mkdir(exist_ok=True)
    clean = ctl / "rpg-2-star-ocean-the-second_jiang-lan_clean-hash-control_test-only-v01_20261021-235007-514b9771.json"
    shutil.copy2(mpath, clean)
    bad_obj = json.loads(clean.read_text(encoding="utf-8-sig"))
    bad_path = ctl / "rpg-2-star-ocean-the-second_jiang-lan_bad-hash-control_test-only-v01_20261021-235007-514b9771.json"
    # flip the declared PNG hash only (walk to a png ref)
    def flip_png(x):
        if isinstance(x, dict):
            p = x.get("path") or x.get("file") or x.get("src")
            if isinstance(p, str) and p.lower().endswith(".png") and "portrait" not in p.lower():
                for hk in ("rawsha256", "sha256", "hash"):
                    if isinstance(x.get(hk), str):
                        x[hk] = "0" * 64
                        return True
            for v in x.values():
                if flip_png(v):
                    return True
        elif isinstance(x, list):
            for v in x:
                if flip_png(v):
                    return True
        return False
    flipped = flip_png(bad_obj)
    bad_path.write_text(json.dumps(bad_obj, ensure_ascii=False, indent=2), encoding="utf-8")
    # Evaluate control through the same declared-hash resolution used above.
    def hash_gate(path: Path):
        obj = json.loads(path.read_text(encoding="utf-8-sig"))
        r = primary_ref(obj, ".png", src, root)
        return bool(r and r[1] == actual)
    clean_ok, bad_ok = hash_gate(clean), hash_gate(bad_path)
    add("negative_control_bad_png_hash", flipped and (not bad_ok) and clean_ok,
        f"clean_accepted={clean_ok} bad_hash_accepted={bad_ok} flipped={flipped}")

    pxos = sorted(src.glob("*.pxo"))
    report["pxo"] = {"status": "pending", "files": [p.name for p in pxos],
                     "reason": "Native PXO roundtrip/export not implemented; separate export root reserved. GUI-clean not inferred.",
                     "export_root": str(out / "pxo-roundtrip")}
    report["gui_clean"] = "not_verified"

    ok = all(c["ok"] for c in checks)
    report["status"] = "pass" if ok else "failed"
    report["check_count"] = len(checks)
    (out / "rpg-2-star-ocean-the-second_jiang-lan_static-source-check_v01_20261021-235007-514b9771.json").write_text(
        json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps({"status": report["status"], "checks": len(checks),
                      "failed": [c["id"] for c in checks if not c["ok"]]}))
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
