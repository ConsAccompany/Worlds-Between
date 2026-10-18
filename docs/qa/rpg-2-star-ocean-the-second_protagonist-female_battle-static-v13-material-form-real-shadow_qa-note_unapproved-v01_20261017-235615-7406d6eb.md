# Female battle static v13: material form and real draw-order evidence (QA note)

Status: **UNAPPROVED, NONRUNTIME, test-only static frame.** The runtime is unchanged and nothing is committed, staged or pushed. No ledger, Game Bible or counter changed (sprites 0/52). No animation work was done.

Auth: Claude Code, Opus 5.5. `claude auth status` reported claude.ai / firstParty / Max. No quota or auth block was hit.

Brief: `docs/coordination/…female-battle-static-v13-material-and-real-shadow-dispatch_unapproved-v01_20261017-235000-dfdc7f83.md`. It contains the Codex visual review of v12:
- the pack and bedroll read as two stacked boxes;
- a large black tail/roll bundle dominates the back;
- bright-floor foot separation is still weak;
- the review overlay drew a 23.4 shadow, but the game draws 18.

## What changed (bounded fork of the v12 author tool; v12 hash-locked and untouched)

Unchanged from v12: the 68×72 cell, pin (32, 68), crown row 7, sole row 67 (crown-to-sole 61 logical px), the bbox [15, 1, 60, 67], the blade (tip x60), and the palette (the same 31 keys, none added). These 13 layers are byte-identical to v12 (gated): head and face, coat torso, shirt wedge, scarf, collar, arm, glove, insignia, loose lock and hair band. The v8 storm-slate coat ramp is kept.

The other seven layers changed:

- **Bedroll → cylinder** (12×7, v12 13×7):
  - an elliptical end cap at the back end: a deep ring with lit turns around a dark core, closed by a seam that curves like the far rim;
  - a rounded front end;
  - one leather binding that bows toward the cap: column x23 on the top and bottom rows, x22 between;
  - the lit top, mid body and deep underside give the round shading.
- **Pack → slumped canvas sack** (137 texels, v12 161; visible 111, v12 131):
  - the top is narrow (x19), so the roll overhangs it by two texels;
  - the soft flap has a lit top plane, and its dark edge curves down to the middle over rows 29–32 (v12: one straight row);
  - the body bulges to x15 and narrows to a rounded, slumped bottom on row 37;
  - there are two transparent rows above the coat tail (v12: touching).
- **Back coat tail**:
  - it is shorter (to row 53, v12 56) and narrower (to x18, v12 x16);
  - it is cloth-valued: a mid-slate body with two deep fold lines, with deep slate only under the belt;
  - the lit split edge and the dark-leather hem are kept.
  - Visible deep slate in the tail drops from 98 to 24 texels.
- **Hip drape**: a short teal tab from the belt (rows 39–47). v12's drape ran down the whole tail edge as a stripe, which helped the "rolled bundle" read.
- **Ponytail**: the forked two-prong tip is now a single taper. The hook, strands and loose lock are unchanged.
- **Boots**: same outlines, re-keyed by the **real runtime contact shadow**: radius 18, y scale 0.28, centred on the pin.
  - The ellipse covers texel columns x24–39 on row 63, x19–44 on 64, x16–47 on 65, x15–48 on 66 and x14–49 on 67. Rows 57–62 stand on paving.
  - On paving, the boot is deep brown (d, l, L): the shafts, row 62, the far heel and the near toe.
  - Inside the shadow, the foot's top plane is lit (D) and the welt is warm grey (u).
  - Gated: 0 lit texels on paving (v12 had 43), and 97–100% lit texels on rows 64–66 inside the shadow.

Sprite totals: 1686 → 1621 opaque texels (−3.9%; IoU 0.953; 7 added, 72 removed). Changed composite texels: 315.

## Files (all untracked)

