# Heya NORTH walk/stop — batch174 source reconciliation (UNAPPROVED)

- Task: `content.char.heya.walk-north` (canonical ledger task, `todo` before this provider report; owner DeepSeek).
- Dependency: `content.char.heya.static-north` DONE. Evidence `outputs/heya-n152/author-check.log` ends
  `HEYA_NORTH_V01_ALL_OK`; the north static manifest/PNG/PXO/ORA/palette pins are byte-exact. The batch171
  verdict’s fit paragraph is superseded by this note’s capture-r4 evidence; its source/independent paragraphs
  remain valid.
- Scope: north only. This is a bounded reconciliation of the existing batch171 source production, not a new
  candidate, visual revision or polish pass.
- Status: **source production verified**; **not** runtime-integrated, **not** default-adopted, **not** art/motion
  approved. This provider made no shared ledger/Bible/registry/Git-index edit, commit or push.

## Result

1. The batch171 author source is unchanged and still deterministic.
2. The independent checker passed again from a fresh `outputs/heya-nw174-provider/independent` directory:
   **37/37 checks PASS**, **14/14 negative controls rejected**, native Pixelorama export **41/41 RGBA-exact**.
3. The existing normal-speed Godot fit contained a real continuity defect in its *test expectation*: capture-r3
   selected the literal `phase7` stop bridge while the frozen timing puts the last walk frame at **phase 11**.
   The pre-fix independent audit **FAILED** (`outputs/heya-nw171/fit-repair/...pre-fix-continuity-failure...`).
   That failure and the capture-r3 proof are retained.
4. The test-only fit driver/script were repaired to derive the stop entry phase from the frozen timing and to
   assert every stop/reverse endpoint. A fresh capture-r4 fit passed **12/12 captures**, and the independent
   post-fix continuity audit satisfied **17/17 continuity checks** (12 boolean predicates + 5 derived phase/restore values). Exact targets, 40 ms walk, 120 ms inclusive settle,
   pivot, scale and all source hashes are unchanged. The repair corrected an incoherent test expectation; it did
   not weaken a source, contact or slip criterion.
5. No production art source byte was rewritten in this reconciliation. No `wb_safe_replace.py` installation was
   needed because no differing production asset was replaced here.

## Commands actually run (repo root)

```bash
V=/home/kel/projects/worlds-between/tooling/venv/bin/python

# 1. pre-run evidence snapshot; existing check result copied for byte comparison
mkdir -p outputs/heya-nw174-provider/pre-run
cp -p outputs/heya-nw171/rpg-2-star-ocean-the-second_heya_walk-check-result-check_unapproved-hnw171-v01_20261024-151500-7a5e4da3.json \
      outputs/heya-nw174-provider/pre-run/

# 2. deterministic source author check (installed tree)
$V -X utf8 -I tools/rpg-2-star-ocean-the-second_heya_walk-north-source-author_unapproved-hnw171-v01_20261024-151500-hnw17101.py check

# 3. independent checker in a fresh provider directory
$V -X utf8 -I tools/rpg-2-star-ocean-the-second_heya_walk-north-independent-check_v01_20261024-151500-hnw17101.py \
   --out outputs/heya-nw174-provider/independent

# 4. repaired bounded Godot normal-speed source-fit (new capture-r4; existing runs untouched)
$V -X utf8 -I tools/rpg-2-star-ocean-the-second_heya_walk-north_normal-speed-fit_v01_20261024-151500-hnw17101.py

# 5. independent continuity audit of capture-r4 (capture-r3 pre-fix failure retained)
$V -X utf8 -I outputs/heya-nw171/fit-repair/rpg-2-star-ocean-the-second_heya_walk-north_fit-continuity-audit_v01_20261024-151500-hnw171fr01.py \
   --manifest outputs/heya-nw171/fit/capture-r4/rpg-2-star-ocean-the-second_heya_walk-north_normal-speed-manifest_test-only-v01_20261024-151500-hnw17101.json \
   --runtime game/assets/characters/heya-native-v01/north-walk/rpg-2-star-ocean-the-second_heya_walk-sprite-set-runtime_unapproved-hnw171-v01_20261024-151500-1eff5ab7.json \
   --stop game/assets/characters/heya-native-v01/north-walk/rpg-2-star-ocean-the-second_heya_walk-stop-transition-supplemental_unapproved-hnw171-v01_20261024-151500-4a055ed1.json \
   --proof outputs/heya-nw171/fit/rpg-2-star-ocean-the-second_heya_walk-north-normal-speed-proof_test-only-v01_20261024-151500-hnw17101-capture-r4.json \
   --out-json outputs/heya-nw174-provider/fit-repair-post/rpg-2-star-ocean-the-second_heya_walk-north_post-fix-continuity-pass_unapproved-hnw174-v01_20261024-152000-hnw17401.json \
   --out-md outputs/heya-nw174-provider/fit-repair-post/rpg-2-star-ocean-the-second_heya_walk-north_post-fix-continuity-pass_unapproved-hnw174-v01_20261024-152000-hnw17401.md \
   --label "post-fix (capture-r4, repaired phase-derived fit)"
```

