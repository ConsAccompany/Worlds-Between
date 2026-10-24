#!/usr/bin/env python3
"""Independent Muxiu mdisplay91 display-image contract check (structure adapted from the Lin Que display64 checker).

Usage: python <this> --root R --manifest M --out O
Exit 0 pass, 1 failure, 2 producer artifact pending. One JSON report under O.
Read-only for source/producer files; no motion/default/art-approval claims.
The display image must be an exact integer 2x pixel replication of the committed native south static.
"""
import argparse
import copy
import hashlib
import io
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

from PIL import Image

P = "rpg-2-star-ocean-the-second"
T = "20261024-083014-7c4a91d2"
A = "muxiu"
SS = "e14d5c50890d7fcd0c75eb362d2b08fd1d4ac02c9c33e04fc4861b5a7d7a26fe"
SRGBA = "02cbb1d00a22eb4268bc40eddbfb5179b106f703645150c8f096bd06f50b5faa"
SM = "game/assets/characters/muxiu-native-v01/south/rpg-2-star-ocean-the-second_muxiu_south-manifest_unapproved-v01_20261024-071500-dd478113.json"
SMSHA = "24c751575fe02a4857628dbfb8b379cd1d42344167062ae8ddbb033024e114de"
SD = (80, 112)
FACTOR = 2
OD = (160, 224)
DEF = "game/assets/characters/muxiu-native-v01/south/rpg-2-star-ocean-the-second_muxiu_south-static_unapproved-v01_20261024-071500-ca23fad5.png"
REP = f"{P}_{A}_display-contract-report_v01_{T}.json"
SCOPE = ("independent exact integer-replication/manifest contract only; no motion, default-use, "
         "runtime, or art-approval claims; source and producer files are read-only")


def sh(b):
    return hashlib.sha256(b).hexdigest()


def g(c, n, o, d=""):
    c.append({"id": n, "ok": bool(o), "detail": d})


def ins(r, p):
    try:
        p.resolve().relative_to(r.resolve())
        return True
    except ValueError:
        return False


def pick(r, b, v, pr=False):
    """Resolve one explicit metadata path; no recursive/glob lookup."""
    if not v:
        return None
    q = Path(str(v).replace("\\", "/"))
    for f in ([r, b] if pr else [b, r]):
        x = (q if q.is_absolute() else f / q).resolve()
        if ins(r, x) and x.is_file():
            return x
    return None


def wr(o, r):
    o.mkdir(parents=True, exist_ok=True)
    p = o / REP
    with open(p, "w", encoding="utf-8", newline="\n") as f:
        f.write(json.dumps(r, indent=2, ensure_ascii=False) + "\n")
    return p


def replicate_ok(src, out):
    if src.size[0] * FACTOR != out.size[0] or src.size[1] * FACTOR != out.size[1]:
        return False, "size"
    s, o = src.load(), out.load()
    for y in range(src.height):
        for x in range(src.width):
            want = s[x, y]
            for dy in range(FACTOR):
                for dx in range(FACTOR):
                    if o[x * FACTOR + dx, y * FACTOR + dy] != want:
                        return False, f"pixel {x},{y}+{dx},{dy}"
    return True, f"{out.size[0] * out.size[1]} pixels"


