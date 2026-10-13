# Worlds Between — MVP game project

Open `game/project.godot` in Godot 4.7.2. Run the project to see the bilingual menu and a movable temporary protagonist. The room is an M1 input and pixel-display prototype; the world map starts in M2.

## Project structure

- `scenes/` — menu and temporary room
- `scripts/` — app language and input state, menu, room behavior
- `assets/characters/` — uniquely named temporary game sprite

Stable content IDs will use `board.area.object` (for example, `scifi.outskirts.recruit_zhaoling`). Save data and content registries begin in later MVP steps. The four aptitude IDs are `martial`, `adaptive`, `scholarly`, and `spiritual`; naming IDs in English keeps localization text separate from saved identifiers.

