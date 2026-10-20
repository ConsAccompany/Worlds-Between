"""Bounded normal-input Godot recordings. Run after the source package and distance model are integrated.
No external model calls, accounts, default changes or art acceptance. Each movie is a separate file.
"""
from pathlib import Path
import datetime, hashlib, importlib.util, json, os, subprocess, uuid, sys

C = Path(__file__).resolve().parents[1]
P = C.parents[1]
PY = Path(os.sys.executable)
GODOT = P / 'work/tooling/godot-4-7-2/Godot_v4.7.2-stable_win64_console.exe'
FFMPEG = Path(r'C:/Users/hkzha/AppData/Local/Microsoft/WinGet/Links/ffmpeg.EXE')
FFPROBE = FFMPEG.with_name('ffprobe.EXE')
CHECKED = C / 'tools/rpg-2-star-ocean-the-second_godot_checked-runner_v01_20261018-203400-f74ac6d1.py'
HARNESS = C / 'tools/rpg-2-star-ocean-the-second_heroine-sea_distance-normal-input_root-check-v01_20261020-214820-65d417ac.gd'
spec = importlib.util.spec_from_file_location('checked', CHECKED)
checked = importlib.util.module_from_spec(spec)
spec.loader.exec_module(checked)


def lp(path):
    return Path('\\\\?\\' + str(path.resolve()))


def sha(path):
    return hashlib.sha256(lp(path).read_bytes()).hexdigest()


def main():
    tag = datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%d-%H%M%S') + '-' + uuid.uuid4().hex[:8]
    out = C / 'outputs/hsea-root09'
    out.mkdir(exist_ok=True)
    package_dir = Path(sys.argv[1]).resolve() if len(sys.argv) > 1 else C / 'game/data/hsea-gait09'
    revision = sys.argv[2] if len(sys.argv) > 2 else 'v04'
    registries = list(package_dir.glob('*registry*.json'))
    assert len(registries) == 1, registries
    registry = 'res://' + registries[0].relative_to(C / 'game').as_posix()
    runs = []
    for context, fps in [('city', 30), ('room', 60)]:
        profile = P / 'work/dual09/profiles' / ('root-' + context)
        for key, sub in [('APPDATA', 'a'), ('LOCALAPPDATA', 'l')]:
            folder = profile / sub
            folder.mkdir(parents=True, exist_ok=True)
            os.environ[key] = str(folder)
        raw = P / 'work/dual09/raw' / tag / context
        raw.mkdir(parents=True)
        stem = 'rpg-2-star-ocean-the-second_' + context + '_distance-raw_' + tag
        cmd = [str(GODOT), '--path', str(C / 'game'), '--resolution', '1280x720', '--position', '40,40',
               '--audio-driver', 'Dummy', '--fixed-fps', str(fps), '--write-movie', str(raw / (stem + '.png')),
               '--script', str(HARNESS), '--', registry, str(out), tag, context, str(fps)]
        log = out / f'rpg-2-star-ocean-the-second_heroine-sea-distance_{context}-run_v01_{tag}.log'
        result = checked.run_checked(cmd, 180, expected=['SEA_DISTANCE_ROOT_PASS'], log_path=lp(log))
        print(context, result['passed'], result['reason'], result['log'][-900:], flush=True)
        assert result['passed'], result['log'][-4000:]
        frames = list(raw.glob(stem + '*.png'))
        movie = out / f'rpg-2-star-ocean-the-second_heroine-sea-distance_{context}-{fps}fps-normal-input_unapproved-{revision}_{tag}.mp4'
        encode = subprocess.run([str(FFMPEG), '-hide_banner', '-v', 'error', '-y', '-framerate', str(fps), '-i',
                                 str(raw / (stem + '%08d.png')), '-c:v', 'libx264', '-preset', 'slow', '-crf', '18',
                                 '-pix_fmt', 'yuv420p', '-movflags', '+faststart', str(movie)], capture_output=True, text=True, encoding='utf8')
        assert encode.returncode == 0, encode.stderr
        probe = subprocess.run([str(FFPROBE), '-v', 'error', '-count_frames', '-select_streams', 'v:0', '-show_entries',
                                'stream=width,height,avg_frame_rate,nb_read_frames:format=duration,size', '-of', 'json', str(movie)],
                               capture_output=True, text=True, encoding='utf8')
        assert probe.returncode == 0, probe.stderr
        info = json.loads(probe.stdout)
        stream = info['streams'][0]
        assert (stream['width'], stream['height'], stream['avg_frame_rate']) == (1280, 720, f'{fps}/1')
        assert int(stream['nb_read_frames']) == len(frames)
        assert 0 < movie.stat().st_size <= 16 * 1024 * 1024
        runs.append({'context': context, 'fps': fps, 'movie': movie.relative_to(C).as_posix(), 'sha256': sha(movie),
                     'frames': len(frames), 'probe': info, 'command': cmd, 'log': log.relative_to(C).as_posix()})
        print('SEA_DISTANCE_MOVIE_PASS', context, len(frames), flush=True)
    source_files = [HARNESS,
                    C / 'game/scripts/hsea09/rpg-2-star-ocean-the-second_heroine-sea_distance-driver_opt-in-v01_20261020-214620-4be375a2.gd',
                    C / 'game/scripts/rpg-2-star-ocean-the-second_hsea09_locomotion-phase_model_v01_20261020-174416-39e12f18.gd',
                    C / 'game/scripts/exploration_sprite_set_pilot.gd']
    source_pins = [{'file': f.relative_to(C).as_posix(), 'sha256': sha(f), 'hashMode': 'raw'} for f in source_files]
    report = {'completedAt': datetime.datetime.now(datetime.timezone.utc).isoformat(), 'result': 'PASS', 'runs': runs,
              'revision': revision, 'testedSourceFiles': source_pins,
              'harnessSha256': sha(HARNESS), 'registry': registry, 'registrySha256': sha(registries[0]),
              'defaultAdoption': False, 'artApproved': False, 'fluidityCertified': False}
    target = out / f'rpg-2-star-ocean-the-second_heroine-sea-distance_combined-root-proof_v01_{tag}.json'
    lp(target).write_text(json.dumps(report, indent=2) + '\n', encoding='utf8')
    print('SEA_DISTANCE_COMBINED_ROOT_PASS', target, flush=True)


if __name__ == '__main__':
    main()
