# Female battle static v12: mass and identity pass (QA note)

Status: **UNAPPROVED, NONRUNTIME, test-only static frame.** The runtime is unchanged (battle still draws its existing female frames), nothing is committed, staged or pushed, and no counter moves: meter 40.8%, scenes 3/12, sprites 0/52. No motion work was started.

Auth: Claude Code, Opus 5.5, `claude auth status` = claude.ai / firstParty / Max; `ANTHROPIC_API_KEY` absent. No quota block was hit.

## What this answers

The creator answered "继续精修静止帧" on the v11 archive/outskirts captures (v11 not accepted). The brief is the Codex visual target `docs/qa/…battle-static-v11-creator-feedback-and-v12-visual-target_unapproved-v01_20261017-193755-c7a93e12.md`. v12 is a new fork of the v11 author tool; v11's PNG/.pxo/.ora/manifest are hash-locked and read only (`v11_unchanged` passes before and after build and check; the four tracked v11 captures are byte-unchanged).

Kept: 68×72 cell, pin (32, 68), crown row 7, sole row 67 (crown-to-sole 61 logical px), right-facing stance, head outline and face texel-for-texel, arm, glove, blade, insignia, collar and hip drape byte-identical to v11. Leftmost texel stays x15 (Liang gap) and the blade tip x60 (sentry gap).

## Changes (20 layers + hidden guides; palette 30 → 31 keys)

- **Mass:** grey-brown pack 13×13 (was 10×11), rounded corners, one strap and buckle; teal bedroll 13×7 (was 10×7) sitting on the pack top; coat skirt fuller (back tail flares to x16 and hangs to row 56; front panel to x45 with a hem rising toward the knee so the thigh shows); coat front 1–3 texels further forward on rows 30–37; near thigh 5–6 colour texels (was 4–5); far trouser 5; boots 15 wide.
- **Hair:** ponytail and head hair re-keyed darker (hair-1 share 0.33 → 0.61); new `loose-lock` layer falls from the hook tip with ≥ 1 transparent column to the tail and to the head on rows 10–15. The pale hair tie (read as a bead) is now a dark leather band.
- **Shirt wedge:** W/w framed by a dark lapel line; visible shirt texels 19 → 37; 6–7 wide on rows 34–37 (was 3), plus 3–4 above the arm (scarf tail shortened).
- **Scarf:** compact, lit top row, knot ends on row 26 (was 28).
- **Boots:** lit low-saturation brown feet over the contact shadow, dark shafts over the paving, new warm-grey outsole welt `u` #7a6f68 (L ≈ 113, saturation 0.15) on row 66. No orange anywhere below the belt (0 texels).
- **Coat hue:** unchanged v8 storm slate. The target text calls the coat "charcoal-brown" (character sheet), but the approved v8 exploration identity is slate; recolouring is left to the creator.

## Files (all untracked)

