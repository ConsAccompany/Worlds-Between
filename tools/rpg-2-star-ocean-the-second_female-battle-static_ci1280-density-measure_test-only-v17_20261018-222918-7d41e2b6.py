"""TEST-ONLY v17 capture measurement (reads captures, writes one report JSON and separate inspection crops).

Proves from the actual Godot viewport images (not from the source PNG alone):
  * render mode: 1280x720 backing, logical 640x360, canvas_items factor 2 (harness report) AND, pixel-level, the 136x144
    texture appears texel-for-texel (sub-logical 2x2 detail survives); a 640-then-upscale path would make every
    logical 2x2 block uniform, which is what the v16 control shows
  * same apparent bounds: physical bbox of the hero texture v16 vs v17 in the same 1280 context
  * unchanged context: outside the hero union rect the v16 and v17 frames are identical; UI control rects identical;
    normal party x positions and the 0.1 s move probe recorded by the harness
  * 640 compatibility: which native texel phase nearest sampling keeps, and how much face detail is lost there
Run: python -I -B <this> <outputs/battle-static-v17 dir> <author tool path>
"""
import hashlib, importlib.util, json, os, sys
import numpy as np
from PIL import Image

RUNS = {"k1280-def-v16": ("ci1280", "default", "v16"), "k1280-def-v17": ("ci1280", "default", "v17"),
        "k1280-osk-v16": ("ci1280", "outskirts", "v16"), "k1280-osk-v17": ("ci1280", "outskirts", "v17"),
        "n640-def-v17": ("native640", "default", "v17")}
FACE_BOX = (72, 22, 95, 44)        # native texels (x0, y0, x1, y1 exclusive)
TOOL = os.path.basename(os.path.abspath(__file__))


def sha_file(p):
    return hashlib.sha256(open(p, "rb").read()).hexdigest()


def load(p):
    return np.array(Image.open(p).convert("RGBA"))


def nonuniform_blocks(img, mask):
    """count logical 2x2 blocks (aligned to even physical coords) fully inside mask with > 1 distinct colour."""
    h, w = mask.shape
    h2, w2 = h // 2, w // 2
    m = mask[:h2 * 2, :w2 * 2].reshape(h2, 2, w2, 2).all(axis=(1, 3))
    px = img[:h2 * 2, :w2 * 2, :3].reshape(h2, 2, w2, 2, 3).transpose(0, 2, 1, 3, 4).reshape(h2, w2, 4, 3)
    diff = (px != px[:, :, :1, :]).any(axis=(2, 3))
    return int(m.sum()), int((m & diff).sum())


