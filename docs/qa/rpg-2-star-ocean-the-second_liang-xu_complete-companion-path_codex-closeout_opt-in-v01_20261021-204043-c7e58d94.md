# Liang Xu: complete playable companion preview

Owner Claude; independent boundary harness DeepSeek; integration/real-input checks Codex. Tested base `1cf65d314d93dee489cbf611afc448baa7a6d085` plus the exact source hashes in the [proof](../../outputs/lpath30/root/rpg-2-star-ocean-the-second_liang-playable-path_codex-production-proof_v01_20261021-204011-4dc924fd.json).

## Delivered boundary

Existing NYC recruit NPC uses the completed lexplore28 source bank through a separate Liang driver. The lcombat29 set works through a per-member combat model; Zhao and Liang can coexist while the hero model remains separate. Existing generic overrides win; an explicit companion pair selects only its named member and its actual index must be member-only. Missing/malformed Liang data refuses the whole Liang package while preserving the other actors. No followers, wandering AI, source-art changes, stats, damage, cooldown, story, collision, input or save-schema changes.

The fresh preview starts at NYC. Subsequent walking, E dialogue, Invite click, map/region/Yonkers/departure clicks, relay interaction, patrol contact, Tab control, Q/L/K/D/J, victory/result click and exploration return use real handlers driven by Input events. Reload calls AppState.load_save on the game's own autosave; it is not Save/Load-menu interaction. The defeat boundary first loads a declared 1HP/0energy saved checkpoint; the enemy causes the loss and the normal before-battle autosave restores a valid retry.

## Checks

- Combined editor import passes under the checked runner.
- Actual EN male victory at fixed60fps:60/60. EN female victory and original-clock MovieMaker recording at30fps:60/60. ZH female declared defeat/retry boundary at60fps:49/49. These are scripted input, not human playtests or motion/art acceptance.
- DeepSeek's independent current-host suite:120/120. Separate explicit-pair isolation:15/15. Existing Zhao boundary suite:15/15 for each hero appearance. Zhao's ordinary-default real-input victory/reload regression:55/55, without preview config calls or overrides.
- Preview entry rejects a missing dedicated profile before starting a run; a correct isolated profile reaches READY. The direct entry requires APPDATA/LOCALAPPDATA beneath a fresh work/lpath30-preview-profiles/<tag> folder and WB_LPATH30_PROFILE set to that folder.
-356 existing source/default files remain byte-exact. The two host changes are confined to presentation hooks; original renderer/mechanics/input/save code is retained. New stage bytes are compared with tested raw hashes.
- Actually observed Liang actions across these live runs: attack, defeat, dodge, guard, idle, move, skill. Hit is not claimed from these runs; all eight source clips were separately validated in the preceding source task.

Codex viewed native NYC NPC and controlled battle captures. NPC anchor282/180 is unchanged; the post-travel Zhao NPC remains visible while Liang stays in party data with no follower. Group overlap/proportions, faces and motion finish remain unaccepted and deferred. The original movie is1280x720/30fps; native screenshots are640x360. MP4 and the separate640x360/15fps GIF preserve elapsed time; no acceleration or artificial motion interpolation. The GIF is an excerpt, not a complete animation-set review.

## Corrections and limits

The first EN run failed two assertions: normal hero AI won before Liang reached melee range, and the harness incorrectly expected the unjoined Zhao NPC at Yonkers to be hidden. The revised test uses actual A input to move the hero left before Tab and preserves the real controlled-J attack assertion; it correctly retains the Zhao NPC. No gameplay numbers or actor positions were assigned to force a win. The exact failed harness snapshot hash matches its original report.

Root corrected provider comments from 梁旭 to canon 梁序, tightened explicit pair/index isolation, and guarded direct-preview saves. Producer originals remain in the isolated worktree. Headless source-boundary logs retain ObjectDB exit warnings (four instances in the independent suite); no SCRIPT ERROR, parser/runtime error or timeout passed as success.

## Completion and creator decision

Production **57.8% →57.8% (+0.0 pp)**. The two frozen integration tasks require ordinary default use and therefore remain in progress. A concrete one-line adoption patch passes git apply --check --unidiff-zero but is NOT applied. Project AGENTS.md requires separate creator authorization before replacing the ordinary Liang default. Full art, motion, sprite acceptance and two human playtests remain separate. This preview completes the implementation/test boundary without inventing points or weakening the task criterion.

Next: show actual gameplay media, obtain the default-adoption decision, then apply the prepared switch and verify the ordinary path.

Two display logs are whitespace-normalized for Git readability; byte-exact originals remain in hashed gzip snapshots. Source code, fixtures and test verdicts are unchanged. The prepared patch uses zero context, explicitly checked with --unidiff-zero.
