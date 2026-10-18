"""Female SOUTH RUN v10r1 (bounded amendment of v10): encode the real-Godot normal-speed showreels and export the critical frames (UNAPPROVED /
NONRUNTIME review evidence).

Input: the lossless 1280x720 PNG window frames the v10 capture tool wrote (one per tick, --motion-dir) and its capture
receipt (derived from the v10 tool, which is preserved unchanged).  The reels use the same input sequence as the v07 / v09 / v10 reels (REEL_SEGS in the v09 tool, inherited unchanged):
idle -> start + sustained run -> quick release (3 @60) + re-press -> reversal to north (runtime placeholder sprite) ->
south -> stop -> short run -> stop.  Output, one separate file each (no collage, no side-by-side):
  * 1x normal-speed MP4s of the full native window (1280x720 = the 640x360 logical canvas at 2x): city-bright at 30 fps,
    annex-dark at 60 fps;
  * a few critical frames of each reel as separate full-window PNGs, byte copies of the lossless captures (heel strike,
    flight, re-press touchdown, stop release, stop touchdown, first v8 frame), each labelled with its tick, scene, fps
    and the native-window-of-logical-canvas size;
  * a receipt (sha256-bytes, frame counts, the segment marks, the chosen ticks with their gait states, encode settings).
Encode: ffmpeg libx264 -crf 12 -preset slow -pix_fmt yuv420p; frame count of every MP4 == captured ticks (ffprobe).

Usage (repository root):
  python -I -B tools/<this file> --frames <dir> --receipt <json> --out-dir outputs
"""
import argparse, hashlib, json, os, shutil, subprocess, tempfile

from PIL import Image

SLUG = "rpg-2-star-ocean-the-second"
STAMP = "20261018-142136"
RUN_ID = "249dbf66"
REELS = (("city-bright", 30), ("annex-dark", 60))
PATH_LIMIT = 250
WINDOW_LABEL = "win1280-of-640"   # native 1280x720 window of the 640x360 logical canvas


def _fs(p):
    p = os.path.abspath(p)
    return "\\\\?\\" + p if os.name == "nt" and len(p) > 247 and not p.startswith("\\\\?\\") else p


def fid(role):
    return hashlib.sha256(f"{RUN_ID}:{role}".encode()).hexdigest()[:8]


def sha(path):
    with open(_fs(path), "rb") as f:
        return hashlib.sha256(f.read()).hexdigest()


def frames_of(d, tag, n):
    out = [os.path.join(d, "%s_tick-%03d.png" % (tag, t)) for t in range(n)]
    missing = [p for p in out if not os.path.exists(p)]
    if missing:
        raise SystemExit(f"{len(missing)} frames missing for {tag}, e.g. {missing[0]}")
    return out


def encode(pngs, fps, out_path):
    tmp = tempfile.mkdtemp(prefix="wb-v10r1mp4-")
    try:
        for i, p in enumerate(pngs):
            Image.open(p).convert("RGB").save(os.path.join(tmp, "f%04d.png" % i))
        r = subprocess.run(["ffmpeg", "-v", "error", "-y", "-framerate", str(fps), "-i", os.path.join(tmp, "f%04d.png"),
                            "-c:v", "libx264", "-preset", "slow", "-crf", "12", "-pix_fmt", "yuv420p",
                            "-movflags", "+faststart", "-r", str(fps), os.path.join(tmp, "o.mp4")], capture_output=True, text=True)
        if r.returncode != 0:
            raise SystemExit(r.stderr)
        shutil.move(os.path.join(tmp, "o.mp4"), _fs(out_path))
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
    pr = subprocess.run(["ffprobe", "-v", "error", "-count_frames", "-select_streams", "v:0", "-show_entries",
                         "stream=nb_read_frames,width,height,r_frame_rate", "-of", "json", _fs(out_path)],
                        capture_output=True, text=True)
    st = json.loads(pr.stdout)["streams"][0]
    if int(st["nb_read_frames"]) != len(pngs):
        raise SystemExit(f"{out_path}: {st['nb_read_frames']} frames != {len(pngs)}")
    return st


def lands(fr):
    return [e for e in fr.get("events", []) if e and e[0] == "land"]


