# Yanke south static — batch96 QA addendum (UNAPPROVED v01)

Task: `content.char.yanke.static-south` (frozen criterion: south native pixel static at 48 logical px, committed
with QA; the old 32×48 placeholder does not count). Owner/producer: **DeepSeek** (adapter-selected batch93
producer; batch96 verifier). Status: **source package produced and technically re-verified, unapproved, not
adopted, not runtime-wired**. No ledger, Bible, operating-registry, index or commit change was made.

Base/tested revision: `a376e8fc5ec26ab6ecc9475c0c87b34c1c3b030f`. Hash convention: SHA-256 of raw bytes, no
text normalization.

## Byte verification and provenance correction

The batch93 package bytes on disk were verified against the batch93 QA note before any new run; every hash matched
(the static PNG, PXO, ORA, palette, manifest, author and checker). The batch93 note's `Owner: claude` label was
false: the adapter-selected batch93 producer was DeepSeek (batch96 task authority). The local batch93 job
transcript is retained at `outputs/yanke-s93/coordinator/provider-source-history.jsonl`. The label was corrected
in place; the pre-edit note was preserved under `outputs/yanke-s96/backups/qa/` and its raw hash verified.

| Artifact | Raw SHA-256 |
| --- | --- |
| Batch93 QA note, pre-batch96 (backup) | `685655ae99f9eea64afef30a3540445598d8c026680ef3433c55c19471f1ff76` |
| Same note after owner/provenance correction | `25069cdaa7c7c4705fe009543f85e4036490202693dc5336499ef67769250ed4` |
| New native-export checker tool | `77e6a29f8b588eb269ca8c6ff4355de5b7fd743e39a4898b2969038a852510ab` |

The batch93 note's statement that batch93 had "no Pixelorama export equality test" is historically true and is
superseded only by this addendum. Its failed iterations and fit diagnostics remain unchanged.

## Fresh deterministic and independent reruns

```bash
../tooling/venv/bin/python -X utf8 -I tools/rpg-2-star-ocean-the-second_yanke_south-static-author_unapproved-v01_20261024-084428-b93c1a4e.py check
../tooling/venv/bin/python -X utf8 -I tools/rpg-2-star-ocean-the-second_yanke_static-source-check_v01_20261024-084428-b93c1a4e.py --root . --out outputs/yanke-s96/independent
```

- Author check: exit **0**, `YANKE_SOUTH_V01_ALL_OK`, deterministic rebuild true, disk-match true for all five
  package files, hard failures `[]`, all reused tool pins true. 80×112, pivot (40,104), body rows 8..103, display
  scale 0.5, **48 logical px**, 38 colours, 12 role layers, 22 isolated texels. Log:
  `outputs/yanke-s96/author-check.log` (`744bdfb14f597f610d907e7f957d673868af8c5a71c4b6d0da5bdd36cf1b27e5`).
- Independent checker: exit **0**, `YANKE_S93_INDEPENDENT 31 / 31`, `FAILURES []`. Fresh proof:
  `outputs/yanke-s96/independent/` (proof `972bd7c0…bdb`, corrupt-hash control `c5dc4afc…6bf2f0`). Log:
  `outputs/yanke-s96/independent-check.log` (`d94d7f89bd1a1cbeb8043373e009f97eee6cea0c4ab362eb47bfd629f050a27c`).

This rerun reproduces the batch93 result from the same bytes; no gate was changed or weakened.

## Native Pixelorama 1.2.3 export equality (new in batch96)

The new scoped checker copies the installed PXO/ORA to an isolated run directory and invokes the repository's
established command with isolated HOME/XDG dirs (so the real editor profile is untouched):

```bash
../tooling/venv/bin/python -X utf8 -I tools/rpg-2-star-ocean-the-second_yanke_static-native-pixelorama-check_v01_20261024-085818-3e43ee2b.py --out outputs/yanke-s96/native
```

Each run uses `Pixelorama.x86_64 --headless --quit -- --export [--split-layers] -o <out.png> <copy>`, 120 s
finite deadline, fresh `HOME`/`XDG_CONFIG_HOME`/`XDG_DATA_HOME`/`XDG_CACHE_HOME`.

