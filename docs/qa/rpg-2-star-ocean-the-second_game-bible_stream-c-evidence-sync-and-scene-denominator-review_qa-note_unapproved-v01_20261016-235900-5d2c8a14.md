# Game Bible Stream C: evidence sync, review-queue badges and scene-denominator review

Status: **Local edit for coordinator review. Not committed, not staged, not published. No gate, counter or meter changed.**
Meter **35.8%**, M2 **10/12**, runtime sprites **0/52**, science scenes **0/11**, post-art playtests **0/2**.

## Session limits

This Claude session ran non-interactively. Every `node`, `git hash-object`, `git ls-tree`, WebFetch and auth-status command needed approval and was refused. A subagent probe gave the same result. So:

- No app, server, builder, meter or Site test ran. Commands to run are listed below.
- No image URL was fetched. Raw-URL status is inferred from Git tracking only.
- The Claude Max / no-`ANTHROPIC_API_KEY` precondition could not be checked from the shell. The session proceeded on the dispatch's statement, and no paid fallback was used.
- Nothing was staged. `git add` was not attempted because nothing could be verified.

## Preexisting dirty files (inspected, not edited)

| File | Contents of the existing diff | Owner/assessment |
|---|---|---|
| `outputs/…game-bible_app_v01_…90e7bc24.js` | +61/+9: 2026-10-14 arena, paving, paving-A/B v8, archaeology and enemy-pilot cards | Old local work. It describes `battle_arena.gd` candidates that are themselves uncommitted, so it should not be synced until that script is. |
| `tools/…game-bible_server_v05_…3d5b8a9f.js` | Allowlist for three sentry GIFs, NUL-byte rejection | Same 2026-10-14 batch. |
| `docs/progress.md` | +48: dated 10-14/10-15 entries for the same batch and Liangzhu | Same batch. |
| `outputs/…mvp-progress_state_v01_…28a1c7e4.json` | 26 Codex zero-change closeouts 22:28–00:40 UTC, `lastUpdated` → `closeout-20261017-004051-d30c07f4`, 35.8% | Valid in form (delta 0, no gate change). Several cite evidence files that are **untracked** (review queue, eleven-scene audit, m8 visual review, v10 Codex audits, coordination docs), so a clean clone's meter `check` evidence would point at missing files unless those docs are synced with it. |

## Review queue: six actual Godot captures

All six were confirmed as real Godot captures from their manifests or reports. Map v02 uses a test-only runtime skin. The badges are stored in `environmentVisualReview.crossDeviceReviewQueue` in the Bible state and follow the recorded approval flags, not caption text.

| # | Capture | Badge | Git |
|---:|---|---|---|
| 1 | selout v8 city-bright | Approved static baseline (south still only) · nonruntime | tracked, blob `bd3add4a` |
| 2 | battle v10 ruins 640 | Unapproved · nonruntime | tracked, blob `cd5598dc` |
| 3 | NYC City Hall Park v04 640 axis | Unapproved · nonruntime | **local only**; hash-pinned in evidence index `2f06d687` |
| 4 | WDC Capitol west v08 640 entry | Unapproved · nonruntime | tracked (subdirectory), blob `bb022ebe` |
| 5 | Map v02 Northeast zh 640 | Unapproved · nonruntime (test-only skin) | **local only**; hash-pinned in evidence index `2f06d687` |
| 6 | Map v02 Chicago card zh 640 | Unapproved · nonruntime (test-only skin) | **local only**; hash-pinned in evidence index `2f06d687` |

The five generated concepts and identity references are a separate `nonruntimeConcepts` list with `galleryEligible: false`.

**The deployed Site will not show this queue yet.** The Site's forked `bible.js` (version 10) renders only `characterVisualReview.previews` and accepts only flat `outputs/*.png` names. Items 3 and 4 live in subdirectories, and items 3, 5 and 6 are not committed, so their raw URLs would 404. Publishing the queue needs:

1. a Site client patch, owned by Codex and not written here, that reads `crossDeviceReviewQueue`, allows one subdirectory level and uses the stored badge; and
2. a decision on whether the three local-only captures may be committed. They are evidence screenshots of unapproved scenes. They were not staged, in line with the instruction not to stage unapproved scene assets.

The `previews` list was deliberately left at 9, because `tests/game-bible-site-preview-figures` pins exactly 9 committed flat previews.

## Chicago Loop: twelfth science scene-quality gate?

**Recommendation: yes, add `chicago-loop-outdoor` as gate 12. Not applied.**

Reasons:

- The creator's 2026-10-15 decision places Chicago's Loop inside the MVP.
- `game/scripts/…chicago-loop_district-placeholder-scene_m2-v02_….gd` is a walkable, saveable and resumable street-grid scene. It is reached by the only air route, so players see it in normal play.
- The original 11 gates (map, three outdoor areas, six interiors, battle arena) date from 2026-10-14, before the US geography, and none of them covers the Loop. Codex's eleven-scene audit already flags this.
- Without a gate, environment art could reach 11/11 while a code-drawn placeholder ships in an MVP area.

**Meter.** Accepted scenes stay 0. Environment art goes from 0/11 to 0/12, which is 0 weighted points either way. By hand, the total stays 20 + 8.33 + 7.5 + 0 + 0 + 0 = **35.83 → 35.8%**.

**Why it was not applied.** Changing a denominator is a baseline revision. It has to change all of the following together and then be verified by running them:

- the meter CLI (`denominator: 11`; `validate` rejects `sceneVisualsTarget` ≠ 11);
- the meter test (pins 0/11 and a rejection case for 12);
- `approvalLedger.counters.sceneVisualsTarget` in the progress state, and a recorded closeout made through the CLI;
- the asset-inventory scene items (the app derives "场景画质 0 / 11" from them);
- `environmentVisualReview.sceneQualityTarget`, builder canon check line 294, and the builder canon test;
- the current-counter assertions in the environment-candidate, paving-A/B, enemy-pilot, M2 global-travel and selout tests.

Dated historical text (for example the 15c9b73 static-pilot snapshot, creator-decision counters and old QA reports) should stay 0/11. Doing this blind would risk a broken meter `check`.

## Tests to run before staging

```
node tools/rpg-2-star-ocean-the-second_game-bible-builder_v01_20261013-195422-7e2a4f19.js --check
node tests/game-bible-builder/rpg-2-star-ocean-the-second_game-bible-builder_canon-reconciliation_check_m2-v01_20261015-230500-5c2d9e71.js
node tests/game-bible-site-preview-figures/rpg-2-star-ocean-the-second_game-bible-site_production-preview-figures_check_v01_20261016-113125-a29ef51f.js
node tests/game-bible-m2-global-travel/rpg-2-star-ocean-the-second_game-bible_m2-global-travel-gates_check_m2-v01_20261015-064400-06efaa9b.js
node tools/rpg-2-star-ocean-the-second_mvp-completion-meter_recompute-and-task-closeout-cli_v01_20261015-233032-d296a2cb.js check
node tests/mvp-completion-meter/rpg-2-star-ocean-the-second_mvp-completion-meter_recompute-and-closeout_check_v01_20261015-233032-af0786b1.js
```

Expected: the builder check reports `contentEqual: true`, because curated sections are copied verbatim and the new keys were written in canonical 2-space form. The other checks should be unaffected, since no previews, counters or meter fields changed.
