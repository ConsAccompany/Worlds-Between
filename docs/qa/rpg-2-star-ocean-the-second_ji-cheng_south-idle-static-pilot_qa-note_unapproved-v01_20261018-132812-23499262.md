# 纪澄 / Ji Cheng — south idle STATIC pilot v01 — QA note (UNAPPROVED, NONRUNTIME)

Run `04cd6a26`, stamp `20261018-132812` (UTC). Worktree `work/max0840-ji-cheng`, branch
`codex/ji-cheng-south-static-v01-20261018-0920` from exact `160b823`. Not committed, not pushed.

**Status:** technical static pilot for root review only. Art is UNAPPROVED and not human-reviewed. The pilot is not
wired into the runtime, has no animation and no other direction. Runtime sprites stay **0/52**, scene visuals **3/12**,
the meter stays **40.8%** and plays stay **0/2**. This pass changed no runtime, default, shared Game Bible or ledger file.

## What was made

One south-facing exploration idle frame of Ji Cheng. It uses the approved female selout v8 cell and pose template:
an 80x112 cell, a 96-texel body (cell rows 8..103), foot pin (40,104) and display scale 0.5, so it shows at
**48 logical px**. It has a 1-texel near-black outer outline, light from the upper left, and 2–4 step material ramps.
It was authored fresh from hand-placed row spans, strokes and small stamps in four bounded passes, judged at x5 and at
1x/2x next to v8, then frozen as literal 56x96 `MAP`/`ROLE` grids in the build tool. No image generation, sampling of
the sheet, resampling, filtering, quantization or dithering was used, and no texel or palette entry from v8, the old
32x48 Ji Cheng or any other character was copied or recoloured.

No newer Ji Cheng high-density static existed (searched all branches, worktrees and outputs), so this is v01, not a
revision.

## Identity read from the sheet (not guessed from the name)

Source: `outputs/rpg-2-star-ocean-the-second_ji-cheng_character-sheet_v01_20261013-190436-dcea1a37.png`. Its registry
approval is `concept`, the only portrait on record. The old review describes her as a 28-year-old relic restorer.

| Sheet trait | In the pilot |
| --- | --- |
| Her **left** temple shaved with razor lines, rectangular drop earring | Pale stubble patch on the viewer-right head outline: 28 texels, cell bbox (45,13)–(48,21), four darker razor-line texels, ear, 4-texel brass drop earring |
| Blue-black straight bob, side part above the shaved side, swept across the forehead toward her right | Crown swept from the part to the viewer-left, with a sheen along the sweep. The hair reaches 14 px left of the face centre; the head reaches 11 px right |
| Bob falls to the shoulder on her right, silver-white ends; shorter silver-tipped lock behind the shaved side | Jagged curtain with three silver points, plus a short lock behind the ear: 71 silver texels in total |
| Dark forest-green long open coat, uneven pointed hem, grey rolled linings, worn brass | Forest-green ramp (825 texels). Long ragged point on the viewer-left, cut-away hem on the viewer-right. Grey cuffs, pocket flap, seams, brass toggles and trim glints |
| Folding brass magnifier raised in her right hand | Gloved right forearm raised; a 7x6 brass ring with lit glass sits beside the hair, with 1–2 px of clear background between them on cell rows 27–38 |
| Book in her left hand; black high collar with buckle; brown chest harness, belt, hip vials/pouch, thigh strap; cream patterned cloth; black gloves/trousers/buckled boots | All present at 1–3 texel scale |

## Files (all new, untracked)

Assets live in `game/assets/characters/ji-cheng-hd/`. That folder has a `.gdignore`, so Godot never imports it.

