# Patrol animation independent technical review

Reviewed against e600241 baseline; canonical arena at a0107c3 is byte-identical to baseline (SHA256 7f6233522e90e044f4c16ee0a3a39bc066658ea0a01dae38304ee17acb4077c0). The +43/-1 arena diff is a default-off visual hook only. Stats and combat simulation are protected. No creator artistic/motion approval is implied.

## Findings and bounded repairs
- The producer loader accepted existing dot-segment/double-slash JSON paths, existing strip traversal, missing strip SHA and wrong strip SHA. An unfiltered before-fix headless probe demonstrated all five rejected-case predicates false; retained log records expected failure. Added canonical path spelling, strip existence and exact raw PNG SHA validation. After-fix all 6 probe predicates pass.
- Manifest `helperSha256TextLf` correctly refers to its Python native-format helper, not the GDScript loader. An initial reviewer suspicion of stale helper hash was withdrawn after reading the builder. Added explicit loader filename and LF SHA fields without changing the native helper field. Builder deterministically regenerates the manifest and `--check` passes all 10 artifacts; PNG/PXO/ORA/runtime JSON pixels and bytes are unchanged by these repairs.
- Enhanced producer harness adds five malformed-path/hash cases (31 loader predicates total); temporary fixture filenames now follow project naming.

## Independent evidence
- Original unfiltered full harness: sim20, loader26, capture16, parity32; checked-run PASS 11.266s.
- One subsequent windowed attempt failed at GLES shader initialization with ERROR diagnostics before tests. Raw failed log is retained. No diagnostics were filtered, no pass was claimed. A fresh isolated APPDATA/LOCALAPPDATA invocation completed the final windowed run; exact cause of the shader startup failure is not established.
- Final unfiltered full harness: sim20, loader31, capture16, parity32; checked-run PASS 11.672s. All 32 default/Sentry 640x360 images match baseline and all 20 combat hashes match. Two ObjectDB leak warnings remain at fixture exit; not a clean-warning claim. Headless adversarial after-fix PASS 0.578s.
- Builder check 10/10 deterministic artifacts. Source/artifact hashes are in the companion proof. No new native-app run was made; producer separately disclosed Pixelorama 168 exact layer exports, inexact flattened alpha compositing and 10 shader ERROR diagnostics. No clean native-app or GUI reopen claim.

## Boundaries
Six states and 24 frames are produced in editable 7-layer PXO plus representative ORAs. Producer captures use normal battle scene/HUD, but pose captures and the timing loop manipulate fixture state; loop holds HP until two strikes. No MP4 was produced in this original batch. Timing transitions/state screenshots do not establish fluidity. Root is separately arranging real normal-speed evidence. Root must run combined normal-path/PCK integration before readiness acceptance. Default flag remains off and all art remains unapproved. No shared ledger, Bible, Git index or Site was changed by this review.
