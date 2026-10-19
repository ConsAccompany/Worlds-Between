# Existing Sentry v2: independent editable-package inspection

Scope: close the **unscored editability gap** for the existing v2 candidate. This is not new enemy art, a new motion revision, runtime adoption or creator approval. No production points or acceptance counters change. Producer: DeepSeek; independent archive/pixel/source inspection: Codex.

## Verified package

Only the ten verified producer files were copied to `game/assets/enemies/sentry-editable-v01/`: one builder, one PXO, one unchanged strip PNG, six representative ORAs and one manifest. All ten canonical copies are byte-identical to the producer files.

Independent checker: `tools/rpg-2-star-ocean-the-second_sentry_native-independent-check_v01_20261019-220550-2b708970.py`.

**990/990 checks passed**, independently reading archive headers, metadata and cel bytes rather than accepting producer self-check booleans:

- PXO v7, Pixelorama 1.2.3 schema, 112 × 62, **21 frames**, 12 FPS and six editable normal-blend, unclipped, visible paint roles: legs, mechanisms, body, claw, eye and impact. No flattened-frame layer or new cel is substituted.
- Every RGBA cel has binary alpha and its source pixels belong to its named role. The checker independently reconstructs topmost visible ownership from the existing v2 author's Part geometry using vectorized interior/four-neighbor outline masks; explicit existing spark pixels belong to impact. The role masks are disjoint and cover every original opaque pixel exactly.
- Every reconstructed frame equals the existing `ffefdc6f` v2 frame PNG and strip cell pixel-for-pixel. The copied strip is also byte-identical to the old strip. No new pixels, recolor, resampling or shadow was introduced.
- Pivot `[46,60]`, ground-contact row 60, body center x64 and all six one-based tag ranges match the existing source.
- Native durations preserve the source timing: idle 0.22 s, strike 0.15 s, hit 0.12 s, defeat 0.16 s. Move (59 ms) and windup (240 ms) are explicitly **linearized editor previews** from the old preview sequence; runtime movement remains distance-driven at one cel per four pixels and windup remains progress-driven. Hold-last defeat remains runtime behavior; no 22nd frame is invented.
- Six ORAs independently preserve all six role layers and exact source composites for idle0, move4, windup12, strike14, hit16 and defeat20. Archive normal compositing, opacity, visibility and origins are checked.
- All nine non-manifest binary/source artifacts rebuild byte-identically in a fresh ignored peer. The full manifest is **not** byte-deterministic: `createdAtUtc`, builder/helper provenance paths and package directory change with time/location. Excluding only these four disclosed administrative fields, the rebuilt manifest is identical. These exclusions do not include pixels, timing, hashes, flags, tags, roles or source data.

## Source lineage and preserved failed inspection

The first strict inspection passed 985/989 checks and failed four source-hash/rebuild bindings. The producer used the exact LF source-manifest bytes, SHA `ac40a43ec023e9164d1405a5fd5e5d668b63491296e2e88319f5cb3532223d13`; the canonical working copy is a CRLF checkout, raw SHA `6c59a5d12f943e427b82d1aaf12f923b1255d44831b6ba5ceb0a34bae1f62f5c`. The canonical **Git blob** is the producer's exact LF bytes. Converting only CRLF to LF reproduces that blob byte-for-byte, and the JSON content is unchanged.

The corrected inspection binds native provenance to the canonical Git blob, records both raw working/Git hashes and verifies this exact line-ending bridge. Rebuild uses an ignored snapshot containing the exact source-manifest Git blob and unchanged source PNG/author bytes; **the existing canonical legacy file is not edited**. The first failed report remains `outputs/sentry-editable-v01/rpg-2-star-ocean-the-second_sentry_native-first-failed-report_v01_20261019-220550-2b708970.json`; no pixel or artistic threshold was relaxed.

An earlier harness invocation used an extended-prefix script argument while the builder's provenance calculation mixed drive-path forms, so the rebuild did not complete; the checker then incorrectly attempted to read absent rebuild artifacts. The bounded harness correction uses an ordinary short script argument while retaining extended-length source reads/writes, and guards missing artifact reads. This did not modify producer source or any package bytes.

The old v2 author intentionally imports the earlier **static** v01 palette/compositor. That dependency is preserved; it is not an animation-v1/v3 mix. Inspection/rebuild consumes only the v2 manifest, v2 author, v2 frames/strip, its static source/palette dependency and the existing format helper. No animation-v1 or animation-v3 input is used. The historical producer-location paths in the manifest remain a frozen provenance record.

## Evidence and limitations

- Final independent report: `outputs/sentry-editable-v01/rpg-2-star-ocean-the-second_sentry_native-independent-report_v01_20261019-220550-2b708970.json`.
- Ten-file copy, checker and report raw hashes: `outputs/sentry-editable-v01/rpg-2-star-ocean-the-second_sentry_native-copy-source-proof_v01_20261019-220550-2b708970.json`.

No native Pixelorama application launch, application export, editor playback, or GUI Save As/reopen was inspected. Archive/schema and exact-composite checks establish the editable package's structural/pixel provenance, not application reliability. Layers contain only the visible source raster; geometry already overwritten by another part cannot be recovered without inventing art. A contact shadow absent from the existing author/frames is not invented; the sixth semantic role contains the existing impact sparks instead.

The accepted action-direction scope is unchanged. Runtime defaults, art acceptance, motion approval, character counts, scene counts, ledger, index, Git and private Site were not changed by this inspection.
