"""Build a native Windows unsigned PLAYTEST candidate with official Godot 4.7.2 release export templates.

Not a final release, not art/release acceptance, no bundled editor. Startup/save success is NOT claimed here;
the coordinator tests the produced bundle independently.
Reuses the play54 portable builder helpers (long paths, hashing, git, archive extraction, sidecar verification,
checked runner). Steps, each gated (checked runner: diagnostics, exit code and expected markers fail):
  1. preflight: global stop absent, HEAD game tree == pinned source game tree, official template provenance,
     protected tracked game hashes, git status snapshot, validated play54 engine notices
  2. git archive <commit>:game into work/n56-<id>/s (never edits earlier archived input), headless import
  3. isolated export preset delta (custom release template, x86_64, no resource modification, no signing,
     separate PCK) written only in the n56 source copy; --export-release; original preset bytes restored
  4. sidecar check (CRLF-only .import differences, same helper as play54), PCK tool-name check
  5. delivery folder with spaces: <stem>.exe + <stem>.pck + notices + readme + manifest; local ZIP
  6. protected tracked game hashes/git status unchanged -> report
Run: <python> -X utf8 tools/<this file> --template-dir <dir> [--template-tpz <tpz>] [--console-wrapper]
"""
from datetime import datetime, timezone
from pathlib import Path
import argparse, hashlib, importlib.util, json, os, re, shutil, sys, uuid, zipfile

SLUG = 'rpg-2-star-ocean-the-second'
TOOL_ID = '20261022-210709-4d8577b8'
ROOT = Path(__file__).resolve().parents[1]
PRIMARY = ROOT.parents[1]
HELPER_PATH = ROOT / f'tools/{SLUG}_mvp_portable-playtest-build_v01_20261022-202347-7fea20f0.py'
TEMPLATE_DIR_DEFAULT = PRIMARY / 'work/tooling/godot-4-7-2/windows-templates-4.7.2.stable'
TPZ_DEFAULT = PRIMARY / ('work/tooling/godot-4-7-2/rpg-2-star-ocean-the-second_godot_export-templates_'
                         'official-4-7-2_20261022-210622-7c97dbfc.tpz')
TPZ_SHA256 = 'f298490b8d44d934be425a5a65a51bf15f422428b229a06a6e11d9ffea248011'
TEMPLATE_VERSION = '4.7.2.stable'
RELEASE_TEMPLATE, DEBUG_TEMPLATE = 'windows_release_x86_64.exe', 'windows_debug_x86_64.exe'
PRODUCER = ROOT / 'outputs/native56/producer'
BASELINE_BUNDLE = ROOT / 'work/play54-20261022-202347-7fea20f0/bundle-20261022-203718-2fd4b10c'
BASELINE_MANIFEST = BASELINE_BUNDLE / f'{SLUG}_mvp_playtest-manifest_developer_20261022-203718-2fd4b10c.json'
NOTICE_PATTERNS = ('_copyright-info_embedded_', '_engine-license-text_embedded_', '_thirdparty-license-info_embedded_')
PRESET_NAME = 'Windows Desktop'
TIMEOUT_IMPORT, TIMEOUT_EXPORT = 420, 420
SAVE_DIR = r'%APPDATA%\Godot\app_userdata\Worlds Between'
LABEL = ('NATIVE WINDOWS UNSIGNED PLAYTEST CANDIDATE - official Godot 4.7.2 release template export; '
         'not a final release, not art or release acceptance.')


def load_helper():
    spec = importlib.util.spec_from_file_location('play54_builder', HELPER_PATH)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


H = load_helper()
long, sha, rel, git = H.long, H.sha, H.rel, H.git
COMMIT = H.COMMIT
CONSOLE = H.CONSOLE


