# Heya north static — author face-gate repair addendum (UNAPPROVED source)

Task `content.char.heya.static-north`, bounded batch152 repair `h152n002`. Scope was limited to replacing one
fake hard gate in the north author, with a verified pre-edit backup and fresh checks. No art, package pixels,
installed asset, manifest, ledger, Bible, registry, index, default or Git item was changed. This addendum is new;
the old producer receipt and QA note remain untouched as historical records.

## Defect and correction

The old author at line 248 contained:

```python
g["north_face_no_eyes_or_mouth"] = True
```

That is not evidence. It was replaced with the same genuine pixel-based test used by the separate source checker
(`no_face_features`): read the `face` layer's opaque texels and reject the declared eye-white, iris and mouth
palette keys `e1`, `e2`, `m1`.

```python
fm = blobs["face"][..., 3] == 255
fcols = {tuple(c) for c in blobs["face"][fm][:, :3]}
face_eye_mouth = {S.rgb(k) for k in ("e1", "e2", "m1")}
g["north_face_no_eyes_or_mouth"] = not (fcols & face_eye_mouth)
g["north_face_palette_detail"] = {"eye_mouth_colours_present": sorted(
    "#" + "".join(f"{v:02x}" for v in c) for c in fcols & face_eye_mouth)}
```

The gate is now data-derived and fails if any eye-white/iris/mouth texel enters the face layer. No gate name,
package field, threshold or acceptance criterion was weakened.

## Hash identity

| Item | SHA-256 | Size |
|---|---|---|
| Pre-repair author (verified backup) | `582da48e7f97dc3ff891d7ad0679b1306f0b5b598e05a85636b005328d3ee1b0` | 27398 |
| Corrected author | `514f25c1b385a72935a48fd353710da743c6affbef20ac743ab143edefb26075` | 27792 |
| Old producer receipt (unchanged) | `244286f55b72e0a1625ac150aab3e9dd29f8a0631f89b4e092f0cd851ffe1bd2` | — |
| Backup receipt | `154518dd60a11076a507cbbf5c85d28375b97f174e2f7ba995d24114e5b7c438` | — |
| Draft-preservation receipt | `50e9533d2b59c294f145c3af458396147d87bd7c464f6df6d230984a39c20464` | — |

The old producer receipt's `tools[0].sha256` is the now-stale pre-repair author hash
`582da48e7f97dc3ff891d7ad0679b1306f0b5b598e05a85636b005328d3ee1b0`. The corrected author hash is
`514f25c1b385a72935a48fd353710da743c6affbef20ac743ab143edefb26075`. The old receipt and
`docs/qa/...producer-note...h152n001.md` were deliberately not rewritten, avoiding circular receipt/QA churn.

## Backup (copy2, unique, verified)

- Source: `tools/rpg-2-star-ocean-the-second_heya_north-static-author_unapproved-v01_20261024-134500-h152n001.py`
- Backup:
  `outputs/heya-n152/source-backups/20261024-134500-h152n001-author-facegate-fix-20261024-133343/rpg-2-star-ocean-the-second_heya_north-static-author_unapproved-v01_20261024-134500-h152n001.py`
- Receipt:
  `outputs/heya-n152/source-backups/20261024-134500-h152n001-author-facegate-fix-20261024-133343/receipt.json`
- Backup hash equals the pre-repair source hash
  `582da48e7f97dc3ff891d7ad0679b1306f0b5b598e05a85636b005328d3ee1b0`; size, mode (`0664`), uid/gid and
  mtime nanoseconds matched at verification. The backup directory was unique and did not pre-exist.

The author lives under `tools/`, outside the `wb_safe_replace.py` development-path allowlist
(`outputs/` or `game/assets/`), so this was a direct `copy2` backup rather than a helper replacement. No
`outputs/` or `game/assets/` existing file was replaced in this repair, so the helper was not required or invoked.
No installed image, PXO, ORA or manifest was touched.

## Preserved `/tmp` drafts (read-only copy)

