# 蒋岚 / Jiang Lan — native exploration sprite prototype · M8

## Canon and status

The authoritative `visual_id` is `jiang-lan`; the approved portrait and character bible identify **蒋岚**, a **科技板块** engineer and device designer. An earlier task message called her “江岚” and described a nature-region test. That was a naming/region error, corrected before drawing. This set tests a fourth technology character identity, **not** nature-region transfer. Portrait approval does not approve these game sprites.

The [frame manifest](../../game/assets/characters/native-animation/rpg-2-star-ocean-the-second_jiang-lan_native-exploration-manifest_m8-prototype_20261014-144703-dbe4b4c6.json) lists 20 separate native 32×48 RGBA PNGs: one idle plus four walk phases for south, west, north and east. The [reproducible authoring script](../../tools/rpg-2-star-ocean-the-second_jiang-lan_native-exploration-author_m8-prototype_20261014-144009-7c54f08b.py) draws directly at final pixel size. Source portrait: `outputs/rpg-2-star-ocean-the-second_jiang-lan_character-sheet_hairstyle-v02_20261013-161317-c21bd255.png`.

## Identity at native scale

The approved hairstyle's short shaved sides and back, tall backward-swept dark spikes, and slim orange streak are drawn as silhouette shapes instead of a uniform short cap. Paired square forehead goggles, pale asymmetric tool vest, orange rolled cuffs, unlike-shaped hip devices and orange-soled boots provide additional identity cues. East and west directions have separately drawn hair, vest and device placement rather than a mirrored image. At 8× nearest-neighbor, [the single south idle detail preview](rpg-2-star-ocean-the-second_jiang-lan_native-idle-south-detail-preview_m8-prototype_20261014-144746-157efd2f.png) shows the authored pixels; this enlarged view is for detail inspection, not scale acceptance.

## Four separate 640×360 scale previews

Each preview places exactly one idle frame at foot position `(320,253)` over the existing science-city background, at one native sprite pixel per game pixel. These are **static composites**, not Godot screenshots or proof of runtime integration: [south](rpg-2-star-ocean-the-second_jiang-lan_native-south-game-scale-preview_m8-prototype_20261014-144703-146ce5fe.png), [west](rpg-2-star-ocean-the-second_jiang-lan_native-west-game-scale-preview_m8-prototype_20261014-144703-18411aec.png), [north](rpg-2-star-ocean-the-second_jiang-lan_native-north-game-scale-preview_m8-prototype_20261014-144703-79b2b60f.png), [east](rpg-2-star-ocean-the-second_jiang-lan_native-east-game-scale-preview_m8-prototype_20261014-144703-3effe923.png).

## Automated validation and limits

- The generator validates 20 unique 32×48 RGBA images, transparent corners, y=44 opaque boots at the shared `(16,44)` foot anchor and a maximum of 22 opaque colors.
- Walking phases change 46–128 pixels from their direction's idle. South, north and east keep a constant bounding box across five frames; west's hair tips intentionally vary by one pixel horizontally, while foot coordinates stay fixed. This may look like a small tuft sway or jitter and needs live inspection.
- City-scale static previews make the goggles, pale vest and orange cuffs readable without a name label, but motion timing and differentiation from all other 51 identities are unverified. No Godot runtime, visual registry, tracker, or asset acceptance state was changed. This remains **prototype_not_accepted** pending in-engine 640×360 and 1280×720 review.
