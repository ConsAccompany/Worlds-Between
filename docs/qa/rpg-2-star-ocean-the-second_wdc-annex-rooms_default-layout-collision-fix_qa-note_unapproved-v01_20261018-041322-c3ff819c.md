# Washington survey annex rooms 1–2: default layout and collision fix

**Status: UNAPPROVED technical bug fix. Nothing staged, committed or pushed. Counters unchanged.**
Accepted environments stay **3/12**, full sprites 0/52, human plays 0/2, all meters 40.8%. No art was changed and no human art acceptance is claimed or requested.

- Stream: Claude Code, signed-in Claude Max (firstParty; `ANTHROPIC_API_KEY` absent). No quota or auth stop was hit.
- Base: upstream `origin/main` `7370739`. Local HEAD is `c20118d`; `survey_annex.gd` is the same blob in both (`eecdcca`).
- Follows the room-2 integration QA note `…records-chamber-playable-integration_qa-note_unapproved-v01_20261018-035908-3a34d132.md`. That note and its evidence are kept unmodified.
- Run: 2026-10-18 ~04:15–04:30 EDT, Godot 4.7.2 windowed, real scene `res://scenes/survey_annex.tscn`, with an isolated `APPDATA` per run under `%LOCALAPPDATA%\Temp\wdcfix-c3ff819c\`.

## What was fixed

This fixes the three baseline bugs disclosed by the room-2 integration report, plus one more of the same kind that the new bound check found. All changes are in `game/scripts/survey_annex.gd`. They apply only to `scifi.ruins` (Washington), rooms 1 and 2, with and without `--wdc-records-chamber-v01`.

| # | Bug at HEAD (default build) | Fix |
|---|---|---|
| 1 | Room 2's English title, "Washington, D.C. ruins · U.S. Capitol · Records Chamber", ends at x 497, under Save (x 418). | The existing 14 px English-title rule now covers both Washington rooms. The title ends at x 391. Chinese is unchanged: 18 px, ending at x 317. |
| 2 | In room 2, the heroine's feet walk through the plate's side walls, stepped back corners, back wall and near-corner rubble. Only the room clamp (x 25–615, y 78–305) stopped her. | The existing room-2 wall blockers (the back wall plus the 12 stepped-corner, side-wall and rubble rects already in `WDC_ROOM_TWO_BLOCKERS`) now block in default room 2 too, through the existing `_slide`. The three fixture-base blockers and the table blocker (indices 1–4) stay opt-in only, because those fixtures are drawn only with the flag. |
| 3 | Room 1's English "Return outside" needs 123 px, so the 98 px Back button grew to 123 px and ran off the screen edge. | For Washington rooms only, a label that does not fit steps its font size down until it fits. "Return outside" fits at 12 px (95 px wide). The button stays at 98×38. Labels that already fit keep the default 16 px, so every Chinese label is unchanged. |
| 3b | **Found by the new check:** room 2's English "Outer room" needs 100 px, so its button grew to 100 px. | The same rule applies: 15 px, 94 px wide. |

No new physics framework, no global UI redesign, no new blocker geometry. The NYC and Yonkers code paths are untouched, including Yonkers room 1's own wide-button rule.

**Unchanged:**

- clue text and clue positions;
- inspect radius and rects;
- spawn, exit, terminal, and the room-1 return spot (555, 257);
- the save and autosave format;
- all art and art flags;
- opt-in room-2 behaviour, apart from the shared title and button rule.

Fix-only change against the room-2 integration snapshot: +21/−6 in 7 hunks (`…fix-only-incremental-diff-vs-room2-v01-integration…patch`).

## Intentional default screenshot changes relative to HEAD (disclosed)

The old room-2 v01 `--default-off-parity` gate (0 px versus HEAD) **can no longer pass, by design**. It was rerun and fails at its first English frame: `default room 1 en differs from HEAD in 1377 px` (log `godot-v01-parity-rerun-expected-fail.log`). The new check replaces that assertion with these rules:

| Default frame | Pixels changed vs HEAD | Where |
|---|---|---|
| room 1 zh | 0 | none |
| room 1 en | 1,377 | bbox x 530–639, y 12–49 (Back button only) |
| room 2 zh | 0 | none |
| room 2 en | 4,965 | bbox x 18–624, y 10–49 (header only: title and Back button) |

With the flag, room 1 shows the same result: zh 0 px, en 1,377 px in the Back button. Nothing below the 62 px header changes in any static frame. Collision changes only how she moves.

## Before → after evidence (actual Godot 640×360, runtime heroine, real held keys)

**Header bounds.** The check asserts the title's right edge ≤ Save − 4, both buttons at exactly 98×38, the text's minimum width ≤ 98, both buttons inside x 640, and no overlap between Save and Back.

| Frame | HEAD | After |
|---|---|---|
| room 1 en | Back 123 px wide, off-screen | Back 98 px, text 95 px at 12 px |
| room 2 en | title ends at 497 (under Save); Back 100 px | title ends at 391; Back 98 px, text 94 px at 15 px |
| zh frames | already within bounds | identical |

**Wall collision**, default room 2. Each case holds WASD from a start position until she stops.

| Case | HEAD stop | After stop |
|---|---|---|
| west wall | (25, 220), inside wall | (34.0, 220) |
| east wall | (615, 220), inside wall | (599.1, 220) |
| back wall | (240, 78), inside wall | (240, 116.0) |
| west back corner (W+A) | (25, 78), inside wall | (57.2, 145.6) |
| east back corner (W+D) | (615, 78), inside wall | (587.7, 162.1) |
| west rubble | (25, 295), inside wall | (49.7, 295) |
| east rubble | (615, 295), inside wall | (602.0, 295) |

At HEAD, 7 of 7 cases end inside a wall. After the fix, 7 of 7 stop outside every blocker, and one more 3 px step would be blocked. Opt-in room 2 gives the same 7 of 7.

**Reachability.** A 1 px flood fill from the spawn reaches the exit, the terminal and clues 3, 4 and 5. The room-1 return spot is clear.

- Default room 2: 103,844 cells.
- Opt-in room 2: 96,222 cells, identical to the v01 integration report.

**Real interactions, default room 2.** For each clue she walks up with W, presses E, and the clue opens with the exact `survey_content.gd` title and body in zh and en. Esc closes it. The terminal opens the locked message. The exit marker (E) returns to room 1 at (555, 257).

**Saves.** Each run used its own isolated `user://`. The test saves were deleted afterwards (`test_saves_removed: true`). No `.uid`, `.import` or tracked-file side effects: the `git status` of tracked files is identical before and after.

