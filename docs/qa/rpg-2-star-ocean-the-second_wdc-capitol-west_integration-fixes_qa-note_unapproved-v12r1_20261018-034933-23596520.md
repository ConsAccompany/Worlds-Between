# Washington Capitol west — v12r1 bounded integration fixes (QA note, UNAPPROVED, opt-in only)

- **Date:** 2026-10-18, 03:49–05:10 EDT. Stamp `20261018-034933`, run id `23596520`, run dir `outputs/wdc-cw-v12r1_20261018-034933-23596520/`.
- **Author:** Claude Code (Opus 5.5), signed in to Max through claude.ai firstParty. No API key and no paid fallback. No quota or auth stop happened during the run.
- **Status:** an **UNAPPROVED technical amendment** to the v12 integration candidate. It is reachable only with `-- --wdc-capitol-west-v12r1`.
  - The art is not accepted.
  - The v8 frame is shown as a scale reference only. It is not a sprite approval.
  - Counters are unchanged: 40.8 %, M2 10/12, scenes 3/12, sprites 0/52, playtests 0/2.
- **Repo actions:** nothing staged, committed or pushed, and the Git index is untouched.
  - Untouched: ledger, Bible, Site, progress JSON, `survey_annex.gd`, `battle_arena.gd`, Chicago, Yonkers and `scifi_exploration_area.gd`. That last file's pre-existing NYC/Yonkers diff equals the batch-0340 snapshot, and its mtime is still 2026-10-17 18:26.
  - The v12 selector, its tools, art and evidence are unchanged.
- **Read:** this stream's dispatch, the resume handoffs `…125b3a68` and `…cae4bf90`, the follow-up brief `…c36d289f`, and the v12 QA note `…66d00477`. There is no `AGENTS.md` in the repo, so naming follows `~/.codex/AGENTS.md`.
- **Scope note:** this dispatch narrows `…c36d289f`. Ledger receipts, the map-art progress detail and staging belong to root. None of them were done here.

## What changed (each item is one of the defects Codex listed)

v12r1 is a selector that `extends` the v12 selector. It keeps v12's art layers, walk mask, clue anchors and IDs, interaction radii and order, encounter radius, bypass zone, annex hand-off and battle hand-off.

