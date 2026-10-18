# Chicago State/Lake v05 and battle heroine STATIC v13: isolated 7370739 integration verification (QA note, UNAPPROVED)

Date: 2026-10-18 04:16 local. Prepared by Claude Code (Opus 5.5). `claude auth status` reports claude.ai / firstParty / max, and no quota or auth limit was hit.

This is integration preparation only. Nothing is committed or pushed. Root Codex visually inspected v05 and v13 and accepts their technical evidence only; **both arts remain UNAPPROVED.**

Counters are unchanged:
- meter 40.8%;
- M2 10/12;
- scenes 3/12;
- sprites 0/52;
- playtests 0/2;
- formal acceptance false.

## Base and overlay

- **Base:** upstream main `73707394745d928afc1033f73b3c03a2c78b92b0`. Upstream `game/` is identical to `c20118d`.
- **Integration tree:** `work/iv5v13`, a detached git worktree with its own index. The primary checkout and its index are untouched.
- **Overlay:** exactly 3 kinds of change:
  1. New files only, listed with sha256 in `outputs/rpg-2-star-ocean-the-second_chicago-v05-battle-v13_integration-selection-manifest_unapproved-v01_20261018-041551-66d3cb79.json`.
  2. **One** modified tracked line, owned by the Chicago candidates. The shared Loop `.tscn` script path changes from the v03r1 selector to the v04 selector.
     - This is the same hunk that the primary checkout holds unstaged.
     - The v04 selector extends v02 and routes `--chicago-state-lake-v04`, then v03r1, then v03. With no flag, the scene is still v02.
     - The v05 selector is reached only through the in-memory harness of its own check. Default play is unchanged.
  3. No hunk from `game/scripts/battle_arena.gd`. No hunk from the dirty Chicago placeholder script, whose working-tree diff is the old v01 code path and not v05.
- **Round 2 (2026-10-18, after root review)** adds:
  - the G3 r1 fix in the v05 source check;
  - the official WEB reopen supplement and identity proof for Yonkers v04;
  - the private Site v14 operational QA and its public-safe proof;
  - the ledger edit on the upstream progress JSON: 4 zero-change closeouts plus the v03r2 map-art text correction. All 119 existing closeouts are preserved.
- **Round 2 check.** The full v05 source check was re-run in a fresh mirror whose `git write-tree` equals this tree's round-2 index (`998962fc…`): 25/25, G3 r1 PASS. The report above is that run.

## Checks actually run from 7370739 + overlay

Path-length workaround: about 330 upstream files exceed MAX_PATH under `work/iv5v13`. So every check ran in a short-path **mirror** worktree, `%TEMP%\iv737`. The mirror was built by `git apply --index` of this tree's staged binary diff. Its `git write-tree` is **identical** to this tree's: `329eb7d51e033e1ca93a0f85d9049bc7d74a8818`, taken before these evidence files were added. Godot `--import` ran in the mirror only. Its import products (68 `.import`, 34 `.uid`) were not copied back.

| Check | Result |
|---|---|
| v05 Godot 4.7.2 capture check (windowed, `--chicago-state-lake-v05`) | `CHICAGO_LOOP_V05_OK checks=79`. All 19 fresh PNG captures are **byte-identical** to the delivered `…_v05_20261018-000240-1d1b9337.png` set. The visible-hero counts JSON is identical apart from CR/LF. |
| v05 pixel source check (official Pixelorama 1.2.3 CLI, temp APPDATA) | `CHICAGO_LOOP_V05_PIXEL_SOURCE_CHECK 25/25` (includes G3, R1, P1, P2). Report: `outputs/chicago-loop-state-lake-v05/…pixel-source-check-report_v05-isolated-7370739_20261018-041551-8bfab6cf.json` |
| v05 walk reachability | `CHICAGO_LOOP_V05_WALK_REACHABILITY 4/4`. 64225/64225 walkable px are reachable. |
| v13 author `check` (Pixelorama 1.2.3, APPDATA redirected to an empty temp dir) | `55/55 PASS`. Report: `outputs/…battle-static-v13_isolated-7370739-check-report_unapproved-v13_20261018-041551-d3789b8b.json` |
| v13 probe captures (Godot, windowed, `--resolution 640x360`) | archive (bright), outskirts (dark) and head-geometric each give `CAPTURE PASS` (1621/1621 px, 0 off-palette, nearest 1.0, self-check pass). All 3 PNGs are **byte-identical** to the delivered `0cc9f010` / `66527b60` / `3129b639`. |

- **Battle draw script.** The probe ran against the unmodified 7370739 `battle_arena.gd`. The capture manifests record its byte-hash as `918dcdad…`, the CRLF working copy. The LF hash is `e9737c40…`, which equals the 7370739 blob and the hash recorded in the v13 QA.
- **Floors.** The archive and outskirts floors were read from the two band PNGs **inside this tree**, with sha256 pins `c840e071…` and `feea6297…`. No input came from outside the tree, apart from the Godot and Pixelorama executables.
- **Tree side effects.** Running the checks changed nothing in the mirror tree: `git status` was identical before and after each run.

## Dependency completeness

- **Chicago v05 needs v04.** The v05 selector preloads the v04 selector, and R1 compares v05 with v04's manifest, `.ora` and author. The v04 runtime chain, its editable sources, its author tool and its two `approved-heroine-ref` captures (stamp `1f83552b`) are therefore included.
  - v04's own check tools, its other 17 PNG captures and its visible-hero counts JSON, its source-check report and its comparison image are **not** included. v04's own source check (C5) would therefore not be complete from this tree. v05's checks are.
  - **Limited scope, not a release claim.** v04 is synced only as v05's runtime and comparison dependency. No standalone v04 checker completeness is claimed. v04 stays UNAPPROVED, reachable only via `--chicago-state-lake-v04`.
- **Already in 7370739:** the v02, v03 and v03r1 chains, plus the v02 and v03r1 reference captures.
- **Battle v13:**
  - v12 is tracked at 7370739 and its lock passes.
  - The two references, the v8 south static and the character sheet, are tracked.
  - The v13 dispatch, which the manifest cites, is included.
  - Following the tracked convention for sprite pilots, the v13 PNG has no `.import`.
  - The band PNGs keep their existing `.import` sidecars. Without them, Godot would regenerate the sidecars as untracked files.

## Known caveats

- **G3 fixed (r1, 2026-10-18).** The first draft of this note flagged that the old v05 G3 required the Loop `.tscn` to differ from HEAD, so it would fail once the line was committed.
  - The source check's G3 now validates the exact allowed Loop scene (v04 selector only), the pinned v04 selector (flag, override −1, v02 fall-through) and the v05 routes, whatever HEAD holds.
  - A throwaway mutation test passes 11/11.
  - It is the only tool that changed. See the addendum in the v05 QA note.
- **Excluded from this selection:**
  - the two v04-over-v05 comparison composites (derived, combined images);
  - session logs;
  - other band PNGs (ruins, city-terrace);
  - all Washington, Site, progress and Bible files;
  - root's in-progress Yonkers reopen-retry files that appeared at 04:04–04:05 (file times), during this session.
