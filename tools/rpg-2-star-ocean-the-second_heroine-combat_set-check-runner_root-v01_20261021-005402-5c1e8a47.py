"""Independent technical set check of the opt-in heroine combat set at the current HEAD.
Reuses existing harnesses on throwaway git-archive exports (HEAD and default-off base 11973af)
so import side effects never touch the worktree. Scripted evidence only: no art approval,
no human playtest, no default adoption. Usage: python -I <this>
"""
import os, sys, json, hashlib, importlib.util, subprocess, uuid, tarfile, io
from pathlib import Path
from datetime import datetime, timezone

C = Path(__file__).resolve().parents[1]
P = next(p for p in C.parents if (p / 'work/tooling/godot-4-7-2').is_dir())
def lp(p): return Path('\\\\?\\' + str(Path(p).resolve()))
def sha(p): return hashlib.sha256(lp(p).read_bytes()).hexdigest()
spec = importlib.util.spec_from_file_location('checked', C / 'tools/rpg-2-star-ocean-the-second_godot_checked-runner_v01_20261018-203400-f74ac6d1.py')
checked = importlib.util.module_from_spec(spec); spec.loader.exec_module(checked)
godot = P / 'work/tooling/godot-4-7-2/Godot_v4.7.2-stable_win64_console.exe'
tag = datetime.now(timezone.utc).strftime('%Y%m%d-%H%M%S') + '-' + uuid.uuid4().hex[:8]
out = C / 'outputs/hsc-v01' / tag; out.mkdir(parents=True)
tmp = Path(os.environ['LOCALAPPDATA']) / 'Temp/hsc' / tag[-8:]; tmp.mkdir(parents=True)
head = subprocess.run(['git', '-C', str(C), 'rev-parse', 'HEAD'], capture_output=True, text=True, check=True).stdout.strip()
BASE = '11973af6492ef60a99ca1f2eacb01e12c091ccb9'
INDEX = 'res://data/heroine-sea-combat-v01/rpg-2-star-ocean-the-second_heroine-sea-combat_spritesheet-index_v01_20261020-201338-38ecfcb0.json'
results = []; failed = []

def export(rev, name, paths):
    dst = tmp / name; dst.mkdir()
    data = subprocess.run(['git', '-C', str(C), '-c', 'core.autocrlf=false', 'archive', '--format=tar', rev] + paths, capture_output=True, check=True).stdout
    with tarfile.open(fileobj=io.BytesIO(data)) as t:
        for m in t.getmembers():
            if not m.isfile(): continue
            target = Path(str(lp(dst)) + '\\' + m.name.replace('/', '\\'))
            assert '..' not in m.name.split('/'), m.name
            os.makedirs(target.parent, exist_ok=True); target.write_bytes(t.extractfile(m).read())
    return dst

def run(name, root, script=None, extra=(), headless=True, marker=None, editor=False, res='640x360', timeout=150):
    env = dict(os.environ)
    for k in ['APPDATA', 'LOCALAPPDATA']:
        p = tmp / 'prof' / (name + '-' + k[0]); p.mkdir(parents=True); env[k] = str(p)
    cmd = [str(godot)] + (['--headless'] if headless else ['--resolution', res, '--position', '2000,100', '--audio-driver', 'Dummy']) + ['--path', str(root / 'game')]
    if editor: cmd += ['--editor', '--import', '--quit']
    if script: cmd += ['--script', str(script)]
    if extra: cmd += ['--'] + [str(x) for x in extra]
    old = dict(os.environ); os.environ.clear(); os.environ.update(env)
    log = out / ('rpg-2-star-ocean-the-second_heroine-combat_' + name + '_set-check-log_' + tag + '.log')
    try: r = checked.run_checked(cmd, timeout, expected=([marker] if marker else []), log_path=lp(log))
    finally: os.environ.clear(); os.environ.update(old)
    text = r['log']
    rec = {k: v for k, v in r.items() if k != 'log'} | {'name': name, 'command': cmd, 'log': log.relative_to(C).as_posix(),
           'warnings': [x for x in text.splitlines() if 'WARNING' in x], 'errorLines': [x for x in text.splitlines() if 'ERROR' in x]}
    if rec['errorLines'] and rec['passed']: rec['passed'] = False; rec['reason'] = 'ERROR line present'
    results.append(rec); print(name, rec['passed'], rec['reason'], text.splitlines()[-2:] if text else '', flush=True)
    if not rec['passed']: failed.append(name)
    return rec

# 1. Package (frames, pivots, authored ticks, loop starts, all eight actions, source hashes) - no Godot.
pv = out / ('rpg-2-star-ocean-the-second_heroine-combat_package-verify_set-check-report_' + tag + '.json')
r = subprocess.run([sys.executable, '-I', str(C / 'tools/rpg-2-star-ocean-the-second_heroine-sea-combat_package-verifier_v01_20261020-201338-38ecfcb0.py'), '--report', str(pv)],
                   capture_output=True, text=True, encoding='utf-8', errors='replace', cwd=str(C))
