"""QA orchestration for Milo east walk/stop mew01 (content.char.milo.walk-east). Same pattern as milo-nw01/milo-sw01.

Usage (from repo/): python3 -I outputs/milo-ew01/<this> <step> [<new log dir name>]
  steps: check | build | indep   (indep = independent checker incl. tamper controls, Pixelorama native export, preview)
Each step's combined stdout/stderr goes to outputs/milo-ew01/logs/<dir>/<step>.log; rc is printed.
"""
import os
import pathlib
import subprocess
import sys

R = pathlib.Path(__file__).resolve().parents[2]
TAG = '20261024-061500-3e1a5c07'
# Do not resolve(): the venv python is a symlink and following it drops the venv site-packages.
py = os.path.abspath(R.parent / 'tooling/venv/bin/python')
pxl = str(R.parent / 'tooling/pixelorama-1.2.3/Pixelorama-Linux-64bit/Pixelorama.x86_64')
author = f'tools/rpg-2-star-ocean-the-second_milo_walk-east-source-author_unapproved-mew01-v01_{TAG}.py'
checker = f'tools/rpg-2-star-ocean-the-second_milo_walk-east-independent-check_v01_{TAG}.py'
step = sys.argv[1]
q = R / 'outputs/milo-ew01/logs' / (sys.argv[2] if len(sys.argv) > 2 else step)
q.mkdir(parents=True, exist_ok=False)
env = dict(os.environ, PYTHONUTF8='1', PIXELORAMA=pxl)
env.pop('ANTHROPIC_API_KEY', None)


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
    sys.exit(run(step, [py, '-X', 'utf8', '-I', author, step]) != 0)
elif step == 'indep':
    sys.exit(run('indep', [py, '-X', 'utf8', '-I', checker, '--out', f'outputs/milo-ew01/{q.name}'], timeout=400) != 0)
else:
    raise SystemExit(f'unknown step {step}')
