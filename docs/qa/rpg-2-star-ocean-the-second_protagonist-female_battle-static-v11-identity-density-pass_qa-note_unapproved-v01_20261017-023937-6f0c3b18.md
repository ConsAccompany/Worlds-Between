# Female battle static v11: identity-density pass (QA note)

Status: **UNAPPROVED, NONRUNTIME, test-only static frame.** Nothing is wired into runtime. The Game Bible meter, the 0/52 sprite count, the scene 3/12 count and the 40.8% overall figure are unchanged. Motion work waits until the creator accepts a battle static baseline.

Sync addendum (2026-10-17): this note, the four 640×360 captures with their manifests, the sprite PNG, the `.pxo`/`.ora` editables and the sprite manifest are now tracked in Git, with unchanged bytes, so the creator can review them on another device. Codex judged the static identity legible enough to show the creator for feedback; that is not art approval. The three v11 tools in the table below stay local and are hash-pinned only. The "Files" heading below describes the state when this note was written. For links and the sync record, see the cross-device review packet `docs/qa/rpg-2-star-ocean-the-second_protagonist-female_battle-static-v11_cross-device-review-packet_unapproved-v01_20261017-165645-d581e7bc.md`.

Auth: claude.ai firstParty, Max subscription, with no `ANTHROPIC_API_KEY` set. This was checked before work started.

## What this answers

Codex reviewed the real v10 640×360 four-person outskirts capture (`outputs/...party-capture-outskirts-640_unapproved-v10_20261016-162819-7829fd0b.png`). It found two problems:

- The heroine reads too small and too detail-poor next to the approved exploration identity.
- Her lower body reads warm and orange.

The creator-approved 0.65 display proportion is unchanged:

- Same 68×72 cell, pin (32, 68), crown row 7 and sole row 67.
- Crown-to-sole is 61 logical px, and 61.0 px measured in Godot.

## Interrupted v11

`tools/...author_unapproved-v11_20261016-175823-e1e2a4b7.py` exists, but I did not use it:

- It stopped on a 429 session limit (`tmp/...v11-claude-response_v01_20261016-175800-53a0792c.json`) and never built any files.
- It targets the older v10 ruins review (arm separation, pack/roll).
- It keeps v10's orange legs and boots.
- Its offline 640 render (`%TEMP%/wb-v11/p2`) is almost identical to v10.

That file is left untouched. This v11 is a new fork of the verified v10 tool (check 35/35).

## Changes vs v10 (art)

