"""Metric summary for the UNAPPROVED / NONRUNTIME female south compact locomotion pilot v02 (m8-w05).

Reads the v02 Godot capture receipt (per-tick foot states + pixel measurements from real 1280x720 windowed captures) and:
  * collects the pixel-measured planted-boot world displacement per tick and per ground contact (30 / 60 / 144 fps);
  * recomputes the per-tick SILHOUETTE XOR in the body frame from the drawn images themselves (the capture proved
    exact-RGB fidelity of the drawn image on every tick), by re-stacking the part PNGs for each logged state with the
    deterministic check's independent compositor; this is independent of animated scene backgrounds, and is the same
    kind of number as v01's loop-step XOR 51-231 and stop XOR 291-315 (alpha masks of the drawn frames);
  * summarises stop durations, airborne-boot steps, crown steps, extents and re-press order;
and writes one JSON next to the receipt (AGENTS naming).  Read-only on assets; review evidence only.
Usage (repository root): python -I tools/<this> --receipt outputs/<capture receipt>.json
"""
import argparse, glob, importlib.util, json, os
import numpy as np
from PIL import Image

REPO = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
CHECK_GLOB = "tests/protagonist-female-south-locomotion-compact-v02/*deterministic-check*.py"
ASSET_REL = "game/assets/characters/locomotion-pilots-compact-v02"
V8_REL = ("game/assets/characters/pixelorama-pilots/rpg-2-star-ocean-the-second_protagonist-female_"
          "south-idle-selout-v8-cloth-leather-candidate_m8-v08_20261015-021600-157a5ea0.png")
