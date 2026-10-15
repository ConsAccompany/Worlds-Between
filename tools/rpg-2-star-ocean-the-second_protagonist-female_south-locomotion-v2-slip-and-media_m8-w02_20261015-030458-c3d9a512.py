"""Female south locomotion v2 (m8-w02) - measured foot slip from the captured pixels + review media.

Inputs: the Godot capture receipt (outputs/...locomotion-v2-capture-receipt_m8-w02_<run>.json) and
the per-tick captures + sprite-free backgrounds the harness wrote to --motion-dir (scratch).

Slip is measured on the CAPTURED WINDOW PIXELS, not on declared data:
  * sprite mask = pixels that differ from the sprite-free background of the same scene, inside the
    80x112 cell rectangle the receipt reports for that tick;
  * for every tick whose frame has a planted leg, the planted sole = lowest masked window row in that
    leg's column band (cell x < 38 = viewer-left leg "vl", x >= 38 = viewer-right "vr", rows >= 84),
    and its x = mean masked column of the bottom 2 sole rows;
  * a stance = consecutive ticks with that leg planted; slip = max - min of the sole's window y (the
    motion axis) over the stance; per-tick drift = |change| between consecutive ticks of a stance.
  The camera is static, so window pixels are world pixels (1 window px = 0.5 logical px).
Head motion (the cost of the root lock): head top = first masked row in cell columns 10-45; its
residual against uniform motion (2 * hero_y + const) and its per-tick step are reported.
Media (into outputs/, one file per item, no collages): per scene x mode a real-time 60 fps MP4 (2x
nearest crop, at the tick rate) and a real-time 30 fps GIF; for run-140 also a quarter-speed MP4 labelled "slowmo-quarter"
for frame-by-frame inspection; per alternative an in-place loop GIF of the cell frames.
GIF/MP4 are lossy review aids; the PNG captures are the colour-exact evidence.
Usage (repo root):  python -I tools/<this> --receipt <receipt json> --motion-dir <scratch dir>
"""
import argparse, hashlib, json, os, subprocess, tempfile
import numpy as np
from PIL import Image

REPO = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
OUT = os.path.join(REPO, "outputs")
V2_DIR = os.path.join(REPO, "game/assets/characters/walk-pilots-v2")
SLUG = "rpg-2-star-ocean-the-second"


def sha(path):
    with open(path, "rb") as f:
        return hashlib.sha256(f.read()).hexdigest()


def ffmpeg(args):
    subprocess.run(["ffmpeg", "-hide_banner", "-loglevel", "error", "-y"] + args, check=True)


def load(path):
    return np.array(Image.open(path).convert("RGB")).astype(np.int16)


def measure(bg, img, origin):
    ox, oy = origin
    cell_bg = bg[oy:oy + 112, ox:ox + 80]
    cell = img[oy:oy + 112, ox:ox + 80]
    mask = (np.abs(cell - cell_bg).sum(axis=2) > 0)
    res = {}
    for leg, (x0, x1) in (("vl", (0, 38)), ("vr", (38, 80))):
        band = mask[84:, x0:x1]
        rows = np.nonzero(band.any(axis=1))[0]
        if rows.size == 0:
            continue
        sole = int(rows.max()) + 84
        bottom = mask[sole - 1:sole + 1, x0:x1]
        xs = np.nonzero(bottom.any(axis=0))[0]
        res[leg] = {"sole_y": oy + sole, "sole_x": ox + x0 + float(xs.mean())}
    head_rows = np.nonzero(mask[:, 10:46].any(axis=1))[0]
    res["head_top_y"] = oy + int(head_rows.min()) if head_rows.size else None
    return res


