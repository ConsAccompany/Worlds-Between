# Yanke north static source QA — `content.char.yanke.static-north` (UNAPPROVED v01)

Recorded 2026-10-24T09:25Z author stamp; QA closed 2026-10-24T09:32Z. Task-map owner **claude**, **2 points**
(frozen). Actual producer: **deepseek-flash** through the authorized adapter; this note records the actual producer
and does not claim a Claude run, a ledger change or art approval. Canonical task remains `todo`; this producer did
not mark it done, stage Git paths or edit the shared ledger/Bible/registry/defaults.

## Verdict

Yanke now has a native 80x112 **back-facing north** idle static with editable PXO/ORA sources, a declared palette,
hidden guides, explicit pivot/body rows and a 48-logical-pixel display height. It passes the deterministic author
build/check (`YANKE_NORTH_V01_ALL_OK`, hard failures `[]`), an independent source checker
(`YANKE_N101_NORTH_INDEPENDENT 43 / 43`, failures `[]`), malformed wrong-direction and corrupt-hash rejection
controls, Pixelorama 1.2.3 PXO/ORA export equality (11/11 gates), and four checked bilingual source-fit captures
(`JIANG37_SOURCE_FIT_PASS captures=4`, `CHECKED_RUN PASS`). This is **source production only**: no runtime/default
adoption, no motion, no GUI SaveAs/reopen, no normal-game actor integration and no creator art approval.

## Base, scope and scores

- Tested base revision: `f8e628c6e568cd6c1f724038432472df1dc34f46` (south and west source packages committed).
- Dependency `content.char.yanke.static-south` is done; west is a sibling reference only.
- Write scope used: `game/assets/characters/yanke-native-v01/north/`, `outputs/yanke-n101/north/` plus the
  north contract under `outputs/yanke-n101/`, `tools/*yanke*north*`, `docs/qa/*yanke*north*`.
- Pre-existing `outputs/yanke-n101/hermes101/` coordinator smoke files and all unrelated dirty/staged work were
  preserved. Shared ledger/Bible/registry/Git index were not read or changed for scoring.
- No canonical meter transition is claimed. Task-map value remains 2 points; inspection and art approval are
  separate and unchanged.

## Identity and north view

Bible character-07 (identity reference only; concept sheet UNAPPROVED, no pixels sampled): 37-year-old friendly
heavy-tool craftsperson; short curly dark-brown hair, thick beard; cream work shirt; olive-green work apron with
worn character; broad leather shoulder straps and brass buckles; dark-brown baggy work trousers; heavy brown
leather boots; red work rag at the character's right hip; notched heavy steel tool head on a wooden handle slung
over the right shoulder.

North is a **true back view**, authored in absolute back coordinates, not rotated, squashed, recoloured or
mirrored from south/west. The camera sees the back of the hair mass, ears, nape, back of the shirt and harness,
trouser seat and back pockets, boot heels/soles, and the tool carried across the back. There is **no painted front
face**: no eye, iris or mouth colour is used anywhere in the composite, and the `face` layer is skin-only ears and
nape. The character's right side is screen right in a back view, so the red rag and the steel head are on screen
right and the handle runs down-left to the left hip.

## Contract and measured metrics

| Property | Value |
| --- | --- |
| Canvas | 80x112 source px (density 2) |
| Opaque body rows | 8..103 = 96 source px |
| Display scale / logical height | 0.5 / **48 logical px** |
| Pivot | (40,104), inside row-103 feet span |
| Declared palette | 38 entries; 35 used (24..48 gate) |
| Genuine visible role layers | 12 (>=8 gate) |
| Isolated texels | **0** (<=24 gate; deterministic 4-neighbour despeckle after outline) |
| Silhouette width | 58 source px |
| Opaque shoulder columns rows 38..46 | 55 (>=34 gate) |
| Steel tool texels (k1/k2/k3) | 177 (>=120 gate) |
| Tool head bounds | x57..71, y11..29 (above the right shoulder) |
| Handle bounds | x22..66, y30..82 (diagonal across the back) |
| North vs south alpha | 903 differing texels (>=400) |
| North vs mirrored south alpha | 641 differing texels (>=400) |
| North vs west alpha | 1972 differing texels (>=400) |
| North vs mirrored west alpha | 2220 differing texels (>=400) |
| Front-face colours in composite | 0 (eyes/iris/mouth absent) |
| Face layer | skin-only ears + nape; no eye/mouth components |
| Hair / beard | 693 / 78 visible texels |
| Contributions (hammer, grip, harness, trousers, apron, hair, beard, face) | 233, 235, 375, 455, 263, 693, 78, 107 |
| Alpha / border | binary / no opaque border |
| Layers | hammer, boots, trousers, shirt, apron, harness, grip, belt, arms, face, hair, beard, guides (hidden) |

