"""Build a Windows DEVELOPER PLAYTEST bundle: unchanged vendor Godot runtimes + current game PCK + .cmd launcher.

Not a native release export, not art/release acceptance. No export templates are used (--export-pack only).
Steps, each gated (checked runner: diagnostics, exit code and expected markers fail):
  1. preflight: global stop absent, vendor runtime sizes, protected-source hashes, git status snapshot
  2. git archive <commit>:game into a clean source tree (no dirty-checkout files), raw hashes recorded
  3. headless import + --export-pack "Windows Desktop" (existing preset, unedited) in isolated APPDATA/LOCALAPPDATA
  4. engine license/copyright dump via the engine's own Engine.get_license_* data
  5. bundle assembly, smoke from an EMPTY dir (console runtime + PCK, no --path game), launcher smoke from a path with spaces
  6. protected sources/git status unchanged -> manifest -> ZIP (only after every check passed)
Run: <python> tools/<this file>
"""
from datetime import datetime, timezone
from pathlib import Path
import argparse, hashlib, importlib.util, io, json, os, shutil, subprocess, sys, tarfile, uuid, zipfile

SLUG = 'rpg-2-star-ocean-the-second'
TOOL_ID = '20261022-202347-7fea20f0'
COMMIT = 'd5f204373c17c62e45e92dea14c3a2e85c525062'
ROOT = Path(__file__).resolve().parents[1]
PRIMARY = ROOT.parents[1]
VENDOR = PRIMARY / 'work/tooling/godot-4-7-2'
GUI = VENDOR / 'Godot_v4.7.2-stable_win64.exe'
CONSOLE = VENDOR / 'Godot_v4.7.2-stable_win64_console.exe'
EXPECTED_SIZES = {GUI.name: 180858888, CONSOLE.name: 198152}
WORK = ROOT / f'work/play54-{TOOL_ID}'
PRODUCER = ROOT / 'outputs/play54/producer'
RUNNER_PATH = ROOT / 'tools/rpg-2-star-ocean-the-second_godot_checked-runner_v01_20261018-203400-f74ac6d1.py'
LICENSE_GD = ROOT / f'tools/{SLUG}_mvp_engine-license-dump_v01_{TOOL_ID}.gd'
STOP = PRIMARY / 'work/dual01/control/rpg-2-star-ocean-the-second_dual-provider_global-stop_v01_20261019-001423-861097ca.json'
OWN_SCOPES = ('work/play54-', 'outputs/play54/', f'_{TOOL_ID}.')
TIMEOUT_IMPORT, TIMEOUT_EXPORT, TIMEOUT_SHORT = 420, 300, 60
LABEL = 'DEVELOPER PLAYTEST BUILD - runtime+PCK bundle, not a native release export, not art or release acceptance.'


def long(p):
    """Extended-length path string; LongPathsEnabled is 0 on this machine."""
    s = str(Path(p).resolve())
    return s if s.startswith('\\\\?\\') else '\\\\?\\' + s


def sha(p):
    h = hashlib.sha256()
    with open(long(p), 'rb') as f:
        for block in iter(lambda: f.read(1 << 20), b''):
            h.update(block)
    return h.hexdigest()


def rel(p):
    return Path(p).resolve().relative_to(ROOT).as_posix()


def git(*args):
    r = subprocess.run(['git', '-C', str(ROOT), *args], capture_output=True, timeout=120)
    if r.returncode != 0:
        raise SystemExit(f'git {args} failed: {r.stderr.decode("utf-8", "replace")}')
    return r.stdout


def foreign_status():
    """git status minus this task's own write scopes; must be identical before and after."""
    lines = git('status', '--porcelain=v1', '--untracked-files=all').decode('utf-8', 'replace').splitlines()
    return sorted(l for l in lines if not any(s in l for s in OWN_SCOPES))


