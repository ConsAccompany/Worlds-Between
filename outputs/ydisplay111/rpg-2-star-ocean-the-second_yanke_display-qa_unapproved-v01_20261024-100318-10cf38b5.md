# Yanke display (content.char.yanke.display) — targeted render QA, batch111 — UNAPPROVED

Run 20261024-100318-10cf38b5. Status: **technical validation PASS; human art approval = false**.

| Check | Result |
|---|---|
| Godot `--import` (checked runner, headless, Dummy audio) | PASS (exit 0, 3.6 s) |
| Probe headless en / zh | PASS: 57/57 checks each |
| Probe Xvfb en / zh with captures (llvmpipe GL) | PASS: 66/66 checks each |
| Portrait pixels in capture | 15872/15872 opaque texels exact at (26,69); transparent corner shows card bg |
| Actor (south static, 0.5x) | inside stage; 995 differing px vs 992 expected; control corner 0 |
| Fallback (missing portrait) | localized label shown, static source still bound, no engine error |
| Contract / malformed (prior a1 reports) | real manifest PASS; all malformed fixtures rejected |
| Tracked game/tools files modified | none |

Captures (outputs/ydisplay111/a1/):
- `…preview-capture_standalone-en-south-static_…png`, `…standalone-zh-south-static_…png`
- `…preview-capture_fallback-missing-portrait-en_…png`, `…fallback-missing-portrait-zh_…png`

Agent visual read: the layout has no overlaps, the CJK text renders, and the "Art pending / 美术待定" badge is visible. This is not art approval.

Limitations: the profile was not isolated with separate XDG/TMPDIR directories (that compound command was denied in attempt112 and was not retried). Only a V-Sync WARNING appears under Xvfb. Details, hashes and rerun commands are in `provider-receipt.json`.
