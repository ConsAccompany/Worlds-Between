"""Female south walk pilot w01 - review media + foot-slip measurement (M8).

Inputs: the Godot capture receipt (outputs/...walk-pilot-capture-receipt_m8-w01_<run>.json), its
per-scene stills in outputs/, and the per-tick motion captures the harness wrote to --motion-dir
(scratch, outside the repo).  Outputs (into outputs/, one file per review item, no collages):
  - per scene: a motion MP4 (H.264, 60 fps, 2x nearest crop around the walk path, played 3 times)
    and a motion GIF (every 3rd tick at 20 fps = real time, 2x nearest);
  - city: an in-place loop GIF of the 8 frame stills (3x nearest crop, 10 fps);
  - one slip/metrics JSON.
GIF/MP4 are lossy review aids; the PNG stills are the colour-exact evidence.
Requires ffmpeg on PATH.  Usage (repo root):
  python -I tools/<this> --receipt <receipt json> --motion-dir <scratch dir>
"""
import argparse, hashlib, json, os, subprocess, sys, tempfile

REPO = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
OUT = os.path.join(REPO, "outputs")
PIN_Y = 104
# Sole row of each leg per frame, measured by the build tool's --check on the frame PNGs.
SOLES = {"f01-contact-vr": {"vl": 99, "vr": 104}, "f02-down-vr": {"vl": 98, "vr": 103},
         "f03-passing-vr": {"vl": 99, "vr": 103}, "f04-up-vr": {"vl": 103, "vr": 102},
         "f05-contact-vl": {"vl": 104, "vr": 98}, "f06-down-vl": {"vl": 103, "vr": 98},
         "f07-passing-vl": {"vl": 103, "vr": 99}, "f08-up-vl": {"vl": 102, "vr": 103}}


def sha(path):
    with open(path, "rb") as f:
        return hashlib.sha256(f.read()).hexdigest()


