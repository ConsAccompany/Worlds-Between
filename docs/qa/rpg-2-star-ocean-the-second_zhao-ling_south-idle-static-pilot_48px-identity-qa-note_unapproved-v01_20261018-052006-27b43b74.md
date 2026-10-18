# Zhao Ling south idle static pilot v01: 48 px identity QA note

- **Date:** 2026-10-18, stamp `20261018-052006` (local EDT), run id `7027d25c`. **Current captures `20261018-053525-2baef17e`** (v01r1 harness, player placeholder hidden); the first set `20261018-052703-dfb8d67a` is kept unchanged as history.
- **Scope:** one direction (south), one exploration idle **static** frame, Zhao Ling only. No animation, no other facing, no runtime integration, no other character touched.
- **Status:** **UNAPPROVED, NONRUNTIME.** The manifest and capture report say `art_approved: false` and `human_reviewed: false`. Exploration sprites stay **0/52**. No ledger, Game Bible, checklist, inventory, progress or counter file was edited.
- **Auth:** Claude Code signed in through Claude Max. No API key, paid or cloud fallback was used, and no image generation was used for the sprite.

## Identity sources read

| Source | What it fixes |
|---|---|
| [Character sheet](../../outputs/rpg-2-star-ocean-the-second_zhao-ling_character-sheet_v01_20261013-193120-54215370.png) (1916×821), front full-body view x≈30–400 | asymmetric bob; earcup + antenna on her left ear (viewer-right); oversized near-black jacket with light-grey collar and rolled cuffs; white tee; crossbody straps; hip radio on the viewer-right hip with coiled cable; tablet in her right hand (viewer-left); fingerless gloves; baggy charcoal trousers with rolled grey cuffs and hanging blue straps; black lace-up boots with blue-grey soles |
| same sheet, head close-ups x≈870–1580, y≈0–370 | side part; long fringe over her right eye (viewer-left); blue inner tips at the jaw; grey-blue eyes; steel-rimmed teal-blue earcups; black antenna with brass tip; hand raised to the earcup |
| same sheet, chibi turnarounds x≈1380–1916, y≈480–740 | the front view shows **one** visible earcup, with the antenna rising from it; the back view shows a radio pack |
| same sheet, radio prop x≈830–1350, y≈340–800 | black/brass radio, waveform screen, knob, tool tray, strap |
| [Character bible](../../outputs/rpg-2-star-ocean-the-second_remaining-companions_character-bible_v01_20261013-181920-6d2a4f8c.md), entry 31 | **赵铃 / Zhao Ling**, female, 26, firearms (枪械), city radio repair technician; 湖蓝耳机、整齐的侧分短发和便携天线; skill 回声测距 |
| [48 px identity-transfer audit](rpg-2-star-ocean-the-second_science-companions_48px-identity-transfer-codex-audit_unapproved-v01_20261016-114641-a9e6c2d1.md) and [hairstyle audit](rpg-2-star-ocean-the-second_science-cast_hairstyle-and-identity-at-48px_unapproved-v01_20261016-183000-9234b6e1.md) | needs the asymmetric chin-length bob, teal tips, round earcup, vertical antenna, and crossbody comms kit as a second mass; outline wider on the fringe side; don't treat the headset as a bun; don't borrow Liang's silver streak |
| [2026-10-14 native review](../character-visuals/rpg-2-star-ocean-the-second_zhao-ling_native-exploration-review_m8-v01_20261014-142600-582df7a1.md) and its 32×48 frames | the old body that lost the cues. **Not reused, recoloured or upscaled.** The premium concept was not used either. |
| Female selout v8 [decision](../character-visuals/rpg-2-star-ocean-the-second_protagonist-female_south-idle-static-baseline-decision_m8-v08_20261015-022700-07161696.md) | **Benchmark only:** same 80×112 cell, pin (40,104), 96-texel body, 0.5 scale, 1-texel outer ink. No v8 texel, colour or design element was copied. |

All reference files are tracked and were clean at HEAD `c20118d`. Their hashes are locked in the manifest, and `check` re-verifies them.

## Files (all new, untracked, not staged)

