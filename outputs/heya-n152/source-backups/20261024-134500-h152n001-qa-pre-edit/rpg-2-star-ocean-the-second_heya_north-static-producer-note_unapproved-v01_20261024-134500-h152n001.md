# Heya north static — producer note (UNAPPROVED source)

Task `content.char.heya.static-north`, batch `h152n001`, producer DeepSeek. Base revision
`122fbe1102f026fc09adffc7058386550779681c`. Status: source produced and independently checked;
`UNAPPROVED`, `approval=false`, `artApproved=false`, `runtimeAdopted=false`. No ledger, registry, Bible, index or
Git commit was touched. Coordinator verification remains separate.

## Deliverable

True rear-view native north static at 80x112 source, pivot `(40,104)`, body rows 8..103, display scale 0.5 =
48 logical px. Same exact 35-entry palette, 14-layer vocabulary (13 visible roles + hidden guides), outline rule
and PXO/ORA/PNG serializers as committed Heya south/west. 31 used colours, 13 genuine role layers, 18 isolated
texels. The rear view shows both ears, the back of the auburn head, a centred low braided coil at the nape, the
grey-white scarf with its tail down the screen-left back, the ivory coat back with centre seam/yoke and lower
vent exposing charcoal, the apron tied in a back bow, the dark-red bag on the character's LEFT (screen left),
brass hardware, herb sprig, both gloved arms and brown boots. No eyes, nose or mouth are invented on the back of
the head; the restrained patient smile remains carried by the south/west views. The old 32x48 placeholder is
untouched.

Installed package (raw sha256):

- `game/assets/characters/heya-native-v01/north/..._heya_north-static_..._56efefc2.png`
  `d0019c77032ec7dcb403e3d54cc80a6b9b60a875881cefa1887bb145072656c4`
- `..._heya_north-edit_..._ced44bda.pxo` `f612bba8815533e8c0411270ed81c381e44d6e22d4266d03ae9b2fb84de44942`
- `..._heya_north-edit_..._7c039253.ora` `999f3929036569190fadec06c4602156a39ef1f3ce2d81a67794f5de1b5ee6ce`
- `..._heya_north-palette_..._023052d9.json` `e1a1a9ac775ccb452498f02db97230b3135727da7d999bf132f2877837483a52`
- `..._heya_north-manifest_..._ee613b85.json` `6bb045c18102ecd0b8e0ecbcdfdc22345f4442010f4dc2186316c539fb4f0089`
- `.gdignore` empty, `.gitattributes` `* -text -eol`.

Style/source contract: `outputs/heya-n152/rpg-2-star-ocean-the-second_heya_north-style-source-contract_unapproved-v01_20261024-134500-h152n001.md`
`2512e8b0bd07979e3dfbb73eebea6ee04fc6b26384cf567885cbdd456e3c8679`.

Tools (all new, written once):

- author `6098959f983783413b7bbbc64a33537cbc27739c263f0c29d3d5ac8fe0746a84`
- independent checker `632bbc16063d1f6e94f2ac255875c1ac4aec00ad69d3f3a08696179b14d49e4c`
- native Pixelorama checker `6c37b0e13a19dd672dcc0424c9ca86599e70cecaf47b495db5cf9f41350704b9`
- source-fit harness `4308e845e24938dd51239bdf2d30004849c55ebda5dee97cb1ac2fe4e6a10d78`.

Producer receipt: `outputs/heya-n152/rpg-2-star-ocean-the-second_heya_north-static-producer-receipt_unapproved-v01_20261024-134500-h152n001.json`
`51073d817ee2301e7b8fc427b5894b68da2dd6e49d269551a9007fec5d5522e1`.

## Checks performed

1. Author `check` (post-install): `HEYA_NORTH_V01_ALL_OK`, rc0; deterministic two-build equality; all staging and
   installed hashes match; south and west packages and palettes unchanged; all pinned author dependencies match.
   Log `outputs/heya-n152/author-check.log`.
2. Independent checker (does not import the Heya author; reuses only the Jiang ORA parser): 49/49 checks pass,
   rc0. Report `outputs/heya-n152/independent-1/...independent-source-proof...json`
   `2dfe3038499a774b9ed4f3d1dcb73442084dc24a101dbae3df9dce6ced73ea0d`. Negative controls cover corrupt
   manifest hash, tampered PNG pixel, visible guides, eyes/mouth on the rear face (wrong direction), high bun,
   missing scarf, bag moved to the wrong hip, and hidden charcoal dress. ORA/PXO recomposition equals the PNG.
   Silhouette differs from south by 646 alpha texels and from west by 1407; no flip/recolour.
3. Native Pixelorama exact exports: 11/11 equality gates pass (PXO flat, PXO split per-layer + merged, ORA flat,
   inputs/package unchanged). Report `outputs/heya-n152/native-1/20261024-132655-1786665a/...json`
   `04ed8c3e29a4bde53786a9b166faf929b43c4c6a2edf7e3a03b053b3858e1552`. `diagnostic_clean=false` is retained:
   four custom-sampler/shader diagnostic lines per run. Exact export equality is not a diagnostic-clean claim, and
   GUI SaveAs/reopen is untested.
