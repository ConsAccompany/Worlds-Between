# NYC City Hall Park — native 640×360 scene candidate v06 (reference-transfer pass) — QA note

**Status: UNAPPROVED.**
- This is one bounded candidate for Codex to judge. It is not accepted art.
- Counters are unchanged: meter **40.8%**, accepted science scenes **3/12**, complete sprites **0/52**, human playtests **0/2**.
- Nothing was staged, committed or pushed. No progress state, Game Bible, map, Chicago, Washington or Git-index file was touched.
- Run: `nyc-chp-v06_20261017-165253-4519dffe`.
- Author: Claude Code (Opus 5.5) on the signed-in Claude Max subscription. `claude auth status` reported `authMethod: claude.ai`, `apiProvider: firstParty`, `subscriptionType: max`. `ANTHROPIC_API_KEY` was absent. No API billing, image model or paid fallback was used.
- v05 (`nyc-chp-v05_20261017-015916-23a7984f`) is untouched and remains the audit baseline. The v06 check re-hashes all of v05's files against its manifest.

## Inputs read

- Global `~/.codex/AGENTS.md` (naming rules) and the repo status.
- The [v05 QA note](rpg-2-star-ocean-the-second_nyc-city-hall-park_scene-candidate-640x360_qa-note_unapproved-v05_20261017-015916-23a7984f.md) and the [style-alignment direction](rpg-2-star-ocean-the-second_nyc-city-hall-park_style-alignment-visual-direction_unapproved-v01_20261016-225800-2a4e7c91.md).
- The v05 Godot captures and the current runtime city capture.
- The accepted NYC public-facilities Room 1 and Room 2 captures (`outputs/room1-visual-review/`, `outputs/room2-fixtures-pilot/`).
- The nonruntime art-direction reference `outputs/…style-alignment-reference_nonruntime-v01_20261016-225515-5ee8060c.png` (sha256 `4a029b72…`, 1672×941, untracked).

## Source honesty

Most visible pixels come from an **imported generated source**: the AI-generated nonruntime reference. **This scene is not wholly hand-painted** and must not be described as hand-painted.

The tool processes the reference as follows:
- **Recomposition:** it box-recomposes the reference for the real game frame. Reference rows 0–425 map to screen rows 62–171, and rows 425–860 map to rows 172–317. Horizontal scale is 0.383. City Hall is therefore vertically squashed about 0.68 and the park about 0.88.
- **Palette reduction:** deterministic k-means to 72 colours, plus 16 hand-picked native accents (88 colours, all used).
- **Cluster pass:** a lonely pixel takes its neighbour majority when the colours are close. High-contrast singles such as window lights and flower heads are kept on purpose.
- **Layer split:** the result is split into named layers.

Visible-pixel share by origin (rows 62–317 of the flat, measured by the tool):

| origin | share |
|---|---|
| imported reference (unchanged position) | 70.4% |
| imported reference, moved (SE elm) | 4.4% |
| imported reference, recomposed (lawn/hedge/bed/bench patches, repeated lamp) | 5.5% |
| native | 19.7% |

Native work:
- **Walk network:** the north promenade with warm border courses, the west apron, the fountain link, the west link, the terrace walk with its retaining-wall face, the report link, a re-laid report plaza (radial pavers, plinth removed) and the kiosk apron. Each has curbs, grass overhang and edge shading. Flag tones are sampled from the reference's central walk.
- **Removals:** lawn and hedge in-painting where trunks, the plinth and the terminal were removed.
- **Moves:** the east elm is moved to the SE lower lawn and given a crisp rim. The reference's teal terminal is moved to the report plaza.
- **Fixtures:**
  - the public-works survey stair kiosk;
  - the allocation-ledger board;
  - a gate-pier inspection sheet (trace 2);
  - the double-numbered sign with teal (repair) and amber (storage) pavement lines (trace 1).
- **Smaller details:** promenade teal inlay studs, a report-plaza teal ring, and cupola patina. The reference's gilded dome is toned to verdigris, because real City Hall has no gold dome.
- **Gameplay data:** the walk mask, obstacles, Y-sort pivots and crown-reveal parameters.

## Files

