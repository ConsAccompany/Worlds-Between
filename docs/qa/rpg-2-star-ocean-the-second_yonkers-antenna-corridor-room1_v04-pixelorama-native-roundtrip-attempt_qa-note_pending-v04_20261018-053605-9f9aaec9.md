# Yonkers room 1 v04: native Pixelorama round-trip attempt — NOT RUN (pending locally)

Date: 2026-10-18. Tag `20261018-053605-9f9aaec9`. The v04 candidate stays **UNAPPROVED**, nonruntime and off by default. Codex judged the real zh/en Godot entry captures: the materials are still schematic, and there is no art acceptance. No art, game file or earlier commit was changed.

## Target

The target file is `outputs/yonkers-room1-v04_523bba3b/rpg-2-star-ocean-the-second_yonkers-antenna-room1_material-depth-scene-layers_unapproved-v04_20261018-052445-523bba3b.pxo`.

- sha256-bytes: `ed9d605bad1cfa1d6875db6b4e535523023f1e9efcb437939115510317ab5e28` (unchanged)
- Its `data.json` declares `pixelorama_version` v1.2.3-stable and `pxo_version` 7, with size 640×360 and 13 layers. These values were read from the file's own metadata; that is not an editor verification.

## Attempt (bounded: one official download)

```
curl -sSfL -o px.zip https://github.com/Orama-Interactive/Pixelorama/releases/download/v1.2.3/Pixelorama-Linux-64bit.zip
-> curl: (22) The requested URL returned error: 404
curl -sSf https://api.github.com/repos/Orama-Interactive/Pixelorama/releases/tags/v1.2.3   # list the real asset names
-> curl: (22) The requested URL returned error: 403   (blocked by the session's network proxy)
```

## Result: native editor round trip NOT RUN

**Missing capability:** this cloud session has no official Pixelorama v1.2.3 binary.

- The guessed Linux asset name does not exist (404).
- The release asset listing that would give the correct name is refused by the network proxy (403).
- The upstream source plus its Godot export templates would also need building, which is a dependency chase outside this bound.

No GUI automation, no reimplemented .pxo parser and no modified upstream loader were used. **Nothing is claimed as passed.** The earlier v04 source check (7/7) and the Godot test-only capture check stay as recorded. Neither is a native editor check.

## Local commands to close the gap

These need Pixelorama 1.2.3; the headless CLI export is the same one the v03 checker used on Windows.

```
python -I tools/rpg-2-star-ocean-the-second_yonkers-antenna-room1_material-depth-source-check_unapproved-v04_20261018-052445-523bba3b.py --pixelorama <path to Pixelorama 1.2.3 executable>
```

This runs `Pixelorama --headless --quit -- --export [--split-layers] -o <tmp>/f.png <copy of the .pxo>` in a temp APPDATA. It requires all 13 split layers to be byte-exact with the source layers, the flat export to be exact, the source to be unchanged and the real APPDATA to be untouched. A save-as/reopen of a distinctly named .pxo still needs the Pixelorama app and remains pending.
