# WEST source: actual browser-editor Save As and fresh reopen

Codex performed this operation in the official Pixelorama 1.2.3 browser editor on 2026-10-18, approximately 22:47–22:55 UTC. This supplements the produced WEST run source; no new production points, art approval, full character completion or desktop GUI reliability are claimed.

## Actual application operation

1. Opened the committed 128-frame source through File > Open.
2. Used the application's Save As dialog and downloaded a separate uniquely named PXO. The browser appended a second `.pxo`; the preserved project copy has one extension and identical downloaded bytes.
3. Closed the editor. In a fresh application instance, canceled session restoration and used File > Open to load the downloaded copy.
4. Selected the final frame. The actual UI displayed **128/128**, **80×112** and **70 FPS**, with the loaded layered character visible.

Ctrl+O did not perform the required application import; the File menu route did. Startup Splash/RestoreSession exclusive-child diagnostics were observed and retained. No later import/save error was observed. This does not establish clean application diagnostics or Windows desktop Save As reliability.

## Source-bound comparison

- Original SHA256: `3a16204285aa5dacd5cbd19fe00a886c4cc9dea6b8fd16b6e6f6202978618c18`.
- Saved SHA256: `b4bff32ecbbe495346e2b31223ad144d36e9129c92d59f7457fed2a9973a6a1a`.
- Both archives contain 128 frames and 13 layers; all **1,664 raw layer cells** match, including the hidden guide cells. Dimensions, frame durations, FPS, layer properties and author fields match.
- Save As changed export directory/name and normalized an opaque tag color from RGB to RGBA with alpha `ff`. Other semantic metadata matched. The derived preview thumbnail changed and is outside the cell-pixel equality claim.
- Raw file paths and author values are deliberately omitted from published reports.

## Evidence

- Source: `outputs/female-west-run-stop-v01/rpg-2-star-ocean-the-second_female-west-run_animated-source_unapproved-v01_20261018-182900-0817f0b2.pxo`.
- Saved copy: `outputs/pixelorama-gui-west-v01/rpg-2-star-ocean-the-second_female-west-run_web-gui-saveas-reopen_v01_20261018-184756-df07c82b.pxo`.
- Integrity report: `outputs/pixelorama-gui-west-v01/rpg-2-star-ocean-the-second_female-west-run_web-gui-saveas-integrity_v01_20261018-184756-df07c82b.json`.
- Fresh-reopen screenshot: `outputs/pixelorama-gui-west-v01/rpg-2-star-ocean-the-second_female-west-run_web-gui-fresh-reopen-frame128_v01_20261018-185456-3ea1c254.jpg`.

Idle ORA diagnostic failures and unverified desktop operations remain separate open limitations.

## Integrated reusable checker closeout

Selected producer commit `d682c6961e493c841d2941633d76193bee6fc167` was integrated as `14639cd`. Root independently reran the actual pair in the canonical checkout: PASS, all1,664 raw cells and1,664 index payloads equal, no unexpected semantic differences. Root also independently ran the final54-case suite:54passed/0failed, including the386-character Windows path and private-key/truncated-PNG/illegal-filter regressions. The temporary fixtures were removed by the test runner.

The initial checker missed two independently reproduced defects; they were corrected before acceptance, and a further illegal-PNG-filter guard was added. Intermediate50/50 and53/53 results are retained in the package QA and are not the final proof. No production or approval points were added for this supporting operation.

Package: `outputs/pxo-saveas-integrity-v01_20261018-190126-ebf0a394/`. Its reusable command, supported PXO7/RGBA8 pixel-layer scope, report and limitations are in `rpg-2-star-ocean-the-second_pxo-saveas-integrity-qa_v01_20261018-190126-ebf0a394.md`. This file check complements the actual GUI operation; it does not replace it.
