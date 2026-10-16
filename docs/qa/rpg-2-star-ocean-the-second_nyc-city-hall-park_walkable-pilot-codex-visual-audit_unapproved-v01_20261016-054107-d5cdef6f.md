# City Hall Park walkable pilot v01 — Codex visual audit

**Status: unapproved, nonruntime. Scene-art acceptance remains 0/11.** I inspected the three actual 1280×720 Godot captures in `outputs/nyc-chp-v01_20261016-044931-92357bf2/`, including the central path, fountain occlusion and tree occlusion. Technical results are recorded separately in the candidate's QA note; they do not establish art quality.

## Visible strengths

- The civic building, cupola, axial gate, fountain and park paths make the place legible at a glance. The older fabric with small teal fixtures follows the approved New York art direction.
- The protagonist is legible at the approved 48-logical-pixel exploration display scale. Fountain, tree and lamp overlap vary with her position.
- The pilot is a useful walkability and layering foundation for one local camera view.

## Visual defects to fix before creator review

- The City Hall facade is highly regular and compressed behind the large heroine. Even allowing background perspective, the abrupt join between its front steps and the hero-scale central walk gives it a model-like feel.
- The dark grove, building, hedge and lawn form nearly full-width horizontal bands. There is little Lower Manhattan context, depth or foreground framing to break the diagrammatic layout.
- Most lawn area is vacant. Flower ovals, similarly shaped trees and evenly spaced lamps repeat visibly.
- The fountain-behind capture makes the heroine appear to stand on the fountain's upper edge. Occlusion can be technically correct while the overlapping silhouettes remain confusing.
- The tree-behind capture lacks a clear contact shadow; the heroine looks detached from the paving. The current pilot's paving and shadows are too uniform for the requested high-precision finish.
- The nonruntime v03 concept's monumental facade should not be traced. [NYC's City Hall description](https://www.nyc.gov/site/dcas/business/dcasmanagedbuildings/city-hall.page) identifies a central pavilion, projecting wings, a columned entrance portico and a domed tower. The pilot contains some of these cues, but its window rhythm and site geometry need a location-specific polish pass.

## Next visual pass

Keep the editable layers and walkability proof. Improve the building-to-walk perspective, add varied park activity and a restrained urban edge, hand-place distinct foliage clusters and paving wear, then inspect the same three camera positions in Godot. Resolve the fountain silhouette and actor ground contact before asking for creator acceptance. Whether the final pixels are edited in Pixelorama's GUI or in the editable layer source is still an open production choice; this audit does not require a decision while other work can proceed.

**Counter impact:** none. The v01 test art is not a runtime replacement or an accepted scene.
