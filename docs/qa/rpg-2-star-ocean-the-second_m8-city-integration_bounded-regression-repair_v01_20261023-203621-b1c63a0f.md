# M8 city integration: bounded regression repair

Canonical task: `qa.validation.pre-playtest-regression`, still **TODO**, with every creator dependency and its existing doneCriterion retained. Operational queue boundary: `m8-city-integration-repair`. This repair earns **0 points**. Producer: Claude Code Opus 5.5 through the guarded `controller.py run-provider` adapter, firstParty. Independent reviewer/integrator: Hermes. The audited ledger transfer to Hermes records current technical-inspection accountability; it does not relabel Claude's implementation or historical work.

Base/tested source: `ababe587c3f3504a592dca11e7f966ee946955ec` plus the exact repaired test bytes below. Initial checkout was clean. Only `game/tests/m8_city_integration_smoke.gd` changes game-tree source. No runtime script, default selector, source asset, viewport, canon, approval, task weight or denominator changed. M7's existing repair was not repeated.

## Diagnosis and preserved RED

The coordinator ran the original test through the existing finite checked Godot runner, with Dummy audio. It failed at line69: `CITY_INTEGRATION_FAILED: native pixel actor male`. Original test raw SHA-256: `4cc0e73103130652c90fb4bedbe57a83a037b4d5efefe35a39ee71f8cd477a42`.

Ranked hypotheses:

1. Stale native32x48 fixture — confirmed. The test expected32x48 textures, scale1 and legacy offset(0,-20). Current ordinary creator-authorized defaults draw80x112 density2 frames at scale0.5: male `mexplore23` through `mpath24`, heroine `hsea-front17` through `hsea18/hsea09`, Liang Xu `lexplore28` through `lpath30`. These defaults were already authorized; default use is not final art/motion approval.
2. Incorrect active source — not observed in the bounded checks. The repaired test pins exact registry and referenced set-manifest bytes, expected driver script/parent, set IDs, independently loaded frame arrays, and heroine breathing manifest/frame hashes. It compares both production-loader and driver arrays against the independent oracle. A forged matching set ID with Liang's textures is rejected.
3. Scale, pivot or direction runtime fault — not observed in the bounded checks. Exact native frame80x112, density2, pivot(40,104), scale(0.5,0.5), nearest filtering, centred x, floor1logical pixel below the actor, soles ending on row103 and standing body48±0.5logical pixels pass for both heroes and Liang. The test does not move runtime defaults to satisfy the oracle.

Final test raw SHA-256: `1e0ad13dcbaf242b4db93b0b5c7dd6e726e8bca51678e601a0d8d139cebd4bff`.

## Protected checks

Both ordinary male/Chinese and female/English routes run without sprite opt-in overrides. Every current idle/walk frame is loaded and checked for80x112 size and the floor bound; counts are pinned (idle4/1/4 and walk12 per direction; heroine breathing8 per direction). Existing legacy32x48 idle/walk bank checks remain as fallback-source checks, not adoption of the rejected baseline.

Input starts walking in each direction; each short moving tick must actually move. The expected direction's texture must be drawn. Released input must settle to that direction's idle. `_tick` advances clock-based hero drivers before the host, matching their process ordering; the heroine's distance driver remains advanced by the normal host hook. Short presses remain inside the open plaza rather than accidentally testing a collision stop as walking.

The original hotspot reachability, west-plaza collision, recruitment interaction, NPC+label hiding, exact valid-save position, old-save(82,260)→(82,203.5) recovery/standability and world-map return checks remain. The test additionally requires visible enabled invitation UI and visible NPC+label before recruitment, and active hero source/geometry after reload. The screenshot manifest now records actual captured dimensions instead of the old hard-coded640x360; no viewport setting changed.

## Independent execution on final bytes

All final calls use the existing checked runner with a120-second deadline, required markers, diagnostics gate and Dummy audio. A zero process exit alone is insufficient.

- M8 city integration: PASS `M8_CITY_INTEGRATION_OK`.
- M7: PASS `M7_SMOKE_OK`.
- M1: PASS `M1_SMOKE_OK`.
- City navigation: PASS `M8_CITY_NAVIGATION_OK`.
- City re-entry: PASS `M8_CITY_REENTRY_OK`.
- Xvfb/OpenGL actual M8 render run: PASS,10 separate1280x720 captures, matching manifest.
- Separate-process wrong-set-pin mutant: expected RED at `active hero source male: set manifest bytes are not pinned`, no parser/runtime script error. The checked runner terminates on this intended diagnostic, exit-9; this is negative-control evidence, not a green game run.

