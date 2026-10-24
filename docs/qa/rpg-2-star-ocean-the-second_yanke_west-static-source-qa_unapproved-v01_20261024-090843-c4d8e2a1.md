# Yanke west static source QA — `content.char.yanke.static-west` (UNAPPROVED v01)

Recorded: 2026-10-24T09:08:43Z author stamp; QA closed 2026-10-24T09:15Z. Producer: **deepseek-flash** (adapter-routed batch99; this note records the actual producer and does not claim a Claude run). Status: **produced source package, technically checked, unapproved, not adopted**. The canonical ledger task remains `todo`; this producer did not mark it done.

## Verdict

Yanke now has a native 80×112 west idle static with editable PXO/ORA sources, a declared palette, hidden guides, explicit pivot/body rows, and a 48-logical-pixel gameplay display height. The package passes the author's deterministic rebuild/check gates (`YANKE_WEST_V01_ALL_OK`), an independent source checker (`YANKE_W99_WEST_INDEPENDENT 37 / 37`), Pixelorama 1.2.3 PXO/ORA export equality (11/11 gates), and four checked bilingual source-fit captures (`CHECKED_RUN PASS`). This is source production only: **no runtime/default adoption, no other direction or animation, no GUI save/reopen, no normal gameplay motion review and no creator art approval**.

## Base, scope and task-local starting meters

- Tested base revision: `234cfabeacd48a9ebc80b2608af448feb535af69` (Yanke south committed in this revision; no later commit was made).
- Task-local canonical starting meters supplied by the coordinator: production **62.1%**, content **694/1881**; inspection **21.6%**; creator approval **7.8%**. This producer did not edit the ledger, Bible, operating registry, Git index or defaults and claims no score transition.
- Write scope used: `game/assets/characters/yanke-native-v01/west/`, `outputs/yanke-w99/`, `tools/*yanke*west*`, `docs/qa/*yanke*west*`. No south/north/east package, shared ledger/Bible/registry/index, other character, default or unrelated dirty file was edited. Pre-existing Muxiu staged/untracked work and the dirty operating registry were left as found.

## Identity and west view

Bible character-07 (identity reference only; concept sheet UNAPPROVED, no pixels sampled): 37-year-old friendly heavy-tool craftsperson; short curly dark-brown hair, thick beard, broad warm face and cheerful direct smile; cream rolled-sleeve work shirt; olive-green work apron with stitched pocket and worn hem; broad leather shoulder straps and brass buckles; dark-brown baggy work trousers with olive knee patches; heavy brown leather boots; red work rag at the character's right hip; notched heavy steel tool head on a wooden handle slung over the right shoulder.

West = nose toward screen **left**, so the character's **LEFT** side faces the camera. The sprite was authored in forward coordinates with the existing Lin Que `P` pen (`s = -1`), not rotated, squashed, recoloured or mirrored from south. The far (right) shoulder/hip are behind the torso: the steel head and notch read above/behind the upper back at screen right, the far handle end emerges over the near left shoulder at screen front, and the red rag peeks behind the far hip. One brown eye, one ear, a nose protruding past the forehead and a smile with teeth establish the profile.

## Contract and measured metrics

| Property | Value |
| --- | --- |
| Canvas | 80×112 source px (density 2) |
| Opaque body rows | 8..103 = 96 source px |
| Display scale / logical height | 0.5 / **48 logical px** |
| Pivot | (40,104), inside row-103 feet span |
| Declared palette | 38 entries (same colours as south) |
| Used colours | 38 (24..48 gate) |
| Genuine visible role layers | 12 (≥8 gate) |
| Isolated texels | 24 (≤24 gate) |
| Opaque chest depth (rows 38..46) | 25 source px (`profile_depth_ge_20`) |
| Steel tool texels (k1/k2/k3) | 131 (≥120 gate) |
| West vs south alpha silhouette | 2071 differing texels (≥400 gate) |
| West vs mirrored south alpha silhouette | 1837 differing texels (≥400 gate) |
| Profile eye components | 1 (iris-only e2); south control | 2 |
| Nose front x / forehead front x | 28 / 32 (nose leads) |
| Alpha / border | binary / no opaque border |
| Layers | hammer, boots, trousers, shirt, apron, harness, grip, belt, arms, face, hair, beard, guides (hidden) |

