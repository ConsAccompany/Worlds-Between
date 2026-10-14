# Open World Pixel RPG Implementation Progress

Last updated: 2026-10-13

## Summary

- M1 project foundation is complete. Godot 4.7.2 imports and launches the project; a scene smoke check passes Chinese/English menu labels, entry/return, movement, and temporary sprite loading.
- M2 world-map exploration is complete: three destinations, top-down movement, NPC interaction, visible enemies, an avoidance path, and enemy reset on reentry.
- Four 640×360 M2 captures were inspected for readability and layout. The M2 encounter preview is now replaced by the M3 battle arena.
- M3 combat core is complete: contact opens a fixed side-view arena with two fixed enemy types, horizontal movement, attack, dodge, guard, HP and energy, victory recovery, and defeat return to the menu.
- Godot M1–M3 smoke checks pass; three M3 captures were inspected. The measured encounter transition stayed below the provisional one-second target on this development machine.
- The right-side MVP widget reads the named JSON progress file in `outputs/`.

## Milestones Checklist

### Phase M1 - Project foundation

- [x] Create the Godot project and version-control boundary.
- [x] Set crisp pixel display and default input actions.
- [x] Build a launchable menu and movable temporary hero.
- [x] Verify Chinese and English menus on Windows.

### Phase M2 - World map and exploration

- [x] Implement the three MVP destinations and visible avoidable enemies.

### Phase M3 - Combat core

- [x] Implement the fixed arena and battle recovery rules.

### Phase M4 - Companions and AI

- [ ] Implement the three recruit paths, switching, and AI.

### Phase M5 - Levels and jobs

- [ ] Implement XP, JP, aptitudes, and the four MVP job series.

### Phase M6 - Saves and recovery

- [ ] Implement autosave, manual save, and loading.

### Phase M7 - Playable content

- [ ] Build the 25–35 minute bilingual route.

### Phase M8 - Acceptance and tuning

- [ ] Complete fresh playthroughs and fix blockers.

