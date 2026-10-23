# Lin Que lexplore59: bounded source-production verdict (unapproved artwork)

Hermes, 2026-10-23. Exact integration/test base: `b677e2902c57d0ab327b7733ad9ad89dccb65f2f`. Original producer base: `1c5793224c2d5b77f2dc9fc19b92cefff15b0ec9`. This report accompanies the source commit; the subsequent ledger closeout binds that commit explicitly. No default policy, existing game source, roster, scoring definition or creator decision is changed.

## Existing completion boundary

- `content.char.lin-que.idle-anim`: four directional idle loops committed with QA (2 existing points).
- `content.char.lin-que.walk-south`, `walk-west`, `walk-north`, `walk-east` under the same prefix: directional cycle and stop sources committed with contact/slip checks (3 existing points each).

The delivered source boundary satisfies those five existing production criteria. It does NOT satisfy `content.char.lin-que.runtime-integration`, `qa.char.lin-que.runtime-set-check`, full runtime visual review or creator acceptance. Their stricter runtime/default/slip and human gates are not weakened. No new version/report/test points are introduced.

The source author is Claude, from the completed PC producer. The independent package checker is DeepSeek's completed PC output. Hermes safely reconciled the bank, independently reran their checks, added raw-cel foot measurements, native animated exports and actual bilingual source-fit evidence. Historical ownership/attribution is retained; only the five already audited Hermes production tasks will receive their existing credit after this source is committed.

## Sources and hashes

- Source manifest: `outputs/lexplore59/rpg-2-star-ocean-the-second_lin-que_explore-source-manifest_unapproved-lexplore59-v01_20261022-231558-7d9a8dba.json`, SHA256 `67a6b5b390a2f136fc5425c0f81a67840a90eac4cd565a58461eb17ff01bfb90`.
- Primary animated PXO raw SHA256: south `7548408a4c3e3b4983fb02f9e7ef50c70ef56f858176e24d9991b28c131f7854`; west `e8f13e53329a631644c4271502d9c11f81c50febf4d46767c373c8153d52010c`; north `45d063f461f097df61783c7a6ea1150cce28ade6bb327b4de4f37de1c1058ddb`; east `c166326317694e95492ca8ae3e48d45e80d725d77a8bb990255f2305f0a1eac5`.
- Complete exact tested tools/helpers/game sources and artifact hashes: `outputs/lexplore59/hermes61/rpg-2-star-ocean-the-second_lin-que_source-boundary-proof_unapproved-v01_20261023-050631-c52d784a.json`.

All 346 incoming entries passed preflight SHA256/size and safe-path/conflict checks before materialization. Only absent paths were created; different bytes would have been refused. All 346 original files remain byte-exact. All 4,939 previously tracked game files remain raw-byte unchanged. Immutable vault was not modified. Scoped Git attributes preserve original PC bytes and new evidence independently.

Hash values are raw bytes unless explicitly labelled producer `text_lf_v1`: that implementation replaces CRLF with LF only. The initial boundary checker's prose incorrectly also mentioned lone-CR normalization; the producer function was not altered, and this correction is explicit.

## Actual executed checks

Use `source ../tooling/worlds-between-env.sh` first. The new boundary checker offers `materialize`, `source`, `contacts`, `native`; its exclusive receipts preserve failed runs rather than overwriting them.

- Existing independent DeepSeek package checker: 6/6 groups passed, including in-memory bad-hash, bad-duration and bad-actor refusal controls. No source mutation.
- Existing independent raw native-bank checker: 2,717/2,717 predicates passed. Raw PXO cels recompose to all source PNGs; ORA layers and merged statics match; alpha/bounds/floor contracts pass.
- Original author's source checks reproduced: 52/52; all 12 neutral PNG/PXO/ORA pins exact before/after; two Linux reconstructions deterministic.
- Independent raw-cel contact checker (no author import): all four direction results agree with the source report. Supplementary cross-host checker independently measures the 60 fps side excursion.
- Actual installed Pixelorama animated export: 41/41 frames per direction, 164/164 exact RGBA matches; all original PXO SHA256 values unchanged. Fresh unique directories were inspected, actual emitted names recorded and renamed only after pixel comparison. Requested `-o` basename was not trusted.
- Godot import passed through the bounded checked runner. Actual Xvfb/Mesa source fit passed: EN30 631/631, ZH60 1,087/1,087 checks; 16 actual 1280x720 PNG captures. Normal input actions exercise all idle/walk directions, exact frame boundaries and one microsecond before them, wrap, immediate stop, re-press and reversal. The companion is a labelled test-only avatar injection; no ordinary roster host is invented.
- Movies fully decoded: EN30 270 frames /9.0 seconds, ZH60 534 frames /8.9 seconds, both 1280x720. These are fixed-timestep actual renderer captures encoded at the tested cadence for 1x playback, not a human real-time playthrough. They do not demonstrate supplemental stop bridges.
- M1 smoke passed. Owner invariant test passed 7 checks after supplying its required repository-root argument; the initial missing-argument invocation failed before tests.

