# Washington Capitol distant vista v02 — Codex visual audit

**Status: unapproved, nonruntime cinematic candidate. Scene-art acceptance remains 0/11.** I inspected the actual 1280×720 Godot vista and its 640×360 landmark crop in `outputs/wdc-dome-west-v02_20261016-044903-cdb4ebdb/`. This is a distant establishing view, not the walkable Capitol grounds scene.

## What improved over v01

- The Capitol dome and west facade now dominate the visual hierarchy. The massive near-wall that hid much of v01 is gone.
- The drained pool floor, meadow and left tree give foreground, middle-distance and landmark layers. The small heroine and subdued survey tripod no longer compete with the dome or sit on its central axis.
- Collapsed right-wing masonry, left-wing ivy and missing dome plates communicate abandonment while leaving the landmark recognizable. The 640×360 crop makes the dome and terrace readable.

## Remaining visual issues

- The broad horizontal bands of pool floor, meadow, hill and sky still feel flat. Texture is procedural and repeated, with mottled dither rather than locally composed surfaces.
- Tree crowns share a rounded cluster language; the rocks look like soft lumps, and the fallen lamp is difficult to identify.
- Damage is concentrated at the edges and one neat grid-shaped dome hole. The center of the facade remains clean and repetitive, so it can read as an intact building with added damage marks.
- The heroine faces the viewer because only her south idle frame is approved. The vista invites a character looking toward the Capitol, but a back-facing sprite would require separate art review.
- The 640×360 crop loses both outer wings. It is effective for the dome, but it cannot stand in for an overview of the whole Capitol grounds.

## Next visual pass

Vary foreground material by hand, break the evenly banded depth with asymmetric terrain and debris, refine the dome breach and facade damage, and compare the full view and crop again in Godot. Preserve v02 separately. Do not use this cinematic proof as evidence that the required walkable Washington scene has reached the target quality. GUI pixel editing can be considered when practical; the current layers remain editable.

**Counter impact:** none. Technical pass reports and a recognizable landmark are progress on a candidate, not creator acceptance.
