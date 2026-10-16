# Female protagonist battle static v09: three-issue pass, QA note (v08 vs v09)

**Status:** UNAPPROVED, NONRUNTIME, test-only static pilot.
- One frame, no animation, no other characters touched.
- Not runtime-integrated: `game/scripts/battle_arena.gd` (dirty, another workstream's) and `game/scenes` were only read. `battle_arena.gd` sha256 `be8859a8…a592acae` before and after.
- Game Bible, meter/progress state, trackers and acceptance count (complete sprites still **0/52**) unchanged. Nothing staged, committed or pushed. Every v09 file is untracked.
- v08 is hash-locked and unchanged (PNG, .pxo, .ora, manifest checked before and after every build/check).

The creator approved only the 0.65 battle display proportion. v09 keeps it exactly. Neither v08 nor v09 is creator-approved.

## Input

- Codex v08 visual audit: `docs/qa/rpg-2-star-ocean-the-second_protagonist-female_battle-static-v08-codex-visual-audit_unapproved-v01_20261016-145125-5e1b7d6c.md`. It names three remaining issues: the teal roll nearly joins the scarf and reads as a shoulder block; the dark far leg and boots blend into both floors; the narrow hip drape lacks the approved exploration v8's back-fabric character.
- v08 asset, author tool (`…author_unapproved-v08_20261016-095054-326522f8.py`), QA note (`…68ec4f17.md`).
- Approved exploration baseline: south v8 static `game/assets/characters/pixelorama-pilots/…south-idle-selout-v8-cloth-leather-candidate_m8-v08_20261015-021600-157a5ea0.png`. Read from it: v8 shades its spruce trousers with the slate deep `#222839` (C); its boots are mid browns; its drape is a wide teal cloth hanging from the hip with a ragged hem.
- Global `AGENTS.md` naming and separate-image rules.

## Files (all new, all untracked)

| Role | Path | sha256 (bytes) |
|---|---|---|
| Pilot PNG (Pixelorama 1.2.3 flat export of the .pxo) | `game/assets/characters/combat-sideview-pilots/rpg-2-star-ocean-the-second_protagonist-female_sideview-idle-right-static-native0p65_unapproved-v09_20261016-135202-07e7f74a.png` | `7e9d7ef2…3a55dfed` |
| Editable Pixelorama project, 18 layers + hidden locked guides | `…/combat-sideview-pilots/…_editable-layers_unapproved-v09_20261016-135202-34faf685.pxo` | `ef5adb2a…54c59fb4` |
| Same layers as OpenRaster | `…/combat-sideview-pilots/…_editable-layers_unapproved-v09_20261016-135202-51c824c2.ora` | `1940e7cb…42cc20eb` |
| Manifest (includes intended regions + scope report vs v08) | `…/combat-sideview-pilots/…_manifest_unapproved-v09_20261016-135202-0bea0fc8.json` | `2505eead…54fe63e88` |
| Author tool (preview / build / check) | `tools/rpg-2-star-ocean-the-second_protagonist-female_sideview-battle-idle-right-native-0p65-author_unapproved-v09_20261016-135202-43cf7e01.py` | — |
| Capture script for any 640×360 multiple (used for 640×360) | `tools/rpg-2-star-ocean-the-second_protagonist-female_sideview-battle-idle-right-native-0p65-party-capture-any-size_unapproved-v09_20261016-135202-fb7e61ce.gd` | — |
| Read-only v08-vs-v09 measurement | `tools/rpg-2-star-ocean-the-second_protagonist-female_sideview-battle-static-v08-vs-v09-region-measure_unapproved-v09_20261016-135202-dcd62b79.py` | — |
| Godot 1280×720 capture, ruins (+ manifest `…ruins-manifest_…-34b4c767.json`) | `outputs/rpg-2-star-ocean-the-second_protagonist-female_sideview-idle-right-static-native0p65_party-capture-ruins_unapproved-v09_20261016-135202-e6fe04c7.png` | `e0808bee…` |
| Godot 1280×720 capture, outskirts (+ `…outskirts-manifest_…-f9bc2dea.json`) | `outputs/…_party-capture-outskirts_unapproved-v09_20261016-135202-6daa9a52.png` | `e980e4f1…` |
| Godot 640×360 capture, ruins (+ `…ruins-640-manifest_…-37c1f039.json`) | `outputs/…_party-capture-ruins-640_unapproved-v09_20261016-135202-c26ecd6c.png` | `e72addff…` |
| Godot 640×360 capture, outskirts (+ `…outskirts-640-manifest_…-31cc4115.json`) | `outputs/…_party-capture-outskirts-640_unapproved-v09_20261016-135202-0f032fbf.png` | `8fbbf6f9…` |

Each capture is its own file. No comparison sheets, crops or x-scaled images were saved in the repo (inspection crops stayed in `%TEMP%`).

## What changed (hand-typed ASCII layers, binary alpha, no new colour)

Same 68×72 cell, pin (32, 68), sole row 67, crown row 7 (61 logical px crown-to-sole), leftmost texel x15, the same 18 layers in the same order and the same 30-key palette as v08. 14 layers are byte-identical to v08's .ora layers: pack, ponytail, coat, coat-skirt, shirt-lapel, near-arm, sword-blade, sword-guard, fist, head, hair-tie, collar, scarf-neck, collar-front. So v08's fist-above-belt and one-line sword fixes are kept exactly (sword light core still 1 component of 19 texels; hand/hilt still 4 rows clear of the belt).

1. **Far leg and boots (`far-leg`, and `near-leg` rows 62-65 only).** Values were picked against the floor measured behind each row: paving L ≈ 70-100 down to row 61, contact shadow L ≈ 45-58 on rows 62-67. No rim or outline was added; the K outline is unchanged.
   - Far trouser: v8 trouser deep C (L 40) with one spruce T front edge, instead of v08's T body + t edge (L 65 / 92, both within ~20 L of the paving).
   - Both boots: the foot in the contact shadow is mid leather b (L 92) with a lit B instep edge, instead of the shadow-valued l (L 59). The shafts above the shadow stay dark L/l. The far boot's cuff back end is l instead of the floor-valued b.
2. **Roll vs scarf (`bedroll`).** The roll is drawn end-on as a 7×7 coil (it lies across the back, as v8 carries it): lit outer ring top-right, one dark Q spiral turn round a lit core, shadowed base, sitting on the back half of the pack. It ends at x21, so columns x22-23 are fully transparent between it and the coat/scarf on roll rows 22-27 (the rows the gate checks). On row 28 the coil's shadowed base sits on the pack, and the pack is continuous with the coat on that row. No roll texel is 4-adjacent to coat/scarf/collar. *(Corrected 2026-10-16 by independent re-verification: this note first said "on every roll row".)*
3. **Hip drape (`hip-drape`).** v8's back-hip fabric is wider (5-7 interior texels, v08: 3-4) and longer (rows 40-54, v08: 40-49). It flares back past the coat tail to x15. It has a plain g body with a lit G front edge; from row 45 one diagonal Q fold runs parallel to the front edge and opens into the split between two hem tails (v8's ragged hem); the flared underside is q/Q. Its front edge stays left of the far leg's back edge on every row.

