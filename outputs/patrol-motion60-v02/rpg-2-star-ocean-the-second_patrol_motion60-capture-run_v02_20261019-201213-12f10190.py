"""Patrol battle animation pilot v01 (UNAPPROVED): 60 fps real-time capture run, MP4 encode, critical stills, report (v02).

Adapted from tools/rpg-2-star-ocean-the-second_patrol_motion-capture-run_v01_20261019-200500-5b7c2e19.py (frozen, not
edited). Changes: the v02 harness caps Engine.max_fps at 60 (capture harness only); every run gets its own run id, fresh
APPDATA/LOCALAPPDATA and an ignored per-frame cache under cache/<run>/; nothing from an earlier run is deleted or reused;
row 0 (scene-entry sample) is reported separately from post-start frames; one strike/hit/defeat still per language is
copied byte-exact from the captured frames. One bounded checked-runner invocation (windowed, unfiltered), then one
ffmpeg libx264 encode per clip using each captured frame exactly once at its measured wall-clock time (no duplicate,
drop or interpolation; nothing is derived from the v01 240 Hz videos). Usage: <python> -I <this>
"""
import hashlib, json, os, secrets, shutil, statistics, subprocess, sys
from datetime import datetime, timezone
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
PRIMARY = ROOT.parents[2]
TOOL_STAMP = 'v02_20261019-201213-12f10190'
SLUG = 'rpg-2-star-ocean-the-second_patrol_motion60-'
STOP = PRIMARY / 'work/dual01/control/rpg-2-star-ocean-the-second_dual-provider_global-stop_v01_20261019-001423-861097ca.json'
GODOT = PRIMARY / 'work/tooling/godot-4-7-2/Godot_v4.7.2-stable_win64_console.exe'
RUNNER = ROOT / 'tools/rpg-2-star-ocean-the-second_godot_checked-runner_v01_20261018-203400-f74ac6d1.py'
HARNESS = HERE / f'{SLUG}capture-harness_{TOOL_STAMP}.gd'
OUT = HERE
PKG = 'game/assets/enemies/patrol-anim-v01/rpg-2-star-ocean-the-second_patrol_battle-animation-'
# Frozen sources: must be byte-identical to the versions root validated (sha256-bytes, no normalization).
FROZEN = {
    'game/scripts/battle_arena.gd': '799308e292b0cfebf3406aa30b283cd4ab595397c5a027e7edd0a7085355d3d2',
    PKG + 'loader_v01_20261019-194007-a4b10a85.gd': 'f051d5938afa9f6208b1ddebd1eb263c11f82451585b28ec980312c052dda853',
    PKG + 'runtime-package_v01_20261019-194007-a4b10a85.json': '075a438e13d80b86b1b69b5d80c6ba14678cb464d68c8dfb5e9eae7b10f8f46a',
    PKG + 'strip_v01_20261019-194007-a4b10a85.png': 'e91f4373fb8f4f4b1ae3fbe0db966e8f807614863a5dc62ce8b861667ed99fa0',
    PKG + 'manifest_v01_20261019-194007-a4b10a85.json': '3f34afc6f5aa13e138c6dc72d82ad6fab6cb7d19704e5606c46eb5fe1bb3d877',
    'tools/rpg-2-star-ocean-the-second_patrol_motion-capture-harness_v01_20261019-200500-5b7c2e19.gd': 'af3fd15c53afcedb0138f0fd3ecb6d06428238feec437dab316cf2a3c291b9ec',
    'tools/rpg-2-star-ocean-the-second_patrol_motion-capture-run_v01_20261019-200500-5b7c2e19.py': 'a48b93a5d29869c2de0c002d636cf99633c3d6bbdd5e2f13c4fa344828768cb0',
}
V02_TOOLS = [HARNESS.relative_to(ROOT).as_posix(), Path(__file__).resolve().relative_to(ROOT).as_posix()]
STATES = ['idle', 'move', 'windup', 'strike', 'hit', 'defeat']
# One still per language for each critical state, taken from the clip where that state occurs (strike never occurs in
# normal unmodified play, so it comes from the labelled durability-held clip).
CRITICAL = [('strike', 'held'), ('hit', 'normal'), ('defeat', 'normal')]
TARGET = 1.0 / 60.0


