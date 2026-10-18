# Global map v03r1: zoomed label clamp and obsolete background-visual expectation (UNAPPROVED correction)

Date: 2026-10-17. Status: **unapproved map-art correction**. This is the one bounded correction the [v03r1 zoom-legibility dispatch](../coordination/rpg-2-star-ocean-the-second_global-map-v03r1-zoom-legibility-dispatch_unapproved-v01_20261017-184800-fc76e93d.md) asks for after the [v03 QA note](rpg-2-star-ocean-the-second_global-map_native-art-pass_qa-note_unapproved-v03_20261017-175314-e8b8f8af.md) (synced `ec8b8f5`, Game Bible queue #10). The creator has not accepted map art. M2 stays 10/12 and the meter 40.8%. Nothing here advances a gate or accepts art.

Scope:
- Touched: `game/scripts/scifi_world_map.gd` (one fallback in label placement), the map-specific test `game/tests/…_scifi-world-map_background-visual-check_m8-v01_…-239f6b80.gd`, a new test-only tool, captures/logs in `outputs/`, and this note.
- Not touched: geography, relief, route endpoints, palette, travel minutes or dates, airport-name omission, click handling, save, `world_map_data.gd`, `world_map_text.gd`, Game Bible, progress, character, Chicago, City Hall and Yonkers files, the Git index. Nothing staged, committed or pushed.
- The dispatch says to read `AGENTS.md`. There is no `AGENTS.md` in this repo or its parent folders, so this pass followed the dispatch, the v03 note and the existing code conventions.
- This ran in Claude Code (Opus 5.5) signed in through claude.ai Max (first-party). `ANTHROPIC_API_KEY` was absent. No API billing, credits or paid fallback was used. Only Godot processes started by this session's own commands ran; none were stopped by name.

## Problem 1: the zoomed-in Washington card's labels (runtime fix)

**Cause.** `_place_marker_button` tries the place's own side and then eight slots. If none is clear of the fixed controls, the card, other dots and placed labels, v03 took **the first slot inside the frame, whatever it covered**. At 1.5× zoom with the Washington car card open (the route-card readability check's state, `zoom_view((320, 134), 1.5)`):
- Washington's marker (147.5, 256.4 map-local) is boxed in. The Globe and region buttons are above it, the scale bar is to the right, and the frame bottom is 12 px below. Every slot is blocked, so the fallback took "above" and the plate covered the region button completely and part of the Globe button. In the real capture, 2302 region-button pixels and 96 (zh) / 360 (en) Globe pixels were repainted.
- New York's marker (447.1, 19.0) is under the card, so every slot touched the card. The fallback put the plate across the card's left edge, and the card cut it to "New York Ci".

**Fix (labels only).** There is one new fallback, `_clamped_label_rect`. It runs only when no slot is clear and the marker is inside the frame. It places the plate at the nearest position within `CLAMP_REACH` = 64 px of the marker that meets all of these:
- it is clear of everything the slots must clear, plus its own 18 px dot box;
- its leader (marker → nearest plate point) does not cross a control, another dot or another plate. A rect the marker itself is under (the card) does not reject the leader.

Candidate positions are the slot positions plus positions flush with each blocked rect and with the frame. Ties go upper-left, so the result is deterministic. The existing leader line joins the plate to its marker. If nothing qualifies, v03's old fallback still applies.

Not changed: marker positions, the slot order, what counts as blocked, the button structure (dot + plate), click handling, card layout and colours.

**Result at 1.5×, zh and en:**
- **Washington:** the plate sits right of the region button, above the scale bar, at map-local (195, 220). The leader is 48.4 px. The plate is clear of every control and the card, and the button pixels are identical with the place labels hidden.
- **New York:** the plate sits flush with the card's left edge at the top of the frame (3 px gap), whole. The leader is 26.1 px, and only its stub shows outside the card. New York stays named and clickable while its dot is under the card.
- **Yonkers:** the marker is above the frame at this zoom, so its plate stays off-frame and clipped, as in v03 at any pan or zoom that leaves a marker outside.

