# Heroine optional-pilot one-shot facing latch QA

- Project: rpg-2-star-ocean-the-second
- Base commit: 4ef439193286d271d5311987773ca3f96229c4ce (worktree branch codex/hero-facing-v01)
- Task: fix the optional contact-event pilot's non-attack one-shot facing defect; synthetic fixture only, no art approval/default adoption.
- Tested source: game/scripts/rpg-2-star-ocean-the-second_combat-sprite-set_loader-playback_pilot-v01_20261018-153656-43a19158.gd
- Text hash normalization: sha256-text-lf-v1 (CRLF replaced with LF before hashing; working files were already LF, raw SHA-256 equals normalized SHA-256).

## Source and test hashes

| Artifact | SHA-256 (LF-normalized) |
| --- | --- |
| Pre-fix loader (preserved) | d3ec4a64b6ce07bd1589626c209cd4ff9fe18e3cfc6412fa0580688fb0d88d2f |
| Fixed loader | ac8cd3dce945de02763fc7c8037d7587a83e874297ee3e0f5e6675d073cfdebf |
| Facing check script | f89c6d0f1cfd3762ac219f34cac968bac6c740d0a85edd27073af65f8fd6aa4f |
| Pre-fix fixture copy | d3ec4a64b6ce07bd1589626c209cd4ff9fe18e3cfc6412fa0580688fb0d88d2f |

The preserved pre-fix copy is at game/tests/fixtures/facing-latch-v01/ and outputs/facing-latch-v01/20261020-165240-7f0afc08/; both raw and LF SHA-256 are d3ec4a64b6ce07bd1589626c209cd4ff9fe18e3cfc6412fa0580688fb0d88d2f.

## Checked result

Runner: tools/rpg-2-star-ocean-the-second_godot_checked-runner_v01_20261018-203400-f74ac6d1.py
Godot: P/work/tooling/godot-4-7-2/Godot_v4.7.2-stable_win64_console.exe

Pre-fix (preserved loader, explicit fixture state):
- 31 PASS, 7 FAIL, checks=38, process exit 1.
- Failing cases are exactly the defect: dodge hold (both facings), hit hold, skill hold, defeat hold, per-fighter crossed latch, shared-time dodge after crossing.
- Log: rpg-2-star-ocean-the-second_heroine-facing_prefix-check_v04_20261020-165313-18819495.log

Fixed loader:
- 38 PASS, 0 FAIL, FACING_TEST PASS checks=38, process exit 0.
- No SCRIPT_ERROR or parser error in the check log.
- Checked runner reports FAIL diagnostic and exits 1 solely because Godot emits the environment diagnostic ERROR: Failed to read the root certificate store. at startup; the runner correctly fails on ERROR even with exit 0. This environment failure is retained, not suppressed.
- Fixed log: rpg-2-star-ocean-the-second_heroine-facing_fixed-check_v04_20261020-165313-18819495.log
- Godot log: rpg-2-star-ocean-the-second_heroine-facing_godot-fixed_v02_20261020-165313-18819495.log

Commands (run from the ds-face worktree):

    python tools/rpg-2-star-ocean-the-second_godot_checked-runner_v01_20261018-203400-f74ac6d1.py --timeout 60 --expect "FACING_TEST PASS" --log <pre-fix.log> -- <godot> --headless --log-file <godot-prefix.log> --path game -s res://tests/rpg-2-star-ocean-the-second_heroine-facing_pilot-latch-check_v01_20261020-165313-18819495.gd -- --tmp-dir=<out>/tmp --loader=res://tests/fixtures/facing-latch-v01/rpg-2-star-ocean-the-second_heroine-facing_prefix-loader_v01_20261020-165240-7f0afc08.gd

    python tools/rpg-2-star-ocean-the-second_godot_checked-runner_v01_20261018-203400-f74ac6d1.py --timeout 60 --expect "FACING_TEST PASS" --log <fixed.log> -- <godot> --headless --log-file <godot-fixed.log> --path game -s res://tests/rpg-2-star-ocean-the-second_heroine-facing_pilot-latch-check_v01_20261020-165313-18819495.gd -- --tmp-dir=<out>/tmp

## Coverage

The fixed 38 checks cover both facings; entry/restart latch; dodge, hit, skill and defeat holds; release to idle; defeat hold through revive; enemy exactly same x retaining previous facing; hit/skill/dodge ending boundaries; interruption/relatch; per-fighter isolation; 30/60 shared-time action/facing/frame equivalence; explicit attack event clock/facing preservation; dodge/skill/hit preemption; legacy no-cross state/render parity over 45 common ticks; and missing/empty/malformed set fallback.

## Limits

- Loader-level deterministic state/frame checks only. battle_arena.gd was not edited or exercised; no combined game gate was run.
- Synthetic diagnostic fixture, not character art. No art approval, default adoption, or motion-fluidity claim.
- The checked runner's green gate is blocked by the pre-existing Godot Windows certificate-store environment error, not by a test failure. Do not report the overall runner as PASS.
- No commits, staging, shared ledger, Bible, registry, Site, account changes, or legacy report-path overwrites.
- The only content diff from HEAD is the loader (git diff --stat shows 12 insertions, 2 deletions there). Godot import created the ignored game/.godot cache; generated .import content is byte-identical to HEAD on sampled files (git status may show stale stat entries because the sandbox denied index.lock refresh).