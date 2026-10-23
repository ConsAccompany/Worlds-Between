# Lin Que display production closeout (art unapproved)

Task: content.char.lin-que.display. Claude is the producer through the authorized run-provider adapter; Hermes independently inspects and integrates. Tested base: 92efd6bbfb200ca03407f0c4904a970a05520ea9. Only the existing two-point display criterion is eligible: image committed and shown in UI. No runtime-integration, visual-review, creator-approval or human-playtest credit.

## Deliverable and source

Reuses the credited Jiang Lan display40 pipeline: deterministic crop, manifest, standalone bilingual opt-in character display scene and existing exploration pilot. This is not linked to ordinary gameplay. The original concept stays unapproved; no new/repainted/resampled pixels or native-source claim is made. Existing native south static is the already-completed dependency, not new credit here.

Source: outputs/rpg-2-star-ocean-the-second_lin-que_character-sheet_v01_20261013-153556-88b92720.png; SHA-256 24007e147c9dd67b330af4a84ac13054f65989cddb9bdf2702dc5c80de7fb352. Rectangle (16,0,592,800), right/bottom exclusive, yields 576x800. Crop SHA-256 9f755bcb4fde08b149a8153ac8572fa72ca3d3112126648012246921d60d320f; decoded RGBA SHA-256 7d8bbb214bb6e8780e26622a0acda37b8d35dd30c0c2dfadd561ab07ba3ab333. All file hashes are raw bytes, no normalization.

Scene: game/scenes/ldisplay64/rpg-2-star-ocean-the-second_lin-que_display-preview_standalone-v01_20261023-214513-92b6d62b.tscn. Portrait/source manifest: game/assets/portraits/ldisplay64/. Game/script source remains scoped to ldisplay64; existing pilot temporarily receives a preview override, then restores its static override values. No ordinary defaults, story, recruitment, save or party changes. Hermes compared all 5106 pre-existing tracked game files with HEAD raw blobs: zero differences.

## Independent verification

Exact commands, tested source hashes, 18 capture hashes and command exits are recorded in outputs/ldisplay64/hermes6/rpg-2-star-ocean-the-second_lin-que_display-independent-proof_v01_20261023-214513-92b6d62b.json.

- Deterministic crop check: LDISPLAY64_CROP OK, pinned source and exact pixels.
- Independent coordinator rerun of producer contract checker: 21 checks PASS, three built-in negative fixtures refused (wrong hash, actor, out-of-bounds crop).
- Malformed-input gate: 10 predicates, zero failures, LDISPLAY64_MALFORMED_OK. Shifted rectangle, other actor, Jiang manifest, truncated JSON and tampered pixel are rejected; absent manifest is explicitly PENDING. The tamper case tests the contract checker, NOT a tampered builder invocation despite the helper docstring wording.
- Checked Godot import: PASS.
- Real Xvfb OpenGL EN and ZH probes: each 117 checks, zero failures, BINDING pilot, CAPTURES true, LDISPLAY64_PROBE_OK. Nine actual 640x360 captures per language include all four facings/idle/walk plus localized missing-portrait fallback. Missing portrait and forced manual-viewer checks pass, including exact first-frame and cycle-wrap microsecond boundaries.
- Actor render test compares sprite on-screen bounds against the stage background, requires meaningful opaque-pixel evidence and a clean empty-stage control; not merely a differently colored background panel.
- Checked normal-entry M1 smoke: M1_SMOKE_OK, no diagnostics.
- Hermes directly viewed independent EN and ZH south-idle PNGs: complete head, weapon, boots and cape visible; identity text clear of portrait/stage; Lin Que / 林阙 and age22 localized correctly; sprite visible; Art pending / 美术待定 explicit. This is display verification, not artistic acceptance.

All Godot commands use the repository checked runner, finite deadlines and Dummy audio. Current project settings are untouched; captures explicitly request 640x360 as the established display precedent. Independent source hashes remained unchanged throughout checks. Staged raw-byte verification is required before publication.

## Reproduction

From repo, use ../tooling/venv/bin/python (do not resolve its symlink to the system Python). Run tools/rpg-2-star-ocean-the-second_lin-que_display-crop-build_v01_20261023-214513-92b6d62b.py check, then the matching display-contract-check with --root . --manifest game/assets/portraits/ldisplay64/rpg-2-star-ocean-the-second_lin-que_display-portrait-manifest_v01_20261023-214513-92b6d62b.json --out <new scoped output>. Run display-malformed-check with --out <new scoped output>.

Launch the existing checked runner with --timeout 90 --expect LDISPLAY64_PROBE_OK --expect 'CAPTURES true' --log <new log> -- followed by Godot --audio-driver Dummy --rendering-driver opengl3 --resolution 640x360 --path game --script <absolute tools/rpg-2-star-ocean-the-second_lin-que_display-preview-probe_v01_20261023-214513-92b6d62b.gd> -- --lang=en|zh --out=<existing capture directory>. Wrap the invocation in xvfb-run -a. The independent proof records full executable paths and exact tested commands.

## Failures retained and limits

Batch4 stopped on coordinator usage retrieval timeout, leaving only scratch/cand.png. Batch6 provider1 stopped at max_turns, not depletion. Provider2 and3 had successful process exits but adapter classifications permission_denied from denied shell commands; these are not clean adapter successes. Their actual files were inspected and tests independently rerun; adapter status does not substitute for completion evidence. Private adapter/account logs stay outside Git. No fallback billing or DeepSeek invocation occurred.

Producer qa1/build.log, check.log and malformed.log retain ModuleNotFoundError: No module named 'PIL': its orchestration resolved the virtual-environment executable to the system Python. Producer corrected that in qa2; Hermes used the actual virtual-environment path and independently passed. No failed logs are erased. Producer earlier checker/probe work was incomplete at max-turns; only final independent source hashes define the tested candidate.

Single fixed-position preview and sampled walk frames do not establish continuous normal-speed motion quality, stop-bridge integration, foot lock or full runtime-set inspection. Existing native-app/shader/animated GUI limitations from lexplore59 remain open. Lin Que ordinary runtime defaults remain unauthorized/unchanged. Creator acceptance and both timed human playtests remain separate. No Site deployment claimed.

## Progress and next action

Starting canonical production61.0%, inspection21.6%, approval7.8%. Only the existing display task may be marked done after its source commit; final exact before/after values and source commit are captured by the canonical progress recorder. No new tasks, weights, denominator changes or review points. Next: select an existing eligible unfinished production item; do not adopt Lin Que defaults without the creator gate. Final art review remains creator-owned.
