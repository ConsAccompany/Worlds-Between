# Exploration character art pipeline · decision memo · M8 v01

**Status: recommendation only. Nothing here is approved by the user.** No art, code, assets, manifests, Game Bible or progress files were created or changed. The only measurements were made in memory on existing PNGs; no files were written. The user has approved one thing: a **48 logical px** display height. Art quality, direction fidelity, animation and batch production are all still unapproved, and **0/52** exploration sprites are accepted.

> **Update, 2026-10-14 (added after the memo was written; the original text below is unchanged).** The §2 toolchain inventory is a snapshot taken before the memo's file-name timestamp, 16:55 UTC on 2026-10-14. Since then two things it reports have changed:
>
> - **Pixelorama v1.2.3 has been used.** The user ran its **web build** in a browser for a south-idle pilot of the female protagonist. Two `.pxo` projects (both `pixelorama_version: v1.2.3-stable`) and two PNG exports, dated 21:03 and 21:06 UTC, are in `game/assets/characters/pixelorama-pilots/`, with a [pilot manifest](../../game/assets/characters/pixelorama-pilots/rpg-2-star-ocean-the-second_protagonist-female_south-idle-pixelorama-pilot-manifest_m8-v01_20261014-211454-868681b7.json).
> - **A portable Windows build is staged** at `work/tooling/pixelorama-1-2-3/Pixelorama-Windows-64bit/Pixelorama.exe` (official GitHub release zip, SHA-256 verified, executable not signed, `work/` git-ignored). Nothing shows it was used for the pilot.
>
> So "Not installed: … Pixelorama" in §2, and "no pixel editor installed" in the Method A column of §3, no longer hold for Pixelorama. The other tools on that list were not re-checked. Two variant-tagged 48 px city captures exist (downscale and four-texel paint pass); details are in the [Pixelorama setup note](rpg-2-star-ocean-the-second_protagonist-female_pixelorama-south-pilot-setup_m8-v01_20261014-170109-dd62c262.md). The pilot is a single idle frame, has no walk frames, fails the §4 cell, height, alpha and palette targets, and is **not approved**. Acceptance is unchanged: **0/52** exploration sprites and **0/11** scene-quality gates.

Inputs: [production standard draft](rpg-2-star-ocean-the-second_scifi-city_premium-exploration-production-standard_m8-draft_20261014-153400-481ae2c9.md), [walk-pipeline feasibility review](rpg-2-star-ocean-the-second_exploration-walk-pipeline_feasibility-review_m8-v01_20261014-163221-c4e19a7d.md) (C1–C7, M1–M10 and S1–S6 below are its IDs), [leg-layer extraction manifest](../../outputs/rpg-2-star-ocean-the-second_protagonist-female_leg-layer-extraction-feasibility-manifest_m8-v01_20261014-164552-8e0ac267.json), and the [segmented-rig review](rpg-2-star-ocean-the-second_protagonist-female_segmented-rig-walk-review_m8-concept_20261014-162000-417b2e95.md).

## 1. Evidence this decision rests on

| Fact | Source |
|---|---|
| Image-model edits cannot output pixels from a source image at their original coordinates. Two attempts to extract one leg with its knee guard kept only **189/64,989** and **13/254,523** opaque pixels unchanged at the same canvas coordinates. Both were rejected. | Extraction manifest |
| Generating each frame separately swaps accessories between sides: the knee guard changed legs, and the torso jumped 4.3 logical px sideways. | Feasibility review C1, C2 |
| Cutting the parts out of the **same source image** kept the face, scarf, knee guard and bag identical in every frame. It failed for other reasons: feet slid, the arms did not move, the hem/thigh joint showed hard seams, and nearest-neighbour rotation of a 1300 px source at runtime caused pixel noise. | Segmented-rig review; feasibility C3, C4 |
| A separately drawn 192×224 native pixel sample looked cartoonish, and detail collapsed in the city scene. | Production standard |
| The approved south concept is a flat 1145×1374 RGBA PNG. The body's strong-alpha bounding box is 591×1281 px, and **493,841** pixels have partial alpha. | Measured in memory for this memo |
| A box-filter downsample of that concept to a 96-texel body (scale 0.07494) gives **2,570 opaque texels, 2,277 unique colours and 2,882 partial-alpha texels**. East: 1,961 opaque / 1,784 colours. North: 2,275 opaque / 1,951 colours. | Measured in memory for this memo |