| File | Hash |
|---|---|
| [pilot PNG 80×112](../../game/assets/characters/zhao-ling/south-idle-static-pilot-unapproved-v01/rpg-2-star-ocean-the-second_zhao-ling_south-idle-static-pilot_unapproved-v01_20261018-052006-73f1d603.png) | sha256-bytes `069acee4ba3c25c55cd381e19ab3a7453bb9ddd7fe27ff69eca7068c038859f7` |
| [editable Pixelorama `.pxo`](../../game/assets/characters/zhao-ling/south-idle-static-pilot-unapproved-v01/rpg-2-star-ocean-the-second_zhao-ling_south-idle-static-pilot-editable_unapproved-v01_20261018-052006-9c80d0fc.pxo) | sha256-bytes `78ad93cfa83c4be62549fd996f8ec7d566e5138af892fa89e1122892a1527a2e` |
| [layered `.ora`](../../game/assets/characters/zhao-ling/south-idle-static-pilot-unapproved-v01/rpg-2-star-ocean-the-second_zhao-ling_south-idle-static-pilot-editable-layers_unapproved-v01_20261018-052006-2e77e99e.ora) | sha256-bytes `180f86a94456a5a13f92288b5c7d286530af953e20c9a9b31e84c3bfa14c6fb4` |
| [palette, named ramps](../../game/assets/characters/zhao-ling/south-idle-static-pilot-unapproved-v01/rpg-2-star-ocean-the-second_zhao-ling_south-idle-static-pilot-palette_unapproved-v01_20261018-052006-1622a443.json) | sha256-text-lf-v1 `2d1394cf6c5e6389dcff1e07353709d22541c9f9750bbb845e778dbfd318765b` |
| [manifest](../../game/assets/characters/zhao-ling/south-idle-static-pilot-unapproved-v01/rpg-2-star-ocean-the-second_zhao-ling_south-idle-static-pilot-manifest_unapproved-v01_20261018-052006-fe4b7eda.json) | sha256-text-lf-v1 `de07cd94a1ad88a7927f9d41bf6476c4b1bafd2b78a08f030f0ddd4b3681f5eb` (regenerated after the name/question text fix; the first version `3a90e316…43dc` is kept in `%TEMP%\wb-zhao-scratch\superseded`) |
| `.gdignore` (empty) in the same folder | Godot does not import the folder; no `.import` or `.uid` file was created |
| [build/check tool](../../tools/rpg-2-star-ocean-the-second_zhao-ling_south-idle-static-pilot-build-and-check_unapproved-v01_20261018-052006-36f0253c.py) (about 580 lines, about 200 of them literal grids; grids unchanged, manifest text fixed) | sha256-text-lf-v1 `11baed2cf3799ef3939fb1dab6e671cc7f7558a851f87bcbe23ca752078d35b1` |
| [shared v8-format utils](../../tools/rpg-2-star-ocean-the-second_static-pilot-v8-format_shared-utils_unapproved-v01_20261018-052006-fcae68d3.py) | sha256-text-lf-v1 `7c8f3c0fd42751a1dd0233bbff32bd6ad5970473bdf35d929c5c27c94e778425` |
| [Godot capture tool v01r1, player hidden](../../tools/rpg-2-star-ocean-the-second_zhao-ling_south-idle-static-pilot-godot-capture-player-hidden_unapproved-v01r1_20261018-053437-4c1e9a07.gd) (test-only, `-s`, outside `res://`; **current**) | sha256-text-lf-v1 `7e03bcecbac5d93718149183ca9c720a9f957280157f65467ad0ca48e117a278` |
| [Godot capture tool v01](../../tools/rpg-2-star-ocean-the-second_zhao-ling_south-idle-static-pilot-godot-capture_unapproved-v01_20261018-052006-692aadba.gd) (history; left the player placeholder visible) | sha256-text-lf-v1 `f20dc7165a5f6d8977b689ba1e698e8607045684ca50066e2799445675b2929f` |
| [×4 nearest preview, sprite only](../../outputs/rpg-2-star-ocean-the-second_zhao-ling_south-idle-static-pilot-x4-nearest-preview_unapproved-v01_20261018-052006-2695076d.png) | sha256-bytes `c09ca5e3c4170e52261052177f0702974f41e1653d9a9ed4bf73d4852f8c8a6a` |

The shared utils module holds the character-agnostic parts of the Liang and male pilot tools: the pxo/ora writers, the gates, and the isolated Pixelorama CLI round trip. It takes a parameter spec, so the Zhao tool carries only its grids, ramps, references and identity metrics. The Liang and male tools are unchanged.

## How it was made

