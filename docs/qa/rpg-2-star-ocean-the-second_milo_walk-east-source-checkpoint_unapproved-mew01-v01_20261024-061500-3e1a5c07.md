# Milo east walk/stop source checkpoint: mew01 (UNAPPROVED)

Task: `content.char.milo.walk-east` (batch 52). Scope: **east only**. Milo west is paused and was not touched. No default, ledger, Bible, registry, Git index or commit changes. No runtime adoption: the package is staged under `outputs/milo-ew01/pkg` and is non-default.

## Pipeline reused
- Engine: frozen jexplore39 side cycle (12 phases × 40 ms, world-locked stance 16.8/5.6/-5.6/-16.8 at host 140 logical px/s = 11.2 src/phase), plus `leg_transform`, `arm_transform`, `stop_poses`, `contact_report` and the serializers (mexplore23 `make_pxo`/`make_ora`).
- Milo bindings: the committed msw01 south author (`render_idle`, roles, palette), the same as mnw01 north.
- Neutral source: the committed Milo east static author `draw()`. It must recompose to the existing east static PNG (`af45b51d…b17a`). The east PXO/ORA/manifest/palette are read-only hash pins, and they were unchanged before and after the run.
- East-specific replacement (in memory only): `side_parts`, `static_feet` and `render_side`. The jexplore39 versions assume Jiang's far toe peeks ahead of the near toe; Milo's far leg is set back 4 texels. Changes:
  - The far leg is the visible static strip laid over a darkened near-leg copy shifted -4 (hidden fill).
  - Every far texel visible at neutral is forced to the neutral pixel, and the module asserts that the neutral pose recomposes byte-exact.
  - The far forearm and the green far-wrist wristband share one opposite-swing shear.
  - The case rides the torso (bob only).

## Files (new only)
- `tools/rpg-2-star-ocean-the-second_milo_walk-east-source-author_unapproved-mew01-v01_20261024-061500-3e1a5c07.py` (raw sha256 `8bcffaca…62b2`)
- `tools/rpg-2-star-ocean-the-second_milo_walk-east-independent-check_v01_20261024-061500-3e1a5c07.py` (raw `e3224ab6…2c30`; no author/engine imports)
- `outputs/milo-ew01/rpg-2-star-ocean-the-second_milo_walk-east-qa-orchestrate_v01_20261024-061500-3e1a5c07.py`
- Build output, 89 files listed in `outputs/milo-ew01/…file-list…-1910dd40.json`:
  - 41 PNGs in `png/`: static, idle ×4, walk ×12, stop s1/s2 ×12
  - editable PXO `…-04413ee1.pxo` (far-limbs + 11 Milo roles + guides, 41 frames, 14 tags)
  - neutral ORA `…-d7d101e6.ora`
  - source manifest `…-9c61f2d2.json`
  - `pkg/`: sprite set, stop supplemental (`runtime_default: false`), package-local registry, PNG copies
- QA runs: `outputs/milo-ew01/logs/{check1,check2,build1,indep1..indep4}`, `outputs/milo-ew01/indep1..indep4/`, scratch diagnostic `outputs/milo-ew01/scratch/`.

## Results
- Author `build`: WROTE 89, REBUILD 89/89, deterministic, SOURCE 19/19, pins exact, PASS.
- Independent `indep4`: **39/39 PASS**, all 21 negative controls rejected.
  - Native Pixelorama 1.2.3 headless export with Dummy audio and isolated XDG: 41/41 frames RGBA-exact, exit 0, source unchanged.
- Failed attempts retained:
  - `check1`: assertion, the neutral pose did not recompose. Cause: near boot-top texels hidden under the far trouser leg; fixed in the author.
  - `check2`: run before build, so files were missing. Its `check-result-check` JSON stays as a failed result.
  - `indep1` and `indep2`: the s2 → idle f00 endpoint check compared cel-split heels and then occluded pixels. Both were measurement errors (the f00 static `boots` cel holds both feet). Replaced with a profile-geometry endpoint check: near toe = neutral front edge, far heel = neutral back edge, sole opaque.
  - `indep3`: the p00 endpoint control slid a lifted foot. It was redesigned to slide the grounded foot; the controls now reject both near-foot and far-foot slides.
- Application diagnostics: Pixelorama emits 4 shader `ERROR: Condition "!actions.custom_samplers.has(...)"` lines. They are reported separately, are not an export-equality gate, and the run is not application-clean.

## Contact / slip (world space, 140 logical px/s, east = +x)
- Gated (frozen jexplore39 criterion): planted-foot slip at 40 ms boundaries is **0.8 src (0.4 logical)**. This is ≤ 1 and is integer rounding of 11.2.
- Each foot is grounded for 4 of 12 phases. **Flight at p4, p5, p10, p11** (a jog-like stride, not double-support walking).
- Stop bridges: a grounded foot moves 0 through walk p → s1 → s2, and s2 → idle f00 has error 0 in all 12 phases. Every bridge ends on the exact neutral bytes.
- **Disclosed residual, not a pass:** inside a held 40 ms frame the host keeps moving, so the planted foot slides forward and snaps back at the next tick.
  - 1 ms samples: up to **11.72 src (5.86 logical)**.
  - 60 fps ticks: 10.667 src (5.33 logical).
  - Near-toe world position at hold edges: 65.0 → 75.92 at t=0/39 ms, then 65.2 at 40 ms, and so on.
  - The animation is not footlocked and not slip-free.

## Limitations / gaps
- No source-fit harness or Godot runner pass was done for east (time budget). There is no Godot import/runtime, normal-input motion or normal-host stop playback. The generic loader ignores the stop supplemental.
- The GIF preview is a source-bound PIL composite, not a Godot capture. GUI SaveAs/reopen was not verified.
- The far forearm and wristband stay in front of the coat even when swung back (static layering).
- Legs are sheared static texels, and the far leg is a darkened fill. One cycle covers both walk and run, with no separate run cycle.
- Art, fluidity and motion are **not approved**. Human review of a normal-speed movie is still required. Nothing has been committed; the coordinator must verify and commit the selected paths.
