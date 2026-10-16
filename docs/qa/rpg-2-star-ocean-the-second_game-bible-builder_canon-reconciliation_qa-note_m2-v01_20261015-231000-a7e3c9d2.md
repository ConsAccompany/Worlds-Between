# Game Bible builder: canon reconciliation (Workstream A)

- Date: 2026-10-15, around 23:00 America/New_York (2026-10-16 03:05 UTC)
- Dispatch: `docs/coordination/rpg-2-star-ocean-the-second_post-quota_three-workstream-dispatch-prep_unapproved-v01_20261015-223416-8b4cd70e.md`, Workstream A only
- Inputs read first: the cloud stale-snapshot audit (`docs/qa/…game-bible-cloud_stale-snapshot-visual-audit_unapproved-v01_20261015-220957-76c8aa20.md`), the creator-decision note (`docs/design/…creator-decisions-2026-10-15_world-skills-ai-endgame_reconciliation-note_v01_20261015-174559-39efc292.md`), and the HEAD `cb6ca33` builder, Game Bible state and progress state. `AGENTS.md` does not exist in this repository.
- Kind: tracking-source fix. No game runtime, art, approval status or counter changed. Nothing deployed, committed or pushed.

## Finding

At `cb6ca33` the tracked Game Bible state JSON already holds the reconciled canon: five Earth civilization spheres plus the separate portal planet, NYC / City Hall Park / Yonkers / the Catskills / 2537-05-25, the 7-node and 5-node drafts marked superseded, and the 710-node rule. The progress JSON already reports M2 as 9/12 gates implemented with none accepted. The cloud panel shows old copy because it still serves snapshot `09d3689`. That is a deployment problem, separate from this source fix, and this session did not touch it.

The builder was the defect. It still:

- took every chapter body from the v01 design brief (five boards, 星外 as the fifth board, four Earth mainlines, first city to be decided);
- hard-coded the old facts (`5 个板块 · 地球与传送门另一端`) and the old open questions (seven-node trees, unnamed places);
- enforced the 7-node / 5-node drafts as if they were the design;
- wrote only its own keys.

So the next rebuild would have reverted the canon and silently dropped `creatorDecisions`, `citySampleReview`, `characterVisualReview`, `environmentVisualReview`, the approved job-roster status, and the superseded labels and approved rules on both tree blocks.

## Change

**Builder** (`tools/rpg-2-star-ocean-the-second_game-bible-builder_v01_20261013-195422-7e2a4f19.js`):

- **Still derived from the source files:** 51 identities, the 20-series × 5-stage job roster (status set to approved 2026-10-15, with the approval scope), and the 20 seven-node and 16 five-node drafts. The drafts are validated as superseded drafts and carry `superseded`, `pendingRedesign`, the approved 10-node rules and `redesignNodesRequired` 200 / 510.
- **Taken from the v01 brief:** chapter ids and titles only.
- **Carried from the tracked state and checked:** the reconciled chapter bodies, `openQuestions`, the three review blocks and `creatorDecisions`. Any unknown top-level key is also carried.
- **Refusal:** the builder throws if the tracked state lacks `creatorDecisions` (with the decision-note path), a reconciled chapter, or a curated section, instead of regenerating the brief text.
- **Canon facts it now writes:** world fact `5 个地球文明圈 · 终局星球经传送门`, chapter-2 summary, edition `设计基线 v0.2 · 2026-10-15 创作者决定`, and a note that the creator decisions are incorporated.
- **New `canonBasis` block:** records why the brief is superseded, that companions keep their legacy board labels with no invented sphere assignment (Wuxia has no companions), and the skill-node counts: **approved required 710 = 200 + 510, approved authored 0**, superseded draft nodes 140 + 80.
- **`checkCanon()`:** 24 named checks run on every build and exported for tests. They cover the five spheres in order with hubs and regions, the portal planet outside the spheres, the NYC / City Hall Park / Yonkers / Catskills / 2537-05-25 / NYC–Chicago geography, the world chapter (must contain the new canon and must not contain the v01 board table or the "four mainlines" and "first city pending" text), the 10-node rule text in chapters 4, 5 and 9, the superseded labels, 0/710 authored, 51 identities with legacy board counts 1/11/11/11/10/7, scene visuals 0/11 and runtime sprites 0.
- **`--check` mode:** rebuilds in memory and compares with the tracked file; writes nothing. The module exports `build`, `checkCanon` and `serialize`, and only writes when run directly.

**Game Bible state** (`outputs/…game-bible_state_v01_20261013-195422-b8c16d42.json`), edited by hand to equal the builder output, not regenerated: `edition`, `note`, `updatedAt` and the new `canonBasis` block. Chapters, characters, jobs, trees, open questions, review blocks and `creatorDecisions` are unchanged.

