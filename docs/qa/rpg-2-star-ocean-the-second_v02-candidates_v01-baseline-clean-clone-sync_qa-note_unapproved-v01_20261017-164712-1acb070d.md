# Chicago and Washington v02: v01 comparison baselines synced for clean clones

Recorded 2026-10-17 at 16:47 EDT by Claude Max firstParty (`ANTHROPIC_API_KEY` absent). This repairs the gap named in `docs/qa/rpg-2-star-ocean-the-second_v02-candidates_selective-integration-closeout_unapproved-v01_20261017-163336-0121aa11.md` ("Not synced (local only)").

**Status:** reproducibility repair only. Chicago Loop State/Lake v02 (`55667f46`) and WDC survey annex room 1 v02 (`71300729`) stay **technically verified, creator-UNAPPROVED**. The synced v01 files are immutable superseded baselines, also UNAPPROVED. No runtime code, scene wiring or test harness changed.

Counters unchanged: weighted MVP **40.8%**, scenes **3/12**, sprites **0/52**, M2 **10/12** (not accepted), human playtests **0/2**. Zero-change receipt: `closeout-20261017-204712-707d78de`.

## The gap

In a clean checkout of `00199fc`:
- the Chicago check stopped at C2 with `FileNotFoundError`, because it reads three v01 captures;
- the Washington check could not pass S5 or C3–C5 and C7, because it reads the v01 manifest, its 16 pinned files and 16 v01 captures.

## What is synced (40 files, 4,929,361 bytes)

Every file was audited by path, size and sha256. Nothing was batch-added by directory.

**Chicago (3 PNGs, 136,228 bytes).** `outputs/chicago-loop-state-lake-v01/after/…state-lake-godot-{zh-arrival,en-arrival,zh-approved-heroine-ref}-640x360_v01_20261017-031308-509a5e64.png`. These are exactly the three files that `V01_CAPTURES` reads for C2.
- **Provenance:** v01 (`26d71e3c`) Godot captures. Their `flat_stats` recomputed in the export equal the v01 values in the committed v02 report (zh arrival: 686 colours, edge density 0.4177).

**Washington (37 files).**
- the v01 manifest `…scene-and-fixtures-manifest_unapproved-v01_20261017-030801-65b9618f.json`;
- its 16 pinned files:
  - 12 sources in `outputs/wdc-sr1-v01_65b9618f/`: `.png`, `.ora` and `.pxo` for the scene and the 3 fixtures;
  - 4 runtime PNGs: 1 under `game/assets/environments/wdc-survey-room1/` and 3 under `game/assets/props/wdc-annex-room1/`;
- 4 matching `.png.import` sidecars. Their UIDs are unique, and `--import` left them byte-identical (ignoring CR);
- 16 v01 captures: 8 in `before/` and 8 in `after/`. S5 requires exactly 16.
- **Provenance:** all 16 manifest files match the v01 manifest's sha256. All 16 captures match the `v01_capture_sha256` map in the committed v02 report `…pixel-source-pixelorama-check-report_v02_20261017-160235-e3b74490.json`.
- **Runtime:** the v01 runtime PNGs are not referenced by any game script, so they only add about 30 KB of unused imports.

## Deliberately left local (not read by any v02 gate)

- **Chicago v01:** the other 3 `after/` captures, 2 `before/` captures, the `.pxo`, `.ora`, preview, walkmask, layer manifest and v01 check report.
- **WDC v01:** the check report `…v01_20261017-030801-92521a7f.json`.
- **v01 QA notes, author and check tools:** not needed by the v02 checks.

No gate was made optional, and no check was weakened.

## Verification on an export of the exact staged index

The export was made with `git checkout-index` with `core.autocrlf=true` and `core.longpaths=true` (repo policy), under `C:\wb\v01s-…`. Real Pixelorama 1.2.3 was used with a temporary APPDATA, and Godot 4.7.2 came from the main tree's `work/tooling`.

| Check | Result |
|---|---|
| Chicago pixel/source check | **13/13 PASS**, including S1 byte-exact rebuild, P1–P2 Pixelorama, G3 runtime wired to v02, C2 v02 denser than v01 |
| Washington pixel/source/Pixelorama check | **15/15 PASS**, including S5 (16 files and 16 captures), C3–C5, C7 (other rooms pixel-identical to v01), P1–P3 |
| Godot `--headless --import` | exit 0, no errors |
| `m2_smoke.gd` | `M2_SMOKE_OK` |
| `m7_smoke.gd` | `M7_SMOKE_OK` |
| US science migration smoke | `US_SCIENCE_MIGRATION_SMOKE_OK checks=32` |
| Export data inclusion smoke | `EXPORT_DATA_INCLUSION_SMOKE_OK mode=source checks=24` |
| Meter `check` | `CHECK OK`, 40.8% |

## Remaining limitations

- **Tools outside the repo.** Pixelorama and Godot binaries live under gitignored `work/tooling`, so a fresh clone must supply them with `--pixelorama` or the default path.
- **Windowed captures not re-run.** The Godot capture checks (Chicago 42, `WDC_V02_ALL_OK`) are windowed and were not re-run. Their v02 captures are committed and were re-verified through C1/C2.
- **One line-ending policy tested.** Only `autocrlf=true` was exported. The added text files (`.import`, manifest JSON) are parsed, not byte-hashed.
- **Not approval.** This is not creator approval of any art.
