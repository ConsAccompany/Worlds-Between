# Exploration sprite set pilot: QA note (capability, test-only fixtures)

Task: `code.runtime.character-sprite-pipeline` (6 points, coding stage). Branch `codex/exploration-sprite-set-pilot-20261018`, cut from origin/main `3e040a9`. Run ID `20261018-153932-9f31902d`.

**What this is:** a runtime capability. It loads high-density, four-direction idle and walk sets for the exploration avatar and plays them in normal gameplay. It is off by default and turned on by `--exploration-sprite-set-pilot` plus a data manifest.

**What this is not:**

- It is not art adoption. The shipped registry lists **no** sets. No existing art (unapproved or rejected) becomes accepted or default.
- The 32Ã—48 placeholders are not used as evidence.
- Every set loaded in these checks is a TEST-ONLY diagnostic fixture: hazard-striped boxes with an arrow for the facing, bars for the frame number, and a colour-coded ID patch. They prove which frame the runtime selected and drew. They say nothing about smooth motion or character design. No fluidity claim is made.

The production ledger, Game Bible and Site were not edited or credited. Nothing was pushed.

## Code changes

| File | Change |
|---|---|
| `game/scripts/exploration_sprite_set_pilot.gd` (new, + `.uid`) | Flag and registry handling, manifest and frame validation, session cache, and a per-avatar driver node (time-based cadence, idle/walk/facing state). |
| `game/scripts/scifi_exploration_area.gd` | +13 lines. `attach()` after the hero is built. `face()` / `walk()` / `idle()` early-outs in the three existing texture functions. |
| `game/scripts/survey_annex.gd` | The same +13 lines. |
| `game/scripts/â€¦chicago-loop_state-lake-block-scene_unapproved-v02_â€¦-55667f46.gd` | The same +13 lines. This is the default Loop scene, reached through the opt-in selectors, which extend it. |
| `game/data/exploration-sprite-sets/â€¦registry_no-approved-sets-v01_â€¦.json` (new) | Default registry with `actors: {}`. It ships in exports via the `data/*.json` include filter. |

The WDC v12/v12r1/v12r2/v13 selectors inherit the area script, so the pilot also works under those opt-ins. The pilot drives its own clock (child node, `process_priority = -1`), so the selectors' `_process` override needs no edit. `battle_arena.gd`, `app_state.gd`, settings and combat helpers are untouched. Movement, collision, interactions, y-sort, occlusion, the city canopy silhouette and save data are unchanged: hooks only swap the Sprite2D texture, scale and offset, and the module never reads or writes AppState or saves.

## Contract for artists (schema `worlds-between.exploration-sprite-set.v1`)

One JSON per actor. Frame files are listed relative to the JSON (or as `res://` paths). Values follow the master cell of the [sprite production pipeline](../design/rpg-2-star-ocean-the-second_character-sprites_pixel-art-production-pipeline_unapproved-v01_20261015-040155-ffd3391d.md) and heroine v8 (80Ã—112, 43Ã—96 visible, alpha rows 8â€“103):

```json
{
  "schema": "worlds-between.exploration-sprite-set.v1",
  "set_id": "protagonist-female-hd2-v01",
  "actor_id": "protagonist-female",
  "density": 2,
  "frame_size": [80, 112],
  "pivot": [40, 104],
  "actions": {
    "idle": {"south": [{"file": "â€¦_south-idle-f1_â€¦.png", "duration_ms": 470}, â€¦], "west": [â€¦], "north": [â€¦], "east": [â€¦]},
    "walk": {"south": [{"file": "â€¦_south-walk-f1_â€¦.png", "duration_ms": 130}, â€¦], "west": [â€¦], "north": [â€¦], "east": [â€¦]}
  }
}
```

The validator rejects the **whole set** if any rule fails. The actor then keeps the legacy textures; frames are never mixed.