class Gate(H.Gate):
    """play54 checked-runner gate with native56 log names."""

    def run(self, name, command, timeout, expected=(), cwd=None):
        if H.STOP.exists():
            raise SystemExit('GLOBAL STOP present')
        log = PRODUCER / f'{SLUG}_native56_{name}-log_v01_{self.tag}.log'
        old = os.getcwd()
        if cwd:
            os.chdir(cwd)
        try:
            result = self.runner.run_checked(command, timeout, expected=list(expected), log_path=log)
        finally:
            os.chdir(old)
        result.pop('log', None)
        step = {'step': name, 'command': command, 'cwd': str(cwd or old), 'timeoutSeconds': timeout,
                'expectedMarkers': list(expected), 'log': rel(log), 'logSha256': sha(log), **result}
        self.steps.append(step)
        print(f'[{name}] passed={result["passed"]} reason={result["reason"]} exit={result["exitCode"]} '
              f'{result["elapsedSeconds"]}s', flush=True)
        if not result['passed']:
            raise H.GateFailure(step)
        return step


def tracked_game_hashes():
    names = git('ls-files', '-z', '--', 'game').decode('utf-8').split('\0')
    return {n: sha(ROOT / n) for n in names if n and (ROOT / n).is_file()}


def template_provenance(template_dir, tpz, console_wrapper):
    version_file = template_dir / 'version.txt'
    if not version_file.is_file():
        raise SystemExit(f'template version.txt missing: {version_file}')
    version = version_file.read_text(encoding='utf-8').strip()
    if version != TEMPLATE_VERSION:
        raise SystemExit(f'template version {version!r} != {TEMPLATE_VERSION!r}')
    needed = [RELEASE_TEMPLATE] + ([DEBUG_TEMPLATE] if console_wrapper else [])
    files = {}
    for name in [RELEASE_TEMPLATE, DEBUG_TEMPLATE, 'version.txt']:
        p = template_dir / name
        if p.is_file():
            files[name] = {'bytes': p.stat().st_size, 'sha256': sha(p)}
        elif name in needed:
            raise SystemExit(f'required template missing: {p}')
    prov = {'templateDir': str(template_dir), 'version': version, 'files': files,
            'officialTpz': None, 'tpzMemberMatch': None}
    if tpz is not None:
        if not tpz.is_file():
            raise SystemExit(f'template TPZ missing: {tpz}')
        tpz_sha = sha(tpz)
        if tpz_sha != TPZ_SHA256:
            raise SystemExit(f'template TPZ SHA256 {tpz_sha} != pinned {TPZ_SHA256}')
        match = {}
        with zipfile.ZipFile(long(tpz)) as z:
            members = {Path(i.filename).name: i.filename for i in z.infolist() if not i.is_dir()}
            for name in files:
                if name not in members:
                    raise SystemExit(f'{name} not present in official TPZ')
                h = hashlib.sha256()
                with z.open(members[name]) as f:
                    for block in iter(lambda: f.read(1 << 20), b''):
                        h.update(block)
                if h.hexdigest() != files[name]['sha256']:
                    raise SystemExit(f'extracted {name} differs from official TPZ member {members[name]}')
                match[name] = members[name]
        prov['officialTpz'] = {'path': str(tpz), 'bytes': tpz.stat().st_size, 'sha256': tpz_sha,
                               'pinnedSha256': TPZ_SHA256}
        prov['tpzMemberMatch'] = match
    else:
        prov['limitation'] = 'TPZ not supplied: extracted templates not compared to official archive members'
    return prov


def baseline_notices():
    """Engine notices from the validated play54 developer bundle, verified against its manifest."""
    manifest = json.loads(Path(long(BASELINE_MANIFEST)).read_text(encoding='utf-8'))
    if manifest.get('sourceCommit') != COMMIT:
        raise SystemExit('baseline bundle source commit mismatch')
    notices = {}
    for name, rec in manifest['files'].items():
        if any(p in name for p in NOTICE_PATTERNS):
            if sha(BASELINE_BUNDLE / name) != rec['sha256']:
                raise SystemExit(f'baseline notice differs from its manifest: {name}')
            notices[name] = rec
    if len(notices) != len(NOTICE_PATTERNS):
        raise SystemExit(f'expected {len(NOTICE_PATTERNS)} baseline notices, found {sorted(notices)}')
    return manifest, notices


