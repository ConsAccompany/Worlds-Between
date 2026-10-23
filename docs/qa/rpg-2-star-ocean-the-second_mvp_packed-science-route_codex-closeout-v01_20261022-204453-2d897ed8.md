# Packaged science-route journey and real process restart

Task `current-packaged-science-route-journey`, Codex accountable owner. Repository base `3f7bf0158d897cb3e197e29da4ec01a22fe66f4c`; game content remains `d5f204373c17c62e45e92dea14c3a2e85c525062`. This validates the existing delivered developer bundle; no replacement download or game-source change is required.

## Completed and directly verified

The same parameterized input harness and bounded runner now complete the following using the actual bundled Godot runtime and PCK, from an empty working directory and isolated per-run Windows profiles:

1. Ordinary main menu -> character setup. Language/name/female appearance are chosen with real mouse/key events; no progress is seeded.
2. Ordinary map marker and departure UI -> NYC. Held WASD follows the actual walk mask; E and Invite recruit Liang Xu.
3. Both NYC survey rooms: read all six clues through E/UI, select three evidence pairs and the final answer through actual buttons.
4. Actual map travel -> Yonkers. E checks the relay; real Invite recruits Zhao Ling. Walking into the bypass region records machine observation. Both rooms' six clues, three pairs and answer complete normally.
5. Actual map travel -> Washington. E reads the records plaque; real Invite recruits Ji Cheng. Both rooms' six clues, three pairs and answer complete normally.
6. Walking into the visible sentry triggers the real encounter. T enables ordinary full-auto; unchanged AI wins naturally. The real result button returns to Washington and clears the encountered enemy for that return. No HP, damage, cooldown, enemy, AI or finish flags are assigned.
7. Actual travel -> NYC, walk to the report marker and E -> report completed with all three surveys and companions.
8. Continue -> actual area Save button -> manual slot1 Save. Capture its exact entry ID/schema/snapshot and nonzero area foot position. Save Back -> area Esc -> map menu -> actual main-menu Quit ends the first process.
9. A distinct process starts with the same isolated profile and fresh empty autoload quest/party state. Main-menu Load -> same manual slot Load restores the actual area.24 persisted state bindings,5 travel bindings, physical position, report prerequisites and bounded play-time restoration pass. Entry ID/snapshot survives unchanged on disk.

| Run | Journey/reload process IDs | Checks | Final captures |
| --- | --- | --- | --- |
| Chinese female, Lin |31112 /32528|146 +45 =191|17|
| English female, Maya |17976 /43544|146 +45 =191|17|

**382/382 functional checks pass in four diagnostic-clean bounded processes;34 separate native640x360 captures.** Codex viewed12 final captures: the three survey-completion overlays, natural victory, report endpoint and restarted loaded area in both languages. Two earlier partial Liang/annex captures were also viewed. This is not a claim that every captured frame was visually inspected.

[Chinese two-process receipt](../../outputs/route55/root/r-20261022-205750-92b80aad/rpg-2-star-ocean-the-second_route55_receipt_20261022-205750-92b80aad.json) · [English two-process receipt](../../outputs/route55/root/r-20261022-205851-a8452695/rpg-2-star-ocean-the-second_route55_receipt_20261022-205851-a8452695.json).

## Evidence boundaries

- The sole setup fixture is loading ordinary `main_menu.tscn` as the first scene. All progression thereafter uses `Input.parse_input_event`; source geometry/answer data and save entries are read only. No `configure`, direct quest/recruit/save/load calls, teleportation, scenario-state seeding or battle shortcuts. Reading answer data is a test oracle, not a blind puzzle-solving assessment.
- The runner binds actual runtime/PCK/tool hashes and command/cwd/profile. It passes `--main-pack` with no source-project path or visual/pilot overrides. Godot consumes some engine options before exposing argument arrays; the external command binding supplies that proof, not the harness's argument-list check alone.
- Fixed60-fps simulation may run faster than real time. The game's automatically written roughly50-second receipt is **scripted simulation evidence**, not human timing. No human25–35-minute pacing, artistic acceptance, normal-speed motion assessment, new audio audition or final M9 regression is claimed. Human post-art plays remain0/2.
- This route tests ordinary full-auto sentry victory. It does not add another manual-skill/defeat/all-route-order/patrol/Chicago-flight regression. Previously scoped checks remain separate; do not describe this as every Godot test on the final art-integrated build.
- Static mask connectivity verifies pinned NYC/Washington masks have connected trigger regions. Some Washington marker pixels are inside prop blockers; gameplay correctly uses nearby interaction radii. The report retains exact-marker and legal-trigger results, not a claim that blocked prop pixels should be walkable.
- All3001 protected tracked game files excluding import files remain raw-byte identical. No game fix, new default, content point or approval was inferred from a test-tool correction.

## Failed checks and corrections

Claude's useful partial implementation covered real menu/setup/map/NYC/Liang/first-annex entry. It returned incomplete after243.25seconds, not an11-minute deadline or quota event; original tools and runs are preserved. Its first greedy walker stalled on the NYC mask; BFS corrected that test issue. DeepSeek completed an independent persistence/false-positive review in103.266seconds; Codex checked its conclusions against full source and completed the existing harness/runner.

Root's first full-route test reached all three surveys but its coarse4px waypoint planner failed the sentry approach. A downstream test then incorrectly accessed battle-only fields on the surface node, producing a diagnostic and failed run. Planner steps now match actual140px/s × process delta, check segment midpoints and handle scene disposal; battle entry is guarded before reading battle fields. No game geometry or interaction thresholds changed.

The next actual journey/save/quit/reload exposed strict dictionary equality failures in hero/member records. Inspection showed **only JSON float -> integer representation changes** at existing stage/skill-rank normalization sites in `growth_rules.gd`; no keys or numeric values were lost. The oracle now recursively compares exact numeric value while retaining all keys, array ordering and types for strings/bools/other values. It does not round values or compare only selected hero fields. Negative checks prove changed ranks/actual hero level, numeric strings and booleans are rejected. Original failed runs, diagnostic source, and the exact intermediate source reconstructed by matching its recorded SHA256 are retained. Final zh/en runs use the same final tested tool bytes.

## Progress and remaining work

Production **60.3% ->60.3%(+0.0pp)**; inspection **21.6% ->21.6%(+0.0pp)**; creator approval **7.8% ->7.8%(+0.0pp)**. Frozen1183-task baseline, coding111/111,content635/1881,inspection44/204,creator19/244 unchanged. This closes a playable delivery verification boundary without duplicating content/version points or marking the art-dependent final regression complete. Existing character source/slip and final art gates remain separately recorded.

The current developer ZIP can be played as delivered. Next delivery boundary: verify the official Windows release-export template route and prepare a native executable build if the matching template is available; no paid route or art refinement is authorized by this test. Final human plays and final art remain creator-owned gates.
