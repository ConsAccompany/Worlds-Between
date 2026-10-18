# Washington Capitol west — v12 actual-viewport integration (QA note, UNAPPROVED, opt-in only)

- **Date:** 2026-10-17/18 (stamp `20261017-235608`, run id `66d00477`, run dir `wdc-cw-v12_20261017-235608-66d00477`). Final check run 2026-10-18 00:16–00:17 EDT.
- **Author:** Claude (Claude Code, Opus 5.5). `claude auth status` at start: claude.ai, firstParty, subscription `max`. No API key, image model or paid fallback. No quota or auth stop.
- **Status:** one **UNAPPROVED technical integration candidate**, reachable only with `-- --wdc-capitol-west-v12`. The art is not accepted. Counters unchanged (scenes 3/12, sprites 0/52, timed plays 0/2).
- **Repo actions:** nothing staged, committed or pushed; Git index untouched. The ledger, Game Bible, progress files, map, Chicago, Yonkers, battle and every v11 file are untouched (v11 hashes re-verified by `check`).
- **Read:** the dispatch `…wdc-capitol-west-v12-real-viewport-integration-dispatch…819af3dc.md`, the v11 QA note, and v11's real 640×360 HUD entry/interact captures. There is no `AGENTS.md` in the repo; naming follows `~/.codex/AGENTS.md`.

## What is real game integration and what is test-only

**Real (runs in the actual game):**
- `game/scenes/scifi_exploration_area.tscn` now attaches the **v12 selector**. This one-line script path is the only shared-file edit.
- The selector `extends "res://scripts/scifi_exploration_area.gd"`.
  - **Without the flag:** every override calls `super()` straight away.
  - **With the flag, for `scifi.ruins` only:** it keeps the real HUD (`_build_ui`), input actions, markers (`_draw_field_marker`), labels, dialogue, saves, annex hand-off, battle hand-off and Esc/World-map exit.
  - **What it changes:** the plate (v11 layers), the ruins anchors, the walk mask, a `Camera2D`, and two candidate-only layout fixes (listed below).
- The captures come from the real flow:
  1. `AppState.select_destination("scifi.ruins")`;
  2. the world map's own `_enter_scene()` loads the real scene;
  3. movement uses `Input.action_press` on the real move actions;
  4. E and Esc go through `Input.parse_input_event`, so the scene's `_unhandled_input` handles them.

**Test-only:**
- The harness `tools/…real-scene-capture-probe-harness…gd` (a `-s` tool, not shipped).
- For the four review frames it places the heroine on the exact pose by assignment, after turning her with one frame of real input. The objective routes are walked with real input.
- The battle return is simulated by setting `returning_from_battle` / `enemy_cleared_for_return`, as `battle_arena.gd` does on victory. The battle itself is not played.
- **Placeholders that are still in the runtime (not new art):** the sentry is the baseline `_draw_enemy` pink box, and the clue markers are the baseline generic circles.

## How the viewport problem is solved (no squash, no rescale)

- The runtime HUD leaves rows **62..317** (256 rows). v11's composition needs 360 rows: statue top row 3, plaza feet rows 203..359.
- v12 keeps v11's 27 art layers **byte-identical**. The v12 flat equals v11's flat, sha `85ec56d9…`. A `Camera2D` (fixed top-left) puts world row `scroll` at screen row 62:
  - `scroll = clamp(max(2·(feet − 250), feet + 3 − 255), 0, 104)`.
- **Dome zone:** while the feet are at row 250 or above, scroll is 0. The whole dome and statue (rows 3–110 → screen 65–172) and the whole 48-row heroine canvas (feet−44..feet+3) are in the play band.
- **Further south:** the camera scrolls 2 px per px of walking, so the player sees up to 52 rows ahead instead of walking along the footer.
- **Safe band:** the v12 walk mask is v11's mask clipped to feet x 16..623 and y ≤ 356 (61,260 of 62,687 texels). At any walkable foot the 32×48 canvas stays inside x 0..639 and rows 62..317.
- **Review poses** (all at scroll 0, dome fully visible):
  - entry/spawn (372,246), facing south;
  - vista (408,240), facing north;
  - interaction (334,238), facing west at the records glyph;
  - occlusion (196,246), behind the survey mast, facing north.
- **Runtime clues placed on v11 fixtures** (my implementation decision):

  | clue | v11 fixture | position |
  |---|---|---|
  | survey entrance → annex | north steps (also the v11 north exit) | (372,192) |
  | records (记录台) | Olmsted plaque on the left stair pier | (302,214) |
  | Ji Cheng | west of that pier | (268,243) |
  | trace 1 | west seat-wall seam | (150,232) |
  | trace 2 | fallen Olmsted lantern | (464,240) |
  | strata panel (assist) | near-pile toe | (548,264) |
  | sentry | east patrol path near the beacon | (566,320) |
  | bypass zone | east exit lane | x 606–623, y 278–340 |

  Interaction radii and order are the inherited ones.
