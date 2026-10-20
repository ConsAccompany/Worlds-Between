# Patrol machine battle animation v01 — QA note (UNAPPROVED technical candidate; off by default)

Task `content.enemy.patrol.battle-animation`. Producer: Claude. Worktree base `e600241`, uncommitted. Session ran 19:36–19:52 local on 2026-10-19.
Status: a production candidate with an optional hookup. It is **not** creator-approved, not a default, not an adoption and not a full-sprite claim. Root inspection is pending.

## What exists
- **Contract:** `game/assets/enemies/patrol-anim-v01/*_battle-animation-contract_*.md`. It covers a 112x72 cell, pivot (56,66), 7 layers, 6 states and 24 frames. The identity comes from the selected Patrol native static (reverse-knee walker, sandstone egg hull, visor head with a teal lens). No Sentry pixels are used. There is a short shock prod and no claw.
- **Builder:** `*_battle-animation-builder_*.py`. It is deterministic integer rig poses drawn with Pillow ImageDraw, with no generated, traced or random pixels. It rebuilds twice and compares; `--check` compares against the files on disk.
- **Package (10 files, sha256-bytes; JSON uses LF):** the strip PNG `e91f4373…`, the layered PXO `61af851a…` (24 frames × 7 layers, native tags and durations), 6 ORAs (one representative frame per state), the runtime package JSON `075a438e…` and the manifest `a54b8fa3…`. The manifest lists every artefact hash.
- **Loader** (`*_battle-animation-loader_*.gd`, sha256 `fe4e95f0…`): validates the path prefix, size cap, schema, enemy, every value type and range, the frame indices, the timed states, the front states, the strip location and the strip size against cell×frame_count. Any defect returns `{}` and keeps the placeholder block.
- **Hook** in `game/scripts/battle_arena.gd` (HEAD `7f623352…` → `799308e2…`, +43/−1):
  - the `--patrol-battle-animation-pilot` flag, plus `patrol_animation_override` / `patrol_animation_package_override`;
  - the loader is `load()`ed only when the flag is on and the enemy is the Patrol, so off-path load is zero;
  - a `windup_phases` branch spreads the 3 windup frames evenly over the real 0.65 s windup. The Sentry has no such key, so it keeps its exact two-half logic;
  - no stat, AI, range, timer or position code was touched. The Patrol stats are asserted as 64/12/55/0.65/1.35.

## Evidence (windowed Godot 4.7.2, checked runner, isolated APPDATA/LOCALAPPDATA)
Harness `tools/*_battle-animation-harness_*.gd` (`3648609a…`). The final run r3 printed `PATROL_ANIM_HARNESS OK sim=20 loader=26 captures=16 parity=32`, with checked-run PASS in 11.8 s and no diagnostic markers. Report: `cap/*harness-report_*.json`.
- **Simulation parity:** the HEAD script (compiled in memory from `git show HEAD:`) is compared with this tree under off, patrol-on, sentry-on and both-on, for both Patrol and Sentry battles. Each run steps at a fixed 1/60 s with auto mode and hashes a per-tick combat tuple (enemy x/hp/windup/cooldown/attacks/target/finished, plus each fighter's x, cooldown and hp). **All 20 digests equal HEAD.**
  - Plain battles end before the Patrol ever attacks (92 ticks).
  - So a second pass applies one identical HP hold to every variant until 3 enemy strikes. That covers 398 ticks for the Patrol and 333 for the Sentry, including windup, strike and party damage.
- **Pixel parity at 640x360 in EN and ZH:** the default Patrol, the default Sentry, Sentry-on, and Sentry-on with the Patrol flag also on are each compared against the HEAD script across idle, windup, hit and defeat. **All 32 are byte-identical to HEAD.** This shows the Sentry flag is independent and the default is unchanged.
- **Loader / fallback: 26/26 checks pass.**
  - 5 bad paths are rejected, including a traversal path and `user://`.
  - 15 single-field type/range mutations are rejected, plus a strip/cell size mismatch.
  - In battle, a missing package leaves the placeholder and the battle still steps.
  - Mutations are written to a temporary file in the package directory and deleted afterwards; none was left behind.
- **Actual 1x captures (EN and ZH):** idle, move, windup a/b/c, strike, hit and defeat (16 files); default-off Patrol idle; Sentry-on idle. All are 640x360 viewport captures in a normal battle scene with the real HUD.
- **Normal-speed loop** (real engine frames and deltas, EN): 1377 frames over 5.8 s, with first-frame captures of move, windup, strike, hit and defeat.
  - For this loop only, the Patrol's HP is held at 40+ until it has struck twice (the auto party otherwise destroys it first). This is labelled `hpHeldUntilTwoStrikes`.
  - Measured transitions: windup 10→11→12 at 1.545 / 1.775 / 1.992 s (about 0.22 s per phase), strike 13→14→15 at 0.11 s, hit 16→18 at about 0.09 s, defeat 19→23 at 0.15 s, holding on 23.

## Native format vs app (reported separately)
- **Format parity (builder, in memory before writing):** every PXO cel equals the builder layer; each PXO composite equals the strip cell; the durations and tags match; each ORA's stack order, layers and merged image are exact. `--check` reports `PATROL_ANIM_CHECK OK files=10`.
- **Pixelorama 1.2.3 CLI** (`tools/*_app-export-check_*.py`, temp copy, report `*_app-export-report_*.json`):
  - The `--split-layers` export is **168/168 cels byte-exact**.
  - The flattened export is **not exact**: it differs by ±1 channel unit only where the translucent shadow (alpha 110) or smoke (alpha 200) composite. This is the known app rounding.
  - The app also emitted **10 shader `ERROR` diagnostics**, so `cleanAppSuccess=false`.
  - No GUI reopen or Save As was performed or claimed.

## Defects fixed in this pass (one authored pass, then concrete repairs)
1. Defeat frames 22–23: the visor head dropped through the near leg. Fixed by splaying the feet back and carrying the head forward.
2. Defeat frames 21–22: the IK pushed a knee below the floor. Fixed by clamping the knee to row 61 or above.
3. Evidence: the harness r1 failed honestly ("never showed windup/strike") because the party won first. The log is kept. Fixed in the evidence loop only, as described above.

## Limitations / open
- The art is unapproved. Smoothness and pacing need the creator's normal-speed review; frame counts and timings are not proof.
- The Patrol is about 50 px tall against heroes of about 60 px. That is deliberate (a compact machine) but needs the creator's eye.
- During windup the existing arena tint (1, 0.70, 0.66) and red ring wash the sprite strongly red. This is unchanged shared behaviour, the same as for the Sentry.
- During cooldown the enemy keeps walking, so the strike/hit frames can play while `enemy_x` changes. This is existing logic, the same as the Sentry; no foot-lock is applied outside the move state.
- The hit flinch re-triggers under party combos, as it does for the Sentry.
- The translucent shadow and smoke make the flattened app export inexact (see above). Making them binary alpha would trade away the soft contact shadow.
- No PCK/export build was run for this candidate. The loader `.gd` and JSON live under `game/assets/…`; an export filter that excludes them would fall back cleanly, but this is unverified. No native EXE claim.
- The Godot `--import` also rewrote 447 tracked `.import` files' line endings and created 268 sidecars outside scope. All were restored or removed. The only remaining changes are `battle_arena.gd`, the package directory (including its own `.png.import` and `.gd.uid`), the two tools and these outputs.
