"""Patrol battle animation pilot v01 (UNAPPROVED): run the real-time motion-capture harness, encode MP4s, write a report.

One bounded checked-runner invocation (windowed, isolated APPDATA/LOCALAPPDATA, no diagnostic filtering), then one
ffmpeg libx264 encode per clip. The MP4 uses each captured viewport frame exactly once with its measured wall-clock
duration (concat demuxer, passthrough VFR): no duplicated, dropped or interpolated frames. Source hashes are frozen at
start and rechecked at end. Usage: python -I <this>
"""
import hashlib, json, os, shutil, subprocess, sys
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PRIMARY = ROOT.parents[2]
STAMP = 'v01_20261019-200500-5b7c2e19'
SLUG = 'rpg-2-star-ocean-the-second_patrol_motion-'
STOP = PRIMARY / 'work/dual01/control/rpg-2-star-ocean-the-second_dual-provider_global-stop_v01_20261019-001423-861097ca.json'
GODOT = PRIMARY / 'work/tooling/godot-4-7-2/Godot_v4.7.2-stable_win64_console.exe'
RUNNER = ROOT / 'tools/rpg-2-star-ocean-the-second_godot_checked-runner_v01_20261018-203400-f74ac6d1.py'
HARNESS = ROOT / f'tools/{SLUG}capture-harness_{STAMP}.gd'
OUT = ROOT / 'outputs/patrol-motion-v01'
PKG = 'game/assets/enemies/patrol-anim-v01/'
BOUND = ['game/scripts/battle_arena.gd', PKG + 'rpg-2-star-ocean-the-second_patrol_battle-animation-loader_v01_20261019-194007-a4b10a85.gd',
         PKG + 'rpg-2-star-ocean-the-second_patrol_battle-animation-runtime-package_v01_20261019-194007-a4b10a85.json',
         PKG + 'rpg-2-star-ocean-the-second_patrol_battle-animation-strip_v01_20261019-194007-a4b10a85.png',
         PKG + 'rpg-2-star-ocean-the-second_patrol_battle-animation-manifest_v01_20261019-194007-a4b10a85.json',
         'tools/' + HARNESS.name, 'tools/' + Path(__file__).name]
STATES = ['idle', 'move', 'windup', 'strike', 'hit', 'defeat']


def ext(p):
    return '\\\\?\\' + str(Path(p).resolve())


def sha_file(p):
    with open(ext(p), 'rb') as f:
        return hashlib.sha256(f.read()).hexdigest()


def hashes():
    return {p: sha_file(ROOT / p) for p in BOUND}


def stop_check(where):
    if STOP.exists():
        raise SystemExit(f'GLOBAL STOP present before {where}; stopped')