| Field | Rule |
|---|---|
| `schema`, `actor_id` | Exact schema string. `actor_id` must equal the registry key (`protagonist-female`, `protagonist-male`, â€¦; the host uses `"protagonist-" + AppState.hero_appearance`). |
| `density` | Integer 2â€“4 (texels per logical px). Display scale is `1/density`. Density 2 with an 80Ã—112 cell gives 1 texel = 1 window px at the default 1280Ã—720 window. |
| `frame_size` | `[w, h]`, at most 64 logical px each way. Every frame must be exactly this size. |
| `pivot` | `[x, y]` ground pin in texels. `y` is the floor line under the soles (last opaque row + 1); for the master cell this is `(40, 104)`. |
| `actions` | Exactly `idle` and `walk`, each with exactly `south`, `west`, `north`, `east`. Idle has 1â€“16 frames, walk 2â€“16. Mirrored facings are not supported: author all four. |
| `duration_ms` | Integer 40â€“2000 per frame. Cadence is time-based. Both actions loop. |
| Frames | Imported `res://` Texture2D, readable and uncompressed (the default lossless import). Binary alpha (0/255). Nothing opaque on the cell border. Nothing at or below the floor line. Body at most 48 logical px + 1 texel tall. |
| Idle frames | Soles end exactly on the floor-line row. Body is 48 logical px Â±1 texel (96 Â±1 at density 2), the 48-logical exploration display. |

Registry (schema `worlds-between.exploration-sprite-set-registry.v1`): `{"schema": â€¦, "actors": {"<actor id>": "<set json>"}}`. The default registry is `game/data/exploration-sprite-sets/â€¦no-approved-sets-v01_â€¦.json`. A run can point elsewhere with `--exploration-sprite-set-registry=<res:// or user:// path>`. Adding a set to the default registry is a content/approval decision and is not part of this task.

Runtime placement:

- `sprite.offset = frame_size/2 âˆ’ pivot + (0, density)` with `centered = true`. The floor line is drawn **1 logical px below the node position**, so HD soles sit on the same logical row the legacy 32Ã—48 soles occupy (texel row 44 at offset (0, âˆ’20)).
- Collision points, interaction radii, y-sort pivots, occlusion polygons and the WDC camera all stay keyed to the same feet position.
- Note: older v8 review harnesses drew v8 at offset (0, âˆ’40), which puts its soles 3.5 px lower. The pilot follows the pipeline's pin instead.

Behaviour:

- Any change of action or facing restarts at frame 0, matching legacy behaviour. The avatar is idle whenever it did not move that frame: stopped, pushing into a wall, or with a dialogue/overlay open.
- Frames advance on a microsecond clock with carried fractional microseconds built from real frame deltas, so the frame shown depends on elapsed time, not frame rate.
- Each set is loaded and checked once per session (24 texture loads for a 2+4-frame set, about 0.1 s) and then cached. Drawing never reads files.
- Rejected sets and registries print one `push_warning` with the reasons.

## Verification (13/13 final gates pass)

The evidence check orchestrates every run: `python -I tools/rpg-2-star-ocean-the-second_exploration-sprite-set-pilot_evidence-check_v01_20261018-153932-9f31902d.py`. It takes about 2.5 minutes and uses an isolated APPDATA/LOCALAPPDATA under `%TEMP%`, so real saves and preferences are untouched. Results are in the [evidence report / manifest](../../outputs/spriteset-pilot-9f31902d/rpg-2-star-ocean-the-second_spriteset-pilot_evidence-report_20261018-153932-9f31902d.json), which includes sha256 (text-lf-v1 / bytes) for code, tools, fixtures and captures.