| path | role |
|---|---|
| `tools/…_scene-author-640x360_unapproved-v06_20261017-165253-4519dffe.py` | author/preview/check tool, 1,334 lines, sha256-text-lf-v1 `43026d4a…`; `python -I -B <tool> preview <dir outside repo> \| build \| check [--write-report]` |
| `game/scripts/city_hall_park_v06_scene.gd` | runtime layer loader, mask collision, legacy migration, crown-reveal shader (255 lines, `f5e1ac2b…`) |
| `tools/…_godot-entry-traversal-collision-check_unapproved-v06_….gd` | Godot harness + captures (422 lines, `43137749…`) |
| `tools/…_godot-export-pack-check_unapproved-v06_….gd` | exported-pack check (92 lines, `a9c1f06b…`) |
| `game/assets/environments/candidates/nyc-chp-v06_20261017-165253-4519dffe/` | `.pxo` `3ba6ad20…`, `.ora` `e4c839b8…`, flat `29b6cad4…`, `.gpl`, walk mask `674fb82d…`, rt-base, 9 rt-y layers, `scene.json` + `scene.tres`, and a manifest with all hashes and per-layer origin. The longest path including `.import` is 255 characters. |
| `outputs/nyc-chp-v06_20261017-165253-4519dffe/` | check report, 18 Godot captures, capture manifest |

Layers, bottom to top:
1. **Reference layers:** `ref-backdrop-skyline-treeline-fence`, `ref-city-hall`, `ref-park-ground`.
2. **Recomposed and native base layers:** `inpaint-lawn-hedge`, `native-walks`, `native-ground-detail`, `native-fixtures`.
3. **Y-sorted layers** (z = pivot row): `lamps-promenade-s` 216, `bollard-plaza` 229, `lamp-axis-e` 249, `fountain-centre` 262, `lamp-plaza-e` 273, `lamp-plaza-w` 273, `bollard-junction-se` 275, `tree-east-elm` 305 (canopy), `cart-se` 316.
4. **Hidden and locked:** `guides`.

## Composition (what changed against v05)

- **City Hall** now spans 345 px and rows 62–150: the cupola with clock, the balustraded wings, the portico and stair, flags, and gate piers with lanterns. In v05 it was 248 px with a facade about hero height. Only the cupola's finial is under the header.
- **Park layout** follows the reference: a fountain plaza in the west, the central axis, and terraced east lawns with a retaining wall. Lamps, banners, bollards, benches, a cart, Broadway on the left and the Park Row sidewalk on the right complete it.
- **Walk lanes** sit on top of that layout:
  - the promenade in front of the City Hall fence joins every north hotspot;
  - a full lane rings the fountain basin;
  - the axis links through the west link to trace 1;
  - the terrace walk and report link lead to the report plaza;
  - the kiosk apron gives access to the survey entrance.
- **Kept unchanged:** the destination, names, travel, canon, spawn (340,253), Liang Xu (282,180), all hotspot coordinates and radii, and the 48-logical-px actor. Every hotspot is exactly standable, and none of their runtime markers sit under a Y-sorted sprite (0 pixels).

## Occlusion: crowns never nearly hide the hero

- NW and NE tree crowns are backdrop behind the hedge line, so no walkable foot is behind them.
- The only crown over walkable ground is the moved SE elm. It covers at most **31.8% of the hero's body**, at the promenade's east end (594,203). v05's NE elm hid her completely.
- That crown carries a **dithered reveal shader** (logical-pixel Bayer 4×4 hole around the body). It opens while the hero is behind the crown and closes once she leaves, at 6/s.
- Measured in Godot at that worst-case foot, the share of hero pixels visible is **0.888 with the reveal and 0.706 without**.
- In v06 the old hide-and-silhouette cue is not used: `hidden_by_canopy` returns false.
- Fountain centre, lamps, bollards and the cart are Y-sorted. The harness verifies that promenade-lamp pixels draw over a hero standing behind them (exact pixel match).

## Legacy save at (82,260)

