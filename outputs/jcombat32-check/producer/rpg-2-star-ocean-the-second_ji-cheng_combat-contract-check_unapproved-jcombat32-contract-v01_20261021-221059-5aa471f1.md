# Ji Cheng combat source check (UNAPPROVED)

Status: **TARGET PRODUCTION CHECKS PASS; WRAPPER SELF-TEST FAIL (not isolated)**. The source manifest appeared while this task ran. The unchanged wrapper’s positive control and a production-mode run pass on the emitted set, but the `--self-test` adversarial cases fail to isolate because their temp fixtures were written outside the producer root. No blanket Ji asset, art, motion, scale, default or approval pass is claimed.

Base `f22556c7d36b7f7db127f8a73568ec8a36c02941`. Canonical `game/scripts/app_state.gd` sha256 `e3a162ef3d70aafbb97f4a668b69813dc8aed3e327ee6a87b398aba29fdbc33f` and `game/scripts/battle_arena.gd` sha256 `a73fe020f0fbcf3621ced1286b89d03f88993d1b400ee52faec026b91a370818` are byte-equal to the producer copies. No runtime/default/mechanics/input/save/collision/ledger/Bible/registry/Git-index edit.

## Actual result

Source: `outputs/jcombat32/rpg-2-star-ocean-the-second_ji-cheng-combat_author-manifest_unapproved-jcombat32-v01_20261021-220632-53e4c35a.json`, sha256 `ce6f6b4209dccdc633b3b5dda9d8d2ca7f8b50bd4c99fd561fd5ff89cea72d34`, 63,182 B. Runtime manifest sha256 `aa49f9432145707290c989df9332ee9b075108c48f764fd38b7e83f3c272ff28`; index sha256 `9677d8e36cf080031d95610fe0d8b51ce9ad2c5ed49c3e7785da0dc4a0caf9e0`; sheet sha256 `2093f9022fc80c9d690fd9b58c7663bba3808bf1b2dd72f70b2d983f9a8fbdaf` (816x576, 6x4, 24 cells, 23 referenced).

| run | exit | result |
|---|---:|---|
| wrapper positive control (`--self-test` case 1) | 0 | PASS, validator PASS, native reader true, 0 failed predicates |
| wrapper production (`no --self-test`) | 0 | **PASS 38/38**; validator **180/180**; native reader **1056/1056**, 73 files, 96 raw-hash checks |
| wrapper `--self-test` overall | 1 | **FAIL**; positive PASS, two adversarial cases not isolated |

Evidence: `outputs/jcombat32-check/…combat-source-check_production…20261021-221900-4c7a0e15.json` (+ `.validator.json`, `.native-reader.json`) and `…combat-source-check…20261021-221500-8b2e6d47.json`.

Self-test failure, actual: `member_index_extra` and `action_source_drift` matched their expected predicates (`index.member_only`, `actions.skill.source_match`) but `isolated` is false. The existing native reader raised `ValueError: path.relative_to(ROOT)` because the temp fixtures were created under this writable check directory, not the producer root. A producer-root `--out` rerun was denied by the sandbox and no approval channel was available. This is a harness-location gate failure, not a demonstrated Ji source defect; it is not waived.

## Contract (confirmed on the emitted set)

- Character `{"member_id": "ji-cheng"}`, member-only index key `ji-cheng`; runtime/source/index all agree. No `hero:*`.
- `136x144` cell, pivot `64,136`, `logical_scale 0.5`, `display_proportion "0.65"`, `authored_facing "right"`, `tick_rate 30`, 6-column sheet, 10 role layers; the existing native reader requires only ≥2.
- 23 distinct pose cells + a separate still; 24-cell sheet. Compact frames are valid: the accepted Liang precedent and this set use 27 frames; **binding is per-action total ticks**, not hsc19’s 35 frames.

| action | frames | ticks | loop |
|---|---:|---:|---|
| idle | 2 | 28 | yes |
| attack | 5 | 13 | no |
| move | 4 | 12 | yes |
| guard | 2 | 14 | yes (2-tick intro, loop from hold) |
| dodge | 3 | 9 | no |
| skill | 5 | 14 | no |
| hit | 3 | 8 | no |
| defeat | 3 | 9 | no |

Total **27 frames / 107 ticks (107/30 s)**, equal to the hsc19 tick totals (`game/data/hsc19/…spritesheet-manifest…07587a3c.json`, sha256 `e32403b3218ff35221d2a6ef1c2c186acef8d2de048f9fa3f5c50fde35e2ee62`). `defeat` is the set key even though the arena sets `visual_action = "down"` (`battle_arena.gd:965`; loader lines 87–88/382–407).

Identity: 纪澄, 28, female, records restorer; shaved **LEFT** temple with razor lines and rectangular drop earring; straight dark shoulder bob with silver tips; ink-green long coat with uneven cream panels and grey sleeve lining; harness, hip vials, thigh strap/pouch; brass folding magnifier; small book. Concept sheet `outputs/…ji-cheng_character-sheet…dcea1a37.png` sha256 `4165c47e28329e2d4fd2dd160886118a70cb06fd160172b90ba45f00584cc546` is **unapproved**.

At `authored_facing: right` the near side is her **RIGHT**: silver-tipped curtain near, magnifier near hand, book far hand, hip vials/thigh strap/pouch, long cream panel/ragged point. The shaved LEFT temple/left-ear earring are far-side; the emitted manifest discloses only the undercut wrap and earring glint. Do not relocate the shaved temple to the visible right side. The loader mirrors one sheet for the other facing, so it cannot show the shaved left temple in both facings.

