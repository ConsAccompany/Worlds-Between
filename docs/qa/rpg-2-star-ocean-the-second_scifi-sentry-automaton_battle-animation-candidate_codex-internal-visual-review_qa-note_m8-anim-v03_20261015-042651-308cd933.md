# Science region: sentry automaton v3 candidate, Codex internal visual review

2026-10-15. This follows up the [v3 candidate QA note](rpg-2-star-ocean-the-second_scifi-sentry-automaton_battle-animation-candidate_qa-note_m8-anim-v03_20261015-041413-5be0252b.md).

> **Codex internal review, NOT a user art verdict.** It records Codex's look at the v3 captures. It does not approve or reject any art on the user's behalf. Art acceptance and the user's review of v2 are unchanged.

## Captures inspected

Each is a separate 1280×720 Godot capture listed in the [v3 capture manifest](../../outputs/rpg-2-star-ocean-the-second_scifi-sentry-automaton-animation-pilot_capture-manifest_m8-anim-v03_20261015-042119-ae4ce2a0.json):

| What | v3 | v2 comparison |
| --- | --- | --- |
| Strike impact, target at 53 px (f14) | [target53 zh](../../outputs/rpg-2-star-ocean-the-second_scifi-sentry-automaton-animation-pilot_ruins-strike-impact-target53-f14-zh_m8-anim-v03_20261015-042119-d718958c.png) | [v2 target53 zh](../../outputs/rpg-2-star-ocean-the-second_scifi-sentry-automaton-animation-pilot_ruins-v2-compare-strike-impact-target53-f14-zh_m8-anim-v03_20261015-042119-1a4c6cc1.png) |
| Strike impact, target at 69 px (f14) | [target69 zh](../../outputs/rpg-2-star-ocean-the-second_scifi-sentry-automaton-animation-pilot_ruins-strike-impact-target69-f14-zh_m8-anim-v03_20261015-042119-83ecc7b3.png) | [v2 target69 zh](../../outputs/rpg-2-star-ocean-the-second_scifi-sentry-automaton-animation-pilot_ruins-v2-compare-strike-impact-target69-f14-zh_m8-anim-v03_20261015-042119-8a3b4113.png) |
| Defeat hold (f20, result overlay hidden) | [defeat inspect en](../../outputs/rpg-2-star-ocean-the-second_scifi-sentry-automaton-animation-pilot_ruins-defeat-hold-f20-inspect-en_m8-anim-v03_20261015-042119-8bbc6f12.png) | [v2 defeat inspect en](../../outputs/rpg-2-star-ocean-the-second_scifi-sentry-automaton-animation-pilot_ruins-v2-compare-defeat-hold-f20-inspect-en_m8-anim-v03_20261015-042119-2a9c06d3.png) |
| Full wind-up (f13) | [windup full en](../../outputs/rpg-2-star-ocean-the-second_scifi-sentry-automaton-animation-pilot_ruins-windup-full-f13-en_m8-anim-v03_20261015-042119-c9f31e09.png) | [v2 windup full en](../../outputs/rpg-2-star-ocean-the-second_scifi-sentry-automaton-animation-pilot_ruins-v2-compare-windup-full-f13-en_m8-anim-v03_20261015-042119-fba20536.png) |

## Findings

| Issue | Codex judgment |
| --- | --- |
| Occlusion at the usual 53 px contact | **Worse than v2.** The cyan claw-arc hides more of the hero during the impact frame (177 hero body pixels vs v2's 86, per the v3 note). The user asked for less occlusion, so this goes the wrong way. |
| Reach mismatch at 69 px | **Masked, not solved.** The metal claw still visibly stops short of the hero; only the arc reaches. The effect hides the gap instead of closing it. A real fix still needs a distance-aware lunge in `battle_arena.gd`. |
| Charge eye (f12–13) | **Small improvement.** The lens is brighter and has more structure under the wind-up tint, but it still reads warm, not cyan. |
| Defeat grounding (f18–20) | **Small improvement.** The dithered shadow grounds the downed body. It is a hard dither, not the soft ellipse the live fighters use. |

The two small gains do not outweigh the worse occlusion at 53 px and the unsolved reach at 69 px.

## Outcome

- **Keep v2** as the current reversible runtime candidate (`ENEMY_SPRITE_ANIMATIONS["sentry"]` still loads the v2 strip). It is still unapproved and awaits the user's review.
- **v3 stays test-only and unapproved.** It is not to be integrated as a whole. Its lens and defeat-shadow ideas could later be reused separately; the claw-arc should not be.

## Scope and counters

- No art, code, Game Bible, progress files or Git were edited for this note.
- Counters unchanged:
  - accepted enemy pilots **0**: every manifest under `game/assets/enemies/` is `pilot_unapproved`, `animation_pilot_unapproved` or `animation_candidate_unapproved`;
  - runtime character sprites **0/52**;
  - science scene visuals **0/11**.
