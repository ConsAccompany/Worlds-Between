# Female NORTH run/stop v06: stop/re-press mechanical fix, unapproved

Task: `content.char.protagonist-female.walk-north`. Root authorized this bounded mechanical fix of v05's 952 matrix failures. No art, motion or creator approval is claimed. Nothing was staged, committed or pushed. No ledger, index, default, Site or game file was written. The `git status --porcelain game` hash is `bf776733` before and after, and the index is empty. Every Godot run used the canonical checked runner with isolated APPDATA/LOCALAPPDATA under `%TEMP%\fn6`. v01–v05 sources, outputs and the v05 failure report (77078/952) are unchanged.

## One coherent change

Model: `tools/…run-stop-source_unapproved-v06_20261019-001844-7759f49b.gd`, sha256 `1f25c2aac2837d14a21eb2c8ddd60f93c19f2570cd486716003394e6f7789562`. It is v05 plus changes to the stop and re-press transition code only. The gait, the art, the 128 steady states and their cels are unchanged.

1. **Stop landings:** the first foot steps home over 0–0.060 s and the second over 0.020–0.078 s. v05 used 0.04–0.11 s.
2. **Stop step path in screen rows:**
   - A foot that starts above its home row stays at least 1 row above it until it lands.
   - A foot that starts at or below its home row rises to it monotonically with a 1-row heel peel. It never passes the home row, which removes the v05 dip-relift.
3. **Torso settle:** the torso now settles in 0.12 s. Arms, hair and scarf keep 0.24 s, so the last moving frames carry no leg change.
4. **Run (re)start, using the first frame's known travel:**
   - If the grounded lead's stance survives that frame, v05's rule applies.
   - If both feet are down and it would not survive, the lead holds its world point for the first frame only (push-off), so the two feet do not lift together (hop).
   - Otherwise the airborne foot re-enters at q108 and lands after 20 rows.
   - Restart blends take 0.07 s. A foot leaving a held contact blends from that contact instead of being pulled back to its pre-press pose.
   - The idle-start path shares this code, so it is affected too, at ≤ 35 Hz only.

## Results

| gate | result |
|---|---|
| **Full frozen matrix**, run once. v06-bound copy `2395bf54`; it differs from v05 `e3f72f3f` only in model path, hash and labels. | **78636/78636, 0 failed**, 408 s. Model hash is constant (`invalidated=false`). Log has no ERROR. Report `.json.gz` sha `9a1cfd3d…` (raw `ee0e2d9c…`). |
| Matrix maxima at 30 / 60 / mixed | landing 0.100 / 0.083 / 0.0792 s; support 0.100 / 0.083 / 0.0792 s; settle 0.200 / 0.183 / 0.192 s; last-moving-frame diff 63 / 63 / 53 texels (v05: 964) |
| Targeted pre-check: same predicates, 19 failing-family phases (`4467d9a6`) | 12026/12026 (diagnostic only, not the gate) |
| Steady identity vs v05 (`6bf159f9`) | 7/7: 280 Hz states and cels, and 30/60 Hz states and cels, identical |
| City bright EN 30 fps capture (`cd0b358d`, v05 harness re-bound) | **340/340**. Heel-cap travel 0.0, cadence 4.29. Both stops land by 0.100 s and settle at 0.200 s. Re-press support on the first frame. |
| Annex dark ZH 60 fps capture | **695/695**. Heel-cap travel 0.0, cadence 4.44. Both stops land by 0.083 s and settle at 0.183 s. Re-press support on the first frame. |

## Outputs in `outputs/female-north-run-v06/`

- **Native transition frames:** 168 separate native 80×128 PNGs. These cover 8 representative failure cases, each rendered by both v05 and v06 frame by frame. One texel equals one screen pixel at gameplay scale. Index: `…native-transition-frames-report…json`.
- **Gameplay frames:** 20 critical gameplay PNGs (idle, start, release, both landed, stop settled, re-press, re-press support, and the final stop's release, both-landed and settled frames), listed in `…critical-gameplay-frames…json`.
- **Movies:** two normal-speed MP4s, 1280×720 at 2×, without burned-in labels: city `d6be4216…` and annex `65954060…`.
- **Reports and logs:** both capture reports and all logs, including the v05 and v06 diagnostic logs.

## Limitations (honest)

- **Push-off hold.** From the exact static pose, a home foot has only 7 world-locked rows before the −7 peel, so a no-hop re-press at ≤ 30 Hz must overextend for one frame:
  - at 30 Hz the trailing foot reaches depth −9;
  - at 24 Hz it reaches −12, and the next blend frame is still −11.3.
  At gameplay scale the 24 Hz frames read as a long, stilt-like trailing leg (`…repress-both-home-mixed-q12-r3-v06-f04/f05…`). This replaces v05's both-feet-off hop. It is a visual trade-off for root to judge.
- **Fast stop landings.** At 30 Hz a high swing foot comes down in two frames.
- **Heel-peel stepping.** A foot stepping home from behind shows only a 1-row heel peel, not a lifted arc.
- **Not done in this pass:** no PXO/ORA rebake or native full set. The v05 package stays the produced content, with failed readiness. MP4s are yuv420p.

## Native source package closeout (tag v06_20261019-004238-ad92c263)

Root accepted the v06 mechanical pose result as the basis for this technical native step only. That is not creator approval, a fluidity judgment or runtime adoption. The motion source `1f25c2aa…` and the frozen matrix were not changed.

**Wrappers.** The v05 bake and packager were cloned into new files. Only the model path and hash, tag, output folder, labels, PXO user_data text and the zip timestamp differ:
- bake `…native-bake_test-only-v06_20261019-004238-ad92c263.gd`, sha `8162007c…`;
- packager `…native-package_v06_20261019-004238-ad92c263.py`, sha `05e83611…`.

**Bake.** Two independent bakes each produced 145 cels: 128 run cels plus a 17-frame representative stop. The stop is release q25 at 60 fps, chosen by the v05 rule (largest final settle step, 63 texels). All 128 stop finals are exact static, and the second bake is byte-identical.

**Package: 1186/1186 gates.**
- Run PXO `9529c89e…` and ORA `5a082a7a…`: 128 cels at 70 fps × 0.25.
- Stop PXO `d4b1ed16…` and ORA `ca8ea5a7…`: 17 cels at 60 fps.
- All 13 role layers plus hidden, locked guides. Cell 80×128, pivot 40/104, scale 0.5.
- The final stop cel equals the static image. Torso roles equal the static roles shifted by the body offset, and colours stay within the approved v8 palette.

**Pixelorama 1.2.3 reopen.** Exports are exact: run 1664/1664, stop 221/221. Each process logged 4 known inherited shader diagnostics and no unexpected ones, so **cleanAppSuccess=false** and GUI Save As is unverified.

**Evidence manifest:** `outputs/female-north-run-v06/rpg-2-star-ocean-the-second_female-north-run-stop_evidence-manifest_v06_20261019-004238-ad92c263.json` (sha `708ad73d…`). It links the full matrix (78636/0), the steady identity check, both captures and movies, the critical frames, the native package and the limitations above. Index empty; game status hash `bf776733` is unchanged.