## Technical checks (all run in this session)

- **`build`:** Pixelorama 1.2.3 headless with APPDATA redirected per run. Flat and split-layer exports of both .pxo and .ora matched (18/18 visible layers, guides not exported). The PNG is Pixelorama's flat export and equals the tool render. Real `%APPDATA%\pixelorama` untouched (another session's GUI, PID 50828, was open throughout).
- **`check`: PASS 29/29** in the working tree. New gates over v08's 19:
  - `palette_same_as_v08`, `layer_order_same_as_v08`;
  - `changes_only_in_intended_regions_and_layers`: 196 composite texels differ from v08, **0 outside** the four declared boxes (far leg + boot 129, near boot instep 25, roll 33, drape 93; each box changed); per layer, only far-leg (96), near-leg (25), bedroll (36) and hip-drape (87) changed, each only inside its own box; every other layer has 0 changed texels;
  - `pxo_layer_stack_recomposes_png`, `ora_layer_stack_recomposes_png`, `ora_mergedimage_equals_png`, `pxo_guides_hidden_locked`;
  - `roll_scarf_gap_ge_2_transparent_columns` (per row 5/4/2/2/2/3), `leftmost_texel_x15_same_as_v08`, `manifest_scope_matches_fresh_scope`.
  - A negative test (in memory, nothing written) confirmed the scope gate fails for one changed fist texel, one far-leg texel outside its box, and a one-unit palette edit.
