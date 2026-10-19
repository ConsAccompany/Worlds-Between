"""Worlds Between interface sounds v01: editable, deterministic source for three authored UI WAVs.

Original synthesis only (no samples, no generation service): shaped sine partials, an exponential
pitch glide, a low felt "knock" and LCG noise through one-pole filters. Warm, tactile and short.

Usage:
  python <this> build <out_dir>              write the three WAVs into out_dir
  python <this> verify <delivered_dir> <report.json>
      rebuild twice in temp dirs, byte-compare both rebuilds with the delivered WAVs, run the
      signal checks on the delivered bytes and write a JSON report; exit 1 on any failed check.
"""
import hashlib
import json
import math
import os
import struct
import sys
import tempfile

RATE = 44100
PEAK_DBFS = -14.0
PREFIX = "rpg-2-star-ocean-the-second_"
STAMP = "20261018-215528"

# Each cue: duration, edge fades (ms), layers. Layer kinds:
#   noise: LCG noise -> low-pass fc -> high-pass hp; envelope attack/tau (ms)
#   knock: plain sine at f; envelope attack/tau
#   tone: harmonic partials over an exponential glide f0 -> f1 (glide tau ms); start offset ms
#   bell: one inharmonic partial (ratio x f) with its own fast decay, for a soft struck edge
CUES = {
    "ui.confirm": {
        "file": PREFIX + "ui-confirm_interface-sfx_v01_" + STAMP + "-fd2f02df.wav",
        "character": "felt tap + short rising pip (G5); bright-warm, decisive, 90 ms",
        "duration_ms": 90.0, "fade_in_ms": 1.2, "fade_out_ms": 10.0, "seed": 4111,
        "layers": [
            {"kind": "noise", "amp": 0.55, "lp": 2800.0, "hp": 400.0, "attack": 0.4, "tau": 3.5},
            {"kind": "knock", "amp": 0.32, "f": 190.0, "attack": 0.8, "tau": 10.0},
            {"kind": "tone", "amp": 0.55, "f0": 700.0, "f1": 783.99, "glide": 8.0, "start": 2.0,
             "partials": [1.0, 0.22, 0.06], "attack": 2.5, "tau": 28.0},
        ],
    },
    "ui.cancel": {
        "file": PREFIX + "ui-cancel_interface-sfx_v01_" + STAMP + "-b6b84df7.wav",
        "character": "muted thump + falling C5->G4 sigh; darker and softer, 120 ms",
        "duration_ms": 120.0, "fade_in_ms": 0.8, "fade_out_ms": 14.0, "seed": 9721,
        "layers": [
            {"kind": "noise", "amp": 0.42, "lp": 1100.0, "hp": 180.0, "attack": 0.8, "tau": 5.0},
            {"kind": "knock", "amp": 0.30, "f": 140.0, "attack": 1.2, "tau": 14.0},
            {"kind": "tone", "amp": 0.60, "f0": 523.25, "f1": 392.0, "glide": 30.0, "start": 1.5,
             "partials": [1.0, 0.12, 0.03], "attack": 4.0, "tau": 38.0},
        ],
    },
    "ui.notice": {
        "file": PREFIX + "ui-notice_interface-sfx_v01_" + STAMP + "-09a0a294.wav",
        "character": "two soft struck notes D5 then G5 (open fourth); neutral, unhurried, 300 ms",
        "duration_ms": 300.0, "fade_in_ms": 1.0, "fade_out_ms": 18.0, "seed": 2203,
        "layers": [
            {"kind": "noise", "amp": 0.08, "lp": 1500.0, "hp": 300.0, "attack": 0.6, "tau": 3.0},
            {"kind": "tone", "amp": 0.50, "f0": 587.33, "f1": 587.33, "glide": 1.0, "start": 0.0,
             "partials": [1.0, 0.18], "attack": 4.0, "tau": 70.0},
            {"kind": "bell", "amp": 0.08, "f": 587.33, "ratio": 2.76, "start": 0.0, "attack": 1.0, "tau": 15.0},
            {"kind": "tone", "amp": 0.50, "f0": 783.99, "f1": 783.99, "glide": 1.0, "start": 65.0,
             "partials": [1.0, 0.18], "attack": 4.0, "tau": 85.0},
            {"kind": "bell", "amp": 0.08, "f": 783.99, "ratio": 2.76, "start": 65.0, "attack": 1.0, "tau": 15.0},
        ],
    },
}


