# Root navigation UI + themed music verification (unapproved technical candidate)

Recorded UTC: 2026-10-19T22:24:56.623022+00:00.

## Scope and responsibility

Codex independently tested the final root integration, without changing game/helper/producer source, staging, committing, ledger, Site or progress. Root retains code/Git/acceptance responsibility. This is a navigation UI capability/presentation check, not visual approval or a human playtest. Extra probes are explicitly unscored.

## Final result

- Source-bound root v04r1: **525/525**, normal exit, no engine errors/warnings. Producer v02 meaningful predicates retained; final root additions cover the declared NYC English room1 Title alongside Back, and Back-only room2.
- Exact same-instance probe: **14/14** EN/ZH contexts; **310 Button-context instances** including hidden controls. Actual Callable objects+flags compared before/after apply/revert (not connection counts or string signatures). Geometry, text, font resource/size, disabled/visibility/focus/input unchanged by the skin. Styleboxes/font colours are the helper's intended presentation changes.
- Combined normal `.tscn` path: **6/6**, EN/ZH exploration, NYC annex room1 and map, native640x360. Static nav override stays -1; CLI flags only `--themed-music-pilot` and `--navigation-ui-skin-pilot`. Main predicate suite uses only music flag; its static overrides exercise nav off/on.
- Audio: no doubled players or changed player identities, PCM, bus, volume or loop state during apply/revert. Existing city/annex retain one ambient+one cue player; map creates none. Selected city PCM SHA256 `52afbae0955065e5640cf4b1c9bf76a089d233e4ec2e0279432556faec1d7e70`,24000Hz,loopEnd1212632, playing. Dummy backend means no listening/quality claim. No2710-case audio rerun.
- All final processes observed **two actual AudioServer mix boundaries**, <=300ms, after fixture streams detached and run locals left scope; no diagnostic filtering. Final game/helper/music-selector raw hashes remain unchanged through all runs.

## Declared defaults and causal pixel proof

Root alone ported67 nav hook lines, then the NYC Back font-fit repair and the already established14px English title rule to NYCroom1. All10/12 other annex contexts remain default pixel/control exact. NYC ENroom1 allows only its original Title+Back control footprints; room2 Back only. Exact named changed set2/1, text, actions and all other controls unchanged. Actual old room1 Title ended428 against Saveleft418; repaired Title14 ends337. Old Back ended648; repaired98px ends623.

v03 initially passed519/520: the extra requirement that every Save-rectangle pixel remain identical was wrong because the original Title glyph visibly overlapped it. This failure is retained. A same-scene counterfactual changes ONLY old `title_label.visible=false`: same original Save and Back button text/font/rect/styles/exact Callables stay equal; restoring title visibility restores the full old screenshot exactly. The repaired visible Title14 Save crop equals the old Title-hidden Save crop byte-for-byte. Exactly65 changed Save pixels equal the actual old Title visible/hidden glyph mask, not a broad rectangle exception. v04 replaces only that incorrect predicate with the strict causal mask/crop contracts and adds5 explicit checks. No pixel/control threshold widened.

v04 functional525/525 initially warned about pending Dummy AudioStreamWAV/PlaybackWAV cleanup references. Raw warnings and verbose diagnosis retained. The known music-test teardown pattern stops/detaches fixture streams only AFTER all observations, frees fixture scenes, then drains2 real mixes bounded300ms. Final v04r1 retains all525 functional predicates and is diagnostic-clean. No game audio source changed.

## Visual inspection

Codex viewed all six separate actual normal640 captures: exploration/annex/map frames are legible in both languages; NYC ENroom1 Title clearly clears Save and Back fits; Chinese header fits. Native map frame, geography, labels and route-card dressing are intentionally untouched and retain their existing pixel contracts. Viewed old/new/Title-hidden Save crops show the removed stray old-title glyph at the left edge. No creator art approval inferred.

## Evidence and portability

Final result: `outputs/navigation-ui-v01/rpg-2-star-ocean-the-second_navigation-ui_root-combined-run-result_v04r1_20261019-222224-7d2c965e.json`. Final preflight binds producer v02 source hash, explicit root adaptations, current root music+legacy-guard pre-nav frozen sources at691522f and exact prerepair source066810... rebuilt by undoing ONLY the declared Back+Title repairs. An exact portable prerepair fixture is archived; it is not runtime code. Reproduction copies frozen sources to temporary original basenames and runs the same arguments in fresh APPDATA/LOCALAPPDATA with Godot4.7.2 windowed native640 and Dummy. Raw logs are retained unchanged; proof supplies raw and normalized-LF hashes for deliberate Git treatment by root.

One initial extra-probe compile mistake read `resource_path` on a preloaded script constant; literal resource-path hashing fixed it before execution, diagnostic retained. A Python console encoding failure after the v03 run did not change its saved raw log or result. Manual provisional future diagnostic filename tags181950/182050 were corrected to actual UTC rename221908 before publication, with mapping receipt; all final run/capture tags come from actual system UTC. No historical failure is counted as a pass.

Final proof manifest lists only the recommended final evidence plus separately labelled history, avoiding duplicate intermediate captures. Source/asset generation and final visual acceptance remain separate.
