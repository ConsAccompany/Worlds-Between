# Female protagonist south compact walk v01: 8-frame walk + 3-frame shared stop (QA note, m8-w04)

**Status: UNAPPROVED / NONRUNTIME pilot.** All manifest flags are `false`: `art_approved`, `human_reviewed`, `runtime_integrated`, `walk_animation_approved`, `stop_animation_approved`, `counts_toward_art_acceptance`. Claude checked the frames and the Godot captures as an agent; that is not a human review. **Codex inspects the visual result before any acceptance.** The only approved items are still the selout v8 SOUTH IDLE static frame and the 48 logical px exploration display scale. Motion is not approved.

- **Auth:** checked before any work with `claude auth status --json`: `authMethod: claude.ai`, `apiProvider: firstParty`, `subscriptionType: max`. No `ANTHROPIC_*` variables were set. No API key, credits or paid fallback was used.
- **Not touched:** v8 PNG / manifest / `.pxo` (v8 sha256-bytes `ccf9d2a2…68b6fd`, re-verified by the check script), runtime scripts and scenes, MOVE_SPEED, the stop policy, meters, Game Bible, `docs/progress.md`, M2 travel, the Intuition proposal, Washington art, and every v3r2/v3r3/v3r4/stop-bank file. No Git staging, commit or push.
- **AGENTS.md:** the repo has none. The global `~/.codex/AGENTS.md` naming rules were followed: slug first, descriptive sections, stamp + 8-hex id, separate files, no sheets.

## Independent re-verification and corrections (2026-10-16, Claude Code Opus 5.5, agent check, not a human review)

**Gate unchanged.** This pilot is still UNAPPROVED / NONRUNTIME and does **not** meet the full sprite gate. The meter stays at 35.0% and sprites at 0/52. A zero-change task closeout was recorded in the progress-state completion ledger. No art, runtime, travel, Washington, site or Git change was made.

**What I reproduced myself:**
- **Deterministic check:** `…-5b0e21c7.py --pixelorama` gives **17/17 OK**. That includes a byte-identical rebuild of all 15 asset files, the v8 hash lock, all flags false, and the Pixelorama 1.2.3 headless export matching every frame PNG.
- **Godot 4.7.2 capture:** re-run windowed from an isolated copy of `game/` under `%LOCALAPPDATA%\Temp`, with `APPDATA` pointing to a temp dir. It exited 0.
  - All **42 capture PNGs are byte-identical** to the `185704-6a0e6012` set.
  - Every per-tick, stop and tap value in the receipt is identical; only the filename stamps differ.
  - The repo's `git status` gained no entry from this run.
- **Receipt hashes:** the GIF receipt's 69 GIF hashes and its capture-receipt hash (`ec60551f…`) match the files on disk.
- **Slip recomputed from the receipt's per-tick sole rows:** 4.64 / 5 (60 fps), 9.32 / 10 (30 fps), 1.94 / 2 (144 fps) window px per tick.
- **Stops and loop:** stop XOR 291 (f3) / 315 (f7) in all three scenes. Loop XOR is 51–231, measured on the frame PNGs.
- **Visual check:** agent look at 4× crops of the 12 city-bright stills and the annex-dark stop from f7. No GIF was watched in real time, and no person has viewed the motion.

**Corrections to this note:**
1. **Verdict is overstated.** "Compact motion is achievable at the bar this brief set" has not been shown. The cycle still has:
   - world-space planted-boot slide;
   - a 291–315 px silhouette jump into the stop;
   - a restart discontinuity with the current runtime timer reset;
   - no real-time inspection by a person.

   Read the verdict as "the compact pilot is technically consistent with its own measurements". It does not say the motion is acceptable.
