"""Independent combined-checkout natural input flow and lossless-time Godot movie capture.
Scripted evidence, not a human playtest or fluidity/art/default-adoption acceptance.
"""
import os, sys, json, hashlib, importlib.util, subprocess, uuid
from pathlib import Path
from datetime import datetime, timezone

C = Path(__file__).resolve().parents[1]
P = next(p for p in C.parents if (p / 'work/tooling/godot-4-7-2').is_dir())
def lp(p):
    return Path('\\\\?\\' + str(p.resolve()))
def sha(p):
    return hashlib.sha256(lp(p).read_bytes()).hexdigest()
def module(name, p):
    spec = importlib.util.spec_from_file_location(name, p)
    m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m); return m
checked = module('checked', C / 'tools/rpg-2-star-ocean-the-second_godot_checked-runner_v01_20261018-203400-f74ac6d1.py')
media = module('media', C / 'tools/rpg-2-star-ocean-the-second_heroine-sea_motion-capture-runner_test-only-v01_20261020-153144-3fb36c1a.py')
tag = datetime.now(timezone.utc).strftime('%Y%m%d-%H%M%S') + '-' + uuid.uuid4().hex[:8]
out = C / 'outputs/hsea07'; out.mkdir(exist_ok=True)
index = 'res://data/heroine-sea-combat-v01/rpg-2-star-ocean-the-second_heroine-sea-combat_spritesheet-index_v01_20261020-201338-38ecfcb0.json'
harness = C / 'tools/rpg-2-star-ocean-the-second_heroine-natural-battle_flow-check_test-only-v01_20261020-205219-4c19e7a2.gd'
ffmpeg = media.find_ffmpeg(); ffprobe = media.ffprobe_for(ffmpeg)
results = []
for scenario, fps in [('patrol', 30), ('sentry', 60)]:
    raw = P / 'work/dual07/root-capture' / tag / scenario; raw.mkdir(parents=True)
    stem = 'rpg-2-star-ocean-the-second_' + scenario + '_raw_' + tag
    for key, suffix in [('APPDATA','a'), ('LOCALAPPDATA','l')]:
        profile = P / 'work/dual07/profiles' / (tag[-8:] + scenario[:1]) / suffix
        profile.mkdir(parents=True); os.environ[key] = str(profile)
    cmd = [str(P / 'work/tooling/godot-4-7-2/Godot_v4.7.2-stable_win64_console.exe'),
           '--resolution', '1280x720', '--position', '40,40', '--audio-driver', 'Dummy',
           '--fixed-fps', str(fps), '--write-movie', str(raw / (stem + '.png')),
           '--path', str(C / 'game'), '--script', str(harness), '--', str(out), index, tag, scenario]
    log = out / f'rpg-2-star-ocean-the-second_natural-{scenario}_root-run-v01_{tag}.log'
    r = checked.run_checked(cmd, 110, expected=[f'NATURAL_FLOW_ALL_PASS scenario={scenario}'], log_path=lp(log))
    print(scenario, r['passed'], r['reason'], r['log'][-350:], flush=True)
    assert r['passed'], r['log'][-2000:]
    frames = sorted(raw.glob(stem + '*.png')); assert frames
    movie = out / f'rpg-2-star-ocean-the-second_heroine-natural-battle_{scenario}-{"en30-bright" if scenario=="patrol" else "zh60-default"}_scripted-normal-v01_{tag}.mp4'
    cmd_enc = [str(ffmpeg), '-hide_banner', '-v', 'error', '-y', '-framerate', str(fps), '-i', str(raw / (stem + '%08d.png')),
               '-c:v','libx264','-preset','slow','-crf','18','-pix_fmt','yuv420p','-movflags','+faststart',str(movie)]
    enc = subprocess.run(cmd_enc, capture_output=True, text=True, encoding='utf-8'); assert enc.returncode == 0, enc.stderr
    pr = subprocess.run([str(ffprobe),'-v','error','-count_frames','-select_streams','v:0','-show_entries',
                         'stream=codec_name,width,height,avg_frame_rate,nb_read_frames:format=duration,size','-of','json',str(movie)],
                        capture_output=True, text=True, encoding='utf-8')
    assert pr.returncode == 0, pr.stderr
    probe = json.loads(pr.stdout); st = probe['streams'][0]
    assert st['width'] == 1280 and st['height'] == 720 and st['avg_frame_rate'] == f'{fps}/1'
    assert int(st['nb_read_frames']) == len(frames) and movie.stat().st_size <= 16*1024*1024
    flow = next(out.glob(f'*{scenario}-flow-report*{tag}.json'))
    report = json.loads(lp(flow).read_text(encoding='utf-8')); assert not report['failures']
    results.append({'scenario':scenario,'fps':fps,'checks':len(report['checks']),'command':cmd,'flowReport':flow.relative_to(C).as_posix(),
                    'log':log.relative_to(C).as_posix(),'warnings':[line for line in r['log'].splitlines() if 'WARNING' in line],
                    'movie':{'file':movie.relative_to(C).as_posix(),'sha256':sha(movie),'probe':probe},'rawFrames':len(frames),
                    'noInterpolation':True,'scriptedInput':True,'staged':False})
    print('MOVIE_PASS', scenario, len(frames), probe['format']['duration'], flush=True)
proof = {'completedAt':datetime.now(timezone.utc).isoformat(),'tag':tag,'runs':results,'allPass':True,
         'harnessSha256':sha(harness),'runnerSha256':sha(Path(__file__)),
         'sourceHashes':{rel:sha(C/rel) for rel in ['game/scripts/battle_arena.gd','game/scripts/rpg-2-star-ocean-the-second_combat-sprite-set_loader-playback_pilot-v01_20261018-153656-43a19158.gd']},
         'humanPlaytest':False,'artApproved':False,'defaultAdoption':False}
file = out / f'rpg-2-star-ocean-the-second_natural-battle_combined-root-proof-v01_{tag}.json'
lp(file).write_text(json.dumps(proof,indent=2)+'\n',encoding='utf-8'); print('ROOT_NATURAL_FLOW_PASS',file,flush=True)
