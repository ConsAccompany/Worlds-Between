# Liang Xu south idle static pilot v01: 48 px identity QA note

- **Date:** 2026-10-16 (UTC stamp 20261016-140940, run id `baa30d44`; captures 20261016-141751)
- **Scope (Task G):** one direction (south), one exploration idle **static** frame, Liang Xu only. No animation, no runtime integration, no other character touched.
- **Status:** **UNAPPROVED.** Manifest and capture report say `art_approved: false`, `human_reviewed: false`. Counters unchanged: 0/52 exploration sprites, 0/11 scene gates, 0/2 timed playtests.
- **Auth:** Claude Code signed in through claude.ai (Claude Max, firstParty). No API key, credits or paid fallback used. No image generation was used for the sprite.

## Inputs read first

- `~/.codex/AGENTS.md` naming rules (all new files follow them).
- Game Bible state, `character-01 梁序 Liang Xu`: 46-year-old mentor; visual anchors 石墨灰长外套、铜色领扣、束起的灰白发、折叠式战术板.
- [Liang Xu character sheet](../../outputs/rpg-2-star-ocean-the-second_liang-xu_character-sheet_v01_20261013-153556-c7630671.png) and the 2026-10-14 [premium south concept](../../game/assets/characters/high-fidelity-prototypes/rpg-2-star-ocean-the-second_liang-xu_south-exploration-premium-pixel_m8-concept_20261014-153531-4c6e2bcd.png), for design only. No texels were taken from either.
- Prior 48 px city captures: [Liang solo](../../outputs/rpg-2-star-ocean-the-second_scifi-city_liang-xu-character-quality-h48-canvas-items_m8-v02_20261014-153547-1ca1259c.png), [three-character scale review](../../outputs/rpg-2-star-ocean-the-second_scifi-city_liang-xu-male-female-south-scale-review_m8-concept_20261014-153644-9226ceab.png), [native south preview](../../outputs/rpg-2-star-ocean-the-second_liang-xu_native-game-preview-south_m8-v03_20261014-180100-f3128e01.png).
- [Science companions 48 px identity-transfer audit](rpg-2-star-ocean-the-second_science-companions_48px-identity-transfer-codex-audit_unapproved-v01_20261016-114641-a9e6c2d1.md). It found that the forelock, bun and tablet do not read at game size, and that Liang needs two long coat tails with negative space between them.
- Female selout v8 [decision](../character-visuals/rpg-2-star-ocean-the-second_protagonist-female_south-idle-static-baseline-decision_m8-v08_20261015-022700-07161696.md), [QA note](rpg-2-star-ocean-the-second_protagonist-female_south-idle-selout-v8_visual-qa-note_m8-v08_20261015-021600-c1694107.md) and harness. v8 is used as the **quality and scale benchmark only**: same 80×112 cell, pin (40,104), 96-texel body, 0.5 display scale, 1-texel ink outline. No v8 texel, colour or design element was copied.
- [Pixel-art production pipeline](../design/rpg-2-star-ocean-the-second_character-sprites_pixel-art-production-pipeline_unapproved-v01_20261015-040155-ffd3391d.md) (role layers, P1–P5 and S1–S5 gates).

## Files (all new)

