# Male / Liang exploration technical gate: NOT PASSED

Base `66ae88e706d57d029a247dcba64a963066673683`; all2378 protected runtime/data/scene files unchanged. No default, mechanics or art changes. Production59.1→59.1(+0.0pp),inspection20.1→20.1(+0.0pp),creator approval7.8→7.8(+0.0pp). Both existing QA tasks remain blocked; no new scoring buckets.

[Source-bound root proof](../../outputs/xcheck36/root/rpg-2-star-ocean-the-second_male-liang_runtime-contact_verdict-not-passed_v01_20261021-234911-bd5a14a9.json) retains all commands, raw/display diagnostics, source-only support, rejected adapter attempts and the compact reproducible game defect.

## Actual finding

The ordinary male host moves140logical px/s. At40ms, actual body translation is5.5999756px while the source planted heel compensates2px. The net foot moves3.5999756px during a planted interval, confirmed against exact source PNG heel alpha and the real ordinary host/driver texture phase. This reproducer passing means the defect was reproduced; **it is not a passing slip gate**. Source documents already disclosed this50px/s-vs140px/s mismatch. Front/back in-place loops likewise do not establish world foot lock.

Liang is an ordinary stationary field NPC, with no follower. The same moving source cycle has the same hypothetical mismatch; do not claim ordinary Liang walks/slides behind the protagonist. Four-direction moving-source and stop/stance checks remain fixture scope.

## Useful evidence and rejected checks

DeepSeek independently checked the source banks/PNG hashes/bridge endpoints and rejected one-frame/stop-manifest corruption; root reran it successfully. It explicitly does not establish runtime foot lock. Its initial59/4 oracle failures and corrected results remain archived.

Claude's bounded600-second task ended at the deadline, not Max depletion. The large unverified runtime proposal initially had a parser error; root patched only the explicit integer type. A subsequent run produced128 image-byte,92 frame and16 stop assertion failures. These adapter expectations are not accepted runtime defects and no pass is claimed. Original, patched and final producer sources plus all attempts are archived, rather than installing another redundant validation framework. The small root contact reproducer is the maintained defect reproduction. Its2 ObjectDB shutdown leak warnings are retained.

## Next action

Do not repeat the same audit or tune cosmetic parameters now. Creator instruction defers character refinement until after MVP; keep these QA tasks blocked with this precise finding and continue missing native content. Existing authorized MVP actor defaults stay in use. A later coherent gait/source revision must re-run the unchanged foot-contact requirement; coordinate stability alone cannot close it.
