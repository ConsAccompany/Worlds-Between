# Female protagonist south RUN v04: targeted-fix test-only pilot (QA note, m8-w07)

**Status: UNAPPROVED / NONRUNTIME.** This is a test-only motion pilot. It is not a production sprite, not a runtime replacement, and not accepted.
- Every manifest and receipt flag is `false`: `art_approved`, `human_reviewed`, `runtime_integrated`, `walk_animation_approved`, `run_animation_approved`, `stop_animation_approved` and `counts_toward_art_acceptance`.
- Only Claude reviewed this, as an agent. That is not a human or creator review. **Exploration sprites stay 0/52. No counter or meter change.**
- **Real-time motion is still not validated.** Codex validated only v03 stills. I cannot play the GIF/MP4 files in real time either, so the v04 real-time read is still open.
- Not touched:
  - the approved v8 static PNG (byte-identical, `ccf9d2a2…68b6fd`, unchanged against git HEAD);
  - every v03 file (168 files pinned by hash before v04 was written; still identical, check 13);
  - `MOVE_SPEED`, scenes, runtime scripts, other directions and characters, `docs/progress.md` and the meter.
- No staging, commit or push.

**Auth.** Checked first with `claude auth status`: `loggedIn: true`, `authMethod: claude.ai`, `apiProvider: firstParty`, `subscriptionType: max`. `ANTHROPIC_API_KEY` is unset. No API key, credits or paid fallback was used, and no quota limit was hit.

**Inputs:**
- the v03 QA note (`…south-run-v03_test-only-motion-pilot_qa-note_unapproved-nonruntime_20261017-015030-7c1d4e92.md`);
- Codex's v03 review in the Stream D2 dispatch (`docs/coordination/…claude-stream-d2_female-south-run-v04-neck-landing-stop-prompt_v01_20261016-221000-6c7cf191.md`). Codex inspected city-bright 1x key stills at 0/24/48/72 px and the annex-dark 4-frame airborne stop, and listed three problems:
  1. the forward leg is too long and straight on landing;
  2. the neck has a 1-pixel shear;
  3. the hair/cape settle lengthens airborne stops after the feet are down.

## What v04 changes (targeted; nothing else)

v04 is a copy of the v03 tools. Every v03 file is untouched. The three fixes:

| Codex finding | Cause found in v03 | v04 change |
|---|---|---|
| Forward leg too long and straight on landing | (a) The boot landed 6 rows below v8's ground row. (b) The compact strike/reach boots dropped a shaft row and were 3–6 rows shorter than v8's boot, so the leg made up the gap with repeated trouser rows: hip-to-sole up to 46 (vl) / 49 (vr) rows against v8's 40 / 43. (c) The shin ended at v8's x, but the strike boot's cuff sits 4 (vl) / 6 (vr) texels further out, so the leg ran straight down and then jogged sideways into the boot. | Landing at **+3 rows** (liftoff moved back to −19, so contact is still 22 px / 79 ms). Strike/reach boots keep v8's **whole 8-row shaft**. A longer-than-v8 leg keeps **v8's thigh rows 1:1** plus the whole knee band. The **shin takes the extra rows and slopes from the knee to the boot cuff**. The knee leans **2 texels inward** as the boot reaches and lands (1 at q 2, 0 from the v8 spot on). |
| 1-pixel neck shear | The head stayed steady while the shoulders, scarf and torso shifted 1 texel toward the planted boot. | The **head and hair lock shift with the torso**: the whole v8 upper body is one rigid block moved by (sx, bob). Every head and neck texel stays v8's own texel relative to the torso, so the v8 idle identity is kept by construction (no redraw). |
| Hair/cape settle lengthens airborne stops | After the last touchdown: a 34 ms dip (3 ticks at 60 fps), a 34 ms hair lag, a 34 ms cape lag, then the v8 switch. That is about 117 ms at 60 fps. | Once stopped: **hair lag 16 ms** (one 60 fps tick), **cape returns with the torso** (0 ms), **dip 25 ms** (2 ticks at 60 fps). The 1-row dip stays as the readable "settled" beat. |

One consequence fix: a boot planted at the new rear limit in the **toe view** starts its stop shuffle in that view. The 14-row heel-up boot did not fit under the dipped hip at o = −18, and the builder's feasibility sweep caught it.

