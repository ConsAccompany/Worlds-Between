# Game Bible Stream C v02: review-queue card, Washington v08 canon sync and the Chicago gate decision

Status: **local edits for coordinator review. Staged nothing until the coordinator accepts the stage list below. No commit, no push.** No gate, counter or meter value changed.
Meter **35.8%**, M2 **10/12**, runtime sprites **0/52**, science scenes **0/11**, post-art playtests **0/2**.

Supersedes the execution-blocked v01 note (`…stream-c-evidence-sync-and-scene-denominator-review_qa-note_unapproved-v01_20261016-235900-5d2c8a14.md`), which is kept for history. Its analysis was correct. This pass ran the tests and fetched the images it could not.

## Session

- Auth checked from the shell: `claude auth status` → `claude.ai` / `firstParty` / `max`, and `ANTHROPIC_API_KEY` absent. No API billing, credits or paid fallback were used.
- Peers asked over cross-session messages:
  - Stream A (map) and Stream B (Washington v09) both confirmed they do not own any Game Bible, progress or Stream C file.
  - Stream A asked that its `scifi_world_map.gd`, its route-inset tool and its QA note not be staged. They are not in the list below.
- `origin/main` = `a87ac16` (checked with `ls-remote`). Nobody has pushed since the live Site audit.

## Changes

| Path | Change |
|---|---|
| `outputs/…game-bible_state_v01_…b8c16d42.json` | **Washington v08 sync.** Walkable range is now v01–v08. `latestWalkable` = v08 (`6cf49486`, 67/67, UNAPPROVED / NONRUNTIME), with its v07 parent (`0f854fbc`) pinned. New `walkableHistory` keeps v06's 47/47 erratum and v07's 60/60. The art-route open-question prose says v08 and keeps both older counts as history. **Denominator review:** stale "Node blocked" wording replaced; meter impact restated after the CLI ran; the content-vs-visibility counter-point added; QA pointer moved to this note. The queue block from v01 is unchanged. |
| `outputs/…mvp-progress_state_v01_…28a1c7e4.json` | Current M2 text only (anchor gate detail, M2 details[3], remaining[1]): Washington walkable v01–v06 → v01–v08, City Hall Park pilots v01–v02 → v01–v04. Dated closeouts are untouched. |
| `tools/…game-bible-builder_v01_…7e2a4f19.js` | Two canon checks moved from v06 to v08. Each version's own gate count is pinned (v06 47/47 with the 48/48 erratum, v07 60/60, v08 67/67). The M2 text check rejects stale v01–v05..v07 and City Hall Park v01–v02/v03 ranges. Still 33 checks. |
| `outputs/…game-bible_app_v01_…90e7bc24.js` | New Production card `#cross-device-review-queue`, shown before "新版画面验收":<br>• the six captures as separate figures;<br>• each status badge computed from `creatorApproved` / `runtimeIntegrated` / `artAccepted`, never from caption text;<br>• a sync badge (GitHub commit vs "仅本机");<br>• the five concepts as text in a collapsed list, never as `<img>`. |
| `tools/…game-bible_server_v05_…3d5b8a9f.js` | Exact allowlist of two nested capture PNGs (NYC v04, WDC v08 entry). Every other nested or traversal path still returns 404. |
| `tests/game-bible-review-queue/…_check_v01_20261016-210902-8a86c60c.js` | New read-only test, 6 checks (below). |

## Review queue: what is honest to show

| # | Capture | Badge (from flags) | Git / raw URL at `a87ac16` |
|---:|---|---|---|
| 1 | selout v8 city-bright | 已批准静态基准 · 未接入运行时 · 未验收 (south still and 48 px scale only) | tracked; **raw 200, sha256 = local** |
| 2 | battle v10 ruins 640 | 未批准 · 未接入运行时 · 未验收 | tracked; **raw 200, sha256 = local** |
| 3 | NYC City Hall Park v04 640 | 未批准 · 未接入运行时 · 未验收 | **local only**; sha256 pinned in evidence index `2f06d687` |
| 4 | WDC Capitol west v08 640 entry | 未批准 · 未接入运行时 · 未验收 | tracked (run subdirectory); **raw 200, sha256 = local** |
| 5 | Map v02 Northeast zh 640 (test-only skin) | 未批准 · 未接入运行时 · 未验收 | **local only**; raw 404 (expected); pinned in `2f06d687` |
| 6 | Map v02 Chicago card zh 640 (test-only skin) | 未批准 · 未接入运行时 · 未验收 | **local only**; pinned in `2f06d687` |

