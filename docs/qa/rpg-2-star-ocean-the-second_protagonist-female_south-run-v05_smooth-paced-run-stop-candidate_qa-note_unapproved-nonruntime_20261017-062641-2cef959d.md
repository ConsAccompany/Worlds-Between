# Female protagonist south RUN v05: smooth / well-paced run-and-stop candidate (QA note, m8-w08)

**Status: UNAPPROVED / NONRUNTIME.** This is a single-direction, test-only motion candidate for creator review. It is not a production sprite, it is not integrated into the runtime, and it is not accepted.
- Every manifest and receipt approval flag is `false`.
- Only Claude has reviewed it, as an agent.
- Counters are unchanged:
  - cloud meter **40.8%**;
  - accepted scenes **3/12**;
  - complete sprites **0/52**;
  - human playtests **0/2**.
- Not touched: map, rooms, runtime scripts, shared progress state, Game Bible source and the git index. Nothing was staged or committed.
- The approved v8 PNG is byte-identical (`ccf9d2a2…68b6fd`).
- Every v03 and v04 file is identical to its pinned listing (check 13).

**Auth.** Checked first with `claude auth status`: `loggedIn: true`, `authMethod: claude.ai`, `apiProvider: firstParty`, `subscriptionType: max`. `ANTHROPIC_API_KEY` is absent. No API key, credits or paid fallback was used, and no quota or auth failure occurred.

**Inputs read:**
- the creator motion standard (`docs/design/…character-motion_smooth-fluid-well-paced-creator-standard_v01_20261016-233420-702db4c9.md`);
- Codex's v04 review with the creator's choice "继续打磨跑动或停步" ("keep polishing the run or the stop") (`docs/qa/…south-run-v04-native-godot-stills-codex-visual-review_unapproved-v01_20261016-222301-2a46573f.md`);
- the v04 QA note and v04 tools;
- the approved selout v8 south idle (the identity and the stop destination);
- `docs/progress.md`;
- the global naming rules in `~/.codex/AGENTS.md`. The repository has no project-level AGENTS.md.

## What v05 changes

v05 forks the v04 builder. The part library, compositor, identity rules (rigid head and torso block, no neck shear), zero-slip planted boot, stance roll, re-press rule and landing/shuffle keys are unchanged. Only the **gait** and the **stop settle** change:

