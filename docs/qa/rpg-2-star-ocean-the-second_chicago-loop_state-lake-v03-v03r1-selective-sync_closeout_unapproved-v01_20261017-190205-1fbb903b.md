# Chicago State/Lake v03 + v03r1: exact-file selective sync, closeout

**Status: UNAPPROVED and opt-in only (off by default).** This sync puts the existing v03 and v03r1 candidates on GitHub so Codex and the creator can review them. It approves nothing:
- Chicago scene quality for this location stays 0;
- science scene visuals stay 3/12;
- MVP meter 40.8%, M2 10/12, character variants 0/52, post-art playtests 0/2.

Codex still judges the upper facade busy and muddy, and not all Chicago art is done. No art was changed in this sync.

Done by Claude Code (Opus 5.5) through signed-in Claude Max, firstParty. `ANTHROPIC_API_KEY` was absent and no paid fallback was used. No process was terminated, by name or by PID: every Godot and Python run exited on its own.

## What was synced

All paths were staged by exact name. Nothing from City Hall, Yonkers, the map, characters, battle, the Game Bible app/server or other sessions' ledger work is in this commit.

- **v03 and v03r1, each:**
  - 7 runtime PNGs and their `.import` files (`game/assets/environments/chicago-loop-state-lake-v03*/`);
  - the scene `.tscn`, the scene script, the opt-in selector, and the `.uid` files Godot wrote for both scripts;
  - the editable sources: Pixelorama `.pxo`, OpenRaster `.ora`, the merged preview, the walk-mask guide, the `.gpl` palette and the layer manifest;
  - the source-check report from the original build;
  - the author tool, the Godot capture check and the pixel/source check;
  - the QA note.
