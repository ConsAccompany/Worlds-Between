# Content-hash algorithm for text locks: `sha256-text-lf-v1`

M8, 2026-10-14. This is a tooling decision. It does not approve or reject any art, and it changes no counter (exploration sprites **0/52**, scene-quality gates **0/11**, human timed playtests **0/2**).

## Problem

After `ff8acd8` (female south idle static baseline, selout v8), a clean checkout failed the readiness check and the Game Bible selout test. The cause was that text files had been hash-locked by their raw on-disk bytes. On this Windows workspace (`core.autocrlf=true`, no `.gitattributes`), the bytes on disk depend on which tool wrote the file and on the checkout settings. Git stores every one of these files with LF.

| File | Workspace bytes | Lock taken over | Clean CRLF checkout | Clean LF checkout |
| --- | --- | --- | --- | --- |
| v8 manifest (Python `write_text`) | CRLF | CRLF | pass | **fail** |
| v8 QA report (Godot) | LF | LF | **fail** | pass |
| registry, inventory (`sources.*.sha256`) | CRLF / LF | mixed | stale checklist | stale checklist |

Observed failures:

- **Readiness builder, check mode:** `static baseline qa_report missing or hash changed` (CRLF clone) or `static baseline manifest missing or hash changed` (LF clone), plus stale checklist JSON and Markdown in both clones.
- **Selout test:** the inventory hash at step 4 failed in the CRLF clone, and the `0fa7937d…` manifest assertion failed in the LF clone.

## Decision

Every recorded content hash now names its algorithm (`sha256_algorithm`):

- **`sha256-bytes`:** SHA-256 of the exact file bytes. Used for binary files (PNG). The values are unchanged.
- **`sha256-text-lf-v1`:** SHA-256 of the file bytes after each CRLF pair (`0D 0A`) is replaced by LF (`0A`). Used for text files (JSON, Markdown).
  - Nothing else is normalized. A lone CR, the BOM, whitespace and the Unicode form are hashed as they are.
  - Input containing a NUL byte or invalid UTF-8 is refused, not hashed. A PNG therefore cannot be locked with this algorithm by mistake.
  - The readiness check also fails if a `.png` lock uses anything other than `sha256-bytes`, or a text lock uses anything other than `sha256-text-lf-v1`.

For a file that Git stores with LF, the `sha256-text-lf-v1` value equals the raw SHA-256 of the committed blob. The new portability test checks this against `HEAD`.

Implementations:

- Python: `text_sha256` / `content_hash` in the [readiness builder](../tools/rpg-2-star-ocean-the-second_character-sprite-readiness_build-and-check_m8-v01_20261014-184413-c8e6c511.py).
- Node: the [shared helper](../tools/rpg-2-star-ocean-the-second_content-hash_text-lf-v1_m8-v01_20261014-224905-022124e7.js), used by the [selout test](../tests/game-bible-selout-v2/rpg-2-star-ocean-the-second_game-bible_selout-v2-review-card_check_m8-v02_20261014-234724-e3b7a915.js) and the [portability test](../tests/content-hash-portability/rpg-2-star-ocean-the-second_content-hash-portability_check_m8-v01_20261014-224905-72fc691e.js).
- The portability test runs both implementations on the same inputs and requires identical results.

The builder now always writes the checklist JSON and Markdown with LF. Its stale-artifact check compares content after CRLF→LF only.

## Regenerated values

| Lock | Before | After |
| --- | --- | --- |
| v8 manifest | raw `0fa7937d…5992` (CRLF working copy) | `sha256-text-lf-v1` `3ba35811…10ed` |
| v8 QA report | raw `513ab659…631a` (LF) | `sha256-text-lf-v1` `513ab659…631a` (same) |
| registry (`sources.registry`) | raw `2f0fc50e…556a` (CRLF working copy) | `sha256-text-lf-v1` `73275389…273d` |
| inventory (`sources.inventory`) | raw `04a83797…def2` (LF) | `sha256-text-lf-v1` `04a83797…def2` (same) |
| v8 PNG, three captures | `sha256-bytes` | unchanged |

Source integrity is preserved:

- The CRLF manifest that produced `0fa7937d…` still hashes to that value in the original workspace.
- After CRLF→LF it is byte-identical to Git object `dd24f1e231f5fa905f159a6553a4071be4cf3d6a` committed in `ff8acd8`, whose SHA-256 is `3ba35811…10ed`.
- The [decision record](character-visuals/rpg-2-star-ocean-the-second_protagonist-female_south-idle-static-baseline-decision_m8-v08_20261015-022700-07161696.md) keeps both values.

## Not done, and why

- **No `.gitattributes`.** Normalized hashing already makes the locks independent of checkout settings. A `* text eol=…` rule would renormalize unrelated files across the repo and still would not cover a user's local `core.autocrlf`. Git already detects the PNGs as binary and never converts them; the PNG locks pass byte-exact in both clean clones.
- **Historical edit tools unchanged.** The selout v2–v8 edit tools and the raw-byte hashes they wrote into their manifests (`editor.script_sha256`, preserved-file locks) are one-shot authoring provenance. No check re-verifies them, and rewriting them would change the hash-locked v8 manifest. Re-running those tools from a clean checkout is not part of verification.
- **Historical notes unchanged.** The v8 QA note and the v8 entry in `docs/progress.md` still quote the raw `0fa7937d…` value. That was accurate for the Windows working copy at the time; this record and the decision-record amendment explain it.

## Verification

Run from the repository root (`PYTHON` must point to Python 3.10+ if `python3` / `python` on PATH is not one):

```
python tools/rpg-2-star-ocean-the-second_character-sprite-readiness_build-and-check_m8-v01_20261014-184413-c8e6c511.py
node tests/content-hash-portability/rpg-2-star-ocean-the-second_content-hash-portability_check_m8-v01_20261014-224905-72fc691e.js
node tests/game-bible-selout-v2/rpg-2-star-ocean-the-second_game-bible_selout-v2-review-card_check_m8-v02_20261014-234724-e3b7a915.js
node tests/game-bible-character-readiness/rpg-2-star-ocean-the-second_game-bible_character-readiness-view_check_m8-v01_20261014-225834-0f4cdab5.js
```

These pass in fresh clones of the fix commit with `core.autocrlf=true` (CRLF working tree) and `core.autocrlf=false` (LF working tree). A one-character edit to the v8 manifest or a one-byte edit to the v8 PNG still fails all three hash-checking checks. A CRLF↔LF conversion alone passes.
