# Four MVP display portraits and one five-variant helper

Scope: `content.char.protagonist-male.display`, `content.char.liang-xu.display`, `content.char.ji-cheng.display`, `content.char.zhao-ling.display`. Producer: DeepSeek. Independent package corrections, one necessary Ji crop correction and normal growth integration: Codex. No party-icon kit, dialogue kit, full-sprite, art/canon approval or human-playtest completion is claimed.

## Exact image production

Every source is existing AI-generated **UNAPPROVED CONCEPT** art at1916×821. Only exact source rectangle slices are used, with no resampling, repainting, new generation, background removal or invented pixels. Each deliverable is a separate PNG and one-layer OpenRaster ORA. No PXO or semantic anatomy/handpaint layer is claimed.

| Subject | Final ROI [left,top,right,bottom] | Native size | Pixels |
| --- | --- | --- | --- |
| Male protagonist | [948,54,1187,365] |239×311|74,329|
| Liang Xu |[930,35,1235,403]|305×368|112,240|
| Ji Cheng corrected v02 |[830,10,1190,420]|360×410|147,600|
| Zhao Ling |[830,15,1210,360]|380×345|131,100|

Independent oracle: **62/62**, all **465,269** final ROI pixels exact. Source hashes, native sizes, ORA single-layer/merged/payload equality, manifest hashes/identity/provenance, producer-byte preservation, normalized names, same-runtime deterministic rebuilding and rebuilt pixel equality passed.

The male/Liang/Zhao PNG and ORA preserve original producer compressed bytes exactly. The existing female package and its `48118289…` PNG remain untouched. Two local rebuilds are byte-identical to each other and pixel-identical to the authoritative images; compression bytes may differ across Python/zlib runtimes. The existing female builder is the explicit PNG/ORA primitive dependency, bound in the source proof.

### Ji Cheng correction and retained prior

Root inspected the producer capture and found the root-selected original ROI `[830,10,1215,420]` included a neighboring portrait strip. This was not a producer identity error. Root authorized the narrower `[830,10,1190,420]` crop. Its new run identity is `v02_20261019-225614-54ca9249`:

- PNG SHA `764f7615d5eb6b2ed49eac7f8fe05bfb32645e3dcaa4bd8a2f6186946143b761`.
- ORA SHA `4adf8e515ee1d4e364f8b91d427198405f726887700087180c41d9dc3892aaed`.

The too-wide original Ji PNG/ORA/normalized metadata/checksum files are retained under `outputs/mvp-portraits-v01/prior-ji-crop-v01/`; the producer workspace is untouched. Helper, builder and oracle now use only the corrected Ji ROI/native size/hash/path. Codex viewed final actual EN/ZH captures: no neighboring portrait strip is visible at the right edge. This remains unapproved art.

## Package and integration corrections

- Four compound `.manifest.json` filenames became `display-portrait-manifest_…json`, with matching `display-portrait-checksums_…sha256` receipts. Paths/checksums point at current artifacts and properly named helper/builder files. Unshipped schema-file claims were removed.
- Provenance explicitly distinguishes original AI-generated concept sheets from the exact crop operation: `original_source_ai_generated=true`, `new_generative_processing=false`, `human_artist=false`, no canon/static/full-sprite approval.
- One generic helper maps hero male/female variants and three companion IDs independently. Unknown hero appearances/IDs and wrong argument types hide/refuse; the actual host `selected_id` must match. Literal image paths, raw SHA and native size validate before first texture creation. Five validated textures are cached; repeated selection retains the same texture objects and returns before file loading.
- Constructor loads no file/texture/metadata. Fixed rect `(522,88,96,124)`, aspect preserving, mouse-ignore/focus-none, immediately below node overlay. Passive decoration is excluded from collisions; actual interactive controls including sliders/custom mouse-handling controls and real text cause refusal.
- Only existing `game/scripts/growth_screen.gd` was wired: new `--mvp-display-portraits-pilot` takes priority, then `elif` preserves old `--female-display-portrait-pilot`. Both supplied still create **one** portrait helper. Neither supplied creates none. Refresh and exit hooks do not modify original UI controls or AppState.