def val(m, obyt, sbyt, smbyt):
    c = []
    try:
        s = Image.open(io.BytesIO(sbyt)).convert("RGBA")
    except Exception as e:
        return {"ok": False, "checks": [{"id": "source.decode", "ok": False, "detail": repr(e)}]}
    g(c, "subject.muxiu", m.get("subject") == A, str(m.get("subject")))
    g(c, "content_id", m.get("content_id") == "content.char.muxiu.display", str(m.get("content_id")))
    g(c, "status.unapproved", str(m.get("status", "")).startswith("UNAPPROVED"), str(m.get("status")))
    src = m.get("source") if isinstance(m.get("source"), dict) else {}
    g(c, "source.path", src.get("path") == DEF, str(src.get("path")))
    g(c, "source.sha", src.get("sha256") == SS, str(src.get("sha256")))
    g(c, "source.size", (src.get("width"), src.get("height")) == SD, str((src.get("width"), src.get("height"))))
    g(c, "source.mode-rgba", src.get("mode") == "RGBA", str(src.get("mode")))
    g(c, "source.raw-rgba", src.get("raw_rgba_sha256") == SRGBA, str(src.get("raw_rgba_sha256")))
    g(c, "source.actual-sha", sh(sbyt) == SS, sh(sbyt))
    g(c, "source.actual-size", s.size == SD, str(s.size))
    g(c, "source.actual-rgba", sh(s.tobytes()) == SRGBA, sh(s.tobytes()))
    sm = m.get("source_manifest") if isinstance(m.get("source_manifest"), dict) else {}
    g(c, "source-manifest.path", sm.get("path") == SM, str(sm.get("path")))
    g(c, "source-manifest.sha", sm.get("sha256") == SMSHA and sh(smbyt) == SMSHA, sh(smbyt))
    try:
        smj = json.loads(smbyt)
    except Exception as e:
        smj = None
        g(c, "source-manifest.parse", False, repr(e))
    if smj is not None:
        g(c, "source-manifest.actor", smj.get("actor_id") == A, str(smj.get("actor_id")))
        g(c, "source-manifest.content", smj.get("content_id") == "content.char.muxiu.static-south", str(smj.get("content_id")))
        g(c, "source-manifest.canvas", smj.get("canvas") == list(SD), str(smj.get("canvas")))
        g(c, "source-manifest.pivot", smj.get("pivot") == [40, 104], str(smj.get("pivot")))
        g(c, "source-manifest.scale", smj.get("display_scale") == 0.5, str(smj.get("display_scale")))
    tr = m.get("transform") if isinstance(m.get("transform"), dict) else {}
    g(c, "transform.method", tr.get("method") == "nearest-neighbor-integer-upscale", str(tr.get("method")))
    g(c, "transform.factor", tr.get("factor") == FACTOR, str(tr.get("factor")))
    g(c, "transform.rect", tr.get("source_rect") == [0, 0, SD[0], SD[1]], str(tr.get("source_rect")))
    g(c, "transform.resampled", tr.get("resampled") is True, str(tr.get("resampled")))
    g(c, "transform.replication", tr.get("pixel_replication_only") is True, str(tr.get("pixel_replication_only")))
    g(c, "transform.not-repainted", tr.get("repainted") is False, str(tr.get("repainted")))
    g(c, "transform.no-new-generative", tr.get("ai_generated_new_pixels") is False, str(tr.get("ai_generated_new_pixels")))
    g(c, "transform.no-new-colours", tr.get("new_colour_values") is False, str(tr.get("new_colour_values")))
    g(c, "transform.alpha-preserved", tr.get("alpha_preserved") is True, str(tr.get("alpha_preserved")))
    out = m.get("output") if isinstance(m.get("output"), dict) else {}
    g(c, "output.size-declared", (out.get("width"), out.get("height")) == OD, str((out.get("width"), out.get("height"))))
    g(c, "output.file-sha-declared", out.get("file_sha256") == sh(obyt), str(out.get("file_sha256")))
    try:
        i = Image.open(io.BytesIO(obyt)).convert("RGBA")
    except Exception as e:
        i = None
        g(c, "output.decode", False, repr(e))
    if i is not None:
        g(c, "output.actual-size", i.size == OD, str(i.size))
        g(c, "output.actual-raw-rgba", sh(i.tobytes()) == out.get("raw_rgba_sha256"), sh(i.tobytes()))
        g(c, "pixels.exact-integer-replication", *replicate_ok(s, i))
        opaque = sum(1 for p in i.getdata() if p[3] > 127)
        g(c, "output.opaque-pixels", opaque > 0, str(opaque))
        border = [i.getpixel((x, 0))[3] for x in range(i.width)] + [i.getpixel((x, i.height - 1))[3] for x in range(i.width)]
        border += [i.getpixel((0, y))[3] for y in range(i.height)] + [i.getpixel((i.width - 1, y))[3] for y in range(i.height)]
        g(c, "output.transparent-border", all(a == 0 for a in border), f"{len(border)} border texels")
    return {"ok": all(x["ok"] for x in c), "checks": c}


def wrong_actor(m):
    m["subject"] = "jiang-lan"


def wrong_hash(m):
    m["output"]["file_sha256"] = "0" * 64


def wrong_factor(m):
    m["transform"]["factor"] = 3


def fx(n, m, obyt, sbyt, smbyt, fn):
    x = copy.deepcopy(m)
    fn(x)
    try:
        q = val(x, obyt, sbyt, smbyt)
        return {"id": n, "refused": not q["ok"], "failedChecks": [z["id"] for z in q["checks"] if not z["ok"]][:8]}
    except Exception as e:
        return {"id": n, "refused": True, "failedChecks": [f"exception:{e!r}"]}


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--root", default=".")
    ap.add_argument("--manifest", required=True)
    ap.add_argument("--out", required=True)
    a = ap.parse_args(argv)
    root = Path(a.root).resolve()
    mp = Path(a.manifest)
    if not mp.is_absolute():
        mp = root / mp
    mp = mp.resolve()
    out = Path(a.out).resolve()
    rep = {"schema": "muxiu-display-contract-che