Unchanged from v03:
- **140 logical px/s**;
- the single south direction;
- the part library cut from v8 (32 colours, binary alpha);
- the zero-slip planted boot and the stance roll strike → v8 → heelup → toe;
- swing lift ≤ 3;
- arm poses and timing;
- the re-press rule;
- the **test-only contact shadow** (separate sprite, opacity 0.38; no runtime system);
- the **≤ 100 ms raised boot after a release** gate.

## Verdict (agent judgment, for Codex review)

**All three findings measurably improve, and every v03 gate still passes.** I compared real Godot stills of v03 and v04 side by side at the same pin (1x–3x), and v04's real 60 fps tick crops.
- **Landing leg:** the leg is visibly shorter and now bends at the knee. The thigh comes down from the hip, the knee leans in, and the shin angles out into the boot, where v03 had one straight diagonal. The vr (viewer-right) leg at the 48 px key is the clearest case.
- **Neck:** no shear at any tick. The head now moves 1 window px sideways with the torso on stride ticks (15 of 51 at 60 fps). That is a small head sway; v03 had a 1-px neck shear on the same ticks (14 of 51).
- **Stop:** an airborne stop now reads as touchdown → short shuffle → 2-tick dip → v8, with the hair one tick behind. The settle after touchdown is 67 ms at 60 fps (v03 117 ms).

**Open risks, said plainly:**
- **It is still a run:** 5.83 steps/s, 54 % airborne, unchanged by design.
- **The leg is shorter, not v8-short.** At landing, hip-to-sole is 43 / 46 rows against v8's 40 / 43. The forward boot still reaches 3 rows (1.5 logical px) below v8's ground row; v03 reached 6.
- **The knee lean reads knock-kneed at 2x+.** The knee goes inward while the strike boot stays outward, because the planted-roll rule pins the strike sole under v8's splayed foot. At 1x it reads as a knee bend. Whether it reads as valgus at gameplay scale is for Codex to judge.
- **The head sway is new motion.** It is 1 window px and only on stride ticks. It replaces a shear rather than adding to steadiness.
- **Per-tick silhouette change grew in places.** Releasing the dip, hair and torso shift on nearly the same ticks compresses the stop:

  | Change per tick (pixels) | v03 | v04 |
  |---|---|---|
  | Run max, 60 fps | 388 | 399 |
  | Run max, 30 fps | 495 | 437 |
  | Run max, 144 fps | 349 | 383 |
  | Stop max, 60 fps | 285 | 375 |

  The stop maximum is still below the run maximum at each fps.
- **The rear (lifting) leg is unchanged in method but one view further back.** Liftoff is at −19 instead of −16. The rear-boot cuff jog of up to 5.5 texels in the heel-up/toe views is v03's and was not changed; Codex did not flag it.

## Measurements (real Godot 4.7.2, windowed)

**Capture setup:**
- same as v03: 640×360 canvas in a 1280×720 window, sprite scale 0.5, nearest filter;
- the hero is moved by each scene's own `_process` with `move_down` held, measured at **140.000 logical px/s**;
- scenes: city-bright and annex-dark (room 2);
- capture stamp `20261017-021230-fa373f55`, exit 0, no gate failure.

**Gates (all passed on captured pixels):**
- GDScript compositor equals v8 at the neutral state, and equals all 12 builder keyframes and their shadows;
- the steady-state gait equals the manifest's per-px table;
- exact-RGB fidelity on every tick;
- straight-south movement, and the hero stationary without input;
- **new:** on every captured tick (runs, 70 stops, 54 re-presses), the v8 head (crown/face) and the v8 scarf/chest match the capture at the same (dx, dy) offset, and no neck seam texel was filled.

| | v03 | v04 |
|---|---|---|
| Forward leg hip-to-sole, max (vl / vr rows; v8 40 / 43) | 46 / 49 | **43 / 46** (captured: 42–43 / 46) |
| Boot cuff jog into the forward boot (texels) | 4 / 6 | **1 / 1** |
| Lowest sprite row (v8 ground 103) | 109 (+6) | **106 (+3)** |
| Neck shear on captured ticks | 1 px on every torso-shift tick (14 / 51 at 60 fps) | **0 on every tick** |
| Contact length | 22 px, 79 ms | 22 px, 79 ms |
| Airborne share; steps/s | 54 %; 5.83 | 54 %; 5.83 |
| Planted boot, all fps: lowest-row Δ / same-view x Δ / texels changed | 0 / 0 / 0 | **0 / 0 / 0** |
| Planted boot: sole x-extent Δ at a roll change | ≤ 2 px | ≤ 2 px |

