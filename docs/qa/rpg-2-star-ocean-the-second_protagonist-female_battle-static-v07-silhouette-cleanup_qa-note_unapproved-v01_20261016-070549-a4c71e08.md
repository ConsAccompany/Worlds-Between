# Female protagonist battle static v07: silhouette cleanup QA note (v06 vs v07)

**Status:** This is an UNAPPROVED, test-only static candidate.
- It has one frame, with no animation.
- It is not runtime-integrated. Nothing in `game/scripts` or `game/scenes` changed.
- The Game Bible, trackers, acceptance count (complete sprites still **0/52**) and progress meter are unchanged.
- Committed to Git: the sprite, .pxo/.ora, manifest, the three tools, both captures with manifests, this note and the Codex audit. The ×3 hero crops stay local only and are not in Git.
- v06's files are byte-locked and unchanged (PNG, .pxo, .ora and manifest are hash-checked before and after build/check).

The creator approved only the 0.65 battle display proportion. This frame is not approved.

## Input

v07 responds to the Codex visual audit of v06: `docs/qa/rpg-2-star-ocean-the-second_protagonist-female_battle-static-v06-codex-visual-audit_unapproved-v01_20261016-065735-4e4450cb.md`. It also uses the v06 QA note (`…battle-static-v06-identity-cues_qa-note_unapproved-v01_20261016-065106-3e9f41d7.md`).

This pass targets only the four defects that are most visible at battle size:
1. The ponytail silhouette merges into the teal bedroll.
2. The collar shows only as a wedge behind the nape.
3. The pack/back cluster is crowded.
4. The lower coat and boots merge into one dark shape.

Nothing was added that reads only at zoom. Two zoom-only details were removed: the split hair strand and the steel buckle strap.

## Files (all new; v06 untouched)

| Role | Path | sha256 (bytes) |
|---|---|---|
| Candidate PNG (Pixelorama 1.2.3 flat export of the .pxo) | `game/assets/characters/combat-sideview-pilots/rpg-2-star-ocean-the-second_protagonist-female_sideview-idle-right-static-native0p65_unapproved-v07_20261016-070549-6711a51d.png` | `b6b26f40…48b3cb` |
| Editable source, 17 layers + hidden guides | `…_editable-layers_unapproved-v07_20261016-070549-f6ab9173.pxo` / `…-c3e59c16.ora` (same dir) | `01b0b6fc…e51e75` / `6072987c…d4732b` |
| Manifest | `…_manifest_unapproved-v07_20261016-070549-04075564.json` (same dir) | `fb26fa64…6776f5` |
| Author tool (preview / build / check) | `tools/rpg-2-star-ocean-the-second_protagonist-female_sideview-battle-idle-right-native-0p65-author_unapproved-v07_20261016-070549-0e2efcac.py` | — |
| Capture script (v06 method; only the header and test save root differ) | `tools/rpg-2-star-ocean-the-second_protagonist-female_sideview-battle-idle-right-native-0p65-party-capture_unapproved-v07_20261016-070549-33eb7e74.gd` | — |
| Region measurement (read-only) | `tools/rpg-2-star-ocean-the-second_protagonist-female_sideview-battle-static-v06-vs-v07-region-measure_unapproved-v07_20261016-070549-5b0d9e21.py` | — |
| Godot 1280×720 party capture, ruins | `outputs/rpg-2-star-ocean-the-second_protagonist-female_sideview-idle-right-static-native0p65_party-capture-ruins_unapproved-v07_20261016-070549-fedb99df.png` (+ `-ruins-manifest_…-54128bd4.json`) | `56d7b103…219d82c` |
| Godot 1280×720 party capture, outskirts | `outputs/…_party-capture-outskirts_unapproved-v07_20261016-070549-129e2621.png` (+ `-outskirts-manifest_…-73f12011.json`) | `8a83a283…e89333` |
| Hero crops ×3 nearest, cut from the real captures (one separate image each; local only, not committed) | `outputs/rpg-2-star-ocean-the-second_protagonist-female_battle-static_hero-crop-x3-{ruins,outskirts}-{v06,v07}_unapproved-v07_20261016-070549-*.png` (+ `…hero-crops-x3-manifest_…-8881e0ce.json`) | in the crop manifest |

The v06 references used for comparison are:
- PNG `…unapproved-v06_20261016-065106-a1d82e3a.png`;
- captures `…ruins_unapproved-v06_20261016-065106-3c5e1a90.png` and `…outskirts_unapproved-v06_20261016-065106-9a7c4e12.png`.

