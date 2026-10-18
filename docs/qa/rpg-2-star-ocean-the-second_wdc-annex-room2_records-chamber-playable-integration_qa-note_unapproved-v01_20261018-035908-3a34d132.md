# Washington survey annex room 2 (记录内室 / Records Chamber): records-chamber v01 playable integration

**Status: UNAPPROVED technical candidate. Off by default. Nothing staged, committed or pushed. Counters unchanged.**
Accepted environments stay **3/12**. Full sprites stay 0/52, human plays 0/2, and all meters stay 40.8%. No creator decision was requested.

- Stream: Claude Code, signed-in Claude Max (claude.ai / firstParty, `ANTHROPIC_API_KEY` absent). Resumed 2026-10-18 after the 03:40 EDT quota reset.
- Base: local HEAD `c20118d` with pre-existing dirty files. Upstream main is `7370739`; `survey_annex.gd` is the same blob in both (`eecdcca`).
- Evidence run: 2026-10-18 04:02:48–04:03:25 EDT, Godot 4.7.2 (`work/tooling/godot-4-7-2/Godot_v4.7.2-stable_win64_console.exe`), windowed, real game scene `res://scenes/survey_annex.tscn`.

## What this is

Room 2 of the `scifi.ruins` survey annex can now be played with the four native pixel fixtures already authored in `outputs/wdc-rc2-v01_151fb8d0/` (runtime copies in `game/assets/props/wdc-annex-room2/`). It is opt-in only: `-- --wdc-records-chamber-v01`.

| Fixture | Clue / interaction |
|---|---|
| Machine-translation stone and field translator | `scifi.ruins:3` |
| Parallel-inscription basalt tablet | `scifi.ruins:4` |
| Erased-heading bronze plaque | `scifi.ruins:5` |
| Analysis light table | Existing research terminal (320, 263) |

The room background is still the existing m8-concept plate; it was not touched.

**Clue text is unchanged.** `game/scripts/survey_content.gd` is byte-identical to HEAD (gate S4). The Godot check compares every overlay title and body with `survey_content.gd` in zh and en.

- The machine translation keeps its low-confidence "offering" and its unnamed recipient.
- The parallel inscription keeps "closer to 'transfer'" and "may describe different processes".
- The erased heading keeps "cannot restore its wording".
- The terminal keeps "keep original codes and mark uncertainty" as the answer.

**No heading text was invented.** The plaque shows only scraped stroke stubs, and all glyph marks are abstract 3x3 cells, not characters of any script.

## Bounded changes in this session

All runtime changes sit in `game/scripts/survey_annex.gd` and take effect only when `wdc_room_two` is true, i.e. ruins room 2 launched with the flag. Without the flag, rooms 1 and 2 are pixel-identical to HEAD (gate D1).

1. **English title.** The title ended at x 497, under Save (x 418). Room 2 now uses the existing 14 px English-title rule, so it ends at x 391. Chinese is unchanged: 18 px, ending at x 317.
2. **Clue discs.** They are drawn 19 px higher (`WDC_ROOM_TWO_MARKER_LIFT`), above the fixture tops. Before, they covered the top rows of the erased-heading band and the tablet's upper register. Inspection still uses the unchanged `CLUE_POSITIONS` radius plus the inspect rects.
3. **Clue names.** Each is one line, 140 px wide, above its disc. Before, the English names wrapped onto the discs.
4. **Terminal label.** It sits beside its disc at (340, 255). Before, it sat on the parallel-inscription plinth.
5. **Feet blockers.** Twelve new blockers follow the plate's stepped back corners, side walls and near-corner rubble. Before, the heroine could walk into the walls. The exit marker, the spawn and the full-width lane walk (to x 602.7) stay clear.

**Check-tool fixes** (`tools/…wdc-annex-room2_godot-capture-and-check_unapproved-v01_20261018-001157-151fb8d0.gd`):

