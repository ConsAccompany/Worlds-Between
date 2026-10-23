# M8 city integration bounded repair — Claude producer report (m8reg63)

Base `ababe587c3f3504a592dca11e7f966ee946955ec` (clean at start). Producer: Claude Code (Opus 5.5). Hermes reviews independently.
No runtime, default, asset, viewport, canon, ledger, Bible, registry, index or Git commit changes. Full `qa.validation.pre-playtest-regression` stays TODO, zero points. No art/motion approval is claimed.

## Files changed
- `game/tests/m8_city_integration_smoke.gd` (original sha256 `4cc0e731…a477a42`, final sha256 `3a73e14cdd95d2b802407dc2dd0902c9e38a4201d8b4868e00d64bee488d3b81`)
- New producer-only files under `work/m8reg63/`: `trace_sources.py` (read-only source tracer), `run_checks.py` (checked-runner wrapper), run logs and summaries, `renders-20261023-202707/`, this report. No extra Godot helper was added.

## Hypotheses (ranked) and verdict
1. **Stale 32x48 test (CONFIRMED).** The test still required legacy 32x48, scale 1 and offset −20 frames. The ordinary game now uses creator-authorized default drivers (art and motion still unapproved):
   - male: `mpath24 …explore-driver` `DEFAULT_ADOPTED := true` (2026-10-21), reached through `exploration_sprite_set_pilot.attach` → `male_enabled()`.
   - female: `hsea18 heroine-normal-default` `CREATOR_DEFAULT_ADOPTED := true` → `hsea09` Sea distance driver `attach_registry(front17)`.
   - Liang: `lpath30` config `DEFAULT_ADOPTED := true` → `attach_liang_npc` (zpath27 behaviour).
   All three set `scale = 0.5` on 80x112 frames, so line 69 failed on the first actor.
2. **Wrong active source: rejected.** The pinned registry bytes, driver script and set id match on both routes and after save reload.
3. **Scale, pivot or direction defect: rejected.** Scale is 0.5 and filtering is nearest. Pivot [40,104] puts the floor line 1.00 logical px below the node, matching `FLOOR_DROP_LOGICAL`. Idle soles end on row 103. The displayed idle body is 48 logical px. Each of the four directions draws its own walk and idle frames. No runtime defect was found, so no scope expansion is proposed.

## Traced active sources (`python3 -I work/m8reg63/trace_sources.py`)
| actor | registry sha256 | set id | density / frame / pivot | idle / walk frames per dir |
|---|---|---|---|---|
| protagonist-male | `e156bbc344795b7c21300dabcc9f060bd58a8bd856aec0cf3f937f170fb3290c` | hero-male-exploration-source-20261021-162551-6e3b1a7d | 2 / 80x112 / 40,104 | 4 / 12 |
| protagonist-female | `a0c6eeb745cc4116beb3ca402047c120cfd70922f0128f9b11c4cbee6b7805f6` (= hsea18 pin) | hero-female-exploration-source-20261020-222654-1478e147 | 2 / 80x112 / 40,104 | 1 (+breathing) / 12 |
| liang-xu | `99d8fa23cc0ce28dd5dbc004f5f5044cc59a619d052dbe21cc7290c13ab2be91` | liang-xu-exploration-source-20261021-194350-3acdbd6e | 2 / 80x112 / 40,104 | 4 / 12 |

