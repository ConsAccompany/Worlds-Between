# Milo east: Hermes independent source-production verdict (UNAPPROVED)

Canonical task `content.char.milo.static-east`. Tested base `1f0519de8080a6c57298838cfa8b68963b2a3bde`. Existing Claude-adapter east art from interrupted attempt 43 was retained unchanged; batch 45 completed its independent checker and source QA through the authorized adapter. Hermes independently reran the required checks and inspected actual images. Production credit is conditional on scoped source commit; no human art acceptance, native application-clean/GUI reliability, motion, ordinary actor integration or default adoption is granted.

## Verdict and source contract

PASS for the frozen source-production criterion: an east-facing native static at 48 logical pixels, editable layered PXO/ORA and deterministic PNG with QA, not the old 32x48 placeholder. Canvas80x112; body rows8..103; display scale0.5; pivot40,104. Retained hard gates:34 used colours,10 genuine visible role layers,18 isolated texels and hidden guides. Original white-grey short medical coat, navy clothes, silver temple patch, medicine case and green wristband remain visible.

Hermes inspected the actual x6 source preview plus English City Hall and Chinese Capitol ruins static-overlay captures. Nose/eye lead screen-right, silver patch is visible near the temple, case projects behind the near hip and green wristband is in front on the far wrist. Hands and feet remain attached; no disconnected limb or source cropping was observed. At gameplay size the coat/case/band retain distinct light/green accents, while fine facial detail is small. This is a bounded technical inspection, not creator artistic acceptance. Captures are labeled test-only overlays, not normal actor use, motion or a dark-scene test.

## Independent reruns

From repository root, orchestration is `outputs/milo-e01/rpg-2-star-ocean-the-second_milo_east-qa-orchestrate_v01_20261024-000137-e4a1c7d2.py`. Commands were `python3 -I <orchestrator> <step> <logdir>`, with these exact arguments:

- `check hermes45-check`: inner rc0, MILO_EAST_V01_ALL_OK; deterministic rebuild and all five disk artifacts match, hard_failures empty.
- `source hermes45-source`: inner rc0, MILO_E01_INDEPENDENT56/56, FAILURES empty. Independent checker imports no Milo author. Six direction negative controls and corrupt hash, tampered PNG, visible guides, tampered south/north manifests are rejected. Dirty west is a read-only negative control, not a production dependency or accepted source.
- `pixelorama hermes45-pxl`: both headless exports rc0; source hashes unchanged. Application diagnostic gate FAILS separately below.
- `compare hermes45-compare hermes45-pxl`: inner rc0, MILO_EAST_PXL_EXPORT_PIXEL_EXACT; PXO and ORA exports each have0 differing texels. Both emitted raw PNG hashes are395ede84c500caa98381466c4a6adfde95bda71bd99b82b2bca76b9f1f87604b.
- `fit hermes45-fit`: existing checked Godot runner, Dummy audio, Xvfb/OpenGL3, finite110-second inner deadline. JIANG37_SOURCE_FIT_PASS captures=4 and CHECKED_RUN PASS, rc0,3.565seconds. One V-Sync warning, no ERROR/Parse Error/SCRIPT_ERROR. Four EN/ZH city/ruins captures and manifest retained.

Hermes parsed all five summary files rather than trusting orchestration exit0: every inner result is0, pinsUnchanged is true, sourceRevision is the tested base and all pinned files still match exact raw SHA-256. A separate pre-integration baseline verified all18 canonical/protected package files unchanged, including south, north and unfinished west. Existing unrelated dirty work remains protected.

## Source hashes

SHA-256 of exact raw bytes, no normalization. Prefix `game/assets/characters/milo-native-v01/east/`:

- rpg-2-star-ocean-the-second_milo_east-static_unapproved-v01_20261024-000137-820dcbf2.png: af45b51d44c0b409267c2995ec196593cbf0fca6cbb178c01b65e6f0d749e070
- rpg-2-star-ocean-the-second_milo_east-edit_unapproved-v01_20261024-000137-8799fd7f.pxo: a854453e33abcfe03437a7c0cc90f50a72660772a983f78792cf802aa620b17a
- rpg-2-star-ocean-the-second_milo_east-edit_unapproved-v01_20261024-000137-a77ff61f.ora: 56171d13a062b1eff9a48201b3338c06d861365cbbf318af5af865258d484b78
- rpg-2-star-ocean-the-second_milo_east-palette_unapproved-v01_20261024-000137-29b43d49.json: c322e69c1ca22a79347e1981d82bc5d4cab6b8e4dc901a3a88add70ff3b01333
- rpg-2-star-ocean-the-second_milo_east-manifest_unapproved-v01_20261024-000137-1a15f1d2.json: dc77dec5f89b68754782bef12c158fbccda29ba314bf998cbab1da3ab936db44

Independent checker raw hash789a9797e32243c9e37b55548d8e74789bb2cd515f99a9a6cf2233a9f5b8c5c3. Full source/tool/capture hashes are retained in independent proof and step summaries. Creator/source contract and producer QA are preserved unchanged.

## Failures and limitations retained

Pixelorama application-clean remains FAILED: PXO4 shader ERROR lines; ORA11 ERROR lines plus1 warning, including4 shader errors,3 get_child bounds errors, null rp_node, ancestor-control failure,12 leaked texture RIDs,16 resources still in use and160 leaked ObjectDB instances. Exact export equality does not establish diagnostic-clean execution or GUI reliability. No new GUI save/reopen was tested. These application failures do not disappear merely because native exports match.

Adapter job f2286fc47aeb45e2a58729e7ad3c0e0c finished with outcome exited, returncode0, classification permission_denied and scope.confirmed true. Exact operational logs: `/home/kel/projects/worlds-between/autonomy/provider/46-claude.stdout.log` and `/home/kel/projects/worlds-between/autonomy/provider/46-claude.stderr.log` (stderr empty). Adapter attempt46 belongs to coordinator attempt45; it is not a second writer. The two actual permission-denied commands were:

```
cd /home/kel/projects/worlds-between/repo; cat outputs/milo-e01/*orchestrate*.py; cat outputs/milo-e01/*contract*.md; for d in outputs/milo-e01/logs/*; do echo "== $d"; ls $d; tail -5 $d/* 2>/dev/null | head -40; done; cat outputs/milo-e01/author/*.json
cd /home/kel/projects/worlds-between/repo; O=outputs/milo-e01/rpg-2-star-ocean-the-second_milo_east-qa-orchestrate_v01_20261024-000137-e4a1c7d2.py; python3 -I $O check check1 | tail -8; python3 -I $O source source1 | grep -v '^ ' | tail -40
```

Both returned `A variable in this command can't be checked before it runs`. They are not counted as successful checks. Adapter subsequently produced allowed-form check logs; Hermes independently reran the exact checks through its own authorized verification tools. No permission settings or provider/account route was changed; no replacement was necessary because the existing art bytes were retained. No claim of creator overwrite-consent failure is made. Operational receipt success alone is not game completion evidence.

The coordinator's first read-only JSON stdout parser failed with AttributeError on a string-valued message; the corrected parser type-checks entries and successfully inspected the actual final result and denied commands. No game validation failure was concealed.

## Completion boundary

Existing two production points only, after commit and audited ledger transition. Starting meters: production61.2%, inspection21.6%, approval7.8%; final values belong in the Bible via its existing progress CLI. Frozen baseline/weights and every other task remain unchanged. Full sprite-set readiness, west production, animation, creator art review and ordinary actor adoption remain separate. Next existing useful source task is unfinished Milo west, but this batch does not resume or modify it.
