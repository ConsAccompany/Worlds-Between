# Game Bible selout v2 review card: verification note

M8, 2026-10-14. Scope: the separate **selout v2** review card on the Game Bible production page, the state files it relies on, and the v2 and v1 `.pxo` files it points at. This note covers no art approval. v2 is **not approved**.

## Decision being recorded

- The user chose selout v1 (simplified/selective outline) as the closer of the two refinement candidates. v1 itself is not approved.
- The user says selout v2 is closer still, but **v2 is not approved**. Static-frame polish continues, and walk-frame production stays paused. No walk frames exist.
- Unchanged: exploration sprites 0/52, scene-quality gates 0/11, 48-logical-pixel display scale (the only approved scale decision), 51 identities / 52 variants, play limited to the science region.

## Changed files (this change only)

- `outputs/rpg-2-star-ocean-the-second_game-bible_app_v01_20261013-195526-90e7bc24.js`: new `#idle-selout-v2` card after the two v1 candidate cards. It shows the city, bright-outskirts and dark survey-annex v2 captures as separate images, links the dark prototype-room v2 capture and the four same-run v1 references, shows the badge "比 v1 更接近 · 仍未批准" (closer than v1, still not approved) and a "状态：未批准" (status: not approved) line, and labels the `.pxo` as the v1 editable baseline, not v2.
- `outputs/rpg-2-star-ocean-the-second_game-bible_styles_v01_20261013-195526-6c13fa09.css`: `.idle-v2-grid`.
- `outputs/rpg-2-star-ocean-the-second_asset-inventory_state_v01_20261013-191033-7d1e0a8b.json`: `runtime-sprite.protagonist-female` note and new `seloutV2*` / `seloutV1PixeloramaBaselinePxo` fields. `checked` stays `false`.
- `outputs/rpg-2-star-ocean-the-second_mvp-progress_state_v01_20261013-183804-28a1c7e4.json`: M8 summary sentence. Status stays `in_progress`.
- Readiness checklist JSON and MD: the inventory sha256 is now `04a8379778f986759eb9f7428143e10fb412812b54940a93f22c4234809cdef2`, and the v2 manifest is appended to the female variant's unregistered related manifests. These are the two values `--write` would change. They were edited by hand because Python could not be run in this session (see below).
- `docs/progress.md` and this note.
- New check: `tests/game-bible-selout-v2/rpg-2-star-ocean-the-second_game-bible_selout-v2-review-card_check_m8-v02_20261014-234724-e3b7a915.js`.

## Evidence gathered in this session

The shell permission policy in this session allowed only `sha256sum`, `wc`, `tail`/`od` and file reads. Every `node`, `python`, `curl`, `unzip` and `git add/fetch` invocation was refused. What was verified:

| Item | Method | Result |
| --- | --- | --- |
| v2 sprite `…selout-v2-polish-candidate_…d2eeefa2.png` | sha256sum | `4c8a720a…70e6f5` = manifest `output.sha256` = report `pilot_source_sha256` |
| 8 captures (`…_{city,outskirts-bright,survey-annex-room2-dark,prototype-room-dark}_…-selout-{v2,v1-reference}-h48_m8-v02_20261014-234215-2a1b6b58.png`) | sha256sum against report `capture_sha256` | all 8 match, all 8 distinct |
| QA report | read | 8 captures at 1280×720, each 43×96 window, `exact_rgb_matches == opaque_texels` (v2 2433, v1 2408), `human_reviewed: false`, `art_approved: false`, counters 0/52 and 0/11 |
| v1 `.pxo` `…selout-pixelorama-baseline_m8-v01_…5e93c40a.pxo` | sha256sum, size, binary entry-name scan | sha256 `b5b431c05fbee8bc6b92beedcbdf7c17849512e6f3b162c6a536ada2824c3039`, 9,218 bytes; ZIP local and central entries `data.json`, `image_data/frames/1/`, `image_data/frames/1/layer_1` and `image_data/frames/1/indices_layer_1` (Pixelorama project layout). Not referenced by the v2 manifest. |
| Inventory hash recorded in checklist | sha256sum after the final inventory edit | `04a83797…09cdef2` |
| Committed inventory vs old checklist hash | `git show HEAD:… \| sha256sum` | `a190f5fe…3330f1` matched before this change |

## Not run in this session

Run these from the repository root before committing:

```
node tests/game-bible-selout-v2/rpg-2-star-ocean-the-second_game-bible_selout-v2-review-card_check_m8-v02_20261014-234724-e3b7a915.js
node tests/game-bible-character-readiness/rpg-2-star-ocean-the-second_game-bible_character-readiness-view_check_m8-v01_20261014-225834-0f4cdab5.js
python -I tools/rpg-2-star-ocean-the-second_character-sprite-readiness_build-and-check_m8-v01_20261014-184413-c8e6c511.py
```

The new check:

- re-verifies the hashes above;
- reads the `.pxo` central directory with CRC-32 checks, then asserts that the canvas is 80×112 and that a raw RGBA cel has v1's 2,408 opaque texels and not v2's 2,433;
- asserts the inventory, progress and checklist invariants;
- starts the v05 server on a spare port and renders the production view. It asserts exactly one v2 card after the v1 cards, the three inline v2 images, all eight capture links served byte-identical, the unapproved wording, the v1 `.pxo` label and the unchanged 0/52 and 0/11 counters.

The `.pxo` cel assertion assumes Pixelorama stores `layer_1` as raw 80×112 RGBA. If the check fails there, inspect the entry sizes it prints before changing anything.

The checklist build script also globs every `protagonist-female_*manifest*.json` under `game/assets/characters/`. If the concurrent v3 session adds a manifest there before the build script runs, its no-write check will report the checklist as stale. That is expected, and the v3 session should regenerate it.

The live panel on port 18727 was not probed (curl was refused). Restarting it is not needed for this change, because the server code is unchanged and serves the edited files on each request.
