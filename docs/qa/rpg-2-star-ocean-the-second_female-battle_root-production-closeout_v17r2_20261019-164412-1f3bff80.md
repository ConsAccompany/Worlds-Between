# Female battle still v17r2: complete still revision, not animation acceptance

Task `content.combat.protagonist-female.combat-static.revision`, Claude production, Codex independent integration/inspection. Standing creator rejection: v16 was “way too coarse, her face is not even recognizable”. This revision completes the denser v17/v17r1 method with deliberate body finishing; it does not repeat the rejected32×48 method.

## Deliverable

One136×144 native still, logical68×72/pin32,68, apparent0.65 proportion retained.25editable roles, genuine one-frame PXO and ORA, native PNG, separate protected face/hair crop and manifest/source. Face/hair rows0–44 and soles/padding132–143 remain exactly v17r1;1063body texels changed.44existing palette colors, no new glow, automatic filtering or noise. Coat shoulder/underarm/waist/tail planes, glove shape, boot ankle/toe/heel and pack restraint were authored in one finishing pass. No game default, animation, formation, collision or movement change.

## Root evidence

- Re-ran source build/check in canonical integration:20/20. All frozen output bytes deterministically rebuild, source and input hashes declared with explicit LF normalization for text.
- Independent native/render proof:53/53.25PXO raw roles equal ORA roles; their composite and ORA merged image equal the native PNG. Protected head/sole rows remain exact.
- Fresh checked-runner Godot captures from current e80ba09 code in actual1280×720/640×360logical viewport: bright/default and outdoors/outskirts, both English and Chinese; normal party positions135,171,207,243 retained. Every one of399opaque face-box texels is exact and unoccluded in all four scenes.110body/weapon texels differ only because of independently rendered later companions; all110match the exact occluder matte/color, with zero unexplained mismatches. No changes outside hero bounds; UI positions and normal168px/s battle input unchanged.
- Root personally viewed both full gameplay scenes and enlarged native still: coat planes and boot cuffs/toes are clearer; the face survives at the native1280 backing. The face remains stylized, posture stiff, and the blade tip remains partly behind a companion.640backing necessarily loses the finer sub-logical detail. These limitations are not hidden or converted into an approval claim.

Primary final capture folders: `outputs/battle-static-v17r2/root-default-v02-20261019-164412-1f3bff80/` and `root-outskirts-v02-20261019-164412-1f3bff80/`. The two-color images in `diag-occl` are MASK-ONLY diagnostics, not gameplay visuals. Actual full images are the `injected_test-only` files. Root reran with lowercase descriptive filenames; no asset or visual threshold changed.

Root checker initially stopped before image comparisons because normal Windows paths exceeded MAX_PATH. It now uses extended paths; the53successful checks are from that corrected reader. No source-art criterion was relaxed.

## Native application limitation

Producer Pixelorama reopening/export reports25/25exact role layers from each of PXO and ORA, with source files unchanged. `nativeExactExport=true`, but `cleanApp=false`: PXO logs four shader diagnostics; ORA additionally reports tree/cleanup/resource diagnostics. GUI Save As/reopen remains unverified. Root independently reconstructs all native layer bytes rather than treating exit0 as a clean application pass. The diagnostic report is preserved separately; native format equality does not erase these application failures.

## State

This delivers the fixed revision bucket with production QA; repeated future versions earn no additional bucket. Codex verdict: technically complete still candidate ready for scoped creator review, with the stated overlap/density limitations. Creator acceptance is still pending. No combat actions are authored from it before creator baseline acceptance. Full runtime sprites0/52, accepted environments3/12, human playtests0/2 and formal acceptancefalse remain unchanged.