- **Key events.** Synthetic keys now carry both `keycode` and `physical_keycode`, as a real keyboard does. The game's actions bind physical keys but `ui_cancel` binds `keycode`, so the old physical-only Esc never closed the overlay. That was a harness bug, not a game bug.
- **False-positive list.** The spawn point was removed: it lies inside the exit radius, so pressing E there correctly leaves the room.
- **Occlusion shots.** They now place the heroine where her head shows above the fixture and her body is hidden. The old position hid her completely.
- **New coverage:**
  - a label-layout gate;
  - six wall/rubble collision cases;
  - door-entry and return captures;
  - save and load through the real UI (mouse clicks on the room's Save button, slot 1 Save, Back, then title menu Load, slot 1 Load and auto row 1 Load);
  - a `--default-off-parity` mode that loads the HEAD script in memory onto the same scene.

**New check:** `tools/rpg-2-star-ocean-the-second_wdc-annex-room2_pixel-source-pixelorama-check_unapproved-v01_20261018-035908-3a34d132.py`. Its Pixelorama gates fail if the executable is missing; they never skip.

## Commands and results (all fresh, isolated)

Each Godot run used its own empty `APPDATA` under `%LOCALAPPDATA%\Temp\rc2-final\`, so `user://`, test saves and caches stayed out of the real profile.

- No `--import` was run: the four runtime PNGs' import cache was already current (source MD5 = imported MD5).
- `git status` before and after differs only by this session's new files and other streams' concurrent files (WDC v12r1, Yonkers v04). No `.uid` or `.import` side effects.

| # | Command (from repo root) | Result |
|---|---|---|
| 1 | `APPDATA=<tmp1> Godot --path game -s <abs>/tools/…room2_godot-capture-and-check…151fb8d0.gd -- <O>/cap <O>/probe 20261018-035908-3a34d132 --wdc-records-chamber-v01` | exit 0, `WDC_R2_V01_ALL_OK`, no `SCRIPT ERROR`, 33 captures |
| 2 | `APPDATA=<tmp2> Godot --path game -s <same tool> -- <O>/parity <O>/pprobe <stamp> <tmp>/head-survey_annex.gd --default-off-parity` (HEAD copy from `git show HEAD:game/scripts/survey_annex.gd`) | exit 0, `WDC_R2_V01_DEFAULT_OFF_PARITY_OK` with room 1 zh/en and room 2 zh/en all at 0 px; no records-chamber nodes without the flag |
| 3 | `APPDATA=<tmp3> Godot --path game -s <abs>/tools/…wdc-annex-room1_v02-review-gate-accepted-rooms-replay_check-v01_20261017-172907-03286bf3.gd -- <O>/replay <stamp>` | exit 0, `ACCEPTED_REPLAY_ALL_OK`, interactions 3+3+3 |
| 4 | `python -I tools/…room2_pixel-source-pixelorama-check…3a34d132.py --captures <O>/cap --probes <O>/probe --parity <O>/parity --replay <O>/replay --report … --deps …` | exit 0, **GATES 16/16 PASS** |
| 5 | Pixel comparison of the 33 final captures against an earlier identical run (run3) | 33/33 identical |

`<O>` = `outputs/wdc-rc2-v01i_3a34d132`. Python is the real runtime at `C:\Users\hkzha\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe`.

### What test 1 proves (real key input through `Input`, the InputMap and the viewport)

**Clues.** For each of the three clues, the heroine walks from the lane with held WASD keys until the fixture base stops her (y 226.0–227.2), then presses E.

- The overlay opens with the exact `survey_content.gd` title and body in zh and en, and Esc closes it.
- Each clue also opens from behind, from both sides and from the front (3×4 positions).
- Six lane and side spots open nothing.

**Terminal.** She walks down until the table's blocker stops her (y 271.5) and presses E.

- With fewer than six clues, the locked message opens.
- With six clues, the link mode opens.
- Once the survey is solved, the disc recolours.

**Collision.** 18 held-key cases pass:

- fixture fronts, back and sides;
- the back wall;
- the table from the north, west and east;
- the near-edge clamp;
- the west and east walls and back corners;
- the near-corner rubble.

A diagonal input slides along a fixture, and a start inside a blocker can walk out (older saves).

**Reachability.** A 1 px flood fill (96,222 cells) reaches the exit, the terminal, the save spot, and the front and back of every clue.

**Save/load (real UI clicks).**

1. Inspecting a clue writes an auto save.
2. Clicking the room's Save button, then slot 1 "Save here", writes the manual save. Back resumes the room at (410, 262) with the fixtures.
3. In a fresh run, title menu Load → slot 1 Load restores Washington room 2, the fixtures, position (410, 262), clues 1/6 and language en.
4. Auto row 1 Load restores room 2 at (163, 232).

The test saves were deleted afterwards.

**Transitions.**

- Room 1 "Go deeper" (E) opens room 2 with the fixtures at the spawn point.
- Esc returns to room 1 at (555, 257), which is unblocked.
- Room 2's exit marker (E) also returns to room 1.

**Labels.** No clue name, disc, terminal label or fixture overlaps another, in zh or en. The English title ends 27 px before Save.

### Gates in test 4

- **S1:** all four assets' PNG, `.ora` and `.pxo` hashes match the manifest. A rebuild from the author tool is byte-identical, and the layers decode exactly.
- **S2:** the only semi-transparent texels are the contact shadows.
- **S3:** the runtime constants equal the manifest's placements, blockers and preloads, and the flag gate is present.
- **S4:** the background hash and the clue text are unchanged.
- **G1:** the Godot results file reports ok.
- **C1:** the full bilingual 640×360 set exists, plus both return captures.
- **C2:** in all 16 hero-hidden frames, all 9,869 opaque fixture texels render exactly 1:1. Table texels inside the terminal disc (radius 17 around (320, 263)) are excluded, because the disc is drawn over them.
- **C3:** only pixels inside the heroine's box change.
- **C4:** in front of a fixture, the heroine draws over it (>100 px on her own fixture).
- **C5:** behind a fixture, the fixture covers her. 0 hero pixels are on its opaque texels, every covering texel is exact, and her head stays visible.
- **C6:** she never overlaps the table.
- **D1:** default-off is pixel-identical to HEAD.
- **D2:** the accepted rooms are pixel-identical to the exact images cited in their acceptance records, 8/8 at 0 px:
  - NYC room 1 zh/en, `d3590c0a`;
  - NYC room 2 zh/en/approach/interaction, `6b3138d8`;
  - Yonkers room 2 zh/en, `94cebca4`.
- **P1–P3:** the real Pixelorama 1.2.3 CLI (headless, temporary APPDATA) round-trips the files:
  - P1: `--split-layers` reproduces every layer of all 8 `.pxo`/`.ora` files exactly;
  - P2: the flat exports are exact (0 differing texels, max delta 0);
  - P3: the real Pixelorama APPDATA is unchanged.

## Native editor scope: CLI versus Save As

Only the native Pixelorama **CLI** was exercised: load, plus `--export` and `--split-layers`. A **GUI Save As → close → reopen** of these `.pxo` files was NOT performed and remains pending. These `.pxo` files are written by the author tool in `pxo_version 7` form; Pixelorama has loaded and exported them but never saved one.

## Evidence (all new, uniquely named, untracked)

- QA note: this file.
- Captures: `outputs/wdc-rc2-v01i_3a34d132/cap/` holds 33 native 640×360 images, all named `rpg-2-star-ocean-the-second_wdc-annex-room2_v01-godot-<zh|en>-<label>-640x360_20261018-035908-3a34d132.png`:

  | Labels | Languages |
  |---|---|
  | `entry`, `door-entry-from-room1` | zh + en |
  | `front-clue-3/4/5`, `occlusion-behind-clue-3/4/5` | zh + en |
  | `interaction-clue-3/4/5`, `interaction-terminal-locked` | zh + en |
  | `terminal-approach` | zh + en |
  | `after-load` | zh + en |
  | `terminal-solved-marker` | zh |
  | `return-room1-via-esc` | zh |
  | `return-room1-via-exit-marker` | en |
  | `save-screen-slot1` | en |
  | `front-clue-4-runtime-hero` (runtime heroine sprite, no capture-only dressing) | zh |

- Other evidence in `outputs/wdc-rc2-v01i_3a34d132/`:
  - `probe/`: hero-hidden frames and `godot-check-results.json`;
  - `parity/`: 8 default-off frames (working tree and HEAD);
  - `replay/`: 8 accepted-room frames;
  - `logs/`: the 3 Godot logs and the Python log.
- Report: `outputs/wdc-rc2-v01i_3a34d132/rpg-2-star-ocean-the-second_wdc-annex-room2_v01-integration-check-report_20261018-035908-3a34d132.json`.
- Dependency manifest: `outputs/wdc-rc2-v01i_3a34d132/rpg-2-star-ocean-the-second_wdc-annex-room2_v01-selected-dependency-manifest_20261018-035908-3a34d132.json`. It has 30 entries with hash algorithm and git state. `survey_annex.gd` is the only modified tracked file; the scene, the clue text, the background and the hero reference are tracked and unchanged; everything else is untracked.
- Exact script diff: `outputs/wdc-rc2-v01i_3a34d132/rpg-2-star-ocean-the-second_wdc-annex-room2_v01-survey-annex-gd-working-tree-diff_20261018-035908-3a34d132.patch` (105+/13−). The whole working-tree diff of `survey_annex.gd` is this room-2 branch: the batch-0340 snapshot plus this session's bounded fixes.

## Remaining limitations (honest)

1. **Style seam.** Same class as room 1 v02: crisp hand-pixel fixtures sit on a softened, generated m8-concept plate drawn with linear filtering. The plate was not repainted (out of scope).
2. **Capture-only heroine.** Most captures dress her as the approved selout v8 idle at 48 px, as room 1 v02 did. The runtime sprite that actually ships is smaller; see `zh-front-clue-4-runtime-hero`.
3. **Default room 2 is left as it was.** Without the flag it keeps its pre-existing English title under Save and its walk-through walls, by design (0 px parity).
4. **Room 1 Back button.** In English, room 1's "Return outside" overflows its 98 px button. This is pre-existing room 1 v02 behaviour, visible in `en-return-room1-via-exit-marker`, and outside this scope.
5. **Disc lift.** The discs are drawn 19 px above the logical clue sites. Interaction areas are unchanged and verified, but the creator may prefer another disc placement.
6. **Pixelorama GUI.** GUI Save As/reopen is pending (see above). There is no human play and no creator visual acceptance.

## Task-closeout proposal (for root; not a receipt)

- **Task:** Washington survey annex room 2 records-chamber v01 playable integration (opt-in, UNAPPROVED).
- **Evidence:** this note, the 16/16 report, the dependency manifest and the diff patch above.
- **Meter effect: zero.** Accepted environments stay 3/12. M2, sprites, plays, formal acceptance and all six meters (40.8%) are unchanged. The work stays technical-only until a human accepts the art.
- **Selective sync (root):**
  - Stage exactly the files the dependency manifest marks untracked or modified.
  - Treat `survey_annex.gd` as a whole-file room-2-only diff.
  - Optionally add the capture set and the report. `probe/`, `parity/` and `replay/` are verification bytes and can stay local, hash-pinned by the report.
  - Never stage the whole tree.

## Addendum 2026-10-18 (integration onto main): default-off parity expectation r1

The text above is kept as the record of the 03:59–04:03 run. Since then, the default layout and collision fix (`…default-layout-collision-fix_qa-note_unapproved-v01_20261018-041322-c3ff819c.md`) has changed the Washington English header on purpose:
- the room-2 title rule;
- the Back-button font fit.

So the 0 px default-off expectation for English is superseded.

**r1 rules.** The Godot `--default-off-parity` mode and the Python gate (renamed `D1_default_off_zh_identical_en_header_only`) now require:
- zh frames identical to HEAD;
- en frames changed only in the 62-row header.

**Re-run against main `7553581` with the combined script:**
- parity OK: room 1 zh 0, room 2 zh 0, room 1 en 1377, room 2 en 4965, all in the header;
- `WDC_R2_V01_ALL_OK`;
- accepted rooms 8/8 at 0 px;
- **GATES 16/16**.

**Captures.** The 15 opt-in English captures in `cap/` above predate the font fit. A fresh run differs from them only in the Back-button box (x 529–624, y 12–49). The 18 zh captures are byte-identical.
