# Game Bible accuracy correction: sentry v2 scope, Washington candidates, M2 route links

- Status: copy/link correction only. No art, gameplay, gate status or counter changed. Sprites 0/52, scenes 0/11, human playtests 0/2, M2 9/12 and the 35.0% meter are unchanged.
- Trigger: the private tracker at `/tracker` (GitHub `main` 22d3444, 35%) still carried three stale details.

## Corrections

1. **Sentry animation v2.** The creator approved v2 as the ACTION direction baseline only. That is not full sprite or art acceptance. This scope was relayed in the 2026-10-16 Codex dispatch; no earlier repo record existed. `approvalLedger` `sentry-direction` stays `direction_accepted`, and its scope, the M8 summary/notes/remaining text and the `sentry-v2` decision now say "action direction baseline only; art acceptance 0". v3–v5 stay unwired.
2. **Washington, D.C. Pixelorama scene.** The tracker said "尚未制作" (not yet made). Unapproved walkable west-grounds v01–v04 and a separate dome cinematic vista v01–v02 do exist. None is wired into the runtime or accepted. The Bible open question and the new `environmentVisualReview.washingtonDC.unapprovedCandidates` record now say so. The flags `highPrecisionPixelSceneAuthored`, `runtimeIntegrated` and `artAccepted` stay false; the first means there is no runtime-ready or accepted scene. In M2, the anchor gate and the remaining items also name the unapproved City Hall Park walkable pilot v01.
3. **Active M2 route links.** `m2Expansion.researchPacket` now points to the US migration QA note (`docs/qa/…us-science-sphere_runtime-migration_qa-note_m2-v02_…364131c8.md`). `airRoutePacket` and the new `activeTravelData` point to the v02 US travel data (`game/data/world-travel/…m2-us-science-v02_…c454007b.json`). The two Shanghai packets are kept under `archivedResearchPackets` with `status: archived_superseded`. In the local Bible app, the gates-card link now reads "查看当前美国路线来源 / View current US route sources" and opens the US note through `/evidence`. The Shanghai packet is now a separate link labelled "归档：已取代的上海／良渚路线研究 / Archive".

## Files

- `outputs/rpg-2-star-ocean-the-second_mvp-progress_state_v01_20261013-183804-28a1c7e4.json`
- `outputs/rpg-2-star-ocean-the-second_game-bible_state_v01_20261013-195422-b8c16d42.json`
- `tools/rpg-2-star-ocean-the-second_game-bible-builder_v01_20261013-195422-7e2a4f19.js`: new canon check 25 rejects the old "尚未制作" text and any Washington candidate marked runtime or accepted. The HEAD 22d3444 state now fails this check, as intended.
- `outputs/rpg-2-star-ocean-the-second_game-bible_app_v01_20261013-195526-90e7bc24.js`: only the route-link hunk was staged. Other workstreams' uncommitted hunks were left out.
- `tests/game-bible-m2-global-travel/…_check_m2-v01_20261015-064400-06efaa9b.js`: assertions updated for the new wording, links and archive.

## Checks

- Builder `--check`: contentEqual true, bytesEqual true, 25 canon checks.
- Tests PASS: M2 global travel (5), builder canon reconciliation (5), character readiness (7), selout v2 (14), meter (6). Meter `check`: CHECK OK 35.0%.

## Limitations

- The hosted tracker's own source is not in this repo. It reads GitHub `main`. Whether it renders `researchPacket`/`airRoutePacket` as links, or shows `archivedResearchPackets`, must be checked on the live Site.
- The walkable v01–v03 QA notes and the v04 technical note are still uncommitted local files. The tracked evidence is the v04 Codex audit plus the dome v01 and v02 QA notes.