The south hard gate `stocky_shoulders_ge_34` measures frontal shoulder spread and is not meaningful in strict profile; it is replaced by the declared `stocky_profile_depth_ge_20` with a 20 px threshold. All other south hard gates and thresholds are retained unchanged. The independent checker reports both the profile depth and the south/mirror differences explicitly.

## Deliverables (raw SHA256, no normalization)

Package under `game/assets/characters/yanke-native-v01/west/`:

| Purpose | File | Raw SHA256 |
| --- | --- | --- |
| Native static PNG | `rpg-2-star-ocean-the-second_yanke_west-static_unapproved-v01_20261024-090843-c7b9c800.png` | `7fce1fe9dec54ebcc60143adf75c4fd2cc3c50f37668d110df5ea4ce5dceabd3` |
| Editable Pixelorama PXO | `rpg-2-star-ocean-the-second_yanke_west-edit_unapproved-v01_20261024-090843-0d5bfb6b.pxo` | `2525494dc7a12198e40e7e6b5a5bdd99ff3bad418afb0ae149351e64c58a5d3e` |
| Editable ORA | `rpg-2-star-ocean-the-second_yanke_west-edit_unapproved-v01_20261024-090843-bbe6c9e8.ora` | `74f1d32371d6b7a18c97216c286ba43a5cadc3611f137f252aa14e44fa4e5cca` |
| Declared palette | `rpg-2-star-ocean-the-second_yanke_west-palette_unapproved-v01_20261024-090843-edd8f51a.json` | `2c5eeea118470d8a532a0359849c5f5964ab56ac49a9c448507c08ac8794e416` |
| Manifest | `rpg-2-star-ocean-the-second_yanke_west-manifest_unapproved-v01_20261024-090843-e4019ea8.json` | `2741ec94a1779077f6771b2bafcbe59f07bc9a8e449b62659683118aa1191df6` |
| Godot ignore marker | `.gdignore` (0 bytes) | `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855` |

Author, checker and contract:

| Purpose | File | Raw SHA256 |
| --- | --- | --- |
| Author / deterministic build (r2) | `tools/rpg-2-star-ocean-the-second_yanke_west-static-author_unapproved-v01_20261024-090843-w99a1b2c.py` | `9937ec2107fb53db290908cdae9bf8de8c1291fd868ad90878ee083daf186175` |
| Independent source checker | `tools/rpg-2-star-ocean-the-second_yanke_west-static-source-check_v01_20261024-090843-w99a1b2c.py` | `e4895a44543448326d02352ae0f05355e4fd6547e77a47609f4c2b6e99ed7cc4` |
| Native Pixelorama export checker | `tools/rpg-2-star-ocean-the-second_yanke_west-static-native-pixelorama-check_v01_20261024-090843-w99a1b2c.py` | `a01184985b2d82d8fcea4dfc00d1b60ceab5a5b2faeb1f2bde68cf32aa139e47` |
| Bounded west contract (written before authoring) | `outputs/yanke-w99/rpg-2-star-ocean-the-second_yanke_west-style-source-contract_unapproved-v01_20261024-090843-w99a1b2c.md` | `e9671861f99fdcbb43b64eb442302228f1d0fe50380b2d079e83a43bb445f815` |

Evidence under `outputs/yanke-w99/`:

