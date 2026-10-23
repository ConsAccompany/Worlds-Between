"""Provider13 QA re-run for Milo south static v01: author check, independent checker, generic Godot source-fit.

Usage (from repo/): python3 -I outputs/milo65/provider13/<this>
Writes only under outputs/milo65/provider13/. Each step logs cmd, rc and output; source hashes before/after.
"""
import hashlib
import json
import os
import pathlib
import subprocess

R = pathlib.Path(__file__).resolve().parents[3]
Q = pathlib.Path(__file__).resolve().parent
TAG = '20261023-215823-51a12dd6'
# Do not resolve(): the venv python is a symlink and following it drops the venv site-packages.
py = os.path.abspath(R.parent / 'tooling/venv/bin/python')
godot = str((R / '../tooling/godot-4.7.2/Godot_v4.7.2-stable_linux.x86_64').resolve())
runner = str(R / 'tools/rpg-2-star-ocean-the-second_godot_checked-runner_v01_20261018-203400-f74ac6d1.py')
fit = str(R / 'tools/rpg-2-star-ocean-the-second_native-static_scene-fit-capture_test-only-v01_20261021-235007-514b9771.gd')
author = f'tools/rpg-2-star-ocean-the-second_milo_south-static-author_unapproved-v01_{TAG}.py'
checker = f'tools/rpg-2-star-ocean-the-second_milo_static-source-check_v01_{TAG}.py'
src = R / 'game/assets/characters/milo-native-v01/south'
png = src / f'rpg-2-star-ocean-the-second_milo_south-static_unapproved-v01_20261023-215823-28a012bd.png'
env = dict(os.environ, PYTHONUTF8='1')
env.pop('ANTHROPIC_API_KEY', None)
results = {}


def sha(p):
    return hashlib.sha256(pathlib.Path(p).read_bytes()).hexdigest()


def pins():
    files = sorted(src.iterdir()) + [R / author, R / checker, pathlib.Path(fit), pathlib.Path(runner)]
    return {str(p.relative_to(R)) if p.is_relative_to(R) else str(p): sha(p) for p in files if p.is_file()}


def run(name, cmd, timeout):
    try:
        p = subprocess.run(cmd, cwd=R, env=env, capture_output=True, text=True, encoding='utf-8', errors='replace',
                           timeout=timeout)
        out, rc = p.stdout + p.stderr, p.returncode
    except subprocess.TimeoutExpired as e:
        out, rc = f'TIMEOUT after {timeout}s\n{e.stdout or ""}{e.stderr or ""}', 'timeout'
    (Q / f'{name}.log').write_text(f'cmd: {cmd}\nrc: {rc}\n\n{out}', encoding='utf-8')
    results[name] = rc
    print(f'== {name} rc={rc}')
    print('\n'.join(out.strip().splitlines()[-40:]))
    return rc


before = pins()
run('author-check', [py, '-X', 'utf8', '-I', author, 'check'], 300)
run('independent-source', [py, '-X', 'utf8', '-I', checker, '--root', '.', '--out', str(Q / 'independent')], 300)
cap = Q / 'fit'
cap.mkdir(exist_ok=False)
run('fit', ['xvfb-run', '-a', '-s', '-screen 0 640x360x24', py, '-I', runner, '--timeout', '110',
            '--expect', 'JIANG37_SOURCE_FIT_PASS captures=4', '--log', str(Q / 'fit.runner.log'), '--',
            godot, '--audio-driver', 'Dummy', '--rendering-driver', 'opengl3', '--resolution', '640x360',
            '--path', 'game', '--script', fit, '--', str(png), str(cap), f'provider13-{TAG}', 'milo'], 150)
for f in sorted(cap.iterdir()):
    print(f.name, sha(f))
after = pins()
summary = {'sourceRevision': subprocess.run(['git', 'rev-parse', 'HEAD'], cwd=R, capture_output=True, text=True).stdout.strip(),
           'results': results, 'pinsBefore': before, 'pinsUnchanged': before == after,
           'captures': {f.name: sha(f) for f in sorted(cap.iterdir())}, 'hash': 'sha256 of raw bytes, no normalization'}
(Q / f'rpg-2-star-ocean-the-second_milo_provider13-qa-summary_test-only-v01_{TAG}.json').write_text(
    json.dumps(summary, indent=2) + '\n', encoding='utf-8')
print('PINS_UNCHANGED', before == after)
print('RESULTS', results)
raise SystemExit(0 if before == after and all(v == 0 for v in results.values()) else 1)
