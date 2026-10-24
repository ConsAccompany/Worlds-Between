"""Malformed-input gate for the Heya hdisplay179 contract checker and builder.

Usage: python -I <this> --out <new dir>
Runs the contract checker on the real manifest (must PASS with all three built-in fixtures refused) and on
external malformed inputs (each must be refused/PENDING as stated). Also confirms the checker refuses a
tampered display copy, a crop-shifted copy and a manifest with missing blocks. Writes only under --out.
"""
import argparse
import hashlib
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RUN = "20261024-154240-h179d001"
P = "rpg-2-star-ocean-the-second"
CHECKER = ROOT / f"tools/{P}_heya_display-contract-check_v01_{RUN}.py"
BUILDER = ROOT / f"tools/{P}_heya_display-build_v01_{RUN}.py"
MANIFEST = ROOT / f"game/assets/portraits/hdisplay179/{P}_heya_display-portrait-manifest_v01_{RUN}.json"
DISPLAY = ROOT / f"game/assets/portraits/hdisplay179/{P}_heya_display-portrait_v01_{RUN}.png"
YANKE = ROOT / "game/assets/portraits/ydisplay111/rpg-2-star-ocean-the-second_yanke_display-portrait-manifest_v01_20261024-100318-10cf38b5.json"
REPORT = f"{P}_heya_display-contract-report_v01_{RUN}.json"


