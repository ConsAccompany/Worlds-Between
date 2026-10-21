# Heroine normal-input and visible-defeat closeout

Task: support.heroine.normal-input-default-candidate. Before production54.5%, inspection16.7% (34/204), creator7.8% (19/244). Base124a275927b1cf69cfab50f1bac4354364cc5b23. Complete heroine remains opt-in pending the separate default-use decision.

## Delivered and independently checked

- DeepSeek extended the existing reusable flow/runner/CLI with --scenario actions; Codex reviewed and merged it, preserving existing victory/defeat checks and source bindings.
- Codex reproduced a presentation bug: the opaque loss overlay hid all three authored defeat poses. Two assertions failed before the fix. The result now waits for the actual .3s source clip; the existing2.0s menu-return timer, HP, damage, rewards, save rules and AI are unchanged.
- Actual-input EN+ZH actions route:129 checks each, all8 source states observed. Guard cost6/reduced damage4, dodge cost12/avoided hit, personal skill cost12/cooldown set. One normal attack leaves the enemy alive; normal AI causes hit/defeat, followed by normal menu and pre-battle retry. No forced pose/HP/energy/damage/cooldown/AI/finish calls.
- Root proof: outputs/heroine-actions18/rpg-2-star-ocean-the-second_heroine-playable-path_combined-root-proof_v16_20261021-031211-ae1bc851.json. Both original1x MP4s are840 frames/30fps=28.0s,1280x720. AVI frame count retained, no time rescale.
- Root defeat-only regression:94 checks/language, proof outputs/heroine-actions18/rpg-2-star-ocean-the-second_heroine-playable-path_combined-root-proof_v16_20261021-031859-cf230e36.json.
- Root victory regression:104 checks/language, proof outputs/heroine-actions18/rpg-2-star-ocean-the-second_heroine-playable-path_combined-root-proof_v16_20261021-031839-f770b7d5.json.
- Exact-boundary synthetic unit fixture:14 predicates, current real heroine clip0/.1/.2/.3s, male/disabled/alive/missing/other-set exclusions. Unit fixture, not normal gameplay.
- Claude prepared ordinary-game source selection in its isolated checkout. Codex merged the presentation fix into that candidate and checked female, male, explicit disable/contact semantics and missing phase-PNG whole-package fallback:15+6+11+6=38 predicates. Synchronous contact tests use disclosed fixture placement/calls; they are not normal-input evidence. Candidate sources/patch: outputs/heroine-default18/prepared-20261021-031817-59b2296f/rpg-2-star-ocean-the-second_heroine-default18_prepared-source-manifest_v01_20261021-031817-59b2296f.json. Canonical defaults remain unchanged.

## Inspection verdict: changes requested for artistic motion; technical candidate usable

Codex inspected actual PNGs and samples of all8 states extracted from the original movie, plus live browser playback excerpts at rate1.0. Sampled visual inspection, not uninterrupted frame-by-frame viewing or creator acceptance. Attack visibly extends the blade toward the enemy; guard raises the blade; skill has a small outward wrist/blade gesture; hit turns/compresses the torso; defeat ends in a clear kneel before the overlay. Identity, teal scarf, boots and ground scale remain consistent.

Remaining observable art issue: dodge retains a near-idle upright silhouette while translating backward; skill changes the wrist/blade much more than the torso. These need stronger authored body poses before claiming the creator's smooth/fluid/well-paced standard. No full art approval or human playtest inferred. Sample manifest: outputs/heroine-actions18/review-20261021-031659-120b1001/rpg-2-star-ocean-the-second_heroine-actions18_sampled-review-manifest_v01_20261021-031659-120b1001.json.

## Failures and corrections retained

- Before-fix normal loss failed exactly the two visible-defeat checks; source fix, not a changed threshold, resolved them.
- Producer first action route observed7/8: skill input arrived while the loader still prioritized dodge. Waiting for the actual dodge state to finish before pressing skill resolved the missing observation.
- Rejected DeepSeek runner changes that suppressed the Godot certificate-store ERROR and tolerated errored imports. Canonical runner has neither filter nor exception; all engine errors remain fatal. Producer logs local only; canonical strict runs passed.
- Initial root default-candidate run refused a missing-sheet resource after producer import-sidecar restoration. Strict native import passed, then all38 candidate predicates passed. Refused run retained locally.
- Claude hit the bounded660s task deadline, not subscription quota. Codex finished candidate validation. Producer future-labelled evidence not published; root-created source/probe/evidence names use actual timestamps.
- No denominator changes or points for version/test counts. Default integration milestones remain in_progress. Artistic acceptance and both timed human playtests remain separate.
