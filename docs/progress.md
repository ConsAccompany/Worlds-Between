# Open World Pixel RPG Implementation Progress

Last updated: 2026-10-14

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
- The remaining Spiritual aptitude series now have seven-node proposals: Luminous Source, Umbral Source, Summoning, and Relic Studies. The game bible displays 20/20 career trees and 140 unique nodes. These are design proposals pending player confirmation and balance work. Light and dark are complementary sources, summons are temporary effects outside the five-member party, and relic skills add optional archaeological insight without gating discoveries.
- The player ended the first attempted M7 playtest in the city before traveling. The game exited normally and produced no city-report receipt. The player clarified that they simply stopped for now; this does not indicate an onboarding defect. No formal timed run has been completed yet.
- Personal skill tree proposals now cover the protagonist and all 15 main companions. Each keeps the character bible's unique signature skill, with five level-gated nodes at character levels 1/10/20/30/40. The game bible displays these proposals in each character profile. The remaining 35 companions' personal trees, JP costs and combat balance remain open. M7 still awaits two completed human playthrough receipts.
- MVP scope was revised by the player: all 51 characters need in-game visual identities (52 image variants because the protagonist has male and female versions), while the playable content remains the science region. The environment target is the perceived quality of Wandering Sword, judged from running scenes rather than concept art. The new v0.2 plan adds M8 visual production and M9 integrated acceptance. The asset inventory now separately tracks 52 source sheets (9 previously accepted), 52 in-game displays, 52 four-direction exploration sprites, five playable combat identities, three visual-direction gates, and eleven science-region scene-quality gates. Existing geometric rooms remain functionality proofs, not accepted final visuals.

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

### Phase M8 - Character and environment art

- [x] Revise MVP scope, asset inventory and side panel gates for 52 character variants and eleven science-region scene visuals.
- [x] Generate two city background candidates and separate protagonist/Liang Xu cutouts; import the selected city and both characters into a 1280×720 Godot preview. Inspect the actual engine screenshot and show it in the game bible production view. The city reads as practical high-tech restoration; the characters remain distinguishable by hair and outfit.
- [x] Integrate the city art as a playable candidate with foot anchors, walkable boundaries, foreground occlusion and clearer hotspots; review four actual engine captures. Keep art approval open.
- [x] Register all 52 visual variants against source art (9 approved portraits, 43 concepts); test three character identities at 40 px in Godot and reject the first high-resolution direction drafts for runtime use.
- [ ] Approve the character and city visual sample before batch production.
- [ ] Integrate and review the 52 in-game displays and four-direction sprites.
- [ ] Finish the playable team's battle art and the eleven scene visuals.

The playable city now uses the static visual-direction candidate, manually traced walking and foreground layers, and static character cutouts. It still needs directional walking, architectural and stair alignment, a visual approval decision, and the other ten scene-quality gates.

### Phase M9 - Integrated acceptance

- [ ] Complete two fresh playthroughs with the finished art and fix any blockers.


## 2026-10-14 - City cutout integration candidate

- City protagonist variants and Liang Xu now use visible alpha bounds for a provisional 44-pixel height and foot anchoring; interaction labels have dark outlines. Current M7 hotspot/test coordinates are preserved.
- Fresh cloud Godot 4.7.2 import, M1–M7, M6 cold restart and the new M8 city integration check pass. The rendered check covers both appearances, movement, recruitment visibility and saved/legacy positions. Four separate Chinese/English playable-city viewport captures were inspected.
- Review: [city integration review](../outputs/rpg-2-star-ocean-the-second_scifi-city_integration-review_m8-foot-anchors_20261014-051328-11830a39.md); [capture manifest](../outputs/rpg-2-star-ocean-the-second_scifi-city_in-engine-check_manifest_m8-foot-anchors_20261014-051328-11830a39.json).
- This is candidate integration evidence. Asset acceptance flags and M7/M8/M9 statuses are unchanged. Directional walking, layered occlusion, detailed obstacle alignment, fullscreen review and two genuine human timed playthroughs remain outstanding.

