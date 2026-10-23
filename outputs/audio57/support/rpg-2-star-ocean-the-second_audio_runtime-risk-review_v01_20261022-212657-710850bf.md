# Audio runtime risk review v01 (read-only technical support, review.content.audio)

- Source: HEAD f1d2faca0a353cc2d916351eaac69ee8897850bc (working tree read, nothing edited/run in Godot)
- Scope: technical QA only. No listening/audition claim, no artistic judgment, no metric-as-audibility claim.
- Method: static source reading of the lines cited below. No Godot run, no PCK inspection (time-boxed).

## Result: no reproducible default-path audio defect found

| Risk | Finding | Evidence (game/) |
|---|---|---|
| Competing music after scene change | None. Every music/ambience player is a child of its scene, and every transition uses `change_scene_to_*`, which frees the old scene and its players. No overlay-style battle/scene stacking. | `scripts/scifi_exploration_area.gd:507-519`, `:799` (battle via `change_scene_to_packed`); `scripts/battle_arena.gd:362-372`, `:1168-1179`; `scripts/survey_annex.gd:554-566`, `:886-911` |
| Shared stream mutation | None. Fallback ambience is `.duplicate()`d before `loop_mode` and loop points are written; the themed selector builds a fresh `AudioStreamWAV`. | `scifi_exploration_area.gd:511`, `battle_arena.gd:365`, `survey_annex.gd:558`; selector `:182-190` |
| Mute / restore | Correct. 0 mutes the Master bus; any value >0 unmutes and sets dB, so restoring from 0 works. | `scripts/game_settings.gd:88-96` |
| Pause interaction | Consistent. The settings overlay pauses the tree (`game_settings.gd:131-147`, restores the earlier pause state). Scene music players inherit pause (music pauses). The cue node is `PROCESS_MODE_ALWAYS` (`game_audio_cues.gd:55`), so UI cues still play in the overlay. Design behaviour, not a defect. | as cited |
| Preferences safety | Missing/corrupt/invalid config is handled field by field; volume is clamped to 0-100 and only an int/float is accepted. | `game_settings.gd:43-68` |
| Missing SFX asset | Cues fall back to generated PCM when an asset is missing or unusable (`ResourceLoader.exists` + `usable_asset`). The cue pilot is off by default (`--audio-cues-pilot`). | `game_audio_cues.gd:6`, `:120-142` |

## One unverified packaging risk (opt-in pilot only, not a default blocker)

The themed-music selector (`--themed-music-pilot`, off by default) reads the **raw** WAV bytes with `FileAccess` (`scripts/audio/...themed-music_selector_v01_20261019-212037-7f3c2a26.gd:310-315`). The `.wav` files under `assets/music/themed-v01/` are imported resources. `export_presets.cfg:8-9` uses `all_resources` with `include_filter="data/*.json,assets/*.json,*.pxo"`, and no `*.wav` pattern is in that filter. Godot normally exports imported WAVs as `.import`/`.sample` remaps rather than the raw source file. If that holds here, packaged builds started with `--themed-music-pilot` would get `null` from the selector and silently fall back to the legacy ambience. That fallback is safe: nothing crashes and no music overlaps. But the pilot would not be exercised in packaged builds.

Status: **not reproduced**. I did not list the PCK contents.

Minimal check for the coordinator:
1. List the developer/native PCK entries, e.g. `Godot_v4.7.2-stable_win64_console.exe --headless --path game` with a bounded script that opens the pack, or any PCK lister. Look for `res://assets/music/themed-v01/*_audio_v01_*.wav` as a raw entry, as opposed to only `.wav.import` plus `.godot/imported/*.sample`.
2. If the raw WAV is absent and the pilot needs to work in packaged builds, add `assets/music/themed-v01/*.wav` to `include_filter` (or load through `ResourceLoader`). Then rerun the existing themed-music selector tests and one packaged launch with `--themed-music-pilot`.
3. If packaged pilot audio is out of MVP scope, record it as a known limitation. No default-path change is needed.

No fix applied; left to coordinator.