## Commands and results (all fresh)

| # | Command (repo root; `G` = `work/tooling/godot-4-7-2/Godot_v4.7.2-stable_win64_console.exe`, `O` = `outputs/wdc-rooms-fix_c3ff819c`, HEAD copy = `git show origin/main:game/scripts/survey_annex.gd`) | Result |
|---|---|---|
| 1 | `APPDATA=<tmp/a1> G --path game -s <abs>/tools/…default-layout-collision-fix_godot-check…c3ff819c.gd -- <O>/cap <O>/probe <stamp> <HEAD copy>` | exit 0, `WDC_ROOMS_FIX_DEFAULT_ALL_OK` |
| 2 | same, plus `--wdc-records-chamber-v01` (APPDATA a2) | exit 0, `WDC_ROOMS_FIX_OPTIN_ALL_OK` |
| 3 | room-2 v01 check, opt-in, unmodified (APPDATA a3) → `<O>/v01-rerun` | exit 0, `WDC_R2_V01_ALL_OK` (opt-in interactions, occlusion, save/load UI, transitions still pass) |
| 4 | accepted-rooms replay tool `…03286bf3.gd` (APPDATA a4) → `<O>/replay` | exit 0, `ACCEPTED_REPLAY_ALL_OK`, interactions 3+3+3 |
| 5 | room-2 v01 `--default-off-parity` (APPDATA a5) | exit 1 **as expected**: room 1 en 1,377 px (disclosed above) |
| 6 | `python -I tools/…default-layout-collision-fix_evidence-check…c3ff819c.py --out <O>` | exit 0, **GATES 12/12** |

**Gates in run 6:**

- G1–G3: the three Godot results files report ok.
- H1: header bounds hold in every frame after the fix.
- H2: the HEAD header bugs reproduce.
- W1: the walls stop her after the fix.
- W2: at HEAD she walks through the walls in 7 of 7 cases.
- R1: clues, terminal and exit are reachable.
- P1: the zh frames match HEAD exactly.
- P2: the en changes stay inside the header.
- D2: the accepted rooms are 0 px against their acceptance-record images in 8 of 8 frames:
  - NYC room 1 zh/en, `d3590c0a`;
  - NYC room 2 zh/en/approach/interaction, `6b3138d8`;
  - Yonkers room 2 zh/en, `94cebca4`.
- S1: these files are byte-equal (text compared LF-normalised) to `7370739`:
  - `survey_content.gd`;
  - `survey_annex.tscn`;
  - `app_state.gd`;
  - the room-2 plate;
  - the room-1 v02 plate.

## Evidence (new, uniquely named, untracked)

