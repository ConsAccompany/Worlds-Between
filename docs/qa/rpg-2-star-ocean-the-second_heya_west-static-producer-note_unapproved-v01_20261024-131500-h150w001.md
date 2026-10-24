# Heya west static — producer QA note (UNAPPROVED)

Task: `content.char.heya.static-west` (batch 150). Producer: DeepSeek via the accepted adapter job; not the
creator or art approver. Base HEAD: `5ca658171fb40d2bee0b7055f3101373538031be`; south dependency committed at
`dc8ad3b4` and re-verified byte-identical here. Status: `UNAPPROVED`, `approval=false`, `artApproved=false`,
`runtimeAdopted=false`.

Canonical criterion: **west native pixel static (48 logical px) committed with a QA note; the old 32x48
placeholder does not count.** The source package is produced and technically checked; it is **not committed**.
The coordinator owns integration, the ledger and the commit. No art approval, runtime/default adoption, motion
review, GUI save/reopen reliability or native-diagnostic-clean claim is made.

## Scope confirmation

Wrote only:

- four new Heya-west tools under `tools/` (author, independent source check, native Pixelorama check, source fit);
- `outputs/heya-w150/` (contract, staging, previews, independent/native/fit evidence, disposable Godot home);
- `game/assets/characters/heya-native-v01/west/` (new package; no south/north/east bytes touched);
- this `docs/qa/*heya*west-static*` note.

No shared ledger/Bible/registry/Git index edit, no commit, no push, no default/runtime selection, no scoring
change, no permission bypass. Unrelated dirty/staged work was preserved. The west destination was new, so no
different existing bytes were replaced and `tools/wb_safe_replace.py` was not needed; staging and installed
bytes are identical. Had a different destination existed, the author's `install` path calls the helper.

## Source identity and view contract

- Subject: Heya / 赫娅, Bible character-26 / companion #26, female 44, clinician who respects a patient's
  bodily autonomy; restrained closed-lip smile.
- Canonical anchors: auburn braided coil **LOW at the nape**, cool grey-white **medical scarf**, ivory open
  clinician coat over pale grey-white apron and charcoal underdress, dark-red **emergency bag on the character's
  LEFT**, dark gloves, brown leather boots.
- Identity reference: `outputs/rpg-2-star-ocean-the-second_heya_character-sheet_v01_20261013-192811-6cbcb12e.png`
  (raw sha256 `918e8a17ea297a1eece49b4240712b19c08fab09eadc29eb7620d77b9a68e3e0`), UNAPPROVED; hues chosen by
  eye, no pixels sampled.
- West view: nose toward **screen LEFT**, character's LEFT side toward camera. Reauthored in forward coordinates
  with the Lin Que `P` pen (`s=-1`), not a rotation, squash, recolour or mirror of south.
- Style/source contract:
  `outputs/heya-w150/rpg-2-star-ocean-the-second_heya_west-style-source-contract_unapproved-v01_20261024-131500-h150w001.md`
  (raw sha256 `d79df23a2aa406dc44635511ea71c607721a1751021ffe30f426283961f6b2c1`).

## Produced package

Native canvas 80x112, pivot (40,104), body rows 8..103, display scale 0.5 = **48 logical px**. Binary alpha,
transparent one-pixel border, 33 used colours of a 35-entry declared palette (<=40 PXO grid), 11 genuine visible
role layers, 19 isolated texels (<=24 unchanged limit), profile depth 21 px. Layer order: boots, dress, coat,
apron, belt, strap, bag, arms, herb, face, hair, braid, scarf, hidden guides.

Identity gates (not tuned to pass): nose x=31 / back of head x=46 (nose leads screen left); face width 16,
one eye; low braided coil rows 24..40, 92 texels, mean x 47.47, max x 51; hair crown ends at row 26 (no high
bun); scarf rows 33..55, 173 texels, only cool grey-white colours; bag 305 texels, mean x 39.0, rows 57..81,
on the near/left hip with brass; restrained smile 3 mouth texels, width 2, no teeth; charcoal dress placket
32 composite texels visible in the open coat front; herb 19 texels. South package and palette are byte-identical
to their pinned hashes; no south bytes were replaced.

Installed game package (`game/assets/characters/heya-native-v01/west/`):

- `rpg-2-star-ocean-the-second_heya_west-static_unapproved-v01_20261024-131500-22034c8f.png`
  `f8a167d8df2a554660c01b8cb88e461f878297c8d8da2456a566bdc0c2ed766e`
