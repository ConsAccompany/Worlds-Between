# M7 field-station regression: bounded test repair

Task: `qa.validation.pre-playtest-regression` (remains TODO; full acceptance dependencies unchanged). Producer: Claude Code using the existing signed-in Max/firstParty route. Coordinator and independent checker: Hermes. Tested base: `8a00eeaf9e302fc538aad0daf6f48515cc177901` plus the exact test-file hash in the machine proof. No game runtime, default, asset, art acceptance or scoring definition changed.

## Delivered boundary

`game/tests/m7_smoke.gd` now chooses the active Capitol ruins anchors, resolves prop coordinates onto the existing walkable mask, and retains the previous branch when the v12-based ruins selector is inactive. It checks that recruitment dialogue is open, visible, in recruit mode and enabled before emitting the invitation button signal, for city, outskirts and ruins. No existing assertion or destination expectation was removed.

The ordinary default was already creator-authorized; the repair does not adopt any new candidate. Source production and artistic acceptance remain separate.

## Diagnosis and actual evidence

The unmodified M7 test failed `field station opens scifi.ruins`. Its legacy field-station position no longer falls inside the current Capitol-west interaction radius. Legacy recruitment also falsely succeeded because directly emitting the button signal did not require that dialogue had opened. The new guard catches that path.

Independent execution used the existing bounded checked runner, finite 120-second deadlines, fresh Godot processes and Dummy audio. Required success markers and runtime/parser diagnostics were checked in addition to process status. Seven independent runs are retained:

1. Original test snapshot: expected RED at `field station opens scifi.ruins`.
2. Negative fixture with legacy coordinates: expected RED at `ruin recruitment dialogue opens`.
3. Repaired M7: PASS `M7_SMOKE_OK`, including its Chinese/all-companion and English/optional-companion routes, field traces, survey returns, saves/reloads and report flow.
4. M1: PASS `M1_SMOKE_OK`.
5. City navigation: PASS `M8_CITY_NAVIGATION_OK`.
6. City integration: FAIL `CITY_INTEGRATION_FAILED: native pixel actor male`.
7. City re-entry: PASS `M8_CITY_REENTRY_OK`.

The city-integration failure was independently reproduced in the existing isolated readiness checkout at `53769f4cf99071b0c090cfa6fa92f2e48957682b`, before this repair. Its test bytes are identical to the active checkout. This demonstrates the failure predates this M7 test-only change; it does not resolve or waive it. Full regression remains NOT green. Next bounded work is to distinguish that test's old 32x48/native-idle expectations from the creator-authorized current sprite/default pipeline before changing anything.

## Failed attempts retained

- Initial Claude startup hit `Prompt is too long`; retrying with unrelated MCP discovery disabled preserved normal subscription authentication.
- One Claude session lacked edit/command permissions and produced a static diagnosis only; it supplied no execution evidence.
- The repair session reached its bounded turn limit after obtaining M7 GREEN; a separate report-only Claude call wrote the producer report. No quota depletion was reported and no DeepSeek inference/fallback was used.
- An intermediate compile-time preload caused an `AppState` compile error; loading script constants after autoload initialization resolved that startup ordering issue.
- Standing at raw prop anchors failed exact survey-return position. The final test uses the runtime's existing safe walkable-position mapping; it does not loosen return equality.

## Proof and limits

Machine proof: `outputs/m7reg62/rpg-2-star-ocean-the-second_m7-regression_independent-proof_v01_20261023-054500-a37c62f1.json`. It binds the exact test hash, base, commands, positive/negative outcomes, baseline failure and 11 preserved producer/independent log/report artifacts by raw SHA-256. All hashes are raw bytes; no text normalization is claimed. Original negative fixtures and the execution helper remain in ignored `work/m7-rotation/`.

This is headless functional evidence, not rendered bilingual visual acceptance, continuous-motion inspection, listening, Windows execution, or either required human playtest. Full pre-playtest regression and its creator-art dependencies remain open. The current default exercises the v12 branch; successful legacy-layout behavior has not been newly established. The negative legacy-coordinate fixture is not a successful legacy-layout test.

## Progress

- Production **61.0% → 61.0% (+0.0 pp)**.
- Performed inspection **21.6% → 21.6% (+0.0 pp)**.
- Creator approval **7.8% → 7.8% (+0.0 pp)**.

No task/weight/denominator was added. A useful regression-test repair is delivered without claiming full QA credit. The tested source and evidence are selectively integrated; subsequent Git verification records the actual integrated revision.