- **Candidate-only layout fixes:**
  - The hint line drops to the largest size from 11 to 9 px that ends left of Save. The en hint fits at 10 px (385 of 392 px); zh stays 11.
  - `records_label` and `enemy_label` get the dark outline the base already gives the other world labels. Without it, cream "Records" text vanished on v11's pale lawn.
  - Baseline UI otherwise unchanged.

## Results: `check --write-report` → **PASS 72/72** (technical gates, not art acceptance)

- **Lock/package (2):** the v11 files plus v11 tool sha-text `e8c85dc2…` are unchanged, and the files on disk equal a fresh rebuild.
- **Static (25):**
  - art layers identical to v11; new guides layer uses only the guide palette; binary alpha;
  - runtime layers re-stack exactly to the flat;
  - walk mask ⊆ v11 and inside the safe band; every walkable foot keeps the canvas in rows 62..317;
  - review poses are walkable at scroll 0 with the dome and canvas in view;
  - each flow target triggers exactly its intended interaction; entry, vista and occlusion don't open the annex;
  - routes exist for all targets, and the bypass is possible without an encounter;
  - selector constants equal the package and the v11 Y-sort pivots;
  - nothing is drawn in front of the heroine at entry, vista or interaction, or in front of Ji. The occlusion pose has 155 mast texels in front;
  - objective glyphs are in the play band at their poses;
  - the sentry is 100 % in view when the encounter triggers (feet (564,298), scroll 96).
- **Pixelorama 1.2.3 headless (8):**
  - `.pxo` and `.ora` flats are exact; both split exports give 27 exact art layers, and the hidden guides are not exported;
  - **the six runtime PNGs rebuilt from Pixelorama's own `.pxo` split exports equal the shipped ones**;
  - sources unchanged;
  - isolation held. Each run used a temp `APPDATA`. The real `%APPDATA%\pixelorama` changed only `.running`, the heartbeat of another session's open GUI (PID 37584, not touched).
- **Godot 4.7.2, real scene, windowed at 640×360 (37):**
  - **Captures (14):**
    - 12 captures, all 640×360;
    - review frames at scroll 0;
    - **the dome box is pixel-exact in all 8 zh/en review frames**;
    - **the heroine is 100 % visible** at entry, vista and interaction. At the occlusion pose 81.3 % is visible, and every hidden texel shows a mast pixel;
    - Ji is 100 % visible;
    - **play-band pixels outside markers, labels and actors equal the art exactly (0 mismatches in all 12)**;
    - the HUD bars are present;
    - title and hint end left of Save in both languages;
    - no overlapping labels in the play band;
    - the records glyph is drawn and unobstructed at the prompt frame;
    - the patrol frame is scrolled (104) with the heroine fully visible.
  - **Flow (23):**
    - entered via the world map with v12 active at the spawn;
    - every route was walked with real input;
    - records checked → Ji recruited through her dialogue and the Invite button → both traces recorded → strata-panel assist completed;
    - patrol bypassed (feedback `bypass_notice`, no battle);
    - W/S/E edge zones reached;
    - survey entrance → real `survey_annex.tscn` → Esc → back at (371,213), v12 active;
    - walking into the sentry → `battle_arena.tscn` (enemy `sentry`); the return position (534,290) is walkable and 44.2 px from the sentry; the return restores v12 with the patrol cleared;
    - Esc → world map;
    - every frame of the 882 flow frames and 555 sweep frames was walkable, with the canvas inside rows 62..317 (worst bottom 317) and columns 0..637;
    - 10 collision sweeps into the terrace, seat wall, pile, elm, survey kit, tripod, beacon and the three edges all ended walkable;
    - the runtime mask equals the PNG at all 230,400 texels;
    - the camera is current and the layers use nearest filtering;
    - the command-line flag enables v12.
  - **Default behaviour unchanged:**
    - with the flag off, the selector equals the base script at entry and after input (image bytes, positions, texts and state) for `scifi.city`, `scifi.outskirts` and `scifi.ruins`;
    - the existing headless smokes `m4_smoke`, `m6_smoke`, `m7_smoke` and `m8_city_reentry_smoke` pass with the selector attached.
- **Side effects:** the Godot runs created no `.uid` or `.import` files (git status diffed before and after). Harness saves go only to `user://test-saves/wdc-cw-v12`; I did not separately audit the real user save folder.

## Limitations (honest)

