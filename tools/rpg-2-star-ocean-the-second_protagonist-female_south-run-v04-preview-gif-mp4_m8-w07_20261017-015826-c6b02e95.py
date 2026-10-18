"""Motion previews (GIF + MP4) for the UNAPPROVED / NONRUNTIME female SOUTH RUN motion pilot v04 (m8-w07, test-only).

v04: a copy of the v03 preview tool (tools/...south-locomotion-compact-v03-preview-gif-mp4_m8-w06_20261017-012243-65b9415a.py,
untouched) with v04 names; it also writes a 1x run loop MP4 (every 60 fps tick, 1 window px = 1 px, real time).

Reads the per-tick window crops that the v04 Godot capture tool wrote to --motion-dir (real windowed captures of the
project's 640x360 canvas in its 1280x720 window, cropped by the tool to a fixed box per sequence) and its capture receipt,
and writes SEPARATE single-view files next to the receipt (no sheets, no collages):
  * <scene> run-1x          GIF, real time, fixed window, 1 window px = 1 px, every 2nd 60 fps tick at 30/30/40 ms
  * <scene> run-follow-3x   GIF, real time, re-centred on the hero's pin (camera follows), 3x nearest
  * <scene> run-2x-60fps    MP4 (H.264 yuv420p), every captured 60 fps tick at 60 fps (real time), 2x nearest
                            (2x so chroma subsampling falls on whole window pixels)
  * <scene> stop-<stance|flight>-r<n>-1x / -quarter-2x GIF; -2x-60fps MP4: last 10 moving ticks, stop, v8, hold
  * <scene> repress-r<n>-g<k>-1x GIF; -2x-60fps MP4
GIF palettes are lossy review aids; the PNG captures are the colour-exact evidence.  Started from the v02 GIF tool
(tools/...south-locomotion-compact-v02-preview-gif_m8-w05_20261016-200500-630375df.py, not imported) [v03 note].
Usage (repository root):  python -I tools/<this> --motion-dir <abs scratch> --receipt <dir>/<capture receipt>.json
"""
import argparse, hashlib, json, os, shutil, subprocess, tempfile
from PIL import Image

REPO = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
SLUG = "rpg-2-star-ocean-the-second"
VARIANT = "unapproved-nonruntime"
STOP_CASES = {30: "stance", 36: "flight"}   # = STILL_STOP_CASES in the capture tool
REPRESS_CASES = [(16, 1), (16, 8)]
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


def save_mp4(frames, path, ffmpeg, scale=2):
    tmp = tempfile.mkdtemp(prefix="wb-run-v04-mp4-")
    try:
        for i, f in enumerate(frames):
            f2 = f.resize((f.width * scale, f.height * scale), Image.NEAREST)
            w, h = f2.width - f2.width % 2, f2.height - f2.height % 2
            f2.crop((0, 0, w, h)).save(os.path.join(tmp, f"f{i:04d}.png"))
        subprocess.run([ffmpeg, "-hide_banner", "-loglevel", "error", "-y", "-framerate", "60", "-i",
                        os.path.join(tmp, "f%04d.png"), "-c:v", "libx264", "-preset", "veryslow", "-crf", "8",
                        "-pix_fmt", "yuv420p", "-movflags", "+faststart", path], check=True)
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