## Test changes (no opt-in override is set anywhere)
- **Source identity predicate:** checks the driver is a child of the sprite, the exact driver script path, the pinned registry sha256, the set id via the production `load_registry` and `load_set`, the set id on the driver, and that the drawn texture belongs to that set.
- **Geometry predicate:** checks an 80x112 frame, scale (0.5, 0.5), nearest filtering, and a floor line exactly 1 logical px below the node with x centred. Contract values are pinned literals, not read from the code under test. For idle frames it also checks that soles end at the pivot row and the displayed body is 48 ± 0.5 logical px.
- **Facing predicate:** checks the driver's state facing and that the texture is in that facing's walk or idle clip (plus the heroine's breathing clip for idle).
- **Real input per direction (S, N, W, E):** walk must show on the first moving tick, every walk tick must actually move, and after release plus 30 ticks the driver must be in `idle` with that facing's idle frame and idle geometry. `_tick` advances the driver clock before the host, matching `process_priority -1`.
- **Liang:** `LiangConfig.npc_attached`, source identity, idle geometry and south idle.
- **Kept invariants:** hotspot walking, west-plaza block, walk to Liang, dialogue open, plus new checks that the panel and invite button are visible and enabled before the invite and that Liang and his label are visible before it. Also kept: NPC and label hide together, valid save at the exact position, and the reloaded hero keeps the same active driver, set and geometry (new). Legacy (82,260)→(82,203.5) recovery, standability and world-map return are unchanged.
- **Kept legacy assertion:** the 32x48 idle and walk banks remain intact as the whole-package refusal fallback.
- **Manifest `canvas`:** now records the actual captured viewport image size (1280x720) instead of the hard-coded [640,360]. The viewport itself is unchanged.

## Negative controls (inline mutate → same predicate must reject → revert → must re-accept)
These run on every execution, on both routes:
- `M8_NEGATIVE_SOURCE_REJECTED`: Liang's south idle texture (same 80x112 size) on the hero → "drawn texture is not from the active set".
- `M8_NEGATIVE_SCALE_REJECTED`: scale (1,1) → rejected.
- `M8_NEGATIVE_PIVOT_REJECTED`: legacy offset (0,−20) → floor line 14.00 px → rejected.
- `M8_NEGATIVE_DIRECTION_REJECTED`: opposite facing's same-index walk frame, ×4 directions → rejected.
Final counts per run: SOURCE 2, SCALE 2, PIVOT 2, DIRECTION 8.

## Runs (checked runner `tools/…godot_checked-runner_v01_20261018-203400-f74ac6d1.py`, 120 s, Dummy audio, marker `M8_CITY_INTEGRATION_OK`)
Command: `python3 -I work/m8reg63/run_checks.py headless|xvfb`. The xvfb run uses `xvfb-run -a … --rendering-driver opengl3` with `WB_CITY_EVIDENCE_DIR=work/m8reg63/renders-<stamp>`.
1. `headless-20261023-202612.log` — **FAILED (preserved):** `walk continues female south`. The driver was in `settle` with `actual_distance 0`, meaning the heroine walked about 12 px south of spawn (340,253) and hit the plaza edge on the 6th tick. Male had silently "passed" that tick because its stop bridge starts on a walk frame. Fix: 1+3 ticks per press, with every tick required to move. This was a test-geometry error, not a runtime defect.
2. `headless-20261023-202649.log` — passed (verbose state text in messages; later trimmed).
3. `headless-20261023-202704.log` / `-summary.json` — **PASS**, test sha256 `3a73e14c…3b81`, no diagnostics.
4. `xvfb-20261023-202707.log` / `-summary.json` — **PASS**. 10 renders (5 per route: 4 directions + recruited) and the manifest are hashed in the summary. I looked at male south (zh) and female west (en): both actors stand on the plaza at the expected size, Liang is visible, and labels are in the correct language. This is only a visual check that the renders are sane, not art approval.

Original RED (coordinator): `work/m8reg63/red-original.log`, `CITY_INTEGRATION_FAILED: native pixel actor male` at line 69.

## Limitations
- Inline negatives mutate live sprite properties. They do not run separate mutated-script processes. The coordinator's planned independent negatives are still needed.
- The release check observes the settled idle after 30 ticks (0.5 s). Intermediate stop-bridge frames are not individually asserted.
- I did not run M7, M1, navigation or re-entry; those are coordinator-owned.
- The pivot (40,104) and frame (80,112) are pinned once for all three sets. A future set with a different contract must update the test deliberately.