The south hard gate `face_has_eye` is replaced for north by the declared back-view rule
`north_face_no_eyes_or_mouth` plus the independent zero-face-feature and skin-only-face checks. All other south
hard gates and thresholds are retained unchanged.

## Deliverables — raw SHA256, no normalization

Package under `game/assets/characters/yanke-native-v01/north/`:

| Purpose | File | Raw SHA256 |
| --- | --- | --- |
| Native static PNG | `rpg-2-star-ocean-the-second_yanke_north-static_unapproved-v01_20261024-092500-1acf16c9.png` | `0d08dc76106cb93a44de16af9cc631cc74edce418e99e3b4f35525ac9d0fafca` |
| Editable Pixelorama PXO | `rpg-2-star-ocean-the-second_yanke_north-edit_unapproved-v01_20261024-092500-1e3c80a0.pxo` | `975938e4eb6442db091c7d1c5e49f880e0642a05d284a46be2c437a0feaf0562` |
| Editable ORA | `rpg-2-star-ocean-the-second_yanke_north-edit_unapproved-v01_20261024-092500-f6a16389.ora` | `0b43a0be2f7a9d78c43855236d019ede89950a6619c1d9730724534a0f111495` |
| Declared palette | `rpg-2-star-ocean-the-second_yanke_north-palette_unapproved-v01_20261024-092500-aa9b6f33.json` | `27e68c2ea9dceaed41c4bfa7940e934473ebe9b21a1f16b29f3b419a06fd0774` |
| Manifest | `rpg-2-star-ocean-the-second_yanke_north-manifest_unapproved-v01_20261024-092500-9eb0ab17.json` | `57aa3478c5036b3676e97abf58998876ccbb6a1e0765af02621b1eadf751a5fd` |
| Godot ignore marker | `.gdignore` (0 bytes) | `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855` |

Author, checkers and contract:

| Purpose | File | Raw SHA256 |
| --- | --- | --- |
| Deterministic author / build | `tools/rpg-2-star-ocean-the-second_yanke_north-static-author_unapproved-v01_20261024-092500-n101north.py` | `59115cffaeb19576a27188e55439c50dc05e865a6fb65763dc15928bcb4caac6` |
| Independent source checker | `tools/rpg-2-star-ocean-the-second_yanke_north-static-source-check_v01_20261024-092500-n101north.py` | `526b377591ef00f17cf0851f0aa52ef875949dfde251829a0e74eba7290469fa` |
| Native Pixelorama export checker | `tools/rpg-2-star-ocean-the-second_yanke_north-static-native-pixelorama-check_v01_20261024-092500-n101north.py` | `544a233cfc2598f9a24c86cfddd2db6785ff14707ce05401306b772b370929e0` |
| Bounded source-fit runner | `tools/rpg-2-star-ocean-the-second_yanke_north-static-source-fit_v01_20261024-092500-n101north.py` | `426451b074360534de132aff34adee0d813514fcabebbba2e49215828ce80d08` |
| Bounded contract (written before authoring) | `outputs/yanke-n101/rpg-2-star-ocean-the-second_yanke_north-style-source-contract_unapproved-v01_20261024-092500-n101north.md` | `27c24f5dce0b62882ec66ca32886d985400ca09eb1ea0c0da63daa8fdc7cebbc` |

## Evidence — raw SHA256

