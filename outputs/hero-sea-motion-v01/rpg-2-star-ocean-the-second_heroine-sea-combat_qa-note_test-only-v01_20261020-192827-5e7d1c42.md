# Heroine Sea of Stars combat motion pilot v01: QA note (TEST-ONLY, UNAPPROVED)

- **Task:** `content.combat.protagonist-female.combat-actions`. This partial pilot covers 2 of the 8 actions (idle and short-blade attack), so the task stays **IN_PROGRESS**.
- **Owner:** Claude.
- **Base and tested revision:** `99bf35a` (worktree `work/dual05/cl-motion`). Nothing is staged or committed.
- **Unchanged:** game sources, defaults, camera, party positions, ledger, registry, Bible and index.
- **Movie/capture:** none is claimed here. DeepSeek owns it in `work/dual05/cx-combined`. No movie harness from this session exists or is claimed.

## Source binding

| Item | Value |
|---|---|
| Approved base still (read only, never rewritten) | `outputs/hero-sea-v01/…still-native136_sea-unapproved-v01_20261020-181955-1294c865.png`, sha256 `4ce65a7915c0c0270a4ca353152b45b7d68b42672cb1483dd4f3e9cf4ac9d5e6` |
| Author tool | `tools/rpg-2-star-ocean-the-second_heroine-sea_combat-motion-author_test-only-v01_20261020-192028-9bab493d.py`. Raw bytes sha256 and sha256-text-lf-v1 (CRLF→LF only) are both `b5d0926c75bdd5da27299fec18f5293da8c68e6ae51e5956cfa5395ec41d64cc` (the file is LF). |
| Manifest | `…combat_manifest_test-only-v01_20261020-192028-7e93a93c.json`, sha256 `a012cc3d42c4b81f6c73cdc984ccb10f15d37fcb73b2c06938a01595be790657` |
| Check report | `…combat_check-report_test-only-v01_20261020-192028-6bd34355.json`, sha256 `0e8922909cbc5b325f74865ae7c8fd2bcac7101f7423c7c61ec383093f3a4b86` |
| Pixelorama native report | `…combat_pixelorama-native-report_test-only-v01_20261020-192028-8b01666e.json`, sha256 `8b826ef1b4f68071ba938e541401ef3050ee2736303d293684a165d5fa6f2d02` |

The PNG/PXO/ORA hashes for each pose are listed under `files` in the manifest. The native pose PNGs are:

| Pose | sha256 |
|---|---|
| idle-b1 | `68726810…` |
| idle-b2 | `035978c5…` |
| atk-antic-a | `b214e6d5…` |
| atk-antic-b | `dc0b99c8…` |
| atk-smear | `cfa9098e…` |
| atk-contact | `d095cb7e…` |
| atk-follow | `a83b10a0…` |
| atk-recover | `18d051f5…` |

Each pose also has its own separate x4 inspection PNG (flat grey, viewing only). There are no contact sheets.

## Commands

All run from the worktree root, with Python at `C:\Users\hkzha\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe` (`PY` below) and `PYTHONUTF8=1`. `T` is the author tool path.

```
PYTHONHASHSEED=1 PY -I T build    # HSM01 BUILD PASS 86/86
PYTHONHASHSEED=7 PY -I T check    # HSM01 CHECK PASS 119/119
PYTHONHASHSEED=12345 PY -I T check    # HSM01 CHECK PASS 119/119 (Codex reran independently: 119/119)
PY -I T native                    # HSM01_NATIVE EXACT 32 / 32 DIAGNOSTICS 0 / 32
```

- **Hash-seed fix:** the first build differed across processes because a colour tie was broken by `set` order. The tie-break is now sorted, and the outputs were rebuilt before these runs.
- **Native run:** it finished in the previous session, before the coordinator deadline. Its report file is write-once (`x` mode), so it was not rerun.

## Results

### Check: 119/119 PASS

**Per pose:**
- 136x144 RGBA, binary alpha.
- Every colour is from the still's 30-colour palette.
- Columns 0 and 135 and rows 136..143 are transparent.
- Lowest row is 135, and both boots are byte-identical to the still (planted).
- The face (head texels in rows 18..41) is preserved exactly at the body offset.
- No enclosed hole outside the still's own pockets at that offset. Tiny new pockets of 4 texels or fewer are closed with outline in the `seams` layer.
- The layer stack equals the PNG.
- The ORA merged image equals the PNG.
- The PXO raw cels equal the ORA layers.
- In attack poses, the still's sword arm is removed and repainted.

