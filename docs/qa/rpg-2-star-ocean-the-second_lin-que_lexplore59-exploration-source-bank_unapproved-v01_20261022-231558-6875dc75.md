# Lin Que lexplore59 exploration source bank (UNAPPROVED technical source)

Run `20261022-231558-6875dc75`, base `1c5793224c2d5b77f2dc9fc19b92cefff15b0ec9`. Tasks: `content.char.lin-que.idle-anim`,
`walk-south/west/north/east`. This is a production source bank. It carries no art, motion, fluidity or default approval.
The Lin statics it starts from are UNAPPROVED.

## Method
- Tool: `tools/rpg-2-star-ocean-the-second_lin-que_exploration-source-author_unapproved-lexplore59-v01_20261022-231558-6875dc75.py` (~170 lines).
  It is a thin adapter over the frozen jexplore39 Jiang author. That author's renderer, stop bridges, contact report, source checks
  and serializers are reused without changes. The adapter rebinds, in memory only: actor/paths/run/ZIP date, ROLES/PXO_LAYERS
  (11 Lin roles), PAL/RGB/INV, a DARK map that covers every Lin key, HEAD=(face,hair,goggles),
  TORSO=(cape,coat,belt,firearm,scarf), neutral PNG + PXO/ORA pins, and `load_neutral` (Lin `draw(d)` must recompose to the
  exact static PNG). It rewrites the source-manifest metadata (task ids, inputs, tool, limitations) for Lin. Check labels
  are relabelled.
- Real geometry fix: `FAR_BASE = 3`. The far toe in Lin's west and east statics sits 3 texels ahead of the near toe; Jiang's was 2.
  With Jiang's value, the side stop bridges failed at s2 -> idle f00 (far foot slipped 1 texel). That first build was
  deleted (only its own new outputs) and rebuilt.
- No Jiang or Lin static file was modified. No Git, ledger or registry changes.

## Outputs
- `outputs/lexplore59/`: 164 independent PNGs in `png/` (per direction: static, idle f00-f03, walk p00-p11, 12x2 stop
  intermediates), 4 PXO files (41 frames each, far-limbs + 11 roles + guides, tags idle/walk/stop-pNN), 4 static-layer ORA
  files, a source manifest, a file list and a check result.
- `game/data/lexplore59/`: a standard `exploration-sprite-set.v1` (idle+walk only), a registry (lin-que only), the
  `exploration-stop-transition.supplemental.v1` file (endpoints k0/k1 refs, intermediates k1/3, 2/3) and byte-identical
  PNG copies. Not adopted by anything; `runtime_default: false`.

## Commands and results
`python -X utf8 -I <tool> build` then `... check`. Both exit 0: REBUILD 341/341, DETERMINISTIC True, SOURCE 52/52,
neutral pins exact before and after, RESULT PASS.

| dir | walk slip @40ms (src) | 60fps planted excursion (src) | flight phases | stop grounded slip |
|---|---|---|---|---|
| south | 11.2 (in place: residual, NOT slip-free) | n/a | 4,5,10,11 | 0 |
| west | 0.8 (<=1 bound kept) | 10.667 (frame hold, disclosed) | 4,5,10,11 | 0 |
| north | 11.2 (in place: residual, NOT slip-free) | n/a | 4,5,10,11 | 0 |
| east | 0.8 (<=1 bound kept) | 10.667 (frame hold, disclosed) | 4,5,10,11 | 0 |

Static and idle f00 match the existing Lin static PNG bytes exactly in all 4 directions. Every bridge is [walk p, s1, s2, idle f00].

## Limitations / remaining
- Side gait is the inherited jog-like stride with 2 flight phases per step. Side far leg and far arm are darkened copies of the near
  limb; the static far-leg texels are not kept in walk frames.
- Cape and scarf only ride the torso bob/settle. No secondary follow-through was added. No visual review was done in this batch.
- Not run: Pixelorama round-trip, Godot import/fit/captures, normal-speed movie (coordinator-owned). The generic loader goes to
  idle immediately, so supplemental stop playback is not demonstrated.
