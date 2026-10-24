# Yanke south static source QA — `content.char.yanke.static-south` (UNAPPROVED v01)

Recorded: 2026-10-24T08:44:28Z author stamp. Owner: claude. Status: **produced source package, unapproved, not adopted**.
Task map points: 3 (frozen). No score/ledger/index transition is made by this producer note.

## Verdict

Yanke now has a native 80×112 south idle static package with editable Pixelorama PXO/ORA sources, a declared
palette, hidden guides, an explicit pivot/body rows, and a 48-logical-pixel gameplay display height. The package
passes the author's deterministic rebuild gates (`YANKE_SOUTH_V01_ALL_OK`) and an independent source checker
(`YANKE_S93_INDEPENDENT 31 / 31`). A checked Godot source-fit overlay produced four bilingual test-only captures
with `CHECKED_RUN PASS`. This is source production only: no runtime/default adoption, no other direction or
animation, no GUI roundtrip, no Pixelorama export equality test and no creator art approval.

## Base and identity

- Tested repository base: `a376e8fc5ec26ab6ecc9475c0c87b34c1c3b030f` (working tree already contained unrelated
  staged/untracked producer work; it was preserved).
- Bible: character-07, 岩柯 / Yanke, 37-year-old friendly heavy-tool craftsperson; broad leather shoulder straps,
  dark-brown work trousers, notched heavy tool head, sturdy build, cheerful direct personality; identity/hair
  anchor 短卷发与浓胡须.
- Concept source: `outputs/rpg-2-star-ocean-the-second_yanke_character-sheet_v01_20261013-153818-244380f3.png`,
  raw SHA256 `65ded437ee36afd47f2bbd17cefc72a2ec0afe5914d54bcb6f46f17855b8b23f`, approval **UNAPPROVED/concept**.
  Used as an identity reference only; hues were chosen by eye, no concept pixels were sampled or resampled.
- Authored anchors: short curly dark-brown hair and thick beard; broad face with a cheerful open smile; cream
  rolled-sleeve work shirt; olive-green work apron with pocket and worn hem; broad leather shoulder straps and
  brass buckles; broad leather belt, brass buckle and red work rag at the character's right hip (screen left);
  dark-brown baggy trousers with olive knee patches; heavy brown leather boots; notched steel tool head slung
  over the right shoulder with the far handle end emerging over the left shoulder. Sturdy 60-texel silhouette.

## Native contract and metrics

| Property | Value |
| --- | --- |
| Canvas | 80×112 source px |
| Pivot | (40, 104) |
| Opaque body rows | 8..103 |
| Display scale | 0.5 |
| Gameplay display height | 48 logical px |
| Declared palette | 38 entries (≤40 PXO grid) |
| Used colours | 38 (24..48 gate) |
| Genuine visible role layers | 12 (≥8 gate) |
| Isolated texels | 22 (≤24 gate) |
| Binary alpha / borders | yes / no opaque border |
| Pivot inside feet span | yes |
| Layers | hammer, boots, trousers, shirt, apron, harness, grip, belt, arms, face, hair, beard, guides |
| Guides | hidden in PXO/ORA; no overlap with opaque art |

The old 32×48 native-animation placeholder was not read, modified, replaced or counted. `not_placeholder` is true
(no `*yanke*` file exists under `game/assets/characters/native-animation`). No other character, direction,
animation, default, registry, Bible, ledger or Git index entry was written.

## Deliverables (raw SHA256, no normalization)

All package files under `game/assets/characters/yanke-native-v01/south/`:

| Purpose | File | Raw SHA256 |
| --- | --- | --- |
| Native static PNG | `rpg-2-star-ocean-the-second_yanke_south-static_unapproved-v01_20261024-084428-73949161.png` | `4f6bcf937390e300e2829ac052bcb1047fdb6387de41561490c757246a32fef0` |
| Editable Pixelorama PXO | `rpg-2-star-ocean-the-second_yanke_south-edit_unapproved-v01_20261024-084428-5b76b5f2.pxo` | `173779784354c7d2decbc87a0c13edfc2928d70aeabc91772e63d950d0b20992` |
| Editable ORA | `rpg-2-star-ocean-the-second_yanke_south-edit_unapproved-v01_20261024-084428-e87e7c42.ora` | `d536eae42395ce5765f6b1f4eb201203ef0c77d44a4285568adf3ed6d2e67267` |
| Declared palette | `rpg-2-star-ocean-the-second_yanke_south-palette_unapproved-v01_20261024-084428-76f9bb9e.json` | `018567be5e0f4c73b71abdfd719088a99b29e0f4b696f6425137dbf357048d9b` |
| Manifest | `rpg-2-star-ocean-the-second_yanke_south-manifest_unapproved-v01_20261024-084428-4305a59b.json` | `e57f5c93131daffff56bc75a47d9a2c1357f4c337797ea0d07c0c73918692e7e` |
| Godot ignore marker | `.gdignore` (0 bytes, scoped to this package) | `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855` |

