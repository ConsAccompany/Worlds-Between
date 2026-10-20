# Heroine contact timing pilot v01 (opt-in, technical, UNAPPROVED)

Base `11973af`. Implements the later opt-in boundary of the contact-and-interruption contract (`63d0b923`) for `hero:female` only. This is technical evidence. It does not approve art or motion, adopt anything as a default, or complete the combat-actions integration task.

## Switch

Use `-- --heroine-sea-contact-pilot` or `heroine_sea_contact_override = 1`. When it is off, no fighter carries `contact_event_*` keys, so `_try_attack`, the loader and every other path run the base code unchanged. The authored pose shares the event clock only when `--combat-sprite-set-pilot` is also on. The package is chosen through the existing `--combat-sprite-set-index=` or `combat_sprite_set_index_override`. No package path is hardcoded.

## Decisions (routine implementation choices)

- **Request:** checks the cooldown, then sets cooldown 0.43 and `player_attack_count += 1`. It also assigns the next battle-wide monotonic event id, sets elapsed to 0 and latches facing toward the enemy (0 px counts as right). No damage, VFX or bonus use happens at the request.
- **Time origin:** pending events advance at the start of `_process`, before input, AI and the enemy. A request made later in the frame starts at elapsed 0 and is not advanced by that frame's delta.
- **Contact:** fires once at `elapsed + 1e-6 >= 5/30`. This is the loader's own `frame_at` boundary predicate, so a tick_rate-30 package shows its contact frame on the same frame. Range is rechecked at contact.
  - **Hit:** damage is base + fighter boost + shared `next_attack_bonus`. Both bonuses are consumed only here. The attack VFX is emitted with the latched facing. Enemy HP 0 calls `_finish_battle` once.
  - **Miss:** gives `battle_far` feedback when she is the controlled fighter. Bonuses are kept, and the attack still counts.
- **Recovery:** ends at `12/30`. One large delta can cross both contact and recovery; contact still resolves exactly once.
- **Interruption:** `_set_fighter_visual_action` with dodge, skill, job skill, hit or down cancels a pending attack. There is no damage and no cooldown refund. After contact it only interrupts recovery.
  - **Same frame:** input order is attack, then dodge, skill, job skill, so a same-frame defensive or skill action cancels the attack.
  - **Movement:** does not cancel.
  - **Repress:** before contact or during recovery, repress is rejected by the cooldown, because 0.43 > 0.40.
- **Hero personal skill:** unchanged. It adds the shared bonus at request time and has no direct damage. Apex 8/30 is presentation only.
- **AI ordering:** other fighters keep the immediate path. AI allies may use up the shared bonus at their own earlier hit before the heroine's contact. This is documented, not changed.
- **Pause, result and exit:**
  - Pause freezes the event clock.
  - `_finish_battle` cancels any pending event (`cancelled_result`).
  - Event state lives only in the node, so a scene exit resolves nothing.
- **Loader schema** (`worlds-between.combat-sprite-set/1` is kept):
  - **tick_rate:** an optional per-action integer from 1 to 1000. When present, each frame must have integer `ticks` ≥ 1 and no `ms`. Frame ends are `cumulative_ticks / rate`, not rounded. When absent, each frame must have `ms` and no `ticks`. Mixed, both or invalid values are rejected.
  - **loop_start:** optional and allowed on loop actions only; `0 ≤ loop_start < frames`. The intro plays once, then the action loops from that frame.
  - **Explicit event clock:** used only when the fighter has `contact_event_id`. A new attack is detected by id change, the clock is the arena event clock, and facing is latched.

## Evidence

All runs used the bounded checked runner, headless, with a fresh APPDATA. Logs are in `outputs/heroine-contact-v01/`.

| Run | Result |
|---|---|
| `timing-check-run` (attempt 1) | FAIL, parse errors: untyped `dt`, and no import cache yet |
| `check-run02` | FAIL 72 passed / 8 failed. Harness defect: all manual `_process` calls ran inside one engine frame, so `is_action_just_pressed` re-fired after cooldown. The fix awaits one engine frame after each press. |
| `check-run03` | `HEROINE_CONTACT PASS checks=80` |
| `legacy-run01` (frozen loader check, `--no-capture`) | `COMBAT_SET_PILOT PASS checks=162` |
| `half-run01` (half-scale root check v02) | `COMBAT_HALF_SCALE PASS checks=273 failures=0` (ran on the LF-normalized loader, same text) |
| `check-run04`, `legacy-run02` (final bytes) | `HEROINE_CONTACT PASS checks=80`; `COMBAT_SET_PILOT PASS checks=162` |

Final source bytes:
- `battle_arena.gd`: sha256 `86f90af3…2dcc` (LF, `eol=lf`).
- Loader: sha256-bytes `6f8b0b36e8d0d1c3e78fa7bcc3d1b7ec461c289789011d3bb49de29d1a9f82d3`, sha256-text-lf-v1 `d3ec4a64b6ce07bd1589626c209cd4ff9fe18e3cfc6412fa0580688fb0d88d2f`.

The loader is a `-text` CRLF snapshot. My patch had normalized it to LF; it was restored to CRLF before the final runs.

What the 80 checks cover:
- **Normal input path:** `Input.action_press` / `_process` / `Input.action_release`.
- **Timing:** 30 and 60 fps frame counts to contact and recovery; 5/30 − 1 ms (no hit), exactly 5/30 (hit) and a single 5/30 delta; a 0.5 s delta crossing everything; and a newborn event not advanced by a 0.5 s request frame.
- **Cancellation:** dodge, skill and job skill via input; same-frame attack+dodge; enemy hit; down; hit during recovery.
- **Bonus, range and facing:** bonus kept on a miss and consumed on the next hit; range recheck in both directions; latched facing and loader clock equal to the event clock.
- **Pause, result and exit:** pause, final-hit result, a pending event at an external result, and scene exit.
- **Repress:** before contact, during recovery and at the cooldown boundary (id 2).
- **Schema:** 15 malformed timing-schema rejections, exact tick ends, and loop_start intro and wrap.
- **Scope:** flag-off female and flag-on male keep the immediate damage path.

## Limitations

- The sprite set used is the SYNTHETIC half-scale fixture (not art). The real DeepSeek package has not been exercised.
- There is no windowed capture or normal-speed visual review. There is no full-trace default-off baseline comparison against `11973af`. Default-off parity rests on code structure (keys absent, so the base branch runs), the targeted flag-off checks and the 162/273 regressions.
- Scene exit is shown only as "node freed, no deferred effect", not a reload round-trip.
- Simultaneous-fighter and AI-ally bonus races are documented, not exercised.
- The legacy fallback renderer (no sprite-set flag) still shows its 0.39 s attack visual, not the 12/30 recovery.
- Side effects:
  - `--import` rewrote 447 `.import` files and created 334 sidecars in this checkout. All were restored or removed afterwards; the ignored `game/.godot` cache stays.
  - The half-scale root-check tool hardcodes its report path in `work/max0840-sentry-sync`, so run 1 overwrote that tracked report. A copy is kept here as `half-run01-report`, and that one file was restored to its committed HEAD bytes.