**Timeline and package:**
- The attack ends on the approved base still.
- The attack is 400 ms, within the 0.43 s cooldown.
- Every duration is a whole 1/30 s tick, so 30 and 60 fps show the same poses.
- Hit sync is not claimed.
- The rebuild is deterministic.
- The bytes on disk equal the rebuild.

### Pixelorama 1.2.3 headless (fresh APPDATA/LOCALAPPDATA per run)

Executable sha256 `6412014e…f10`.

**Source equality: EXACT for all 32 runs.** This covers 8 poses × (PXO, ORA) × (split layers, flat). All exits were 0 and every source was left unchanged.

**Clean-application gate: FAILED, 0/32 clean.** Raw diagnostic lines across all runs (the per-run lines are in the native report):
- 128× `ERROR: Condition "!actions.custom_samplers.has(function->arguments[j].tex_builtin)" is true.`, the known shader diagnostic.
- ORA runs also show:
  - 48× `children_cache` index out-of-bounds ERROR
  - 16× each of:
    - `Required object "rp_node" is null`
    - `Must be an ancestor of the control`
    - `16 resources still in use at exit`
    - `9 RID allocations … leaked`
  - 16× WARNING `118 ObjectDB instances were leaked`

No GUI Save As or reopen was performed, and none is claimed.

## Timing (from the manifest)

| Clip | Frames (1/30 s ticks) | Length |
|---|---|---|
| Idle loop | base 8, b1 6, b2 8, b1 6 | 933.333 ms |
| Attack | antic-a 2, antic-b 2, smear 1, contact 2, follow 2, recover 2, settle (idle-b1) 1 | 400 ms, then the approved base still, byte-exact |

- **Contact:** the staged contact pose starts at **166.667 ms**.
- **Arena mechanics:** in the current game (`battle_arena.gd`, read only), `_try_attack` applies damage and the hit VFX **on the press frame**. The visual attack runs 0.39 s and the cooldown is 0.43 s. The pilot's contact therefore trails real damage by 166.667 ms. **Hit synchronisation is not achieved or claimed.**
- **Smallest later fix, opt-in only and not implemented:** add a default-off arena flag that makes `_try_attack` store a pending hit and apply damage and VFX at the pilot's contact time (0.1667 s, below the 0.43 s cooldown), with a range recheck.

## Method and limits (what this does and does not prove)

**How the poses are built:**
- **Head and torso:** one rigid whole-texel translation (body offsets up to (+4,+3)), so face pixels are exact. There is no rotation, scaling or blur.
- **Ponytail:** a separate lagging part over an anchored root copy.
- **Legs:** the thigh and shin bitmaps are re-posed with a RotSprite-style rotation (3× EPX upscale, nearest sample).
  - The knees are authored per pose. IK was abandoned because it was too sensitive on the nearly straight legs.
  - Thigh and shin lengths may stretch by less than 1.5 texels.
  - Hip and knee joint copies are painted underneath, and the boots never move.
- **Sword arm:** removed in attack poses. The jacket side it covered is painted in.
  - The sleeve, forearm and bracer are painted per pose as shaded capsules running shoulder → IK elbow → grip.
  - The still's fist and blade cluster is rotated about the grip.
  - A hard-edged smear crescent marks the swing.

**Layer limits:**
- Each per-pose source has 9 layers: seams, ponytail, leg-back, leg-front, torso, head, arm, weapon and fx.
- The torso and head layers are still slices of the flattened still, with painted underlay only at the sword-arm side, neck and joints. They are not complete painted anatomy behind every overlap.
- The rear arm, scarf tail and coat do not move independently.
- The rotated fist and blade show some broken outline texels at the guard and tip.
- The procedural sleeve and forearm differ in texture from the still's arm, so there is a style change when idle switches to attack.

**Not proven:**
- continuous normal-speed fluidity (no movie here)
- in-game rendering of these poses
- complete anatomy
- hit synchronisation
- the other states: move, guard, dodge, hit, skill and down

**Status:** automated gates are technical only. The motion is UNAPPROVED and needs Codex inspection, then creator review.
