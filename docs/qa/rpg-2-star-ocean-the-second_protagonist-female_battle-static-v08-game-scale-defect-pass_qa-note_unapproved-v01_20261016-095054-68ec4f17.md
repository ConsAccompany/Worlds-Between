# Female protagonist battle static v08: game-scale defect pass, QA note (v07 vs v08)

**Status:** This is an UNAPPROVED, test-only static pilot.
- It has one frame, with no animation.
- It is not runtime-integrated: `game/scripts/battle_arena.gd` and `game/scenes` were not touched.
- The Game Bible, trackers, completion state, acceptance count (complete sprites still **0/52**) and Git are unchanged. Every v08 file is untracked.
- v07 is byte-locked and unchanged: its PNG, .pxo, .ora and manifest are hash-checked before and after build/check.

The creator approved only the 0.65 battle display proportion. v08 keeps it exactly. The art is not accepted.

## Input

- Codex game-scale audit of v07: `docs/qa/rpg-2-star-ocean-the-second_protagonist-female_battle-static-v07-game-scale-codex-audit_unapproved-v01_20261016-114641-bf5d6029.md`. It names five defects: a fragmented white sword, a forearm/belt/hilt merge, jacket and hip blending into the gray paving, a squared teal back pouch that lost v8's fabric/bedroll identity, and stiff parallel boots.
- v07 source and QA note (`…battle-static-v07-silhouette-cleanup_qa-note…-a4c71e08.md`).
- Approved exploration baseline: south v8 static (`game/assets/characters/pixelorama-pilots/…south-idle-selout-v8-cloth-leather-candidate_m8-v08_20261015-021600-157a5ea0.png`). It is the reference for the teal roll on the pack and the teal hip drape.

## Files (all new, all untracked)

| Role | Path | sha256 (bytes) |
|---|---|---|
| Pilot PNG (Pixelorama 1.2.3 flat export of the .pxo) | `game/assets/characters/combat-sideview-pilots/rpg-2-star-ocean-the-second_protagonist-female_sideview-idle-right-static-native0p65_unapproved-v08_20261016-095054-a06775a0.png` | `edee2924…d0adc5` |
| Editable Pixelorama project, 18 layers + hidden locked guides | `…/combat-sideview-pilots/rpg-2-star-ocean-the-second_protagonist-female_sideview-idle-right-static-native0p65_editable-layers_unapproved-v08_20261016-095054-2574ce1c.pxo` | `bf7111a2…04544cb` |
| Same layers as OpenRaster | `…_editable-layers_unapproved-v08_20261016-095054-314d939f.ora` (same dir) | `818e4bd4…6048e34` |
| Manifest | `…_manifest_unapproved-v08_20261016-095054-ab653c87.json` (same dir) | `8ec39ef6…a903814b` |
| Author tool (preview / build / check) | `tools/rpg-2-star-ocean-the-second_protagonist-female_sideview-battle-idle-right-native-0p65-author_unapproved-v08_20261016-095054-326522f8.py` | — |
| Read-only v07-vs-v08 measurement | `tools/rpg-2-star-ocean-the-second_protagonist-female_sideview-battle-static-v07-vs-v08-region-measure_unapproved-v08_20261016-095054-c2a29cc3.py` | — |
| Godot 1280×720 four-person capture, ruins | `outputs/rpg-2-star-ocean-the-second_protagonist-female_sideview-idle-right-static-native0p65_party-capture-ruins_unapproved-v08_20261016-095054-a7962fdf.png` (+ `…party-capture-ruins-manifest_unapproved-v08_20261016-095054-1a83eade.json`) | `2865e4d5…60f1f55d` |
| Godot 1280×720 four-person capture, outskirts | `outputs/rpg-2-star-ocean-the-second_protagonist-female_sideview-idle-right-static-native0p65_party-capture-outskirts_unapproved-v08_20261016-095054-d9a8abaf.png` (+ `…party-capture-outskirts-manifest_unapproved-v08_20261016-095054-7dee7835.json`) | `19c5677e…a60c95e56` |

The capture script is the committed clean-clone helper, used unchanged: `tools/rpg-2-star-ocean-the-second_protagonist-female_sideview-battle-idle-right-native-0p65-party-capture-clean-clone_unapproved-v07r1_20261016-085133-1c89279f.gd`. Its blob matches `b12576a`. No x3 crops and no comparison sheets were produced. Each capture is its own file.

## What changed (hand-typed ASCII layers, binary alpha, no new colour)

Unchanged from v07:
- the 68×72 cell, pin (32, 68), sole row 67 and crown row 7, so the 0.65 proportion holds at 61 logical px crown-to-sole;
- the head/face, hair tie, ponytail, nape collar, collar front, scarf, shirt/lapel and coat torso shape;
- the 30-key palette, all from v8 or v07. 29 keys are used; the dark steel `m` is unused.

