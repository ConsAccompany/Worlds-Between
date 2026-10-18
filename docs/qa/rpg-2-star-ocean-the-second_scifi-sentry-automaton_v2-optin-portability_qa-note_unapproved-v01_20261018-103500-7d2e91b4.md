# Sentry automaton v2: opt-in portable code integration (QA note, UNAPPROVED v01)

- Date: 2026-10-18
- Worktree: `work/max0840-sentry-sync`, branch `codex/sentry-v2-optin-portability-20261018-1011`
- Base: verified `main` = `origin/main` = `eb70de1e6df3280297ec1fd9fd0da63b872ac675`
- Status: root accepted the **technical code port only** (2026-10-18). Committed on this branch, **not pushed, not the default**. The serialized metadata correction is a separate commit; this note's commit changes no Game Bible, ledger, progress-state or acceptance count.
- Approval scope (unchanged): the creator approved sentry animation v2 as the **action direction baseline only**. The full sprite, the animation and the art are **not** accepted; art acceptance stays 0. Code bools: `SENTRY_V2_ART_APPROVED = false`, `SENTRY_V2_SPRITE_ACCEPTED = false`.

## What changed (exact paths)

| Path | Change |
| --- | --- |
| `game/scripts/battle_arena.gd` | +218 / −3 vs eb70de1 (the root-approved hunks below, plus the opt-in gate) |
| `game/tests/rpg-2-star-ocean-the-second_sentry-automaton_v2-optin-pilot-check-capture_unapproved-v01_20261018-102800-c3f81a6d.gd` | new: the sentry-only adaptation of the primary's untracked `…m8-anim-v02_20261014-230639-ad3f9d97.gd` |
| `tools/rpg-2-star-ocean-the-second_sentry-automaton_v2-optin-default-parity-capture_unapproved-v01_20261018-101900-5e7a2c41.gd` | new: deterministic battle capture, run with `-s` against the base export and the candidate |
| `tools/rpg-2-star-ocean-the-second_sentry-automaton_v2-optin-default-parity-compare_unapproved-v01_20261018-102400-9b4d17e3.py` | new: Pillow pixel comparison of base / default-off / flag-on captures |
| `docs/qa/…v2-optin-portability_qa-note_unapproved-v01_20261018-103500-7d2e91b4.md` | this note |
| `outputs/sentry-v2-optin-unapproved-v01_20261018-102755-e4b20e2e/` | evidence (256 files, 9.3 MB; every file name carries a timestamp + ID; names ≤ 109 chars; longest relative path 173 chars = 243 at the primary checkout, 268 in this worktree, which needs `core.longpaths` / the `\\?\` prefix) |

Text hashes (`sha256-text-lf-v1`): `battle_arena.gd` 8bf461aa81f2eab65c4d65fbe0320e30f45654e4c0b18c34ac514c875d8570e2 (base eb70de1: e9737c4082ffa180b6bab1340311db8d33aab526a9ef7bcb42bb178d5f859f02); check 39b736d4fd7e57789c14959ed72bee92384a7f5f2a3026a6ef4def608ba50d8c; capture tool c06353931c63f2e1cdaf3658bce48493e560d3e1242eb3ea55aa94c6dc25b617; compare tool 640da3242640ba04e7d2977861fbf22d43626f94d0df3dbe6c71e6820f6c1683 (both after the naming fix below; before it 3a952f0d… / b9d89152…). The capture manifest's `battleScriptSha256` (ce5548c7…) hashes the CRLF working-copy bytes of the same file.

No asset, scene, `.import`, data or other script changed. The primary checkout was only read: its `battle_arena.gd` is still +278 / −11 and its index was not touched. Nothing was staged or copied from it as a whole file.

## Ported hunks (root-approved plan, nothing else)

Taken from the primary's dirty `battle_arena.gd`:
- `ARENA_FLOOR_Y := 272.0`
- `ENEMY_SPRITE_PILOTS` with the **sentry entry only** (static PNG, anchor 48,60, ring centre y 241, ring scale 2.0 × 1.2)
- `ENEMY_SPRITE_ANIMATIONS["sentry"]`: v2 strip path, cell 112×62, anchor 46,60, body_center_x 64, states/frames, frame times, gait_step_px 4, move_grace 0.08, front_states [strike]. **Values are byte-for-byte the primary's; no retiming.**
- `ENEMY_WINDUP_MODULATE`, `ENEMY_TELEGRAPH_CENTER_Y/RADIUS/COLOR`
- the enemy visual vars (18), the `_load_enemy_sprite_pilot()` call in `_ready`, and the 2 `_advance_enemy_visual` calls in `_process`
- the 8 visual helpers: `_advance_enemy_visual`, `_enemy_visual_duration`, `_enemy_gait_step`, `_enemy_distance_gait`, `_enemy_draw_x`, `_enemy_body_offset_x`, `_enemy_visual_in_front`, `_enemy_visual_frame`
- the load functions `_load_enemy_sprite_pilot`, `_load_enemy_animation`
- the enemy-behind / foreground draw order in `_draw`, and the new `_draw_enemy`

Excluded (verified by a line diff against the primary file): arena band constants and `_load_arena_candidate`, `_draw_contact_shadows`, the telegraph label outline, the patrol sprite entry, `ARENA_CANDIDATE_ENABLED` / `ENEMY_SPRITE_PILOT_ENABLED` / `ENEMY_SPRITE_ANIMATION_ENABLED`, the career candidate passives (`GrowthRules.candidate_basic_hit`, `_standing_member_states`: they need the uncommitted growth rules), and all v3–v5 / P3 / P4 / P6 and other fighter art. The geometric backdrop branch of `_draw` is the base code unchanged. The only wording edits are comments: "contact shadow" was dropped from two comments, because that code is not ported.

## Opt-in gate (City Hall v06 pattern)

- `static var sentry_v2_override := -1` and `static func sentry_v2_enabled()`: `1` = on, `0` = off, `-1` (default) = on only if the command line holds `-- --sentry-v2-pilot`.
- Both loads are gated: `_load_enemy_sprite_pilot` (the static PNG) and `_load_enemy_animation` (the strip) each check `sentry_v2_enabled()` first, so with the flag off neither texture is loaded.
- The flag only covers the sentry, because the pilot tables hold only `"sentry"`. Patrol battles are pixel-identical with the flag on.
- The per-instance `enemy_sprite_pilot_enabled` / `enemy_sprite_animation_enabled` (default `true`) can only narrow the pilot (static only, or none). They cannot switch it on without the flag (this is tested).
- Off-path equivalence: with no texture loaded, `_enemy_body_offset_x()` is 0, the ring is `draw_circle((enemy_x, 240), 30, same colour)`, the enemy still draws after the fighters and only while `enemy_hp > 0`, and the block code is untouched. The pixel parity below confirms it.
- Gameplay: no HP, damage, reach, AI, cooldown, wind-up, speed or position code changed. The visual helpers only read combat state.

## Dependencies (all tracked at eb70de1, hashes verified)

- Static PNG `game/assets/enemies/sentry-automaton-pilot-0b9664e2/…battle-idle-left_m8-pilot-v01_20261014-221901-e3ab87f9.png`: sha256-bytes 5ca76fe9…2462 (matches the pilot manifest and the primary copy)
- v2 strip `…battle-animation-strip-left_m8-anim-v02_20261014-230329-ffefdc6f.png`, 2352×62 = 21 cells of 112×62: sha256-bytes 26d1fb1c…e52e (matches the v2 manifest and the primary copy)
- `.import` for both (tracked, `fix_alpha_border=true`, lossless); v2 manifest `…battle-animation-manifest_m8-anim-v02_20261014-230329-ffefdc6f.json`
- 21 frame PNGs in `frames_m8-anim-v02_ffefdc6f/` (`.gdignore`d): a Pillow check confirmed all 21 equal their strip cells byte for byte (RGBA)
- Author scripts (Python + Pillow): v2 `…pilot-author_m8-anim-v02_20261014-225908-7e2215bc.py` text-LF hash 7ba2bb89…34f2, static `…idle-pilot-author_m8-v01_20261014-221848-0b9664e2.py` a8dfa204…d6d0. Both match their manifests, so **no author rebuild was needed** and none was run.
- v1 strip `…m8-anim-v01_20261014-223820-f181f893.png` (tracked): used **only by the test**, as the foot-slide sensitivity replay. Not wired.
- **No PXO/ORA exists for the sentry.** The art is Pillow-authored, not editable in Pixelorama.

## Results (Godot 4.7.2.stable.official.ed1daf0bf, `work/tooling/godot-4-7-2`; APPDATA isolated under `%LOCALAPPDATA%\Temp\sentry-v2-optin-20261018-101714\appdata`)

| Run | Result |
| --- | --- |
| Default-off pixel parity: base eb70de1 export (`git archive` under Temp) vs candidate, no flag; sentry + patrol × zh/en × 1280×720 + native 640×360 × idle / wind-up ring / hit taken / defeat result | **32/32 captures, 0 differing pixels** |
| Same harness, candidate with `--sentry-v2-pilot` | patrol 16/16 still 0 px; sentry 16/16 differ (idle 16145 px @1280, wind-up 24137, hit 15768, defeat-under-result 396) |
| Check, headless `--no-capture` | `SENTRY_V2_OPTIN PASS checks=281` |
| Check, `--sentry-v2-pilot --cli-flag-only` | `SENTRY_V2_OPTIN CLI PASS checks=5` (CLI alone enables; patrol untouched; override 0 beats the CLI) |
| Check, windowed with captures | `SENTRY_V2_OPTIN PASS checks=789 frames=21 captures=60 crops=78` |
| `m3_smoke`, `m4_smoke`, `m5_smoke`, `m6_smoke`, `m6_restart_smoke` headless, default and `--sentry-v2-pilot` | all 10 runs exit 0 (`M3_SMOKE_OK`, `M4_SMOKE_OK`, …) |
| Male / female / Liang / Zhao / Ji side-view combat smokes, headless `--no-capture`, default and flag | all 10 runs exit 0 (`M8_*_COMBAT_VISUAL_SMOKE_OK`). Without `--no-capture` they fail at their own capture step under `--headless` (the known display-only limit), in both modes. |

What the windowed check covers (sentry only):
- **Default off**: no textures, r30 ring at y 240 centred on enemy_x, inert state machine, per-instance switches cannot enable it. The pilot tables hold the sentry only.
- **Load**: static fallback 96×62 at anchor 48,60; strip 2352×62; cell 112×62, anchor 46,60, body offset +18; ring 2.0×1.2 at y 241; frame 0 = static PNG at the 16 px margin; state table = manifest.
- **Frame audit, all 21 cells**: anchor row 60; inside the cell; only the strike uses the margin; soles planted; centroid drift ≤ 4 px (strike ≤ 9); gait foot steps exactly 4 px (6 pairs); consecutive frames differ; 11 reused v1 poses equal.
- **Combat unchanged**: stats 96/18/68/0.48/1.10, approach step, 53 px wind-up start, melee 19, dodge 12, guarded 60→54, unguarded 60→42, **strike reach 69 px** (70 px untouched), **hero melee 61 px hits / 62 misses**.
- **Simulation parity**: 600 auto-battle steps, pilot on vs `override = 0`, identical trace (first difference −1). The pilot run passes through move 83, windup 116, strike 72, hit 148, defeat 147 and idle 34 steps.
- **State selection**: idle 0–3 loop; gait 4–11 by distance, drawn in 4 px steps (≤ 2 px from enemy_x); reverse gait; 0.08 s grace; wind-up 12→13 behind the fighters; strike 14→15 in front (hit lands for 18) then idle; hit 16→17 behind; pause freezes it; defeat 18→19→20, holding 20.
- **Walk foot lock** (160 real 60 fps steps): v2 slip 0.00 px over 115 planted pairs, max draw offset 2.0, stop snap 0. The v1 replay through the same code slips 187 px, so the measure is sensitive.
- **Fallbacks**: animation off → static pilot; missing / wrong-shape / v1 strip → static; pilot switch off → block + r30; patrol stays the block with the flag on; the static fallback ignores defeat states.
- **Telegraph, tint, ring**: the label clears the coiled top; the ring keeps 3213 / 3212 visible px around frames 12 / 13 (block baseline 1248); wind-up tint (1.0, 0.70, 0.66) is matched on screen.
- **Bilingual captures**: 15 cases × zh/en × review 1280×720 + native 640×360 = 60 captures. Rendered-frame match ≥ 0.857 (hero-overlapped contact frames; idle / move / defeat ≥ 0.97). Eye ≥ 0.866 and claw ≥ 0.815 at the 53 px melee spacing. The strike draws in front and hit frames behind (overlap order checked). Transitions ≤ 15.4 ms.
- **Crops**: solo crops of all 21 strip frames in both windows (42, each frame ≥ 0.97 on-screen match); 16 real gait-step walk crops; 2 × 10 contact crops (v2 and the v1 replay).

Evidence: `outputs/sentry-v2-optin-unapproved-v01_20261018-102755-e4b20e2e/` holds the capture manifest JSON (frame audit, parity, walk, visibility, ring/overlap, 60 capture records with SHA-256 and `artAccepted: false`), the PNGs, `parity/` (the 96 parity PNGs, each run's index JSON and the compare reports, all stamped) and `logs/` (the 7 original run logs plus the rename and recapture logs).

## Parity file naming fix (2026-10-18 13:51–13:55, after root review)

The first parity runs wrote 99 files whose own names had no timestamp or ID (`parity/{base,off,on}/…-parity_index.json` and `…-parity_patrol-idle-en-640.png` etc.); only the parent folder was unique. Fix:
- The capture tool now writes `<PREFIX>_<variant>-<enemy>-<state>-<language>-<window>_<stamp>.png` and `<PREFIX>_<variant>-index_<stamp>.json` and requires `--stamp=YYYYMMDD-HHMMSS-<8 hex>`; the three runs share one folder. The compare tool pairs files by that name, takes `<parity-dir> <stamp>`, and uses the Windows extended-length prefix because the stamped paths pass 260 chars in a worktree.
- Evidence: the 96 PNGs were **moved, not re-encoded** (every SHA-256 re-checked after the move) to `parity/` under the original run stamp `20261018-102755-e4b20e2e`. The three index JSONs got the new `file` names plus `variant`, `stamp` and a `nameMigration` block. The compare report under the run stamp was regenerated by the fixed compare tool (the old one listed the unstamped names; its sha256 733063… is in the receipt). The original compare log keeps the old names verbatim. Receipt: `rpg-2-star-ocean-the-second_sentry-v2_parity-rename-receipt_20261018-135103-7a97ecda.json` (every old → new path with its sha256).
- Targeted revalidation: the fixed compare tool over the renamed evidence prints `SENTRY_V2_DEFAULT_PARITY PASS` (32 default-off 0 px / 16 flag-on patrol 0 px / 16 flag-on sentry differ). A fresh windowed recapture with the fixed capture tool (stamp `20261018-135153-a5a778fe`; base = the eb70de1 export, off and on = this worktree) wrote all 99 stamped names, passes the same compare, and its 96 PNGs are **byte-identical** to the renamed evidence, so only the three recapture index JSONs, the recapture compare report and the 4 recapture logs were kept. The recapture left `git status` unchanged.
- Bounded audit of the other generated names: every other file in the evidence folder (captures, crops, manifest, logs) already ends in `_20261018-102755-e4b20e2e`. No other new generated file lacks a stamp.

## Visible limitations (honest)

- It still uses the **geometric placeholder backdrop**: the arena band, contact shadows and label outline are excluded by design, so the sentry has no ground shadow and stands on the purple / grey placeholder field. The telegraph label has no outline. It was readable in the wind-up captures I inspected by eye (zh 1280); the check only proves it clears the sentry, not its contrast.
- The animated sprite draws **18 px further from the party than `enemy_x`**. This is visual only: reach is still measured from `enemy_x`, so at the 53 px spacing hits can land with a visible gap, and the strike lunge (frame 14) closes it.
- In hit frame 17 the hero's sword thrust covers part of the eye bezel, because the hero draws on top by design (eye ≥ 0.866).
- The animated pilot stays on the field in its defeat pose under the result overlay. The block and the static fallback still vanish.
- The flag covers every sentry battle in the process (ruins and the Washington sentry encounter alike), not just one area.
- On a fresh tree, `godot --import` rewrites ~378 tracked `.import` files to LF (content-identical) and creates ~54 `.import` and ~37 `.uid` sidecars. I reverted / removed all of them in this worktree; a clean clone will see the same noise and must not stage it.
- I did not re-run the windowed `m3_visual_capture` / `m4_visual_capture` / `m5_battle_visual_capture` (they write into `outputs/`); the parity harness covers the default-vs-flag visual question. No full regression sweep was run.

## Proposed truthful wording correction (for root; not applied)

`outputs/rpg-2-star-ocean-the-second_mvp-progress_state_v01_20261013-183804-28a1c7e4.json`, `decisions[id = "sentry-v2"].detail` currently says "…21 帧候选，为当前运行默认…" (current runtime default). That is true only of the primary's **local dirty** `battle_arena.gd`; verified main eb70de1 draws the placeholder block. Proposed (after this candidate lands, approvals unchanged):

- zh: 「修正遮挡与滑步的 21 帧候选。已验证的 main 运行默认仍为占位方块；v2 仅可选启用（`-- --sentry-v2-pilot`），默认关闭。创作者已批准 v2 作为动作方向基准（仅动作方向）；完整精灵与美术均未验收，美术验收 0；v3–v5 候选未接入运行。」
- en: "21-frame candidate that fixes occlusion and foot slide. The verified main runtime default is still the placeholder block; v2 is opt-in only (`-- --sentry-v2-pilot`), off by default. The creator approved v2 as the action direction baseline only; full sprite and art not accepted, art acceptance 0; v3–v5 candidates not wired."

Before this candidate lands, the accurate wording is "v2 is not in the verified main runtime (local uncommitted only)". The `sentry-direction` scope and all approval / acceptance data stay unchanged. Root updates the serialized metadata. Update: the corrected wording was then applied in a separate metadata commit on this branch (see that commit).

## Not done (by instruction)

No push, default adoption, persistent memory, new art, other enemies, v2 retiming, regression sweep or ownership fallback. The primary checkout, its index and the other worktrees were not modified.
