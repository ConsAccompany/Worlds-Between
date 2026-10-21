# Current heroine combat set: independent Codex technical verdict

Existing task qa.combat.protagonist-female.set-check. Claude checked85a32e3 and documented docs/qa/rpg-2-star-ocean-the-second_heroine-combat_set-check-qa_root-v01_20261021-005750-5c1e8a47.md. Codex independently reran its unmodified runner against combined production commitaeb49202939f3b0cac58e2264e2e3a8149c2c5d5. Runtime hashes are exact git-archive blobs; no gameplay/animation source change for this inspection.

## Results and retained failures

Root proof:outputs/hsc-v01/20261021-005806-e3795911/rpg-2-star-ocean-the-second_heroine-combat_set-check-proof_root-v01_20261021-005806-e3795911.json. All11 Godot invocations passed their required markers:2imports and9 timing/contact/facing/bonus/scale/input/default-isolation/natural-flow suites.1185 predicate checks, no ERROR/SCRIPT_ERROR. ObjectDB exit-instance warnings and the intentional malformed-exponent warning remain disclosed.

The original combined runner exits1/resultFAIL because its historical package verifier runs inside the deliberately dirty integration checkout.5raw failed predicates:package_file_set(extra generated PNG.import),base_revision(hardcoded11973af),no_tracked_changes,scope_untracked,no_unstaged_tracked_changes. Retain this attempt; do not report a clean aggregate pass.

Codex reran the unmodified verifier in a NEW clean detached worktree ataeb4920, report outside that checkout:outputs/environments-adopt14/rpg-2-star-ocean-the-second_heroine-combat_clean-package-root-check_v01_20261021-005930-83c2e67a.json.570/571pass,exit1,only base_revision fails because it requires historical HEAD11973af. All4committed package files,source cells,pivots,frames,ticks and provenance pass. No original predicate or threshold was removed/rewritten. Current checkout is independently asserted to exactaeb49202939f3b0cac58e2264e2e3a8149c2c5d5; original package provenance remains11973af. Do not claim571/571 or a clean original verifier.

All8 authored actions exist; actual packed-set facing tests cover one-shots and idle/move/guard release. Attack contact/recovery/cancellation are independently exercised. Shared loader tests explicitly use synthetic fixtures, not new art. Normal Input/natural encounter captures are scripted. Their old motion-comparison harness explicitly disables background drawing; environment-default operation is separately proven by72/52checks. No claim those motion screenshots show the new default backdrop.

Codex viewed the actual1280x720 contact frame: heroine blade contact visible,legacy red enemy and old backdrop remain diagnostic context. Static frames cannot establish continuous fluidity.

## Verdict and scope

The existing task's Godot technical-check criterion passes at the pinned combined source. Record technical-pass for that inspection only, retaining the old package verifier's checkout limitation and raw aggregate failure. Visual motion review,full runtime sprites0/52,default heroine adoption and human plays0/2 remain incomplete. No new art production points.
