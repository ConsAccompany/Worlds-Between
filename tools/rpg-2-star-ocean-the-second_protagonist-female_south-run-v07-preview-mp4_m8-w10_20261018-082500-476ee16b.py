"""Normal-speed review MP4s for the UNAPPROVED / NONRUNTIME female SOUTH RUN motion pilot v07 (m8-w10, test-only).

A small v07 preview tool (the v06 tool, tools/...south-run-v06-preview-gif-mp4_m8-w09_20261017-211600-8ae57ec2.py, is not
imported or changed).  It writes a BOUNDED review package, every clip a separate single-view file (no sheets, no collages):
  * 4 showreels: <scene> showreel-1x-60fps / showreel-1x-30fps for city-bright and annex-dark - the FULL 1280x720 window
    at every captured frame, played at the capture frame rate (normal speed, 1 window px = 1 px): idle on v8, start,
    sustained run, quick release + re-press, reversal (runtime placeholder north walk, not pilot art), south again,
    releases to the v8 PNG
  * at most 4 worst-case clips (hero crop from the same windowed captures, real time, 2x nearest zoom so the boots read):
      1 worst-repress30-r006-g01: v06 QA defect 5 replayed (city-bright, 30 fps, late-stance release at frame 6,
        re-press 1 frame later)
      2 the city-bright (bright) 30 fps re-press, other than 1, with the largest pose change between the re-press and
        the next touchdown
      3 the 60 fps re-press with the largest pose change in the 200 ms after the re-press
      4 the annex-dark (dark) 30 fps re-press with the largest pose change between the re-press and the next touchdown
    Mixed-frame-time runs are not filmed (the receipt keeps their measured timings; a fixed-rate MP4 would misstate them).
Reads the per-frame window captures that the v07 Godot capture tool wrote to --motion-dir and its capture receipt.
MP4 is H.264 yuv420p (lossy chroma); the colour-exact evidence is the PNG captures and the receipt.
Usage (repository root):  python -I tools/<this> --motion-dir <abs scratch> --receipt outputs/<v07 capture receipt>.json
"""
import argparse, hashlib, json, os, shutil, subprocess, tempfile
from PIL import Image

REPO = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
SLUG = "rpg-2-star-ocean-the-second"
VARIANT = "unapproved-nonruntime"
DEFECT_CASE = ("city-bright", "city-bright_repress-30fps-006-gap-01")
WIN_LONG_PREFIX = "\\\\?\\"


def _fs(path):
    path = os.path.abspath(path)
    if os.name == "nt" and len(path) > 247 and not path.startswith(WIN_LONG_PREFIX):
        return WIN_LONG_PREFIX + path
    return path


def load(md, tag, t):
    return Image.open(_fs(os.path.join(md, f"{tag}_tick-{t:03d}.png"))).convert("RGB")


def frames_of(md, tag):
    ts = []
    t = 0
    while os.path.exists(_fs(os.path.join(md, f"{tag}_tick-{t:03d}.png"))):
        ts.append(t)
        t += 1
    return ts


