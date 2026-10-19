# Female battle static v15: material-value pass (QA note)

Status: **UNAPPROVED, NONRUNTIME, test-only static frame.** This is a supporting refinement. It has no animation and adds no new direction.

What stayed unchanged:
- runtime, `battle_arena.gd`, defaults, the Game Bible, the ledger, the Site and every counter (scenes 3/12, sprites 0/52, human plays 0/2, production 51.2%);
- this version earns no points.

Nothing is staged, committed or pushed. The root reviews the actual captures before any integration.

Auth: Claude Code, Opus 5.5, signed in to Max. No quota was hit.

Worktree: `work/max0840-battle` (dirty, preserved), branch `codex/chicago-native-materials-v06`, HEAD `9c38351`. v15 writes only:
- `outputs/battle-static-v15/`;
- two new `tools/` files;
- this note.

## Brief and named defects

Root review of the v14 actual 640×360 four-person archive capture:
1. coat and feet merge with the dark floor;
2. back and pack details are busy.

Preserve:
- v14's cloth volume and slimmer boot shape;
- the face, hair, scarf and slate-coat identity, and the adult head;
- the 0.65 proportion: 68×72 cell, pin (32, 68), crown row 7, sole row 67;
- blade reach, party draw order and the contact shadow.

## What changed (values only; alpha silhouette identical to v14)

The tool is a fork of the v14 author tool. Every row keeps v14's start column and length, so the alpha silhouette is v14's (IoU 1.0, 1590 texels, bbox [15, 1, 60, 67]). 184 composite texels change.