| Gate | Result |
|---|---|
| G01 fixtures | 55 fixture files rebuild byte-identically. |
| G02 logic, 12/12 | **Flag and registry:** flag off reads no file and leaves the sprite untouched. The default registry is valid and empty, so every actor stays legacy. Actor ids pick their own set; unknown or empty ids fall back. 48 logical display: scale 0.5, offset (0, âˆ’46). **Cache:** 24 loads per set and none during 600 frames of play. **Malformed input:** 21 malformed cases each reject the set for the intended reason (missing or non-texture file, wrong size, partial alpha, border, floating idle, missing or unknown direction, extra or missing action, 1-frame walk, bad durations, density 1/5, bad pivot, declared-size mismatch, actor mismatch, schema). **Partial set:** a set with 23/24 valid frames is rejected whole, the sprite keeps its legacy texture/offset/scale, and the other actor's valid set still loads. **Bad registries:** 6 cases fall back. **Timing:** 30/60/144 fps and a 0.75 s hitch land on the analytic frame. **Transitions:** see Behaviour above. |
| G03 gameplay at `--fixed-fps 60` and `30` | Uses the real CLI flags. Six scenes are entered the way the game enters them: area city, outskirts and ruins; annex city room 1 and ruins room 2; Chicago Loop (v02 via the Loop selector). The real `move_*` actions walk a rectangle with idle stops. **Every rendered frame** (2,172 at 60 fps) is read back: the ID patch matches the pilot's (actor, action, facing, frame), and the outline spans exactly 48 rows with the soles on the legacy row. All 48 states (2 actors Ã— 4 facings Ã— (2 idle + 4 walk)) are seen on screen. The female and male sets switch with `hero_appearance`. |
| G04 cadence | In both runs every tick shows the analytic frame for its clock. Equal-clock ticks agree across 30/60 fps (0 mismatches; ticks within 1 ms of a boundary are skipped). Each leg ends on the same position. A state change is seen on the first frame after the input changes: 1/30 s or 1/60 s, which is input sampling, not cadence. |
| G05 captures | 12 bilingual 640Ã—360 and 2 at 1280Ã—720, each verified on screen. |
| G06 motion | 30 rendered frames, all verified. |
| G07 default parity | 45 captures (9 scene types incl. annex room 1 Ã—3 and room 2 Ã—2, entry zh/en, walk east, walk north, stopped) are **pixel-identical** across: the base tree (origin/main `3e040a9`, exported), the base again (noise check), this branch with the flag off, and this branch with the flag on and the shipped registry. |
| G08 | The parity walks really move the hero in all 9 scenes. |
| G09 accepted rooms, 8/8 | The existing accepted-rooms replay (NYC rooms 1 and 2, Yonkers room 2; read-only) is byte-identical to the eight acceptance-record images with the flag off, the flag on with the shipped registry, and the flag on with the fixture registry. |
| G10 | The runs write no tracked game file. |

## Evidence captures (separate files, no contact sheets; diagnostic fixtures, not art)

640Ã—360, zh and en for each:

- City, female walk east f3: [zh](../../outputs/spriteset-pilot-9f31902d/rpg-2-star-ocean-the-second_spriteset-pilot_city_female-walk-east-f3_zh_test-only_20261018-153932-9f31902d.png), [en](../../outputs/spriteset-pilot-9f31902d/rpg-2-star-ocean-the-second_spriteset-pilot_city_female-walk-east-f3_en_test-only_20261018-153932-9f31902d.png)
- Outskirts, male walk south f4: [zh](../../outputs/spriteset-pilot-9f31902d/rpg-2-star-ocean-the-second_spriteset-pilot_outskirts_male-walk-south-f4_zh_test-only_20261018-153932-9f31902d.png), [en](../../outputs/spriteset-pilot-9f31902d/rpg-2-star-ocean-the-second_spriteset-pilot_outskirts_male-walk-south-f4_en_test-only_20261018-153932-9f31902d.png)
- Ruins, female walk west f3: [zh](../../outputs/spriteset-pilot-9f31902d/rpg-2-star-ocean-the-second_spriteset-pilot_ruins_female-walk-west-f3_zh_test-only_20261018-153932-9f31902d.png), [en](../../outputs/spriteset-pilot-9f31902d/rpg-2-star-ocean-the-second_spriteset-pilot_ruins_female-walk-west-f3_en_test-only_20261018-153932-9f31902d.png)
- Annex city room 1, male walk north f2: [zh](../../outputs/spriteset-pilot-9f31902d/rpg-2-star-ocean-the-second_spriteset-pilot_annex-city-r1_male-walk-north-f2_zh_test-only_20261018-153932-9f31902d.png), [en](../../outputs/spriteset-pilot-9f31902d/rpg-2-star-ocean-the-second_spriteset-pilot_annex-city-r1_male-walk-north-f2_en_test-only_20261018-153932-9f31902d.png)
- Annex ruins room 2, female idle south f2: [zh](../../outputs/spriteset-pilot-9f31902d/rpg-2-star-ocean-the-second_spriteset-pilot_annex-ruins-r2_female-idle-south-f2_zh_test-only_20261018-153932-9f31902d.png), [en](../../outputs/spriteset-pilot-9f31902d/rpg-2-star-ocean-the-second_spriteset-pilot_annex-ruins-r2_female-idle-south-f2_en_test-only_20261018-153932-9f31902d.png)
- Chicago Loop, female idle east f1: [zh](../../outputs/spriteset-pilot-9f31902d/rpg-2-star-ocean-the-second_spriteset-pilot_chicago-loop_female-idle-east-f1_zh_test-only_20261018-153932-9f31902d.png), [en](../../outputs/spriteset-pilot-9f31902d/rpg-2-star-ocean-the-second_spriteset-pilot_chicago-loop_female-idle-east-f1_en_test-only_20261018-153932-9f31902d.png)

