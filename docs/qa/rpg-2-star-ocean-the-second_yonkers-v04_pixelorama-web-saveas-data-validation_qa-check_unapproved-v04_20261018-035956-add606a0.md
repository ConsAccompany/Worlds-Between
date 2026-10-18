# Yonkers v04 — Pixelorama web Save As: data validation (QA check, UNAPPROVED)

Date: 2026-10-18 03:59 local. Scope: one data-validation pass only. No art, Pixelorama settings, package or ledger changes. Nothing staged, committed or pushed, and no counters changed.

## Verdict

- **The saved file is VALID and LOSSLESS.** All 13 layers are byte-identical to the original. Names, order, visibility, lock, opacity and blend are unchanged. The composite is pixel-exact.
- **The GUI reopen FAILED.** The reopen screenshot shows a single `untitled` 64×64 tab. No second project tab was created, so the reopen did not load the file. This is a UI/load-path problem, not data loss.

## Inputs

| Role | Path | SHA-256 | Bytes |
|---|---|---|---|
| Original (work copy) | `work/native-save-0340/…_original-layered-v04_20261018-034900-258a9bc1.pxo` | `ed9d605b…7ab5e28` | 112366 |
| Original (git `7370739`, `outputs/yonkers-room1-v04_523bba3b/…material-depth-scene-layers_unapproved-v04_20261018-052445-523bba3b.pxo`, read via `git show`) | — | `ed9d605b…7ab5e28` (identical) | 112366 |
| Web Save As output | `work/native-save-0340/…_pixelorama-web-saveas-v04_20261018-035200-a8d73e65.pxo` | `05c03eb2…220c4ff` | 80504 |

## Container and metadata

- Both files are ZIPs with `mimetype` = `application/x-pixelorama`, `pxo_version` 7, size 640×360, 1 frame and 13 layers. `unzip -t` reports no errors.
- The 13 `layer_N` blobs are 921600 B each (640×360 RGBA), with `indices_layer_N` = `00`. Every raw blob is **byte-equal** between the two files.
- Layer order (bottom→top) is identical: sky-and-ridge, back-parapet-masonry, wall-kit-and-ivy, deck-slabs, walkway-grating-and-trench, deck-detail-cables-moss, cast-shadows, doors-and-side-walls, front-parapet, antenna-a-lattice-yagi, antenna-b-dish, antenna-c-guyed-whip, foreground-occluder. All layers are visible, unlocked, opacity 1, blend 0, parent −1 and type 0.
- `data.json` (8033 → 8234 B): the only semantic differences are valid web-save metadata:
  - `export_profile.directory_path` `""` → `"user://"`. This is the web build's virtual FS.
  - `export_profile.file_name` `yonkers-room1-v04` → the original's long descriptive stem. CLI exports of the saved file are therefore named after that stem.
  - Key `name` (`yonkers-antenna-room1-v03`) moved position in the object. The value is unchanged.
- Size drop 112366 → 80504 B: `preview.png` is now a 256×144 thumbnail (16062 B, was a 640×360 image of 48978 B). The thumbnail is fully opaque and equals the nearest-neighbour downscale of the composite. No layer data was lost.

## Official native CLI (pre-existing tooling, isolated)

