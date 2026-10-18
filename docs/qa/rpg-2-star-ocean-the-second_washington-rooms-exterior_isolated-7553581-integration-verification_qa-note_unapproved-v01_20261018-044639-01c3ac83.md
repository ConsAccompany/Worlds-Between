# Washington annex rooms 1–2 and Capitol west exterior v12r2: isolated 7553581 integration verification (QA note, UNAPPROVED)

Date: 2026-10-18 04:46–04:54 local. Prepared by Claude Code (Opus 5.5), signed in to Claude Max (claude.ai / firstParty). No quota or auth stop, and no API, paid or cloud fallback.

This is integration preparation only. Root inspected these native captures and accepts the technical results:
- annex en room 1 and en room 2;
- v12r1 entry, patrol, v8ref and battle return;
- v12r2 en pre-trigger and battle return.

**All new art stays UNAPPROVED.** Counters are unchanged: 40.8%, M2 10/12, scenes 3/12, sprites 0/52, playtests 0/2, formal acceptance false.

## Base and selection

- **Base:** main `755358137cc5a6b32ee878dec857869ebb6cf30a`. `survey_annex.gd` and `scifi_exploration_area.tscn` are the same blobs as at `7370739`.
- **Integration tree:** `work/iv5v13`, a detached worktree with its own index. The primary checkout and its index are untouched.
- **Full path list with hashes:** `outputs/rpg-2-star-ocean-the-second_washington-rooms-exterior_integration-selection-manifest_unapproved-v01_20261018-044639-01c3ac83.json`.

**Modified tracked files (3):**
1. `game/scripts/survey_annex.gd`, staged as a whole file.
   - Its diff against `7553581` (+120/−13) equals the c3ff819c full-diff patch line for line: the room-2 records-chamber branch plus the default layout and collision fix.
   - Every hunk is gated on `scifi.ruins` / `wdc_room_two`. NYC and Yonkers code paths are untouched.
2. `game/scenes/scifi_exploration_area.tscn`: one line, the v12r2 hook (LF pin `37f634af…`, as in the v12r2 note).
   - With all flags off, the scene runs the base script.
   - The v12r1 flag alone gives exact v12r1; the v12 flag alone gives exact v12.
   - No hunk from `scifi_exploration_area.gd` or `battle_arena.gd` is taken.
3. The progress ledger: two zero-change closeouts, described below.

**New files:**
- the room-2 fixtures (4 runtime PNG + `.import`, and their native `.pxo`/`.ora`/PNG sources with the author manifest and author tool);
- the room and default-fix tools and the accepted-rooms replay tool;
- the v12 selector, the v12r1 selector and the v12r2 selector;
- the 7 v12 runtime layers with their `.import` files;
- the v12 editable sources: 28-layer `.pxo`/`.ora`, flat, manifest, palette and contract;
- the v12, v12r1 and v12r2 harnesses and checkers;
- the QA notes and the evidence directories.

**Left out:**
- the v12 build-check (it needs the uncommitted v11 candidate);
- the room probe, parity, replay and log bytes (hash-pinned by their reports);
- the wdc-table Save As report (not ready yet);
- all Bible, Site, run-v07, account, budget, controller and log files.

## Checker updates (bounded, existing tools only)

- **Room-2 parity r1.** The `--default-off-parity` mode in the room-2 Godot check, and the room-2 Python gate (renamed `D1_default_off_zh_identical_en_header_only`), now require:
  - zh identical to HEAD;
  - en changed only in the 62-row header.
  This replaces the 0 px expectation that the intentional c3ff819c header fix made stale. The old QA text is kept, with dated addenda.
- **c3ff819c evidence check.** Its report string now records the r1 rule instead of "expected FAIL".
- **v12r1 checker.** Its `overlay_matches_worktree_candidate_files` now also accepts the worktree hook naming the pinned v12r2 successor line. Only that line; any other hook still fails.
  - Without this, the run against `7553581` gave 49/50 with only this gate failing. The failure was caused by the selected v12r2 hook, which the v12r1 tool predates.

## Checks run from 7553581 + this selection

All runs used a short-path mirror, `%TEMP%\iv755`, built by `git apply --index` of this tree's staged diff. Its `git write-tree` (`4cb944b2…`) equals this tree's index tree before the late edits to the evidence documents and checkers. Each Godot run used a private `APPDATA`. The exterior clean tree was rebuilt from `7553581` under a redirected `LOCALAPPDATA`, so root's existing `%LOCALAPPDATA%\Temp\w12r1-23596520` tree was left untouched. No mirror run changed tracked files.

| Check | Result |
|---|---|
| Room 2 opt-in Godot check | `WDC_R2_V01_ALL_OK` |
| Room 2 default-off parity r1 | OK: room 1 zh 0, room 2 zh 0, room 1 en 1377, room 2 en 4965 px, all in the header |
| Accepted rooms replay | `ACCEPTED_REPLAY_ALL_OK`. **NYC room 1, NYC room 2 and Yonkers room 2 are 8/8 at 0 px** against their acceptance images. |
| Room 2 Python source/pixel/Pixelorama check | **GATES 16/16** (CLI only; GUI Save As is not claimed) |
| Default-fix Godot check | `WDC_ROOMS_FIX_DEFAULT_ALL_OK`, `WDC_ROOMS_FIX_OPTIN_ALL_OK` |
| Default-fix evidence check | **GATES 12/12** |
| v12r2 sentry viewport check `all` | **PASS 30/30**: clean tree exported from `7553581` (1,296 HEAD blobs re-verified, 0 mismatches), headless smokes pass, sentry zone and real routes pass, battle return passes |
| v12r1 integration fix check `all` | **PASS 50/50** after the successor-hook update (49/50 before; only `overlay_matches_worktree_candidate_files` failed) |