4. Bounded checked source-fit through the existing generic harness, 640x360, OpenGL3, Dummy audio: four captures
   (city bright / ruins dark, EN and ZH), source unchanged, `runtimeAdopted=false`, `artApproved=false`.
   Proof `..._north_source-fit-proof_test-only-v01_20261024-134500-h152n001-fit.json`
   `50dff0b347966c1a2ebc8f72813e6ed2c92c458dec60c3ececa0a7d1a4ecd774`; this is a test-only overlay, not
   ordinary actor integration. Capture hashes: city-en `05bb6dab...`, city-zh `774613f7...`, ruins-en
   `36f2d6a6...`, ruins-zh `2d3b4ce0...`.
5. M1 smoke through the checked runner, headless, Dummy audio: `M1_SMOKE_OK`, `CHECKED_RUN PASS`, exit0, 0.765 s,
   isolated `HOME`/`XDG`. Logs `outputs/heya-n152/m1-smoke-r2.log` and `.runner.log`.

## Preservation

Every new repo script/manifest/contract was written once from a separately iterated `/tmp` draft and then received
no Edit/Write. A `copy2` metadata-preserving snapshot was taken with SHA256 verification at
`outputs/heya-n152/source-backups/20261024-134500-h152n001/` (receipt
`.../preservation-receipt.json`); original and backup SHA256, mode, size and mtime match for all five files. This
is a protective baseline, not a retrospective cure. No existing file was replaced, so `wb_safe_replace.py` was not
needed and no backup-before-replacement event occurred. The pre-existing `outputs/heya-n152/coordinator/` files
were not touched.

## Actual failures / limitations

- First M1 attempt failed before project load: Godot could not open `user://logs/...`; the checked runner returned
  `CHECKED_RUN FAIL diagnostic exit=-9`, missing `M1_SMOKE_OK`. Both logs are retained (`m1-smoke.log`,
  `m1-smoke.runner.log`). It passed only after an isolated `HOME`/`XDG` was supplied; the check was not weakened.
- Native application diagnostics are not clean (four shader sampler lines per run); exact export equality passes.
- GUI SaveAs/reopen untested; no native-diagnostic-clean or GUI-reliability claim.
- No runtime/default adoption, no normal actor integration, no motion review, no creator art approval.
- Default `python3` in this runtime lacks numpy/Pillow; all commands use
  `/home/kel/projects/worlds-between/tooling/venv/bin/python3`.
- No denial occurred; no blanket Bash, permission bypass, deletion, secret/account/settings change, ledger/Bible/
  registry/index edit, commit or push was performed.

## Exact rerun commands (fresh output directories)

```bash
cd /home/kel/projects/worlds-between/repo
/home/kel/projects/worlds-between/tooling/venv/bin/python3 -I tools/rpg-2-star-ocean-the-second_heya_north-static-author_unapproved-v01_20261024-134500-h152n001.py check
/home/kel/projects/worlds-between/tooling/venv/bin/python3 -I tools/rpg-2-star-ocean-the-second_heya_north-static-source-check_v01_20261024-134500-h152n001.py --root . --out outputs/heya-n152/independent-2
/home/kel/projects/worlds-between/tooling/venv/bin/python3 -I tools/rpg-2-star-ocean-the-second_heya_north-static-native-pixelorama-check_v01_20261024-134500-h152n001.py --out outputs/heya-n152/native-2
/home/kel/projects/worlds-between/tooling/venv/bin/python3 -I tools/rpg-2-star-ocean-the-second_heya_north-static-source-fit_v01_20261024-134500-h152n001.py
env HOME=$PWD/outputs/heya-n152/godot-home/home XDG_CONFIG_HOME=$PWD/outputs/heya-n152/godot-home/config XDG_DATA_HOME=$PWD/outputs/heya-n152/godot-home/data XDG_CACHE_HOME=$PWD/outputs/heya-n152/godot-home/cache XDG_RUNTIME_DIR=$PWD/outputs/heya-n152/godot-home/run TMPDIR=$PWD/outputs/heya-n152/tmp \
  /home/kel/projects/worlds-between/tooling/venv/bin/python3 -I tools/rpg-2-star-ocean-the-second_godot_checked-runner_v01_20261018-203400-f74ac6d1.py --timeout 60 --expect M1_SMOKE_OK --log outputs/heya-n152/m1-smoke-r3.runner.log -- /home/kel/projects/worlds-between/tooling/godot-4.7.2/Godot_v4.7.2-stable_linux.x86_64 --headless --audio-driver Dummy --path game --script res://tests/m1_smoke.gd
```

For a future revision: preserve the current north files with `copy2` into a new unique
`outputs/heya-n152/source-backups/...` directory, verify SHA256 and metadata, then rebuild into a new staging
directory and install differing destinations only through `python3 tools/wb_safe_replace.py SOURCE DEST`.