def main():
    out, author = sys.argv[1], sys.argv[2]
    spec = importlib.util.spec_from_file_location("author", author)
    a = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(a)
    v17 = load(os.path.join(out, a.NAMES["png"]))
    v16 = load(os.path.join(os.path.dirname(out), "battle-static-v16", os.path.basename(a.V16_PNG_REL)))
    gates, runs = [], {}

    def gate(name, ok, detail=None):
        gates.append({"gate": name, "pass": bool(ok), "detail": detail})

    for name, (mode, plate, ver) in RUNS.items():
        d = os.path.join(out, name)
        rep_name = [f for f in os.listdir(d) if f.endswith(".json")][0]
        rep = json.load(open(os.path.join(d, rep_name), encoding="utf-8"))
        sprite = v17 if ver == "v17" else v16
        factor = rep["stretchFactor"]
        gate(f"{name}: harness report mode/backing/logical/factor", rep["mode"] == mode and rep["plate"] == plate
             and rep["backing"] == ([1280, 720] if mode == "ci1280" else [640, 360]) and rep["logicalVisible"] == [640, 360]
             and factor == (2 if mode == "ci1280" else 1) and rep["contentScaleMode"] == "canvas_items",
             {k: rep[k] for k in ("mode", "plate", "backing", "logicalVisible", "stretchFactor")})
        gate(f"{name}: arena source is canonical 404eabfd and sprite hash bound", rep["arenaSha256"].startswith("404eabfd")
             and rep["spriteSha256"] == hashlib.sha256(open(os.path.join(out, a.NAMES["png"]) if ver == "v17" else
             os.path.join(os.path.dirname(out), a.V16_PNG_REL.split("outputs/")[1]), "rb").read()).hexdigest(),
             {"arena": rep["arenaSha256"][:16], "sprite": rep["spriteSha256"][:16]})
        recs = {}
        for r in rep["records"]:
            lang = r["language"]
            inj_p = os.path.join(d, r["injected"])
            base_p = os.path.join(d, r["baseline"])
            gate(f"{name}/{lang}: capture file hashes match the harness report",
                 sha_file(inj_p) == r["injectedFileSha256"] and sha_file(base_p) == r["baselineFileSha256"])
            img = load(inj_p)
            gate(f"{name}/{lang}: actual viewport image size", img.shape[1::-1] == tuple(rep["backing"]),
                 list(img.shape[1::-1]))
            gate(f"{name}/{lang}: 0 changed pixels outside the hero bounds, party x normal, move probe 16.8 px",
                 r["changedOutsideHeroBounds"] == 0 and r["partyX"] == [135.0, 171.0, 207.0, 243.0]
                 and abs(r["moveProbe"]["afterX"] - r["moveProbe"]["initialX"] - 16.8) < 0.01,
                 {"changed": r["changedPixels"], "outside": r["changedOutsideHeroBounds"], "move": r["moveProbe"]})
            px0, py0, pw, ph = r["candidatePhysicalRect"]
            crop = img[py0:py0 + ph, px0:px0 + pw]
            sh, sw = sprite.shape[:2]
            # Occlusion: the next party member (and its selection ring) is drawn AFTER the hero in the normal layout.
            # A candidate-opaque pixel that differs from the candidate but is identical in the main-hero frame (whose
            # hero art differs) was overdrawn by a later draw call; it is excluded and counted, never hidden.
            base_crop = load(base_p)[py0:py0 + ph, px0:px0 + pw]
            phase_hist = None
            if mode == "ci1280":
                exp = sprite if sw == pw else np.repeat(np.repeat(sprite, 2, axis=0), 2, axis=1)
                op = exp[..., 3] == 255
                hit = op & (crop[..., :3] == exp[..., :3]).all(axis=2)
            else:
                # nearest sampling of 136 texels into 68 pixels: each pixel must show ONE of its 4 native texels
                cells = [sprite[oy::2, ox::2][:ph, :pw] for oy in (0, 1) for ox in (0, 1)]
                op = np.all([c[..., 3] == 255 for c in cells], axis=0)        # pixels whose whole 2x2 cell is opaque
                eq = [(crop[..., :3] == c[..., :3]).all(axis=2) for c in cells]
                hit = op & np.any(eq, axis=0)
                only = [op & e & ~np.any([f for j, f in enumerate(eq) if j != i], axis=0) for i, e in enumerate(eq)]
                phase_hist = {f"{ox}{oy}": int(only[i].sum()) for i, (oy, ox) in enumerate([(0, 0), (0, 1), (1, 0), (1, 1)])}
                exp = cells[0]
            occluded = op & ~hit & (crop == base_crop).all(axis=2)
            vis = op & ~occluded
            n_op, n_vis, match = int(op.sum()), int(vis.sum()), int(hit.sum())
            full, non = nonuniform_blocks(crop, vis)
            rec = {"physicalRect": [px0, py0, pw, ph], "opaqueSpritePixels": n_op, "occludedByLaterDraws": int(occluded.sum()),
                   "visibleSpritePixels": n_vis, "exactMatches": match, "fidelityVisible": round(match / max(n_vis, 1), 6),
                   "uniquelyIdentifiedSamplePhase(ox,oy)": phase_hist,
                   "fullyOpaqueLogical2x2": full, "nonUniformLogical2x2": non,
                   "distinctColoursInHero": len({tuple(c) for c in crop[vis][:, :3].tolist()})}
            if occluded.any():
                oy_, ox_ = np.nonzero(occluded)
                rec["occludedPhysicalXRange"] = [px0 + int(ox_.min()), px0 + int(ox_.max())]
            op = vis
            ys, xs = np.nonzero(op)
            rec["heroPhysicalBBox"] = [px0 + int(xs.min()), py0 + int(ys.min()), px0 + int(xs.max()), py0 + int(ys.max())]
            if mode == "ci1280":
                fx0, fy0, fx1, fy1 = FACE_BOX
                fcrop, fop = crop[fy0:fy1, fx0:fx1], op[fy0:fy1, fx0:fx1]
                f_full, f_non = nonuniform_blocks(fcrop, fop)
                rec["face"] = {"physicalBox": [px0 + fx0, py0 + fy0, fx1 - fx0, fy1 - fy0], "opaque": int(fop.sum()),
                               "distinctColours": len({tuple(c) for c in fcrop[fop][:, :3].tolist()}),
                               "fullyOpaqueLogical2x2": f_full, "nonUniformLogical2x2": f_non}
                # separate inspection crop of the actual capture (x3 nearest), one subject per file
                c = Image.fromarray(np.ascontiguousarray(img[py0 - 8:py0 + ph + 8, px0 - 8:px0 + pw + 8]), "RGBA")
                cname = f"rpg-2-star-ocean-the-second_v17-inspect-capture-hero-x3_{name}-{lang}_test-only_20261018-222918-7d41e2b6.png"
                c.resize((c.width * 3, c.height * 3), Image.NEAREST).save(os.path.join(out, "inspect", cname))
                rec["inspectionCrop"] = "inspect/" + cname
            else:
                fx0, fy0, fx1, fy1 = (v // 2 for v in FACE_BOX)
                fcrop, fop = crop[fy0:fy1, fx0:fx1], op[fy0:fy1, fx0:fx1]
                src = v17[FACE_BOX[1]:FACE_BOX[3], FACE_BOX[0]:FACE_BOX[2]]
                sop = src[..., 3] == 255
                rec["face640"] = {"logicalBox": [fx0, fy0, fx1 - fx0, fy1 - fy0], "shownPixels": int(fop.sum()),
                                  "nativeFaceTexels": int(sop.sum()),
                                  "shownDistinctColours": len({tuple(c) for c in fcrop[fop][:, :3].tolist()}),
                                  "nativeDistinctColours": len({tuple(c) for c in src[sop][:, :3].tolist()})}
                c = Image.fromarray(np.ascontiguousarray(img[py0 - 4:py0 + ph + 4, px0 - 4:px0 + pw + 4]), "RGBA")
                cname = f"rpg-2-star-ocean-the-second_v17-inspect-capture-hero-x6_{name}-{lang}_test-only_20261018-222918-7d41e2b6.png"
                c.resize((c.width * 6, c.height * 6), Image.NEAREST).save(os.path.join(out, "inspect", cname))
                rec["inspectionCrop"] = "inspect/" + cname
            gate(f"{name}/{lang}: every visible hero pixel is an exact native texel (no filtering / blending; "
                 f"{'texel-for-texel' if mode == 'ci1280' else 'one of its 4 native texels'})",
                 match == n_vis, {"matches": match, "visible": n_vis, "occluded": int(occluded.sum())})
            rec["controlsLogical"] = r["controlsLogical"]
            rec["img"] = img
            rec["union"] = r["heroLogicalUnionRect"]
            recs[lang] = rec
        runs[name] = {"report": rep_name, "mode": mode, "plate": plate, "sprite": ver, "records": recs}

    summary = {}
    for plate in ("default", "outskirts"):
        k16, k17 = f"k1280-{'def' if plate == 'default' else 'osk'}-v16", f"k1280-{'def' if plate == 'default' else 'osk'}-v17"
        for lang in ("en", "zh"):
            r16, r17 = runs[k16]["records"][lang], runs[k17]["records"][lang]
            ux, uy, uw, uh = r17["union"]
            mask = np.ones(r17["img"].shape[:2], bool)
            mask[uy * 2:(uy + uh) * 2, ux * 2:(ux + uw) * 2] = False
            same_ctx = bool((r16["img"][mask] == r17["img"][mask]).all())
            gate(f"1280 {plate}/{lang}: v16 and v17 frames identical outside the hero union (same context)", same_ctx)
            gate(f"1280 {plate}/{lang}: UI control rects identical v16 vs v17",
                 r16["controlsLogical"] == r17["controlsLogical"], len(r17["controlsLogical"]))
            b16, b17 = r16["heroPhysicalBBox"], r17["heroPhysicalBBox"]
            dl = [b17[i] - b16[i] for i in range(4)]
            gate(f"1280 {plate}/{lang}: same apparent figure bounds (each edge within 4 physical px = 2 logical)",
                 all(abs(v) <= 4 for v in dl), {"v16": b16, "v17": b17, "delta": dl})
            gate(f"1280 {plate}/{lang}: v16 control has NO sub-logical detail (every opaque logical 2x2 block uniform)",
                 r16["nonUniformLogical2x2"] == 0, r16["nonUniformLogical2x2"])
            gate(f"1280 {plate}/{lang}: v17 sub-logical detail survives the real render (>= 25% of opaque blocks)",
                 r17["nonUniformLogical2x2"] >= 0.25 * r17["fullyOpaqueLogical2x2"],
                 {"nonUniform": r17["nonUniformLogical2x2"], "blocks": r17["fullyOpaqueLogical2x2"]})
            summary[f"{plate}-{lang}"] = {
                "v16": {k: r16[k] for k in ("heroPhysicalBBox", "distinctColoursInHero", "fullyOpaqueLogical2x2",
                                            "nonUniformLogical2x2", "face", "fidelityVisible", "occludedByLaterDraws")},
                "v17": {k: r17[k] for k in ("heroPhysicalBBox", "distinctColoursInHero", "fullyOpaqueLogical2x2",
                                            "nonUniformLogical2x2", "face", "fidelityVisible", "occludedByLaterDraws")}}
    for lang in ("en", "zh"):
        c1280 = runs["k1280-def-v17"]["records"][lang]["controlsLogical"]
        c640 = runs["n640-def-v17"]["records"][lang]["controlsLogical"]
        gate(f"controls/{lang}: logical UI control rects identical at 1280 canvas_items and native 640", c1280 == c640,
             len(c640))
        r6 = runs["n640-def-v17"]["records"][lang]
        summary[f"native640-{lang}"] = {k: r6[k] for k in ("heroPhysicalBBox", "distinctColoursInHero",
                                                          "uniquelyIdentifiedSamplePhase(ox,oy)", "fidelityVisible",
                                                          "face640", "visibleSpritePixels", "occludedByLaterDraws")}
        summary[f"native640-{lang}"]["nativeOpaqueTexels"] = int((v17[..., 3] == 255).sum())
    ok = all(g["pass"] for g in gates)
    for rn in runs.values():
        for rec in rn["records"].values():
            rec.pop("img"); rec.pop("controlsLogical")
    report = {"status": "TEST-ONLY v17 density capture measurement; not art approval", "pass": ok,
              "passed": sum(g["pass"] for g in gates), "total": len(gates), "gates": gates, "summary": summary,
              "runs": runs, "tool": "tools/" + TOOL,
              "faceBoxNative": list(FACE_BOX)}
    path = os.path.join(out, "rpg-2-star-ocean-the-second_v17-capture-measure-report-r2_test-only_20261018-222918-7d41e2b6.json")
    with open(path, "x", encoding="utf-8", newline="\n") as f:
        f.write(json.dumps(report, indent=1, ensure_ascii=False) + "\n")
    print("MEASURE", "PASS" if ok else "FAIL", f"{report['passed']}/{report['total']}", path)
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()
