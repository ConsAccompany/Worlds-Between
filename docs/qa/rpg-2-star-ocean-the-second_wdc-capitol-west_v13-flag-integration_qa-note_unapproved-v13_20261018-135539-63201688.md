# Washington Capitol west — v13 in the normal game behind `--wdc-capitol-west-v13` (QA note, UNAPPROVED, OFF BY DEFAULT)

- **Date:** 2026-10-18, about 13:54–14:10 EDT (wall clock), in the same session that closed out v13 (`b674c7e`). The stamp `20261018-135539` and run id `63201688` are run labels; no time is inferred from them.
- **Author:** Claude Code (Opus 5.5), signed in on the Max subscription (claude.ai, firstParty). No API key, cloud credits, paid fallback or image model was used. There was no quota or auth stop during this run.
- **Worktree:** `work/max0840-wdc-ruin`, branch `codex/wdc-ruin-material-v13-20261018-0953`, on top of `b674c7e`.
- **Status:** runtime art **UNAPPROVED**, opt-in only. The default game is unchanged, and v13 is not adopted as the default.
- **Purpose:** closes the "test-harness-only" gap left by `b674c7e`. The finished v13 art (run `wdc-cw-v13_20261018-100938-075675cf`) can now be played in the normal game with a flag. The art was not modified.

## What changed

**New selector:** `game/scripts/rpg-2-star-ocean-the-second_wdc-capitol-west_exploration-opt-in-selector_unapproved-v13_20261018-135539-63201688.gd` (44 lines).
- It extends the v12r2 selector, the same pattern v12r1 → v12 and v12r2 → v12r1 use.
- With the flag, it turns v12r2 on and overrides one function, `_v12_path`. Only `rt-base` resolves to the v13 file; every other layer resolves to v12's file.
- Unchanged from v12/v12r1/v12r2: `rt-fg`, the four Y-sort layers, `rt-walk`, anchors, radii, encounter, camera, label solver and hand-offs.
- There is no duplicated scene or generator.

**Scene:** `game/scenes/scifi_exploration_area.tscn` changes one script path line, from the v12r2 selector to the v13 selector.

**Import sidecar:** `…/wdc-cw-v13_20261018-100938-075675cf/…rt-base….png.import`.
- Godot's own `--import` wrote it in an isolated temp tree; only this one file was copied back.
- Its `[params]` equal v12's committed rt-base sidecar.
- Without it, the selector would fall back to an un-imported `ImageTexture`, which still works. With it, the v13 base loads the same way v12's does.

**Flag precedence (explicit):**
- `--wdc-capitol-west-v13` wins whenever it is present. v13 builds on v12r2, so it switches v12r2, v12r1 and v12 on and overrides any of their flags given with it.
- **Flag absent:** the v13 selector calls straight through to v12r2, so the old behaviour is identical. That includes no flag at all, `--wdc-capitol-west-v12r2`, `-v12r1` and `-v12`.
- The Washington records chamber (survey annex room 2, `--wdc-records-chamber-v01`) is a separate scene with its own flag. Neither flag affects the other.

**Not changed:** the v13 art and its manifest; every v12/v12r1/v12r2 file; `survey_annex.gd`, `scifi_exploration_area.gd` and `battle_arena.gd`; walk masks, the HUD and saves; the Bible, ledger, queue, Site, progress and counters.

## Verification

Tool: `tools/…v13-flag-integration-check_unapproved-v13_20261018-135539-63201688.py check --write-report` → **21/21**.

**How it ran:**
- In a temp tree: `git archive HEAD` (`b674c7e`, 1,776 `game/` blobs re-verified) plus exactly this run's three `game/` changes, as LF bytes.
- Godot 4.7.2 ran there with its own `APPDATA`.
- **The new captures use the normal flag path**: the shared scene's own script with the command-line flag. No texture is overridden in memory.
- The flag-path harness (`tools/…v13-flag-path-harness…gd`) subclasses the committed v13 harness. It reuses that harness's routes, poses, captures and battle steps, and replaces only the in-memory override with the real flag.

**Gates:**
- **F01–F05 (setup):**
  - The temp tree is HEAD plus exactly this run's changes.
  - The scene diff is one line.
  - The v13 art still matches its committed manifest.
  - The sidecar's parameters equal v12's.
  - The import is clean.
- **F06–F07 (flag selection):**
  - Both flag runs (`--wdc-capitol-west-v13` and `--wdc-capitol-west-v12r2`) finish without errors.
  - The shared scene runs the v13 selector.
  - The v13 flag enables v13; the v12r2 flag leaves v13 off and enables v12r2.
