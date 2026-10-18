# Washington Capitol west — v12r2 sentry-encounter viewport fix (QA note, UNAPPROVED, opt-in only)

- **Date:** 2026-10-18, 04:20–04:50 EDT. Stamp `20261018-042200`, run id `7c1e5b39`.
- **Author:** Claude Code (Opus 5.5), signed in to Max through claude.ai firstParty. No quota or auth stop, and no paid or cloud fallback.
- **Status:** an **UNAPPROVED technical viewport fix**, reachable only with `-- --wdc-capitol-west-v12r2`.
  - With the flag off, the scene runs the base script.
  - The v12r1 flag alone gives exact v12r1, and the v12 flag alone gives exact v12.
  - No art is accepted. Counters are unchanged: 40.8 %, M2 10/12, scenes 3/12, sprites 0/52, playtests 0/2.
- **Repo actions:** nothing staged, committed or pushed, and the index is untouched.
  - Untouched: ledger, Bible, Site, progress JSON, `battle_arena.gd`, `scifi_exploration_area.gd`, `survey_annex.gd`, Chicago and Yonkers.
  - All v12 and v12r1 files and evidence are unchanged and stay historical.
- **Correction to the v12r1 note:** its header says the run ended "05:10 EDT". The actual end was about **04:13 EDT**. The note itself was left unedited as historical evidence.

## The defect and the fix

**Defect.** v12r1's camera eased to 1.5 scroll rows per walked row. Walking south into the sentry (`_draw_enemy` at (566,320)) triggers the encounter at about foot row 298. At that row v12r1's scroll is 75, so the feet blocks' bottom row (world row 337) sat at screen row 324, under the 318..359 footer.
- Over every walkable foot within 23 px of the sentry, the v12r1 worst case is screen row 324.
- Within 28 px it is screen row 331.

**Fix: `v12r2` selector.** It is 73 lines, `extends` the v12r1 selector, and overrides only `_v12_sync` with a new static `r2_scroll_for`.
- The curve has the same eased shape and the same start row (238, so the spawn stays at scroll 0).
- The ease is shorter: 12 rows instead of 20.
- The hold rate is 1.7 instead of 1.5. v12's instant kink was 2.0.
- Unchanged: art, walk mask, anchors, radii, encounter trigger, glyph pinning, label solver, annex and battle hand-offs, spawn and the canvas safety floor.

| foot row | v12 | v12r1 | **v12r2** |
|---|---|---|---|
| 238 (spawn) | 0 | 0 | **0** |
| 246 | 0 | 2 | 5 |
| 262 | 24 | 21 | 31 |
| 280 | 60 | 48 | 61 |
| 298 (north trigger) | 96 | 75 | **92** |
| 315 | 104 | 98 | 104 |

**Smoothness.**
- The peak rate is 1.70. The largest slope change is 0.071 per half row; v12 jumped by 2.0 at once.
- Real walk down lane x 300 and back: 53 frames each way, largest step 4 px per frame, no reversals.
- Approach routes: largest step 4 px per frame.

## Checks: `tools/…sentry-viewport-check…v12r2….py all` → **PASS 30/30**

These are technical gates. Report: `outputs/wdc-cw-v12r2_20261018-042200-7c1e5b39/…technical-check-report…json`.

