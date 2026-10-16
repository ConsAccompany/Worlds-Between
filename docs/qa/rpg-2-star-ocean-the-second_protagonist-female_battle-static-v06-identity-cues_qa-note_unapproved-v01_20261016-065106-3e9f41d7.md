# Female protagonist battle static v06: identity cues QA note (v05 vs v06)

**Status:** This is an UNAPPROVED, test-only static candidate.
- It has one frame, with no animation.
- It is not runtime-integrated. Nothing in `game/scripts` or `game/scenes` changed.
- The Game Bible, trackers, acceptance count (complete sprites still **0/52**) and progress meter are unchanged.
- Nothing is staged or committed.
- v05's files are byte-locked and unchanged (hash-checked before and after build/check).

The creator approved only the 0.65 battle display proportion. This frame is not approved.

## Input

v06 responds to the Codex identity/readability audit of v05: `docs/qa/rpg-2-star-ocean-the-second_protagonist-female_battle-static-v05-identity-readability-audit_unapproved-v01_20261016-064516-5c1f320e.md`. The audit's priorities were:
- a distinct teal bedroll on the pack;
- a pack emblem;
- a clear coat collar and cuff break;
- a more asymmetric high ponytail;
- coat light/dark planes separated from the floor;
- all at the same 0.65 scale and foot baseline.

## Files (all new; v05 untouched)

| Role | Path | sha256 (bytes) |
|---|---|---|
| Candidate PNG (Pixelorama 1.2.3 flat export of the .pxo) | `game/assets/characters/combat-sideview-pilots/rpg-2-star-ocean-the-second_protagonist-female_sideview-idle-right-static-native0p65_unapproved-v06_20261016-065106-a1d82e3a.png` | `2f573d9e…32decf` |
| Editable source, 16 layers + hidden guides | `…_editable-layers_unapproved-v06_20261016-065106-0122b1e0.pxo` / `…-63f3256a.ora` (same dir) | `e05466ef…a56c99f` / `d97d98bd…e0c500` |
| Manifest | `…_manifest_unapproved-v06_20261016-065106-80843e62.json` (same dir) | `9c88f89f…ef63b7` |
| Author tool (preview / build / check) | `tools/rpg-2-star-ocean-the-second_protagonist-female_sideview-battle-idle-right-native-0p65-author_unapproved-v06_20261016-065106-7ac0f8e3.py` | — |
| Capture script (v05 method; only the header and test save root differ) | `tools/rpg-2-star-ocean-the-second_protagonist-female_sideview-battle-idle-right-native-0p65-party-capture_unapproved-v06_20261016-065106-08846793.gd` | — |
| Godot 1280×720 party capture, ruins | `outputs/rpg-2-star-ocean-the-second_protagonist-female_sideview-idle-right-static-native0p65_party-capture-ruins_unapproved-v06_20261016-065106-3c5e1a90.png` (+ `-ruins-manifest_…-4b8d2f61.json`) | `6480d90b…4815ca` |
| Godot 1280×720 party capture, outskirts | `outputs/…_party-capture-outskirts_unapproved-v06_20261016-065106-9a7c4e12.png` (+ `-outskirts-manifest_…-e2f60b38.json`) | `9e5aa2ae…d82f` |
| Comparison crops: ruins v05, ruins v06, outskirts v05, outskirts v06 (×3 nearest, cut from the real captures) | `outputs/…_v05-vs-v06-party-capture-hero-crops-x3_unapproved-v06_20261016-065106-5d2b7c91.png` | `ba0fc847…40eb4d` |

The v05 references used for comparison are:
- PNG `…unapproved-v05_20261016-054620-8e5e4656.png`;
- captures `…ruins_unapproved-v05_20261016-054620-845c716a.png` and `…outskirts_unapproved-v05_20261016-054620-cfa9cdf9.png`.

## What changed (hand-typed ASCII layers, fixed palette, binary alpha)

Unchanged from v05:
- the 68×72 cell, pin (32, 68), sole row 67 and crown row 7;
- the head/face, hair tie, scarf, legs, boots and sword.