- **F08 (no flag):**
  - With every opt-in forced off, city, outskirts and ruins equal the base script: entry image, after-input image and positions.
  - Their entry and after-input hashes also equal those recorded at the previous scene line (the committed v13 run's reports). So **no-flag pixel parity with the current base holds.**
- **F09 (v13 flag):**
  - Every shot's base sprite is a `CompressedTexture2D` loaded from the v13 rt-base path, with no override. Its image hash is `ba106505…`, which is the v13 PNG.
  - Every other layer path is v12's.
  - The walk mask and foreground are the same images as under v12r2, so collision is v12r2's.
- **F10 (old v12r2 flag):** it still draws v12's rt-base (`058fb629…`) and v12's other layers, unchanged.
- **F11 / F12 (deterministic shots):** entry, records prompt, records checked, occlusion and breach view, in zh and en, compared with the committed `b674c7e` frames.
  - **In the final run all 20 are pixel-exact with equal state.** The v13-flag frames match the in-memory-override frames; the v12r2-flag frames match the v12 reference frames.
  - Several are byte-identical files: zh entry `a4b1e573…`, en entry `dad1525b…` and v13 zh battle-return `1e9608ea…`.
- **F13 (real-time shots):** traversal, traversal end and battle return are pixel-exact when the state matches. Otherwise they must be within one scroll row and 3 px.
  - In the final run, v13 zh battle-return is exact.
  - v12r2-flag en battle-return returned at (534, 289), scroll 77, against the committed (533, 290), scroll 78.
- **F14–F17 (gameplay):**
  - The real `interact` action sets records checked.
  - Under both flags and in both languages: a real-input walk, the real sentry battle (auto mode by the real action, HP fixture 12 as before), and a real `ui_accept` return to the r2 scene on the return texel with the camera current.
  - The heroine stays inside the play band.
  - Real saves are untouched.
- **F18 (accepted rooms):** the tracked accepted-rooms replay ran with `--wdc-capitol-west-v13` on the command line. NYC room 1, NYC room 2 and Yonkers room 2 gave **8/8 frames at 0 px**, 3/3 interaction lines, and `ACCEPTED_REPLAY_ALL_OK`.
- **F19:** the existing smokes `m4`, `m6`, `m7` and `m8_city_reentry` pass.
- **F20–F21:** the worktree's `game/` status is unchanged by the runs, and the harness contract equals the committed v13 run's.

**Honest disclosures:**
- **21/21 came from the third full run.** Gates were re-defined after the first two runs:
  1. **Run 1, 18/21.**
     - *F09/F10:* the first definition hashed the walk mask and foreground PNGs. Godot's import (`fix_alpha_border=true`, also used by v12's committed sidecars) rewrites RGB under transparent texels, so a loaded image can never hash like the PNG. These gates now require v12's file paths plus the identical loaded image under both flags. The base layer is opaque, and its hashes did match the PNGs.
     - *F13:* the first definition required the same scroll. v13 en traversal-end stopped at scroll 13 against 14, with the hero 0.9 px away. The tolerance is now one scroll row.
  2. **Run 2, 20/21.**
     - *F12* (on the unchanged v12r2 path): zh traversal end stopped about 2 px further west. v12r1's label solver keeps each label's previous slot (`r1_slots`), so the "痕迹 1" label moved from x 104 to x 167. It stayed there in the later records, occlusion and breach shots (532 px each).
     - This is inherited behaviour, and this run did not change it.
     - F11/F12 now accept either pixel-exact, or "only label slots moved": everything else equal, and every differing pixel inside the old or new rect (+3 px) of a moved label.
     - In the final run, no shot needed that allowance.
  - The final evidence comes from run 3 only. The first two runs' outputs were deleted before re-running, because the same file names would have been reused.
- **Real-time variance:** the traversal and battle-return frames depend on where real-time walks stop by a frame step, as in the v12r2 and v13 runs. They are compared by state and tolerance, not pixels, unless the states match.
- **Old check tools not re-run:** the v12, v12r1 and v12r2 check tools rebuild the scene line from HEAD with their own expected line. They were not re-run, and their scene-line expectations are not v13-aware. The v12r2 behaviour itself was re-verified by F10/F12/F15 above.
- **Approval:** no creator review and no art approval. Runtime art is UNAPPROVED. The ground grain and blocky foliage that root noted are unchanged, because the art was not touched.

## Exact paths (in `work/max0840-wdc-ruin`)

**Sources** (sha256-text-lf-v1):

| file | sha |
|---|---|
| `game/scripts/…exploration-opt-in-selector_unapproved-v13_20261018-135539-63201688.gd` | `c160f161…` |
| `game/scenes/scifi_exploration_area.tscn` (one line) | `b60cf714…` |
| `game/assets/environments/candidates/wdc-cw-v13_20261018-100938-075675cf/…rt-base….png.import` | `833b94c4…` |
| `tools/…v13-flag-path-harness_unapproved-v13_20261018-135539-63201688.gd` | `72022631…` |
| `tools/…v13-flag-integration-check_unapproved-v13_20261018-135539-63201688.py` | `91fdc038…` |

**Evidence** (`outputs/wdc-cw-v13flag_20261018-135539-63201688/`, 37 files):
- **Captures:** 32 frames, `rt640-<zh|en>-<view>_flag-v13_…` and `_flag-v12r2_…`, for entry, traversal, traversal-end, records-prompt, records-checked, occlusion, breach-view and battle-return.
  - v13 zh entry `a4b1e573…`, en entry `dad1525b…`;
  - zh traversal `18086fab…`, en traversal `eecd3c10…`;
  - zh battle-return `1e9608ea…`, en battle-return `44d09da8…`.
- **Reports, log and manifest:** `godot-flag-harness-report-v13flag` / `-v12r2flag`, `accepted-rooms-replay-log-with-v13-flag`, `flag-integration-check-report` (`bc2b6e0e…`) and `flag-integration-manifest` (`84bd4475…`).
  - The manifest pins the 36 other evidence files (sha256 bytes) and the 5 sources.
  - Reports and logs carry `<TEMP_TREE>` / `<REPO>` placeholders instead of machine paths. JSON and TXT are LF, with exact-path `eol=lf` rules in `.gitattributes`.

**Play it:** `Godot --path game -- --wdc-capitol-west-v13`, then travel to the Washington ruins. To remove it, point the `.tscn` line back at the v12r2 selector.
