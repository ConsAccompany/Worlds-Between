# Four themed music tracks: root technical integration

Task: `content.audio.themed-music`. Producer: DeepSeek V4.1 Flash assistance; independent verification and bounded integration: Codex. This records produced content and an opt-in technical integration, **not listening inspection or creator approval**.

## Deliverable and correction

`game/assets/music/themed-v01/` contains four separate editable score JSONs, four standard MIDI files, four 24 kHz/16-bit/stereo PCM WAV files, one deterministic renderer, one manifest and one attribution file. Fifteen files, 17,981,400 WAV bytes total. The four 16-bar themes use city 76 BPM, field 92 BPM, ruins 62 BPM and battle 116 BPM; every score uses 480 PPQ and 30,720 loop ticks.

The first producer package used the wrong project filename prefix and fabricated a composer alias / human authorship. That package was rejected. The corrected package explicitly identifies DeepSeek-assisted score/render generation and Codex coordination/inspection, claims no human composer, and retains listening/approval false. All eight final WAV/MIDI files match the rejected package's original audio/MIDI bytes exactly; only naming and provenance were corrected. The generation record's absence of supplied samples/references is an input observation, not an originality or legal clearance certificate.

The producer's existing run completed normally on 2026-10-19 at 21:49:05 UTC, exit 0. No duplicate provider inference was started for this verification. The authored package's historical `runtime_integrated=false` flag is preserved; the following root opt-in wiring is recorded separately.

## Bounded normal scene wiring

The selector is `game/scripts/audio/rpg-2-star-ocean-the-second_themed-music_selector_v01_20261019-212037-7f3c2a26.gd`.

- `scifi_exploration_area.gd`: city / outskirts / ruins select city / field / ruins.
- `survey_annex.gd`: both existing rooms at each destination select the corresponding surface theme.
- `battle_arena.gd`: battle selects the battle theme.

Each scene adds one preload, two static check overrides and a nullable stream selection inside the existing ambient-player setup. The same existing `AudioStreamPlayer`, Master bus and original -11/-12/-13 dB scene gain are used. No new player, autoload, settings, mixer or gameplay behavior is introduced. The existing ambience stream is duplicated on null (including disabled, absent or invalid package). A separately disclosed legacy loop-bound repair below corrects its invalid zero loop end; old PCM is unchanged, but original broken loop metadata is intentionally changed.

`--themed-music-pilot` is **off by default**. Static override 0 forces off and 1 forces on; the asset-directory override is a check seam. No runtime default adoption or artistic acceptance is implied.

## Independent evidence

1. **183/183** final-package checks: score form, every MIDI note-on/off timing/channel/pitch/velocity against score, tempo/meter/end-of-track, WAV format/exact sample count/headroom/DC/zero endpoints/stereo/hash/file sizes, four distinct transposition-relative opening motifs, and exact deterministic rebuild of all eight WAV/MIDI files. The parser is independent; rebuild uses frozen producer renderer source. See `outputs/themed-music-v01/rpg-2-star-ocean-the-second_themed-music_independent-final-report_v01_20261019-175000-350dd10b.json`.
2. **2710/2710 final** actual windowed game checks: three surfaces, six annex rooms and battle, with baseline/off/on runs against three **explicitly repaired loop-bound controls**. All ten contexts retain identical old-stream metadata/PCM to those repaired controls with the pilot off, zero rendered-pixel difference both off and on, and identical game state through 120 explicit process steps per run. No doubled players; all four new PCM streams, full-loop bounds, Master gain/mute/unmute and existing player gains verified. Missing / invalid packages fall back to the exact repaired legacy streams in all ten contexts. Malformed numeric types, paths, hashes, JSON and corrupted-but-rehashed WAV headers/data boundaries safely return null without script diagnostics. A real-time startup observation is bounded to 100 ms (all 30 observations were immediately playing, maximum observed wait 0.005 ms); the separate 130-check repair proof observes sustained playback after real mixes rather than relying on this initial flag. Final report/captures: `outputs/themed-music-v01/actual-repaired-2a99d440/`.
3. **18/18 final** actual CLI checks: the real pilot argument automatically selects all four themes, override 0 forces off even with the flag, and all three normal scene classes start their existing player with the selected PCM. See `outputs/themed-music-v01/rpg-2-star-ocean-the-second_themed-music_repaired-cli-final-report_v01_20261019-215839-2a99d440.json`.
4. **21/21** closeout checks: corrected filenames/provenance/attribution hash, unchanged original WAV/MIDI bytes and diagnostic records. Raw asset hashes are in `outputs/themed-music-v01/rpg-2-star-ocean-the-second_themed-music_root-closeout-proof_v01_20261019-215218-b598290c.json`. Actual runtime report binds the exact tested three scene sources and selector hashes. Source hashes use raw bytes; staging must preserve those bytes.