2. **The slide per ground contact is larger than stated.** The note says "over one 300 ms stance … ≈ 84 window px". Each boot is actually on the ground for **6 of 8 frames (450 ms)**. The receipt (city-bright, 60 fps) shows one vl contact of 27 ticks sliding **121 window px (≈ 60 logical px)**, and vr contacts sliding 102 and 79 px.
3. **"Accepted convention" / "classic sprite-walk convention" is a description, not an acceptance.** Neither the creator nor Codex has accepted world-space slip for this project.
4. **"A boot on the ground never changes a texel or a row" applies in-cell only.** In world space the planted boot moves 4–5 window px every tick at 60 fps.
5. **Capture PNG hashes are not in the receipts.** The capture receipt lists the 42 PNG names and their fidelity counts, but no sha256. Only the GIFs are hash-pinned. The PNGs are now backed by this byte-identical re-capture, not by a stored hash.
6. **The "restart" claim is incomplete.** Item 7 is true: with the runtime's timer reset, a quick re-press re-lifts the leg that just landed (reproduced: `stop-plant-vl` → `f1-bend-vl`). The "suggested restart" that avoids this is not wired into the runtime.

**Remaining risks (unchanged by this check):**
- world slip;
- the stop-entry silhouette jump;
- the restart re-lift;
- depth shown inverted on vl steps;
- contact and bend frames that are nearly v8 (visible in the stills: f4 / f8 are hard to tell from v8 at 4×);
- partly authored lifted boots;
- no real-time human review.

## Verdict in one paragraph

