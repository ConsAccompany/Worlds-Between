# Heya NORTH walk/stop (content.char.heya.walk-north) — source verdict (UNAPPROVED)

- Task: `content.char.heya.walk-north` (batch171, provider scope only).
- Dependency: `content.char.heya.static-north` DONE — `game/assets/characters/heya-native-v01/north/`
  (`HEYA_NORTH_V01_ALL_OK`, `outputs/heya-n152/author-check.log`).
- Direction scope: **north only**. South/west/east walk and idle tasks are not produced here.
- Status: produced technical source, independently checked; **not** art/motion approved, **not** runtime-integrated,
  **not** adopted as default.
- Production is source-only. No shared ledger/Bible/registry/Git-index edit, commit or push was made by this provider.

## Deliverables

- Author: `tools/rpg-2-star-ocean-the-second_heya_walk-north-source-author_unapproved-hnw171-v01_20261024-151500-hnw17101.py`
  (`sha256 fb1eb8ab0cbb8d5724870548865641cfb4d4e96aca81d428f34542d6b487cd3d`)
- Independent checker: `tools/rpg-2-star-ocean-the-second_heya_walk-north-independent-check_v01_20261024-151500-hnw17101.py`
  (`sha256 c1172e367b555fc03e8acb9bb50357c79b1530ee4d828822e4a009c52bd9c987`)
- Godot fit driver: `tools/rpg-2-star-ocean-the-second_heya_walk-north_normal-speed-fit_v01_20261024-151500-hnw17101.py`
  (`sha256 3081ad29585a2e68c35ace0829dd99a4928f3e8afb714cb566e752a5c7d18cd5`)
- Godot fit script: `tools/rpg-2-star-ocean-the-second_heya_walk-north_normal-speed-fit_test-only-v01_20261024-151500-hnw17101.gd`
  (`sha256 258a49144fcde9ddb5a6ab5fd7bdc85b2a86b028c708182993ffcd71f10d0c16`)
- Source output / editable native / package:
  - `outputs/heya-nw171/` — 12 walk PNGs, 4 idle PNGs, 24 stop-bridge PNGs, editable PXO/ORA, manifest, file list,
    check results, contact sheet/preview under `independent-2/`, Godot captures under `fit/capture-r3/`.
  - `game/assets/characters/heya-native-v01/north-walk/` — opt-in runtime sprite set, stop supplemental, package-local
    registry, PNG copies, `.gdignore`, `.gitattributes`.
- Author manifest: `outputs/heya-nw171/rpg-2-star-ocean-the-second_heya_walk-source-manifest_unapproved-hnw171-v01_20261024-151500-3ec3c594.json`
  (`sha256 e9da00e81607a3ae147b16ec8559dab62df8a66fde5cec571968852912b94bb2`).
- Independent result: `outputs/heya-nw171/independent-2/rpg-2-star-ocean-the-second_heya_walk-north-independent-result_v01_20261024-151500-hnw17101.json`
  (`sha256 0b76ee1f73df42fcefc8a01015f90a4999c3731cb190151777c8678c3c22e53a`), **37/37 checks PASS**, 14/14 negative
  controls rejected, native export **41/41 RGBA-exact**.
- Fit proof: `outputs/heya-nw171/fit/rpg-2-star-ocean-the-second_heya_walk-north-normal-speed-proof_test-only-v01_20261024-151500-hnw17101-capture-r3.json`
  (`sha256 66c301a97c667a4dc09cfd9ebcc47aa23d79b7540f9191c4130541970eb1e31a`), **PASS**, 12/12 captures.

## Reused pipeline (no new framework)

- Frozen `jexplore39` Jiang Lan exploration engine (timing, 12-phase front/back cycle, `stop_poses`,
  `contact_report`, `leg_transform`, PXO/ORA serializers, `mexplore23` helper) — in-memory rebind only.
