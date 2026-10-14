# City cutout integration review

Recorded: 2026-10-14T05:13:28.520632+00:00

## Change

City-only protagonist and Liang Xu cutouts now use each image's visible alpha bounds to set a provisional 44-logical-pixel height and anchor the visible bottom to the actor position. NPC labels move up and interaction labels gain dark outlines. Background, walkable rules, city hotspots, recruitment routes and current M7 test coordinates are preserved.

## Verified

Godot 4.7.2 imports the project. M1–M7 and M6 cold-restart checks pass. The new `game/tests/m8_city_integration_smoke.gd` passes headless and with an actual OpenGL rendered city. It checks both appearances, visible foot anchors, movement to all city hotspots, the west plaza boundary, recruitment sprite/label visibility, exact valid save positions, recovery of the old (82,260) city spawn onto (82,208), and return to the world map.

Four separate engine viewport captures cover male/Chinese and female/English before and after recruitment. Characters sit at the intended foot coordinates and outlined labels remain readable over the detailed background. These are cloud-rendered 640×360 viewport images from the playable scene; the virtual game window was 1280×720. They are automated evidence, not human playthroughs or final art approval.

Manifest: `rpg-2-star-ocean-the-second_scifi-city_in-engine-check_manifest_m8-foot-anchors_20261014-051328-11830a39.json`

- [rpg-2-star-ocean-the-second_scifi-city_in-engine-check_m8-female-entry_20261014-051106-f6834d86.png](rpg-2-star-ocean-the-second_scifi-city_in-engine-check_m8-female-entry_20261014-051106-f6834d86.png)
- [rpg-2-star-ocean-the-second_scifi-city_in-engine-check_m8-female-recruited_20261014-051107-cac67ac6.png](rpg-2-star-ocean-the-second_scifi-city_in-engine-check_m8-female-recruited_20261014-051107-cac67ac6.png)
- [rpg-2-star-ocean-the-second_scifi-city_in-engine-check_m8-male-entry_20261014-051106-b8312bee.png](rpg-2-star-ocean-the-second_scifi-city_in-engine-check_m8-male-entry_20261014-051106-b8312bee.png)
- [rpg-2-star-ocean-the-second_scifi-city_in-engine-check_m8-male-recruited_20261014-051106-b4de9167.png](rpg-2-star-ocean-the-second_scifi-city_in-engine-check_m8-male-recruited_20261014-051106-b4de9167.png)

## Open gates

All asset acceptance flags remain unchanged: portraits 9/52, displays 0/52, four-direction sprites 0/52, playable battle identities 0/5, art direction 0/3, scene quality 0/11. M7 remains in progress, M8 remains in progress, M9 remains todo.

Directional animation, layered city occlusion and detailed obstacle alignment are the next production work. The visible height is provisional and awaits visual approval. Two completed human M7 playthroughs in different location orders and a genuine 25–35 minute pacing review are still required.

Exit ObjectDB leak warnings remain in several automated checks. Cloud audio output is unavailable; this pass did not assess sound.
