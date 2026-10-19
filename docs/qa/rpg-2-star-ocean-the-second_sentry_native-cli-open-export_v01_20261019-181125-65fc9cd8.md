# Sentry v2 editable package: actual Pixelorama CLI open/export

## Verdict

The existing Sentry v2 editable PXO opens and exports all 21 timeline frames through actual Pixelorama 1.2.3 headless CLI. Every exported 112×62 RGBA frame equals its corresponding cell in the existing 2352×62 v2 strip, with zero pixel differences. This is native CLI usability evidence, separate from the earlier independent archive-reader proof.

The application is **not diagnostic-clean**. Candidate and unchanged known-working control each exited 0 and emitted the same four `shader_compiler.cpp:1329` custom-sampler diagnostics. Raw stdout/stderr are retained. Their identical occurrence on the control supports an inherited headless/backend issue; it does not prove GUI reliability or justify calling this an error-free application run.

## Bounded execution

- Candidate: 2026-10-19 22:11:42–22:11:46 UTC, one invocation, exit 0, no timeout.
- Control: 2026-10-19 22:12:09–22:12:13 UTC, one invocation, exit 0, no timeout.
- Both used the repository-established `--headless --quit -- --export -o <png> <pxo>` command with fresh isolated APPDATA and LOCALAPPDATA, 120-second finite deadline, and the original PXO bytes copied to a short ignored working path.
- Pixelorama's default CLI export produced 21 numbered PNGs, rather than one spritesheet PNG. All 21 files are preserved separately, in original timeline order, and compared against the existing strip in memory. No replacement strip or new artwork was generated.
- Candidate source and its input copy remained byte-identical; control source and copy also remained unchanged.
- No retries, GUI interaction, source-package changes, runtime edits, default selector changes, approval changes, Git/index operations, ledger edits or Site edits were performed.

## Source bindings

| Artifact | SHA-256 |
| --- | --- |
| Sentry PXO `game/assets/enemies/sentry-editable-v01/rpg-2-star-ocean-the-second_sentry_editable-native_v01_20261019-215808-765b18c6.pxo` | `b5027f402bfd14ba031860875714faf0a9bfc7d1f4a321ebb153ad716d3da676` |
| Existing v2 strip / identical copied native strip | `26d1fb1c0d13371f348ec04c27b35901bd8a06701694446374dae6f27c35e52e` |
| Unchanged female battle v15 control PXO | `72b03201d33dfa7ea9f815122908f8f8dacf03b939c2838192bb8540e7b7f947` |
| New verification tool | `b5e319958a3cf51c3d705760bcd2981c90aaaa7746e65a6e6e20f2ccf0ceb4c7` |

## Separate new evidence

- Tool: `tools/rpg-2-star-ocean-the-second_sentry_native-app-export_v01_20261019-181125-65fc9cd8.py`
- Report with source hashes, commands, timestamps, export hashes/sizes and verdict fields: `outputs/sentry-native-app-v01/rpg-2-star-ocean-the-second_sentry_native-cli-report_v01_20261019-181125-65fc9cd8.json`
- Candidate stdout/stderr: same directory, `rpg-2-star-ocean-the-second_sentry_native-cli-candidate-{stdout,stderr}_v01_20261019-181125-65fc9cd8.log`
- Control stdout/stderr: same directory, `rpg-2-star-ocean-the-second_sentry_native-cli-unchanged-control-{stdout,stderr}_v01_20261019-181125-65fc9cd8.log`
- Candidate PNGs: same directory, `rpg-2-star-ocean-the-second_sentry_native-cli-candidate-export-{01..21}_v01_20261019-181125-65fc9cd8.png`.
- Control PNG: same directory, `rpg-2-star-ocean-the-second_sentry_native-cli-unchanged-control-export-01_v01_20261019-181125-65fc9cd8.png`.

## Limits

No native GUI open, editing, Save As, reopening a GUI-saved file, animation playback, hearing, gameplay motion approval or creator art approval is claimed. The pre-existing staged package, proof, checker and QA were not edited. This supporting evidence does not advance an art or acceptance gate.
