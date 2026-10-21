"""Independent inspection of the existing exploration source-bank manifest format.

Composes raw Pixelorama cels and OpenRaster layers without the author module.
This verifies editable source/export equality and geometry, not animation/art approval.
"""
import argparse
from datetime import datetime, timezone
import hashlib
import io
import json
import os
from pathlib import Path
import sys
import uuid
import xml.etree.ElementTree as ET
import zipfile
import numpy as np
from PIL import Image

ROOT = Path(__file__).resolve().parent.parent


def lp(path):
    path = Path(path).resolve()
    return Path("\\\\?\\" + str(path)) if os.name == "nt" else path


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("manifest")
    parser.add_argument("--out-dir", required=True)
    args = parser.parse_args()
    manifest = ROOT / args.manifest
    raw = lp(manifest).read_bytes()
    data = json.loads(raw)
    checks = []

    def ck(value, label):
        checks.append({"check": label, "passed": bool(value)})

    def png(entry):
        b = lp(ROOT / entry["file"]).read_bytes()
        ck(hashlib.sha256(b).hexdigest() == entry["sha256"], "file hash " + entry["file"])
        return Image.open(io.BytesIO(b)).convert("RGBA")

    ck(set(data["directions"]) == {"south", "west", "north", "east"}, "exactly four directions")
    for direction, bank in data["directions"].items():
        order = [bank["static"], *bank["idle"], *bank["walk"]]
        for phase in range(len(bank["walk"])):
            bridge = bank["stop_bridges"]["phase" + str(phase)]
            ck(len(bridge) == 4 and bridge[0] == {"ref": "walk", "index": phase, "k": 0.0}
               and bridge[-1] == {"ref": "idle", "index": 0, "k": 1.0}, "stop endpoints " + direction + "/" + str(phase))
            order.extend(bridge[1:3])
        images = [png(entry) for entry in order]
        for i, image in enumerate(images):
            a = np.asarray(image)
            alpha = a[:, :, 3]
            bb = image.getbbox()
            ck(image.size == (80, 112) and set(np.unique(alpha)) <= {0, 255}, "native binary-alpha cell " + direction + "/" + str(i))
            ck(bb is not None and bb[0] > 0 and bb[1] > 0 and bb[2] < 80 and bb[3] <= 104
               and bb[3] - bb[1] <= 97, "body/border/floor bounds " + direction + "/" + str(i))
            if i <= len(bank["idle"]):
                ck(bb is not None and bb[3] == 104 and 95 <= bb[3] - bb[1] <= 97, "neutral/idle ground pin " + direction + "/" + str(i))
        native = bank["pxo"]
        nb = lp(ROOT / native["file"]).read_bytes()
        ck(hashlib.sha256(nb).hexdigest() == native["sha256"], "PXO hash " + direction)
        with zipfile.ZipFile(io.BytesIO(nb)) as z:
            d = json.loads(z.read("data.json"))
            ck((d["size_x"], d["size_y"]) == (80, 112) and len(d["frames"]) == len(order), "PXO dimensions/frame count " + direction)
            ck(len(d["layers"]) > 1 and all(x["blend_mode"] == 0 for x in d["layers"]), "editable normal-blend role layers " + direction)
            for i, expected in enumerate(images):
                flat = Image.new("RGBA", (80, 112))
                for j, layer in enumerate(d["layers"]):
                    if not layer.get("visible", True):
                        continue
                    ck(layer.get("opacity", 1.0) == 1.0 and d["frames"][i]["cels"][j].get("opacity", 1.0) == 1.0, "native opacity " + direction + "/" + str(i) + "/" + str(j))
                    cel = Image.frombytes("RGBA", (80, 112), z.read(f"image_data/frames/{i + 1}/layer_{j + 1}"))
                    flat.alpha_composite(cel)
                ck(np.array_equal(np.asarray(flat), np.asarray(expected)), "raw PXO composite exact " + direction + "/" + str(i))
        native = bank["ora"]
        nb = lp(ROOT / native["file"]).read_bytes()
        ck(hashlib.sha256(nb).hexdigest() == native["sha256"], "ORA hash " + direction)
        with zipfile.ZipFile(io.BytesIO(nb)) as z:
            xml = ET.fromstring(z.read("stack.xml"))
            flat = Image.new("RGBA", (80, 112))
            for layer in reversed(xml.find("stack").findall("layer")):
                if layer.get("visibility", "visible") != "visible":
                    continue
                tile = Image.open(io.BytesIO(z.read(layer.attrib["src"]))).convert("RGBA")
                flat.alpha_composite(tile, (int(layer.get("x", "0")), int(layer.get("y", "0"))))
            ck(np.array_equal(np.asarray(flat), np.asarray(images[0])), "ORA layer composite exact " + direction)
            merged = Image.open(io.BytesIO(z.read("mergedimage.png"))).convert("RGBA")
            ck(np.array_equal(np.asarray(merged), np.asarray(images[0])), "ORA merged export exact " + direction)
    tag = datetime.now(timezone.utc).strftime("%Y%m%d-%H%M%S") + "-" + uuid.uuid4().hex[:8]
    out = ROOT / args.out_dir
    out.mkdir(parents=True, exist_ok=True)
    result = {"manifest": args.manifest, "manifestSha256Raw": hashlib.sha256(raw).hexdigest(),
              "checkerSha256Raw": hashlib.sha256(lp(__file__).read_bytes()).hexdigest(), "checks": checks,
              "passed": all(c["passed"] for c in checks), "artApproved": False, "humanPlaytest": False}
    path = out / ("rpg-2-star-ocean-the-second_exploration-source_native-bank-proof_test-only-v01_" + tag + ".json")
    lp(path).write_bytes((json.dumps(result, indent=2) + "\n").encode("utf8"))
    print("NATIVE_BANK", result["passed"], len(checks), path.relative_to(ROOT).as_posix())
    for check in checks:
        if not check["passed"]:
            print("FAIL", check["check"])
    return 0 if result["passed"] else 1


if __name__ == "__main__":
    sys.exit(main())
