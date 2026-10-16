# Washington Capitol west grounds v06 — clean-clone `check` closure addendum (Task K, UNAPPROVED, NONRUNTIME)

- **Date:** 2026-10-16. **Stamp/id:** `20261016-110135-03d32c38`. Addendum to `docs/qa/rpg-2-star-ocean-the-second_wdc-capitol-west_walkable-scale-depth_qa-note_unapproved-v06_20261016-071733-18b9cea3.md`. That note's body and erratum are unchanged.
- **Author:** Claude (Claude Code, Opus 5.5), signed-in claude.ai Max, firstParty only. No API billing, credits, auto-reload or paid fallback.
- **Status:** v06 stays **UNAPPROVED, NONRUNTIME**, not wired. Science scenes stay **0/11**.
- **Not touched:** no runtime file, no completion state, no counter, no Game Bible, no `docs/progress.md`, no Git commit.
- **v06 art is byte-identical:** no candidate or output file was rewritten (16/16 pinned digests match).

## Problem (reproduced on unmodified main `4245dd2`)

In a fresh clone (`core.longpaths=true`), `check` had two defects:

1. **`core.autocrlf=true`** (this machine's system default): `check` stopped before any gate with `…scene-palette….gpl on disk differs from a fresh rebuild`.
   - The `.gpl` is text, so Git checks it out as CRLF (136 CR bytes).
   - The rebuild comparison was byte-exact.
2. **`core.autocrlf=false`**: `FAIL`, with `v05_v04_and_vista_v02_untouched = false`.
   - LOCK hashes `game/assets/environments/candidates/wdc-capitol-west-v04_20261016-004457-a17af0a6/`, which is untracked and absent from any clone.
   - `lock_digest()` also returned the hash of an empty listing for a missing path, so "missing" and "changed" were not distinguished.

## Fix (builder only; LOCK data unchanged)

1. **`LOCK_OPTIONAL_IF_ABSENT = {v04 candidate dir}`.** The `LOCK` dict, including the recorded v04 hash `b0b959f5…f3c4`, is unchanged; the stored manifest embeds it.
   - **Condition (documented in the tool):** v04 is a historical sibling, not an input. The v06 tool reads nothing from it; its only other mention is a docstring metric comparison.
   - **If the v04 dir exists, it must still match exactly.** If it is absent, the entry is reported `present: false, status: "absent: …"` and listed in `lock_optional_absent`.
   - Every other entry is tracked and stays **mandatory**: v05 candidate dir, v05 outputs dir, v05 tool, v05 QA note, v05 Codex audit, real-site audit, and vista v02 dir.
   - Every entry now gets an explicit existence check, so a missing mandatory path reports `MISSING` instead of an empty-listing hash.
2. **`OWN_ARTIFACTS`:** this run's 7 candidate and 9 output files are pinned to the digests already recorded in the v06 note.
   - Text files (JSON, `.gpl`) use `t:` CRLF→LF; the others use `b:` raw bytes.
   - `own_artifacts_check()` must be 16/16 for `result: PASS`.
   - It is reported as `own_artifacts`, outside the `gates` dict, so the technical gate set stays **47**, the number the erratum and the Game Bible cite. Before this fix, only 5 of the 7 candidate files and none of the 9 outputs were verified.
3. **Rebuild comparison of the `.gpl` is line-ending independent** (CRLF→LF on both sides). `.pxo`, `.ora` and the PNGs stay byte-exact.
4. **New `--godot <exe>` option.** The default is still the gitignored `work/tooling/godot-4-7-2/…console.exe`, which a clean clone lacks.
5. **Console summary** now prints `gates_passed`, `lock_optional_absent`, `own_artifacts` and `own_artifacts_failed`.

**Builder:** `tools/rpg-2-star-ocean-the-second_wdc-capitol-west_walkable-scale-depth_pixelorama-build_unapproved-v06_20261016-071733-18b9cea3.py`
- now 4,135 lines (+71 / −8);
- sha256-text-lf-v1 `aa7baec94e74f93f751c859b77c311f9c410dfa42d1f7aa3f584a65777a38e66`. This replaces the note's `d672021e…` for the tool only.

**New test:** `tools/rpg-2-star-ocean-the-second_wdc-capitol-west_v06-check-closure_lock-test_unapproved-v06_20261016-105556-10745f41.py`
- 132 lines, sha256-text-lf-v1 `42603f395ca0e98fdae059a0c785a99bc7629a17f2029849104e291ee2d98ad9`.
- It imports the builder and points its `REPO` at a throwaway mirror under `%LOCALAPPDATA%\Temp` (extended-length paths). It mutates the mirror and never writes to the repo.

| case | expected | result |
|---|---|---|
| 1 baseline | LOCK ok, own 16/16 | PASS |
| 2 v04 absent | LOCK ok, v04 reported absent | PASS |
| 3 v04 present but changed | LOCK **fails** (`MISMATCH`) | PASS (skipped where no v04 dir exists) |
| 4 v05 candidate dir absent | LOCK **fails** (`MISSING`) | PASS |
| 5 vista v02 file changed | LOCK **fails** | PASS |
| 6 v06 capture changed by one bit | own artifacts **fail** (15/16) | PASS |
| 7 v06 candidate JSON as CRLF | own artifacts still 16/16 | PASS |
| 8 v06 `.gpl` absent | own artifacts **fail** (15/16) | PASS |

## Verification

| tree | test | full `check` (Pixelorama 1.2.3 + Godot 4.7.2) |
|---|---|---|
| main working tree (v04 present) | 8/8 | **PASS, 47/47 gates, own 16/16**, `lock_optional_absent: []` |
| fresh clone `C:\wb\k6t` at `4245dd2`, `autocrlf=true`, + the 2 files | 7/7 (case 3 skipped) | **PASS, 47/47, own 16/16**, v04 absent |
| fresh clone `C:\wb\k6f` at `4245dd2`, `autocrlf=false`, + the 2 files | 7/7 (case 3 skipped) | **PASS, 47/47, own 16/16**, v04 absent |

- Both clones had a `git status` of only `M` builder and `??` test, before and after.
- `4245dd2` equals `origin/main` after `git fetch`.

**Clean-clone command (Git Bash):**

```sh
git -c core.longpaths=true -c core.autocrlf=true clone <repo> C:/wb/k6t && cd C:/wb/k6t && git config core.longpaths true
# copy the 2 changed/new tools files listed above into tools/
mkdir -p "$LOCALAPPDATA/Temp/wb-taskk-appdata-k6t"
PY=/c/Users/hkzha/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/python.exe
$PY -I -B tools/rpg-2-star-ocean-the-second_wdc-capitol-west_v06-check-closure_lock-test_unapproved-v06_20261016-105556-10745f41.py
APPDATA="$(cygpath -w "$LOCALAPPDATA/Temp/wb-taskk-appdata-k6t")" $PY -I -B \
  tools/rpg-2-star-ocean-the-second_wdc-capitol-west_walkable-scale-depth_pixelorama-build_unapproved-v06_20261016-071733-18b9cea3.py \
  check --godot "<main checkout>\work\tooling\godot-4-7-2\Godot_v4.7.2-stable_win64_console.exe"
```

The same commands were run with `autocrlf=false` in `C:\wb\k6f`. No `--write-report` was used, so no evidence file was rewritten.

## Pixelorama guard — isolation and its limitation

- A Pixelorama 1.2.3 GUI from another session was open the whole time (PID 50828, untitled). It autosaves `%APPDATA%\pixelorama\backups\2026_10_15_13_56_34\(untitled backup)-…` about every 62 s and rewrites `.running` about every 15 s. That GUI was not touched.
- **Isolated guard dir:** every `check` ran with the parent `APPDATA` set to an empty temp dir (`%LOCALAPPDATA%\Temp\wb-taskk-appdata-<tree>`). Each headless Pixelorama/Godot child still got its own fresh fake APPDATA from the tool.
- All 6 Pixelorama runs ran without a guard kill, and `pixelorama_isolation_held` was true in every tree. The parent temp dir was still empty afterwards in all three runs.
- **Limitation:** in this mode the tool's built-in kill-switch watches the empty `<temp>\pixelorama`, not the real `%APPDATA%\pixelorama`. So `pixelorama_isolation_held` proves only that the children did not write to the parent APPDATA.
- **Covering the real dirs:** an independent before/after `(size, mtime)` snapshot of the real `%APPDATA%\pixelorama` and `%APPDATA%\Godot` (240 entries) was taken around each run.
  - The only changes were the GUI's `.running` heartbeat and its own untitled backup.
  - In the main and `k6t` runs there was also log rotation under `Godot\app_userdata\Worlds Between\logs\`, which is the real game project.
  - The tool's Godot gates use throwaway temp projects with fake APPDATA. The `k6f` run, with identical gates, showed no Godot change. So the log rotation is attributed to another session running the game project, not to this check.
- Running plain `check` against the real APPDATA while that GUI autosaves will still trip the kill-switch, as the erratum recorded. That is the guard working, not a defect.

## Remaining

- v04 itself stays untracked. Syncing or deleting it is its owner's call. With this fix it is no longer a clean-clone blocker, and it is still verified wherever it exists.
- The Game Bible's `47/47` stays correct; nothing there needs changing.
