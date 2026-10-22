# Ji Cheng combat static + eight source actions: jcombat32 producer QA (UNAPPROVED)

- Base and tested revision: `f22556c7d36b7f7db127f8a73568ec8a36c02941`. All files are new and uncommitted. No tracked file was modified.
- Tool: `tools/rpg-2-star-ocean-the-second_ji-cheng_combat-static-and-actions-author_unapproved-jcombat32-v01_20261021-220632-060661dc.py`, sha256-text-lf-v1 (CRLF->LF) `f9200c7b98779eb8163954f5227e91681463e1ebce5b1866e8d76d250be4ba58`.
- Status: technical source only. Art, motion, scale and default adoption are **not approved**. The source concept is UNAPPROVED. Nothing is wired into the runtime, and the default, mechanics, input, saves, collision, ledger, Bible and registry are unchanged.

## Deliverable
- 23 poses covering idle (2), move (4), guard (2), attack (4), dodge (2), skill (4), hit (2) and defeat (3), plus the combat static (`battle-still`, which uses the idle-a pixels). Each pose ships as a native 136x144 PNG, a layered ORA and an editable PXO, with 10 role layers: coat-back, arm-back, leg-back, leg-front, torso, head, book, arm-front, magnifier and fx.
- The runtime sheet uses 6 columns. The manifest follows `worlds-between.combat-sprite-set/1`: 136x144 cells, pivot 64/136, authored facing right, scale 0.5, display proportion 0.65 and 30 ticks/s. Action totals match hsc19: idle 28, attack 13, move 12, guard 14, dodge 9, skill 14, hit 8, defeat 9. There is no victory action.
- The index is member-only: `sets = {"ji-cheng": ...}`, with no hero key and no appearance key.
- The author manifest records provenance, per-pose rig parameters and hashes. The package in `game/data/jcombat32` (sha256):
  - author-manifest `ce6f6b4209dccdc633b3b5dda9d8d2ca7f8b50bd4c99fd561fd5ff89cea72d34`
  - runtime-index `9677d8e36cf080031d95610fe0d8b51ce9ad2c5ed49c3e7785da0dc4a0caf9e0`
  - spritesheet-manifest `aa49f9432145707290c989df9332ee9b075108c48f764fd38b7e83f3c272ff28`
  - spritesheet PNG `2093f9022fc80c9d690fd9b58c7663bba3808bf1b2dd72f70b2d983f9a8fbdaf`

## Identity and mechanics as authored
- The palette is a literal copy of the jexplore31 PAL and is checked against that module at check time. The rig architecture comes from lcombat29, but this is not a Liang recolour: idle silhouette IoU is checked to be below 0.85 against the heroine, male, Zhao and Liang sets. The old 32x48 prototype was not read.
- Costume: blue-black shoulder bob with three jagged silver tips, ink-green open long coat with an uneven hem and a ragged rear point, cream panel, grey rolled elbow lining, black high collar with a brass buckle, leather harness and belt, silver vials and a pouch, thigh strap and pouch, and buckled boots.
- Props: a brass folding magnifier in the near (right) hand and a leather book in the far (left) hand.
- Attack (`attack_range` 100, damage 12, read only): the magnifier lens-flare lance appears on **attack frame 0, tick 0**, matching the immediate `_try_attack`. No timing or damage was changed.
- Skill Fault-Line Recall (断层回读): the book opens, the magnifier reads over the page, a fault-line trace appears, then recall brackets and a paused ring appear as the book closes. This illustrates the existing windup/cooldown delay and adds no mechanics.
- Guard: the closed book is raised cover-out in front of the face.

## Checks (actual results)
- `build`: PASS 217/217. Builds are deterministic, and the build refuses to run when a gate fails.
- `check`: PASS 296/296. This includes byte equality between the on-disk files and a fresh rebuild.
- `check --pixelorama <Pixelorama 1.2.3>`: PASS 297/297.
  - Flat export: all 24 PXOs reopen and export pixel-equal (24/24).
  - Split-layer export matches exactly: attack-strike 10/10, skill-fault 10/10, still 9/9, guard-hold 9/9, defeat-down 9/9. Only non-empty layers are counted, and fx is empty on the last three.
- **Diagnostics disclosed:** every one of the 29 native runs printed `ERROR: Condition "!actions.custom_samplers.has(function->arguments[j].tex_builtin)" is true. Continuing.`. This is a Pixelorama shader message, not a SCRIPT ERROR. I make no clean-application or GUI Save As claim (`guiSaveAsVerified: false`).
- Reports:
  - `outputs/jcombat32/...source-check-report_...-92b389e9.json`
  - `outputs/jcombat32/...source-check-report-pixelorama_...-7a156195.json`
  - `...file-list_...-13304dfb.json`
- No Godot run was performed. Runtime and arena validation belong to the root.

## Limitations and open items (not refined, per MVP priority)
- Authored facing right shows her RIGHT side. The shaved LEFT temple is on the far side, so it reads only as a pale undercut wrap with razor lines at the back of the head and the brass drop-earring glint below it.
- The rig uses the shared side-view proportions. The face is small at native scale, and the hair reads as a dark cap at 1x. Hands are simple glove discs.
- There is a single preview pass with one fix round: curtain moved behind the cheek, silver tips moved off the chin, the cream panel narrowed, and the recall fx moved inside the cell. No normal-speed motion review was done.
- Next for the root: use the existing independent composition/runtime validators and the member arena probe with the explicit jcombat32 index, at normal speed in bright and dark arenas, in EN and ZH.
