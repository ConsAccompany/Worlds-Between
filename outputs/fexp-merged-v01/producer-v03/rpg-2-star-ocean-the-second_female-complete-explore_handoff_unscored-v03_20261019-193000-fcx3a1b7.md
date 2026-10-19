# HANDOFF: female complete-exploration pilot fcx-v03 exact render optimization (UNAPPROVED, unscored, opt-in only)

Base: `d9a86d5` in the `cl-management` worktree, on top of the uncommitted v02 pilot (f2c0a7e1). Nothing was committed, staged or pushed. I did not touch the ledger, Site, account, driver, hosts, loader or package JSON; the receipt checks this. The pilot is still off by default. There is no new art and no change to state, timing or cadence. The global stop file was absent when checked before any mutation.

## What changed (one optimization pass, four model scripts only)

Frozen v02 copies are preserved first in `outputs/fcx-v03/frozen-v02/`, with hashes equal to the v02 receipt: E `f526e06e`, N `1f25c2aa`, S `80bfd5e1`, W `2ca7cee6`.

| Model (text-lf) | Change |
|---|---|
| EAST `6eb186d6…` | `render_pose` paints raw RGBA8 `PackedInt32Array` buffers. Per-layer opaque-row tables are built in `_init()`. `_bone`/`_band` are inlined with per-leg terms hoisted, and a bone is skipped only when its band weight is exactly 0. `_rotate_pixels` is clipped to the forward map of the source's opaque bounds (±0.5, +1 px margin). The spur rule and the trail's first-write-wins rule run on buffers. |
| NORTH `7df9922c…` | Leg, coat, follow and arm loops visit only opaque source texels per row, in the same order, with the same row maps and offsets. Palette constants and the crease test use exact set_pixel texels. |
| SOUTH `373440cf…` | `Comp10.compose` does the PartCompositor + Comp9 + Comp10 chain in one pass over buffers, using per-role texel tables built lazily and invalidated by `load_parts`. Holes, seams and the v09 fill are scanned only inside the composed used-rect. The v10 island flood fill is replaced by row-run union-find labeling, which keeps the same discovery order and the same "first largest kept" rule. Any case it does not cover exactly (error paths, texels outside the cell, transparent drawn texels, unknown roles) falls back to the v02 path `_compose_v10`. The only change in that path is `super(state)` → `super.compose(state)`. |
| WEST `2ca7cee6` | Unchanged and byte-identical to frozen. It already cost about 2 ms per render. |

Interfaces, constructor inputs, `advance()`/`tick()`, snapshots and result keys are unchanged. The v02 per-texel helpers stay in the files. The package builder asserted "copy == source except SOURCE" for EAST/WEST, and the SOUTH file header says GENERATED, so the root must re-bind or regenerate on merge. That is root/DeepSeek scope, and I did not do it here.

## Evidence (checked runner, every listed log clean)

- **RGBA8 probe:** get_pixel→set_pixel is the identity for all 256 byte values, and Color8 equality holds 256/256. Byte copies are therefore exact.
- **Oracle** (`render-oracle-report_v03try2`, PASS): frozen v02 is compiled from source and compared with the current models over identical sequences.
  - Sequences: dense (one gait phase per tick, 300 ticks, then stop) plus 30, 60 and mixed rates. Each covers start, run, stop, same-facing re-press during the stop, a short tap and stop to rest.
  - Snapshots match. Full deep compare covers `full`, every role image, contacts, sole rows, leg info and leg images. For SOUTH it covers body image, shadow image, boots, soles, near, legs and seam/fill/island counts.
  - Counts: E/W/N 676 poses each (554/554/566 unique); S 528 composes (310 unique). That makes 0 mismatches in 2556 comparisons.
  - SOUTH fast path vs fallback: 106/106 equal. Neutral rest shadow is equal. The self-test detects a one-byte change.
  - The first oracle run (`try1`) also passed, before the SOUTH run-labeling change.
- **Model render cost** (same process, frozen → current, p50/p95/max ms):

  | Direction | Frozen | Current |
  |---|---|---|
  | N | 14.3 / 21.3 / 25.2 | 1.29 / 2.05 / 2.62 |
  | S | 11.2 / 16.5 / 18.2 | 2.02 / 3.07 / 3.57 |
  | E | 9.9 / 13.3 / 18.1 | 2.93 / 4.27 / 5.18 |
  | W | 2.3 / 3.6 / 4.0 | unchanged |

- **Driver check** (existing v01 tool, unchanged) against current models: `FCX_DRIVER_CHECK_PASS`. This includes rest == idle phase 00 for all directions and rates, plus its own cache-vs-fresh RGBA oracle.
- **Whole-frame proof:** the v03 actual movies city EN 60 fps and annex room 2 ZH 30 fps are byte-identical AVIs to the v02 movies (`bd858c9f…`, `600c988f…`).