### Observed results

| Run | Result | Exit |
| --- | --- | --- |
| author `check` | `REBUILD 91/91  DETERMINISTIC True`; `SOURCE 20/20`; `RESULT PASS []` | 0 |
| independent checker | `INDEPENDENT PASS 37 / 37`; 14/14 negative controls rejected; native export 41/41 exact | 0 |
| repaired Godot fit | `HEYA_HNW171_NORTH_WALK_NORMAL_SPEED_FIT PASS`; 12/12 captures; 2.509 s | 0 |
| post-fix continuity audit | `independent_continuity_passed: true`; `verdict: PASS`; 17/17 continuity checks | 0 |

Author contact summary (unchanged from batch171):

```json
{"walk_max_world_slip_src_at_40ms_boundaries": 11.2,
 "walk_max_world_slip_logical_at_40ms_boundaries": 5.6,
 "flight_phases": [4, 5, 10, 11],
 "stop_bridge_grounded_slip_src_max": 0.0}
```

Independent contacts: each foot grounded exactly 4/12 phases; planted screen position constant while grounded;
all 12 stop bridges have grounded slip 0.0 and end on exact neutral feet/idle f00. The 11.2 source / 5.6 logical
px per 40 ms in-place residual is **retained and disclosed**, not footlocked and not slip-free.

The author check rewrote its result JSON to the same bytes (pre-run copy `cmp` byte-identical); no existing
evidence was changed.

## Authority / hashes (raw sha256 bytes, no EOL normalization)

