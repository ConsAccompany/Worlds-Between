# Exploration idle/walk pipeline · technical feasibility review · M8 v01

**Status:** this is an engineering analysis only. No PNGs, runtime scripts, registries or trackers were changed. No new Godot runs, captures or measurements were made: every number below either comes from the cited review documents, comes from reading the code, or is labelled as an estimate. Nothing here is art approval. The user has approved the **scale only** (48 logical px visible height, 640×360 logical, `canvas_items` at 1280×720). Animation and art quality are still unapproved. 0/52 exploration sprites are accepted. The 48-frame set in §3 is a **proposed one-character quality pilot**, not a production standard. The final per-variant frame count is undecided and depends on the pilot's evidence and on explicit user approval (see the [asset intake checklist](rpg-2-star-ocean-the-second_character-visuals_asset-intake-checklist_m8-design_20261014-162946-c4e7a19d.md), which follows the same rule).

Inputs read: [production standard draft](rpg-2-star-ocean-the-second_scifi-city_premium-exploration-production-standard_m8-draft_20261014-153400-481ae2c9.md), [quality spec v0.2](rpg-2-star-ocean-the-second_scifi-city_character-quality-spec_m8-v02_20261014-150058-3c97d04e.md), [protagonist concept manifest](../../game/assets/characters/high-fidelity-prototypes/rpg-2-star-ocean-the-second_protagonists_premium-direction-concepts-manifest_m8-v01_20261014-152650-9c21e75a.json), [Liang Xu concept manifest](../../game/assets/characters/high-fidelity-prototypes/rpg-2-star-ocean-the-second_liang-xu_exploration-direction-concepts-manifest_m8-v01_20261014-154500-fae9103a.json), the female walk reviews ([keyframe](rpg-2-star-ocean-the-second_protagonist-female_south-walk-keyframe-feasibility_m8-concept_20261014-153100-418eb35c.md), [four-phase v02](rpg-2-star-ocean-the-second_protagonist-female_south-walk-cycle-continuity-review_m8-concept-v02_20261014-155600-2c7f9a80.md), [procedural](rpg-2-star-ocean-the-second_protagonist-female_procedural-walk-fallback-review_m8-concept_20261014-160600-f25d7861.md), [segmented rig](rpg-2-star-ocean-the-second_protagonist-female_segmented-rig-walk-review_m8-concept_20261014-162000-417b2e95.md) and its [capture script](../../game/tests/rpg-2-star-ocean-the-second_protagonist-female_segmented-walk-visual-capture_m8-concept_20261014-161200-8b3a6f12.gd)), `character_directional_motion.gd`, `character_directional_idle.gd`, the walk logic in `scifi_exploration_area.gd` / `survey_annex.gd`, the [motion registry builder](../../tools/rpg-2-star-ocean-the-second_character-motion-registry-builder_m8-v01_20261014-181250-76bb5a42.py), and `project.godot` (the working tree has an uncommitted change to `stretch/mode="canvas_items"`, `scale_mode="integer"`).

## 1. Why animation continuity failed