## 2026-10-14 - City navigation boundary candidate

- Replaced the broad western rectangle with garden, lamp-base and planter polygons. Swept movement prevents crossing narrow obstacles on long frames; edge sliding and nearest-valid save recovery preserve access to the city route.
- Godot 4.7.2 navigation checks pass headless and rendered; city integration, M2, M6 and both M7 automated routes pass. Four separate Chinese/English engine captures were inspected, including diagnostic boundary overlays.
- Review: [city navigation review](../outputs/rpg-2-star-ocean-the-second_scifi-city_navigation-review_m8-boundaries_20261014-063728-a19da10f.md); [manifest](../outputs/rpg-2-star-ocean-the-second_scifi-city_navigation-manifest_m8-boundaries_20261014-063728-a19da10f.json).
- This remains candidate integration. Static cutouts, foreground occlusion, detailed architecture alignment and genuine human playthroughs remain unfinished. Asset acceptance and M7/M8/M9 statuses are unchanged.

## 2026-10-14 - Parallel city and QA integration

- The playable city now layers the garden canopy and street furniture over characters by foot depth. Distinct hotspot icons and nearby text reduce labels covering the paving; a locator shows the protagonist behind dense foliage. Four separate Godot viewport captures document both protagonist appearances and Liang Xu before/after recruitment.
- Combined Godot 4.7.2 checks pass: M8 navigation, M8 city integration, M8 city return/recruitment with bilingual proximity labels, and both automated M7 routes. The new QA test was updated after integration because some city labels intentionally appear only when approached. An occasional ObjectDB warning occurs on exit without a failing test.
- [City runtime review](../outputs/rpg-2-star-ocean-the-second_scifi-city_runtime-review_m8-v05_20261014-133629-a4c139fb/rpg-2-star-ocean-the-second_scifi-city_runtime-review_m8-v05_20261014-133700-3d6148a7.md) and [QA playtest routes](qa/rpg-2-star-ocean-the-second_scifi-region_human-playtest-routes_m7-m8_20261014-133240-51d0c8a7.md) are ready. M7 remains awaiting two genuine 25–35 minute human runs; M8 visual acceptance and M9 remain open.
- [Character visual review](character-visuals/rpg-2-star-ocean-the-second_character-visual-review_first-directional-pass_20261014-140000-8de210f4.md) tested five separate direction drafts in six separate Godot 640×360 captures. At 40 px, the character silhouettes blend into the city and the female protagonist's hairstyle is not reliably distinct. The [native sprite specification](character-visuals/rpg-2-star-ocean-the-second_character-visual-spec_topdown-v01_20261014-135700-17a0c9d4.md) calls for 32×48 four-direction redraws before a 52-character batch. Accepted runtime sprites remain **0/52**.

## 2026-10-14 - Native directional idle prototypes

- Three isolated branches produced separate native 32×48 transparent RGBA south, west, north and east idle frames for the male protagonist, female protagonist and Liang Xu: **12 frames**. These were drawn at native pixel scale using the source sheets for design guidance. The female ponytail was widened after a 640×360 preview showed weak separation.
- The playable science city now uses those frames at 1:1 scale with nearest filtering and a shared (16,44) foot anchor. The protagonist changes facing with movement. Liang Xu uses the native south frame as a recruitable NPC. Separate [male](../outputs/rpg-2-star-ocean-the-second_protagonist-male_native-idle-in-engine-city-south_m8-v01_20261014-135900-4829b1de.png), [female](../outputs/rpg-2-star-ocean-the-second_protagonist-female_native-idle-in-engine-city-south_m8-v01_20261014-135900-03fa228c.png) and [Liang Xu](../outputs/rpg-2-star-ocean-the-second_liang-xu_native-game-preview-south_m8-v03_20261014-180100-f3128e01.png) game-scale images are available.
- Godot 4.7.2 import, M8 city integration/navigation/reentry, and M7 automated routes pass. The [runtime capture manifest](../outputs/rpg-2-star-ocean-the-second_scifi-city_native-idle-in-engine_m8-v02_20261014-135900-c51f78ab/rpg-2-star-ocean-the-second_scifi-city_native-idle-capture-manifest_m8-v01_20261014-175723-9797aa74.json) lists each facing separately.
- These are idle prototypes, **4/20 frames per character**. Walking loops, in-motion silhouette review, broader scene polish and art approval remain open. Asset acceptance stays **0/52** for runtime sprites; M7 human playtests remain outstanding.