def _envelope(t, attack_s, tau_s):
    if t < 0.0:
        return 0.0
    rise = 0.5 - 0.5 * math.cos(math.pi * t / attack_s) if t < attack_s else 1.0
    return rise * math.exp(-max(0.0, t - attack_s) / tau_s)


def _lp(samples, fc):
    a = math.exp(-2.0 * math.pi * fc / RATE)
    out, y = [], 0.0
    for x in samples:
        y = (1.0 - a) * x + a * y
        out.append(y)
    return out


def _hp(samples, fc):
    low = _lp(samples, fc)
    return [x - l for x, l in zip(samples, low)]


def _noise(count, seed):
    state, out = seed, []
    for _ in range(count):
        state = (state * 1103515245 + 12345) & 0x7FFFFFFF
        out.append(state / 1073741824.0 - 1.0)
    return out


def render(spec):
    count = int(round(spec["duration_ms"] * RATE / 1000.0))
    mix = [0.0] * count
    for layer in spec["layers"]:
        attack, tau = layer["attack"] / 1000.0, layer["tau"] / 1000.0
        start = layer.get("start", 0.0) / 1000.0
        if layer["kind"] == "noise":
            raw = _hp(_lp(_noise(count, spec["seed"]), layer["lp"]), layer["hp"])
            for i in range(count):
                mix[i] += layer["amp"] * raw[i] * _envelope(i / RATE, attack, tau)
        elif layer["kind"] == "knock":
            for i in range(count):
                t = i / RATE
                mix[i] += layer["amp"] * math.sin(2.0 * math.pi * layer["f"] * t) * _envelope(t, attack, tau)
        elif layer["kind"] == "tone":
            phase, glide = 0.0, layer["glide"] / 1000.0
            norm = sum(layer["partials"])
            for i in range(count):
                t = i / RATE - start
                if t < 0.0:
                    continue
                f = layer["f1"] + (layer["f0"] - layer["f1"]) * math.exp(-t / glide)
                phase += 2.0 * math.pi * f / RATE
                value = sum(a * math.sin((k + 1) * phase) for k, a in enumerate(layer["partials"])) / norm
                mix[i] += layer["amp"] * value * _envelope(t, attack, tau)
        elif layer["kind"] == "bell":
            for i in range(count):
                t = i / RATE - start
                if t >= 0.0:
                    mix[i] += layer["amp"] * math.sin(2.0 * math.pi * layer["f"] * layer["ratio"] * t) * _envelope(t, attack, tau)
    mix = _hp(mix, 25.0)  # remove any sub-audible offset before the edge windows
    fade_in = max(2, int(round(spec["fade_in_ms"] * RATE / 1000.0)))
    fade_out = max(2, int(round(spec["fade_out_ms"] * RATE / 1000.0)))
    for i in range(fade_in):
        mix[i] *= 0.5 - 0.5 * math.cos(math.pi * i / fade_in)
    for i in range(fade_out):
        mix[count - 1 - i] *= 0.5 - 0.5 * math.cos(math.pi * i / fade_out)
    peak = max(abs(x) for x in mix)
    gain = (10.0 ** (PEAK_DBFS / 20.0)) / peak
    pcm = [int(round(x * gain * 32767.0)) for x in mix]
    pcm[0] = pcm[-1] = 0
    return pcm


def wav_bytes(pcm):
    data = struct.pack("<%dh" % len(pcm), *pcm)
    header = b"RIFF" + struct.pack("<I", 36 + len(data)) + b"WAVE"
    header += b"fmt " + struct.pack("<IHHIIHH", 16, 1, 1, RATE, RATE * 2, 2, 16)
    header += b"data" + struct.pack("<I", len(data))
    return header + data


def build(out_dir):
    os.makedirs(out_dir, exist_ok=True)
    for spec in CUES.values():
        with open(os.path.join(out_dir, spec["file"]), "wb") as handle:
            handle.write(wav_bytes(render(spec)))


