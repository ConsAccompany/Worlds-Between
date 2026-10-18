# Battle backdrop loader pilot: capability QA note (opt-in, TECHNICAL only)

2026-10-18. Base `0636b40` (equal to `origin/main` when this work started). This note covers one capability: the normal battle can load an existing tracked backdrop band, and it is off by default.

**Status.**
- **Capability:** done and tested in the normal runtime behind `-- --battle-backdrop-pilot`.
- **Art:** both bands used here are **UNAPPROVED candidate art** with art acceptance 0. Neither is the default, and nothing here approves or adopts any backdrop.
- **Scope:** no ledger, Bible, Site or meter file was edited. Default adoption is a separate content and approval decision.
- **Push:** not pushed.

## What changed

The only runtime file is `game/scripts/battle_arena.gd` (+80/−8 vs `0636b40`).

- **Switches.**
  - Off by default. `-- --battle-backdrop-pilot` or the static `battle_backdrop_override = 1` turns the loader on. `0` forces it off; `-1` (the default) follows the CLI flag, as `sentry_v2_override` does.
  - `-- --battle-backdrop-arena=<id>` or the static `battle_backdrop_arena_override` picks an arena directly. Today this is the only way to reach the archive band, because no battle starts in the archive.
  - The per-instance `battle_backdrop_path_override` only swaps the band file. Like the sentry switches, it never enables the pilot.
- **Data.** Two constants hold all the configuration.
  - `BATTLE_ARENA_BY_DESTINATION` maps the real destination IDs to arena IDs: `scifi.city` → `city-terrace`, `scifi.outskirts` → `outskirts`, `scifi.ruins` → `ruins`. The encounter already uses these destination IDs to choose the enemy.
  - `BATTLE_BACKDROP_BANDS` lists only the two **tracked** bands, `archive` and `outskirts`.
- **Loader (`_load_battle_backdrop`).** It runs once in `_ready`, after the sentry loader, and sets a status:
  - `off`: the flag is off.
  - `no_band`: the arena ID has no tracked band, or is invalid or empty.
  - `missing`: the file does not exist.
  - `unsupported`: the resource is not a texture, or is not an exact integer multiple of 640×212.
  - `loaded`: anything else. The band is shrunk nearest-neighbour from 1280×424 to the 640×212 logical play band (`Image.resize` with `INTERPOLATE_NEAREST`). Every logical pixel is the source texel (2x+1, 2y+1), with no blending; the check verified all 135,680 pixels of both bands. The band therefore shares the sprites' 640-logical pixel grid in the native 640×360 window and as 2×2 blocks at 1280×720.
- **Draw order.**
  - Without a band, `_draw` issues exactly the old geometric commands.
  - With a band, the old commands are replaced by one `draw_texture` at (0, 90). The band sits under the fighters and the enemy, and the HUD `CanvasLayer` (opaque header 0–90, footer 302–360) stays above it.
  - The battle has no camera, so the band is static in screen space. Feet stay on the existing 272 floor line.
- **Not ported (not requested):** contact shadows, the telegraph label outline, the prototype tint and any untracked band.
- **Unchanged:** no fighter or sentry art, timing, stats, AI, input or scene flow changed. `app_state.gd` is untouched.

### Why `AppState.battle_arena_id` is not used

That field does not exist at `0636b40`: `git log --all -S battle_arena_id` finds nothing. I did not add it, for two reasons:
- `app_state.gd` is shared, and two tracked checks list it as unchanged: the global-map v03r2 source check and the WDC annex default-layout evidence check.
- The battle already knows `AppState.current_destination_id`, the key the encounter itself uses.

The arena key is resolved in one function, `battle_backdrop_arena()`: static override, then the CLI arena argument, then the destination map. That function is the only place to change if the root later adds `AppState.battle_arena_id`.

## Source provenance (exact)

