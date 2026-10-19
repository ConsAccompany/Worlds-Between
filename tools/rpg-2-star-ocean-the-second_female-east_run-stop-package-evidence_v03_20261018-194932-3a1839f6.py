"""EAST v03 production package evidence: bind native PXOs, boundary matrix, root body report and
actual ordinary-Input captures to the locked model; copy only compact evidence into outputs/.

Usage (checkout root, Codex-runtime Python 3.12): python -I <this> <temp root>
<temp root> holds bake_a/, cap30/, cap60/, cap30.log, cap60.log, the two normal1x .mp4 files,
trans_v03.json and v02np/all/ (v02 renderer phases, comparison only). Raw capture PNG
sequences and full-frame bake PNGs stay in Temp. Text hashes sha256-text-lf-v1 (CRLF->LF);
binary sha256-bytes; .json.gz entries also record the uncompressed sha256.
"""
from pathlib import Path
import gzip, hashlib, io, json, os, subprocess, sys, zipfile
import numpy as np
from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
SLUG = 'rpg-2-star-ocean-the-second'
TAG = 'v03_20261018-194932-3a1839f6'
OUT = ROOT / 'outputs/female-east-run-v03'
CORE = 'tools/rpg-2-star-ocean-the-second_female-east_run-stop-source_unapproved-v03_20261018-193030-48da69c1.gd'
CORE_SHA = 'e783de5d8ab6b1e3f678299eb8cffde11109d1aab06c47155831ebc4388bb07f'
NATIVE_MANIFEST = f'outputs/female-east-run-v03/{SLUG}_female-east-run-stop_native-source-manifest_unapproved-{TAG}.json'
NATIVE_REPORT = f'outputs/female-east-run-v03/{SLUG}_female-east-run-stop_native-report_{TAG}.json'
BODY = 'outputs/female-east-run-v03/rpg-2-star-ocean-the-second_female-east_body-continuity-report_v03_20261018-193030-6d8bd4ef.json'
BODY_CHECKER = 'tools/rpg-2-star-ocean-the-second_female-east_rendered-coat-projection-trajectory-check_test-only-v02_20261018-193030-5ce91065.gd'
ROOT_SLOW = ['outputs/female-east-run-v03/rpg-2-star-ocean-the-second_female-east_traj_v01_slow-failure-evidence_v01_20261018-193030-113d603b.json.gz',
             'outputs/female-east-run-v03/rpg-2-star-ocean-the-second_female-east_traj_v02b_slow-failure-evidence_v01_20261018-193030-113d603b.json.gz']
WEST_STATIC = 'outputs/female-west-static-v01/rpg-2-star-ocean-the-second_protagonist-female_west-static_unapproved-v01_20261018-174421-618816ac.png'
PRESERVED = ['outputs/female-east-run-v01/rpg-2-star-ocean-the-second_female-east-run_prototype-evidence-manifest_v01_20261018-184444-8aa2a7e3.json',
             'outputs/female-east-run-v02/rpg-2-star-ocean-the-second_female-east-run_native-poses-report_v02_20261018-190542-52b0e405.json',
             'outputs/female-east-run-v02/rpg-2-star-ocean-the-second_female-east-run_normal1x-annex-room2-dark-zh-60fps_v02_20261018-190542-52b0e405.mp4']
TOOLS = [CORE,
         'tools/rpg-2-star-ocean-the-second_female-east_run-stop-native-bake_test-only-v03_20261018-194932-3a1839f6.gd',
         'tools/rpg-2-star-ocean-the-second_female-east_run-stop-native-package_v03_20261018-194932-3a1839f6.py',
         'tools/rpg-2-star-ocean-the-second_female-east_run-stop-transition-check_test-only-v03_20261018-194932-3a1839f6.gd',
         'tools/rpg-2-star-ocean-the-second_female-east_run-stop-actual-prototype_test-only-v03_20261018-194932-3a1839f6.gd',
         'tools/rpg-2-star-ocean-the-second_female-east_run-stop-package-evidence_v03_20261018-194932-3a1839f6.py',
         'tools/rpg-2-star-ocean-the-second_female-east_run-stop-evidence-check_v03_20261018-194932-3a1839f6.py']