## What changed (hand-typed ASCII layers, binary alpha)

Unchanged from v06:
- the 68×72 cell, pin (32, 68), sole row 67 and crown row 7, so the approved 0.65 proportion and foot line hold;
- the head/face, hair tie, plume, scarf, coat torso and skirt, shirt, near arm and cuff, near leg and sword;
- the palette: the same 30 keys as v06, all taken from v8 south or carried over from v06. **No new colour.**

Changes:
- **Bedroll moved under the pack.** It is the same 9×9 teal roll end, now strapped beneath the pack at rows 34–42 instead of on top of it. The coat and skirt draw over its right edge. Nothing but hair now sits behind the head.
- **Ponytail.** It keeps v06's tall asymmetric plume. Below that is one clean tail that tapers to a tip on row 20, with clear air (rows 21–24) above the pack. The loose split strand is gone.
- **Pack simplified.** It moves back to v05's row (top row 25) and keeps the diamond emblem and dark flap edge. The steel buckle strap is removed and the body is shorter.
- **Collar front (new layer `collar-front`).** A 4×6 lit-slate collar point (`o` face, `c` inner fold) stands up under the jaw, drawn over the scarf's front edge. With v06's nape collar kept, the collar now shows on both sides of the scarf.
- **Lower-body plane change.**
  - The far trouser leg is now v8 spruce (`#324542` body, `#4a625c` front edge). In v06 it was the coat's deep slate `#222839`: the same colour as the coat's deep back tail, separated only by the outline.
  - The far boot gets a lit fold-over leather cuff (`B`/`b`), matching the near boot.
  - Reading top to bottom, the lower body is now slate skirt, leather hem, spruce leg, lit cuff, then dark boot.

Opaque texels fell from 1357 to 1345. Isolated single texels fell from 85 to 79.

## Technical checks (all run in this session)

- **`check` result: PASS, 19/19 gates.** These cover:
  - RGBA 68×72, binary alpha, no off-palette colour, 30 colours (≤ 32);
  - sole row 67 and crown row 7 the same as v06; pin row clear; both boots on the sole row; transparent border;
  - manifest hashes and unapproved flags;
  - byte-identical editable rebuild; .pxo and .ora layers equal the tool render;
  - Pixelorama flat and split-layer round-trips of both .pxo and .ora (17/17 visible layers, guides not exported), with the real Pixelorama APPDATA untouched;
  - the PNG equals a fresh Pixelorama flat export;
  - v06 is unchanged.
- **Godot 4.7.2 windowed captures** (real `battle_arena.tscn`, arena override `ruins` / `outskirts`, sentry, party at x 300/252/204/150, no yellow disc). Both report `CAPTURE PASS`:
  - sole at screen y 543 and crown at 422, so crown-to-sole is 122 screen px = 61 logical px, the same as v06;
  - integer 2× texels; 5380/5380 sprite pixels match the nearest-neighbour prediction; 0 off-palette pixels;
  - gap to Liang Xu 10 screen px with 0 overlap, the same as v06. The leftmost texel stays x15.
- **Background identity:** in both arenas, the v06 and v07 captures differ from the v07 no-sprite frame in 0 pixels outside the sprite. The two versions can therefore be measured against the same background.
- The working tree's `game/scripts/battle_arena.gd` has another workstream's uncommitted edits (sha256 `be8859a8…a592acae`). The captures ran against that file, as v06's did. Godot left no `.uid`, `.import` or other new files: the `git status` before/after diff shows only this task's files, plus files another session committed meanwhile in `8522451`.

### Structural measures for the four defects (`…region-measure…py`, texel space)

| Measure | v06 | v07 |
|---|---|---|
| Ponytail texels touching the bedroll (4-neighbour) | 5 | **0** |
| Ponytail texels hidden under later layers | 14 | 5 |
| Ponytail ↔ bedroll minimum gap (texels) | 1 | **14** |
| Visible ponytail texels / lowest visible row | 121 / row 17 | 128 / row 20 |
| Gear texels (pack, roll) above the scarf's top row | 20 | **0** |
| Back-gear texels | 173 | 141 |
| Collar texels in front of the scarf's front edge | 0 | **20** |
| Far trouser colour vs coat deep | identical (`#222839`) | different hue and value (spruce) |

### Value separation from the floor (mean |ΔL| Rec.709 / % of pixels under 20), real captures

