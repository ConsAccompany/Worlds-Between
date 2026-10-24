"""Bounded Godot normal-speed east walk/stop source-fit for Heya h176ew01 (test-only).

Uses the checked runner (finite deadline + diagnostic stop), Xvfb 640x360, OpenGL3 and Dummy audio. Loads the
optional source sprite set and stop supplement from the opt-in package, renders a 3x source preview plus the
0.5x game-scale sprite with pivot (40,104), and captures start/walk/stop/repress/reverse-stop at 12 targets in
alternating bright/dark themes with EN/ZH labels. It records the actual elapsed time and independently re-derives
the expected frame from that time.

The stop entry phase is derived from the frozen timing, not from a literal bridge name: at STOP_MS-1 the walk
is phase 11, so the phase11 supplemental stop bridge is the only coherent choice. The reverse stop test likewise
starts from the final reverse-walk phase (also 11), plays the same bridge's s2/s1 in reverse order, restores walk
phase 11 and ends on neutral idle f00. This is reversing a supplemental stop bridge for test coverage, NOT an
actual direction/host reversal. The tool asserts pre-stop phase == selected bridge entry and every stop/reverse
endpoint; no runtime adoption, default change, input approval or art approval. Writes only under
outputs/heya-ew176/fit/.
"""
import hashlib, importlib.util, json, os
from pathlib import Path
from PIL import Image

R = Path(__file__).resolve().parents[1]
TAG = "20261024-154500-h176ew01"
OUT = R / "outputs/heya-ew176/fit"
OUT.mkdir(parents=True, exist_ok=True)
FIT = OUT / "capture"
n = 1
while FIT.exists() and any(FIT.iterdir()):
    n += 1
    FIT = OUT / f"capture-r{n}"
FIT.mkdir(parents=True, exist_ok=True)
HOMEDIR = R / "outputs/heya-ew176/godot-home"
for sub in ("home", "config", "data", "cache", "run", "tmp"):
    (HOMEDIR / sub).mkdir(parents=True, exist_ok=True)
os.environ.update(TMPDIR=str(HOMEDIR / "tmp"), HOME=str(HOMEDIR / "home"),
                  XDG_CONFIG_HOME=str(HOMEDIR / "config"), XDG_DATA_HOME=str(HOMEDIR / "data"),
                  XDG_CACHE_HOME=str(HOMEDIR / "cache"), XDG_RUNTIME_DIR=str(HOMEDIR / "run"))
PKG = R / "game/assets/characters/heya-native-v01/east-walk"
runtime = next(PKG.glob("*sprite-set-runtime*.json")).resolve()
stop = next(PKG.glob("*stop-transition-supplemental*.json")).resolve()
gd = R / "tools/rpg-2-star-ocean-the-second_heya_walk-east_normal-speed-fit_test-only-v01_20261024-154500-h176ew01.gd"
runner_path = R / "tools/rpg-2-star-ocean-the-second_godot_checked-runner_v01_20261018-203400-f74ac6d1.py"
godot = Path("/home/kel/projects/worlds-between/tooling/godot-4.7.2/Godot_v4.7.2-stable_linux.x86_64")

WALK_MS = 40
START_MS = 320
STOP_MS = 800
REPRESS_MS = 940
REV_MS = 1420
END_MS = 1560
NPH = 12