PROTECTED = ['game/scripts/app_state.gd', 'game/scripts/scifi_exploration_area.gd', 'game/scripts/survey_annex.gd', 'game/project.godot',
             'game/scenes/scifi_exploration_area.tscn', 'game/scenes/survey_annex.tscn']
SCENES = [(30, 'city-bright', 'en', 120), (60, 'annex-room2-dark', 'zh', 238)]
QA = f'docs/qa/{SLUG}_female-east-run-stop_produced-candidate-unapproved-{TAG}.md'


def long(p):
    s = str(Path(p).resolve()); prefix = chr(92) * 2 + '?' + chr(92)
    return prefix + s if os.name == 'nt' and not s.startswith(prefix) else s


def read(p): return Path(long(p)).read_bytes()
def write(p, b): Path(long(p)).write_bytes(b)
def sha(b): return hashlib.sha256(b).hexdigest()
def tsha(b): return sha(b.replace(b'\r\n', b'\n'))
def rgba(b): return np.array(Image.open(io.BytesIO(b)).convert('RGBA'))
def rel(p): return Path(p).resolve().relative_to(ROOT.resolve()).as_posix()


def gz(src_bytes, name):
    write(OUT / name, gzip.compress(src_bytes, compresslevel=9, mtime=0))
    return {'file': rel(OUT / name), 'sha256': sha(read(OUT / name)), 'uncompressedSha256': sha(src_bytes)}