| Region | ruins v06 | ruins v07 | outskirts v06 | outskirts v07 |
|---|---|---|---|---|
| Coat (torso + skirt), unchanged pixels | 40.8 / 18.3 % | 40.8 / 18.3 % | 42.4 / 17.6 % | 42.4 / 17.6 % |
| Collar (all collar layers) | 44.6 / 0 % (19 tx) | 44.6 / 5.1 % (39 tx) | 45.8 / 6.6 % | 46.1 / 9.6 % |
| **Far trouser leg (rows 42–56)** | **41.3 / 0 %** | **28.3 / 42.1 %** | **46.5 / 3.3 %** | **30.1 / 57.9 %** |
| Boots (rows 57–67) | 33.8 / 29.6 % | 33.8 / 29.1 % | 28.9 / 45.8 % | 29.3 / 45.3 % |
| Back gear (pack + bedroll) | 48.3 / 20.2 % | 47.5 / 22.9 % | 47.4 / 20.5 % | 48.8 / 23.6 % |
| Teal (scarf + bedroll) | 49.2 / 12.0 % | 48.3 / 13.2 % | 48.6 / 17.7 % | 50.2 / 20.0 % |
| Ponytail | 41.3 / 25.4 % | 41.0 / 24.0 % | 41.5 / 18.8 % | 42.4 / 18.0 % |
| Whole sprite | 50.2 / 18.2 % | 49.6 / 19.4 % | 49.8 / 19.5 % | 49.6 / 21.1 % |

## Honest visual comparison (actual 1280×720 Godot captures and the separate ×3 crops)

**Clearly better in v07:**
- **Ponytail.** In both arenas it now reads as one high, swept-back tail with its own outline and background showing around the tip. It looks longer than in v06, and it is no longer cut by the roll. The head-and-hair silhouette is the clearest it has been since v05, and the plume is kept.
- **Back cluster.** Above the shoulders there is now just hair, scarf and collar. The pack (with its emblem) and the teal roll form one stacked block on the lower back, below the scarf line. The teal roll still reads as a spiral and still repeats the scarf's teal, but now at waist height, so the two teals no longer stack together behind the head.
- **Collar.** A slate point is visible under the jaw in front of the scarf at gameplay size. Together with the nape piece, it reads as a stand collar the scarf is tucked into, not just a wedge behind the head.
- **Lower coat vs legs.** The far leg is now a green-grey trouser between the slate skirt and the boot, and the lit cuffs on both boots show the boot tops. The skirt, leg and boot read as three separate planes instead of one dark mass running from the coat's back tail to the boots.

**Trade-offs and regressions (measured):**
- **The far leg's separation from the floor dropped.** Spruce `#324542` is lighter than the slate deep, so it sits nearer the mid-value paving: |ΔL| fell 41→28 on ruins and 47→30 on outskirts, and over 40 % of its pixels are now within 20 L of the floor. The far leg still has its dark outline and reads as a leg, but on the outskirts floor it is the lowest-contrast part of the figure. This was the price of breaking it away from the coat while staying inside the v8 colours. The only in-palette alternative, a deep far leg, would bring back the fusion.
- **Waist area is fuller.** The roll now sits beside the belt and the skirt's back edge. At a glance it can read as a hip pouch or bundle rather than a bedroll. The back silhouette as a whole is still a large brown-plus-teal block, just lower and no longer touching the hair.
- **Collar-front shape.** It is a small dark slate block. Under the chin it could be misread as a shadowed jaw or throat, because `o` (L ≈ 108) is darker than the skin and teal around it.

**Unchanged (still open, not targeted):**
- the stiff, straight stance and the neutral face;
- the coat's lit plane `#5e6e8c` stays about 25 L from both floors (the creator decision about stepping above v8's ramp is still open);
- the three companions are still visibly simpler than the environment, which keeps the whole lineup looking provisional.

## Verdict and next step

v07 fixes the four targeted defects in structure:
- the ponytail is fully separated from the roll (gap 14 texels, 0 contacts);
- no gear sits behind the head;
- the collar shows in front of the scarf;
- the far leg no longer shares the coat's colour.

The cost is lower floor separation on the far leg and a fuller waist. Neither version is approved.

Suggested next static-only checks (not done here):
1. Decide whether the far leg may keep spruce at its lower contrast, or whether a darker in-ramp step should be tried on the outskirts floor only after creator review.
2. Judge whether the under-pack roll reads as a bedroll or as a pouch. If it reads as a pouch, a horizontal strap texel line across it could help, but only if it reads at 1280×720.
3. Before any motion work, have Codex or the creator view the source plus both four-person captures.

Motion remains blocked until the static is accepted.

This is Claude's visual judgement of the cited pixels and measurements, not creator acceptance.
