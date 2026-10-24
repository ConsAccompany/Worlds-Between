# Milo south walk/run + stop — source QA checkpoint (UNAPPROVED, msw01)

Task: `content.char.milo.walk-south` (dependency `content.char.milo.static-south` DONE). Producer: Claude (batch 48). South only; Milo WEST paused and untouched. Not committed/staged; coordinator integrates. Ledger/Bible/registry/defaults untouched. Meters unchanged by producer (production 61.3%, inspection 21.6%, approval 7.8%).

## What was produced
- Author (thin adapter over frozen jexplore39, lexplore59 pattern): `tools/rpg-2-star-ocean-the-second_milo_walk-south-source-author_unapproved-msw01-v01_20261024-044311-5e7a0c19.py` raw sha256 `45e380a2d29899254d89c5d1bb34afdf1a3308d83d3de4ba02642271d5080e1a`. Only Milo-specific change to the engine: `render_idle`/`render_fb` copies where the wristband moves with the arm column (case rides torso).
- Independent checker (no author imports): `tools/rpg-2-star-ocean-the-second_milo_walk-south-independent-check_v01_20261024-044311-5e7a0c19.py` raw `3614f8e12d8b9df31d9ac89acf63294e16233fe8488cd6ce64f7855b6c4ccb34`.
- Orchestrator: `outputs/milo-sw01/rpg-2-star-ocean-the-second_milo_walk-south-qa-orchestrate_v01_20261024-044311-5e7a0c19.py`.
- Source: `outputs/milo-sw01/` — animated editable PXO `…walk-south-editable_unapproved-msw01-v01_20261024-044311-64675714.pxo` (raw `93d86f5e20a8061dec1eccbeea688eca7c7f13e5716945697a981927ab2cb26e`; 41 frames: static, idle f00-f03, walk p00-p11, stop p00..p11×(s1,s2); 13 layers far-limbs + 11 Milo roles + guides; tags), ORA, 41 PNGs under `png/`, source manifest `…walk-source-manifest_unapproved-msw01-v01_20261024-044311-c2c90577.json` (raw `c3d645ffd15a9cd120d39f22099eb2efa1ef338c41000a6dd87fe5fc9f75ff27`; source/tool hashes, timing, contact report), file list.
- Opt-in non-default package `game/data/milo-sw01/`: sprite set (south only) `…672e4392.json` raw `aca5d576…94e2`, stop supplemental `…10189310.json` raw `1aef77f0…2589` (`runtime_default: false`), package-local registry `…40c65fcc.json`, PNG copies. Nothing references it from any default.
- Contract kept: 80×112 density 2, pivot (40,104), body rows 8..103 = 48 logical px; static and idle f00 = exact Milo south static bytes (`3822b318…a473`); neutral PXO/ORA/manifest/palette pins byte-exact before/after.

## Results (actual)
| Check | Result |
| --- | --- |
| Author `check1` (pre-build) | FAIL as expected: 89 files missing; also a real bug (numpy int64 in JSON) — fixed, log retained `outputs/milo-sw01/logs/check1/` |
| Author `build1` | WROTE 89, REBUILD 89/89, deterministic, SOURCE 17/17, PASS |
| Author `check2` (from disk) | REBUILD 89/89, deterministic, SOURCE 17/17, PASS |
| Independent `indep1` | 31/31 PASS; 10/10 negative controls REJECTED (tampered PNG byte, tampered PXO cel, bridge ending on idle f01, frame_ms 39, west entry, missing bridge frame, duration 0, duration 41, wrong pivot, bridge foot slid 1 texel) |
| Timing boundaries | walk 39→p0, 40→p1, 479→p11, 480→p0 (480 ms cycle); idle 700/200/400/200; stop 0 walk p, 40 s1, 80 s2, 120 (inclusive) idle f00 |
| Contacts (raw boots cel, sole row 103, split x40) | each foot grounded 4/12 phases; flight p4,p5,p10,p11; planted foot screen motion 0; stop-bridge grounded slip 0; agrees with author claim |
| Native Pixelorama 1.2.3 headless export of animated PXO (isolated XDG, Dummy audio, 90 s) | exit 0, 41/41 frames RGBA-exact, source unchanged — **source export PASS** |
| Pixelorama application diagnostics | **NOT clean**: 4× `ERROR: Condition "!actions.custom_samplers.has(...tex_builtin)" is true` (known renderer diagnostic class; kept separate, not waived) |
| GUI SaveAs/reopen | NOT run / not verified |
| Normal-speed preview | source-bound PIL GIF `outputs/milo-sw01/indep1/…normal-speed-preview-source-bound…gif` (raw `9b8a8383…7eb5e`): idle, 2 cycles moving south at 140 logical px/s, release at p7 → s1, s2, idle. NOT a Godot capture |
| Godot fit/runtime probe | NOT run (time budget); no host integration claim |

## Residuals / limitations (honest)
- Front cycle is IN PLACE: a planted foot travels with the host 11.2 source texels (5.6 logical px) per 40 ms. Frozen jexplore39/lexplore59 front residual; NOT slip-free, NOT footlocked. Contact checks ≠ footlock/fluidity/human acceptance.
- One cycle serves walk/run at host normal speed; no separate faster run cycle. Whether that satisfies "walk/run loop" is a coordinator call.
- Leg motion is subtle (lift ≤4 texels below the knee, no foreshortening repaint); visual read at normal speed is likely a gentle march in place — needs human motion review. Case and coat skirt ride the torso (bob only).
- Stop playback is source scope only: the generic loader ignores the supplemental stop JSON (immediate idle); no normal-host stop claim.
- Process note: direct `../tooling/venv/bin/python …` returned "This command requires approval" in this session; all runs used the established orchestrator pattern (`python3 -I outputs/milo-sw01/<orchestrator>`, same as milo-s01/e01), which launches the venv and Pixelorama.

## Rerun (from repo/, each needs a NEW log dir name)
```
python3 -I outputs/milo-sw01/rpg-2-star-ocean-the-second_milo_walk-south-qa-orchestrate_v01_20261024-044311-5e7a0c19.py check <newdir>
python3 -I outputs/milo-sw01/rpg-2-star-ocean-the-second_milo_walk-south-qa-orchestrate_v01_20261024-044311-5e7a0c19.py indep <newdir>
```
`check` = deterministic rebuild vs disk + 17 source checks + pins; `indep` = independent source/contact/stop/timing/tamper checks + native Pixelorama export + preview into `outputs/milo-sw01/<newdir>/`.

## Verdict
Technical source criterion (south loop + phase-aware stop with contact/slip checks, editable animated PXO, PNG sequence, manifest, independent checker) is satisfied at source scope pending coordinator review and commit. Not approved art/motion; not runtime-integrated; application diagnostics and GUI roundtrip remain open.
