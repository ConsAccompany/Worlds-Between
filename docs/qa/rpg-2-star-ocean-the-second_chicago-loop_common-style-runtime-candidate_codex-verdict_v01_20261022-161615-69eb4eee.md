# Chicago common-style playable candidate: Codex verdict

## Scope and ownership

- Creator decision: **“采用这个统一方向继续制作”**; [docs/design/rpg-2-star-ocean-the-second_science-scenes_common-style-direction_approved-v01_20261022-161615-69eb4eee.md](../design/rpg-2-star-ocean-the-second_science-scenes_common-style-direction_approved-v01_20261022-161615-69eb4eee.md). Scope is shared science-scene material/light direction only, not default use, final art acceptance or human playthrough.
- Existing task: `content.scene.chicago-loop.native-pass.revision` (Codex accountable, Claude source assembly, Codex independent inspection/integration). The existing revision bucket was reopened and is closed only after this verified package. No new version points or denominator change. `content.scene.chicago-loop.native-default` stays blocked until separate authorization.
- Tested base: `6d1e6d23db9eb9b4717d4137ee34666ab7b8d963`. Exact hashes and unchanged scope: `outputs/style42/root/rpg-2-star-ocean-the-second_chicago-loop_root-protected-and-package-proof_style42-v01_20261022-161615-69eb4eee.json`. Package manifest: `outputs/style42/rpg-2-star-ocean-the-second_chicago-loop-style42_native-manifest_unapproved-v01_20261022-161615-69eb4eee.json`.

## Delivered result

One native-resolution640x360 separately playable scene, seven raster art planes plus hidden walk guide, editable primary Pixelorama and supplemental OpenRaster, native flat and seven lossless runtime textures (ground, five foreground groups, reveal mask). A deterministic source-assembly builder pins the generated reference and old source hashes. The current ordinary heroine package is reused; no character art/motion change.

Visible color/material pixels are nearest samples from the approved1672x941 generated reference, with73057 unique colors. This is **reference-derived raster scenery at native game resolution**, not hand-authored pixel clusters, independent vector objects or a newly native-authored painting. The actor-free image exactly reconstructs the sampled reference. Under opaque props,38388pixels use existing old-style v05 ground. The five foreground masks retain old silhouettes,26prop regions/pivots, original walk and reveal masks. Original scene logic is semantically exact except comments and texture path; a new separate scene avoids changing any existing ordinary default.

## Independent checks and actual Godot evidence

- Builder canonical rebuild/check:14/14files equal after the Windows long-path fix. Producer's manifest marked provenance manifest absent; canonical rebuild truthfully marks it present and refreshes source hash. Original producer manifest and builder snapshot retained.
- Codex independent package checker:90checks pass (all file hashes/nativePNGdimensions; ORA canvas, per-plane composition and merged image; PXO raw cels and preview; exact reference sampling; original foreground alpha, walk/reveal masks,26props/pivots and geometry; six-plane runtime composite). Three negative predicate fixtures refuse wrong size/alpha/hash. No producer code is executed to establish the new pixels; old author is imported to establish protected geometry.
- Native Pixelorama headless reopen/flat export produces exact native image. **Application-clean gate fails** with4diagnostic lines; exit0 is not a clean-app pass. Raw log retained. GUI SaveAs/reopen is unverified. ORA structure/composite/cels are checked independently; native ORA app export was not claimed.
- Checked Godot import passes. Old v05 control:161checks. First candidate pass:161checks. Final EN and ZH:173checks each,24actual640x360 captures, no Godot errors. Exact root probe uses a declared test-only in-memory scene handover and policy preview, starts a new game, uses actual map departure, held movement, interact events, return button and ordinary heroine driver. It does not edit disk selectors or claim ordinary default adoption/human play.
- Tests sample all230400collision coordinates against the original; protect exact spawn/sites/radius/26prop regions/pivots/labels/material paths; confirm flight charges time, walking does not, three localized notes open/close after held-input approaches, column and two tree occlusion/reveal transitions, world-map return and no extra goal credit. Three approach starts are explicitly positioned fixtures, not claimed end-to-end human walks.
- All2548protected tracked game scripts/scenes/data remain byte-identical; seven new textures and one separate scene/script are additional assets only. All four existing scene default switches remain false.

## Codex visual judgment and remaining limits

Viewed the final native English/Chinese entry, column occlusion/reveal and west-tree occlusion/reveal captures. Warm masonry, amber shop light, richer metal/foliage and restrained teal match the approved direction more closely than the earlier flat geometric scene. Heroine and localized UI remain readable.

This is a **technically playable MVP candidate, artistic approval pending**.15/26edge-correlation regions show a1–4pixel best offset; this diagnostic is disclosed, not a quality pass/fail threshold. Old alpha equality does not prove generated-object silhouette equality. Minor rim mismatch and old-style clean-plate pixels can appear through the reveal window, particularly vegetation. Further polish is deferred only if the creator authorizes this candidate for MVP; no final art endorsement is inferred. Keep original art and rollback path.

## Failures and coordination

- Host turn cancellation stopped the first two processes before outputs; no quota or credit exhaustion was reported. Their absent PIDs were verified before bounded redispatch.
- DeepSeek support attempted redundant Python/dependency installation rather than writing its bounded checker; Codex stopped that owned process and excluded its environment changes. No DeepSeek validation pass is claimed. Codex supplied and ran the independent checker using the existing runtime.
- Claude's bounded420s session ended after assets/builder and its checks, before a final message; artifacts are independently inspected, not trusted from exit status. No reset alarm or usage depletion is inferred.
- Initial root builder failed on a Windows long input path. Root changed only path I/O handling, preserved original source snapshot and rebuilt exact visible/native assets.
- First root parser invocation used a project-relative tool path and failed before loading; raw log retained. Absolute-path parser check passed. Initial log-directory creation failure produced no Godot run. No test thresholds or game mechanics were weakened.

## Default-use decision prepared, not applied

A two-file prepared patch changes only the Chicago policy fallback target to this new candidate and enables its existing policy bit. Explicit old opt-in flags still target old assets; NYC/Washington switches remain false. Patch is stored as `outputs/style42/root/rpg-2-star-ocean-the-second_chicago-loop_default-adoption-patch_prepared-never-applied-v01_20261022-161615-69eb4eee.patch`. Default use requires creator authorization after seeing actual gameplay. If approved, apply only that patch, recheck ordinary map arrival and rollback, and finish the existing two-point default task. Final scene acceptance and human playtests remain separate.

Production before59.9%; reopening the existing six-point revision temporarily showed59.7%. Closing this delivered revision restores59.9%: **59.9% →59.9% (+0.0pp)** across the full batch, not new points. Inspection20.6%→20.6%, approval7.8%→7.8%. Full sprites0/52, accepted scene art5/12, humanplays0/2, formalfalse. No scene count is added for direction approval or this candidate.