The project remains 640x360 logical/source canvas with a 1280x720 window/output. No project resolution setting was changed.

## Strict cross-host raw rebuild: FAILED, retained

The PC author's historical 341/341 byte-rebuild pass was NOT reproduced on this Linux toolchain: 18/341 raw files match. The strict check exits nonzero and its `passed:false` receipt remains intact. No original output was regenerated over different bytes, no expected hashes were replaced, and this failure is not relabelled as an all-pass.

Diagnosis on installed Pillow13.0.0 /zlib1.3:

- 312 differing source/runtime PNG files have exact decoded RGBA AND exact decompressed PNG filter streams; compressed IDAT bytes differ.
- Four PXO archives have exact decompressed member bytes, including native metadata/timing and all editable cels. ZIP platform `create_system` differs (PC0, Linux3).
- Four ORA archives retain exact layer/merged content; differing embedded PNGs decode exactly.
- Two JSON files differ only in explicit hashes of regenerated packaging; the additional file-list differs transitively.

Separate diagnostic: all 340 reconstructed content entries match; all 340 original file-list hashes match the retained disk bytes. This is not substitution for the failed raw rebuild. It establishes that the committed editable source/cycle/stop content is the original producer content and meets the frozen source-production criterion. Exact cross-host encoded-byte regeneration remains a disclosed portability limitation, not an earned gate.

## Contact limits, not a fluidity claim

Side40ms boundary slip is0.8 source texel /0.4 logical pixel; front/back in-place residual is11.2 source /5.6 logical pixels. Both side directions independently reproduce10.667 source pixels of frame-hold excursion at60fps. Grounded stop-source bridge movement is0 under the declared near-toe/heel and far-toe scope. Flight phases4,5,10,11 are retained. Occluded far heel/full outline continuity is not certified. The generic runtime host immediately idles on release and does not read supplemental stop JSON. Cape/scarf secondary follow-through is not authored. Do not call these fully footlocked or fluid animations.

## Diagnostics and visual scope

Pixelorama produces four shader diagnostics per direction (16 total); application-clean remains false. Animated-bank GUI SaveAs/reopen remains unverified. Codex separately verified one representative STATIC GUI SaveAs/fresh-process reopen/export; that does not prove animated-bank reliability. Rendered Godot runs retain V-Sync support and two ObjectDB-leak shutdown warnings. No diagnostic was filtered to create a pass.

One initial capture attempt used an incorrect hand-entered registry suffix; the loader correctly refused it. The failed log is retained. The final runs use the exact discovered existing registry path and pass.

Following the creator's system-readiness correction, Hermes loaded and inspected four actual capture stills with native `vision_analyze` on the existing main model. The separate still-inspection note records the visible coarse source style, scene-placement/contact-shadow limits and absence of cell cropping. Continuous movie perception, full motion/set review and creator approval were not performed. No visual/approval ledger task is closed.

## Combined-path failure and next bounded task

The existing M7 smoke fails `field station opens scifi.ruins`. Hermes independently reproduced the SAME failure on an isolated exact Git archive of base `b677e290`, with no Lin Que files. Both bounded logs are retained. This is not caused by adopting Lin Que (nothing was adopted), and it is not a passed combined regression. Do not claim release readiness or all Godot tests green.

Next concrete work: diagnose this M7 failure against the normal current field-station interaction, distinguishing stale fixture coordinates/state from a real playable defect, under the existing pre-playtest regression work (`qa.validation.pre-playtest-regression`). No new scoring task or QA completion is authorized by this note. Remaining Lin display/runtime/default work stays open; art/canon/default decisions and both timed human playtests remain creator-only.

## Progress and integration

Starting meters: production60.5%, inspection21.6%, approval7.8%. The separate ledger closeout records actual after-values; the verified five source tasks carry14 frozen existing content points, projecting content644→658/1881 and production61.0%, with inspection/approval unchanged. No operational transfer/readiness credit.

Before final push, integrate the creator-supplied disjoint readiness commit `53769f4cf99071b0c090cfa6fa92f2e48957682b` after stabilizing this source commit. Its full document and evidence were read; no environment/vault audit was repeated. Native still perception and representative static GUI reopen are now verified; CLI --image, private Site publishing auth, broad gh REST auth, Windows execution, listening and human playtests remain outside the claimed scope.
