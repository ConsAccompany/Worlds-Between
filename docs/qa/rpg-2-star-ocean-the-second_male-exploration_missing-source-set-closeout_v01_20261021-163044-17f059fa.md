# Male protagonist: four-direction exploration source boundary

Base: `ccd33bf7638cb1f3782181178db2cfc5185f0b44`. Claude produced the source set; Codex independently corrected loader compatibility, packaged it, checked native/source integrity and normal input. Creator priority: missing MVP deliverables first; cosmetic refinements deferred.

## Frozen production tasks

Existing west/north/east statics(6points), four-direction idle loops(2points), south/west/north/east walk+stop sources(12points):20existing content points. South static remains exact and receives no duplicate credit. Default integration remains open; no art/motion approval or full character acceptance is inferred.

The set has4statics,16idle frames,48gait frames and96intermediate stop frames. Four editable multi-frame PXOs each contain41frames with genuine role layers; static ORAs are also retained. Each direction has12phase-specific stop bridges: current gait exact ->2authored intermediate poses -> exact neutral,40ms/stage,120ms settle. Source pivot40/104,80×112cell,48logical-pixel body at0.5scale.

## Compatibility corrections

The first producer snapshot violated the unchanged loader contract: south idle could shrink to94source pixels, new north outlines crossed the sole line, and side statics were99pixels tall. Codex kept the existing loader limits, bounded new idle head travel, lowered newly authored side head geometry by3source pixels, and cropped the extra north outline at floor row104. The old south neutral PNG remains byte-exact. These changes fix a load blocker, rather than continue an artistic refinement loop.

Runtime manifest paths originally pointed to repository-relative outputs. The deterministic author now copies PNGs losslessly into the new `game/data/mexplore23/png` package and emits relative paths plus the existing generic registry schema. No new runtime framework, host, movement, collisions or defaults were changed.

## Evidence

- Deterministic rebuild:340/340files match.
- Pixelorama native export:41/41frames per direction,164/164total. Shader diagnostic lines remain; GUI Save As/reopen is unverified. Export equality is not clean application behavior.
- Codex independent native-cel composition and source/pack/geometry/contact checks:947passed. Source-mode heel positions and stop drift are measured from actual native layers, not only trusted metadata.
- Real normal-input existing-loader runs: EN30FPS570checks; ZH60FPS1026checks. All idle/gait frames appeared, movement remained140logical px/s, stopping had no physical drift, and the rectangle returned to its start.
- Separate actual640×360gameplay captures and one30FPS8.9second1280×720movie retained. Codex viewed south/north/east walking, west idle and a movie sample. This is scripted compatibility evidence, not a human playtest or artistic fluidity approval.
- Existing heroine/exploration/battle scripts remain unchanged against the base commit.

[Source-bound root proof](../../outputs/mexplore23/rpg-2-star-ocean-the-second_male-exploration_root-source-closeout-proof_v01_20261021-163044-17f059fa.json). The author, source manifest and exact runtime PNGs are linked and hash-bound there.

## Known integration/motion limits

The current generic opt-in loader uses a time clock and immediately hands off to idle. The phase-aware stop bank is produced but not wired through this loader. Side gait has0source-model heel slip only at its declared2logical pixels/phase; the existing140px/s game with40msframes does not match that source model(3.6logical pixels/phase difference). Front/back gait is in-place, not world locked. Maximum source stop heel drift is15texels(7.5logical pixels) on side views,1north and0south. Do not describe these results as proven smooth motion or world foot lock. They remain explicit runtime/motion follow-ups; production credit is separate from readiness and artistic review.

East mirrors west, including light direction. The ENmovie test logged2ObjectDB leak warnings at exit; no script/parser/runtime errors occurred. Defaults, artwork acceptance, source style canon and human playtest counters remain unchanged.

## Next useful boundary

Connect the produced male exploration/combat set into a reproducible opt-in playable path, resolving required timing/stop integration. Keep further cosmetic revisions deferred. Default adoption remains a separate creator decision under the existing project rules.
