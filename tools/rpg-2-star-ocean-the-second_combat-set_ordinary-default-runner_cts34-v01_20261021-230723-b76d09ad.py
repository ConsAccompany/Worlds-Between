"""Bounded runner for the cts34 ordinary-default combat-set checker.
Exports committed HEAD game/ via git archive (bytes = blobs, core.autocrlf=false) to a temp tree, adds this checker,
imports there (no worktree side effects), runs the rational-clock and half-scale checks once (headless) and the
checker windowed at native 640x360 in en and zh. Any ERROR/SCRIPT_ERROR/parser line fails a run even on exit 0.
Technical evidence only: no art/motion/human acceptance, no default or runtime change.
Usage: python -X utf8 -I <this> [--no-capture]
"""
import hashlib, importlib.util, io, json, os, subprocess, sys, tarfile, uuid
from datetime import datetime, timezone
from pathlib import Path

C = Path(__file__).resolve().parents[1]
P = next(p for p in C.parents if (p / 'work/tooling/godot-4-7-2').is_dir())
def lp(p): return Path('\\\\?\\' + str(Path(p).resolve()))
def sha(p): return hashlib.sha256(lp(p).read_bytes()).hexdigest()
spec = importlib.util.spec_from_file_location('checked', C / 'tools/rpg-2-star-ocean-the-second_godot_checked-runner_v01_20261018-203400-f74ac6d1.py')
checked = importlib.util.module_from_spec(spec); spec.loader.exec_module(checked)
GODOT = P / 'work/tooling/godot-4-7-2/Godot_v4.7.2-stable_win64_console.exe'
CHECKER = C / 'tools/rpg-2-star-ocean-the-second_combat-set_ordinary-default-check_cts34-v01_20261021-230723-b76d09ad.gd'
CAPTURE = '--no-capture' not in sys.argv
tag = datetime.now(timezone.utc).strftime('%Y%m%d-%H%M%S') + '-' + uuid.uuid4().hex[:8]
out = C / 'outputs/cts34' / tag; lp(out).mkdir(parents=True)
tmp = Path(os.environ['LOCALAPPDATA']) / 'Temp/cts34' / tag[-8:]; lp(tmp).mkdir(parents=True)
head = subprocess.run(['git', '-C', str(C), 'rev-parse', 'HEAD'], capture_output=True, text=True, check=True).stdout.strip()
dirty = subprocess.run(['git', '-C', str(C), 'status', '--porcelain', '--', 'game'], capture_output=True, text=True, check=True).stdout
results = []; failed = []

data = subprocess.run(['git', '-C', str(C), '-c', 'core.autocrlf=false', 'archive', '--format=tar', head, 'game', 'tools'], capture_output=True, check=True).stdout
H = tmp / 'h'
with tarfile.open(fileobj=io.BytesIO(data)) as t:
    for m in t.getmembers():
        if not m.isfile(): continue
        assert '..' not in m.name.split('/'), m.name
        target = Path(str(lp(H)) + '\\' + m.name.replace('/', '\\'))
        os.makedirs(target.parent, exist_ok=True); target.write_bytes(t.extractfile(m).read())
tool_copy = H / 'tools' / CHECKER.name
lp(tool_copy).write_bytes(lp(CHECKER).read_bytes())

def run(name, script=None, extra=(), headless=True, marker=None, editor=False, timeout=180):
    env = dict(os.environ)
    for k in ['APPDATA', 'LOCALAPPDATA']:
        p = tmp / 'prof' / (name + '-' + k[0]); lp(p).mkdir(parents=True); env[k] = str(p)
    cmd = [str(GODOT)] + (['--headless'] if headless else ['--resolution', '640x360', '--position', '2000,100', '--audio-driver', 'Dummy']) + ['--path', str(H / 'game')]
    if editor: cmd += ['--editor', '--import', '--quit']
    if script: cmd += ['--script', str(script)]
    if extra: cmd += ['--'] + [str(x) for x in extra]
    old = dict(os.environ); os.environ.clear(); os.environ.update(env)
    log = out / ('rpg-2-star-ocean-the-second_combat-set_' + name + '_cts34-log_' + tag + '.log')
    try: r = checked.run_checked(cmd, timeout, expected=([marker] if marker else []), log_path=lp(log))
    finally: os.environ.clear(); os.environ.update(old)
    text = r['log']
    rec = {k: v for k, v in r.items() if k != 'log'} | {'name': name, 'command': cmd, 'log': log.relative_to(C).as_posix(),
           'warningCount': sum('WARNING' in x for x in text.splitlines()), 'errorLines': [x for x in text.splitlines() if 'ERROR' in x]}
    if rec['errorLines'] and rec['passed']: rec['passed'] = False; rec['reason'] = 'ERROR line present'
    results.append(rec); print(name, rec['passed'], rec.get('reason'), text.splitlines()[-2:] if text else '', flush=True)
    if not rec['passed']: failed.append(name)
    return rec