- `(82,260)` is the old generic area spawn that pre-navigation city saves still hold. The old plate recovered it onto its west road at exactly `(82,203.5)`. v05 kept it, because it was valid paving there, so the existing smoke failed with v05 on.
- In v06, `(82,260)` is planting beside the plaza lamp, so it is not standable. `(82,203.5)` is deliberately kept as standable west-apron paving.
- The scene data declares the migration explicitly: `legacy_positions: [{from: [82,260], to: [82,203.5], why: …}]`. The runtime applies it only to that exact position, and prints a log line when it does, so the migration is not silent.
- Old saves land where they always did. The save file is not rewritten on load: the harness compares the file before and after.
- The existing assertion `== Vector2(82, 203.5)` is **unchanged**. `game/tests/m8_city_integration_smoke.gd` gains one stronger assertion (+2 lines): the recovered position must be standable in the active city layout. It passes on the old plate too.
- Results:
  - `m8_city_integration_smoke` passes in default mode and with `--city-hall-park-v06`.
  - With `--city-hall-park-v05` it still fails at the same old assertion. The v05 baseline is unchanged.

## Export

- Scene data ships as a `.tres` resource (`metadata/scene_json`) that the runtime loads. `export_presets.cfg` is unchanged.
- **Verified with a real export:**
  - `--export-pack "Windows Desktop"` from an isolated copy of `game/` produced a 58 MB `.pck`;
  - `Godot --main-pack <pck> -s <export check>` passed 10/10, running from the pack only;
  - from the pack, the `.tres`, all 11 textures (with readable images), the v06 script, the reveal shader and the legacy migration all load, and the city scene runs the v06 layers;
  - capture: `godot-exported-pack-en-entry-640x360`.
- **Correction to the v05 QA note.** Godot 4.7.2's `all_resources` filter **does** export `.json` files, because JSON is a resource type. The pack contains both the v06 and the v05 scene JSON, so v05's "would not ship" remark was wrong.

## Runtime integration (opt-in, reversible)

- **Off by default.** The old plate, its navigation and all its tests are unchanged.
- **To play:** `Godot --path game -- --city-hall-park-v06`. Tests can instead set `city_hall_park_v06_scene.gd` `enabled_override = 1`. The v06 flag takes priority over `--city-hall-park-v05`.
- **`game/scripts/scifi_exploration_area.gd`** (already modified by other sessions) gains four small hunks:
  - a preload;
  - the `city_hall_park` variable is untyped, so it can hold v05 or v06;
  - a v06-first branch before the existing v05 branch;
  - a `bool` annotation on `hidden_by_canopy`.
- **Godot `--import`:** it created the run's `.import` files and `city_hall_park_v06_scene.gd.uid`. It also created one `.import` for another session's file (female sideview v11 PNG), which was deleted. Other foreign `.import`/`.uid` files in `git status` were already there.

## Evidence: real Godot 4.7.2 captures (windowed native 640×360, GL Compatibility)

`outputs/nyc-chp-v06_20261017-165253-4519dffe/rpg-2-star-ocean-the-second_nyc-city-hall-park_godot-<view>_unapproved-v06_20261017-165253-4519dffe.png`. All 18 are hashed in the capture manifest.

| group | views |
|---|---|
| entry (approved v8 static at 48 px) | `zh-entry-640x360`, `en-entry-640x360` |
| same-viewport reference (switch off) | `en-current-runtime-city-reference-640x360` |
| traversal (real input) | `zh-traverse-axis`, `zh-traverse-promenade-gate`, `en-traverse-fountain-behind`, `en-traverse-report-plaza`, `en-traverse-survey-kiosk` |
| occlusion | `en-occlusion-se-elm-reveal`, `zh-occlusion-se-elm-reveal` |
| interactions | `zh-interact-liang-xu`, `zh-interact-trace-sign`, `en-interact-trace-pier`, `en-interact-ledger`, `en-interact-report-locked`, `zh-annex-return-kiosk` |
| legacy save / export | `en-legacy-save-landing`, `exported-pack-en-entry` |

## Checks

- **Author `check --write-report`: PASS 29/29.** Gates covered:
  - fresh rebuild equals the files on disk, the build is deterministic, the reference hash is pinned, and the v05 files are unchanged;
  - binary alpha, opaque base, and palette-only flat;
  - a single walk component, every hotspot exactly standable, the visible band, no feet in the basin, and every walkable foot on paving;
  - legacy spawn not standable, landing standable, and the assist-down block below 204;
  - the integration smoke's straight hotspot walks simulated;
  - markers clear of Y-sort layers, a 48-px heroine, and occluder behind-cases;
  - `.pxo` layer list, and `.tres` = JSON.
