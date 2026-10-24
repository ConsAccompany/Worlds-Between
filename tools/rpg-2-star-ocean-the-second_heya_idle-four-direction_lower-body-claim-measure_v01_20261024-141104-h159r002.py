"""Measure the Heya i159 manifest lower-body claim against actual frame bytes.

Producer manifests claim `boots and lower-body rows 76..103 unchanged` while the authored/independent
checks only froze composite rows 90..103. This tool measures rows 76..89 and 90..103 separately and
reports the actual result without changing any source asset or weakening any contract. Writes only a new
JSON under outputs/heya-i159/repair2/qa/.
"""
import glob, hashlib, json, os
from datetime import datetime, timezone
import numpy as np
from PIL import Image

ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
ROOT_IDLE = os.path.join(ROOT, "game/assets/characters/heya-native-v01/idle")
DIRS = ("south", "west", "north", "east")
OUT = os.path.join(ROOT, "outputs/heya-i159/repair2/qa")


def sha(b):
    return hashlib.sha256(b).hexdigest()


def main():
    results = {}
    for d in DIRS:
        man = glob.glob(os.path.join(ROOT_IDLE, d, "*manifest*.json"))
        assert len(man) == 1, (d, man)
        m = json.loads(open(man[0], encoding="utf8").read())
        claim = m.get("idle_model", {}).get("planted_feet", "")
        frames, hashes = [], []
        for fr in m["directions"]["frames"]:
            p = os.path.join(ROOT_IDLE, d, fr["file"])
            b = open(p, "rb").read()
            hashes.append(sha(b))
            frames.append(np.array(Image.open(p).convert("RGBA")))
        static = frames[0]
        sp = m["directions"]["static_png"]
        sp_path = os.path.join(ROOT_IDLE, d, sp["file"])
        if not os.path.isfile(sp_path):
            sp_path = os.path.join(ROOT, "game/assets/characters/heya-native-v01", d, sp["file"])
        sp_bytes = open(sp_path, "rb").read()
        f00_matches_static = hashes[0] == sha(sp_bytes) == sp["sha256"]
        rows = {}
        for lo, hi in ((76, 90), (90, 104), (76, 104)):
            per_frame = []
            for i, a in enumerate(frames):
                changed = (np.where(np.any(a[lo:hi] != static[lo:hi], axis=(1, 2)))[0] + lo).tolist()
                per_frame.append(changed)
            rows[f"{lo}..{hi - 1}"] = {"changed_rows_per_frame": per_frame,
                                      "frozen_all_frames": all(not x for x in per_frame)}
        results[d] = {"manifest": os.path.relpath(man[0], ROOT), "manifest_sha256": sha(open(man[0], "rb").read()),
                      "planted_feet_claim": claim,
                      "claims_rows_76_103_frozen": "76..103" in claim,
                      "frame_sha256": hashes,
                      "f00_equals_static": f00_matches_static,
                      "row_measurements": rows}
    actual_76_89 = all(r["row_measurements"]["76..89"]["frozen_all_frames"] for r in results.values())
    actual_90_103 = all(r["row_measurements"]["90..103"]["frozen_all_frames"] for r in results.values())
    claim_76_103 = all(r["claims_rows_76_103_frozen"] for r in results.values())
    report = {"task": "content.char.heya.idle-anim lower-body row claim measurement",
              "generated_utc": datetime.now(timezone.utc).isoformat(),
              "directions": results,
              "producer_claim_rows_76_103_frozen": claim_76_103,
              "actual_rows_76_89_frozen_all_directions": actual_76_89,
              "actual_rows_90_103_frozen_all_directions": actual_90_103,
              "claim_76_103_is_false": bool(claim_76_103 and not actual_76_89),
              "sole_rows_90_103_still_frozen": actual_90_103,
              "source_assets_modified": False,
              "contract_weakened": False,
              "note": "Rows 76..89 are measured directly from installed frame PNG bytes against frame f00; "
                      "no source asset or manifest text was changed."}
    os.makedirs(OUT, exist_ok=True)
    rid = datetime.now(timezone.utc).strftime("%Y%m%d-%H%M%S")
    path = os.path.join(OUT, f"rpg-2-star-ocean-the-second_heya_idle_lower-body-claim-measure_v01_{rid}.json")
    with open(path, "x") as f:
        f.write(json.dumps(report, indent=2) + "\n")
    print(json.dumps({"report": os.path.relpath(path, ROOT),
                      "claim_76_103": claim_76_103, "actual_76_89_frozen": actual_76_89,
                      "actual_90_103_frozen": actual_90_103,
                      "claim_76_103_is_false": report["claim_76_103_is_false"]}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
