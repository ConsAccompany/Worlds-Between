# Washington Capitol west grounds walkable v05 — Codex visual audit

**Status: unapproved, nonruntime. Accepted science scene art remains 0/11.** I inspected real Godot 1280×720 entry, vista and beacon-front captures and the 640×360 entry capture in `outputs/wdc-cw-v05_20261016-055159-ca6ec5f1/`. Technical checks are recorded in the candidate QA note and do not establish visual acceptance.

## Observed improvement

- The dome and West Front are now visible from a walkable camera, making the site recognizably the Capitol rather than a generic stone ruin.
- Survey equipment, collapsed masonry and encroaching meadow communicate an abandoned city with active research. The heroine remains legible at the approved exploration display scale.
- The front path and interactions provide a plausible playable route between the foreground and the landmark.

## Remaining visual problems

- The landmark is only about three heroine heights tall in the entry view. The forced perspective suggests a miniature building rather than the expansive Capitol grounds.
- Sky, building, meadow and retaining wall form broad horizontal bands. Stone and turf have regular procedural texture; rubble reads as schematic. Several tree crowns remain similarly round.
- The distant patrol machine is nearly invisible. The near overhead ground and distant side-on facade do not yet share a fully convincing depth transition.
- The scene still needs material-specific pixel clusters, stronger asymmetry, and more readable traces of vegetation incursion and survey activity to approach the requested visual quality.

## Next pass

Retain the layered walkable proof, then study a more convincing scale and camera-depth composition before adding detail. Hand-place distinct stone breakage, organic growth and equipment silhouettes. Review entry, vista and beacon positions at both 1280×720 and 640×360. The source was authored through Python placement tables with a Pixelorama round-trip; the final painting workflow remains an open production choice.

**Counter impact:** none. v05 is neither a runtime replacement nor approved scene art.