| File | Hash |
|---|---|
| [pilot PNG, 80×112](../../game/assets/characters/liang-xu/south-idle-static-pilot-unapproved-v01/rpg-2-star-ocean-the-second_liang-xu_south-idle-static-pilot_unapproved-v01_20261016-140940-46a036ed.png) | sha256-bytes `9fee901809d33128839779cc1e926fc314f4d92fd11baa3b857d4cffebfe38ab` |
| [editable Pixelorama `.pxo`](../../game/assets/characters/liang-xu/south-idle-static-pilot-unapproved-v01/rpg-2-star-ocean-the-second_liang-xu_south-idle-static-pilot-editable_unapproved-v01_20261016-140940-65edcfd2.pxo) | sha256-bytes `26024bdd2c2d16b29c6a0e5df63a17038d29829506f505f0ca37f13a73ff09ee` |
| [palette (named ramps)](../../game/assets/characters/liang-xu/south-idle-static-pilot-unapproved-v01/rpg-2-star-ocean-the-second_liang-xu_south-idle-static-pilot-palette_unapproved-v01_20261016-140940-cda9b0c6.json) | sha256-text-lf-v1 `6d0be31c634e113fcdbecdd655d7791f4b2f9e05f59487601d774cfd2f7e9c4f` |
| [manifest](../../game/assets/characters/liang-xu/south-idle-static-pilot-unapproved-v01/rpg-2-star-ocean-the-second_liang-xu_south-idle-static-pilot-manifest_unapproved-v01_20261016-140940-74be7552.json) | sha256-text-lf-v1 `5cd6fea99e3ba4d8298448d57c9b450185040f39a7f965020a70475521b0bcfa` |
| `.gdignore` (empty) in the same folder | keeps Godot from importing the folder, as pipeline §6 requires; no `.import`/`.uid` files were made |
| [build/check tool](../../tools/rpg-2-star-ocean-the-second_liang-xu_south-idle-static-pilot-build-and-check_unapproved-v01_20261016-140940-6a60848d.py) | sha256-text-lf-v1 `a91cea8abfe3d4cc8b1028f69a53e004bc3cd72b6116c5a3d8298a1bfc56609b` (matches the manifest) |
| [Godot capture tool](../../tools/rpg-2-star-ocean-the-second_liang-xu_south-idle-static-pilot-godot-capture_unapproved-v01_20261016-140940-0e7a1c55.gd) (`-s`, lives outside `res://`) | sha256-text-lf-v1 `b553990b620edf795c88abee26511cdfb8a7b5a16e8fd1049d8465ed83af238f` |
| [×4 nearest preview, sprite only](../../outputs/rpg-2-star-ocean-the-second_liang-xu_south-idle-static-pilot-x4-nearest-preview_unapproved-v01_20261016-140940-3018cfc8.png) | sha256-bytes `6021596235fa7196539f6a763c0f4e3ed0c1641a721e157fa8b289ae935b4c35` |
| captures and report | see the Godot section |

## How it was made

- **Source of truth:** two literal 56×96 grids inside the build tool, placed at cell offset (12,8).
  - `MAP` holds the colour keys.
  - `ROLE` holds the role-layer keys.
  - Every texel was placed or edited by hand.
- **Blocking:** a scratch primitive pass (not shipped) seeded the large masses first.
- **Hand passes:** the head, bun and forelock rows were typed by hand. Then came cluster passes for:
  - the collar and copper ring;
  - turned-back lapels;
  - the navy tunic with a copper front placket joining the collar ring to the belt ring;
  - the pocket arm with its elbow out, rolled cuff and copper cuff button;
  - the board and gloved hand;
  - belt, skirt hem, trouser folds, boots and straps;
  - per-row tail folds and lining wedges.
- **Not used:** resampling, filtering, quantization, dithering or AI image generation.
- **Palette:** 33 colours in 11 named ramps; light from the upper left.
- **Pixelorama layers** (bottom to top, pipeline §1.3 order). Layers do not overlap; their union equals the PNG exactly.

| Layer | Texels |
|---|---|
| `hair-back` (bun) | 117 |
| `arm-far` (pocket arm) | 145 |
| `boots` | 320 |
| `legs` | 304 |
| `accessory` (board, collar ring, belt) | 211 |
| `torso-coat` | 1015 |
| `arm-near` (tablet arm and hand) | 52 |
| `head-face` | 150 |
| `hair-front` (dark hair and silver forelock) | 157 |
| `guides` (hidden, locked: border, rows 8/103, pin) | — |

## Identity cues at ordinary game size

All figures below are in texels, which equal window pixels at 1280×720. They are report-only measurements and are recorded in the manifest.

- **High bun.**
  - The bun is 14 px wide and 9 rows tall, above a 6 px pinch. The crown below it is 16 px wide, so each side shows a notch of about 4 px. This is the outline difference from the protagonist's ponytail and Zhao Ling's bob.
  - Six grey strand texels run through the bun, for the Bible's 灰白发.
- **Broad silver forelock.**
  - 82 texels, cell rows 19–36.
  - It sweeps from a part right of centre across the forehead (9 px wide at its widest) and down the viewer-left cheek.
  - Mean L\* is 73.7 against 21.2 for the dark hair (ΔL\* 52.4).
- **Split long coat tails.**
  - The coat opens below the belt. The two tails flare to hems at mid-calf with pointed outer tips.
  - Background shows between each tail and the boots from cell row 73–74 down to the hem (1–4 px slots). There is also a 2 px gap between the legs.
  - Navy lining wedges (1–3 px) mark the inner faces of the lower tails.