- **Pixelorama 1.2.3 headless (part of the same check):**
  - `.pxo` and `.ora` flat exports are exact;
  - split layers are exact for every art layer;
  - hidden guides are not exported;
  - the sources are unchanged.
- **Pixelorama isolation:** another session's Pixelorama GUI was open, so the parent `APPDATA` pointed at an empty temp dir. A manual snapshot of the real `%APPDATA%\pixelorama` showed only that GUI's `.running` heartbeat changing.
- **Godot harness: `CHP6_GODOT_CHECK_OK`, 86 PASS / 0 FAIL, 1,008 moved frames, 0 frames off the walk mask.**
  - **Traversal:** routes walked by real input, including a full lap of the fountain lane.
  - **Reveal:** opens and closes, with the measured visibility above.
  - **10 collision probes:**
    - promenade north edge, axis curb, and basin from the south and from the north;
    - plaza lamp, footer, kiosk stair mouth and kiosk hedge;
    - report terminal, and the ledger south edge (blocks before 204).
  - **Reachability:** a swept flood reaches all 6 hotspots, and save/resume recovery is stable.
  - **Interactions through the real `interact` action:**
    - Liang Xu, trace 1, trace 2 and the ledger assist;
    - the report answers "locked";
    - the survey entrance opens `SurveyAnnex`, and `_back_room()` returns onto the apron.
  - **Legacy save:** end to end.
- **Export check: `CHP6_EXPORT_CHECK_OK` 10/10** (from the `.pck` only).
- **Existing smokes, all passing:**
  - default (headless): `m1`, `m2`, `m7`, `m8_city_navigation`, `m8_city_reentry`, `m8_city_integration`, and the canopy-silhouette sync smoke;
  - with `--city-hall-park-v06`: `m8_city_integration`, `m8_city_reentry` and `m8_city_navigation`.

## Comparison (judge at 1×, same viewport)

- **Against v05.** v06 is much closer to the creator's target:
  - City Hall is large and recognisable, not a hero-height strip.
  - Foliage is layered with lit tops and cool undersides instead of one seeded clump stamp.
  - The fountain plaza, lamps, banners and teal bollards read as one material language.
  - The hero is never fully hidden.

  The cost: most of the image is a recomposed generated reference rather than authored pixel art. Native additions (paving, kiosk, sign, board) are visibly simpler than the reference-derived areas around them.
- **Against the accepted interiors (Room 1 / Room 2).** Warm masonry, cool shadow planes, teal civic emitters and dense small-scale texture now match better than any earlier park candidate. The interiors are tighter, darker and more deliberately clustered; v06's reference-derived foliage and lawns still show some soft, noisy clusters at 2×.

## Visible flaws (candid)

1. **The north promenade is a wide, flat, regular band** across the middle of the frame. It is required so that Liang Xu, trace 2, the ledger and the old-save landing stay on their exact coordinates. Its repeated six-row courses read as manufactured next to the reference paving.
2. **Seams:**
   - native flags meet the reference's fountain-ring and axis pavers with a visible change of grain;
   - the west link, terrace walk and report link are rectangular blocks;
   - the kiosk apron reads slightly like a raised plinth.
3. **City Hall is vertically squashed** (about 0.68) to fit under the header. The cupola's finial is cut by the header line, and the dome shape is still the reference's enlarged form, only recoloured.
4. **The fountain is the reference's stone tazza**, not the restored Mould fountain.
5. **The kiosk, sign and board are simple native drawings.** They are clear at 1×, but less rich than the reference props.
6. **Some imported detail stays soft at 2×** after quantization, in foliage noise and lawn stripes. The skyline is the reference's generic massing.
7. **The SE elm crown** is cut by the right screen edge and overhangs the Park Row sidewalk props.
8. **The hero can stand directly north of the fountain**, where the bowl hides her legs (correct depth, but it can read as "in the bowl"). The capture uses a partly-behind spot.
9. **Runtime marker discs and labels** sit over the art unchanged. Traversal and interaction captures use the runtime's walk and idle frames. No visitor NPCs exist.

