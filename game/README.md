# Worlds Between — MVP game project

Open `game/project.godot` in Godot 4.7.2. Run the project, choose "开始探索" / "Start exploring", then click one of three destinations on the science-region map. Move with WASD or arrow keys, press E near an NPC, and use Esc to return to the map. The outskirts and ruins contain visible machines: walk around them or touch one to enter the battle arena. In battle, move with A/D or left/right arrows, press J to attack, K to dodge, and hold L to guard. Winning returns you to the same area with 20%-of-maximum HP and energy recovery; defeat returns to the main menu. Leaving and reentering a location resets its enemy.

Recruit Liang Xu in the city, Zhao Ling in the outskirts, and Ji Cheng in the ruins after examining the records console. Choosing “later” leaves each available on a return visit. Only the protagonist is shown while exploring. In battle, Tab switches controlled characters, Q uses the controlled character's quick skill, P pauses for that character's skill and temporary teammate orders, and T toggles full auto. The pause panel also cycles each teammate's persistent balanced, attack, or cautious AI policy. M4 skill effects are provisional until M5's job and skill progression is built.

## Project structure

- `scenes/` — menu, world map, three configurable exploration locations, fixed battle arena, and temporary foundation room
- `scripts/` — app language and input state, menu, map, exploration, combat rules, battle arena, and room behavior
- `assets/characters/` — uniquely named temporary game sprite

Stable content IDs will use `board.area.object` (for example, `scifi.outskirts.recruit_zhaoling`). Save data and content registries begin in later MVP steps. The four aptitude IDs are `martial`, `adaptive`, `scholarly`, and `spiritual`; naming IDs in English keeps localization text separate from saved identifiers.

Run `--headless --path game --script res://tests/m1_smoke.gd` through `res://tests/m4_smoke.gd` with Godot for milestone smoke checks. Exploration and combat figures remain temporary geometric art; save/load and final visual assets belong to later steps.

