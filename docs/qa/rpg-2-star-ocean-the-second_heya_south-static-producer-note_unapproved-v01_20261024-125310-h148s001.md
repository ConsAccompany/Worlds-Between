# Heya south static — producer QA note (UNAPPROVED)

Task: `content.char.heya.static-south` (batch 148). Producer: Claude. Not creator/art approver.
Base HEAD: `4ffeefb4f4d6641d00ddca51b1d8f758cf9e2fbe`. Status: `UNAPPROVED`, `approval=false`.
Canonical criterion: south native pixel static (48 logical px) committed with a QA note; the old 32x48
placeholder does not count.

**Classification:** producer deliverable complete and technically checked; **not committed**. The ledger task
remains `todo` until the coordinator commits and records evidence. No art approval, runtime/default adoption,
motion review, or GUI save/reopen reliability is claimed.

## Meter snapshot

Production 62.3%, inspection 21.6%, approval 7.8% at start. After: unchanged (pending coordinator ledger read).
I did not edit the ledger, Bible, registry, index, defaults or scoring.

## Scope confirmation

Wrote only:

- `tools/*heya*` static author/check/native/fit (four new tools, listed below)
- `outputs/heya-s148/`
- `game/assets/characters/heya-native-v01/south/`
- this `docs/qa/*heya*south-static*` note

No shared ledger/Bible/registry/index/default/settings changes, no commit, no push, no paid route, no permission
bypass. Existing dirty/staged work was preserved (the pre-existing registry modification was not touched).
No existing destination bytes were replaced, so `tools/wb_safe_replace.py` was not needed and no backup was
created; the game package is entirely new.

## Source identity and Bible override

- Subject: Heya / 赫娅, Bible character-26 / companion #26, female 44, clinician who respects a patient's
  bodily autonomy. Restrained patient closed-lip smile.
- Identity anchors: auburn **braided coil LOW at the nape**, cool grey-white **medical scarf**, dark-red
  **emergency bag**.
- Concept reference: `outputs/rpg-2-star-ocean-the-second_heya_character-sheet_v01_20261013-192811-6cbcb12e.png`
  (raw sha256 `918e8a17ea297a1eece49b4240712b19c08fab09eadc29eb7620d77b9a68e3e0`), UNAPPROVED identity reference;
  hues chosen by eye, no pixels sampled.
- Bible source identity overrides the sheet's inconsistencies: the sheet's white head-veil would hide the
  low auburn coil, so it is omitted; the sheet's long dark-red shawl is reduced to the canonical dark-red
  emergency bag at the character's left hip. The concept's herb sprig is kept as a small chest accent.
- Sea of Stars direction contract read:
  `docs/design/rpg-2-star-ocean-the-second_characters_sea-of-stars-style-direction_v01_20261020-181026-f5938409.md`.

## Produced package

- Native canvas 80x112, pivot (40,104), body rows 8..103, display scale 0.5 = **48 logical px**.
- Binary alpha, transparent border, 35 declared/used colours (<=40 PXO grid), 13 genuine visible role layers,
  10 isolated texels (<=24), silhouette width 41 px, chest width 33 px (slim mature female, not the male
  stocky gate).
- Layers bottom-to-top: boots, dress, coat, apron, belt, strap, bag, arms, herb, face, hair, braid, scarf,
  hidden guides.