| file | sha256 |
|---|---|
| `game/assets/characters/combat-sideview-pilots/…static-native0p65_unapproved-v12_20261017-224530-fbd81525.png` (68×72 RGBA, binary alpha, Pixelorama flat export) | `27f0f79e25dd7587386c5e20df865322aea3a6de024bcf8e745fe02b97c3a079` |
| `…editable-layers_unapproved-v12_20261017-224530-b3da5b53.pxo` (pxo_version 7, 20 layers + hidden locked guides) | `a362b607647c1f3781d4b23ce40c62aa91a9fa2361e86e081a015f4f4bc8a64c` |
| `…editable-layers_unapproved-v12_20261017-224530-2ae3fe34.ora` | `4fde9395cab3cf66377f12f6f4b0c309308cc56fd43857e7eda12ca5f3c8772d` |
| `…manifest_unapproved-v12_20261017-224530-cd2b6299.json` (`art_approved`/`runtime_integrated` false) | `8b4fa592fc60d1e37e9d9333b11d96ac2d501b161ec77828945a4206311117ec` |
| `tools/…native-0p65-author_unapproved-v12_20261017-224530-74401c3e.py` | `113473402ad9f71d2211553900ab4e1f6328bd0c6ada3fc7f39584a4cd80661e` |
| `tools/…party-capture-any-size_unapproved-v12_20261017-224530-2eb05ad9.gd` | `febe5f09fb0eb1552bf4ab03089c82ddda3320e0f264d14862013fda03745226` |
| `tools/…battle-static-v11-vs-v12-capture-measure_unapproved-v12_20261017-224530-27fc2c14.py` (read-only) | `1344c01a48e33dd072527763cfa82934e6b97c545e0fbf27e74b84541d318e6c` |
| `outputs/…party-capture-archive-640_unapproved-v12_20261017-224530-ec98d813.png` | `828ed1465c4bd041f701b2a220c60e1d2c28f8f312864fba3f1a3a737f6ab8c2` |
| `outputs/…party-capture-outskirts-640_unapproved-v12_20261017-224530-b7dc7d31.png` | `da8a897fbfdb3b25d596c384e756276ea711d89fca2d851018c6e37208cc45d1` |
| `outputs/…party-capture-archive-640-draw-order_unapproved-v12_20261017-224530-409fdc2c.png` | `9fe58ba4030ff541d5b2e85e4887473a94285f3d45759ef64602e722e018f4e6` |
| `outputs/…party-capture-outskirts-640-draw-order_unapproved-v12_20261017-224530-51e84eb1.png` | `afc6346a23000c5ba6d50c9aeb19142d746b7183004bb1388b2ebe6b1ae8449d` |

Each capture has a `…-manifest_…json` beside it (archive `0a1826f9`, outskirts `fde113b2`, archive draw-order `0c9b398e`, outskirts draw-order `0d96e711`). No-sprite frames stayed in `%TEMP%\wb-fv12\cap` (not deliverables).

## Technical checks