| Run | Exit | Exports | Equality result |
| --- | --- | --- | --- |
| PXO flat | 0 | 1 | exact RGBA equality with package static PNG |
| PXO split-layers | 0 | 12 visible layers | every layer exact vs its PXO layer; merged composite exact vs package static; `guides` not exported |
| ORA flat | 0 | 1 | exact RGBA equality with package static PNG |

All 11 equality/input gates passed: `pxo_flat_one_export`, `pxo_flat_exact_static`, `pxo_split_layer_count`,
`pxo_split_each_layer_exact`, `pxo_split_merged_exact_static`, `pxo_no_visible_guide_export`,
`pxo_inputs_unchanged`, `ora_flat_one_export`, `ora_flat_exact_static`, `ora_inputs_unchanged`,
`package_bytes_unchanged`. Both flat exports are the same raw bytes:
`7a6fd520996a24b26c75738f2ff181c0a664cff0776c3f2f19342761cde326a3` (identical to the existing
`outputs/yanke-s93/coordinator/native/yanke-south-idle-static-v01.png`); the merged split-layer composite is
pixel-equal to the package static. The package static remains
`4f6bcf937390e300e2829ac052bcb1047fdb6387de41561490c757246a32fef0`.

Report: `outputs/yanke-s96/native/20261024-085846-a68f0026/rpg-2-star-ocean-the-second_yanke_native-pixelorama-export-report_test-only-v01_20261024-085818-3e43ee2b.json`
(`63ed11a85935291f5208ee7270a6e9695a328fb2bd3db38b804f9e05d906a6fc`); raw stdout/stderr under the same
run directory.

### Native application diagnostics — FAILED, retained separately

Export equality does **not** mean a diagnostic-clean editor:

- PXO flat and PXO split: exit 0 but each emitted four
  `ERROR: Condition "!actions.custom_samplers.has(function->arguments[j].tex_builtin)" is true. Continuing.`
  (`shader_compiler.cpp:1329`), the known inherited Pixelorama/Godot headless issue.
- ORA flat: exit 0 and exact pixels, but emitted the four sampler errors plus three
  `Index p_index = 0 is out of bounds`, one `Required object "rp_node" is null`, one
  `Must be an ancestor of the control`, one RID-allocation leak, one `16 resources still in use at exit`, and a
  166-instance ObjectDB leak warning.

`diagnostic_clean: false` is recorded as a failed application-diagnostic check, not as an export failure and not as
a pass. No control was re-run in batch96; the unchanged-control evidence for the sampler errors is the earlier
project record. No GUI SaveAs/reopen or GUI reliability claim is made.

## Checked Godot bilingual source-fit (Dummy audio)

```bash
FIT="$PWD/outputs/yanke-s96/fit"
env HOME="$FIT/home" XDG_CONFIG_HOME="$FIT/config" XDG_DATA_HOME="$FIT/data" \
  XDG_CACHE_HOME="$FIT/cache" TMPDIR="$FIT/tmp" \
  xvfb-run -a -s "-screen 0 640x360x24" ../tooling/venv/bin/python -X utf8 -I \
  tools/rpg-2-star-ocean-the-second_godot_checked-runner_v01_20261018-203400-f74ac6d1.py \
  --timeout 110 --expect "JIANG37_SOURCE_FIT_PASS captures=4" --log "$FIT/fit.runner.log" -- \
  ../tooling/bin/godot --audio-driver Dummy --rendering-driver opengl3 --resolution 640x360 --path game \
  --script "$PWD/tools/rpg-2-star-ocean-the-second_native-static_scene-fit-capture_test-only-v01_20261021-235007-514b9771.gd" \
  -- "$PWD/game/assets/characters/yanke-native-v01/south/rpg-2-star-ocean-the-second_yanke_south-static_unapproved-v01_20261024-084428-73949161.png" \
  "$FIT/fit" yanke-s96-20261024-085818-3e43ee2b yanke
```

Result: exit **0**, `JIANG37_SOURCE_FIT_PASS captures=4`, `CHECKED_RUN PASS`, elapsed 4.798 s, missing `[]`.
Only the known V-Sync warning; no `SCRIPT_ERROR`/parse error. Test-only overlay at 640×360, scale 0.5, candidate
position [400,280], `runtimeAdopted:false`, `artApproved:false`. The four captures are byte-identical to the
batch93 fit4 captures (same raw hashes), which is a determinism check, not adoption:

