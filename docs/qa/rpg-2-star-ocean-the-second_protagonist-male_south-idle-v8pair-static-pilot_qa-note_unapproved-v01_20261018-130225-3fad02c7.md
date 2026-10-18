# Male protagonist south idle static pilot, paired to female selout v8 (v01): QA note

Status: **UNAPPROVED, NONRUNTIME.** This is one static south-facing exploration idle frame of the male protagonist at the approved 48 logical px. There is no animation, no other direction, no other character and no runtime wiring. The test harness hides the old placeholder only inside its own capture run.

Counters are unchanged: runtime sprites **0/52**, scenes **3/12**, meter **40.8%**, plays **0/2**. Nothing was committed or pushed. No Game Bible, ledger, progress or counter file was edited.

Session: worktree `work/max0840-male`, branch `codex/male-south-static-v01-20261018-0850`, based on `160b823564cf9212f4c03d2b78e92ca8e2b6c969`. `claude auth status` reported `loggedIn: true`, `authMethod: claude.ai`, `apiProvider: firstParty`, `subscriptionType: max`. No Anthropic API key variable was set. There were no quota or auth errors, and no image generation, paid API or credits were used. Run stamp 20261018-130225 UTC, run id `3617dbe6`.

## What was read

- Global `~/.codex/AGENTS.md` (naming rule).
- The male character sheet `outputs/…protagonist_character-sheet_male_20261013-153316-5b7c19e2.png`, viewed as an image. It is the identity source.
- The approved female v8 PNG `…selout-v8-cloth-leather-candidate…157a5ea0.png`. I read it as an ASCII colour map to get its rows and spans: head top row 8, chin row 33, shoulders around row 34, belt rows 54–56, knee pad around rows 74–79, boot tops row 85, sole row 103. I also read its outline and ramp language.
- The v8 decision and visual QA notes.
- The cast identity audit `…science-cast_hairstyle-and-identity-at-48px…9234b6e1.md`. For the male it asks for uneven outward-pointing short hair, the teal scarf, an open field coat and the pack/bedroll. It rules out a rounded cap and a recoloured female frame.
- The pipeline design `…pixel-art-production-pipeline…ffd3391d.md`, read at its 160b823 version (the primary checkout has uncommitted edits to it). Its "Pixelorama for the female only" boundary is overridden here by the explicit request for a male .pxo. Its "male vs female differ in silhouette mass, not recolour" rule was followed.
- The male v02 QA note, plus the local v01/v02 tool and Godot capture script, read-only from the primary checkout. I reused their tooling pattern: the .pxo/.ora writer, the CLI round-trip, the capture approach.

No v01/v02 art, nothing from the rejected 32×48 frame, and no v8 texel or palette entry was used as a base.

## How it was made

The source of truth is a pair of literal 56×96 grids, `MAP` (colour keys) and `ROLE` (layer keys), in the build tool. To author them, I placed each part by hand in a scratch script (kept in `%TEMP%`, not shipped) using spans, polygons, 1-texel strokes and small stamps:

- bedroll, pack and coat skirt;
- sash, legs and boots;
- torso/coat, harness and both arms;
- face, hair and scarf.

I judged four drafts at x5 over grey, dark-floor and bright-floor colours, and at 1x/2x beside v8. The final draft was frozen into the tool, and the built PNG is byte-for-byte equal to that draft.

A deterministic 4-neighbour pass adds the 1-texel near-black outline, as in v8. A short list of front/back part pairs gets internal separation lines.

No sampling or resampling of the concept sheet was done, and no filtering, quantization or dithering.

- **Pixel scale:** native 96 body texels map to 48 logical px. Scale 0.5, nearest filtering, binary alpha.
- **Light:** upper left, as in v8.
- **Palette:** 34 colours in named ramps of 2–4 steps (v8 has 32).
- **Identity cues kept from the sheet:**
  - tousled dark-brown short hair with uneven tufts, 26 px wide against a 13 px face;
  - a 3/4 face turned to the viewer-left, with thick straight brows, 2×2 eyes and a small closed smile;
  - the teal scarf;
  - an open warm grey-brown field coat with a popped collar;
  - the viewer-left hand gripping the pack strap, as in the sheet's front view;
  - rolled cream cuffs and fingerless gloves;
  - the teal emblem, belt buckle and teal sash;
  - olive-grey trousers with a knee pad and cargo pocket;
  - tall cuffed boots;
  - a teal bedroll with a spiral end on a brown pack behind the viewer-right shoulder.
