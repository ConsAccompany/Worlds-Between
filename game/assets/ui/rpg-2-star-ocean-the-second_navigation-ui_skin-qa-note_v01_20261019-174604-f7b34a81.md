# Navigation/exploration UI skin helper v01 — QA note

Task: `content.ui-visual.navigation`. Status: **UNAPPROVED technical candidate**, not wired, no art approval.
Source revision: `d9a86d591782b8e71722bc5aaeffbb6276c882c1` (branch `codex/dual02-management`); the three scene scripts
are unchanged against HEAD. Hash normalization for text: sha256-text-lf-v1 (CRLF → LF, UTF-8).

| File | sha256-text-lf-v1 |
| --- | --- |
| `game/scripts/rpg-2-star-ocean-the-second_navigation-ui_skin-helper_v01_20261019-174604-f7b34a81.gd` | `d15e83b859df369896a72e5c3e84625a51b32a46d722423d100a8252eb7e6b5f` |
| `game/assets/ui/rpg-2-star-ocean-the-second_navigation-ui_selfcheck_v01_20261019-174604-f7b34a81.py` | `8154d8c4f286e26c233c095cac0b129d28727039df3136a6574a1e9956025aea` |
| `game/scripts/scifi_exploration_area.gd` (read-only) | `6fe049f1778016ebfda1af330becf1012b4f6ed2b7e8a87353fed1544bee0b60` |
| `game/scripts/survey_annex.gd` (read-only) | `521f5335e01723267c1a5bcc4d1720f7394b5ab1bb72742e7bdac309d0ad8078` |
| `game/scripts/scifi_world_map.gd` (read-only) | `87489682dd3df4230b7b65e544301dd9ec934568cd831c0911c9053f86884f7b` |
| battle-skin-v01 manifest (read-only, pinned in the helper) | `545c0e25368a15061ee9b1cb8fca3f4c796907d43eecbcaa0c6e35bed221a504` |

No images were created or altered; the helper reuses the 11 battle-skin-v01 PNGs read-only.

## API

`var skin = load(helper_path).new("res://assets/ui/battle-skin-v01")` (loads nothing) →
`skin.apply(scene) -> bool` after the scene's `_ready()` built its UI; `skin.revert()` restores it exactly.
`screen_kind` is `exploration`, `annex` or `map`; `last_error` explains a `false`. A second `apply` on the same
scene returns true without changes; on another scene it returns false. A fresh helper on an already-skinned scene
refuses (chrome ColorRect already has a child / buttons already have style overrides).

Kind detection (required refs): map = `route_card` + `commerce_overlay` + `credits_overlay`; annex = `overlay_body`
(RichTextLabel) + `link_buttons` + `overlay` (ColorRect); exploration = `dialogue_overlay` + `invite_button` +
`later_button`.

## Node map

Every plate is the only child of an existing chrome ColorRect, exactly its size (draws over the flat fill, under
every later sibling label/button). NinePatchRect, nearest, `MOUSE_FILTER_IGNORE`, `FOCUS_NONE`, `draw_center`.
Overlay dim ColorRects are not touched (colour, visibility, input guard unchanged). The CanvasLayer child order is
unchanged (the map's `_sync_commerce_focus` loop sees the same nodes).

| Scene | Plate (skin) | Parent ColorRect | Skinned stock Buttons |
| --- | --- | --- | --- |
| exploration | hud-band | header 0,0 640×62 | back, save |
| exploration | hud-band | footer 0,318 640×42 | — |
| exploration | panel | dialogue panel 87,93 466×185 (in `dialogue_overlay`) | invite, later |
| annex | hud-band | header 0,0 640×62 | save, back |
| annex | hud-band | footer 0,318 640×42 | — |
| annex | panel | investigation panel 53,41 534×278 (in `overlay`) | option×3, link×6, notes, previous, next, close |
| map | hud-band | header 0,0 640×44 (above the map frame) | save, growth, back |
| map | hud-band | strip 0,313 640×47 (below the map frame) | field, commerce |
| map | panel | field log 48,39 544×285 | talk, field_close |
| map | panel | company 48,39 544×285 | member×(MEMBER_DEFS−1 = 3), recall, rest, close |
| map | panel | credits 72,62 496×236 | credits_close |

Buttons get StyleBoxTexture overrides for normal/hover/pressed/hover_pressed/disabled/focus that copy the old
stylebox content margins (minimum size checked equal before mutation) and the manifest's six font colours. Text,
fonts, font sizes, positions, sizes, disabled, visibility, focus and signals are never written.

## Boundary — map chrome deliberately not skinned

The world map's own v03r2 native chrome is preserved untouched: the map frame and all of its children (terrain,
routes, labels, markers, leaders, legend backing, calendar, zoom/view buttons, relief credit plate), and the travel
**route card**. Concrete reasons, not omissions:
- the route card is a PanelContainer whose `_draw_route_card` dressing (header band, brass tab, bevel, brackets,
  shadow) draws on the card under its children; a NinePatchRect child would be laid out by the container over that
  dressing, and replacing its panel StyleBoxFlat would discard the card's opaque teal/brass treatment;
