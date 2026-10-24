# Heya south walk/stop source QA (UNAPPROVED)

Task: `content.char.heya.walk-south` (batch165). Dependency `content.char.heya.static-south` is DONE and its Heya
south PNG/PXO/ORA/manifest/palette are byte-pinned by the author and re-checked by the independent checker.
Scope: SOUTH ONLY. No west/north/east, idle task, default, shared ledger/Bible/registry, git index/commit/push or
creator art approval was changed. This note is source-production evidence, not art or motion acceptance.

## Produced artifacts

- Author: `tools/rpg-2-star-ocean-the-second_heya_walk-south-source-author_unapproved-h165sw-v01_20261024-143000-h165s001.py`
- Independent checker: `tools/rpg-2-star-ocean-the-second_heya_walk-south-independent-check_v01_20261024-143000-h165s001.py`
- Godot fit runner / test-only script:
  `tools/rpg-2-star-ocean-the-second_heya_walk-south_normal-speed-fit_v01_20261024-143000-h165s001.py`,
  `tools/rpg-2-star-ocean-the-second_heya_walk-south_normal-speed-fit_test-only-v01_20261024-143000-h165s001.gd`
- Source/output staging: `outputs/heya-sw165/` (editable PXO/ORA, 41 deterministic PNGs, source manifest,
  optional runtime sprite set + stop supplement, check results, independent result, native log, preview).
- Opt-in package: `game/assets/characters/heya-native-v01/south-walk/` (byte-equal PNG/JSON copies, `.gdignore`,
  `.gitattributes`). No existing Heya static file was replaced.

Contract: 80x112 native, binary alpha, pivot (40,104), body rows 8..103, density 2, display scale 0.5 = 48 logical
px. 4 idle frames (700/200/400/200 ms), 12 walk phases (40 ms, 480 ms cycle, host normal 140 logical px/s), and 12
phase-specific stop bridges `[walk p, s1, s2, idle f00]` with a 120 ms inclusive settle. Static and idle f00 are
the exact existing Heya south static PNG bytes.

## Executed checks (actual results)

1. Author `build|check`:
   `python -X utf8 -I tools/...heya_walk-south-source-author...py check`
   - `REBUILD 91/91 DETERMINISTIC True`, `SOURCE 18/18`, `RESULT PASS []`.
   - Real contacts: front in-place planted-foot world slip 11.2 source texels = 5.6 logical px per 40 ms; flight
     phases `[4,5,10,11]`; each foot grounded 4/12 phases; stop-bridge grounded slip 0.0.
   - The 5.6 logical px/40 ms residual is preserved and disclosed, not called slip-free or footlocked.
2. Independent checker (no author imports):
   `python -X utf8 -I tools/...heya_walk-south-independent-check...py --out outputs/heya-sw165/independent-2`
   - `INDEPENDENT PASS 35/35`; all 41 frame PNG raw hashes match; PXO cels recompose to every PNG; tags,
     timing boundaries (39/40 and 479/480/481 ms), stop boundaries (40/80/120 ms), 12 stop endpoints exact neutral,
     palette/border/identity checks pass; 13 negative controls rejected (tampered PNG/PXO, malformed bridge, wrong
     endpoint, 0/41 ms duration, wrong pivot, foot slide, off-neutral endpoint, unchanged walk bitmap).
   - Native Pixelorama export: 41/41 frames RGBA-exact, exit 0, no timeout, source unchanged. Application diagnostic
     cleanliness FAILS separately with 4 `custom_samplers` shader diagnostics; export equality and application
     diagnostics are not conflated. GUI SaveAs/reopen is NOT verified.
3. Godot Dummy-audio normal-speed source fit:
   `python -X utf8 -I tools/...heya_walk-south_normal-speed-fit...py`
   - `HEYA_H165SW_SOUTH_WALK_NORMAL_SPEED_FIT PASS`; checked runner, finite deadline, no missing marker; 6 captures
     at 640x360; walk phases 2/11/7 then phase-7 stop s1/s2/idle f00; elapsed targets within bound; frame-kind and
     frame-hash re-derived independently; pivot/scale/logical height exact; runtime adopted false, art approved false.
   - Proof under `outputs/heya-sw165/fit/capture-r3/` and the matching `*-capture-r3.json` proof.
4. Source-bound normal-speed preview (PIL, not a Godot capture):
   `outputs/heya-sw165/independent-2/rpg-2-star-ocean-the-second_heya_walk-south-normal-speed-preview-source-bound_...gif`
   and the walk/s1/s2 contact sheet. These are inspection aids, not human motion approval.

## Identity and art limitations (not approval)

The 13 Heya role layers are preserved: auburn low braided coil, grey-white scarf with screen-right tail, ivory open
coat, pale apron, charcoal underdress, dark-red bag with brass, herb sprig, gloves, boots. Per frame the author/checker
verify the low braid, scarf, bag, herb, coat and apron colours/regions; the independent checker also verifies the braid
keeps a constant offset to the hair.

The Heya static has no separate trousers layer. This source therefore articulates the boots only: each boot is split at
x=40 and lifted below the knee (max 4 source texels) for its swing; the A-line dress hem and coat/apron/bag are
torso-only (bob, never lifted) and the braid/scarf have no secondary motion. A lifted boot can pass behind the static
hem, so the lower-body gait is coarse and the front view is in place. This is the frozen jexplore39 front residual,
reused without threshold change. It is not a repaint, footlock or fluidity proof. Heya south static/portrait remain
UNAPPROVED. No creator art, motion, runtime or default approval is claimed.

## Scope and integration boundary

All writes are under `outputs/heya-sw165/`, `game/assets/characters/heya-native-v01/south-walk/`, the four task-specific
`tools/*heya*walk-south*` files, and this QA note. No existing game asset was overwritten (package directory was new).
The unrelated dirty Git index, shared ledger, Bible, registry and defaults are untouched. The coordinator owns commit,
integration and ledger transitions. Starting canonical meters are production 62.7%, inspection 21.6%, approval 7.8%;
this note makes no meter claim.