class Gate:
    def __init__(self, tag):
        spec = importlib.util.spec_from_file_location('checked_runner', RUNNER_PATH)
        self.runner = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(self.runner)
        self.tag, self.steps = tag, []

    def run(self, name, command, timeout, expected=(), cwd=None):
        if STOP.exists():
            raise SystemExit('GLOBAL STOP present')
        log = PRODUCER / f'{SLUG}_play54_{name}-log_v01_{self.tag}.log'
        old = os.getcwd()
        if cwd:
            os.chdir(cwd)
        try:
            result = self.runner.run_checked(command, timeout, expected=list(expected), log_path=log)
        finally:
            os.chdir(old)
        result.pop('log', None)
        step = {'step': name, 'command': command, 'cwd': str(cwd or old), 'timeoutSeconds': timeout,
                'expectedMarkers': list(expected), 'log': rel(log), **result}
        self.steps.append(step)
        print(f'[{name}] passed={result["passed"]} reason={result["reason"]} exit={result["exitCode"]} '
              f'{result["elapsedSeconds"]}s', flush=True)
        if not result['passed']:
            raise GateFailure(step)
        return step


class GateFailure(Exception):
    pass


def extract_archive(dest):
    tar_path = WORK / f'{SLUG}_play54_game-source-archive_v01_{TOOL_ID}.tar'
    with open(long(tar_path), 'wb') as f:
        r = subprocess.run(['git', '-C', str(ROOT), 'archive', '--format=tar', COMMIT, 'game'],
                           stdout=f, stderr=subprocess.PIPE, timeout=300)
    if r.returncode != 0:
        raise SystemExit('git archive failed: ' + r.stderr.decode('utf-8', 'replace'))
    hashes = {}
    with tarfile.open(long(tar_path)) as t:
        for m in t.getmembers():
            target = Path(long(dest)) / m.name
            if m.isdir():
                os.makedirs(target, exist_ok=True)
            elif m.isfile():
                os.makedirs(target.parent, exist_ok=True)
                data = t.extractfile(m).read()
                with open(target, 'wb') as out:
                    out.write(data)
                hashes[m.name] = hashlib.sha256(data).hexdigest()
            else:
                raise SystemExit(f'unexpected archive member type: {m.name}')
    os.remove(long(tar_path))
    return hashes


def verify_sources(src, game_hashes):
    """Only exact CRLF/LF sidecar conversion may differ from the pinned commit.

    Fresh Godot import can create missing .import/.uid metadata, recorded separately.
    Source content, existing UID files and all importer options must stay identical.
    """
    changed = {k: {'commit': v, 'packedInput': sha(src / k)} for k, v in game_hashes.items() if sha(src / k) != v}
    if any(not k.endswith('.import') for k in changed):
        raise SystemExit('import changed a non-.import source')
    requests = ''.join(COMMIT + ':' + k + '\n' for k in changed).encode('utf-8')
    r = subprocess.run(['git', '-C', str(ROOT), 'cat-file', '--batch'], input=requests,
                       capture_output=True, timeout=120, check=True)
    stream = io.BytesIO(r.stdout)
    for k, record in changed.items():
        header = stream.readline().split()
        if len(header) != 3 or header[1] != b'blob':
            raise SystemExit('missing original blob: ' + k)
        raw = stream.read(int(header[2]))
        if stream.read(1) != b'\n':
            raise SystemExit('invalid original blob: ' + k)
        record['gitBlobSha256'] = hashlib.sha256(raw).hexdigest()
        # Git archive honors this Windows checkout's text eol attributes.
        # Recover only its exact LF -> CRLF form; arbitrary baseline bytes fail.
        if record['gitBlobSha256'] != record['commit']:
            archive_form = raw.replace(b'\r\n', b'\n').replace(b'\n', b'\r\n')
            if hashlib.sha256(archive_form).hexdigest() != record['commit']:
                raise SystemExit('archive hash is not pinned blob or its CRLF form: ' + k)
            record['archiveConversion'] = 'Git archive emitted exact CRLF form of commit blob'
        current = Path(long(src / k)).read_bytes()
        if raw.replace(b'\r\n', b'\n') != current.replace(b'\r\n', b'\n'):
            raise SystemExit('import options changed beyond line endings: ' + k)
        record['difference'] = 'CRLF/LF only; all content and importer options exact'
    extra = {}
    for dirpath, dirs, names in os.walk(long(src / 'game')):
        dirs[:] = [d for d in dirs if d != '.godot']
        for name in names:
            k = 'game/' + Path(dirpath, name).relative_to(Path(long(src / 'game'))).as_posix()
            if k not in game_hashes:
                if not k.endswith(('.import', '.uid')):
                    raise SystemExit('unexpected generated source: ' + k)
                extra[k] = sha(src / k)
    return changed, extra