## Decision for Codex / creator

- v06 is left as an **opt-in runtime candidate** (default off), the same status v05 had. It is a clear step past v05 and fit to show for **environment-only** review beside the paired current-city capture. It is not fit to present as final hand-authored art.
- If Codex judges the reference-transfer look or flaws 1–3 unacceptable, the next step is to remove the `CityHallParkV06` preload and branch in `scifi_exploration_area.gd`, which makes v06 nonruntime. That is a small, self-contained revert.
- Open questions:
  - Keep the promenade width, or move some hotspot coordinates (canon) so the lawn can come back?
  - Real Mould fountain or reference tazza?
  - Accept the City Hall squash, or crop the skyline instead?

## Process notes

- **Scratch files:** previews and logs live under `%TEMP%\chp6`, outside the repo. The isolated export copy of `game/` and the `.pck` were deleted after the export check.
- **Rebuild:** the candidate directory was rebuilt once, deleting only this run's own files, to shorten runtime layer names below MAX_PATH (265 → 255).
- **Concurrent sessions:** other sessions changed Game Bible and meter files during this work (staged `tests/*.js`, `outputs/*state*.json`). They were not touched.

## Selective sync addendum (2026-10-17 17:40 EDT, Claude Code Opus 5.5, Max firstParty)

Codex reviewed v06 and kept it **UNAPPROVED**. Its objections: the wide promenade is flat; seams and rectangular links remain; the City Hall dome is vertically compressed and cropped; the fountain is not the Mould fountain; and about 80% of visible pixels derive from the generated reference. The art was **not** revised, and no v07 exists. Only what makes v06 reproducible from Git was changed:

- **v05 is not synced.** It stays a local-only baseline, so the committed `scifi_exploration_area.gd` carries **only the v06 opt-in path**: one preload, the untyped `city_hall_park` variable, the v06 branch, the draw guard, the silhouette helper (at `CityHallParkV06.SILHOUETTE_Z`, the same 3000 as v05), the `bool` canopy annotation, and the safe/slide/walkable delegation. The worktree copy still also holds the v05 branch and other sessions' Yonkers fixture hunks, which are not committed.
- **Two code-only patches** let the checks run where v05 is absent. They do not change the art:
  - The author tool records `v05_baseline_present` and gates `v05_baseline_files_unchanged` only when v05 exists. It never counts the gate as passed when v05 is missing. Tool sha256-text-lf-v1 is now `724c254c…` (was `43026d4a…`).
  - The Godot harness switches off the v05 override only if that script exists (`f5be30f2…`, was `43137749…`).
- **Generated source is tracked.** The AI-generated nonruntime reference `outputs/…style-alignment-reference_nonruntime-v01_20261016-225515-5ee8060c.png` (sha256 `4a029b72…`) and its direction note are committed with v06, because `build`/`check` need it. That note told later passes **not** to paste or downsample the reference. v06 does exactly that for about 80% of its pixels, so it stays a reference-transfer candidate, not hand-authored art.
- **Verified on the exact staged tree** (exported into fresh clones):
  - author `check` with Pixelorama: PASS 28/28 (v05 gate skipped as absent) with autocrlf=true, and PASS without Pixelorama with autocrlf=false; in this worktree with v05 present it is 29/29;
  - Godot harness: `CHP6_GODOT_CHECK_OK` 86/0, 1,008 moved frames, 0 off-mask. 12 of 17 captures are byte-identical, including `zh-entry`, `en-entry` and the current-runtime reference. The other 5 differ only inside the hero's box (walk phase or reveal dither);
  - export pack: `CHP6_EXPORT_CHECK_OK` 10/10;
  - default: m1, m2, m7, m8 city navigation/reentry/integration and canopy smokes OK;
  - `--city-hall-park-v06`: m8 integration (the v06 legacy migration was logged), reentry and navigation OK.
- **Unchanged:** v06 is off by default and old saves are not rewritten. Counters stay at 40.8%, M2 10/12, scenes 3/12, sprites 0/52 and playtests 0/2.