## Mechanics/state mapping

- **Attack**: 12 base damage + `boost` + `next_attack_bonus`; range `100.0`; cooldown `0.43 s`; immediate on request; VFX at enemy x, floor−28 (`app_state.gd:581`; `battle_arena.gd:696-713`). `ji-cheng` has no contact-event keys (only `hero` + female gets them, `battle_arena.gd:342`), so the heroine 5/30 contact cue does not apply.
- **Personal skill** 断层回读 / Fault-Line Recall: 14 energy, 2.2 s, rank default 1; `enemy_cooldown += 0.65*rank`, and windup same only when already winding up; no damage/heal. FX `personal-ji-cheng` at fighter x, floor−34 (`battle_arena.gd:852-879`; `app_state.gd:120,359`).
- **Relics job skill**: cost `10+3*stage`, 2.2 s; no range gate; cooldown `+= 0.25+0.2*rank+0.2*(stage-1)`, windup same when active; no damage. FX `job-relics` at fighter x (`battle_arena.gd:891-929`).
- **Guard** 30% damage/6 energy; **dodge** 12 energy/0.27 s invulnerable/0.75 s cooldown (`battle_arena.gd:830-840,952-955`). Enemy patrol 12/sentry 18, reach 69 (`battle_arena.gd:13-14,942`).
- Input `battle_attack/dodge/skill/job_skill/guard` maps to those functions; pause/switch/auto at `battle_arena.gd:417-425,1177-1185`. Visual mapping: dead→`defeat`, `dodge_time>0`→`dodge`, attack→`attack`, skill/hit→`skill`/`hit`, guard→`guard`, moving→`move`, else `idle` (loader 382–407).

Cue contract: attack strike and skill effect at **tick 0**, because companion damage/effect resolve on request; guard opens at tick 0; dodge/hit/defeat tick 0; attack clip 13/30, skill 14/30. Emitted `strikeCueTick = 0`.

Timing boundaries, measured: attack `13/30 = 0.43333 s` exceeds the `0.43 s` cooldown by `1/300 s` on Ji’s immediate path (the heroine is cut earlier at her 12/30 recovery); dodge `9/30 = 0.30 s` exceeds `dodge_time 0.27 s`, so the final `0.03 s` is not displayed (shared loader). The legacy `HERO_COMBAT_ACTION_DURATION` (.39/.24/.45/.30) clears `visual_action`, but a one-shot still plays to its own clip duration (loader line 401); do not re-time ticks to those legacy values. Keep 13/30 for tick-total parity.

## Palette/source reference

Palette tool `tools/…ji-cheng_explore-source-author…b2782add.py` sha256 `eac4d03afa45366d8cb21c71c632212ea0071d3190e2f0890a7d9fea029929ef`; it imports `jx.PAL` (line 67) from `…ji-cheng_south-idle-static-pilot-build-and-check…0d31a6f9.py` sha256 `18ef5efcc95a05518360998fb5ed1ce6e2abce6820e6586a0fa1ea0ca72b61b8`, ramps lines 86–103: coat `#5a7450/#3c5338/#223524/#0f1a11`, lining `#a9ada4/#787d76`, cream `#dcd0b2/#a89c84`, hair `#292c34/#111216`, silver `#e2e4e6/#b2b8c0/#7e848e`, skin `#f0d0bc`, brass `#e2c272/#a8844a`, leather `#a2724a/#77513a`, lens `#d2e4e8`, outline `#0c0a0e` (38 keys; full map in JSON). Exploration runtime `…jexplore31…58d91a02.json` sha256 `8999aad32aeb7057014a76030df4eb3ea1004f10fe0fdc298531d0c68568107d` is `80x112`, pivot `40,104`, density 2 — identity/palette only, not the combat cell. East static `…1c39fa48.png` sha256 `2c61d647794faf636f59bfdf373dbf9bb0200bade1c42960c0acfc3ccd11cbf1`, UNAPPROVED.

## Runtime gap

`battle_arena.gd` `COMPANION_COMBAT_POLICIES` lists only `zhao-ling` and `liang-xu` (lines 154–157). There is no Ji policy/index wiring, so the emitted set cannot load in the current canonical path without root-owned integration; Ji still draws legacy `JiCombatFrames` (`battle_arena.gd:1517,1525-1526`). Ordinary adoption remains false and separate.

## Clean self-test rerun (root)

```powershell
& "C:/Users/hkzha/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/python.exe" -X utf8 -I "<PRODUCER>/tools/rpg-2-star-ocean-the-second_lcombat29_combat-source-independent-check_wrapper-v01_20261021-201231-0fa32a.py" --root "<PRODUCER>" --manifest "<PRODUCER>/outputs/jcombat32/<AUTHOR_MANIFEST>.json" --out "<PRODUCER>/outputs/jcombat32-check/<REPORT>.json" --self-test
```

Use the **author** manifest, not the runtime manifest (`source_provenance` basename binding, wrapper:430-435). `--out` must stay under the producer root so the self-test temp fixtures resolve inside the existing native reader’s ROOT. Then inspect `status`, `failed_predicates`, every `checks[*].ok`, and the sibling `.validator.json` / `.native-reader.json`; do not infer a pass from exit 0 alone.

## Limitations

The wrapper `--self-test` is not clean; the target production-mode static checks passed 38/38, 180/180 and 1056/1056, but this is source/index/export evidence only. No Godot import/load, playback, normal input, motion, scale, art, default, save or creator approval. The concept and jexplore31 outputs are unapproved references. The single-sheet mirror cannot preserve the shaved LEFT temple in both facings. Root independently validates the final Ji output.