- **Source of truth:** two literal 56×96 grids in the build tool, `MAP` (colour keys) and `ROLE` (layer keys), placed at cell offset (12,8).
- **Seeding:** a scratch primitive script (not shipped; kept in `%TEMP%\wb-zhao-scratch`) seeded the masses and the outer ink.
- **Hand pass:** the head rows 8–34 were hand-typed: halo sheen, side part, a fringe lock sweeping over the viewer-left eye, three blue-tipped strands, the oval earcup, the 2-px band, the antenna, and the chin/collar rows. After that came the body details: the arm gap, contrapposto legs, the open uneven hem, the sleeve patch, snaps, the cargo pocket, and the boot lace zigzag.
- **Review:** each change was judged on ×3/×6 previews over the city and annex floor colours, then in real Godot.
- **Not used:** resampling, filtering, quantization, dithering or image generation.
- **Palette:** 33 colours in 11 lit ramps plus ink/eye/mouth, with light from the upper left. The minimum adjacent L\* step is **12.76**, against 11.87 for v8. Two colours (hair `g`, jacket `j`) were nudged to pass.
- **Layers** (bottom to top; no overlaps; the union equals the PNG):

| Layer | Texels |
|---|---|
| `hair-back` | 6 |
| `boots` | 314 |
| `legs` | 606 |
| `torso-jacket` | 394 |
| `straps-belt` | 93 |
| `radio-kit` | 160 |
| `arm-tablet` | 289 |
| `arm-near-radio` | 150 |
| `head-face` | 103 |
| `hair-front` | 290 |
| `headset-antenna` | 86 |
| `guides` | hidden + locked |

## Source cues kept, and proposed pixel simplifications

**Kept, with report-only measurements** (cell px = window px at 1280×720):

- **Bob.** Hair extends 10 px left of the face on the fringe side and 1 px on the tucked side. The fringe side drops to row 34; the tucked side ends at row 30.
- **Blue tips.** 29 lake-blue texels in three strands, rows 28–34, ΔE76 44.9 against the hair.
- **Headset.** One earcup, 5×9 (15 blue texels), plus 17 band texels.
- **Antenna.** Column 48, rows 8–20: 4 px above the crown, with a brass collar and tip.
- **Jacket.** Oversized jacket with a popped grey collar and rolled cuffs, over a white tee.
- **Strap and radio.** A dark crossbody strap with a brass buckle runs to an 11×10 hip radio. The radio sticks out 10 px past the trousers and has a waveform screen. A 3×10 coiled cable hangs from it.
- **Tablet.** 10×12, held in a fingerless glove, sticking out 10 px past the sleeve, with a waveform.
- **Lower body.** A lake-blue strap hangs on the viewer-left thigh. Rolled grey cuffs. Boots with a lake-blue sole edge (23 texels).
- **Accent colour.** ΔE76 24.9 against v8's teal, so the two accents are different colour families.

**Proposed simplifications** (for the root to judge, also listed in the manifest):

1. **Pose.** The sheet's hand-to-earcup gesture is replaced by a neutral idle: the tablet is held at the hip, and the viewer-right arm hangs above the radio.
2. **Tablet.** It is shown screen-forward with an echo waveform. The sheet shows its dark back. This keeps it from reading as Liang's copper board.
3. **Accent colour.** The sheet's muted steel-teal is pushed to a brighter lake blue (the Bible's 湖蓝).
4. **Jacket value.** The jacket is lifted from near-black to a dark charcoal, and the trousers sit one step lighter.
5. **Gear.** One strap replaces several. The hip tool pouch with vials, the thigh holster pouches and the second hanging strap are dropped. The radio has no tool tray and no antenna of its own.
6. **Second earcup.** It is hidden by the fringe, as in the sheet's front views.
7. **Face.** 2-texel eyes, a 1-texel nose and a 2-texel mouth.

## Name and design notes

- **Name:** the canonical, existing name is **赵铃 / Zhao Ling** (character bible, Game Bible state, asset inventory, app strings). The brief's 赵羚 was a coordinator typo, not an open creator question.
- **Weapon:** the sheet shows no firearm, so none is drawn. This south static needs no answer on it.
- **Pending for later directions only:** whether the sheet's back radio pack (with its own antenna) is the same unit as the hip radio. It matters for the north and side facings, not for this south static.

## Technical gates

**Build:** hard gates pass.

| Gate | Result |
|---|---|
| P1 | binary alpha; no opaque texel on the border |
| P2 | 33 colours (cap 48) |
| P3 | every colour declared and used |
| P4 | min step 12.76 |
| S1 | height 96 (rows 8–103, antenna tip at row 8, hair crown at row 12); sole row 103; sole span 26–52 contains pin x 40; visible 46×96 |
| Determinism | two in-process builds are byte-identical |