*(Author's original wording. See correction 1 above: it is not a demonstrated acceptance bar.)* Compact motion **is achievable** at the bar this brief set, with one cost that cannot be removed at this frame count, stated here rather than hidden.

The pilot uses **8 loop frames + 3 shared stop frames = 11 PNGs**, against v3r4's 16 run + 187 stop PNGs. It is drawn at the logical position with no root lock, so the stop never depends on sub-pixel position (no D table). Measured on real Godot pixels in 3 scenes:
- a boot on the ground never changes a texel or a row, while walking or through any stop;
- the crown moves only between rows 8 and 9;
- every stop lands a lifted foot on the **release tick (0 ms airborne)**, against N32's 233 ms;
- no stop or restart ever lands the trailing foot first.

**The cost:** without a root lock the planted boot glides with the body in world space at the runtime speed (4.6 window px per tick at 60 fps). This is the classic sprite-walk convention. It is **not** the zero-slip lock v3r4 had. See "Why zero slip is out of reach for 6–8 frames" below. If Codex requires world-space zero slip, this pilot does not meet it and no 6–8-frame pilot can at 140 px/s.

## What was built

Builder: `tools/…south-walk-compact-v01-build_m8-w04_20261016-184552-1c53af0d.py`. It is standalone and source-locked to v8. It copies the v3r4 helpers verbatim but never imports v3r4: palette, v8 split, boot shaft strings and foot views, arm segments, cape/hair lag, `.pxo` writer.

- **Legs are v8's own leg texels**, re-stacked per pose as whole rows: thigh / knee band / shin repeated or dropped, knee leaned 1 texel inward on the lift. No resampling, filtering, flip, mirror or generative redraw.
  - `plant` at bob 0 rebuilds v8's legs texel-for-texel, and a neutral recomposition rebuilds all of v8. Both are build gates.
  - Every pose with the foot down uses **v8's own boot on v8's own ground row** (vl 100, vr 103).
  - Lifted boots use v8's shaft strings plus the v3r4 `hang` / `reach` feet in v8 leather colours. Each is shifted so its sole centre sits over v8's toe spot (fully for `reach`, half for `hang`). A descending foot therefore drops onto its spot instead of sliding onto it.
- **Upper body:** v8 rows 8–57, moved only by the 0/+1 bob. Exceptions are the declared arm zones (v3r4's B1 / N / F1 elbow poses, contralateral) and the hair lock (±1 row lag on bob changes). Gated: 0 mismatched texels.
- **Palette:** v8's 32 colours only. Binary alpha. Every frame ≤ 96 texels tall with the lowest row ≤ 103, so the figure never exceeds 48 logical px.

### Loop (time-driven, 75 ms per frame, 600 ms cycle, 3.33 steps/s at 140 px/s)

vl is the viewer-left leg (her right, knee guard). It is v8's back foot, so it lifts first and the loop starts naturally out of v8.

| # | Frame | vl | vr | Bob | Crown row | Arms R / L | vl sole | vr sole |
|---|---|---|---|---|---|---|---|---|
| 1 | f1-bend-vl | bend (knee down 1, in 1) | plant | +1 | 9 | F1 / B1 | **100** | **103** |
| 2 | f2-lift-vl | lift 5 (hang) | plant | 0 | 8 | N / N | 95 | **103** |
| 3 | f3-reach-vl | reach 2 | plant | 0 | 8 | B1 / F1 | 98 | **103** |
| 4 | f4-contact-vl | plant | plant | +1 | 9 | B1 / F1 | **100** | **103** |
| 5 | f5-bend-vr | plant | bend | +1 | 9 | B1 / F1 | **100** | **103** |
| 6 | f6-lift-vr | plant | lift 5 (hang) | 0 | 8 | N / N | **100** | 98 |
| 7 | f7-reach-vr | plant | reach 2 | 0 | 8 | F1 / B1 | **100** | 101 |
| 8 | f8-contact-vr | plant | plant | +1 | 9 | F1 / B1 | **100** | **103** |

Bold = on its ground row. At least one boot is on the ground in every frame, and both are on the ground in 4 of 8 (double support; no flight phase).

### Stop / plant bank (3 frames, each shared by several release phases; drawn at the logical position)

| Bank frame | Legs | Bob | Arms | Used after release from |
|---|---|---|---|---|
| stop-plant-vl | vl bend (just landed on v8's spot), vr plant | +1 | N / N | f2, f3 |
| stop-plant-vr | vl plant, vr bend | +1 | N / N | f6, f7 |
| stop-settle | both plant | +1 | N / N | every case (last before v8) |

- **Feet in the air at release (f2, f3, f6, f7):** stop-plant-X for 67 ms, then stop-settle for 67 ms, then v8.
- **Feet on the ground (f1, f4, f5, f8):** stop-settle, then v8.
- **Runtime lookup:** `frame = floor(walk_time / 75 ms) mod 8`, then `stop_table[frame]`. There is no position, sub-pixel or D input.

## Floor contact (measured on PNGs and on Godot pixels)

**PNG-level, re-measured by the check script from the files on disk (17/17 OK):**
- **Grounded boots:** every boot on its ground row is v8's boot exactly. 0 texels differ, so the toe moves 0 texels sideways.
- **Contact texels:** vl's sole row has 3 contact texels (x 26–28) and vr's has 5 (x 49–53), as in v8.
- **Loop steps:** across all 8 loop steps, no boot that is on the ground in both frames changes a texel.
- **Lifted boots:** each boot leaves the ground once per cycle and rises then falls (vl 100→95→98→100; vr 103→98→101→103). There is no in-air reversal inside the loop.

**Godot 4.7.2.** Real windowed 1280×720 run, 640×360 canvas, scale 0.5, nearest filtering, no shadow. The hero is moved by each scene's own `_process` at MOVE_SPEED 140 (measured 140.000). Scenes: city-bright, outskirts-bright, annex-dark. All gates passed (exit 0), with identical numbers in all three scenes:

| Measure | 60 fps | 30 fps | 144 fps |
|---|---|---|---|
| Grounded boot in-cell row errors (every walk tick) | 0 | 0 | 0 |
| Loop-frame skips or backward steps per tick | 0 | 0 | 0 |
| **World-space planted-boot slip**, window px per tick (mean / max) | **4.64 / 5** | **9.32 / 10** | **1.94 / 2** |
| Exact-RGB fidelity (stills, every 5th walk tick, every stop / idle tick) | 100 % | 100 % | 100 % |

The slip row is the honest cost. *(Corrected: each boot is grounded for 6 of 8 frames = 450 ms, so one ground contact slides up to ≈ 121 window px (≈ 60 logical px) with the body, not ≈ 84 px over 300 ms.)*

## Immediate stop (Godot, all 8 release frames × 3 scenes, released on the last tick of each frame)

| Released from | Feet on the ground | In the air | Stop frames shown (ticks at 60 fps) | v8 at tick | Grounded boot row / texel change | Airborne foot lands | Max head step | Max silhouette XOR / tick |
|---|---|---|---|---|---|---|---|---|
| f1-bend-vl | vl, vr | — | settle ×5 | +5 (83 ms) | 0 / 0 | — | 1 | 113 |
| f2-lift-vl | vr | vl | plant-vl ×5, settle ×4 | +9 (150 ms) | 0 / 0 | **release tick (0 ms)** | 1 | 167 |
| f3-reach-vl | vr | vl | plant-vl ×5, settle ×4 | +9 | 0 / 0 | **0 ms** | 1 | 291 |
| f4-contact-vl | vl, vr | — | settle ×5 | +5 | 0 / 0 | — | 1 | 113 |
| f5-bend-vr | vl, vr | — | settle ×5 | +5 | 0 / 0 | — | 1 | 113 |
| f6-lift-vr | vl | vr | plant-vr ×5, settle ×4 | +9 | 0 / 0 | **0 ms** | 1 | 178 |
| f7-reach-vr | vl | vr | plant-vr ×5, settle ×4 | +9 | 0 / 0 | **0 ms** | 1 | 315 |
| f8-contact-vr | vl, vr | — | settle ×5 | +5 | 0 / 0 | — | 1 | 113 |

- **Planted-boot pop at the switch:** 0 in every case.
- **Fixed-pin bbox comparison:** last walk frame vs v8 lowest row is 103 = 103 for every case. The lifted foot's own drop is ≤ 5 rows, which is the lift height.
- **Body during the stop:** the hero does not move, and the crown steps once by 1 (9 → 8 into v8).
- **Loop-step XOR for scale:** 51–231 per frame change.
- **Tick quantisation:** at 60 fps a 67 ms frame shows for 5 ticks when it starts on the release tick. Durations are therefore 83 + 67 ms as measured, not 67 + 67.

**"Phase reversal" checks:**
- **Landing order:** only one foot is ever in the air, so the trailing foot cannot land first. N32 had 4 such reversed cases.
- **Lifted foot reversing direction:** this happens only when the stop comes during the rising half of a step (f2: the foot rose 5 rows into f2, then is put straight down on the release tick). It never holds in the air. N32 held a foot up 150–233 ms.
- **Re-press 2 ticks after a stop from f3 (tap cases, all scenes):**
  - with the runtime's own timer reset (restart at f1), **the leg that just landed (vl) lifts again immediately**. This is a defect of combining this cycle with the current timer reset;
  - with the manifest's `restart_after_stop_suggestion` (resume at f5 after a vl step), vr lifts next and the alternation holds.

  Wiring that rule is a runtime-owner decision and was not done.

## Why zero slip is out of reach for 6–8 frames (evidence for the cost)

**Root lock needs offsets or many frames.** A root-locked planted foot must stay fixed in world space while the body moves 140 logical px/s. With an 8-frame / 600 ms cycle a held frame lasts 75 ms. In that time the body moves 10.5 logical px (21 window px), and the foot can only stay fixed if the sprite is drawn at a per-tick offset from the logical position. That is the v3 root lock.

**The offset forces D-keyed stops.** On an immediate stop the offset must be undone: either the planted boot pops (v3r3: up to 14 / 24 px), or the stop frames must be keyed by the rounding case D (v3r4: 88 cases, 187 frames; N32: 32 frames plus offsets, with 4 reversed landings).

**Without the offset, held frames slide.** Doing the lock with frames alone would need about 1 frame per tick of stance (v3r4's stance frames were 7/3 px = 1 tick). Fewer frames make the body hop 21 px per frame.

**So compact means accepting world slip.** "Few frames + immediate stop + no pop" and "world-space zero slip" are mutually exclusive at 140 px/s. This pilot chooses the first and reports the slip.

## Reuse and size cost

| | This pilot | v3r4 run + stop | v3r4 bank N32 |
|---|---|---|---|
| Unique PNGs | **11** (8 loop + 3 stop) | 203 (16 + 187) | 16 + 32 |
| PNG bytes | **38,600** | 674,605 (stop: 623,184) | — |
| Stop lookup | `stop_table[frame]` (8 entries; ≤ 2 frames each) | `table[frame][D]` (352 entries) | 352 (pose, offset) entries |
| Draw offset | none | per-tick root lock | per-frame vertical offset |
| Stop duration | 83–150 ms | 267 ms | 267 ms |

- **Editable layered sources:**
  - `…loop-editable_….pxo` (57,061 B): 8 frames × 11 layers (`cape, arm-vl-back, arm-vr-back, hips, leg-far, leg-near, coat-skirt, upper-body, hair-lock, arm-vl, arm-vr`).
  - `…stop-bank-editable_….pxo` (24,334 B): 3 frames × 11 layers.
  - Both export through Pixelorama 1.2.3 `--headless --export -f 1-N` with an isolated `APPDATA` temp dir, to RGBA identical to every frame PNG (check 10). They were **not** opened in the GUI.
- **Reuse for other directions or characters:** the method needs only the target's own static idle split into leg, boot, arm and hair parts, plus four leg poses. Any other direction or character still needs its own approved static, its own boot views and a new review. Nothing here is proven for them.

## Remaining defects (honest)

1. **World-space slip.** The planted boot glides with the body: 4.6 px/tick at 60 fps, 9.3 px/tick at 30 fps. This is a common sprite convention, not solved, and not accepted for this project.
2. **Depth is not shown by foot height.** Feet only plant on v8's spots, and v8 already has vl 3 rows higher than vr. So on vl steps the "forward" (just-landed) foot sits higher on screen than the trailing one. The stride reads from lift and arms, not from foot depth. A larger forward reach would need stop frames that move a planted foot, which this pilot rules out.
3. **Contact and bend frames are subtle.**
   - The legs in f4 / f8 are v8's legs (compressed 1 row by the bob).
   - `bend` moves only the knee band (1 row down, 1 in). There is no heel lift, because the boot must stay texel-identical on the ground.
   - Codex criticised it1 for a contact pose that was idle + bob. This pilot shares that trait in its contact frames. The difference is that lift / reach frames carry real knee lean, shin re-stack and foot change.
4. **Lifted boots are partly authored.** The `hang` / `reach` feet are the v3r4 Claude-authored foot rows in v8 colours, on v8 shaft strings. They are not v8's boot and are narrower or wider than it.
5. **The stop from a reach frame is the biggest single change.** Silhouette XOR is 291 / 315, against a loop maximum of 231: the foot lands and the arms return to N in one step.
6. **The 2-frame stop lasts 150 ms at 60 fps** (tick quantisation), not 134 ms.
7. **The runtime timer reset re-lifts the just-landed leg on a quick re-press** (see the tap cases). The fix is a wiring rule, which was not applied.
8. **Arms are reused v3r4 B1 / N / F1 poses.** The back pose hides part of the hand behind the hip. The hair lock flicks ±1 row on each bob change.
9. **No shadow, no palette change.** Annex-dark legibility of trousers and boots is unchanged from v8.
10. **Not judged in real time by a person.** I inspected stills and 3× scratch crops. The GIFs were generated but not watched as motion by me. Real-time feel is Codex's call.

## Files (all new; nothing existing was overwritten or deleted except this run's own orphans)

| Path | sha256 (bytes) |
|---|---|
| `tools/rpg-2-star-ocean-the-second_protagonist-female_south-walk-compact-v01-build_m8-w04_20261016-184552-1c53af0d.py` | `ac58c731…a06dad` |
| `tests/protagonist-female-south-walk-compact-v01/rpg-2-star-ocean-the-second_protagonist-female_south-walk-compact-v01_deterministic-check_m8-w04_20261016-184552-5b0e21c7.py` (17/17 OK with `--pixelorama`) | `527f202e…170c0c52` |
| `tools/rpg-2-star-ocean-the-second_protagonist-female_south-walk-compact-v01-godot-capture_m8-w04_20261016-184552-7d3a90c4.gd` (`-s` tool, no `game/` footprint) | `53cdbf9b…f968fd1b` |
| `tools/rpg-2-star-ocean-the-second_protagonist-female_south-walk-compact-v01-preview-gif_m8-w04_20261016-184552-2f61c8b9.py` | `ef93153f…66e71d01` |
| `game/assets/characters/walk-pilots-compact-v01/` (+ empty `.gdignore`, so Godot imports nothing): 11 PNGs `…south-walk-compact-v01-{f1-bend-vl … f8-contact-vr, stop-plant-vl, stop-plant-vr, stop-settle}_m8-w04_20261016-184552-<id>.png` | per PNG in manifest |
| `…/walk-pilots-compact-v01/…-manifest_m8-w04_20261016-184552-d49be940.json` (LF only; poses, soles, stop table, restart suggestion, all builder metrics) | `59b9eada…3486f6` |
| `…/walk-pilots-compact-v01/…-loop-editable_…-93427d77.pxo` / `…-stop-bank-editable_…-31bab315.pxo` | `a8096468…59e8616b` / `becdf932…852f57bb` |
| `outputs/…south-walk-compact-v01-…-h48_m8-w04_20261016-185704-6a0e6012.*`: **42 separate 1280×720 PNGs** and **69 single-view GIFs**, plus the capture receipt `…capture-receipt…json` (`ec60551f…3322d18`) and the GIF receipt `…preview-gif-receipt…json` (`59f40d91…ad65cf3`) | GIFs: in the GIF receipt. PNGs: **not hashed** in any receipt (correction 5) |

**Output PNGs:**
- **City-bright stills at one pin:** v8 reference, all 8 loop frames, all 3 stop frames.
- **Outskirts-bright and annex-dark stills:** v8, f2 and f6.
- **Stop sequences** in city-bright and annex-dark, released from f2-lift-vl, f4-contact-vl and f7-reach-vr. Each has last walk tick, stop k1, stop k2 and v8.

**GIFs per scene:**
- the walk at 60 fps (realtime 1× and quarter-speed 2×);
- an in-place follow-camera loop at 3×;
- all 8 stop cases (1× and 2×);
- both tap cases (1× and 2×).

GIF palettes are lossy; the PNG captures are colour-exact.

**Side effects:**
- The Godot run created no `.uid` or `.import` files; `git status` was compared before and after.
- An aborted first run (stamp `185631-eb9882a4`) left 12 city stills. I deleted them, since they were my own orphans.
- Scratch files are in `work/walk-pilot-scratch/` (gitignored), including the per-tick motion captures.
- During this session another workstream modified M2 travel scripts and tests (`app_state.gd`, `scifi_world_map.gd`, `world_route_registry.gd`, …). Those changes are not from this pilot.

## Reproduce

```
PY=C:/Users/hkzha/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/python.exe
$PY -I -B tools/…south-walk-compact-v01-build_…-1c53af0d.py --out-dir <scratch>        # byte-identical rebuild (--write targets the asset folder)
$PY -I -B tests/protagonist-female-south-walk-compact-v01/…-5b0e21c7.py --pixelorama     # 17/17 OK
work/tooling/godot-4-7-2/Godot_v4.7.2-stable_win64_console.exe --path game -s <abs path of …godot-capture_…-7d3a90c4.gd> -- --motion-dir=<abs scratch>
$PY -I -B tools/…preview-gif_…-2f61c8b9.py --motion-dir <abs scratch> --receipt outputs/<capture receipt>.json
```

**Reversal:** delete the following. Nothing else was changed.
- `game/assets/characters/walk-pilots-compact-v01/`
- `tests/protagonist-female-south-walk-compact-v01/`
- the three `tools/…south-walk-compact-v01…` files
- this note
- `outputs/*south-walk-compact-v01*20261016-185704-6a0e6012*`
