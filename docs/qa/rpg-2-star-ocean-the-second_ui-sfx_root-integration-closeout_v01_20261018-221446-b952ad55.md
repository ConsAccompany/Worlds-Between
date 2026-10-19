# UI sound content: root integration closeout

Task `content.audio.ui-sfx`, ownerClaude; Codex coordinator independently inspected and integrated. Frozen criterion: UI sounds committed and wired. The three original authored44.1kHz16-bit mono WAVs (confirm/cancel/notice), deterministic editable source and minimal actual menu/save hook mapping meet that production criterion after the selected commit. Credit only the existing2content points. No new task/denominator or sound-quality approval.

## Independent verification

- Root compared producer base0b0e7d9 to canonical pre-port game scripts: identical LF-normalized bytes before applying the diff. Changed production files: game_audio_cues.gd (+49/-5), game_settings.gd (+2), save_screen.gd (+3). Other code content/defaults unchanged.
- Root reran deterministic double WAV rebuild and signal verification45/45: delivered bytes exact;90/120/300ms;peak-14dBFS;no clipping;quiet endpoints;lowDC;distinct waveform/envelope and consistent levels. This is signal evidence, not listening.
- Godot editor import of three new WAVs passed through the bounded runner. First root windowed attempt at1280×720 failed34/43 because the producer test passed640logical mouse coordinates to window-coordinate Input.parse_input_event. Keyboard and direct playback worked; button events missed. Preserve this failing report/log. The old test was explicitly scoped640×360 and is retained unchanged.
- New root v02 test uses the documented `Viewport.push_input(event,true)` for viewport-local mouse positions, keeping key-event and Control handling paths. Independent exact40ms acceptance added alongside39/41ms checks. Actual windowed WASAPI runs pass44/44 at1280×720 and44/44 at640×360, with the same production code/assets. These are engine-injected events through normal GUI handlers, not physical desktop clicks or a human playthrough.
- Imported data hashes match all three WAV PCM data chunks. Actual AudioStreamPlayers run; Master recording non-silent (~-27.28dBFS peak). Mute/40%volume/defaultOFF, single-click supersession, finite voices/cache, missing/wrong-type/looping-asset fallbacks, unchanged game state except running play clock, same-frame full-snapshot equality and procedural combat cues pass. No human hearing audition claimed.
- Producer prior audio46headless/47windowed, settings fresh/restart/invalid, save494checks andM7 smoke preserved. Deliberately corrupt settings phase emits ConfigFile error and remains a runner failure, not reported as clean success. Original parse/edge and stdout-encoding failures retained.

## Scope and limits

Pilot defaultOFF (`--audio-cues-pilot`); UI content available through existing controls when enabled. Save success notice/Back/settings close replace generic clicks. World-map/exploration Esc and failed-save-specific sound remain outside this bounded mapping. Per-player gain remains-14dB in addition to WAV peak. Warm/tactile are design intent until audition. Audio content QA depends on themed tracks and combat sounds too and stays open; no accepted-scene/sprite/playtest change.

Source normalization is explicit: WAVs raw SHA256, source/code/reports LF-normalized SHA256 (CRLF→LF only). Producer's full manifest is frozen provenance for its tested base. The root integration manifest binds the selected current code and independent evidence separately. GUI scale correction reference: [Godot Viewport.push_input](https://docs.godotengine.org/en/stable/classes/class_viewport.html#class-viewport-method-push-input).

The first root failure log contains a literal trailing space emitted by the test. Its selected delivery is a lossless `.log.gz`; decompression reproduces the original bytes exactly (raw SHA256 fb83947175fcee2b90bbff635f99e11deb87243b5d9b5d7e6f9dcf37ccf4fb79). The original local log is preserved. No failure content was trimmed to satisfy the whitespace gate.
