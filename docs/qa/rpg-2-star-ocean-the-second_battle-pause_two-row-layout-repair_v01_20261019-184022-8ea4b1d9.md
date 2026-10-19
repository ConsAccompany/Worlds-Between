# Battle pause: two-row layout repair

## Scope and cause

Codex supporting task: repair the existing pause personal/job-skill overlap and English Resume-button overflow at native 640×360. This is a usability correction, not new art or creator acceptance.

The existing personal-skill button at `(78,99,139,36)` used full default-font translated text; its actual text minimum exceeded the nominal width and reached the job button beginning at x223. The Resume button at `(493,99,61,36)` similarly expanded beyond the pause panel in English. Existing EN/ZH actual captures under `outputs/battle-ui-skin-v01/actual/` show the defect; prior root QA already disclosed it.

## Exact repair

Only eleven geometry literals in `game/scripts/battle_arena.gd` and one matching panel constant in the existing root-v02 skin helper changed:

| Element | New geometry |
| --- | --- |
| Pause panel | `(55,43,530,286)` |
| Personal skill | `(78,99,288,36)` |
| Resume | `(430,99,124,36)` |
| Two job skills | `(78+246×stage,142,230,32)` |
| Target label | `(78,185)` |
| AI policy | `(365,179,189,27)` |
| Target buttons | Existing x/size, y211 |
| Order buttons | Existing x/size, y249 |
| Feedback | `(78,292)` |

No wording, fonts/font sizes, callbacks, signals, input settings, combat logic, resources or opt-in defaults changed. The original arena already contained the repaired ambient loop guard and opt-in pilots; it was preserved whole except for these eleven literals. A source reconstruction check proves exactly that change set. The existing skin helper's `PAUSE_PANEL_RECT` changes from height265 to286 so its exact lookup continues to apply.

## Actual verification

Windowed Godot4.7.2, native640×360, Dummy audio, fresh APPDATA/LOCALAPPDATA, finite100-second checked runner:

- **7817/7817 contracts pass**. This is the pairwise geometry matrix count, not a completion-score measure.
- EN/ZH × skin off/on × four current party members × plain/personal-checkmark/both job-checkmark states: actual text/control minimum sizes fit, all visible content stays inside the panel, and no visible interactive/text pair overlaps.
- Both job stages are open in test fixtures; real clicks select each exact queued job ID without spending energy during pause. Resume executes the same job and exact13/16-energy cost. Real personal-skill click queues only, then Resume executes the exact current member's12/16/14-energy cost. No direct signal emission substitutes for mouse clicks.
- Thirty explicit combat updates per paused context leave fighters, enemy state and party resource state unchanged.
- Normal, victory and defeat captures remain **pixel-identical** to pre-repair controls for both languages and skin off/on. For the frozen skin-on control, the unchanged frozen helper is applied externally, avoiding accidentally testing the old panel through the new helper constant.
- Two actual audio mix boundaries drain after test-owned players are stopped and detached; final log is free of script/runtime errors and warnings. The process exits0 with required `PAUSE_LAYOUT_DONE` marker.
- Codex viewed actual EN/ZH skin-on pause captures: full personal labels and queued checkmarks, both job buttons and Resume are legible and clear inside the enlarged panel.

## Preserved failure

The first checked run stopped immediately on a test-harness parse error: an inferred `key` local was built from an untyped loop value. No runtime checks executed. It was corrected to explicit String typing; no game source or geometry threshold changed in response. The original failure log remains beside the final second-run log.

## Source bindings and artifacts

All new files use tag `20261019-184022-8ea4b1d9`.

| Source | Raw SHA-256 |
| --- | --- |
| Frozen arena before repair | `e182709b83645321769c780a83951ad0bb605eec8c05267626aeddd07ba06309` |
| Arena after repair | `7f6233522e90e044f4c16ee0a3a39bc066658ea0a01dae38304ee17acb4077c0` |
| Frozen root-v02 helper | `4458b658ccd6536ba5e73934a5ff4f3e2a3fcef3167df0da142a6309105fdd1b` |
| Helper after repair | `58c469c76021cca8ede12b61dbd78583917a101df183d7a07204a67e37b1c009` |

- Probe: `tools/rpg-2-star-ocean-the-second_battle-pause_layout-runtime-check_v01_20261019-184022-8ea4b1d9.gd`.
- Source-bound proof, 7817-check report, frozen exact sources, first/second raw logs and actual captures: `outputs/pause-layout-v01/`.
- Captures for review: `rpg-2-star-ocean-the-second_battle-pause_en1-pause-two-rows_actual-640_v01_20261019-184022-8ea4b1d9.png` and equivalent `zh1`; `en0`/`zh0` show skin off.

The proof hashes every source/report/capture/log. Text reconstruction compares UTF-8 with explicit CRLF→LF normalization; hashes are raw bytes. Root must preserve staged bytes through its normal hash gate. No Git/index, ledger, Site or provider operation was performed. No full UI/art approval, arbitrary user-name stress test or new human playtest is claimed.

## Coordinator inspection

Root independently inspected the exact +11/-11 arena geometry diff and helper panel constant, verified all raw source/evidence hashes, and viewed native EN/ZH skin-on captures. The personal skill, both job skills and Resume are clear inside the panel. This is an unscored usability repair of an existing menu defect; no added production points, art approval or playtest credit.