| Capture | Raw SHA-256 |
| --- | --- |
| city EN | `a473ff523dc55a477bba18b654c8744f5f7c9063c8d1cc873e263433dbf13f73` |
| city ZH | `47e50c027fb35bdd145d039a4dc430eeb51a927ea04eba24f2b63e55e4793134` |
| ruins EN | `f3a8619e2357f410b33f769520be5d21631236a75791134cf5a275ab457ea429` |
| ruins ZH | `ba1ae070d8debe71f8cbb3af2af4e4e6a00db858ed55cf503a6fdcba2f7b6252` |
| fit manifest | `822cc839949a6caa9563ea57dd139faa613accdd84fab02df0c4ee7e3f228763` |

Runner log `outputs/yanke-s96/fit/fit.runner.log` (`0e2337bc6f0fa7c8a832d1a8d6c5ed7d98214c35c21f922f120b702d3ecefc3f`);
outer log `outputs/yanke-s96/fit/runner.outer.log` (`0f142af8308047b1a478c569f3e144346001c4b52201fd2d4a101baeb3fd74be`).
The visual overlay was inspected: the candidate appears at the test position with the explicit
`YANKE SOURCE FIT / TEST ONLY` label. It is not a normal gameplay/adoption capture.

## Retained failures and limitations

- Batch93 author draft `isolated_texels_le_24` failed at 31 and again at 33 after a layer reorder; subsequent
  17/21/22 builds passed, and the 22-texel build was installed. Intermediate previews remain in
  `outputs/yanke-s93/author/` and were not relabelled.
- Batch93 fit attempts 1–2 used an incorrect `$ROOT/tooling` path (exit 127); fit attempt 3 used
  `res://tools/...` and Godot reported `File not found` (checked runner FAIL `diagnostic`, exit -9). Log retained at
  `outputs/yanke-s93/fit3/fit.runner.log`. Batch96 used the corrected absolute script path and sibling `../tooling`.
- Batch96 native application diagnostics are **FAILED** as detailed above (sampler errors; additional ORA
  import/exit errors). Source/export equality is passed separately.
- No technical permission denial occurred. No `wb_safe_replace.py` run was needed because no existing
  `outputs/` or `game/assets/` bytes were replaced; the only existing-file replacement was the `docs/qa` note,
  which has a unique metadata-preserving backup with a verified hash (helper scope covers `outputs/` and
  `game/assets/` only).
- Limits: south idle static only; no other direction/animation, runtime wiring, scene selector, default adoption,
  normal-speed gameplay motion review, GUI SaveAs/reopen, or creator art approval. Concept and sprite remain
  UNAPPROVED. Test overlays are not normal adoption evidence.

## Meter snapshot and integration recommendation

Coordinator-stated start values: production **62.0%**, content **691/1881**, inspection **21.6%**, approval
**7.8%**. This producer made no ledger/registry/Bible/index/commit change; after values remain pending coordinator
validation. Recommended explicit integration paths (coordinator stages exact paths after hash verification):

- `game/assets/characters/yanke-native-v01/south/` — PNG, PXO, ORA, palette, manifest, `.gdignore`
- `tools/rpg-2-star-ocean-the-second_yanke_south-static-author_unapproved-v01_20261024-084428-b93c1a4e.py`
- `tools/rpg-2-star-ocean-the-second_yanke_static-source-check_v01_20261024-084428-b93c1a4e.py`
- `tools/rpg-2-star-ocean-the-second_yanke_static-native-pixelorama-check_v01_20261024-085818-3e43ee2b.py`
- `docs/qa/rpg-2-star-ocean-the-second_yanke_south-static-source-qa_unapproved-v01_20261024-084428-b93c1a4e.md`
- `docs/qa/rpg-2-star-ocean-the-second_yanke_south-static-source-qa-addendum_unapproved-v01_20261024-085818-3e43ee2b.md`
- Evidence: `outputs/yanke-s93/`, `outputs/yanke-s96/` (including the receipt, backups, native report/logs, fit)

Do not adopt runtime defaults, close the canonical task or award creator approval from these automated checks.
