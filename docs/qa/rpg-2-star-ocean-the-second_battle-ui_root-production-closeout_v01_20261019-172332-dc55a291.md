# Battle UI native-skin production closeout

Task content.ui-visual.battle; producer Claude Max, independent fixes/checks/integration Codex. Base d9a86d591782b8e71722bc5aaeffbb6276c882c1. Production candidate only; creator approval false. Defaults unchanged; --battle-ui-skin-pilot is required.

## Produced and integrated

Eleven separate native nine-patch skins (PNG, one-frame five-role PXO, ORA), deterministic Python author and exact manifest. Warm bronze hairlines, navy panels, teal controls, semantic health/energy/enemy bars; visible normal/hover/pressed/disabled/focus states. Root-v02 transactional helper wires existing HUD, all 20 buttons (five party capacity), pause/skills and win/lose panels without simulation changes. Original producer helper is retained only in its separate worktree; integrated root-v02 includes disclosed corrections.

## Independent evidence

- 355/355 native checks: hashes, dimensions, layer roles/cels/composites, exact34-file rebuild. Native app/GUI save/reopen not tested.
- 407/407 malformed-package checks on final helper, checked runner clean. Original malformed hash Dictionary/Array/number triggered SCRIPT_ERROR even with exit0 and407inner passes; firstfailed logs and overallFAIL verdict preserved. Explicit String hash validation fixes it; unchanged negative test passes.
- 1250/1250 actual640x360 Godot checks on final helper: baseline/off/on600step combat parity, default-off0pixel difference, EN/ZH normal/pause/victory/defeat all visible rectangles/minimums/text/fonts/sizes/disabled/focus/connections exact; real mouse party-selection, skill activation16energy and pause/resume. Four plates ignore mouse/focus; idempotence and revert verified.
- Original apply guard falsely rejected transient hidden controls initially smaller than their existing minimum. Root compares effective settled size.max(minimum); independent actualvisible comparisons above retain strict exact equality. This is a disclosed guard correction, not evidence that every transient pre-layout hidden rectangle is unchanged.
- Final runtime log v04 passes cleanly with fresh isolated APPDATA. Rerun v02 omitted required script args (harness invocation error); v03 encountered shader initialization diagnostics in reused profile and was rejected. Both retained; no tests/thresholds weakened. v01 initial successful actual run retained.

## Visual inspection

Codex viewed actual English normal/pause and Chinese victory/English defeat captures. Crisp restrained bronze borders and semantic bars are coherent and readable. Existing pause quick-skill/EdgeBreak text overlap remains baseline geometry; this skin does not fix that layout defect. No artistic acceptance, fullUI review, fullsprite approval or playtest credit. No character/environment default change.

Source/test raw hashes are in the root integration manifest; staged bytes are checked before publication. Generated import/cache noise is excluded. Full UI review depends on remaining navigation, management and portrait content.