| # | Root cause | Evidence | What the player sees |
|---|---|---|---|
| C1 | **Every frame is a separate generation.** No pixels are shared between frames, and the model has no persistent idea of which side or limb owns an accessory. | v02: the knee guard swapped legs; the scarf swapped sides until a targeted edit fixed it, but that edit failed to fix the knee guard. The keyframe doc found redrawn eyes, hair strands and belt. | Identity flicker; accessories jump sides. |
| C2 | **Each frame is normalized on its own.** Every frame gets its own scale (0.03709 vs 0.03747) and its own foot point taken from its alpha bounding box (source x 638 / 644 / 533). A stride is naturally shorter than idle, so forcing it to 48 px inflates the body. Registering on the *stride foot* moves the torso. | v02: torso centre x342.5 vs x338.1, a **4.3 logical px** lateral jump. | The body swims sideways between phases. |
| C3 | **Large sources are downsampled at runtime with nearest-neighbour.** 1024–1536 px sources are reduced about 27:1. Any change in position, rotation or source picks a different subset of source pixels. | Rig test rotates nearest-sampled parts by ±4° on a 1300 px source. The concept manifests and male review report low-alpha fringe across the canvas. | Pixel "boiling" and noisy edges even when the source art is identical. |
| C4 | **Wrong motion model for a 3/4 top-down walk.** Stepping toward or away from the camera (south/north) shows up as vertical foot offset, leg foreshortening and changes in overlap order. Rotating a leg about the hip in the screen plane only splays it sideways. Rigid one-segment legs that move with the body cannot plant a foot. | Rig test: legs at ±4°, body moving 5 px/frame, feet slide (doc confirms), arms static. Procedural test: limbs never change, so it reads as gliding or hopping. | Sliding, wobbling, "skating". |
| C5 | **Runtime timing is tied to the clock, not to distance.** `phase = floor(walk_time/0.12) % 4 + 1` (`scifi_exploration_area.gd:320`, `survey_annex.gd:151`) at `MOVE_SPEED = 140`. | One 4-phase cycle = 0.48 s = **67.2 px of travel, 33.6 px per step ≈ 0.70× body height**. A normal walking step at 48 px is about 0.35–0.45× height (17–22 px). | Even perfect frames will skate. At the current speed, the gait needs to be a jog/run stride or the speed needs to come down. |
| C6 | **Runtime assumes a fixed 32×48 cell.** `hero.offset = (0,-20)` is hard-coded. The registry stores textures only, with no per-frame pin or contact data. The builder hard-codes 19/20 frames for 5 named characters and preloads every texture in a `const`. | Code reading. | Any new cell size or anchor breaks alignment silently. Preloading 52 characters' frames at script parse does not scale. |
| C7 | **No measurable frame-to-frame gate.** Reviews judged single frames or one phase per facing (the integration review captured 12 stills). GIFs alter colours. | Review docs. | Defects were found only by eye, late, one at a time. |

**Note on C2:** per-image normalization is also how the static south/east/north direction concepts were displayed in the screenshot the user used to approve the 48 px scale. That was a static-scale experiment. It settled the display height, but it is not a method for animation frames. The production standard and the intake checklist now follow the rule in §3: one fixed-resolution master, plus one scale, one cell and one ground pin shared by every frame of a variant. Per-frame foot contact points are recorded for gait only, and are never used to rescale or recenter the torso.

Further runtime issues found by reading the code (none were run or tested):

- `city_hero_silhouette.texture` is assigned once in `_build_city_foreground()`, and `_update_city_labels()` updates only its position and visibility. It will probably show a stale idle frame while the hero walks under the canopy. It also uses LINEAR filtering.
- The facing rule `abs(y) >= abs(x)` has no hysteresis, so analog input near 45° can flip facing every frame. Each flip also resets the walk phase to idle (`_set_city_facing`).
- Hero positions are never quantized. Fractional positions with a nearest-filtered sprite produce per-frame texel jitter.

**Conclusion:** C1–C3 are structural to the generate-per-frame and runtime-downsample approach, and no amount of prompt revision fixes them. C4 explains why the cutout rig stayed unconvincing. C5–C6 will spoil *any* art, so they must be fixed whichever method is chosen.

## 2. Methods compared

| | A. Per-frame image generation + cleanup | **B. Layered part-swap sprites, offline bake (recommended)** | C. 3D proxy → pixel render → paint-over |
|---|---|---|---|
| How | Generate each pose image, then fix by hand or by edit prompt. | Per direction: one **idle master** at final resolution, split into locked layers (head/hair, torso, bag, insignia) and **pre-drawn limb parts** (legs: contact-front, contact-back, passing, lift; arms: 2–3 swings; ponytail/scarf: 2–3 secondary poses). A deterministic compositor places the parts at **integer offsets only** (no rotation or scaling) from a shared pose table, then a hand cleanup pass follows. | Model and rig each character, retarget one shared walk, render orthographic at the 3/4 angle at final resolution, then paint over. |
| Identity continuity | Poor (C1); unbounded cleanup. | **Guaranteed by construction**: locked layers are identical pixels in every frame. | Good geometrically; painted style may drift from the concepts. |
| Foot contact | Uncontrolled. | Controlled by the pose table plus distance-driven playback (§4). | Excellent. |
| Fit with the approved look | Matches concepts per frame but cannot loop. | Idle master starts from the approved downsample, so it can match it (see risk R1). | Uncertain for 51 stylized designs. |
| Setup cost (estimate) | Low. | Medium: compositor, metrics, Godot harness, plus one walk template per body archetype. | High: Blender pipeline, shader, base rig, per-character modeling. |
| Per-character cost (estimate) | Unbounded; failed 3 out of 3 attempts. | 2.5–4 person-days (pd) after the template exists (detail in §3). | 3–6 pd (modeling dominates); cheapest if many *more* actions are needed later. |
| Verdict | Use only for pose ideas and reference images (one image per file). **Never for shipped frames.** | **Adopt for the one-character gate.** | Fallback if B's limb drawing becomes the bottleneck. |