| File | SHA-256 |
| --- | --- |
| `…ji-cheng_south-idle-static_unapproved-v01_20261018-132812-1920ff13.png` (80x112, binary alpha) | `58c92f51959aa7b34dfc9d37c953665579fe75b5629e6d8c807180cba4a32a1d` |
| `…south-idle-static-editable_unapproved-v01_20261018-132812-d4b5aa5e.pxo` (Pixelorama 1.2.3, 13 role layers + hidden locked guides) | `ce9c1fab360c04b7412142a14dca5cd211b91d7e3b14e840a0cc0b4de6b8b69c` |
| `…south-idle-static-layers_unapproved-v01_20261018-132812-f5077465.ora` (same layers) | `e3cca7bdd7c4250a90778c196a2329cf8a3905cb144595e00f951c5715f046e6` |
| `…south-idle-static-palette_unapproved-v01_20261018-132812-f94e7fac.json` (16 named ramps, 38 colours) | text-lf `da909135…` |
| `…south-idle-static-manifest_unapproved-v01_20261018-132812-e65f21d8.json` | text-lf `5cf59841…` |
| `tools/…ji-cheng_south-idle-static-pilot-build-and-check_unapproved-v01_20261018-132812-0d31a6f9.py` | `18ef5efc…` |
| `tools/…ji-cheng_south-idle-static-pilot-godot-capture_unapproved-v01_20261018-132812-81f87641.gd` | `eede7fe8…` |
| `outputs/…south-idle-static-pixelorama-check-report_unapproved-v01_20261018-132812-87d370be.json` | `26986940…` |
| `outputs/…south-idle-static-x4-nearest-preview_unapproved-v01_20261018-132812-39012108.png` | `b8929b9a…` |
| `outputs/…south-idle-static-godot-capture-report_unapproved-v01_20261018-133420-cab29676.json` + 16 capture PNGs (below) | `3a59e509…` (report) |

The 13 role layers, bottom to top, with texel counts: coat-back 88, cloth-panels 157, legs 269, boots 303,
coat-front 708, inner-top 111, harness-belt 115, arm-hanging 130, book 86, arm-raised 139, magnifier 60, head-face
212, hair 442. The arms, magnifier, book, hair and head are separate layers, ready for a later animation pass. Each
layer is a flat partition of this one frame, so texels hidden behind a part are not drawn.

## Technical gates (build/check tool, real Python `-I -B`)

`check --pixelorama <Pixelorama 1.2.3>` result: **PASS**.

- **Hard gates:** binary alpha, nothing on the cell border, 38 colours (cap 48), all declared, none unused. Body 96 texels, rows 8–103, sole row 103, pin x 40 inside the feet span.
- **Rebuild:** byte-equal. A second `build` reports every file `unchanged`. The manifest's reference hashes are current.
- **Pixelorama round trips:** the official CLI ran headless with APPDATA redirected to a temp dir. For both the .pxo and the .ora:
  - two flattened exports are byte-identical and RGBA-equal to the PNG;
  - a `--split-layers` export gives exactly the 13 role layers, and the hidden guides are not exported;
  - the input files are unchanged.
- **User's Pixelorama config:** nothing of ours changed. Only the open GUI's `.running` heartbeat moved.
- **Locked sources unchanged:** all five female v8 source files and the old 32x48 Ji Cheng south frame (`13372e64`).
- **Report-only value steps:** the minimum adjacent L\* step is 12.14, against v8's 11.87, after one hex-only retune of the hair, coat, black-top and trouser darks.
- **Report-only speckle:** 53 isolated single texels against v8's 145. The pilot is cleaner, and flatter, than v8.

## Real Godot evidence (Godot 4.7.2, windowed)

The test harness hides the old placeholder hero (`visible = false`) and stands the pilot on the hero's ground point
by its foot pin. No `game/` file was added or edited. Captures cover the science city (bright, first-visit layout)
and the city survey annex room 2 (the darker interior used by earlier pilots), in the Chinese and English UI.

All gates passed:

- **1280 window:** the pilot's diff window is exactly **42x96 window px = 48 logical px**, with **2820/2820 texels exact RGB**.
- **Pivot:** window left = 2·spot_x − 24 and window bottom = 2·ground_y. City spot (340, 254) gives window x 656, bottom 508. Annex spot (87, 262) gives x 150, bottom 524.
- **v8 pair frames:** v8 is 43x96 with 2419/2419 exact texels, on the same ground row, and does not overlap the pilot.
- **Native 640x360 window:** the pilot's window is **21x48** with its bottom on ground_y. All 703 changed pixels are pilot palette colours, so nearest sampling with no blending.

Scale labels (also recorded per capture in the report):

- `solo-1280-1x`, `with-female-v8-1280-1x`: 1280x720 window, 1 texel = 1 window px = 0.5 logical px (the default game window).
- `…-2x-crop`: a crop of that window, nearest x2. This is a review aid only.
- `native-640-1x`: the window resized to the 640x360 canvas, so 1 logical px = 1 window px. The 96-texel sprite is nearest-subsampled 2:1, so about half the texels are not shown.

Captures in `outputs/`, all suffixed `_unapproved-v01_20261018-133420-cab29676.png`, with prefix
`rpg-2-star-ocean-the-second_ji-cheng_south-idle-static-`:

- `city-bright-zh-solo-1280-1x`, `city-bright-zh-solo-1280-2x-crop`, `city-bright-zh-native-640-1x`
- `city-bright-en-solo-1280-1x`, `city-bright-en-solo-1280-2x-crop`, `city-bright-en-with-female-v8-1280-1x`, `city-bright-en-with-female-v8-1280-2x-crop`, `city-bright-en-native-640-1x`
- `annex-room2-dark-zh-solo-1280-1x`, `annex-room2-dark-zh-solo-1280-2x-crop`, `annex-room2-dark-zh-native-640-1x`
- `annex-room2-dark-en-solo-1280-1x`, `annex-room2-dark-en-solo-1280-2x-crop`, `annex-room2-dark-en-with-female-v8-1280-1x`, `annex-room2-dark-en-with-female-v8-1280-2x-crop`, `annex-room2-dark-en-native-640-1x`

The zh and en 2x solo crops of each scene are byte-identical, because no UI text falls inside the crop. The 1x
frames differ by their UI.

Contrast against an 8 px ring median (CIELAB dE76; mean / min; report-only, same in zh and en):

| Region | City bright | Annex room 2 |
| --- | --- | --- |
| whole figure | 42.7 / 5.4 | 27.5 / 10.4 |
| hair black | 49.1 / 29.6 | 25.2 / 18.5 |
| silver tips | 27.1 / 24.8 | 38.7 / 25.2 |
| shaved temple | 16.0 / 13.0 | 29.4 / 21.9 |
| coat | 41.2 / 27.2 | 22.6 / 19.2 |
| magnifier | 28.0 / 20.2 | 39.6 / 13.2 |
| cream cloth | **15.1 / 5.4** | 40.2 / 28.8 |
| boots | 46.0 / 34.4 | **20.0 / 10.4** |
| v8 whole figure (pair) | 39.3 / 6.1 | 30.1 / 6.9 |

## Visible limitations (candid)

- **Stiff pose.** It is frontal and nearly symmetric from the waist down. It lacks v8's weight shift and is less dynamic. The legs are parallel columns.
- **Less material texture than v8.** There are 53 against 145 isolated texels. The coat is cleaner but flatter, and the boots read as heavy dark blocks.
- **Cream cloth panel.** On the viewer-left it reads as a narrow plank, and it nearly vanishes against bright city paving (min dE 5.4).
- **Shaved patch.** It is clear at 2x and is the only pale area on the head's right outline. At 1x it could still be read as a pale hair streak; that needs the creator's eye. The razor lines are lost in the native 640 view.
- **Silver tips.** They sit on the shoulder line and could be read as shoulder trim at 1x.
- **Book.** At the hip it reads as a small brown box or pouch rather than clearly a book.
- **Thin details.** In the native 640 view (2:1 subsampling), the earring, collar buckle, strap buckles and toggles drop out or flicker by position.
- **Placement in annex room 2.** At the default hero spot the pilot stands near the exit arrow, which is close but does not overlap.
- **Placeholders unchanged.** The game still shows the old placeholder hero and the old 32x48 Ji Cheng (ruins NPC, party). Nothing was integrated.

## Pending decisions for root / creator

1. Does the shaved temple read as shaved scalp (not grey hair) at 1x?
2. Do the silver tips read as hair ends rather than shoulder pads?
3. Is the raised magnifier the right idle pose, or should the idle hold it lower (the sheet's chibi has both hands down)?
4. Should the cream cloth panel be reduced or darkened?
5. Is a stiffer frontal stance acceptable for a quiet archivist, or should weight shift be added (as v8 has) before any animation?

## Reproduce

All commands run from the worktree root, using real Python `-I -B`.

1. Build: `python -I -B tools/…0d31a6f9.py build`. It never overwrites a different file.
2. Check: `python -I -B tools/…0d31a6f9.py check --pixelorama work/tooling/pixelorama-1-2-3/Pixelorama-Windows-64bit/Pixelorama.exe`.
3. Prepare Godot captures with one `Godot_v4.7.2-stable_win64_console.exe --headless --path game --import`, with APPDATA set to a temp dir.
4. Capture: `Godot_v4.7.2-stable_win64_console.exe --path game -s <absolute path of tools/…81f87641.gd>`, windowed.
5. The import rewrote the CRLF of 378 tracked `.import` files and added 90 `.import`/`.uid` sidecars. In this worktree these were restored (`git checkout -- .`) and deleted afterwards. `git status` now shows only this pilot's 23 untracked entries (28 files: 6 in the asset folder, 2 tools, 1 QA note, 19 outputs).