- Depart/Cancel/zoom/view buttons already carry science-UI style overrides, and the trip option buttons are freed
  and rebuilt on every `_refresh_route_card`, so a one-shot override would not survive refresh. The helper refuses
  any target Button that already has a stylebox override instead of restyling it.
So map coverage is the header/strip bars, their stock buttons, and the field log/company/credits panels and buttons.
The geography and the credit plate are never covered (header plate ≤ y 44, strip plate ≥ y 313; the credits panel
plate sits under the credits text).

## Pre-mutation validation

Manifest text hash pin, JSON via `JSON.new().parse`, typed fields with finite whole-number checks
(`_is_whole`/`_number_equals`), 64-hex sha256 strings, plain file names, all 11 PNGs present with raw sha256-bytes,
texture sizes, slices leaving a stretch centre, `#rrggbb` font colours; then every ref's type and parent layer, every
chrome ColorRect's exact rect (unique, childless), overlays at 0,0 640×360, plate in the 640×360 view and larger than
its slices, each intersecting button's effective rect (size max combined minimum) inside the plate's inner rect, and
each label/RichTextLabel origin outside the border (1 px top allowance, see below); then every stylebox. Any failure
returns false with nothing changed. After mutation, a snapshot of every touched control (position, effective size,
combined minimum, visible) must equal the pre-mutation one or everything is reverted.

## Self-check (bounded, no Godot)

`PYTHONUTF8=1 <bundled python> -I game/assets/ui/rpg-2-star-ocean-the-second_navigation-ui_selfcheck_v01_20261019-174604-f7b34a81.py`
→ `NAVIGATION_UI_SELFCHECK checks 211 fails 0 PASS` (exit 0). It covers the package, the helper constants and safety
idioms, 75 scene geometry literals (21 exploration, 22 annex, 32 map) (asserted present in the read-only sources), and the clearance replay for every
plate including the annex Yonkers English widened Back (503,12 125×38, Save at 398) and 3 company member buttons.
Minimum inner gaps: explore 8/11 px, annex 8 px, map header 2 px, **map strip 0 px** (field/company buttons' top edge
at y 317 sits exactly on the band's inner edge — enclosed, not crowding, but tight), map panels 8–17 px.

## Limitations / for root

- Not executed in Godot (per scope): parse, apply/revert, EN/ZH actual captures, button/overlay interaction, default
  parity and refresh/language survival are root's checks. No art approval claimed.
- `LABEL_TOP_ALLOWANCE = 1 px`: the map title label origin is at y 3, one row inside the header band's 4 px top
  border; its glyphs start below the label's line-top padding. Root should confirm visually in the map capture.
- The hud-band centre replaces the bars' flat `#0d1723` fill visually; contrast of the existing header/footer text
  on it is an art judgment for review.
- Hidden overlays are validated with the effective (max of size and minimum) rect; root checks visible states after
  render (dialogue: recruit/assist/trace modes; annex: clue/question/link/message/notes; map: field/company/credits).
- Suggested wiring for `--navigation-ui-skin-pilot`: construct once per scene after `_ready()` (e.g. call_deferred),
  default off; nothing in the helper reads command-line flags.