imp = run('import', editor=True, timeout=300)
if imp['passed']:
    run('rational-clock', H / 'tools/rpg-2-star-ocean-the-second_combat-rational-clock_root-check_v01_20261020-201636-582fa0ef.gd', marker='ROOT_RATIONAL_CLOCK_PASS checks=')
    run('half-scale', H / 'tools/rpg-2-star-ocean-the-second_combat-half-scale_check_v01_20261020-154048-7d4bddce.gd', marker='COMBAT_HALF_SCALE PASS')
    for lang in ['en', 'zh']:
        run('ordinary-' + lang, tool_copy, [out, tag, lang, 'capture=1' if CAPTURE else 'capture=0'], headless=not CAPTURE, marker='CTS34_ALL_PASS language=' + lang, timeout=300)

S = 'game/scripts/'
src = [S + 'battle_arena.gd', S + 'rpg-2-star-ocean-the-second_combat-sprite-set_loader-playback_pilot-v01_20261018-153656-43a19158.gd',
       S + 'mpath24/rpg-2-star-ocean-the-second_male-playable-path_explore-driver_opt-in-v01_20261021-170200-5e1c24a7.gd',
       S + 'zpath27/rpg-2-star-ocean-the-second_zhao-playable-path_config_opt-in-v01_20261021-223218-3246d731.gd',
       S + 'lpath30/rpg-2-star-ocean-the-second_liang-playable-path_config_opt-in-v01_20261021-202247-ca439d91.gd',
       S + 'jpath33/rpg-2-star-ocean-the-second_ji-playable-path_config_opt-in-v01_20261021-222438-7d4b2e91.gd',
       S + 'hsea18/rpg-2-star-ocean-the-second_heroine-normal-default_policy_runtime-v01_20261021-032237-7c02af94.gd',
       'game/scenes/battle_arena.tscn']
for d in ['mcombat22', 'zcombat26', 'lcombat29', 'jcombat32']:
    src += sorted('game/data/%s/%s' % (d, f.name) for f in lp(H / 'game/data' / d).iterdir() if f.suffix in ('.json', '.png'))
reports = sorted(str(p.relative_to(lp(C))).replace('\\', '/') for p in lp(out).glob('*ordinary-default-check*.json'))
summary = {}
for r in reports:
    j = json.loads((lp(C) / r).read_text(encoding='utf-8'))
    summary[r] = {'passed': j['passed'], 'checks': j['checkCount'], 'failures': j['failures'], 'captures': len(j['captures']), 'fixturesUsed': j['fixturesUsed']}
report = {'tasks': ['qa.combat.protagonist-male.set-check', 'qa.combat.zhao-ling.set-check', 'qa.combat.liang-xu.set-check', 'qa.combat.ji-cheng.set-check'],
          'result': 'FAIL' if failed else 'PASS', 'failed': failed, 'testedRevision': head, 'gameTreeDirtyAtRun': dirty,
          'hashNormalization': 'sha256-bytes of git-archive export with core.autocrlf=false (= committed blob bytes); tools: working bytes',
          'sourceSha256': {s: sha(H / s) for s in src},
          'toolSha256': {CHECKER.name: sha(CHECKER), Path(__file__).name: sha(Path(__file__))},
          'checkerReports': summary, 'runs': results,
          'scope': 'technical ordinary-default combat checks; no art/motion/human acceptance; no fluidity claim',
          'artApproved': False, 'humanPlaytest': False, 'completedAt': datetime.now(timezone.utc).isoformat()}
f = out / ('rpg-2-star-ocean-the-second_combat-set_ordinary-default-proof_cts34-v01_' + tag + '.json')
lp(f).write_text(json.dumps(report, indent=2, default=str) + '\n', encoding='utf-8')
print('CTS34_RUNNER', report['result'], failed, f, flush=True)
sys.exit(1 if failed else 0)