def critical_ticks(reel):
    """label -> tick, from the receipt's segment marks and per-tick gait events (no pixel heuristics)."""
    fr = reel["frames"]
    seg = reel["segments"]          # [name, first tick, ticks]
    run1, quick, rep, stop = seg[1][1], seg[2][1], seg[3][1], seg[6][1]
    out = {"start-idle": run1 - 1}
    out["start-step"] = next(i for i in range(run1, len(fr)) if any(fr[i]["modes"][s] != "contact" for s in ("vl", "vr")))
    lt = [i for i in range(run1, quick) if lands(fr[i])]
    out["strike"] = lt[1] if len(lt) > 1 else lt[0]
    out["midstance"] = next(i for i in range(out["strike"], quick) if fr[i]["state"]["bob"] == 2)
    out["flight"] = next(i for i in range(out["strike"], quick) if all(fr[i]["modes"][s] == "swing" for s in ("vl", "vr")))
    out["quick-release"] = quick
    out["repress-step"] = rep
    out["repress-land"] = next(i for i in range(rep, len(fr)) if lands(fr[i]))
    out["stop-release"] = stop
    v8 = next(i for i in range(stop, len(fr)) if fr[i]["show_v8"])
    td = [i for i in range(stop, v8 + 1) if lands(fr[i])]
    out["stop-land"] = td[-1] if td else stop
    out["stop-v8"] = v8
    keep = ("strike", "flight", "repress-land", "stop-release", "stop-land", "stop-v8")
    return {k: v for k, v in out.items() if k in keep}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--frames", required=True)
    ap.add_argument("--receipt", required=True)
    ap.add_argument("--out-dir", required=True)
    a = ap.parse_args()
    rec = json.load(open(_fs(a.receipt), encoding="utf-8"))
    if rec["art"] != "v10r1":
        raise SystemExit("not a v10r1 capture receipt")
    os.makedirs(_fs(a.out_dir), exist_ok=True)
    outputs, frames_out = {}, {}
    for scene, fps in REELS:
        reel = rec["scenes"][scene]["showreel"]
        if int(reel["fps"]) != fps:
            raise SystemExit(f"{scene} reel fps {reel['fps']} != {fps}")
        pngs = frames_of(a.frames, reel["tag"], int(reel["ticks"]))
        name = f"{SLUG}_{scene}_female-south-run-v10r1-showreel-1x-{WINDOW_LABEL}-{fps}fps-h48_unapproved_{STAMP}-{fid(scene + 'reel')}.mp4"
        path = os.path.join(a.out_dir, name)
        if len(os.path.abspath(path)) > PATH_LIMIT:
            raise SystemExit(f"path too long: {path}")
        st = encode(pngs, fps, path)
        outputs[name] = {"scene": scene, "fps": fps, "kind": "showreel-1x-normal-speed", "frames": len(pngs),
                         "width": st["width"], "height": st["height"], "native_window": [1280, 720], "logical_canvas": [640, 360],
                         "sha256_bytes": sha(path), "capture_tag": reel["tag"], "segments": reel["segments"],
                         "releases": reel["releases"]}
        print("MP4", name, st["width"], st["height"], len(pngs))
        for label, t in critical_ticks(reel).items():
            fname = (f"{SLUG}_{scene}_female-south-run-v10r1-{label}-t{t:03d}-{WINDOW_LABEL}-{fps}fps-h48_unapproved_"
                     f"{STAMP}-{fid(scene + label)}.png")
            dst = os.path.join(a.out_dir, fname)
            if len(os.path.abspath(dst)) > PATH_LIMIT:
                raise SystemExit(f"path too long ({len(os.path.abspath(dst))}): {fname}")
            with Image.open(pngs[t]) as im:
                if im.size != (1280, 720):
                    raise SystemExit(f"{pngs[t]} is {im.size}, not the 1280x720 window")
            shutil.copyfile(pngs[t], _fs(dst))
            f = reel["frames"][t]
            frames_out[fname] = {"scene": scene, "fps": fps, "label": label, "tick": t, "ms_since_reel_start": round(1000.0 * t / fps, 1),
                                 "native_window": [1280, 720], "logical_canvas": [640, 360], "sha256_bytes": sha(dst),
                                 "input": f["input"], "show_v8": f["show_v8"], "modes": f.get("modes"), "state": f.get("state"),
                                 "events": f.get("events")}
            print("PNG", fname)
    receipt = {"purpose": "normal-speed review MP4s and separate critical-frame PNGs of the female SOUTH RUN v10r1 (real Godot, "
                          "native 1280x720 window of the 640x360 logical canvas, gameplay 48 logical px); UNAPPROVED / NONRUNTIME",
               "art_approved": False, "human_reviewed": False, "runtime_integrated": False,
               "same_input_as": "v07 / v09 / v10 reels (REEL_SEGS of the v09 capture tool, inherited unchanged); compare with "
                                "outputs/*female-south-run-v10-showreel-1x-* (20261018-143213) and v0[79] (20261018-133700)",
               "encode": "ffmpeg libx264 -preset slow -crf 12 -pix_fmt yuv420p from lossless 1280x720 PNG window captures; "
                         "every MP4 frame count == captured ticks (ffprobe -count_frames); critical PNGs are byte copies",
               "segments_note": "segments: [name, first tick, ticks] at 60 fps units x fps/60: idle, start + sustained run, "
                                "quick release (3 @60) + re-press, reversal to north (runtime placeholder sprite, not pilot "
                                "art), south again, stop to v8, short run, stop to v8",
               "capture_receipt": os.path.basename(a.receipt), "mp4": outputs, "critical_frames": frames_out}
    rname = f"{SLUG}_city-annex_female-south-run-v10r1-showreel-and-critical-frames-receipt_unapproved_{STAMP}-{fid('reel-receipt')}.json"
    with open(_fs(os.path.join(a.out_dir, rname)), "w", encoding="utf-8", newline="\n") as f:
        f.write(json.dumps(receipt, indent=1) + "\n")
    print("RECEIPT", rname)


if __name__ == "__main__":
    main()
