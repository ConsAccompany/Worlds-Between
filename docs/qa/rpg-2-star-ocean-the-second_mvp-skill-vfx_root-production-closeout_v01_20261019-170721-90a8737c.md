# MVP skill effects: native production and actual skill hooks

Task `content.vfx.mvp-skills`: DeepSeek produced the bounded eight-set package; Codex independently built the strict loader, added opt-in presentation hooks and inspected the actual game. Base integration6d41f00; no new skill mechanic, resource cost, cooldown, range, AI, save/reward or character identity design was introduced.

## Package and integration

Four personal cues map to the existing hero, Liang Xu, Zhao Ling and Ji Cheng actions. Four job-family cues map to sword, firearms, tactics and relics, covering BOTH implemented skill stages of each family. Merchant's placeholder battle actions remain rejected with no effect. No claims about the other full-game/skeletal nodes.

Eight64×64sets, pivot32,32, eight RGBA cels each, three editable roles per set,64PNGs plus8PXO timelines and8ORA middle-cel snapshots. Authored duration .45/.55/.45/.65s for the four personal effects and .30/.25/.55/.65s for sword/firearms/tactics/relics. Native fps12 with correct frame-duration multipliers; alpha≤166. Distinct focus brackets, coordination chevrons, ranging arc, record glyph ring, slash, tracer impact, formation pulse and old-gold seal. Existing runtime skill names remain unchanged.

`--mvp-skill-vfx-pilot` or test override explicitly enables the package, off by default. Personal effects originate at their caster; damaging sword/firearms effects at the existing target; support/interference jobs at their caster. All hooks occur only after existing action guards succeed. Native missing/invalid kinds preserve prior no-skill-cue presentation. Pauses freeze events; existing post-battle updates expire them. Uniform native durations are checked individually because the runtime samples equal cels: a shifted pair with the same total must be rejected.

## Independent verification

-389/389native/raw-hash/pixel/timing/rebuild checks, including all64PXOcel composites,8ORA snapshots and all81package files rebuilt byte-for-byte. Source/helper raw bytes explicitly hash-bound.
-191/191loader boundary checks: invalid numeric types/fractions, missing/partial/unsafe paths, wrong size, malformed JSON and unequal per-cel native timing with equal total all safely fall back. No arbitrary-corrupt-PNG decoder recovery claim.
-1375/1375actual Godot checks in final stage-expanded run.600step baseline/off/on combat-state parity, default screenshot0pixel difference, all four personal and all eight first/second-stage job actions retain exact state outcomes, real rejected actions emit nothing, all eight kinds load their native cels, all16EN/ZH captures stay localized, pause and exact expiry pass. Final checked-runner log is clean with expected marker. The earlier two1359-check runs had two ObjectDB cleanup warnings; logs retained. The final test adds concrete second-stage coverage and releases held references; no gameplay or assertion threshold was weakened.
-Root viewed all eight actual skill images and common contact/guard/dodge/heal samples, alongside the separately checked encounter result feedback. Cues remain quiet and local, with no interface-text coverage; some caster/support accents blend with dark clothing. This is a recorded static composition/technical inspection, not creator artistic acceptance or a continuous normal-speed animation-quality certificate. No claim that new character motion was produced or approved.

## Limits

Native application clean export and GUI Save As/reopen were not verified for these new VFX packages; native reconstruction is separate. Art remains unapproved. Default adoption, full runtime sprites0/52, accepted scene visuals3/12, human playtests0/2 and formal acceptancefalse are unchanged. The common, skill and encounter packages are separately opt-in technical candidates. Production credit records the authored/wired work; approval remains its own queue.

Reproduce with the native checker and bounded Godot runtime/loader scripts sharing this timestamp/id. Final gameplay captures/report: `outputs/skill-vfx-v01/actual-v03/`. The frozen pre-integration arena is retained alongside the reports; source SHA is in the actual report.
