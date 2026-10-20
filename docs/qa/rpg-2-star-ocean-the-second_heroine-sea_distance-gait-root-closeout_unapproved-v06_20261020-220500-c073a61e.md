# Heroine distance gait / source revision: independent root closeout

Recorded 2026-10-20T22:05:39.240484+00:00. Base e93cf501f7ae44cab2a2a0e44ad1f4c18eb708c4; integrated SHA is recorded by the serial metadata closeout. No default adoption, art acceptance or full motion certification.

## Ownership and deliverable

Claude authored v04 then side-only v05/v06 source methods. DeepSeek produced a pure actual-displacement phase model and synthetic tests. Codex defined/integrated the opt-in adapter, independently tested and corrected timing, measured the actual game traces, and owns publication. Creator approval remains separate.

The useful finished boundary is an OFF-DEFAULT, female-only, exact-package distance driver plus a measured side-gait improvement. All four directions have 1idle +12walk=52 source PNGs,16 supplemental bridges,4 PXOs with17frames/7layers,4 idle ORAs. South idle0 remains exact6bf1d688487bd3fcc71eeb2e7c9b7c74f1fe6b6cd6362860b7fa0d42e009e429. North/south and all idle frames remain v04 byte-identical (28/28); this is not a fully polished four-direction set.

Runtime selector: --heroine-sea-distance-pilot plus --exploration-sprite-set-registry=res://data/hsea-gait11/rpg-2-star-ocean-the-second_hero-female_exploration-sprite-set-registry_runtime-v01_20261020-175959-c31e4a79.json. Defaults and host speed140 remain unchanged. Actor protagonist-female only. Only four opt-in hook lines were added to the generic adapter; no host movement/collision/camera/interaction changes.

## Measured actual before / after

Same normal-input routes, same positions, same facing/frame/phase traces were verified byte-value equal between v04 and v06. Independently decode each PXO near/far leg's lowest opaque row midpoint, then compute world x = host x + (sole x - pivot40)/density2. Sample side stances separately by walking segment, direction, cycle and foot; no settle/turn samples mixed in.

- City EN30fps: max sampled stance-foot world-x range12.9165 →3.3334 logical pixels.
- Interior ZH60fps:14.9167 →3.6667 logical pixels.
- See outputs/hsea-root09/rpg-2-star-ocean-the-second_heroine-sea_stance-drift-root-proof_v01_20261020-220341-15a8a67b.json.

This is sampled geometry over actual gameplay traces, not optical-flow proof, continuous foot lock or artistic fluidity certification. Discrete12-pose stepping leaves residual drift; front/back slip was not solved. The interior is not a validated dark context.

## Source methods and inspection

v04 segmented rotations were source-format-valid but failed the art brief: weak arms, too-short planted sweep and knee artifacts. Preserved as a diagnostic baseline, not promoted as an improved visual.

v05 fixed-length IK met the requested sole trajectory but visibly crouched with blocky boots. This was caused by Codex's supplied rig geometry; it is not an accepted method. Its editable source remains in the producer checkout outputs/hsea-gait10 and was not integrated.

v06 changes the method to authored side-leg pose guides with controlled foreshortening and original leg-texture/boot pixels. Stance soles sweep48source pixels to offset24logical travel per step. Root viewed separate source poses0/3/6/8 and actual game captures. Crouch/stubs improve; the leg spread is stretched, shin texture is busy, far-leg shading is simple, arm swing remains weak, north/south are not polished, and the final settle-to-idle pose may pop. Only a technical candidate: not ready for creator motion acceptance.

Source outputs/hsea-gait11/src-v06-20261020-175838, manifest SHA256c723d3a813b0291a8674c6c9b13ae29b49c2a7866f10d6ddf72296858db1ac7b. Old v04 source outputs/hsea-gait09/src-v04-20261020-180500. v04's180500 is an authoring tag, not a truthful session end time; actual provider times are retained locally. The producer's initial28-minute narrative was contradicted by its307.329-second receipt and is not used.

