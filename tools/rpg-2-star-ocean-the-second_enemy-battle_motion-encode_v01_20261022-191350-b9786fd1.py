"""Encode enemy battle actual-motion captures into separate native 640x360 MP4 clips at normal 1x speed.

Uses only the capture report's actual frame timestamps and frame files (each PNG is shown for its measured
wall interval through an ffconcat list; no duplication, dropping, interpolation, scaling or collage). A median final hold is requested; the MP4 muxer may shorten only that final still hold. ffmpeg must already be on PATH (shutil.which). Refuses to overwrite.

Usage: python -I <this file> --report <capture report json> --output-dir <dir> [--tag <tag>]
"""
import argparse
import hashlib
import json
import re
import shutil
import statistics
import subprocess
import sys
from pathlib import Path

PROJECT = "rpg-2-star-ocean-the-second"
DEFAULT_TAG = "actual-motion-v01_20261022-191350-b9786fd1"


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1 << 20), b""):
            digest.update(block)
    return digest.hexdigest()


def ffconcat_path(path: Path) -> str:
    return path.resolve().as_posix().replace("'", "'\\''")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--report", required=True)
    parser.add_argument("--output-dir", required=True)
    parser.add_argument("--tag", default=DEFAULT_TAG)
    args = parser.parse_args()
    if not re.fullmatch(r"[a-z0-9][a-z0-9._-]*", args.tag):
        print("ENEMY49_ENCODE_FAIL tag must be lowercase [a-z0-9._-]")
        return 1
    ffmpeg = shutil.which("ffmpeg")
    ffprobe = shutil.which("ffprobe")
    if ffmpeg is None:
        print("ENEMY49_ENCODE_FAIL ffmpeg not on PATH")
        return 1
    report_path = Path(args.report)
    report = json.loads(report_path.read_text(encoding="utf-8"))
    capture_root = report_path.parent
    out_dir = Path(args.output_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    manifest_path = out_dir / f"{PROJECT}_enemy-battle_motion-encode-manifest_{args.tag}.json"
    if manifest_path.exists():
        print(f"ENEMY49_ENCODE_FAIL manifest exists, refusing to overwrite: {manifest_path}")
        return 1
    failures = []
    outputs = []
    for clip in report.get("clips", []):
        name = clip["name"]
        rows = clip.get("rows", [])
        if len(rows) < 2:
            failures.append(f"{name}: fewer than 2 frames")
            continue
        times = [float(row["t"]) for row in rows]
        deltas = [b - a for a, b in zip(times, times[1:])]
        if min(deltas) <= 0.0:
            failures.append(f"{name}: non-monotonic timestamps")
            continue
        durations = deltas + [statistics.median(deltas)]
        frame_paths = []
        for row in rows:
            frame = capture_root / row["file"]
            if not frame.is_file():
                failures.append(f"{name}: missing frame {frame}")
                break
            if sha256(frame) != row["sha256"]:
                failures.append(f"{name}: frame hash mismatch {frame}")
                break
            frame_paths.append(frame)
        if len(frame_paths) != len(rows):
            continue
        enemy, language = clip["enemy"], clip["language"]
        mp4 = out_dir / f"{PROJECT}_{enemy}_{language}-clip-normal-1x_{args.tag}.mp4"
        concat = out_dir / f"{PROJECT}_{enemy}_{language}-clip-ffconcat_{args.tag}.txt"
        if mp4.exists() or concat.exists():
            failures.append(f"{name}: output exists, refusing to overwrite: {mp4}")
            continue
        lines = ["ffconcat version 1.0"]
        for frame, duration in zip(frame_paths, durations):
            lines.append(f"file '{ffconcat_path(frame)}'")
            lines.append("option framerate 1000000")
            lines.append(f"duration {duration:.6f}")
        concat.write_text("\n".join(lines) + "\n", encoding="utf-8", newline="\n")
        command = [ffmpeg, "-hide_banner", "-loglevel", "error", "-n", "-f", "concat", "-safe", "0", "-i", str(concat),
                   "-fps_mode", "passthrough", "-video_track_timescale", "1000000",
                   "-enc_time_base", "1:1000000", "-c:v", "libx264", "-bf", "0", "-preset", "slow", "-crf", "12", "-pix_fmt", "yuv420p", "-an", str(mp4)]
        result = subprocess.run(command, capture_output=True, text=True, encoding="utf-8", errors="replace")
        if result.returncode != 0 or not mp4.is_file():
            failures.append(f"{name}: ffmpeg exit {result.returncode}: {result.stderr.strip()[:400]}")
            continue
        probe = {}
        if ffprobe is not None:
            probe_run = subprocess.run([ffprobe, "-v", "error", "-select_streams", "v:0", "-count_frames", "-show_entries",
                                        "stream=width,height,nb_read_frames,duration", "-of", "json", str(mp4)],
                                       capture_output=True, text=True, encoding="utf-8", errors="replace")
            if probe_run.returncode == 0:
                probe = json.loads(probe_run.stdout)["streams"][0]
                if (int(probe.get("width", 0)), int(probe.get("height", 0))) != (640, 360):
                    failures.append(f"{name}: encoded size {probe.get('width')}x{probe.get('height')}")
                if int(probe.get("nb_read_frames", -1)) != len(rows):
                    failures.append(f"{name}: encoded frames {probe.get('nb_read_frames')} != captured {len(rows)}")
            else:
                failures.append(f"{name}: ffprobe exit {probe_run.returncode}")
        outputs.append({"clip": name, "mp4": mp4.name, "mp4Sha256": sha256(mp4), "ffconcat": concat.name,
                        "frames": len(rows), "capturedSeconds": round(times[-1] - times[0] + durations[-1], 6),
                        "lastFrameDurationRule": "median interval requested; verify actual stream duration because the muxer can shorten the final still hold", "ffprobe": probe})
    manifest = {"project": PROJECT, "tag": args.tag, "report": report_path.name, "reportSha256": sha256(report_path),
                "speed": "normal 1x from captured wall timestamps", "scaling": "none (native 640x360)",
                "codec": "libx264 crf12 yuv420p bf0, microsecond encoder timebase, VFR passthrough", "outputs": outputs, "failures": failures}
    manifest_path.write_text(json.dumps(manifest, indent=1, ensure_ascii=False) + "\n", encoding="utf-8", newline="\n")
    print(f"ENEMY49_ENCODE_MANIFEST {manifest_path}")
    if failures:
        for failure in failures:
            print("FAIL " + failure)
        print(f"ENEMY49_ENCODE_FAIL count={len(failures)}")
        return 1
    print(f"ENEMY49_ENCODE_OK clips={len(outputs)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