def parse_wav(blob):
    """Strict RIFF/PCM parse; returns (fmt dict, samples) or raises ValueError."""
    if blob[:4] != b"RIFF" or blob[8:12] != b"WAVE":
        raise ValueError("not RIFF/WAVE")
    pos, fmt, data = 12, None, None
    while pos + 8 <= len(blob):
        cid, size = blob[pos:pos + 4], struct.unpack("<I", blob[pos + 4:pos + 8])[0]
        body = blob[pos + 8:pos + 8 + size]
        if cid == b"fmt ":
            tag, ch, rate, brate, align, bits = struct.unpack("<HHIIHH", body[:16])
            fmt = {"format": tag, "channels": ch, "rate": rate, "byteRate": brate, "blockAlign": align, "bits": bits}
        elif cid == b"data":
            data = body
        pos += 8 + size + (size & 1)
    if fmt is None or data is None:
        raise ValueError("missing fmt/data chunk")
    return fmt, list(struct.unpack("<%dh" % (len(data) // 2), data)), data


def _db(x):
    return 20.0 * math.log10(x) if x > 0 else -999.0


def analyse(blob):
    fmt, s, data = parse_wav(blob)
    n = len(s)
    fs = [x / 32768.0 for x in s]
    peak = max(abs(x) for x in fs)
    win = int(0.03 * RATE)
    loud = max(math.sqrt(sum(x * x for x in fs[i:i + win]) / win) for i in range(0, max(1, n - win), 64))
    # Spectral centroid over the first 60 ms (naive DFT on 64 bins up to 8 kHz).
    seg = fs[:int(0.06 * RATE)]
    num = den = 0.0
    for b in range(1, 65):
        f = b * 125.0
        re = sum(x * math.cos(2 * math.pi * f * i / RATE) for i, x in enumerate(seg))
        im = sum(x * math.sin(2 * math.pi * f * i / RATE) for i, x in enumerate(seg))
        mag = math.hypot(re, im)
        num += f * mag
        den += mag
    return {
        "fmt": fmt, "frames": n, "durationMs": round(1000.0 * n / RATE, 3),
        "peakDbfs": round(_db(peak), 3), "maxAbsSample": max(abs(x) for x in s),
        "clippedSamples": sum(1 for x in s if x in (32767, -32768)),
        "dcFs": sum(fs) / n, "firstSample": s[0], "lastSample": s[-1],
        "edgeMaxAbsFs": round(max(abs(x) for x in fs[:16] + fs[-16:]), 6),
        "maxStepFs": round(max(abs(fs[i + 1] - fs[i]) for i in range(n - 1)), 6),
        "loudest30msRmsDbfs": round(_db(loud), 3), "centroidHz": round(num / den, 1),
        "dataChunkSha256": hashlib.sha256(data).hexdigest(),
        "_samples": fs,
    }


def _xcorr_max(a, b):
    """Peak normalized cross-correlation over lags of +-5 ms (shape similarity)."""
    n = min(len(a), len(b))
    a, b = a[:n], b[:n]
    ea = math.sqrt(sum(x * x for x in a)); eb = math.sqrt(sum(x * x for x in b))
    best = 0.0
    for lag in range(-220, 221, 2):
        acc = sum(a[i] * b[i + lag] for i in range(max(0, -lag), min(n, n - lag)))
        best = max(best, abs(acc) / (ea * eb))
    return best


def verify(delivered_dir, report_path):
    checks, hashes = [], {}

    def check(label, ok, detail=None):
        checks.append({"check": label, "passed": bool(ok), "detail": detail})
        print("UI_SFX", "PASS" if ok else "FAIL", label, "" if detail is None else detail)

    with tempfile.TemporaryDirectory(prefix="wb-uisfx-a-") as one, tempfile.TemporaryDirectory(prefix="wb-uisfx-b-") as two:
        build(one)
        build(two)
        for event, spec in CUES.items():
            a = open(os.path.join(one, spec["file"]), "rb").read()
            b = open(os.path.join(two, spec["file"]), "rb").read()
            d = open(os.path.join(delivered_dir, spec["file"]), "rb").read()
            check(event + " rebuild is deterministic (two rebuilds byte-equal)", a == b)
            check(event + " delivered WAV bytes equal rebuild", d == a, hashlib.sha256(d).hexdigest())
            hashes[event] = {"file": spec["file"], "sha256-bytes": hashlib.sha256(d).hexdigest(), "bytes": len(d)}
    stats = {}
    for event, spec in CUES.items():
        blob = open(os.path.join(delivered_dir, spec["file"]), "rb").read()
        st = analyse(blob)
        stats[event] = st
        f = st["fmt"]
        check(event + " PCM 16-bit mono 44.1 kHz", f == {"format": 1, "channels": 1, "rate": 44100, "byteRate": 88200, "blockAlign": 2, "bits": 16}, f)
        check(event + " frames match authored duration", st["frames"] == int(round(spec["duration_ms"] * RATE / 1000.0)), st["frames"])
        check(event + " short enough for menus (<= 320 ms)", st["durationMs"] <= 320.0, st["durationMs"])
        check(event + " peak within -16..-12 dBFS", -16.0 <= st["peakDbfs"] <= -12.0, st["peakDbfs"])
        check(event + " no clipped samples", st["clippedSamples"] == 0)
        check(event + " near-zero DC (|mean| < 0.001 FS)", abs(st["dcFs"]) < 0.001, st["dcFs"])
        check(event + " zero first/last sample", st["firstSample"] == 0 and st["lastSample"] == 0)
        check(event + " smooth edges (first/last 16 samples < 0.01 FS)", st["edgeMaxAbsFs"] < 0.01, st["edgeMaxAbsFs"])
        check(event + " no sample-step discontinuity (< 0.1 FS)", st["maxStepFs"] < 0.1, st["maxStepFs"])
        check(event + " not silence (loudest 30 ms RMS > -40 dBFS)", st["loudest30msRmsDbfs"] > -40.0, st["loudest30msRmsDbfs"])
    louds = [s["loudest30msRmsDbfs"] for s in stats.values()]
    check("levels consistent (loudest 30 ms RMS spread <= 4 dB)", max(louds) - min(louds) <= 4.0, round(max(louds) - min(louds), 3))
    events = list(CUES)
    for i in range(len(events)):
        for j in range(i + 1, len(events)):
            x, y = stats[events[i]], stats[events[j]]
            corr = _xcorr_max(x["_samples"], y["_samples"])
            check("distinct waveforms %s vs %s (max xcorr < 0.5)" % (events[i], events[j]), corr < 0.5, round(corr, 4))
            check("distinct hashes %s vs %s" % (events[i], events[j]), x["dataChunkSha256"] != y["dataChunkSha256"])
    durations = sorted(s["durationMs"] for s in stats.values())
    check("distinct durations/envelopes", len(set(durations)) == len(durations), durations)
    centroids = {e: s["centroidHz"] for e, s in stats.items()}
    check("cancel is darker than confirm (centroid)", centroids["ui.cancel"] < centroids["ui.confirm"], centroids)
    failed = sum(1 for c in checks if not c["passed"])
    for st in stats.values():
        st.pop("_samples")
        st["dcFs"] = round(st["dcFs"], 8)
    report = {
        "builder": os.path.basename(__file__),
        "builderSha256TextLfV1": hashlib.sha256(open(__file__, "rb").read().replace(b"\r\n", b"\n")).hexdigest(),
        "assets": hashes, "signal": stats, "checks": checks,
        "passed": len(checks) - failed, "total": len(checks),
        "auditioned": False, "audioArtApproved": False,
    }
    with open(report_path, "w", encoding="utf-8", newline="\n") as handle:
        handle.write(json.dumps(report, indent=2, ensure_ascii=False) + "\n")
    print("UI_SFX_RESULT %d/%d" % (len(checks) - failed, len(checks)))
    return 1 if failed else 0


if __name__ == "__main__":
    if len(sys.argv) == 3 and sys.argv[1] == "build":
        build(sys.argv[2])
    elif len(sys.argv) == 4 and sys.argv[1] == "verify":
        sys.exit(verify(sys.argv[2], sys.argv[3]))
    else:
        print(__doc__)
        sys.exit(2)
