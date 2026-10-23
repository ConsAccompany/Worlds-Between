# Native Windows package-check support report

Task: bounded support verifier and bilingual native quickstart draft.
Date: 2026-10-22 (task tag `20261022-210709-4d8577b8`).
Owner: DeepSeek support; coordinator owns integration and acceptance.

This report covers only static tooling and a draft guide. **No game launch, UI, save, combat, route, human playtest, art/default adoption or old test suite was run.** The coordinator-provided `outputs/route55` science-route evidence was not re-run or re-inspected by this task.

## Delivered files

| File | Bytes | SHA-256 |
| --- | ---: | --- |
| `tools/rpg-2-star-ocean-the-second_mvp_native-windows-package-check_v01_20261022-210709-4d8577b8.py` | 45553 | `ffbe0da557641a411822db01d51f4b50a6feb35986ecdb73aa505dec300f0cdd` |
| `outputs/native56/support/rpg-2-star-ocean-the-second_mvp_native-quickstart_draft-v01_20261022-210709-4d8577b8.txt` | 5691 | `ba576d2410e8750330cddffa0616f93a5f9f54cad0c2a12cc2cff0b781f2f95b` |
| `outputs/native56/support/rpg-2-star-ocean-the-second_mvp_native-package-check_support-report_v01_20261022-210709-4d8577b8.md` | this file | not self-hashed |

Both new primary files are UTF-8 with LF newlines; all binary reads/hashes in the verifier are raw bytes.

## Verifier interface

CLI:

```text
python <tool> --bundle DIR --manifest JSON --output NEW_UNIQUE.json [--require-native] [--expect-source-commit 40HEX]
python <tool> --self-test
```

The manifest may be the root object or an object with a `manifest`, `bundleManifest` or `data` wrapper. Required fields: `sourceCommit` (40 lowercase hex) and `files` (a mapping keyed by **basename**; each value has integer `bytes` and 64-hex `sha256`). `nativeReleaseExport` selects native vs declared developer runtime+PCK; `--require-native` forces the native gate. For a native export, `template` (or `templateProvenance`/`exportTemplate`/`engine.template`/`template_provenance`) must declare the official Godot 4.7.2-stable source URL, version, template SHA-256, and a coherent signed/unsigned state. `manifest.passed` is explicitly ignored and recorded as ignored.

The verifier checks: UTF-8 JSON, exact size/SHA-256 of every listed member, missing/extra dangerous executables and scripts, MZ/PE/`0x8664`/`0x20b` headers, one `GDPC` PCK with a matching launcher/manifest basename, no Godot editor runtime in a native claim, private auth/config filenames (license/notice `.json`/`.txt` exempted), symlinks/junctions and path escapes, official/version/hash template declarations, and Authenticode table presence versus the signed/unsigned declaration. ZIP archives are not supported; extract first. Unsigned MVPs are accepted without a signing certificate.

## Static tests actually run

Python was the existing uv-managed CPython 3.14.9 at `%APPDATA%\uv\python\cpython-3.14.9-windows-x86_64-none\python.exe`; `PYTHONUTF8=1`. No diagnostic output was filtered.

1. **Embedded negative/positive self-tests: 11/11 expected outcomes.**
   `... --self-test` created temporary controlled fixtures under `work/`, then removed them. Results:
   - `native-valid` -> pass (proves the native gate and template/signature path can pass).
   - `changed-pck-bytes` -> fail at `member-sha256-game.pck`.
   - `changed-pck-size` -> fail at `member-size-game.pck`.
   - `manifest-hash-lie` -> fail at `member-sha256-game.pck` while `manifest.passed` was `true` (parser does not trust the manifest verdict).
   - `missing-pck` -> fail at `file-present-game.pck`.
   - `missing-launcher` -> fail at `file-present-run.cmd`.
   - `wrong-pck-reference` -> fail at `launcher-pck-reference`.
   - `path-traversal-key` (`../escape.exe`) -> fail at `manifest-safe-basename`.
   - `editor-runtime-native` -> fail at `no-editor-runtime-for-native`.
   - `unsigned-not-declared` -> fail at `unsigned-status-declared`.
   - `signed-without-cert` -> fail at `declared-signature-matches-header`.

2. **Actual existing bundle, declared developer mode.** Command used the actual bundle and manifest below, with `--expect-source-commit d5f204...`.

```text
PACKAGE_CHECK PASS kind=developer-runtime-pck nativeRelease=False checks=98 failures=0 warnings=3
```

Observed: 96 pass, 2 not-applicable, 0 fail; 10 listed members plus the manifest itself as the only extra. Both executables parsed as PE64/AMD64 (`MZ`, `PE`, machine `0x8664`, optional magic `0x20b`); the one PCK began `GDPC` and both launchers referenced its exact basename; notice JSON/TXT files were exempted from private-file rejection; no symlink/junction/path escape or unexpected executable was found. Source commit matches `d5f204373c17c62e45e92dea14c3a2e85c525062`.

