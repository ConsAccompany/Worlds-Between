# Worlds Between — MVP game project

Open `game/project.godot` in Godot 4.7.2. Run the project, choose "开始探索" / "Start exploring", then click one of three destinations on the science-region map. Move with WASD or arrow keys, press E near an NPC, and use Esc to return to the map. The outskirts and ruins contain visible machines: walk around them or touch one to enter the battle arena. In battle, move with A/D or left/right arrows, press J to attack, K to dodge, and hold L to guard. Winning returns you to the same area with 20%-of-maximum HP and energy recovery; defeat returns to the main menu. Leaving and reentering a location resets its enemy.

Recruit Liang Xu in the city, Zhao Ling in the outskirts, and Ji Cheng in the ruins after examining the records console. Choosing “later” leaves each available on a return visit. Only the protagonist is shown while exploring. In battle, Tab switches controlled characters, Q uses their personal skill, R uses their current job skill, P pauses to choose any unlocked skill in the current job series or issue temporary teammate orders, and T toggles full auto. The pause panel also cycles each teammate's persistent balanced, attack, or cautious AI policy.

Victory awards each active character XP and JP. A traveling reserve receives 25% of both. Levels are individual and restore full HP and energy. At every level divisible by 10, the character must choose to stay, promote (when the next MVP stage exists), or enter another series allowed by their aptitude. The game opens the growth screen after a battle at a threshold; it can also be opened from the world map. Four job series have their first two stages and two skills each. Learned ranks and job stages remain recorded when switching away and back. JP upgrades unlocked job and personal skills; higher aptitude lowers JP cost by up to 50%. The MVP starts the protagonist at level 1. Job art and skill effects remain temporary.

Use **Save** on the world map or in an exploration area to choose one of three manual slots. **Load Game** on the main menu opens the same list. Autosaves retain the five most recent records: contact with an enemy creates a safe prebattle checkpoint, and victory writes a second record after recovery and rewards. Defeat returns to the main menu, where the checkpoint can be loaded. Saves use version 1 JSON in Godot's `user://saves` directory; an unsupported version is shown but cannot be loaded. Exploration location, precise hero position, visible/cleared enemy, discovery and recruitment state, party, individual growth and job records all restore. A pending mandatory job choice opens the growth screen before exploration resumes.

## Project structure

- `scenes/` — menu, world map, three configurable exploration locations, fixed battle arena, and temporary foundation room
- `scripts/` — app language and input state, menu, map, exploration, combat rules, battle arena, and room behavior
- `assets/characters/` — uniquely named temporary game sprite

Stable content IDs will use `board.area.object` (for example, `scifi.outskirts.recruit_zhaoling`). Save data and content registries begin in later MVP steps. The four aptitude IDs are `martial`, `adaptive`, `scholarly`, and `spiritual`; naming IDs in English keeps localization text separate from saved identifiers.

Run `--headless --path game --script res://tests/m1_smoke.gd` through `res://tests/m6_smoke.gd` with Godot for milestone smoke checks. After M6, run `res://tests/m6_restart_smoke.gd` in a separate Godot process to verify a cold load. Test saves use isolated `user://test-saves` folders. Exploration and combat figures remain temporary geometric art; final visual assets belong to later steps.