| Purpose | File | Raw SHA256 |
| --- | --- | --- |
| r2 deterministic build log | `author/build-r2.log` | `4e92fef7d2ca757d6ecf83f89a2a62bbbae7f1e4e3ac89e0117355fcdd459d24` |
| r2 deterministic check log | `author/check-r2.log` | `ef06d863e88e6a57bcd7f8d17a7441788f9564d1d91868a9d4090f290099a8b8` |
| Final r2 preview ×6 (non-source) | `author/rpg-2-star-ocean-the-second_yanke_west-preview-x6_unapproved-v01_20261024-090843-7fce1fe9.png` | `f9bb6ce817e9bf47b93da3c99cad1ae2fdd20de69ba1ae68e42b52b5a468d185` |
| Final staged output/hash listing | `author/rpg-2-star-ocean-the-second_yanke_west-output-paths-rawhashes_unapproved-v01_20261024-090843-d5bf0607.json` | `7bd69c52a85755430cdfdf83bb7b60390e127109a9c5b3fc72f96874b2e8fffb` |
| Independent 37/37 log | `independent-check-r2.log` | `e5616f3d692e12384479002ae1add3576f7ad7c0a8ba84b32297f8f9997508b6` |
| Independent proof | `independent-r2/rpg-2-star-ocean-the-second_yanke_west_independent-source-proof_v01_20261024-090843-w99a1b2c.json` | `49ccabc7b4d849b973d74450bbbae83b31bba20d5f07636546a412212a13e991` |
| Corrupt-hash control JSON | `independent-r2/rpg-2-star-ocean-the-second_yanke_corrupt-hash-control_test-only-v01_20261024-090843-w99a1b2c.json` | `89e8ff8780f6f89f4b4e183b7d408aeaebe3bfb8dd9aec8dcbfd01fc1e963769` |
| Native export report | `native/20261024-091405-2b39d1e6/rpg-2-star-ocean-the-second_yanke_west_native-pixelorama-export-report_test-only-v01_20261024-090843-w99a1b2c.json` | `fcdd53b29883d7c01734ea34f59362765ed4d3b1799b0f144791ff7017138671` |
| Native check log | `native-check.log` | `bbeca1c9ad14946885ae39d673e57a9333e77ed3513188162d17375e651d8132` |
| Safe-replace receipts (5) | `safe-replace-r2.log` | `55f320c37b3941bfc975525512143be5468d0752e08f5f5a4f08bd9dc509eccb` |
| Wrong-direction control log | `controls/wrong-direction.log` | `1d4013fac66b6c109056931b2d67be6b7f1122ebfb727d9b2642aad79a38b869` |
| Corrupt-PNG control log | `controls/corrupt-png.log` | `c04423138448e4f468e08f6b05ea8b1692bbe847bcf03a15744363f7446a1a70` |
| Wrong-direction proof | `controls/out-wrong-direction/rpg-2-star-ocean-the-second_yanke_west_independent-source-proof_v01_20261024-090843-w99a1b2c.json` | `9ccfe1d87733e8de7928a0494f656d67dc29d1648c15ecd86fcfb7ee048c2bc8` |
| Corrupt-PNG proof | `controls/out-corrupt-png/rpg-2-star-ocean-the-second_yanke_west_independent-source-proof_v01_20261024-090843-w99a1b2c.json` | `5b7c61b7fa436dc4fd4200d8c4c71f21a3123f15eed3d9764ef13b309bdec7ce` |

The final installed package bytes match the r2 stage listing and the manifest hashes (verified). The south package still matches its own manifest/PNG pin; `git diff 234cfabe -- game/assets/characters/yanke-native-v01/south` is empty.

## Commands and machine results

Interpreter: sibling `../tooling/venv/bin/python`, run with `-X utf8 -I`. Raw SHA-256 only, no normalization.

1. Author deterministic build into fresh `outputs/yanke-w99/stage-r2/` (r1 stage retained):
   `../tooling/venv/bin/python -X utf8 -I tools/rpg-2-star-ocean-the-second_yanke_west-static-author_unapproved-v01_20261024-090843-w99a1b2c.py build`
   → exit **0**, `YANKE_WEST_V01_ALL_OK`, `hard_failures []`, deterministic rebuild true, all stage files match rebuild, all reused tool pins true, south unchanged true.
2. Author deterministic check on installed bytes:
   `... check`
   → exit **0**, `YANKE_WEST_V01_ALL_OK`, all five package files match the rebuild, 38 colours, 12 role layers, 24 isolated texels, body rows [8,103], profile depth 25.
3. Independent source check:
   `../tooling/venv/bin/python -X utf8 -I tools/rpg-2-star-ocean-the-second_yanke_west-static-source-check_v01_20261024-090843-w99a1b2c.py --root . --out outputs/yanke-w99/independent-r2`
   → exit **0**, `YANKE_W99_WEST_INDEPENDENT 37 / 37`, `FAILURES []`.
   It verifies manifest identity/spec/hashes, 80×112, rows 8..103, 48 logical px, pivot, binary alpha/borders, palette containment, six identity colour families, 131 steel texels, ORA composition/merged bytes/mimetype, 12 genuine ORA roles, 8 anchor roles ≥12 contributions, hidden guides + visible-guides negative control, PXO composition/roles/labels/size, corrupt-hash and tampered-PNG controls, wrong-direction control, not-placeholder, west-only package, silhouette differences from Yanke south/Jiang/Lin/Milo/Muxiu (2071/984/866/1218/1285), west vs south/mirror (2071/1837), profile depth 25, one iris component, south two-iris control, and nose-leading profile.
