# Exploration source identity/runtime contract check - short QA note

- Run tag: `20261022-012317-d92a0e57`
- Actor argument: `ji-cheng`
- Manifest: `outputs/jexplore31/rpg-2-star-ocean-the-second_ji-cheng_explore-source-manifest_unapproved-jexplore31-v01_20261021-210451-6ebd469a.json`
- Manifest SHA-256 (raw): `4d0409ccf830a35ebb8111ad70714957f620bd1ce169fc3e1795c496c205940b`
- Repository root: `C:\Users\hkzha\Documents\Codex\2026-10-12\rpg-2-star-ocean-the-second\work\max0840-sentry-sync`
- Wrapper: `C:\Users\hkzha\Documents\Codex\2026-10-12\rpg-2-star-ocean-the-second\work\needle31\ds-jcheck\tools\rpg-2-star-ocean-the-second_exploration-source_identity-runtime-contract-check_test-only-v01_20261021-210451-b2782add.py`
- Wrapper SHA-256 (raw): `2fe0faabadaed3b79f184f31e68fe54fe54d9fe36e2275811a6a2e94cc7f0349`
- Python: `C:\Users\hkzha\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe` (3.12.14)

## Actual checks

- Positive: **True**; checks=2596; failed=0.
- Runtime set: `ji-cheng-exploration-source-20261021-210451-b2782add`; actor=`ji-cheng`.
- Source counts: `{"east": {"idle": 4, "walk": 12}, "north": {"idle": 4, "walk": 12}, "south": {"idle": 4, "walk": 12}, "west": {"idle": 4, "walk": 12}}`.
- SOUTH exact source: `game/assets/characters/ji-cheng-hd/rpg-2-star-ocean-the-second_ji-cheng_south-idle-static_unapproved-v01_20261018-132812-1920ff13.png`.

| Negative case | Expected | Refused | Expected failure observed | Unexpected failures | Passed |
|---|---|---:|---|---:|---|
| wrong-registry-actor | refuse | True | registry.actor_matches_argument | 0 | True |
| changed-runtime-copied-png | refuse | True | runtime.frame_hash.walk.south[0] | 0 | True |

## Safety guard

- Original references: 343 (343 present, 0 missing).
- Aggregate SHA-256 before: `dacba634261593b63fa0c3cc38382c16b0a0906a81358a5507e4db3b0eb58a81`
- Aggregate SHA-256 after: `dacba634261593b63fa0c3cc38382c16b0a0906a81358a5507e4db3b0eb58a81`
- Original files unchanged: **True**.
- Fixtures preserved under: `outputs/jexplore31-check/root-deepseek/run-20261022-012317-d92a0e57/fixtures`.

## Scope and limits

- This is a source/package identity and hash contract check. It does not recompose PXO/ORA pixels; the existing tracked native-bank checker remains the pixel check.
- No Godot gameplay, native game test, runtime integration, default adoption, ledger, Bible, operating registry, Git index/commit or account change was made by this wrapper.
- Source portraits and source art remain CONCEPT/UNAPPROVED; this wrapper makes no art or approval claim.
- Tests alone earn no production ledger points.
- Ji Cheng: **tested source contract only**; a different actor result does not establish Ji Cheng.
- Overall result: **True**.