- Heya north static author `h152n001` — neutral rear-view role layers, palette and pins; **no south mirror**.
- Method references: Heya south walk `h165sw`, Heya west walk `hww167`, Muxiu/Yanke north walk.
- Checked runner `rpg-2-star-ocean-the-second_godot_checked-runner_v01_20261018-203400-f74ac6d1.py`; existing Xvfb /
  OpenGL3 / Dummy-audio fit pattern. No new test framework.

## Commands actually run (repo root)

```bash
V=/home/kel/projects/worlds-between/tooling/venv/bin/python
# 1. staged source build (fresh staging tree)
WB_STAGE_REL=outputs/heya-nw171/stage $V -X utf8 -I tools/rpg-2-star-ocean-the-second_heya_walk-north-source-author_unapproved-hnw171-v01_20261024-151500-hnw17101.py build
# 2. install only the three differing existing outputs through the authorized helper (hash-verified backups)
python3 tools/wb_safe_replace.py outputs/heya-nw171/stage/outputs/heya-nw171/<manifest|file-list|check-result-build> outputs/heya-nw171/<same>
# 3. deterministic final author check
$V -X utf8 -I tools/rpg-2-star-ocean-the-second_heya_walk-north-source-author_unapproved-hnw171-v01_20261024-151500-hnw17101.py check
# 4. independent checker (native Pixelorama export + preview + tamper controls)
$V -X utf8 -I tools/rpg-2-star-ocean-the-second_heya_walk-north-independent-check_v01_20261024-151500-hnw17101.py --out outputs/heya-nw171/independent-2
# 5. bounded Godot normal-speed source-fit
$V -X utf8 -I tools/rpg-2-star-ocean-the-second_heya_walk-north_normal-speed-fit_v01_20261024-151500-hnw17101.py
```

Results: author `REBUILD 91/91 DETERMINISTIC True`, `SOURCE 20/20`, `RESULT PASS`.
Contacts: walk max world slip `11.2 src / 5.6 logical` per 40 ms boundary, flight phases `[4,5,10,11]`,
stop-bridge grounded slip `0.0` (all 12 entry phases), endpoint exact neutral. This is the frozen in-place residual,
**not footlocked and not slip-free**.

## Independent check highlights

- 41/41 frame PNG raw hashes matched; 80×112, binary alpha, clear border, pinned Heya palette only.
- PXO 41 frames recomposed to every PNG; tags `north-idle 2-5`, `north-walk 6-17`, 12 stop tags.
- Exact timing boundaries: 39/40/479/480 ms walk; 699/700/899/900/1299/1300/1499/1500 ms idle; 39/40/79/80/119/120 ms
  stop bridge.
- Feet split at x=40 on raw `boots` cel sole row 103; each foot grounded exactly 4/12 phases; planted screen position
  constant while grounded.
- Rear identity: low nape braid constant offset to hair top (16 rows), scarf back tail screen-left, bag screen-left,
  herb screen-right, coat/apron present in every frame; **no eye/mouth colours in the face layer**.
- Anti-mirror: north neutral vs `fliplr(south)` differs in **1981 opaque texels**; north static is its own rear art.
- Negative controls rejected 14/14: tampered PNG, tampered PXO cel, malformed stop JSON (idle f01), `frame_ms=39`,
  out-of-scope `south` bridge entry, missing bridge frame, missing phase, zero/41 ms duration, wrong pivot,
  bridge foot slide, off-neutral endpoint, unchanged “walk”, erased identity.

## Native PXO equality vs application diagnostics (severed)

- Pixelorama `--headless --export`, isolated XDG, 90 s deadline: exit 0, no timeout, 41/41 frames RGBA-exact,
  source PXO unchanged, 6.63 s.
- Application diagnostics remain: **4×** `ERROR: Condition "!actions.custom_samplers.has(function->arguments[j].tex_builtin)" is true. Continuing.`
  These are retained and are **not** an export-equality gate. Export equality does not establish clean application
  behavior; GUI SaveAs/reopen was not tested.

## Godot normal-speed source-fit (test-only, Dummy audio)