What follows from this:
- Identity across frames can only be guaranteed when every identity texel is **copied** from one master image, never redrawn.
- No AI model may produce production pixels. AI output stays limited to pose references.
- The open question is no longer identity. It is whether the limbs can be posed without redrawing them, and how much hand work that takes.

## 2. Local toolchain inventory (read-only)

*Snapshot as of 2026-10-14, before 16:55 UTC. Pixelorama has since been used (web build) and a portable Windows build staged; see the update at the top.*

I scanned Program Files (x86 and x64), the user's AppData folders, the WinGet links, Store (Appx) packages, the uninstall registry, the Steam `common` folder and this project. I did not search personal folders or the D: drive.

| Available | Use for this pipeline |
|---|---|
| Godot **4.7.2**, project-local at `work/tooling/godot-4-7-2/` (GL Compatibility) | Test scenes, 1280×720 captures, Movie Maker video. Can render 3D, but it has no modelling or rigging tools. |
| Python **3.12.14** from the Codex runtime (`~/.cache/codex-runtimes/.../python.exe`, not on PATH), with **Pillow 12.3.0** and **NumPy 2.3.5** only. Missing: scipy, OpenCV, scikit-image, psd-tools. | Deterministic downsampling, quantization, masking, compositing and metrics. |
| ffmpeg **8.1.1** (WinGet) | Lossless conversion of captures. No GIF output (GIF alters colours). |
| Node.js | Existing Game Bible and widget tools only. |
| Microsoft Paint 11.2605 and the classic MSPaint (Store apps) | The only raster editors installed. They have no indexed palette and no onion skin, and I did not verify whether they can save layered files. Usable only for a few single-texel fixes. |
| Unreal Engine **5.0 Early Access**. Its templates include `Mannequin/Animations/ThirdPersonWalk`, `ThirdPersonRun` and `ThirdPersonIdle`. | Possible **motion reference** only (a generic mannequin, not this character). Not launched. It is an Early Access build from 2021, so it may not run on this machine. |
| Wandering Sword (逸剑风云决), installed through Steam. Its folder layout (`Engine/`, `Wandering_Sword/Content`, `JH.exe`) is a packaged Unreal game. | Visual benchmark for the user to judge only. Its asset files were not opened, and local evidence does not show how its sprites were made. |

**Not installed:** Aseprite, LibreSprite, Pixelorama, Krita, GIMP, Photoshop (only Acrobat DC and Flash Player are present), Affinity, Clip Studio, Blender, Inkscape, ImageMagick, Spine, Live2D, VRoid and MagicaVoxel. The `convert` command on PATH is the Windows disk-conversion utility, not ImageMagick.

**Layered sources in the project: none.** All 1,144 PNGs are flat. The only vector files are three old flat SVG placeholder sprites from M1/M7, copied into three `work/` worktrees. There are no .psd, .kra, .ase, .xcf, .ora, .blend, .fbx, .glb or .vrm files.

**Excluded routes.** Image-to-3D, layer separation and image editing through connected services (for example Higgsfield `generate_3d`, Canva `separate-image-layers`, ElevenLabs image edit) spend credits or need paid plans. They are out of scope under the subscription-only rule, and none were tested.

## 3. Methods compared