def ext(p):
    return '\\\\?\\' + str(Path(p).resolve())


def sha_file(p):
    with open(ext(p), 'rb') as f:
        return hashlib.sha256(f.read()).hexdigest()


def hashes():
    return {p: sha_file(ROOT / p) for p in list(FROZEN) + V02_TOOLS}


def stop_check(where):
    if STOP.exists():
        raise SystemExit(f'GLOBAL STOP present before {where}; stopped')


def stats(values):
    v = sorted(values)
    q = lambda f: v[min(len(v) - 1, int(round(f * (len(v) - 1))))]
    return {'n': len(v), 'min': v[0], 'p50': q(0.5), 'p95': q(0.95), 'p99': q(0.99), 'max': v[-1], 'mean': round(sum(v) / len(v), 6),
            'over20ms': sum(1 for x in v if x > 0.020), 'over25ms': sum(1 for x in v if x > 0.025), 'over34ms': sum(1 for x in v if x > 0.034)}


def main():
    stop_check('capture')
    now = datetime.now().astimezone()
    run_stamp = f"v02_{now.strftime('%Y%m%d-%H%M%S')}-{secrets.token_hex(4)}"
    run_short = 'r' + now.strftime('%H%M%S')
    cache = OUT / 'cache' / run_short
    cache.mkdir(parents=True, exist_ok=False)
    before = hashes()
    head = subprocess.run(['git', 'rev-parse', 'HEAD'], cwd=ROOT, capture_output=True, text=True, encoding='utf-8').stdout.strip()
    env = dict(os.environ)
    for k, d in (('APPDATA', cache / 'app'), ('LOCALAPPDATA', cache / 'local')):
        d.mkdir()  # fresh per run (v01 attempt 3: a reused isolated shader cache produced shader_gles3 init ERRORs)
        env[k] = str(d)
    env.pop('ANTHROPIC_API_KEY', None)
    log = OUT / f'{SLUG}runner-log_{run_stamp}.log'
    raw_path = OUT / f'{SLUG}capture-raw_{run_stamp}.json'
    cmd = [sys.executable, '-I', str(RUNNER), '--timeout', '300', '--expect', 'PATROL_MOTION60_CAPTURE OK', '--log', str(log), '--',
           str(GODOT), '--path', str(ROOT / 'game'), '--resolution', '640x360', '-s', str(HARNESS), '--',
           '--patrol-battle-animation-pilot', f'--cache-dir={cache}', f'--raw-path={raw_path}']
    t0 = datetime.now()
    run = subprocess.run(cmd, env=env, capture_output=True, text=True, encoding='utf-8', errors='replace', timeout=420)
    runner = {'exit': run.returncode, 'seconds': (datetime.now() - t0).total_seconds(), 'log': log.relative_to(ROOT).as_posix(),
              'logSha256': sha_file(log) if log.exists() else None, 'stdout': run.stdout[-2500:], 'stderr': run.stderr[-2000:],
              'command': [str(c) for c in cmd]}
    failures = []
    for p, want in FROZEN.items():
        if before[p] != want:
            failures.append(f'frozen source differs from validated bytes: {p} {before[p]} != {want}')
    if run.returncode != 0 or 'CHECKED_RUN PASS' not in run.stdout:
        failures.append(f'checked runner exit {run.returncode} / no CHECKED_RUN PASS')
    if not raw_path.exists():
        failures.append('raw capture report missing')
        return finish(run_stamp, cache, before, head, runner, None, [], [], failures)
    raw = json.loads(raw_path.read_text(encoding='utf-8'))
    failures += ['harness: ' + f for f in raw.get('failures', [])]
    eng = raw.get('engine', {})
    if eng.get('maxFps') != 60 or raw.get('engineMaxFpsAtEnd') != 60:
        failures.append(f"Engine.max_fps not 60 during capture: {eng.get('maxFps')} / end {raw.get('engineMaxFpsAtEnd')}")
    clips = []
    for clip in raw['clips']:
        stop_check('encode ' + clip['name'])
        rows = clip['rows']
        if any(r.get('maxFps') != 60 for r in rows):
            failures.append(f"{clip['name']}: a row was captured with max_fps != 60")
        lst = cache / f"concat-{clip['name']}.txt"
        lines = ['ffconcat version 1.0']
        for i, r in enumerate(rows):
            dur = (rows[i + 1]['t'] - r['t']) if i + 1 < len(rows) else r['wallDelta']
            lines += [f"file '{(cache / r['file']).as_posix()}'", 'option framerate 1000000', f'duration {dur:.6f}']
        lst.write_text('\n'.join(lines) + '\n', encoding='utf-8', newline='\n')
        mp4 = OUT / f"{SLUG}{clip['name']}-normal1x-640_{run_stamp}.mp4"
        enc = ['ffmpeg', '-v', 'error', '-y', '-f', 'concat', '-safe', '0', '-i', str(lst), '-fps_mode', 'passthrough',
               '-c:v', 'libx264', '-preset', 'slow', '-crf', '12', '-profile:v', 'high', '-level:v', '4.0', '-pix_fmt', 'yuv420p',
               '-video_track_timescale', '1000000', '-movflags', '+faststart', str(mp4)]
        e = subprocess.run(enc, capture_output=True, text=True, encoding='utf-8', errors='replace', timeout=240)
        if e.returncode != 0 or e.stderr.strip():
            failures.append(f"ffmpeg {clip['name']}: {e.returncode} {e.stderr.strip()[:300]}")
            continue
        probe = json.loads(subprocess.run(['ffprobe', '-v', 'error', '-count_frames', '-select_streams', 'v:0', '-show_entries',
                                           'stream=codec_name,profile,level,pix_fmt,width,height,r_frame_rate,avg_frame_rate,time_base,nb_frames,nb_read_frames,duration:format=duration,size,format_name:format_tags',
                                           '-of', 'json', str(mp4)], capture_output=True, text=True, encoding='utf-8').stdout)
        pts = subprocess.run(['ffprobe', '-v', 'error', '-select_streams', 'v:0', '-show_entries', 'packet=pts_time', '-of', 'csv=p=0', str(mp4)],
                             capture_output=True, text=True, encoding='utf-8').stdout.split()
        pts = sorted(float(x) for x in pts if x.strip())
        gaps = [b - a for a, b in zip(pts, pts[1:])]
        want = [rows[i + 1]['t'] - rows[i]['t'] for i in range(len(rows) - 1)]
        pts_err = max(abs(g - w) for g, w in zip(gaps, want)) if gaps else None
        if len(pts) != len(rows) or pts_err is None or pts_err > 0.0001:
            failures.append(f"{clip['name']}: MP4 pts do not reproduce captured frame times")
        st = probe['streams'][0]
        nread = int(st.get('nb_read_frames', -1))
        if nread != len(rows):
            failures.append(f"{clip['name']}: MP4 frames {nread} != captured {len(rows)}")
        if (st['width'], st['height']) != (640, 360):
            failures.append(f"{clip['name']}: MP4 size {st['width']}x{st['height']}")
        span = rows[-1]['t'] - rows[0]['t'] + rows[-1]['wallDelta']
        if abs(float(probe['format']['duration']) - span) > 0.05:
            failures.append(f"{clip['name']}: MP4 duration {probe['format']['duration']} vs captured span {span:.3f}")
        post = rows[1:]
        post_wall = stats([r['wallDelta'] for r in post])
        post_proc = stats([r['processDelta'] for r in post])
        post_fps = round((len(post) - 1) / (post[-1]['t'] - post[0]['t']), 3)
        # 60 fps gate on post-start frames only: median frame interval within 1.5 ms of 1/60 s and mean rate 57..61 fps.
        if not (abs(post_wall['p50'] - TARGET) <= 0.0015 and 57.0 <= post_fps <= 61.0):
            failures.append(f"{clip['name']}: post-start capture not ~60 fps (p50 wall {post_wall['p50']}, rate {post_fps})")
        first = {}
        runs = {}
        for i, r in enumerate(rows):
            first.setdefault(r['state'], r['t'])
            if r['state'] not in runs:
                j = i
                while j + 1 < len(rows) and rows[j + 1]['state'] == r['state']:
                    j += 1
                runs[r['state']] = (i, j)
        clips.append({'name': clip['name'], 'kind': clip['kind'], 'language': clip['language'], 'durabilityHold': clip['durabilityHold'],
                      'holdWrites': clip['holdWrites'], 'label': 'TEST-ONLY durability-held supplement (Patrol HP floored at 40 until 2 strikes; not normal gameplay)' if clip['durabilityHold'] else 'normal unmodified combat (one battle_auto key input; no state/HP writes)',
                      'mp4': mp4.relative_to(ROOT).as_posix(), 'mp4Sha256': sha_file(mp4), 'mp4Bytes': mp4.stat().st_size,
                      'concatListLocalCache': lst.relative_to(ROOT).as_posix(), 'concatSha256Bytes': sha_file(lst),
                      'frameCacheLocalOnly': (cache / 'frames' / clip['name']).relative_to(ROOT).as_posix(), 'frames': len(rows),
                      'frameSha256ListSha256': hashlib.sha256('\n'.join(r['sha256'] for r in rows).encode()).hexdigest(),
                      'capturedSpanSeconds': round(span, 6), 'autoPressedAt': clip['autoPressedAt'], 'battleFinishedAt': clip['finishedAt'],
                      'statesFrameCount': clip['statesFrameCount'], 'stateFirstSeenSeconds': first, 'stateFirstRunRows': runs,
                      'statesMissing': [s for s in STATES if s not in clip['statesFrameCount']],
                      'initialSceneEntrySample': {'row': 0, 't': rows[0]['t'], 'wallDelta': rows[0]['wallDelta'], 'processDelta': rows[0]['processDelta'],
                                                  'note': 'first frame after instantiate/add_child; includes scene load and first _process; kept in the clip and the MP4'},
                      'postStartFrames': {'rows': f'1..{len(rows) - 1}', 'wallDelta': post_wall, 'processDelta': post_proc, 'effectiveFps': post_fps},
                      'allFramesIncludingEntry': {'wallDelta': stats([r['wallDelta'] for r in rows]), 'processDelta': stats([r['processDelta'] for r in rows]),
                                                  'effectiveFpsRow0ToLast': round((len(rows) - 1) / (rows[-1]['t'] - rows[0]['t']), 3)},
                      'mp4Probe': probe, 'mp4PtsFirst5': pts[:5], 'mp4PtsLast': pts[-1] if pts else None,
                      'mp4PtsGap': {'min': min(gaps), 'max': max(gaps), 'maxErrorVsCapture': pts_err, 'count': len(gaps)} if gaps else None,
                      'encoder': ' '.join(enc[:-1]) + ' <mp4>'})
    for lang in ('en', 'zh'):
        union = set()
        for c in raw['clips']:
            if c['language'] == lang:
                union |= set(c['statesFrameCount'])
        missing = [s for s in STATES if s not in union]
        if missing:
            failures.append(f'{lang}: states never captured {missing}')
    stills = []
    by_name = {c['name']: c for c in raw['clips']}
    for lang in ('en', 'zh'):
        for state, kind in CRITICAL:
            clip = by_name.get(f'{kind}-{lang}')
            idx = [i for i, r in enumerate(clip['rows']) if r['state'] == state] if clip else []
            if not idx:
                failures.append(f'{kind}-{lang}: no {state} frame for critical still')
                continue
            a = idx[0]
            b = a
            while b + 1 < len(clip['rows']) and clip['rows'][b + 1]['state'] == state:
                b += 1
            i = (a + b) // 2  # middle of the first contiguous run: well clear of the possible one-frame label lead
            r = clip['rows'][i]
            dst = OUT / f"{SLUG}critical-{state}-{lang}-{kind}-640_{run_stamp}.png"
            shutil.copyfile(ext(cache / r['file']), ext(dst))
            got = sha_file(dst)
            if got != r['sha256']:
                failures.append(f'{dst.name}: copy hash mismatch')
            stills.append({'png': dst.relative_to(ROOT).as_posix(), 'sha256Bytes': got, 'clip': clip['name'], 'state': state,
                           'source': 'durability-held supplement (TEST-ONLY)' if kind == 'held' else 'normal unmodified combat',
                           'row': i, 'stateRunRows': [a, b], 't': r['t'], 'enemyFrame': r['frame'], 'enemyHp': r['enemyHp'],
                           'cacheFrame': (cache / r['file']).relative_to(ROOT).as_posix()})
    return finish(run_stamp, cache, before, head, runner, raw, clips, stills, failures)


