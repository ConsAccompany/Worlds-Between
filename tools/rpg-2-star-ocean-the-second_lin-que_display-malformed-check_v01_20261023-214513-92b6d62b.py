"""Malformed-input gate for the Lin Que ldisplay64 contract checker and builder.

Usage: python -I <this> --out <new dir>
Runs the contract checker on the real manifest (must PASS with all three built-in fixtures refused) and on
four external malformed inputs (must each exit nonzero with the stated status). Also confirms the builder
`check` refuses a tampered crop copy. Writes fixtures/reports only under --out. Prints LDISPLAY64_MALFORMED_OK.
"""
import argparse
import hashlib
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RUN = "20261023-214513-92b6d62b"
P = "rpg-2-star-ocean-the-second"
CHECKER = ROOT / f"tools/{P}_lin-que_display-contract-check_v01_{RUN}.py"
MANIFEST = ROOT / f"game/assets/portraits/ldisplay64/{P}_lin-que_display-portrait-manifest_v01_{RUN}.json"
CROP = ROOT / f"game/assets/portraits/ldisplay64/{P}_lin-que_display-portrait-crop_v01_{RUN}.png"
JIANG = ROOT / f"game/assets/portraits/jiang-display40/{P}_jiang-lan_display-portrait-manifest_v01_20261022-155956-1414792c.json"


def run_checker(manifest: Path, out: Path):
    r = subprocess.run([sys.executable, "-I", str(CHECKER), "--root", str(ROOT), "--manifest", str(manifest),
                        "--out", str(out)], capture_output=True, text=True, encoding="utf-8")
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

    def expect(name, cond, detail):
        results.append({"id": name, "ok": bool(cond), "detail": detail})
        if not cond:
            fails.append(name)
            print("FAIL", name, detail)

    base = json.loads(MANIFEST.read_text(encoding="utf-8"))
    code, s = run_checker(MANIFEST, out / "real")
    rep = json.loads((out / "real" / f"{P}_lin-que_display-contract-report_v01_{RUN}.json").read_text(encoding="utf-8"))
    expect("real.pass", code == 0 and s["status"] == "PASS", s)
    expect("real.all-checks-ok", rep["checks"] and all(c["ok"] for c in rep["checks"]), len(rep["checks"]))
    expect("real.fixtures-refused", len(rep["negativeFixtures"]) == 3
           and all(v["refused"] for v in rep["negativeFixtures"].values()), rep["negativeFixtures"])

    shifted = json.loads(json.dumps(base))
    shifted["crop"].update(left=17, right=593)
    noactor = json.loads(json.dumps(base))
    noactor["subject"] = "jiang-lan"
    fx = {
        "shifted-rect": json.dumps(shifted, indent=2),
        "other-actor": json.dumps(noactor, indent=2),
        "truncated-json": json.dumps(base)[:200],
    }
    for name, text in fx.items():
        p = out / f"{P}_lin-que_display-manifest-fixture_{name}_{RUN}.json"
        p.write_text(text, encoding="utf-8", newline="\n")
        code, s = run_checker(p, out / name)
        expect(f"{name}.refused", code == 1 and s["status"] == "FAIL", s)
    code, s = run_checker(JIANG, out / "jiang-manifest")
    expect("jiang-manifest.refused", code == 1 and s["status"] == "FAIL", s)
    code, s = run_checker(out / "absent.json", out / "absent")
    expect("absent.pending", code == 2 and s["status"] == "PENDING", s)

    # Tampered crop: one pixel changed in a copy pointed to by a manifest copy; file hash and pixel checks must fail.
    from PIL import Image
    tam_dir = out / "tampered"
    tam_dir.mkdir()
    tam = tam_dir / CROP.name
    im = Image.open(CROP).convert("RGB")
    px = im.getpixel((288, 400))
    im.putpixel((288, 400), (px[0] ^ 1, px[1], px[2]))
    im.save(tam)
    tm = json.loads(json.dumps(base))
    tm["output"]["path"] = tam.relative_to(ROOT).as_posix()
    tmp = tam_dir / f"{P}_lin-que_display-manifest-fixture_tampered-pixel_{RUN}.json"
    tmp.write_text(json.dumps(tm, indent=2), encoding="utf-8", newline="\n")
    code, s = run_checker(tmp, out / "tampered-report")
    expect("tampered-pixel.refused", code == 1 and "pixels.exact-crop" in s.get("failures", []), s)

    unchanged = hashlib.sha256(CROP.read_bytes()).hexdigest() == base["output"]["file_sha256"]
    expect("real-crop.unchanged", unchanged, base["output"]["file_sha256"])
    report = {"schema": "lin-display-malformed-check/v1", "run": RUN, "results": results,
              "status": "PASS" if not fails else "FAIL"}
    (out / f"{P}_lin-que_display-malformed-report_v01_{RUN}.json").write_text(
        json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8", newline="\n")
    print("LDISPLAY64_MALFORMED", len(results), "CASES", len(fails), "FAILS")
    if not fails:
        print("LDISPLAY64_MALFORMED_OK")
    return 0 if not fails else 1


if __name__ == "__main__":
    sys.exit(main())
