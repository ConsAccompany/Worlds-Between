# JPATH33 Ji Cheng playable-path boundary check (test-only)

- Task tag: `20261021-222224-c7e7cec5`
- Owner: DeepSeek support; canonical base `759f2b9ffc1d2e236f5ab15dca3350b20e7943bb`
- Verdict: **PASS**, `150` checks, `0` failed, checked-runner exit `0`.
- Success marker: `JPATH33_BOUNDARY_PASS checks=150`
- Harness: `tools/rpg-2-star-ocean-the-second_ji-playable-path_boundary-check_test-only-v01_20261021-222224-c7e7cec5.gd`
- Harness SHA-256 (raw bytes): `8D1B224B643DA6D8971FDA7772B484238AB9A5BCED38DAEAEE6A04D5E8F2311A`
- Checked log: `run-20261021-222224-c7e7cec5/boundary-02.log` (SHA-256 `C088D0653C2C7E8FA893276BA7BC724BE78942F0561AB92293964DDAEDFA5A21`)
- Retained failure: `run-20261021-222224-c7e7cec5/boundary-01.log` (first attempt).

## Tested source (producer checkout read-only; byte-identical temp copy)

| Path | SHA-256 |
|---|---|
| `game/scripts/jpath33/..._config_opt-in-v01_20261021-222438-7d4b2e91.gd` | `90826C1C3F25531F0AE5D1EAFA8FB40971F584D5B6FC3B6BADAA0124D661625E` |
| `game/scripts/jpath33/..._entry_opt-in-v01_20261021-222438-7d4b2e91.gd` | `91F5D770FF84EE2453F1E99AD6CB7DEE3D264D9E97D823418D6D67A2BA0DF779` |
| `game/scripts/jpath33/..._npc-driver_opt-in-v01_20261021-222438-7d4b2e91.gd` | `003CE85B39BA492703BD3B8C29F95C70DEAC47C29BBE3A5014D27BB0B7CE5AD6` |
| `game/scripts/scifi_exploration_area.gd` | `A8E147F11E1487E8DDEC57BC068CA10B96451636E99F7187B6362EC50E3E3F70` |
| `game/scripts/battle_arena.gd` | `C9C01B86589CAFFE57B63C33C1D8428F2ED7B414E700CEAAC046089ED70FF543` |

Hashes were re-checked equal between the producer checkout and the isolated runtime copy immediately before the checked run. The canonical checkout was not written; the temporary copy (under this output root) was removed after evidence collection. Re-run after any later producer edit.

## What the 150 checks exercise

1. **Defaults**: Ji `DEFAULT_ADOPTED=false`, `ART_APPROVED=false`, no override, `enabled()==false`; Zhao and Liang authorized defaults still on, art unapproved; Ji member/destination exactly `ji-cheng` / `scifi.ruins`.
2. **Locale/appearance/package**: `en/male` and `zh/female` validate; invalid locale `fr` and invalid appearance `other` are refused atomically with an unchanged state snapshot; the actual combat index contains exactly the `ji-cheng` member.
3. **Real ruins host + field driver**: `scifi_exploration_area` attaches the jpath33 driver to the existing `field_npc` at `(200,145)` in `scifi.ruins`; hero-only party, no forced recruit/follower; four-direction idle/walk banks, distinct walk paths, phase-aware stop bridge, cancellation and settle, all from `jexplore31`; the NPC never moves.
4. **Actor prerequisite (existing story rule only)**: direct `recruit_member("ji-cheng")` is refused before the records console; the real ruins invite is disabled and shows `recruit_ji_locked`; the real `E` console interaction sets `ji_records_checked`; the invite then enables, shows `recruit_ji`, and the actual dialogue primary handler recruits Ji. No new story rule, dialogue, stat or save-schema behavior.
5. **Coexistence**: declared party fixture (hero/Zhao/Liang/Ji) loads three independent member models; each model owns only its own slot; Zhao-first legacy alias still Zhao; hero keeps slot 0.
6. **Own disable / alias fallback**: Ji off removes only Ji from combat and the ruins hook; Zhao/Liang field and combat paths remain; with Zhao off the alias falls back to the first loaded model (Liang), not a fake Zhao.
7. **Whole-package rejection**: missing registry, wrong-member registry, missing supplement, wrong-actor supplement, missing combat index, wrong-member combat index and surplus-member combat index are each rejected by `validate()`, each `configure()` refuses without state mutation, and the hosts keep hero plus Zhao/Liang whole while omitting Ji whole.
8. **Rollback**: restores only Ji's `enabled_override`; Zhao/Liang controls and host overrides stay untouched; post-rollback companions are Zhao/Liang only and Ji's ruins hook is off.
9. **Hero female/male regression**: after a normal app start, the hero combat model still owns slot 0 for both appearances.

## Command (isolated copy, checked runner, 180 s cap)

```text
python -X utf8 -I tools/rpg-2-star-ocean-the-second_godot_checked-runner_v01_20261018-203400-f74ac6d1.py \
  --timeout 180 --expect JPATH33_BOUNDARY_PASS --log <run>/boundary-02.log -- \
  python -X utf8 -I outputs/jpath33-check/..._godot-cert-store-filter_test-only-v01_20261021-222224-c7e7cec5.py \
  <godot> --headless --path <isolated-game-copy> --fixed-fps 30 -s res://tests/<harness>
```

`CHECKED_RUN PASS None exit= 0 elapsed= 11.344 missing= []`; 150 PASS lines, 0 FAIL, 0 diagnostic lines. The test-local filter removes only the confined-Windows bootstrap line `ERROR: Failed to read the root certificate store.` and its immediate `at: get_system_ca_certificates` continuation. Every other line, including any other `ERROR`/`SCRIPT ERROR`/parse error, still reaches the checked runner. Import itself exited `0` with only that bootstrap line.

## Honest failures and limits

- First attempt `boundary-01.log`: the harness instantiated `battle_arena` before any run had initialized `hero_state`, producing `SCRIPT ERROR ... 'job_series'` at `battle_arena.gd:1767`. Fixed in the harness by calling the normal `AppState.begin_new_run()` before the default hero regression; no host code was changed for this.
- This is a boundary/renderer/fixture check, **not** real input, a playthrough, save/reload, combat balance, dialogue content, collision, AI, stats or art/motion approval. Ji's actual `E` console and invite were invoked through the real host handlers, but not by human input; root owns the real-input/movie path and the combined canonical run.
- Ji remains `DEFAULT_ADOPTED=false`; no default/art adoption, ledger/Bible/registry edit, commit, push, account or paid-credit change was made.
