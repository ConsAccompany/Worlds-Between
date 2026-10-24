# Muxiu north walk/stop — source verdict, UNAPPROVED

Canonical task: `content.char.muxiu.walk-north`. Sole producer run through the adapter; the coordinator independently
inspects and commits. Tested base `0fc437a8a8a566836933b3020f94d1e422d7b92c`. Recorded 2026-10-24 UTC.
SHA-256 means raw bytes; text LF hashes are labelled separately. Starting canonical production/inspection/approval
meters are unchanged by this source-only batch; no ledger/Bible/registry/default change and no self-approval.

## Production boundary

North/back walk-run cycle and phase-aware stop for Muxiu, source-only. 80x112, pivot (40,104), body rows 8..103,
display scale 0.5 = 48 logical px, binary alpha, same 27-colour Muxiu palette and 13 visible roles. The neutral
layers come from the committed north static author and recompose byte-exactly to the committed north PNG.
Outputs: layered animated PXO (41 frames), supplemental static ORA, 41 PNG frames, source manifest, file list,
opt-in runtime sprite set, and supplemental stop data. Existing north/south/west source is read-only and pinned.
No runtime/default wiring, no east, no `north-walk` deletion, no art/motion approval.

- Author: `tools/rpg-2-star-ocean-the-second_muxiu_walk-north-source-author_unapproved-nw89-v01_20261024-084500-nw89a001.py`
  raw/LF SHA-256 `7e9bd972218656a17fdb6c3e550860ed1f039ce7a2c14f1820c11c87f038f7ff`.
- Independent checker: `tools/rpg-2-star-ocean-the-second_muxiu_walk-north-independent-check_v01_20261024-084500-nw89a001.py`
  raw/LF SHA-256 `76db90e0eb89220388f9bb12781575bfe47600aadb96fa6b16e754980733f011`. It imports no author/engine.
- Package: `game/assets/characters/muxiu-native-v01/north-walk/`.
- Manifest: `outputs/muxiu-nw89/source/rpg-2-star-ocean-the-second_muxiu_walk-source-manifest_unapproved-nw89-v01_20261024-084500-af95ebb6.json`
  raw/LF `71a8ffddaf6d11cc852b07f0accefbe7e165f14d8514368011b63c4365627752`.
- File list: `outputs/muxiu-nw89/source/rpg-2-star-ocean-the-second_muxiu_walk-file-list_unapproved-nw89-v01_20261024-084500-2882bddb.json`
  raw/LF `568e0830c8fcb92a8a48470edacf0b0da751caa78fa1a8e8a63b7fcd1df1b315`.
- PXO raw `e675da8e21e8646689dbb198c09ad2e651e729396c9f2a4f247a4e25fad45442`.
- ORA raw `ba857fe241fd70308a364f6273b9c01b792362c44e54c1b2e766b4ef83f04810`.
- 41 frame PNGs: `frame_png_set_sha256` = `12bea63f51d2505a4a44128d64a740a53f3598f17d99e7ef1ad5e48649c2707b`
  (sorted raw bytes concatenated; individual hashes are in the manifest/file-list).
- Runtime sprite set raw/LF `eb366c47fc195ba4fef54370a8c8ff1fe98498ad894e1aa88171a46daeba24e6`,
  supplemental stop raw/LF `8e7e6e4d2b7c4cee617057bc711b47ff8e52dd03e5a9ba0af07cf798e481ecbc`,
  registry raw/LF `24d35bdd799a876b34346c13a316656b03884bd28ae6ce256dcf410f7b22ae78`.
- Independent result: `outputs/muxiu-nw89/independent-r3/rpg-2-star-ocean-the-second_muxiu_walk-north-independent-result_v01_20261024-084500-nw89a001.json`
  raw/LF `e4c645813fd3487d8c32a827d0b6f6c9f614e600fa091eef32c44d2d554264c1`.

## Pins (all verified before and after)

Reused engine jexplore39 raw `ae8654f28c89e4c11ef7c52b61fc87ee992af5ae805277998102e4ba9bf80cd5`; north static
author r2 raw `06784115351bf1cfdf6c80c91e80f504267706304ec9d6731de8f97fa37b2e1c`; its transitive pins (Lin Que,
Jiang south, male v8pair, Milo south) all `PIN_OK`; Muxiu south/west manifests unchanged relative to their pins.
Engine transitive modules are additionally pinned in the receipt: Jiang south static raw
`35005f3c904802251c773838d61068d4aea847c993f6e354676e88a599db69b4` (also in the north static author pins),
Jiang directions static raw `8191a20bbb24e08628def5583b04241c94981061ff97b7d0ed0a3d5d7cdb0127` (loaded by
jexplore39; the north `load_neutral` override is from the north static author, so it supplies no north pixels),
and mexplore23 raw `93a349eeb4de306b971f36ae50e934e9e278890cd7cdd42e0a138b82097bc1f2` (LF hash in the manifest).
Committed north neutral PNG raw `03062ace22b7e83aacf8d02b6b0d715e6ff0d4ef74c71770ff7fb8aeb96e5bbe`; the four
north editable pins (PXO/ORA/manifest/palette) are byte-exact. `neutral_pins_exact_before_after` is true.

## Source run — PASS

Commands (from repo, `../tooling/venv/bin/python -B -X utf8 -I`, logs in `/tmp/nw89_build.log` and `/tmp/nw89_check.log`):

