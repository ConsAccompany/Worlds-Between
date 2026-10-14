# Science city runtime integration — M8 candidate v05

## Implemented

- Reuses the existing 1672×941 city illustration as three polygonal foreground pieces at the correct 640×360 canvas UV scale. The garden canopy, central lamp, and east planting can cover an actor according to foot depth, without producing an edited duplicate of the art.
- A translucent protagonist silhouette and small locator appear only when the protagonist stands inside the garden canopy. The city plate remains opaque, so the tree does not fade during ordinary travel.
- Report, field survey, field assist, and trace markers have distinct icons with a dark backing. Trace and assist text appears near the protagonist instead of covering distant paving. The report label is slightly larger and brighter. All interaction coordinates, movement geometry, recruit state, save recovery, and entrances retain their prior behavior.
- A repeatable rendered capture script records distinct protagonist and recruitment states. The four final screenshots below are actual Godot 4.7.2 OpenGL viewport captures from the playable scene. The project uses a 640×360 logical viewport and a 1280×720 window override.

## Reviewed captures

- [Male protagonist behind the garden canopy](rpg-2-star-ocean-the-second_scifi-city_engine-viewport_m8-male-garden-occlusion_20261014-173631-ba65acd0.png) — foreground depth and the locator are visible.
- [Female protagonist beside the report hotspot](rpg-2-star-ocean-the-second_scifi-city_engine-viewport_m8-female-report-hotspot_20261014-173631-2f4700f5.png) — icon and nearby label remain legible over the stone paving.
- [Liang Xu before recruitment](rpg-2-star-ocean-the-second_scifi-city_engine-viewport_m8-female-liang-before_20261014-173631-b408a93d.png) — his city cutout and label are present.
- [Liang Xu after recruitment](rpg-2-star-ocean-the-second_scifi-city_engine-viewport_m8-female-liang-after_20261014-173631-1c9b3ba7.png) — both disappear while the protagonist remains.

Machine-readable file list: [capture manifest](rpg-2-star-ocean-the-second_scifi-city_engine-capture-manifest_m8-v01_20261014-173631-f7a6405a.json).

## Checks

- `m8_city_navigation_smoke.gd`: exit 0; all six hotspots reachable, swept collision/slide and save recovery pass.
- `m8_city_integration_smoke.gd`: exit 0 after v05; both protagonist appearances, cutout anchors, hotspot approach, recruitment visibility, city save restoration and world-map return pass.
- `m7_smoke.gd`: exit 0; both automated location-order routes reach the report. Receipts were written under isolated `user://test-saves/m7` and are **not human playthroughs**.
- Rendered capture script: exit 0 with `CITY_VISUAL_CAPTURE_OK 4`. Audio driver was set to Dummy, so audio was not assessed. An earlier headless integration run emitted the pre-existing ObjectDB exit warning; the final run did not.

## Still open

This is a playable city candidate, not final M8 art acceptance. The characters remain static cutouts, and the background is one baked illustration. The right stairs and building thresholds still need a full art/navigation pass before the environment can be judged at the intended quality; occlusion polygons are traced manually against this candidate plate and must be revisited if it changes. The city screenshot cannot establish the quality of the other ten sci-fi scenes or replace human 25–35 minute playtests.
