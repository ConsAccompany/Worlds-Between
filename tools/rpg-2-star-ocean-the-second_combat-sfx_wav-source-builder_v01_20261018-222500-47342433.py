"""Worlds Between combat sounds v01: editable, deterministic source for eight authored battle WAVs.

Original synthesis only (no samples, recordings or generation services): sine partials with
exponential pitch glides, inharmonic struck partials, pitch-dropping knocks and LCG noise through
swept one-pole filters. Synthesized content candidate; not a professional listening audition.

Usage:
  python <this> build <out_dir>              write the eight WAVs into out_dir
  python <this> verify <delivered_dir> <report.json>
      rebuild twice in temp dirs, byte-compare both rebuilds with the delivered WAVs, run the
      signal checks on the delivered bytes and write a JSON report; exit 1 on any failed check.
  python <this> manifest <out.json> <repo_root> <path>...
      hash repo-relative paths: .wav/.gz as sha256-bytes, everything else sha256-text-lf-v1
      (CRLF -> LF only, no other normalization).
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
PREFIX = "rpg-2-star-ocean-the-second_combat-"
STAMP = "20261018-222500"


def _file(event, uid):
    return PREFIX + event + "_battle-sfx_v01_" + STAMP + "-" + uid + ".wav"


def _note(f, start, amp, tau, partials, attack=6.0, f0=None, glide=1.0):
    return {"kind": "tone", "amp": amp, "f0": f if f0 is None else f0, "f1": f, "glide": glide,
            "start": start, "partials": partials, "attack": attack, "tau": tau}


# Layer kinds (times in ms):
#   noise: LCG noise -> 2-pole low-pass swept lp0 -> lp1 (sweep tau) -> high-pass hp; envelope attack/tau
#   knock: sine whose pitch drops f0 -> f1 (glide tau); envelope attack/tau
#   tone:  harmonic partials over an exponential glide f0 -> f1
#   bell:  inharmonic partials [ratio, amp, tau] over base f, struck at start
BRASS = [1.0, 0.5, 0.33, 0.2]
CUES = {
    "attack": {
        "file": _file("attack", "44fc6fe0"),
        "character": "rising blade swish into a bright contact snap at ~80 ms with a dropping knock; 230 ms",
        "duration_ms": 230.0, "fade_in_ms": 2.0, "fade_out_ms": 20.0, "seed": 5101,
        "layers": [
            {"kind": "noise", "amp": 0.45, "lp0": 900.0, "lp1": 3800.0, "sweep": 60.0, "hp": 600.0, "start": 0.0, "attack": 55.0, "tau": 25.0},
            {"kind": "noise", "amp": 0.95, "lp0": 4500.0, "lp1": 2000.0, "sweep": 15.0, "hp": 1500.0, "start": 78.0, "attack": 0.3, "tau": 6.0},
            {"kind": "knock", "amp": 0.6, "f0": 220.0, "f1": 95.0, "glide": 20.0, "start": 78.0, "attack": 0.6, "tau": 28.0},
            {"kind": "bell", "f": 1180.0, "start": 78.0, "attack": 0.5, "partials": [[1.0, 0.2, 40.0], [2.7, 0.1, 20.0]]},
        ],
    },
    "dodge": {
        "file": _file("dodge", "de3cac5f"),
        "character": "airy swell-and-pass whoosh with a faint falling whistle, no impact; 250 ms",
        "duration_ms": 250.0, "fade_in_ms": 2.0, "fade_out_ms": 30.0, "seed": 7313,
        "layers": [
            {"kind": "noise", "amp": 0.7, "lp0": 600.0, "lp1": 2600.0, "sweep": 90.0, "hp": 800.0, "start": 0.0, "attack": 70.0, "tau": 45.0},
            _note(620.0, 15.0, 0.18, 60.0, [1.0], attack=40.0, f0=1050.0, glide=60.0),
        ],
    },
    "guard": {
        "file": _file("guard", "f17092a4"),
        "character": "short tick then metallic inharmonic shield ring (410 Hz base) over a low block knock; 420 ms",
        "duration_ms": 420.0, "fade_in_ms": 1.0, "fade_out_ms": 30.0, "seed": 1999,
        "layers": [
            {"kind": "noise", "amp": 0.5, "lp0": 6000.0, "lp1": 3000.0, "sweep": 10.0, "hp": 2000.0, "start": 0.0, "attack": 0.3, "tau": 4.0},
            {"kind": "bell", "f": 410.0, "start": 0.0, "attack": 0.8, "partials": [
                [1.0, 0.5, 160.0], [2.41, 0.35, 110.0], [3.93, 0.25, 70.0], [5.4, 0.15, 45.0], [6.79, 0.1, 30.0]]},
            {"kind": "knock", "amp": 0.35, "f0": 180.0, "f1": 140.0, "glide": 30.0, "start": 0.0, "attack": 0.8, "tau": 25.0},
        ],
    },
    "hit": {
        "file": _file("hit", "58dc96e7"),
        "character": "heavy body thud: 150->52 Hz pitch-dropping knock, dark noise burst, short crunch; 260 ms",
        "duration_ms": 260.0, "fade_in_ms": 2.5, "fade_out_ms": 25.0, "seed": 3301,
        "layers": [
            {"kind": "knock", "amp": 1.0, "f0": 150.0, "f1": 52.0, "glide": 35.0, "start": 0.0, "attack": 1.0, "tau": 55.0},
            {"kind": "noise", "amp": 0.55, "lp0": 1800.0, "lp1": 500.0, "sweep": 40.0, "hp": 120.0, "start": 0.0, "attack": 0.5, "tau": 22.0},
            {"kind": "knock", "amp": 0.3, "f0": 420.0, "f1": 260.0, "glide": 10.0, "start": 0.0, "attack": 0.4, "tau": 9.0},
        ],
    },
    "skill": {
        "file": _file("skill", "7576322a"),
        "character": "detuned energy charge rising 330->990 Hz with shimmer, struck release at 260 ms; 560 ms",
        "duration_ms": 560.0, "fade_in_ms": 2.0, "fade_out_ms": 40.0, "seed": 6007,
        "layers": [
            _note(990.0, 0.0, 0.5, 220.0, [1.0, 0.35, 0.15], attack=120.0, f0=330.0, glide=140.0),
            _note(1000.0, 0.0, 0.25, 220.0, [1.0], attack=120.0, f0=333.0, glide=140.0),
            {"kind": "bell", "f": 1320.0, "start": 260.0, "attack": 2.0, "partials": [[1.0, 0.3, 120.0], [2.0, 0.15, 80.0]]},
            {"kind": "noise", "amp": 0.15, "lp0": 3000.0, "lp1": 8000.0, "sweep": 200.0, "hp": 3000.0, "start": 0.0, "attack": 150.0, "tau": 150.0},
        ],
    },
    "heal": {
        "file": _file("heal", "868719df"),
        "character": "soft rising C major arpeggio C5-E5-G5-C6 with faint air; gentle, 720 ms",
        "duration_ms": 720.0, "fade_in_ms": 2.0, "fade_out_ms": 60.0, "seed": 8191,
        "layers": [
            _note(523.25, 0.0, 0.4, 180.0, [1.0, 0.1], attack=8.0),
            _note(659.25, 90.0, 0.4, 180.0, [1.0, 0.1], attack=8.0),
            _note(783.99, 180.0, 0.4, 180.0, [1.0, 0.1], attack=8.0),
            _note(1046.5, 270.0, 0.4, 200.0, [1.0, 0.1], attack=8.0),
            {"kind": "noise", "amp": 0.05, "lp0": 9000.0, "lp1": 9000.0, "sweep": 1.0, "hp": 4000.0, "start": 0.0, "attack": 200.0, "tau": 200.0},
        ],
    },
    "victory": {
        "file": _file("victory", "3e851f4e"),
        "character": "bright brassy fanfare G4-C5-E5 up to a held G5 over C5; 980 ms",
        "duration_ms": 980.0, "fade_in_ms": 2.0, "fade_out_ms": 80.0, "seed": 4243,
        "layers": [
            _note(392.0, 0.0, 0.35, 90.0, BRASS),
            _note(523.25, 110.0, 0.35, 90.0, BRASS),
            _note(659.25, 220.0, 0.35, 90.0, BRASS),
            _note(783.99, 330.0, 0.4, 380.0, BRASS, attack=10.0),
            _note(523.25, 330.0, 0.25, 380.0, BRASS, attack=10.0),
        ],
    },
    "defeat": {
        "file": _file("defeat", "5b91e159"),
        "character": "dark descending E4-C4-A3 with the last note sagging to G3 over a low rumble; 900 ms",
        "duration_ms": 900.0, "fade_in_ms": 4.0, "fade_out_ms": 80.0, "seed": 2711,
        "layers": [
            _note(329.63, 0.0, 0.4, 160.0, [1.0, 0.3, 0.12], attack=12.0),
            _note(261.63, 180.0, 0.4, 160.0, [1.0, 0.3, 0.12], attack=12.0),
            _note(196.0, 360.0, 0.45, 220.0, [1.0, 0.3, 0.12], attack=12.0, f0=220.0, glide=300.0),
            {"kind": "noise", "amp": 0.06, "lp0": 250.0, "lp1": 250.0, "sweep": 1.0, "hp": 60.0, "start": 0.0, "attack": 30.0, "tau": 200.0},
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
    for number, layer in enumerate(spec["layers"]):
        attack, tau = layer["attack"] / 1000.0, layer.get("tau", 1.0) / 1000.0
        start = layer.get("start", 0.0) / 1000.0
        kind = layer["kind"]
        if kind == "noise":
            raw, y, z, sweep = _noise(count, spec["seed"] + 97 * number), 0.0, 0.0, layer["sweep"] / 1000.0
            swept = []
            for i, x in enumerate(raw):
                t = max(0.0, i / RATE - start)
                fc = layer["lp1"] + (layer["lp0"] - layer["lp1"]) * math.exp(-t / sweep)
                a = math.exp(-2.0 * math.pi * fc / RATE)
                y = (1.0 - a) * x + a * y  # two cascaded poles: 12 dB/oct keeps noise free of sample steps
                z = (1.0 - a) * y + a * z
                swept.append(z)
            raw = _hp(swept, layer["hp"])
            for i in range(count):
                mix[i] += layer["amp"] * raw[i] * _envelope(i / RATE - start, attack, tau)
        elif kind in ("knock", "tone"):
            phase, glide = 0.0, layer["glide"] / 1000.0
            partials = layer.get("partials", [1.0])
            norm = sum(partials)
            for i in range(count):
                t = i / RATE - start
                if t < 0.0:
                    continue
                f = layer["f1"] + (layer["f0"] - layer["f1"]) * math.exp(-t / glide)
                phase += 2.0 * math.pi * f / RATE
                value = sum(a * math.sin((k + 1) * phase) for k, a in enumerate(partials)) / norm
                mix[i] += layer["amp"] * value * _envelope(t, attack, tau)
        elif kind == "bell":
            for i in range(count):
                t = i / RATE - start
                if t >= 0.0:
                    mix[i] += sum(amp * math.sin(2.0 * math.pi * layer["f"] * ratio * t) * _envelope(t, attack, ptau / 1000.0)
                                  for ratio, amp, ptau in layer["partials"])
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
    """Strict RIFF/PCM parse; returns (fmt dict, samples, data bytes) or raises ValueError."""
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


def _rms(seg):
    return math.sqrt(sum(x * x for x in seg) / max(1, len(seg)))


def _zcr_hz(seg):
    """Zero-crossing pitch estimate in Hz (half the crossing rate); tonal segments only."""
    crossings = sum(1 for i in range(len(seg) - 1) if (seg[i] < 0.0) != (seg[i + 1] < 0.0))
    return 0.5 * crossings * RATE / max(1, len(seg))


def _centroid(seg):
    num = den = 0.0
    for b in range(1, 65):
        f = b * 125.0
        re = sum(x * math.cos(2 * math.pi * f * i / RATE) for i, x in enumerate(seg))
        im = sum(x * math.sin(2 * math.pi * f * i / RATE) for i, x in enumerate(seg))
        mag = math.hypot(re, im)
        num += f * mag
        den += mag
    return num / den


def analyse(blob):
    fmt, s, data = parse_wav(blob)
    n = len(s)
    fs = [x / 32768.0 for x in s]
    peak = max(abs(x) for x in fs)
    win, hop = int(0.03 * RATE), 64
    rms30 = [(i, _rms(fs[i:i + win])) for i in range(0, max(1, n - win), hop)]
    loud_at, loud = max(rms30, key=lambda row: row[1])
    win5 = int(0.005 * RATE)
    rms5 = [(i, _rms(fs[i:i + win5])) for i in range(0, n - win5, 32)]
    burst_at, burst = max(rms5, key=lambda row: row[1])
    quarter = n // 4
    return {
        "fmt": fmt, "frames": n, "durationMs": round(1000.0 * n / RATE, 3),
        "peakDbfs": round(_db(peak), 3), "maxAbsSample": max(abs(x) for x in s),
        "clippedSamples": sum(1 for x in s if x in (32767, -32768)),
        "dcFs": sum(fs) / n, "firstSample": s[0], "lastSample": s[-1],
        "edgeMaxAbsFs": round(max(abs(x) for x in fs[:16] + fs[-16:]), 6),
        "maxStepFs": round(max(abs(fs[i + 1] - fs[i]) for i in range(n - 1)), 6),
        "loudest30msRmsDbfs": round(_db(loud), 3), "loudest30msStartMs": round(1000.0 * loud_at / RATE, 1),
        "loudest5msStartMs": round(1000.0 * burst_at / RATE, 1),
        "tailRmsDbRelLoudest": round(_db(_rms(fs[3 * quarter:])) - _db(loud), 3),
        "centroidFirst120msHz": round(_centroid(fs[:int(0.12 * RATE)]), 1),
        "zcrPitchFirstQuarterHz": round(_zcr_hz(fs[:quarter]), 1),
        "zcrPitchLastHalfHz": round(_zcr_hz(fs[2 * quarter:]), 1),
        "dataChunkSha256": hashlib.sha256(data).hexdigest(),
        "_samples": fs,
    }


def _xcorr_max(a, b):
    """Peak normalized cross-correlation of the first 150 ms over lags of +-5 ms (shape similarity)."""
    n = min(len(a), len(b), int(0.15 * RATE))
    a, b = a[:n], b[:n]
    ea = math.sqrt(sum(x * x for x in a)); eb = math.sqrt(sum(x * x for x in b))
    best = 0.0
    for lag in range(-220, 221, 4):
        acc = sum(a[i] * b[i + lag] for i in range(max(0, -lag), min(n, n - lag)))
        best = max(best, abs(acc) / (ea * eb))
    return best


def verify(delivered_dir, report_path):
    checks, hashes = [], {}

    def check(label, ok, detail=None):
        checks.append({"check": label, "passed": bool(ok), "detail": detail})
        print("COMBAT_SFX", "PASS" if ok else "FAIL", label, "" if detail is None else detail)

    with tempfile.TemporaryDirectory(prefix="wb-cbsfx-a-") as one, tempfile.TemporaryDirectory(prefix="wb-cbsfx-b-") as two:
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
        st = analyse(open(os.path.join(delivered_dir, spec["file"]), "rb").read())
        stats[event] = st
        check(event + " PCM 16-bit mono 44.1 kHz", st["fmt"] == {"format": 1, "channels": 1, "rate": 44100, "byteRate": 88200, "blockAlign": 2, "bits": 16}, st["fmt"])
        check(event + " frames match authored duration", st["frames"] == int(round(spec["duration_ms"] * RATE / 1000.0)), st["frames"])
        check(event + " at most 1 s (runtime usable_asset bound)", st["frames"] <= RATE, st["durationMs"])
        check(event + " peak within -16..-12 dBFS", -16.0 <= st["peakDbfs"] <= -12.0, st["peakDbfs"])
        check(event + " no clipped samples", st["clippedSamples"] == 0)
        check(event + " near-zero DC (|mean| < 0.001 FS)", abs(st["dcFs"]) < 0.001, st["dcFs"])
        check(event + " zero first/last sample", st["firstSample"] == 0 and st["lastSample"] == 0)
        check(event + " smooth edges (first/last 16 samples < 0.01 FS)", st["edgeMaxAbsFs"] < 0.01, st["edgeMaxAbsFs"])
        check(event + " no sample-step discontinuity (< 0.1 FS)", st["maxStepFs"] < 0.1, st["maxStepFs"])
        check(event + " not silence (loudest 30 ms RMS > -40 dBFS)", st["loudest30msRmsDbfs"] > -40.0, st["loudest30msRmsDbfs"])
        check(event + " decays (last-quarter RMS >= 12 dB below loudest 30 ms)", st["tailRmsDbRelLoudest"] <= -12.0, st["tailRmsDbRelLoudest"])
    louds = [s["loudest30msRmsDbfs"] for s in stats.values()]
    check("levels consistent (loudest 30 ms RMS spread <= 6 dB)", max(louds) - min(louds) <= 6.0, round(max(louds) - min(louds), 3))
    events = list(CUES)
    for i in range(len(events)):
        for j in range(i + 1, len(events)):
            x, y = stats[events[i]], stats[events[j]]
            corr = _xcorr_max(x["_samples"], y["_samples"])
            check("distinct waveforms %s vs %s (max xcorr < 0.5)" % (events[i], events[j]), corr < 0.5, round(corr, 4))
            check("distinct hashes %s vs %s" % (events[i], events[j]), x["dataChunkSha256"] != y["dataChunkSha256"])
    durations = sorted(s["durationMs"] for s in stats.values())
    check("distinct durations/envelopes", len(set(durations)) == len(durations), durations)
    # Timbre/envelope intent, measured on the delivered bytes.
    c = {e: s["centroidFirst120msHz"] for e, s in stats.items()}
    at = stats["attack"]["loudest5msStartMs"]
    check("attack: wind-up then contact burst between 70 and 110 ms", 70.0 <= at <= 110.0, at)
    check("hit: impact burst within the first 20 ms", stats["hit"]["loudest5msStartMs"] <= 20.0, stats["hit"]["loudest5msStartMs"])
    check("hit is darker than attack and guard (centroid)", c["hit"] < c["attack"] and c["hit"] < c["guard"], c)
    check("dodge swells (loudest 30 ms starts after 20 ms) with no low impact (centroid > hit)",
          stats["dodge"]["loudest30msStartMs"] > 20.0 and c["dodge"] > c["hit"], [stats["dodge"]["loudest30msStartMs"], c["dodge"]])
    check("guard rings longer than hit (tail RMS higher)", stats["guard"]["tailRmsDbRelLoudest"] > stats["hit"]["tailRmsDbRelLoudest"],
          [stats["guard"]["tailRmsDbRelLoudest"], stats["hit"]["tailRmsDbRelLoudest"]])
    for event in ("skill", "heal", "victory"):
        st = stats[event]
        check(event + " pitch rises (zero-crossing pitch, last half > first quarter)", st["zcrPitchLastHalfHz"] > st["zcrPitchFirstQuarterHz"],
              [st["zcrPitchFirstQuarterHz"], st["zcrPitchLastHalfHz"]])
    st = stats["defeat"]
    check("defeat pitch falls (zero-crossing pitch, last half < first quarter)", st["zcrPitchLastHalfHz"] < st["zcrPitchFirstQuarterHz"],
          [st["zcrPitchFirstQuarterHz"], st["zcrPitchLastHalfHz"]])
    check("defeat is darker than victory (centroid)", c["defeat"] < c["victory"], [c["defeat"], c["victory"]])
    failed = sum(1 for row in checks if not row["passed"])
    for st in stats.values():
        st.pop("_samples")
        st["dcFs"] = round(st["dcFs"], 8)
    report = {
        "builder": os.path.basename(__file__),
        "builderSha256TextLfV1": _text_lf(open(__file__, "rb").read()),
        "assets": hashes, "signal": stats, "checks": checks,
        "passed": len(checks) - failed, "total": len(checks),
        "auditioned": False, "audioArtApproved": False,
    }
    with open(report_path, "w", encoding="utf-8", newline="\n") as handle:
        handle.write(json.dumps(report, indent=2, ensure_ascii=False) + "\n")
    print("COMBAT_SFX_RESULT %d/%d" % (len(checks) - failed, len(checks)))
    return 1 if failed else 0


def _text_lf(blob):
    return hashlib.sha256(blob.replace(b"\r\n", b"\n")).hexdigest()


def manifest(out_path, repo_root, paths):
    rows = []
    for rel in paths:
        blob = open(os.path.join(repo_root, rel), "rb").read()
        binary = rel.endswith((".wav", ".gz"))
        rows.append({"path": rel, "normalization": "sha256-bytes" if binary else "sha256-text-lf-v1",
                     "sha256": hashlib.sha256(blob).hexdigest() if binary else _text_lf(blob), "bytes": len(blob)})
    with open(out_path, "w", encoding="utf-8", newline="\n") as handle:
        handle.write(json.dumps({"files": rows}, indent=2, ensure_ascii=False) + "\n")


if __name__ == "__main__":
    if len(sys.argv) == 3 and sys.argv[1] == "build":
        build(sys.argv[2])
    elif len(sys.argv) == 4 and sys.argv[1] == "verify":
        sys.exit(verify(sys.argv[2], sys.argv[3]))
    elif len(sys.argv) >= 5 and sys.argv[1] == "manifest":
        manifest(sys.argv[2], sys.argv[3], sys.argv[4:])
    else:
        print(__doc__)
        sys.exit(2)
