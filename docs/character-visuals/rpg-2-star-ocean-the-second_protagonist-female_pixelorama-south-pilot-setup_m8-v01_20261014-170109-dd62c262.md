# Female protagonist · south-only Pixelorama pilot · setup note · M8 v01

**Status: technical pilot run, not approved.** Pixelorama v1.2.3 (web build) produced one south **idle** frame in two steps: a downscale and a downscale with four hand-painted texels. Neither is art-approved or used at runtime, and the pilot contains **no walk frames**. Acceptance is unchanged: **0/52** exploration sprites and **0/11** scene-quality gates ([art pipeline decision memo](rpg-2-star-ocean-the-second_character-visuals_art-pipeline-decision-memo_m8-v01_20261014-165532-0cc81856.md)).

This is the free-editor fallback the memo lists as missing (Method A, feasibility S6). The user asked for one **manually reviewed** pilot: female protagonist, **south direction only**. No batch work, no other directions or characters.

Updated 2026-10-14 (21:14 UTC). The first version of this note was written before the editor was used. It said Pixelorama had not been launched, that no art files existed, and that the user still had to launch it. All three are now out of date.

Corrected 2026-10-14. The 21:14 version said the paint pass had no 48 px city capture. That was wrong: variant-tagged captures of **both** steps exist (21:14:25 and 21:14:31 UTC). The screenshot QA section and open gate 1 below now cover both.

## Editor

The user ran the **web build** of Pixelorama v1.2.3 in a browser. Both `.pxo` files record `pixelorama_version: v1.2.3-stable` and `pxo_version: 7`. The Windows build staged earlier (below) is still on disk, but nothing shows it was used for this pilot.

| Item | Value |
|---|---|
| Release | Pixelorama **v1.2.3**, official `Orama-Interactive/Pixelorama` GitHub release, published 2026-09-15 by `github-actions[bot]`, not a prerelease |
| Staged Windows asset | `Pixelorama-Windows-64bit.zip`, 40,853,820 bytes, SHA-256 `942e38288b818ef44e0c834691a00a521f811739af523a2cfdc09aae58753646` (matches the GitHub release digest) |
| Staged executable | `work/tooling/pixelorama-1-2-3/Pixelorama-Windows-64bit/Pixelorama.exe`, SHA-256 `6412014e27f31e6ad7eed64c1f4e80551a40c6cfd815bb00dc74b10f34b92f10`, FileVersion 1.2.3.0. **Not signed.** |
| `Pixelorama.pck` SHA-256 | `ba1fd5657b9c9ac5420f5d79851935bbb0e2bfd66303ad41ab186bf13b26205f` |
| Git | `work/` is ignored. `.gitignore` was not changed. |
| Cost | Free (MIT licence). No account, API key, paid service or AI generation was used. |

**Not verified:** where the web build stores its settings (presumably browser storage), and where the Windows build would store them.

## What was made

All four files are in `game/assets/characters/pixelorama-pilots/`. The [pilot manifest](../../game/assets/characters/pixelorama-pilots/rpg-2-star-ocean-the-second_protagonist-female_south-idle-pixelorama-pilot-manifest_m8-v01_20261014-211454-868681b7.json) records each file's source, hash and relationship. No collage or sprite sheet was made. Godot has no `.import` entry for them, and no runtime script or scene references them. Only the QA test scene loads them, and it reads them straight from disk.

| Step | File | Size | SHA-256 |
|---|---|---|---|
| 1 · editable downscale | `…south-idle-editable-pilot_m8-v01_20261014-210343-7e2c9a1f.pxo` | 96×115, 1 layer, 30,805 B | `f9a313a0…0c0a43c9` |
| 1 · PNG export | `…south-idle-downscale-pilot_m8-v01_20261014-210343-c45a80e2.png` | 96×115 RGBA, 12,399 B | `d5776400…364ecb05f2` |
| 2 · editable paint pass | `…south-idle-handpolish-pilot_m8-v01_20261014-210652-94e8b110.pxo` | 96×115, 2 layers, 31,193 B | `bc3acc44…7b51` |
| 2 · PNG export | `…south-idle-handpolish-pilot_m8-v01_20261014-210652-438e6fb3.png` | 96×115 RGBA, 12,414 B | `93327c6e…b7c159` |

Full hashes are in the manifest.

**Source (read-only):** `game/assets/characters/high-fidelity-prototypes/rpg-2-star-ocean-the-second_protagonist-female_south-exploration-premium-pixel_m8-concept_20261014-145800-62c3a10f.png`, 1145×1374, SHA-256 `28f9efac…2fb222`. It was imported into the browser editor. Git shows no change to it since commit `b1aff00`.

**Step 1.** The whole source canvas was scaled with nearest-neighbour sampling to 96×115, one uniform scale (about 0.0838). The PNG matches a Pillow nearest resize of the source at 11,019 of 11,040 texels. The other 21 differ by ±1 in a single channel on semi-transparent texels, which is export rounding.

**Step 2.** The step-1 layer was kept untouched: the raw `Layer 1` data is byte-identical in both `.pxo` files. A separate `readability-paint` layer holds exactly **4** hand-placed hair-highlight texels, all RGBA (139, 96, 72, 255), at (34,11), (33,13), (31,16) and (29,19). The two PNGs differ at those four texels and nowhere else. Texel (29,19) was fully transparent before, so one highlight adds an opaque texel at the hair edge.