- `...north-source-author...py build` → rc0, `WROTE 89 files`, `REBUILD 89/89 DETERMINISTIC True`, `SOURCE 20/20`, `RESULT PASS []`.
- `...north-source-author...py check` → rc0, `REBUILD 89/89 DETERMINISTIC True`, `SOURCE 20/20`, `RESULT PASS []`.
- Contact report: in-place residual `11.2` source px (`5.6` logical) per 40 ms; `flight_phases=[4,5,10,11]`;
  stop-bridge grounded slip `0.0`. No threshold was changed for north.

## Independent checker — PASS 42/42

Command: `...north-independent-check...py --out outputs/muxiu-nw89/independent-r3` → rc0, `INDEPENDENT PASS 42/42`.
It re-derives from bytes (not author metadata): all 41 PNG hashes; binary alpha/border/palette; PXO 41-frame layer
composition == every PNG; ORA role composition == neutral PNG and mergedimage == neutral PNG; tags/frame order;
walk 480 ms and idle 1500 ms exact boundaries (39/40/479/480/481, 699/700/…/1500); stop 40 ms steps and 120 ms
inclusive settle; boots sole-row contact with per-foot 4 grounded phases, planted-screen-motion 0, held-frame
residual, all 12 stop-entry phases and exact neutral endpoint; legwraps lift with boots; bracelet constant 9-row
offset on the screen-left arm; north identity anchors; no eyes/mouth; no whistle wood. Negative controls rejected:
tampered PNG hash, tampered PXO cel, malformed stop JSON (idle f01, frame_ms 39, west entry, missing frame, missing
phase), duration 0 and 41, wrong pivot, bridge s1 slide, off-neutral endpoint, unchanged bitmap, injected eye colour,
injected whistle wood.

The first independent invocation failed on a checker path glob (no manifest; `outputs/muxiu-nw89/independent/FAILED-first-run.log`
retained), and the second (r2) failed only because the injected-wood control set RGB without alpha; both are retained,
the r2 result is `NOT-REJECTED` for that control, and r3 after the control fix is the PASS above. No source/test gate
was weakened; the control fix makes the negative control actually reject.

## Native application diagnostics — separate, FAIL

Pixelorama `--headless --audio-driver Dummy --quit -- --export` of the 41-frame PXO (fresh XDG dirs under
`outputs/muxiu-nw89/independent-r3/xdg`, 90 s deadline): rc0, 41/41 frames RGBA-exact, source unchanged, no timeout.
**Application-clean is false:** four shader compile diagnostics
`ERROR: Condition "!actions.custom_samplers.has(function->arguments[j].tex_builtin)" is true. Continuing.`
are retained in `...north-native-export_test-only-v01_20261024-084500-nw89a001.log` (raw SHA-256
`6e86f1b94065f76140a359590c36a8d1060aa69ee3c740b27de17cb18e2c2fee`). Exact native export is not an
application-clean verdict; GUI SaveAs/reopen is not verified. No claim that all native checks passed.

## Targeted Godot probe — PASS

Checked runner, 60 s deadline, Dummy audio, session-local HOME/XDG:
`../tooling/venv/bin/python -B tools/rpg-2-star-ocean-the-second_godot_checked-runner_v01_20261018-203400-f74ac6d1.py --timeout 60 --expect M1_SMOKE_OK --log outputs/muxiu-nw89/godot/m1-smoke-r3.runner.log -- ../tooling/bin/godot --headless --audio-driver Dummy --path game --script res://tests/m1_smoke.gd`
→ `M1_SMOKE_OK`, `CHECKED_RUN PASS`, exit 0, elapsed 0.656 s. Two earlier attempts are retained: log-open failure
without session-local HOME (`m1-smoke.runner.log`), and a 60 s timeout because `--script` was omitted
(`m1-smoke-r2.runner.log`). The existing fit harness was not run: this package is opt-in and not adopted by the
normal host, so the smoke probe is the targeted runtime check; no runtime wiring is claimed.

## Visual inspection, not approval

The source-bound contact sheet and enlarged p01/p04 frames were inspected. The back view reads: brown hair mass,
braid plait over the screen-right shoulder, moss capelet with cream back tree, rope bracelet on the screen-left
wrist, brown boots/legwraps. Legs are composed as whole left/right columns (trousers below the hip, legwraps,
boots) and the lifted side stays a broad leg, not a detached 1 px sliver; the checker confirms legwraps move with
boots. The cycle is visibly rigid/symmetric, and two flight phases per cycle are inherent to the frozen front/back
model. This is not fluid/footlocked motion and is not human art approval.

## Limitations and retained failures

- In-place front/back model: a planted foot travels with the host 11.2 src (5.6 logical) px per 40 ms held frame;
  NOT footlocked, NOT slip-free. Contact metrics are not fluidity or human motion acceptance.
- Legs are static texels lifted below the knee (no foreshortening repaint); the split at x=40 can show a gap
  between the lifted and standing leg — disclosed static-texel limit.
- Braid/pouches/cloak ride head/torso (no secondary motion); coarse frozen static, cosmetic refinement deferred.
- Supplemental stop JSON is not read by the generic loader (immediate idle); stop playback is source scope only and
  is not normal-host playback.
- Muxiu north static/portrait are UNAPPROVED; no art, motion, fluidity, GUI or creator approval.
- Native application diagnostics above remain a separate FAIL; exact export equality is separately PASS.
- No runtime/default/registry/ledger/Bible edit and no commit by the producer.

## Bounded next action

Coordinator independently inspects the explicit new paths, reruns the checker/native probe as desired, and commits
only those paths if acceptable. Then the next explicitly assigned unpaused task; do not infer north-walk approval,
default adoption, or permission to start other directions from this source pass.