**Planted tick pairs:** 51 at 144 fps (v03 48), 18 at 60 fps, 7 at 30 fps. **Airborne ticks while moving:** 28/50 at 60 fps, 14/25 at 30 fps, 65/120 at 144 fps (v03 68/120).

**Immediate stops** (70 cases: 60 fps every tick of one stride in both scenes, plus 30 and 144 fps in city-bright). "Post-contact" means last touchdown → v8 PNG; the bracket is the last visible change after touchdown.

| fps | Released in flight → v8 (v03) | Released in stance → v8 (v03) | **Post-contact (v03)** | Longest raised boot | Max lift | Switch to v8 |
|---|---|---|---|---|---|---|
| 60 | **150–167 ms** (200–217) | **183–200 ms** (233–250) | **67 ms** [50] (117) | 83 ms | 3 | 0 px |
| 30 | **200 ms** (300) | **233 ms** (300) | **67–100 ms** [33–67] (167) | **100 ms** (at the limit, as v03) | 2 | 0 px |
| 144 | **132–139 ms** (146–153) | **167–181 ms** (181–188) | **56 ms** [49] (76) | 76 ms (v03 69) | 3 | 0 px |

- **Honest landing:** every airborne boot still flies to its v8 spot and touches down before the settle. No boot is off the floor longer than 100 ms after a release; that is gated in both the capture tool and the check.
- At 30 fps one tick is 33 ms, so the 100 ms case is 3 ticks, the same as v03.

**Re-press** (54 cases):
- 54/54 next touchdowns are the other boot.
- The last-landed boot stood at least 67 ms.
- The next touchdown comes 33–167 ms after the re-press (v03 33–150).
- The planted boot stays pinned throughout.

**Contact shadow:** at least 52 shadow pixels are darker than the background on every tick, in both scenes (as v03). It is still test-only.

## Import (isolated copy)

- A copy of `game/` without `.godot` was made under `%LOCALAPPDATA%\Temp\wb-rv04-imp-2a8e4f71`, and the pilot `.gdignore` was removed there only. The copy was deleted afterwards.
- Import printed `RUN_V04_IMPORT PASS`: 86 PNGs lossless, no mipmaps, alpha and opaque RGB identical, default filter Nearest.
- In the shared tree the asset folder keeps an empty `.gdignore`, so no `.import` or `.uid` file was created.

## Focused check: 33/33 OK

Run as:
```
tests/protagonist-female-south-run-v04/…-4f7a1d3c.py --pixelorama --receipt <capture receipt> --import-receipt <import receipt>
```

It keeps v03's checks (01–12) with the v04 compositor rules re-implemented independently. New checks:
- **13 v03 immutability:** 168 v03 files plus v8 hash to the pinned listing digest `f253e9a76c88b7a7…`, and the v03 manifest keeps `a5a2f7fa…`;
- **14 forward leg:** shorter than v03 on both legs, cuff jog ≤ 1;
- **15 neck:** the keyframe neck rows equal v8 + (sx, bob);
- **16a captured neck shear:** 0;
- **16b settle:** every 60 fps post-contact settle is under v03's 117 ms.

The Pixelorama 1.2.3 headless round-trip ran with an isolated `APPDATA`:
- the `.pxo` gave 156 layer PNGs, equal to the keyframes and shadows;
- the `.ora` gave 62 layer PNGs, equal to the parts.

The real `%APPDATA%\pixelorama` was unchanged.

## Evidence for Codex review

All files are in `outputs/`. Every name contains `south-run-v04` and ends `…_unapproved-nonruntime_20261017-021230-fa373f55.<ext>`.

**Stills (42 colour-exact PNGs, full 1280×720 window):**
- per scene: `still-v8-idle-shadow`, `still-key-00px` … `still-key-88px`, `stop-stance-{1-last-move,2-plus2,3-plus5,4-v8}` and `stop-flight-{…}`;
- for direct comparison with Codex's v03 sample: city-bright `still-key-{00,24,48,72}px` and annex-dark `stop-flight-1…4`.

**1x loops:**
- `preview-run-1x` GIF (real time, 1 window px = 1 px);
- **new `preview-run-1x-60fps` MP4** (every 60 fps tick, 1 window px = 1 px);
- `preview-run-2x-60fps` MP4;
- `preview-run-follow-3x` GIF.

**Stops and re-press:**
- `preview-stop-{stance-r030,flight-r036}-{1x.gif, quarter-2x.gif, 2x-60fps.mp4}`;
- `preview-repress-r016-{g01,g08}-{1x.gif, 2x-60fps.mp4}`.

