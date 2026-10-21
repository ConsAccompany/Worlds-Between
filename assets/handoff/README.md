# Complete project asset handoff

This is a content-deduplicated snapshot for DeepSeek takeover, not a playable game release or new artistic approval.

- **8,773 unique files:**8,199 media/native assets plus574source/provenance manifests and authoring sources.
- **4,361 already in this Git repository**, reused at their existing paths.
- **4,412 additional files in22ordinary-Git ZIP bundles**,each below100MiB.
-47registered project worktrees plus project scratch authoring locations were inventoried with0scan errors.
- Excluded: private account/credential/controller folders, engines/dependencies/import caches, reproducible raw recording/per-frame debug sequences and test fixtures. Nothing outside the listed project/worktree scope is claimed covered.
- Historical, rejected and unapproved assets are preserved as archives. **No default or approval changed.**
- Each indexed file has SHA-256, size, storage location, original paths/root identifiers and exact-file inventory claims where available. Index claims do not override creator approval scope.

## Start here

- [Full searchable JSON index](rpg-2-star-ocean-the-second_project-assets_complete-index_v01_20261021-180244-718e0ceb.json)
- [Browse/download CSV](rpg-2-star-ocean-the-second_project-assets_browse-index_v01_20261021-180244-718e0ceb.csv)
- [Downloadable asset packages](packages/)
- [Fetch, verify and safe historical restore tool](../../tools/rpg-2-star-ocean-the-second_project-assets_fetch-verify-restore_v01_20261021-180329-38c38f93.py)
- [Canonical artistic inventory](../../outputs/rpg-2-star-ocean-the-second_asset-inventory_state_v01_20261013-191033-7d1e0a8b.json)

Package upload is in progress until the remote publication proof is linked below.

## DeepSeek: get every indexed asset

Clone/pull ConsAccompany/Worlds-Between main. From its repository root, using a Python3 runtime:

```powershell
python -X utf8 -I "tools/rpg-2-star-ocean-the-second_project-assets_fetch-verify-restore_v01_20261021-180329-38c38f93.py" --manifest "assets/handoff/rpg-2-star-ocean-the-second_project-assets_complete-index_v01_20261021-180244-718e0ceb.json" --download --verify
```

A normal full clone already contains all archive files in assets/handoff/packages. This verifies them and every indexed member, plus existing Git files. If a package is missing, the command can fetch its public raw GitHub URL. No LFS, model inference or credential export is required.

The tool verifies exact Git object bytes for text source when a Windows working copy differs only by CRLF conversion. It never normalizes a hash and calls it exact. Binary/source content changes beyond line endings are refused.

To inspect just the files already in Git:

```powershell
python -X utf8 -I "tools/rpg-2-star-ocean-the-second_project-assets_fetch-verify-restore_v01_20261021-180329-38c38f93.py" --manifest "assets/handoff/rpg-2-star-ocean-the-second_project-assets_complete-index_v01_20261021-180244-718e0ceb.json" --verify-main
```

## Restore a historical authoring workspace

The JSON roots list names each origin. Restore only into a separate folder:

```powershell
python -X utf8 -I "tools/rpg-2-star-ocean-the-second_project-assets_fetch-verify-restore_v01_20261021-180329-38c38f93.py" --manifest "assets/handoff/rpg-2-star-ocean-the-second_project-assets_complete-index_v01_20261021-180244-718e0ceb.json" --restore-root primary --destination "work/restored-primary-assets"
```

This reconstructs original asset/source paths from Git files or verified archive members. It refuses path traversal, symlink/reparse targets and nonmatching existing files. It does not restore a complete historical code checkout or promise old scripts run unchanged; it preserves the asset/source bytes and their provenance.

## Current heroine defaults

- Exploration:game/data/hsea-front17.
- Combat:game/data/hsc19.
- Whole-package/default selector:game/scripts/hsea18/rpg-2-star-ocean-the-second_heroine-normal-default_policy_runtime-v01_20261021-032237-7c02af94.gd.
- Ordinary female default use is creator-authorized; full motion/art acceptance remains pending.
- Archive location, filename, version or successful restoration does not make an old asset current or approved.

## Integrity and coverage

The ZIPs retain byte-exact files in content-addressed members. All archived bytes were checked against their source SHA-256 at packaging and each ZIP passed a complete CRC read. The full index preserves origin aliases without publishing absolute account paths. Source images, editable PXO/ORA, animation/video references, audio, and available manifests/authoring tools are included.

After downloading, do not replace live game assets wholesale. Use the index to choose a source, inspect it in the actual game and follow the canonical production/inspection/creator-approval workflow. Production stays54.6%; this transfer earns no duplicate asset-production points.