- **This note.**
- **Tools:**
  - `tools/rpg-2-star-ocean-the-second_wdc-annex-rooms_default-layout-collision-fix_godot-check_unapproved-v01_20261018-041322-c3ff819c.gd`
  - `tools/rpg-2-star-ocean-the-second_wdc-annex-rooms_default-layout-collision-fix_evidence-check_unapproved-v01_20261018-041322-c3ff819c.py`
- **`outputs/wdc-rooms-fix_c3ff819c/`:**
  - `cap/`: 33 captures named `…_fix-<default|optin>-<before|after>-godot-<zh|en>-<label>-640x360_20261018-041322-c3ff819c.png`. They cover:
    - room 1 and room 2 entry, before and after;
    - room 2 west-wall and east-rubble stops, before and after;
    - default room 2 clue 3/4/5 interactions, zh and en;
    - room 1 after the exit.
  - `probe/`: the two results JSONs.
  - `v01-rerun/`, `v01-parity-rerun/`, `replay/`: verification frames.
  - `logs/`: 5 Godot logs and the Python log.
  - Report: `rpg-2-star-ocean-the-second_wdc-annex-rooms_fix-check-report_20261018-041322-c3ff819c.json`.
  - Dependency manifest: `rpg-2-star-ocean-the-second_wdc-annex-rooms_fix-dependency-manifest_20261018-041322-c3ff819c.json`. It has 116 entries with hash algorithm (`sha256-text-lf-v1` for text, `sha256-bytes` for binaries) and git state. `survey_annex.gd` is the only modified tracked file.
  - Patches:
    - `…survey-annex-gd-full-diff-vs-origin-main-7370739…patch` (120+/13−): the room-2 integration plus this fix, as one whole-file diff.
    - `…fix-only-incremental-diff-vs-room2-v01-integration…patch`: this fix alone.

## Remaining limits (honest)

1. **Art untouched, still UNAPPROVED.**
   - Room 2's opt-in native fixtures stay crisper than the soft, linearly filtered m8-concept plate.
   - Room 1 v02 is still an unaccepted candidate.
   - Nothing was repainted.
2. **Default room 2 still uses old marker and label placement.** Without the flag, the English clue names "Machine Translation" and "Parallel Inscription" wrap onto their discs. This is pre-existing, outside this bounded fix, and visible in `default-after-…-room2-entry`. The opt-in branch already solves it.
3. **Feet-only blockers.** The wall blockers stop her feet, so at the west wall (x 34) part of the runtime sprite still overlaps the wall art by a few pixels. The blocker geometry is the existing v01 geometry and was not retuned.
4. **Mixed button font sizes.** In English the Back button now uses a smaller font (12 px in room 1, 15 px in room 2) than Save (16 px). It is legible but not matched.
5. **No human play or acceptance.** There has been no creator visual review. The Pixelorama GUI Save As/reopen for room 2 is still pending, as stated in the v01 note.

## Task-closeout proposal (for root; not a receipt)

- **Task:** Washington survey annex rooms 1–2 default layout and collision fix (UNAPPROVED, technical only).
- **Meter effect: zero.** Accepted environments stay 3/12, sprites 0/52, plays 0/2, all meters 40.8%. There is no ledger, Bible, progress or Site change.
- **Selective sync (root, later):**
  - Stage `game/scripts/survey_annex.gd` as a whole file. Its diff against `7370739` is the room-2 integration plus this fix; they cannot be split cleanly, so sync it together with the room-2 v01 integration set from `3a34d132`.
  - Stage the two new tools and this note.
  - Optionally stage `cap/`, the report and the manifest. The other folders are verification bytes, hash-pinned by the manifest, and can stay local.
  - Never stage the whole tree.
- **Before or with the merge:**
  - Retire the room-2 v01 default-off 0 px parity expectation for the English frames. It is superseded by gates P1/P2 here.
  - The v01 Python gate D1 will fail against the new script by design.

## Addendum 2026-10-18 (integration onto main)

- **Parity retirement done.** As proposed above, the room-2 v01 parity expectation was retired. The v01 parity mode and its D1 gate now enforce zh 0 px and en header-only changes, and they pass on the combined script.
- **This check's report** now records that, instead of "expected FAIL".
- **Re-run against main `7553581`:**
  - `WDC_ROOMS_FIX_DEFAULT_ALL_OK`;
  - `WDC_ROOMS_FIX_OPTIN_ALL_OK`;
  - **GATES 12/12**.
- **Captures.** 31 of the 33 captures are byte-identical. The two `default-after-…-room2-west-wall` frames differ near the heroine, because real-time held-key stepping stopped her at x 32.67 instead of 34.04. Both stops are outside the x < 32 blocker.