- `rpg-2-star-ocean-the-second_heya_west-edit_unapproved-v01_20261024-131500-4bc15dd4.pxo`
  `ee5bd72e1b1297c22909b1c952048acd092aeb146ee320dd7d1a8adb54fd6247`
- `rpg-2-star-ocean-the-second_heya_west-edit_unapproved-v01_20261024-131500-3346f283.ora`
  `fc3d332b0b263fba3d6f5be39f38c45b3ed872b76e706471e2671cb4bd4d424b`
- `rpg-2-star-ocean-the-second_heya_west-palette_unapproved-v01_20261024-131500-2b57e26b.json`
  `59491af00cb984ed840489de9e7bd427aea456152ef9f0b1423f0c3f26979d7c`
- `rpg-2-star-ocean-the-second_heya_west-manifest_unapproved-v01_20261024-131500-164571cd.json`
  `75b0519c2b1282dc4441b38a90fa3bc64868a442f1779c436455928fd8897752`

The old 32x48 placeholder was neither modified nor counted; no `*heya*` old placeholder PNG was found under
`game/assets/characters/native-animation`.

## Actual commands and outcomes

All commands ran with the project interpreter `../tooling/venv/bin/python -X utf8 -I`; no permission denial
occurred. Dependent results were checked before the next mutation.

1. Author `preview` — **FAIL** first (see retained failures), then final hard gates `[]` with 19 isolated texels.
2. Author `build` — exit 0, `HEYA_WEST_V01_ALL_OK`; fresh `outputs/heya-w150/staging/west/`.
3. Author `install` — exit 0, `HEYA_WEST_V01_ALL_OK`; new destination, no differing bytes replaced.
4. Author `check` — exit 0, `HEYA_WEST_V01_ALL_OK`; deterministic rebuild, staging and installed bytes match.
5. `... heya_west-static-source-check ... --root . --out outputs/heya-w150/independent-3` — exit 0,
   `HEYA_W150_INDEPENDENT 49 / 49`, `FAILURES []`. Checker does not import the author. All malformed controls
   detected: corrupt hash, tampered PNG pixel, visible guides, wrong direction (mirrored face), high bun,
   missing scarf, bag on the wrong hip, teeth, hidden charcoal dress.
6. `... heya_west-static-native-pixelorama-check ... --out outputs/heya-w150/native-1` — exit 0,
   `HEYA_W150_NATIVE_PIXELORAMA PASS`; all 11 export-equality gates true (PXO flat, every split layer, PXO
   merged, ORA flat, package bytes unchanged, inputs unchanged, no visible guide export).
   `diagnostic_clean=false` is retained separately: 4 `custom_samplers` shader diagnostics in each of the three
   runs, plus in the ORA run a 12-marker failure group including a 14-RID leak, out-of-bounds `p_index`, a null
   `rp_node`, a control-ancestor error, and ObjectDB/resource leaks at exit. This is **not** an
   application-diagnostic pass and **not** a GUI result.
7. `... heya_west-static-source-fit ...` — exit 0, `HEYA_W150_WEST_SOURCE_FIT PASS`; four 640x360 captures
   (city/scifi.city bright + ruins/scifi.ruins dark, en/zh) through the checked runner, OpenGL3, Xvfb and
   **Dummy audio**, source sha256 unchanged, scale 0.5, manifest `runtimeAdopted=false`, `artApproved=false`.
   All four captures and wide crops inspected; the Chinese label renders.

## Retained failures and lessons (not rewritten away)

- First preview: `AttributeError: 'P' object has no attribute 'hline'` — the forward pen exposes `rect`, not
  `hline/vline`; converted to `rect` calls. No package bytes were built.
- Second preview: `ValueError: zero-size array to reduction operation maximum which has no identity` — the mouth
  sat on the face silhouette edge and the outline finish overwrote it; moved the mouth inward and guarded the
  metric. No package bytes were built.
- Third preview: `HEYA_WEST_V01_FAIL`, hard failures `['no_opaque_border', 'guides_hidden_no_overlap',
  'isolated_texels_le_24', 'identity_colours_all', 'profile_face_narrow', 'profile_depth_20_34',
  'profile_one_eye', 'bag_left_hip_west', 'restrained_smile_west']` — strap/bag/arms/herb/face/hair/braid/scarf
  were drawn on the raw layer instead of the forward pen, so negative x wrapped to the canvas edge. Wrapped every
  layer in the pen; no package bytes were built.
