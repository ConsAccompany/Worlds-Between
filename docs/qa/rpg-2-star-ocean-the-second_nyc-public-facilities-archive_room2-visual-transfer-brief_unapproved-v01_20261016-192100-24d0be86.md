# New York public facilities archive — room 2 visual transfer brief

**Codex visual direction, 2026-10-16. Unapproved, no runtime or meter change.** This is a contained first science-scene quality candidate for `visual-scene.city-survey-inner`. It is still part of the NYC investigation and must use the current real-place naming. The current reference is `outputs/rpg-2-star-ocean-the-second_survey-annex-room2-dark_protagonist-female-south-idle-selout-v8-h48_m8-v08_20261015-022215-e2203167.png`; it is an older real Godot capture, not evidence that the current NYC title has been rendered.

## What the existing capture communicates

The room has a disciplined warm/dark palette, legible stone floor and detailed top cabinets. The approved female south static frame remains visible at 48 logical pixels. The three objective symbols are clear but float over largely empty floor; the room reads like a menu laid over a decorative background. Uniform cabinet bays and floor tiles repeat across the full width, so there is little visual hierarchy between the archive clues.

`game/scripts/survey_content.gd` names three existing evidence objects: **维修手册 / repair manual**, **轮值记录 / duty log**, and **负载注释 / load annotation**. The next art pass should turn those into three physically distinct station silhouettes, each still carrying its existing accessible interaction marker:

1. **Repair manual, left:** open book or folio at a low maintenance workbench, with one lamp and a few service tools. Light should pool on the pages and the hand-reachable edge. Keep the established clue trigger and text unchanged.
2. **Duty log, center:** a compact desk or archival lectern with a clearly layered stack of date sheets and a visible ledger spine. Avoid another circular console so this station differs from the left and right. Keep the central path open.
3. **Load annotation, right:** a wall-adjacent analog meter or terminal with a separate small paper annotation clipped beside its display. Distinguish old meter hardware from modern cabinets through material and glow, reflecting the clue about records with different scope.

## Pixelorama and Godot constraints

- Author editable pixel layers at the game's existing top-down view and verify a real Godot 640×360 capture, plus a 1280×720 nearest-neighbor capture for detailed inspection. Do not paste a generated continuous-colour image into the scene.
- Preserve movement bounds, all three clue triggers, return exit, terminal, UI accessibility and current investigation/save behaviour. Keep enough walkable space for the 48-pixel protagonist to approach each station without sprite/marker overlap.
- Separate floor base, cabinet architecture, station props, practical lights, shadows, and foreground occlusion. Use restrained warm light at the manual/log and a different cooler source at the load meter; keep important text/interaction icons readable in Chinese and English.
- Vary the cabinet rhythm at two or three intentional points (an open drawer, maintenance panel, cable junction), without filling the top wall with noise. Add contact shadows for furniture; the open floor should remain readable but less empty.
- The three evidence objects must remain recognizable **after** interaction markers are temporarily hidden for an art-only capture. Show both the art-only and normal interactive view. Compare with the accepted heroine v8 static and an ordinary placeholder companion at the same display scale.

## Acceptance path

The image is a production brief, not an accepted scene. A technical pass needs collision/trigger checks and bilingual screenshots. Codex then judges scene depth and readability in the actual capture. The creator must see the real playable room and approve its quality before `visual-scene.city-survey-inner` can move from 0 to 1. No other science scene or character sprite is implied to pass with it.

## Image edit review, 2026-10-16 19:23 ET

`outputs/rpg-2-star-ocean-the-second_nyc-public-facilities-room2_three-evidence-stations-reference-nonruntime-v01_20261016-192300-9cd8a41f.png` is a generated **nonruntime visual reference** made from the actual Godot room capture. It keeps the three marker positions and the main route through the room. The manual bench, narrow ledger lectern and analog meter are visually distinct at game composition scale; each can be approached from the open lower floor. These prop silhouettes and the mixed warm/cool practical lights are useful for a hand-authored Pixelorama pass.

Do **not** paste the image as a scene background: it is continuous generated colour at a different resolution, alters both character figures, keeps the obsolete pre-NYC heading, and does not prove clue triggers or collision. Rebuild the three props as editable pixel layers in the existing real room, preserve the actual v8 heroine, and use the current New York localization. The art-only and interactive Godot captures plus creator review are still required.
