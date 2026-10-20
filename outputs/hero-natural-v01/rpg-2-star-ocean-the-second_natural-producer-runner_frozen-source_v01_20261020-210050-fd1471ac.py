"""Natural heroine battle flow runner (test-only). Runs the flow harness twice through the checked runner in a real
1280x720 window under --fixed-fps with Godot's movie writer (actual rendered frames, no compositing), then encodes each
raw PNG sequence to MP4 at its original fps (no speed-up/interpolation) and probes it. Raw frames stay local.
Usage: python <this> [patrol|sentry ...]"""
import hashlib, importlib.util, json, os, shutil, subprocess, sys, uuid
from datetime import datetime, timezone
from pathlib import Path

C = Path(__file__).resolve().parents[1]
P = C.parents[2]
GODOT = P / 'work/tooling/godot-4-7-2/Godot_v4.7.2-stable_win64_console.exe'
HARNESS = C / 'tools/rpg-2-star-ocean-the-second_heroine-natural-battle_flow-check_test-only-v01_20261020-205219-4c19e7a2.gd'
INDEX = 'res://data/heroine-sea-combat-v01/rpg-2-star-ocean-the-second_heroine-sea-combat_spritesheet-index_v01_20261020-201338-38ecfcb0.json'
SCEN = {'patrol': 30, 'sentry': 60}


def lp(p):
    s = str(p)
    return Path(s) if s.startswith('\\\\?\\') else Path('\\\\?\\' + str(Path(p).resolve()))


def sha(p):
    return hashlib.sha256(lp(p).read_bytes()).hexdigest()


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


check = load('checked', C / 'tools/rpg-2-star-ocean-the-second_godot_checked-runner_v01_20261018-203400-f74ac6d1.py')
mc = load('mc', C / 'tools/rpg-2-star-ocean-the-second_heroine-sea_motion-capture-runner_test-only-v01_20261020-153144-3fb36c1a.py')