A runtime `Skeleton2D` / `Polygon2D` cutout rig is a variant of B and is **rejected** for shipping, because it rotates and resamples pixel art every frame (C3, C4). Godot is still useful as a *bake* host, as long as parts move only by integer offsets.

## 3. Recommended pipeline (Method B)

1. **Lock the cell.** One cell, pin and scale apply to every direction, action and frame of a visual variant. Author at 2× logical density, so 1 texel = 1 screen pixel. This continues spec v0.2's "node scale 0.5" proposal at the approved 48 px height:
   - visible body 96 ±1 texels;
   - cell **80×112 texels** (40×56 logical), giving room for the ponytail, coat and bag;
   - ground pin at **(40,104)**;
   - Sprite2D scale fixed at 0.5;
   - nearest filtering;
   - `flip_h` mirroring allowed only where the record says the character is symmetric. The female protagonist is not (side ponytail, single knee guard, scarf tail), so her west direction must be authored separately.
2. **Idle master per direction (art).** Downsample the approved concept to 96 texels with area averaging, quantize to a per-character palette of ≤48 colours, then hand-clean the outline, face, insignia and alpha to binary. Starting from the downsample keeps the detail the user saw in the approved screenshot. Do not draw from scratch: the earlier independently drawn 192×224 sample looked more cartoonish. Use **one scale per visual variant**, derived once from the south idle master, never per frame.
3. **Layer split + occlusion fill (art).** Split the idle master into locked layers. Fill in the pixels hidden behind legs, arms and coat hem. Add a **mask layer** with flat key colours for side-owned items (knee guard, scarf tail, ponytail) so ownership can be checked by a script.
4. **Limb parts (art).** Draw these per direction:
   - legs: 4 poses × 2 sides;
   - arms: 3 poses × 2;
   - 2–3 secondary hair/scarf poses.
   For south/north, express depth through foot y, shin length and overlap order (C4), not rotation. Parts from the first character of each body archetype are recoloured or adjusted for the others.
5. **Pose table + compositor (engineering).** A shared JSON per archetype lists, for each walk frame (the pilot proposes **8**: contact, down, passing, up × 2): the part id, its integer offset, its z-order, the torso bob (0–2 texels), the contact foot and the contact point. For the pilot, idle uses 4 frames of breathing/sway with locked layers. A Python/PIL tool (same stack as the existing `tools/` authoring scripts) reads the layer PNG exports plus the pose table and writes:
   - frame PNGs, **one separate file per direction/action/frame**. No atlas, sprite sheet, contact sheet or other combined image is produced (project rule: every generated image is its own file);
   - a manifest with the declared frame count per direction and action; the variant's master, scale, cell size and ground pin, declared once; and, for each frame, contact points (gait data only, never used to rescale or recenter), bbox (reported only), palette and per-layer hashes;
   - a metrics report (§5).
   The output must be bit-identical for the same inputs.
6. **Cleanup (art).** Fix seams at hips and hem only. Every texel changed inside a locked layer region is logged, and the metrics fail if a frame exceeds the budget.
7. **Godot import (engineering).** Generate one `SpriteFrames` `.tres` per character that references the separate frame PNGs, plus the manifest, from the bake. Godot never sees the large concept PNGs.

