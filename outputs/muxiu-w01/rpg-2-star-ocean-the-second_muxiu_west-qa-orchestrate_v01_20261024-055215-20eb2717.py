"""QA orchestration for Muxiu west static v01 (adapted from the Muxiu south v01 orchestration; same tools/flags).

Usage (from repo/): python3 -I outputs/muxiu-w01/<this> <step> <new log dir name> [pixelorama log dir]
  steps: preview | check | build | source | pixelorama | compare | fit
Each step's combined stdout/stderr goes to outputs/muxiu-w01/logs/<dir>/<step>.log (dir must be new); rc is printed.
"""
import hashlib
import json
import os
import pathlib
import subprocess
import sys

R = pathlib.Path(__file__).resolve().parents[2]
TAG = '20261024-055215-20eb2717'
# Do not resolve(): the venv python is a symlink and following it drops the venv site-packages.
py = os.path.abspath(R.parent / 'tooling/venv/bin/python')
pxl = str(R.parent / 'tooling/pixelorama-1.2.3/Pixelorama-Linux-64bit/Pixelorama.x86_64')
author = f'tools/rpg-2-star-ocean-the-second_muxiu_west-static-author_unapproved-v01_{TAG}.py'
checker = f'tools/rpg-2-star-ocean-the-second_muxiu_west-static-source-check_v01_{TAG}.py'
WEST = R / 'game/assets/characters/muxiu-native-v01/west'
step, logname = sys.argv[1], sys.argv[2]
q = R / 'outputs/muxiu-w01/logs' / logname
q.mkdir(parents=True, exist_ok=False)
env = dict(os.environ, PYTHONUTF8='1')
env.pop('ANTHROPIC_API_KEY', None)


def sha(p):
    return hashlib.sha256(pathlib.Path(p).read_bytes()).hexdigest()


def run(name, cmd, timeout=300):
    try:
        p = subprocess.run(cmd, cwd=R, env=env, capture_output=True, text=True, encoding='utf-8', errors='replace',
                           timeout=timeout)
        out, rc = p.stdout + p.stderr, p.returncode
    except subprocess.TimeoutExpired as e:
        out, rc = f'TIMEOUT after {timeout}s\n{e.stdout or ""}{e.stderr or ""}', 'timeout'
    (q / f'{name}.log').write_text(f'cmd: {cmd}\nrc: {rc}\n\n{out}', encoding='utf-8')
    print(f'== {name} rc={rc}')
    print('\n'.join(out.strip().splitlines()[-70:]))
    return rc


if step in ('preview', 'check', 'build'):
    run(step, [py, '-X', 'utf8', '-I', author, step], timeout=240)
elif step == 'source':
    run('source', [py, '-X', 'utf8', '-I', checker, '--root', '.', '--out', f'outputs/muxiu-w01/independent-{q.name}'],
        timeout=240)
elif step == 'pixelorama':
    for ext in ('pxo', 'ora'):
        src = next(WEST.glob(f'*edit*.{ext}'))
        before = sha(src)
        dst = q / f'export-{ext}'
        dst.mkdir(parents=True, exist_ok=False)
        target = dst / f'rpg-2-star-ocean-the-second_muxiu_west-pxl-export-from-{ext}_test-only-v01_{TAG}.png'
        run(f'pixelorama-{ext}', [pxl, '--headless', '--audio-driver', 'Dummy', '--quit', '--', '--export', '-o',
                                  str(target), str(src)], timeout=90)
        print(f'   source unchanged: {sha(src) == before}; emitted: {sorted(x.name for x in dst.iterdir())}')
elif step == 'compare':                                         # exact RGBA equality, read-only on sources
    from PIL import Image
    src = next(WEST.glob('*static*.png'))
    ref = Image.open(src).convert('RGBA')
    res = {'source_png': str(src.relative_to(R)), 'source_sha256': sha(src)}
    for ext in ('pxo', 'ora'):
        pngs = sorted((R / 'outputs/muxiu-w01/logs' / sys.argv[3] / f'export-{ext}').glob('*.png'))
        r = {'emitted': [x.name for x in pngs], 'rgba_equal': False}
        if len(pngs) == 1:
            im = Image.open(pngs[0]).convert('RGBA')
            r.update(size=list(im.size), sha256=sha(pngs[0]), rgba_equal=im.size == ref.size and im.tobytes() == ref.tobytes())
        res[ext] = r
    res['all_equal'] = all(res[e]['rgba_equal'] for e in ('pxo', 'ora'))
    text = json.dumps(res, indent=1) + '\nMUXIU_WEST_PXL_EXPORT_' + ('EQUAL' if res['all_equal'] else 'MISMATCH') + '\n'
    (q / 'compare.log').write_text(text, encoding='utf-8')
    print(text)
elif step == 'fit':
    # existing checked runner + existing generic static-fit capture (test-only, no adoption); user:// isolated
    for k in ('XDG_DATA_HOME', 'XDG_CONFIG_HOME', 'XDG_CACHE_HOME'):
        env[k] = str(q / 'xdg' / k.lower()); pathlib.Path(env[k]).mkdir(parents=True)
    png = next(WEST.glob('*static*.png'))
    out = q / 'fit'; out.mkdir()
    godot = str(R.parent / 'tooling/godot-4.7.2/Godot_v4.7.2-stable_linux.x86_64')
    runner = 'tools/rpg-2-star-ocean-the-second_godot_checked-runner_v01_20261018-203400-f74ac6d1.py'
    gd = 'tools/rpg-2-star-ocean-the-second_native-static_scene-fit-capture_test-only-v01_20261021-235007-514b9771.gd'
    run('fit', ['xvfb-run', '-a', '-s', '-screen 0 640x360x24', py, '-I', runner, '--timeout', '110',
                '--expect', 'JIANG37_SOURCE_FIT_PASS captures=4', '--log', str(q / 'fit.runner.log'), '--',
                godot, '--audio-driver', 'Dummy', '--rendering-driver', 'opengl3', '--resolution', '640x360',
                '--path', 'game', '--script', str(R / gd), '--', str(png), str(out), f'{q.name}-{TAG}', 'muxiu'],
        timeout=150)
    for x in sorted(out.iterdir()):
        print(f'   {x.name} {sha(x)}')
else:
    raise SystemExit(f'unknown step {step}')