**Reports from these 7553581 runs** are 7 JSON files in `outputs/wdc-integration-755_01c3ac83/`. The original report files in the candidate evidence dirs are kept unchanged as history.

### Captures compared with the delivered sets

- **Room 2 (3a34d132):**
  - 18 zh captures are byte-identical.
  - The 15 en captures differ only in the Back-button box (x 529–624, y 12–49; 715–731 px each; 1377 px for the room-1 return frame). They were taken before the c3ff819c font fit.
- **Default fix (c3ff819c):**
  - 31 of 33 captures are byte-identical.
  - The two `default-after-…-room2-west-wall` frames differ near the heroine. Real-time held-key stepping stopped her at x 32.67 rather than 34.04. Both stops are outside the x < 32 blocker and the gate passes.
- **Exterior:** all PNGs are byte-identical to the delivered sets: v12r1 21/21, v12r2 8/8, v12 reproduction 12/12.

## Round 2 (2026-10-18, after root review of the 202-path selection)

**Reproducibility and candour fixes.** None of them weakens a runtime or default gate.

1. **Exterior replays work after commit.**
   - What changed: `scene_with_hook` in the v12r1 checker, which the v12r2 checker also uses, accepts HEAD's `scifi_exploration_area.tscn` only under these conditions:
     - it carries exactly one of three pinned hook lines (base script, v12r1 selector, v12r2 selector);
     - with that line set back to the base script, it equals the pinned baseline scene (LF sha256 `df063dd9…`, the file at 7370739 and 7553581).
   - Rejected: any other hook, a second hook, or any other edit.
   - Mutation fixtures (throwaway, 9/9):
     - accepted: base, v12r1, v12r2 and CRLF v12r2;
     - rejected: an unpinned v12 hook, an arbitrary script, a missing hook, two hooks, an extra node.
2. **Room default-off baseline pinned.** The room-2 `--default-off-parity` mode and the default-fix check's "before" run now require the baseline copy's LF sha256 to equal `bedc4adb…`. That is `survey_annex.gd` blob `eecdcca`, identical at 7370739 and 7553581.
   - After commit, HEAD is no longer that baseline. The copy comes from `git show 7370739:game/scripts/survey_annex.gd`.
   - A missing or different file fails, with that instruction.
3. **`survey_annex.gd` comment corrected (comment only).** The new header comment claimed that without the flag room 2 "draws and plays exactly as before". That was wrong: the default build intentionally changes Washington behaviour. The comment now states the actual scope:
   - opt-in only: the fixtures, markers and labels, the fixture and table blockers, and the lifted discs;
   - default, Washington rooms only: room-2 wall blockers, the English 14 px title and the Back font-fit;
   - zh frames unchanged.
   - Consequence: the whole-file diff against 7553581 now differs from the c3ff819c full-diff patch only in those comment lines.

**Added to this commit:**
- **WDC analysis-table native WEB Save As (d4864693).**
  - Files: the saved `.pxo` copy (`3f14e0b2…`), root's identity screenshot (`614803cf…`), the reusable checker (`f8aab523…`), the 10/10 report (`b5df2ec4…`), and the corrected QA note (`f1dad8cf…`).
  - Scope: **WEB GUI only**; desktop GUI unverified.
  - Its report records that one existing desktop untitled-backup file in the real Pixelorama APPDATA changed during the window. `config.ini` and all other files were unchanged. The cause, the open desktop window's autosave, is inferred, not proven.
- **Yonkers room 1 v05 test-only candidate (4b9d66f1), 58 files:**
  - 5 tools;
  - `.pxo`/`.ora`, flat, palette and manifest;
  - 5 nonruntime exports;
  - source-check report, pixel-check report and 2 Godot logs, which the pixel check reads;
  - 30 captures and 8 accepted-room replay captures;
  - the QA note.
  - The v03/v04 dependencies are already at 7553581. The accepted-rooms replay tool is the same file as in this selection (`a6552f03…`).
  - Not wired: `survey_annex.gd` still loads v03.
  - The v05 evidence was produced on a `git archive 7553581` scratch tree.

**Ledger:** 4 zero-change closeouts after the existing 123:
- Washington rooms;
- Washington exterior;
- WDC table web Save As;
- Yonkers v05.

## Honest dates

- **v12r1 end time.** The v12r1 QA note's header says the run ended "05:10 EDT". The actual end was about **04:13 EDT**. The v12r2 note records this correction, and the v12r1 note is kept unedited as history.
- **Primary tool mtime.** One primary-checkout file was briefly edited by mistake during this preparation and restored at 04:35:
  - file: `tools/…wdc-annex-room2_godot-capture-and-check…151fb8d0.gd`;
  - its content again matches the sha256 pinned in both dependency manifests, `1de17fdd…`;
  - only its mtime changed.

## Remaining limitations

- **Style seam.** The native props are sharper than the soft m8-concept background. This is a stylistic seam and is not resolved.
- **Exterior placeholders.** The English machine label is displaced left but readable. The sentry is still the red-block `_draw_enemy` placeholder in clean replays, and it is not claimed as accepted animation. Camera feel still needs a human review.
- **Replays after commit (fixed in round 2, see below).** The exterior clean replays first required HEAD to carry the base hook line, so they could run only before commit. That is fixed. After commit, the replay's "HEAD" tree already contains the candidate files, so the HEAD smokes there test HEAD-with-candidate. The default-flags-off runtime gates still prove base behaviour.
- **No GUI Save As here.** The Pixelorama GUI Save As/reopen of the room-2 fixtures is not part of this batch. A separate wdc-table check is pending and held back.
- **Nothing accepted.** There has been no human play and no art acceptance.