1. **No new raster art and no recomposition.** v12 is v11's art plus a camera. The dome is fully visible only while scroll ≤ 3 (feet ≤ 251). Further south it scrolls out by design.
2. **Camera feel:** from feet row 250 to 302 the camera scrolls at twice walking speed, so the heroine drifts up the screen while walking south. There is no smoothing. A creator/feel review is still needed.
3. **Known layout defects, still present** (the same ones Codex listed in the later follow-up dispatch `…wdc-v12-review-capture-and-selective-sync-prep…c36d289f.md`, which a separate stream will handle):
   - At scroll 0 the far strata-panel glyph peeks about 6 rows above the footer.
   - In the scrolled patrol view the wide "Automated machine" label (drawn above everything, as in the base) runs into the bypass glyph at the right edge.
   - My label gate checks label-vs-label only, not label-vs-glyph.
4. **Placeholder content:** the runtime sentry is still the baseline pink-box placeholder, and the markers are the baseline generic circles drawn over the art.
5. **Hero sprite:** the captures show the runtime native m8 prototype heroine (32×48 canvas, about 42 px opaque). That is not v11's Pixelorama v8 pilot, and no runtime hero asset was changed.
6. **Edge exits:** W/E/S are walk-contract zones with no runtime destination. N is mapped to the real survey entrance.
7. **Dirty base script:** validated in the shared worktree. The base `scifi_exploration_area.gd` there carries other sessions' uncommitted edits (Yonkers fixtures, NYC selection), so no clean-clone or HEAD-only validation was done.
8. **No Pixelorama GUI work:** no GUI open/save/paint. The `.pxo` is written by Python and verified by headless export.
9. **No 1280×720 capture set** this time; only the native 640×360 set.
10. **To revert:** point the `.tscn` script path back at `res://scripts/scifi_exploration_area.gd`. The candidate files can stay or be deleted.

## Exact file list (all new, untracked, except the one modified scene line)

**Modified:**
- `game/scenes/scifi_exploration_area.tscn`: one line, the script path → selector. sha-text `9ccf7164…`.

**Runtime script:**
- `game/scripts/rpg-2-star-ocean-the-second_wdc-capitol-west_exploration-opt-in-selector_unapproved-v12_20261017-235608-66d00477.gd` (328 lines, sha-text `34e017bf…`).

**Tools:**
- `tools/rpg-2-star-ocean-the-second_wdc-capitol-west_viewport-integration_build-check_unapproved-v12_20261017-235608-66d00477.py` (1,022 lines, sha-text `b5cf9a7e…`; modes `build` | `check [--write-report] [--no-smokes]` | `static`).
- `tools/rpg-2-star-ocean-the-second_wdc-capitol-west_real-scene-capture-probe-harness_unapproved-v12_20261017-235608-66d00477.gd` (475 lines, sha-text `d0cab89b…`).

**Candidate dir:** `game/assets/environments/candidates/wdc-cw-v12_20261017-235608-66d00477/`. Each file is `rpg-2-star-ocean-the-second_wdc-capitol-west_<purpose>_unapproved-v12_20261017-235608-66d00477.<ext>`; sha256 of bytes:

| purpose | sha256 | purpose | sha256 |
|---|---|---|---|
| `scene-28layer.pxo` | `c1be47e0…` | `rt-base.png` | `60474fce…` |
| `scene-28layer.ora` | `e8fc4d64…` | `rt-fg.png` | `74cf02cd…` |
| `scene-flat-640x360.png` (= v11) | `85ec56d9…` | `rt-walk.png` | `40feec73…` |
| `scene-palette.gpl` | `c2537445…` | `rt-ys-mast.png` | `fb784e18…` |
| `scene-manifest.json` | `7ae68c7c…` | `rt-ys-tripod.png` | `b341224c…` |
| `rt-contract.json` | `5fa545a5…` | `rt-ys-beacon.png` | `a2d054d0…` |
| | | `rt-ys-elm.png` | `139cb258…` |

**Outputs:** `outputs/wdc-cw-v12_20261017-235608-66d00477/`, same naming, real 640×360 captures:

| lang | entry | vista | interact-prompt | interact | occlusion | patrol-scrolled (extra) |
|---|---|---|---|---|---|---|
| zh | `40c11036…` | `43ad1f84…` | `9e564690…` | `be5ac590…` | `f6a1093f…` | `0e536425…` |
| en | `528e4097…` | `5c3d4b01…` | `fe452209…` | `bfa2411c…` | `7b75e4ac…` | `0fad1329…` |

Each capture is `rt640-<lang>-<view>`. `technical-check-report.json` is `9eedd93c…`.

**Docs:** this note.