**Proposed pilot asset counts (one character, not a production decision):** 4 directions × (4 idle + 8 walk) = **48 frames**, each a separate PNG, plus 4 layered source files, about 20–30 part images per direction (each its own file), 1 manifest, 1 `SpriteFrames`, 1 metrics report and 1 capture video. Memory: 48 × 80×112 × 4 B ≈ 1.7 MB per variant uncompressed (lossless import), and only the characters present in a scene are loaded.

**Production frame count is not decided.** The current runtime layout and the intake checklist's existing description use 20 frames per variant (1 idle + 4 walk per direction). The pilot tests whether 48 is worth its cost; the final count is chosen only after the pilot's evidence (M1–M10, actual effort against S2) and explicit user approval. For scale only: 48 frames across 52 variants would be 2,496 frames, 20 frames would be 1,040, and spec v0.2's 2 idle + 6 walk would be 1,664 (6 walk frames give weaker contact poses). Whatever count is chosen, the validator reads it from each manifest's declared frame counts and never hard-codes 20 or 48.

**Effort estimates.** These are assumptions, not measurements: a skilled pixel artist or tech artist, with Claude writing the tooling.

| Item | Estimate |
|---|---|
| Tooling: compositor, metrics, Godot harness, SpriteFrames generator | 3–5 engineering days |
| First archetype walk template (pose table + reference limb parts) | 1.5–2.5 pd (+1–2 pd per later archetype; 4–6 archetypes expected: slim, average, broad/armoured, long coat/skirt, small/child, non-human) |
| Gate character, 4 directions (idle masters 1–2, split + fill 0.5–1, limbs 1–2, bake + cleanup 0.5–1, QA 0.25–0.5) | **3.25–6.5 pd** |
| Later characters reusing an archetype | 2.5–4 pd each |
| All 52 variants | about **130–210 pd** + tooling + archetypes. This is below the segmented-rig doc's 150–300 pd only if archetype reuse works (stop condition S4). |

Cost levers for the user to decide (not decided here): a smaller frame set for characters who never walk in the MVP, and grouping by body archetype.

## 4. Godot implementation advice (for the next engineering batch, not applied)

- **Display:**
  - visual child node with `scale = Vector2(0.5, 0.5)`, `centered = false`, `offset = -pin` (in texels), so the node origin is the ground contact point;
  - `texture_filter = NEAREST`;
  - import settings: mipmaps off, lossless, `fix_alpha_border` on;
  - y-sort by origin;
  - shadow as a separate sprite at the origin that does not bob;
  - no runtime rotation, and no scale other than 0.5 and `flip_h`.
- **Pixel snapping:** keep the gameplay position as a float, but place the visual node at `(global_position * 2.0).round() / 2.0` so 1 texel always lands on 1 screen pixel. `rendering/2d/snap/snap_2d_transforms_to_pixel` may do this, but it has **not been verified** whether it snaps to logical or physical pixels under `canvas_items` in Godot 4.7.2. Test before relying on it.
- **Distance-driven walk.** Use `distance += travelled_this_frame`, then `frame = int(distance / (cycle_len / n)) % n`, where `n` is the walk frame count declared in the manifest (8 in the pilot) and `cycle_len` comes from the manifest's contact points (two steps). **Design decision needed:**
  - Option (a): keep 140 px/s and author a jog/run stride (step ≈ 26–34 px).
  - Option (b): lower walk speed to about 80–100 px/s for a walk stride (step ≈ 18–22 px, ≈ 2–2.5 cycles/s at 40 px per cycle).
  Today's 4 × 0.12 s is effectively (a), but with walk art.
- **Turns and stops:**
  - Facing hysteresis: switch only when the new axis dominates by about 1.2×, or keep the current facing if it is still one of the pressed axes.
  - Keep the distance phase through turns; do not snap to idle.
  - On stop, advance to the nearest contact frame (both feet down) before idle.
  - Idle is time-driven (holds of 0.25–0.4 s).
- **Data:**
  - Replace the two `const` preload tables with per-character `SpriteFrames` loaded on demand (`ResourceLoader.load_threaded_request` per area).
  - The registry builder should iterate the visual registry JSON and validate directions × actions × frame counts against the counts **explicitly declared in each manifest**, not hard-code 19, 20 or 48. A missing declaration is a failure, not a default.
  - Store the cell, pin and scale once per variant, and the contact points per frame. The validator fails any frame whose size differs from the cell or that carries its own pin or scale.