V01 = {"world_slip_window_px_per_tick_mean_max": {"60": [4.64, 5], "30": [9.32, 10], "144": [1.94, 2]},
       "slide_per_ground_contact_window_px_max": 121, "loop_step_xor": [51, 231], "stop_xor": [291, 315],
       "stop_ms_60fps": [83, 150], "repress": "runtime timer reset re-lifts the leg that just landed (stop-plant-vl -> f1-bend-vl)"}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--receipt", required=True)
    a = ap.parse_args()
    os.chdir(REPO)
    spec = importlib.util.spec_from_file_location("v02check", glob.glob(CHECK_GLOB)[0])
    chk = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(chk)
    m = json.load(open(glob.glob(os.path.join(ASSET_REL, "*-manifest_*.json"))[0], encoding="utf-8"))
    parts = {e["role"]: chk.texels(chk.rgba(os.path.join(ASSET_REL, e["file"]))) for e in m["parts"]}
    v8 = set(chk.texels(chk.rgba(V8_REL)))
    rec = json.load(open(a.receipt, encoding="utf-8"))
    cache = {}

    def mask(e):
        if e["show_v8"]:
            return v8
        k = json.dumps(e["state"], sort_keys=True)
        if k not in cache:
            cache[k] = set(chk.compose(parts, m["rig"], e["state"]))
        return cache[k]

    def seq_xor(ticks):
        out = []
        for p, q in zip(ticks, ticks[1:]):
            out.append(len(mask(p) ^ mask(q)))
        return out

    def crown(mk):
        return min(y for (x, y) in mk if 10 <= x < 70)

    summary = {"scenes": {}, "v01_reference": V01}
    allw = {"30": [], "60": [], "144": []}
    for sk, sr in rec["scenes"].items():
        s = {"walk": {}, "stops": {}, "repress": {}}
        for mode, w in sr["walk"].items():
            fps = mode.split("-")[1].replace("fps", "")
            t = w["ticks"]
            xs = seq_xor([e for e in t if e["input"]])
            allw[fps] += xs
            cr = [crown(mask(e)) for e in t if e["input"]]
            low = [max(y for (_, y) in mask(e)) for e in t if e["input"]]
            per_tick = [p for e in t for p in e.get("planted", {}).values()]
            s["walk"][mode] = {
                "ticks": len(t), "speed_logical_px_s": round(w["logical_px_per_s_measured"], 3),
                "planted_tick_pairs": w["planted_tick_pairs"],
                "planted_world_disp_per_tick_window_px": {"row_max": w["planted_sole_row_world_disp_max_px"],
                                                          "x_max": w["planted_sole_x_world_disp_max_px"],
                                                          "row_mean": float(np.mean([abs(p["sole_row_d"]) for p in per_tick])) if per_tick else 0.0},
                "planted_boot_texels_compared": w["planted_boot_texels_compared"], "planted_boot_texels_changed": w["planted_boot_texels_changed"],
                "contact_runs": [{"side": c["side"], "ticks": c["ticks"], "world_row_span_px": c["world_row_max"] - c["world_row_min"]} for c in w["contact_runs"]],
                "per_contact_slide_window_px_max": max(c["world_row_max"] - c["world_row_min"] for c in w["contact_runs"]),
                "image_silhouette_xor_per_tick": {"max": max(xs), "mean": round(float(np.mean(xs)), 1)},
                "screen_mask_xor_per_tick_max_incl_background_animation": w["cell_silhouette_xor_max_per_tick"],
                "unplanted_sole_step_world_px_per_tick_max": w["unplanted_sole_row_step_max_px"],
                "crown_cell_rows": sorted(set(cr)), "lowest_cell_row_max": max(low),
                "visible_height_texels_max": max(lo - c for lo, c in zip(low, cr)) + 1,
            }
        for tag, st in sr["stops"].items():
            t = st["ticks"]
            rel_i = next(i for i, e in enumerate(t) if not e["input"])
            xs = seq_xor(t[rel_i - 1:])
            mode = "flight" if all(v != "contact" for v in st["modes_at_release"].values()) else "stance"
            s["stops"][tag] = {"fps": st["fps"], "phase_px": st["released_at_phase_px"], "release": mode,
                               "v8_after_ms": round(st["v8_after_ms"], 1), "switch_to_v8_xor": st["switch_to_v8_xor"],
                               "image_silhouette_xor_max": max(xs),
                               "planted_world_disp_max_px": max(st["stop"]["planted_sole_row_world_disp_max_px"], st["stop"]["planted_sole_x_world_disp_max_px"]),
                               "airborne_step_max_px": st["stop"]["unplanted_sole_row_step_max_px"],
                               "crown_step_max": max(abs(crown(mask(p)) - crown(mask(q))) for p, q in zip(t[rel_i - 1:], t[rel_i:]))}
        for tag, rp in sr["repress"].items():
            t = rp["ticks"]
            i0 = next(i for i, e in enumerate(t) if e["tick"] == rp["repress_tick"])
            xs = seq_xor(t[i0 - 1:i0 + 12])
            s["repress"][tag] = {"phase_px": rp["released_at_phase_px"], "gap_ticks": rp["gap_ticks"],
                                 "showing_v8_at_repress": rp["showing_v8_at_repress"],
                                 "last_touchdown": rp["last_touchdown_before_repress"], "next_touchdown": rp["next_touchdown_after_repress"],
                                 "next_touchdown_ms": rp["next_touchdown_ms_after_repress"],
                                 "last_landed_stood_ms": rp["last_landed_boot_stood_ms_touchdown_to_liftoff"],
                                 "alternation_ok": rp["alternation_ok_next_touchdown_is_the_other_boot"],
                                 "image_silhouette_xor_max_200ms": max(xs),
                                 "planted_world_disp_max_px": rp["repress_200ms"]["planted_sole_row_world_disp_max_px"],
                                 "airborne_step_max_px_200ms": rp["repress_200ms"]["unplanted_sole_row_step_max_px"]}
        summary["scenes"][sk] = s
    # roll-ups
    roll = {"walk_image_xor_max_per_fps": {k: max(v) for k, v in allw.items() if v}}
    for fps in (30, 60, 144):
        for mode in ("flight", "stance"):
            ss = [v for sc in summary["scenes"].values() for v in sc["stops"].values() if v["fps"] == fps and v["release"] == mode]
            if ss:
                roll[f"stops_{fps}fps_{mode}"] = {"cases": len(ss), "v8_after_ms": [min(v["v8_after_ms"] for v in ss), max(v["v8_after_ms"] for v in ss)],
                                                 "image_xor_max": max(v["image_silhouette_xor_max"] for v in ss),
                                                 "airborne_step_max_px": max(v["airborne_step_max_px"] for v in ss),
                                                 "crown_step_max": max(v["crown_step_max"] for v in ss)}
    rps = [v for sc in summary["scenes"].values() for v in sc["repress"].values()]
    roll["repress"] = {"cases": len(rps), "alternation_ok": sum(v["alternation_ok"] for v in rps),
                       "last_landed_stood_ms_min": min(v["last_landed_stood_ms"] for v in rps),
                       "next_touchdown_ms": [min(v["next_touchdown_ms"] for v in rps), max(v["next_touchdown_ms"] for v in rps)],
                       "image_xor_max_200ms": max(v["image_silhouette_xor_max_200ms"] for v in rps),
                       "planted_world_disp_max_px": max(v["planted_world_disp_max_px"] for v in rps)}
    summary["rollup"] = roll
    summary["source_receipt"] = os.path.relpath(a.receipt, REPO).replace("\\", "/")
    summary["status"] = "UNAPPROVED / NONRUNTIME review evidence; agent measurement, not a human review"
    out = a.receipt.replace("capture-receipt", "metrics-summary")
    with open(out, "w", encoding="utf-8", newline="\n") as f:
        json.dump(summary, f, indent=1)
        f.write("\n")
    print(json.dumps(roll, indent=1))
    for sk, s in summary["scenes"].items():
        for mode, w in s["walk"].items():
            print(sk, mode, {k: w[k] for k in ("planted_world_disp_per_tick_window_px", "per_contact_slide_window_px_max",
                                               "image_silhouette_xor_per_tick", "crown_cell_rows", "lowest_cell_row_max",
                                               "visible_height_texels_max", "unplanted_sole_step_world_px_per_tick_max")})
    print("wrote", out)


if __name__ == "__main__":
    main()
