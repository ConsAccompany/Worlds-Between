# exp-pack08 exploration-source packager QA note (TEST-ONLY)

Status: synthetic capability test and tool only. No art, motion, default enablement or creator approval. No existing game/script or default files were edited. No shared ledger or Git index was touched.

Base commit: `e6a97c87a265dacbc1399607176a29c3f12f9a93` (isolated worktree `work/dual08/ds-pack`).

## Deliverables

- Tool: `tools/rpg-2-star-ocean-the-second_exploration-source-package_packager_v01_20261020-171611-e359539c.py` (sha256-text-lf-v1 `e7c1cf146c1a98cc1d4b03ae30b88f9304bc30d4aea5fb1e1e8a8124d157c338`).
- Tests: `tests/exp-pack08/rpg-2-star-ocean-the-second_exploration-source-package_packager-tests_test-only-v01_20261020-171611-c1ba3679.py` (sha256-text-lf-v1 `5a8912d18e3ca5ff14e76b5cc5b7027fa988611e255f641d4c06e32781d169df`).
- Test report: `outputs/exp-pack08/rpg-2-star-ocean-the-second_exp-pack08_packager-tests-report_test-only-v01_20261020-172030-46c06821.json` (sha256-bytes `bbae8c53fa44a7b431edbc360aad8d8fa0369d55f76abf55ea3cdf5392901e08`).
- Demo provenance: `outputs/exp-pack08/rpg-2-star-ocean-the-second_exp-pack08_demo-provenance_test-only-v01_20261020-172030-5452fe83.json` (sha256-bytes `201f88b1dfeef4bd77cd496c58a2f3cbb461cc54159aa9ad7ade8e05f60c626d`).
- Synthetic demo source/package: `outputs/exp-pack08/d1/source` and `/package` (16 frame PNGs; 19 package files; no `.import` files).
- Godot logs: `outputs/exp-pack08/rpg-2-star-ocean-the-second_exp-pack08_godot-import_test-only-v01_20261020-172030-5452fe83.log`, `outputs/exp-pack08/rpg-2-star-ocean-the-second_exp-pack08_godot-loader-probe_test-only-v01_20261020-172030-5452fe83.log`.

## Behavior checked

- Full source contract: schema, actor_id, density, frame_size, pivot, exactly idle/walk, exactly 4 directions, idle 1..16, walk 2..16, integer duration 40..2000.
- Relative-only paths, no traversal/absolute/out-of-root, junction/symlink rejection, unique lowercase project_subject_purpose_variant_timestamp-id `.png` names.
- 80x112 8-bit RGBA, hard alpha, transparent border, no alpha at y>=104, idle body exactly 96 source px with last opaque row 103, walk body <=97, pivot/floor semantics.
- Byte-for-byte PNG copies, runtime set schema, registry schema, source/provenance hashes, no import metadata copied, no network.
- Atomic failure: invalid input leaves no package; existing empty out stays empty; non-empty out is refused and unchanged.
- `--repo-root` containment and relative resolution.

## Result

- Targeted Python suite: **37/37 passed, 0 failed, 0 skipped**; exit 0. Cases include valid full four-direction input and missing/invalid schema, actor, density, frame_size, pivot, actions, directions, counts, durations, paths, filenames, duplicates, alpha, size, floor, body, source_files and repo-root containment.
- Godot loader probe: the existing `exploration_sprite_set_pilot.gd` loaded the emitted package and printed `EXP_PACK_PROBE_OK frames=16`; the mutated invalid package was rejected and the host sprite transform stayed unchanged (warning `rejected for hero:female: idle/south frame 1 duration_ms must be an integer 40..2000`).
- The bounded checked runner did **not** report a clean pass: after the loader marker, Godot headless emitted `ERROR: Failed to read the root certificate store.` plus exit-time leak/resource errors at exit 0. Per project policy, `ERROR` fails even at exit 0, so this is recorded as a probe-process limitation, not converted into a pass. The sandbox has no approval channel for a wider one-shot retry.

## Exact commands

```powershell
$py = 'C:/Users/hkzha/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/python.exe'
$test = '<repo>/tests/exp-pack08/rpg-2-star-ocean-the-second_exploration-source-package_packager-tests_test-only-v01_20261020-171611-c1ba3679.py'
& $py -I $test --work-root '<repo>/tmp/e8f1' --godot 'C:/Users/hkzha/Documents/Codex/2026-10-12/rpg-2-star-ocean-the-second/work/tooling/godot-4-7-2/Godot_v4.7.2-stable_win64_console.exe' --report '<repo>/outputs/exp-pack08/<report>.json'
```
Actual producer source, when the coordinator has the manifest (not awaited or polled here):
```powershell
& $py -I '<repo>/tools/rpg-2-star-ocean-the-second_exploration-source-package_packager_v01_20261020-171611-e359539c.py' --source 'C:/Users/hkzha/Documents/Codex/2026-10-12/rpg-2-star-ocean-the-second/work/dual08/cl-explore/outputs/hsea-exp02/<producer-source-manifest>.json' --out '<repo>/outputs/exp-pack08/actual-<new-unique-id>'
```

## Remaining limits

- The producer art under `work/dual08/cl-explore/outputs/hsea-exp02` was not polled or packaged; only the synthetic demo was packaged.
- The Godot probe is loader-acceptance evidence only; it is not a clean checked-runner pass and no visual/motion/default/approval claim is made.
- Windows symlink creation required administrator rights, so the path-escape test used a directory junction (still rejected by the tool).
- The source schema deliberately allows extra top-level keys for provenance notes; action/direction objects are exact. The source manifest filename itself is not naming-rule validated by the tool (only referenced PNG filenames are); the demo manifest filename does follow the rule.
- A relative/very long temporary root can exceed MAX_PATH for ordinary Python copy helpers; use a short work root (the final run used `tmp/e8f1`). The packager itself uses extended-length prefixes when needed.