| Artifact | sha256 |
| --- | --- |
| source author tool (unchanged) | `fb1eb8ab0cbb8d5724870548865641cfb4d4e96aca81d428f34542d6b487cd3d` |
| independent checker (unchanged) | `c1172e367b555fc03e8acb9bb50357c79b1530ee4d828822e4a009c52bd9c987` |
| fit driver — before repair (backed up) | `3081ad29585a2e68c35ace0829dd99a4928f3e8afb714cb566e752a5c7d18cd5` |
| fit script — before repair (backed up) | `258a49144fcde9ddb5a6ab5fd7bdc85b2a86b028c708182993ffcd71f10d0c16` |
| fit driver — intermediate rev1 (backed up) | `cc80fdde10d08779fb9680ea8fed4140d85b8298fa5b8473c4e2619bbda084ff` |
| fit driver — repaired / authoritative | `c98cf10d377db6ee52e33f0401cc3665aa652d242730dca318840e272a5c4a82` |
| fit script — repaired / authoritative | `35549040f924306b00d85bf7511a549b3ed702f7fa2437496e90229c7fd968ed` |
| continuity audit script | `cc5fe601ca551dd5cb2fec323838a89229693151557b3589c48445a53b48353e` |
| source manifest | `e9da00e81607a3ae147b16ec8559dab62df8a66fde5cec571968852912b94bb2` |
| editable PXO | `4045153a0cccd4223be7e2780e07844074f55e90ef9b02c43e8cdccf272c6347` |
| editable ORA | `a5df335d628f39a109265d7f17cb165aea542be40e3d3c08f05ab27cee0c64ee` |
| runtime sprite set | `0bb769b19247b6a986b34d7b82528c155402ef621ab12c573bf3d27012cabed6` |
| stop supplemental | `5050b1ee4b3901d3f0491b9345d993078015bdfd1329ea8fbb4d90c354e2c1a5` |
| pre-fix continuity failure JSON | `9054c25d2952f8c57ae9de51c307c88bdc229d85523522139e6e63e48aec17ac` |
| capture-r3 proof (self-reported pass, audited FAIL) | `66c301a97c667a4dc09cfd9ebcc47aa23d79b7540f9191c4130541970eb1e31a` |
| capture-r4 fit manifest | `60b5c6c6b1f02e057107b3dc5f27c64c325f4039a5277cfcfd27007b264acef1` |
| capture-r4 fit proof (PASS) | `0fca940f8933b3989810d5b546f3857b5dc4986421768dc9d2cb9f6d25ba6f97` |
| batch174 independent result | `a9b9406d91d5c9b078833bfb51cbfc4ff9b65ad89373df260d0659ef69861407` |
| batch174 post-fix audit result | `ef48575f783c6995c0655dd5c032ee97ff53be8ae4b3a4214a318ad37173d797` |
| batch171 source verdict (historical) | `feb294cff9ac0691850c8fc2d9838660c74ed71e952ee3f586757ecc07131e74` |

Backups with verified hash/metadata receipts: `outputs/heya-nw171/backups/20261024T150952Z_fit-gd-original_89b77aed/`,
`outputs/heya-nw171/backups/20261024T150952Z_fit-tool-original_d27a6db8/`,
`outputs/heya-nw171/backups/20261024T151023Z_fit-tool-rev1-intermediate_00421361/`. The current fit driver differs
from rev1 only by removing a dead mistyped Godot path line; the functional phase/continuity repair is covered by
the verified original and rev1 backups above.

## What changed, and what did not

Changed (test/evidence only):

- `tools/...heya_walk-north_normal-speed-fit...py` and `...test-only...gd`: derive the stop entry from frozen
  timing (`STOP_MS - 1` = phase 11), select the matching supplemental bridge, assert forward/reverse
  pre-stop == selected entry, assert every stop/reverse endpoint, and record `stop_phase`/`reverse_phase`.
- New capture-r4 fit output/proof and the batch174 independent/post-fix audit evidence.
- This QA note.

Not changed:

- The author tool, independent checker, 41 source PNGs, PXO/ORA editables, source manifest, runtime sprite set,
  stop supplement, package registry, `.gitattributes`/`.gdignore`, and all batch171 source bytes.
- Defaults, selectors, art/motion approvals, shared ledger/Bible/registry, and the Git index.

## Preserved failures / retained limitations

1. **Pre-fix fit continuity FAIL is retained.** capture-r3 self-reports `passed: true` but the independent audit
   re-derived phase 11, found the literal phase-7 bridge, and failed `forward_prestop_equals_selected`,
   `reverse_prestop_equals_selected`, `reverse_restore_equals_reverse_prestop` and
   `all_stop_and_reverse_endpoints_continuous`. This was a test-expectation defect, not a source-art defect.
2. North walk is **in place**: a planted foot travels 11.2 source / 5.6 logical px per 40 ms held frame. It is
   **not footlocked and not slip-free**. Stop-bridge grounded slip is 0.0 because the host is stopped.
3. Legs are static boot texels split at x=40 and lifted below the knee; no foreshortening. The A-line dress hem is
   torso-only, so a lifted boot can pass behind the static hem. Braid, scarf, coat, apron, bag and herb have no
   secondary motion.
4. Stop supplemental playback is **source scope only**; the generic loader still goes to immediate idle.
5. Native Pixelorama export is 41/41 RGBA-exact, but **4 application diagnostics** remain
   (`!actions.custom_samplers.has(...)`). GUI SaveAs/reopen was not tested. Export equality does not establish
   clean application behavior.
