# Battle arena wiring: independent clean-context closeout

Task `content.scene.battle-arena.wiring`; producer DeepSeek; independent inspection/integration Codex.

Tested game source: `99bf35affa8fd332802c3922a1c632e9ea22695e`. Canonical game code is unchanged for this milestone. Evidence: `outputs/battle-wiring-v04/rpg-2-star-ocean-the-second_battle-arena-wiring_root-integration-proof_v04_20261020-191841-072db685.json`.

## Actual result

The original Godot executable ran windowed640x360 from the ordinary Codex context with fresh physically created profile directories. Unfiltered raw log is clean: **297/297**, including88boundary,168victory,20defeat,15source and6setup checks. Four fresh normal-entry victories cover patrol/sentry × EN/ZH. Patrol starts64HP and takes4actual19-damage hits; sentry starts96HP and takes6. Cooldowns advance naturally at1/60, enemy AI damages the hero, and the hero is positioned once only. Rewards, idempotent finish callback, before/after saves, result click, safe return and destination-filtered reload are checked. A separate explicitly staged defeat case verifies no reward/after-victory save and return to menu. It is not counted as a natural victory.

Codex inspected actual start frames for both enemy types, Chinese victory, English Washington return and English defeat. These show the existing default placeholder character/enemy art and expected result/return surfaces. They do not accept art or establish a human playtest.

## Corrections and failed gates retained

The first wrapper failed after a clean297-check game run because it compared the report's eight raw hashes (seven game files plus fixture self-hash) to only seven. Rootr2 verifies all eight exact keys and hashes. Fresh import also generates UID/import metadata; rootr2 verifies generated entries correspond to tracked scripts/PNG/WAV source files and that the tracked game has no substantive Git diff. No diagnostic, source/hash, combat or behavior threshold is disabled. The first root guard initially rejected PNG/WAV import metadata; the corrected guard retains/discloses those entries and verifies their source association. Windows extended paths are used for long capture filenames. Failed original wrapper manifest/report/log and successful run evidence are preserved. Failed first-run duplicate captures remain local; published27captures bind the successful run.

The previous DeepSeek-sandbox root-certificate diagnostic is not suppressed or reclassified. This independent ordinary-context run has no such diagnostic, resolving the execution blocker for this verified artifact. The producer was stopped after output handoff to avoid redundant import-metadata cleanup; no quota/credit depletion was reported.

## Remaining limitation

A live language switch after victory exposes cached English reward text in the Chinese result screen. Title and button translate; the reward line does not. A separate small Codex fix/test is underway. This wiring milestone does not claim complete localization. Staged boundary/defeat setup and deterministic victory stepping are disclosed, not described as continuous manual input.

## Progress

The existing three-point wiring task meets its automated collision/encounter/exit/save criterion. No new task, denominator, per-version points or art acceptance. Full sprites0/52, scene visuals3/12, human post-art plays0/2 unchanged.
