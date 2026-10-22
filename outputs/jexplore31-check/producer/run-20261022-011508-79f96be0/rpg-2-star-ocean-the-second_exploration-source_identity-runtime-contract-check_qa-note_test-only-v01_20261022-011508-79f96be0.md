# Exploration source identity/runtime contract check - short QA note

- Run tag: `20261022-011508-79f96be0`
- Actor argument: `liang-xu`
- Manifest: `outputs/lexplore28/rpg-2-star-ocean-the-second_liang-xu_explore-source-manifest_unapproved-lexplore28-v01_20261021-194350-2ceb83e8.json`
- Manifest SHA-256 (raw): `6198eafca26c0d76e4a636d953eccab0a8ea4e628c9e734c77fe05535094bdc2`
- Repository root: `C:\Users\hkzha\Documents\Codex\2026-10-12\rpg-2-star-ocean-the-second\work\max0840-sentry-sync`
- Wrapper: `C:\Users\hkzha\Documents\Codex\2026-10-12\rpg-2-star-ocean-the-second\work\needle31\ds-jcheck\tools\rpg-2-star-ocean-the-second_exploration-source_identity-runtime-contract-check_test-only-v01_20261021-210451-b2782add.py`
- Wrapper SHA-256 (raw): `2fe0faabadaed3b79f184f31e68fe54fe54d9fe36e2275811a6a2e94cc7f0349`
- Python: `C:\Users\hkzha\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe` (3.12.14)

## Actual checks

- Positive: **True**; checks=2596; failed=0.
- Runtime set: `liang-xu-exploration-source-20261021-194350-3acdbd6e`; actor=`liang-xu`.
- Source counts: `{"east": {"idle": 4, "walk": 12}, "north": {"idle": 4, "walk": 12}, "south": {"idle": 4, "walk": 12}, "west": {"idle": 4, "walk": 12}}`.
- SOUTH exact source: `game/assets/characters/liang-xu/south-idle-static-pilot-unapproved-v01/rpg-2-star-ocean-the-second_liang-xu_south-idle-static-pilot_unapproved-v01_20261016-140940-46a036ed.png`.

| Negative case | Expected | Refused | Expected failure observed | Unexpected failures | Passed |
|---|---|---:|---|---:|---|
| wrong-registry-actor | refuse | True | registry.actor_matches_argument | 0 | True |
| changed-runtime-copied-png | refuse | True | runtime.frame_hash.walk.south[0] | 0 | True |

## Safety guard

- Original references: 341 (341 present, 0 missing).
- Aggregate SHA-256 before: `1b6432c5f5dfc605ed25f5afe2a2a56b1d97a91cab08a03c47616a8d52d3b1c6`
- Aggregate SHA-256 after: `1b6432c5f5dfc605ed25f5afe2a2a56b1d97a91cab08a03c47616a8d52d3b1c6`
- Original files unchanged: **True**.
- Fixtures preserved under: `C:\Users\hkzha\Documents\Codex\2026-10-12\rpg-2-star-ocean-the-second\work\needle31\ds-jcheck\outputs\jexplore31-check\run-20261022-011508-79f96be0/fixtures`.

## Scope and limits

- This is a source/package identity and hash contract check. It does not recompose PXO/ORA pixels; the existing tracked native-bank checker remains the pixel check.
- No Godot gameplay, native game test, runtime integration, default adoption, ledger, Bible, operating registry, Git index/commit or account change was made by this wrapper.
- Source portraits and source art remain CONCEPT/UNAPPROVED; this wrapper makes no art or approval claim.
- Tests alone earn no production ledger points.
- Ji Cheng: **NOT TESTED in this run**; a different actor result does not establish Ji Cheng.
- Overall result: **True**.
