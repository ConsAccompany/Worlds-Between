# Chicago State/Lake v06: one completed native material revision

Completed 2026-10-18T17:35:31-04:00. Base `c1a6ab3e40f679d28a6bac45f5ac7f25d0d210c2`; source began as interrupted Claude v06 work and was finished by Codex under creator authorization. No Claude/model, cloud-credit or paid calls were used in this finish. This is a **completed production revision**, **unapproved art**, **nonruntime candidate**. No progress ledger, approval count, Site or remote changes are included.

## Bounded visual changes

The inherited v06 source adds upper-left material/depth cues to the facade and elevated structure: glass reflections, window reveals, cornice shadows, girder flange/web shading, braces, rivet pairs, planter materials and prop contact shadows. Codex made one finishing pass, reducing foreground slab/joint contrast and isolated stone flecks and reducing the repeating small foliage creases in favor of broader lit masses. No concept generation, parameter grid or repeated art search was used.

An inherited v06 foreground-planting silhouette change was found during geometry checks (656 alpha pixels). It was corrected by constraining the finish to the original v05 code-authored silhouette and restoring missing original rim pixels from the unchanged v05 code painter. **All five y-sort alpha silhouettes now match v05 exactly**, as do walk/reveal masks, prop regions/pivots, geometry, spawn, interaction anchors and hero-visibility model. This was a contract repair, not a widened tolerance.

The real v05 scene, selector, shared Loop scene and scene script remain byte-equivalent to the base after LF normalization. No game file was changed by production or capture. The test-only harness replaces six v05 resource-cache textures in memory and shows the new pixels through the real scene renderer, y-sort and reveal shader. The approved female south static at 48 logical pixels is used solely as the same scale reference used by the previous capture harness. No character or environment acceptance is inferred.

## Editable native source and exactness

Native canvas **640x360**. The editable package contains **13 visible layers plus one hidden, locked walk-guide layer**, in both PXO and ORA. Pixelorama 1.2.3 was launched as independent headless CLI processes with fresh APPDATA and LOCALAPPDATA; each independently reopened a copied PXO/ORA and exported all 13 visible layers exactly. The hidden guide stayed hidden, source archives were unchanged and every exported pixel matches the code-authored layers. Existing user editor processes were not selected, controlled or stopped. GUI Save As/re-saving was not tested and is not claimed.

Focused source/native report: **15/15 gates passed**: final source/file hashes; geometry/prop/visibility equality; exact walk/reveal masks; exact y-sort alpha; exact six runtime textures and flat; binary alpha/native dimensions; exact PXO cells/layer names/hidden locked guide; exact ORA layers/hidden guide; both actual native reopen/export runs; unchanged scene source.

Source/native report: `outputs/chicago-loop-state-lake-v06/rpg-2-star-ocean-the-second_chicago-loop_source-native-pixelorama-report_v06_20261018-173234-48416048.json`.

## Actual gameplay and isolation evidence

- Real Godot harness: **17/17 checks passed** at native 640x360.
- Control A: unchanged real v05 imported assets render identically to the committed v05 capture (**0 differing pixels**).
- Control B: injecting v05 PNGs over their own paths also renders identically (**0 differing pixels**), validating the override method before v06 is injected.
- The v06 walk guide matches the actual scene's walkable function across all 230,400 pixels, including **64,225 walkable pixels**. Reveal mask matches the real scene everywhere. Spawn, three anchors, bilingual titles and art-unaccepted labels are unchanged.
- Held movement crosses the under-L lane through the real scene with no calendar time charged; west-column occlusion/reveal is exercised. Chicago remains excluded from the three-place goal.
- **Six fresh bilingual v06 captures** cover entry, lane walk and column reveal; one additional same-position v05 reference capture is preserved.
- With all six Chicago replacement textures installed in memory, the existing accepted-room replay completed **nine clue interactions across three accepted rooms**, and **all eight captures remain exactly 0 pixels different** from acceptance references. No replacement texture leaks into those rooms.
- Logs are clean: no SCRIPT ERROR, ERROR or FAIL lines. The interrupted harness initially had an inferred-bool parse error; it was fixed with an explicit bool annotation before the final clean run. No runtime threshold changed.

Final source/capture binding: `outputs/chicago-loop-state-lake-v06/rpg-2-star-ocean-the-second_chicago-loop_v06-runtime-evidence-manifest_20261018-173428-fca4766d.json`. Run `tools/rpg-2-star-ocean-the-second_chicago-loop_v06-runtime-evidence-check_v01_20261018-173459-c45a5b72.py` to recheck current source hashes, all saved capture/log hashes, the 15-gate native report, 17-gate Godot report, game-source base hashes and the eight actual acceptance pixel comparisons. Text source hashes use `sha256-text-lf-v1`; images/archives use raw SHA256.

## Actual visual inspection and remaining limits

Codex viewed the final native flat, the actual English entry capture and Chinese west-column reveal capture. The foreground grid is calmer, the elevated steel has material shading and rivet detail, and the labels and walk lane remain legible. Foliage still has a lacy small-pixel treatment and repeated fence/architectural rhythms remain visible. These are limitations for root/creator visual judgment; no final scene-quality or premium-art claim is made. The delivered package is ready for independent inspection, not automatically approved.

No runtime selector/default was changed. Full sprites remain 0/52, accepted environments remain 3/12, human post-art playthroughs remain 0/2. Root owns serialized integration and any single fixed revision-bucket update after inspecting this evidence.