def main():
    tag = datetime.now(timezone.utc).strftime('%Y%m%d-%H%M%S') + '-' + uuid.uuid4().hex[:8]
    out = C / 'outputs/hero-natural-v01' / tag
    lp(out).mkdir(parents=True)
    ffmpeg = mc.find_ffmpeg(); ffprobe = mc.ffprobe_for(ffmpeg)
    results = []
    if not (C / 'game/.godot/global_script_class_cache.cfg').is_file():
        env = dict(os.environ)
        for k in ('APPDATA', 'LOCALAPPDATA'):
            d = P / 'work/dual07/profiles' / tag[-8:] / ('im' + k[:2].lower())
            lp(d).mkdir(parents=True, exist_ok=True); env[k] = str(d)
        old = dict(os.environ); os.environ.clear(); os.environ.update(env)
        try:
            r = check.run_checked([str(GODOT), '--headless', '--path', str(C / 'game'), '--editor', '--import', '--quit'], 300,
                                  log_path=lp(out / f'rpg-2-star-ocean-the-second_heroine-natural-battle_import-log_test-only-v01_{tag}.log'))
        finally:
            os.environ.clear(); os.environ.update(old)
        print('import', r['passed'], r['reason'], flush=True)
        results.append({'scenario': 'import', **{k: v for k, v in r.items() if k != 'log'}})
        if not r['passed']:
            raise SystemExit('IMPORT_FAILED ' + r['log'][-2000:])
    for scen in (sys.argv[1:] or list(SCEN)):
        fps = SCEN[scen]
        raw = out / f'raw-{scen}'
        lp(raw).mkdir()
        env = dict(os.environ)
        for k in ('APPDATA', 'LOCALAPPDATA', 'TEMP', 'TMP'):
            d = P / 'work/dual07/profiles' / tag[-8:] / (scen[:2] + k[:2].lower())
            lp(d).mkdir(parents=True, exist_ok=True); env[k] = str(d)
        cmd = [str(GODOT), '--resolution', '1280x720', '--position', '40,40', '--audio-driver', 'Dummy', '--fixed-fps', str(fps),
               '--write-movie', str(raw / 'frame.png'), '--path', str(C / 'game'), '-s', str(HARNESS), '--', str(out), INDEX, tag, scen]
        log = out / f'rpg-2-star-ocean-the-second_heroine-natural-battle_{scen}-godot-log_test-only-v01_{tag}.log'
        old = dict(os.environ); os.environ.clear(); os.environ.update(env)
        try:
            r = check.run_checked(cmd, 140, expected=[f'NATURAL_FLOW_ALL_PASS scenario={scen}'], log_path=lp(log))
        finally:
            os.environ.clear(); os.environ.update(old)
        print(scen, r['passed'], r['reason'], r['log'].splitlines()[-4:], flush=True)
        rec = {'scenario': scen, 'fps': fps, 'command': cmd, 'log': log.relative_to(C).as_posix(), **{k: v for k, v in r.items() if k != 'log'}}
        frames = sorted(lp(raw).glob('frame*.png'))
        rec['rawFrames'] = len(frames)
        if frames:
            mp4 = out / f'rpg-2-star-ocean-the-second_heroine-natural-battle_{scen}-{"en30-bright" if scen == "patrol" else "zh60-dark"}_scripted-normal-movie_{tag}.mp4'
            title = f'Scripted normal-game evidence {scen} {fps}fps original speed - not a human playtest or fluidity certification'
            enc = subprocess.run([str(ffmpeg), '-hide_banner', '-v', 'warning', '-y', '-framerate', str(fps), '-i', str(raw / 'frame%08d.png'),
                                  '-c:v', 'libx264', '-preset', 'slow', '-crf', '18', '-pix_fmt', 'yuv420p', '-movflags', '+faststart',
                                  '-metadata', 'title=' + title, str(mp4)], capture_output=True, text=True, encoding='utf-8', errors='replace')
            probe = json.loads(subprocess.run([str(ffprobe), '-v', 'error', '-count_frames', '-select_streams', 'v:0', '-show_entries',
                                               'stream=codec_name,width,height,r_frame_rate,avg_frame_rate,nb_read_frames:format=duration,size',
                                               '-of', 'json', mp4.name], cwd=str(out), capture_output=True, text=True, encoding='utf-8', errors='replace').stdout or '{}')
            st = (probe.get('streams') or [{}])[0]
            if not lp(mp4).is_file():
                rec['mp4'] = {'ok': False, 'ffmpegExit': enc.returncode, 'ffmpegStderr': enc.stderr[-2000:]}
                results.append(rec)
                continue
            rec['mp4'] = {'file': mp4.relative_to(C).as_posix(), 'sha256': sha(mp4), 'bytes': lp(mp4).stat().st_size, 'ffmpegExit': enc.returncode,
                          'ffmpegStderr': enc.stderr, 'probe': probe,
                          'ok': enc.returncode == 0 and st.get('width') == 1280 and st.get('height') == 720 and st.get('avg_frame_rate') == f'{fps}/1'
                          and int(st.get('nb_read_frames', -1)) == len(frames) and lp(mp4).stat().st_size <= 16 * 1024 * 1024}
            rec['firstFrameSha256'] = sha(frames[0]); rec['lastFrameSha256'] = sha(frames[-1])
        results.append(rec)
    report = {'tag': tag, 'harness': HARNESS.relative_to(C).as_posix(), 'harnessSha256Raw': sha(HARNESS), 'runnerSha256Raw': sha(Path(__file__)),
              'arenaSha256Raw': sha(C / 'game/scripts/battle_arena.gd'), 'index': INDEX, 'results': results,
              'allPass': all(r['passed'] and r.get('mp4', {}).get('ok') for r in results),
              'note': 'scripted normal-game evidence; not human playtest, fluidity certification, art approval or default adoption',
              'completedAt': datetime.now(timezone.utc).isoformat()}
    f = out / f'rpg-2-star-ocean-the-second_heroine-natural-battle_runner-proof_test-only-v01_{tag}.json'
    lp(f).write_text(json.dumps(report, indent=1) + '\n', encoding='utf-8')
    print('NATURAL_RUNNER', 'PASS' if report['allPass'] else 'FAIL', f, flush=True)
    sys.exit(0 if report['allPass'] else 1)


if __name__ == '__main__':
    main()