The 96-texel height includes the antenna tip, just as Liang's height included the bun. The head's top ink is at row 11, about two rows above v8's (row 13). Zhao's head therefore reads slightly larger than v8's.

**`check` (PASS, exit 0):**

| Gate | Result |
|---|---|
| Rebuild equality | rebuilt PNG, `.pxo`, `.ora`, palette and manifest equal the files on disk |
| Hash locks | manifest file hashes match; all 10 reference locks are current; the v8 PNG is still `ccf9d2a2…b6fd` |
| PNG decode | the PNG decodes back to the grids exactly |
| `.ora` structure | mimetype is first and stored; `guides` is the only hidden layer; layers recompose to the PNG; `mergedimage` equals the PNG |
| Pixelorama 1.2.3 headless CLI, `.pxo` and `.ora` each | two flattened exports are RGBA-equal to the PNG and byte-identical to each other; the split-layer export matches all 11 layers exactly; `guides` is not exported; the input is unchanged |

- **Isolation:** every CLI run used `APPDATA=<fresh temp>`, and nothing of ours changed in the real `%APPDATA%\pixelorama`.
- **Another session's GUI:** that session's Pixelorama GUI (PID 37584) was open. Only its `.running` heartbeat and an untitled autosave backup changed, and the check excludes those as GUI-owned.

## Godot captures (Godot 4.7.2, windowed, test-only harness)

**Harness fix (v01r1).** The first capture set (`…052703-dfb8d67a`) left the runtime player placeholder (the chunky heroine) visible next to Zhao, so its "solo" frame was not a solo frame. The v01r1 harness sets the placeholder `visible = false` after reading its ground line and before the baseline frame, then fails if it is visible in any saved frame. Background NPCs, world and UI are untouched. Art, palette and proportions are unchanged (the PNG is still `069acee4…59f7`).

**Settings:**

- 640×360 canvas, `canvas_items`, 1280×720 window.
- Sprite scale 0.5, nearest filter, no shadow.
- Zhao is placed by her foot pin at placeholder x + 36, the Liang/v8 review spot; `hero_appearance = "female"` only sets the hidden placeholder.

**Current frames** (each a separate full frame, no collage). In the science city the old runtime Liang Xu NPC remains, as world content; it is not Zhao.

| Scene | Zhao alone | Comparison with approved v8 |
|---|---|---|
| Science city, bright | [city solo](../../outputs/rpg-2-star-ocean-the-second_zhao-ling_south-idle-static-pilot-city-bright-h48_unapproved-v01r1_20261018-053525-2baef17e.png) `f630614a…0866` | [city vs v8](../../outputs/rpg-2-star-ocean-the-second_zhao-ling_south-idle-static-pilot-vs-female-v8-city-bright-h48_unapproved-v01r1_20261018-053525-2baef17e.png) `815c229d…81f1` |
| Annex room 2, dark | [annex solo](../../outputs/rpg-2-star-ocean-the-second_zhao-ling_south-idle-static-pilot-annex-room2-dark-h48_unapproved-v01r1_20261018-053525-2baef17e.png) `bab9a434…566f` | [annex vs v8](../../outputs/rpg-2-star-ocean-the-second_zhao-ling_south-idle-static-pilot-vs-female-v8-annex-room2-dark-h48_unapproved-v01r1_20261018-053525-2baef17e.png) `10554567…c95b` |

- **Report:** [capture report v01r1](../../outputs/rpg-2-star-ocean-the-second_zhao-ling_south-idle-static-pilot-capture-report_unapproved-v01r1_20261018-053525-2baef17e.json) (sha256-text-lf-v1 `39196a332dc57abf8b5fc8d9b10b7608284846d369671e316ceff0a371e5ec0d`).
- **Gates, all passed:** source SHA locks (Zhao, v8); player placeholder hidden in every saved frame (a 60×84 window was removed each time); 1280×720 frames; Zhao window exactly 46×96 and v8 exactly 43×96, both 1:1; texel fidelity 2491/2491 (Zhao) and 2419/2419 (v8) in every frame; the two windows do not touch.
- **History (not current):** the v01 frames `…052703-dfb8d67a` (city `9b07178f…b761`, annex `b4260d5a…346c`, comparisons `b97314b5…5214` / `be198976…7995`, report `c5f5954d…e755`) stay on disk unchanged.
- **Side effects:** a `git status` diff around the rerun shows only the five new v01r1 outputs; no `.uid`/`.import`, no tracked file changed. `check` was re-run after the manifest fix: **PASS**.