def sha(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def run_checker(manifest: Path, out: Path):
    r = subprocess.run([sys.executable, "-I", str(CHECKER), "--root", str(ROOT), "--manifest", str(manifest),
                        "--out", str(out)], capture_output=True, text=True, encoding="utf-8", timeout=120)
    try:
        summary = json.loads(r.stdout.strip().splitlines()[-1])
    except (ValueError, IndexError):
        summary = {"status": "UNPARSEABLE", "stdout": r.stdout, "stderr": r.stderr}
    return r.returncode, summary


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    out = Path(ap.parse_args().out).resolve()
    if out.exists():
        raise SystemExit(f"REFUSE existing --out {out}")
    out.mkdir(parents=True)
    results, fails = [], []
    guarded = [DISPLAY, MANIFEST, CHECKER, BUILDER]
    before = {str(p.relative_to(ROOT)): sha(p) for p in guarded}

    def expect(name, cond, detail):
        results.append({"id": name, "ok": bool(cond), "detail": detail})
        if not cond:
            fails.append(name)
            print("FAIL", name, detail)

    base = json.loads(MANIFEST.read_text(encoding="utf-8"))
    code, s = run_checker(MANIFEST, out / "real")
    rep = json.loads((out / "real" / REPORT).read_text(encoding="utf-8"))
    expect("real.pass", code == 0 and s["status"] == "PASS", s)
    expect("real.all-checks-ok", rep["checks"] and all(c["ok"] for c in rep["checks"]), len(rep["checks"]))
    expect("real.fixtures-refused", len(rep["negativeFixtures"]) == 3
           and all(v["refused"] for v in rep["negativeFixtures"].values()), rep["negativeFixtures"])

    def mut(fn):
        m = json.loads(json.dumps(base))
        fn(m)
        return json.dumps(m, indent=2, ensure_ascii=False)

    fx = {
        "wrong-factor": (mut(lambda m: m["transform"].__setitem__("factor", 3)), "transform.factor"),
        "other-actor": (mut(lambda m: m.__setitem__("subject", "yanke")), "subject.heya"),
        "wrong-source-hash": (mut(lambda m: m["source"].__setitem__("sha256", "0" * 64)), "source.sha"),
        "wrong-source-commit": (mut(lambda m: m["source"].__setitem__("source_commit", "0" * 40)), "source.commit"),
        "shifted-source-rect": (mut(lambda m: m["transform"].__setitem__("source_rect", [1, 0, 81, 112])), "transform.rect"),
        "approved-status": (mut(lambda m: m.__setitem__("status", "APPROVED")), "status.unapproved"),
        "missing-blocks": (mut(lambda m: [m.pop(k) for k in ("transform", "source_manifest", "editable_sources")]), "transform.method"),
        "wrong-editable-pxo": (mut(lambda m: m["editable_sources"]["pxo"].__setitem__("sha256", "f" * 64)), "editable.pxo"),
        "wrong-editable-palette": (mut(lambda m: m["editable_sources"]["palette"].__setitem__("sha256", "0" * 64)), "editable.palette"),
        "root-is-list": ("[1, 2, 3]", "manifest.parse"),
        "truncated-json": (json.dumps(base)[:200], "manifest.parse"),
    }
    for name, (text, want) in fx.items():
        p = out / f"{P}_heya_display-manifest-fixture_{name}_{RUN}.json"
        p.write_text(text, encoding="utf-8", newline="\n")
        code, s = run_checker(p, out / name)
        expect(f"{name}.refused", code == 1 and s["status"] == "FAIL" and want in s.get("failures", []), s)
    code, s = run_checker(YANKE, out / "yanke-manifest")
    expect("yanke-manifest.refused", code == 1 and s["status"] == "FAIL", s)
    code, s = run_checker(out / "absent.json", out / "absent")
    expect("absent.pending", code == 2 and s["status"] == "PENDING", s)

    from PIL import Image
    src_img = Image.open(DISPLAY).convert("RGBA")
    # Tampered display: one opaque pixel changed in a copy pointed to by a manifest copy.
    tam_dir = out / "tampered"
    tam_dir.mkdir()
    tam = tam_dir / DISPLAY.name
    im = src_img.copy()
    xy = next((x, y) for y in range(im.height) for x in range(im.width) if im.getpixel((x, y))[3] == 255)
    px = im.getpixel(xy)
    im.putpixel(xy, (px[0] ^ 1, px[1], px[2], px[3]))
    im.save(tam)
    tm = json.loads(json.dumps(base))
    tm["output"]["path"] = tam.relative_to(ROOT).as_posix()
    tmp = tam_dir / f"{P}_heya_display-manifest-fixture_tampered-pixel_{RUN}.json"
    tmp.write_text(json.dumps(tm, indent=2), encoding="utf-8", newline="\n")
    code, s = run_checker(tmp, out / "tampered-report")
    expect("tampered-pixel.refused", code == 1 and "pixels.exact-integer-replication" in s.get("failures", []), s)
    # Crop-shift: display content moved by one output pixel (an odd shift breaks every 2x2 block).
    sh_dir = out / "shifted"
    sh_dir.mkdir()
    shf = sh_dir / DISPLAY.name
    moved = Image.new("RGBA", src_img.size)
    moved.paste(src_img.crop((1, 0, src_img.width, src_img.height)), (0, 0))
    moved.save(shf)
    sm = json.loads(json.dumps(base))
    sm["output"]["path"] = shf.relative_to(ROOT).as_posix()
    smp = sh_dir / f"{P}_heya_display-manifest-fixture_shifted-pixels_{RUN}.json"
    smp.write_text(json.dumps(sm, indent=2), encoding="utf-8", newline="\n")
    code, s = run_checker(smp, out / "shifted-report")
    expect("shifted-pixels.refused", code == 1 and "pixels.exact-integer-replication" in s.get("failures", []), s)
    # Report overwrite protection: a second run into the same --out must refuse rather than replace evidence.
    code, s = run_checker(MANIFEST, out / "real")
    expect("report-overwrite.refused", code != 0 and sha(out / "real" / REPORT) == hashlib.sha256(
        (json.dumps(rep, indent=2, ensure_ascii=False) + "\n").encode("utf-8")).hexdigest(), {"exit": code})
    # Builder check mode re-derives and verifies the installed bytes.
    r = subprocess.run([sys.executable, "-I", str(BUILDER), "check"], capture_output=True, text=True,
                       encoding="utf-8", timeout=120)
    expect("builder.check", r.returncode == 0 and "HDISPLAY179_BUILD OK" in r.stdout, r.stdout.strip())

    after = {str(p.relative_to(ROOT)): sha(p) for p in guarded}
    expect("guarded-files.unchanged", after == before and before[str(DISPLAY.relative_to(ROOT))] == base["output"]["file_sha256"], after)
    report = {"schema": "heya-display-malformed-check/v1", "run": RUN, "results": results,
              "guarded_sha256": after, "status": "PASS" if not fails else "FAIL"}
    (out / f"{P}_heya_display-malformed-report_v01_{RUN}.json").write_text(
        json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8", newline="\n")
    print("HDISPLAY179_MALFORMED", len(results), "CASES", len(fails), "FAILS")
    if not fails:
        print("HDISPLAY179_MALFORMED_OK")
    return 0 if not fails else 1


if __name__ == "__main__":
    sys.exit(main())