1280Ã—720 (the default window; shows the 2Ã— texel density):

- [City, walk east f3](../../outputs/spriteset-pilot-9f31902d/rpg-2-star-ocean-the-second_spriteset-pilot_city_female-walk-east-f3_zh-1280x720_test-only_20261018-153932-9f31902d.png)
- [City, idle east f2](../../outputs/spriteset-pilot-9f31902d/rpg-2-star-ocean-the-second_spriteset-pilot_city_female-idle-east-f2_zh-1280x720_test-only_20261018-153932-9f31902d.png)

Normal 1Ã— motion:

- [City walk-then-stop APNG](../../outputs/spriteset-pilot-9f31902d/rpg-2-star-ocean-the-second_spriteset-pilot_city_walk-stop-motion-30fps-1280x720_test-only_20261018-153932-9f31902d.png): 30 rendered frames (1.0 s), 1280Ã—720, at `--fixed-fps 30`. The encoder merges identical consecutive idle frames, so the file stores fewer frames with summed durations. It is a diagnostic of selection and timing only, not a fluidity claim.

## Known limits and follow-ups

- **Avatar only.** NPC sprites (`city_npc`, `field_npc`) keep their legacy static idles.
- **Chicago candidate scenes not wired.** The Chicago v03/v03r1/v04/v05 candidate scenes are separate opt-in script copies and were not wired. Their flags hand over before the v02 code runs, so with those flags the avatar is legacy.
- **Labels draw over the avatar.** World labels (CanvasLayer) draw on top of the avatar; this is existing behaviour. The check paths were chosen to stay clear of them.
- **Existing English header overlap.** The annex English header overlaps the Save button in the captures. This is pre-existing and unrelated to the pilot.
- **Non-nominal first-frame delta.** The first frames after entering a scene can carry a non-nominal delta even under `--fixed-fps`; one 30 fps tick was 41.7 ms. Legacy movement and the pilot clock both integrate it. The frame shown stays analytic for its clock.
- **Historical checks flip by design.** Editing the three host scripts was required, so two older candidate checks that pin them will report a change:
  - The WDC v13 flag-deterministic check, gate D03, which requires `scifi_exploration_area.gd` and `survey_annex.gd` to be identical to `6406bb8`.
  - The WDC annex-rooms layout-fix evidence check, which hash-pins `survey_annex.gd` as a dependency.

  The Chicago v02 source check only regex-reads constants, which are unchanged.
- **Godot import side effects.** Running `--import` on a fresh tree rewrites tracked `.import` sidecars to LF, and writes sidecars for other sessions' untracked PNGs. These were reverted or removed and are not committed. The fixture `.import` files are committed (same lossless defaults as v8).
- **No approval.** Nothing here is approved; adopting a real set is for the content and creator-approval tasks.

## Codex takeover and independent verification — 2026-10-18

The creator authorized Codex implementation during Max gaps. Codex finished the interrupted capability without further Claude calls.

- Fixed a real shared-boundary defect: rounding each delta gave 399996us at 30fps and 400008us at 60fps for the same 400ms. Fractional microseconds now carry between ticks and reset with action/facing changes.
- L09 uses independent literal duration expectations and checks the accumulated clock at every sample, including boundaries, at 30/60/144fps. No +/-1ms sample exclusions remain. L11 checks shared 400/800/2400ms and 10s loop boundaries explicitly.
- The final evidence checker rejects SCRIPT ERROR even on exit0. Gameplay cross-rate comparisons require equal clocks within1us and skip no boundaries.
- Final run: 13/13 gates passed, logic12/12, actual48states rendered at30/60fps, 12bilingual captures, 2density captures, 30motion diagnostic frames. Default render parity passed and all8accepted-room replay images remained pixel-identical in each tested configuration.
- Root personally inspected the fresh English Chicago capture and Chinese WDCroom2 capture: the diagnostic avatar is drawn in the actual scene. The WDCdefault room shown here is not a new fixture-art or scene approval.
- These hazard-striped test avatars prove loading/selection/placement. They are not character art and supply no fluidity or full-sprite approval. Existing known limits above remain.

Final source/tools/fixtures and selected capture hashes are in the linked evidence report. No scoring or approval records were edited by this producer.