Author and checker:

| Purpose | File | Raw SHA256 |
| --- | --- | --- |
| Author / deterministic build | `tools/rpg-2-star-ocean-the-second_yanke_south-static-author_unapproved-v01_20261024-084428-b93c1a4e.py` | `cdc21721e7423a4df6696273be4271f0a564edfe7d91cd2b2beb13955459fd1c` |
| Independent source checker | `tools/rpg-2-star-ocean-the-second_yanke_static-source-check_v01_20261024-084428-b93c1a4e.py` | `d65e64dfd37b0a67acab867d3e60f9e260fdb21810c04fdd0f423b2c162ad5bf` |

QA evidence under `outputs/yanke-s93/`:

| Purpose | File | Raw SHA256 |
| --- | --- | --- |
| Author preview ×6 (non-source) | `author/rpg-2-star-ocean-the-second_yanke_south-preview-x6_unapproved-v01_20261024-084428-4f6bcf93.png` | `6f7c4ab7f22d6a5be5df3b9d809579865d52bd55704c39e1fcc0edfa6cfefddc` |
| Output path/hash listing | `author/rpg-2-star-ocean-the-second_yanke_south-output-paths-rawhashes_unapproved-v01_20261024-084428-3ca399c9.json` | `4602b70173050ebfc3e0dd4707b7f6ae56625d7e04af1dd33429e9b4fcffdbcc` |
| Independent proof | `independent-source-proof/rpg-2-star-ocean-the-second_yanke_independent-source-proof_v01_20261024-084428-b93c1a4e.json` | `972bd7c08b2e78c02d57a2c436f3c255f582df3d305d2f3bb913ee4044e00bdb` |
| Corrupt-hash negative control | `independent-source-proof/rpg-2-star-ocean-the-second_yanke_corrupt-hash-control_test-only-v01_20261024-084428-b93c1a4e.json` | `c5dc4afc6fd87d4f97b3b4397d03f1c156940ebca8e493119d371ea3606bf2f0` |

Reused tool pins were verified at build time (all true): Lin Que four-direction author
`0ddbea4591312c767b2ac46da6be29302b908cf311adb92eaf5ed26c300eff82`, Jiang south author
`35005f3c904802251c773838d61068d4aea847c993f6e354676e88a599db69b4`, male v8pair serializer
`fcd9d6e88e7401097e9c8afe8061df6dcdd9e2132892680522d7d722ac2abb79`, Muxiu south structural template
`f329ac7aa595f003ba741ed8de6cf5aade1d912acfa65a1720ce731eb24737f1`.

## Commands and machine results

The project-local interpreter with NumPy/Pillow is the sibling tooling venv. The author/checker were run with
`-X utf8 -I`.

1. Deterministic build (write only if bytes match a fresh rebuild):
   `../tooling/venv/bin/python -X utf8 -I tools/rpg-2-star-ocean-the-second_yanke_south-static-author_unapproved-v01_20261024-084428-b93c1a4e.py build`
   → exit 0, `YANKE_SOUTH_V01_ALL_OK`, deterministic rebuild true, disk matches rebuild true, hard failures empty.
2. Deterministic check (rebuild twice in memory, compare disk):
   `../tooling/venv/bin/python -X utf8 -I tools/rpg-2-star-ocean-the-second_yanke_south-static-author_unapproved-v01_20261024-084428-b93c1a4e.py check`
   → exit 0, `YANKE_SOUTH_V01_ALL_OK`, 38 colours, 12 role layers, 22 isolated texels, body rows [8,103].
3. Independent source check (does not import the author; reads only the game tree, writes only `--out`):
   `../tooling/venv/bin/python -X utf8 -I tools/rpg-2-star-ocean-the-second_yanke_static-source-check_v01_20261024-084428-b93c1a4e.py --root . --out outputs/yanke-s93/independent-source-proof`
   → exit 0, `YANKE_S93_INDEPENDENT 31 / 31`, failures empty.
   Checks include manifest identity/spec/hashes, 80×112 canvas, body rows 8..103, 48 logical px, pivot inside feet,
   binary alpha/borders, palette containment, all six identity colour families, 240 steel tool texels, ORA
   composition/merged bytes/mimetype, 12 genuine ORA roles, 8 anchor roles ≥12 contributions, hidden guides with
   a visible-guides negative control, PXO composition/roles/labels/size, corrupt-hash and tampered-PNG controls,
   not-placeholder, south-only package, and silhouettes differing by ≥400 alpha texels from Jiang, Lin, Milo and
   Muxiu (1659/1783/1335/1072).
