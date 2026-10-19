# Female protagonist display portrait: exact crop and opt-in integration

Task: `content.char.protagonist-female.display`. Producer: DeepSeek. Independent inspection, bounded correction and growth-screen wiring: Codex. This is a technical candidate, not creator art approval, accepted character canon, a sprite-set completion or completion of the whole UI kit.

## Results

- Independent package checks: **17/17**. All **74,329** RGBA crop pixels match source rectangle `[952,42,1191,353]` of the original 1916×821 concept sheet. No resampling, repainting, background removal or invented pixels.
- The canonical PNG and single-layer ORA preserve the original producer compressed bytes exactly. PNG SHA `481182891a0bf9b110a2ba05ca69c9c902b9d208255cf76bddd1aeb6c15868f6`; ORA SHA `2351f7f6a501974db81b857053ea26082dc78d111dc8607df6bb651465260a85`. The ORA layer PNG is byte-identical to the crop, with exact merged pixels. No PXO or semantic anatomy-layer claim.
- Two fresh ignored rebuilds with the bundled runtime are byte-identical to each other. Their compressed PNG/ORA bytes differ from the producer runtime, while every decoded pixel is identical. This runtime/zlib difference is disclosed and the original art bytes are preserved.
- Actual windowed Godot 4.7.2, native 640×360, Dummy audio backend: **143/143**. Final checked-runner exit 0 and required success marker; final raw log contains no script/runtime errors or warnings. Fresh APPDATA/LOCALAPPDATA; 100-second runner deadline.
- Real growth scene checked in EN and ZH, with management skin off and on: default portrait-off image is **0 pixels different** from the frozen pre-wiring growth script, and original visible/hidden control rectangles, minimum sizes, text and input properties are preserved.
- Fixed portrait rectangle `(522,88,96,124)`, native texture 239×311, aspect-preserving display, mouse-ignore/focus-none and below-overlay draw order passed. No existing label was shrunk, moved or clipped. Passive background/skin plates are ignored by collision checks; actual text and interactive conflicts cause refusal.
- Actual party-button clicks hide for a companion, restore for the female hero; male appearance and node overlay hide the portrait. A real temporary button below the hidden portrait remains clickable. Real node-open/close clicks passed. Malformed JSON/object/field types, fractional dimensions, bad paths, missing files and wrong declared identity/hash contracts refuse safely, then the valid package recovers. Real overlapping text refuses without changing that text or position.
- One real map → Characters & Jobs → Back route passed with `--female-display-portrait-pilot --management-ui-skin-pilot --navigation-ui-skin-pilot --themed-music-pilot`. Female portrait and management skin are applied, the map returns normally, and hero state/party/destination remain unchanged.

## Provenance and corrections

The source sheet is **AI-generated, UNAPPROVED CONCEPT** art. `crop.ai_generated=false` describes only the crop operation; it does not claim that the original sheet is human art. Canonical provenance explicitly records `original_source_ai_generated=true`, `new_generative_processing=false`, `human_artist=false`, and no canon/static/full-sprite approval.

The producer's compound `.manifest.json` filename was normalized to `display-portrait-manifest_…json`, with current helper/builder paths and checksums. The helper gained strict type guards, exact integral finite-number validation, fixed image SHA binding and bare-filename-only resolution. The overlap guard excludes passive decoration while retaining actual text/interactive obstruction. The constructor performs no file/texture/metadata load. The flag is OFF by default; default path creates no portrait controls. Only `game/scripts/growth_screen.gd` was wired among existing game scripts.

The shipped builder documents and reproduces the exact ROI. Because its PNG compression can vary by Python/zlib runtime, reproduction means pixel identity plus same-runtime deterministic bytes; it does not promise cross-runtime compressed-byte equality. The original producer PNG/ORA remain authoritative.

## Preserved failures

- `actual-first-log`: 121/136. The integration writer initially decoded the source's middle dot with Windows default encoding, producing `Â·`; this changed default labels and pixels. Corrected to exact original UTF-8 `·`, without changing selected wording.
- `actual-second-log`: 132/136. A queued-for-deletion test-only click receiver still existed when the overlap guard correctly scanned it. Fixed the harness to synchronously remove that owned test fixture before asserting restoration; no game tolerance was weakened.
- `actual-third-log`: the 136 growth checks reached the added normal route, where the harness incorrectly typed the map's Node2D root as Control. The checked runner stopped on the diagnostic. Fixed only the test variable to Node.
- `actual-final-log` passed 143/143. After removing an unused, non-shipped schema-file claim from the manifest, the exact final package was rerun: `actual-final-source-log` passed 143/143.
- The independent Python checker initially had an escaped-string syntax typo in its extended-path function; corrected to explicit character construction before its successful 17/17 run. No package check had executed at that failure.

## Source-bound evidence and scope

All new source/evidence uses tag `20261019-182839-4d72f1c6`.

- Source/hash proof: `outputs/female-portrait-v01/rpg-2-star-ocean-the-second_female-display_source-bound-proof_v01_20261019-182839-4d72f1c6.json` (raw SHA-256 for source sheet, final builder/helper/growth source, test/checker and all package artifacts; LF source text, no hidden normalization).
- Package: `game/assets/portraits/female-display-v01/` (PNG, ORA, normalized manifest, checksum receipt).
- Helper: `game/scripts/rpg-2-star-ocean-the-second_protagonist-female_display-portrait-helper_v01_20261019-182839-4d72f1c6.gd`.
- Builder and independent checker: `tools/rpg-2-star-ocean-the-second_protagonist-female_display-portrait-builder_v01_20261019-182839-4d72f1c6.py` and `tools/rpg-2-star-ocean-the-second_female-display_independent-package-check_v01_20261019-182839-4d72f1c6.py`.
- Actual runtime probe: `tools/rpg-2-star-ocean-the-second_female-display_actual-runtime-check_v01_20261019-182839-4d72f1c6.gd`.
- Captures, frozen pre-wiring source, first/final logs, malformed fixtures and the 143-check report: `outputs/female-portrait-v01/`. EN/ZH skin-on portraits and combined normal-route captures are actual game frames, not mockups. Root visually inspects and decides what to present.

No ledger, Git/index, Site, account/provider state, other game scripts, character assignment or approval was changed. The source remains unapproved pending creator review. No native ORA GUI open/edit/save/reopen or audio listening is claimed.

## Coordinator closeout

Codex personally inspected native EN/ZH skin-on captures and the actual combined-flags growth screen. The source portrait is legible, fits the reserved rectangle, and does not cover the listed controls. This observation approves technical integration only; its beige source background and concept identity remain subject to creator review. Raw hashes of all 10 source/package files were independently rechecked before staging. Only this single display-image production task receives 2 points; whole UI portraits, full sprites, art approval and playtests remain unchanged.
