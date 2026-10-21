# Heroine breathing idle in the ordinary game

Owner/integration: Codex. Source production: Claude Max. Creator canceled the DeepSeek takeover; Codex remains coordinator.

## Delivered

- Four direction-specific8-sample breathing clips,2400ms per cycle, bound to the current front17 heroine.
- Exact original neutral PNG bytes at both endpoints. Lower body from source row56 down is exact; head identity translates by one source pixel in the inhale samples. No new palette colors or partial alpha.
- Editable per-direction8-frame PXO and peak-pose ORA, plus deterministic author tool. The original front17 assets, walk/stop bridges, locomotion model, scene hosts, battle host and default policy bytes/content remain protected.
- Separate presentation clock resets to neutral on movement, facing changes, teleport and settle completion. It never moves the actor or changes movement/collision/attack rules.
- The current source profile requires the pinned idle manifest and every frame hash. Missing supplement rejects the whole ordinary heroine package and preserves the legacy fallback.

## Evidence

- [Source-bound root proof](../../outputs/idle21/rpg-2-star-ocean-the-second_heroine-breathing-idle_root-closeout-proof_v01_20261021-152533-405ccef9.json) lists all changed-source hashes and actual evidence paths.
-77timing checks at30/60fps and mixed boundaries;122default/explicit parity and override checks.
- Actual city English30fps capture:41checks. Actual ruins Chinese60fps capture:36checks. Both verify fixed stationary positions, all four facings, unchanged transform and immediate actual movement interrupt.
- Normal-game English all8combat states:149checks. Chinese natural victory/return/reload:124checks.
- Missing idle manifest:6fallback checks; fixture restored byte-exact before any subsequent work.
- Template-free169,195,728-byte PCK exported with the existing raw-input hook and launched from an initially empty directory. The same122runtime parity/override checks passed against packed resources. See `outputs/idle21/rpg-2-star-ocean-the-second_heroine-breathing-idle_packed-runtime-proof_v01_20261021-152750-38f4f863.json`. No native EXE is delivered by this check.
- All41authored package files rebuilt byte-exact before Godot generated import sidecars. The author tool's strict verify mode targets this authored snapshot; engine-generated sidecars are outside that41-file snapshot.
-16Pixelorama pixel-export comparisons passed. Unchanged committed native control reproduces the headless shader diagnostic. Application diagnostics are not clean and GUI save/reopen was not verified.

## Failed checks and limits

The initial city capture fixture was placed inside an existing obstacle. Two movement-interruption assertions failed while collision correctly blocked movement. The fixture was moved to a verified clear center, and explicit cardinal-clearance/actual-displacement checks were added. Game collision and assertions were preserved; the failed report/log remain available.

An initial independent crop check assumed a completely static head. The stated source contract allows a coherent one-source-pixel head rise; the final check verifies the exact translated head pixels and fixed lower body. This does not certify full fluidity. Hair/scarf follow-through and the dropped neck/scarf row remain visible-method limitations.

Source poses and actual neutral/inhale gameplay frames were inspected. Normal-speed movies are provided; complete continuous motion quality and artistic acceptance remain pending. No full sprite approval or human playtest is recorded.

The first staged-byte gate also caught CRLF normalization of newly generated combined-path JSON evidence. Timestamp-scoped `-text whitespace=cr-at-eol` preserves those exact tested bytes while retaining other whitespace checks. All selected files are compared with staged Git blobs before commit.

## Progress and publication

Production54.6% →54.6%(+0.0pp), inspection18.1% →18.1%(+0.0pp), creator approval7.8% →7.8%(+0.0pp). Idle already had production credit; another version earns no extra points.

Repository Bible/registry and selected source/evidence are updated. The existing Sites project could not be found through the current connector, and its site list was empty. No replacement site, access change or successful live publication is claimed.
