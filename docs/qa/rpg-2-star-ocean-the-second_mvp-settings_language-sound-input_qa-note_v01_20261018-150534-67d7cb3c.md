# MVP settings (language, sound, input) — QA note v01

- Task: remaining MVP coding task `code.ui.settings` ("Language, sound, input settings").
- Status: TECHNICAL coding capability. The UI uses native Godot controls and is functional. Final UI art is UNAPPROVED. Not pushed; waiting for root review.
- Base: origin/main 7e5f74c, branch `codex/mvp-settings-ui-20261018-1510`.
- Evidence: `outputs/mvp-settings-v01_20261018-150534-67d7cb3c/`. The manifest pins every source, capture, index and log hash, plus the accepted-room parity rows.
- Not changed: art, sprite and playtest counters, the progress ledger, the Game Bible, the Site, save formats and save data.

## What it does

| Area | Behaviour |
| --- | --- |
| Entry | The title screen has a new **设置 / Settings** button, sharing the last row with Quit so the column still fits in 360 px. **F10** opens the overlay anywhere. F10, Esc or the Close button closes it. |
| Pause | Opening sets `get_tree().paused = true`. Closing restores the earlier value. The previous GUI focus owner gets focus back, or focus is released if there was none. The battle's own pause menu (`battle.paused`) is never touched, so a battle that was already paused stays paused with its menu and focus intact. `GameSettings` runs with `PROCESS_MODE_ALWAYS`, so the overlay stays usable while everything under it is paused. Paused scenes receive no input, and any key the overlay does not use is consumed in `_unhandled_input`. |
| Language | 中文 / English buttons call the existing `AppState.toggle_language()` and `language_changed` signal. There is no second language state. Screens under the overlay relabel straight away. |
| Volume | Master 0–100 in steps of 5, applied to the existing `Master` bus with `linear_to_db(v/100)`. 100 gives exactly 0.0 dB, the bus default. 0 mutes the bus rather than using −inf dB. No audio assets were added. |
| Movement preset | **Default (WASD / arrows)** keeps exactly the events `_install_default_controls()` created; they are captured at startup and put back as-is. **Arrow keys only** keeps just the arrow-key events on `move_left/right/up/down`. No other action changes. There is no free rebinding. |
| Key hints | Under the arrow preset, `AppState.text_for()` returns a `*_arrows` variant for the five help lines that name movement keys: `area_help`, `survey_help`, `room_help`, `battle_help` and `setup_controls`, in zh and en. Every scene already reads its help through `text_for` and refreshes on `language_changed`, so no scene script changed. Under the default preset, `text_for` output is unchanged. |
| Reset | **Reset controls & volume** restores the exact default bindings and 100 % (0 dB). The language is left as it is. |
| Storage | Preferences live only in `user://settings.cfg` (`[settings]` version, language, master_volume, movement_preset). The file is written only by actions in the Settings overlay. The title-screen language toggle still does not persist, as before. A missing file means nothing is applied. An unreadable or wrong-typed file falls back to defaults and is not rewritten at startup. Saves are untouched: loading a save still sets the language from the save, as before. |

## Checks run (official Godot 4.7.2, APPDATA isolated to `%LOCALAPPDATA%\Temp\mvp-settings-1510\appdata`)

- **Settings check**, `game/tests/…_mvp-settings_overlay-check_v01_…67d7cb3c.gd`, windowed at 640×360, run as four separate processes so real restarts are covered. It refuses to run unless the user data dir is the isolated one.
  - `fresh`, 65 checks:
    - No file → language, preset, volume and every InputMap action (104) match the origin/main dump.
    - Title layout fits.
    - The title toggle writes nothing.
    - A real mouse click opens the overlay and pauses the tree.
    - zh/en apply and persist.
    - Volume: 0 mutes; a real keyboard step works while paused (5 %); 40 % sets the gain.
    - Arrow preset: movement uses arrow keys only and everything else is unchanged; zh/en hints follow.
    - Reset restores exact defaults.
    - F10 and Esc close the overlay and restore focus.
    - Exploration guard: E, Right, D and J held for 8 frames under the overlay cause no movement and no dialogue. Esc closes the overlay without leaving the area. Positive controls after closing: E interacts, Right moves, D no longer moves under the arrow preset.
    - Battle guard: J, K, P, Tab, T and Left under the overlay cause no attack, dodge, pause, swap, auto or movement. Positive control: J attacks after closing.
    - An already-paused battle keeps its pause menu and focus.
    - A tree that was already paused stays paused.
    - No layout overflow in zh or en on the title screen, the overlay, or the exploration and battle hint labels.
    - The prefs file holds only the four keys, and no save was written.
  - `restart`, 4 checks: en, 40 % and arrows are applied at startup with matching bindings and hints. Reset restores exact defaults.
  - `corrupt`, 6 checks: an unreadable file gives exact defaults and is left as it was. The engine logs its own `ConfigFile parse error`, which is expected.
  - `invalid`, 10 checks: wrong types give exact defaults. Volume clamps to 100 above range and to 0 (muted) below range.
- **Default parity without a prefs file**: `tools/…_mvp-settings_input-audio-baseline-dump_check-v01_…201f58ff.gd` was run on origin/main before any edit and on the candidate. The JSON dumps (all 104 actions, Master bus volume, mute state, bus count, language) are byte-identical.
- **Accepted rooms**: the existing replay `tools/…_wdc-annex-room1_v02-review-gate-accepted-rooms-replay_check-v01_…03286bf3.gd` was run on origin/main and on the candidate. All 8 of 8 captures are byte-identical (NYC room 1 zh/en, NYC room 2 zh/en + approach + interaction, Yonkers room 2 zh/en). The overlay is built only on first open, so nothing renders while it is closed.
- **Smokes (headless)**: M1_SMOKE_OK, M3_SMOKE_OK, M6_SMOKE_OK, M6_RESTART_OK.
- Not run: the full regression sweep (not requested) and the M2/M4/M5/M7/M8 smokes.

## Captures (640×360, committed)

`title-zh`, `title-settings-zh`, `title-settings-en`, `exploration-arrows-hint-en` (closed, arrow hint in the HUD), `exploration-settings-en`, `battle-settings-zh`. The battle capture shows 35 % because it was taken after the guard step: Tab moved overlay focus to the slider and Left lowered it. This shows that keys under the overlay drive the overlay UI, not the game. `title-en` and `battle-settings-en` were also captured and are sha-pinned in the fresh index, but are kept local.

## Still unproven / limits

- Audio players pause along with the tree, so a volume change made inside the overlay can't be heard until it closes. There is no preview sound, because no new audio assets were allowed.
- Joypad input was not exercised. The defaults have no joypad bindings for movement.
- The volume steps are 5 %. A hand-edited non-multiple such as 42 is applied as stored, but the slider shows the nearest step.
- F10 is not blocked during scene transitions. It was not tested mid-`change_scene_to_file`.
- Ambient audio level by ear at 100 % was not checked by listening. Only the bus state was proven equal to origin/main: 0.0 dB, unmuted, 1 bus.
- The UI look is native and functional only. Art approval is out of scope for this coding capability.
