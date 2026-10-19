# Canonical PCK exact raw-input boundary

## Result and scope

The canonical checkout `da9e5e20ff767a3a3878875c670e0a426e29c20e` now has the bounded export fix proven in the isolated probe. One template-free PCK was exported from the final source and actually launched from an **initially empty directory**, with no source checkout used as `res://`.

Final run `20261019-192016-dd50df7f`: checked export passed in13.906s; checked PCK launch passed in1.062s. Both logs are unfiltered and contain no script/runtime errors or warnings. Export counts: **67 raw scripts,740 PNGs,20 WAVs**. Source/config/protected portrait bytes were unchanged by export/launch.

PCK: **159,457,132 bytes**, raw SHA-256 `2be861186a01b0b810e47a42ce0fdb04cd2b3d547979ca51c90a706477aac337`. It is retained only under ignored `work/raw-pack-20261019-192016-dd50df7f/`; an actual `git check-ignore` read confirmed it is ignored. No PCK is placed in Git evidence.

This proves the tested raw-input/compiled-resource boundary in an engine-launched PCK. It does **not** deliver a native executable, platform release, full female runtime driver acceptance, art approval, audible listening or human playtest.

## Only production edits

Three files under `game/addons/raw-png-export-v01/`:

- `plugin.cfg`: editor-plugin registration; display name/description now describe exact raw input export rather than an isolated probe.
- `rpg-2-star-ocean-the-second_export-pack_raw-input-editor-plugin_v08_20261019-231503-7f42cbb8.gd`: registers/removes the export hook.
- `rpg-2-star-ocean-the-second_export-pack_raw-input-hook_v08_20261019-231503-7f42cbb8.gd`: adds original PNG/WAV bytes at their paths; recursively adds original `res://scripts/**/*.gd` bytes in `_export_begin`, while compiled `.gdc`/remaps remain. Counts reset to0 at each `_export_begin` because Godot can reuse the plugin instance across exports.

Two configuration edits:

- `game/export_presets.cfg`: `include_filter="data/*.json,assets/*.json,*.pxo"`.
- `game/project.godot`: enable `res://addons/raw-png-export-v01/plugin.cfg`.

`script_export_mode=2` remains unchanged. No existing game script, portrait image/source package, asset import setting, ledger, Bible, index, Site, provider or account file was edited. Pre-existing dirty import metadata is preserved and is outside the selected scope.

## Actual packed checks

- Raw PNG exists inside the PCK and has its exact original3816bytes / SHA `ccf9d2a293e7f1b9c706b4d2f1bf9c00b3c7714ec4e9b8bddf023e166f68b6fd`.
- Raw `Image.load_from_file(ProjectSettings.globalize_path(...))` RGBA SHA is exact `2f2e742e3611e662c33f2a3fb2590f69ac2792b276a6c3fc5d5c2ff500d306ae`.
- Existing `ResourceLoader` texture remains available with the unchanged imported RGBA SHA `748e411b01ec04716c34dbaa774d9cfa77b8e1b0249a74f3614a34e19b9ab531`. **It is not equal to original decoded RGBA**; no such equality is claimed.
- The native PXO is readable by ZIPReader using both `res://` and globalized paths; both expose8641bytes of `data.json`.
- Raw growth GD exists, with exact raw/text-LF SHA `2c4dca616acf3027a171ca8f5c53307e3edb7f8113b76622ac33c46dceded91f` and16948characters. ResourceLoader still loads an instantiable compiled GDScript via its `.gd.remap`; `.gdc` exists and loaded compiled source text is empty. Explicit assertions cover coexistence rather than silently switching script export to text.
- UI asset JSON is present with exact SHA `545c0e25368a15061ee9b1cb8fca3f4c796907d43eecbcaa0c6e35bed221a504`.
- Actual packed `growth_screen.tscn` instantiates: title populated, existing **five** member buttons, management skin **applied**, MVP female portrait **shown**, native239×311. No refusal/management error.
- Actual themed city selector returns a valid24000Hz stream with4,850,528PCMbytes. Its raw WAV is also present with exact SHA `4a4d9a3a03bf216df497023d8212a0dd89fe5ed654ef9561b85738c251118884`.

## Preserved experiments and corrections

Earlier isolated results are copied unchanged into `outputs/export-boundary-v01/`:

1. `…_decoded-source-equivalence_v03_20261019-230838-d6e78cb3.json`: ResourceLoader RGBA differs from original PNG RGBA in both checkout and packed paths. The repair preserves exact raw bytes alongside imported resources; it does not mislabel imported pixels as original.
2. `…_png-gd-coexistence-results_v07_20261019-231357-395abc7e.json`: the earlier `_export_file` approach observed zero `.gd` callbacks because script compilation/remapping precedes that callback. The final hook adds raw script inputs in `_export_begin` instead.
3. `…_complete-raw-boundary-results_v08r1_20261019-231602-1d97cb5a.json`: the probe incorrectly expected4party buttons; existing `AppState.PARTY_CAPACITY` is5. The fixture was corrected without changing game capacity.

The first canonical port passed at `20261019-191902-3c9f8596`; its report/logs are retained. Root then requested reusable-counter reset and accurate displayed plugin naming. Final canonical source was rerun once, producing the final result above. No old report was overwritten and no failure marker was filtered.

## Reusable bounded verification and bindings

- Launcher: `tools/rpg-2-star-ocean-the-second_export-pack_bounded-boundary-check_v01_20261019-191758-4650fe2a.py`.
- Actual probe: `tools/rpg-2-star-ocean-the-second_export-pack_complete-raw-boundary-probe_v01_20261019-191758-4650fe2a.gd`.
- Launcher uses the existing checked runner:120s export deadline,60s actual PCK deadline, required success markers, fresh isolated APPDATA/LOCALAPPDATA, fresh ignored PCK directory and empty launch directory. It never launches a failed export. Each run receives a new timestamp/unique ID.
- Final result/report and both raw logs: `outputs/export-boundary-v01/rpg-2-star-ocean-the-second_export-pack_canonical-…_v01_20261019-192016-dd50df7f.*`.
- Source-bound proof: `outputs/export-boundary-v01/rpg-2-star-ocean-the-second_export-pack_final-source-proof_v01_20261019-191758-4650fe2a.json`.

Final raw hashes:

| File | Raw SHA-256 |
| --- | --- |
| `game/project.godot` | `fdf6c94ef9d5fa35ea89771d25509702e05c41624dbc2af3da54d5a3db7c383f` |
| `game/export_presets.cfg` | `547857819f0e86155ebe6da5ccb784c86f052062921170d5c2b03a1b0fea5ccc` |
| `plugin.cfg` | `2a88f9cd6eef3875ce7c6de22aa50614b1d4cac349e3832e9b130dd65f16a915` |
| Editor plugin GD | `f989c48db0e8f3c647e93b34904819e4cf8874cd2ca19c473e9369a65f9f6739` |
| Export hook GD | `b5d0dda497c79be99a1f66a9820536ff624e5007f2ba49a00b29e4ec3d2b9783` |

Hashes describe tested working bytes. Git reported an LF/CRLF conversion warning for `project.godot`; root must apply its scoped-attributes/staged-byte hash gate before committing. No gratuitous whitespace normalization was performed here.
