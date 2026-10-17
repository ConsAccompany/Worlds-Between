# NYC public facilities room 1 — native scene visual candidate

**Status:** creator review requested; no scene-quality acceptance counted yet. This is the first investigation room in the Lower Manhattan civic archive. The adjacent second room is separately accepted as scene 1/12.

## What changed

The original Room 1 had three repeated floor plaques with clue markers. Three distinct 64×64 original pixel fixtures now sit at the unchanged clue x-coordinates 163, 320 and 477: a rectangular usage console, an exposed old conduit and a resident notes board. Each has `contact-shadow`, `structure` and `identity-detail` layers in its OpenRaster source, plus an exact merged PNG. The runtime only draws them for the NYC first room. The three original clue IDs, position rules, exit and walk lane are unchanged. Room 2 keeps its separately approved fixtures.

## Real Godot evidence

- Godot 4.7.2 imported the three new PNGs and the project parsed with exit code 0.
- The existing playable `survey_annex.tscn` was rendered at native 640×360 in Chinese and English: `outputs/room1-visual-review/rpg-2-star-ocean-the-second_nyc-public-facilities-room1_existing-scene-godot-zh-640x360-review-v01_20261017-011400-d3590c0a.png` and the matching `en` capture.
- The capture uses the creator-approved female south idle static frame at 48 logical pixels as a **review-only** override. It does not approve or replace the incomplete runtime four-direction sprite.
- Actual `interact` input was sent from a clear right-side approach at all three sites. `AppState.survey_clues` contained `scifi.city:0`, `:1` and `:2`; Godot printed `ROOM1_REVIEW_INTERACTIONS_OK 3` and exited 0.
- All three OpenRaster sources opened as archives with three layer images each (`ROOM1_ORA_OK 3 sources, three layers each`). A separate Godot replay of accepted Room 2 after this script change still printed `ROOM2_FIXTURE_INTERACTIONS_OK 3` and `ROOM2_FIXTURE_CAPTURE_OK 4`, exit 0.

## Codex visual review

At 640×360, the three stations have different silhouettes and readable visual purpose; the warm masonry, brass and teal details agree with the adjacent accepted Room 2. Their shadows contact the floor and the lower walking lane remains clear. The unchanged room background is an older whole-scene plate, so this pilot does not establish an editable source for that plate. Static capture and interaction checks do not prove character animation quality or a timed human playthrough. Creator scene-art acceptance is pending.