def main():
    stop_check('capture')
    OUT.mkdir(parents=True, exist_ok=True)
    before = hashes()
    head = subprocess.run(['git', 'rev-parse', 'HEAD'], cwd=ROOT, capture_output=True, text=True, encoding='utf-8').stdout.strip()
    env = dict(os.environ)
    run_id = datetime.now().strftime('%H%M%S')
    for k in ('APPDATA', 'LOCALAPPDATA'):
        # fresh per run: reusing a previous run's isolated shader cache gave shader_gles3 init ERRORs (attempt 3)
        d = OUT / f"{'app' if k == 'APPDATA' else 'local'}-{run_id}"
        d.mkdir()
        env[k] = str(d)
    env.pop('ANTHROPIC_API_KEY', None)
    # The checked runner opens its log exclusively, so each run gets its own; stale outputs of this tool are cleared first.
    log = OUT / f"{SLUG}capture-runner-log-{datetime.now().strftime('%H%M%S')}_{STAMP}.log"
    for old in list(OUT.glob(f'{SLUG}*.mp4')) + list(OUT.glob(f'{SLUG}concat-*.txt')) + list(OUT.glob(f'{SLUG}capture-raw_*.json')):
        old.unlink()
    if (OUT / 'frames').exists():
        shutil.rmtree(ext(OUT / 'frames'))
    cmd = [sys.executable, '-I', str(RUNNER), '--timeout', '300', '--expect', 'PATROL_MOTION_CAPTURE OK', '--log', str(log), '--',
           str(GODOT), '--path', str(ROOT / 'game'), '--resolution', '640x360', '-s', str(HARNESS), '--',
           '--patrol-battle-animation-pilot', f'--capture-dir={OUT}']
    t0 = datetime.now()
    run = subprocess.run(cmd, env=env, capture_output=True, text=True, encoding='utf-8', errors='replace')
    runner = {'exit': run.returncode, 'seconds': (datetime.now() - t0).total_seconds(), 'log': log.relative_to(ROOT).as_posix(), 'stdout': run.stdout[-2000:], 'stderr': run.stderr[-2000:]}
    raw_path = OUT / f'rpg-2-star-ocean-the-second_patrol_motion-capture-raw_{STAMP}.json'
    failures = []
    if run.returncode != 0 or 'CHECKED_RUN PASS' not in run.stdout:
        failures.append(f'checked runner exit {run.returncode}')
    if not raw_path.exists():
        failures.append('raw capture report missing')
        return finish(before, head, runner, None, [], failures)
    raw = json.loads(raw_path.read_text(encoding='utf-8'))
    failures += ['harness: ' + f for f in raw.get('failures', [])]
    clips = []
    for clip in raw['clips']:
        stop_check('encode ' + clip['name'])
        rows = clip['rows']
        lst = OUT / f"{SLUG}concat-{clip['name']}_{STAMP}.txt"
        lines = ['ffconcat version 1.0']
        for i, r in enumerate(rows):
            dur = (rows[i + 1]['t'] - r['t']) if i + 1 < len(rows) else r['wallDelta']
            # per-file image2 framerate 1e6 keeps microsecond timestamps; no trailing duplicate entry (attempt 1 added one
            # extra frame and its default 1/25 timebase quantized the timestamps).
            lines += [f"file '{(OUT / r['file']).as_posix()}'", 'option framerate 1000000', f'duration {dur:.6f}']
        lst.write_text('\n'.join(lines) + '\n', encoding='utf-8', newline='\n')
        mp4 = OUT / f"rpg-2-star-ocean-the-second_patrol_motion-{clip['name']}-normal1x-640_{STAMP}.mp4"
        enc = ['ffmpeg', '-v', 'error', '-y', '-f', 'concat', '-safe', '0', '-i', str(lst), '-fps_mode', 'passthrough',
               '-c:v', 'libx264', '-preset', 'slow', '-crf', '12', '-pix_fmt', 'yuv420p', '-video_track_timescale', '1000000',
               '-movflags', '+faststart', str(mp4)]
        e = subprocess.run(enc, capture_output=True, text=True, encoding='utf-8', errors='replace')
        if e.returncode != 0 or e.stderr.strip():
            failures.append(f"ffmpeg {clip['name']}: {e.returncode} {e.stderr.strip()[:300]}")
            continue
        probe = json.loads(subprocess.run(['ffprobe', '-v', 'error', '-count_frames', '-select_streams', 'v:0', '-show_entries',
                                           'stream=codec_name,profile,pix_fmt,width,height,r_frame_rate,avg_frame_rate,time_base,nb_frames,nb_read_frames,duration:format=duration,size:format_tags',
                                           '-of', 'json', str(mp4)], capture_output=True, text=True, encoding='utf-8').stdout)
        pts = subprocess.run(['ffprobe', '-v', 'error', '-select_streams', 'v:0', '-show_entries', 'packet=pts_time', '-of', 'csv=p=0', str(mp4)],
                             capture_output=True, text=True, encoding='utf-8').stdout.split()
        pts = sorted(float(x) for x in pts if x.strip())
        gaps = [b - a for a, b in zip(pts, pts[1:])]
        want = [rows[i + 1]['t'] - rows[i]['t'] for i in range(len(rows) - 1)]
        if len(pts) != len(rows) or max(abs(g - w) for g, w in zip(gaps, want)) > 0.0001:
            failures.append(f"{clip['name']}: MP4 pts do not reproduce captured frame times")
        deltas = [r['processDelta'] for r in rows[1:]]
        wall = [r['wallDelta'] for r in rows[1:]]
        st = probe['streams'][0]
        nread = int(st.get('nb_read_frames', -1))
        if nread != len(rows):
            failures.append(f"{clip['name']}: MP4 frames {nread} != captured {len(rows)}")
        if (st['width'], st['height']) != (640, 360):
            failures.append(f"{clip['name']}: MP4 size {st['width']}x{st['height']}")
        span = rows[-1]['t'] - rows[0]['t'] + rows[-1]['wallDelta']
        if abs(float(probe['format']['duration']) - span) > 0.05:
            failures.append(f"{clip['name']}: MP4 duration {probe['format']['duration']} vs captured span {span:.3f}")
        seen = {s: n for s, n in clip['statesFrameCount'].items()}
        first = {}
        for r in rows:
            first.setdefault(r['state'], r['t'])
        clips.append({'name': clip['name'], 'kind': clip['kind'], 'language': clip['language'], 'durabilityHold': clip['durabilityHold'],
                      'holdWrites': clip['holdWrites'], 'label': 'TEST-ONLY durability-held (Patrol HP floored at 40 until 2 strikes)' if clip['durabilityHold'] else 'normal unmodified combat (one battle_auto key input; no state/HP writes)',
                      'mp4': mp4.relative_to(ROOT).as_posix(), 'mp4Sha256': sha_file(mp4), 'concatList': lst.relative_to(ROOT).as_posix(), 'concatSha256Bytes': sha_file(lst),
                      'frameDir': f"outputs/patrol-motion-v01/frames/{clip['name']}", 'frames': len(rows),
                      'frameSha256ListSha256': hashlib.sha256('\n'.join(r['sha256'] for r in rows).encode()).hexdigest(),
                      'capturedSpanSeconds': round(span, 6), 'autoPressedAt': clip['autoPressedAt'], 'battleFinishedAt': clip['finishedAt'],
                      'statesFrameCount': seen, 'stateFirstSeenSeconds': first, 'statesMissing': [s for s in STATES if s not in seen],
                      'processDelta': {'min': min(deltas), 'max': max(deltas), 'mean': sum(deltas) / len(deltas)},
                      'wallDelta': {'min': min(wall), 'max': max(wall), 'mean': sum(wall) / len(wall), 'over25ms': sum(1 for w in wall if w > 0.025)},
                      'effectiveCaptureFps': round((len(rows) - 1) / (rows[-1]['t'] - rows[0]['t']), 3),
                      'mp4Probe': probe, 'mp4PtsGap': {'min': min(gaps), 'max': max(gaps), 'maxErrorVsCapture': max(abs(g - w) for g, w in zip(gaps, want))} if gaps else None,
                      'encoder': ' '.join(enc[:-1]) + ' <mp4>'})
    for lang in ('en', 'zh'):
        union = set()
        for c in clips:
            if c['language'] == lang:
                union |= set(c['statesFrameCount'])
        missing = [s for s in STATES if s not in union]
        if missing:
            failures.append(f'{lang}: states never captured {missing}')
    return finish(before, head, runner, raw, clips, failures)