## Diagnostics and limits

The first 2710-check windowed run exited 0 and passed assertions but printed a cleanup warning that four ObjectDB instances leaked at exit. This warning is retained in `...runtime-log_v01_20261019-215013-95dc2f6a.log`. A same-source verbose rerun was clean, but the later final-staging failure below exposed the insufficient old-player observation window; neither historical run is used as the final sustained-playback certificate. Further legacy-proof normal runs printed two cleanup warnings; deferred quit alone did not resolve them. The final TEST cleanup stops/detaches player streams after observations and drains two actual audio-mix boundaries under a 300 ms deadline before quit. The final repaired-control **2710/2710**, **130/130** legacy proof and **18/18** CLI logs are clean, with no ERROR, SCRIPT ERROR or WARNING markers. Earlier warnings and harness-only diagnostic failures remain. No diagnostic output was filtered, no assertions were dropped, and no game changes were made for shutdown warnings. Producer-side startup-message filtering was not reused in root verification.

All actual runs used a real windowed renderer and **Dummy audio backend**. They establish stream/player dispatch, PCM, looping and settings routing, **not audible playback, musical quality, mix quality or subjective loop smoothness**. No listening or creator approval credit is claimed. Default ambience PCM and all existing accepted-art counters remain unchanged; legacy loop behavior is separately repaired as disclosed below.

## Final-staging regression diagnosis — resolved below

The coordinator's exact-staged-byte rerun, after CRLF-to-LF normalization of two scene scripts, produced **2708/2710**, with `area-outskirts-r1-off-playing-and-master` and `battle-city-r1-baseline-playing-and-master` false. The failed log is retained as `outputs/themed-music-v01/rpg-2-star-ocean-the-second_music_final-lf-runtime-log_v01_20261019-215618-c8eea47d.log`. This supersedes any unqualified final-pass claim above; native package/rebuild results remain valid.

A focused independent diagnostic found a **pre-existing old-ambience defect, not delayed startup**: the imported QOA streams report eight-second length and 22,050 Hz but are played with `LOOP_FORWARD` and `loop_begin=loop_end=0`. Frozen old scenes and current pilot-off scenes initially report playing, then stop after the first audio mix and remain stopped near 300 ms. An arbitrary one-frame sample sometimes runs before this mix, which explains the earlier nondeterministic passes. A 100 ms deadline would not repair or validate this behavior.

Diagnostic-only controls preserve the same imported stream/PCM/player and change only the local duplicated stream's end from zero to 176,400 frames (8 × 22,050). Both area and battle controls remain playing near 300 ms and advance playback position to roughly 0.284 seconds; unchanged controls stop. This proves the missing full-loop bound is causal. No game sources or WAVs were changed for the diagnostic.

Evidence: `...music_startup-observations_v01_20261019-215712-539684bf.json`, `...music_loop-bound-control-observations_v01_20261019-215712-539684bf.json` and clean diagnostic logs v02/v03. The first diagnostic v01 incorrectly requested `get_stream_playback()` while inactive and emitted a harness-only error; that failed log is retained, and a guarded query fixed the diagnostic without altering the tested game. The loop-bound repair was then implemented and sustained-playback verified; no wait-only change or relaxed predicate was used to accept the inherited failure.

## Final resolution and exact source binding

The routine legacy fix adds only a guard after `LOOP_FORWARD`: if `loop_end <= loop_begin`, set begin to zero and end to `round(get_length() * mix_rate)`. Separately labelled repaired references are generated from exact HEAD `8d56d51` plus only these guards; the original broken frozen controls are untouched. The separate QA is `docs/qa/rpg-2-star-ocean-the-second_legacy-ambience_loop-bound-repair_v01_20261019-215839-2a99d440.md`.

The separate **130/130** actual proof reproduces all ten old-context failures after at least 300 ms of real time, proves repaired identical PCM stays active and advances, seeks to the actual eight-second loop's 7.9-second point and proves wrap after at least 350 ms, and verifies existing Master/settings. It deliberately changes the old invalid loop end and records that behavior change.

After that repair, the final music v02 test retains all 2710 predicates and compares against the repaired references, with a bounded 100 ms startup observation and explicit test-process stream teardown. Final CLI checks retain all 18 predicates. Both runs use the exact same final scene/selector hashes, recorded in `outputs/themed-music-v01/rpg-2-star-ocean-the-second_themed-music_final-source-proof_v01_20261019-220314-4ed2c05d.json`. This **16/16** source-binding proof also checks all 30 startup observations, exact repaired reference hashes, clean final logs and retention of the original two failures. No native package, waveform, composition or gameplay parameter changed during the loop repair.