- Fourth preview: `HEYA_WEST_V01_FAIL`, hard failure `['identity_colours_all']` — the charcoal underdress was
  fully covered by the coat (1 visible texel). Widened the open coat front to expose a 4 px charcoal placket;
  then all gates passed. No package bytes were installed before the fix.
- Native application diagnostics remain: PXO runs 4 `custom_samplers` each; the ORA run has 12 markers
  (RID/ObjectDB/resource leaks at exit, out-of-bounds `p_index`, null `rp_node`, control-ancestor error). Retained
  as a separate failure; export equality is the only native result claimed.
- GUI save/reopen is untested (`gui_saveas_tested=false`).

## Visual inspection (producer, not approval)

At 48 logical px in the bright city and dark ruins captures, the auburn head, ivory coat, pale apron, dark-red
bag on the near left hip and brown boot read, and the silhouette faces screen left. The low braided coil reads as
a banded auburn mass behind/below the ear at the nape; at 1x the plait detail is subtle and a human reviewer
should judge whether it reads as a braided coil rather than a segmented bun. Strict profile occludes the far arm
and most of the far-right herb; only the sprig tips protrude past the near front edge. The charcoal placket is
about 2 logical px wide and is partially crossed by the strap; the bag partly covers the apron. These are honest
limitations, not approval.

## Evidence paths and raw sha256

Tools:

- `tools/rpg-2-star-ocean-the-second_heya_west-static-author_unapproved-v01_20261024-131500-h150w001.py`
  `75467c614e38cfedf21c9f27f644ce2df88a518234398c40cff0752a14f8c070`
- `tools/rpg-2-star-ocean-the-second_heya_west-static-source-check_v01_20261024-131500-h150w001.py`
  `61f7fcc4c0af9640f284b0f3c089089bae83fd382601ee71110b7f2e69526a48`
- `tools/rpg-2-star-ocean-the-second_heya_west-static-native-pixelorama-check_v01_20261024-131500-h150w001.py`
  `5025947c23d7790f1f27e659adbccb010c40fd8c1db86a76d2ff93f0a348dc77`
- `tools/rpg-2-star-ocean-the-second_heya_west-static-source-fit_v01_20261024-131500-h150w001.py`
  `4f322932784be9861d89c7e1f21ba84d9035d02700a19f687a2ba32aa2f9fc07`

Evidence:

- independent proof
  `outputs/heya-w150/independent-3/rpg-2-star-ocean-the-second_heya_independent-source-proof_v01_20261024-131500-h150w001.json`
  `0683046a682300b533a20fb29ab0a96d559799dd6c537466bc654ed99924d74f`
- corrupt-hash control
  `outputs/heya-w150/independent-3/rpg-2-star-ocean-the-second_heya_corrupt-hash-control_test-only-v01_20261024-131500-h150w001.json`
- native report
  `outputs/heya-w150/native-1/20261024-131345-b5bec9a0/rpg-2-star-ocean-the-second_heya_west_native-pixelorama-export-report_test-only-v01_20261024-131500-h150w001.json`
  `dfbcc2f740cfbb713048141a8efa3c3c24545003a760ee44793ceb518ca359ed`
- source-fit proof
  `outputs/heya-w150/rpg-2-star-ocean-the-second_heya_west_source-fit-proof_test-only-v01_20261024-131500-h150w001-fit.json`
  `b8dbd30f9fbf056927ead516a7acc342956a0c16f25c5d82ba17ae11ecb465a2`
- fit manifest and four captures under `outputs/heya-w150/fit/`; checked-runner log `outputs/heya-w150/fit.runner.log`
- staging paths/raw hashes
  `outputs/heya-w150/author/rpg-2-star-ocean-the-second_heya_west-staging-output-paths-rawhashes_unapproved-v01_20261024-131500-d7917a5b.json`
- author logs `outputs/heya-w150/author/{preview1,preview2,preview3,build,install,check}.log`

## State separation and next action

- Produced: yes, west native source package exists and passes its production gates.
- Integrated: no; the coordinator must independently regenerate/check and commit the explicit paths.
- Inspected: producer visual inspection only; Codex/coordinator review and creator art approval remain open.
- Native diagnostics: failed/retained (`custom_samplers`), GUI unverified.
- Ledger/Bible/registry/defaults/scoring: unchanged by this producer. Meter movement is the coordinator's job
  after verified integration; no points are claimed here.

Bounded next action for the coordinator: independently rerun the author `check`, the west source check and the
native export check against `5ca65817` plus these untracked paths, inspect the 640x360 captures, then commit the
explicit west files and record the ledger/QA evidence. Creator art review stays separate.
