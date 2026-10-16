# 武艺 ten-node proposal validator: clean-clone integrity repair — QA receipt

- Date: 2026-10-16 14:03 local (EDT)
- Status: **integrity repair only. The 武艺 proposal stays a PROPOSAL, UNAPPROVED and NONRUNTIME.** All 50 nodes are still pending balance and creator review. No node data, rule, cap or JP value changed.
- Not touched: `game/scripts/battle_arena.gd` (its uncommitted local edits belong to another workstream), runtime, art, the Game Bible, the Site checkout, and the 应变 proposal. The progress meter stays at 35.0% with a zero-change closeout.

## Defect

`outputs/…martial-job-trees_ten-node-skill-proposal_unapproved-v01_20261016-112044-4e3b550a.json`, as pushed in 462b17d, pinned `sources.runtimeBattleArena` to `be8859a8…a592acae`. That is the hash of the dirty local `battle_arena.gd`, not the committed one. The embedded `source-hashes` result was `pass`.

On a detached worktree at `origin/main` 462b17d, `node tools/…706c17da.js` gave:

```
WARN source-hashes — drift: runtimeBattleArena
FAIL embedded-results-match — 差异 2 项：source-hashes|warn|drift: runtimeBattleArena / source-hashes|pass|10 个来源一致
21/23 pass, 1 warn, 1 fail
```

So a drift that the validator classes as a warning still failed the run through the embedded-results comparison.

## Fix

1. **Proposal:** `sources.runtimeBattleArena.sha256` → `e9737c4082ffa180b6bab1340311db8d33aab526a9ef7bcb42bb178d5f859f02`. This is the committed file, unchanged from da394c3 through 462b17d. Its note now says the pin is the committed version.
   - Every constant the proposal cites was re-read in the committed file: `GUARD_HIT_COST := 6`, `damage * 0.30`, `DODGE_COST := 12`, `dodge_time = 0.27`, windup 0.48 / 0.65, reach `> 69.0`, and `var cost := 10 + 3 * skill_stage`.
   - `validation.ranAt` and `validation.note` are updated. The 22 embedded check results are unchanged.
   - Proposal `sha256-text-lf-v1`: `8cf65b63…7ebd3d` → `dcc5c330…4350e2`.
2. **Validator** `tools/…706c17da.js` (`sha256-text-lf-v1` `7e8b374a…` → `d8beaa1b…`): `embedded-results-match` compares only the id of `source-hashes` (`ENVIRONMENT_CHECKS`). Drift there stays a WARN. All other checks still compare id, result and detail.
3. **Design/QA note** `docs/design/…d2cf9637.md`: the hash line is updated and a repair section is added.

## Evidence (detached worktree `C:\wb\mfix` at origin/main 462b17d + the two repaired files)

| Run | Result | Exit |
|---|---|---|
| Martial validator `…706c17da.js` | 23/23 pass, 0 warn, 0 fail; `embedded-results-match — 22 项一致` | 0 |
| Adaptive validator `…e0ce1cbc.js` | 23/23 pass; embedded results match | 0 |
| Independent crosscheck `…122bcb8b.js` | 13/15 pass, 2 warn, 0 fail (the known redirect-cap 50 vs 40 and energy-return-ceiling differences) | 0 |
| Martial validator in the main working tree (dirty `battle_arena.gd`) | 22/23 pass, 1 warn (`source-hashes — drift: runtimeBattleArena`), 0 fail | 0 |

Mutations run on the worktree copy, outside the repo files:
- An active node's energy set to 99 fails `active-passive-energy` and `embedded-results-match` (exit 1).
- Removing the embedded `source-hashes` entry fails `embedded-results-match` (exit 1).
- A wrong source hash gives a `source-hashes` WARN only (exit 0). This is by design.

## Limits

- Source drift, including a wrong pinned hash, is only a warning. That was already the validator's documented policy. This repair stops the drift from also failing the run through the embedded comparison.
- When another workstream commits its `battle_arena.gd` edits, this validator will WARN on `source-hashes` until the proposal is re-pinned. It will not fail.
- The open balance points remain: JP 30/45/60/75 vs runtime 35/55/80/110; redirect cap 50 vs 40; energy return 32 vs 24.
