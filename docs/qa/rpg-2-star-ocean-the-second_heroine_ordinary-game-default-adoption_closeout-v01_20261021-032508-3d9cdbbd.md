# Heroine ordinary-game default adoption

Creator authorization in this chat: “设为女主默认显示” (2026-10-21 UTC). This authorizes ordinary-game default use of the existing four-direction exploration and eight-action combat set. It is NOT full art, animation quality, roster, environment or human-playtest acceptance.

Before production54.5%; inspection17.2%; creator7.8%. Base321b3c55c139c982e8a9a94d7a6ab222f205496f. Source assets unchanged.

## Implementation
- Adopted the reviewed isolated source-selection policy for female heroine only. No opt-in flags or overrides are needed in ordinary female play. Male, other actors, explicit disabled/alternate selectors stay on their prior paths.
- Front17 four-direction exploration retains current anchors, scale, distance phases and phase-aware stop/repress/reversal. Current29-pose combat set retains source-bound contact and recovery.
- Whole pinned package refusal keeps legacy exploration art and legacy immediate combat contact. Do not draw legacy sprites under the heroine contact clock.
- The already-fixed .3s visible defeat presentation also applies to this newly adopted default; the2.0s return timer and gameplay rules remain unchanged.
- The existing shared setup/checker now accepts --normal-default and records whether adoption is active. It asserts all exploration, registry, combat, index and contact overrides remain unset and no runtime pilot CLI flags are supplied. Normal gameplay uses the same AppState female choice/destination entry.
- Immutable source package metadata still describes its original unapproved/nondefault authoring state. The authorized runtime policy and Bible record present default adoption separately, without changing source bytes/art approval.

## Evidence and limitations
All combined final runs passed with diagnostics fatal. Source assets unchanged.
- Canonical source-selection/fallback fixture:38 predicates across female/male/disabled/missing; contact placement is explicitly synthetic. Actual full input routes are separate.
- Bilingual normal-input actions:133 checks/language,840 frames at30fps, original1x28s; all8 source actions. No forced HP/energy/AI/pose/damage/finish.
- Existing four-direction physical stop, stop phase, same-direction repress, reversal, normal encounter, safe return and reload checks reused.
- Full artistic fluidity still unapproved; sampled visual review asks for stronger dodge/skill body articulation.

## Retained failures
- Added harness assertion initially used PackedStringArray.all, which Godot does not implement. Checked runner stopped on parse error; converted to Array before all().
- A missing-file fixture was mistakenly run alongside the normal victory checker. Its temporary phase-PNG removal caused the policy to refuse the package and the checker to fail; no assertion was weakened. The PNG was restored byte-exact; destructive fixture completed before serial victory/defeat reruns. This is a test-coordination failure, not evidence of a normal-game defect. Future package-mutation fixtures must run exclusively.
- No engine ERROR suppression, quota retries, cloud credits or paid fallback.

Final current-source proofs:
- actions: outputs/heroine-actions18/rpg-2-star-ocean-the-second_heroine-playable-path_combined-root-proof_v16_20261021-032317-978801e5.json; [('en', 133), ('zh', 133)]
- victory: outputs/heroine-actions18/rpg-2-star-ocean-the-second_heroine-playable-path_combined-root-proof_v16_20261021-032435-d1dc9817.json; [('en', 108), ('zh', 108)]
- defeat: outputs/heroine-actions18/rpg-2-star-ocean-the-second_heroine-playable-path_combined-root-proof_v16_20261021-032458-eae68d08.json; [('en', 98), ('zh', 98)]

Source integration commit d41e91fa2fb2eaa03dd4b0037cd1b00409ce0df7. Selected92 staged files match exact working bytes. Creator approval is default-use only; no accepted-sprite counter increased.

Closeout meters: production54.5→54.6 (+0.1pp); inspection17.2→17.6 (+0.4pp); creator7.8→7.8 (+0.0pp). Default integration4 existing points and1 existing technical-inspection point earned; no art approval counter changed.

Private Bible v60 published and live-verified: before/after54.5→54.6, inspection17.6, creator7.8; current default heroine movie readyState4,28s,1280x720,rate1 with no media error. Verification: outputs/heroine-default18/rpg-2-star-ocean-the-second_tracker_default-adoption-live-verification_v60_20261021-032952-529bab8e.json.
