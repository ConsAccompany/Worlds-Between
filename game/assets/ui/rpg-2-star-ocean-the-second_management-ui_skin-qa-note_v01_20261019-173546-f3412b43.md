# Management UI skin v01: producer QA note and node map (UNAPPROVED technical candidate)

Scope: `content.ui-visual.management`. Covers `growth_screen.gd` (party/jobs plus the ten-node overlay) and `save_screen.gd` (manual and auto slots). This is not creator-approved art. Nothing is wired yet. The producer did not run Godot.

## Files (sha256-text-lf-v1, LF on disk)
- Helper: `game/scripts/rpg-2-star-ocean-the-second_management-ui_skin-helper_v01_20261019-173546-f3412b43.gd`, `1d3b6b40…1a8191`.
- Self-check: `game/assets/ui/rpg-2-star-ocean-the-second_management-ui_selfcheck_v01_20261019-173546-f3412b43.py`, `1744418c…52387d`.
- Package: the copied `game/assets/ui/battle-skin-v01/` (manifest `545c0e25…a504`, pinned in the helper). It is reused read-only: 11 PNGs, 11 PXOs and 11 ORAs. No image was generated or changed.
- Untouched: the battle-skin package, the native author/helper, `battle_arena`, and the battle root-v02 helper (`69f2cd51…8463b`, unchanged).

## Self-check (bundled Python, no Godot)
`PYTHONUTF8=1 <bundled python> -I -B game/assets/ui/<selfcheck>.py` → `MANAGEMENT_UI_SELFCHECK checks 152 fails 0 PASS`, exit 0.

It covers:
- the manifest LF hash against the helper pin;
- typed fields;
- all 11 skins: raw PNG sha256-bytes, RGBA mode and size, slice values and bounds, PXO/ORA presence and hashes;
- that the helper's `REQUIRED` table matches the manifest;
- that the helper uses `JSON.new().parse` and writes no files;
- that the geometry literals in both screens are still the ones the plates assume;
- the plate clearance rules replayed for growth main, the node overlay, and save in both save and load modes.

It does not parse GDScript.

## Node map
All plates are `NinePatchRect` with nearest filtering, `MOUSE_FILTER_IGNORE` and `FOCUS_NONE`. Each is inserted directly after the existing background, shade or row `ColorRect`, so it draws below every label and button.

| context | plate (parent-local rect) | skin | centre |
|---|---|---|---|
| growth main | `…PlateHeader` (0,0 640×44), screen child 1 | hud-band | drawn |
| growth main | `…PlateGroup0` (10,82 620×180): info/aptitude/job/skill/pending labels plus upgrade×2, stay, promote | panel | drawn |
| growth main | `…PlateGroup1` (10,270 620×88): series×5, personal, nodes | panel | drawn |
| ten-node overlay | `…PlateNodeHeader` (0,0 640×44), `node_panel` child 1 after the shade | hud-band | drawn |
| save | `…PlateHeader` (0,0 640×42), screen child 1 | hud-band | drawn |
| save rows ×8 | `…PlateCell`, child 0 of each row `ColorRect`, full row height, ending 4 px before the row's first visible button (manual 413 px in save mode, 509 px in load mode; auto 509 px) | panel | frame only |

Buttons get the `normal`/`hover`/`pressed`+`hover_pressed`/`disabled`/`focus` StyleBoxTextures plus the six manifest font colours.
- **Growth (37 buttons):** back, member×5, upgrade×2, stay, promote, series×5, personal, nodes, node close, career×10, personal node×10.
- **Save (12 buttons):** back, save×3, load×3, auto load×5.

The selected member keeps its existing `disabled` look.

## Contract
- `Helper.new(dir)` loads nothing.
- `apply(screen)` detects growth or save by its existing refs, then checks everything below before any mutation. Failure returns false with `last_error` set and nothing changed.
  - The package: manifest LF hash pin, schemaVersion 1 and packageId as whole finite numbers and strings, `filter` = nearest, an exact 11-key `skinOrder`, each size and slice as a whole finite number equal to the expected value with a stretch centre left, plain png/pxo/ora names with 64-hex hashes, a **required raw PNG** with a matching sha256 (`require_raw_png`), the loaded texture size, and `#`-hex font colours.
  - The screen: every ref and the group counts, the full-rect background/shade as child 0, the exact save row `ColorRect`s, and no existing plate.
  - Clearance: every plate stays inside 640×360 and clears the layer's other `ColorRect`s. Any button whose effective rect touches a plate must sit wholly inside the plate's slice-inset centre, and no label origin may sit on a border.
  - Every stylebox's minimum size must equal the old one.
- After applying, it compares position, effective size (`size.max(combined minimum)`, so transient sub-minimum hidden controls are not false failures), combined minimum and visibility for every button, label, row and the node panel. Any difference triggers `revert()` and returns false.
- `revert()` is public and restores every override and removes every plate. Calling `apply` again on the same screen returns true. Calling it on a different screen while applied returns false. A new instance on an already-skinned screen returns false.
- Text, fonts and sizes, translations, disabled states, visibility, signals, the shade/overlay semantics (the node overlay still covers the screen and the shade still blocks input), party/jobs/save behaviour and defaults are not touched.

## Known limitations / for root
- Clearance is tight but non-overlapping: the save back button touches the header band's inner edge (0 px), and the growth/node headers leave 1 px. Root should judge crowding in real EN/ZH captures. The band heights are constants.
- The save cell width depends on the save buttons' visibility at apply time; the mode is fixed per visit. A layout that shows the Save buttons after apply would have them sitting over the cell frame.
- Plates shift sibling indices: growth by 3, the node panel by 1, save by 1, plus one child per row. Tests that use `get_child(n)` will see them.
- No inner dividers: the group panel borders act as the dividers, because there is no vertical room for 8 px nine-patch strips without crowding labels.
- Godot parse/runtime, `--management-ui-skin-pilot` wiring, ON-vs-OFF rect/min/text/font/connection comparison in EN/ZH growth/node/save contexts, and visual review are all still pending at root.
