# Heroine natural battle flow: QA (test-only v01)

Base `4ef439193286d271d5311987773ca3f96229c4ce`. The game source was not changed. No defect was found, so `battle_arena.gd` is untouched (raw SHA-256 `2b214b6b…3ea63`, the same as closeout b09ea1fd; loader `d3ec4a64…d2f`). This is scripted evidence from the normal game path. It is not a human playtest, a fluidity certification, art approval or default adoption.

## Method

- Harness `tools/…_heroine-natural-battle_flow-check_test-only-v01_20261020-205219-4c19e7a2.gd` (raw/LF SHA-256 `3c259040cb6e964aab600f96aab924763fad1d962ed1d674baa0692c35bca917`; ASCII, LF).
- Runner `tools/…_heroine-natural-battle_flow-runner_test-only-v01_20261020-205219-4c19e7a2.py` (`ff76280f4337369568e5f05b80373082cac10700a8d5f2f12950634bb31d6886`).
- Godot runs in a real 1280x720 window under the checked runner, with `--fixed-fps 30|60` and `--write-movie` (Godot's own rendered frames, no compositing). APPDATA/LOCALAPPDATA/TEMP use short folders under `work/dual07/profiles/<id>`.
- Flags: `combat_sprite_set_override=1`, index override set to the actual package `…spritesheet-index_v01_20261020-201338-38ecfcb0.json`, `heroine_sea_contact_override=1`. Patrol uses backdrop=1 (bright); sentry uses backdrop=0 (default/dark). Patrol animation and sentry v2 are both 0.
- Party: the solo female heroine from `begin_new_run()`. No companions were recruited or faked, so this is not a four-person party claim.
- Declared setup: the exploration hero is placed once, 70 px left of the visible enemy. From there `move_right` walks into the enemy and the real `<23 px` check opens the encounter. Nothing is placed in battle.
- Battle inputs: `Input.action_press/release` for `move_right` and `battle_attack`. Presses are applied at the start of a frame, and the attack press is released at the next frame start. Hero and enemy stats, HP, timers, cooldowns and AI stay normal. The harness never calls `_try_attack`/`_finish_battle` and never writes HP or damage.
- The result is dismissed by a real left-mouse press/release through `Input.parse_input_event` on the visible button.

## Result: final run `outputs/hero-natural-v01/20261020-205808-f3fc1888` (runner proof `allPass: true`)

| | patrol EN 30 fps bright (outskirts) | sentry ZH 60 fps dark (ruins) |
|---|---|---|
| Checks | 30/30 | 30/30 |
| Contact log | 4 hits ×19 at clock 0.1667 s (5/30) | 6 hits ×19 + 1 `cancelled_hit` (a natural enemy hit cancelled the pending contact at clock 0.05) |
| Attack presses / enemy attacks / min hero HP | 4 / 1 / 88 | 7 / 2 / 64 |
| Finishing contact → result enabled | frame 105 → 112 | frame 275 → 289 |
| Reward | 26 XP / 12 JP, exactly one after-battle save | 44 XP / 20 JP (level 2, no pending job choice), exactly one after-battle save |
| Return | exploration, enemy cleared, battle id empty, return flag consumed, hero at the >43 px safe point | same |
| Reload of the after-battle autosave | encounter stays cleared, no XP/JP/HP change, no new save | same |
| MP4 (ffprobe) | 122 frames, 30/1, 4.067 s, 1,142,197 B, h264 1280x720, sha `cf8fc3e9…4b7c` | 299 frames, 60/1, 4.983 s, 673,031 B, sha `5a834f9c…926a` |

The JSON reports keep the per-frame trace for each run: HP, energy, x positions, cooldowns, enemy wind-up, event id/state/clock, sprite frame and inputs. Critical PNGs (explore-start, anticipation, contact, finishing-contact, result, return) are separate live-window captures. Raw movie frames (80 MB + 63 MB) stay local only.

## Failed attempts (kept, not hidden)

- 205352 (directory deleted) and 205410: harness parse errors (`SaveStore` global, untyped `:=`).
- 205420: fresh worktree with no import cache, so app_state failed to parse. The runner now does a checked `--import` first. That import rewrote 447 tracked `.import` files and created 335 `.uid` files; all were restored to the HEAD state.
- 205447: press-after-frame timing meant `is_action_just_pressed` never fired. The heroine took 0 attacks and lost; the click reached the main menu.
- 205644: both flows passed, but the patrol MP4 path exceeded MAX_PATH in the Python checks. Fixed with extended-length paths.

## Limits

- No staged defeat, cancel or scene-exit test was run in this batch.
- Single heroine only.
- `--write-movie` fixed-fps is not real-time wall-clock play.
- Godot prints `WARNING: 2 ObjectDB instances were leaked at exit` (a warning, not an error).
- No full regression suite was run, by instruction.