| | A. Hand-painted layered pixel art | B. 3D proxy → pixel render | **C. Hybrid: source-locked layer bake (recommended experiment)** |
|---|---|---|---|
| How | An artist paints the idle master, layers, occlusion fills and every limb pose in a pixel editor. A compositor assembles the frames. | Model and rig each character, render an orthographic 3/4 view at final resolution, then paint over. | Downsample the approved concept once to a 96-texel master. Code cuts layers out of that master using a key-colour mask, so the layer pixels are copied, not redrawn. Limb poses come only from **integer transforms of copied pixels**: whole-part offsets, per-row offsets and dropping or duplicating rows for foreshortening. No rotation, no resampling and no AI pixels. Only seams and occluded areas are touched by hand, and every hand-edited texel is logged. |
| Identity across walk frames | Guaranteed in the locked layers. Hand-drawn limbs are only as consistent as the artist. | Shapes are consistent, but painting over each frame brings back drift. The painted look is a new interpretation, not the approved concept. | **Guaranteed by construction.** Every identity texel is a copy from the master, and the knee guard sits inside its leg's layer, so it cannot change sides. |
| Fit with the approved look | Risk of looking cartoonish if drawn from scratch (as the 192×224 sample was). | Uncertain for 51 stylized designs. | Starts from the image the user approved. Risk **R1**: detail may be lost at 96 texels. |
| Foot contact / gait | Fully controllable. | Excellent. | **Unproven.** Integer leg deformation may not travel far enough for a walk stride (see §4 E8). This is the main question the experiment answers. |
| Tools today | **Blocked**: no pixel editor installed (feasibility S6). Installing a free one (Pixelorama, LibreSprite, Krita) or buying Aseprite is the user's decision. | **Blocked**: no modelling or rigging tool, and AI 3D generation is a paid route. UE 5.0 EA can supply only a generic mannequin walk. | **Runs today**: Python with Pillow and NumPy, Godot 4.7.2 and ffmpeg. Paint only for single-texel fixes. |
| Solo-dev cost (estimate) | Gate character 3.25–6.5 person-days (pd); about 130–210 pd for all 52 variants if body archetypes can be reused (feasibility §3). Assumes pixel-art skill. | 3–6 pd per character, mostly modelling, plus pipeline setup. Assumes 3D skill. | Unknown, which is what the experiment measures. Mostly tooling time from Claude; the user's hand time is limited to logged fixes. |
| Role | Fallback when C's limbs need redrawing (E6 fails). | Optional **motion reference only** (UE mannequin foot timing) if E8 fails. Not an identity pipeline. | Run first. |

**No method makes 52 variants × 4 directions cheap.** The choice of method only changes who spends the time and whether identity drifts. Ways to cut the total, such as fewer walking NPCs, fewer directions or shared archetypes, remain the user's decision (feasibility R5).

## 4. Recommended smallest experiment: female protagonist, south, 1 idle + 8 walk frames

**Why this one:** the standard requires south idle and stepping first. She has the most side-specific identity markers: knee guard, scarf tail and ponytail. Her south view is where the knee-guard swap and the extraction failures happened, and two baselines already exist for comparison (v02 four-phase and segmented rig). The experiment is **south only**. East, north, west and other characters wait for the stop or continue decision below.

**Prerequisite (user decision R2):** the walk speed. Option (b), 80–100 px/s with a walk stride, matches walk art. Option (a), 140 px/s, needs a jog stride. The experiment bakes one stride and records which one was used. It does not set the game's speed.

### Source inputs (read-only)

1. Approved-detail concept: `game/assets/characters/high-fidelity-prototypes/rpg-2-star-ocean-the-second_protagonist-female_south-exploration-premium-pixel_m8-concept_20261014-145800-62c3a10f.png`.
2. Pilot parameters from the feasibility review. These are for the pilot only and are not an approved standard:
   - visible body 96 ±1 texels;
   - cell 80×112;
   - ground pin (40,104);
   - Sprite2D scale 0.5;
   - nearest filtering;
   - one scale for the whole variant, never set per frame.
3. Pose table: JSON numbers for 8 walk phases (contact, down, passing, up, then the same for the other leg). Each phase gives every part's integer offset, row-drop list, z-order and torso bob of 0–2 texels. It contains numbers only and no images.
4. Baselines for the review: the v02 four-phase concepts, the segmented-rig captures and the approved 48 px three-character screenshot. The user may optionally add their own Wandering Sword screenshot as a visual benchmark.

### Outputs

Every image is a **separate file**. No atlas, sprite sheet, contact sheet, grid or side-by-side composite is produced. All files go under `outputs/` with project-standard names, and nothing goes into `game/assets` or the playable runtime.