def ffmpeg(args):
    subprocess.run(["ffmpeg", "-hide_banner", "-loglevel", "error", "-y"] + args, check=True)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--receipt", required=True)
    ap.add_argument("--motion-dir", required=True)
    a = ap.parse_args()
    rec = json.load(open(a.receipt, encoding="utf-8"))
    run = os.path.basename(a.receipt).rsplit("_", 1)[1][:-5]          # <stamp>-<uid>
    made, slip = [], {}
    for scene, sd in rec["scenes"].items():
        wx = int(sd["pin_x_logical"] * 2)
        gy = int(sd["ground_y_logical"] * 2)
        crop = f"crop=180:340:{max(wx - 90, 0)}:{gy - 80 - 120}"     # covers the 96 px south walk + figure height
        mp4 = os.path.join(OUT, f"rpg-2-star-ocean-the-second_{scene}_protagonist-female-south-walk-pilot-motion-video_m8-w01_{run}.mp4")
        ffmpeg(["-stream_loop", "2", "-framerate", "60", "-i", os.path.join(a.motion_dir, f"{scene}_tick-%03d.png"),
                "-vf", f"{crop},scale=iw*2:ih*2:flags=neighbor", "-c:v", "libx264", "-crf", "12", "-pix_fmt", "yuv420p",
                "-movflags", "+faststart", mp4])
        gif = os.path.join(OUT, f"rpg-2-star-ocean-the-second_{scene}_protagonist-female-south-walk-pilot-motion-gif_m8-w01_{run}.gif")
        ffmpeg(["-framerate", "60", "-i", os.path.join(a.motion_dir, f"{scene}_tick-%03d.png"),
                "-vf", f"select='not(mod(n\\,3))',setpts=N/20/TB,{crop},scale=iw*2:ih*2:flags=neighbor,split[a][b];[a]palettegen=max_colors=256:stats_mode=full[p];[b][p]paletteuse=dither=none",
                "-r", "20", "-loop", "0", gif])
        made += [mp4, gif]
        # foot slip: screen y of the declared stance foot's sole = 2*pin_y + (sole_row - PIN_Y)
        ticks = sd["motion_ticks"]
        ys = [2 * t["pin_logical"][1] + SOLES[t["frame"]][t["stance_leg"]] - PIN_Y for t in ticks]
        drift, held, changed = [], 0, 0
        for i in range(1, len(ticks)):
            if ticks[i]["stance_leg"] != ticks[i - 1]["stance_leg"]:
                continue
            d = abs(ys[i] - ys[i - 1])
            drift.append(d)
            if ticks[i]["frame"] == ticks[i - 1]["frame"]:
                held += 1
            else:
                changed += 1
        stances, cur = [], [0]
        for i in range(1, len(ticks)):
            if ticks[i]["stance_leg"] == ticks[i - 1]["stance_leg"]:
                cur.append(i)
            else:
                stances.append(cur); cur = [i]
        stances.append(cur)
        per_stance = [{"leg": ticks[s[0]]["stance_leg"], "ticks": len(s), "body_travel_screen_px": 2 * (ticks[s[-1]]["pin_logical"][1] - ticks[s[0]]["pin_logical"][1]),
                       "stance_foot_screen_slip_px": ys[s[-1]] - ys[s[0]]} for s in stances if len(s) > 1]
        slip[scene] = {"compared_ticks": len(drift), "held_frame_ticks": held, "frame_change_ticks": changed,
                       "max_px_per_tick": max(drift), "mean_px_per_tick": round(sum(drift) / len(drift), 3),
                       "ticks_over_1px": sum(1 for d in drift if d > 1), "per_stance": per_stance}
    # in-place loop GIF from the city stills (frame order f01..f08)
    city = rec["scenes"]["city-bright"]
    wx, gy = int(city["pin_x_logical"] * 2), int(city["ground_y_logical"] * 2)
    stills = [s for s in city["stills"] if s["frame"].startswith("f0")]
    with tempfile.TemporaryDirectory() as td:
        for i, s in enumerate(stills):
            ffmpeg(["-i", os.path.join(OUT, s["capture"]), "-vf", f"crop=120:124:{wx - 60}:{gy - 112},scale=iw*3:ih*3:flags=neighbor",
                    os.path.join(td, f"loop-{i:02d}.png")])
        loop = os.path.join(OUT, f"rpg-2-star-ocean-the-second_city-bright_protagonist-female-south-walk-pilot-in-place-loop-gif_m8-w01_{run}.gif")
        ffmpeg(["-stream_loop", "0", "-framerate", "10", "-i", os.path.join(td, "loop-%02d.png"),
                "-vf", "split[a][b];[a]palettegen=max_colors=256:stats_mode=full[p];[b][p]paletteuse=dither=none", "-loop", "0", loop])
        made.append(loop)
    metrics = {"project": "Worlds Between", "milestone": "M8", "variant": "m8-w01", "receipt": os.path.basename(a.receipt),
               "receipt_sha256": sha(a.receipt),
               "slip_definition": "screen y of the declared stance foot's lowest opaque row; per-tick drift compared only between ticks with the same stance leg (E8 style, 1 screen px threshold); body moves 2 screen px per tick",
               "slip": slip,
               "media": [{"file": os.path.basename(p), "sha256": sha(p), "bytes": os.path.getsize(p)} for p in made],
               "media_note": "GIF (palette) and MP4 (H.264 yuv420p) are lossy review aids; colour-exact evidence is the PNG stills"}
    mpath = os.path.join(OUT, f"rpg-2-star-ocean-the-second_city-outskirts_protagonist-female-south-walk-pilot-slip-and-media_m8-w01_{run}.json")
    with open(mpath, "w", encoding="utf-8") as f:
        f.write(json.dumps(metrics, indent=1) + "\n")
    print(json.dumps(slip, indent=1))
    for p in made + [mpath]:
        print("WROTE", os.path.basename(p))


if __name__ == "__main__":
    main()
