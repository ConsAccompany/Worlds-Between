# Complete heroine playable path: technical delivery and workflow changes

Recorded 2026-10-21T02:04:47.573699+00:00. Base bb3449d4928fdb9495ebda9c8b61f1f41b47bac3. Claude authored phase-aware stop source and play entry; DeepSeek authored independent source checker and combined normal-flow harness; Codex inspected, corrected, tested and integrated.

## Delivered

One reusable opt-in entry starts a fresh solo female run in the normal game, with all four exploration directions, actual normal walk-in patrol encounter, the existing 29-pose/eight-action combat set and contact timing, natural victory, result click, exploration return and autosave reload. It uses a separate local save profile. One-click Chinese launcher: tools/rpg-2-star-ocean-the-second_heroine_playable-preview_zh-v01_20261021-020447-2e046dd4.cmd. Launcher prepares assets through a bounded native import, refuses engine diagnostics, caps startup at20s, then leaves normal interactive play open after READY. No main-menu/default adoption or art/human-playtest approval.

Side-stop source now includes 12 actual outgoing phases per east/west direction, four samples each, exact outgoing walk and original idle endpoints. 52 original idle/walk PNG bytes and 16 legacy stop PNGs protected; 96 phase samples equal their 2 editable 48-frame/9-layer PXO compositions. Original 52-pose native sources remain referenced read-only. New runtime exact profile pins set/provenance/52 source PNGs, transition and phase PNGs. The model, speed140, physical stop and inclusive120ms settle are unchanged. All 24 outgoing phase selections and switch boundaries pass (449 predicates). Old profiles still accepted and altered/missing packages refuse without target mutation.

## Evidence

- Independent source checker: outputs/hsea-stop15-root/rpg-2-star-ocean-the-second_heroine-sea_phase-stop-independent-source-check_v01_20261021-014426-c6c468d8.json (all11 structural gates; no art claim). Six copied positive/negative fixtures pass, including bad hash/missing phase/protected idle/path traversal/malformed JSON, no traceback or input mutation; root receipt under outputs/hsea-stop15-root/*checker-fixtures*.json.
- Old/new normal movement: before013730-5cfeb209 / after015624-dcd47342, cityEN30 and interiorZH60 each134/214checks,103/199trace entries. Position/action/facing/model diagnostics/settle timing exactly equal, only presentation sample/set IDs differ. Separate normal1x MP4s and critical PNGs under outputs/hsea-root09.
- Combined proof: outputs/heroine-path16/rpg-2-star-ocean-the-second_heroine-playable-path_combined-root-proof_v16_20261021-020115-6f145c72.json, en104/zh104 checks, 250-frame1280x720/30fps normal1x MP4 each. Real HP/damage/cooldowns/AI; no direct _try_attack/_finish_battle, source pose injection or synthetic damage. Setup uses four disclosed safe probe placements plus one70px-left encounter placement. All29 authored combat poses load; ordinary attack contact/recovery, rewards, return and load use normal game logic. All eight actions were separately technically checked in prior source-bound combat evidence; this flow exercises normal attack rather than pretending to trigger every action.
- Root inspected separate live captures for side stop, north/south motion, combat contact and return; browser playback confirms normal1x 1280x720/30fps media loaded (ready4). This establishes visible evidence availability, not full fluidity certification.

## Concrete efficiency changes

Updated existing docs/workflow.md and operating registry: one complete heroine path before roster expansion, short task context, existing packagers/checkers/recorders, changed-scope checks then one combined publication per completed deliverable, deterministic file work without model calls, two unsuccessful revisions trigger a method change. No extra orchestration/metrics platform. Source packaging reused the existing packager. Existing fallback probe gained a phase mode. Combined harness reuses the existing natural-flow script.

Native AVI capture removes per-frame PNG write overhead for the full-path recording; H264 output retains exact250frames/30fps and1x speed. Current combined recordings completed in12.078s EN and10.781s ZH (engine wall time, excluding encode/coordination). This is a measured result for these clips, not a promised project-wide speedup.

## Corrections and failures retained

Root corrected DeepSeek filesystem resource roots (C/data -> C/game/data), added an explicit configure().ok gate, removed unnecessary computed recursive cleanup and retained raw capture evidence. Initial --stamp packager invocation was unsupported and refused before writing; corrected CLI reused unchanged packager. An initial long-path copy failed after registry rename; corrected extended-length file access and completed pins. Native Godot import passed. Entry smoke en/zh reached READY and exited normally with engine quit-after20; fr refused with exit1. Both normal short shutdowns reported2 ObjectDB leak warnings; retained as warnings, not relabeled clean shutdown. Fixture builder refused the initial output basename; rerun under its declared hsea-stopcheck15 root passed. These are not counted as completed production gates.

Raw-hash-bound GDScript/JSON snapshots are staged byte-exact under scoped -text attributes; producer tools additionally declare LF-normalized hashes where their manifests do. Native PXO composition/export equality does not certify clean Pixelorama diagnostics or GUI SaveAs/reopen. No such claim is made.

## Remaining

Front/back legs and arm articulation remain less developed; mirrored west costume, side sleeve contrast/coat texture, broad rest stance and complete normal-speed motion need artistic refinement. Motion is UNAPPROVED and full runtime sprites0/52; accepted environments5/12; human playtests0/2. Generic enemies/NPCs visible in the preview remain placeholders. The opt-in path is technically playable, not final-quality accepted character delivery.

Production54.5%→54.5%(+0.0pp); inspection16.7% and creator approval7.8% unchanged. Existing integration production tasks explicitly require ordinary-game DEFAULT adoption; this opt-in delivery does not meet that gate and scores are not changed. No points per version, screenshot, test or workflow report. Next primary work: complete front/back authored movement in this same heroine path before expanding the roster.

## Integration byte gate

The initial staged-byte check found2 document newline mismatches. Added exact -text attributes and explicitly renormalized only those two selected files; all643 selected files then matched exact staged blob bytes. The reusable selected-stage-byte checker uses2 Git calls and completed in3.703s; it does not stage or mutate sources. This replaces the prior per-file process loop and preserves the same raw-byte comparison.