`/tmp/wbn` was accessible and was copied without edit or deletion to
`outputs/heya-n152/source-backups/draft-preservation-20261024-133343/`; all five files' SHA-256 and metadata
matched at copy verification (receipt hash above). The preserved author draft
`north_author_draft.py` is `6098959f983783413b7bbbc64a33537cbc27739c263f0c29d3d5ac8fe0746a84`, which differs from
the pre-repair repo author `582da48e…`. It is preserved as historical draft state only; the repair was made from
the verified repo author, not from that draft, and no retrospective compliance is claimed for earlier unbacked
`/tmp` edits. No new temporary draft was needed; the scratch area `/home/kel/.hermes/cache/scratch` was not used
for writes, and no `/tmp` path was written.

## Actual checks (fresh output directory)

Output directory: `outputs/heya-n152/repair-20261024-133343-h152n002/`

1. Author check:
   `/home/kel/projects/worlds-between/tooling/venv/bin/python3 -I tools/rpg-2-star-ocean-the-second_heya_north-static-author_unapproved-v01_20261024-134500-h152n001.py check`
   - exit `0`
   - `HEYA_NORTH_V01_ALL_OK`
   - `hard_failures: []`
   - `deterministic_rebuild: true`
   - `north_face_no_eyes_or_mouth: true`
   - all stage/install disk hashes matched the rebuild
   - log `outputs/heya-n152/repair-20261024-133343-h152n002/author-check.log`
     `4ea25614a3964a1e43300d980713547647fdfa1ee379f09cd7e1221efa7355f3`

2. Independent checker (does not import the Heya author):
   `/home/kel/projects/worlds-between/tooling/venv/bin/python3 -I tools/rpg-2-star-ocean-the-second_heya_north-static-source-check_v01_20261024-134500-h152n001.py --root . --out outputs/heya-n152/repair-20261024-133343-h152n002/independent`
   - exit `0`
   - `HEYA_N152_INDEPENDENT 49 / 49`
   - `FAILURES []`
   - `north_face_no_eyes_or_mouth: true`
   - `control_front_face_detected: true` (same detector returns false for a synthetic face containing `e1`/`m1`)
   - log `outputs/heya-n152/repair-20261024-133343-h152n002/independent.log`
     `0a926cbd21f9100274f743fafe85a0059101af913428fa57121b2fe596afc103`
   - proof
     `outputs/heya-n152/repair-20261024-133343-h152n002/independent/rpg-2-star-ocean-the-second_heya_independent-source-proof_v01_20261024-134500-h152n001.json`
     `9066329647e57a47eb9b3b36981e2fa7619fee0d842d5457960cabab53699a41`

3. Installed package bytes were re-hashed and are unchanged from the old receipt: manifest
   `7445095eec59c152a0f580acf0d63f17ec900be4824c1eb35cd2fc7a8064c0f7`, palette
   `e1a1a9ac775ccb452498f02db97230b3135727da7d999bf132f2877837483a52`, PNG
   `d0019c77032ec7dcb403e3d54cc80a6b9b60a875881cefa1887bb145072656c4`, PXO
   `f612bba8815533e8c0411270ed81c381e44d6e22d4266d03ae9b2fb84de44942`, ORA
   `999f3929036569190fadec06c4602156a39ef1f3ce2d81a67794f5de1b5ee6ce`.

No native-export, source-fit or M1 smoke rerun was performed in this bounded repair; the coordinator's earlier
49/49, native 11/11, source-fit and smoke evidence remains historical and is not replaced by this addendum.

## Failures, limitations and scope

- The repaired defect was the fake hard gate itself. No check failed after the correction.
- The old producer receipt now necessarily carries the stale author hash `582da48e…`; it was not edited. The old
  QA note and all earlier receipts/logs are preserved as history.
- Earlier `/tmp` draft edits were not backed up before the prior job edited them. Their preserved state is
  recorded, not retroactively excused.
- No new art was produced or reviewed; `UNAPPROVED`, `approval=false`, `artApproved=false`,
  `runtimeAdopted=false` are unchanged.
- No denial occurred. No blanket Bash, permission bypass, deletion, credential/account/billing action, ledger,
  Bible, registry, index, default, commit or push was touched.