That is 16 GIFs and 12 MP4s; the GIF palettes are lossy and the PNGs are the exact evidence.

**Receipts (sha256 first 16):**
- `…city-annex_…-south-run-v04-capture-receipt-h48_…json`: `59e6fc8f84534ff3`;
- `…preview-receipt-h48_…json`: `5c9ce002b86a0097`;
- `…south-run-v04-import-validation-receipt_unapproved-nonruntime_20261017-021441-2a8e4f71.json`: `4ccb1f21623c7329`.

The capture log printed two `output name too long (151)` warnings. That is the tool's own conservative 150-character warning, the same as v03; both files were written and verified by hash.

## Files (all new; nothing existing was modified)

| Path | sha256 (first 16) |
|---|---|
| `game/assets/characters/run-v04-unapproved/` (90 files incl. empty `.gdignore`, 492 KB; 62 parts, 12 keyframes, 12 keyframe shadows; longest asset path 245 characters) | in the manifest |
| `…/…south-run-v04-manifest_unapproved-nonruntime_20261017-015826-a3169015.json`: LF; `v04_targeted_fixes`; `metrics.forward_leg_nominal_cycle` with the v03 reference | `9271c124e8341ca9` |
| `…/…south-run-v04-keyframes-editable_…-11237870.pxo`: **editable Pixelorama source**, 12 frames × 13 layers | `9ea1c392d61847c4` |
| `…/…south-run-v04-part-library-editable_…-9f053899.ora`: 62 layers | `9979eed94ce50244` |
| `tools/…south-run-v04-build_m8-w07_20261017-015826-5b1e7d2a.py` (byte-identical rebuilds) | `035954d02484909f` |
| `tools/…south-run-v04-godot-capture_m8-w07_20261017-015826-9d3f6c18.gd` | `1cac199e7f8cfc4b` |
| `tools/…south-run-v04-godot-import-validation_m8-w07_20261017-015826-2a8e4f71.gd` | `a8d55ab955bf34db` |
| `tools/…south-run-v04-preview-gif-mp4_m8-w07_20261017-015826-c6b02e95.py` | `d6637a152a0ba4c8` |
| `tests/protagonist-female-south-run-v04/…_focused-check_unapproved-m8-w07_20261017-015826-4f7a1d3c.py` | `f0afe8cb4b851703` |
| `outputs/*south-run-v04*` (42 PNG, 16 GIF, 12 MP4, 3 receipts; about 74 MB) | see the receipts |

Scratch work is in `work/loco-v04-scratch/` (gitignored): logs, per-tick crops, comparison sheets, the v03 hash snapshot and one-off patch scripts.

## Reproduce

```
PY=C:/Users/hkzha/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/python.exe
GD=work/tooling/godot-4-7-2/Godot_v4.7.2-stable_win64_console.exe
$PY -I -B tools/…south-run-v04-build_…-5b1e7d2a.py --out-dir <scratch>          # byte-identical rebuild (--write = asset folder)
APPDATA=<scratch appdata> $GD --path game -s <abs …v04-godot-capture_…-9d3f6c18.gd> -- --motion-dir=<abs scratch>   # windowed; writes outputs/
$PY -I -B tools/…v04-preview-gif-mp4_…-c6b02e95.py --motion-dir <abs scratch> --receipt outputs/<capture receipt>.json
$PY -I -B tests/protagonist-female-south-run-v04/…-4f7a1d3c.py --pixelorama --receipt outputs/<capture receipt>.json --import-receipt outputs/<import receipt>.json
```

**Reversal:** delete the following. Nothing else was changed.
- `game/assets/characters/run-v04-unapproved/`
- `tests/protagonist-female-south-run-v04/`
- the four `tools/…south-run-v04…` files
- this note
- `outputs/*south-run-v04*`

## Open decisions for Codex / the creator

1. Does the shorter, bent landing leg read correctly at 1x in real time? Or does the 2-texel inward knee read as knock-kneed? The fallback is lean 1, which keeps the cuff connection.
2. Is a 1-px head sway with the torso shift acceptable? The alternative is dropping the torso shift entirely (steady head and torso, no shear, less weight transfer).
3. Is a 67 ms post-contact settle (2-tick dip plus one hair tick) still a readable stop? Or should the dip go too (about 50 ms)?
4. Unchanged from v03: is a 5.83 steps/s light run acceptable at 140 px/s? Should the runtime get a contact shadow? Both are runtime/gameplay-owner decisions.

No runtime integration, art acceptance or meter change follows from this note. Exploration sprites remain **0/52**.