**No other state changed.** The full v03 capture tool, run on a temp copy of `game/` with the v03r1 script, prints `NATIVE_MAP_ART_OK 1873 checks, 12 captures`. **All 12 v03 captures are byte-identical** to v03's pinned manifest: globe, Northeast browse, Washington card at default zoom, Chicago card, reverse card and credits, in zh and en. In those states every label finds a normal slot, so the fallback never runs.

## Problem 2: `background-visual-check` (obsolete expectation, test updated)

**Geometry is intentionally correct; the test was stale.**
- The M8 test (b1aff00) pinned a fixed three-point background: buttons at `marker + (-68, 29)`, 136×39, whose press entered the area scene.
- Since `09d3689` the scene is the global Earth map. Its [runtime QA note](rpg-2-star-ocean-the-second_global-earth-map_runtime-implementation_qa-note_m2-v01_20261015-024300-15ce9195.md) already records this test's geometry as superseded by design.
- Destination buttons are now place label plates laid out per view, and a press opens the route card.
- The test has failed on `button geometry scifi.city` at every map revision since (route-inset, v01, v02 and v03 notes).

**Update (same file, same three destination IDs `scifi.city`, `scifi.outskirts`, `scifi.ruins`).** In both languages, each destination button is checked in its region view. It must:
- be the place marker of a travel-data place, on its coordinates;
- cover its marker with its button;
- keep its plate inside the map frame, clear of every fixed control;
- not overlap another place's click target;
- be visible, enabled and show a non-empty name.

A press must open that place's route card, stay on the map, leave `current_destination_id` unchanged and charge no minutes. Departure goes through Depart / `confirm_travel`, which the travel regressions cover. The window is pinned to native 640×360, as in the map capture tools: the project window is larger than in M8, so the old capture-size assertion also failed once the geometry was fixed. The M8 background-asset import check is kept.

**The updated test passes on both v03 and v03r1 scripts.** That confirms the runtime destination geometry did not need a fix; only the expectation did.

## Before / after logs (real Godot 4.7.2)

| Test | Before (v03 scripts) | After (v03r1) |
| --- | --- | --- |
| `background-visual-check` (windowed) | **FAIL** `WORLD_MAP_VISUAL_CHECK_FAILED: button geometry scifi.city` ([log](../../outputs/rpg-2-star-ocean-the-second_global-map_v03r1_bg-visual-check-before_test-only-v03r1_20261017-184737-5ef3676e.log)) | `WORLD_MAP_VISUAL_CHECK_OK captures=2 buttons=3` ([log](../../outputs/rpg-2-star-ocean-the-second_global-map_v03r1_bg-visual-check-after_test-only-v03r1_20261017-184737-5ef3676e.log)); headless `captures=0 buttons=3`; updated test on v03 scripts `captures=2 buttons=3` |
| v03r1 zoom-label tool | **FAIL 16/503**, all in the zoomed Washington card: NYC label across the card / clear of fixed UI; Washington label over Globe and region buttons; button pixels repainted (96 / 360 Globe, 2302 region) ([log](../../outputs/rpg-2-star-ocean-the-second_global-map_v03r1_zoom-tool-before-v03_test-only-v03r1_20261017-184737-5ef3676e.log)) | `MAP_V03R1_ZOOM_LABEL_OK 503 checks, 6 captures` ([log](../../outputs/rpg-2-star-ocean-the-second_global-map_v03r1_zoom-tool-after_test-only-v03r1_20261017-184737-5ef3676e.log)) |

The "before" runs used a temp copy of the current `game/` tree under `%LOCALAPPDATA%\Temp\wb-map-v03r1\root-before` with v03's `scifi_world_map.gd` (sha256-text-lf-v1 `ad451eb52008a0e4`, = HEAD) restored. The v03r1 tool ran unchanged against both trees.

## Captures: real Godot, native 640×360, windowed

**Tool:** `tools/rpg-2-star-ocean-the-second_global-map_zoom-label-clamp_capture-check_test-only-v03r1_20261017-184737-5ef3676e.gd`. A second run reproduced all six captures byte for byte. Files are in `outputs/`, named `rpg-2-star-ocean-the-second_global-map_v03r1_<state>-640x360_test-only-v03r1_20261017-184737-5ef3676e.png`, with a capture manifest and checks JSON beside them.

