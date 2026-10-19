# Female battle static v16: boot construction + canister restore (QA note)

Status: **UNAPPROVED, NONRUNTIME, test-only static frame. Not a final static baseline. Not ready for creator approval
until the root judges the captures.** One bounded authored pass; no animation and no other character work.

What stayed unchanged:
- runtime, `battle_arena.gd`, defaults, the Game Bible, the ledger, the Site, the index and every counter (production
  51.2%, scenes 3/12, sprites 0/52, human plays 0/2);
- this version earns no points.

Nothing is staged, committed or pushed. Auth: Claude Code, claude-opus-5-5, signed in to Max (firstParty). No quota was
hit during this pass.

Worktree: `work/max0840-battle` (dirty, preserved), branch `codex/chicago-native-materials-v06`, HEAD `9c38351`. v16 adds
only these untracked paths:
- `outputs/battle-static-v16/`;
- two `tools/` files;
- this note.

v14 (tracked) and v15 (untracked) sources, outputs and captures are hash-locked and byte-identical before and after.
The separate NORTH v03 session in `max0840-male` was not touched.

## Brief (root review of v15)

What the root saw in v15:
- the pack is calmer, but its internal form is flatter;
- the lower body is darker and heavier;
- the boots still merge inside the outskirts contact shadow;
- removing the canister loses an outfit identity item, so that removal is not adopted.

What this pass does: ONE method change, not another palette or darkness tweak.
- Redraw the boots' material planes and their knee-to-ankle, shaft, vamp, heel and toe volume.
- Restore the canister as a quiet steel form.
- Keep v14's slim boot width and stance, the 0.65 proportion, the 68×72 cell, pin (32, 68), crown row 7 and sole row 67,
  the blade reach and the draw order.

## What changed

