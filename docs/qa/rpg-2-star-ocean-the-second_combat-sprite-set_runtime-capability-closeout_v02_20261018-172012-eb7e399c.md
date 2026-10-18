# Combat sprite runtime capability - technical closeout

Completed 2026-10-18T17:20:12 America/New_York. Account quota was not used: Codex finished the interrupted implementation after creator authorization. Task `code.runtime.combat-sprite-pipeline`. Base commit `3e040a9ae3bd410d8fab4b0921bcb63e8bb3c9b7`.

## Scope and limits

The normal battle renderer can load cached, data-driven side-view action sets when `--combat-sprite-set-pilot` is explicitly enabled. Default remains OFF. `--combat-sprite-set-index=<path>` selects the index. Each fighter independently falls back atomically to the existing renderer for an invalid or absent set. No movement, collision, party order, HP, energy, AI, inputs, attack reach, hit timing, save data or default art changes.

The five sets are code-drawn diagnostic mannequins: male hero, female hero, Liang Xu, Zhao Ling and Ji Cheng. Both hero appearances have separate identity manifests and distinct diagnostic colors. They exercise the existing 0.65 display proportion, 61-pixel crown-to-sole at native logical scale, and floor pivot. They are NOT character art, not candidates for artistic review and not a complete accepted character set. Full sprite acceptance remains 0/52. No fluidity or motion-quality claim is made.

## Fix and independent checks

The interrupted loader converted untrusted JSON fields with `String(value)`. The prior root probe demonstrated that a dictionary schema raised a SCRIPT ERROR despite exit 0. The loader now checks actual types before conversion. It validates schema, character/appearance identity, display proportion, facing, sheet path and optional metadata. Numeric cell/pivot/frame fields require finite integral values in range before narrowing. Invalid JSON uses the error-returning parser and does not print an engine parse error. A male manifest requested as female rejects with identity_mismatch; a valid female set loads in an actual battle.

Malformed tests cover dictionaries, arrays, numbers, booleans, null, strings where an integer is required, fractional/overflow coordinates and durations, malformed action collections and loop booleans, missing/unknown actions and schemas, empty frames, invalid sheet/cell/pivot/identity, missing/typed index fields and empty index paths. Test expectations use explicit rejection statuses. No test threshold was widened or edge case skipped.

- Headless: **162 checks passed**, no SCRIPT ERROR/ERROR/FAIL lines.
- Windowed: **261 checks passed**, **12 bilingual native 640x360 captures**, no SCRIPT ERROR/ERROR/FAIL lines.
- Three encounters each have **600-step** pilot-on/off traces equal to each other and the saved pre-feature base trace. HP, energy, positions, timers, real hits, AI, feedback, party order and save snapshot match.
- Five flag-off render combinations are pixel-identical to the base (patrol, sentry without its pilot, sentry pilot, backdrop, sentry+backdrop). Missing-index pilot-on output is also pixel-identical to flag-off.
- Attack/dodge one-shots and idle/move/guard loops match an oracle built directly from fixture JSON at 30/60 fps. Every action/frame pivot in both facings is checked (296 cases). A lethal hit plays defeat and holds its final frame. Zhao skill correctly falls back to attack when the optional action is absent.
- Fixture rebuild: **11 files byte-exact** after LF normalization of JSON.
- Independent evidence checker passes source LF hashes, 12 image hashes, base Git-blob hash, base render hashes, three trace hashes, malformed fallback count and clean logs.

The saved base report SHA256 `5b69823ff3acca2f1ab6241c4de9c3f2be2c0c94b78d366249f51fe3955173d2` matches the exact base `game/scripts/battle_arena.gd` Git blob. Final manifest: `outputs/csp-typed-v02_20261018-171817-b62803cf/rpg-2-star-ocean-the-second_combat-set-pilot_capture-manifest_20261018-171908-a4e51160.json`. Its source hashes use **sha256-text-lf-v1**, avoiding Windows checkout line-ending mismatches. Captures and PNG fixtures use raw SHA256.

## Actual visual inspection

Codex viewed the final female action-mix English capture and mirrored dodge/defeat Chinese capture. Diagnostic body colors, facing, ground ticks, left-facing mirroring and fallen Liang appear in the expected battle positions. HUD text remains readable. Floating TEST/frame labels are intentional fixture annotations, not scene content. These still images do not demonstrate artistic fluidity.

## Reproduction

Use Godot 4.7.2, import the project first, and redirect APPDATA and LOCALAPPDATA to a new isolated temporary profile. Do not use the real preferences/save folder.

Run `game/tests/rpg-2-star-ocean-the-second_combat-sprite-set_pilot-check-capture_v01_20261018-153656-9efd4413.gd` with `--headless -- --no-capture` for logic, or windowed `--resolution 640x360 -- --capture-dir=<new absolute dir> --baseline-dir=<repo>/outputs/combat-set-pilot-v01_21e56480` for captures. The test itself must be launched without the pilot CLI flag; it controls the opt-in override per case.

Run `tools/rpg-2-star-ocean-the-second_combat-sprite-set_evidence-check_v02_20261018-171937-e88cf5bf.py` to verify this exact evidence package. Run the synthetic fixture builder with `--check` for deterministic source reproduction. Technical completion is ready for root inspection and serialized integration; creator art approval, other content tasks and progress-ledger changes are outside this commit.
