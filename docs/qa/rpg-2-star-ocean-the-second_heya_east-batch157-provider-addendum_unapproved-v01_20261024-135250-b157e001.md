# Heya east static — batch 157 provider addendum (UNAPPROVED)

Task: `content.char.heya.static-east`. Batch 157 provider adapter: DeepSeek. Status: **existing batch155
source package reconciled and re-checked; UNAPPROVED, uncommitted, not integrated**. `artApproved=false`,
`runtimeAdopted=false`, defaults/selectors unchanged, no ledger/Bible/registry/Git-index edit and no commit.

This addendum is scoped to `content.char.heya.static-east`. It does not repaint, rebuild, scaffold, replace or
install any east file. No source tool, asset, manifest, palette, PXO, ORA or PNG was edited in batch 157.
The only new writes are under `outputs/heya-e157/` and this addendum file.

## Why this addendum exists

The batch155 producer QA at
`docs/qa/rpg-2-star-ocean-the-second_heya_east-static-qa_unapproved-v01_20261024-141500-h155e001.md`
contains two statements that the coordinator audit contradicts and that are **not repeated here**:

1. "No backup failures and no permission denials occurred" — false. The second QA-document edit
   (`8331560bc26b32e810f81547fc8d12704e43125be387d2cfbbb59223afe2958e` →
   `509697f82078c0d7a2d22a8ae190e49cd7a3d13299e74f3f14351cf918194d34`) had no own unique pre-edit backup.
   The intermediate text was recovered exactly from the verified first backup plus the first recorded edit, but
   reconstruction is **not retroactive compliance**.
2. `author-preview.log` was redirected twice over differing content with no verified backup. The surviving file
   (`sha256 bec339449083dba7b558549f30603d6d9a09fbbb79003eba335e0ff694def09f`) is the later log, not the lost
   original. `failed-draft-check.log` is a later rerun, not the original log.

The coordinator also recorded one technical denial for an unrelated combined provider-wait/process-inspection
command (script execution via `-c` in single-query mode). It was abandoned, not bypassed; it did not block an
east artifact write. No blanket Bash or permission bypass was used.

Retained failures remain failures. The failed draft's `identity_colours_all` and `upper_left_light_east` gate
result, the three earlier tool/API errors, the native diagnostic errors and the preservation failures are not
cleared by the later passes below.

## Fresh batch157 checks (actual commands and results)

Python: `/home/kel/projects/worlds-between/tooling/venv/bin/python3` (`-I -X utf8`). Hashes are raw SHA-256,
no normalization.

1. Author check, in-memory deterministic rebuild plus stage/install comparison:

   `python3 -X utf8 -I tools/rpg-2-star-ocean-the-second_heya_east-static-author_unapproved-v01_20261024-141500-h155e001.py check`

   Result: exit 0, `HEYA_EAST_V01_ALL_OK`, `hard_failures: []`, all ten `disk_matches_rebuild` entries `true`
   (five staging and five installed artifacts), south/west/north unchanged pins `true`.
   Log `outputs/heya-e157/provider-author-check.log`
   (`760a56d2228beac90434ed8345d4d750a560a8af36153f5056d24e16b5d00692`).

2. Independent source checker (does not import the author), fresh directory:

   `python3 -X utf8 -I tools/rpg-2-star-ocean-the-second_heya_east-static-source-check_v01_20261024-141500-h155e001.py --root . --out outputs/heya-e157/provider-independent-1`

   Result: exit 0, `HEYA_E155_INDEPENDENT 57 / 57`, `FAILURES []`. Report
   `outputs/heya-e157/provider-independent-1/rpg-2-star-ocean-the-second_heya_east_independent-source-proof_v01_20261024-141500-h155e001.json`
   (`8389823e7419099398e761622c2df3a26ec2c85ef5de558445eea3c88f081bd5`), byte-identical to both batch155
   independent reports; log `outputs/heya-e157/provider-independent-1.log`
   (`efa86365a916d2393b099531db71c97b0b6131ce127228fba38046cf993e9d65`).

3. Machine verification of existing source/native/fit evidence:
   `outputs/heya-e157/provider-verification.json`
   (`55798ff5d9c82250bc0787b5db282f9428235e99facf801b1679d10e26329e97`) records 32/32 checks passing.
   It recomputes the installed/staging bytes, manifest declarations, tool pins, the e155 independent reports,
   the native report, both fit proofs and their captures, the six source backups, protected files and the
   south/west/north dependency pins.

## Evidence validity verdict

- **Source**: installed and staging bytes match the batch155 QA hashes; manifest canvas `[80,112]`, pivot
  `[40,104]`, body rows `8..103`, `display_scale 0.5` = 48 logical px. `.gdignore` and `.gitattributes`
  (`* -text -eol`) match. The independent checker recomputes identity/direction/light/coil/scarf/far-bag/silhouette
  gates from the installed PNG/ORA/PXO bytes and detects every corrupted/wrong-facing control.