- **Clean clones:** `check` PASS 29/29 in fresh `--shared` clones of HEAD `462b17d` with `core.autocrlf=true` and `false` (only the v09 tool and four v09 asset files copied in; v08 locks from Git; clones deleted afterwards).
- **Godot 4.7.2 windowed captures, 1280×720**, with the committed v07r1 helper unchanged (file sha256 `2498b627…`, identical to HEAD; git blob `f813dcfd…`; *corrected: this note first called the sha256 a "blob"*): real `battle_arena.tscn`, `arena_override` `ruins` / `outskirts`, sentry, party at x 300/252/204/150, yellow disc not drawn. Both `CAPTURE PASS arenaMode=arena-override-band`: crown y 422, sole y 543, 61 logical px; 5496/5496 sprite pixels match nearest-neighbour texels; 0 off-palette; all texels 2×2; gap to Liang Xu 10 screen px, 0 overlap (same as v08).
- **Godot 640×360 captures** (`--resolution 640x360`, new any-size script): both PASS, 1 screen px per texel, 1374/1374 exact, crown y 211, sole y 271, 61 px, gap to Liang Xu 5 px, 0 overlap. The same script at 1280×720 reproduces the v07r1 ruins capture byte-for-byte. The 640×360 frames are a real render, not a downscale (the arena art renders differently).
- **Background identity:** this run's no-sprite frames are byte-identical to the v07/v08 runs' no-sprite frames. An offline composite of the PNG over them reproduces every capture byte-for-byte. 0 pixels differ outside the sprite for v08 and v09 in both arenas.
- **Working tree:** the `git status` diff before/after shows only the 15 v09 files (4 assets, 8 outputs, 3 tools) plus this note. No `.uid`, `.import` or other files. Lines that disappeared were files another session committed meanwhile in `462b17d`.

## Measurements, real 1280×720 captures (mean |ΔL| Rec.709 / % of pixels under 20)

| Region | ruins v08 | ruins v09 | outskirts v08 | outskirts v09 |
|---|---|---|---|---|
| Far trouser leg (visible) | 33.1 / 34.7 % | **41.0 / 17.4 %** | 33.9 / 52.8 % | **42.6 / 21.5 %** |
| Far boot | 28.8 / 36.0 % | **40.5 / 4.6 %** | 25.9 / 49.8 % | **37.8 / 18.6 %** |
| Near boot | 33.5 / 34.5 % | 41.6 / 20.1 % | 31.0 / 41.6 % | 40.3 / 20.4 % |
| Both boots, contact-shadow rows 62-65 | 19.6 / 55.9 % | **40.7 / 6.7 %** | 20.3 / 68.3 % | **43.1 / 11.8 %** |
| Hip drape | 52.8 / 13.7 % (53 tx) | 55.2 / 4.9 % (107 tx) | 51.2 / 17.0 % | 54.0 / 5.1 % |
| Coat skirt (visible) | 40.9 / 19.3 % (157 tx) | 38.3 / 22.5 % (120 tx) | 41.1 / 11.1 % | 36.9 / 13.1 % |
| Hip band, all layers, rows 38-54 | 43.2 / 19.5 % | 45.2 / 16.0 % | 43.5 / 15.3 % | 44.8 / 11.3 % |
| Bedroll | 53.7 / 13.6 % | 53.0 / 8.8 % | 54.7 / 13.0 % | 51.9 / 10.1 % |
| Sword, jacket | unchanged | unchanged | unchanged | unchanged |
| Whole sprite | 47.3 / 19.4 % | 49.3 / 14.7 % | 47.3 / 20.0 % | 49.2 / 14.6 % |

| Structure (texel space) | v08 | v09 |
|---|---|---|
| Roll bbox / rows | 9×6 capsule / 23-28 | 7×7 coil / 22-28 |
| Transparent columns right of the roll, rows 24-27 | 0 (touches coat) | 2 / 2 / 2 / 3 |
| Roll texels touching coat/scarf/collar | 4 | 0 |
| Roll teal ↔ scarf teal gap | 4 | 6 |
| Drape texels / max row width / rows | 53 / 6 / 40-49 | 107 / 9 / 40-54 |
| Far-leg / near-leg visible texels (stance not covered) | 145 / 155 | 145 / 155 |
| Drape texels 4-adjacent to the far leg | 0 | 3 (outline beside outline; none covered) |
| Isolated single texels | 100 | 90 |

