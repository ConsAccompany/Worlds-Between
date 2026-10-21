# Heroine front/back front17 v01 — UNAPPROVED source package

Run: `src-v01-20261021-022403` (uid cabad530), baseline stop15 f141d653. Author:
`tools/rpg-2-star-ocean-the-second_heroine-sea-explore_front-back-author_test-only-v01_20261021-022152-ebe12539.py`.

Reproduce (PY = codex runtime python):
- author: `PY -I <author> --out-tag YYYYMMDD-HHMMSS`
- rebuild check: `PY -I <author> --verify outputs/hsea-front17/src-v01-20261021-022403` -> `VERIFY PASS rebuilt=268 on_disk=268`

Evidence: protect-check report 14/14 PASS (4 idle, 24 E/W walk, 96 E/W phase, 8 side legacy bytes equal to stop15;
192 samples s0==walk, s3==idle; palette subset; bounds; PXO hashes). Pixelorama 1.2.3 CLI merged export of the 4 new
PXOs: 13/13, 48/48, 13/13, 48/48 frames RGBA-exact, but 4 shader `ERROR` diagnostic lines per run (retained, not clean).
Changed: 24/24 N/S walk, 8/8 N/S legacy bridges, 96 N/S phase samples (s1/s2 authored). Hashes: raw bytes.

Limitations:
- Method: thigh-only foreshortening + rigid source shin/boot, 0-2 px inward swing, knee cap/fold rows recoloured with
  existing trouser colours; forearms cut from the torso swing -2..+1 px. Upper sleeves/shoulders do not rotate.
- Forearm cut boxes are hand-picked; edge pixels of scarf outline/belt may travel with the arm (north left arm).
- Hair/scarf v04 underlay kept in upper-body (removing it opened a 1 px gap); scarf sway can widen the tail by 1 px.
- Overlap only visible near the crotch (legs rarely overlap in front view); leg-overlap baking is mostly 0 px.
- Toe-off phases (lift 1) float the boot 1 px rather than peeling the heel.
- No runtime profile, game code, checker or ledger change. No fluidity or visual-quality claim; root judges the
  normal-speed actual game. Checker `--front-back-revision` mode is not part of this package (root/support scope).
