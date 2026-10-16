# Game Bible: static-frame status sync after 15c9b73 (female battle v08, Liang Xu south v01), QA note

- **Date:** 2026-10-16 (UTC stamp 20261016-152110, id `590f82e3`). HEAD at start: `15c9b73`.
- **Scope:** Game Bible factual status only. No art, runtime, Game Bible app/server JS, progress state, completion meter or other session's dirty file was touched. Nothing was staged or committed; a separate integrator will do that.
- **Result:** the Bible now separates the one creator-approved static baseline from the two unapproved static pilots. No counter moves: sprites **0/52**, scenes **0/11**, playtests **0/2**, meter **35%**.

## Inputs read

- `~/.codex/AGENTS.md` (naming rules; this note follows them).
- Game Bible state `outputs/rpg-2-star-ocean-the-second_game-bible_state_v01_20261013-195422-b8c16d42.json` and builder `tools/rpg-2-star-ocean-the-second_game-bible-builder_v01_20261013-195422-7e2a4f19.js`.
- Independent technical audit: `docs/qa/rpg-2-star-ocean-the-second_static-pilots_female-battle-v08-liang-xu-south-v01_technical-audit-commit-closure_qa-note_unapproved-v01_20261016-150108-f2a96a98.md`.
- Codex visual audits: `docs/qa/rpg-2-star-ocean-the-second_protagonist-female_battle-static-v08-codex-visual-audit_unapproved-v01_20261016-145125-5e1b7d6c.md` and `docs/qa/rpg-2-star-ocean-the-second_liang-xu_south-idle-static-pilot-codex-visual-audit_unapproved-v01_20261016-145125-76c4ab13.md`.
- Pilot QA notes (`…battle-static-v08-game-scale-defect-pass…-68ec4f17.md`, `…south-idle-static-pilot_48px-identity-qa-note…-d01e679f.md`) and the selout v8 baseline decision `docs/character-visuals/rpg-2-star-ocean-the-second_protagonist-female_south-idle-static-baseline-decision_m8-v08_20261015-022700-07161696.md`.

## What changed

### Game Bible state (`characterVisualReview`)

New block `staticBaselinesAndPilots` (as of `15c9b73`), with `zh`/`en` summaries:

| Entry | Status | Key facts |
|---|---|---|
| `femaleExplorationSouthBaseline` | CREATOR-APPROVED STATIC BASELINE | selout v8, one south still at 48 logical px (PNG sha256 `ccf9d2a2…b6fd`); no animation, no other facing, not runtime, not a 0/52 acceptance. Links PNG, decision, QA note. |
| `femaleBattleSideviewV08` | UNAPPROVED / NONRUNTIME | run `326522f8`, one right-facing side-view still, no animation; only the 0.65 battle display proportion is creator-approved. Links PNG, .pxo/.ora, manifest, 2 Godot captures, QA note, Codex audit. Four open issues from the Codex audit. |
| `liangXuSouthIdleV01` | UNAPPROVED / NONRUNTIME | run `baa30d44`, `directions: ["south"]`, `fourDirectionSprite: false`, no animation, `humanReviewed: false`. Links PNG, .pxo, manifest, 4 captures, capture report, QA note, Codex audit. Six open identity issues; gender-neutral wording with a pronoun note. |
| `technicalAudit` | `reproducible: false` | closure check 11/11, author checks, and reproduction limits F1–F6 from the audit. |
| `counters` | snapshot | `0/52`, `0/11`, `0/2`, `35%`. |

Two `previews` entries were added (the app already renders `previews`, so no JS change was needed): the v08 ruins party capture and the Liang city-bright capture. Both captions say unapproved, not runtime-integrated, no animation, and name the main open issues.

`updatedAt` was refreshed. The existing `status` string and every counter field were left as they were.

### Builder canon checks (28 → 32)

1. Selout v8 is a creator-approved **static** baseline only: south, 1 frame, `animation`/`runtimeIntegrated`/`runtimeSpriteAccepted` false, exact PNG and decision file.
2. Battle v08: `UNAPPROVED / NONRUNTIME`, run `326522f8`, not approved/accepted/wired/animated, 1 frame, ≥3 open issues, approval note names only 0.65, all evidence files exist.
3. Liang v01: same, plus `directions == ["south"]`, `fourDirectionSprite: false`, `humanReviewed: false`, and no gendered pronoun (他/她, he/him/his/she/her/hers) in the entry or its preview caption.
4. Technical audit linked with `reproducible: false` and ≥3 limits; snapshot counters exactly 0/52, 0/11, 0/2, 35%; Bible `runtimeSpritesAccepted` stays 0. The check does not read the live meter, so a later legitimate meter change will not break the Bible build.

### Builder test

Six mutations added to `tests/game-bible-builder/…canon-reconciliation_check_m2-v01_20261015-230500-5c2d9e71.js`: selout v8 marked animated, v08 marked APPROVED, v08 marked wired, Liang given four directions, a gendered word added to Liang, and a counter set to 1/52. Each is rejected (8 → 14 mutations).

## Verification

| Command | Result |
|---|---|
| `node tools/…game-bible-builder….js --check` | `contentEqual: true`, `bytesEqual: true`, 32 canon checks |
| builder canon test | PASS (5), 14 mutations rejected, tracked JSON read-only |
| M2 global-travel test | PASS (5) |
| character-readiness test | PASS (7) |
| environment-candidate cards + paving v8 card | exit 0 |
| enemy-pilots card | exit 0 |
| selout-v2 card | PASS (14) |
| completion meter test | PASS (6) |
| static-pilot closure check (`…commit-closure-check…-0f79c1db.py`, `python -I -B`) | PASS 11/11 (`liang_reference_drift_known` still true) |

LF text hashes (first 16 hex), HEAD → working tree:
- Game Bible state `6713ab7e202ff077` → `ba077c1f0bd32a83`
- builder `4fd9c3ce0b0a6830` → `e1ff53c9773469c6`
- builder test `b603f5836b75c188` → `0a9b0c3d08d1a5d9`

## Open points for the integrator

- **F1 widens.** The Liang manifest locks a pre-`4245dd2` Game Bible state hash; this sync changes the state again. `check` and the closure check still pass (the drift is allowed only for `game_bible_state`), but Liang `build` stays non-idempotent.
- The app JS, server JS, `docs/progress.md`, readiness checklist and `game/scripts/battle_arena.gd` are dirty from other sessions. They are not part of this change. Stage by explicit pathspec only:
  - `outputs/rpg-2-star-ocean-the-second_game-bible_state_v01_20261013-195422-b8c16d42.json`
  - `tools/rpg-2-star-ocean-the-second_game-bible-builder_v01_20261013-195422-7e2a4f19.js`
  - `tests/game-bible-builder/rpg-2-star-ocean-the-second_game-bible-builder_canon-reconciliation_check_m2-v01_20261015-230500-5c2d9e71.js`
  - this note
- No closeout record was added to the progress state, because the meter and progress files were out of scope. Add one at commit time if the integrator's convention needs it (zero change, 35.0%).
- The Liang Xu author `check` (Pixelorama) was not rerun; no input to it changed except the Bible state, which `check` does not verify.
