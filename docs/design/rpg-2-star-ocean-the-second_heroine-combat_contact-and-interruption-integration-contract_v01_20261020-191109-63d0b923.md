# Heroine combat motion: contact and interruption integration contract

Source inspected: canonical game commit `99bf35affa8fd332802c3922a1c632e9ea22695e`. This is an implementation contract, not creator approval or a completed motion gate.

## Current behavior to preserve by default

- `game/scripts/battle_arena.gd:595` starts the attack cooldown at 0.43 seconds and sets the attack visual before checking range. A miss still starts its visual and cooldown.
- Damage is immediate at the successful request; attack visual duration is 0.39 seconds. Authored anticipation before a later contact cannot match this mechanical hit without an explicitly changed timing mode.
- Manual attack, dodge, skill and job skill are processed independently in one update (lines330-340). Later requests, and enemy hit/down later in the update, can replace the attack visual after damage has already occurred.
- Movement remains possible during recovery. Cooldown is independent of presentation interruption.
- The combat-sprite loader infers a new action event from changed action/decreased visual elapsed; it has no unique event ID. Its own one-shot clock can outlast the arena duration and the next cooldown boundary. Facing is recomputed from enemy position and can flip during an attack.
- AI attacks follow party array order and consume shared next-attack bonus on the first successful hit. Final damage synchronously awards rewards, writes the return save and opens results; recovery behind that screen is not evidence of synchronized contact.

## Current bounded pilot

The approved right-facing136x144 source must retain its68x72 logical draw rectangle, pivot32/68, face/costume identity and hard-alpha pixel appearance. Paint coherent missing anatomy rather than move flat masked cutouts. Present a clearly labeled staged idle/anticipation/contact/recovery timeline, and a separate actual-event probe. Do not claim the staged timeline establishes normal gameplay synchronization, cancellation, movement responsiveness or complete combat-set readiness.

The existing full-set loader requires all required actions atomically and logical_scale1. A partial136-source2-action pilot must not fake missing actions or silently double display size to satisfy that schema. Defaults remain unchanged.

## Later opt-in integration boundary

A genuinely synchronized timing mode needs an explicit request/contact split with unique per-fighter event IDs, elapsed/contact timestamps, latched facing and exactly-once committed/cancelled state. Rendering alone cannot delay already-applied damage. Preserve the current default path, and label timing differences in any optional experimental path. Before implementation, choose and document cancellation, hit-range recheck and buff-reservation behavior as routine implementation decisions; do not ask the creator to tune milliseconds.

Required targeted checks: default-off mechanical parity; successful attack and miss; 30/60fps and large-delta contact crossing; repress before contact/during recovery/at cooldown boundary; simultaneous fighters; same-frame attack+dodge/skill/hit/down; enemy range/facing changes; bonus reservation; pause; scene exit; final hit, defeat, return and reload without orphan damage or duplicate rewards/saves.

## Review scope

Codex owns independent source/visual inspection. Claude owns the authored action pilot. The creator owns motion acceptance after actual normal-speed gameplay review. All eight actions are required before the parent combat-actions production task is complete. This contract alone awards no points.