Changes:
- **Teal bedroll (new layer):** a 9×9 roll end sits on top of the pack. It has a lit `G` upper rim, a `g` body, one dark `Q` spiral ring and a `q` shadow base. It is drawn over the ponytail tips so the whole roll end stays visible.
- **Pack emblem:**
  - The pack is one row lower to seat the roll.
  - The lit flap carries a 5×5 diamond: a pale-beige rim (`#d7c0a8`, taken from v8 south's palette) around a teal leaf cross.
  - Below it are a dark flap edge and a steel buckle strap.
- **Collar (new layer):** a raised lit-slate collar stands behind the nape, drawn over the back hair and under the scarf.
- **Cuff:** the rolled sleeve cuff is v8 pale beige (`#d7c0a8` / `#b09986`), one texel wider than the sleeve. Its hue differs from the cream shirt.
- **Ponytail:**
  - A taller plume rises up and back from the tie, reaching row 1 (v05: row 3).
  - The main tail sweeps down the back of the head.
  - One loose strand splits off.
- **Coat value grouping:** this stays inside v8's storm-slate ramp.
  - The torso and skirt back halves and the sleeve underside are in the deep `#222839`.
  - The front planes and sleeve top are in the light `#5e6e8c`.
  - The mid `#3a4560` (closest to the paving) is reduced to a one-texel transition band.

Palette grew from 28 to 30 colours. Opaque texels grew from 1266 to 1357.

## Technical checks (all run in this session)

- **`check` result: PASS, 19/19 gates.** These cover:
  - RGBA 68×72, binary alpha, no off-palette colour, ≤ 32 colours;
  - sole row 67 and crown row 7 the same as v05; pin row clear; both boots on the sole row; transparent border;
  - manifest hashes and unapproved flags;
  - byte-identical editable rebuild; .pxo and .ora layers equal the tool render;
  - Pixelorama flat and split-layer round-trips of both .pxo and .ora (16/16 layers, hidden guides not exported, real APPDATA untouched);
  - PNG equals a fresh Pixelorama flat export;
  - v05 PNG/.pxo/.ora hashes unchanged.
- **Godot 4.7.2 captures:** windowed, real `battle_arena.tscn`, sentry, four-person party, `arena_override` = `ruins` / `outskirts`, no yellow disc. Both runs printed `CAPTURE PASS`:
  - 1280×720 at integer screen scale 2.0;
  - 5428/5428 sprite pixels exactly predicted from the texels, 0 off-palette;
  - crown-to-sole 61.0 logical px (same as v05), sole offset −2 screen px versus companions (same as v05);
  - 0 opaque-on-opaque overlap with any companion; bbox gap to Liang Xu **10 screen px (same as v05)**, because the leftmost texel stays at x15.
- **Godot side effects:** the run added no `.import`, `.uid` or other files under `game/` (checked by file mtime).

### Figure/floor value separation

The metric is mean |ΔL| (Rec.709) of each region's sprite pixels against the same pixels in the no-sprite frame, plus the share of pixels with |ΔL| < 20. Regions come from layer ownership, not colour keys. Both versions are measured against the v06 run's no-sprite frames; the background outside the sprite is identical between runs.

| Region | Ruins v05 | Ruins v06 | Outskirts v05 | Outskirts v06 |
|---|---|---|---|---|
| Coat slate (torso + skirt + collar + sleeve) | 29.0 / 41.1 % | **36.5 / 14.3 %** | 31.3 / 32.9 % | **38.2 / 11.2 %** |
| Coat lit plane `o` only | 28.1 / 27.1 % (144 px) | 27.8 / 21.3 % (268 px) | 23.9 / 17.4 % | 24.6 / 16.8 % |
| Back gear (pack + bedroll) | 44.6 / 11.7 % | 48.3 / 20.2 % | 44.3 / 11.7 % | 47.4 / 20.5 % |
| Teal (scarf + bedroll) | 45.8 / 13.1 % | 47.5 / 16.2 % | 42.5 / 28.7 % | 44.3 / 23.9 % |
| Ponytail | 41.2 / 23.7 % | 41.3 / 25.4 % | 43.2 / 17.0 % | 41.5 / 18.8 % |
| Whole sprite | 49.0 / 21.5 % | 50.2 / 18.2 % | 49.0 / 22.0 % | 49.8 / 19.5 % |

## Honest visual comparison (actual 1280×720 Godot captures)

**Clearly better in v06:**
- The **teal bedroll** reads at gameplay size in both arenas as a rolled teal spiral above the pack. It is the strongest new identity cue, and it repeats the scarf's teal on the back of the silhouette.
- The **pack emblem** reads as a small pale diamond with a teal centre. The pack is no longer a plain brown block.
- The **coat** now reads as a dark back mass and a lighter front plane instead of one mid-dark mass.
  - On ruins, coat pixels within 20 L of the floor fell from 41 % to 14 %. On outskirts they fell from 33 % to 11 %.
  - The skirt's back tail separates from the paving much more clearly.
- The **cuff** is visible as a beige band between sleeve and forearm, distinct from the cream shirt.

**Only partly solved:**
- **Collar:** at 1280×720 it reads as a small slate wedge between ponytail and scarf, not unmistakably as a raised field-coat collar. It does add a light break between dark hair and teal.
- **Ponytail:** the plume is taller and asymmetric. However, the bedroll now hides the lower tail and most of the split strand, so the hair silhouette reads a little *shorter* than v05's long arc. The "loose strands" quality of the sheet is still only hinted.
- **Coat lit plane:** `#5e6e8c` sits only about 25–28 L from both floors. The light plane's own separation barely moved, though it covers almost twice as many pixels. The gain comes from pushing the back half deep, not from a lighter light. A clearly lighter coat light would mean leaving v8's approved ramp, which is still a creator decision (carried over from v05).

**Regressions or trade-offs:**
- **Back silhouette:** the back is busier again (roll + emblem + ponytail cluster). v05 had removed the bedroll specifically to calm the back.
  - The gap to Liang Xu is unchanged at 10 screen px, and there is no overlap.
  - Back-gear pixels within 20 L of the floor rose from 12 % to 20 %, because the roll's dark `Q`/`q` and the pack's dark lower body sit near floor value.
- **Ponytail:** the hair now has less visible length (see above).

**Unchanged (still open):**
- the stiff, straight stance;
- the face carries no expression at this size;
- boots and lower coat share value.

## Verdict and next step

v06 is a better *identity* read than v05: teal roll, emblem, cuff and coat value grouping all register in the real party row. Collar and ponytail improvements are only partial, and the back is busier. Neither version is approved.

Suggested next static-only pass (not done here):
1. Let the ponytail tail fall in front of the roll's upper-left quarter, or shift the roll one texel down, so the hair regains length.
2. Widen the collar into a two-sided point that also shows at the front of the scarf.
3. Decide with the creator whether the coat light may step above v8's `#5e6e8c`.

Motion remains blocked until the static is accepted.

This is Claude's visual judgement of the cited pixels and measurements, not creator acceptance.