| State | zh (sha256, first 16) | en | vs v03 |
| --- | --- | --- | --- |
| Northeast browse | `us-northeast-zh` `418b24c3ef3a9baf` | `us-northeast-en` `249ae409a57de439` | identical to v03's captures |
| Zoomed (1.5×) Washington car card | `us-northeast-zoom-card-washington-car-zh` `0187f93b0ae76411` | `…-en` `99332a5a398e3a6c` | **changed** (the fix) |
| Chicago flight card (strip) | `us-great-lakes-card-chicago-air-zh` `a1a5b1678c74c2dd` | `…-en` `4c6c705e71489585` | identical to v03's captures |
| Before: zoomed Washington card, v03 scripts | `before-v03-zoom-card-washington-car-zh` `3d102c5a8732303f` | `…-en` `10e49afb4afc4dca` | v03 defect record |

**What the tool checks in each state, zh and en:**
- Every visible place plate whose marker is in the frame:
  - is inside the frame and above the footer;
  - is clear of every fixed control, both by `fixed_ui_rects()` and by the zoom, Globe and region button rects themselves;
  - is clear of the card, the other markers and its own marker as drawn;
  - is 2 px or more from other plates, within 64 px of its marker, and named at 12 px or more;
  - has a click target that overlaps no other place's.
- **Rendered proof:** with the place buttons hidden, the four view and zoom buttons and the open card render identically (0 px differ), and each plate's full rect changes, so the plate is really drawn and not clipped. Zoomed card plates: Washington 3240/3240 (zh) and 3834/3834 (en), New York 2052/2052 and 2403/2403.
- **Card:**
  - it keeps the CARD_RECT width and stays within its height (238 px);
  - title, kind and from are 11 px or more, the subtitle and coordinates 10 px or more, and the option line 11 px or more;
  - every shown line plus Depart and Cancel sit inside the card;
  - the card is opaque (0 map pixels show through);
  - the selection reticle ticks are drawn.
- **Trips:**
  - the trips are pinned: Washington by car 300 min, Chicago by air 360 min;
  - arrival is the date only ("2537年5月25日" / "May 25, 2537");
  - modes are generic and charges are whole hours;
  - the option line equals `route_option_text()`;
  - no airport, terminal or check-in word appears on the card, the strip or the labels;
  - previews, zoom and language swaps charged nothing.

**Readability at native size.**
- Card text is unchanged from v03 and readable in both languages.
- In the zoomed Washington card, v03's overflow rule still drops the coordinates line (zh), and the coordinates and "From" lines (en). The strip's gold-ringed origin names New York.
- The Chicago card keeps every line.

## Targeted regressions (Godot 4.7.2, live tree after the fix)

Summary log: [`…_v03r1_regressions_…log`](../../outputs/rpg-2-star-ocean-the-second_global-map_v03r1_regressions_test-only-v03r1_20261017-184737-5ef3676e.log). There was no `SCRIPT ERROR` in any log.

- **Headless:**
  - `GLOBAL_EARTH_MAP_SMOKE_OK checks=212`
  - `GLOBAL_MAP_TRAVEL_INTEGRATION_OK checks=114`. v03 recorded 111. The static guard runs one check per script in `game/scripts/`, and other workstreams have since added Chicago v03r1 scripts to the shared tree.
  - `GLOBAL_TRAVEL_CORE_OK`
  - `M2_WHOLE_HOUR_TRAVEL_OK checks=246`
  - `EXPORT_DATA_INCLUSION_SMOKE_OK mode=source checks=24`
  - `US_SCIENCE_MIGRATION_SMOKE_OK checks=32`
  - `COMMERCE_WEEKLY_SETTLEMENT_OK checks=149`
  - `M2_SMOKE_OK`, `M6_SMOKE_OK`, `M6_RESTART_OK`
- **Windowed** (captures to temp):
  - `ROUTE_CARD_READABILITY_OK 117 checks`. This includes the zoomed Washington state.
  - `STATUS_BACKING_READABILITY_OK 203 checks`
  - `CANVAS_POINTER_REGRESSION_OK` (real window-pixel clicks)
  - `WORLD_MAP_VISUAL_CHECK_OK` (updated, see above)