## Measured against the memo's pilot parameters

These parameters come from the memo and are not an approved standard. The pilot does not meet most of them yet:

| Check | Memo target | Measured | Met |
|---|---|---|---|
| Cell | 80×112 | 96×115 | no |
| Visible body height (E4) | 96 ±1 texels | 107 | no |
| Partial-alpha texels (E5) | 0 | 3,476 (downscale), 3,473 (paint pass) | no |
| Colours (E5) | ≤48 | 3,070 RGBA values (downscale), 3,068 (paint pass) | no |
| Opaque texels on cell border | 0 | 0 | yes |

Almost the whole sprite is semi-transparent. Only 5 texels in the downscale are fully opaque, and 3,017 have alpha 250–254, which comes from the source. Quantizing the palette and making the alpha binary would be the next technical step, if the user wants to continue on this route.

The E6 hand-work budget (≤12 texels) applies to walk frames, so this idle frame does not test it. The 4-texel log above is the first entry.

## Screenshot QA (48 logical px)

All captures come from `game/tests/rpg-2-star-ocean-the-second_protagonist-female_pixelorama-south-pilot-city-visual-qa_m8-v01_20261014-213000-5b9e2f47.tscn`, which takes `--pilot=downscale` or `--pilot=handpolish` and writes the variant into the file name. The pilot is scaled so its alpha ≥128 bounds are 48 logical px tall (factor 0.4486, nearest filter, `canvas_items` 640×360 shown at 1280×720). It stands on the same ground line as the current 32×48 female placeholder in the science city.

| Variant shown | Capture | Size | Bytes | SHA-256 |
|---|---|---|---|---|
| Step 1 · downscale | [`…pixelorama-south-downscale-pilot-h48-beside-placeholder_m8-v01_20261014-211425-c01ae148.png`](../../outputs/rpg-2-star-ocean-the-second_scifi-city_protagonist-female-pixelorama-south-downscale-pilot-h48-beside-placeholder_m8-v01_20261014-211425-c01ae148.png) | 1280×720 RGBA | 1,532,741 | `8708ba8d…6266d59` |
| Step 2 · four-texel paint pass | [`…pixelorama-south-handpolish-pilot-h48-beside-placeholder_m8-v01_20261014-211431-209c5b2d.png`](../../outputs/rpg-2-star-ocean-the-second_scifi-city_protagonist-female-pixelorama-south-handpolish-pilot-h48-beside-placeholder_m8-v01_20261014-211431-209c5b2d.png) | 1280×720 RGBA | 1,532,740 | `8a3adfe5…07f7df19` |

Full hashes are in the manifest.

- **Untagged earlier capture.** `…pixelorama-south-pilot-h48-beside-placeholder_m8-v01_20261014-210813-c3f6fba6.png` (no variant tag) is **byte-identical** to the tagged downscale capture (same SHA-256 `8708ba8d…`, `cmp` reports no difference). It is a duplicate of the step-1 capture, not a third result.
- **Downscale vs paint pass, pixel diff.** The two tagged captures decode to identical RGB at every window pixel except **4**, and all window pixels are opaque in both. Each of the four painted texels survives at 48 px as exactly one window pixel showing (139,96,72):

  | Texel | Window pixel | Downscale capture | Paint-pass capture |
  |---|---|---|---|
  | (34,11) | (740,418) | (32,28,27) | (139,96,72) |
  | (33,13) | (739,420) | (71,49,44) | (139,96,72) |
  | (31,16) | (737,423) | (36,26,28) | (139,96,72) |
  | (29,19) | (735,425) | (146,127,101), the paving behind the hair | (139,96,72) |

  The highlight colour occurs 0 times in the downscale capture and 4 times in the paint-pass capture. The 21:14 version of this note said texel (29,19) "falls between sampled columns" and is not shown; the real paint-pass capture shows it, so that placement-fit estimate was wrong.
- **Honest four-texel assessment (technical, not a verdict):** the paint pass is a 4-pixel change in a 921,600-pixel frame: four isolated single pixels along the hair, one of which extends the hair silhouette by one pixel onto the paving. It does not change the partial-alpha, palette or height results above. Whether those four pixels read as a highlight at play distance, or are worth the hand work, has **not** been judged by anyone. That is the user's call (E10), and neither capture is art-approved.
- **Technical observation, not a verdict:** at 48 px the downscale keeps far more costume detail than the placeholder. The face and hair are noisy at this size, and the soft partial-alpha fringe is visible against the paving. Whether the approved detail survives is the user's call (E10).

## Guard rails (still in force)

- The source PNG and the four pilot files are not to be overwritten. New work gets new unique names.
- Nothing goes into the runtime until the user approves it.
- One image per file. No sprite sheets, atlases, contact sheets or GIFs.
- No AI pixels in any frame (memo stop condition 3).
- Log every hand-edited texel per frame (E6).
- E10 review belongs to the user alone.

## Open gates

1. **User review (E10)** of both tagged 48 px captures against the approved 48 px screenshot: is the detail kept, and are the four highlight pixels worth it? (Both captures exist; nothing is approved.)
2. Partial alpha, palette and body height: either fix them, or the user explicitly changes those pilot targets.
3. **Walk speed (R2)** is still undecided. Walk frames, other directions and the other 51 variants have not been started.
4. Runtime integration, in-motion review, the 11 scene-quality gates and two genuine human M7/M9 playthroughs remain open.
