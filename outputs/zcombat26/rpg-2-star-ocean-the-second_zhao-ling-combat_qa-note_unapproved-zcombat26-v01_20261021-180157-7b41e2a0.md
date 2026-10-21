# Zhao Ling combat static + eight source actions — zcombat26 v01 QA note (UNAPPROVED)

Status: production source package only. Art and motion are NOT approved, this is NOT a default, and the runtime is NOT wired. Ledger tasks
`content.combat.zhao-ling.combat-static` / `combat-actions` are not updated here (the coordinator owns the ledger).

- Base revision: 13e59cc (worktree cl-zcombat). Author tool:
  `tools/rpg-2-star-ocean-the-second_zhao-ling_combat-static-and-actions-author_unapproved-zcombat26-v01_20261021-180157-5d3c9a71.py`,
  sha256-text-lf-v1 (CRLF->LF) `cb923d9aaa94d65853e0827791e2f493ab741ec330aae552ddbfffa898214535`. Binary hashes: see the author manifest / file list.
- Method: the proven mcombat22 rig/raster/ORA code and the established PXO writer (female south-run v06 `make_pxo`). The costume,
  body, handgun and fx are Zhao's own; the Zhao palette is the literal zexplore25 PAL. Identity refs: portrait
  `outputs/rpg-2-star-ocean-the-second_zhao-ling_character-sheet_v01_20261013-193120-54215370.png` (concept only, not approval) and the
  zexplore25 east static.
- Contract: 136x144 cell, pivot (64,136), right-facing, logical scale 0.5, display proportion "0.65", 30 tick/s, 6-column sheet (23 cells).
  Actions are idle/move/guard/attack/dodge/skill/hit/defeat, each with the same total ticks as heroine hsc19. Character is `{"member_id":"zhao-ling"}`.
  The runtime index has only the `zhao-ling` key and no hero key. No victory poses.
- Attack: the muzzle flash is frame 0 (tick 0), followed by recoil (muzzle rises, hand pulls back, smoke and casing), hold, recover.
  The existing immediate companion attack is unchanged and no delayed damage is implied. Skill (Echo ranging) runs tune (hand off,
  eyes shut), antenna ping rings, tablet ranging sweep, then target lock reticle.
- Files: 23 poses + battle still, each as a native PNG, an 11-layer ORA and a single-frame 11-layer PXO, all in `outputs/zcombat26`.
  The sheet, runtime manifest, member-only index and author manifest are in `game/data/zcombat26`; the sheet and manifest also have copies in outputs.

## Commands (from the worktree root; PY = C:/Users/hkzha/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/python.exe)

    $PY -X utf8 -I tools/<tool>.py build                         -> ZCOMBAT26 BUILD PASS 211/211
    $PY -X utf8 -I tools/<tool>.py check                         -> ZCOMBAT26 CHECK PASS 290/290 (source-check-report json)
    $PY -X utf8 -I tools/<tool>.py check --pixelorama <P>/work/tooling/pixelorama-1-2-3/Pixelorama-Windows-64bit/Pixelorama.exe
                                                                 -> ZCOMBAT26 CHECK PASS 291/291 (source-check-report-pixelorama json)

Gates cover: deterministic rebuild; on-disk bytes; binary alpha and palette; margins, grounded/airborne rows and limb stretch; full layers;
PNG == composite == ORA merged == PXO cels; identity texels; male palette absent; consecutive frames differ; contract and tick schema;
member-only index; firing cue at tick 0; recoil direction; skill fx order; sheet cells; silhouette IoU against the heroine and male idles; names.

Native Pixelorama 1.2.3 headless export: all 24 PXOs give a flat export exactly equal to their PNG. The split-layer exports of the still,
attack-fire, skill-sweep and defeat-down match every non-empty source layer exactly (11/11, 10/10, 11/11, 10/10).
**Disclosed diagnostic:** each run prints the known renderer line
`ERROR: Condition "!actions.custom_samplers.has(function->arguments[j].tex_builtin)" is true. Continuing.`
So the native result is exact but not diagnostic-clean. GUI Save As was not verified.

## Limitations

- These are authored rig poses, not hand-finished frames. Normal-speed motion review, arena evidence and creator review are still pending
  (Codex owns the arena evidence).
- Light comes from the upper left on a right-facing side view. The left-hip radio and left antenna are on the far side and only peek out.
  The head and earcup read large; the bob silhouette is simple; trouser roll cuffs are blocky. These are cosmetic and deferred per the MVP rule.
- Only static checks were run. No Godot load of this set has been run here.