## 2026-10-14 - Native directional walk prototypes

- Three parallel character passes produced **48 separate 32×48 four-direction walk frames** (four phases per direction for the male protagonist, female protagonist and Liang Xu), bringing each exploratory set to 20 idle-and-walk frames. Nine additional south attack/hit images are motion studies only; the separate horizontal battle art specification remains open.
- The male and female protagonist now animate while moving through all three playable science areas and return to directional idle when stopped or blocked. Liang Xu remains a stationary recruitable city NPC, with all four walk directions authored and posed in the city for visual review.
- Godot 4.7.2 imported the 57 new PNGs. M2, M7, M8 city integration, navigation and reentry checks pass. [Twelve separate 640×360 engine captures](../outputs/rpg-2-star-ocean-the-second_scifi-city_native-motion-in-engine_m8-v01_20261014-141222-62e97563/rpg-2-star-ocean-the-second_scifi-city_native-motion-capture-manifest_m8-v01_20261014-181226-6f8d6327.json) show one walking phase per direction and character. These are static frame inspections, not a human motion review.
- The Game Bible and asset checklist reflect this progress. Character sprite acceptance remains **0/52**, because gait timing, moving silhouette, Liang Xu's actual party movement, broader scene color checks and user art approval are still open. M7 human playtests and all scene gates remain open.

## 2026-10-14 - M8 art quality and scale correction

- The creator rejected the 32×48 native exploration frames as a production visual baseline. They remain playable functional placeholders only. No character sprite is art approved (0/52), and no scene quality gate is closed (0/11).
- Godot now renders the 640×360 logical game at a native 1280×720 window using `canvas_items`. The M2–M8 automated checks and the field NPC visual check passed after the change. This improves the presentation of the city and text but does not itself improve the old character drawings.
- Separate higher-detail transparent concept frames now exist for the female and male protagonists facing south, east, and north. Liang Xu also has three separate direction concepts. West may mirror east during an experiment; animation and runtime integration are still open. The creator accepted the detail level but found the first 72-logical-pixel sample too large, then **approved 48 logical pixels as the exploration character display scale** after viewing [all three at the same foot position](../outputs/rpg-2-star-ocean-the-second_scifi-city_liang-xu-male-female-south-scale-review_m8-concept_20261014-153644-9226ceab.png). This scale approval does not approve the individual art or motion.
- Five distinct 20-frame side-view combat sets are integrated for both protagonists, Liang Xu, Zhao Ling, and Ji Cheng. All five are functional prototypes, with **0/5 art approved**. Lazy loading keeps the tested first battle transition below one second.
- Science-region field NPCs, world-map art, outdoor backgrounds, and six survey-room backgrounds have candidate in-engine displays. The Game Bible and asset inventory record the new art as under review; playable acceptance still requires creator inspection and two genuine human M7/M9 routes.
- A female south walk experiment reached a four-phase Godot preview, but separately generated frames move the knee guard between legs and shift the torso by about four logical pixels. One targeted image edit fixed scarf side but did not fix the guard. The sequence is not accepted for production. Separate dark-background checks of the three premium south concepts showed no visible halo at 48 logical pixels; low-alpha fringe cleanup remains a production detail.

