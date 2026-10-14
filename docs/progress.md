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
- M7 now writes a local JSON playtest receipt at the first city report, including elapsed time, event order, recruits, surveys, conversations heard before report, and retry counts. A Windows launcher starts the game with the bundled Godot executable and copies the receipt into `outputs/` after the game closes. The M7 smoke test checks receipt contents for both route orders. No real timed playthrough has been recorded yet.
- The game bible's production view now reads local M7 playtest receipts and shows elapsed time, visit order, recruitment, surveys, conversations, battles, and retry counts. The panel remains empty until a completed local run is copied into `outputs/`; automated smoke receipts stay in isolated test storage.
- M7 evidence review now has a bilingual collected-clue notebook inside the analysis overlay. Players can reread the full text of discovered clues while linking evidence or making the final judgment, then return without losing their current selection. Both route orders pass the revised M7 smoke check; Chinese and English 640×360 captures were inspected for clipping.
- M7 machine-bypass tracking now requires the player to move into the bypass zone. Loading or returning from a survey inside that zone no longer records a bypass merely because the scene appears; M2 and M7 route checks cover the change. The human timed playthrough is still outstanding.
- The game bible production view now has a local playtest launch control. It opens the visible Godot game through the existing launcher, prevents duplicate launches, reports running/completed/no-report status, and refreshes recorded runs when the game closes. The launcher scans only new validated receipts and copies them into `outputs/`. The launch button is available in the current local panel at port 18726; a real timed playthrough has not yet been performed.
- M7 now has one optional, returnable field station per science-region location. Liang Xu, Zhao Ling and Ji Cheng each use a distinct personal field ability after recruitment; the first use gives that companion 4 JP and 2 bond, records a bilingual finding, writes an autosave, and appears in the playtest receipt. Locked, completed, replay and save/load paths pass in the two-route smoke check. Five separate 640×360 captures were reviewed. The 25–35 minute content target still needs actual playtesting.
- The game bible's launch button was exercised from its live browser panel: it opened a visible Godot game window, showed `running`, and returned to `no_report` after that test window was closed before any report. No receipt was fabricated. Older panels now link directly to the current launch-capable panel. This validates launch and early-exit behavior, not the full playthrough or receipt-copy path.
- M7 playtest receipts now include cumulative time spent in each science destination and on the map or character setup. The game bible displays those splits alongside each survey's completion time, so actual playtests can identify pacing gaps without assuming that source length predicts play duration. A synthetic revisit timing check and both automated route receipts pass; no human duration has been inferred from them.
- M7 adds two optional, visibly marked field traces in each of the three destinations. Finding both lets the local recruited companion interpret them at the existing field station; recruitment and the city report remain independent. Each trace has distinct bilingual text, survives save/load, is listed in the field log and playtest receipt, and has no repeat reward. Both route orders pass the updated smoke test. Nine separate 640×360 captures were reviewed for text and marker placement. This adds exploration with a return visit; a human timed run is still needed to judge pacing.
- The game bible production page now gives two explicit fresh-run visit orders and the required report path, plus the observations only a human player can judge. The local Godot launcher remains the playable Windows entry; a standalone export template is not installed in this workspace. No human completion receipt exists yet.
- The production page now has separate first-run and second-run feedback fields for navigation, controls, text, combat, and exploration observations. They autosave in the current browser and are visibly labeled as browser-local notes to share in chat for project review. The first real game window remains open; no report receipt has returned yet.
- While the first player-run window remains open, a separate full-game design proposal now lists all 20 job series, their five tier names, roles, and one reusable endgame unlock challenge per series. The game bible presents it under Rules → Levels, Aptitudes and Jobs, clearly marked as a proposal; skill nodes and balance values remain to be designed. The provisional stealth series is proposed as a mobile skirmishing series to respect the canceled infiltration mechanic.
- A second proposal now gives Guardian, Skirmishing, Tactics, and Runecraft seven-node job trees, one sample from each aptitude. The paired tier-2 and tier-4 branches are both learnable; the draft specifies level/tier gates, three skill ranks, JP discount, energy use, and preservation on job switching. The game bible displays all 28 nodes separately from the confirmed rules; the other 16 trees and balance values remain pending.
- The remaining four Martial aptitude series now have seven-node proposals as well: Swordcraft, Heavy Arms, Martial Arts, and Polearms. The game bible displays 8/20 trees and 56 unique skill nodes; all five Martial series are covered. The active player run was left untouched, and its report receipt is still pending.
- The remaining Adaptive aptitude series now have seven-node proposals: Archery and Tracking, Firearms, Beast Bonding, and Commerce. The game bible displays 12/20 trees and 84 unique nodes; all five Adaptive series are covered. Commerce nodes include stationed weekly settlement effects and combat support while preserving the requirement that a current Commerce companion manages each guild. The first player run remains open without a report receipt.
- The remaining Scholarly aptitude series now have seven-node proposals: Engineering, Automata, Medicine, and Alchemy. The game bible displays 16/20 trees and 112 unique nodes; all five Scholarly series are covered. Separate notes clarify that deployed devices do not occupy party slots, temporary alchemy products do not enter inventory, and battle revival follows the established postbattle recovery rules.

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
- [x] Add a local playtest launcher and verify the report receipt for both route orders.
- [x] Show real local playtest receipts in the game bible production view.
- [x] Let players reread collected clues during evidence links and final judgment.
- [x] Prevent scene return inside the machine-bypass zone from creating a false observation.
- [x] Start a local timed playtest from the game bible and show its completion status.
- [x] Add three optional companion field abilities that reward return exploration and persist across saves.
- [x] Verify the browser's playtest launch, visible game window and no-report exit state.
- [x] Record per-destination time and survey completion points for pacing review.
- [x] Add six optional field traces that give each recruited local companion a concrete investigation to finish.
- [ ] Time a fresh start-to-finish playthrough and fix any blockers or text overflow.

### Phase M8 - Acceptance and tuning

- [ ] Complete fresh playthroughs and fix blockers.

