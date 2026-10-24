# Heya four-direction idle — batch163 source QA closeout (UNAPPROVED)

Task: `content.char.heya.idle-anim`. Producer: DeepSeek via the authorized adapter. Coordinator: Hermes.
Status: **UNAPPROVED technical source closeout**; the existing four-direction bank is unchanged in animation
bytes and is ready for coordinator inspection/commit. This is **not** runtime/default adoption, not
`SpriteFrames` engine playback, not human motion review, and not art/style/gameplay acceptance.
This is a NEW batch163 addendum. The producer QA and the v02 repair addendum are preserved untouched.

Receipt: `outputs/heya-i159/batch163-provider/provider-receipt.json`
Fresh staging: `outputs/heya-i159/batch163-provider/staging/idle/`
Installed bank: `game/assets/characters/heya-native-v01/idle/`
New author tool: `tools/rpg-2-star-ocean-the-second_heya_idle-four-direction-author_unapproved-i163-v01_20261024-141806-h163b001.py`

## 1. Determination: false `76..103` statement is prose, not an unmet contract

The v02 addendum proved the manifest text `boots and lower-body rows 76..103 unchanged` is false: rows
76..89 move while composite sole rows 90..103 stay frozen. That is **inaccurate prose against the established
source model**, not a genuine unmet acceptance contract:

- The established idle model deliberately settles torso/leg rows (torso +1 source texel at f01/f02) and freezes
  only boots/composite sole rows **90..103**. The author and independent checks have always tested 90..103.
- Each direction manifest already carried the accurate `directions.planted_feet` statement
  (`boots layer and composite sole rows 90..103 identical in all 4 frames`); the false text was the separate
  `idle_model.planted_feet` sentence.
- Measured installed bytes: 90..103 frozen in all four directions/frames; 76..89 move in animated frames in
  all four directions. Freezing 76..103 would contradict the authored settle model.
- No frozen check or threshold was weakened. The 90..103 freeze check is unchanged; a **new** check binds the
  manifest prose to the measured rows (`..._manifest_planted_feet_prose_matches_measured_rows`, 4/4 pass).

Only `idle_model.planted_feet` changed, in the four direction manifests, from
`boots and lower-body rows 76..103 unchanged; no global sprite bob` to
`boots layer and composite sole rows 90..103 unchanged in all 4 frames; torso/leg rows 76..89 settle with the
torso group; no global sprite bob`. A byte diff of each replaced manifest against its backup shows exactly that
one JSON line. No PNG, PXO, ORA, palette or runtime sprite-set byte changed.

## 2. Revalidation (fresh outputs, historical reports untouched)

| Gate | Result |
|---|---|
| Deterministic rebuild | 34 files, `DETERMINISTIC True`; source pins exact |
| Author checks | **48/48** (4 prose/measurement + 4 direction geometry + 1 runtime geometry added), `INSTALLED 33/33`, `RESULT PASS` |
| Four directions / four frames / 1500 ms | south/west/north/east, 4 frames each, `[700,200,400,200]` = 1500 ms |
| Canvas/pivot/logical | 80x112, pivot `[40,104]`, display 0.5, 48 logical px, checked in each direction manifest and the runtime manifest; f00 == existing static PNG |
| Independent checker | `passed: true`, 4/4 directions, **5/5 negative controls rejected** |
| Native Pixelorama export v02 | 48/48 gates; export-gated verdict true; image equality true; export success true; input unchanged; **208/208 cells**; `diagnostic_clean: false` (8 `custom_samplers` lines/direction, retained) |
| Normal-speed source-fit v02 | 12 captures; **16/16 exact boundaries**; 2/2 malformed manifests rejected; **120 ms** original bound; checked runner + Xvfb 640x360x24 + OpenGL3 + **Dummy audio**; `PASS` |
| Lower-body measurement | `76..103` claim now false/absent; `90..103` frozen all directions; `76..89` move |
| Only manifests differ vs preserved i159 staging | 29/33 identical, exactly the 4 manifests differ; installed == new staging 33/33 |

The normal-speed proof is a **source-fit overlay only**. It is not a `SpriteFrames`/runtime engine loop and is
not claimed as one. No new engine-loop probe was added because the existing harness has no ordinary actor
runtime binding for this unadopted bank, and the task forbids scaffolding a replacement pipeline.

## 3. Executed commands and exits

