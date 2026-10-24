# Heya north walk-fit continuity audit — pre-fix (capture-r3, frozen failing evidence)

- Independent verdict: **FAIL**
- Fit proof self-reported passed: `True` (not trusted)
- Scope: north-only source fit; no runtime adoption, input approval or art/motion approval
- Frozen timing: walk 40 ms, start 320 ms, stop 800 ms, repress 940 ms, reverse 1420 ms, settle 120 ms inclusive

## Derived continuity predicates

| Predicate | Value | Pass |
| --- | --- | --- |
| `forward_prestop_walk_phase_derived` | `11` | — |
| `forward_selected_bridge_phase` | `7` | — |
| `forward_prestop_equals_selected` | `False` | FAIL |
| `forward_captured_prestop_frame_is_phase` | `True` | PASS |
| `forward_s1_s2_supplied_by_selected_bridge` | `True` | PASS |
| `forward_stop_endpoints_walk_to_idle` | `True` | PASS |
| `reverse_prestop_walk_phase_derived` | `11` | — |
| `reverse_selected_bridge_phase` | `7` | — |
| `reverse_prestop_equals_selected` | `False` | FAIL |
| `reverse_restore_walk_phase` | `7` | — |
| `reverse_restore_equals_reverse_prestop` | `False` | FAIL |
| `reverse_s2_s1_supplied_by_selected_bridge` | `True` | PASS |
| `reverse_bridge_endpoints_walk_to_idle` | `True` | PASS |
| `reverse_sequence_ends_idle_f00` | `True` | PASS |
| `exact_targets_preserved` | `True` | PASS |
| `walk_and_settle_durations_preserved` | `True` | PASS |
| `all_stop_and_reverse_endpoints_continuous` | `False` | FAIL |

## Actual captured stop/reverse frames

| t (ms) | kind | idx | frame |
| --- | --- | --- | --- |
| 780 | walk | 11 | `rpg-2-star-ocean-the-second_heya_walk-north-walk-p11_unapproved-hnw171-v01_20261024-151500-10589253.png` |
| 820 | s1 | 0 | `rpg-2-star-ocean-the-second_heya_walk-north-stop-p07-s1_unapproved-hnw171-v01_20261024-151500-e329e992.png` |
| 860 | s2 | 0 | `rpg-2-star-ocean-the-second_heya_walk-north-stop-p07-s2_unapproved-hnw171-v01_20261024-151500-6166de03.png` |
| 900 | idle | 0 | `rpg-2-star-ocean-the-second_heya_walk-north-idle-f00_unapproved-hnw171-v01_20261024-151500-740768fc.png` |
| 960 | walk | 0 | `rpg-2-star-ocean-the-second_heya_walk-north-walk-p00_unapproved-hnw171-v01_20261024-151500-1721b5e9.png` |
| 1200 | walk | 6 | `rpg-2-star-ocean-the-second_heya_walk-north-walk-p06_unapproved-hnw171-v01_20261024-151500-d8e37908.png` |
| 1440 | s2 | 0 | `rpg-2-star-ocean-the-second_heya_walk-north-stop-p07-s2_unapproved-hnw171-v01_20261024-151500-6166de03.png` |
| 1480 | s1 | 0 | `rpg-2-star-ocean-the-second_heya_walk-north-stop-p07-s1_unapproved-hnw171-v01_20261024-151500-e329e992.png` |
| 1520 | walk | 7 | `rpg-2-star-ocean-the-second_heya_walk-north-walk-p07_unapproved-hnw171-v01_20261024-151500-4d0a6775.png` |
| 1560 | idle | 0 | `rpg-2-star-ocean-the-second_heya_walk-north-idle-f00_unapproved-hnw171-v01_20261024-151500-740768fc.png` |

## Artifacts

- manifest: `outputs/heya-nw171/fit/capture-r3/rpg-2-star-ocean-the-second_heya_walk-north_normal-speed-manifest_test-only-v01_20261024-151500-hnw17101.json` `ec110aa2cfd3f607877a133af73d4d7b9d6b712a715fa78f696bb379b8ca03e8`
- runtime: `game/assets/characters/heya-native-v01/north-walk/rpg-2-star-ocean-the-second_heya_walk-sprite-set-runtime_unapproved-hnw171-v01_20261024-151500-1eff5ab7.json` `0bb769b19247b6a986b34d7b82528c155402ef621ab12c573bf3d27012cabed6`
- stop: `game/assets/characters/heya-native-v01/north-walk/rpg-2-star-ocean-the-second_heya_walk-stop-transition-supplemental_unapproved-hnw171-v01_20261024-151500-4a055ed1.json` `5050b1ee4b3901d3f0491b9345d993078015bdfd1329ea8fbb4d90c354e2c1a5`
- proof: `outputs/heya-nw171/fit/rpg-2-star-ocean-the-second_heya_walk-north-normal-speed-proof_test-only-v01_20261024-151500-hnw17101-capture-r3.json` `66c301a97c667a4dc09cfd9ebcc47aa23d79b7540f9191c4130541970eb1e31a`
- audit script: `outputs/heya-nw171/fit-repair/rpg-2-star-ocean-the-second_heya_walk-north_fit-continuity-audit_v01_20261024-151500-hnw171fr01.py` `cc5fe601ca551dd5cb2fec323838a89229693151557b3589c48445a53b48353e`

Existing fit proofs/reports are immutable and were not modified by this audit.