Both final positive M8 runs execute the same live mutate/reject/restore predicates used for positive assertions: SOURCE2, SAME_ID_SET2, BREATHING1, SCALE2, PIVOT2 and DIRECTION8 rejections per run. Each restoration must re-accept. Three `M8_ACTIVE_SET_VERIFIED` markers confirm current actor banks were inspected. These controls prove the checks reject wrong source/scale/pivot/direction rather than merely accepting nonnull textures.

## Rendered pixel inspection

Hermes loaded actual PNG pixels, not filenames or headless results. The initial reviewed implementation's full-size Chinese male-south, English female-west and English post-recruitment captures showed legible UI, expected hero/NPC scale and visible ground contact, with Liang and his label removed after recruitment. After the source-oracle followup, Hermes viewed the final10-capture overview and full-size English female-east and Chinese male-east viewports. Text was legible, expected directions/appearances and Liang's label were visible, with no obvious missing glyph boxes or sprite clipping in these samples. The overview also shows post-recruitment removal.

The full final capture set and a review sheet are under `outputs/m8reg63/`. The review sheet is a layout of original frames, not a replacement for the separate captures. The overview was downscaled by the vision loader; only the selected full-size viewports support detailed pixel observations. No continuous-motion/fluidity, intermediate stop timing, final artistic acceptance, Windows runtime or human-playtest claim is made.

## Failed and limited attempts

- Both provider calls returned adapter classification `permission_denied` because some Bash forms were refused. They nevertheless produced edits through authorized tools and executable checks through allowed commands. Adapter exit1 is retained, not reported as success. No permission setting, provider route or billing rule was changed. Independent checks establish the delivered result. No quota depletion, pause or unknown safety verdict was reported.
- Producer202612 and debug202622 attempts failed `walk continues female south` after walking into the plaza edge. Male's bridge initially obscured the same blocked tick. Shortening the press and requiring movement on every tick fixes test geometry, not runtime behavior. Both failure logs and exact reconstructed source snapshots are retained.
- The first coordinator final-suite wrapper mistakenly required M8 negative markers from the navigation test. Navigation's Godot result was green. The wrapper was corrected to exact test labels and the complete final suite rerun; the earlier logs remain.
- Unsupported progress-recorder `--help` and two read-only transcript-parser errors are disclosed in the machine proof. Actual `begin`/`finish` CLI forms and corrected snapshot reconstruction are used.
- The first producer source oracle trusted its driver's own texture arrays. Independent review requested a followup: pin referenced manifests and compare against an independent oracle. The final SAME_ID_SET and BREATHING controls cover this gap.
- The progress CLI begin record was created after the producer's initial test edit, before independent acceptance. The initial unmodified ledger summary had already been read; canonical meters were unchanged in between. It is not claimed to timestamp the start of producer execution.

All hashes are raw bytes, with no text normalization. The machine proof binds the original/final tests, both provider receipts, all preserved failure logs/reports/source snapshots, commands, final results, screenshots and the tracked game-source/asset hash manifest. Native PNG bytes are bound in that source manifest; the smoke test itself pins set paths/metadata but does not add per-frame PNG pins to male/Liang manifests. Intermediate authored stop-bridge timing is outside this bounded repair. This is not the frozen full all-tests regression.

## Progress and next boundary

Production61.0% →61.0% (+0.0pp); performed inspection21.6% →21.6% (+0.0pp); creator approval7.8% →7.8% (+0.0pp). No human gates or points changed. Full `qa.validation.pre-playtest-regression` remains TODO.

Machine proof: `outputs/m8reg63/rpg-2-star-ocean-the-second_m8-city_regression-independent-proof_v01_20261023-203621-b1c63a0f.json`. Integration proof is recorded separately after the scoped commit/push and remote verification. No hosted Site publication or broader GitHub credentials are used.

Next action: continue the existing pre-playtest regression inventory on current ordinary defaults, recording the next actual failure as a separate bounded contract. Do not infer all Godot tests green or bypass the frozen creator dependencies from this M8 result.
