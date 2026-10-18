# Yonkers room 1 v04: official Pixelorama v1.2.3 CLI export check (UNAPPROVED)

Date: 2026-10-18. Tag `20261018-053800-4be2a917`. This note supersedes the "NOT RUN" result in `…_v04-pixelorama-native-roundtrip-attempt_qa-note_pending-v04_20261018-053605-9f9aaec9.md` for the CLI export check only. v04 stays **UNAPPROVED**, nonruntime and off by default, with no art acceptance (Codex: materials still schematic).

## Upstream binary

- **URL:** `https://github.com/Orama-Interactive/Pixelorama/releases/download/v1.2.3/Pixelorama-Linux-64bit.tar.gz`. Codex found it on the official release page; a single retry was authorized.
- **sha256:** `e7bb3b5f485e3a67f06b15a2c8414a8a7c18b7c6d2cf73f6b3b5904d86821e4b`, which matches the officially displayed value. It was verified before running. The archive is 31,229,117 bytes.
- **Executable:** `Pixelorama-Linux-64bit/Pixelorama.x86_64` plus `Pixelorama.pck`. It was extracted to the session scratchpad and is not in the repo. It was not modified.

## Commands

```
python3 -I tools/rpg-2-star-ocean-the-second_yonkers-antenna-room1_material-depth-source-check_unapproved-v04_20261018-052445-523bba3b.py \
  --pixelorama <scratch>/Pixelorama-Linux-64bit/Pixelorama.x86_64 \
  --report outputs/yonkers-room1-v04_523bba3b/…_material-depth-pixelorama-native-cli-check-report_official-v1.2.3_20261018-053800-4be2a917.json
Pixelorama.x86_64 --headless --quit -- --export -o <tmp>/out.png <tmp copy of the v04 .pxo>   # evidence export
```

The check tool runs `--export` and `--export --split-layers` on temporary copies of the `.pxo` and `.ora`, each with its own temporary APPDATA.

## Result

- **Split export through upstream code:** `.pxo` and `.ora` each exit 0 with 13 PNGs. All 13 named layers decode **byte-exact** against the source layers: sky-and-ridge through foreground-occluder.
- **Flat export:** `.pxo` and `.ora` each exit 0 and are **exact** (0 differing texels) against the composite.
- **Inputs:** both source copies are unchanged by the CLI, and the real APPDATA was untouched.
- **Report gates:** S1–S4 and V1–V3 PASS; P (Pixelorama CLI round trip) **true**.
  - Two caveats about the report:
    - Its `G_godot_capture` text is the tool's fixed wording ("no Godot binary here"). Godot was in fact run in the separate test-only check; see `…_v04-godot-test-only-capture-and-closeouts_qa-note_unapproved-v04_20261018-053200-7c41e9d2.md`.
    - The tool crashed only on its final `print`, because a relative `--report` path was given. The report had already been written.
- **Preserved export:** `outputs/yonkers-room1-v04_523bba3b/…_material-depth-pixelorama-official-cli-flat-export-640x360_official-v1.2.3_20261018-053800-4be2a917.png`, sha256 `0d23de9fdb970c5e7e679d9183bf8653b08e0178cf065d128a1ba4ea28cbe0c5`. It is 640×360 RGBA and **pixel-equal** to the committed v04 native flat PNG.
- **Original v04 `.pxo`:** unchanged, sha256 `ed9d605bad1cfa1d6875db6b4e535523023f1e9efcb437939115510317ab5e28`.

## Still pending

- **Save as a new .pxo, then reopen:** the official CLI offers export only, not project save. No GUI automation was used, so this check stays **pending** (it needs the Pixelorama app run by a person).
