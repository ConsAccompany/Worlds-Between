# Heroine battle static, Sea of Stars v01: QA note (UNAPPROVED)

Task: content.combat.protagonist-female.combat-static.revision. Owner: Claude. Base: f2f5f04 in the cl-hero-style worktree (nothing committed). Status: technical static candidate only. It is not approved art, has no motion, is not adopted as the default, and makes no game-source change.

## Method

This replaces the v17r2 procedural texel authoring, which the creator rejected.

- **Input:** the Codex-selected generated key pose `rpg-2-star-ocean-the-second_heroine_battle-keypose-generated-input_unapproved-v01_20261020-181640-a8fdf0f7.png` (sha256 recorded in the manifest).
  - It is pixel-looking but not on a clean grid: FFT pitch is about 8.0–8.9 source px.
  - It is not native pixel art. Its generator settings are unknown to this tool.
- **Resampling:** one step, 9.5263 source px per texel, onto the existing 136x144 native cell.
  - Occupied rows are 3..135, the same as v17r2, so there is no hidden scale change.
  - The pin is (64,136) native, which is (32,68) logical. The lowest sole of both boots is on row 135, and the pin column is the midpoint between the boots.
  - Each texel takes the palette-index mode of the central 60% of its source cell. Alpha needs at least 50% coverage, and the source alpha threshold is 128.
- **Palette:** 30 colours. 26 come from a median-cut over all opaque pixels. 4 come from a separate median-cut over the blade steel.
  - This was the one concrete correction: in the first preview, the global cut had turned the blade beige.
- **Curation:** fixed rules only, with 0 hand-painted texels.
  - 3 stray-alpha texels removed and 4 pinholes filled.
  - 52 interior speckles merged into their neighbours. Eyes, brows and mouth inside the face box are exempt.
- **Layers:** legs, body, scarf, weapon, hair and head. They are mask slices that partition the one flattened still; nothing is painted behind another part. The rules are in the manifest under `layerRule`.

## Results

| Check | Result |
|---|---|
| Tool `check` (determinism, partition, PXO/ORA equality, pin, margins, proportion, on-disk bytes) | PASS 21/21 |
| Pixelorama 1.2.3 headless export, PXO and ORA, split layers and flat | EXACT 4/4, exit 0 |
| Pixelorama application diagnostics (unfiltered) | NOT CLEAN. PXO: `custom_samplers` shader ERROR. ORA: the same, plus "16 resources still in use", 6 leaked RIDs and a `children_cache` index ERROR. No GUI Save As was done. |
| Godot 4.7.2 actual captures (checked runner, fresh APPDATA/LOCALAPPDATA, isolated temp copy of `game` at HEAD) | 4/4 `CHECKED_RUN PASS`, 0 ERROR/SCRIPT ERROR lines |
| Arena SHA (raw, current) | d7c4fb46… matches the source |
| Party x / logical 640x360 / canvas_items | [135,171,207,243] / yes / yes |
| Changed pixels outside the hero bounds | 0 in all 8 records |
| Restored default draw equals baseline (same instance) | true in all 8 records |
| Move probe, 0.1 s at 168 px/s | +16.8 in all 8 records |

The captures are frozen static frames of a normal battle start, not a playthrough. They are in `cap-{ci1280,native640}-{default,outskirts}/`, as EN and ZH `mainhero` (baseline) and `injected` (candidate) PNGs plus a report JSON.

Note on the plates: `default` is the flat dark-purple arena. `outskirts` is the sunlit garden backdrop pilot. In this build the "bright" and "dark" labels are therefore reversed relative to the plate names.

## Visual observations at actual size (for root/creator judgement)

- **At 1280x720:** face (eyes, brows, mouth), hair mass, ponytail, scarf and blade read clearly, with clean light and shadow clusters.
- **At 640x360 native:** nearest sampling keeps 1 of every 4 texels. The eyes and face break into noise, and the body turns speckled.
- **Next to the companions:** the slim, realistic-proportion figure reads smaller and in a different style from the chibi-proportioned companions. That is a party-consistency question for the creator.
- **Selection disc:** the existing yellow disc at y 272 still overlaps the boots. This is unchanged behaviour.
- **Outlines:** gaps in the generator's outlines are kept; nothing was redrawn.