- **Pose:** relaxed idle. Weight is on the viewer-right leg; the viewer-left leg angles out with its foot set back (sole row 101 against 103).

## Files

All are new and untracked in the worktree. Hashes are sha256 of the bytes. The two JSON files are written with LF line endings, so their sha256-text-lf-v1 hash equals the byte hash.

| File | sha256 |
| --- | --- |
| `game/assets/characters/protagonist-male-v8pair/rpg-2-star-ocean-the-second_protagonist-male_south-idle-v8pair_unapproved-v01_20261018-130225-79ed5d37.png`: candidate PNG, 80×112 cell, visible 39×96 | `e4b2db368f65e158724dff4c8844fe2dcabf9f9b7f7a9aa3807d76bd72409af2` |
| `…/rpg-2-star-ocean-the-second_protagonist-male_south-idle-v8pair-editable_unapproved-v01_20261018-130225-f6b08a07.pxo`: pxo v7, 13 role layers plus hidden, locked `guides` | `216b3a29579b86042ee49de6ece50b7702cc6c863e7dec32ac6d79e8a1e2ea0c` |
| `…/rpg-2-star-ocean-the-second_protagonist-male_south-idle-v8pair-layers_unapproved-v01_20261018-130225-587897cb.ora` | `bba61903b962cb38a2ccd24bc203a4ed1ca778bf2e9c680a35398350bbf0b9f3` |
| `…/rpg-2-star-ocean-the-second_protagonist-male_south-idle-v8pair-palette_unapproved-v01_20261018-130225-c1cfbc02.json` | `041f012d7ef922da1ae84630c046fca623aa723fb0d9a36b001d61a0716c3988` |
| `…/rpg-2-star-ocean-the-second_protagonist-male_south-idle-v8pair-manifest_unapproved-v01_20261018-130225-da428624.json` | `4acb8bf326dbf9f844086c843b4cb4817299e0432e8d3545818a56c0f4631cf0` |
| `…/.gdignore` | empty |
| Build/check tool `tools/rpg-2-star-ocean-the-second_protagonist-male_south-idle-v8pair-static-pilot-build-and-check_unapproved-v01_20261018-130225-f28bd26d.py` | `fcd9d6e88e7401097e9c8afe8061df6dcdd9e2132892680522d7d722ac2abb79` |
| Godot capture tool `tools/rpg-2-star-ocean-the-second_protagonist-male_south-idle-v8pair-static-pilot-godot-capture_unapproved-v01_20261018-130225-098354f7.gd` | `d7d7e1a078e0d78f5f20a4166099ebd440cd8a6f20a404f720acce968533c91b` |
| `outputs/rpg-2-star-ocean-the-second_protagonist-male_south-idle-v8pair-x4-nearest-preview_unapproved-v01_20261018-130225-0cb74546.png` (sprite alone, x4) | `e93abe83007dc33f2922b55cff80837fcb503d1fb387e6bae0ddc0ffff7cb9c3` |

The 13 layers, bottom to top: bedroll, pack, coat-skirt, sash, legs, boots, torso-coat, harness, arm-hanging, arm-grip, head-face, hair, scarf. The hidden `guides` layer holds:
- the cell border;
- ticks on v8's template rows: head top 8, shoulder 34, belt 54, knee 76, sole 103;
- the pin at (40,104).

## Technical evidence

`python -I -B <tool> check --pixelorama <work/tooling/pixelorama-1-2-3/…/Pixelorama.exe>` returned **PASS** (exit 0). The parent and each child run used a separate temporary `APPDATA`. The check covered:

- **Rebuild:** the PNG, .pxo, .ora, palette and manifest are equal to a fresh deterministic rebuild. The manifest file hashes and all 7 reference hashes are current, and the PNG decodes exactly to the grids.
- **Hard gates:**
  - binary alpha;
  - transparent border;
  - 34 colours, all declared, none unused;
  - **96-texel body (rows 8–103) = 48.0 logical px**;
  - sole on row 103;
  - pin (40,104) inside the feet span.