| layer | v16 change (alpha identical to v15 = v14) |
|---|---|
| far-leg (boot) | Boot redrawn as planes, one step darker than the near boot (body's shadow). Cuff lip `L d n n d`. Cylinder shaft `L L d n n`. The lit plane bends forward over the instep onto the toe (`n` → `D`). Foot side `d` toward the heel (`L` heel edge) and `n` toward the toe. Sole is one dark leather row `L`. The thigh and shin keep v15's `C`/`T` planes. |
| near-leg (shin + boot) | The shin under the knee pad turns as a cylinder `C T T t t`, its lit front meeting the boot's lit front. Cuff lip `d n n D D`. Cylinder shaft `L d n D D`. One contiguous lit plane `D` runs down the shaft front, over the instep, onto the toe cap. The foot side is mid leather `n`, darkening to the heel counter `d` (`L` heel edge). Sole is a dark leather row `L`. **v14/v15's two-row lit base is removed: no welt band, no perimeter, no rim.** |
| pack | v15's calm planes plus one contiguous mid-leather bulge `n` (rows 31–33) under the flap, for volume. No buckle, strap or marks. |
| canister (restored) | Quiet steel bottle inside the pack alpha (x16–20, rows 30–36), outlined. Its side away from the light is the coat's mid slate `c` (dark blue-grey steel at this size), then mid steel `m`, a lit column `M` only two texels tall, and a dark base `c`. |

**Disclosed palette plane:** one new key, `n` = `#5d4738` (L≈75). It sits between `d` (55) and `D` (93) in the same
brown hue.

Two other keys were drafted and dropped before the build so the sprite stays at ≤32 used colours (32 used):
- a lit-leather toe crest `#8a6e5c`; the toe crest is `D` instead;
- a dark steel `#3d4550`; the canister's dark side reuses `c` instead.

No metric or grid search was run.

17 layers are byte-identical to v15:
- head and face, hair, ponytail, loose lock, hair band;
- scarf, collars, coat torso, coat skirt (with v15's `e` tail);
- shirt, arm, fist, blade, guard, insignia;
- bedroll, hip drape.

The silhouette is unchanged against v15: IoU 1.0, 1590 texels, bbox [15, 1, 60, 67], identical edge keys. 155 composite
texels change.

## Files

All files are new and untracked. Directory `outputs/battle-static-v16/`; every name starts
`rpg-2-star-ocean-the-second_female-battle-idle-right_` and ends `_unapproved-v16_20261018-212808-<id>`.

| file (middle part + id) | sha256 |
|---|---|
| `static-native0p65` … `e75685af.png` (68×72 RGBA, binary alpha, Pixelorama flat export of the .pxo) | `ce6d294c23f89556e3822470966704ef68534d4deb69500a03d47f63ca79b768` |
| `editable-layers` … `42bf565b.pxo` (pxo_version 7, 21 layers + hidden locked guides) | `4b5fcfa2ef339f624089d456f1ddcfe0e91ada2c323e3ddcd40ef39052ffa140` |
| `editable-layers` … `5df7445c.ora` | `5715ef9d907d79ce1c11a141c2ef94bd129f2a87294d68e693fbafce3880c3cf` |
| `manifest` … `f5435c16.json` | `127bb9bcf605215eea636a1dfb1c7c6033084abf1f1cb41c7f001bcdbcb876f0` |
| `cap-ref160b823-archive-640-zh` … `111b8e75.png` | `0a5d0e4256141ef28b906b4a400bd237f571ecb83ceb09b28cb63b16e99b2d7e` |
| `cap-ref160b823-archive-640-en` … `018e4300.png` | `413b2f710a404e75088c4a177e58df53f673eaf4b90feff1ff97a44a245e9994` |
| `cap-ref160b823-outskirts-640-zh` … `82ac83e8.png` | `cfcc6bfc55c5f7f67b9e15a0ad7b8abb0ba045fca30e2f424708d2d774693f90` |
| `cap-ref160b823-outskirts-640-en` … `e3d6352b.png` | `a244d852c4488f808f91de81aafbbed4b93aa96a5dbad1915fc47f877a675164` |
| capture manifests `cap-ref160b823-<tag>-manifest` | archive zh `5b093151…`, archive en `10df7e0d…`, outskirts zh `30ddbfb8…`, outskirts en `2388475f…` |
| no-sprite frames `cap-ref160b823-<tag>-nosprite` | archive zh `6547af00…`, archive en `ce31bdbd…`, outskirts zh `45f10d5f…`, outskirts en `219931c1…` (equal to v15's) |
| `author-check-report` … `59e9c563.json` | `f9edef267841e7b92e155746dc47f76bf82807727b1eb68d786bab5adae9849d` |
| `capture-measure-report` … `10f7678d.json` | `4393d18fb253deefd2f03895dafc30a76e71fd7f53f827a2b092b2e209cde936` |
| `capture-run-evidence` … `c1fd0792.json` | `81a874d1f59eeb7bcf8a563fdc2f5ae4feacbbf272a1269a83db0228b765a343` |
| batch manifest `batch-manifest` … `788f1b9f.json` | listed in the session report (it hashes this note) |
| `tools/rpg-2-star-ocean-the-second_female-battle-static_author_unapproved-v16_20261018-212808-b8cd7ca5.py` | `abe0623f80082c9b986ded767c1c5789655f6fffe18793a4ed6ebd7d2efbee63` |
| `tools/rpg-2-star-ocean-the-second_female-battle-static_v15-vs-v16-capture-measure_unapproved-v16_20261018-212808-2b9eb962.py` (read-only) | `0d6f01edb366fa98e5aa0a3c05f3d354488f9292d1b972584f8b19f18782bbc6` |

JSON and .py files are LF, so raw sha256 equals sha256-text-lf-v1. PNG, .pxo and .ora hashes are sha256-bytes.

## Evidence

**Author `check` (worktree, Pixelorama 1.2.3 headless, APPDATA redirected): PASS 42/42.** The gates are preservation
and construction checks, not contrast thresholds:
- binary alpha; 32 colours; crown row 7; sole row 67; x15–60;
- 17 layers byte-identical to v15;
- the changed layers keep v15's alpha;
- **both leg/boot layers' alpha is identical to v14** (slim width, stance, heel step, toe);
- the canister lies inside both the v15 and v14 pack alpha;
- edge keys are identical to v15 (no new rim);
- plane order `d < n < D` and `c < m < M`;
- each boot's lit plane `D` is one 4-connected surface, and so is its mid plane `n`;
- both sole rows are `L` only (no lit base or welt);
- the canister uses steel and outline keys only, with a lit column of ≤2 texels touching `m`;
- no buckle on the pack; no `u` on the lower body;
- manifest, rebuild and recomposition checks pass;
- v15, v14 and protected locks are unchanged.

**Native pixel equality vs application diagnostics (separate).**
- *Native:* the Pixelorama flat export equals the PNG for .pxo and .ora. Split export matches 21/21 layers for both,
  and the guides are not exported. The real APPDATA is untouched.
- *Application diagnostics (not clean, not gated):*
  - every .pxo export prints 4× `ERROR: Condition "!actions.custom_samplers.has(...)"` (shader_compiler.cpp:1329);
  - every .ora export adds importer/exit errors (`p_index` out of bounds ×3, `rp_node` null, "Must be an ancestor",
    "16 resources still in use", RID/ObjectDB leaks).
  - The unchanged v15 .pxo/.ora controls print the same classes. Only the leak counts differ (22 vs 21 RIDs, 196 vs 190
    ObjectDB), because v16 has one more layer.
  - **The application run is not clean.**
- No GUI Save As or reopen was run.

**Captures (real Godot 4.7.2, windowed 640×360, four separate images).**

Context, labelled as such:
- the frozen reference is `git archive 160b823 game` plus the unchanged v14 probe (`720c8377…`);
- the bands and the radius-18 contact shadow are **test-presentation context drawn by the probe**. They are not proof
  that current main draws them by default;
- **no runtime or default-integration claim** is made for v16;
- the root captures the canonical game's own geometry separately during integration.

How the runs went:
- Import and all eight runs went through the canonical checked runner (`0a3e036a…`), each with a finite timeout, a
  unique log and `--expect "CAPTURE PASS"`. Every run was CHECKED_RUN PASS, exit 0, with no ERROR, SCRIPT ERROR or parse
  line.
- Each run printed only the two exit-leak WARNINGs, the same as in the v15 controls.
- After the runs, 1760/1760 commit files are byte-identical. The only additions are Godot import products.

Measure tool result: PASS.
- The v15 control reproduced all four root-reviewed v15 captures byte for byte.
- The v16 no-sprite frames equal the control's.
- The v16 PNG over the no-sprite frame equals each capture.
- Captures differ from v15 only inside the sprite alpha (155 px).
- 1590/1590 sprite px, 0 off-palette, crown y211, sole y271, bbox x283–328.
- 0 companion overlap; HUD zh/en as requested.

Disclosure: the first v16 capture run used longer names whose absolute paths reached 253–265 characters (MAX_PATH 260).
Those 8 files, created by this session minutes earlier, were deleted and the runs were repeated with the shorter
`cap-ref160b823` label. Both runs passed; only the second is delivered.

## Visual review at game size and limits

These are my own judgements from the actual captures (zoomed crops looked at outside the repo). They are not approval.

Better:
- The boots read as boots, not flat blocks. There is a darker shaft back, a lit front that bends over the instep to the
  toe, a mid foot side, a heel, and a dark sole.
- On both paving floors the shoe's shape (shaft, ankle, instep slope, toe) is visible at 1×, without extra width.
- The canister is back: a small grey bottle on the pack's back corner, outlined, mostly mid and dark steel.
- The pack has a soft bulge under the flap.

**Remaining limitation (not solved):**
- Inside the outskirts contact shadow, the boots' lowest rows still merge. The `L` sole and the `d` lower foot side sit
  near the shadow's value (~46). Only the upper foot (`n`/`D`) separates.
- With v15's lit base gone, the foot's bottom edge no longer reads in the shadow. The boot now reads as standing in a
  dark contact rather than outlined by a light band.
- The descriptive numbers go the wrong way, and I am not hiding that. For boots in the outskirts shadow:

  | | v15 | v16 |
  |---|---|---|
  | mean \|ΔL\| | 34.2 | 18.2 |
  | share with \|ΔL\| < 20 | 37.5% | 70.3% |

  Archive in-shadow share goes 17.2% → 57.8%.
- These numbers are descriptive only, as is the improvement on paving (outskirts on-paving share 18.6% → 53.5%
  closer to the floor, archive 14.0% → 18.6%). They decide nothing either way.

Other observations:
- On the archive's warm paving, the mid-leather `n` planes are close in hue to the floor. The outline carries the
  silhouette.
- The near boot's lit front plane is a diagonal run of `D` texels, inset from the outline. The root should judge whether
  at 1× it still reads as an edge light. By construction it never touches the outline.

Per the brief, this is the result of the one construction pass, not a new tuning loop. Planes alone did not solve the
in-shadow merge without either a lit base band (rejected) or a heavier/brighter boot (identity).

## Next action

The root inspects the v16 still and the four captures against v15.

If the in-shadow base is still unacceptable, the open choice belongs to the root or creator:
- accept a dark contact base as natural grounding, or
- allow one specific base treatment, for example a mid-value sole plane that is not a bright welt.

No further versions were made in this session.

## Not done

- No animation, runtime swap, `battle_arena.gd` edit, or default change.
- No Game Bible, ledger, index, Site or progress edit.
- No commit or push.
- No GUI Pixelorama Save As or reopen.
- No approval or production claim.
