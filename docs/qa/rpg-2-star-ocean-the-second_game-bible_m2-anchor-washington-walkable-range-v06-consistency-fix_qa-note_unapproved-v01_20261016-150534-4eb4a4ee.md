# Game Bible: M2 anchor text, Washington walkable range v01–v05 → v01–v06 (QA note, text-only consistency fix)

- **Date:** 2026-10-16 15:05 UTC. **Stamp:** `20261016-150534`. **Id:** `4eb4a4ee`.
- **Author:** Claude (Claude Code, Opus 5.5).
- **Trigger:** A Codex live-site read at GitHub SHA `3f97c9a` found an inconsistency. The M2 first-city / anchor section said the Washington Pixelorama walkable candidates were **v01–v05**, but the art-route section correctly said **v01–v06**.
- **Scope:** a factual text correction plus one builder assertion. **No counter, gate status, meter value, closeout record, art approval or runtime file changed.**
  - The v06 candidate stays **UNAPPROVED / NONRUNTIME**, with technical checks at **47/47**.
  - Scenes stay **0/11**, sprites **0/52** and playtests **0/2**. M2 stays **9/12**. The overall meter stays **35.0%**.
- **Not staged, committed or pushed.**
- **Not touched:**
  - the dirty Game Bible app (`outputs/…game-bible_app_v01_…90e7bc24.js`) and server (`tools/…game-bible_server_v05_…3d5b8a9f.js`);
  - `docs/progress.md`, `game/scripts/battle_arena.gd` and the character-readiness checklist files;
  - the Capitol v06 build tool;
  - the Game Bible state JSON (sha256 checked before and after the builder `--check`).

## Where the stale text was

The stale text is not in the Game Bible state, which already said v01–v06 (see the v06 sync note `…game-bible_wdc-capitol-west-v06-state-sync_qa-note_unapproved-v01_20261016-145140-4b9cef78.md`). It is in the MVP progress state that the site serves at `/state`:
`outputs/rpg-2-star-ocean-the-second_mvp-progress_state_v01_20261013-183804-28a1c7e4.json`.

Three current-state strings in it still carried the v05 range:

| location | before | after |
|---|---|---|
| `m2Expansion.gates[id=anchor].detail` (首城与地下社区锚点, the section Codex flagged) | `…Pixelorama 候选（可步行 v01–v05、独立定场远景 v01–v02）…` | `…（可步行 v01–v06、独立定场远景 v01–v02）…` |
| `steps[id=M2].details[]` (zh "仍待制作或核实" line) | `（可步行 v01–v05、独立定场远景 v01–v02）` | `（可步行 v01–v06、独立定场远景 v01–v02）` |
| `steps[id=M2].remaining[]` (en "Art for the implemented places" line) | `(walkable west grounds v01-v05 and a separate dome cinematic vista v01-v02)` | `(walkable west grounds v01-v06 and a separate dome cinematic vista v01-v02)` |

- All three are the same statement, so the zh and en M2 lines were corrected along with the anchor gate.
- Nothing else in those strings changed: "未批准、未接入运行时", "均未验收" and the City Hall Park v01–v02 wording are as before.
- **Left as history on purpose:** the dated closeout record `closeout-20261016-095626-fd80e626` says "v01–v04". It records what was true at 09:56 and was not edited.
- `git diff --numstat` for the progress state: `3 3`. The replacement script required exactly 2 zh hits and 1 en hit, and re-parsed the JSON before writing. The file stays LF.

## Builder assertion (canon checks 27 → 28)

File changed: `tools/rpg-2-star-ocean-the-second_game-bible-builder_v01_20261013-195422-7e2a4f19.js`

- New read-only constants `progressDest` and `readProgress()`. Both are exported, along with the existing exports.
- New signature: `checkCanon(bible, progress = readProgress())`. Existing callers are unchanged.
- **New check:** "M2 anchor / progress text: Washington walkable v01-v06 matches the Bible, no stale v01-v05". It requires:
  - the Bible's `washingtonDC.unapprovedCandidates.walkable` ends at `v06`;
  - the anchor gate detail contains `可步行 v01–v06`, `独立定场远景 v01–v02` and `均未验收`;
  - the combined current M2 text (anchor detail + M2 `details` + M2 `remaining`) contains `可步行 v01–v06` and `walkable west grounds v01-v06`, and does not match `/v01[–-]v05/`.
- Closeout records are not part of this check.

**Negative probes** (run in memory; nothing written):

| probe | result |
|---|---|
| progress state at `HEAD` (`3f97c9a`, via `git show`) | rejected by the new check |
| only the anchor gate reverted to v01–v05 | rejected |
| only the M2 en `remaining` line reverted | rejected |
| only the M2 zh `details` line reverted | rejected |
| Bible walkable list cut back to v05 | rejected (existing Washington check) |
| current state | passes, 28 checks |

## Tests (2026-10-16, repository root)

| command | result |
|---|---|
| `node tools/…game-bible-builder_v01_…7e2a4f19.js --check` | `contentEqual true, bytesEqual true, canonChecks 28`, exit 0; Bible state sha256 unchanged |
| `tests/game-bible-builder/…canon-reconciliation_check_m2-v01_…5c2d9e71.js` | RESULT PASS (5 checks), exit 0 |
| `tests/game-bible-m2-global-travel/…m2-global-travel-gates_check_m2-v01_…06efaa9b.js` | RESULT PASS (5 checks), exit 0; 9/12 gates, door-to-door 0 |
| `tests/game-bible-environment-candidates/…environment-candidate-cards_check_m8-v01_…c9369925.js` | all PASS, exit 0 |
| `tests/game-bible-environment-candidates/…paving-ab-selout-v8-card_check_m8-v02_…4e7a1c2d.js` | all PASS, exit 0 |
| `tests/mvp-completion-meter/…recompute-and-closeout_check_v01_…af0786b1.js` | RESULT PASS (6 checks), exit 0 |
| meter `check` | `CHECK OK 35.0%`; sprites 0/52, scenes 0/11, playtests 0/2 |

The two panel tests that start a server use the working-tree `game-bible_server_v05`, which has another session's uncommitted edits. That file was not modified here.

## Not claimed

- No scene or art approval and no runtime wiring. `highPrecisionPixelSceneAuthored` stays false.
- No meter closeout was added, and no counter or gate changed.
- The live site was not re-read. The fix appears there only after these working-tree edits are committed and deployed, which this task did not do.
