# Yonkers antenna corridor (room 1): v03 outdoor refinement candidate

**Status: UNAPPROVED.** The creator rejected v02's outdoor look ("继续精修室外画面"). This is a bounded v03 art pass for Codex to inspect at 1× before any creator question. Accepted science scene visuals stay **3/12**. The ledger, Game Bible, other scenes and the Git index are unchanged; nothing is staged or committed.

Dispatch: `docs/coordination/rpg-2-star-ocean-the-second_yonkers-antenna-v03-claude-dispatch_unapproved-v01_20261017-224300-8ac43e19.md`. Built 2026-10-17, 22:44–22:57 EDT, by Claude (Claude Code Opus 5.5, signed-in Claude Max firstParty; `ANTHROPIC_API_KEY` unset). The repo has no `AGENTS.md`; names follow the existing `rpg-2-star-ocean-the-second_<subject>_<status-version>_<stamp>` convention. Inputs: the [v02 creator feedback](rpg-2-star-ocean-the-second_yonkers-antenna-room1_v02-creator-feedback-and-v03-visual-target_unapproved-v01_20261017-195248-b8e3d71a.md), the [material-depth judgment](rpg-2-star-ocean-the-second_yonkers-antenna-corridor_material-depth-reference-visual-judgment_unapproved-v01_20261017-200235-9c17e2ab.md), and the [real-place transfer note](rpg-2-star-ocean-the-second_yonkers-outskirts_real-place-native-scene-visual-transfer_unapproved-v01_20261017-202137-77b9152e.md). The nonruntime imagegen reference was read only as direction. No pixel of it was pasted, traced or resampled.

## What changed from v02

The layer stack, sprite boxes (128×152 at y 58), props, markers and collision footprints are all unchanged. The runtime change is five asset paths in `game/scripts/survey_annex.gd`: the plate, the foreground and antennas A, B and C now point to v03 files. A gate confirms all 12 layout literals are present.

- **Parapet depth.** The sun now sits behind the parapet, so the masonry is one step darker.
  - The coping has a lit top, a jointed front face with chipped corners, and a dark drip edge with an underside shadow.
  - The wall face is in shade. Block edges are only partly lit. Weathering comes in clusters instead of single scattered pixels, plus 46 rain streaks and six spalls.
  - Each pilaster has a lit west face, a shaded front, and a cap that overhangs and shadows its own top course.
  - The parapet, pilasters and ivy project a jagged band of shade, about 11–13 px deep, onto the foot of the deck.
  - The side piers are also darker.
- **Localized deck wear.** Slab tone follows a slow field, so neighbouring slabs weather together. Wear is placed where it would happen:
  - traffic polish in front of each plinth and at both door aprons;
  - a damp stain along the wall foot;
  - seven placed cracks, some with branches and moss;
  - chipped slab corners;
  - rust drips under the anchors and riser clamps;
  - moss in clusters along the wall foot, plinth corners and shaded edges, with none in the traffic zones.
- **Grating rhythm.** The lane has 12 panels of unequal width (38–62 px) of three kinds:
  - bearing-bar panels, with cross rods at 5, 6 or 7 px;
  - a chequer-plate replacement panel by A;
  - dull, rust-stained panels by B and C, one of which is missing a rod.

  Highlights appear only in 0–3 lit patches per panel, plus 12 placed sun glints and boot polish in front of the markers and doors. The first rows sit in the trench lip's shadow. The brass nosing is worn back to steel where boots cross it. The trench covers vary in length, and one lifted cover shows the teal and brass cables.
- **Concave dish B.** The ellipse is more foreshortened: minor/major 0.53, down from v02's 0.68.
  - The sun-side rim throws a hard crescent of shadow into the bowl, and the far lower-right wall is the brightest part.
  - Curvature rings are centred toward the vertex.
  - The upper-left lip is lit and the lower-right lip turns away.
  - A dark back shell shows below the rim, and a rear truss runs to the yoke.
  - The feed horn sits on three struts with its shadow inside the bowl.
- **HUD clearance.** Antenna A's top parts drop 11–14 px and C's radome, crossarm and collar drop 4–9 px. The highest texels are now at y **73** (A), **83** (B) and **68** (C). None sit under the 62 px header: 0 texels at y < 62, and the author asserts no texel above y 66.

## Artifacts (new, untracked)

- **Author:** `tools/rpg-2-star-ocean-the-second_yonkers-antenna-room1_corridor-scene-author_unapproved-v03_20261017-224447-15709be4.py`. Deterministic: two runs produced identical hashes for all 7 outputs. Palette: 65 declared colours, all used, binary alpha.
- **Editable source** (13 layers, Pixelorama `.pxo` v7, OpenRaster `.ora`, flat preview): `outputs/yonkers-room1-v03_15709be4/rpg-2-star-ocean-the-second_yonkers-antenna-room1_corridor-scene-layers_unapproved-v03_20261017-224447-15709be4.{pxo,ora,png}`
- **Manifest:** `outputs/yonkers-room1-v03_15709be4/rpg-2-star-ocean-the-second_yonkers-antenna-room1_corridor-scene-manifest_unapproved-v03_20261017-224447-15709be4.json`. It records sha256 hashes, layout and `hud_clearance`.
- **Runtime PNGs and `.import` files:**
  - `game/assets/environments/yonkers-antenna-room1/…_{corridor-plate,foreground-occluder}_unapproved-v03_20261017-224447-15709be4.png`
  - `game/assets/props/yonkers-antenna-room1/…_{antenna-a-lattice-yagi,antenna-b-dish,antenna-c-guyed-whip}_unapproved-v03_20261017-224447-15709be4.png`

  The v02 PNGs stay on disk, unreferenced.
