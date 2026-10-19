# HANDOFF: female complete-exploration pilot v02 (unscored, UNAPPROVED, opt-in only)

Base: `d9a86d5` in the isolated `cl-management` checkout. Hosts were synced from canonical C `21c325e`. Nothing was committed, staged or pushed. No shared ledger, Site or account was touched. No new art, directions, turn animation or battle animation was made. Default behaviour is unchanged.

Global stop-file check: no stop file was found in the registry, workflow, `outputs/` or `work/`, so production continued.

## What was built

The pilot is enabled with `-- --female-complete-exploration-pilot`, and only for the `protagonist-female` actor.

- **Driver:** `game/scripts/fexp/…_driver_pilot-v01_20261019-184900-f2c0a7e1.gd` (text-lf `e468c1f9`).
- **Package:** everything lives under `game/`, with no `res://../outputs` dependency.
  - Model copies:
    - EAST v03 (`f526e06e`) and WEST v01 (`2ca7cee6`) are identical to their sources except the single `SOURCE` line, which now points at the copied PXO under `res://assets/fexp/`. The builder asserts this.
    - NORTH v06 is copied verbatim (`1f25c2aa`).
  - SOUTH v10r1: the pure inner classes (`IM`, `PartCompositor`, `Loco`, `Loco7`, `Comp9`, `Comp10`, `Loco10`, `Loco10r1`) were extracted verbatim from the SceneTree chain into `…south-model_extracted…gd` (`80bfd5e1`).
  - The hash chain is resolved at build time into `game/data/fexp/…south-runtime_v01…json`. The 1.58 s `_prepare` now runs only in the bake; attach takes 79 ms.
  - Assets: 48 idle-four PNGs and 2 PXOs in `game/assets/fexp/`.
  - Package JSON: `game/data/fexp/…package_v01…json`.
- **Loader branch:** `exploration_sprite_set_pilot.gd` gets a 6-line branch behind its own flag. The existing 16-frame validation and registries are untouched.
- **Host hooks:** the only host change is a presentation-only `_step_sprite_pilot(delta, from)` call. It runs after movement, collision and clamp, and before the city silhouette copy. It is in `scifi_exploration_area.gd`, `survey_annex.gd` and the Chicago v02 scene. The pre-sync workspace copies of the first two are kept in `outputs/fcx-v02/preserved-pre-c-sync/`.
  - Syncing from C brought in the themed-music selector script that C's hosts preload.
- **Behaviour as implemented:**
  - Physical facing is immediate.
  - When facing changes, the incoming model is reset to its exact constructed rest at the current floor pin, then advanced from the actual displacement.
  - Re-pressing the same facing keeps the live model.
  - The opposite-intent placeholder is never used.
  - The SOUTH shadow is a separate child sprite.
  - Live poses are cached by every state field the renderer reads, capped at 192 per direction. After the cap, a persistent `ImageTexture.update` is used.
  - At rest the 12-phase idle plays from phase 0.

## Evidence (checked runner; every log clean, all PASS; in `outputs/fcx-v02/`)

1. **SOUTH bake** (`south-bake-report`):
   - 144 compose rows (128 per-px rows plus 16 keyframes, image and shadow) match exactly.
   - 720 loco ticks at 30, 60 and mixed frame rates match exactly.
   - neutral == v8, and the v8 hash matches.
   - The first run failed with a parse error. Its log is kept as `south-bake-log_v01`; the passing run is `v01r2`.
2. **Driver check** (`driver-check-report`):
   - Default-off returns null with 0 package reads, and other actors are not attached.
   - The whole set loads (267 ms, about 6.3 MB of static memory).
   - For all four directions at 30, 60 and mixed rates: start, run, stop, then the first idle frame equals idle phase 00 RGBA exactly. Stop length to rest in ticks is S 12/6/12, W 14/7/12, N 16/8/14, E 14/7/12 (60 / 30 / mixed).
   - Pivot offset and 0.5 scale are exact. The shadow shows only for SOUTH.
   - Turns between all axis pairs, including reversals, work with no placeholder.
   - Same-facing re-press during a stop goes stop → run with no reset.
   - Blocked movement stops.
   - Diagonals use dominant-axis facing.
   - Every cache hit was compared against a fresh render (RGBA oracle): 0 mismatches.
3. **Actual normal game** (real host `_process`, action input). Reports are `actual-*_report`; MP4s are 1x and AVIs are kept alongside.
   - Runs: city bright EN at 60 fps (movie), annex room 2 ZH at 30 fps (movie), city mixed frame times, plus flag-off city 60 and annex 30.
   - Each run covers idle, east start/run/stop, re-press, reversal to west, north, south, NE and SW diagonals, and blocked pushing (189 blocked frames in the city, 49 in the annex).
   - The mode flag and the visible pose agree on every frame. There are 0 placeholder frames, and the final state is the idle loop.
   - **Movement parity:** flag-on and flag-off positions are identical on every frame (641/641 and 326/326).
   - Contact strips `*-contact-strip_*.png` show all four directions rendering in both scenes.
4. **Hash receipt:** `hash-receipt_v02_…json` (text-lf `583c1389`) binds every script, data file, log, report, MP4, PNG and asset.

## Cost (measured, not readiness)

At 60 fps in the actual city run, host process time is p50 12.6 ms and p95 19.0 ms with the pilot, against 4.3 / 4.5 ms with it off.

- A live render miss costs about 9 ms for E and S, 12–13 ms for N (max 18.7) and about 2 ms for W.
- The cache filled to 290 entries, about 24.9 MB estimated, with only 49 hits in 641 frames.
- The cache belongs to each driver instance, so it is rebuilt on every scene entry.

So 60 fps is **not** met during live N/E/S motion. One bounded optimisation pass is still available and has not been used. Preferred option: a cache shared across scenes, warmed with the 128 steady phases per direction at attach, verified with the RGBA oracle.

## Remaining gaps (not done; do not treat as passed)

- **Export:** no export templates are installed, so there was no PCK or export launch. Raw PNG/PXO/JSON are loaded with `Image.load_from_file` / `ZIPReader` and `globalize_path`. An export would need an `include_filter` for these files and buffer-based loading. The package is only self-contained as a source tree under `game/`.
- **Default-off capture parity:** not checked against C bytes. Default-off was shown through movement parity in the same build and the null and `has_method` guards.
- **Chicago:** the hook is added but was not run in the actual game.
- **Scene lighting:** the annex room 2 run is the scene used earlier as "dark"; whether it is actually dark was not re-measured.
- **Mixed-rate timing:** the mixed-rate actual run's process_ms includes the injected delay, so it is not a cost measurement.
- **Turns:** the instant turn is not an authored turn, and no foot identity carries across 90 degrees.
- **Approval:** no art, motion, fluidity, default-integration or full-sprite approval is claimed.
