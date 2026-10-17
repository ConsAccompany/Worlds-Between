# Chicago Loop arrival: visual transfer brief (unapproved)

Status: art-direction recommendation for the first walkable Chicago scene. No scene art is accepted by this note. The science scene-quality count remains 0/11.

## Evidence

- The present technical arrival capture is an overhead street-grid placeholder: `outputs/rpg-2-star-ocean-the-second_global-earth-map_chicago-loop-arrival-zh-runtime-capture_m2-v02_20261015-184808-49d78162.png`. The map and movement work; the grid and labels are not a finished district.
- Existing nonruntime elevated-rail reference: `outputs/rpg-2-star-ocean-the-second_chicago-loop_car-arrival-l-viaduct-art-direction-nonruntime-v01_20261015-214006-6a56c565.png`. It conveys iron structure, old masonry and restrained future infrastructure. Its rendered perspective, people and vehicle are not runtime sprites.
- Existing Daley Plaza concept: `outputs/rpg-2-star-ocean-the-second_chicago-loop-daley-plaza_arrival-art-direction-nonruntime-v01_20261015-222021-d1b7c925.png`. Do not transfer its sculpture/fountain arrangement as geographical evidence.
- The Chicago Transit Authority describes the downtown Loop Elevated, including elevated stations and a trestle. [CTA All Stations Accessibility Plan](https://www.transitchicago.com/assets/1/6/ASAP_Strategic_Plan_508_FINAL.pdf). [Choose Chicago Loop overview](https://www.choosechicago.com/neighborhoods/loop/) notes the elevated train's downtown loop.

## Game-scale composition recommendation

Use a compact playable block beneath or beside an elevated rail span, leaving the route through the scene legible at 640 × 360. One steel support, its strong shadow, an older masonry frontage and a restrained cyan transit/survey element can identify this as the Loop without filling the viewport with repeated girders. Keep the player at the already approved 48-logical-pixel exploration display height and place no permanent companion follower behind the player.

The elevated track should have a clear draw-order rule: characters moving behind its near support may be occluded briefly, while the central walkable path and interaction markers remain visible. Keep vehicles outside the walking collision path. Any arrival vehicle is scenery only; the world map already models the flight with a simple fixed travel time and the user explicitly asked for generic flight information rather than airport names.

The [official Loop overview](https://www.choosechicago.com/neighborhoods/loop/) supports the elevated rail as a distinctive visual feature. In this game it is a **landmark/background structure**, not a new player travel mode or boarding interaction: the creator's travel rule remains airplane/car between map destinations and walking inside scenes. A static or distant train can be considered during art review, but no playable rail route is implied by this brief.

The scene can visually suggest a 2537 science-center city through small additions to familiar architecture. Do not assume or depict a specific aircraft terminal or airport. The exact Loop street/intersection for the art pilot is not a creator-approved landmark; retain the approved general Loop location and avoid naming a new exact site in the Game Bible as canon.

## Validation gate

Author editable pixel layers, export a single playable scene, then inspect a Godot 640 × 360 capture with player, UI and an interactable. Check path readability, ironwork occlusion, collision and bilingual labels. Human visual review remains necessary before scene acceptance.

## Overhead arrangement reference, 2026-10-16 19:50 ET

`outputs/rpg-2-star-ocean-the-second_chicago-loop_elevated-rail-walkable-block-art-direction-nonruntime-v02_20261016-195030-8c456a73.png` is a separate **generated, nonruntime** top-down reference. It clarifies one rail span, two support columns, broad pedestrian route, older facade and a small transit-information object. Its central path is visually clearer than the existing grid placeholder, and the two supports establish a simple occlusion test. The image is continuous-colour generated art, not a Pixelorama scene, not a real Chicago street plan and not accepted game art. At 640×360, the large lower foreground facade could cut off a player's entry route, and the upper trestle may hide too much of a 48-pixel figure near the supports. Recompose and pixel-author the layers around the actual movement bounds, then inspect the live scene with the hero and UI. The Chicago arrival visual has not changed the 0/11 science-scene counter; the denominator question remains open.
