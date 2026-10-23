"""QA orchestration for Milo north static v01 (content.char.milo.static-north). Test orchestration only.

Adapted from the Milo west orchestrator. Usage (from repo/): python3 -I outputs/milo-n01/<this> <step> <new log dir>
  steps: check | build | preview | diag | source | pixelorama | compare <pxl log dir> | fit
Each step writes cmd, rc and combined stdout/stderr to outputs/milo-n01/logs/<dir>/<step>.log and refuses to
reuse an existing log dir. Source hashes (north + south + dirty west package, tools) are recorded before/after
every step. No runtime/default change: the fit step runs the existing generic overlay script through the checked
runner.
"""
import hashlib
import json
import os
import pathlib
import subprocess
import sys

R = pathlib.Path(__file__).resolve().parents[2]
TAG = '20261023-225642-1b612f93'
# Do not resolve(): the venv python is a symlink and following it drops the venv site-packages.
py = os.path.abspath(R.parent / 'tooling/venv/bin/python')
pxl = str(R.parent / 'tooling/pixelorama-1.2.3/Pixelorama-Linux-64bit/Pixelorama.x86_64')
godot = str((R / '../tooling/godot-4.7.2/Godot_v4.7.2-stable_linux.x86_64').resolve())
runner = 'tools/rpg-2-star-ocean-the-second_godot_checked-runner_v01_20261018-203400-f74ac6d1.py'
fit = 'tools/rpg-2-star-ocean-the-second_native-static_scene-fit-capture_test-only-v01_20261021-235007-514b9771.gd'
author = f'tools/rpg-2-star-ocean-the-second_milo_north-static-author_unapproved-v01_{TAG}.py'
checker = f'tools/rpg-2-star-ocean-the-second_milo_north-static-source-check_v01_{TAG}.py'
south_author = 'tools/rpg-2-star-ocean-the-second_milo_south-static-author_unapproved-v01_20261023-215823-51a12dd6.py'
south_checker = 'tools/rpg-2-star-ocean-the-second_milo_static-source-check_v01_20261023-215823-51a12dd6.py'
base = R / 'game/assets/characters/milo-native-v01'
north, south, west = base / 'north', base / 'south', base / 'west'
scratch = 'outputs/milo-n01/scratch'
step, logdir = sys.argv[1], sys.argv[2]
q = R / 'outputs/milo-n01/logs' / logdir
q.mkdir(parents=True, exist_ok=False)
env = dict(os.environ, PYTHONUTF8='1')
env.pop('ANTHROPIC_API_KEY', None)
results = {}


def sha(p):
    return hashlib.sha256(pathlib.Path(p).read_bytes()).hexdigest()


def pins():
    files = [p for d in (north, south, west) if d.is_dir() for p in sorted(d.iterdir())]
    files += [R / x for x in (author, checker, south_author, south_checker, fit, runner)]
    return {str(p.relative_to(R)): sha(p) for p in files if p.is_file()}


def run(name, cmd, timeout=300):
    try:
        p = subprocess.run(cmd, cwd=R, env=env, capture_output=True, text=True, encoding='utf-8', errors='replace',
                           timeout=timeout)
        out, rc = p.stdout + p.stderr, p.returncode
    except subprocess.TimeoutExpired as e:
        out, rc = f'TIMEOUT after {timeout}s\n{e.stdout or ""}{e.stderr or ""}', 'timeout'
    (q / f'{name}.log').write_text(f'cmd: {cmd}\nrc: {rc}\n\n{out}', encoding='utf-8')
    results[name] = rc
    print(f'== {name} rc={rc}')
    print('\n'.join(out.strip().splitlines()[-70:]))
    return rc


before = pins()
if step in ('check', 'build', 'preview'):
    run(step, [py, '-X', 'utf8', '-I', author, step])
elif step == 'diag':
    run('diag', [py, '-X', 'utf8', '-I', f'{scratch}/milo_north_isolated_diag.py'])
elif step == 'source':
    run('source', [py, '-X', 'utf8', '-I', checker, '--root', '.', '--out', str(q / 'independent')])
elif step == 'pixelorama':
    for ext in ('pxo', 'ora'):
        src = next(north.glob(f'*edit*.{ext}'))
        b0 = sha(src)
        dst = q / f'export-{ext}'
        dst.mkdir(parents=True, exist_ok=False)
        target = dst / f'rpg-2-star-ocean-the-second_milo_north-pxl-export-from-{ext}_test-only-v01_{TAG}.png'
        run(f'pixelorama-{ext}', [pxl, '--headless', '--audio-driver', 'Dummy', '--quit', '--', '--export', '-o',
                                  str(target), str(src)], timeout=120)
        print(f'   source unchanged: {sha(src) == b0}; emitted: {sorted(x.name for x in dst.iterdir())}')
elif step == 'compare':
    run('compare', [py, '-X', 'utf8', '-I', f'{scratch}/milo_north_pxl_compare.py', sys.argv[3]])
elif step == 'fit':
    png = next(north.glob('*north-static_*.png'))
    cap = q / 'fit'
    cap.mkdir(exist_ok=False)
    run('fit', ['xvfb-run', '-a', '-s', '-screen 0 640x360x24', py, '-I', runner, '--timeout', '110',
                '--expect', 'JIANG37_SOURCE_FIT_PASS captures=4', '--log', str(q / 'fit.runner.log'), '--',
                godot, '--audio-driver', 'Dummy', '--rendering-driver', 'opengl3', '--resolution', '640x360',
                '--path', 'game', '--script', str(R / fit), '--', str(png), str(cap), f'n01-{TAG}', 'milo'], 150)
    for f in sorted(cap.iterdir()):
        print(f.name, sha(f))
else:
    raise SystemExit(f'unknown step {step}')
after = pins()
head = subprocess.run(['git', 'rev-parse', 'HEAD'], cwd=R, capture_output=True, text=True).stdout.strip()
summary = {'step': step, 'sourceRevision': head, 'results': results, 'pinsBefore': before,
           'pinsAfter': after, 'pinsUnchanged': before == after, 'hash': 'sha256 of raw bytes, no normalization'}
(q / 'summary.json').write_text(json.dumps(summary, indent=2) + '\n', encoding='utf-8')
print('PINS_UNCHANGED', before == after, '(build is expected to add north files)' if step == 'build' else '')
print('RESULTS', results)
