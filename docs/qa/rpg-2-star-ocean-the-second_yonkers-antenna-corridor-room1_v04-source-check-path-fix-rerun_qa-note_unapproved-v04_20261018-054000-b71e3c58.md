# Yonkers room 1 v04: source-check report-path fix and rerun (UNAPPROVED)

Date: 2026-10-18. Tag `20261018-054000-b71e3c58`. This supersedes the caveats in `…_v04-pixelorama-official-cli-export-roundtrip_qa-note_unapproved-v04_20261018-053800-4be2a917.md`. The earlier reports are kept unchanged as historical evidence. v04 stays UNAPPROVED, nonruntime and off by default.

## Fix (`tools/…_material-depth-source-check_unapproved-v04_20261018-052445-523bba3b.py` only)

- The `--report` path is now resolved before writing. The final print shows it relative to the repo root when possible, so a relative `--report` no longer crashes the run.
- The `G_godot_capture` text now reads "Godot is not run by this source checker; see separate v04 Godot test-only evidence". The evidence is in `…_v04-godot-test-only-capture-and-closeouts_qa-note_unapproved-v04_20261018-053200-7c41e9d2.md`.
- No gate logic, test, art or runtime file changed.

## Rerun (once, with the hash-verified official Pixelorama v1.2.3 Linux binary)

The archive sha256 was rechecked as `e7bb3b5f485e3a67f06b15a2c8414a8a7c18b7c6d2cf73f6b3b5904d86821e4b`.

```
python3 -I tools/…_material-depth-source-check_unapproved-v04_20261018-052445-523bba3b.py \
  --pixelorama <scratch>/Pixelorama-Linux-64bit/Pixelorama.x86_64 \
  --report outputs/yonkers-room1-v04_523bba3b/…_material-depth-source-and-pixelorama-check-report_official-v1.2.3-path-fix_20261018-054000-b71e3c58.json
```

- **Overall command exit 0.** Gates S1–S4 and V1–V3 pass (7/7).
- **Pixelorama:** for the `.pxo` and the `.ora`, the split export exits 0 with all 13 layers byte-exact, and the flat export is exact. Both sources are unchanged, and the real APPDATA is untouched.
- **Asset hashes:** the v04 `.pxo`, `.ora`, PNGs and nonruntime exports hash the same before and after the run.
- The tool still prints its Pixelorama result under the label `PENDING P_pixelorama_cli_round_trip: True`. The value `True` means the Pixelorama export checks passed.
- **Still pending:** saving and reopening a new `.pxo` in the Pixelorama app. The CLI can only export.
