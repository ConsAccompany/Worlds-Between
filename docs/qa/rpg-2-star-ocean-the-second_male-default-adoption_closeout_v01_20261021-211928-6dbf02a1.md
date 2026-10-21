# Authorized male ordinary defaults

Task: `male-default-adoption`; owner Codex. Base: `e544db07621bbf9e493fea6fcb927e5a7559e291`.

The creator explicitly answered **设为男主默认显示（推荐）** after seeing the exploration/battle captures and a prompt limiting authorization to ordinary default use, not artistic or motion acceptance. This closes the separate default-use authorization required by AGENTS.md.

## Implemented and checked

- Enabled the single shared male default switch. Ordinary exploration uses the complete four-direction idle/walk/stop package; ordinary battles use all eight source actions. No presentation flags or process overrides are needed.
- Reused the same normal-input flow with a setup mode that leaves all exploration/combat overrides unset. It starts a fresh test run with the male appearance; the normal scene and battle select the assets themselves.
- EN victory139, EN defeat118, ZH victory139 and ZH defeat118 checks pass (514 total). Natural encounter, result/return, post-battle reload, natural defeat and pre-battle retry all use the ordinary default. No HP/damage/AI/cooldown/reward edits.
- Profile fixture16/16 confirms female defaults, exact override rollback and explicit exploration/combat disable still work. The default does not alter other actor assignments or the game rules.
- No artwork was edited. Source art/motion approval and both human playthroughs remain open. Existing source manifests keep their original creation-status metadata; this runtime policy and the Bible record current default use.

[Canonical default-path proof](../../outputs/mpath24/20261021-211736-349f31c2/rpg-2-star-ocean-the-second_male-playable-path_root-proof_test-only-v01_20261021-211736-349f31c2.json) binds the tested raw source bytes and commands. [Scope check](../../outputs/mpath24/rpg-2-star-ocean-the-second_male-default-adoption_profile-scope_test-only-v01_20261021-211925-c5238fd0.log) retains the16 checks. All four report/log pairs and selected default-gameplay captures are committed; repeated direction screenshots remain local. Tests use isolated temporary save profiles and the existing checked runner. Two ObjectDB exit warnings remain disclosed; no passing run contained a parser/runtime error.

Reproduce:

```powershell
python -X utf8 -I tools/rpg-2-star-ocean-the-second_male-playable-path_root-runner_test-only-v01_20261021-171230-68e0e142.py --normal-default
```

Source gait/side-stop slip and male anticipation versus immediate mechanical contact remain deferred, as disclosed in the preceding playable-path closeout. No world-foot-lock or fluidity acceptance is asserted. The earlier opt-in proof is a historical snapshot at77e870d; this default proof supersedes its default-use status.

## Scoring

The two existing production tasks now meet their unchanged criteria: `content.char.protagonist-male.runtime-integration` (2points) and `content.combat.protagonist-male.combat-integration` (2points). Production **55.6% →55.7% (+0.1pp)**, content489→493/1881; coding111/111 remains100%. Inspection **18.1% →18.1%**, creator approval **7.8% →7.8%**. No new task denominator, revision credit, artistic acceptance or human playtest is invented.
