# Male protagonist playable path — integration closeout

Task: `male-playable-path-integration`. Existing ledger targets: `content.char.protagonist-male.runtime-integration` and `content.combat.protagonist-male.combat-integration`. Claude produced the bounded adapter; Codex independently corrected scope/rollback and integrated/tested the final source. Base: `bbbfbde84cdc2d07556eded68eeb618522cc183b`.

## Delivered

- One male play entry connects the existing four-direction exploration source set and eight-state combat set through the normal exploration scene, walk-in encounter, battle, result, return, save/reload and natural defeat/retry.
- The exploration adapter binds the existing authored phase stop banks. Re-press and reversal cancel a pending stop bridge; physical movement, speed and collision remain host-owned.
- The male combat index is actor-scoped. It cannot suppress the authorized heroine default when a later female run is started in the same process.
- Configuration refuses invalid packages before starting a new run. Rollback restores the exact prior male overrides, including repeated configuration, and never rewrites the generic combat choices.
- The result overlay waits for the loaded male defeat clip; the existing two-second defeat-to-menu timer is unchanged. All three defeat frames were observed before the overlay.
- A shared dormant `DEFAULT_ADOPTED = false` switch now prepares both ordinary exploration and battle adoption. Its package validation covers the exploration/stop/combat files as one unit. **Ordinary male defaults remain unchanged pending creator authorization.**
- A small male CLI reuses the existing launcher, controls reader and asset preparation. Its settings/saves use the separate ignored `work/mpath24-profile`; it starts a fresh demonstration run.

## Independent canonical evidence

[Root proof and raw source hashes](../../outputs/mpath24/20261021-211004-35c7ce7d/rpg-2-star-ocean-the-second_male-playable-path_root-proof_test-only-v01_20261021-211004-35c7ce7d.json): EN victory138, EN defeat117, ZH victory138, ZH defeat117 checks, all passed. Each execution used the existing checked runner, a120-second deadline, a fresh isolated save profile and actual window rendering at1280×720/30fps. The inherited normal-input harness discloses safe exploration placements and a70px walk-in; battle HP, damage, cooldowns, AI and rewards were never edited to force results.

The four runs cover four directions, release/re-press/reversal, unchanged140logicalpx/s, immediate physical stop, six combat states under normal input and hit/defeat under actual enemy AI, natural rewards/return, pre/post-battle saves and reload without duplicate rewards. Invalid stop JSON, incorrect bridge hash, missing registry and missing combat index were refused.

[Profile scope/rollback check](../../outputs/mpath24/rpg-2-star-ocean-the-second_male-playable-path_profile-scope-rerun_test-only-v01_20261021-171235-035dd16f.log):14/14 passed, including actual female arena creation while the male profile remains active, female source/contact preservation and restoration of prior explicit settings. This is a setup fixture, not normal-input gameplay. The first probe incorrectly preloaded the arena before autoload initialization; that failed diagnostic is retained separately. Loading the arena after initialization fixed the fixture; no game behavior was weakened.

[Heroine normal-default regression](../../outputs/heroine-actions18/rpg-2-star-ocean-the-second_heroine-playable-path_combined-root-proof_v16_20261021-211150-615161ca.json): existing EN normal-input victory/return/reload124checks passed against the final integrated arena. [Launcher smoke](../../outputs/mpath24/rpg-2-star-ocean-the-second_male-playable-path_launcher-smoke_test-only-v01_20261021-171445-180e2d4a.json): actual ZH entry emitted `MPATH24_PLAYABLE_READY` and exited normally under the test-only150-frame limit.

The486 protected source/data files captured before this batch, excluding the two intentionally changed presentation hooks, are byte-identical afterwards. This includes existing heroine packages, both male asset packages, exploration host, save store, AppState and battle rules. Final source hashes still match the tested proof. Staged Git bytes are checked before publication; new hash-bound snapshots use scoped `-text` attributes. No score or approval is inferred from test counts.

Codex inspected actual exploration and attack captures. All109 root-run artifacts are retained locally; selected gameplay captures, all four result reports/logs and source-bound proofs are committed. The other repeated direction screenshots listed in reports remain local and are not claimed as remote assets. Producer-only evidence and partial work remain in the isolated producer checkout; canonical evidence applies to Codex's corrected source.

## Reproduce

```powershell
python -X utf8 -I tools/rpg-2-star-ocean-the-second_male-playable-path_root-runner_test-only-v01_20261021-171230-68e0e142.py
python -X utf8 -I tools/rpg-2-star-ocean-the-second_male-playable-path_launch-cli_opt-in-v01_20261021-170550-24d80b63.py play --language en
```

Use the installed project Python/Godot runtimes. The launcher runs a separate save profile. Root tests are automated, not human playthroughs.

## Remaining boundaries

- No art/motion approval or full runtime-set acceptance is asserted. The male ordinary-game default needs the separate authorization required by project AGENTS.md; the prepared switch remains false.
- Male damage still follows the existing immediate-attack mechanics while the artwork has anticipation. This mismatch is explicitly deferred; this batch does not retime damage or claim synchronized contact.
- The source's480ms gait and authored side-stop drift remain as previously disclosed. No world-foot-lock, slip inspection pass or smooth/fluid artistic acceptance is claimed. No new source art was painted.
- Normal-speed movies were not produced in this batch. Captures are actual1280×720 game-window renders, not native640×360 capture claims. Two ObjectDB exit warnings remain disclosed; no parser/runtime diagnostic was accepted in a passing check.
- Creator visual acceptance and both human integrated playtests remain separate and open. Existing scene/full-sprite counts remain unchanged.

## Frozen meters

Production **55.6% →55.6% (+0.0pp)**; inspection **18.1% →18.1% (+0.0pp)**; creator approval **7.8% →7.8% (+0.0pp)**. Coding111/111; content489/1881. This batch delivers playable integration readiness. The two existing production criteria explicitly require ordinary default use, so they remain in progress until authorized adoption is actually implemented and checked. No per-version task, new denominator or cosmetic-refinement points were added.