| layer | v15 change |
|---|---|
| coat-skirt | Back-tail body changes from mid slate `c` (L≈69, inside the outskirts floor's L≈76–86 band) to the new deep-mid slate `e`. v14's fold drawing, `C` flank, `o` ridge and split edge, and `l` hem are kept. The front panel is unchanged. |
| far-leg | One receding shadow plane (`C` + `T`). v14's lit `t` front stripe is removed. |
| boots (both legs) | Shaft and heel side in dark leather `L` (L≈31), mid `d` between. v14's lit `D` vamp/toe plane and its two-row lit `D` base in the contact shadow are kept. The near shaft's front is lit `D`. The warm-grey `u` toe texels become `D`. |
| near-leg | v14's warm-grey `u` thigh/shin planes become lit spruce `t`. Shin values run `C C T T t`. |
| pack | Broad planes: v14's lit flap `D`, one `d` body, and a shaded `l`/`L` back side. The pale buckle, strap line and flap marks are removed. |
| canister | **Layer removed (deviation, disclosed).** At 1× it read as a pale grey mark, which is part of the busy-back defect. |
| bedroll | Top plane changes from pale `G` (L≈180) to the scarf's mid teal `g`. The cylinder drawing is v14's. |
| hip-drape | Deep teal `Q` with one `q` texel (v14: a lit `g` edge). |

**Palette extension (disclosed):** one key, `e` = `#2e364d` (L≈54). It sits between v8's `C` (L 40) and `c` (L 68.6), in the same storm-slate hue, and is used only on the back tail.

The other 14 layers are byte-identical to v14:
- head and face (v14's brow included), hair, ponytail, loose lock, hair band;
- scarf, collar, collar-front, coat torso, shirt;
- arm, fist, blade, guard, insignia.

Silhouette edge keys are identical to v14, so there is no rim, halo, glow or neon. Floor and lighting are not touched.

## Files (all new, untracked)

Directory `outputs/battle-static-v15/`, shared prefix `rpg-2-star-ocean-the-second_female-battle-idle-right_`, stamp `20261018-210446`:

| file (suffix) | sha256 |
|---|---|
| `static-native0p65_unapproved-v15_…-abde2095.png` (68×72 RGBA, binary alpha, Pixelorama flat export of the .pxo) | `c6aca9b804d1fd83c284c1491cbeb347190d2528d8f05c460e1e055800e1f4e2` |
| `editable-layers_unapproved-v15_…-e9ee7d3b.pxo` (pxo_version 7, 20 layers + hidden locked guides) | `72b03201d33dfa7ea9f815122908f8f8dacf03b939c2838192bb8540e7b7f947` |
| `editable-layers_unapproved-v15_…-58b39cc2.ora` | `8b83cb533efb4a1fae143723e1948df47b31011dfd79a82dc685b77161959554` |
| `manifest_unapproved-v15_…-9ce58767.json` | `f1f44ede7e32832d5108f77fec237a051d1e5bb64a78a48236fc4302024a441a` |
| `party-capture-archive-640-zh_…-a586f209.png` | `e4357f367dd76f97cf2c106f5c4bbe29429dfa914e71500a88d73e1f33cd4d79` |
| `party-capture-archive-640-en_…-d7efa712.png` | `f7087453537999f1297b53e4d8ddf61f67014e3e27570ef60610dd3c9e2ecc7e` |
| `party-capture-outskirts-640-zh_…-b75254f4.png` | `cde3cc16a63ad3436c3a20919f20d8dd4c1e4504500236ef261eebf5909cbda5` |
| `party-capture-outskirts-640-en_…-ca75b69d.png` | `0a447c471addbd902090ca37dc8c14514b1b282f2248b1fb05b2612029d5e2d0` |
| capture manifests `…-640-{zh,en}-manifest_…` | archive zh `792f3934…`, archive en `ed8c6ec4…`, outskirts zh `44ca8e38…`, outskirts en `d1f96d3d…` |
| no-sprite frames `…-640-{zh,en}-nosprite_…` | archive zh `6547af00…`, archive en `ce31bdbd…`, outskirts zh `45f10d5f…`, outskirts en `219931c1…` |
| `author-check-report_…-99449561.json` | `d686ef31f77a1b312e8525aeb366ddd5389720010140d152a007e04890349eab` |
| `capture-measure-report_…-6007228c.json` | `910ec424af31edfbbf605adc3172b5873654df16a2b90b4bf8c8c65b10c409e2` |
| `capture-run-evidence_…-d52cef71.json` | `4ee55c27745b0f926ed39cc38fc7b4409a8420a174378f397f5af55b981569d0` |
| `tools/rpg-2-star-ocean-the-second_female-battle-static_author_unapproved-v15_…-2c0b5777.py` | `de236952d4bb8a505fc4e635af38eef80e7bcd5bc38bc3bf596abfc2c4057cf4` |
| `tools/rpg-2-star-ocean-the-second_female-battle-static_v14-vs-v15-capture-measure_unapproved-v15_…-7e3a91c4.py` (read-only) | `467f167c671d5eb67358644d059798488faa33a5af5927edfc62c9d88b1b9990` |

All JSON and .py files are LF, so raw sha256 equals sha256-text-lf-v1. PNG, .pxo and .ora hashes are sha256-bytes.

Locked and unchanged before and after build and check: the four v14 sprite files, the v14 author tool and capture probe, the six v14 captures, `battle_arena.gd` (LF `5b69823f…`) and both band PNGs. `git status` gained only the three new untracked paths.

## Evidence

**Author `check` (worktree, Pixelorama 1.2.3 headless, APPDATA redirected): PASS 37/37.**

Static and preservation gates:
- binary alpha, 31 colours, no off-palette colour;
- crown row 7, sole row 67, x15–60;
- the 14 declared layers byte-identical to v14;
- changed layers keep v14's alpha, and the removed canister was inside v14's pack alpha;
- silhouette edge keys identical to v14;
- `e` lies between `C` and `c`;
- pale-accent texels in the back region (keys `GPpMZu`): 8 → 0;
- no buckle or steel on the pack;
- no `u` on the lower body.

Native source and export:
- manifest hashes and UNAPPROVED flags;
- byte-identical rebuild; a second `build` with the final tool reported all four files "unchanged";
- .pxo/.ora stacks recompose the PNG.

**Native pixel equality vs application diagnostics (separate).**
- *Native:* the Pixelorama flat export equals the PNG for both .pxo and .ora. Split export matches 20/20 layers for both, and the guides are not exported. The real APPDATA is untouched.
- *Application diagnostics (not clean, not gated):*
  - Every .pxo export prints 4× `ERROR: Condition "!actions.custom_samplers.has(...)"` (shader_compiler.cpp:1329).
  - Every .ora export prints the same shader lines plus importer/exit errors: `p_index` out of bounds ×3, `rp_node` null, "Must be an ancestor", RID/ObjectDB leaks, and "16 resources still in use".
  - The unchanged v14 .pxo and .ora controls print the same classes. Only the leak counts differ (22 vs 21 layers). So these are inherited, but **the application run is not clean**.
- No GUI Save As or reopen was run.

**Captures (real Godot 4.7.2, windowed 640×360).**
- Run through the bounded checked runner, `--expect "CAPTURE PASS"`, `--timeout 150`.
- The isolated tree is `git archive 160b823 game`: the same base and unchanged v14 probe as the root-reviewed v14 captures. After import and the runs, 1760/1760 commit files are byte-identical to their blobs. The only additions are Godot import products: 873 under `.godot/`, 53 `.import` and 37 `.uid`.
- Import also ran through the checked runner. Its expect marker is only the engine banner, because import has no success marker.
- Every run: CHECKED_RUN PASS, exit 0, no ERROR or SCRIPT ERROR. Two exit-leak WARNINGs appear in each run, identical in the v14 control runs.
- **Unchanged control:** the same probe on the v14 PNG in this tree reproduced all four tracked v14 captures byte for byte.
- Measure tool result: PASS, in all 4 runs:
  - the v15 no-sprite frame equals the v14 control's;
  - the v15 PNG over the no-sprite frame equals the capture;
  - the capture differs from v14's only inside the sprite alpha (184 px);
  - 1590/1590 sprite pixels, 0 off-palette, nearest 1.0;
  - crown y211, sole y271, bbox x283–328;
  - 0 overlap with every companion;
  - HUD zh/en as requested.

**Descriptive numbers (not gated; no contrast search was run).** Each cell is mean |ΔL| / share of texels with |ΔL| < 20 against the floor they cover, outline excluded. Same frame for both versions.

| floor | region | v14 | v15 |
|---|---|---|---|
| archive | lower body 38–67 | 37.1 / 28.9% | 42.5 / 19.1% |
| archive | coat skirt + legs 40–56 | 36.1 / 30.2% | 41.0 / 19.7% |
| archive | boots on paving | 48.9 / 14.0% | 58.2 / 14.0% |
| archive | boots in shadow | 22.2 / 37.5% | 27.2 / 17.2% |
| archive | back x≤31 rows 20–56 | 43.8 / 22.8% | 47.6 / 12.9% |
| outskirts | lower body 38–67 | 28.3 / 34.0% | 32.2 / 23.8% |
| outskirts | coat skirt + legs 40–56 | 26.0 / 36.9% | 29.0 / 25.8% |
| outskirts | boots on paving | 25.2 / 33.7% | 34.4 / 18.6% |
| outskirts | boots in shadow | 33.4 / 37.5% | 34.2 / **37.5% (unchanged)** |
| outskirts | back x≤31 rows 20–56 | 31.7 / 29.9% | 34.4 / 17.7% |

Head is identical. Torso is within ±2 points.

## Visible review at game size (actual captures) and limits

Better, judged on the actual captures (v14 tracked vs v15):
- The back reads as one teal roll over one brown pack. The grey canister mark, pale buckle and bright roll top are gone.
- The boots separate from the warm archive paving instead of reading as brown on brown, and they separate from the grey outskirts paving.
- The far leg recedes.

Still open, or possibly worse:
- **Boots inside the dark outskirts contact shadow still merge.** The dark uppers sit at about the shadow's value. Only v14's two-row lit base carries them there.
- The back tail is only a step darker. At 1× on the outskirts it remains close to the floor, and the lower-coat merge is reduced, not solved.
- The lower body is darker overall. The shape is v14's, but darker boots can read slightly heavier. The root should judge whether this crosses into "heavy boots".
- The pack is now a plainer, darker brown mass. It is calmer, but has less internal form.
- Removing the canister drops a character-sheet identity item (deviation).
- HEAD's geometric backdrop was not captured this time (bright and dark band floors only).

## Not done

- No animation, runtime swap, `battle_arena.gd` edit, default change, or Game Bible / ledger / Site / progress edit.
- No commit or push.
- No GUI Pixelorama Save As or reopen.
- No art-approval claim.