- Xvfb 640×360, OpenGL3, Dummy audio, checked runner, 75 s deadline, pass marker
  `HEYA_HNW171_NORTH_WALK_NORMAL_SPEED_PASS captures=12`; elapsed 2.57 s, exit 0.
- Timeline: start → walk (p6/p11) → stop phase 7 (s1, s2, idle f00) → repress walk p0/p6 → reversal (reverse stop
  bridge s2, s1, then walk p7) → idle. 12 targets exact, frame indices and hashes exact, pivot `[40,104]`, 0.5× game
  scale, 48 logical height.
- Alternating **bright/dark** themes with **EN/ZH** labels (`walk / 行走 bright / 明亮`); both themes present in every
  manifest. Capture tests are not default adoption or art approval.

## Preserved failures / corrections (honest record)

1. First author check **FAILED** my own new anti-mirror assertion because I required the *flipped alpha silhouette* to
   differ by ≥400 texels; north vs flipped south is only 362 alpha texels (near-symmetric rear outline). The genuine
   requirement (no mirrored copy) was replaced with a stricter **raw opaque-pixel** comparison; north vs flipped south
   = 1981 differing texels. This is a test correction, not a weakened art/contact criterion.
2. A broadcast bug in that new check (`(112,80)` vs `(112,80,1)`) raised `ValueError`; fixed, then rebuilt.
3. The author's overwrite guard refused the changed manifest/file-list. A `WB_STAGE_REL` staging path was added, the
   new tree rebuilt deterministically, and only the 3 differing existing files were installed through
   `tools/wb_safe_replace.py` with verified backups (see `outputs/development-backups/{c57e6dca…,41037a66…,ca77dcf8…}`).
4. Checker run 1 was 37/37 PASS but had a cosmetic check label `south-only`; it was corrected and rerun as
   `independent-2` (37/37 PASS). Run 1 is retained.
5. Fit run 1/2 captured the theme/label one frame late (theme applied after `frame_post_draw`). The loop was reordered;
   run 3 is authoritative. Runs 1/2 and their proofs are retained.

## Limitations (disclosed, not hidden)

- North walk is **in place**: a planted foot travels with the host 11.2 source texels (5.6 logical) per 40 ms held
  frame. Residual is disclosed; **not footlocked, not slip-free**.
- Legs are static boot texels split at x=40 and lifted below the knee; no foreshortening repaint. The A-line dress hem
  is torso-only and not lifted, so a lifted boot can pass behind the static hem (coarse lower-body silhouette).
- Braid, scarf, coat, apron, bag and herb ride head/torso with no secondary motion.
- Stop supplemental is not read by the generic loader (immediate idle); stop playback is source scope only.
- North only; package is opt-in/non-default and has no south/west/east entries.
- Heya north static and portrait remain UNAPPROVED; no art, motion or fluidity acceptance.
- 4 known Pixelorama application diagnostics remain (export equality intact, application not “clean”).
- Fit is a source-fit overlay, not ordinary actor integration, normal-host stop playback or human motion review.

## Independent rerun commands

```bash
cd /home/kel/projects/worlds-between/repo
/home/kel/projects/worlds-between/tooling/venv/bin/python -X utf8 -I tools/rpg-2-star-ocean-the-second_heya_walk-north-source-author_unapproved-hnw171-v01_20261024-151500-hnw17101.py check
/home/kel/projects/worlds-between/tooling/venv/bin/python -X utf8 -I tools/rpg-2-star-ocean-the-second_heya_walk-north-independent-check_v01_20261024-151500-hnw17101.py --out outputs/heya-nw171/independent-3
/home/kel/projects/worlds-between/tooling/venv/bin/python -X utf8 -I tools/rpg-2-star-ocean-the-second_heya_walk-north_normal-speed-fit_v01_20261024-151500-hnw17101.py
```

## Bounded next action

Coordinator independently inspects the source bytes, native export and captures, then decides scoped integration and
audited ledger transitions. No default adoption or art approval is inferred from these tests. This provider does not
own commit/push, the shared ledger/Bible/registry or the Git index.