## Actual normal-path evidence

Windowed Godot4.7.2, actual `growth_screen.tscn`, native640×360, Dummy audio, fresh APPDATA/LOCALAPPDATA,90-second checked-runner deadline:

- First run: **118/118**, clean unfiltered checked log. A final bounded run adds explicit all-flags-off image parity and filename sanitation: **121/121**, exit0 and `MVP_PORTRAITS_ROOT` marker, no errors or warnings.
- All four new/old flag combinations in EN/ZH: original control geometry, minimum sizes, wording, fonts, input properties and action connections unchanged. Default and old-female-only images are0 pixels different from frozen pre-wiring growth. Explicit all-flags-off management/portrait default parity also passes.
- EN/ZH actual captures for male, Liang, Zhao and corrected Ji; original female mapping also checked. Hero appearance does not affect companion identity. Actual party-button clicks switch correctly; all five cached textures retain the same object identity on subsequent selection.
- Real node-open/close clicks hide/restore. Bad identity argument types, unknown selected ID, unknown hero appearance, cold missing image and cold wrong raw hash refuse without placeholder or script errors. Temporary test-only helper copies change only the invalid image-path/hash literal; no package asset is renamed/modified for these cases.
- Actual overlapping HSlider refuses without moving it; passive decoration is ignored. No original label is shrunk, moved, clipped or relabeled.
- Real map → Characters & Jobs → Back route passes with new and old portrait flags plus management/navigation/music flags. Exactly the generic male helper appears; management skin applies; map returns and hero resource state, party and destination remain unchanged.

No new game failure occurred in these two runs. The producer's earlier isolated94-check result used a filtered certificate-store diagnostic; it is described only as producer evidence and is not represented as a clean application run here. Root's121-check final log is unfiltered and clean. The first root capture labels included array punctuation; final probe sanitizes filenames, and those first-run duplicate files remain in an ignored work folder rather than the integration evidence directory.

## Source-bound handoff

All root integration/test files use tag `20261019-185434-7c95e421`:

- Final growth raw SHA: `2c4dca616acf3027a171ca8f5c53307e3edb7f8113b76622ac33c46dceded91f`; frozen before: `bb9ff55479a308fb4ee84e0479a9a10cf673f7109206df2a9ae5f697c262c80c`.
- Generic helper raw SHA: `0a211d3351d93264eab705d18241a86f90a1cd2342f4b62bb35517b88ace2dde`.
- Builder raw SHA: `897ad2a052460bee8f16be326c79d5df31fd01e1f8895e754baeb578f6757220`.
- New package: `game/assets/portraits/mvp-display-v01/` (four PNG/ORA/manifest/checksum sets).
- Helper: `game/scripts/rpg-2-star-ocean-the-second_mvp-display_portrait-helper_v01_20261019-185434-7c95e421.gd`.
- Builder, independent oracle and actual probe under `tools/`, respectively `…_mvp-display_portrait-builder…py`, `…_mvp-display_independent-package-check…py`, `…_mvp-display_actual-runtime-check…gd`.
- `outputs/mvp-portraits-v01/` contains frozen growth, actual separate captures, first/final logs,121-check report, invalid-helper fixtures, prior Ji and the `…_mvp-display_source-bound-proof…json` with raw source/package/evidence hashes and file list.

All source/proof hashes are raw SHA-256, final source text LF, no hidden normalization. The checker’s explanatory compression text and proof metadata were clarified after its62-check run; validation logic did not change. No ledger/index/Git/Site/provider/account operation or other existing game script edit was performed. No audible listening, native ORA GUI Save As/reopen, artistic acceptance or full-sprite readiness is claimed.
