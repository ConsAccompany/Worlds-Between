# Female protagonist battle static v10: ready-stance pass, QA note (v09 vs v10)

**Status:** UNAPPROVED, NONRUNTIME, test-only static pilot. It waits for Codex's visual review; there is no approval request yet.
- One frame, no animation. Motion stays blocked until a static frame is accepted.
- No other character, runtime battle logic, scene, or node display scale was touched. `game/scripts/battle_arena.gd` (dirty, another workstream's) was only read: sha256 `be8859a8…` before and after.
- Game Bible, meter/progress state, trackers and the sprite acceptance count (still **0/52**) are unchanged. Nothing was staged, committed or pushed; every v10 file is untracked.
- v09 is hash-locked and unchanged (PNG, .pxo, .ora and manifest are checked before and after every build/check).
- The creator has approved only the 0.65 battle display proportion. v10 keeps it exactly. Neither v09 nor v10 is creator-approved.
- Auth for this session: signed-in Claude Max through claude.ai / firstParty, `ANTHROPIC_API_KEY` absent. No API billing or paid fallback was used.

## Input

The trigger was a Codex inspection of the real v09 1280×720 and 640×360 ruins party captures (2026-10-16). Codex found that the heroine at slot four reads and the approved display proportion works, but:
- the torso is upright and stiff;
- the teal pack coil looks like a small knob;
- the hip drape dominates the coat back and partly reads as a skirt;
- the boots and far leg merge with the dark floor at 640.

Other inputs:
- v09 asset, author tool (`…author_unapproved-v09_20261016-135202-43cf7e01.py`) and QA note (`…f5f2ad17.md`, including its re-verification section).
- Approved exploration baseline: south v8 static (`…south-idle-selout-v8-cloth-leather-candidate_m8-v08_20261015-021600-157a5ea0.png`). It is the source of the coat/trouser ramps, the teal drape and roll, and the pale boot laces.
- The global `AGENTS.md` naming and separate-image rules.

## Files (all new, all untracked)

| Role | Path | sha256 (bytes, first 16) |
|---|---|---|
| Pilot PNG (Pixelorama 1.2.3 flat export of the .pxo) | `game/assets/characters/combat-sideview-pilots/rpg-2-star-ocean-the-second_protagonist-female_sideview-idle-right-static-native0p65_unapproved-v10_20261016-162819-1c891d6d.png` | `dd7dbc7ac7ffb818` |
| Editable Pixelorama project, 18 layers + hidden locked guides | `…/combat-sideview-pilots/…_editable-layers_unapproved-v10_20261016-162819-73e8d4a2.pxo` | `8aa3a6ea58235f14` |
| Same layers as OpenRaster | `…/combat-sideview-pilots/…_editable-layers_unapproved-v10_20261016-162819-d0483645.ora` | `fd0a685b5ceec29a` |
| Manifest (silhouette report vs v09, pose report + gates) | `…/combat-sideview-pilots/…_manifest_unapproved-v10_20261016-162819-0fb8a88b.json` | `439af456926463ea` |
| Author tool (preview / build / check) | `tools/rpg-2-star-ocean-the-second_protagonist-female_sideview-battle-idle-right-native-0p65-author_unapproved-v10_20261016-162819-91df8059.py` | — |
| Capture script (copy of v09 any-size; only HEAD_X 24-47, save path and labels differ) | `tools/…party-capture-any-size_unapproved-v10_20261016-162819-3a7c52e1.gd` | — |
| Read-only v09-vs-v10 measurement + scope test | `tools/rpg-2-star-ocean-the-second_protagonist-female_sideview-battle-static-v09-vs-v10-region-measure_unapproved-v10_20261016-162819-5e0c7a14.py` | — |
| Godot 1280×720 capture, ruins (+ `…ruins-manifest_…-06bde83a.json`) | `outputs/rpg-2-star-ocean-the-second_protagonist-female_sideview-idle-right-static-native0p65_party-capture-ruins_unapproved-v10_20261016-162819-8dc84c1e.png` | `fd68319c81671e0d` |
| Godot 1280×720 capture, outskirts (+ `…outskirts-manifest_…-08906318.json`) | `outputs/…_party-capture-outskirts_unapproved-v10_20261016-162819-9aeff8e6.png` | `2b6a54e64cba17c6` |
| Godot 640×360 capture, ruins (+ `…ruins-640-manifest_…-2556a3f4.json`) | `outputs/…_party-capture-ruins-640_unapproved-v10_20261016-162819-de44e59a.png` | `50687caf05283c4f` |
| Godot 640×360 capture, outskirts (+ `…outskirts-640-manifest_…-09e4a6ed.json`) | `outputs/…_party-capture-outskirts-640_unapproved-v10_20261016-162819-7829fd0b.png` | `c6784648c7a7a21d` |

Each capture is its own file. No comparison sheets were saved in the repo; inspection crops stayed in `%TEMP%\wb-v10`. A first v10 build and its four captures were deleted and rebuilt under the same deterministic names after the leg-value fix below. They were never reviewed or tracked.

## What changed (hand-typed ASCII layers, binary alpha, same 30-key palette, no new colour)

Unchanged from v09: the 68×72 cell, pin (32, 68), sole row 67, crown row 7 (61 logical px crown-to-sole), leftmost texel x15 (gap to Liang Xu unchanged) and the 18 layer names. One layer moved in the stack: `hip-drape` now sits under `coat`/`coat-skirt`. `coat-skirt` is byte-identical to v09; every other layer changed.

1. **Ready stance (stiff torso).** The hips stay where they were. The coat back edge steps one texel toward the enemy about every four rows (x24 at the belt → x28 at the shoulder; lean 4 texels, v09 0). The head, collar, scarf and ponytail moved 4 texels forward. The sword arm reaches forward: the upper arm angles from the shoulder, the elbow sits in front of the chest, the fist sits 6 texels further forward (x43-49), and the same 45° blade comes with it (rightmost texel x60 vs x54). The sword light core is still 1 component of 19 texels, and the hand/hilt is still 4 rows clear of the belt. The legs keep v09's shapes: braced far leg, bent near knee (knee pad moved 1 texel forward).
2. **Coil → bedroll.** It is now a 10×7 teal roll lying on the pack's top edge (v09: a 7×7 end-on coil). It has a lit top, a shadowed underside, a rear end cap showing the rolled layers, and one leather strap. It has ≥2 transparent columns to the coat on every roll row above the pack (5/4/3/3/2/3), is 7 texels from the scarf teal and 13 texels from the drape, and touches no coat/scarf/collar texel. The pack moved 2 texels forward with the back.
3. **Hip drape.** It now hangs behind the coat skirt. Only a one-texel teal rim along the slate coat tail shows, plus a narrow shadowed tail with a split end below the hem (visible drape 107 → 48 texels; visible coat skirt 120 → 210). It stays clear of the far leg's back edge.
4. **Legs and boots against both floors.** The values were picked against the measured floors: paving L ≈ 80-95 above row 62, contact shadow L ≈ 45-58 on rows 62-67. No mid value is left over the paving:
   - the far trouser is all v8 trouser deep C (v09's spruce T front edge sat within 20 L of the paving);
   - the near shin drops its lit spruce t edge;
   - both boot shafts are dark leather L carrying a pale-beige strap (P near, p far) under a lit turned-down cuff B;
   - the feet in the shadow stay mid leather b with a lit B instep.

   A first build had mid-leather b shafts. The measure showed that this made the boots worse over the paving, so it was reverted to dark shafts before the final build.

## Technical checks (all run in this session)

- **`build`:** Pixelorama 1.2.3 headless with APPDATA redirected per run. Flat and split-layer exports of both the .pxo and the .ora matched (18/18 visible layers, guides not exported). The PNG is Pixelorama's flat export and equals the tool render.
- **`check`: PASS 35/35**. Runs: working tree with redirected APPDATA; working tree with real APPDATA (on the second attempt); fresh `--shared` clones of HEAD `d69871e` with `core.autocrlf=true` and `false` (only the v10 tool and 4 v10 assets copied in; v09 locks from Git; clones deleted).
  - Two real-APPDATA runs failed only `real_appdata_pixelorama_untouched_except_heartbeat`. Another session's open Pixelorama GUI autosaved into `%APPDATA%\pixelorama\backups` during the run. This is the known flake; our headless runs always use a redirected APPDATA.
  - Gates include palette and layer names the same as v09, crown row 7 / sole row 67, leftmost ≥ x15, Pixelorama round-trips, .pxo/.ora layer-stack recomposition and v09 unchanged.
  - Pose gates: torso lean ≥ 3; roll larger than v09's 7×7 and ≥ 2 transparent columns to the coat; roll ≥ 3 texels from scarf and drape; drape behind coat skirt; visible coat skirt ≥ 2× visible drape; boot contact rows mostly L ≥ 85 with a B cuff and a P/p strap.
  - The manifest silhouette/pose reports equal a fresh computation.
- **Godot 4.7.2 windowed captures** used the new any-size script with the real `battle_arena.tscn`, `arena_override` `ruins` / `outskirts`, the sentry, the party at x 300/252/204/150, and no yellow disc. All four reported `CAPTURE PASS arenaMode=arena-override-band`:
  - **1280×720:** 5804/5804 sprite pixels exact, 0 off-palette, crown y 422, sole y 543, 61 logical px, gap to Liang Xu 10 screen px, 0 overlap.
  - **640×360:** 1451/1451 exact, crown y 211, sole y 271, 61 px, gap 5 px, 0 overlap. These are real 640×360 renders, not downscales.
  - **Parity:** the committed v07r1 helper (same as HEAD) reproduces both v10 1280 captures and their no-sprite frames byte for byte. Two separate capture runs gave byte-identical no-sprite frames.
- **Nothing changed outside the target sprite** (measure tool, PASS 20/20):
  - For all four arena × size pairs, the v09 and v10 captures differ in **0 pixels outside the union of the two sprites' footprints**. Companions, enemy, HUD, arena band and contact shadow are identical. This part also passes in a clean clone without any temp files.
  - Pasting the v10 PNG over the no-sprite frame reproduces each v10 capture exactly; pasting the v09 PNG over the v10 run's no-sprite frame reproduces each v09 capture exactly.
  - The area v09 covered and v10 left is pure background, and the v10 no-sprite frames are byte-identical to the v09 run's.
- **Working tree:** `git status` diff before/after shows only the 14 v10 files plus this note. There are no `.import`/`.uid` files. Other lines that changed belong to concurrent sessions.

## Silhouette and structure vs v09

| Measure (texel space) | v09 | v10 |
|---|---|---|
| Opaque texels | 1374 | 1451 |
| Silhouette IoU with v09 | — | 0.699 (289 added, 212 removed) |
| Torso lean (coat back edge row 24 − row 37) | 0 | 4 |
| Head x span / fist bbox | 25-42 / x37-43 | 29-46 / x43-49 |
| Rightmost texel (blade tip) | 54 | 60 |
| Roll size / transparent columns to coat (rows 22-27) | 7×7 / 5,4,2,2,2,3 | 10×7 / 5,4,3,3,2,3 |
| Visible drape / visible coat skirt texels | 107 / 120 | 48 / 210 |
| Far trouser keys (K/C/T) | 15/13/8 | 13/21/0 |
| Boot light anchors rows 58-67 (B, P/p) far / near | 8, 0 / 9, 0 | 9, 2 / 12, 2 |
| Isolated single texels | 90 | 77 |

## Value separation, real captures (mean |ΔL| Rec.709 / % of pixels under 20), v09 → v10

| Region | ruins 1280 | outskirts 1280 | ruins 640 | outskirts 640 |
|---|---|---|---|---|
| Far leg trouser (visible) | 41.0/17.4 → **45.1/0.0** | 42.6/21.5 → **47.0/2.9** | 40.5/16.7 → **44.8/0.0** | 42.1/22.2 → **46.0/5.9** |
| Far boot | 40.5/4.6 → 42.1/3.9 | 37.8/18.6 → 39.9/17.2 | 40.7/5.5 → 42.4/4.6 | 37.8/18.3 → 39.9/16.5 |
| Near boot | 41.6/20.1 → 44.5/18.6 | 40.3/20.4 → 43.7/16.8 | 42.1/21.7 → 45.3/17.0 | 40.9/19.6 → 44.1/16.0 |
| Boots, contact-shadow rows 62-65 | 40.7/6.7 → 40.9/8.6 | 43.1/11.8 → 43.2/12.1 | 40.5/7.5 → 41.3/7.5 | 43.6/11.8 → 43.5/11.8 |
| Near leg (visible) | 41.0/23.7 → 42.8/20.6 | 39.9/23.7 → 41.6/22.4 | 41.3/25.2 → 43.3/19.6 | 40.3/23.2 → 41.8/22.1 |
| Coat skirt (visible) | 38.3/22.5 → 41.3/17.4 | 36.9/13.1 → 42.3/9.8 | 39.2/21.7 → 42.1/17.1 | 36.3/15.0 → 41.9/11.0 |
| Hip drape (visible) | 55.2/4.9 → 53.1/10.9 | 54.0/5.1 → 51.1/12.5 | 54.1/5.6 → 54.1/8.3 | 54.4/6.5 → 51.1/12.5 |
| Bedroll | 53.0/8.8 → 49.9/9.6 | 51.9/10.1 → 50.3/11.7 | 52.7/8.1 → 49.6/10.0 | 52.6/8.1 → 50.1/10.0 |
| Jacket (torso + belt) | 45.2/5.4 → 41.8/7.2 | 47.5/7.6 → 46.6/7.6 | 45.1/5.9 → 41.9/7.0 | 46.7/5.9 → 46.1/7.0 |
| Whole sprite | 49.3/14.7 → 48.8/13.7 | 49.2/14.6 → 49.3/14.0 | 49.6/14.6 → 48.9/13.4 | 49.2/14.6 → 49.2/14.1 |

## Visual inspection at gameplay size (Claude's reading of the real captures, not a Codex audit)

**Better than v09:**
- **Pose:** at 1280×720 and 640×360 she now leans into the enemy with the fist and blade carried forward. She reads as a ready stance rather than standing upright. The blade sits clear in front of the face.
- **Back gear:** the roll reads as a strapped teal bundle on the brown pack, bigger than v09's knob, with floor visible between it and the coat.
- **Coat back:** the slate coat tail is the main back shape again. The teal is a thin rim plus a small tail, not a skirt panel.
- **Legs:** the far trouser now reads as one dark leg over both pavings (pixels under 20 L: 17-22 % → 0-6 %). Each boot shows a lit cuff and a pale strap above the brown foot, and these stay visible at 640.

**Remaining defects and costs (open):**
- The lean comes from the upper body only. The legs keep v09's shapes, so the stance width and knee bend are unchanged. The weight shift reads at 1280 but is modest at 640.
- The sword arm, coat back and sleeve are one slate mass at 1×; the forearm is hard to separate from the torso. The fist and blade read.
- The roll at 640 is about 10×7 px: a teal block with a barely visible strap. It reads as "gear", not certainly as a bedroll.
- The drape is now so small that v8's teal hip cloth (an identity cue) is weak. A reviewer may want more of it back, outside the coat-tail silhouette.
- The boots on the contact-shadow rows are unchanged in value (|ΔL| ≈ 41-43). The dark sole band still merges with the shadow, so the boot bottoms read slightly short at 640.
- The near shin lost its lit edge and is flatter.
- Unchanged from v09: the neutral face, the companions' simpler finish, and the capture overlay drawing above companions (inherited runtime draw-order caveat).

## Verdict

Claude judges v10 a clearer improvement over v09 at game scale than v09 was over v08, mainly from the lean, the forward guard, and the coat back no longer being covered. This is Claude's visual judgement only. It is not a Codex audit and not creator acceptance. v09 is untouched, v10 is UNAPPROVED/NONRUNTIME, sprites stay 0/52, and the meter is unchanged. Codex reviews the captures next, and an approval request comes only after that.