- **v03 tools:**
  - The v03 capture tool on a temp copy with the v03r1 script printed `NATIVE_MAP_ART_OK 1873 checks, 12 captures`, all 12 byte-identical to v03.
  - The v03 source check (report written to temp) printed `SOURCE_CHECK_OK 40 checks`. The route core and travel data equal git HEAD, and the rebake is identical.

**This pass is all-pass on the targeted set**, including the previously inherited `background-visual-check` failure.

## Files (local, unstaged)

| File | State | sha256-text-lf-v1 (first 16) |
| --- | --- | --- |
| `game/scripts/scifi_world_map.gd` | modified vs HEAD/v03 (+73 lines): `CLAMP_REACH` constant, a 2-line call in `_place_marker_button`, new `_clamped_label_rect` and `_segment_hits_rect` | `8fdc130c4a4500ec` |
| `game/tests/rpg-2-star-ocean-the-second_scifi-world-map_background-visual-check_m8-v01_20261014-143900-239f6b80.gd` | modified: Earth-map destination-button contract, native 640×360 window | `af235b5958f84153` |
| `tools/rpg-2-star-ocean-the-second_global-map_zoom-label-clamp_capture-check_test-only-v03r1_20261017-184737-5ef3676e.gd` | new (test-only) | `aa697bf77582f7d1` |
| `game/scripts/world_map_data.gd`, `game/scripts/world_map_text.gd` | **unchanged** (= v03) | `c1fe920f07f9613e`, `68400bef1ac32496` |
| `outputs/…_v03r1_*` | new: 6 captures + 2 before captures, capture manifest, checks JSON, 4 before/after logs, regression summary | see the tables above |

## What remains open (candid)

1. **Map art is still unapproved.** This is a legibility correction, not an art pass. Every v03 open item about style stays: planning-UI card body, stock-theme buttons, the small strip, the dense card, bigger plates over New Jersey and Western Europe, and the narrower sea step.
2. **Zoomed Washington's marker is still boxed in.** The marker itself is not moved (geography). The top tick of its selection ring reaches about 1 px under the region button's bottom edge (the ring top is at y 244.9 and the button ends at 246; the button draws over it). Its lowest tick meets the frame bottom. The label now sits 48 px away on a leader, which is a fallback, not an ideal placement. At deeper zoom or other pans, other boxed-in states may also need the fallback. Each is checked only where a tool visits it: this tool's zoomed state and the route-card readability check.
3. **A place under the card keeps a plate at the card's edge** (New York in the zoomed card). The plate names a dot you cannot see, joined by a 3 px leader stub. Hiding it instead would remove a click target, which the dispatch forbids. Codex should judge whether the edge plate reads clearly.
4. **The zoomed card still drops lines** (v03's overflow rule): the coordinates in zh, and the coordinates and "From" in en. The strip there is the NYC↔Chicago relief drawn at non-1:1 scale. Both are unchanged from v03.
5. **Selected label on the right slot touches its own selection ring.** v03's standard "right" slot starts 10 px from the marker, so the Chicago card's plate overlaps Chicago's 11.5 px selection ring by 2 px (recorded as a fact, not a failure). This is unchanged from v03 and was left alone to keep the default-zoom captures identical.
6. **Off-frame markers keep off-frame (clipped) plates**, as before; Yonkers at this zoom is one. There is no edge indicator for off-view places.
7. **The updated background test checks default-zoom geometry and the click-to-card contract only.** The zoom fallback is covered by the v03r1 tool and the route-card readability test, not by it.

## Reproducibility

- **Capture and check:** needs a display and takes about 15 s. Rerunning overwrites the same six files byte-identically.

  ```
  work/tooling/godot-4-7-2/Godot_v4.7.2-stable_win64_console.exe --path game -s <absolute path to the v03r1 tool>
  ```

  Set `WB_MAP_V03R1_OUT=<folder>` to write elsewhere (used for the "before" run).

- **Before run:**
  1. Copy `game/` to a temp folder.
  2. Restore `git show HEAD:game/scripts/scifi_world_map.gd` there.
  3. Run the same command with `--path <temp copy>`.
- **Background test:**

  ```
  …console.exe --path game --script res://tests/rpg-2-star-ocean-the-second_scifi-world-map_background-visual-check_m8-v01_20261014-143900-239f6b80.gd
  ```

  Set `WB_MAP_EVIDENCE_DIR` to write its two captures and manifest.