4. Checked Godot source-fit overlay (test-only, no adoption), from the repository root:
   `env HOME="$PWD/outputs/yanke-s93/fit4/home" XDG_CONFIG_HOME="$PWD/outputs/yanke-s93/fit4/config" XDG_DATA_HOME="$PWD/outputs/yanke-s93/fit4/data" XDG_CACHE_HOME="$PWD/outputs/yanke-s93/fit4/cache" TMPDIR="$PWD/outputs/yanke-s93/fit4/tmp" xvfb-run -a -s "-screen 0 640x360x24" ../tooling/venv/bin/python -X utf8 -I tools/rpg-2-star-ocean-the-second_godot_checked-runner_v01_20261018-203400-f74ac6d1.py --timeout 110 --expect "JIANG37_SOURCE_FIT_PASS captures=4" --log "$PWD/outputs/yanke-s93/fit4/fit.runner.log" -- ../tooling/bin/godot --audio-driver Dummy --rendering-driver opengl3 --resolution 640x360 --path game --script "$PWD/tools/rpg-2-star-ocean-the-second_native-static_scene-fit-capture_test-only-v01_20261021-235007-514b9771.gd" -- "$PWD/game/assets/characters/yanke-native-v01/south/rpg-2-star-ocean-the-second_yanke_south-static_unapproved-v01_20261024-084428-73949161.png" "$PWD/outputs/yanke-s93/fit4/fit" yanke-s93-20261024-084428-b93c1a4e yanke`
   → `JIANG37_SOURCE_FIT_PASS captures=4`, `CHECKED_RUN PASS`, exit 0, elapsed 4.405 s. Only the known
   V-Sync warning; no `SCRIPT_ERROR`, parse error or other diagnostic. Viewport is the harness's own 640×360 test
   viewport, scale 0.5, candidate position [400,280]; `runtimeAdopted:false`, `artApproved:false`.
   Captures and raw hashes (source SHA for all four `4f6bcf93...`):
   - city EN `a473ff523dc55a477bba18b654c8744f5f7c9063c8d1cc873e263433dbf13f73`
   - city ZH `47e50c027fb35bdd145d039a4dc430eeb51a927ea04eba24f2b63e55e4793134`
   - ruins EN `f3a8619e2357f410b33f769520be5d21631236a75791134cf5a275ab457ea429`
   - ruins ZH `ba1ae070d8debe71f8cbb3af2af4e4e6a00db858ed55cf503a6fdcba2f7b6252`
   - fit manifest `ddb70a5b0819fd284132f083e88b2aa307ef128f444a620246861b43887664c6`

## Failed checks and diagnostics (retained, not relabelled)

- Draft author preview v01: hard failure `isolated_texels_le_24` at 31 isolated texels. The draft preview is retained
  at `outputs/yanke-s93/author/...ecc82471.png`; it is not the shipped package.
- Author revision after fixing the shirt/apron order and hammer geometry: still 33 isolated texels, then 17/21/22
  after notch and cluster fixes. Only the build at 22 isolated texels was installed. Intermediate previews
  remain in `outputs/yanke-s93/author/` as retained iteration evidence, not deliverables.
- Fit attempt 1/2: the command used `$ROOT/tooling/venv/bin/python` (repository root) instead of the sibling
  `../tooling` venv, so `xvfb-run` reported `.../repo/tooling/venv/bin/python: not found` and exited 127. This was a
  path error, not a permission denial; it was corrected by using the actual sibling tooling path.
- Fit attempt 3: `--script res://tools/...native-static_scene-fit-capture...gd` resolved under the `game/`
  project and Godot reported `Attempt to open script ... File not found`; the checked runner returned FAIL
  `diagnostic`, exit -9. Log retained at `outputs/yanke-s93/fit3/fit.runner.log`. Corrected by passing the absolute
  filesystem path to the script as the final command; the fit then passed. No gate was weakened.
- No technical permission denial occurred for the executed author, checker, or fit commands. No blanket Bash,
  permission bypass, provider launch, commit, stage, push or ledger write was used.

## Meter snapshot (producer, no transition)

Coordinator-stated canonical starting values for this batch: production **62.0%**, content **691/1881**,
inspection **21.6%**, creator approval **7.8%**. This producer did not edit the ledger, registry, Bible, Git index
or defaults and does not claim a score change; the after values remain pending coordinator validation/integration.
Production, inspection and creator approval stay separate states.

## Limitations and remaining work

- South idle static only. No west/north/east, walk/run/stop/combat animation, runtime wiring, scene selector,
  default adoption, normal gameplay capture, GUI save/reopen or Pixelorama export-equality test.
- The concept portrait is unapproved and the new sprite is unapproved. Human identity/direction review and creator
  art acceptance remain pending; automated checks cannot supply them.
- Fit captures are test-only source overlays, not normal-host movement/occlusion/lighting evidence.
- The palette/source contract is shared with the existing native pipeline; no new framework was scaffolded.
- Coordinator review should verify the staged bytes and decide integration. No commit/stage/push was performed.