- **`check` PASS 50/50, twice:** once with APPDATA redirected to an empty temp dir, once with the real APPDATA. Another session's Pixelorama GUI (PID 37584) was open throughout and left alone; a snapshot of the real `pixelorama` dir (excluding `.running`) was identical before and after build and check. Gates: binary alpha, palette ≤ 32, crown row 7, sole row 67, x15 ≤ bbox ≤ x62, pin row clear, both boots on row 67; manifest hashes and UNAPPROVED flags; byte-identical rebuild of .pxo/.ora; .pxo and .ora layer stacks recompose to the PNG; .ora merged image = PNG; layer/palette diff vs v11 exactly as declared; 22 identity/mass/boot gates (all listed in the manifest's `pose_gates`).
- **Pixelorama 1.2.3 headless round-trip:** .pxo and .ora flat exports equal the tool render; split-layer export 20/20 visible layers exact for both; guides not exported; the delivered PNG is the .pxo export.
- **Godot 4.7.2, real windowed 640×360 captures** (canvas_items integer stretch, k = 1, real `battle_arena.tscn`, `arena_override` band, `battle_arena.gd` sha `0c47a274…` = the v11 captures' script). All four report CAPTURE PASS: 1686/1686 texels, 0 off-palette, nearest-texel match 1.0, every texel 1×1 px, scene static.
  - *Overlay* (v11 method, comparable with v11): the v12 script run on the v11 PNG reproduces both committed v11 captures byte-for-byte.
  - *Draw-order* (new, real runtime path): the candidate is drawn by `battle_arena._draw_fighter` as fighter 0 by pointing the female idle frame-cache entries at it (translated (−2, +5) onto `HERO_COMBAT_ANCHOR` (30, 73), no resampling), with the real radius-18 contact shadows and companions drawn over it. No yellow disc (auto_mode set after the HUD update while paused). It differs from the overlay frame only in the 143-px shadow region; HUD and sprite pixels are identical, and no candidate texel is hidden by a companion. An outskirts draw-order run of v11 (temp only) matched the offline v11 composite exactly.
- **Measure tool:** in all four captures the v12 PNG composited at (268, 204) over the matching no-sprite frame equals the Godot capture exactly, and only the 1686 sprite texels differ.

## Measurement report: v11 vs v12 (same backgrounds)

**Position (both versions, all captures):** pin texel (32, 68) → screen (300, 272); crown y 211, sole y 271, crown-to-sole 61.0 logical px (67 with the ponytail); bbox x283–328, y205–271; width 46 px. Opaque-on-opaque overlap with every companion 0 px; bbox gap to Liang 5 px; to the sentry 74 px. Sole-row runs: v11 x21–32 / x39–48, v12 x19–30 / x38–50 (the pin column is now clear between the feet; the stance on the sole row is 4 texels wider).

**Silhouette width by band** (bbox width / mean opaque texels per row; the sword arm, hand and blade excluded in brackets):

| band (rows) | v11 | v12 |
|---|---|---|
| head (7–19) | 45 / 22.5 (31 / 21.6) | 45 / 24.1 (31 / 23.2) |
| torso (20–39) | 44 / 27.9 (31 / 24.3) | 44 / 33.1 (31 / 29.9) |
| coat skirt (40–56) | 30 / 20.5 | 31 / 22.8 |
| lower body (40–67) | 34 / 20.1 | 37 / 23.4 |
| boots (57–67) | 33 / 19.5 | 36 / 24.2 |
| whole sprite, opaque texels | 1473 | 1686 (+14.5%; IoU 0.87, 218 added, 5 removed) |

Coat + skirt + pack + bedroll visible texels 484 → 600 (pack 87 → 131, roll 60 → 87).

**Floor contrast** (mean |ΔL| Rec.709 against the background each texel covers, outline excluded / share with |ΔL| < 20):

| capture | region | v11 | v12 |
|---|---|---|---|
| outskirts overlay | lower body | 34.6 / 28.6% | 37.6 / 19.3% |
| | boots (57–67) | 35.6 / 34.5% | 42.3 / 15.6% |
| | boot contact rows (62–66, bg L 47) | 38.1 / 33.3% | 48.3 / 9.9% |
| archive overlay | lower body | 39.9 / 18.1% | 42.0 / 16.7% |
| | boots | 38.2 / 4.3% | 39.3 / 8.1% |
| | boot contact rows (bg L 68) | 31.6 / 5.2% | 31.0 / 12.4% |
| outskirts draw-order | boots | 31.3 / 41.0% | 36.9 / 22.6% |
| | boot contact rows (bg L 57) | 31.9 / 42.7% | 40.1 / 20.7% |
| archive draw-order | boots | 37.1 / 15.8% | 37.2 / 21.0% |
| | boot contact rows (bg L 83) | 30.0 / 21.9% | 27.7 / 32.2% |

Head |ΔL| rises 52.1 → 56.9 (outskirts) and 58.7 → 64.6 (archive); torso 50.9 → 54.7 and 51.3 → 56.2.

## Limitations (honest)

- **Bright-floor boots got slightly worse.** The lit foot (L ≈ 93) separates clearly from the dark outskirts shadow, but on archive the share of boot texels within 20 L rises (contact rows 5% → 12% overlay, 22% → 32% draw-order). In the runtime draw order the real shadow is radius 18, not the 23.4 used by the review captures, so the instep row and the near toe stand on bright paving (archive L ≈ 105–116). No single foot value separates from both archive paving and the outskirts shadow; I did not tune the art to the metric. The black outline still bounds the boot on every floor.
- **Shadow convention.** The v11/v12 overlay captures draw a 0.65-scaled 23.4 shadow; the game draws 18. Which one the integrated sprite will get is undecided.
- **Still slimmer than the companions.** Mass rose about 15% inside the fixed height and bbox, but the three companions are wider big-headed chibis; she remains the narrowest figure.
- **Pack and bedroll read as two stacked blocks** at 1×; the teal hip drape is now a thin edge behind the fuller coat tail (visible teal 22 → 12); the back tail hides most of the far thigh; the tail-or-lock-to-roll gap is 2 rows (v11: 4).
- **Coat colour** stays slate (see Changes); the shirt/coat separation was solved by width and a dark lapel line, not by hue.
- **Micro-details unchanged:** face (2×2 eye reads as one dot at 1×), insignia (4 teal texels), glove.
- **No clean-clone run.** v11's locked files are tracked (53a912f), but the v12 files, tools and the arena-band `battle_arena.gd` the captures need are local/uncommitted.

## Next

Codex/creator review of the archive and outskirts captures at 1× (overlay and draw-order). No motion, runtime swap, commit or counter change follows from this note.
