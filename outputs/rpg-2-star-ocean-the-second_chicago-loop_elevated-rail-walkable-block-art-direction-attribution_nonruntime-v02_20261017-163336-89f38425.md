# Chicago Loop elevated-rail walkable block: art-direction reference, attribution

Status: **nonruntime, unapproved reference.** It is not game art, not native pixel art and not a scene-acceptance candidate.

File: `outputs/rpg-2-star-ocean-the-second_chicago-loop_elevated-rail-walkable-block-art-direction-nonruntime-v02_20261016-195030-8c456a73.png`
- sha256-bytes `73b57deb1532fcd6be419b96ec7b33aea894458f39a7f3d42c8842f778761be4`
- 3,183,221 bytes

## What it is

It is a **generated, continuous-colour** top-down reference image, made on 2026-10-16 at 19:50 ET. It is described in the tracked brief `docs/qa/rpg-2-star-ocean-the-second_chicago-loop_arrival-scene-visual-transfer-brief_unapproved-v01_20261016-184100-0ea38e17.md`, section "Overhead arrangement reference". That brief says it is:
- not a Pixelorama scene;
- not a real Chicago street plan;
- not accepted game art.

The generation prompt was not saved with the image. This note records only what the repo can show; it does not reconstruct the prompt.

## Why it is synced

The Chicago Loop State/Lake v02 candidate (`55667f46`, UNAPPROVED) uses this image as its underpainting source. The author tool `tools/rpg-2-star-ocean-the-second_chicago-loop_state-lake-block-pixel-author_unapproved-v02_20261017-160959-55667f46.py`:
1. box-downscales the image to 640×360;
2. recomposes its rows;
3. repairs generator defects;
4. quantizes it to a 128-colour palette.

It then adds three hand-pixelled props: the bench, the State/Lake station plate and the flag banner.

The tool pins the image's sha256, so the candidate can only be rebuilt from this exact file. Most of the v02 runtime pixels are therefore quantized generated colour, not hand-placed pixel clusters. See defect 1 in `docs/qa/rpg-2-star-ocean-the-second_chicago-loop_state-lake-arrival-block-native-scene_qa-note_unapproved-v02_20261017-160959-6bcff07f.md`.
