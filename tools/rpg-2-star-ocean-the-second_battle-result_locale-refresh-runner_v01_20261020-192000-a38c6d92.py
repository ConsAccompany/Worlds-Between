"""Bounded coordinator-run unit fixture; no natural-victory/playtest claim."""
import importlib.util
import json
import os
from pathlib import Path
import sys
import datetime
import uuid

root = Path(__file__).resolve().parent.parent
stage = sys.argv[1]
assert stage in ('baseline', 'fixed')
tag = datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%d-%H%M%S') + '-' + uuid.uuid4().hex[:8]
out = root / 'outputs/result-locale-v01' / (stage + '-' + tag)
out.mkdir(parents=True, exist_ok=False)
for key, sub in [('APPDATA', 'appdata'), ('LOCALAPPDATA', 'localappdata')]:
    directory = out / 'profile' / sub
    directory.mkdir(parents=True)
    os.environ[key] = str(directory)
spec = importlib.util.spec_from_file_location('checked', root / 'tools/rpg-2-star-ocean-the-second_godot_checked-runner_v01_20261018-203400-f74ac6d1.py')
checked = importlib.util.module_from_spec(spec)
spec.loader.exec_module(checked)
godot = root.parents[1] / 'tooling/godot-4-7-2/Godot_v4.7.2-stable_win64_console.exe'
test = root / 'tools/rpg-2-star-ocean-the-second_battle-result_locale-refresh-unit_v01_20261020-192000-a38c6d92.gd'
log = out / ('rpg-2-star-ocean-the-second_battle-result_locale-unit-log_' + stage + '_' + tag + '.log')
command = [str(godot), '--path', str(root / 'game'), '--resolution', '640x360', '-s', str(test), '--', str(out), tag, stage]
result = checked.run_checked(command, 90, ['RESULT_LOCALE_UNIT_OK'], log)
summary = {key: value for key, value in result.items() if key != 'log'}
summary['command'] = command
summary['rawLog'] = str(log)
summary['stage'] = stage
summary['fixture'] = 'Unit fixture: real finish callback directly, no natural victory or human playtest'
receipt = out / ('rpg-2-star-ocean-the-second_battle-result_checked-run_' + stage + '_' + tag + '.json')
receipt.write_text(json.dumps(summary, indent=2) + '\n', encoding='utf8')
print(json.dumps(summary))
print(result['log'][-2500:])
raise SystemExit(0 if result['passed'] else 1)
