# Worlds Between M2: Windows export data inclusion audit (global Earth map + travel calendar)

- Date: 2026-10-15
- Engine: Godot 4.7.2.stable.official.ed1daf0bf (`work/tooling/godot-4-7-2/Godot_v4.7.2-stable_win64_console.exe`)
- Scope: whether the custom JSON and geodata read by the M2 map, route core and calendar would ship in a future Windows export. This note does not set a distribution plan, an export path, signing, or which folders ship.
- Status: audit only. Nothing staged or committed.

## Findings before this change

- `game/` had no `export_presets.cfg`, so no Windows export could be run or checked.
- `game/project.godot` has no export settings and no setting that hides `data/`.
- Run-time data reads for M2. All are `res://` JSON files read with `FileAccess`:
  - `scripts/world_route_registry.gd` `DEFAULT_DATA_PATH` → `data/world-travel/rpg-2-star-ocean-the-second_global-earth-travel_locations-routes_m2-provisional-v01_20261015-024215-b876e53d.json` (routes, locations, calendar start)
  - `scripts/world_map_data.gd` `REGISTRY_PATH` → `data/world-map/rpg-2-star-ocean-the-second_earth-map_place-registry_m2-v01_20261015-024300-36903495.json`
  - `scripts/world_map_data.gd` `GEODATA_PATH` → `data/world-map/rpg-2-star-ocean-the-second_earth-map_runtime-geodata_m2-v01_20261015-024300-2595ada6.json` (149,029 bytes)
  - `scripts/travel_calendar.gd` is code only and reads no files. The calendar start comes from the travel JSON above.
- No `.gdignore` file sits under `game/data/`. The existing `.gdignore` files are under `game/assets/...` and `game/.godot`.
- Saves and playtest receipts write to `user://saves`, which works in an exported build.

## Change

1. `game/export_presets.cfg`: one preset, `Windows Desktop`, with `export_filter="all_resources"` and `include_filter="data/*.json"`. No exclude filter or export path is set. The only option set is `binary_format/embed_pck=false`, which is the default. It is there so Godot does not report an empty options section.
2. `game/tests/rpg-2-star-ocean-the-second_global-earth-map-calendar_export-data-inclusion-smoke_m2-v01_20261015-033441-6e5c07b5.gd`, which runs in two modes:
   - **Source mode** (`--path game`) checks that the preset exists and targets Windows Desktop. It checks that Godot treats `.json` as a resource. For each of the three paths, which it reads from the script constants, it checks that the file exists, is not under a `.gdignore` folder, is packed by the preset and is not excluded. It then runs the real loads (see below).
   - **Pack mode** (`--main-pack game.pck ... -- --pack-mode`, started from a folder that holds only the pck) checks that there is no `project.godot` or `data/` on disk, so every read must come from the pack. It checks that all three files are in the pack, then runs the real loads: `WorldRouteRegistry.load_default()` is valid with locations and a start location, the calendar start converts with `TravelCalendar.iso_text`, the map registry has places and regions, and the geodata has global land rings.

No M2 runtime or map script, world-travel JSON, Game Bible or `docs/progress.md` was changed.

## Evidence

All Godot runs used an isolated copy: `C:\Users\hkzha\AppData\Local\Temp\wb-export-audit-20261015-033441-6e5c07b5\game`, which is `game/` without `.godot`, followed by `--import`. The shared tree got no `.uid` or import side effects. A check for `.uid` files newer than the change found none.

| Run | Result |
|---|---|
| `--import` (copy) | exit 0 |
| Source mode, final preset | `EXPORT_DATA_INCLUSION_SMOKE_OK mode=source checks=24` |
| `--export-pack "Windows Desktop" final/game.pck` | exit 0, no ERROR/WARNING lines, 53,493,036 bytes. The log shows `Storing File:` for all 3 M2 JSON files, plus `world_route_registry`, `world_map_data`, `travel_calendar` and the other `world_*` scripts as `.gdc` |
| Pack mode on `final/game.pck` | `EXPORT_DATA_INCLUSION_SMOKE_OK mode=pack checks=13`, exit 0 |
| Main scene boot from the pack (`--main-pack game.pck --quit-after 180`) | exit 0, no ERROR or SCRIPT ERROR lines |
| Negative control: `exclude_filter="data/world-map/*,data/world-travel/*"` | Source mode FAIL `preset does not exclude data/world-travel/...json`. 0 M2 JSON files stored. Pack mode FAIL `pack contains data/world-travel/...json`, exit 1 |
| Control: empty `include_filter` | 3 M2 JSON files still stored, both modes OK |

The last control shows that Godot 4.7.2 packs `.json` under `all_resources` without help, because JSON is a resource type. The `data/*.json` include filter is a safety net in case a later preset switches to `selected_resources` or `scenes` mode.

Commands, from the repository root:

```
G=work/tooling/godot-4-7-2/Godot_v4.7.2-stable_win64_console.exe
T=<temp copy root>
$G --headless --path "$T/game" --import
$G --headless --path "$T/game" --script res://tests/rpg-2-star-ocean-the-second_global-earth-map-calendar_export-data-inclusion-smoke_m2-v01_20261015-033441-6e5c07b5.gd
$G --headless --path "$T/game" --export-pack "Windows Desktop" "$T/final/game.pck"
cd "$T/final" && $G --headless --main-pack game.pck --script res://tests/rpg-2-star-ocean-the-second_global-earth-map-calendar_export-data-inclusion-smoke_m2-v01_20261015-033441-6e5c07b5.gd -- --pack-mode
```

## Risks and limits

- **Untracked inputs.** The three M2 JSON files, `world_*.gd`, `travel_calendar.gd`, this preset and this test are all untracked (`??`) at audit time. An export from a clean clone would miss them until the owning session commits them.
- **Pack only, no .exe.** No Windows export templates are installed (`%APPDATA%\Godot\export_templates` is empty). A full `--export-release` to `.exe` was not run. The pck-only export uses the same file selection, but the executable wrapper, icon and rcedit options were not tested.
- **The pack includes non-game files.** Under `all_resources` the pack also includes `tests/`, the data-folder `.gd` render helper, and other review or QA scenes and scripts. Excluding them is a distribution decision and is out of scope here. If a later exclude filter is broad (for example `data/*`), this smoke test fails in source mode.
- **Filenames are pinned in code.** If a data file is renamed, the script constant must change too. The test reads the constants, so it follows a rename, but a constant that points at a missing file fails.
- **Engine version.** All results are for 4.7.2. Re-run both modes after an engine upgrade.
- **Leftovers.** The dev-only character-source gallery script calls `ProjectSettings.globalize_path("res://")`, which would not work in an export. It is not on the M2 path. Not changed.