def analyse(rec, motion_dir):
    out = {}
    for scene, sd in rec["scenes"].items():
        bg = load(os.path.join(motion_dir, f"{scene}_background.png"))
        out[scene] = {}
        for mode, md in sd["modes"].items():
            per_tick, stances, cur = [], [], {}
            for t in md["ticks"]:
                img = load(os.path.join(motion_dir, f"{scene}_{mode}_tick-{t['tick']:03d}.png"))
                m = measure(bg, img, t["cell_origin_window_px"])
                per_tick.append({"tick": t["tick"], "frame": t["frame"], "planted": t["planted"],
                                 "hero_y": t["hero_logical"][1], **{k: m.get(k) for k in ("vl", "vr", "head_top_y")}})
                for leg in ("vl", "vr"):
                    if leg in t["planted"] and leg in m:
                        if leg not in cur:
                            cur[leg] = {"leg": leg, "ticks": [], "sole_y": [], "sole_x": [], "frames": []}
                        cur[leg]["ticks"].append(t["tick"])
                        cur[leg]["sole_y"].append(m[leg]["sole_y"])
                        cur[leg]["sole_x"].append(round(m[leg]["sole_x"], 2))
                        cur[leg]["frames"].append(t["frame"])
                    elif leg in cur:
                        stances.append(cur.pop(leg))
            stances += list(cur.values())
            # keep only stances fully inside the capture (not cut by the first/last tick)
            last = md["ticks"][-1]["tick"]
            full = [s for s in stances if s["ticks"][0] > 0 and s["ticks"][-1] < last]
            for s in stances:
                s["slip_y_px"] = max(s["sole_y"]) - min(s["sole_y"])
                s["slip_x_px"] = round(max(s["sole_x"]) - min(s["sole_x"]), 2)
                s["max_tick_drift_px"] = max([abs(b - a) for a, b in zip(s["sole_y"], s["sole_y"][1:])] or [0])
                s["complete"] = s in full
                s["stance_ticks"] = len(s["ticks"])
            drift = [abs(b - a) for s in full for a, b in zip(s["sole_y"], s["sole_y"][1:])]
            hy = np.array([p["head_top_y"] for p in per_tick], float)
            ideal = 2.0 * np.array([p["hero_y"] for p in per_tick])
            resid = hy - ideal
            resid -= np.median(resid)
            steps = np.diff(hy)
            nominal = float(np.mean(np.diff(ideal)))
            out[scene][mode] = {
                "stances_complete": len(full),
                "slip_y_px_per_stance": [s["slip_y_px"] for s in full],
                "slip_y_px_mean": round(float(np.mean([s["slip_y_px"] for s in full])), 3) if full else None,
                "slip_y_px_max": max([s["slip_y_px"] for s in full]) if full else None,
                "slip_x_px_max": max([s["slip_x_px"] for s in full]) if full else None,
                "per_tick_drift_px_max": max(drift) if drift else None,
                "per_tick_drift_px_mean": round(float(np.mean(drift)), 3) if drift else None,
                "planted_tick_pairs": len(drift), "planted_tick_pairs_over_1px": int(sum(d > 1 for d in drift)),
                "stance_ticks": [s["stance_ticks"] for s in full],
                "head": {"nominal_step_px_per_tick": round(nominal, 3),
                         "step_min_px": float(steps.min()), "step_max_px": float(steps.max()),
                         "residual_vs_uniform_px_max_abs": round(float(np.abs(resid).max()), 2),
                         "residual_vs_uniform_px_peak_to_peak": round(float(resid.max() - resid.min()), 2)},
                "stances": stances, "per_tick": per_tick}
    return out


