"""Animation previews (GIF) for the UNAPPROVED / NONRUNTIME female south compact locomotion pilot v02 (m8-w05).

Reads the per-tick window crops that the v02 Godot capture tool wrote to --motion-dir (real 1280x720 windowed captures,
cropped by the tool to a fixed box per sequence) and its capture receipt, and writes SEPARATE single-view GIFs to outputs/
(no sheets, no collages):
  * <scene> walk-60fps-realtime-1x      fixed window, every 2nd 60 fps tick at 30/30/40 ms (mean 33.3 ms = 2 ticks)
  * <scene> walk-60fps-quarter-speed-2x every tick at 70 ms (~1/4 speed), 2x nearest
  * <scene> walk-60fps-follow-3x        re-centred on the hero's pin (camera follows), 3x, realtime
  * <scene> stop-r<release tick>-phase-<px>-realtime-1x   every 60 fps stop case: last 10 moving ticks, stop, v8
  * <scene> stop-...-quarter-speed-2x   the two stop cases also saved as full stills
  * <scene> repress-...-realtime-1x     re-press cases whose ticks were saved
GIF palettes are lossy review aids; the PNG captures are the colour-exact evidence.
Usage (repository root):  python -I tools/<this> --motion-dir <abs scratch> --receipt outputs/<capture receipt>.json
"""
import argparse, hashlib, json, os
from PIL import Image

REPO = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
SLUG = "rpg-2-star-ocean-the-second"
VARIANT = "m8-w05"
QUARTER_STOPS = (30, 36)      # = STILL_STOP_CASES in the capture tool
WIN_LONG_PREFIX = "\\\\?\\"   # the four characters  \\?\  (scratch dirs + these names can pass MAX_PATH)


def _fs(path):
    path = os.path.abspath(path)
    if os.name == "nt" and len(path) > 247 and not path.startswith(WIN_LONG_PREFIX):
        return WIN_LONG_PREFIX + path
    return path


def load(md, tag, t):
    return Image.open(_fs(os.path.join(md, f"{tag}_tick-{t:03d}.png"))).convert("RGB")


def save_gif(frames, durations, path):
    pal = [f.quantize(colors=255, method=Image.Quantize.MEDIANCUT, dither=Image.Dither.NONE) for f in frames]
    pal[0].save(path, save_all=True, append_images=pal[1:], duration=durations, loop=0, disposal=1, optimize=False)


def realtime(frames):
    sel = frames[::2]
    return sel, [(30, 30, 40)[i % 3] for i in range(len(sel))]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--motion-dir", required=True)
    ap.add_argument("--receipt", required=True)
    a = ap.parse_args()
    rpath = a.receipt if os.path.isabs(a.receipt) else os.path.join(REPO, a.receipt)
    with open(rpath, "rb") as f:
        rbytes = f.read()
    rec = json.loads(rbytes)
    stamp_uid = os.path.basename(rpath).rsplit("_", 1)[1].rsplit(".", 1)[0]
    out_dir = os.path.dirname(rpath)
    written = {}

    def emit(scene, what, frames, durs):
        n = f"{SLUG}_{scene}_protagonist-female-south-locomotion-compact-v02-preview-{what}-h48_{VARIANT}_{stamp_uid}.gif"
        p = os.path.join(out_dir, n)
        if os.path.exists(_fs(p)):
            raise SystemExit(f"refusing to overwrite {n}")
        save_gif(frames, durs, _fs(p))
        with open(_fs(p), "rb") as f:
            written[n] = hashlib.sha256(f.read()).hexdigest()

    def tick_files(tag, first, last):
        return [t for t in range(first, last + 1) if os.path.exists(_fs(os.path.join(a.motion_dir, f"{tag}_tick-{t:03d}.png")))]

    for scene, sr in rec["scenes"].items():
        # ------------------------------------------------ walk 60 fps
        w = sr["walk"]["walk-60fps"]
        tag = f"{scene}_walk-60fps"
        cx, cy = w["crop"][0], w["crop"][1]
        ticks = [e["tick"] for e in w["ticks"]]
        frames = [load(a.motion_dir, tag, t) for t in ticks]
        f1, d1 = realtime(frames)
        emit(scene, "walk-60fps-realtime-1x", f1, d1)
        emit(scene, "walk-60fps-quarter-speed-2x", [f.resize((f.width * 2, f.height * 2), Image.NEAREST) for f in frames],
             [70] * len(frames))
        fol = []
        for e, fr in zip(w["ticks"], frames):
            x = int(round(e["hero_logical"][0] * 2)) - cx
            y = e["pin_window_y"] - cy
            c = fr.crop((x - 50, y - 108, x + 50, y + 20))
            fol.append(c.resize((c.width * 3, c.height * 3), Image.NEAREST))
        f2, d2 = realtime(fol)
        emit(scene, "walk-60fps-follow-3x-realtime", f2, d2)
        # ------------------------------------------------ stops (60 fps cases carry motion crops)
        for tag, st in sr["stops"].items():
            if st["fps"] != 60:
                continue
            cx, cy = st["crop"][0], st["crop"][1]
            last = st["ticks"][-1]
            x = int(round(last["hero_logical"][0] * 2)) - cx
            y = last["pin_window_y"] - cy
            rel = st["release_tick"]
            v8_tick = rel - 1 + round(st["v8_after_ms"] * 60 / 1000)
            ts = tick_files(tag, max(0, rel - 10), v8_tick + 6)
            fr = [load(a.motion_dir, tag, t).crop((x - 70, y - 150, x + 70, y + 20)) for t in ts]
            n_walk = rel - 1
            what = f"stop-r{n_walk:03d}-ph{st['released_at_phase_px']:02d}"
            f3, d3 = realtime(fr)
            emit(scene, what + "-realtime-1x", f3, d3)
            if n_walk in QUARTER_STOPS:
                emit(scene, what + "-quarter-2x", [f.resize((f.width * 2, f.height * 2), Image.NEAREST) for f in fr],
                     [70] * len(fr))
        # ------------------------------------------------ re-press
        for tag, rp in sr["repress"].items():
            ts = tick_files(tag, 0, 400)
            if not ts:
                continue
            fr = [load(a.motion_dir, tag, t) for t in ts]
            what = f"repress-r{rp['release_tick'] - 1:03d}-gap-{rp['gap_ticks']:02d}"
            f4, d4 = realtime(fr)
            emit(scene, what + "-realtime-1x", f4, d4)
    receipt = {"project": "Worlds Between", "milestone": "M8",
               "status": "UNAPPROVED / NONRUNTIME review aid; GIF palettes are lossy, PNG captures are colour-exact",
               "source_capture_receipt": os.path.relpath(rpath, REPO).replace("\\", "/"),
               "source_capture_receipt_sha256_bytes": hashlib.sha256(rbytes).hexdigest(),
               "tool": "tools/" + os.path.basename(__file__), "gifs_sha256_bytes": written}
    rn = f"{SLUG}_city-outskirts-annex_protagonist-female-south-locomotion-compact-v02-preview-gif-receipt-h48_{VARIANT}_{stamp_uid}.json"
    with open(_fs(os.path.join(out_dir, rn)), "w", encoding="utf-8", newline="\n") as f:
        json.dump(receipt, f, indent=1)
        f.write("\n")
    print(f"{len(written)} GIFs; receipt {rn}")


if __name__ == "__main__":
    main()
