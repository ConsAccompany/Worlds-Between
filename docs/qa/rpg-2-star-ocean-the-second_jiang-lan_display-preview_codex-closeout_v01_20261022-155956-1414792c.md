# Jiang Lan display image and standalone UI closeout

- Task: `content.char.jiang-lan.display`; Claude producer, DeepSeek independent crop checker, Codex inspection and integration.
- Tested base: `530edeedd1742706794d7e5b517e76715098eedd`; exact source and evidence hashes: repository-relative hash proof is `outputs/jdisplay40/root/rpg-2-star-ocean-the-second_jiang-lan_display-root-hash-proof_v01_20261022-155956-1414792c.json`.
- Deliverable: deterministic 480x630 exact source crop plus a separately launchable 640x360 bilingual display UI; it is not linked to ordinary gameplay. Source identity was previously approved; no new sprite/art/default approval is inferred.
- Source rectangle (0,0,480,630), source 1915x821, SHA bbddf46f3c1370742c86d1934e36adf7969e5f43a4e6d67ddbf9ba8d44902e4a. No repainted, resampled or generated pixels. Output file SHA 0bed68c35c4cf2dcb69248609f91a6f52125285aeec2003122bc1fb886a6d4e4.

## Independently observed result

- Deterministic builder `check` passes. DeepSeek contract checker: 21 checks plus three rejected malformed fixtures (wrong file hash, wrong actor and crop outside source).
- Codex added explicit `file_sha256` schema support to the checker and its wrong-hash mutation. The original failed report and producer checker snapshot remain in `outputs/jdisplay40/root`; the source crop was unchanged.
- Checked Godot import passed. Final fresh-profile EN and ZH windowed probes each pass 47 checks with `BINDING pilot`, zero diagnostics, eight actual 640x360 captures each. Both use the existing exploration pilot at 0.5 scale, with real four-direction buttons and idle/walk toggles.
- Codex viewed actual EN/ZH captures. The first English capture clipped the identity line behind the stage; root shortened/wrapped it and added three text/stage overlap checks. Final image is legible and contains the full head and the cropped source body; it is not a full-body runtime sprite.
- All 2568 protected tracked runtime/data/scene/old Jiang-source files remain byte-identical. No party membership, recruitment, save, story, defaults or shared loader change.

## Failed checks and limits

- Producer's fresh unimported worktree had missing global classes/textures: its two probe iterations are FAILED despite emitted check markers. All four logs are retained. No producer screenshot was claimed.
- Root r2 EN failed OpenGL shader initialization before scene checks. It is retained; unchanged final source passed once in newly isolated profiles (r3) in both languages. This is not a clean-driver-reliability claim.
- The preview has an explicit manual-viewer fallback, but final evidence used `pilot`. Stop-bridge playback, foot lock, fluidity and ordinary Jiang gameplay were not verified by this display task. Previous source limitations remain.
- `content.char.jiang-lan.runtime-integration` remains blocked: the current MVP has no ordinary Jiang host/role. No new story/combat/recruitment scope is inferred. Full art acceptance remains separate.

## Reproduction

Run the display builder with `check`, then the independent checker with `--root . --manifest game/assets/portraits/jiang-display40/rpg-2-star-ocean-the-second_jiang-lan_display-portrait-manifest_v01_20261022-155956-1414792c.json --out <unique-dir>`. Run the Godot probe using the checked runner, native `--resolution 640x360 --rendering-method gl_compatibility`, script `tools/rpg-2-star-ocean-the-second_jiang-lan_display-preview-probe_v01_20261022-155956-1414792c.gd`, and `-- --lang=en|zh --out=<unique-dir>`. Require `JDISPLAY40_PROBE_OK` and `BINDING pilot` with no diagnostic errors.

Progress is recorded by the canonical ledger/recorder after the source commit. Only the existing two-point display task is completed; no additional review or runtime credit.