| file | sha256 |
|---|---|
| `game/assets/characters/combat-sideview-pilots/…static-native0p65_unapproved-v13_20261017-235615-1195f40e.png` (68×72 RGBA, binary alpha, Pixelorama 1.2.3 flat export of the .pxo) | `5b295aa1d19dcceb69b740e983eb2695d966701a4ead4ad8bbb72f13af6ebdb2` |
| `…editable-layers_unapproved-v13_20261017-235615-24e9a137.pxo` (pxo_version 7, 20 layers + hidden, locked guides) | `4e707496f3e27fb374600d944398e43d81209a3227dff27079d10715f955a6bc` |
| `…editable-layers_unapproved-v13_20261017-235615-3fffbeeb.ora` | `0fb1eda94deb9721446e543883779975bbb2983a516b0acb1017d83373088fb7` |
| `…manifest_unapproved-v13_20261017-235615-96c04b57.json` (`art_approved` and `runtime_integrated` both false) | `2e262894f802c0d61b1c1c93edf105db141f8bc82e63956d8525599900e65d75` |
| `tools/…native-0p65-author_unapproved-v13_20261017-235615-8f5d19fb.py` (fork of the v12 tool) | `b033417bdea28255a355565190beaaacb4b3efc8601b649f7e44acbe433a0e12` |
| `tools/…native-0p65-party-capture-probe_unapproved-v13_20261017-235615-5c3a1e08.gd` (v12 capture script + `probe` mode) | `796ffad4d3eacdb1b5f9b82c2d715980998fafa9ae30385a422b23a1e9d55ac1` |
| `tools/…battle-static-v12-vs-v13-capture-measure_unapproved-v13_20261017-235615-9b6e4d21.py` (read-only) | `4dbcd87b1308ee46bc79fed2f85457444bacc8aa6424ebd0be555bf502c1b7d9` |
| `outputs/…party-capture-archive-640-probe_unapproved-v13_20261017-235615-0cc9f010.png` (bright) | `5be556014d1e682a3a3f72adace8ddfc0d6a8e96a2354fea0130b00679e559e1` |
| `outputs/…party-capture-outskirts-640-probe_unapproved-v13_20261017-235615-66527b60.png` (dark) | `0eed9f0f9fec694a5dd5fccaf875d17cc3631c906174d7ce0ce34204559786d3` |
| `outputs/…party-capture-head-geometric-640-probe_unapproved-v13_20261017-235615-3129b639.png` (HEAD's own floor) | `40379ba7e27ea3b9fd9065e577b458ef24ff4f47c00eee9324caf5e40dcd5e4c` |

Each capture has a manifest next to it: archive `14a17904`, outskirts `91f3bcf9`, head-geometric `f521c753`. Their `capturePng` field records the temp path that the isolated run wrote to. The files in `outputs/` are byte copies, and the hashes match. The no-sprite frames stayed in `%TEMP%\wb-fv13\iso-cap` and are not deliverables.

## Evidence defect: resolved with real draw order and the real shadow

**Method: the `probe` mode of the v13 capture script.**
- The scene's own `battle_arena.gd` is extended **in memory** by a test-only subclass (`GDScript.new()`). No file is written and the scene is untouched.
- Its `_draw()` draws, in order:
  1. the floor: a pinned band PNG over `Rect2(0, 90, 640, 212)` with the working-tree tint, or HEAD's own geometric rects;
  2. contact shadows at radius 18, y scale 0.28, rgba(0.02, 0.03, 0.05, 0.42) for every living fighter and the enemy, using the working-tree `_draw_contact_shadows` constants;
  3. every fighter through the **real** `_draw_fighter`, in fighter order;
  4. the real `_draw_enemy`.
- The candidate reaches `_draw_fighter` as fighter 0 through the female idle frame-cache entries (v12 draw-order method, translated (−2, +5) onto `HERO_COMBAT_ANCHOR`).
- No yellow disc: `auto_mode` is set after the HUD update while paused.
- Companions draw over her. 0 candidate texels are hidden by a companion.

**Isolated tree** (`%TEMP%\fv13iso`; this throwaway copy can be deleted):
- It is `git archive` of HEAD `c20118d` `game/` (1251 files) plus exactly six enumerated v13 files: the PNG, .pxo, .ora, manifest, author tool and capture script.
- A read-only verifier checked, before and after the runs:
  - all 1251 HEAD files are present and byte-exact as git blobs;
  - the only extra files are the six enumerated ones;
  - after the Godot runs, the remaining extras are only Godot's import products (815 under `.godot/`, 52 `.import`, 34 `.uid`).
- Its `battle_arena.gd` is HEAD's (sha256 `e9737c40…`): no bands, no contact shadow, no `arena_override`. **The dirty working-tree `battle_arena.gd` is not used.** It was not edited or staged, and its sha256 `0c47a274…` is the same before and after.

**Self-check (all three isolated runs).** With no floor texture and radius 0, the probe frame is byte-identical to the scene's own `_draw()` frame (HEAD backdrop, fighters, enemy, HUD). So the probe re-draws HEAD in HEAD's own order.

**Explicit external inputs (not in the tree).** The two band PNGs are read read-only by absolute path from the main working tree, and sha256-pinned in each manifest:
- archive `c840e071…`
- outskirts `feea6297…`

They are untracked M8 arena candidates (1280×424 images, which the runtime scales into 640×212). This is the only thing the bright and dark captures take from outside HEAD. The **head-geometric** capture uses no external input at all.

**Cross-check against the real runtime.** In the main working tree, the v13 script's `draw-order` mode was run through the dirty band-capable `battle_arena.gd` for archive and outskirts. Temp only; this is a cross-check, not a deliverable.
- The isolated HEAD probe captures equal those runtime frames **byte-for-byte over the whole party region** (x 0–360, y 90–302): 0 px differ.
- The whole-frame difference (4058 px) is the enemy only:
  - HEAD draws its placeholder block where the working tree draws the sentry sprite;
  - the enemy's own shadow sits at `enemy_x` in the probe but is offset by the sentry's body centre in the working tree.
- Because of that enemy difference, the "candidate right edge → enemy" gap reads 81 px (HEAD placeholder), against 74 px with the sentry sprite.

**Every capture reports CAPTURE PASS (640×360, k = 1):**
- 1621/1621 sprite px;
- 0 off-palette;
- nearest-texel match 1.0;
- static scene (the re-grab is identical).

Positions:
- crown y 211, sole y 271 (61.0 logical px), bbox x283–328 / y205–271;
- Liang gap 5 px;
- 0 px opaque overlap with every companion.

**Measure tool.** The v13 PNG composited at (268, 204) over each no-sprite frame equals the Godot capture exactly, and only the 1621 sprite texels differ (`fidelity_pass` true). v12 is composited offline on the same backgrounds for the comparison. That is valid because both have zero companion overlap and the same pin. v12's own draw-order captures `409fdc2c` and `51e84eb1` also used the radius-18 shadow; v12's overlay captures (23.4 shadow) are superseded as evidence.

## Technical checks

- **`check` PASS 55/55, twice:** once with APPDATA redirected to an empty temp dir, once with the real APPDATA.
  - Another session's Pixelorama GUI (PID 37584) stayed open and was left alone. The real `pixelorama` dir (heartbeat excluded) was unchanged.
  - Gates:
    - static: binary alpha, palette, crown/sole rows, bbox, pin row clear, both soles on row 67;
    - manifest hashes and UNAPPROVED flags;
    - byte-identical rebuild of the .pxo/.ora;
    - .pxo and .ora stacks recompose to the PNG, and the .ora merged image equals the PNG;
    - layer/palette structure versus v12 as declared;
    - the v12 lock, before and after;
    - 27 identity, form and runtime-shadow boot gates, listed in the manifest's `pose_gates`.
- **Pixelorama 1.2.3 headless round-trip:**
  - .pxo and .ora flat exports equal the tool render;
  - split export is 20/20 layers for both formats, and the guides are not exported;
  - the delivered PNG is the .pxo flat export.
- **In the isolated tree:** `check --no-pixelorama` passes 53/53. That is the same gate set minus the two Pixelorama gates, because Pixelorama is not part of the tree.

## Measurements: v12 vs v13 on identical real draw-order backgrounds

Each cell is mean |ΔL| (Rec.709) of sprite texels against the background they cover, outline excluded, followed by the share of texels with |ΔL| < 20. Lower share is better.

| capture (bg L) | region | v12 | v13 |
|---|---|---|---|
| archive, bright | boots rows 57–67 | 37.2 / 21.0% | **45.6 / 2.2%** |
| | boot contact rows 62–66 | 27.7 / 32.2% | **40.6 / 3.3%** |
| | boot texels on paving (bg 108) | 40.1 / 27.4% | **53.3 / 0.0%** |
| | boot texels in shadow (bg 67) | 32.6 / 11.0% | 33.6 / 5.5% |
| | lower body 38–67 | 41.3 / 21.3% | 40.4 / 19.7% |
| outskirts, dark | boots rows 57–67 | 36.9 / 22.6% | 36.4 / 24.7% |
| | boot texels on paving (bg 76) | 27.6 / 32.7% | **25.4 / 39.8% (worse)** |
| | boot texels in shadow (bg 47) | 51.3 / 6.8% | 53.4 / 1.4% |
| | lower body 38–67 | 35.7 / 21.8% | **31.1 / 31.3% (worse)** |
| head-geometric (HEAD floor) | boots rows 57–67 (bg 72: HEAD's floor rect starts at screen y 268, so boot rows 57–63 stand on its dark backdrop) | 23.8 / 55.4% | **22.1 / 72.6% (worse)** |
| | lower body 38–67 | 30.8 / 35.6% | **28.0 / 51.4% (worse)** |

Head and torso are within ±3 points everywhere.

**Back region** (x ≤ 31, rows 20–56: pack, roll, tail):
- texels darker than L 45: 356 → 260 including the outline (−27%), and 220 → 142 excluding it (−35%);
- mean L excluding the outline: 60.3 → 63.9;
- visible deep slate: 176 → 104 (−41%). The coat torso back and the far trouser stay deep slate on purpose, so I gated the tail (98 → 24) and not this region figure. My first draft gate (region ≤ 50%) failed, and I did not keep it.

Width without the sword arm: coat-skirt band 31 → 28, lower body 37 → 35, boots 36 → 35. Sole-row stance is unchanged: x19–30 / x38–50.

## Visible trade-offs and limits (candid)

- **The bright floor is fixed; the dark floor is slightly worse.** Deep boots over the archive paving (L ≈ 108) separate strongly. Over the outskirts paving (L ≈ 76) the same deep brown is only about 25 L away, so more boot texels fall under 20. No single boot value separates from both pavings; the black outline still bounds every boot. In the shadow, both floors improved.
- **The de-blackened tail costs contrast on the dark floor.** The mid-slate tail (L ≈ 68) sits close to the outskirts wall and paving (L ≈ 80–88). Lower-body |ΔL| < 20 rises from 21.8% to 31.3% there, while archive is flat. This is the direct price of removing the black bundle.
- **HEAD's geometric backdrop is unfavourable for the new boots.** Its floor rect starts at screen y 268, so the boot shafts stand on the dark purple wall (L ≈ 61). The deep boot shafts lose contrast there (boots 55% → 73% under 20). That backdrop is a placeholder, not one of the reviewed floors.
- **She is about 4% lighter in mass than v12.** The shorter tail and the smaller pack and roll reduce the silhouette (1686 → 1621 texels; coat-skirt band 31 → 28 wide). Codex liked v12's fuller coat, and part of that read is traded away. She is still the narrowest party member. I did not widen her to match the big-headed companion prototypes.
- **The roll and the drape at 1×.**
  - The cylinder end cap is a 3×3 ring with a dark core. At 1× it reads as a rounded roll end, not as a detailed spiral.
  - The pack and roll still form one stacked unit on her back, but now as a round roll over a sack, not two rectangles.
  - The teal drape tab next to the tail can read as a small teal flare at the hip at 1×.
- **Micro details are unchanged:** the face (2×2 eye), the 4-texel insignia and the glove.
- **External band inputs.** The bright and dark captures need the two untracked band PNGs, read by pinned absolute path. They are explicit inputs, but they are not part of HEAD. Only the head-geometric capture is HEAD plus v13 files alone.

## Next

Codex/creator review of the three 640×360 captures at 1×. Compare against v12's draw-order captures `…archive-640-draw-order…409fdc2c.png` and `…outskirts-640-draw-order…51e84eb1.png`, which use the same radius-18 shadow and fighter order. No motion, runtime swap, commit or counter change follows from this note.