- **Review captures (minimal set), each version:** `zh-entry`, `en-entry`, `zh-approved-heroine-ref`, `en-approved-heroine-ref`, `en-default-off-v02-entry`, and the visible-hero counts JSON. The heroine-reference pair is what the v03r1 C3/C6/F1 gates compare against.
- **Generated reference:** `outputs/…chicago-state-lake_style-alignment-reference_nonruntime-v01_20261017-173900-4c6e2b91.png` (sha256 `7608a64f…`). It is NONRUNTIME, Codex-generated continuous-colour art, and is never shown in the game. Both author tools read it (hash-pinned) for the disclosed 20% backdrop underpainting, so a clean checkout cannot rebuild v03/v03r1 without it. The first clean-checkout run failed for exactly that reason, so it was added (as with v02's committed reference).
- **Tracked edits (two):**
  - the runtime Loop `.tscn`: its one script `path=` now names the v03r1 selector (the same line the v03r1 pass changed locally);
  - the v02 pixel/source check: the G3 test-expectation repair below.

## Test-expectation repair (G3)

The v02 and v03 source checks string-matched their own script name in the Loop `.tscn`. Once a selector legitimately routes all versions, those were false failures.

- **v02 check, `G3_runtime_scene_wired_to_v02`:** now follows the Loop scene's script up its `extends "res://…"` chain. It passes only if the v02 script is on that chain and every selector above it has the `super()` fall-through used when its flag is off. The chain is written to the report (`runtime_scene_script_chain`).
- **v03 check, `runtime_scene_uses_selector`:** passes if the Loop names the v03 selector, or names a later selector that:
  - extends the v02 script;
  - preloads the v03 selector;
  - delegates to its `v03_enabled()` rule and `V03_SCENE`;
  - has the `super()` fall-through.

Every other part of G3 is unchanged: the selector→v03 scene→v03 script wiring, the v02 baseline hashes and the v02 git-clean check. The route, render and source checks are untouched, and the Godot captures (below) prove the behaviour.

**Still failing on purpose:** v03 `C3_plaza_denser_in_foliage_teal_and_lit_stone_than_v02`. Lit plaza stone is 25.43% against v02's 28.95%. This is an art-only result for the old v03 ground, unrelated to wiring. It was the reason for v03r1, which passes the same gate verbatim at 33.21%. v03 is kept as the unchanged baseline, so its art is not edited to pass.

## Clean-checkout verification

The exact staged tree was exported to a throwaway clone under `%LOCALAPPDATA%\Temp` (`core.autocrlf=true`, `core.longpaths=true`), with HEAD set to a temporary commit of that tree. Godot 4.7.2: `--headless --import` (exit 0, no errors), then windowed capture checks with a fresh stamp `20261017-185649-13ae82ed`.

| Run | Result |
|---|---|
| Default, no flag (v02 capture check on the runtime Loop scene) | `CHICAGO_LOOP_V02_OK checks=42 … runtime_scene=true` |
| `-- --chicago-state-lake-v03` (v03 capture check) | `CHICAGO_LOOP_V03_OK checks=72` |
| `-- --chicago-state-lake-v03r1` (v03r1 capture check) | `CHICAGO_LOOP_V03R1_OK checks=74` |
| Fresh renders vs original captures | v02 8/8, v03 17/17, v03r1 17/17 at **0 px different**; counts JSONs equal except the stamp |
| v02 pixel/source check (`--capture-stamp 20261017-162405-1bdb3cd5`) | **13/13** (was 12/13, G3 only) |
| v03 pixel/source check (fresh stamp) | **14/15**: only C3 fails, as explained above (was 13/15) |
| v03r1 pixel/source check (fresh stamp) | **18/18**, Pixelorama 1.2.3 CLI P1/P2 included |

The three Godot runs used the tree before the generated reference was added. That tree differs only by that nonruntime PNG, and the Godot runs never read it. The source checks ran on the final tree.

Shared headless smokes in the same clone, all exit 0:
- `US_SCIENCE_MIGRATION_SMOKE_OK checks=32`
- `M2_SMOKE_OK`
- `M7_SMOKE_OK`
- `GLOBAL_TRAVEL_CORE_OK`
- `M2_WHOLE_HOUR_TRAVEL_OK checks=246`
- `EXPORT_DATA_INCLUSION_SMOKE_OK mode=source checks=24`
- `GLOBAL_EARTH_MAP_SMOKE_OK checks=212`
- `GLOBAL_MAP_TRAVEL_INTEGRATION_OK checks=111`

The v03r1 note's 114 came from the shared worktree, which has another session's uncommitted map edits. 111 is the committed figure.

## Unresolved aesthetic defects (unchanged by this sync)

- The upper facade band (rows 62–94) is still busy and muddy. It is generator-derived underpainting, 20.16% of the visible frame; a real fix means redrawing it by hand.
- The largest single colour is 8.07% (`pv3` slab interiors); slab fills read flat.
- v02 still has the more painterly texture.
- The stair, medallion and fountain are invented. The kiosk and dock are small. The reveal dither may look noisy in motion.
- The kiosk, stair and pylon note wording (zh/en) is unreviewed.

## Captures kept local (hash-pinned, sha256 of bytes)

These 24 real Godot captures complete each 17-tag set but are not in the commit. A clean checkout regenerates them with the capture checks above; the fresh renders matched these bytes at 0 px.

| Capture | sha256 |
|---|---|
| `en-interact-kiosk-640x360_v03_20261017-182019-3e3c762e.png` | `a15f6018015e6f6032e58bff2627afe57cb8114e760983714c855301b59fef7f` |
| `en-interact-pylon-640x360_v03_20261017-182019-3e3c762e.png` | `0023a93e43dd8ed32262e0a4aad39fbf8aad98937f5dc8cb16ef8325f00f527f` |
| `en-interact-stair-640x360_v03_20261017-182019-3e3c762e.png` | `cc80cc3b471cecfb69a3e06e35b96c8314f471827f2731b36d3bf6df88631265` |
| `en-occlusion-column-reveal-640x360_v03_20261017-182019-3e3c762e.png` | `93f32fff61d0c362c56c6277f10b81d5e54a973412b72fc2f04aa1b44667e3e6` |
| `en-traverse-crosswalk-640x360_v03_20261017-182019-3e3c762e.png` | `6742c17b5624605d80ec8bd886b85afffeef6a0598aa51fee872020ab745cd61` |
| `zh-interact-kiosk-640x360_v03_20261017-182019-3e3c762e.png` | `9fb07509fd33b2fce528121e411161dec7eebbdaeb5f6baf7befb8b2a3195de8` |
| `zh-interact-pylon-640x360_v03_20261017-182019-3e3c762e.png` | `d6bb767a9b3fba0c0ff5404c928ac53bcc344806e77b940ece4ae4b201d1b2c7` |
| `zh-interact-stair-640x360_v03_20261017-182019-3e3c762e.png` | `fecf5bbafef0a5f0c87ddbbd3dc5517f3399fcb32894fda8c93b9c98e3223869` |
| `zh-occlusion-column-raw-640x360_v03_20261017-182019-3e3c762e.png` | `6b3f523b56df7363fc5aadf67d837f3c06c8aedf2639ef3ae11724aa92d6ed7c` |
| `zh-occlusion-honey-locust-640x360_v03_20261017-182019-3e3c762e.png` | `71a04d8c3f00c3b57a9985fb24be60acb40db633d64ee10228357940b584ffc9` |
| `zh-traverse-stair-foot-640x360_v03_20261017-182019-3e3c762e.png` | `5f7dc7e3c8b00de5565f757e9d27c4ce1c9824fcbc03d06d319864fdfe8f4dba` |
| `zh-traverse-under-l-lane-640x360_v03_20261017-182019-3e3c762e.png` | `b38122f4b8040bb6cff5314521792524cc51b6878ec8f4f083397907d8e2549f` |
| `en-interact-kiosk-640x360_v03r1_20261017-184340-44bc6d7f.png` | `f552b1865c3c9fd6ee6f69c15c7eb679b720b0f868beb75105a42ba5e89a82a4` |
| `en-interact-pylon-640x360_v03r1_20261017-184340-44bc6d7f.png` | `1a7f9b798f70a47d7304bdc069c34835f7c4042d87945706cd6295d6626e6ba1` |
| `en-interact-stair-640x360_v03r1_20261017-184340-44bc6d7f.png` | `90c0eb98c3e5f187d5693d69a8f16332b6e381592deda75f6bc72c0afe7e8d96` |
| `en-occlusion-column-reveal-640x360_v03r1_20261017-184340-44bc6d7f.png` | `cdc0e559142582de6d3d5393311574a3cc535f35a44c282f8ea839c70def6704` |
| `en-traverse-crosswalk-640x360_v03r1_20261017-184340-44bc6d7f.png` | `405013219581386eabc4bb2410b2c3a04c48a81154fd77b19d59d9562abc94db` |
| `zh-interact-kiosk-640x360_v03r1_20261017-184340-44bc6d7f.png` | `c49b75018a3ba03aa2cb0df2070fc79bae6a6bb9ca565c91466438fef084e72c` |
| `zh-interact-pylon-640x360_v03r1_20261017-184340-44bc6d7f.png` | `682315470c443fc7a815379752b58a44dd3115d5aa3bb3b62109a06768a13b7a` |
| `zh-interact-stair-640x360_v03r1_20261017-184340-44bc6d7f.png` | `040a476051f3266c7b64dc5ece1691f4e53f207b1cbfd49f26ffa6972e5bdef6` |
| `zh-occlusion-column-raw-640x360_v03r1_20261017-184340-44bc6d7f.png` | `5b36b7aba9f66398b7f0e5471c6850b107cdea2598c5e261f7ba9585654fac24` |
| `zh-occlusion-honey-locust-640x360_v03r1_20261017-184340-44bc6d7f.png` | `663b7f13a3dc6e61dc2c915c27b13354c48c4d86ea3d7972007cdc42f57b0395` |
| `zh-traverse-stair-foot-640x360_v03r1_20261017-184340-44bc6d7f.png` | `f449f20d5bbd910d8383d115251925a14a1bb435f7a86e5f34b9dd1152e555d5` |
| `zh-traverse-under-l-lane-640x360_v03r1_20261017-184340-44bc6d7f.png` | `094e6a9d8ab999444b65ad41f1846fdc41710122183ae52141e99cce2bc1937f` |
