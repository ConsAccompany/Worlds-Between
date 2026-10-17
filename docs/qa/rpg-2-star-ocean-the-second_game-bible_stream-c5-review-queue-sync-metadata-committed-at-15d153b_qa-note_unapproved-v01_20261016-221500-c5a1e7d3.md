# Game Bible review queue: sync metadata for #3, #5, #6 corrected to committed-at-15d153b (Stream C5, UNAPPROVED)

Date: 2026-10-16. Source commit: `15d153ba915a84e1456def1abd840cae522e138b` (`origin/main` and local `HEAD` before this change).

## Why

Commit 15d153b pushed the three unapproved 640x360 Godot captures in the cross-device visual review queue (#3 NYC City Hall Park v04,
#5 world map v02 Northeast, #6 Chicago travel card v02), but the Game Bible state still badged them `staged-not-pushed`, and
`siteRendering` still described site version 10 with no raw URL. The private Site review-queue client is now deployed as site
version 11 (custom access preserved, per the coordinator). This is a metadata-only correction.

## Raw GitHub verification at the full SHA

`https://raw.githubusercontent.com/ConsAccompany/Worlds-Between/<full sha>/<file>`, downloaded to a fresh temp directory:

| # | commit | HTTP | bytes | git blob | sha256 | matches record |
|---|---|---|---|---|---|---|
| 3 | 15d153b | 200 | 84362 | 9848c949d99361c2ea0aed33318283493ed1911e | 9f61420c…b43a42a | yes |
| 5 | 15d153b | 200 | 72977 | 8e637f163ae049d1009883fba86ce9e9b5e9c367 | 50e59f16…5ec355f | yes |
| 6 | 15d153b | 200 | 73256 | 62a01a9b39ffe2db58dabd3599ae8b3dff5c22d0 | 0c9fb5d1…f96778 | yes |
| 1 | a87ac16 | 200 | — | bd3add4a9cb69ee162fa0aaaef900e320ad4c29a | 0b8e67ac… | yes |
| 2 | a87ac16 | 200 | — | cd5598dc93937272b777e74b7917f1e77491ca49 | 50687caf… | yes |
| 4 | a87ac16 | 200 | — | bb022ebebbe01193ffb40a8f05013dd747552841 | b566a88a… | yes |

`git rev-parse 15d153b:<file>` also equals the recorded blob for #3, #5 and #6.

## Changes

`outputs/rpg-2-star-ocean-the-second_game-bible_state_v01_20261013-195422-b8c16d42.json`, `environmentVisualReview.crossDeviceReviewQueue` only:

- items #3, #5, #6 `syncState`: `staged-not-pushed` → `committed-at-15d153b` (exactly three values);
- `siteRendering`: site version 11 deployed, all six actual captures on GitHub (#1, #2, #4 at a87ac16; #3, #5, #6 at 15d153b), approves nothing;
- `gitProposal.state`: `staged-not-committed` → `committed-at-15d153b`; `note` says pushed instead of staged; new `syncQa` points to this note.

Unchanged: `syncStateRule` (kept as the generic rule), every `gitBlob`, `sha256` and `hashPinnedIn`, all flags (`creatorApproved`,
`runtimeIntegrated`, `artAccepted`), badges, captions, concepts (5, `galleryEligible: false`, sync states unchanged), counters
0/52, scenes 0/12, playtests 0/2, meter 35.8%, all other canon. No generator or canon check change was needed.

`tests/game-bible-review-queue/...cross-device-review-queue_check_v01_20261016-210902-8a86c60c.js`: section 2 now requires 6/6
committed, 0 staged, 0 local-only, each recorded short SHA resolving to a commit in `HEAD` history with `<sha>:<file>` equal to the
recorded blob, the working file's blob and sha256 equal to the record, evidence-index sha256 pins kept, the Git proposal at
`committed-at-15d153b`, and a Site note naming site version 11 with no staged/local-only claim. The render check now expects 6
GitHub badges (3 × a87ac16, 3 × 15d153b) and no staged or local-only badge. Path, flag, badge, no-approval-control, byte-identical
serving and 4 nested/traversal 404 defenses are unchanged.

## Checks

- builder `--check`: contentEqual true, bytesEqual true, canonChecks 33 (working tree and clean staged-tree export)
- review-queue check: RESULT PASS (6 checks)
- canon reconciliation 5/5, M2 global travel gates 5/5, selout-v2 card 14/14, Site preview figures PASS, completion meter 7/7, character readiness 7/7

## Limits

The Site v11 deployment was reported by the coordinator; this stream did not open the Site or touch its checkout or credentials.
Being on GitHub or the Site approves nothing: five items stay unapproved, all six nonruntime and unaccepted.