Contrast is unchanged from the first run (the placeholder was outside Zhao's ring).
Contrast, CIELAB ΔE76 ring mean / min, Zhao only (report-only; same method as the v8/Liang QA):

| Region | City | Annex |
|---|---|---|
| whole figure | 39.5 / 16.3 (v8 43.9) | 32.0 / 9.3 (v8 30.1) |
| hair | 45.5 / 35.3 | 32.8 / 29.0 |
| blue hair tips | 40.9 / 40.6 | 45.0 / 37.9 |
| earcup + band | 33.9 / 22.4 | 39.4 / 23.1 |
| antenna | 45.4 / 27.2 | 34.9 / 33.6 |
| face skin | **19.4** / 16.3 | 32.7 / 22.5 |
| jacket | 38.6 / 27.4 | 26.8 / 24.1 |
| trousers | 31.2 / 20.0 | **21.5** / 18.7 |
| boots | 42.3 / 28.5 | 28.1 / 21.0 |
| hip radio | 43.0 / 22.4 | 32.3 / 18.7 |
| coiled cable | 41.2 / 40.7 | 41.6 / 37.9 |
| tablet | 37.9 / 20.1 | 30.5 / 21.0 |

## Shortcomings, for the root's visual judgement

1. **Stiffer than v8.** The stance is upright and nearly symmetric. Only the relaxed viewer-left leg angles out, and there is no hip tilt or head tilt. v8's weight shift and cape give it more life.
2. **Face on bright paving.** Pale skin is close in value to the warm city stone (ring mean 19.4). The face reads because it is framed by the dark bob.
3. **Trousers in the dark annex** have the lowest contrast there (21.5). The grey cuffs, blue strap and ink carry the legs.
4. **Liang overlap.** The head-silhouette IoU for rows 8–35 is **0.603 against the Liang pilot** (0.474 against v8). Both are dark short hair at this scale. Separation relies on the blue tips, the earcup and the antenna, against Liang's bun and silver forelock. No nameless side-by-side confusion test was run.
5. **Flatter than v8.** Isolated single texels number 53, against v8's 145. Zhao is cleaner but has less micro-texture than v8.
6. **Wider than v8.** 46 px wide against v8's 43, because of the tablet and the radio. The jacket is boxy, as in the sheet.
7. **Antenna on dark floors.** It is a 1-px dark rod. On the dark annex mostly the brass tip and collar carry it (ring mean 34.9).
8. **Changed HUD text.** The city HUD shows other workstreams' renamed destination text, so these frames are not pixel-comparable to older v8 captures at the HUD.
9. **Not done:** north and side facings; 1920×1080 sampling; a GUI-saved `.pxo` round trip, which needs a person at the GUI; a four-character nameless lineup.

## Dependencies

- **Runtime:** real Python 3.12.14 (`C:\Users\hkzha\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe`), Pillow 12.3.0 and NumPy 2.3.5, run with `-I -B`.
- **Tools:** Pixelorama v1.2.3 at `work/tooling/pixelorama-1-2-3/…` and Godot 4.7.2 at `work/tooling/godot-4-7-2/…`. `work/` is gitignored.
- **Read-only inputs:** the v8 PNG, the tracked references above, and the city and annex scenes with their scripts, the `AppState` autoload and `SaveStore`. The scripts were only read, in a shared tree that carries other sessions' uncommitted hunks.
- **Shared module:** the build tool imports the shared v8-format utils by path, and its hash is pinned in the manifest.

## Reproduce (from the repository root)

```
python -I -B tools/rpg-2-star-ocean-the-second_zhao-ling_south-idle-static-pilot-build-and-check_unapproved-v01_20261018-052006-36f0253c.py build
python -I -B tools/rpg-2-star-ocean-the-second_zhao-ling_south-idle-static-pilot-build-and-check_unapproved-v01_20261018-052006-36f0253c.py check
work/tooling/godot-4-7-2/Godot_v4.7.2-stable_win64_console.exe --path game -s <absolute path>/tools/rpg-2-star-ocean-the-second_zhao-ling_south-idle-static-pilot-godot-capture-player-hidden_unapproved-v01r1_20261018-053437-4c1e9a07.gd
```

`build` reports `unchanged` when the files already match, and refuses to overwrite different bytes. To edit the art, change the grids, delete this run's own output files, and rebuild. The Godot run writes a fresh capture set with a new stamp.
