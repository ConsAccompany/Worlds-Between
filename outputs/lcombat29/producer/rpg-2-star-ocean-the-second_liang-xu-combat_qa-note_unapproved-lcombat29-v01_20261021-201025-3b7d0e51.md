# Liang Xu combat static + eight source actions — lcombat29 v01 producer QA note (UNAPPROVED)

Status: this is a production source package only. Art and motion are NOT approved. It is NOT a default and the runtime is NOT wired.
The coordinator owns the ledger tasks and did not receive updates from this run. This run made no ledger, Bible, registry, runtime,
shared-validator, Git index, commit or account edits.

- Base revision: 96e1a1a (worktree `work/needle29/cl-lcombat`). Author tool:
  `tools/rpg-2-star-ocean-the-second_liang-xu_combat-static-and-actions-author_unapproved-lcombat29-v01_20261021-201025-efc98984.py`,
  sha256-text-lf-v1 (CRLF->LF) `016782559277330b99b08da3122187213f5644bd4cf489fcaea4115faf8f4c70`. For binary hashes, see the author manifest
  and `outputs/lcombat29/...file-list...-f8fa2107.json`.
- Architecture: the zcombat26 rig, raster, ORA code and gate set, plus the established PXO writer (female south-run v06 `make_pxo`).
  Liang's costume, body, signature tool and fx are newly authored. No handgun, knife or tablet was copied from Zhao or the male set.
  A gate checks that the Zhao gun/jacket RGB and the male scarf/coat/leather RGB are absent.
- Palette: a literal copy of the lexplore28 author PAL (the Liang south pilot named ramps). At check time a gate imports the lexplore28
  module and compares the key/RGB lists. They are equal.
- Identity (neutral prose): a tactical mentor aged 46. Dark hair is pinned up in a top-knot with a copper pin, and a silver streak sweeps
  back over the near (right) temple. The character has a navy high collar, copper placket, studs and buckle, and a split graphite long
  coat: a side panel to the shin plus a rear vent tail that swings. The folding tactical board is in the far (left) hand, as in the
  lexplore28 east view. Age cues are a heavy brow and a cheek line. References: lexplore28 east static (`...-6d681674.png`) and the
  character sheet `outputs/...liang-xu_character-sheet_v01_20261013-153556-c7630671.png` (a concept, not an approval).
- Mechanics read (unchanged):
  - `app_state.gd` MEMBER_DEFS liang-xu: attack_damage 16, attack_range 65.0, so the attack is close range.
  - `battle_arena.gd` `_try_attack`: damage applies immediately, cooldown 0.43 s.
  - `_use_skill`: energy 16, cooldown 2.2 s; allies get `command=focus` and `boost += 4*rank` ("Tactical Calibration").
- Attack: an edge-first strike with the folded board. The impact burst is attack frame 0 (tick 0), which matches the immediate damage.
  Follow-through swing and trail, fold back, recover. No timer or damage change.
- Guard: the board opens into an upright two-panel shield. Skill: board opens and is read, calibration grid projected, near-hand signal
  chevrons back toward the allies, copper link ticks as the board folds. Defeat ends kneeling with eyes shut and the board down.
- Contract: worlds-between.combat-sprite-set/1, 136x144 cell, pivot (64,136), right-facing, logical scale 0.5, display proportion
  "0.65", 30 tick/s, 6-column sheet with 23 cells. Per-action ticks equal heroine hsc19: idle 28, attack 13, move 12, guard 14, dodge 9,
  skill 14, hit 8, defeat 9. Character `{"member_id":"liang-xu"}`. The index has only the `liang-xu` key: no hero key and no appearance
  key. No victory poses.
- Files: 23 poses plus the battle still, each as a native PNG, a 9-layer ORA and a single-frame 9-layer PXO (`outputs/lcombat29`).
  The sheet, runtime manifest, member-only index and author manifest are in `game/data/lcombat29`; the sheet and manifests also have
  copies in outputs. Layers: coat-back, arm-back, leg-back, leg-front, torso, board, head, arm-front, fx.

## Commands (worktree root; PY = C:/Users/hkzha/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/python.exe)

    $PY -X utf8 -I tools/<tool>.py build                          -> LCOMBAT29 BUILD PASS 216/216
    $PY -X utf8 -I tools/<tool>.py check                          -> LCOMBAT29 CHECK PASS 295/295 (source-check-report ...-e827e947.json)
    $PY -X utf8 -I tools/<tool>.py check --pixelorama <repo>/work/tooling/pixelorama-1-2-3/Pixelorama-Windows-64bit/Pixelorama.exe
                                                                  -> LCOMBAT29 CHECK PASS 296/296 (source-check-report-pixelorama ...-56d710e9.json)

The build refuses to write when any source gate fails. An early failed build had already written files before that guard existed; I
deleted those files (this run's own new directories) and rebuilt. Gates cover:
- deterministic rebuild, on-disk bytes, lexplore28 palette equality
- binary alpha and declared palette, margins, grounded/airborne rows, limb stretch, full role layers
- PNG == composite == ORA merged == PXO cels, identity texels, absent foreign weapon colours
- consecutive frames differ by at least 60 texels, contract and tick schema, member-only index
- strike cue at tick 0 with the folded board tip at least 30 px ahead of the pelvis, follow-through order, guard shield, skill fx
  order, defeat
- sheet cells, silhouette IoU against the heroine (0.298), male mcombat22 (0.738) and Zhao zcombat26 (0.791) idles (< 0.85), names

Native Pixelorama 1.2.3 headless export:
- All 24 PXOs give a flat export exactly equal to their PNG (exit 0).
- Split-layer exports match every non-empty source layer exactly: still 8/8, attack-strike 9/9, guard-hold 8/8, skill-grid 9/9,
  defeat-down 8/8.
- **Disclosed diagnostic:** each run prints the known renderer line
  `ERROR: Condition "!actions.custom_samplers.has(function->arguments[j].tex_builtin)" is true. Continuing.`
  The native result is exact but not diagnostic-clean (not app-clean). No SCRIPT ERROR appeared. GUI Save As was not verified.

## Limitations

- These are authored rig poses, not hand-finished frames. Normal-speed motion review, the actual arena capture (root-owned) and
  creator review are still pending. I ran no Godot load. Independent validation is assigned to DeepSeek.
- The idle silhouette IoU against Zhao is 0.791, under the 0.85 gate but close, because both use the same rig proportions. Identity
  separation comes mainly from the long coat, top-knot, palette and board.
- The long coat reads skirt-like. The top-knot is small and the silver streak is a thin band at 136 px. The board in the far hand is
  layered above the torso, which approximates depth. Light comes from the upper left. All of these are cosmetic and deferred under the
  MVP rule.
