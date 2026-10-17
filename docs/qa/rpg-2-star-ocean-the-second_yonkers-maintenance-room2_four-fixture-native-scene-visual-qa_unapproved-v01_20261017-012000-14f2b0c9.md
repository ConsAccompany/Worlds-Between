# Yonkers signal workshop — native scene visual pilot

**Status:** technically verified, visually reviewed by Codex, **not creator accepted**. Science scene-art count remains 1/12 while its separate creator review is pending. This is Yonkers outskirts survey room 2, not the accepted NYC public facilities room.

## Runtime art

Four original 64×64 pixel fixtures now sit in the existing cool steel and teal interior: line checker, patrol log terminal and three-cell battery rack at the unchanged clue x-coordinates 163, 320 and 477, plus a low analysis console at the unchanged center terminal. Each has three editable OpenRaster layers (`contact-shadow`, `structure`, `identity-detail`) and a merged PNG. `game/scripts/survey_annex.gd` draws them only for `scifi.outskirts` room 2; no clue ID, interaction radius, route or collision body was changed.

## Godot evidence

- Godot 4.7.2 imported the four PNGs and parsed the project with exit code 0.
- The playable `survey_annex.tscn` produced native 640×360 Chinese and English captures: `outputs/yonkers-room2-visual-review/rpg-2-star-ocean-the-second_yonkers-maintenance-room2_four-pixel-fixtures-godot-zh-640x360-review-v01_20261017-011814-94cebca4.png` and the matching `en` capture.
- Actual `interact` input from a clear side approach registered `scifi.outskirts:3`, `:4` and `:5`; output `YONKERS_ROOM2_INTERACTIONS_OK 3`, exit 0.
- The four OpenRaster archives each contain exactly three image layers (`YONKERS_ROOM2_ORA_OK 4 sources x 3 layers`).
- The creator-approved female south idle static frame is used as a capture-only 48-logical-pixel visual reference. It does not approve or replace the runtime's incomplete full character sprite.

## Codex visual judgment and limits

The three clue fixtures read as different devices at native size. Their silhouettes, dark contact shadows and desaturated teal screens fit the preexisting steel-floor room. The new low console grounds the formerly floating center analysis marker. The lower side walking lane remains visible. This is a static visual and focused interaction check; it does not certify character motion, human pacing or scene-art acceptance. The older whole-room background plate is still a single image without editable source layers in this pilot; the four new fixtures have editable sources.
