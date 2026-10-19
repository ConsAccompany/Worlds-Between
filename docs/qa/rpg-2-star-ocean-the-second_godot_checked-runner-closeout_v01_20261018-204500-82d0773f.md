# Bounded Godot runner — incident fix

The first NORTH native bake encountered compiler errors in a loaded dependency. Its SceneTree stayed alive, leaving the CLI waiting after the error was already known. Root identified the exact failing bake command and stopped only its console/engine processes. The corrected producer prototype later passed14/14 and547/547 small checks; its remaining artistic/contact issues are separate.

Added a reusable runner with a finite deadline, explicit error-marker detection (including ANSI-coloured errors), nonzero-exit and required-marker gates, preserved unique logs and owned-process termination. It rejects zero/negative/NaN/infinite deadlines and refuses to overwrite evidence logs. It leaves unrelated applications untouched. This is not a sandbox for hostile or deliberately escaped descendants; it controls ordinary owned test trees.

Verification: **10/10 targeted regression cases** passed, including compiler-error+hang, partial-line timeout, zero-exit error, missing marker, nonzero marker, unrelated process preservation and exclusive logs. An actual Godot inner-load parse-error reproduction was independently stopped as diagnostic failure in **1.219 seconds**, rather than waiting for the10second deadline. It is a successful failure-detection test, not a successful game feature test.

Source-bound report: `outputs/rpg-2-star-ocean-the-second_godot_checked-runner-regression-report_v01_20261018-204000-034fc98d.json`. Both tool and regression source hashes are LF-normalized in that report. No runtime defaults, content score, inspection score or creator acceptance changed.
