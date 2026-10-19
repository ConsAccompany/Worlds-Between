# Battle HUD skin v01 — producer QA note (UNAPPROVED technical candidate)

Scope `content.ui-visual.battle`. Package `20261019-171056-ca4652ec`. Not creator-approved, not wired, no Godot run by the producer.

## Files
- Author: `game/assets/ui/rpg-2-star-ocean-the-second_battle-ui_native-skin-author_skin-v01_20261019-171056-ca4652ec.py` (sha256 `418a3543…cfdced`), uses the copied `assets/inputs` native-format helper.
- Package: `game/assets/ui/battle-skin-v01/`. 11 separate PNGs, 11 one-frame PXOs, 11 role-layer ORAs and 1 manifest (`…asset-manifest…json`, sha256 `545c0e25…a504`). There is no atlas or contact sheet.
- Helper: `game/scripts/rpg-2-star-ocean-the-second_battle-ui_skin-pilot-helper_skin-v01_20261019-171056-ca4652ec.gd` (sha256 `a02037ca…46a2`).

## Build / check (deterministic)
```
cd game/assets/ui
PYTHONUTF8=1 <bundled python> -I rpg-2-star-ocean-the-second_battle-ui_native-skin-author_skin-v01_20261019-171056-ca4652ec.py --out-dir battle-skin-v01
PYTHONUTF8=1 <bundled python> -I rpg-2-star-ocean-the-second_battle-ui_native-skin-author_skin-v01_20261019-171056-ca4652ec.py --out-dir battle-skin-v01 --check
```
Result: `BUILD files 34 fails 0 PASS` and `CHECK files 34 fails 0 PASS`. The `--check` step rebuilt the package byte-identically and found no extra files. Pillow `getdata` deprecation warnings are harmless.

The self-check covers: RGBA mode and size, binary alpha only, a stretch centre left by the slices, uniform rows and columns across each stretched span (so scaling never smears a detail), ORA merged image equal to the PNG, PXO header size and 1 frame, PXO layer names equal to the manifest roles, and PXO layers compositing exactly to the PNG.

## Skin → node map
| skin | size | slices L/T/R/B | applied to |
|---|---|---|---|
| hud-band | 24×24 | 4/4/4/4 | NinePatchRect plate, first child of header ColorRect (0,0 640×90) and footer ColorRect (0,302 640×58) |
| panel | 24×24 | 4/4/4/4 | plate on pause panel ColorRect (55,43 530×265) and result panel ColorRect (112,99 416×171) |
| button-normal / hover / pressed / disabled | 16×16 | 4 | `normal`/`hover`/`pressed`+`hover_pressed`/`disabled` on all buttons |
| button-focus | 16×16 | 4 | `focus` overlay (parchment ring + bronze corner brackets, clear field) |
| bar-trough | 16×16 | 4 | `background` of hp/energy/enemy bars |
| bar-fill-health / energy / enemy | 16×16 | 2/4/2/4 | `fill` of hp_bar / energy_bar / enemy_bar |

Buttons covered: quick_skill, auto, party ×4 (PARTY_CAPACITY), pause_skill, pause_job_skill ×2, pause_resume, pause_policy, pause_target ×4, pause_order ×3 (focus/defend/skill), result. Button font colours are overridden from manifest `fontColors` (parchment text; disabled `#7f8c90`). Text, font, font size, labels, signals, veils, simulation and settings are not touched.

## Helper contract
- `Helper.new(dir)` loads nothing. `apply(arena) -> bool` first validates the manifest, all 11 skins (size, slices, PNG sha256 when the raw file exists, loaded texture size), the font colours, every arena ref and the four ColorRects by exact rect. It also builds every stylebox and checks that its minimum size equals the old one. Only then does it mutate anything.
- StyleBoxTexture content margins copy the old stylebox's effective `get_margin()` per state. The textures are wrapped in `CanvasTexture` with `TEXTURE_FILTER_NEAREST`, so the controls' own `texture_filter` (and so glyph rendering) is untouched. Plates use NEAREST, MOUSE_FILTER_IGNORE and FOCUS_NONE.
- After mutating, it compares every touched control's position, size and combined minimum size. On any difference it calls `revert()` and returns false. `revert()` is public. A second `apply` on the same instance returns true without changes, and existing plates make a new instance return false.

## Known limitations / for root to verify
- Bars: the fill keeps the 2 px trough rim clear, so a value under ~2 px (for example 1/64 HP on the 119 px enemy bar ≈ 1.9 px) shows only the trough. At 2 px or more the shadow edge is visible.
- A nine-patch centre cannot carry internal dividers. The band and panel have no inner rules other than the frame hairline and corner joints.
- The helper adds 4 child Controls to the ColorRects. Tests that count those children, or that use `get_child(0)` on the panels, will see the plate.
- `CanvasTexture` filter honouring for StyleBoxTexture must be confirmed in actual captures (renderer-dependent). The fallback is to set the controls' `texture_filter`, which root should check for glyph parity.
- Not done by the producer: Godot parse/run, `--battle-ui-skin-pilot` wiring, en/zh normal/pause/victory/defeat captures, default-parity proof, and any visual review.
