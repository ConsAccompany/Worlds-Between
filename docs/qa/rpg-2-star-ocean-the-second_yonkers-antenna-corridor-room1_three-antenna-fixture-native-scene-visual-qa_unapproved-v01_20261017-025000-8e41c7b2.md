# Yonkers antenna walkway (room 1): native antenna fixture pilot

**Status:** technically verified by Claude, **UNAPPROVED**, not creator reviewed. This covers Yonkers outskirts survey room 1 (天线走廊 / Antenna Walkway) only. The accepted maintenance room 2 is unchanged. Science scene-visual count stays **3/12** and the weighted meter stays **40.8%**. Nothing is staged, committed or pushed.

## Runtime art

Three original 64×64 pixel fixtures now sit under the unchanged clue markers at x = 163, 320 and 477, with the same placement as room 2 (clue + (−32, +2)). They use the accepted room 2 palette, ink outlines and contact-shadow ellipse. Four small accents were added: jitter amber, frost and two corridor moss tones.

| Clue | Fixture | What it shows |
|---|---|---|
| 天线 A / Antenna A | `a-jitter-mast` | Tall lattice mast with a side-view Yagi array. All four strength bars are lit, the steady baseline is broken by tall amber jumps, and sparks show at the array tip: strongest, but not reliable. |
| 天线 B / Antenna B | `b-steady-dish` | Low compact dish with a smooth sine trace and two of four bars lit. A clamped, intact cable runs to a brass ground rod, and a service tag hangs on the box: weaker, but steady. |
| 天线 C / Antenna C | `c-cold-mast` | Bright new capsule radome on a weathered guyed mast, with a wind ribbon and a trace that drops out. The backup battery is frosted with one amber cell lit, and the old capsule head lies on the floor: the new head did not fix the wind dropouts. |

`game/scripts/survey_annex.gd` gains only `YONKERS_ROOM_ONE_FIXTURES` and one `room == 1 and destination_id == "scifi.outskirts"` draw block (+9 lines, no deletions). Clue IDs, interaction radii, text, routes, movement clamps and doors are unchanged. There is still no camera and no collision body.

## Sources

`outputs/yonkers-room1-antenna-pilot/` holds the following for each fixture:

- a merged PNG;
- a four-layer OpenRaster file (`contact-shadow`, `structure`, `lit-edges`, `clue-detail`);
- a four-layer Pixelorama `.pxo` (pxo_version 7);
- the shared manifest with sha256 hashes.

The runtime PNGs in `game/assets/props/yonkers-antenna-room1/` are byte-identical to the source PNGs. Their import settings match the room 2 fixtures. Author tool: `tools/rpg-2-star-ocean-the-second_yonkers-antenna-corridor-room1-pixel-fixtures-author_v01_20261017-024000-9b3e6f21.py`.

## Evidence

- Real Godot 4.7.2 captures at 640×360, with the creator-approved female south idle as a capture-only 48-logical-pixel reference. The after set is in `outputs/yonkers-room1-antenna-pilot/after/` (`zh-start`, `en-start`, and `zh-lane-b` with the heroine standing in front of antenna B). The matching HEAD baseline set is in `before/`.
- Capture and check tool: `tools/rpg-2-star-ocean-the-second_yonkers-antenna-corridor-room1-capture-and-check_v01_20261017-023412-5e2b7c19.gd`. Results:
  - `INTERACTIONS_OK 3x2`: real `interact` input registers `scifi.outskirts:0/1/2` from the side and from below.
  - `LANE_WALK_OK`: held `move_right` crosses the central lane from the start to the next marker.
  - `NO_NEW_COLLISION_OK`: walking up through antenna B's footprint reaches the old y clamp.
  - `NEXT_ROOM_OK`.
  - These pass both at HEAD and with the fixtures.
- Pixel, source and Pixelorama check tool: `tools/rpg-2-star-ocean-the-second_yonkers-antenna-corridor-room1-pixel-and-source-check_v01_20261017-024346-3f8d5a62.py`. All 9 gates PASS, and the report is saved next to the sources. The main results:
  - Zero changed pixels outside the three fixture rectangles or where the fixtures are transparent, in all three shots. This means text, UI, labels and marker rings are unchanged.
  - Every opaque fixture pixel not under a marker renders exactly. The contact-shadow blend error is at most 0.85 of a channel unit.
  - No fixture pixel falls inside a label box or the y 236–290 walk lane. Fixtures occupy screen rows 167–229.
  - All 605 heroine pixels are unchanged in the lane-b shot.
  - The Pixelorama 1.2.3 headless CLI opens every `.pxo` and `.ora`. It exports each layer exactly with `--split-layers`, and the flattened export is also exact.
  - Every opaque colour comes from the declared palette. Only the contact shadow is semi-transparent.

## Limits and visible defects

- A Python-written `.pxo` loads and exports exactly in the Pixelorama CLI. A file saved by the Pixelorama GUI was not tested, because the CLI cannot write `.pxo`.
- Another session's open Pixelorama GUI autosaved `backups/2026_10_16_23_14_03/(untitled backup)-…` during the check. The gate lists that change but does not count it. All headless runs used temporary `APPDATA` folders, and the real `config.ini` was not changed.
- The baseline also shows that the English "Return outside" header button text overflows its 98 px button. This is existing UI and was not changed.
- The room background is still the older single plate with no editable layers. The fixtures are drawn by `_draw`, so they never sort in front of the heroine. A player standing behind a fixture overlaps it instead of being hidden by it.
- Antenna A's Yagi tips and antenna C's whip reach screen y 167. They sit beside the markers, not under them. The markers draw on top where they overlap.
