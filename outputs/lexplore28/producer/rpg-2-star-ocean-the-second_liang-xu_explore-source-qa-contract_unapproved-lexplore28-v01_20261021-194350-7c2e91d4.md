# Liang Xu exploration source bank lexplore28 — QA contract (UNAPPROVED technical source)

Run `3acdbd6e`, stamp 20261021-194350. Owner: Claude. Status: produced technical source. Art is not approved, the set is not playable-ready, and no runtime default, NPC or hero integration was made. Not committed. The ledger, Bible and registry were not edited.

Task IDs: `content.char.liang-xu.static-west`, `static-north`, `static-east`, `idle-anim`, `walk-south`, `walk-west`, `walk-north`, `walk-east`.

## Contract

80x112 cell, density 2, pivot 40/104, sole row 103, 96-texel body (48 logical px), binary alpha, Liang named ramps unchanged. Per direction: static, 4-frame idle (700/200/400/200 ms), 12-phase walk (40 ms reference) and 12 phase-aware stop bridges ([walk p exact, s1, s2, idle f00 exact], settle 120 ms). The schema matches zexplore25: source manifest, sprite-set v1, registry v1, stop supplemental v1 and loader-ready.

- **South.** Built from the exact v01 MAP/ROLE role layers. `accessory` is split into `belt-placket` and `board`, and the composite is unchanged. Static and idle f00 are byte-exact with the source PNG `9fee9018…`. Motion uses only offsets, a shin/boot lift and a 1-texel hem sway, with no repaint. The south visual audit and cosmetic revision bucket stay open: deferred, not waived.
- **North.** Mirrored south silhouettes refilled as back surfaces: top-knot and copper pin, silver streak on his right, collar band, split-coat vent and board back.
- **West.** Authored puppet showing his left side, with the board edge-on in the near hand.
- **East.** Separately authored puppet showing his right side: silver temple sweep, board in the far hand peeking past the coat front. It is then mirrored, so it is not a mirror of west.
- **Reuse.** Helpers come from mexplore23 (unmodified). The south grids come from the v01 Liang build tool (unmodified). The 32x48 placeholders were not used.

## Evidence (this run)

| Gate | Result |
|---|---|
| `build` | 341 files (164 PNG in outputs + 164 lossless runtime copies, 4 PXO, 4 ORA, 5 JSON) |
| `check --pixelorama` | REBUILD 341/341, SOURCE 47/47, RESULT PASS |
| Pixelorama 1.2.3 export equality | 41/41 frames for each of the 4 directions, exit 0, no SCRIPT ERROR |
| Pixelorama diagnostics (reported separately, not clean) | 4× `ERROR: Condition "!actions.custom_samplers.has(...)"` shader diagnostics per direction |
| Independent native-bank checker `493fd162` | NATIVE_BANK True, 2430/2430 checks |

- Source manifest: `outputs/lexplore28/rpg-2-star-ocean-the-second_liang-xu_explore-source-manifest_unapproved-lexplore28-v01_20261021-194350-2ceb83e8.json` (sha256-bytes `cba71207…34b1832`).
- Tool: `tools/rpg-2-star-ocean-the-second_liang-xu_explore-source-author_unapproved-lexplore28-v01_20261021-194350-3acdbd6e.py` (sha256-text-lf-v1 `c80dd5e6…b943c2e`).
- The native-bank proof filename uses the checker's own UTC timestamp convention (`20261021-234843`).

## Contact, slip and stop (measured, not a fluidity claim)

- **Side source cycle.** The planted heel moves exactly the declared 4 source texels per phase (0 texels residual against declared movement, west and east). This is source-space consistency only, not a world foot lock.
- **At 140 logical px/s with a 40 ms phase clock.** The world advances 11.2 source texels per phase against 4 declared. The planted side foot slides 3.6 logical px per phase (21.6 per stance). A pure distance driver would need 70 phases/s, so 60 fps playback skips phases. Neither option is claimed as foot-locked.
- **Front/back.** In-place cycles that slide 11.2 source texels per 40 ms in world space.
- **Stop bridges.** South/north planted drift is 0. On west/east the planted heel travels 15 source texels in total across a bridge, with a maximum of 5 per frame. That is a visible shuffle.

## Known weaknesses

- **Side legs overreach.** The side IK overreaches by up to 1.425 source texels at the stance extremes, so legs look straight and stretched at contact.
- **Front/back stride.** The front/back walk is a lift-only cycle with no foreshortened stride.
- **Side puppet quality.** The puppets are below the hand-placed south texel quality: flat profile face, simple coat panels.
- **North head.** The back head and top-knot read as a tall column.
- **Board readability.** The board is a thin edge-on slab in side views.
- **East lighting.** East light becomes upper-right after the mirror.
- **Untested at gameplay scale.** No actual Godot gameplay capture or normal-speed motion review was done in this batch.

## Exact next action

Codex should inspect independently and run a source-bound Godot 48 px capture of the four statics and the normal-speed walk/stop for each direction, on bright and dark plates, using a test-only loader that points at the registry in `game/data/lexplore28`. The creator then reviews it. Do not wire it into any default before that review.