- **Layers:** the 13 role layers do not overlap and reassemble the sprite exactly.
- **.ora structure:** the mimetype entry comes first and is stored, only `guides` is hidden, each layer equals its role blob, and mergedimage equals the PNG.
- **Official Pixelorama 1.2.3 CLI, for both .pxo and .ora:**
  - two flattened exports, RGBA-equal to the PNG and byte-identical to each other;
  - split-layers 13/13 exact, guides not exported;
  - inputs unchanged.
- **Female v8 kept exact:** the 5 v8 source files are hash-locked: PNG, .import, cloth-leather manifest, editable .pxo and editable manifest. After cleanup, `git status` lists no tracked change, and `git ls-files --eol` shows the v8 text files back in their checkout CRLF form.
- **Real AppData:** a before/after snapshot of `%APPDATA%\pixelorama` and `%APPDATA%\Godot` showed only `pixelorama\.running` and one `backups\…(untitled backup)` file changed. Those belong to another session's open Pixelorama GUI (heartbeat and autosave), which I left alone. No Godot file changed.
- **Report-only:**
  - minimum ramp step 6.79 L\* (hair 3→4) against v8's 11.87; every other ramp step is ≥ 9.6;
  - 58 isolated single texels (v8: 145);
  - scarf/bedroll 4-neighbour contacts: 4, at the collar's right edge.

**Godot 4.7.2-stable (official), windowed** (`--path game -s <abs tool path>`, exit 0). I ran one `--headless --import` in the worktree first, with `APPDATA`/`LOCALAPPDATA` set to a temp directory.

- Settings: the project's own display settings (640×360 canvas, canvas_items, 1280×720 window), scale 0.5, nearest filtering, no shadow.
- Placeholder: hidden by the harness. The pilot stands at the placeholder's spot by its foot pin.
- Scenes: the bright science city and the dark survey annex room 2, each in the zh and en UI.
- Gates passed in all 4 scene/language runs:
  - **pilot window 39×96 window px = 48 logical px**;
  - **texel match 2488/2488 exact RGB**;
  - **pivot**: window left equals 2·spot_x − 18 and window bottom equals 2·ground_y. City: spot (340, 254) → left 662, bottom 508. Annex: spot (87, 262) → left 156, bottom 524.
- v8 pair frames: 43×96, 2419/2419, on the same ground row, with no overlap.
- Placement change: in the en city frame, v8 was first placed at its earlier spot (x − 36). The English district label covers that spot, so v8 matched only 2399/2419 texels there. v8 was moved to x + 40, the pilot's right. That failed run and the debug frames were deleted.

Captures (all in `outputs/`, stamp `20261018-131126-1bae8044`). The "1x" frames are the full 1280×720 window as the game shows it. The "2x crop" frames are nearest x2 crops around the figure(s).

| Capture | sha256 |
| --- | --- |
| `rpg-2-star-ocean-the-second_protagonist-male_south-idle-v8pair-city-bright-zh-solo-1x_unapproved-v01_20261018-131126-1bae8044.png` | `87b2d7572885fc0a76883ddc11bec6dfd266a81568a58e6fb23b823415df322e` |
| `…-city-bright-en-solo-1x_…png` | `0a415b1b9288d28307ecfe236c7cffe1c8a0b343a3fd37aa5cdf8f1bd846ade5` |
| `…-annex-room2-dark-zh-solo-1x_…png` | `de860c2bd49b902f4e4b176b2b64349f63f8644e038aa90d2c84d8173493f283` |
| `…-annex-room2-dark-en-solo-1x_…png` | `76aa58ce3f78fc0b8f5aee977540c8e4698e731d0e8b08ccff57b6f9f083d57b` |
| `…-city-bright-zh-solo-2x-crop_…png` (byte-identical to the en crop: no UI text inside the crop) | `7ed6d40fda0d8b345b1d379c39e1077b6bc5f46855409c9ee0a9cff252e32b40` |
| `…-city-bright-en-solo-2x-crop_…png` | `7ed6d40fda0d8b345b1d379c39e1077b6bc5f46855409c9ee0a9cff252e32b40` |
| `…-annex-room2-dark-zh-solo-2x-crop_…png` | `d872668508c7b314591df9c7dc3bbf6e6e654cbc9f162c1f7e6f721a1c6c84a3` |
| `…-annex-room2-dark-en-solo-2x-crop_…png` | `428cc81beb6dd228570e794b721e6e51b129a122582c79053758874c0cde3531` |
| `…-city-bright-en-with-female-v8-1x_…png` | `29f096d2d92cfd078ecc97aab73156df5e97ba517282c8286c33289c36340efa` |
| `…-city-bright-en-with-female-v8-2x-crop_…png` | `c92fa02d231ffdc3d824bc8aace42e4a8bb51bf060bb96e32bc6b42d128df303` |
| `…-annex-room2-dark-en-with-female-v8-1x_…png` | `e0a3e51da389b1daa0340c020e1b67bcc265f3b50b839ae1fe433dd62e201469` |
| `…-annex-room2-dark-en-with-female-v8-2x-crop_…png` | `cdea97c7bd961a0ccf2fca5868a3f361c99bf523476c2bc2166e653bc460cdb1` |
| Report `…-godot-capture-report_unapproved-v01_20261018-131126-1bae8044.json` | `b63ab9bd89723f44dbb84c347f8d5909e6d293203ecb9ba02a730a884c7686a5` |