def sha(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def phase_at(ms, origin_ms):
    return ((ms - origin_ms) // WALK_MS) % NPH


FORWARD_PREST0P_PHASE = phase_at(STOP_MS - 1, START_MS)
REVERSE_PREST0P_PHASE = phase_at(REV_MS - 1, REPRESS_MS)


def state_at(ms):
    if ms < START_MS:
        return ("start", 0)
    if ms < STOP_MS:
        return ("walk", phase_at(ms, START_MS))
    if ms < STOP_MS + WALK_MS:
        return ("s1", 0)
    if ms < STOP_MS + 2 * WALK_MS:
        return ("s2", 0)
    if ms < REPRESS_MS:
        return ("idle", 0)
    if ms < REV_MS:
        return ("walk", phase_at(ms, REPRESS_MS))
    if ms < REV_MS + WALK_MS:
        return ("s2", 0)
    if ms < REV_MS + 2 * WALK_MS:
        return ("s1", 0)
    if ms < END_MS:
        return ("walk", REVERSE_PREST0P_PHASE)
    return ("idle", 0)


TARGETS = [160, 560, 780, 820, 860, 900, 960, 1200, 1440, 1480, 1520, 1560]


spec = importlib.util.spec_from_file_location("checked", runner_path)
runner = importlib.util.module_from_spec(spec); spec.loader.exec_module(runner)
before = {str(p): sha(p) for p in [runtime, stop, gd, runner_path]}
cmd = ["xvfb-run", "-a", "-s", "-screen 0 640x360x24", str(godot), "--path", str(R / "game"),
       "--resolution", "640x360", "--rendering-driver", "opengl3", "--audio-driver", "Dummy",
       "--script", str(gd), "--", str(runtime), str(stop), str(FIT.resolve()), TAG]
log = OUT / f"normal-speed-{FIT.name}.runner.log"
res = runner.run_checked(cmd, 75, ["HEYA_HEW176_EAST_WALK_NORMAL_SPEED_PASS captures=12"], log)
res.pop("log", None)
man = next(FIT.glob("*normal-speed-manifest*.json"))
m = json.loads(man.read_text(encoding="utf8"))
captures = sorted(FIT.glob("*normal-speed-*.png"))
dims = {p.name: list(Image.open(p).size) for p in captures}
runtime_j = json.loads(runtime.read_text(encoding="utf8"))
stop_j = json.loads(stop.read_text(encoding="utf8"))
walk = runtime_j["actions"]["walk"]["east"]
idle = runtime_j["actions"]["idle"]["east"]

# Independently derive the entry phase from the frozen timing and select that bridge. The bridge key is
# checked against the derived phase, so a literal phase7/phase11 drift cannot silently pass.
forward_prestop_phase = phase_at(STOP_MS - 1, START_MS)
reverse_prestop_phase = phase_at(REV_MS - 1, REPRESS_MS)
bridge_key = f"phase{forward_prestop_phase}"
east_bridges = stop_j["phase_bridges"]["east"]
if bridge_key not in east_bridges:
    raise SystemExit(f"derived stop entry {bridge_key} missing from supplemental")
bridge = east_bridges[bridge_key]
bridge_entry_phase = int(bridge[0].get("index", -1)) if bridge else -1
path_for = {("walk", i): walk[i]["file"] for i in range(NPH)}
path_for[("idle", 0)] = idle[0]["file"]
path_for[("s1", 0)] = bridge[1]["file"]
path_for[("s2", 0)] = bridge[2]["file"]
path_for[("start", 0)] = idle[0]["file"]
frame_ok, sha_ok, target_ok, size_ok, fit_ok = True, True, True, True, True
for c in m["captures"]:
    exp = state_at(c["elapsed_ms"])
    frame_ok &= (c["kind"], c["frame_index"]) == exp
    target_ok &= (c["target_kind"], c["target_frame_index"]) == state_at(c["target_ms"])
    rel = path_for[exp]
    src = PKG / rel
    sha_ok &= c.get("frame_file") == rel and c.get("frame_sha256") == sha(src)
    fit_ok &= c["pivot"] == [40, 104] and abs(c["scale"] - 0.5) < 1e-9 and c["logical_height_px"] == 48 \
        and c["texture_size"] == [80, 112] and c["sprite_rect"] == [40.0, 56.0]
size_ok = len(captures) == 12 and all(v == [640, 360] for v in dims.values())
span_ok = sorted({(c["kind"], c["frame_index"]) for c in m["captures"]}) == [("idle", 0), ("s1", 0), ("s2", 0),
                                                                           ("start", 0), ("walk", 0), ("walk", 6),
                                                                           ("walk", 11)]
speed_ok = all(c["elapsed_ms"] <= c["target_ms"] + 250 for c in m["captures"])
theme_ok = {c.get("theme") for c in m["captures"]} == {"bright", "dark"}
label_ok = all(isinstance(c.get("label_bilingual"), str) and "/" in c["label_bilingual"]
               and any(ord(ch) > 127 for ch in c["label_bilingual"]) for c in m["captures"])
timeline_ok = [c["target_ms"] for c in m["captures"]] == TARGETS

# Explicit, independently-derived continuity predicate. Timing decides the phase; the selected bridge
# must match it, and every stop/reverse boundary must connect coherently.
bridge_shape_ok = bool(
    len(bridge) == 4
    and bridge[0].get("ref") == "walk" and int(bridge[0].get("index", -1)) == forward_prestop_phase
    and bridge[-1].get("ref") == "idle" and int(bridge[-1].get("index", -1)) == 0
)
forward_prestop_ok = bool(
    state_at(STOP_MS - 1) == ("walk", forward_prestop_phase)
    and bridge_entry_phase == forward_prestop_phase
    and bridge_key == f"phase{forward_prestop_phase}"
)
reverse_prestop_ok = bool(
    state_at(REV_MS - 1) == ("walk", reverse_prestop_phase)
    and bridge_entry_phase == reverse_prestop_phase
)
forward_stop_endpoints_ok = bool(
    bridge_shape_ok
    and state_at(STOP_MS) == ("s1", 0)
    and state_at(STOP_MS + WALK_MS) == ("s2", 0)
    and state_at(STOP_MS + 2 * WALK_MS) == ("idle", 0)
    and all(state_at(t) == ("idle", 0) for t in range(STOP_MS + 2 * WALK_MS, REPRESS_MS))
)
reverse_endpoints_ok = bool(
    bridge_shape_ok
    and bridge_entry_phase == reverse_prestop_phase
    and state_at(REV_MS) == ("s2", 0)
    and state_at(REV_MS + WALK_MS) == ("s1", 0)
    and state_at(REV_MS + 2 * WALK_MS) == ("walk", reverse_prestop_phase)
    and state_at(END_MS) == ("idle", 0)
)
by_target = {int(c["target_ms"]): c for c in m["captures"]}
expected_capture_files = {
    780: walk[forward_prestop_phase]["file"],
    820: bridge[1]["file"],
    860: bridge[2]["file"],
    900: idle[0]["file"],
    1440: bridge[2]["file"],
    1480: bridge[1]["file"],
    1520: walk[reverse_prestop_phase]["file"],
    1560: idle[0]["file"],
}
capture_continuity_ok = bool(all(
    t in by_target and by_target[t].get("frame_file") == f for t, f in expected_capture_files.items()
))
continuity = {
    "forward_prestop_phase_derived": forward_prestop_phase,
    "reverse_prestop_phase_derived": reverse_prestop_phase,
    "selected_bridge_key": bridge_key,
    "selected_bridge_walk_index": bridge_entry_phase,
    "forward_prestop_equals_selected": forward_prestop_ok,
    "reverse_prestop_equals_selected": reverse_prestop_ok,
    "bridge_shape_walk_to_idle": bridge_shape_ok,
    "forward_stop_endpoints_continuous": forward_stop_endpoints_ok,
    "reverse_stop_endpoints_continuous": reverse_endpoints_ok,
    "capture_sequence_continuous": capture_continuity_ok,
}
continuity_ok = bool(forward_prestop_ok and reverse_prestop_ok and forward_stop_endpoints_ok
                     and reverse_endpoints_ok and capture_continuity_ok)

after = {str(p): sha(p) for p in [runtime, stop, gd, runner_path]}
proof = {"task": "content.char.heya.walk-east normal-speed Godot source-fit (test-only)",
         "command": cmd, "tag": TAG, "runtimeManifest": str(runtime.relative_to(R)),
         "runtimeManifestSha256": before[str(runtime)], "stopManifest": str(stop.relative_to(R)),
         "stopManifestSha256": before[str(stop)], "script": str(gd.relative_to(R)),
         "scriptSha256": before[str(gd)], "runner": str(runner_path.relative_to(R)),
         "runnerSha256": before[str(runner_path)], "godot": str(godot), "godotSha256": sha(godot),
         "log": str(log.relative_to(R)), "result": res, "captures": [str(p.relative_to(R)) for p in captures],
         "captureDimensions": dims, "manifest": str(man.relative_to(R)), "manifestSha256": sha(man),
         "normalSpeedFramesExact": frame_ok, "frameHashesExact": sha_ok, "targetStatesExact": target_ok,
         "phaseSpanExact": span_ok, "fitContractExact": fit_ok, "elapsedWithinBound": speed_ok,
         "themeBrightDark": theme_ok, "bilingualLabels": label_ok, "timelineExact": timeline_ok,
         "continuityPredicateExact": continuity_ok, "continuity": continuity,
         "expectedStates": {str(c["target_ms"]): list(state_at(c["target_ms"])) for c in m["captures"]},
         "runtimeAdopted": m.get("runtimeAdopted"), "artApproved": m.get("artApproved"), "testOnly": True,
         "audioDriver": "Dummy", "renderingDriver": "opengl3", "xvfb": "640x360x24",
         "note": "direct deterministic animated source-fit overlay through the existing checked runner; east walk "
                 "start/walk/stop(phase-derived s1,s2,idle)/repress/reverse supplemental stop bridge at 40 ms, "
                 "settle 120 ms inclusive, bright+dark with EN/ZH labels; reverse means replaying the supplemental "
                 "stop bridge, not an actual direction/host reversal; not ordinary actor integration, not human "
                 "motion review"}
proof["passed"] = bool(res.get("passed") and size_ok and frame_ok and sha_ok and target_ok and fit_ok and span_ok
                       and speed_ok and theme_ok and label_ok and timeline_ok and continuity_ok and before == after
                       and m.get("runtimeAdopted") is False and m.get("artApproved") is False)
proof_path = OUT / f"rpg-2-star-ocean-the-second_heya_walk-east-normal-speed-proof_test-only-v01_{TAG}-{FIT.name}.json"
proof_path.write_text(json.dumps(proof, indent=2) + "\n", encoding="utf8")
print(json.dumps({"passed": proof["passed"], "captures": proof["captures"], "frame_ok": frame_ok,
                  "sha_ok": sha_ok, "target_ok": target_ok, "fit_ok": fit_ok, "speed_ok": speed_ok,
                  "continuity_ok": continuity_ok, "continuity": continuity, "dims": dims, "result": res}, indent=2))
print("HEYA_HEW176_EAST_WALK_NORMAL_SPEED_FIT " + ("PASS" if proof["passed"] else "FAIL"))
raise SystemExit(0 if proof["passed"] else 1)
