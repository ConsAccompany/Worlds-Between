# Open World Pixel RPG Implementation Progress

Last updated: 2026-10-13

## Summary

- M1 project foundation is complete. Godot 4.7.2 imports and launches the project; a scene smoke check passes Chinese/English menu labels, entry/return, movement, and temporary sprite loading.
- M2 world-map exploration is complete: three destinations, top-down movement, NPC interaction, visible enemies, an avoidance path, and enemy reset on reentry.
- Four 640×360 M2 captures were inspected for readability and layout. The M2 encounter preview is now replaced by the M3 battle arena.
- M3 combat core is complete: contact opens a fixed side-view arena with two fixed enemy types, horizontal movement, attack, dodge, guard, HP and energy, victory recovery, and defeat return to the menu.
- Godot M1–M3 smoke checks pass; three M3 captures were inspected. The measured encounter transition stayed below the provisional one-second target on this development machine.
- M4 companions and AI are complete: three distinct recruit routes with decline and return, level-matched party seeds, five active slots, switching, rule-based AI policies, temporary teammate orders, pause, quick skills, and full auto.
- Godot M1–M4 smoke checks pass. A four-character AI party won a battle; four M4 captures were inspected. Formal sprite animation remains later work.
- M5 levels and jobs are complete: independent XP/JP, level-up recovery, a mandatory choice at each ten-level threshold, four aptitude gates and job series with two stages each, preserved cross-series progress, JP ranks for job and personal skills, reserve quarter rewards, and a bilingual playable growth screen.
- Godot M1–M5 smoke checks pass. M5 checks cover staying, promotion, switching away and back, skill ranks, aptitude discounts and gates, reserve rewards, combat skill use, and battle-to-growth routing. Five M5 captures were inspected. Final job art and effects remain later work.
- M6 saves and recovery are complete: three manual slots, a rolling five-record autosave history, a safe prebattle checkpoint, victory autosave after rewards, versioned JSON, and main-menu load. Map/area position, party, recruitment, enemies, discovery, AI and job records restore.
- Godot M6 scenario and separate-process restart checks pass. Four Chinese/English M6 captures were inspected. The right-side game bible reads the named JSON progress and asset inventory files in `outputs/`.
- M7 is in progress: character name and appearance choice, optional field guide, three-location objective log, relay and ruin findings, machine observation, city report and continued play are implemented. The route remains open to multiple location and recruit orders. Four location/battle ambient loops and one discovery cue are connected.
- Godot M7 route checks pass and six Chinese/English captures were reviewed. A 25–35 minute content length has not yet been demonstrated; more meaningful exploration content and a timed playthrough are required before M7 can be marked complete.
- M7 now includes two survey rooms in each of the three science-region destinations: 18 bilingual clues, three evidence questions with retry, one-time JP rewards, room/position save recovery, and an in-game run timer. Two freely ordered routes and an annex save/load check pass; new Chinese/English survey screenshots were reviewed. The planned 25–35 minute duration still needs a real timed playthrough.
- M7 evidence review now requires three clue pairs per destination before its final judgment. There are nine bilingual pair explanations across the slice, and correct/incorrect pair attempts are retryable. Link progress saves and loads. A pacing audit found only about 31 seconds of minimum walking inside all six survey rooms at the current movement speed; this is a mechanical lower bound, not a playthrough duration. Content length remains unverified.
- M7 adds six optional bilingual party conversations: three individual reflections and three two-person exchanges unlocked by recruitment and completed surveys. Topics remain available on return; first completion grants 3 prototype bond to each participant and autosaves, while replay grants no extra bond. The available-topic and dialogue screens were visually reviewed. This strengthens the recruitment loop but is not a substitute for a timed playthrough.

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

- [x] Implement the three recruit paths, switching, and AI.

### Phase M5 - Levels and jobs

- [x] Implement XP, JP, aptitudes, and the four MVP job series.

### Phase M6 - Saves and recovery

- [x] Implement autosave, manual save, and loading.

### Phase M7 - Playable content

- [x] Connect character setup, three locations, discoveries, companions, machine choice, field log and report endpoint.
- [x] Save and reload route, name and appearance state; review Chinese/English screens.
- [x] Add six survey rooms, 18 readable clues and three evidence decisions without blocking recruit order.
- [x] Add nine evidence pair deductions, bilingual feedback and save recovery.
- [x] Add six non-missable companion conversations with one-time bond and save recovery.
- [ ] Time a fresh start-to-finish playthrough and fix any blockers or text overflow.

### Phase M8 - Acceptance and tuning

- [ ] Complete fresh playthroughs and fix blockers.

