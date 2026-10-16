# Female protagonist battle static v06/v07: party-capture clean-clone repair (QA note)

Status: reproducibility repair only, not an art approval. v06 and v07 stay UNAPPROVED, test-only and non-runtime. No change to game/scripts, game/scenes or game/data. `game/scripts/battle_arena.gd` was not edited or staged; its working-tree sha256 stayed `be8859a8…a592acae` before and after. The approved 0.65 battle display proportion is preserved (crown-to-sole 61.0 logical px). Sprites stay **0/52** and the meter stays **35.0%**. This worker recorded no closeout and made no Git commit or stage; the root/sync worker owns that.

## Problem

The committed v06/v07 capture scripts:
- `tools/…native-0p65-party-capture_unapproved-v06_20261016-065106-08846793.gd`
- `tools/…native-0p65-party-capture_unapproved-v07_20261016-070549-33eb7e74.gd`

Both set `battle.arena_override` and read `arena.ARENA_FLOOR_Y`. Neither exists in the committed `battle_arena.gd`; only another workstream's uncommitted edit adds them. In a clean clone at `2b47e0a`, both scripts print:

`SCRIPT ERROR: Invalid assignment of property or key 'arena_override' with value of type 'String' on a base object of type 'Node2D (battle_arena.gd)'.`

Godot then never quits, so both runs hit the 120 s / 60 s `timeout` and exit with code 124. That is **0/2 runs**: v07 ruins and v06 outskirts were each tried once.

There is a second gap behind the first, and no change under `tools/` can close it:
- The ruins/outskirts band PNGs (`game/assets/environments/…scifi-{ruins,outskirts,city-terrace,archive}-battle-arena_runtime-band_m8-candidate_20261014-213622-14315e18.png`) are **untracked** and absent from all Git history.
- The band, contact-shadow and sentry-pilot drawing code exists only in the uncommitted `battle_arena.gd` (Set 3C, which needs user approval).

So a clean clone cannot render ruins or outskirts backdrops at all.

## Fix (one new test-only file under tools/)

`tools/rpg-2-star-ocean-the-second_protagonist-female_sideview-battle-idle-right-native-0p65-party-capture-clean-clone_unapproved-v07r1_20261016-085133-1c89279f.gd` (sha256 `2498b627927c141b61554ea3d538ea2ec7cdcd4100347efc20063394dc9830be`, LF, the same with or without CR stripping)

This is the v07 capture script with three changes. The committed v06/v07 scripts are left as they are. The method, gates and measurement code are the same, and one script serves both v06 and v07.

1. **`arena_override` only when declared.** It is set with `set()`, and only if the scene's property list has `arena_override`.
   - If so, the run is `arenaMode: "arena-override-band"`. It behaves exactly like the old scripts, including the `arena_id == arg5` gate.
   - If not, the run is `arenaMode: "head-geometric-backdrop"`. The arena argument must be a known id; the gate becomes "no `arena_texture`"; HEAD's own backdrop is drawn; and no contact shadow is drawn, matching the runtime, which draws none without a band.
2. **Local `FLOOR_Y := 272.0`** replaces `arena.ARENA_FLOOR_Y`. That is HEAD's hard-coded floor, and the band build's constant has the same value.
3. **More manifest fields:** `requestedArena`, `arenaMode`, `arenaBandDrawn` and `battleArenaScriptSha256Bytes`. The `method`/`subject` text now names the mode. The test save root is `user://test-saves/m8-female-sideview-native-0p65-capture-r1`.

## Reproduction (Git Bash; Godot 4.7.2 windowed, not `--headless`)

```bash
# clean clone (short temp root; core.longpaths), then a one-time import (a fresh clone has no .godot cache)
git -c core.longpaths=true clone <repo> /c/Users/hkzha/AppData/Local/Temp/wbC && cd /c/Users/hkzha/AppData/Local/Temp/wbC
G="<repo>/work/tooling/godot-4-7-2/Godot_v4.7.2-stable_win64_console.exe"   # gitignored local tool
"$G" --headless --path game --import
S=$(cygpath -m "$PWD/tools/rpg-2-star-ocean-the-second_protagonist-female_sideview-battle-idle-right-native-0p65-party-capture-clean-clone_unapproved-v07r1_20261016-085133-1c89279f.gd")
P=$(cygpath -m "$PWD/game/assets/characters/combat-sideview-pilots/rpg-2-star-ocean-the-second_protagonist-female_sideview-idle-right-static-native0p65_unapproved-v07_20261016-070549-6711a51d.png")
H=$(sha256sum "$P" | cut -d' ' -f1)
"$G" --path game -s "$S" -- "$P" "$H" <out.png> <out.json> ruins <out-nosprite.png>   # or: outskirts
```

For v06, use `…unapproved-v06_20261016-065106-a1d82e3a.png`. Pass `cygpath -m` paths: a backslash path makes Git Bash's `sha256sum` print a `\`-prefixed hash.

## Results: 8/8 runs PASS (2×2 per tree)

| Tree | Mode | v06 ruins | v06 outskirts | v07 ruins | v07 outskirts |
|---|---|---|---|---|---|
| Working tree (dirty `battle_arena.gd` `be8859a8…`, untracked bands present) | arena-override-band | `6480d90b…814815ca` = committed | `9e5aa2ae…89d6d82f` = committed | `56d7b103…c219d82c` = committed | `8a83a283…62e89333` = committed |
| Clean clone at `2b47e0a` + only the r1 script (`game/` content == HEAD) | head-geometric-backdrop | `6de95406…a62a253d` | identical to ruins | `3824d76b…96d076d1` | identical to ruins |