## 2026-10-14 - Female south-idle Pixelorama technical pilot

- The user ran the free Pixelorama v1.2.3 web build. They imported the female premium south concept, which remains unchanged in git. A nearest downscale to 96×115 was saved as a `.pxo` and a PNG. A second `.pxo` and PNG keep that layer byte-identical and add a separate `readability-paint` layer with exactly four hand-placed hair-highlight texels. The two PNGs differ at those four texels only.
- The four files are in `game/assets/characters/pixelorama-pilots/`. A [pilot manifest](../game/assets/characters/pixelorama-pilots/rpg-2-star-ocean-the-second_protagonist-female_south-idle-pixelorama-pilot-manifest_m8-v01_20261014-211454-868681b7.json) records each file's source, SHA-256 and relationship. The [setup note](character-visuals/rpg-2-star-ocean-the-second_protagonist-female_pixelorama-south-pilot-setup_m8-v01_20261014-170109-dd62c262.md) was corrected: it had said the editor was not launched and no art files existed.
- These two pilot PNGs do not meet the memo's pilot targets: 3,476 partial-alpha texels (target 0), about 3,070 colours (target ≤48), 107-texel visible height (target 96 ±1), and a 96×115 cell instead of 80×112.
- Variant-tagged 1280×720 Godot city captures at 48 logical pixels beside the 32×48 placeholder exist for both steps: [downscale](../outputs/rpg-2-star-ocean-the-second_scifi-city_protagonist-female-pixelorama-south-downscale-pilot-h48-beside-placeholder_m8-v01_20261014-211425-c01ae148.png) and [four-texel paint pass](../outputs/rpg-2-star-ocean-the-second_scifi-city_protagonist-female-pixelorama-south-handpolish-pilot-h48-beside-placeholder_m8-v01_20261014-211431-209c5b2d.png). They differ at exactly four window pixels, one per painted texel. The earlier [untagged capture](../outputs/rpg-2-star-ocean-the-second_scifi-city_protagonist-female-pixelorama-south-pilot-h48-beside-placeholder_m8-v01_20261014-210813-c3f6fba6.png) is byte-identical to the downscale capture, not a separate result.
- Two further candidates were made by a [deterministic script](../tools/rpg-2-star-ocean-the-second_protagonist-female_south-idle-quantized-downscale-author_m8-v01_20261014-212322-42a51d4b.py) straight from the source concept, with no AI editing and no hand edits: crop, BOX or LANCZOS resample, binary alpha, a 48-colour palette and an 80×112 cell. A [second manifest](../game/assets/characters/pixelorama-pilots/rpg-2-star-ocean-the-second_protagonist-female_south-idle-quantized-downscale-manifest_m8-v01_20261014-212322-aa446773.json) records hashes and measurements. Both PNGs meet the numeric pilot targets (independently re-measured: 80×112, 0 partial-alpha texels, 48 colours, 96-texel height, no border texels). Each has a tagged 48 px city capture: [boxquant](../outputs/rpg-2-star-ocean-the-second_scifi-city_protagonist-female-pixelorama-south-boxquant-pilot-h48-beside-placeholder_m8-v01_20261014-212445-f010e332.png) and [lanczosquant](../outputs/rpg-2-star-ocean-the-second_scifi-city_protagonist-female-pixelorama-south-lanczosquant-pilot-h48-beside-placeholder_m8-v01_20261014-212450-2b647e78.png). Passing numbers is not art approval: face, badge and buckle detail weakens at this density, and no human has reviewed the art or any animation.
- All four variants are one idle frame, not a walk pilot. None is integrated, art-approved or production-ready. Character acceptance stays **0/52** and scene quality **0/11**. Still open: the user's E10 review of all four captured variants, the R2 walk-speed decision, walk frames, other directions and the other 51 variants. M7, M8 and M9 statuses are unchanged.