Concepts: Washington damage guide, Chicago L guide, female sheet (identity reference), Washington and Yonkers battle guides. All are `galleryEligible: false`, are listed as text only, and appear in neither the queue nor `characterVisualReview.previews`.

**Deployed Site.** The Site (separate repo, forked `public/bible.js`) renders only `characterVisualReview.previews`, and only flat `outputs/*.png` names. So after a push:
- the queue card shows in the local Game Bible only;
- on the Site, a Codex-owned client patch is still needed to read `crossDeviceReviewQueue` and allow one subdirectory level;
- items 3, 5 and 6 load nowhere off this machine until the coordinator decides to commit those PNGs.

`previews` stays at 9 (pinned by the Site preview test). I did not add v10 or WDC v08 there, because the Site's status lookup would label them only from `staticBaselinesAndPilots`, and WDC v08's nested path does not resolve.

## Chicago Loop: twelfth gate — decision record

**Recommendation: yes.** Add `chicago-loop-outdoor` as gate 12. **Not applied.** Accepted scenes stay **0**.

Rationale:
- The creator's 2026-10-15 decision makes the Loop the one playable Chicago block (`mvpChicago`).
- `…chicago-loop_district-placeholder-scene_m2-v02_….gd` is walkable along the real street grid, saveable and resumable. It is reached by the only air route, so players see it in normal play.
- The 11 gates (2026-10-14) predate the US geography, and none covers it.
- Counter-point: the Loop has no survey, recruit, trace or battle and is not in `areas_visited`. The gate is about visual finish, not content, so it still applies, scored on finish and street-grid legibility only.

Meter, from the defined formula: environment art = 20 × 0/11 = 0, and would be 20 × 0/12 = 0. Total 20 + 8.33 + 7.5 + 0 + 0 + 0 = **35.83 → 35.8%** either way.
- `meter check` reports `CHECK OK 35.8%`.
- The new test recomputes both denominators from the stored categories.

Why not applied: it is a baseline revision. All of the following pin 11 and must change in one reviewed revision with a baseline closeout:
- the meter CLI (`denominator: 11`; `validate` rejects `sceneVisualsTarget` 12);
- `approvalLedger.counters`, the inventory scene items and `sceneQualityTarget`;
- builder canon check 0/11;
- six Game Bible tests and the meter test.

The 11 is a creator-set target, so this stream proposes the change rather than making it.

## Tests (all run 2026-10-16 ~21:15 ET on the working tree)

- `node tmp/…stream-c-test-runner_local-v01_….js` → **RUNNER: all passed (14 scripts)**:
  - meter CLI `check` (CHECK OK 35.8%);
  - builder `--check` (`contentEqual: true`, `bytesEqual: true`, `canonChecks: 33`);
  - meter test 6/6, canon test 5/5, Site preview figures PASS, M2 gates 5/5;
  - environment, paving A/B, enemy-pilot, selout and readiness tests;
  - the new review-queue test 6/6.
- **Review-queue test**, 6 checks:
  - flags and badges;
  - Git blobs at the recorded commit and the evidence-index sha256 for local-only items;
  - concepts excluded;
  - counters and the 11/12 recomputation;
  - rendered card: 1 approved-static and 5 unapproved badges, 3 local-only badges, 6 images served byte-identical, concepts as text, 4 traversal or non-allowlisted probes 404;
  - read-only hashes.
- Raw GitHub URLs: the three tracked captures each returned 200 `image/png` with sha256 equal to the local file. The local-only map capture returned 404, as expected.
- The clean-export result for the staged set is in the hand-off report.

## Not touched

- Stream A and B files.
- `game/scripts/*`, `docs/progress.md`.
- The v08 QA note's uncommitted Codex addition.
- The 2026-10-14 environment/enemy cards and GIF allowlist already in the app/server diffs. Those depend on the uncommitted `battle_arena.gd` candidates and are left out of the stage list.
- Every unapproved scene, character or concept image.
