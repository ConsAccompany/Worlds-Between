# Three v02 candidates: selective Git integration and task closeouts

Recorded 2026-10-17 at 16:33 EDT by Claude Max firstParty (`ANTHROPIC_API_KEY` absent). This follows the dispatch `docs/coordination/rpg-2-star-ocean-the-second_v02-candidate-selective-integration-dispatch_v01_20261017-163000-8f42a6b1.md`.

**Status:** two scene candidates are synced as **technically verified, creator-UNAPPROVED** runtime candidates. The male static v02 gets a zero-change receipt only. Nothing here is creator acceptance.

## Unchanged gates

- Science scene visuals **3/12**
- Runtime sprites **0/52**
- Post-art human playtests **0/2**
- M2 **10/12** (not accepted)
- Science-sphere playable content **3/4**
- Core gameplay **5/5**
- Weighted MVP estimate **40.8%**

`approvalLedger` items and counters are not edited, and neither are `formalApproval`, steps or `m2Expansion.gates`. The three task closeouts are zero-change receipts, each recorded 40.8% → 40.8% with the meter CLI:

| Receipt | Task |
|---|---|
| `closeout-20261017-203400-5ca4d812` | Chicago |
| `closeout-20261017-203401-3878b3eb` | Washington |
| `closeout-20261017-203402-cf4b3ed4` | Male static |

They are staged index-only, as the HEAD progress state plus these three receipts. The other sessions' uncommitted progress-state edits stay out of the commit.

## 1. Chicago Loop State/Lake v02 (`55667f46`): synced, UNAPPROVED technical arrival placeholder

QA note: `docs/qa/rpg-2-star-ocean-the-second_chicago-loop_state-lake-arrival-block-native-scene_qa-note_unapproved-v02_20261017-160959-6bcff07f.md`

**Codex review (real zh and en 640×360 captures).** It improves on v01, but it is still a technical arrival placeholder, not landmark-final art. Remaining problems:
- texture grain;
- generic architecture;
- the heroine is fully hidden when she stands directly behind an L column shaft.

Scene count stays 3/12 and M2 stays 10/12. The in-game badge still reads "Technical placeholder · Art not accepted".

**Provenance.** Most pixels are a **quantized, generated, continuous-colour reference**, not native pixel art. Only the bench, the State/Lake station plate and the flag banner are hand-pixelled. The reference PNG `…elevated-rail-walkable-block-art-direction-nonruntime-v02_20261016-195030-8c456a73.png` is synced, because the author tool pins its sha256 and cannot rebuild without it. Its attribution sidecar is `outputs/rpg-2-star-ocean-the-second_chicago-loop_elevated-rail-walkable-block-art-direction-attribution_nonruntime-v02_20261017-163336-89f38425.md`. The original generation prompt was not saved, and the sidecar says so.

**Runtime wiring.** One `.tscn` line now points the Loop scene at the v02 script. To revert, point that line back at `…district-placeholder-scene_m2-v02…gd`. In Git that file is still the earlier code-drawn placeholder. The uncommitted v01 art version of it was not synced.

**Line endings.** The v02 source check byte-hashes the `.gpl` palette (LF). This sync adds a path-scoped `text eol=lf` rule for that one file to `.gitattributes`, following the NYC v03 precedent, so that `autocrlf=true` clones keep gate S1.

## 2. Washington survey annex room 1 v02 (`71300729`): synced, UNAPPROVED

QA note: `docs/qa/rpg-2-star-ocean-the-second_wdc-annex-room1_capitol-interior-v02-quality-pass_qa-note_unapproved-v02_20261017-160235-f1e4f2a0.md`

**Codex review (real zh and en 640×360 captures).** v02 is richer than v01, and the header and fixture problems are improved.

**Provenance.** About 95% of the visible background (155,689 of 163,840 play-area px) is a **palette-reduced underpainting** of the Codex-generated reference `…capitol-civic-interior-art-direction-reference_nonruntime-v01_20261017-032700-a82fde43.png`. That reference was itself an edit of the old m8-concept plate. The reference PNG and its prompt file (`…-reference-prompt_nonruntime-v01_20261017-032700-a82fde43.md`) are synced as rebuild sources.
- The scene is **not** wholly hand-painted and is not creator-approved.
- Only the hand layers (8,151 px) and the three 64×64 fixtures are hand-drawn.