- **Godot check:** `tools/rpg-2-star-ocean-the-second_yonkers-antenna-room1_godot-capture-and-check_unapproved-v03_20261017-224447-15709be4.gd`, with log `outputs/yonkers-room1-v03_15709be4/…_godot-check-log_unapproved-v03_….txt`.
- **Gate:** `tools/rpg-2-star-ocean-the-second_yonkers-antenna-room1_pixel-source-pixelorama-check_unapproved-v03_20261017-224447-15709be4.py`, with report `outputs/yonkers-room1-v03_15709be4/…_pixel-source-pixelorama-check-report_unapproved-v03_….json`.
- **Accepted-room replay:** captures in `outputs/yonkers-room1-v03_15709be4/acc/` (8 files), with log `…_accepted-rooms-replay-log_v03_….txt`.

## Native 640×360 Godot captures (30)

Folder: `outputs/yonkers-room1-v03_15709be4/captures/`. Files are named `rpg-2-star-ocean-the-second_yonkers-antenna-room1_v03-godot-<zh|en>-<label>-640x360_20261017-224447-15709be4.png`. Each label below exists in **both zh and en**:

- `entry`, plus `entry-runtime-heroine`, which uses the actual runtime sprite;
- `approach-a`, `approach-b`, `approach-c`;
- `interact-a`, `interact-b`, `interact-c`, each opened by a real `interact`;
- `b-dish-from-lane`;
- `occlusion-behind-a`, `occlusion-behind-c` (A/C depth overlap);
- `beside-b`, `west-stair`;
- `traversal` (real held input);
- `returned-from-room2`, taken after a real next → room 2 → back trip, at 6/6 clues.

Apart from `entry-runtime-heroine`, the shots use the approved female south idle at 48 px for review, as in every room review.

## Test outcomes (exact)

| Check | Result |
|---|---|
| Godot check | `YK1_V03_ALL_OK`; 0 script errors, 0 fail lines |
| HUD | `YK1_V03_HUD_CLEAR` A top y 73, B 83, C 68; texels under the header 0/0/0 |
| Six clues | Room 1: 3 clues × 3 approaches (marker, side, behind), with 0 false positives at 5 lane/deck spots. Room 2: 3 clues by real interact. `YK1_V03_ALL_SIX_CLUES_OK 6/6` |
| Transitions | Next → room 2 (no room-1 build leaks into it); room 2 back → room 1 at (555, 257), unblocked; exit → `scifi_exploration_area.tscn`; isolation OK in 4 other rooms |
| Collision | 14/14 held-input cases. The largest difference in stop position from v02 is 0.002 px. Diagonal slide and walk-out-of-plinth both OK. Reachability 56,083 cells, the same as v02. |
| Occlusion | Probe hidden behind A: 192/480 px (v02 188). Behind C: 270/480 (v02 265). In front of each antenna 480/480 visible, lane 480/480. The strip behind B stays walk-blocked. |
| Captions/markers | 0 antenna texels under any caption or marker, zh and en. The en header ends at x 621 (v01 reached 639). |
| Pixel/source/Pixelorama gate | **16/16**: S1–S4, P1–P3, C1–C3, G1, R1–R3, H1, L1. Pixelorama 1.2.3 CLI exported all 13 split layers and the flat image exactly for both `.pxo` and `.ora`. It ran with a temp APPDATA, and the real one was unchanged. The zh/en entry captures equal the authored scene outside the UI (150,477 / 149,065 px compared, 0 different, including 11,753 antenna texels). |
| Accepted interiors | The replay of NYC rooms 1–2 and Yonkers room 2 matched the acceptance captures (`…011400-d3590c0a`, `…010418-6b3138d8`, `…011814-94cebca4`) at 0 px on all **8 images**, and interactions passed 3/3/3. Their asset files show no `git status` change against HEAD. |
| WDC room 1 v02 | `WDC_V02_ALL_OK`, run in a temp folder. All 13 stored captures differ by 0 px. The only change is the expected `other-outskirts-room1` shot, which shows this room. |
| `m7_smoke` (headless) | `M7_SMOKE_OK`, no repo side effects |

## Codex 1× inspection notes and remaining defects

1. **Finish is still code-placed.** The plate is darker and less flat than v02, but it is still crisper and more geometric than the painterly accepted interiors. The coping top still reads as one continuous light line at 1×, and the pilasters remain the brightest stone.
2. **Deck rows are still regular.** The perspective slab grid is still a regular set of rows. The wear is now localized, but it is subtle at 1×.
3. **The dish's curvature rings are dashed.** They could read as panel seams rather than shading. The feed struts are 1 px and break up at 1×. The dish now reads as a tilted bowl in `b-dish-from-lane`, but only a creator look can confirm the "not a sign" goal.
4. **The parapet's cast-shadow band is subtle** because the wall-foot deck was already dark.
5. **Inherited from v02 and still open:**
   - The strip behind B is not walkable.
   - The 42 px marker trigger reaches the lane.
   - The door captions have no dark backing.
   - The English header fix applies to this room only.
   - The foreground shrubs barely touch the heroine (469/480 visible at the stair).
   - Antenna cast shadows are approximate projections.
6. **Process.**
   - `--import` again created a `.import` for another session's female sideview v11 PNG. I deleted only that file.
   - Another session's Pixelorama GUI (PID 37584) was left alone.
   - The v02 runtime PNGs, v02 notes and the v01 packet are now stale but kept.