- **Native**: report
  `outputs/heya-e155/native-1/20261024-134516-f81e7cb8/rpg-2-star-ocean-the-second_heya_east_native-pixelorama-export-report_test-only-v01_20261024-141500-h155e001.json`
  (`d39ae4538b6a68125ad1c4d67258e1a0eff1068451e065ac18323cf3f6ae080d`) has `equality_passed=true`, all 11
  equality gates true, package hashes equal to installed. **Diagnostics are not clean**: `diagnostic_clean=false`;
  `custom_samplers` shader errors 4/4/4 for pxo-flat/pxo-split/ora-flat plus ORA-run leak/out-of-bounds markers
  (12 markers). No GUI save/reopen test (`gui_saveas_tested=false`), no runtime/default or art claim.
- **Fit**: both batch155 proofs (`-fit.json` `3749b9ad...`, `-fit-r2.json` `a0e60ee5...`) pass with four 640x360
  captures (city/ruins × en/zh), capture hashes match their manifests, source SHA equals the installed PNG
  (`273e5e85...`), `sourceUnchanged=true`, `runtimeAdopted=false`, `artApproved=false`. This is a test-only
  overlay, not normal actor integration, motion review or art approval. `-fit-r2` is the retained rerun; the
  original `fit` directory is unchanged.

## Coordinator rerun commands (exact)

```bash
cd /home/kel/projects/worlds-between/repo

# Independent source rerun (fresh directory must not exist)
/home/kel/projects/worlds-between/tooling/venv/bin/python3 -X utf8 -I \
  tools/rpg-2-star-ocean-the-second_heya_east-static-source-check_v01_20261024-141500-h155e001.py \
  --root . --out outputs/heya-e157/coordinator-independent-1

# Native Pixelorama export equality rerun (fresh directory)
/home/kel/projects/worlds-between/tooling/venv/bin/python3 -X utf8 -I \
  tools/rpg-2-star-ocean-the-second_heya_east-static-native-pixelorama-check_v01_20261024-141500-h155e001.py \
  --out outputs/heya-e157/coordinator-native-1

# Bilingual bright/dark source-fit rerun; the tool auto-creates outputs/heya-e155/fit-r3
# and ...-fit-r3.json and does not overwrite fit/ or fit-r2/.
/home/kel/projects/worlds-between/tooling/venv/bin/python3 -X utf8 -I \
  tools/rpg-2-star-ocean-the-second_heya_east-static-source-fit_v01_20261024-141500-h155e001.py
```

The native rerun is expected to reproduce equality while still reporting `diagnostic_clean=false`; that is a
retained limitation, not a pass condition to relax.

## Honest limitations / retained failures

- Failed draft gates `identity_colours_all`, `upper_left_light_east` are retained in
  `outputs/heya-e155/failed-draft-check.log` (`f6a8edd8...`) and the failed preview/source
  (`...645dd370.png` `afe48136...`; `tmp/failing-author-draft-645dd370.py` `d6c99ec5...`).
- Three earlier author-tool errors (`P.hline`, missing PIL import, wrong west manifest constant) remain in the
  batch155 backups and failure record.
- Preservation failures above are permanent facts; recovered text is not proof of compliant backup practice.
- Native diagnostics not clean; no GUI save/reopen proof; no motion/combat/runtime integration; no art approval.
- No ledger/Bible/registry/Git-index/commit change by this provider. Coordinator source commit, independent
  integration run and ledger transition remain.

## Protected hashes: provider before/after observation (raw SHA-256)

This provider ran no ledger/Bible/registry/index write. The canonical ledger nevertheless changed **during**
the provider window, after the 32/32 verification snapshot: mtime `2026-10-24T13:53:06Z`, size `890006`,
`56d9448d…` -> `a361d83d…`. The change is recorded, not hidden or attributed to this adapter; the coordinator
was concurrently active (a coordinator fit-r3 proof also appeared at `13:52:05Z`) and must confirm/attribute
its own ledger transition.

| File | before | after |
| --- | --- | --- |
| production ledger | `56d9448d2f75fa6d8557905b6c05f3225debbbbc7910b69b9bfc826382c55f68` | `a361d83d1fdb2c0cb2dc0ee58314ba9f0ae34c44c634d3e8219c343950c82878` |
| game Bible state | `20971d75d0a07b7839eff66e770786b91166e9908f43dc0278f8001b908d7c94` | same |
| operating registry | `0d54dc53fdb1e7867d641fe0b9d2cbb27fcec4b8379d387e9f52b9b65c61c14a` | same |
| MVP progress state | `a601fb6c75a7605e734e46547eabaf14d23d24ee37a13e52d0a54672d5e28fc9` | same |
| asset inventory state | `42af8137d0b3a4dbf8318688e4e6dd481a4ee023859c9e26f5e12c4104fa78a7` | same |
| character visual registry | `732753892b57d394427d5a2c0e02f218183f04d4334b167eb417288c2e61273d` | same |
| Git index | `b86e48ea9ead31dbe14aa50cc72fd3ae7393a532bedc6bbdb6f76f478f5fcf7f` | same |

The operating registry already showed ` M` in git status before provider work; its bytes are unchanged.
Dependency pins unchanged: south `d6ddec7e…`, west `75b0519c…`, north `7445095e…`.
Full machine record: `outputs/heya-e157/provider-receipt.json` and `outputs/heya-e157/provider-verification.json`.