- Pixelorama v1.2.3 `work/tooling/pixelorama-1-2-3/Pixelorama-Windows-64bit/Pixelorama.exe` (sha256 `6412014e…4b92f10`).
- Each of the 4 runs (saved/original × split/flat) used `APPDATA` = a fresh temp dir. Inputs and outputs were under `%LOCALAPPDATA%\Temp\pxo-saveas-check-a8d73e65\`.
- Command: `--headless --quit -- --export [--split-layers] -o <tmp>/f.png <file>`.
- Results: all 4 runs exited 0. Each split run wrote 13 PNGs and each flat run wrote 1. Both runs logged the same 4 dummy-renderer shader `ERROR` lines.
- Saved-file split PNGs: 13/13 equal the raw layer bytes. Original split PNGs: 13/13.
- All layers have binary alpha.
- Saved flat equals original flat equals the Pillow alpha-composite of the 13 layers. It also equals the committed CLI flat export `…pixelorama-official-cli-flat-export-640x360_official-v1.2.3_20261018-053800-4be2a917.png` (from `7370739`). Composite RGBA sha256 is `4e59618b…d4dd5590f`.
- Real `%APPDATA%\pixelorama` before/after: one change, `backups/2026_10_16_23_14_03/(untitled backup)-…`. That is the already-open GUI's ~62 s untitled autosave, not these isolated runs.
- Comparison script (throwaway, not in repo): `%LOCALAPPDATA%\Temp\pxo-saveas-check-a8d73e65-tool\compare.py`. Results JSON: `…\pxo-saveas-check-a8d73e65\result.json`.

## Screenshot correction (honest reference)

`outputs/rpg-2-star-ocean-the-second_yonkers_pixelorama-web-saveas-reopened-proof-v04_20261018-035600-f682ca74.png` (sha256 `67311109…d7ef069`, untracked) is **not proof of success**. It shows the *failed* reopen:
- a single tab named `untitled`
- `[64x64]` canvas
- one `Layer 1`
- an empty transparent canvas

It should be read as "web reopen FAILED — empty untitled canvas". I left it unrenamed because it belongs to the root session. Root should rename it, e.g. to `…_pixelorama-web-saveas-reopen-FAILED-empty-untitled-64x64-v04_20261018-035600-f682ca74.png`, or keep it only with this note.

## Recommendation to Codex (GUI reopen, actual UI)

1. The file is fine, so retry the load path, not the save.
2. In a fresh page load of the same official embed, use **File > Open** and pick `…pixelorama-web-saveas-v04_20261018-035200-a8d73e65.pxo`.
3. **Success** criteria:
   - a **second tab** appears, titled with the file stem
   - the top bar shows `[640x360]`
   - the timeline lists 13 layers, with `foreground-occluder` on top and `sky-and-ridge` at the bottom
4. If File > Open again yields only `untitled`:
   - try drag-and-drop of the file onto the canvas
   - try a short-named copy, e.g. `yk-v04-saveas.pxo`, with byte-identical content (to rule out filename-length handling in the browser upload path)
   - check the browser console for a load error and record it
5. Capture proof only when the 640×360 13-layer view is visible, and name the capture accordingly.
6. A blank `untitled` 64×64 capture must be filed as FAILED.

Status: v04 art UNAPPROVED. Save As data integrity is VERIFIED. Web GUI reopen is NOT YET DEMONSTRATED. Acceptance is left to root.

## Supplement 2026-10-18 04:30 local: official WEB reopen verified (supersedes "NOT YET DEMONSTRATED")

Source: Codex's visual observation handoff `work/claude-cycle/batch-0340/…web-editor-success-handoff_v01_20261018-040600-cd623075.txt` (local, not published). Claude re-inspected the screenshots named below.

- **WEB reopen now succeeded.** In a fresh page of the official Pixelorama web editor v1.2.3, an explicit File > Open of the actual Save As output loaded it.
  - The file was `…pixelorama-web-saveas-v04_20261018-035200-a8d73e65.pxo`, sha256 `05c03eb2…220c4ff`.
  - No shortened filename was used. The short-named copy in `work/` was never imported.
- **Identity proof.** `outputs/rpg-2-star-ocean-the-second_yonkers_pixelorama-web-saveas-reopened-640-source-identity-v04_20261018-040600-78d5e6a1.png`, sha256 `e2f46033…80dc41f4`. It shows:
  - the File menu entry `Save rpg-2-star-ocean-the-second_yonkers_pixelorama-web-saveas-v04_20261018-035200-a8d73e65.pxo`;
  - `[640x360]`;
  - the Yonkers v04 artwork;
  - the top of the layer list: `foreground-occluder`, `antenna-c-guyed-whip`, `antenna-b-dish`, `antenna-a-lattice-yagi`, and a partly visible `front-parapet`.
- **Lower layers: Codex observation only.** Codex observed the lower layers (deck-slabs, wall-kit-and-ivy, back-parapet-masonry, sky-and-ridge) while scrolling. No screenshot shows them.
  - The local `…reopened-bottom-layers-v04_20261018-040600-1c3f9d82.png` does **not** show the bottom layers, despite its name. It shows two project tabs and the same top layers.
  - It is not used as evidence.
- **Superseded screenshot.** `…reopen-empty-failed-v04_20261018-035600-f682ca74.png` (blank `untitled` 64×64) is kept only as superseded, intermediate history.
- **Scope.** Official WEB GUI load > Save As > fresh page > load of the saved copy is DEMONSTRATED. Together with the 13/13 byte-equal layers and the exact native CLI flat export above, the web round trip is verified.
- **Still open.** DESKTOP Pixelorama GUI Save As/reopen is NOT demonstrated. v04 art stays UNAPPROVED. No meter changes.
