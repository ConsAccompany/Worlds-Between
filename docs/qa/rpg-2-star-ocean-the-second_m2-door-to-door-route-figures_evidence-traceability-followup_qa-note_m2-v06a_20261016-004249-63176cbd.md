# M2 NYC–Chicago door-to-door route figures: evidence traceability follow-up (QA note, m2-v06a)

- Date: 2026-10-16 00:42 America/New_York.
- Scope: repository hygiene only. No travel figure, runtime data, gameplay code, test, art, Site source, Game Bible prose, `docs/progress.md` or source claim was changed. **No network calls were made**; only the final `git push`.
- Audited note: `docs/qa/rpg-2-star-ocean-the-second_m2-door-to-door-route-figures_offline-resume-runtime-held-v02_qa-note_m2-v06_20261016-003651-90b56d7c.md` (commit `16652a0`).
- **M2 door-to-door route-figures gate: stays OPEN.** The meter is unchanged at 35.0%.

## 1. Problem found

At `16652a0`, the v06 note's "Previous notes" list pointed at four research files that existed only in the local working tree, not on GitHub `main`. The committed v05 note (from `176e155`) also linked the untracked v04 note. Readers on GitHub could not follow the evidence chain v02 → v03 → v04 → v05 → v06.

| Linked file | State at `16652a0` | Action |
|---|---|---|
| v02 audit note `docs/qa/rpg-2-star-ocean-the-second_m2-us-science-route-figures_real-world-travel-audit_qa-note_m2-v02_20261015-195053-10d2525c.md` | local only | **published unchanged** |
| v03 curb note `docs/qa/rpg-2-star-ocean-the-second_m2-nyc-chicago-airport-curb-endpoints_v03-candidate_qa-note_m2-v03_20261015-200518-7c3e19a4.md` | local only | **published unchanged** |
| v03 candidate data `docs/qa/rpg-2-star-ocean-the-second_global-earth-travel_nyc-chicago-airport-curbs_m2-us-science-v03-candidate-nonruntime_20261015-200518-7c3e19a4.json` | local only | **published unchanged** (outside `game/`; the runtime never loads it) |
| v04 blocked note `docs/qa/rpg-2-star-ocean-the-second_m2-nyc-chicago-typical-door-to-door_resume-attempt-blocked_qa-note_m2-v04_20261015-224916-c4e1a7b2.md` | local only | **published unchanged** |
| v05 note and v05 candidate JSON (`…cfba3fc5`) | already committed (`176e155`) | none |

All four files are published with their content unchanged. The only difference is line endings: the working copies use CRLF, and Git stores LF under `core.autocrlf=true`. Their statements, figures and retrieval dates are the original authors' and were not edited.

## 2. Verification before publishing (offline, this session)

| Check | Result |
|---|---|
| v03 validator `%LOCALAPPDATA%\Temp\wb-m2v03-scripts\check_v03_candidate.js` re-run with Node on the v03 candidate JSON, `wb-m2v03-osm\curbways.json` and the saved Valhalla/OSRM responses. It is read-only: it uses only `fs`, `path` and `crypto`. | **ALL PASS, 41 `ok` lines**, exit 0 |
| SHA-256 of the 12 BTS monthly zips in `wb-m2v03-bts\dl\` | 12 of 12 appear in the v03 candidate JSON |
| SHA-256 of the Overpass snapshot `wb-m2v03-osm\curbways.json` | `606da1cf…354b5c`, as stated in the v03 note and JSON |
| SHA-256 of the v02 audit's BTS zips in `wb-bts-audit-1792108043\dl\` (`ot.zip`, `ot_1.zip`, `ot_4.zip`) | all three match the full hashes in v02 §8 |
| v04 §2 hand arithmetic (totals 329/299, raw 329.1/298.4, monthly n sums 11,611) | covered by the v03 validator's total, raw-total and n-sum checks above |
| Link targets inside the four notes | every `docs/`, `game/` and `tests/` path is tracked after this commit, except the one listed in §3 |
| Publishing safety | no credentials, tokens or e-mail addresses. Two notes contain `C:\Users\hkzha\…` temp paths; that path already appears in 79 committed files, so nothing new is exposed. |

**Not re-verifiable offline** (left as the original authors' dated claims): v02's OSRM re-queries and web quotations, and v03's Valhalla/OSRM queries beyond the saved-response hash checks. Those need network access.

## 3. Sources that remain local-only (deliberately not published)

- `docs/coordination/rpg-2-star-ocean-the-second_post-quota_three-workstream-dispatch-prep_unapproved-v01_20261015-223416-8b4cd70e.md`, linked from v04 as its dispatch. It is another workstream's unapproved coordination draft in an untracked folder and is not route evidence. **It is local-only; that link will not resolve on GitHub.**
- Everything under `%LOCALAPPDATA%\Temp\wb-*` (raw BTS zips, Overpass, Valhalla and OSRM responses, NYC TLC / Chicago summaries, and the scripts). The v02–v06 notes already label these as outside the repository. They are large raw downloads and are not committed. Their hashes are recorded in the notes and the v03/v05 JSON.

## 4. Files

- Added: the four files in §1 and this note.
- Changed: meter zero-change closeout `closeout-20261016-044315-944afcbc` (35.0% → 35.0%) in `outputs/rpg-2-star-ocean-the-second_mvp-progress_state_v01_20261013-183804-28a1c7e4.json`.
- Not changed: the v06 note (its links now resolve), travel data, scripts, tests, art, the Game Bible and other sessions' dirty files.