| Arena | Runtime band (tracked since `7553581`) | sha256-bytes | Made from |
| --- | --- | --- | --- |
| archive | `game/assets/environments/rpg-2-star-ocean-the-second_scifi-archive-battle-arena_runtime-band_m8-candidate_20261014-213622-14315e18.png`, 1280×424 | `c840e071e126510cf301e8deafde2d085c759415c00c57ba88140da12c916f4b` | concept `outputs/rpg-2-star-ocean-the-second_scifi-archive-battle-arena_visual-concept-unapproved_m8-v01_20261014-205826-ee2a7ca7.png` (sha256-bytes `dfef79fb…`), full-width 1672×554 crop at y = 140, Lanczos to 1280×424 |
| outskirts | `game/assets/environments/rpg-2-star-ocean-the-second_scifi-outskirts-battle-arena_runtime-band_m8-candidate_20261014-213622-14315e18.png`, 1280×424 | `feea6297f1e859c64daffe0771e1ac5beadaffb0595066944b3b473cff82a4aa` | concept `outputs/rpg-2-star-ocean-the-second_scifi-outskirts-battle-arena_visual-concept-unapproved_m8-v01_20261014-210110-99003219.png` (sha256-bytes `dbb619bf…`), same crop at y = 130 |

- **Tracked record.** The two bands entered Git in `7553581` as the "battle-v13-external-background-band" group of `outputs/rpg-2-star-ocean-the-second_chicago-v05-battle-v13_integration-selection-manifest_unapproved-v01_20261018-041551-66d3cb79.json`, which lists the same hashes.
- **Untracked lineage, read for provenance only.** The concept PNGs, the concept manifest v02 (`…battle-arenas_visual-concept-manifest_m8-v02_20261014-210701-65b33894.json`, status `concept_unapproved`, `assetAccepted: false`) and the 2026-10-14 crop-prep script (`game/tests/…battle-arena-candidate_runtime-crop-prep_m8-v01_20261014-213622-14315e18.gd`) exist only as untracked files in the primary checkout. I read them there; I did not copy them.
- **Generator.** The concept manifest does not record how the concepts were generated.
- **Primary prototype.** The primary checkout's dirty `battle_arena.gd` was read only to find these tracked asset paths. No code was copied from it.
- **Not used:** the city-terrace and ruins bands. They exist only as untracked files in the primary checkout, so no path to them is listed. Those arenas resolve to `no_band` and keep the geometric backdrop.

## Checks (all real windowed Godot 4.7.2 official runs)

**Setup.**
- Two isolated trees under `%TEMP%\bbp`, each imported with its own `APPDATA`:
  - **base:** a `git archive` of `0636b40`;
  - **candidate:** the same export with this `battle_arena.gd` (sha256-bytes `5b69823f…`, LF).
- Both tools run with `-s <absolute tools path>`, so they leave no file in `game/`. No import ran in the worktree, so it gained no `.godot` folder or `.uid` files.
- Every run below used one shared stamp, `20261018-144653-faa6ec0f`.

**Default parity** (`tools/…default-parity-capture-compare_…5a686c81.gd`). Each run renders 32 deterministic battle states: sentry/ruins and patrol/outskirts × zh/en × 1280×720 and native 640×360 × idle / wind-up / hit / defeat. The candidate runs compare pixel for pixel against the matching base run:

| Run | Compared against | Result |
| --- | --- | --- |
| candidate, no flag | base, no flag | 32/32 identical (0 differing pixels) |
| candidate, `--sentry-v2-pilot` | base, `--sentry-v2-pilot` | 32/32 identical; the Sentry code path is unchanged |
| candidate, `--battle-backdrop-pilot` (negative control) | base, no flag | all 16 patrol captures differ (≥ 63,907 px); all 16 sentry/ruins captures are identical (no band, so geometric) |

**Focused check** (`tools/…check-capture_…367f3344.gd`). Four runs:

| Mode (CLI args) | Passed |
| --- | --- |
| default (no flag) | 79/79 |
| `--battle-backdrop-pilot` | 79/79 |
| `--battle-backdrop-pilot --sentry-v2-pilot` | 89/89 |
| the same plus `--battle-backdrop-arena=archive` | 66/66 (the destination-mapping section is skipped in this mode by design) |

The four runs cover:
- **Normal path.** Battles open through `scifi_exploration_area._open_encounter()`, the real `change_scene_to_packed`, with only the CLI flags and no static override.
  - Without the flag: outskirts and ruins encounters are both `off`.
  - With the flag: outskirts is `loaded` (outskirts band); ruins is `no_band` (geometric); with the arena pick, both are `loaded` (archive band).
  - The sentry v2 sprite appears only with its own flag, and only on the sentry.
