# Female NORTH run v02: contact-trajectory correction prototype (UNAPPROVED, test-only)

**Scope.** This is a bounded correction of the v01 world-foot slip that root diagnosed (`...contact-diagnostic_unapproved-v01_20261018-204300-8eec63be.json`).
- It is not a package: no 128-phase matrix, .pxo, reversals, ZH/bright sets, GUI or performance work.
- Nothing was staged, committed or pushed, and no default game, ledger, index or Site file was written.
- Owner: Claude (Max, firstParty, no API key). Checkout: `work/max0840-male`. Base HEAD: `4b0ff5880b722cad2272928489f65b3b11bf1758`.
- No art, motion or fluidity acceptance is claimed.

## v01 baseline preserved
The v01 source, tools, poses, reports and clip were not modified. Their hashes after this session:
- model `5ac05f65…`, poses tool `aebe162e…` and capture tool `cd6e44af…` all match the v01 note.
- capture report `59b457e7d9f0…` matches root's diagnostic.

## Sources (tested; sha256-bytes = sha256-text-lf-v1, files are LF)
- Model: `tools/rpg-2-star-ocean-the-second_female-north_run-stop-source_unapproved-v02_20261018-210300-c653a747.gd`, sha256 `9c5435aaefb8c6ecbaee2052385d6c29f219cd78e79525cfd898ebb5c1e196d4`
- Poses + 30/60 contact tests: `tools/..._female-north_run-stop-contact-poses-tests_test-only-v02_20261018-210300-c653a747.gd`, sha256 `72334922fbb36c41574dd9269376274bcd61c50163703864f26dc42754e6b23f`
- Actual capture: `tools/..._female-north_run-stop-actual-capture_test-only-v02_20261018-210300-c653a747.gd`, sha256 `e85f6b8447855dc5fa838c2bb03f129c8b30282599679aa1dd0fa18514a98d05`
- Identity/endpoint: the same NORTH idle static PNG `6ed8d8dd` and .pxo `99e861ce` as v01, unchanged.

## What changed from v01
- **Contact contract.** A stance foot is world-ground contact. In v01 the stance depth stayed within ±2 rows; in v02 it is `19 − phase` source rows over the unchanged 38-phase stance.
  - The gait clock advances exactly 1 phase per source row of rendered travel, so the heel cap stays on one world point at any frame rate.
  - Speed is unchanged at 140 logical px/s. The design cadence is unchanged at 4.375 steps/s; measured cadence was 4.36 and 4.44 at 60 Hz and 4.29 at 30 Hz.
- **Named contact feature.** The **heel cap**: each boot's static heel block, rows sole−3..sole of the boots layer (24 / 22 texels for leg 0 / 1). Its underside edge is the measured contact point.
  - During stance the block is drawn unmodified (no reveal, no medial shift), so the same texels are the contact in every frame.
- **Peel is explicit and outside stance.**
  - At swing phases 38–44 the heel cap rises along the authored lift curve, and static-palette sole-tread rows are revealed between the heel rows and the cap.
  - The toe pivot is hidden behind the boot in a back view and is not drawn. Peel frames are not counted as contact.
- **Projection, not a figure rescale.**
  - Ahead = higher on screen: at touchdown the far boot's heel is at row 84, rising under the coat hem. The coat vent now stays in front of a rising boot.
  - Behind = lower on screen: at the last stance phase the near boot's heel is at row 121.
  - Only the trousers and the boot shaft are resampled, by a span factor from the hidden hip row (62) to the heel, clamped to 0.5–1.6. The cuff (5 rows) and heel block (4 rows) stay rigid.
  - Body/gear scale is 0.5; the torso, pack and head are never stretched.
- **Cell.** Grows from 80x112 to **80x128**, with transparent rows at the bottom only. The pivot stays (40,104) and the scale 0.5. The top 112 rows of the rest/idle frame are byte-identical to the static PNG and rows 112–127 are transparent.
  - Lowest opaque row over all 128 phases: 121.
- **Start.** A fresh start uses phase 19 (stance depth 0), so the planted foot stays on its world point from the first press frame with no blend.
- **Stop.** A planted foot holds its world point until airborne feet have landed home. It then takes a lifted recovery step home. The figure settles to the exact static in 10 frames (0.167 s) at 60 Hz.
- **Re-press.** It resumes the stance phase from a grounded foot's depth. With no grounded foot, the lower foot is put in late swing, at phase 100.
- **Arms, torso bob, coat hem, scarf and ponytail** are unchanged from v01. The swing curve was revised once (see Iterations).

