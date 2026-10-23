"""Read actual Godot AVI PCM output. No artistic/listening verdict is inferred."""
import argparse
import hashlib
import json
from pathlib import Path
import struct
import wave
import numpy as np


def chunks(data, start, end):
    at = start
    while at + 8 <= end:
        kind = data[at:at + 4]
        count = struct.unpack_from('<I', data, at + 4)[0]
        stop = at + 8 + count
        if stop > end:
            raise ValueError('Truncated RIFF chunk')
        yield kind, at + 8, stop
        at = stop + (count & 1)


def read_avi(path):
    data = Path(path).read_bytes()
    if data[:4] != b'RIFF' or data[8:12] != b'AVI ':
        raise ValueError('Not an AVI RIFF capture')
    size = struct.unpack_from('<I', data, 4)[0] + 8
    if size > len(data):
        raise ValueError('Incomplete AVI')
    formats, audio_chunks, frame_jpegs = [], {}, []

    def walk(start, end, inside_movie=False):
        for kind, begin, stop in chunks(data, start, end):
            if kind == b'LIST':
                list_kind = data[begin:begin + 4]
                if list_kind == b'strl':
                    fields = {k: data[b:e] for k, b, e in chunks(data, begin + 4, stop)}
                    if fields.get(b'strh', b'')[:4] == b'auds':
                        formats.append(struct.unpack_from('<HHIIHH', fields[b'strf']))
                else:
                    walk(begin + 4, stop, inside_movie or list_kind == b'movi')
            elif inside_movie and kind.endswith(b'wb'):
                audio_chunks.setdefault(kind, []).append(data[begin:stop])
            elif inside_movie and kind.endswith(b'dc') and not frame_jpegs:
                frame_jpegs.append(data[begin:stop])
    walk(12, size)
    if len(formats) != 1 or len(audio_chunks) != 1:
        raise ValueError('Expected exactly one audio stream')
    fmt, channels, rate, byte_rate, block_align, bits = formats[0]
    if fmt != 1 or bits not in (16, 32) or channels not in (1, 2):
        raise ValueError(f'Unsupported PCM format: {formats[0]}')
    raw = b''.join(next(iter(audio_chunks.values())))
    if block_align != channels * bits // 8 or byte_rate != rate * block_align or len(raw) % block_align:
        raise ValueError('Inconsistent PCM alignment')
    pcm = np.frombuffer(raw, dtype='<i2' if bits == 16 else '<i4').reshape(-1, channels)
    values = pcm.astype(np.float64) / float(2 ** (bits - 1))
    return values, raw, {'channels': channels, 'rate': rate, 'bits': bits,
                         'frames': len(pcm), 'seconds': len(pcm) / rate,
                         'aviSha256': hashlib.sha256(data).hexdigest()}, frame_jpegs


def stats(samples):
    if not samples.size:
        raise ValueError('Empty segment')
    return {'samplesPerChannel': len(samples), 'peak': float(np.max(np.abs(samples))),
            'rms': float(np.sqrt(np.mean(samples ** 2))),
            'dc': [float(x) for x in samples.mean(axis=0)],
            'fullScaleSamples': int(np.sum(np.abs(samples) >= 0.9999)),
            'allZero': bool(np.all(samples == 0))}


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--avi', type=Path, required=True)
    p.add_argument('--wav', type=Path, required=True)
    p.add_argument('--output', type=Path, required=True)
    args = p.parse_args()
    for out in (args.wav, args.output):
        if out.exists():
            raise SystemExit('Refusing to overwrite evidence: ' + str(out))
    samples, raw, info, _ = read_avi(args.avi)
    # Preserve the actual movie PCM without amplification or resampling.
    with wave.open(str(args.wav), 'wb') as w:
        w.setnchannels(info['channels'])
        w.setsampwidth(info['bits'] // 8)
        w.setframerate(info['rate'])
        w.writeframes(raw)
    info.update(stats(samples))
    info.update(wavSha256=hashlib.sha256(args.wav.read_bytes()).hexdigest(),
                toolSha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
                listeningVerdict=False, artisticallyApproved=False,
                fixtureAudioNotOrdinaryGameplay=True)
    args.output.write_text(json.dumps(info, indent=2) + '\n', encoding='utf-8')
    print(json.dumps(info))


if __name__ == '__main__':
    main()