## Visual comparison (real captures, 1× and 640×360)

**Better in v09 (Claude's judgement):**
- **Roll:** a small teal coil on the pack with floor visible between it and the scarf. It no longer joins the scarf into one shoulder band.
- **Far leg and boots:** measurably better separated (contact-shadow boot rows |ΔL| ≈ 20 → 41-43). The far leg reads darker against both floors, and the feet stay brown inside the contact shadow. No glow line. At 1x and 640×360 the visible difference from v08 is small, because v08's feet already showed some mid-brown. *(Softened 2026-10-16.)*
- **Hip drape:** a clear teal cloth panel at the back hip with a fold and a split hem, closer to v8's drape; the stance below it is unchanged.
- Head, ponytail, scarf, coat, raised sword and fist read as in v08.

**Costs and open points (not hidden):**
- The roll is small (7×7 texels; 14 px at 1280×720, 7 px at 640×360). It reads as a coil/knot rather than a full bedroll; a larger coil would close the gap or move the leftmost texel.
- The wider drape now covers most of the coat's deep back tail (visible skirt 157 → 120 texels; skirt ΔL slightly lower). The back of the coat reads teal; a reviewer may find the drape too dominant or skirt-like.
- The far trouser is mostly slate deep C (v8's own trouser shade); spruce shows only on its front edge.
- Both boots are now two-tone (dark shaft, mid-brown foot), which some may read as gaiters over shoes.
- At 640×360 every detail is 1 px; the changes still register as teal accents and visible boots, but the coil's spiral does not.
- Unchanged: upright torso, neutral face, the companions' simpler finish, and the capture overlay draws above companions (runtime draw order caveat inherited from v07r1).

## Verdict

At game scale, Claude judges v09 better than v08 on the three issues the Codex v08 audit names, with v08's sword and fist/belt fixes kept byte-identical. This is Claude's visual judgement, not a Codex audit and not creator acceptance. Neither version is approved. v08 is untouched. Motion stays blocked until a static frame is accepted.

**Scale caveat (added 2026-10-16):** Codex later inspected the real 1280×720 ruins and 640×360 outskirts captures against v08. It agrees that the boots read more clearly, the coil is visibly separate and the drape is stronger, but finds the changes subtle at gameplay scale. The improvement is incremental. It is not evidence of sprite quality acceptance.

## Independent re-verification (2026-10-16, closeout `closeout-20261016-180831-3e5ab356`)

A separate session re-ran these checks. No v09 art, tool, runtime or Game Bible file was written.
- `check` in the working tree: **PASS 29/29**, `v08_unchanged` true. The sha256 of all 4 asset files and all 4 capture PNGs equals the table above.
- Godot 4.7.2 windowed captures re-rendered into `%TEMP%`:
  - Committed v07r1 helper at 1280×720, ruins and outskirts: both CAPTURE PASS, byte-identical to `e0808bee…` / `e980e4f1…`.
  - Any-size script at 640×360: both PASS, byte-identical to `e72addff…` / `8fbbf6f9…`.
  - Any-size script at 1280×720: byte-identical to the v07r1 output in both arenas, including the no-sprite frames.
- The measurement tool reproduces every number in the measurement tables, with 0 pixels outside the sprite differing for either version in either arena.
- `battle_arena.gd` sha256 was `be8859a8…` before and after the checks. `git status` showed no new files after Godot ran (no `.uid`/`.import`).
- Corrections made in this note: the roll gap holds on rows 22-27, not "every roll row"; the v07r1 hash is a file sha256, not a git blob; the boot/far-leg claim is softened; the scale caveat above.
- Visual issues still open at 1x (reviewer reading of the captures):
  - The coil reads as a small teal knob or hook, not a bedroll. At 640×360 its spiral is lost.
  - The drape is now the largest teal shape on the back and partly reads as a skirt or tail panel.
  - The boot and far-leg gains are hard to see without zooming.
  - The torso is still upright and stiff.
  - The companions' finish is still uneven.
- Status unchanged: UNAPPROVED/NONRUNTIME, sprites 0/52, meter 35.0% (zero-change closeout).