vr = json.loads(lp(pv).read_text(encoding='utf-8')) if lp(pv).is_file() else {}
vchecks = vr.get('checks', []); vfail = sorted(c['id'] for c in vchecks if not c['pass'])
# base_revision/scope_untracked assert the producer checkout state (HEAD==11973af, no other untracked files);
# they fail at any later revision by construction. Retained as raw failures, reported separately from content.
STATE = {'base_revision', 'scope_untracked'}
pk = {'name': 'package-verifier', 'verifierExit': r.returncode, 'checks': len(vchecks), 'rawFailed': vfail,
      'checkoutStateFailures': sorted(set(vfail) & STATE), 'contentFailures': sorted(set(vfail) - STATE),
      'passed': bool(vchecks) and not (set(vfail) - STATE) and 'Traceback' not in r.stderr,
      'tail': (r.stdout + r.stderr)[-1500:], 'report': pv.relative_to(C).as_posix()}
results.append(pk); print('package-verifier', pk['passed'], pk['tail'][-300:], flush=True)
if not pk['passed']: failed.append('package-verifier')

# 2. Exports and imports.
H = export(head, 'h', ['game', 'tools']); B = export(BASE, 'b', ['game'])
run('head-import', H, editor=True); run('base-import', B, editor=True)
T = H / 'tools'
run('rational220', H, T / 'rpg-2-star-ocean-the-second_combat-rational-clock_root-check_v01_20261020-201636-582fa0ef.gd', marker='ROOT_RATIONAL_CLOCK_PASS checks=220')
run('contact80', H, T / 'rpg-2-star-ocean-the-second_heroine-contact_timing-check_v01_20261020-203500-c7e41a2d.gd', marker='HEROINE_CONTACT PASS checks=80')
run('facing251', H, T / 'rpg-2-star-ocean-the-second_heroine-contact_facing-root-check_v01_20261020-205251-5a7d3155.gd', [out / ('rpg-2-star-ocean-the-second_heroine-combat_facing-report_set-check_' + tag + '.json')], marker='ROOT_FACING_PASS checks=251')
run('shared-bonus16', H, T / 'rpg-2-star-ocean-the-second_heroine-contact_shared-bonus-root-check_v01_20261020-205136-2f7329fb.gd', [out / ('rpg-2-star-ocean-the-second_heroine-combat_bonus-report_set-check_' + tag + '.json')], marker='ROOT_SHARED_BONUS_PASS checks=')
run('half273', H, T / 'rpg-2-star-ocean-the-second_combat-half-scale_check_v01_20261020-154048-7d4bddce.gd', marker='COMBAT_HALF_SCALE PASS checks=273 failures=0')
cap = out / 'cap'; cap.mkdir()
run('normal-input46', H, T / 'rpg-2-star-ocean-the-second_heroine-contact_normal-input-root-check_v01_20261020-202215-d3fc3728.gd', [cap, INDEX, tag], headless=False, res='1280x720', marker='ROOT_NORMAL_CONTACT_PASS checks=')
legacy = 'game/tests/rpg-2-star-ocean-the-second_combat-sprite-set_pilot-check-capture_v01_20261018-153656-9efd4413.gd'
bdir = out / 'base640'; bdir.mkdir(); cdir = out / 'head640'; cdir.mkdir()
run('base-default-off-capture', B, B / legacy, ['--baseline-only', '--capture-dir=' + str(bdir)], headless=False, marker='COMBAT_SET_PILOT BASELINE PASS')
run('legacy-default-off-and-actions640', H, H / legacy, ['--baseline-dir=' + str(bdir), '--capture-dir=' + str(cdir)], headless=False, marker='COMBAT_SET_PILOT PASS')
nat = out / 'natural'; nat.mkdir()
run('natural-patrol', H, T / 'rpg-2-star-ocean-the-second_heroine-natural-battle_flow-check_test-only-v01_20261020-205219-4c19e7a2.gd', [nat, INDEX, tag, 'patrol'], headless=False, res='1280x720', marker='NATURAL_FLOW_ALL_PASS scenario=patrol')

src = ['game/scripts/battle_arena.gd', 'game/scripts/rpg-2-star-ocean-the-second_combat-sprite-set_loader-playback_pilot-v01_20261018-153656-43a19158.gd',
       'game/data/heroine-sea-combat-v01/rpg-2-star-ocean-the-second_heroine-sea-combat_spritesheet_v01_20261020-201338-38ecfcb0.png',
       'game/data/heroine-sea-combat-v01/rpg-2-star-ocean-the-second_heroine-sea-combat_spritesheet-manifest_v01_20261020-201338-38ecfcb0.json',
       'game/data/heroine-sea-combat-v01/rpg-2-star-ocean-the-second_heroine-sea-combat_spritesheet-index_v01_20261020-201338-38ecfcb0.json']
report = {'task': 'qa.combat.protagonist-female.set-check', 'result': 'FAIL' if failed else 'PASS', 'failed': failed, 'testedRevision': head, 'defaultOffBase': BASE,
          'hashNormalization': 'sha256-bytes of git-archive export with core.autocrlf=false (= committed blob bytes)',
          'sourceSha256': {s: sha(H / s) for s in src}, 'runs': results, 'artApproved': False, 'humanPlaytest': False, 'defaultAdoption': False,
          'completedAt': datetime.now(timezone.utc).isoformat()}
f = out / ('rpg-2-star-ocean-the-second_heroine-combat_set-check-proof_root-v01_' + tag + '.json')
lp(f).write_text(json.dumps(report, indent=2, default=str) + '\n', encoding='utf-8')
print('SET_CHECK', report['result'], failed, f, flush=True)
sys.exit(1 if failed else 0)