- **Silhouette:** drive `city_hero_silhouette` from the same `SpriteFrames` and frame index, with nearest filtering.
- **Capture harness:**
  - A headless scene walks a character along fixed straight and diagonal paths at gameplay speed, on light and dark ground, and logs per tick: node position, frame index, and the world position of the contact foot.
  - Record review video with Godot Movie Maker (`--write-movie <file>.avi --fixed-fps 60`) at 1280×720. Do not use GIF, because palette quantization was already shown to alter colours.

## 5. One-character gate (female protagonist, 4 directions × idle + walk)

She has the most side-owned identity markers, and all three earlier failures used her, so she is the hardest and most comparable test. Every check below must pass on the baked frames and in the engine capture:

| Metric | Pass threshold |
|---|---|
| M1 Locked-layer identity | 0 changed texels in head/torso/bag/insignia across a direction's frames, apart from the declared integer bob. Logged cleanup ≤ 12 texels per frame. |
| M2 Ownership | The mask-colour centroids of the knee guard, scarf tail and ponytail stay on their declared side in every frame the manifest declares (48/48 for the proposed pilot set). |
| M3 Torso registration | Torso pin x drift = 0. y bob follows the pose table (0–2 texels). |
| M4 Height / scale | Idle 96 ±1 texels in all 4 directions. Walk frames −3 to +1 texels. One constant scale. |
| M5 Foot lock (engine) | Contact-foot world drift ≤ 1 screen px per tick during contact frames, at the chosen speed, on straight and diagonal paths. |
| M6 Alpha hygiene | 0 partial-alpha texels outside declared soft layers. Corners transparent. No opaque texel on the cell border. |
| M7 Palette | All frames use a subset of the idle-master palette (≤ 48 colours). |
| M8 Turn consistency | Shoulder width and head size match across directions within the ratios recorded in the manifest. No idle snap on turn. |
| M9 Runtime | 1 texel = 1 screen px (no fractional positions). No facing flicker at 45°. Silhouette frame matches the hero frame. |
| M10 User review | The user watches the Movie Maker capture beside the approved three-character screenshot and **explicitly approves the motion**. Only the user can pass this. |

**Stop conditions before any bulk production:**

- **S1** Any of M1–M9 still fails after 2 cleanup iterations → stop and revise the method.
- **S2** The gate character takes more than 6.5 pd, or more than 1.5× its estimate → stop and re-estimate before committing to 51 more.
- **S3** M10 is not approved, *or* the user judges the 96-texel idle master a downgrade from the approved screenshot (risk **R1**) → stop. Consider the 3D proxy route (Method C) or a different density.
- **S4** A second, different archetype (Liang Xu: long coat, older build) reuses less than 50% of the pose table or limb-part templates, or costs more than 4 pd → the archetype assumption fails and the 130–210 pd estimate is invalid. Stop.
- **S5** Cleanup needs whole frames regenerated by an image model → this is Method A again. Stop.
- **S6** The art tooling cannot produce pixel-exact layer and part PNGs at 80×112 that the compositor can consume (ChatGPT image output cannot be edited at texel level, and no human pixel editor such as Aseprite is available) → stop. This is the largest feasibility risk, and the gate is designed to expose it early.

**Rollout after a pass and after the user has approved a production frame count (R5):** Liang Xu (S4 check) → male protagonist (reuses the female template) → a wave of 5 → waves of 10, each wave re-running M1–M9 automatically, with a user spot-check of one capture per wave.

## 6. Open risks and decisions

- **R1:** a hand-cleaned 96-texel master may lose the richness of the runtime-downsampled concept the user approved. Only an in-engine side-by-side settles this.
- **R2:** the walk speed decision (§4, option a or b) changes stride art and must be made before limb parts are drawn.
- **R3:** the concept sources' low-alpha fringe (both concept manifests) must be removed in the idle master, not at runtime.
- **R4:** side-view combat remains a separate specification and is not covered here.
- **R5:** the production frame count per variant (20, 48 or another value) is an open user decision. It is made after the pilot, from its evidence, and is recorded in the manifests that the validator reads.
