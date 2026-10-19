#!/usr/bin/env python3
"""Deterministic renderer for the Worlds Between four-theme music package.

The score data and this render source were generated with DeepSeek V4.1 Flash
assistance and coordinated/inspected by Codex; no human composer or human
authorship is claimed. It reads the four editable score JSON files beside it,
writes one standard MIDI file and one 24 kHz / 16-bit / stereo PCM WAV per
score, and writes a hash manifest. It uses only the Python standard library and
the already-installed NumPy. No external samples or external melodic references
were supplied to this generation run. That is an observed-input statement, not
a copyright-clearance or legal assurance. There are no external APIs, network
calls, runtime random sources, or master fade-outs.

Run:
    python rpg-2-star-ocean-the-second_themed-package_render-source_v01_20261019-212037-7f3c2a26.py --build
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import platform
import struct
import sys
from pathlib import Path

import numpy as np


TIMESTAMP = "20261019-212037"
UNIQUE_ID = "7f3c2a26"
FILE_PREFIX = "rpg-2-star-ocean-the-second"
PACKAGE_ID = f"{FILE_PREFIX}-themed-v01-{TIMESTAMP}-{UNIQUE_ID}"
GENERATION_MODEL = "DeepSeek V4.1 Flash"
COORDINATED_INSPECTED_BY = "Codex"
CREATED_UTC = "2026-10-19T21:20:37Z"
TASK = "content.audio.themed-music"

BASE = Path(__file__).resolve().parent
SOURCE_NAME = Path(__file__).name
MANIFEST_NAME = f"{FILE_PREFIX}_themed-package_manifest_v01_{TIMESTAMP}-{UNIQUE_ID}.json"
ATTRIBUTION_NAME = (
    f"{FILE_PREFIX}_themed-package_attribution_v01_{TIMESTAMP}-{UNIQUE_ID}.txt"
)

TRACK_SPECS = [
    {
        "subject": "city-dawn-inquiry",
        "slug": "city_dawn_inquiry",
        "score": f"{FILE_PREFIX}_city-dawn-inquiry_score_v01_{TIMESTAMP}-{UNIQUE_ID}.json",
        "midi": f"{FILE_PREFIX}_city-dawn-inquiry_midi_v01_{TIMESTAMP}-{UNIQUE_ID}.mid",
        "wav": f"{FILE_PREFIX}_city-dawn-inquiry_audio_v01_{TIMESTAMP}-{UNIQUE_ID}.wav",
    },
    {
        "subject": "field-wayfarer-current",
        "slug": "field_wayfarer_current",
        "score": f"{FILE_PREFIX}_field-wayfarer-current_score_v01_{TIMESTAMP}-{UNIQUE_ID}.json",
        "midi": f"{FILE_PREFIX}_field-wayfarer-current_midi_v01_{TIMESTAMP}-{UNIQUE_ID}.mid",
        "wav": f"{FILE_PREFIX}_field-wayfarer-current_audio_v01_{TIMESTAMP}-{UNIQUE_ID}.wav",
    },
    {
        "subject": "ruins-observatory-silence",
        "slug": "ruins_observatory_silence",
        "score": f"{FILE_PREFIX}_ruins-observatory-silence_score_v01_{TIMESTAMP}-{UNIQUE_ID}.json",
        "midi": f"{FILE_PREFIX}_ruins-observatory-silence_midi_v01_{TIMESTAMP}-{UNIQUE_ID}.mid",
        "wav": f"{FILE_PREFIX}_ruins-observatory-silence_audio_v01_{TIMESTAMP}-{UNIQUE_ID}.wav",
    },
    {
        "subject": "battle-controlled-pulse",
        "slug": "battle_controlled_pulse",
        "score": f"{FILE_PREFIX}_battle-controlled-pulse_score_v01_{TIMESTAMP}-{UNIQUE_ID}.json",
        "midi": f"{FILE_PREFIX}_battle-controlled-pulse_midi_v01_{TIMESTAMP}-{UNIQUE_ID}.mid",
        "wav": f"{FILE_PREFIX}_battle-controlled-pulse_audio_v01_{TIMESTAMP}-{UNIQUE_ID}.wav",
    },
]

MELODIC_ENGINES = {"additive_pluck", "additive_pad", "round_bass", "additive_bell"}
PERCUSSION_ENGINES = {"kick", "wood_tick", "side_stick", "shaker", "frame_drum"}


# ---------------------------------------------------------------------------
# Small deterministic helpers
# ---------------------------------------------------------------------------

def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha256_file(path: Path) -> str:
    return sha256_bytes(path.read_bytes())


def db_from_linear(value: float) -> float:
    return 20.0 * math.log10(max(float(value), 1.0e-12))


def rms(values: np.ndarray) -> float:
    if values.size == 0:
        return 0.0
    return float(np.sqrt(np.mean(np.square(values, dtype=np.float64))))


def midi_hz(midi_note: int) -> float:
    return 440.0 * (2.0 ** ((int(midi_note) - 69) / 12.0))


def equal_power_pan(pan: float) -> tuple[float, float]:
    p = max(-1.0, min(1.0, float(pan)))
    angle = (p + 1.0) * math.pi / 4.0
    return math.cos(angle), math.sin(angle)


def pan_for_note(part_name: str, midi_note: int, midi_pan: int) -> float:
    base = (float(midi_pan) - 64.0) / 64.0
    if part_name == "pad":
        return max(-0.92, min(0.92, base + 0.58 * math.sin((midi_note - 60) * 0.37 + 0.3)))
    if part_name == "lead":
        return max(-0.92, min(0.92, base + 0.10 * math.sin(midi_note * 0.91 + 0.4)))
    if part_name == "bell":
        return max(-0.92, min(0.92, base + 0.16 * math.sin(midi_note * 0.31)))
    return max(-0.92, min(0.92, base))


def _hash_noise(n: int, seed: int) -> np.ndarray:
    """Deterministic 64-bit integer-hash white noise; no RNG state."""
    if n <= 0:
        return np.zeros(0, dtype=np.float64)
    x = np.arange(n, dtype=np.uint64) + np.uint64(seed & 0xFFFFFFFFFFFFFFFF)
    with np.errstate(over="ignore"):
        z = x + np.uint64(0x9E3779B97F4A7C15)
        z = (z ^ (z >> np.uint64(30))) * np.uint64(0xBF58476D1CE4E5B9)
        z = (z ^ (z >> np.uint64(27))) * np.uint64(0x94D049BB133111EB)
        z = z ^ (z >> np.uint64(31))
    bits = z >> np.uint64(11)
    unit = bits.astype(np.float64) * (1.0 / 9007199254740992.0)
    return unit * 2.0 - 1.0


def _smooth(values: np.ndarray, width: int) -> np.ndarray:
    if width <= 1 or values.size <= 1:
        return values
    width = max(1, int(width))
    kernel = np.ones(width, dtype=np.float64) / float(width)
    return np.convolve(values, kernel, mode="same")


def _attack(t: np.ndarray, attack_s: float, sr: int) -> np.ndarray:
    a = max(float(attack_s), 1.0 / sr)
    return 1.0 - np.exp(-t / a)


def _release_gate(t: np.ndarray, release_start_s: float, release_s: float, sr: int) -> np.ndarray:
    gate = np.ones_like(t, dtype=np.float64)
    length = max(float(release_s), 1.0 / sr)
    mask = t > release_start_s
    if np.any(mask):
        x = np.clip((t[mask] - release_start_s) / length, 0.0, 1.0)
        gate[mask] = 0.5 + 0.5 * np.cos(math.pi * x)
    return gate


def _phase0(midi_note: int, start_tick: int, index: int) -> float:
    frac = (midi_note * 0.6180339887498949 + start_tick * 0.000371 + index * 0.2718281828) % 1.0
    return 2.0 * math.pi * frac


def _partial_env(t: np.ndarray, decay_s: float, index: int, release_gate: np.ndarray,
                 attack: np.ndarray) -> np.ndarray:
    decay = max(float(decay_s), 0.02) / (1.0 + 0.55 * index)
    return np.exp(-t / decay) * release_gate * attack


# ---------------------------------------------------------------------------
# Note synthesis
# ---------------------------------------------------------------------------

def synth_note(note: dict, cfg: dict, bpm: float, sr: int, seed: int,
               part_index: int) -> np.ndarray:
    params = cfg["synthesis"]
    engine = params["engine"]
    gain = float(params["gain"])
    vel = max(1, min(127, int(note["velocity"]))) / 127.0
    dur_s = max(1, int(note["duration_ticks"])) * 60.0 / (bpm * 480.0)
    midi_note = int(note["midi"])
    freq = midi_hz(midi_note)
    start_tick = int(note["start_tick"])

    if engine in PERCUSSION_ENGINES:
        decay = max(0.025, float(params.get("decay_s", 0.1)))
        span_s = max(decay * 6.0, 0.08)
        n = int(math.ceil(span_s * sr)) + 1
        t = np.arange(n, dtype=np.float64) / sr
        amp = gain * (vel ** 1.35)
        note_seed = int((seed + start_tick * 131 + midi_note * 17 + part_index * 1009)
                        & 0xFFFFFFFFFFFFFFFF)

        if engine == "kick":
            f0 = float(params.get("pitch_start_hz", 110.0))
            f1 = float(params.get("pitch_end_hz", 48.0))
            glide = 0.035
            f = f1 + (f0 - f1) * np.exp(-t / glide)
            phase = 2.0 * math.pi * np.cumsum(f) / sr
            body = np.sin(phase) * np.exp(-t / decay)
            click = _hash_noise(n, note_seed)
            click = np.diff(click, prepend=0.0)
            click *= np.exp(-t / 0.008)
            x = body + float(params.get("noise", 0.1)) * click
            x *= _attack(t, 0.001, sr)
        elif engine in ("wood_tick", "side_stick"):
            f = float(params.get("freq_hz", 900.0))
            ring = np.sin(2.0 * math.pi * f * t + _phase0(midi_note, start_tick, 1))
            ring += 0.45 * np.sin(2.0 * math.pi * f * 1.97 * t + _phase0(midi_note, start_tick, 2))
            click = _hash_noise(n, note_seed)
            click = np.diff(click, prepend=0.0)
            x = (ring + float(params.get("noise", 0.06)) * click)
            x *= np.exp(-t / decay) * _attack(t, 0.0008, sr)
        elif engine == "shaker":
            noise = _hash_noise(n, note_seed)
            noise = np.diff(noise, prepend=0.0)
            noise = _smooth(noise, 3)
            env = np.exp(-t / decay) * _attack(t, 0.0012, sr)
            x = noise * env
            bright = float(params.get("brightness", 0.55))
            x = x * (0.72 + 0.28 * bright)
        elif engine == "frame_drum":
            f0 = float(params.get("pitch_start_hz", 90.0))
            f1 = float(params.get("pitch_end_hz", 55.0))
            f = f1 + (f0 - f1) * np.exp(-t / 0.055)
            phase = 2.0 * math.pi * np.cumsum(f) / sr
            body = np.sin(phase) * np.exp(-t / decay)
            noise = _hash_noise(n, note_seed)
            noise = np.diff(noise, prepend=0.0)
            noise = _smooth(noise, 5)
            x = body + float(params.get("noise", 0.08)) * noise * np.exp(-t / (decay * 0.55))
            x *= _attack(t, 0.0015, sr)
        else:
            raise ValueError(f"unknown percussion engine: {engine}")
        return (x * amp).astype(np.float64, copy=False)

    if engine not in MELODIC_ENGINES:
        raise ValueError(f"unknown synthesis engine: {engine}")

    release = max(0.025, float(params.get("release_s", 0.2)))
    n = int(math.ceil((dur_s + release) * sr)) + 1
    t = np.arange(n, dtype=np.float64) / sr
    attack = _attack(t, float(params.get("attack_s", 0.01)), sr)
    release_gate = _release_gate(t, dur_s, release, sr)
    amp = gain * (vel ** 1.45)

    if engine == "additive_pluck":
        partials = [float(v) for v in params["partials"]]
        brightness = float(params.get("brightness", 0.6))
        detune = float(params.get("detune_cents", 0.0))
        x = np.zeros_like(t)
        for i, a in enumerate(partials):
            env_i = _partial_env(t, float(params["decay_s"]), i, release_gate, attack)
            w = 2.0 * math.pi * freq * (i + 1) * t
            x += a * (brightness ** i) * env_i * np.sin(w + _phase0(midi_note, start_tick, i))
        if detune != 0.0:
            ratio = 2.0 ** (detune / 1200.0)
            x2 = np.zeros_like(t)
            for i, a in enumerate(partials):
                env_i = _partial_env(t, float(params["decay_s"]), i, release_gate, attack)
                w = 2.0 * math.pi * freq * ratio * (i + 1) * t
                x2 += a * (brightness ** i) * env_i * np.sin(
                    w + _phase0(midi_note, start_tick, i + 7) + 0.5)
            x = 0.84 * x + 0.16 * x2
        x *= amp

    elif engine == "additive_pad":
        partials = [float(v) for v in params["partials"]]
        detune = float(params.get("detune_cents", 4.0))
        lfo_hz = float(params.get("lfo_hz", 0.06))
        ratio_up = 2.0 ** ((detune * 0.5) / 1200.0)
        ratio_down = 2.0 ** ((-detune * 0.5) / 1200.0)
        x = np.zeros_like(t)
        for i, a in enumerate(partials):
            phase = _phase0(midi_note, start_tick, i + 11)
            w = 2.0 * math.pi * freq * (i + 1) * t
            x += 0.5 * a * np.sin(w * ratio_up + phase)
            x += 0.5 * a * np.sin(w * ratio_down + phase + 0.73)
        lfo = 0.94 + 0.06 * np.sin(
            2.0 * math.pi * lfo_hz * t + _phase0(midi_note, start_tick, 3))
        x *= attack * release_gate * lfo * amp

    elif engine == "round_bass":
        partials = [float(v) for v in params["partials"]]
        drive = max(0.0, float(params.get("drive", 0.15)))
        x = np.zeros_like(t)
        for i, a in enumerate(partials):
            w = 2.0 * math.pi * freq * (i + 1) * t
            x += a * np.sin(w + _phase0(midi_note, start_tick, i + 5))
        body = 0.74 + 0.26 * np.exp(-t / 0.45)
        x *= attack * release_gate * body
        if drive > 0.0:
            d = 1.0 + drive * 3.5
            x = np.tanh(d * x) / math.tanh(d)
        x *= amp

    elif engine == "additive_bell":
        ratios = [float(v) for v in params["ratios"]]
        amps = [float(v) for v in params["amps"]]
        decays = [float(v) for v in params["decays_s"]]
        if not (len(ratios) == len(amps) == len(decays)):
            raise ValueError("bell ratio/amp/decay arrays differ in length")
        x = np.zeros_like(t)
        for i, (ratio, a, dec) in enumerate(zip(ratios, amps, decays)):
            env_i = np.exp(-t / max(dec, 0.05))
            w = 2.0 * math.pi * freq * ratio * t
            x += a * env_i * np.sin(w + _phase0(midi_note, start_tick, i + 13))
        x *= attack * release_gate * amp

    else:
        raise AssertionError("unreachable")

    return x.astype(np.float64, copy=False)


# ---------------------------------------------------------------------------
# Mixing and WAV encoding
# ---------------------------------------------------------------------------

def section_gain_envelope(score: dict, total_frames: int, n_loop_frames: int,
                          sr: int) -> np.ndarray:
    bpm = float(score["tempo_bpm"])
    tick_s = 60.0 / (bpm * score["ticks_per_quarter"])
    frames_per_bar = 4.0 * tick_s * sr
    levels: dict[int, float] = {}
    for sec in score["structure"]:
        for bar in range(int(sec["bars"][0]), int(sec["bars"][1]) + 1):
            levels[bar] = float(sec["level"])
    if set(levels) != set(range(1, 17)):
        raise ValueError("structure does not cover exactly bars 1..16")
    if abs(levels[1] - levels[16]) > 1.0e-9:
        raise ValueError("first and last section levels must match for a clean loop")

    gain = np.empty(total_frames, dtype=np.float64)
    for bar in range(1, 17):
        start = int(round((bar - 1) * frames_per_bar))
        end = int(round(bar * frames_per_bar)) if bar < 16 else n_loop_frames
        start = min(max(start, 0), total_frames)
        end = min(max(end, start), total_frames)
        gain[start:end] = levels[bar]
    gain[n_loop_frames:] = levels[16]

    width = int(round(0.30 * sr))
    if width % 2 == 0:
        width += 1
    if width > 3:
        kernel = np.hanning(width + 2)[1:-1]
        kernel = kernel / kernel.sum()
        pad = width // 2
        gain = np.convolve(np.pad(gain, (pad, pad), mode="edge"), kernel, mode="valid")
    return gain


def render_track(score: dict, score_seed: int) -> tuple[np.ndarray, dict]:
    sr = int(score["render"]["sample_rate_hz"])
    if sr != 24000:
        raise ValueError("this package is fixed to 24000 Hz")
    if int(score["render"]["channels"]) != 2 or int(score["render"]["bit_depth"]) != 16:
        raise ValueError("this package is fixed to 16-bit stereo")
    target_peak = float(score["render"]["target_peak"])
    if target_peak > 0.85:
        raise ValueError("target peak exceeds 0.85 headroom limit")

    bpm = float(score["tempo_bpm"])
    tick_s = 60.0 / (bpm * int(score["ticks_per_quarter"]))
    loop_seconds = int(score["loop_end_tick"]) * tick_s
    n_loop_frames = int(round(loop_seconds * sr))
    wrap_seconds = float(score["render"]["wrap_tail_seconds"])
    wrap_frames = int(round(wrap_seconds * sr))
    total_frames = n_loop_frames + wrap_frames
    audio = np.zeros((total_frames, 2), dtype=np.float64)

    for part_index, part in enumerate(score["parts"]):
        part_name = str(part["name"])
        instrument_name = str(part["instrument"])
        cfg = score["instruments"][instrument_name]
        midi_pan = int(cfg.get("midi_pan", 64))
        for note in part["notes"]:
            mono = synth_note(note, cfg, bpm, sr, score_seed, part_index)
            start = int(round(int(note["start_tick"]) * tick_s * sr))
            end = start + mono.size
            if start < 0 or end > total_frames:
                raise RuntimeError(
                    f"note outside render buffer: {part_name} tick {note['start_tick']}")
            pan = pan_for_note(part_name, int(note["midi"]), midi_pan)
            gl, gr = equal_power_pan(pan)
            audio[start:end, 0] += mono * gl
            audio[start:end, 1] += mono * gr

    gain = section_gain_envelope(score, total_frames, n_loop_frames, sr)
    audio *= gain[:, None]

    tail = audio[n_loop_frames:n_loop_frames + wrap_frames].copy()
    main = audio[:n_loop_frames].copy()
    main[:wrap_frames] += tail

    tail_end_window = max(1, int(0.10 * sr))
    tail_end_rms = rms(tail[-tail_end_window:])
    wrapped_tail_rms = rms(tail)

    main -= main.mean(axis=0, keepdims=True)
    edge_s = float(score["render"]["edge_declick_ms"]) / 1000.0
    if not (0.001 <= edge_s <= 0.020):
        raise ValueError("edge de-click must be between 1 ms and 20 ms")
    edge = max(2, int(round(edge_s * sr)))
    fade = 0.5 - 0.5 * np.cos(np.linspace(0.0, math.pi, edge, endpoint=True))
    main[:edge] *= fade[:, None]
    main[-edge:] *= fade[::-1, None]

    raw_peak = float(np.max(np.abs(main)))
    if raw_peak <= 0.0:
        raise RuntimeError("silent render")
    main *= target_peak / raw_peak

    quantized = np.rint(main * 32767.0)
    clipped = int(np.count_nonzero((quantized < -32768.0) | (quantized > 32767.0)))
    if clipped:
        raise RuntimeError(f"clipping would occur: {clipped} samples")
    pcm = np.clip(quantized, -32768.0, 32767.0).astype("<i2")
    decoded = pcm.astype(np.float64) / 32768.0

    peak = float(np.max(np.abs(decoded)))
    rms_value = rms(decoded)
    dc = decoded.mean(axis=0)
    seam_step = np.abs(decoded[0, :] - decoded[-1, :])
    metrics = {
        "sample_rate_hz": sr,
        "channels": 2,
        "bit_depth": 16,
        "frames": int(n_loop_frames),
        "duration_seconds": round(n_loop_frames / float(sr), 6),
        "peak_linear": round(peak, 9),
        "peak_dbfs": round(db_from_linear(peak), 6),
        "rms_linear": round(rms_value, 9),
        "rms_dbfs": round(db_from_linear(rms_value), 6),
        "dc_offset_left": round(float(dc[0]), 12),
        "dc_offset_right": round(float(dc[1]), 12),
        "clipped_samples": clipped,
        "wrapped_tail_frames": int(wrap_frames),
        "wrapped_tail_seconds": round(wrap_frames / float(sr), 6),
        "wrapped_tail_rms_dbfs": round(db_from_linear(wrapped_tail_rms), 6),
        "tail_end_rms_dbfs": round(db_from_linear(tail_end_rms), 6),
        "edge_declick_ms": round(edge_s * 1000.0, 3),
        "edge_declick_samples": int(edge),
        "first_frame_lr": [int(decoded[0, 0] * 32768.0), int(decoded[0, 1] * 32768.0)],
        "last_frame_lr": [int(decoded[-1, 0] * 32768.0), int(decoded[-1, 1] * 32768.0)],
        "loop_boundary_step_lr": [round(float(seam_step[0]), 12), round(float(seam_step[1]), 12)],
        "loop_boundary_step_max_abs": round(float(np.max(seam_step)), 12),
        "master_fadeout": False,
        "loop_treatment": "release tails rendered, 5.0 s wrapped into the head, 3 ms endpoint de-click",
    }
    if peak > 0.85:
        raise RuntimeError("rendered peak exceeds 0.85")
    if metrics["dc_offset_left"] == 0.0 and metrics["dc_offset_right"] == 0.0:
        pass
    if abs(metrics["dc_offset_left"]) > 1.0e-5 or abs(metrics["dc_offset_right"]) > 1.0e-5:
        raise RuntimeError("DC offset exceeds 1e-5")
    if metrics["rms_dbfs"] < -24.0:
        raise RuntimeError("RMS is near silence")
    return pcm, metrics


def wav_bytes(pcm: np.ndarray, sr: int) -> bytes:
    if pcm.dtype != np.dtype("<i2") or pcm.ndim != 2 or pcm.shape[1] != 2:
        raise ValueError("expected interleaved <i2 stereo samples")
    data = pcm.tobytes(order="C")
    channels = 2
    bits = 16
    block_align = channels * bits // 8
    byte_rate = sr * block_align
    fmt_payload = struct.pack("<HHIIHH", 1, channels, sr, byte_rate, block_align, bits)
    header = (
        b"RIFF" + struct.pack("<I", 36 + len(data)) + b"WAVE"
        + b"fmt " + struct.pack("<I", 16) + fmt_payload
        + b"data" + struct.pack("<I", len(data))
    )
    return header + data


def validate_wav(blob: bytes, expected_frames: int) -> dict:
    if blob[:4] != b"RIFF" or blob[8:12] != b"WAVE":
        raise RuntimeError("invalid WAV RIFF header")
    if struct.unpack_from("<I", blob, 4)[0] + 8 != len(blob):
        raise RuntimeError("WAV RIFF size mismatch")
    pos = 12
    fmt = None
    data = None
    while pos + 8 <= len(blob):
        tag = blob[pos:pos + 4]
        size = struct.unpack_from("<I", blob, pos + 4)[0]
        payload = blob[pos + 8:pos + 8 + size]
        if len(payload) != size:
            raise RuntimeError("truncated WAV chunk")
        if tag == b"fmt ":
            if size < 16:
                raise RuntimeError("short WAV fmt chunk")
            fmt = struct.unpack("<HHIIHH", payload[:16])
        elif tag == b"data":
            data = payload
        pos += 8 + size + (size & 1)
    if fmt is None or data is None:
        raise RuntimeError("missing WAV fmt/data chunk")
    audio_format, channels, sr, _, _, bits = fmt
    if (audio_format, channels, sr, bits) != (1, 2, 24000, 16):
        raise RuntimeError("WAV format is not 24 kHz 16-bit stereo PCM")
    if len(data) != expected_frames * 4:
        raise RuntimeError("WAV frame count mismatch")
    return {"format": audio_format, "channels": channels, "sample_rate_hz": sr,
            "bit_depth": bits, "frames": expected_frames, "data_bytes": len(data)}


# ---------------------------------------------------------------------------
# Standard MIDI file writer / verifier
# ---------------------------------------------------------------------------

def vlq(value: int) -> bytes:
    if value < 0:
        raise ValueError("negative VLQ")
    out = [value & 0x7F]
    value >>= 7
    while value:
        out.append((value & 0x7F) | 0x80)
        value >>= 7
    return bytes(reversed(out))


def meta_event(kind: int, payload: bytes) -> bytes:
    return bytes([0xFF, kind]) + vlq(len(payload)) + payload


def midi_chunk(tag: bytes, payload: bytes) -> bytes:
    return tag + struct.pack(">I", len(payload)) + payload


def make_midi_track(events: list[tuple[int, int, bytes]], end_tick: int) -> bytes:
    events = list(events)
    events.append((end_tick, 99, meta_event(0x2F, b"")))
    events.sort(key=lambda item: (item[0], item[1], item[2]))
    out = bytearray()
    last_tick = 0
    for tick, _, data in events:
        if tick < last_tick:
            raise ValueError("unordered MIDI event")
        out += vlq(tick - last_tick)
        out += data
        last_tick = tick
    return midi_chunk(b"MTrk", bytes(out))


def midi_track_name(name: str) -> bytes:
    return meta_event(0x03, name.encode("ascii"))


def build_midi(score: dict) -> tuple[bytes, dict]:
    loop_end = int(score["loop_end_tick"])
    tpq = int(score["ticks_per_quarter"])
    if tpq != 480:
        raise ValueError("MIDI must use 480 ticks per quarter")
    tempo_us = int(round(60_000_000.0 / float(score["tempo_bpm"])))
    tempo_track_events = [
        (0, 0, midi_track_name(f"{score['score_id']} tempo and meter")),
        (0, 0, meta_event(0x51, tempo_us.to_bytes(3, "big"))),
        (0, 0, meta_event(0x58, bytes([4, 2, 24, 8]))),
    ]
    for sec in score["structure"]:
        marker = f"{sec['section']}: {sec['name']}".encode("ascii")
        tempo_track_events.append((int(sec["start_tick"]), 0, meta_event(0x06, marker)))
    tracks = [make_midi_track(tempo_track_events, loop_end)]

    expected_notes = 0
    for part in score["parts"]:
        cfg = score["instruments"][part["instrument"]]
        ch = int(cfg["midi_channel"])
        if not (0 <= ch <= 15):
            raise ValueError("bad MIDI channel")
        name = f"{score['score_id']} {part['name']}".encode("ascii")
        events: list[tuple[int, int, bytes]] = [(0, 0, meta_event(0x03, name))]
        if cfg.get("gm_program") is not None:
            program = int(cfg["gm_program"])
            if not (0 <= program <= 127):
                raise ValueError("bad GM program")
            events.append((0, 0, bytes([0xC0 | ch, program])))
        events.append((0, 0, bytes([0xB0 | ch, 7, int(cfg.get("midi_volume", 100))])))
        events.append((0, 0, bytes([0xB0 | ch, 10, int(cfg.get("midi_pan", 64))])))
        for n in part["notes"]:
            start = int(n["start_tick"])
            end = start + int(n["duration_ticks"])
            if end > loop_end:
                raise ValueError("MIDI note exceeds loop end")
            pitch = int(n["midi"])
            vel = int(n["velocity"])
            if not (0 <= pitch <= 127 and 1 <= vel <= 127):
                raise ValueError("bad MIDI note or velocity")
            events.append((start, 2, bytes([0x90 | ch, pitch, vel])))
            events.append((end, 1, bytes([0x80 | ch, pitch, 0x40])))
            expected_notes += 1
        tracks.append(make_midi_track(events, loop_end))

    header = b"MThd" + struct.pack(">IHHH", 6, 1, len(tracks), tpq)
    blob = header + b"".join(tracks)
    info = parse_midi(blob)
    if info["format"] != 1 or info["division"] != 480:
        raise RuntimeError("MIDI header mismatch")
    if info["tempo_us"] != tempo_us:
        raise RuntimeError("MIDI tempo mismatch")
    if info["note_ons"] != expected_notes or info["note_offs"] != expected_notes:
        raise RuntimeError("MIDI note count mismatch")
    return blob, {"format": 1, "divisions_per_quarter": 480, "track_chunks": len(tracks),
                  "note_ons": info["note_ons"], "note_offs": info["note_offs"],
                  "tempo_us_per_quarter": tempo_us}


def _read_vlq(buf: bytes, pos: int) -> tuple[int, int]:
    value = 0
    for _ in range(4):
        if pos >= len(buf):
            raise RuntimeError("truncated VLQ")
        b = buf[pos]
        pos += 1
        value = (value << 7) | (b & 0x7F)
        if not (b & 0x80):
            return value, pos
    raise RuntimeError("VLQ too long")


def parse_midi(blob: bytes) -> dict:
    if blob[:4] != b"MThd" or len(blob) < 14:
        raise RuntimeError("missing MIDI header")
    length, fmt, ntrks, division = struct.unpack_from(">IHHH", blob, 4)
    if length != 6:
        raise RuntimeError("bad MIDI header length")
    pos = 14
    note_ons = note_offs = 0
    tempo_us = None
    tracks_seen = 0
    while pos < len(blob):
        if blob[pos:pos + 4] != b"MTrk":
            raise RuntimeError("missing MTrk")
        chunk_len = struct.unpack_from(">I", blob, pos + 4)[0]
        track = blob[pos + 8:pos + 8 + chunk_len]
        if len(track) != chunk_len:
            raise RuntimeError("truncated MTrk")
        pos += 8 + chunk_len
        tracks_seen += 1
        p = 0
        running = None
        saw_end = False
        while p < len(track):
            _, p = _read_vlq(track, p)
            if p >= len(track):
                raise RuntimeError("truncated event")
            status = track[p]
            if status < 0x80:
                if running is None:
                    raise RuntimeError("running status without status")
                status = running
            else:
                p += 1
                running = status
            if status == 0xFF:
                if p >= len(track):
                    raise RuntimeError("truncated meta")
                kind = track[p]
                p += 1
                meta_len, p = _read_vlq(track, p)
                payload = track[p:p + meta_len]
                if len(payload) != meta_len:
                    raise RuntimeError("truncated meta payload")
                p += meta_len
                if kind == 0x51 and meta_len == 3:
                    tempo_us = int.from_bytes(payload, "big")
                if kind == 0x2F:
                    saw_end = True
                    break
            elif status in (0xF0, 0xF7):
                sysex_len, p = _read_vlq(track, p)
                p += sysex_len
                if p > len(track):
                    raise RuntimeError("truncated sysex")
            else:
                high = status >> 4
                if high in (0x8, 0x9):
                    if p + 2 > len(track):
                        raise RuntimeError("truncated note event")
                    note = track[p]
                    velocity = track[p + 1]
                    p += 2
                    if high == 0x9 and velocity > 0:
                        note_ons += 1
                    else:
                        note_offs += 1
                elif high in (0xA, 0xB, 0xE):
                    p += 2
                elif high in (0xC, 0xD):
                    p += 1
                else:
                    raise RuntimeError(f"unsupported MIDI status {status:#x}")
        if not saw_end:
            raise RuntimeError("missing end-of-track")
    if tracks_seen != ntrks:
        raise RuntimeError("MIDI track count mismatch")
    if tempo_us is None:
        raise RuntimeError("MIDI tempo missing")
    return {"format": fmt, "division": division, "track_chunks": tracks_seen,
            "note_ons": note_ons, "note_offs": note_offs, "tempo_us": tempo_us}


# ---------------------------------------------------------------------------
# Build
# ---------------------------------------------------------------------------

def load_and_validate_scores() -> list[tuple[dict, dict, bytes]]:
    loaded = []
    seen_subjects = set()
    for spec in TRACK_SPECS:
        path = BASE / spec["score"]
        blob = path.read_bytes()
        score = json.loads(blob.decode("utf-8"))
        if score.get("subject") != spec["subject"] or score.get("score_id") != spec["slug"]:
            raise RuntimeError(f"score identity mismatch: {path.name}")
        if score.get("meter") != "4/4" or int(score.get("beats_per_bar", 0)) != 4:
            raise RuntimeError(f"meter mismatch: {path.name}")
        if int(score.get("bars", 0)) != 16 or int(score.get("loop_end_tick", 0)) != 30720:
            raise RuntimeError(f"bar/tick range mismatch: {path.name}")
        if int(score.get("ticks_per_quarter", 0)) != 480:
            raise RuntimeError(f"tick resolution mismatch: {path.name}")
        if int(score.get("loop_start_tick", -1)) != 0:
            raise RuntimeError(f"loop start mismatch: {path.name}")
        if not score.get("parts"):
            raise RuntimeError(f"no parts: {path.name}")
        for part in score["parts"]:
            if part["instrument"] not in score["instruments"]:
                raise RuntimeError(f"missing instrument config: {path.name}")
            for n in part["notes"]:
                if n["instrument"] != part["instrument"]:
                    raise RuntimeError(f"instrument mismatch: {path.name}")
                if not (0 <= int(n["start_tick"]) and int(n["duration_ticks"]) > 0):
                    raise RuntimeError(f"bad note timing: {path.name}")
                if int(n["start_tick"]) + int(n["duration_ticks"]) > 30720:
                    raise RuntimeError(f"note beyond loop: {path.name}")
                if not (1 <= int(n["velocity"]) <= 127):
                    raise RuntimeError(f"bad velocity: {path.name}")
        if spec["subject"] in seen_subjects:
            raise RuntimeError("duplicate subject")
        seen_subjects.add(spec["subject"])
        loaded.append((spec, score, blob))
    return loaded


def build() -> dict:
    if not BASE.is_dir():
        raise RuntimeError("package directory missing")
    attribution_path = BASE / ATTRIBUTION_NAME
    if not attribution_path.is_file():
        raise RuntimeError("attribution file missing")
    source_path = BASE / SOURCE_NAME
    source_hash = sha256_file(source_path)
    loaded = load_and_validate_scores()

    track_records = []
    total_wav_bytes = 0
    for spec, score, score_blob in loaded:
        midi_blob, midi_info = build_midi(score)
        midi_path = BASE / spec["midi"]
        midi_path.write_bytes(midi_blob)
        if parse_midi(midi_path.read_bytes())["note_ons"] != int(score["notes_total"]):
            raise RuntimeError(f"MIDI verification failed: {midi_path.name}")

        pcm, metrics = render_track(score, int(score["render"]["seed"]))
        wav_blob = wav_bytes(pcm, int(score["render"]["sample_rate_hz"]))
        wav_path = BASE / spec["wav"]
        wav_path.write_bytes(wav_blob)
        wav_info = validate_wav(wav_path.read_bytes(), metrics["frames"])

        if len(wav_blob) >= 8_000_000:
            raise RuntimeError(f"WAV exceeds 8 MB: {wav_path.name}")
        total_wav_bytes += len(wav_blob)
        midi_hash = sha256_bytes(midi_blob)
        wav_hash = sha256_bytes(wav_blob)
        if midi_hash != sha256_file(midi_path) or wav_hash != sha256_file(wav_path):
            raise RuntimeError("written file hash mismatch")

        record = {
            "subject": spec["subject"],
            "title": score["title"],
            "mood": score["mood"],
            "tempo_bpm": score["tempo_bpm"],
            "meter": score["meter"],
            "bars": score["bars"],
            "ticks_per_quarter": score["ticks_per_quarter"],
            "form": score["form"],
            "structure": score["structure"],
            "note_counts": score["note_counts"],
            "notes_total": score["notes_total"],
            "max_simultaneous_score_notes": score["max_simultaneous_score_notes"],
            "render_seed": score["render"]["seed"],
            "loop": {
                "start_tick": score["loop_start_tick"],
                "end_tick": score["loop_end_tick"],
                "start_frame": 0,
                "end_frame": metrics["frames"],
                "end_seconds": metrics["duration_seconds"],
            },
            "files": {
                "score": {"path": spec["score"], "sha256": sha256_bytes(score_blob),
                          "bytes": len(score_blob)},
                "midi": {"path": spec["midi"], "sha256": midi_hash, "bytes": len(midi_blob)},
                "wav": {"path": spec["wav"], "sha256": wav_hash, "bytes": len(wav_blob)},
            },
            "midi": midi_info,
            "wav": wav_info,
            "metrics": metrics,
            "technical_checks": {
                "peak_at_or_below_0_85": metrics["peak_linear"] <= 0.85,
                "no_clipped_samples": metrics["clipped_samples"] == 0,
                "dc_offset_within_1e5": (
                    abs(metrics["dc_offset_left"]) <= 1.0e-5
                    and abs(metrics["dc_offset_right"]) <= 1.0e-5
                ),
                "healthy_audible_rms": metrics["rms_dbfs"] >= -24.0,
                "loop_boundary_zeroed": metrics["loop_boundary_step_max_abs"] == 0.0,
                "wav_under_8MB": len(wav_blob) < 8_000_000,
            },
        }
        track_records.append(record)
        print(
            f"rendered {spec['subject']}: {metrics['duration_seconds']:.3f}s, "
            f"peak {metrics['peak_dbfs']:.2f} dBFS, RMS {metrics['rms_dbfs']:.2f} dBFS, "
            f"seam {metrics['loop_boundary_step_max_abs']:.1f}, {len(wav_blob)} bytes"
        )

    if total_wav_bytes > 24_000_000:
        raise RuntimeError("total WAV bytes exceed 24 MB")

    manifest = {
        "schema": "worlds-between.themed-music-package.v1",
        "package_id": PACKAGE_ID,
        "project": "Worlds Between",
        "task": TASK,
        "created_utc": CREATED_UTC,
        "package_path": "game/assets/music/themed-v01",
        "generation": {
            "model": GENERATION_MODEL,
            "assistance": "score and render-source generation",
            "coordinated_inspected_by": COORDINATED_INSPECTED_BY,
            "authorship_claim": "none; no human composer or human authorship is claimed",
            "attribution_file": {
                "path": ATTRIBUTION_NAME,
                "sha256": sha256_file(attribution_path),
            },
        },
        "source": {
            "path": SOURCE_NAME,
            "sha256": source_hash,
            "language": "Python (standard library + NumPy)",
            "roles": ["score loader", "MIDI writer", "NumPy WAV renderer", "hash manifest"],
        },
        "tracks": track_records,
        "totals": {
            "track_count": len(track_records),
            "wav_bytes": total_wav_bytes,
            "wav_mib": round(total_wav_bytes / (1024.0 * 1024.0), 6),
            "wav_limit_bytes": 24_000_000,
            "individual_wav_limit_bytes": 8_000_000,
            "separate_files": True,
            "combined_medley": False,
        },
        "provenance": {
            "origin": "Fixed-score composition for Worlds Between; four distinct themes.",
            "generation": (
                "Score data and render source generated with DeepSeek V4.1 Flash "
                "assistance; coordinated/inspected by Codex."
            ),
            "authorship_claim": "none; no human composer or human authorship is claimed",
            "observed_inputs": {
                "external_samples_supplied": False,
                "external_melodic_references_supplied": False,
                "scope": (
                    "generation-run inputs only; not a copyright-clearance guarantee "
                    "or legal assurance"
                ),
            },
            "legal_clearance": (
                "not assessed; no copyright-clearance guarantee or legal assurance is made"
            ),
            "network_or_api": "none",
            "singing": "none",
            "new_installs": "none",
            "randomness": "none; deterministic integer-hash percussion noise and fixed seeds only",
            "runtime_random": False,
            "renderer_environment": (
                f"CPython {platform.python_version()}, NumPy {np.__version__}, "
                "standard library only; Pillow not used"
            ),
            "sample_rate_hz": 24000,
            "bit_depth": 16,
            "channels": 2,
            "loop_treatment": (
                "Per-note release envelopes are rendered through a 5.0 s tail; the tail is "
                "wrapped into the head, then a 3 ms raised-cosine endpoint de-click is applied. "
                "No structural master fadeout is used."
            ),
            "dynamic_treatment": "Section gain automation (0.30 s smoothing) with varied velocities and pan.",
        },
        "rebuild": {
            "command": f"python {SOURCE_NAME} --build",
            "deterministic": True,
            "notes": "Fixed score bytes, fixed seeds, integer-hash noise, no clock-derived output metadata.",
            "source_sha256": source_hash,
        },
        "limitations": {
            "listened": False,
            "creator_approved": False,
            "runtime_integrated": False,
            "technical_metrics_are_not_a_listening_claim": True,
            "quality_claim": "none",
        },
    }

    manifest_blob = (json.dumps(manifest, indent=2, ensure_ascii=True) + "\n").encode("utf-8")
    (BASE / MANIFEST_NAME).write_bytes(manifest_blob)

    # Final post-write integrity check of every requested artifact class.
    for rec, (spec, score, score_blob) in zip(track_records, loaded):
        if sha256_file(BASE / spec["score"]) != rec["files"]["score"]["sha256"]:
            raise RuntimeError("score hash verification failed")
        if sha256_file(BASE / spec["midi"]) != rec["files"]["midi"]["sha256"]:
            raise RuntimeError("MIDI hash verification failed")
        if sha256_file(BASE / spec["wav"]) != rec["files"]["wav"]["sha256"]:
            raise RuntimeError("WAV hash verification failed")
    if sha256_file(BASE / ATTRIBUTION_NAME) != manifest["generation"]["attribution_file"]["sha256"]:
        raise RuntimeError("attribution hash verification failed")
    if sha256_file(source_path) != manifest["source"]["sha256"]:
        raise RuntimeError("source hash verification failed")

    return manifest


def main() -> int:
    parser = argparse.ArgumentParser(description="Worlds Between themed music deterministic build")
    parser.add_argument("--build", action="store_true", help="render MIDI/WAV and write the manifest")
    args = parser.parse_args()
    if not args.build:
        parser.error("--build is required; this package is built directly, not by a runtime loader")
    manifest = build()
    print(f"wrote {BASE / MANIFEST_NAME}")
    print(f"tracks={manifest['totals']['track_count']} wav_bytes={manifest['totals']['wav_bytes']}")
    print("technical build checks passed; no listening or approval claim is made")
    return 0


if __name__ == "__main__":
    sys.exit(main())
