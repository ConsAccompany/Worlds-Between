# Female south locomotion v02 — Codex motion review

**2026-10-16; unapproved, nonruntime.** Viewed the actual browser playback of the generated Godot-capture GIFs at realtime 1× and follow-camera 3×, plus sampled 1280×720 Godot still captures. This is an independent visual judgment, not creator approval. The technical QA note is `docs/qa/rpg-2-star-ocean-the-second_protagonist-female_south-locomotion-compact-v02_part-compositor-zero-slip-run_qa-note_m8-w05_20261016-200500-4993d9e9.md`.

Evidence viewed:

- `outputs/rpg-2-star-ocean-the-second_annex-dark_protagonist-female-south-locomotion-compact-v02-preview-walk-60fps-realtime-1x-h48_m8-w05_20261016-211456-07c96521.gif`
- `outputs/rpg-2-star-ocean-the-second_annex-dark_protagonist-female-south-locomotion-compact-v02-preview-walk-60fps-follow-3x-realtime-h48_m8-w05_20261016-211456-07c96521.gif`
- `outputs/rpg-2-star-ocean-the-second_annex-dark_protagonist-female-south-locomotion-compact-v02-preview-stop-r032-ph13-realtime-1x-h48_m8-w05_20261016-211456-07c96521.gif`
- `outputs/rpg-2-star-ocean-the-second_annex-dark_protagonist-female-south-locomotion-compact-v02-preview-stop-r036-ph32-quarter-2x-h48_m8-w05_20261016-211456-07c96521.gif`
- `outputs/rpg-2-star-ocean-the-second_annex-dark_protagonist-female-south-locomotion-compact-v02-still-keyframe-phase-48px-h48_m8-w05_20261016-211456-07c96521.png`

## What is visibly better

The v8 hair, teal scarf, face and coat remain recognizable during movement. In the realtime preview, the feet no longer make the prolonged backward skating seen in the earlier walk attempt. The planted-foot and stop metrics in the technical note are consistent with the sampled GIF frames, although visual inspection alone cannot prove the reported zero-slip measurement.

## Remaining visual blockers

1. At the game's ordinary viewing size the action reads as a rapid high-knee run. The legs travel much farther and faster than the nearly fixed head, shoulders and arms; this makes the torso feel carried by a separate lower-body animation. The enlarged follow-camera preview makes the repeated thigh rows and compressed rear leg especially apparent.
2. The landing and airborne phases have no contact-shadow cue. In the bright stone-floor preview, the rear boot sometimes reads as suspended over the floor. At 3× the sole/boot shape also turns into a small dark block under the knee.
3. The static idle identity is strong, but the long forward boot occasionally extends the silhouette below the previously approved 48-logical-pixel standing height. Motion can extend past idle, yet this must be checked against collision and neighboring props in a real playable scene before treating the 48-pixel scale as preserved.
4. A representative stop GIF shows a short extra settling step before the v8 idle pose. It is smooth enough to avoid a hard pop, but does not yet have an authored weight shift through the torso and scarf.

## Direction for the next pilot

Keep the source-locked v8 identity and planted-foot improvement. Prototype **one** more south-facing motion at the actual exploration camera: reduce the high knee / airborne share, move shoulders and scarf with the stride, add a small contact shadow or equivalent ground cue, and hand-author the compressed thigh and boot silhouettes in the worst key poses. Review a 640×360 scene capture at realtime speed before producing any other direction or character. If the current 140 logical px/s speed prevents a believable walk, treat a deliberate run as its own locomotion state; do not relabel this as a walk. No runtime integration or art acceptance follows from this note.

Completion meter unchanged: full runtime sprites **0/52**.