**Palette.** Still 30 colours. The v8 orange leather pair is removed (`b` #845436, `B` #bb7c50). A deep, low-saturation brown pair is added (`d` #45342e at L 55, `D` #6f5a4c at L 93; saturation 0.32, so neither counts as orange). Every shared key keeps its v10 colour.

**Lower body.**
- The coat hem trim is deep slate or dark leather.
- The belt is dark leather with a pale buckle.
- The near knee has a cool grey pad (m/M) on a dark strap.
- Trousers are spruce (T/t) over deep slate.
- Boots: a dark cuff (l) and deep-brown shaft (d) with a pale strap sit over the paving (rows 58-61, background L ≈ 75-110). Over the contact shadow (rows 62-67, background L ≈ 45-70), the foot is lit with D, plus a pale toe glint and a dark heel and sole.
- Saturated orange texels from the belt down: 116 → 0 (19.5% → 0%).

**Head and hair.**
- Hair is darker: shades 1/2 are 78% of hair texels.
- A pale hair tie sits where the ponytail leaves the head.
- The ponytail is a fuller hook that ends in two split locks, at least 4 rows clear of the bedroll.
- A side lock frames the face in front of the ear, and fringe strands fall over the brow.
- Face: a 3-wide brow over a 2×2 eye (lash, iris and one white catch), blush, nose step and mouth.

**Arm and hand.** The sleeve is rolled to the elbow with a pale cuff (9 texels). The forearm is bare skin (11 texels). The hand wears a fingerless dark glove (8 texels) with bare knuckles and thumb (12 texels).

**Pack and insignia.** The pack is grey-brown canvas (10×11, was 9×10 tan) with a dark flap edge, a strap and a pale buckle. A new `insignia` layer puts a 3×3 teal diamond on the upper sleeve. At 1x it is a colour placement, not a legible emblem.

**Unchanged layers.** These are byte-identical to v10: hip-drape, shirt-lapel, sword-blade, sword-guard, collar, scarf-neck and collar-front.

**Silhouette.** The bounding box is the same [15, 1, 60, 67]. Texels go from 1451 to 1473, IoU 0.93.

## Files (all untracked, local)

| file | sha256 |
|---|---|
| `game/assets/characters/combat-sideview-pilots/...static-native0p65_unapproved-v11_20261017-023937-873fe1e6.png` (runtime-format candidate, 68×72 RGBA, binary alpha) | `cca1683392af7cd9d6c8305b64d2527b1573bc582cf2d011ec3bd876bc4b24c3` |
| `...editable-layers_unapproved-v11_20261017-023937-e2debcc6.pxo` (Pixelorama pxo_version 7, 19 layers + hidden locked guides) | `73aacdf0474f912a65d4deb8bfed3c9cad03a632dbdcd85c4d17f799e32fda86` |
| `...editable-layers_unapproved-v11_20261017-023937-4d57e12a.ora` | `21e09b9aced48ae5003c0c01c1bc2eee3c4527089a6dce01123065806307cd32` |
| `...manifest_unapproved-v11_20261017-023937-3e18a8af.json` | `b6ec32906e010570592516e6a268f1806a21d8497113be2a2ec0b10141656dd6` |
| `tools/...native-0p65-author_unapproved-v11_20261017-023937-c4a17e52.py` | `2e89d1f253b22a5ce2b718746eef7567c410787c83dbbd12d5a95db0ee88a629` |
| `tools/...party-capture-any-size_unapproved-v11_20261017-023937-5b81c0d4.gd` (v10 script + sentry-gap measure) | `dce7400fa420b13707f5c16aca775c84f86dbe5576c2f8059f94c3356f577502` |
| `tools/...battle-static-v10-vs-v11-capture-measure_unapproved-v11_20261017-023937-9d2e61f7.py` (read-only) | `fb22d1d2a234b14a9d052b96c60aa30260e0fcb323add0e06ebc1a095d1c8798` |
| `outputs/...party-capture-ruins-640_unapproved-v11_20261017-023937-b6af9a1c.png` | `51ff11303368db4bca434be8c88a3470d83e094a994c7da0a2363e69399c6234` |
| `outputs/...party-capture-archive-640_unapproved-v11_20261017-023937-0b43cdb2.png` | `c9e529a9b0eff29f1887530852e7d7e2f8820bd41f7066021b425acc7c9d0357` |
| `outputs/...party-capture-city-terrace-640_unapproved-v11_20261017-023937-fe093ca6.png` | `cb88f9cb43f719ecd73024fd36947db2db39603b814460bc06016f4a85dfd808` |
| `outputs/...party-capture-outskirts-640_unapproved-v11_20261017-023937-0ec09d0b.png` | `6e4a5f4227774c289f752f0490cd4ab6b9b1d1fc887c1c86bee877b3a8b65d9a` |

Each capture has a matching `...-640-manifest_...json` in `outputs/`: ruins `3b6a06d2`, archive `11e14503`, city-terrace `83496a11`, outskirts `6ad0b2a3`.

The v10 files are hash-locked and read-only for the tool; `v10_unchanged` passes before and after.

## Technical evidence

**`check`: PASS 40/40,** run twice: once with the real APPDATA and once with APPDATA redirected to an empty temp dir. A Pixelorama GUI from another session was open throughout and was left alone. The gates cover:
- binary alpha, palette, ≤ 32 colours;
- crown row 7, sole row 67, left edge ≥ x15, right edge ≤ x62;
- manifest hashes and UNAPPROVED flags;
- byte-identical rebuild of the `.pxo` and `.ora`;
- `.pxo` and `.ora` layer stacks recompose to the PNG;
- the `.ora` merged image equals the PNG;
- the layer and palette diff vs v10 is exactly as declared;
- 12 identity, lower-body and boot gates.

**Pixelorama 1.2.3 headless round-trip.**
- `.pxo` flat export: RGBA equals the tool render, and the delivered PNG is that export.
- `.ora` flat export: RGBA equals the tool render.
- Split-layer export: 19/19 visible layers match for both `.pxo` and `.ora`; the guides layer is not exported.
- The real Pixelorama APPDATA was untouched apart from the GUI's heartbeat.

**Godot 4.7.2 captures.** All four are real windowed captures at 640×360 (`--resolution 640x360`, canvas_items integer stretch, k = 1) in the real `battle_arena.tscn`, using each arena band through `arena_override`. All report CAPTURE PASS:
- sprite pixels 1473/1473, off-palette 0, nearest-texel match 1.0, every texel exactly 1×1 px;
- crown-to-sole 61.0 logical px (67.0 including the ponytail), sprite bbox x283-328, y205-271;
- zero opaque-on-opaque overlap with any companion;
- bbox gap to Liang Xu 5 px, the same as v10's 640 captures;
- gap to the sentry 74 px (sentry's own pixels start at x403).

**Read-only measure tool.** For each arena, the v11 PNG drawn over the matching Godot no-sprite frame equals the Godot capture exactly, and only the 1473 sprite pixels differ. Fidelity passes.

## Bright vs dark environments

Mean |ΔL| of sprite texels against the background they cover (outline excluded). Same background for v10 and v11, measured by the tool above.

| arena (background L behind the figure) | region | v10 |ΔL| / share < 20 / orange | v11 |ΔL| / share < 20 / orange |
|---|---|---|---|
| archive (brightest at the figure, lower body L 91) | lower body | 42.3 / 15.2% / 27.6% | 39.9 / 18.1% / 0% |
| archive | boots | 39.0 / 9.1% / 57.6% | 37.7 / 3.8% / 0% |
| ruins (brightest whole scene) | lower body | 38.9 / 17.6% / 27.6% | 35.6 / 22.9% / 0% |
| ruins | boots | 42.0 / 13.6% / 57.6% | 37.3 / 14.4% / 0% |
| outskirts (darkest at the figure, lower body L 76) | lower body | 38.3 / 20.2% / 27.6% | 34.6 / 28.6% / 0% |
| outskirts | boots | 42.7 / 25.0% / 57.6% | 36.1 / 33.3% / 0% |
| city-terrace | boots | 43.9 / 3.8% / 57.6% | 39.3 / 3.8% / 0% |

The torso gains contrast on every arena (49.7-51.3, against v10's 45.4-48.4). The head is level or higher (51.4-58.7, against 51.3-55.3); ruins is 0.5 lower.

All four arena bands have mid-value floors. "Dark" here means outskirts, which is the darkest behind the figure. None of them is a truly dark or night field.

## Visible limitations (honest)

- **"Too small" is not solved by size.** The approved proportion fixes her height, and the silhouette box is identical to v10's. She still reads slimmer and lighter in mass than the three wide, big-headed companions. The added density is in the face, hand, forearm, hair, boots and pack, and it mostly shows at 2× and above. At 1× it reads as clearer colour blocks: dark tied hair, teal scarf, slate coat, spruce/brown legs.
- **Cooler lower body costs some contrast.** Lower-body |ΔL| drops by 1.6-3.7 against v10 on every arena. On outskirts, boot texels within 20 L of the background rise from 25% to 33%; this is mostly the dark sole band inside the contact shadow. A first v11 pass with all-dark feet measured 63.6% and was rebuilt with lit D feet before delivery.
- **Boots are two-tone** (dark shaft, lit foot), as in v09/v10.
- **Hair still reads mid-brown at 1×.** Shade 2 (#3d2a22) dominates. It is darker than v10 but lighter than the character sheet.
- **The pale hair tie reads as a separate bead** at 8×.
- **The face is small.** The 2×2 eye and brow read at 2× and above; at 1× they form one dark dot.
- **The insignia is 4 visible teal texels.** It is a colour placement only.
- **The scene is limited.** It is a four-person party with an empty fifth slot and an idle sentry; no attack telegraph was captured.
- **The draw order differs from runtime.** The overlay draws the candidate above the companions; at runtime, fighter 0 draws beneath them.
- **No clean-clone run.** The v10 lock files are untracked and local, so a clean clone would fail the lock.

## Next

Codex/creator visual review of the four 640×360 captures. No motion, runtime swap or counter change follows from this note.