```bash
cd /home/kel/projects/worlds-between/repo
# 1. initial build: exit 1, preserved tool bug (KeyError 'idle_model'), 34 files written,
#    no animation change; log outputs/heya-i159/batch163-provider/build.log
/home/kel/projects/worlds-between/tooling/venv/bin/python3 -I tools/rpg-2-star-ocean-the-second_heya_idle-four-direction-author_unapproved-i163-v01_20261024-141806-h163b001.py build

# 2. pre-install check: exit 1, 43/43 model checks, expected 4 installed-manifest differences only
/home/kel/projects/worlds-between/tooling/venv/bin/python3 -I tools/rpg-2-star-ocean-the-second_heya_idle-four-direction-author_unapproved-i163-v01_20261024-141806-h163b001.py check

# 3. four authorized backup+replacements: exit 0 each; receipts in
#    outputs/heya-i159/batch163-provider/backups/replace-receipts.jsonl
python3 tools/wb_safe_replace.py outputs/heya-i159/batch163-provider/staging/idle/<dir>/<manifest>.json \
  game/assets/characters/heya-native-v01/idle/<dir>/<manifest>.json

# 4. post-install check: exit 0; 43/43 then 48/48 after adding explicit pivot/logical geometry gates, INSTALLED 33/33, RESULT PASS
/home/kel/projects/worlds-between/tooling/venv/bin/python3 -I tools/rpg-2-star-ocean-the-second_heya_idle-four-direction-author_unapproved-i163-v01_20261024-141806-h163b001.py check

# 5. independent checker: exit 0; passed true, 5/5 controls rejected
/home/kel/projects/worlds-between/tooling/venv/bin/python3 -I tools/rpg-2-star-ocean-the-second_heya_idle-four-direction-independent-check_v01_20261024-140235-a159i001.py --out outputs/heya-i159/batch163-provider/qa

# 6. lower-body measurement: exit 0
/home/kel/projects/worlds-between/tooling/venv/bin/python3 -I tools/rpg-2-star-ocean-the-second_heya_idle-four-direction_lower-body-claim-measure_v01_20261024-141104-h159r002.py

# 7. native export repair v02: exit 0; 48/48, 208/208, diagnostic_clean false
/home/kel/projects/worlds-between/tooling/venv/bin/python3 -I tools/rpg-2-star-ocean-the-second_heya_idle-four-direction_native-pixelorama-check-repair_v02_20261024-141104-h159r002.py

# 8. normal-speed source-fit repair v02: exit 0; PASS
/home/kel/projects/worlds-between/tooling/venv/bin/python3 -I tools/rpg-2-star-ocean-the-second_heya_idle-four-direction_normal-speed-fit-repair_v02_20261024-141104-h159r002.py
```

Fresh evidence: `author-check-batch163-...-141849.json` (pre), `...-141903.json` (post),
`qa/...independent-check...141909.json`, `repair2/native-20261024-141912-ca768d77/...report...json`,
`repair2/...normal-speed-repair-proof...-r4.json`, `repair2/qa/...lower-body-claim-measure...141909.json`.

## 4. Changed paths and backups

Installed replacements (only these four):
`game/assets/characters/heya-native-v01/idle/{south,west,north,east}/...-manifest_...a159i001.json`

| direction | before SHA256 | after SHA256 | verified backup |
|---|---|---|---|
| south | `5d448bb4…ea9f2a` | `53a3f9ca…f3388` | `outputs/development-backups/d8c9b3cf41ea4265aede0f58aaad29d8/original` |
| west | `4e1b5406…794f28` | `b9289054…b5262` | `outputs/development-backups/5ddab4d8990f4b458226c61995d96690/original` |
| north | `ad711d0a…a90b1` | `8601dd23…dc5b0` | `outputs/development-backups/11be178a81e1442683cc35ef613c3a4c/original` |
| east | `3d11a0cb…a9f2a` | `0e9c8a9f…403821` | `outputs/development-backups/c4b7a32a5bd74d0fa202f90e91805adf/original` |

Exact full hashes, modes, mtimes and receipt paths are in `provider-receipt.json`. Backups are unique, verified
before replacement, and preserve mode `0664` and original mtime. Hashing is SHA-256 over raw bytes; the idle and `outputs/heya-i159/`
`.gitattributes` are `* -text -eol`, so no LF/CRLF normalization was applied. JSON text was decoded as UTF-8.

New (not overwritten): the batch163 author tool, `outputs/heya-i159/batch163-provider/`, fresh native/fit/lower-body
evidence, and this addendum. Preserved untouched: producer QA, v02 repair addendum, producer receipt,
`outputs/heya-i159/staging/`, `file-list.json`, prior failure logs and prior native/fit reports.

## 5. Preserved earlier failures

i159 draft2 guides-first PXO ordering failure and backups; failed independent reports `...T140508/140527/140542.json`;
Godot `AnimatedSprite2D` parse/type failure (`fit/failed-parse-r1`) and wrong-frame playback (`fit/failed-anim-r2`);
v01 native checker ignoring export exit/timeout; v01 `frame_at` stuck after 1500 ms and the 250 ms relaxation;
the false `2700 = 3` constant (`repair2/logs/failed-boundary-constant/`); producer QA's `224` cell arithmetic
(corrected to 208 in v02 and here, historical text preserved); the false `76..103` statement (preserved in the
historical manifests/backups, corrected here). A batch163 initial author-build `KeyError ('idle_model')` is
preserved in `build.log`; it was a tool bug, fixed by reading the staged manifest bytes, with no animation change.

## 6. Limits and scope confirmation

Limits: Pixelorama application diagnostics remain unclean (`custom_samplers`, 8 lines/direction); GUI
SaveAs/reopen, ordinary actor integration, `SpriteFrames`/runtime engine playback, save/reload, performance,
interaction, walk/stop/combat, human motion review and art approval were not tested or claimed.

Scope: only `content.char.heya.idle-anim` (existing four-direction Heya idle bank) was touched. No walk/combat/
runtime/default adoption, no new animation scope or cosmetic polish, no settings/permissions/pause change, no
shared ledger/Bible/registry/Git index/commit/push, no unrelated 153 staged files, no credentials/accounts/
billing/secrets/vault, no deletion or paid fallback. Existing default/creator approval state is preserved and
is not inferred from this technical QA. Coordinate commit remains with Hermes.