LAUNCHER = r'''@echo off
rem {label}
rem Starts the normal main menu from this folder. No art/pilot flags. Saves go to the normal Godot user folder.
rem Extra arguments are passed through, e.g.  {name} --headless --quit-after 10
setlocal
set "HERE=%~dp0"
echo {label}
"%HERE%{exe}" --main-pack "%HERE%{pck}" %*
exit /b %ERRORLEVEL%
'''


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--reuse-imported-run', help='Resume a previously imported clean archive inside this task workspace')
    parser.add_argument('--quickstart', help='Root-reviewed bilingual text included in the bundle')
    args = parser.parse_args()
    started = datetime.now(timezone.utc)
    tag = datetime.now().strftime('%Y%m%d-%H%M%S') + '-' + uuid.uuid4().hex[:8]
    if STOP.exists():
        raise SystemExit('GLOBAL STOP present')
    if git('rev-parse', 'HEAD').decode().strip() != COMMIT:
        raise SystemExit('checkout HEAD is not the declared source commit')
    for exe in (GUI, CONSOLE):
        if exe.stat().st_size != EXPECTED_SIZES[exe.name]:
            raise SystemExit(f'vendor runtime size mismatch: {exe}')
    vendor = {exe.name: {'bytes': exe.stat().st_size, 'sha256': sha(exe)} for exe in (GUI, CONSOLE)}
    protected_paths = [ROOT / 'game/project.godot', ROOT / 'game/export_presets.cfg', RUNNER_PATH, LICENSE_GD,
                       Path(__file__).resolve()] + sorted((ROOT / 'game/addons/raw-png-export-v01').iterdir())
    protected = {rel(p): sha(p) for p in protected_paths if p.is_file()}
    status_before = foreign_status()

    run_dir = WORK / f'run-{tag}'
    src = run_dir / 's'
    bundle = WORK / ('bundle-' + tag)
    if bundle.exists():
        raise SystemExit(f'bundle folder already exists; refusing to overwrite: {bundle}')
    for d in (run_dir, src, run_dir / 'app', run_dir / 'local', run_dir / 'lic', run_dir / 'empty', PRODUCER):
        os.makedirs(long(d), exist_ok=True)
    # Isolated app data for this builder's export/test subprocesses only (the launcher never sets these).
    os.environ['APPDATA'] = str(run_dir / 'app')
    os.environ['LOCALAPPDATA'] = str(run_dir / 'local')
    gate = Gate(tag)
    report = {'tool': rel(__file__), 'label': LABEL, 'tag': tag, 'startedUtc': started.isoformat(),
              'sourceCommit': COMMIT, 'vendorRuntimes': vendor, 'protectedSourceSha256': protected,
              'textHashNormalization': 'none: sha256 of raw bytes for every file', 'steps': gate.steps,
              'notNativeReleaseExport': True, 'artApproval': False, 'releaseAcceptance': False}
    report_path = PRODUCER / f'{SLUG}_play54_build-report_v01_{tag}.json'
    try:
        if args.reuse_imported_run:
            previous = Path(args.reuse_imported_run).resolve()
            if not previous.is_relative_to(WORK.resolve()) or not previous.name.startswith('run-'):
                raise SystemExit('reused source must be a run inside this task workspace')
            previous_tag = previous.name[4:]
            previous_hashes = PRODUCER / f'{SLUG}_play54_raw-game-hashes_v01_{previous_tag}.json'
            game_hashes = json.loads(previous_hashes.read_text(encoding='utf-8'))
            src = previous / 's'
            verify_sources(src, game_hashes)
            report['reusedImportedArchive'] = rel(previous)
            report['reusedRawHashListSha256'] = sha(previous_hashes)
        else:
            game_hashes = extract_archive(src)
        game = src / 'game'
        report['rawGameFileCount'] = len(game_hashes)
        archive_list = PRODUCER / f'{SLUG}_play54_raw-game-hashes_v01_{tag}.json'
        archive_list.write_text(json.dumps(game_hashes, indent=1, sort_keys=True) + '\n', encoding='utf-8', newline='\n')

        if not args.reuse_imported_run:
            gate.run('import', [str(CONSOLE), '--headless', '--path', str(game), '--import'], TIMEOUT_IMPORT)
        pck_name = f'{SLUG}_mvp_playtest-pack_developer_{tag}.pck'
        pck_tmp = run_dir / pck_name
        gate.run('export-pack', [str(CONSOLE), '--headless', '--path', str(game), '--export-pack', 'Windows Desktop',
                                 str(pck_tmp), '--quit'], TIMEOUT_EXPORT, expected=['RAW_INPUT_EXPORT_FILE_COUNTS'])
        if not pck_tmp.is_file() or pck_tmp.stat().st_size == 0:
            raise SystemExit('export reported success but PCK missing/empty')
        pck_bytes = Path(long(pck_tmp)).read_bytes()
        injected = [s for s in ('engine-license-dump', 'portable-playtest-build', 'checked-runner') if s.encode() in pck_bytes]
        if injected:
            raise SystemExit(f'test/tool script names found inside PCK: {injected}')
        changed, extra = verify_sources(src, game_hashes)
        report['importRewrittenSidecars'] = changed
        report['importGeneratedSidecars'] = extra
        print(f'[sidecars] {len(changed)} exact CRLF/LF-only changes, {len(extra)} generated metadata files', flush=True)

        (run_dir / 'lic' / 'project.godot').write_text('; empty project for engine license dump\nconfig_version=5\n',
                                                       encoding='utf-8', newline='\n')
        notices = run_dir / 'notices'
        os.makedirs(notices)
        prefix = tag
        gate.run('license-dump', [str(CONSOLE), '--headless', '--path', str(run_dir / 'lic'), '--script', str(LICENSE_GD),
                                  '--', str(notices), prefix], TIMEOUT_SHORT, expected=['LICENSE_DUMP_OK'])

        os.makedirs(bundle)
        for exe in (GUI, CONSOLE):
            shutil.copy2(long(exe), long(bundle / exe.name))
        shutil.copy2(long(pck_tmp), long(bundle / pck_name))
        for f in sorted(notices.iterdir()):
            shutil.copy2(long(f), long(bundle / f.name))
        launchers = {}
        for variant, exe in (('normal', GUI.name), ('console-log', CONSOLE.name)):
            name = f'{SLUG}_mvp_playtest-launcher_{variant}_{tag}.cmd'
            text = LAUNCHER.format(label=LABEL, name=name, exe=exe, pck=pck_name).replace('\n', '\r\n')
            Path(long(bundle / name)).write_bytes(text.encode('ascii'))
            launchers[variant] = name
        label_file = bundle / f'{SLUG}_mvp_playtest-label_developer_{tag}.txt'
        Path(long(label_file)).write_text(LABEL + '\r\nDouble-click the "normal" .cmd launcher to start the main menu.\r\n'
                              'Source commit: ' + COMMIT + '\r\n', encoding='ascii', newline='')
        if args.quickstart:
            guide = Path(args.quickstart).resolve()
            if not guide.is_relative_to(PRODUCER.resolve()) or not guide.is_file():
                raise SystemExit('quickstart must be an existing task producer text file')
            shutil.copy2(long(guide), long(bundle / guide.name))
        for exe in (GUI, CONSOLE):
            if sha(bundle / exe.name) != vendor[exe.name]['sha256']:
                raise SystemExit(f'bundled runtime differs from vendor: {exe.name}')

        # Smoke 1: console runtime + bundled PCK from an EMPTY directory, no --path game.
        empty = run_dir / 'empty'
        if any(empty.iterdir()):
            raise SystemExit('smoke dir not empty')
        gate.run('smoke-empty-dir', [str(bundle / CONSOLE.name), '--headless', '--main-pack', str(bundle / pck_name),
                                     '--quit-after', '5'], TIMEOUT_SHORT, cwd=empty)
        # Smoke 2: both launchers from a copy of the bundle under a path containing spaces, cwd elsewhere.
        # cmd.exe cannot open .cmd files through extended-length path syntax.
        # Keep this real launcher test short enough for Windows' legacy MAX_PATH.
        smoke_workspace = PRIMARY / 'work' / ('p54-smoke-' + tag[-8:])
        spaced = smoke_workspace / 'play test'
        if smoke_workspace.exists():
            raise SystemExit('refusing to overwrite an existing smoke workspace')
        shutil.copytree(long(bundle), long(spaced))
        for variant, name in launchers.items():
            cmdline = f'cmd /d /s /c ""{spaced / name}" --headless --quit-after 10"'
            gate.run(f'smoke-launcher-{variant}', cmdline, TIMEOUT_SHORT, cwd=empty)
        cleanup_target = smoke_workspace.resolve()
        if cleanup_target.parent != (PRIMARY / 'work').resolve() or cleanup_target.name != 'p54-smoke-' + tag[-8:]:
            raise SystemExit('refusing cleanup outside this task workspace')
        report['verifiedCleanupTarget'] = str(cleanup_target)
        shutil.rmtree(long(cleanup_target))

        if {rel(p): sha(p) for p in protected_paths if p.is_file()} != protected:
            raise SystemExit('protected source bytes changed')
        if foreign_status() != status_before:
            raise SystemExit('git status outside own scopes changed')
        report['protectedBytesUnchanged'] = True
        report['gitStatusOutsideOwnScopesUnchanged'] = True

        manifest = {'label': LABEL, 'sourceCommit': COMMIT, 'builder': rel(__file__),
                    'builderSha256': protected[rel(__file__)], 'licenseDumpScriptSha256': protected[rel(LICENSE_GD)],
                    'exportPreset': 'Windows Desktop (game/export_presets.cfg at source commit, unedited)',
                    'exportPresetsSha256AtCommit': game_hashes['game/export_presets.cfg'],
                    'projectGodotSha256AtCommit': game_hashes['game/project.godot'],
                    'rawGameFileCount': len(game_hashes), 'rawGameHashesSha256': sha(archive_list),
                    'rawGameHashes': game_hashes, 'importRewrittenSidecars': report['importRewrittenSidecars'], 'importGeneratedSidecars': report['importGeneratedSidecars'], 'textHashNormalization': 'none (raw bytes)',
                    'launchers': launchers, 'launcherDefaultFlags': ['--main-pack <pck>'],
                    'savesIsolated': False, 'nativeReleaseExport': False, 'artApproval': False,
                    'files': {f.name: {'bytes': Path(long(f)).stat().st_size, 'sha256': sha(f)} for f in sorted(bundle.iterdir())},
                    'smokeSteps': [s['step'] for s in gate.steps], 'buildTag': tag}
        manifest_name = f'{SLUG}_mvp_playtest-manifest_developer_{tag}.json'
        Path(long(bundle / manifest_name)).write_text(json.dumps(manifest, indent=1) + '\n', encoding='utf-8', newline='\n')
        shutil.copy2(long(bundle / manifest_name), long(PRODUCER / manifest_name))

        zip_path = WORK / f'{SLUG}_mvp_playtest-bundle_developer_{tag}.zip'
        with zipfile.ZipFile(long(zip_path), 'x', zipfile.ZIP_DEFLATED) as z:
            for f in sorted(bundle.iterdir()):
                z.write(long(f), f'{SLUG}_playtest_{tag}/{f.name}')
        with zipfile.ZipFile(long(zip_path)) as z:
            if z.testzip() is not None:
                raise SystemExit('zip CRC check failed')
        report.update(passed=True, bundle=rel(bundle), pck=rel(bundle / pck_name), manifest=rel(bundle / manifest_name),
                      zip=rel(zip_path), zipBytes=zip_path.stat().st_size, zipSha256=sha(zip_path))
    except GateFailure as e:
        report.update(passed=False, failedStep=e.args[0]['step'])
    except SystemExit as e:
        report.update(passed=False, failure=str(e))
    except Exception as e:
        report.update(passed=False, failure=type(e).__name__ + ': ' + str(e))
    report['endedUtc'] = datetime.now(timezone.utc).isoformat()
    report_path.write_text(json.dumps(report, indent=1) + '\n', encoding='utf-8', newline='\n')
    print(json.dumps({k: report.get(k) for k in ('passed', 'failure', 'failedStep', 'bundle', 'pck', 'manifest', 'zip')}, indent=1))
    print('report:', report_path)
    if not report['passed']:
        raise SystemExit(1)


if __name__ == '__main__':
    main()
