#!/usr/bin/env python3
"""Independent Heya north walk-fit continuity audit (no author/checker/fit imports).

Reads frozen artifacts only: the Godot fit capture manifest, the opt-in runtime sprite set, the
opt-in stop supplement and (optionally) the fit proof.  It derives the pre-stop walk phase from
the frozen timing constants embedded in the captures, matches the actually captured s1/s2 frames
back to the stop-bridge phase that supplied them, and asserts:

  * forward pre-stop walk phase == selected forward stop-bridge entry phase;
  * reverse pre-stop walk phase == selected reverse stop-bridge entry phase;
  * reverse restored walk phase == reverse pre-stop/entry phase;
  * every forward stop endpoint (walk -> s1 -> s2 -> idle) and reverse endpoint
    (s2 -> s1 -> walk entry -> idle) is continuous and lands on the neutral idle f00.

This is a pre/post-fix diagnostic.  It deliberately does not trust the fit proof's `passed` field
or the fit tool's `expectedStates`; it re-derives everything from bytes and timing.
"""
import argparse
import hashlib
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
NPH = 12


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def load(path):
    return json.loads(Path(path).read_text(encoding="utf8"))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--manifest", required=True, help="Godot fit capture manifest JSON")
    ap.add_argument("--runtime", required=True, help="opt-in runtime sprite-set JSON")
    ap.add_argument("--stop", required=True, help="opt-in stop-transition supplemental JSON")
    ap.add_argument("--proof", default=None, help="fit proof JSON (recorded, not trusted)")
    ap.add_argument("--out-json", required=True)
    ap.add_argument("--out-md", required=True)
    ap.add_argument("--label", default="fit-continuity")
    a = ap.parse_args()

    man_p, run_p, stop_p = Path(a.manifest), Path(a.runtime), Path(a.stop)
    man, runtime, stop = load(man_p), load(run_p), load(stop_p)
    proof = load(a.proof) if a.proof else None
    caps = man["captures"]
    if not caps:
        raise SystemExit("no captures")

    # Frozen timing is taken from the captures themselves, not from the fit tool source.
    c0 = caps[0]
    walk_ms = int(c0["walk_ms"])
    start_ms = int(c0["start_ms"])
    stop_ms = int(c0["stop_ms"])
    repress_ms = int(c0["repress_ms"])
    rev_ms = int(c0["reversal_ms"])
    settle_inclusive = int(c0["settle_ms_inclusive"])
    walk = runtime["actions"]["walk"]["north"]
    idle = runtime["actions"]["idle"]["north"]
    if len(walk) != NPH:
        raise SystemExit(f"expected {NPH} walk phases, got {len(walk)}")

    def phase_after(ms, origin_ms):
        return ((ms - origin_ms) // walk_ms) % NPH

    forward_prestop_phase = phase_after(stop_ms - 1, start_ms)
    reverse_prestop_phase = phase_after(rev_ms - 1, repress_ms)

    by_target = {int(c["target_ms"]): c for c in caps}

    def one(kind, before=None, after=None):
        found = [c for c in caps if c["kind"] == kind
                 and (before is None or int(c["target_ms"]) < before)
                 and (after is None or int(c["target_ms"]) >= after)]
        if len(found) != 1:
            raise SystemExit(f"expected exactly one {kind} capture in window {before}/{after}, got {len(found)}")
        return found[0]

    forward_prestop = max((c for c in caps if int(c["target_ms"]) < stop_ms), key=lambda c: int(c["target_ms"]))
    forward_s1 = one("s1", before=repress_ms)
    forward_s2 = one("s2", before=repress_ms)
    forward_idle = one("idle", before=repress_ms)
    reverse_s2 = one("s2", after=rev_ms)
    reverse_s1 = one("s1", after=rev_ms)
    reverse_restore = one("walk", after=rev_ms)
    final_idle = max(caps, key=lambda c: int(c["target_ms"]))

    # Map each captured stop frame back to the bridge phase that actually supplied it.
    bridges = stop["phase_bridges"]["north"]
    bridge_phase_by_file = {}
    for p in range(NPH):
        for idx in (1, 2):
            entry = bridges[f"phase{p}"][idx]
            bridge_phase_by_file[entry["file"]] = p
            bridge_phase_by_file[Path(entry["file"]).name] = p

    def bridge_phase(cap):
        f = str(cap.get("frame_file", ""))
        if f in bridge_phase_by_file:
            return bridge_phase_by_file[f]
        if Path(f).name in bridge_phase_by_file:
            return bridge_phase_by_file[Path(f).name]
        raise SystemExit(f"cannot map captured stop frame to a bridge phase: {f}")

    forward_selected_phase = bridge_phase(forward_s1)
    forward_selected_phase_s2 = bridge_phase(forward_s2)
    reverse_selected_phase = bridge_phase(reverse_s2)
    reverse_selected_phase_s1 = bridge_phase(reverse_s1)
    if forward_selected_phase != forward_selected_phase_s2:
        raise SystemExit("forward s1/s2 came from different bridge phases")
    if reverse_selected_phase != reverse_selected_phase_s1:
        raise SystemExit("reverse s1/s2 came from different bridge phases")

    fwd_bridge = bridges[f"phase{forward_selected_phase}"]
    rev_bridge = bridges[f"phase{reverse_selected_phase}"]
    fwd_first, fwd_last = fwd_bridge[0], fwd_bridge[-1]
    rev_first, rev_last = rev_bridge[0], rev_bridge[-1]
    idle0_name = Path(idle[0]["file"]).name

    checks = {
        "forward_prestop_walk_phase_derived": forward_prestop_phase,
        "forward_selected_bridge_phase": forward_selected_phase,
        "forward_prestop_equals_selected": forward_prestop_phase == forward_selected_phase,
        "forward_captured_prestop_frame_is_phase": int(forward_prestop["frame_index"]) == forward_prestop_phase,
        "forward_s1_s2_supplied_by_selected_bridge": (
            bridge_phase(forward_s1) == forward_selected_phase and bridge_phase(forward_s2) == forward_selected_phase
        ),
        "forward_stop_endpoints_walk_to_idle": (
            fwd_first.get("ref") == "walk" and int(fwd_first.get("index", -1)) == forward_selected_phase
            and fwd_last.get("ref") == "idle" and int(fwd_last.get("index", -1)) == 0
            and Path(str(forward_idle["frame_file"])).name == idle0_name
        ),
        "reverse_prestop_walk_phase_derived": reverse_prestop_phase,
        "reverse_selected_bridge_phase": reverse_selected_phase,
        "reverse_prestop_equals_selected": reverse_prestop_phase == reverse_selected_phase,
        "reverse_restore_walk_phase": int(reverse_restore["frame_index"]),
        "reverse_restore_equals_reverse_prestop": int(reverse_restore["frame_index"]) == reverse_prestop_phase,
        "reverse_s2_s1_supplied_by_selected_bridge": (
            bridge_phase(reverse_s2) == reverse_selected_phase and bridge_phase(reverse_s1) == reverse_selected_phase
        ),
        "reverse_bridge_endpoints_walk_to_idle": (
            rev_first.get("ref") == "walk" and int(rev_first.get("index", -1)) == reverse_selected_phase
            and rev_last.get("ref") == "idle" and int(rev_last.get("index", -1)) == 0
        ),
        "reverse_sequence_ends_idle_f00": (
            final_idle["kind"] == "idle" and int(final_idle["target_ms"]) == max(int(c["target_ms"]) for c in caps)
            and Path(str(final_idle["frame_file"])).name == idle0_name
        ),
        "exact_targets_preserved": [int(c["target_ms"]) for c in caps] == [160, 560, 780, 820, 860, 900, 960, 1200, 1440, 1480, 1520, 1560],
        "walk_and_settle_durations_preserved": walk_ms == 40 and settle_inclusive == 120,
    }
    checks["all_stop_and_reverse_endpoints_continuous"] = bool(
        checks["forward_prestop_equals_selected"]
        and checks["forward_s1_s2_supplied_by_selected_bridge"]
        and checks["forward_stop_endpoints_walk_to_idle"]
        and checks["reverse_prestop_equals_selected"]
        and checks["reverse_restore_equals_reverse_prestop"]
        and checks["reverse_s2_s1_supplied_by_selected_bridge"]
        and checks["reverse_bridge_endpoints_walk_to_idle"]
        and checks["reverse_sequence_ends_idle_f00"]
    )
    passed = bool(
        checks["forward_prestop_equals_selected"]
        and checks["forward_s1_s2_supplied_by_selected_bridge"]
        and checks["forward_stop_endpoints_walk_to_idle"]
        and checks["reverse_prestop_equals_selected"]
        and checks["reverse_restore_equals_reverse_prestop"]
        and checks["reverse_s2_s1_supplied_by_selected_bridge"]
        and checks["reverse_bridge_endpoints_walk_to_idle"]
        and checks["reverse_sequence_ends_idle_f00"]
        and checks["exact_targets_preserved"]
        and checks["walk_and_settle_durations_preserved"]
    )

    artifacts = {
        "fit_manifest": str(man_p),
        "fit_manifest_sha256": sha(man_p),
        "runtime": str(run_p),
        "runtime_sha256": sha(run_p),
        "stop": str(stop_p),
        "stop_sha256": sha(stop_p),
        "fit_proof": str(a.proof) if a.proof else None,
        "fit_proof_sha256": sha(a.proof) if a.proof else None,
        "audit_script": str(Path(__file__).resolve().relative_to(ROOT)),
        "audit_script_sha256": sha(Path(__file__)),
    }
    out = {
        "audit": "heya north walk-fit independent continuity",
        "label": a.label,
        "task": "content.char.heya.walk-north (Batch171 follow-up, fit repair)",
        "scope": "north-only source fit; no runtime adoption, input approval or art/motion approval",
        "derivation": {
            "walk_ms": walk_ms,
            "start_ms": start_ms,
            "stop_ms": stop_ms,
            "repress_ms": repress_ms,
            "reversal_ms": rev_ms,
            "settle_ms_inclusive": settle_inclusive,
            "walk_phases": NPH,
            "forward_prestop_ms": stop_ms - 1,
            "reverse_prestop_ms": rev_ms - 1,
        },
        "actual_capture_sequence": [
            {"target_ms": int(c["target_ms"]), "kind": c["kind"], "frame_index": int(c["frame_index"]),
             "frame_file": c["frame_file"]} for c in caps
        ],
        "checks": checks,
        "fit_proof_self_reported_passed": None if proof is None else proof.get("passed"),
        "independent_continuity_passed": passed,
        "verdict": "PASS" if passed else "FAIL",
        "artifacts": artifacts,
        "note": "The proof's own passed field is recorded but not trusted. This audit re-derives the "
                "pre-stop phase from frozen timing and maps captured s1/s2 frames back to the stop bridge.",
    }
    Path(a.out_json).parent.mkdir(parents=True, exist_ok=True)
    Path(a.out_json).write_text(json.dumps(out, indent=2) + "\n", encoding="utf8")

    lines = [
        f"# Heya north walk-fit continuity audit — {a.label}",
        "",
        f"- Independent verdict: **{out['verdict']}**",
        f"- Fit proof self-reported passed: `{out['fit_proof_self_reported_passed']}` (not trusted)",
        f"- Scope: {out['scope']}",
        f"- Frozen timing: walk {walk_ms} ms, start {start_ms} ms, stop {stop_ms} ms, repress {repress_ms} ms, "
        f"reverse {rev_ms} ms, settle {settle_inclusive} ms inclusive",
        "",
        "## Derived continuity predicates",
        "",
        "| Predicate | Value | Pass |",
        "| --- | --- | --- |",
    ]
    for k, v in checks.items():
        if isinstance(v, bool):
            lines.append(f"| `{k}` | `{v}` | {'PASS' if v else 'FAIL'} |")
        else:
            lines.append(f"| `{k}` | `{v}` | — |")
    lines += [
        "",
        "## Actual captured stop/reverse frames",
        "",
        "| t (ms) | kind | idx | frame |",
        "| --- | --- | --- | --- |",
    ]
    for c in caps:
        if int(c["target_ms"]) >= stop_ms - 40:
            lines.append(f"| {int(c['target_ms'])} | {c['kind']} | {int(c['frame_index'])} | `{Path(str(c['frame_file'])).name}` |")
    lines += [
        "",
        "## Artifacts",
        "",
        f"- manifest: `{artifacts['fit_manifest']}` `{artifacts['fit_manifest_sha256']}`",
        f"- runtime: `{artifacts['runtime']}` `{artifacts['runtime_sha256']}`",
        f"- stop: `{artifacts['stop']}` `{artifacts['stop_sha256']}`",
        f"- proof: `{artifacts['fit_proof']}` `{artifacts['fit_proof_sha256']}`",
        f"- audit script: `{artifacts['audit_script']}` `{artifacts['audit_script_sha256']}`",
        "",
        "Existing fit proofs/reports are immutable and were not modified by this audit.",
    ]
    Path(a.out_md).parent.mkdir(parents=True, exist_ok=True)
    Path(a.out_md).write_text("\n".join(lines) + "\n", encoding="utf8")
    print(json.dumps({"verdict": out["verdict"], "passed": passed, "checks": checks,
                      "out_json": str(Path(a.out_json)), "out_md": str(Path(a.out_md))}, indent=2))
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