def realtime(frames):
    sel = frames[::2]
    return sel, [(30, 30, 40)[i % 3] for i in range(len(sel))]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--motion-dir", required=True)
    ap.add_argument("--receipt", required=True)
    a = ap.parse_args()
    ffmpeg = shutil.which("ffmpeg")
    if not ffmpeg:
        raise SystemExit("ffmpeg not found on PATH")
    rpath = a.receipt if os.path.isabs(a.receipt) else os.path.join(REPO, a.receipt)
    with open(rpath, "rb") as f:
        rbytes = f.read()
    rec = json.loads(rbytes)
    stamp_uid = os.path.basename(rpath).rsplit("_", 1)[1].rsplit(".", 1)[0]
    out_dir = os.path.dirname(rpath)
    written = {}

    def name(scene, what, ext):
        return f"{SLUG}_{scene}_protagonist-female-south-run-v04-preview-{what}-h48_{VARIANT}_{stamp_uid}.{ext}"

    def emit(scene, what, frames, durs):
        n = name(scene, what, "gif")
        p = os.path.join(out_dir, n)
        if os.path.exists(_fs(p)):
            raise SystemExit(f"refusing to overwrite {n}")
        save_gif(frames, durs, _fs(p))
        with open(_fs(p), "rb") as f:
            written[n] = hashlib.sha256(f.read()).hexdigest()

    def emit_mp4(scene, what, frames, scale=2):
        n = name(scene, what, "mp4")
        p = os.path.join(out_dir, n)
        if os.path.exists(_fs(p)):
            raise SystemExit(f"refusing to overwrite {n}")
        save_mp4(frames, p, ffmpeg, scale)
        with open(_fs(p), "rb") as f:
            written[n] = hashlib.sha256(f.read()).hexdigest()

    def tick_files(tag, first, last):
        return [t for t in range(first, last + 1) if os.path.exists(_fs(os.path.join(a.motion_dir, f"{tag}_tick-{t:03d}.png")))]

    for scene, sr in rec["scenes"].items():
        # ------------------------------------------------ run 60 fps
        w = sr["walk"]["walk-60fps"]
        tag = f"{scene}_walk-60fps"
        cx, cy = w["crop"][0], w["crop"][1]
        ticks = [e["tick"] for e in w["ticks"]]
        frames = [load(a.motion_dir, tag, t) for t in ticks]
        f1, d1 = realtime(frames)
        emit(scene, "run-1x", f1, d1)
        emit_mp4(scene, "run-2x-60fps", frames)
        emit_mp4(scene, "run-1x-60fps", frames, 1)       # v04: 1 window px = 1 px (yuv420p rounds odd edges by cropping 1 px)
        fol = []
        for e, fr in zip(w["ticks"], frames):
            x = int(round(e["hero_logical"][0] * 2)) - cx
            y = e["pin_window_y"] - cy
            c = fr.crop((x - 50, y - 108, x + 50, y + 20))
            fol.append(c.resize((c.width * 3, c.height * 3), Image.NEAREST))
        f2, d2 = realtime(fol)
        emit(scene, "run-follow-3x", f2, d2)
        # ------------------------------------------------ stops (the two still cases)
        for n_walk, label in STOP_CASES.items():
            stag = f"{scene}_stop-60fps-{n_walk:03d}"
            st = sr["stops"].get(stag)
            if st is None:
                continue
            cx, cy = st["crop"][0], st["crop"][1]
            last = st["ticks"][-1]
            x = int(round(last["hero_logical"][0] * 2)) - cx
            y = last["pin_window_y"] - cy
            rel = st["release_tick"]
            v8_tick = rel - 1 + round(st["v8_after_ms"] * 60 / 1000)
            ts = tick_files(stag, max(0, rel - 10), v8_tick + 12)
            fr = [load(a.motion_dir, stag, t).crop((x - 70, y - 150, x + 70, y + 20)) for t in ts]
            what = f"stop-{label}-r{n_walk:03d}"
            f3, d3 = realtime(fr)
            emit(scene, what + "-1x", f3, d3)
            emit(scene, what + "-quarter-2x", [f.resize((f.width * 2, f.height * 2), Image.NEAREST) for f in fr], [70] * len(fr))
            emit_mp4(scene, what + "-2x-60fps", fr)
        # ------------------------------------------------ re-press
        for n_walk, gap in REPRESS_CASES:
            rtag = f"{scene}_repress-{n_walk:03d}-gap-{gap:02d}"
            rp = sr["repress"].get(rtag)
            if rp is None:
                continue
            ts = tick_files(rtag, 0, 400)
            if not ts:
                continue
            fr = [load(a.motion_dir, rtag, t) for t in ts]
            what = f"repress-r{n_walk:03d}-g{gap:02d}"
            f4, d4 = realtime(fr)
            emit(scene, what + "-1x", f4, d4)
            emit_mp4(scene, what + "-2x-60fps", fr)
    receipt = {"project": "Worlds Between", "milestone": "M8",
               "status": "UNAPPROVED / NONRUNTIME review aid; GIF palettes are lossy, MP4 is H.264 yuv420p at 2x nearest; "
                         "the PNG captures are the colour-exact evidence",
               "source_capture_receipt": os.path.basename(rpath),
               "source_capture_receipt_sha256_bytes": hashlib.sha256(rbytes).hexdigest(),
               "tool": "tools/" + os.path.basename(__file__), "files_sha256_bytes": written}
    rn = f"{SLUG}_city-annex_protagonist-female-south-run-v04-preview-receipt-h48_{VARIANT}_{stamp_uid}.json"
    with open(_fs(os.path.join(out_dir, rn)), "w", encoding="utf-8", newline="\n") as f:
        json.dump(receipt, f, indent=1)
        f.write("\n")
    print(f"{len(written)} previews; receipt {rn}")


if __name__ == "__main__":
    main()
