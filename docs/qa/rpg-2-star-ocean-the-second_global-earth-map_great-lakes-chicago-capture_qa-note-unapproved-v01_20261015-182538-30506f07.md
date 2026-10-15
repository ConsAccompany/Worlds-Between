# Great Lakes / Chicago Loop runtime captures: QA note (unapproved)

Status: runtime evidence only. **Art not accepted. Visual acceptance not granted.** These captures show what the game currently renders. Nobody has signed off on them.

## What changed

- Only `game/tests/rpg-2-star-ocean-the-second_global-earth-map_visual-capture_m2-v01_20261015-024300-9b2fac94.gd` was edited. I added a `CHICAGO` constant and a `_capture_chicago()` step that runs after the existing 12 captures. No runtime script or other test was touched.
- The new step starts from the New York City start location. It does three things:
  1. It opens the `us_great_lakes` region and the NYC→Chicago card, selects the available air option, and captures the card in zh and en.
  2. It departs through the real `map.depart()` path. The route core charges the trip once. The step then captures the Chicago Loop scene in zh and en.
  3. It reloads the world map and captures the Great Lakes region and the Chicago card with Chicago as the current location, in zh and en.
- The step fails with `push_error` and exit code 1 if any of these hold:
  - Chicago is not a map place.
  - The card is not in the `ready` state.
  - There is no air option.
  - Departing does not open the Loop scene.
  - The party is not at Chicago after the trip.

## Run

```
work/tooling/godot-4-7-2/Godot_v4.7.2-stable_win64_console.exe --path game \
  --script res://tests/rpg-2-star-ocean-the-second_global-earth-map_visual-capture_m2-v01_20261015-024300-9b2fac94.gd
```

The run was windowed (not headless) on an RTX 3080 with OpenGL 3.3 Compatibility. Exit code 0, final line `GLOBAL_MAP_CAPTURE_OK 22`, with no errors or warnings. Stamp/run id: `20261015-182538-30506f07`. The 12 original labels were also re-captured under this new stamp. No older files were overwritten.

Route and state lines from the core:

```
ROUTE zh route.air.nyc__chicago [selected]: 飞机 · 航程 1177.1 km · 6小时5分钟 / 抵达 2537年5月25日 14:05 / 里程与旅时为估算
ROUTE en route.air.nyc__chicago [selected]: Air · Air 1177.1 km · 6 h 5 min / Arrive May 25, 2537 14:05 / estimated distance and time
BEFORE earth.us.ny.new-york-city May 25, 2537 08:00
AFTER earth.us.il.chicago May 25, 2537 14:05
```

From NYC to Chicago the core offers exactly one available option, which is air.

## New Great Lakes / Chicago captures (outputs/, 1280x720)

Prefix: `rpg-2-star-ocean-the-second_global-earth-map_`. Suffix: `-runtime-capture_m2-v02_20261015-182538-30506f07.png`.

| Label | What it shows |
|---|---|
| `us-great-lakes-zh` / `-en` | Great Lakes region, party still at NYC |
| `us-great-lakes-chicago-air-route-card-zh` / `-en` | NYC→Chicago card: air, 1177.1 km, 6 h 5 min, arrival May 25, 2537 14:05, estimate note, Depart enabled |
| `chicago-loop-arrival-zh` / `-en` | Chicago Loop placeholder scene after the real departure |
| `us-great-lakes-chicago-here-zh` / `-en` | Great Lakes region at 14:05 with the gold current-location ring on Chicago |
| `us-great-lakes-chicago-here-card-zh` / `-en` | Chicago card: "Party is here / Already here. No travel needed.", Enter scene button |

## Observations (not fixed: runtime/text is out of scope for this worker)

1. **English air line repeats "Air".** It reads `Air · Air 1177.1 km`, because the `mode_air` text is followed by the `air_km` label. The Chinese line reads `飞机 · 航程 1177.1 km` without repetition. This is a copy issue in `world_map_text.gd` / `route_option_text`.
2. **The Loop scene header overlaps the buttons in English.** The `Technical placeholder · Art not accepted` badge runs under the Save button. The subtitle (`…Blocks inside the elevated loop`) is cut off by the Save/World map buttons. The zh capture fits without overlap.
3. With the route card open, the card covers the eastern part of the Great Lakes frame (Michigan shore). Chicago and its label stay clear of the card.
4. The status bar still reads `Places 0/3 · Surveys 0/3` after arriving in Chicago. This is expected for a fresh run, and it is noted here only so the captures are not misread as survey progress.