6. The independent checker’s source-bound GIF preview still uses an explicit release phase 7 for its visual
   composite; it is not the timing-derived fit. The authoritative timing evidence is capture-r4 (phase 11).
7. North only; package is opt-in/non-default and has no south/west/east entries.
8. No human art, motion, fluidity or normal-play acceptance is claimed.
9. **Historical backup-compliance caveat (batch171, not cured here).** The coordinator record
   `outputs/heya-nw171-coordinator/provider-source-edit-and-failure-history.json` states that the original
   north author-tool creation/edit did not have a pre-edit backup and that retrospective history is not
   retroactive compliance. This reconciliation did not rewrite that tool; its current bytes are hash-pinned and
   the deterministic check passes. The fit-tool repair recorded in this note does have the verified backups
   listed above. The current pass must not be read as proof of the missing historical backup.

## Production files required for scoped commit

The exact path-and-hash list is generated after this note as
`outputs/heya-nw174-provider/scoped-commit-manifest.json` (raw sha256). Required payload categories:

- Tools (4): source author, independent checker, repaired fit driver, repaired fit `.gd`.
- Runtime package (46): `game/assets/characters/heya-native-v01/north-walk/` — 41 PNGs, runtime sprite set,
  stop supplemental, package-local registry, `.gdignore`, `.gitattributes`.
- Source output (48): `outputs/heya-nw171/png/` 41 PNGs; editable PXO/ORA; source manifest; file list;
  build/check result JSONs; provider receipt.
- Authoritative independent evidence (4): `outputs/heya-nw171/independent-2/` result, contact sheet, native
  export log, source-bound GIF. (The run-1 `independent/` files and native/XDG frames are retained on disk but
  are not required production payload.)
- Authoritative fit evidence (15): `outputs/heya-nw171/fit/capture-r4/` 12 PNGs + manifest; capture-r4 proof;
  capture-r4 runner log.
- Failure/repair evidence (4): `outputs/heya-nw171/fit-repair/` pre-fix failure JSON/MD, audit script,
  pre-fix audit log. Retained alternate runs (capture, r2, r3 and their proofs/logs) and the verified tool
  backups are listed as retained evidence, not as new production bytes.
- QA (2): the existing batch171 source verdict and this reconciliation note.
- Batch174 verification evidence (11): author/checker/fit logs, fresh independent result/contact sheet/native
  log/GIF, post-fix audit JSON/MD/log, and the pre-run hash snapshot.

Explicitly excluded from the production payload: `outputs/heya-nw171/stage/` (staging rebuild tree),
`outputs/heya-nw171/godot-home/` (Godot/Xvfb cache and user data), and native/XDG test caches. They are
regenerable and not source/evidence bytes.

## State and next action

- **Source production:** complete and verified (author + independent + timing fit + continuity audit).
- **Runtime integration:** not done. The package remains opt-in/non-default; no normal-game selector or
  normal-host stop playback was changed or claimed.
- **Human art/motion approval:** not granted. Heya north static/portrait remain UNAPPROVED.
- **Canonical criterion:** after the coordinator commits the scoped source/package/checks above and records the
  evidence through the ledger CLI, the canonical `content.char.heya.walk-north` criterion
  (“north walk or run cycle and stop committed with contact / slip checks”) can be satisfied. It is not
  satisfied by an uncommitted provider report alone, and commit does not imply art approval.

No permission denial occurred in this reconciliation. `landlock-run: partial enforcement` is a sandbox notice,
not a denied operation. The only writes were under `outputs/heya-nw171/`, `outputs/heya-nw174-provider/`, and
this `docs/qa/` note; no other character direction, credentials, provider config or shared record was touched.

Bounded next action: coordinator independently inspects the source bytes, fresh independent run, capture-r4 and
post-fix audit, then stages the explicit scoped paths and performs the audited ledger transition. Do not adopt
defaults or infer creator art approval.