| Ask (creator / Codex) | v04 | v05 |
|---|---|---|
| Shorter forward stride | step 48 px, 5.83 steps/s; boot lands 3 rows below its v8 spot; forward leg hip-to-sole up to 43 / 46 rows (v8: 40 / 43) | **step 42 px, 6.67 steps/s; lands 2 rows below; hip-to-sole up to 42 / 45** (captured at 60 fps: 41 / 44); cuff jog 1 texel; knee lean at touchdown 2 → **1** |
| Less airborne-looking time | swing boot spends most of the swing behind the body with lift 3; flight 93 ms per step; **floor gap** (lowest boot above v8's ground row) max 10 rows, mean 3.52, ≥ 3 rows on 52% of the cycle | swing lift ≤ 2; the swing boot comes forward early and passes low near its v8 spot; **flight 75 ms per step; floor gap max 5 rows, mean 1.64, ≥ 3 rows on 31%** (captured at 60 fps: max 5, mean 1.70, ≥ 3 rows on 30%) |
| Contact-flag airborne share | 54.2% (captured 28 / 50 ticks at 60 fps) | **50.0%** (captured 27 / 50) |
| Stop: visible boot lands before the body settles | dip and torso shift released on the same tick | after the last touchdown, **at most one body change per tick**: hair catches up → torso re-centres → arms → dip release → hair. The dip lands with the touchdown. |

Zero slip is kept: on every captured tick at 30, 60 and 144 fps, and in every stop, re-press, showreel and reversal tick, the planted boot moves **0 px** in world space. The lowest row is always pinned. While the view holds, the x-extent and every boot texel are also pinned. When the roll view changes, the sole x-extent moves by at most 2 px.

## Normal-speed evidence (real Godot 4.7.2, windowed)

The project's 640×360 canvas is rendered in a 1280×720 window with the sprite at scale 0.5 and nearest filtering. The scenes' own `_process` moves the hero at a measured **140.000 logical px/s**. Capture stamp `20261017-060817-3bcbb263`, exit 0.

**Main review clips (normal speed, every 60 fps tick, full 1280×720 window, 1 window px = 1 px):**
- `outputs/rpg-2-star-ocean-the-second_city-bright_protagonist-female-south-run-v05-preview-showreel-1x-60fps-h48_unapproved-nonruntime_20261017-060817-3bcbb263.mp4`
- `outputs/rpg-2-star-ocean-the-second_annex-dark_protagonist-female-south-run-v05-preview-showreel-1x-60fps-h48_unapproved-nonruntime_20261017-060817-3bcbb263.mp4`

Each clip is 187 ticks (3.1 s, verified with ffprobe: 1280×720, 60/1, 187 frames). The segments are:
1. idle 0.30 s;
2. **start** and **sustained run** (0.6 s = 2 cycles);
3. release for 3 ticks, then **quick re-press**;
4. run;
5. **reversal**: `move_up` held for 0.4 s;
6. **south again**;
7. **release to v8**;
8. a short run;
9. **release to v8**.

Both uninterrupted releases end on the v8 PNG 183 ms after release, with 0 changed pixels at the switch.

**Diagnostic clips** (same capture; `…-preview-<what>-h48_unapproved-nonruntime_20261017-060817-3bcbb263.<ext>`, per scene unless noted):
- `showreel-track-2x-60fps.mp4`: hero track crop at 2x;
- `run-1x-60fps.mp4`, `run-2x-60fps.mp4`, `run-1x.gif`, `run-follow-3x.gif`;
- `stop-{landing-r027, mid-stance-r029, late-stance-r030, flight-r034}-{1x.gif, 2x-60fps.mp4}`: one per **stop entry phase**;
- `repress-r016-{g01, g08}-{1x.gif, 2x-60fps.mp4}`;
- city-bright only: `reversal-r020-…` and `reversal-r029-…`.

**Stills** (58 colour-exact 1280×720 PNGs, diagnostic only):
- per scene: `still-v8-idle-shadow`, `still-key-00px` … `still-key-77px` (12 keyframes every 7 px);
- per scene: `stop-{landing, mid-stance, late-stance, flight}-{1-last-move, 2-plus2, 3-plus5, 4-v8}`.

Slow motion and stills are diagnostics only; the 1x 60 fps showreels are the normal-speed judgment material.

**Reversal limitation.** No north pilot art exists, and other directions are out of scope until creator review. While `move_up` is held, the capture therefore shows the scene's own runtime hero sprite (its existing placeholder north walk) and hides the pilot. Those ticks are labelled `runtime_north` in the receipt and are not pilot evidence. On the next south press the pilot re-enters from the v8 idle with the start rule.

### Gates and measurements

| | 60 fps | 30 fps | 144 fps |
|---|---|---|---|
| Stops (from every 60 fps tick of one stride in both scenes, plus 30 / 144 fps in city-bright): release → v8 PNG | **150–200 ms** (v04 150–200) | **267–333 ms** (v04 200–233) | 125–174 ms (v04 132–181) |
| Last touchdown → v8 (post-contact) | 67–83 ms (v04 67) | 167–200 ms (v04 67–100) | 56–63 ms (v04 56) |
| Longest raised boot after release | 83 ms | 100 ms (the limit) | 76 ms |
| Switch to v8 | 0 px | 0 px | 0 px |
| Body changes per settle tick | ≤ 1 | ≤ 1 | ≤ 1 |
| Per-tick silhouette change, run max (v04) | 371 (399) | 473 (437) | 374 (383) |
| Per-tick silhouette change, stop max (v04 60 fps 375) | 358 | 318 | 342 |

- **Re-press:** 54 cases. In every case the next touchdown is the other boot. It comes 33–133 ms after the re-press, and the last-landed boot stood at least 67 ms.
- **Reversal sweep:** 9 cases, turning at phases 11 / 25 / 39 / 53 / 67 / 81 px in city-bright and 25 / 53 / 81 px in annex-dark. The pilot re-entry lifts vl first and touches down 150 ms after south is pressed again. Every final stop reaches v8 at 183 ms with 0 changed pixels.
- **Neck shear:** 0 on every captured tick. The head moves 1 px sideways with the torso on 17 of 50 run ticks at 60 fps, as in v04.
- **Contact shadow:** at least 59 shadow pixels are darker than the background on every tick, in both scenes. It is still a test-only sprite.
- **Parity and fidelity:** the GDScript compositor equals v8 at the neutral state, and equals all 12 builder keyframes and their shadows. Exact-RGB fidelity holds on every captured pilot tick. Steady-state gait equals the manifest's per-px table.

**Focused check: 35/35 OK** (`--pixelorama --receipt --import-receipt`). The checks:
- rebuild byte-identical (90 files);
- palette, binary alpha, independent compositor, identity and neck;
- foot pinning, swing lift 1..2, bounds, `MOVE_SPEED` 140, no runtime reference;
- `.ora` structure;
- Pixelorama 1.2.3 headless round-trip with an isolated APPDATA (156 `.pxo` layer PNGs, 62 `.ora` layer PNGs);
- **13** v03 + v04 immutability;
- **14** forward leg shorter than v04;
- **17** gait and floor gap below v04 (recomputed independently);
- **16b** one body change per settle tick, with the 60 fps settle ≤ 100 ms;
- **18** showreels and reversal sweep;
- receipt hashes, and the isolated-copy import (`RUN_V05_IMPORT PASS`: 86 PNGs lossless, no mipmaps, Nearest filter).

## Unresolved visual flaws (plainly)

1. **The trailing boot still rises to about knee height behind the body.**
   - With a zero-slip contact at MOVE_SPEED 140, the planted boot must travel 21 px up the screen before it lifts. The rear limit the leg rig can draw (o = −19) is unchanged from v04.
   - The floor gap halved, but 30% of moving ticks still show both boots ≥ 3 rows above the floor line.
   - The only further levers are a shorter contact with a faster cadence, a planted foot that slips, or a different runtime speed. Those are creator or gameplay decisions.
2. **It is still a run.** By the contact flag, 50% of the cycle is airborne (v04 54%). Most of v05's gain is in how low and how briefly the boots hang, not in the contact flag.
3. **Cadence is 14% faster (6.67 steps/s).** That is less hang time per step but busier feet. Whether it reads as "well-paced" or as frantic needs the creator's eye at 1x.
4. **Stops at 30 fps are slower than v04** (267–333 ms against 200–233 ms). The one-change-per-tick settle costs 33 ms per step at 30 fps. At 60 fps the stop length is unchanged from v04, and the post-contact settle can be up to one tick longer (83 ms against 67 ms). Making the settle time-based would remove the 30 fps regression; that was not done in this pass.
5. **The run silhouette changes more per tick at 30 fps** (473 against v04's 437). At 60 fps and 144 fps it changes less than v04.
6. **Reversal is a hard cut.** The runtime's north placeholder is larger and in a different style from the 48 px pilot, so each turn swaps art abruptly. No turn animation exists, and none can be made without north art.
7. **The re-entry start takes 150 ms to the first touchdown.** This is v04's start rule: vr stays planted and vl swings.
8. **Inherited from v04:**
   - 1-px head sway with the torso shift;
   - possible knock-knee read (lean reduced to 1, not reviewed);
   - the rear-boot cuff jog in the heel-up and toe views;
   - the test-only contact shadow.
9. **This is agent review only.** I checked consecutive real 60 fps frames as image strips; I cannot play the MP4s in real time. The creator's normal-speed viewing is the actual gate.
10. **Environment.** Another stream edited `game/scripts/scifi_exploration_area.gd` (opt-in City Hall Park layers) and map scripts while the capture ran. `MOVE_SPEED` was asserted at 140, and the captured city frames show the existing city plate. Those edits are not part of this work.

## Files (all new; nothing existing modified)

| Path | sha256 (first 16) |
|---|---|
| `game/assets/characters/run-v05-unapproved/` (90 files incl. empty `.gdignore`, 488 KB; 62 parts, 12 keyframes, 12 keyframe shadows) | in the manifest |
| `…/…south-run-v05-manifest_unapproved-nonruntime_20261017-055617-481b74f4.json` (`v05_changes`, `gait.floor_gap_*`, `gait.v04_reference`) | `7249cca9b08b25cb` |
| `…/…south-run-v05-keyframes-editable_unapproved-nonruntime_20261017-055617-706e15b6.pxo` (12 frames × 13 layers) | `95b8f3a3b3795035` |
| `…/…south-run-v05-part-library-editable_unapproved-nonruntime_20261017-055617-85d03f64.ora` (62 layers) | `4ca61f04b10cff84` |
| `tools/…south-run-v05-build_m8-w08_20261017-055617-998d6a83.py` (byte-identical rebuilds) | `8205784cb6a481cf` |
| `tools/…south-run-v05-godot-capture_m8-w08_20261017-055617-257bf083.gd` | `d432c98e0b567b48` |
| `tools/…south-run-v05-godot-import-validation_m8-w08_20261017-055617-e19d1283.gd` | `3c82a50d6b323412` |
| `tools/…south-run-v05-preview-gif-mp4_m8-w08_20261017-055617-ff0bf38f.py` | `909870c98d4c14e9` |
| `tests/protagonist-female-south-run-v05/…_focused-check_unapproved-m8-w08_20261017-055617-f05bfd27.py` | `bd1d25b2dc5a57dc` |
| `outputs/…city-annex_…-south-run-v05-capture-receipt-h48_unapproved-nonruntime_20261017-060817-3bcbb263.json` | `ff8849fe5b0c040d` |
| `outputs/…city-annex_…-south-run-v05-preview-receipt-h48_unapproved-nonruntime_20261017-060817-3bcbb263.json` | `52e6206f5c182705` |
| `outputs/…south-run-v05-import-validation-receipt_unapproved-nonruntime_20261017-062459-e19d1283.json` | `bea1d9524eb8a1ee` |
| `outputs/*south-run-v05*` (59 PNG, 19 GIF, 23 MP4, 3 receipts; about 96 MB) | see the receipts |

The editable source stays compact: 62 parts plus 12 keyframes and rules, with no stop bank. Scratch work (per-tick frames, logs, patch scripts, comparison strips) is in `work/loco-v05-scratch/`, which is gitignored. The isolated import copy under `%LOCALAPPDATA%\Temp` was deleted.

## Reproduce

```
PY=C:/Users/hkzha/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/python.exe
GD=work/tooling/godot-4-7-2/Godot_v4.7.2-stable_win64_console.exe
$PY -I -B tools/…south-run-v05-build_…-998d6a83.py --out-dir <scratch>       # byte-identical rebuild (--write = asset folder)
APPDATA=<scratch appdata> $GD --path game -s <abs …v05-godot-capture_…-257bf083.gd> -- --motion-dir=<abs scratch>   # windowed; writes outputs/
$PY -I -B tools/…v05-preview-gif-mp4_…-ff0bf38f.py --motion-dir <abs scratch> --receipt outputs/<capture receipt>.json
$PY -I -B tests/protagonist-female-south-run-v05/…-f05bfd27.py --pixelorama --receipt outputs/<capture receipt>.json --import-receipt outputs/<import receipt>.json
```

**Reversal:** delete the following. Nothing else was changed.
- `game/assets/characters/run-v05-unapproved/`
- `tests/protagonist-female-south-run-v05/`
- the four `tools/…south-run-v05…` files
- this note
- `outputs/*south-run-v05*`

## Decisions for the creator

1. Watch the two 1x showreels. Does the shorter, lower, faster v05 run read as smooth and well-paced, or does 6.67 steps/s look busy?
2. Is the remaining rear-boot rise acceptable? If not, choose the lever:
   - (a) a faster cadence with a shorter contact;
   - (b) allow a small, steady planted-foot slip;
   - (c) a runtime speed change.
3. Do the stops land first and settle cleanly at normal speed? Should the settle become time-based to remove the 30 fps slowdown?
4. Only after approving the south motion: north, east and west art, and a turn transition to replace the reversal cut.