Changes, one per defect:

1. **Sword.** The blade is now raised forward at 45°. Each row is outline, edge light `Z`, steel `M`, outline, stepping one texel per row. The edge light runs as one unbroken 1:1 diagonal instead of v07's 2:1 stair of two-texel dashes. The guard is a small diagonal crossguard square to the blade.
2. **Forearm/belt/hilt.** The elbow bends and the forearm comes forward across the white shirt: slate sleeve, beige cuff, then a tan glove (new `fist` layer) closed round the grip at chest height. The hand and hilt end on row 33, four rows above the belt. The belt's top row is now lit leather `B`, so it reads as one warm waist line.
3. **Jacket/hip.**
   - v8's teal hip drape (new `hip-drape` layer) hangs from the belt over the deep back of the coat skirt.
   - The skirt hem trim is lit `B` (L 134) instead of `b` (L 92, close to the floor's L ≈ 82).
   - The v07 shirt tail under the coat front was removed.
4. **Back gear.** The 9×9 spiral square under the pack is gone. In its place, a teal blanket roll lies **on top of** the pack, as v8 carries it above the shoulder. It is a 9×6 rounded capsule with a lit top, a coiled back end and one leather strap. The pack is a plain tan block with one beige buckle; v07's diamond emblem only read at zoom. The ponytail is drawn over the roll, so it is never cut.
5. **Boots and stance.** This is now a ready stance:
   - the near knee is bent forward over a flat front boot;
   - the far leg is angled back onto the ball of a heel-raised rear boot whose sole slopes to the toe.

   The stance is 31 texels wide (v07: 24) and the boots stand 5 texels apart on the sole row (v07: 3).

## Technical checks (all run in this session)

- **`build`:** Pixelorama 1.2.3 headless, with APPDATA redirected. Flat and split-layer exports of both .pxo and .ora matched (18/18 visible layers, guides not exported). The PNG is Pixelorama's flat export and equals the tool render.
- **`check`: PASS 19/19** on the rerun. The first `check` run failed one gate, `pixelorama_roundtrips`, only because `real_appdata_pixelorama_untouched_except_heartbeat` was false. The other session's open Pixelorama GUI (PID 50828) autosaved `%APPDATA%\pixelorama\backups\2026_10_15_13_56_34\(untitled backup)-…` at 10:01:09 during the run. This tool's exports use a temp APPDATA; all four round-trips passed in that run too. The immediate rerun passed 19/19.
- **Clean clone:** `check` passes 19/19 from fresh `--shared` clones of HEAD (`b12576a`), with `core.autocrlf=true` and with `false`. Only the v08 tool and the four v08 asset files were copied in; the v07 locks come from Git. The clones were deleted afterwards.
- **Godot 4.7.2 windowed captures** use the real `battle_arena.tscn`, arena override `ruins` / `outskirts`, the sentry, and the party at x 300/252/204/150. The yellow disc is not drawn. Both captures report `CAPTURE PASS arenaMode=arena-override-band`:
  - sole at screen y 543 and crown at 422, so crown-to-sole is 122 screen px = 61 logical px, the same as v07;
  - integer 2× texels; 5452/5452 sprite pixels match the nearest-neighbour prediction; 0 off-palette pixels;
  - gap to Liang Xu 10 screen px with 0 overlap, the same as v07; the leftmost texel stays at x15.
- **Background identity:** the v08 run's no-sprite frames are byte-identical to the v07 no-sprite frames, in both arenas. An offline 2× composite of the PNG over them reproduces both real captures byte-for-byte. The measurement tool finds 0 changed pixels outside the sprite for both versions.
- **Working tree:** the captures ran against the working tree's uncommitted `battle_arena.gd` (sha256-text-lf `be8859a8…a592acae`, unchanged before and after), as v06/v07's did. The `git status` diff before and after shows only the 10 v08 files: no `.uid`, `.import` or other new files. Lines that disappeared were files another session committed meanwhile in `b12576a`.

### Structural measures (`…v07-vs-v08-region-measure…py`, texel space)

| Measure | v07 | v08 |
|---|---|---|
| Light blade texels (Z+M) / 4-connected light components | 23 / 1 | 19 / 1 |
| Blade geometry | 2:1 stair, edge light in 2-texel dashes | 1:1 diagonal, one continuous edge-light line |
| Lowest hand/hilt row / rows clear of belt top (row 38) | 40 / **−3** (overlaps belt) | 33 / **4** |
| Bedroll bbox (w×h) / rows | 9×9 square / 34–42 | 9×6 capsule / 23–28 |
| Ponytail texels touching roll / min gap | 0 / 14 | 0 / 3 (ponytail drawn over the roll) |
| Roll teal ↔ scarf teal min gap (texels) | 12 | 4 |
| Stance width / sole-row gap between boots | 24 / 3 | 31 / 5 |
| Rear boot heel lift above sole row | 1 | 2 (sloped sole) |
| Isolated single texels (tool stat) | 79 | 100 |

The two blades both form one 4-connected light component, so the "fragmented" read cannot be measured this way. The improvement is the line regularity, and that is a visual judgement. The rise in isolated texels is mostly diagonal lines whose same-colour neighbours touch only at corners: blade 19, drape highlight and fold 9, roll coil 8. It is not added noise.

### Value separation from the floor (mean |ΔL| Rec.709 / % of pixels under 20), real captures

| Region | ruins v07 | ruins v08 | outskirts v07 | outskirts v08 |
|---|---|---|---|---|
| Jacket (coat torso incl. belt) | 43.9 / 9.7 % | 45.2 / 5.4 % | 46.1 / 10.1 % | 47.5 / 7.6 % |
| Coat skirt | 39.5 / 21.9 % | 40.9 / 19.3 % | 40.8 / 20.7 % | 41.1 / 11.1 % |
| Hip drape (v08 only) | — | 52.8 / 13.7 % | — | 51.2 / 17.0 % |
| Hip band, all layers, rows 38–52 | 46.6 / 23.2 % | 43.7 / 18.4 % | 47.3 / 21.1 % | 43.9 / 13.1 % |
| Far trouser leg | 35.5 / 35.6 % | 33.1 / 34.7 % | 34.9 / 48.9 % | 33.9 / **52.8 %** |
| Boots | 33.8 / 29.1 % | 31.5 / **34.6 %** | 29.3 / 45.3 % | 28.5 / 46.5 % |
| Back gear (pack + roll) | 47.5 / 22.9 % | 46.6 / 20.4 % | 48.8 / 23.6 % | 46.9 / 20.0 % |
| Teal (scarf + roll + drape) | 48.3 / 13.2 % | 51.1 / 12.1 % | 50.2 / 20.0 % | 50.9 / 18.4 % |
| Sword (blade + guard) | 88.2 / 7.3 % | 88.7 / 2.4 % | 88.7 / 3.2 % | 88.6 / 0.0 % |
| Whole sprite | 49.6 / 19.4 % | 47.3 / 19.4 % | 49.6 / 21.1 % | 47.3 / 20.0 % |

The hip band's mean |ΔL| fell. v07's band contained the bright glove and hilt, which v08 moved up to the chest. The share of hip pixels within 20 L of the floor fell in both arenas, and that share is the blending measure.

## Visual comparison at 1× (real 1280×720 captures, viewed full-frame)

**Better in v08:**
- **Sword:** one bright diagonal raised toward the sentry, with no dash pattern. It is the clearest weapon read in the lineup.
- **Hand:** tan fist at chest height in front of the white shirt, clearly separate from the belt line below it.
- **Pose:** the open ready stance with the forward knee and raised rear heel removes the parallel-boots stiffness. The figure reads as about to move, not standing at attention.
- **Back gear:** a teal roll sits on a tan pack. That is the v8 arrangement, and it no longer reads as a square pouch at the waist.
- **Hip:** a teal accent and a lit belt and hem break the jacket/hip area away from the gray paving.

**Costs and open defects (not hidden):**
- **Far leg:** still the weakest region against both floors (33 |ΔL|; 53 % of pixels under 20 on outskirts, slightly worse than v07). The boots lost a little separation on ruins (29 % → 35 % under 20).
- **Roll vs scarf:** the roll sits 4 texels from the scarf teal (v07: 12). At 1× they stay separated by the coat's dark upper back. A reviewer may still read a teal band across the shoulders.
- **Roll detail:** the roll's coiled end is 3 texels and does not read at 1×. The roll reads as a teal bundle or roll on the pack, not as a detailed bedroll.
- **Hip drape:** a narrow sash tail, smaller than v8's wide drape. It could also read as a sash.
- **Unchanged:** the upright torso, the neutral face and the companions' simpler finish.

## Verdict

At actual 1× game scale, Claude judges v08 better than v07 on all five named defects. The cost is a slightly weaker far leg and boots on the floor, plus a closer roll-to-scarf teal spacing. Under the brief's rule ("if worse than v07, keep v07"), v08 is not worse. It is the suggested test-only static reference for the next review.

This is Claude's visual judgement, not Codex's audit and not creator acceptance. Neither version is approved, and v07 stays committed and untouched. Motion stays blocked until a static frame is accepted.
