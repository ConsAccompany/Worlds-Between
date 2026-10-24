# Milo north walk and stop — producer source checkpoint (UNAPPROVED)

Canonical task: content.char.milo.walk-north, attempt 50. Producer: Claude. Not self-approved; coordinator reruns checks and owns ledger/Git integration. Base revision edb87b8e (uncommitted producer files below). Hashes are raw SHA-256 bytes unless labelled text_lf_v1 (CRLF/CR -> LF).

## Delivered boundary (producer claim, pending independent rerun)

North-only 12-phase in-place back walk cycle (40 ms/phase, 480 ms loop) plus a phase-aware stop from every phase ([walk p, s1, s2, idle f00], 120 ms inclusive settle). It includes an editable 41-frame/13-layer PXO, a layered neutral ORA, a PNG sequence and an opt-in supplemental package, with a deterministic author and an independent checker. Source is 80x112, density 2, pivot 40,104, 48 logical px. Static and idle f00 are the byte-exact committed Milo north static PNG. One cycle serves walk/run at the host normal speed; there is no separate run-speed cycle.

Reuse: the frozen jexplore39 engine and the Milo render_idle/render_fb from the committed msw01 south author are loaded in memory. Neutral layers come from the committed Milo north static author draw() and must recompose to the pinned PNG. No existing file was replaced, so no backup or wb_safe_replace was needed.

## New files (scope: tools north author/checker, outputs/milo-nw01, this note)

- tools/rpg-2-star-ocean-the-second_milo_walk-north-source-author_unapproved-mnw01-v01_20261024-045533-2abbb86c.py: d3e44b8f227f9b7c6c887324ba6a80f5d293a6416bf88ca9c2ba20d94c2890cd
- tools/rpg-2-star-ocean-the-second_milo_walk-north-independent-check_v01_20261024-045533-2abbb86c.py: 0bb5c6a59ef821118e4c8c2770b250101d76fbbd24f6dd838f0c66ca876ec576 (derived from the msw01 checker; no author/engine imports)
- outputs/milo-nw01/rpg-2-star-ocean-the-second_milo_walk-north-qa-orchestrate_v01_20261024-045533-2abbb86c.py: c7dc1ff0fec7cae54f6c99ad41436fe17fd9eb0081bf0288b2f250837b316804
- 89 built files pinned in outputs/milo-nw01/rpg-2-star-ocean-the-second_milo_walk-file-list_unapproved-mnw01-v01_20261024-045533-8ecc42ce.json (bc174e671e5d6237098d15c3408fd8b955264dc1bd688ab90e83ee851873a446)
- PXO 70ab94137f5af7ab7f4725d71b629400df95ce52664bd0612e1ba99a7c6c6fd8; ORA 1b27f26b16411588cfc5c0901ed1eddfefb644b57033de450742b914ec3d5b5e; source manifest (…-b137cda1.json) 754688b89658c90524277446fce18329d3a34e07a3ad80791dabe22c66f69ab7
- Package is staged at outputs/milo-nw01/pkg (sprite set 47f05aba…, stop supplemental text_lf_v1 aa854f96…, package-local registry). It was deliberately NOT written to game/data, which is outside the assigned scope.

Read-only pins verified unchanged before and after: Milo north static PNG cf1e5598…, PXO 9d9004e6…, ORA a7a691f6…, manifest 0cb2b25f…, palette e837c5f7…; Milo south static PNG 3822b318….

## Commands and verdicts (from repo/, logs under outputs/milo-nw01/logs/<dir>/)

1. `python3 -I outputs/milo-nw01/<orchestrator> check check0` -> rc 1 (retained failed check): REBUILD 0/89 because outputs did not exist yet. SOURCE 19/19 in memory, deterministic.
2. `... build build1` -> rc 0: WROTE 89, REBUILD 89/89, DETERMINISTIC True, SOURCE 19/19, RESULT PASS.
3. `... check check1` -> rc 0: REBUILD 89/89, deterministic, SOURCE 19/19, neutral pins exact before/after.
4. `... indep indep1` -> rc 0: INDEPENDENT PASS 37/37 and 16/16 negative controls rejected: tampered PNG/PXO cel, bridge ending on idle f01, stop 39 ms, settle 119 ms, west entry, relabelled south, missing bridge frame, missing phase11, walk 0/41 ms, idle 699 ms, wrong pivot, extra south sprite entry, one-texel bridge foot slide, and a mirrored (south-sided) identity. Result JSON outputs/milo-nw01/indep1/…independent-result_v01_20261024-045533-2abbb86c.json: d1fdbd533dacaf14f7981374b3ca051b762e2eee17d61309e85068cf187da9dd.
5. Native Pixelorama 1.2.3 headless export (inside indep1, isolated XDG, Dummy audio, 90 s deadline): 41/41 RGBA-exact, exit 0, 6.81 s, source PXO unchanged. Four `custom_samplers` ERROR diagnostics remain, so application_clean=false. This is the same class seen on south. GUI SaveAs/reopen is not verified.

## Contact/slip (actual values)

Raw boots cels: each foot is grounded 4/12 phases; flight phases are 4, 5, 10 and 11. The planted-foot screen position is constant while grounded. Stop-bridge grounded-foot movement is 0 texels. The back gait is IN PLACE: at 140 logical px/s, a planted foot slips 11.2 source / 5.6 logical px per 40 ms phase. It is NOT footlocked and NOT slip-free. Contact metrics do not establish fluidity.

## Limitations / not claimed

- Leg motion is static leg texels lifted at most 4 source texels below the knee, with no foreshortening repaint. Coat and case ride the torso bob. At this scale the lift reads as subtle in the contact sheet.
- The source-bound PIL GIF (indep1) moves the sprite up-screen at host speed and jumps to a release at phase 7. It is not Godot gameplay or normal-input stop evidence.
- No Godot fit/probe was run in this attempt, and no runtime/default adoption. The generic loader ignores the stop supplemental. This single-direction package is not four-direction loader readiness.
- No art, motion or fluidity approval. Milo west remains paused and untouched; no ledger, Bible, registry or Git index edits.

## Next action

The coordinator independently reruns `check` and `indep` into fresh log dirs, then decides integration paths (optionally a checked-runner Dummy-audio source-fit overlay). Human normal-speed motion review stays separate.
