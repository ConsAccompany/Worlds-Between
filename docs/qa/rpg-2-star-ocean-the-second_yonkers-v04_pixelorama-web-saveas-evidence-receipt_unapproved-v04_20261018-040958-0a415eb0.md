# Yonkers v04: Pixelorama WEB Save As + fresh reopen evidence receipt (UNAPPROVED)

Date: 2026-10-18 (first draft 04:10, updated 04:30 local after Codex's web-reopen success observation). This receipt records what was verified, using the add606a0 data-validation check and its dated supplement:
`docs/qa/rpg-2-star-ocean-the-second_yonkers-v04_pixelorama-web-saveas-data-validation_qa-check_unapproved-v04_20261018-035956-add606a0.md`

No art was authored. Counters are unchanged: 40.8%, M2 10/12, scenes 3/12, sprites 0/52, playtests 0/2, formal acceptance false. v04 art stays UNAPPROVED.

## Verified: official WEB editor v1.2.3

1. **Save As.** File > Save As on the v04 layered source `outputs/yonkers-room1-v04_523bba3b/…material-depth-scene-layers_unapproved-v04_20261018-052445-523bba3b.pxo` (sha256 `ed9d605b…7ab5e28`, tracked at `7370739`).
2. **Lossless.** The saved file keeps all 13 layers byte-equal to the original, with names, order, visibility, lock, opacity and blend unchanged.
   - The official native CLI v1.2.3 flat export is pixel-equal to the original's.
   - The only `data.json` differences are web-save export metadata and a 256×144 preview thumbnail.
3. **Fresh reopen.** In a fresh page, File > Open of that saved file loaded it. The file menu names the file, the canvas is `[640x360]` and the Yonkers v04 artwork shows.

| Role | Path | sha256 |
|---|---|---|
| Save As output (byte copy) | `outputs/yonkers-room1-v04_523bba3b/rpg-2-star-ocean-the-second_yonkers-antenna-room1_pixelorama-web-saveas-output-lossless_official-web-v1.2.3_20261018-035200-a8d73e65.pxo` (80504 B) | `05c03eb232a96f6683f7881fdbb694f6af953d83f3e7887c5b9dcd7c3220c4ff` |
| Reopen identity proof | `outputs/rpg-2-star-ocean-the-second_yonkers_pixelorama-web-saveas-reopened-640-source-identity-v04_20261018-040600-78d5e6a1.png` | `e2f46033318fac8c1b05d6f4ee8935587565aa5bd4f03555875e180a80dc41f4` |
| Superseded intermediate (blank `untitled` 64×64, historical only) | `outputs/rpg-2-star-ocean-the-second_yonkers_pixelorama-web-saveas-reopen-empty-failed-v04_20261018-035600-f682ca74.png` | `673111096eed2f20321e1410b725cfaaad0d53bacf719d749a7881048d7ef069` |

The original Save As file is left in place at `work/native-save-0340/rpg-2-star-ocean-the-second_yonkers_pixelorama-web-saveas-v04_20261018-035200-a8d73e65.pxo` (same sha256).

## Screenshot semantics

- **The identity proof shows:**
  - the File menu entry `Save rpg-2-star-ocean-the-second_yonkers_pixelorama-web-saveas-v04_20261018-035200-a8d73e65.pxo`;
  - `[640x360]`;
  - the artwork;
  - the top layers: `foreground-occluder`, `antenna-c-guyed-whip`, `antenna-b-dish`, `antenna-a-lattice-yagi`, and a partly visible `front-parapet`.
- **Lower layers.** The lower layers (deck-slabs down to sky-and-ridge) were seen by Codex while scrolling. That is an observation, not a screenshot.
- **Not used as evidence.** The local `…reopened-bottom-layers…1c3f9d82.png` shows two project tabs and the same top layers, **not** the bottom layers. It is not committed.

## Not verified

- **DESKTOP Pixelorama GUI Save As/reopen is NOT demonstrated.** The web and desktop scopes are separate.
- No art acceptance and no meter or gate change.