- **Tablet (property cue).**
  - A 9×19 folding board at cell (52,42)–(60,60), sticking out 9 px past the sleeve.
  - 49 copper texels make the frame and ring emblem; copper vs coat is ΔE76 69.2. Two screen-glow texels.
  - A fingerless glove grips the inner edge.
- **Pose:** hand in pocket with the elbow out, which leaves a background triangle at the waist. The eyes look toward the board.
- **Head+hair overlap with v8 (S4, report only):** IoU 0.293 at the matched pin. The pipeline sets no threshold until a pair is user-judged.

## Technical gates (`check` mode: PASS)

| Gate | Result |
|---|---|
| P1 alpha | binary alpha; no opaque texel on the border |
| P2 palette cap | 33 colours (cap 48) |
| P3 declared palette | every colour is declared; no declared colour is unused |
| P4 ramp spacing | minimum adjacent L\* step 12.62, against 11.87 measured from v8's declared cloth ramps. To pass, four colours were nudged (hair-dark, coat D, trousers T, boots o/q). The two inks and the single brow colour are exempt as non-ramps, as in v8 |
| S1 height and pin | body height 96; alpha bounds (17,8)–(62,103); sole row 103 above pin (40,104); feet centre x 39.5 |
| S5 determinism | two in-process builds are byte-identical; files on disk equal a rebuild; PNG decodes to the maps |
| Pixelorama 1.2.3 headless | two flattened exports are texel-identical to the PNG (0 differing) and byte-identical to each other. The split-layer export matches all 9 role layers exactly; `guides` is not exported. The source `.pxo` is unchanged by the CLI |
| Isolation | every CLI run used `APPDATA=<fresh temp>`; the real `%APPDATA%\pixelorama` had no changes (the GUI heartbeat `.running` is ignored) |

## Godot captures (Godot 4.7.2, windowed, real scenes)

Settings: 640×360 canvas, `canvas_items`, 1280×720 window, sprite scale 0.5, nearest filter, no shadow.

Liang is placed at hero placeholder x + 36. That is the spot where v8 was user-reviewed: the city window is (729,412) against v8's (731,412), with the same foot centre. In the benchmark frames, v8 stands beside the placeholder at −36 (city) and +80 (annex).

Each file is a separate full frame; there is no collage.

| Scene | Liang alone | Liang + v8 benchmark |
|---|---|---|
| Science city, bright | [city solo](../../outputs/rpg-2-star-ocean-the-second_city-bright_liang-xu-south-idle-static-pilot-h48_unapproved-v01_20261016-141751-bd083d0a.png) `d2c34078…bdc20` | [city + v8](../../outputs/rpg-2-star-ocean-the-second_city-bright_liang-xu-pilot-with-female-v8-benchmark-h48_unapproved-v01_20261016-141751-bd083d0a.png) `bc232b41…bbf1` |
| Survey annex room 2, dark interior | [annex solo](../../outputs/rpg-2-star-ocean-the-second_survey-annex-room2-dark_liang-xu-south-idle-static-pilot-h48_unapproved-v01_20261016-141751-bd083d0a.png) `b8e6dc18…a3b7` | [annex + v8](../../outputs/rpg-2-star-ocean-the-second_survey-annex-room2-dark_liang-xu-pilot-with-female-v8-benchmark-h48_unapproved-v01_20261016-141751-bd083d0a.png) `72cab5f1…8423` |

- Full sha256-bytes values are in the [capture report](../../outputs/rpg-2-star-ocean-the-second_city-bright-dark_liang-xu-south-idle-static-pilot-capture-report_unapproved-v01_20261016-141751-bd083d0a.json) (sha256-text-lf-v1 `42919c83b400c790fce28ccc1da46308bb6581719f3ad64186ee7a8473434787`).
- **Gates, all passed (exit 0):**
  - both source SHA locks;
  - 1280×720 frames;
  - Liang window exactly 46×96 and v8 window exactly 43×96 (1:1);
  - texel fidelity 2471/2471 (Liang) and 2419/2419 (v8);
  - the two sprites' windows do not touch.
- **Side effects:** none. A `git status` diff around the runs shows only the new files above; no `.uid`/`.import` files were made and no tracked file changed.

Contrast, CIELAB ΔE76, mean / min, Liang only (reported, not gated). "Ring" is against the median of an 8 px ring of background; "row-local" is against the ring pixels within ±6 rows. Both use the same method as the v8 QA.

