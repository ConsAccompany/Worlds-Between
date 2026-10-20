# Heroine Sea-of-Stars exploration source v03 — QA note (UNAPPROVED, test-only)

Base revision e6a97c87a265dacbc1399607176a29c3f12f9a93, worktree work/dual08/cl-explore. No game, script, data, default, ledger, Bible or registry edits. No art or motion approval; generated bases are reference sources, not hand-authored pixel art.

## Delivered
- Source manifest (schema `worlds-between.exploration-source.v1`): `outputs/hsea-exp02/src-v03-20261020-172100/rpg-2-star-ocean-the-second_heroine-sea_explore-source-manifest_unapproved-v03_20261020-172100-4aceb0cb.json` (sha256 21a2ddda…5e2c).
- `actor_id` = `protagonist-female` (coordinator correction: the SpriteSetPilot.attach host key; `hero:female` in the earlier brief was a contract error, used only in the rejected v02 run).
- Four directions × idle (1 pose each) + walk (8 phases × 60 ms = 4.167 steps/s). South idle f00 is the approved static, byte-exact (sha256 6bf1d688…e429).
- Per-direction Pixelorama `.pxo` layer sources (all idle+walk frames, layers: under-trouser-paint, far-leg, near-leg, upper-body) and supplemental idle0 `.ora` files.
- Author tool `tools/…heroine-sea-explore_source-author_test-only-v03_20261020-172000-b81d5c3e.py`; checker `tools/…source-check_test-only-v03_20261020-172100-9d2e4a61.py` → 70/70 PASS (schema, counts, durations, names, hard alpha, borders, no opaque row ≥104, idle bodies exactly 96 px ending at row 103, exact south idle0, PXO layers reconstruct every export, deterministic rebuild).
- Godot preview harness `tools/…actual-preview_test-only-v03_20261020-172200-c4f81a07.gd`: 1280×720 movie per context in `outputs/hsea-exp02/prev-v03-20261020-172300/` (city-bright, annex room 2), 406 frames each at 60 fps; checked runner PASS, 0 ERROR lines (exit WARNING: 2 ObjectDB instances leaked).

## Method
East/north bases: Codex imagegen sources in `outputs/hse-dir08` (unapproved), cropped to the alpha bbox, nearest-scaled to a 96 px body, placed on an 80×112 canvas with pivot (40,104), hard alpha ≥128, colours mapped to the approved south palette (32 colours). West = east mirrored, so asymmetric straps and the scarf tail switch sides. Walk: upper body bobs (+1 at contact, −1 at passing). Side-view legs split into thigh and shin+boot segments and rotated about the hip and knee using a planned footfall table. Front/back legs are foreshortened as the foot lifts. A painted trouser under-layer, hidden at rest, fills the joints. On rising frames the top row of each planted leg extends one pixel upward.

## Known limits / failures
- No arm counter-swing and no scarf or ponytail secondary motion. Arms, scarf and hair are fixed in the upper-body layer.
- Nearest rotation leaves small aliasing artefacts and stray pixels on some side-view shin/boot frames. North/south gait reads subtly; foreshortening is the only leg cue.
- Feet slide at 140 px/s: the planted stance travel is much shorter than the required 33.6 logical px per step.
- Preview staging: the placeholder hero is hidden and host processing is disabled. The path is a scripted E→S→W→N square with stops; there is no camera follow and collisions are not tested. The annex start is moved to (250,250) because the placeholder spawns at the door edge. The "room2-dark" context is the survey annex room 2 scene, which is not visibly dark.
- The fresh worktree needed `--import`; 447 tracked `.import` modifications were restored with `git restore`, and 337 untracked import metadata files remain in place (not canonical).
- Native Pixelorama open/export and GUI Save As/reopen were not run; only the Python layer reconstruction was verified.
- The rejected v02 primitive-redraw run stays as evidence in `outputs/hsea-exp02/src-20261020-171600` (actor_id hero:female, 73/73 contract checks; Codex visual FAIL).
- Earlier failed preview attempts are kept with `-attempt1..4` suffixes.