def main():
    T = Path(sys.argv[1]); checks = {}
    def check(k, v, detail=None):
        checks[k] = {'pass': bool(v), 'detail': detail}
    core_before = sha(read(ROOT / CORE)); check('model_locked_before', core_before == CORE_SHA)
    n = json.loads(read(ROOT / NATIVE_MANIFEST)); nr = json.loads(read(ROOT / NATIVE_REPORT))
    check('native_report_all_gates', not nr['failedGates'] and nr['passed'] == nr['total'], [nr['passed'], nr['total']])
    check('native_report_binds_manifest', nr['manifestSha256'] == sha(read(ROOT / NATIVE_MANIFEST)))
    check('native_model_bound', n['modelSha256Bytes'] == CORE_SHA and nr['modelSha256Before'] == nr['modelSha256After'] == CORE_SHA)
    native = {r['index']: r['rgbaSha256'] for r in n['sets']['run']['frames']}
    east_static = n['sets']['stop']['frames'][-1]['rgbaSha256']
    west_static = sha(rgba(read(ROOT / WEST_STATIC)).tobytes())
    # Boundary matrix.
    tr_raw = read(T / 'trans_v03.json'); tr = json.loads(tr_raw)
    check('transition_all_pass', tr['failed'] == 0 and tr['passed'] == 25381, [tr['passed'], tr['failed']])
    check('transition_model_bound', tr['modelSha256Before'] == tr['modelSha256After'] == CORE_SHA and not tr['invalidated'])
    maxima = {}
    for c in tr['checks']:
        s = c['key'].split('-')[0]
        for label, part in [('settleSeconds', '-settle-deadline-'), ('raisedFootLandingSeconds', '-raised-foot-deadline-'), ('repressFirstSupportSeconds', '-repress-landing-')]:
            if part in c['key']:
                maxima.setdefault(label, {}); maxima[label][s] = max(maxima[label].get(s, 0), c['detail'])
    families = {}
    for c in tr['checks']:
        fam = '-'.join(w for w in c['key'].split('-') if not w.isdigit())
        families[fam] = families.get(fam, 0) + 1
    # Root body report: bound, not rerun.
    body_raw = read(ROOT / BODY); body = json.loads(body_raw)
    check('root_body_report_valid', body['valid'] and body['failed'] == 0 and body['passed'] == 15744 and body['modelSha256'] == CORE_SHA, [body['passed'], body['failed']])
    body_checker = ROOT / BODY_CHECKER
    body_checker_sha = sha(read(body_checker)) if Path(long(body_checker)).exists() else None
    check('root_body_checker_bytes_match_report', body_checker_sha == body['checkerSha256'], body_checker_sha)
    # Actual captures.
    captures = []
    for fps, scene, lang, count in SCENES:
        folder = T / f'cap{fps}'
        report_path = next(folder.glob('*actual-report*.json')); raw = read(report_path); r = json.loads(raw)
        key = f'{scene}-{fps}'
        check(key + ':internal_checks', r['failed'] == 0 and r['passed'] == count * 4, [r['passed'], r['failed']])
        check(key + ':model_bound', r['modelSha256'] == CORE_SHA)
        check(key + ':fps_language_frames', r['fps'] == fps and r['language'] == lang and len(r['frames']) == count and r['scene'] == scene)
        frames = r['frames']; files_ok = True; imgs = {}
        for f in frames:
            data = read(folder / f['file']); files_ok &= sha(data) == f['sha256']; imgs[f['tick']] = rgba(data)
        check(key + ':capture_png_hashes', files_ok)
        steady = [f for f in frames if f['steadyRun']]
        torso_eq = [f for f in steady if f['torsoEqualsNativeCel']]
        held = [f for f in steady if not f['torsoEqualsNativeCel']]
        check(key + ':steady_equals_native_cel', torso_eq and all(f['sourceRgbaSha256'] == native[int(f['state']['q'])] for f in torso_eq),
              {'steady': len(steady), 'torsoEqual': len(torso_eq), 'guardHeld': len(held)})
        idle = [f for f in frames if f['state']['mode'] == 'idle']
        check(key + ':idle_equals_east_static', idle and all(f['sourceRgbaSha256'] == east_static for f in idle), len(idle))
        rev = [f for f in frames if f['state']['mode'] == 'reverse-placeholder']
        check(key + ':reversal_is_west_static_placeholder', rev and all(f['sourceRgbaSha256'] == west_static for f in rev), len(rev))
        check(key + ':final_frame_exact_static', frames[-1]['state']['mode'] == 'idle' and frames[-1]['sourceRgbaSha256'] == east_static)
        check(key + ':sprite_at_source_renderx', all(abs(f['state']['renderX'] - round(f['heroX'] * 2) / 2) < 1e-9 and f['spriteCanvasOrigin'][0] == f['state']['renderX']
                                                     and f['spriteCanvasOrigin'][1] == frames[0]['spriteCanvasOrigin'][1] and f['spriteCanvasScale'] == [.5, .5]
                                                     and f['spriteOffset'] == [-40, -104] for f in frames))
        # Capture/source deltas: when neither the source RGBA nor the sprite origin changed, the
        # unambiguous sprite texels on screen must be unchanged; otherwise record measured deltas.
        deltas = []; static_pairs = 0; static_pair_changes = 0; screen = [0, 0]; screen_frames = 0
        for a, b in zip(frames, frames[1:]):
            ia, ib = imgs[a['tick']], imgs[b['tick']]
            ox, oy = b['spriteCanvasOrigin']
            x0, y0 = int(ox) - 21, int(oy) - 53
            win = (ia[y0:y0 + 54, x0:x0 + 42, :3] != ib[y0:y0 + 54, x0:x0 + 42, :3]).any(2)
            whole = int((ia[:, :, :3] != ib[:, :, :3]).any(2).sum())
            same_src = a['sourceRgbaSha256'] == b['sourceRgbaSha256'] and a['spriteCanvasOrigin'] == b['spriteCanvasOrigin']
            if same_src:
                static_pairs += 1; static_pair_changes += int(win.sum())
            deltas.append([b['tick'], round(b['heroX'] - a['heroX'], 6), b['state']['renderX'] - a['state']['renderX'], same_src, int(win.sum()), whole])
        check(key + ':unchanged_source_unchanged_sprite_window', static_pairs > 0 and static_pair_changes == 0, {'pairs': static_pairs, 'changedPixels': static_pair_changes})
        # Diagnostic only: screen pixel vs the unambiguous 2x2 source block it samples at scale 0.5.
        bake = {r_['rgbaSha256']: r_['tempPng'] for s in n['sets'].values() for r_ in s['frames']}
        for f in frames:
            if f['sourceRgbaSha256'] not in bake: continue
            s = rgba(read(Path(n['fullFramePngsTempOnly']) / bake[f['sourceRgbaSha256']])); cap = imgs[f['tick']]
            ox, oy = f['spriteCanvasOrigin']; screen_frames += 1
            for Y in range(int(oy) - 60, int(oy) + 4):
                for X in range(int(ox) - 24, int(ox) + 24):
                    tx = int(round(2 * (X + .5 - ox) + 40)); ty = int(round(2 * (Y + .5 - oy) + 104))
                    if not (1 <= tx < 80 and 1 <= ty < 112): continue
                    blk = s[ty - 1:ty + 1, tx - 1:tx + 1].reshape(-1, 4)
                    if not (blk[:, 3] == 255).all() or not (blk == blk[0]).all(): continue
                    screen[1] += 1; screen[0] += int((cap[Y, X, :3] == blk[0, :3]).all())
        movie = next(T.glob(f'*normal1x-{scene}-{lang}-{fps}fps_{TAG}.mp4'))
        probe = json.loads(subprocess.run(['ffprobe', '-v', 'error', '-select_streams', 'v:0', '-count_frames', '-show_entries',
                                           'stream=codec_name,width,height,r_frame_rate,nb_read_frames,pix_fmt', '-of', 'json', str(movie)],
                                          capture_output=True, text=True, encoding='utf-8').stdout)['streams'][0]
        check(key + ':movie_normal1x', probe['width'] == 640 and probe['height'] == 360 and probe['r_frame_rate'] == f'{fps}/1' and probe['nb_read_frames'] == str(count), probe)
        log = read(T / f'cap{fps}.log').replace(b'\r\r\n', b'\n').replace(b'\r\n', b'\n')
        check(key + ':log_clean', b'ERROR' not in log and b'SCRIPT' not in log and f'captured {count} actualframes'.encode() in log)
        # Store compact evidence.
        write(OUT / movie.name, read(movie))
        log_name = f'{SLUG}_female-east-run_actual-log-{scene}-{lang}-{fps}fps_{TAG}.log'; write(OUT / log_name, log)
        stored_report = gz(raw, f'{SLUG}_female-east-run_actual-report-{scene}-{lang}-{fps}fps_{TAG}.json.gz')
        start = [f for f in torso_eq if f['segment'] == 'start-run']
        picks = [(label, min(start, key=lambda f: abs((f['state']['q'] - q + 64) % 128 - 64))) for label, q in [('contact', 0), ('passing', 19), ('flight', 51)]]
        picks.append(('release-first', next(f for f in frames if f['segment'] == 'release')))
        picks.append(('repress-first', next(f for f in frames if f['segment'] == 'repress')))
        picks.append(('settle-before-idle', next(f for f in reversed(frames) if f['segment'] == 'final-stop' and f['state']['mode'] == 'stop')))
        picks.append(('final-static', frames[-1]))
        critical = []
        for label, f in picks:
            name = f'{SLUG}_female-east-run_critical-{scene}-{lang}-{label}-640_{TAG}.png'
            write(OUT / name, read(folder / f['file']))
            critical.append({'purpose': label, 'tick': f['tick'], 'segment': f['segment'], 'mode': f['state']['mode'], 'q': f['state']['q'],
                             'file': rel(OUT / name), 'sha256': f['sha256'], 'sourceRgbaSha256': f['sourceRgbaSha256']})
        captures.append({'scene': scene, 'language': lang, 'fps': fps, 'frames': count, 'simulationSeconds': count / fps, 'recordingWallClockMs': r['recordingWallClockMs'],
                         'report': stored_report, 'log': {'file': rel(OUT / log_name), 'sha256': sha(log)},
                         'movie': {'file': rel(OUT / movie.name), 'sha256': sha(read(OUT / movie.name)), 'probe': probe},
                         'steadyRunFrames': len(steady), 'steadyEqualNativeCel': len(torso_eq), 'steadyTorsoGuardHeld': len(held),
                         'idleFrames': len(idle), 'reversalPlaceholderFrames': len(rev),
                         'captureSourceDeltas': {'columns': ['tick', 'heroDeltaX', 'renderDeltaX', 'sourceAndOriginUnchanged', 'spriteWindowChangedPixels', 'wholeFrameChangedPixels'], 'rows': deltas},
                         'unchangedSourcePairs': static_pairs,
                         'onScreenSpriteTexelDiagnostic': {'framesCompared': screen_frames, 'unambiguousTexelsMatched': screen[0], 'unambiguousTexelsCompared': screen[1],
                                                           'scope': 'Not a gate. Remaining pixels are covered by scene overlays (y-sorted NPC/props, name labels, interaction markers).'},
                         'critical': critical, 'rawFramesTempOnly': str(folder)})
    # v02 renderer comparison (disclosure only).
    v02_same = []; v02_changed = []
    for r_ in n['sets']['run']['frames']:
        a = np.array(Image.open(T / 'v02np' / 'all' / ('q%03d.png' % r_['index'])).convert('RGBA'))
        b = rgba(read(Path(n['fullFramePngsTempOnly']) / r_['tempPng']))
        d = int((a != b).any(2).sum()); (v02_same if d == 0 else v02_changed).append(d)
    # Protected game sources unchanged from HEAD.
    head = subprocess.run(['git', 'rev-parse', 'HEAD'], cwd=ROOT, capture_output=True, text=True).stdout.strip()
    protected = {}
    for p in PROTECTED:
        base = subprocess.run(['git', 'show', 'HEAD:' + p], cwd=ROOT, capture_output=True).stdout
        protected[p] = tsha(read(ROOT / p)); check('unchanged:' + p, protected[p] == tsha(base) and base != b'')
    check('model_locked_after', sha(read(ROOT / CORE)) == CORE_SHA)
    stored_transition = gz(tr_raw, f'{SLUG}_female-east-run_exact-boundary-report_{TAG}.json.gz')
    failed = [k for k, v in checks.items() if not v['pass']]
    files = {}
    package = [p for p in OUT.glob(f'*{TAG}*') if 'evidence-manifest' not in p.name] + [ROOT / p for p in TOOLS[1:] if Path(long(ROOT / p)).exists()]
    if Path(long(ROOT / QA)).exists(): package.append(ROOT / QA)
    for p in sorted(package):
        data = read(p); text = p.suffix in ('.py', '.gd', '.md', '.json', '.log')
        files[rel(p)] = {'sha256': tsha(data) if text else sha(data), 'textLf': text, 'bytes': len(data)}
    m = {'task': 'content.char.protagonist-female.walk-east', 'stage': 'v03 production package (one EAST run + representative stop), produced candidate only',
         'approval': {'art': False, 'motion': False, 'fluidity': False, 'fullSprite': False, 'ledgerUpdated': False},
         'hashNormalization': {'text': 'sha256-text-lf-v1 (CRLF->LF only) for .py/.gd/.md/.json/.log', 'binary': 'sha256-bytes', 'gz': 'file sha256-bytes + uncompressedSha256'},
         'baseRevision': head, 'model': {'path': CORE, 'sha256Bytes': CORE_SHA, 'before': core_before, 'after': sha(read(ROOT / CORE))},
         'nativeManifest': NATIVE_MANIFEST, 'nativeReport': NATIVE_REPORT,
         'nativeExport': [{k: j[k] for k in ('kind', 'exit', 'cells', 'exact', 'knownInheritedShaderDiagnostics', 'unexpectedDiagnostics', 'cleanAppSuccess')} for j in nr['native']],
         'exactBoundary': {'report': stored_transition, 'passed': tr['passed'], 'failed': tr['failed'], 'durationSeconds': tr['durationSeconds'], 'checkFamilies': families,
                           'maxima': maxima, 'seedSource': tr['seedSource'],
                           'limits': {'settleSeconds': '<=0.250001 at 30/60, <=0.300001 mixed', 'raisedFootLandingSeconds': '<=0.100001', 'repressFirstSupportSeconds': '<=0.100001'}},
         'rootBodyReport': {'file': BODY, 'sha256Bytes': sha(body_raw), 'checker': BODY_CHECKER, 'checkerSha256': body['checkerSha256'], 'passed': body['passed'],
                            'checkCount': body['checkCount'], 'durationSeconds': body['durationSeconds'],
                            'summary': {s: {k: v for k, v in x.items() if k != 'worstRiseCase'} for s, x in body['summary'].items()},
                            'fullStopRendersRetainedMeaning': 'projection.fullStopRendersRetained=384 counts the initial (release) frame render of each of 384 full plain-stop sequences (128 phases x 3 schedules); every later settle frame of those sequences was also fully rendered but is not counted there. It is not the total number of full render_pose calls.',
                            'notRerun': True, 'slowFailureEvidence': {p: sha(read(ROOT / p)) for p in ROOT_SLOW}},
         'captures': captures,
         'v02RendererComparison': {'identicalRunCels': len(v02_same), 'changedRunCels': len(v02_changed), 'changedTexelsMin': min(v02_changed) if v02_changed else 0,
                                   'changedTexelsMax': max(v02_changed) if v02_changed else 0,
                                   'cause': 'v03 rounds/guards the torso y; render_pose places the near-arm shoulder at the continuous body, so the arm pivot is now integer-aligned. Representative q000/q019/q051 and the q060 stop sequence are byte-identical to v02.'},
         'preservedEarlierEvidence': {p: sha(read(ROOT / p)) for p in PRESERVED},
         'protectedGameSourcesHead': protected,
         'checks': checks, 'passed': len(checks) - len(failed), 'total': len(checks), 'failed': failed,
         'files': files,
         'limitations': ['WEST input shows the produced WEST static placeholder; no WEST motion or reversal animation is claimed.',
                         'Test-only presenter: no game/default/navigation/registry/Site/ledger change; the game still shows its existing hero.',
                         'Pixelorama CLI reopen/export is exact but every process prints 4 inherited headless shader-compiler diagnostics: not a clean-app result. No GUI Save As/reopen claim for EAST.',
                         'Native PXO cels are the 280 Hz reference states; live 30/60 fps uses the same controller and may hold the torso 1 source px for a frame (0 such steady frames in these two captures).',
                         'Bright 30 fps idle start position is partly covered by scene overlays (inherited lane); one language per scene.']}
    mp = OUT / f'{SLUG}_female-east-run-stop_evidence-manifest_{TAG}.json'
    write(mp, (json.dumps(m, indent=2) + '\n').encode('utf-8'))
    print(rel(mp)); print('EAST V03 EVIDENCE', m['passed'], '/', m['total'], 'failed', failed)
    print('files', len(files), 'bytes', sum(v['bytes'] for v in files.values()))
    if failed: raise SystemExit(1)


if __name__ == '__main__':
    main()