| Region (texels) | City ring | City row-local | Annex ring | Annex row-local |
|---|---|---|---|---|
| whole figure (2471) | 43.0 / 20.9 | 50.4 / 10.9 | 32.7 / 9.1 | 32.5 / 8.1 |
| coat (725) | 35.3 / 21.0 | 46.3 / 14.6 | 26.1 / 22.0 | 26.3 / 19.1 |
| silver forelock (82) | 27.7 / 20.9 | 29.2 / 21.6 | 39.5 / 23.1 | 39.0 / 21.6 |
| bun (117) | 44.6 / 20.9 | 39.2 / 15.3 | 28.4 / 9.1 | 30.4 / 10.4 |
| tablet (170) | 48.5 / 21.8 | 50.1 / 21.3 | 37.7 / 13.1 | 38.3 / 13.1 |
| tail lining (68) | 54.7 / 54.3 | 69.4 / 47.3 | 48.2 / 44.2 | 46.3 / 41.3 |
| boots (220) | 40.0 / 21.8 | 41.7 / 10.9 | 24.5 / 13.1 | 21.9 / 11.5 |

For reference, v8 in the same scenes had whole-figure ring means of 38.6 (city) and 29.0 (annex).

## Shortcomings, for the root visual judgement

1. **Stiffer than v8.** The legs stand straight and symmetric with no contrapposto, and the trousers read as two dark columns. v8's weight shift, belt pouches and asymmetric cape give it more life. Fixing this needs leg geometry redrawn, not recolouring.
2. **Silver vs bright paving.** In the bright city the silver forelock sits close in value to the pale stone (ring mean 27.7). It reads because of the dark hair beside it and the ink outline, not by value against the ground. It is the strongest cue in the dark annex (39.5).
3. **Dark masses in the annex.** The graphite coat, bun and boots separate from the warm-brown floor mainly by the 1-texel ink (bun ring min 9.1, boots row-local min 11.5). The silver, copper and navy accents carry the read there.
4. **The board may read as a phone or book.** At 9×19 the copper frame and ring are clear, but "folding tactical board" is not explicit. Only 2 screen-glow texels are shown.
5. **Tail slots are small.** They are 1–4 px and start only below about cell row 73. The figure is already 46 px wide against v8's 43; wider flaring would widen it further.
6. **Age read.** Composure, narrowed eyes, one nasolabial texel and the silver hair carry the age. The face is small (12 px) and may still read younger than 46.
7. **Proportion.** Because the bun uses about 10 of the 96 rows, Liang's shoulders sit lower than the protagonist's at the same 48 px total height. This follows the previously approved scale rule (visible height including hair), but Liang reads slightly shorter in body.
8. **Changed HUD text.** The city HUD title now reads 下曼哈顿 · 市政厅公园, from another workstream's destination rename. The scene art and placement code match the v8 run, but the frames are not pixel-comparable to v8's at the HUD.
9. **Not done:**
   - north and side facings (the audit's next step);
   - 1920×1080 sampling (1.5 px per texel);
   - GUI-saved `.pxo` round trip, which needs a person at the GUI;
   - the confusion-pair check against Heya (no Heya sprite exists).
10. **Pronoun inconsistency.** The Task G brief calls Liang "his"; the 2026-10-14 concept review says "her"; the Bible entry does not say. The face and figure follow the identity sheet unchanged.

## Unchanged

- No other character, runtime scene or script, readiness ledger/checklist, Game Bible file, `docs/progress.md` or acceptance counter was edited.
- The v8 PNG is still `ccf9d2a2…b6fd`. No commit or stage was made in Git.

## Reproduce (from the repository root)

```
python -I -B tools/rpg-2-star-ocean-the-second_liang-xu_south-idle-static-pilot-build-and-check_unapproved-v01_20261016-140940-6a60848d.py build
python -I -B tools/rpg-2-star-ocean-the-second_liang-xu_south-idle-static-pilot-build-and-check_unapproved-v01_20261016-140940-6a60848d.py check
work/tooling/godot-4-7-2/Godot_v4.7.2-stable_win64_console.exe --path game -s <absolute path>/tools/rpg-2-star-ocean-the-second_liang-xu_south-idle-static-pilot-godot-capture_unapproved-v01_20261016-140940-0e7a1c55.gd
```

- `python` is the real runtime Python (3.12.14, Pillow 12.3.0, NumPy 2.3.5).
- `build` reports `unchanged` when the files match and refuses to overwrite different bytes.
- The Godot run writes a fresh set of captures with a new stamp.