## Code and strict source binding

The phase model uses actual post-collision Euclidean displacement /48logical per cycle; no wall-clock walk-in-place, no engine movement mutation. Same-facing re-press continues live phase; turns reset incoming phase and do not preserve foot identity. Visual settle consumes the first stopped tick and ends within120ms; physical stop is immediate. Two authored bridge poses are selected inside that window, without alpha interpolation or an added timer.

The adapter pins the exact source-set JSON, provenance JSON and all52 source PNG hashes plus the supplemental transition JSON/16bridge hashes before changing any target field. Wrong variants cannot mix with new bridges. A byte mutation in either bridge JSON or a PNG and the old v04 package all refuse whole with unchanged texture/transform/children; finally blocks restore original bytes.

Root found the final producer model skipped the first stopped delta, violating inclusive120ms timing. Its untouched final model and failing report are preserved under outputs/hsea-model09. Root retains the earlier inclusive-time implementation and fixes one completed-settle diagnostic that used a cleared start value. Two producer assertions were corrected to distinguish cosmetic phase progress from actual-distance progress; thresholds were not relaxed. The original fixture/runner are historical snapshots, outside active tests.

## Evidence and failures

- Root77 boundary predicates: final-stop-boundaries log; inclusive .04+.08s stop, no skipped frame, no invalid-state mutation, independent instances, preserved re-press phase, final diagnostic.
- Full corrected synthetic suite2204/2204, clean checked run: full-model-suite-corrected log. Synthetic, not gameplay.
- Native normal game: city82checks/107frames at30fps, interior118checks/203frames at60fps. Real input, fixed initial placement270/235, no hidden hero or disabled host. Normal1x movies are separate. Final combined report: outputs/hsea-root09/rpg-2-star-ocean-the-second_heroine-sea-distance_combined-root-proof_v01_20261020-220030-0b3a34af.json. It pins the actual driver/model/hook/harness source bytes, registry and video hashes.
- Generic legacy adapter12/12 regression includes flag-off zero data reads, unchanged target and old frame-clock/boundary behavior.
- New valid attachment9/9; source refusal3cases,7checks each. Original bytes restored.
- Root source137/137 checks: native cells/alpha/borders/floor/idle, source hashes, all17 PXO frame/layer reconstruction. Producer139/139 additionally includes deterministic rebuild; native Pixelorama GUI save/reopen and native-app diagnostics were NOT established.
- Producer's2204 numeric assertions passed, but its checked-run failed on a startup certificate-store ERROR. Preserved, never filtered or counted as a passing gate. Root's corrected suite under the normal local profile had no ERROR/SCRIPT_ERROR. No security setting was changed.
- Root's first boundary command used a wrong relative script path and failed; retried with an absolute path. One runner compile attempt used the wrong worktree and did not find its file; corrected. Root's first drift analysis assumed a producer metadata key; it failed before reporting, then was replaced with independent PXO leg-layer decoding. Failed logs retained where emitted.
- v04 earlier actual-input diagnostics bind their script/model snapshots under outputs/hsea-model09; they are distinct from the final v06 tested sources.
- Raw hashes are raw bytes unless explicitly marked text-LF. Scoped attributes preserve new hash-bound artifacts; staged bytes are checked before commit. The existing generic script retains its preexisting raw-byte attributes.

## Completion scope and next work

Production53.6% →53.6%(+0.0pp), inspection14.2% unchanged, creator7.0% unchanged; fullsprites0/52, scenes3/12, timed humanplays0/2, formalfalse. These repair already-credited source/runtime tasks; no per-version points or new denominator.

Next: authored full-body arm/shoulder/scarf motion and front/back leg placement using the side stance contract as a reusable production reference. Clean stretched contact poses/shin noise and the final idle handoff. Evaluate normal-speed start/run/stop/repress/reversal and genuine bright/dark contexts before presenting a complete set. Do not restart metric-only parameter searches or re-use rejected crouched IK.
