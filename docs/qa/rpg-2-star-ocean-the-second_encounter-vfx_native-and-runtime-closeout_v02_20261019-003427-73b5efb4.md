# Encounter feedback: native package and optional runtime wiring

Producer DeepSeek V4.1 Flash, coordinator/independent inspector Codex. Task `content.vfx.encounter`. Completed native timing correction, +37-line optional arena wiring and bounded malformed-manifest/missing-frame loader guard. No new art/style iteration, creator approval or game-default adoption.

## Outputs

- `game/assets/vfx/encounter-v02/`:4editable PXOs,4layered ORAs,32PNG frames and hash manifest. Source author is in its parent vfx/; helper is in assets/inputs/, preserving runnable author/helper and manifest source-relative layout.
- New timing-v03 feedback module in game/scripts; arena flag `--encounter-feedback-pilot`, static override -1/0/1, off by default.
- Encounter after ready; victory/defeat once after the existing finish guard; recovery after existing winning recovery for each then-living member. No gameplay HP/energy/reward/save/RNG changes.
- Independent root test sources in tools/; source-bound reports/captures in outputs/encounter-vfx-v02/.

## Independent checks

1. **84/84** root native timing/hash/pixel checks: all32RGBA frames unchanged from the benchmark; each timeline totals0.50/0.80/0.65/0.60seconds, respectively. The original helper stores12fps duration multipliers, now correctly duration/8*12. The producer additionally reported135Python checks.
2. Final guarded module: **184/184** Godot API/timing/FIFO/draw-readonly checks, no runtime diagnostics.
3. Final guarded module: **20/20** actual Godot missing-manifest/malformedJSON/wrong-events/short-frame-array/missing8paths/wrong-name-type/valid32texture checks, no ERROR/SCRIPT_ERROR. Scope does not claim a new corrupted-PNG decoder.
4. Final arena: **1220/1220**, including all600baseline simulation steps against pilot off and on, exact default render pixel parity, ready/finish/recovery triggers, pause, duplicate-finish guard, expiry after battle finish and bilingual actual captures. These are check counts, not production points.
5. The first arena harness failed because the coordinator called nonexistent AppState.set_language. The test was corrected to the existing language property/signal; thresholds and assertions were unchanged. Final runs pass.

## Visual inspection and limitations

Codex viewed actual640x360 encounter, final victory/recovery and defeat captures. Amber encounter arcs appear around the controlled heroine. The first result capture hid effects under the panel; DeepSeek added a result-only foreground surface and compact left-margin placement. Final1220checks include layer absence when off, active surface when finished, expiry hiding, and actual alpha-frame bounds clear of panel text/top-bottomHUD. Final captures show separate teal recovery rings and small gold/ember result cues beside the panel. Text/buttons remain clear. The effects are produced and connected; polish/creator acceptance remain separate and the pilot stays off by default. Other character sprites/environment in these captures remain prototypes. No fluid-motion approval is inferred from static captures.

Primary native structures and timing metadata are checked. The earlier benchmark's Pixelorama exact layer exports emitted inherited shader diagnostics; this task does not claim clean-editor or GUI SaveAs verification, or new native-app playback verification.

Source binding JSON records raw tested hashes and explicit LF-normalized code hashes. Native author/helper/assets retain raw bytes. The modified arena uses normal repository LF text normalization in Git; staged normalized bytes must equal the recorded LF hash. No account balances, reset logs or model transcripts are included.

## Completion scope

The frozen production criterion is four effect sets committed and wired. That scope is complete as an optional review pilot. Review/placement refinement, final default selection and creator acceptance remain separate. No repeated revision bucket or automatic approval points.

Native author/helper were rebuilt from their final integrated relative layout: all41files byte-identical. The final foreground patch adds55/removes3lines beyond the initial37-line wiring; only presentation changes. Producer mocks are not counted as runtime evidence; root used actual game captures.