def encode(frames, path, ffmpeg, scale, durations_s=None, fps=None):
    tmp = tempfile.mkdtemp(prefix="wb-run-v07-mp4-")
    try:
        names = []
        for i, f in enumerate(frames):
            f2 = f.resize((f.width * scale, f.height * scale), Image.NEAREST) if scale != 1 else f
            w, h = f2.width - f2.width % 2, f2.height - f2.height % 2
            n = os.path.join(tmp, f"f{i:04d}.png")
            f2.crop((0, 0, w, h)).save(n)
            names.append(n)
        enc = ["-c:v", "libx264", "-preset", "veryslow", "-crf", "8", "-pix_fmt", "yuv420p", "-movflags", "+faststart"]
        if durations_s is None:
            cmd = [ffmpeg, "-hide_banner", "-loglevel", "error", "-y", "-framerate", str(fps), "-i", os.path.join(tmp, "f%04d.png")] + enc + [path]
        else:
            # variable frame rate: the concat demuxer with each frame's real duration (the last entry repeated, per ffmpeg)
            lst = os.path.join(tmp, "list.txt")
            with open(lst, "w", encoding="utf-8", newline="\n") as fh:
                for n, d in zip(names, durations_s):
                    fh.write(f"file '{n.replace(os.sep, '/')}'\nduration {d:.6f}\n")
                fh.write(f"file '{names[-1].replace(os.sep, '/')}'\n")
            cmd = [ffmpeg, "-hide_banner", "-loglevel", "error", "-y", "-f", "concat", "-safe", "0", "-i", lst,
                   "-fps_mode", "vfr"] + enc + [path]
        subprocess.run(cmd, check=True)
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


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
    if rec["quick_debug_run"]:
        raise SystemExit("refusing a quick / single-scene debug receipt")
    stamp_uid = os.path.basename(rpath).rsplit("_", 1)[1].rsplit(".", 1)[0]
    out_dir = os.path.dirname(rpath)
    written = {}
    chosen = {}

    def emit(scene, what, frames, scale, fps=None, durations_s=None, why=""):
        n = f"{SLUG}_{scene}_protagonist-female-south-run-v07-preview-{what}-h48_{VARIANT}_{stamp_uid}.mp4"
        p = os.path.join(out_dir, n)
        if os.path.exists(_fs(p)):
            raise SystemExit(f"refusing to overwrite {n}")
        encode(frames, p, ffmpeg, scale, durations_s, fps)
        with open(_fs(p), "rb") as f:
            written[n] = hashlib.sha256(f.read()).hexdigest()
        chosen[n] = why

    # ---------------------------------------------------------------- 4 normal-speed showreels (full window, 1x)
    for scene, sr in rec["scenes"].items():
        for fps in (60, 30):
            reel = sr[f"showreel_{fps}fps"]
            frames = [load(a.motion_dir, reel["frames_dir_tag"], f["tick"]) for f in reel["frames"]]
            emit(scene, f"showreel-1x-{fps}fps", frames, 1, fps=fps,
                 why=f"normal-speed showreel, {reel['ticks']} frames at {fps} fps, full 1280x720 window")

    # ---------------------------------------------------------------- worst-case clips (<= 4)
    def crop_clip(scene, tag, first=0, last=10 ** 6):
        ts = [t for t in frames_of(a.motion_dir, tag) if first <= t <= last]
        if not ts:
            raise SystemExit(f"no saved frames for {tag}")
        return [load(a.motion_dir, tag, t) for t in ts], ts

    # 1: the v06 defect case
    sc, tag = DEFECT_CASE
    r1 = rec["scenes"][sc]["repress"][tag]
    fr, _ = crop_clip(sc, tag)
    emit(sc, "worst-repress30-r006-g01-2x-30fps", fr, 2, fps=30,
         why=f"v06 QA defect 5 replayed: {tag}; handoff pose change max {r1['handoff_cell_xor_max']} px, 200 ms max "
             f"{r1['repress_200ms_cell_xor_max']} px (steady {r1['steady_run_cell_xor_max_same_fps']}); rise faults {len(r1['rise_faults'])}")
    # 2 (city-bright) and 4 (annex-dark): worst 30 fps re-press handoff per scene, other than 1
    for scene in ("city-bright", "annex-dark"):
        cands = [(e["handoff_cell_xor_max"], e["repress_200ms_cell_xor_max"], t) for t, e in rec["scenes"][scene]["repress"].items()
                 if e["fps"] == 30 and t != DEFECT_CASE[1] and frames_of(a.motion_dir, t)]
        h2, x2, t2 = max(cands)
        fr, _ = crop_clip(scene, t2)
        e2 = rec["scenes"][scene]["repress"][t2]
        emit(scene, f"worst-repress30-r{e2['release_tick'] - 1:03d}-g{e2['gap_ticks']:02d}-2x-30fps", fr, 2, fps=30,
             why=f"largest 30 fps handoff pose change in {scene}: {t2}; handoff {h2} px, 200 ms max {x2} px (steady {e2['steady_run_cell_xor_max_same_fps']})")
    # 3: worst 60 fps re-press, 200 ms window
    cands = [(e["repress_200ms_cell_xor_max"], e["handoff_cell_xor_max"], s, t) for s, sr in rec["scenes"].items()
             for t, e in sr["repress"].items() if e["fps"] == 60 and frames_of(a.motion_dir, t)]
    x3, h3, s3, t3 = max(cands)
    fr, _ = crop_clip(s3, t3)
    e3 = rec["scenes"][s3]["repress"][t3]
    emit(s3, f"worst-repress60-r{e3['release_tick'] - 1:03d}-g{e3['gap_ticks']:02d}-2x-60fps", fr, 2, fps=60,
         why=f"largest 60 fps pose change within 200 ms of a re-press: {t3}; 200 ms max {x3} px, handoff {h3} px (steady {e3['steady_run_cell_xor_max_same_fps']})")
    receipt = {"project": "Worlds Between", "milestone": "M8",
               "status": "UNAPPROVED / NONRUNTIME review aid; MP4 is H.264 yuv420p (lossy chroma); showreels 1 window px per px at the "
                         "capture frame rate; worst-case clips are hero crops at 2x nearest, real time; the PNG captures and the "
                         "capture receipt are the exact evidence; runtime-north showreel segments show the runtime placeholder, not the pilot",
               "source_capture_receipt": os.path.basename(rpath),
               "source_capture_receipt_sha256_bytes": hashlib.sha256(rbytes).hexdigest(),
               "tool": "tools/" + os.path.basename(__file__), "files_sha256_bytes": written, "selection": chosen}
    rn = f"{SLUG}_city-annex_protagonist-female-south-run-v07-preview-receipt-h48_{VARIANT}_{stamp_uid}.json"
    with open(_fs(os.path.join(out_dir, rn)), "w", encoding="utf-8", newline="\n") as f:
        json.dump(receipt, f, indent=1)
        f.write("\n")
    for n, why in chosen.items():
        print(n, "<-", why)
    print(f"{len(written)} MP4s; receipt {rn}")


if __name__ == "__main__":
    main()