- **Clean tracked HEAD:**
  - The v12r1 temp tree (`%LOCALAPPDATA%\Temp\w12r1-23596520\`) was reused. All **1,250** HEAD blobs that the overlay does not replace were re-hashed exactly.
  - The overlay is v12r1's enumerated files plus the v12r2 selector, the `.tscn` line (HEAD base → v12r2) and the harness. Every file was checked against the worktree.
  - The tree was re-imported, and the 4 headless smokes (`m4`, `m6`, `m7`, `m8_city_reentry`) pass.
- **Harness:** exit 0 with no errors, both in the clean tree and in the shared worktree. The shared-worktree run left no new `game/` status lines.
- **Defaults:**
  - All flags off: equal to `scifi_exploration_area.gd` for city, outskirts and ruins (entry and after-input image bytes, positions).
  - v12r1 flag only: equal to the v12r1 selector.
  - v12 flag only: equal to the v12 selector.
  - The command-line flag enables r2.
- **Curve:**
  - Godot's curve equals the tool's.
  - It is monotonic, with peak 1.7 and eased.
  - Spawn is at scroll 0.
  - The 48-row canvas is inside play rows 62..317 at every walkable foot row.
- **Sentry zone (static, every walkable foot):**
  - within **23 px** (the trigger zone, 1,616 feet): minimum scroll 92, feet bottom at screen row **≤ 307**;
  - within **28 px**, which also covers the last *drawn* frame before the trigger (2,341 feet): minimum scroll 83, feet bottom **≤ 316**.
- **Real routes, real input, real battle (zh and en):**
  - Entry is through the world map's `_enter_scene`, at scroll 0, with the dome region pixel-exact against the v12 flat.
  - **zh** walks the v12 contract's actual sentry route (north-west approach). **en** walks straight down column x 566 (pure north approach, the worst case).
  - Each walk ends in the real `battle_arena.tscn`.
  - **Last drawn frame before the encounter.** The trigger frame itself is never rendered, because the scene change is deferred to the end of that frame.
    - zh: 24.4 px from the sentry, scroll 89. en: 24.2 px, scroll 88.
    - All **112/112** feet-block texels are inside the play band. Their bottom row is at screen 310 (zh) and 311 (en), 7–8 rows above the footer.
    - 99 texels show the exact feet colour. The other 13 are behind the v11 `rt-fg` foreground layer: the inherited v12 draw order puts world art above the root canvas where the placeholder sentry is drawn. None are hidden by the HUD.
  - **Battle:**
    - auto mode turned on by the real `battle_auto` action, with the sentry's HP lowered from 96 to 12 as a fixture;
    - won through `_finish_battle(true)`, with both flags set by the battle;
    - the real `ui_accept` on the focused result button returns to the scene;
    - the heroine is on her battle-return texel, the scroll equals `r2_scroll_for(position)`, and the camera is current.
  - **South end** (372,354): scroll 104.
  - **Every shot** (entry, pre-trigger, battle return, south end, in both languages):
    - 640×360;
    - the heroine's 48-row canvas is inside the play band;
    - the test-only approved v8 south still (48 logical rows) is **605/605 texels unobstructed**, rows inside the band;
    - no label overlaps another label, a glyph or the heroine, and nothing sits outside the band.
- **Captures:** the deterministic ones (entry and south end, zh/en) are byte-identical between the clean tree and the shared worktree. The pre-trigger and battle-return frames depend on real-time stepping and are compared by state. The shared-worktree run had zh at 23.0 px, scroll 90, and en at 24.2 px, scroll 88.
- **Saves:** the real `user://saves` is unchanged. Test saves went to `user://test-saves/wdc-cw-v12r2`.

## Native 640 evidence (`outputs/wdc-cw-v12r2_20261018-042200-7c1e5b39/`)

File names are `rpg-2-star-ocean-the-second_wdc-capitol-west_<view>_unapproved-v12r2_20261018-042200-7c1e5b39.png`. Values are sha256 prefixes.

| view | zh | en |
|---|---|---|
| `rt640-*-entry-v8ref` | `4e69f516` | `6d3ff722` (= v12r1 en v8ref) |
| `rt640-*-sentry-pre-trigger` | `f6b949c6` | `7d628301` |
| `rt640-*-battle-return-v8ref` | `c837b2bb` | `6ff0d555` |
| `rt640-*-south-end-v8ref` | `625e1a29` | `1a106b2b` |

Also in that dir: `technical-check-report` (`c02fe469`), `replay-run` (`c628cf15`, with overlay pins, smokes and logs), `clean-harness-report` (`6ac10423`) and `main-harness-report` (`768a5b31`).

## Exact diffs and files

**`game/scenes/scifi_exploration_area.tscn`** has one line changed versus HEAD. The worktree's whole diff is this line. It replaces the earlier v12r1 hook line.
```
-[ext_resource type="Script" path="res://scripts/scifi_exploration_area.gd" id="1_area"]
+[ext_resource type="Script" path="res://scripts/rpg-2-star-ocean-the-second_wdc-capitol-west_exploration-opt-in-selector_unapproved-v12r2_20261018-042200-7c1e5b39.gd" id="1_area"]
```
Its LF text pin is `37f634af…`.

**New files (untracked):**
- `game/scripts/rpg-2-star-ocean-the-second_wdc-capitol-west_exploration-opt-in-selector_unapproved-v12r2_20261018-042200-7c1e5b39.gd`: 73 lines, `18cf5e30…`.
- `tools/rpg-2-star-ocean-the-second_wdc-capitol-west_sentry-viewport-harness_unapproved-v12r2_20261018-042200-7c1e5b39.gd`: 411 lines, `a03366a0…`. Test-only `-s` tool.
- `tools/rpg-2-star-ocean-the-second_wdc-capitol-west_sentry-viewport-check_unapproved-v12r2_20261018-042200-7c1e5b39.py`: 427 lines, `4cab8ea2…`. It imports the v12r1 check tool's helpers read-only.
- This note.

**Runtime dependencies** (unchanged from the v12r1 manifest, all untracked):
- the v12r1 selector `4f64abb5…`;
- the v12 selector `34e017bf…`;
- the 7 v12 runtime PNGs and 7 `.import` sidecars. Hashes are in the v12r1 note and in `replay-run.json`.

**Staging plan delta vs v12r1** (for root, not executed):
- add the v12r2 selector, the two tools above, this note, and the 12 files in the v12r2 outputs dir (or at least the report plus the 4 pre-trigger and battle-return PNGs);
- stage the `.tscn` hunk as the v12r2 line;
- keep everything in the v12r1 plan.
- To revert to v12r1, point the `.tscn` back at the v12r1 selector.

## Remaining limitations

1. **The camera runs a little faster than v12r1:** peak 1.7 instead of 1.5, still below v12's 2.0 and eased instead of a kink. The heroine's screen foot row moves within 266..312 over a full south walk (v12r1: 279..312). Feel review is still needed.
2. **Inherited draw order.** The placeholder sentry is drawn on the root canvas, under v11's foreground. At the north trigger, 13 of its 112 feet texels are behind `rt-fg` art, which is world occlusion, not the HUD. Its translucent 24-px aura still reaches past the footer.
3. **English sentry label.** As in v12r1, the label solver puts the wide "Automated machine" label with its right edge about 110 px left of the sentry in these crowded pre-trigger frames (zh sits right above the sentry). Nothing overlaps, but the association with the sentry is weak.
4. **The battle used a fixture.** HP 12 and auto mode prove the hand-off, the outcome path and the return, not balance. The growth-screen branch was not exercised.
5. **The v8 sprite exists only in the harness.** It stands 44 px to whichever side clears the labels and the sentry. At 640×360 it is the 0.5-scale nearest sample of the approved PNG (sha `ccf9d2a2…b6fd`).
6. **Still placeholders.** The sentry and markers are still the baseline placeholders. No new art was made.
7. **The clean tree is a reused temp copy** of HEAD `c20118d`, re-verified blob by blob, not a fresh `git archive`. Upstream main is `7370739`. This proof is against the local HEAD only.