def isolated_preset(original, release_exe, console_wrapper):
    """Return (new preset text, delta) changing only preset.0 options for a native release export."""
    text = original.decode('utf-8')
    crlf = '\r\n' in text
    text = text.replace('\r\n', '\n')
    if '\r' in text or (crlf and text.replace('\n', '\r\n').encode('utf-8') != original):
        raise SystemExit('export_presets.cfg has mixed line endings; refusing ambiguous edit')
    if text.count('[preset.0.options]') != 1 or '[preset.1' in text:
        raise SystemExit('unexpected export preset layout')
    if f'name="{PRESET_NAME}"' not in text:
        raise SystemExit('preset name changed')
    delta = {
        'custom_template/debug': '""',
        'custom_template/release': json.dumps(release_exe.resolve().as_posix()),
        'binary_format/architecture': '"x86_64"',
        'binary_format/embed_pck': 'false',
        'debug/export_console_wrapper': '1' if console_wrapper else '0',
        'application/modify_resources': 'false',
        'codesign/enable': 'false',
    }
    head, options = text.split('[preset.0.options]\n', 1)
    kept, before = [], {}
    for line in options.splitlines():
        m = re.match(r'^([A-Za-z0-9_/.\-]+)=(.*)$', line)
        if m and m.group(1) in delta:
            before[m.group(1)] = m.group(2)
            continue
        kept.append(line)
    while kept and kept[-1] == '':
        kept.pop()
    new_options = kept + [f'{k}={v}' for k, v in delta.items()]
    new = head + '[preset.0.options]\n' + '\n'.join(new_options) + '\n'
    if crlf:
        new = new.replace('\n', '\r\n')
    return new.encode('utf-8'), {'set': delta, 'previousValues': before,
                                 'lineEndingsPreserved': 'CRLF' if crlf else 'LF'}


