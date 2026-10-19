# Female NORTH run/stop prototype v01: provenance and limits (UNAPPROVED, test-only)

Task `content.char.protagonist-female.walk-north`, owner Claude (signed-in Max, firstParty, no API key), producer checkout `work/max0840-male`, base HEAD `4b0ff5880b722cad2272928489f65b3b11bf1758`. Nothing was staged, committed, pushed, or wired into the game. The ledger, index, Site and default game files are untouched.

This is a bounded first prototype for root to inspect. It is not a production package. The 128-phase multi-schedule matrix, Pixelorama packaging, reversals, bright/dark bilingual sets, GUI SaveAs/reopen, performance measurements and creator/human review were **not done**.

## Sources (sha256-bytes; the text-lf-v1 hash is identical because the files are LF)
- Model `tools/rpg-2-star-ocean-the-second_female-north_run-stop-source_unapproved-v01_20261018-202253-402f6707.gd`: `5ac05f659848990b1c5d0822b268e41182b99bb20853081cf480faa5f4eaf8f5`
- Pose bake + checks `tools/..._female-north_run-stop-native-poses_test-only-v01_20261018-202253-402f6707.gd`: `aebe162e3d4542a49120c638732e4249092691886963997a883f111642fa09eb`
- Capture `tools/..._female-north_run-stop-actual-capture_test-only-v01_20261018-202253-402f6707.gd`: `cd6e44af66001eebcf2a21ee67fce4713c5d82c64e753720973e649ec0e4b7e3`
- Identity/endpoint (repo-local, tracked, working bytes = HEAD blobs): the north idle static PNG `...6ed8d8dd.png` `bd5c81661e52ed2ff4fb3c41940cf96de8390c6cec14129f78d691b613cb8e82` and its .pxo `...99e861ce.pxo` `7ca7dbdffe9787948ea56ae033b55e738cbd3f80bfbd694ed2d3a9a110756ef9` (built by `...9af15df7.py`; unapproved but produced). EAST e115c70 was used only as a reference for timing and state concepts. No EAST, WEST or SOUTH image is used, mirrored or flipped.
- The hashes above were identical before and after the bake and capture runs. `git status` gained only these new outputs and the three new tools.

## Construction
- Native cell 80x112, pivot (40,104), scale 0.5 (48 logical px), binary alpha, nearest. All texels are static role-layer texels moved by integer row/column remaps. The only exception is the revealed sole rows under a lifted heel: heel face + tread, using the static palette colours `714730/41302b/201c20/302526/0a0a0e`.
- The gait clock is driven by distance: 128 phases per 128 source px. At 140 logical px/s the design cadence is 4.375 steps/s. Stance lasts 38 of every 64 phases, so there is a flight phase.
- Perspective contract: the back view has **no screen-Y foot lock**. Contact is a pose state. A stance foot keeps its lateral columns and stays within its static sole row ±2 (ahead→behind in depth). The swing foot kicks back toward the camera (heel up, foreshortened shaft, sole showing), passes under the body and reaches ahead.
- Follow-through:
  - Torso bob +2/-2 px, plus a 1 px weight shift toward the stance foot.
  - Bent-arm carriage. On the back swing the elbow goes out and the glove shows at the hip; on the forward swing the forearm is hidden in front of the body and closed with an outline.
  - The coat hem lifts up to 2 px over a lifting knee.
  - The scarf tail and the ponytail tip lag the gait.
- The EAST v03 rendered-torso guard is kept (≤1 source px per 60 Hz frame).
- Start blends from the static over 0.08–0.10 s. Release: the lower airborne foot lands first, the other steps home, and everything settles to rest; idle at 0.22 s.
- The rest-parameter render is pixel-identical to the static, so the end of a stop does not pop.
- Identity: the right-knee strap, boot buckles, canister on the character's left, ponytail and scarf tail on the right, pack, bedroll and cuffs all come straight from the static texels.

## Results (60 Hz fixed delta)
- Pose bake (headless, `--path game -s <bake> -- outputs/female-north-run-v01 20261018-203441-909cd39c 50`): **14/14 pass**, 0 SCRIPT_ERROR/parse markers. Checks: layer composite = static; rest identity; 128 phases; binary alpha; palette; stance band + lateral lock; both feet airborne at q44–59; torso step ≤1; idle = static; first press runs with one foot grounded; cadence; stop reaches exact static and settles in ≤0.25 s (released at q52; final at stop frame 13).
- Capture (windowed, `--fixed-fps 60 --resolution 640x360`, survey_annex room 2, scifi.city, EN, hero x=240, ordinary `Input.action_press/release("move_up")`): **547/547 pass**, 0 error markers, 135 frames.
  - Per-frame checks: fixed delta, physical 140 px/s input, 640x360 viewport, presented texture = model RGBA.
  - The idle frames match the static exactly.
  - The first press frame both moves and runs.
  - Both releases stop physically on the first frame and settle to the exact static in 10 frames (0.167 s).
  - Cadence 4.44 steps/s. This comes from landing ticks 27/41/54, only two intervals, so it is quantised; the design value is 4.375.
- Clip: `...annex-room2-en-60fps-normal1x-640x360_..._909cd39c.mp4`, 135 frames at 60 fps, libx264 crf 10 yuv420p. Chroma subsampling softens pixel colours slightly.

## Failures and corrections during the session (disclosed)
1. Parse errors that the gate caught: an untyped `bx`/`elbow_dx`, an inner-class call to an outer static function, and an untyped `cadence`. All were fixed and rerun.
2. The rest render differed from the static in 17 px because trouser row 84/85 was dropped. The construction was fixed; no tolerance was added.
3. The first stance check had a wrong constant: one floor band, 101–105, for both legs. It was corrected to the model's declared per-leg band, static sole ±2. Lateral lock is now measured on the union of the lowest 9 boot rows instead of one row that the heel peel moves.
4. The first cadence check counted contacts inside a fixed window. That is a fencepost-biased estimator: 4 contacts in 0.767 s read as 5.2 steps/s, while the actual intervals were 14/13/14 frames. Both checks now use the mean landing interval, with the same 4.0–4.5 bound.
5. Visual iteration 1:
   - The revealed sole read as a detached disc under the narrow heel rounding. It is now inserted between the authored heel rows and the rounded underside.
   - Back-kick and arm swing were too weak to read at 48 px. Peak lift went from 10 to 13 px; arm crop and raise were increased.
6. The first capture lane, x=320, ran through room-2 fixtures and their labels. It was moved to the clear lane at x=240, with shorter runs so she stays below the back wall.

## Known limits / open for root inspection
- At the static-sole floor band the planted foot drifts with the body in screen Y. This is a deliberate contract for the back view, not a hidden slide fix; judge it at normal speed.
- Motion is still modest:
  - The torso and pack are rigid apart from the bob and sway.
  - There is no shoulder counter-rotation and no head lag.
  - The coat skirt only lifts at the hem; it does not swing.
  - Boots read darker on the annex floor.
- The forward-swing hand is cropped rather than redrawn.
- Tested: only one context (annex room 2, EN, 60 Hz) and one release phase in the bake. Not tested: 30 Hz, re-press from mid-flight, reversals, other release phases, ZH, bright city.
- Fluidity is not claimed from frame counts or checks; it needs root and creator review at normal speed.

## Next action
Root inspects the six native PNGs and the clip. If the anatomy is accepted, run the full 128-phase multi-schedule boundary matrix (30/60 Hz, every release and re-press phase), bright and dark bilingual captures, and native .pxo packaging. If it is rejected, revise the named defects (likely candidates are torso/shoulder rotation and coat swing) without changing the thresholds.