- Hard identity gates (not tuned to pass): low coil rows 25..35 with 67 texels on each side of the neck;
  scarf row span 33..62 with 257 texels; bag 244 texels at mean x 58.5 (character's left / screen right);
  restrained smile 8 mouth texels, width 6, no teeth; coat open front reveals the charcoal underdress;
  herb visible.
- Actual editable PXO/ORA are layered and deterministic; PNG is the flat composite. Palette and manifest are
  included. The old 32x48 placeholder was neither modified nor used; no `*heya*` old placeholder PNG was
  found under `game/assets/characters/native-animation`, and the delivered file is a new 80x112 package.

## Actual commands and outcomes

All commands ran with the project interpreter `../tooling/venv/bin/python -X utf8 -I`; **no denial occurred
this session**. The first command was a read-only smoke of the committed Yanke author, which returned
`YANKE_SOUTH_V01_ALL_OK`.

1. `../tooling/venv/bin/python -X utf8 -I tools/rpg-2-star-ocean-the-second_heya_south-static-author_unapproved-v01_20261024-125310-h148s001.py preview`
   - First attempt: **FAIL** — `isolated_texels` 88 > 24 (`HEYA_SOUTH_V01_FAIL`). Retained here; the
     strap, boot eyelets, braid/face edge details and outline stair-steps were redesigned.
   - Final preview: all gates pass, 10 isolated texels.
2. `... heya_south-static-author ... build`
   - First attempt after the art fix: all art gates passed but the tool's status line returned `FAIL`
     because the not-yet-installed destination was `null`. Fixed the build status predicate; rerun exit 0,
     `HEYA_SOUTH_V01_ALL_OK`, fresh staging written.
3. `... heya_south-static-author ... install` — exit 0, `HEYA_SOUTH_V01_ALL_OK` (new destination, no overwrite).
4. `... heya_south-static-author ... check` — exit 0, `HEYA_SOUTH_V01_ALL_OK`; staging and installed bytes match
   the deterministic rebuild.
5. `... heya_static-source-check ... --root . --out outputs/heya-s148/independent-1` — exit 0,
   `HEYA_S148_INDEPENDENT 39 / 39`, `FAILURES []`. The checker does not import the author. Malformed controls
   all detected: corrupt hash, tampered PNG pixel, visible guides, high bun, teeth, missing scarf, bag moved to
   the wrong hip.
6. `... heya_static-native-pixelorama-check ... --out outputs/heya-s148/native-1` — exit 0,
   `HEYA_S148_NATIVE_PIXELORAMA PASS`; all 11 equality gates true (PXO flat/split, every visible layer exact,
   ORA flat, merged composite, package bytes unchanged, inputs unchanged, no visible guide export).
   `diagnostic_clean=false` is retained separately: 4 `custom_samplers` shader diagnostics per run. This is
   not an application-diagnostic pass and not a GUI result.
7. `... heya_south-static-source-fit ...` — exit 0, `HEYA_S148_SOUTH_SOURCE_FIT PASS`; 4 captures at 640x360
   (city/scifi.city bright + ruins/scifi.ruins dark, en/zh), source sha256 unchanged, checked runner passed,
   manifest `runtimeAdopted=false`, `artApproved=false`. All four crops inspected; Chinese label renders.

## Visual inspection (producer, not approval)

At 48 logical px in the bright city and dark ruins captures, the pale coat/scarf silhouette, auburn low side
coil masses and dark-red bag read. The low coil is visible as two auburn plaited masses below the ears with
alternating light/dark bands; at 1x the plait detail is subtle and the front view occludes the nape center, so
a human art reviewer should judge whether it reads as "braided coil low at nape" rather than two low buns.
The restrained smile reads at x6/x12 and is subtle at 1x, as expected. The white/grey scarf is visually large
and dominates the upper torso. These are honest limitations, not approval.

## Evidence paths and raw sha256

Tools:

- `tools/rpg-2-star-ocean-the-second_heya_south-static-author_unapproved-v01_20261024-125310-h148s001.py`
  `3bccc473faba713b7ea096ffa9154dd7b59f91fcc303b393e421ccd2bca1b31e`
- `tools/rpg-2-star-ocean-the-second_heya_static-source-check_v01_20261024-125310-h148s001.py`
  `382b6e5a69b7476d3cec7dc9663b9caa7af70f95caf3fb75315006fb7030eeca`
- `tools/rpg-2-star-ocean-the-second_heya_static-native-pixelorama-check_v01_20261024-125310-h148s001.py`
  `11cd4a512c6160afb106b54e8c8753afe46485ac98f682e5f86f53437fe94eca`
- `tools/rpg-2-star-ocean-the-second_heya_south-static-source-fit_v01_20261024-125310-h148s001.py`
  `07995d45a9afdaf076da43f6ad4f5fe914c4fcdf06a25e4a6974aef9fdde88be`

Installed game package (`game/assets/characters/heya-native-v01/south/`):

- `rpg-2-star-ocean-the-second_heya_south-static_unapproved-v01_20261024-125310-231d2b03.png`
  `f6e60682bc7f5290aff11ec1154e515137a2b0f66a7fd5141ef4a9afa755d2c3`
- `rpg-2-star-ocean-the-second_heya_south-edit_unapproved-v01_20261024-125310-9665bd23.pxo`
  `f5613b9d4b787e694eddf0c76bb0de28535495849d427d838c30647b7257b12a`
- `rpg-2-star-ocean-the-second_heya_south-edit_unapproved-v01_20261024-125310-42e46403.ora`
  `694e105375eded54d605698f6c65862f152a3e0c63a2462dd90fe4073c8aff36`
- `rpg-2-star-ocean-the-second_heya_south-palette_unapproved-v01_20261024-125310-a902fe49.json`
  `a699845e99d7cc794402b5e31b3e515cafb5459645fbab05d5a4eefb4071e838`
- `rpg-2-star-ocean-the-second_heya_south-manifest_unapproved-v01_20261024-125310-a9210ea1.json`
  `d6ddec7e38d74083e6a774d96e7235c9b64fe5ba7b7ec3664f5067f82217d80c`

Staging has identical hashes under `outputs/heya-s148/staging/south/`. Preview and evidence:

- `outputs/heya-s148/author/rpg-2-star-ocean-the-second_heya_south-preview-x12_unapproved-v01_20261024-125310-f6e60682.png`
  `7accdc7a6a21d4ec0c4d212d687a3f4d768d20cd1b93e6f5747c9c61399e07fb` (final visual)
- `outputs/heya-s148/author/build.log` `5607221932da94c88de5c9e95301a1296e7d4b91738edb12ef560a9b792200ee`
- `outputs/heya-s148/author/check.log` `01e6d86f408fbbe9496257819a9f0d6e601477070eafcd5d071b3294e3725ee0`
- `outputs/heya-s148/author/install.log` `01e6d86f408fbbe9496257819a9f0d6e601477070eafcd5d071b3294e3725ee0`
- `outputs/heya-s148/author/rpg-2-star-ocean-the-second_heya_south-staging-output-paths-rawhashes_unapproved-v01_20261024-125310-bf43965e.json`
  `2b141de029108f1ca452a293a28404d75f6e7d0cb3372b7b70f27be38074b0fb`
- `outputs/heya-s148/independent-1/rpg-2-star-ocean-the-second_heya_independent-source-proof_v01_20261024-125310-h148s001.json`
  `82f9a847d5613b96078926b069fa937c2ff13c22ea395bec99d7e0a46bbc8039`
- `outputs/heya-s148/independent-1/rpg-2-star-ocean-the-second_heya_corrupt-hash-control_test-only-v01_20261024-125310-h148s001.json`
  `9af8ad5a719547912484e06b15e3609be4a9b3bd1610744ad09184933b801479`
- `outputs/heya-s148/native-1/20261024-125827-89a18ae0/rpg-2-star-ocean-the-second_heya_native-pixelorama-export-report_test-only-v01_20261024-125310-h148s001.json`
  (native report; contains run logs and shader diagnostics)
- `outputs/heya-s148/rpg-2-star-ocean-the-second_heya_south_source-fit-proof_test-only-v01_20261024-125310-h148s001-fit.json`
  `9399776fcc23501f64fc137f8222c9a81e0fa81ea11993acb7c3ba0ab4f9b01f`
- Fit captures (all 640x360):
  - city-en `140aaa46e8888063c176475322693f07916d5a86024fdf31f64b91b5f1ba4ad8`
  - city-zh `d3a0236ccadd0c3977cf57b09b6f21df807d9145f48518308c144a83327609e4`
  - ruins-en `a9d39980daf5820f8a1c2c2c6b0b2c3d1ac06155c08fc0f38085c528a492109b`
  - ruins-zh `8968a49749ff0ab0ea325e5c84d0ab5c7f011cda473c7aa260b8897907220b20`
- Inspected x4 crops: city-en, city-zh, ruins-en, ruins-zh under `outputs/heya-s148/fit/crop-*`.

## Failed checks / limitations retained

- Initial author preview failed `isolated_texels_le_24` at 88; fixed and rechecked to 10. The failed build is
  recorded here because the passing log overwrote the transient tool output.
- Native Pixelorama `diagnostic_clean=false` with shader-sampler diagnostics; export equality passed only.
  No GUI SaveAs/reopen proof; no animated-bank GUI proof.
- No runtime wiring, default adoption, other directions, motion, interaction, or art approval.
- No commit/push; ledger/Bible remain coordinator-owned and currently unchanged.

## Exact coordinator verification/commit commands

From `/home/kel/projects/worlds-between/repo`:

```bash
git add -- \
  tools/rpg-2-star-ocean-the-second_heya_south-static-author_unapproved-v01_20261024-125310-h148s001.py \
  tools/rpg-2-star-ocean-the-second_heya_static-source-check_v01_20261024-125310-h148s001.py \
  tools/rpg-2-star-ocean-the-second_heya_static-native-pixelorama-check_v01_20261024-125310-h148s001.py \
  tools/rpg-2-star-ocean-the-second_heya_south-static-source-fit_v01_20261024-125310-h148s001.py \
  outputs/heya-s148 \
  game/assets/characters/heya-native-v01/south \
  docs/qa/rpg-2-star-ocean-the-second_heya_south-static-producer-note_unapproved-v01_20261024-125310-h148s001.md
```

Before commit, add the established binary attributes (coordinator-owned `.gitattributes`; not edited by the
producer) so the raw bytes are preserved on checkout:

```text
game/assets/characters/heya-native-v01/south/** -text -eol
outputs/heya-s148/** -text -eol
```

Then verify the staged bytes with `git check-attr -a` and `git show :PATH | sha256sum`, and re-run:

```bash
../tooling/venv/bin/python -X utf8 -I tools/rpg-2-star-ocean-the-second_heya_static-source-check_v01_20261024-125310-h148s001.py --root . --out outputs/heya-s148/independent-2
../tooling/venv/bin/python -X utf8 -I tools/rpg-2-star-ocean-the-second_heya_static-native-pixelorama-check_v01_20261024-125310-h148s001.py --out outputs/heya-s148/native-2
../tooling/venv/bin/python -X utf8 -I tools/rpg-2-star-ocean-the-second_heya_south-static-source-fit_v01_20261024-125310-h148s001.py
```

Commit only after those pass, e.g.:

```bash
git commit -m "[verified] Produce Heya south static source; retain native and human gates"
```

Then record the evidence/task transition through the existing ledger CLI
`tools/rpg-2-star-ocean-the-second_production-completion_ledger-cli_v01_20261018-140533-3b436630.js` (coordinator
owns the exact status/evidence command). Do not infer creator art approval.
