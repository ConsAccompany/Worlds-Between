# Legacy ambience: missing loop end repaired

This is a separate, routine playback bugfix. It adds **only three guarded loop bounds** to the pre-music scene sources at `8d56d51aeb7adc9e2886a9f7b3297be4d4c49543`; it does not introduce themed music, change assets, players, gains, Master/settings or simulation. The integration coordinator stages these exact separately generated repaired-reference bytes, preserving the opt-in music changes as later work.

## Cause and actual behavior

The existing imported eight-second QOA ambient streams had `LOOP_FORWARD`, `loop_begin=0`, **`loop_end=0`**. In original frozen area/battle scenes and pilot-off candidates, `playing` initially appeared true but became false at the first audio mix and stayed false around 300 ms. One arbitrary process-frame observation could occur before or after that mix; this caused the earlier music probe's nondeterministic player-state result. CRLF-to-LF normalization exposed the timing but did not change the audio behavior. The final-LF failure (2708/2710) is retained, not retried away.

The causal diagnostic changed only the duplicated stream's local `loop_end` from 0 to 176,400 frames (8 × 22,050), retaining identical imported PCM/player. Those controls remained playing around 300 ms and playback position advanced to roughly 0.284 seconds, while unmodified controls stopped. Observations/logs are in `outputs/themed-music-v01/*startup-observations*` and `*loop-bound-control-observations*` with tag `20261019-215712-539684bf`.

## Exact repair

Immediately after the existing `stream.loop_mode = AudioStreamWAV.LOOP_FORWARD`, for each local stream variable:

```gdscript
if stream.loop_end <= stream.loop_begin:
    stream.loop_begin = 0
    stream.loop_end = int(round(stream.get_length() * stream.mix_rate))
```

The guard preserves any already valid loop, including all four separately produced new themes. It intentionally changes the defective legacy default's loop end; **default loop metadata is not claimed identical to the broken original**. Imported sound bytes, stream format/rate/stereo, player count/gain, Master bus and all game state remain unchanged.

The three repaired control scripts and source map are `outputs/themed-music-v01/*repaired-baseline-only*` and `*repaired-baseline-source-map*`, tag `20261019-215839-2a99d440`. The original three `*frozen-before-wiring*` controls and their hashes remain untouched. Each repaired reference is exactly the original HEAD source plus the three guard lines above; no themed selector or override is present.

## Independent actual check

`tools/rpg-2-star-ocean-the-second_music_legacy-loop-repair-check_v01_20261019-215839-2a99d440.gd` verifies **130 contracts** in a real windowed Godot process with Dummy audio:

- All three surface destinations, both annex rooms at each destination, and battle (ten contexts).
- Original zero-end failure explicitly reproduced after at least 300 ms of real time.
- Repaired identical imported PCM stays playing and advances after at least 300 ms.
- Seek to the real eight-second stream's 7.9-second point, then wait at least 350 ms; playback wraps to the beginning and remains active. No shortened loops or synthetic process-clock retiming.
- Existing player count, Master routing, volume, mute and unmute preserved.

The report records actual waits, positions, loop metadata and raw hashes of all six original/repaired controls: `outputs/themed-music-v01/rpg-2-star-ocean-the-second_music_legacy-loop-repair-report_v01_20261019-215839-2a99d440.json`.

## Diagnostics and scope

Early 130-check normal runs passed but printed two ObjectDB cleanup warnings; logs remain. A verbose same-source run passed without warnings. Deferred quit alone did not eliminate the normal-mode warning. The final harness explicitly stops/detaches player streams after observations, releases local run scope, and drains up to two actual audio-mix boundaries under a 300 ms cleanup deadline before quit. This is test-process cleanup only; no playback assertion, game code or loop timing was changed to hide the warning. See the final drained log and source-bound proof for its actual diagnostic outcome; do not infer a clean run from exit code alone.

The first diagnostic also called `get_stream_playback()` on an inactive player and emitted a harness-only error. That failed v01 log is retained, and guarded v02/v03 diagnostics completed cleanly. There is no audible listening, musical quality or creator approval claim. Themed-music production/integration remains a separate deliverable and must compare against these honestly labelled repaired controls.
