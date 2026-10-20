# Battle result reward locale refresh

Recorded: 2026-10-20T19:20:06.543349+00:00

Base: `99bf35a`. Small runtime fix: store awarded XP/JP as per-arena numbers; format `result_reward_text` in `_refresh_text`. No second award or save operation is introduced. Existing `_finish_battle` idempotence guard stays intact.

## Evidence

- Baseline: 48/50 checks pass. EN to ZH and ZH to EN each leave the original reward language; two exact reward-line assertions fail.
- Fixed: 50/50 checks pass, clean checked-runner exit0, marker `RESULT_LOCALE_UNIT_OK`.
- Both starts are tested EN→ZH→EN and ZH→EN→ZH. Titles, buttons and exact reward strings match. Hero XP/JP and exact save-ID lists remain identical through language changes, repeated refresh and repeated finish.
- Six baseline and six fixed actual640x360 result screenshots. Root may inspect/choose the two switch images per stage.
- This is explicitly a unit fixture invoking the real finish callback directly. It does not simulate a natural victory, prove combat timing or count as a playtest.

Baseline raw arena SHA256: `d7c4fb46bbdff55596aac443d7eafc470be51728f00a78f2cc45b1a2301dec95`
Fixed raw arena SHA256: `41548c86eb04fb12a988c211373601f7c08d579b408d4951aa6d0f03302cb197`
Evidence manifest: `outputs/result-locale-v01/rpg-2-star-ocean-the-second_battle-result_locale-refresh-evidence_v01_20261020-192006-5907a714.json`

## Reproduce

`C:/Users/hkzha/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/python.exe tools/rpg-2-star-ocean-the-second_battle-result_locale-refresh-runner_v01_20261020-192000-a38c6d92.py fixed`

Runner creates a fresh unique output/profile folder on every run, inherits certificate configuration, uses the original Godot binary and checked runner with90s deadline. No diagnostic filtering. Import may be needed first in a fresh checkout.

## Limitations and earlier failed attempts

- Initial import attempt used a wrong Godot path and produced an empty log; original retained. Correct absolute path import passed in34.454s.
- First unit invocation failed GDScript type inference for prefix. Raw diagnostic retained; explicit String repaired the test before the two-failure baseline and50/50 fixed run.
- Fresh worktree import generated .import/.uid changes; these are preserved and excluded from the proposed integration.
- No visual-art approval, gameplay balance, natural victory or human playtest is claimed.

## Canonical integration inspection

Codex inspected the exact +5/-1 runtime diff and reran the unit fixture in the canonical checkout:50/50, clean checked runner, six actual captures. Codex viewed the EN→ZH and ZH→EN result screenshots; the reward line now matches the title/button language. XP/JP and exact save IDs remain unchanged after refresh and repeated finish. The original runner is preserved for the producer worktree; canonical reproduction uses `tools/rpg-2-star-ocean-the-second_battle-result_locale-refresh-root-runner_v02_20261020-192206-ac8c7d5e.py fixed`, whose tooling discovery supports both worktree depths. No new completion points.
