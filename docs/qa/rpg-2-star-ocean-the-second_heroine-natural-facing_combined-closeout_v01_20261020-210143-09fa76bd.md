# Heroine natural roundtrip and one-shot facing — independent closeout

Completed 2026-10-20T21:01:43.921992+00:00. Base4ef439193286d271d5311987773ca3f96229c4ce. Claude authored the scripted normal-game flow; DeepSeek repaired the loader; Codex independently tested the combined checkout and handled source/media integration. No change to battle_arena.gd or art pixels.

## Delivered and independently reproduced

- Optional heroine one-shots latch facing on entry/restart for dodge/hit/skill/defeat, hold through target crossing, then release on idle/move/guard. Defeat holds until revived. Explicit contact attack clocks/IDs/facing stay unchanged. Legacy fighters remain outside this branch.
- Two real1280x720 Godot runs: exploration movement into an actual encounter, engine-loop Input.action_press/release attacks, natural victory, real result-button mouse input, exploration return and normal battle-autosave reload. Solo heroine; one initial exploration placement70px left of the visible enemy is disclosed. No battle placement, HP/stat/timer/AI overrides, direct attack/finish calls, renderer subclasses or pose injection.
- PatrolEN30bright:30checks,122frames/4.066667s,4hits; sentryZH60default:30checks,299frames/4.983333s,6hits and a naturally cancelled precontact attack after enemy damage. Enemy AI remained active. Exactly one encounter pre-save and one postbattle save each; return/reload grants no duplicate reward or damage. Sentry background is the existing default geometric placeholder, not finished scene art.
- Root facing251predicates on actual packed art: before48failures, after251pass. Includes both facings/restarts/end/isolation and180legacy common-time output comparisons. Shared bonus16explicit boundary fixtures cover both hit orders, cancellation and an ally finisher; the low-HP finisher is staged, not a natural victory.
- Combined clock220/contact80/legacy162 pass after the final loader patch. ObjectDB warnings retained; no ERROR/SCRIPT_ERROR counted as a passing gate.

Natural proof: `outputs/hsea07/rpg-2-star-ocean-the-second_natural-battle_combined-root-proof-v01_20261020-205944-af162133.json`.
Combined checks: `outputs/hsea07/rpg-2-star-ocean-the-second_heroine-facing-bonus_combined-proof-v01_20261020-205746-2bf9a6d1.json`.
Arena rawSHA256: `2b214b6b0483bb8320a96cfd53f890b20fb5b987923f5502131facea17c3ea63`.
Loader rawSHA256: `ac8cd3dce945de02763fc7c8037d7587a83e874297ee3e0f5e6675d073cfdebf`.

## Visual evidence and scope

Codex viewed the actual combined anticipation, contact, finishing contact and return PNGs. The short blade changes pose; finishing contact remains visible before results; the heroine returns to exploration without a lingering battle sprite. Enemy art and the yellow controlled-character marker are still placeholders. Normal-speed MP4s are encoded from every original Godot frame at30/60fps,1280x720, no interpolation/speed change/compositing. These are scripted input evidence; sampled critical frames and successful decoding do not certify continuous fluidity or a human playthrough. Keep the previous staged source-action reels separate from this evidence.

## Retained failures and limits

DeepSeek's synthetic38-predicate check passed its assertions but the producer checked-runner gate FAILED on a root-certificate-store ERROR. Root's separate actual-set251 and combined suites pass with strict diagnostics; the producer failure is retained, not relabelled green. Producer import metadata churn stays in its isolated checkout. Claude retained parse/import/input-edge and long-path probe failures before two clean final runs. Producer QA refers to its unchanged-loader base; this closeout and root hashes bind the final combined patch. The producer runner is archived as frozen source, not installed as the canonical runner because its worktree ancestry differs. Root uses the portable ancestor-discovery runner. Scoped attributes and staged-blob checks preserve tested bytes. No thresholds were weakened. A prematurely labelled combined-log timestamp was corrected before integration; completedAt records the real time.

No full sprite/art approval, default adoption, additional directions, human playthrough, native GUI SaveAs/reopen or whole-game regression is claimed. Four-person natural battle and full action fluidity review remain separate follow-ups.

## Before → after and scoring

Production53.6% →53.6%(+0.0percentage points); inspection14.2%→14.2%(+0.0); creator7.0%→7.0%(+0.0). This repairs and extends already-credited source/runtime work. No new scoring task, revision bucket or denominator is introduced. Source production remains credited while approval waits. Accepted environments3/12,fullsprites0/52,humanpost-artplays0/2,formalfalse.
