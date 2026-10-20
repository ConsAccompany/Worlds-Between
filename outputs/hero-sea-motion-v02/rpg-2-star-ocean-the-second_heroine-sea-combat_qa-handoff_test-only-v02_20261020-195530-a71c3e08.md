# Heroine Sea of Stars combat motion v02: handoff (TEST-ONLY, UNAPPROVED, PARTIAL task)

## Task status

- **Task:** `content.combat.protagonist-female.combat-actions`. Owner: Claude.
- **Base:** `99bf35a`, worktree `work/dual05/cl-motion`. Nothing is staged or committed. No game, default, ledger, index, provider or Site changes.
- **Auth:** checked at session start. claude.ai / firstParty, `ANTHROPIC_API_KEY` absent.

**State:** source poses now exist for all 8 actions. Idle and attack are in v01 (frozen); move, guard, dodge, hit, skill and down are in v02. The parent task stays **IN_PROGRESS**:
- there is no loader;
- there is no gameplay playback evidence for v02 (root does the actual capture);
- the Pixelorama native export has not been run on v02;
- there is no creator approval.

## Source binding

**v02 author**
- File: `tools/rpg-2-star-ocean-the-second_heroine-sea_combat-motion-author_test-only-v02_20261020-193906-4c7e2a90.py`.
- sha256 `d04ab3fb985fc8be5f44657f15d61520e536ab0c6ae7058b82ebbdf5c23f88d2`. Raw bytes and text-LF are the same because the file is LF.
- It **imports** the frozen v01 author read-only. The v01 author is pinned at sha256-text-lf `b5d0926c…64cc` and v02 asserts that hash.

**v01 is untouched:** for example, the atk-antic-a PNG is still `b214e6d5…`.

**Approved still:** sha `4ce65a79…d5e6`, read-only. Every gate verifies it.

**v02 outputs (all in this folder):**
- Manifest `…manifest_test-only-v02_20261020-193906-15478d2e.json`, sha256 `b6d8a14e…5151`.
- Check report `…check-report_test-only-v02_20261020-193906-385785c4.json`, sha256 `e8cd3aa3…27e1`.
- For each of the 18 poses: a separate `native136` PNG, an `inspect-x4` PNG, an `editable` PXO and a `layered` ORA. That makes 72 pose files, with no sheets or grids.
- The hashes of all 72 pose files are in the manifest under `files`.

## Commands

Run from the worktree root. `PY` is the runtime Python and `PYTHONUTF8=1` is set.

```
PYTHONHASHSEED=1  PY -I <v02 author> build   # HSM02 BUILD PASS 147/147
PYTHONHASHSEED=99 PY -I <v02 author> check   # HSM02 CHECK PASS 224/224
```

## Actions and timing

All timings are whole 1/30 s ticks.

| Action | Poses (ticks) | Total | Arena limit |
|---|---|---|---|
| move (loop) | move-a 3, move-b 3, move-c 3, move-d 3 | 400 ms | phase .11 s loop |
| guard | enter guard-a 2; loop guard-b 6, guard-c 6 | 67 + 400 ms | phase .18 s loop |
| dodge | dodge-a 4 (airborne, soles at row 131/130), dodge-b 4 (crouched landing) | 267 ms, then base | dodge_time .27 |
| hit | hit-a 4 (recoil, blade flung back), hit-b 3 | 233 ms, then base | .24 |
| skill | skill-tel-a 4, skill-tel-b 3 (teal charge glints), skill-strike 1 (teal crescent, front foot steps +4), skill-contact 2, skill-recover 3 | 433 ms, then base | .45 |
| down | down-a 3, down-b 3 (overshoot, body +11), down-c 3 (settle, body +9) | 300 ms, last pose held | .30 held |

- **Skill contact:** the staged skill contact starts at 267 ms.
- **Attack (v01):** contact at 166.667 ms, while the current mechanics apply damage at the press. Hit synchronisation is **not** achieved or claimed for either skill or attack.

## Checks (224/224)

**Per pose:**
- binary alpha
- every colour from the still's 30-colour palette
- margins clear: columns 0 and 135 and rows 136..143 are transparent
- boots byte-exact at the declared whole-texel foot offsets, except texels covered by the arm, weapon or fx layers in front
- lowest row equals the declared sole row
- face texels (head rows 18..41) exact at the body offset
- no new pinhole of 4 texels or fewer
- layer stack equals the PNG, and the ORA merged image equals the PNG
- PXO cels equal the ORA layers
- bytes on disk equal the rebuild

**Global:**
- every v02 pose PNG is unique and differs from the base and every v01 pose
- each pose belongs to exactly one action
- every duration is whole ticks
- clips fit the arena durations
- skill has a 2-pose telegraph, then contact, then recovery
- down overshoots and then settles
- hit, dodge and skill end on the base
- the rebuild is deterministic; a seed-99 check passed against a seed-1 build

**Pivot and size:** no pose needed bounds larger than 136x144. The pivot stays (64,136) native = (32,68) logical in every pose. Foot moves are declared per pose (`soleRow`, `inCellRootOffset`).

**Gates loosened this session (disclosed):**
- **Boot check:** it now ignores boot texels covered by the arm, weapon or fx layers in front. The lowered down-b/down-c blade passes over a boot.
- **Hole check:** enclosed pockets larger than 4 texels (negative space between the blade or arm and the body, or the ponytail and the head) are no longer failures. They are listed for visual review under `newNegativeSpacePockets` in the check report.

## Method

Same rig as v01:
- **Upper body:** rigid, moved by whole texels.
- **Ponytail:** lags behind the head.
- **Legs:** RotSprite re-pose of thigh and shin, with painted hip and knee joint copies.
- **Sword arm:** painted per pose, with the still's fist and blade rotated about the grip.

New in v02:
- **Feet:** they move by whole texels (move, dodge, skill step).
- **Deep crouches:** dodge landing, skill and down take the knee from two-bone IK.
- **Weapon outline:** the blade gets `#151728` outline repair after rotation, which fixes the broken guard/tip outline from v01.
- **Skill fx:** teal glints and a teal-edged crescent, all palette colours.

## Not run / open

- **Pixelorama:** the v02 native export and the clean-application diagnostic were **not run**. Do not claim exact native export for v02. A single representative run is enough. The application gate is expected to fail with the same shader, leak and ORA errors as v01, which was 0/32 clean.
- **Movie:** no movie or gameplay capture was made.

## Visual limits

**Whole set:**
- The torso and head never rotate or lean, so dodge, hit and down read as a translated upright body over re-posed legs. Weight transfer is limited.
- Down is a slumped crouch with the blade lowered, not a kneel or fall. Kneeling would need boot rotation and new anatomy.

**Individual actions:**
- The skill strike crescent sweeps under and in front of the body (a rising slash), so it is visually heavy.
- The move cycle is a 4-pose shuffle and has not been checked at speed.
- Dodge-a airborne lift is only 4–5 texels.

**Carried over from v01:**
- The sleeve texture still changes between the still's arm and the painted arm.
- Ponytail and scarf secondary motion is minimal.

**Not proven:** fluidity, hit synchronisation, complete anatomy, and any loader or runtime playback.
