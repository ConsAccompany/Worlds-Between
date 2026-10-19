# Female exploration input guard: three rejection-path repairs

Scope: DeepSeek isolated workspace `work/dual02/ds-fexp-guard` only. Codex froze the producer driver, guard, test, result and v06 stdout/stderr before changes, then corrected three concrete guard defects. No canonical integration checkout, driver, host, renderer model, package/runtime JSON pin, source asset, ledger/index/Git, provider, account or Site file was changed.

## Repairs

1. `_read_bytes()` and `text_lf_sha256()` no longer call `HashingContext.update()` with an empty buffer. Empty input yields the exact SHA-256 `e3b0c442…b855`; an empty package/runtime is still refused at its raw fixed pin before JSON parsing or model construction.
2. The model-validation loop runs only when the dictionary has exactly the required east/west/north keys. A three-item dictionary with three unrelated keys now returns validation errors rather than indexing missing keys.
3. Model-copy comparison converts/compares only an actual String model value after type validation. A Dictionary model value now returns the expected path-type error rather than calling `String(Dictionary)`.

The fixed raw package/runtime JSON pins remain unchanged. This remains a pinned representative-package guard, not a general loader for arbitrary mutable packages.

## Actual verification

The original99 guard/driver assertions plus8 meaningful regressions pass: **107/107**, exit0, required `FEXP_GUARD_TESTS_OK checks=107` marker, **9.031s** under the repository checked runner with100-second deadline. A direct headless Godot4.7.2 process used fresh isolated APPDATA/LOCALAPPDATA and Dummy audio. The complete unfiltered combined log contains no `ERROR`, `SCRIPT_ERROR` or warning diagnostics.

New cases cover empty raw/text hashing, empty package pin rejection, empty runtime pin rejection, wrong three model keys, Dictionary model value, empty-package attach refusal and unchanged target/zero constructors after that rejected attach.

Attach atomicity was reviewed: flag/actor gates precede loading; failed package validation returns before `_build_runtime`; unsuccessful model construction returns before target mutation. Scale/flip and child insertion occur only after the complete per-driver runtime is built. Existing tests retain flag-off/off-path no-I/O behavior, mutated package/runtime refusal, source rest/contact/shadow/turn/re-press contracts and independent mutable state for two attached drivers. No driver semantics were changed by these guard fixes.

## Preserved diagnostics and limits

The producer's v06 stderr remains preserved verbatim: two `user://logs` write/open diagnostics and one Windows root certificate-store diagnostic. Its successful assertion marker was not represented as a clean application pass. The new direct isolated run does not reproduce those errors; no diagnostic filter or system account/configuration change was used. This does not establish a universal cause/fix for every producer sandbox environment.

Frozen producer artifacts and the new checked log/result use descriptive project-prefixed filenames under this directory. Generic historical `guardtest*.stdout` files are not selected as integration evidence. No new failure occurred in the final107-case run. M1 was not rerun because only the bounded guard rejection paths and tests changed; the producer's older M1 result/diagnostics are not upgraded to clean evidence by this work.

## Files and bindings

- Modified guard: `game/scripts/fexp/rpg-2-star-ocean-the-second_female-complete-explore_input-guard_v01_20261019-190507-a7d3e9b1.gd`.
- Modified test: `game/tests/rpg-2-star-ocean-the-second_female-complete-explore_guard-contract-check_v01_20261019-190507-a7d3e9b1.gd`.
- Frozen prior driver/guard/test and producer result/stdout/stderr: `outputs/guard-root-v02/…_v02_20261019-192404-8ab21e47.*`.
- New unfiltered log and checked-runner command/result: `…_actual-checked-log…log` and `…_actual-result…json`.
- `…_source-bound-proof…json` binds final raw source hashes, protected model/driver/host/JSON hashes and evidence. Protected source bytes are unchanged. All hashes are raw SHA-256; edited text is UTF-8/LF, with no hidden normalization in the hash fields.

Root still owns merging optimized renderer models, repinning the integrated package and final normal-scene verification. No full female driver, art, motion or release approval is claimed.
