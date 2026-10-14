# M8 Game Bible progress review

Recorded 2026-10-14 UTC. This note describes prototype production, not visual acceptance.

## Repository evidence checked

- `game/scripts/character_directional_idle.gd` and `character_directional_motion.gd` reference five separate native 32×48 exploration sets: male and female protagonist, Liang Xu, Zhao Ling, and Ji Cheng. Each set has four directional idle frames and sixteen directional walk frames. The hero variants walk in playable science areas. `scifi_exploration_area.gd` displays Liang, Zhao, and Ji as recruitable NPCs.
- `battle_arena.gd` references integrated side-view frame providers for the male hero, female hero, and Liang. Their manifests contain twenty separate frames each, covering idle, move, attack, guard, dodge, hit, down, and skill. A Zhao twenty-frame candidate exists but is not referenced by the battle arena. Ji's side-view set is still pending.
- `scifi_world_map.gd`, `scifi_exploration_area.gd`, and `survey_annex.gd` reference one science map, three outdoor-area backgrounds, and six individual annex-room backgrounds. A separate battle-arena background candidate exists but is not counted as integrated.
- The standalone Godot character source gallery loaded all 52 source images in its targeted check: 9 approved source portraits and 43 concepts. It does not grant game-display or runtime-sprite acceptance.

## Live panel result

At `http://127.0.0.1:18727/`, the Production page displayed five authored exploration sets, three science recruit NPCs, three integrated combat sets, one map, three outdoor backgrounds, and six annex backgrounds. The page still showed source portraits **9/52**, game displays **0/52**, exploration sprites **0/52**, scene quality **0/11**, and human M7 route receipts **0/2**. The Asset page showed Zhao's exploration item as **制作中** and unchecked. Local `/bible`, `/inventory`, `/state`, and `/bible.js` endpoints returned the updated records. JSON parsing and JavaScript syntax validation passed.

## Remaining review

The authored and integrated candidates need human inspection at 640×360, motion and interaction review, and explicit acceptance per asset. The gallery is an internal source-image review tool. No acceptance checkbox was added or changed to true.