**Progress state** (`outputs/…mvp-progress_state_v01_20261013-183804-28a1c7e4.json`), M2 evidence wording only:

- The Shanghai route packet was described as the "source of the current preliminary figures"; it is now labelled superseded, since the Rome2Rio figures are retired and the US figures sit in the migration QA note.
- The Shanghai air packet is now labelled superseded by the creator's NYC–Chicago choice.
- The pre-migration 201 / 103 test counts are labelled as an earlier run.
- `updatedAt` updated.
- Gates, statuses, counters, ledger and decisions are unchanged.

**New test:** `tests/game-bible-builder/rpg-2-star-ocean-the-second_game-bible-builder_canon-reconciliation_check_m2-v01_20261015-230500-5c2d9e71.js`, read-only, five checks:

1. Canon checks pass on the tracked Bible.
2. A rebuild reproduces the tracked state (deep equality and key order), and the approved series equal the source verbatim.
3. Missing `creatorDecisions` and missing review blocks are refused. The v01 world chapter is rejected, and 8 stale or overstated mutations are rejected: an invented companion sphere, 710 nodes claimed as written, the old five-board fact, the final planet as a sixth sphere, an un-superseded draft, a rewritten rank rule, a scene counter of 1, and a 2026 start date.
4. Progress: M2 `in_progress`, 9/12 gates implemented, the three open gates named, none accepted, the exact counters, and start date and 710-node redesign consistent with the Bible.
5. File hashes are unchanged.

## Counters (unchanged)

Runtime exploration sprites 0/52, science scene visuals 0/11, human timed playtests 0/2, 51 identities / 52 visual variants. M2 is in progress with 9/12 gates implemented and none accepted. Approved 10-node skill nodes: 0/710 written.

## Verification status — NOT RUN

In this Claude Code session every `node` invocation needed approval, and the non-interactive session denied it automatically. That covered both `node -e` and `node <test file>`. **No builder run, no `--check`, no `node --check` and no test was executed.** The JSON was not regenerated by the builder. The edits were made by hand, and equality was argued by reading the code: source-key order, annotation key order, chapter titles and summaries, board counts, the 9 approved portraits, and the exact shared strings, confirmed with grep. Before integration, the coordinator must run from the repository root:

```
node --check tools/rpg-2-star-ocean-the-second_game-bible-builder_v01_20261013-195422-7e2a4f19.js
node tools/rpg-2-star-ocean-the-second_game-bible-builder_v01_20261013-195422-7e2a4f19.js --check
node tests/game-bible-builder/rpg-2-star-ocean-the-second_game-bible-builder_canon-reconciliation_check_m2-v01_20261015-230500-5c2d9e71.js
node tests/game-bible-m2-global-travel/rpg-2-star-ocean-the-second_game-bible_m2-global-travel-gates_check_m2-v01_20261015-064400-06efaa9b.js
```

Expected results:

- `--check` prints `contentEqual:true`. If it shows `bytesEqual:false` with `contentEqual:true`, the difference is formatting only, and one plain builder run normalizes it.
- The new test prints `RESULT PASS (5 checks)`.
- The existing M2 test still prints `RESULT PASS (5 checks)`. Its assertions do not touch the edited fields; it renders through the dirty app/server files.

## Remaining issues (not in this workstream's ownership)

1. **Cloud snapshot.** The private side panel still shows `09d3689`. Deployment and refresh are separate, and gated on Codex checking the local result.
2. **Dirty app and server not modified.** The progress fields `m2Expansion.researchPacket` and `airRoutePacket`, and the server route `/source/shanghai-liangzhu` behind the "查看路线研究 / View route research" link, still point to the superseded Shanghai packets. The existing M2 test requires those files to exist and to be served. Relabelling them needs the app/server owner.
3. **`docs/progress.md`** was not updated, because ownership was not transferred.
4. **The v01 design brief itself is unchanged.** The reconciled chapter text now lives only in the tracked state JSON, and the builder refuses to run without it. A reconciled brief v02 would make a cleaner long-term source and needs an owner decision.
5. **Open design work, unchanged:** companion sphere re-mapping, with Wuxia still empty; the 200 + 510 skill nodes; the prologue date and old-save date shift; relationship stages, reputation weights, difficulty multipliers and AI presets.
6. **Possible stale decisions, left unchanged.** The audit says the sentry v2 decision may be resolved or superseded. No creator record of that was found in the cited notes, so the `sentry-v2` candidate entry and the `sentry-direction` ledger scope were left as is. The `female-four-direction-animated` scope stops at v3r2, while local v3r3 and v3r4 candidates are unsynced; that belongs to the M8 owner.