## Results
- **Headless poses + contact tests (try3): 131/131, `NORTH_V02_TESTS_OK`, checked-runner PASS.**
  - Schedules: 60 and 30 Hz × 3 sub-pixel starts, each run as idle → run 1.2 s → stop → re-press 0.6 s → stop.
  - Raster template search found exactly one heel-cap match in every grounded frame, including first and last stance frames, stop holds and re-press stances.
  - **Worst heel-cap travel: 0.0 world px** over 78 contact segments. 0 lateral shift.
  - v01 on the same raster measure (60 Hz): 12.5 px, with its late-stance peel frames unmatched. Root's geometric inference was 14.5 px.
  - Other checks: exact static after both stops at both rates, binary alpha, static palette only, and torso step within the guard.
- **Actual gameplay capture.** Survey annex room 2 (scifi.city), EN, ordinary `Input.action_press/release("move_up")`, unmodified `survey_annex.gd` moving the hero, clear lane x=240. The window is 1280x720, with the 640x360 canvas stretched 2x so 1 texel = 1 screen px. Fixed fps.
  - Contact is measured from the **captured viewport image**: the heel-cap template is found by exact RGB match, then mapped to scene space through `(root final transform × host canvas transform)⁻¹`.
  - **60 fps: 558/558, 135 frames.** 10 contact segments, worst travel 0.0 scene px in Y and X. Full stances run 8–9 frames, e.g. leg 1 phases 0→37 at ticks 54–62, all at Y 204.5.
  - **30 fps: 290/290, 68 frames.** 10 segments, worst 0.0. Full stances are 4 frames, phases 2–32.
  - Both captures: `NORTH_V02_CAPTURE_OK`, checked-runner PASS.
- **Clips** (normal speed, libx264 crf 10 yuv420p, so chroma subsampling softens colours):
  - `...en-60fps-normal1x-1280x720_..._c653a747.mp4`: 135 frames, `1c7ffba9…`
  - `...en-30fps-normal1x-1280x720_...mp4`: `ccbba12c…`
- **Native PNGs (80x128)**, all from real `advance()` states:
  - contact q0 `5ecd990e…`, passing q18 `60721c60…`, stance-end q37 `827ab8f6…`, peel q42 `38eb8ede…`, flight q52 `157122e1…`, kick q58 `03d524ba…`
  - settle: 60 Hz stop, tick 82, `8407147c…`
  - final: exact static, padded, `6761bcd3…`

## Iterations and failures (disclosed)
1. **Parse errors in the test tool**, caught by the checked runner (log `...tests-try1...`). Six untyped inferences and one wrong `Dictionary` type. Fixed.
2. **Swing curve, iteration 1.** All checks passed: tests 131/131; capture 558/558 at 60 fps and 290/290 at 30 fps. But in the 60 Hz frames the lifted boot stayed below the standing line until about phase 56, which read as a stilt leg.
   - The swing knots after toe-off were revised once, to a sharper kick. Stance was untouched.
   - The iteration-1 PNGs, reports and frames are kept in `iter1/`. Their reports record model hash `e379dd2d…`, which is superseded.

## Concrete tradeoff (the open anatomy issue)
The world-ground lock is achieved exactly, but it costs a **long trailing leg in late stance**.
- **Where it comes from.**
  - The stance moves the foot 37 source rows relative to the sprite, about the whole visible static leg (28 rows).
  - From about phase 28 to the peel at 44, the near boot's heel sits 9–18 rows below the static sole.
  - The trousers stretch up to about 2.1x and the shaft to 1.56x (stance-end q37: shaft 17 rows, cuff top row 96).
- **How it reads.** In the 60 fps frames this reads as a stilt-like extended leg for about a quarter of each step. The revised kick only shortened the post-toe-off part.
- **At contact the far boot is mostly hidden by the coat**: about 10 rows of boot are visible below the hem.
- **Why I stopped rather than tune it.** A flat heel cap held for 38 phases at 140 px/s cannot sit closer to the standing line without:
  - reducing the stance distance, shortening the stance or slowing the run, all of which are forbidden; or
  - choosing a different contact feature (the toe), which is hidden in this back view.
- **Possible method changes for root to decide.**
  - Shift the stance window ahead (e.g. MID 22–24). The trailing extension shrinks by 3–5 rows, but touchdown happens almost entirely under the coat.
  - Author a dedicated near-leg drawing (bent knee, foreshortened thigh, more boot and sole) instead of row resampling of the static trousers.
  - Accept the projection as the back-view look.

## Not tested
- Re-press with no grounded foot (the phase-100 branch).
- Release at other phases: all schedules released near stance phase 35 or in flight.
- ZH, bright city, reversals, the 128-phase release/re-press matrix, the Pixelorama package.
- Human normal-speed review.

## Next action
Root judges anatomy and proportion: the long trailing leg in stance-end/peel and the hidden far-boot contact. Root also judges the contact evidence. If accepted, run the full 128-phase native bake and matrix. If rejected, pick one of the method changes above; another curve pass would not resolve it.