README = '''{label}

Worlds Between - Windows playtest build ({tag})
Source commit: {commit}

HOW TO PLAY
  1. Unzip the whole folder anywhere you like (a path with spaces is fine).
  2. Double-click "{exe}".
  The game opens at the normal main menu. No art/pilot flags are set.

KEEP THE PAIR TOGETHER
  "{exe}" needs "{pck}" (the game data) in the SAME folder with the SAME name.
  Do not rename, move or delete either file on its own.

SAVES
  Saves go to the normal Godot user folder: {save_dir}
  Nothing in this build deletes saves. Removing this playtest folder does not remove saves.

WINDOWS WARNINGS
  This build is unsigned. Windows SmartScreen may say "Windows protected your PC";
  choose "More info" -> "Run anyway" only if you obtained this folder from the project team.

STATUS
  Native unsigned PLAYTEST candidate, not a final release. Not art approval, not release acceptance.
  No Godot editor is bundled. Engine copyright/license and third-party notices are included as the
  *_copyright-info_*, *_engine-license-text_* and *_thirdparty-license-info_* files.

中文：解压整个文件夹后双击 "{exe}" 即可从主菜单开始。"{pck}" 必须与其同名同目录保留。
存档位于 {save_dir}，本构建不会删除存档。此为未签名的试玩候选版本，并非正式发布，也不代表美术或发布验收。
'''


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('--template-dir', default=str(TEMPLATE_DIR_DEFAULT),
                        help='Extracted official 4.7.2 Windows templates (version.txt + windows_release_x86_64.exe)')
    parser.add_argument('--template-tpz', default=str(TPZ_DEFAULT),
                        help='Official TPZ for SHA256/member provenance; pass "none" to skip (recorded as limitation)')
    parser.add_argument('--console-wrapper', action='store_true',
                        help='Also export the <stem>.console.exe wrapper (needs windows_debug_x86_64.exe)')
    args = parser.parse_args()
    started = datetime.now(timezone.utc)
    tag = datetime.now().strftime('%Y%m%d-%H%M%S') + '-' + uuid.uuid4().hex[:8]
    short = tag[-8:]
    if H.STOP.exists():
        raise SystemExit('GLOBAL STOP present')
    os.makedirs(long(PRODUCER), exist_ok=True)
    gate = Gate(tag)
    report = {'tool': rel(__file__), 'toolSha256': sha(__file__), 'helper': rel(HELPER_PATH),
              'helperSha256': sha(HELPER_PATH), 'label': LABEL, 'tag': tag, 'startedUtc': started.isoformat(),
              'sourceCommit': COMMIT, 'steps': gate.steps,
              'textHashNormalization': 'none: sha256 of raw bytes for every file',
              'nativeReleaseExport': True, 'signed': False, 'finalRelease': False, 'artApproval': False,
              'releaseAcceptance': False, 'startupVerified': False, 'saveVerified': False,
              'startupSaveNote': 'Not tested by this builder; requires independent coordinator test.'}
    report_path = PRODUCER / f'{SLUG}_native56_build-report_v01_{tag}.json'
    try:
        head = git('rev-parse', 'HEAD').decode().strip()
        head_tree = git('rev-parse', 'HEAD:game').decode().strip()
        pinned_tree = git('rev-parse', COMMIT + ':game').decode().strip()
        if head_tree != pinned_tree:
            raise SystemExit(f'HEAD game tree {head_tree} != pinned source game tree {pinned_tree}')
        report['checkoutHead'] = head
        report['gameTree'] = {'head': head_tree, 'pinnedSource': pinned_tree, 'identical': True}
        template_dir = Path(args.template_dir).resolve()
        tpz = None if args.template_tpz.lower() == 'none' else Path(args.template_tpz).resolve()
        report['templates'] = template_provenance(template_dir, tpz, args.console_wrapper)
        release_exe = template_dir / RELEASE_TEMPLATE
        baseline_manifest, notices = baseline_notices()
        report['baseline'] = {'bundle': rel(BASELINE_BUNDLE), 'manifest': rel(BASELINE_MANIFEST),
                              'manifestSha256': sha(BASELINE_MANIFEST), 'buildTag': baseline_manifest.get('buildTag'),
                              'notices': notices}
        vendor_version = 'Godot_v4.7.2-stable'
        if vendor_version not in CONSOLE.name:
            raise SystemExit('helper runtime is not Godot 4.7.2 stable')
        report['versionComparison'] = {'templateVersion': report['templates']['version'],
                                       'exportEngine': CONSOLE.name, 'exportEngineSha256': sha(CONSOLE),
                                       'match': True}
        protected_extra = [Path(__file__).resolve(), HELPER_PATH, H.RUNNER_PATH]
        game_before = tracked_game_hashes()
        extra_before = {rel(p): sha(p) for p in protected_extra}
        report['protectedTrackedGameFileCount'] = len(game_before)
        report['protectedTrackedGameDigest'] = hashlib.sha256(
            json.dumps(game_before, sort_keys=True).encode('utf-8')).hexdigest()
        H.OWN_SCOPES = ('outputs/native56/', f'_{TOOL_ID}.')
        status_before = H.foreign_status()

        work = PRIMARY / 'work' / f'n56-{short}'
        if work.exists():
            raise SystemExit(f'refusing to reuse existing workspace {work}')
        src, app, local = work / 's', work / 'app', work / 'local'
        delivery = work / f'Worlds Between playtest {short}'
        for d in (src, app, local, work / 'x'):
            os.makedirs(long(d))
        os.environ['APPDATA'] = str(app)
        os.environ['LOCALAPPDATA'] = str(local)
        report['workspace'] = str(work)
        H.WORK = work
        game_hashes = H.extract_archive(src)
        game = src / 'game'
        hashes_path = PRODUCER / f'{SLUG}_native56_raw-game-hashes_v01_{tag}.json'
        hashes_path.write_text(json.dumps(game_hashes, indent=1, sort_keys=True) + '\n', encoding='utf-8', newline='\n')
        report['rawGameFileCount'] = len(game_hashes)
        report['rawGameHashesSha256'] = sha(hashes_path)
        tracked_mismatch = [k for k, v in game_hashes.items() if game_before.get(k) not in (None, v)]
        report['archiveVsCheckoutDifferingFiles'] = len(tracked_mismatch)

        gate.run('import', [str(CONSOLE), '--headless', '--path', str(game), '--import'], TIMEOUT_IMPORT)

        preset_path = game / 'export_presets.cfg'
        original_preset = Path(long(preset_path)).read_bytes()
        if hashlib.sha256(original_preset).hexdigest() != game_hashes['game/export_presets.cfg']:
            raise SystemExit('archived export_presets.cfg changed before preset edit')
        new_preset, delta = isolated_preset(original_preset, release_exe, args.console_wrapper)
        Path(long(preset_path)).write_bytes(new_preset)
        preset_copy = PRODUCER / f'{SLUG}_native56_isolated-export-preset_v01_{tag}.cfg'
        Path(long(preset_copy)).write_bytes(new_preset)
        report['isolatedPreset'] = {'originalSha256': game_hashes['game/export_presets.cfg'],
                                    'isolatedSha256': hashlib.sha256(new_preset).hexdigest(),
                                    'isolatedCopy': rel(preset_copy), **delta,
                                    'scope': 'n56 archived source copy only; tracked game file untouched'}

        stem = f'{SLUG}_mvp_native-playtest_unsigned_{tag}'
        out_dir = work / 'x'
        exe_tmp = out_dir / f'{stem}.exe'
        try:
            gate.run('export-release', [str(CONSOLE), '--headless', '--path', str(game), '--export-release',
                                        PRESET_NAME, str(exe_tmp)], TIMEOUT_EXPORT,
                     expected=['RAW_INPUT_EXPORT_FILE_COUNTS'])
        finally:
            after_export = Path(long(preset_path)).read_bytes()
            report['isolatedPreset']['bytesAfterExportSha256'] = hashlib.sha256(after_export).hexdigest()
            Path(long(preset_path)).write_bytes(original_preset)
        pck_tmp = out_dir / f'{stem}.pck'
        produced = sorted(p.name for p in out_dir.iterdir())
        expected_out = sorted([exe_tmp.name, pck_tmp.name] + ([f'{stem}.console.exe'] if args.console_wrapper else []))
        if produced != expected_out:
            raise SystemExit(f'export outputs {produced} != expected {expected_out}')
        for p in (exe_tmp, pck_tmp):
            if Path(long(p)).stat().st_size == 0:
                raise SystemExit(f'empty export output: {p.name}')
        if sha(exe_tmp) == sha(CONSOLE) or sha(exe_tmp) == sha(H.GUI):
            raise SystemExit('exported executable is an editor binary')
        if Path(long(exe_tmp)).stat().st_size != report['templates']['files'][RELEASE_TEMPLATE]['bytes']:
            report['exeSizeNote'] = 'exported exe size differs from release template (expected only if Godot patched it)'
        pck_bytes = Path(long(pck_tmp)).read_bytes()
        injected = [s for s in ('engine-license-dump', 'portable-playtest-build', 'native-windows-build',
                                'checked-runner') if s.encode() in pck_bytes]
        if injected:
            raise SystemExit(f'tool script names found inside PCK: {injected}')
        del pck_bytes
        changed, extra = H.verify_sources(src, game_hashes)
        report['importRewrittenSidecars'] = changed
        report['importGeneratedSidecars'] = extra
        print(f'[sidecars] {len(changed)} exact CRLF/LF-only changes, {len(extra)} generated metadata files', flush=True)

        os.makedirs(long(delivery))
        for p in out_dir.iterdir():
            shutil.copy2(long(p), long(delivery / p.name))
        for name in notices:
            shutil.copy2(long(BASELINE_BUNDLE / name), long(delivery / name))
        readme_name = f'{SLUG}_mvp_native-playtest-readme_unsigned_{tag}.txt'
        readme = README.format(label=LABEL, tag=tag, commit=COMMIT, exe=exe_tmp.name, pck=pck_tmp.name,
                               save_dir=SAVE_DIR).replace('\n', '\r\n')
        Path(long(delivery / readme_name)).write_bytes(b'\xef\xbb\xbf' + readme.encode('utf-8'))
        for name, rec in notices.items():
            if sha(delivery / name) != rec['sha256']:
                raise SystemExit(f'copied notice differs: {name}')

        game_after = tracked_game_hashes()
        if game_after != game_before or {rel(p): sha(p) for p in protected_extra} != extra_before:
            raise SystemExit('protected tracked game/tool bytes changed')
        if H.foreign_status() != status_before:
            raise SystemExit('git status outside own scopes changed')
        report['protectedBytesUnchanged'] = True
        report['gitStatusOutsideOwnScopesUnchanged'] = True

        files = {f.name: {'bytes': Path(long(f)).stat().st_size, 'sha256': sha(f)} for f in sorted(delivery.iterdir())}
        base_pck = next((n for n in baseline_manifest['files'] if n.endswith('.pck')), None)
        manifest = {'label': LABEL, 'sourceCommit': COMMIT, 'buildTag': tag, 'builder': rel(__file__),
                    'builderSha256': report['toolSha256'], 'helperSha256': report['helperSha256'],
                    'officialTemplate': report['templates'], 'isolatedPreset': report['isolatedPreset'],
                    'exportCommand': '--export-release "Windows Desktop" (official custom release template)',
                    'executable': exe_tmp.name, 'pck': pck_tmp.name, 'readme': readme_name,
                    'notices': {n: 'copied from validated play54 bundle ' + BASELINE_BUNDLE.name for n in notices},
                    'rawGameFileCount': len(game_hashes), 'rawGameHashesSha256': report['rawGameHashesSha256'],
                    'importRewrittenSidecars': len(changed), 'importGeneratedSidecars': len(extra),
                    'baselineComparison': {'developerBundle': BASELINE_BUNDLE.name, 'developerPck': base_pck,
                                           'developerPckSha256': baseline_manifest['files'].get(base_pck, {}).get('sha256'),
                                           'nativePckSha256': files[pck_tmp.name]['sha256'],
                                           'note': 'PCK equality is NOT expected: release export differs from '
                                                   '--export-pack (debug) packing.'},
                    'savesIsolated': False, 'saveFolder': SAVE_DIR, 'editorBundled': False, 'signed': False,
                    'finalRelease': False, 'artApproval': False, 'releaseAcceptance': False,
                    'startupVerified': False, 'saveVerified': False, 'files': files,
                    'textHashNormalization': 'none (raw bytes)'}
        manifest_name = f'{SLUG}_mvp_native-playtest-manifest_unsigned_{tag}.json'
        Path(long(delivery / manifest_name)).write_text(json.dumps(manifest, indent=1, ensure_ascii=False) + '\n',
                                                        encoding='utf-8', newline='\n')
        shutil.copy2(long(delivery / manifest_name), long(PRODUCER / manifest_name))

        zip_path = work / f'{SLUG}_mvp_native-playtest-bundle_unsigned_{tag}.zip'
        with zipfile.ZipFile(long(zip_path), 'x', zipfile.ZIP_DEFLATED) as z:
            for f in sorted(delivery.iterdir()):
                z.write(long(f), f'Worlds Between playtest {short}/{f.name}')
        with zipfile.ZipFile(long(zip_path)) as z:
            if z.testzip() is not None:
                raise SystemExit('zip CRC check failed')
        report.update(passed=True, delivery=str(delivery), executable=str(delivery / exe_tmp.name),
                      pck=str(delivery / pck_tmp.name), manifest=rel(PRODUCER / manifest_name),
                      bundleFiles=files, zip=str(zip_path), zipBytes=Path(long(zip_path)).stat().st_size,
                      zipSha256=sha(zip_path))
    except H.GateFailure as e:
        report.update(passed=False, failedStep=e.args[0]['step'])
    except SystemExit as e:
        report.update(passed=False, failure=str(e))
    except Exception as e:
        report.update(passed=False, failure=type(e).__name__ + ': ' + str(e))
    report['endedUtc'] = datetime.now(timezone.utc).isoformat()
    report_path.write_text(json.dumps(report, indent=1, ensure_ascii=False) + '\n', encoding='utf-8', newline='\n')
    print(json.dumps({k: report.get(k) for k in ('passed', 'failure', 'failedStep', 'delivery', 'manifest', 'zip')},
                     indent=1, ensure_ascii=False))
    print('report:', report_path)
    if not report['passed']:
        raise SystemExit(1)


if __name__ == '__main__':
    main()