Mean ΔE76 against the 8 px ring median. This is a proxy only, not a quality claim.

| Region | City (zh = en) | Annex (zh = en) |
| --- | --- | --- |
| Whole figure | 38.2 | 24.8 |
| v8 whole figure, same frame | 39.3 | 30.1 |
| Hair / face / scarf | 46.7 / 25.1 / 36.3 | 22.1 / 42.9 / 41.8 |
| Coat / trousers / boots | 28.0 / 26.7 / 35.1 | **9.5 / 10.1** / 17.7 |
| Shirt (min) | 23.8 (5.2) | 46.5 |

Worktree hygiene: the Godot import rewrote the line endings of 413 tracked `.import` files (content-identical under `--ignore-cr-at-eol`). It also created 90 `.uid`/`.import` files for other workstreams' assets. I restored the tracked files from git and deleted the 90 generated files. `git status -uall` now lists only the 23 files of this deliverable: the 22 in the two tables above plus this note. `game/.godot/` (gitignored) remains in the worktree.

## Visual judgement (mine, not approval)

In the 1x city frame he reads as the sheet's traveller: dark tousled hair wider than the head, a bright teal scarf, the bedroll on his right shoulder, an open brown coat over a cream shirt, a teal sash and tall boots. Beside v8 in the 2x crops the two read as a matching pair: same outline weight, upper-left light and cluster size. He is distinct by silhouette, through the short wide hair, broader shoulders, longer coat and the hand on the strap, not by recolouring. He stands a few pixels taller at the crown than her skull, because her ponytail tip sets her row 8.

## Observable limits (candid)

1. **Dark annex: the coat and trousers merge with the warm floor.** Mean ΔE is 9.5 and 10.1, against v8's figure at 30.1. At 1x the lower body reads mainly through the outline, the cream cuffs, the sash and the boots. Fixing this would mean a cooler or darker coat, which moves away from the sheet's warm grey-brown.
2. **The hair crown reads as three tidy spikes** rather than the sheet's looser mop. The hair's darkest ramp step (6.79 L\*) is compressed, so the shadow side reads near-flat.
3. **Less micro detail than v8** (58 against 145 isolated texels). The chest and coat are cleaner but flatter. v8 has more buckles, accents and fabric breakup.
4. **The pose is stiffer than v8's.** The legs and torso are near-frontal. The grip hand reads as a dark knot with skin knuckles at 1x, and as a hand on the strap only at 2x.
5. **The shirt opening is a large bright block.** In the city its lowest contrast against the pale paving is ΔE 5.2. Only the coat edges separate it.
6. **The face is simple.** Brows, 2×2 eyes and a 3-texel smile. At 1x it reads as "young man, pleasant". The sheet's expressive smile does not carry.
7. **The scarf touches the bedroll edge** at the collar's right (4 contacts). The two teals differ in value, but at 1x they come close to joining.
8. **Coverage.** One static south frame only. No 1920×1080 sampling, no runtime swap, no animation, no other directions.

## For the root reviewer

1. Open `…city-bright-en-with-female-v8-2x-crop…png` and `…annex-room2-dark-en-with-female-v8-2x-crop…png` for the pairing check.
2. Then open the four `…solo-1x…png` frames for true game scale.
3. Decide whether limit 1 (dark-room coat) and limit 2 (crown) need a targeted pass before any animation or other direction.