4. Malformed source controls (expected failure, retained):
   - Wrong-direction manifest package: `--package outputs/yanke-w99/controls/wrong-direction --out outputs/yanke-w99/controls/out-wrong-direction` → exit **1**, failures `['identity', 'control_wrong_direction_refused']`.
   - Tampered-PNG package: `--package outputs/yanke-w99/controls/corrupt-png --out outputs/yanke-w99/controls/out-corrupt-png` → exit **1**, failures `['filehashes', 'palette', 'ora_composition', 'ora_merged', 'pxo_composition', 'control_corrupt_hash_refused']`.
5. Native Pixelorama 1.2.3 export equality (isolated HOME/XDG, 120 s deadline):
   `../tooling/venv/bin/python -X utf8 -I tools/rpg-2-star-ocean-the-second_yanke_west-static-native-pixelorama-check_v01_20261024-090843-w99a1b2c.py --out outputs/yanke-w99/native`
   → exit **0**, `YANKE_W99_WEST_NATIVE_PIXELORAMA PASS`, 11/11 equality gates true: PXO flat exact static, PXO split 12 visible layers each exact plus merged exact, guides not exported, PXO/ORA/package inputs unchanged, ORA flat exact static. Both flat exports share raw SHA `aca006d2367055e365f953220ab2f9c762a0f30a6e15963b1e3811fc3ba12107`; package static remains `7fce1fe9…dceabd3`.
   **Application diagnostics are FAILED and retained separately**: each of PXO flat/PXO split/ORA flat emitted four `custom_samplers` shader errors; ORA flat also emitted three `Index p_index = 0 is out of bounds`, one `rp_node` null, one `Must be an ancestor of the control`, one RID-allocation leak, one `16 resources still in use at exit`, and a 166-instance ObjectDB leak warning. `diagnostic_clean:false`. Export equality is not a diagnostic-clean or GUI claim.
6. Checked Godot bilingual source-fit (test-only overlay, Dummy audio, 640×360):
   `xvfb-run -a -s "-screen 0 640x360x24" ../tooling/venv/bin/python -X utf8 -I tools/rpg-2-star-ocean-the-second_godot_checked-runner_v01_20261018-203400-f74ac6d1.py --timeout 110 --expect "JIANG37_SOURCE_FIT_PASS captures=4" --log outputs/yanke-w99/fit/fit.runner.log -- ../tooling/bin/godot --audio-driver Dummy --rendering-driver opengl3 --resolution 640x360 --path game --script .../native-static_scene-fit-capture_test-only-v01_20261021-235007-514b9771.gd -- .../west PNG outputs/yanke-w99/fit/fit yanke-w99-20261024-090843-w99a1b2c yanke`
   → exit **0**, `JIANG37_SOURCE_FIT_PASS captures=4`, `CHECKED_RUN PASS`, elapsed 4.74 s, missing `[]`; only the known V-Sync warning, no `SCRIPT_ERROR`/parse error. All four captures record `sourceSha256 7fce1fe9…dceabd3`, scale 0.5, position [400,280], `testOnly:true`, `runtimeAdopted:false`, `artApproved:false`.
   - city EN `fecba5c244abaf39b88a2af4b3421b61c0142c2cb211a3c5c5ab23b815b8094c`
   - city ZH `e33126ba4ff2b995b6ddee93b6a56068f6b78e2b9da990ab096d5d781de39194`
   - ruins EN `72b2a7199361c71f40e1cc29aaa5182f948166eb9b8f0d364636409358812811`
   - ruins ZH `33cdef184f6b0dc41f500f22da24303ebe49815195d93f3db1517e237715ef57`
   - fit manifest `0d34963de907d7332de6990fbc9b79f7939bf2fbe61edbbd3705b236b1147826`
   - runner log `0e2337bc6f0fa7c8a832d1a8d6c5ed7d98214c35c21f922f120b702d3ecefc3f`; outer log `e9e24560b554c02fae8c19361a9f3207f362b4544e66a7ae5bded62a0e50b83e`.
