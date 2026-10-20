# Patrol machine battle animation v01 — native contract (UNAPPROVED technical candidate)

Task `content.enemy.patrol.battle-animation`. Enemy `patrol` (巡逻机械 / Patrol machine). This is art for a mechanical enemy, not a human.
Protected values that no visual change may alter: HP 64, damage 12, speed 55, windup 0.65, cooldown 1.35, the stop range of 53 px, the AI, timers and positions.
Optional flag `-- --patrol-battle-animation-pilot`, off by default. The Sentry flag `--sentry-v2-pilot` stays independent.

## Identity and style
- The identity follows the selected Patrol native static (`assets/enemies/patrol/static-bench-v01`): a reverse-knee two-legged walker with a warm sandstone egg hull, a steel visor head with one teal lens, a rear teal vent, an amber hatched warning plate and a teal-tipped antenna.
- This version re-authors it at gameplay scale. It does not upscale the 64x64 static, and it does not trace or copy any Sentry pixels.
- The style language is shared with the Sentry: warm metal plates in a 4-step ramp, cool steel joints, one dark shared outline `#241e22`, teal tech light and a single amber warning. Light comes from the upper left.
- What sets it apart from the Sentry: an upright biped instead of a low crawler, an egg hull plus a visor head, and no claw. The attack is a short shock prod under the visor that reaches about 14 px past the head and stays in front of the hero rather than over them.

## Native size and pivot
- Each cell is 112x72 and faces LEFT toward the party. It is drawn at 1x on the 640x360 logical canvas.
- The body is about 50 px from the sole to the antenna tip, close to the roughly 48 px player body.
- The pivot / runtime anchor is (56, 66), which is `enemy_x` on floor y 272. The sole rows are 65 and below, and the contact shadow covers rows 63–68.
- The front edge at rest is about `enemy_x − 30`. The prod tip at strike contact is about `enemy_x − 44`, and the hero front edge is about `enemy_x − 41` when the Patrol stops at 53 px. `body_center_x` is 60, which positions the wind-up ring.

## Layers (bottom → top), the same in PXO, ORA and the builder
`shadow` (alpha 110 contact ellipse) · `far-leg` (darker value) · `hull` · `head` (visor + lens) · `near-leg` · `prod` · `fx` (sparks / charge).

## States (24 frames in one strip)
| state | frames | timing | notes |
|---|---|---|---|
| idle | 0–3 | 0.22 s | hull bob of 1 px, head lags one frame, lens pulse, antenna sway |
| move | 4–9 | distance gait, 4 px/step | each foot is planted for 3 steps (world-fixed) and swings for 3 steps; it plays backwards when the Patrol backs off |
| windup | 10–12 | 3 phases over the real 0.65 s windup | pulls back, crouches, then charges the prod; lens brightens and the amber plate lights |
| strike | 13–15 | 0.11 s, drawn in front | contact lunge plus spark → hold → recover (damage lands at windup end, so frame 13 is the contact) |
| hit | 16–18 | 0.09 s | recoil with a moderate warm tint baked in (30 % → 15 % → 0 % toward `#ff8c78`), no white flash |
| defeat | 19–23 | 0.15 s, holds the last frame | sparks → knees buckle → slump → collapse → lens dark with smoke |

## Runtime
The runtime package is a JSON manifest plus the strip PNG, in this directory. A small helper (`.gd` in this directory) validates the package, the file and every type. It loads only when the flag is on, and any defect falls back cleanly to the existing placeholder block.
