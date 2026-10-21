# Adopt the two already accepted environments in normal play

Codex implementation and inspection. Base production85a32e3; approval recorded separately ate3f49a5. Existing frozen tasks content.scene.outskirts.native-default and content.scene.battle-arena.native-default,2points each. No new art/version points.

## Changes

- Yonkers outskirts now loads the exact approved native640x360 environment without opt-in. Original opt-in flag remains harmlessly compatible; explicit --yonkers-outskirts-legacy is a diagnostic rollback. Original missing-resource/invalid-size fallback remains intact. Only destination scifi.outskirts is selected.
- The approved side-view science environment now loads by default for the outskirts arena. Other arenas remain unchanged. Existing explicit battle_backdrop_override=0 remains the old off diagnostic; the original native flag still explicitly enables the accepted band. No gameplay timing,enemy/party stats,hit logic,input,collision,save or transition changes.
- No character,enemy,motion or editor reliability acceptance is inferred. Existing2native editor diagnostic failures remain unresolved; complete sprites0/52,human timed plays0/2,formalfalse.

## Checked actual normal-game evidence

- Final default outskirts:72/72, no art opt-in flag; tag20261021-005528-b7bc8c39. EN/ZH ordinary Input/button trace investigation,recruitment,save/load,assist,annex return,natural AI battle victory and safe return.
- Final legacy outskirts:68/68, explicit rollbackflag; tag20261021-005700-880c9c46.
- Default battle:52/52, no art opt-in flag; tag20261021-005528-04d024c8. Four normal party members,patrol+sentry,EN/ZH,natural victory,result button and safe return.
- Legacy battle:48/48, explicit diagnostic override0; tag20261021-005528-573212ee.
-18default gameplay screenshots(6exploration+12battle) pixel-identical to their previously tested approved-preview versions. No rerendered art. Six legacy exploration screenshots also match the old fallback0changed pixels.
- Two ObjectDB exit-instance warnings occur on some default/legacy runs, as in prior baseline; retained and not claimed leakfree. No ERROR/SCRIPT_ERROR,missing success marker or failed check in these final runs. Automated fixed-step evidence is not a human timed playtest/performance benchmark.
- Intermediate pre-comment/line-ending captures are not the final source-bound proof. Only the final tags above and source hashes in outputs/environments-adopt14/rpg-2-star-ocean-the-second_accepted-environments_source-pins_v01_20261021-005731-c39c5a23.json support integration.

Source is byte-pinned in outputs/environments-adopt14/rpg-2-star-ocean-the-second_accepted-environments_source-pins_v01_20261021-005731-c39c5a23.json. Both new runners reuse the existing finite-deadline diagnostic checked runner. The original authoritative captures and their recorded hashes remain unchanged.
