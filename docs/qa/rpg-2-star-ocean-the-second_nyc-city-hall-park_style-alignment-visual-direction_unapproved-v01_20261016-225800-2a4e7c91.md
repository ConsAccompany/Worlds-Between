# NYC City Hall Park: visual style alignment (unapproved)

2026-10-16 creator feedback: City Hall Park v04 looks unlike the other science-region scenes. Withdraw v04 from final scene-quality review. It remains a nonruntime, unapproved walkable pilot; scene art stays **0/12 accepted** and the MVP meter does not change.

## Evidence and cause

- [Existing science-city background](../../game/assets/environments/rpg-2-star-ocean-the-second_scifi-city_environment-background_m8-v02_20261013-232003-48d0ab67.png) is a single detailed environment plate (SHA-256 `8d1ac49c4827201a40bda328a77a7c7b1cca007b676bd3169f8d7ae7afe79b8c`). The current exploration scene scales that plate into 640×360 with linear texture filtering. It has dense masonry and foliage texture, warm windows, cool teal civic technology, and strong depth from overlapping architecture and shadows. This whole-plate technique is itself not an accepted final scene pipeline.
- [City Hall Park v04 art-only Godot capture](../../outputs/nyc-chp-v04_20261016-172144-eb092a52/rpg-2-star-ocean-the-second_nyc-city-hall-park_godot-render-640x360-axis-art-only_unapproved-v04_20261016-172144-eb092a52.png) is a separate authored 640×360 layered-pixel pilot (SHA-256 `bc3e29f6ee0071911537376aa9e5b4e821cd27bd621104ab66a5ff38abdaccbe`). Its axial walk, civic building, fountain and park remain readable. Repeated tree/window shapes, broad flat lawns, sparse facade shadow planes and few science-civilization cues make it look like a simpler, present-day civic garden. Test-only visitors in the other v04 capture are lower detail than the environment.
- The two images also differ in apparent camera and spatial depth: the old plate is a rich three-quarter environment, while the new park is flatter and more symmetrical. Showing one at 1280×720 and the other at native 640×360 exaggerates the apparent difference; comparison must use the same game viewport and character height.

## Nonruntime visual target

[City Hall Park style-alignment reference](../../outputs/rpg-2-star-ocean-the-second_nyc-city-hall-park_style-alignment-reference_nonruntime-v01_20261016-225515-5ee8060c.png) (SHA-256 `4a029b723174212db0ea2fd1dc02c6b3d0801c70479bbbab23067762c780e01c`) uses v04 for layout and the old science-city plate for value, material and lighting cues. It is AI-generated, contains continuous-color detail, and is **not** a Pixelorama layer, runtime texture, or approved art. Do not paste, downsample, trace indiscriminately or mark it complete.

### Real-landmark guardrails for the visual pass

- [NYC's City Hall building description](https://www.nyc.gov/site/dcas/business/dcasmanagedbuildings/city-hall.page) identifies a central pavilion, two projecting wings, broad entrance stairs, a columned portico, roof balustrades and a central domed tower. Preserve these large-scale cues before spending pixels on ornamental microdetail.
- [NYC Parks' City Hall Park history](https://nycgovparks.org/about/history/before-they-were-parks/manhattan) records the restored Jacob Wrey Mould fountain, central walkway, gardens, grass and trees. These give the scene its location identity. The 2537 treatment may add civic technology while keeping the landmark legible.
- The generated reference is an art-direction sketch, not architectural evidence. Its enlarged gilded dome and fountain treatment should not be copied as literal historical detail. Check the final silhouette against the official descriptions and real-location imagery before submitting a scene for acceptance.

For the next native Pixelorama pass, preserve the real City Hall Park landmark and current walkable/collision layout. Prioritize, in this order:

1. Establish shared science-city light and material language: warm light on pale masonry, cool shadow planes, teal technology accents, restrained highlights, and distinct foreground/middle/background values.
2. Give City Hall its own readable facade rhythm, recessed windows and entrance depth. Strengthen the fountain's ornamental silhouette before adding more tiny plants.
3. Build foliage as separated lit canopy, midtone leaf clusters and cool undersides; use varied scale and overlap rather than repeating the same tree stamp.
4. Vary path and plaza materials with purposeful stone clusters, joints, wear and edge shadow. Keep the central walk readable and open for movement.
5. Add a few believable public technology cues for 2537 New York, subordinate to the historic park: one small information fixture and/or pavement light accents. Avoid aircraft, elevated roads, wholesale skyline changes and generic fantasy ornament.
6. Review the approved **48-logical-pixel exploration character display size** against the native 640×360 scene. Test-only NPCs are excluded from environmental acceptance and must not be presented as finished characters.

## Gate to show the creator again

Produce a new editable Pixelorama layered source and a real Godot 640×360 capture at the approved character display scale. Inspect the same scene at 2× without treating upscaling as added detail. Show the new capture together with the existing science-city view at the same viewport size. Verify path collision and foreground occlusion. Ask the creator for **scene environment** acceptance only after the two views appear to belong to one game; keep full sprites and other locations on their own acceptance gates.
