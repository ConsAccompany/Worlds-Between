# Half-scale combat playback maintenance: independent closeout

Owner DeepSeek; independent review/testing/integration Codex. Existing `code.runtime.combat-sprite-pipeline` maintenance, no new completion points. Producer base9b4c2f4; coordinator base73b8922. Scope: existing helper plus synthetic fixtures/tests only, no default art adoption or battle mechanics changes.

Codex inspected the77insertions/19deletions diff. Scale accepts exact1or0.5 only; half dimensions and base/perframe pivots must be even. Mirroring and texture-region geometry use source pixels plus integer logical draw dimensions; scale1 destination/source formulas are unchanged. Requiredall7actions and optional-skill fallback, validation/cache/defaultoff flags remain.

Ordinary-context root import and both strict checked runs pass:273targeted checks,162unchanged frozen legacy checks. Producer-context certificateERRORfailures remain preserved and are not treated as passes. Root keeps the legitimate1e999warning and legacy2ObjectDBwarnings disclosed. No ERROR/SCRIPT_ERROR filter or tolerance changed.

Root additionally exercised actual normal-arena draw_fighter at1280backing with a diagnostic half-scale set in both facings. Every visible opaque source texel maps byte-exact to its corresponding physical pixel (136x144source ->68x72logical). Synthetic fixture hero is explicitly placed atx70 to isolate the texel test; other defaultparty positions unchanged. This is not characterart or ordinaryplayer-input evidence.

Initial root render failures are preserved:1relative scriptpath resolved inside res:// incorrectly;2outside-project autoload symbol reference plus startup shader-cache errors;3source-texel equality incorrectly assumed no occlusion at defaultparty spacing. Corrected absolute script/projectpaths, root singletonlookup, fresh profile and an explicitly nonoverlapping synthetic position resolved those fixture setup errors. No image comparison threshold was weakened. Final render marker HALF_NATIVE_TEXEL_RENDER_PASS passes with two real1280captures; its2ObjectDBWARNING remains. No production code change was required for these fixture corrections.

Root proofs/captures/logs: `outputs/half-scale-root-20261020-195118-1b6c6fdd/`. Native fixture is not inserted into any runtime index. Actual heroine package/rational authored tick timing/defaultadoption are later tasks.