| Output | Type | Count |
|---|---|---|
| Idle master (quantized, binary alpha) | PNG RGBA 80×112 | 1 |
| Layer parts:<br>• hair + ponytail<br>• face/head<br>• torso + coat<br>• bag<br>• scarf tail<br>• left leg with knee guard<br>• right leg<br>• left arm<br>• right arm<br>• occlusion fill | PNG RGBA 80×112, one per part | 10 |
| Ownership mask with flat key colours for the knee guard, scarf tail and ponytail | PNG RGBA 80×112 | 1 |
| Walk frames | PNG RGBA 80×112, one per frame | 8 |
| Pose table; bake manifest (cell, pin and scale declared once; per-frame contact point, hashes and hand-edit log) | JSON | 2 |
| Metrics report | JSON + short MD review | 2 |
| Godot test-scene stills at 1280×720 (9 frames × light and dark ground) | PNG, one per capture | 18 |
| Walk capture from Godot Movie Maker at 1280×720 and 60 fps | AVI (MJPEG); optional ffmpeg FFV1 MKV copy. **No GIF.** | 1–2 |

### Acceptance metrics

E1–E7 are checked automatically on the baked PNGs. E8–E9 are checked in the Godot test scene. E10 is the user's call alone.

| # | Metric | Pass |
|---|---|---|
| E1 | Source lock | 100% of opaque texels in the locked layers equal the idle master after the declared integer offset (M1). The idle master equals the deterministic quantized downsample, except for logged edits. |
| E2 | Ownership | Knee guard on the viewer-left leg, and scarf tail and ponytail on their declared sides, in **9/9** frames (M2). |
| E3 | Registration | Torso pin x drift = 0. y bob follows the pose table. All frames 80×112, with one scale (M3). |
| E4 | Height | Idle 96 ±1 texels. Walk frames −3 to +1 (M4). |
| E5 | Alpha and palette | 0 partial-alpha texels. No opaque texel on the cell border. ≤48 colours. Every walk frame's colours are a subset of the idle palette (M6, M7). The 2,882 partial-alpha texels measured above must all be resolved. |
| E6 | Hand work | ≤12 logged hand-edited texels per walk frame (M1 budget). The number of synthesized occlusion-fill texels is reported. **This number decides between C and A.** |
| E7 | Determinism | Re-running the bake produces byte-identical PNGs (matching SHA-256). |
| E8 | Foot contact | Contact-foot world drift ≤1 screen px per tick during contact frames, at the recorded speed (M5). Risk: at a walk step of 18–22 logical px, a planted foot has to move up the cell by roughly half a step per contact phase, which may be more than integer leg foreshortening can deliver. The measured value is reported whether it passes or fails. |
| E9 | Display | 1 texel = 1 screen px, no fractional placement, and distance-driven frame stepping, in the test scene only (M9). |
| E10 | User review | The user compares the capture with the approved 48 px screenshot and both baselines. They say explicitly (i) whether the idle master keeps the approved detail (R1) and (ii) whether the motion is acceptable. Until they do, nothing counts as approved. |
| E11 | Effort | ≤1.5 pd of total wall-clock time. This is the upper end of the segmented-rig review's estimate of 0.5–1.5 pd for south split, fill, contact and loop. |

### Stop conditions

Stop and report on the first of these that occurs. Do not expand the scope.

1. Any of E1–E7 still fails after **2** bake or cleanup iterations. Feasibility S1 applies.
2. E6 is over budget: the limbs need redrawing rather than transforming. Stop C. The evidence then supports Method A, which first needs the user to decide whether to install or buy a pixel editor (S6).
3. A frame needs any image-model output (S5).
4. E11 is exceeded, or the work takes more than 1.5× the estimate (S2).
5. The user rejects the 96-texel idle master as a downgrade (R1). The density is then wrong, whatever the method. Stop before any further limb work.
6. E8 fails, but E1–E7 and E10(i) pass. Stop and offer two choices: a stride or speed change (R2), or a UE mannequin motion-reference test. Do not start either one without user approval.
7. The Claude subscription limit is reached. Stop and record where the work got to. Do not switch to API keys, credits or paid routes.

**If the experiment passes**, the next step still needs explicit user approval. The proposed next step is the east direction, the hardest for leg overlap and foot contact, then a second archetype (Liang Xu, feasibility S4). No other character, direction or batch work starts until then.