## Actual normal-scene benchmark (city EN, real host `_process` and action input, same v01 plan and capture)

`FRAME_PROCESS` is per-frame node process time, measured by first and last process-priority probes. It includes the host and the pilot step and excludes the capture code.

Important correction: `Performance.TIME_PROCESS`, the v02 "process_ms", is Godot's maximum over the last ~1 s, published once per second. It is not a per-frame value. It is still reported as `MONITOR(1s-max)` with the same capture overhead, which includes the per-frame `pilot.report()`.

Fixed 60 fps, no movie, two repetitions (a/b), p50/p95/max ms:

| Run | Cold FRAME_PROCESS | Warm FRAME_PROCESS | Monitor 1 s max p50/p95 | Driver step p95 cold/warm |
|---|---|---|---|---|
| off | 0.05 / 0.08–0.09 / 0.15–0.18 | 0.06 / 0.10–0.11 / 0.15–0.16 | 4.3 / 4.4–4.5 | – |
| frozen **INJECTED** | 0.14–0.19 / 13.9 / 17.8–19.8 | 0.11–0.14 / 10.7–11.0 / 14.9–16.1 | 16.8–17.5 / 19.6–21.1 | 13.8 / 10.6–10.9 |
| current | 0.14–0.17 / 3.1–3.5 / 5.2–5.7 | 0.11–0.14 / 2.6–2.8 / 4.0–4.4 | 7.7–8.3 / 8.3–8.4 | 3.1–3.4 / 2.6–2.7 |

- Cold means a fresh process with an empty driver cache. Warm means the second play of the plan in the same scene.
- Real time (no fixed fps; this machine presents at about 240 Hz): current frame dt p95 is 4.5 ms and warm max 8.3 ms. Frozen dt p95 is 13.3 ms cold. One 133 ms frame at scene entry appears in all three runs, flag-off included.
- INJECTED = benchmark-only test package in `user://fcx3-inj/` whose four model scripts are the frozen copies. All asset entries and hash checks are the real package's. **This is not root combined normal-CLI acceptance.**
- Startup: model construction E 3.7→7.8 ms, N 5.6→16.1 ms, W same, S setup + first compose 100.9→86.9 ms. Driver-check whole-set load was 355 ms (v02 run 267 ms). These are separate runs and the difference is not fully attributed.
- Memory: lookup tables cost about +0.55 MB E, +0.88 MB N and +0.52 MB S of static memory. After attach the scene is 32.5 MB current vs 30.7 MB frozen.
- Allocations: Godot exposes no per-call allocation count. Per-pass object-count deltas are identical, frozen vs current (658 cold, 202 warm). Images are now made from buffers instead of being written texel by texel.
- Driver cache (driver scope, unchanged): 290 entries / about 24.9 MB after cold; about 65 MB estimated in the 240 Hz real-time run, where the 192-per-direction cap fell back to live updates.

**Conclusion:** the current models put the pilot's per-frame cost (p95 about 3.5 ms, max ≤ 5.7 ms) well inside a 16.7 ms frame in this scene on this machine. That is measured headroom, not a 60 fps readiness or export claim.

## Movies (actual 1x, current models)

- City bright EN 60 fps: mean Y 86/255.
- Annex room 2 ZH 30 fps: mean Y **67/255**, so it is **not truly dark**. This answers the v02 open question.
- Ruins ZH 30 fps: mean Y 133/255.
- No normal scene is truly dark, so `annex-r2-zh-30fps-testonly-dim030` adds a clearly labeled **TEST-ONLY** CanvasModulate 0.30 on the world canvas (UI layers unaffected): mean Y 26.8/255. It is a capture condition, not a game scene or art.
- MP4s sit alongside the AVIs. The contact strips are `city-en-contact-strip` and `annex-zh-dim-contact-strip`.

## Not done / limits

- **Export:** no export templates are installed, so there is no export or PCK claim.
- **WEST:** not optimized.
- **Out of scope** (DeepSeek/root): driver cache growth and per-frame `cache_bytes()` iteration in `report()`, package re-binding, and builder regeneration.
- **Lighting:** the dark-scene requirement is met only by the labeled test-only dim.
- **Approval:** no art, motion, approval, default or scoring change.

## Files

- Tools (`tools/*fcx3a1b7*`): rgba8 probe, render oracle, south stage profile, actual-scene bench, hash-receipt builder.
- Evidence: `outputs/fcx-v03/`. The receipt `hash-receipt_v03_…json` covers the frozen and optimized models, the tools and every evidence file, and runs scope checks. `failed-parse/` holds the first bench attempt (GDScript type-inference parse error, kept). `superseded-monitor-only/` holds the runs made before the per-frame probe.
