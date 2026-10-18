# Battle VFX capability: completed technical implementation

Task `code.runtime.vfx-system`, based on combat loader commit `fe66540a1cdf5a131ab67c1fec013a55c0a9e1dd`. Completed 2026-10-18T17:26:32 America/New_York by Codex during the authorized Max quota gap. No Claude inference, cloud credits or paid calls were used.

## Contract and integration

A reusable transient event layer supports attack, dodge, guard, hit and heal. Normal battle hooks emit contact attack only after a successful in-range damage action; dodge only after success; guard only after actual energy-funded blocked contact; and hit after ordinary damage (including insufficient-energy guard). Missed, cooldown-rejected and evaded contacts do not emit inappropriate effects. Presentation never changes stats, timers, input, collision, AI or saves.

The source-drawn presentation is OFF by default and explicitly enabled with `--battle-vfx-pilot` or `battle_vfx_override = 1`. These are technical provisional accents, not approved VFX art. They use thin local lines/marks, no screen flash, screen shake, opaque rectangles or full-body overlay. Actual per-capture effect differences are only 14-28 pixels within the body/feet band. No smoothness/art-quality approval is claimed.

Events use elapsed time and finite coordinates/deltas, with 0.20-0.55 second lifetimes, a 24-event bounded queue and deterministic oldest-event removal. Normal pause freezes them. Battle-end updates clean up remaining effects. No per-frame event emission is used.

**Healing limitation:** the current battle personal/job skills and GrowthRules have no healing combat mechanic. `show_heal_vfx(index)` is an explicit presentation-only API, tested for valid and invalid targets and unchanged HP/energy. No healing gameplay was invented; no success hook can be connected until a healing action exists. This limitation is included in the report and both heal captures.

Optional dynamic audio hooks were added in this arena at root request, leaving the disjoint audio service untouched. `_emit_battle_cue` safely checks `AppState.get("audio_cues")` and `play_cue` dynamically. Attack/dodge/guard/hit/heal calls occur independently of the VFX flag; successful skill actions and victory/defeat also call the service. This producer worktree has no audio service, so these calls are verified safe no-ops here. Root must test actual playback and rejection with the service after integration.

## Evidence

- Final actual windowed VFX check: **53/53 passed**, **10 bilingual native 640x360 captures** (five event kinds, EN and ZH).
- Positive normal-action hooks plus rejected cooldown/miss/evaded/insufficient-energy cases; bounded queue, negative/invalid inputs, 30/60 fps elapsed-time parity, pause freeze and cleanup/no-spam checks pass.
- VFX on/off: **three 600-step encounters** preserve exact simulation trace and save snapshots while real effects are emitted only in the enabled run.
- Fresh combined combat loader run: **261/261 passed**, **12 bilingual native 640x360 captures**, current arena hash bound in its new report. This preserves malformed-manifest/identity/facing/action/timing checks, three 600-step on/off/base traces, five exact default render identities and missing-index atomic fallback.
- Final logs contain no SCRIPT ERROR, ERROR, FAIL or leaked-instance warnings. Initial test harness preload ordering was corrected to runtime-load the arena after autoload initialization; the final runs are clean.
- Sources use `sha256-text-lf-v1`; images use raw SHA256. Run `tools/rpg-2-star-ocean-the-second_battle-vfx_combined-evidence-check_v01_20261018-172632-baacbefc.py` to verify this exact combined package. The earlier historical combat report remains tied to its earlier arena and is not claimed valid for this changed source.

Codex actual visual inspection: attack EN shows a restrained amber contact spark near the enemy, guard ZH a small teal arc on the defended side, heal EN two small green accents. Their pixels are localized and do not cover the HUD or obscure a character. These stills establish rendering capability, not animation fluidity or final art acceptance.

Evidence folder: `outputs/vfx-capability_20261018-172526-e9e7344f`. VFX report `rpg-2-star-ocean-the-second_battle-vfx_capability-report_v01_20261018-172526-e9e7344f.json`; combined loader report `rpg-2-star-ocean-the-second_combat-set-pilot_capture-manifest_20261018-172542-b9cf9e3e.json`.

## Reproduction

Godot 4.7.2, import once, redirect APPDATA and LOCALAPPDATA to a fresh isolated temporary profile. Run `res://tests/rpg-2-star-ocean-the-second_battle-vfx_runtime-check-capture_v01_20261018-172403-e6060319.gd` windowed at 640x360 without the VFX CLI flag (the test controls overrides); `--headless` runs the nonvisual checks. Then run the existing combat loader check with `--baseline-dir=<repo>/outputs/combat-set-pilot-v01_21e56480`. Use a newly named capture directory for new executions. No progress ledger, Site, approval counter or remote changes belong to this commit.