Full working-tree hashes:
- v06 ruins `6480d90b3fea0e85752034a0db0a33680b4c446e91011d9b3da27d05814815ca`
- v06 outskirts `9e5aa2aeff2aff6695ad4de36b710549d10f87d224b25a5127b9c78789d6d82f`
- v07 ruins `56d7b1033452e5cdecb5b8ea73160faa84a4f60f83efda04158c22e8c219d82c`
- v07 outskirts `8a83a28352cb7b026dbd8d276695d65e105e845528e04ddc6895f43e62e89333`

All four are **byte-identical** to the committed captures `…party-capture-{ruins,outskirts}_unapproved-v0{6,7}_…png`, so with a band-capable scene the r1 script reproduces the stored evidence exactly.

Every run printed `CAPTURE PASS`, exited 0 and had 0 script errors. All 8 runs agree on:
- sprite px 5428/5428 (v06) and 5380/5380 (v07); prediction ratio 1.0; 0 off-palette pixels;
- integer 2×2 texels (39 columns and 67 rows, all 2 px);
- crown y 422, sole y 543, crown-to-sole **61.0 logical** (the approved 0.65 proportion);
- gap to Liang Xu 10 screen px; 0 overlap with all three companions;
- the same companion used-rects.

A Pillow cross-check found that the sprite mask pixels are **bit-identical** between the two modes (5428/5428 and 5380/5380 at the same screen coordinates). Only the background differs.

In head mode, ruins and outskirts give identical bytes. Their no-sprite frame is `d9b2a0e1…61051f36` in both. That is expected: HEAD has no band art and does not vary the backdrop by destination.

## New evidence outputs (separate images; the clean clone wrote them directly)

| File (`outputs/`) | sha256 |
|---|---|
| `rpg-2-star-ocean-the-second_protagonist-female_battle-static-v06_party-capture-head-backdrop-clean-clone_unapproved-v07r1_20261016-085133-9d9c096f.png` | `6de954064d23f3e4bd7ba74422e81cf208ade47bc3cd767d0e16d1dda62a253d` |
| `…battle-static-v06_party-capture-head-backdrop-clean-clone-manifest_unapproved-v07r1_20261016-085133-da5d1cb3.json` | `b4d97047e3c605d1e82cfef3690f11ed6c52c59f339b4b8156dcebf862448c17` |
| `rpg-2-star-ocean-the-second_protagonist-female_battle-static-v07_party-capture-head-backdrop-clean-clone_unapproved-v07r1_20261016-085133-627c4e5a.png` | `3824d76bb3813d8ef9512c1880a583e4ccb1b8c8127fef99450e000096d076d1` |
| `…battle-static-v07_party-capture-head-backdrop-clean-clone-manifest_unapproved-v07r1_20261016-085133-eb02baf2.json` | `5b1a7450acb6531632ad5be615d37788607d42afa4505f104b37256d09b8d4ca` |

These were captured with `ruins` requested. The outskirts request gives the same bytes, so it is not stored twice. These images show the HEAD geometric sentry backdrop with the placeholder enemy block. They are **not** ruins/outskirts art reviews. The real ruins/outskirts images are the committed v06/v07 captures, which this run reproduced byte for byte. The manifests' `candidatePng` paths point into the temp clone. `battleArenaScriptSha256Bytes` there is `918dcdad…` (the CRLF checkout, `core.autocrlf=true`); the HEAD blob's LF hash is `e9737c40…5f859f02`.

## Dependency closure (r1 script, head mode)

**Tracked at HEAD, and present in the clone:**
- `game/project.godot` (autoloads AppState, SaveStore)
- `res://scenes/battle_arena.tscn` and `res://scripts/battle_arena.gd`, with its preloaded companion frame scripts and textures
- the v06/v07 candidate PNGs
- the r1 script itself (new and untracked until synced)

**Not tracked:**
- Godot 4.7.2 (`work/tooling/…`, gitignored)
- the one-time `--import` cache (`game/.godot`)

**Band mode only:** the uncommitted `battle_arena.gd` plus the 4 untracked band PNGs (plus `.import`).

**Side effects:**
- Main working tree: the `git status --porcelain` diff before and after shows this task's new files (the tool, four outputs and this note). It also shows `game/assets/environments/candidates/wdc-cw-v06_20261016-071733-18b9cea3/`, which another session created meanwhile. Godot added no `.uid` or `.import` files. Nothing is staged.
- Clone: the capture runs changed nothing. The earlier `--import` there wrote `.import`/`.uid` files, which is expected in a throwaway clone. The temp clone was deleted after the runs.

## Remaining limitations

- A clean clone **cannot** make real ruins/outskirts captures until the root/sync owner, with user approval (Set 3C), syncs both the arena band code in `battle_arena.gd` and the band PNGs. After that sync, the same r1 command switches to band mode on its own, and should match the committed captures byte for byte.
- Head-mode images are not comparable with band-mode ones for floor value contrast (|ΔL|). The v07 region-measure figures stay band-only and working-tree-only.
- If the scene fails, the old v06/v07 scripts still hang until timeout; keep a `timeout` wrapper. The r1 script fails fast for an unknown arena id, but a GDScript runtime error still stalls the run.
- The r1 script is untracked. The selective-sync worker should consider: the r1 tool, these four outputs and this note. Not included: the cross-check helper or the temp matrix files under `%TEMP%\wbCout`.
