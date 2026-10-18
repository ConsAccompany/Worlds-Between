# Yonkers antenna corridor v07 — bounded technical closeout

**2026-10-18. UNAPPROVED environment revision, NONRUNTIME, test-only.** Produced by Codex during a Claude quota gap, as explicitly authorized. This updates the existing revision deliverable; it creates no new per-version points, creator acceptance or default adoption. The creator's accepted environment count stays 3/12, complete sprites 0/52 and human playthroughs 0/2.

## Source and bounded method change

Producer branch: `codex/yonkers-structural-material-v07-20261018`, base `36591d7daefc05347e3de4841d0fa9c1adf610f7`. The existing 379 changed import files were preserved; no pre-existing functional source was changed. `survey_annex.gd` was independently compared with canonical `f6d9e20` and was identical.

The v06 review requested changes for large flat wall fields, pale bases and a rigid three-pad layout. Rather than add noise or increase line density, this pass reads the committed v06 native ORA layers and uses a small reusable material kit:

- Authored structural bays with broad header undersides and left/right recess returns under consistent upper-left light.
- Broader calm stone/concrete clusters, limited existing palette, without random pixel marks or resampling.
- One continuous service surface joining the fixed stations; no uniform six-part floor grid.
- Aged pedestal tops, fronts and turned side faces, with contact-shadow clusters.

Root first inspected actual bilingual entry captures before long validation. Its first response requested one bounded light/volume correction within v07. That correction is the final bundle tagged **`20261018-220210-4d281c37`**. Earlier local drafts tagged `215722-7a10f835` are excluded from the selected package. No v08 or further micro-iteration was started.

## Final source and captures

Final package: `outputs/yk1-v07_7a10f835/`.

- Manifest: `rpg-2-star-ocean-the-second_yonkers-antenna-room1_structural-material-manifest_unapproved-v07_20261018-220210-4d281c37.json`.
- Native sources: `…_structural-material-layers_unapproved-v07_20261018-220210-4d281c37.ora` and `…_structural-material-editable_unapproved-v07_20261018-220210-4d281c37.pxo`, 13 editable layers at 640×360.
- `exp/`: final plate, three antenna crops and foreground. These are not under `game/` and are not the game's defaults.
- `cap/`: the corrected zh/en actual entry captures root judged, ending `220210-4d281c37`.
- `cap-final/`: 30 final actual Godot captures, 15 per language, including entry, approaches, interactions, traversal, occlusion probes, runtime heroine and room-2 return.
- `control-v06/`: two selected native entry controls from a fresh run of the committed v06 candidate. Both full candidate/control runs produced 30 captures; only these two control images and the full control log are needed in the selected evidence package.

The material manifest binds assets and author/kit code hashes; the runtime report binds the final 30 captures and both runtime logs. Code uses SHA-256 with explicitly normalized LF line endings; PNG/ORA/PXO evidence uses byte hashes. The evidence-package manifest additionally binds all selected source, checks, QA and media.

## Checks actually run

| Check | Result |
| --- | --- |
| Source/native package | **18/18 source/export checks only**: final asset/source hashes, 13 native layers, declared palette, binary alpha, exact flat/exports, PXO layer bytes, protected masks/anchors, real Pixelorama export |
| Protected layers | Sky, wall kit/ivy, walkway/grating/trench, doors/sidewalls, front parapet and foreground remain byte-identical to v06 |
| Protected alpha/anchors | All three antenna alpha masks and foreground alpha remain exact; antenna anchors `(163,210)`, `(320,210)`, `(477,210)` and crops `[x−64,58,128,152]` unchanged |
| Pixelorama 1.2.3 official CLI | Both PXO and ORA opened and exported: 13/13 split layers exact for each, flat exports 0 differing texels, sources unchanged. Isolated temporary APPDATA; zero real preference changes and zero GUI autosave exclusions in the final run |
| Actual Godot candidate and v06 control | Both exit 0 under fixed 60fps. Candidate injects only its five final textures into the normal survey scene in memory; no game file is replaced |
| Targeted runtime evidence | **7/7**: final injection, clean logs, required interaction/transition checks, 14 collision cases, fresh control parity, 30 native captures and exact bilingual entry pixels |
| Fresh-control behavior | **42 lines identical**, including positions, anchors, HUD/captions, collision stops, lane movement, slide/escape, reachability, six clues and three transitions |
| Entry pixel proof | Protected non-UI comparison masks against the final v07 native composition: zh 150,477 pixels and en 149,065 pixels, 0 differ. Each mask includes 11,753 antenna texels, 0 differ. This is not a whole-scene v06/v07 zero-difference claim |

The collision runner is inherited from the committed v06 harness instead of copying its large implementation. Its `YK1_V06_*` lines name the **check protocol**, not the candidate art version. The new `YK1_V07_INJECTED` marker, manifest, native pixels and `YK1_V07_CAPTURE` paths bind the actual v07 assets. The inherited dish depth probe reports the existing `behind_hidden_px=-1` sentinel; no positive dish-hidden-pixel measurement is claimed. A/C and front visibility checks remain as in the control.

The original inherited Pixelorama helper recorded export parity and exit codes but discarded native stdout/stderr. A final bounded diagnostic rerun saved all four logs. **Native diagnostic status is `errors_present`, not clean**: PXO split/flat logs contain shader `custom_samplers` errors; ORA split/flat also contain `get_child`, `is_ancestor_of`/control ancestry errors and shutdown object/resource leaks. All four commands exited 0 and still exported exact pixels. These errors are neither whitelisted nor treated as passed diagnostics. The 18/18 figure covers only the named source/export checks; native application reliability and native GUI Save As/reopen remain unresolved. Godot gameplay logs are separate and clean. The final source/native report lists every detected diagnostic line and links the four raw stdout/stderr logs.

The first short capture attempt incorrectly looked for `SaveStore` as a root autoload and produced a script error. That attempt was stopped. The harness was corrected to the existing static `SaveStore.root_path` API; subsequent first captures and final candidate/control runs completed cleanly. The failed attempt is not counted as a passed check.

## Root visual verdict and remaining limits

Root viewed the corrected **actual English** entry image and accepted the bounded source/native/runtime **technical closeout only**: header/jamb depth and darker bases read better, the service floor is calmer, and station layout remains legible.

**Art verdict remains `changes_requested` against the accepted room's finish.** Broad concrete faces and the repeated station/grating rhythm still read schematic. This is not a final-ready visual or a request for creator acceptance. Fixed functional geometry was deliberately preserved; no attempt was made to move the stations. The source format was tested with Pixelorama CLI, not native GUI Save As/reopen. Entry images show the approved 48-logical-pixel female south static only as a scoped reference; they do not approve character motion or complete sprites.

All testing was targeted to the revised scene and its preserved control. No unrelated whole-game regression, default adoption, ledger update or Site publication was performed by this workstream.