- **Combined flags.** With both flags, the outskirts patrol and the ruins sentry each play full-auto to the won result screen, and so does the archive-band sentry.
- **Selection.** 9 cases: every destination; arena picks archive, outskirts and ruins; the invalid keys `nope` and `../outskirts`; the placeholder `scifi.loop`. Override 0 beats an arena pick.
- **Band texture.** Each band's file sha matches the table, the source is 1280×424, the texture is 640×212, and every pixel is an exact nearest texel.
- **Fallback.** These all keep the geometric backdrop, and each renders pixel-identical to flag-off:
  - a missing file;
  - a tracked 1672×941 image (not a multiple of 640×212);
  - a non-texture resource (`battle_arena.tscn`);
  - the `ruins`, `city-terrace` and `nope` arenas.
- **Layering and cropping.** Checked in zh and en, at 640 and at 1280:
  - Header rows 0–89 and footer rows 302–359 are identical to flag-off.
  - Empty band columns equal the band texels exactly (1×1 blocks at 640, 2×2 at 1280).
  - Every fighter and the enemy is still drawn over the band.
  - The fighters (y 199–285) and the enemy sit inside the 90–302 play band.
  - The header labels and the footer console (feedback and help text) fit inside 640×360, and the console sits in the footer.
- **Gameplay trace.** For patrol and for sentry, 600 fixed steps (1/60 s) of full-auto combat ran in all four combinations of backdrop {0, 1} × sentry {0, 1}. The traces cover enemy x, HP, wind-up, cooldown, target and hit counts, feedback, and every fighter's x, HP, energy, cooldowns and action. They are identical within each enemy:
  - patrol `111930cccb48…`: 3 enemy hits, 41 party hits;
  - sentry `8e5307e31701…`: 4 enemy hits, 41 party hits.

**Captures.** Six actual 640×360 bilingual captures, in the evidence folder `outputs/battle-backdrop-v01_20261018-144653-faa6ec0f/`. All are wind-up states (paused, fixed layout) opened through the real encounter path. A rerun with an earlier stamp produced byte-identical PNGs.

| Case | zh | en |
| --- | --- | --- |
| outskirts / patrol, band `loaded` | `…outskirts-loaded-patrol-windup-zh-640_…png` (`28153f87…`) | `…-en-640_…png` (`31206617…`) |
| archive pick / sentry v2 + band `loaded` | `…archive-loaded-sentry-windup-zh-640_…png` (`5d296be6…`) | `…-en-640_…png` (`faebc1f2…`) |
| ruins / sentry v2, `no_band` (geometric fallback) | `…ruins-no_band-sentry-windup-zh-640_…png` (`a243bf28…`) | `…-en-640_…png` (`aac124ab…`) |

**Evidence files.**
- One capture manifest per check run (`…capture-manifest-<mode>_….json`). Each holds every check label, the gameplay trace hashes and the capture hashes.
- Five parity index JSONs in `parity/`, holding per-capture sha256 values and per-pixel compare rows. The 160 parity PNGs stayed in `%TEMP%` and are not committed.
- Nine run logs in `logs/`. They contain absolute temp paths.

## Limits and open points

- **Normal play today.** Only outskirts (patrol) battles show a band. Ruins (sentry) battles fall back to geometric, because no ruins band is tracked. No battle starts in the city or the archive; the archive band is reachable only through the arena pick.
- **1280×720 density.** At 1280×720 the band shows at 640-logical density (2×2 blocks) by design, not at its 1280×424 detail. The 2026-10-14 prototype drew it 1:1 to physical pixels instead.
- **Wind-up label.** Without the prototype's outline, the wind-up label sits directly on the band. It reads in these six captures, but its contrast was not measured.
- **Load cost.** One observation each: the first outskirts encounter logged `BATTLE_TRANSITION_MS` 21.14 with the flag against 3.62 without. The cost is the band load plus resize. It was not profiled further.
- **Steps to result.** The play-to-result step counts (87 / 140 / 116 steps) include a few real-time engine frames before the fixed-step loop, so they vary slightly from run to run: an earlier run gave 117 for the archive sentry. The bit-exact gameplay evidence is the 600-step paused trace, not these counts.
- **Not run:** windowed runs only, no headless run (`Image` access under the dummy renderer was not tested); no broad regression sweep (excluded by request); no clean-clone run beyond the `git archive` exports.
- **Existing art concern.** `docs/qa/rpg-2-star-ocean-the-second_wdc-capitol-west_battle-arena-visual-direction_unapproved-v01_20261016-193018-c42dd476.md` already found that the `ruins` and `outskirts` candidate bands read as ornate, generic fantasy stone rather than the New York / Yonkers / Washington setting. The archive band was not assessed there. Whether any band becomes the default is a separate player or creator decision; none has been made here.