Scene count stays 3/12.

**Runtime wiring.** The whole `game/scripts/survey_annex.gd` diff against `776db55` is the v02 room-1 change (+92/−11). It is gated to `room == 1 and destination_id == "scifi.ruins"`, and every hunk was reviewed. The file carries no other session's work.

## 3. Male protagonist south idle HD static v02 (`160419`): zero-change receipt; candidate not synced

QA note: `docs/qa/rpg-2-star-ocean-the-second_protagonist-male_south-idle-high-density-static-pilot_qa-note_unapproved-nonruntime-v02_20261017-160419-ba29a498.md`

**Codex review (bright and dark Godot comparisons).** The male is still visibly coarser than the approved female v8 static baseline. It stays **NONRUNTIME and UNAPPROVED**, and no sprite is counted.

**What is synced.** Only the QA note, a text document with no art, so that the zero-change receipt's evidence resolves on GitHub. The PNG, `.pxo`, `.ora`, palette, manifest, tools, preview and captures stay local. The QA note pins them by sha256.

**Why the rest is not synced.** It would add a rejected-quality art candidate to the repo without making any gate checkable.

## Tests

**Reused, not rerun.** The evidence in the two scene QA notes was checked against the files:
- **Chicago:**
  - `CHICAGO_LOOP_V02_OK checks=42 runtime_scene=true` (Godot 4.7.2, windowed);
  - the pixel/source check report gives 13/13, with all gates true;
  - 8 headless regressions OK: US science migration 32, M2, M7, global travel core, whole-hour 246, export inclusion, earth map 212, map travel integration 108.
- **Washington:**
  - `WDC_V02_ALL_OK`;
  - the pixel/source/Pixelorama check report gives 15/15 PASS;
  - `M7_SMOKE_OK`.

**Re-verified for this sync.** Every file pinned by the two manifests matches its sha256: Chicago 13/13, Washington 21/21.

**Run on an export of the exact staged index.** The export was made with `git checkout-index` and `autocrlf=true`, under `C:\wb\v02x-20261017-163336`:
- **Meter:** `CHECK OK 40.8%`. All closeout evidence paths exist in the export.
- **Chicago pixel/source check, without Pixelorama:**
  - With no v01 baseline in the export, it **stops at C2** with `FileNotFoundError` on the v01 captures. This is the expected clean-clone gap.
  - With the 3 local v01 captures copied into the temp export only: **11/11 PASS**, including S1 (byte-exact rebuild plus the LF `.gpl` hash) and G3 (the runtime scene is wired to v02).
- **Washington pixel/source check:**
  - With the local v01 baseline copied into the temp export only, 12/12 non-Pixelorama gates pass: S1–S5 and C1–C7.
  - P1–P3 are false only because Pixelorama was deliberately not supplied. The QA run's 15/15 covers them.
- **Godot 4.7.2 headless,** after `--import` on the export (exit 0):
  - `M2_SMOKE_OK`
  - `M7_SMOKE_OK`
  - `US_SCIENCE_MIGRATION_SMOKE_OK checks=32`: it flies to Chicago, loads the Loop scene through the v02 script, then saves, returns and loads the save.

## Not synced (local only)

- **v01 baselines.**
  - `outputs/chicago-loop-state-lake-v01/`, its assets and tools;
  - `outputs/wdc-sr1-v01_65b9618f/`, its v01 runtime PNGs and tools.

  These are superseded candidates. Several v02 comparison gates read these local files, so in a clean clone those gates fail until the baselines are synced or made optional:
  - Chicago C2 (v02 denser than v01);
  - Washington S5, C3–C5 and C7.

  The v02 rebuild and source gates do not need them: Chicago S1–S4 and G1–G3, Washington S1–S4.
- **Chicago test scene.** `game/scenes/…state-lake-block-scene_unapproved-v02_….tscn` was used only for the pre-wiring check.
- **Godot cache churn.** `game/scripts/…district-placeholder-scene_m2-v02_….gd.uid`.
- **Male candidate.** Everything except its QA note.
- **Other dirty files.** All other dirty or untracked files belong to other sessions, including `battle_arena.gd`, the readiness checklist, the Game Bible app and server, `docs/progress.md`, and the other 12 worktree-only receipts in the progress state.