def finish(before, head, runner, raw, clips, failures):
    after = hashes()
    changed = [p for p in BOUND if before[p] != after[p]]
    if changed:
        failures.append(f'bound source changed during run: {changed} (rerun affected probe)')
    ffv = subprocess.run(['ffmpeg', '-version'], capture_output=True, text=True, encoding='utf-8').stdout.splitlines()[0]
    report = {'stamp': STAMP, 'status': 'UNAPPROVED technical evidence for an off-by-default candidate; not art acceptance',
              'gitHead': head, 'hashNormalization': 'sha256-bytes of working files (no text normalization)',
              'boundSha256AtStart': before, 'boundSha256AtEnd': after, 'runner': runner, 'ffmpeg': ffv,
              'engine': raw.get('engine') if raw else None, 'harnessSourceSha256': raw.get('sourceSha256AtStart') if raw else None,
              'clips': clips, 'failures': failures, 'result': 'PASS' if not failures else 'FAIL'}
    path = OUT / f'{SLUG}report_{STAMP}.json'
    path.write_text(json.dumps(report, indent=1, ensure_ascii=False) + '\n', encoding='utf-8', newline='\n')
    print(('PATROL_MOTION_RUN PASS' if not failures else 'PATROL_MOTION_RUN FAIL') + f' clips={len(clips)} report={path.name}')
    for f in failures:
        print('FAIL', f)
    return 0 if not failures else 1


if __name__ == '__main__':
    sys.exit(main())