3. **Same actual bundle forced through the native gate.** `--require-native` produced 95 pass / 4 fail and the expected non-native failures:

```text
native-label-consistency        DEVELOPER PLAYTEST ... not a native release export
no-editor-runtime-for-native    Godot_v4.7.2-stable_win64.exe, ..._console.exe
native-template-provenance      template block missing
native-main-executable          non-editor executable list is empty
```

This is the important result: the existing `outputs/play54`-referenced local bundle is a **developer runtime + external PCK** bundle, not a native Windows export. Its default static consistency passes only for that declared kind.

## Actual inputs examined

- Bundle: `work/play54-20261022-202347-7fea20f0/bundle-20261022-203718-2fd4b10c`
- Manifest: `.../rpg-2-star-ocean-the-second_mvp_playtest-manifest_developer_20261022-203718-2fd4b10c.json`
- PCK: `.../rpg-2-star-ocean-the-second_mvp_playtest-pack_developer_20261022-203718-2fd4b10c.pck` (177,618,576 bytes, SHA-256 `1ca1b09acb95c61051d75503121d3e6c9831b56f41e898808d99c4eb585a03c9`)
- Runtime pair: `Godot_v4.7.2-stable_win64.exe` (180,858,888 bytes, SHA-256 `ab1824f85bfd8e0e4128182c000c4003a3e042245b2967848d089b2a04b22424`) and console binary (198,152 bytes, SHA-256 `c8f0a6bc45a19b33541501e57f6f7cd972ab18453743266339d495cbbe846643`).
- Reviewed quickstart member: 3,063 bytes, SHA-256 `d8e956fa0455969b273a5860eac960a50906e8f6f45a70d1d02a805c6428b7b7`.

The two Godot binaries have PE Authenticode certificate tables present. The developer manifest does not make a native signing declaration, so the verifier recorded this as a warning, not as a native pass. The draft quickstart describes the future native MVP as unsigned and explains SmartScreen; a signing certificate is not required.

## Git and scope

- HEAD: `bc42ae7ef8ea92eea54a53f99d55df19dcb432ab`.
- `git diff --name-only d5f204373c17c62e45e92dea14c3a2e85c525062 HEAD -- game` -> **0 files** (identical game tree, as stated by the coordinator).
- No staging, commit, ledger or Bible edit; no tracked game edit; no defaults/art change. Only the three new support paths are intentionally added. The pre-existing dirty checkout was left intact (2,612 status lines on the whole worktree; 1,541 under `game`, all pre-existing).
- No provider calls, no extra agents, no old test suites, no Godot launch.

## Material limitations

1. **No native package exists in the checked inputs.** The existing bundle is explicitly developer runtime+PCK and fails the native gate. Do not present its default static pass as native packaging.
2. **No native export template provenance** was present, so official template URL/version/hash/signature could not be checked for a native artifact. A future native manifest must supply the documented `template` block.
3. **Template hash is declaration-only.** The verifier does not fetch upstream Godot archives; it checks URL/version/hash shape and, when a template file is shipped, its exact member hash. No network call was made.
4. **Signature trust is not verified.** The verifier compares the declared signed/unsigned state with the PE certificate table; it does not validate certificate chains or a signer identity. Unsigned MVP remains acceptable.
5. **Static only.** No launch, rendering, input, save/reload, battle return, audio or UI behavior was exercised. `outputs/route55` was not rerun; that evidence remains coordinator-provided.
6. **ZIP is unsupported.** The verifier expects an extracted directory; ZIP CRC/containment remains a separate coordinator check.
7. Two empty scratch directories, `work/nv56-selftest-nnqggl3v` and `work/nvtest-qf8krova`, were left by a temporary-directory ACL failure. They contain no deliverables; cleanup under the normal sandbox was denied and no approval channel was available. They are not part of the verifier, quickstart or report.

## Bounded next action

Run the verifier on the actual native export bundle once its manifest supplies `nativeReleaseExport: true`, `files`, `sourceCommit`, and the `template` provenance/unsigned declaration. Expected command:

```powershell
$env:PYTHONUTF8='1'
python tools\rpg-2-star-ocean-the-second_mvp_native-windows-package-check_v01_20261022-210709-4d8577b8.py `
  --bundle <native-bundle-dir> `
  --manifest <native-manifest.json> `
  --output <new-unique-result.json> `
  --require-native `
  --expect-source-commit d5f204373c17c62e45e92dea14c3a2e85c525062
```

Do not treat a developer-bundle pass as native readiness; the report's `bundleKind`/`nativeRelease` fields are the distinction.