| Purpose | File | Raw SHA256 |
| --- | --- | --- |
| Author check log | `outputs/yanke-n101/north/author-check.log` | `91af41a08c796bdd7381a33447f5d176601ee9ee01790263865dfcda0b789b97` |
| Independent 43/43 log | `outputs/yanke-n101/north/independent-check.log` | `e02a76c3390498b3b37653ab957153726a4a5253e18ad54a6f6b2d54297f2442` |
| Independent proof | `outputs/yanke-n101/north/independent-r2/rpg-2-star-ocean-the-second_yanke_north_independent-source-proof_v01_20261024-092500-n101north.json` | `7614e76ad15d6a920520f107b38bb4783ee7d6f5cb04e8e2b26f007b227f683b` |
| Wrong-direction control log (expected rejection) | `outputs/yanke-n101/north/controls/wrong-direction/check.log` | `74884b291872231463b9505a0f77d3301f0112998b8296723d63e44d5d1bd1c3` |
| Corrupt-hash control log (expected rejection) | `outputs/yanke-n101/north/controls/corrupt-hash/check.log` | `b5b5f1af2f5287a6bd3329c9b24b61c190d81db86c8390c085280ccdd2d29e64` |
| Native export report | `outputs/yanke-n101/north/native/20261024-092716-91b4ddd0/rpg-2-star-ocean-the-second_yanke_north_native-pixelorama-export-report_test-only-v01_20261024-092500-n101north.json` | `958f5f3b9adff36cce68036186e711ab73c234181680aac9b6bd30a74d30956b` |
| Source-fit proof (fit-r2) | `outputs/yanke-n101/north/rpg-2-star-ocean-the-second_yanke_north_source-fit-proof_test-only-v01_20261024-092500-n101north-fit-r2.json` | `f5e9b5c6c9f63034a48286c17607db972fff1c9b0861a5b1ce265c6f65eeafaa` |
| Source-fit log (fit-r2) | `outputs/yanke-n101/north/fit-r2.runner.log` | `0e2337bc6f0fa7c8a832d1a8d6c5ed7d98214c35c21f922f120b702d3ecefc3f` |
| Failed fit attempt 1 (xvfb TMPDIR denied) | `outputs/yanke-n101/north/fit-attempt1-failure.log` | `4c375a634a1d4d96ed3e95ff07bff9fc3d774a6e54f8a11c681b0cf8a7bab73f` |
| Failed fit attempt 2 (Godot user:// log denied) | `outputs/yanke-n101/north/fit-attempt2-failure.log` | `2cebe6a587bf8180b46b0b3cb92fbeef5d1f55d4bfce07fcb2fd148a644e4f82` |
| Fit city EN | `outputs/yanke-n101/north/fit-r2/rpg-2-star-ocean-the-second_yanke-north_source-fit-city-en_test-only-640-v01_20261024-092500-n101north.png` | `4974854d00d1ca9603b62d63ba2f081de421e2cff212fecbfdef5769f94d2add` |
| Fit city ZH | `...city-zh...png` (same directory) | `275e4c057ff0eee19f0a17a748960bf89f63eb7429035cb802a6640b09a302c8` |
| Fit ruins EN | `...ruins-en...png` (same directory) | `c6c10462ddab907c2be5bfe5124158563fb38f22afce3dab94c182f3a31c46fa` |
| Fit ruins ZH | `...ruins-zh...png` (same directory) | `fc8c6af839706e82735d4d6e2262c87f5284d92e95daf18d690b5a7f21a05335` |
| Source preview x6 (non-source) | `outputs/yanke-n101/north/author/rpg-2-star-ocean-the-second_yanke_north-preview-x6_unapproved-v01_20261024-092500-0d08dc76.png` | at `0d08dc76...` revision; derived from the tested PNG |
| Full raw-hash listing | `outputs/yanke-n101/north/hash-listing.json` | generated after the final run (files, not itself) |

The native report hashes the tested PNG/PXO/ORA as `0d08dc76...` / `975938e4...` / `0b43a0be...` and records
`equality_passed:true` with `package_bytes_unchanged:true`. Export equality is **not** application cleanliness:
`diagnostic_clean:false`, with four `custom_samplers` sampler/shader `ERROR` lines in each of the PXO-flat,
PXO-split and ORA-flat routes; the ORA route also retains renderer RID-leak, out-of-bounds index, null `rp_node`,
ancestor-control and exit-leak diagnostics. These are retained and not claimed as a pass.

## Exact rerunnable commands

From `/home/kel/projects/worlds-between/repo`, with the project tooling venv:

```bash
WB_PY=/home/kel/projects/worlds-between/tooling/venv/bin/python

# deterministic author check against the installed package (read-only)
$WB_PY -X utf8 -I tools/rpg-2-star-ocean-the-second_yanke_north-static-author_unapproved-v01_20261024-092500-n101north.py check

# independent source checker (choose a fresh --out directory)
$WB_PY -X utf8 -I tools/rpg-2-star-ocean-the-second_yanke_north-static-source-check_v01_20261024-092500-n101north.py --root . --out outputs/yanke-n101/north/independent-r3

# malformed-source controls (expected exit 1)
$WB_PY -X utf8 -I tools/rpg-2-star-ocean-the-second_yanke_north-static-source-check_v01_20261024-092500-n101north.py --root . --package outputs/yanke-n101/north/controls/wrong-direction/package --out outputs/yanke-n101/north/controls/wrong-direction/proof-r2
$WB_PY -X utf8 -I tools/rpg-2-star-ocean-the-second_yanke_north-static-source-check_v01_20261024-092500-n101north.py --root . --package outputs/yanke-n101/north/controls/corrupt-hash/package --out outputs/yanke-n101/north/controls/corrupt-hash/proof-r2

# native Pixelorama PXO/ORA export equality (writes a timestamped fresh run dir)
$WB_PY -X utf8 -I tools/rpg-2-star-ocean-the-second_yanke_north-static-native-pixelorama-check_v01_20261024-092500-n101north.py --out outputs/yanke-n101/north/native

# bounded checked Godot source-fit, Dummy audio, Xvfb 640x360, fresh fit-rN on rerun
$WB_PY -X utf8 -I tools/rpg-2-star-ocean-the-second_yanke_north-static-source-fit_v01_20261024-092500-n101north.py
```

Reproduction of the package from the stage uses the same author `build` then `install`; `install` writes only new
or byte-identical files and refuses different existing bytes. No differing destination existed, so no
`tools/wb_safe_replace.py` receipt was required and none was created. Nothing was deleted.

## Failures, limitations and honest state

- Native Pixelorama routes exit 0 and export exactly, but application diagnostics remain and `diagnostic_clean` is
  **false**; GUI SaveAs/reopen was not tested. Do not read export equality as clean application behavior.
- Source-fit is a deterministic **test-only overlay** through the existing generic harness: four 640x360 EN/ZH
  city/ruins captures, `runtimeAdopted:false`, `artApproved:false`. It is not ordinary actor integration, motion,
  occlusion, lighting or human-play credit. The HUD label overlaps the lower capture area by design.
- Two fit attempts failed before the successful run and are preserved: attempt 1 could not create Xvfb's mktemp
  directory under the inherited scratch path; attempt 2 could not open Godot's `user://logs` because HOME/XDG
  were not yet isolated. Fixes were operational (writable TMPDIR, isolated HOME/XDG), not source or threshold
  changes.
- The author applies a deterministic 4-neighbour despeckle after the outline pass so the broad-cluster style gate
  reads 0 isolated texels; alpha, layer ownership, silhouette and role counts are unchanged.
- No old 32x48 Yanke placeholder exists under `game/assets/characters/native-animation`; nothing there was edited
  or counted. The package is a new 80x112 native source.
- Static north only. No runtime wiring, no default selector change, no south/west/east package change, no motion, no
  portrait approval. All art remains UNAPPROVED and creator acceptance is separate.
- The canonical ledger/Bible/registry and Git index were not edited or staged. Coordinator integration and any
  audited ledger transition remain coordinator-owned.

## Explicit scope confirmation

Only these new paths were written: `game/assets/characters/yanke-native-v01/north/` (6 files),
`outputs/yanke-n101/north/` and `outputs/yanke-n101/*yanke_north-style-source-contract*`,
`tools/*yanke*north*` (4 files), and this `docs/qa/*yanke*north*` note. South and west package hashes were verified
unchanged by the author. No published/live content, vault/history, credentials, accounts/billing, provider or
default was touched. No actual permission denial occurred. No Git commit or stage was made.
