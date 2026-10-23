"""Read actual Godot AVI PCM output. No artistic/listening verdict is inferred."""
import argparse
import hashlib
import json
from pathlib import Path
import struct
import wave
import numpy as np


def read_avi(path):
    # Use the installed media decoder instead of hand-accepting an unusual RIFF
    # length declaration. Decoder diagnostics are retained; errors fail closed.
    import shutil
    import subprocess
    ffmpeg, ffprobe = shutil.which('ffmpeg'), shutil.which('ffprobe')
    if not ffmpeg or not ffprobe:
        raise RuntimeError('Installed ffmpeg and ffprobe are required')
    probe = subprocess.run([ffprobe, '-v', 'warning', '-show_streams', '-of', 'json', str(path)], capture_output=True, timeout=30)
    if probe.returncode:
        raise RuntimeError(probe.stderr.decode('utf-8', 'replace'))
    streams = json.loads(probe.stdout)['streams']
    audio = [x for x in streams if x.get('codec_type') == 'audio']
    if len(audio) != 1 or audio[0]['codec_name'] not in ('pcm_s16le', 'pcm_s32le'):
        raise ValueError('Expected one uncompressed integer PCM stream')
    channels, rate = int(audio[0]['channels']), int(audio[0]['sample_rate'])
    if channels not in (1, 2) or not 8000 <= rate <= 192000:
        raise ValueError('Unexpected channel count or sample rate')
    command = [ffmpeg, '-v', 'warning', '-xerror', '-i', str(path), '-map', '0:a:0', '-f', 's32le', '-acodec', 'pcm_s32le', 'pipe:1']
    decoded = subprocess.run(command, capture_output=True, timeout=60)
    if decoded.returncode:
        raise RuntimeError(decoded.stderr.decode('utf-8', 'replace'))
    raw = decoded.stdout
    if not raw or len(raw) % (channels * 4):
        raise ValueError('Empty or misaligned decoded PCM')
    pcm = np.frombuffer(raw, dtype='<i4').reshape(-1, channels)
    values = pcm.astype(np.float64) / float(2 ** 31)
    avi = Path(path).read_bytes()
    declared = struct.unpack_from('<I', avi, 4)[0] + 8 if avi[:4] == b'RIFF' else None
    return values, raw, {'channels': channels, 'rate': rate, 'bits': 32,
        'sourceCodec': audio[0]['codec_name'], 'frames': len(pcm), 'seconds': len(pcm) / rate,
        'aviSha256': hashlib.sha256(avi).hexdigest(), 'aviActualBytes': len(avi),
        'aviRiffDeclaredBytes': declared, 'aviRiffDeclarationExact': declared == len(avi),
        'probeDiagnostics': probe.stderr.decode('utf-8', 'replace'),
        'decoderDiagnostics': decoded.stderr.decode('utf-8', 'replace'),
        'decoderCommand': command, 'conversion': 'integer PCM to signed32; original rate/channels retained'}, []


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
