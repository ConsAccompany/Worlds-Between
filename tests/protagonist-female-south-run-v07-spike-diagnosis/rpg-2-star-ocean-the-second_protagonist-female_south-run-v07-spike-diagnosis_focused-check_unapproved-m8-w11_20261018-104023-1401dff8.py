"""Focused check of the v07 post-re-press spike DIAGNOSIS receipt (UNAPPROVED / NONRUNTIME; nothing changed).

Asserts, from the receipt the diagnosis tool wrote, that
  01 the four v07 spike cases are reproduced exactly (30 fps 484 / 480 / 477, 144 fps 374) with the v07 receipt's numbers;
  02 on every spike frame the steady per-px gait itself, drawn at the same two phases, changes at least as much (so the spike
     is a sampling of the nominal gait, not something the arm easing adds); in the 30 fps release-15 case the arms already
     match the gait (no arm deviation) and the frame is still over 473;
  03 the steady per-px envelope at 9 / 10 px steps (30 fps) exceeds 473 at several phases, so the v07 "steady 473" limit is
     one start alignment, not the gait's maximum; the 144 fps steady run reaches 374 at every start alignment;
  04 v06 / v07 sources are untouched: the capture tools, manifests, amendment and art folders equal git HEAD.
Usage (repository root): python -I tests/<this dir>/<this file> [--receipt outputs/<diagnosis receipt>.json]
"""
import argparse, glob, json, subprocess, sys

ap = argparse.ArgumentParser()
ap.add_argument("--receipt", default=None)
a = ap.parse_args()
path = a.receipt or sorted(glob.glob("outputs/*south-run-v07-post-repress-spike-diagnosis-receipt_*.json"))[-1]
r = json.load(open(path, encoding="utf-8"))
ok = 0
def check(name, cond, info=""):
    global ok
    print(("OK   " if cond else "FAIL ") + name + ("  " + str(info) if info else ""))
    ok += bool(cond)

cases = {(c["fps"], c["release_frame"], c["gap"]): c for c in r["cases"]}
want = {(30, 6, 1): 484, (30, 15, 1): 480, (30, 5, 1): 477, (144, 20, 12): 374}
check("01 v07 spikes reproduced exactly", r["all_v07_spikes_reproduced"] and all(cases[k]["spike_frame"]["cell_xor"] == v and cases[k]["reproduced_exactly"] for k, v in want.items()),
      {str(k): cases[k]["spike_frame"]["cell_xor"] for k in want})
check("02 steady per-px at the same phases >= every spike; release-15 has no arm deviation",
      all(c["spike_frame"]["steady_per_px_xor_same_phases"] >= c["spike_frame"]["cell_xor"] for c in r["cases"])
      and not any(d.startswith("arm") for d in cases[(30, 15, 1)]["spike_frame"]["deviation_from_steady_per_px"]) and cases[(30, 15, 1)]["spike_frame"]["cell_xor"] > 473,
      {str(k): (c["spike_frame"]["steady_per_px_xor_same_phases"], c["spike_frame"]["deviation_from_steady_per_px"]) for k, c in cases.items()})
env = r["per_px_envelope"]; sw = r["steady_alignment_sweep"]
check("03 per-px envelope at 9/10 px > 473; 144 fps steady 374 at every alignment",
      env["9"]["max"] > 473 and env["10"]["max"] > 473 and [53, 63, 484] in env["10"]["pairs_over_473"] and sw["144"]["max"] == 374 and set(sw["144"]["per_alignment"]) == {374} and sw["30"]["max"] == 473,
      {"env9": env["9"]["max"], "env10": env["10"]["max"], "steady": {k: v["max"] for k, v in sw.items()}})
paths = ["tools/rpg-2-star-ocean-the-second_protagonist-female_south-run-v06-godot-capture_m8-w09_20261017-211600-ff47ce98.gd",
         "tools/rpg-2-star-ocean-the-second_protagonist-female_south-run-v07-godot-capture_m8-w10_20261018-082500-8770ac39.gd",
         "game/assets/characters/run-v06-unapproved", "game/assets/characters/run-v07-unapproved"]
st = subprocess.run(["git", "status", "--porcelain", "--"] + paths, capture_output=True, text=True)
check("04 v06 / v07 sources untouched vs git HEAD", st.returncode == 0 and st.stdout.strip() == "", st.stdout.strip()[:200])
print(f"{ok}/4 OK")
sys.exit(0 if ok == 4 else 1)