1. **Camera (fixes the unsmoothed 2× south drift).**
   - v12 jumped from rate 0 to rate 2 at foot row 250.
   - v12r1 uses an eased follow curve over foot rows:
     - scroll is 0 up to row 238;
     - over 20 rows it eases in to **1.5 scroll rows per walked row**;
     - it holds that rate, then eases out over 20 rows to the 104 limit.
   - The curve is monotonic, so there is no overshoot. The largest change in slope is 0.0375 per half row (v12's kink was 2).
   - It takes the sub-pixel foot position, which avoids integer rounding steps.
   - A safety floor keeps the 48-row actor canvas inside play rows 62..317. This was checked at every walkable foot row of the mask.
   - Real-input walk south 230 → 354 and back:
     - 53 frames each way;
     - largest per-frame scroll step 4 px (feet move 2.33 px per frame);
     - 0 direction reversals;
     - the heroine's screen foot row stays within 279..312.
   - For comparison, v12's 2× rate peaked at 4.67 px per frame.
   - **Spawn:** moved 8 rows north, from (372,246) to (372,238), so entry is at scroll 0 with the whole dome in view.
2. **Marker and footer clipping.**
   - A clue glyph whose circle would be cut by the header or footer is **pinned inside the play band**.
   - A glyph more than 44 rows outside the band is not drawn.
   - A pinned glyph that would sit under the heroine steps 33 px to her side.
   - Unpinned glyphs stay at their real world positions.
3. **Right-side patrol/bypass label crowding.**
   - Each world label takes the first free slot from this list:
     - v12's default position;
     - above, below, left, right;
     - the four diagonals;
     - two higher rows;
     - then a slide along those rows.
   - A slot is free when it is inside the play band and clears the other labels, every drawn glyph, Ji, the sentry and the heroine canvas.
   - A label keeps its slot while that slot stays free (hysteresis), so labels don't flicker as she walks.
4. **Battle return is now real.**
   - The heroine walks into the sentry with real input, which opens the real `battle_arena.tscn` (enemy `sentry`).
   - Auto mode is turned on by the **real `battle_auto` input action**.
   - The battle's own code reaches `enemy_hp == 0`, then `_finish_battle(true)`. That sets `returning_from_battle` and `enemy_cleared_for_return` and writes the after-battle auto-save to the test root.
   - A real `ui_accept` presses the focused result button, which runs `_return_after_result` and changes back to the exploration scene.
   - **Test fixture:** the sentry's HP is lowered from 96 to 12 before auto mode starts, so the run is short. No victory flags are set by the harness.
   - Result: back in the scene with v12r1 active.
     - The heroine is on the battle return texel (534,289), 44.5 px from the sentry, on a walkable spot.
     - Scroll is 62, which equals `r1_scroll_for(position)`, and the camera is current.
     - The patrol is cleared and the return flag is consumed.
     - The label layout is clean.
     - Capture: `rt640-zh-battle-return`.

## Clean tracked-HEAD proof (no shared-worktree swapping)

1. **Export.** `git archive` of HEAD `c20118d` `game/` was taken with `core.autocrlf=false` into a private temp root, `%LOCALAPPDATA%\Temp\w12r1-23596520\` (longest path 239 characters). All **1,251 tracked blobs** were re-hashed and match their git blob ids (tree `a7c2a093…`).
2. **HEAD baseline.** HEAD was imported, then the 4 headless smokes ran (`m4`, `m6`, `m7`, `m8_city_reentry`): **all pass**.
3. **Overlay.** Only the enumerated overlay was copied in (manifest below), then the tree was re-imported. The same 4 smokes **all pass** with the overlay.
4. **Harness runs in the clean tree:**
   - the v12r1 harness, windowed at 640×360 (full run);
   - the same harness at the default 1280×720 window (v8 pair only);
   - the **unchanged v12 harness**. Its 12 captures are **byte-identical** to the existing local (uncommitted) v12 outputs. So v12 does not depend on the dirty base script and stays reproducible through the new hook.
5. **Main worktree.** The same v12r1 harness also ran once in the main worktree. All 16 deterministic captures are byte-identical to the clean-tree captures. The run left no new `game/` status lines, so no `.uid` or `.import` files were created.
   - The battle-return frame is compared by state, not bytes. Real-time stepping ends the walk into the sentry at a slightly different sub-pixel spot in each run (return (534,289) vs (535,288)).
   - The many pre-existing untracked `.uid` files under `game/` belong to other sessions' earlier imports. Their status was the same before and after.
6. **Saves.** Harness saves go only to `user://test-saves/wdc-cw-v12r1`. The real `user://saves` tree was SHA-256-listed before and after every run and is **unchanged**.

## Results: `tools/…integration-fix-check…v12r1….py all` → **PASS 50/50**

These are technical gates, not art acceptance. Report: `…technical-check-report_unapproved-v12r1_….json` (sha256 `199acb0d…`).

- **Clean replay:**
  - every HEAD blob exact;
  - HEAD smokes and overlay smokes pass;
  - overlay = worktree candidate files (LF-normalised), and only the enumerated files;
  - harness exit 0 with no errors;
  - v12 reproduces byte-identically.
- **Default behaviour:**
  - both flags off: the selector equals `scifi_exploration_area.gd` for city, outskirts and ruins (entry and after-input image bytes, positions, texts, state);
  - v12 flag only: v12r1 equals the unamended v12 selector (images, positions, texts, state; spawn still (372,246));
  - the command-line flag enables r1.
- **Camera:**
  - the Godot curve equals the tool's reimplementation;
  - monotonic, peak 1.5, eased;
  - canvas inside the band at every walkable row;
  - real walks are smooth;
  - flow (879 frames) and sweeps (555 frames) stay walkable and in band, with the largest scroll step 4.
- **Layout over 2,570 walkable feet** (8×6 grid, before and after the objectives):
  - 0 label/label overlaps;
  - 0 labels over a glyph;
  - 0 labels over the heroine;
  - 0 labels or glyphs outside the play band.
  - Glyph pinning: the strata panel at 604 positions, the bypass waymark at 892.
- **Captures (12 at 640×360, zh/en):** entry, records prompt, records checked, occlusion, patrol/bypass (scroll 99), strata near.
  - Each has the heroine canvas in band, no label overlap, no label over a glyph or the heroine, glyphs and labels in band, and the hint ending left of Save.
  - The entry dome region is pixel-exact against the v12 flat in zh and en.
  - The patrol view shows the enemy label and the bypass glyph separated.
  - The records glyph and label show at the prompt, and the records are checked afterwards.
- **v8 reference pair:**
  - the approved PNG matches its pinned sha256 `ccf9d2a2…b6fd`;
  - opaque height is **exactly 48 logical rows**: 48 px at 640×360 and 96 px in the 1280×720 window;
  - its bottom row is level with the runtime heroine's feet.
- **Flow:**
  - entry through the world map's `_enter_scene` at the spawn, scroll 0;
  - records, then Ji's dialogue and Invite, both traces, strata assist, bypass without battle, and the E/S/W edge walks, all with real input;
  - annex round trip back to (371,215) with v12r1 active;
  - real battle hand-off, victory and result-button return (above);
  - Esc to the world map;
  - sweeps end walkable;
  - the runtime mask equals the PNG at all 230,400 texels.
- **Side effects:** real saves unchanged; main-worktree run OK with no `game/` side effects; clean and main captures byte-identical.

## Captures to inspect (all 640×360 unless noted)

Files are in `outputs/wdc-cw-v12r1_20261018-034933-23596520/`, named `rpg-2-star-ocean-the-second_wdc-capitol-west_<view>_unapproved-v12r1_20261018-034933-23596520.png`. Values are sha256 prefixes.

| view | zh | en |
|---|---|---|
| `rt640-*-entry` (= `v8ref-off`) | `3644185a` | `cfe04454` |
| `rt640-*-records-prompt` | `8010daf8` | `454061b9` |
| `rt640-*-records-checked` | `7525a891` | `2e992ca4` |
| `rt640-*-occlusion` | `260c546f` | `4811b8c4` |
| `rt640-*-patrol-bypass` | `110b968d` | `be4d6691` |
| `rt640-*-strata-near` | `32131c5b` | `343eafb8` |
| `rt640-*-v8ref` | `167c11cf` | `6d3ff722` |
| `rt1280-*-v8ref-off` (1280×720 window) | `c8bb3d5d` | `c3a6ffdf` |
| `rt1280-*-v8ref` (1280×720 window) | `f51cd7ac` | `a063fbd4` |
| `rt640-zh-battle-return` | `ea405775` | — |

Reports in the same dir:
- `clean-replay-run` (export, overlay manifest, smokes, run logs);
- `clean-harness-report-full` / `-v8hd`;
- `clean-contract`;
- `main-worktree-run`;
- `main-harness-report-full`;
- `technical-check-report`.

The original v12 captures and report are untouched and remain the functional baseline.

## Limitations (honest)

1. **Look-ahead is lower than v12.** The camera now moves at most 1.5× walking speed. When the heroine walks straight south into the sentry, the encounter triggers at about scroll 75 (v12: 96), so the sentry's lowest 8 rows (its feet blocks) are still under the footer at that moment. The encounter, its radius and its position are unchanged. Feel review is still needed.
2. **Crowded patrol view.** At the specific patrol/bypass pose, the sentry, bypass waymark, strata glyph and heroine leave no free slot near the sentry for the wide English "Automated machine" label. The layout therefore puts it about 78 px left of the sentry, beside the heroine (zh sits right above the sentry). Nothing overlaps, but the label sits further from the sentry than ideal.
3. **Pinned glyphs move.** A pinned glyph is drawn up to 44 rows from its real anchor. Example: at entry the strata panel and the bypass waymark sit on the footer edge. Interaction still uses the real anchors and radii.
4. **The battle used a fixture.** HP was lowered to 12 and auto mode chose the actions. This proves the hand-off, the outcome path and the return, not combat balance. In a fresh run the result went straight to exploration. The growth-screen branch (pending job choice) was not exercised.
5. **Still placeholders.** The sentry is still the baseline `_draw_enemy` box, and the markers are the baseline circles. The art is v11's, unchanged. No new artwork was made.
6. **The v8 pair is a reference only.** At 640×360, the 0.5-scale v8 is subsampled (every other source row). The 1280×720 pair shows its full 96-px detail, as the game window draws it. The v8 sprite exists only in the harness. No runtime hero asset changed.
7. **Review frames are posed.** The heroine is placed by assignment after one real facing input, as in v12. The objective, annex, battle and camera routes are walked with real input.
8. **Temp tree left in place.** The clean tree remains at `%LOCALAPPDATA%\Temp\w12r1-23596520\` for root to re-inspect. It can be deleted (about the size of `game/` plus `.godot`).

## Exact dependency manifest (clean replay overlay over HEAD `c20118d`)

Pins are `sha256-text-lf-v1` for text and `sha256-bytes` for PNG (prefixes; full values are in `clean-replay-run`).

**Modified tracked file:**
- `game/scenes/scifi_exploration_area.tscn`. Its one line goes from HEAD `res://scripts/scifi_exploration_area.gd` to the v12r1 selector. Pin `244596c6…`.
- The main worktree's diff is exactly this one line. It replaces the pre-existing v12 hook line.

**Pre-existing candidate hook dependency (untracked):**
- `game/scripts/rpg-2-star-ocean-the-second_wdc-capitol-west_exploration-opt-in-selector_unapproved-v12_20261017-235608-66d00477.gd` (`34e017bf…`, unchanged).

**New runtime script (untracked):**
- `game/scripts/rpg-2-star-ocean-the-second_wdc-capitol-west_exploration-opt-in-selector_unapproved-v12r1_20261018-034933-23596520.gd` (`4f64abb5…`, 288 lines).

**v12 runtime layers (untracked):** the files are `game/assets/environments/candidates/wdc-cw-v12_20261017-235608-66d00477/rpg-2-star-ocean-the-second_wdc-capitol-west_<purpose>_unapproved-v12_20261017-235608-66d00477.png` plus a `.png.import` sidecar for each.

| purpose | PNG sha256 | `.import` |
|---|---|---|
| rt-base | `60474fce…` | `db409d78…` |
| rt-fg | `74cf02cd…` | `4f5880ba…` |
| rt-walk | `40feec73…` | `c4c23cc2…` |
| rt-ys-mast | `fb784e18…` | `2be6d272…` |
| rt-ys-tripod | `b341224c…` | `1db4c698…` |
| rt-ys-beacon | `a2d054d0…` | `89e8af8a…` |
| rt-ys-elm | `139cb258…` | `c8a038df…` |

**Test-only tools (outside `game/`, untracked):**
- `tools/rpg-2-star-ocean-the-second_wdc-capitol-west_real-scene-probe-harness_unapproved-v12r1_20261018-034933-23596520.gd` (`4f42090e…`)
- `tools/rpg-2-star-ocean-the-second_wdc-capitol-west_integration-fix-check_unapproved-v12r1_20261018-034933-23596520.py` (`294256da…`). It also reads the v12 `rt-contract`, the v12 `scene-flat-640x360` and the v12 outputs.
- `tools/rpg-2-star-ocean-the-second_wdc-capitol-west_real-scene-capture-probe-harness_unapproved-v12_20261017-235608-66d00477.gd` (`d0cab89b…`, unchanged; used for the v12 reproduction).

**Already tracked at HEAD (no overlay):** the approved v8 PNG and its `.import`, `battle_arena.gd`, `scifi_exploration_area.gd` and `survey_annex.gd`. The HEAD versions are the ones the clean replay ran on.

**Not required at runtime:** v12's `.pxo`/`.ora`/flat/manifest/palette/contract and its build-check tool, and v11's files. These are evidence and tool inputs only.

## Proposed selective integration plan (for root, not executed)

1. **Stage exactly:**
   - the `.tscn` one-line hunk (use a blob-level, index-only patch; the worktree file has no other hunk);
   - the v12 selector and the v12r1 selector;
   - the 7 v12 runtime PNGs and 7 sidecars;
   - the three tools above;
   - this QA note and the v12 QA note `…66d00477.md`;
   - the review captures. Either all of `outputs/wdc-cw-v12r1_…/` (21 PNG + 7 JSON), or at least `technical-check-report`, `clean-replay-run` and the zh/en entry, records-prompt, patrol-bypass, battle-return and v8ref PNGs, with the rest sha-pinned.
   - Optional: v12's `rt-contract` and `scene-flat` (the r1 checker reads them), and the v12 outputs dir for the byte-reproduction gate.
2. **Never stage:**
   - `scifi_exploration_area.gd`: its whole dirty diff is NYC v07 and Yonkers fixtures, not needed;
   - `battle_arena.gd` and `survey_annex.gd`;
   - progress, Bible and Site files;
   - other sessions' `.uid` files.
3. **Verify** with a throwaway `GIT_INDEX_FILE`. `checkout-index` into temp, run `--import`, then `python tools/…integration-fix-check…v12r1….py replay` from a clone. Expect PASS 50/50 after `main` + `analyze`, or run `replay` + `analyze` and accept the main-worktree gates as N/A.
4. **Revert:** point the `.tscn` back at the v12 selector, which keeps v12 opt-in, or at `res://scripts/scifi_exploration_area.gd`.
5. **Codex should look at these fresh captures** before any sync: patrol-bypass en, battle-return, v8ref and entry.

## Decisions recorded (made independently, no human input requested)

- The v12r1 selector is a subclass of the v12 selector rather than an edit to it, so v12 and its evidence stay byte-reproducible.
- The `.tscn` hook now names v12r1. The v12 flag alone still gives exact v12.
- The camera peak rate is 1.5 rather than v12's 2.0, with 20-row eases. The spawn moved 8 rows north so that the dome-at-entry rule still holds.
- Clipped glyphs are pinned instead of hidden, so a clue in interaction range never vanishes under the footer.
- I used a battle HP fixture and the real auto-mode input instead of scripted attack timing.
- The v8 reference was added 44 px east of the runtime heroine at the entry pose, at the same foot row and the same z.
