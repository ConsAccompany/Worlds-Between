# Heya display (content.char.heya.display) — targeted render QA, batch179 — UNAPPROVED

Run `20261024-154240-h179d001`. Status: **technical validation PASS; human art approval = false; coordinator commit pending**.

Derived deterministically from the committed native south static:

- source PNG `game/assets/characters/heya-native-v01/south/rpg-2-star-ocean-the-second_heya_south-static_unapproved-v01_20261024-125310-231d2b03.png`
  (80×112 RGBA, file SHA-256 `f6e60682…55d2c3`, raw-RGBA SHA-256 `59e322f0…145d65`), source commit
  `dc8ad3b4cff0ac375a00dee3b46ab8135e27e80f` (`content.char.heya.static-south`, done).
- transform: exact integer 2× nearest-neighbour pixel replication, no repaint / no new pixels / no new colours.
- output `game/assets/portraits/hdisplay179/rpg-2-star-ocean-the-second_heya_display-portrait_v01_20261024-154240-h179d001.png`
  (160×224 RGBA, 10 960 opaque texels, raw-RGBA SHA-256 `9c3694a7…84ec04`).

| Check | Result |
|---|---|
| Builder `build` / `check` | PASS (`HDISPLAY179_BUILD OK`) |
| Independent contract checker | PASS: 44/44 checks; 3 built-in negative fixtures refused |
| Malformed negative controls | PASS: 21/21 cases, 0 fails (including tampered pixel, shifted pixels, wrong actor/hash/factor/commit, approved status, missing blocks, palette/PXO pins, truncated JSON, report-overwrite refusal, builder check) |
| Godot `--import` (checked runner, headless, Dummy audio, project-local XDG) | PASS (exit 0, 6.1 s) |
| Probe headless en / zh | PASS: 61/61 checks each |
| Probe Xvfb en / zh with captures (llvmpipe GL) | PASS: 70/70 checks each |
| Portrait pixels in capture | 10 960/10 960 opaque texels exact at (26,69); transparent corner shows card background |
| Actor (south static, 0.5×) | inside stage; 683 differing px vs 685 expected; control corner 0 |
| Fallback (missing portrait) | localized "Portrait unavailable" / "展示图缺失" label, static source still bound, no engine error |
| M1 normal-game smoke (`res://tests/m1_smoke.gd`) | PASS (`M1_SMOKE_OK`) |
| Shared tracked game/tools defaults modified | none; all writes are new untracked paths |

The opt-in standalone scene is `game/scenes/hdisplay179/rpg-2-star-ocean-the-second_heya_display-preview_standalone-v01_20261024-154240-h179d001.tscn`
with script `game/scripts/hdisplay179/rpg-2-star-ocean-the-second_heya_display-preview_standalone-v01_20261024-154240-h179d001.gd`.
It uses the same 180×250 portrait frame / 160×224 image rect, nearest filtering, keep-aspect-centred, 0.5× static
actor stage and localized fallback as the Yanke/Muxiu/Lin Que precedent. It is not attached to any ordinary flow,
party, exploration, battle, save or default.

Captures (`outputs/hdisplay179/captures/`):

- `…preview-capture_standalone-en-south-static_20261024-154240-h179d001.png`
- `…preview-capture_standalone-zh-south-static_20261024-154240-h179d001.png`
- `…preview-capture_fallback-missing-portrait-en_20261024-154240-h179d001.png`
- `…preview-capture_fallback-missing-portrait-zh_20261024-154240-h179d001.png`

Agent visual read: the portrait is left, the identity stack (name / Clinician · 44 / Bible visual anchors) is clear
of the portrait and the actor stage, the CJK text renders, the 0.5× south static is centred in the stage, and the
"Art pending / 美术待定" badge is visible. The fallback capture shows the localized missing-portrait label with the
actor still bound. This is not human art approval.

## Preserved failed checks (fixed, not hidden)

1. First contract run failed `output.opaque-texels` (declared 2 740 source texels instead of 10 960 replicated output
   texels). Fixed in the checker; failed report/log kept at `outputs/hdisplay179/contract/` and `contract.log`.
2. First malformed run failed `wrong-editable-palette.refused` because the contract checker did not yet validate the
   palette pin. Added the palette check; failed report/log kept at `outputs/hdisplay179/malformed/` and `malformed.log`.
3. First Godot import failed with `ERROR: Cannot save file '/home/kel/.config/godot/editor_settings-4.7.tres'`
   (default profile not writable in this sandbox). Retried with project-local XDG dirs; failed log kept at
   `outputs/hdisplay179/import.runner.log` / `import.execution.log`.
4. First headless English probe failed `identity clear of actor stage: identity` (the long anchor line reached x=419
   while the stage starts at x=404). Shortened "low at the nape" to "low at nape" (still the Bible anchor); failed
   log kept at `outputs/hdisplay179/probe-headless-en.runner.log` / `probe-headless-en.log`.

## Limitations

Human art approval is false. No motion/idle/walk claim, no default adoption, no party/exploration/battle/save wiring,
no ledger/Bible/registry/score/index/commit/push change. The source static itself remains unapproved. Rendering used
llvmpipe software GL under Xvfb (a V-Sync WARNING is non-fatal). The `.png.import` and `.gd.uid` files are generated
by the editor import and are not part of the proposed commit. The coordinator must re-hash staged blobs. Full
commands and hashes are in `provider-receipt.json`.
