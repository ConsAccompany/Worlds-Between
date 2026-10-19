# UI interface sounds v01: production candidate (content.audio.ui-sfx)

Owner: Claude (Max, firstParty). Producer checkout `work/max-ui-audio`, base `0b0e7d915324686a8cf29cf74c4b3b6841cf3fa4`, uncommitted. Not integrated, not auditioned by a listener, not approved.

Manifest: `outputs/ui-sfx-v01_b7ad3396/rpg-2-star-ocean-the-second_ui-sfx_source-and-check-manifest_v01_20261018-215528-b7ad3396.json`, sha256-text-lf-v1 `d750ea1a1dc34a7b4b14a9ece1b78e51a4fc7c77f2e3bb21b906980b342c39c6`. It binds every source, code, import and evidence file by hash.

## Content

All three cues are original synthesis from `tools/rpg-2-star-ocean-the-second_ui-sfx_wav-source-builder_v01_20261018-215528-960dcf71.py`. That source uses shaped sine partials, exponential pitch glides, a low felt knock, and LCG noise through one-pole filters. No samples or generation services were used. Format: 44.1 kHz, mono, 16-bit PCM, peak −14.0 dBFS. Godot imports them uncompressed (`compress/mode=0`).

| Event | Design | Length | sha256-bytes |
| --- | --- | --- | --- |
| `ui.confirm` | felt tap + short rising pip to G5 | 90 ms | `329cf03a0581318e0c693674486c1ef8fa126de899a8916df1654e90f7c5e64d` |
| `ui.cancel` | muted thump + falling C5→G4 sigh (darker) | 120 ms | `aac80c0c2516f7052e812a11e2e32362b95fa208b7e62109d1f0efca75117637` |
| `ui.notice` | two soft struck notes D5→G5, open fourth | 300 ms | `e25466d79530edd78fcb90151f6bbd129f6a9939366d145ab85990d298dd1ff7` |

## Wiring (default OFF, `--audio-cues-pilot`)

- `game_audio_cues.gd`:
  - `ASSETS` paths are loaded with `ResourceLoader.exists`/`load`.
  - `usable_asset` requires 16-bit mono 44.1 kHz audio, no loop, and at most 1 s. A missing, wrong-type or wrong-format asset falls back to the generated PCM.
  - Within the existing 40 ms window, a cancel or notice cue replaces the generic confirm click from the same press.
  - The 4 voices, per-event cache, Master bus routing and −14 dB player gain are unchanged.
- `game_settings.gd` `close()` plays `ui.cancel`. This covers F10, Esc and the Close button on every screen.
- `save_screen.gd`: a successful manual save plays `ui.notice`, and Back plays `ui.cancel`.
- Combat cues and their generated PCM are unchanged.

## Checks

- WAV verify:
  - try1 FAILED 44/45 (confirm edge 0.0245 FS). Fixed in the source with a 1.2 ms fade-in; the threshold was not changed.
  - try2: 45/45. Covers deterministic double rebuild, delivered bytes equal to the rebuild, format and frame count, peak and DC, endpoints, step size, levels (2.6 dB spread), and distinctness (xcorr < 0.08).
- Windowed wiring probe (checked runner, 90 s): try4 43/43, `UI_SFX_WIRING_OK`. It covers:
  - Default OFF.
  - Real F10/Esc keys and real mouse clicks on the overlay Reset/Close and the save screen Save/Back.
  - Asset identity: the imported data sha equals the WAV data chunk.
  - Voices actually playing.
  - Non-silent Master-bus recording.
  - Mute and volume.
  - 39/41 ms coalescing boundary.
  - Supersession.
  - Bounded voices and cache.
  - Missing, PNG and looped-WAV fallback.
  - Combat cues still procedural.
  - Snapshot unchanged.
- Earlier tries were kept:
  - try1: parse error in the probe.
  - try2: 41/42. The snapshot comparison spanned frames in which the play clock advanced; the check was corrected.
  - try3: 43/43, but the runner's console print crashed on cp1252.
- Regressions: prior audio-cue test 46/46 headless and 47/47 windowed (one rate-predicate edit). Settings fresh/restart/invalid pass. Save-UI smoke 494 checks pass. M7 smoke passes.
- The settings `corrupt` phase reaches PHASE_OK but is a runner FAIL, because the engine logs `ConfigFile parse error`. That phase provokes the error on purpose, and the same line appears in the original settings delivery log.

## Limitations / next

- No listening audition happened. The quality claims rest on design intent and signal checks only.
- World-map and exploration Esc paths stay silent.
- Next: root verification and integration, then Codex in-game listening (`review.content.audio`) and creator acceptance.
