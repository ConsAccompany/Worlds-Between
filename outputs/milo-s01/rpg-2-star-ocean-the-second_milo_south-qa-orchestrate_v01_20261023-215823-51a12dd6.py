"""QA orchestration for Milo south static v01: author check/build, independent source check, Pixelorama export.

Usage (from repo/): python3 -I outputs/milo-s01/<this> <step> [<new log dir name>]
  steps: check | build | source | pixelorama
Each step's combined stdout/stderr goes to outputs/milo-s01/logs/<dir>/<step>.log; rc is printed.
"""
import hashlib
import os
import pathlib
import subprocess
import sys

R = pathlib.Path(__file__).resolve().parents[2]
TAG = '20261023-215823-51a12dd6'
# Do not resolve(): the venv python is a symlink and following it drops the venv site-packages.
py = os.path.abspath(R.parent / 'tooling/venv/bin/python')
pxl = str(R.parent / 'tooling/pixelorama-1.2.3/Pixelorama-Linux-64bit/Pixelorama.x86_64')
author = f'tools/rpg-2-star-ocean-the-second_milo_south-static-author_unapproved-v01_{TAG}.py'
checker = f'tools/rpg-2-star-ocean-the-second_milo_static-source-check_v01_{TAG}.py'
step = sys.argv[1]
q = R / 'outputs/milo-s01/logs' / (sys.argv[2] if len(sys.argv) > 2 else step)
q.mkdir(parents=True, exist_ok=True)
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
    print('\n'.join(out.strip().splitlines()[-60:]))
    return rc


if step in ('check', 'build'):
    run(step, [py, '-X', 'utf8', '-I', author, step])
elif step == 'diag':
    run('diag', [py, '-X', 'utf8', '-I', 'outputs/milo-s01/scratch/milo_isolated_diag.py'])
elif step == 'compare':
    run('compare', [py, '-X', 'utf8', '-I', 'outputs/milo-s01/scratch/milo_pxl_compare.py'])
elif step == 'source':
    run('source', [py, '-X', 'utf8', '-I', checker, '--root', '.', '--out', f'outputs/milo-s01/independent-{q.name}'])
elif step == 'pixelorama':
    from_dir = R / 'game/assets/characters/milo-native-v01/south'
    for ext in ('pxo', 'ora'):
        src = next(from_dir.glob(f'*edit*.{ext}'))
        before = sha(src)
        dst = q / f'export-{ext}'
        dst.mkdir(parents=True, exist_ok=False)
        target = dst / f'rpg-2-star-ocean-the-second_milo_south-pxl-export-from-{ext}_test-only-v01_{TAG}.png'
        run(f'pixelorama-{ext}', [pxl, '--headless', '--audio-driver', 'Dummy', '--quit', '--', '--export', '-o',
                                  str(target), str(src)], timeout=120)
        print(f'   source unchanged: {sha(src) == before}; emitted: {sorted(x.name for x in dst.iterdir())}')
else:
    raise SystemExit(f'unknown step {step}')