7. Installation: r1 was installed as new files; r2 differed and was installed only through the explicitly authorized helper for each package file:
   `python3 tools/wb_safe_replace.py outputs/yanke-w99/stage-r2/<file> game/assets/characters/yanke-native-v01/west/<file>`
   → five receipts, each `before_sha256` verified against the unique backup and `after_sha256` verified against the installed file. Backups live under `outputs/development-backups/<id>/original` with per-replacement `receipt.json`; the receipt log is `outputs/yanke-w99/safe-replace-r2.log` (`55f320c3…c509eccb`). `.gdignore` was identical and left untouched; no deletion was performed.

## Failed checks, revisions and diagnostics (retained, not relabelled)

- First draft preview: 28 isolated texels > unchanged limit 24. Preview `c20731b1` retained; not installed.
- r1: author gates passed and r1 was installed, but the independent checker found `steel_tool_mass` 96 < 120, and the eye-component check failed because it included the white teeth (`e1`) with the eye colours. The checker was corrected to count **iris-only `e2`** (correctness fix, not a threshold change), and the steel head was enlarged so the final package has 131 steel texels. r2 was installed over r1 through `wb_safe_replace.py`; the r1 bytes and verified backups are retained. The earlier independent proof (`independent/`, 34/37) is retained as the failed r1 record.
- Intermediate previews `c20731b1` (28 isolated), `f2fa611d` (transient r1 variant) and `54689a3b` (r1 with 24 isolated) remain in `outputs/yanke-w99/author/`; only `7fce1fe9` is the final r2 preview.
- Early output listing `221ab5b7` was written before the `.gdignore` entry was added; `760933a0` was the pre-r2 listing. Both are retained intermediates. The final authoritative listing is `d5bf0607`, whose five package hashes and `.gdignore` hash match the installed bytes.
- Native application diagnostics failed as detailed above. No control rerun was performed for the known Pixelorama/Godot sampler issue; the south QA addendum records the same inherited diagnostic family. No GUI SaveAs/reopen, diagnostic-clean or editor-reliability claim is made.
- No technical permission denial occurred. No blanket Bash, permission bypass, provider launch, account/secret change, commit, stage, push or shared-ledger write was used. The pre-existing dirty operating registry and unrelated Muxiu staged/untracked work were not touched.

## Limitations and remaining work

- West idle static only. No south/north/east changes, walk/run/stop/combat animation, runtime wiring, scene selector, default adoption, normal gameplay capture, motion review, GUI save/reopen or creator art approval.
- The concept sheet and this sprite remain UNAPPROVED. Automated checks cannot supply human identity/direction/art acceptance.
- Source-fit captures are test-only overlays, not normal-host movement/occlusion/lighting evidence.
- Provider routing is adapter-controlled; this receipt records the actual producer (`deepseek-flash`) and makes no Claude-depletion or account claim.
- The canonical task stays `todo` until the coordinator independently verifies and commits. No shared/index changes were made.

## Recommended integration paths (coordinator verifies exact staged bytes)

- `game/assets/characters/yanke-native-v01/west/` — PNG, PXO, ORA, palette, manifest, `.gdignore`
- `tools/rpg-2-star-ocean-the-second_yanke_west-static-author_unapproved-v01_20261024-090843-w99a1b2c.py`
- `tools/rpg-2-star-ocean-the-second_yanke_west-static-source-check_v01_20261024-090843-w99a1b2c.py`
- `tools/rpg-2-star-ocean-the-second_yanke_west-static-native-pixelorama-check_v01_20261024-090843-w99a1b2c.py`
- `docs/qa/rpg-2-star-ocean-the-second_yanke_west-static-source-qa_unapproved-v01_20261024-090843-c4d8e2a1.md`
- Evidence: `outputs/yanke-w99/` (contract, author/stage/preview, independent proofs, native report/logs, fit, controls, safe-replace receipts, `provider-receipt.json`)

Do not adopt runtime defaults, close the task or award creator approval from these automated checks.
