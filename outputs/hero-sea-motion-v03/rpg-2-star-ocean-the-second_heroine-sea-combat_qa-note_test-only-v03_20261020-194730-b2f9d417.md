# Heroine combat motion v03: hit and down revision. QA note (TEST-ONLY, UNAPPROVED)

Written at 2026-10-20 19:47:30 UTC (actual clock). Correction: the v02 handoff file name carries the stamp 195530, which was a future time when it was written (about 19:42). It is a label only, not an observed finish time.

**Scope**
- Only hit and down are re-authored. v02's hit and down poses are superseded for review; their files are untouched.
- idle and attack (v01), and move, guard, dodge and skill (v02) are unchanged.
- Base: `99bf35a`. Nothing is committed. No game, default, ledger, index, provider or Site changes.
- No Pixelorama run was made for v03 (time). Export equality is not claimed. The known application diagnostics (v01: 0/32 clean) are expected to remain.

## Source binding

- **Author:** `tools/rpg-2-star-ocean-the-second_heroine-sea_combat-motion-author_test-only-v03_20261020-194523-e3b8d061.py`, sha256 `d748e3ded03ff2725fba541aeb717388388587427e7636a9a257b954497f0a69` (LF file).
- **Frozen inputs:** it imports the frozen v01 author `b5d0926c…` and v02 author `d04ab3fb…`, hash-pinned. Both were re-verified unchanged.
- **Approved still:** `4ce65a79…`, read-only.
- **Manifest:** `…manifest_test-only-v03_20261020-194523-5d441ac3.json`, sha256 `66f7804c…0edd`.
- **Check report:** `…check-report_…-1533fdd4.json`, sha256 `a0a71aad…f8ac`.
- **Pose files:** each of the 6 poses has a separate native136 PNG, x4 inspection PNG, PXO and ORA. The native PNG hashes are:

| Pose | sha256 |
|---|---|
| hit-a | `d49aa202…` |
| hit-b | `24001698…` |
| hit-c | `e79a1e1f…` |
| down-a | `e93968af…` |
| down-b | `bf73f705…` |
| down-c | `03c0dd59…` |

## Commands

```
PYTHONHASHSEED=1  PY -I <v03> build   # HSM03 BUILD PASS 43/43
PYTHONHASHSEED=42 PY -I <v03> check   # HSM03 CHECK PASS 68/68
```

## What changed (method)

**Upper body**
- Ponytail, torso and head are now **rotated together** about the waist (RotSprite-style, nearest sampling, no blur).
- Hit leans back −15°, then −8°, then −3° (recovery).
- Down slumps forward +10°, then +20°, then +16°.

**Expression mask**
- Hurt and down poses repaint the eyes inside box x61..72, y28..33 of the still: squeezed shut in hit-a, hit-b and down-a; closed in down-b and down-c.
- **The face is NOT byte-identical to the still in any v03 pose.** Identity rests on the same head, hair and outfit clusters and proportions.

**Down: single-knee kneel**
- The pelvis drops about 30 texels.
- The front boot is planted 6 texels forward, with the knee up via IK.
- The back thigh goes down to a knee on the floor (knee centre at row 131).
- The back shin and calf boot are rotated −88° to lie behind on the floor.
- The blade rests low: the grip is below row 95.
- Sequence: down-a (drop), down-b (lowest, pelvis +30), down-c (settles up 1 texel, lean eases), held. Total 300 ms.

**Hit**
- Timing: hit-a 2 ticks, hit-b 3, hit-c 2, for 233 ms, then the base still.
- The arm is flung down and back, then returns to a ready angle.

**Arm**
- The sword arm is repainted from the rotated shoulder, with the grip given as a reach from that shoulder.
- The weapon outline repair from v02 is applied.

## Checks (68/68)

**Per pose**
- binary alpha
- every colour from the still's 30-colour palette
- margins clear (columns 0 and 135, rows 136..143)
- grounded: lowest row is 135
- no pinhole of 4 texels or fewer
- layers equal the PNG, the ORA merged image equals the PNG, and the PXO cels equal the ORA layers
- bytes on disk equal the rebuild; the rebuild is deterministic

**Global**
- hit leans back by more than 5° and recovers a > b > c
- down's pelvis is at least 25 texels below the still's hips
- down's back knee is at row 130 or lower
- down drops past and then settles
- down slumps at least 10° with the blade low
- clips fit the arena durations: hit within 0.24 s, down within 0.30 s
- the six v03 poses are unique
- face byte-equality is not claimed

## Limitations

- **Back leg in down:** the kneeling back leg (rotated shin plus calf boot) is a cluttered dark mass at the bottom left. It needs a hand-painted floor shin and boot.
- **Rotation artefacts:** rotation aliases the jacket and face texture slightly, as RotSprite does.
- **Coat on the floor:** the coat tails do not pool on the floor.
- **Arm:** the sleeve texture still differs from the still's arm.
- **Not proven:** continuous fluidity at speed, in-game capture (root will capture), and creator acceptance.
- **Skill (v02):** the heroine's current personal skill is a self-buff (`_use_skill` sets the next-attack bonus). v02 skill-contact is a visual apex, not a claim that direct skill damage lands there.
- **Hit synchronisation:** attack contact at 166.667 ms against damage at the press is still open.

## Task status

`content.combat.protagonist-female.combat-actions` stays **IN_PROGRESS**. All 8 actions have authored source poses: v01 idle and attack; v02 move, guard, dodge and skill; v03 hit and down. The production criterion (all 8 committed with QA) is not met: nothing is committed, and hit and down are still under revision. Creator approval and runtime adoption are separate from that criterion.