def media(rec, motion_dir, run):
    made = []
    for scene, sd in rec["scenes"].items():
        for mode, md in sd["modes"].items():
            t0, t1 = md["ticks"][0], md["ticks"][-1]
            cx = t0["cell_origin_window_px"][0] + 40
            y0 = min(t["cell_origin_window_px"][1] for t in md["ticks"]) - 16
            y1 = max(t["cell_origin_window_px"][1] for t in md["ticks"]) + 112 + 16
            h = (y1 - y0 + 1) // 2 * 2
            crop = f"crop=160:{h}:{cx - 80}:{y0}"
            pat = os.path.join(motion_dir, f"{scene}_{mode}_tick-%03d.png")
            base = f"{SLUG}_{scene}_protagonist-female-south-locomotion-v2-{mode}"
            fps = int(round(1.0 / md["tick_delta_s"]))
            mp4 = os.path.join(OUT, f"{base}-motion-video-realtime-{fps}fps_m8-w02_{run}.mp4")
            ffmpeg(["-stream_loop", "2", "-framerate", str(fps), "-i", pat, "-vf", f"{crop},scale=iw*2:ih*2:flags=neighbor",
                    "-c:v", "libx264", "-crf", "12", "-pix_fmt", "yuv420p", "-movflags", "+faststart", mp4])
            gif = os.path.join(OUT, f"{base}-motion-gif-realtime-30fps_m8-w02_{run}.gif")
            ffmpeg(["-framerate", str(fps), "-i", pat, "-vf",
                    f"fps=30,{crop},scale=iw*2:ih*2:flags=neighbor,split[a][b];[a]palettegen=max_colors=256:stats_mode=full[p];[b][p]paletteuse=dither=none",
                    "-r", "30", "-loop", "0", gif])
            made += [mp4, gif]
            if mode == "run-140":
                slow = os.path.join(OUT, f"{base}-motion-video-slowmo-quarter-speed_m8-w02_{run}.mp4")
                ffmpeg(["-framerate", "15", "-i", pat, "-vf", f"{crop},scale=iw*3:ih*3:flags=neighbor",
                        "-r", "60", "-c:v", "libx264", "-crf", "12", "-pix_fmt", "yuv420p", "-movflags", "+faststart", slow])
                made.append(slow)
    # in-place loops of the cell frames (frame durations from the distance table at each alternative's speed)
    manifest = json.load(open(os.path.join(V2_DIR, rec["manifest"]), encoding="utf-8"))
    for alt, a in manifest["alternatives"].items():
        ims, durs = [], []
        for f in a["frames"]:
            im = Image.open(os.path.join(V2_DIR, f["file"])).convert("RGBA")
            bgc = Image.new("RGBA", im.size, (92, 108, 118, 255))
            bgc.alpha_composite(im)
            ims.append(bgc.convert("RGB").resize((240, 336), Image.NEAREST))
            durs.append(max(20, int(round(f["hold_px"] / a["speed_logical_px_s"] * 100)) * 10))
        gif = os.path.join(OUT, f"{SLUG}_protagonist-female_south-locomotion-v2-{alt}-in-place-loop-gif-3x_m8-w02_{run}.gif")
        ims[0].save(gif, save_all=True, append_images=ims[1:], duration=durs, loop=0, optimize=False)
        made.append(gif)
    return made


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--receipt", required=True)
    ap.add_argument("--motion-dir", required=True)
    a = ap.parse_args()
    rec = json.load(open(a.receipt, encoding="utf-8"))
    run = os.path.basename(a.receipt).rsplit("_", 1)[1][:-5]
    res = analyse(rec, a.motion_dir)
    made = media(rec, a.motion_dir, run)
    summary = {s: {m: {k: v for k, v in d.items() if k not in ("stances", "per_tick")} for m, d in md.items()}
               for s, md in res.items()}
    report = {"project": "Worlds Between", "milestone": "M8", "variant": "m8-w02",
              "purpose": "Measured planted-foot slip (from captured window pixels) and review media for female south locomotion v2.",
              "status": "technical review evidence only; unapproved", "receipt": os.path.basename(a.receipt),
              "receipt_sha256": sha(a.receipt), "units": "window px at 1280x720 (1 px = 0.5 logical px = 1 texel)",
              "summary": summary, "detail": res,
              "media": [{"file": os.path.basename(p), "sha256": sha(p)} for p in made],
              "media_note": "MP4 at 60 fps and GIF at 30 fps are real time; the slowmo-quarter MP4 is labelled slow motion for inspection only. In-place GIF durations are rounded to 10 ms (run stance 30 ms vs 25 ms exact)."}
    rp = os.path.join(OUT, f"{SLUG}_city-outskirts_protagonist-female-south-locomotion-v2-slip-and-media_m8-w02_{run}.json")
    with open(rp, "w", encoding="utf-8", newline="\n") as f:
        f.write(json.dumps(report, indent=1) + "\n")
    print(json.dumps(summary, indent=1))
    print("REPORT", rp, sha(rp))


if __name__ == "__main__":
    main()