def finish(run_stamp, cache, before, head, runner, raw, clips, stills, failures):
    after = hashes()
    changed = [p for p in before if before[p] != after[p]]
    if changed:
        failures.append(f'bound source changed during run: {changed}')
    ffv = subprocess.run(['ffmpeg', '-version'], capture_output=True, text=True, encoding='utf-8').stdout.splitlines()[0]
    report = {'runStamp': run_stamp, 'toolStamp': TOOL_STAMP, 'utcFinished': datetime.now(timezone.utc).isoformat(timespec='seconds'),
              'status': 'UNAPPROVED technical evidence for an off-by-default candidate; not art acceptance, no smoothness claim',
              'gitHead': head, 'hashNormalization': 'sha256-bytes of working files (no text normalization)',
              'provenance': {'adaptedFrom': {k: v for k, v in FROZEN.items() if k.startswith('tools/')},
                             'captureChange': 'Engine.max_fps = 60 set in the v02 capture harness only (game sets no max_fps); vsync, physics ticks, time scale, scene, CLI flag, input and combat untouched',
                             'notDerivedFrom': 'no frame, video or timing is taken from the v01 240 Hz recordings'},
              'boundSha256AtStart': before, 'boundSha256AtEnd': after, 'frozenExpected': FROZEN, 'runner': runner, 'ffmpeg': ffv,
              'freshAppData': {'APPDATA': (cache / 'app').relative_to(ROOT).as_posix(), 'LOCALAPPDATA': (cache / 'local').relative_to(ROOT).as_posix()},
              'engine': raw.get('engine') if raw else None, 'engineMaxFpsAtEnd': raw.get('engineMaxFpsAtEnd') if raw else None,
              'rawCapture': (OUT / f'{SLUG}capture-raw_{run_stamp}.json').relative_to(ROOT).as_posix(),
              'rawCaptureSha256Bytes': sha_file(OUT / f'{SLUG}capture-raw_{run_stamp}.json') if raw else None,
              'harnessSourceSha256': raw.get('sourceSha256AtStart') if raw else None,
              'clips': clips, 'criticalStills': stills, 'failures': failures, 'result': 'PASS' if not failures else 'FAIL'}
    path = OUT / f'{SLUG}report_{run_stamp}.json'
    path.write_text(json.dumps(report, indent=1, ensure_ascii=False) + '\n', encoding='utf-8', newline='\n')
    print(('PATROL_MOTION60_RUN PASS' if not failures else 'PATROL_MOTION60_RUN FAIL') + f' clips={len(clips)} stills={len(stills)} report={path.name}')
    for f in failures:
        print('FAIL', f)
    return 0 if not failures else 1


if __name__ == '__main__':
    sys.exit(main())
